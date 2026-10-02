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
import uuid


SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
WORK = re.compile(rf"(?:work/(?P<legacy>{SLUG})\.md|\.p2p/work/(?P<active>{SLUG})/contract\.md)\Z")


def work_slug(work):
    match = WORK.fullmatch(work)
    if not match:
        raise ValueError("work item must be a P2P contract path")
    return match.group("active") or match.group("legacy")


def contract_origin(root, slug):
    path = safe(root, f".p2p/work/{slug}/contract-origin.json")
    return json.loads(path.read_text()) if path.is_file() else None


def verify_contract_origin(root, slug, receipt):
    legacy = f"work/{slug}.md"
    active = safe(root, f".p2p/work/{slug}/contract.md")
    source = safe(root, legacy)
    expected = {"schema": "promise-to-proof/contract-origin/v1", "path": legacy,
                "sha256": digest(active.read_bytes()), "binding_inputs": receipt.get("binding_inputs")}
    if receipt != expected or not source.is_file() or digest(source.read_bytes()) != expected["sha256"]:
        raise ValueError("legacy contract origin or bytes changed; reconcile before dependent work")
    return active


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def snapshot_key(entries):
    return "snapshot:sha256:" + digest(canonical(entries))


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
    slug = work_slug(work)
    setup(root)
    item = safe(root, work)
    receipt = contract_origin(root, slug)
    if receipt is not None:
        verify_contract_origin(root, slug, receipt)
    if receipt is not None and work.startswith("work/"):
        item = verify_contract_origin(root, slug, receipt)
    artifact = safe(root, f".p2p/work/{slug}")
    if item.exists() and not item.is_file():
        raise ValueError("work item is not a file")
    if artifact.exists() and not artifact.is_dir():
        raise ValueError("artifact directory collides with a file")
    candidate = safe(root, f".p2p/work/{slug}/candidate.json")
    if candidate.exists():
        record = json.loads(candidate.read_text())
        allowed = {work}
        if receipt is not None:
            allowed.update({f".p2p/work/{slug}/contract.md", f"work/{slug}.md"})
        if not isinstance(record, dict) or record.get("work_item") not in allowed:
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


def require_ignored(root, *names):
    """Require this exact repo-local path to stay out of Git."""
    relatives = [PurePosixPath(name).as_posix() for name in names]
    for relative in relatives:
        if PurePosixPath(relative).is_absolute() or any(part in ("", ".", "..") for part in relative.split("/")):
            raise ValueError("unsafe repository path: " + relative)
    if not relatives:
        return
    result = subprocess.run(["git", "-C", str(root), "check-ignore", "--no-index", "-z", "--stdin"],
                            input=b"\0".join(os.fsencode(path) for path in relatives) + b"\0",
                            capture_output=True)
    if result.returncode not in (0, 1):
        raise ValueError("could not verify repo-local ignore rules")
    ignored = set(filter(None, result.stdout.split(b"\0")))
    exposed = [relative for relative in relatives if os.fsencode(relative) not in ignored]
    if exposed:
        raise ValueError("repo-local artifact path is not ignored: " + exposed[0])


def setup(root):
    """Validate the project-owned ignored P2P namespace without changing it."""
    root = Path(root).resolve()
    tracked = git(root, "ls-files", "-z", "--", ".p2p").split(b"\0")
    if any(tracked):
        raise ValueError("tracked P2P state blocks repo-local storage: " + ", ".join(
            name.decode() for name in tracked if name))
    state = root / ".p2p"
    if state.is_symlink() or (state.exists() and not state.is_dir()):
        raise ValueError("repo-local P2P state path collides with a non-directory: .p2p")
    ignore = root / ".gitignore"
    if not ignore.is_file() or "/.p2p/" not in ignore.read_text().splitlines():
        raise ValueError("project .gitignore must contain the exact /.p2p/ rule")
    result = subprocess.run(["git", "-C", str(root), "check-ignore", "--no-index", "--", ".p2p/work/probe"],
                            capture_output=True)
    if result.returncode != 0:
        raise ValueError("repo-local .p2p state is not effectively ignored; resolve conflicting ignore rules")
    detail = subprocess.run(["git", "-C", str(root), "check-ignore", "-v", "--no-index", "--", ".p2p/work/probe"],
                            capture_output=True, text=True, check=True).stdout
    if not detail.startswith(".gitignore:") and not detail.startswith(str(ignore) + ":"):
        raise ValueError("project .gitignore rule is overridden by a higher-priority ignore source")
    if state.is_dir():
        require_ignored(root, *(path.relative_to(root).as_posix() for path in state.rglob("*")
                                if path.is_file() or path.is_symlink()))
    return {"storage": "repository-local", "root": ".p2p/work"}


def snapshot(root, commit=None, exclude=()):
    excluded = set(exclude)
    entries = []
    if commit:
        records = git(root, "ls-tree", "-rz", "--full-tree", commit).split(b"\0")
        sources = []
        for record in filter(None, records):
            meta, name = record.split(b"\t", 1)
            mode, kind, oid = meta.decode().split()
            path = name.decode("utf-8")
            if path == ".p2p" or path.startswith(".p2p/") or path in excluded:
                continue
            if kind != "blob":
                raise ValueError(f"submodules are not supported: {path}")
            sources.append((path, mode, git(root, "cat-file", "blob", oid)))
    else:
        names = set(git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard").split(b"\0"))
        sources = []
        for name in filter(None, names):
            path = name.decode("utf-8")
            if path == ".p2p" or path.startswith(".p2p/") or path in excluded:
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


def tree_identity(entries):
    result = []
    for entry in entries:
        content = (base64.b64decode(entry["content_base64"], validate=True)
                   if entry["type"] == "file" else entry["target"].encode("utf-8"))
        result.append({"path": entry["path"], "type": entry["type"], "mode": entry["mode"],
                       "sha256": digest(content)})
    return result


def tree_changes(base, candidate):
    before = {entry["path"]: entry for entry in tree_identity(base)}
    after = {entry["path"]: entry for entry in tree_identity(candidate)}
    changes = []
    for path in sorted(before.keys() | after.keys()):
        old, new = before.get(path), after.get(path)
        if old == new:
            continue
        item = new or old
        changes.append({"path": path, "state": "deleted" if new is None else "added" if old is None else "modified",
                        "type": item["type"], "mode": item["mode"], "sha256": item["sha256"]})
    return changes


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


def bindings(root, work, require_trackable=True, _follow_origin=True):
    legacy_match = re.fullmatch(rf"work/(?P<slug>{SLUG})\.md", work)
    if legacy_match and _follow_origin:
        receipt = contract_origin(root, legacy_match.group("slug"))
        if receipt is not None:
            active = f".p2p/work/{legacy_match.group('slug')}/contract.md"
            verify_contract_origin(root, legacy_match.group("slug"), receipt)
            return bindings(root, active, require_trackable)
    if re.fullmatch(rf"\.p2p/work/{SLUG}/contract\.md", work):
        origin = contract_origin(root, work.split("/")[2])
        if origin is not None:
            verify_contract_origin(root, work.split("/")[2], origin)
            current = bindings(root, origin["path"], require_trackable, _follow_origin=False)
            if current != origin["binding_inputs"]:
                raise ValueError("legacy contract binding inputs changed; reconcile before dependent work")
            return current
    found = {}
    slug = work_slug(work)
    def is_contract(relative):
        return bool(re.fullmatch(rf"\.p2p/work/{SLUG}/contract\.md", relative))
    def is_imported_issue(relative):
        return bool(re.fullmatch(rf"\.p2p/work/{SLUG}/orchestration/issue\.json", relative))
    def is_imported_source(relative):
        return bool(re.fullmatch(
            rf"\.p2p/work/{re.escape(slug)}/source-(?:issue|pr-[0-9]+)\.md", relative))
    def visit(relative, from_contract_source=False):
        p2p_path = relative == ".p2p" or relative.startswith(".p2p/")
        allowed = is_contract(relative) or is_imported_issue(relative) or (
            from_contract_source and is_imported_source(relative))
        if p2p_path and not allowed:
            raise ValueError("generated artifacts cannot be binding inputs")
        if relative in found:
            return
        file = safe(root, relative)
        if require_trackable and not relative.startswith(".p2p/"):
            trackable(root, [relative])
        data = file.read_bytes()
        found[relative] = digest(data)
        for line in document_lines(data.decode()):
            if not re.match(r"^(Source|Parent|Parent contract):\s*", line):
                continue
            source_link = line.startswith("Source:")
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", line):
                if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                    continue
                target = target.split("#", 1)[0]
                if not target:
                    continue
                resolved = os.path.normpath(str(PurePosixPath(relative).parent / target))
                visit(resolved, from_contract_source=is_contract(relative) and source_link)
    if require_trackable and not is_contract(work):
        trackable(root, [work])
    visit(work)
    del found[work]
    return [{"path": path, "sha256": value} for path, value in sorted(found.items())]


def reconcile(root, legacy):
    """Copy an explicitly selected legacy contract into ignored active state."""
    match = re.fullmatch(rf"work/(?P<slug>{SLUG})\.md", legacy)
    if not match:
        raise ValueError("reconcile requires an explicit work/<slug>.md legacy contract")
    root = Path(root).resolve()
    source = safe(root, legacy)
    if not source.is_file():
        raise ValueError("legacy contract does not exist: " + legacy)
    # Resolve and hash every binding before copying; preserve the old relative-link origin.
    inputs = bindings(root, legacy)
    data = source.read_bytes()
    slug = match.group("slug")
    artifact = safe(root, f".p2p/work/{slug}")
    target = safe(root, f".p2p/work/{slug}/contract.md")
    origin = safe(root, f".p2p/work/{slug}/contract-origin.json")
    require_ignored(root, str(target.relative_to(root)), str(origin.relative_to(root)))
    if target.exists() and target.read_bytes() != data:
        raise ValueError("active contract conflicts with legacy bytes")
    receipt = {"schema": "promise-to-proof/contract-origin/v1", "path": legacy,
               "sha256": digest(data), "binding_inputs": inputs}
    receipt_bytes = json.dumps(receipt, indent=2, ensure_ascii=False).encode() + b"\n"
    if origin.exists() and origin.read_bytes() != receipt_bytes:
        raise ValueError("active contract origin conflicts with legacy binding identity")
    artifact.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        atomic_write(target, data, ignored_root=root)
    if not origin.exists():
        atomic_write(origin, receipt_bytes, ignored_root=root)
    if target.read_bytes() != data or digest(target.read_bytes()) != receipt["sha256"]:
        raise ValueError("active contract readback failed")
    return {"contract": str(target.relative_to(root)), "sha256": receipt["sha256"],
            "binding_inputs": inputs, "legacy_source_retained": legacy}


def atomic_write(target, data, ignored_root=None):
    """Retain either the previous complete bytes or the new complete bytes."""
    target = Path(target)
    temporary = target.with_name(target.name + "." + uuid.uuid4().hex)
    if ignored_root is not None:
        root = Path(os.path.abspath(ignored_root))
        for path in (target, temporary):
            try:
                relative = Path(os.path.abspath(path)).relative_to(root)
            except ValueError:
                continue  # Reconciled legacy state lives outside the project Git tree.
            require_ignored(root, relative.as_posix())
    with temporary.open("xb") as output:
        try:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
            os.replace(temporary, target)
            descriptor = os.open(target.parent, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        finally:
            if temporary.exists():
                temporary.unlink()


def save(root, work, name, data):
    item, artifact = paths(root, work)
    if not item.is_file():
        raise ValueError("work item does not exist")
    target = safe(artifact, name)
    if not work.startswith(".p2p/"):
        trackable(root, [work])
    require_ignored(root, str(target.relative_to(root)))
    if PurePosixPath(name).parts[0] == "history":
        raise ValueError("history is reserved")
    if target.exists():
        old = target.read_bytes()
        if old == data:
            return str(target.relative_to(root))
        committed = subprocess.run(
            ["git", "-C", str(root), "show", "HEAD:" + str(target.relative_to(root))],
            capture_output=True)
        if committed.returncode or committed.stdout != old:
            archived = safe(root, str(artifact.relative_to(root) / "history" / digest(old) / name))
            archived.parent.mkdir(parents=True, exist_ok=True)
            if archived.exists() and archived.read_bytes() != old:
                raise ValueError("history collision")
            atomic_write(archived, old, ignored_root=root)
    target.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(target, data, ignored_root=root)
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


def capture(root, work, base, commit=None, exclude=()):
    item, _ = paths(root, work)
    check_index(root)
    manifest = snapshot(root, exclude=exclude)
    chosen = full_commit(root, commit or "HEAD")
    committed = snapshot(root, chosen, exclude=exclude)
    if commit and manifest != committed:
        raise ValueError("working tree differs from requested committed candidate")
    comparison_base = full_commit(root, base)
    base_manifest = snapshot(root, comparison_base, exclude=exclude)
    record = {"work_item": work, "work_item_sha256": digest(item.read_bytes()),
              "comparison_base": comparison_base, "binding_inputs": bindings(root, work),
              "key": snapshot_key(manifest), "changes": tree_changes(base_manifest, manifest)}
    if manifest == committed:
        record["commit"] = chosen
    save(root, work, "candidate.json", json.dumps(record, indent=2, ensure_ascii=False).encode() + b"\n")
    return record


def validate(root, work, base, exclude=()):
    check_index(root)
    item, artifact = paths(root, work)
    record = json.loads((artifact / "candidate.json").read_text())
    shared = {"work_item", "work_item_sha256", "comparison_base", "binding_inputs"}
    valid = (shared | {"commit"}, shared | {"key", "manifest"},
             shared | {"commit", "changes"}, shared | {"key", "changes"},
             shared | {"key", "changes", "commit"})
    if set(record) not in valid:
        raise ValueError("candidate must contain exactly one committed or snapshot identity")
    for name in ("work_item", "work_item_sha256", "comparison_base", "commit" if "commit" in record else "key"):
        if not isinstance(record[name], str):
            raise ValueError("candidate field must be a string: " + name)
    if not isinstance(record["binding_inputs"], list):
        raise ValueError("binding_inputs must be an array")
    if "manifest" in record and not isinstance(record["manifest"], list):
        raise ValueError("snapshot manifest must be an array")
    if "changes" in record:
        changes = record["changes"]
        if not isinstance(changes, list) or any(
            not isinstance(entry, dict) or set(entry) != {"path", "state", "type", "mode", "sha256"} or
            not isinstance(entry["path"], str) or not entry["path"] or "\\" in entry["path"] or "\0" in entry["path"] or
            entry["path"].startswith("/") or any(part in ("", ".", "..") or part.lower() == ".git"
                                                 for part in entry["path"].split("/")) or
            entry["state"] not in ("added", "modified", "deleted") or entry["type"] not in ("file", "symlink") or
            entry["mode"] not in (("100644", "100755") if entry["type"] == "file" else ("120000",)) or
            not isinstance(entry["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])
            for entry in changes
        ) or len({entry["path"] for entry in changes}) != len(changes) or changes != sorted(changes, key=lambda entry: entry["path"]):
            raise ValueError("candidate compact identity is malformed")
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
        expected = snapshot(root, full_commit(root, record["commit"]), exclude=exclude)
    else:
        expected = record.get("manifest")
        if expected is not None and record["key"] != snapshot_key(expected):
            raise ValueError("snapshot digest mismatch")
    base_manifest = snapshot(root, full_commit(root, record["comparison_base"]), exclude=exclude)
    current = snapshot(root, exclude=exclude)
    if expected is not None and current != expected:
        raise ValueError("product candidate changed")
    if "changes" in record and tree_changes(base_manifest, current) != record["changes"]:
        raise ValueError("product candidate changed")
    if "key" in record and record["key"] != snapshot_key(current):
        raise ValueError("snapshot digest mismatch")
    if "changes" not in record and current != expected:
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
                if not relative.startswith(".p2p/"):
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
    reconcile_command = commands.add_parser("reconcile")
    reconcile_command.add_argument("work")
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
        elif args.command == "reconcile":
            result = reconcile(root, args.work)
        elif args.command == "create":
            item, artifact = paths(root, args.work)
            if artifact.exists() and any(artifact.iterdir()):
                raise ValueError("artifact directory already contains records")
            if not args.work.startswith(".p2p/"):
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
