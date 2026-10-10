"""Offline runner/oracle regressions. Never report these as live model judgments."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
import uuid
from unittest.mock import patch

import check_p2p_judgments_host as evaluation
from test_p2p_delivery import fixture_host, d



class OfflineJudgmentTransport:
    """Host-shaped model responses for controller wiring tests, NEVER judgment evidence."""

    def __init__(self):
        self.bad = False
        self.prompts = []

    def __call__(self, args, prompt, event_path, error_path, deadline, idle_seconds=None):
        launch = json.loads((event_path.parent / "launch.json").read_text())
        stage, inputs = launch["stage"], launch["inputs"]
        if stage not in ("review", "proof"):
            raise AssertionError("offline fixture invokes review and proof only")
        self.prompts.append((stage, prompt))
        if stage == "review":
            finding = {"id": "F1", "source": "R2", "axis": "Contract fidelity",
                       "location": "username.py", "evidence": "whitespace is accepted",
                       "consequence": "R2 is missing", "correction": "reject whitespace-only input",
                       "handoff": "implement-contract"}
            report = {
                "status": "CHANGES NEEDED" if self.bad else "REVIEWED",
                "input_identity_json": json.dumps(inputs),
                "requirements": [{"id": name, "observation": "offline transport, no live judgment"}
                                 for name in ("R1", "R2", "R3")],
                "gaps": [], "learning_candidates": [], "coverage": "R1, R2, R3",
                "checks": [{"command": "FIXTURE check", "result": "observed",
                            "observation": "not real host evidence"}],
                "limitations": ["offline fixture"], "findings": [finding] if self.bad else [],
                "missing_input": "", "expected_result": "",
            }
        else:
            proof_rows = []
            for name in ("R1", "R2", "R3"):
                missing = self.bad and name == "R2"
                proof_rows.append({
                    "id": name, "verdict": "missing" if missing else "proven",
                    "observation": "offline stub, no independent verification",
                    "evidence": [] if missing else [{
                        "assertion": "FIXTURE claim", "observation": "FIXTURE event",
                        "artifact": "FIXTURE command; no model judgment"
                    }],
                })
            report = {
                "status": "NOT PROVEN" if self.bad else "PROVEN",
                "input_identity_json": json.dumps(inputs),
                "requirements": proof_rows,
                "gaps": ["R2 whitespace regression"] if self.bad else [],
                "learning_candidates": [], "details": "OFFLINE STUB: not live proof",
            }
        product = Path(prompt.split('workspace ', 1)[1].split('. ', 1)[0])
        excluded = [inputs['work_item']] + [item['path'] for item in inputs.get('binding_inputs', [])]
        manifest = d.fs.snapshot(product, exclude=excluded)
        changed = d.fs.tree_changes(d.fs.snapshot(product, inputs['comparison_base'], exclude=excluded), manifest)
        paths = [item['path'] for item in changed]
        report['coverage_trace'] = {
            'requirements': [{'id': row['id'], 'paths': paths,
                              'existing': not bool(paths), 'evidence': ['row']}
                             for row in report['requirements']],
            'supporting_changes': [],
            **({'inspected_paths': sorted({item['path'] for item in manifest} & set(paths))}
               if stage == 'review' else {}),
        }
        session = "offline-" + uuid.uuid4().hex
        events = [
            {"type": "thread.started", "thread_id": session},
            {"type": "item.completed", "item": {
                "type": "command_execution", "command": "FIXTURE check",
                "exit_code": 0, "aggregated_output": "FIXTURE command output"}},
            {"type": "item.completed", "item": {
                "type": "agent_message", "text": json.dumps(report)}},
            {"type": "turn.completed", "usage": {"input_tokens": 1, "output_tokens": 1}},
        ]
        event_path.write_text("".join(json.dumps(event) + "\n" for event in events))
        error_path.write_text("FIXTURE transport: not live\n")
        return {"exit_code": 0, "outcome": "finished",
                "finished": d.now(), "elapsed_seconds": 0.01}


class LiveJudgmentRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="p2p-live-evaluation-offline-")
        self.root = Path(self.temp.name)
        self.home = patch.dict(os.environ, {
            "HOME": str(self.root),
            "P2P_EXECUTION_ROOT": str(self.root / "executions"),
        })
        self.home.start()
        self.data, self.digest = evaluation.load_manifest()

    def tearDown(self):
        self.home.stop()
        self.temp.cleanup()

    def test_manifest_covers_independent_positive_negative_and_follow_up_cases(self):
        cases = {case["id"]: case for case in self.data["cases"]}
        original = {
            "correct-control", "green-but-incomplete", "unrelated-scope-expansion",
            "optional-polish", "follow-up-regression",
        }
        review_quality = {
            "review-meaningful-tests", "review-tautological-test",
            "review-circular-oracle", "review-overmocked-boundary",
            "review-unreliable-regression-test", "review-sample-only-implementation",
            "review-conditional-security-risk", "review-reconcile-corrected-finding",
        }
        self.assertEqual(set(cases), original | review_quality)
        for case in cases.values():
            for candidate in case["candidates"]:
                self.assertIn(candidate["expected"]["review"], ("REVIEWED", "CHANGES NEEDED"))
                self.assertIn(candidate["expected"]["proof"], ("PROVEN", "NOT PROVEN"))
                self.assertTrue(
                    {"empty-username", "visible-username", "whitespace-only-username", "unrelated-fee"}
                    <= {p["id"] for p in candidate["oracle"]}
                )
                for probe in candidate.get("guard_probes", []):
                    self.assertEqual(probe["replace"], ["username.py"])
                    self.assertIn(probe["expected_exit"], (0, 1))
                self.assertTrue(case["rationale"])
        followup = cases["follow-up-regression"]["candidates"]
        self.assertEqual(len(followup), 2)
        self.assertEqual(followup[0]["expected"]["proof"], "PROVEN")
        self.assertEqual(followup[1]["expected"]["proof"], "NOT PROVEN")
        self.assertTrue(followup[1]["requires_previous_observations"])

    def test_fixture_oracles_exercise_real_public_cli_without_model(self):
        # This is a deterministic fixture check only. It neither grades a worker
        # nor pretends that any supported host has reviewed/proven the candidate.
        for case in self.data["cases"]:
            root, base = evaluation.source_repo(self.root / self._new_case(case), self.data, case)
            source_before = d.fs.snapshot(root)
            with fixture_host():
                delivery = evaluation.admit(root, base, len(case["candidates"]), 120)
                self.assertTrue(delivery.state["live_evaluation"])
                self.assertEqual(delivery.state["attempts"], [])
                previous = None
                for spec in case["candidates"]:
                    candidate = evaluation.capture_fixed_candidate(
                        delivery, evaluation.candidate_files(self.data, spec))
                    self.assertNotEqual(candidate["key"], previous)
                    previous = candidate["key"]
                    result = evaluation.observable_checks(
                        delivery, spec, self.root / "observations" / case["id"] / spec["name"])
                    self.assertTrue(result["passed"], case["id"] + ": " + json.dumps(result))
                    self.assertEqual(result["supplied_tests"]["exit"], 0)
                    guard = evaluation.guard_sensitivity_checks(
                        delivery, spec, self.data,
                        self.root / "observations" / case["id"] / spec["name"])
                    self.assertTrue(guard["passed"], case["id"] + ": " + json.dumps(guard))
                    self.assertEqual(delivery.state["attempts"], [])
                    delivery.current()
                self.assertEqual(
                    [g["stage"] for g in delivery.state["local_git_generations"]],
                    ["admission"] + ["live-evaluation"] * len(case["candidates"]))
            self.assertEqual(d.fs.snapshot(root), source_before)

    def _new_case(self, case):
        directory = Path(case["id"])
        (self.root / directory).mkdir()
        return directory


    def test_live_candidate_follow_up_uses_normal_per_stage_verification_history(self):
        case = next(c for c in self.data["cases"] if c["id"] == "follow-up-regression")
        directory = self.root / "followup"
        directory.mkdir()
        root, base = evaluation.source_repo(directory, self.data, case)
        transport = OfflineJudgmentTransport()
        with fixture_host(), patch.object(d, "launch", transport):
            delivery = evaluation.admit(root, base, 2, 120)
            initial, changed = case["candidates"]
            first = evaluation.capture_fixed_candidate(
                delivery, evaluation.candidate_files(self.data, initial))
            for stage in ("review", "proof"):
                result = delivery.stage(stage)
                self.assertEqual(result["status"], initial["expected"][stage])
                self.assertEqual(delivery.read_report(stage)["status"], initial["expected"][stage])
            self.assertEqual(delivery.verification_history("review")["previous_candidate"]["key"],
                             first["key"])
            transport.bad = True
            second = evaluation.capture_fixed_candidate(
                delivery, evaluation.candidate_files(self.data, changed))
            self.assertNotEqual(first["key"], second["key"])
            for stage in ("review", "proof"):
                history = delivery.verification_history(stage)
                self.assertTrue(history["available"], stage)
                self.assertEqual(history["previous_candidate"]["key"], first["key"])
                self.assertEqual(history["current_candidate"]["key"], second["key"])
                result = delivery.stage(stage)
                self.assertEqual(result["status"], changed["expected"][stage])
                self.assertEqual(delivery.read_report(stage)["status"], changed["expected"][stage])
                self.assertIn(first["key"], transport.prompts[-1][1])
                self.assertIn(second["key"], transport.prompts[-1][1])
            self.assertEqual([item["stage"] for item in delivery.state["attempts"]],
                             ["review", "proof", "review", "proof"])
            self.assertEqual(len({a["session_id"] for a in delivery.state["attempts"]}), 4)
            self.assertEqual(delivery.state["local_git_generations"][-1]["candidate_key"], second["key"])

    def test_test_quality_controls_distinguish_genuine_from_hollow_regression_guards(self):
        cases = {case["id"]: case for case in self.data["cases"]}
        positive = cases["review-meaningful-tests"]["candidates"][0]
        self.assertEqual(positive["expected"]["review"], "REVIEWED")
        self.assertEqual(positive["guard_probes"][0]["expected_exit"], 1)
        for name in ("review-tautological-test", "review-circular-oracle",
                     "review-overmocked-boundary", "review-unreliable-regression-test"):
            candidate = cases[name]["candidates"][0]
            self.assertEqual(candidate["expected"]["review"], "CHANGES NEEDED")
            self.assertEqual(candidate["expected"]["proof"], "PROVEN")
            self.assertEqual(candidate["expected"]["review_finding"]["axis"], "Engineering quality")
            self.assertEqual(candidate["guard_probes"][0]["expected_exit"], 0)
        flaky = cases["review-unreliable-regression-test"]["candidates"][0]
        self.assertEqual([p["expected_exit"] for p in flaky["guard_probes"]], [0, 1])
        self.assertEqual(
            cases["review-conditional-security-risk"]["candidates"][0]["expected"]["review"],
            "CHANGES NEEDED")
        sequence = cases["review-reconcile-corrected-finding"]["candidates"]
        self.assertTrue(sequence[1]["requires_previous_observations"])
        self.assertEqual(sequence[1]["expected"]["reconciles_review_finding"], "R2")

    def test_corrected_prior_finding_requires_fresh_positive_judgment(self):
        old = {"status": "CHANGES NEEDED", "findings": [{
            "source": "R2", "axis": "Contract fidelity",
            "evidence": "whitespace accepted", "location": "username.py"
        }]}
        complete = {"status": "REVIEWED", "findings": [],
                    "requirements": [{"id": name, "observation": "fresh checked outcome"}
                                     for name in ("R1", "R2", "R3")]}
        proof = {"status": "PROVEN", "requirements": [
            {"id": name, "verdict": "proven"} for name in ("R1", "R2", "R3")]}
        expected = {"review": "REVIEWED", "proof": "PROVEN",
                    "reconciles_review_finding": "R2"}
        self.assertEqual(evaluation.judgment_mismatches(complete, proof, expected, old), [])
        self.assertTrue(evaluation.judgment_mismatches(complete, proof, expected))
        incomplete = dict(complete, requirements=[{"id": "R1", "observation": "not R2"}])
        self.assertTrue(evaluation.judgment_mismatches(incomplete, proof, expected, old))

    def test_full_evaluation_runner_reconciles_real_candidate_history_offline(self):
        # Run the same report/receipt/oracle path as live evaluation, but with
        # unmistakably labeled offline transport. Never report these verdicts as
        # behavioral model evidence.
        case = next(c for c in self.data["cases"]
                    if c["id"] == "review-reconcile-corrected-finding")
        output = self.root / "runner"
        output.mkdir()
        fake = OfflineJudgmentTransport()

        def launch(*args, **kwargs):
            fake.bad = len(fake.prompts) < 2  # First candidate broken, second fixed.
            return fake(*args, **kwargs)

        with fixture_host(), patch.object(d, "launch", side_effect=launch):
            result = evaluation.run_case(output, self.data, case, self.digest, 120, position=1)
        self.assertTrue(result["passed"], result.get("error") or json.dumps(result))
        self.assertEqual([r["observed"]["review"]["status"] for r in result["candidates"]],
                         ["CHANGES NEEDED", "REVIEWED"])
        self.assertEqual([r["observed"]["proof"]["status"] for r in result["candidates"]],
                         ["NOT PROVEN", "PROVEN"])
        self.assertEqual(len(fake.prompts), 4)
        self.assertTrue(all("review-reconcile-corrected-finding" not in prompt
                            for _, prompt in fake.prompts))
        self.assertEqual([len(r["stage_attempts"]) for r in result["candidates"]], [2, 2])
        self.assertNotEqual(result["candidates"][0]["candidate"]["key"],
                            result["candidates"][1]["candidate"]["key"])
        self.assertEqual(result["candidates"][1]["expected"]["reconciles_review_finding"], "R2")
        saved = json.loads((output / "candidate-001" / "summary.json").read_text())
        self.assertEqual(saved["fixture"], case["id"])
        self.assertTrue(saved["passed"])
        self.assertTrue((output / "candidate-001" / "observation-02" /
                         "guard-sensitivity.json").is_file())
        self.assertTrue(Path(saved["runtime"]).is_dir())

    def test_live_evaluation_generation_requires_explicit_admission(self):
        case = self.data["cases"][0]
        directory = self.root / "ordinary"
        directory.mkdir()
        root, base = evaluation.source_repo(directory, self.data, case)
        args = evaluation.SimpleNamespace(
            work=evaluation.WORK, comparison_base=base, destination="delivery-target",
            authorize_local=True, hard_cost_cap=None, mandate=None, exclude_dirty=[],
            max_dispatches=2, max_seconds=None, max_stage_seconds=120, max_repairs=0,
            worker_idle_seconds=None,
        )
        with fixture_host():
            delivery = d.create(root, args)
            with self.assertRaisesRegex(ValueError, "not enabled"):
                delivery.capture("live-evaluation")

    def test_semantic_mismatch_detection_is_not_exact_prose_matching(self):
        cases = {case["id"]: case for case in self.data["cases"]}
        good_review = {"status": "REVIEWED", "findings": [], "requirements": []}
        proven = {"status": "PROVEN", "requirements": [
            {"id": name, "verdict": "proven"} for name in ("R1", "R2", "R3")
        ]}
        self.assertEqual(evaluation.judgment_mismatches(
            good_review, proven, cases["correct-control"]["candidates"][0]["expected"]), [])
        incomplete = cases["green-but-incomplete"]["candidates"][0]["expected"]
        self.assertTrue(evaluation.judgment_mismatches(good_review, proven, incomplete))
        missing_review = {"status": "CHANGES NEEDED", "findings": [{
            "axis": "Contract fidelity", "source": "R2",
            "location": "username.py", "evidence": "whitespace input erroneously accepted"
        }]}
        not_proven = {"status": "NOT PROVEN", "requirements": [
            {"id": "R1", "verdict": "proven"},
            {"id": "R2", "verdict": "missing"},
            {"id": "R3", "verdict": "proven"},
        ]}
        self.assertEqual(evaluation.judgment_mismatches(missing_review, not_proven, incomplete), [])
        scope = cases["unrelated-scope-expansion"]["candidates"][0]["expected"]
        self.assertTrue(evaluation.judgment_mismatches(missing_review, proven, scope))
        scope_review = {"status": "CHANGES NEEDED", "findings": [{
            "axis": "Scope and simplicity", "source": "spec.md",
            "location": "fees.py", "evidence": "fee changed from 100 to 101",
        }]}
        self.assertEqual(evaluation.judgment_mismatches(scope_review, proven, scope), [])

    def test_unsupported_host_fails_with_diagnostics_not_fake_live_evidence(self):
        output = self.root / "unsupported"
        with patch.object(evaluation.platform, "system", return_value="Linux"):
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                code = evaluation.main(["--output-dir", str(output)])
        report = json.loads(buffer.getvalue())
        self.assertEqual(code, 1)
        self.assertFalse(report["passed"])
        self.assertFalse(report["live_evidence"])
        self.assertIn("macOS", report["error"])
        self.assertEqual(json.loads((output / "summary.json").read_text()), report)
        # A repeated command may not rewrite retained invocation evidence.
        with self.assertRaises(SystemExit):
            evaluation.main(["--output-dir", str(output)])


if __name__ == "__main__":
    unittest.main()
