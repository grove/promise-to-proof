"""Safe fact reuse and refreshed verifier conclusions (all hosts below are OFFLINE)."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
import uuid
from unittest.mock import patch

import p2p_applicability as applicability
import test_p2p_delivery as fixture
import check_p2p_judgments_host as judgments


d = fixture.d


def prior_trace(stage="proof", *, unknown=False, reach="bounded", extra=None):
    trace = {
        "requirements": [{"id": name, "paths": [path], "existing": False,
                          "evidence": ["row"]}
                         for name, path in (("R1", "one.py"), ("R2", "two.py"),
                                            ("R3", "three.py"))],
        "supporting_changes": [],
        "risks": [{"id": "S1", "requirements": ["R1"], "paths": ["one.py"],
                   "reach": reach, "trigger": "one changes unexpectedly",
                   "why_applicable": "its public call site depends on one",
                   "consequence": "R1 can regress", "evidence": ["row"],
                   "status": "addressed"}] if reach else [],
    }
    if stage == "review":
        trace["inspected_paths"] = ["one.py", "two.py", "three.py"]
    if unknown:
        trace["requirements"][1]["paths"] = []
    if extra:
        trace["supporting_changes"] = extra
    return trace


def old_report(stage="proof", **kwargs):
    report = {"status": "REVIEWED" if stage == "review" else "PROVEN",
              "requirements": [
                  {"id": name, "observation": "Independently checked old " + name,
                   **({"verdict": "proven",
                       "evidence": [{"assertion": name, "observation": "old good result",
                                     "artifact": "saved command"}]}
                      if stage == "proof" else {})}
                  for name in ("R1", "R2", "R3")],
              "coverage_trace": prior_trace(stage),
              "findings": [] if stage == "review" else None}
    return report | kwargs


class PureApplicabilityTests(unittest.TestCase):
    def assess(self, changed, stage="proof", report=None):
        return applicability.classify(
            report or old_report(stage), [{"path": p, "state": "modified",
                                           "type": "file", "mode": "100644",
                                           "sha256": "a"*64} for p in changed],
            ["R1", "R2", "R3"], stage,
            prior_candidate="snapshot:sha256:" + "0"*64, report_sha256="1"*64)

    def test_one_localized_change_reuses_only_disjoint_original_observations(self):
        result = self.assess(["one.py"])
        self.assertEqual(result["status"], "SELECTIVE")
        self.assertEqual(result["refresh_requirements"], ["R1"])
        self.assertEqual([row["id"] for row in result["potentially_reusable"]],
                         ["R2", "R3"])
        self.assertTrue(all(item["from_candidate"].endswith("0"*64)
                            for item in result["potentially_reusable"]))
        self.assertTrue(result["new_full_verdict_required"])
        self.assertEqual(result["previous_report_sha256"], "1"*64)

    def test_broad_recheck_on_unmapped_shared_tests_configs_and_uncertain_reach(self):
        cases = [
            (["unlisted.py"], old_report(), "not covered"),
            (["one.py"], old_report(coverage_trace=prior_trace(unknown=True)),
             "dependency paths"),
            (["one.py"], old_report(coverage_trace=prior_trace(reach="uncertain")),
             "uncertain behavioral reach"),
            (["tests/test_one.py"], old_report(coverage_trace=prior_trace(
                extra=[{"path": "tests/test_one.py", "reason": "test fixture"}])),
             "shared supporting"),
            (["one.py"], old_report(coverage_trace={"requirements": [],
                                                     "supporting_changes": []}),
             "traceability"),
        ]
        for changed, report, hint in cases:
            with self.subTest(hint=hint):
                result = self.assess(changed, report=report)
                self.assertEqual(result["status"], "FULL_RECHECK")
                self.assertEqual(result["potentially_reusable"], [])
                self.assertEqual(result["refresh_requirements"], ["R1", "R2", "R3"])
                self.assertIn(hint.lower(), result["reason"].lower())

    def test_old_defect_or_missing_actual_proof_is_never_called_reusable(self):
        broken = old_report()
        broken["requirements"][1]["verdict"] = "missing"
        result = self.assess(["one.py"], report=broken)
        self.assertEqual(result["refresh_requirements"], ["R1", "R2"])
        self.assertEqual([x["id"] for x in result["potentially_reusable"]], ["R3"])
        uncertain_source = old_report("review")
        uncertain_source["findings"] = [{"source": "other-binding", "axis": "Contract fidelity"}]
        self.assertEqual(self.assess(["one.py"], "review", uncertain_source)["status"], "FULL_RECHECK")

    def test_old_without_risk_trace_refreshes_everything_but_unchanged_is_explicit(self):
        legacy = old_report()
        del legacy["coverage_trace"]["risks"]
        self.assertEqual(self.assess(["one.py"], report=legacy)["status"], "FULL_RECHECK")
        identical = self.assess([])
        self.assertEqual(identical["status"], "UNCHANGED")
        self.assertEqual(identical["potentially_reusable"], [])
        self.assertEqual(identical["refresh_requirements"], [])


class OfflineSelectiveTransport:
    """Labeled fake report transport; MUST NOT be treated as review/proof evidence."""
    def __init__(self):
        self.calls = []
    def __call__(self, args, prompt, event_path, error_path, deadline, idle_seconds=None):
        launch = json.loads((event_path.parent / "launch.json").read_text())
        stage, inputs = launch["stage"], launch["inputs"]
        assert stage in ("review", "proof"), stage
        self.calls.append((stage, inputs["key"], prompt))
        product = Path(prompt.split("workspace ", 1)[1].split(". ", 1)[0])
        manifest = d.fs.snapshot(product, exclude=[inputs["work_item"]])
        base = d.fs.snapshot(product, inputs["comparison_base"],
                             exclude=[inputs["work_item"]])
        changed = d.fs.tree_changes(base, manifest)
        paths = sorted({x["path"] for x in changed} & {"one.py", "two.py", "three.py"})
        trace = prior_trace(stage, reach="bounded")
        trace["inspected_paths"] = paths if stage == "review" else trace.get("inspected_paths")
        if stage != "review":
            trace.pop("inspected_paths", None)
        evidence = [{"assertion": "OFFLINE: " + x, "observation": "offline fake",
                     "artifact": "FIXTURE command"} for x in ("one.py",)]
        report = {"status": "REVIEWED" if stage == "review" else "PROVEN",
                  "input_identity_json": json.dumps(inputs),
                  "requirements": [
                      {"id": name, "observation": "OFFLINE fixture inspected " + path,
                       **({} if stage == "review" else {
                           "verdict": "proven", "evidence": evidence})}
                      for name, path in (("R1", "one.py"), ("R2", "two.py"),
                                         ("R3", "three.py"))],
                  "gaps": [], "learning_candidates": [], "coverage_trace": trace}
        if stage == "review":
            report.update(coverage="Offline fixture paths", checks=[{
                "command": "FIXTURE python3", "result": "passed",
                "observation": "OFFLINE, not real verification"}],
                limitations=["Offline fixture"], findings=[],
                missing_input="", expected_result="")
        else:
            report["details"] = "OFFLINE fixture report — not model proof"
        events = [
            {"type": "thread.started", "thread_id": uuid.uuid4().hex},
            {"type": "item.completed", "item": {"type": "command_execution",
                "command": "FIXTURE python3", "aggregated_output": "FIXTURE outcome",
                "exit_code": 0}},
            {"type": "item.completed", "item": {"type": "agent_message",
                "text": json.dumps(report)}},
            {"type": "turn.completed", "usage": {"input_tokens": 1, "output_tokens": 1}},
        ]
        event_path.write_text("".join(json.dumps(e) + "\n" for e in events))
        error_path.write_text("OFFLINE fixture only\n")
        return {"exit_code": 0, "outcome": "finished", "finished": d.now(),
                "elapsed_seconds": 0.01}


class ControllerReuseTests(unittest.TestCase):
    def setUp(self):
        self.case = fixture.DeliveryTests("test_clean_project_delivery_uses_local_contract_and_records")
        self.case.setUp()
        self.addCleanup(self.case.tearDown)
        self.work = ".p2p/work/tiny/contract.md"

    def test_completed_resume_is_read_only_and_skips_every_model_and_canonical_write(self):
        self.assertEqual(self.case.cli()[0], 0)
        local = d.local_directory(self.case.root, self.work)
        state = (local / "delivery.json").read_bytes()
        cp = self.case.root / "p2p-state/tiny.json"
        checkpoint = cp.read_bytes()
        before_calls = list(self.case.fake.calls)
        before_files = {(local / name).relative_to(local).as_posix(): (local / name).read_bytes()
                        for name in ("delivery.json", "implementation.md", "review.md", "proof.md")}
        code, result = self.case.cli("resume")
        self.assertEqual(code, 0, result.get("blocker"))
        self.assertEqual(result["reuse"]["status"], "UNCHANGED_COMPLETION")
        self.assertEqual(result["reuse"]["new_model_calls"], 0)
        self.assertEqual(self.case.fake.calls, before_calls)
        self.assertEqual((local / "delivery.json").read_bytes(), state)
        self.assertEqual(cp.read_bytes(), checkpoint)
        self.assertEqual({key: (local / key).read_bytes() for key in before_files},
                         before_files)
        self.assertEqual(result["work_selection"]["next"],
                         "none — current local completion already established")

    def test_corrupt_candidate_and_checkpoint_never_fast_reuse(self):
        self.assertEqual(self.case.cli()[0], 0)
        source = self.case.runtime() / "workspace/greet.py"
        original = source.read_bytes()
        source.write_text("print('wrong')\n")
        code, response = self.case.cli("resume")
        self.assertEqual(code, 1)
        self.assertIn("candidate", response["blocker"].lower())
        source.write_bytes(original)
        cp = self.case.root / "p2p-state/tiny.json"
        preserved = cp.read_bytes()
        cp.write_bytes(preserved + b" ")
        code, response = self.case.cli("resume")
        self.assertEqual(code, 1)
        self.assertIn("checkpoint", response["blocker"].lower())

    def test_completed_after_cleanup_returns_verified_saved_record_without_write(self):
        self.case.complete_and_cleanup()
        directory = self.case.root / ".p2p/work/tiny/artifacts"
        before = {name: (directory / name).read_bytes() for name in
                  ("candidate.json", "delivery.json", "review.md", "proof.md")}
        calls = len(self.case.fake.calls)
        code, output = self.case.cli("resume")
        self.assertEqual(code, 0, output.get("blocker"))
        self.assertEqual(output["reuse"]["status"], "UNCHANGED_COMPLETION")
        self.assertEqual(len(self.case.fake.calls), calls)
        self.assertEqual({name: (directory / name).read_bytes() for name in before}, before)

    def test_missing_new_host_preflight_cannot_take_unchanged_fast_path(self):
        self.assertEqual(self.case.cli()[0], 0)
        state = self.case.state()
        state["checkpoint_restored_from"] = "a"*64
        state["preflight_complete"] = False
        self.assertEqual(applicability.next_work(state)["next"], "receiving-host preflight")
        delivery = d.Delivery(self.case.root, self.work, state)
        delivery.read_only = True
        with self.assertRaisesRegex(ValueError, "host readiness"):
            delivery.verified_unchanged_completion()

    def test_resume_status_explains_missing_and_reused_actual_stages(self):
        self.assertEqual(self.case.cli()[0], 0)
        state = self.case.state()
        summary = applicability.next_work(state)
        self.assertEqual(summary["stages"], dict.fromkeys(
            ("implementation", "review", "proof"), "REUSED"))
        self.assertEqual(summary["preflight"], "READY")
        state["reports"].pop("proof")
        self.assertEqual(applicability.next_work(state)["next"], "proof")
        state["reports"]["review"]["inputs"]["key"] = "stale"
        self.assertEqual(applicability.next_work(state)["stages"]["review"], "STALE")


class ChangeScopeControllerTests(unittest.TestCase):
    def test_changed_candidate_runs_fresh_independent_full_conclusions_and_selective_checks(self):
        with tempfile.TemporaryDirectory(prefix="p2p-selective-controller-") as folder:
            location = Path(folder)
            with patch.dict(os.environ, {
                    "HOME": folder, "P2P_EXECUTION_ROOT": str(location / "executions")}):
                test_data, _ = judgments.load_manifest()
                place = location / "case"
                place.mkdir()
                root, base = judgments.source_repo(place, test_data, {})
                actor = OfflineSelectiveTransport()
                with fixture.fixture_host(), patch.object(d, "launch", actor):
                    delivery = judgments.admit(root, base, 2, 120)
                    first = judgments.capture_fixed_candidate(delivery, {
                        "one.py": "VERSION = 1\n", "two.py": "VERSION = 2\n",
                        "three.py": "VERSION = 3\n"})
                    for stage in ("review", "proof"):
                        self.assertEqual(delivery.stage(stage)["status"],
                                         "REVIEWED" if stage == "review" else "PROVEN")
                    second = judgments.capture_fixed_candidate(delivery, {
                        "one.py": "VERSION = 10\n"})
                    self.assertNotEqual(first["key"], second["key"])
                    for stage in ("review", "proof"):
                        handoff = delivery.verification_history(stage)
                        self.assertTrue(handoff["available"], handoff)
                        advice = handoff["applicability"]
                        self.assertEqual(advice["status"], "SELECTIVE", advice)
                        self.assertEqual(advice["refresh_requirements"], ["R1"])
                        self.assertEqual([row["id"] for row in advice["potentially_reusable"]],
                                         ["R2", "R3"])
                        self.assertTrue(advice["new_full_verdict_required"])
                        verdict = delivery.stage(stage)
                        self.assertEqual(verdict["status"],
                                         "REVIEWED" if stage == "review" else "PROVEN")
                        self.assertEqual(json.loads(verdict["input_identity_json"])["key"],
                                         second["key"])
                    self.assertEqual([stage for stage, _, _ in actor.calls],
                                     ["review", "proof", "review", "proof"])
                    self.assertEqual(len({key for _, key, _ in actor.calls}), 2)
                    self.assertEqual(len({json.loads(a["inputs"] if isinstance(a["inputs"], str)
                                         else json.dumps(a["inputs"]))["key"] for a in
                                         delivery.state["attempts"] if a["stage"] in ("review", "proof")}), 2)
                    # Both new stage prompts may refer ONLY to their own report history.
                    self.assertIn("applicability", actor.calls[2][2])
                    self.assertIn("applicability", actor.calls[3][2])
                    self.assertNotEqual(delivery.state["reports"]["review"]["attempt_id"],
                                        delivery.state["reports"]["proof"]["attempt_id"])


if __name__ == "__main__":
    unittest.main()
