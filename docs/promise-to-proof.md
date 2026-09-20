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
the same sources that `acceptance-matrix` and `/prove` will read later.

The repository provides the five skills used below. To confirm the current set
from a clone, run:

```bash
find skills -name SKILL.md -print | sort
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
/acceptance-matrix
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
                                      /fix-pr          ready to merge
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
outcome, skip these planning steps and begin with `acceptance-matrix`.

## Turn the ticket into an acceptance contract

Start with a GitHub issue, a specification, or an agreed outcome that states
what the change must accomplish. If the source only says "improve retries" or
"make uploads reliable," resolve that ambiguity before implementation. The
workflow cannot preserve a promise that nobody has made concrete.

Run `acceptance-matrix` against the source:

```text
/acceptance-matrix #124
```

The skill separates the source into stable requirements that a real observation
can prove or disprove. It also records boundaries such as an empty collection, a
retry after restart, a different authorization level, or a partial failure when
the source or code path makes those cases relevant. Each row names one primary
form of evidence: a behavioral test through a public interface, an invariant
that prevents the counterexample, or an exact verification command.

Do not treat the new matrix as a test report. Its rows begin as `planned` or
`not proven` because `acceptance-matrix` designs the checks but does not run
them. That distinction matters. A thoughtful test name is still only a plan
until a fixed candidate produces the expected observation.

For a retry ticket, the useful result is a contract with separate promises such
as these:

```text
R1: A failed upload can be retried successfully.
R2: Retrying the same upload leaves exactly one stored upload.
R3: The retry preserves the original filename and metadata.
R4: The retry succeeds after the application reloads its state.
```

Keep those IDs and statements unchanged as work moves forward. If the product
decision changes, record the authorized change. Do not let an implementation
shortcut quietly rewrite the agreement.

## Challenge the design before code makes it expensive

When the implementation has a consequential choice, run `interrogate` after
the matrix and before editing code:

```text
/interrogate #124
```

Ask the agent to name the affected files, the proposed flow, the assumptions
that must remain true, and the evidence that will establish each requirement.
Then challenge the parts that would be painful to reverse. Persistence,
concurrency, authorization, migrations, caching, and cross-service changes
deserve more scrutiny than a local rename because a plausible design in those
areas can fail far from the edited line.

Use the conversation to reach a decision, not to generate an unlimited list of
possibilities. Once the plan survives the important objections, state the
chosen approach and any authorized requirement changes. Then authorize
implementation explicitly. Agreement with a design does not by itself grant
permission to edit the repository.

Skip `interrogate` when the design is already clear and the cost of a wrong
choice is low. A one-line correction with an existing regression seam rarely
needs a separate design session. The acceptance contract still helps because
small diffs can omit behavior too.

## Implement with Matt's feedback loops

Pass the ticket and its acceptance matrix into Matt's implementation workflow:

```text
/implement #124
```

Keep the matrix beside the work and map each meaningful code path or check back
to its requirement ID. `/implement` uses `/tdd` at the agreed seams, so each
vertical slice moves through a failing test, the smallest working change, and a
cleanup pass. The matrix and TDD answer different questions. TDD drives the next
piece of code, while the matrix keeps every ticket promise in view.

For a difficult defect or performance regression, use `/diagnosing-bugs` to
build a reproduction, test hypotheses, and leave a regression check. Once the
cause is known, return to the same requirement IDs so the fix does not solve one
symptom while leaving the promised outcome unverified.

Matt's `/implement` closes with `/code-review`, which checks both repository
standards and fidelity to the source specification. Finish the review and
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

Run `prove` only after the candidate and the contract are fixed:

```text
/prove #124
```

The skill starts from the source promises instead of the implementation. For
every requirement, it identifies an observation and an independent oracle that
decides whether the result is correct. It also searches for realistic
counterexamples at state transitions, retries, restarts, authorization
boundaries, concurrency windows, and the final workflow outcome when those
cases apply.

Do not ask `/prove` to fix what it finds. Proof must leave both the candidate
and the contract unchanged so that every observation still belongs to the same
code. If a file changes during the run, the old observations no longer support
the new candidate. The correct verdict is `NOT PROVEN`, followed by a separate
repair and a fresh proof.

Read the verdict literally:

```text
PROVEN
Every material requirement has credible evidence for the fixed candidate.

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

Authorize the edit only after the proof result, the contract, and the candidate
still match. The skill changes the smallest amount of implementation or evidence
needed for the named IDs, runs a focused check, and reports the candidate before
and after the repair. It leaves unrelated gaps alone and preserves every valid
check that already exists.

Expect `REPAIRED`, `NO CHANGE`, or `BLOCKED`, never `PROVEN`. A passing focused
check shows that the repair is worth testing again, but it does not re-evaluate
the other requirements against the changed candidate. Run proof again:

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
checks passed without showing that every ticket promise was checked. If
`fix-pr` changes product behavior or acceptance evidence, run `/prove` again on
the repaired commit. Refresh the repository's code review when the repair makes
the previous review stale.

## Choose the shortest workflow that covers the risk

For a straightforward ticket with a settled design, use the compact path:

```text
/acceptance-matrix #124
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
/acceptance-matrix #124
/interrogate #124
/implement #124
/prove #124
open the pull request
```

For a difficult bug, replace the broad planning phase with a disciplined
diagnosis while keeping the acceptance and proof steps:

```text
/acceptance-matrix #124
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
/prove #124       if product behavior or acceptance evidence changed
review again      if the reviewed diff changed materially
```

Use every step that closes a real uncertainty and omit the rest. The workflow
works because Matt's skills move the work from an idea to reviewed code, while
the skills in this repository keep the acceptance contract and evidence intact.
`acceptance-matrix` defines the checks, `interrogate` tests the proposed design,
`/prove` verifies a fixed candidate, `repair-proof` changes only named gaps, and
`fix-pr` restores the pull request's required automation. None of those results
is a substitute for another.
