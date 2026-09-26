# PROVEN: work/parent.md

Requirements: 4/4
Counterexamples tested: five boundary categories (empty, mixed case, uppercase, multiple names, missing).
Contract: work/parent.md v1
Contract snapshot: git show 159b5f50400479e1e5429b26b6c75e6d5f45682f:work/parent.md; SHA-256 38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada
Binding input: specs/registry.md at same commit; SHA-256 64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9
Candidate: 159b5f50400479e1e5429b26b6c75e6d5f45682f
Comparison base: 159b5f50400479e1e5429b26b6c75e6d5f45682f
Candidate stability: unchanged; HEAD and trunk match captured candidate; no product diff or untracked product files before/after.
Contract stability: unchanged; exact hashes validated before and after.
Verification context: Python 3.9.6, disposable local repository, PYTHONDONTWRITEBYTECODE=1, no network.
Actor context: /root/scenario_parent_outcomes:S12

## Outcome

The actual combined candidate on trunk captures original casing, looks names up case-insensitively, and produces Welcome Ada from the full capture/lookup/summary interaction. All four requirement checks and additional literal-oracle boundary assertions pass. Source and contract reconcile, and no pending amendment is linked. No historical child verdict or ticket status substitutes for these actual observations.

## Delivery context

.p2p/work/parent/slicing.md v1 independently routes capture, lookup and summary to trunk; no integration branch exists in the approved plan. Approval text is retained in approval.md. Approved section SHA-256: 6ddc21b5453e16b607299bb1789e3ad93a137c9442ddb373b1665302d16e25f5; recoverable exact bytes remain in slicing.md. Capture contributes R1, lookup R2, summary R3; R4 was checked on this one combined candidate. Actual capture prerequisite behavior exists and passes. The plan table retains historical “remaining” labels despite the request reporting landed contributions; this administrative state is not used as acceptance evidence. Direct trunk identity and actual combined behavior establish the requested candidate outcome. No empty parent or integration PR is needed or created.

## Requirement verdicts

| ID | Observation and independent oracle | Evidence | Verdict |
|---|---|---|---|
| R1 | Ada captured as {'ada': 'Ada'}; empty and additional casing examples preserve the supplied value. | evidence/commands.txt: capture PASS and boundary assertions; registry.py implementation inspection | proven |
| R2 | ADA finds Ada; missing returns None; real captures and a two-name dictionary support varied key casing. | evidence/commands.txt: lookup PASS and boundary assertions | proven |
| R3 | Supplied Ada produces literal Welcome Ada, and empty name produces Welcome plus one space. | evidence/commands.txt: summary PASS and boundary assertions | proven |
| R4 | Public composition of actual capture, lookup and summary preserves Ada as literal Welcome Ada, with additional mixed-case examples. | evidence/commands.txt: parent PASS and boundary assertions | proven |

## Evidence and stability

Exact commands, outputs, exit codes, environment, candidate/base identities and repeated validation are retained in evidence/commands.txt. All four agreed check.py commands exit 0. The boundary command asserts independent literal expected results, not copied production logic. Source inspection confirms simple dictionary and string operations with no persistence or network. Only .p2p/ records are untracked, and product content stayed fixed. Proof does not establish review, CI gates or merge authority.

## Unresolved gaps

None for parent acceptance. Full parent engineering review is absent; it remains a separate phase.

## Repairs needed

None. No code, tests, contracts, refs or tracker state changed. Only proof.md, evidence/commands.txt, and the case-root actor-report.md were written.

Next steps:
1. /review-implementation .p2p/work/parent/candidate.json against 159b5f50400479e1e5429b26b6c75e6d5f45682f (full assembled parent scope). No publication action is needed for the already-landed combined candidate.
