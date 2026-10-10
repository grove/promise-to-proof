"""Focused speed-path regressions: preserve exact trust boundaries and outcomes.

The fake-host delivery below is a controller test, not live macOS/Codex evidence.
"""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import benchmark_p2p_first_pass as benchmark
import test_p2p_delivery as fixture

d, repo = fixture.d, fixture.repo


class CaptureFastPathTests(unittest.TestCase):
    def test_reused_snapshots_preserve_public_capture_semantics_and_git_objects(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            base = repo(root)
            (root / "app.py").write_text("print('hello')\n")
            (root / "link").symlink_to("app.py")
            (root / "executable").write_text("echo ok\n")
            (root / "executable").chmod(0o755)
            work = ".p2p/work/tiny/contract.md"
            exclude = {work}
            base_entries = d.fs.snapshot(root, base)
            actual_entries = d.fs.snapshot(root)
            before = d.fs.git(root, "for-each-ref")
            index = d.fs.git(root, "ls-files", "--stage", "-z")
            product = [row for row in actual_entries if row["path"] not in exclude]
            product_base = [row for row in base_entries if row["path"] not in exclude]
            with patch.object(d.fs, "snapshot", wraps=d.fs.snapshot) as snapshots:
                optimized = d.fs.capture(root, work, base, exclude=exclude,
                                         prepared=(product, product_base))
                optimized_scans = snapshots.call_count
            expected = d.fs.capture(root, work, base, exclude=exclude)
            self.assertEqual(optimized, expected)
            self.assertEqual(optimized["changes"], d.fs.tree_changes(product_base, product))
            self.assertEqual(optimized["key"], d.fs.snapshot_key(product))
            self.assertEqual({e["mode"] for e in product if e["path"] == "executable"}, {"100755"})
            self.assertEqual({e["type"] for e in product if e["path"] == "link"}, {"symlink"})
            self.assertLessEqual(optimized_scans, 1)
            self.assertEqual(before, d.fs.git(root, "for-each-ref"))
            self.assertEqual(index, d.fs.git(root, "ls-files", "--stage", "-z"))
            self.assertEqual(d.fs.snapshot(root), actual_entries)

    def test_prepared_input_never_bypasses_staged_index_validation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            base = repo(root)
            work = ".p2p/work/tiny/contract.md"
            (root / "spec.txt").write_text("staged version\n")
            d.fs.git(root, "add", "spec.txt")
            (root / "spec.txt").write_text("different unstaged version\n")
            prepared = (d.fs.snapshot(root, exclude=(work,)),
                        d.fs.snapshot(root, base, exclude=(work,)))
            with self.assertRaisesRegex(ValueError, "partially staged"):
                d.fs.capture(root, work, base, exclude=(work,), prepared=prepared)


class NormalDeliveryFastPathTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture.DeliveryTests("test_clean_project_delivery_uses_local_contract_and_records")
        self.fixture.setUp()

    def tearDown(self):
        self.fixture.tearDown()

    def test_unchanged_source_skips_redundant_head_snapshot_but_detects_source_drift(self):
        self.assertEqual(self.fixture.cli()[0], 0)
        state = self.fixture.state()
        delivery = d.Delivery(self.fixture.root, ".p2p/work/tiny/contract.md", state)
        with patch.object(d.fs, "snapshot", wraps=d.fs.snapshot) as snapshots:
            delivery.source_stable()
            source_checks = [call for call in snapshots.call_args_list
                             if call.args and call.args[0] == self.fixture.root]
        self.assertEqual(len(source_checks), 1, source_checks)
        self.assertEqual(source_checks[0].args, (self.fixture.root,))
        (self.fixture.root / "spec.txt").write_text("changed source\n")
        with self.assertRaisesRegex(ValueError, "source checkout changed"):
            delivery.source_stable()

    def test_matching_review_proof_and_portable_checkpoint_survive_capture_optimization(self):
        code, output = self.fixture.cli()
        self.assertEqual(code, 0, output.get("blocker"))
        state = self.fixture.state()
        self.assertEqual([a["stage"] for a in state["attempts"]],
                         ["preflight-1", "preflight-2", "implementation", "review", "proof"])
        self.assertEqual(state["reports"]["review"]["inputs"],
                         state["reports"]["proof"]["inputs"])
        self.assertEqual(state["checkpoint"]["status"], "LOCAL_ONLY")
        self.assertEqual(state["candidate"]["key"],
                         state["local_git_generations"][-1]["candidate_key"])
        self.assertEqual(output["status"], "REVIEWED_AND_PROVEN")
        self.assertEqual({name: d.Delivery(self.fixture.root, ".p2p/work/tiny/contract.md", state)
                          .read_report(name)["status"] for name in ("review", "proof")},
                         {"review": "REVIEWED", "proof": "PROVEN"})

    def test_old_and_new_checkpoint_writers_produce_identical_portable_bytes(self):
        self.assertEqual(self.fixture.cli()[0], 0)
        root = self.fixture.root
        work = ".p2p/work/tiny/contract.md"
        state = self.fixture.state()
        delivery = d.Delivery(root, work, state)
        target = root / "p2p-state/tiny.json"
        original_writer = benchmark.historical_checkpoint()
        real_run = d.subprocess.run

        def measured(writer):
            launches = []
            def run(args, *positional, **kwargs):
                if isinstance(args, (list, tuple)) and args and args[0] == "git":
                    launches.append(list(args))
                return real_run(args, *positional, **kwargs)
            with patch.object(d.subprocess, "run", side_effect=run), patch.object(
                    d.fs, "checkpoint", writer):
                result = d.export_checkpoint(root, work, delivery=delivery)
            self.assertEqual(result["status"], "LOCAL_ONLY")
            payload = target.read_bytes()
            d.fs.read_checkpoint(root, payload)
            return payload, launches

        before, old_launches = measured(original_writer)
        after, new_launches = measured(d.fs.checkpoint)
        self.assertEqual(before, after)
        self.assertGreater(len(old_launches), len(new_launches))
        self.assertEqual(json.loads(before)["required_commits"],
                         json.loads(after)["required_commits"])
        self.assertTrue(any("attempts/" in args[-1] for args in old_launches))

    def test_comparator_rejects_a_fake_speedup_that_skips_verification(self):
        a = {"snapshot_key": "k", "stage_sequence": ["implementation", "review", "proof"],
             "fixture_calls": ["implementation", "review", "proof"],
             "report_statuses": {"review": "REVIEWED", "proof": "PROVEN"},
             "checkpoint_status": "LOCAL_ONLY", "model_calls": 0}
        durations = {"elapsed_seconds": 3., "git_processes": 10,
                     "snapshots": 10, "checkpoint_calls": 4,
                     "checkpoint_seconds": .5, "capture_seconds": .3,
                     "source_stable_seconds": .8}
        before = a | durations
        optimized = before | {"elapsed_seconds": 1., "stage_sequence": ["implementation", "review"]}
        with self.assertRaisesRegex(AssertionError, "stage_sequence"):
            benchmark.compare([before], [optimized])


if __name__ == "__main__":
    unittest.main()
