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


if __name__ == "__main__":
    unittest.main()
