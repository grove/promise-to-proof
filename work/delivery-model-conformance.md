# Acceptance contract: Test the delivery controller against the FizzBee model

Contract revision: v1
Source: [Pinned Phase 3 handoff](../specs/delivery-model-conformance-source.md)
Source: [Acceptance contract protocol](../docs/acceptance-contract-protocol.md)
Source attribution: [GitHub issue #30](https://github.com/grove/promise-to-proof/issues/30), imported 2026-09-26T14:34:22Z; issue body retained verbatim below. Import returned no comments. The pinned handoff is bound to repository commit `5c2c6b64b997dd2c04ac8ba85dcad8e08047eac2`, SHA-256 `7162a965fa53322a8805582756ea6137a847d72798e057dd751cc2e46c98f65a`.
Parent: None
Prerequisites: Phase 1 model and documented bounds in [checks/delivery-model/README.md](../checks/delivery-model/README.md), from issue #24; single-work-item controller and its fixtures in [p2p_delivery.py](../skills/productivity/deliver-issue/scripts/p2p_delivery.py), [test_p2p_delivery.py](../checks/test_p2p_delivery.py), and [check_p2p_delivery_host.py](../checks/check_p2p_delivery_host.py), from issue #28 and merged PR #29. These earlier phases are prerequisites, not an inherited parent contract.

Intended outcome: Repeatable FizzBee model-based tests drive the actual supported single-work-item delivery controller through its public operations, detect differences between modeled rules and controller behavior, and retain replayable evidence. Model checks, substitute-backed controller tests, and live-host observations remain distinguishable.

Advisory learnings: None; no advisory learning register is present.

## Acceptance matrix

| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | Issue #30; pinned handoff §19 Phase 3, F05 | Before choosing the adapter language, demonstrate that the pinned FizzBee model-based testing driver performs an adapter operation and catches a deliberately mismatched result. Record the language choice from that observed compatibility checkpoint. | A second model run or a handwritten action list disconnected from FizzBee driver operations does not establish compatibility. Do not choose the language before the checkpoint. If the required FizzBee tools are unavailable, record an execution blocker; that does not permit substituting a handwritten action list. | Pinned FizzBee v0.5.3 model-based testing driver invoking a scratch controller's public `status` or `run` operation | The driver's observed operation and its failure on a known mismatched result | First bounded task: use the installed tool at `/private/tmp/p2p-fizzbee-24/fizzbee-v0.5.3-macos_arm/fizz` if available, with a tiny scratch controller exposing public `status` or `run`. Retain the exact command, tool and binary hashes, adapter operation, mismatch, and failing output under `.p2p/work/delivery-model-conformance/evidence/`. Make the executable path configurable (for example, `FIZZBEE` or `--fizz`) and document the version and executable hashes for reproduction. This checkpoint does not require the full Phase 3 implementation. | planned |
| R2 | Issue #30; pinned handoff §19 Phase 3 | FizzBee-generated actions drive the actual controller through repeatable successful, failed, and restarted delivery sequences. Restart cases launch a fresh controller process and inspect both its returned result and persisted records. The one-repair bound persists across restart. | A modeled restart without restarting the controller, inspecting only worker output, or checking only returned output or only saved state is insufficient. Worker results may use existing substitutes where needed; those results do not stand in for controller execution. Restart must not reset a consumed repair allowance: no second repair may dispatch after restart. | Model-based adapter at the controller CLI; fresh-process `resume` operation | The model's declared transition and invariant, compared with controller output and saved state | Named cases `successful-delivery`, `blocked-failure`, `known-result-restart`, `uncertain-launch-restart`, and `repeated-resume`; assert the expected public result and corresponding persisted attempt, report, repair, and completion state. In `repair-restart-exhaustion`, consume the one repair, restart the controller, assert the repair allowance remains exhausted, and assert that resume dispatches no second repair. Reuse the existing temporary-repository fixtures and subprocess restart patterns in `checks/test_p2p_delivery.py`. | planned |
| R3 | Issue #30; pinned handoff §21.2 | Cover applicable conformance cases: unauthorized actions; stale or mistyped identities; candidate mutation during verification; incomplete archives; interrupted report storage; late results; duplicate writes; repeated resume; and contested dirty files. Extend the bounded model when a required case or controller behavior is outside its current scope. | Keep the model bounded and document its state abstractions, exploration limits, assumptions, and unchecked behavior. Existing model coverage is not presumed to include controller behavior. A changed candidate requires both full independent verifier reports—REVIEWED and PROVEN—against that candidate. No second repair may dispatch after restart once the one-repair allowance is consumed. Preserve exact identities, authorization, durable evidence, and unrelated work. No added host support is implied. | FizzBee action-to-controller mapping and each corresponding public controller operation | Contract/protocol identity and authorization rules; the controller's persisted state and returned blocker; and existing model invariants where applicable | Add named model-connected cases with assertions: `unauthorized-before-dispatch`, `stale-identity`, `mistyped-identity`, `candidate-mutated-during-verification`, `incomplete-archive`, `interrupted-report-storage`, `late-stage-result`, `duplicate-report-write`, `repeated-resume`, and `contested-dirty-file`. Assert authorization before dispatch and exact identity checks; in `candidate-mutated-during-verification`, assert that changed candidate identity prevents reuse of verifier reports and requires both full independent REVIEWED and PROVEN reports for the changed candidate. In `repair-restart-exhaustion`, assert after restart that no second repair dispatch occurs. For each case, retain the action sequence, controller invocation, expected oracle, actual result, and relevant saved-state observation. Update the model and traceability documentation only for cases outside its present bounds. | planned |
| R4 | Issue #30; pinned handoff §19 Phase 3 | Demonstrate that tests detect deliberate defects in real controller protections. At minimum, removing stale-report rejection must fail a conformance test that inspects the returned result and persisted state. | A mutation only to the model, adapter, expected value, or test harness is not a controller defect. Mutating a guard must not weaken the independent oracle. | Actual controller guard reached through the public CLI | The corresponding model invariant and expected controller outcome, independent of the mutated implementation | Named mutation `stale-report-guard-removed`: deliver a stale successful result after input drift; assert that the unmodified controller blocks it and that removing its real guard makes the test fail. Retain the mutation diff or reproducible mutation procedure, failing assertion/output, model trace, returned result, and persisted state. Apply the same method to other real guards exercised by the conformance suite where their mutation has a distinct oracle. | planned |
| R5 | Issue #30; pinned handoff §19 Phase 3 | Test overlapping controller operations at the supported public boundary where the selected host permits them, and record what the supported host can establish. | Do not claim overlap coverage from interleaved model actions alone. If the selected host cannot safely run an overlap case, state that limit and retain the available boundary-level result; do not add another host. | Concurrent invocations of the actual controller CLI, including `resume` where supported | Public results and persisted state showing that overlapping operations preserve the controller's admission and state invariants | Named case `concurrent-resume`: start overlapping fresh controller processes against one work item, then inspect each return value and the single persisted state. Reuse the existing subprocess concurrency fixture pattern in `checks/test_p2p_delivery.py`; label fixture transport as substitute-backed. Record the supported-host capability observation separately. | planned |
| R6 | Issue #30; pinned handoff §19 Phase 3 | Retain failure sequences another person can replay against the actual controller and its saved records. | A summary, model-only trace, or non-reproducible temporary path is not a replayable failure sequence. | Public controller CLI plus the FizzBee adapter/replay entry point | Re-execution produces the named controller observation and persisted-state assertion under the documented bounds | Save replayable FizzBee action traces and the exact command, fixture inputs, tool configuration, and assertion results under `.p2p/work/delivery-model-conformance/evidence/`. Provide a command/path for each retained counterexample or failure sequence; exclude machine-local installation paths from required inputs. | planned |
| R7 | Issue #30; pinned handoff §21.2; current delivery protocol | Distinguish model-check results, substitute-backed controller tests, and live-host evidence. Any live-host claim must be supported by receipts from the actual selected host, including host-issued run identities; worker-supplied identity fields are not provenance. | Fixture transport and mocked stage replies can establish controller behavior only. A passing fixture or model check does not establish real host isolation or provenance. Missing host evidence is reported as a limitation, not silently treated as a pass. | Existing live-host check at [check_p2p_delivery_host.py](../checks/check_p2p_delivery_host.py) and its actual controller/host receipts | Host-issued session events and retained completion records, separately inspectable from fixture transport records | Retain and label three evidence classes separately in `.p2p/work/delivery-model-conformance/evidence/`: FizzBee model checks, substitute-backed controller cases, and live-host runs. For live-host observations retain the exact command/environment, actual session IDs and host receipts, controller result, and saved state. | planned |
| R8 | Issue #30; pinned handoff §19 Phase 3 | Document model bounds, adapter mapping, and evidence limits, including which required controller behavior was added to the bounded model and which cases use substitutes or the live host. | Do not claim that finite exploration proves all controller executions, that model success proves host behavior, or that fixture success proves host provenance. | Model README, model-to-controller mapping, and retained run summaries | Source-to-model-to-controller traceability and the recorded command/result for each evidence class | Update `checks/delivery-model/README.md` or the appropriate existing model documentation with the adapter operation mapping, bounds, assumptions, exploration limits, unchecked behavior, tool pin, configurable executable path, replay instructions, and model/fixture/live-host distinctions. Preserve the existing model and controller fixtures; add no empty framework. | planned |

## Unresolved gaps

- None in the planned seams or oracles. The compatibility checkpoint, controller mutations, and live-host receipts are implementation evidence still to be gathered; this contract does not claim they have been run. If the pinned FizzBee tools are unavailable, record that as an execution blocker rather than substituting a handwritten action list.

## Open questions

- None. The source settles the outcome and scope. The adapter language is a compatibility-gated implementation choice: the first bounded task must record the observed FizzBee operation and caught mismatch before that choice is committed.

## Out of scope

- Work beyond Phase 3, including the current roadmap's separate Phase 3.1 addition; preserve that committed addition without adding new host support under issue #30.
- Additional host support, strategy or model comparisons, optional checking levels, child scheduling, automatic strategy selection, publication, or changes to the meanings of full independent `REVIEWED` and `PROVEN`.
- A second model disconnected from controller operations, a general testing framework, or new architecture not required by the mapped conformance cases.

## Source reconciliation

- Issue #30's actual-controller integration, repeatable success/failure/restart, overlap where supported, replayable failures, controller defect detection, required Section 21.2 cases, model extension, documentation, and evidence distinctions map to R1–R8.
- Pinned handoff §19 Phase 3 supplies the adapter compatibility checkpoint and requires model actions to exercise real controller operations; these map to R1–R6.
- Pinned handoff §21.2 supplies the conformance cases and real-host provenance requirement; these map to R3 and R7.
- Phase 1 model checking remains a prerequisite and a source of model rules, not controller-conformance evidence. Phase 2's actual controller and fixtures are reused. The prerequisite is context, not a parent contract whose earlier outcomes must be redelivered.

## Imported issue text

The following is the imported issue body retained verbatim from `.p2p/work/delivery-model-conformance/evidence/issue-import.json`; its source URL and retrieval identity are recorded above.

```markdown
Connect the Phase 1 FizzBee model to the real single-work-item delivery controller from #28 and merged PR #29, so tests detect differences between the model and the running program.

## Scope

- Drive the actual controller through repeatable success, failure, and restart sequences. A modeled restart must restart the controller and inspect recovery from saved records.
- Test overlapping operations where the supported host permits them.
- Retain failure sequences that another person can replay.
- Introduce deliberate controller defects and demonstrate that the tests detect them. Removing a real protection, such as stale-report rejection, must make a test fail. Inspect both returned results and persisted state.
- Cover applicable Section 21.2 cases: unauthorized actions, stale or mistyped identities, candidate mutation, incomplete archives, interrupted report storage, late results, duplicate writes, repeated resume, and contested dirty files. Check real host provenance.

Demonstrate that the pinned FizzBee tools can drive the adapter before choosing its language. Reuse the delivered model and controller fixtures. Extend the bounded model where required controller behavior falls outside its current scope. Document bounds and distinguish model checks, substitute-backed controller tests, and live-host evidence. Running a second copy of the model alone does not satisfy this work.

## Boundaries

Phase 3 only. Preserve full independent REVIEWED and PROVEN requirements, exact identities, authorization, durable evidence, unrelated work, and the repair bound across restart. Strategy comparisons, optional checking levels, child scheduling, and automatic strategy selection remain in later phases. Do not add support for additional hosts as part of this issue.

Use /plan-acceptance to establish the canonical work/ contract. This source issue does not approve implementation, decomposition, or publication of delivery results.

## Source

[Exact optimization handoff](https://github.com/grove/promise-to-proof/blob/5c2c6b64b997dd2c04ac8ba85dcad8e08047eac2/plans/promise_to_proof_optimization_handoff.md)

Selected scope: Section 19, Phase 3, with Section 20 and applicable Section 21 constraints. The source specification remains authoritative.

- Repository: grove/promise-to-proof
- Path: plans/promise_to_proof_optimization_handoff.md
- Commit: 5c2c6b64b997dd2c04ac8ba85dcad8e08047eac2
- SHA-256: 7162a965fa53322a8805582756ea6137a847d72798e057dd751cc2e46c98f65a

The pinned file was retrieved and matched the local bytes before the separately requested status update. That local update records Phase 2 completion and Phase 3 as next; it is not included in this pinned revision.

This issue selects Phase 3. Closed issues #24 and #28 cover earlier phases of the same roadmap.

<!-- grove:create-parent-issue source=grove/promise-to-proof:plans/promise_to_proof_optimization_handoff.md -->
```

## Change notes

- Initial contract v1. This is a same-meaning correction before the first canonical save; no prior requirement IDs existed. It preserves issue #30 promises and the pinned Phase 3 constraints. No unresolved product decision or extra approval gate is introduced. Planning only; no implementation or proof is claimed.

## Implementation handoff

The enclosing workflow saves and rereads this contract at `work/delivery-model-conformance.md`. Begin implementation with R1's bounded FizzBee driver compatibility checkpoint before selecting its language. Preserve the requirement IDs, use configurable tool paths with documented pins, and implement only inside this Phase 3 scope. Retain evidence outside the product candidate.

## Proof handoff

Evaluate every requirement against this exact contract revision and one fixed candidate. Inspect the FizzBee traces and adapter operations, actual controller results and saved state, mutation failures, replay paths, and separately labeled model, substitute-backed, and live-host evidence. Record bounds and evidence limitations in a separate proof report; model success alone is not proof of controller conformance.

Next steps:

1. The enclosing workflow saves and rereads this exact contract at `work/delivery-model-conformance.md`.
2. Begin the already authorized implementation with the R1 FizzBee driver compatibility checkpoint.