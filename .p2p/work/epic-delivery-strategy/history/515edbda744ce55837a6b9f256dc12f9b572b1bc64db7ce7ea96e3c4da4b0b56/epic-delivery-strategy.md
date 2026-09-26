# Work item: Support independent, grouped, and mixed epic delivery

Status: Imported source for parent acceptance planning; no acceptance contract or approval yet.
Source: [Epic delivery strategy specification](../plans/epic-delivery-strategy-spec.md)
Source attribution: https://github.com/grove/promise-to-proof/issues/33, updated 2026-09-26T21:33:35Z

## Imported issue

Support epics whose children merge independently, through one integration branch, or in a mixture of both. Existing skills recommend destinations, retain the approved plan, and explain where work will merge. Users can revise the strategy after work starts without recreating the epic.

## Scope

- Extend the existing slicing, delivery, implementation, review, publication, and readiness workflows and keep shipped protocol copies consistent.
- Record the canonical delivery plan in `.p2p/work/<parent>/slicing.md`, with the configured final destination, optional integration branch, default choice, child exceptions, resolved destinations and reasons, approval identity, history, and outstanding actions.
- Recover the approved plan from a child work-item path in a fresh session. Keep proposals separate from active decisions and bind publication previews and readiness reports to the exact approved plan. Preserve unsliced workflows and normalize explicit legacy approvals without asking again.
- Resolve prerequisites against actual candidate behavior. Block missing or conflicting routing decisions and explicit or actual PR targets that disagree with the plan.
- Support strategy changes for unstarted work, local candidates, open PRs, integrated children, and children already merged into the final destination. Preserve work and history, preview affected actions and stale verification, and prevent unfinished sibling changes from reaching the final destination.
- Keep strategy approval separate from authority for branch and PR effects. Support exact authorized retargeting through `publish-pr`, with verification and readback. Reject stale previews, preserve confirmed partial effects, and reconcile retries without duplicate branches or PRs.
- Verify the complete parent outcome on one assembled candidate, including independently merged contributions and interactions. Child completion never establishes parent acceptance. Require full parent review and proof before parent PR publication, and required CI and repository approvals before final merge. All-independent delivery needs parent verification but no empty parent PR.
- Add the specified how-to walkthrough, README link, and FAQ. Extend scenario checks for S1–S14 using disposable Git and controlled tracker fixtures; identify unavailable live-service validation as unexecuted.

## Constraints and exclusions

Reuse existing work items, skills, commands, Markdown records, history, and candidate identity rules. Do not hard-code `main`. Preserve existing review, proof, CI, compatibility, safety, and authorization gates. Delivery-plan revisions remain separate from acceptance-contract revisions; changed product promises return to `plan-acceptance`.

Exclude automatic merges, new tracker labels or requirements, policy enforcement outside the skills, release orchestration, new feature-flag systems, stacked PRs, cross-repository delivery, multiple integration groups per parent, and a new scheduler. Strategy changes do not imply reverting published work, deleting branches, force-pushing, or weakening checks.

## Authoritative source

The linked specification contains the full promises, boundaries, and required scenarios. This issue summarizes the source for acceptance planning; it is not an acceptance contract or ticket breakdown.

- Specification: https://github.com/grove/promise-to-proof/blob/5e369c1b45ba817b8add6b20a9b7b1c97898fa12/plans/epic-delivery-strategy-spec.md
- Repository: `grove/promise-to-proof`
- Path: `plans/epic-delivery-strategy-spec.md`
- Commit: `5e369c1b45ba817b8add6b20a9b7b1c97898fa12`
- SHA-256: `7a231d84f739a459f770870d23038fbc4946c759f04241c87f2a6322d9a1645e`

<!-- grove:create-parent-issue source=grove/promise-to-proof:plans/epic-delivery-strategy-spec.md -->
