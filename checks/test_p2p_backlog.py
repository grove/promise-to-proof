"""Deterministic affected-backlog scenarios; no live tracker or model claim."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "skills/productivity/replan-backlog/scripts"))
import p2p_backlog as b


def issue(number, states, *, affected=True, active=False, amendment=False):
    return {"id": number, "state": "open", "affected": affected,
            "active_contract": active, "material_amendment": amendment,
            "obligations": [{"id": f"R{i}", "promise": f"Outcome {i}", "state": state,
                             "evidence": f"git:{number}:{i}" if state != "missing" else None}
                            for i, state in enumerate(states, 1)]}


class BacklogTests(unittest.TestCase):
    def test_affected_partial_narrows_and_unrelated_is_not_selected(self):
        result = b.assess([issue(10, ["shipped", "missing"]), issue(11, ["missing"], affected=False)])
        self.assertEqual([(r["id"], r["action"], r["remaining"]) for r in result],
                         [(10, "NARROW", ["R2"])])

    def test_all_open_includes_unrelated_without_rewriting_it(self):
        result = b.assess([issue(10, ["shipped"]), issue(11, ["missing"], affected=False)],
                          all_open=True)
        self.assertEqual([(r["id"], r["action"]) for r in result],
                         [(10, "CLOSE"), (11, "KEEP")])

    def test_pending_pr_and_unexecuted_validation_never_close(self):
        result = b.assess([issue(1, ["pending_pr"]), issue(2, ["shipped", "needs_validation"])])
        self.assertEqual([r["action"] for r in result], ["KEEP", "VERIFY"])

    def test_accepted_in_flight_stays_pinned_and_amendment_handoff_is_explicit(self):
        item = b.assess([issue(1, ["shipped"], active=True, amendment=True)])[0]
        self.assertEqual(item["action"], "KEEP")
        self.assertEqual(item["amendment_handoff"], "plan-acceptance")

    def test_no_shipped_claim_without_retrievable_evidence(self):
        with self.assertRaisesRegex(ValueError, "retrievable evidence"):
            b.assess([{"id": 1, "state": "open", "affected": True,
                       "obligations": [{"id": "R1", "promise": "Works", "state": "shipped"}]}])

    def test_hard_prerequisites_and_parallel_candidates(self):
        plan = b.roadmap([{"id": 1, "hard_dependencies": []},
                          {"id": 2, "hard_dependencies": [1]},
                          {"id": 3, "hard_dependencies": []}])
        self.assertEqual(plan["parallel_waves"], [[1, 3], [2]])
        self.assertEqual(plan["next"], 1)
        with self.assertRaisesRegex(ValueError, "cycle"):
            b.roadmap([{"id": 1, "hard_dependencies": [2]},
                       {"id": 2, "hard_dependencies": [1]}])
        with self.assertRaisesRegex(ValueError, "unresolved prerequisite"):
            b.roadmap([{"id": 1, "hard_dependencies": [99]}])


if __name__ == "__main__":
    unittest.main()
