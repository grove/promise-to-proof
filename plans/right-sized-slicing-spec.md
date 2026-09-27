# Proposal: Fewer, right-sized child issues

**Status:** Proposed specification, version 1.0 — not an approved acceptance contract.  
**Date:** 27 September 2026.  
**Suggested repository location:** `specs/right-sized-slicing.md`.  
**Inspected baseline:** `grove/promise-to-proof` at commit `18bab308a297b9af978d6dcf3e1107cd5eaedce5`.

## 1. Objective

Improve `slice-contract` so that its first complete proposal contains the **fewest child work items that remain coherent and reasonably manageable through a full `deliver-issue` cycle**.

Every additional child must earn the overhead of a separate delivery cycle. Prefer combining related work; split only when the combined work would otherwise be materially harder to implement, review, or prove, or would violate a binding delivery constraint.

This applies to canonical local child work items, not just their optional GitHub mirrors. Hiding several local delivery units behind one tracker issue does not achieve the goal.

“First complete proposal” means that inspection and boundary refinement happen within the original slicing invocation, before presenting a finished breakdown or creating child files. It does not mean using the first grouping the model considers, guaranteeing successful delivery, or forbidding later changes when new evidence appears.

### Decision priority

Preserve the complete agreement and existing safety rules first. Require manageable, coherent delivery units second. Among decompositions meeting those conditions, prefer fewer children. Where child counts are equal, prefer less duplicated context, verification setup, and coordination.

If the parent itself is manageable as one coherent work item, return `NO SPLIT`. Do not create a single child that simply restates the parent.

The goal is the smallest defensible decomposition, not a claim to have found a mathematically optimal partition.

## 2. Existing workflow boundaries

The current slicer already favors few useful, outcome-oriented children and inspects implementation, tests, and history. This proposal makes its sizing judgment more explicit rather than replacing decomposition. [S1]

`create-parent-issue` remains an optional source-publication operation. It does not size children. `plan-acceptance` remains the sole author of parent and child acceptance contracts and revisions. [S2][S3]

A delivery cycle means the existing work-item workflow: implementation, candidate capture, independent review, independent proof, durable evidence, and any repair/recheck permitted by the protocol. It does **not** mean one agent context. Publication and merge readiness remain separate and separately authorized. No verification requirement or repair limit changes. [S4][S5]

A child need not be independently releasable. Genuine prerequisites and approved grouped delivery remain supported. However, grouping children onto an integration branch must not excuse an oversized child or incomplete child verification. [S3]

## 3. Required sizing behavior

The R identifiers below identify proposed source requirements. `plan-acceptance` will normalize this specification into the canonical acceptance contract; this document does not create or approve that contract.

### R1. Inspect enough context to make a grounded judgment

Read the source, parent agreement when present, existing decomposition, and relevant repository instructions. Preserve the existing `NO SPLIT` path for a clearly small source without manufacturing a contract; a complete decomposition still requires an established parent agreement. Inspect the implementation paths, interfaces, state changes, tests, and evidence facilities that materially affect candidate boundaries.

Use relevant, retrievable delivery history when available: for example, a linked earlier work item with similar implementation or proof difficulties. Distinguish observed facts from an interpretation of why a delivery succeeded or failed. A repair or failed test alone is not evidence that the child was too large.

Do not scan unrelated history, invent past experience, or require an experience-recording feature. When history is absent, use current evidence and identify material assumptions. Inspection should stop when additional investigation is unlikely to change the boundaries; sizing must not turn into implementation or an exhaustive architecture study.

### R2. Start with the broadest plausible grouping

First consider whether the parent can remain unsliced. Otherwise propose a small number of broad, coherent contributions rather than generating a ticket for each requirement and merging them afterward.

A coherent contribution can contain several closely related behaviors. Validation, persistence, authorization, failure handling, tests, and necessary documentation may all belong to the same outcome.

Separate requirement IDs, files, software layers, actors, or test cases are not reasons to create separate children. Neither a suggested ticket list nor the number of available agents establishes the appropriate count. An existing approved plan is handled under R8, not silently replaced.

### R3. Assess the full delivery burden

For each candidate child, consider these questions together:

| Dimension | Question |
|---|---|
| Outcome | Does this form one understandable contribution rather than a bundle of unrelated changes? |
| Implementation context | Can the relevant mechanisms and interactions be understood and changed as one bounded piece of work? |
| Uncertainty | Are remaining unknowns routine implementation choices, or decisions likely to change the scope or approach substantially? |
| Prerequisites and compatibility | Are dependencies explicit, and are transition states and inherited constraints manageable? |
| Review and proof | Can independent reviewers and verifiers establish the complete child outcome using a bounded, credible evidence approach? |
| Added-cycle overhead | Would separating this work duplicate substantial context, setup, review, proof, or handoff work? |

Support consequential judgments with inspected facts. “Large,” “complex,” “agent-sized,” or “fits one session” alone are not sufficient explanations.

Do not turn these dimensions into scores, story points, fixed time budgets, requirement limits, file-count thresholds, or model-token arithmetic. A broad mechanical edit can be easier than a small change to a concurrency invariant. Reading the parent to recover inherited constraints is required context, not itself evidence of oversizing.

### R4. Challenge every plausible additional boundary with a merge test

Before presenting the breakdown, examine related children and plausible groups of children—not only neighbors in the display order. Prioritize groups sharing a production path, state transition, evidence setup, or tightly coupled prerequisite.

Ask:

> Could these be delivered together without materially compromising coherence, manageability, verification, or a binding constraint?

When the answer is yes, combine them. The fact that two behaviors can be named or tested separately does not by itself justify paying for two delivery cycles.

When retaining a boundary, name the concrete reason and supporting context: for example, substantially different recovery mechanisms, a necessary compatibility transition, or an independently bounded verification problem that would otherwise overload the combined work.

A small child is permitted when its separation is necessary. An evidenced enabling step or required migration stage must not be merged merely to improve the count. Conversely, generic statements about parallelism, cleanliness, or possible independent value are not enough to create another child.

### R5. Split only to solve an identified delivery problem

When a candidate is too broad, identify the source of the burden before dividing it. State what becomes simpler to implement, review, or prove after the split, and why the remaining children are still complete contributions.

Choose the least additional fragmentation that resolves the problem. Do not split all remaining candidates merely because one needed division. Reassess the resulting children and their plausible merges before finalizing.

Keep ordinary tests, failure handling, security boundaries, compatibility behavior, and necessary documentation with the behavior they establish. Preserve justified preparatory work and migration exceptions under the existing protocol. Do not create a standalone proof or integration ticket for ordinary workflow bookkeeping; assign actual integration work where it belongs.

If a difficult outcome has no defensible split, do not invent layer tickets or label it manageable without evidence. Identify the missing decision or concrete feasibility question through the existing draft/blocker handoff. A normal implementation unknown or missing test harness is not automatically such a blocker.

### R6. Finish the sizing judgment before creating children

Before the first complete proposal, establish that every child has a credible full-delivery approach, every retained boundary has a material reason, no obvious feasible merge remains, and all parent promises and shared constraints are allocated.

This is reasoning inside `slice-contract`, not another slash command, mandatory audit, delegated review, or user-operated iteration loop. Evaluate plausible alternatives without enumerating every possible partition. Stop when the remaining decisions are defensible or a material blocker is identified.

Outcome-defining ambiguity must not be concealed by choosing either one oversized child or many speculative children. Route changed promises and unresolved agreement decisions through `plan-acceptance` as today. A clear outcome with missing evidence tooling normally keeps that tooling in the necessary implementation work. [S1]

### R7. Save a short, evidence-backed sizing rationale

Add a `## Sizing rationale` section to the existing `.p2p/work/<parent>/slicing.md`. Keep it outside the `## Approved delivery plan` section, preferably before it, without altering the approved section’s exact bytes or the machine-consumed routing format. The current protocol binds that approved section by its exact bytes. [S3]

The rationale should explain why an unsliced parent is or is not appropriate, why each child is manageable, why plausible merges were rejected, and which material assumptions remain. Use concise decision summaries and source references, not a transcript of internal deliberation.

For example:

```markdown
## Sizing rationale

Decision: Keep S1 and S2 separate.
Unsplit alternative: Would combine server-side retry persistence with a new
browser offline queue, each requiring different recovery-state verification.

| Slice | Why manageable | Why keep this boundary? |
|---|---|---|
| S1 | Existing upload path; bounded persistence and restart checks. | Server recovery can be established before the new browser state machine. |
| S2 | One browser retry flow using S1's confirmed behavior. | Combining both recovery mechanisms would broaden implementation and proof substantially. |

Evidence: <inspected implementation, checks, and applicable history references>.
Assumptions: <material assumptions, or none identified>.
```

Reuse the existing outcome, contribution, dependency, and evidence descriptions instead of copying a second contract into this section. For `NO SPLIT`, a short explanation in the normal result or existing report is sufficient; do not create a work item solely for the rationale.

### R8. Preserve authority, identity, and downstream requirements

Apply the new sizing behavior to new decompositions and explicitly requested reconsideration. Do not invalidate or automatically regroup an approved plan because it lacks a sizing rationale. Do not create replacement issues, rewrite child contracts, or close existing children merely to reduce the count.

For authorized re-slicing, preserve completed work, human edits, identities, history, and traceable old-to-new contributions. Preview material allocation changes under existing approval rules. Changes to child promises return to `plan-acceptance`; regrouping unchanged promises does not by itself revise the parent's meaning. [S3]

Preserve local-first operation, draft-only behavior, publication authority, readiness rules, prerequisite checks, and full parent verification on one assembled candidate. Historical child proofs must not become a parent verdict. Existing result statuses remain unchanged. [S1][S3]

The resulting flow remains parent acceptance planning → slicing and existing approval/storage → child acceptance planning → child delivery. `deliver-issue` may invoke missing child planning under its existing rules; sizing does not supply approval or bypass it. [S4]

## 4. Example: let the codebase determine the boundary

Consider retry-safe uploads. A preliminary task list separates database changes, API changes, authorization, browser changes, tests, and documentation.

If the repository already has the required storage and authorization mechanisms, and browser work is a thin call into the same existing flow, the entire change may be one manageable outcome. The preferred result is `NO SPLIT`, not six children or a single wrapper child.

If inspection instead reveals substantial server-side persistence/recovery work and a new browser offline queue with its own restart and cancellation behavior, separate server and browser contributions may be justified. Each still includes its relevant tests, failures, inherited constraints, and evidence. The browser child has an explicit server prerequisite, and combined interactions remain in parent verification.

These are illustrative alternatives, not fixed expected counts. The difference is the inspected implementation and verification burden—not the number of headings in the specification.

## 5. Implementation scope

| Location | Required change |
|---|---|
| `skills/productivity/slice-contract/SKILL.md` | Replace the vague sizing preference with the explicit minimum-child objective and R1–R8 behavior. Perform sizing before child creation. |
| `skills/productivity/slice-contract/references/sizing.md` — new | Supply a compact decision guide and contrasting examples. Keep the core rules in `SKILL.md`; bundle the reference for standalone installation. |
| `docs/acceptance-contract-protocol.md` | Add the sizing invariant to parent/child rules without changing ownership, routing schema, status values, or approval semantics. Keep distributed protocol copies consistent. |
| `checks/slice-contract-scenarios.md` | Add the behavioral cases below and retain existing coverage. Reuse current fixture conventions. |
| `checks/slice-contract-sizing-validation.md` — new | Record actual baseline/candidate observations, retained evidence, failures, and unexecuted checks. Do not present planned tests as results. |
| `docs/how-to.md` and `docs/faq.md` | Explain the fewer-children preference, `NO SPLIT`, and a contrasting sizing example. Adjust the README only where necessary for consistency. |

No delivery-controller changes, numerical size policy, new scheduler, learning service, issue type, mandatory audit, or new user configuration is required. `create-parent-issue` is unchanged. Implementing `audit-slicing` is outside this proposal.

## 6. Required behavioral scenarios

Extend the existing human-runnable checks. Those checks already require installed-skill invocations, hidden evaluator expectations, captured actions/artifacts, and honest distinction between simulations and live behavior. [S6]

The scenario IDs below follow the inspected suite's T21. Renumber only if intervening repository changes require it.

| Case | Fixture and required observation | Requirements |
|---|---|---|
| T22: Manageable parent | One coherent outcome with several requirements. First result is `NO SPLIT`, with no wrapper child. | R2, R3, R6 |
| T23: Artificial micro-tickets | One small behavior proposed as field/API/validation/test/documentation tickets. Combine the work before the first complete proposal; preserve every obligation. | R2, R4–R6 |
| T24: Hidden mini-epic | A short proposal combines substantial mechanisms with distinct state and recovery obligations. Identify the concrete overload and form complete, manageable contributions rather than accepting the short description as small. | R1, R3, R5 |
| T25: Good boundaries | A draft already has necessary, manageable contributions and evidenced reasons not to combine them. Retain useful boundaries rather than reducing count at any cost or fragmenting further. | R3–R5 |
| T26: Size proxies mislead | Paired cases: a broad mechanical change across many files; a small diff with difficult concurrency behavior. Base decisions on mechanisms and verification, not counts. | R1, R3 |
| T27: Merge beyond neighbors | Related fragments are separated in display order; a plausible group shares one outcome and evidence setup. Consolidate that group without relying on adjacency. | R4, R6 |
| T28: Necessary small stage | A compatibility migration requires an evidenced small preparatory stage. Retain it when combining would violate the transition constraint. | R4, R5, R8 |
| T29: Grouped and dependent delivery | Children need prerequisites or an approved integration destination. Neither force independent release nor use grouping to waive child completeness or parent proof. | R3, R8 |
| T30: Missing knowledge | Contrast a missing test harness for a clear outcome with an unresolved product decision affecting scope. Assign ordinary evidence work in the first; expose the blocking decision in the second. | R1, R5, R6 |
| T31: History used honestly | Supply relevant prior delivery evidence, then an absent-history variant and a prior unrelated failure. Use applicable observations without inventing history, causation, or a mandatory history dependency. | R1, R3 |
| T32: Safe rerun | An approved legacy plan lacks sizing notes and contains started work. An unchanged rerun preserves it; explicit re-slicing previews changes and preserves history and human edits. Draft-only runs create no children. | R6–R8 |
| T33: Wording does not set size | Reorder and paraphrase the same obligations, or group them under different headings. Produce materially equivalent boundaries unless real constraints change. | R2–R6 |

No scenario passes merely because it contains sizing vocabulary. Evaluate outcomes, scope coverage, evidence references, actual artifacts, and reasons for retained boundaries. Except where a fixture genuinely warrants `NO SPLIT`, do not bake an arbitrary target child count into the expectation.

## 7. Validation and acceptance

### First-proposal comparison

Run the baseline and revised installed skill against identical disposable fixtures, with the same available tools, permissions, model configuration, and starting artifacts. Capture the first complete result before any corrective feedback. Keep evaluator expectations and held-out cases outside the slicer's input.

Execute all new cases. Repeat the central under-slicing and over-slicing cases in at least three fresh contexts per version to expose variability. This repetition is an evaluation procedure, not a runtime workflow or ticket-count rule.

Use mechanical checks for preserved scope, links, unchanged protected content, and permitted writes where practical. Have an evaluator other than the slicing invocation assess whether reasons are supported and whether a credible lower-count alternative was missed. Do not demand identical wording or a unique decomposition.

Record selected children, unnecessary boundaries, oversized contributions, lost obligations, first-proposal corrections, and actual tool effects. Compare the complete decomposition, including enabling or integration work; moving work off the child list is not a reduction.

### Delivery reality check

Exercise at least one representative parent through both baseline and revised delivery paths, and a second, more demanding parent through the revised path. Use fresh equivalent checkouts, establish required approvals, deliver all selected children through the real supported workflow, and verify the assembled parent. An unsliced result is delivered directly as the parent.

Retain completion/blocker outcomes, repair work, re-slicing, human intervention, and available elapsed-time and usage evidence, including planning overhead. Distinguish sizing-related problems from host, permission, or unrelated defects. Mark unavailable cost data unknown. Never treat fewer planned tickets alone as proof of faster or cheaper delivery.

### Acceptance conditions

The change is ready when required scenarios and affected regression checks pass, standalone installation includes the sizing guidance, and representative delivery observations support the proposed boundaries without a known unresolved sizing-related failure.

Over-fragmented fixtures must lose avoidable boundaries; genuinely broad fixtures must retain necessary splits. Complete source coverage, inherited constraints, verification, approvals, and preservation rules must survive. Unavailable required executions remain validation gaps rather than passing claims.

The comparison must disclose where the baseline already performs as well, where the revision helps, and where it fails. Claim measured savings only when the paired observations support them. Preserve historical validation records rather than rewriting them as evidence for the new behavior. The existing sampled validation explicitly limits its own conclusions; it does not establish this proposal's improvement. [S7]

## 8. Completion definition

This work delivers improved slicing instructions, installed reference material, aligned documentation, executable scenario fixtures where needed, and retained behavioral validation—not merely a new paragraph saying “make children the right size.”

The intended user experience is unchanged: invoke `slice-contract` once, receive a defensible first proposal with fewer unnecessary children, follow the existing approval and child-planning steps, and deliver those children normally.

**Working rule: Start with less fragmentation. Every extra child needs a concrete reason. Never buy a smaller issue count by making delivery unreliable or weakening the promise.**

## Sources inspected

All references below are pinned to the inspected baseline; they describe existing behavior, not implementation or approval of this proposal.

- [S1: `slice-contract` instructions](https://github.com/grove/promise-to-proof/blob/18bab308a297b9af978d6dcf3e1107cd5eaedce5/skills/productivity/slice-contract/SKILL.md).
- [S2: `create-parent-issue` instructions](https://github.com/grove/promise-to-proof/blob/18bab308a297b9af978d6dcf3e1107cd5eaedce5/skills/productivity/create-parent-issue/SKILL.md).
- [S3: Acceptance contract protocol, parent/child contracts and epic delivery plans](https://github.com/grove/promise-to-proof/blob/18bab308a297b9af978d6dcf3e1107cd5eaedce5/docs/acceptance-contract-protocol.md#parent-and-child-contracts).
- [S4: `deliver-issue` instructions, work-item and agreement handling](https://github.com/grove/promise-to-proof/blob/18bab308a297b9af978d6dcf3e1107cd5eaedce5/skills/productivity/deliver-issue/SKILL.md).
- [S5: `deliver-issue` review, proof, recovery, and authority](https://github.com/grove/promise-to-proof/blob/18bab308a297b9af978d6dcf3e1107cd5eaedce5/skills/productivity/deliver-issue/SKILL.md#review-prove-and-recover).
- [S6: Slice-contract scenario suite](https://github.com/grove/promise-to-proof/blob/18bab308a297b9af978d6dcf3e1107cd5eaedce5/checks/slice-contract-scenarios.md).
- [S7: Historical sampled slicing validation](https://github.com/grove/promise-to-proof/blob/18bab308a297b9af978d6dcf3e1107cd5eaedce5/checks/slice-contract-validation.md).
