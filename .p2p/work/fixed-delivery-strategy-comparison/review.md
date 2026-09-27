# REVIEWED: Fixed delivery strategy comparison

Contract: `work/fixed-delivery-strategy-comparison.md` v2, SHA-256 `71c99c721096b5a0e535b44a00a0a8c9264175b584c417322868d342e7a21de2`.
Candidate: `snapshot:sha256:fec6aee428b20820d2da2e98f9cf4140247dda49e754e43a3a0f320fe7a3d1cd`.
Comparison base: `cc27a47f5ee765cff3cf13b21c36f974cb1234ae`; scope includes the captured working tree, comparison scripts, tests, documentation, and contract. Candidate and contract were unchanged at report time.

Coverage: R1–R12; both comparison scripts, their tests, the documented workflow, retained controller diff, manifest, host receipts, analysis, and independent greeting adjudications.

## Contract fidelity

No material findings in the comparison tooling. It fixes the task/order population before execution, keeps controller copies identical except for verifier order, accounts for every assignment and attempt, preserves unknown observations, and always labels this small feasibility pilot inconclusive. Its analyzer does not treat a workflow verdict as an independent correctness label.

## Scope and simplicity

No material findings. The implementation uses the standard library and existing controller/filesystem helpers. It does not change the normal delivery policy, add a host, or claim live concurrency.

## Engineering quality

No material findings in the captured code. The focused tests cover accounting, overlap, sensitivity, malformed inputs, uncertain dispatch, stop-on-failure behavior, both serial orders, and repair exhaustion.

## Checks and limitations

Both focused suites passed (11 analyzer tests and 4 runner tests). Re-running the documented analyzer command reproduced the retained report byte-for-byte. Two greeting candidates, one per order, passed the independent oracle, but both controller workflows were blocked. Review-first used verdict `proven` on a `REVIEWED` row and was rejected before acceptance-bundle creation. Proof-first used its one repair but lacked an unambiguous host completion receipt for fresh proof; the full episode lasted 1,800.511 seconds, 0.511 seconds above the registered ceiling. Four assignments remain unrun. The report is inconclusive and records unknown cost and human effort.

## Handoff

No code finding IDs. The proof report records R2 and R8 as not proven for this run. The approved cohort is terminal under the uncertain-dispatch rule; no retries or extra assignments were started.

Review only; acceptance proof and merge readiness are separate.

## Next steps

1. Use `proof.md` for the final acceptance status of this candidate; it is `NOT PROVEN` for the full paired comparison.
2. If completing R2 and R8 remains necessary, resolve the review-verdict output and timing-bound issues without weakening controller requirements, agree how to capture human effort, then obtain authorization for a new cohort and capture a new candidate.
