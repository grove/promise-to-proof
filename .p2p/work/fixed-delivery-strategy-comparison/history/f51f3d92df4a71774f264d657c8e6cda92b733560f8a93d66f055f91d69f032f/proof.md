# NOT PROVEN: Fixed delivery strategy comparison

Requirements: 10/12 proven; R2 and R8 not proven for the approved live cohort.
Contract: `work/fixed-delivery-strategy-comparison.md` v2, SHA-256 `71c99c721096b5a0e535b44a00a0a8c9264175b584c417322868d342e7a21de2`.
Contract snapshot: included in candidate manifest; source hashes are recorded in `candidate.json`.
Candidate: `snapshot:sha256:fec6aee428b20820d2da2e98f9cf4140247dda49e754e43a3a0f320fe7a3d1cd`.
Candidate stability: unchanged before and after verification.
Contract stability: unchanged.
Verification context: macOS 26.6.2 arm64; Codex CLI 0.157.1; `gpt-6-luna`, xhigh; isolated `:workspace` sandbox for the independent oracle. The report is limited to this host and the three small Python task fixtures.

## Outcome

The comparison tooling is implemented and its stored calculations are reproducible. The approved live cohort stopped after the first episode returned nonzero, as preregistered. The report retains all six assignments, one independent satisfactory outcome without workflow completion, five unresolved unexecuted outcomes, unknown total cost, and unknown human effort. It has no matched two-strategy cohort, so no elapsed-time comparison or recommendation is justified. The six-episode feasibility pilot is therefore `NOT PROVEN` as a completed comparison and remains inconclusive.

## Requirement verdicts

| ID | Observation and oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | The approved task set, alternating order, host/configuration, oracle, limits, and stop rule were retained before dispatch. | `evidence/pilot/manifest.json`; `evidence/pilot/agreement.md` | proven |
| R2 | Both strategies were assigned, but only review-first greeting ran. Five assignments were left unexecuted after the first nonzero result; no matched strategy comparison exists. Concurrent review/proof remains unsupported. | `evidence/pilot/comparison-input.json`; `evidence/pilot/comparison-report.json`; `episodes/greeting-review-first/finished.json` | not proven |
| R3 | The same retained input reproduced the exact analysis bytes on rerun. | `checks/compare_delivery_strategies.py`; `evidence/pilot/comparison-input.json`; report SHA-256 `bac01dc54fc267b8308d1fd655f89a70f9c4e00bee7585724a8d5b39f455c6f8` | proven |
| R4 | All six assignments remain in the denominator; five are marked unexecuted. The live episode retains five stage attempts and completion receipts without duplicate charging. | `evidence/pilot/comparison-report.json`; `episodes/greeting-review-first/source/.p2p/work/greeting/delivery.json` | proven |
| R5 | The preregistered oracle passed the exact candidate’s `hello
`/exit-zero behavior. Its result is satisfactory; five outcomes remain unresolved, not inferred from worker reports. The fixture suite also verifies detection of the seeded swallowed-I/O-error defect. | `episodes/greeting-review-first/oracle-result.json`; `adjudication.json`; `checks/test_run_delivery_comparison.py` | proven |
| R6 | One end-to-end duration is retained (1,278.658 seconds); analyzer tests verify serial duration and overlap accounting. Remaining episode intervals are unknown, and the report shows one observed value only. | `evidence/pilot/comparison-report.json`; `checks/test_compare_delivery_strategies.py` | proven |
| R7 | No settled charge or price input is available; the analyzer retains unknown components and null total, including pilot overhead. | `evidence/pilot/comparison-report.json`; `manifest.json` | proven |
| R8 | Active effort, passive waiting, and interruptions are separate fields, but no human observations were collected for this cohort; all remain null. | `evidence/pilot/comparison-input.json`; `evidence/pilot/comparison-report.json` | not proven |
| R9 | The live host, CLI version, model, reasoning setting, controller hashes, exact task identity, receipts, and evidence type are recorded. Concurrent execution is explicitly unexecuted. | `evidence/pilot/manifest.json`; `episodes/greeting-review-first/source/.p2p/work/greeting/admission.json`; `comparison-report.json` | proven |
| R10 | Retained synthetic sensitivity assumptions exercise cost/failure-rate crossover calculations; they are labeled estimates, not live measurements. | `evidence/pilot/evaluation/sensitivity.json`; `comparison-report.json`; `checks/test_compare_delivery_strategies.py` | proven |
| R11 | The 20% threshold was fixed before execution. The analysis reports `inconclusive`, no supported winner, and unavailable comparison/payback inputs. | `evidence/pilot/agreement.md`; `evidence/pilot/comparison-report.json` | proven |
| R12 | The controller copies differ only in verifier order; the pilot retained full review/proof requirements, identity checks, authority limits, and the one-repair ceiling. The cohort stopped on the saved blocker without retrying or changing live policy. | `controller-order.diff`; `manifest.json`; `checks/test_run_delivery_comparison.py`; `finished.json` | proven |

## Unresolved gaps

- R2: the live cohort did not produce a paired comparison. The review report returned `REVIEWED` with no gaps but used row verdict `proven`; the unchanged controller requires `reviewed` and stopped before acceptance-bundle creation.
- R8: human active time, passive waiting, and interruptions were not observed.
- Five assigned episodes were not run under the agreed stop rule. Their outcomes, costs, and timings remain unresolved.

## Repairs needed

- No repair was made to this candidate. A future comparison needs the review-stage verdict mismatch resolved without weakening the controller’s full-check requirements, plus a prospective method to collect human effort. The approved cohort must remain terminal.

Fresh `/prove` and `/review-implementation` are required if the candidate changes.

## Next steps

1. Keep this cohort closed; the recorded stop rule ended live dispatch after its first nonzero episode.
2. If completing R2 and R8 remains necessary, obtain fresh authorization for a new cohort after resolving the review-verdict output mismatch and defining prospective human-effort capture. Preserve this report as the historical result.
