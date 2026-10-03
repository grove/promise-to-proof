"""Mandate scope and unlimited serialization, independent of host execution."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/productivity/deliver-issue/scripts'))
import p2p_autonomy as a


class AutonomyTests(unittest.TestCase):
    def test_unlimited_aliases_serialize_as_null(self):
        for value in (None, 'null', 'none', 'unlimited', 'infinite', 'inf', 'Infinity'):
            with self.subTest(value=value):
                self.assertIsNone(a.limit(value))
                self.assertEqual(json.dumps(a.limit(value), allow_nan=False), 'null')
        self.assertEqual(a.limit('0'), 0)
        self.assertEqual(a.limit('2', integer=True), 2)

    def test_invalid_and_nonintegral_limits_are_rejected(self):
        for value in ('nan', '-inf', '-1', 'junk'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                a.limit(value)
        with self.assertRaises(ValueError):
            a.limit('2.5', integer=True)

    def test_local_authority_has_no_effects(self):
        record = a.local('Deliver the agreed outcome')
        self.assertEqual(set(record['policy']['decisions']), a.DECISIONS)
        with self.assertRaisesRegex(ValueError, 'outside the standing mandate'):
            a.authorize(record, 'push', 'owner/repo', 'feature/x')

    def test_exact_grants_do_not_cover_other_actions_or_destinations(self):
        record = a.local('Deliver and publish')
        record['policy']['effects'] = [{'action':'push', 'repository':'owner/repo', 'destination':'feature/x'}]
        self.assertEqual(a.authorize(record, 'push', 'owner/repo', 'feature/x')['action'], 'push')
        for action, repo, target in [('merge','owner/repo','feature/x'), ('push','owner/other','feature/x'),
                                     ('push','owner/repo','main')]:
            with self.subTest(action=action, repo=repo, target=target), self.assertRaises(ValueError):
                a.authorize(record, action, repo, target)

    def test_file_changes_invalidate_saved_authority(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'mandate.json'
            path.write_text(json.dumps(a.local('Deliver')['policy']))
            record = a.load(path)
            a.current(record)
            path.write_text(path.read_text() + '\n')
            with self.assertRaisesRegex(ValueError, 'mandate changed'):
                a.current(record)

    def test_wildcards_force_push_and_unknown_decisions_are_rejected(self):
        for action, target in [('push','feature/*'), ('force-push','feature/x')]:
            policy = a.local('Deliver')['policy']
            policy['effects'] = [{'action': action, 'repository': 'owner/repo', 'destination': target}]
            with self.assertRaises(ValueError):
                a.validate(policy)
        policy = a.local('Deliver')['policy']
        policy['decisions'].append('weaken-proof')
        with self.assertRaises(ValueError):
            a.validate(policy)

    def test_schema_and_attribution_are_required(self):
        for change in ({'approval_source':''}, {'schema':'unknown'}, {'effects':None}, {'surprise':True}):
            policy = a.local('Deliver')['policy'] | change
            with self.subTest(change=change), self.assertRaises(ValueError):
                a.validate(policy)


if __name__ == '__main__':
    unittest.main()
