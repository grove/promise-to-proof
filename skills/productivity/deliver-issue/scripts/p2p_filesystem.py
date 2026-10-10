#!/usr/bin/env python3
"""P2P storage paths, access probes and exact candidate identities (stdlib only)."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import uuid


SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
WORK = re.compile(rf"(?:work/(?P<legacy>{SLUG})\.md|\.p2p/work/(?P<active>{SLUG})/contract\.md)\Z")
CHECKPOINT_SCHEMA = "promise-to-proof/checkpoint/v1"
CHECKPOINT_LIMIT = 262144
CHECKPOINT_DIRECTORY = "p2p-state"


def product_path(path):
    return path.split("/", 1)[0] not in (".p2p", CHECKPOINT_DIRECTORY)


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


def git_blobs(root, object_ids):
    """Read exact Git blobs in one process, preserving binary data and order."""
    object_ids = tuple(dict.fromkeys(object_ids))
    if not object_ids:
        return {}
    result = subprocess.run(["git", "-C", str(root), "cat-file", "--batch"],
                            input="".join(oid + "\n" for oid in object_ids).encode("ascii"),
                            capture_output=True)
    if result.returncode:
        raise ValueError(result.stderr.decode().strip() or "Git blob batch failed")
    data, offset, blobs = result.stdout, 0, {}
    for oid in object_ids:
        newline = data.find(b"\n", offset)
        header = data[offset:newline].split(b" ") if newline >= 0 else []
        if (len(header) != 3 or header[0] != oid.encode("ascii") or
                header[1] != b"blob" or not header[2].isdigit()):
            raise ValueError("missing or malformed Git blob batch response: " + oid)
        start = newline + 1
        end = start + int(header[2])
        if end >= len(data) or data[end:end + 1] != b"\n":
            raise ValueError("truncated Git blob batch response: " + oid)
        blobs[oid] = data[start:end]
        offset = end + 1
    if offset != len(data):
        raise ValueError("unexpected trailing Git blob batch response")
    return blobs


def execution_directory(root, work):
    """Reuse a retained location; configuration selects only new execution state."""
    root = Path(root).resolve()
    common = git(root, "rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip()
    repo_id = root.name + "-" + digest(str(Path(common).resolve()).encode())[:16]
    slug = work_slug(work)
    receipt = safe(root, f".p2p/work/{slug}/execution-location.json")
    default = Path.home() / ".p2p/executions" / repo_id / slug
    default_present = default.exists() and any(default.iterdir())
    if receipt.is_file():
        record = json.loads(receipt.read_text())
        if not isinstance(record, dict) or record.get("schema") != "promise-to-proof/execution-location/v1":
            raise ValueError("invalid execution location receipt")
        directory = Path(record["directory"])
        if directory.parts[-2:] != (repo_id, slug):
            raise ValueError("execution location belongs to another repository or work item")
    elif default_present:
        directory = default  # Existing candidates stay in place, including before receipts existed.
    else:
        configured = os.environ.get("P2P_EXECUTION_ROOT", str(Path.home() / ".p2p/executions"))
        execution_root = Path(configured).expanduser()
        if not execution_root.is_absolute():
            raise ValueError("P2P_EXECUTION_ROOT must be an absolute directory outside the source checkout")
        directory = execution_root / repo_id / slug
    if not directory.is_absolute():
        raise ValueError("execution location must be absolute")
    for path in (directory, directory.parent, directory.parent.parent):
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            raise ValueError("execution location is not a regular directory: " + str(path))
    directory = directory.resolve()
    if directory == root or root in directory.parents:
        raise ValueError("external P2P execution path resolves inside the source checkout")
    if receipt.is_file() and default_present and directory != default.resolve():
        raise ValueError("both retained and default execution roots exist; reconcile without overwriting either")
    return directory


def probe_write(directory):
    """Exercise this process's actual write boundary without changing existing files."""
    directory = Path(directory)
    try:
        with tempfile.TemporaryFile(prefix=".p2p-access-", dir=directory) as probe:
            probe.write(b"p2p-access\n")
            probe.flush()
            probe.seek(0)
            if probe.read() != b"p2p-access\n":
                raise ValueError("write probe readback failed: " + str(directory))
    except OSError as error:
        raise ValueError("write access required for " + str(directory) + ": " + str(error)) from error


def prepare_execution(root, work):
    """Check and retain the selected external root before implementation starts."""
    _, records = paths(root, work)
    directory = execution_directory(root, work)
    directory.mkdir(parents=True, exist_ok=True)
    records.mkdir(parents=True, exist_ok=True)
    for path in (directory, records):
        probe_write(path)
    receipt = safe(records, "execution-location.json")
    if not receipt.exists():
        data = canonical({"schema": "promise-to-proof/execution-location/v1", "directory": str(directory)}) + b"\n"
        atomic_write(receipt, data, ignored_root=root)
        if receipt.read_bytes() != data:
            raise ValueError("execution location readback failed")
    return {"execution_directory": str(directory), "records_directory": str(records)}


def publication_access(root, work, workspace=None):
    """Check the worktree, actual Git metadata and records before preview approval."""
    _, records = paths(root, work)
    workspace = Path(workspace) if workspace is not None else execution_directory(root, work) / "runtime/workspace"
    return workspace_access(workspace, records, operator_root=root)


def workspace_access(workspace, records, operator_root=None):
    """Probe actual Git storage; publication additionally requires checkout isolation."""
    workspace, records = Path(workspace), Path(records)
    workspace = workspace.resolve()
    git_dir = Path(git(workspace, "rev-parse", "--absolute-git-dir").decode().strip()).resolve()
    common = Path(git(workspace, "rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip()).resolve()
    root = Path(operator_root).resolve() if operator_root is not None else None
    if root is not None:
        if workspace == root or root in workspace.parents:
            raise ValueError("publication workspace must be outside the operator's checkout")
        source_common = Path(git(root, "rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip()).resolve()
        if common == source_common or git_dir == root or root in git_dir.parents or common == root or root in common.parents:
            raise ValueError("publication Git metadata must be isolated from the operator's checkout")
    records.mkdir(parents=True, exist_ok=True)
    directories = dict.fromkeys((workspace, git_dir, common, common / "objects", common / "refs", records))
    for directory in directories:
        if directory != records and (directory.is_symlink() or (root is not None and root in directory.resolve().parents)):
            raise ValueError("publication write directory is not isolated: " + str(directory))
        probe_write(directory)
    return {"status": "WRITABLE", "workspace": str(workspace), "git_directory": str(git_dir),
            "git_common_directory": str(common), "records_directory": str(records),
            "probed_directories": [str(path) for path in directories]}


def safe(root, relative, leaf_symlink=False):
    path = PurePosixPath(relative)
    if path.is_absolute() or any(p in ("", ".", "..") or p.lower() == ".git" for p in relative.split("/")):
        raise ValueError(f"unsafe repository path: {relative}")
    current = root
    for i, part in enumerate(path.parts):
        current = current / part
        if current.is_symlink() and not (leaf_symlink and i == len(path.parts) - 1):
            raise ValueError(f"symlink in repository path: {relative}")
        if i < len(path.parts) - 1 and current.exists() and not current.is_dir():
            raise ValueError(f"non-directory in repository path: {relative}")
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
    probe = ".p2p/work/probe"
    names = [probe]
    if state.is_dir():
        names.extend(path.relative_to(root).as_posix() for path in state.rglob("*")
                     if path.is_file() or path.is_symlink())
    # One batch verifies both the project-owned rule and every existing record.
    # Recheck on each call: ignore files and index entries may change mid-delivery.
    result = subprocess.run(["git", "-C", str(root), "check-ignore", "-v", "-z", "--no-index", "--stdin"],
                            input=b"\0".join(os.fsencode(name) for name in names) + b"\0",
                            capture_output=True)
    if result.returncode not in (0, 1):
        raise ValueError("repo-local .p2p state is not effectively ignored; resolve conflicting ignore rules")
    fields = result.stdout.split(b"\0")
    if fields[-1] or (len(fields) - 1) % 4:
        raise ValueError("could not verify repo-local ignore rules")
    matches = {fields[index + 3]: (fields[index], fields[index + 2])
               for index in range(0, len(fields) - 1, 4)}
    for name in names:
        match = matches.get(os.fsencode(name))
        if match is None or match[1].startswith(b"!"):
            if name == probe:
                raise ValueError("repo-local .p2p state is not effectively ignored; resolve conflicting ignore rules")
            raise ValueError("repo-local artifact path is not ignored: " + name)
    if matches[os.fsencode(probe)][0] not in (b".gitignore", os.fsencode(ignore)):
        raise ValueError("project .gitignore rule is overridden by a higher-priority ignore source")
    return {"storage": "repository-local", "root": ".p2p/work"}


def snapshot(root, commit=None, exclude=()):
    excluded = set(exclude)
    entries = []
    if commit:
        records = git(root, "ls-tree", "-rz", "--full-tree", commit).split(b"\0")
        objects = []
        for record in filter(None, records):
            meta, name = record.split(b"\t", 1)
            mode, kind, oid = meta.decode().split()
            path = name.decode("utf-8")
            if not product_path(path) or path in excluded:
                continue
            if kind != "blob":
                raise ValueError(f"submodules are not supported: {path}")
            objects.append((path, mode, oid))
        blobs = git_blobs(root, (oid for _, _, oid in objects))
        sources = [(path, mode, blobs[oid]) for path, mode, oid in objects]
    else:
        names = set(git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard").split(b"\0"))
        sources = []
        for name in filter(None, names):
            path = name.decode("utf-8")
            if not product_path(path) or path in excluded:
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
        if relative.split("/", 1)[0] == CHECKPOINT_DIRECTORY:
            raise ValueError("generated artifacts cannot be binding inputs")
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



def entry_source(root, request, issue_repository=None):
    """Resolve a user-facing request without creating a second delivery state.

    This only selects a saved contract or a planning/restore handoff. It never
    infers approval, source currency, a current verdict, or write authority.
    """
    root = Path(root).resolve()
    if not isinstance(request, str) or not request.strip():
        raise ValueError("provide one nonempty delivery request")
    request = request.strip()
    if WORK.fullmatch(request):
        selected = safe(root, request)
        if selected.is_file():
            return {"action": "USE", "kind": "contract", "work_item": request,
                    "next": "Validate the saved agreement, approvals, current sources and controller status."}
        checkpoint_file = safe(root, f"{CHECKPOINT_DIRECTORY}/{work_slug(request)}.json")
        if checkpoint_file.is_file():
            record = json.loads(checkpoint_file.read_bytes())
            if record.get("schema") != CHECKPOINT_SCHEMA or record.get("work_item") != request:
                raise ValueError("checkpoint conflicts with the requested contract; reconcile it before restoration")
            return {"action": "RESTORE", "kind": "contract", "work_item": request,
                    "checkpoint": checkpoint_file.relative_to(root).as_posix(),
                    "next": "Restore the validated checkpoint before resuming; never infer approval from its presence."}
        raise ValueError("contract is missing; restore its checkpoint or provide its original source")

    issue = re.fullmatch(r"#([1-9][0-9]*)", request)
    if issue:
        if not issue_repository or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", issue_repository):
            raise ValueError("issue number needs an unambiguous configured OWNER/REPO; read the active issue-tracker instructions")
        kind = "issue"
        identity = f"https://github.com/{issue_repository}/issues/{issue[1]}"
        fingerprint = digest(identity.encode())
        stem = "issue-" + issue[1] + "-" + fingerprint[:12]
    elif (request.endswith(".md") or
          ("/" in request and not any(ch.isspace() for ch in request))):
        if request.startswith(".p2p/") or request.startswith(CHECKPOINT_DIRECTORY + "/"):
            raise ValueError("generated state is not a project specification; provide the exact contract path")
        source_file = safe(root, request)
        if not source_file.is_file():
            raise ValueError("specification does not exist: " + request)
        trackable(root, [request])
        kind = "spec"
        identity = request
        fingerprint = digest(source_file.read_bytes())
        stem = re.sub(r"[^a-z0-9]+", "-", PurePosixPath(request).stem.lower()).strip("-")
        stem = (stem[:40].strip("-") or "spec") + "-" + digest(request.encode())[:12]
    else:
        kind = "text"
        identity = request
        fingerprint = digest(request.encode("utf-8"))
        stem = "request-" + fingerprint[:16]

    def matches(work, contract_text, handoff):
        if kind == "issue":
            return any(re.fullmatch(r"Source attribution:\s*" + re.escape(identity) + r"(?:[;\s].*)?", line.strip())
                       for line in document_lines(contract_text))
        if kind == "spec":
            for line in document_lines(contract_text):
                if not re.match(r"^Source:\s*", line):
                    continue
                for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", line):
                    if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                        continue
                    relative = os.path.normpath(str(PurePosixPath(work).parent / target.split("#", 1)[0]))
                    if relative == identity:
                        return True
            return False
        for line in document_lines(handoff or ""):
            if not line.startswith("Entry request JSON: "):
                continue
            try:
                saved = json.loads(line[len("Entry request JSON: "):])
            except (ValueError, TypeError):
                raise ValueError("saved entry request provenance is malformed: " + work)
            if saved == request:
                return True
        return False

    def checkpoint_text(checkpoint, relative):
        rows = [row for row in checkpoint.get("files", []) if
                row.get("scope") == "project" and row.get("path") == relative]
        if len(rows) != 1:
            return None
        row = rows[0]
        sha = row.get("sha256")
        if not isinstance(sha, str) or not re.fullmatch(r"[a-f0-9]{64}", sha):
            raise ValueError("checkpoint file digest is invalid: " + relative)
        text = checkpoint.get("texts", {}).get(sha)
        if text is None and row.get("git_commit"):
            try:
                text = git(root, "show", row["git_commit"] + ":" + relative).decode("utf-8")
            except (ValueError, UnicodeError):
                return None
        if text is not None and digest(text.encode("utf-8")) != sha:
            raise ValueError("checkpoint source bytes differ from saved digest: " + relative)
        return text

    candidates = {}
    for file in sorted((root / ".p2p/work").glob("*/contract.md")):
        relative = file.relative_to(root).as_posix()
        if not WORK.fullmatch(relative):
            continue
        content = safe(root, relative).read_text(encoding="utf-8")
        handoff = safe(root, f".p2p/work/{work_slug(relative)}/planning-handoff.md")
        provenance = handoff.read_text(encoding="utf-8") if handoff.is_file() else None
        if matches(relative, content, provenance):
            candidates[relative] = {"action": "USE", "work_item": relative}
    for file in sorted((root / CHECKPOINT_DIRECTORY).glob("*.json")):
        relative = file.relative_to(root).as_posix()
        record = json.loads(safe(root, relative).read_bytes())
        if record.get("schema") != CHECKPOINT_SCHEMA or not WORK.fullmatch(record.get("work_item", "")):
            continue
        work = record["work_item"]
        if work in candidates:
            continue
        content = checkpoint_text(record, work)
        provenance = checkpoint_text(record, f".p2p/work/{work_slug(work)}/planning-handoff.md")
        if content and matches(work, content, provenance):
            candidates[work] = {"action": "RESTORE", "work_item": work, "checkpoint": relative}
    if len(candidates) > 1:
        raise ValueError("multiple saved contracts match this request; select the exact contract: " +
                         ", ".join(sorted(candidates)))
    if candidates:
        chosen = next(iter(candidates.values()))
        return chosen | {"kind": kind, "source_sha256": fingerprint,
                         "next": "Check exact source changes, agreement and approval identity; restore if needed, then status/resume before planning."}
    suggested = f".p2p/work/{stem}/contract.md"
    if safe(root, suggested).exists():
        raise ValueError("suggested work-item path already belongs to different source: " + suggested)
    return {"action": "PLAN", "kind": kind, "source_sha256": fingerprint,
            "suggested_work_item": suggested,
            "next": "Use existing plan-acceptance and audit within delivery, save exact source provenance and contract, then follow existing sizing and admission."}


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
    if name != "candidate.json":
        checkpoint(root, work)
    return str(target.relative_to(root))


def full_commit(root, ref):
    return git(root, "rev-parse", "--verify", "--end-of-options", ref + "^{commit}").decode().strip()


def check_index(root):
    # Retain one version, including modes even when Git ignores filesystem mode changes.
    staged = {name.decode() for name in git(root, "diff", "--cached", "--name-only", "-z").split(b"\0")
              if name and product_path(name.decode())}
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


def product_index_sha256(root):
    records = git(root, "ls-files", "--stage", "-z").split(b"\0")
    return digest(b"\0".join(record for record in records if record and product_path(record.split(b"\t", 1)[1].decode())))


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


def checkpoint_path(root, work, destination=None):
    slug = work_slug(work)
    shared = safe(root, f"{CHECKPOINT_DIRECTORY}/{slug}.json")
    local = safe(root, f".p2p/work/{slug}/checkpoint.json")
    if shared.exists() and local.exists():
        raise ValueError("conflicting Git and GitHub checkpoints; reconcile the selected destination")
    existing = shared if shared.exists() else local if local.exists() else None
    if existing:
        previous = json.loads(existing.read_bytes())
        if previous.get("schema") != CHECKPOINT_SCHEMA or previous.get("work_item") != work:
            raise ValueError("checkpoint path belongs to another record; preserve and reconcile it")
        if destination is not None and destination != previous.get("destination"):
            raise ValueError("checkpoint destination changed; reconcile the existing checkpoint first")
        destination = previous["destination"]
    destination = destination or {"kind": "git"}
    if destination == {"kind": "git"}:
        trackable(root, [shared.relative_to(root).as_posix()])
        return shared, destination
    if (set(destination) != {"kind", "repository", "issue"} or destination["kind"] != "github" or
            not re.fullmatch(r"[\w.-]+/[\w.-]+", destination["repository"]) or
            type(destination["issue"]) is not int or destination["issue"] < 1):
        raise ValueError("invalid checkpoint destination")
    require_ignored(root, local.relative_to(root).as_posix())
    return local, destination


def checkpoint_documents(root, work):
    """Collect live agreements and referenced receipts, not every draft or log."""
    selected = set()
    pending = [work]
    records = ("contract.md", "contract-origin.json", "planning-handoff.md", "delivery-shape.md", "slicing.md",
               "slicing-approval.md", "source-publication.md", "tracker-publication.json",
               "tracker-publication.md", "publication.md", "archive.md", "implementation.md",
               "review.md", "proof.md", "audit.md", "repair.md", "candidate.json", "retrospective.md")
    owners = set()
    referenced_hashes = set()
    inspected_hashes = set()
    while pending:
        relative = pending.pop()
        if relative in selected:
            continue
        file = safe(root, relative)
        if not file.is_file():
            raise ValueError("missing checkpoint input: " + relative)
        selected.add(relative)
        if file.suffix == ".md":
            referenced_hashes.update(re.findall(r"[a-f0-9]{64}", file.read_text()))
        if WORK.fullmatch(relative):
            owner = f".p2p/work/{work_slug(relative)}"
            if owner not in owners:
                owners.add(owner)
                pending.extend(owner + "/" + name for name in records if safe(root, owner + "/" + name).exists())
                artifacts = safe(root, owner + "/artifacts")
                pending.extend(str(p.relative_to(root)) for p in artifacts.glob("*") if p.is_file())
            pending.extend(row["path"] for row in bindings(root, relative))
            pending.extend(children(root, relative))
        if relative.startswith(".p2p/") and file.suffix == ".md":
            origin = PurePosixPath(relative).parent
            if "history" in origin.parts:
                origin = PurePosixPath(*origin.parts[:origin.parts.index("history")])
            text = file.read_text()
            targets = re.findall(r"\[[^\]]*\]\(([^)]+)\)", text)
            for line in document_lines(text):
                if line.startswith("Approval source:"):
                    plain = re.sub(r"\[[^\]]*\]\([^)]+\)|[a-zA-Z][a-zA-Z0-9+.-]*://\S+", "", line)
                    targets.extend(re.findall(r"(?<![\w/])([.\w/-]+\.md)(?=$|[\s.,;`])", plain))
            for target in targets:
                if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                    continue
                target = target.split("#", 1)[0]
                if not target:
                    continue
                linked = os.path.normpath(str(origin / target))
                parts = PurePosixPath(linked).parts
                # Captured source snapshots retain their original document links;
                # code/README links are not workflow receipts. Binding inputs and
                # child contracts are independently checked above.
                if (len(parts) > 3 and parts[:2] == (".p2p", "work") and
                        safe(root, '/'.join(parts[:3])).is_dir()):
                    safe(root, linked)
                    pending.append(linked)
        # Older approval tables sometimes name historical drafts only by digest.
        # Preserve those exact retained bytes without exporting every old draft.
        for sha in referenced_hashes - inspected_hashes:
            for historical in (root / '.p2p/work').glob('*/history/' + sha + '/**/*'):
                if historical.is_file() and str(historical.relative_to(root)) not in selected:
                    pending.append(str(historical.relative_to(root)))
            inspected_hashes.add(sha)
    return sorted(selected)


def checkpoint(root, work, destination=None, execution=None, candidate_commit=None, extra_files=()):
    """Write bounded, deduplicated metadata; never perform a Git or tracker write."""
    root = Path(root).resolve()
    paths(root, work)
    target, destination = checkpoint_path(root, work, destination)
    previous = json.loads(target.read_bytes()) if target.exists() else {}
    # Filesystem saves may occur within a controller stage. Keep its last complete
    # boundary until the controller explicitly replaces it, rather than inventing one.
    if execution is None and previous.get("execution") is not None:
        return {"status": "LOCAL_ONLY", "path": str(target.relative_to(root)),
                "bytes": target.stat().st_size, "blocker": "controller checkpoint needs its next completed boundary"}
    files, texts, required = [], {}, set()
    try:
        head = full_commit(root, "HEAD")
    except ValueError:
        head = None
    committed_checkpoint = subprocess.run(["git", "-C", str(root), "show",
                                          str(head) + ":" + str(target.relative_to(root))], capture_output=True)
    retained_texts = json.loads(committed_checkpoint.stdout).get("texts", {}) if committed_checkpoint.returncode == 0 else {}
    def add(scope, relative, data):
        safe(root, relative)
        sha = digest(data)
        existing = next((row for row in files if row["scope"] == scope and row["path"] == relative), None)
        if existing:
            if existing["sha256"] != sha:
                raise ValueError("conflicting checkpoint input: " + relative)
            return
        row = {"scope": scope, "path": relative, "sha256": sha}
        retained = next((row for row in previous.get("files", []) if row["scope"] == scope and row["path"] == relative and
                         row["sha256"] == sha and row.get("git_commit")), None)
        if retained:
            row.update({key: retained[key] for key in ("git_commit", "checkpoint_path") if key in retained})
            required.add(retained["git_commit"])
            files.append(row)
            return
        if destination["kind"] == "git" and sha in retained_texts and retained_texts[sha].encode() == data:
            row.update(git_commit=head, checkpoint_path=str(target.relative_to(root)))
            required.add(head)
            files.append(row)
            return
        commit = retained["git_commit"] if retained else head
        committed = subprocess.run(["git", "-C", str(root), "show", str(commit) + ":" + relative], capture_output=True)
        if scope == "project" and product_path(relative) and committed.returncode == 0 and committed.stdout == data:
            row["git_commit"] = commit
            required.add(commit)
        else:
            texts[sha] = data.decode("utf-8")
        files.append(row)
    retained_agreement = {relative: data for scope, relative, data in extra_files if scope == "agreement"}
    if execution is not None and not safe(root, work).is_file():
        selected = [work, *(row["path"] for row in execution["binding_inputs"]),
                    *(row["path"] for row in execution.get("routing_records", []))]
    else:
        selected = checkpoint_documents(root, work)
    for relative in sorted(set(selected)):
        file = safe(root, relative)
        add("project", relative, file.read_bytes() if file.is_file() else retained_agreement[relative])
    for scope, relative, data in extra_files:
        add(scope, relative, data)
    if len({(row["scope"], row["path"]) for row in files}) != len(files):
        raise ValueError("duplicate checkpoint input")
    candidate_record = next((safe(root, path) for path in (f".p2p/work/{work_slug(work)}/artifacts/candidate.json",
                                                         f".p2p/work/{work_slug(work)}/candidate.json") if safe(root, path).is_file()), None)
    if candidate_record and execution is None:
        record = json.loads(candidate_record.read_bytes())
        candidate_commit = candidate_commit or record.get("commit")
        if candidate_commit and record.get("key"):
            agreement_paths = [work, *(row["path"] for row in bindings(root, work))]
            expected = snapshot_key(snapshot(root, candidate_commit, exclude=agreement_paths if "/artifacts/" in str(candidate_record) else ()))
            if record["key"] != expected:
                raise ValueError("checkpoint candidate commit differs from the saved candidate")
    if candidate_commit:
        if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", candidate_commit):
            raise ValueError("checkpoint candidate needs a full commit SHA")
        required.add(candidate_commit)
    if execution:
        required.update([execution["comparison_base"], execution["local_git_base"]["local_commit"]])
        execution["source_recovery_commit"] = None
        for commit in (execution["source_head"], execution["starting_commit"], execution["local_git_generations"][0]["commit"]):
            if snapshot_key(snapshot(root, commit)) == execution["source_tree_key"]:
                required.add(commit)
                execution["source_recovery_commit"] = commit
                break
    value = {"schema": CHECKPOINT_SCHEMA, "work_item": work, "destination": destination,
             "files": sorted(files, key=lambda row: (row["scope"], row["path"])), "texts": texts,
             "required_commits": sorted(required), "candidate_commit": candidate_commit,
             "execution": execution}
    data = canonical(value) + b"\n"
    if len(data) > CHECKPOINT_LIMIT:
        raise ValueError(f"checkpoint exceeds 256 KiB: {len(data)} bytes; retain local state and move essential large evidence to durable referenced storage")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_bytes() == data:
        pass
    else:
        atomic_write(target, data, ignored_root=root if destination["kind"] == "github" else None)
    if target.read_bytes() != data:
        raise ValueError("checkpoint readback failed")
    return {"status": "LOCAL_ONLY", "path": str(target.relative_to(root)), "sha256": digest(data), "bytes": len(data)}


def read_checkpoint(root, data):
    if len(data) > CHECKPOINT_LIMIT:
        raise ValueError("checkpoint exceeds 256 KiB")
    value = json.loads(data)
    fields = {"schema", "work_item", "destination", "files", "texts", "required_commits", "candidate_commit", "execution"}
    if not isinstance(value, dict) or set(value) != fields or value["schema"] != CHECKPOINT_SCHEMA:
        raise ValueError("invalid checkpoint schema")
    work_slug(value["work_item"])
    if (not isinstance(value["texts"], dict) or not isinstance(value["files"], list) or
            not isinstance(value["required_commits"], list)):
        raise ValueError("invalid checkpoint files/texts")
    for sha, text in value["texts"].items():
        if not isinstance(text, str) or digest(text.encode()) != sha:
            raise ValueError("checkpoint text hash mismatch")
    seen, contents = set(), []
    for row in value["files"]:
        if (not isinstance(row, dict) or set(row) not in ({"scope", "path", "sha256"}, {"scope", "path", "sha256", "git_commit"},
                                                       {"scope", "path", "sha256", "git_commit", "checkpoint_path"}) or
                row["scope"] not in ("project", "runtime", "local", "agreement")):
            raise ValueError("invalid checkpoint file")
        safe(root, row["path"])
        if row["scope"] == "runtime" and not re.fullmatch(
                r"base-tree-key|instructions/[a-f0-9]{64}\.json|generations/[0-9]{6}\.json|(?:previous-records|superseded-records)/[\w.-]+|attempts/[a-f0-9-]+/(?:report|exit|portable-receipt)\.json", row["path"]):
            raise ValueError("unsupported checkpoint runtime path")
        if row["scope"] == "local" and row["path"] not in ("implementation.md", "repair.md", "review.md", "proof.md", "mandate.json"):
            raise ValueError("unsupported checkpoint local path")
        key = (row["scope"], row["path"])
        if key in seen or not product_path(row["path"]) and row["path"].startswith(CHECKPOINT_DIRECTORY + "/"):
            raise ValueError("duplicate or recursive checkpoint file")
        seen.add(key)
        if "git_commit" in row:
            if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", row["git_commit"]) or row["git_commit"] not in value["required_commits"]:
                raise ValueError("checkpoint document commit is not retained")
            if "checkpoint_path" in row:
                if not re.fullmatch(rf"{CHECKPOINT_DIRECTORY}/{SLUG}\.json", row["checkpoint_path"]):
                    raise ValueError("invalid retained checkpoint path")
                retained = json.loads(git(root, "show", row["git_commit"] + ":" + row["checkpoint_path"]))
                if retained.get("schema") != CHECKPOINT_SCHEMA:
                    raise ValueError("invalid retained checkpoint schema")
                content = retained["texts"][row["sha256"]].encode()
            else:
                content = git(root, "show", row["git_commit"] + ":" + row["path"])
        else:
            content = value["texts"][row["sha256"]].encode()
        if digest(content) != row["sha256"]:
            raise ValueError("checkpoint file hash mismatch: " + row["path"])
        contents.append((row["scope"], row["path"], content))
    for commit in value["required_commits"]:
        if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", commit) or full_commit(root, commit) != commit:
            raise ValueError("missing or invalid checkpoint Git commit")
    if ("project", value["work_item"]) not in seen:
        raise ValueError("checkpoint contract missing")
    if value["candidate_commit"] and value["candidate_commit"] not in value["required_commits"]:
        raise ValueError("checkpoint candidate commit missing")
    if not value["candidate_commit"] and any(relative.endswith("/candidate.json") and json.loads(content).get("key")
                                              for _, relative, content in contents):
        raise ValueError("candidate payload has no recoverable Git commit; retain local execution state")
    execution = value["execution"]
    if execution is not None:
        if not isinstance(execution, dict) or execution.get("work_item") != value["work_item"]:
            raise ValueError("invalid checkpoint execution")
        allowed = {value["work_item"], *(row["path"] for row in execution["binding_inputs"])}
        origin_path = f'.p2p/work/{work_slug(value["work_item"])}/contract-origin.json'
        origin_data = next((content for scope, relative, content in contents if scope == "project" and relative == origin_path), None)
        if origin_data is not None:
            origin = json.loads(origin_data)
            if origin.get("schema") != "promise-to-proof/contract-origin/v1" or origin.get("sha256") != execution["contract"]["sha256"]:
                raise ValueError("checkpoint legacy contract origin mismatch")
            allowed.update({origin_path, origin["path"], f'.p2p/work/{work_slug(value["work_item"])}/contract.md'})
        if any(scope == "agreement" and relative not in allowed for scope, relative, _ in contents):
            raise ValueError("unsupported checkpoint agreement path")
        indexed = {(scope, relative): content for scope, relative, content in contents}
        checkpoint_instructions(execution, indexed)
        contract = indexed[("project", value["work_item"])]
        if digest(contract) != execution["contract"]["sha256"] or contract.decode() != execution["contract"]["content"]:
            raise ValueError("checkpoint agreement identity mismatch")
        for attempt in execution["attempts"]:
            prefix = "attempts/" + attempt["id"] + "/"
            receipt = indexed[("runtime", prefix + "portable-receipt.json")]
            parsed = json.loads(receipt)
            end = json.loads(indexed[("runtime", prefix + "exit.json")])
            if (digest(receipt) != attempt["portable_receipt_sha256"] or parsed["exit"] != end or
                    parsed["attempt_id"] != attempt["id"] or end["attempt_id"] != attempt["id"] or end["inputs"] != attempt["inputs"]):
                raise ValueError("checkpoint stage receipt identity mismatch")
            if attempt.get("report"):
                report = indexed[("runtime", attempt["report"])]
                if digest(report) != attempt["report_sha256"] or parsed["host"]["message"].encode() != report:
                    raise ValueError("checkpoint stage report identity mismatch")
        agreement_paths = execution.get("agreement_paths", ())
        candidate = snapshot(root, value["candidate_commit"])
        if (snapshot_key(candidate) != execution["candidate"]["key"] or
                tree_changes(snapshot(root, execution["comparison_base"], exclude=agreement_paths), candidate) != execution["candidate"]["changes"]):
            raise ValueError("checkpoint candidate identity mismatch")
    return value, contents


def checkpoint_instructions(execution, indexed):
    """Validate instruction provenance before a portable restore writes anything."""
    import p2p_instructions as instructions
    bundles = {}
    for (scope, relative), data in indexed.items():
        match = re.fullmatch(r"instructions/([a-f0-9]{64})\.json", relative)
        if scope == "runtime" and match:
            bundles[match[1]] = instructions.decode(data, match[1])
    active = execution.get("instruction_identity")
    history = execution.get("instruction_history", [])
    attempt_identities = []
    for attempt in execution.get("attempts", []):
        inputs = attempt.get("inputs", {})
        if not isinstance(inputs, dict):
            raise ValueError("invalid checkpoint stage inputs")
        candidate = inputs.get("candidate", {})
        identities = [inputs.get("instruction_identity")]
        if isinstance(candidate, dict):
            identities.append(candidate.get("instruction_identity"))
        attempt_identities.append([value for value in identities if value is not None])
    if active is None:
        if bundles or history or any(attempt_identities):
            raise ValueError("checkpoint instruction provenance lacks its active identity")
        return  # Legacy receipts retain their original, limited skill identity.
    if not isinstance(active, str) or not re.fullmatch(r"[a-f0-9]{64}", active) or not isinstance(history, list):
        raise ValueError("invalid checkpoint instruction identity/history")
    referenced = {active}
    previous, previous_count = None, 0
    for index, entry in enumerate(history):
        if (not isinstance(entry, dict) or not all(isinstance(entry.get(key), str) and
                re.fullmatch(r"[a-f0-9]{64}", entry[key]) for key in ("from", "to")) or
                entry["from"] == entry["to"] or previous is not None and entry["from"] != previous):
            raise ValueError("checkpoint instruction transition history is inconsistent")
        expected_id = digest(canonical(['instruction-upgrade/v1', execution['invocation_id'],
                                        entry['from'], entry['to'], index]))
        count = entry.get('attempt_count')
        if (entry.get('transition_id') != expected_id or type(count) is not int or
                not previous_count <= count <= len(attempt_identities) or
                entry.get('refreshed_stages') != ['review', 'proof'] or
                not isinstance(entry.get('approval_source'), str) or not entry['approval_source'].strip() or
                not isinstance(entry.get('mandate_policy_sha256'), str) or
                not re.fullmatch(r'[a-f0-9]{64}', entry['mandate_policy_sha256'])):
            raise ValueError("checkpoint instruction transition provenance is invalid")
        referenced.update((entry["from"], entry["to"]))
        previous, previous_count = entry["to"], count
    if previous is not None and previous != active:
        raise ValueError("checkpoint instruction transition does not reach the active identity")
    expected, transition = (history[0]['from'] if history else active), 0
    for index, identities in enumerate(attempt_identities):
        while transition < len(history) and history[transition]['attempt_count'] <= index:
            expected = history[transition]['to']
            transition += 1
        for identity in identities:
            if not isinstance(identity, str) or identity != expected:
                raise ValueError("checkpoint stage instruction identity differs from its historical boundary")
            referenced.add(identity)
    if set(bundles) != referenced:
        raise ValueError("checkpoint instruction inputs are missing or unreferenced; preserve the exact snapshots before transfer")
    for entry in history:
        instructions.compatible(bundles[entry["from"]], bundles[entry["to"]])


def restore_checkpoint(root, data, upgrade_instructions=False, authorize_upgrade=False):
    """Validate the entire transfer before writing any local agreement or product input."""
    if authorize_upgrade and not upgrade_instructions:
        raise ValueError("--authorize-upgrade requires --upgrade-instructions")
    root = Path(root).resolve()
    value, contents = read_checkpoint(root, data)
    setup(root)
    if value["execution"]:
        import p2p_delivery
        return p2p_delivery.restore_checkpoint(root, value, contents, data,
                                              upgrade_instructions=upgrade_instructions,
                                              authorize_upgrade=authorize_upgrade)
    if upgrade_instructions or authorize_upgrade:
        raise ValueError("instruction upgrades require a delivery checkpoint; restore this planning handoff normally")
    if any(scope != "project" for scope, _, _ in contents):
        raise ValueError("runtime files require a controller checkpoint")
    targets = []
    for _, relative, content in contents:
        target = safe(root, relative)
        if target.exists() and (not target.is_file() or target.read_bytes() != content):
            raise ValueError("checkpoint conflicts with local file: " + relative)
        targets.append((target, content))
    target, _ = checkpoint_path(root, value["work_item"], value["destination"])
    if target.exists() and target.read_bytes() != data:
        raise ValueError("checkpoint conflicts with selected local checkpoint")
    for file, content in targets + [(target, data)]:
        file.parent.mkdir(parents=True, exist_ok=True)
        if not file.exists():
            atomic_write(file, content, ignored_root=root if file.is_relative_to(root / ".p2p") else None)
    resolve(root, value["work_item"])
    return {"status": "RESTORED", "work_item": value["work_item"], "checkpoint_sha256": digest(data),
            "next_action": "Continue the saved planning/decomposition handoff; approval is never inferred from restoration."}


def checkpoint_status(root, work, remote=None):
    target, destination = checkpoint_path(root, work)
    data = target.read_bytes()
    value, contents = read_checkpoint(root, data)
    checkpoint_current(root, value, contents)
    result = {"status": "LOCAL_ONLY", "path": str(target.relative_to(root)), "sha256": digest(data), "bytes": len(data)}
    if destination["kind"] != "git":
        raise ValueError("use checkpoint-github-status for the selected GitHub destination")
    relative = str(target.relative_to(root))
    committed = subprocess.run(["git", "-C", str(root), "show", "HEAD:" + relative], capture_output=True)
    if committed.returncode == 0 and committed.stdout == data:
        result["status"] = "COMMITTED"
    if remote:
        refs = git(root, "ls-remote", "--heads", remote).decode().splitlines()
        tips = [line.split("\t")[0] for line in refs]
        for tip in tips:
            if subprocess.run(["git", "-C", str(root), "cat-file", "-e", tip + "^{commit}"], capture_output=True).returncode:
                git(root, "fetch", "--no-tags", remote, tip)
        def reachable(commit):
            return any(subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", commit, tip],
                                      capture_output=True).returncode == 0 for tip in tips)
        if not all(reachable(commit) for commit in value["required_commits"]):
            raise ValueError("checkpoint candidate or binding commit is not available from the remote's branches")
        if any(subprocess.run(["git", "-C", str(root), "show", tip + ":" + relative], capture_output=True).stdout == data for tip in tips):
            result.update(status="PORTABLE", remote=remote)
        else:
            raise ValueError("current checkpoint bytes have not been published to this remote")
    return result


def checkpoint_current(root, value, contents):
    execution = value["execution"]
    if execution and (execution.get("source_recovery_commit") not in value["required_commits"] or
                      snapshot_key(snapshot(root, execution["source_recovery_commit"])) != execution["source_tree_key"]):
        raise ValueError("source admission has no recoverable Git commit; preserve and reconcile excluded local changes before transfer")
    for scope, relative, content in contents:
        if scope == "project":
            file = safe(root, relative)
            if file.is_file() and file.read_bytes() != content:
                raise ValueError("checkpoint is stale; local input changed: " + relative)
    local = safe(root, f'.p2p/work/{work_slug(value["work_item"])}/delivery.json')
    if local.is_file():
        current = json.loads(local.read_bytes())
        boundary = value["execution"]
        if boundary is None or any(current.get(key) != boundary.get(key) for key in
                                  ("invocation_id", "candidate", "contract", "limits", "routing", "reports", "blocker",
                                   "instruction_identity", "instruction_history")):
            raise ValueError("checkpoint is stale; the local controller needs a new completed boundary")
        if any(a["status"] not in ("complete", "retired") for a in current["attempts"]):
            raise ValueError("uncertain dispatch prevents portability; retain local execution state")
        import p2p_delivery
        if p2p_delivery.controller_running(p2p_delivery.Delivery(root, value["work_item"], current)) is not False:
            raise ValueError("stop the active controller before verifying a portable handoff")


def checkpoint_github_body(data):
    value = json.loads(data)
    return (f'<!-- p2p-checkpoint:{work_slug(value["work_item"])}:{digest(data)} -->\n'
            '```json\n' + data.decode().rstrip("\n") + '\n```\n')


def checkpoint_github_read(repository, issue, sha=None):
    result = subprocess.run(["gh", "api", "--paginate", "--jq", ".[]", f"repos/{repository}/issues/{issue}/comments"],
                            capture_output=True, text=True)
    if result.returncode:
        raise ValueError("checkpoint GitHub read failed: " + result.stderr.strip())
    found = []
    for line in result.stdout.splitlines():
        comment = json.loads(line)
        match = re.fullmatch(r"<!-- p2p-checkpoint:([a-z0-9-]+):([a-f0-9]{64}) -->\n```json\n(.*)\n```\n?", comment.get("body", ""), re.S)
        if not match and sha is not None and sha in comment.get("body", "") and '<!-- p2p-checkpoint:' in comment.get("body", ""):
            raise ValueError("malformed matching GitHub checkpoint")
        if not match or sha is not None and match[2] != sha:
            continue
        data = match[3].encode() + b"\n"
        if digest(data) != match[2] or work_slug(json.loads(data)["work_item"]) != match[1]:
            raise ValueError("GitHub checkpoint marker/hash mismatch")
        found.append((data, comment.get("html_url")))
    if not found:
        raise ValueError("missing exact GitHub checkpoint SHA-256")
    if len(found) != 1:
        raise ValueError("ambiguous GitHub checkpoint; reconcile duplicate records")
    return found[0]


def checkpoint_github_publish(root, work, authorized_sha256):
    target, destination = checkpoint_path(root, work)
    if destination["kind"] != "github":
        raise ValueError("work item selects Git, not a GitHub checkpoint")
    data = target.read_bytes()
    read_checkpoint(root, data)
    body = checkpoint_github_body(data)
    if authorized_sha256 != digest(body.encode()):
        raise ValueError("publication needs authority for the exact checkpoint comment body SHA-256")
    if len(body) > 60000:
        raise ValueError("checkpoint exceeds the 60000-character issue-comment budget; select Git or reduce redundant metadata")
    repository, issue = destination["repository"], destination["issue"]
    try:
        existing, url = checkpoint_github_read(repository, issue, digest(data))
    except ValueError as error:
        if "missing exact GitHub checkpoint" not in str(error):
            raise
        # A readback after any uncertain write is mandatory before a caller retries.
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as file:
            file.write(body)
            file.flush()
            result = subprocess.run(["gh", "issue", "comment", str(issue), "--repo", repository, "--body-file", file.name],
                                    capture_output=True, text=True)
        existing, url = checkpoint_github_read(repository, issue, digest(data))
    if existing != data:
        raise ValueError("checkpoint GitHub readback differs; retain local state")
    return {"status": "RECORDED", "url": url, "sha256": digest(data),
            "next_action": "Verify candidate and binding commits with checkpoint-github-status --remote before deleting local state."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("setup")
    for name in ("checkpoint", "checkpoint-status", "checkpoint-restore", "checkpoint-github-preview",
                 "checkpoint-github-publish", "checkpoint-github-status", "checkpoint-github-restore"):
        command = commands.add_parser(name)
        if name not in ("checkpoint-github-restore",):
            command.add_argument("work")
        if name == "checkpoint":
            command.add_argument("--github", help="select OWNER/REPO as the checkpoint destination")
            command.add_argument("--issue", type=int)
            command.add_argument("--candidate-commit")
        if name in ("checkpoint-status", "checkpoint-github-status"):
            command.add_argument("--remote", help="verify published checkpoint and Git objects against this remote")
        if name == "checkpoint-github-publish":
            command.add_argument("--authorize-comment-sha256", required=True)
        if name in ("checkpoint-restore", "checkpoint-github-restore"):
            command.add_argument("--upgrade-instructions", action="store_true",
                                 help="preview or apply the shared instruction upgrade after restoring pinned inputs")
            command.add_argument("--authorize-upgrade", action="store_true",
                                 help="authorize the compatible instruction transition under the current delivery mandate")
        if name == "checkpoint-github-restore":
            command.add_argument("--repository", required=True)
            command.add_argument("--issue", type=int, required=True)
            command.add_argument("--sha256", required=True)
    for name in ("execution-path", "execution-access", "publication-access"):
        command = commands.add_parser(name)
        command.add_argument("work")
        if name == "publication-access":
            command.add_argument("--workspace", help="retained isolated candidate workspace")
    entry_command = commands.add_parser("resolve-entry", help="read-only lookup for a single delivery request")
    entry_command.add_argument("source", help="quoted text, configured #issue, repository spec, or saved contract path")
    entry_command.add_argument("--issue-repository", help="configured GitHub OWNER/REPO for an issue number")
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
        if name == "create":
            command.add_argument("--github", help="select OWNER/REPO before the first checkpoint")
            command.add_argument("--issue", type=int)
    args = parser.parse_args(argv)
    try:
        root = Path(git(Path(args.repo), "rev-parse", "--show-toplevel").decode().strip()).resolve()
        if args.command in ("create", "checkpoint"):
            if bool(args.github) != (args.issue is not None):
                raise ValueError("select --github and --issue together")
            destination = {"kind": "github", "repository": args.github, "issue": args.issue} if args.github else None
        if args.command == "setup":
            result = setup(root)
        elif args.command == "checkpoint":
            state = safe(root, f".p2p/work/{work_slug(args.work)}/delivery.json")
            if state.is_file():
                import p2p_delivery
                result = p2p_delivery.export_checkpoint(root, args.work, destination=destination)
            else:
                result = checkpoint(root, args.work, destination, candidate_commit=args.candidate_commit)
        elif args.command == "checkpoint-restore":
            target, _ = checkpoint_path(root, args.work)
            result = restore_checkpoint(root, target.read_bytes(),
                                        upgrade_instructions=args.upgrade_instructions,
                                        authorize_upgrade=args.authorize_upgrade)
        elif args.command == "checkpoint-status":
            result = checkpoint_status(root, args.work, args.remote)
        elif args.command == "checkpoint-github-preview":
            target, destination = checkpoint_path(root, args.work)
            if destination["kind"] != "github":
                raise ValueError("select the GitHub checkpoint destination first")
            body = checkpoint_github_body(target.read_bytes())
            result = {"destination": destination, "body": body, "sha256": digest(body.encode())}
        elif args.command == "checkpoint-github-publish":
            result = checkpoint_github_publish(root, args.work, args.authorize_comment_sha256)
        elif args.command == "checkpoint-github-restore":
            data, url = checkpoint_github_read(args.repository, args.issue, args.sha256)
            value = json.loads(data)
            if value["destination"] != {"kind": "github", "repository": args.repository, "issue": args.issue}:
                raise ValueError("GitHub checkpoint destination differs from the selected issue")
            result = restore_checkpoint(root, data, upgrade_instructions=args.upgrade_instructions,
                                        authorize_upgrade=args.authorize_upgrade) | {"url": url}
        elif args.command == "checkpoint-github-status":
            target, destination = checkpoint_path(root, args.work)
            if destination["kind"] != "github":
                raise ValueError("work item does not select a GitHub checkpoint")
            data = target.read_bytes()
            value, contents = read_checkpoint(root, data)
            checkpoint_current(root, value, contents)
            published, url = checkpoint_github_read(destination["repository"], destination["issue"], digest(data))
            if published != data:
                raise ValueError("GitHub checkpoint differs from local bytes")
            if value["required_commits"]:
                if not args.remote:
                    raise ValueError("candidate/source commits need --remote verification")
                tips = [line.split("\t")[0] for line in git(root, "ls-remote", "--heads", args.remote).decode().splitlines()]
                for tip in tips:
                    if subprocess.run(["git", "-C", str(root), "cat-file", "-e", tip + "^{commit}"], capture_output=True).returncode:
                        git(root, "fetch", "--no-tags", args.remote, tip)
                if not all(any(subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", commit, tip], capture_output=True).returncode == 0
                               for tip in tips) for commit in value["required_commits"]):
                    raise ValueError("checkpoint Git objects are not published to this remote")
            result = {"status": "PORTABLE", "url": url, "sha256": digest(data), "bytes": len(data)}
        elif args.command == "execution-path":
            result = {"execution_directory": str(execution_directory(root, args.work))}
        elif args.command == "execution-access":
            result = prepare_execution(root, args.work)
        elif args.command == "publication-access":
            result = publication_access(root, args.work, args.workspace)
        elif args.command == "resolve-entry":
            result = entry_source(root, args.source, args.issue_repository)
        elif args.command == "reconcile":
            result = reconcile(root, args.work)
        elif args.command == "create":
            item, artifact = paths(root, args.work)
            checkpoint_path(root, args.work, destination)
            if artifact.exists() and any(artifact.iterdir()):
                raise ValueError("artifact directory already contains records")
            if not args.work.startswith(".p2p/"):
                trackable(root, [args.work])
            data = Path(args.source).read_bytes()
            item.parent.mkdir(parents=True, exist_ok=True)
            with item.open("xb") as output:
                output.write(data)
            result = resolve(root, args.work)
            result["checkpoint"] = checkpoint(root, args.work, destination)
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
