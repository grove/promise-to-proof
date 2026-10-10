#!/usr/bin/env python3
"""Offline acceptance checks for P2P delivery measurements."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

CHECKS = Path(__file__).resolve().parent
sys.path.insert(0, str(CHECKS))
sys.path.insert(0, str(CHECKS.parent / "skills/productivity/deliver-issue/scripts"))
from p2p_delivery_measurements import SCHEMA, EXPORT_SCHEMA, build
import p2p_delivery_measurements as measurements
import compare_p2p_delivery_measurements as comparison
import p2p_delivery as delivery
import export_p2p_delivery_measurement as exporter
from test_p2p_delivery import FakeTransport, fixture_host, repo


def iso(seconds):
    import datetime
    return datetime.datetime.fromtimestamp(seconds, datetime.timezone.utc).isoformat()


def sample_state(status="RUNNING"):
    return {
        "invocation_id": "episode-1", "work_item": ".p2p/work/task/contract.md",
        "contract": {"revision": "v1", "sha256": "c" * 64},
        "comparison_base": "b" * 40, "candidate": {"key": "snapshot:sha256:" + "d" * 64},
        "local_git_base": {"repository_id": "repo-a-d10c3299628ebf1e"},
        "policy": "macos-codex-local-v1", "host": {"name": "Codex CLI", "version": "2.0",
                                                        "executable": "/usr/local/bin/codex"},
        "started_at": iso(100), "started_epoch": 100, "deadline_started_epoch": 120, "deadline": 130,
        "status": status, "repair_used": False, "resume_count": 0,
        "attempts": [
            {"id": "pre-1", "stage": "preflight-1", "started": iso(104), "launch_started": iso(105),
             "launch_finished": iso(115), "finished": iso(115),
             "elapsed_seconds": 10, "status": "complete", "outcome": "finished",
             "usage": {"input_tokens": 7, "output_tokens": 3, "cached_input_tokens": 2,
                       "reasoning_tokens": 1, "total_tokens": 13}, "inputs": {}},
            {"id": "impl-1", "stage": "implementation", "started": iso(108), "launch_started": iso(110),
             "launch_finished": iso(145), "finished": iso(145),
             "elapsed_seconds": 35, "status": "complete", "outcome": "finished",
             "usage": {"input_tokens": 11, "output_tokens": 5}, "inputs": {"candidate_key": "snapshot:impl"}},
            {"id": "review-1", "stage": "review", "started": iso(138), "launch_started": iso(140),
             "launch_finished": iso(160), "finished": iso(160),
             "elapsed_seconds": 20, "status": "complete", "outcome": "finished",
             "usage": "unknown", "inputs": {"candidate_key": "snapshot:impl"}},
        ],
    }


def fixture_runtime(folder, state):
    folder.mkdir(parents=True, exist_ok=True)
    for attempt in state["attempts"]:
        path = folder / "attempts" / attempt["id"] / "launch.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "prompt": "PRIVATE RAW PROMPT MUST NOT BE EXPORTED",
            "configuration": {"model": "model-a", "model_reasoning_effort": "high",
                              "api_key": "must-not-export"}}))


def record(episode_id, elapsed, seconds, model):
    return {
        "schema": SCHEMA, "episode_id": episode_id, "work_item": "work/task.md",
        "repository_id": "repo-a-d10c3299628ebf1e",
        "contract": {"revision": "v1", "sha256": "c" * 64}, "comparison_base": "b" * 40,
        "elapsed_seconds": elapsed,
        "stages": {"implementation": {"attempt_count": 1, "attempt_seconds": seconds}},
        "attempts": [{"stage": "implementation", "usage": {"input_tokens": 4, "output_tokens": 2,
                               "cached_input_tokens": None, "reasoning_tokens": None, "other": {}}}],
        "host_configurations": [{"model": model, "controller": "v1"}],
        "terminal_outcome": "successful",
    }


class MeasurementTests(unittest.TestCase):
    def test_launch_interval_excludes_delayed_reservation_preparation(self):
        state = sample_state("BLOCKED")
        state["attempts"] = [{"id": "delayed", "stage": "implementation", "started": iso(100),
                              "launch_started": iso(110), "launch_finished": iso(118),
                              "finished": iso(118), "elapsed_seconds": 8,
                              "status": "complete", "outcome": "finished", "usage": {},
                              "inputs": {}}]
        state["ended_at"] = iso(120)
        with tempfile.TemporaryDirectory() as temporary:
            item = build(state, temporary)
        attempt = item["attempts"][0]
        self.assertEqual(attempt["reserved_at"], iso(100))
        self.assertEqual((attempt["start"], attempt["end"]), (iso(110), iso(118)))
        self.assertAlmostEqual((measurements._epoch(attempt["end"]) -
                                measurements._epoch(attempt["start"])), attempt["elapsed_seconds"])
        self.assertEqual(item["attempt_seconds"], 8)
        self.assertEqual(item["controller_seconds"], 12)

    def test_transport_receipt_bounds_match_monotonic_elapsed(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            result = delivery.launch([sys.executable, "-c", "pass"], "",
                                     folder / "events.jsonl", folder / "stderr.txt", None)
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["launch_finished"], result["finished"])
        interval = measurements._epoch(result["launch_finished"]) - measurements._epoch(
            result["launch_started"])
        self.assertAlmostEqual(interval, result["elapsed_seconds"], delta=0.001)

    def test_episode_identity_intervals_usage_and_preflight_are_separate(self):
        state = sample_state(status="BLOCKED")
        state["ended_at"] = iso(220)
        state["attempts"][1]["elapsed_seconds"] = 35
        with tempfile.TemporaryDirectory() as temporary:
            runtime = Path(temporary)
            fixture_runtime(runtime, state)
            item = build(state, runtime)
        self.assertEqual(item["schema"], SCHEMA)
        self.assertEqual(item["episode_id"], "episode-1")
        self.assertEqual((item["repository_id"], item["work_item"], item["contract"]["revision"],
                          item["contract"]["sha256"], item["comparison_base"]),
                         ("repo-a-d10c3299628ebf1e", state["work_item"], "v1", "c" * 64, "b" * 40))
        self.assertEqual(item["elapsed_seconds"], 120)
        self.assertEqual(item["attempt_seconds"], 65)
        self.assertEqual(item["controller_seconds"], 65)
        self.assertEqual(item["controller_breakdown_seconds"]["setup_admission"], 20)
        self.assertEqual(item["controller_breakdown_seconds"]["preflight_host_check_attempts"], 10)
        self.assertEqual(item["pre_deadline_setup_seconds"], 20)
        self.assertEqual(item["execution_window_seconds"], 100)
        self.assertEqual(item["preflight_attempt_count"], 1)
        self.assertEqual(item["dispatch_count"], 3)
        self.assertEqual(item["stages"]["implementation"]["attempt_seconds"], 35)
        self.assertEqual(item["attempts"][0]["usage"]["cached_input_tokens"], 2)
        self.assertIsNone(item["attempts"][1]["usage"]["reasoning_tokens"])
        self.assertEqual(item["attempts"][0]["usage"]["other"], {"total_tokens": 13})
        self.assertEqual(item["attempts"][1]["candidate_key"], "snapshot:impl")
        serialized = json.dumps(item)
        self.assertNotIn("PRIVATE RAW PROMPT", serialized)
        self.assertNotIn("api_key", serialized)
        self.assertNotIn("source code", serialized)

    def test_incoherent_attempt_bounds_make_attempt_and_stage_time_unknown(self):
        state = sample_state("BLOCKED")
        state["ended_at"] = iso(220)
        state["attempts"] = [dict(state["attempts"][0], launch_started=iso(80),
                                  launch_finished=iso(90), elapsed_seconds=10)]
        with tempfile.TemporaryDirectory() as temporary:
            item = build(state, temporary)
        self.assertIsNone(item["attempts"][0]["elapsed_seconds"])
        self.assertIsNone(item["attempt_seconds"])
        self.assertIsNone(item["stages"]["preflight-1"]["attempt_seconds"])
        self.assertIsNone(item["controller_seconds"])
        other = record("episode-valid", 60, 30, "model-a")
        other["work_item"] = state["work_item"]
        compared = comparison.compare({"schema": EXPORT_SCHEMA, "episodes": [item, other]})
        group = compared["compatible_groups"][0]
        self.assertIsNone(group["stages"]["preflight-1"][0]["attempt_seconds"])
        self.assertIn("stage:preflight-1", group["unknowns"])

    def test_invalid_deadline_ordering_is_unknown(self):
        state = sample_state("BLOCKED")
        state["ended_at"] = iso(220)
        state["deadline_started_epoch"] = 90
        with tempfile.TemporaryDirectory() as temporary:
            item = build(state, temporary)
        self.assertIsNone(item["pre_deadline_setup_seconds"])
        self.assertIsNone(item["execution_window_seconds"])

    def test_reserve_times_direct_source_validation(self):
        state = {"limits": {"dispatches": None, "stage_seconds": 60}, "deadline": None,
                 "repair_used": False, "attempts": [], "controller_timing": {}}
        root = Path(__file__).resolve().parents[1]
        controller = delivery.Delivery(root, ".p2p/work/measure-p2p-delivery/contract.md", state)
        with patch.object(controller, "source_stable") as source_check, \
                patch.object(controller, "save"), \
                patch.object(delivery.time, "monotonic", side_effect=[100.0, 104.0]):
            controller.reserve("implementation", {}, Path("/private/tmp/issue59-reserve-scratch"))
        source_check.assert_called_once_with()
        self.assertEqual(state["controller_timing"]["identity_snapshot_validation"], 4.0)

    def test_controller_breakdown_keeps_validation_and_persistence_separate(self):
        state = sample_state("BLOCKED")
        state["ended_at"] = iso(220)
        state["controller_timing"] = {
            "identity_snapshot_validation": 1.25,
            "persistence_readback": 0.5,
        }
        with tempfile.TemporaryDirectory() as temporary:
            item = build(state, temporary)
        self.assertEqual(item["controller_breakdown_seconds"]["identity_snapshot_validation"], 1.25)
        self.assertEqual(item["controller_breakdown_seconds"]["persistence_readback"], 0.5)

    def test_incomplete_attempt_interval_makes_controller_wall_time_unknown(self):
        state = sample_state("BLOCKED")
        state["ended_at"] = iso(220)
        state["attempts"][1]["launch_finished"] = None
        with tempfile.TemporaryDirectory() as temporary:
            item = build(state, temporary)
        self.assertIsNone(item["controller_seconds"])

    def test_legacy_attempt_without_launch_interval_has_unknown_controller_time(self):
        state = sample_state("BLOCKED")
        state["ended_at"] = iso(220)
        for attempt in state["attempts"]:
            attempt.pop("launch_started")
            attempt.pop("launch_finished")
        with tempfile.TemporaryDirectory() as temporary:
            item = build(state, temporary)
        self.assertIsNone(item["controller_seconds"])

    def test_incoherent_launch_bounds_make_controller_time_unknown(self):
        state = sample_state("BLOCKED")
        state["ended_at"] = iso(220)
        state["attempts"][0]["launch_finished"] = iso(116)
        with tempfile.TemporaryDirectory() as temporary:
            item = build(state, temporary)
        self.assertIsNone(item["controller_seconds"])

    def test_out_of_episode_launch_bounds_make_controller_time_unknown(self):
        for left, right in ((80, 90), (210, 220), (90, 110), (190, 210)):
            with self.subTest(interval=(left, right)):
                state = sample_state("BLOCKED")
                state["ended_at"] = iso(200)
                state["attempts"] = [{"id": "outside", "stage": "implementation",
                                      "started": iso(left), "launch_started": iso(left),
                                      "launch_finished": iso(right), "finished": iso(right),
                                      "elapsed_seconds": right - left, "status": "complete",
                                      "outcome": "finished", "usage": {}, "inputs": {}}]
                with tempfile.TemporaryDirectory() as temporary:
                    item = build(state, temporary)
                self.assertIsNone(item["controller_seconds"])

    def test_invalid_deadline_order_makes_both_deadline_intervals_unknown(self):
        for deadline, end in ((90, 120), (110, 100)):
            with self.subTest(deadline=deadline, end=end):
                state = sample_state("BLOCKED")
                state["deadline_started_epoch"] = deadline
                state["ended_at"] = iso(end)
                with tempfile.TemporaryDirectory() as temporary:
                    item = build(state, temporary)
                self.assertIsNone(item["pre_deadline_setup_seconds"])
                self.assertIsNone(item["execution_window_seconds"])

    def test_missing_configuration_identity_is_explicit_and_disclosed(self):
        state = sample_state("BLOCKED")
        state["host"] = {"name": None, "version": None, "executable": None}
        state["attempts"] = [state["attempts"][0]]
        with tempfile.TemporaryDirectory() as temporary:
            runtime = Path(temporary)
            (runtime / "attempts" / "pre-1").mkdir(parents=True)
            (runtime / "attempts" / "pre-1" / "launch.json").write_text('{"configuration": {}}')
            item = build(state, runtime)
        config = item["attempts"][0]["configuration"]
        self.assertEqual(config, {"host": None, "host_version": None, "controller": state["policy"],
                                  "tool": None, "model": None, "model_reasoning_effort": None})
        first, second = record("unknown-1", 10, 5, None), record("unknown-2", 12, 6, None)
        first["host_configurations"] = [config]
        second["host_configurations"] = [config]
        result = comparison.compare({"schema": EXPORT_SCHEMA, "episodes": [first, second]})
        unknowns = result["compatible_groups"][0]["configuration_unknowns"]
        self.assertEqual([row["episode_id"] for row in unknowns], ["unknown-1", "unknown-2"])
        self.assertEqual(unknowns[0]["fields"], ["host", "host_version", "model", "model_reasoning_effort", "tool"])

    def test_reversed_episode_bounds_make_episode_timing_unknown(self):
        state = sample_state("BLOCKED")
        state["ended_at"] = iso(90)
        with tempfile.TemporaryDirectory() as temporary:
            item = build(state, temporary)
        self.assertIsNone(item["elapsed_seconds"])
        self.assertIsNone(item["execution_window_seconds"])
        self.assertIsNone(item["controller_seconds"])

    def test_receipt_dedup_conflict_and_terminal_outcomes(self):
        state = sample_state()
        duplicate = dict(state["attempts"][0])
        state["attempts"].append(duplicate)
        with tempfile.TemporaryDirectory() as temporary:
            item = build(state, temporary)
        self.assertEqual(item["dispatch_count"], 3)
        state["attempts"].append(dict(duplicate, usage={"input_tokens": 99}))
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "conflicting duplicate"):
                build(state, temporary)
        for status, attempt_outcome, attempt_status, expected in [
                ("BLOCKED", "finished", "complete", "blocked"),
                ("BLOCKED", "failed", "failed", "failed"),
                ("BLOCKED", "interrupted", "failed", "interrupted"),
                ("REVIEWED_AND_PROVEN", "finished", "complete", "successful")]:
            case = sample_state(status)
            case["attempts"] = [dict(case["attempts"][0], outcome=attempt_outcome, status=attempt_status)]
            case["repair_used"] = expected == "successful"
            case["attempts"][0]["stage"] = "repair" if case["repair_used"] else "implementation"
            with tempfile.TemporaryDirectory() as temporary:
                item = build(case, temporary)
            self.assertEqual(item["terminal_outcome"], expected)
            self.assertEqual(item["repair_count"], int(expected == "successful"))
        state = sample_state()
        state["resume_count"] = 2
        before = build(state, ".")
        after = build(dict(state, resume_count=3), ".")
        self.assertEqual(before["episode_id"], after["episode_id"])
        self.assertEqual((before["dispatch_count"], after["dispatch_count"]), (3, 3))
        self.assertEqual(after["resume_count"], 3)

    def test_explicit_export_is_compact_and_never_overwrites(self):
        state = sample_state()
        with tempfile.TemporaryDirectory() as temporary:
            runtime = Path(temporary) / "runtime"
            runtime.mkdir()
            fixture_runtime(runtime, state)
            item = build(state, runtime)
            target = Path(temporary) / "saved.json"
            measurements.write_export(target, item)
            data = json.loads(target.read_text())
            self.assertEqual(data["schema"], EXPORT_SCHEMA)
            self.assertEqual(data["episodes"], [item])
            self.assertNotIn("PRIVATE RAW PROMPT", target.read_text())
            with self.assertRaisesRegex(ValueError, "already exists"):
                measurements.write_export(target, item)

    def test_deterministic_comparison_unknowns_config_and_external_adjudication(self):
        first = record("episode-a", 60, 30, "model-a")
        second = record("episode-b", 70, 35, "model-b")
        first["candidate_key"], first["candidate_generations"] = "snapshot:first", ["snapshot:first"]
        second["candidate_key"], second["candidate_generations"] = "snapshot:second", ["snapshot:second"]
        source = {"schema": EXPORT_SCHEMA, "episodes": [second, first]}
        one = comparison.compare(source)
        two = comparison.compare(source)
        self.assertEqual(one, two)
        self.assertEqual(len(one["compatible_groups"]), 1)
        group = one["compatible_groups"][0]
        self.assertEqual({row["elapsed_seconds"] for row in group["episodes"]}, {60, 70})
        self.assertEqual(group["configuration_differences"]["model"], ["model-a", "model-b"])
        self.assertEqual(group["candidate_identity_differences"], {
            "candidate_generations": [["snapshot:first"], ["snapshot:second"]],
            "candidate_key": ["snapshot:first", "snapshot:second"]})
        self.assertEqual({row["candidate_key"] for row in group["episodes"]},
                         {"snapshot:first", "snapshot:second"})
        self.assertIn("tokens:cached_input_tokens", group["unknowns"])
        self.assertIsNone(group["stages"]["implementation"][0]["tokens"]["cached_input_tokens"])
        self.assertEqual(group["stages"]["implementation"][0]["tokens"]["input_tokens"], 4)
        self.assertTrue(all(row["independent_outcome"] is None for row in group["episodes"]))
        source["independent_adjudications"] = {"episode-a": {"outcome": "satisfactory", "source": "held-out oracle"}}
        group = comparison.compare(source)["compatible_groups"][0]
        outcomes = {row["episode_id"]: row["independent_outcome"] for row in group["episodes"]}
        self.assertEqual(outcomes["episode-a"]["source"], "held-out oracle")
        self.assertIsNone(outcomes["episode-b"])
        source["episodes"].append(record("other-base", 50, 20, "model-c") | {"comparison_base": "e" * 40})
        separated = comparison.compare(source)
        self.assertEqual(len(separated["compatible_groups"]), 1)
        self.assertIn("other-base", separated["unmatched_episode_ids"])
        bad = dict(source)
        bad["episodes"] = [first]
        with self.assertRaisesRegex(ValueError, "at least two"):
            comparison.compare(bad)

    def test_missing_compatibility_identity_stays_unmatched(self):
        for field in ("repository_id", "work_item", "contract.revision", "contract.sha256", "comparison_base"):
            with self.subTest(field=field):
                episodes = [record("missing-a", 60, 30, "model-a"),
                            record("missing-b", 70, 35, "model-a")]
                for episode in episodes:
                    if field.startswith("contract."):
                        episode["contract"].pop(field.split(".", 1)[1])
                    else:
                        episode.pop(field)
                report = comparison.compare({"schema": EXPORT_SCHEMA, "episodes": episodes})
                self.assertEqual(report["compatible_groups"], [])
                self.assertEqual(report["unmatched_episode_ids"], ["missing-a", "missing-b"])

    def test_cross_repository_episodes_are_not_combined(self):
        episodes = [record("repo-a-1", 60, 30, "model-a"),
                    record("repo-a-2", 70, 35, "model-a"),
                    record("repo-b-1", 80, 40, "model-a")]
        episodes[-1]["repository_id"] = "repo-b-9a16da41f29d018b"
        result = comparison.compare({"schema": EXPORT_SCHEMA, "episodes": episodes})
        self.assertEqual(len(result["compatible_groups"]), 1)
        group = result["compatible_groups"][0]
        self.assertEqual(group["identity"]["repository_id"], "repo-a-d10c3299628ebf1e")
        self.assertEqual({row["episode_id"] for row in group["episodes"]}, {"repo-a-1", "repo-a-2"})
        self.assertEqual(result["unmatched_episode_ids"], ["repo-b-1"])

    def test_comparison_cli_reprocesses_identical_inputs(self):
        source = {"schema": EXPORT_SCHEMA, "episodes": [
            record("episode-a", 60, 30, "model-a"), record("episode-b", 70, 35, "model-a")]}
        script = CHECKS / "compare_p2p_delivery_measurements.py"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "input.json"
            path.write_text(json.dumps(source))
            first = subprocess.run([sys.executable, str(script), str(path)], capture_output=True, text=True)
            second = subprocess.run([sys.executable, str(script), str(path)], capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(json.loads(first.stdout)["compatible_groups"][0]["episodes"][0]["elapsed_seconds"], 60)

    def test_controller_measurement_is_observational_and_cleanup_does_not_require_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            home = temp / "home"
            home.mkdir()
            root = temp / "source"
            base = repo(root)
            fake = FakeTransport()
            with patch.dict(os.environ, {"HOME": str(home)}), patch.object(delivery, "launch", fake), \
                    fixture_host():
                output = io.StringIO()
                args = ["--repo", str(root), "run", ".p2p/work/tiny/contract.md",
                        "--comparison-base", base, "--authorize-local", "--destination", "delivery-target"]
                with contextlib.redirect_stdout(output):
                    code = delivery.main(args)
                result = json.loads(output.getvalue())
                self.assertEqual(code, 0, result)
                self.assertEqual(result["status"], "REVIEWED_AND_PROVEN")
                self.assertEqual([call for call in fake.calls],
                                 ["preflight", "preflight", "implementation", "review", "proof"])
                self.assertEqual(result["measurement"]["terminal_outcome"], "successful")
                self.assertEqual(result["measurement"]["repair_count"], 0)
                self.assertGreater(result["measurement"]["controller_breakdown_seconds"]
                                   ["identity_snapshot_validation"], 0)
                self.assertGreater(result["measurement"]["controller_breakdown_seconds"]
                                   ["persistence_readback"], 0)
                self.assertEqual(result["measurement"]["attempts"][2]["usage"]["input_tokens"], 7)
                self.assertIsNone(result["measurement"]["attempts"][2]["usage"]["cached_input_tokens"])
                target = temp / "selected-measurement.json"
                with contextlib.redirect_stdout(io.StringIO()):
                    export_code = exporter.main(["--repo", str(root), "--work",
                        ".p2p/work/tiny/contract.md", "--output", str(target)])
                self.assertEqual(export_code, 0)
                saved = json.loads(target.read_text())["episodes"][0]
                saved_state = json.loads((delivery.local_directory(root, ".p2p/work/tiny/contract.md") /
                                          "delivery.json").read_text())
                self.assertEqual(saved["episode_id"], result["invocation_id"])
                self.assertEqual(saved, result["measurement"])
                self.assertEqual(saved_state["completed_at"], saved["ended_at"])
                self.assertEqual(saved["elapsed_seconds"], result["measurement"]["elapsed_seconds"])
                self.assertEqual(saved["controller_breakdown_seconds"]["persistence_readback"],
                                 result["measurement"]["controller_breakdown_seconds"]["persistence_readback"])
                self.assertNotIn("FIXTURE TRANSPORT", target.read_text())
                del result["measurement"]
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = delivery.main(["--repo", str(root), "cleanup", ".p2p/work/tiny/contract.md"])
                self.assertEqual(code, 0, output.getvalue())
                self.assertTrue((delivery.delivery_paths(root, ".p2p/work/tiny/contract.md")[1] /
                                 "delivery.json").is_file())
                self.assertFalse((delivery.local_directory(root, ".p2p/work/tiny/contract.md") / "delivery.json").exists())

    def test_failed_terminal_measurement_write_does_not_claim_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            home = temp / "home"
            home.mkdir()
            root = temp / "source"
            base = repo(root)
            fake = FakeTransport()
            original_save = delivery.local_save
            finalization = {"armed": False}

            def fail_finalization(root, work, name, data):
                state = json.loads(data) if name == "delivery.json" else {}
                if (finalization["armed"] and state.get("status") == "REVIEWED_AND_PROVEN"
                        and state.get("completed_at")):
                    finalization["armed"] = False
                    raise OSError("fixture terminal write failure")
                saved = original_save(root, work, name, data)
                if name == "delivery.json" and state.get("final_proof") and state.get("status") == "RUNNING":
                    finalization["armed"] = True
                return saved

            with patch.dict(os.environ, {"HOME": str(home)}), patch.object(delivery, "launch", fake), \
                    fixture_host(), \
                    patch.object(delivery, "local_save", side_effect=fail_finalization):
                output = io.StringIO()
                args = ["--repo", str(root), "run", ".p2p/work/tiny/contract.md",
                        "--comparison-base", base, "--authorize-local", "--destination", "delivery-target"]
                with contextlib.redirect_stdout(output):
                    code = delivery.main(args)
                result = json.loads(output.getvalue())
                state_path = delivery.local_directory(root, ".p2p/work/tiny/contract.md") / "delivery.json"
                persisted = json.loads(state_path.read_text())
                self.assertEqual(code, 1)
                self.assertEqual(result["status"], "BLOCKED")
                self.assertEqual(persisted["status"], "BLOCKED")
                self.assertIsNone(persisted["completed_at"])

    def test_measurement_docs_limit_interpretation(self):
        docs = (CHECKS.parent / "docs/p2p-delivery-controller.md").read_text().lower()
        comparison_docs = (CHECKS.parent / "docs/delivery-strategy-comparison.md").read_text().lower()
        for text in (docs, comparison_docs):
            for phrase in ("observations", "monetary", "human effort", "independent"):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
