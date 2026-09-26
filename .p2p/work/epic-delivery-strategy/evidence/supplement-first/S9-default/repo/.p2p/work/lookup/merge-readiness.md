# BLOCKED: https://fixture.invalid/epic/pull/17

Actor context: /root/scenario_publication_gates. Read-only assessment at 2026-09-26T22:24:06.278829+00:00.
Destination: epic/example; actual base epic/example at c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f; exact head c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f. Contract work/lookup.md v1 SHA-256 fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9. Full product tree and all binding hashes validated against candidate.json. Current PR was reread through the configured simulator, and actual origin tips match.

Policy supplied by fixture owner: required-ci COMPLETED SUCCESS for current head and current repository approval. reviewDecision APPROVED is authoritative. Observed checks: [{"name": "required-ci", "status": "IN_PROGRESS", "conclusion": null}]. Approval: APPROVED. Saved review .p2p/work/lookup/review.md and proof .p2p/work/lookup/proof.md were separately evaluated.

Gates: required-ci is not completed SUCCESS for current head

Approved plan v1 SHA-256 b67b46a4cba48649504916d2b2e873fdc0fc642d0f7fdfa7a32b41fd27cf79cd; exact retained text in publication.md and .p2p/work/parent/slicing.md. Grouped child parent integration/review/proof remain separate.

Draft state observed: True. READY here assesses supplied gates; it does not change draft state, authorize merge, or perform the separate human ready-for-review transition. Required check status is the current-head rollup from the fixture service; no separate run SHA is exposed.
Synchronization: skipped by explicit read-only request. PR body unchanged. Evidence: evidence/gate-command-log.jsonl.

Proposed entry: Merge readiness: BLOCKED; observed 2026-09-26T22:24:06.278829+00:00; head c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f; base c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f; local report .p2p/work/lookup/merge-readiness.md; required-ci is not completed SUCCESS for current head. Applies only to this observed state.

Next steps:
1. Wait for required-ci to complete successfully, then /merge-readiness https://fixture.invalid/epic/pull/17; read-only. Do not infer parent acceptance.
