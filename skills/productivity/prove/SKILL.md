---
name: prove
description: Prove that an implemented issue is actually resolved by mapping every material requirement to independent evidence, hunting counterexamples, strengthening tests, fixing discovered gaps, and refusing to declare success while any requirement remains unproven.
disable-model-invocation: true
---

`/prove` is a post-implementation verification skill. It determines whether a
ticket, spec, or agreed conversation has been implemented by checking its promises
against independent, observable evidence. Treat that source and its authorized
amendments as the contract; an acceptance matrix records the contract but does not
replace it.

Unlike a conventional code review, `/prove` does not primarily ask whether the diff looks clean or follows style guidelines. It starts from the desired outcome:

> **What must be true for this issue to be completely resolved, and can we demonstrate that each of those things is true?**

The primary objective is:
> **Every material requirement in the issue contract is supported by credible evidence under the available verification environment, and reasonable attempts to falsify those claims fail.**

The output is never "looks good" or "seems complete." It is strictly **PROVEN** or **NOT PROVEN**, accompanied by concrete evidence.
* **PROVEN**: Every material requirement in the issue contract is supported by credible evidence under the available verification environment, and reasonable attempts to falsify those claims have failed.
* **NOT PROVEN**: One or more material requirements lack direct evidence, an unhandled counterexample remains, or verification fails. (Software correctness in general cannot literally be proven by a handful of tests—`PROVEN` denotes meeting this strict evidentiary standard, not metaphysical certainty.)

---

## Core Principles

1. **Requirements to Evidence, Not Diff to Opinions**: The issue is the contract; the diff is merely one attempt at fulfilling it.
2. **Falsification Over Confirmation**: Actively ask: *"What is the smallest realistic scenario that demonstrates this claim is false?"* Do not just look for passing happy paths.
3. **Evidence Over Confidence Language**: Never use phrases like "looks correct" or "tests appear comprehensive." State demonstrable facts: *"R1 is proven by test X; R2 currently lacks direct evidence."*
4. **Behavioral Completeness Over Test Quantity**: Five meaningful behavioral tests through public seams provide more confidence than fifty shallow unit tests mocking internals.
5. **Independent Oracles**: Assertions must come from domain rules, specs, and issue requirements—not mirrored calculations copied from the production code.
6. **Fix Local Gaps**: When a test or implementation gap within the issue's scope is uncovered, fix it and rerun verification.
7. **Comfortable with NOT PROVEN**: Ending in `NOT PROVEN` is a successful outcome when evidence is missing or a genuine gap remains. Never massage evidence to force a pass.

---

## Non-Goals & Scope Discipline

* **Not a general code review**: Formatting, naming, stylistic preferences, and repository conventions belong in `/code-review`.
* **Not a general simplification pass**: Do not refactor working code because another design looks prettier. Changes must strictly strengthen the proof or fix a demonstrated defect.
* **Not a coverage maximizer**: Never add tests solely to inflate line or branch coverage percentages.
* **Not a replacement for TDD**: TDD governs development; `/prove` audits the finished outcome and retrofits acceptance proof where missing.
* **Not speculative paranoia**: Counterexamples must be rooted in real domain states, actual control flow, public APIs, storage semantics, and concrete caller contracts.
* **Scope boundaries**: Only make issue-local repairs and tests. Do not redesign surrounding architecture or expand feature scope. Report larger defects in the final assessment.

For a report-only or read-only request, inspect and run safe diagnostics within
that scope. Report needed repairs instead of editing files or injecting faults.

---

## The Proof Model

Use the issue's existing **Acceptance Matrix** when available, or create one
from the issue contract:

| Requirement | Evidence | Status |
|---|---|---|
| R1: Retrying a failed upload makes the original file retrievable | `retry-upload.test.ts :: retrieves file after retry`; retrieved bytes equal the original fixture | proven |
| R2: Retry does not create duplicates | DB uniqueness constraint + integration test asserting one upload for the operation | proven |
| R3: Metadata survives retry | No direct assertion | not proven |
| R4: Retry works after page refresh | Session rehydration integration test asserting file retrieval after retry | proven |

Each material requirement must resolve to:
* `proven`: Direct, credible evidence confirms the required behavior holds under verification.
* `not proven`: Requirement may be implemented, but available evidence is weak, absent, unrun, or inconclusive.
* `disproven`: A concrete counterexample or test demonstrates the requirement is violated.

Convert incoming `planned` rows to one of these verdicts after verification.
An unavailable tool or environment leaves a row `not proven`, not `disproven`.
Record the verified commit or worktree state and relevant environment with the
results. Reassess affected verdicts when requirements, evidence, or implementation
change. Use uppercase `PROVEN` or `NOT PROVEN` only for the overall conclusion.

---

## Evidence Evaluation

**Prefer the strongest evidence appropriate to the claim** rather than adhering to a rigid hierarchy. Different claims demand different evidentiary foundations:

* **Hard invariants & data integrity** (e.g. uniqueness, non-nullability, state transitions): Enforced most reliably by database constraints, type systems, schema validations, or state machine guards—often far stronger and more durable than an integration test.
* **End-to-end workflows & behavioral semantics**: Best demonstrated by behavioral automated tests through public seams.
* **Operational or performance bounds**: Best proven with deterministic benchmarks, verification scripts, or CLI checks.
* **Weakest evidence**: Reasoned code inspection alone is rarely sufficient for central behavioral claims. Explicitly flag any requirement that relies solely on inspection.

---

## Workflow: The 8-Phase Proof Loop

```text
1. Contract & Parent ──> 2. Map Evidence ──> 3. Audit Tests ──> 4. Hunt Counterexamples
                                                                             │
8. Declare & Close Loop <── 7. Verify Whole <── 6. Sensitivity <── 5. Strengthen & Fix
```

### Phase 1: Establish the Contract & Inherit Parent Spec
Read the source contract before deeply inspecting the implementation diff.
1. **Locate the contract**: Use the supplied ticket, spec, or agreed conversation. For an issue, inspect user input (`#123`, URL), branch/commit metadata, PR description, or issue tracker. If no requirement source can be established, stop and ask.
2. **Follow parent/spec links**:
   - Check the issue for parent references (e.g. `Parent: #100`, `Part of #100`, links to a spec, or epic).
   - If a parent exists, read the parent issue/spec to understand the overarching system guarantees.
   - **Inherit selectively**: Inherit only those parent requirements, constraints, and invariants directly relevant to this child ticket. Do not import the parent's entire scope.
3. **Extract material requirements**:
   - Explicit acceptance criteria, requested user-visible behaviors, and inherited parent constraints.
   - Required state transitions and negative requirements ("must NOT duplicate").
   - Data preservation, error handling, and domain invariants implied by the outcome.
4. **Reconcile the acceptance matrix**: Read any matrix embedded in or linked
   from the issue, or supplied with the task. Preserve its requirement IDs,
   promised results, boundaries, and open questions. If none exists, draft one
   (`R1, R2, ...`). Independently compare the matrix with the issue and applicable
   parent constraints; add omitted material requirements with unused IDs.
   - Record changed or dropped promises with their original IDs, source, and
     explicit authorization for any scope change. A PR's implementation or
     weaker tests do not authorize narrowing the contract. Keep unsupported
     changes visible as unresolved gaps and return **NOT PROVEN** while they
     remain unresolved.
   - Resolve conflicts against the source contract and authorized amendments.
     Report ambiguous product decisions instead of choosing the easiest reading.
     Evidence mappings are proposals to evaluate; earlier statuses are not
     evidence for the current implementation.

### Phase 2: Map Existing Evidence
Map existing code and tests to each requirement:
* Inspect tests, runtime validations, database schemas, and type constraints.
* Read the actual assertions and invariants—confirm they establish the specific behavioral claim rather than merely executing the code path.
* For each row, identify the required observable result and the assertion or
  enforced condition that establishes it. Record replacement evidence and why it
  still establishes the same promise. A passing suite does not establish a row
  whose required result is never checked.

### Phase 3: Audit Test Quality
Ensure tests serving as evidence are credible:
* **Behavioral & Seam-focused**: Verifies observable behavior at public seams, not private implementation details.
* **Independent Oracles**: Expected values derive from domain rules and specs, not copied production code logic.
* **Sensitive & Durable**: Fails when the requirement is broken; does not break on internal refactoring.
* *Reference*: See [Testing Heuristics & Anti-Patterns](./references/testing-heuristics.md) for mock illusions, tautologies, and common traps.

### Phase 4: Hunt Concrete Counterexamples
Attack claims with failure scenarios grounded in the domain and codebase:
* Explore adjacent lifecycle states, semantic boundaries (`0 / 1 / N`, tenant/auth boundaries), persistence/restart transitions, retries & idempotency, check-then-write race windows, and caller contracts.
* Trace the requested workflow from trigger through completion. Could every row
  pass while the intended user or operational outcome still fails? Check how the
  steps connect and what the user can observe at completion. Strengthen evidence
  or add a missing obligation where the contract supports it.
* *Reference*: See [Counterexample Hunting Patterns](./references/counterexample-patterns.md) for domain-specific attack vectors.

### Phase 5: Strengthen the Proof & Repair Gaps
When evidence is missing or a counterexample exposes a gap:
1. Strengthen the smallest appropriate evidence. Use a behavioral test at the highest meaningful seam for behavioral gaps, or an enforced invariant or verification command for claims those checks establish.
2. Run the focused check. If it demonstrates a violation, fix the issue-scoped defect and rerun. If it passes but sensitivity is uncertain, consider a Phase 6 sensitivity check. Report unavailable verification as an evidence gap.
3. Keep changes tightly focused on the issue contract.

### Phase 6: Sensitivity Checks (Selective)
When cheap, safe, and materially confidence-improving (such as for critical bug fixes, deduplication guards, or idempotency checks), confirm the test is sensitive to regressions:
1. Temporarily introduce a controlled fault (e.g. comment out the guard or inversion).
2. Run the test and confirm it turns **RED**.
3. Restore the implementation and confirm it returns **GREEN**.
4. Clean diff check: Never leave intentional faults or disabled guards in the code.
*Note: Skip fault injection when it is costly, risky, or provides negligible confidence gain.*

### Phase 7: Verify the Whole Change
Ensure proof fixes did not introduce regressions:
1. Check the PR status for the exact commit under review. If all required checks are green and the working tree is clean, treat those checks as project-wide verification. Do not rerun tests, typechecks, or linters locally just to duplicate green CI.
2. Run focused tests, static checks, or the full suite only when the PR checks are missing, stale, incomplete for the affected paths, or no longer cover the final diff because `/prove` changed files.
3. Inspect `git diff` to ensure no temporary test scaffolding remains.
4. Update the reconciled Acceptance Matrix with current evidence and verdicts.
   Account for every original ID and added requirement. Retain the disposition
   of changed or dropped promises, including their source and authorization;
   unresolved requirements and product decisions prevent **PROVEN**.

### Phase 8: Declare the Result & Close the Review Loop
Report the conclusion with complete objectivity.
Include the intended outcome, evidence of workflow completion, and reconciliation
with the ticket's matrix. Report added, changed, or dropped requirements and
replaced evidence by ID, or state that none changed. Keep unmet requirements and
missing evidence visible in the final matrix and unresolved gaps.

#### Closing the Review / Prove Loop
If `/prove` added tests, changed code, or fixed defects, **it modified the diff and may have invalidated a prior code review**.
Whenever files are changed during `/prove`, the final output MUST conclude with an explicit directive:
> **Diff modified during proof.** Repeat the repository's code review against the actual target base. Use `/code-review <base>` if installed, or the repository's equivalent review process.

This handoff does not invoke another skill, publish a result, or merge the PR.
An acceptance verdict and a code review assess different parts of PR quality.

#### Reporting Format

##### If PROVEN:
```markdown
# PROVEN — <ticket, spec, or agreed source>

> PROVEN: Every material requirement in the issue contract is supported by credible evidence under the available verification environment.

**Requirements:** <N>/<N> demonstrated (including inherited parent constraints)
**Counterexamples tested:** <count> (<fixed_count> resolved)
**Requirements relying on inspection alone:** 0

**Outcome:** <intended result and evidence of workflow completion>
**Contract reconciliation:** <added requirements, authorized scope changes, and replaced evidence by ID, or "None">
**Verification context:** <commit or worktree state, relevant environment>

### Acceptance Matrix
| Requirement | Evidence | Status |
|---|---|---|
| R1: <claim> | <test or invariant and observed result> | proven |
| R2: <inherited from Parent #X> | <test or invariant and observed result> | proven |

### Verification
- Focused tests: <count> passed
- Typecheck: passed
- Project-wide verification: <result>

### Changes Made During Proof (if any)
- Added regression test for <case> (`<file>`)
- Fixed <defect found> in `<file>`

> **Diff modified during proof** (if changes were made): Repeat code review against the actual target base using `/code-review <base>` if installed, or the repository's equivalent review process.
```

##### If NOT PROVEN:
```markdown
# NOT PROVEN — <ticket, spec, or agreed source>

**Requirements:** <proven_count>/<total_count> demonstrated

**Outcome:** <intended result and what prevents establishing it>
**Contract reconciliation:** <added, changed, or dropped requirements and replaced evidence by ID, with sources and authorization where applicable, or "None">
**Verification context:** <commit or worktree state, relevant environment>

### Unresolved Gaps
- **Requirement R<X>**: <description of what is unproven or failing>
  - *Evidence / Counterexample*: <concrete scenario or race condition>
  - *Why unresolved*: <architectural limitation outside issue scope, external dependency, etc.>

### Acceptance Matrix
| Requirement | Evidence | Status |
|---|---|---|
| R1: <claim> | <test or invariant and observed result> | proven |
| R2: <claim> | Insufficient concurrency evidence | not proven |

### Verification Status
- Focused tests: <result>
- Project-wide verification: <result>

### Changes Made During Proof (if any)
- Added regression test for <case> (`<file>`)
- Fixed <defect found> in `<file>`

> **Diff modified during proof** (if changes were made): Repeat code review against the actual target base using `/code-review <base>` if installed, or the repository's equivalent review process.
```

---

## Detailed References

* [Counterexample Patterns](./references/counterexample-patterns.md): Domain boundary, state, idempotency, and failure hunting techniques.
* [Testing Heuristics & Anti-Patterns](./references/testing-heuristics.md): Test illusions, tautological checks, and sensitivity verification protocol.
