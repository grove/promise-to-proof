# DRAFT: work/parent.md
Context: S1-default-8308b6e4-9618-4e18-924b-2f0cb7695f50
Contract: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada
Parent: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada
Candidate: f62b5329a22f996af6bb550cc1c7d75223af303c
Plan: .p2p/work/parent/slicing.md v1 sha256:6ddc21b5453e16b607299bb1789e3ad93a137c9442ddb373b1665302d16e25f5; exact text retained in command-evidence.txt.

Draft-only inspection. Existing work files, approvals and active routing remain unchanged. Reuse work/capture.md, work/lookup.md and work/summary.md; no new children.

| Slice | Contribution | Direct prerequisite | Check |
|---|---|---|---|
| S1 capture | work/parent.md v1:R1 | none | python3 check.py capture |
| S2 lookup | work/parent.md v1:R2 | actual S1 capture outcome | python3 check.py lookup |
| S3 summary | work/parent.md v1:R3 | none | python3 check.py summary |

Stable topological sequence: S1, S2, S3. The only blocker edge is S1 -> S2. S3 has no blocker despite appearing last. All inherit ASCII-only, no persistence/network and no automatic merge. R4 is assigned to full parent verification with python3 check.py parent on one assembled candidate, including all contributions and inherited constraints. No extra integration ticket is required for ordinary parent proof. Existing check.py assertions and registry.py public functions provide the evidence seams. Source promises and exclusions are fully allocated; this is allocation, never acceptance.

# Registry decomposition

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

## Contributions
Capture contributes R1, lookup R2, summary R3; full R4 is verified on the assembled parent. Lookup requires actual capture behavior. Parent text sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada.

Child publication requires complete child implementation, matching full review/proof against the destination tip, then /publish-pr work/<child>.md; target <resolved destination>; draft only. Branch names: work/capture, work/lookup, work/summary. Lookup requires capture integrated in its actual target candidate first. Grouped children target epic/example directly, no stacked PRs. Parent completion requires fresh full parent review and proof of the one assembled candidate, never combined child verdicts. All children route independently to trunk; no integration branch or empty parent PR. Verify the final combined trunk candidate.

Next steps:
1. Use the retained approved routing; obtain approval of any consequential new allocation before local publication.
2. /plan-acceptance work/capture.md, then work/lookup.md and work/summary.md as applicable; preserve existing contracts.
