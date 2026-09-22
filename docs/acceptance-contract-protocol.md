# Acceptance contract protocol

Build exactly the promised capability: no less in substance, no more in scope.
Prefer the simplest complete implementation.

## Contract and proof

The acceptance contract says what must be true. Proof says whether it was true
for one exact candidate.

| Artifact | Contents | Identity |
|---|---|---|
| Acceptance contract | Requirements, boundaries, seams, oracles, planned evidence, gaps, and exclusions | Source and contract revision, such as `#124 v3` |
| Proof report | Observations, durable evidence references, and requirement verdicts | Exact contract revision and exact candidate commit or snapshot |

The contract is candidate-independent. Its acceptance matrix uses only `planned`
and `gap` as plan states. Candidate-specific verdicts belong only in proof
reports, including verdicts imported from earlier runs.

## Spec envelope

The lower bound is completeness. Every material promise must reach its complete
observable outcome. Necessary state transitions, invariants, persistence, and
failure behavior belong to the implementation when that outcome depends on them.
Stubs, TODOs, fixture-specific behavior, mock-only substitutes, wiring-only
assertions, and incomplete happy paths do not satisfy a requirement.

The upper bound is scope. Unrequested product behavior, genericity,
configurability, extension points, frameworks, compatibility layers, and adjacent
improvements are outside the contract. Necessary internal engineering and
repository-native abstractions are allowed when correctness requires them.
An explicit invariant can require substantial work. A small implementation can
fully satisfy the contract without extra architecture.

The target is the smallest complete solution. Line count does not establish
completeness or overengineering. Implementation choices stay inside this envelope
and do not authorize changing it.

## Requirements and revisions

Each independently falsifiable promise has a stable ID such as `R1`. Input
variations belong in its boundaries. Existing GitHub acceptance checkboxes are
sources to reconcile with these rows, not a second checklist to duplicate.
A checked box is never acceptance evidence.

Reruns preserve IDs by matching the existing promises, not row order. New
requirements receive unused IDs. Splits and merges record the old-to-new mapping;
retired IDs remain recorded and are never reassigned to unrelated promises.
Never silently rewrite an existing requirement.

Contracts start with `Contract revision: v1`. An authorized change to a material
promise, boundary, expected outcome, or exclusion increments the revision.
Record the affected IDs, previous and new agreement, and authorization in a
change note. Preserve the prior revision so old proof remains interpretable.
New evidence, a changed test path, or wording that preserves meaning does not
increment the revision. A changed promise requires fresh proof.

## Seams, oracles, and evidence plans

A seam is the highest meaningful public interface through which a requirement
can be observed. Reuse seams agreed in specification or TDD work. A consequential
new seam is an explicit design decision, not an implementation convenience.

An oracle is the independent source that determines whether an observation is
correct. Use the contract, a known-good example, or another independent source.
Copying production logic into the expected result is not an independent oracle.

Each row names its seam, oracle, and one primary evidence path:

- A behavioral test with a named case and an assertion of the promised outcome.
- An invariant with a named constraint or guard and a check that it prevents the
  counterexample through the relevant interface.
- An exact verification command and the condition its successful exit establishes.

`planned` means a credible, concrete path exists but has not established
acceptance. `gap` means the path, seam, or oracle is missing or inadequate.
Unresolved product decisions go in open questions, evidence limits in unresolved
gaps, and deliberate exclusions in out of scope. Planning does not run proof.

## Implementation handoff

Implement the minimum complete solution inside the spec envelope. For every
requirement, reach the real observable outcome and implement the state,
invariant, and failure behavior it needs. Start evidence at the agreed public
seam. Prefer existing repository mechanisms and add machinery only where
correctness requires it. Preserve requirement IDs and promised outcomes.

Specification, ticket slicing, implementation, and TDD retain their own
workflows. This contract is the artifact those workflows consume.

## Proof and repair handoffs

Every proof run binds an exact contract revision to one exact candidate. Record
the full commit SHA or a reproducible snapshot covering relevant tracked and
untracked files. Preserve the exact contract text used, with an immutable
reference or captured content and digest, even when its revision did not change.
An issue number, branch name, or `HEAD` alone is not an exact identity.

Proof records each requirement's observation, independent oracle, durable
evidence reference, and verdict. Evidence references identify the assertion and
its saved output, artifact, or immutable run, with the command and environment
needed to interpret it. Checkbox state and green CI alone do not prove a ticket.

- `proven`: credible evidence establishes the full requirement for this candidate.
- `disproven`: a concrete observation violates the requirement.
- `not proven`: evidence or identity is unavailable, weak, ambiguous, or inconclusive.

Overall `PROVEN` requires every material requirement to be proven, no unresolved
contract discrepancy, and unchanged candidate and contract throughout the run.
Otherwise the result is `NOT PROVEN`. Proof leaves the candidate, worktree, and
contract unchanged. Save evidence outside the candidate. Drift invalidates the
run rather than authorizing a repair during proof.

Repair means the smallest complete repair for the named requirements: narrow in
scope, complete in depth. Preserve valid checks and the contract. A repair never
silently weakens a promise or declares acceptance.

Any changed candidate requires fresh proof against all requirements before
acceptance. Prior proof describes only its original candidate. This includes CI
repairs that change product behavior, acceptance evidence, or relevant tests.
A green CI repair does not refresh proof automatically.
