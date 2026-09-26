# REVIEWED and PROVEN: issue #30

[Source issue](https://github.com/grove/promise-to-proof/issues/30). Full local delivery of R1–R8 is complete. The stateful FizzBee conformance suite drives the real controller CLI, observes persisted state across restarts, tests overlapping CLI calls, catches five real guard mutations, and retains reproducible traces. The issue-owned changes are integrated in `/Users/grove/projects/promise-to-proof` on `main`.

## Exact agreement and candidate

- Canonical contract: [work/delivery-model-conformance.md](../../../work/delivery-model-conformance.md), revision v1; SHA-256 `0751249534a5cf5f21d8f97250e95e4c91a3c5b27ec578f45fc5c21624167237`.
- Candidate: `snapshot:sha256:7a82e6bfc71d1e7fcf2318f9aa18473ed9a92e06c8f0d318b40b9be44dfcf912`. All 126 complete product entries are recoverable in [candidate.json](candidate.json); exact hashed manifest bytes are in [snapshots/candidate.manifest.json](snapshots/candidate.manifest.json).
- Full comparison base: `833a33647f545afb9028d03bf82d03613415ddf9`; recoverable base tree in [snapshots/base.json](snapshots/base.json).
- Binding protocol SHA-256: `bec3503abc6ebc40356e662ca0b279be73a4da482eb1616a5c5b435509184351`.
- Binding pinned source SHA-256: `7162a965fa53322a8805582756ea6137a847d72798e057dd751cc2e46c98f65a`.
- No parent contract. The pinned Phase 1 and Phase 2 prerequisites were inspected; source import and amendments are retained in `evidence/issue-import.json` and `evidence/issue-recheck.json`.

The integrated product tree was compared in full with the saved manifest. All bytes, modes and symlink targets match. `.p2p/` is excluded from the product identity. The candidate was reconstructed before independent handoff, and its complete 64-character digest was recomputed from saved bytes. Both final reports bind the exact same contract, candidate and base. See [final validation](host/final-validation.json) and [integration record](host/integration.json).

The starting source commit was `b217049db5de5df2cc5b138f5ce1cc64b68575fd`. Concurrent user roadmap commits were preserved, and the isolated base was aligned to the final comparison base before review and proof. Product changes comprise the conformance README, model, TypeScript adapter, Python runner/bridge and npm package files, plus the canonical contract and pinned source. Production controller and original fixture/model code have no implementation delta.

## Reports and independent contexts

- [Implementation](implementation.md), native agent `/root/implement_conformance`; actual invocation/completion retained under `host/native-implementation/`.
- [Full REVIEWED report](review.md), independent session `01a0de75-50c1-73d0-b916-c51856d1a086`. Its initial invocation is `host/review-recheck/`; `host/review-clarification/` records a same-reviewer reassessment without product changes.
- [Full PROVEN report](proof.md), independent session `01a0de75-5908-7a23-89e8-0b1c0410310d`, with exact launch, raw events and completion under `host/proof-recheck/`.
- Original independent proof session `01a0de5c-5ee1-7a10-8b60-19db2d879d76` executed the full runtime checks; its full raw observations remain under `host/proof/` and `evidence/proof-run.tar.gz`.

The user explicitly approved sandboxed Codex CLI stages. Actual preflight sessions `01a0de2b-9e26-76f0-8d49-9510baa769e2` and `01a0de30-17a2-7380-bb67-01db81966a94` verified the read-only input/scratch-write boundary before implementation. Review and proof used separate contexts with candidate, base and agreement outside their writable scratch. Their actual session IDs and event hashes were read back; process IDs were not substituted for agent identities.

## Observed checks and retrievable evidence

- 17 stateful baseline scenarios passed, including success, failure, restart recovery, repair and repair exhaustion, every requested fault family, dirty-file preservation, repeated resume and two overlapping controller processes.
- Five mutations of actual controller guards were detected. The stale-report mutation was independently replayed and reproduced the incorrect persisted proof report and normalized state mismatch.
- The original 19 controller tests and all 43 finite model checks passed in independent proof.
- The live-host tiny delivery passed with five distinct genuine host sessions, matching launch/event/completion records, actual public output and saved state, and protected-write denials. The original product and source remained unchanged.
- The final proof recheck inspected the full retained independent evidence, recomputed live identities, and ran fresh public baseline and stale-guard observations.

The original proof scratch `/private/tmp/p2p-proof30` is retained in [proof-run.tar.gz](evidence/proof-run.tar.gz), with [inventory and path mapping](evidence/proof-run-inventory.json). The recheck scratch `/private/tmp/p2p-proof30b` is retained in [proof-recheck.tar.gz](evidence/proof-recheck.tar.gz), with [inventory and path mapping](evidence/proof-recheck-inventory.json). Archive member paths preserve report references relative to their original scratch roots. Exact dependency lockfiles, tool pins, invocation arguments, outputs, mutation copies and fixture records are retained; disposable dependency caches are excluded.

Additional evidence: [compatibility checkpoint](evidence/compatibility/PORTABLE-README.md), [development evidence](evidence/README.md), [live-host summary](evidence/live-host/summary.json), [portable full live records](evidence/live-host-run.tar.gz), [live entry-identity check](evidence/live-host/product-identity-check.json), and `evidence/review-diagnostics.tar.gz` / `evidence/review-recheck.tar.gz`. The live archive also retains nested fixture Git metadata, so its records remain transferable through Git.

One evidence-only repair/recheck cycle was used. The first proof compared raw-file hashes with canonical-entry hashes; [repair.md](repair.md) and the independently rerun [identity-format check](evidence/live-host/identity-format.md) resolve that interpretation. No original receipt or historical verdict was edited. A later optimization-mode concern was withdrawn by its owning reviewer because that mode is outside the documented invocation; the earlier report remains historical. No further product correction occurred.

## Limits and authority

Evidence covers the documented finite cases under ordinary Python execution. Model evidence, substitute worker replies, and actual serial live-host evidence are separate. CLI overlap does not prove concurrent live agent execution, and these bounded checks do not establish all possible host behavior or interleavings.

Reports were saved and reread exactly. Their historical “storage pending” statements are satisfied by this handoff, not rewritten. No unresolved requirement, evidence, storage or identity gap remains. No commit, push, tracker write, PR, merge or deployment was performed.

Next steps:

1. Local delivery needs no further action. Publication is optional and requires separate authorization.
