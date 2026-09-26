# DRAFT: work/parent.md
Agent context: /root/scenario_routing_batch (shared host context; fixtures are separate)
Run ID: S2-default-a4829059-bea6-4cc0-ba87-acc99ae02feb
Contract: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada
Parent: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada
Candidate: 43bef71ef80318f5adc9f3cb6b016ccb32bcbedc
Plan: .p2p/work/parent/slicing.md v1 sha256:c0cce217b1d2e045942cd2d5999c43f04aa74ed84b9b1d513f8b4ccee3ba4dc4; exact text retained in command-evidence.txt.

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
Integration start: 43bef71ef80318f5adc9f3cb6b016ccb32bcbedc
Default choice: grouped

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
| work/capture.md | grouped | epic/example | Must ship with the parent | remaining |
| work/lookup.md | grouped | epic/example | Must ship with the parent | remaining |
| work/summary.md | grouped | epic/example | Must ship with the parent | remaining |

Parent completion: All parent requirements, including R4 composition, need review and proof on one exact assembled candidate. Grouped parent publication also requires full matching parent reports.
Pending actions: None.

## Contributions
Capture contributes R1, lookup R2, summary R3; full R4 is verified on the assembled parent. Lookup requires actual capture behavior. Parent text sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada.

Child publication requires complete child implementation, matching full review/proof against the destination tip, then /publish-pr work/<child>.md; target <resolved destination>; draft only. Branch names: work/capture, work/lookup, work/summary. Lookup requires capture integrated in its actual target candidate first. Grouped children target epic/example directly, no stacked PRs. Parent completion requires fresh full parent review and proof of the one assembled candidate, never combined child verdicts. Grouped parent publication routes epic/example to trunk after matching full parent reports; suggested parent head is epic/example. Each complete child publishes directly to epic/example, then the assembled parent publishes to trunk.

Next steps:
1. Use the retained approved routing; obtain approval of any consequential new allocation before local publication.
2. /plan-acceptance work/capture.md, then work/lookup.md and work/summary.md as applicable; preserve existing contracts.
