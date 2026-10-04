"""Execution storage and publication permission regressions (no remote effects)."""
import errno
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/productivity/deliver-issue/scripts"
spec = importlib.util.spec_from_file_location("execution_fs", SCRIPTS / "p2p_filesystem.py")
fs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fs)
WORK = ".p2p/work/example/contract.md"


class ExecutionAccessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / "source"
        self.root.mkdir()
        fs.git(self.root, "init", "-q")
        (self.root / ".gitignore").write_text("/.p2p/\n")
        (self.root / "product.txt").write_text("source\n")
        fs.git(self.root, "add", ".")
        fs.git(self.root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
               "commit", "-qm", "base")
        contract = self.root / WORK
        contract.parent.mkdir(parents=True)
        contract.write_text("# Local agreement\n")
        self.execution_root = self.root.parent / "executions"
        config = patch.dict(os.environ, {"P2P_EXECUTION_ROOT": str(self.execution_root)})
        config.start()
        self.addCleanup(config.stop)

    def workspace(self):
        directory = fs.prepare_execution(self.root, WORK)["execution_directory"]
        runtime = Path(directory) / "runtime"
        runtime.mkdir()
        workspace, metadata = runtime / "workspace", runtime / "repository.git"
        fs.git(runtime, "init", "-q", "--separate-git-dir=" + str(metadata), str(workspace))
        (workspace / "candidate.txt").write_text("retained candidate\n")
        return workspace, metadata

    def test_new_configuration_is_retained_across_resume(self):
        directory = Path(fs.prepare_execution(self.root, WORK)["execution_directory"])
        candidate = directory / "retained.txt"
        candidate.write_bytes(b"candidate")
        with patch.dict(os.environ, {"P2P_EXECUTION_ROOT": str(self.root.parent / "different")}):
            self.assertEqual(fs.execution_directory(self.root, WORK), directory)
            self.assertEqual(fs.prepare_execution(self.root, WORK)["execution_directory"], str(directory))
        self.assertEqual(candidate.read_bytes(), b"candidate")
        self.assertFalse((self.root.parent / "different").exists())

    def test_existing_default_candidate_is_not_relocated(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(Path, "home", return_value=self.root.parent):
            default = fs.execution_directory(self.root, WORK)
            default.mkdir(parents=True)
            (default / "candidate.txt").write_text("existing")
            with patch.dict(os.environ, {"P2P_EXECUTION_ROOT": str(self.execution_root)}):
                self.assertEqual(fs.execution_directory(self.root, WORK), default)
                self.assertEqual(fs.prepare_execution(self.root, WORK)["execution_directory"], str(default))
            self.assertEqual((default / "candidate.txt").read_text(), "existing")
        self.assertFalse(self.execution_root.exists())

    def test_configuration_rejects_checkout_relative_and_symlink_roots(self):
        linked = self.root.parent / "linked"
        linked.symlink_to(self.root, target_is_directory=True)
        for location in (self.root / ".p2p/executions", Path("relative"), linked):
            with self.subTest(location=location), patch.dict(os.environ, {"P2P_EXECUTION_ROOT": str(location)}):
                with self.assertRaises(ValueError):
                    fs.prepare_execution(self.root, WORK)
        self.assertFalse((self.root / ".p2p/work/example/execution-location.json").exists())

    def test_conflicting_default_and_retained_roots_require_reconciliation(self):
        directory = Path(fs.prepare_execution(self.root, WORK)["execution_directory"])
        temporary_home = self.root.parent / "other-home"
        default = temporary_home / ".p2p/executions" / directory.parent.name / directory.name
        default.mkdir(parents=True)
        (default / "candidate.txt").write_text("conflicting retained candidate")
        with patch.object(Path, "home", return_value=temporary_home):
            with self.assertRaisesRegex(ValueError, "both retained and default execution roots"):
                fs.execution_directory(self.root, WORK)
        self.assertTrue(default.is_dir())
        self.assertTrue(directory.is_dir())

    def test_empty_default_directory_does_not_pin_new_work(self):
        temporary_home = self.root.parent / "other-home"
        with patch.object(Path, "home", return_value=temporary_home):
            with patch.dict(os.environ, {}, clear=True):
                default = fs.execution_directory(self.root, WORK)
                default.mkdir(parents=True)
            directory = fs.execution_directory(self.root, WORK)
            self.assertIn(self.execution_root, directory.parents)
            self.assertNotEqual(directory, default)
        self.assertEqual(list(default.iterdir()), [])

    def test_denied_execution_access_saves_no_location(self):
        real_probe = fs.tempfile.TemporaryFile

        def denied(*args, **kwargs):
            if Path(kwargs["dir"]).is_relative_to(self.execution_root):
                raise PermissionError(errno.EACCES, "session denied execution writes")
            return real_probe(*args, **kwargs)

        with patch.object(fs.tempfile, "TemporaryFile", side_effect=denied):
            with self.assertRaisesRegex(ValueError, "write access required for"):
                fs.prepare_execution(self.root, WORK)
        self.assertFalse((self.root / ".p2p/work/example/execution-location.json").exists())

    def test_publication_probes_separate_git_metadata_and_preserves_checkout(self):
        workspace, metadata = self.workspace()
        head, index = fs.git(self.root, "rev-parse", "HEAD"), (self.root / ".git/index").read_bytes()
        before = {p: p.read_bytes() for p in workspace.parent.rglob("*") if p.is_file()}
        result = fs.publication_access(self.root, WORK, workspace)
        self.assertEqual(result["git_directory"], str(metadata))
        self.assertIn(str(metadata / "objects"), result["probed_directories"])
        self.assertIn(str(metadata / "refs"), result["probed_directories"])
        self.assertEqual(before, {p: p.read_bytes() for p in workspace.parent.rglob("*") if p.is_file()})
        self.assertEqual(fs.git(self.root, "rev-parse", "HEAD"), head)
        self.assertEqual((self.root / ".git/index").read_bytes(), index)

    def test_writable_worktree_does_not_hide_denied_git_access(self):
        workspace, metadata = self.workspace()
        if os.geteuid() == 0:
            self.skipTest("root bypasses directory mode write restrictions")
        metadata.chmod(0o555)
        try:
            fs.probe_write(workspace)
            with self.assertRaisesRegex(ValueError, "write access required for " + str(metadata)):
                fs.publication_access(self.root, WORK, workspace)
        finally:
            metadata.chmod(0o755)
        self.assertEqual((workspace / "candidate.txt").read_text(), "retained candidate\n")

    def test_linked_source_worktree_cannot_be_used_for_publication(self):
        linked = self.root.parent / "linked-worktree"
        fs.git(self.root, "worktree", "add", "--detach", str(linked), "HEAD")
        with self.assertRaisesRegex(ValueError, "metadata must be isolated"):
            fs.publication_access(self.root, WORK, linked)


if __name__ == "__main__":
    unittest.main()
