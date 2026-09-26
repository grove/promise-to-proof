# Registry decomposition

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

## Contributions
Capture contributes R1, lookup R2, summary R3; full R4 is verified on the assembled parent. Lookup requires actual capture behavior. Parent text sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada.

## Amendment handoff

BLOCKED for dependent strategy completion.

Actor: /root/scenario_remaining_handoffs. One actual shared context for these cases; no delegation or independent reviewer contexts claimed.
Installed skill: /private/tmp/p2p-epic-repair-cases/S10-promise-change/installed/slice-contract/SKILL.md sha256:72c3aa33935bf36af16e6a03f546e4cd44ccafd376014df37bd30bf290b6087a.
Bundled protocol: sha256:c916e48be9de29f423716518dc290a64b9c667bdf42b40da87dc346853957b43.
Commands and exact output: /private/tmp/p2p-epic-repair-cases/S10-promise-change/handoff-command-evidence.jsonl. Only supplied fixture gh was used when tracker inspection was needed. No live network.
Authority: repair-request.md, local inspection and stage records only. No product, contract, ref, push, tracker, or merge effects performed.
Parent: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada; source specs/registry.md sha256:64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9.
Exact approved agreement bytes recoverable using `git show c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f:work/parent.md` and the same commit's specs/registry.md. Work files remain unchanged.

## Coverage and dependencies

| Slice | Existing work | Complete outcome and qualified parent contribution | Direct prerequisite | Evidence location |
|---|---|---|---|---|
| S1 | work/capture.md | Lower-case dictionary key preserves original name; work/parent.md v1:R1 | None | registry.capture; check.py capture |
| S2 | work/lookup.md | Any case of captured key returns original; missing returns None; work/parent.md v1:R2 | S1 capture behavior in actual candidate, because lookup consumes captured keys | registry.lookup; check.py lookup |
| S3 | work/summary.md | Welcome plus one space and supplied name; work/parent.md v1:R3 | None | registry.summary; check.py summary |

All slices inherit ASCII, no persistence/network, and plain text where applicable. No new enabling ticket, platform, persistence or network work is allocated. R4 spans capture's preserved value, lookup's retrieval and summary's output; the parent workflow owns `python3 check.py parent` on one exact assembled candidate, alongside full R1-R3 checks and inherited constraints. Child evidence cannot establish parent acceptance.
Actual dependency graph: S1 -> S2; S3 has no blocker. Stable lowest-ID topological sequence: S1, S2, S3. This sequence does not add an S2 -> S3 blocker. Existing child contracts and identities are reused. No child or parent file was created or edited. Routing and agreement approvals still govern implementation readiness.

Requested amendment: [requested-amendment.md](../../../requested-amendment.md). Exact request: "User amendment: lookup must additionally accept Unicode names and preserve Unicode case semantics. This changes the approved ASCII-only promise; treat as an unresolved requested product change, not approval of new contract bytes."
Affected agreement: work/lookup.md v1:R1 and inherited ASCII boundary; work/parent.md v1:R2 with R1 capture-key and R4 composition implications; specs/registry.md ASCII exclusion. Old promise accepts ASCII names only and preserves original values. Proposed promise extends name support to Unicode with undefined case semantics. This is a material product change, not a destination-only update.
Unresolved focused question for acceptance planning: Which Unicode case-equivalence and normalization rules must capture and lookup share, including multi-character case mappings, and must original code points be preserved in returned names? Do not choose a lower/casefold/normalization algorithm as an unapproved product decision.
Authority permits considering the request and retaining this handoff, not approving new contract bytes. No revision or contract matrix was changed. Amendment source is retained above in the source-linked decomposition; source/contract files remain unchanged under explicit no-edit authority. plan-acceptance must reconcile source and affected parent/child promises, preserve IDs/history, increment semantic revision for approved changes, and obtain approval before dependent implementation.

## Proposed delivery plan

Active v1 remains grouped to epic/example for all children, final destination trunk. "Lookup may now be independent" is tentative. A possible v2 would retain grouped default and set only lookup independent to trunk if its complete revised outcome is acceptable without remaining children. No routing change is activated while the product outcome is unresolved. Integration origin remains the v1 exact start; no ref action is proposed.
PR 17 readback is OPEN, head child/lookup at c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f, base epic/example. A future approved independent strategy would require a new preview of epic/example -> trunk and scope inspection for unfinished sibling payload. No retarget is authorized.
Saved review/proof describe the ASCII v1 candidate only. They do not prove Unicode support. After approved revised agreements and any implementation, capture the exact candidate and refresh full applicable review and full proof. A routing-only change would require fresh review for a changed target base, without changing acceptance revision; that exception does not apply to this amendment.
Storage: .p2p/work/parent/slicing.md; helper retains prior plan bytes. Approved section, contracts, request and all old reports remain unchanged.

Next steps:
1. `/plan-acceptance work/parent.md; amendment requested-amendment.md; handoff .p2p/work/parent/slicing.md` to resolve Unicode semantics and affected parent/child agreement. Approve and save revised contracts before dependent work.
2. `/slice-contract work/parent.md` to reconcile contributions and decide revised lookup outcome acceptability on trunk; retain unaffected routing and histories.
3. After authorized implementation, refresh full review and proof for the exact changed candidate and revised binding agreements, then prepare publication only under its separate authority.
