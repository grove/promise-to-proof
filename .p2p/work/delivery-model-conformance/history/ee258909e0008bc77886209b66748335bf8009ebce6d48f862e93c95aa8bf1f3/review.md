# CHANGES NEEDED: `work/delivery-model-conformance.md`

Contract: `work/delivery-model-conformance.md` v1; SHA-256 `0751249534a5cf5f21d8f97250e95e4c91a3c5b27ec578f45fc5c21624167237`. Binding source: `specs/delivery-model-conformance-source.md`, SHA-256 `7162a965fa53322a8805582756ea6137a847d72798e057dd751cc2e46c98f65a`. Binding protocol: `docs/acceptance-contract-protocol.md`, SHA-256 `bec3503abc6ebc40356e662ca0b279be73a4da482eb1616a5c5b435509184351`.

Parent context: None. Phase 1 and Phase 2 are named prerequisites, not inherited contracts.

Candidate: `snapshot:sha256:7a82e6bfc71d1e7fcf2318f9aa18473ed9a92e06c8f0d318b40b9be44dfcf912`, recoverable from `.p2p/work/delivery-model-conformance/candidate.json`.

Comparison: Full candidate snapshot against base `833a33647f545afb9028d03bf82d03613415ddf9`, excluding `.p2p/`. The full delta includes seven conformance files under `checks/delivery-model/`, the binding spec, and the contract.

Stability: Candidate validation passed before reporting. The candidate key, all 126 manifest entries, agreement digest, binding hashes, and base identity match. The candidate checkout’s `HEAD` is the specified base. No product, contract, base, or receipt inputs were changed.

Coverage: Full R1–R8 scope. Inspected the complete snapshot delta, model, runner, TypeScript adapter, Python bridge, package files, documentation, compatibility checkpoint, prior conformance evidence, and relevant live-host receipts.

## Contract fidelity

No observed missing promised controller scenario or scope discrepancy. R1’s compatibility checkpoint records FizzBee driving the real public `status` operation and rejecting a deliberately wrong observation before TypeScript was chosen. R2–R6 map model actions to fresh CLI processes, persisted state, corruption cases, real-controller guard mutations, overlap, and replay traces. R8 documents the action mapping, bounds, and evidence limits.

**F1 affects confidence in the R3, R4, and R6 checks:** the runner’s required-action and mutation-result validations can be disabled under Python optimization; see Engineering quality.

## Scope and simplicity

No material findings. The changes add the bounded conformance seam and its documentation. The controller itself is unchanged from the base; the runner’s deliberate guard mutations are applied to disposable copies.

## Engineering quality

**F1 — Fail-closed validation uses removable assertions (R3, R4, R6).** In `checks/delivery-model/conformance.py:83-86,121-130,153-178` and `checks/delivery-model/conformance_bridge.py:92-94,190-226`, critical checks use Python `assert`, including required real-action counts, model and tool checks, mutation outcomes, and state comparisons. Python removes these checks under `-O` or `PYTHONOPTIMIZE`. I confirmed the behavior with `/opt/homebrew/bin/python3 -O -c 'assert False, "assert optimization probe"; print("assert removed under -O")'`, which exited successfully and printed `assert removed under -O`. When the runner is invoked in that mode, or inherits `PYTHONOPTIMIZE`, missing-action coverage and other asserted conditions are no longer guaranteed to fail the run. This weakens the fail-closed runner required for these conformance checks. Replace correctness-critical assertions in the runner and bridge with explicit conditional checks that raise errors or exit nonzero.

## Checks and limitations

- `/opt/homebrew/bin/python3 /Users/grove/.agents/skills/review-implementation/scripts/p2p_filesystem.py --repo /Users/grove/projects/promise-to-proof validate work/delivery-model-conformance.md --base 833a33647f545afb9028d03bf82d03613415ddf9` — passed at final recheck. It confirmed the candidate key, work-item SHA, binding hashes, and comparison base.
- `/opt/homebrew/bin/python3 /Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/live-host/check-product-identity.py --candidate /Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/candidate.json --live-host /Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/live-host` — passed: all 126 canonical manifest-entry hashes match both `invocation.json` and `summary.json`; the candidate key matches; `passed`, `code_unchanged`, and `source_preserved` are true.
- Inspected `checks/check_p2p_delivery_host.py:29` and `skills/productivity/deliver-issue/scripts/p2p_filesystem.py:18-22`. The recorded `product_entries_sha256` values hash canonical JSON entries containing path, type, mode, and encoded content or symlink target. They are not hashes of decoded file bytes. The earlier R7 observation compared different hash inputs; the corrected interpretation is supported by recomputing the complete map. The historical NOT PROVEN report was not changed.
- Inspected the live-host `stdout.json`, each of the five raw `thread.started` events, and the corresponding attempt launch and completion records. Each distinct host-issued thread ID matches the session ID recorded for its stage and the matching attempt; all five completion receipts have exit code 0 and matching event-stream hashes. The live result reports `REVIEWED_AND_PROVEN` for the tiny fixture. This is separate from the FakeTransport conformance fixtures and does not establish concurrent live-host execution.
- Inspected the retained compatibility records and prior conformance evidence, including the documented 17 cases and five guard mutations. No new MBT run or exhaustive proof was performed, as this review did not require one. The existing evidence describes finite, seed-bounded runs; fixture worker replies do not establish live-host provenance.
- No PR or merge gates were assessed. This review is not an acceptance proof or merge approval.

## Handoff

F1 is an in-scope engineering-quality finding affecting R3, R4, and R6. It requires a runner and bridge correction under the existing agreement, followed by a new candidate identity and fresh full review and proof.

Report storage: pending. The enclosing workflow owns storage and will save and reread these exact report bytes at `.p2p/work/delivery-model-conformance/review.md`.

Review only; acceptance proof and merge readiness are separate.

## Next steps

1. After this report is saved and reread, run `/implement-contract work/delivery-model-conformance.md; findings .p2p/work/delivery-model-conformance/review.md` to replace correctness-critical assertions with checks that remain active under Python optimization.
2. Capture the changed candidate, then refresh full `/review-implementation` and `/prove` for R1–R8 against that exact candidate.