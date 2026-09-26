# REVIEWED: work/lookup.md

Actor: /root/scenario_remaining_handoffs. One actual shared context for these cases; no delegation or independent reviewer contexts claimed.
Installed skill: /private/tmp/p2p-epic-repair-cases/S10-base-only/installed/review-implementation/SKILL.md sha256:eabc51ad2ec4cb31aee379cc89a10b200f186cff730cc62ec25568a895a9b5ca.
Bundled protocol: sha256:c916e48be9de29f423716518dc290a64b9c667bdf42b40da87dc346853957b43.
Commands and exact output: /private/tmp/p2p-epic-repair-cases/S10-base-only/handoff-command-evidence.jsonl. Only supplied fixture gh was used when tracker inspection was needed. No live network.
Authority: repair-request.md, local inspection and stage records only. No product, contract, ref, push, tracker, or merge effects performed.
Parent: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada; source specs/registry.md sha256:64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9.
Exact approved agreement bytes recoverable using `git show c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f:work/parent.md` and the same commit's specs/registry.md. Work files remain unchanged.

Contract: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9, recoverable at git:c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f:work/lookup.md.
Candidate: git:c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f; complete committed tree, no included working-tree product changes.
Comparison: actual approved epic/example tip b6fcfa6297c60b3b060c1a189c4d495f42ad7721; merge base c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f. Prior comparison base c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f is stale. candidate.json was recaptured with the same commit and new base via installed helper, retaining old bytes in history.
Delivery plan: .p2p/work/parent/slicing.md v1; exact approved section sha256:b86ffd9b9b6ccbd0615efbcc57d3da023e1a8a0c185303a28832aafc0490ffe2, recoverable in that file and evidence/approved-plan.md. Same grouped lookup route; no routing or agreement change. The exact active section matches the retained proof plan text and digest, including its final blank-line byte.
Stability: helper validation succeeds after base refresh; work/lookup.md, work/parent.md and specs/registry.md hashes match retained candidate inputs. Complete working product diff is empty.
Coverage: full child R1, parent v1:R2 contribution, capture prerequisite, inherited ASCII/no persistence/no network constraints. All registry.py functions, check.py callers and assertions inspected. Unrelated sibling completion is not required or claimed.

## Contract fidelity

No material findings. registry.py:3-7 captures the original value under lower-case key and performs case-normalized dict.get, including None for missing names. Actual capture prerequisite exists in both candidate and integration target. Literal assertions in check.py cover return values and missing-key behavior.

## Scope and simplicity

No material findings. Candidate introduces no sibling payload against current target. `git diff epic/example...HEAD` is empty because candidate is the target's ancestor. Endpoint `git diff epic/example HEAD` shows only absence of target-note.txt, containing "Integrated target-only note". A PR merge does not delete that target-only file; no product behavior depends on it. It is not ignored in the full comparison.

## Engineering quality

No material findings. Direct dictionary operations, no dependencies, network, persistence, hidden Git-derived execution inputs or unnecessary abstraction. All function callers are in check.py; contracts and relevant source were inspected directly.

## Checks and limitations

`python3 -B check.py capture` -> capture: PASS; `python3 -B check.py lookup` -> lookup: PASS. Python 3.14.7. Exact outputs and before/after identities are retained in the case command log. No exhaustive acceptance proof was rerun.
Retained .p2p/work/lookup/proof.md and evidence/proof-commands.txt remain applicable to exact candidate c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f and unchanged ASCII agreement. The target-only advance does not alter those proof observations. Proof's historical comparison base remains unchanged; it is not represented as new proof on the advanced target or assembled parent. The stale review was replaced by this actual full review. Existing publication previews must refresh their target-tip/report identities.
PR 17 currently targets epic/example, head child/lookup at the same candidate. This review assesses neither CI nor merge approvals. Whole-parent acceptance remains separate.

## Handoff

Report storage: .p2p/work/lookup/review.md. Old report and candidate record retained by installed helper. Only those records and history changed; proof bytes were preserved. Review only, not merge approval.

Plan digest correction: the first saved version omitted the final newline byte before the next level-two heading. This report now hashes and retains the exact protocol-defined section. The earlier report and original command observations remain in history.

## Next steps

1. Use this fresh full review with the retained exact-candidate proof for any new publication assessment; invalidate the old target-tip preview. If integration changes candidate bytes, run fresh full review and `/prove work/lookup.md` for the new candidate.
2. When PR 17 approaches merge, run `/merge-readiness 17; review .p2p/work/lookup/review.md; proof .p2p/work/lookup/proof.md` against actual current target and merge gates.
