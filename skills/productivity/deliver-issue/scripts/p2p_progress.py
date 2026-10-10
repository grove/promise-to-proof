#!/usr/bin/env python3
"""Deterministic, read-only explanations of existing Promise to Proof evidence.

This module holds no workflow state and makes no completion decisions. Callers
must first validate the authoritative controller/delivery records. An optional
GitHub observation is checked against that same candidate before it can change
the presentation of publication or merge status.
"""
import json
from pathlib import Path
import re
import subprocess

import p2p_filesystem as fs


PR_URL = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/pull/([1-9][0-9]*)\Z")
SHA = re.compile(r"[a-f0-9]{40}|[a-f0-9]{64}\Z")
MARKER = re.compile(
    r"<!-- grove:publish-pr repo=([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+) "
    r"candidate=(snapshot:sha256:[a-f0-9]{64}|git:[a-f0-9]{40,64}) "
    r"contract=sha256:([a-f0-9]{64}) -->"
)


def _unverified(reason, url=None):
    return {"status": "UNVERIFIED", "verified": False, "url": url,
            "reason": reason}


def _target(route):
    if not isinstance(route, dict):
        return None
    ref = route.get("target_ref")
    if isinstance(ref, str):
        if ref.startswith("refs/heads/"):
            return ref[len("refs/heads/"):]
        if ref.startswith("refs/remotes/"):
            remaining = ref[len("refs/remotes/"):]
            return remaining.partition("/")[2] or None
    # Historical destination records can lack their ref.
    return None


def inspect_github_pr(root, status, url, *, runner=subprocess.run):
    """Read a PR exactly once and verify it matches the accepted candidate.

    No network request is made for an unproven candidate. Remote results, PR
    descriptions, mutable branch names and saved publication prose are never
    accepted as a replacement for exact local candidate/tree identity.
    """
    if not isinstance(url, str) or not PR_URL.fullmatch(url):
        return _unverified("A full GitHub pull-request URL is required.", url)
    if status.get("status") != "REVIEWED_AND_PROVEN":
        return _unverified("Local full review and proof have not been established.", url)
    candidate = status.get("candidate") or {}
    candidate_key = candidate.get("key")
    contract = status.get("contract") or {}
    digest = contract.get("sha256")
    destination = _target(status.get("routing"))
    if (not isinstance(candidate_key, str) or not isinstance(digest, str) or
            not re.fullmatch(r"[a-f0-9]{64}", digest) or destination is None):
        return _unverified("The exact candidate, contract or approved destination is unavailable.", url)
    match_url = PR_URL.fullmatch(url)
    repository = match_url[1] + "/" + match_url[2]
    args = ["gh", "pr", "view", url, "--json",
            "url,state,mergedAt,mergeCommit,headRefOid,baseRefName,body,isDraft"]
    try:
        response = runner(args, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return _unverified("GitHub could not be read; the PR's current state is unknown.", url)
    if response.returncode:
        return _unverified("GitHub could not confirm this PR; check access and readback.", url)
    try:
        record = json.loads(response.stdout)
    except (ValueError, TypeError):
        return _unverified("GitHub returned an unreadable PR result.", url)
    if not isinstance(record, dict) or record.get("url") != url:
        return _unverified("GitHub readback did not identify the requested PR.", url)
    body = record.get("body")
    if not isinstance(body, str) or body.count("<!-- grove:publish-pr ") != 1:
        return _unverified("The PR has no unique saved P2P publication identity.", url)
    markers = MARKER.findall(body)
    if len(markers) != 1 or markers[0] != (repository, candidate_key, digest):
        return _unverified("The PR publication identity differs from the reviewed candidate or agreement.", url)
    if record.get("baseRefName") != destination:
        return _unverified("The PR target does not match the agreed delivery destination.", url)
    head = record.get("headRefOid")
    if not isinstance(head, str) or not SHA.fullmatch(head):
        return _unverified("The PR head is not an exact Git commit identity.", url)
    if candidate_key.startswith("git:"):
        match = candidate_key == "git:" + head
    else:
        match = False
        bases = []
        workspace = status.get("candidate_workspace")
        if workspace:
            bases.append(Path(workspace))
        bases.append(Path(root))
        excludes = tuple(status.get("agreement_paths") or (status.get("work_item"),))
        for base in bases:
            try:
                tree = fs.snapshot(base, head, exclude=excludes)
            except (OSError, ValueError, subprocess.SubprocessError):
                continue
            match = fs.snapshot_key(tree) == candidate_key
            break
    if not match:
        return _unverified("The PR head's product tree could not be verified against the reviewed candidate; fetch the exact commit or reconcile its changed bytes.", url)
    state = record.get("state")
    if state not in ("OPEN", "CLOSED", "MERGED"):
        return _unverified("GitHub returned an unknown PR state.", url)
    merge_commit = record.get("mergeCommit")
    if state == "MERGED":
        oid = merge_commit.get("oid") if isinstance(merge_commit, dict) else None
        if not record.get("mergedAt") or not isinstance(oid, str) or not SHA.fullmatch(oid):
            return _unverified("GitHub merge confirmation lacks its actual merge commit.", url)
    elif record.get("mergedAt"):
        return _unverified("GitHub returned contradictory open/closed and merged observations.", url)
    return {"status": state, "verified": True, "url": url,
            "head_sha": head, "target": destination, "is_draft": record.get("isDraft") is True,
            "merge_commit": merge_commit["oid"] if state == "MERGED" else None,
            "merged_at": record.get("mergedAt") if state == "MERGED" else None,
            "evidence": "Current GitHub PR readback and exact reviewed product-tree comparison"}


def _short_reason(message):
    text = " ".join(str(message or "").split())
    if len(text) > 220:
        text = text[:217].rsplit(" ", 1)[0] + "..."
    return text


def _kind_of_blocker(blocker):
    message = (blocker or "").lower()
    if ("no delivery invocation exists" in message or
            "missing delivery invocation" in message or
            "no local delivery invocation" in message):
        return "not-admitted"
    if ("app-server" in message or "sandbox" in message or "codex" in message) and (
            "permission" in message or "not permitted" in message or "initialize" in message):
        return "host"
    if "uncertain dispatch" in message or "unreconciled dispatch" in message or "missing controller host completion" in message:
        return "uncertain-worker"
    if any(key in message for key in ("approval required", "awaiting approval", "approval missing", "needs approval")):
        return "approval"
    if any(key in message for key in ("authority missing", "outside the standing mandate", "effect grant", "permission denied")):
        return "authority"
    if any(key in message for key in ("stale", "source changed", "candidate changed", "agreement changed", "identity")):
        return "identity"
    return "other"


def _milestones(status):
    finished = {a.get("stage") for a in (status.get("attempts") or [])
                if isinstance(a, dict) and a.get("status") == "complete"}
    reports = status.get("reports") or {}
    done = status.get("status") == "REVIEWED_AND_PROVEN"
    recorded = []
    if "planning" in finished:
        recorded.append("Acceptance planning produced a recorded result.")
    if "planning-audit" in finished:
        recorded.append("An independent planning audit ran; that is not approval.")
    if done or status.get("implementation_complete") is True:
        recorded.append("The implementation stage completed.")
    if done:
        recorded += ["Independent implementation review passed for the exact candidate.",
                     "Independent proof established the full accepted requirements."]
    else:
        if "review" in reports:
            recorded.append("Review observations are saved; a current passing verdict is not established here.")
        if "proof" in reports:
            recorded.append("Proof observations are saved; a current passing verdict is not established here.")
    return recorded


def _final_receipt_ok(finalization, publication, candidate_key):
    """Only a future verified #50/#47 receipt may establish full finalization."""
    if not isinstance(finalization, dict):
        return False
    verified = (finalization.get("status") == "FINALIZED" and
                finalization.get("receipt_verified") is True and
                finalization.get("candidate_mapping_verified") is True and
                finalization.get("destination_verified") is True and
                finalization.get("candidate_key") == candidate_key and
                isinstance(finalization.get("delivered_commit"), str) and
                SHA.fullmatch(finalization["delivered_commit"]))
    if not verified:
        return False
    # A verified direct/assembled parent can be finalized without a PR.
    # When one is present, its actual merge commit must still agree.
    return publication is None or (
        publication.get("verified") is True and publication.get("status") == "MERGED" and
        finalization["delivered_commit"] == publication.get("merge_commit"))


def explain(status, *, publication=None, finalization=None):
    """Make a readable view from facts validated by the caller, without writes.

    No milestone, approval, publication, merge, or finalization can be established
    from an estimated percentage, log modification time, agent prose, or an
    unverified PR marker. The raw status remains available alongside this view.
    """
    if not isinstance(status, dict):
        raise ValueError("status must be an existing validated delivery result")
    state = status.get("status")
    if not isinstance(state, str):
        raise ValueError("delivery status is missing")
    last = status.get("progress") or {}
    milestones = _milestones(status)
    accepted = state == "REVIEWED_AND_PROVEN"
    checkpoint_restored = status.get("checkpoint_restored_from") is not None
    fresh_preflight = status.get("fresh_host_preflight_complete") is True
    work = status.get("work_item") or "this work item"
    candidate = status.get("candidate") or {}
    candidate_key = candidate.get("key")
    location = ("retained isolated candidate workspace" if status.get("candidate_workspace") else
                "saved delivery records; a recoverable candidate workspace is not confirmed")
    what, why, next_action = "", "", ""
    phase, action_needed = "", False
    not_established = []
    pub = publication if isinstance(publication, dict) else None
    verified_pub = bool(pub and pub.get("verified") is True and pub.get("status") in ("OPEN", "CLOSED", "MERGED"))
    active = last.get("controller_running")
    continuation = status.get("continuation") or {}

    if state == "AWAITING_APPROVAL":
        phase, action_needed = "AWAITING_APPROVAL", True
        what = "Acceptance planning has a proposal, but exact approval has not been established."
        why = "An audit or a recommendation to approve does not authorize implementation."
        next_action = "Review and approve the exact agreement, or resolve the named product decision."
        location = "no confirmed implementation candidate"
        not_established = ["User approval", "Implementation", "Independent review", "Proof"]
    elif checkpoint_restored and not fresh_preflight and not accepted and not status.get("blocker"):
        phase = "RESTORED_NEEDS_PREFLIGHT"
        what = "Saved delivery work was restored from a portable checkpoint."
        why = "Historical reports and worker receipts were imported, but the receiving host's isolation and task prerequisites have not been rechecked. No current worker is proven to be running."
        next_action = "Run the existing supported resume after making the receiving host available; it must establish a fresh preflight before implementation continues."
        not_established = ["Receiving-host preflight", "New live worker"]
        action_needed = bool(status.get("blocker"))
    elif state == "REVIEWED_AND_PROVEN":
        if _final_receipt_ok(finalization, pub, candidate_key):
            phase = "FULLY_FINALIZED"
            what = "The exact delivered code and its durable final receipt have been independently reconciled."
            why = ("Local review/proof, the merged PR, delivered-code mapping and receipt all match."
                   if verified_pub and pub["status"] == "MERGED" else
                   "Local review/proof, the directly delivered code and durable receipt all match; no PR was required.")
            next_action = "No further delivery action is required for this outcome."
            location = "verified delivered destination branch"
        elif verified_pub and pub["status"] == "MERGED":
            phase = "MERGED_RECEIPT_PENDING"
            what = "GitHub confirms that the matching pull request was merged with target " + pub["target"] + "."
            why = "The accepted local candidate and published PR head are verified. The actual delivered-code mapping, current destination tip and durable final receipt are not yet verified."
            next_action = "Inspect the actual merged commit and retain finalization as pending. #50/#47 must supply a supported validated receipt before P2P can claim delivery fully finalized."
            location = "merged pull request " + pub["url"] + " (current destination branch contents not independently verified)"
            not_established = ["Delivered-code mapping", "Durable final receipt"]
        elif verified_pub and pub["status"] == "OPEN":
            phase = "PR_PUBLISHED_NOT_MERGED"
            what = "Independent review and proof passed, and GitHub confirms the matching pull request is still open."
            why = "The reviewed code is published in a " + ("draft" if pub["is_draft"] else "ready-for-review") + " PR, not merged into the destination."
            next_action = "Check current-target compatibility, CI and approvals with merge-readiness; merge only with separate authority."
            location = "published pull request " + pub["url"] + " (operator checkout unchanged by P2P)"
            not_established = ["Merge", "Delivered-code final receipt"]
        elif verified_pub and pub["status"] == "CLOSED":
            phase = "PR_CLOSED_NOT_MERGED"
            what = "The reviewed and proven candidate had a matching PR, but GitHub says it was closed without merging."
            why = "Closure is not delivery to the destination branch."
            next_action = "Reconcile the closed PR and obtain authority for any new publication."
            location = "retained local candidate; historical closed PR " + pub["url"]
            not_established = ["Merge", "Finalization"]
        elif pub and pub.get("status") == "UNVERIFIED":
            phase = "PUBLICATION_UNCONFIRMED"
            what = "The exact local candidate passed independent review and proof."
            why = "Its requested PR could not be verified: " + _short_reason(pub.get("reason"))
            next_action = "Read back the PR and verify its head against the retained exact candidate before claiming publication or merge."
            not_established = ["Current PR state", "Merge", "Finalization"]
        else:
            phase = "LOCAL_REVIEWED_PROVEN"
            what = "The exact local candidate passed independent review and proof for the agreed requirements."
            why = "This proves the isolated candidate against its saved base; it does not commit, publish, merge, deploy, or update the operator's checkout."
            next_action = "No further action is required for a local-only delivery. Publication needs a separately authorized request."
            not_established = ["Published PR", "Merge", "Deployment"]
    elif state == "HANDOFF" and continuation.get("delegated") is True:
        phase = "AUTOMATIC_HANDOFF"
        what = "P2P preserved its work and paused at an authorized " + str(continuation.get("action") or "planning") + " handoff."
        why = "The previous implementation and evidence are retained; the next step belongs to the existing outer workflow."
        next_action = "The outer delivery continues the saved handoff and resumes at the supported boundary."
        not_established = ["Full local review and proof"]
    elif state in ("HANDOFF", "BLOCKED"):
        reason = _short_reason(status.get("blocker"))
        kind = _kind_of_blocker(reason)
        attempted = sum(1 for a in (status.get("attempts") or []) if a.get("stage") == "implementation")
        if status.get("invocation_exists") is False:
            phase, action_needed = "NOT_ADMITTED", True
            what = "Delivery has not started an admitted controller invocation."
            why = ("The recorded problem is: " + reason + ". " if reason else "") + (
                "Planning and implementation may still be pending; no worker, independent review or proof "
                "has been established, and there is no controller invocation to resume.")
            next_action = ("Resolve the named host or agreement blocker, then continue the original "
                           "/deliver-issue request through admission. Do not use controller resume "
                           "until an invocation actually exists.")
            location = "source or planning records only; no admitted implementation candidate"
        elif kind == "not-admitted":
            phase, action_needed = "NOT_ADMITTED", True
            what = "A delivery invocation has not yet been admitted for this work item."
            why = "The saved request or planning agreement alone does not mean implementation started, and there are no controller stages to resume."
            next_action = "Continue the existing /deliver-issue request from its saved source and complete any necessary agreement, approval and admission checks."
            location = "source/planning records only; no admitted implementation candidate"
        elif kind == "host":
            phase, action_needed = "BLOCKED_HOST", True
            what = "P2P is blocked by the execution host before it can safely continue."
            why = "The host reported " + (reason or "an unavailable worker capability") + ". A planning-audit result is not approval, and no implementation or live proof can be inferred from it."
            next_action = "Resolve the host restriction or obtain a supported execution path, then reconcile the retained invocation. Simply rerunning the same failed host command is not evidence of recovery."
        elif kind == "uncertain-worker":
            phase, action_needed = "BLOCKED_UNCERTAIN_WORKER", True
            what = "P2P cannot establish whether a reserved worker finished."
            why = "Its completion evidence is missing or unreconciled; starting another worker could duplicate effects."
            next_action = "Inspect and reconcile the saved host completion receipt before any new dispatch."
        elif kind == "approval":
            phase, action_needed = "AWAITING_APPROVAL", True
            what = "P2P retained an agreement or planning result but is awaiting an approval decision."
            why = "A saved proposal, independent audit or ready-for-approval recommendation is not the actual approval."
            next_action = "Confirm or revise the exact proposal under the existing approval rules, then resume the saved delivery."
        elif kind == "authority":
            phase, action_needed = "BLOCKED_AUTHORITY", True
            what = "P2P stopped because the next action is not authorized."
            why = reason or "The current mandate does not cover the requested decision or effect."
            next_action = "Provide the exact missing grant or reduce the requested effect; preserve the same candidate and proof."
        else:
            phase, action_needed = "BLOCKED", True
            what = "P2P is blocked with its existing work and observations retained."
            why = ("The recorded blocker is: " + reason) if reason else "A required decision, input or check is not established."
            next_action = "Resolve the named blocker using the saved supported handoff, then resume this invocation rather than starting over."
        if kind == "host" and not attempted:
            location = "planning/host records; no confirmed implementation candidate"
            if any(a.get("stage") == "planning-audit" and a.get("status") == "complete"
                   for a in (status.get("attempts") or []) if isinstance(a, dict)):
                what = "Planning and an independent audit finished, but execution was blocked before implementation."
                why = ("The audit does not approve the agreement. The worker could not initialize: " +
                       (reason or "host capability unavailable") +
                       ". Implementation, live review and proof never started.")
            if status.get("resume_count", 0) > 0:
                why += " A saved reconciliation or resume was attempted; it has not established host recovery."
        not_established = ["Full local review and proof", "Publication", "Merge"]
    elif state == "RUNNING" and active is True:
        phase = "IN_PROGRESS"
        stage = last.get("stage") or "delivery"
        what = "P2P is working on " + str(stage).replace("-", " ") + "."
        why = "Only the completed saved milestones establish progress; recent host-log activity is not proof of useful work."
        next_action = "The controller continues within the current authorized run. No action is required unless it reports a material blocker."
        not_established = ["Full local review and proof"]
    elif state == "RUNNING" and active is False:
        phase = "INTERRUPTED_RESUMABLE"
        what = "No running controller is confirmed for this unfinished delivery."
        why = "The saved contract, candidate and completed stage observations remain available; completion has not been established."
        next_action = "Use the existing resume path to reconcile the retained worker and continue at the incomplete stage."
        not_established = ["Full local review and proof"]
    elif state == "RUNNING":
        phase = "CONTROLLER_UNCERTAIN"
        what = "P2P could not establish whether the controller is running."
        why = "Unknown lock or process state is not evidence that the worker has finished."
        next_action = "Check the saved controller lock and worker receipts before resuming or dispatching another worker."
        action_needed = True
        not_established = ["Current worker state", "Full local review and proof"]
    elif state == "RESTORED":
        phase = "RESTORED_NEEDS_PREFLIGHT"
        what = "Existing planning or delivery records were restored from a checkpoint."
        why = "Those are retained facts, not evidence that the new host has passed preflight or that a worker is active."
        next_action = "Inspect the saved approval and resume only after the receiving host passes its required checks."
        location = "restored local records; live candidate/workspace not established"
        not_established = ["Receiving-host preflight", "New live worker"]
    else:
        phase = "NOT_ESTABLISHED"
        what = "A complete delivery state has not been established for " + work + "."
        why = "Saved inputs or a completed controller result are missing or insufficient."
        next_action = "Inspect the existing work-item records and resolve the missing agreement or invocation before continuing."
        action_needed = True
        not_established = ["Implementation", "Review", "Proof", "Publication"]
    if checkpoint_restored and not fresh_preflight and phase != "RESTORED_NEEDS_PREFLIGHT":
        why += " Restored evidence does not replace a fresh preflight on this host."
        if "Receiving-host preflight" not in not_established:
            not_established.append("Receiving-host preflight")
    if not accepted and status.get("parent_has_children"):
        why += " Child completion does not establish acceptance for an assembled parent."
        if "Assembled-parent review and proof" not in not_established:
            not_established.append("Assembled-parent review and proof")
    stage_work = status.get("work_selection")
    if isinstance(stage_work, dict) and isinstance(stage_work.get("stages"), dict):
        labels = {"REUSED": "retained and current", "STALE": "needs refreshed evidence",
                  "MISSING": "not yet established"}
        statements = [name.replace("-", " ") + ": " + labels.get(stage_work["stages"].get(name),
                      "not established")
                      for name in ("implementation", "review", "proof")]
        next_stage = stage_work.get("next")
        if statements and isinstance(next_stage, str):
            why += " Saved work: " + "; ".join(statements) + ". Next existing work: " + next_stage + "."
    chain = status.get('promise_continuity')
    if chain:
        why += (' This unit contributes ' + chain['contribution'] + ' to the original promise ' +
                chain['origin'] + '; it does not complete the original promise. ' +
                'Final combined acceptance belongs to ' + str(chain['final_acceptance_owner']) + '.')
        if phase in ('LOCAL_REVIEWED_PROVEN', 'FULLY_FINALIZED', 'PR_PUBLISHED_NOT_MERGED',
                     'MERGED_RECEIPT_PENDING'):
            next_action = chain['next_action']
        if 'Original promise completion' not in not_established:
            not_established.append('Original promise completion')
    message = " ".join((what, why, "Next: " + next_action))
    return {
        "phase": phase, "message": message, "what_happened": what,
        "why_it_matters": why, "next_action": next_action,
        "requires_user_action": action_needed,
        "where_is_the_code": location, "confirmed": milestones,
        "not_yet_established": not_established,
        "activity": {"last_log_activity_at": last.get("last_activity_at"),
                     "meaning": "Log activity is not a verified milestone."},
    }
