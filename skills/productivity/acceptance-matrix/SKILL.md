---
name: acceptance-matrix
description: Turn a spec, ticket, or conversation into atomic acceptance requirements with stable IDs, concrete evidence paths, and explicit gaps.
disable-model-invocation: true
---

Turn the ticket's promises into a testable agreement: what the PR must deliver
and how implementation, review, and verification will judge it. State the intended
user or operational outcome, then map every material promise to an observable
result and credible evidence.

By itself, this skill only produces the matrix. Implementing code, writing tests,
running proof, or publishing requires authorization from the broader user request.
New matrices describe requirements and evidence plans; only `/prove` assigns
completed verification verdicts.

Aim for the smallest complete set of independently verifiable requirements.
Row count follows the contract; completeness and credible evidence take priority
over brevity. A finished matrix defines how to judge success, not a guarantee
that the implementation succeeds.

## Build the matrix

1. Read the supplied spec, plan, tickets, or conversation. Follow parent links
   only for applicable constraints. If no contract can be established, report
   the missing source and stop. Use the repository's domain vocabulary.
2. Extract every material requirement: explicit behavior, negative requirements,
   state transitions, data preservation, operational constraints, and necessary
   domain invariants. Tie each to its source or explain the invariant's basis.
   For requested workflows, capture successful completion as an observable
   outcome, not merely the ability to start individual steps.
   Implementation preferences, speculative edge cases, and coverage goals do
   not establish requirements.
3. Make each row one observable claim that a concrete counterexample could
   falsify. State the conditions and required result precisely enough for an
   implementer and reviewer to agree on what passes. Split distinct obligations
   that can succeed or fail independently.
   Keep input variations and failure scenarios for the same obligation in its
   boundaries and evidence; one requirement may need several test cases.
   Put ambiguous language such as "works correctly" in `Open questions` when
   its meaning cannot be established. Merge duplicates and retain all source
   references.
4. Preserve existing requirement IDs. Otherwise assign `R1`, `R2`, ... in source
   order across all tickets, skipping used IDs. Qualify colliding source IDs
   with their ticket or document. On updates, keep IDs stable and note changes
   to requirements or evidence mappings.
5. Record boundaries supported by the source, domain, or actual code path,
   such as empty/one/many, authorization, retries, restart, state transitions,
   or operational failure. Use concrete scenarios relevant to the row.
6. Inspect relevant public interfaces, tests, schemas, constraints, and configured
   commands before mapping evidence. Reuse repository conventions and existing
   checks that support the claim. When repository access is missing, retain the
   known requirements and report evidence gaps.

## Map evidence and status

Choose one primary evidence type per row:

| Evidence type | Exact evidence |
|---|---|
| behavioral test | Test file and named case at the highest meaningful public interface |
| invariant | File or schema location and named database/type constraint, validation, state guard, or test demonstrating it |
| verification command | Exact deterministic command or check for an operational, build, migration, or configuration requirement |

Evidence must establish the claim through observable outcomes or enforcement.
Expected values come from the contract, not copied production calculations;
private implementation assertions and mock-only checks are insufficient for
behavioral claims. Include supporting checks when the primary evidence needs them.
For each evidence target, name the assertion or enforced condition that
distinguishes success from the row's counterexample. A test name, successful
command exit, or exercised code path alone does not establish a behavioral claim.
Shared tests may support several rows only when their assertions establish each
claim separately. Map additional cases where the primary check leaves a relevant
boundary untested.

Distinguish existing evidence from proposed additions. A proposed test can have
an exact target, such as `tests/orders.test.ts :: rejects a second capture`,
when repository conventions support it. If a credible path or command cannot
be determined, write `unresolved`, mark the row `not proven`, and explain the
gap by ID. Keep the requirement visible without inventing repository facts.

| Status | Use when |
|---|---|
| `planned` | A concrete evidence path is proposed for implementation or a future run; no verification verdict exists |
| `proven` | A prior `/prove` result accepted the named evidence in its verification context; do not assign this in a new matrix |
| `not proven` | Evidence cannot yet be mapped, or a verification attempt cannot establish the claim because checks are unrun, weak, or inconclusive |
| `disproven` | A prior `/prove` result recorded a concrete counterexample or failing check; do not assign this in a new matrix |

New matrices normally use `planned` and `not proven`. Carry verification
verdicts only with their supporting results and context, including the verified
commit or worktree state and relevant environment. Reassess a verdict
when its requirement, evidence, or implementation changes. Inspection alone
cannot justify `proven`: a concrete proposal with no verification verdict remains
`planned`, while an inspection-only verification verdict is `not proven`.
A tool or environment failure does not establish `disproven`.

## Check and hand off

Audit the draft before returning:

- Read the source again and account for every material requirement with a row
  or an explicit open question. Check in reverse that each row has a source or
  a justified domain invariant.
- Challenge the overall outcome: could every row pass while the ticket's
  intended result still fails? Trace the requested workflow from its trigger
  through completion and identify the rows and evidence that establish that
  outcome. Separate checks that steps can start are insufficient. Use realistic
  scenarios grounded in the contract and actual workflow, especially data loss,
  authorization, and partial failure where relevant. Add a missing obligation,
  strengthen evidence for an existing one, or expose an unresolved decision.
- Check row size: removing a row must lose a distinct obligation; splitting one
  must expose independently verifiable obligations, not just more test inputs.
  Merge duplicates without losing source references or relevant boundaries.
- Check each claim against its counterexamples and evidence. Record weak or
  missing checks as gaps and apply the status rules above.

Finish when these checks expose no further supported omissions, redundant rows,
or compound obligations, and remaining uncertainties are explicit. Identify which
open decisions block implementation and which evidence gaps block verification.
An unresolved requirement stays visible and prevents declaring the ticket resolved.

Return the outcome and matrix together for implementation, PR review, and a later
`/prove` run. Keep product and scope decisions in `Open questions`, evidence
limitations in `Unresolved gaps`, and excluded nearby concerns in `Out of scope`.
Include this handoff rule: account for every requirement ID in verification,
report changed or dropped promises with their source and authorization, and keep
unmet promises visible. Evidence may improve; the promised result must not be
weakened to fit the implementation.

The matrix can guide implementation and review directly. `/implement` and
`/code-review` are optional integrations; producing the matrix does not require
those skills to be installed or authorize invoking other skills.

## Output format

Use this structure unless the user asks for another format. The upload rows
illustrate atomic promises and concrete assertions; replace them and their
illustrative test paths with requirements and evidence grounded in the task.

```markdown
# Acceptance matrix: <source>

Intended outcome: A user can recover a failed upload and retrieve the original
file with its metadata intact, without creating a duplicate.

## Matrix

| ID | Source | Requirement and scope | Boundaries / counterexamples | Evidence type | Exact evidence | Status |
|---|---|---|---|---|---|---|
| R1 | <retry criterion> | After retrying a failed upload, the user can retrieve the original file bytes | Retry is accepted but the upload never completes or returns different bytes | behavioral test | Proposed: `tests/uploads.test.ts :: retrieves file after retry`; retrieve through the public interface and assert bytes equal the original fixture | planned |
| R2 | <no-duplicates criterion> | Retrying the same failed upload leaves exactly one stored upload | Retry creates a second stored upload | behavioral test | Proposed: `tests/uploads.test.ts :: retry creates no duplicate`; assert exactly one upload exists for this operation | planned |
| R3 | <metadata criterion> | Retrying preserves the upload's original filename and description | Upload completes but metadata is reset | behavioral test | Proposed: `tests/uploads.test.ts :: retry preserves metadata`; assert retrieved filename and description equal their original fixture values | planned |

## Unresolved gaps

- <missing, weak, or unavailable evidence, or "None">

## Open questions

- <unresolved product or scope decision, or "None">

## Out of scope

- <nearby concern deliberately excluded, or "None">

Verification handoff: Account for every requirement ID. Report changed or dropped
promises with their source and authorization. Keep unmet promises visible;
improve evidence without weakening the required results.
```
