# Compare fixed delivery strategies

Phase 4 compares review-first and proof-first on three small Python tasks. The
six-episode pilot uses one configured model and the macOS Codex CLI host. It
keeps full independent review, proof, and the one-repair allowance. Its result
is descriptive and cannot justify changing live delivery policy.

The canonical agreement is [the Phase 4 contract](../work/fixed-delivery-strategy-comparison.md).
The pilot and its records live under
`.p2p/work/fixed-delivery-strategy-comparison/evidence/pilot/`.

## Reproduce the analysis

These commands read retained observations and make no model calls:

```sh
python3 checks/run_delivery_comparison.py collect --output-dir .p2p/work/fixed-delivery-strategy-comparison/evidence/pilot
python3 checks/compare_delivery_strategies.py .p2p/work/fixed-delivery-strategy-comparison/evidence/pilot/comparison-input.json
```

The second command prints deterministic JSON. Repeating it with the same input
reproduces the calculations, not a fresh stochastic delivery. It reports every
assigned episode, including unexecuted, blocked, and unresolved cases.

`manifest.json` fixes the tasks, inputs, execution order, model preferences,
controller hashes, oracle hash, and dispatch/time limits before evaluation.
`controllers/` holds the exact executable copies. `controller-order.diff`
shows the single tuple-order change for proof-first. Normal controller code
and policy remain unchanged.

Each episode retains the source repository, controller workspace, raw host
receipts, `started.json`, and `finished.json`. The collector checks saved
completion receipts before using observations. A started episode without a
finished receipt is uncertain; the runner refuses to dispatch it again.
Investigate the retained receipts before taking any further action.
The cohort runner stops after any nonzero episode result. Unexecuted assignments
remain in the report's denominator and are labeled separately from live attempts.

## Interpret the report

- Elapsed time comes from episode boundaries. Summed stage time and the union
  of occupied intervals are separate values. Overlapping work is not counted
  twice as elapsed time.
- Money has separate measured and estimated subtotals. Unknown components make
  the total unknown. Token usage is retained but is not a monetary charge.
- Useful completion requires both workflow completion and an independent
  satisfactory result. Green workflow reports cannot provide their own
  correctness label. Unresolved results remain unresolved.
- Active human effort, passive waiting, and interruptions remain separate.
  Missing observations are unknown, including comparison and maintenance effort.
- Strategy totals exclude shared comparison overhead; overall totals include
  it. Payback is unavailable without the necessary observations. Active-human
  seconds are never converted into saved waiting time.
- The provisional improvement target is 20% lower median elapsed time with no
  worse completion, missed defects, or human effort. This feasibility pilot
  always concludes that adoption evidence is inconclusive.

Concurrent verification is unexecuted. Synthetic interval checks establish the
arithmetic only. They do not establish live concurrency support or predict its
actual speed. Results apply only to the recorded host, configuration, and small
Python tasks.

## Run an authorized pilot

Preparing a new directory creates local disposable task repositories and
retains the input manifest. It makes no model calls:

```sh
python3 checks/run_delivery_comparison.py prepare --output-dir /path/to/new-pilot
```

Running requires authority for real model calls. Costs remain unknown; the host
cannot enforce a monetary cap. The approved pilot permits six episodes, each
with at most eight dispatches and 1,800 elapsed seconds. `prepare` refusing an
existing directory prevents overwriting earlier evidence.

```sh
python3 checks/run_delivery_comparison.py run --output-dir /path/to/new-pilot --authorize-live
```

Use `--episode greeting-review-first` to run one named episode. Keep the manifest
order when executing the pilot. After a completed episode, independently judge
the returned candidate with the prewritten `evaluation/oracle.py`. Execute
candidate code only in an OS sandbox with a separate writable scratch directory,
protected candidate and evidence files, no network access, and a process timeout.
Validate the candidate identity before and after evaluation. Retain the actual
command, output, exit status, and sandbox boundary probe with the adjudication.

Save `episodes/<id>/adjudication.json` with `outcome` equal to `satisfactory`,
`defective`, or `unresolved`; `missed_defects` as an observed count or null; and
`provenance` pointing to the independent evidence. A setup failure is unresolved,
not a product defect. Ambiguous outcomes require maintainer adjudication. For a
passing finite oracle, zero means no defects observed by those checks, not proof
that no defects exist. The collector never derives this file from worker claims.

## Check the calculations and runner

```sh
python3 checks/test_compare_delivery_strategies.py
python3 checks/test_run_delivery_comparison.py
```

These checks use independent hand-calculated ledgers and trusted fixture code.
They cover overlap, failures, repair and resume accounting, false-green reports,
unknown costs, empty cohorts, sensitivity, task identity, and uncertain dispatch.
They make no model calls and do not execute generated candidate code.
