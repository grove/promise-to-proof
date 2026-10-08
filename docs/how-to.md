# How to deliver a change with Promise to Proof

New to Promise to Proof? Start with [Getting Started](./getting-started.md) first. It walks through one small delivery from an agreed outcome to `REVIEWED + PROVEN`, so the recipes below have something concrete to build on.

Start here when you have a change to deliver. Pick the path that matches your
source, save each result, and give the next skill the saved result rather than a
summary from chat. The [detailed workflow](./promise-to-proof.md) explains each
phase in depth. The [FAQ](./faq.md) answers questions about what the results mean.

## Choose a starting point

Run `/setup-promise-to-proof` in a new project. It creates `.p2p/work/` and
`.p2p/tmp/` and checks Git ignore rules. It does not create `specs/` or `work/`;
projects may use them for their own files. Generated contracts and all `.p2p/**`
state stay out of project Git history. Tracker configuration is optional.

For a new change, run `/plan-acceptance <source>`; it saves the contract under
`.p2p/work/<slug>/contract.md`. A source file may be in `specs/`, `work/`, or
another project path. Follow the saved delivery-shape recommendation instead of
choosing a route in advance. An agreed outcome can also go directly into a
standalone work item without a spec.
After acceptance planning, P2P recommends either direct delivery or sizing
inspection; you do not need to choose first. A direct recommendation proceeds
through `/deliver-issue`, which applies the existing #60 admission before
implementation. For broad or materially uncertain boundaries, run
`/slice-contract`; `NO SPLIT` means the parent remains one delivery unit and
continues through the direct path.

```text
Local work item → deliver-issue → optional separately authorized publish-pr
Local spec      → plan-acceptance → direct delivery or slice-contract
Tracker issue   → import into .p2p/work/<slug>/contract.md → same local workflow
```

## Re-size from delivery evidence

A delivery may expose a useful boundary that was not visible during planning.
Ask `/slice-contract` to inspect the current tree only when concrete output
shows a separable complete contribution or a materially safer compatibility,
ownership, recovery, or verification boundary. The report must explain how the
boundary reduces delivery work and cite the exact candidate and retained
evidence. Difficulty, elapsed time, failing tests, review/proof defects,
repair exhaustion, and diff or requirement counts alone stay on the existing
implementation or repair path; hard but indivisible work remains one leaf.

Re-sizing preserves the old contract, candidate, reports, human edits, and
history. It changes only the smallest affected subtree after the required
allocation approval. Unaffected siblings and completed work remain stable;
code and pull requests are not moved automatically. A leaf converted to a
parent waits for its descendants, then receives full parent review and proof
on one assembled candidate. Child proofs never add up to parent acceptance.
Each delivery or ancestor handoff returns one next leaf, unresolved decision,
prerequisite, blocker, or parent-verification action from the current tree.

The coordinated path needs separate stage invocations and independent review
and proof contexts. Use the [manual stages](#complete-a-local-work-item) if the
host cannot provide them. Settle unclear outcomes with `interrogate` or an
explicit `critique` before planning. For optional tracker triage, use the next
procedure.

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
| 8 | [`retrospect`](../skills/productivity/retrospect/SKILL.md) | Capable | Separate observed experience from predictions and scope advice to evidence. |
| 9 | [`audit-acceptance`](../skills/productivity/audit-acceptance/SKILL.md) | Capable | Detect missing promises, scope drift, and evidence plans that cannot prove outcomes. |
| 10 | [`publish-pr`](../skills/productivity/publish-pr/SKILL.md) | Capable | Preserve exact candidate bytes and authorization across publication steps. |
| 11 | [`repair-gaps`](../skills/productivity/repair-gaps/SKILL.md) | Capable | Make a complete repair for named proof gaps without changing the agreement. |
| 12 | [`merge-readiness`](../skills/productivity/merge-readiness/SKILL.md) | Mid-tier | Match the current PR to proof, review, CI, and repository approval rules. |
| 13 | [`interrogate`](../skills/productivity/interrogate/SKILL.md) | Mid-tier | Answer challenges with evidence and revise a proposal when warranted. |
| 14 | [`triage-issue`](../skills/productivity/triage-issue/SKILL.md) | Mid-tier | Choose a defensible next action from the issue and its prerequisites. |
| 15 | [`create-parent-issue`](../skills/productivity/create-parent-issue/SKILL.md) | Mid-tier | Summarize a spec faithfully and check its exact source before publication. |

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

## Plan on an issue before delivery

Run `/plan-acceptance <issue>` to save a local proposal and post its exact text
on the existing issue for review. This direct invocation authorizes the proposal
comment; add `local-only` or `draft-only` to keep it local. The comment includes
the intended work path, revision, text hash, and retrievable binding inputs.
Approve the specific proposal on the issue, identifying its comment and hash.
If you approve only in conversation, transfer the saved approval receipt to the
delivery checkout as well.

Later, in the same or another checkout, run `/deliver-issue <issue>`. Delivery
imports the approved text into `.p2p/work/<slug>/contract.md` and retains its approval when
the text and binding inputs match. Changed or conflicting agreements require
reconciliation. The local contract stays in ignored `.p2p/` during active work;
a durable Delivery Record preserves completed issue-backed agreement identity.
No preliminary planning PR is needed.

Calling `deliver-issue` directly still plans locally as part of delivery. Its
nested planning step does not post a proposal comment automatically.

## Complete a local work item

On a supported host, `/deliver-issue .p2p/work/retry-safe-uploads/contract.md` runs the direct
path from the work-item reference and returns the current result and saved references. It asks for
unresolved outcome decisions and required approval of the exact proposed
agreement. It does not imply authority to commit, push, publish, or edit triage
labels. The [workflow scenarios](../checks/deliver-issue-scenarios.md) describe
what to inspect in a disposable end-to-end run.

For manual stage work or an unsupported host, run these commands as separate
invocations. Each stage skill returns a handoff for the next phase; it does not
call the next skill for you.

```text
/plan-acceptance .p2p/work/retry-safe-uploads/contract.md
/implement-contract .p2p/work/retry-safe-uploads/contract.md
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
Give review a fixed comparison base. Save `review.md` and `proof.md` under
`.p2p/work/retry-safe-uploads/`, which is excluded from the candidate, with the identities and evidence needed to read them in another
session. The [durable handoff rules](./acceptance-contract-protocol.md#durable-contract-handoff)
give the storage convention.

You can run review and proof in either order against the same fixed candidate.
Review examines the implementation's fidelity, scope, and engineering. Proof
checks every promised outcome against observed evidence. A `REVIEWED` result
does not stand in for `PROVEN`, and neither result replaces required CI or the
repository's review gate.

When matching full review and proof are saved, local acceptance needs no further
step. For an existing PR, use `/merge-readiness` near the merge decision. If a
new draft PR is wanted, use `/publish-pr`. Skill results number their next steps
so a particular action can be referenced without guessing which one was meant.

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
workspace, verifies that its complete tree outside `.p2p/` preserves the candidate,
and compares the current target tip with the review's frozen comparison base. It
allows the same destination at that base or a fast-forward descendant, while
keeping the candidate and reports bound to the original base. The preview records
the current target tip separately and says that acceptance evidence alone does
not establish compatibility with later target commits. The skill checks that tip
again before each effect, pushes without force, and rereads the draft PR. The
model may prepare the read-only preview on its own; publication effects still
require exact authorization. A non-fast-forward move blocks publication, and
merge readiness remains a separate assessment of the actual current PR target.

After the PR is confirmed, invoke `/merge-readiness <PR URL>` with the saved
review and proof reports near the merge decision. It checks that the PR's current
candidate has matching evidence, required CI, and repository approval and merge
conditions. It reports blockers without merging or replacing the repository's
approval process. Changes after the check require a new readiness assessment.

For the executable macOS Codex CLI workflow, see [the local delivery controller](./p2p-delivery-controller.md). It retains resumable stages and an isolated candidate while preserving the source checkout.

## Learn from an accepted delivery (optional)

After a full `PROVEN` result, use [`/retrospect`](../skills/productivity/retrospect/SKILL.md)
with the saved proof, exact candidate and contract references, and retrievable
use or maintenance observations. A matching review is useful when available,
but no PR or green unrelated CI is required. The skill proposes an evaluation
report at `.p2p/work/<slug>/retrospective.md`; save it under existing authority
and reread it from a fresh session. No learning is a valid outcome.

```text
/retrospect <saved PROVEN proof>; candidate <exact proven candidate>; experience <retrievable observations>
```

See the [retrospective walkthrough](./promise-to-proof.md#learn-from-a-proven-delivery-optional)
for report storage, possible violations, and evidence-backed suggestions.
Review each suggested learning and explicitly authorize the exact disposition:
accept, reject, or rewrite then accept. Accepted advice goes in one project-local
register (by default `docs/retrospective-learnings.md`), created on the first
authorized acceptance. Future `/plan-acceptance` runs consider relevant active
advice and cite what they used; the current source still determines the contract.
Promoting advice to a binding rule is a separate human-authorized change through
the source's owning workflow. If a later candidate is evaluated retrospectively,
it needs its own proof and evaluation; an old report stays historical.

## Inspect delivery boundaries when recommended

You do not need to choose direct delivery or slicing before planning. When
`plan-acceptance` recommends sizing inspection, run `/slice-contract` on the
saved parent contract:

```text
/plan-acceptance .p2p/work/retry-safe-uploads/contract.md
/slice-contract .p2p/work/retry-safe-uploads/contract.md
```

The default result is ignored child contracts such as
`.p2p/work/retry-safe-uploads-api/contract.md` and
`.p2p/work/retry-safe-uploads-browser/contract.md`.
The parent lists children and contributions. Each child links to the parent
and states a complete outcome, inherited constraints, and prerequisites.
Slicing creates no extra specifications by default. `NO SPLIT` records the
contract identity and direct-delivery reason in `.p2p/work/<slug>/slicing.md`;
continue with `/deliver-issue` and its existing #60 admission. No child contract
is created for that result.

Resolve consequential outcome or dependency decisions before dependent work.
Run `/plan-acceptance` on each child to complete its contract in place, then
implement, review, and prove that child. Select working branches under the
repository's normal rules. For dependent children, use a shared integrated
candidate or wait for prerequisites; draft PR publication does not support
stacked PRs.

Finally, capture one integrated candidate and review and prove the full parent.
Child proofs do not combine into parent proof.

## Deliver an epic with mixed destinations

Suppose a registry epic has three children: capture, lookup, and summary.
Capture is useful on its own. Lookup and summary must reach users together.
The repository's final destination is `trunk`.

1. Ask for a delivery preview on the established parent contract:

   ```text
   /slice-contract .p2p/work/registry/contract.md; capture may ship independently; keep lookup and summary together on epic/registry; final destination trunk; draft only
   ```

   Check that capture targets `trunk`, while lookup and summary target
   `epic/registry`. The preview explains whether each intermediate outcome is
   acceptable if the other children never ship. Dependencies alone do not
   determine the destination.

2. Approve the exact plan revision. The saved plan is
   `.p2p/work/registry/slicing.md`. If `epic/registry` does not exist, the handoff
   names its exact starting commit and the local or remote creation needed.
   Approve those concrete effects separately, or include them explicitly in the
   same grant. Saving the strategy creates no branch.

3. Complete the child contracts with `/plan-acceptance`, then run each child's
   delivery from its work path:

   ```text
   /deliver-issue .p2p/work/registry-capture/contract.md
   /deliver-issue .p2p/work/registry-lookup/contract.md
   /deliver-issue .p2p/work/registry-summary/contract.md
   ```

   Each workflow recovers its destination from the parent plan. Lookup waits
   until its required capture behavior exists in the actual candidate. After
   matching full child review and proof, `/publish-pr .p2p/work/registry-lookup/contract.md`
   previews a child PR targeting `epic/registry`. Review its exact preview before
   authorizing publication.

4. If lookup later becomes useful independently while its PR is open, revise
   the existing parent:

   ```text
   /slice-contract .p2p/work/registry/contract.md; lookup may now ship independently to trunk; inspect its open PR and preview the change
   ```

   Check the old and new destinations, affected children, saved work, required
   PR actions, and stale verification. Approve the revised strategy. Previously
   landed capture remains landed. Summary keeps its approved destination.
   Saving the revision leaves the open lookup PR unchanged.

5. Prepare lookup's candidate against `trunk`. If its current candidate includes
   unfinished sibling work, return to `/implement-contract` to isolate its
   contribution. A changed base needs fresh review; changed candidate content
   needs full fresh review and proof. Then run `/publish-pr` to preview the
   exact retargeting of the existing lookup PR. Authorize that concrete edit
   after inspecting the preview. The skill reads the resulting target back and
   preserves unrelated human text. `/merge-readiness` reports a target mismatch
   until the actual PR agrees with the revised plan.

6. Assemble every required contribution, including the independently landed
   work from `trunk`, into one exact parent candidate. Run both stages:

   ```text
   /review-implementation .p2p/work/registry/contract.md
   /prove .p2p/work/registry/contract.md
   ```

   A failed interaction returns to implementation or repair and requires fresh
   verification. Once full parent review and proof match, `/publish-pr
   .p2p/work/registry/contract.md` previews the remaining parent PR to `trunk`.
   `/merge-readiness` then checks the final destination's required CI and
   repository approvals. If every child landed independently, verify the
   assembled parent on `trunk`; no empty parent PR is needed.

Transfer the work files and `.p2p/work/` records with the candidate when changing
checkouts. A fresh session can then start from a child path without repeating
the strategy decision. A proposal awaiting approval does not replace the saved
approved plan.

## Create a tracker mirror when you need one

Local work does not require a GitHub issue. To publish a specification summary,
preview and explicitly authorize that separate action:

```text
/create-parent-issue specs/retry-safe-uploads.md; draft only
/create-parent-issue <approved preview>; publish the approved single issue to GitHub
```

The remote source reference must be durable and retrievable. Publishing an issue
does not commit or push local files. Keep the canonical acceptance contract in
`work/retry-safe-uploads.md` and use the issue as a link or mirror.

To mirror an approved decomposition, explicitly request tracker publication
from `slice-contract`. Local child paths remain their identities, and their
work files remain canonical. Retain remote issue references in those files.
Read back every remote write and resolve uncertain outcomes before retrying.
A pending remote mirror does not prevent a complete local handoff.

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
happens to be implemented. Record the proposal in the canonical work item or link it directly from there. For example:

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
owner approves the change, record that decision in the work item and run
`/plan-acceptance .p2p/work/retry-safe-uploads/contract.md`. Only `plan-acceptance` revises the
contract; a comment proposing or approving a change is not itself the new
contract.

Save and reread the returned contract at its canonical location. A material
change increments the revision (for example, v1 to v2) and keeps v1 available
as history. A new test path, more evidence, or clearer wording with the same
meaning does not increment it. Exact byte changes still invalidate old agreement
hashes. Preserve older revisions in Git or the work item's artifact history.
Update optional remote mirrors only under tracker-write authority. A changed
promise requires fresh proof against the new contract and exact candidate.

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

Do not commit `.p2p/` records. When moving an active delivery, copy its
`.p2p/work/<slug>/` contract and compact records plus the matching
`~/.p2p/executions/<repo-id>/<slug>/` directory, preserving bytes and access
limits. After successful explicit cleanup, the external runtime retains the
candidate workspace and Git objects. Keep secrets out of snapshots and
evidence, and delete scratch files only after durable records are read back.

In the new checkout, resume with the work-item path:

```text
/deliver-issue .p2p/work/retry-safe-uploads/contract.md
```

The workflow discovers linked specifications, parent and children, candidate,
reports, and evidence. It checks current identities before reusing results.
Local `.p2p/` record updates leave reports bound to their original candidate.
Product, agreement, or comparison-base changes require fresh applicable
verification. File presence alone is not acceptance.

For manual inspection, use the installed skill's `scripts/p2p_filesystem.py`
with `resolve` to list records or `resume` with the intended comparison base to
validate candidate currency. This helper does not judge proof or grant approval.
The [protocol](./acceptance-contract-protocol.md#candidate-identity-and-resume)
defines the identity and recovery rules.

## Reduce retained work data

Run checks in `.p2p/tmp/` or an OS temporary directory. Save the relevant command,
assertion, actual result, and environment in the final report. Retain separate
files when they supply required evidence, such as replayable traces and host
receipts. Keep one recoverable candidate snapshot; reference it from reports.

After a successful verified delivery, run the controller's explicit cleanup.
It verifies the source checkout stayed at admission, reads back the four final
local records, and removes attempt logs and scratch. The candidate workspace
and Git objects remain under `~/.p2p/executions/<repo-id>/<slug>/runtime/` for
publication. Keep the remaining `.p2p/` records ignored; they are never
committed to the project.

For historical inspection of P2P files already present in an older Git commit,
recover them into a new temporary directory:

```sh
recovery_dir=$(mktemp -d)
git archive FULL_COMMIT_SHA .p2p/work/SLUG | tar -x -C "$recovery_dir"
```

Use only a full commit that already contains the legacy files. A full clone
retains the referenced ancestor; a shallow clone or source export may need the
missing Git history before recovery. Restore required files before verification
or resume. Do not create new commits that add `.p2p/` records.

This reduces the working tree size. Existing Git objects
remain in history, so the repository's Git storage does not shrink.

For a P2P state migration that removes selected records from the current Git
tree while keeping history intact, follow the [migration guide](./p2p-state-migration.md).

## Pick a command

| Command | Use it to |
|---|---|
| `/setup-promise-to-proof` | Establish local storage and Git rules, with optional tracker configuration. |
| `/create-parent-issue` | Preview an optional GitHub mirror of a specification; publish only with authority. |
| `/triage-issue` | Recommend the next action for an existing issue; apply only approved label or closure changes. |
| `/plan-acceptance` | Define and revise the acceptance contract. |
| `/audit-acceptance` | Independently audit an exact proposed contract before human approval. |
| `/slice-contract` | Create linked local child work items; optionally publish approved tracker mirrors. |
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
