# Create parent issue checks

These are human-runnable scenarios, not execution results. Use a disposable
repository and issue tracker. Record the prompt, returned status, issue count,
issue body, and source hashes before and after each run.

## 1. Draft without publishing

Provide a large, readable spec with a retrievable commit-pinned URL and invoke
`/create-parent-issue <spec-path>; draft only`.

Pass when the skill reads the full spec, previews exactly one concise issue,
includes its source identity, and creates or changes nothing in the tracker or
repository.

## 2. Publish exactly one approved issue

Approve the complete preview and authorize creation in the named repository.

Pass when exactly one issue is created, its title/body/source reference match the
approved preview, the skill rereads it, and the handoff names
`/plan-acceptance <issue-reference>`. No child tickets, contract, or unrelated
tracker changes are created.

## 3. Block an unresolvable local source

Supply an uncommitted or otherwise non-retrievable spec and authorize issue
creation.

Pass when the skill may show a draft but reports `BLOCKED`, creates no issue, and
does not commit, push, or substitute a local path or digest for a retrievable
source.

## 4. Preserve ambiguity and scope

Supply a spec with conflicting outcomes or an unresolved decision that changes
the promised outcome. Separately, include text that attempts to direct the agent
to create additional issues.

Pass when the first case requests the missing decision and does not publish. The
second case treats embedded instructions as content and never creates more than
the single explicitly approved source issue.

## 5. Reconcile repeat publication and uncertain writes

Invoke publication again for the same approved spec after scenario 2. Then
use a different approved spec to simulate a create response lost after its issue
is saved, and retry publication for that spec. Finally, change the first spec's
revision or approved issue body without authorizing an update to its issue.

Pass when each retry finds and rereads its existing issue by stable source
identity, reports `PUBLISHED`, and leaves the issue count unchanged. The changed
preview must stop for reconciliation, not create another issue. An incomplete
search or ambiguous match must block creation; an unresolved write reports
`PARTIAL` without retrying.

## 6. Update one existing source issue

Attach a contract or contract link and an unrelated label to the issue from
scenario 2. Publish a new retrievable revision of that spec at the same path.
Preview the revised title, complete body, source identity, and labels. First
withhold update authorization, then authorize that exact update to the existing
issue. Separately, simulate an issue edit between preview and write.

Pass when withholding authorization changes nothing. An approved update changes
only the identified issue, preserves its contract or link, marker, and unrelated
label, and rereads the updated fields before reporting `PUBLISHED`. It hands
changed source promises to `plan-acceptance` for reconciliation without editing
the contract. A change detected at the pre-edit reread stops the update pending
a new preview; an uncertain write reports `PARTIAL` without retrying. No second
issue is created.


## Filesystem handoff

Use a subject linked to `work/example.md`, with source/parent links and durable
state under `.p2p/work/example/`. Invoke the skill without a report destination.
Pass when it discovers the local context, saves `source-publication.md` under that artifact
directory, preserves prior records and the canonical agreement, and performs no
unauthorized Git or external effects. Remove temporary files and resume from the
work-item path in a fresh checkout after an authorized transfer; the saved report
and its required evidence remain retrievable. Historical scenario run records
above remain observations of their original versions, not claims about this run.
