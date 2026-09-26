# How to take a work item from promise to proof

For a shorter set of task recipes, start with the [HOW-TO](./how-to.md).
The [FAQ](./faq.md) answers common questions about issue creation, slicing,
review, and proof. This guide gives the detailed path and examples.

A convincing implementation is not the same as a finished ticket. The code can
look right while one sentence from the issue never reaches a test. A test suite
can pass while its assertions miss the promised result. A green pull request can
hide a weakened check.

Use `/deliver-issue work/<slug>.md` for one coherent local work item on a host that supports
separate stage invocations and independent read-only review and proof contexts.
It coordinates the native skills to plan acceptance, implement the agreed
capability, review a captured candidate, and prove the result. Optional external
planning and TDD tools can help, but the delivery path works without them.

The acceptance contract defines the spec envelope. Implementation fills it.
Proof establishes that one exact candidate satisfies one exact contract revision.

```text
source → plan-acceptance → optional audit-acceptance → any required approval
       → saved contract → implement-contract → captured candidate
       → review-implementation + prove → optional publish-pr → merge-readiness
```

The sequence is not a ceremony. Each skill answers a different question.
Skip optional planning, slicing, and repair steps when they do not apply.
Merge still requires current proof for the final candidate.
After a proven delivery, `/retrospect` can separately evaluate experience for
future work; it is not part of publication or merge readiness.

## Install the skills

Install the skills:

```bash
npx skills@latest add grove/promise-to-proof
```

In a new project, run `/setup-promise-to-proof` to establish `specs/`, `work/`,
`.p2p/work/`, and `.p2p/tmp/` with validated ignore rules. Existing configuration
and human edits are preserved. Tracker configuration is optional.
External planning or TDD tools are also optional; install Matt Pocock's
collection separately if you want them:

```bash
npx skills@latest add mattpocock/skills
```

Both collections can use the same project-local configuration when its tracker
and label conventions match.

To list the current skills from a clone, run:

```bash
rg --files skills -g SKILL.md | sort
```

The stage skills remain available independently, including on hosts where
`/deliver-issue` reports that independent contexts are unavailable. The manual
path uses explicit phases:

```text
/plan-acceptance       -> propose the contract
/audit-acceptance      -> optionally check the exact proposal before approval
/implement-contract    -> save the report and capture the candidate
/review-implementation -> save findings for that candidate and comparison base
/prove                 -> save the proof and requirement evidence
/publish-pr            -> preview or publish the exact candidate as a draft PR
/retrospect             -> optionally evaluate a proven delivery for future advice
```

Review and proof may run in either order against the same fixed candidate.
Stage skills do not invoke the next skill. `/deliver-issue` owns their handoffs
and invocations, but not publishing. Neither review nor proof needs an open PR or
unrelated green CI. Merge requires current proof, green required checks for the
final candidate, and the repository's review requirements.

## Start from a local work item

A lasting specification belongs in `specs/<slug>.md`. Plan one coherent delivery
in `work/<slug>.md`; a small task needs no separate specification. The work file
holds the only canonical acceptance contract. The remaining examples use
`work/retry-safe-uploads.md` and its child `work/retry-safe-uploads-api.md`.

```text
/plan-acceptance specs/retry-safe-uploads.md
/deliver-issue work/retry-safe-uploads.md
```

A GitHub issue can be imported through `plan-acceptance` or `deliver-issue`.
Preserve attribution and reconcile later source changes as proposed amendments.
Local delivery and slicing do not require a tracker. Optional `triage-issue`
recommends a next action for an existing issue; `create-parent-issue` previews
an optional spec mirror. Tracker writes require their own authority.

## Optionally shape the work with external planning tools

For a feature that begins as an idea, start with a focused conversation:

```text
/grill-with-docs Add retry support for failed uploads
```

The skill presses on unclear requirements while it keeps the project's domain
language and architectural decisions up to date. Once the important choices are
settled, turn the conversation into a durable specification:

```text
/to-spec
```

If an external workflow such as `/to-tickets` has already created tickets, they
remain valid inputs. For a local specification, run `/plan-acceptance` directly. Use
`/create-parent-issue` only when a GitHub mirror is wanted. To divide an agreed parent contract, use the optional
[slicing step](#divide-large-work-without-changing-the-agreement).

Use `/wayfinder` before `/to-spec` when the work is too large or uncertain for
one agent session. It records the decisions that block a reliable plan and
resolves them one at a time. When the issue already states a complete, agreed
outcome, skip these planning steps and begin with `plan-acceptance`.

## Request an independent critique when it helps

If you want the agent to assess whether a proposal will achieve its intended
outcome, explicitly invoke `critique` with an idea, local document, or GitHub
issue:

```text
/critique <idea, document path, or GitHub issue reference>
```

The agent checks consequential claims and recommends whether to proceed,
adjust, or rethink the approach. When missing evidence prevents a defensible
judgment, it reports insufficient evidence and the smallest useful next check.

Use `critique` for agent-led assessment of a supplied proposal. Use `interrogate`
when you want to lead the questions about the agent's proposal and reach a
design decision. `plan-acceptance` plans requirements and evidence, while
`prove` verifies an implementation against the agreed contract.

Critique is optional and advisory. It does not edit the artifact, repository,
or acceptance contract, publish findings, or begin implementation. No downstream
skill is required. You can take unresolved decisions into `interrogate`, plan
acceptance with `plan-acceptance`, or proceed directly when appropriate.

## Turn the ticket into an acceptance contract

Start with a GitHub issue, a specification, or an agreed outcome that states
what the change must accomplish. If the source only says "improve retries" or
"make uploads reliable," resolve that ambiguity before implementation. The
workflow cannot preserve a promise that nobody has made concrete.

Run `plan-acceptance` against the source:

```text
/plan-acceptance work/retry-safe-uploads-api.md
```

Follow the [acceptance contract protocol](./acceptance-contract-protocol.md)
for the shared rules. The skill records a contract revision
such as `v1` with stable `R` IDs, independent of any implementation candidate.
Each row names the promise, relevant boundaries, the seam where behavior is
observed, an independent oracle, and planned evidence. An oracle defines the
correct result without taking the candidate's output as the answer.

Include empty inputs, retries, restarts, authorization boundaries, and partial
failures when the promise depends on them. Record outcomes and exclusions so
the contract states both what completion requires and what remains out of scope.

Keep plan state separate from proof. Contract rows use only `planned` or `gap`.
Use `gap` when the seam, oracle, or evidence path is missing or inadequate.
Record unresolved product decisions as open questions. Only `prove` assigns
`proven`, `disproven`, or `not proven` to rows for a fixed candidate. A test name or
planned command does not establish behavior.

For a retry ticket, the useful result is a contract with separate promises such
as these:

```text
R1: A failed upload can be retried successfully.
R2: Retrying the same upload leaves exactly one stored upload.
R3: The retry preserves the original filename and metadata.
R4: The retry succeeds after the application reloads its state.
```

For R4, plan a check through the upload API and a fresh application process.
Use the original filename, metadata, and stored upload count as independent
expected results. A test that retries against the same in-memory object cannot
establish the restart promise.

Preserve requirement IDs across revisions. Increment `v1` to `v2` only for an
authorized material change to a promise, boundary, outcome, or exclusion.
Record the affected IDs, agreement, and authorization, and preserve the prior
revision. Moving a test file, changing an evidence path, or clarifying wording
without changing meaning does not increment the revision. Never weaken R4 to fit an
implementation that loses retry state on restart.

Reconcile GitHub checkboxes with the contract. A checked box is a completion
claim to verify, not evidence. Resolve a mismatch before claiming acceptance.

For an independent check before approval, run:

```text
/audit-acceptance <exact proposed contract> against <source>
```

`READY_FOR_APPROVAL` is advice about that exact proposal, not approval.
`CHANGES_NEEDED` returns audit findings to `plan-acceptance`; `BLOCKED` requires
the missing source, identity, authority, parent context, or outcome decision.
The audit does not revise or save the proposal and does not inspect a candidate.

Save and reread the contract in `work/<slug>.md` under the planning request's
local write authority. Keep required agreement approval separate from saving
its proposal. Preserve the acceptance matrix and revision in that same file.
Minimal acceptance bullets can be enriched in place; they do not require a
second contract store. See the protocol's
[durable handoff convention](./acceptance-contract-protocol.md#durable-contract-handoff).

## Divide large work without changing the agreement

Keep one coherent task on the direct path. For larger work, save the parent
contract and request local children:

```text
/slice-contract work/retry-safe-uploads.md
```

The skill inspects the exact parent, existing work, and implementation. It
creates the fewest useful child work items, maps every parent promise to a
contribution and completion check, and records prerequisites. The parent lists
its children; each child links back through a `Parent:` Markdown link.
`NO SPLIT` means separate work items add no useful boundary. A missing parent
contract returns to `plan-acceptance`.

By default, children use names such as `work/retry-safe-uploads-api.md` and
`work/retry-safe-uploads-browser.md`. A child gets a separate specification
only when it defines an independently reusable product or design concept.
Saving local work does not authorize tracker writes, commits, or pushes.
For a preview without writes, request `draft only`.

Resolve consequential outcome and dependency choices before dependent work.
The exact parent bytes, source specification, and inherited constraints remain
binding. Each child's local IDs map to qualified parent requirements such as
`work/retry-safe-uploads.md v2:R4`; equal ID numbers do not imply equal promises.

Plan acceptance in each child file, then deliver it:

```text
/plan-acceptance work/retry-safe-uploads-api.md
/deliver-issue work/retry-safe-uploads-api.md
```

Resume slicing with the parent work-item path. Inspect existing files and
preserve human edits rather than recreating children. A path collision requires
resolution before writing. Optional tracker publication mirrors these local
files only after explicit authorization and verified remote readback.

Finally, review and prove the full parent on one exact integrated candidate,
including interactions and shared invariants. Assign actual integration code
and checks to a child when needed. Ordinary parent proof needs no extra work
item. Closed children and historical child proofs cannot establish that result.

## Challenge the design before code makes it expensive

When the implementation has a consequential choice, run `interrogate` after
the contract and before editing code:

```text
/interrogate work/retry-safe-uploads-api.md
```

Ask the agent to name the affected files, the proposed flow, the assumptions
that must remain true, and the evidence that will establish each requirement.
Then challenge the parts that would be painful to reverse. Persistence,
concurrency, authorization, migrations, caching, and cross-service changes
deserve more scrutiny than a local rename because a plausible design in those
areas can fail far from the edited line.

Challenge both missing required behavior and speculative machinery. Reuse the
agreed testing seams; treat consequential new seams as explicit decisions.

`grill-me` lets the agent interview you about your decisions. `interrogate`
lets you question the agent's understanding and proposal. You can use either
on its own, or carry the decisions from `grill-me` into `interrogate` without
repeating the interview.

Lead with the questions you need answered. The agent explains the evidence,
revises the proposal when an objection holds, and identifies checks that could
settle unknowns. Continue until you are ready to move on; there is no turn limit.
Then carry the agreed approach, authorized requirement changes, and unresolved
questions into the next step. Save authorized amendments in the source or link
them directly from it. Have `plan-acceptance` reconcile them before work
that depends on the changed promise. Use implementation authority
already present in the request. If the request covers design only, obtain
implementation authority before editing code.

Skip `interrogate` when the design is already clear and the cost of a wrong
choice is low. A one-line correction with an existing regression seam rarely
needs a separate design session. The acceptance contract still helps because
small diffs can omit behavior too.

## Implement the saved agreement

Pass the ticket or canonical contract path to the implementation skill:

```text
/implement-contract work/retry-safe-uploads-api.md
```

Explicit invocation authorizes scoped local implementation and safe development
checks unless your request limits the work to planning or inspection. It does
not authorize commits, pushes, publication, deployments, or destructive changes.

Resolve the saved contract, inspect the source, and reconcile pending amendments
before implementing affected behavior. Preserve unrelated work. Stop affected
edits when ownership overlaps or concurrent changes make the target uncertain.
Do not reset, stash, or discard changes to produce a clean worktree.

Build the smallest complete implementation within the specification. Include
necessary invariants, state transitions, failure handling, and persistence.
For the retry example, R4 requires durable retry state even if an in-memory fix
has a smaller diff. Omit speculative machinery that no promise requires.

Use meaningful checks at the agreed public seams. Prefer test-first development
for new behavior and regressions where a suitable seam exists. An external `/tdd`
skill is an optional aid, not a required dependency. Existing checks may suffice for
already-covered behavior or documentation. A missing planned test is work to
perform; an unavailable material check must remain a reported limitation.

Expect `IMPLEMENTED`, `PARTIAL`, or `BLOCKED`. The report maps requested requirement
IDs to implementation locations, observed checks, and remaining gaps. For an
explicit subset such as R2, the outcome covers that subset and keeps unresolved
R4 visible. No implementation outcome declares acceptance.

## Capture and transfer the candidate

Save `implementation.md` and `candidate.json` under `.p2p/work/<slug>/`.
Review, proof, repair, and resume find them from the work-item path. Capture
the full candidate commit SHA or a recoverable snapshot with exact paths, bytes,
modes, symlink targets, and deletions. Include relevant uncommitted and untracked
files. Exclude all of `.p2p/` from the candidate and use the fixed review base.

Record exact work-item and binding parent/specification hashes. Use local
Markdown links on `Source:`, `Parent:`, or `Parent contract:` lines to identify
binding documents. Preserve source attribution when importing external text.
A mutable issue, branch name, or bare digest is not a recoverable candidate.

Before replacing records, retain prior bytes and related evidence in Git or the
work item's `history/` directory. Never save secrets, including inside snapshots.
For unsuitable evidence, retain a safe durable reference, checksum, and access
limitations; otherwise report it unavailable. Required observations must survive
deletion of `.p2p/tmp/` and OS temporary files.

Commit durable records only when authorized. If candidate A is followed by a
commit B containing reports, reports still describe A. Compare the complete tree
outside `.p2p/`, current work-item and binding-input bytes, and comparison base
before reuse. A fresh checkout resumes from `work/<slug>.md` and the retained
candidate, reports, and evidence, without manually supplied artifact paths.

## Review the captured implementation

Invoke review separately with the source, candidate, and comparison context:

```text
/review-implementation <saved implementation handoff> against <comparison base>
/review-implementation <saved implementation handoff>; include uncommitted work
```

`review-implementation` resolves mutable references to fixed identities and examines
contract fidelity, scope and simplicity, and engineering quality. It reads the
actual diff and relevant surrounding implementation, including unchanged code
that a requirement depends on. A working-tree review includes the requested
staged, unstaged, deleted, and relevant untracked files.

Expect `REVIEWED`, `CHANGES NEEDED`, or `BLOCKED`, with coverage and limitations
visible. `REVIEWED` is neither acceptance proof nor platform approval. Review
inspects and may run safe isolated diagnostics, but never edits or repairs the
candidate. Candidate or contract drift prevents a complete conclusion for the
changed target.

Save and reread `.p2p/work/<slug>/review.md`, outside the candidate by definition. Preserve finding IDs, affected requirement IDs, candidate
identity, and the captured base and comparison scope.

For supported implementation findings under the same agreement, explicitly
invoke `implement-contract` with the saved report and selected finding IDs.
For changed promises or consequential seam decisions, save a source-linked
amendment and return to `plan-acceptance`. `interrogate` can help resolve the
decision. A review finding alone is not the matching `NOT PROVEN` report required
by `repair-gaps`.

After implementation changes the candidate, refresh review and any prior proof.
Neither the implementation nor review skill runs the next phase implicitly.

## Prove the fixed candidate

Run `prove` only after the candidate and the contract revision are fixed:

```text
/prove <saved contract>; candidate <saved implementation handoff>
```

The skill starts from the source promises instead of the implementation. For
every requirement, it identifies an observation and an independent oracle that
decides whether the result is correct. It also searches for realistic
counterexamples at state transitions, retries, restarts, authorization
boundaries, concurrency windows, and the final workflow outcome when those
cases apply.

Bind the proof report to the exact contract revision and exact candidate
identity, and preserve the exact contract text used. For each row, retain
durable evidence references with the command or observation, actual result, and
oracle comparison. A passing suite summary
cannot replace missing row evidence.

The saved proof report can hold the commands, named assertions, actual outputs,
environment, and candidate identity itself. Reference its sections from the
requirement rows and save it at `.p2p/work/<slug>/proof.md`. One report can cover many rows.

Do not ask `/prove` to fix what it finds. Proof must leave both the candidate
and the contract unchanged so that every observation still belongs to the same
code. If a file changes during the run, the old observations no longer support
the new candidate. The correct verdict is `NOT PROVEN`, followed by a separate
repair and a fresh proof.

Read the verdict literally:

```text
PROVEN
Every material requirement has credible, durable evidence for the exact
contract revision and fixed candidate.

NOT PROVEN
At least one requirement, evidence path, contract detail, or candidate identity
remains unresolved.
```

`NOT PROVEN` does not always mean that the product is broken. A concrete
counterexample is `disproven`, while an unavailable service, an inconclusive
assertion, or an uncertain candidate is `not proven`. Both block acceptance,
but they call for different repairs.

## Repair only the gaps that proof named

When `/prove` returns `NOT PROVEN`, pass the proof result and its unresolved
requirement IDs to `repair-gaps`:

```text
/repair-gaps <matching proof report>; candidate <saved implementation handoff>; requirements <IDs>
```

Check that the proof result, contract revision, and candidate still match.
Proceed under existing repair authority, including the current request. Ask
for authority only if the request does not authorize the needed edit.

The skill makes the smallest complete implementation or evidence repair for the
named IDs. Keep the scope narrow while repairing the full cause, including
necessary state, failure, and persistence paths. For R4, another in-memory retry
guard is incomplete if restart still loses the upload. Preserve valid checks,
run a focused check, and report the candidate before and after the repair.

Expect `REPAIRED`, `NO CHANGE`, or `BLOCKED`, never `PROVEN`. A passing focused
check shows that the repair is worth testing again, but it does not re-evaluate
the other requirements against the changed candidate. Run full proof again
for every contract row after each candidate change:

```text
/prove <saved contract>; candidate <repaired candidate handoff>
```

Repeat this loop only while proof identifies specific, repairable gaps:

```text
prove
   ↓
NOT PROVEN with repairable named gaps
   ↓
repair-gaps
   ↓
changed candidate
   ↓
fresh prove
   ↓
fresh review-implementation when the reviewed candidate changed
```

Stop when the missing input is a product decision, unavailable credential, or
external capability. `repair-gaps` must not guess its way through a stale or
ambiguous contract.

After a repair changes the candidate, refresh review as well as full proof:

```text
/review-implementation <repaired candidate handoff> against <comparison base>
```

Proof checks whether the ticket's promises hold. Review examines contract fidelity,
scope, and engineering quality. Keep both results tied to the repaired candidate;
you may run them in either order.

## Publish the exact candidate as a draft pull request

After the candidate has matching full review and proof, prepare publication
without changing local or remote state:

```text
/publish-pr <saved candidate, review, and proof handoff>; target <branch>; draft only
```

Review the exact destination, target tip, head branch, candidate-to-commit plan,
title, body, and requested effects. Then explicitly authorize that unchanged
preview. `publish-pr` uses a matching commit or creates one in an isolated
workspace, verifies its complete tree outside `.p2p/` against the captured candidate, pushes
without force, creates one draft pull request, and rereads the remote state.

A content-equivalent commit preserves the candidate-bound reports because the
skill records the exact mapping. A mismatch blocks publication rather than
silently adopting new bytes. `PUBLISHED` still leaves CI, repository approval,
and merge policy to `/merge-readiness`.

## Check the current pull request before merge

Near the merge decision, run `/merge-readiness <PR URL>` with the saved full
review and proof reports. It checks their exact agreement and candidate against
the current PR head and base, required CI (including applicable merge-queue
checks), repository approvals, and other merge conditions. `REVIEWED` is not a
GitHub approval. The result is `READY`, `BLOCKED`, or `UNKNOWN` for
the inspected PR state. The skill updates the PR description's readiness entry
and confirms it by readback before the merge handoff. An explicitly read-only
request leaves the description unchanged. Even `READY` does not merge or
authorize merging. A changed head, base, contract, or gate state needs a new
assessment.

## Repair failed GitHub Actions without weakening the check

If a required GitHub Actions workflow fails, invoke `fix-pr` with the pull
request or the failed workflow run:

```text
/fix-pr #456
```

The skill finds the earliest causal failure, classifies it as `PRODUCT`,
`WORKFLOW`, or `EXTERNAL`, and repairs the layer that owns the failure. It may
inspect, edit, commit, push, and rerun workflows on the target pull request
branch. It never force-pushes, and it stops when the branch, commit, credentials,
or safe execution path cannot be established.

Keep the failed quality signal intact. Deleting a test, lowering coverage,
making a required job optional, swallowing an error, or adding an arbitrary
retry does not repair the workflow. A changed check is valid only when the
contract and evidence show that the old check was wrong or obsolete, and the
replacement must provide stronger evidence for the same promise.

Treat an unexplained green rerun as unresolved flakiness, not a fix. `FIXED`
means that the cause is understood, the repair is durable, the repaired commit
is pushed, and every required check is green for that exact commit. `NOT FIXED`
keeps an unavailable dependency, unsafe branch state, uncertain cause, or
pending verification visible.

`FIXED` is narrower than `PROVEN`. GitHub Actions can show that the configured
checks passed without showing that every ticket promise was checked. Every
changed candidate makes its previous proof stale. Run full `/prove` again on
the repaired candidate, especially after product, acceptance evidence, or
relevant test changes. A contract revision can remain unchanged while its
candidate needs fresh proof. Refresh `/review-implementation` for the changed candidate
as well.

## Learn from a proven delivery (optional)

Use `/retrospect` when concrete use or maintenance experience reveals something
worth considering in future work. It is not a second review or proof run, and it
does not depend on a PR, unrelated green CI, or a merge. Start with a saved full
`PROVEN` report, the exact candidate it covers, and the canonical contract's
revision and recoverable text. Bring retrievable observations, such as a support
record or attributed team feedback, and a saved matching review if available:

```text
/retrospect <saved PROVEN proof>; candidate <exact proven candidate>; experience <retrievable observations>
```

The evaluation names each observation's source, effect, limits, and consequence.
For example, repeated maintenance reports about brittle tests may support
advice to specify a user-visible outcome next time; they do not change what
the old contract required. A suspected broken promise instead goes to a fresh
review and proof for the applicable exact candidate, or a normal issue
follow-up. The historical `PROVEN` report stays unchanged. With weak evidence
or nothing useful to learn, the report can have no suggestions.

Save the evaluation at `.p2p/work/<slug>/retrospective.md` under existing
authority and confirm another session can retrieve it and its evidence. If
saving or readback fails, keep storage pending; a chat reply is not a
saved report. Review each suggestion separately. Accept, reject, or rewrite it
only after seeing the exact proposed change; acceptance of a rewrite requires
wording supported by the observation. Use existing report-write authority for the evaluation. Obtain authority for
each accepted entry in the project-local advisory register before writing it. The
default register is `docs/retrospective-learnings.md`, created only on the first
authorized accepted learning. Rejected suggestions remain in the evaluation report.

Later `/plan-acceptance` runs consider relevant active register entries as
advice, with a citation and reason. Advice cannot add a requirement or change an
agreement by itself: promotion to a rule or contract revision needs separate
human authorization through the owning workflow. To evaluate a later candidate,
obtain its own proof and run a separate retrospective; neither the earlier report
nor its disposition becomes a merge gate.

## Choose the shortest workflow that covers the risk

For a standalone work item with a settled design, use the compact path:

```text
/plan-acceptance work/retry-safe-uploads-api.md
# Optionally audit the exact proposal before any required approval and saving.
/audit-acceptance <exact proposed contract> against <source>
/implement-contract work/retry-safe-uploads-api.md
/review-implementation <saved implementation handoff> against <comparison base>
/prove <saved contract>; candidate <saved implementation handoff>
/publish-pr <saved candidate and reports>; target <branch>; draft only
# Approve the exact publication preview.
/publish-pr <approved preview>; publish the draft PR
```

For a larger feature, start with a specification and local slices:

```text
/plan-acceptance specs/retry-safe-uploads.md
/slice-contract work/retry-safe-uploads.md
/plan-acceptance work/retry-safe-uploads-api.md
/deliver-issue work/retry-safe-uploads-api.md
/plan-acceptance work/retry-safe-uploads-browser.md
/deliver-issue work/retry-safe-uploads-browser.md
/review-implementation work/retry-safe-uploads.md; candidate <integrated candidate>
/prove work/retry-safe-uploads.md; candidate <integrated candidate>
```

For a difficult bug, optionally use an external `diagnosing-bugs` skill before implementation:

```text
/plan-acceptance work/retry-safe-uploads-api.md
/diagnosing-bugs
/implement-contract work/retry-safe-uploads-api.md
/review-implementation <saved implementation handoff> against <comparison base>
/prove <saved contract>; candidate <saved implementation handoff>
```

When proof finds a gap, insert the repair loop without blurring its roles:

```text
/prove <saved contract>; candidate <saved implementation handoff>
/repair-gaps <matching proof report>; candidate <saved implementation handoff>; requirements <IDs>
/prove <saved contract>; candidate <repaired candidate handoff>
/review-implementation <repaired candidate handoff> against <comparison base>
```

When GitHub Actions fails, repair that workflow and refresh any result that the
new commit invalidates:

```text
/fix-pr #456
/prove <saved contract>; candidate <repaired candidate handoff>
/review-implementation <repaired candidate handoff> against <comparison base>
```

Keep each result attached to the agreement and candidate it actually describes.
`implement-contract` builds the requested capability, `review-implementation` examines
it, and `/prove` establishes acceptance evidence. Repairs change the candidate
and require fresh results. None of these phases grants permission to merge.
