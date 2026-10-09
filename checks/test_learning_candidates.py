from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/productivity/deliver-issue/scripts"
sys.path.insert(0, str(SCRIPTS))
import p2p_delivery as delivery


class LearningCandidateTests(unittest.TestCase):
    def test_stage_reports_have_bounded_learning_candidates(self):
        for stage in ("implementation", "repair", "review", "proof"):
            with self.subTest(stage=stage):
                schema = delivery.report_schema(stage)
                learning = schema["properties"]["learning_candidates"]
                self.assertEqual(learning["type"], "array")
                self.assertEqual(learning["maxItems"], 5)
                item = learning["items"]
                self.assertEqual(
                    set(item["required"]),
                    {"scope", "lesson", "evidence", "uncertainty"},
                )
                self.assertFalse(item["additionalProperties"])

    def test_learning_candidate_rendering_marks_candidates_unvalidated(self):
        text = delivery.learning_candidates_markdown({
            "learning_candidates": [{
                "scope": "retry handling",
                "lesson": "A reusable candidate lesson.",
                "evidence": "Observed in the delivery.",
                "uncertainty": "Needs final proof context.",
            }]
        })
        self.assertIn("## Learning candidates", text)
        self.assertIn("candidate only; retrospective validation required", text)
        self.assertIn("Needs final proof context.", text)

    def test_empty_learning_candidates_are_explicitly_valid(self):
        self.assertIn("None.", delivery.learning_candidates_markdown({"learning_candidates": []}))

    def test_skill_boundaries_keep_retrospect_as_promoter(self):
        # Markdown line wrapping must not change these required authority rules.
        retrospect = " ".join((ROOT / "skills/productivity/retrospect/SKILL.md").read_text(encoding="utf-8").split())
        deliver = " ".join((ROOT / "skills/productivity/deliver-issue/SKILL.md").read_text(encoding="utf-8").split())
        self.assertIn("Treat those candidates only as attributed leads", retrospect)
        self.assertIn("only the existing explicit human disposition flow", retrospect)
        self.assertIn("Do not invoke it automatically", deliver)
        self.assertIn("do not promote candidate wording into project advice", deliver)


if __name__ == "__main__":
    unittest.main()
