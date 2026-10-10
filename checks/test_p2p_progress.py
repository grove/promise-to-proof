#!/usr/bin/env python3
"""Meaning-based, offline tests for trustworthy P2P progress explanations."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/productivity/deliver-issue/scripts"
sys.path.insert(0, str(SCRIPTS))
import p2p_progress as progress
import p2p_filesystem as fs
import test_p2p_delivery as fixture


KEY = "snapshot:sha256:" + "a" * 64
CONTRACT = "b" * 64
WORK = ".p2p/work/demo/contract.md"
PR = "https://github.com/owner/repository/pull/15"
SOURCE = {
    "status": "RUNNING",
    "blocker": None,
    "work_item": WORK,
    "candidate": {"key": KEY},
    "contract": {"sha256": CONTRACT, "revision": "v1", "source": "demo"},
    "agreement_paths": [WORK],
    "candidate_workspace": "/isolated/workspace",
    "routing": {"target_ref": "refs/heads/main", "destination": "main"},
    "progress": {"stage": "implementation", "controller_running": False,
                 "last_activity_at": "2026-10-01T11:00:00+00:00"},
    "attempts": [], "reports": {},
}


def report(**changes):
    data = dict(SOURCE)
    data.update(changes)
    return data


def publication(status="OPEN"):
    return {"status": status, "verified": True, "url": PR,
            "target": "main", "head_sha": "1" * 40,
            "is_draft": True, "merge_commit": "2" * 40 if status == "MERGED" else None}


class ExplanationTests(unittest.TestCase):
    def test_local_proven_is_not_published_or_in_operator_checkout(self):
        saved = report(status="REVIEWED_AND_PROVEN")
        before = json.dumps(saved, sort_keys=True)
        first = progress.explain(saved)
        self.assertEqual(first, progress.explain(saved))
        self.assertEqual(json.dumps(saved, sort_keys=True), before)
        self.assertEqual(first["phase"], "LOCAL_REVIEWED_PROVEN")
        self.assertIn("independent review and proof", first["message"].lower())
        self.assertIn("does not commit, publish, merge", first["message"])
        self.assertIn("isolated", first["where_is_the_code"])
        self.assertFalse(first["requires_user_action"])
        self.assertNotIn("fully finalized", first["message"].lower())

    def test_working_logs_are_not_verification_or_percent_complete(self):
        saved = report(progress={"controller_running": True, "stage": "implementation",
                                 "last_activity_at": "2026-10-10T12:30:00+00:00"})
        shown = progress.explain(saved)
        self.assertEqual(shown["phase"], "IN_PROGRESS")
        self.assertIn("not proof", shown["message"])
        self.assertNotIn("%", shown["message"])
        self.assertNotIn("ETA", shown["message"])
        self.assertFalse(shown["requires_user_action"])
        self.assertEqual(shown["activity"]["last_log_activity_at"],
                         "2026-10-10T12:30:00+00:00")

    def test_interrupted_run_recovers_without_restarting(self):
        shown = progress.explain(report())
        self.assertEqual(shown["phase"], "INTERRUPTED_RESUMABLE")
        self.assertIn("existing resume", shown["next_action"])
        self.assertIn("saved contract", shown["why_it_matters"])
        self.assertNotIn("start a new delivery", shown["message"])

    def test_preflight_failure_after_audit_is_not_approval_or_implementation(self):
        saved = report(
            status="BLOCKED",
            blocker="Codex failed to initialize its app-server client (Operation not permitted).",
            attempts=[{"stage": "planning", "status": "complete"},
                      {"stage": "planning-audit", "status": "complete"}],
            progress={"stage": "preflight", "controller_running": False},
            resume_count=1,
        )
        shown = progress.explain(saved)
        self.assertEqual(shown["phase"], "BLOCKED_HOST")
        self.assertIn("Planning and an independent audit finished", shown["what_happened"])
        self.assertIn("audit does not approve", shown["why_it_matters"])
        self.assertIn("never started", shown["why_it_matters"])
        self.assertIn("reconciliation or resume was attempted", shown["why_it_matters"])
        self.assertIn("host restriction", shown["next_action"])
        self.assertTrue(shown["requires_user_action"])
        self.assertIn("no confirmed implementation candidate", shown["where_is_the_code"])

    def test_waiting_for_approval_distinguishes_audit_from_permission(self):
        shown = progress.explain(report(status="AWAITING_APPROVAL"))
        self.assertEqual(shown["phase"], "AWAITING_APPROVAL")
        self.assertIn("audit", shown["why_it_matters"])
        self.assertTrue(shown["requires_user_action"])
        self.assertIn("approve", shown["next_action"].lower())

    def test_missing_invocation_is_not_resumable(self):
        shown = progress.explain(report(
            status="BLOCKED", blocker="no delivery invocation exists",
            candidate_workspace=None))
        self.assertEqual(shown["phase"], "NOT_ADMITTED")
        self.assertIn("no controller stages to resume", shown["why_it_matters"])
        self.assertIn("/deliver-issue", shown["next_action"])
        self.assertNotIn("then resume this invocation", shown["next_action"])

    def test_restore_requires_new_host_preflight_even_with_prior_implementation(self):
        shown = progress.explain(report(
            checkpoint_restored_from="9" * 64,
            fresh_host_preflight_complete=False,
            implementation_complete=True,
            progress={"controller_running": False, "stage": "review"},
        ))
        self.assertEqual(shown["phase"], "RESTORED_NEEDS_PREFLIGHT")
        self.assertIn("restored", shown["what_happened"].lower())
        self.assertIn("fresh preflight", shown["next_action"])
        self.assertIn("Receiving-host preflight", shown["not_yet_established"])
        self.assertIn("No current worker", shown["why_it_matters"])

    def test_blocked_restored_host_reports_real_blocker_not_generic_restore(self):
        shown = progress.explain(report(
            status="BLOCKED",
            blocker="Codex app-server client initialization: Operation not permitted",
            checkpoint_restored_from="9" * 64, fresh_host_preflight_complete=False,
        ))
        self.assertEqual(shown["phase"], "BLOCKED_HOST")
        self.assertIn("Restored evidence", shown["why_it_matters"])
        self.assertIn("Receiving-host preflight", shown["not_yet_established"])

    def test_uncertain_worker_never_causes_duplicate_dispatch(self):
        shown = progress.explain(report(
            status="BLOCKED",
            blocker="uncertain dispatch worker-1: missing controller host completion",
        ))
        self.assertEqual(shown["phase"], "BLOCKED_UNCERTAIN_WORKER")
        self.assertIn("reconcile", shown["next_action"])
        self.assertIn("duplicate", shown["why_it_matters"])

    def test_incomplete_parent_cannot_be_certified_by_children(self):
        shown = progress.explain(report(
            status="BLOCKED", blocker="Parent assembly still needs full review and proof",
            parent_has_children=True,
        ))
        self.assertIn("Child completion does not establish acceptance", shown["why_it_matters"])
        self.assertIn("Assembled-parent review and proof", shown["not_yet_established"])

    def test_open_pr_is_not_merged_and_has_one_next_action(self):
        shown = progress.explain(report(status="REVIEWED_AND_PROVEN"), publication=publication())
        self.assertEqual(shown["phase"], "PR_PUBLISHED_NOT_MERGED")
        self.assertIn("still open", shown["what_happened"])
        self.assertIn(PR, shown["where_is_the_code"])
        self.assertIn("merge-readiness", shown["next_action"])
        self.assertNotIn("finalized", shown["what_happened"].lower())

    def test_closed_without_merge_is_not_delivered(self):
        shown = progress.explain(report(status="REVIEWED_AND_PROVEN"),
                                 publication=publication("CLOSED"))
        self.assertEqual(shown["phase"], "PR_CLOSED_NOT_MERGED")
        self.assertIn("closed without merging", shown["what_happened"])

    def test_merge_without_receipt_is_partial_not_finalized(self):
        shown = progress.explain(report(status="REVIEWED_AND_PROVEN"),
                                 publication=publication("MERGED"))
        self.assertEqual(shown["phase"], "MERGED_RECEIPT_PENDING")
        self.assertIn("durable final receipt", shown["why_it_matters"])
        self.assertIn("#50/#47", shown["next_action"])
        self.assertIn("Durable final receipt", shown["not_yet_established"])

    def test_validated_finalization_requires_all_existing_mapping_facts(self):
        merged = publication("MERGED")
        future = {"status": "FINALIZED", "receipt_verified": True,
                  "candidate_mapping_verified": True, "destination_verified": True,
                  "candidate_key": KEY, "delivered_commit": merged["merge_commit"]}
        saved = report(status="REVIEWED_AND_PROVEN")
        success = progress.explain(saved, publication=merged, finalization=future)
        self.assertEqual(success["phase"], "FULLY_FINALIZED")
        self.assertIn("No further delivery action", success["next_action"])
        for broken in ("receipt_verified", "candidate_mapping_verified", "destination_verified"):
            self.assertEqual(
                progress.explain(saved, publication=merged,
                                 finalization=future | {broken: False})["phase"],
                "MERGED_RECEIPT_PENDING")
        self.assertEqual(
            progress.explain(saved, publication=merged,
                             finalization=future | {"candidate_key": "wrong"})["phase"],
            "MERGED_RECEIPT_PENDING")

    def test_unknown_publication_is_not_a_published_pr(self):
        shown = progress.explain(report(status="REVIEWED_AND_PROVEN"), publication={
            "status": "UNVERIFIED", "verified": False, "reason": "not found"
        })
        self.assertEqual(shown["phase"], "PUBLICATION_UNCONFIRMED")
        self.assertIn("could not be verified", shown["why_it_matters"])
        self.assertIn("Current PR state", shown["not_yet_established"])


class GitHubReadbackTests(unittest.TestCase):
    def setUp(self):
        self.entries = [{"path": "src/code.py", "mode": "100644", "type": "file",
                         "content_base64": "cHJpbnQoJ29rJykK"}]
        self.key = fs.snapshot_key(self.entries)
        self.local = report(status="REVIEWED_AND_PROVEN",
                            candidate={"key": self.key})
        self.head = "c" * 40
        self.body = (f"Readable summary\n<!-- grove:publish-pr repo=owner/repository "
                     f"candidate={self.key} contract=sha256:{CONTRACT} -->\n")

    def observed(self, state="OPEN", **changes):
        data = {"url": PR, "state": state, "mergedAt": None,
                "mergeCommit": None, "headRefOid": self.head, "baseRefName": "main",
                "body": self.body, "isDraft": True}
        if state == "MERGED":
            data.update(mergedAt="2026-10-10T11:00:00Z", mergeCommit={"oid": "d"*40})
        data.update(changes)
        return data

    def check(self, data, entries=None):
        def runner(argv, **kwargs):
            self.assertEqual(argv[:3], ["gh", "pr", "view"])
            return subprocess.CompletedProcess(argv, 0, json.dumps(data), "")
        with patch.object(progress.fs, "snapshot", return_value=self.entries if entries is None else entries):
            return progress.inspect_github_pr(Path("/tmp/fixture"), self.local, PR, runner=runner)

    def test_matching_open_and_merged_readback(self):
        live = self.check(self.observed())
        self.assertEqual(live["status"], "OPEN")
        self.assertTrue(live["verified"])
        self.assertEqual(progress.explain(self.local, publication=live)["phase"],
                         "PR_PUBLISHED_NOT_MERGED")
        merged = self.check(self.observed("MERGED"))
        self.assertEqual(merged["status"], "MERGED")
        self.assertEqual(progress.explain(self.local, publication=merged)["phase"],
                         "MERGED_RECEIPT_PENDING")

    def test_matching_marker_cannot_certify_changed_product_tree(self):
        mismatched = [{"path": "src/code.py", "mode": "100644", "type": "file",
                       "content_base64": "d3Jvbmc="}]
        result = self.check(self.observed("MERGED"), mismatched)
        self.assertEqual(result["status"], "UNVERIFIED")
        self.assertFalse(result["verified"])
        self.assertEqual(progress.explain(self.local, publication=result)["phase"],
                         "PUBLICATION_UNCONFIRMED")

    def test_misbound_or_ambiguous_pr_marker_blocks_claim(self):
        for body in ("No identity marker", self.body + self.body,
                     self.body.replace(CONTRACT, "f"*64)):
            with self.subTest(body=body[:30]):
                result = self.check(self.observed(body=body))
                self.assertFalse(result["verified"])

    def test_open_with_merge_metadata_is_contradictory(self):
        result = self.check(self.observed(mergedAt="2026-10-10T11:00:00Z"))
        self.assertFalse(result["verified"])

    def test_different_base_or_unknown_state_never_claims_merge(self):
        for record in (self.observed(baseRefName="other"),
                       self.observed(state="BROKEN"),
                       self.observed("MERGED", mergeCommit=None)):
            with self.subTest(state=record["state"]):
                result = self.check(record)
                self.assertFalse(result["verified"])

    def test_remote_errors_and_missing_authority_are_not_success(self):
        with patch.object(progress.fs, "snapshot", return_value=self.entries):
            missing = progress.inspect_github_pr(Path("/tmp"), self.local,
                                                  "not-a-pr", runner=lambda *_args, **_kw: None)
        self.assertFalse(missing["verified"])
        without_proof = progress.inspect_github_pr(Path("/tmp"), report(),
                                                   PR, runner=lambda *_args, **_kw: self.fail("No remote read"))
        self.assertFalse(without_proof["verified"])


class ExistingControllerIntegration(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture.DeliveryTests("test_clean_project_delivery_uses_local_contract_and_records")
        self.fixture.setUp()

    def tearDown(self):
        self.fixture.tearDown()

    def test_completed_delivery_explains_verified_local_only_status(self):
        code, result = self.fixture.cli()
        self.assertEqual(code, 0, result)
        self.assertEqual(result["human_progress"]["phase"], "LOCAL_REVIEWED_PROVEN")
        before_attempts = len(result["attempts"])
        code, current = self.fixture.cli("status")
        self.assertEqual(code, 0, current)
        self.assertEqual(current["human_progress"]["phase"], "LOCAL_REVIEWED_PROVEN")
        self.assertEqual(len(current["attempts"]), before_attempts)
        self.assertIn("where_is_the_code", current["human_progress"])

    def test_status_pr_readback_only_renders_verified_remote_facts(self):
        code, _ = self.fixture.cli()
        self.assertEqual(code, 0)
        from test_p2p_delivery import d
        before = list(self.fixture.fake.calls)
        observed = publication("OPEN")
        with patch.object(d.progress_view, "inspect_github_pr", return_value=observed) as readback:
            code, output = self.fixture.cli("status", "--pr", PR)
        self.assertEqual(code, 0, output)
        self.assertEqual(output["human_progress"]["phase"], "PR_PUBLISHED_NOT_MERGED")
        self.assertEqual(output["publication_observation"], observed)
        self.assertEqual(self.fixture.fake.calls, before)
        readback.assert_called_once()

    def test_saved_pr_hint_requires_fresh_readback_and_ambiguity_stays_unknown(self):
        code, _ = self.fixture.cli()
        self.assertEqual(code, 0)
        from test_p2p_delivery import d
        note = self.fixture.root / ".p2p/work/tiny/publication.md"
        calls = list(self.fixture.fake.calls)
        note.write_text("Pull request: " + PR + "\n")
        with patch.object(d.progress_view, "inspect_github_pr",
                          return_value=publication("OPEN")) as lookup:
            code, status = self.fixture.cli("status")
        self.assertEqual(code, 0, status)
        lookup.assert_called_once()
        self.assertEqual(status["human_progress"]["phase"], "PR_PUBLISHED_NOT_MERGED")
        note.write_text("PRs: " + PR + "\nhttps://github.com/owner/repository/pull/16\n")
        with patch.object(d.progress_view, "inspect_github_pr",
                          side_effect=AssertionError("No ambiguous PR lookup")):
            code, status = self.fixture.cli("status")
        self.assertEqual(code, 0, status)
        self.assertEqual(status["status"], "REVIEWED_AND_PROVEN")
        self.assertEqual(status["human_progress"]["phase"], "PUBLICATION_UNCONFIRMED")
        self.assertEqual(self.fixture.fake.calls, calls)

    def test_plain_cli_is_readable_and_does_not_dispatch(self):
        code, _ = self.fixture.cli()
        self.assertEqual(code, 0)
        calls = list(self.fixture.fake.calls)
        from test_p2p_delivery import d
        output = io.StringIO()
        args = ["--repo", str(self.fixture.root), "status",
                ".p2p/work/tiny/contract.md", "--human"]
        with contextlib.redirect_stdout(output):
            code = d.main(args)
        self.assertEqual(code, 0)
        self.assertIn("Next:", output.getvalue())
        self.assertIn("Where the code is:", output.getvalue())
        self.assertIn("User action required: no", output.getvalue())
        self.assertEqual(self.fixture.fake.calls, calls)


if __name__ == "__main__":
    unittest.main()
