"""Offline #71 continuity cases, including late PR identity and missing origin."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "skills/productivity/deliver-issue/scripts"))
import p2p_continuity as c
import p2p_issue_topology as t


def scenario(parent=False):
    return {
        "origin": {"reference": "grove/pg-react#8", "contract": ".p2p/work/react/contract.md",
                   "revision": "v1", "sha256": "a"*64,
                   "promise": "Deliver complete pg-react behavior.", "obligations": ["R1","R2"]},
        "sizing": {"decision": "SPLIT", "identity": "b"*64, "evidence": "retained #77 sizing",
                   "reason": "one prerequisite establishes the required integration seam"},
        "factors": {"naturally_sequential": not parent, "parallel_ownership": parent,
                    "long_lived_aggregate": False, "independent_parent_integration": False,
                    "reason": "Existing concrete seam requires separable implementation."},
        "units": [
            {"id":"S1","outcome":"prerequisite integration","contributes":["R1"],
             "blocked_by":[],"status":"active"},
            {"id":"S2","outcome":"complete original behavior","contributes":["R2"],
             "blocked_by":["S1"],"status":"pending"}],
        "order":["S1","S2"],
        "existing_work":[{"reference":"https://github.com/trickle-labs/pg-react/pull/9",
                          "identity":"c"*64,"ownership":"S1","affects_boundary":True}],
        "existing_shape":None}


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.decision=t.choose(scenario())
        self.refs={"S1":{"work_item":".p2p/work/react-prereq/contract.md",
                         "issue":"https://github.com/grove/pg-react/issues/9"},
                   "S2":{"work_item":".p2p/work/react-final/contract.md",
                         "issue":"https://github.com/grove/pg-react/issues/10"}}
        self.record=c.project(self.decision,self.refs)

    def test_prerequisite_keeps_original_and_final_owner(self):
        status=c.view(self.record,self.decision,"S1")
        self.assertEqual(status["origin"],"grove/pg-react#8")
        self.assertFalse(status["complete_original_promise"])
        self.assertEqual(status["final_acceptance_owner"],"S2")
        self.assertIn("R2",status["remaining_obligations"])
        self.assertIn("issues/10",status["next_action"])

    def test_tree_keeps_parent_owner_and_unaffected_obligations(self):
        decision=t.choose(scenario(parent=True))
        record=c.project(decision,self.refs)
        status=c.view(record,decision,"S1")
        self.assertEqual(status["final_acceptance_owner"],"grove/pg-react#8")
        self.assertIn("R2",status["remaining_obligations"])

    def test_late_reconciliation_does_not_modify_pr_or_reports(self):
        self.assertEqual(self.record["existing_work"][0]["identity"],"c"*64)
        self.assertEqual(self.record["existing_work"][0]["reference"],
                         "https://github.com/trickle-labs/pg-react/pull/9")

    def test_exact_pointer_checkpoint_roundtrip(self):
        import p2p_filesystem as fs
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/".p2p/work/react").mkdir(parents=True)
            (root/".p2p/work/react-prereq").mkdir(parents=True)
            (root/".p2p/work/react-prereq/contract.md").write_text("# accepted")
            doc={"topology":self.decision,"continuity":self.record}
            canonical=json.dumps(doc,sort_keys=True,separators=(",",":"),ensure_ascii=False)
            origin=f".p2p/work/react/slicing.md"
            pointer=f".p2p/work/react-prereq/continuity.json"
            raw=("## Sizing\n<!-- p2p-continuity-v1\n"+canonical+"\n-->\n").encode()
            (root/origin).write_bytes(raw)
            (root/pointer).write_text(json.dumps({"origin":".p2p/work/react/contract.md",
                "unit":"S1","topology_identity":self.decision["identity"],
                "record_sha256":t.digest(doc)}))
            self.assertEqual(c.load(root,self.refs["S1"]["work_item"])["unit"],"S1")
            files=[("project",origin,raw),("project",pointer,(root/pointer).read_bytes())]
            self.assertEqual(c.load(root,self.refs["S1"]["work_item"],
                                    checkpoint_files=files)["origin"],"grove/pg-react#8")
            (root/origin).write_text("tampered")
            with self.assertRaisesRegex(ValueError,"continuity"):
                c.load(root,self.refs["S1"]["work_item"])
            self.assertEqual(c.load(root,self.refs["S1"]["work_item"],checkpoint_files=files)["unit"],"S1")

    def test_pr_cannot_close_original_unfulfilled_issue(self):
        status=c.view(self.record,self.decision,"S1")
        with self.assertRaisesRegex(ValueError,"unfinished originating"):
            c.publication_guard(status,"Fixes #8\n")
        with self.assertRaisesRegex(ValueError,"unfinished originating"):
            c.publication_guard(status,"Closes grove/pg-react#8")
        self.assertEqual(c.publication_guard(status,"Implements prerequisite.\n"),
                         "Implements prerequisite.\n")

    def test_persist_retains_slicing_and_pointers_without_tracker_effects(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            subprocess.run(["git","init","-q",str(root)],check=True)
            (root/".gitignore").write_text("/.p2p/\\n")
            for slug in ("react","react-prereq","react-final"):
                folder=root/".p2p/work"/slug
                folder.mkdir(parents=True)
                (folder/"contract.md").write_text("# Accepted contract\\n")
            parent=root/".p2p/work/react/slicing.md"
            original=b"## Approved delivery plan\\nPlan revision: v1\\n"
            parent.write_bytes(original)
            saved=c.persist(root,".p2p/work/react/contract.md",self.decision,self.refs)
            self.assertEqual(saved["status"],"PRESERVED")
            self.assertEqual(saved["tracker_effects"],0)
            self.assertTrue(parent.read_bytes().startswith(original))
            again=c.persist(root,".p2p/work/react/contract.md",self.decision,self.refs)
            self.assertEqual(saved,again)
            self.assertEqual(c.load(root,self.refs["S2"]["work_item"])["final_acceptance_owner"],"S2")
            self.assertEqual(len(list((root/".p2p/work/react/history").glob("*/slicing.md"))),1)

    def test_changed_topology_refuses_stale_continuity(self):
        altered=dict(self.decision,identity="x"*64)
        with self.assertRaisesRegex(ValueError,"stale"):
            c.view(self.record,altered,"S1")
        with self.assertRaises(ValueError):
            c.project(altered,self.refs)

if __name__=="__main__":
    unittest.main()
