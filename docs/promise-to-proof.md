# How to take a ticket from promise to proof

A convincing implementation is not the same as a finished ticket. The code can
look right while one sentence from the issue never reaches a test. A test suite
can pass while its assertions miss the promised result. A green pull request can
hide a weakened check.

Use [Matt Pocock's skills](https://github.com/mattpocock/skills) to understand
the problem, write the specification, divide the work, implement it, and review
the result. Add the skills from this repository where the workflow needs a clear
acceptance contract or independent evidence. Together, the collections carry
the original agreement from the first design discussion through the final
GitHub Actions run.

The acceptance contract defines the spec envelope. Implementation fills it.
Proof establishes that one exact candidate satisfies one exact contract revision.

```text
source promise → acceptance contract vN → minimum complete implementation
               → fixed candidate → candidate-bound proof
```

The sequence is not a ceremony. Each skill answers a different question, and
you can omit a step when that question has a clear, low-risk answer.

## Install the skills

Install both collections before you start:

```bash
npx skills@latest add mattpocock/skills
npx skills@latest add grove/skills
```

When the first command asks which skills to install, include
`setup-matt-pocock-skills`. Run the setup once in each repository:

```text
/setup-matt-pocock-skills
```

Choose the issue tracker, triage labels, and documentation locations that the
project already uses. The setup gives Matt's planning and implementation skills
the same sources that `acceptance-contract` and `/prove` will read later.

To list the current skills from a clone, run:

```bash
rg --files skills -g SKILL.md | sort
```

The complete path looks like this:

```text
idea or problem
      |
      v
/grill-with-docs
      |
      +---- /wayfinder when one session cannot resolve the work
      |
      v
/to-spec -> /to-tickets
      |
      v
for each ticket
      |
      v
/acceptance-contract
      |
      v
/interrogate       optional when the design is already settled
      |
      v
/implement         uses /tdd and closes with /code-review
      |
      v
/prove
   |         |
   |         +---- PROVEN --------------------+
   |                                           |
   +---- NOT PROVEN                            |
             |                                 |
             v                                 |
       /repair-proof                           |
             |                                 |
             +----> fresh /prove, then review -+
                                                 |
                                                 v
                                           pull request
                                                 |
                                      CI red ----+---- CI green
                                         |                  |
                                         v                  v
                                      /fix-pr          current proof + review
                                         |                  |
                                         |                  v
                                         |             ready to merge
                                         |
                                         v
                              refresh stale proof or review
```

## Shape the work with Matt's planning skills

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

If the specification is too large for one ticket, divide it into complete
slices that can each deliver and verify useful behavior:

```text
/to-tickets #123
```

Use `/wayfinder` before `/to-spec` when the work is too large or uncertain for
one agent session. It records the decisions that block a reliable plan and
resolves them one at a time. When the issue already states a complete, agreed
outcome, skip these planning steps and begin with `acceptance-contract`.

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
design decision. `acceptance-contract` plans requirements and evidence, while
`prove` verifies an implementation against the agreed contract.

Critique is optional and advisory. It does not edit the artifact, repository,
or acceptance contract, publish findings, or begin implementation. No downstream
skill is required. You can take unresolved decisions into `interrogate`, plan
acceptance with `acceptance-contract`, or proceed directly when appropriate.

## Turn the ticket into an acceptance contract

Start with a GitHub issue, a specification, or an agreed outcome that states
what the change must accomplish. If the source only says "improve retries" or
"make uploads reliable," resolve that ambiguity before implementation. The
workflow cannot preserve a promise that nobody has made concrete.

Run `acceptance-contract` against the source:

```text
/acceptance-contract #124
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

Save the returned contract before handing the work to a fresh session. The
workflow invoking `acceptance-contract` owns this step under existing authority.
Follow the protocol's [durable handoff convention](./acceptance-contract-protocol.md#durable-contract-handoff):
attach the contract or its direct reference to the originating ticket. Without
a tracker, use `docs/acceptance-contracts/<work-id>.md` unless the repository
documents another location. Reread the saved contract and pass its location and
revision onward. Include local files in the commit or snapshot transferred to
another checkout. Report storage as pending when it cannot be completed.

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
them directly from it. Have `acceptance-contract` reconcile them before work
that depends on the changed promise. Use implementation authority
already present in the request. If the request covers design only, obtain
implementation authority before editing code.

Skip `interrogate` when the design is already clear and the cost of a wrong
choice is low. A one-line correction with an existing regression seam rarely
needs a separate design session. The acceptance contract still helps because
small diffs can omit behavior too.

## Implement with Matt's feedback loops

Pass the ticket and its acceptance contract into Matt's implementation workflow:

```text
/implement #124
```

Resolve the saved contract from the ticket reference or documented local path.
Reconcile pending amendments before implementing affected behavior. Map each
meaningful code path or check back to its requirement ID. `/implement` uses `/tdd`
at the agreed seams, so each vertical slice moves through a failing test, the
smallest working change, and a cleanup pass. TDD drives the next piece of code,
while the contract keeps every ticket promise in view. Use Matt's existing
planning, implementation, TDD, and review steps rather than creating a second
implementation workflow.

Build the smallest complete implementation within the specification. Include
necessary invariants, state transitions, failure handling, and persistence.
For the retry example, R4 requires durable retry state even if an in-memory fix
has a smaller diff. Omit speculative machinery that no promise requires.

For a difficult defect or performance regression, use `/diagnosing-bugs` to
build a reproduction, test hypotheses, and leave a regression check. Once the
cause is known, return to the same requirement IDs so the fix does not solve one
symptom while leaving the promised outcome unverified.

Matt's `/implement` closes with `/code-review`, which checks both repository
standards and fidelity to the source specification. Review both missing promised
behavior and unrequested scope. Finish the review and
commit the candidate before proof. A clean commit gives every later observation
one exact identity and avoids the awkward question of whether a file changed
halfway through verification.

Record that identity before you invoke proof:

```bash
git status --short
git rev-parse HEAD
```

If `git status --short` reports unrelated changes, separate or resolve them
before proof. `/prove` can use an exact snapshot when necessary, but a dirty or
changing worktree is `NOT PROVEN` unless the verifier can establish precisely
which files the observations cover.

## Prove the fixed candidate

Run `prove` only after the candidate and the contract revision are fixed:

```text
/prove #124
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
requirement IDs to `repair-proof`:

```text
/repair-proof #124
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
/prove #124
```

Repeat this pair only while proof identifies specific, repairable gaps:

```text
NOT PROVEN -> /repair-proof -> fresh /prove
```

Stop when the missing input is a product decision, unavailable credential, or
external capability. `repair-proof` must not guess its way through a stale or
ambiguous contract.

If the repair changes a diff that `/code-review` already checked, run the review
again after fresh proof succeeds:

```text
/code-review main
```

Proof checks whether the ticket's promises hold. Code review checks whether the
new diff follows project standards and still matches the specification. Keep
both results tied to the repaired candidate.

## Repair failed GitHub Actions without weakening the check

Open the pull request after the candidate is proven and reviewed according to
the repository's process. If a required GitHub Actions workflow fails, invoke
`fix-pr` with the pull request or the failed workflow run:

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
candidate needs fresh proof. Refresh code review when the repair changes the
reviewed diff.

## Choose the shortest workflow that covers the risk

For a straightforward ticket with a settled design, use the compact path:

```text
/acceptance-contract #124
/implement #124
/prove #124
open the pull request
```

For a feature that starts as an idea, use the full planning and delivery path:

```text
/grill-with-docs <idea>
/to-spec
/to-tickets #123

# For each ticket:
/acceptance-contract #124
/interrogate #124
/implement #124
/prove #124
open the pull request
```

For a difficult bug, replace the broad planning phase with a disciplined
diagnosis while keeping the acceptance and proof steps:

```text
/acceptance-contract #124
/diagnosing-bugs
/implement #124
/prove #124
```

When proof finds a gap, insert the repair loop without blurring its roles:

```text
/prove #124
/repair-proof #124
/prove #124
/code-review main  if the repair changed the reviewed diff
```

When GitHub Actions fails, repair that workflow and refresh any result that the
new commit invalidates:

```text
/fix-pr #456
/prove #124       full proof for every changed candidate
review again      if the reviewed diff changed materially
```

Use every step that closes a real uncertainty and omit the rest. The workflow
works because Matt's skills move the work from an idea to reviewed code, while
the skills in this repository keep the acceptance contract and evidence intact.
`acceptance-contract` defines the checks, `interrogate` tests the proposed design,
`/prove` verifies a fixed candidate, `repair-proof` changes only named gaps, and
`fix-pr` restores the pull request's required automation. None of those results
is a substitute for another.
