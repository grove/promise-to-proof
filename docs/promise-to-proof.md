# How to take a ticket from promise to proof

For a shorter set of task recipes, start with the [HOW-TO](./how-to.md).
The [FAQ](./faq.md) answers common questions about issue creation, slicing,
review, and proof. This guide gives the detailed path and examples.

A convincing implementation is not the same as a finished ticket. The code can
look right while one sentence from the issue never reaches a test. A test suite
can pass while its assertions miss the promised result. A green pull request can
hide a weakened check.

Use Promise to Proof's native skills to plan acceptance, implement the agreed capability,
review a captured candidate, and prove the result. Optional external planning and TDD
tools can help, but the delivery path works without them.

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

## Install the skills

Install the skills:

```bash
npx skills@latest add grove/promise-to-proof
```

Use the repository's existing issue-tracker and domain-document configuration.
A local specification and saved contract do not require an external setup skill.
If you want external planning or TDD tools, install that collection separately:

```bash
npx skills@latest add mattpocock/skills
```

The collection's optional setup skill configures its tools for your repository.
Keep the issue tracker, triage labels, and documentation locations consistent
with the sources it reads.

To list the current skills from a clone, run:

```bash
rg --files skills -g SKILL.md | sort
```

The delivery path uses explicit phases:

```text
/plan-acceptance       -> propose the contract
/audit-acceptance      -> optionally check the exact proposal before approval
/implement-contract    -> save the report and capture the candidate
/review-implementation -> save findings for that candidate and comparison base
/prove                 -> save the proof and requirement evidence
/publish-pr            -> preview or publish the exact candidate as a draft PR
```

Review and proof may run in either order against the same fixed candidate.
A handoff does not invoke the next skill. The enclosing authorized workflow owns
invocation and any publishing. Neither review nor proof needs an open PR or
unrelated green CI. Merge requires current proof, green required checks for the
final candidate, and the repository's review requirements.

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
remain valid inputs. For a local spec in this repository that needs one
originating issue, use `/create-parent-issue`; `/to-tickets` is not the parent
issue creation path. To divide an agreed parent contract, use the optional
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
/plan-acceptance #124
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

After any required approval, save the returned contract before handing the work
to a fresh session. The workflow invoking `plan-acceptance` owns this step under
existing authority.
Follow the protocol's [durable handoff convention](./acceptance-contract-protocol.md#durable-contract-handoff):
attach the contract or its direct reference to the originating ticket. Without
a tracker, use `docs/acceptance-contracts/<work-id>.md` unless the repository
documents another location. Reread the saved contract and pass its location and
revision onward. Include local files in the commit or snapshot transferred to
another checkout. Report storage as pending when it cannot be completed.

## Divide large work without changing the agreement

Keep a small, coherent task on the direct acceptance, implementation, review,
and proof path. For larger work, save the parent contract first, then request a
draft decomposition:

```text
/slice-contract #123; draft only
```

The skill inspects the source, exact parent revision, existing work, and relevant
implementation. It proposes the fewest useful outcomes, maps every parent promise
to a contribution and completion check, and records genuine prerequisites.
`NO SPLIT` means separate tickets add no useful boundary. A missing parent contract
returns to `plan-acceptance`; slicing cannot invent its requirements or revision.

Review the ticket outcomes, coverage map, dependency order, parent completion plan,
labels, destination, and intended links. Approve consequential exceptions, such
as batches that need a shared integration candidate. Resolve outcome-changing
unknowns before dependent publication. A missing test with a clear outcome can
instead become assigned evidence work.

Invocation alone permits inspection and a draft. Authorize local plan storage
separately when needed. Publication requires approval of the breakdown and
authority for the named destination and changes. You can give both together:

```text
/slice-contract #123; publish the approved breakdown as GitHub issues
```

The skill retains prior authority for an unchanged approved plan. A materially
changed allocation, destination, dependency, or exception needs approval unless
already delegated. Publication covers the approved tickets, planning metadata,
and necessary links. It does not grant contract edits, assignments, issue closure,
commits, pushes, or implementation authority.

Use the configured tracker and local paths. If you explicitly choose local tickets
and no layout exists, the default is `.scratch/<work-id>/plan.md` with one child
file under `.scratch/<work-id>/issues/`. Transfer those artifacts and the parent
snapshot to the next checkout. Saving files does not authorize a commit.

After publication, reopen the canonical index, tickets, and relationships.
`PUBLISHED` means the intended artifacts and required links were saved and reread.
`PARTIAL` records successful, pending, and uncertain operations. `BLOCKED` identifies
an input, decision, permission, or capability that prevents safe progress.
A draft remains `DRAFT`; a chat draft alone is not a saved handoff.

To resume, pass the parent or saved plan back to `slice-contract`. The skill uses
stable slice IDs and actual ticket references, including closed tickets, to
reconcile work. After a lost response, confirm remote state before retrying.
Preserve successful writes and human edits. If the parent or an active child
changed, reconcile affected writes before continuing. A disclosed text-link
fallback can replace unavailable native relationships only when repository
requirements allow it. Otherwise publication remains incomplete.

For each child, explicitly run acceptance planning:

```text
/plan-acceptance <child-reference>
```

The child retains the exact parent reference and applicable constraints. Its
local requirement IDs map through `Source` to qualified parent obligations,
such as `grove/project#123 v2:R4`. Slice IDs such as `S1` are planning identities.
A child contract covers its own contribution without requiring unrelated sibling
functionality. Missing contracts and prerequisites prevent unattended implementation
readiness even after successful publication.

Continue with the chosen implementation, review, and proof workflows. Missing
companion skills do not block slicing; their next steps remain explicit handoffs.
Finally, invoke `/prove` on the full parent contract against one integrated
candidate, including interactions between children. Allocate actual integration
code and checks to a ticket when needed. Ordinary parent proof needs no separate
integration ticket. If the integrated candidate differs from the reviewed child
candidates or contains shared integration code, review that candidate too. Closed
children and proofs on earlier candidates cannot replace this parent evaluation or
the applicable review and merge gates.

## Challenge the design before code makes it expensive

When the implementation has a consequential choice, run `interrogate` after
the contract and before editing code:

```text
/interrogate #124
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
/implement-contract #124
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

Save the implementation report at the supplied or documented destination.
Without one, propose a destination outside the candidate and mark storage pending
until the authorized workflow saves and rereads it. Preserve the canonical
contract location, semantic revision, and exact text through an immutable
reference or retrievable captured text with a digest.

Capture the candidate as a full commit SHA or reproducible snapshot, including
relevant uncommitted and untracked content. A commit is optional. Preserve existing
work and include only the agreed candidate scope. Record the comparison base
when known, or leave it explicitly unresolved for the next phase.

Pass the saved implementation handoff to review, proof, and repair. An issue
number alone does not identify a candidate. For a committed candidate, pass the
full SHA. For uncommitted work, pass the reproducible snapshot and its included
files. Pass the matching proof report and unresolved requirement IDs to
`repair-gaps`.

When another session uses another checkout, transfer recoverable content as well
as its identity. A hash without content, or a local path left behind in a previous
session, does not complete the handoff. Transfer source and contract files too.

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

Save and reread the review report outside the candidate under the same report
storage convention. Preserve finding IDs, affected requirement IDs, candidate
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
requirement rows and save it outside the candidate. One report can cover many rows.

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
workspace, verifies its complete tree against the captured candidate, pushes
without force, creates one draft pull request, and rereads the remote state.

A content-equivalent commit preserves the candidate-bound reports because the
skill records the exact mapping. A mismatch blocks publication rather than
silently adopting new bytes. `PUBLISHED` still leaves CI, repository approval,
and merge policy to `/merge-readiness`.

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

## Choose the shortest workflow that covers the risk

For a straightforward ticket with a settled design, use the compact path:

```text
/plan-acceptance #124
# Optionally audit the exact proposal before any required approval and saving.
/audit-acceptance <exact proposed contract> against <source>
/implement-contract #124
/review-implementation <saved implementation handoff> against <comparison base>
/prove <saved contract>; candidate <saved implementation handoff>
/publish-pr <saved candidate and reports>; target <branch>; draft only
# Approve the exact publication preview.
/publish-pr <approved preview>; publish the draft PR
```

For a feature that starts as an idea, optionally add external planning tools:

```text
/grill-with-docs <idea>
/to-spec
/plan-acceptance #123
/slice-contract #123; draft only
# Approve the breakdown and authorize publication.
/slice-contract #123; publish the approved breakdown

# For each child ticket:
/plan-acceptance #124
/interrogate #124
/implement-contract #124
/review-implementation <saved child handoff> against <child comparison base>
/prove <saved child contract>; candidate <saved child handoff>
/publish-pr <saved child candidate and reports>; target <branch>; draft only
# Approve and publish the exact preview when a child PR is required.

# On the final integrated candidate:
/review-implementation <saved integrated handoff> against <parent comparison base>
/prove <saved parent contract>; candidate <saved integrated handoff>
# Apply the repository review and merge gates.
```

For a difficult bug, optionally use an external `diagnosing-bugs` skill before implementation:

```text
/plan-acceptance #124
/diagnosing-bugs
/implement-contract #124
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
