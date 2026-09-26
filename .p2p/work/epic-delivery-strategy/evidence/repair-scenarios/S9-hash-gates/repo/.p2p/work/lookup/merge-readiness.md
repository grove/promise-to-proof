# BLOCKED: work/lookup.md

Actor context: /root/scenario_transfer_readiness. Actual leaf context; no delegation or separate verifier claimed.
Case: S9-hash-gates. Repository: /private/tmp/p2p-epic-repair-cases/S9-hash-gates/repo.
Contract: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9.
Candidate: git:c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f. Comparison base: c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f. Expected destination: epic/example.
Binding inputs: [{"path": "specs/registry.md", "sha256": "64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9"}, {"path": "work/parent.md", "sha256": "38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada"}].
Plan: .p2p/work/parent/slicing.md v1, approved section sha256:b86ffd9b9b6ccbd0615efbcc57d3da023e1a8a0c185303a28832aafc0490ffe2.
Exact raw section retained unchanged at evidence/transfer-approved-plan.md; approval retained in ../parent/approval.md and linked history in ../parent/history where applicable.
Installed identities:
- merge-readiness/SKILL.md sha256:a8c589ea69886b023f5a6d5553d72759029423a6fc1121a9a3a831ef2a2225ad
- merge-readiness/references/acceptance-contract-protocol.md sha256:209562cadbad5a945998fe1fb370ffab5ab4ea648fc4ac720888c2d3a3ca634d
- merge-readiness/scripts/p2p_filesystem.py sha256:90e0856bd73cbf3912c5e57a6ef80b63fdb1e81771cb8d0a7c91fe401b8b4cd2
- publish-pr/SKILL.md sha256:c1c0c65b5d588bba53f464a2b52ca2c4eb239d390d2c470e89b4f2a7ce8f0884
- publish-pr/references/acceptance-contract-protocol.md sha256:209562cadbad5a945998fe1fb370ffab5ab4ea648fc4ac720888c2d3a3ca634d
- publish-pr/scripts/p2p_filesystem.py sha256:90e0856bd73cbf3912c5e57a6ef80b63fdb1e81771cb8d0a7c91fe401b8b4cd2

Exact commands and complete output: /private/tmp/p2p-epic-repair-cases/S9-hash-gates/transfer-gate-command-evidence.jsonl; durable checkpoint evidence/transfer-gate-command-evidence.jsonl. No live network, real GitHub, or fixture internals read. Only explicitly controlled gh PR reads used where requested.

PR: https://fixture.invalid/epic/pull/17; OPEN, draft True; head child/lookup at c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f; actual target epic/example at c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f. Observed 2026-09-26T22:45:25.122658+00:00.
Saved full review.md and proof.md cover the same exact contract and candidate; complete product tree and binding inputs validate. Historical route hash text is not used as current routing authority: current raw approved bytes were extracted and retained. Parent R1-R4 assembled proof/review are required for parent assessment; child completion is not a substitute. Grouped child assessment leaves assembled parent integration, review and proof separate.
Required CI: {"name": "required-ci", "status": "IN_PROGRESS", "conclusion": null} for the current PR head. Repository approval: APPROVED; supplied policy requires APPROVED. BLOCKED: required-ci is IN_PROGRESS, conclusion null. Draft state remains unchanged. Proof and engineering review do not substitute for repository approval or CI.
Synchronization: skipped, explicitly read-only. Proposed entry: Merge readiness: BLOCKED — required-ci is IN_PROGRESS, conclusion null; head c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f, base c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f, target epic/example; local .p2p/work/lookup/merge-readiness.md, applies only to this observed state. PR description remains unchanged.

Next steps:
1. Wait for required-ci SUCCESS for this exact head; use /fix-pr https://fixture.invalid/epic/pull/17 if it fails.
2. /merge-readiness https://fixture.invalid/epic/pull/17 after the unmet gate is resolved. No merge authority is granted.

Retained approved section follows byte-for-byte:
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
