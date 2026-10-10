"""Delivery Record v1: historical local acceptance and exact landed-code mapping.

Offline disposable Git transport only; no live model, remote effects, or CI oracle.
"""
import base64
import copy
import datetime
import json
from pathlib import Path
import subprocess
import sys
import unittest

import test_p2p_delivery as fixture

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "skills/productivity/deliver-issue/scripts"))
import p2p_delivery_record as record_protocol


class DeliveryRecordTests(unittest.TestCase):
    def setUp(self):
        self.item = fixture.DeliveryTests("test_clean_project_delivery_uses_local_contract_and_records")
        self.item.setUp()
        self.addCleanup(self.item.tearDown)
        self.root, self.base = self.item.root, self.item.base
        self.work = ".p2p/work/tiny/contract.md"
        code, output = self.item.cli()
        self.assertEqual(code, 0, output)
        self.state = self.item.state()
        self.local = fixture.d.Delivery(self.root, self.work, self.state)
        self.original = self.local.final_record()
        self.checkpoint = (self.root / "p2p-state/tiny.json").read_bytes()
        self.index, self.contents = fixture.d.fs.read_checkpoint(self.root, self.checkpoint)
        self.candidate_commit = self.index["candidate_commit"]

    def git(self, *args):
        return fixture.d.fs.git(self.root, *args).decode().strip()

    def snapshot(self, rev):
        return fixture.d.fs.snapshot(self.root, rev)

    def commit(self, manifest, parents, description):
        tree = fixture.d.git_generation_tree(self.root, manifest)
        args = ["-c", "user.name=Fixture", "-c", "user.email=test@example.invalid",
                "commit-tree", tree]
        for parent in parents:
            args += ["-p", parent]
        return self.git(*args, "-m", description)

    @staticmethod
    def addition(path, data):
        return {"path": path, "type": "file", "mode": "100644",
                "content_base64": base64.b64encode(data).decode()}

    def landed(self, method, pr=False):
        before = self.base
        # An unrelated change may have been merged since the review's frozen base.
        if method in ("merge", "squash", "rebase"):
            manifest = self.snapshot(self.base)
            manifest.append(self.addition("unrelated.txt", b"independent upstream work\n"))
            before = self.commit(manifest, [self.base], "Earlier unrelated target work")
        candidate = self.snapshot(self.candidate_commit)
        after_manifest = {e["path"]: e for e in self.snapshot(before)}
        # Apply the exact complete reviewed candidate delta to the newer target.
        changes = self.state["candidate"]["changes"]
        candidate_by_path = {e["path"]: e for e in candidate}
        for row in changes:
            if row["state"] == "deleted":
                after_manifest.pop(row["path"], None)
            else:
                after_manifest[row["path"]] = candidate_by_path[row["path"]]
        final_tree = sorted(after_manifest.values(), key=lambda e:e["path"])
        if method == "merge":
            after = self.commit(final_tree, [before, self.candidate_commit], "Merge reviewed change")
        elif method in ("squash", "direct"):
            after = self.commit(final_tree, [before], "Satisfy reviewed change")
        elif method == "rebase":
            mid = self.commit(self.snapshot(before), [before], "First rebased step")
            after = self.commit(final_tree, [mid], "Final rebased step")
        elif method == "integrated":
            # The assembled parent is already on the final destination; this test
            # supplies an explicit parent contract separately.
            after = before
        else:
            raise AssertionError(method)
        self.git("update-ref", "refs/heads/delivery-target", after)
        arguments = dict(checkpoint=self.checkpoint, method=method,
                         repository="owner/repo", destination_ref="refs/heads/delivery-target",
                         before=before, after=after,
                         confirmed_at="2026-10-10T12:00:00+00:00")
        if pr:
            arguments.update(pull_request="https://github.com/owner/repo/pull/42",
                             pr_head=self.candidate_commit,
                             merged_at="2026-10-10T12:00:01+00:00")
        return record_protocol.preview(self.root, self.original, **arguments), arguments

    def test_unmodified_local_only_record_preserves_old_meaning(self):
        observed = record_protocol.validate(self.root, self.original, checkpoint=self.checkpoint)
        self.assertEqual(observed["status"], "LOCAL_REVIEWED_PROVEN")
        self.assertNotIn("landing", self.original)
        self.assertIn("No delivered commit", record_protocol.render(self.original, observed))

    def test_compact_cleaned_local_artifacts_validate_without_runtime_or_checkpoint(self):
        code, result = self.item.cli("cleanup")
        self.assertEqual(code, 0, result)
        path = self.root / ".p2p/work/tiny/artifacts"
        record = json.loads((path / "delivery.json").read_bytes())
        self.assertEqual(record_protocol.validate(self.root, record, artifact_directory=path)["status"],
                         "LOCAL_REVIEWED_PROVEN")
        changed = copy.deepcopy(record)
        changed["review_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "review/proof"):
            record_protocol.validate(self.root, changed, artifact_directory=path)

    def test_full_two_parent_merge_preserves_unrelated_target_changes(self):
        completed, _ = self.landed("merge", pr=True)
        observed = record_protocol.validate(self.root, completed, checkpoint=self.checkpoint)
        self.assertEqual(observed["status"], "LANDED_MAPPING_VERIFIED")
        self.assertEqual(observed["method"], "merge")
        self.assertEqual(observed["pull_request"], "https://github.com/owner/repo/pull/42")
        self.assertFalse(observed["receipt_published"])
        self.assertIn("receipt", record_protocol.render(completed, observed))

    def test_squash_merge_and_rebased_sequence(self):
        for method in ("squash", "rebase"):
            with self.subTest(method=method):
                completed, _ = self.landed(method, pr=True)
                observed = record_protocol.validate(self.root, completed, checkpoint=self.checkpoint)
                self.assertEqual(observed["method"], method)

    def test_issue_less_direct_delivery_with_no_pr(self):
        completed, _ = self.landed("direct")
        self.assertIsNone(completed["landing"]["pull_request"])
        self.assertEqual(record_protocol.validate(
            self.root, completed, checkpoint=self.checkpoint)["method"], "direct")

    def test_idempotent_retry_changes_neither_event_nor_receipt(self):
        completed, args = self.landed("squash")
        repeated = record_protocol.preview(self.root, completed,
                                           **(args | {"confirmed_at": "2026-10-11T20:30:00Z"}))
        self.assertEqual(completed, repeated)
        fresh = record_protocol.preview(self.root, self.original,
                                        **(args | {"confirmed_at": "2026-10-11T20:30:00Z"}))
        self.assertEqual(fresh["landing"]["receipt_id"], completed["landing"]["receipt_id"])
        self.assertEqual(fresh["landing"]["event_id"], completed["landing"]["event_id"])
        self.assertNotEqual(fresh["landing"]["confirmed_at"], completed["landing"]["confirmed_at"])

    def test_candidate_product_overlap_does_not_sneak_into_landed_tree(self):
        completed, _ = self.landed("squash")
        bad = copy.deepcopy(completed)
        bad["candidate_changes_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "changed-path scope|identity"):
            record_protocol.validate(self.root, bad, checkpoint=self.checkpoint)

    def test_changed_contract_binding_and_checkpoint_are_rejected(self):
        completed, _ = self.landed("squash")
        for mutated, expected in (
            ({"contract": {**completed["contract"], "sha256": "f"*64}}, "contract"),
            ({"binding_inputs": []}, "binding"),
            ({"review_sha256": "e"*64}, "review/proof"),
        ):
            with self.subTest(expected=expected):
                with self.assertRaises(ValueError):
                    record_protocol.validate(self.root, {**completed, **mutated},
                                             checkpoint=self.checkpoint)
        changed = copy.deepcopy(completed)
        changed["landing"]["checkpoint_sha256"] = "f"*64
        with self.assertRaisesRegex(ValueError, "checkpoint"):
            record_protocol.validate(self.root, changed, checkpoint=self.checkpoint)

    def test_report_identity_and_requirement_coverage_must_be_independent(self):
        completed, _ = self.landed("squash")
        bad_cp = copy.deepcopy(self.index)
        state = bad_cp["execution"]
        self.assertTrue(state["reports"])
        state["reports"]["review"]["inputs"]["key"] = "snapshot:sha256:" + "0"*64
        # The source execution boundary is semantically inconsistent with the
        # checkpoint stage receipts; this is never an acceptable completed claim.
        with self.assertRaises(ValueError):
            record_protocol.validate(self.root, completed,
                                     checkpoint=fixture.d.fs.canonical(bad_cp)+b"\n")

    def test_ambiguous_external_changed_path_is_rejected(self):
        completed, _ = self.landed("squash")
        before = completed["landing"]["destination"]["before"]
        changed = {e["path"]: e for e in self.snapshot(before)}
        changed["greet.py"] = self.addition("greet.py", b"unreviewed edit\n")
        overlap = self.commit(list(changed.values()), [self.base], "Conflicting upstream edit")
        final = {e["path"]: e for e in self.snapshot(overlap)}
        final["greet.py"] = next(e for e in self.snapshot(self.candidate_commit) if e["path"] == "greet.py")
        after = self.commit(list(final.values()), [overlap], "Overwrite target overlap")
        self.git("update-ref", "refs/heads/delivery-target", after)
        with self.assertRaisesRegex(ValueError, "overlapping destination change"):
            record_protocol.preview(self.root, self.original, checkpoint=self.checkpoint,
                                    method="squash", repository="owner/repo",
                                    destination_ref="refs/heads/delivery-target", before=overlap,
                                    after=after, confirmed_at="2026-10-10T12:00:00Z")

    def test_fabricated_destination_ref_or_incomplete_commit_mapping_rejected(self):
        completed, _ = self.landed("merge", pr=True)
        changed = copy.deepcopy(completed)
        changed["landing"]["destination"]["ref"] = "refs/heads/wrong"
        with self.assertRaisesRegex(ValueError, "destination"):
            record_protocol.validate(self.root, changed, checkpoint=self.checkpoint)
        changed = copy.deepcopy(completed)
        changed["landing"]["pull_request"]["head"] = self.base
        with self.assertRaisesRegex(ValueError, "PR head"):
            record_protocol.validate(self.root, changed, checkpoint=self.checkpoint)

    def test_a_checkpoint_reference_cannot_certify_unretrievable_evidence(self):
        completed, _ = self.landed("direct")
        broken = copy.deepcopy(completed)
        broken["landing"]["evidence_refs"] = [
            {"scope": "runtime", "path": "evidence/missing.json", "sha256": "f"*64}]
        with self.assertRaisesRegex(ValueError, "evidence reference"):
            record_protocol.validate(self.root, broken, checkpoint=self.checkpoint)


if __name__ == "__main__":
    unittest.main()
