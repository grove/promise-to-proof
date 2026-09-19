# Acceptance-matrix skill spec

## Problem Statement

The existing workflow can produce specs and tickets, but acceptance criteria often remain broad checkboxes. Implementers then have to decide what each criterion means, which edge cases matter, and how to verify completion. That leaves gaps for `/prove` to find late and gives `/code-review` too little behavioral context.

## Solution

Create an `acceptance-matrix` skill that turns a spec, ticket, or conversation into
a testable agreement about what the PR must deliver. State the intended outcome
and produce the smallest complete set of independently verifiable requirements.

Each matrix row must describe one material, observable, falsifiable requirement and identify:

- the requirement and its scope;
- relevant boundaries or counterexamples;
- the evidence type: behavioral test, invariant, or verification command;
- the exact test, invariant, or command and the assertion or enforced condition that establishes success;
- the current status: planned, proven, not proven, or disproven.

The skill should prefer existing public seams and repository testing patterns. It should identify missing or ambiguous requirements instead of silently guessing, while avoiding speculative requirements and coverage-driven test expansion.

The output guides implementation and PR review directly. `/prove` consumes an
existing matrix, independently checks its completeness, and reconciles every
requirement with current evidence. An optional `/implement` skill may also use it.

## User Stories

1. As an implementer, I want each acceptance criterion split into atomic requirements, so that I know exactly what behavior to build.
2. As an implementer, I want each requirement mapped to evidence, so that I write the necessary tests while implementing.
3. As a reviewer, I want negative cases and boundaries called out, so that happy-path tests do not hide defects.
4. As a verifier, I want stable requirement identifiers, so that I can trace each requirement from ticket to test and final result.
5. As a maintainer, I want existing seams and test conventions reused, so that the skill does not create unnecessary abstractions or test infrastructure.
6. As a project owner, I want unresolved ambiguity reported explicitly, so that missing product decisions are not disguised as implementation decisions.

## Implementation Decisions

- The skill is user-invoked and produces the matrix without invoking or modifying other skills.
- It accepts a spec, ticket, or current conversation as its source material.
- It produces one matrix with stable IDs such as `R1`, `R2`, and `R3`.
- A requirement is considered material only when it is required by the source contract, an inherited constraint, or a necessary domain invariant.
- Behavioral requirements should map to tests at the highest meaningful public seam.
- Data and state invariants may map to database constraints, type constraints, schema validation, or tests that demonstrate the constraint.
- Operational requirements must map to an exact verification command or deterministic check.
- The skill should use the repository’s existing domain vocabulary and testing patterns.
- The skill should report gaps and unresolved questions separately from the matrix rather than inventing answers.
- Later steps preserve IDs and promises, report authorized scope changes, and explain replacement evidence. Unresolved requirements prevent declaring the ticket complete.
- Check that passing all rows establishes the intended workflow outcome. Tests that only start individual steps are insufficient.
- The default output is Markdown that can be pasted into a ticket or saved with the implementation plan.

## Testing Decisions

- Test the skill with representative specs containing happy paths, negative requirements, state transitions, persistence boundaries, authorization boundaries, and operational checks.
- Verify that every material requirement receives an evidence type and an exact evidence path.
- Verify that vague criteria such as “works correctly” are split or reported as unresolved.
- Verify that duplicate requirements are merged rather than repeated.
- Verify that out-of-scope concerns are not promoted into requirements.
- Verify that the output preserves requirement IDs across multiple tickets and reports changes to evidence mappings.
- Verify that `/prove` retains unmet promises, detects omitted requirements, and distinguishes unavailable evidence from a demonstrated violation.
- Prefer assertions about the generated matrix’s observable structure and content over exact prose wording.

## Out of Scope

- Editing external issue trackers or publishing tickets.
- Implementing product code or writing project tests directly.
- Replacing `/prove`’s independent verification.
- Replacing `/to-spec`’s product and technical specification work.
- Maximizing test coverage or generating tests for every implementation branch.
- Resolving product decisions that the source material leaves ambiguous.

## Further Notes

The intended workflow is:

Ticket or spec → `/acceptance-matrix` → implementation → `/prove` → code review.

`/interrogate` supports design discussion. `/fix-pr` repairs failed CI without
declaring the whole ticket proven. `/to-spec`, `/to-tickets`, `/implement`, and
`/code-review` are optional integrations not shipped in this repository.

The matrix is a planning and traceability artifact, not proof by itself. A row becomes `proven` only after its named evidence has run successfully and `/prove` accepts the evidence.

The spec could not be published to an issue tracker because no tracker configuration or triage vocabulary was available in the current workspace.
