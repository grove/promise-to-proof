# NOT PROVEN: work/parent.md

Requirements: 3/4
Contract: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada; immutable contract 2a7733c6ac449ab6203d856f090c2e67173daace:work/parent.md; binding inputs [{"path": "specs/registry.md", "sha256": "64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9"}]
Actor context: /root/scenario_parent_repaired; single actor, no delegated reviewers.
Candidate: git:2a7733c6ac449ab6203d856f090c2e67173daace; recoverable with git show 2a7733c6ac449ab6203d856f090c2e67173daace:<path>.
Parent comparison base / merge base: 928231303f30c9c01d93754ce5653e9b27b42399 (observed local and origin trunk).
Plan: .p2p/work/parent/slicing.md, v1, approved-section sha256:787c4a50a0828bba064b7ca5b817f17ac3657cd88b51e3a4df9c838f75cc02db; approval receipt .p2p/work/parent/approval.md retained.
All children route grouped to epic/example at 2a7733c6ac449ab6203d856f090c2e67173daace. Parent routes to trunk.
Environment: Python 3, disposable local fixture repository, PYTHONDONTWRITEBYTECODE=1; exact version and commands in evidence log.
Source reconciliation: specs/registry.md and all four v1 contracts inspected in full; no pending amendments found. ASCII scope; no network/persistence/automatic merge. Functions use ordinary in-memory string/dictionary operations. No unspecified architecture required.
Candidate and contract stability: unchanged. Helper validate passed with exact captured bases and binding hashes; git diff HEAD outside .p2p was empty and git status showed only .p2p.
Evidence: .p2p/work/parent/evidence/behavior.txt contains exact behavioral commands, observations, independent literal assertions, exit codes and stderr. Command transcript retained separately.

## Outcome

All three child primitives behave as promised, but the assembled greeting destroys original case. Existing child proofs are supporting references, not an aggregated parent verdict.

## Requirement verdicts

| ID | Observation and independent oracle | Evidence | Verdict |
|---|---|---|---|
| R1 | Ada maps to literal {ada: Ada}; empty and aDA preserve original values | check.py capture exit 0; boundary assertions | proven |
| R2 | Captured Ada read using ADA returns Ada; missing is None; many-key BOB lookup returns Bob | check.py lookup exit 0; boundary assertions using actual capture | proven |
| R3 | Ada maps to literal Welcome Ada; empty yields Welcome followed by one space | check.py summary exit 0; boundary assertions | proven |
| R4 | direct composition returns Welcome Ada, but actual greet('Ada') returns Welcome ADA; aDA also loses case | check.py parent exit 1 at line 13; independent printed/asserted boundary result | disproven |

## Counterexamples tested

Four name boundaries (empty, Ada, aDA, BOB), empty/missing dictionary and multi-key lookup; direct composition and public greet compared. Concrete counterexamples: Ada and aDA greeting casing. No persistence/restart/concurrency behavior promised; no invented requirement imposed.

## Unresolved gaps

R4 complete case-preserving public workflow fails. Candidate includes all contributions and final trunk ancestry, so this is an actual interaction defect, not missing child evidence.

## Repairs needed

R4: remove premature uppercasing at registry.py:13 so capture receives original name. No product, test or contract edits were made.

Next steps:
1. `/repair-gaps .p2p/work/parent/proof.md` under an authorized repair request.
2. Capture repaired candidate and run full `/review-implementation work/parent.md` against current trunk and `/prove work/parent.md` before publication/readiness.
