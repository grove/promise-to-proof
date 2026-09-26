# IMPLEMENTED: single-work-item delivery

Contract: work/single-work-item-delivery.md v1, SHA-256 e447f13a94dae84b9af2dfc06cfb6be36900eee2c0e381a3942015245b48826d.
Scope: R1–R14, whole contract.
Candidate before: 1a296f6ec7a064b32ce1be6a5d29f0c39df12294, main.
Candidate after: snapshot:sha256:847704b1ef38871fc2e62529426105cc31ae029a79c11e8190c00fcb3b519259. All 118 manifest entries are recoverable from candidate.json.
Review base: 1a296f6ec7a064b32ce1be6a5d29f0c39df12294.
Changes: stdlib controller p2p_delivery.py; atomic replacement/history in the existing filesystem helper; deterministic controller tests; real-host check; CLI documentation and how-to link. Existing task-owned contract and delivery records were preserved. The controller delivers an isolated candidate and preserves its source checkout.

## Requirement handoff

Production implementation is in skills/productivity/deliver-issue/scripts/p2p_delivery.py unless a row names another file. Fixture cases below are methods in checks/test_p2p_delivery.py. Fixture reports are deliberately labeled and do not establish host behavior.

| ID | Implementation reference | Acceptance check and actual observation | Remaining gap |
|---|---|---|---|
| R1 | command, dispatch, host_events, receipt, preflight | Final live invocation started two fresh preflights and separate implementation/review/proof sessions. Every stage retained a distinct host thread ID plus matching launch/events/exit records. | None identified. |
| R2 | preflight, external repository.git, verifier scratch-only dispatch | Both final live preflights denied writes to source HEAD/index, candidate sentinel, contract, binding input, base-manifest and controller admission record through absolute paths, symlinks and subprocesses. Scratch writes succeeded. Final verifier contexts ran from separate scratch roots. | None identified. |
| R3 | stage, run, complete; checks/check_p2p_delivery_host.py | Final public-controller live run returned REVIEWED_AND_PROVEN, exit 0. The implementation created greet.py; independent review inspected the full manifest/base; independent proof ran the CLI and observed exact hello+LF bytes and exit 0. The live runner recorded unchanged outer product key. | None identified. |
| R4 | helper capture/validate/bindings, report input identity comparison, retained base bundle | test_reconstruct_candidate_with_retained_base restored the candidate in a fresh checkout from retained Git objects/manifest and passed helper validation. Drift tests reject changed product, agreement, binding source, base content and stale digest. Existing helper/bundle identity tests also passed. | None identified. |
| R5 | helper atomic_write/save, retained, read_report, complete | test_success_source_preservation_and_retrieval rejects truncated report/evidence; test_source_agreement_binding_base_and_report_loss rejects missing canonical report content; test_storage_failure_is_recoverable_from_exact_host_return recovers the exact saved host result without redispatch. Full row coverage and nonempty proof observations/evidence are required. | None identified. |
| R6 | current/source_stable before and after verifiers, input equality, repaired report invalidation | test_stale_and_missing_coverage_rejected rejects stale input identity; test_agreement_and_candidate_drift rejects changed product; successful and exhausted repair tests rerun both full independent verifier stages after recapture. | None identified. |
| R7 | work-item flock, durable reserve, receipt reconciliation, duplicate-result guard | test_fresh_process_recovers_known_completion_once exits a controller after process completion and before receipt consumption, then reconciles once in a new process. test_fresh_process_uncertain_launch_blocks and test_uncertain_launch_never_repeats preserve reservations with missing completion. Storage-failure recovery and repeat resume retain exact prior results. | None identified. |
| R8 | durable repair_used reservation, immutable admission, fresh review/proof eligibility | test_successful_repair_rereviews_and_reproves and test_repair_refreshes_both_and_exhaustion_persists show exactly one repair and both fresh verifier runs; repeated resume dispatches no second repair. | None identified. |
| R9 | create scope inventory, isolated workspace, excluded comparison-base bytes, capture scope guard | test_success_source_preservation_and_retrieval checks unchanged unrelated bytes, executable mode, symlink target and original source behavior; test_contested_dirty_blocks prevents dispatch with ambiguous dirty paths. The real live source still has no greet.py, while the isolated candidate does. | None identified. |
| R10 | explicit --authorize-local, immutable admission, isolated configuration, sandbox write roots | test_missing_authority_dispatches_nothing and test_persisted_scope_cannot_widen pass. Final live shell network attempt is denied. Additional project-config-probe uses exact frozen command() arguments against a project requesting extra write roots, escalation and MCP startup, under actually configured trusted ancestors. Outside write denied, MCP canary absent; host tool-discovery and effective policy receipts confirm no extra tools/write roots. | None identified. |
| R11 | attempt starts/finishes/outcomes/elapsed/usage, explicit unknown costs | Fixture event assertions retain stage timestamps, nonnegative elapsed seconds and supplied usage. Uncertain launch retains unknown fields. Final real host stages retain actual token categories and elapsed durations; monetary cost is unknown. A credential-pattern scan of retained final live text records found no matches. | None identified. |
| R12 | reserve under lock, persisted max-dispatches/deadline, hard-cap rejection | test_admission_no_new_effects, test_authority_hard_cap_and_expired_admission, test_persisted_scope_cannot_widen and test_concurrent_controller_cannot_reserve all pass. Exhausted/expired/unsupported limits cause no new model dispatch. | None identified. |
| R13 | result host fields and docs/p2p-delivery-controller.md | Final live records distinguish actual host usage from unknown monetary cost; hard monetary cap is unsupported. Docs distinguish admission/process termination from exact provider billing cutoff. Fixtures and live records remain labeled separately. | None identified. |
| R14 | complete conjunction, result, structured exception/blocker handling, read-only status | The final live case exits 0 with both full reports. Fixture cases return precise nonzero BLOCKED results for identity, evidence, authority, storage, resource and uncertain-host failures with durable progress/resume references. The earlier live development case was correctly blocked despite REVIEWED/PROVEN status strings because a review row used the wrong verdict. | None identified. |

## Checks and retained evidence

- `PYTHONDONTWRITEBYTECODE=1 python3 checks/test_p2p_delivery.py`: 19 tests passed in 99.110 seconds. Exact output retained at evidence/fixture-tests-final.log.
- `PYTHONDONTWRITEBYTECODE=1 python3 checks/test_p2p_filesystem.py`: 2 tests plus filesystem assertions passed after the atomic storage change.
- `PYTHONDONTWRITEBYTECODE=1 python3 checks/test_verify_acceptance_bundle.py`: 2 tests passed.
- `git diff --check`: passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 checks/check_p2p_delivery_host.py --output-dir .p2p/work/single-work-item-delivery/evidence/live-delivery-final`: passed, exit 0. summary.json records passed=true, code_unchanged=true, source_preserved=true and the exact outer candidate key above. invocation.json retains every product entry hash before dispatch; final readback confirmed the same product content.
- `evidence/project-config-probe/runner.py`: executed against the unchanged production command builder to resolve review F1's missing configuration evidence. summary.json passed. observations.md describes actual inherited user trust, exact malicious project settings, observed permission denial and absent MCP startup. tool-discovery-host-excerpt.json retains the actual host tool call/output and effective filesystem/permission records, not only a worker assertion. No configuration warning was emitted, and stderr remains retained as empty.
- The outer filesystem helper validate command passed after live completion and the additional configuration probe; exact candidate key, contract and binding identities remain unchanged.

Final live host sessions:

| Stage | Host thread ID | Elapsed seconds |
|---|---|---|
| preflight-1 | 01a0dd78-0e9e-7361-80ac-a427a5063ad2 | 43.632 |
| preflight-2 | 01a0dd78-ba0a-7122-9b90-1eb6fe6e1cfa | 39.648 |
| implementation | 01a0dd79-5704-7303-bccb-8bb855def606 | 144.683 |
| review | 01a0dd7b-9050-7de1-b0f0-4d4cb02dc181 | 111.139 |
| proof | 01a0dd7d-45c6-7aa1-9e3e-d518bff3a624 | 126.641 |
| project configuration probe | 01a0dd82-b854-7bd3-ba99-1e8a4e124501 | 25.158 |

The final tiny delivery's canonical reports, exact structured reports/evidence and host receipts are discoverable under evidence/live-delivery-final/tiny-source/.p2p/work/tiny/. The returned tiny candidate has its own candidate.json and retained base.bundle. Full actual host usage categories are in delivery.json and summary.json; no cost estimate is presented as a cap.

The earlier development run under evidence/live-delivery-development-1 is preserved as failed historical evidence. Its real review returned status REVIEWED with row verdict `proven` instead of required `reviewed`. The completion gate rejected it; no report was manually corrected. The final unchanged-candidate run returned the required full row values and completed.

## Limits and decisions

The supported host is macOS Codex CLI 0.157.1 with the existing configured OpenAI model preference. The controller and OS host are trusted. Permission claims do not cover an administrator or arbitrary malicious same-user process rewriting the host. Model judgment and evidence adequacy remain the independent skills' responsibility; the deterministic bundle checker establishes consistency, not truth by itself.

An uncertain launch without a saved controller completion remains BLOCKED instead of being retried. An interrupted implementation/capture can preserve changed workspace bytes and return a precise recovery blocker. This is permitted by the contract's safe-resume-or-exact-blocker rule. The controller does not silently refresh stale identities, invent cost data, or grant a second repair.

Report storage: .p2p/work/single-work-item-delivery/implementation.md, saved and reread; previous progress reports and related evidence retained under history/.

Implementation report only; independent acceptance requires /prove.

Next steps:

1. `/review-implementation work/single-work-item-delivery.md` can reconcile review F1 against the new same-candidate project configuration evidence. The canonical candidate and this report are discoverable from the work-item path.
2. `/prove work/single-work-item-delivery.md` evaluates the full unchanged candidate with final live and fixture observations. Publication remains a separately authorized action.
