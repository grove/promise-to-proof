"""Task readiness through the real controller with fixture transport, not live host proof."""
import json
import unittest
from unittest.mock import patch

import test_p2p_delivery as fixture

d = fixture.d


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture.DeliveryTests('test_clean_project_delivery_uses_local_contract_and_records')
        self.fixture.setUp()
        self.work = '.p2p/work/tiny/contract.md'

    def tearDown(self):
        self.fixture.tearDown()

    def transport(self, edit):
        original = self.fixture.fake

        def wrapped(*args, **kwargs):
            result = original(*args, **kwargs)
            event_path = args[2]
            launch = json.loads((event_path.parent / 'launch.json').read_bytes())
            if 'task_readiness' in launch['inputs']:
                events = [json.loads(line) for line in event_path.read_text().splitlines()]
                message = next(event['item'] for event in events
                               if event.get('item', {}).get('type') == 'agent_message')
                report = json.loads(message['text'])
                edit(report, events)
                message['text'] = json.dumps(report)
                event_path.write_text(''.join(json.dumps(event) + '\n' for event in events))
            return result

        return wrapped

    @staticmethod
    def missing(kind, name, command, observation):
        def edit(report, events):
            report['checks'].append({'kind': kind, 'prerequisite': name, 'requirement_id': 'R1',
                                     'command': command, 'observation': observation, 'available': False})
            report.update(status='BLOCKED', missing_input=name,
                          expected_result='The existing prerequisite is accessible inside the delivery worker.',
                          reason='The agreed verification path needs this existing input before implementation.')
            events.append({'type': 'item.completed', 'item': {'type': 'command_execution',
                           'command': command, 'aggregated_output': observation, 'exit_code': 1}})
        return edit

    def test_admission_binds_actual_receipts_and_reuses_on_unchanged_resume(self):
        code, value = self.fixture.cli('run', '--max-dispatches', '2')
        self.assertEqual(code, 1, value)
        state = self.fixture.state()
        decision = state['admission_decision']
        self.assertEqual(decision['status'], 'ADMITTED')
        self.assertEqual(set(row['name'] for row in decision['conditions']),
                         {'agreement', 'routing', 'workspace', 'recovery', 'verifier', 'prerequisites'})
        self.assertTrue((self.fixture.runtime() / 'decision.json').is_file())
        before = self.fixture.fake.calls.count('preflight')
        self.assertEqual(self.fixture.cli('extend', '--authorize-extension',
                                           '--max-dispatches', '6')[0], 0)
        self.assertEqual(self.fixture.cli('resume')[0], 0)
        self.assertEqual(self.fixture.fake.calls.count('preflight'), before)
        self.assertTrue(all(row['applicability'] == 'REUSED'
                            for row in self.fixture.state()['admission_decision']['conditions']))

    def test_changed_host_executable_blocks_before_implementation_or_reuse(self):
        code, value = self.fixture.cli('run', '--max-dispatches', '2')
        self.assertEqual(code, 1, value)
        executable = fixture.Path(self.fixture.state()['host']['executable'])
        original = executable.read_bytes()
        try:
            executable.write_bytes(b'#!/bin/sh\\necho modified\\n')
            code, value = self.fixture.cli('resume')
            self.assertEqual(code, 1, value)
            self.assertIn('capability configuration changed', value['blocker'])
            self.assertNotIn('implementation', self.fixture.fake.calls)
        finally:
            executable.write_bytes(original)

    def test_ready_uses_existing_second_context_and_does_not_require_unimplemented_product(self):
        self.assertFalse((self.fixture.root / 'greet.py').exists())
        code, result = self.fixture.cli()
        self.assertEqual(code, 0, result)
        self.assertEqual(self.fixture.fake.calls, ['preflight', 'preflight', 'implementation', 'review', 'proof'])
        state = self.fixture.state()
        readiness = state['task_readiness']
        self.assertEqual(readiness['status'], 'READY')
        attempt = next(a for a in state['attempts'] if a['id'] == readiness['attempt_id'])
        report = json.loads((self.fixture.runtime() / readiness['report']).read_bytes())
        self.assertEqual(json.loads(report['input_identity_json']), attempt['inputs'])
        self.assertNotEqual(attempt['inputs']['candidate']['key'], state['candidate']['key'])
        self.assertEqual(report['checks'][0]['prerequisite'], 'Python 3.11')
        prompt = self.fixture.fake.prompts[1][1]
        self.assertIn('NEVER a missing prerequisite', prompt)
        self.assertIn('actual required access', prompt)
        self.assertIn('Do not install dependencies', prompt)

    def test_missing_evidence_blocks_before_implementation_and_resumes_same_delivery(self):
        edit = self.missing('input', 'required historical SQL evidence',
                            'FIXTURE read historical.sql', 'historical.sql: No such file')
        with patch.object(d, 'launch', self.transport(edit)):
            code, result = self.fixture.cli()
        self.assertEqual(code, 1, result)
        self.assertIn('required historical SQL evidence', result['blocker'])
        self.assertIn('resume this delivery', result['blocker'])
        self.assertEqual(self.fixture.fake.calls, ['preflight', 'preflight'])
        before = self.fixture.state()
        self.assertFalse(before.get('preflight_complete'))
        self.assertEqual(before['task_readiness']['status'], 'BLOCKED')
        self.assertTrue(all(a['status'] == 'complete' for a in before['attempts']))
        self.assertEqual(before['attempts'][-1]['report_validation'], 'accepted')
        code, result = self.fixture.cli('resume')
        self.assertEqual(code, 0, result)
        after = self.fixture.state()
        self.assertEqual(after['invocation_id'], before['invocation_id'])
        self.assertEqual(after['attempts'][0]['id'], before['attempts'][0]['id'])
        self.assertEqual(after['task_readiness']['status'], 'READY')
        self.assertEqual(self.fixture.fake.calls, ['preflight', 'preflight', 'preflight',
                                                  'implementation', 'review', 'proof'])

    def test_unavailable_service_is_not_hidden_by_a_working_client_executable(self):
        edit = self.missing('service', 'local PostgreSQL socket',
                            'FIXTURE psql -h /tmp/required-socket -c SELECT_1',
                            'connection to required socket: Operation not permitted')
        with patch.object(d, 'launch', self.transport(edit)):
            code, result = self.fixture.cli()
        self.assertEqual(code, 1, result)
        self.assertIn('local PostgreSQL socket', result['blocker'])
        self.assertNotIn('implementation', self.fixture.fake.calls)
        self.assertNotIn('diagnosis', self.fixture.fake.calls)

    def test_readiness_rejects_unobserved_available_check(self):
        def unobserved(report, events):
            report['checks'][0]['observation'] = 'a capability the host never observed'

        with patch.object(d, 'launch', self.transport(unobserved)):
            code, result = self.fixture.cli()
        self.assertEqual(code, 1, result)
        self.assertIn('host-recorded command evidence', result['blocker'])
        attempt = self.fixture.state()['attempts'][-1]
        self.assertEqual(attempt['status'], 'complete')
        self.assertEqual(attempt['report_validation'], 'rejected')
        self.assertNotIn('implementation', self.fixture.fake.calls)

    def test_failed_command_cannot_establish_available_prerequisite(self):
        def failed(report, events):
            for event in events:
                item = event.get('item', {})
                if item.get('command') == report['checks'][0]['command']:
                    item['exit_code'] = 1

        with patch.object(d, 'launch', self.transport(failed)):
            code, result = self.fixture.cli()
        self.assertEqual(code, 1, result)
        self.assertIn('host-recorded command evidence', result['blocker'])
        self.assertNotIn('implementation', self.fixture.fake.calls)

    def test_recorded_shell_wrapper_preserves_exact_submitted_command(self):
        def wrapped(report, events):
            for event in events:
                item = event.get('item', {})
                if item.get('command') == report['checks'][0]['command']:
                    item['command'] = "/bin/zsh -lc '" + item['command'] + "'"

        with patch.object(d, 'launch', self.transport(wrapped)):
            code, result = self.fixture.cli()
        self.assertEqual(code, 0, result)
        self.assertEqual(self.fixture.fake.calls.count('preflight'), 2)

    def test_readiness_rejects_stale_candidate_identity(self):
        def stale(report, events):
            inputs = json.loads(report['input_identity_json'])
            inputs['candidate']['key'] = '0' * 64
            report['input_identity_json'] = json.dumps(inputs)

        with patch.object(d, 'launch', self.transport(stale)):
            code, result = self.fixture.cli()
        self.assertEqual(code, 1, result)
        self.assertIn('stale task-readiness', result['blocker'])
        self.assertEqual(self.fixture.state()['attempts'][-1]['report_validation'], 'rejected')
        self.assertNotIn('implementation', self.fixture.fake.calls)

    def test_resume_reuses_readiness_after_product_candidate_changes(self):
        code, result = self.fixture.cli('run', '--max-dispatches', '3')
        self.assertEqual(code, 1, result)
        before = self.fixture.state()
        self.assertTrue(before['implementation_complete'])
        self.assertEqual(self.fixture.cli('extend', '--authorize-extension', '--max-dispatches', '6')[0], 0)
        code, result = self.fixture.cli('resume')
        self.assertEqual(code, 0, result)
        after = self.fixture.state()
        self.assertEqual(after['task_readiness'], before['task_readiness'])
        self.assertEqual(self.fixture.fake.calls.count('preflight'), 2)
        self.assertEqual(self.fixture.fake.calls.count('implementation'), 1)

    def test_legacy_boundary_only_preflight_gets_one_readiness_refresh(self):
        code, result = self.fixture.cli('run', '--max-dispatches', '2')
        self.assertEqual(code, 1, result)
        state = self.fixture.state()
        attempt = state['attempts'][-1]
        attempt['inputs'].pop('task_readiness')
        attempt['inputs'].pop('candidate')
        folder = self.fixture.runtime() / 'attempts' / attempt['id']
        events = [json.loads(line) for line in (folder / 'events.jsonl').read_text().splitlines()]
        next(event['item'] for event in events if event.get('item', {}).get('type') == 'agent_message')['text'] = (
            'FIXTURE legacy boundary-only preflight')
        event_data = ''.join(json.dumps(event) + '\n' for event in events).encode()
        (folder / 'events.jsonl').write_bytes(event_data)
        end = json.loads((folder / 'exit.json').read_bytes())
        end.update(inputs=attempt['inputs'], event_sha256=d.fs.digest(event_data))
        (folder / 'exit.json').write_bytes(d.encoded(end))
        for key in ('report', 'report_sha256', 'report_validation'):
            attempt.pop(key, None)
        state.pop('task_readiness')
        delivery = d.Delivery(self.fixture.root, self.work, state)
        delivery.save()
        self.assertEqual(self.fixture.cli('extend', '--authorize-extension', '--max-dispatches', '6')[0], 0)
        code, result = self.fixture.cli('resume')
        self.assertEqual(code, 0, result)
        self.assertEqual(self.fixture.fake.calls.count('preflight'), 3)
        self.assertEqual(self.fixture.fake.calls.count('implementation'), 1)
        self.assertEqual(self.fixture.state()['task_readiness']['status'], 'READY')


if __name__ == '__main__':
    unittest.main()
