#!/usr/bin/env python3
"""Guard optional learning preservation using the existing retrospective and #82 checkpoint.

No retrospective is launched here. Unselected deliveries use the original fast
path; selected lessons must have precise, remotely recoverable support before
temporary execution evidence can be discarded.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

import p2p_filesystem as fs

HEX = re.compile(r"[a-f0-9]{64}\Z")
EVIDENCE = re.compile(
    r"^- (E[1-9][0-9]*): \[([^\]\n]+)\]\(([^)\n]+)\) SHA-256 \x60([a-f0-9]{64})\x60"
    r" - ([^\n]+)$")
FORBIDDEN = ("runtime/", "attempts/", "scratch", "transcript", "secret",
             ".log", ".jsonl", "stderr", "stdout", ".p2p/tmp")
LABELS = ("Learning preservation", "Delivery identity", "Contract SHA-256",
          "Candidate identity", "Evidence status")


def single_line(content, label):
    matches = re.findall(r"^" + re.escape(label) + r": ([^\r\n]+)$", content, re.M)
    if len(matches) != 1 or not matches[0].strip():
        raise ValueError("retrospective needs exactly one " + label)
    return matches[0].strip()


def selected_report(root, work):
    """No report means zero new work; old reports with suggestions need classification."""
    owner = fs.safe(root, f".p2p/work/{fs.work_slug(work)}")
    path = owner / "retrospective.md"
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError("retrospective is not a safe regular file")
    data = path.read_bytes()
    if len(data) > 64000:
        raise ValueError("retrospective is too large to retain as a compact lesson")
    text = data.decode("utf-8")
    decisions = re.findall(r"^Learning preservation: (selected|none)$", text, re.M)
    if len(decisions) != 1:
        raise ValueError("retrospective needs an explicit selected/none learning preservation decision")
    if decisions[0] == "none":
        if re.search(r"^-\s*E[1-9][0-9]*:", text, re.M):
            raise ValueError("no-learning report unexpectedly names retained evidence")
        return None
    return text


def delivery_identity(root, work):
    owner = fs.safe(root, f".p2p/work/{fs.work_slug(work)}")
    active, completed = owner / "delivery.json", owner / "artifacts/delivery.json"
    if active.is_file():
        value = json.loads(active.read_bytes())
    elif completed.is_file():
        value = json.loads(completed.read_bytes())
    else:
        raise ValueError("selected lesson has no saved delivery identity")
    if value.get("work_item") != work or not value.get("invocation_id"):
        raise ValueError("selected lesson belongs to an unrecognized delivery")
    contract = value.get("contract") or {}
    candidate = value.get("candidate")
    if isinstance(candidate, dict):
        candidate = candidate.get("key")
    candidate = candidate or value.get("candidate_key") or "none"
    return {
        "invocation": value["invocation_id"],
        "contract": contract.get("sha256"),
        "candidate": candidate,
        "status": value.get("status"),
        "attempts": value.get("attempts", []),
    }


def inspect(root, work):
    text = selected_report(root, work)
    if text is None:
        return {"status": "NONE", "reason": "no worthwhile learning selected; no preservation work"}
    identity = delivery_identity(root, work)
    for label, expected in (
        ("Delivery identity", identity["invocation"]),
        ("Contract SHA-256", identity["contract"]),
        ("Candidate identity", identity["candidate"]),
    ):
        if single_line(text, label) != expected:
            raise ValueError("retrospective " + label + " does not match the exact delivery")
    if not HEX.fullmatch(identity["contract"] or ""):
        raise ValueError("saved delivery lacks a canonical contract digest")
    evidence_status = single_line(text, "Evidence status")
    if evidence_status not in ("PROVEN", "UNPROVEN"):
        raise ValueError("retrospective must distinguish PROVEN from UNPROVEN observations")
    if evidence_status == "PROVEN" and identity["status"] != "REVIEWED_AND_PROVEN":
        raise ValueError("unfinished work cannot claim proven retrospective evidence")
    if evidence_status == "UNPROVEN":
        if identity["status"] not in ("BLOCKED",):
            raise ValueError("unproven terminal handoff requires a blocked saved delivery")
        if not single_line(text, "Terminal decision source") or not re.search(
                r"^Terminal disposition: (abandoned|terminally blocked)$", text, re.M):
            raise ValueError("terminal unproven handoff requires explicit abandonment/block decision")
    if not re.search(r"^## Suggested learnings\s*$", text, re.M):
        raise ValueError("selected retrospective has no suggested learnings")
    if "pending" not in text.lower() and "accepted" not in text.lower():
        raise ValueError("selected learning needs the existing human disposition")
    found = {}
    for line in text.splitlines():
        if not line.startswith("- E"):
            continue
        match = EVIDENCE.fullmatch(line)
        if not match:
            raise ValueError("learning evidence reference is not a retrievable file and SHA-256")
        number, label, path, expected, reason = match.groups()
        if number in found:
            raise ValueError("duplicate learning evidence ID " + number)
        if any(item in path.lower() for item in FORBIDDEN) or "://" in path or "#" in path:
            raise ValueError("raw or private execution source is not a safe learning reference: " + path)
        if (not (path.startswith(f".p2p/work/{fs.work_slug(work)}/") or
                 path.startswith(("specs/", "docs/", "work/", "checks/"))) or
                path.endswith((".jsonl", ".log"))):
            raise ValueError("lesson evidence must be a durable, scoped checkpoint file")
        file = fs.safe(root, path)
        if not file.is_file() or file.is_symlink() or fs.digest(file.read_bytes()) != expected:
            raise ValueError("learning evidence bytes are missing or changed: " + path)
        found[number] = {"path": path, "sha256": expected, "description": label, "observation": reason}
    if not found:
        raise ValueError("selected learning needs at least one concrete, hash-checked observation")
    # Do not persist sources which the normal completed cleanup deliberately removes.
    if identity["status"] == "REVIEWED_AND_PROVEN":
        for row in found.values():
            path = row["path"]
            if path.startswith(f".p2p/work/{fs.work_slug(work)}/"):
                relative = path.split(f".p2p/work/{fs.work_slug(work)}/", 1)[1]
                if not (relative.startswith("artifacts/") or relative == "contract.md"
                        or relative == "retrospective.md"):
                    raise ValueError("learning cites a local report discarded by completion cleanup: " + path)
    return {"status": "SELECTED", "identity": identity, "evidence": found,
            "report": f".p2p/work/{fs.work_slug(work)}/retrospective.md"}


def _required_remote_commits(root, checkpoint, remote):
    # Use the same destination and commit-reachability requirements as #82.
    tips = [line.split("\t")[0] for line in fs.git(root, "ls-remote", "--heads", remote).decode().splitlines()]
    for tip in tips:
        exists = subprocess.run(["git", "-C", str(root), "cat-file", "-e", tip + "^{commit}"],
                                capture_output=True)
        if exists.returncode:
            fs.git(root, "fetch", "--no-tags", remote, tip)
    for commit in checkpoint["required_commits"]:
        if not any(subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", commit, tip],
                                  capture_output=True).returncode == 0 for tip in tips):
            raise ValueError("learning's required checkpoint commit is not published")
    return tips


def verify(root, work, remote=None, require_portable=False):
    root = Path(root).resolve()
    selection = inspect(root, work)
    if selection["status"] == "NONE":
        return selection
    checkpoint_path, destination = fs.checkpoint_path(root, work)
    data = checkpoint_path.read_bytes()
    checkpoint, contents = fs.read_checkpoint(root, data)
    index = {(scope, path): blob for scope, path, blob in contents}
    if index.get(("project", selection["report"])) != fs.safe(root, selection["report"]).read_bytes():
        raise ValueError("retrospective is not preserved in the selected checkpoint")
    for row in selection["evidence"].values():
        blob = index.get(("project", row["path"]))
        if blob is None or fs.digest(blob) != row["sha256"]:
            raise ValueError("learning evidence absent from the recoverable checkpoint: " + row["path"])
    if not require_portable:
        return {"status": "LOCAL_ONLY", "checkpoint_sha256": fs.digest(data),
                "evidence": sorted(selection["evidence"]), "identity": selection["identity"]}
    if not remote:
        raise ValueError("selected lesson needs --remote for shared recovery readback before cleanup")
    if destination["kind"] == "git":
        result = fs.checkpoint_status(root, work, remote)
        if result["status"] != "PORTABLE":
            raise ValueError("selected learning checkpoint is not remotely portable")
    else:
        fs.checkpoint_current(root, checkpoint, contents)
        received, _ = fs.checkpoint_github_read(
            destination["repository"], destination["issue"], fs.digest(data))
        if received != data:
            raise ValueError("selected learning GitHub checkpoint readback differs")
        _required_remote_commits(root, checkpoint, remote)
    return {"status": "PORTABLE", "checkpoint_sha256": fs.digest(data),
            "evidence": sorted(selection["evidence"]), "identity": selection["identity"]}


def cleanup_guard(root, work, remote=None):
    """Called only at the irreversible deletion boundary of successful cleanup."""
    if selected_report(root, work) is None:
        return {"status": "NONE"}
    if remote is None:
        remotes = fs.git(root, "remote").decode().splitlines()
        if "origin" in remotes:
            remote = "origin"
    return verify(root, work, remote=remote, require_portable=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--contract", required=True)
    parser.add_argument("--remote")
    parser.add_argument("--portable", action="store_true")
    args = parser.parse_args(argv)
    try:
        root = Path(args.repo).resolve()
        outcome = verify(root, args.contract, remote=args.remote,
                         require_portable=args.portable)
        print(json.dumps(outcome, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print("BLOCKED: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
