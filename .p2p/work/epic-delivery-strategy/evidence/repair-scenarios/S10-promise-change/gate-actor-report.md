# DRAFT: reuse existing publication

Target omitted resolves to epic/example from approved grouped plan. Current PR 17 already targets epic/example; no retarget, replacement PR, commit or push is needed. Actual head and base both match candidate and full saved review/proof. Historical confirmed publication is preserved by helper history. This local preview proposes zero remote effects. CI is not a publication gate. Grouped child acceptance does not establish assembled-parent acceptance.

Actor context: /root/scenario_publication_gates. One actual shared context; no independent reviewers or delegation.
Contract: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9; exact bytes recoverable with git show c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f:work/lookup.md.
Candidate: git:c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f; comparison base c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f. Full committed product tree and binding inputs validated by installed helper; no product drift.
Evidence: evidence/gate-command-log.jsonl contains exact commands, outputs, exit status and environment. Python 3.14.7. Initial validate invocation omitted required --base; corrected validation passed. No product/ref/PR effects authorized or performed.
Plan: .p2p/work/parent/slicing.md v1; exact approved section sha256:b67b46a4cba48649504916d2b2e873fdc0fc642d0f7fdfa7a32b41fd27cf79cd. Approval source .p2p/work/parent/approval.md.
```markdown
## Approved delivery plan
Plan revision: v1
Approval source: Fixture owner approved these exact destinations and parent completion conditions in setup receipt approval.md. Strategy authority only; no ref or PR effects.
Parent: work/parent.md
Final destination: trunk
Integration branch: epic/example
Integration start: c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f
Default choice: grouped

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
| work/capture.md | grouped | epic/example | Must ship with the parent | remaining |
| work/lookup.md | grouped | epic/example | Must ship with the parent | remaining |
| work/summary.md | grouped | epic/example | Must ship with the parent | remaining |

Parent completion: All parent requirements, including R4 composition, need review and proof on one exact assembled candidate. Grouped parent publication also requires full matching parent reports.
Pending actions: None.
```

Report identities:
- .p2p/work/lookup/candidate.json sha256:b0cd299b9b80d0d792cf373cccbb1b53dc21b67d4aed43fc5c7dbac82cc306bb
- .p2p/work/lookup/review.md sha256:cfd128e974196ba5b9f9820306ebe27eb74b306b10428b09e64db9397e109af2
- .p2p/work/lookup/proof.md sha256:1b2f31d7bd4444bcb1beca9c4ee37296320a9bb5507297f78fe42b59936c9afa

Stage reports saved through installed history helper and reread. Changed paths: review.md for S12/S1, proof.md for S1 only, publication.md, merge-readiness.md where invoked, evidence/gate-command-log.jsonl, helper history, and case-root gate reports/log. Product, contracts, refs and PR bodies unchanged.

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

Final validation succeeded; git diff --exit-code passed and only .p2p/ is untracked. Evidence saved and reread through installed history helper. No live services were called.
