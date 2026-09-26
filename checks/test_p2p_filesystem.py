#!/usr/bin/env python3
"""Disposable Git repository checks: python3 checks/test_p2p_filesystem.py."""
import importlib.util
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("p2p", Path(__file__).resolve().parents[1] / "skills/productivity/deliver-issue/scripts/p2p_filesystem.py")
p2p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p2p)


def rejects(fn, message):
    try:
        fn()
    except (ValueError, OSError) as error:
        assert message in str(error), str(error)
    else:
        raise AssertionError("expected rejection: " + message)


def run():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "repo"
        root.mkdir()
        p2p.git(root, "init", "-q")
        p2p.git(root, "config", "user.name", "Filesystem Check")
        p2p.git(root, "config", "user.email", "check@example.invalid")
        p2p.setup(root)
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
        for malformed in ({**candidate, "key": "snapshot:sha256:bad", "manifest": []},
                          {**candidate, "commit": 1}, {**candidate, "binding_inputs": None}):
            candidate_file.write_text(json.dumps(malformed))
            rejects(lambda: p2p.validate(root, work, base), "candidate" if "key" in malformed or malformed.get("commit") == 1 else "binding_inputs")
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
        p2p.git(root, "add", ".p2p")
        p2p.git(root, "commit", "-qm", "artifact B")
        assert p2p.validate(root, work, base)["commit"] == base
        rejects(lambda: p2p.validate(root, work, "HEAD"), "comparison base changed")
        clone = Path(directory) / "clone"
        subprocess.run(["git", "clone", "-q", str(root), str(clone)], check=True)
        assert p2p.validate(clone, work, base)["commit"] == base
        assert "evidence/local-run.log" in " ".join(p2p.resolve(clone, work)["artifacts"])
        report = root / ".p2p/work/feature-api/review.md"
        committed_report = report.read_bytes()
        history = report.parent / "history"
        p2p.save(root, work, "review.md", b"uncommitted report")
        assert not (history / p2p.digest(committed_report) / "review.md").exists()
        assert p2p.git(root, "show", "HEAD:.p2p/work/feature-api/review.md") == committed_report
        p2p.git(root, "add", str(report))
        p2p.save(root, work, "review.md", b"next report")
        assert (history / p2p.digest(b"uncommitted report") / "review.md").read_bytes() == b"uncommitted report"
        p2p.git(root, "reset", "-q", "HEAD", str(report))
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
        assert all(not entry["path"].startswith(".p2p/") for entry in dirty["manifest"])
        assert p2p.validate(root, work, base) == dirty
        p2p.git(root, "add", ".")
        p2p.git(root, "commit", "-qm", "retained snapshot")
        assert p2p.validate(root, work, base) == dirty
        snapshot_clone = Path(directory) / "snapshot-clone"
        subprocess.run(["git", "clone", "-q", str(root), str(snapshot_clone)], check=True)
        assert p2p.validate(snapshot_clone, work, base) == dirty
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
        (root / ".gitignore").write_text("/.p2p/tmp/\n/.p2p/work/*/history/\n")
        rejects(lambda: p2p.setup(root), "conflicting ignore")
        proof = root / ".p2p/work/feature-api/proof.md"
        proof.write_bytes(proof.read_bytes() + b" uncommitted")
        original_proof = proof.read_bytes()
        rejects(lambda: p2p.save(root, work, "proof.md", b"replacement"), "conflicting ignore")
        assert proof.read_bytes() == original_proof
        (root / ".gitignore").write_text("/.p2p/tmp/\n")
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
        rejects(lambda: p2p.bindings(root, work), "conflicting ignore")
        (root / ".gitignore").write_text("/.p2p/\n")
        rejects(lambda: p2p.setup(root), "conflicting ignore")
        (root / ".gitignore").write_text("/work/\n")
        rejects(lambda: p2p.setup(root), "conflicting ignore")
    print("P2P filesystem checks passed")


class FilesystemTests(unittest.TestCase):
    def test_disposable_repository(self):
        run()

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


if __name__ == "__main__":
    unittest.main()
