# REVIEWED: work/lookup.md

Agent context: /root/scenario_child_verification. Review and proof are separate passes in this same context; no independent-context claim.
Contract: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9; exact text recoverable from candidate.json manifest or candidate Git object.
Parent context: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada; specs/registry.md sha256:64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9. Child R1 contributes parent R2. Decomposition: .p2p/work/parent/slicing.md. Parent R3/R4 and whole-parent delivery are outside this child verdict. Capture already exists at the target; candidate adds no prerequisite payload.
Candidate: git:6200ab72615e708585b48bcf3cbb7f9c45d3573e; recoverable .p2p/work/lookup/candidate.json.
Comparison: resolved epic/example at c74003fe4a40add496b1888ded0706494f49a47d; full product scope, including staged/unstaged/deleted/untracked files outside .p2p. Fixed target equals candidate.json comparison_base and observed remote tip.
Plan: v1 sha256:f97a0dda89221fcb76d436094a5cccc88b931ba77c0b8da35c2efaec49e6f304; recoverable exact bytes .p2p/work/lookup/evidence/approved-plan.md; source .p2p/work/parent/slicing.md, approval receipts retained with parent records.
Stability: installed helper validate passed before and after behavioral checks, including complete product content, canonical contract and transitive binding hashes. No candidate/ref/contract edits during review or proof.

Coverage: all child R1, inherited ASCII/no-network/no-persistence/no-merge constraints, and actual capture prerequisite for lookup. registry.py:3-7, complete check.py and full target diff inspected. No source discrepancy; no child requirement omitted.

## Contract fidelity

No material findings.

## Scope and simplicity

Full diff is limited to the intended contribution and, where approved, the capture prerequisite. No unfinished sibling payload or unrelated machinery.

## Engineering quality

Native string.lower and dictionary operations suffice. Tests use literal expected values through public functions. No dependencies, filesystem, network or merge behavior in product code. No material findings.

## Checks and limitations

Static review covered every production function and caller in check.py. Evidence: .p2p/work/lookup/evidence/child-verification-checks.json. Existing implementation.md is historical where its candidate differs; the validated candidate.json controls this captured review. No parent acceptance or PR readiness inferred.

## Handoff

Report storage: .p2p/work/lookup/review.md, saved and reread with helper history.
Review only; acceptance proof and merge readiness are separate.

## Next steps

1. Matching full review and proof are saved for git:6200ab72615e708585b48bcf3cbb7f9c45d3573e; publication is assessed in .p2p/work/lookup/publication.md.
2. Full parent review and proof remain separate before parent completion.
