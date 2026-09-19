---
name: acceptance-matrix
description: Turn a spec, ticket, or conversation into a small, proof-ready acceptance matrix with stable requirement IDs and exact evidence paths.
disable-model-invocation: true
---

`/acceptance-matrix` turns source material into a traceable contract for
implementation and verification. It makes each material requirement atomic,
observable, falsifiable, and tied to evidence without inventing product
decisions or expanding test scope.

The output is a Markdown matrix that can be pasted into a ticket or handed to
`/implement`. It is a planning artifact, not proof: a row becomes `proven`
only when its named evidence has run successfully and `/prove` accepts it.

## Inputs and scope

Accept any of these sources:

- a spec or plan file;
- one or more tickets or issue excerpts;
- the current conversation when it contains the requirements.

Read the source before drafting. Follow linked parent specs only far enough to
inherit constraints that apply to this work. If the source cannot establish a
contract, report that gap instead of manufacturing requirements.

This skill only produces the matrix. It does not implement product code, write
project tests, edit issue trackers, publish tickets, replace `/to-spec`, or
replace `/prove`.

## Core rules

1. **Extract material requirements.** Include only claims required by the
   source contract, an inherited applicable constraint, or a necessary domain
   invariant. Do not promote implementation preferences, speculative edge
   cases, or coverage goals into requirements.
2. **Make rows atomic.** Split compound or vague criteria such as “works
   correctly” into separate observable claims. Each row must be falsifiable by
   a concrete scenario or check.
3. **Merge duplicates.** If multiple tickets or sections state the same
   requirement, keep one row and record all relevant source references rather
   than repeating it.
4. **Preserve traceability.** Keep source-provided requirement IDs. Otherwise
   assign `R1`, `R2`, ... in source order. Once assigned, do not renumber
   existing IDs when adding rows. Use the `Source` column to retain mapping
   across multiple tickets.
5. **Name boundaries.** For each row, record relevant negative cases and
   boundaries such as empty/one/many, invalid input, authorization, retries,
   persistence or restart, state transitions, and operational failure. Include
   only boundaries supported by the source, domain, or actual code path.
6. **Choose credible evidence.** Prefer the repository’s existing public seams
   and testing conventions. Avoid private implementation assertions, copied
   production calculations, mock-only evidence, and tests added solely for
   coverage.
7. **Do not guess.** Put missing product decisions, ambiguous terms, unknown
   ownership, and unavailable verification commands in `Open questions` or
   `Unresolved gaps`. Do not hide them in a broad requirement.

## Evidence mapping

Every material row must have exactly one primary evidence type and an exact
evidence path:

- **behavioral test** — a named test file and test case at the highest
  meaningful public seam;
- **invariant** — a named database constraint, type constraint, schema
  validation, state guard, or test that demonstrates the invariant;
- **verification command** — the exact deterministic command or check for an
  operational, build, migration, or configuration requirement.

Evidence can be planned before implementation. Say exactly what should be
added or run, for example `tests/orders.test.ts — “rejects a second capture”`
or `npm test -- orders.test.ts`. Do not call planned evidence `proven`.

Use these statuses only:

- `planned` — the requirement and evidence path are defined, but the evidence
  is not yet successful;
- `proven` — the named evidence exists, was run successfully in the current
  verification context, and directly supports the row;
- `not proven` — evidence is missing, weak, inconclusive, or has not been run;
- `disproven` — a concrete counterexample or failing evidence shows the
  requirement is violated.

Code inspection alone is not proof for a central behavioral requirement. If
inspection is the best available evidence, mark the row `not proven` and say
why in `Unresolved gaps`.

## Workflow

### 1. Establish the source contract

Identify the source and its scope. Extract explicit acceptance criteria,
requested user-visible behavior, negative requirements, state transitions,
data preservation rules, operational requirements, and directly relevant
parent constraints. Resolve terminology using the repository’s domain
vocabulary.

### 2. Inspect the repository

Before choosing evidence, inspect the relevant public seams, existing tests,
schemas, type constraints, commands, and neighboring skills. Reuse existing
test names, file locations, fixtures, and verification commands when they fit.
Do not invent an abstraction or test infrastructure just to make the matrix
look complete.

### 3. Build the matrix

Create one row per material, observable requirement. Merge duplicates, assign
stable IDs, state the scope, call out concrete boundaries, choose the evidence
type, and name the exact test, invariant, or command. Keep requirements
separate from implementation tasks.

### 4. Audit for gaps

Check that every row is falsifiable, has one evidence type, has an exact
evidence path, and has a status justified by the available evidence. Report
ambiguous source language, missing decisions, weak evidence, unavailable
commands, and relevant out-of-scope concerns separately. Do not add rows to
maximize coverage.

### 5. Hand off cleanly

Return the Markdown matrix. Keep IDs and evidence mappings unchanged if the
matrix is later updated. `/implement` can use `planned` rows as its worklist;
`/prove` can independently verify the named evidence and update the statuses.

## Output format

Use this structure unless the user asks for another format:

```markdown
# Acceptance Matrix — <source>

## Matrix

| ID | Source | Requirement and scope | Boundaries / counterexamples | Evidence type | Exact evidence | Status |
|---|---|---|---|---|---|---|
| R1 | <ticket/spec> | <one observable, falsifiable claim> | <relevant negative case or boundary> | behavioral test | `<path>` — `<test case>` | planned |

## Unresolved gaps

- <missing, weak, or unavailable evidence, or “None”>

## Open questions

- <unresolved product or scope decision, or “None”>

## Out of scope

- <nearby concern deliberately excluded, or “None”>
```

The matrix must be useful even when the source contains several tickets: use
one combined ID sequence, preserve source references, and keep duplicate
requirements merged. If the source uses vague language and no defensible
atomic interpretation exists, leave the requirement unresolved rather than
silently choosing one.
