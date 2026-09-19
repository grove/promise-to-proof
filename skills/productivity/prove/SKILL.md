---
name: prove
description: Prove that an implemented issue is actually resolved by mapping every material requirement to independent evidence, hunting counterexamples, strengthening tests, fixing discovered gaps, and refusing to declare success while any requirement remains unproven.
disable-model-invocation: true
---

`/prove` is a post-implementation verification skill. It determines whether a GitHub issue has actually been resolved by treating the originating issue as a set of behavioral claims and proving each claim with independent, observable evidence.

Unlike a conventional code review, `/prove` does not primarily ask whether the diff looks clean or follows style guidelines. It starts from the desired outcome:

> **What must be true for this issue to be completely resolved, and can we demonstrate that each of those things is true?**

The primary objective is:

> **Every material claim in the originating issue must have independent evidence, and reasonable attempts to falsify those claims must fail.**

The output is never "looks good" or "seems complete." It is strictly **PROVEN** or **NOT PROVEN**, accompanied by concrete evidence.

---

## Core Principles

1. **Requirements to Evidence, Not Diff to Opinions**: The issue is the contract; the diff is merely one attempt at fulfilling it.
2. **Falsification Over Confirmation**: Actively ask: *"What is the smallest realistic scenario that demonstrates this claim is false?"* Do not just look for passing happy paths.
3. **Evidence Over Confidence Language**: Never use phrases like "looks correct" or "tests appear comprehensive." State demonstrable facts: *"R1 is proven by test X; R2 currently lacks direct evidence."*
4. **Behavioral Completeness Over Test Quantity**: Five meaningful behavioral tests through public seams provide more confidence than fifty shallow unit tests mocking internals.
5. **Independent Oracles**: Assertions must come from domain rules, specs, and issue requirements—not mirrored calculations copied from the production code.
6. **Fix Local Gaps**: When a test or implementation gap within the issue's scope is uncovered, fix it and rerun verification. Do not merely report what is broken when you have the power to repair it.
7. **Comfortable with NOT PROVEN**: Ending in `NOT PROVEN` is a successful outcome when evidence is missing or a genuine gap remains. Never massage evidence to force a pass.

---

## Non-Goals & Scope Discipline

* **Not a general code review**: Formatting, naming, stylistic preferences, and repository conventions belong in `/code-review`. Only flag code quality when it directly undermines confidence that the issue is resolved (e.g. duplicated invariant where one path omits the fix).
* **Not a coverage maximizer**: Never add tests solely to inflate line or branch coverage percentages. Coverage is a diagnostic signal, not an objective.
* **Not a replacement for TDD**: TDD governs development; `/prove` audits the finished outcome and retrofits acceptance proof where missing.
* **Not speculative paranoia**: Counterexamples must be rooted in real domain states, actual control flow, public APIs, storage semantics, and concrete caller contracts—not endless hypothetical scenarios.
* **Not an overengineering pass**: Do not refactor working code because another design looks prettier. Ponytail handles simplicity. Changes must strictly strengthen the proof or fix a demonstrated defect.
* **Scope boundaries**: Only make issue-local repairs and tests. Do not redesign surrounding architecture or expand the feature scope. If a larger architectural defect is discovered outside the issue's boundaries, report it clearly in the final assessment.

---

## The Proof Model

Every issue is converted into an **Acceptance Matrix**:

| Requirement | Evidence | Status |
|---|---|---|
| R1: Failed upload can be retried | `retry-upload.test.ts` (retries after failure) | Proven |
| R2: Retry does not create duplicates | Integration test + DB uniqueness constraint | Proven |
| R3: Metadata survives retry | No direct assertion | Not Proven |
| R4: Retry works after page refresh | Session rehydration integration test | Proven |

Each material requirement must resolve to one of three states:
* **Proven**: Sufficiently direct, credible evidence confirms the required behavior holds.
* **Not Proven**: Requirement may be implemented, but available evidence is weak, absent, or inconclusive.
* **Disproven**: A concrete counterexample or test demonstrates the requirement is violated.

Your goal is to eliminate both `Not Proven` and `Disproven` through verification and targeted local fixes.

---

## Evidence Hierarchy

Evaluate evidence from strongest to weakest:

1. **Behavioral automated test through a public seam** (strongest)
2. **Hard invariant enforced by types, schema, or runtime constraint**
3. **Deterministic executable verification script or CLI check**
4. **Existing system-level or integration test**
5. **Manual / runtime observation when automation is impractical**
6. **Reasoned code inspection** (weakest; rarely sufficient for central behavioral claims)

Explicitly flag any requirement that relies solely on reasoned inspection.

---

## Workflow: The 8-Phase Proof Loop

```text
1. Contract ──> 2. Map Evidence ──> 3. Audit Tests ──> 4. Hunt Counterexamples
                                                                │
8. Declare <── 7. Verify Whole <── 6. Sensitivity <── 5. Strengthen & Fix
```

### Phase 1: Establish the Contract
Read the originating issue before deeply inspecting the implementation diff.
1. **Locate the issue**: From user input (`#123`, URL), branch/commit metadata, PR description, or issue tracker. If no requirement source can be established, stop and ask—never guess requirements.
2. **Extract material requirements**:
   - Explicit acceptance criteria and requested user-visible behaviors.
   - Required state transitions and negative requirements ("must NOT duplicate").
   - Data preservation, error handling, compatibility guarantees, and invariants implied by the outcome.
   - Separate requirements from incidental suggestions, background context, or discarded alternatives. Issue comments that clarify scope take precedence.
3. **Draft the initial Acceptance Matrix** (`R1, R2, ...`).

### Phase 2: Map Existing Evidence
Map existing code to each requirement:
* Inspect tests, runtime validations, database schemas, type constraints, and changed implementation.
* Do not accept "there is a test file with a similar name." Read the actual assertion and confirm it establishes the specific behavioral claim.

### Phase 3: Audit Test Quality
Ensure tests serving as evidence are credible:
* **Behavioral**: Tests observable behavior through a public or agreed seam, not private implementation details.
* **Independent**: The expected value does not mirror production code algorithms or rely on tautological helpers.
* **Sensitive**: The test would actually fail if the requirement broke (avoid mock illusions where mocks predetermine success).
* **Specific & Durable**: Clear failure message when broken; refactoring internal details doesn't break the test.

### Phase 4: Hunt Concrete Counterexamples
Derive plausible failure scenarios directly from the codebase:
* **Adjacent domain states**: If handling `FAILED`, check reachable adjacent states (`CANCELLED`, `TIMED_OUT`, `PARTIAL`).
* **Boundaries**: `0 / 1 / N`, empty vs non-empty, first vs last, authenticated vs unauthorized, expired vs active.
* **Persistence transitions**: Fresh in-memory vs reloaded from database, cached vs uncached, before vs after restart/refresh.
* **Idempotency & retries**: What happens when the operation or network call triggers twice?
* **Concurrency boundaries**: Check-then-write sequences, missing unique constraints, race windows.
* **Error paths**: Dependency fails halfway through; cleanup and rollback behavior.
* **Callers & consumers**: Check other call sites of modified functions to ensure no regression.

### Phase 5: Strengthen the Proof & Repair Gaps
When evidence is missing or a counterexample exposes a gap:
1. Write or strengthen the smallest useful behavioral test at the highest meaningful public seam.
2. Run the focused test.
3. If it fails, fix the implementation defect within the issue's scope.
4. Rerun the test until green.

### Phase 6: Sensitivity Checks
For 1–3 central regression claims, verify that the test is truly sensitive to regressions:
1. Temporarily introduce a controlled fault (e.g. comment out the deduplication guard or status update).
2. Run the test and confirm it turns **RED**.
3. Restore the implementation and confirm it returns **GREEN**.
4. *Strict rule*: Sensitivity checks must be temporary. Never leave intentional faults or disabled guards in the code.

### Phase 7: Verify the Whole Change
Ensure proof fixes did not introduce regressions:
1. Run focused tests for the issue.
2. Run static type checking and relevant linters.
3. Run the full test suite (or project-wide automated test command).
4. Inspect `git diff` to ensure no temporary test scaffolding or unintended changes remain.
5. Rebuild the final Acceptance Matrix.

### Phase 8: Declare the Result
Report the conclusion with complete objectivity.

#### If PROVEN:
Use only when every material requirement has credible evidence, all counterexamples are addressed, and full verification passes.

```markdown
# PROVEN — Issue #<number>

**Requirements:** <N>/<N> demonstrated
**Counterexamples tested:** <count> (<fixed_count> resolved)
**Requirements relying on inspection alone:** 0

### Acceptance Matrix
| Requirement | Evidence | Status |
|---|---|---|
| R1: <claim> | <test or invariant> | Proven |
| R2: <claim> | <test or invariant> | Proven |

### Verification
- Focused tests: <count> passed
- Typecheck: passed
- Full suite: <count> passed

### Changes Made During Proof
- Added regression test for <case> (`<file>`)
- Fixed <defect found> in `<file>`
```

#### If NOT PROVEN:
Use whenever any material requirement lacks sufficient evidence, an unhandled counterexample remains, or verification fails.

```markdown
# NOT PROVEN — Issue #<number>

**Requirements:** <proven_count>/<total_count> demonstrated

### Unresolved Gaps
- **Requirement R<X>**: <description of what is unproven or failing>
  - *Evidence / Counterexample*: <concrete scenario or race condition>
  - *Why unresolved*: <architectural limitation outside issue scope, external dependency, etc.>

### Acceptance Matrix
| Requirement | Evidence | Status |
|---|---|---|
| R1: <claim> | <test or invariant> | Proven |
| R2: <claim> | Insufficient concurrency protection | Not Proven |

### Verification Status
- Focused tests: <result>
- Full suite: <result>
```

---

## Detailed References

For deep catalogs and patterns, refer to:
* [Counterexample Patterns](./references/counterexample-patterns.md): Concrete domain boundary and failure hunting techniques.
* [Testing Heuristics & Anti-Patterns](./references/testing-heuristics.md): Common test illusions, mock traps, and sensitivity verification.
