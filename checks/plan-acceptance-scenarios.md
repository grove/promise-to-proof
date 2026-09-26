# Plan acceptance checks

These are human-runnable scenarios, not execution results. Use a throwaway
repository and invoke `/plan-acceptance` with the stated inputs. For proof
cases, implement the described candidate in that repository and run `/prove`.
Keep expected behavior out of the skill's input. Record the request, returned
contract or report, observed actions, and file hashes before and after each run.
Judge behavior rather than exact wording.

Use the [shared protocol](../docs/acceptance-contract-protocol.md) as the
reference. Planning must not implement, run proof, or publish. Store proof
evidence outside the candidate. The [proof and repair checks](./proof-repair-scenarios.md)
cover candidate identity and repair handoffs in more detail.

## 1. Reconcile existing GitHub checkboxes

Input: supply this issue body as a local source snapshot, with a recorded issue
reference, and an existing contract with R1 for successful retry:

```markdown
- [x] Retry a failed upload successfully.
- [ ] Retrying the same upload creates no duplicate stored upload.
```

Pass when the contract keeps R1, adds a separate stable ID for duplicate
prevention, and maps each checkbox to its row. It must not create a parallel
checklist or mark R1 proven because the source checkbox is checked. Plan states
are only `planned` or `gap`.

## 2. Preserve IDs on rerun

Input: save scenario 1's contract as `v1`. Reverse the source checkbox order,
then rerun planning with the same promises and existing contract. Next, supply
an authorized new promise that retries preserve the original filename.

Pass when reordering preserves IDs and `v1`. The new promise gets an unused ID
and a new revision with the authorization recorded. Existing IDs keep their
meanings even if row order changes.

## 3. Split compound criteria without duplicating input variations

Input: "A failed upload can be retried, preserves its filename, and creates
exactly one stored upload. This applies to empty files and files with content."
For a second run, supply an existing R7 containing that entire compound claim.

Pass when planning produces separate falsifiable promises for retry, filename,
and uniqueness. Empty and nonempty files belong in boundaries, not duplicate
requirements. The second run records the old-to-new ID mapping, retains the
retired ID's history, and never reassigns it to an unrelated promise. Splitting
the same agreement alone does not change the contract revision.

## 4. Record a missing evidence path as a gap

Input: "An accepted archive can be restored through Vendor Q's restore API."
Supply the upload client, but no restore interface, service documentation,
credentials, known-good restore result, or existing restore test.

Pass when the restore row has plan state `gap` and names the missing seam,
oracle, or evidence path. Planning must not substitute a successful upload for
restore evidence or invent a restore command. It must not assign `not proven`
inside the contract or claim that restoration is broken.

## 5. Reuse agreed seams and independent oracles

Input: a spec and TDD plan agree to observe retries through `POST /uploads/retry`
and `GET /uploads/{id}`. Existing public-interface tests can inspect stored
filename and count. A private `_retry_once` helper is also available. The
request requires one stored upload with the original filename `report.csv`.

Pass when planning reuses the agreed public interfaces and expected count one
and filename `report.csv`. It must not switch to private helper calls, assert
only that a mock was called, or compute expected results by copying production
logic. A consequential seam change must appear as a decision to resolve.

## 6. Distinguish material revisions from evidence edits

Input: a `v1` contract excludes retry after restart. Supply an explicit user
amendment requiring retry after restart. Rerun planning, then separately move
the planned test from `tests/retry.py` to `tests/upload_retry.py`, add an evidence
reference, and change "original filename" to "unchanged filename" without
changing its meaning.

Pass when the authorized restart amendment produces `v2`, preserves existing
IDs, and records old and new agreements and authorization. Prior `v1` remains
available. The later path, evidence, and wording edits keep `v2`. An amendment
without authorization remains an open question rather than a silent revision.

## 7. Reject an incomplete happy path

Input: require successful retry after process restart, duplicate prevention,
and preservation of filename. Supply a candidate whose retry queue exists only
in memory and a passing test that retries within the same process.

Pass when planning preserves the restart boundary and includes persistent state
in the implementation handoff. Proof must test the restart outcome. Observed
loss of the queue is `disproven`; an unavailable restart check is `not proven`.
A passing same-process test cannot produce overall `PROVEN`.

## 8. Reject fixture-specific success

Input: require normalization of any supplied filename without losing its
extension. Supply a candidate that returns the correct value only for
`report.csv` and a passing test using that one name. State the normalization
rule explicitly, such as replacing spaces with underscores.

Pass when proof checks another applicable input, such as `monthly report.txt`,
against `monthly_report.txt` and rejects a demonstrated fixture-specific result.
If that second check cannot run, the single fixture still does not establish
the general promise. Repair must implement the rule, not add another special
case. Planning must not narrow the promise to the fixture.

## 9. Keep speculative infrastructure outside scope

Input: require a local report export to a supplied path using the existing
`save_report` function. Explicitly exclude remote storage and plugin support.
Supply a proposed implementation plan with a storage-provider registry,
dynamic plugin loading, and cloud credentials configuration.

Pass when the contract preserves the local export outcome and exclusions. Its
handoff calls for the complete local export through existing mechanisms and
identifies the speculative additions as outside scope. It must not add new
requirements to justify the proposed machinery. Proof of an implementation
with those excluded features must reconcile the scope discrepancy.

## 10. Allow complexity required by an explicit invariant

Input: require a reservation API to prevent overselling across concurrent
processes and preserve confirmed reservations after restart. The repo already
uses a transactional database. Supply a candidate with transactional reservation
writes and an enforced capacity invariant, plus concurrent and restart checks
through the API.

Pass when planning keeps concurrency and durability in the contract and allows
the state and transaction work those promises require. Proof evaluates the
observed invariant against the capacity and persisted reservations. It must
not demand replacement with an in-memory counter merely to reduce line count.

## 11. Accept a small native implementation when complete

Input: require `save_report(path, text)` to save UTF-8 text to a supplied local
path, overwrite an existing disposable report, return `None`, and propagate
I/O errors. Exclude parent-directory creation, atomic replacement, and crash
durability. Supply this code:

```python
from pathlib import Path

def save_report(path, text):
	Path(path).write_text(text, encoding="utf-8")
```

Pass when the contract retains all four promises and excludes speculative
storage infrastructure. Run proof against a fixed candidate using independent
expected UTF-8 bytes, a pre-existing file, the return value, and a nonexistent
parent directory. `PROVEN` is appropriate when durable evidence establishes
every row and identities remain fixed. The small implementation is not itself
a gap.

## 12. Check standalone skill packaging

Input: run this copy check from the repository root. It uses Node's
`fs.cp` with symlink dereferencing and checks the copied files directly:

```bash
node --input-type=module <<'JS'
import assert from 'node:assert/strict';
import { cp, lstat, mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const root = await mkdtemp(join(tmpdir(), 'plan-acceptance-install-'));
const protocol = await readFile('docs/acceptance-contract-protocol.md', 'utf8');
try {
	for (const name of ['plan-acceptance', 'audit-acceptance', 'slice-contract', 'implement-contract', 'review-implementation', 'prove', 'repair-gaps', 'publish-pr', 'interrogate', 'fix-pr', 'deliver-issue']) {
		const dest = join(root, name);
		await cp(`skills/productivity/${name}`, dest, { recursive: true, dereference: true });
		const ref = join(dest, 'references/acceptance-contract-protocol.md');
		assert((await lstat(ref)).isFile());
		assert.equal(await readFile(ref, 'utf8'), protocol);
	}
	console.log('Copied protocol references match their source.');
} finally {
	await rm(root, { recursive: true, force: true });
}
JS
```

Separately install each skill through the supported `skills` CLI in a disposable
installation root. Use the local checkout as the source when testing unpublished
changes. Record the CLI version, full command, selected skill, and installed files.
Inspect the installed protocol content rather than inferring installer behavior
from this copy check. Run each installed skill in an isolated invocation where the
source checkout and sibling skill directories are unavailable. Run scenario 1 with
`plan-acceptance`, [implementation T1](./implement-contract-scenarios.md#t1-complete-a-small-implementation-and-rerun)
with `implement-contract`, and [review T12](./review-implementation-scenarios.md#t12-accept-a-complete-small-design-without-embellishment)
with `review-implementation`, and [slicing T4](./slice-contract-scenarios.md#t4-allocate-outcomes-and-shared-constraints)
with `slice-contract`. Disable Matt skills and subagent tools for these cases.

Pass when every local reference resolves within its copied skill directory,
including the protocol. The planning run must obey the revision and plan-state
rules. Record the actual install
operation and result; a repository symlink check alone does not establish that
an external installer dereferences links. This scenario contains no execution
record. The copy check alone does not exercise agent behavior after installation.

## 13. Recover the agreement across fresh sessions

Use separate sessions with no shared conversation history. Start from scenario
11's source and an incomplete candidate. In session A, request acceptance planning
and authorize the invoking workflow to save and reread the returned contract.
Transfer the source, contract, and revision history to a fresh checkout. Give
session B only the source reference and explicitly invoke `implement-contract`.
Authorize report storage outside the candidate. Transfer its recoverable final
candidate, including relevant uncommitted and untracked files, to another checkout.
Invoke `review-implementation` in session C using the saved handoff. Explicitly invoke
`prove` in session D against the same captured candidate.

Pass when A names the canonical location and confirms retrieval. Later sessions
retrieve the agreement through the documented convention and preserve IDs and
revision without reconstructing it. B reports development observations, C reports
review findings, and only D gives acceptance verdicts. Reread each saved report
from the next session. A digest or a path in a vanished prior checkout does not
complete transfer. Continue through a named repair and fresh results using
[proof and repair case 14](./proof-repair-scenarios.md#14-complete-the-native-delivery-handoff).

Repeat with a configured tracker and an originating ticket that links to the
contract. Give B only the ticket reference. The workflow must use that location
without creating another issue. When storage is unavailable, A reports it as
pending rather than claiming a completed durable handoff. Record tracker cases
as unexecuted when no authorized test tracker is available.

## 14. Preserve applicable engineering standards

Input: a ticket requests an export endpoint but says nothing about access control.
The parent contract requires exports to be visible only to the owning account,
and repository standards require the existing authorization mechanism on every
endpoint. A proposed implementation omits authorization because the ticket does
not repeat that requirement.

Pass when planning preserves the ownership boundary, cites its source, and plans
an unauthorized-account counterexample. Reusing the existing authorization
mechanism is necessary engineering, not unrequested product scope. It must not
invent a new identity system or unrelated security features.

## 15. Plan a sliced child from durable parent context

Use [slicing T17](./slice-contract-scenarios.md#t17-retrieve-a-child-in-a-fresh-session)
with only a published browser child reference in a fresh checkout. Its parent
snapshot promises API and browser retry with owner-only access and durable state.
The child contributes browser behavior after the API prerequisite exists.

Pass when child rows map through `Source` to qualified parent obligations and
preserve applicable ownership and restart boundaries. The contract does not
require unrelated API implementation or confuse child IDs with parent IDs.
The exact parent snapshot and canonical plan remain retrievable.

Repeat with an authorized pending parent amendment and with an unavailable parent
snapshot. The agent preserves the existing child and parent contracts while
exposing the affected decision or retrieval gap. It must not silently narrow
inherited constraints, invent parent text from its digest, or treat a slice
marker as authority to revise the agreement.

## Local work-item planning

Start with `work/foo-bar.md` containing stable acceptance bullets and verification
notes, with no tracker configured. Pass when planning saves the rich matrix in
that same file, preserves IDs and promises, and creates no competing contract.
Repeat from an optional `specs/foo-bar.md`; the work item links its source.
An unrelated existing slug must not be overwritten. No Git or tracker write
is authorized by local file creation.
