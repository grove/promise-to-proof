# PROVEN: work/greeting.md v1

Requirements: 1/1

Counterexamples tested: Checked exact output, stderr, and exit-status failure conditions on the specified public invocation; none were observed. The source defines no alternate-input or stateful behavior.

Contract: `work/greeting.md`, revision v1

Contract snapshot: UTF-8 bytes with SHA-256 `852f618a0d65c579bfca8a42439bfa483802f23e9bbab0f4da667db98658d5d8`; binding source `spec.txt` SHA-256 `043c563287f6436e4b72b40f450ddddc3715fcdd9456c6a8ed0972857a64f08c`.

Parent context: None.

Candidate: `snapshot:sha256:b59546173e23076384bb6566554239a56869c0b628b190d7bccab664a1443ee5`; full product manifest validated with `.gitignore`, `greet.py`, `spec.txt`, and `work/greeting.md`.

Candidate stability: Unchanged. Identity validation passed before and after the public-seam check.

Contract stability: Unchanged. Both validations confirmed the exact work-item and binding-input hashes.

Verification context: Python 3.9.6; Git 2.54.0 (Apple Git-157). Ran from `/Users/grove/projects/promise-to-proof/.p2p/work/fixed-delivery-strategy-comparison/evidence/pilot/episodes/greeting-review-first/source/.p2p/work/greeting/runtime/workspace`. `TMPDIR` and `PYTHONPYCACHEPREFIX` pointed into the authorized scratch directory.

## Outcome

The linked specification says `greet.py` prints `hello` followed by a newline and exits zero. Its listed exclusions are parent creation, atomic replacement, and crash durability. The one contract row, R1, maps to the direct `python3 greet.py` seam with exact stdout and exit status as its oracle. The verified candidate prints the required bytes, emits no stderr, and exits zero. No source promises were omitted, and no discrepancy remains for this proof.

The installed proof protocol links to `references/acceptance-bundle-v1.md`, but that file was not present in the installed skill trees. Bundle inspection is not part of this proof, so this did not limit R1 verification.

A preliminary validation invocation used the wrong work-item argument, and the first assertion harness encoded the expected newline incorrectly. Those were setup errors, not candidate observations. I corrected both and reran validation and the public seam; only the successful corrected results below support the verdict.

## Requirement verdicts

| ID | Observation and oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | From the verified candidate workspace, `python3 greet.py` produced stdout `b'hello\\n'`, stderr `b''`, and exit status `0`. Exact-byte, empty-stderr, and zero-exit assertions passed against the contract's public-seam oracle. | `r1-public-seam.json`; command: `python3 greet.py` from the workspace. | proven |

## Unresolved gaps

- None.

## Repairs needed

- None. Fresh `/prove` is required after any repair. Refresh `/review-implementation` separately if the candidate changes.

Next steps:

1. If no full `REVIEWED` report is bound to this snapshot and comparison base `b2ac94d626d3303e08c84265fac24089c8f41cff`, run `/review-implementation <candidate handoff> against b2ac94d626d3303e08c84265fac24089c8f41cff`. This proof does not establish engineering review or merge readiness.