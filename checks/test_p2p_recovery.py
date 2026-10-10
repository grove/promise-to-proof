#!/usr/bin/env python3
"""Recovery lifecycle regressions using fixture transport, never live model calls."""
from contextlib import contextmanager
import json
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

import test_p2p_delivery as fixtures

d = fixtures.d


class RecoveryReceiptTests(unittest.TestCase):
    setUp = fixtures.DeliveryTests.setUp
    tearDown = fixtures.DeliveryTests.tearDown
    cli = fixtures.DeliveryTests.cli
    cli_item = fixtures.DeliveryTests.cli_item
    state = fixtures.DeliveryTests.state
    runtime = fixtures.DeliveryTests.runtime

    @contextmanager
    def responses(self, change):
        original = self.fake

        def launch(*args):
            result = original(*args)
            path = args[2]
            events = [json.loads(line) for line in path.read_text().splitlines()]
            message = next(event['item'] for event in events
                           if event.get('item', {}).get('type') == 'agent_message')
            message['text'] = change(original.calls[-1], message['text'])
            path.write_text(''.join(json.dumps(event) + '\n' for event in events))
            return result

        with patch.object(d, 'launch', launch):
            yield

    def test_malformed_diagnosis_is_saved_and_corrected_once_in_same_delivery(self):
        self.fake.mode = 'partial-implementation'
        with self.responses(lambda stage, message: 'not valid JSON' if stage == 'diagnosis' and
                            self.fake.calls.count('diagnosis') == 1 else message):
            code, value = self.cli()
        self.assertEqual(code, 0, value)
        attempts = [attempt for attempt in self.state()['attempts'] if attempt['stage'] == 'diagnosis']
        self.assertEqual(len(attempts), 2)
        self.assertEqual(attempts[0]['status'], 'complete')
        self.assertEqual(attempts[0]['report_validation'], 'rejected')
        self.assertEqual((self.runtime() / attempts[0]['report']).read_text(), 'not valid JSON')
        self.assertEqual(attempts[1]['report_validation'], 'accepted')
        self.assertEqual(self.fake.calls.count('implementation'), 1)
        self.assertEqual(self.fake.calls.count('repair'), 1)
        self.assertEqual(self.fake.calls.count('review'), 1)
        self.assertEqual(self.fake.calls.count('proof'), 1)
        self.assertEqual(self.state()['recovery_history'][0]['diagnosis_attempt_id'], attempts[1]['id'])

    def test_two_malformed_diagnoses_block_without_more_attempts_on_resume(self):
        self.fake.mode = 'partial-implementation'
        with self.responses(lambda stage, message: '{}' if stage == 'diagnosis' else message):
            code, value = self.cli()
            self.assertEqual(code, 1, value)
            self.assertIn('after one format correction', value['blocker'])
            calls = list(self.fake.calls)
            self.assertEqual(calls.count('diagnosis'), 2)
            for action in ('status', 'resume', 'resume'):
                _, value = self.cli(action)
                self.assertNotIn('uncertain dispatch', value['blocker'])
                self.assertEqual(self.fake.calls, calls)
        self.assertTrue(all(attempt['status'] == 'complete' for attempt in self.state()['attempts']))
        self.assertNotIn('repair', self.fake.calls)

    def test_stale_diagnosis_is_terminal_without_format_retry(self):
        self.fake.mode = 'partial-implementation'

        def stale(stage, message):
            if stage == 'diagnosis':
                report = json.loads(message)
                report['input_identity_json'] = '{}'
                return json.dumps(report)
            return message

        with self.responses(stale):
            code, value = self.cli()
            self.assertEqual(code, 1, value)
            self.assertIn('stale recovery diagnosis', value['blocker'])
            calls = list(self.fake.calls)
            code, value = self.cli('resume')
        self.assertEqual(code, 1, value)
        self.assertEqual(self.fake.calls, calls)
        self.assertEqual(calls.count('diagnosis'), 1)
        self.assertNotIn('repair', calls)

    def test_saved_diagnosis_is_adopted_after_interruption_without_redispatch(self):
        self.fake.mode = 'partial-implementation'
        original = d.Delivery.save
        interrupted = False

        def save(delivery):
            nonlocal interrupted
            original(delivery)
            if not interrupted and delivery.state.get('recovery_decision', {}).get('status') == 'diagnosed':
                interrupted = True
                raise OSError('fixture interruption after completed diagnosis')

        with patch.object(d.Delivery, 'save', save):
            code, value = self.cli()
        self.assertEqual(code, 1, value)
        self.assertEqual(self.fake.calls.count('diagnosis'), 1)
        self.assertNotIn('repair', self.fake.calls)
        code, value = self.cli('resume')
        self.assertEqual(code, 0, value)
        self.assertEqual(self.fake.calls.count('diagnosis'), 1)
        self.assertEqual(self.fake.calls.count('implementation'), 1)
        self.assertEqual(self.fake.calls.count('repair'), 1)
        self.assertEqual(self.state()['recovery_decision']['status'], 'consumed')

    def test_legacy_completed_bad_diagnosis_resumes_original_delivery(self):
        self.fake.mode = 'partial-implementation'
        reserve = d.Delivery.reserve
        validate = d.Delivery.report_validation

        def legacy_reserve(delivery, stage, inputs, scratch):
            if stage == 'diagnosis':
                inputs.pop('recovery_context_sha256', None)
            return reserve(delivery, stage, inputs, scratch)

        @contextmanager
        def stop_before_parse(delivery, attempt, host):
            if attempt['stage'] == 'diagnosis':
                raise OSError('fixture stop after legacy host exit zero')
            with validate(delivery, attempt, host):
                yield

        with patch.object(d.Delivery, 'reserve', legacy_reserve), \
                patch.object(d.Delivery, 'report_validation', stop_before_parse), \
                self.responses(lambda stage, message: 'invalid legacy response' if stage == 'diagnosis' else message):
            code, value = self.cli()
        self.assertEqual(code, 1, value)
        state = self.state()
        original_id = state['invocation_id']
        self.assertEqual(state['attempts'][-1]['status'], 'reserved')
        state.pop('recovery_decision')
        state.pop('task_readiness')
        preflight = next(attempt for attempt in state['attempts'] if attempt['stage'] == 'preflight-2')
        preflight['inputs'].pop('task_readiness')
        preflight['inputs'].pop('candidate')
        preflight.pop('report')
        preflight.pop('report_sha256')
        preflight.pop('report_validation')
        folder = self.runtime() / 'attempts' / preflight['id']
        events = [json.loads(line) for line in (folder / 'events.jsonl').read_text().splitlines()]
        events = [event for event in events if event.get('item', {}).get('command') != 'FIXTURE python3 --version']
        next(event['item'] for event in events if event.get('item', {}).get('type') == 'agent_message')['text'] = \
            'FIXTURE host preflight, not live evidence'
        (folder / 'events.jsonl').write_text(''.join(json.dumps(event) + '\n' for event in events))
        for name in ('exit.json', 'launch.json'):
            receipt = json.loads((folder / name).read_bytes())
            receipt['inputs'] = preflight['inputs']
            if name == 'exit.json':
                receipt['event_sha256'] = d.fs.digest((folder / 'events.jsonl').read_bytes())
            (folder / name).write_bytes(d.encoded(receipt))
        state_path = d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'delivery.json'
        state_path.write_bytes(d.encoded(state))
        code, value = self.cli('resume')
        self.assertEqual(code, 0, value)
        self.assertEqual(value['invocation_id'], original_id)
        self.assertEqual(self.fake.calls.count('diagnosis'), 2)
        self.assertEqual(self.fake.calls.count('preflight'), 3)
        self.assertEqual(self.fake.calls[-5:], ['diagnosis', 'preflight', 'repair', 'review', 'proof'])
        self.assertEqual(self.fake.calls.count('implementation'), 1)
        self.assertEqual(self.fake.calls.count('repair'), 1)

    def test_blocked_diagnosis_is_renewed_after_new_readiness_observation(self):
        self.fake.mode = 'blocked'
        code, value = self.cli()
        self.assertEqual(code, 1, value)
        self.assertIn('recovery needs', value['blocker'])
        invocation = value['invocation_id']
        old_context = self.state()['recovery_decision']['context_sha256']

        def available(stage, message):
            if stage not in ('diagnosis', 'review'):
                return message
            report = json.loads(message)
            if stage == 'diagnosis':
                report.update(status='ACTIONABLE', action='implementation',
                              approach='Use the now available local CLI input.', strategy_changed=True,
                              reason='The resumed capability probe confirms the prerequisite.',
                              missing_input='', expected_result='',
                              capability_check='P2P_RECOVERY_CAPABILITY=fixture local CLI available')
            elif self.fake.calls.count('repair'):
                report.update(status='REVIEWED', findings=[], gaps=[], missing_input='', expected_result='')
            return json.dumps(report)

        with self.responses(available):
            code, value = self.cli('resume')
        self.assertEqual(code, 0, value)
        self.assertEqual(value['invocation_id'], invocation)
        self.assertEqual(self.fake.calls.count('diagnosis'), 2)
        self.assertEqual(self.fake.calls.count('preflight'), 3)
        self.assertEqual(self.fake.calls.count('implementation'), 1)
        self.assertNotEqual(self.state()['recovery_decision']['context_sha256'], old_context)

    def test_missing_diagnosis_exit_receipt_remains_uncertain_without_retry(self):
        self.fake.mode = 'partial-implementation'
        original = self.fake

        def interrupted(*args):
            result = original(*args)
            if original.calls[-1] == 'diagnosis':
                raise OSError('fixture lost host completion')
            return result

        with patch.object(d, 'launch', interrupted):
            self.assertEqual(self.cli()[0], 1)
            calls = list(self.fake.calls)
            code, value = self.cli('resume')
        self.assertEqual(code, 1, value)
        self.assertIn('missing controller host completion', value['blocker'])
        self.assertEqual(self.fake.calls, calls)
        self.assertEqual(self.state()['attempts'][-1]['status'], 'reserved')

    def test_invalid_review_is_terminal_and_resume_keeps_specific_error(self):
        with self.responses(lambda stage, message: '{}' if stage == 'review' else message):
            code, value = self.cli()
            self.assertEqual(code, 1, value)
            calls = list(self.fake.calls)
            for action in ('status', 'resume'):
                _, value = self.cli(action)
                self.assertNotIn('uncertain dispatch', value['blocker'])
                self.assertIn('unsupported or missing fields', value['blocker'])
        self.assertEqual(self.fake.calls, calls)
        self.assertNotIn('proof', calls)
        self.assertNotIn('review', self.state()['reports'])
        self.assertEqual(self.state()['attempts'][-1]['report_validation'], 'rejected')

    def test_invalid_implementation_preserves_bytes_without_accepting_or_repeating(self):
        with self.responses(lambda stage, message: '{}' if stage == 'implementation' else message):
            code, value = self.cli()
            self.assertEqual(code, 1, value)
            calls = list(self.fake.calls)
            candidate = value['candidate']
            for action in ('status', 'resume'):
                _, value = self.cli(action)
                self.assertIn('unsupported or missing fields', value['blocker'])
                self.assertNotIn('uncertain dispatch', value['blocker'])
                self.assertEqual(value['candidate'], candidate)
        self.assertEqual(self.fake.calls, calls)
        self.assertEqual((Path(value['candidate_workspace']) / 'greet.py').read_text(), "print('hello')\n")
        self.assertFalse((self.root / 'greet.py').exists())
        self.assertFalse(self.state().get('implementation_complete'))
        self.assertNotIn('implementation', self.state()['reports'])
        self.assertNotIn('review', calls)
        self.assertNotIn('proof', calls)

    def test_invalid_planning_response_is_retained_and_not_repeated(self):
        self.fake.mode = 'review-plan-handoff'
        with self.responses(lambda stage, message: '{}' if stage == 'planning' else message):
            code, value = self.cli()
            self.assertEqual(code, 1, value)
            self.assertIn('invalid or stale planning', value['blocker'])
            calls = list(self.fake.calls)
            code, value = self.cli('resume')
        self.assertEqual(code, 1, value)
        self.assertEqual(self.fake.calls, calls)
        self.assertEqual(self.state()['contract']['revision'], 'v1')
        self.assertNotIn('planning-audit', calls)
        self.assertEqual(self.state()['attempts'][-1]['report_validation'], 'rejected')

    def test_paraphrased_gap_with_changed_candidate_requires_new_strategy(self):
        self.fake.mode = 'multi-repair'

        def repeated(stage, message):
            if stage not in ('proof', 'diagnosis'):
                return message
            report = json.loads(message)
            if stage == 'proof':
                report['gaps'] = ['The output is not established.' if self.fake.calls.count('proof') == 1 else
                                  'Expected stdout remains unsupported by an observation.']
            else:
                report['strategy_changed'] = False
                report['reason'] = 'Same unresolved R1 and same failed mechanism despite different gap wording.'
            return json.dumps(report)

        with self.responses(repeated):
            code, value = self.cli()
        self.assertEqual(code, 1, value)
        self.assertIn('no new executable strategy', value['blocker'])
        self.assertEqual(self.fake.calls.count('repair'), 1)
        self.assertEqual(self.fake.calls.count('diagnosis'), 1)
        history = self.state()['recovery_history']
        self.assertNotEqual(history[0]['candidate_before'], history[0]['candidate_after'])

    def test_partial_repair_with_fewer_named_requirements_continues_without_diagnosis(self):
        self.fake.mode = 'partial-repair'
        contract = self.root / '.p2p/work/tiny/contract.md'
        extra = '| R2 | spec.txt | Exit zero. | Nonzero status fails. | CLI | zero | Observe exit status. | planned |\n'
        contract.write_text(contract.read_text().replace('\n## Unresolved gaps', extra + '\n## Unresolved gaps'))

        def progress(stage, message):
            if stage in ('preflight', 'diagnosis', 'planning', 'planning-audit'):
                return message
            report = json.loads(message)
            report['requirements'].append(dict(report['requirements'][0], id='R2'))
            if stage == 'implementation':
                report['gaps'] = ['R1: output not ready.', 'R2: exit status not ready.']
            elif stage == 'repair' and self.fake.calls.count('repair') == 1:
                report['gaps'] = ['R2: exit status not ready.']
            return json.dumps(report)

        with self.responses(progress):
            code, value = self.cli()
        self.assertEqual(code, 0, value)
        self.assertEqual(self.fake.calls.count('diagnosis'), 1)
        self.assertEqual(self.fake.calls.count('repair'), 2)
        self.assertEqual(self.fake.calls.count('review'), 1)
        self.assertEqual(self.fake.calls.count('proof'), 1)


class RecoveryProgressTests(unittest.TestCase):
    def test_candidate_cycle_forces_diagnosis_even_when_findings_change_phase(self):
        delivery = object.__new__(d.Delivery)
        delivery.state = {'limits': {'repairs': None}, 'attempts': [], 'requirements': ['R1'],
                          'candidate': {'kind': 'snapshot', 'key': 'candidate-a'}, 'recovery_history': []}
        for before, after, findings in [('candidate-a', 'candidate-b', {'review_gaps': ['first issue']}),
                                         ('candidate-b', 'candidate-a', {'proof_gaps': ['different issue']})]:
            delivery.state['recovery_history'].append({
                'status': 'complete', 'candidate_before': before, 'candidate_after': after,
                'findings': findings, 'fingerprint': d.fs.digest(d.fs.canonical(findings)),
                'action': 'implementation', 'approach': 'Prior repair.'})
        delivery.diagnose = Mock(return_value={'strategy_changed': False, 'reason': 'Candidate A recurred.'})
        delivery.stage = Mock()
        with self.assertRaisesRegex(ValueError, 'no new executable strategy'):
            delivery.recover({'implementation': ['A newly worded remaining gap.']})
        delivery.diagnose.assert_called_once()
        delivery.stage.assert_not_called()

    def test_same_method_and_capability_cannot_claim_new_strategy(self):
        delivery = object.__new__(d.Delivery)
        findings = {'implementation': ['R1 is incomplete.']}
        delivery.state = {'limits': {'repairs': None}, 'attempts': [], 'requirements': ['R1'],
                          'candidate': {'kind': 'snapshot', 'key': 'candidate-b'},
                          'recovery_history': [{
                              'status': 'complete', 'candidate_before': 'candidate-a', 'candidate_after': 'candidate-b',
                              'findings': findings, 'fingerprint': d.fs.digest(d.fs.canonical(findings)),
                              'action': 'implementation', 'approach': 'Inspect local seam.',
                              'capability_check': 'P2P_RECOVERY_CAPABILITY=local seam available'}]}
        delivery.diagnose = Mock(return_value={
            'strategy_changed': True, 'action': 'implementation', 'approach': 'INSPECT  local seam!',
            'capability_check': 'P2P_RECOVERY_CAPABILITY=local seam available'})
        delivery.stage = Mock()
        with self.assertRaisesRegex(ValueError, 'repeated an exhausted strategy'):
            delivery.recover(findings)
        delivery.stage.assert_not_called()


if __name__ == '__main__':
    unittest.main()
