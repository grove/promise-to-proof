#!/usr/bin/env python3
"""Single-request routing contracts, in disposable Git repos with no model or network calls."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "skills/productivity/deliver-issue/scripts"
spec = importlib.util.spec_from_file_location("entry_fs", SCRIPTS / "p2p_filesystem.py")
fs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fs)


class SingleEntryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        fs.git(self.root, "init", "-q")
        fs.git(self.root, "config", "user.name", "Entry Test")
        fs.git(self.root, "config", "user.email", "entry@example.invalid")
        (self.root / ".gitignore").write_text("/.p2p/\n")
        (self.root / "specs").mkdir()
        (self.root / "specs/authentication.md").write_text("# Authentication\nReject empty usernames.\n")
        fs.git(self.root, "add", ".")
        fs.git(self.root, "commit", "-qm", "setup")

    def saved(self, slug, content, handoff=None):
        owner = self.root / ".p2p/work" / slug
        owner.mkdir(parents=True, exist_ok=True)
        work = f".p2p/work/{slug}/contract.md"
        (owner / "contract.md").write_text(content)
        if handoff is not None:
            (owner / "planning-handoff.md").write_text(handoff)
        return work

    def test_text_starts_planning_and_remains_read_only(self):
        message = "Reject empty usernames with a validation error"
        first = fs.entry_source(self.root, message)
        self.assertEqual(first["action"], "PLAN")
        self.assertEqual(first["kind"], "text")
        self.assertEqual(first["suggested_work_item"], fs.entry_source(self.root, message)["suggested_work_item"])
        self.assertFalse((self.root / ".p2p").exists())
        self.assertEqual(fs.git(self.root, "status", "--porcelain"), b"")
        with self.assertRaisesRegex(ValueError, "nonempty delivery request"):
            fs.entry_source(self.root, "  ")

    def test_exact_text_reuses_one_saved_agreement_and_checkpoint(self):
        message = 'Reject empty usernames with a "validation error"'
        receipt = ("Entry source kind: text\n"
                   "Entry request JSON: " + json.dumps(message) + "\n"
                   "Approval: delegated local planning audit recorded\n")
        work = self.saved("usernames", "# Acceptance contract: usernames\n", receipt)
        reused = fs.entry_source(self.root, message)
        self.assertEqual((reused["action"], reused["work_item"]), ("USE", work))
        self.assertEqual(fs.entry_source(self.root, message + ".")["action"], "PLAN")
        self.assertEqual(fs.entry_source(self.root, work)["action"], "USE")
        # A checkpoint preserves the normal planning handoff and may be restored
        # to another checkout without rerunning planning.
        checkpoint = fs.checkpoint(self.root, work)
        self.assertEqual(checkpoint["status"], "LOCAL_ONLY")
        (self.root / work).unlink()
        (self.root / ".p2p/work/usernames/planning-handoff.md").unlink()
        result = fs.entry_source(self.root, message)
        self.assertEqual(result["action"], "RESTORE")
        self.assertEqual(result["work_item"], work)
        self.assertEqual(result["checkpoint"], "p2p-state/usernames.json")
        restored = fs.restore_checkpoint(self.root, (self.root / result["checkpoint"]).read_bytes())
        self.assertEqual(restored["status"], "RESTORED")
        self.assertEqual(fs.entry_source(self.root, message)["action"], "USE")

    def test_specification_binds_real_source_and_detects_changed_bytes(self):
        source = "specs/authentication.md"
        proposed = fs.entry_source(self.root, source)
        self.assertEqual(proposed["action"], "PLAN")
        work = self.saved("auth", "# Acceptance contract: authentication\n"
                          "Source: [Specification](../../../specs/authentication.md)\n")
        used = fs.entry_source(self.root, source)
        self.assertEqual((used["action"], used["work_item"]), ("USE", work))
        before = used["entry_fingerprint_sha256"]
        (self.root / source).write_text("# Authentication\nDifferent requirement.\n")
        changed = fs.entry_source(self.root, source)
        self.assertEqual(changed["action"], "USE")  # Reconcile before delivery; not automatic approval.
        self.assertNotEqual(before, changed["entry_fingerprint_sha256"])
        with self.assertRaisesRegex(ValueError, "specification does not exist"):
            fs.entry_source(self.root, "specs/missing.md")

    def test_issue_needs_tracker_config_and_reuses_attributed_contract(self):
        with self.assertRaisesRegex(ValueError, "configured OWNER/REPO"):
            fs.entry_source(self.root, "#123")
        proposed = fs.entry_source(self.root, "#123", "owner/repo")
        self.assertEqual(proposed["action"], "PLAN")
        self.assertEqual(proposed["kind"], "issue")
        contract = ("# Acceptance contract: issue 123\n"
                    "Source attribution: https://github.com/owner/repo/issues/123; retrieved sha256: abc\n")
        work = self.saved("existing-issue", contract)
        used = fs.entry_source(self.root, "#123", "owner/repo")
        self.assertEqual((used["action"], used["work_item"]), ("USE", work))
        self.assertEqual(fs.entry_source(self.root, "#123", "other/repo")["action"], "PLAN")
        self.assertEqual(fs.entry_source(self.root, "#124", "owner/repo")["action"], "PLAN")
        with self.assertRaisesRegex(ValueError, "configured OWNER/REPO"):
            fs.entry_source(self.root, "#123", "not-a-repository")

    def test_conflicts_and_ambiguous_match_do_not_guess(self):
        msg = "A small change"
        receipt = "Entry request JSON: " + json.dumps(msg) + "\n"
        self.saved("a", "# Acceptance contract: first\n", receipt)
        self.saved("b", "# Acceptance contract: second\n", receipt)
        with self.assertRaisesRegex(ValueError, "multiple saved contracts match"):
            fs.entry_source(self.root, msg)
        different = "Unrelated request"
        proposed = fs.entry_source(self.root, different)
        (self.root / proposed["suggested_work_item"]).parent.mkdir(parents=True, exist_ok=True)
        (self.root / proposed["suggested_work_item"]).write_text("Unrelated existing contract")
        with self.assertRaisesRegex(ValueError, "already belongs to different source"):
            fs.entry_source(self.root, different)

    def test_work_markdown_is_a_spec_unless_explicit_legacy_contract(self):
        (self.root / "work").mkdir()
        spec = self.root / "work/authentication.md"
        spec.write_text("# Project-authored spec\nNormal work, not a P2P contract.\n")
        fs.git(self.root, "add", "work/authentication.md")
        fs.git(self.root, "commit", "-qm", "project authored spec")
        result = fs.entry_source(self.root, "work/authentication.md")
        self.assertEqual(result["action"], "PLAN")
        self.assertEqual(result["kind"], "spec")
        legacy = self.root / "work/legacy.md"
        legacy.write_text("# Acceptance contract: legacy\n\nContract revision: v1\n")
        self.assertEqual(fs.entry_source(self.root, "work/legacy.md")["action"], "USE")

    def test_prose_mentioning_markdown_is_not_mistaken_for_file(self):
        result = fs.entry_source(self.root, "Please add a new README.md")
        self.assertEqual(result["action"], "PLAN")
        self.assertEqual(result["kind"], "text")

    def test_generated_paths_and_unsafe_sources_are_not_specs(self):
        for value in (".p2p/work/x/source.md", "p2p-state/x.json"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "generated state"):
                    fs.entry_source(self.root, value)
        with self.assertRaisesRegex(ValueError, "unsafe repository path"):
            fs.entry_source(self.root, "../outside.md")
        with self.assertRaisesRegex(ValueError, "missing"):
            fs.entry_source(self.root, ".p2p/work/unknown/contract.md")

    def test_cli_resolves_without_writes(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            code = fs.main(["--repo", str(self.root), "resolve-entry", "specs/authentication.md"])
        self.assertEqual(code, 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["action"], "PLAN")
        self.assertFalse((self.root / ".p2p").exists())
        with contextlib.redirect_stdout(io.StringIO()) as output, contextlib.redirect_stderr(io.StringIO()):
            code = fs.main(["--repo", str(self.root), "resolve-entry", "#123"])
        self.assertEqual(code, 1)
        self.assertEqual(output.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
