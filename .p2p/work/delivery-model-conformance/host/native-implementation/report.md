# IMPLEMENTED: Test the delivery controller against the FizzBee model

Contract: `work/delivery-model-conformance.md` v1, SHA-256 `0751249534a5cf5f21d8f97250e95e4c91a3c5b27ec578f45fc5c21624167237`.
Scope: whole contract, R1-R8. No parent contract. No agreement or binding-input changes.
Candidate before: base `a38045968c8d4d551a9e3a1f8bf14fed8bd4b481` plus the enclosing workflow's explicitly owned incomplete draft. The draft catalogue model and adapter were replaced. Its production archive-schema change and fixture edits were reverted.
Candidate after: `snapshot:sha256:7a82e6bfc71d1e7fcf2318f9aa18473ed9a92e06c8f0d318b40b9be44dfcf912`.
Recoverable content: `candidate.json`, with all 126 product entries and their bytes, modes, and symlink targets. The entire `.p2p/` tree is excluded.
Review base: `833a33647f545afb9028d03bf82d03613415ddf9`. The enclosing workflow aligned the isolated checkout with the user's later roadmap-only commit before capture. It verified that all task implementation bytes and modes were unchanged by that alignment.
Binding inputs: protocol SHA-256 `bec3503abc6ebc40356e662ca0b279be73a4da482eb1616a5c5b435509184351`; pinned Phase 3 source SHA-256 `7162a965fa53322a8805582756ea6137a847d72798e057dd751cc2e46c98f65a`.

All R1-R8 implementation obligations and development checks are complete. The enclosing workflow ran the live-host check against its exact reconstruction. I inspected the actual host-issued sessions, launch configuration, event hashes, completion receipts, full reports, saved state, and fixed-candidate summary.

## Changes

Product changes are confined to `checks/delivery-model/`:

- `conformance.fizz` declares independent stateful transitions and safety assertions at real serial controller boundaries.
- `conformance-adapters.ts` connects generated FizzBee operations to one persistent fixture per trace. It contains pause-point scheduling metadata, with no expected controller results.
- `conformance_bridge.py` invokes actual fresh-process controller CLI operations, uses the existing `FakeTransport` only for worker replies, injects boundary crashes and corruption, runs overlapping resume processes, and reads actual output and saved records.
- `conformance.py` runs pinned model exploration, generates and compiles the official TypeScript registry, executes MBT, rejects missing coverage and validation errors, applies actual controller guard mutations in disposable copies, and retains replayable evidence.
- `package.json` and `package-lock.json` pin the demonstrated TypeScript runtime dependencies.
- `README.md` documents the operation mapping, Phase 1 refinement, commands, bounds, mutation procedure, replay, and evidence classes.

The canonical contract and pinned source entered this isolated tree through the enclosing planning workflow and are preserved exactly. Production controller, original fixtures, original `delivery.fizz`, and `check.py` have no implementation diff. No Git metadata, refs, or index was written by this stage. Fixture Git setup and commits occurred only inside disposable test repositories. This stage did not invoke review or proof for issue 30, publish, or send external messages.

## Requirement handoff

| ID | Implementation reference | Direct check and observed result | Remaining gap |
|---|---|---|---|
| R1 | Pinned tool validation in `conformance.py`; TypeScript adapter selected from the existing checkpoint | `evidence/compatibility/README.md`, `PORTABLE-README.md`, and portable good/bad/replay logs establish actual `status`, a caught deliberately wrong result, and seed-42 replay before language choice. Final generator SHA-256 independently matched the release pin. | None in local development evidence. |
| R2 | Stateful `Start`, `Review`, `Proof`, `Restart`, `Resume` actions; fresh CLI process for each enabled operation | All named successful, failed, known-return, uncertain-launch, repeated-resume, and repair-exhaustion cases passed. Both repair branches executed two full review/proof generations on the same invocation. Saved attempts, completion count, reports, identities, current bytes, and repair allowance matched the model. | None in local development evidence. |
| R3 | Model corruption and storage transitions; bridge edits actual authoritative saved inputs | All ten specified cases passed, with public results and saved-state observations. Stale identity uses the real earlier pre-implementation candidate identity. Candidate mutation prevents proof acceptance and completion. Successful repair requires fresh full REVIEWED and PROVEN reports for candidate generation two. Incomplete archive removes authoritative base-manifest content. Contested dirty bytes remain unchanged. | None in local development evidence. |
| R4 | `MUTATIONS` edits real controller source in disposable copies, without changing model or adapter oracles | Five mutants produced MBT return-value mismatches: stale report, conflicting duplicate report, late receipt, repair bound, and local authority. Stale-guard removal persisted an invalid proof even though the later completion guard still blocked. The model caught completed-attempt count 5 and proof presence instead of expected count 4 and no proof. Exact edits, output, model traces, controller results, and saved state are retained. | None in local development evidence. |
| R5 | `Overlap` starts two actual `resume` subprocesses against one work item with a lock rendezvous | `concurrent-resume-42` passed. The loser returned the lock blocker while the winner remained live. The loser changed no persisted state; the winner advanced exactly one review. The selected OS supports this CLI admission overlap. Worker replies are substitutes. | Live-host evidence establishes serial host behavior separately, not concurrent agent execution. |
| R6 | Per-case seed, retained model and fixture, exact invocation records, documented replay command | Every case and mutant has a replay command in its observation. The stale mutant was rerun at seed 42 and reproduced the identical enabled action sequence and normalized observed projections. See `evidence/development/replay-comparison.json`. | None in local development evidence. |
| R7 | Separate model, substitute-controller, and live-host evidence directories; existing live-host checker reused | Model, fixture, and live classes are retained separately. The actual live check passed against the exact fixed product key. Five distinct host-issued sessions, successful receipts, and both actual isolation probes were inspected. See `evidence/development/live-host-inspection.json` and `evidence/live-host/`. No fixture identity or worker-provided field establishes provenance. | None. |
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

Executed external command, from the enclosing workflow's protected reconstructed candidate:

```sh
/opt/homebrew/bin/python3 checks/check_p2p_delivery_host.py --output-dir /Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/live-host
```

Observed result: exit zero; summary `passed`, `code_unchanged`, and `source_preserved` are all true. The product key exactly matches `snapshot:sha256:7a82e6bfc71d1e7fcf2318f9aa18473ed9a92e06c8f0d318b40b9be44dfcf912`. The controller finished `REVIEWED_AND_PROVEN` with five completed attempts and no repair. Its normalized acceptance bundle passed the existing checker. Actual review and proof reports bind the same captured tiny candidate and cover its full R1 requirement. The proof host event contains the actual successful `greet.py` assertion execution.

Actual host-issued sessions, read from `thread.started` events and matched to controller completion receipts:

| Stage | Host session |
|---|---|
| preflight-1 | `01a0de4d-d57a-72d0-a0b9-019ff03a486a` |
| preflight-2 | `01a0de4e-5f50-7a53-9f65-7969d9159054` |
| implementation | `01a0de4e-f14c-7d53-8285-f042b0d75ad6` |
| review | `01a0de51-179e-71d1-bc2e-00471d6a9c14` |
| proof | `01a0de52-e43d-7ca3-bc12-df0b0f5ff737` |

Both actual preflight commands ran the retained probe scripts and exited zero. Each returned 29 observations, with protected writes and network denied and scratch writes allowed. Inspection confirmed the recorded workspace-write sandbox and disabled approval escalation. Event hashes, attempt IDs, exact input identities, and controller receipts matched. `evidence/development/live-host-inspection.json` records these assertions and the actual observations. `evidence/live-host/` retains invocation, output, summary, and the full live record tree. This establishes serial host behavior. CLI overlap remains the separately labeled substitute-backed two-process case.

No material development validation remains unavailable.

Report storage: `.p2p/work/delivery-model-conformance/implementation.md` in the isolated checkout. Candidate and evidence are adjacent and ready for authorized transfer to the source work-item directory.

Implementation report only; independent acceptance requires `/prove`.

Next steps:

1. `/review-implementation work/delivery-model-conformance.md`
2. `/prove work/delivery-model-conformance.md`
