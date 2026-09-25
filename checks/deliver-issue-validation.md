# Issue-first host capability probe

Date: 2026-09-25. Host: Codex CLI v0.157.0 on macOS. Repository:
`grove/promise-to-proof`, branch `main`. This probe checks context isolation,
not the issue-first delivery outcome. See the disposable issue run below for
observed D1 behavior. D2-D10 in
[the workflow scenarios](./deliver-issue-scenarios.md) remain **unexecuted**
as complete cases.

Three separate `codex exec --ephemeral --sandbox read-only -C "$PWD"`
invocations used independent sessions:

| Session ID | Stage material read | Observation |
|---|---|---|
| `01a0d98a-04cc-7f50-9500-bf903dda62c6` | `deliver-issue` | Reported that separate read-only review and proof contexts are required. |
| `01a0d98a-627c-7201-b2cd-f88af1e94b7e` | `prove` | Reported that proof must not edit the candidate. |
| `01a0d98b-9173-7612-9a92-5d30ff072091` | `review-implementation` | Reported that review must not edit the candidate. |

The CLI printed `sandbox: read-only` and a distinct session ID on each run.
`git status --short` before and after listed only the in-progress issue #23
edits; `git diff --check` passed after the probes. These sessions alone do not
establish a delivery verdict.

## Disposable issue-reference run

Source: local read-only tracker `#123` in `/tmp/p2p-issue23-fixture`, on a
disposable Git repository at base commit
`c6abd074856fcc3d33a6f5f19a37a565fc02a5e0`. The preapproved canonical
contract was `docs/acceptance-contracts/123.md` v1, SHA-256
`0706a5f05d048a3fa817d98c0b839963e51a8f5e10a298d431e363b427b9afe6`.
The developer gave the issue reference, not report paths or stage commands.
The host was instructed to use separate read-only review and proof sessions;
their distinct invocation records were not retained. The enclosing context
saved and reread the returned reports in
`/tmp/p2p-issue23-artifacts/710a1eb61b495108da7e7ec534b14e49fdbb4aab44540ac6ac2764194e1b0776/`.

Observed sequence: the first run implemented `save_report` and passed two
focused tests but returned `BLOCKED` because the sandbox could not write into
`.git`. With an authorized external artifact directory, resuming from `#123`
captured a candidate and separate review/proof reports. Inventory inspection
found macOS `._*` archive entries; the host recaptured without them. A further
readback caught a shared one-character error in both report hashes, so it
retained those reports and requested fresh separate read-only review and proof
on the same candidate. The corrected v4 reports matched; a final resume from
`#123` returned `REVIEWED` and `PROVEN` with retrievable references. No source
tracker write, commit, push, PR, or label change occurred.

Candidate: `candidate-v3.tar.gz`, SHA-256
`4d3c93851d0a68d44106b62771766c3fb8d9bebb99aa84e22d1995ed5e34900b`.
Its members and bytes match the base tree plus only `app.py` and `test_app.py`;
the unrelated tracker-config edit stays outside the candidate. Before/after
`app.py` SHA-256: `397a9b42caff7f945d905dc338ce1ddeda04a4bdab56bf9fd13bb02a90142761`
to `24fb92868567a9d3fdd302f6c48b8797aa4ffb49a7b07bdcefd34630973f95b3`.
The contract hash remained unchanged. Saved reports: `review-v4.md` SHA-256
`9bfdd6f54db19d5d37994c34ce86185117e5774f11daf03fbe963264ff38fcf4`
and `proof-v4.md` SHA-256
`2713b455b73f5818ca608777e25e9d2508d4b75bd6a81f0572a66bebd6807d8a`.
Proof recorded all four public-seam assertions; the candidate tests passed in
the implementation context. The review sandbox could not create temporary
directories, so it used non-mutating diagnostics instead. The stage report's
original `storage pending` statement remained untouched after the enclosing
workflow saved and reread it.

This validates issue-reference resume, storage, exact identities, and the
returned local result, but not independent stage execution. Because the first
invocation blocked and later
resumes received corrective instructions, the stricter uninterrupted D1 case
remains **partial** until a fresh one-reference run completes without handoffs.

An additional clean attempt used `/tmp/p2p-issue23-fresh` at the same base with
only an unrelated tracker configuration edit and a writable external artifact
directory from the start. Its sole task input was `#123`. The host saved a
candidate and implementation report, but its terminal execution was interrupted
before review and proof. No success verdict was recorded for that attempt.

A second clean run used `/tmp/p2p-issue23-clean2` and the same `#123` input.
It returned `REVIEWED` and `PROVEN`, saving an implementation report, candidate,
review, and proof under `/tmp/p2p-issue23-clean2-artifacts/123/`. Its contract
SHA-256 remained `0706a5f05d048a3fa817d98c0b839963e51a8f5e10a298d431e363b427b9afe6`;
its candidate archive SHA-256 was
`8f9d560d0255afd40caa1c62a63dcac52e27a6da2a42ad8ca48f3293686e41d6`.
Readback **rejected** this claimed success: the archive contained only `app.py`
and `test_save_report.py`, and the reports gave only `c6abd07` for the base,
without a transferable full base tree. Neither saved verifier report recorded
a distinct read-only host invocation or session ID, and proof cited the
implementation test run without a retrievable independent observation. The
reports and candidate hashes matched, but those facts alone do not establish
recoverability or independent verification. D1 remains **partial**, not passed.

A subsequent `#123` resume rejected those reports. Attempting a nested
`codex exec` read-only verifier failed at app-server initialization with
`Operation not permitted`; the workflow returned `BLOCKED` with the missing
independent contexts, preserved the artifacts, and requested a capable host.
This observes the unavailable-host branch of D10, not its untrusted-issue or
storage cases. The earlier top-level read-only Codex probes establish only
that separate CLI sessions can run from the caller, not that this enclosing
agent can spawn them. The preflight now requires a real nested read-only
invocation before implementation.

In a fresh `/tmp/p2p-issue23-gate` run, the required preflight initially failed
with `Operation not permitted`, then succeeded after host permission in nested
session `01a0d9c9-192f-7261-901d-a4c4b8ad8453`. The separate implementation
session `01a0d9ca-17aa-7c82-88e5-bc83473e3335` completed R1-R4 checks and
saved a snapshot. The terminal was interrupted during independent review and
proof dispatch, so no matching full reports or D1 pass were recorded. This
demonstrates the pre-implementation isolation check and separate implementation
invocation, not a successful end-to-end handoff.