# Publish or reconcile a decomposition

Use this procedure for authorized publication, reconciliation, and publication
previews that need destination capability checks. Follow configured tracker tools
and triage conventions. Inspect the installed interface and permissions rather
than assuming CLI flags or API support.

## Reconcile identity before writing

Give each slice a stable ID within its source work item. Preserve IDs across
reordering, reruns, and parent revisions for the same logical slice. Retain
mappings for retired or replaced slices. Keep the ID-to-ticket map in the canonical
plan. New issues also carry a stable marker such as:

```html
<!-- grove:slice-contract parent=grove/project#123 slice=S1 -->
```

Give the canonical parent index its own stable marker, using the same parent key:

```html
<!-- grove:slice-contract-index parent=grove/project#123 -->
```

Before creating an index, inspect the parent body, all comment pages, and linked
plan artifacts for that marker. Reuse the confirmed index on reruns and after
uncertain writes. If an older index has no marker, confirm its identity and add
the marker within approved planning edits. Multiple matches or uncertain identity
require reconciliation before writing another index.

Inspect mapped issues and relevant existing children, including closed items.
Use enough pagination and readback to establish identity. Titles, a single search
page, and an old chat summary are insufficient. Markers identify records but grant
no edit authority. Reuse only confirmed matching work and preserve existing parent
relationships unless a change is explicitly approved.

Recheck the parent agreement and ticket state before writing. If amendments,
concurrent edits, or started implementation invalidate the approved plan, pause
affected writes and present a scoped reconciliation. Regrouping unchanged promises
changes the decomposition, not the parent revision. Child contract revisions
still belong to `acceptance-contract`. Preserve unrelated human content.

## Save tickets and relationships

For GitHub, resolve the target repository explicitly. Create one issue per approved
new slice and reuse existing matches. Create prerequisites first when their actual
identifiers are needed. Record each confirmed returned identifier immediately in
the publication record, then establish parent and blocking links with real IDs.

Prefer native sub-issue and dependency relationships when tools and permissions
support them. Keep readable references in ticket bodies too. A disclosed textual
fallback is sufficient unless repository automation requires native edges.
An unavailable mandatory edge leaves publication incomplete. Preview known
limitations before writing and never report an unconfirmed relationship as saved.

Keep one canonical index on the originating issue, in a managed section or
comment, or in a directly linked repository artifact. Modify only approved
planning metadata. Preserve the source and contract text, rather than replacing
the parent description or creating a second parent. A local source without a
tracker parent can use a durable source and plan link. Creating a tracker parent
needs explicit approval. Paths inaccessible from the receiving checkout are not
durable references.

For local publication, follow the configured layout. If none exists and local
publication was explicitly selected, use `.scratch/<work-id>/plan.md` and
`.scratch/<work-id>/issues/S<n>-<slug>.md`. Resolve relative links from the saved
artifact. Contract storage still follows the protocol. Transfer required files
in a commit or snapshot before another checkout receives the handoff. Saving
alone does not authorize committing.

Reread tickets, relationships, and the canonical index. Confirm destination,
content, identifiers, and edge directions. Return actual persisted references.

## Recover incomplete publication

If a request times out with an unknown result, search and read back by stable
identity before retrying. If uniqueness or remote state remains uncertain, stop.
Do not infer failure merely from a nonzero exit or missing response.

Retain successful writes. Record uncertain operations and remaining approved
actions, then resume only missing operations after reconciliation. Never delete
successful issues as rollback. Updates to active or human-edited tickets need
scoped authority and must preserve unrelated content. If concurrent publishers
prevent establishing uniqueness, pause. Multi-step writes are neither transactional
nor guaranteed exactly once.

## Child ticket shape

Use the following information without repeating empty sections. Criteria remain
source material, not an independently issued acceptance contract.

```markdown
# <Observable outcome>

<!-- grove:slice-contract parent=<stable source key> slice=S1 -->

## Parent and contribution
Parent source: <durable reference>
Parent contract: <location, revision, exact snapshot reference>
Decomposition: <canonical plan/index>
Contribution: <qualified parent IDs and precise portion delivered>

## What this delivers
<Observable outcome once prerequisites exist.>

## Acceptance criteria for this slice
- <Required behavior and boundaries grounded in the parent.>

## Inherited constraints and non-goals
<Applicable invariants, exclusions, compatibility, and repository obligations.>

## Blocked by
<Actual references and required outcomes, or no work prerequisites.>

## Evidence approach and open decisions
<Agreed seams, independent expected outcomes, evidence gaps, and decisions.>

## Handoff
Run /acceptance-contract on this ticket, preserving the parent mapping.
Then use the chosen implementation, review, and proof workflows.
Child completion does not establish parent acceptance.
```

Requirement IDs need not appear in titles or code comments. Tracker checkboxes
may present criteria, but their checked state is not proof.
