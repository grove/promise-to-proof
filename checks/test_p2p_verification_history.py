#!/usr/bin/env python3
"""Same-stage observation handoffs through real controller fixture deliveries."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_p2p_delivery as fixture

d = fixture.d


class VerificationHistoryTests(unittest.TestCase):
    def setUp(self):
        self.case = fixture.DeliveryTests()
        self.case.setUp()
        self.addCleanup(self.case.tearDown)

    def delivery(self):
        return d.Delivery(self.case.root, '.p2p/work/tiny/contract.md', self.case.state())

    def test_repair_hands_each_verifier_only_its_own_observations_and_complete_delta(self):
        self.case.fake.mode = 'repair'
        histories = []
        original = d.Delivery.verification_history

        def change_inputs(stage):
            workspace = self.case.runtime() / 'workspace'
            if stage == 'implementation':
                (workspace / 'settings.json').write_text('{"enabled": false}\n')
                (workspace / 'alias').symlink_to('greet.py')
            elif stage == 'repair':
                (workspace / 'settings.json').write_text('{"enabled": true}\n')
                (workspace / 'alias').unlink()
                (workspace / 'alias').symlink_to('settings.json')
                (workspace / 'greet.py').chmod(0o755)

        self.case.fake.on_stage = change_inputs

        def observe(delivery, stage):
            value = original(delivery, stage)
            histories.append((stage, value))
            return value

        with patch.object(d.Delivery, 'verification_history', observe):
            code, result = self.case.cli()
        self.assertEqual(code, 0, result)
        self.assertEqual(result['status'], 'REVIEWED_AND_PROVEN')
        self.assertEqual([stage for stage, _ in histories], ['review', 'proof', 'review', 'proof'])
        self.assertEqual([value for _, value in histories[:2]], [None, None])
        state = self.case.state()
        for name, history in histories[2:]:
            self.assertTrue(history['available'], history)
            previous = next(attempt for attempt in state['attempts'] if attempt['id'] == history['attempt_id'])
            self.assertEqual(previous['stage'], name)
            self.assertEqual(history['stage'], name)
            self.assertNotEqual(history['previous_candidate']['key'], history['current_candidate']['key'])
            changes = {change['path']: change for change in history['complete_delta']}
            self.assertEqual(set(changes), {'alias', 'greet.py', 'settings.json'})
            self.assertEqual(changes['greet.py']['mode'], '100755')
            self.assertEqual(changes['alias']['type'], 'symlink')
            saved = Path(history['report']['path']).read_bytes()
            self.assertEqual(d.fs.digest(saved), history['report']['sha256'])
            self.assertEqual(json.loads(json.loads(saved)['input_identity_json']), previous['inputs'])
        review_history, proof_history = histories[2][1], histories[3][1]
        self.assertNotEqual(review_history['attempt_id'], proof_history['attempt_id'])
        for name, history in histories[2:]:
            prompt = [text for stage, text in self.case.fake.prompts if stage == name][-1]
            self.assertIn(history['report']['path'], prompt)
            other = proof_history if name == 'review' else review_history
            self.assertNotIn(other['report']['path'], prompt)

    def test_lost_or_corrupt_old_evidence_falls_back_to_fresh_checks_without_relabeling(self):
        code, result = self.case.cli()
        self.assertEqual(code, 0, result)
        delivery = self.delivery()
        previous = next(attempt for attempt in delivery.state['attempts'] if attempt['stage'] == 'proof')
        report = delivery.runtime / previous['report']
        original = report.read_bytes()
        report.write_bytes(original + b' ')
        history = delivery.verification_history('proof')
        self.assertFalse(history['available'])
        self.assertNotIn('report', history)
        self.assertEqual(previous['status'], 'complete')
        report.write_bytes(original)
        events = delivery.runtime / 'attempts' / previous['id'] / 'events.jsonl'
        events.unlink()
        self.assertFalse(delivery.verification_history('proof')['available'])
        self.assertEqual(previous['status'], 'complete')

    def test_other_contract_or_environment_cannot_supply_reusable_observations(self):
        code, result = self.case.cli()
        self.assertEqual(code, 0, result)
        delivery = self.delivery()
        previous = next(attempt for attempt in delivery.state['attempts'] if attempt['stage'] == 'review')
        self.assertIsNone(delivery.verification_history('implementation'))
        previous['verification_environment'] = 'a different runtime'
        self.assertFalse(delivery.verification_history('review')['available'])
        previous['verification_environment'] = delivery.verification_environment()
        previous['inputs']['work_item_sha256'] = '0' * 64
        self.assertIsNone(delivery.verification_history('review'))

    def test_portable_report_without_local_command_output_is_not_a_reuse_cache(self):
        code, result = self.case.cli()
        self.assertEqual(code, 0, result)
        delivery = self.delivery()
        previous = next(attempt for attempt in delivery.state['attempts'] if attempt['stage'] == 'proof')
        (delivery.runtime / 'attempts' / previous['id'] / 'portable-receipt.json').write_text('{}')
        history = delivery.verification_history('proof')
        self.assertFalse(history['available'])
        self.assertNotIn('report', history)


if __name__ == '__main__':
    unittest.main()
