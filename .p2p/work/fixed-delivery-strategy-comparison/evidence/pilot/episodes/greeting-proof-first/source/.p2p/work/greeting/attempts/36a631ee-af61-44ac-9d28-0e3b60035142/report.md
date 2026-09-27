# PROVEN: work/greeting.md v1

Requirements: 1/1
Counterexamples tested: 0; the contract defines no input or state variants. The sole public invocation was checked against exact output, exit status, and stderr assertions.
Contract: `work/greeting.md`, revision v1
Contract snapshot: Exact bytes are included in the candidate manifest; SHA-256 `852f618a0d65c579bfca8a42439bfa483802f23e9bbab0f4da667db98658d5d8`.
Source reconciliation: `spec.txt` requires `greet.py` to print `hello` followed by a newline and exit zero; it excludes parent creation, atomic replacement, and crash durability. R1 preserves that promise and those exclusions. Source SHA-256: `043c563287f6436e4b72b40f450ddddc3715fcdd9456c6a8ed0972857a64f08c`.
Parent context: None.
Candidate: `snapshot:sha256:b59546173e23076384bb6566554239a56869c0b628b190d7bccab664a1443ee5`; comparison base `b2ac94d626d3303e08c84265fac24089c8f41cff`.
Candidate stability: Unchanged. Read-only validation before and after execution confirmed the snapshot manifest and key; the tracked product diff against the base was empty, and the untracked-file listing was unchanged.
Contract stability: Unchanged. The post-run validation reconfirmed the work-item and binding-input hashes.
Verification context: Python 3.9.6. Checks ran against the fixed workspace with `TMPDIR` and `PYTHONPYCACHEPREFIX` directed to the supplied scratch directory. Captured outputs are in that scratch directory; this report also records the observations so temporary files are not needed to interpret it.

## Outcome

The complete non-`.p2p` candidate manifest contains `.gitignore`, `greet.py`, `spec.txt`, and `work/greeting.md`; all were inspected. The exact public seam produced the promised output and status. The contract and candidate identities remained stable through verification. No product or contract files were changed. This response contains the report for the enclosing controller to save and reread; no durable report was written by this stage.

The first assertion harness had an escaping error in its expected-byte literal. Its execution still observed `stdout=b'hello\\n'`, status 0, and empty stderr. I corrected the oracle to use the exact expected bytes `68656c6c6f0a`; the corrected assertions passed.

## Requirement verdicts

| ID | Observation and oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | The public seam returned status 0, emitted exactly `hello` followed by byte `0a`, and emitted no stderr. The independent oracle is the source promise in `spec.txt`, matching R1. | Scratch captures `greet.stdout`, `greet.stderr`, and `greet.returncode`; see the command and assertions in the evidence below. | proven |

## Unresolved gaps

None affecting the contract or proof. The protocol's `acceptance-bundle-v1.md` reference was not present at the linked prove-skill path or in the installed skill roots. That reference concerns post-proof bundle inspection; this proof did not require that stage.

## Repairs needed

None.

Fresh `/prove` is required after any repair.

Next steps:

1. No matching implementation review was present in `.p2p/work/greeting/`. Run `/review-implementation .p2p/work/greeting/candidate.json against b2ac94d626d3303e08c84265fac24089c8f41cff` to complete the review/proof pair for this candidate. No PR context was supplied.