---
name: prove
description: Verify an implemented issue against its promises without changing the candidate, and report PROVEN or NOT PROVEN with concrete evidence.
disable-model-invocation: true
---

`/prove` checks whether a ticket, specification, or agreed outcome is actually
met. It verifies a fixed candidate and reports gaps; it does not repair the
candidate. Use `/repair-proof` for scoped repairs, then run `/prove` again.

Before verification, read the [acceptance contract protocol](references/acceptance-contract-protocol.md).
It defines the spec envelope, identities, evidence, and verdicts.

## Verdicts

- `PROVEN`: every material requirement has credible evidence, no contract
  discrepancy remains, and the candidate stayed fixed during verification.
- `NOT PROVEN`: any requirement lacks evidence, a counterexample remains, the
  contract is incomplete or ambiguous, tooling is unavailable, or candidate
  identity is uncertain.
- A concrete violation is `disproven`; unavailable or inconclusive evidence is
  `not proven`, not `disproven`.

## Rules

- Reconcile the versioned acceptance contract with the source and authorized
  amendments. Report discrepancies without narrowing or rewriting the contract.
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
- Reject stubbed or fixture-specific behavior, mock-only substitutes, and
  evidence that bypasses required production state. Distinguish a demonstrated
  violation from a weak check that leaves the outcome unknown.
- Judge the complete promised capability. Do not penalize a small implementation
  for lacking unnecessary architecture. Report unrequested scope against the
  contract's exclusions or source reconciliation, not architectural taste.

## Workflow

### 1. Establish the contract

Resolve the canonical contract location using the protocol's durable handoff
convention. Read the source, pending amendments, applicable parent constraints,
and exact acceptance contract revision. Preserve all requirement IDs, boundaries,
seams, oracles, open questions, and exclusions. Report omitted, conflicting, or
ambiguous source promises instead of editing the contract. If no versioned
contract can be established, report `NOT PROVEN` and hand off to
`/acceptance-contract`; do not create or revise it during proof.

### 2. Identify the candidate

Record the full commit SHA or exact snapshot, contract source and revision,
captured contract identity, target or base when relevant, and verification
environment. Follow the protocol's identity rules and confirm both identities
before checks begin. If either cannot be established, return `NOT PROVEN`.
If the candidate or contract drifts, or observations cannot be tied to them,
return `NOT PROVEN`.

### 3. Map and audit evidence

For every requirement, name the observation and the independent oracle that says
whether it passes. Check existing tests, invariants, schemas, and commands at the
agreed public seam. If a seam or oracle needs a consequential change, report the
decision as a gap rather than silently replacing it. A passing suite or checked
GitHub criterion does not cover a promise whose result is never asserted.

### 4. Hunt counterexamples

Check realistic boundaries: empty/one/many, state transitions, retries, restart,
authorization, concurrency, and the final workflow outcome. When useful, run a
controlled sensitivity check only in a disposable copy; discard it afterward.

### 5. Verify without mutation

Run the smallest high-signal checks that establish the requirements. Preserve
durable evidence outside the candidate and tie each reference to its observation,
assertion, command, and environment. The saved proof report may hold the evidence
itself under the protocol's evidence rules. Check the candidate, worktree, and
captured contract again afterward. Never fix a failure in this skill. Report
the smallest complete repair needed and name the affected requirement IDs for
`/repair-proof`.

### 6. Report

Return the intended outcome, contract reconciliation, candidate, environment,
every requirement verdict, evidence observations, counterexamples, candidate
stability, and unresolved gaps. A proof result must account for every requirement
ID and must not hide an unmet promise.

## Output

```markdown
# <PROVEN | NOT PROVEN>: <source>

Requirements: <proven>/<total>
Counterexamples tested: <count>
Contract: <source and exact revision, such as #124 v3>
Contract snapshot: <immutable reference or captured text and digest>
Candidate: <commit or exact snapshot>
Candidate stability: <unchanged or NOT PROVEN>
Contract stability: <unchanged or NOT PROVEN>
Verification context: <environment>

## Outcome

<intended result and why it is or is not established>

## Requirement verdicts

| ID | Observation and oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | <observed outcome and independent expected result> | <saved report section, artifact, or run; command and assertion> | proven |

## Unresolved gaps

- <requirement, counterexample, or limitation, or "None">

## Repairs needed

- <requirement ID and smallest complete repair, or "None">

Fresh `/prove` is required after any repair.
```
