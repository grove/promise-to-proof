"""Structural regressions for the shipped agent rules, not live model evidence.

These checks catch removed safeguards and contradictory mandatory instructions.
Behavioral delivery scenarios are in pragmatic-verification-scenarios.md; passing
this file does not establish model compliance or a measured latency improvement.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def text(path):
    return (ROOT / path).read_text(encoding='utf-8')


def words(value):
    return ' '.join(value.split())


def section(value, heading):
    match = re.search(r'^' + re.escape(heading) + r'\n(.*?)(?=^## |\Z)',
                      value, flags=re.M | re.S)
    if match is None:
        raise AssertionError(f'Missing normative section: {heading}')
    return words(match.group(1))


class PragmaticVerificationRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = text('docs/acceptance-contract-protocol.md')
        cls.proof = text('skills/productivity/prove/SKILL.md')
        cls.review = text('skills/productivity/review-implementation/SKILL.md')

    def policy(self):
        return section(self.protocol, '## Pragmatic assurance')

    def test_sufficient_assurance_is_the_default(self):
        self.assertIn('Establish sufficient assurance with the least work necessary.',
                      self.policy())
        self.assertIn('Stop when all accepted obligations have credible evidence',
                      self.policy())

    def test_binding_requirements_cannot_be_discarded(self):
        self.assertIn('Never drop, weaken, or relabel an accepted obligation as optional',
                      self.policy())
        self.assertIn('Explicit verification requirements and repository standards remain binding',
                      self.policy())

    def test_optional_findings_do_not_start_repairs(self):
        self.assertIn('Optional suggestions do not trigger implementation, repair, or another verification cycle.',
                      self.policy())
        self.assertIn('realistic trigger', self.policy())
        self.assertIn('smallest useful check', self.policy())

    def test_evidence_is_proportional_not_a_quota(self):
        self.assertIn('One credible evidence path can be sufficient', self.policy())
        self.assertIn('not a universal checklist', self.policy())
        self.assertIn('independently inspect', self.policy())

    def test_compact_planning_preserves_existing_contracts(self):
        self.assertIn('Do not turn rationale, illustrative examples, or optional implementation suggestions',
                      self.policy())
        self.assertIn('Do not re-plan an active contract merely to make it shorter.',
                      self.policy())

    def test_changed_candidates_still_need_both_fresh_reports(self):
        repair = section(self.protocol, '## Focused re-verification after a repair')
        self.assertIn('Both independent stages still issue fresh, full-scope reports', repair)
        self.assertIn('Never relabel an old verdict or evidence receipt with a new candidate identity.', repair)
        self.assertIn('Full scope means complete obligation coverage', repair)

    def test_reuse_requires_more_than_a_small_diff(self):
        repair = section(self.protocol, '## Focused re-verification after a repair')
        for obligation in ('complete candidate delta', 'dependencies', 'configuration',
                           'environment', 'independently establish', 'retrievable'):
            with self.subTest(obligation=obligation):
                self.assertIn(obligation, repair)
        self.assertIn('A small diff or an unchanged filename is not an applicability argument.', repair)
        self.assertIn('current other verifier', repair)

    def test_uncertain_applicability_requires_fresh_checking(self):
        repair = section(self.protocol, '## Focused re-verification after a repair')
        self.assertIn('When applicability cannot be established, do fresh checking', repair)
        self.assertIn('full checking when the uncertainty cannot be bounded', repair)
        self.assertIn('Do not expand a verifier\'s sandbox or expose another verifier\'s results', repair)

    def test_proof_selects_risks_instead_of_an_exhaustive_checklist(self):
        self.assertIn('### 4. Check material counterexamples', self.proof)
        self.assertNotIn('### 4. Hunt counterexamples', self.proof)
        self.assertIn('Stop investigating when', self.proof)

    def test_full_suite_is_conditional_but_binding_checks_remain(self):
        proof = words(self.proof)
        self.assertNotIn('Run the full suite once on a clean copy of the final frozen candidate;', proof)
        self.assertIn('Run a full suite when the accepted contract or repository standards require it', proof)
        self.assertIn('Do not skip a binding check', proof)

    def test_review_finishes_without_optional_polishing(self):
        review = words(self.review)
        self.assertIn('Return `REVIEWED` with optional suggestions', review)
        self.assertIn('Do not turn optional suggestions into `CHANGES NEEDED`', review)
        self.assertIn('The reviewer, not the implementer or controller, owns', review)

    def test_verifiers_link_to_the_canonical_rules(self):
        for skill in (self.proof, self.review):
            for anchor in ('pragmatic-assurance', 'focused-re-verification-after-a-repair'):
                with self.subTest(anchor=anchor, skill=skill.splitlines()[1]):
                    self.assertIn('references/acceptance-contract-protocol.md#' + anchor, skill)

    def test_evidence_validators_are_not_bypassed_for_reuse(self):
        repair = section(self.protocol, '## Focused re-verification after a repair')
        self.assertIn('Existing evidence and bundle validators keep their exact-identity checks.', repair)
        self.assertIn('rerun the check rather than bypassing validation.', repair)

    def test_existing_acceptance_and_authority_guards_remain(self):
        protocol = words(self.protocol)
        for guard in ('A manually edited verdict does not establish acceptance.',
                      'Only `prove` issues acceptance verdicts;',
                      'Effect grants specify one supported action, exact repository and exact destination;',
                      'Otherwise the result is `NOT PROVEN`.',
                      'Drift invalidates the run rather than authorizing a repair during proof.'):
            with self.subTest(guard=guard):
                self.assertIn(guard, protocol)


if __name__ == '__main__':
    unittest.main()
