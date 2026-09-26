# DRAFT: reuse existing publication

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

Omitted target resolves to epic/example. Full child review/proof match git:c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f; observed remote target tip equals the review base. Capture prerequisite passes; no new sibling payload exists in the empty target diff. Existing PR 17 already matches head, target and identity marker, so this exact preview proposes ZERO commit, ref, push, PR creation, retarget or body-edit effects. No publication grant requested for a no-effect reuse. Required CI is pending, which is a readiness gate and does not block this preview.
Destination repository: fixture/epic, controlled local bare origin. Head: child/lookup at c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f; target epic/example at c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f. Existing title: Lookup names. Existing complete body retained unchanged as JSON: "Human note: keep this sentence byte-for-byte.\n<!-- grove:publish-pr repo=fixture/epic candidate=git:c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f contract=sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9 -->\n". Existing draft: true. No commit inputs or candidate mapping needed for unchanged Git commit. Operator checkout remains unchanged, with local .p2p records; no reconciliation effect authorized. Reports and approval/history are local recoverable records, not claimed remotely published.
Review/proof references: .p2p/work/lookup/review.md and proof.md; candidate.json and their byte hashes are retained in evidence below. No product edits.
Merge readiness: NOT ASSESSED by publication; separate explicitly requested assessment follows.

Next steps:
1. No publication effect is needed. Assess /merge-readiness https://fixture.invalid/epic/pull/17 independently.

Record identities:
- .p2p/work/lookup/candidate.json sha256:b0cd299b9b80d0d792cf373cccbb1b53dc21b67d4aed43fc5c7dbac82cc306bb
- .p2p/work/lookup/review.md sha256:cfd128e974196ba5b9f9820306ebe27eb74b306b10428b09e64db9397e109af2
- .p2p/work/lookup/proof.md sha256:1b2f31d7bd4444bcb1beca9c4ee37296320a9bb5507297f78fe42b59936c9afa
- .p2p/work/parent/slicing.md sha256:64ff1e1837c2600fe816fff70614377a3aa63dd7113d252c584d2e8de9718597
- .p2p/work/parent/approval.md sha256:7b14282140fcc3f4926cb8a6b78a179b82a90ed1310116ac1bcd486884dfcddd

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
