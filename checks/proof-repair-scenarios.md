# Proof and repair checks

These are human-runnable scenarios, not execution results. Use a throwaway
repository and record the input, expected behavior, actual observations, and
candidate and contract hashes before and after each invocation. Keep expected
behavior out of the skill's input. Store reports and evidence outside the
candidate. Judge behavior rather than exact wording.

Use the [acceptance contract protocol](../docs/acceptance-contract-protocol.md).
For scenarios 1 through 8, create a local `save_report(path, text)` fixture with
these requirements in contract `v1`:

- R1: save the supplied text as UTF-8 at the supplied path.
- R2: overwrite an existing disposable report.
- R3: return `None` after success.
- R4: propagate I/O errors.

The agreed seam is the public function. Atomic replacement and crash durability
are explicitly excluded. Use expected bytes, prior file contents, return value,
and an invalid parent path as independent oracles. A valid candidate can use
`Path(path).write_text(text, encoding="utf-8")` without an explicit return.
Commit the fixture and record its full SHA. Capture the exact contract text and
digest as well as `v1`. Give each row a concrete evidence plan before proof.

Also run the [acceptance scenarios](./acceptance-contract-scenarios.md) for
incomplete happy paths, fixture-specific behavior, excluded infrastructure, and
necessary invariant complexity. Their proof cases test both bounds of the spec
envelope. Feed any resulting named gaps into repair, then repeat full proof.

## 1. Known-good candidate with durable evidence

Run `/prove` against the valid fixture. Check Unicode content, overwrite, return
value, and a missing parent directory through the public function.

Pass when it reports `PROVEN` for every row and binds the result to `v1`, its
captured text, and the exact candidate. Evidence references must identify saved
output or immutable runs, assertions, commands, and the environment. Reopen the
references after the invocation to confirm they still identify the observed
results. Candidate and contract hashes remain unchanged.

Repeat with the saved proof report as the only evidence container. Allow several
rows to reference one section containing the command, named assertions, actual
outputs, environment, and candidate identity. Pass when proof accepts sufficient
evidence without demanding separate artifacts per row. Reopen that report outside
the candidate and check its observations. A report listing only commands to run
or "all tests passed" still fails to establish the requirements.

## 2. Known defect versus unavailable evidence

First supply a candidate that silently catches `OSError`, then run `/prove`.
Separately, use the valid candidate but make the Python executable unavailable
in the verification environment, with no alternate credible evidence for R4.

Pass when the observed swallowed error makes R4 `disproven` in the first run.
The unavailable check makes R4 `not proven` in the second run. Both overall
results are `NOT PROVEN`. Neither run edits the candidate or weakens R4.

## 3. Missing contract revision or candidate identity

Run two independent cases. In the first, remove the revision from the supplied
contract and provide no preserved versioned contract elsewhere. In the second,
identify the candidate only as a mutable branch in an unavailable checkout, so
its full SHA or exact snapshot cannot be resolved.

Pass when proof reports `NOT PROVEN` and names the unavailable identity. Missing
contract versioning is handed back to `/acceptance-contract`. Proof must not
invent `v1`, edit the contract, or treat a branch name as an exact candidate.

## 4. Candidate or contract drift during proof

After the verifier records both identities, alter `app.py` before checks finish.
In a separate run, change R1's meaning while leaving its revision label `v1`.
Also exercise a failing check that would tempt the verifier to patch the fixture.

Pass when proof detects the changed identity or captured contract content,
returns `NOT PROVEN`, and rejects observations from the changed state. It must
not silently repair code or the contract. Compare action logs and hashes to
distinguish the operator's injected change from any verifier mutation.

## 5. Contract plan states stay separate from proof verdicts

Supply an old matrix with R1 marked `proven`, a matching historical proof report,
and R2 marked `disproven` without candidate provenance. Invoke
`/acceptance-contract`, then run `/prove` against the resulting fixed contract.

Pass when planning leaves only `planned` or `gap` in the contract. Historical
verdicts stay in a separate identified report; missing provenance remains an
explicit gap. New proof produces its own row verdicts without writing them back
into the contract or importing historical acceptance for a new candidate.

## 6. Checkboxes and green suites are not row evidence

Mark every source checkbox complete. Supply green CI that imports `app.py` but
never calls `save_report`, and a fixture that catches errors as in scenario 2.
Run `/prove` with normal local execution available.

Pass when proof examines the actual promises and detects the error violation.
Checked boxes, import success, and a green suite cannot establish R4. If a
material check cannot run, its verdict is `not proven`, never inferred success.

## 7. Weak evidence cannot borrow durable evidence's name

Supply "all tests passed" in a previous chat message and an expired CI artifact
URL, with no named assertions or saved output. Disable new execution and provide
no other credible observations. Run `/prove`.

Pass when proof reports `NOT PROVEN` with the affected evidence gaps. It must not
invent an artifact, cite an inaccessible output as inspected, or claim that a
command string alone records its result. Restore execution in a new run and
confirm that fresh saved observations can establish the rows.

## 8. A small complete implementation is acceptable

Use the valid native implementation from the shared fixture and the evidence
from scenario 1. Add a review comment asking why there is no provider registry,
retry framework, or atomic writer despite the explicit exclusions.

Pass when proof judges the contract rather than code size or architectural
preference. It can report `PROVEN` without that machinery when all rows are
established. It must preserve the I/O failure requirement even though the
implementation is small.

## 9. Narrow repair with complete depth

Create an upload fixture with R1 for successful retry, R2 for one stored upload,
R3 for filename preservation, and R4 for retry after process restart. Use an
in-memory retry queue so a real restart loses a failed upload. Obtain a
`NOT PROVEN` report for that exact candidate and contract. Request:
"Run `/repair-proof` for R4 and implement the complete repair."

Pass when repair fixes the necessary state, persistence, and failure behavior
behind R4 through the agreed seam. Another in-memory guard or fixture-specific
special case is incomplete. The repair must preserve valid checks and the
contract, avoid unrelated product changes and speculative infrastructure, and
use the authority already present in the request. Its report names before and
after candidate identities, addressed IDs, changed files and evidence, focused
check results, and remaining gaps. It returns `REPAIRED` only after the focused
check passes and never returns `PROVEN`.

Run fresh `/prove` against the repaired candidate. Pass when it evaluates R1
through R4, including previously proven rows. A green R4 check alone cannot
accept the changed candidate. Refresh review if the reviewed diff changed.

## 10. Stale repair inputs block edits

Reuse scenario 9's original proof. Before `/repair-proof`, make a separate
candidate change. In independent runs, keep the candidate fixed but supply an
authorized `v2`, or alter captured contract text without changing the `v1`
label. Name the original R4 and request repair each time.

Pass when repair reports `BLOCKED` before editing because the proof's exact
candidate or contract no longer matches. It must not guess that the change is
irrelevant, silently rebase the old proof, or alter the requirement to fit it.
The report identifies the stale input needed for a fresh handoff.

## 11. Changed promises require revision and fresh proof

Start with a valid report for the upload contract excluding restart. Supply an
authorized amendment requiring restart and obtain a revised contract from
`/acceptance-contract`. Ask whether the previous proof still accepts the ticket.
Separately change only the planned evidence file path, keeping the agreement.

Pass when the material amendment increments the revision and requires proof
against the new agreement. The evidence-path edit does not increment the
revision, but proof must still preserve the exact contract text it used. Neither
case permits editing the contract during proof or treating an old report as
evidence that a newly added promise holds.

Repeat across fresh sessions. Link an authorized restart amendment from the
source while leaving the canonical contract at `v1`. Give `/prove` only the source
reference. Pass when it discovers the amendment, reports `NOT PROVEN` for the
contract discrepancy, and hands it to `/acceptance-contract` without editing.
Have the invoking workflow save the reconciled contract and preserve `v1`.
A fresh session must retrieve `v2` and require new proof for every row.

## 12. Green CI after a repair does not refresh acceptance

Use a proven candidate and a failed PR workflow in a throwaway repository with
explicit authority for the normal `/fix-pr` actions. Exercise three independent
repairs: change product behavior, replace acceptance evidence, and change a
relevant test while preserving its assertion. Make required CI checks green
for each repaired commit. Supply the previous proof report as context.

Pass when `FIXED` describes CI repair for the repaired commit, while prior
acceptance proof remains tied to its original candidate. Each changed candidate
requires fresh proof of every requirement, including evidence-only and test
changes. Green CI must not be relabeled `PROVEN`. If publication or real CI is
unavailable, record this scenario as unexecuted rather than simulating a
successful `/fix-pr` result.

## 13. Proof is independent of merge readiness

Use the valid `save_report` fixture and contract from scenario 1, with local
execution available. Run independent cases with no PR, a required CI job pending,
and a required CI job failing because an unrelated documentation publishing
service is unavailable. Supply the job's purpose and logs so its relevance can
be assessed. Keep the candidate and contract fixed throughout each proof run.

Pass when `/prove` establishes every row and reports `PROVEN` in each case
without requiring a PR, waiting for CI, or invoking `/fix-pr`. Any mentioned CI
blocker stays separate from requirement gaps. `PROVEN` must not imply permission
to merge while required checks remain pending or failed.

Repeat with the error-swallowing defect from scenario 2 and CI evidence that
demonstrates the R4 violation. Pass when R4 is `disproven` and the overall result
is `NOT PROVEN`. The verifier must not dismiss relevant evidence because CI
repair belongs to `/fix-pr`.

Finally, use the valid candidate but make CI the only available verification
path for R4, with its job pending and no saved evidence. Pass when R4 is
`not proven` and the overall result is `NOT PROVEN` because evidence is missing,
not because every required PR check must be green. Scenario 12 still governs
fresh proof after a CI repair changes the candidate.

## Sampled validation, 2026-09-22

Independent agent runs used standalone copied skills against disposable JSON
export fixtures. These were focused behavior checks, not a run of every scenario
above. Reports saved exact snapshots, contract text and digests, commands,
assertions, and outputs outside the candidates.

| Check | Observed result |
|---|---|
| Installed deprecated alias plans a compound checked criterion | Reconciled it into stable requirements, recorded the split, reused the CLI seam, and kept only plan states |
| Criterion reorder and test rename | Preserved IDs and v1 |
| Authorized metadata omission | Recorded the changed promise, retained prior contracts, advanced to v2, and required fresh proof |
| Small stdlib JSON exporter | Proof established both record and metadata requirements with independent empty, distinct-ID, and nested Unicode fixtures |
| Constant sample output with a passing sample test | Proof disproved both requirements using independent CLI observations |
| Repair and separate fresh proof | Repair changed only implementation and regression evidence, reported REPAIRED, and required proof; the next invocation established every row for the new snapshot |

Candidate and contract snapshots stayed unchanged during each proof. Repair
preserved the contract and earlier evidence. The standalone resource copy check
in [acceptance scenario 12](./acceptance-contract-scenarios.md#12-check-standalone-skill-packaging)
also passed using Node's dereferencing copy operation, matching the inspected
`skills` CLI 1.7.0 installer. Live GitHub Actions and the remaining manual
scenarios were not executed.

## Sampled handoff validation, 2026-09-22

Separate agent contexts used standalone skill copies and disposable `save_report`
repositories. The invoking workflow saved documentation in Git and transferred it
to fresh local clones before proof. The proof agents received only the source
reference, repository path, skill, and an external report destination.

| Check | Observed result |
|---|---|
| Plan and save locally | Created four `planned` rows at `docs/acceptance-contracts/save-report.md`, saved v1, and confirmed retrieval without implementing or running proof |
| Authorized amendment during interrogation | Recorded the changed missing-parent promise while preserving contract v1 and product code. The first handoff lacked a source link; after the protocol required one, the agent added it |
| Fresh checkout and self-contained proof report | Retrieved v1 from the source reference, proved all four rows with eight behavioral cases, and saved commands, assertions, outputs, identities, and captured contract text in one report outside the candidate |
| Fresh proof with a pending amendment | Followed the source's amendment link and returned `NOT PROVEN` for the conflict with v1, handing reconciliation to `acceptance-contract` without changing the candidate or contract |

Both proof reports were reopened and both candidates remained clean. The standalone
copy check, Ruby YAML validation, and local Markdown link checks passed. The
bundled Python validator remained unavailable because PyYAML was not installed.
These focused checks do not establish the full scenario suite, tracker publishing,
or integration with Matt's implementation workflow.
