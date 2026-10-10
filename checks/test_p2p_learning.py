"""Safe learning-retention and terminal-handoff regression tests (offline only)."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/productivity/deliver-issue/scripts"
sys.path.insert(0, str(SCRIPTS))
import p2p_learning as lesson
import p2p_filesystem as fs

WORK = ".p2p/work/tiny/contract.md"
DIGEST = "a" * 64
INVOCATION = "fixture-delivery"
CANDIDATE = "snapshot:sha256:" + "b" * 64


class LearningRetentionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.owner = self.root / ".p2p/work/tiny"
        self.owner.mkdir(parents=True)
        (self.owner / "contract.md").write_text("contract")
        self.record = {
            "work_item": WORK, "invocation_id": INVOCATION,
            "contract": {"sha256": DIGEST}, "candidate_key": CANDIDATE,
            "status": "REVIEWED_AND_PROVEN", "attempts": [],
        }
        self.write_record()
        self.support = self.owner / "artifacts/safe-evidence.md"
        self.support.parent.mkdir()
        self.support.write_text("Confirmed reproducible safe observation.\n")
        self.write_report("selected")

    def write_record(self):
        (self.owner / "artifacts").mkdir(exist_ok=True)
        (self.owner / "artifacts/delivery.json").write_text(json.dumps(self.record))

    def write_report(self, state, status="PROVEN", source=None):
        sha = fs.digest(self.support.read_bytes())
        body = (f"# Retrospective\n\nLearning preservation: {state}\n"
                f"Delivery identity: {INVOCATION}\nContract SHA-256: {DIGEST}\n"
                f"Candidate identity: {CANDIDATE}\nEvidence status: {status}\n"
                + (f"Terminal disposition: abandoned\nTerminal decision source: {source}\n" if source else "")
                + "## Suggested learnings\n\n- S1: pending human disposition\n"
                + f"\n## Retained evidence\n\n- E1: [Observed invariant]({self.support.relative_to(self.root)}) SHA-256 `{sha}` - one observed case\n")
        (self.owner / "retrospective.md").write_text(body)

    def test_unselected_retrospective_is_noop(self):
        self.write_report("none")
        text = (self.owner / "retrospective.md").read_text()
        self.assertIn("Learning preservation: none", text)
        # No evidence may be carried in a no-learning record.
        with self.assertRaisesRegex(ValueError, "unexpectedly names"):
            lesson.inspect(self.root, WORK)
        (self.owner / "retrospective.md").unlink()
        self.assertEqual(lesson.cleanup_guard(self.root, WORK)["status"], "NONE")

    def test_selected_real_observation_is_verified(self):
        selected = lesson.inspect(self.root, WORK)
        self.assertEqual(selected["status"], "SELECTED")
        self.assertEqual(selected["identity"]["invocation"], INVOCATION)
        self.support.write_text("tampered\n")
        with self.assertRaisesRegex(ValueError, "missing or changed"):
            lesson.inspect(self.root, WORK)

    def test_unproven_terminal_handoff_never_claims_proof(self):
        self.record["status"] = "BLOCKED"
        self.write_record()
        self.write_report("selected", "UNPROVEN", "human confirmed abandonment")
        self.assertEqual(lesson.inspect(self.root, WORK)["identity"]["status"], "BLOCKED")
        self.write_report("selected", "PROVEN")
        with self.assertRaisesRegex(ValueError, "cannot claim proven"):
            lesson.inspect(self.root, WORK)

    def test_proven_lesson_rejects_missing_portable_publication(self):
        fake = {"schema": fs.CHECKPOINT_SCHEMA, "work_item": WORK,
                "destination": {"kind": "git"}}
        with patch.object(fs, "checkpoint_path", return_value=(self.root / "checkpoint.json", fake["destination"])), \
             patch.object(fs, "read_checkpoint", return_value=(fake, [
                 ("project", ".p2p/work/tiny/retrospective.md",
                  (self.owner / "retrospective.md").read_bytes()),
                 ("project", str(self.support.relative_to(self.root)), self.support.read_bytes())
             ])):
            (self.root / "checkpoint.json").write_bytes(b"checkpoint")
            with patch.object(fs, "checkpoint_status", return_value={"status": "LOCAL_ONLY"}):
                with self.assertRaisesRegex(ValueError, "not remotely portable"):
                    lesson.verify(self.root, WORK, "origin", require_portable=True)
            with patch.object(fs, "checkpoint_status", return_value={"status": "PORTABLE"}):
                self.assertEqual(lesson.verify(self.root, WORK, "origin", True)["status"], "PORTABLE")

    def test_selected_cleanup_refuses_missing_checkpoint(self):
        with self.assertRaises(OSError):
            lesson.cleanup_guard(self.root, WORK, remote="origin")


if __name__ == "__main__":
    unittest.main()
