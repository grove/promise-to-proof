"""Combined #44/#41/#42/#43 gate regressions: offline harness, not live model evidence."""
import contextlib
import io
import json
import os
from pathlib import Path
import re
import tempfile
import unittest
import uuid
from unittest.mock import patch

import check_p2p_quality_integration as integrated
import check_p2p_judgments_host as judgments
from test_live_judgments import OfflineJudgmentTransport
from test_p2p_delivery import d, fixture_host, FakeTransport, repo


class IntegratedQualityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="p2p-quality-integration-offline-")
        self.root = Path(self.temp.name)
        self.home = patch.dict(os.environ, {
            "HOME": str(self.root),
            "P2P_EXECUTION_ROOT": str(self.root / "executions"),
        })
        self.home.start()
        self.selected, self.fixtures, self.selection_sha, self.fixture_sha = integrated.selection()
        self.cases = {case["id"]: case for case in self.fixtures["cases"]}

    def tearDown(self):
        self.home.stop()
        self.temp.cleanup()

    def test_fixture_set_is_small_and_the_same_contracts_have_fixed_outcomes(self):
        self.assertEqual(len(self.selected["cases"]), 6)
        self.assertEqual({case["expected"] for case in self.selected["audit"]},
                         {"READY_FOR_APPROVAL", "BLOCKED"})
        self.assertIn("review-reconcile-corrected-finding", self.selected["cases"])
        self.assertIn("verification-durable-control", self.selected["cases"])
        self.assertIn("review-overmocked-boundary", self.selected["cases"])
        self.assertIn("green-but-incomplete", self.selected["cases"])
        self.assertIn("unrelated-scope-expansion", self.selected["cases"])
        self.assertIn("review-meaningful-tests", self.selected["cases"])
        self.assertEqual(self.cases["green-but-incomplete"]["contract"],
                         self.cases["review-meaningful-tests"]["contract"]
                         if "contract" in self.cases["review-meaningful-tests"]
                         else self.fixtures["contract"])
        self.assertEqual(len(self.selected["cases"]), len(set(self.selected["cases"])))
        self.assertTrue(self.selected["optional_advice"].startswith("\nOptional"))
        _, ids = d.parse_contract(self.fixtures["contract"].encode())
        self.assertEqual(set(ids), {"R1", "R2", "R3"})

    def test_source_audit_detects_conflict_and_never_makes_approval(self):
        source = self.fixtures["base_files"]["spec.md"]
        good = self.selected["audit"][0]
        bad = self.selected["audit"][1]
        complete = {"source_sha256": "a"*64, "contract_sha256": "b"*64,
                    "comparison_base": "c"*40, "proposal": judgments.WORK}
        def decision(status, conflicts):
            return {"status": status, "input_identity_json": json.dumps(complete),
                    "coverage": "R1-R3 matched or identified in source",
                    "reason": "A source requirement needs a material decision" if conflicts
                              else "Proposed contract preserves all source promises",
                    "conflicts": conflicts}
        conflict = {"first_source_excerpt": source.strip(),
                    "second_source_excerpt": bad["spec_suffix"].strip(),
                    "consequence": "R2 could be both accepted and rejected",
                    "needed_decision": "Choose whether whitespace-only names are valid"}
        self.assertEqual(integrated.assess_audit(decision("READY_FOR_APPROVAL", []),
                                                  good["expected"], complete, source), [])
        self.assertEqual(integrated.assess_audit(decision("BLOCKED", [conflict]),
                                                  bad["expected"], complete,
                                                  source + bad["spec_suffix"]), [])
        self.assertTrue(integrated.assess_audit(decision("READY_FOR_APPROVAL", []),
                                                 bad["expected"], complete,
                                                 source + bad["spec_suffix"]))
        self.assertTrue(integrated.assess_audit(decision("BLOCKED", [conflict]),
                                                 bad["expected"], complete, source))
        tampered = decision("BLOCKED", [conflict])
        tampered["input_identity_json"] = "{}"
        self.assertTrue(integrated.assess_audit(tampered, bad["expected"], complete,
                                                 source + bad["spec_suffix"]))

    def test_audit_uses_real_stage_transport_shape_and_preserves_source(self):
        # These two JSON messages are FIXTURE data only. Real audit competence
        # requires an authorized macOS/Codex host run, never this offline mock.
        launch_prompts = []
        def transport(args, prompt, event_path, error_path, deadline):
            identity = json.loads(re.search(
                r"Exact input_identity_json must encode: (\{.*\})\.$", prompt).group(1))
            source = (event_path.parent / "source/spec.md").read_text()
            contradiction = "is valid" in source
            report = {"status": "BLOCKED" if contradiction else "READY_FOR_APPROVAL",
                      "input_identity_json": json.dumps(identity),
                      "coverage": "FIXTURE: observed R1, R2, R3",
                      "reason": "FIXTURE: conflicting source promises" if contradiction
                                else "FIXTURE: all planned examples agree",
                      "conflicts": [{
                          "first_source_excerpt": source.splitlines()[0],
                          "second_source_excerpt": source.strip().splitlines()[-1],
                          "consequence": "The same R2 input has contradictory outputs",
                          "needed_decision": "Choose which whitespace outcome is intended",
                      }] if contradiction else []}
            launch_prompts.append(prompt)
            events = [
                {"type": "thread.started", "thread_id": uuid.uuid4().hex},
                {"type": "item.completed", "item": {
                    "type": "command_execution", "command": "FIXTURE cat spec.md",
                    "aggregated_output": "Fixture inspection only", "exit_code": 0}},
                {"type": "item.completed", "item": {
                    "type": "agent_message", "text": json.dumps(report)}},
                {"type": "turn.completed", "usage": {"input_tokens": 1, "output_tokens": 1}},
            ]
            event_path.write_text("".join(json.dumps(event) + "\n" for event in events))
            error_path.write_text("FIXTURE; no model invoked\n")
            return {"exit_code": 0, "outcome": "finished",
                    "finished": d.now(), "elapsed_seconds": 0.01}
        output = self.root / "audit-fixtures"
        output.mkdir()
        with patch.object(integrated.d, "launch", side_effect=transport):
            audits = [integrated.audit_one(
                output, fixture, self.fixtures, "/fixture/codex",
                {"path": "/fixture/audit-acceptance/SKILL.md", "sha256": "a"*64},
                30, number)
                for number, fixture in enumerate(self.selected["audit"], 1)]
        self.assertEqual([x["observed"] for x in audits],
                         ["READY_FOR_APPROVAL", "BLOCKED"])
        self.assertTrue(all(x["passed"] for x in audits), audits)
        self.assertEqual(len(launch_prompts), 2)
        self.assertTrue(all("expected" not in prompt.lower()
                            for prompt in launch_prompts))
        self.assertNotIn("implementation", [a["id"] for a in audits])
        self.assertTrue(all(Path(a["receipt"]).is_file() and Path(a["report"]).is_file()
                            for a in audits))

    def test_cross_stage_fixed_good_bad_and_repair_bind_exact_candidate(self):
        output = self.root / "candidate-fixtures"
        output.mkdir()
        fixture_transport = OfflineJudgmentTransport()

        def fake_launch(*args, **kwargs):
            # Respond from inspected candidate source, not fixture expectation.
            prompt = args[1]
            workspace = Path(prompt.split("workspace ", 1)[1].split(". ", 1)[0])
            actual = (workspace / "username.py").read_text()
            fixture_transport.bad = 'if value == ""' in actual
            return fixture_transport(*args, **kwargs)

        cases = [
            self.cases["review-meaningful-tests"],
            self.cases["green-but-incomplete"],
            self.cases["review-reconcile-corrected-finding"],
        ]
        with fixture_host(), patch.object(d, "launch", side_effect=fake_launch):
            summaries = []
            for i, case in enumerate(cases, 1):
                result = judgments.run_case(output, self.fixtures, case,
                                            self.fixture_sha, 120, i)
                errors = integrated.assess_case(result, case,
                                                case.get("contract", self.fixtures["contract"]))
                self.assertEqual(errors, [], (case["id"], errors, result.get("error")))
                summaries.append(integrated.compact_case(result, case, errors))
        self.assertTrue(all(x["passed"] for x in summaries))
        self.assertEqual([len(x["candidates"]) for x in summaries], [1, 1, 2])
        self.assertEqual([c["observed"]["proof"] for s in summaries for c in s["candidates"]],
                         ["PROVEN", "NOT PROVEN", "NOT PROVEN", "PROVEN"])
        self.assertEqual(len(fixture_transport.prompts), 8)
        with patch.object(integrated, "SELECTION", self.root / "selection.json"):
            (self.root / "selection.json").write_text(json.dumps(
                {"cases": [s["fixture"] for s in summaries],
                 "audit": self.selected["audit"]}))
            incomplete = integrated.integrate(
                output, {"cases": [s["fixture"] for s in summaries],
                         "audit": self.selected["audit"]},
                [{"id": a["id"], "passed": True, "issues": []}
                 for a in self.selected["audit"]],
                summaries, live_evidence=False)
        self.assertEqual(incomplete["status"], "FAIL")
        self.assertFalse(incomplete["live_host_evidence"])

    def test_corrupt_scope_and_stale_proof_cannot_pass_integration(self):
        example = {"passed": True, "source_base": "f"*40, "contract_sha256": "a"*64,
                   "runtime": "/missing", "candidates": [{
                       "name": "fixed", "candidate": {"key": "snapshot:sha256:" + "b"*64,
                                                       "comparison_base": "f"*40},
                       "generation": {"candidate_key": "snapshot:sha256:"+"b"*64,
                                      "commit": "c"*40},
                       "stage_attempts": [], "observed": {"review": {}, "proof": {}},
                       "review_scope": {"candidate_key": "snapshot:sha256:"+"b"*64},
                       "oracle": {"passed": True}, "guard_sensitivity": {"passed": True}
                   }]}
        issues = integrated.assess_case(example, self.cases["review-meaningful-tests"],
                                       self.fixtures["contract"])
        self.assertTrue(any("Git object" in x for x in issues))
        self.assertTrue(any("scope" in x for x in issues))
        self.assertTrue(any("verifier dispatch" in x for x in issues))

    def test_representative_normal_controller_completes_without_extra_quality_stage(self):
        # The fixed-candidate runner is not an implementation worker. This
        # exercises the ordinary complete delivery path with its own offline
        # fake transport, checking stage ownership and terminal records.
        root = self.root / "ordinary"
        base = repo(root)
        fake = FakeTransport()
        work = ".p2p/work/tiny/contract.md"
        args = ["--repo", str(root), "run", work, "--comparison-base", base,
                "--authorize-local", "--destination", "delivery-target"]
        with fixture_host(), patch.object(d, "launch", fake):
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = d.main(args)
            value = json.loads(stream.getvalue())
            self.assertEqual(code, 0, value.get("blocker"))
            self.assertEqual(value["status"], "REVIEWED_AND_PROVEN")
            stages = [a["stage"] for a in value["attempts"]]
            self.assertEqual(stages, ["preflight-1", "preflight-2",
                                      "implementation", "review", "proof"])
            self.assertEqual(fake.calls, ["preflight", "preflight",
                                          "implementation", "review", "proof"])
            state = json.loads((d.local_directory(root, work)/"delivery.json").read_text())
            self.assertEqual(state["coverage_format_version"], 2)
            self.assertEqual(state["reports"]["review"]["review_scope"]["candidate_key"],
                             state["candidate"]["key"])
            self.assertEqual(state["reports"]["review"]["review_scope"]
                             ["seam_dependencies"]["risks"], [])
            self.assertEqual(state["reports"]["review"]["inputs"],
                             state["reports"]["proof"]["inputs"])
            self.assertEqual(value["status"], "REVIEWED_AND_PROVEN")


if __name__ == "__main__":
    unittest.main()
