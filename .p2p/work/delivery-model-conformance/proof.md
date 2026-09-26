# PROVEN: Test the delivery controller against the FizzBee model

Requirements: 8/8  
Counterexamples tested: 19 deliberate mutations (14 model mutations and five production guard mutations), plus the named controller boundary cases and a fresh stale-report replay.  
Contract: `work/delivery-model-conformance.md` v1  
Contract snapshot: SHA-256 `0751249534a5cf5f21d8f97250e95e4c91a3c5b27ec578f45fc5c21624167237`  
Binding source: `specs/delivery-model-conformance-source.md`, SHA-256 `7162a965fa53322a8805582756ea6137a847d72798e057dd751cc2e46c98f65a`  
Binding protocol: `docs/acceptance-contract-protocol.md`, SHA-256 `bec3503abc6ebc40356e662ca0b279be73a4da482eb1616a5c5b435509184351`  
Parent context: None. Phase 1 and Phase 2 are named prerequisites, not inherited contracts.  
Candidate: `snapshot:sha256:7a82e6bfc71d1e7fcf2318f9aa18473ed9a92e06c8f0d318b40b9be44dfcf912`  
Comparison base: `833a33647f545afb9028d03bf82d03613415ddf9`  
Candidate stability: Unchanged. Recomputed all 126 manifest entries from the fixed checkout, including content, modes, and symlink targets; they match the saved manifest and candidate key before and after checks.  
Contract stability: Unchanged. The candidate work item and agreement snapshot both hash to the contract SHA above; binding hashes and comparison base also match.  
Verification context: macOS arm64; `/opt/homebrew/bin/python3` (Python 3.14.7); FizzBee 0.5.3; MBT 0.2.0; npm lockfile package `@fizzbee/mbt` 0.1.2. Scratch and npm cache were confined to `/private/tmp/p2p-proof30b`.

## Outcome

The fixed candidate meets the full R1–R8 contract. Fresh public-controller MBT runs passed successful delivery and caught a stale-report guard removal. Retained raw traces establish the other required controller cases and guard mutations. The live-host identity issue is resolved by comparing the producer’s actual canonical-entry hashes, not decoded file-byte hashes.

I inspected the original proof session’s launch, events, completion, and historical `NOT PROVEN` report. Its R7 comparison hashed a different input than the producer. I independently recomputed the producer’s canonical JSON hash for every manifest entry and confirmed the complete 126-entry map matches both live receipts. No historical verdict or receipt was edited.

## Requirement verdicts

| ID | Observation and independent oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | The pinned MBT driver invoked the public `status` operation and rejected a deliberately wrong observation before TypeScript was selected. The retained counter experiment also catches a wrong subprocess result and reproduces the mismatch at seed 42. | [Compatibility evidence](/Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/compatibility/README.md), `commands.json`, and `controller-bad-verified.log`. This is historical language-choice evidence. | proven |
| R2 | The fresh successful-delivery run passed with real enabled actions `Start`, `Inspect`, `Review`, `Proof`, `Restart`, and two `Resume` calls. Final controller state was `REVIEWED_AND_PROVEN`, with implementation, review, and proof reports saved and five attempts; both terminal resumes preserved state. The retained suite also covers failed delivery, uncertain and known-result restart, repair exhaustion across restart, and successful repair. | Fresh command and output: `/private/tmp/p2p-proof30b/out/successful-delivery/`; retained 17-trace summary and action/state records in [controller-conformance](/Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/controller-conformance/). | proven |
| R3 | The final runner exercised authorization, stale and mistyped identity, candidate mutation, incomplete archive, interrupted storage, late result, duplicate write, repeated resume, and contested dirty file. The action traces record fresh CLI processes and returned results alongside persisted state; invalid cases end blocked or absent as expected. | `controller-conformance/summary.json` and each named case’s `fixture/actions.jsonl`, including `candidate-mutated-during-verification-42` and `contested-dirty-file-42`. | proven |
| R4 | Five mutations changed real controller guards in disposable copies while leaving the model and adapter oracle fixed. Each reached the controller and failed on `Return value mismatched`. The fresh stale-report mutant likewise failed; its persisted state contains an invalid proof generation (`-1`) and differs from the model’s expected report state. | Five mutation traces and mutation source copies in `controller-conformance/`; fresh replay output in `/private/tmp/p2p-proof30b/out/stale-report-guard-removed/`. | proven |
| R5 | `concurrent-resume` launched overlapping fresh controller processes. The loser returned `BLOCKED` with “another controller holds the work-item lock,” and the trace confirms loser state was unchanged while the winner proceeded. | `controller-conformance/concurrent-resume-42/fixture/actions.jsonl`. The evidence labels worker replies as substitutes. | proven |
| R6 | Retained traces include commands, fixture inputs, action sequences, returned observations, and saved state. A separate seed-42 stale-report replay has the same enabled action order and normalized observations as its original replay. I also ran a fresh stale-report replay. | [Replay comparison](/Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/development/replay-comparison.json); [replay evidence](/Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/controller-replay/); durable archive SHA-256 `921911ca0c654f7d7df417bb609abb89f0a4a4ae75cbcd717c521eb1b874b7b0`. | proven |
| R7 | I inspected the producer at `checks/check_p2p_delivery_host.py:29` and serializer at `p2p_filesystem.py:22`. `product_entries_sha256` is SHA-256 of canonical JSON for each full entry, including path, mode, type, and encoded content or link target. My independent full-map recomputation matched all 126 entries and the candidate key in both invocation and summary receipts. Five distinct `thread.started` IDs match their controller session IDs; event hashes match completion records, all five exits are zero, and raw preflight output records protected-path probes and network denied with scratch access allowed. | [Live identity check](/Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/live-host/product-identity-check.json); `invocation.json`, `summary.json`, raw attempt `events.jsonl`, `launch.json`, and `exit.json`; [host inspection](/Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/development/live-host-inspection.json). | proven |
| R8 | The model documentation records operation mapping, tool pins, bounds, assumptions, replay commands, unchecked behavior, and the distinction between model, substitute-backed controller, and live-host evidence. The retained 43-check model suite passed; it is treated as bounded model evidence, not proof of controller or host behavior. | [Model README](/Users/grove/projects/promise-to-proof/.p2p/tmp/issue-30/candidate/checks/delivery-model/README.md); [model-check output](/Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/development/model-checks.log). | proven |

## Commands and observations

Fresh successful-delivery run:

```sh
env PATH=/private/tmp/p2p-proof30b/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin \
  TMPDIR=/private/tmp/p2p-proof30b/tmp TMP=/private/tmp/p2p-proof30b/tmp TEMP=/private/tmp/p2p-proof30b/tmp \
  npm_config_cache=/private/tmp/p2p-proof30b/npm-cache \
  PYTHONPYCACHEPREFIX=/private/tmp/p2p-proof30b/pycache \
  FIZZBEE=/private/tmp/p2p-fizzbee-24/fizzbee-v0.5.3-macos_arm/fizz \
  FIZZBEE_MBT=/Users/grove/projects/promise-to-proof/.p2p/tmp/issue-30/compatibility/fizzbee-mbt-0.2.0-macos_arm \
  /opt/homebrew/bin/python3 /Users/grove/projects/promise-to-proof/.p2p/tmp/issue-30/candidate/checks/delivery-model/conformance.py \
  --case successful-delivery --seed 42 \
  --output-dir /private/tmp/p2p-proof30b/out/successful-delivery
```

Fresh stale-report guard replay used the same environment and runner, with `--case stale-identity --seed 42 --mutation stale-report-guard-removed --output-dir /private/tmp/p2p-proof30b/out/stale-report-guard-removed`. It failed the model comparison as required after reaching the mutated controller. The model expected a blocked result without an accepted proof report; the actual saved state retained the stale proof as invalid and reported proof generation `-1`.

The runner installed dependencies with fresh `npm ci --ignore-scripts` from the candidate’s copied lockfile. Both fresh runs passed, checked pinned tool identities, and enforced action coverage. The successful trace explored 105 model nodes to depth 8 and recorded all required enabled actions.

I also independently ran the retained full-map identity calculation before and after the checks. It recomputed the candidate key and each entry hash using sorted, compact UTF-8 JSON, then compared the entire map to both untouched live receipts; all 126 entries matched with no path differences. The standalone candidate snapshot recomputation also matched all 126 entries, the saved work-item digest, both binding hashes, and the full base SHA.

Prior independent observations inspected against underlying traces: 17 baseline controller cases, five production-guard mutations, the separate stale-mutant replay, 19 controller tests, and 43 model checks. The final full runner is the only conformance evidence reused; earlier exploratory runs with disabled model actions were excluded.

## Limitations

The FizzBee exploration is finite and bounded. Controller conformance uses substitute worker replies and fixture session IDs; it establishes controller behavior, not host provenance. Live-host evidence is a small serial delivery example and does not establish live-host concurrency. The selected host reports unknown cost and no hard monetary cap. These limits are documented and do not exceed the contract’s claims.

A filesystem helper validation attempt against the product-only checkout could not find the enclosing `.p2p` candidate record. That checkout intentionally omits those generated records; direct full-manifest and binding recomputation from the fixed checkout passed instead.

## Candidate and contract stability

The saved candidate record, fixed checkout, contract, agreement snapshot, binding inputs, comparison base, and original live receipts remained unchanged. No product or contract repair was made. The original proof session `01a0de5c-5ee1-7a10-8b60-19db2d879d76` is retained with its historical R7 hash-input mistake documented above; its other observations were reused only after checking their underlying evidence.

Report storage: pending. The enclosing workflow owns proof report storage; I have not saved this report outside the permitted scratch scope.

## Unresolved gaps

None.

## Repairs needed

None.

## Next steps

1. The enclosing workflow saves and rereads this exact report. A matching full review against base `833a33647f545afb9028d03bf82d03613415ddf9` already exists; with this proof, acceptance evidence is complete for this candidate. No PR exists, and no publication action is requested.