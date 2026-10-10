"""Risk-driven verification facts and destination checks (offline, no model judgments)."""
import base64
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from test_p2p_delivery import d, repo, FakeTransport, fixture_host, apply_candidate


def blob(name, text):
    return {"path": name, "type": "file", "mode": "100644",
            "content_base64": base64.b64encode(text.encode()).decode()}


class RiskTraceTests(unittest.TestCase):
    def setUp(self):
        self.base = [blob("booking.py", "def reserve(): pass\n"),
                     blob("cli.py", "from booking import reserve\n")]
        self.current = [blob("booking.py", "def reserve(): return True\n"),
                        self.base[1]]
        self.changed = d.fs.tree_changes(self.base, self.current)
        self.report = {
            "status": "REVIEWED", "requirements": [
                {"id": "R1", "observation": "Read the booking CLI"},
                {"id": "R2", "observation": "Inspected the persistent store"}],
            "checks": [{"command": "python3 -m unittest tests.test_booking",
                        "result": "passed", "observation": "restart and one-winner assertions passed"}],
            "limitations": []}
        self.risk = {"id": "S1", "requirements": ["R2"],
                     "paths": ["booking.py", "cli.py"], "reach": "bounded",
                     "trigger": "two clients contend for the same seat",
                     "why_applicable": "booking has a shared database slot",
                     "consequence": "oversell to multiple users",
                     "evidence": ["check:0"], "status": "addressed"}
        self.trace = {
            "requirements": [{"id": "R1", "paths": ["cli.py"], "existing": True,
                              "evidence": ["row"]},
                             {"id": "R2", "paths": ["booking.py"], "existing": False,
                              "evidence": ["row", "check:0"]}],
            "supporting_changes": [],
            "inspected_paths": ["booking.py", "cli.py"],
            "risks": [self.risk],
        }

    def validate(self, trace=None, report=None):
        return d.fs.validate_coverage_trace(
            trace if trace is not None else self.trace,
            ["R1", "R2"], report if report is not None else self.report,
            "review", self.current, self.changed, risks=True)

    def test_high_risk_anchors_real_trigger_seam_and_check(self):
        self.assertEqual(self.validate()["risks"], ["S1"])
        scope = d.fs.review_scope(
            {"key": d.fs.snapshot_key(self.current),
             "work_item_sha256": "a"*64, "comparison_base": "b"*40,
             "changes": self.changed}, self.current, "c"*40,
            ["booking.py", "cli.py"], trace=self.trace, checks=self.report["checks"])
        self.assertEqual(scope["seam_dependencies"]["risks"][0]["check_commands"],
                         ["python3 -m unittest tests.test_booking"])
        self.assertEqual(d.fs.compare_review_scope(scope, self.current, self.current)["status"],
                         "COVERED")
        self.assertEqual(scope["seam_dependencies"]["paths"], ["booking.py", "cli.py"])

    def test_low_risk_control_has_no_mandatory_extra_check(self):
        low = dict(self.trace, risks=[])
        self.assertEqual(self.validate(low)["risks"], [])
        schema = d.report_schema("review", coverage=True, risks=True)
        self.assertIn("risks", schema["properties"]["coverage_trace"]["required"])
        self.assertNotIn("risks", d.report_schema("review", coverage=True, risks=False)
                         ["properties"]["coverage_trace"]["required"])

    def test_material_unresolved_risk_cannot_be_marked_reviewed(self):
        blocked = dict(self.trace, risks=[dict(self.risk, status="unresolved", evidence=[])])
        with self.assertRaisesRegex(ValueError, "unaddressed material risk"):
            self.validate(blocked)
        finding = dict(self.report, status="CHANGES NEEDED")
        self.assertEqual(self.validate(blocked, finding)["risks"], ["S1"])

    def test_weak_or_invented_risk_evidence_does_not_pass(self):
        for item, error in [
            (dict(self.risk, evidence=["check:9"]), "nonexistent"),
            (dict(self.risk, paths=["invented.py"]), "real paths"),
            (dict(self.risk, why_applicable=" "), "realistic trigger"),
            (dict(self.risk, trigger=" "), "realistic trigger"),
            (dict(self.risk, evidence=["file:booking.py"]), "observation or check"),
            (dict(self.risk, id="S0"), "invalid or duplicate"),
        ]:
            with self.subTest(error=error, item=item), self.assertRaisesRegex(ValueError, error):
                self.validate(dict(self.trace, risks=[item]))
        failed_check = dict(self.report, checks=[dict(self.report["checks"][0], result="failed")])
        with self.assertRaisesRegex(ValueError, "failed or unavailable"):
            self.validate(report=failed_check)

    def test_unrelated_target_movement_is_not_a_new_check_quota(self):
        base = self.base
        unrelated = base + [blob("docs/readme.md", "Unrelated notes\n")]
        scope = d.fs.review_scope(
            {"key": d.fs.snapshot_key(self.current),
             "work_item_sha256": "a"*64, "comparison_base": "b"*40,
             "changes": self.changed}, self.current, "c"*40,
            ["booking.py", "cli.py"], trace=self.trace, checks=self.report["checks"])
        self.assertEqual(d.fs.assess_target_risks(scope, base, unrelated)["status"],
                         "NO_ADDITIONAL_RISK_CHECKS")
        changed_booking = [blob("booking.py", "def reserve(): raise RuntimeError()\n"),
                           self.base[1]]
        affected = d.fs.assess_target_risks(scope, base, changed_booking)
        self.assertEqual(affected["status"], "TARGETED_CHECKS_REQUIRED")
        self.assertEqual(affected["affected_risks"][0]["id"], "S1")
        self.assertEqual(affected["affected_risks"][0]["touched_paths"], ["booking.py"])
        self.assertIn("NOT", affected["boundary"].upper() or "NOT")
        broad = dict(scope, seam_dependencies={
            "paths": scope["seam_dependencies"]["paths"],
            "risks": [dict(scope["seam_dependencies"]["risks"][0],
                           reach="uncertain")],
        })
        self.assertEqual(d.fs.assess_target_risks(broad, base, unrelated)["status"],
                         "TARGETED_CHECKS_REQUIRED")
        historical = dict(scope)
        historical.pop("seam_dependencies")
        self.assertEqual(d.fs.assess_target_risks(historical, base, unrelated)["status"], "UNKNOWN")


class TargetRiskCommandTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="p2p-risk-command-")
        self.home = patch.dict(os.environ, {"HOME": self.temp.name})
        self.home.start()
        self.root = Path(self.temp.name) / "source"
        self.base = repo(self.root)
        self.fake = FakeTransport()
        self.launch = patch.object(d, "launch", self.fake)
        self.launch.start()
        self.host = fixture_host()
        self.host.__enter__()
        self.work = ".p2p/work/tiny/contract.md"

    def tearDown(self):
        self.host.__exit__(None, None, None)
        self.launch.stop()
        self.home.stop()
        self.temp.cleanup()

    def test_exact_pair_requires_no_extra_check_for_unrelated_movement(self):
        args = ["--repo", str(self.root), "run", self.work, "--comparison-base",
                self.base, "--authorize-local", "--destination", "delivery-target"]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(d.main(args), 0, output.getvalue())
        state = json.loads((d.local_directory(self.root, self.work)/"delivery.json").read_text())
        self.assertEqual(state["coverage_format_version"], 2)
        self.assertEqual(state["reports"]["review"]["review_scope"]["seam_dependencies"]["risks"], [])
        self.assertEqual([a["stage"] for a in state["attempts"]][-3:],
                         ["implementation", "review", "proof"])
        apply_candidate(self.root, d.execution_runtime(self.root, self.work) / "workspace")
        d.fs.git(self.root, "add", "greet.py")
        d.fs.git(self.root, "commit", "-qm", "exact candidate")
        head = d.fs.full_commit(self.root, "HEAD")
        self.assertEqual(d.fs.target_risk_status(self.root, self.work, self.base, head)["status"],
                         "NO_ADDITIONAL_RISK_CHECKS")
        target = Path(self.temp.name) / "target"
        subprocess.run(["git", "-C", str(self.root), "worktree", "add", "-b",
                        "target-test", str(target), self.base], check=True, capture_output=True)
        (target / "docs.txt").write_text("Only unrelated documentation changed\n")
        d.fs.git(target, "add", "docs.txt")
        d.fs.git(target, "commit", "-qm", "unrelated fast-forward")
        target_tip = d.fs.full_commit(target, "HEAD")
        unrelated = d.fs.target_risk_status(self.root, self.work, target_tip, head)
        self.assertEqual(unrelated["status"], "NO_ADDITIONAL_RISK_CHECKS")
        self.assertEqual(unrelated["compatibility_status"], "NOT ASSESSED")
        (target / "greet.py").write_text("print('different greeting')\n")
        d.fs.git(target, "add", "greet.py")
        d.fs.git(target, "commit", "-qm", "touch reviewed seam")
        touched = d.fs.full_commit(target, "HEAD")
        self.assertEqual(d.fs.target_risk_status(self.root, self.work, touched, head)["status"],
                         "TARGETED_CHECKS_REQUIRED")
        stale = d.fs.target_risk_status(self.root, self.work, touched, self.base)
        self.assertEqual(stale["status"], "UNKNOWN")
        self.assertIn("PR head", stale["reason"])

    def test_nonexistent_scope_or_nonexact_inputs_never_pass(self):
        self.assertEqual(d.fs.target_risk_status(self.root, self.work,
                                                 self.base, self.base)["status"], "UNKNOWN")
        with self.assertRaisesRegex(ValueError, "exact full"):
            d.fs.target_risk_status(self.root, self.work, "main", self.base)


if __name__ == "__main__":
    unittest.main()
