# CHANGES NEEDED: work/lookup.md

Agent context: /root/scenario_child_verification. Review and proof are separate passes in this same context; no independent-context claim.
Contract: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9; exact text recoverable from candidate.json manifest or candidate Git object.
Parent context: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada; specs/registry.md sha256:64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9. Child R1 contributes parent R2. Decomposition: .p2p/work/parent/slicing.md. Parent R3/R4 and whole-parent delivery are outside this child verdict. Exact shared-candidate approval at .p2p/work/parent/shared-candidate-approval.md covers capture plus lookup only; each child has a separate full report. Capture is not integrated in the target.
Candidate: git:194af4c2baba22b019b76bb36be64bf7c3b1b589; recoverable .p2p/work/lookup/candidate.json.
Comparison: resolved epic/example at 66a04c3617995cce9bf4cbd282e28d8f09cfd906; full product scope, including staged/unstaged/deleted/untracked files outside .p2p. Fixed target equals candidate.json comparison_base and observed remote tip.
Plan: v1 sha256:a7f70fc11fc26bd176526c63c3fd344a62da1d15dfcb14e05b0992c3ff6eeeb9; recoverable exact bytes .p2p/work/lookup/evidence/approved-plan.md; source .p2p/work/parent/slicing.md, approval receipts retained with parent records.
Stability: installed helper validate passed before and after behavioral checks, including complete product content, canonical contract and transitive binding hashes. No candidate/ref/contract edits during review or proof.

Coverage: all child R1, inherited ASCII/no-network/no-persistence/no-merge constraints, and actual capture prerequisite for lookup. registry.py:3-7, complete check.py and full target diff inspected. No source discrepancy; no child requirement omitted.

## Contract fidelity

F1, contract fidelity, child R1 / parent R2: registry.py:7 raises NotImplementedError("lookup unfinished") for a captured Ada query. python3 check.py lookup exits 1 at its first literal assertion; actual capture-to-lookup also raises. Implement case-insensitive lookup and missing-key None through registry.lookup, then refresh both reports.

## Scope and simplicity

Full diff contains only capture and lookup changes approved by the shared-candidate exception. Lookup remains unfinished and prevents publication of the shared candidate.

## Engineering quality

Native string.lower and dictionary operations suffice. Tests use literal expected values through public functions. No dependencies, filesystem, network or merge behavior in product code. F1 prevents every supported lookup query; no separate quality finding needed.

## Checks and limitations

Static review covered every production function and caller in check.py. Evidence: .p2p/work/lookup/evidence/child-verification-checks.json. Existing implementation.md is historical where its candidate differs; the validated candidate.json controls this captured review. No parent acceptance or PR readiness inferred.

## Handoff

Report storage: .p2p/work/lookup/review.md, saved and reread with helper history.
Review only; acceptance proof and merge readiness are separate.

## Next steps

1. /implement-contract work/lookup.md; findings .p2p/work/lookup/review.md
2. Capture changed candidate, then /review-implementation work/lookup.md and /prove work/lookup.md over the full contract.
