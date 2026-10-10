#!/usr/bin/env python3
"""Complete an authorized delivery with one validated Delivery Record v1.

Read-only previews, exact effect grants, live GitHub/remote readback and
idempotent receipts; no second acceptance or delivery-state protocol.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import p2p_autonomy as autonomy
import p2p_delivery_record as records
import p2p_filesystem as fs

PR = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/pull/([1-9][0-9]*)\Z")
ISSUE = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/issues/([1-9][0-9]*)\Z")
COMMIT = re.compile(r"(?:[a-f0-9]{40}|[a-f0-9]{64})\Z")
RECEIPT = re.compile(r"<!-- p2p-final:sha256:([a-f0-9]{64}) -->\n" +
                     r"\x60\x60\x60json\n(.*?)\n\x60\x60\x60\n?\Z", re.S)
READINESS = "<!-- p2p-finalization-readiness:v1 -->"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def run(argv, *, input=None, env=None, check=True, runner=subprocess.run):
    result = runner(argv, input=input, capture_output=True, text=True, env=env, timeout=30)
    if check and result.returncode:
        raise ValueError("command failed: " + " ".join(argv[:4]) + "; " +
                         (result.stderr.strip() or "result unavailable"))
    return result


def gh(path, *, runner=subprocess.run):
    return json.loads(run(["gh", "api", path], runner=runner).stdout)


def read_pr(repository, number, *, runner=subprocess.run):
    pr = gh(f"repos/{repository}/pulls/{number}", runner=runner)
    url = f"https://github.com/{repository}/pull/{number}"
    need(isinstance(pr, dict) and pr.get("number") == number and
         pr.get("html_url") == url and
         pr.get("base", {}).get("repo", {}).get("full_name") == repository,
         "GitHub PR readback does not match exact repository and number")
    need(isinstance(pr.get("head", {}).get("sha"), str) and
         COMMIT.fullmatch(pr["head"]["sha"]) and
         isinstance(pr.get("base", {}).get("sha"), str) and
         COMMIT.fullmatch(pr["base"]["sha"]) and
         isinstance(pr.get("base", {}).get("ref"), str),
         "GitHub PR does not have exact head/base identities")
    return pr


def remote_branches(root, remote, *, runner=subprocess.run):
    stdout = run(["git", "-C", str(root), "ls-remote", "--heads", remote],
                 runner=runner).stdout
    branches = {}
    for line in stdout.splitlines():
        match = re.fullmatch(r"([a-f0-9]{40}|[a-f0-9]{64})\t(refs/heads/\S+)", line)
        need(match, "invalid Git remote branch identity")
        branches[match[2]] = match[1]
    return branches


def remote_contains(root, ancestor, tips):
    return any(subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", ancestor, tip],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        for tip in tips if COMMIT.fullmatch(tip))


def portable(root, checkpoint, remote, *, runner=subprocess.run):
    """Verify the actual #82 published source/candidate Git objects and bytes."""
    value, _ = fs.read_checkpoint(root, checkpoint)
    branches = remote_branches(root, remote, runner=runner)
    tips = set(branches.values())
    need(tips, "remote has no verifiable published Git branches")
    for sha in value["required_commits"]:
        need(remote_contains(root, sha, tips),
             "checkpoint Git commit is not recoverable from the remote's branches: " + sha)
    destination = value["destination"]
    if destination["kind"] == "git":
        path = f"p2p-state/{fs.work_slug(value['work_item'])}.json"
        need(any(subprocess.run(
            ["git", "-C", str(root), "show", tip + ":" + path],
            capture_output=True).stdout == checkpoint for tip in tips),
            "exact #82 checkpoint bytes are not published to this remote")
        location = remote + ":" + path
    else:
        data, location = fs.checkpoint_github_read(
            destination["repository"], destination["issue"], fs.digest(checkpoint))
        need(data == checkpoint, "GitHub checkpoint readback differs from retained bytes")
    return {"checkpoint_sha256": fs.digest(checkpoint), "url": location,
            "branches": branches}


def read_readiness(path):
    need(path is not None, "open PR needs a saved independently assessed merge-readiness record")
    saved = Path(path).read_text(encoding="utf-8")
    blocks = re.findall(re.escape(READINESS) +
                        r"\n\x60\x60\x60json\n(.*?)\n\x60\x60\x60", saved, re.S)
    need(len(blocks) == 1, "one unambiguous machine-readable READY section is required")
    data = json.loads(blocks[0])
    fields = {"schema", "status", "pr", "head", "base", "target",
              "integration_commit", "integration_check", "required_checks",
              "policy_sha256", "synchronized", "observed_at", "merge_method"}
    need(isinstance(data, dict) and set(data) == fields and
         data["schema"] == "promise-to-proof/merge-readiness/v1" and
         data["status"] == "READY" and data["synchronized"] is True,
         "readiness was not approved and synchronized for this exact PR")
    need(isinstance(data["required_checks"], list) and
         all(isinstance(v, str) and v.strip() for v in data["required_checks"]) and
         isinstance(data["integration_check"], str) and data["integration_check"].strip() and
         isinstance(data["policy_sha256"], str) and
         re.fullmatch(r"[a-f0-9]{64}", data["policy_sha256"]) and
         isinstance(data["integration_commit"], str) and
         COMMIT.fullmatch(data["integration_commit"]),
         "readiness is missing valid integration/branch-policy facts")
    return data


def check_runs(repository, sha, *, runner=subprocess.run):
    response = gh(f"repos/{repository}/commits/{sha}/check-runs?per_page=100",
                  runner=runner)
    rows = response.get("check_runs")
    need(isinstance(rows, list) and response.get("total_count") == len(rows),
         "current required checks cannot be fully read back")
    groups = {}
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("name"), str):
            groups.setdefault(row["name"], []).append(row)
    return groups


def _passed(name, groups):
    rows = groups.get(name, [])
    return len(rows) == 1 and rows[0].get("status") == "completed" and rows[0].get("conclusion") == "success"


def check_ready(root, record, remote, repository, pr, method, readiness,
                *, runner=subprocess.run):
    head, base, branch = pr["head"]["sha"], pr["base"]["sha"], pr["base"]["ref"]
    need(readiness["pr"] == pr["html_url"] and readiness["head"] == head and
         readiness["base"] == base and readiness["target"] == branch and
         readiness["merge_method"] == method,
         "readiness is stale for this PR's head, base, or merge method")
    need(pr.get("state") == "open" and pr.get("merged") is False and
         pr.get("draft") is False and pr.get("mergeable") is True and
         pr.get("mergeable_state") == "clean",
         "PR is draft, conflicting, blocked or has unknown mergeability")
    need(record["routing"]["destination"] == branch,
         "PR target conflicts with the approved routing")
    need(remote_branches(root, remote, runner=runner).get("refs/heads/" + branch) == base,
         "remote target has advanced since readiness inspection")
    repository_info = gh(f"repos/{repository}", runner=runner)
    field = {"merge": "allow_merge_commit", "squash": "allow_squash_merge",
             "rebase": "allow_rebase_merge"}[method]
    need(repository_info.get(field) is True, "merge method disabled by repository settings")
    rules = gh(f"repos/{repository}/rules/branches/{branch}", runner=runner)
    need(isinstance(rules, list) and
         fs.digest(fs.canonical(rules)) == readiness["policy_sha256"],
         "branch rules changed or cannot be read back")
    need(not any(isinstance(r, dict) and r.get("type") == "merge_queue" for r in rules),
         "merge queue is required; direct merge is unsupported")
    checks = [c for rule in rules if isinstance(rule, dict) and
              rule.get("type") == "required_status_checks"
              for c in rule.get("parameters", {}).get("required_status_checks", [])]
    names = sorted({c["context"] for c in checks})
    need(names == sorted(readiness["required_checks"]),
         "required checks differ from the saved readiness assessment")
    integration = readiness["integration_commit"]
    need(fs.full_commit(root, integration) == integration,
         "exact current head/target integration commit is unavailable locally")
    parents = fs.git(root, "rev-list", "--parents", "-n", "1", integration).decode().split()
    need(parents[1:] == [base, head],
         "integration check is not for the exact current head and target")
    runs = check_runs(repository, integration, runner=runner)
    need(_passed(readiness["integration_check"], runs) and
         all(_passed(name, runs) for name in names),
         "required current-target integration/check-run result is not successful")
    if any(isinstance(rule, dict) and rule.get("type") == "pull_request" for rule in rules):
        reviews = gh(f"repos/{repository}/pulls/{pr['number']}/reviews", runner=runner)
        need(isinstance(reviews, list) and
             any(r.get("state") == "APPROVED" and r.get("commit_id") == head for r in reviews) and
             not any(r.get("state") == "CHANGES_REQUESTED" for r in reviews),
             "current GitHub PR approvals are insufficient or conflicting")
    return {"head": head, "base": base, "integration": integration,
            "target": branch}
