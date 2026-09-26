# IMPLEMENTED: work/lookup.md

Actor context: /root/scenario_transfer_readiness. Actual leaf context; no delegation or separate verifier claimed.
Case: S4-transfer. Repository: /private/tmp/p2p-epic-repair-cases/S4-transfer/repo.
Contract: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9.
Candidate: git:4eff794b7d393119436349728e7fbbb283a95061. Comparison base: 4eff794b7d393119436349728e7fbbb283a95061. Expected destination: epic/example.
Binding inputs: [{"path": "specs/registry.md", "sha256": "64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9"}, {"path": "work/parent.md", "sha256": "38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada"}].
Plan: .p2p/work/parent/slicing.md v1, approved section sha256:2b401d498df37510c019ff01848d59c36bf1bdfe78a23ea2b329dc0f49d04f85.
Exact raw section retained unchanged at evidence/transfer-approved-plan.md; approval retained in ../parent/approval.md and linked history in ../parent/history where applicable.
Installed identities:
- implement-contract/SKILL.md sha256:c66733017ad8c36f1ef44ef34155b920e5c6dc3142ce339c744a4d5bb4f5d9ca
- implement-contract/references/acceptance-contract-protocol.md sha256:209562cadbad5a945998fe1fb370ffab5ab4ea648fc4ac720888c2d3a3ca634d
- implement-contract/scripts/p2p_filesystem.py sha256:90e0856bd73cbf3912c5e57a6ef80b63fdb1e81771cb8d0a7c91fe401b8b4cd2

Exact commands and complete output: /private/tmp/p2p-epic-repair-cases/S4-transfer/transfer-gate-command-evidence.jsonl; durable checkpoint evidence/transfer-gate-command-evidence.jsonl. No live network, real GitHub, or fixture internals read. Only explicitly controlled gh PR reads used where requested.

Inspection only; changes: none. Child R1 contributes parent v1:R2; parent R4 acceptance remains separate. Actual capture prerequisite and lookup checks both PASS (python3 -B check.py capture; python3 -B check.py lookup). Full candidate validation and empty product diff confirm no drift. Existing epic/example equals approved integration start and candidate; no unavailable prerequisite or setup needed. Retained approval and, for legacy transfer, original exact normalization history are locally available. No strategy reapproval is needed. No prior checkout or scratch dependency was read. No branch, product, contract, or tracker changes.

Next steps:
1. /review-implementation work/lookup.md against the comparison base above.
2. /prove work/lookup.md on the same candidate. Neither stage was invoked; this is development observation only.

Retained approved section follows byte-for-byte:
```markdown
## Approved delivery plan
Plan revision: v1
Approval source: Fixture owner approved these exact destinations and parent completion conditions in setup receipt approval.md. Strategy authority only; no ref or PR effects.
Parent: work/parent.md
Final destination: trunk
Integration branch: epic/example
Integration start: 4eff794b7d393119436349728e7fbbb283a95061
Default choice: grouped

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
| work/capture.md | grouped | epic/example | Must ship with the parent | remaining |
| work/lookup.md | grouped | epic/example | Must ship with the parent | remaining |
| work/summary.md | grouped | epic/example | Must ship with the parent | remaining |

Parent completion: All parent requirements, including R4 composition, need review and proof on one exact assembled candidate. Grouped parent publication also requires full matching parent reports.
Pending actions: None.

```

Saved section and recorded SHA-256 read back and compared: MATCH. Prior stage bytes retained through installed helper history.
