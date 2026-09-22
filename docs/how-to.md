# How to deliver a change with Grove

Start here when you have a change to deliver. Pick the path that matches your
source, save each result, and give the next skill the saved result rather than a
summary from chat. The [detailed workflow](./promise-to-proof.md) explains each
phase in depth. The [FAQ](./faq.md) answers questions about what the results mean.

## Choose a starting point

If you have a small, coherent GitHub issue, follow [the direct path](#complete-a-github-issue).
If the issue needs several independently useful outcomes, plan its parent contract
first and then [divide the work](#divide-a-large-issue). You can give
`plan-acceptance` a local specification or an agreed outcome too. A GitHub issue
is not a prerequisite for those inputs, though this repository records its own
issues and specifications in GitHub Issues.

```text
Existing, coherent issue  → plan-acceptance → implement-contract → review and prove
Existing, large issue     → plan-acceptance → slice-contract → child workflows
Local specification       → plan-acceptance → direct path or approved slicing
```

If your source is still an idea, settle the outcome before planning acceptance.
Use `interrogate` when you want to question a proposed approach, or request
`critique` when you want an independent assessment. Neither skill creates a
ticket or an acceptance contract.

## Complete a GitHub issue

Run these commands as separate invocations. Each skill returns a handoff for the
next phase; it does not call the next skill for you.

```text
/plan-acceptance #123
/implement-contract #123
/review-implementation <saved implementation handoff> against <comparison base>
/prove <saved contract>; candidate <saved implementation handoff>
```

After `plan-acceptance`, save and reread the acceptance contract at its canonical
location. Pass its location, revision, and exact text identity to implementation.
After `implement-contract`, save the report and capture the candidate as a full
commit SHA or a reproducible snapshot that includes relevant uncommitted files.
Give review a fixed comparison base. Save the review and proof reports outside
the candidate, with the identities and evidence needed to read them in another
session. The [durable handoff rules](./acceptance-contract-protocol.md#durable-contract-handoff)
give the storage convention.

You can run review and proof in either order against the same fixed candidate.
Review examines the implementation's fidelity, scope, and engineering. Proof
checks every promised outcome against observed evidence. A `REVIEWED` result
does not stand in for `PROVEN`, and neither result replaces required CI or the
repository's review gate.

## Divide a large issue

Save the parent contract before asking for a split. A draft shows the proposed
child outcomes, coverage of each parent promise, dependencies, and the plan for
checking the integrated result.

```text
/plan-acceptance #123
/slice-contract #123; draft only
```

Review the draft's coverage, destination, labels, links, and any exception for
work that cannot be independently green. Approve a consequential breakdown and
authorize its publication to the named destination before publishing it. If
separate tickets add no useful boundary, keep the direct path when the result is
`NO SPLIT`.

```text
/slice-contract #123; publish the approved breakdown as GitHub issues
/plan-acceptance <each published child issue>
```

Each child receives its own saved contract before implementation. Run the direct
implementation, review, and proof path for each child, then assemble the work in
one exact integrated candidate. Run `/prove` against the full parent contract on
that candidate. Review the integrated candidate if it differs from the reviewed
child candidates or contains shared integration code. Child proofs do not combine
into parent proof.

## Create an originating issue when you need one

For work **in this repository**, create the source GitHub issue with
`gh issue create` before starting the tracked workflow. Put the agreed outcome and
boundaries in that issue; `plan-acceptance` turns them into a contract. Keep the
contract on the originating issue or link it directly from that issue. Do not
create a second issue merely to store the contract.

For a project using Grove's skills, follow that project's issue-tracker rules.
`plan-acceptance` also accepts a specification path or agreed outcome, so a local
specification can remain the source when no tracker issue is required. If you
later publish a decomposition from a local source, `slice-contract` may create
approved child issues. Creating a tracker parent for that source needs explicit
approval; slicing does not create it by default. The [publication procedure](../skills/productivity/slice-contract/references/publication.md#save-tickets-and-relationships)
defines how to keep the source, parent index, and children linked.

## Fix a review finding

When review returns `CHANGES NEEDED`, save its report and pass the supported
finding IDs to a new `implement-contract` invocation. Keep the original contract
unless the finding exposes a changed promise or consequential design decision.

```text
/implement-contract <saved implementation handoff>; findings <review finding IDs>
/review-implementation <new candidate handoff> against <comparison base>
/prove <saved contract>; candidate <new candidate handoff>
```

Refresh review after the candidate changes. If proof already ran, refresh full
proof too. A review finding by itself is not input to `repair-gaps`; that skill
needs a matching `NOT PROVEN` proof report.

## Repair a failed proof

Read the `NOT PROVEN` report before choosing a repair. If it names repairable
implementation or evidence gaps, pass the matching report, exact candidate, and
unresolved requirement IDs to `repair-gaps`. Keep a contract decision, missing
authorization, or uncertain candidate identity out of this repair path; resolve
that input first.

```text
/repair-gaps <matching proof report>; candidate <saved candidate handoff>; requirements <IDs>
/prove <saved contract>; candidate <repaired candidate handoff>
/review-implementation <repaired candidate handoff> against <comparison base>
```

Run proof against every contract row after a candidate change, including rows
that the earlier proof marked `proven`. Refresh review for the changed candidate
as well. The focused check in a repair report helps you decide whether to rerun
proof; it does not itself establish acceptance.

## Reconcile a changed requirement

When implementation, review, or proof finds that the agreed promise must change,
record the proposed amendment with its affected requirement IDs and source
authorization. Return to `plan-acceptance` before dependent work continues.
Save and reread the new contract revision, then give subsequent skills that exact
revision and text. Do not edit a requirement to match behavior that happens to
be implemented.

## Repair failing CI

For a failed pull request workflow, invoke the CI repair skill with the pull
request or failed run. `fix-pr` addresses the workflow failure and reports
`FIXED` or `NOT FIXED`; it does not prove the ticket's promises.

```text
/fix-pr #456
```

If CI repair changes the candidate, run full proof and refresh review against
the repaired candidate. Before merge, confirm that the pull request head matches
the candidate described by the current reports. Required checks and repository
review requirements still apply after proof succeeds.

## Carry work to another session or checkout

Transfer the canonical contract location, revision, and exact text or retrievable
snapshot. Transfer the saved implementation report, a full candidate commit SHA
or reproducible snapshot, and the comparison base used for review. Include the
saved review and proof reports with their evidence. For sliced work, include the
parent contract snapshot, decomposition, child contributions, and prerequisites.

A path available only in the old checkout or a digest without recoverable
content cannot restore the handoff. If storage is pending, say so and save and
reread the artifact before asking another session to use it. The
[candidate and report rules](./acceptance-contract-protocol.md#implementation-and-review-handoffs)
describe the required identities.

## Pick a command

| Command | Use it to |
|---|---|
| `/plan-acceptance` | Define and revise the acceptance contract. |
| `/slice-contract` | Draft a breakdown and publish approved child tickets. |
| `/implement-contract` | Build the agreed scope or correct review findings. |
| `/review-implementation` | Inspect a fixed candidate against a comparison base. |
| `/prove` | Check every contract promise on one exact candidate. |
| `/repair-gaps` | Repair named gaps in a matching `NOT PROVEN` report. |
| `/fix-pr` | Repair a failed pull request workflow. |
| `/interrogate` | Question the agent's proposal and reasoning. |
| `/critique` | Request an independent assessment of a proposal. |

For the precise rules behind each handoff, read the
[acceptance contract protocol](./acceptance-contract-protocol.md).
