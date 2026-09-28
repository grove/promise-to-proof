# REVIEWED: Issue #37 — frozen delivery bases under moving targets

Contract: `work/frozen-delivery-base.md` v2, SHA-256 `3925c513a6702b94fbc2fcfc30f7d2d057638a275ae103056031cb3ca38aa0a9`.
Binding source: `plans/frozen-delivery-under-moving-targets.md`, SHA-256 `c570232a7371a53fd6dad954ec9d53f7940ecba171b3a2080fd995a6bd9a77d2`.
Approval: `.p2p/work/frozen-delivery-base/planning-handoff.md` records the user's approval of these exact v2 contract and source hashes. The contract's historical proposal wording is unchanged.
Candidate: `snapshot:sha256:d0a2b3cc0d60f6f0f36e019e47ddddad7ca5845ee570ac02269ac3956bc82404`; recoverable from `.p2p/work/frozen-delivery-base/candidate.json` (141 entries).
Comparison: `dbe54bc20a19b8ab8e700fb3aba9c9e8a59ce4d4` (B). Compared the full manifest outside `.p2p/` with B: 141 candidate entries versus 140 in B; 19 changed paths (18 tracked changes and the added work contract).
Stability: Candidate, contract, binding source and comparison-base identities validated before review and revalidated after checks. No product or contract files were changed.
Coverage: Requirements R1–R21 reviewed. R1: destination resolution, ref validation and stale-base admission. R2–R4: immutable admission base, target movement and integrity/drift handling. R5–R6: review/proof bindings. R7–R11: resume, observations and retained-base recovery. R12: direct-review scope. R13–R15: legacy recovery, CLI and verdict compatibility. R16–R18: bounded model state, witness and mutations. R19–R20: publication/readiness boundaries. R21: protocol, instructions, docs and scenarios. Inspected the full candidate change set and relevant surrounding controller, tests, skills, docs, scenarios and model/checker.

## Contract fidelity

No material findings. The C2 R1 finding is fixed: `explicit_destination()` now runs `git check-ref-format` on accepted fully qualified `refs/heads/...` and `refs/remotes/...` values before returning them (`skills/productivity/deliver-issue/scripts/p2p_delivery.py:115–130`). The added controller test exercises both `refs/heads/delivery-target~1` and `refs/remotes/origin/delivery-target~1`, requiring rejection before any stage dispatch. This closes the earlier path where Git revision expressions could be resolved as the destination tip.

Frozen-base movement remains intact. `test_movement_during_implementation_review_and_proof_keeps_all_bindings_fixed` moves the target while implementation, review and proof run, then checks that candidate and both verifier/report inputs remain bound to admission base A. The inspected controller coverage also retains repeated movement, unavailable and non-fast-forward destination observations, fresh-process resume, integrity checks, and no verifier redispatch after completed reports. The prior review's execution-limit/process-group F1 remains covered by the real subprocess timeout test.

## Scope and simplicity

No material findings. The changes stay within the approved frozen-base behavior. The current-target checks for publication and merge readiness remain in their existing boundaries; no automatic integration behavior or new acceptance verdict was introduced.

## Engineering quality

No material findings. The R1 correction validates ref syntax before any revision resolution and is covered at the controller admission boundary for both supported fully qualified ref namespaces. The focused movement and process-cleanup regressions also pass.

## Checks and limitations

- `p2p_filesystem.py validate --base dbe54bc20a19b8ab8e700fb3aba9c9e8a59ce4d4 work/frozen-delivery-base.md` passed before review and after checks. It confirmed the exact C3 key, B, work-item hash, binding-source hash and 141-entry manifest.
- Ran `python3 -m unittest checks.test_p2p_delivery.DeliveryTests.test_fully_qualified_destination_rejects_revision_expressions checks.test_p2p_delivery.DeliveryTests.test_unsliced_stale_explicit_base_names_current_destination checks.test_p2p_delivery.DeliveryTests.test_explicit_remote_tracking_destination_resumes_from_stored_ref checks.test_p2p_delivery.DeliveryTests.test_real_transport_timeout_and_heartbeat checks.test_p2p_delivery.DeliveryTests.test_movement_during_implementation_review_and_proof_keeps_all_bindings_fixed`: 5 tests passed in 21.779 seconds. The environment emitted a non-fatal PATH-alias permission warning.
- `git diff --check dbe54bc20a19b8ab8e700fb3aba9c9e8a59ce4d4` and `git diff --check` passed.
- Reviewed the current implementation report and planning approval receipt. The existing `.p2p/work/frozen-delivery-base/proof.md` is bound to candidate `snapshot:sha256:62d091adb1dbca6759b728946c47f1c9203d7094350c0bdac22a7bccbb165331` and base `39cf3a96aaf89789fceed9b0454682f9e88bc0b8`; it is stale for C3 and is not used as C3 proof.
- Inspected but did not execute the bounded model runner or direct interactive stage scenarios, and did not rerun the full controller suite. No `/prove` or publication operation was performed. No external PR or tracker state was checked.

## Handoff

`REVIEWED` for the exact candidate C3 against B and the exact approved v2 contract/source identities above. This review is not acceptance proof or merge readiness. Run a full proof for C3; the existing proof report is bound to a different candidate and base.
Report storage: `.p2p/work/frozen-delivery-base/review.md`. The replaced C2 report bytes are retained at `.p2p/work/frozen-delivery-base/history/02e10f504200a0d957a290d613ca116c8efd2737b1eceb7c8f431bd08b2c575a/review.md`, SHA-256 `02e10f504200a0d957a290d613ca116c8efd2737b1eceb7c8f431bd08b2c575a`.

Review only; acceptance proof and merge readiness are separate.

## Next steps

1. `/prove work/frozen-delivery-base.md; candidate snapshot:sha256:d0a2b3cc0d60f6f0f36e019e47ddddad7ca5845ee570ac02269ac3956bc82404` — produce fresh full proof for C3 against B and this exact contract/source binding.
