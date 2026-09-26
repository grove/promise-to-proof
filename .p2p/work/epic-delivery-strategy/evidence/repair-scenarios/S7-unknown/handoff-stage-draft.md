# Registry decomposition

## Approved delivery plan
Plan revision: v1
Approval source: Fixture owner approved these exact destinations and parent completion conditions in setup receipt approval.md. Strategy authority only; no ref or PR effects.
Parent: work/parent.md
Final destination: trunk
Integration branch: epic/example
Integration start: b5009be45f66cbcca73b61944888f3c4cbf5047d
Default choice: independent

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
| work/capture.md | independent | trunk | Acceptable if no sibling ships | landed |
| work/lookup.md | independent | trunk | Acceptable if no sibling ships | remaining |
| work/summary.md | independent | trunk | Acceptable if no sibling ships | remaining |

Parent completion: All parent requirements, including R4 composition, need review and proof on one exact assembled candidate. Grouped parent publication also requires full matching parent reports.
Pending actions: None.

## Contributions
Capture contributes R1, lookup R2, summary R3; full R4 is verified on the assembled parent. Lookup requires actual capture behavior. Parent text sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada.

## Strategy proposal result

DRAFT.

Actor: /root/scenario_remaining_handoffs. One actual shared context for these cases; no delegation or independent reviewer contexts claimed.
Installed skill: /private/tmp/p2p-epic-repair-cases/S7-unknown/installed/slice-contract/SKILL.md sha256:72c3aa33935bf36af16e6a03f546e4cd44ccafd376014df37bd30bf290b6087a.
Bundled protocol: sha256:c916e48be9de29f423716518dc290a64b9c667bdf42b40da87dc346853957b43.
Commands and exact output: /private/tmp/p2p-epic-repair-cases/S7-unknown/handoff-command-evidence.jsonl. Only supplied fixture gh was used when tracker inspection was needed. No live network.
Authority: repair-request.md, local inspection and stage records only. No product, contract, ref, push, tracker, or merge effects performed.
Parent: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada; source specs/registry.md sha256:64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9.
Exact approved agreement bytes recoverable using `git show b5009be45f66cbcca73b61944888f3c4cbf5047d:work/parent.md` and the same commit's specs/registry.md. Work files remain unchanged.

## Coverage and dependencies

| Slice | Existing work | Complete outcome and qualified parent contribution | Direct prerequisite | Evidence location |
|---|---|---|---|---|
| S1 | work/capture.md | Lower-case dictionary key preserves original name; work/parent.md v1:R1 | None | registry.capture; check.py capture |
| S2 | work/lookup.md | Any case of captured key returns original; missing returns None; work/parent.md v1:R2 | S1 capture behavior in actual candidate, because lookup consumes captured keys | registry.lookup; check.py lookup |
| S3 | work/summary.md | Welcome plus one space and supplied name; work/parent.md v1:R3 | None | registry.summary; check.py summary |

All slices inherit ASCII, no persistence/network, and plain text where applicable. No new enabling ticket, platform, persistence or network work is allocated. R4 spans capture's preserved value, lookup's retrieval and summary's output; the parent workflow owns `python3 check.py parent` on one exact assembled candidate, alongside full R1-R3 checks and inherited constraints. Child evidence cannot establish parent acceptance.
Actual dependency graph: S1 -> S2; S3 has no blocker. Stable lowest-ID topological sequence: S1, S2, S3. This sequence does not add an S2 -> S3 blocker. Existing child contracts and identities are reused. No child or parent file was created or edited. Routing and agreement approvals still govern implementation readiness.

## Proposed delivery plan

Plan revision: v2 proposal, not active.
Approval source: repair-request.md asks to preserve landed capture and save a proposal grouping the remaining work. Prior v1 remains intact pending activation of this exact revision.
Parent: work/parent.md
Final destination: trunk
Integration branch: epic/example
Integration start: b5009be45f66cbcca73b61944888f3c4cbf5047d
Default choice: grouped

| Child | Old destination | Proposed choice | Proposed destination | Reason | State |
|---|---|---|---|---|---|
| work/capture.md | trunk | independent | trunk | Confirmed landed by requester; preserve historical destination at b5009be45f66cbcca73b61944888f3c4cbf5047d | landed |
| work/lookup.md | trunk | default | epic/example | User requests remaining lookup grouped | remaining |
| work/summary.md | trunk | default | epic/example | User requests remaining summary grouped | remaining |

Local integration ref already exists at the proposed start; no setup effect performed. Existing local origin tracking refs agree, but no live remote assertion is made. human-notes.txt remains untouched, sha256:406db673b27baa14dd56db5770cc5e7752ee45d796f213f64b42ce85c13641a6.
PR 17 was historically observed on trunk in .p2p/work/lookup/publication.md. Actual fixture `gh pr view 17 --json number,url,state,headRefName,baseRefName,headRefOid` failed with {"error": "'17'"}. Its current existence, state, base and head remain unresolved. Do not infer that it is closed, absent, or already retargeted. No PR edit/create attempt occurred.
Pending effects: after reliable readback and exact approval, if PR 17 is open and still targets trunk, preview only its base change to epic/example. First verify its actual candidate contains only intended lookup contribution and satisfied capture prerequisite, then obtain fresh full review against current epic/example tip. Existing records supply no review/proof verdict here; full child proof is also required. A changed candidate or agreement requires both fresh review and proof. Summary's eventual child PR also targets epic/example, with its own reports. Candidate extraction, if needed, belongs to implementation.
Parent completion: all R1-R4, interaction and inherited constraints on one assembled candidate against trunk; matching parent review/proof before any parent publication. Landed capture is never moved back to integration.
Storage: .p2p/work/parent/slicing.md, old bytes retained by helper. Existing human notes, contracts, child identities, approval receipt, history and PR observation preserved.

Next steps:
1. Read PR 17 through fixture `gh pr view 17 --json number,url,state,headRefName,baseRefName,headRefOid`; require a reliable current record before planning an exact PR effect.
2. Approve and activate the exact v2 proposal through `/slice-contract work/parent.md`; no ref or PR effect is included in this approval.
3. Refresh required child review/proof at resolved targets before a separately authorized publication or retarget preview.
