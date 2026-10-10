#!/usr/bin/env python3
"""Publish the *saved* P2P review on its exact PR; never run a reviewer.

The preview is read-only. The publish command requires exact effect authority,
rechecks the saved inputs and live PR, and reconciles existing reviews before
and after the only permitted external write.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import p2p_filesystem as fs

SCHEMA = "promise-to-proof/pr-review-preview/v1"
URL = re.compile(r"https://github\.com/([\w.-]+)/([\w.-]+)/pull/([1-9][0-9]*)\Z")
HEX = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}\Z")
MARKER = "p2p:published-review:v1"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode() + b"\n"


def checked_pr_url(url):
    match = URL.fullmatch(url)
    if not match:
        raise ValueError("PR must be an exact github.com/OWNER/REPO/pull/NUMBER URL")
    return f"{match[1]}/{match[2]}", int(match[3])


def gh(args, payload=None):
    cmd = ["gh", "api", *args]
    result = subprocess.run(cmd, input=payload, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "GitHub request failed")
    return json.loads(result.stdout)


def pr_read(repository, number):
    return gh(["--method", "GET", f"repos/{repository}/pulls/{number}"])


def reviews_read(repository, number):
    pages = gh(["--paginate", "--slurp", "--method", "GET",
                f"repos/{repository}/pulls/{number}/reviews?per_page=100"])
    if not isinstance(pages, list) or not all(isinstance(page, list) for page in pages):
        raise ValueError("could not read the complete GitHub review history")
    return [review for page in pages for review in page]


def review_write(repository, number, event, body):
    return gh(["--method", "POST", "--input", "-",
               f"repos/{repository}/pulls/{number}/reviews"],
              json.dumps({"event": event, "body": body}, ensure_ascii=False))


def review_status(raw):
    heading = raw.decode("utf-8").splitlines()[0] if raw else ""
    match = re.fullmatch(r"# (REVIEWED|CHANGES NEEDED|BLOCKED): .+", heading)
    if not match:
        raise ValueError("saved review has no recognized current verdict")
    if match[1] == "BLOCKED":
        raise ValueError("a BLOCKED review cannot be published as a current verdict")
    return match[1]


def load_saved(root, work):
    """Read currently bound controller records; a stale markdown file is not enough."""
    slug = fs.work_slug(work)
    owner = fs.safe(root, f".p2p/work/{slug}")
    active = owner / "delivery.json"
    terminal = owner / "artifacts/delivery.json"
    if active.is_file() and terminal.is_file():
        raise ValueError("conflicting active and completed delivery records")
    if not active.is_file() and not terminal.is_file():
        raise ValueError("missing saved delivery with current review scope")
    completed = terminal.is_file()
    state = json.loads((terminal if completed else active).read_bytes())
    if state.get("work_item") != work:
        raise ValueError("saved delivery belongs to a different agreement")
    agreement = fs.safe(root, work).read_bytes()
    contract_sha = sha(agreement)
    if state.get("contract", {}).get("sha256") != contract_sha:
        raise ValueError("saved review's canonical contract has changed")
    if fs.bindings(root, work) != state.get("binding_inputs"):
        raise ValueError("source or parent binding changed since the saved review")
    if completed:
        if state.get("schema") != "promise-to-proof/delivery-record/v1" or state.get("status") != "REVIEWED_AND_PROVEN":
            raise ValueError("completed delivery record is not full review and proof")
        review_file = owner / "artifacts/review.md"
        raw = review_file.read_bytes()
        if sha(raw) != state.get("review_sha256"):
            raise ValueError("saved completed review bytes changed")
        scope = state.get("review_scope")
        candidate = state.get("candidate_key")
        findings = []
        checks = []
        proof = "PROVEN"
    else:
        record = state.get("reports", {}).get("review")
        if not isinstance(record, dict) or not isinstance(record.get("review_scope"), dict):
            raise ValueError("no current independently saved review scope")
        runtime = fs.execution_directory(root, work) / "runtime"
        raw_report = fs.safe(runtime, record["path"]).read_bytes()
        if sha(raw_report) != record.get("sha256"):
            raise ValueError("original saved review receipt changed")
        report = json.loads(raw_report)
        review_file = owner / "review.md"
        raw = review_file.read_bytes()
        attempt_md = fs.safe(runtime, f"attempts/{record['attempt_id']}/report.md").read_bytes()
        if raw != attempt_md:
            raise ValueError("visible saved review differs from the original review receipt")
        if report.get("status") != review_status(raw):
            raise ValueError("saved review verdict disagrees with its exact stage record")
        scope = record["review_scope"]
        candidate = state.get("candidate", {}).get("key")
        findings = report.get("findings", [])
        checks = report.get("checks", [])
        proof_record = state.get("reports", {}).get("proof")
        proof = "Not established for this candidate"
        if proof_record and proof_record.get("inputs") == record.get("inputs"):
            proof_bytes = fs.safe(runtime, proof_record["path"]).read_bytes()
            if sha(proof_bytes) == proof_record.get("sha256"):
                if json.loads(proof_bytes).get("status") == "PROVEN":
                    proof = "PROVEN"
    if not isinstance(scope, dict) or scope.get("contract_sha256") != contract_sha:
        raise ValueError("saved review scope is missing or bound to another contract")
    if candidate != scope.get("candidate_key"):
        raise ValueError("saved candidate and review scope do not match")
    status = review_status(raw)
    if completed and status != "REVIEWED":
        raise ValueError("completed delivery has a non-clean review")
    if status == "CHANGES NEEDED" and not findings:
        raise ValueError("material findings missing from the original review")
    return {"status": status, "body": raw.decode("utf-8"), "review_sha256": sha(raw),
            "contract_sha256": contract_sha, "candidate": candidate,
            "scope": scope, "proof": proof, "findings": findings, "checks": checks}


def plain(value):
    # Present saved observations as data, not as Markdown controls/instructions.
    return re.sub(r"\s+", " ", str(value)).strip().replace("<", "&lt;").replace(">", "&gt;")


def render_review(saved, repository, number, head):
    status = saved["status"]
    event = "COMMENT" if status == "REVIEWED" else "REQUEST_CHANGES"
    action = "pr-review-comment" if status == "REVIEWED" else "pr-review-request-changes"
    marker = (f"<!-- {MARKER} repo={repository} pr={number} head={head} "
              f"candidate={saved['candidate']} contract={saved['contract_sha256']} "
              f"review={saved['review_sha256']} event={event} -->")
    if status == "REVIEWED":
        introduction = ("**Saved implementation review: no material changes requested.** "
                        "The independent reviewer examined this specific candidate "
                        "against the agreed requirements; this is not a GitHub approval.")
    else:
        introduction = ("**Saved implementation review: material changes required.** "
                        "These are findings from the existing independent review, "
                        "not a fresh review of this pull request.")
    lines = [marker, "", "## Implementation review", "", introduction, "",
             "### Findings", ""]
    if status == "REVIEWED":
        lines.append("No material change-required findings in the saved review.")
    else:
        for finding in saved["findings"]:
            if not isinstance(finding, dict) or not all(finding.get(x) for x in
                    ("id", "consequence", "correction", "location", "evidence")):
                raise ValueError("saved material finding is incomplete")
            lines.extend([f"- **{plain(finding['id'])}** — {plain(finding['location'])}. "
                          f"{plain(finding['consequence'])} "
                          f"Evidence: {plain(finding['evidence'])}. "
                          f"Suggested correction: {plain(finding['correction'])}."])
    lines.extend(["", "### Checks and limits", ""])
    if saved["checks"]:
        for item in saved["checks"]:
            if not isinstance(item, dict) or not all(item.get(x) for x in ("command", "result", "observation")):
                raise ValueError("incomplete saved review check")
            lines.append(f"- {plain(item['command'])}: **{plain(item['result'])}** — "
                         f"{plain(item['observation'])}")
    else:
        lines.append("See the saved review for the exact inspected scope and limitations.")
    lines.extend(["", "### What this does not establish", "",
                  f"- Acceptance proof for this exact candidate: **{plain(saved['proof'])}**.",
                  "- GitHub approval: **not granted by this review**.",
                  "- Merge readiness: **NOT ASSESSED**. This PR is not merged by this action.",
                  "- Findings and checks cover only the unchanged saved candidate and review base.",
                  "", "<details><summary>Exact saved review and identities</summary>", "",
                  f"Candidate: \`{saved['candidate']}\`  ",
                  f"Contract SHA-256: \`{saved['contract_sha256']}\`  ",
                  f"Review SHA-256: \`{saved['review_sha256']}\`  ",
                  f"PR head: \`{head}\`", ""])
    report = saved["body"]
    fence = "\`" * max(3, max((len(x) for x in re.findall(r"\`+", report)), default=0) + 1)
    lines += [fence + "markdown", report.rstrip("\n"), fence, "", "</details>", ""]
    body = "\n".join(lines)
    if len(body.encode()) > 60000:
        raise ValueError("saved review exceeds the safe GitHub review size; no partial publication")
    return body, event, action, marker


def build_preview(root, work, pr_url, head_repo):
    repository, number = checked_pr_url(pr_url)
    pr = pr_read(repository, number)
    if (pr.get("state") != "open" or pr.get("number") != number or
            pr.get("head", {}).get("repo", {}).get("full_name") != repository or
            pr.get("base", {}).get("repo", {}).get("full_name") != repository):
        raise ValueError("PR is not an open same-repository pull request")
    head = pr.get("head", {}).get("sha")
    if not isinstance(head, str) or not HEX.fullmatch(head):
        raise ValueError("PR has no exact current head SHA")
    saved = load_saved(root, work)
    expected = (f"<!-- grove:publish-pr repo={repository} candidate={saved['candidate']} "
                f"contract=sha256:{saved['contract_sha256']} -->")
    if expected not in (pr.get("body") or ""):
        raise ValueError("PR publication marker does not match saved review and agreement")
    scope = fs.review_scope_status(root, work, head_repo, head)
    if scope.get("status") != "COVERED":
        raise ValueError("PR head differs from saved reviewed product: " +
                         scope.get("reason", scope.get("status", "unknown")))
    body, event, action, marker = render_review(saved, repository, number, head)
    return {"schema": SCHEMA, "repository": repository, "pull_number": number, "pr_url": pr_url,
            "head_sha": head, "base_branch": pr["base"]["ref"],
            "pr_body_sha256": sha((pr.get("body") or "").encode()),
            "candidate": saved["candidate"], "contract_sha256": saved["contract_sha256"],
            "review_sha256": saved["review_sha256"], "verdict": saved["status"],
            "proof_status": saved["proof"], "event": event, "effect": action,
            "marker": marker, "body": body}


def existing_review(preview):
    reviews = reviews_read(preview["repository"], preview["pull_number"])
    matching = [r for r in reviews if preview["marker"] in (r.get("body") or "")]
    if len(matching) > 1:
        raise ValueError("duplicate published reviews with the same exact identity")
    if matching:
        review = matching[0]
        state = "COMMENTED" if preview["event"] == "COMMENT" else "CHANGES_REQUESTED"
        if review.get("body") != preview["body"] or review.get("state") != state:
            raise ValueError("previous matching review was edited or has a conflicting effect; preserve it")
        if not review.get("html_url"):
            raise ValueError("published review has no recoverable URL")
        return review["html_url"]
    # A matching review SHA on a changed head is historical, not current.
    return None


def authorize(preview, saved_sha, authorization=None, approved_sha=None, approval_source=None):
    if authorization:
        record = json.loads(Path(authorization).read_bytes())
        effect = record.get("effect") or {}
        if (record.get("status") != "AUTHORIZED" or
                record.get("preview_sha256") != saved_sha or
                effect != {"action": preview["effect"], "repository": preview["repository"],
                           "destination": preview["pr_url"]} or
                record.get("candidate") != preview["candidate"]):
            raise ValueError("standing effect grant does not cover the exact review preview")
    elif approved_sha and approval_source and approval_source.strip():
        if approved_sha != saved_sha:
            raise ValueError("human approval does not match the exact saved review preview")
    else:
        raise ValueError("publishing needs a matching controller effect grant or explicit exact-preview human approval")


def publish(preview, posted=None):
    """One write at most. Reconcile a possibly lost response by remote readback."""
    found = existing_review(preview)
    if found:
        return {"status": "PUBLISHED", "url": found, "reused": True}
    write_error = None
    try:
        review_write(preview["repository"], preview["pull_number"], preview["event"], preview["body"])
    except (OSError, RuntimeError, ValueError) as error:
        write_error = str(error)
    # A write response alone is never publication proof.
    try:
        found = existing_review(preview)
    except (OSError, RuntimeError, ValueError):
        return {"status": "PARTIAL", "reason": "review write may have happened; GitHub readback unavailable"}
    if found:
        return {"status": "PUBLISHED", "url": found, "reused": False}
    return {"status": "PARTIAL", "reason": (
        "GitHub write result uncertain; read back the review before retrying"
        if write_error else "GitHub did not confirm the review after write")}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--contract", required=True)
    parser.add_argument("--pr", required=True)
    parser.add_argument("--head-repo", required=True,
                        help="local isolated checkout with the exact current PR head Git object")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preview-out")
    group.add_argument("--publish-preview")
    group.add_argument("--status-preview")
    parser.add_argument("--authorization", help="saved output of controller authorize-effect")
    parser.add_argument("--approved-sha256", help="explicit human approval of this complete preview")
    parser.add_argument("--approval-source", help="retrievable human approval reference")
    args = parser.parse_args(argv)
    try:
        root = Path(args.repo).resolve()
        fresh = build_preview(root, args.contract, args.pr, Path(args.head_repo).resolve())
        if args.preview_out:
            destination = Path(args.preview_out).resolve()
            if destination.exists() and destination.read_bytes() != canonical(fresh):
                raise ValueError("preview destination contains different bytes; preserve its history")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(canonical(fresh))
            if destination.read_bytes() != canonical(fresh):
                raise ValueError("saved preview readback differs")
            result = {"status": "DRAFT", "path": str(destination),
                      "preview_sha256": sha(canonical(fresh)),
                      "effect": fresh["effect"], "destination": fresh["pr_url"],
                      "head_sha": fresh["head_sha"], "verdict": fresh["verdict"],
                      "review_sha256": fresh["review_sha256"],
                      "body": fresh["body"]}
        else:
            path = Path(args.publish_preview or args.status_preview)
            saved_bytes = path.read_bytes()
            if not saved_bytes.endswith(b"\n") or canonical(json.loads(saved_bytes)) != saved_bytes:
                raise ValueError("review preview must be exact canonical JSON")
            if saved_bytes != canonical(fresh):
                raise ValueError("review, PR, contract, or candidate changed since preview")
            if args.status_preview:
                found = existing_review(fresh)
                result = ({"status": "PUBLISHED", "url": found, "reused": True}
                          if found else {"status": "NOT_PUBLISHED"})
            else:
                authorize(fresh, sha(saved_bytes), args.authorization,
                          args.approved_sha256, args.approval_source)
                # Read the current PR/head again immediately before the effect.
                if canonical(build_preview(root, args.contract, args.pr,
                                           Path(args.head_repo).resolve())) != saved_bytes:
                    raise ValueError("PR or reviewed candidate changed immediately before publication")
                result = publish(fresh)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] not in ("PARTIAL",) else 1
    except (ValueError, OSError, KeyError, TypeError, UnicodeError, RuntimeError,
            json.JSONDecodeError) as error:
        print("BLOCKED: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
