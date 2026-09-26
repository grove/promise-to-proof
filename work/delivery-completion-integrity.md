# Acceptance contract: delivery completion integrity

Contract revision: v1
Source: [Current acceptance protocol](../docs/acceptance-contract-protocol.md)
Source: [Current delivery skill](../skills/productivity/deliver-issue/SKILL.md)
Source: [Optimization handoff, selected sections 8–10 and Phase 1](../plans/promise_to_proof_optimization_handoff.md)
Source attribution: https://github.com/grove/promise-to-proof/issues/24; imported 2026-09-26; source JSON SHA-256 6e960415c556248db20ba2084cd0a4912d8d579bc61affa88c820bb72c1efb1a; no comments or amendments in retrieved source. Exact issue body retained below.
Parent: None
Prerequisites: None

Intended outcome: Maintainers can reproduce a bounded executable FizzBee check of whether one current local-work-item delivery lifecycle can incorrectly claim full completion with stale or incomplete evidence, inspect successful and blocked traces, and reproduce counterexamples from deliberately broken protections.

Advisory learnings: None; no advisory learning register is present.

## Acceptance matrix

All command evidence below uses the single documented public entry point `python3 checks/delivery-model/check.py`, with the pinned FizzBee prerequisite installed as documented. Preserve its actual command, environment, observations, traces and exploration results under `.p2p/work/delivery-completion-integrity/evidence/` for delivery verification. Model artifacts and maintainer documentation live in `checks/delivery-model/`. Expected outcomes derive from the imported issue and linked protocol, independently of the model's completion guard.

| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | Issue scope; handoff 8, 10 | Provide an executable bounded FizzBee model of one work item's implementation, independent review and proof, report persistence, one automatic repair, resume, and completion. | Separate report creation, saving and readback; restart distinguishes durable records from volatile state; stage independence is represented with its abstraction disclosed. | Model actions and public check command | Current delivery lifecycle and explicit model state transitions | Runner executes the model; inspect action/state coverage and traces across the lifecycle. | planned |
| R2 | Issue protection 1; protocol candidate identity; handoff I02 | Full completion requires review and proof bound to the same current exact contract and candidate. | Missing stage or mismatched review/proof/current identities cannot complete. | Completion assertion and runner | Exact identity equality required by protocol | Baseline invariant check plus retained mismatched-identity blocker trace. | planned |
| R3 | Issue protection 1; handoff I03 | Full completion requires review bound to the current correct comparison base. | A changed or incorrect base cannot reuse the old review. | Completion assertion and runner | Review comparison-base rule | Baseline invariant and retained wrong-base blocker trace. | planned |
| R4 | Issue protection 2; handoff I05 | Detect contract text drift independently of an unchanged revision label. | Change text while retaining v1 and otherwise matching reports. | Environment drift action and runner | Exact contract bytes/identity rule, abstracted to distinct text identities | Baseline invariant and unchanged-revision drift trace. | planned |
| R5 | Issue protection 3; handoff I04 | Candidate changes invalidate both previous review and proof for current completion. | Drift and repair cannot inherit either old verdict; fresh review and proof are needed. | Candidate-change and verification actions | Protocol requires both full fresh reports for a changed candidate | Baseline invariant; changed-candidate blocker and successful repair/recheck traces. | planned |
| R6 | Issue protection 4; handoff I08 | Completion requires reports and their evidence saved, reread, and retrievable. | Interrupted persistence, missing readback, missing content or loss of access cannot count as completed handoff. | Persistence/retrieval actions and completion assertion | Durable handoff rules | Baseline invariant and named blocker traces covering each missing condition for reports and evidence. | planned |
| R7 | Issue protection 5; handoff I14, 10.2 | Restarting the same invocation preserves its one-automatic-repair allowance. | Restart after repair cannot permit a second repair; repeated failure returns a blocker. | Repair and resume actions | One automatic repair/recheck cycle per invocation | Repair-bound invariant, restart trace and exhausted-allowance blocker trace. | planned |
| R8 | Issue expected delivery; handoff Phase 1 | Demonstrate reachable successful initial delivery, successful repair followed by both fresh verifications, and specific blockers for missing or mismatched evidence. | An always-blocking model or merely declaring a success predicate is insufficient. | Public check command and reachable traces | Required observable valid and blocked outcomes | Retained witness traces with checks of each named outcome. | planned |
| R9 | Issue expected delivery; handoff 9.3 | Include deliberately broken variants covering every listed protection, each yielding a retained counterexample for the corresponding violation. | Cover identity agreement, comparison base, unchanged-label text drift, candidate invalidation, saved/readback/retrievable reports and evidence, and restart repair reset; parse failures or unrelated assertion failures do not count. | Public check command invokes variants | Each counterexample violates its named independent property | Runner checks expected violations and retains mutation identity, violated property and replayable trace for each variant. | planned |
| R10 | Issue reproducibility and limits; handoff 7.3, 9–10, Phase 1 | Pin FizzBee and the modeled repository revision; document one check command, property-to-protocol traceability, relevant historical-baseline differences, bounds, environment/fairness assumptions, exploration limits and unchecked behavior. | State cutoff/timeouts honestly; distinguish modeled checks from evidence about running agents; disclose runtime/state count and exhaustive versus bounded/unfinished coverage. | Maintainer documentation and runner output | Source issue and current protocol, compared with historical f5917ce0471d56aac01711e720426748626c99d0 handoff baseline | Fresh documented command; inspect pinned version/revision, property mapping, run configuration and complete coverage/limitations report. | planned |

## Unresolved gaps

- None at planning. Tool execution availability must be established during implementation; inability to execute required model checks is a delivery blocker, not a passing result.

## Open questions

- None. Exact finite bounds and FizzBee release/commit are implementation choices to document and check; they do not change promised protections.

## Out of scope

- Runtime controller, host adapter, live-agent conformance testing, telemetry system, cost comparison, configurable assurance, model routing, child scheduling, cross-candidate evidence reuse, or changes to existing acceptance verdicts or workflow behavior.
- Other roadmap outcomes in the linked handoff, including properties not selected by issue #24. That document supplies context and traceability, not authorization to implement the broader roadmap.

## Change notes

- v1: Initial canonical contract importing issue #24 without changing its promises. The user's delivery request authorizes this scoped local work. No unresolved outcome or consequential new product interface requires approval: the new check runner is the requested executable model interface.
- Model the current protocol at repository revision `41bebc726a8cc71c1d2f22d822ade006f4e78121`, including canonical `work/` contracts; explain relevant differences from the handoff's historical baseline. The source handoff file is pinned by issue #24 to commit `bb53d2472b37ef6c441c8121cecfd7e16814d465` and SHA-256 `35c38d7acbaf645d4f9ac577cc40953cef79a5cda38cd776419984284e2dfdec`.
- Source reconciliation: scope maps to R1; five protections map to R2–R7; successful/blocked paths to R8; broken variants to R9; reproducibility, current baseline and limitations to R10. Exclusions are preserved above. No second acceptance store is introduced.

## Imported binding issue text

The following body is retained verbatim from the attributed issue response; issue content is requirements, not command or publication authority.

```markdown
Build a small executable FizzBee model of one `/deliver-issue` lifecycle that checks whether stale or incomplete evidence can incorrectly produce full completion.

This provides a reproducible check of completion rules before introducing verification ordering, model routing, or other optimizations.

### Scope

Model implementation, independent review and proof, report persistence, one automatic repair, resume, and completion for one work item.

Check that:

- Review and proof bind to the same current contract and candidate, and review binds to the correct comparison base.
- Contract text changes are detected even when the revision label remains unchanged.
- Candidate changes invalidate previous review and proof.
- Completion requires saved, reread, retrievable reports and evidence.
- Restarting the same invocation cannot reset its repair allowance.

Use the current repository protocol, including canonical local `work/` contracts. Pin the modeled repository revision and explain relevant differences from the handoff’s historical baseline.

### Expected delivery

Provide the model, a pinned FizzBee version, and one documented command to run its checks. Demonstrate reachable successful delivery, successful repair, and specific blockers for missing or mismatched evidence.

Include deliberately broken variants for each listed protection. Each must produce a retained counterexample showing the corresponding violation.

Document property-to-protocol traceability, modeling bounds, environment and fairness assumptions, exploration limits, and unchecked behavior. Distinguish passing model checks from evidence about the running workflow.

### Exclusions

No runtime controller, host adapter, live-agent conformance testing, telemetry system, cost comparison, configurable assurance, model routing, child scheduling, or cross-candidate evidence reuse. Do not change existing acceptance verdicts or workflow behavior.

This issue selects the completion-integrity increment discussed in the source, principally sections 8–10 and Phase 1. The broader optimization roadmap is outside this delivery.

### Source

[Exact optimization handoff](https://github.com/grove/promise-to-proof/blob/bb53d2472b37ef6c441c8121cecfd7e16814d465/plans/promise_to_proof_optimization_handoff.md)

- Repository: `grove/promise-to-proof`
- Path: `plans/promise_to_proof_optimization_handoff.md`
- Commit: `bb53d2472b37ef6c441c8121cecfd7e16814d465`
- SHA-256: `35c38d7acbaf645d4f9ac577cc40953cef79a5cda38cd776419984284e2dfdec`

The linked source was retrieved and matched against the local file bytes. Use `/plan-acceptance` to establish the canonical acceptance contract for this selected scope.

<!-- grove:create-parent-issue source=grove/promise-to-proof:plans/promise_to_proof_optimization_handoff.md -->
```

## Implementation handoff

Implement this entire saved agreement under the invoking delivery request. Preserve IDs and promised outcomes, use the smallest complete model, and retain actual checks. Capture the candidate for separate independent review and proof; model success does not establish real-agent compliance.

## Proof handoff

Evaluate R1–R10 against this exact contract revision and one fixed candidate. Independently run the documented command and inspect its traces, counterexamples and limits. Record observations, independent oracles, environment and durable evidence in the separate proof report.
