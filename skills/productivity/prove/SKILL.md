---
name: prove
description: Verify an implemented issue against its promises without changing the candidate, and report PROVEN or NOT PROVEN with concrete evidence.
disable-model-invocation: true
---

`/prove` checks whether a ticket, specification, or agreed outcome is actually
met. It verifies a fixed candidate and reports gaps; it does not repair the
candidate. Use `/repair-proof` for scoped repairs, then run `/prove` again.

## Verdicts

- `PROVEN`: every material requirement has credible evidence, no contract
  discrepancy remains, and the candidate stayed fixed during verification.
- `NOT PROVEN`: any requirement lacks evidence, a counterexample remains, the
  contract is incomplete or ambiguous, tooling is unavailable, or candidate
  identity is uncertain.
- A concrete violation is `disproven`; unavailable or inconclusive evidence is
  `not proven`, not `disproven`.

## Rules

- Treat the source ticket or specification and authorized amendments as the
  contract. Do not silently narrow or rewrite it.
- Use a clean commit as the candidate when possible. A dirty or changing
  worktree is `NOT PROVEN` unless its exact snapshot can be established.
- A proof run may not mutate the candidate, worktree, or contract. If any such
  change occurs, return `NOT PROVEN` and discard observations from the changed
  state; the repair belongs to `/repair-proof` and requires a fresh `/prove`.
- Do not edit product code, tests, CI configuration, or the acceptance contract.
- Do not commit, push, publish, or declare a repair.
- Prefer behavioral evidence through public interfaces and independent oracles.
- A test that only runs a path, uses a tautological assertion, or relies on a
  mock that cannot fail does not prove the promised result.

## Workflow

### 1. Establish the contract

Read the source, applicable parent constraints, and acceptance matrix. Preserve
all requirement IDs, boundaries, open questions, and exclusions. Report omitted,
conflicting, or ambiguous source promises in the result instead of editing the
contract.

### 2. Identify the candidate

Record the commit or exact snapshot, contract, target or base when relevant, and
verification environment. Confirm them before checks begin. If the candidate or
contract drifts, or the observations cannot be tied to them, return `NOT PROVEN`.

### 3. Map and audit evidence

For every requirement, name the observation and the independent oracle that says
whether it passes. Check existing tests, invariants, schemas, and commands at the
highest useful public seam. A passing suite does not cover a promise whose result
is never asserted.

### 4. Hunt counterexamples

Check realistic boundaries: empty/one/many, state transitions, retries, restart,
authorization, concurrency, and the final workflow outcome. When useful, run a
controlled sensitivity check only in a disposable copy; discard it afterward.

### 5. Verify without mutation

Run the smallest high-signal checks that establish the requirements. Check the
candidate and worktree again afterward. Never fix a failure in this skill. Report
the smallest repair needed and name the affected requirement IDs for
`/repair-proof`.

### 6. Report

Return the intended outcome, contract reconciliation, candidate, environment,
every requirement verdict, evidence observations, counterexamples, candidate
stability, and unresolved gaps. A proof result must account for every requirement
ID and must not hide an unmet promise.

## Output

```markdown
# <PROVEN | NOT PROVEN> — <source>

Requirements: <proven>/<total>
Counterexamples tested: <count>
Candidate: <commit or exact snapshot>
Candidate stability: <unchanged or NOT PROVEN>
Verification context: <environment>

## Outcome

<intended result and why it is or is not established>

## Acceptance matrix

| ID | Requirement | Evidence observation and oracle | Status |
|---|---|---|---|
| R1 | <promise> | <what was observed and what independently proves it> | proven |

## Unresolved gaps

- <requirement, counterexample, or limitation, or "None">

## Repairs needed

- <requirement ID and smallest repair, or "None">

Fresh `/prove` is required after any repair.
```
