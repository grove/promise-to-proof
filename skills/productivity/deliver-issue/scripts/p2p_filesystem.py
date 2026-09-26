#!/usr/bin/env python3
"""Repository-local P2P paths and exact candidate identities (stdlib only)."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys


WORK = re.compile(r"work/[a-z0-9]+(?:-[a-z0-9]+)*\.md\Z")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode:
        raise ValueError(result.stderr.decode().strip() or "git command failed")
    return result.stdout


def safe(root, relative, leaf_symlink=False):
    path = PurePosixPath(relative)
    if path.is_absolute() or any(p in ("", ".", "..") or p.lower() == ".git" for p in relative.split("/")):
        raise ValueError(f"unsafe repository path: {relative}")
    current = root
    for i, part in enumerate(path.parts):
        current = current / part
        if current.is_symlink() and not (leaf_symlink and i == len(path.parts) - 1):
            raise ValueError(f"symlink in repository path: {relative}")
    return current


def paths(root, work):
    if not WORK.fullmatch(work):
        raise ValueError("work item must be work/<lowercase-kebab-case>.md")
    item = safe(root, work)
    artifact = safe(root, f".p2p/work/{item.stem}")
    if item.exists() and not item.is_file():
        raise ValueError("work item is not a file")
    if artifact.exists() and not artifact.is_dir():
        raise ValueError("artifact directory collides with a file")
    candidate = safe(root, f".p2p/work/{item.stem}/candidate.json")
    if candidate.exists():
        record = json.loads(candidate.read_text())
        if not isinstance(record, dict) or record.get("work_item") != work:
            raise ValueError("artifact directory belongs to another work item or has malformed candidate metadata")
    return item, artifact


def trackable(root, names):
    result = subprocess.run(["git", "-C", str(root), "check-ignore", "--no-index", "--", *names], capture_output=True)
    if result.returncode not in (0, 1):
        raise ValueError(result.stderr.decode())
    if result.stdout:
        ignored = result.stdout.decode().splitlines()
        detail = subprocess.run(["git", "-C", str(root), "check-ignore", "-v", "--no-index", "--", *ignored], capture_output=True)
        raise ValueError("conflicting ignore rules hide durable paths: " + detail.stdout.decode().strip())


def setup(root):
    for name in ("specs", "work", ".p2p/work", ".p2p/tmp"):
        safe(root, name).mkdir(parents=True, exist_ok=True)
    probes = ["specs/p2p-trackability-check.md", "work/p2p-trackability-check.md",
              ".p2p/work/p2p-trackability-check/candidate.json",
              ".p2p/work/p2p-trackability-check/history/check/proof.md",
              ".p2p/work/p2p-trackability-check/evidence/check.log"]
    existing = [str(path.relative_to(root)) for directory in ("specs", "work", ".p2p/work")
                for path in safe(root, directory).rglob("*") if path.is_file()]
    trackable(root, probes + existing)
    ignore = safe(root, ".gitignore")
    content = ignore.read_bytes() if ignore.exists() else b""
    if b"/.p2p/tmp/" not in content.splitlines():
        ignore.write_bytes(content + (b"\n" if content and not content.endswith(b"\n") else b"") + b"/.p2p/tmp/\n")
    git(root, "check-ignore", "--no-index", ".p2p/tmp/p2p-check")
    return {"directories": ["specs/", "work/", ".p2p/work/", ".p2p/tmp/"]}


def snapshot(root, commit=None):
    entries = []
    if commit:
        records = git(root, "ls-tree", "-rz", "--full-tree", commit).split(b"\0")
        sources = []
        for record in filter(None, records):
            meta, name = record.split(b"\t", 1)
            mode, kind, oid = meta.decode().split()
            path = name.decode("utf-8")
            if path == ".p2p" or path.startswith(".p2p/"):
                continue
            if kind != "blob":
                raise ValueError(f"submodules are not supported: {path}")
            sources.append((path, mode, git(root, "cat-file", "blob", oid)))
    else:
        names = set(git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard").split(b"\0"))
        sources = []
        for name in filter(None, names):
            path = name.decode("utf-8")
            if path == ".p2p" or path.startswith(".p2p/"):
                continue
            file = safe(root, path, leaf_symlink=True)
            if file.is_symlink():
                sources.append((path, "120000", os.readlink(file).encode("utf-8")))
            elif file.is_file():
                sources.append((path, "100755" if file.stat().st_mode & 0o111 else "100644", file.read_bytes()))
            elif file.exists():
                raise ValueError(f"non-file candidate path (possibly submodule): {path}")
    for path, mode, data in sources:
        entry = {"path": path, "mode": mode}
        if mode == "120000":
            entry.update(type="symlink", target=data.decode("utf-8"))
        else:
            entry.update(type="file", content_base64=base64.b64encode(data).decode())
        entries.append(entry)
    return sorted(entries, key=lambda entry: entry["path"])


def document_lines(text):
    """Read document metadata, excluding fenced examples."""
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
        elif marker:
            fence = marker[1]
        else:
            yield line


def bindings(root, work):
    found = {}
    def visit(relative):
        if relative == ".p2p" or relative.startswith(".p2p/"):
            raise ValueError("generated artifacts cannot be binding inputs")
        if relative in found:
            return
        file = safe(root, relative)
        trackable(root, [relative])
        data = file.read_bytes()
        found[relative] = digest(data)
        for line in document_lines(data.decode()):
            if not re.match(r"^(Source|Parent|Parent contract):\s*", line):
                continue
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", line):
                if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                    continue
                target = target.split("#", 1)[0]
                if not target:
                    continue
                resolved = os.path.normpath(str(PurePosixPath(relative).parent / target))
                visit(resolved)
    visit(work)
    del found[work]
    return [{"path": path, "sha256": value} for path, value in sorted(found.items())]


def save(root, work, name, data):
    item, artifact = paths(root, work)
    if not item.is_file():
        raise ValueError("work item does not exist")
    target = safe(artifact, name)
    trackable(root, [str(target.relative_to(root)), work])
    if PurePosixPath(name).parts[0] == "history":
        raise ValueError("history is reserved")
    if target.exists():
        old = target.read_bytes()
        if old == data:
            return str(target.relative_to(root))
        archived = safe(root, str(artifact.relative_to(root) / "history" / digest(old) / name))
        trackable(root, [str(archived.relative_to(root))])
        archived.parent.mkdir(parents=True, exist_ok=True)
        if archived.exists() and archived.read_bytes() != old:
            raise ValueError("history collision")
        archived.write_bytes(old)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return str(target.relative_to(root))


def full_commit(root, ref):
    return git(root, "rev-parse", "--verify", "--end-of-options", ref + "^{commit}").decode().strip()


def check_index(root):
    # Retain one version, including modes even when Git ignores filesystem mode changes.
    staged = {name.decode() for name in git(root, "diff", "--cached", "--name-only", "-z").split(b"\0")
              if name and name != b".p2p" and not name.startswith(b".p2p/")}
    if not staged:
        return
    current = {entry["path"]: entry for entry in snapshot(root)}
    indexed = {}
    for record in filter(None, git(root, "ls-files", "--stage", "-z").split(b"\0")):
        meta, name = record.split(b"\t", 1)
        path = name.decode()
        if path not in staged:
            continue
        mode, oid, stage = meta.decode().split()
        if stage != "0":
            raise ValueError("unresolved index conflict: " + path)
        indexed[path] = (mode, git(root, "cat-file", "blob", oid))
    for path in staged:
        actual = current.get(path)
        expected = indexed.get(path)
        if actual is None and expected is None:
            continue
        if actual is not None and expected is not None:
            data = actual["target"].encode() if actual["type"] == "symlink" else base64.b64decode(actual["content_base64"])
            if expected == (actual["mode"], data):
                continue
        raise ValueError("partially staged path needs one candidate version (content or mode): " + path)


def capture(root, work, base, commit=None):
    item, _ = paths(root, work)
    check_index(root)
    manifest = snapshot(root)
    chosen = full_commit(root, commit or "HEAD")
    committed = snapshot(root, chosen)
    if commit and manifest != committed:
        raise ValueError("working tree differs from requested committed candidate")
    record = {"work_item": work, "work_item_sha256": digest(item.read_bytes()),
              "comparison_base": full_commit(root, base), "binding_inputs": bindings(root, work)}
    if manifest == committed:
        record["commit"] = chosen
    else:
        record.update(key="snapshot:sha256:" + digest(canonical(manifest)), manifest=manifest)
    save(root, work, "candidate.json", json.dumps(record, indent=2, ensure_ascii=False).encode() + b"\n")
    return record


def validate(root, work, base):
    check_index(root)
    item, artifact = paths(root, work)
    record = json.loads((artifact / "candidate.json").read_text())
    shared = {"work_item", "work_item_sha256", "comparison_base", "binding_inputs"}
    if set(record) not in (shared | {"commit"}, shared | {"key", "manifest"}):
        raise ValueError("candidate must contain exactly one committed or snapshot identity")
    for name in ("work_item", "work_item_sha256", "comparison_base", "commit" if "commit" in record else "key"):
        if not isinstance(record[name], str):
            raise ValueError("candidate field must be a string: " + name)
    if not isinstance(record["binding_inputs"], list):
        raise ValueError("binding_inputs must be an array")
    if "manifest" in record and not isinstance(record["manifest"], list):
        raise ValueError("snapshot manifest must be an array")
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", record["comparison_base"]):
        raise ValueError("comparison base must be a full commit SHA")
    if record["comparison_base"] != full_commit(root, base):
        raise ValueError("comparison base changed")
    if record["work_item_sha256"] != digest(item.read_bytes()):
        raise ValueError("work item changed")
    if record["binding_inputs"] != bindings(root, work):
        raise ValueError("binding inputs changed")
    if "commit" in record:
        if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", record["commit"]):
            raise ValueError("candidate commit must be a full commit SHA")
        expected = snapshot(root, full_commit(root, record["commit"]))
    else:
        expected = record["manifest"]
        if record["key"] != "snapshot:sha256:" + digest(canonical(expected)):
            raise ValueError("snapshot digest mismatch")
    if snapshot(root) != expected:
        raise ValueError("product candidate changed")
    return record


def children(root, work):
    result = []
    section = False
    for line in document_lines(safe(root, work).read_text()):
        if line.startswith("## "):
            section = line.strip() == "## Children"
        if section:
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", line):
                if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                    continue
                relative = os.path.normpath(str(PurePosixPath(work).parent / target.split("#", 1)[0]))
                item, _ = paths(root, relative)
                if not item.is_file():
                    raise ValueError("child work item does not exist: " + relative)
                trackable(root, [relative])
                result.append(relative)
    return sorted(set(result))


def resolve(root, work):
    item, artifact = paths(root, work)
    return {"work_item": work, "artifact_directory": str(artifact.relative_to(root)),
            "binding_inputs": bindings(root, work), "children": children(root, work),
            "artifacts": sorted(str(file.relative_to(root)) for file in artifact.rglob("*") if file.is_file())}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("setup")
    for name in ("resolve", "create", "capture", "validate", "resume", "save"):
        command = commands.add_parser(name)
        command.add_argument("work")
        if name in ("capture", "validate", "resume"):
            command.add_argument("--base", required=True)
        if name == "capture":
            command.add_argument("--commit")
        if name == "save":
            command.add_argument("name")
        if name in ("create", "save"):
            command.add_argument("--from", dest="source", required=True)
    args = parser.parse_args(argv)
    try:
        root = Path(git(Path(args.repo), "rev-parse", "--show-toplevel").decode().strip()).resolve()
        if args.command == "setup":
            result = setup(root)
        elif args.command == "create":
            item, artifact = paths(root, args.work)
            if artifact.exists() and any(artifact.iterdir()):
                raise ValueError("artifact directory already contains records")
            trackable(root, [args.work])
            data = Path(args.source).read_bytes()
            item.parent.mkdir(parents=True, exist_ok=True)
            with item.open("xb") as output:
                output.write(data)
            result = resolve(root, args.work)
        elif args.command == "capture":
            result = capture(root, args.work, args.base, args.commit)
        elif args.command in ("validate", "resume"):
            result = {"candidate": validate(root, args.work, args.base), **resolve(root, args.work)}
        elif args.command == "save":
            result = {"saved": save(root, args.work, args.name, Path(args.source).read_bytes())}
        else:
            result = resolve(root, args.work)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError, UnicodeError) as error:
        print(f"p2p: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
