# PROVEN: work/lookup.md

Requirements: 1/1
Contract: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9; exact bytes recoverable at 2a7733c6ac449ab6203d856f090c2e67173daace:work/lookup.md.
Binding inputs: [{"path": "specs/registry.md", "sha256": "64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9"}, {"path": "work/parent.md", "sha256": "38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada"}]
Comparison base: 2a7733c6ac449ab6203d856f090c2e67173daace, current approved integration target. Lookup's previous base metadata is retained by helper history; no historical implementation/publication report was rewritten.
Actor context: /root/scenario_parent_repaired; single actor, no delegated reviewers.
Candidate: git:2a7733c6ac449ab6203d856f090c2e67173daace; recoverable with git show 2a7733c6ac449ab6203d856f090c2e67173daace:<path>.
Parent comparison base / merge base: 928231303f30c9c01d93754ce5653e9b27b42399 (observed local and origin trunk).
Plan: .p2p/work/parent/slicing.md, v1, approved-section sha256:787c4a50a0828bba064b7ca5b817f17ac3657cd88b51e3a4df9c838f75cc02db; approval receipt .p2p/work/parent/approval.md retained.
All children route grouped to epic/example at 2a7733c6ac449ab6203d856f090c2e67173daace. Parent routes to trunk.
Environment: Python 3, disposable local fixture repository, PYTHONDONTWRITEBYTECODE=1; exact version and commands in evidence log.
Source reconciliation: specs/registry.md and all four v1 contracts inspected in full; no pending amendments found. ASCII scope; no network/persistence/automatic merge. Functions use ordinary in-memory string/dictionary operations. No unspecified architecture required.
Candidate and contract stability: unchanged. Helper validate passed with exact captured bases and binding hashes; git diff HEAD outside .p2p was empty and git status showed only .p2p.
Evidence: .p2p/work/parent/evidence/behavior.txt contains exact behavioral commands, observations, independent literal assertions, exit codes and stderr. Command transcript retained separately.

Parent context: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada. Child R1 contributes parent R2; decomposition keeps R4 for assembled-parent verification. Lookup prerequisite capture was exercised against the actual candidate, not inferred from issue state. Capture and summary have no prerequisites.

## Requirement verdicts

| ID | Observation and independent oracle | Evidence | Verdict |
|---|---|---|---|
| R1 | lookup({'ada':'Ada'},'ADA') == 'Ada'; lookup({},'ADA') is None; assertion matched literal contract examples, with empty and mixed-case boundaries | python3 check.py lookup, exit 0; boundary command in parent/evidence/behavior.txt | proven |

## Counterexamples and limits

Empty input, mixed-case Ada/aDA and uppercase BOB preserved each original value through each child's public seam. Lookup also covered missing and many-key dictionaries. No child counterexample found. Parent greet('Ada') returns Welcome ADA; that assembled R4 failure does not add an unrelated sibling requirement to this child contract. No parent acceptance or child publication is asserted.

## Unresolved gaps

None for this child's complete contract.

## Repairs needed

None for this child.

Next steps:
1. `/review-implementation work/lookup.md` against 2a7733c6ac449ab6203d856f090c2e67173daace if child publication is requested; no child review was invoked here.
2. Complete parent R4 repair and fresh assembled-parent review/proof before parent publication.
