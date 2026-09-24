# Acceptance contract protocol

Build exactly the promised capability: no less in substance, no more in scope.
Prefer the simplest complete implementation.

## Contract and proof

The acceptance contract says what must be true. Proof says whether it was true
for one exact candidate.

| Artifact | Contents | Identity |
|---|---|---|
| Acceptance contract | Requirements, boundaries, seams, oracles, planned evidence, gaps, and exclusions | Source and contract revision, such as `#124 v3` |
| Proof report | Observations, durable evidence references, and requirement verdicts | Exact contract revision and exact candidate commit or snapshot |

The contract is candidate-independent. Its acceptance matrix uses only `planned`
and `gap` as plan states. Candidate-specific verdicts belong only in proof
reports, including verdicts imported from earlier runs.

Proof and merge readiness are separate. Proof requires neither an open PR nor
green CI. Unrelated failed or pending checks do not block `PROVEN`, and proof
does not wait for them. CI affects a requirement verdict when it supplies
evidence, reveals a counterexample, or prevents verification without another
credible evidence path. Repository standards and other binding constraints
still apply.

Before merge, require current proof, green required checks for the final
candidate, and the repository's review requirements. Use `/fix-pr` to repair CI
failures separately from proof. A repair that changes the candidate requires
fresh proof under the handoff rules below.

## Spec envelope

The lower bound is completeness. Every material promise must reach its complete
observable outcome. Necessary state transitions, invariants, persistence, and
failure behavior belong to the implementation when that outcome depends on them.
Stubs, TODOs, fixture-specific behavior, mock-only substitutes, wiring-only
assertions, and incomplete happy paths do not satisfy a requirement.

The upper bound is scope. Unrequested product behavior, genericity,
configurability, extension points, frameworks, compatibility layers, and adjacent
improvements are outside the contract. Necessary internal engineering and
repository-native abstractions are allowed when correctness requires them.
An explicit invariant can require substantial work. A small implementation can
fully satisfy the contract without extra architecture.

The target is the smallest complete solution. Line count does not establish
completeness or overengineering. Implementation choices stay inside this envelope
and do not authorize changing it.

Repository standards, security constraints, compatibility guarantees, and
applicable parent contracts remain binding even when the ticket does not restate
them. Satisfying them does not constitute product scope expansion.

## Durable contract handoff

Keep one canonical contract location per work item. With a configured tracker,
the originating ticket holds the contract or a direct reference to its repository
file. Otherwise use the repository's documented location, defaulting to
`docs/acceptance-contracts/<work-id>.md`. Use a stable ticket key or source slug
for `<work-id>`. Preserve prior contract text in version history or saved revisions.

The workflow invoking `plan-acceptance` owns saving its returned text under
existing authorization. For tracker storage, attach or link it on the originating
ticket without creating a separate issue. Reread the saved destination before
handing off its location and revision. If saving is unavailable, return the
proposed destination and mark storage pending. A chat response alone is not a
completed durable handoff.
Repository files must travel with the work in a commit or transferred snapshot
when the next session uses another checkout.

Consumers resolve that location and read the source and authorized amendments
before implementation, review, proof, or repair. Report missing or conflicting inputs
instead of reconstructing an agreement from memory. The location finds the
contract; proof still captures its exact text under the identity rules below.

## Pre-approval audit

`audit-acceptance` may independently inspect an exact proposed contract before
human approval. It reconciles every material source promise and contract row,
checks stable identities and revisions, and examines whether seams, oracles, and
evidence plans can establish the stated outcomes. An honestly marked evidence
gap may remain when the outcome is settled; an unresolved outcome decision does
not pass the audit.

The audit is read-only and candidate-independent. `READY_FOR_APPROVAL` means the
exact proposal is fit for a human approval decision, not that approval was
granted. Findings return to `plan-acceptance`, the sole contract author. The
auditor does not revise, save, approve, publish, implement, or prove the contract.

## Requirements and revisions

Each independently falsifiable promise has a stable ID such as `R1`. Input
variations belong in its boundaries. Existing GitHub acceptance checkboxes are
sources to reconcile with these rows, not a second checklist to duplicate.
A checked box is never acceptance evidence.

Reruns preserve IDs by matching the existing promises, not row order. New
requirements receive unused IDs. Splits and merges record the old-to-new mapping;
retired IDs remain recorded and are never reassigned to unrelated promises.
Never silently rewrite an existing requirement.

Contracts start with `Contract revision: v1`. An authorized change to a material
promise, boundary, expected outcome, or exclusion increments the revision.
Record the affected IDs, previous and new agreement, and authorization in a
change note. Preserve the prior revision so old proof remains interpretable.
New evidence, a changed test path, or wording that preserves meaning does not
increment the revision. A changed promise requires fresh proof.

`plan-acceptance` is the sole author of acceptance-contract revisions. Other skills
hand it amendments naming affected IDs, old and new agreement, and authorization.
The invoking workflow saves pending amendments in the source or links them
directly from it. Reconcile them through `plan-acceptance` before work that
depends on the changed promise. Storing its returned text does not authorize
rewriting it.

## Parent and child contracts

`slice-contract` owns decomposition, coverage allocation, dependency planning,
and authorized ticket publication. It consumes an established parent contract;
`plan-acceptance` alone authors parent and child contracts and revisions.
Child ticket criteria are source material for that planning, not a child contract.
Small work can retain the direct contract, implementation, review, and proof path.

A sliced child records the parent's canonical location, revision, and exact text
as an immutable reference or retrievable captured text with a digest. Link the
canonical decomposition and record the child's precise contribution and
prerequisite outcomes. These references must be retrievable in a fresh checkout.
Use qualified obligations in durable cross-ticket references, for example
`grove/project#123 v2:R4`, or an unambiguous repository/source path, revision,
and ID for local work. Child IDs are local to the child contract. Its `R1` does
not mean parent `R1`; map each child row through its `Source` to the qualified
parent obligations it refines. Planning IDs such as `S1` are separate from both.

Judge a child by its own complete outcome and declared contribution, with all
applicable inherited boundaries, invariants, exclusions, and repository
constraints. The parent remains authoritative when a child omits or contradicts
them. Unrelated sibling functionality need not exist for child completion.
For obligations spanning slices, record each contribution, apply constraints to
every affected child, and name where the complete parent obligation will be
checked. A closed prerequisite ticket does not establish its required outcome;
the receiving workflow must confirm the needed artifact or behavior is available.

Consumers read the captured parent, current canonical agreement, source-linked
amendments, contribution mapping, and prerequisites. Capture applicable parent
identities with child reports and recheck them before handoff. If a material
parent change invalidates the mapping or inherited agreement, pause dependent
work and reconcile through `plan-acceptance` and the decomposition workflow.
Preserve prior snapshots and human edits. Regrouping unchanged promises changes
the plan, not the parent's semantic revision. Historical reports retain their
original meaning; they do not establish acceptance of a changed agreement.

Complete allocation is not acceptance evidence. Child proof evaluates the
child contract with its applicable inherited constraints. Final parent proof
evaluates every parent obligation, including interactions and shared invariants,
against one exact integrated candidate. Closed tickets and historical child
proofs do not compose into a parent verdict. Allocate actual integration work
to a named ticket when needed; ordinary parent-level `/prove` needs no separate
integration ticket. Existing review and merge conditions still apply.

## Seams, oracles, and evidence plans

A seam is the highest meaningful public interface through which a requirement
can be observed. Reuse seams agreed in specification or TDD work. A consequential
new seam is an explicit design decision, not an implementation convenience.

An oracle is the independent source that determines whether an observation is
correct. Use the contract, a known-good example, or another independent source.
Copying production logic into the expected result is not an independent oracle.

Each row names its seam, oracle, and one primary evidence path:

- A behavioral test with a named case and an assertion of the promised outcome.
- An invariant with a named constraint or guard and a check that it prevents the
  counterexample through the relevant interface.
- An exact verification command and the condition its successful exit establishes.

`planned` means a credible, concrete path exists but has not established
acceptance. `gap` means the path, seam, or oracle is missing or inadequate.
Unresolved product decisions go in open questions, evidence limits in unresolved
gaps, and deliberate exclusions in out of scope. Planning does not run proof.

## Implementation and review handoffs

Implement the minimum complete solution inside the spec envelope. For every
requirement, reach the real observable outcome and implement the state,
invariant, and failure behavior it needs. Start evidence at the agreed public
seam. Prefer existing repository mechanisms and add machinery only where
correctness requires it. Preserve requirement IDs and promised outcomes.

`implement-contract` consumes the saved agreement and reports development work
for an exact candidate. `review-implementation` inspects a captured candidate against
the agreement, scope, and engineering obligations without repairing it. Neither
authors the contract, grants acceptance, or establishes merge readiness.
Specification, ticket slicing, and TDD may supply inputs without being required.

Implementation and review reports capture the canonical contract location,
revision, and exact text through an immutable reference or retrievable captured
text and digest. Capture the full candidate commit SHA or a reproducible snapshot
including relevant uncommitted and untracked files. A digest without recoverable
content is insufficient for transfer to another checkout. Review also preserves
the comparison base or merge base and included working-tree scope. Implementation
labels an unresolved review base instead of guessing it.

Keep reports outside the candidate. Use a supplied or documented destination;
otherwise propose a destination and mark storage pending until the authorized
workflow saves and rereads it. A prior-session path alone is not a completed
handoff. Transfer the report and recoverable candidate when the next session uses
another checkout. Do not add another canonical contract store or require one
artifact per requirement.

Review findings use local IDs distinct from contract requirement IDs. Supported
corrections within the agreement go to an authorized `implement-contract`
invocation. Named gaps in a matching `NOT PROVEN` report go to `repair-gaps`.
Changed promises or consequential seam decisions return to `plan-acceptance`
through the source-linked amendment convention. These handoffs do not invoke
the next skill or grant publication authority.

Review and proof may run in either order or separately on the same fixed candidate.
Refresh review and any stale proof after candidate changes. Neither stage requires
an open PR or unrelated green CI. Only `prove` issues acceptance verdicts;
the existing merge conditions still apply.

## Proof and repair handoffs

Every proof run binds an exact contract revision to one exact candidate. Record
the full commit SHA or a reproducible snapshot covering relevant tracked and
untracked files. Preserve the exact contract text used, with an immutable
reference or captured content and digest, even when its revision did not change.
An issue number, branch name, or `HEAD` alone is not an exact identity.

Proof records each requirement's observation, independent oracle, durable
evidence reference, and verdict. Evidence references identify the assertion and
its saved output, artifact, or immutable run, with the command and environment
needed to interpret it. Checkbox state and green CI alone do not prove a ticket.

The saved proof report itself may contain the evidence: command, named assertion,
actual observation or relevant output, environment, and candidate identity.
Several requirements may reference the same report section or run. Separate
artifacts per requirement are unnecessary. Save the report outside the candidate
and provide a retrievable reference; a command without its result is not evidence.

- `proven`: credible evidence establishes the full requirement for this candidate.
- `disproven`: a concrete observation violates the requirement.
- `not proven`: evidence or identity is unavailable, weak, ambiguous, or inconclusive.

Overall `PROVEN` requires every material requirement to be proven, no unresolved
contract discrepancy, and unchanged candidate and contract throughout the run.
Otherwise the result is `NOT PROVEN`. Proof leaves the candidate, worktree, and
contract unchanged. Save evidence outside the candidate. Drift invalidates the
run rather than authorizing a repair during proof.

Repair means the smallest complete repair for the named requirements: narrow in
scope, complete in depth. Preserve valid checks and the contract. A repair never
silently weakens a promise or declares acceptance.

Any changed candidate requires fresh proof against all requirements before
acceptance. Prior proof describes only its original candidate. This includes CI
repairs that change product behavior, acceptance evidence, or relevant tests.
A green CI repair does not refresh proof automatically.

## Pull-request publication handoff

`publish-pr` may prepare and, under exact publication authority, publish one
recoverable candidate with matching full `REVIEWED` and `PROVEN` reports as a
draft pull request. Its preview binds the candidate and agreement identities,
reports, destination, target and head refs, commit inputs, title, body, and
authorized commit, push, and pull-request effects. Changed inputs require a new
preview. Publication does not grant merge readiness or merge authority.

The model may invoke `publish-pr` to prepare its read-only `DRAFT` preview after
matching review and proof exist. Model invocation grants no publication effect;
commit creation, push, and pull-request creation require the exact authority
bound by that preview.

The proposed target tip must equal the review report's fixed comparison base.
This keeps the reviewed change set and proposed pull-request change set aligned.
A different target tip requires fresh full review against that tip before
publication; merge readiness remains a later, separate check.

The stable publication identity uses the candidate key to which review and proof
bind: `git:<full-object-id>` for a commit or
`snapshot:sha256:<64-lowercase-hex>` for a snapshot. Contract publication
identity uses SHA-256 of the exact canonical contract UTF-8 bytes with no text
normalization. A content-equivalent commit does not replace a report-bound
snapshot key.

When a snapshot needs a commit, create it in an isolated publication workspace
and compare its complete Git tree with the captured candidate. Record the exact
snapshot-to-commit mapping. A content-equivalent commit preserves candidate-bound
review and proof; any byte, path, mode, symlink, deletion, or included-fixture
mismatch is a changed candidate and cannot be published under those reports.
Persist and reread the created commit and mapping before remote effects. Resume
uses that retained commit; missing or conflicting mapping state blocks creating
a different publication commit from implicit Git metadata. If commit creation
already occurred but that required mapping cannot be established, publication is
`PARTIAL` even when no remote write began. `PARTIAL` consistently means an
authorized local or remote publication effect lacks required completion or
readback.

Push without force to one approved head branch and confirm the remote SHA before
creating a draft pull request. Use stable identity markers and readback to reuse
one exact existing effect after retries or lost responses. Conflicting refs,
ambiguous matches, or uncertain readback block repetition. Reread the pull
request and confirm its head, base, title, body, marker, and draft state before
reporting publication. Required CI, repository approvals, and merge policy remain
separate checks for `merge-readiness`.
