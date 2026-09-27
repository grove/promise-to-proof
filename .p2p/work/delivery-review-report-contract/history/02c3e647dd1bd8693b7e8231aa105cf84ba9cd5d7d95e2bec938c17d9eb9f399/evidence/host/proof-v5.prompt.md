Prove this fixed candidate against the full agreed contract. Follow the candidate's `skills/productivity/prove/SKILL.md` and `docs/acceptance-contract-protocol.md`.

Contract: `work/delivery-review-report-contract.md`, revision v3, SHA-256 `b490dc25a68ba6521282128bcf60bc3f77e8a11b907b0c9b385402fa230677cb`.
Candidate root: `/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v5`.
Exact candidate key: `snapshot:sha256:ba332bf48e9ff1a00853a6b6ecc3d604016cb2be5c2ce5354c8b1ac8962610f4`.
Comparison base: `d0467b7bbaed2078e7e677b6ce3be407d4fb2058`.
Recoverable candidate record: `/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v5/.p2p/work/delivery-review-report-contract/candidate.json`.
Matching review: `.p2p/work/delivery-review-report-contract/review.md` in the enclosing repository; use it only as a navigation aid, not proof.

Reconcile the contract with its linked review skill. Independently verify R1–R3 against this one exact candidate. Before and after verification, run from the candidate root:
`/opt/homebrew/opt/python@3.14/bin/python3.14 skills/productivity/deliver-issue/scripts/p2p_filesystem.py --repo /Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v5 validate work/delivery-review-report-contract.md --base d0467b7bbaed2078e7e677b6ce3be407d4fb2058`

Do not modify product files, the contract, candidate record, or candidate snapshot. Keep all temporary output in `/private/tmp/p2p-delivery-report-contract-v5-proof-scratch`. Set `TMPDIR=/private/tmp/p2p-delivery-report-contract-v5-proof-scratch/.p2p/tmp`, `PYTHONPYCACHEPREFIX=/private/tmp/p2p-delivery-report-contract-v5-proof-scratch/pycache`, and `PYTHONDONTWRITEBYTECODE=1`. Run the complete controller suite against the candidate:
`/opt/homebrew/opt/python@3.14/bin/python3.14 -m unittest checks.test_p2p_delivery -v`
Also run `git diff --check d0467b7bbaed2078e7e677b6ce3be407d4fb2058` from the candidate root. Inspect the real source paths and tests that implement each requirement; test results alone do not replace the promised outcome.

Check realistic counterexamples through the existing fixture tests: blank or verdict-bearing review rows, unsupported/free-text/contradictory review fields, review report sections and identity, a BLOCKED review on initial run and resume, and plan-acceptance handoff routing. Distinguish fixture evidence from live-host evidence; the contract explicitly excludes live-host claims from fixture transport.

Return the proof skill's exact report format with one verdict for every requirement, commands and observations, counterexamples, candidate and contract stability, environment, unresolved gaps, and numbered `Next steps`. Return PROVEN only if each requirement has credible evidence; otherwise NOT PROVEN. Never modify the candidate or claim a command you did not run.
