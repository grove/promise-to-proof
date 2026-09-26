# Epic delivery strategy

Status: Proposed implementation specification, 26 September 2026.

## Outcome

Promise to Proof supports epics whose children merge independently, together,
or in a mixture of both. The existing skills recommend a delivery plan, remember
the approved choice, and explain the destination before publication or merge.
Users can change the strategy after work starts without recreating the epic.

An epic is an existing parent work item with children. This specification adds
no new work-item type, skill, command, or tracker requirement. It is source
material for a later acceptance contract, not a claim of implementation or proof.

## Existing behavior

The [acceptance contract protocol](../docs/acceptance-contract-protocol.md)
already separates child completion from parent acceptance. Parent proof covers
one integrated candidate, including interactions and shared invariants.

The [slicing skill](../skills/productivity/slice-contract/SKILL.md) already records
an intended delivery path. It permits a parent branch and separately branched
children, but does not prescribe consistent destination selection and enforcement
through the remaining skills. Publication requires matching full review and proof,
even for a draft PR. This specification preserves that requirement.

## Delivery choices

A plan names the final destination branch, normally the repository's configured
default branch. Examples use `main`; implementations must not hard-code it.
A plan that groups children also names one integration branch, such as
`epic/checkout`, using repository branch conventions.

Each child has one effective merge destination:

| Choice | Destination | Meaning |
|---|---|---|
| Merge independently | Final destination | The child's complete outcome is acceptable there without the remaining children. |
| Merge with the epic | Integration branch | The child joins the assembled work before the parent PR reaches the final destination. |

The plan records a default choice and explicit child exceptions. It displays the
resolved destination and a short reason for every child. A mixed plan needs no
third mode. One integration branch per parent is sufficient for this change.

The recommendation answers this question:

> If this child reached the final destination and the remaining children never
> shipped, would that intermediate state be acceptable?

Merging and releasing are distinct. Work behind an existing feature flag can
merge independently when that intermediate state meets the agreement. This
feature does not add flags or weaken compatibility, safety, or acceptance rules.

Dependencies describe required outcomes, not merge destinations. A child can
merge independently and still depend on another child. The receiving workflow
must confirm that prerequisite behavior exists in its actual candidate.
Issue hierarchy, open siblings, and tracker labels do not determine destinations.

## Planning and durable state

`slice-contract` recommends destinations from the source promises, repository
rules, and inspected behavior. It asks about unclear product intent rather than
requiring the user to choose a branching model. The delivery choice appears in
the existing breakdown preview and approval. An unchanged approved choice does
not trigger another strategy question downstream.

The canonical delivery plan stays in `.p2p/work/<parent>/slicing.md`, alongside
the existing decomposition. It records:

- The parent and child work-item paths, the final destination, and any integration branch.
- The default choice, child exceptions, resolved destinations, and reasons.
- The approved plan revision, its approval source, and retained previous revisions.
- The parent completion conditions and any pending setup or strategy-change actions.

The plan revision identifies delivery decisions separately from contract revisions.
Pending proposals must be distinguishable from the active approved plan. Saving
a proposal does not activate it or overwrite the prior approved decision.

Children retain their existing parent and decomposition links. Users do not
maintain duplicate destination settings in every contract. Starting with only a
child work-item path, a fresh session can recover the approved plan and its
history through those links. Required records must travel with the work under
the existing retention and transfer rules.

Publication previews and readiness reports retain the exact approved plan
revision and retrievable text identity they used. A changed plan invalidates
affected routing decisions and publication previews, even though `.p2p/` remains
outside the product candidate. Historical reports keep their original meaning.

Unsliced work keeps its current workflow. An older sliced plan with an explicit,
approved destination can be normalized without asking the user to decide again.
Missing or conflicting routing information returns a focused handoff to
`slice-contract` before dependent work. It never silently defaults a child to
`main` or invents a prior approval.

## User experience across skills

The following examples specify meaning, not exact wording.

| Stage | Required behavior |
|---|---|
| `slice-contract` | Show each child's destination and reason, then explain which work can reach the final destination first. |
| `deliver-issue` and direct implementation | Resolve the saved plan before choosing the starting point and comparison base. State the destination and any unavailable prerequisite. |
| `review-implementation` | Review against the actual intended target base and inherited agreement. Preserve exact candidate and base identities. |
| `publish-pr` | Discover the destination when omitted. Show it in the preview and PR description. Reject a conflicting explicit target with a strategy-change handoff. |
| `merge-readiness` | Compare the actual PR target with the current approved plan. Name that target in its result and withhold readiness on a mismatch. |
| Parent completion handoff | Identify remaining integration work, parent review, and parent proof. Child completion alone never becomes parent acceptance. |

A mixed-plan preview can say:

| Child | PR destination | Reason |
|---|---|---|
| Backward-compatible API extension | `main` | Useful and safe without the checkout changes. |
| Checkout flow | `epic/checkout` | Must arrive with checkout validation. |
| Checkout validation | `epic/checkout` | Part of the complete checkout behavior. |

> The API extension can reach `main` first. The checkout changes reach `main`
> together after verification of the assembled parent.

Delivery of a grouped child can say:

> This child's PR targets `epic/checkout`. Completing it does not complete Checkout.

A successful child readiness assessment can say:

> Ready to merge into `epic/checkout`. Parent verification is still pending.

Existing machine-readable outcomes such as `READY`, `BLOCKED`, and `PROVEN`
remain unchanged. Human-facing text adds the destination and the next action.
It does not imply that a skill's readiness advice grants merge authority.

## Integration and parent completion

Planning records branch setup without creating or switching branches. If the
integration branch is missing, the handoff names its exact proposed starting
commit and the local or remote creation needed. The invoking workflow performs
that setup only under authority covering those effects, then verifies the refs.
An existing branch is inspected and reused only when it matches the plan.
An unrelated branch with the same name is a conflict, not an overwrite target.
Users need no new command or hand-edited metadata for this setup.

Child PRs target the integration branch directly. A dependent child can pick up
its prerequisite after that prerequisite is integrated there. This does not add
stacked-PR publication or permit a child PR to carry unreviewed sibling work.
If a slice cannot satisfy its own contract, grouping alone does not make it
publishable. Required CI remains a merge-readiness gate, not a prerequisite for
proof or publication. The existing shared-candidate exception and approval rules
still apply without weakening either gate.

Changes to an integration branch can make a child's comparison base stale.
Publication and readiness must apply the existing base and candidate checks;
the branch name alone does not establish current review or proof.

Before the grouped parent reaches the final destination, all required child
contributions must exist in the assembled candidate. This includes independently
merged children and any changes needed to integrate with the final destination.
Closed issues and merged-PR counts are insufficient evidence.

The exact assembled candidate needs full parent review, full parent proof, and
the final destination's required CI and repository approvals. Changes after
verification require the refresh prescribed by the shared protocol. The parent
PR is published after matching full review and proof. There is no early,
unverified parent draft-PR path in this change.

When all children merge independently, parent verification still checks their
combined outcome on an exact candidate. No empty integration PR is required
solely to mark the parent complete.

## Changing strategy after work starts

Users can invoke `slice-contract` on the existing parent with requests such as:

> Keep the remaining children together until the epic is finished.

> The API extension can now merge independently.

The skill reads the approved plan, current work, saved reports, and known PR
state. It proposes a revision with the old and new destinations, reasons,
affected children, required branch or PR actions, and stale verification.
Unknown remote state is marked unresolved, not assumed unchanged.

The preview distinguishes these cases:

| Current state | Required treatment |
|---|---|
| Child has not started | Update its destination after approval. Preserve its contract, identity, and dependency links. |
| Local work or reports exist | Preserve the work. Reassess prerequisites, candidate scope, base, and report applicability. |
| Child has an open PR | Propose the exact retargeting or replacement needed. Do not change the PR just by saving the plan. |
| Child is already integrated into the epic branch | Keep that history. Independent delivery needs a candidate containing only the intended work and satisfied prerequisites. Retargeting must not expose unfinished siblings. |
| Child is already merged into the final destination | Record it as landed. Apply the new strategy to remaining work. Do not undo or reclassify the historical merge. |

Plan approval and external-effect authority remain distinct. An unchanged grant
is reused within its scope. Approval can cover a concrete plan and listed effects
together, but approval of strategy alone does not authorize ref changes,
retargeting, publication, or merging.

`slice-contract` owns the revised plan and the action handoff. `publish-pr` gains
a narrow path to preview and perform retargeting of a known open PR under exact
authority, with matching candidate verification against the new target and
readback of the resulting PR. It preserves unrelated human edits and records
the updated target and plan identity. It does not treat a retry as permission to
create a duplicate PR. Candidate extraction or repair returns to implementation.
`merge-readiness` detects mismatches but does not retarget PRs.

Publication to the superseded destination is blocked. An authorized retargeting
can proceed after its verification requirements pass. Merge readiness remains
blocked until the actual PR target matches the approved plan and all other gates
pass. Unaffected children can continue.
Partial application retains confirmed effects and outstanding actions so that
resume reconciles current state before retrying. Concurrent plan or PR changes
invalidate a stale preview rather than authorizing an overwrite.

Changing delivery destinations alone does not change product promises or bump
the acceptance contract revision. A changed promise routes through
`plan-acceptance`. A changed comparison base requires fresh review. A changed
candidate or binding agreement requires full fresh proof and review as prescribed
by the protocol. Unchanged proof remains historical evidence for its exact
candidate; strategy approval does not manufacture a new matching report pair.

## Acceptance scenarios

These are required implementation checks, not observed results. Scenario runs
must inspect saved state and tool effects as well as user-facing text.

| ID | Scenario | Required result |
|---|---|---|
| S1 | Unsliced work and an epic of independent children | Ordinary delivery stays available. Children can target the configured final destination without waiting for unrelated siblings. |
| S2 | Grouped epic with two complete children | Child PRs target the integration branch. Neither is presented as ready for the final destination. Parent publication waits for integrated parent verification. |
| S3 | Mixed epic | One child targets the final destination and two target the integration branch. The preview explains why, and each later stage uses the saved choice. |
| S4 | Fresh session given only a child path | Resolve the approved destination without chat history, repeated strategy questions, or manually supplied report paths. |
| S5 | Missing, conflicting, or proposed-only plan | Do not infer an approved destination. Identify the smallest planning decision needed. A pending revision does not replace the active plan. |
| S6 | Explicit target or actual PR target conflicts with the plan | Publication or readiness blocks with the expected and actual destinations and a corrective handoff. No silent retargeting occurs. |
| S7 | Switch from independent to grouped after one child merged | Preserve the landed child. Preview changes for remaining local work and open PRs. Apply only authorized effects. |
| S8 | Switch a grouped child to independent after siblings integrated | Prevent unrelated sibling changes from reaching the final destination. Require a correctly scoped candidate and fresh applicable verification. |
| S9 | Strategy changes after preview approval, or during application | Reject the stale preview. Preserve confirmed effects, reconcile on resume, and avoid duplicate branches or PRs. |
| S10 | Destination changes with unchanged code, then with a rebase or repair | Distinguish base-only review refresh from full verification of a changed candidate. Never treat old reports as proof of new content. |
| S11 | All children complete but parent interaction fails | Parent remains unproven and blocked from final merge. Child completion and green child checks cannot override the failure. |
| S12 | All children merge independently | Verify the parent on an exact integrated candidate without creating an empty parent PR. |
| S13 | Integration branch missing, conflicting, or advanced | Give an exact setup or refresh handoff. Do not overwrite refs, reuse a stale review base, or weaken required checks. |
| S14 | Existing feature flag, custom default branch, and child dependency | Respect the acceptable intermediate state, configured destination, and actual prerequisite outcomes. Do not equate hierarchy or release timing with merge destination. |

## Implementation scope and documentation

Extend the shared protocol and existing slicing, delivery, implementation,
review, publication, and readiness instructions where they consume this plan.
Keep any shipped protocol copies consistent. Reuse existing Markdown records,
history, candidate identity rules, and scenario-check conventions.

Add one how-to walkthrough covering mixed destinations, a strategy change with
an open PR, and final parent verification. Link it from the README's slicing
entry. Add a short FAQ explaining that child completion, integration, and parent
acceptance are different events. Examples must show the destination and next
action without requiring users to read the protocol.

Extend the existing scenario checks with the cases above. Use disposable Git
fixtures for branch and candidate-scope checks and controlled tracker fixtures
for PR changes. Any unavailable live-service validation remains explicitly
unexecuted; a textual walkthrough alone does not prove remote mutation behavior.

Out of scope are automatic merges, new tracker labels, repository-hosted policy
enforcement outside the skills, release orchestration, new feature-flag systems,
stacked PRs, cross-repository delivery, multiple integration groups within one
parent, and a new scheduler. Strategy changes never imply reverting published
work, deleting branches, force-pushing, or weakening required checks.
