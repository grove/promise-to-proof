# CHANGES NEEDED: Frozen delivery bases under moving targets

Contract: `work/frozen-delivery-base.md` v2, SHA-256 `3925c513a6702b94fbc2fcfc30f7d2d057638a275ae103056031cb3ca38aa0a9`  
Binding source: `plans/frozen-delivery-under-moving-targets.md`, SHA-256 `c570232a7371a53fd6dad954ec9d53f7940ecba171b3a2080fd995a6bd9a77d2`  
Parent context: None  
Candidate: `snapshot:sha256:62d091adb1dbca6759b728946c47f1c9203d7094350c0bdac22a7bccbb165331`; recoverable manifest in `.p2p/work/frozen-delivery-base/candidate.json`  
Comparison: base `dbe54bc20a19b8ab8e700fb3aba9c9e8a59ce4d4`; all 141 candidate entries compared, `.p2p/` excluded. The candidate differs from this base at 19 paths: 18 modified and the new contract.  
Stability: candidate key, contract v2, and binding source remained unchanged. GitHub `main` still pointed at the captured base on final recheck.

Coverage: Full contract R1–R21. The previous full review of this candidate against A covered the unchanged contract obligations. This pass compared the complete candidate against the new base and rechecked the changed controller, tests, model, protocol, docs, and stage guidance. R1–R4, R7–R11, and R13–R15: admission, resume, retained-base, report, destination-observation, and CLI paths. R5–R6 and R12: review/proof handoff and binding. R16–R18: model and trace-checking changes. R19–R20: publication/readiness guidance and scenarios. R21: protocol and documentation changes. The base-specific compatibility finding below prevents a clean review conclusion.

## Contract fidelity

The frozen-base behavior remains aligned with the approved contract: destination movement is kept separate from the candidate and verifier base; publication and readiness retain their current-target boundaries. No contract change is indicated.

## Scope and simplicity

No additional scope or complexity finding.

## Engineering quality

### F1 — Preserve the controller's existing execution limits and process cleanup

- Source: comparison-base behavior and checks in `dbe54bc20a19b8ab8e700fb3aba9c9e8a59ce4d4`.
- Location: `skills/productivity/deliver-issue/scripts/p2p_delivery.py:370-388, 631-648, 1140-1150`; `skills/productivity/deliver-issue/SKILL.md:26-53`; `docs/p2p-delivery-controller.md:49-57`; `checks/test_p2p_delivery.py`.
- Evidence: current `main` exposes `--max-stage-seconds` with a 600-second default and an 1,800-second overall default; it records the earlier per-stage/overall deadline, reports heartbeat activity, and sends `SIGKILL` to the worker process group after the grace period. Its tests cover finite defaults, timeout enforcement, interruption/resume, and a child process that ignores `SIGTERM`. The candidate drops the stage-limit option and recorded attempt deadline; its `--max-seconds` defaults to `None`, and `launch` therefore passes `timeout=None` by default. The candidate also omits the heartbeat and only sends `SIGKILL` when waiting for the parent times out; if the parent exits after `SIGTERM` while a child ignores it, that child can survive. The corresponding timeout and child-cleanup tests present on the comparison base were removed from the candidate.
- Consequence: publishing this candidate would remove the normal per-stage bound, permit an unbounded stage when no overall limit is supplied, and can leave worker descendants running after interruption. These changes are unrelated to freezing the comparison base and conflict with behavior documented and tested on the target.
- Smallest correction: carry the frozen-base changes onto the current target while preserving its stage/overall limits, progress reporting, interruption receipts, and full process-group cleanup; retain regression coverage for those guarantees.
- Handoff: `/implement-contract`.

## Checks and limitations

- `p2p_filesystem.py validate --base refs/codex/review/issue37/main-20260928 work/frozen-delivery-base.md` passed: candidate key, contract/source hashes, comparison base, and 141-entry manifest matched.
- Captured GitHub `main` by read-only metadata as `dbe54bc20a19b8ab8e700fb3aba9c9e8a59ce4d4`; fetched that exact commit into a temporary local ref for tree comparison, then reconfirmed GitHub still named that tip.
- Materialized the captured candidate manifest and compared it to the full base tree outside `.p2p/`. Inspected the changed code, deleted timeout tests, model, scenarios, and documentation. Issue #37's body and planning proposal comment had no new amendment; local approval and source hashes remain intact.
- No test suite or model exploration was run during this review. The earlier `PROVEN` report remains bound to this same candidate and contract against A; it does not establish compatibility with the newly reviewed target.

## Handoff

F1 requires an in-scope implementation correction that preserves current-target behavior while meeting the contract. The contract does not need amendment. After correction, capture the changed candidate and run fresh full review and proof.

Report storage: `.p2p/work/frozen-delivery-base/review.md`; prior report preserved under `history/`.

Review only; acceptance proof and merge readiness are separate.

## Next steps

1. `/implement-contract work/frozen-delivery-base.md; findings .p2p/work/frozen-delivery-base/review.md` — restore current `main`'s stage limits and worker cleanup while retaining the frozen-base behavior.
2. Capture the repaired candidate against the current target, then run fresh full `/review-implementation` and `/prove` reports for that exact candidate.
3. If both reports match and the target still equals the review base, rerun `/publish-pr work/frozen-delivery-base.md; review .p2p/work/frozen-delivery-base/review.md; proof .p2p/work/frozen-delivery-base/proof.md; target main; draft only`. Authorize any commit, push, and PR only against its exact preview.
