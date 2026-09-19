# `/fix-pr` Skill Design

## Status

Proposed

## Summary

`/fix-pr` diagnoses and repairs failed GitHub workflows for pull requests, then verifies that the PR branch satisfies its required checks.

A workflow is not fixed merely because the YAML parses or a rerun turns green. The skill must determine:

1. why the workflow failed,
2. whether the failure represents a real code defect, CI defect, environment problem, or transient failure,
3. what the smallest correct repair is,
4. whether the PR's required checks pass on the repaired commit.

---

# Primary Objective

> **Restore the workflow's intended outcome by identifying and fixing the underlying failure without weakening the verification that exposed it.**

The skill optimizes for the successful operation and the shortest practical time-to-green, not merely a green workflow badge. Every diagnostic or verification action is speculative: choose it when its expected diagnostic value justifies its clock-time and token cost, and avoid redundant local or remote runs.

---

# Typical Invocation

For a pull request:

```text
/fix-pr #123
```

or:

```text
/fix-pr https://github.com/acme/project/pull/123
```

For a failed workflow run:

```text
/fix-pr <workflow-run-url>
```

The skill should infer the relevant workflow from the supplied PR or run whenever possible.

---

# Verification boundary

The skill must restore the intended outcome without weakening verification. Do not delete or skip tests, disable lint rules, lower coverage, make checks optional, swallow failures, add unconditional `continue-on-error`, add arbitrary retries, or comment out workflow steps.

## PR quality invariants

Repairing a workflow must not make the pull request less trustworthy. The skill must:

* preserve every required job, test, assertion, lint/type check, coverage threshold, matrix entry, and failure condition unless it proves that the item is incorrect or obsolete;
* never delete or weaken a test merely because it exposes the failure;
* add or strengthen a focused regression test for a product or test defect when the repository has an appropriate test seam;
* use an independent behavioral assertion for new regression evidence rather than copying the implementation's calculation;
* treat a workflow-only fix as successful only when the same quality checks still run with the same failure semantics;
* stop as `NOT FIXED` if the repair introduces an unexplained quality regression, removes required verification, or makes an existing quality signal unmeasurable.

The skill may fix a bad test or check when the contract and evidence show that it is wrong. It must replace the invalid evidence with stronger evidence; it must not simply remove the gate.

Keep repairs scoped to the failure. Do not redesign workflows, clean up unrelated code, or treat reruns as fixes.

---

# Failure Classification

Before changing code, classify the primary cause:

* **Product:** the branch, test target, or generated output is wrong.
* **Workflow:** GitHub Actions configuration, permissions, or job wiring is wrong.
* **External:** a dependency, runner, credential, or service is unavailable.

Flakiness is a confidence modifier, not a separate cause: a rerun without a relevant change is `WORKFLOW GREEN — FLAKE NOT RESOLVED` until nondeterminism is understood.

---

# Workflow

## 1. Establish the Intended Operation

Determine what the failed workflow was supposed to accomplish. For example:

```text
Validate branch before merge
Run required checks for commit abc123
```

The intended operation defines success.

## 2. Diagnose the Failure

Inspect the run, failed jobs and steps, logs, workflow YAML, and relevant changes. Start with the earliest causal failure, then check for independent failures in parallel jobs. Capture the workflow, job, step, command, and observed error.

Reproduce the failing command locally or remotely only when doing so is the cheapest useful way to distinguish plausible causes or validate a risky repair. Prefer existing workflow artifacts and focused static inspection; avoid running equivalent checks twice. State the failure mechanism and classify its primary cause before editing.

## 3. Apply and Verify the Smallest Correct Repair

Repair the product, test, workflow, or external dependency issue while preserving the guarantee that exposed it. For product and test defects, add or strengthen the smallest focused regression test before declaring the repair complete. Do not bypass checks, add arbitrary retries, delete tests, or broaden the change.

Run the cheapest high-signal verification first, and run broader or duplicate checks only when their expected evidence justifies the cost. Rerun or observe the GitHub workflow and verify all required checks, not only the original failing job; when CI is the authoritative signal and local execution adds little, let the workflow provide that evidence. Confirm the repaired commit is pushed, no verification was weakened, and changed tests provide credible evidence. Run any repository-mandated review or requirement check; a green workflow does not replace it.

---

# Final Outcomes

* `FIXED`: the cause is understood, a durable repair is applied, focused verification passes, required quality signals are preserved or strengthened, the repaired commit is pushed, and all required PR checks are green.
* `NOT FIXED`: the failure remains unresolved, required capability is unavailable, the worktree is unsafe, the repair would weaken quality, or only an unexplained rerun passed.

---

# Authorization

Invoking `/fix-pr` authorizes automatic inspection, scoped edits, local verification, commit, push, and workflow reruns for the target PR.

Before editing, require a clean worktree apart from the target branch's known changes. Stop with `NOT FIXED` when unrelated edits, missing permissions, unavailable credentials, or an unsafe branch state would make the repair ambiguous.

Never weaken required checks, suppress failures, or continue past a failed verification merely to obtain a green status. Cap repair attempts and stop when the cause remains uncertain.

---

# Suggested Frontmatter

```yaml
---
name: fix-pr
description: Diagnose and repair failed GitHub Actions workflows for pull requests without weakening required checks, then verify the repaired commit.
disable-model-invocation: true
---
```

Keep the skill user-invoked initially while its automatic commit and push behavior is established.

---

# Initial Version

Support one repository and one PR or workflow-run target: diagnose the earliest causal failure, apply the smallest repair, run focused checks, commit and push, then verify all required checks.
