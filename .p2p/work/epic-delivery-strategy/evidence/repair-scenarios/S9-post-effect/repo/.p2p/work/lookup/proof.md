# PROVEN: work/lookup.md

Requirements: 1/1
Counterexamples tested: 6 boundary groups: all eight Ada case variants, empty dictionary, absent key in populated dictionary, absent empty key, captured empty name, and multiple captured names with state preservation.
Contract: work/lookup.md v1, sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9. Recover exact bytes with `git show c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f:work/lookup.md`.
Parent context: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada; source specs/registry.md sha256:64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9. Both recoverable at candidate commit. Child R1 contributes parent v1:R2. Capture prerequisite is implemented and executed; no ticket status substituted for behavior. Parent R4 remains final parent verification.
Candidate: c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f, recoverable Git commit in this repository.
Comparison: c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f, actual epic/example target tip and merge base; empty candidate diff; complete unchanged product tree inspected.
Delivery plan: .p2p/work/parent/slicing.md v1, approved section sha256:b86ffd9b9b6ccbd0615efbcc57d3da023e1a8a0c185303a28832aafc0490ffe2; retained exact section evidence/approved-plan.md. Approval source .p2p/work/parent/approval.md inspected. Grouped lookup destination epic/example; final parent destination trunk. Existing target equals approved integration start.
Context: /root/scenario_retarget_verification performed review and proof in the same actual agent context, separately from fixture preparation. No implementation occurred here.

Candidate stability: unchanged before and after checks; no product files written.
Contract stability: exact work item and binding hashes unchanged before and after checks.
Verification context: Python version and exact commands/output retained in evidence/proof-commands.txt. Same actual verifier context as review; no independent second reviewer claimed.

## Outcome

Lookup returns a captured original name for every ASCII case of its key, and None for missing names. The actual capture prerequisite provides lower-case dictionary keys. Source, child contribution and parent constraints agree; parent R4 remains a separate parent acceptance obligation. No contract discrepancy found.

## Requirement verdicts

| ID | Observation and oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | check.py lookup returned PASS. Direct public capture-to-lookup execution returned literal Ada for all eight ASCII case variants; missing names returned None; empty and multiple-name cases preserved literal originals and dictionary state. Contract parent v1:R2 and literal expected values are the oracle, independent of production normalization. | evidence/proof-commands.txt, python3 -B check.py lookup and retained python3 -B -c assertions | proven |

Capture prerequisite: `python3 -B check.py capture` returned capture: PASS. Supplemental summary and parent checks each returned PASS; these do not declare whole-parent acceptance. All commands exited 0. Static inspection of registry.py confirms no network, persistence, or automatic merge mechanism.

## Unresolved gaps

None for the complete child contract. Publication and final parent acceptance remain separate stages.

## Repairs needed

None. Any later repair requires fresh full proof and separate review.

Next steps:

1. Acceptance evidence is complete for candidate c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f and the captured epic/example base. The separately authorized publisher may inspect `.p2p/work/lookup/review.md` and `.p2p/work/lookup/proof.md` to prepare its exact preview; no publication or retargeting action occurred here.
2. When PR 17 approaches merge, run `/merge-readiness 17; review .p2p/work/lookup/review.md; proof .p2p/work/lookup/proof.md`. PR destination reconciliation and ordinary merge gates remain pending and were not assessed as proof requirements.
