"""Review publication uses only saved reports; no live GitHub calls in these tests."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
SKILL = HERE / "skills/productivity/publish-pr-review/scripts"
sys.path.insert(0, str(SKILL))
spec = importlib.util.spec_from_file_location("publish_pr_review", SKILL / "publish_pr_review.py")
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

CONTRACT = "a" * 64
REVIEW = "b" * 64
HEAD = "c" * 40
CANDIDATE = "snapshot:sha256:" + "d" * 64
PR = "https://github.com/owner/repo/pull/9"


def saved(status="REVIEWED"):
    return {"status": status, "contract_sha256": CONTRACT, "review_sha256": REVIEW,
            "candidate": CANDIDATE, "proof": "PROVEN", "checks": [],
            "findings": ([{"id": "F1", "location": "app.py", "evidence": "invalid return",
                         "consequence": "bad output", "correction": "handle errors"}]
                         if status == "CHANGES NEEDED" else []),
            "body": "# " + status + ": source\n\nActual retained reviewer report.\n"}


def preview(status="REVIEWED"):
    body, event, action, marker = r.render_review(saved(status), "owner/repo", 9, HEAD)
    return {"repository": "owner/repo", "pull_number": 9, "pr_url": PR, "head_sha": HEAD,
            "candidate": CANDIDATE, "contract_sha256": CONTRACT,
            "review_sha256": REVIEW, "body": body, "event": event, "effect": action,
            "marker": marker}


class PublishReviewTests(unittest.TestCase):
    def test_clean_saved_review_is_only_a_non_approving_comment(self):
        p = preview()
        self.assertEqual(p["event"], "COMMENT")
        self.assertEqual(p["effect"], "pr-review-comment")
        self.assertIn("not a GitHub approval", p["body"])
        self.assertIn("Merge readiness", p["body"])
        self.assertNotIn("## APPROVE", p["body"])
        self.assertIn("Actual retained reviewer report", p["body"])

    def test_material_findings_require_distinct_effect(self):
        p = preview("CHANGES NEEDED")
        self.assertEqual(p["event"], "REQUEST_CHANGES")
        self.assertEqual(p["effect"], "pr-review-request-changes")
        self.assertIn("F1", p["body"])
        self.assertIn("handle errors", p["body"])

    def test_missing_or_wrong_grant_blocks_submission(self):
        p = preview()
        digest = r.sha(r.canonical(p))
        with self.assertRaisesRegex(ValueError, "authorization"):
            r.authorize(p, digest)
        with self.assertRaisesRegex(ValueError, "does not match"):
            r.authorize(p, digest, approved_sha="0" * 64, approval_source="human approval")
        r.authorize(p, digest, approved_sha=digest, approval_source="human: exact preview")

    def test_identical_retry_reuses_only_matching_remote_review(self):
        p = preview()
        previous = {"body": p["body"], "state": "COMMENTED", "html_url": PR + "#pullrequestreview-12"}
        with patch.object(r, "reviews_read", return_value=[previous]):
            self.assertEqual(r.existing_review(p), previous["html_url"])
            with patch.object(r, "review_write") as write:
                result = r.publish(p)
                self.assertTrue(result["reused"])
                write.assert_not_called()
        with patch.object(r, "reviews_read", return_value=[dict(previous, body=p["marker"] + " tampered")]):
            with self.assertRaisesRegex(ValueError, "edited"):
                r.existing_review(p)
        with patch.object(r, "reviews_read", return_value=[previous, previous]):
            with self.assertRaisesRegex(ValueError, "duplicate"):
                r.existing_review(p)

    def test_success_requires_remote_readback_and_uncertain_write_never_claims_success(self):
        p = preview()
        previous = {"body": p["body"], "state": "COMMENTED", "html_url": PR + "#pullrequestreview-12"}
        with patch.object(r, "reviews_read", side_effect=[[], [previous]]):
            with patch.object(r, "review_write") as write:
                result = r.publish(p)
        self.assertEqual(result["status"], "PUBLISHED")
        write.assert_called_once()
        with patch.object(r, "reviews_read", side_effect=[[], RuntimeError("GitHub offline")]):
            with patch.object(r, "review_write", side_effect=RuntimeError("lost response")):
                result = r.publish(p)
        self.assertEqual(result["status"], "PARTIAL")

    def test_missing_review_or_changed_head_blocks_preview(self):
        with patch.object(r, "pr_read", return_value={
                "state": "open", "number": 9, "head": {"sha": HEAD, "repo": {"full_name": "owner/repo"}},
                "base": {"repo": {"full_name": "owner/repo"}, "ref": "main"},
                "body": "<!-- grove:publish-pr repo=owner/repo candidate=" + CANDIDATE +
                        " contract=sha256:" + CONTRACT + " -->"}):
            with patch.object(r, "load_saved", return_value=saved()):
                with patch.object(r.fs, "review_scope_status", return_value={"status":"UNCOVERED_DELTA"}):
                    with self.assertRaisesRegex(ValueError, "differs"):
                        r.build_preview(Path("."), ".p2p/work/demo/contract.md", PR, Path("."))
                with patch.object(r.fs, "review_scope_status", return_value={"status":"COVERED"}):
                    p = r.build_preview(Path("."), ".p2p/work/demo/contract.md", PR, Path("."))
                    self.assertEqual(p["head_sha"], HEAD)

if __name__ == "__main__":
    unittest.main()
