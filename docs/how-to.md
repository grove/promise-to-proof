# How to deliver a change with Promise to Proof

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
Existing, coherent issue  → plan-acceptance → optional audit-acceptance
						  → implement-contract → review and prove → optional publish-pr
Existing, large issue     → plan-acceptance → slice-contract → child workflows
Local spec in this repo   → create-parent-issue → plan-acceptance → direct or sliced path
Other project's local spec → plan-acceptance → direct path or approved slicing
```

If your source is still an idea, settle the outcome before planning acceptance.
Use `interrogate` when you want to question a proposed approach, or request
`critique` when you want an independent assessment. Neither skill creates a
ticket or an acceptance contract.

For an existing issue that still needs a next action or owner, start with
[triage](#triage-an-existing-issue).

## Choose a model

The skills do not prescribe models or minimum parameter counts. This ranking
estimates the reasoning needed for a typical full-scope run, from hardest to
easiest. A narrow task may need less; a large or ambiguous one may need more.

| Rank | Skill | Suggested capability | What makes it demanding |
|---:|---|---|---|
| 1 | [`slice-contract`](../skills/productivity/slice-contract/SKILL.md) | Strongest | Allocate every parent promise across useful child outcomes and dependencies. |
| 2 | [`implement-contract`](../skills/productivity/implement-contract/SKILL.md) | Strongest | Deliver complete behavior and meaningful checks within the agreed scope. |
| 3 | [`review-implementation`](../skills/productivity/review-implementation/SKILL.md) | Strongest | Judge contract fidelity, scope, and engineering quality independently. |
| 4 | [`fix-pr`](../skills/productivity/fix-pr/SKILL.md) | Strongest | Diagnose causal CI failures and verify a repair without weakening checks. |
| 5 | [`critique`](../skills/productivity/critique/SKILL.md) | Strongest | Test a proposal against its goal, alternatives, and uncertain evidence. |
| 6 | [`prove`](../skills/productivity/prove/SKILL.md) | Capable | Establish each promise on one fixed candidate using independent evidence. |
| 7 | [`plan-acceptance`](../skills/productivity/plan-acceptance/SKILL.md) | Capable | Extract stable, testable promises and credible evidence plans from the source. |
| 8 | [`audit-acceptance`](../skills/productivity/audit-acceptance/SKILL.md) | Capable | Detect missing promises, scope drift, and evidence plans that cannot prove outcomes. |
| 9 | [`publish-pr`](../skills/productivity/publish-pr/SKILL.md) | Capable | Preserve exact candidate bytes and authorization across publication steps. |
| 10 | [`repair-gaps`](../skills/productivity/repair-gaps/SKILL.md) | Capable | Make a complete repair for named proof gaps without changing the agreement. |
| 11 | [`merge-readiness`](../skills/productivity/merge-readiness/SKILL.md) | Mid-tier | Match the current PR to proof, review, CI, and repository approval rules. |
| 12 | [`interrogate`](../skills/productivity/interrogate/SKILL.md) | Mid-tier | Answer challenges with evidence and revise a proposal when warranted. |
| 13 | [`triage-issue`](../skills/productivity/triage-issue/SKILL.md) | Mid-tier | Choose a defensible next action from the issue and its prerequisites. |
| 14 | [`create-parent-issue`](../skills/productivity/create-parent-issue/SKILL.md) | Mid-tier | Summarize a spec faithfully and check its exact source before publication. |

Use a strong long-context model for the first five, especially on unfamiliar
codebases or large contracts. The lower ranks still need the right tools and
permissions: model capability cannot replace access to source issues, tests,
CI results, or an exact candidate. `publish-pr` in particular has a demanding
identity and authorization procedure even though its reasoning is more bounded.

## Triage an existing issue

When an issue needs a next owner or action, run triage before the delivery path:

```text
/triage-issue #123
```

The default result is a recommendation, not a tracker update. It shows the
issue's state, evidence and open questions, one next action, and a preview of
any label or state change. Check the proposed role against the repository's
[triage labels](./agents/triage-labels.md). Missing reporter facts lead to a
specific question (`needs-info`); a maintainer decision or investigation stays
`needs-triage`. A saved, retrievable contract, required approvals, and confirmed
prerequisite outcomes are needed before recommending `ready-for-agent`. Work
that needs human access or judgment goes to `ready-for-human`.

To apply the preview, explicitly approve the label change for that issue. To
decline and close an issue, a maintainer must decide to decline; approve the
`wontfix` label and closure separately, including any closing comment. Triage
preserves unrelated labels and rereads the issue before and after an approved
change. If the issue changed after the preview, review a new recommendation
before approving it. An uncertain write is reported as `PARTIAL`, not retried
automatically.

An unchanged or unapproved recommendation is `DRAFT`; a confirmed update is
`APPLIED`. If the issue or tracker cannot be resolved, the result is `BLOCKED`.

If the issue is clear but has no saved acceptance contract, the next action is
`/plan-acceptance #123`. Save and reread that contract before considering the
issue ready for implementation. Triage does not create a contract or implement
the request.

## Complete a GitHub issue

Run these commands as separate invocations. Each skill returns a handoff for the
next phase; it does not call the next skill for you.

```text
/plan-acceptance #123
/implement-contract #123
/review-implementation <saved implementation handoff> against <comparison base>
/prove <saved contract>; candidate <saved implementation handoff>
```

After `plan-acceptance`, optionally run
`/audit-acceptance <exact proposed contract> against <source>` before any
required approval.
The audit checks source coverage, scope, stable requirements, and evidence plans
without changing or approving the proposal. Return `CHANGES_NEEDED` findings to
`plan-acceptance`; resolve a `BLOCKED` decision or identity before continuing.

After any required approval, save and reread the acceptance contract at its
canonical location. Pass its location, revision, and exact text identity to implementation.
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

For a reproducible snapshot, you can normalize matching full reports into an
[acceptance bundle](./acceptance-bundle-v1.md) and inspect it without a model:

```bash
python3 checks/verify_acceptance_bundle.py path/to/bundle.json
```

The bundle is derived from the canonical contract and retained reports. A valid
bundle checks identity, coverage, evidence resolution, and decision consistency;
it does not replace the reports or judge whether the evidence proves the promise.

To publish that exact reviewed and proven candidate, first inspect a read-only
preview, then explicitly authorize its complete effects:

```text
/publish-pr <saved candidate, review, and proof handoff>; target <branch>; draft only
/publish-pr <approved exact preview>; publish the draft PR
```

The skill uses a matching commit or creates one in an isolated publication
workspace, verifies that its complete tree preserves the candidate content,
requires the target tip to match the review comparison base, pushes without
force, and rereads the draft PR. It does not change the candidate or assess merge
readiness. The model may prepare the read-only preview on its own; publication
effects still require exact authorization.

After the PR is confirmed, invoke `/merge-readiness <PR URL>` with the saved
review and proof reports near the merge decision. It checks that the PR's current
candidate has matching evidence, required CI, and repository approval and merge
conditions. It reports blockers without merging or replacing the repository's
approval process. Changes after the check require a new readiness assessment.

## Learn from an accepted delivery (optional)

After a full `PROVEN` result, use [`/retrospect`](../skills/productivity/retrospect/SKILL.md)
with the saved proof, exact candidate and contract references, and retrievable
use or maintenance observations. A matching review is useful when available,
but no PR or green unrelated CI is required. The skill proposes an evaluation
report outside the evaluated candidate; give it an authorized destination and
reread it from a fresh session. No learning is a valid outcome.

```text
/retrospect <saved PROVEN proof>; candidate <exact proven candidate>; experience <retrievable observations>
```

Review each suggested learning and explicitly authorize the exact disposition:
accept, reject, or rewrite then accept. Accepted advice goes in one project-local
register (by default `docs/retrospective-learnings.md`), created on the first
authorized acceptance. Future `/plan-acceptance` runs consider relevant active
advice and cite what they used; the current source still determines the contract.
Promoting advice to a binding rule is a separate human-authorized change through
the source's owning workflow. If a later candidate is evaluated retrospectively,
it needs its own proof and evaluation; an old report stays historical.

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

For work **in this repository** that starts from a local specification, use
`create-parent-issue` to draft exactly one originating GitHub issue. Review its
summary and durable spec reference, then explicitly authorize publication. The
skill does not split the specification into tickets or write the acceptance
contract.

```text
/create-parent-issue path/to/spec.md; draft only
/create-parent-issue path/to/spec.md; publish the approved single issue to GitHub
/plan-acceptance #123
```

The spec must be retrievable from an immutable reference, such as a
commit-pinned GitHub file URL. The skill will not commit or push it for you.
`plan-acceptance` turns the issue and exact source spec into the contract. Keep
that contract on the originating issue or link it directly from the issue; do
not create a second issue merely to store it.

When the source spec changes, use the same path and destination. The skill finds
the existing issue and previews an update; approve that update separately from
the original publication. It preserves the issue's contract or contract link
and unrelated labels. If the source promises changed, run `plan-acceptance` on
the same issue to reconcile its contract before continuing. An uncertain match
or a change detected before editing stops the update for another review.

For a small agreed outcome without a local spec, create one source issue with
`gh issue create` before starting the tracked workflow. Put the outcome and
boundaries in the issue, then run `plan-acceptance` on it.

```bash
gh issue create --title "Retry failed uploads" --body "Users can retry a failed upload after restarting the app."
```

For a project using Promise to Proof, follow that project's issue-tracker rules.
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

After any candidate change, run `/prove` against every contract row, including
rows previously marked `proven`. Focused checks can show whether the repair is
promising; they never replace that full proof. Refresh review for the changed
candidate as well.

## Reconcile a changed requirement

When implementation, review, or proof reveals that the agreement must change,
pause work that depends on it. Do not edit a requirement to match behavior that
happens to be implemented. Record the proposal on the originating issue (or in
the source specification), or link it directly from there. For example:

```text
Proposed amendment to v1:R2
Previous agreement: One retry is allowed after a failed upload.
Proposed agreement: Two retries are allowed after a failed upload.
Reason: The agreed recovery flow needs a second attempt.
Authorization: Pending owner decision.
```

Name every affected requirement ID, the old and proposed agreement, the reason
for the change, and who authorized it. If authorization is pending, keep the
proposal visible but do not proceed with work that depends on it. Once the
owner approves the change, record that decision on the source and run
`/plan-acceptance #123` on the same source. Only `plan-acceptance` revises the
contract; a comment proposing or approving a change is not itself the new
contract.

Save and reread the returned contract at its canonical location. A material
change increments the revision (for example, v1 to v2) and keeps v1 available
as history. A new test path, more evidence, or clearer wording with the same
meaning does not increment it. If the issue points to a specific older revision,
update its current-contract link to the newly saved revision; if it points to a
stable location, confirm that the location now resolves to the new text. Keep
older revisions retrievable, and reread the issue link before handing off the
current location, revision, and exact text. A changed promise needs fresh proof
against the new contract and an exact candidate.

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
| `/setup-promise-to-proof` | Configure GitHub issue, triage-label, and domain-doc pointers for a new project before tracker-writing or triage work. |
| `/create-parent-issue` | Draft one source issue from a local spec in this repository; publish only after explicit approval. |
| `/triage-issue` | Recommend the next action for an existing issue; apply only approved label or closure changes. |
| `/plan-acceptance` | Define and revise the acceptance contract. |
| `/audit-acceptance` | Independently audit an exact proposed contract before human approval. |
| `/slice-contract` | Draft a breakdown and publish approved child tickets. |
| `/implement-contract` | Build the agreed scope or correct review findings. |
| `/review-implementation` | Inspect a fixed candidate against a comparison base. |
| `/prove` | Check every contract promise on one exact candidate. |
| `/repair-gaps` | Repair named gaps in a matching `NOT PROVEN` report. |
| `/publish-pr` | Preview or explicitly publish an exact reviewed and proven candidate as a draft PR. |
| `/merge-readiness` | Check current PR evidence, required CI, approvals, and merge conditions without merging. |
| `/fix-pr` | Repair a failed pull request workflow. |
| `/interrogate` | Question the agent's proposal and reasoning. |
| `/critique` | Request an independent assessment of a proposal. |

For the precise rules behind each handoff, read the
[acceptance contract protocol](./acceptance-contract-protocol.md).
