# Implementation: Fixed delivery strategy comparison

Contract: `work/fixed-delivery-strategy-comparison.md` v2, SHA-256 `71c99c721096b5a0e535b44a00a0a8c9264175b584c417322868d342e7a21de2`.
Candidate: `snapshot:sha256:fec6aee428b20820d2da2e98f9cf4140247dda49e754e43a3a0f320fe7a3d1cd`, captured against `cc27a47f5ee765cff3cf13b21c36f974cb1234ae`.

Implemented the serial pilot runner and deterministic analyzer in `checks/run_delivery_comparison.py` and `checks/compare_delivery_strategies.py`, added focused tests, and documented setup, execution, limits, and report interpretation in `docs/delivery-strategy-comparison.md`. The pilot retains the preregistered six-task/order assignments, copied controller hashes, independent oracle, host receipts, unknown costs, and unexecuted assignments.

Validation: `python3 -B checks/test_compare_delivery_strategies.py` passed 11 tests; `python3 -B checks/test_run_delivery_comparison.py` passed 4 tests. The saved analyzer output reproduced byte-for-byte from `comparison-input.json` (SHA-256 `76861194f171ba28e69be92c39952f991d9ea05d6172b84c64e3c108a42bf8f1`). Candidate and contract identities remained stable through verification.

Pilot outcome: two greeting episodes ran, one under each serial order, then the cohort stopped after the proof-first episode had no unambiguous proof completion receipt. Both candidates passed the independent greeting oracle, but neither reached `REVIEWED_AND_PROVEN`. The review-first episode was blocked because its `REVIEWED` report used requirement verdict `proven` instead of `reviewed`. The proof-first episode used its one repair and then timed out during fresh proof; it ended at 1,800.511 seconds, 0.511 seconds over the registered limit. Four episodes remain unrun under the uncertain-dispatch stop rule. The report has zero useful workflow completions, unknown costs and human effort, and no strategy conclusion. See `evidence/pilot-findings.md` and `evidence/pilot/comparison-report.json`.
