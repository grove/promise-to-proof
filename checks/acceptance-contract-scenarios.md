# Acceptance contract checks

These are human-runnable scenarios, not execution results. Use a throwaway
repository and invoke `/acceptance-contract` with the stated inputs. For proof
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
I/O errors. Exclude atomic replacement and crash durability. Supply this code:

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

const root = await mkdtemp(join(tmpdir(), 'acceptance-install-'));
const protocol = await readFile('docs/acceptance-contract-protocol.md', 'utf8');
try {
	for (const name of ['acceptance-contract', 'acceptance-matrix', 'prove', 'repair-proof', 'interrogate', 'fix-pr']) {
		const dest = join(root, name);
		await cp(`skills/productivity/${name}`, dest, { recursive: true, dereference: true });
		const ref = join(dest, 'references/acceptance-contract-protocol.md');
		assert((await lstat(ref)).isFile());
		assert.equal(await readFile(ref, 'utf8'), protocol);
	}
	const alias = join(root, 'acceptance-matrix/acceptance-contract.md');
	assert((await lstat(alias)).isFile());
	assert.equal(await readFile(alias, 'utf8'),
		await readFile('skills/productivity/acceptance-contract/SKILL.md', 'utf8'));
	console.log('Copied protocol and alias references match their sources.');
} finally {
	await rm(root, { recursive: true, force: true });
}
JS
```

Separately install each copied skill in an isolated invocation where the source
checkout and sibling skill directories are unavailable. Run scenario 1 once
with the canonical skill and once with the deprecated alias.

Pass when every local reference resolves within its copied skill directory,
including the protocol. The alias must load the canonical instructions and
protocol without relying on the canonical sibling's install path. Both planning
runs obey the same revision and plan-state rules. Record the actual install
operation and result; a repository symlink check alone does not establish that
an external installer dereferences links. This scenario contains no execution
record. The copy check alone does not exercise agent behavior after installation.
