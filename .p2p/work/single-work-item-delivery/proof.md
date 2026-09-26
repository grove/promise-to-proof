# PROVEN: issue #28, single-work-item delivery

Requirements: **14/14 proven**  
Counterexamples tested: **28 live write/network attempts** and **23 deterministic controller tests**  
Contract: `work/single-work-item-delivery.md`, v1  
Contract SHA-256: `e447f13a94dae84b9af2dfc06cfb6be36900eee2c0e381a3942015245b48826d`  
Candidate: `snapshot:sha256:847704b1ef38871fc2e62529426105cc31ae029a79c11e8190c00fcb3b519259`  
Comparison base: `1a296f6ec7a064b32ce1be6a5d29f0c39df12294`  
Candidate stability: unchanged  
Contract stability: unchanged  
Report storage: pending in the enclosing workflow, which will save this exact report.

## Outcome

The v1 contract reconciles the imported issue #28 promises with the pinned optimization handoff, acceptance protocol, and delivery rules. Its 14 rows cover all four Phase 2 scope areas, plus identity, authority, evidence, and failure outcomes. I found no unresolved contract discrepancy.

I independently recomputed the candidate snapshot key from its retained manifest and checked all 118 entries against the fixed candidate’s bytes, modes, and symlink targets. Every entry matched. The contract hash, three binding-input hashes, and comparison-base Git object also matched.

The durable live-delivery record at `evidence/live-delivery-final` reports `REVIEWED_AND_PROVEN` with no blocker. Its separate tiny example has its own candidate key, `snapshot:sha256:fba8e34f9fa4246ccea677efe630aab66d24c62a93677534dbb15ce23ed362ff`; that key is distinct from issue #28’s fixed candidate. I ran that delivered example’s public `greet.py` directly: stdout was `b'hello\n'`, stderr was empty, and exit status was `0`.

The live invocation’s product key matches issue #28’s frozen snapshot. Its auxiliary file-hash map describes the parent checkout rather than the fixed snapshot manifest; all 118 entries differ. The controller and filesystem-helper source bytes used by that live run do match the fixed candidate. I treated the matching key as invocation provenance and the independent manifest recomputation as candidate identity; I did not treat the auxiliary map as proof of manifest equality.

## Requirement verdicts

| ID | Observation and independent oracle | Evidence and verdict |
|---|---|---|
| R1 | Fresh host contexts have distinct host-issued `thread.started` IDs. Live attempt records link IDs to launches, exits, and completion records. | Live tiny-delivery summary and attempt records: preflight `01a0dd78-0e9e-7361-80ac-a427a5063ad2` and `01a0dd78-ba0a-7122-9b90-1eb6fe6e1cfa`; implementation, review, and proof also have distinct IDs. **Proven.** |
| R2 | Real stage probes could write scratch but could not append to protected source, candidate, controller records, or repository Git paths by absolute path, symlink, or subprocess. | Live probe output: 28 denied attempts, zero allowed, scratch readback `ok`; the initial scratch check also got `PermissionError` opening the candidate sentinel. Network probe was denied. **Proven.** |
| R3 | A real CLI run completed implementation, review, and proof for a tiny public behavior; its saved full review and proof reports were reread and hash-checked. | `delivery.json`: `REVIEWED_AND_PROVEN`, no blocker; all five attempts complete with exit 0. Independent `python3 greet.py` observation: exact `hello\n`, empty stderr, exit 0. **Proven.** |
| R4 | Fixed snapshot key recomputes from retained bytes; all 118 manifest entries match actual candidate content and modes. Contract, binding sources, and full comparison-base object match `candidate.json`. | Independent manifest/hash check and Git object check; deterministic `test_source_agreement_binding_base_and_report_loss`, `test_reconstruct_candidate_with_retained_base`, and identity-drift tests. **Proven.** |
| R5 | Live tiny reports and required evidence are saved, retrievable, and hash-matched; missing coverage/evidence and storage failures are rejected by controller checks. | Readback of implementation, review, and proof reports matched recorded SHA-256 values; deterministic `test_missing_coverage_and_evidence`, `test_stale_and_missing_coverage`, and storage-failure coverage. **Proven.** |
| R6 | Changed agreement/candidate and stale or incomplete report returns are rejected; candidate changes require fresh verification. | Deterministic `test_agreement_and_candidate_drift`, `test_stale_and_missing_coverage`, and repair re-review/re-proof checks passed. Fixed candidate was revalidated unchanged at end. **Proven.** |
| R7 | Restart tests recover known completed work once and block unresolved launches without repeating them. | Deterministic `test_fresh_process_recovers_known_completion_once`, `test_fresh_process_uncertain_launch_blocks`, and `test_uncertain_launch_never_repeats` passed. **Proven.** |
| R8 | One repair reservation persists across failures/restarts; successful repair refreshes both verifiers. | Deterministic `test_repair_refreshes_both_and_exhaustion_persists` and `test_successful_repair_rereviews_and_reproves` passed. Live tiny summary records `repair_used: false`. **Proven.** |
| R9 | Unrelated and unfinished files survive delivery; contested dirty ownership blocks before changes. | Deterministic `test_success_source_preservation_and_retrieval` and `test_contested_dirty_blocks` passed. Live tiny invocation records source preservation. **Proven.** |
| R10 | Missing authority, widened persisted scope, hard-cap requests, and forbidden host actions are blocked. Live probes denied protected writes and network access. | Deterministic `test_missing_authority_dispatches_nothing`, `test_persisted_scope_cannot_widen`, `test_authority_hard_cap_and_expired_admission`; live config disables network, connectors/MCP, and approval escalation. **Proven.** |
| R11 | Stage records include outcomes, timestamps, elapsed durations, usage, and unknown cost where appropriate; unsuccessful cases are exercised. | Live attempt ledger has complete start/finish, elapsed time, exit, and host usage for all five stages; cost is explicitly `unknown`. Deterministic interruption/failure ledger cases passed. **Proven.** |
| R12 | Dispatch, elapsed, repair, and concurrency limits gate new work and persist across restart. | Deterministic `test_admission_no_new_effects`, `test_concurrent_controller_cannot_reserve`, and `test_authority_hard_cap_and_expired_admission`; live run retained its seven-dispatch limit and repair reservation state. **Proven.** |
| R13 | Enforced controls are separated from estimates, observations, and unsupported spend limits. | Live result explicitly says hard monetary cap unsupported, cost unknown, and elapsed limits may not stop provider billing. Fixture tests and real-host observations are separately identifiable. **Proven.** |
| R14 | Completion returns success only with matching full reports; representative failure paths return precise blockers with resumable state. | Live result is `REVIEWED_AND_PROVEN`, blocker `null`, with report paths and hashes. Deterministic admission, evidence, authority, restart, and storage-blocker cases passed. **Proven.** |

## Checks and input stability

The required write-boundary check succeeded: a disposable file under `/Users/Shared/p2p-issue-28-fixed-8lm678wl/proof-scratch` could be written and removed; append-open on `/Users/Shared/p2p-issue-28-fixed-8lm678wl/candidate/.p2p/verification-sentinel` was denied before writing.

The deterministic suite ran from the fixed candidate with Python 3.14, `TMPDIR` inside scratch, and bytecode writing disabled:

```text
PYTHONPATH=checks /opt/homebrew/opt/python@3.14/bin/python3.14 -m unittest checks.test_p2p_delivery checks.test_p2p_filesystem checks.test_verify_acceptance_bundle
Ran 23 tests
OK
P2P filesystem checks passed
```

A preliminary run using system Python 3.9 failed because that interpreter lacks `tomllib`; the selected Codex host uses Python 3.14, and the full suite passed there.

At the end, I reread `candidate.json`, recomputed its full 64-digit snapshot key, compared all 118 manifest entries to the fixed candidate, and rechecked the contract and binding hashes. No candidate, contract, or binding-input drift was observed.

## Unresolved gaps

None.

## Repairs needed

None.

**Next steps:**

1. The independent full review was still running separately at dispatch; let it finish and save its matching report. That report is separate from this proof verdict.
2. Once matching full review and proof reports are saved, acceptance evidence is complete for this candidate. No PR exists; no further action is required unless publication is wanted.