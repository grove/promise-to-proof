# Proposal: Self-routing, right-sized, adaptively refinable delivery

**Status:** Proposed specification, version 3.0 — not an approved acceptance contract.  
**Date:** 27 September 2026.  
**Repository location:** Replace `plans/right-sized-slicing-spec.md`.  
**Supersedes:** Version 2.0, “Choose the delivery shape and minimize child issues.”  
**Inspected baseline:** `grove/promise-to-proof` `main` at `357bf61992d960d60014c6531152330021847139`.  
**Execution status:** Specification only. Implementation and behavioral validation have not been performed.

## 1. Objective

Make Promise to Proof choose and maintain sensible delivery-unit boundaries without requiring the developer to predict the workflow shape in advance.

The user should supply the work, resolve product decisions, and approve consequential changes. P2P should decide whether the current work item should move forward directly, be inspected for slicing, or be re-sliced when later evidence shows that an earlier boundary was wrong.

The governing rule is:

> **Use the fewest delivery units that can still be delivered reliably. Right-size before delivery when possible; re-size locally when evidence proves a boundary wrong.**

Every additional child pays for another acceptance-planning and delivery cycle, including implementation context, independent review, proof, durable handoffs, and eventual parent verification. Therefore prefer fewer children. Split only when another boundary materially improves deliverability, verification, compatibility, recovery, or another binding constraint.

This proposal has three connected goals:

1. **Self-routing:** `plan-acceptance` recommends direct delivery or deeper sizing inspection so the user does not need to know whether to invoke `slice-contract`.
2. **Right-sizing on the first attempt:** `slice-contract` produces the smallest defensible decomposition before creating children.
3. **Adaptive refinement:** if actual delivery later reveals an outlier child that is materially too broad, re-slice only that affected work item while preserving the rest of the tree and all prior work.

The goal is not perfect effort prediction or a mathematically optimal partition. It is a grounded engineering judgment that reduces avoidable delivery overhead while keeping work tractable.

## 2. Core principles

### 2.1 Minimize child count subject to reliable delivery

The optimization order is:

1. Preserve the complete agreement, safety constraints, authority, and verification requirements.
2. Keep each leaf work item coherent and realistically deliverable.
3. Among decompositions satisfying 1–2, choose fewer children.
4. At equal child count, prefer less duplicated context, setup, proof work, coordination, and integration burden.

Do not split merely because requirements, files, layers, tests, actors, or UI/API surfaces can be named separately.

### 2.2 Delivery difficulty is not the same as delivery size

A difficult algorithm, tricky concurrency defect, or stubborn proof gap may still be one coherent delivery unit. Re-slicing must not become an escape hatch from hard implementation, failed tests, review findings, or a failed proof.

Create a new boundary only when evidence shows a useful separable unit whose isolation makes delivery materially more manageable.

### 2.3 Decomposition is revisable planning, not a promise rewrite

Changing how an unchanged promise is divided changes the decomposition, not the promise itself. `plan-acceptance` remains the sole owner of acceptance-contract revisions. A changed product outcome, boundary, exclusion, or consequential seam still returns to acceptance planning.

### 2.4 Correction should be local

When one child turns out to be oversized, reconsider that child and the smallest affected subtree. Do not reopen unaffected siblings or recreate the whole epic unless the new evidence actually changes their contribution, prerequisites, or agreement.

### 2.5 The workflow should tell the user what to do next

Every relevant stage should identify one immediate next workflow action from current evidence. The user should not be asked to choose between `deliver-issue`, `slice-contract`, or re-slicing based on internal P2P mechanics.

Routing advice does not grant approval or external write authority.

## 3. Terminology

**Delivery cycle**  
The existing work-item workflow: acceptance planning as needed, implementation, candidate capture, independent review, independent proof, durable evidence, and any permitted repair/recheck. Publication and merge readiness remain separate.

**Leaf work item**  
A work item with no active child decomposition. It is eligible for direct implementation/delivery when its other gates are satisfied.

**Parent work item**  
A work item with an active approved decomposition into children. Its own contract and contribution remain authoritative, but implementation proceeds through its descendants plus any explicitly assigned integration work. Child proofs do not establish parent acceptance.

**Sizing inspection**  
The deeper inspection performed by `slice-contract` to decide `NO SPLIT` versus decomposition and, when decomposed, the smallest defensible boundaries.

**Sizing signal**  
Concrete evidence discovered after initial planning that could change whether the current work item is a viable leaf—for example, two substantially different recovery mechanisms whose implementation and verification are independently bounded. “This is hard” is not a sufficient sizing signal.

**Re-slicing**  
Running `slice-contract` on an existing work item whose current decomposition or leaf status is being reconsidered from new evidence.

**Affected subtree**  
The smallest work-item hierarchy whose contribution, prerequisites, routing, or work allocation must change because of a re-slice.

## 4. Workflow and ownership

The normal path is:

```text
create-parent-issue (optional)
    → plan-acceptance
        → clearly manageable: deliver-issue
        → too broad or materially uncertain: slice-contract
            → NO SPLIT: deliver-issue
            → split: plan children → deliver ready children → parent completion
```

If later evidence shows a leaf is oversized:

```text
... → deliver-issue work/C.md
        → concrete sizing signal
        → BLOCKED with /slice-contract work/C.md
            → NO SPLIT: resume work/C.md with the concrete disagreement resolved
            → split: C becomes a parent; create C1..Cn; unaffected siblings continue
```

The hierarchy may therefore evolve from:

```text
Parent
├── A
├── B
└── C
```

to:

```text
Parent
├── A
├── B
└── C
    ├── C1
    └── C2
```

`C` continues to represent the same contribution to `Parent`. `C1` and `C2` explain how that contribution will be delivered.

| Owner | Responsibility | Must not do |
|---|---|---|
| `create-parent-issue` | Preserve one originating source issue and hand off to acceptance planning. | Size work or create children. |
| `plan-acceptance` | Author the contract and make a lightweight direct-vs-sizing recommendation. | Design child boundaries. |
| `slice-contract` | Perform sizing inspection, initial decomposition, and authorized local re-slicing. | Rewrite acceptance promises or treat hard work as evidence for arbitrary fragmentation. |
| `implement-contract` | Implement one leaf contribution; preserve partial work and report a grounded sizing concern when implementation exposes one. | Create children or silently redefine scope. |
| `deliver-issue` | Coordinate one ready leaf, consume routing/decomposition state, and stop with a precise sizing handoff when a leaf is no longer defensible. | Automatically create children, retry routing indefinitely, or use slicing to avoid a defect. |
| `review-implementation` / `prove` | Provide implementation and acceptance evidence. Their findings may become sizing evidence for the enclosing workflow. | Own decomposition or transform a failed verdict into a split by themselves. |

Stage skills remain separate. This proposal improves handoffs and routing; it does not introduce automatic recursive slash-command invocation.

## 5. Existing requirements retained from version 2

R1–R12 retain their version 2 identities and intent. This version restates them so it is a complete replacement specification.

### R1. Inspect enough context to make a grounded sizing judgment

`slice-contract` reads the source, canonical agreement, existing decomposition, repository instructions, relevant implementation paths, interfaces, state transitions, tests, evidence facilities, and applicable retained history that could materially change a boundary decision.

Use relevant prior delivery observations as evidence, with attribution. Do not infer that a prior failure was caused by ticket size merely because it occurred. Missing history is not a blocker.

Stop when additional inspection is unlikely to change the proposed boundaries. Sizing must not become implementation or an exhaustive architecture exercise.

### R2. Start with the broadest plausible grouping

First consider whether the entire work item should remain one leaf. Otherwise start from a small number of broad, coherent contributions.

Do not create one ticket per requirement, file, layer, test, subsystem label, or available agent and then call that the natural decomposition.

Related validation, persistence, authorization, failure behavior, tests, migration steps, and necessary documentation normally stay with the outcome they establish.

### R3. Assess the full delivery burden

For every candidate leaf, consider these dimensions together:

| Dimension | Question |
|---|---|
| Outcome coherence | Is this one understandable contribution rather than unrelated changes bundled together? |
| Implementation context | Can the relevant mechanisms and interactions be understood and changed as one bounded unit? |
| Uncertainty | Are unknowns ordinary implementation choices, or do they materially threaten the boundary? |
| Prerequisites / compatibility | Are dependencies, transition states, and inherited constraints tractable? |
| Review and proof | Can independent review and proof establish this outcome with a bounded credible evidence approach? |
| Extra-cycle overhead | Would another child duplicate significant context, setup, proof, handoff, or integration work? |

Support consequential judgments with inspected facts. Do not use scores, story points, file counts, requirement counts, token counts, or fixed time limits as substitutes for reasoning.

### R4. Challenge additional boundaries with a merge test

Before presenting a decomposition, examine related children and plausible groups, including non-adjacent ones.

Ask:

> Could these be one delivery unit without materially compromising coherence, manageability, verification, compatibility, or another binding constraint?

If yes, merge them before presenting the first complete proposal.

When retaining a boundary, name the concrete reason it earns another delivery cycle. Generic parallelism, cleanliness, organizational ownership, or the ability to test things separately are not enough by themselves.

### R5. Split only to solve an identified delivery problem

When a candidate is too broad, identify the actual burden first. Explain what becomes materially easier to implement, review, prove, recover, or migrate after the split.

Choose the least additional fragmentation that resolves that burden, then re-run the merge test on the resulting children.

If the underlying work is simply difficult but not usefully separable, keep it intact and expose the actual blocker rather than generating artificial sub-tickets.

### R6. Finish sizing before creating the child set

The first complete proposal must already reflect the merge and split checks. Do not rely on the user to notice over-slicing or under-slicing after the proposed children are created.

Before creation, establish that every proposed leaf has a credible delivery approach, every retained boundary has a material reason, no obvious feasible merge remains, and all parent obligations and shared constraints are accounted for.

### R7. Retain a concise sizing rationale

Store a `## Sizing rationale` in `.p2p/work/<parent>/slicing.md`, outside the exact `## Approved delivery plan` byte range.

Record:

- why the parent is or is not kept whole;
- why each proposed leaf is manageable;
- why the strongest plausible merges were rejected;
- relevant implementation/evidence references;
- material assumptions or unknowns.

This is a decision summary, not chain-of-thought, another acceptance contract, or a numeric score.

For `NO SPLIT`, retain the direct-delivery reason and exact agreement identity without manufacturing a child or delivery plan.

### R8. Preserve authority, history, and downstream semantics

New sizing behavior does not invalidate approved legacy plans merely because they lack new rationale fields.

Material allocation changes follow existing approval rules. External issue, relationship, branch, PR, label, or publication effects retain their own authority and readback requirements.

Preserve work-item identities, human edits, agreement history, completed work, routing history, and exact report meaning. Regrouping unchanged promises does not silently revise the parent acceptance contract.

Full parent verification remains required on one exact assembled candidate. Historical child proof never composes into a parent verdict.

### R9. `plan-acceptance` performs a lightweight delivery-shape assessment

After building the proposed contract, `plan-acceptance` asks:

> Can this complete work item reasonably be implemented, independently reviewed, and proven as one bounded delivery unit?

Use context already inspected for acceptance planning plus only focused additional inspection that could change the route.

Return one advisory result:

| Assessment | Route |
|---|---|
| Clearly coherent and manageable | Direct delivery |
| Clearly too broad | Sizing inspection |
| Materially uncertain whether it fits | Sizing inspection |

Ordinary implementation unknowns, several acceptance rows, missing historical measurements, or a difficult algorithm do not by themselves trigger slicing.

An unresolved product outcome remains an acceptance-planning question, not a sizing question.

### R10. Give one clear immediate next action

For a saved, approved, unblocked unsliced work item:

- direct route → `/deliver-issue work/<slug>.md`;
- sizing route → `/slice-contract work/<slug>.md`.

If approval, storage, an outcome decision, or another gate is pending, that gate is the immediate next action. The later route may be stated conditionally, but do not present multiple competing workflow choices.

The contract template and final `Next steps:` guidance must agree. Do not leave an unconditional implementation handoff that contradicts the delivery-shape recommendation.

### R11. Retain the delivery-shape recommendation without changing the contract

Save `.p2p/work/<slug>/delivery-shape.md` using existing history-preserving storage and readback rules.

Record the exact work-item and binding-input identities, recommendation, concise reason, relevant inspected context, material assumptions, applicable prior `NO SPLIT`/decomposition result, and immediate next action.

The report is advisory. It is not a second contract, a readiness state, a candidate snapshot, or a new admission requirement for old work.

### R12. Prevent routing loops and accidental re-slicing

A current `NO SPLIT` finding is consumed by later planning and delivery so unchanged work is not sent back to `slice-contract` merely because the earlier lightweight assessment was uncertain.

If `deliver-issue` disagrees with a current `NO SPLIT` result, it must name new or previously omitted evidence. A generic “too large” message is insufficient.

Planning invoked inside an existing `deliver-issue` run does not recursively invoke another delivery. A direct result lets the enclosing run continue; a sizing result returns a precise blocker before dependent implementation.

Planning a child assesses the child contribution. It does not automatically reconsider unrelated siblings or create grandchildren.

## 6. Adaptive re-slicing requirements

### R13. Detect a sizing problem from concrete delivery evidence

`deliver-issue` and direct `implement-contract` may discover new evidence that the current leaf boundary is wrong before or during implementation.

A valid sizing signal must identify at least one concrete burden and why a different boundary could reduce it. Examples include:

- multiple substantial state machines with independently bounded outcomes;
- distinct migration/recovery stages that cannot be reasoned about safely as one leaf;
- substantially different verification environments or recovery mechanisms whose combination is the source of delivery risk;
- implementation discovery that the alleged single outcome actually contains separable complete contributions with a stable interface between them.

The report must cite the inspected code, agreement, candidate, failed assumption, or other observable basis for the signal.

The following are **not sufficient on their own**:

- the implementation is taking longer than expected;
- a test failed;
- review requested changes;
- proof found a defect;
- the automatic repair allowance was exhausted;
- the diff is large;
- many files or requirements are involved;
- the model is uncertain or has consumed substantial context.

Those cases follow the existing implementation, repair, or blocker path unless the evidence independently establishes a useful separable delivery boundary.

### R14. Route an oversized leaf to `slice-contract` without silently changing it

When a grounded sizing signal makes the current leaf materially unsuitable for continued direct delivery, stop dependent work safely and return a precise sizing handoff:

```text
Delivery sizing: reconsider this leaf.
Reason: <concrete burden and evidence>.
Preserved work: <candidate/report/worktree references>.
Next: /slice-contract work/<slug>.md
```

`deliver-issue` returns `BLOCKED` rather than pretending the leaf is delivered. `implement-contract` uses `PARTIAL` when safe useful implementation work exists, otherwise `BLOCKED` under its existing semantics.

Neither skill creates children, edits the decomposition, closes issues, or changes tracker relationships automatically.

### R15. Re-slice only the smallest affected subtree

When `slice-contract` is invoked on an existing child, treat that child as the proposed parent of the new subdivision.

By default:

- keep its own parent link unchanged;
- keep unaffected siblings unchanged;
- preserve the original contribution mapping from the child to its parent;
- create the new decomposition under `.p2p/work/<child>/slicing.md`;
- map the new grandchildren to the child contract, not directly to the grandparent;
- change ancestors or siblings only when the new evidence actually changes their prerequisite or contribution semantics.

Do not flatten grandchildren into the top-level parent merely for convenience.

If the smallest safe correction requires changing an ancestor boundary, preview that wider affected subtree explicitly and require the same approval that such a material allocation change would normally require.

### R16. A leaf may become a parent while preserving its meaning

An approved/applied re-slice changes the work item's role, not its promised contribution.

Before:

```text
Parent → C (leaf contribution)
```

After:

```text
Parent → C (same contribution, now a parent)
          ├── C1
          └── C2
```

While C's active decomposition has remaining children, C is not a direct implementation leaf. `deliver-issue work/C.md` must use the decomposition to identify the next appropriate child or parent-completion action rather than start a second competing implementation of C.

C1/C2 receive their own child contracts through `plan-acceptance`. C's original contract remains the agreement that their assembled result must eventually satisfy.

After descendant implementation is assembled, C requires full review and proof of C's complete contract on one exact candidate, including interactions across C1/C2. Their historical proofs do not compose into C acceptance. The top-level parent later retains its own full parent verification requirement.

### R17. Preserve and explicitly allocate in-flight work

Before proposing a re-slice, inspect existing implementation reports, candidates, worktree changes, evidence, open PR state when known, and human edits for the affected leaf.

Retain an `## Existing work allocation` section in its `slicing.md` that classifies relevant existing work as one of:

- attributable to a proposed child;
- shared/integration work belonging at the re-sliced parent level;
- still valid historical evidence but not implementation to carry forward;
- unresolved ownership requiring a focused decision before dependent editing.

Do not move, duplicate, discard, cherry-pick, retarget, close, or rewrite code/PRs merely by saving the decomposition.

Existing implementation may reduce future work, but the planner must not claim that a new child is already implemented merely because some matching bytes exist. The receiving implementation workflow confirms scope, prerequisites, candidate identity, and ownership.

If an open PR contains mixed future-child payload, record the contamination and the required extraction/strategy action. Re-slicing approval alone does not authorize that effect.

### R18. Preserve verification meaning after re-slicing

Existing implementation, review, and proof reports remain historical records tied to their exact old work-item agreement and candidate.

Re-slicing does not automatically transform:

- old parent proof into child proof;
- partial implementation observations into completed child outcomes;
- a review finding into acceptance evidence;
- previously green checks into proof of a new child contract.

Applicable observations and tests may be reused as inputs after their identity and scope are re-established under the existing protocol.

If the final assembled candidate and agreement happen to satisfy ordinary report-reuse rules exactly, existing reuse rules apply; this specification creates no special shortcut.

### R19. Permit consolidation of undersized siblings when it still reduces total cost

Re-sizing may also merge children when later evidence shows that the original plan was unnecessarily fine-grained.

Prefer consolidation only while the affected children are unstarted or still in planning, or when an explicit re-slice can preserve all started work without making the correction cost exceed the avoided delivery overhead.

Do not rewrite completed/proven children merely to make the hierarchy prettier. Their historical identities and completion remain intact.

A merge preview must explain:

- which delivery cycles would be avoided;
- why the combined leaf remains manageable;
- what contracts/work files would be superseded or retained as historical mappings;
- how human edits, candidates, reports, and tracker mirrors are preserved;
- what approval is required.

When consolidation is no longer economical or safe, keep the existing children.

### R20. Bound recursive decomposition and keep the next action ergonomic

Nested slicing is allowed, but recursive fragmentation must stop when another boundary no longer solves a concrete delivery problem.

If a child remains hard because its single outcome is intrinsically difficult, `slice-contract` returns `NO SPLIT` or a focused blocker. It must not generate C1a/C1b/C1c simply to reduce apparent complexity.

Every sizing-related handoff must include:

- current work-item role: leaf or parent;
- exact applicable contract/decomposition identity;
- concise reason for the route;
- preserved in-flight work references when applicable;
- one immediate next action;
- any approval or prerequisite that must occur first.

When the user invokes a parent work item with active descendants, P2P should recover the tree and point to the next ready leaf, unresolved planning decision, or parent-completion step. The user should not need to remember the hierarchy manually.

A stale or contradictory route is reconciled from durable records and current evidence; it is not resolved by blindly alternating `deliver-issue` and `slice-contract`.

## 7. Ergonomic behavior by common situation

| User situation | Expected P2P behavior |
|---|---|
| “I created a parent issue. What next?” | `plan-acceptance` creates the agreement and tells the user direct delivery or sizing inspection. |
| “This contract looks big; I don't know whether to slice.” | User runs the normal planning flow; the routing judgment is P2P's responsibility. |
| `slice-contract` inspects a questionable parent and finds it manageable. | Return durable `NO SPLIT` and route to direct delivery. |
| One child later turns out to be a mini-epic. | Delivery preserves work and routes that child to `slice-contract`; unaffected siblings continue. |
| One child is simply technically hard. | Keep the leaf; continue normal implementation/repair unless a separable boundary is evidenced. |
| Two untouched children prove unnecessarily tiny. | Explicit re-slice may merge them if the avoided cycles exceed correction overhead. |
| Child C becomes parent of C1/C2. | C keeps its parent contribution; P2P routes future work to C1/C2 and later C-level assembly verification. |
| User invokes the old parent path after nested slicing. | Recover the active tree and state the single next ready action instead of asking the user to reconstruct it. |

## 8. Durable records

Reuse existing storage. Do not introduce a new database or scheduler.

### 8.1 `delivery-shape.md`

Owned by acceptance planning for lightweight direct-vs-sizing advice.

Minimum fields:

```markdown
# Delivery shape

Work item: work/foo.md
Contract: v2 sha256:<...>
Binding inputs: <identities>
Assessment: direct | sizing-inspection
Reason: <concise evidence-backed reason>
Applicable slicing result: <path/hash or None>
Material assumptions: <... or None>
Immediate next action: <one action>
Outstanding gates: <... or None>
```

### 8.2 `slicing.md`

Continue to own decomposition and delivery-plan state. Add or retain these sections as applicable:

- `## Sizing rationale`
- coverage map and dependency graph
- `## Existing work allocation` for re-slicing with in-flight work
- `## Proposed delivery plan`
- exactly one active `## Approved delivery plan` under existing byte-identity rules
- history/transition notes identifying the prior decomposition when re-slicing

Do not alter the machine-consumed byte semantics of the approved delivery-plan section.

### 8.3 No new acceptance state

“direct”, “sizing-inspection”, “leaf”, and “parent” are routing/decomposition descriptions, not new acceptance verdicts.

Contract plan states, implementation statuses, review outcomes, proof verdicts, publication states, and merge-readiness semantics remain owned by their existing stages.

## 9. Approval and authority

Detection and recommendation are read-only/advisory except for already-authorized local report storage.

The following remain consequential changes requiring existing authority:

- creating or replacing child work files;
- changing allocation mappings or dependencies;
- activating a revised decomposition or delivery strategy;
- publishing/updating tracker issues or native relationships;
- retargeting or closing PRs;
- changing branches or refs;
- staging, committing, pushing, merging, or deploying.

A user approving a re-slice does not implicitly authorize tracker restructuring, PR changes, source-code movement, or branch effects unless the approval explicitly covers them.

Unchanged approved routing or decomposition authority may be reused only within its existing scope.

## 10. Implementation scope

### Required skill changes

| Location | Change |
|---|---|
| `skills/productivity/plan-acceptance/SKILL.md` | Add R9–R12 routing assessment, durable `delivery-shape.md`, and a single conditional next-step handoff. Remove unconditional implementation wording that bypasses the route. |
| `skills/productivity/slice-contract/SKILL.md` | Implement R1–R8 and R15–R20. Accept any canonical work item, including an existing child, as a potential parent. Add local affected-subtree and in-flight-work rules. |
| `skills/productivity/slice-contract/references/sizing.md` — new | Compact merge/split decision guide, initial-sizing examples, adaptive re-slicing examples, and anti-fragmentation counterexamples. Core requirements remain in `SKILL.md`. |
| `skills/productivity/deliver-issue/SKILL.md` | Consume current routing/slicing records; recognize grounded post-planning sizing signals; return a precise re-slicing blocker; reject direct implementation of an active decomposed parent; recover the next ready leaf or parent-completion handoff. |
| `skills/productivity/implement-contract/SKILL.md` | Preserve partial work and report a grounded sizing concern discovered during direct implementation. Do not create children. Keep ordinary hard implementation on the current work item. |
| `docs/acceptance-contract-protocol.md` | Define leaf/parent role, nested decomposition, local re-slicing, report-history meaning, affected-subtree preservation, and parent verification after nested slicing. Keep copied protocol references consistent. |

`review-implementation` and `prove` need no new ownership role. Their existing reports may supply evidence consumed by `deliver-issue` or a later explicit `slice-contract` invocation. Update their docs only if necessary to make that handoff unambiguous without changing verdict semantics.

### Documentation changes

Update `README.md`, `docs/how-to.md`, and `docs/faq.md` to show:

1. user does not choose direct-vs-slice before planning;
2. `NO SPLIT` is a valid sizing result;
3. an oversized child can later become a parent;
4. unaffected siblings remain stable;
5. hard work is not automatically split;
6. P2P reports one immediate next action from the current tree.

### No new required product surface

Do not add:

- a new mandatory `audit-slicing` skill;
- story points, time estimates, or numerical size scores;
- a new tracker issue type or label;
- a scheduler or autonomous recursive execution engine;
- a new acceptance verdict;
- automatic PR/branch restructuring during re-slicing;
- a requirement that all epics be sliced or that all difficult work be recursively decomposed.

## 11. Behavioral scenarios

Extend the existing human-runnable scenario suites. Keep expected outcomes out of actor input. Capture exact agreements, decompositions, candidates, action logs, affected files, reports, and before/after identities.

### 11.1 Initial routing

**T22 — Small coherent parent**  
`plan-acceptance` recommends direct delivery with a grounded reason. No slicing record is required to make the work usable.

**T23 — Clearly broad parent**  
The contract spans materially distinct delivery mechanisms. Planning recommends `/slice-contract`, not direct delivery.

**T24 — Uncertain parent**  
Planning identifies the exact sizing uncertainty. `slice-contract` performs deeper inspection and returns either `NO SPLIT` or a justified decomposition without relying on a preselected ticket count.

**T25 — Pending approval**  
The contract looks direct or sliced, but approval is pending. The immediate next action is approval; the later route is stated conditionally and is not presented as authorized.

**T26 — Nested planner inside delivery**  
`deliver-issue` invokes missing planning. Direct assessment continues within the same delivery invocation; sizing assessment stops before implementation with the exact slicing handoff and no recursive delivery call.

### 11.2 First-pass right-sizing

**T27 — Artificial micro-tickets**  
A field/API/test/docs task list represents one coherent outcome. Slicing combines it before the first complete proposal.

**T28 — Hidden mini-epic**  
A short issue hides multiple material recovery/state mechanisms. Slicing identifies the actual burden and creates only the boundaries needed to make the work manageable.

**T29 — Good existing boundaries**  
A proposed decomposition already has justified manageable leaves. Preserve it rather than minimizing child count at any cost.

**T30 — Misleading size proxies**  
A many-file mechanical change stays together while a small concurrency/state change may split. Decisions rely on actual mechanisms and verification burden.

**T31 — Non-adjacent merge opportunity**  
Two fragments far apart in display order share one production path and proof setup. Merge them instead of checking only adjacent pairs.

**T32 — Necessary small migration stage**  
A small compatibility stage is retained because combining it would violate a real transition condition.

**T33 — Stable `NO SPLIT`**  
After deeper inspection returns `NO SPLIT`, an unchanged fresh delivery session uses that result and does not bounce back to slicing without new evidence.

### 11.3 Adaptive re-slicing

**T34 — Oversized child discovered before edits**  
Delivery inspection finds two separable mechanisms omitted by initial sizing. It returns a concrete `/slice-contract work/C.md` handoff. A/B are untouched.

**T35 — Hard but indivisible child**  
Implementation encounters a difficult algorithm or failing test with no useful separable outcome. It remains one leaf; no sizing escape hatch is used.

**T36 — Oversized child after partial implementation**  
Implementation has safe useful changes when a real boundary becomes apparent. The implementation result preserves the partial candidate/worktree, returns the sizing handoff, and later `slice-contract` records exact existing-work allocation without editing the code.

**T37 — Evidence appears during review/proof**  
A review or proof observation exposes a structural boundary rather than merely a defect. The enclosing delivery workflow records the observation and recommends re-slicing only when the separability criterion is met. An ordinary defect still routes to implementation/repair.

**T38 — Local nested split**  
Top-level parent has A/B/C. Re-slicing C creates C1/C2, keeps A/B bytes, contracts, links, reports, and tracker state unchanged, keeps C's contribution to the top-level parent unchanged, and maps C1/C2 only through C.

**T39 — Nested parent completion**  
C1 and C2 each complete, but their interaction violates C. C remains unproven until one exact assembled C candidate passes full C review/proof. Top-level parent acceptance remains separate.

**T40 — Existing mixed PR/worktree**  
C has an open PR or local candidate containing future C1/C2 changes. Saving the decomposition causes no PR/ref/code mutation. The plan records what is attributable, shared, contaminated, or unresolved and the exact authorized follow-up required.

**T41 — Merge undersized untouched siblings**  
Two planned/unstarted children are shown by later evidence to be one economical leaf. Re-slicing previews consolidation, preserves identities/history, and demonstrates the avoided delivery-cycle overhead. Repeat after one child is completed: default behavior preserves the completed child instead of rewriting history for aesthetics.

**T42 — Recursive fragmentation guard**  
C was split into C1/C2. C1 is still difficult but has one indivisible outcome. Another slicing invocation returns `NO SPLIT` or a concrete blocker instead of producing arbitrary C1a/C1b.

### 11.4 Ergonomic tree recovery

**T43 — User invokes an ancestor path**  
A fresh session receives only `work/Parent.md` after nested re-slicing. It recovers the active tree and names the next ready leaf, unresolved prerequisite, or parent-completion step without requiring the user to know the child path.

**T44 — User invokes converted child-parent C**  
With C1 remaining, `/deliver-issue work/C.md` does not reimplement C. It routes to the applicable ready descendant or blocker. After descendants are complete, it identifies C parent verification/assembly rather than another leaf implementation.

**T45 — Routing disagreement without loop**  
Current `NO SPLIT` says direct, but delivery discovers genuinely new sizing evidence. The handoff cites that evidence. If slicing still concludes `NO SPLIT`, it records the disagreement and concrete blocker/decision rather than creating an endless direct→slice→direct loop.

### 11.5 Authority and preservation

**T46 — Draft re-slice**  
A re-slice requested as draft performs inspection and saves only permitted planning records. It does not create grandchildren, change parent/child files, mutate issues, PRs, refs, or code.

**T47 — Approved local re-slice**  
Under explicit local allocation authority, create grandchildren and update the child-parent hierarchy with readback. No external effects occur.

**T48 — Tracker hierarchy unavailable**  
Canonical nested local work succeeds. If configured publication requires unsupported native nesting, follow the existing fallback/block rules honestly rather than flattening the canonical hierarchy or claiming success.

## 12. Validation strategy

### 12.1 First-proposal quality

Compare the baseline and revised installed skills on identical disposable fixtures. Capture the first complete routing/slicing proposal before corrective feedback.

Measure:

- unnecessary child boundaries;
- oversized leaves that later need re-slicing;
- lost or duplicated obligations;
- extra delivery cycles implied by the proposal;
- corrections required before delivery;
- unsupported or generic reasons for boundaries.

Do not bake arbitrary target child counts into fixtures. The evaluator should judge whether each boundary is materially justified and whether a credible lower-count decomposition was missed.

### 12.2 Adaptive correction quality

Seed intentionally imperfect initial decompositions, then expose controlled new evidence during implementation/review/proof.

Check that the revised workflow:

- distinguishes structural sizing evidence from ordinary defects;
- localizes re-slicing to the smallest affected subtree;
- preserves unaffected siblings and in-flight work;
- avoids duplicate code/PR effects;
- preserves exact historical report meaning;
- gives one actionable handoff;
- avoids recursive fragmentation and routing loops.

### 12.3 Delivery reality check

Exercise representative work through real supported delivery flows:

1. one task that remains unsliced;
2. one task that is correctly sliced initially;
3. one task with an intentionally oversized child that is re-sliced after partial implementation;
4. one intrinsically hard task that must remain one leaf.

For each, retain actual stage outcomes, repairs, re-slicing, human intervention, available elapsed time/usage information, and final parent verification.

Compare complete delivery episodes, not model-call count or initial ticket count alone. Fewer planned children is not an improvement if it produces repeated failure or expensive rework; more children is not an improvement merely because each ticket looks simpler.

### 12.4 Regression and packaging

Run the affected existing planning, slicing, delivery, implementation, review, proof, publication, readiness, and epic-delivery scenarios.

Install changed skill packages independently through the supported installation path. Verify bundled references and copied protocol bytes. Standalone packages must not depend on sibling source-skill directories.

Record unavailable live GitHub or host checks as unexecuted rather than simulated successes.

## 13. Acceptance conditions for this proposal's implementation

The implementation is ready for acceptance evaluation when:

1. acceptance planning reliably produces a grounded direct-vs-sizing recommendation and one next action;
2. the slicer demonstrates the fewest-defensible-child behavior on over-sliced, under-sliced, and already-good fixtures;
3. an existing child can be re-sliced locally without disturbing unaffected siblings;
4. in-flight work is retained and explicitly allocated rather than silently moved or lost;
5. hard-but-indivisible work does not trigger arbitrary recursive slicing;
6. active nested parents are not accidentally treated as implementation leaves;
7. child-to-parent and parent-to-grandparent proof semantics remain intact;
8. current approval, authority, exact-identity, publication, review, proof, and merge-readiness rules remain unchanged unless explicitly specified here;
9. first-proposal and adaptive-correction validation is retained with honest limits;
10. documentation makes the workflow understandable without requiring the user to memorize routing rules.

## 14. Non-goals

This proposal does not promise:

- perfect effort prediction;
- no future re-slicing;
- a globally minimal mathematical partition;
- automatic execution of every next action;
- automatically parallelizing children;
- automatic code extraction from a partially implemented parent;
- automatic PR retargeting or closure;
- automatic acceptance of a parent from child verdicts;
- replacing product decisions with model judgment;
- weakening review, proof, approval, CI, compatibility, safety, or external-effect authority.

## 15. User experience target

The developer should be able to think in terms of the work, not the workflow graph.

Typical interaction:

```text
/create-parent-issue ...
/plan-acceptance ...
```

P2P then says exactly one of:

```text
Next: /deliver-issue work/foo.md
```

or:

```text
Next: /slice-contract work/foo.md
```

If delivery later learns that `foo-child-c` is the outlier, it says:

```text
This leaf should be reconsidered because <concrete sizing evidence>.
Existing work is preserved at <references>.
Next: /slice-contract work/foo-child-c.md
```

After re-slicing, invoking an ancestor path should recover the current tree and continue guiding the user to the next relevant leaf or parent-completion step.

The intended mental model is therefore:

> **Give P2P the work. P2P chooses the current delivery shape, minimizes unnecessary children, and corrects local sizing mistakes when new evidence appears. You make the product decisions and approve consequential changes.**

## 16. Change notes

- **v1.0:** Proposed explicit right-sizing inside `slice-contract`, optimizing for the fewest manageable children.
- **v2.0:** Added lightweight `plan-acceptance` routing so users do not need to know whether to slice before invoking delivery.
- **v3.0:** Adds adaptive local re-slicing, stable leaf-to-parent conversion, in-flight-work preservation, merge-after-the-fact constraints, recursive-fragmentation guards, and consistent tree-aware next-step routing.

## 17. Source references

These are implementation context, not proof that this proposal has been implemented:

- [S1] `skills/productivity/slice-contract/SKILL.md` — existing decomposition, `NO SPLIT`, coverage, dependency, publication, and parent-completion rules.
- [S2] `skills/productivity/create-parent-issue/SKILL.md` — originating issue is deliberately not a decomposition step.
- [S3] `docs/acceptance-contract-protocol.md` — contract ownership, parent/child semantics, exact identities, delivery plans, history, and parent verification.
- [S4] `skills/productivity/deliver-issue/SKILL.md` — single-work-item delivery, planning orchestration, oversized/unresolved guard, independent review/proof, and repair limits.
- [S5] `skills/productivity/implement-contract/SKILL.md` — one child contribution, partial work preservation, development evidence, and implementation handoff.
- [S6] `skills/productivity/review-implementation/SKILL.md` and `skills/productivity/prove/SKILL.md` — review/proof ownership and exact-candidate semantics.
- [S7] `checks/slice-contract-scenarios.md`, `checks/plan-acceptance-scenarios.md`, and `checks/deliver-issue-scenarios.md` — existing human-runnable behavioral evaluation conventions.
- [S8] `plans/right-sized-slicing-spec.md` v2 at baseline `357bf61992d960d60014c6531152330021847139` — superseded proposal whose R1–R12 identities are retained here.
