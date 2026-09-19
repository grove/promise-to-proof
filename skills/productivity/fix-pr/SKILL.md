---
name: fix-pr
description: Diagnose and repair failed GitHub Actions workflows for pull requests without weakening required checks, then verify the repaired commit.
disable-model-invocation: true
---

`/fix-pr` restores a pull request's intended workflow outcome. It identifies the
earliest causal failure, classifies its cause, applies the smallest durable
repair, and verifies the repaired commit against every required check.

## Invocation

Accept one repository target:

- `/fix-pr #123`
- `/fix-pr https://github.com/acme/project/pull/123`
- `/fix-pr <workflow-run-url>`

Infer the relevant workflow from a pull request or workflow run whenever the
target makes that possible.

## Guardrails

Before editing, inspect the branch and worktree. Continue only when the
current branch and commit identify the target PR head or workflow commit, and
the worktree has no unrelated changes. Stop with `NOT FIXED` when the target
cannot be established, credentials or permissions are unavailable, or the
branch state makes the repair ambiguous.

Commit only the scoped repair, push only the target PR head branch, and never
force-push.

Bind diagnosis and verification to the exact target commit SHA. If the PR
changes during the repair, stop and re-establish the target rather than
silently chasing the newer commit.

For fork or otherwise untrusted PRs, do not expose secrets, approve privileged
workflow execution, broaden permissions, or weaken isolation. Stop with
`NOT FIXED` when the required verification depends on an unavailable safe
execution path.

Preserve the verification boundary that exposed the failure:

- Keep every required job, test, assertion, lint/type check, coverage
  threshold, CI matrix entry, and failure condition. Replace an incorrect or
  obsolete check only under the evidence rule in `Forbidden repairs`.
- For a workflow-only repair, require the same quality checks to run with the
  same failure semantics.
- Add or strengthen a focused regression test for a product or test defect
  when the repository has a suitable seam. Use an independent behavioral
  assertion, not a copy of the implementation's calculation.
- Keep fixes scoped to the failure. A rerun is evidence, not a repair.

## Workflow

### 1. Establish the intended operation

Determine what the failed workflow was meant to guarantee, such as validating
the PR branch before merge or running required checks for a specific commit.
Define success from that guarantee.

Read the linked ticket and any supplied acceptance matrix when they define the
behavior under repair. Preserve requirement IDs, promised results, and relevant
boundaries. If that contract is unavailable or ambiguous, continue only with
repairs whose correctness does not depend on guessing the missing requirement.
Report the gap; a CI failure does not authorize changing the ticket's promises.

### 2. Diagnose before editing

Inspect the workflow run, failed jobs and steps, logs, workflow YAML, relevant
changes, and the target PR's branch-protection or ruleset-required checks.
Start at the earliest causal failure, then look for independent failures in
parallel jobs. Record the workflow, job, step, command, and observed error.

Choose local reproduction, a pushed GitHub Actions run, or both by expected
evidence per unit of clock time, context cost, and compute cost. Use local
checks when they isolate the cause quickly; prefer the authoritative remote
workflow when it is environment-specific or expensive to reproduce locally.
Use existing artifacts and focused static inspection when they answer the
question; avoid equivalent duplicate runs.

Classify the primary cause before changing anything:

- `PRODUCT`: branch code, test target, or generated output is wrong.
- `WORKFLOW`: GitHub Actions configuration, permissions, or job wiring is
  wrong.
- `EXTERNAL`: dependency, runner, credential, or service is unavailable.

For `EXTERNAL`, do not change product or workflow code to compensate for the
unavailable capability. Resolve the external condition only when it is
authorized and independently verifiable; otherwise return `NOT FIXED`.

Treat flakiness as a confidence modifier. A rerun without a relevant change
ends as `NOT FIXED — WORKFLOW GREEN — FLAKE NOT RESOLVED` until nondeterminism
is understood.

### 3. Repair and verify

Apply the smallest correct repair at the layer that owns the failure. Keep
required checks and their failure semantics, subject to the evidence rule in
`Forbidden repairs`. For product and test
defects, add or strengthen the focused regression evidence before declaring
success.

Map product or test repairs to the affected requirements and their observable
results. Record replacement evidence and why it still checks the same promise.
Keep unrelated acceptance gaps visible without expanding this CI repair into a
full implementation or proof run.

Run the cheapest high-signal verification first, whether local or remote. Use
the authoritative GitHub workflow as the primary verification when it is the
more efficient evidence source; run broader local checks only when their
additional evidence justifies the cost.
Verify every required check reported by the target PR's branch protection or
ruleset, not only the original failed job. For a workflow-run target, use its
associated PR when available; otherwise verify every check represented by the
run and state that branch-protection requirements could not be established.
Count a required check only when it succeeds for the exact repaired SHA.
Pending, queued, cancelled, timed-out, skipped, missing, or stale results are
not successful verification. When waiting is authorized, poll adaptively:
use the workflow's observed duration when available, otherwise start at 30
seconds, double the interval up to 5 minutes, and stop at a bounded wait
budget: use the workflow's recent p95 duration when available, otherwise 15
minutes, capped at 30 minutes. Stop immediately on a terminal result; do not
spend calls checking an unchanged run at a fixed short interval. If the budget
expires, return `NOT FIXED — VERIFICATION PENDING` with the run URLs. Confirm
that the repaired commit is pushed, no verification was weakened, and no
unrelated quality regression was introduced.

Allow at most two repair attempts. After a failed verification, use the second
attempt only when the failure identifies a concrete, scoped correction. Stop
after the second unsuccessful attempt. Stop immediately if the cause remains
uncertain, a required capability is unavailable, or the repair would weaken quality.
Also stop when the repair introduces an unexplained quality regression, removes
required verification, or makes an existing quality signal unmeasurable.

## Forbidden repairs

Keep the required quality signal measurable. Do not delete or skip tests,
disable lint rules, lower coverage, make checks optional, swallow failures,
add unconditional `continue-on-error`, add arbitrary retries, or comment out
workflow steps. A check may change only when the source contract and evidence
prove it incorrect or obsolete. The replacement must provide stronger valid
evidence for the same promised behavior. Record the reason and affected
requirement IDs; changing a check does not authorize changing the promise.

Do not redesign workflows, clean up unrelated code, or use a green rerun to
mask an unresolved failure.

## Completion

Return one of these outcomes:

- `FIXED`: the cause is understood, a durable repair and focused verification
  pass, required quality signals are preserved or strengthened, the repaired
  commit is pushed, and all required checks for the target are green.
- `NOT FIXED`: the failure remains unresolved, required capability is
  unavailable, the worktree is unsafe, the repair would weaken quality, or
  only an unexplained rerun passed.

`FIXED` means the workflow is repaired. It does not mean every ticket requirement
is `proven`.

For either outcome, report the intended operation, failure classification,
earliest causal error, files changed, verification performed, required-check
status, and the remaining reason when `NOT FIXED`.
Include the repaired SHA, affected requirement IDs, replaced evidence, and any
acceptance gaps. Changes to implementation or evidence require reassessing prior
proof and review. Identify which results need refreshing on the repaired commit;
use `/prove` for full acceptance verification and the repository's review process
for code quality when those steps are requested or required.

Invoking `/fix-pr` authorizes scoped inspection, edits, commit, push, and
workflow reruns for the target PR or workflow run. It does not authorize
force-pushes, changes outside the target branch, or workarounds that weaken
verification.
