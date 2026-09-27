# NOT PROVEN: Fixed delivery strategy comparison

Requirements: 10/12 proven; R2 and R8 not proven for the approved live cohort.
Contract: `work/fixed-delivery-strategy-comparison.md` v2, SHA-256 `71c99c721096b5a0e535b44a00a0a8c9264175b584c417322868d342e7a21de2`.
Contract snapshot: included in candidate manifest; source hashes are recorded in `candidate.json`.
Candidate: `snapshot:sha256:fec6aee428b20820d2da2e98f9cf4140247dda49e754e43a3a0f320fe7a3d1cd`.
Candidate stability: unchanged before and after verification.
Contract stability: unchanged.
Verification context: macOS 26.6.2 arm64; Codex CLI 0.157.1; `gpt-6-luna`, xhigh; isolated `:workspace` sandbox for the independent oracle. The report is limited to this host and the three small Python task fixtures.

## Outcome

The comparison tooling is implemented and its stored calculations are reproducible. Two greeting episodes ran, one under each serial order. Both exact candidates passed the preregistered finite greeting oracle, but neither workflow completed. Review-first was blocked by a review row using verdict `proven` instead of `reviewed`. Proof-first used its one repair, then lacked an unambiguous completion receipt for fresh proof and exceeded its 1,800-second limit by 0.511 seconds. Four assigned episodes remain unrun under the uncertain-dispatch stop rule. The report retains six assignments, two satisfactory outcomes without workflow completion, four unresolved outcomes, zero useful completions, unknown total cost, and unknown human effort. It has no full matched cohort, so no elapsed-time improvement or recommendation is justified. This phase is `NOT PROVEN` as a completed comparison and remains inconclusive.

## Requirement verdicts

| ID | Observation and oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | The approved task set, alternating order, host/configuration, oracle, limits, and stop rule were retained before dispatch. | `evidence/pilot/manifest.json`; `evidence/pilot/agreement.md` | proven |
| R2 | Both strategies ran only the greeting task; both workflows were blocked and four assignments remain unrun. The report has no matched full cohort; concurrent verification remains unsupported. | `evidence/pilot/comparison-input.json`; `evidence/pilot/comparison-report.json`; both episode `finished.json` records | not proven |
| R3 | The same retained input reproduced the exact analysis bytes on rerun. | `checks/compare_delivery_strategies.py`; `evidence/pilot/comparison-input.json`; report SHA-256 `76861194f171ba28e69be92c39952f991d9ea05d6172b84c64e3c108a42bf8f1` | proven |
| R4 | All six assignments remain in the denominator; four are marked unexecuted. Two live episodes retain their attempts, including the failed proof dispatch and single repair. | `evidence/pilot/comparison-report.json`; both `source/.p2p/work/greeting/delivery.json` records | proven |
| R5 | The preregistered oracle passed both exact greeting snapshots (`hello
`, exit 0). Outcomes are satisfactory but not workflow completions; four others remain unresolved. Fixture tests detect the seeded swallowed-I/O-error defect. | Both `episodes/*greeting*/oracle-result.json` and `adjudication.json`; `checks/test_run_delivery_comparison.py` | proven |
| R6 | Two end-to-end durations are retained: 1,278.658 and 1,800.511 seconds. The analyzer reports one observation per strategy and an incomplete cohort; tests verify serial and overlap arithmetic. | `evidence/pilot/comparison-report.json`; `checks/test_compare_delivery_strategies.py` | proven |
| R7 | No settled charge or price input is available; the analyzer retains unknown components and null total, including pilot overhead. | `evidence/pilot/comparison-report.json`; `manifest.json` | proven |
| R8 | Active effort, passive waiting, and interruptions are separate fields, but no human observations were collected; all remain null. | `evidence/pilot/comparison-input.json`; `evidence/pilot/comparison-report.json` | not proven |
| R9 | The live host, CLI version, model, reasoning setting, controller hashes, exact task identities, receipts, and evidence type are recorded. Concurrent execution is explicitly unexecuted. | `evidence/pilot/manifest.json`; both `source/.p2p/work/greeting/admission.json`; `comparison-report.json` | proven |
| R10 | Retained synthetic sensitivity assumptions exercise cost/failure-rate crossover calculations; they are labeled estimates, not live measurements. | `evidence/pilot/evaluation/sensitivity.json`; `comparison-report.json`; `checks/test_compare_delivery_strategies.py` | proven |
| R11 | The 20% threshold was fixed before execution. The analysis reports `inconclusive`, no supported winner, and unavailable comparison/payback inputs. | `evidence/pilot/agreement.md`; `evidence/pilot/comparison-report.json` | proven |
| R12 | The controller copies differ only in verifier order; the pilot retained full checking, identities, authority limits, and one-repair bound. No live policy was changed. | `controller-order.diff`; `manifest.json`; `checks/test_run_delivery_comparison.py`; episode receipts | proven |

## Unresolved gaps

- R2: no full paired three-task comparison exists. Review-first returned a `REVIEWED` report whose R1 verdict was `proven`; the controller requires `reviewed` and blocked before acceptance-bundle creation. Proof-first timed out with no completion receipt during fresh proof after its one repair.
- R8: human active time, passive waiting, and interruptions were not observed.
- Four assigned episodes were not run after the second episode produced an uncertain dispatch. Their outcomes, costs, and timings remain unresolved.
- The proof-first episode ended at 1,800.511 seconds, 0.511 seconds beyond the registered ceiling.

## Repairs needed

- No repair was made to this candidate. Any future cohort requires resolving the review-verdict mismatch without weakening full checks, keeping execution within the time ceiling, and defining prospective human-effort capture. This cohort remains terminal.

Fresh `/prove` and `/review-implementation` are required if the candidate changes.

## Next steps

1. Keep this cohort closed; the missing host completion receipt made the second dispatch uncertain, and the approved stop rule forbids retrying it or proceeding with further episodes.
2. If completing R2 and R8 remains necessary, obtain fresh authorization for a new cohort after resolving the review-verdict output mismatch, preventing the time overrun, and defining prospective human-effort capture. Preserve this report as the historical result.
