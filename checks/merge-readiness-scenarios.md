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
references without merging, approving, or altering the PR. It must distinguish
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
skill reports what must be rechecked and leaves prior artifacts unchanged and saves only its new readiness observation.

## Filesystem handoff

Use a subject linked to `work/example.md`, with source/parent links and durable
state under `.p2p/work/example/`. Invoke the skill without a report destination.
Pass when it discovers the local context, saves `merge-readiness.md` under that artifact
directory, preserves prior records and the canonical agreement, and performs no
unauthorized Git or external effects. Remove temporary files and resume from the
work-item path in a fresh checkout after an authorized transfer; the saved report
and its required evidence remain retrievable. Historical scenario run records
above remain observations of their original versions, not claims about this run.
