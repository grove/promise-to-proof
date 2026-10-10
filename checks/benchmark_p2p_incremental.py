#!/usr/bin/env python3
"""Matched offline incremental-work measurements with #59 stage receipts.

The fake host has no live model billing. This benchmark may validate reduced
controller work, NOT real Codex model-token savings or live judgment quality.
"""
import argparse
import ast
import contextlib
import io
import json
from pathlib import Path
import statistics
import subprocess
import time
from unittest.mock import patch

import test_p2p_delivery as fixture
import test_p2p_applicability as tests
import test_p2p_checkpoints as checkpoints

d = fixture.d
BASE = "324cafb462215abba499d24489c9f7d4e2ec671e"
PROJECT = Path(__file__).resolve().parents[1]
CONTROLLER = "skills/productivity/deliver-issue/scripts/p2p_delivery.py"


def historical_resume():
    source = d.fs.git(PROJECT, "show", f"{BASE}:{CONTROLLER}").decode()
    method = next(node for node in ast.parse(source).body
                  if isinstance(node, ast.FunctionDef) and node.name == "main")
    environment = dict(vars(d))
    exec(compile(ast.Module(body=[method], type_ignores=[]),
                 BASE + ":p2p_delivery.py", "exec"), environment)
    return environment["main"]


def completed_episode(*, original=False):
    case = fixture.DeliveryTests("test_clean_project_delivery_uses_local_contract_and_records")
    case.setUp()
    try:
        old_entry = historical_resume() if original else d.main
        work = ".p2p/work/tiny/contract.md"
        started = time.perf_counter()
        cold_code, cold = case.cli()
        cold_elapsed = time.perf_counter() - started
        if cold_code or cold["status"] != "REVIEWED_AND_PROVEN":
            raise AssertionError("cold baseline did not complete")
        expected_attempts = [a["stage"] for a in case.state()["attempts"]]
        if expected_attempts != ["preflight-1", "preflight-2", "implementation", "review", "proof"]:
            raise AssertionError("baseline does not have equivalent full stages")
        local = d.local_directory(case.root, work)
        data = local / "delivery.json"
        checkpoint = case.root / "p2p-state/tiny.json"
        original_records = (data.read_bytes(), checkpoint.read_bytes())
        initial_calls = len(case.fake.calls)
        file_writes, git_launches = [], []
        real_save = d.local_save
        real_run = subprocess.run

        def save(*args, **kwargs):
            file_writes.append(str(args[2]))
            return real_save(*args, **kwargs)

        def run(args, *position, **kwargs):
            if isinstance(args, (tuple, list)) and args and args[0] == "git":
                git_launches.append(tuple(args))
            return real_run(args, *position, **kwargs)

        stream = io.StringIO()
        with (patch.object(d, "local_save", side_effect=save),
              patch.object(subprocess, "run", side_effect=run),
              contextlib.redirect_stdout(stream), contextlib.redirect_stderr(io.StringIO())):
            t = time.perf_counter()
            result_code = old_entry(["--repo", str(case.root), "resume", work])
            elapsed = time.perf_counter() - t
        result = json.loads(stream.getvalue())
        if result_code or result["status"] != "REVIEWED_AND_PROVEN":
            raise AssertionError("same-state resume was not accepted: " + str(result.get("blocker")))
        if initial_calls != len(case.fake.calls):
            raise AssertionError("a completed resume launched another model-stage worker")
        if [a["stage"] for a in case.state()["attempts"]] != expected_attempts:
            raise AssertionError("a resumed delivery regenerated stage attempts")
        if case.state()["candidate"]["key"] != cold["candidate"]["key"]:
            raise AssertionError("warm resume changed exact product")
        if not original:
            if file_writes or original_records != (data.read_bytes(), checkpoint.read_bytes()):
                raise AssertionError("unchanged fast resume rewrote canonical state/checkpoint")
        return {
            "cold_seconds": round(cold_elapsed, 6),
            "resume_seconds": round(elapsed, 6),
            "resume_git_processes": len(git_launches),
            "resume_canonical_writes": len(file_writes),
            "resume_checkpoint_changed": original_records[1] != checkpoint.read_bytes(),
            "new_model_calls": len(case.fake.calls)-initial_calls,
            "stages": expected_attempts,
            "candidate_key": case.state()["candidate"]["key"],
            "completion": result["status"],
            "checkpoint_status": cold["checkpoint"]["status"],
            "reuse": result.get("reuse", {}).get("status"),
            "cold_measurement": cold["measurement"],
        }
    finally:
        case.tearDown()


def restored_episode():
    test = checkpoints.CheckpointTests(
        "test_completed_stage_resumes_on_another_computer_without_old_execution")
    test.setUp()
    captures = []
    original = test.fixture.run_root

    def observe(*args, **kwargs):
        code, value = original(*args, **kwargs)
        if args[3] == "resume":
            captures.append((code, value))
        return code, value

    try:
        with patch.object(test.fixture, "run_root", side_effect=observe):
            t = time.perf_counter()
            test.test_completed_stage_resumes_on_another_computer_without_old_execution()
            duration = time.perf_counter() - t
        if len(captures) != 1 or captures[0][0]:
            raise AssertionError("portable receiving-host continuation did not succeed")
        value = captures[0][1]
        stages = [row["stage"] for row in value["attempts"]]
        if (stages.count("prior-preflight-1") != 1 or stages.count("preflight-1") != 1
                or stages.count("preflight-2") != 1 or
                stages.count("implementation") != 1 or stages.count("review") != 1 or
                stages.count("proof") != 1):
            raise AssertionError("restored continuation repeated work or skipped receiving preflight")
        return {"elapsed_seconds": round(duration, 6),
                "retained_stage_receipts": len(stages),
                "fresh_receiving_host_model_calls": 3,
                "fresh_receiving_host_preflights": 2, "new_implementation_calls": 0,
                "new_review_calls": 0, "new_proof_calls": 1,
                "status": value["status"],
                "measurement": value.get("measurement"),
                "live_model_tokens": None, "live_model_cost": None}
    finally:
        test.tearDown()


def changed_episode():
    actor = tests.OfflineSelectiveTransport
    original = actor.__call__
    stages, advice = [], []
    old_history = d.Delivery.verification_history

    def launch(self, args, prompt, events, *other, **kwargs):
        stage = json.loads((events.parent / "launch.json").read_text())["stage"]
        stages.append(stage)
        return original(self, args, prompt, events, *other, **kwargs)

    def history(self, name):
        result = old_history(self, name)
        if result and result.get("applicability"):
            advice.append(result["applicability"])
        return result

    test = tests.ChangeScopeControllerTests(
        "test_changed_candidate_runs_fresh_independent_full_conclusions_and_selective_checks")
    with (patch.object(actor, "__call__", launch),
          patch.object(d.Delivery, "verification_history", history)):
        started = time.perf_counter()
        test.test_changed_candidate_runs_fresh_independent_full_conclusions_and_selective_checks()
        elapsed = time.perf_counter() - started
    selected = [a for a in advice if a["status"] == "SELECTIVE"]
    if stages != ["review", "proof", "review", "proof"] or len(selected) < 2:
        raise AssertionError("changed product did not receive new full independent stage judgments")
    return {"elapsed_seconds": round(elapsed, 6),
            "model_stage_calls": len(stages), "fresh_after_delta": len(stages)//2,
            "potentially_reusable_observations": len(selected[-1]["potentially_reusable"]),
            "refreshed_requirements": selected[-1]["refresh_requirements"],
            "reused_verdicts": 0, "live_model_tokens": None, "live_model_cost": None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=2)
    args = parser.parse_args()
    if not 1 <= args.repeats <= 4:
        parser.error("repeats must be 1–4")
    baseline, optimized = [], []
    for i in range(args.repeats):
        order = [True, False] if i % 2 == 0 else [False, True]
        for old in order:
            (baseline if old else optimized).append(completed_episode(original=old))
    for old, new in zip(baseline, optimized):
        if (old["stages"] != new["stages"] or old["completion"] != new["completion"] or
                old["new_model_calls"] != new["new_model_calls"] or
                old["checkpoint_status"] != new["checkpoint_status"]):
            raise AssertionError("before/after stages, proof or portability differ")
    before = statistics.median(x["resume_seconds"] for x in baseline)
    after = statistics.median(x["resume_seconds"] for x in optimized)
    report = {
        "schema": "promise-to-proof/incremental-measurement/v1",
        "baseline_commit": BASE, "repeats": args.repeats,
        "host": "offline test transport (no live model calls)",
        "unchanged": {"baseline": baseline, "optimized": optimized,
                      "median_baseline_seconds": round(before, 6),
                      "median_optimized_seconds": round(after, 6),
                      "saved_controller_writes": statistics.median(x["resume_canonical_writes"] for x in baseline),
                      "optimized_canonical_writes": 0},
        "restored": restored_episode(),
        "changed_candidate": changed_episode(),
        "token_cost": None, "live_model_time": None,
        "human_interventions_observed": 0,
        "claim_limits": ["Simulated workers; no live model latency or token/cost savings are established.",
                         "Restored continuation still runs a fresh receiving-host preflight.",
                         "Changed candidate has fresh full review and proof on both stages."]
    }
    print(json.dumps(report, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
