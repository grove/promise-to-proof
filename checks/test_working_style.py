"""Structural regressions for Promise to Proof's user-facing working style.

These checks protect shipped instructions. They do not establish live-model
compliance; the behavioral scenario lives in pragmatic-verification-scenarios.md.
"""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "audit-acceptance",
    "create-parent-issue",
    "critique",
    "deliver-issue",
    "fix-pr",
    "implement-contract",
    "interrogate",
    "merge-readiness",
    "plan-acceptance",
    "prove",
    "publish-pr",
    "repair-gaps",
    "retrospect",
    "review-implementation",
    "setup-promise-to-proof",
    "slice-contract",
    "triage-issue",
)


def text(path):
    return (ROOT / path).read_text(encoding="utf-8")


class WorkingStyleRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = text("docs/acceptance-contract-protocol.md")

    def test_protocol_defines_plain_pragmatic_working_style(self):
        for phrase in (
            "## Voice and working style",
            "### Use plain language by default",
            "### Be clear-eyed, not cheerleading",
            "### Look for leverage",
            "### Prefer practical progress",
            "### Make proposals concrete",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.protocol)

    def test_pragmatism_preserves_rigor_and_authority(self):
        # Protect the required wording independently of Markdown line wrapping.
        protocol = " ".join(self.protocol.split())
        for guard in (
            "Leverage never authorizes weakening or reinterpreting an accepted promise",
            "Pragmatic does not mean careless.",
            "A recommendation is not a verdict, proof, approval, or new authority.",
        ):
            with self.subTest(guard=guard):
                self.assertIn(guard, protocol)

    def test_delivery_orchestrator_translates_mechanics_for_people(self):
        deliver = text("skills/productivity/deliver-issue/SKILL.md")
        self.assertIn("## Make delivery easy to follow", deliver)
        self.assertIn("Translate stage verdicts and blockers into ordinary", deliver)
        self.assertIn("recommend the strongest path", deliver)
        self.assertIn("Do not smooth over a failed check", deliver)

    def test_agent_map_treats_conversation_as_product_behavior(self):
        agents = text("AGENTS.md")
        self.assertIn("## User-facing behavior", agents)
        self.assertIn("Conversation behavior is product behavior.", agents)
        self.assertIn("proactive", agents)
        self.assertIn("one obvious next action", agents)

    def test_standalone_skills_ship_the_canonical_working_style(self):
        for skill in SKILLS:
            with self.subTest(skill=skill):
                reference = text(
                    f"skills/productivity/{skill}/references/"
                    "acceptance-contract-protocol.md"
                )
                self.assertEqual(self.protocol, reference)

    def test_behavioral_scenario_covers_plain_solution_oriented_delivery(self):
        scenarios = text("checks/pragmatic-verification-scenarios.md")
        self.assertIn("## 11. Plain-language, solution-oriented delivery", scenarios)
        self.assertIn("existing repository helper", scenarios)
        self.assertIn("smallest complete path", scenarios)
        self.assertIn("missing effect", scenarios)
        self.assertIn("must not hide the blocker", scenarios)


if __name__ == "__main__":
    unittest.main()
