# Incremental delivery reuse: evidence and limits (#73)

A fresh delivery, an unchanged continuation, a receiving-host checkpoint
restore, and a small product edit have different costs and correctness duties.
This change reuses **only saved, independently checkable facts**; it never
transfers old review/proof verdicts to changed code.

## Measured unchanged completion

The [offline GitHub Actions comparison](https://github.com/grove/promise-to-proof/actions/runs/38064869959)
runs each of the following in a fresh disposable repository: a full delivery
using the existing fixture host, then a resume of that exact completed
candidate. For the baseline, only the prior controller entry point from
`324cafb462215abba499d24489c9f7d4e2ec671e` is substituted. For the
optimized case, the current entry point validates and returns the same state
without rendering or rewriting completed canonical records. Baseline and
optimized order alternates across two pairs, and medians are reported.

| Same-version unchanged resume | Previous entry point | Optimized |
|---|---:|---:|
| Median elapsed | 0.398107 s | **0.120602 s** |
| Relative improvement | — | **69.7% less controller time** |
| Git operations | 231 | **87** |
| Canonical local writes per continuation | 8 | **0** |
| New model-stage calls | 0 | **0** |
| Previously verified outcome | REVIEWED + PROVEN | REVIEWED + PROVEN |
| Candidate, stage and checkpoint identities | Unchanged | Unchanged |

The earlier controller already avoided *new model calls* on a completed
candidate; **no model-call saving is claimed for that exact comparison**. The
measured win comes from eliminating unnecessary re-entry through controller
bookkeeping, full completion rendering, and canonical writes while still
checking retained source, agreement, authority, pinned instructions, Git
objects, distinct review/proof host sessions and checkpoint digest.

The cold delivery in the same fixture still performs **two preflight calls,
one implementation, one independent review and one independent proof**. Stage
receipts, attempts and controller elapsed data use existing #59 measurements;
the optimized continuation dispatches none. The portable checkpoint is not
silently skipped, recreated or rewritten.

## Restored and changed candidates

The identical #82 portable checkpoint / Git remote / disposable clone /
receiving-host test passed. It preserves a completed implementation and
review while dispatching **two fresh host preflights and one unfinished
proof** on the receiving machine. It executes **zero new implementation and
zero new review** stages. The offline test episode took approximately
**4.0 seconds**, including Git setup, clone and restore; this is not model
latency or an apples-to-apples end-to-end deployment benchmark.

A small changed-candidate test performs an independently recorded
review/proof for the original Git generation, then changes only `one.py`
while preserving `two.py` and `three.py`. Verified previous per-requirement
traces and exact same-stage host receipts identify:

- **R1:** affected — needs a fresh check.
- **R2 and R3:** their earlier observations are potentially reusable, subject
  to the new verifier independently confirming continued applicability.

Both fresh review **and** proof are dispatched for the second exact candidate
(two new stage calls), and both issue complete-contract reports with that
candidate's new Git identity. **Zero old verdicts** are inherited. The offline
episode took approximately **2.6 seconds**, including fixture Git setup.

The `applicability` advice returns `FULL_RECHECK` for an untracked dependency
change, changed test/oracle, a changed shared support file, unsupported
historical coverage, changed verification environment, missing checked
receipts, unresolved material findings or uncertain risk reach. Those cases
must not be optimized into false acceptance. Exact requirement paths and #42
material seams are reused; no new applicability archive or checkpoint
format is introduced.

## Reproduction

```sh
python3 -m unittest discover -s checks -p 'test_p2p_applicability.py' -v
python3 checks/benchmark_p2p_incremental.py --repeats 2
python3 -m unittest discover -s checks -p 'test_p2p_checkpoints.py' -v
python3 -m unittest discover -s checks -p 'test_p2p_verification_history.py' -v
```

Each deterministic comparison must confirm exact local `REVIEWED_AND_PROVEN`,
unchanged candidate identity, the saved report and checkpoint integrity, and
no extra host dispatches on the unchanged path. It must refuse a modified
candidate, missing checkpoint, pending recovery or interrupted transition.
It compares the same normal controller setup and existing sandboxed-stage
receipts with the earlier entry point. Keep the full prior stage result bytes
for repeatable evidence; the optimized path does not overwrite them.

**The test host is simulated.** Live model tokens, provider time, money and
human effort beyond the controlled fixture are **unknown or unobserved**.
The test reports zero simulated new model calls for an unchanged resume, but
does not establish the real Codex runtime's accuracy, token savings, median
latency or safe concurrent verification. Actual #72 live behavioral evaluation
remains required for judgment claims; the existing #59 structure remains the
only accounting format. Further optimization of cross-session verification
should be driven by authenticated real-host measurements rather than assuming
every historically saved check remains applicable.
