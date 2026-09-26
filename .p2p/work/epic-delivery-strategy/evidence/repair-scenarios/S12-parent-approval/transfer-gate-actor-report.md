# BLOCKED: work/parent.md

Actor context: /root/scenario_transfer_readiness. Actual leaf context; no delegation or separate verifier claimed.
Case: S12-parent-approval. Repository: /private/tmp/p2p-epic-repair-cases/S12-parent-approval/repo.
Contract: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada.
Candidate: git:159b5f50400479e1e5429b26b6c75e6d5f45682f. Comparison base: 159b5f50400479e1e5429b26b6c75e6d5f45682f. Expected destination: trunk.
Binding inputs: [{"path": "specs/registry.md", "sha256": "64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9"}].
Plan: .p2p/work/parent/slicing.md v1, approved section sha256:6ddc21b5453e16b607299bb1789e3ad93a137c9442ddb373b1665302d16e25f5.
Exact raw section retained unchanged at evidence/transfer-approved-plan.md; approval retained in ../parent/approval.md and linked history in ../parent/history where applicable.
Installed identities:
- merge-readiness/SKILL.md sha256:a8c589ea69886b023f5a6d5553d72759029423a6fc1121a9a3a831ef2a2225ad
- merge-readiness/references/acceptance-contract-protocol.md sha256:209562cadbad5a945998fe1fb370ffab5ab4ea648fc4ac720888c2d3a3ca634d
- merge-readiness/scripts/p2p_filesystem.py sha256:90e0856bd73cbf3912c5e57a6ef80b63fdb1e81771cb8d0a7c91fe401b8b4cd2

Exact commands and complete output: /private/tmp/p2p-epic-repair-cases/S12-parent-approval/transfer-gate-command-evidence.jsonl; durable checkpoint evidence/transfer-gate-command-evidence.jsonl. No live network, real GitHub, or fixture internals read. Only explicitly controlled gh PR reads used where requested.

PR: https://fixture.invalid/epic/pull/18; OPEN, draft True; head parent/complete at 159b5f50400479e1e5429b26b6c75e6d5f45682f; actual target trunk at 159b5f50400479e1e5429b26b6c75e6d5f45682f. Observed 2026-09-26T22:45:24.755705+00:00.
Saved full review.md and proof.md cover the same exact contract and candidate; complete product tree and binding inputs validate. Historical route hash text is not used as current routing authority: current raw approved bytes were extracted and retained. Parent R1-R4 assembled proof/review are required for parent assessment; child completion is not a substitute. Grouped child assessment leaves assembled parent integration, review and proof separate.
Required CI: {"name": "required-ci", "status": "COMPLETED", "conclusion": "SUCCESS"} for the current PR head. Repository approval: REVIEW_REQUIRED; supplied policy requires APPROVED. BLOCKED: repository approval is REVIEW_REQUIRED. Draft state remains unchanged. Proof and engineering review do not substitute for repository approval or CI.
Synchronization: skipped, explicitly read-only. Proposed entry: Merge readiness: BLOCKED — repository approval is REVIEW_REQUIRED; head 159b5f50400479e1e5429b26b6c75e6d5f45682f, base 159b5f50400479e1e5429b26b6c75e6d5f45682f, target trunk; local .p2p/work/parent/merge-readiness.md, applies only to this observed state. PR description remains unchanged.

Next steps:
1. Obtain current repository approval for this exact head; skill REVIEWED is not approval.
2. /merge-readiness https://fixture.invalid/epic/pull/18 after the unmet gate is resolved. No merge authority is granted.

Retained approved section follows byte-for-byte:
```markdown
## Approved delivery plan
Plan revision: v1
Approval source: Fixture owner approved these exact destinations and parent completion conditions in setup receipt approval.md. Strategy authority only; no ref or PR effects.
Parent: work/parent.md
Final destination: trunk
Integration branch: none
Integration start: none
Default choice: independent

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
| work/capture.md | independent | trunk | Acceptable if no sibling ships | remaining |
| work/lookup.md | independent | trunk | Acceptable if no sibling ships | remaining |
| work/summary.md | independent | trunk | Acceptable if no sibling ships | remaining |

Parent completion: All parent requirements, including R4 composition, need review and proof on one exact assembled candidate. Grouped parent publication also requires full matching parent reports.
Pending actions: None.

```

Saved section and recorded SHA-256 read back and compared: MATCH. Prior stage bytes retained through installed helper history.
