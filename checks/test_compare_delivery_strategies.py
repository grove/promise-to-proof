#!/usr/bin/env python3
"""Hand-calculated offline accounting cases; no agent calls or external packages."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from compare_delivery_strategies import analyze


def episode(identity='a', strategy='review-first', duration=10, amount=3):
    stages = ['review', 'proof'] if strategy == 'review-first' else ['proof', 'review']
    return {'id': identity, 'task': 'greeting', 'strategy': strategy, 'evidence': 'synthetic',
            'host': {'os': 'macOS', 'version': 'synthetic'},
            'config': {'required_checks': ['review', 'proof'], 'repair_limit': 1,
                       'model': 'fixed', 'controller': 'fixed', 'permissions': 'same'},
            'start': 0, 'end': duration, 'reported_complete': True,
            'adjudication': {'outcome': 'satisfactory', 'missed_defects': 0, 'provenance': 'held-out oracle'},
            'human': {'active_seconds': 180, 'waiting_seconds': 600, 'interruptions': 2},
            'attempts': [{'id': str(i), 'stage': stage, 'start': duration*i/2, 'end': duration*(i+1)/2,
                          'cost': {'kind': 'measured', 'amount': amount if i == 0 else 0, 'provenance': 'synthetic charge'}}
                         for i, stage in enumerate(stages)]}


def cohort(*episodes):
    return {'schema_version': 1, 'currency': 'USD', 'episodes': list(episodes),
            'overhead': {'costs': [], 'active_seconds': 0, 'waiting_seconds': 0, 'interruptions': 0},
            'maintenance_seconds': 0}


class Accounting(unittest.TestCase):
    def test_cohort_eight_and_failed_episode(self):
        a, b = episode(), episode('b', amount=5)
        b['reported_complete'] = False
        b['adjudication'] = {'outcome': 'defective', 'missed_defects': 0, 'provenance': 'oracle'}
        report = analyze(cohort(a, b))['overall']
        self.assertEqual((report['assigned'], report['useful_completions']), (2, 1))
        self.assertEqual((report['cost']['total'], report['cost_per_assigned'], report['cost_per_useful_completion'], report['completion_rate']), (8, 4, 8, .5))

    def test_overlap_serial_and_episode_wait(self):
        e = episode()
        e['strategy'] = 'concurrent'
        e['attempts'][0].update(start=0, end=6)
        e['attempts'][1].update(start=2, end=10)
        row = analyze(cohort(e))['episodes'][0]
        self.assertEqual((row['occupied_seconds'], row['stage_seconds'], row['elapsed_seconds']), (10, 14, 10))
        self.assertFalse(row['eligible'])
        e['end'] = 20
        self.assertEqual(analyze(cohort(e))['episodes'][0]['elapsed_seconds'], 20)
        e['strategy'] = 'review-first'
        e['attempts'][1].update(start=6, end=14)
        row = analyze(cohort(e))['episodes'][0]
        self.assertEqual((row['occupied_seconds'], row['stage_seconds']), (14, 14))

    def test_resume_dedup_and_conflict(self):
        e = episode()
        e['attempts'].append(copy.deepcopy(e['attempts'][0]))
        self.assertEqual(analyze(cohort(e))['overall']['cost']['total'], 3)
        e['attempts'][-1]['cost']['amount'] = 9
        with self.assertRaisesRegex(ValueError, 'conflicting'):
            analyze(cohort(e))

    def test_unknown_cost_estimates_and_overhead(self):
        e = episode()
        e['attempts'][1]['cost'] = {'kind': 'unknown'}
        result = analyze(cohort(e))['overall']
        self.assertIsNone(result['cost']['total'])
        self.assertEqual(result['cost']['measured_subtotal'], 3)
        e['attempts'][1]['cost'] = {'kind': 'estimated', 'usage': {'tokens': 4}, 'rates': {'tokens': .5}, 'provenance': 'synthetic rate'}
        data = cohort(e)
        data['overhead']['costs'] = [{'kind': 'measured', 'amount': 1, 'provenance': 'evaluation charge'}]
        result = analyze(data)
        self.assertEqual(result['overall']['cost']['total'], 6)
        self.assertEqual(result['overall']['cost']['kind'], 'estimated')
        self.assertEqual(result['strategies']['review-first']['cost']['total'], 5)

    def test_missing_label_zero_success_false_green(self):
        e = episode()
        del e['adjudication']
        report = analyze(cohort(e))['overall']
        self.assertEqual(report['outcomes'], {'unresolved': 1})
        self.assertIsNone(report['missed_defects'])
        self.assertIsNone(report['cost_per_useful_completion'])
        e['adjudication'] = {'outcome': 'defective', 'missed_defects': 1, 'provenance': 'held-out seeded OSError defect'}
        report = analyze(cohort(e))['overall']
        self.assertEqual((report['useful_completions'], report['missed_defects']), (0, 1))
        self.assertIsNone(analyze(cohort())['overall']['completion_rate'])

    def test_human_and_missing_observations(self):
        data = cohort(episode())
        data['overhead']['active_seconds'] = 60
        report = analyze(data)
        self.assertEqual(report['overall']['human'], {'active_seconds': 180, 'waiting_seconds': 600, 'interruptions': 2})
        self.assertEqual(report['human_including_overhead']['active_seconds'], 240)
        del data['episodes'][0]['human']
        self.assertIsNone(analyze(data)['human_including_overhead']['active_seconds'])

    def test_sensitivity_crossover(self):
        data = cohort()
        data['sensitivity'] = [{'name': 'synthetic', 'a_base': 2, 'a_repair': 8, 'b_base': 5, 'b_repair': 0,
                                'failure_rates': [.25, .375, .5], 'provenance': 'hand arithmetic'}]
        row = analyze(data)['sensitivity'][0]
        self.assertEqual(row['crossover_failure_probability'], .375)
        self.assertEqual([v['a_expected_cost'] for v in row['values']], [4, 5, 6])
        self.assertEqual([v['preference'] for v in row['values']], ['a', 'tie', 'b'])

    def test_threshold_boundaries_and_no_winner(self):
        for duration, expected in [(81, False), (80, True), (79, True)]:
            data = cohort(episode(duration=100), episode('b', 'proof-first', duration))
            data['overhead']['active_seconds'] = 200
            decision = analyze(data)['decision']
            self.assertEqual(decision['descriptive_threshold_met'], expected)
            self.assertEqual(decision['status'], 'inconclusive')
            self.assertIsNone(decision['supported_winner'])
            self.assertIsNone(decision['break_even_episodes'])
            self.assertIsNone(decision['active_human_break_even_episodes'])
        data['episodes'][1]['adjudication'] = {'outcome': 'defective', 'missed_defects': 1, 'provenance': 'oracle'}
        self.assertFalse(analyze(data)['decision']['descriptive_threshold_met'])
        del data['episodes'][1]['human']
        self.assertIsNone(analyze(data)['decision']['descriptive_threshold_met'])

    def test_preparation_elapsed_is_retained_as_partial_overhead(self):
        data = cohort(episode(duration=10))
        data['overhead']['prepare_elapsed_seconds'] = 2
        report = analyze(data)
        self.assertEqual(report['overhead']['prepare_elapsed_seconds'], 2)
        self.assertEqual(report['elapsed_including_overhead']['known_subtotal_seconds'], 12)
        self.assertEqual(report['elapsed_including_overhead']['status'], 'partial')
        self.assertIsNone(report['elapsed_including_overhead']['total_seconds'])
        data['overhead']['prepare_elapsed_seconds'] = None
        self.assertIsNone(analyze(data)['overhead']['prepare_elapsed_seconds'])
        for invalid in (-1, float('nan')):
            data['overhead']['prepare_elapsed_seconds'] = invalid
            with self.assertRaises(ValueError):
                analyze(data)

    def test_human_payback_uses_per_episode_savings_on_matched_cohort(self):
        episodes = []
        for i in range(3):
            a, b = episode(f'a{i}'), episode(f'b{i}', 'proof-first')
            b['human']['active_seconds'] = 170
            episodes.extend([a, b])
        data = cohort(*episodes)
        data['overhead']['active_seconds'] = 300
        self.assertEqual(analyze(data)['decision']['active_human_break_even_episodes'], 30)
        data['episodes'][-1]['task'] = 'unmatched-task'
        self.assertIsNone(analyze(data)['decision']['active_human_break_even_episodes'])

    def test_public_cli_determinism_and_invalid_input(self):
        script = Path(__file__).with_name('compare_delivery_strategies.py')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'input.json'
            def run(data):
                path.write_text(json.dumps(data))
                return subprocess.run([sys.executable, str(script), str(path)], capture_output=True, text=True)
            first, second = run(cohort(episode())), run(cohort(episode()))
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(first.stdout, second.stdout)
            for field, value in [('start', -1), ('end', float('inf')), ('end', -1), ('reported_complete', 1), ('strategy', 'missing')]:
                data = cohort(episode())
                data['episodes'][0][field] = value
                self.assertNotEqual(run(data).returncode, 0, (field, value))
            data = cohort(episode())
            data['episodes'][0]['attempts'][1]['start'] = 0
            self.assertNotEqual(run(data).returncode, 0)
            data = cohort(episode())
            data['episodes'][0]['attempts'][0]['stage'] = 'proof'
            self.assertNotEqual(run(data).returncode, 0)


if __name__ == '__main__':
    unittest.main()
