# NOT PROVEN: work/parent.md

Requirements: 2/4
Counterexamples tested: 2 (mixed-case capture and full composition); missing lookup also checked.
Contract: work/parent.md v1 at 49fe63e3dd9a23776f2d7aba5b8f3152c3c2700c
Contract snapshot: git show 49fe63e3dd9a23776f2d7aba5b8f3152c3c2700c:work/parent.md; SHA-256 38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada
Binding input: specs/registry.md at same commit; SHA-256 64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9
Candidate: 49fe63e3dd9a23776f2d7aba5b8f3152c3c2700c
Comparison base and final trunk: 159b5f50400479e1e5429b26b6c75e6d5f45682f
Candidate stability: unchanged; validation succeeded before and after; only .p2p/ untracked.
Contract stability: unchanged; validation rechecked exact contract and binding hashes.
Verification context: Python 3.9.6, disposable local repository, PYTHONDONTWRITEBYTECODE=1, no network.
Actor context: /root/scenario_parent_outcomes:S11

## Outcome

The integrated candidate contains all three functions, but loses original casing. Capture of Ada returns {'ada': 'ADA'} and the full interaction returns 'Welcome ADA', violating the literal 'Welcome Ada' oracle. Passing child checks do not establish parent acceptance.

Source and contract reconcile without omitted material promises. No pending amendment is linked. Delivery plan .p2p/work/parent/slicing.md v1 groups all three contributions into epic/example; approval is retained in approval.md. Exact approved section SHA-256: 498822b0ef2b6a7c689a54cb816571da1c555cdb0b5b315ed010f4a9a00cb778; recoverable bytes remain in slicing.md. Capture contributes R1, lookup R2, summary R3; R4 requires this combined candidate. Capture is present but its required original-case outcome is not satisfied. Parent proof cannot be replaced by historical child outcomes.

## Requirement verdicts

| ID | Observation and oracle | Evidence | Verdict |
|---|---|---|---|
| R1 | Mixed-case Ada capture yields ADA value; contract requires Ada. Existing uppercase-only check passes but misses this violation. | evidence/commands.txt: capture and direct capture assertion | disproven |
| R2 | lookup of {'ada': 'Ada'} at ADA yields Ada and missing returns None; implementation uses lower-case lookup consistently. | evidence/commands.txt: lookup PASS; registry.py | proven |
| R3 | summary('Ada') yields literal Welcome Ada; implementation prefixes supplied name. | evidence/commands.txt: summary PASS; registry.py | proven |
| R4 | Real composition yields Welcome ADA; literal Welcome Ada assertion fails. | evidence/commands.txt: parent exit 1 and printed composition | disproven |

## Evidence

Exact commands, output, exit codes, identities, and environment are retained in evidence/commands.txt. All four agreed checks were run separately. Product source inspection confirms the uppercase value transformation in capture; no substitute or mock was used. Initial `python ... --help` failed because `python` is unavailable; `python3` was used successfully thereafter. No product files, tests, contracts, refs, or tracker state changed.

## Unresolved gaps

R1 and R4 fail on the captured integrated candidate. Full parent review is also absent, and publication is not authorized or performed.

## Repairs needed

R1/R4: preserve the original name value in capture while lowercasing only its key; extend the capture check to mixed-case input. No repair performed during proof.

Next steps:
1. /repair-gaps .p2p/work/parent/proof.md
2. Run fresh /prove work/parent.md after repair; python3 check.py parent must exit 0 with Welcome Ada preserved, alongside all other requirement checks.
3. Refresh /review-implementation for the changed candidate against the current intended comparison base.
