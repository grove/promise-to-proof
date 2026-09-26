# DRAFT: work/parent.md
Context: S3-default-298a367a-d1ce-4474-9c6b-c08e804d9104
Contract: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada
Parent: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada
Candidate: a5e227fe6b71924fd7e43a03686c37606a43febc
Plan: .p2p/work/parent/slicing.md v1 sha256:b61df10ce0f3ffdf7186d9a69a5052341d2377477e14b806517ede75e5e742b7; exact text retained in command-evidence.txt.

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
Integration branch: epic/example
Integration start: a5e227fe6b71924fd7e43a03686c37606a43febc
Default choice: grouped

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
| work/capture.md | independent | trunk | Acceptable if no sibling ships | remaining |
| work/lookup.md | grouped | epic/example | Must ship with the parent | remaining |
| work/summary.md | grouped | epic/example | Must ship with the parent | remaining |

Parent completion: All parent requirements, including R4 composition, need review and proof on one exact assembled candidate. Grouped parent publication also requires full matching parent reports.
Pending actions: None.

## Contributions
Capture contributes R1, lookup R2, summary R3; full R4 is verified on the assembled parent. Lookup requires actual capture behavior. Parent text sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada.

Child publication requires complete child implementation, matching full review/proof against the destination tip, then /publish-pr work/<child>.md; target <resolved destination>; draft only. Branch names: work/capture, work/lookup, work/summary. Lookup requires capture integrated in its actual target candidate first. Grouped children target epic/example directly, no stacked PRs. Parent completion requires fresh full parent review and proof of the one assembled candidate, never combined child verdicts. Grouped parent publication routes epic/example to trunk after matching full parent reports; suggested parent head is epic/example. Capture may land on trunk first; bring its required outcome into the grouped candidate before lookup.

Next steps:
1. Use the retained approved routing; obtain approval of any consequential new allocation before local publication.
2. /plan-acceptance work/capture.md, then work/lookup.md and work/summary.md as applicable; preserve existing contracts.
