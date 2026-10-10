"""Bounded intra-implementation progress. Offline host fixtures are NOT live evidence."""
import contextlib
import io
import json
import shutil
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import test_p2p_delivery as fixture
import p2p_slices as slices


d = fixture.d


def witness(**changes):
    return {
        "id": "I1", "requirement_ids": ["R1"], "expected_result": "CLI prints hello",
        "checks": [{"kind": "test", "command": "python3 greet.py",
                    "result": "passed", "observation": "hello\n"}],
        "paths": ["greet.py"], "outcome": "VERIFIED",
        "boundary_reason": "", "next_action": "", "retires": [],
    } | changes


class EvidenceSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.before = [{"path": "spec.txt", "type": "file", "mode": "100644",
                        "content_base64": "Y2hlY2sK"}]
        self.after = self.before + [{"path": "greet.py", "type": "file", "mode": "100644",
                                     "content_base64": "cHJpbnQoJ2hlbGxvJykK"}]
        self.report = {"status": "IMPLEMENTED", "gaps": [],
                       "implementation_slice": witness()}
        self.events = [{"command": "python3 greet.py", "exit_code": 0,
                        "aggregated_output": "hello\n"}]

    def check(self, **params):
        return slices.validate(self.report | params, ["R1"], [], self.events,
                               self.after, self.before)

    def test_single_complete_slice_uses_actual_host_observation(self):
        self.assertEqual(self.check()["id"], "I1")
        self.assertEqual(len(self.check()["checks"]), 1)
        self.assertLessEqual(len(json.dumps(self.check())), 2048)

    def test_false_green_or_missing_check_does_not_verify_slice(self):
        for change in (
                witness(checks=[]),
                witness(checks=[dict(witness()["checks"][0], observation="not observed")]),
                witness(checks=[dict(witness()["checks"][0], command="echo imaginary result")]),
                witness(checks=[dict(witness()["checks"][0], result="failed")]),
                witness(paths=[]),
                witness(requirement_ids=["R9"]),
                witness(next_action="keep working"),
                witness(id="I9"),
                witness(outcome="BLOCKED")):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.check(implementation_slice=change)

    def test_manual_inspection_evidence_is_allowed_when_observed(self):
        manual = witness(checks=[{"kind": "inspection", "command": "cat greet.py",
                                  "result": "observed", "observation": "print("}])
        report = self.report | {"implementation_slice": manual}
        self.assertEqual(slices.validate(
            report, ["R1"], [],
            [{"command": "cat greet.py", "exit_code": 0,
              "aggregated_output": "print('hello')\n"}], self.after, self.before)["id"], "I1")

    def test_partial_slice_requires_real_boundary_and_next_action(self):
        partial = witness(boundary_reason="A separately observable database step.",
                          next_action="Add durability acceptance checks.")
        report = {"status": "PARTIAL", "gaps": ["R1 durability not yet checked"],
                  "implementation_slice": partial}
        self.assertEqual(slices.validate(
            report, ["R1"], [], self.events, self.after, self.before)["outcome"], "VERIFIED")
        for key in ("boundary_reason", "next_action"):
            bad = dict(partial, **{key: ""})
            with self.assertRaisesRegex(ValueError, "justified next"):
                slices.validate(report | {"implementation_slice": bad},
                                ["R1"], [], self.events, self.after, self.before)

    def test_slice_retirement_requires_reason_and_full_obligation_coverage(self):
        original = {"slice": witness(boundary_reason="Separate API outcome.",
                                     next_action="Implement database step."),
                    "attempt_id": "first"}
        after = self.after + [{"path": "tests/test_greet.py", "type": "file",
                               "mode": "100644", "content_base64": "YXNzZXJ0IFRydWUK"}]
        second = witness(id="I2", paths=["tests/test_greet.py"],
                         retires=[{"id": "I1", "reason": "Old plan replaced by direct API check."}])
        report = {"status": "IMPLEMENTED", "gaps": [], "implementation_slice": second}
        result = slices.validate(report, ["R1"], [original],
                                 self.events, after, self.after)
        self.assertEqual(result["retires"][0]["id"], "I1")
        with self.assertRaisesRegex(ValueError, "replacement"):
            slices.validate(report | {"implementation_slice": second |
                                      {"retires": [{"id": "I1", "reason": ""}]}},
                            ["R1"], [original], self.events, after, self.after)


    def test_changed_verified_slice_file_needs_explicit_replacement_and_recheck(self):
        earlier = {"slice": witness(boundary_reason="Separate API outcome.",
                                    next_action="Add persistence regression"),
                   "attempt_id": "verified-I1"}
        next_tree = self.before + [
            {"path": "greet.py", "type": "file", "mode": "100644",
             "content_base64": "cHJpbnQoJ2J5ZScpCg=="}
        ]
        unchecked = witness(id="I2", paths=["greet.py"], retires=[])
        with self.assertRaisesRegex(ValueError, "changed previously verified"):
            slices.validate(
                {"status": "IMPLEMENTED", "gaps": [],
                 "implementation_slice": unchecked},
                ["R1"], [earlier], self.events, next_tree, self.after)
        checked = unchecked | {"retires": [
            {"id": "I1", "reason": "The dependent public function changed; recheck R1."}]}
        self.assertEqual(slices.validate(
            {"status": "IMPLEMENTED", "gaps": [],
             "implementation_slice": checked},
            ["R1"], [earlier], self.events, next_tree, self.after)["id"], "I2")


class DeliverySliceTests(unittest.TestCase):
    def setUp(self):
        self.base = fixture.DeliveryTests("test_clean_project_delivery_uses_local_contract_and_records")
        self.base.setUp()
        self.addCleanup(self.base.tearDown)
        self.work = ".p2p/work/tiny/contract.md"

    def test_tiny_change_finishes_one_slice_with_no_extra_model_stage(self):
        code, outcome = self.base.cli()
        self.assertEqual(code, 0, outcome.get("blocker"))
        state = self.base.state()
        self.assertEqual([a["stage"] for a in state["attempts"]],
                         ["preflight-1", "preflight-2", "implementation", "review", "proof"])
        self.assertEqual(state["implementation_slice_version"], 1)
        self.assertEqual(len(state["implementation_slices"]), 1)
        slice_ = state["implementation_slices"][0]
        self.assertEqual(slice_["slice"]["outcome"], "VERIFIED")
        self.assertEqual(slice_["slice"]["requirement_ids"], ["R1"])
        self.assertEqual(slice_["candidate_key"], state["candidate"]["key"])
        self.assertEqual(outcome["status"], "REVIEWED_AND_PROVEN")
        self.assertEqual(outcome["implementation_progress"]["verified"], 1)

    def test_justified_partial_slice_continues_once_without_diagnosis(self):
        self.base.fake.mode = "sliced"
        code, value = self.base.cli()
        self.assertEqual(code, 0, value.get("blocker"))
        self.assertEqual(value["status"], "REVIEWED_AND_PROVEN")
        state = self.base.state()
        self.assertEqual([a["stage"] for a in state["attempts"]],
                         ["preflight-1", "preflight-2", "implementation",
                          "implementation", "review", "proof"])
        self.assertEqual(len(state["implementation_slices"]), 2)
        self.assertEqual([r["slice"]["id"] for r in state["implementation_slices"]],
                         ["I1", "I2"])
        self.assertNotEqual(state["implementation_slices"][0]["candidate_key"],
                            state["implementation_slices"][1]["candidate_key"])
        self.assertEqual(self.base.fake.calls.count("implementation"), 2)
        self.assertEqual(self.base.fake.calls.count("diagnosis"), 0)
        self.assertEqual(self.base.fake.calls.count("review"), 1)
        self.assertEqual(self.base.fake.calls.count("proof"), 1)
        self.assertEqual(value["implementation_progress"]["next_slice"], None)

    def test_interrupted_between_verified_slices_resumes_without_replay(self):
        self.base.fake.mode = "sliced"
        real_stage = d.Delivery.stage
        def stop_before_second(delivery, name, *args, **kwargs):
            if name == "implementation" and delivery.state.get("implementation_slices"):
                raise ValueError("fixture interruption between evidenced slices")
            return real_stage(delivery, name, *args, **kwargs)
        with patch.object(d.Delivery, "stage", autospec=True, side_effect=stop_before_second):
            code, interrupted = self.base.cli()
        self.assertEqual(code, 1)
        self.assertIn("fixture interruption", interrupted["blocker"])
        record = self.base.state()
        self.assertEqual(len(record["implementation_slices"]), 1)
        self.assertEqual(record["implementation_slices"][0]["slice"]["outcome"], "VERIFIED")
        calls_before = self.base.fake.calls.count("implementation")
        code, resumed = self.base.cli("resume")
        self.assertEqual(code, 0, resumed.get("blocker"))
        self.assertEqual(resumed["status"], "REVIEWED_AND_PROVEN")
        self.assertEqual(self.base.fake.calls.count("implementation") - calls_before, 1)
        self.assertEqual(len(self.base.state()["implementation_slices"]), 2)
        self.assertEqual(self.base.fake.calls.count("diagnosis"), 0)
        self.assertEqual([x["slice"]["id"] for x in self.base.state()["implementation_slices"]],
                         ["I1", "I2"])

    def test_portable_checkpoint_restarts_only_unfinished_implementation_slice(self):
        import test_p2p_checkpoints as portable
        run = portable.CheckpointTests(
            "test_completed_stage_resumes_on_another_computer_without_old_execution")
        run.setUp()
        try:
            run.fixture.fake.mode = "sliced"
            original = d.Delivery.stage
            def interrupt(delivery, name, *args, **kwargs):
                if name == "implementation" and delivery.state.get("implementation_slices"):
                    raise ValueError("fixture portable boundary between implementation slices")
                return original(delivery, name, *args, **kwargs)
            with patch.object(d.Delivery, "stage", autospec=True, side_effect=interrupt):
                code, partial = run.fixture.cli()
            self.assertEqual(code, 1, partial)
            checkpoint_path = run.root / "p2p-state/tiny.json"
            raw = checkpoint_path.read_bytes()
            checkpoint = json.loads(raw)
            self.assertEqual([r["slice"]["id"] for r in
                              checkpoint["execution"]["implementation_slices"]], ["I1"])
            self.assertLess(len(raw), d.fs.CHECKPOINT_LIMIT)
            remote, clone = run.publish_fixture(checkpoint)
            self.assertEqual(d.fs.checkpoint_status(run.root, run.work,
                                                    str(remote))["status"], "PORTABLE")
            shutil.rmtree(run.root / ".p2p")
            shutil.rmtree(Path(run.fixture.temp.name) / "home/.p2p")
            restored = d.fs.restore_checkpoint(clone, raw)
            self.assertEqual(restored["status"], "RESTORED")
            calls_before = run.fixture.fake.calls.count("implementation")
            code, resumed = run.fixture.run_root(clone, run.work, run.fixture.base, "resume")
            self.assertEqual(code, 0, resumed.get("blocker"))
            state = json.loads((clone / ".p2p/work/tiny/delivery.json").read_bytes())
            self.assertEqual([r["slice"]["id"] for r in state["implementation_slices"]],
                             ["I1", "I2"])
            self.assertEqual(state["implementation_slices"][0]["attempt_id"],
                             checkpoint["execution"]["implementation_slices"][0]["attempt_id"])
            stages = [a["stage"] for a in state["attempts"]]
            self.assertEqual(stages.count("prior-preflight-1"), 1)
            self.assertEqual(stages.count("preflight-1"), 1)
            self.assertEqual(stages.count("preflight-2"), 1)
            self.assertEqual(stages.count("implementation"), 2)
            self.assertEqual(stages.count("review"), 1)
            self.assertEqual(stages.count("proof"), 1)
            self.assertEqual(run.fixture.fake.calls.count("implementation") - calls_before, 1)
            self.assertEqual(resumed["status"], "REVIEWED_AND_PROVEN")
        finally:
            run.tearDown()

    def test_tampered_saved_slice_never_counts_as_verified(self):
        self.base.fake.mode = "sliced"
        self.assertEqual(self.base.cli()[0], 0)
        delivery = d.Delivery(self.base.root, self.work, self.base.state())
        records = delivery.state["implementation_slices"]
        records[0]["report_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "stale or unverified"):
            slices.verify_retained(delivery.state, delivery.runtime, delivery.receipt)


if __name__ == "__main__":
    unittest.main()
