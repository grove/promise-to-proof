# Proposal: Choose the delivery shape and minimize child issues

**Status:** Proposed specification, version 2.0 — not an approved acceptance contract.  
**Date:** 27 September 2026.  
**Repository location:** Replace `plans/right-sized-slicing-spec.md`.  
**Supersedes:** Version 1.0, “Fewer, right-sized child issues,” in that same file.  
**Inspected baseline:** `grove/promise-to-proof` at commit `bac5aa15345514416f3f7244f48c88c4edd7daa1`.  
**Execution status:** Specification only. Implementation and behavioral validation have not been performed.

## 1. Objective

Make Promise to Proof recommend the right delivery shape without requiring the developer to decide whether slicing is necessary:

> **Deliver the work directly when it is clearly manageable. Otherwise inspect it through `slice-contract`, and create the fewest children that remain coherent and realistically deliverable.**

This is one feature with two decisions. `plan-acceptance` makes a lightweight routing judgment using the contract and context it has inspected. `slice-contract`, only when warranted, makes the deeper decision about whether and how to split.

Every additional child must earn the overhead of a separate delivery cycle. Prefer combining related work; split only when the combined work would be materially harder to implement, review, or prove, or would violate a binding constraint. This applies to canonical local child work items as well as optional GitHub issues. Hiding multiple local delivery units behind one tracker issue is not a reduction.

### Decision priority

Preserve the full agreement and safety rules first. Require coherent, manageable delivery units second. Among alternatives meeting those conditions, prefer fewer children; at equal child count, prefer less duplicated context, verification setup, and coordination.

If the whole work item is manageable, deliver it directly. `slice-contract` may return `NO SPLIT`; it must not create one child that merely restates the parent. Neither stage must claim a mathematically optimal partition or predict successful delivery with certainty.

“First complete proposal” means the slicer inspects and refines boundaries within the original invocation, before presenting the finished breakdown or creating children. It does not mean accepting the first grouping considered, banning later evidence-based changes, or requiring another audit or user-operated correction loop.

## 2. Workflow and ownership

The normal flow is:

```text
create-parent-issue (optional source publication)
    → plan-acceptance
        → clearly manageable: direct delivery after required approval/gates
        → too broad or materially uncertain: slice-contract
            → NO SPLIT: direct delivery after required approval/gates
            → decomposition: approve the necessary planning decisions,
               establish child contracts, and deliver ready children
```

These arrows are handoffs, not automatic calls. Stage skills do not invoke each other merely because the next step appears in a report. An already authorized enclosing `deliver-issue` workflow retains its existing orchestration responsibilities.

| Owner | Responsibility in this feature | Not its responsibility |
|---|---|---|
| `create-parent-issue` | Preserve the source and give the existing `plan-acceptance` handoff. | Decide child count, author contracts, or determine implementation readiness. |
| `plan-acceptance` | Establish the contract, assess whether direct delivery is clearly manageable, and recommend the next action. | Produce candidate children, a dependency graph, or a detailed decomposition. |
| `slice-contract` | Inspect sizing in depth; return `NO SPLIT` or the smallest defensible decomposition. | Author acceptance-contract revisions or waive approvals. |
| `deliver-issue` | Deliver one ready work item and retain its guard against oversized or unresolved work. | Automatically split a parent or recursively restart itself. |

At the inspected baseline, `plan-acceptance` recommends delivery for an approved issue handoff, or implementation for a local contract, without an explicit delivery-shape decision. Its contract template also contains an unconditional implementation handoff. Both surfaces must be aligned with the proposed routing behavior. [S8]

The existing slicer already prefers few useful, outcome-oriented children. Existing `create-parent-issue`, contract ownership, local-first storage, and delivery authority rules remain the foundation of this change. [S1] [S2] [S3]

A **delivery cycle** is the existing work-item workflow: implementation, candidate capture, independent review, independent proof, durable evidence, and any permitted repair/recheck. It is not one agent context, a guaranteed uninterrupted run, or a promise to finish without a blocker. Publication and merge readiness remain separate. Verification obligations and the repair limit do not change. [S4] [S5]

A **delivery-shape recommendation** chooses direct delivery versus sizing inspection. It is not the **approved delivery plan** that chooses final or integration-branch destinations. Keep these concepts, records, and authority separate. A child may have real prerequisites or an approved grouped destination; neither excuses an oversized child or incomplete verification. [S3]

The R identifiers below are proposed source requirements, not approved acceptance rows. R1–R8 retain their version 1.0 identities; R9–R12 add routing and handoff behavior. They appear in workflow order rather than numeric order.

## 3. Choose whether to slice

### R9. Perform a lightweight delivery-shape assessment

After forming the complete proposed contract and before issuing its next-step recommendation, `plan-acceptance` asks:

> Can this complete work item reasonably be implemented, independently reviewed, and proven as one bounded delivery unit?

Reuse the source, relevant implementation, interfaces, evidence plans, constraints, and applicable history already inspected during acceptance planning. Do only additional focused inspection that could change the route. Do not run delivery, probe host isolation, design child boundaries, or perform an exhaustive sizing exercise here.

| Assessment | Recommendation | Explanation required |
|---|---|---|
| Clearly coherent and manageable | Direct delivery | Name the bounded outcome and implementation/evidence context that make a single delivery plausible. |
| Clearly too broad | Sizing inspection | Name the substantial mechanisms, interactions, uncertainty, or verification burden that make direct delivery unsuitable. |
| Materially uncertain whether it fits | Sizing inspection | Name the specific sizing question deeper inspection must resolve. |

Recommend direct delivery only when the inspected evidence supports it. However, ordinary implementation unknowns, several acceptance rows, or the absence of historical measurements are not sufficient reasons to send every work item through slicing. An uncertainty is material here when resolving it could reasonably change the direct-versus-sliced decision.

Use the dimensions in R3 without turning them into scores, thresholds, or time estimates. Several closely related behaviors may form one outcome. Conversely, a short contract can conceal substantial recovery or concurrency work.

Keep outcome decisions separate from sizing uncertainty. An unresolved promise must be resolved through acceptance planning; slicing is not a way to guess it. Missing permissions, unavailable hosts, and unmet prerequisites are readiness or execution blockers, not evidence that the work needs more children.

### R10. Give one clear next action while preserving gates

For an ordinary unsliced work item, present the recommendation, a short grounded reason, and the exact next command once its preconditions are satisfied.

For direct delivery, the normal standalone handoff becomes `/deliver-issue work/<slug>.md`. A published issue reference may be used when the existing issue-only handoff is actually recoverable. An explicitly chosen manual implementation/review/proof workflow remains supported; this change does not remove `/implement-contract`. [S4] [S8]

For sizing inspection, give `/slice-contract work/<slug>.md`. Do not present direct delivery as an equally recommended alternative for a work item already judged too broad or materially uncertain. The slicer remains free to return `NO SPLIT` after deeper inspection.

A recommendation is not approval, a readiness label, execution authority, or a verification result. If contract storage, required approval, or an outcome decision is pending, name that as the immediate next action and make the subsequent command conditional. Preserve existing handling of evidence-plan gaps: a missing credible seam or oracle remains visible, while merely needing to implement a known harness does not itself require another ticket. Preliminary sizing may proceed only where current authority and the state of the agreement allow it.

Update both the final `Next steps:` guidance and the contract template's generic implementation-handoff prose. The template must no longer unconditionally direct every completed contract to implementation. Keep the selected route outside the acceptance matrix, and do not rewrite an already approved contract just to change routing advice.

For a saved, approved, unblocked contract, example outputs are:

```text
Delivery shape: Direct delivery.
Reason: One bounded update through the existing report-writing path,
with a credible public-interface evidence plan.
Next: /deliver-issue work/save-report.md
```

```text
Delivery shape: Sizing inspection.
Reason: This combines server recovery and a browser offline queue;
their state and proof burden need deeper inspection before delivery.
Next: /slice-contract work/retry-safe-uploads.md
```

When approval is pending, the immediate next action instead identifies the exact proposal needing approval. Do not claim that the displayed later command is already authorized.

### R11. Retain the recommendation without changing the contract

Save a short advisory report at `.p2p/work/<slug>/delivery-shape.md`, using existing filesystem resolution, history-preserving save, and readback conventions. No new helper command, database, configuration, or acceptance state is required.

The report records the work-item path, exact contract revision and hash, relevant binding-input identities, recommendation and reason, inspected context references, material assumptions, applicable earlier slicing result, and next action with outstanding gates. Record code/history references only as needed to support the judgment; this is not a product-candidate snapshot or a second contract.

Keep the report compact. Do not expose internal deliberation, duplicate the acceptance matrix, or calculate a numerical sizing score. An unchanged recommendation on unchanged inputs should reuse the report rather than manufacture history churn. If saving is unavailable, report storage pending and hand off the exact report to the authorized enclosing workflow; do not claim durable storage.

Include the concise recommendation outside the exact contract block when publishing an authorized new standalone planning handoff. Preserve approved contract bytes, existing comments, and publication/readback rules. Do not post an extra tracker comment solely to refresh routine routing advice; a local-only or draft-only invocation remains local. [S9]

Given only the work-item path, a later session can find this report and any applicable `slicing.md`. Check applicability before reuse: a matching revision label alone is insufficient. Changed scope, binding inputs, or consequential implementation facts require reassessment, not blind replay. A recommendation-only change does not revise acceptance promises. Existing candidate, agreement, and proof invalidation rules remain unchanged.

This report is advisory, not a new delivery-admission requirement. Missing or unsaved routing advice is a reporting limitation, not by itself a reason to block otherwise valid delivery; missing required agreement or evidence still blocks under existing rules. Older approved work without the report remains usable, subject to the existing contract and delivery checks.

### R12. Avoid repeated routing, recursive delivery, and accidental re-slicing

**After `NO SPLIT`.** When a canonical work item exists, the slicer saves and rereads its result, exact agreement identity, relevant inspected context, and direct-delivery rationale in the existing `slicing.md`. A fresh planner or delivery session must consider that deeper finding before repeating the same routing judgment. Do not send unchanged work back to slicing solely because an earlier lightweight assessment was uncertain.

`NO SPLIT` does not grant approval or remove unrelated blockers. With an approved, saved contract and no blocking gaps, the slicer's normal handoff becomes `/deliver-issue work/<slug>.md`. Without a contract, retain the existing acceptance-planning handoff. Do not create a wrapper child or an approved branch-destination plan just to record `NO SPLIT`.

**Conflicting assessments.** A current `NO SPLIT` result informs delivery but does not override its safety guard. If delivery still rejects the scope, it must identify a concrete omitted burden, changed fact, or unresolved disagreement and give a focused reconciliation handoff. It must not repeat a generic “too large” message in an endless plan/slice/deliver loop. No additional automatic calls or retry cycles are introduced.

**Planning inside delivery.** If an existing `deliver-issue` invocation calls `plan-acceptance` and the result recommends direct delivery, the enclosing invocation continues under its existing gates; it does not launch another `deliver-issue`. If planning establishes that sizing inspection is needed, retain the contract and recommendation and return a precise blocker before implementation. Do not automatically invoke slicing or create children. If no established contract exists at an earlier delivery guard, retain the existing planning-first handoff rather than sending the slicer an invented agreement.

**Existing children and parents.** Planning a child assesses only its precise contribution and inherited constraints, not unrelated sibling outcomes. A manageable child follows its existing plan. A newly exposed oversized child returns to reconciliation of that decomposition with a concrete reason; it does not automatically gain grandchildren. Planning an already sliced parent preserves its applicable approved child plan and completion workflow rather than recommending delivery of the entire original scope as new work. A final parent review/proof handoff is not a new decomposition request. Material scope changes and authorized re-slicing follow R8.

Missing downstream packages produce an honest installation/handoff message, not a false completion claim or a new mandatory dependency for standalone planning or slicing.

## 4. Produce the fewest right-sized children

### R1. Inspect enough context to make a grounded judgment

Read the source, parent agreement when present, existing decomposition, and relevant repository instructions. Preserve the existing `NO SPLIT` path for a clearly small source without manufacturing a contract; a complete decomposition still requires an established parent agreement. Inspect the implementation paths, interfaces, state changes, tests, and evidence facilities that materially affect candidate boundaries.

Use relevant, retrievable delivery history and applicable accepted advisory learnings when available: for example, a linked earlier work item with similar implementation or proof difficulties. Advice remains nonbinding and must not add unsupported requirements. [S8] Distinguish observed facts from an interpretation of why a delivery succeeded or failed. A repair or failed test alone is not evidence that the child was too large.

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

Reuse the existing outcome, contribution, dependency, and evidence descriptions instead of copying a second contract into this section. For `NO SPLIT` on an existing canonical work item, retain the short result in `slicing.md` as specified by R12. With only a small source and no work item, return the rationale without creating a work item merely to store it. A draft-only invocation continues to report `DRAFT` under existing status rules; it may state a proposed no-split conclusion, but that does not become approval or authority for any later effect.

### R8. Preserve authority, identity, and downstream requirements

Apply the new sizing behavior to new decompositions and explicitly requested reconsideration. Do not invalidate or automatically regroup an approved plan because it lacks a sizing rationale. Do not create replacement issues, rewrite child contracts, or close existing children merely to reduce the count.

For authorized re-slicing, preserve completed work, human edits, identities, history, and traceable old-to-new contributions. Preview material allocation changes under existing approval rules. Changes to child promises return to `plan-acceptance`; regrouping unchanged promises does not by itself revise the parent's meaning. [S3]

Preserve local-first operation, draft-only behavior, publication authority, readiness rules, prerequisite checks, and full parent verification on one assembled candidate. Historical child proofs must not become a parent verdict. Existing result statuses remain unchanged. [S1] [S3]

The resulting flow is the conditional route in Section 2, not mandatory slicing for every parent. `deliver-issue` may invoke missing child planning under its existing rules; sizing does not supply approval or bypass it. Apply R12 to nested invocations, existing children, and parent completion. [S4]

## 5. Example: the same promise can need different delivery shapes

Consider retry-safe uploads. A preliminary list separates database changes, API changes, authorization, browser changes, tests, and documentation.

**Clearly manageable.** The repository already supplies the storage and authorization mechanisms; the browser change is a thin call into the same existing flow, with a bounded public-interface evidence plan. `plan-acceptance` recommends direct delivery. There is no mandatory slicing invocation.

**Materially uncertain.** Acceptance planning identifies the required outcome but cannot yet tell whether browser recovery is a thin extension or a separate state machine. It names that specific question and recommends sizing inspection. If deeper inspection confirms a small existing mechanism, `slice-contract` returns `NO SPLIT`, records why, and directs approved work to delivery without another generic sizing pass.

**Clearly broad.** Inspection establishes substantial server-side persistence/recovery work and a new browser offline queue with its own restart and cancellation behavior. Planning recommends slicing; the slicer may retain separate server and browser contributions because combining both mechanisms would overload implementation and verification. Each includes its necessary tests, failures, constraints, and evidence. The browser contribution has an explicit server prerequisite; combined interactions remain in parent verification.

These alternatives illustrate judgments, not fixed ticket counts. The controlling facts are implementation and verification burden, not document length, headings, or the mere ability to name multiple behaviors.

## 6. Implementation scope

| Location | Required change |
|---|---|
| `skills/productivity/plan-acceptance/SKILL.md` | Add the lightweight assessment, conditional handoff, durable recommendation, and existing/nested-work handling. Update both final next steps and generic contract-template handoff. |
| `skills/productivity/slice-contract/SKILL.md` | Implement R1–R8; consume the planner's sizing question without treating it as an order to split. Retain `NO SPLIT` results and give a consistent direct-delivery handoff under R12. |
| `skills/productivity/slice-contract/references/sizing.md` — new | Bundle a compact decision guide and contrasting examples. Keep core behavior in `SKILL.md`. |
| `skills/productivity/deliver-issue/SKILL.md` | Preserve the oversized-work guard; align nested-planning responses and consideration of current sizing results. Prevent recursive self-invocation and generic routing loops. |
| `docs/acceptance-contract-protocol.md` | Describe delivery-shape advice, ownership, storage, identity, and handoffs. Keep acceptance semantics, approved branch-destination format, existing status values, and authority unchanged. Keep distributed copies consistent. |
| `checks/plan-acceptance-scenarios.md`, `checks/slice-contract-scenarios.md`, and `checks/deliver-issue-scenarios.md` | Add the mapped cases below, reuse fixture conventions, and preserve existing coverage. |
| `checks/right-sized-delivery-validation.md` — new | Retain actual routing/sizing comparisons, delivery observations, failures, and unexecuted checks. Replaces the earlier proposal's narrower validation-file deliverable; do not rewrite historical validation evidence. |
| `docs/how-to.md`, `docs/faq.md`, and relevant README handoffs | Explain the conditional workflow, pending approvals, `NO SPLIT`, and the preference for fewer children. Show direct, sliced, and uncertain-then-unsplit examples. |

`create-parent-issue` keeps its existing behavior and next command. Documentation may explain what acceptance planning decides next; parent creation must not gain a sizing gate or approve a delivery shape.

Use existing filesystem helpers for the small advisory report. Do not add a controller parser, machine-enforced sizing field, required model call, mandatory audit, scheduler, learning service, new issue type, new command, or user configuration. The behavior must work with each skill installed alone and its bundled references. No new runtime dependence on a sibling skill's source files is permitted.

## 7. Required behavioral scenarios

Use the existing installed-skill evaluation conventions: disposable repositories, expectations withheld from the actor, recorded inputs and identities, actual action/artifact inspection, and honest distinction between simulated and live effects. [S6]

The routing cases below use source-specific labels `DS1`–`DS10`; map them into the corresponding check files without colliding with existing case IDs. The sizing cases retain the proposed T22–T33 identities from version 1.0; renumber only if intervening repository changes require it, retaining traceability.

### Routing and handoff cases

| Case | Fixture and required observation | Requirements |
|---|---|---|
| DS1: Small direct path | A coherent, manageable contract with several rows produces direct delivery after required gates. No sizing invocation, child files, or wrapper issue. | R9–R11 |
| DS2: Broad parent | Distinct substantial mechanisms and verification burdens produce a grounded `/slice-contract` recommendation. The planner creates no decomposition, and its template does not contradict that handoff. | R9–R11 |
| DS3: Uncertain, then unsplit | Name a material sizing uncertainty. Deeper slicing inspection resolves it as manageable; retain `NO SPLIT`. A fresh planner and delivery session do not repeat the earlier generic uncertainty. No source facts change between these latter steps. | R9–R12, R7 |
| DS4: Uncertain, then sliced | The same routing pattern reveals genuine breadth on inspection. The first complete decomposition has justified boundaries and no obvious feasible merge. Planning did not preselect a count. | R9, R1–R6 |
| DS5: Route is not readiness | Variants: approval pending, unresolved product promise, missing credible oracle, known harness not yet built, unavailable host, and unmet prerequisite. Identify the actual next gate; neither manufacture splitting nor authorize implementation to bypass it. | R9–R12, R8 |
| DS6: Existing hierarchy | Plan a manageable child and an already sliced parent without making grandchildren or bypassing the approved plan. Introduce concrete new child scope separately and require a scoped reconciliation handoff. Preserve final-parent verification. | R8, R12 |
| DS7: Planning inside delivery | Exercise direct and sizing recommendations from nested planning. The direct case continues the enclosing workflow; the sizing case stops before implementation with retained artifacts. Neither recursively invokes delivery nor automatically slices. | R10–R12 |
| DS8: Persistence and publication | Recover advice from the work path; preserve exact contract bytes and approval receipts. Exercise local-only, draft-only, authorized issue handoff, missing write access, and unchanged rerun variants. No unauthorized extra comment or new acceptance state. | R10, R11 |
| DS9: Drift and disagreement | Reuse a current rationale; separately change a material promise/context fact and detect stale advice. If delivery disputes current `NO SPLIT`, require a specific reason and reconciliation, not a generic loop or blind admission. | R11, R12 |
| DS10: Optional and standalone paths | Each changed skill works with its bundled references and truthful missing-skill handoffs. `create-parent-issue` still points to acceptance planning without a sizing decision. Legacy approved work without advisory reports is not newly blocked. | R8–R12 |

### Sizing cases retained from version 1.0

| Case | Fixture and required observation | Requirements |
|---|---|---|
| T22: Manageable parent | One coherent outcome with several requirements. A normal invocation returns `NO SPLIT`, with no wrapper child; an explicit draft-only invocation retains `DRAFT` and proposes no split. | R2, R3, R6 |
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

## 8. Validation and acceptance

### First-handoff and first-proposal comparison

Run the baseline and revised installed skills on equivalent disposable fixtures, with the same model configuration, tools, permissions, and starting artifacts. Capture the planner's first route and the slicer's first complete proposal before corrective feedback. Retain the exact fixture, skill, model/host identity when available, requests, actions, artifacts, and before/after identities.

Execute every required new case and variant. Repeat the central over-slicing, under-slicing, and uncertain-routing cases in at least three fresh contexts per version. This is an evaluation procedure, not runtime overhead or a ticket-count policy. Hold back cases from the bundled examples to check generalization.

Use mechanical checks for coverage, identities, links, unchanged protected content, and permitted writes where practical. Have an evaluator other than the producing invocation judge whether the routing and boundary reasons are supported, a credible lower-count alternative was missed, or a contribution remains oversized. Define these criteria before examining the candidate outputs. Do not demand identical prose or one unique partition.

Compare unnecessary slicer referrals, inappropriate direct referrals, unnecessary boundaries, oversized contributions, lost obligations, contradictory next steps, repeated routing, and required human corrections. Count the entire plan, including enabling and integration work. Moving work off the child list or bundling unrelated scope is not improvement.

### Delivery reality check

Exercise at least one representative parent through both baseline and revised workflows, and a second, more demanding parent through the revised workflow. Use equivalent fresh checkouts, establish required approvals, deliver all selected children through the real supported workflow, and verify the assembled parent. Deliver an unsliced result directly as the original work item.

Across these observations and the routing scenarios, cover direct delivery, actual decomposition, and uncertain-then-`NO SPLIT` handoffs. At least one retained execution must exercise planning inside an actual `deliver-issue` workflow so a correct-looking standalone recommendation does not conceal recursive dispatch or continued implementation after a sizing blocker.

Record completion/blocker outcomes, repairs, re-slicing, human intervention, extra routing calls, and available elapsed-time and usage evidence, including planning overhead. Distinguish sizing-related failures from host, permission, and unrelated implementation defects. Mark unavailable costs unknown. Fewer planned tickets alone does not prove faster or cheaper delivery.

Controlled fixtures can establish routing and authorized effects against their interface. They cannot establish real host isolation, successful independent delivery, or live GitHub compatibility. Label evidence classes separately; unavailable required execution remains a gap, not a pass.

### Acceptance conditions

The change is ready when R1–R12 and their mapped scenarios are satisfied, affected existing checks pass, standalone installation includes all referenced guidance, and representative delivery observations support the resulting boundaries without a known unresolved sizing-related failure.

Small work must not acquire mandatory slicing overhead. Broad or materially uncertain work must receive an actionable sizing handoff. Over-fragmented work must lose avoidable boundaries, while genuinely broad work retains necessary splits. Applicable `NO SPLIT` decisions must lead forward without bypassing approval or safety checks.

All source promises, inherited constraints, dependent contributions, authority boundaries, and parent-verification obligations must survive. Preserve existing coverage for relationship publication/recovery, exact identities, contract revisions, and partial effects; no change here grants additional remote authority.

Report where the baseline already performs as well, where the revision helps, where results vary, and where it fails. Claim measured savings only when comparable observations support them. Do not rewrite prior validation as evidence of this feature; the historical sampled validation has its own explicit limits. [S7]

## 9. Non-goals and completion definition

This proposal does not implement `audit-slicing`, weaken review/proof, change the repair budget, guarantee a delivery duration, produce numerical effort estimates, enforce a globally minimal partition, or automatically learn new policy. It does not change branch strategy, add child scheduling, create automatic publication, or merge/close existing issues to improve a metric.

Completion requires updated instructions, bundled examples, aligned handoffs and documentation, scenario fixtures where needed, and retained behavioral validation—not only a paragraph advising the model to make better tickets.

The intended experience is: create a source issue when wanted, plan acceptance, follow P2P's explicit recommendation, and receive the fewest manageable children only when slicing is warranted.

> **Avoid an unnecessary slicing pass. Avoid an unnecessary child. Never buy either saving by weakening the promise or making delivery unmanageable.**

## 10. Version and requirement continuity

Version 2.0 is a complete replacement for the version 1.0 proposal, not an additional independent feature specification. Replace `plans/right-sized-slicing-spec.md` under the normal source-edit process; retain the old version in history. This document does not itself authorize a repository update, issue creation, contract revision, implementation, or publication.

R1–R6 keep their original sizing intent. R7 adds durable `NO SPLIT` continuity for an existing work item; R8 now applies within the conditional workflow. R9–R12 add lightweight routing, gated next actions, an advisory record, and loop/lifecycle handling. T22–T33 remain sizing cases; DS1–DS10 extend validation across planning and delivery. The validation deliverable expands from slicing-only to the complete workflow.

If version 1.0 has already become an approved work contract, reconcile this source revision through `plan-acceptance` and its normal amendment/approval rules. Do not silently replace that contract or treat this source's R identifiers as automatically identical to its acceptance rows.

## Sources inspected

References describe the inspected baseline, not implementation, approval, or successful validation of this proposal. The baseline advances the earlier inspected commit `18bab308a297b9af978d6dcf3e1107cd5eaedce5` by adding the version 1.0 proposal; the compared skill and protocol files are unchanged. [S10]

[S1]: https://github.com/grove/promise-to-proof/blob/bac5aa15345514416f3f7244f48c88c4edd7daa1/skills/productivity/slice-contract/SKILL.md "slice-contract instructions"
[S2]: https://github.com/grove/promise-to-proof/blob/bac5aa15345514416f3f7244f48c88c4edd7daa1/skills/productivity/create-parent-issue/SKILL.md "create-parent-issue instructions"
[S3]: https://github.com/grove/promise-to-proof/blob/bac5aa15345514416f3f7244f48c88c4edd7daa1/docs/acceptance-contract-protocol.md#parent-and-child-contracts "Parent/child contracts and epic delivery plans"
[S4]: https://github.com/grove/promise-to-proof/blob/bac5aa15345514416f3f7244f48c88c4edd7daa1/skills/productivity/deliver-issue/SKILL.md "Delivery work-item and agreement handling"
[S5]: https://github.com/grove/promise-to-proof/blob/bac5aa15345514416f3f7244f48c88c4edd7daa1/skills/productivity/deliver-issue/SKILL.md#review-prove-and-recover "Review, proof, recovery, and authority"
[S6]: https://github.com/grove/promise-to-proof/blob/bac5aa15345514416f3f7244f48c88c4edd7daa1/checks/slice-contract-scenarios.md "Existing slicing scenarios"
[S7]: https://github.com/grove/promise-to-proof/blob/bac5aa15345514416f3f7244f48c88c4edd7daa1/checks/slice-contract-validation.md "Historical sampled slicing validation"
[S8]: https://github.com/grove/promise-to-proof/blob/bac5aa15345514416f3f7244f48c88c4edd7daa1/skills/productivity/plan-acceptance/SKILL.md "Acceptance planning and handoffs"
[S9]: https://github.com/grove/promise-to-proof/blob/bac5aa15345514416f3f7244f48c88c4edd7daa1/docs/acceptance-contract-protocol.md#standalone-planning-on-an-issue "Standalone planning and exact approval handoffs"
[S10]: https://github.com/grove/promise-to-proof/compare/18bab308a297b9af978d6dcf3e1107cd5eaedce5...bac5aa15345514416f3f7244f48c88c4edd7daa1 "Comparison with version 1.0 inspected baseline"
[S11]: https://github.com/grove/promise-to-proof/blob/bac5aa15345514416f3f7244f48c88c4edd7daa1/plans/right-sized-slicing-spec.md "Version 1.0 source proposal"

Predecessor source: [Version 1.0 proposal][S11].
