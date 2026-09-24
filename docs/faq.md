# Frequently asked questions

Promise to Proof keeps the source promise, the work done, and the evidence about that work
as separate records. That separation matters most when a ticket is sliced, a
candidate changes after review, or someone resumes the work in a fresh session.
For commands and handoffs, use the [HOW-TO](./how-to.md). For the binding rules,
use the [acceptance contract protocol](./acceptance-contract-protocol.md).

## Issues and slices

### Who creates the original GitHub issue?

For work in this repository, the person or authorized workflow starting the work
creates the source GitHub issue. Promise to Proof has no dedicated originating-issue skill;
use `gh issue create` under this repository's
[issue tracker instructions](./agents/issue-tracker.md). `plan-acceptance` reads a
source and returns a contract for the invoking workflow to save. `slice-contract`
publishes an approved breakdown. Neither silently creates an originating issue.

Projects using these skills may keep a local specification as the source.
`plan-acceptance` accepts a specification or agreed outcome without a GitHub
issue. If an approved split needs a tracker parent for that local source,
`slice-contract` needs explicit approval to create one. It can publish approved
child tickets without treating parent creation as an automatic step.

### Why does a GitHub issue need an acceptance contract?

The issue records the requested change, including context and discussion. The
contract identifies each independently checkable promise, its boundaries, where
to observe it, and how to determine the right result. It also records exclusions
and unresolved evidence gaps. That gives implementation and proof a stable
agreement to use after the issue discussion has grown or the work has moved to a
new checkout. The contract lives on the originating issue or at a direct link
from it, so it does not create another ticket to track.

### When is `slice-contract` useful, and what does `NO SPLIT` mean?

Use it when one parent contract contains several coherent outcomes that people
can implement and review separately. It drafts the fewest useful child tickets,
maps their contributions to parent promises, and can publish the approved plan.
It needs a saved parent contract before a complete decomposition. `NO SPLIT`
means separate tickets add no useful boundary, so the parent can follow the
direct implementation, review, and proof path.

### What are `R1` and `S1`?

`R1`, `R2`, and later `R` IDs identify acceptance requirements in one contract.
They stay with the same promises across revisions. `S1`, `S2`, and later `S`
IDs identify slices in a decomposition. A child contract has its own local `R`
IDs and maps each row to qualified parent obligations, such as
`grove/project#123 v2:R4`. Matching numbers across a parent, a child, and a
slice do not make those records the same requirement.

### If every child is proven, is the parent proven?

No. Each child proof covers that child's outcome and applicable inherited
constraints on its own candidate. A parent promise may cross child boundaries,
and integration may change behavior that passed earlier. Parent proof checks
every parent obligation, including interactions and shared invariants, against
one exact integrated candidate. Assign actual integration code and checks to a
ticket when needed; ordinary parent proof needs no extra integration ticket.

## Contracts and candidates

### What does `audit-acceptance` do?

It assesses whether one exact proposed contract is complete enough for a human
approval decision. It checks the source coverage, scope, requirement identity,
and evidence plans without revising, saving, approving, implementing, or proving
the contract. `READY_FOR_APPROVAL` is advice, not approval. Return
`CHANGES_NEEDED` findings to `plan-acceptance`; resolve the missing input or
decision behind `BLOCKED` before continuing.

### When does a contract revision change?

`plan-acceptance` increments the revision after an authorized material change to
a promise, boundary, expected outcome, or exclusion. It preserves the old
revision and records what changed. A new test path, additional evidence, or
clearer wording with the same meaning does not change the revision. Other skills
can report a needed amendment, but they do not rewrite the contract themselves.

### Why identify an exact candidate?

A branch name or `HEAD` can point to different content later. Proof and review
must say which content they examined: a full commit SHA or a reproducible
snapshot that includes relevant uncommitted and untracked files. The contract's
exact text matters too, even when its revision label has not changed. With both
identities saved, a later session can tell whether an old result still describes
the code in front of it.

### Why save artifacts instead of relying on chat?

A new session or checkout cannot reliably recover the contract text, candidate
files, evidence, and comparison base from a conversation summary. Its
handoffs therefore use saved, retrievable records. A location finds the
contract; the revision and captured text identify its meaning. A candidate
digest can help verify content, but it cannot replace the content needed to
resume work.

## Review, proof, and repair

### What is the difference between review and proof?

`review-implementation` examines whether the candidate follows the contract,
stays within scope, and meets engineering obligations. `prove` checks whether
observed evidence establishes every promised outcome for that exact candidate.
They can run in either order on the same fixed candidate. Review may return
`REVIEWED` while proof returns `NOT PROVEN`, or proof may succeed while review
finds an engineering problem. Neither skill edits the candidate.

### Where do review findings go?

Pass supported findings and their IDs to a separate `implement-contract`
invocation. That skill handles normal corrections within the agreement. After a
candidate change, refresh review and any earlier proof. Do not send a review
finding to `repair-gaps`: that skill requires named repairable gaps from a
matching `NOT PROVEN` proof report.

### What does `PROVEN` mean?

Every material requirement has credible evidence on the exact contract revision
and candidate, with no unresolved discrepancy. It does not mean a pull request
is ready to merge. Required CI, the repository's review rules, and a match
between the reported candidate and the pull request head remain separate gates.
Green CI alone also does not prove an issue, because the configured checks may
miss one of its promises.

### Why run full proof again after a candidate change?

The old report describes the old content. A repair for one requirement can
change behavior needed by another, and an updated test can change the evidence
for a previously proven row. Run `/prove` against every row on the new candidate,
then refresh review. A focused repair check is useful development feedback, but
it is not a replacement for the new proof report.

### How is `fix-pr` different from `repair-gaps`?

`fix-pr` repairs a failed pull request workflow and checks the required CI result
for the repaired commit. `repair-gaps` repairs named implementation or evidence
gaps from a matching `NOT PROVEN` report. A proof can succeed while unrelated CI
fails, and `fix-pr` can return `FIXED` without proving the ticket. When either
repair changes the candidate, refresh the results that described the old one.

### How is `publish-pr` different from `merge-readiness`?

`publish-pr` requires matching full review and proof for one exact candidate. It
prepares a read-only preview, then needs explicit authorization of that exact
preview before it may create a commit in an isolated workspace, push a new
branch, and create a draft PR. Its readback confirms publication, not merge
readiness.

`merge-readiness` inspects the current PR head, matching reports, required CI,
repository approvals, and merge conditions near the merge decision. It does not
publish or merge the PR.

## Workflow choices

### Do the skills call one another automatically?

No. Each skill returns a result and a handoff. Invoke the next skill with the
saved contract, candidate, report, and identities it needs. This lets a person
review decisions and lets another session resume the work without guessing.

### Do I need external planning or TDD skills?

No. Separate planning and TDD skills can help prepare a specification or develop
behavior, but the project's delivery path works without them. Use test-first
development where a useful seam exists, and provide credible evidence for each
contract promise regardless of the development method.

### What if the work reveals a better feature outside scope?

Keep the current implementation within the agreed promise and its necessary
engineering constraints. Record a separate proposal for extra behavior. If the
agreed promise itself must change, preserve an authorized amendment and return
to `plan-acceptance` before dependent work resumes.
