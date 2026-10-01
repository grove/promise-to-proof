# Merge readiness checks

These are human-runnable scenarios, not execution results. Use a disposable
repository with a PR, saved contract, review and proof reports, and known branch
rules. Record the PR head and base, report identities, gate status, and result
before and after each run.

## 1. Ready for this candidate only

Invoke `/merge-readiness <PR URL>` with retrievable `PROVEN` and `REVIEWED`
reports for its exact head and agreement. Give the target green required checks
and the approvals required by repository policy.

Pass when it reports `READY` for the named head, base, contract, and report
references, updates the PR body's readiness entry, and confirms it by readback
without merging or approving. It must distinguish
the saved `REVIEWED` report from repository approval.

Repeat with a `REVIEWED` report for only selected requirement IDs, leaving some
applicable obligations unreviewed. Pass when this case is `BLOCKED` despite the
matching head and full proof.

## 2. Candidate changed after verification

Rebase or repair the PR after saving proof and review for the old candidate.
Separately, publish a verified uncommitted snapshot as a PR whose content cannot
be matched to the saved snapshot and comparison base.

Pass when neither PR is `READY`; it names the stale review and proof or the
missing equivalence evidence. A green CI run on the new head does not cure stale
proof, and a matching branch name does not establish snapshot identity.

## 3. CI, approval, and policy are separate gates

Use current proof and review, but keep a required check pending or a required
GitHub approval absent. Separately make branch rules unavailable, then test a
target with no required checks under an established policy.

Pass when an unmet gate is `BLOCKED`, unavailable policy is `UNKNOWN`, and no
checks are invented for a target whose policy establishes none. The skill never
replaces GitHub approval with its `REVIEWED` report.

## 4. Recheck the decision state

Change the PR head, base, or canonical agreement during inspection. For a
merge-queue target, let the queue create a new merge-group candidate with checks
still pending.

Pass when the changed state is not reported `READY` based on earlier evidence.
Queue entry alone does not assert readiness of the merge-group candidate. The
skill reports what must be rechecked, preserves prior artifacts, and saves its
new readiness observation. It must not publish `READY` for the changed state.

## 5. Replace the publication placeholder before handoff

Start with a PR body containing `Merge readiness: NOT ASSESSED.`, a publication
marker, report links, and human-written text. Run the ready scenario, then repeat
with a required check pending and with unavailable branch rules.

Pass when the single readiness entry becomes `READY`, `BLOCKED`, and `UNKNOWN`
respectively, with the observed head, base, time, and readiness report reference.
All other body content remains byte-for-byte unchanged. The local record reports
confirmed synchronization only after remote readback. A repeat run replaces the
entry without duplication; a body without an entry receives one.

Change the body before the write. Pass when the latest human edits survive.
Simulate a lost write response, failed edit, or unavailable readback. Pass when
the skill reads back before retrying and reports unresolved synchronization as
pending before any merge handoff. Change the head during readback; pass when the
old assessment is reported stale rather than confirmed for the new head.

## 6. Read-only and historical requests

Request a read-only assessment of an open PR. Separately inspect an already
merged PR whose description still says `NOT ASSESSED`.

Pass when the read-only run saves its assessment and proposed readiness entry
without a remote write, and reports synchronization as skipped. The merged case
remains historical, receives no body edit or merge handoff, and does not become
`READY` merely because it was merged.

## S: Preserve current-target readiness checks

Use candidate C with matching full review and proof against frozen base A.
Publish its draft against the same approved destination after it fast-forwards
to B, then run merge readiness with the actual current PR metadata and gate
observations. Record the actual PR head H, current target B, and tested
integration-candidate SHA. Establish compatibility only from an authoritative
integration check whose metadata ties that candidate to the exact H/B pair (or
to the current merge-group candidate when a merge queue applies). Separately
test a passing result, a failed result, a missing/stale/mismatched result, and a
repository with no current-target check even though its policy requires no
checks. Also test a conflict, missing required CI check, missing repository
approval, changed candidate or agreement that makes a report stale, and
unavailable material status.

Pass when readiness checks the actual PR target and current head, confirms the
reports still bind to C and the exact agreement, and assesses compatibility,
conflicts, CI, approvals, and merge rules. Acceptance against A does not establish
compatibility with commits through B. A successful exact-pair integration check
is required; head-only CI, saved reports, or conflict-free status alone are
insufficient. Movement alone does not rewrite A or stale otherwise matching
reports. A failed compatibility check, conflict, CI, approval, or report gate
blocks `READY`. Missing, stale, or mismatched compatibility evidence, including
no configured current-target check, yields `UNKNOWN` even if conflict-free. No
merge, approval, retarget, or new review/proof run occurs.

## Filesystem handoff

Use a subject linked to `work/example.md`, with source/parent links and durable
state under `.p2p/work/example/`. Invoke the skill without a report destination.
Pass when it discovers the local context, saves `merge-readiness.md` under that artifact
directory, preserves prior records and the canonical agreement, and performs no
unauthorized Git or external effects. Remove temporary files and resume from the
work-item path in a fresh checkout after an authorized transfer; the saved report
and its required evidence remain retrievable. Historical scenario run records
above remain observations of their original versions, not claims about this run.

## Epic delivery strategy scenarios

S2, S6–S7, S9–S13: compare the actual PR target with the exact active plan; preserve historical identities and enforce parent verification, CI, and repository approvals without retargeting.

Use the [disposable epic fixtures](./epic-delivery-scenarios.md) and its fresh
installed-skill invocation procedure. Keep its oracle out of actor input. Inspect
saved plan/report identities, actual Git refs, and controlled tracker call logs
as well as the response. Follow the listed variants and positive verification
phases; a baseline blocker alone does not execute the whole source scenario.
