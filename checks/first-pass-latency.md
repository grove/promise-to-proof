# First-pass delivery latency: measured improvements (#57)

## Result

In a matched **offline** first-pass delivery fixture, the optimized controller
reached the same `REVIEWED_AND_PROVEN` outcome with **18.1% less median elapsed
time**, while preserving both independent verifier calls, both host preflights,
the implementation stage, all four portable checkpoint boundaries, exact product
identity and the saved review/proof verdicts.

| Metric | Previous exact-main code | Optimized code | Change |
|---|---:|---:|---:|
| Cold fixture elapsed, median | 2.690100 s | 2.204330 s | **18.1% faster** |
| Git process launches | 1,388 | 1,147 | 241 fewer (17.4%) |
| Git/worktree snapshot calls | 129 | 89 | 40 fewer (31.0%) |
| Source-stability calls | 17 | 15 | 2 fewer |
| Source-stability time | 1.128199 s | 0.856035 s | 24.1% less |
| Candidate capture time | 0.128095 s | 0.112273 s | 12.3% less |
| Portable checkpoint time | 0.383976 s | 0.229180 s | 40.3% less |
| Portable checkpoints | 4 | 4 | **Unchanged** |
| Host/model dispatches | 5 fixture dispatches | 5 fixture dispatches | **Unchanged** |

These measurements are from the [four-pair GitHub Actions run](https://github.com/grove/promise-to-proof/actions/runs/38062599195)
on October 10, 2026. Both variants used the **same current controller**,
replacing only the four affected methods with their original implementations
from `3582eb48cae660e8ff6f4ad759e0988760a174e2` for the baseline. Four
independent source repositories were created for each variant, and run order
alternated `baseline → optimized → optimized → baseline` twice (ABBA, ABBA).
The table uses medians, not a favorable individual run.

An earlier baseline-only run on a different GitHub Actions run observed 2.45–2.52
seconds. This between-run variation is why the result above uses **paired,
alternating runs**, not a comparison of unrelated wall-clock observations.

This is **not live model-delivery timing**. The transport is explicitly a
deterministic test fixture and uses zero live model calls. Model thinking time,
token usage/cost and external network/provider latency are **unknown**, not
estimated as zero. We cannot claim an 18.1% improvement in real end-to-end
macOS/Codex delivery without measurements on that supported host.

## What changed, and why it is safe

1. **Reuse exact product snapshots at candidate capture.** The admission or
   implementation capture was already reading the full frozen comparison base
   and current workspace to check excluded dirty paths. It now passes those
   inspected bytes to the existing candidate writer and Git generation writer
   instead of rereading the same filesystem trees. Index consistency, agreement,
   binding, content/mode/symlink identity, Git generation mapping, and later
   current-candidate validation still apply.
2. **Avoid irrelevant committed HEAD scans.** Source stability still checks the
   actual source checkout on every required boundary, binding inputs, approved
   route, frozen base, stage instructions, and authority. It now compares an
   exact filtered product subset of the already-read source snapshot and only
   inspects committed HEAD/index metadata further if those inputs actually
   changed. Changed metadata still follows the full original drift logic.
3. **Do not run Git for checkpoint inputs that cannot be Git-backed.** Runtime
   execution receipts, local agreements, and ignored P2P records were being
   passed to `git show` even though the writer always persisted them as
   canonical checkpoint text. Those unnecessary subprocesses are gone. Project
   product files still use the full Git-object comparison, and the checkpoint
   format and size ceiling, digest/readback and required commit list remain the
   same. A test calls the old and new writers on the **same saved delivery**
   and verifies **byte-for-byte identical portable checkpoints**.
4. **Remove one back-to-back source scan after each read-only verifier.** The
   controller explicitly validates source stability after the verifier returns;
   its immediate candidate check now avoids repeating that *same* source scan.
   Exact candidate, generation, report identity, independent review/proof and
   receipt validation remain. Other source-drift checks are not removed.

No new user action, model stage, autonomous decision, authority or record store
was added. In particular the fix does not skip portable checkpoints, invalidate
the #82 restore path, misclassify P2P-only metadata as product changes, loosen
source/contract enforcement or reuse proof verdicts across changed candidates.

## Reproduce

From a checkout containing the pinned original commit:

```sh
python3 checks/benchmark_p2p_first_pass.py --repeats 4
python3 -m unittest discover -s checks -p 'test_p2p_first_pass.py' -v
```

The benchmark reports the stage sequence, verified report statuses, checkpoint
state, exact candidate key, controller time/attempts from #59, measured
subprocess/snapshot counts, unknown live-model fields and the alternating
execution order. It fails if optimized runs skip a stage, change a verdict or
candidate identity, reduce checkpoint boundaries, or fail to remove redundant
snapshot/Git/source-validation work.

The focused CI gate runs **one old/new pair** to guard the deterministic work
reduction on ordinary PRs without repeatedly running a longer benchmarking
cohort. The four-pair measurement above remains the retained evidence for this
issue. Existing generation, review/proof, recovery, many-file and portable
checkpoint tests remain active.

## Not adopted

**Concurrent review and proof** may reduce wall time substantially when real
model execution dominates, but this environment cannot establish supported
macOS host isolation, two independent writable scratch regions, distinct
simultaneous host sessions and correct interruption/fallback. Adopting it
without those demonstrations would trade quality or recovery for speculative
speed. Keep the existing serial execution until a separately authorized
real-host evaluation proves concurrency safely.

**Compact model prompts** and eliminating other model reasoning calls are
similarly deferred because no paired authenticated-model time/token evidence
was available. Do not shorten authoritative stage instructions or preflight
based only on an offline speed assumption. Cross-session selective reuse and
safe applicability remain within #73, not this cold-delivery optimization.
