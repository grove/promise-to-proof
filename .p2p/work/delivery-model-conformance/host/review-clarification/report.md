# REVIEWED: `work/delivery-model-conformance.md`

Contract: `work/delivery-model-conformance.md` v1; SHA-256 `0751249534a5cf5f21d8f97250e95e4c91a3c5b27ec578f45fc5c21624167237`. Binding source: `specs/delivery-model-conformance-source.md`, SHA-256 `7162a965fa53322a8805582756ea6137a847d72798e057dd751cc2e46c98f65a`. Binding protocol: `docs/acceptance-contract-protocol.md`, SHA-256 `bec3503abc6ebc40356e662ca0b279be73a4da482eb1616a5c5b435509184351`.

Parent context: None. Phase 1 and Phase 2 are named prerequisites, not inherited contracts.

Candidate: `snapshot:sha256:7a82e6bfc71d1e7fcf2318f9aa18473ed9a92e06c8f0d318b40b9be44dfcf912`, recoverable from `.p2p/work/delivery-model-conformance/candidate.json`.

Comparison: Full candidate snapshot against base `833a33647f545afb9028d03bf82d03613415ddf9`, excluding `.p2p/`. The full delta includes seven conformance files under `checks/delivery-model/`, the binding spec, and the contract.

Stability: Final candidate validation passed. The candidate key, all 126 manifest entries, agreement digest, binding hashes, and base identity match. The candidate checkout’s `HEAD` is the specified base. No product, contract, base, or receipt inputs were changed. The earlier `host/review-recheck/report.md` remains unchanged and historical.

Coverage: Full R1–R8 scope. Inspected the complete snapshot delta, model, runner, TypeScript adapter, Python bridge, package files, documentation, compatibility checkpoint, retained conformance observations, and relevant live-host receipts.

## Contract fidelity

No material findings.

- **R1:** The retained compatibility checkpoint shows FizzBee driving the public `status` operation and rejecting a deliberately wrong result before TypeScript was chosen.
- **R2:** Model actions map to fresh controller CLI processes and inspect both returned output and persisted records across restart.
- **R3:** The model and bridge cover the named authorization, identity, mutation, archive, storage, late-result, duplicate-write, resume, and dirty-file cases.
- **R4:** The runner applies five deliberate mutations to real controller guards in copies, leaving the model and adapter oracle unchanged.
- **R5:** `concurrent-resume` drives overlapping controller processes and checks the lock blocker and unchanged persisted state. The evidence correctly labels this as fixture transport.
- **R6:** Retained traces include action sequences, commands, fixture inputs, controller output, saved state, and replay parameters.
- **R7:** Model, substitute-backed, and live-host evidence are distinguished. The corrected canonical-entry comparison supports the live-host candidate identity.
- **R8:** The README records mapping, pins, replay instructions, bounds, assumptions, and evidence limits.

F1 from the earlier report is withdrawn. The contract and README specify Python 3.11 or newer and invoke the standalone conformance script with ordinary `python3`; they do not promise execution under `-O` or `PYTHONOPTIMIZE`. Repository model-check scripts and fixtures also use `assert`. The `-O` probe established Python behavior but did not demonstrate a failure within the promised invocation. The retained Python 3.14 run used ordinary execution and reports all required enabled-action counts and mutation outcomes. Requiring optimized-mode support or an explicit rejection would add a runtime condition absent from the contract.

## Scope and simplicity

No material findings. The changes add the bounded conformance seam and its documentation. Production controller behavior is unchanged from the comparison base; intentional guard mutations target disposable copies.

## Engineering quality

No material findings. Under the documented invocation, the runner checks tool pins, build and execution results, model links, and actual action counts. The adapter surfaces subprocess errors as nonzero failures. The optional `--node-modules` path documents that it checks direct dependency versions; the default path installs from the lockfile.

## Checks and limitations

- `/opt/homebrew/bin/python3 /Users/grove/.agents/skills/review-implementation/scripts/p2p_filesystem.py --repo /Users/grove/projects/promise-to-proof validate work/delivery-model-conformance.md --base 833a33647f545afb9028d03bf82d03613415ddf9` — passed at final recheck and confirmed the candidate identity, agreement digest, binding hashes, and base.
- `/opt/homebrew/bin/python3 /Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/live-host/check-product-identity.py --candidate /Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/candidate.json --live-host /Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/live-host` — passed: all 126 canonical manifest-entry hashes match both original receipts; the candidate key matches; `passed`, `code_unchanged`, and `source_preserved` are true.
- Inspected `checks/check_p2p_delivery_host.py:29` and `skills/productivity/deliver-issue/scripts/p2p_filesystem.py:18-22`. `product_entries_sha256` hashes each canonical JSON entry, including path, mode, type, and encoded content or link target; it does not hash decoded file bytes. The original R7 comparison used different hash inputs. No historical verdict or receipt was edited.
- Inspected the five raw `thread.started` events and their matching attempt launch and completion records. Each distinct host-issued thread ID matches the controller-recorded session ID. Each completion has exit code 0 and a matching event-stream hash. The live result is for a tiny fixture and remains separate from fixture conformance evidence.
- The retained final-run evidence reports 17 normal cases and five real-guard mutations under ordinary Python 3.14 execution. No MBT suite or live-host run was repeated for this review. Finite model exploration and fixture worker replies do not establish every execution or live-host concurrency.
- No PR or merge gates were assessed. This review is not an acceptance proof or merge approval.

## Handoff

No findings. F1 is withdrawn because its trigger is outside the contract’s documented runtime. The full R1–R8 candidate review is complete; acceptance still requires a matching full proof.

Report storage: pending. The enclosing workflow owns storage; save this as a distinct reassessment and leave `host/review-recheck/report.md` unchanged.

Review only; acceptance proof and merge readiness are separate.

## Next steps

1. Run `/prove work/delivery-model-conformance.md; candidate snapshot:sha256:7a82e6bfc71d1e7fcf2318f9aa18473ed9a92e06c8f0d318b40b9be44dfcf912` for current full R1–R8 acceptance evidence. No PR exists; no further action is required unless publication is later wanted and separately authorized.