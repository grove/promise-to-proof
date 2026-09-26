# SETUP COMPLETE: work/lookup.md

Actor context: /root/scenario_transfer_readiness. Actual leaf context; no delegation or separate verifier claimed.
Case: S13-setup. Repository: /private/tmp/p2p-epic-repair-cases/S13-setup/repo.
Contract: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9.
Candidate: git:928231303f30c9c01d93754ce5653e9b27b42399. Comparison base: 928231303f30c9c01d93754ce5653e9b27b42399. Expected destination: epic/example.
Binding inputs: [{"path": "specs/registry.md", "sha256": "64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9"}, {"path": "work/parent.md", "sha256": "38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada"}].
Plan: .p2p/work/parent/slicing.md v1, approved section sha256:90e5ca4dc86d6c5c0910515eda4f43384f541137b366f4ca1426d55cb0ac9a60.
Exact raw section retained unchanged at evidence/transfer-approved-plan.md; approval retained in ../parent/approval.md and linked history in ../parent/history where applicable.
Installed identities:
- deliver-issue/SKILL.md sha256:94bc54a55394cb9ccd742969d8490bc4e4ce4571ed42f7177fcbff483e43d824
- deliver-issue/references/acceptance-contract-protocol.md sha256:209562cadbad5a945998fe1fb370ffab5ab4ea648fc4ac720888c2d3a3ca634d
- deliver-issue/scripts/p2p_filesystem.py sha256:90e0856bd73cbf3912c5e57a6ef80b63fdb1e81771cb8d0a7c91fe401b8b4cd2

Exact commands and complete output: /private/tmp/p2p-epic-repair-cases/S13-setup/transfer-gate-command-evidence.jsonl; durable checkpoint evidence/transfer-gate-command-evidence.jsonl. No live network, real GitHub, or fixture internals read. Only explicitly controlled gh PR reads used where requested.

Explicit repair-request.md authorizes only refs/heads/epic/example at 928231303f30c9c01d93754ce5653e9b27b42399, then non-force push to /private/tmp/p2p-epic-repair-cases/S13-setup/origin.git. Plan approval itself grants no effect; this request supplies exact setup authority.
Initial non-quiet git show-ref --verify returned 128 for missing ref; orchestration assertion stopped before writes. The corrected --quiet inspection returned 1 (absent). Both errors and all outputs are retained. git update-ref with zero old SHA created exactly the absent local ref (exit 0). Non-force git push of this exact ref to local bare origin succeeded (exit 0). Local and remote readbacks both returned 928231303f30c9c01d93754ce5653e9b27b42399. Repeated setup recovery rechecked the unchanged plan, commit, origin, local ref and remote ref, all matching, without another write or push. No overwrite, branch switch, implementation, review, proof, controller invocation, tracker effect or live network occurred. Setup pending text in the approved section remains historical; confirmed effects are recorded here separately, leaving approved bytes intact.

Next steps:
1. Requested setup and repeated recovery are complete. Stop before implementation/review/proof as requested.

Retained approved section follows byte-for-byte:
```markdown
## Approved delivery plan
Plan revision: v1
Approval source: Fixture owner approved these exact destinations and parent completion conditions in [setup receipt](approval.md). Strategy authority only; no ref or PR effects.
Parent: work/parent.md
Final destination: trunk
Integration branch: epic/example
Integration start: 928231303f30c9c01d93754ce5653e9b27b42399
Default choice: grouped

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
| work/capture.md | grouped | epic/example | Must ship with the parent | remaining |
| work/lookup.md | grouped | epic/example | Must ship with the parent | remaining |
| work/summary.md | grouped | epic/example | Must ship with the parent | remaining |

Parent completion: All parent requirements, including R4 composition, need review and proof on one exact assembled candidate. Grouped parent publication also requires full matching parent reports.
Pending actions: Create epic/example at 928231303f30c9c01d93754ce5653e9b27b42399 only under branch setup authority.

```
