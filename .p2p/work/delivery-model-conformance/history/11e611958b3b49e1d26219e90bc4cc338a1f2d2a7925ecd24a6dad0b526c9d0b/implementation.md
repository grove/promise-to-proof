# PARTIAL: Test the delivery controller against the FizzBee model

Contract: `work/delivery-model-conformance.md` v1, SHA-256 `0751249534a5cf5f21d8f97250e95e4c91a3c5b27ec578f45fc5c21624167237`.
Scope: whole contract, R1-R8. No parent contract. No agreement or binding-input changes.
Candidate before: base `a38045968c8d4d551a9e3a1f8bf14fed8bd4b481` plus the enclosing workflow's explicitly owned incomplete draft. The draft catalogue model and adapter were replaced. Its production archive-schema change and fixture edits were reverted.
Candidate after: `snapshot:sha256:7a82e6bfc71d1e7fcf2318f9aa18473ed9a92e06c8f0d318b40b9be44dfcf912`.
Recoverable content: `candidate.json`, with all 126 product entries and their bytes, modes, and symlink targets. The entire `.p2p/` tree is excluded.
Review base: `833a33647f545afb9028d03bf82d03613415ddf9`. The enclosing workflow aligned the isolated checkout with the user's later roadmap-only commit before capture. It verified that all task implementation bytes and modes were unchanged by that alignment.
Binding inputs: protocol SHA-256 `bec3503abc6ebc40356e662ca0b279be73a4da482eb1616a5c5b435509184351`; pinned Phase 3 source SHA-256 `7162a965fa53322a8805582756ea6137a847d72798e057dd751cc2e46c98f65a`.

All local implementation and substitute-backed checks are complete. R7's live-host check is being run by the enclosing workflow against its exact reconstruction. Until its real receipts are inspected, material development validation remains incomplete.

## Changes

Product changes are confined to `checks/delivery-model/`:

- `conformance.fizz` declares independent stateful transitions and safety assertions at real serial controller boundaries.
- `conformance-adapters.ts` connects generated FizzBee operations to one persistent fixture per trace. It contains pause-point scheduling metadata, with no expected controller results.
- `conformance_bridge.py` invokes actual fresh-process controller CLI operations, uses the existing `FakeTransport` only for worker replies, injects boundary crashes and corruption, runs overlapping resume processes, and reads actual output and saved records.
- `conformance.py` runs pinned model exploration, generates and compiles the official TypeScript registry, executes MBT, rejects missing coverage and validation errors, applies actual controller guard mutations in disposable copies, and retains replayable evidence.
- `package.json` and `package-lock.json` pin the demonstrated TypeScript runtime dependencies.
- `README.md` documents the operation mapping, Phase 1 refinement, commands, bounds, mutation procedure, replay, and evidence classes.

The canonical contract and pinned source entered this isolated tree through the enclosing planning workflow and are preserved exactly. Production controller, original fixtures, original `delivery.fizz`, and `check.py` have no implementation diff. No Git metadata, refs, or index was written by this stage. Fixture Git setup and commits occurred only inside disposable test repositories. No stage review, acceptance proof, publication, or external message was invoked.

## Requirement handoff

| ID | Implementation reference | Direct check and observed result | Remaining gap |
|---|---|---|---|
| R1 | Pinned tool validation in `conformance.py`; TypeScript adapter selected from the existing checkpoint | `evidence/compatibility/README.md`, `PORTABLE-README.md`, and portable good/bad/replay logs establish actual `status`, a caught deliberately wrong result, and seed-42 replay before language choice. Final generator SHA-256 independently matched the release pin. | None in local development evidence. |
| R2 | Stateful `Start`, `Review`, `Proof`, `Restart`, `Resume` actions; fresh CLI process for each enabled operation | All named successful, failed, known-return, uncertain-launch, repeated-resume, and repair-exhaustion cases passed. Both repair branches executed two full review/proof generations on the same invocation. Saved attempts, completion count, reports, identities, current bytes, and repair allowance matched the model. | None in local development evidence. |
| R3 | Model corruption and storage transitions; bridge edits actual authoritative saved inputs | All ten specified cases passed, with public results and saved-state observations. Stale identity uses the real earlier pre-implementation candidate identity. Candidate mutation prevents proof acceptance and completion. Successful repair requires fresh full REVIEWED and PROVEN reports for candidate generation two. Incomplete archive removes authoritative base-manifest content. Contested dirty bytes remain unchanged. | None in local development evidence. |
| R4 | `MUTATIONS` edits real controller source in disposable copies, without changing model or adapter oracles | Five mutants produced MBT return-value mismatches: stale report, conflicting duplicate report, late receipt, repair bound, and local authority. Stale-guard removal persisted an invalid proof even though the later completion guard still blocked. The model caught completed-attempt count 5 and proof presence instead of expected count 4 and no proof. Exact edits, output, model traces, controller results, and saved state are retained. | None in local development evidence. |
| R5 | `Overlap` starts two actual `resume` subprocesses against one work item with a lock rendezvous | `concurrent-resume-42` passed. The loser returned the lock blocker while the winner remained live. The loser changed no persisted state; the winner advanced exactly one review. The selected OS supports this CLI admission overlap. Worker replies are substitutes. | Live-host evidence establishes serial host behavior separately, not concurrent agent execution. |
| R6 | Per-case seed, retained model and fixture, exact invocation records, documented replay command | Every case and mutant has a replay command in its observation. The stale mutant was rerun at seed 42 and reproduced the identical enabled action sequence and normalized observed projections. See `evidence/development/replay-comparison.json`. | None in local development evidence. |
| R7 | Separate model, substitute-controller, and live-host evidence directories; existing live-host checker reused | Model and fixture classes are retained and explicitly labeled. No fixture session ID or worker-provided field is treated as host provenance. Enclosing workflow is running the fixed-candidate live check. | Actual live result, host-issued session receipts, and saved-state inspection pending. |
| R8 | Phase 3 sections in `checks/delivery-model/README.md` | Documents tool and generator pins, configurable paths, scratch-only generated output, public operation mapping, serial refinement, DISABLED proposal behavior, exact coverage checks, replay, state bounds, host limits, and unchecked behavior. | None. |

## Checks and limitations

Executed from the isolated checkout with `/opt/homebrew/bin/python3`, Python 3.14:

```sh
/opt/homebrew/bin/python3 -m unittest discover -s checks -p test_p2p_delivery.py -v
/opt/homebrew/bin/python3 checks/delivery-model/check.py --fizz /private/tmp/p2p-fizzbee-24/fizzbee-v0.5.3-macos_arm/fizz --output-dir .p2p/work/delivery-model-conformance/evidence/model-checks
/opt/homebrew/bin/python3 checks/delivery-model/conformance.py --fizz /private/tmp/p2p-fizzbee-24/fizzbee-v0.5.3-macos_arm/fizz --mbt /Users/grove/projects/promise-to-proof/.p2p/tmp/issue-30/compatibility/fizzbee-mbt-0.2.0-macos_arm --node-modules /Users/grove/projects/promise-to-proof/.p2p/tmp/issue-30/compatibility/node_modules --output-dir .p2p/tmp/mbt-strict3 --all-mutations
/opt/homebrew/bin/python3 checks/delivery-model/conformance.py --fizz /private/tmp/p2p-fizzbee-24/fizzbee-v0.5.3-macos_arm/fizz --mbt /Users/grove/projects/promise-to-proof/.p2p/tmp/issue-30/compatibility/fizzbee-mbt-0.2.0-macos_arm --node-modules /Users/grove/projects/promise-to-proof/.p2p/tmp/issue-30/compatibility/node_modules --output-dir .p2p/tmp/mbt-replay --case stale-identity --mutation stale-report-guard-removed --seed 42
```

Results: 19 original controller tests passed; all 43 original Phase 1 checks passed; 17 stateful baseline cases and five actual controller mutants passed their expected checks; stale-mutant replay matched. Across the 22 model explorations, the graphs contained 2,382 nodes, with maximum observed depth 11, below the 256-action cutoff. TypeScript generation and compilation passed. `git diff --check` passed. The final generator-pin check passed. After those full runs, only the README release URL and the runner's stricter generator hash validation changed; no behavioral model, controller, adapter, or fixture bytes changed.

The sandbox initially blocked the MBT localhost listener. The enclosing authorization allowed tool escalation for these disposable checks, and the completed runs used it. No agent sandbox was disabled. Historical runs that used unsupported Python or unmatched disabled actions are retained under `evidence/invalidated-development/` and explicitly invalidated. Their earlier apparent successes are not reused.

The final runner requires Python 3.11 or newer end-to-end, explicit no-op returns for out-of-phase proposals, exact enabled action counts, and no adapter-execution or unmatched-model-link errors. Passing driver exit alone never establishes coverage. Runtime dependencies and generated files live in output scratch, so the command can run against a protected fixed candidate.

The model bounds one work item, one invocation per trace, serial verifiers, one repair, one corruption family, one optional status read, and two terminal resumes. It does not establish arbitrary host behavior, agent judgment adequacy, all write interleavings, or cryptographic collision resistance. `FakeTransport` returns host-shaped fixture records only. The original finer-grained Phase 1 model remains intact.

## Decisions and next step

No pending amendment or unresolved product decision. The smallest complete change was a conformance suite around the existing controller. No production archive schema was needed: corrupting the authoritative retained base manifest exercises the existing recoverability guard, while absence of a redundant bundle alone is not a sound failure oracle.

Exact remaining external command, from the protected reconstructed candidate:

```sh
/opt/homebrew/bin/python3 checks/check_p2p_delivery_host.py --output-dir ABSOLUTE_NEW_EVIDENCE_DIRECTORY
```

Expected result: exit zero; summary `passed`, `code_unchanged`, and `source_preserved` all true; `product_key` equals `snapshot:sha256:7a82e6bfc71d1e7fcf2318f9aa18473ed9a92e06c8f0d318b40b9be44dfcf912`; actual distinct host-issued session IDs and matching controller completion receipts retained for all stages. Retain `invocation.json`, `stdout.json`, `stderr.txt`, `summary.json`, and the full `tiny-source/.p2p/work/tiny/` record tree. Inspect those actual records before completing R7's development handoff.

Report storage: `.p2p/work/delivery-model-conformance/implementation.md` in the isolated checkout. Candidate and evidence are adjacent and ready for authorized transfer to the source work-item directory.

Implementation report only; independent acceptance requires `/prove`.

Next steps:

1. Inspect the enclosing workflow's live-host result and receipts from the exact command above, then update this development report without changing the candidate.
2. `/review-implementation work/delivery-model-conformance.md`
3. `/prove work/delivery-model-conformance.md`
