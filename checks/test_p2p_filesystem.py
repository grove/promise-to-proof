#!/usr/bin/env python3
"""Disposable Git repository checks: python3 checks/test_p2p_filesystem.py."""
import importlib.util
import base64
import contextlib
import io
import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("p2p", Path(__file__).resolve().parents[1] / "skills/productivity/deliver-issue/scripts/p2p_filesystem.py")
p2p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p2p)


def prepare(root):
    (root / ".gitignore").write_text("/.p2p/\n")
    for name in ("specs", "work", ".p2p/work", ".p2p/tmp"):
        (root / name).mkdir(parents=True, exist_ok=True)
    return p2p.setup(root)


def rejects(fn, message):
    try:
        fn()
    except (ValueError, OSError) as error:
        assert message in str(error), str(error)
    else:
        raise AssertionError("expected rejection: " + message)


def compact_identity_case():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "repo"
        root.mkdir()
        p2p.git(root, "init", "-q")
        p2p.git(root, "config", "user.name", "Filesystem Check")
        p2p.git(root, "config", "user.email", "check@example.invalid")
        prepare(root)
        (root / "unchanged.txt").write_text("same\n")
        (root / "original.txt").write_text("old\n")
        (root / "old-link").symlink_to("original.txt")
        (root / "work/compact.md").write_text("# Compact identity\n")
        p2p.git(root, "add", ".")
        p2p.git(root, "commit", "-qm", "compact base")
        base = p2p.full_commit(root, "HEAD")

        (root / "original.txt").write_text("new\n")
        (root / "original.txt").chmod(0o755)
        (root / "old-link").unlink()
        (root / "added.txt").write_text("added\n")
        (root / "new-link").symlink_to("added.txt")
        candidate = p2p.capture(root, "work/compact.md", base)
        sha = lambda data: hashlib.sha256(data).hexdigest()
        expected = [
            {"path": "added.txt", "state": "added", "type": "file", "mode": "100644", "sha256": sha(b"added\n")},
            {"path": "new-link", "state": "added", "type": "symlink", "mode": "120000", "sha256": sha(b"added.txt")},
            {"path": "old-link", "state": "deleted", "type": "symlink", "mode": "120000", "sha256": sha(b"original.txt")},
            {"path": "original.txt", "state": "modified", "type": "file", "mode": "100755", "sha256": sha(b"new\n")},
        ]
        manifest = p2p.snapshot(root)
        encoded_manifest = json.dumps(manifest, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
        assert candidate["changes"] == expected
        assert candidate["key"] == "snapshot:sha256:" + hashlib.sha256(encoded_manifest).hexdigest()
        serialized = json.dumps(candidate)
        assert "manifest" not in candidate and "content_base64" not in serialized and "unchanged.txt" not in serialized
        assert p2p.validate(root, "work/compact.md", base) == candidate


def run():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "repo"
        root.mkdir()
        p2p.git(root, "init", "-q")
        p2p.git(root, "config", "user.name", "Filesystem Check")
        p2p.git(root, "config", "user.email", "check@example.invalid")
        prepare(root)
        source = Path(directory) / "source.md"
        source.write_text("# Standalone\n")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            assert p2p.main(["--repo", str(root), "create", "work/standalone.md", "--from", str(source)]) == 0
            assert p2p.main(["--repo", str(root), "create", "work/standalone.md", "--from", str(source)]) == 1
        assert (root / "work/standalone.md").read_text() == "# Standalone\n"
        (root / "specs/feature.md").write_text(
            "# Feature\nSource: [Real](details.md)\n"
            "````markdown\nSource: [Example](missing.md)\n```\nParent: [Still example](missing-parent.md)\n````\n"
            "~~~markdown\nSource: [Example](missing-tilde.md)\n~~~\n")
        (root / "specs/details.md").write_text("# Real details\n")
        (root / "work/parent.md").write_text("# Parent\nSource: [Feature](../specs/feature.md)\n\n## Children\n- [API](feature-api.md) — R1 API contribution\n```markdown\n## Children\n- [Fake](missing-child.md)\n```\n")
        work = "work/feature-api.md"
        (root / work).write_text("# API\nParent contract: [Parent](parent.md)\n")
        (root / "app.txt").write_text("one\n")
        (root / "link").symlink_to("app.txt")
        p2p.git(root, "add", ".")
        p2p.git(root, "commit", "-qm", "candidate A")
        base = p2p.full_commit(root, "HEAD")
        before = p2p.git(root, "diff", "--cached")
        candidate = p2p.capture(root, work, base)
        assert candidate["commit"] == base
        assert len(candidate["binding_inputs"]) == 3
        assert p2p.resolve(root, "work/parent.md")["children"] == [work]
        candidate_file = root / ".p2p/work/feature-api/candidate.json"
        candidate_file.write_text(json.dumps({**candidate, "commit": "HEAD"}))
        rejects(lambda: p2p.validate(root, work, base), "full commit SHA")
        for malformed, message in (({**candidate, "key": "snapshot:sha256:bad"}, "snapshot digest"),
                                   ({**candidate, "commit": 1}, "candidate"),
                                   ({**candidate, "binding_inputs": None}, "binding_inputs")):
            candidate_file.write_text(json.dumps(malformed))
            rejects(lambda: p2p.validate(root, work, base), message)
        candidate_file.write_text(json.dumps(candidate))
        assert p2p.git(root, "diff", "--cached") == before
        p2p.save(root, work, "review.md", b"REVIEWED for " + base.encode())
        p2p.save(root, work, "proof.md", b"PROVEN for " + base.encode())
        p2p.save(root, work, "evidence/local-run.log", b"safe retained observation")
        p2p.save(root, work, "review.md", b"new report")
        artifacts = p2p.resolve(root, work)["artifacts"]
        assert any("history/" in path for path in artifacts)
        (root / ".p2p/tmp/scratch").write_text("disposable")
        shutil.rmtree(root / ".p2p/tmp")
        p2p.validate(root, work, base)
        p2p.git(root, "add", "-A")
        p2p.git(root, "commit", "--allow-empty", "-qm", "artifact B")
        assert p2p.validate(root, work, base)["commit"] == base
        assert not p2p.git(root, "ls-tree", "-r", "--name-only", "HEAD").decode().startswith(".p2p/")
        rejects(lambda: p2p.validate(root, work, "HEAD"), "comparison base changed")
        report = root / ".p2p/work/feature-api/review.md"
        committed_report = report.read_bytes()
        history = report.parent / "history"
        p2p.save(root, work, "review.md", b"uncommitted report")
        assert (history / p2p.digest(committed_report) / "review.md").read_bytes() == committed_report
        p2p.save(root, work, "review.md", b"next report")
        assert (history / p2p.digest(b"uncommitted report") / "review.md").read_bytes() == b"uncommitted report"
        assert p2p.git(root, "ls-files", "--", ".p2p") == b""
        for path, expected in (("app.txt", "product candidate changed"), (work, "work item changed"),
                               ("work/parent.md", "binding inputs changed"), ("specs/feature.md", "binding inputs changed")):
            file = root / path
            original = file.read_bytes()
            file.write_bytes(original + b"changed")
            rejects(lambda: p2p.validate(root, work, base), expected)
            file.write_bytes(original)
        (root / "untracked").write_text("new")
        rejects(lambda: p2p.validate(root, work, base), "product candidate changed")
        (root / "untracked").unlink()
        (root / "app.txt").chmod(0o755)
        rejects(lambda: p2p.validate(root, work, base), "product candidate changed")
        (root / "app.txt").chmod(0o644)
        (root / "link").unlink()
        (root / "link").symlink_to("elsewhere")
        rejects(lambda: p2p.validate(root, work, base), "product candidate changed")
        (root / "link").unlink()
        (root / "link").symlink_to("app.txt")
        (root / "app.txt").unlink()
        rejects(lambda: p2p.validate(root, work, base), "product candidate changed")
        (root / "app.txt").write_text("two\n")
        dirty = p2p.capture(root, work, base)
        assert dirty["key"].startswith("snapshot:sha256:")
        assert "manifest" not in dirty and dirty["changes"]
        assert p2p.validate(root, work, base) == dirty
        p2p.git(root, "add", ".")
        p2p.git(root, "commit", "-qm", "retained snapshot")
        assert p2p.validate(root, work, base) == dirty
        snapshot_clone = Path(directory) / "snapshot-clone"
        subprocess.run(["git", "clone", "-q", str(root), str(snapshot_clone)], check=True)
        assert not (snapshot_clone / ".p2p").exists()
        assert not p2p.git(snapshot_clone, "ls-tree", "-r", "--name-only", "HEAD").decode().startswith(".p2p/")
        (root / "app.txt").write_text("staged\n")
        p2p.git(root, "add", "app.txt")
        (root / "app.txt").write_text("two\n")
        rejects(lambda: p2p.validate(root, work, base), "partially staged")
        p2p.git(root, "reset", "-q", "HEAD", "app.txt")
        p2p.git(root, "config", "core.filemode", "false")
        p2p.git(root, "update-index", "--chmod=+x", "app.txt")
        rejects(lambda: p2p.capture(root, work, base), "partially staged")
        rejects(lambda: p2p.validate(root, work, base), "partially staged")
        p2p.git(root, "reset", "-q", "HEAD", "app.txt")
        p2p.git(root, "config", "core.filemode", "true")
        (root / ".gitignore").write_text("/.p2p/\n!/.p2p/\n")
        proof = root / ".p2p/work/feature-api/proof.md"
        proof.write_bytes(proof.read_bytes() + b" uncommitted")
        original_proof = proof.read_bytes()
        rejects(lambda: p2p.save(root, work, "proof.md", b"replacement"), "not effectively ignored")
        assert proof.read_bytes() == original_proof
        (root / ".gitignore").write_text("/.p2p/\n")
        rejects(lambda: p2p.paths(root, "work/../escape.md"), "work item must")
        rejects(lambda: p2p.save(root, work, "../../escape", b"bad"), "unsafe repository path")
        rejects(lambda: p2p.save(root, work, "./history/old/proof.md", b"bad"), "unsafe repository path")
        rejects(lambda: p2p.save(root, work, "history", b"bad"), "history is reserved")
        rejects(lambda: p2p.save(root, work, "history/old/proof.md", b"bad"), "history is reserved")
        (root / "work/linked.md").symlink_to("feature-api.md")
        rejects(lambda: p2p.paths(root, "work/linked.md"), "symlink")
        other = root / ".p2p/work/collision"
        other.mkdir()
        (other / "candidate.json").write_text(json.dumps({"work_item": work}))
        rejects(lambda: p2p.paths(root, "work/collision.md"), "another work item")
        original_work = (root / work).read_text()
        (root / work).write_text("# Unsafe\nSource: [Generated](../.p2p/work/feature-api/proof.md)\n")
        rejects(lambda: p2p.bindings(root, work), "cannot be binding inputs")
        (root / work).write_text("# Unsafe\nSource: [Metadata](../.git/config)\n")
        rejects(lambda: p2p.bindings(root, work), "unsafe repository path")
        rejects(lambda: p2p.save(root, work, ".git/config", b"bad"), "unsafe repository path")
        (root / work).write_text(original_work)
        parent = root / "work/parent.md"
        original_parent = parent.read_text()
        parent.write_text("# Parent\n## Children\n- [Outside](../../outside.md)\n")
        rejects(lambda: p2p.resolve(root, "work/parent.md"), "work item must")
        parent.write_text(original_parent)
        (root / ".gitignore").write_text("/specs/feature.md\n")
        rejects(lambda: p2p.setup(root), "must contain the exact /.p2p/ rule")
        (root / ".gitignore").write_text("/.p2p/\n")
        prepare(root)
        (root / ".gitignore").write_text("/.p2p/\n/work/\n")
        rejects(lambda: p2p.bindings(root, work), "conflicting ignore")
    print("P2P filesystem checks passed")


class FilesystemTests(unittest.TestCase):
    def test_committed_snapshot_batches_blobs_without_changing_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            p2p.git(root, "init", "-q")
            files = {f"file-{index:02}.bin": bytes([index]) + b"\0\nend" for index in range(24)}
            files.update({"empty": b"", "executable": b"#!/bin/sh\necho hello\n",
                          "line\nbreak\tø.txt": b"unusual path\n", "duplicate": b"\0\0\nend",
                          "excluded": b"not part of this identity"})
            for name, data in files.items():
                (root / name).write_bytes(data)
            (root / "executable").chmod(0o755)
            (root / "link").symlink_to("line\nbreak\tø.txt")
            for name in (".p2p/work/contract.md", "p2p-state/task.json"):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("excluded workflow state")
            p2p.git(root, "add", ".")
            p2p.git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@localhost",
                    "commit", "-qm", "binary, executable and symlink fixture")
            base = p2p.full_commit(root, "HEAD")
            # The committed snapshot must not read the now different working files.
            (root / "executable").write_bytes(b"changed since commit")
            expected = [{"path": name, "type": "file",
                         "mode": "100755" if name == "executable" else "100644",
                         "content_base64": base64.b64encode(data).decode()}
                        for name, data in files.items() if name != "excluded"]
            expected.append({"path": "link", "type": "symlink", "mode": "120000",
                             "target": "line\nbreak\tø.txt"})
            expected.sort(key=lambda entry: entry["path"])
            with patch.object(p2p.subprocess, "run", wraps=p2p.subprocess.run) as processes:
                actual = p2p.snapshot(root, base, exclude=("excluded",))
            self.assertEqual(actual, expected)
            self.assertEqual(p2p.snapshot_key(actual), p2p.snapshot_key(expected))
            self.assertEqual(processes.call_count, 2, "snapshot cost must not spawn once per file")

    def test_git_blob_batch_rejects_incomplete_or_misbound_results(self):
        oid = "a" * 40
        header = (oid + " blob 3\n").encode()
        valid = header + b"a\0b\n"
        malformed = (b"", (oid + " missing\n").encode(),
                     ("b" * 40 + " blob 3\na\0b\n").encode(),
                     (oid + " tree 3\na\0b\n").encode(),
                     (oid + " blob -1\n\n").encode(), header + b"a\0", valid[:-1], valid + b"extra")
        for response in malformed:
            with self.subTest(response=response), patch.object(p2p.subprocess, "run", return_value=
                    subprocess.CompletedProcess([], 0, stdout=response, stderr=b"")):
                with self.assertRaisesRegex(ValueError, "Git blob batch response"):
                    p2p.git_blobs(Path("unused-fixture"), [oid])

    def test_committed_snapshot_rereads_missing_objects(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            p2p.git(root, "init", "-q")
            (root / "file").write_text("retained bytes")
            p2p.git(root, "add", ".")
            p2p.git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@localhost",
                    "commit", "-qm", "missing object fixture")
            base = p2p.full_commit(root, "HEAD")
            self.assertEqual(len(p2p.snapshot(root, base)), 1)
            oid = p2p.git(root, "rev-parse", base + ":file").decode().strip()
            (root / ".git/objects" / oid[:2] / oid[2:]).unlink()
            with self.assertRaisesRegex(ValueError, "Git blob batch response"):
                p2p.snapshot(root, base)

    def test_setup_rejects_existing_selectively_unignored_p2p_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            p2p.git(root, "init", "-q")
            (root / ".gitignore").write_text(
                "/.p2p/\n!/.p2p/\n!/.p2p/work/\n/.p2p/work/*\n"
                "!/.p2p/work/tiny/\n/.p2p/work/tiny/*\n!/.p2p/work/tiny/runtime/\n"
                "/.p2p/work/tiny/runtime/*\n!/.p2p/work/tiny/runtime/admission.json\n")
            state = root / ".p2p/work/tiny/runtime/admission.json"
            state.parent.mkdir(parents=True)
            state.write_text("preserve me\n")
            self.assertEqual(p2p.git(root, "check-ignore", "--no-index", ".p2p/work/probe")
                             .decode().strip(), ".p2p/work/probe")
            before = p2p.git(root, "status", "--short")
            self.assertIn(b".p2p/", before)
            rejects(lambda: p2p.setup(root), ".p2p/work/tiny/runtime/admission.json")
            self.assertEqual(state.read_text(), "preserve me\n")
            self.assertEqual(p2p.git(root, "status", "--short"), before)

    def test_setup_rejects_tracked_state_and_path_collisions_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "tracked"
            root.mkdir()
            p2p.git(root, "init", "-q")
            (root / ".gitignore").write_text("/.p2p/\n")
            state = root / ".p2p/work/old/state.json"
            state.parent.mkdir(parents=True)
            state.write_text("preserve me\n")
            p2p.git(root, "add", ".gitignore")
            p2p.git(root, "add", "-f", "--", ".p2p/work/old/state.json")
            p2p.git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@localhost",
                    "commit", "-qm", "tracked P2P state")
            before = p2p.full_commit(root, "HEAD")
            tracked = p2p.git(root, "ls-files", "--stage", "-z")
            rejects(lambda: p2p.setup(root), "tracked P2P state blocks")
            assert state.read_text() == "preserve me\n"
            assert p2p.full_commit(root, "HEAD") == before
            assert p2p.git(root, "ls-files", "--stage", "-z") == tracked

            collision = Path(directory) / "collision"
            collision.mkdir()
            p2p.git(collision, "init", "-q")
            (collision / ".gitignore").write_text("/.p2p/\n")
            (collision / ".p2p").write_text("project data\n")
            rejects(lambda: p2p.setup(collision), "collides with a non-directory")
            assert (collision / ".p2p").read_text() == "project data\n"

    def test_default_setup_does_not_create_repository_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            p2p.git(root, "init", "-q")
            (root / ".gitignore").write_text("/.p2p/\n")
            before = sorted(path.name for path in root.iterdir())
            self.assertEqual(p2p.setup(root), {"storage": "repository-local", "root": ".p2p/work"})
            self.assertEqual(sorted(path.name for path in root.iterdir()), before)
            self.assertEqual(p2p.git(root, "check-ignore", "--no-index", ".p2p/work/probe").decode().strip(), ".p2p/work/probe")
            self.assertFalse((root / "specs").exists())
            self.assertFalse((root / "work").exists())
            self.assertFalse((root / ".p2p").exists())

    def test_setup_does_not_create_specs_or_work(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            p2p.git(root, "init", "-q")
            (root / ".gitignore").write_text("/.p2p/\n")
            p2p.setup(root)
            self.assertFalse((root / "specs").exists())
            self.assertFalse((root / "work").exists())

    def test_generated_contract_is_ignored_and_project_paths_remain_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            p2p.git(root, "init", "-q")
            (root / ".gitignore").write_text("/.p2p/\n")
            specs = root / "specs/foo.md"
            work = root / "work/foo.md"
            specs.parent.mkdir(); work.parent.mkdir()
            specs.write_text("Specification bytes\n")
            work.write_text("Project plan bytes\n")
            original = {path: (path.read_bytes(), path.stat().st_mode & 0o777) for path in (specs, work)}
            contract = root / ".p2p/work/task/contract.md"
            contract.parent.mkdir(parents=True)
            contract.write_text("# Acceptance contract: inputs\n\nContract revision: v1\n"
                                "Source: [Spec](../../../specs/foo.md)\n"
                                "Parent: [Plan](../../../work/foo.md)\n")
            self.assertEqual([item["path"] for item in p2p.bindings(root, ".p2p/work/task/contract.md")],
                             ["specs/foo.md", "work/foo.md"])
            detail = p2p.git(root, "check-ignore", "--no-index", "-v", "--",
                             ".p2p/work/task/contract.md").decode()
            self.assertIn(".gitignore:", detail)
            self.assertIn("/.p2p/", detail)
            self.assertFalse(p2p.git(root, "ls-files", "--", ".p2p"))
            self.assertEqual({path: (path.read_bytes(), path.stat().st_mode & 0o777)
                              for path in (specs, work)}, original)
            (root / ".p2p/work/task/candidate.json").write_text(
                json.dumps({"work_item": ".p2p/work/foreign/contract.md"}))
            rejects(lambda: p2p.paths(root, ".p2p/work/task/contract.md"),
                    "artifact directory belongs to another work item")

    def test_legacy_contract_reconciliation_preserves_identity_and_siblings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            p2p.git(root, "init", "-q")
            (root / ".gitignore").write_text("/.p2p/\n")
            (root / "specs").mkdir()
            (root / "work").mkdir()
            (root / "specs/source.md").write_text("Source\n")
            legacy = root / "work/task.md"
            data = b"# Acceptance contract: task\n\nContract revision: v3\n"
            data += b"Source: [Spec](../specs/source.md)\n\n## Acceptance matrix\n| R17 | stable\n"
            legacy.write_bytes(data)
            siblings = [root / "specs/unrelated.md", root / "work/unrelated.md"]
            for path in siblings:
                path.write_bytes(b"human-owned\n")
                path.chmod(0o640)
            before = {path: (path.read_bytes(), path.stat().st_mode & 0o777) for path in [*siblings, legacy]}
            artifact = root / ".p2p/work/task"
            artifact.mkdir(parents=True)
            (artifact / "planning-handoff.md").write_text("approved receipt\n")
            candidate = {"work_item": "work/task.md", "work_item_sha256": p2p.digest(data),
                         "binding_inputs": p2p.bindings(root, "work/task.md")}
            (artifact / "candidate.json").write_text(json.dumps(candidate))

            result = p2p.reconcile(root, "work/task.md")
            active = root / ".p2p/work/task/contract.md"
            receipt = json.loads((artifact / "contract-origin.json").read_text())
            self.assertEqual(result["sha256"], p2p.digest(data))
            self.assertEqual(active.read_bytes(), data)
            self.assertEqual(receipt["path"], "work/task.md")
            self.assertEqual(p2p.bindings(root, ".p2p/work/task/contract.md"), candidate["binding_inputs"])
            self.assertEqual(p2p.bindings(root, "work/task.md"), candidate["binding_inputs"])
            self.assertEqual(json.loads((artifact / "candidate.json").read_text()), candidate)
            self.assertEqual((artifact / "planning-handoff.md").read_text(), "approved receipt\n")
            self.assertEqual({path: (path.read_bytes(), path.stat().st_mode & 0o777)
                              for path in [*siblings, legacy]}, before)
            active.write_bytes(data + b"human edit\n")
            rejects(lambda: p2p.reconcile(root, "work/task.md"), "origin or bytes changed")
            self.assertEqual(active.read_bytes(), data + b"human edit\n")

    def test_disposable_repository(self):
        run()

    def test_compact_dirty_candidate_identity(self):
        compact_identity_case()

    def test_standalone_skill_packages(self):
        skills = Path(__file__).resolve().parents[1] / "skills/productivity"
        with tempfile.TemporaryDirectory() as directory:
            for source in sorted(skills.iterdir()):
                if not (source / "SKILL.md").exists():
                    continue
                installed = Path(directory) / source.name
                shutil.copytree(source, installed, symlinks=False,
                                ignore=shutil.ignore_patterns("__pycache__"))
                self.assertTrue((installed / "references/acceptance-contract-protocol.md").is_file())
                result = subprocess.run(["python3", str(installed / "scripts/p2p_filesystem.py"), "--help"],
                                        cwd=directory, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("capture", result.stdout)
                if source.name == "deliver-issue":
                    for name in ("p2p_delivery_measurements.py", "verify_acceptance_bundle.py"):
                        self.assertTrue((installed / "scripts" / name).is_file())
                        self.assertFalse((installed / "scripts" / name).is_symlink())
                    result = subprocess.run(["python3", str(installed / "scripts/p2p_delivery.py"), "--help"],
                                            cwd=directory, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("cleanup", result.stdout)
                    # Exercise the installed cleanup entrypoint without any development checks/ directory.
                    root = Path(directory) / "standalone-source"
                    root.mkdir()
                    p2p.git(root, "init", "-q")
                    prepare(root)
                    result = subprocess.run(["python3", str(installed / "scripts/p2p_delivery.py"),
                                             "--repo", str(root), "cleanup", ".p2p/work/example/contract.md"],
                                            cwd=directory, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertEqual(json.loads(result.stdout)["status"], "BLOCKED")
                    self.assertNotIn("ModuleNotFoundError", result.stderr)


if __name__ == "__main__":
    unittest.main()
