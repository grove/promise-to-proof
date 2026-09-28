# Acceptance contract: frozen delivery bases under moving targets

Contract revision: v2
Source: [Frozen delivery base specification, version 1.0](../plans/frozen-delivery-under-moving-targets.md); imported issue text below.
Source attribution: https://github.com/grove/promise-to-proof/issues/37, updated 2026-09-27T13:07:41Z, author grove, retrieved 2026-09-27. The authoritative specification is `plans/frozen-delivery-under-moving-targets.md` at commit `39cf3a96aaf89789fceed9b0454682f9e88bc0b8`, SHA-256 `c570232a7371a53fd6dad954ec9d53f7940ecba171b3a2080fd995a6bd9a77d2`. No issue comments, approvals, amendments, prior contract, or decomposition were present at retrieval.
Parent: None
Prerequisites: None

Intended outcome: A delivery can reach matching REVIEWED and PROVEN results for its exact agreement and candidate against its admission-time comparison base while the destination continues moving. Completion states what was accepted and leaves compatibility with the newer destination to publication and merge readiness.

Advisory learnings: None. No advisory learning register is present.

This is an unapproved proposal. The unsliced admission decision is resolved by the user clarification retained below. In the matrix, `spec` means the linked version 1.0 specification; its R and T identifiers remain source identifiers. C, S, and M below name planned evidence cases, not completed checks.

## Acceptance matrix

| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | spec R1, sections 6 and 13.1, T1; planning clarification below | New admission resolves the approved destination to a full current commit SHA and rejects a requested comparison base that differs before dispatch. | Missing or conflicting routing stays blocked. A stale-start blocker names the actual destination and current SHA and directs a new delivery using that SHA. For unsliced work use an explicit workflow destination, otherwise an unambiguous configured upstream; if neither is established, block before dispatch with a setup instruction. Never infer a destination solely from the requested SHA. | Controller `run` and delivery destination selection | The independently created fixture ref and its tip at admission | C:T1 asserts zero worker dispatches for requested A versus actual B; valid admission records B. Exercise grouped child, independent child, assembled parent, and unsliced admission with explicit destination, upstream fallback, missing/ambiguous context, and stale requested base. | planned |
| R2 | spec R2, R7, sections 6 and 13.2 | The comparison base persisted at admission is immutable for that invocation and is reused on resume. | A repeated `run` requesting B cannot replace persisted A. Ref movement, missing ref, restart, or legacy recovery cannot silently rewrite A. | Controller `run`/`resume`, admission and delivery records | Exact fixture admission SHA A | C:T5 and a repeated-run base-replacement case compare persisted identities before and after restart and reject B without dispatch. | planned |
| R3 | spec R3, sections 6 and 13.3, T2–T4, T6–T7, T12 | Destination movement alone does not prevent implementation, candidate capture, review, proof, saved-report reuse, or matching REVIEWED and PROVEN completion against the frozen base. | Include fast-forward, non-fast-forward, deleted/unresolvable ref, and repeated movement. All actual agreement, candidate, routing, and retained-base inputs remain valid. | Controller `run`/`resume`/`status` through lifecycle boundaries | Successful fixed-input delivery against A with independently moved destination refs | C:T2–T4, T6–T7, T12 assert successful completion, unchanged fixed identities, and valid retained reports while moving only the target ref. | planned |
| R4 | spec R4, R7, sections 10 and 13.4–5, T8–T10 | Actual candidate, agreement, binding-input, approved-routing, report, evidence, or retained-base integrity failures continue to invalidate reuse or block the affected delivery under existing rules. | Movement cannot mask simultaneous drift. Same-revision contract edits, lost candidate recovery content, changed plan approval evidence, mismatched report identities, missing/changed evidence, and explicit base substitution remain failures. | Controller resume/status validation and stage report admission | Independently changed or removed fixture input and the prior exact admission/report identities | C:integrity cases retain existing drift tests and add movement alongside each fault; T8, T9, T10 reject reuse without returning successful acceptance. | planned |
| R5 | spec R5, section 7, section 13.10 | Delivery-launched review uses the authoritative frozen comparison base from a validated delivery/candidate handoff. | A later target tip is an observation, never a substitute review base; an unvalidated arbitrary base cannot authorize REVIEWED. | Review stage prompt, review-implementation invocation, saved comparison scope | Admitted A, candidate C, validated handoff, and independently known diff C against A | S:delivery-review supplies A and later target B; inspect the actual review and its saved scope for C against A. C:T2–T4 check the controller's dispatched identity. | planned |
| R6 | spec R6, sections 5 and 13.4 | Proof remains bound to the exact agreement and candidate despite destination movement. | Report identity mismatch still fails. Proof must not claim verification of later destination commits absent from the candidate. | Proof invocation and retained proof report | Exact agreement hash and candidate manifest, with B-only content absent from C | S:proof-boundary and C:T3–T4 inspect bindings and the retained proof conclusion after target movement. | planned |
| R7 | spec R7, section 10, T5 | Resume continues only missing stages and reuses valid completed reports without chasing the destination. | Interrupted and already-complete runs; repeated resume; moved destination; unavailable observation. Movement alone cannot add review/proof dispatches or consume repair allowance. | Fresh-process controller `resume` and attempt records | Saved stage completion/receipt state before restart | C:T5 interrupts at existing receipt boundaries, moves A to B, resumes in a fresh process, and asserts only missing stages dispatch; repeat resume of a completed run with no new attempts. | planned |
| R8 | spec R8, section 6, section 13.6 | Retain a point-in-time destination observation separately from candidate and report identity, classifying it as unchanged, fast-forward, non-fast-forward, or unavailable relative to the frozen base. | Observation failure alone leaves a recoverable delivery valid. Observation updates do not change the base, candidate/report identities, or acceptance status. No continuous monitoring is required. | Controller retained records and public result | Known fixture Git ancestry or deliberately absent ref, plus recorded observation time | C:observations and T2, T6, T7, T12 assert all four classifications, destination, frozen SHA, observed tip when available, and observation time; compare fixed identities before and after. | planned |
| R9 | spec R9, section 13.12 | Successful completion clearly distinguishes acceptance against the frozen base from unestablished compatibility with a newer or unavailable destination. | Keep the successful acceptance outcome. Do not call the candidate stale, unreviewed, unproven, or merge-ready solely because the target moved. | Controller completion result and delivery skill's human-facing handoff | Candidate C accepted against A; later B was not included or verified | C:T4, T6, T7, T12 inspect completion fields; S:completion-boundary checks candidate, base, destination observation, and explicit integration limitation in the human handoff. | planned |
| R10 | spec R10, sections 5 and 12, T11 | Target movement alone causes no automatic rebase, merge, conflict resolution, candidate rebuild, base refresh, or verifier restart. | An explicitly authorized later integration that changes the candidate requires fresh applicable review and full proof; old reports remain historical. | Delivery execution, retained candidate/attempts, and later integration handoff | Fixed C/A identities and dispatch history; separately transformed candidate C2 | C:T3, T5, T12 assert no candidate/base mutation or extra verification dispatch; T11 demonstrates C2 cannot reuse C's current acceptance. | planned |
| R11 | spec R2, R4, section 6, T10 | The frozen comparison-base commit and required bytes remain recoverable and validated independently of the mutable destination ref. | Deleting or moving the destination cannot erase retained A. Missing, corrupt, or replaced required base manifest/bundle/Git material blocks reuse. | Existing retained base manifest, bundle, candidate recovery, and controller validation | Original full SHA and independently captured tree of A | C:T7 and T10 extend retained-base reconstruction into a fresh repository, validate recovered A after target loss, then reject corruption, replacement, and loss of required recovery material. | planned |
| R12 | spec R5 and section 7 | A new direct review without an admitted delivery resolves the intended current target and freezes its exact tip when review scope is established. | Do not borrow a historical delivery base without a validated handoff. Later ref movement alone does not replace captured scope; changed candidate, agreement, approved destination, or adopted base requires applicable fresh verification. | Direct review-implementation invocation and saved review scope | Intended target B at scope capture, then independently moved target D | S:direct-review captures B, moves the target during review, and verifies fixed B in the saved comparison; changed-input variants withhold reuse. | planned |
| R13 | spec section 11 | A legacy run blocked only by target movement may resume only when its persisted identities and retained comparison-base material validate. | Do not reconstruct missing historical authority or base identity from the current destination. Incomplete or corrupt legacy state remains blocked. | Controller `resume` with retained pre-change delivery records | Recoverable old admission A and matching agreement/candidate/report records | C:legacy-resume loads pre-change-format records blocked on A-to-B movement; the intact case continues against A, while missing/mismatched admission or recovery material blocks before dependent dispatch. | planned |
| R14 | spec section 11 | Existing commands require no new mandatory arguments. | `--comparison-base` remains the exact new-admission base and cannot alter an existing invocation. Unsliced destination resolution adds no required destination flag. | Public controller CLI and documented skill invocations | Existing run/resume/status argument shapes | C:CLI-compatibility exercises unchanged invocation shapes, plus R1/R2 admission and resume assertions. | planned |
| R15 | spec sections 9 and 11 | Existing report verdict names and successful controller outcome remain unchanged. | Observation classifications are informational, not new acceptance verdicts. | Public result, review and proof reports | Existing REVIEWED, PROVEN, and REVIEWED_AND_PROVEN vocabulary | C:T2–T7 and T12 assert the existing success outcome and report statuses; inspect schemas and documentation for verdict compatibility. | planned |
| R16 | spec section 8 and section 13.7–8 | The bounded delivery model separates mutable destination state from the persisted admission base and requires both verifier bindings to match that admission base at completion. | Destination movement cannot modify admission identity; mismatched review or proof base cannot pass the invariant. | `delivery.fizz` state, transitions, completion assertion, and runner's trace checks | Both independently inspected binding base values equal the saved admission value | M:baseline explores the revised model; inspect both verifier bindings in every successful trace and the invariant, including mismatched-binding cases. | planned |
| R17 | spec section 8 and section 13.7 | The bounded model retains a successful witness where the destination moves after verification launches, both verifiers finish against the original base, and reports/evidence are saved and reread before completion. | A trace moving only before admission or after completion does not qualify. The witness shows reachability within stated bounds, not universal eventual termination. | Existing model witness runner and ordered trace artifacts | Required action ordering and terminal fixed-input identities from the specification | M:moving-target witness checks launch, target movement, verifier returns, durable readback, and complete against A with destination B. | planned |
| R18 | spec section 8 and section 13.8 | Model mutations continue to demonstrate that changing or ignoring actual persisted comparison-base identity permits an invalid completion rejected by the safety invariant. | A parse error, unrelated assertion failure, or branch movement alone is not the required counterexample. Preserve independent assertions when weakening guards. | Existing mutation runner and concrete terminal trace checks | Accepted mismatched base versus original admission identity, independently of the weakened completion guard | M:base-mutations require the named invariant failure and inspect the violating base facts, including either verifier's mismatch. | planned |
| R19 | spec section 5 and section 12 | Publication retains its current-target and exact candidate/review-scope checks. | Acceptance against A alone does not authorize publication against B; changed publication inputs require the existing fresh preview and verification. No publication authority is added. | Existing publish-pr preview and drift scenarios | Current publication rule requiring target tip to match fixed review comparison scope | S:publication-boundary uses existing publish-pr scenarios 4 and 9 with accepted C/A and target B, expecting a blocked or refreshed preview, never stale publication. | planned |
| R20 | spec section 5, section 13.11 | Merge readiness retains checks of actual PR head and current target, matching verification, current CI, repository approvals, and merge rules. | Frozen-base acceptance does not imply future compatibility or merge authority. A changed integration candidate receives applicable fresh verification. | Existing merge-readiness scenarios and handoff | Current PR/candidate identities and independently supplied gate observations | S:readiness-boundary uses existing merge-readiness scenarios 2–4 with target/head drift and missing CI/approval gates; no unsupported READY conclusion or merge effect. | planned |
| R21 | spec sections 6–10, section 13.9–12, issue scope | Controller documentation, delivery/review instructions, and the shared protocol consistently describe admission-time freezing and later observational movement, while preserving publication/readiness boundaries. | Unconditional instructions to refresh a valid admitted review solely on target advance are contradictory. Required T1–T12 controller cases must be distinguishable and mapped to assertions. | Repository instructions, protocol references, controller scenario suite, and model documentation | This contract and specification sections 9 and 13 | S:documentation trace maps each T1–T12 to executable controller assertions and inspects all delivery/review/protocol target-advance guidance plus model bounds and evidence descriptions. | planned |

## Evidence plan

C uses `checks/test_p2p_delivery.py` through the production controller's `main` entry point and fresh-process helpers. Extend the existing `test_child_target_advance_and_wrong_explicit_base_block`, receipt-resume, recovery, and drift fixtures. Run `python3 checks/test_p2p_delivery.py`. The source's T1–T12 are mandatory cases; multiple requirements can share one case. Use real disposable Git objects and refs. Substitute only the existing worker transport and record that limitation. These tests establish controller behavior, not an agent's review judgment or live-host isolation.

S uses the existing human-runnable skill scenario conventions in `checks/review-implementation-scenarios.md`, `checks/proof-repair-scenarios.md`, `checks/deliver-issue-scenarios.md`, `checks/publish-pr-scenarios.md`, and `checks/merge-readiness-scenarios.md`. Add the named lifecycle cases to the appropriate existing scenario files. At verification, invoke the actual candidate skill instructions in isolated fixtures, keep expected outcomes outside their input, and retain actual outputs and identity comparisons. Supply controlled read-only PR/gate observations for publication/readiness cases. No real publication or merge is needed. Text search alone does not establish the review-mode behavior in R5 or R12.

M uses the existing pinned FizzBee runner: `python3 checks/delivery-model/check.py --fizz "$FIZZBEE"`, where FIZZBEE names the verified v0.5.3 macOS arm64 executable documented in `checks/delivery-model/README.md`. Keep the existing runner's binary validation, bounded exploration, named assertion checks, and concrete trace inspection. Retain the moving-target witness and actual base-mismatch mutation traces. Do not substitute fixture-controller results for model exploration or claim a bound stronger than the explored model.

At proof time, record commands, assertions, actual observations, environment, and exact candidate identity in `.p2p/work/frozen-delivery-base/proof.md`; retain replayable model traces under its `evidence/` directory. No tests, stage invocations, or acceptance proof are performed by this plan.

## Unresolved gaps

- None in the identified evidence paths. New scenarios and model cases are planned work, not existing passing evidence. The unsliced admission decision is resolved below.

## Open questions

- None. Exact contract approval remains pending.

## Out of scope

- Automatic rebasing, merging, conflict resolution, candidate rebuilding, comparison-base refresh, or verifier restart solely for destination movement.
- Repository-wide locking, continuous destination monitoring, or a requirement that the repository stop changing.
- Proving compatibility with arbitrary future destination commits, guaranteeing conflict-free later integration, weakening publication/readiness gates, or granting merge authority.
- New required command arguments, new verdict names, generic routing infrastructure, or unrelated controller/host redesign.

## Change notes

- v2 clarifies R1 and its R8/R14 boundaries under the exact user decision retained below. The prior v1 left unsliced destination resolution as Q1; v2 requires an explicit workflow destination or unambiguous configured upstream and blocks when neither is established. No requirement IDs change. The unpublished v1 bytes are retained under `.p2p/work/frozen-delivery-base/history/18656d2203d78d76d0740ab4dc1a69e50b3b5dbd365048ca3ba49185d1ca99fe/frozen-delivery-base.md`.
- Initial v1 proposal from issue #37 and its exact version 1.0 specification. The planning request authorizes this proposal and its issue handoff, not approval or implementation.
- R1–R10 retain the corresponding source R1–R10 topics. The source's compound promises are separated without changing their meaning: R2/R4 recovery becomes R11; R5 direct review becomes R12. Source section 11 maps to R13–R15; section 8 maps to R16–R18; publication/readiness map to R19–R20; instruction and scenario consistency maps to R21. No prior contract IDs exist or are retired.
- Source acceptance conditions 13.1–13.12 map respectively to R1; R2; R3/R7/R10; R5/R6; R4/R11; R8; R16/R17; R18; R1/R3/R21; R5/R12; R20; R9/R21. T1 maps to R1; T2–T4 to R3/R5/R6/R8/R9; T5 to R2/R7; T6–T7 to R3/R8/R9/R11; T8–T10 to R4/R11; T11 to R10/R19/R20; T12 to R3/R7/R8/R9/R10.
- The current protocol and review/delivery instructions treat some destination advances as requiring fresh review. The requested lifecycle distinction is the proposed change to that guidance. Publication's current-target equality rule remains binding under R19. Existing unrelated agreements are not silently revised.

## Planning clarification

Source: User decision in the planning conversation on 2026-09-27, response to `request_user_input_async` call `call_AMcJo3OYbsQ3dhkWkfdYZAS7`, question 0.

Exact question: "Use this rule for unsliced runs: resolve an explicit workflow destination or an unambiguous configured upstream, block before dispatch if neither can be established, and add no required CLI argument?"

Exact response: "Yes, include that rule in the proposal."

R1 uses an explicit workflow destination when supplied and otherwise an unambiguous configured upstream. Missing or ambiguous destination context blocks admission with a setup instruction. This authorizes the proposal's admission rule; it does not approve the full acceptance contract or authorize implementation.

## Implementation handoff

Hand off to an explicitly authorized /implement-contract invocation after the exact proposal is approved.
Implement the smallest complete solution inside the spec envelope.
Preserve requirement IDs and promised outcomes.
Capture the resulting candidate for separate /review-implementation and /prove phases.

## Proof handoff

Evaluate every requirement against this contract revision and one fixed candidate.
Record actual evidence and verdicts in a separate proof report.

## Imported issue source

The following issue body is retained verbatim as retrieved from issue #37. Its linked specification above is authoritative. Issue labels are not approval or readiness evidence.

<!-- issue-body-start -->
Let `deliver-issue` reach REVIEWED + PROVEN while its destination branch continues moving.

Resolve the approved destination's current tip at admission, reject a mismatched requested base, and persist that exact comparison base for the invocation. Resume and delivery-launched review must reuse the validated frozen base. Direct review captures the current target when its scope is established.

After admission, destination movement alone must not invalidate implementation, candidate capture, review, proof, saved reports, resume, or completion. Record destination observations separately as unchanged, fast-forward, non-fast-forward, or unavailable. Completion must distinguish acceptance against the frozen base from compatibility with the newer destination.

Preserve checks for candidate, agreement, binding-input, approved routing, report, evidence, and retained-base integrity. Reject attempts to replace an existing invocation's base. Legacy runs may resume only when their persisted identities and retained base material validate.

Scope includes the delivery controller, review instructions, protocol documentation, controller scenarios T1–T12, and bounded delivery model. Model the frozen admission base separately from the mutable destination, demonstrate completion during target movement, and retain mutations detecting actual base-identity mismatches.

No new required command arguments or verdict names. No automatic rebasing, merging, conflict resolution, base refresh, verifier restart due solely to target movement, repository-wide locking, or requirement for repository inactivity.

Publication and merge readiness retain their current-target, candidate, CI, approval, and merge-rule checks. Acceptance does not establish compatibility with future destination commits or grant merge authority. Later candidate transformations require the applicable fresh verification.

The linked specification is authoritative source material for `plan-acceptance`. This issue is not an approved acceptance contract or implementation-readiness decision.

Source:
- [Frozen delivery base under moving targets, version 1.0](https://github.com/grove/promise-to-proof/blob/39cf3a96aaf89789fceed9b0454682f9e88bc0b8/plans/frozen-delivery-under-moving-targets.md)
- Repository: grove/promise-to-proof
- Path: plans/frozen-delivery-under-moving-targets.md
- Commit: 39cf3a96aaf89789fceed9b0454682f9e88bc0b8
- SHA-256: c570232a7371a53fd6dad954ec9d53f7940ecba171b3a2080fd995a6bd9a77d2

<!-- grove:create-parent-issue source=grove/promise-to-proof:plans/frozen-delivery-under-moving-targets.md -->
<!-- issue-body-end -->
