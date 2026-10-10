#!/usr/bin/env python3
"""Matched, offline cold-delivery timing. Never interpreted as live model speed.

Before/after replaces Delivery._capture, Delivery.source_stable, and the
checkpoint writer with their exact pre-change versions from issue #57 main.
All other host, skill, preflight, verification, and recovery code stays identical. Source and
candidate outcomes are checked. No live model calls are made.
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

from test_p2p_delivery import d, DeliveryTests

BASE = "3582eb48cae660e8ff6f4ad759e0988760a174e2"
PROJECT = Path(__file__).resolve().parents[1]
SOURCE = "skills/productivity/deliver-issue/scripts/p2p_delivery.py"


def historical_method(name):
    text = d.fs.git(PROJECT, "show", f"{BASE}:{SOURCE}").decode()
    module = ast.parse(text)
    cls = next(item for item in module.body if isinstance(item, ast.ClassDef)
               and item.name == "Delivery")
    method = next(item for item in cls.body if isinstance(item, ast.FunctionDef)
                  and item.name == name)
    namespace = dict(vars(d))
    exec(compile(ast.Module(body=[method], type_ignores=[]),
                 BASE + ":" + SOURCE, "exec"), namespace)
    return namespace[name]


def historical_checkpoint():
    source = d.fs.git(PROJECT, "show", f"{BASE}:skills/productivity/deliver-issue/scripts/p2p_filesystem.py").decode()
    module = ast.parse(source)
    function = next(item for item in module.body
                    if isinstance(item, ast.FunctionDef) and item.name == "checkpoint")
    namespace = dict(vars(d.fs))
    exec(compile(ast.Module(body=[function], type_ignores=[]),
                 BASE + ":p2p_filesystem.py", "exec"), namespace)
    return namespace["checkpoint"]


def episode(use_historical=False):
    case = DeliveryTests("test_clean_project_delivery_uses_local_contract_and_records")
    case.setUp()
    original_run = subprocess.run
    original_snapshot = d.fs.snapshot
    original_checkpoint = d.Delivery.checkpoint
    original_fs_checkpoint = d.fs.checkpoint
    original_capture = d.Delivery._capture
    original_source_stable = d.Delivery.source_stable
    stats = {"git_processes": 0, "snapshots": 0, "checkpoint_calls": 0,
             "checkpoint_seconds": 0., "capture_seconds": 0.,
             "source_stable_seconds": 0.}
    def run(args, *positional, **kwargs):
        if isinstance(args, (list, tuple)) and args and args[0] == "git":
            stats["git_processes"] += 1
        return original_run(args, *positional, **kwargs)
    def snapshot(*args, **kwargs):
        stats["snapshots"] += 1
        return original_snapshot(*args, **kwargs)
    def checkpoint(self):
        t = time.monotonic()
        try:
            result = original_checkpoint(self)
            if result["status"] != "LOCAL_ONLY":
                raise AssertionError("portable checkpoint failed in a successful delivery: " + str(result))
            return result
        finally:
            stats["checkpoint_calls"] += 1
            stats["checkpoint_seconds"] += time.monotonic() - t
    capture_fn = historical_method("_capture") if use_historical else original_capture
    stable_fn = historical_method("source_stable") if use_historical else original_source_stable
    fs_checkpoint_fn = historical_checkpoint() if use_historical else original_fs_checkpoint
    def capture(self, *args, **kwargs):
        t = time.monotonic()
        try:
            return capture_fn(self, *args, **kwargs)
        finally:
            stats["capture_seconds"] += time.monotonic() - t
    def stable(self):
        t = time.monotonic()
        try:
            return stable_fn(self)
        finally:
            stats["source_stable_seconds"] += time.monotonic() - t

    try:
        with (patch.object(subprocess, "run", side_effect=run),
              patch.object(d.fs, "snapshot", side_effect=snapshot),
              patch.object(d.Delivery, "checkpoint", checkpoint),
              patch.object(d.fs, "checkpoint", fs_checkpoint_fn),
              patch.object(d.Delivery, "_capture", capture),
              patch.object(d.Delivery, "source_stable", stable),
              contextlib.redirect_stderr(io.StringIO())):
            t = time.monotonic()
            code, value = case.cli()
            stats["elapsed_seconds"] = time.monotonic() - t
        if code or value["status"] != "REVIEWED_AND_PROVEN":
            raise AssertionError("fixture delivery failed: " + str(value.get("blocker")))
        state = case.state()
        before = len(state["attempts"])
        stages = [x["stage"] for x in state["attempts"]]
        expected_stages = ["preflight-1", "preflight-2", "implementation", "review", "proof"]
        if stages != expected_stages or len(case.fake.calls) != before:
            raise AssertionError("changed controller stages, verifier calls or host preflight")
        for stage in ("review", "proof"):
            if state["reports"][stage]["inputs"] != d.Delivery(case.root, case.work if hasattr(case, "work")
                                                               else ".p2p/work/tiny/contract.md",
                                                               state).stage_inputs(state["candidate"]):
                raise AssertionError("changed review/proof candidate identity")
        stats.update({"snapshot_key": state["candidate"]["key"],
                      "stage_sequence": stages, "fixture_calls": list(case.fake.calls),
                      "report_statuses": {n: d.Delivery(case.root, ".p2p/work/tiny/contract.md", state)
                                          .read_report(n)["status"] for n in ("review", "proof")},
                      "checkpoint_status": state["checkpoint"]["status"],
                      "checkpoint_bytes": state["checkpoint"]["bytes"],
                      "measurement": value["measurement"],
                      "model_calls": 0})
        return stats
    finally:
        case.tearDown()


def compare(baseline, optimized):
    def med(name, entries):
        return round(statistics.median(item[name] for item in entries), 6)
    fingerprint = ("snapshot_key", "stage_sequence", "fixture_calls", "report_statuses",
                   "checkpoint_status", "model_calls")
    for old, new in zip(baseline, optimized):
        for key in fingerprint:
            if old[key] != new[key]:
                raise AssertionError(f"baseline/optimized mismatch for {key}: {old[key]} vs {new[key]}")
    fields = ("elapsed_seconds", "git_processes", "snapshots", "checkpoint_calls",
              "checkpoint_seconds", "capture_seconds", "source_stable_seconds")
    before = {k: med(k, baseline) for k in fields}
    after = {k: med(k, optimized) for k in fields}
    if after["snapshots"] >= before["snapshots"] or after["git_processes"] > before["git_processes"]:
        raise AssertionError("first-pass optimization did not remove measured redundant work")
    if after["checkpoint_calls"] != before["checkpoint_calls"]:
        raise AssertionError("optimization changed durable checkpoint boundaries")
    return {"baseline": before, "optimized": after,
            "elapsed_saved_percent": (round(100 * (before["elapsed_seconds"]-after["elapsed_seconds"]) /
                                            before["elapsed_seconds"], 1)
                                      if before["elapsed_seconds"] else None),
            "same_full_verification": True,
            "live_model_calls": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--baseline-only", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.repeats <= 10:
        parser.error("repeats must be between 1 and 10")
    # Alternate order within the same runner to reduce cold-cache and
    # scheduling bias. Each episode is still a newly admitted repository.
    before, after, order = [], [], []
    for index in range(args.repeats):
        stages = ["baseline"] if args.baseline_only else (
            ["baseline", "optimized"] if index % 2 == 0 else ["optimized", "baseline"])
        for stage in stages:
            order.append(stage)
            if stage == "baseline":
                before.append(episode(True))
            else:
                after.append(episode(False))
    result = {"schema": "promise-to-proof/first-pass-comparison/v1",
              "baseline_commit": BASE, "repeats": args.repeats,
              "order": order, "fresh_repository_per_episode": True,
              "host": "offline Linux/fixture transport; not live Codex",
              "baseline_samples": before,
              "model_time": None, "model_tokens": None, "model_cost": None}
    if not args.baseline_only:
        result["optimized_samples"] = after
        result["comparison"] = compare(before, after)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
