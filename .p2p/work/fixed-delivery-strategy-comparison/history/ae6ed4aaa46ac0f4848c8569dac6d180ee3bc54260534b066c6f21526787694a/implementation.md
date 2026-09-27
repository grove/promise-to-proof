# Implementation: Fixed delivery strategy comparison

Contract: `work/fixed-delivery-strategy-comparison.md` v2, SHA-256 `71c99c721096b5a0e535b44a00a0a8c9264175b584c417322868d342e7a21de2`.
Candidate: `snapshot:sha256:fec6aee428b20820d2da2e98f9cf4140247dda49e754e43a3a0f320fe7a3d1cd`, captured against `cc27a47f5ee765cff3cf13b21c36f974cb1234ae`.

Implemented the serial pilot runner and deterministic analyzer in `checks/run_delivery_comparison.py` and `checks/compare_delivery_strategies.py`, added focused tests, and documented setup, execution, limits, and report interpretation in `docs/delivery-strategy-comparison.md`. The pilot retains its preregistered six-task/order assignments, copied controller hashes, independent oracle, host receipts, unknown costs, and unexecuted assignments.

Validation: `python3 -B checks/test_compare_delivery_strategies.py` passed 11 tests; `python3 -B checks/test_run_delivery_comparison.py` passed 4 tests. The saved analyzer output reproduced byte-for-byte from `comparison-input.json` (SHA-256 `bac01dc54fc267b8308d1fd655f89a70f9c4e00bee7585724a8d5b39f455c6f8`). Candidate and contract identities remained stable through verification.

Pilot outcome: the approved cohort stopped after `greeting-review-first` returned nonzero. Its review report said `REVIEWED` with no gaps but used requirement verdict `proven`; the retained controller requires `reviewed` verdicts and returned `BLOCKED` before creating an acceptance bundle. The preregistered oracle independently passed the exact greeting candidate. Five episodes remain unexecuted, costs and human effort are unknown, and no strategy comparison or adoption claim is supported. See `evidence/pilot-findings.md` and `evidence/pilot/comparison-report.json`.
