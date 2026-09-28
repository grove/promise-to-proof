# PROVEN: Issue #37 — frozen delivery bases under moving targets

Requirements: 21/21
Counterexamples tested: 15 named model mutations, plus the controller and controlled skill-boundary cases below
Contract: `work/frozen-delivery-base.md`, v2
Contract snapshot: exact UTF-8 bytes, SHA-256 `3925c513a6702b94fbc2fcfc30f7d2d057638a275ae103056031cb3ca38aa0a9`
Parent context: none
Candidate: `snapshot:sha256:d0a2b3cc0d60f6f0f36e019e47ddddad7ca5845ee570ac02269ac3956bc82404`
Comparison base: `dbe54bc20a19b8ab8e700fb3aba9c9e8a59ce4d4`
Binding source: `plans/frozen-delivery-under-moving-targets.md`, SHA-256 `c570232a7371a53fd6dad954ec9d53f7940ecba171b3a2080fd995a6bd9a77d2`
Candidate stability: unchanged; the filesystem validator recomputed all 141 manifest entries and exact identity before and after the checks
Contract stability: unchanged; exact work-item and binding-source hashes matched before and after
Verification context: macOS 26.6.2 arm64; Python 3.14.7. Controller suite used its disposable fake-worker transport. Model run used pinned FizzBee v0.5.3 `fizz` SHA-256 `8e8f905864b1781a3960f44fb654fc4455ef633e45556adf3fae586b652480a6`, `fizzbee` SHA-256 `f0746cd47d13f268835fc0d8c1e85ec28a8ad0034e080cff6ec49a26304c1bf3`, and `parser/parser_bin` SHA-256 `54eb014c1cc7cb874faccfe22e4f93e78dbb3d633a9f496d71e21f5997a8f3fd`

## Outcome

The exact C3 snapshot satisfies all 21 requirements against frozen base B. The controller suite completed 57 tests successfully. The FizzBee run passed 14 baselines, 19 witnesses, and 15 mutations (48 checks total); concrete moving-target and base-mismatch traces are retained. The separate full C3 review is `REVIEWED` for this same candidate, contract, and base (report SHA-256 `3f0c1cfb0599abc88c567086ec37a7a91c90ec3f3170872b8722c57284e408fc`). This proof does not establish compatibility with a later destination tip or merge readiness.

## Requirement verdicts

| ID | Observation and oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | Unsliced admission requires explicit or unambiguous upstream routing; stale requested base reports the actual destination and dispatches no worker. | `evidence/controller-tests-c3.stdout`; tests `test_unsliced_admission_requires_explicit_or_unambiguous_upstream`, `test_unsliced_stale_explicit_base_names_current_destination`, child-routing cases | proven |
| R2 | Repeated `run` cannot replace the admitted base; fresh-process resume retains the saved base. | `evidence/controller-tests-c3.stdout`; tests `test_repeated_run_cannot_replace_frozen_base_after_target_moves`, `test_fresh_process_resumes_missing_stages_after_target_advance` | proven |
| R3 | Fast-forward, repeated, and in-flight target movement leaves implementation, review, proof, candidate, and base fixed; matching reports complete. | `evidence/controller-tests-c3.stdout`; tests `test_movement_during_implementation_review_and_proof_keeps_all_bindings_fixed`, `test_target_advance_after_reports_return_does_not_refresh_verifiers`, `test_busy_destination_moves_repeatedly_without_refreshing_completed_stages` | proven |
| R4 | Candidate, agreement, binding, report, base-manifest, and bundle drift remain blockers even when the target moves. | `evidence/controller-tests-c3.stdout`; tests `test_source_agreement_binding_base_and_report_loss`, `test_agreement_and_candidate_drift`, `test_stale_and_missing_coverage_rejected` | proven |
| R5 | Actual candidate review instructions kept admitted base A after local `main` advanced; the saved scope compared the exact C3 manifest against A. | `evidence/c3-proof/r5-delivery-review/review.md` and `scope-validation.json`; 141 manifest entries matched, with no worker dispatch or external effect | proven |
| R6 | Proof identity remains bound to exact C3, contract v2, source, and B; the proof outcome disclaims compatibility with later destination content. Controller movement-during-proof assertions independently check the verifier binding. | `evidence/c3-proof/identity-before.json`, `identity-after-checks.json`, `evidence/controller-tests-c3.stdout` | proven |
| R7 | Fresh-process resume dispatches only missing stages; completed reports are reused across movement without another verifier call. | `evidence/controller-tests-c3.stdout`; tests `test_fresh_process_resumes_missing_stages_after_target_advance`, `test_fresh_process_recovers_known_completion_once`, `test_busy_destination_moves_repeatedly_without_refreshing_completed_stages` | proven |
| R8 | Observations classify unchanged, fast-forward, non-fast-forward, and unavailable targets while preserving base and candidate identities. | `evidence/controller-tests-c3.stdout`; tests `test_unsliced_admission_requires_explicit_or_unambiguous_upstream`, `test_explicit_remote_tracking_destination_resumes_from_stored_ref`, `test_non_fast_forward_and_missing_destination_do_not_invalidate_acceptance` | proven |
| R9 | Successful completion retains `REVIEWED_AND_PROVEN` and describes newer-target compatibility as unestablished. | `evidence/controller-tests-c3.stdout`; tests `test_movement_during_implementation_review_and_proof_keeps_all_bindings_fixed`, `test_target_advance_after_reports_return_does_not_refresh_verifiers` | proven |
| R10 | No automatic integration or base refresh occurs; adopting B creates a new candidate and fresh report bindings. | `evidence/controller-tests-c3.stdout`; tests `test_repeated_run_cannot_replace_frozen_base_after_target_moves`, `test_adopting_new_base_uses_new_candidate_and_fresh_report_bindings` | proven |
| R11 | Exact B is independently recoverable: the C3 bundle verifies, a separate clone reproduces the commit/tree and every tree object, and a pruned source clone loses B while bundle recovery retains it. Corrupt/lost recovery material blocks controller reuse. | `evidence/comparison-base-c3.bundle` and `comparison-base-c3.json`; 2,226 entries/1,254 unique objects verified. Controller tests `test_reconstruct_candidate_with_retained_base`, `test_resume_rereads_reports_after_source_prunes_base_commit`, `test_source_agreement_binding_base_and_report_loss` | proven |
| R12 | Actual direct-review invocation captured B, then retained B after `main` moved to D; no admitted delivery base was borrowed and C3 content remained unchanged. Exact C3 skill/protocol text requires fresh review after candidate/agreement/routing/base changes. | `evidence/c3-proof/r12-direct-review/review.md`, `scope-captured.json`, and `candidate-scope.json` | proven |
| R13 | Recoverable legacy approved routing resumes against the saved base after movement; incomplete or changed binding/recovery inputs block. | `evidence/controller-tests-c3.stdout`; tests `test_legacy_approved_route_resumes_after_target_move_when_base_is_recoverable`, `test_parent_uses_final_destination_and_plan_loss_blocks_resume` | proven |
| R14 | Existing CLI invocation shape and plain approval survive transfer/resume; no new mandatory destination argument is introduced. | `evidence/controller-tests-c3.stdout`; tests `test_public_cli_retains_plain_approval_on_transfer_and_fresh_recovery`, `test_unsliced_admission_requires_explicit_or_unambiguous_upstream` | proven |
| R15 | Existing `REVIEWED`, `PROVEN`, and `REVIEWED_AND_PROVEN` outcomes remain in use; destination classifications remain observations. | `evidence/controller-tests-c3.stdout`; successful completion/status assertions and retained review/proof identity checks | proven |
| R16 | Model safety exploration keeps the admission base immutable and requires both verifier bindings to match it at completion. | `evidence/model-c3/summary.json`; 14 baselines, including `base`, `review-base`, and `proof-base` | proven |
| R17 | Ordered moving-target witness reaches completion after target movement with fixed verifier bases and saved/read-back reports. | `evidence/model-c3/witness-moving-target/trace.json`, `trace.txt`, `observation.json` | proven |
| R18 | Separate review-base and proof-base mutations produce concrete violations of the named `ComparisonBase` invariant. | `evidence/model-c3/mutation-review-base/trace.json` and `mutation-proof-base/trace.json`; both named mutations passed their counterexample oracle | proven |
| R19 | The actual publication skill blocks a valid matching acceptance pair when controlled target B differs from review base A. Current C3 actor skill, protocol, repository, and tracker instruction bytes exactly match the retained invocation resources; no network or publication effect occurred. | `evidence/skill-boundaries/issue37-r19-publish-boundary/`, including `report-pair-verification.json`, `actual-output.md`, `observations.json`, `input-hashes.json`; parity in `evidence/c3-proof/r19-r20-actor-resource-parity.json` | proven |
| R20 | Actual read-only readiness skill blocks a valid matching pair for target drift, pending required CI, and 0/1 approvals; it preserves the pair and skips synchronization. C3 skill, protocol, and scenario bytes exactly match actor resources. | `evidence/skill-boundaries/issue37-r20-readiness-boundary/`, including `controlled-input.json`, `actor-response.md`, `expected-oracle.md`, `observations.md`; parity in `evidence/c3-proof/r19-r20-actor-resource-parity.json` | proven |
| R21 | Controller documentation maps every T1–T12 to executable assertions; delivery, review, proof, and protocol instructions separate frozen acceptance from current-target publication/readiness; model docs state explored bounds and mutation checks. | `docs/p2p-delivery-controller.md` §“Check target movement”; `skills/productivity/deliver-issue/SKILL.md`, `review-implementation/SKILL.md`, `prove/SKILL.md`; `docs/acceptance-contract-protocol.md` §§“Candidate identity and resume” and “Epic delivery plans”; `checks/delivery-model/README.md` R16–R18 mapping | proven |

## Evidence limits

- The controller suite uses its controlled fake worker transport. It verifies controller behavior and saved identities, not agent judgment or live-host isolation.
- FizzBee v0.5.3 explored the documented bound: one fault family, 64 actions, one restart, and one repair. It is bounded safety evidence, not a universal liveness proof.
- R5 and R12 are actual scope-focused skill invocations, not duplicate full implementation reviews. R12 exercised B→D movement; changed-input variants were not separately injected. The exact candidate skill and protocol require fresh verification for those changes, and the saved scope stayed fixed throughout the observed move.
- R19 and R20 use a valid controlled C′ acceptance pair, not issue #37 C, and an offline controlled tracker snapshot, not live GitHub state. They establish generic gate behavior for actor resources byte-identical to the exact C3 skills/protocol/scenario instructions; they do not claim issue #37 has a published PR or establish current remote state.

## Unresolved gaps

None for the 21 acceptance requirements. The evidence limits above bound the claims; later destination compatibility and merge readiness remain separate decisions.

## Repairs needed

None. Fresh `/prove` is required after any repair. The separate `/review-implementation` result remains the review phase for this exact C3 candidate.

## Next steps

1. Acceptance evidence is complete for C3 against B. If an issue #37 pull request is later opened and approaches merge, run `/merge-readiness <PR URL>; review .p2p/work/frozen-delivery-base/review.md; proof .p2p/work/frozen-delivery-base/proof.md` against its current target and repository gates.
