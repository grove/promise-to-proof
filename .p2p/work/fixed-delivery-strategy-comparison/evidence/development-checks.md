# Development checks

These are implementation observations, not independent acceptance verdicts.

- `python3 checks/test_compare_delivery_strategies.py`: 11 tests passed after correcting per-episode payback and retaining known preparation elapsed. Covers hand-calculated cost totals, interval union, unknown costs, false-green adjudication, repeatable CLI output, sensitivity, malformed values, unmatched cohorts, and overhead.
- `python3 checks/test_run_delivery_comparison.py`: 4 tests passed after correcting cohort stop behavior and adding both copied-controller execution paths. The final run took 37.974 seconds. Covers preregistration and exact input matching, guarded one-line order change, uncertain-dispatch refusal, model drift, receipt/event integrity, good/defective independent oracle fixtures, and each serial order through one repair and repair exhaustion.
- The copied-controller tests use the actual public controller entry point with the existing `FakeTransport`. They establish control flow and accounting, not real host protections.
- Read-only review identified three defects before handoff: payback used cohort savings as per-episode savings; run-all continued after a nonzero episode; and analysis dropped preparation time. All three were corrected with regression assertions.

Input hashes are retained in `development-inputs.json`. Live observations are separate under `pilot/`.
