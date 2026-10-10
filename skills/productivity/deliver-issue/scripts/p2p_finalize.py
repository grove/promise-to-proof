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


def receipt_body(record):
    """Stable exact comment serialization of the one canonical #50 record."""
    identifier = record.get("landing", {}).get("receipt_id")
    need(isinstance(identifier, str) and
         re.fullmatch(r"sha256:[a-f0-9]{64}", identifier),
         "record lacks a stable, verified #50 receipt identity")
    return ("<!-- p2p-final:" + identifier + " -->\n" +
            "\x60\x60\x60json\n" + fs.canonical(record).decode("utf-8") +
            "\n\x60\x60\x60\n")


def comments(repository, issue, *, runner=subprocess.run):
    value = run(["gh", "api", "--paginate", "--jq", ".[]",
                 f"repos/{repository}/issues/{issue}/comments"], runner=runner)
    return [json.loads(line) for line in value.stdout.splitlines() if line.strip()]


def matching_receipt(rows, record):
    body = receipt_body(record)
    identifier = record["landing"]["receipt_id"]
    matches = []
    for item in rows:
        actual = item.get("body")
        if not isinstance(actual, str) or "<!-- p2p-final:" not in actual:
            continue
        captured = RECEIPT.fullmatch(actual)
        need(captured is not None, "malformed existing completion receipt")
        previous = json.loads(captured[2])
        need(isinstance(previous, dict) and
             previous.get("landing", {}).get("receipt_id") == "sha256:" + captured[1] and
             actual == receipt_body(previous),
             "existing receipt marker and record content disagree")
        same_event = previous["landing"]["receipt_id"] == identifier
        if same_event:
            need(actual == body, "completed receipt identity has conflicting bytes")
            matches.append(item)
        elif previous.get("invocation_id") == record.get("invocation_id"):
            raise ValueError("this delivery invocation already has a conflicting receipt")
    need(len(matches) <= 1, "multiple matching completed delivery receipts")
    return matches[0] if matches else None


def receipt_target(root, record, pr_url=None, receipt_issue=None, receipt_ref=None):
    """Select the original issue, matching PR, or an exact existing Git ref."""
    source = fs.safe(root, record["work_item"])
    text = source.read_text(encoding="utf-8") if source.is_file() else ""
    issue_urls = set(re.findall(
        r"^Source attribution:\s*(https://github\.com/[^\s;]+/issues/\d+)",
        text, re.M))
    need(len(issue_urls) <= 1, "ambiguous source issue provenance")
    if receipt_issue:
        need(ISSUE.fullmatch(receipt_issue) is not None and
             receipt_issue in issue_urls,
             "explicit receipt issue must be the agreed original source issue")
        issue_url = receipt_issue
    else:
        issue_url = next(iter(issue_urls)) if issue_urls else None
    if issue_url:
        match = ISSUE.fullmatch(issue_url)
        need(match is not None and match[1] == record["landing"]["repository"],
             "source issue belongs to a different delivery repository")
        return {"kind": "comment", "repository": match[1], "number": int(match[2]),
                "destination": issue_url}
    if pr_url:
        match = PR.fullmatch(pr_url)
        need(match and match[1] == record["landing"]["repository"],
             "receipt PR belongs to a different delivery repository")
        return {"kind": "comment", "repository": match[1], "number": int(match[2]),
                "destination": pr_url}
    need(isinstance(receipt_ref, str) and
         re.fullmatch(r"refs/heads/p2p/receipts/[a-z0-9-]+", receipt_ref),
         "issue-less/no-PR delivery needs an exact authorized p2p/receipts Git ref")
    return {"kind": "git", "ref": receipt_ref}


def comment_receipt(record, target, mandate, *, runner=subprocess.run):
    """Read before writing; on lost reply read again without a second write."""
    body = receipt_body(record)
    need(len(body.encode()) <= 60000, "completed receipt exceeds GitHub comment limit")
    repository, number = target["repository"], target["number"]
    first = matching_receipt(comments(repository, number, runner=runner), record)
    if first is None:
        autonomy.authorize(mandate, "issue-comment", repository,
                           target["destination"])
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as file:
            file.write(body)
            file.flush()
            result = run(["gh", "issue", "comment", str(number), "--repo", repository,
                          "--body-file", file.name], check=False, runner=runner)
        # A failed response may still have applied the effect. Never blindly retry.
    confirmed = matching_receipt(comments(repository, number, runner=runner), record)
    if confirmed is None:
        return {"status": "PARTIAL",
                "reason": "GitHub receipt write was not confirmed; reread before retrying"}
    url = confirmed.get("html_url")
    need(isinstance(url, str) and url.startswith("https://github.com/" + repository + "/"),
         "confirmed receipt lacks its durable GitHub URL")
    return {"status": "RECORDED", "url": url,
            "body_sha256": fs.digest(body.encode())}


def git_receipt(root, remote, target, record, checkpoint, mandate,
                *, runner=subprocess.run):
    """Write one deterministic receipt commit with a separate temporary Git index.

    This changes Git objects/remotes under exact grants, not the operator's
    checked-out branch, files or staging index. Never force-update a receipt ref.
    """
    ref = target["ref"]
    path = f"p2p-state/{fs.work_slug(record['work_item'])}-delivery.json"
    value = fs.canonical(record) + b"\n"
    branches = remote_branches(root, remote, runner=runner)
    tip = branches.get(ref)
    need(tip, "receipt branch is not published; establish its checkpoint under branch-create authority")
    checkpoint_path = f"p2p-state/{fs.work_slug(record['work_item'])}.json"
    saved = run(["git", "-C", str(root), "show", tip + ":" + checkpoint_path],
                check=False, runner=runner)
    need(saved.returncode == 0 and saved.stdout.encode() == checkpoint,
         "receipt branch does not preserve the exact #82 checkpoint")
    prior = run(["git", "-C", str(root), "show", tip + ":" + path],
                check=False, runner=runner)
    if prior.returncode == 0:
        need(prior.stdout.encode() == value,
             "remote receipt branch contains a conflicting completed record")
        return {"status": "RECORDED", "url": remote + ":" + ref + ":" + path,
                "remote_commit": tip}
    autonomy.authorize(mandate, "commit", record["landing"]["repository"], ref)
    autonomy.authorize(mandate, "push", record["landing"]["repository"], ref)
    timestamp = datetime.datetime.fromisoformat(
        record["landing"]["confirmed_at"].replace("Z", "+00:00")).timestamp()
    date = str(int(timestamp)) + " +0000"
    with tempfile.TemporaryDirectory() as folder:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(folder) / "index"),
                   GIT_AUTHOR_NAME="P2P Delivery", GIT_AUTHOR_EMAIL="p2p@localhost",
                   GIT_COMMITTER_NAME="P2P Delivery", GIT_COMMITTER_EMAIL="p2p@localhost",
                   GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
        run(["git", "-C", str(root), "read-tree", tip], env=env, runner=runner)
        blob = run(["git", "-C", str(root), "hash-object", "-w", "--stdin"],
                   input=value.decode(), env=env, runner=runner).stdout.strip()
        run(["git", "-C", str(root), "update-index", "--add", "--cacheinfo",
             f"100644,{blob},{path}"], env=env, runner=runner)
        tree = run(["git", "-C", str(root), "write-tree"], env=env,
                   runner=runner).stdout.strip()
        commit = run(["git", "-C", str(root), "commit-tree", tree, "-p", tip,
                      "-m", "P2P complete " + record["landing"]["receipt_id"]],
                     env=env, runner=runner).stdout.strip()
    run(["git", "-C", str(root), "push", remote, commit + ":" + ref],
        check=False, runner=runner)
    # Confirm after any response (including a lost/nonzero one).
    current = remote_branches(root, remote, runner=runner).get(ref)
    if current != commit:
        return {"status": "PARTIAL",
                "reason": "remote receipt push was not confirmed; never blindly retry"}
    actual = run(["git", "-C", str(root), "show", commit + ":" + path],
                 runner=runner).stdout.encode()
    need(actual == value, "remote receipt object bytes differ from the approved record")
    return {"status": "RECORDED", "url": remote + ":" + ref + ":" + path,
            "remote_commit": commit}
