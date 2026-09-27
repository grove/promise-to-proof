# REVIEWED: Fixed delivery strategy comparison

Contract: `work/fixed-delivery-strategy-comparison.md` v2, SHA-256 `71c99c721096b5a0e535b44a00a0a8c9264175b584c417322868d342e7a21de2`.
Candidate: `snapshot:sha256:fec6aee428b20820d2da2e98f9cf4140247dda49e754e43a3a0f320fe7a3d1cd`.
Comparison base: `cc27a47f5ee765cff3cf13b21c36f974cb1234ae`; scope includes the captured working tree, comparison scripts, tests, documentation, and contract. Candidate and contract were unchanged at report time.

Coverage: R1–R12; both comparison scripts, their tests, the documented workflow, retained controller diff, manifest, host receipts, analysis, and independent greeting adjudication.

## Contract fidelity

No material findings in the comparison tooling. It fixes the task/order population before execution, keeps controller copies identical except for verifier order, accounts for every assignment and attempt, preserves unknown observations, and always labels this small feasibility pilot inconclusive. Its analyzer does not treat a workflow verdict as an independent correctness label.

## Scope and simplicity

No material findings. The implementation uses the standard library and existing controller/filesystem helpers. It does not change the normal delivery policy, add a host, or claim live concurrency.

## Engineering quality

No material findings in the captured code. The focused tests cover accounting, overlap, sensitivity, malformed inputs, uncertain dispatch, stop-on-failure behavior, both serial orders, and repair exhaustion.

## Checks and limitations

Both focused suites passed (11 analyzer tests and 4 runner tests). Re-running the documented analyzer command reproduced the retained report byte-for-byte. The actual cohort stopped on its first episode. That episode's review report had status `REVIEWED` and no gaps but gave R1 verdict `proven`; the unchanged controller requires review verdict `reviewed` and saved `BLOCKED`. The exact candidate passed the preregistered independent greeting oracle. This is a pilot execution limitation, not evidence that the comparison tooling selected a winner. Five assignments remain unexecuted; cost and human-effort inputs remain unknown.

## Handoff

No code finding IDs. The proof report records R2 and R8 as not proven for this run. Do not resume or add episodes to this cohort. Any new cohort needs fresh authorization and must preserve the current evidence.

Review only; acceptance proof and merge readiness are separate.

## Next steps

1. Use `proof.md` for the final acceptance status of this candidate; it is `NOT PROVEN` for a complete paired comparison.
2. If a complete paired comparison is still wanted, resolve the review-verdict output mismatch without weakening controller requirements, agree how to capture human effort, then obtain authorization for a new cohort and capture a new candidate.
