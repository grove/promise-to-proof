---
name: acceptance-matrix
description: Turn a spec, ticket, or conversation into atomic acceptance requirements with stable IDs, concrete evidence paths, and explicit gaps.
disable-model-invocation: true
---

Turn the source promises into a testable agreement: state the intended outcome,
split it into atomic requirements, and say how each one will be checked.

This skill plans acceptance. It does not implement, verify, or publish. New
matrices contain evidence plans, not completed verification verdicts.

## Build the matrix

1. Read the source and any applicable parent contract. If no source contract can
   be established, report that gap and stop.
2. Extract every material promise: behavior, negative requirements, state changes,
   data preservation, authorization, operational limits, and necessary invariants.
   Do not promote implementation preferences or speculative edge cases.
3. Make each row one observable claim that a concrete counterexample could falsify.
   Preserve source references and stable IDs; keep input variations in boundaries.
4. Record relevant boundaries such as empty/one/many, retries, restart, auth,
   concurrency, and operational failure when the source or code path supports them.
5. Inspect the public interface, existing tests, constraints, and configured
   commands before proposing evidence. If no credible evidence path exists, say so.

## Evidence

Use one primary evidence type per row:

| Type | Evidence |
|---|---|
| behavioral test | A named case through the highest meaningful public interface, with the assertion that proves the result |
| invariant | A named constraint, validation, state guard, or test that prevents the counterexample |
| verification command | An exact deterministic command and the condition its successful exit establishes |

Evidence must check the required result, not merely execute a path. Expected
values come from the contract, not copied production calculations. Mock-only or
private implementation assertions do not establish a behavioral promise.

Use these statuses in a new matrix:

- `planned`: a concrete evidence path is proposed but has not been verified.
- `not proven`: the evidence path is missing, weak, unavailable, or inconclusive.

Carry `proven` or `disproven` only from an existing `/prove` result, with its
candidate and verification context. Do not assign completed verdicts yourself.

## Audit and hand off

- Account for every material source promise, and give every row a source or a
  justified domain-invariant basis.
- Trace the requested workflow through completion. Passing individual steps is
  not enough if the final user or operational outcome can still fail.
- Merge duplicate rows; keep independently falsifiable obligations separate.
- Put product decisions in `Open questions`, evidence limits in `Unresolved gaps`,
  and deliberately excluded concerns in `Out of scope`.
- Keep requirement IDs and promises stable. Later work must report authorized
  changes rather than silently weakening the contract.

## Output

```markdown
# Acceptance matrix: <source>

Intended outcome: <what the user or operator can observe>

## Matrix

| ID | Source | Requirement and scope | Boundaries / counterexamples | Evidence type | Exact evidence | Status |
|---|---|---|---|---|---|---|
| R1 | <source> | <one observable promise> | <what would falsify it> | behavioral test | <named case and assertion> | planned |

## Unresolved gaps

- <missing or weak evidence, or "None">

## Open questions

- <unresolved product decision, or "None">

## Out of scope

- <excluded nearby concern, or "None">

Verification handoff: account for every requirement ID; report authorized
changes or dropped promises; keep unmet promises visible.
```
