"""Pure admission condition rules, no claimed live host evidence."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "skills/productivity/deliver-issue/scripts"))
import p2p_admission as a


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.state = {"invocation_id": "inv", "work_item": "work.md",
            "contract": {"source": "source", "revision": "v1", "sha256": "abc"},
            "requirements": ["R1"], "binding_inputs": [], "routing":
            {"destination": "main", "target_tip": "old"}, "routing_records": [],
            "comparison_base": "base", "starting_commit": "base",
            "source_tree_key": "tree", "source_index_sha256": "index",
            "excluded_dirty": [], "agreement_paths": ["work.md"],
            "base_tree_key": "base-tree", "local_git_base": {"ref": "base"},
            "previous_records": {}, "task_readiness": {"status": "READY"}}

    def decision(self, previous=None):
        return a.admitted(self.state, "enforced host", {"host": "host",
            "contract": self.state["contract"]["sha256"]},
            {"verifier": "verified-boundary-attempt",
             "prerequisites": "verified-readiness-report"}, previous)

    def test_explicit_admitted_and_reused_identities(self):
        old = self.decision()
        self.assertEqual(old["status"], "ADMITTED")
        self.assertEqual(len(old["conditions"]), 6)
        new = self.decision(old)
        self.assertTrue(all(row["applicability"] == "REUSED"
                            for row in new["conditions"]))

    def test_destination_tip_and_limits_do_not_invalidate(self):
        old = self.decision()
        self.state["routing"]["target_tip"] = "advanced"
        self.state["limits"] = {"dispatches": 100}
        self.assertEqual(a.applicability(old, a.facts(self.state, "enforced host",
            {"host": "host", "contract": "abc"}))["routing"], "REUSABLE_AFTER_READBACK")

    def test_changed_route_contract_and_capability_need_refresh(self):
        old = self.decision()
        self.state["routing"]["destination"] = "release"
        self.state["contract"]["sha256"] = "changed"
        classifications = a.applicability(old, a.facts(self.state, "other host",
            {"host": "host", "contract": "changed"}))
        for name in ("routing", "agreement", "verifier", "prerequisites"):
            self.assertEqual(classifications[name], "REFRESH_REQUIRED")
        self.assertEqual(classifications["recovery"], "REUSABLE_AFTER_READBACK")

    def test_blockers_name_owner_fact_and_action(self):
        blocked = a.blocked(self.state, "agreement", "Source conflict",
                            "accepted source revision", "Return to planning")
        self.assertEqual(blocked["status"], "BLOCKED")
        self.assertEqual(blocked["owner"], "plan-acceptance")
        with self.assertRaises(ValueError):
            a.blocked(self.state, "unknown", "x", "y", "z")

    def test_unverified_or_missing_receipts_never_admit(self):
        with self.assertRaises(ValueError):
            a.admitted(self.state, "host", {}, {"verifier": "claim"})
        self.state["task_readiness"]["status"] = "BLOCKED"
        with self.assertRaises(ValueError):
            self.decision()


if __name__ == "__main__":
    unittest.main()
