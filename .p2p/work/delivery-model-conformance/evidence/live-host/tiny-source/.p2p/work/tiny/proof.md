# PROVEN: work/tiny.md

Requirements: 1/1
Counterexamples tested: 0
Contract: `work/tiny.md`, revision v1
Contract snapshot: exact contract text is recoverable from the candidate manifest; work-item SHA-256 `5fd555eb8132a635c95dcdfb76e647d3b859b51a51539fbc38aeb067986a502a`
Candidate: `snapshot:sha256:fba8e34f9fa4246ccea677efe630aab66d24c62a93677534dbb15ce23ed362ff`
Comparison base: `6ca164bc97b9953607118abcb99bad727b17c757`
Candidate stability: unchanged; the read-only validator matched the live candidate to its manifest before and after the check.
Contract stability: unchanged; the work-item and binding spec hashes matched before and after.
Verification context: fixed workspace; `python3 greet.py`, invoked through a Python subprocess assertion. `TMPDIR` and `PYTHONPYCACHEPREFIX` pointed into the authorized scratch directory; bytecode writing was disabled.

## Outcome

The spec says the CLI prints `hello` followed by a newline and exits zero. The acceptance contract reconciles that promise as R1, with no additional source promises or unresolved gaps. The candidate’s exact stdout, empty stderr, and zero exit status satisfy R1.

## Requirement verdicts

| ID | Observation and oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | The public CLI produced exactly `hello\n`, no stderr, and exit status 0. Oracle: the contract’s expected output and status, derived from `spec.txt`. | This report: command `python3 greet.py` ran in the fixed workspace. Captured output: `stdout repr: b'hello\n'`; `stderr repr: b''`; `exit status: 0`. Assertions compared stdout to bytes `[104, 101, 108, 108, 111, 10]`, stderr to empty bytes, and status to zero; all passed. | proven |

## Unresolved gaps

- None.

## Repairs needed

- None.

No durable report was written here; the enclosing controller owns report storage. No candidate, contract, Git metadata, or controller records were changed.

Next steps:

1. `/review-implementation <saved candidate> against 6ca164bc97b9953607118abcb99bad727b17c757` (review is not present in this handoff).