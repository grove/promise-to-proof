#!/usr/bin/env python3
"""Measure exact Git snapshot/generation overhead, without model calls.

Example: python3 checks/benchmark_p2p_git.py --baseline-ref HEAD --delivery
The optional delivery case uses the explicitly fake deterministic test transport.
Both variants use the current controller; --baseline-ref substitutes only the
historical Git/storage helpers, isolating the effect of this optimization.
"""
import argparse
import ast
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

import test_p2p_delivery as fixture

d = fixture.d
PROJECT = Path(__file__).resolve().parents[1]
SCRIPT_DIRECTORY = "skills/productivity/deliver-issue/scripts"


@contextlib.contextmanager
def historical_helpers(revision):
    replaced = []
    selections = [(d.fs, "p2p_filesystem.py", {"snapshot", "setup"}),
                  (d, "p2p_delivery.py", {"git_generation_tree", "local_directory",
                       "execution_runtime", "agreement_root", "local_storage_directory",
                       "delivery_paths", "local_save"})]
    try:
        for module, filename, names in selections:
            source = d.fs.git(PROJECT, "show", f"{revision}:{SCRIPT_DIRECTORY}/{filename}").decode()
            functions = {node.name: node for node in ast.parse(source).body
                         if isinstance(node, ast.FunctionDef)}
            for name in names:
                replaced.append((module, name, getattr(module, name)))
                tree = ast.Module(body=[functions[name]], type_ignores=[])
                exec(compile(tree, f"{revision}:{filename}", "exec"), module.__dict__)
        yield
    finally:
        for module, name, original in reversed(replaced):
            setattr(module, name, original)


def measure(action):
    original = subprocess.run
    git_processes = 0

    def run(args, *positional, **kwargs):
        nonlocal git_processes
        if args and args[0] == "git":
            git_processes += 1
        return original(args, *positional, **kwargs)

    started = time.perf_counter()
    with patch.object(subprocess, "run", side_effect=run):
        value = action()
    return value, {"elapsed_seconds": round(time.perf_counter() - started, 6),
                   "git_processes": git_processes}


def probe(commit, manifest, include_delivery):
    snapshot, snapshot_metrics = measure(lambda: d.fs.snapshot(PROJECT, commit))
    snapshot_metrics["snapshot_key"] = d.fs.snapshot_key(snapshot)
    with tempfile.TemporaryDirectory(prefix="p2p-git-benchmark-") as temporary:
        root = Path(temporary)
        d.fs.git(root, "init", "-q")
        tree, generation_metrics = measure(lambda: d.git_generation_tree(root, manifest))
        if d.fs.snapshot(root, tree) != manifest:
            raise AssertionError("generation changed the exact snapshot")
        generation_metrics["tree"] = tree
    result = {"snapshot": snapshot_metrics, "generation": generation_metrics}
    if include_delivery:
        def deliver():
            suite = unittest.defaultTestLoader.loadTestsFromName(
                "DeliveryTests.test_footprint_metrics_p2p_self_delivery", fixture)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as errors:
                outcome = unittest.TextTestRunner(stream=errors).run(suite)
            if not outcome.wasSuccessful():
                raise AssertionError(errors.getvalue())
        _, result["fixture_delivery"] = measure(deliver)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-ref", help="trusted repository revision containing the original helpers")
    parser.add_argument("--delivery", action="store_true", help="also run one offline complete delivery fixture")
    args = parser.parse_args()
    commit = d.fs.full_commit(PROJECT, "HEAD")
    manifest = d.fs.snapshot(PROJECT, commit)
    result = {"repository_commit": commit, "files": len(manifest), "live_model_calls": 0}
    if args.baseline_ref:
        with historical_helpers(args.baseline_ref):
            result["baseline"] = probe(commit, manifest, args.delivery)
    result["current"] = probe(commit, manifest, args.delivery)
    if args.baseline_ref:
        result["identical_snapshot"] = (result["baseline"]["snapshot"]["snapshot_key"] ==
                                        result["current"]["snapshot"]["snapshot_key"])
        result["identical_generation_tree"] = (result["baseline"]["generation"]["tree"] ==
                                               result["current"]["generation"]["tree"])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
