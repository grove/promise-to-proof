# REVIEWED: `work/delivery-model-conformance.md`

Contract: `work/delivery-model-conformance.md` v1; SHA-256 `0751249534a5cf5f21d8f97250e95e4c91a3c5b27ec578f45fc5c21624167237`. Binding source `specs/delivery-model-conformance-source.md`: `7162a965fa53322a8805582756ea6137a847d72798e057dd751cc2e46c98f65a`; acceptance protocol: `bec3503abc6ebc40356e662ca0b279be73a4da482eb1616a5c5b435509184351`.

Parent context: None. The contract names Phase 1 and Phase 2 prerequisites; no inherited parent contract applies.

Candidate: `snapshot:sha256:7a82e6bfc71d1e7fcf2318f9aa18473ed9a92e06c8f0d318b40b9be44dfcf912`, recoverable from `.p2p/work/delivery-model-conformance/candidate.json`.

Comparison: Full product snapshot against base `833a33647f545afb9028d03bf82d03613415ddf9`; `.p2p/` excluded. The product delta is `checks/delivery-model/README.md`, the four conformance model/runner/adapter files, and its two npm files. The snapshot also adds the bound spec and contract.

Stability: Rechecked after inspection. The candidate key recomputes, all 126 manifest entries match the fixed checkout, the base checkout matches the pinned base tree, and the contract and binding hashes match. No candidate or contract inputs were changed.

Coverage: Full R1–R8 scope. Inspected the complete snapshot delta, conformance model and runner, generated TypeScript adapter, Python bridge, lockfiles, documentation, pinned compatibility evidence, retained conformance traces and mutation runs, live-host receipts, and relevant unchanged controller/host-check code.

## Contract fidelity

No material findings.

- **R1:** The retained compatibility checkpoint records the pinned FizzBee driver invoking an operation and rejecting the deliberately mismatched observation before TypeScript was selected. This is compatibility evidence, not a claim that the full suite passed.
- **R2:** The model maps actions to fresh CLI processes over shared saved records. Retained traces cover successful delivery, blocked failure, restart recovery, successful repair, and repair exhaustion across restart. The repair-exhaustion trace records two restarts, two reviews, two proofs, and two terminal resumes.
- **R3:** The 17 named cases cover the contract’s authorization, identity, candidate mutation, archive, storage, late-result, duplicate-write, resume, dirty-file, repair, and overlap cases. The model requires full passing reports against the current fixture candidate before modeling completion.
- **R4:** Five mutations target production guards in disposable controller copies: stale report, duplicate report write, late receipt, repair bound, and authorization. The model and adapter oracles remain unchanged.
- **R5:** `concurrent-resume` holds one real controller process after lock acquisition, invokes a second process, and checks the loser’s blocker and unchanged saved state.
- **R6:** The retained observations include replay commands and fixture inputs. `development/replay-comparison.json` records the same enabled action sequence and projections for a second stale-guard mutant run.
- **R7:** Substitute-backed controller runs and live-host receipts are labeled separately. In the live-host tiny-fixture run, all five controller stages have matching `thread.started` IDs, launch attempt IDs, completed turns, exit receipts, input identities, and event hashes. The live-host summary reports `REVIEWED_AND_PROVEN` for that tiny fixture; it does not stand in for conformance evidence.
- **R8:** The README documents action mapping, bounds, replay, pins, substitutes, live-host evidence, and MBT disabled-action handling.

## Scope and simplicity

No material findings. Changes add the requested bounded conformance seam and its documentation. The production controller and original fixtures are unchanged from the comparison base; the manifest shows no changes to them.

## Engineering quality

No material findings. The runner checks pinned tools, compiles the generated adapter, inspects model depth, rejects execution/link errors, and requires actual enabled-action counts. Adapter operation failures exit nonzero; the runner also rejects MBT server logs containing execution failure or unmatched links. The retained successful repair-exhaustion server log shows matching links for `DISABLED` proposals.

The shared npm installation matched all 36 lockfile package names and versions checked. The runner passes `sys.executable` to Python subprocesses.

## Checks and limitations

- Verified the candidate manifest key, all 126 checkout entries, the full base tree, contract SHA, and both binding-input SHAs before and after review.
- Inspected retained conformance observations for all 17 cases. Each has exit 0 and required actual action counts; maximum recorded model depth is 11 under the 256-action cap. The retained logs show the MBT server bound to port 50051.
- Inspected all five mutation observations: each mutation run exits 1 with `Return value mismatched`, after reaching the required controller actions.
- Inspected the live-host event streams and corresponding launch/completion records; each of the five `thread.started` IDs matches its controller receipt.
- Attempted the focused runner command with Python 3.14, pinned FizzBee and MBT binaries, the matching npm installation, seed 42, and output under scratch:

  `env TMPDIR=tmp PATH="<scratch>/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" PYTHONPYCACHEPREFIX="<scratch>/pycache" /opt/homebrew/bin/python3 <candidate>/checks/delivery-model/conformance.py --fizz /private/tmp/p2p-fizzbee-24/fizzbee-v0.5.3-macos_arm/fizz --mbt /Users/grove/projects/promise-to-proof/.p2p/tmp/issue-30/compatibility/fizzbee-mbt-0.2.0-macos_arm --node-modules /Users/grove/projects/promise-to-proof/.p2p/tmp/issue-30/compatibility/node_modules --case repair-restart-exhaustion --seed 42 --output-dir <scratch>/conformance-restart-3`

  This fresh run did not complete: the sandbox denied MBT’s relative Unix socket bind (`EACCES` for `fizzbee-mbt-…/plugin.sock`). An absolute scratch temp path instead hit a socket-path length error; the initial FizzBee wrapper temp call also hit the restricted OS temp path. The FizzBee checker and MBT server started, but this run provides no new conformance verdict. All attempts wrote only under scratch and left candidate inputs unchanged.
- Model exploration is bounded to the documented cases and seed-42 runs. Worker replies and session IDs in fixture tests are substitutes. The live-host run is a separate small fixture and does not establish host behavior for every conformance case.
- No acceptance proof was run or claimed.

## Handoff

No findings. R1–R8 were reviewed against the fixed candidate and comparison base. Acceptance remains for `/prove`; this review is not an acceptance verdict.

Report storage: pending. The enclosing workflow owns storage and will save and reread these exact returned bytes.

Review only; acceptance proof and merge readiness are separate.

## Next steps

1. After this report is saved and reread, run `/prove work/delivery-model-conformance.md; candidate snapshot:sha256:7a82e6bfc71d1e7fcf2318f9aa18473ed9a92e06c8f0d318b40b9be44dfcf912` to establish candidate-bound evidence for R1–R8. No PR exists; publication is not requested.