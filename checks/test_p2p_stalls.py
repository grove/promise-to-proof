#!/usr/bin/env python3
"""Deterministic stall classification; no model or network dependency."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       'skills/productivity/deliver-issue/scripts'))
import p2p_stalls as stalls


def completed(before, after, findings, *, method='initial-seam'):
    return {'status': 'complete', 'candidate_before': before, 'candidate_after': after,
            'findings': findings, 'action': 'implementation', 'strategy_key': method,
            'approach': 'Inspect the first implementation path.',
            'capability_check': 'P2P_RECOVERY_CAPABILITY=fixture local CLI available'}


class StallSignalsTests(unittest.TestCase):
    def test_reworded_failure_still_identifies_same_obligation_and_seam(self):
        first = {'review': [{'source': 'R1', 'axis': 'Contract fidelity',
                             'location': 'src/output.py:42', 'evidence': 'Missing stdout'}],
                 'unproven': ['R1']}
        second = {'review': [{'source': 'R1', 'axis': 'Contract fidelity',
                              'location': 'src/output.py:99', 'evidence': 'No observed output'}],
                  'unproven': ['R1']}
        detected = stalls.detect(second, 'candidate-b', [completed('candidate-a', 'candidate-b', first)], ['R1'])
        self.assertEqual(detected['kind'], 'unresolved_proof_behavior')
        self.assertEqual(detected['requirements'], ['R1'])
        self.assertEqual(stalls.signals(first, ['R1'])['seams'],
                         stalls.signals(second, ['R1'])['seams'])

    def test_same_failed_reproduction_survives_changed_verifier_wording(self):
        first = {'failed_checks': [{'command': 'python3  greet.py', 'result': 'failed'}]}
        second = {'failed_checks': [{'command': 'python3 greet.py', 'result': 'failed'}],
                  'review_gaps': ['The CLI result remains unacceptable']}
        result = stalls.detect(second, 'candidate-b', [completed('candidate-a', 'candidate-b', first)], ['R1'])
        self.assertEqual(result['kind'], 'unchanged_failed_reproduction')
        self.assertEqual(result['checks'], ['python3 greet.py'])

    def test_real_candidate_oscillation_is_detected_across_different_failure_phases(self):
        history = [completed('A', 'B', {'implementation': ['R1 not done']}),
                   completed('B', 'A', {'review_gaps': ['Different issue']})]
        result = stalls.detect({'proof_gaps': ['Newly phrased failure']}, 'A', history, ['R1'])
        self.assertEqual(result['kind'], 'candidate_oscillation')

    def test_transient_and_changed_requirements_do_not_trigger_reset(self):
        self.assertIsNone(stalls.detect({'review_gaps': ['one temporary timeout']},
                                        'A', [], ['R1']))
        history = [completed('A', 'B', {'implementation': ['R1 wrong']})]
        self.assertIsNone(stalls.detect({'implementation': ['R2 wrong']},
                                        'B', history, ['R1', 'R2']))
        self.assertIsNone(stalls.detect({'review_gaps': ['temporary error']},
                                        'B', [completed('A', 'B', {'review_gaps': ['different']})],
                                        ['R1']))

    def test_repeated_noop_without_named_obligations_is_a_stall_only_after_two(self):
        findings = {'implementation': ['Unexplained retry failure']}
        first = completed('A', 'A', findings)
        self.assertIsNone(stalls.detect(findings, 'A', [first], ['R1']))
        self.assertEqual(stalls.detect(findings, 'A', [first, first], ['R1'])['kind'],
                         'repeated_nonprogress')

    def test_failed_review_checks_exclude_unavailable_and_passed(self):
        got = stalls.failed_checks({'checks': [
            {'command': 'pytest', 'result': 'failed'},
            {'command': 'cargo test', 'result': 'unavailable'},
            {'command': 'python3 test.py', 'result': 'passed'}]})
        self.assertEqual(got, [{'command': 'pytest', 'result': 'failed'}])

    def test_same_method_hidden_behind_paraphrase_is_rejected(self):
        old = completed('A', 'B', {'implementation': ['R1']}, method='read-and-rewrite')
        new = {'action': 'implementation', 'strategy_key': 'read-and-rewrite',
               'approach': 'Completely different words for the same repair',
               'capability_check': old['capability_check']}
        self.assertIn('exhausted', stalls.strategy_repetition(new, [old]))
        new['strategy_key'] = 'alternate-reproducer'
        self.assertIsNone(stalls.strategy_repetition(new, [old]))

    def test_testable_expected_result_is_required(self):
        self.assertFalse(stalls.falsifiable('Try harder until complete.'))
        self.assertFalse(stalls.falsifiable('Check that it is better.'))  # non-falsifiable
        self.assertTrue(stalls.falsifiable(
            'Run python3 greet.py, assert stdout is hello newline, and observe exit zero.'))

    def test_bounded_perspective_reset_keeps_exact_ids_and_recent_strategies(self):
        state = {'contract': {'source': 'Issue #74', 'sha256': 'a' * 64,
                             'content': 'Intended outcome: Return the correct result.\n'},
                 'requirements': ['R1'], 'comparison_base': 'b' * 40,
                 'candidate': {'key': 'tree-A'},
                 'autonomy': {'policy': {'constraints': ['do not weaken contract']}}}
        history = [completed(str(i), str(i + 1), {'proof_gaps': ['R1']},
                             method='method-' + str(i)) for i in range(20)]
        result = stalls.reset_context(state, '.p2p/work/tiny/contract.md',
                                      {'proof_gaps': ['R1 missing']}, history, {'kind': 'same'})
        self.assertEqual(result['promise'], 'Return the correct result.')
        self.assertEqual(result['agreement']['sha256'], 'a' * 64)
        self.assertEqual(result['base'], 'b' * 40)
        self.assertIn('method-19', result['prior_strategies'])
        self.assertNotIn('method-1"', result['prior_strategies'])
        self.assertLess(len(result['prior_strategies']), 3600)


if __name__ == '__main__':
    unittest.main()
