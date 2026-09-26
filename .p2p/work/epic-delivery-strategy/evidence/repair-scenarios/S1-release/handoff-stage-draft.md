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

## Draft assessment

DRAFT.

Actor: /root/scenario_remaining_handoffs. One actual shared context for these cases; no delegation or independent reviewer contexts claimed.
Installed skill: /private/tmp/p2p-epic-repair-cases/S1-release/installed/slice-contract/SKILL.md sha256:72c3aa33935bf36af16e6a03f546e4cd44ccafd376014df37bd30bf290b6087a.
Bundled protocol: sha256:c916e48be9de29f423716518dc290a64b9c667bdf42b40da87dc346853957b43.
Commands and exact output: /private/tmp/p2p-epic-repair-cases/S1-release/handoff-command-evidence.jsonl. Only supplied fixture gh was used when tracker inspection was needed. No live network.
Authority: repair-request.md, local inspection and stage records only. No product, contract, ref, push, tracker, or merge effects performed.
Parent: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada; source specs/registry.md sha256:64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9.
Exact approved agreement bytes recoverable using `git show f6c7de0de6d6ee25d8d9c4d2ce0c4e8c6999e04c:work/parent.md` and the same commit's specs/registry.md. Work files remain unchanged.

## Coverage and dependencies

| Slice | Existing work | Complete outcome and qualified parent contribution | Direct prerequisite | Evidence location |
|---|---|---|---|---|
| S1 | work/capture.md | Lower-case dictionary key preserves original name; work/parent.md v1:R1 | None | registry.capture; check.py capture |
| S2 | work/lookup.md | Any case of captured key returns original; missing returns None; work/parent.md v1:R2 | S1 capture behavior in actual candidate, because lookup consumes captured keys | registry.lookup; check.py lookup |
| S3 | work/summary.md | Welcome plus one space and supplied name; work/parent.md v1:R3 | None | registry.summary; check.py summary |

All slices inherit ASCII, no persistence/network, and plain text where applicable. No new enabling ticket, platform, persistence or network work is allocated. R4 spans capture's preserved value, lookup's retrieval and summary's output; the parent workflow owns `python3 check.py parent` on one exact assembled candidate, alongside full R1-R3 checks and inherited constraints. Child evidence cannot establish parent acceptance.
Actual dependency graph: S1 -> S2; S3 has no blocker. Stable lowest-ID topological sequence: S1, S2, S3. This sequence does not add an S2 -> S3 blocker. Existing child contracts and identities are reused. No child or parent file was created or edited. Routing and agreement approvals still govern implementation readiness.

## Proposed delivery plan

Retain approved v1 without a strategy change. Final destination: trunk. Default choice: independent. Integration branch: none. Integration start: none. No child exceptions. Capture, lookup and summary each resolve to trunk because the request explicitly says each complete outcome is acceptable if the remaining children never ship. One marketing release date does not require grouping. The request identifies the existing EXPERIMENTAL flag; registry.py contains it. No additional flag implementation is proposed.
Existing approval remains at .p2p/work/parent/approval.md and the unchanged approved section above. Proposed child branches: child/capture, existing child/lookup, child/summary. No branch creation is authorized or needed for this draft. Capture and summary have no technical blocker and can land first; lookup must confirm capture behavior. Parent completion uses full review/proof on one exact combined candidate; no empty parent PR is needed for independently landed children.
Storage: .p2p/work/parent/slicing.md. Prior bytes retained by helper; original approved section preserved exactly. Draft-only authority leaves work items and all refs unchanged.

Next steps:
1. Keep the approved independent destinations. Approve any additional allocation details in this draft before local publication; no renewed strategy question is needed.
2. Continue child acceptance planning against the existing work files when authorized, and confirm lookup's capture prerequisite before implementation.
