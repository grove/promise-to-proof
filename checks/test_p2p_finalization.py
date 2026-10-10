#!/usr/bin/env python3
"""Offline #47 external-effect gates and receipt recovery (not live-host proof)."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1] / "skills/productivity/deliver-issue/scripts"
sys.path.insert(0, str(HERE))
import p2p_finalize as final
import p2p_autonomy as autonomy
import p2p_filesystem as fs
import test_p2p_delivery_record as records_fixture


REPO = "owner/repo"
URL = "https://github.com/owner/repo/pull/42"
HEAD = "a" * 40
BASE = "b" * 40
INTEGRATION = "c" * 40
CONTRACT = ".p2p/work/tiny/contract.md"


def mandate(*grants):
    answer = autonomy.local("Finish the exact already accepted delivery")
    answer["policy"]["effects"] = [{"action": action, "repository": REPO,
                                      "destination": destination}
                                     for action, destination in grants]
    return answer


def github_pr(*, merged=False, head=HEAD, base=BASE, body=""):
    return {"html_url": URL, "number": 42, "state": "closed" if merged else "open",
            "merged": merged, "merged_at": "2026-10-10T15:00:00Z" if merged else None,
            "merge_commit_sha": INTEGRATION if merged else None,
            "draft": False, "mergeable": True, "mergeable_state": "clean",
            "body": body,
            "head": {"sha": head, "repo": {"full_name": REPO}},
            "base": {"sha": base, "ref": "delivery-target",
                     "repo": {"full_name": REPO}}}


class ReadinessGates(unittest.TestCase):
    def setUp(self):
        self.record = {"routing": {"destination": "delivery-target"}}
        self.saved = {"schema": "promise-to-proof/merge-readiness/v1",
                      "status": "READY", "synchronized": True,
                      "pr": URL, "head": HEAD, "base": BASE,
                      "target": "delivery-target", "integration_commit": INTEGRATION,
                      "integration_check": "integration", "required_checks": ["CI"],
                      "policy_sha256": fs.digest(fs.canonical([
                          {"type": "required_status_checks",
                           "parameters": {"required_status_checks": [{"context": "CI"}]}}
                      ])),
                      "observed_at": "2026-10-10T14:30:00Z",
                      "merge_method": "squash"}
        self.rules = [{"type": "required_status_checks",
                       "parameters": {"required_status_checks": [{"context": "CI"}]}}]
        self.pr = github_pr()
        self.sync()

    def sync(self):
        self.pr["body"] = ("Merge readiness: READY\n" +
                           "<!-- p2p-ready:sha256:" +
                           fs.digest(fs.canonical(self.saved)) + " -->\n")

    def check(self):
        def gh(path, **kwargs):
            if path == "repos/" + REPO:
                return {"allow_squash_merge": True}
            if path == "repos/" + REPO + "/rules/branches/delivery-target":
                return self.rules
            raise AssertionError("Unexpected external GitHub read: " + path)
        with patch.object(final, "gh", side_effect=gh), \
             patch.object(final, "remote_branches",
                          return_value={"refs/heads/delivery-target": BASE}), \
             patch.object(final.fs, "full_commit", return_value=INTEGRATION), \
             patch.object(final.fs, "git",
                          return_value=(INTEGRATION + " " + BASE + " " + HEAD + "\n").encode()), \
             patch.object(final, "check_runs", return_value={
                 "CI": [{"status": "completed", "conclusion": "success"}],
                 "integration": [{"status": "completed", "conclusion": "success"}],
             }):
            return final.check_ready(Path("/tmp"), self.record, "origin", REPO,
                                     self.pr, "squash", self.saved)

    def test_ready_requires_exact_current_pair_policy_and_synchronized_body(self):
        self.assertEqual(self.check()["base"], BASE)
        self.pr["body"] = "Merge readiness: READY"
        with self.assertRaisesRegex(ValueError, "read back"):
            self.check()
        self.sync()
        self.pr["base"]["sha"] = "f"*40
        with self.assertRaisesRegex(ValueError, "stale"):
            self.check()

    def test_changed_rules_queue_and_repository_method_block_before_effect(self):
        self.rules.append({"type": "merge_queue", "parameters": {}})
        with self.assertRaisesRegex(ValueError, "branch rules changed"):
            self.check()
        self.saved["policy_sha256"] = fs.digest(fs.canonical(self.rules))
        self.sync()
        with self.assertRaisesRegex(ValueError, "merge queue"):
            self.check()

    def test_unsupported_review_or_missing_integration_evidence_blocks(self):
        self.saved["integration_commit"] = "d"*40
        self.sync()
        with self.assertRaisesRegex(ValueError, "exact current head"):
            self.check()

    def test_readiness_format_rejects_unsynced_or_conflicting_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "merge-readiness.md"
            content = (final.READINESS + "\n" + chr(96)*3 + "json\n" +
                       json.dumps(self.saved) + "\n" + chr(96)*3 + "\n")
            path.write_text(content)
            self.assertEqual(final.read_readiness(path), self.saved)
            path.write_text(content + content)
            with self.assertRaisesRegex(ValueError, "one unambiguous"):
                final.read_readiness(path)
            path.write_text(content.replace('"READY"', '"BLOCKED"'))
            with self.assertRaisesRegex(ValueError, "not approved"):
                final.read_readiness(path)


class ReceiptSemantics(unittest.TestCase):
    def setUp(self):
        self.record = {
            "schema": "promise-to-proof/delivery-record/v1",
            "invocation_id": "inv-one",
            "work_item": CONTRACT,
            "landing": {"receipt_id": "sha256:" + "a"*64, "repository": REPO,
                        "confirmed_at": "2026-10-10T14:00:00Z"},
        }
        self.url = "https://github.com/owner/repo/issues/7"
        self.comment = {"body": final.receipt_body(self.record),
                        "html_url": self.url + "#issuecomment-1"}

    def test_one_identical_comment_replays_without_a_new_effect(self):
        self.assertEqual(final.matching_receipt([self.comment], self.record), self.comment)
        body = final.receipt_body(self.record)
        self.assertIn("p2p-final:sha256:", body)
        with patch.object(final, "comments", return_value=[self.comment]), \
             patch.object(final, "run", side_effect=AssertionError("must not write")):
            out = final.comment_receipt(self.record,
                                        {"repository": REPO, "number": 7,
                                         "destination": self.url},
                                        mandate())
        self.assertEqual(out["status"], "RECORDED")

    def test_lost_comment_response_is_read_back_without_retry(self):
        with patch.object(final, "comments", side_effect=[[], [self.comment]]) as reads, \
             patch.object(final, "run", return_value=subprocess.CompletedProcess([], 1, "", "lost")) as write:
            out = final.comment_receipt(
                self.record, {"repository": REPO, "number": 7, "destination": self.url},
                mandate(("issue-comment", self.url)))
        self.assertEqual(out["status"], "RECORDED")
        self.assertEqual(reads.call_count, 2)
        self.assertEqual(write.call_count, 1)

    def test_missing_authority_causes_no_comment(self):
        with patch.object(final, "comments", return_value=[]), \
             patch.object(final, "run", side_effect=AssertionError("No remote write")):
            with self.assertRaisesRegex(ValueError, "outside the standing mandate"):
                final.comment_receipt(self.record,
                                      {"repository": REPO, "number": 7,
                                       "destination": self.url}, mandate())

    def test_duplicate_and_changed_receipts_block(self):
        with self.assertRaisesRegex(ValueError, "multiple matching"):
            final.matching_receipt([self.comment, self.comment], self.record)
        changed = copy.deepcopy(self.comment)
        changed["body"] = changed["body"].replace('"inv-one"', '"inv-two"')
        with self.assertRaisesRegex(ValueError, "identity has conflicting bytes"):
            final.matching_receipt([changed], self.record)
        other = copy.deepcopy(self.record)
        other["landing"]["receipt_id"] = "sha256:" + "b"*64
        with self.assertRaisesRegex(ValueError, "conflicting receipt"):
            final.matching_receipt([self.comment], other)

    def test_exact_source_issue_precedes_pr_and_arbitrary_issue_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            work = Path(root) / CONTRACT
            work.parent.mkdir(parents=True)
            source = "https://github.com/owner/repo/issues/8"
            work.write_text("# Acceptance contract: user\n"
                            "Source attribution: " + source + "\n")
            selected = final.receipt_target(Path(root), self.record,
                                            pr_url=URL)
            self.assertEqual(selected["destination"], source)
            with self.assertRaisesRegex(ValueError, "original source issue"):
                final.receipt_target(Path(root), self.record, receipt_issue=
                                     "https://github.com/owner/repo/issues/9")
            work.write_text("# Acceptance contract: local\n")
            selected = final.receipt_target(Path(root), self.record,
                                            pr_url=URL)
            self.assertEqual(selected["destination"], URL)

    def test_record_receipt_id_is_canonical_not_timestamp_or_transport(self):
        original = final.receipt_body(self.record)
        self.assertEqual(original, final.receipt_body(copy.deepcopy(self.record)))
        modified = copy.deepcopy(self.record)
        modified["landing"]["confirmed_at"] = "2026-10-11T14:00:00Z"
        self.assertNotEqual(original, final.receipt_body(modified))


class RetainedIntent(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        fs.git(self.root, "init", "-q")
        (self.root / ".gitignore").write_text("/.p2p/\n")
        fs.git(self.root, "add", ".gitignore")
        path = self.root / ".p2p/work/tiny/merge-readiness.md"
        path.parent.mkdir(parents=True)
        path.write_text("# READY\n\nApproved, exact head/base.\n")
        self.path = path

    def test_first_merge_reserves_and_second_wont_dispatch(self):
        self.assertTrue(final.reserve_merge(self.root, CONTRACT, self.path,
                                            URL, HEAD, BASE, "squash"))
        original = self.path.read_bytes()
        self.assertFalse(final.reserve_merge(self.root, CONTRACT, self.path,
                                             URL, HEAD, BASE, "squash"))
        self.assertEqual(self.path.read_bytes(), original)
        with self.assertRaisesRegex(ValueError, "conflicting"):
            final.reserve_merge(self.root, CONTRACT, self.path, URL,
                                "f"*40, BASE, "squash")


class IntegrationTests(unittest.TestCase):
    """Reuse the real offline #50 full-review/checkpoint fixture and Git trees."""

    def setUp(self):
        self.bundle = records_fixture.DeliveryRecordTests(
            "test_unmodified_local_only_record_preserves_old_meaning")
        self.bundle.setUp()
        self.addCleanup(self.bundle.doCleanups)
        self.root = self.bundle.root
        self.record = self.bundle.original
        self.checkpoint = self.bundle.checkpoint
        self.work = self.bundle.work
        self.remote = str(Path(self.bundle.item.temp.name) / "remote.git")
        self.durable = mandate(("issue-comment", URL), ("merge", URL))

    def merged(self):
        completed, inputs = self.bundle.landed("squash", pr=True)
        self.after = completed["landing"]["destination"]["after"]
        self.before = completed["landing"]["destination"]["before"]
        self.pr = github_pr(
            merged=True, head=self.bundle.candidate_commit, base=self.before)
        self.pr["merge_commit_sha"] = self.after
        self.pr["merged_at"] = "2026-10-10T12:00:01+00:00"
        return completed

    def execute(self, **kwargs):
        return final.finalize(
            self.root, self.record, self.checkpoint, repository=REPO,
            remote=self.remote, method="squash", pr_url=URL,
            mandate=self.durable, execute=True, **kwargs)

    def test_already_merged_pr_skips_second_merge_and_finalizes_once(self):
        completed = self.merged()
        target = {"refs/heads/delivery-target": self.after}
        receipt = {"status": "RECORDED", "url": URL + "#issuecomment-1"}
        with patch.object(final, "read_pr", return_value=self.pr) as read, \
             patch.object(final, "remote_branches", return_value=target), \
             patch.object(final, "portable", return_value={"status": "PORTABLE"}), \
             patch.object(final, "comment_receipt", return_value=receipt) as published, \
             patch.object(final, "run", side_effect=AssertionError("No merge after landed")):
            result = self.execute()
            second = self.execute()
        self.assertEqual(result["status"], "FINALIZED")
        self.assertTrue(result["finalization"]["receipt_verified"])
        self.assertEqual(result["finalization"]["candidate_key"],
                         self.record["candidate_key"])
        self.assertEqual(result["record"]["landing"]["receipt_id"],
                         completed["landing"]["receipt_id"])
        self.assertEqual(second["record"]["landing"]["receipt_id"],
                         completed["landing"]["receipt_id"])
        self.assertEqual(published.call_count, 2)  # readback/idempotence per run
        self.assertEqual(read.call_count, 4)  # no merge mutation

    def test_merged_but_no_portable_checkpoint_is_partial_not_success(self):
        self.merged()
        with patch.object(final, "read_pr", return_value=self.pr), \
             patch.object(final, "remote_branches",
                          return_value={"refs/heads/delivery-target": self.after}), \
             patch.object(final, "portable",
                          side_effect=ValueError("checkpoint not published")), \
             patch.object(final, "comment_receipt",
                          side_effect=AssertionError("No receipt without backup")):
            result = self.execute()
        self.assertEqual(result["status"], "PARTIAL")
        self.assertEqual(result["phase"], "LANDED_MAPPING_PENDING")
        self.assertIn("checkpoint", result["reason"])
        self.assertNotIn("finalization", result)

    def test_already_merged_with_different_remote_target_blocks_receipt(self):
        self.merged()
        with patch.object(final, "read_pr", return_value=self.pr), \
             patch.object(final, "remote_branches",
                          return_value={"refs/heads/delivery-target": self.before}), \
             patch.object(final, "comment_receipt",
                          side_effect=AssertionError("No receipt")):
            result = self.execute()
        self.assertEqual(result["status"], "PARTIAL")
        self.assertIn("remote destination", result["reason"])

    def test_open_pr_needs_exact_grant_and_only_one_merge_attempt(self):
        self.merged()
        opened = copy.deepcopy(self.pr)
        opened.update(merged=False, state="open", merged_at=None,
                      merge_commit_sha=None)
        self.bundle.git("update-ref", "refs/heads/delivery-target", self.before)
        events = [opened, opened, self.pr, self.pr]
        calls = []
        def gh_effect(args, **kwargs):
            calls.append(args)
            return subprocess.CompletedProcess(args, 1, "", "response lost")
        with patch.object(final, "read_pr", side_effect=events), \
             patch.object(final, "read_readiness", return_value={"status": "READY"}), \
             patch.object(final, "check_ready",
                          return_value={"base": self.before}), \
             patch.object(final, "reserve_merge", return_value=True) as intent, \
             patch.object(final, "run", side_effect=gh_effect), \
             patch.object(final, "remote_branches",
                          return_value={"refs/heads/delivery-target": self.after}), \
             patch.object(final, "portable", return_value={"status": "PORTABLE"}), \
             patch.object(final, "comment_receipt",
                          return_value={"status": "RECORDED", "url": URL + "#issuecomment-2"}):
            self.bundle.git("update-ref", "refs/heads/delivery-target", self.after)
            result = self.execute()
        self.assertEqual(result["status"], "FINALIZED")
        self.assertEqual(len(calls), 1, "lost response must not trigger a second merge")
        self.assertEqual(intent.call_count, 1)

    def test_unknown_merge_response_is_partial_not_an_authorized_retry(self):
        self.merged()
        opened = copy.deepcopy(self.pr)
        opened.update(merged=False, state="open", merged_at=None,
                      merge_commit_sha=None)
        with patch.object(final, "read_pr", side_effect=[opened, opened, opened]), \
             patch.object(final, "read_readiness", return_value={"status": "READY"}), \
             patch.object(final, "check_ready",
                          return_value={"base": self.before}), \
             patch.object(final, "reserve_merge", return_value=True), \
             patch.object(final, "run",
                          return_value=subprocess.CompletedProcess([], 1, "", "lost")) as mutate:
            result = self.execute()
        self.assertEqual(result["status"], "PARTIAL")
        self.assertEqual(result["phase"], "MERGE_UNCONFIRMED")
        self.assertEqual(mutate.call_count, 1)

    def test_insufficient_merge_grant_blocks_all_remote_effects(self):
        self.merged()
        opened = copy.deepcopy(self.pr)
        opened.update(merged=False, state="open")
        with patch.object(final, "read_pr", return_value=opened), \
             patch.object(final, "read_readiness", return_value={"status": "READY"}), \
             patch.object(final, "check_ready",
                          return_value={"base": self.before}), \
             patch.object(final, "run",
                          side_effect=AssertionError("No merge without grant")):
            with self.assertRaisesRegex(ValueError, "outside the standing mandate"):
                self.execute(mandate_override=mandate()) if False else final.finalize(
                    self.root, self.record, self.checkpoint, repository=REPO,
                    remote=self.remote, method="squash", pr_url=URL,
                    mandate=mandate(), execute=True)

    def test_issue_less_direct_delivery_without_a_synthetic_pr(self):
        completed, arguments = self.bundle.landed("direct")
        after = completed["landing"]["destination"]["after"]
        before = completed["landing"]["destination"]["before"]
        receipt = {"status": "RECORDED", "url": self.remote + ":refs/heads/p2p/receipts/tiny"}
        with patch.object(final, "remote_branches",
                          return_value={"refs/heads/delivery-target": after}), \
             patch.object(final, "portable", return_value={"status": "PORTABLE"}), \
             patch.object(final, "git_receipt", return_value=receipt) as publish:
            result = final.finalize(
                self.root, self.record, self.checkpoint, repository=REPO,
                remote=self.remote, method="direct", before=before, after=after,
                confirmed_at="2026-10-10T12:00:00+00:00",
                mandate=mandate(("commit", "refs/heads/p2p/receipts/tiny"),
                                ("push", "refs/heads/p2p/receipts/tiny")),
                receipt_ref="refs/heads/p2p/receipts/tiny", execute=True)
        self.assertEqual(result["status"], "FINALIZED")
        self.assertIsNone(result["record"]["landing"]["pull_request"])
        self.assertEqual(result["human_progress"]["phase"], "FULLY_FINALIZED")
        self.assertIn("no PR", result["human_progress"]["why_it_matters"])
        publish.assert_called_once()

    def test_portable_checkpoint_requires_actual_remote_candidate_git_objects(self):
        completed, _ = self.bundle.landed("direct")
        self.bundle.git("add", "p2p-state/tiny.json")
        self.bundle.git("commit", "-qm", "Publish checkpoint bytes")
        subprocess.run(["git", "init", "--bare", "-q", self.remote], check=True)
        self.bundle.git("push", "--quiet", self.remote,
                        "HEAD:refs/heads/checkpoint")
        with self.assertRaisesRegex(ValueError, "not recoverable"):
            final.portable(self.root, self.checkpoint, self.remote)
        self.bundle.git("branch", "portable-candidate",
                        self.bundle.index["candidate_commit"])
        self.bundle.git("push", "--quiet", self.remote,
                        "portable-candidate:refs/heads/portable-candidate")
        observed = final.portable(self.root, self.checkpoint, self.remote)
        self.assertEqual(observed["checkpoint_sha256"],
                         fs.digest(self.checkpoint))
        self.assertTrue(observed["url"].endswith("p2p-state/tiny.json"))

    def test_missing_receipt_branch_is_created_only_with_all_exact_grants(self):
        completed, _ = self.bundle.landed("direct")
        self.bundle.git("add", "p2p-state/tiny.json")
        self.bundle.git("commit", "-qm", "Publish portable checkpoint")
        subprocess.run(["git", "init", "--bare", "-q", self.remote], check=True)
        self.bundle.git("push", "--quiet", self.remote,
                        "HEAD:refs/heads/checkpoint")
        ref = "refs/heads/p2p/receipts/tiny"
        target = {"kind": "git", "ref": ref}
        with self.assertRaisesRegex(ValueError, "outside the standing mandate"):
            final.git_receipt(self.root, self.remote, target, completed,
                              self.checkpoint, mandate(("commit", ref), ("push", ref)))
        self.assertNotIn(ref, final.remote_branches(self.root, self.remote))
        receipt = final.git_receipt(
            self.root, self.remote, target, completed, self.checkpoint,
            mandate(("branch-create", ref), ("commit", ref), ("push", ref)))
        self.assertEqual(receipt["status"], "RECORDED")
        self.assertEqual(final.remote_branches(self.root, self.remote)[ref],
                         receipt["remote_commit"])
        repeated = final.git_receipt(self.root, self.remote, target, completed,
                                     self.checkpoint, mandate())
        self.assertEqual(repeated["status"], "RECORDED")
        self.assertEqual(repeated["remote_commit"], receipt["remote_commit"])

    def test_detached_git_receipt_preserves_operator_head_and_index(self):
        completed, _ = self.bundle.landed("direct")
        data = fs.canonical(completed) + b"\n"
        # Publish the existing checkpoint to an ordinary remote branch first.
        self.bundle.git("add", "p2p-state/tiny.json")
        self.bundle.git("commit", "-qm", "Publish portable checkpoint")
        baseline = self.bundle.git("rev-parse", "HEAD")
        index = (self.root / ".git/index").read_bytes()
        subprocess.run(["git", "init", "--bare", "-q", self.remote], check=True)
        ref = "refs/heads/p2p/receipts/tiny"
        self.bundle.git("push", "--quiet", self.remote, "HEAD:" + ref)
        grants = mandate(("commit", ref), ("push", ref))
        dest = {"kind": "git", "ref": ref}
        first = final.git_receipt(self.root, self.remote, dest,
                                  completed, self.checkpoint, grants)
        again = final.git_receipt(self.root, self.remote, dest,
                                  completed, self.checkpoint, grants)
        self.assertEqual(first["status"], "RECORDED")
        self.assertEqual(first["remote_commit"], again["remote_commit"])
        self.assertEqual(self.bundle.git("rev-parse", "HEAD"), baseline)
        self.assertEqual((self.root / ".git/index").read_bytes(), index)
        result = subprocess.run(["git", "-C", str(self.root), "show",
                                 first["remote_commit"] + ":p2p-state/tiny-delivery.json"],
                                check=True, capture_output=True)
        self.assertEqual(result.stdout, data)


if __name__ == "__main__":
    unittest.main()
