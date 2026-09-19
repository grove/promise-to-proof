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

Before editing, inspect the branch and worktree. Continue only when changes
are either clean or clearly part of the target branch; stop with `NOT FIXED`
when unrelated edits, missing credentials, unavailable permissions, or an
unsafe branch state make the repair ambiguous.

Preserve the verification boundary that exposed the failure:

- Keep every required job, test, assertion, lint/type check, coverage
  threshold, matrix entry, and failure condition.
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

### 2. Diagnose before editing

Inspect the workflow run, failed jobs and steps, logs, workflow YAML, relevant
changes, and required PR checks. Start at the earliest causal failure, then
look for independent failures in parallel jobs. Record the workflow, job,
step, command, and observed error.

Reproduce a failing command locally or remotely only when it is the cheapest
useful way to distinguish plausible causes or validate a risky repair. Prefer
existing artifacts and focused static inspection; avoid equivalent duplicate
runs.

Classify the primary cause before changing anything:

- `PRODUCT`: branch code, test target, or generated output is wrong.
- `WORKFLOW`: GitHub Actions configuration, permissions, or job wiring is
  wrong.
- `EXTERNAL`: dependency, runner, credential, or service is unavailable.

Treat flakiness as a confidence modifier. A rerun without a relevant change
ends as `WORKFLOW GREEN — FLAKE NOT RESOLVED` until nondeterminism is
understood.

### 3. Repair and verify

Apply the smallest correct repair at the layer that owns the failure. Keep
required checks and their failure semantics unchanged. For product and test
defects, add or strengthen the focused regression evidence before declaring
success.

Run the cheapest high-signal verification first. Then run broader local checks
or the authoritative GitHub workflow when their evidence justifies the cost.
Verify all required checks for the target PR or commit, not only the original
failed job. For a workflow-run target, use its associated PR when available;
otherwise verify the run's required checks. Confirm that the repaired commit
is pushed, no verification was weakened, and no unrelated quality regression
was introduced.

Cap repair attempts. If the cause remains uncertain, a required capability is
unavailable, a verification fails, or the repair would weaken quality, stop.
Also stop when the repair introduces an unexplained quality regression, removes
required verification, or makes an existing quality signal unmeasurable.

## Forbidden repairs

Keep the required quality signal measurable. Do not delete or skip tests,
disable lint rules, lower coverage, make checks optional, swallow failures,
add unconditional `continue-on-error`, add arbitrary retries, or comment out
workflow steps. A check may change only when evidence proves it incorrect or
obsolete, and the replacement must provide stronger valid evidence.

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

For either outcome, report the intended operation, failure classification,
earliest causal error, files changed, verification performed, required-check
status, and the remaining reason when `NOT FIXED`.

Invoking `/fix-pr` authorizes scoped inspection, edits, commit, push, and
workflow reruns for the target PR or workflow run.
