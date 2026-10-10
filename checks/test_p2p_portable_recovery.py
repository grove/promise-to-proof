#!/usr/bin/env python3
"""Recovery across disposable Git clones; fixture transport, never live models."""
import json
import unittest
from unittest.mock import patch

import test_p2p_checkpoints as checkpoints
import test_p2p_delivery as fixtures
import test_p2p_recovery as recovery

d = fixtures.d
WORK = '.p2p/work/tiny/contract.md'


class PortableRecoveryTests(unittest.TestCase):
    setUp = fixtures.DeliveryTests.setUp
    tearDown = fixtures.DeliveryTests.tearDown
    cli = fixtures.DeliveryTests.cli
    cli_item = fixtures.DeliveryTests.cli_item
    run_root = fixtures.DeliveryTests.run_root
    state = fixtures.DeliveryTests.state
    runtime = fixtures.DeliveryTests.runtime
    responses = recovery.RecoveryReceiptTests.responses

    def restore_on_another_computer(self):
        checkpoint = json.loads((self.root / 'p2p-state/tiny.json').read_bytes())
        self.assertEqual(checkpoint['execution']['status'], 'BLOCKED')
        publisher = checkpoints.CheckpointTests()
        publisher.fixture, publisher.root, publisher.work = self, self.root, WORK
        _, clone = publisher.publish_fixture(checkpoint)
        data = (self.root / 'p2p-state/tiny.json').read_bytes()
        self.assertEqual(d.fs.restore_checkpoint(clone, data)['status'], 'RESTORED')
        return clone

    def test_unconsumed_diagnosis_rechecks_capability_on_receiving_host(self):
        self.fake.mode = 'partial-implementation'
        original = d.Delivery.save
        interrupted = False

        def save(delivery):
            nonlocal interrupted
            original(delivery)
            if not interrupted and delivery.state.get('recovery_decision', {}).get('status') == 'diagnosed':
                interrupted = True
                raise OSError('fixture interruption after accepted diagnosis')

        with patch.object(d.Delivery, 'save', save):
            code, value = self.cli()
        self.assertEqual(code, 1, value)
        self.assertEqual(self.fake.calls.count('diagnosis'), 1)
        self.assertNotIn('repair', self.fake.calls)
        previous = self.state()
        original_diagnosis = previous['recovery_decision']['attempt_id']

        clone = self.restore_on_another_computer()
        code, value = self.run_root(clone, WORK, self.base, 'resume')

        self.assertEqual(code, 0, value)
        self.assertEqual(value['status'], 'REVIEWED_AND_PROVEN')
        self.assertEqual(value['invocation_id'], previous['invocation_id'])
        self.assertEqual(self.fake.calls,
                         ['preflight', 'preflight', 'implementation', 'diagnosis',
                          'preflight', 'preflight', 'diagnosis', 'repair', 'review', 'proof'])
        state = json.loads((clone / '.p2p/work/tiny/delivery.json').read_bytes())
        self.assertNotEqual(state['recovery_history'][-1]['diagnosis_attempt_id'], original_diagnosis)
        self.assertEqual(state['recovery_decision']['status'], 'consumed')

    def test_rejected_mutator_checkpoint_preserves_work_without_acceptance(self):
        with self.responses(lambda stage, message: '{}' if stage == 'implementation' else message):
            code, value = self.cli()
        self.assertEqual(code, 1, value)
        self.assertEqual(self.state()['attempts'][-1]['report_validation'], 'rejected')
        candidate = value['candidate']
        clone = self.restore_on_another_computer()
        calls = list(self.fake.calls)

        for action in ('resume', 'status'):
            code, value = self.run_root(clone, WORK, self.base, action)
            self.assertEqual(code, 1, value)
            self.assertEqual(value['status'], 'BLOCKED')
            self.assertIn('unsupported or missing fields', value['blocker'])
            self.assertEqual(value['candidate'], candidate)
            self.assertEqual(self.fake.calls, calls)

        state = json.loads((clone / '.p2p/work/tiny/delivery.json').read_bytes())
        delivery = d.Delivery(clone, WORK, state)
        self.assertFalse(state.get('implementation_complete'))
        self.assertFalse({'implementation', 'review', 'proof'} & state['reports'].keys())
        self.assertEqual((delivery.workspace / 'greet.py').read_text(), "print('hello')\n")
        self.assertFalse((clone / 'greet.py').exists())
        with self.assertRaises((KeyError, ValueError)):
            delivery.complete()
        self.assertFalse((delivery.runtime / 'acceptance-bundle.json').exists())


if __name__ == '__main__':
    unittest.main()
