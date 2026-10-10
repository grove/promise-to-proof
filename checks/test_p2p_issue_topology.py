"""Offline deterministic #78 topology and supersession tests (no tracker writes)."""
import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "skills/productivity/deliver-issue/scripts"))
import p2p_issue_topology as topology
import p2p_autonomy as autonomy


def sample(*, parallel=False):
    return {
        "origin": {"reference": "grove/project#10", "contract": ".p2p/work/origin/contract.md",
                   "revision": "v1", "sha256": "a" * 64,
                   "promise": "An atomic reliable end-to-end result.",
                   "obligations": ["R1", "R2", "R3"]},
        "sizing": {"decision": "SPLIT", "identity": "b" * 64,
                   "evidence": "Saved source-bound #77 candidate/report showing two independently provable seams.",
                   "reason": "A compatibility boundary separates migration from cutover."},
        "factors": {"naturally_sequential": not parallel, "parallel_ownership": parallel,
                    "long_lived_aggregate": False, "independent_parent_integration": False,
                    "reason": "The evidence supports exactly two useful outcome units."},
        "units": [
            {"id": "S1", "outcome": "Compatibility preparation", "contributes": ["R1", "R2"],
             "blocked_by": [], "status": "active"},
            {"id": "S2", "outcome": "Cutover and complete acceptance", "contributes": ["R2", "R3"],
             "blocked_by": ["S1"], "status": "pending"},
        ],
        "order": ["S1", "S2"], "existing_work": [], "existing_shape": None}


def replacements(decision):
    origin = decision["origin"]["reference"]
    return [{"id": name, "url": f"https://github.com/grove/project/issues/{i}",
             "body": f"Source: {origin}\n<!-- grove:issue-topology origin={origin} unit={name} -->"}
            for i, name in enumerate(decision["order"], 11)]


def issue():
    return {"repository": "grove/project", "number": 10, "state": "open",
            "body": "Original promise and human discussion.", "state_reason": None}


class TopologyTests(unittest.TestCase):
    def test_sequential_two_unit_fixture_prefers_no_synthetic_parent(self):
        result = topology.choose(sample())
        self.assertEqual(result["status"], "RECOMMENDED")
        self.assertEqual(result["shape"], "standalone-sequence")
        self.assertEqual(result["current"], "S1")
        self.assertEqual(result["next"], "S2")
        self.assertEqual(result["final_acceptance"]["owner"], "S2")
        self.assertEqual(result["final_acceptance"]["covers"], ["R1", "R2", "R3"])
        self.assertEqual(result["units"][0]["blocked_by"], [])
        self.assertEqual(result["units"][1]["blocked_by"], ["S1"])
        self.assertEqual(result["allocations"]["R2"], ["S1", "S2"])
        self.assertFalse(result["tracker_effects_authorized"])

    def test_parallel_fixture_keeps_useful_parent(self):
        source = sample(parallel=True)
        source["units"][1]["blocked_by"] = []
        result = topology.choose(source)
        self.assertEqual(result["shape"], "parent-tree")
        self.assertEqual(result["final_acceptance"]["owner"], source["origin"]["reference"])
        self.assertIn("parallel_ownership", result["topology_reason"])

    def test_missing_existing_sizing_or_obligation_rejected(self):
        source = sample()
        source["sizing"]["decision"] = "NO SPLIT"
        with self.assertRaisesRegex(ValueError, "SPLIT"):
            topology.choose(source)
        source = sample()
        source["units"][1]["contributes"] = ["R2"]
        with self.assertRaisesRegex(ValueError, "unallocated"):
            topology.choose(source)
        source = sample()
        source["units"][0]["blocked_by"] = ["S2"]
        with self.assertRaisesRegex(ValueError, "prerequisite"):
            topology.choose(source)

    def test_sequence_order_is_not_a_made_up_dependency(self):
        source = sample()
        source["units"][1]["blocked_by"] = []
        result = topology.choose(source)
        self.assertEqual(result["units"][1]["blocked_by"], [])
        self.assertEqual(result["order"], ["S1", "S2"])

    def test_late_change_preserves_existing_pr_candidate_review_identities(self):
        source = sample()
        source["existing_shape"] = "parent-tree"
        source["existing_work"] = [
            {"reference": "https://github.com/grove/project/pull/8",
             "identity": "c" * 64, "ownership": "S1", "affects_boundary": True},
            {"reference": "saved:review/1", "identity": "d" * 64,
             "ownership": "historical", "affects_boundary": False},
            {"reference": "saved:candidate/1", "identity": "e" * 64,
             "ownership": "S1", "affects_boundary": True}]
        before = copy.deepcopy(source["existing_work"])
        result = topology.choose(source)
        self.assertEqual(result["status"], "RECONCILIATION_REQUIRED")
        self.assertEqual(result["existing_work"], before)
        self.assertEqual(result["origin"], source["origin"])
        self.assertEqual(result["sizing"], source["sizing"])
        self.assertFalse(result["tracker_effects_authorized"])

    def test_unresolved_existing_work_blocks_migration(self):
        source = sample()
        source["existing_shape"] = "parent-tree"
        source["existing_work"] = [{"reference": "PR17", "identity": "x",
                                    "ownership": "unresolved", "affects_boundary": True}]
        result = topology.choose(source)
        self.assertEqual(result["status"], "BLOCKED")

    def test_supersession_requires_exact_approval_grants_and_readback(self):
        result = topology.choose(sample())
        origin = issue()
        children = replacements(result)
        preview = topology.supersession_preview(result, origin, children)
        self.assertEqual(preview["close_reason"], "not_planned")
        self.assertIn("not delivered", preview["comment"])
        no_authority = autonomy.local("Perform tracker work")
        with self.assertRaisesRegex(ValueError, "outside"):
            topology.authorize_supersession(preview, no_authority,
                {"preview_sha256": preview["sha256"], "source": "Separate request"}, origin, children)
        grant = autonomy.local("Close origin as superseded")
        grant["policy"]["effects"] = [
            {"action": action, "repository": "grove/project", "destination": "#10"}
            for action in ("issue-comment", "issue-close")]
        authorization = topology.authorize_supersession(preview, grant,
            {"preview_sha256": preview["sha256"], "source": "Explicit tracker approval"}, origin, children)
        self.assertEqual(authorization["status"], "AUTHORIZED_NOT_EXECUTED")
        self.assertEqual(topology.supersession_readback(preview, origin, [])["status"], "PARTIAL")
        saved = origin | {"state": "closed", "state_reason": "not_planned"}
        comment = {"body": preview["comment"], "url": "https://github.com/grove/project/issues/10#issuecomment-1"}
        self.assertEqual(topology.supersession_readback(preview, saved, [comment])["status"], "SUPERSEDED")
        self.assertEqual(topology.supersession_readback(preview, saved | {"state_reason": "completed"},
                                                    [comment])["status"], "PARTIAL")
        self.assertEqual(topology.supersession_readback(preview, saved, [comment, comment])["status"], "PARTIAL")
        modified = copy.deepcopy(children)
        modified[0]["body"] += " concurrent human edit"
        with self.assertRaisesRegex(ValueError, "human edits changed"):
            topology.authorize_supersession(preview, grant,
                {"preview_sha256": preview["sha256"], "source": "Explicit tracker approval"},
                origin, modified)

    def test_supersession_rejects_wrong_order_missing_markers_and_reconciliation(self):
        decision = topology.choose(sample())
        children = replacements(decision)
        with self.assertRaises(ValueError):
            topology.supersession_preview(decision, issue(), children[::-1])
        children[1]["body"] = "No binding source"
        with self.assertRaises(ValueError):
            topology.supersession_preview(decision, issue(), children)
        source = sample()
        source["existing_shape"] = "parent-tree"
        with self.assertRaisesRegex(ValueError, "reconciled"):
            topology.supersession_preview(topology.choose(source), issue(), replacements(decision))


if __name__ == "__main__":
    unittest.main()
