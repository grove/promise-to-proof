"""Exact requirement/scope regressions (offline; not a model judgment)."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_p2p_delivery import d, repo, fixture_host, FakeTransport


class CoverageFactsTests(unittest.TestCase):
    def setUp(self):
        self.base = [{"path": "app.py", "type": "file", "mode": "100644",
                      "content_base64": "cHJpbnQoMSkK"}]
        self.current = [dict(self.base[0], content_base64="cHJpbnQoMikK")]
        self.changes = d.fs.tree_changes(self.base, self.current)
        self.report = {"status": "REVIEWED",
                       "requirements": [{"id": "R1", "observation": "Inspected public app behavior"}],
                       "checks": [{"command": "python3 app.py", "result": "passed",
                                   "observation": "2"}],
                       "limitations": []}

    def trace(self, **kwargs):
        return {"requirements": [{"id": "R1", "paths": ["app.py"],
                                  "existing": False, "evidence": ["row", "check:0"]}],
                "supporting_changes": [], "inspected_paths": ["app.py"]} | kwargs

    def test_valid_trace_binds_real_file_and_retrievable_report_evidence(self):
        self.assertEqual(d.fs.validate_coverage_trace(self.trace(), ["R1"], self.report,
                                                        "review", self.current, self.changes)["unaccounted_changes"], [])
        record = "record:E1@sha256:" + "a" * 64
        valid = self.trace(requirements=[{"id": "R1", "paths": ["app.py"],
                                          "existing": False, "evidence": ["row", record]}])
        with self.assertRaisesRegex(ValueError, "unresolved"):
            d.fs.validate_coverage_trace(valid, ["R1"], self.report, "review",
                                         self.current, self.changes)
        self.assertEqual(d.fs.validate_coverage_trace(valid, ["R1"], self.report,
                                                        "review", self.current, self.changes,
                                                        {record})["requirements"], ["R1"])

    def test_missing_obligation_and_unaccounted_changes_fail(self):
        invalid = self.trace(requirements=[])
        with self.assertRaisesRegex(ValueError, "omits or duplicates"):
            d.fs.validate_coverage_trace(invalid, ["R1"], self.report,
                                         "review", self.current, self.changes)
        invalid = self.trace(requirements=[{"id": "R1", "paths": [], "existing": True,
                                            "evidence": ["row"]}])
        with self.assertRaisesRegex(ValueError, "unaccounted product changes"):
            d.fs.validate_coverage_trace(invalid, ["R1"], self.report,
                                         "review", self.current, self.changes)
        valid = invalid | {"supporting_changes": [
            {"path": "app.py", "reason": "Required supporting change for an unchanged behavior"}]}
        self.assertEqual(d.fs.validate_coverage_trace(valid, ["R1"], self.report,
                                                        "review", self.current, self.changes)["supporting_changes"], ["app.py"])

    def test_absent_paths_invented_evidence_and_undisclosed_inspection_fail(self):
        variants = [
            (self.trace(requirements=[{"id": "R1", "paths": ["untracked.py"],
                                       "existing": False, "evidence": ["row"]}]), "absent"),
            (self.trace(requirements=[{"id": "R1", "paths": ["app.py"],
                                       "existing": False, "evidence": ["record:E1@sha256:bad"]}]), "unresolved"),
            (self.trace(inspected_paths=[]), "not inspected"),
            (self.trace(inspected_paths=["made-up.py"]), "absent"),
            (self.trace(requirements=[{"id": "R1", "paths": ["app.py"],
                                       "existing": False, "evidence": ["check:8"]}]), "missing review check"),
        ]
        for candidate, reason in variants:
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, reason):
                d.fs.validate_coverage_trace(candidate, ["R1"], self.report,
                                             "review", self.current, self.changes)

    def test_existing_behavior_requires_no_artificial_diff(self):
        trace = {"requirements": [{"id": "R1", "paths": ["app.py"], "existing": True,
                                   "evidence": ["row"]}], "supporting_changes": [],
                 "inspected_paths": ["app.py"]}
        self.assertEqual(d.fs.validate_coverage_trace(trace, ["R1"], self.report,
                                                        "review", self.base, [])["unaccounted_changes"], [])

    def test_exact_scope_records_content_and_detects_generated_regressions(self):
        candidate = {"key": d.fs.snapshot_key(self.current),
                     "work_item_sha256": "1" * 64,
                     "comparison_base": "a" * 40,
                     "changes": self.changes}
        scope = d.fs.review_scope(candidate, self.current, "b" * 40, ["app.py"], trace=self.trace())
        self.assertEqual(scope["inspected"][0]["sha256"], d.fs.digest(b"print(2)\n"))
        unchanged = d.fs.compare_review_scope(scope, self.current, self.current)
        self.assertEqual(unchanged["status"], "COVERED")
        new = self.current + [{"path": "generated/test_app.py", "type": "file", "mode": "100644",
                               "content_base64": "YXNzZXJ0IFRydWUK"}]
        drift = d.fs.compare_review_scope(scope, self.current, new)
        self.assertEqual(drift["status"], "UNCOVERED_DELTA")
        self.assertEqual(drift["uncovered_changes"][0]["path"], "generated/test_app.py")
        records_only = self.current  # Generated P2P state is excluded by the snapshot.
        self.assertEqual(d.fs.compare_review_scope(scope, self.current, records_only)["status"], "COVERED")
        self.assertEqual(d.fs.compare_review_scope(None, self.current, self.current)["status"], "UNKNOWN")
        wrong = dict(scope, manifest_sha256="f" * 64)
        self.assertEqual(d.fs.compare_review_scope(wrong, self.current, self.current)["status"], "UNKNOWN")

    def test_only_actual_retained_record_identities_can_be_referenced(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            folder = workspace / ".p2p/work/tiny/evidence"
            folder.mkdir(parents=True)
            identity = d.fs.snapshot_key(self.current)
            record = {"schema": "promise-to-proof/evidence-record/v1",
                      "id": "E1", "candidate": identity,
                      "contract": {"sha256": "b" * 64}}
            path = folder / "E1.json"
            path.write_text(json.dumps(record))
            ref = "record:E1@sha256:" + d.fs.digest(d.fs.canonical(record))
            self.assertEqual(d.fs.available_evidence_refs(
                workspace, ".p2p/work/tiny/contract.md", identity, "b" * 64), {ref})
            self.assertFalse(d.fs.available_evidence_refs(
                workspace, ".p2p/work/tiny/contract.md", identity, "c" * 64))
            path.write_text(json.dumps(dict(record, candidate="snapshot:sha256:" + "0" * 64)))
            self.assertFalse(d.fs.available_evidence_refs(
                workspace, ".p2p/work/tiny/contract.md", identity, "b" * 64))

    def test_review_scope_rejects_fabricated_file_inspection(self):
        candidate = {"key": d.fs.snapshot_key(self.current), "work_item_sha256": "1" * 64,
                     "comparison_base": "a" * 40, "changes": self.changes}
        with self.assertRaisesRegex(ValueError, "absent"):
            d.fs.review_scope(candidate, self.current, "b" * 40, ["missing.py"])


class DeliveryCoverageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = patch.dict(os.environ, {"HOME": self.temp.name})
        self.home.start()
        self.root = Path(self.temp.name) / "source"
        self.base = repo(self.root)
        self.transport = FakeTransport()
        self.launch = patch.object(d, "launch", self.transport)
        self.launch.start()
        self.host = fixture_host()
        self.host.__enter__()
        self.work = ".p2p/work/tiny/contract.md"

    def tearDown(self):
        self.host.__exit__(None, None, None)
        self.launch.stop()
        self.home.stop()
        self.temp.cleanup()

    def test_exact_coverage_is_retained_in_reports_and_durable_completion_record(self):
        args = ["--repo", str(self.root), "run", self.work, "--comparison-base",
                self.base, "--authorize-local", "--destination", "delivery-target"]
        result = io.StringIO()
        with contextlib.redirect_stdout(result):
            self.assertEqual(d.main(args), 0, result.getvalue())
        current = json.loads(result.getvalue())
        self.assertEqual(current["status"], "REVIEWED_AND_PROVEN")
        local = d.local_directory(self.root, self.work)
        state = json.loads((local / "delivery.json").read_text())
        self.assertEqual(state["coverage_format_version"], 1)
        self.assertEqual(state["reports"]["review"]["review_scope"]["candidate_key"],
                         state["candidate"]["key"])
        for name in ("implementation", "review", "proof"):
            self.assertIn("coverage_trace_sha256", state["reports"][name])
        delivery = d.Delivery(self.root, self.work, state)
        record = delivery.final_record()
        self.assertEqual(record["review_scope"]["candidate_key"], state["candidate"]["key"])
        self.assertEqual(set(record["coverage_trace_sha256"]), {"implementation", "review", "proof"})
        same = d.fs.review_scope_status(self.root, self.work, delivery.workspace)
        self.assertEqual(same["status"], "COVERED")
        before = d.fs.review_scope_status(self.root, self.work, self.root)
        self.assertEqual(before["status"], "UNCOVERED_DELTA")
        self.assertEqual(before["uncovered_changes"][0]["path"], "greet.py")
        (self.root / ".p2p/work/tiny/local-note.txt").write_text("records only")
        self.assertEqual(d.fs.review_scope_status(self.root, self.work, delivery.workspace)["status"], "COVERED")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(d.main(["--repo", str(self.root), "cleanup", self.work]), 0, output.getvalue())
        saved = json.loads((self.root / ".p2p/work/tiny/artifacts/delivery.json").read_text())
        self.assertEqual(saved["review_scope"]["candidate_key"], state["candidate"]["key"])
        self.assertEqual(set(saved["coverage_trace_sha256"]), {"implementation", "review", "proof"})
        self.assertEqual(d.fs.review_scope_status(self.root, self.work, delivery.workspace)["status"], "COVERED")

    def test_old_unscoped_delivery_reports_unknown_without_guessing(self):
        result = d.fs.review_scope_status(self.root, self.work)
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertIn("no saved review", result["reason"])


if __name__ == "__main__":
    unittest.main()
