# CHANGES NEEDED: work/parent.md

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

Coverage: full R1–R4, actual registry.py, callers and assertions in check.py; full diff from trunk inspected. R1 capture lines 3–4, R2 lookup lines 6–7, R3 summary lines 9–10 implement promised primitive outcomes. R4 greet lines 12–13 loses original casing. All contributions exist in the single assembled candidate; trunk is an ancestor and no independent contribution is missing.

## Contract fidelity

F1 (R4, specs/registry.md original-case workflow): registry.py:13 passes name.upper() into capture. greet('Ada') produces Welcome ADA instead of literal Welcome Ada. check.py:13 fails. The direct primitive composition passes; the public assembled workflow still violates the source promise. Smallest correction: pass name itself to capture in greet, then rerun full proof. No repair performed.

## Scope and simplicity

No material change-required finding. The one-line diff adds no dependencies or framework. EXPERIMENTAL is unchanged pre-existing code without a new effect; no speculative redesign is required.

## Engineering quality

F1 is a concrete regression from trunk's case-preserving greet. Existing check.py detects it; reporting passing child commands alone would conceal it. No separate engineering finding beyond F1.

## Checks and limitations

Read every contract/source and full implementation/callers. Existing child checks exit 0; parent check exits 1 at greet('Ada'). Boundary observations independently corroborate loss of mixed case. One actor performed separate contract/scope/engineering passes; no independent-reviewer claim. Full scope examined; no identity unknown prevents this conclusion.

## Handoff

Report storage: .p2p/work/parent/review.md. Review only; acceptance and readiness are separate.

Next steps:
1. `/implement-contract work/parent.md; findings .p2p/work/parent/review.md` to correct F1 under separately authorized repair scope.
2. Capture the changed candidate, then refresh `/review-implementation work/parent.md` against current trunk and `/prove work/parent.md` for all R1–R4.
