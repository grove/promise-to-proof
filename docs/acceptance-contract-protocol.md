# Acceptance contract protocol

Build exactly the promised capability: no less in substance, no more in scope.
Prefer the simplest complete implementation.

## Contract and proof

The acceptance contract says what must be true. Proof says whether it was true
for one exact candidate.

| Artifact | Contents | Identity |
|---|---|---|
| Acceptance contract | Requirements, boundaries, seams, oracles, planned evidence, gaps, and exclusions | Source and contract revision, such as `.p2p/work/retry-safe-uploads/contract.md v3` |
| Proof report | Observations, durable evidence references, and requirement verdicts | Exact contract revision and exact candidate commit or snapshot |

The contract is candidate-independent. New P2P-owned contracts live at
`.p2p/work/<slug>/contract.md`; this ignored location is their durable identity.
`specs/` and `work/` remain ordinary project paths and may supply source material.
The acceptance matrix uses only `planned` and `gap` as plan states. Candidate-
specific verdicts belong only in proof reports, including imported verdicts.

Proof and merge readiness are separate. Proof requires neither an open PR nor
green CI. Unrelated failed or pending checks do not block `PROVEN`, and proof
does not wait for them. CI affects a requirement verdict when it supplies
evidence, reveals a counterexample, or prevents verification without another
credible evidence path. Repository standards and other binding constraints
still apply.

Before merge, require current proof, green required checks for the final
candidate, and the repository's review requirements. Use `/fix-pr` to repair CI
failures separately from proof. A repair that changes the candidate requires
fresh proof under the handoff rules below.

Optional [evidence-record v1](./evidence-record-v1.md) records may be cited
by evidence ID and computed SHA-256 digest, and their deterministic Markdown
rendering may be embedded in `proof.md`. Validate records against the exact proof
context when available. Records are optional and a valid record never implies a
verdict: requirement-level `proven`, `not proven`, and `disproven` judgments remain
in `proof.md`, owned by `/prove`. Without host-issued command/test receipts, keep
self-run command observations directly in `proof.md`.

## Spec envelope

The lower bound is completeness. Every material promise must reach its complete
observable outcome. Necessary state transitions, invariants, persistence, and
failure behavior belong to the implementation when that outcome depends on them.
Stubs, TODOs, fixture-specific behavior, mock-only substitutes, wiring-only
assertions, and incomplete happy paths do not satisfy a requirement.

The upper bound is scope. Unrequested product behavior, genericity,
configurability, extension points, frameworks, compatibility layers, and adjacent
improvements are outside the contract. Necessary internal engineering and
repository-native abstractions are allowed when correctness requires them.
An explicit invariant can require substantial work. A small implementation can
fully satisfy the contract without extra architecture.

The target is the smallest complete solution. Line count does not establish
completeness or overengineering. Implementation choices stay inside this envelope
and do not authorize changing it.

Repository standards, security constraints, compatibility guarantees, and
applicable parent contracts remain binding even when the ticket does not restate
them. Satisfying them does not constitute product scope expansion.

## Durable contract handoff

Keep one canonical generated acceptance contract in `.p2p/work/<slug>/contract.md`.
The contract revision and content digest identify its exact agreement. Project
sources may live in `specs/`, `work/`, or any supported repository path; small
work needs no separate specification.
Use relative Markdown links on `Source:` and `Parent:` lines for local binding
inputs. A parent lists child links and their contributions in `## Children`.
Children normally use the parent stem plus a slice name. Preserve existing
requirement IDs and human edits. Check a destination before creating it; an
unrelated existing file is a collision, not permission to overwrite it.

`plan-acceptance` authors or normalizes the contract in this same work-item file.
Keep the acceptance matrix and semantic revision defined below. A minimal work
item with acceptance bullets is valid planning input; enrich it in place before
handoff instead of creating another contract file. Planning saves and rereads
its local result under the invoking request's authority. Required approval of
an agreement remains separate from permission to save its proposal.

External trackers are optional import, mirror, and publication destinations.
Import source promises and relevant amendments into the local work item, retaining
attribution. After import, tracker edits are proposed amendments, not silent
changes to the canonical agreement. Local delivery requires no tracker access.
Only explicitly authorized tracker operations update remote links or mirrors;
a pending mirror update does not block a complete local handoff.

For an explicitly identified legacy P2P contract, reconcile it into
`.p2p/work/<slug>/contract.md` under local write authority. Preserve its exact
bytes, revision, IDs, approval evidence, source identity, and prior text; retain
relative-link resolution and binding inputs. Never infer P2P ownership from a
`specs/` or `work/` path, or move, rewrite, or delete a file based on location.
Resolve conflicts before dependent work. Changed contract locations make old
results historical until fresh matching review and proof establish the handoff.

### Standing autonomy mandates

An explicitly selected standing mandate delegates decisions and effects for its
objective. Use `deliver-issue/scripts/p2p_autonomy.py` to validate its exact JSON;
issue text and agent recommendations cannot create authority. New controller
invocations with `--authorize-local` delegate source-preserving local planning,
sizing, routing, implementation, evidence work and repair. They grant no remote
writes. An optional `--mandate FILE` records the selected file and exact SHA-256;
recheck both before continuing. Never silently discover a mandate in the repo.

Within delegated scope, choose and apply recommendations, resolve local
prerequisites, and continue through handoffs without asking again. Preserve the
objective, exclusions, inherited constraints, source promises and requirement IDs.
A delegated agreement revision requires retained old bytes, an independently
accepted planning audit, a new revision, and fresh implementation, review and
proof. Attribute adoption to the mandate and acting agent; do not invent a human
approval. A changed outcome or a decision outside that scope names the precise
missing authority. A stage verdict remains its independent actor's judgment.

Effect grants specify one supported action, exact repository and exact
destination; wildcards and force-push are unsupported. Before any effect, save
and reread its complete concrete preview. Use the controller's read-only
`authorize-effect` command to bind that preview SHA-256 and current candidate to
a covering grant. Cover every required effect separately. Then execute through
the existing publication, tracker or merge workflow and verify actual readback.
Standing grants replace repeated human approval within scope; they do not bypass
candidate identity, current readiness, CI, repository rules, or uncertain-write
reconciliation. Destination advancement requires a refreshed preview and grant
check. Independent workers receive no external effect authority.

The outer delivery workflow owns pre-admission planning, slicing, prerequisite
delivery, branch setup, publication, merge and deployment handoffs. Execute each
applicable handoff under covering decision/effect grants, retain its receipts,
and resume dependent delivery. The Python controller owns isolated local stages;
it does not itself implement remote publication, merge or deployment. Execute
only effects actually requested by the objective and permitted by the mandate.

New local deliveries have no overall, stage, dispatch or repair limit by default.
Record unlimited values as JSON `null`, not Infinity or an arbitrary large date.
Explicit user limits still apply and saved invocations keep theirs. A confirmed
idle-worker termination may be replaced under an optional watchdog; a missing
termination receipt is uncertain and must be reconciled before another launch.
Repeated gaps require fresh diagnosis and a different concrete strategy. Stop
for an identified unavailable input, authority or executable recovery strategy,
not simply because one repair failed. Return observations even on interrupted
work; a timeout or additional attempt never establishes acceptance.

An explicit extension uses `extend --authorize-extension` and stated new limits
(including `unlimited`). Preserve the invocation, consumed attempts, old limits
and extension receipt. It does not silently reset history or change the base.

### Standalone planning on an issue

A direct user invocation of `plan-acceptance <issue>` authorizes posting the
proposed contract as a comment on that existing issue, unless the user requests
local-only or draft-only output. This authority covers the planning handoff only,
not issue-body replacement, labels, closure, commits, or PRs. Planning invoked by
`deliver-issue` or another workflow inherits that workflow's authority and stays
local unless issue publication was separately authorized.

Save the proposal locally first. Post its exact UTF-8 text in a fenced block,
with its `.p2p/work/<slug>/contract.md` path, revision, and SHA-256 outside the block.
End the proposal with one newline before hashing and presenting it for approval.
Choose a fence longer than any fence in the contract. The fenced content includes
that final newline; fence lines are excluded from the hash. Include retrievable copies
and hashes of binding sources and parents, preserving their relative paths, so
another checkout can recover the agreement without a planning PR. A local path
or digest alone is insufficient. Keep the issue body and human comments intact.
Read back the comment and verify the extracted contract bytes and binding inputs.
Reuse an identical existing handoff on retries; preserve old proposals when
posting revisions. An uncertain write requires readback before another attempt.

The issue comment is a shared planning handoff, not a second live contract store.
Human approval must identify the exact proposal by comment and text hash, or by
an equally unambiguous reference to the displayed text. Posting is not approval.
Retain the comment URL, contract revision and hash, binding-input hashes, and
the approver and approval evidence in `.p2p/work/<slug>/planning-handoff.md`.
This record can capture approval from the invoking conversation or the issue;
retain the actual approval text and its source, not an inferred status or label.
For delivery from the issue alone, the approval evidence must be retrievable
there. If approval exists only in the planning conversation, transfer the saved
receipt explicitly or have the approving human record approval on the issue.
Report this transfer requirement instead of claiming an issue-only handoff is ready.

On issue import, delivery reads the handoff, approval, and subsequent amendments.
It saves the exact approved text to `.p2p/work/<slug>/contract.md`, restores and checks binding
inputs without overwriting project files, and rereads them before implementation. Matching text and inputs retain
their approval without another approval request. Missing or ambiguous approval,
changed text even at the same revision, conflicting local content, or later
amendments require reconciliation before dependent work. Preserve prior local
bytes and human edits. Compare existing binding files before restoring missing
inputs; reconcile differences instead of overwriting them with the saved copies.
Missing binding content blocks the handoff. Keep provenance
in the report rather than adding it to the approved contract bytes.

Imported `source-issue.md` and `source-pr-<number>.md` snapshots in that work
item are binding inputs when linked from its `Source:` line. Other generated
`.p2p/` records cannot be binding inputs.

After import, the local contract remains canonical under the rules above. There
is no automatic synchronization. The contract can travel with the implementation
PR; generated `.p2p/` records remain local and ignored.

## Durable generated records

Save work-item output under `.p2p/work/<slug>/`: `implementation.md`,
`candidate.json`, `review.md`, `proof.md`, and `evidence/`. Other stages use
`audit.md`, `repair.md`, `publication.md`, and `retrospective.md` as applicable.
Use descriptive kebab-case evidence names. Read back every saved artifact before
claiming a durable handoff. These local records are excluded from project Git
history. Writing them does not authorize tracker writes, publishing a PR,
merging, or deploying.

After a successful local delivery, cleanup reads back the four final records
before removing superseded implementation, repair, and generated history
reports. The final `delivery.json` records hashes and reasons for a retained
`planning-handoff.md` or `archive.md`. Unclassified artifacts and staged extras
block cleanup; cleanup never changes the Git index.

Ignore `/.p2p/` under the P2P convention. Setup detects conflicting repository,
local, and global ignores affecting project paths; report the actual conflict
rather than overriding unrelated rules.
Git does not retain empty directories. Setup creates them locally; their first
real files carry them into a checkout, so placeholder files are unnecessary.

Run exploratory checks, generated fixtures, dependency installs, and verbose
debug output in `.p2p/tmp/` or OS temporary directories. Before handoff, retain
the meaningful command, assertion, observation, and environment in the report.
Copy separate evidence only when the report cannot carry the required evidence,
such as replayable failure traces or host receipts checked during resume.
Retain those files selectively; do not archive entire scratch workspaces or
keep both an archive and its extracted contents. Reuse the candidate record's
recoverable snapshot instead of making extra stage-specific copies.
Never retain secrets in reports, snapshots, history, or logs. Redact
secret-bearing output before saving. For large, sensitive, or machine-specific
evidence, retain a description, safe durable reference, SHA-256 checksum, and
access limitations. Without a safe durable copy, mark evidence unavailable.
A checksum or inaccessible old temporary path alone is insufficient.

Execution storage uses an absolute, persistent directory outside the source
checkout. The default execution root is `~/.p2p/executions`; `P2P_EXECUTION_ROOT`
may choose another root for new work. All `~/.p2p/executions/<repo-id>/<slug>/`
paths below refer to the resolved root when configured. Resolve it with
`python3 <skill-dir>/scripts/p2p_filesystem.py --repo <root> execution-path <contract>`.
Before implementation, run `execution-access <contract>` with the same helper;
it probes actual write/read access and retains the absolute location in ignored
`.p2p/work/<slug>/execution-location.json`. Existing default executions and
retained locations take precedence over new configuration. Never relocate an
existing candidate merely because configuration or sandbox access changed.
Conflicting roots require reconciliation; do not overwrite either. Preserve
this receipt with recovery records, including after cleanup.

Before requesting publication approval, run `publication-access <contract>
--workspace <retained workspace>` with the helper. Probe from the actual
publication session, including the worktree, resolved Git directory and common
directory, objects, refs, and local records. `runtime/workspace/.git` points to
`runtime/repository.git`; worktree access alone does not permit a commit.
Record the checked paths in the preview and recheck on resume and before each publication effect.
A missing permission blocks the preview approval handoff. A user's publication
grant does not change the sandbox's writable roots. A later session must repeat
the checks because the delivery worker's permissions establish no publication
access for that session.

The outer `deliver-issue` workflow keeps its invocation record, fixed review
snapshot, reports, candidate payload, and scratch under
`~/.p2p/executions/<repo-id>/<slug>/orchestration/` while active or unresolved.
The `p2p_delivery.py` controller keeps its execution records, attempts,
prompts, events, receipts, reports, scratch, isolated Git workspace, and
candidate payload under the sibling `runtime/` directory. It keeps temporary
agreement snapshots under the sibling `agreement/` directory. Resolve
`<repo-id>` from the repository directory name and the first 16 hex characters of SHA-256
over the absolute Git common directory. Canonical contracts and
compact final records remain under `.p2p/work/<slug>/`; product files and large
execution artifacts stay outside the checkout. An unresolved delivery from
the legacy `~/.p2p/work/<repo-id>/<work-item>/` layout remains there until the
controller reconciles it; conflicting local and legacy roots block use.

After `REVIEWED_AND_PROVEN`, explicit cleanup verifies that the source checkout
still matches its admission identity, writes and reads back the durable records,
then removes attempt logs and scratch while retaining the isolated candidate
workspace and its Git objects outside the checkout for publication. It never applies the candidate to or
switches the operator's checkout. The current records replace prior records
without an extra history copy. The controller keeps any uncommitted prior
record bytes in ignored local recovery until replacement has been read back.
Versions already committed under legacy workflows remain in their existing Git
history; current P2P records never enter project Git history. A fresh checkout
still requires an explicit transfer of the ignored candidate workspace.

Before replacing a report, candidate, evidence, or uncommitted agreement,
retain its previous bytes in ignored
`.p2p/work/<slug>/history/<sha256>/<name>`. If exact old bytes already exist in
legacy Git history, keep that commit as an additional recovery source. Never
add P2P records to a new project commit. Preserve uncommitted versions in
`history/` before replacement.
Retain related evidence and snapshots so historical reports remain interpretable.
Rerunning the owning stage updates verdicts and identities. A manually edited
verdict does not establish acceptance. Acceptance is derived from matching
current reports, never from an authoritative `accepted: true` flag.

### Recover legacy committed records

Some legacy P2P records were already committed before the repo-local ignore
rule. Those old versions may be recovered from their existing commits for
historical inspection. Do not create new commits to archive current P2P records;
use explicit delivery cleanup to remove runtime data while retaining the final
records in ignored local storage. See [Reduce retained work
data](./how-to.md#reduce-retained-work-data).

## Candidate identity and resume

`candidate.json` identifies one fixed candidate and the exact agreement:

- `key`: the full candidate tree's `snapshot:sha256:<digest>` identity. A
  committed candidate may also retain `commit`, its full commit SHA.
- `changes`: compact base-relative rows with the changed path, state, type,
  mode, and content SHA-256. Deleted rows retain the removed entry's type,
  mode, and digest. Older records may retain a full `manifest` instead.
- `comparison_base`: full commit SHA, captured from the intended review base.
- `work_item` and `work_item_sha256`: canonical path and hash of exact file bytes.
- `binding_inputs`: repository paths and SHA-256 hashes of the binding local
  sources and parents, including their transitive sources and parents.

Use simple relative Markdown links on `Source:`, `Parent:`, or `Parent contract:` lines.
Capture additional binding documents referenced elsewhere explicitly as binding
links on these lines. Retain externally sourced binding text locally with its
attribution before capture; an external URL alone cannot establish its currency.
Historical copies in `.p2p/` identify previous agreements but are not live inputs.
The work item, binding inputs, and reports must all agree on these identities.

Exclude the entire `.p2p/` directory from candidate trees and snapshots. Capture
all relevant tracked, staged, unstaged, deleted, and untracked product content,
including executable modes and symlink targets. A compact record keeps the full
candidate key plus only changed path/mode/type/content digests relative to the
comparison base; it does not retain product payloads or unchanged paths. The
controller keeps its full execution workspace outside the checkout under
`~/.p2p/executions/<repo-id>/<slug>/` while a new run is active or unresolved,
then retains its isolated candidate workspace and Git objects after success.
An existing checkout-local runtime stays in place until its delivery is
reconciled. The outer workflow
keeps its invocation record, fixed review snapshot, reports, and scratch under
the sibling `orchestration/` directory. The Python controller keeps its stage
records, attempts, prompts, events, receipts, reports, and scratch under
`~/.p2p/executions/<repo-id>/<slug>/runtime/`. After `REVIEWED_AND_PROVEN`,
run explicit cleanup without applying the candidate to the source checkout.
Cleanup verifies the admitted source tree, reads back the durable records, and
prunes attempt logs and scratch while retaining the candidate at
`~/.p2p/executions/<repo-id>/<slug>/runtime/workspace` with its Git objects. The operator's
checkout stays unchanged. Resolve mixed staged and unstaged versions explicitly; the
helper rejects partially staged content or mode differences and unsupported
submodules instead of dropping inputs. Resolve those inputs before capture.
Isolate unrelated changes before capture without resetting, stashing, or
discarding the user's work.

A product candidate A can be followed by commit B that excludes `.p2p/` records.
Review and proof remain bound to A. To reuse them for B, compare the complete
tracked tree outside `.p2p/`, check relevant uncommitted content, and recheck the
exact work item, every binding input, and the requested comparison base. A
product or agreement difference invalidates reuse. A base change requires fresh
review and prevents claiming a matching pair under the old base. Do not replace
a report's candidate identity with `HEAD` merely because artifacts were committed.
If Git metadata affects the build, also establish execution-input equivalence
under the publication rules below.

Given only `.p2p/work/<slug>/contract.md`, resolve its source and parent links, children,
artifact directory, candidate, reports, and evidence. Recompute their identities
before reuse and resume the earliest incomplete or stale stage. Missing evidence
or recoverable candidate content is a blocked handoff, not a reason to infer
success from chat or file existence. A fresh checkout needs the ignored work-item
records copied from the local work root and candidate Git objects or a retained
snapshot. An authorized transfer must include them before the previous checkout
or temporary files are removed.

The dependency-free `scripts/p2p_filesystem.py` shipped with the skills implements
setup, path resolution, safe creation and replacement, candidate capture,
validation, and resume inventory. Read its `--help` for arguments. It checks
storage and identities, not evidence adequacy or approval, and never invokes
Git writes or external services. Stages still own their reports and verdicts.

## Pre-approval audit

`audit-acceptance` may independently inspect an exact proposed contract before
human approval. It reconciles every material source promise and contract row,
checks stable identities and revisions, and examines whether seams, oracles, and
evidence plans can establish the stated outcomes. An honestly marked evidence
gap may remain when the outcome is settled; an unresolved outcome decision does
not pass the audit.

The audit leaves the proposal and product files unchanged and is candidate-independent.
It saves its findings as `.p2p/work/<slug>/audit.md` under existing local authority. `READY_FOR_APPROVAL` means the
exact proposal is fit for a human approval decision, not that approval was
granted. Findings return to `plan-acceptance`, the sole contract author. The
auditor does not revise, save, approve, publish, implement, or prove the contract.

## Requirements and revisions

Each independently falsifiable promise has a stable ID such as `R1`. Input
variations belong in its boundaries. Existing GitHub acceptance checkboxes are
sources to reconcile with these rows, not a second checklist to duplicate.
A checked box is never acceptance evidence.

Reruns preserve IDs by matching the existing promises, not row order. New
requirements receive unused IDs. Splits and merges record the old-to-new mapping;
retired IDs remain recorded and are never reassigned to unrelated promises.
Never silently rewrite an existing requirement.

Contracts start with `Contract revision: v1`. An authorized change to a material
promise, boundary, expected outcome, or exclusion increments the revision.
Record the affected IDs, previous and new agreement, and authorization in a
change note. Preserve the prior revision so old proof remains interpretable.
New evidence, a changed test path, or wording that preserves meaning does not
increment the revision. A changed promise requires fresh proof.

`plan-acceptance` is the sole author of acceptance-contract revisions. Other skills
hand it amendments naming affected IDs, old and new agreement, and authorization.
The invoking workflow saves pending amendments in the source or links them
directly from it. Reconcile them through `plan-acceptance` before work that
depends on the changed promise. Storing its returned text does not authorize
rewriting it.

## Parent and child contracts

`slice-contract` owns decomposition, coverage allocation, dependency planning,
local child work items, and optional authorized ticket publication. It consumes an established parent contract;
`plan-acceptance` alone authors parent and child contracts and revisions.
Draft child criteria are source material for planning in the child work file.
The planner enriches that file in place; it does not create a second contract.
Slicing creates no extra specifications by default.
Small work can retain the direct contract, implementation, review, and proof path.

A sliced child records the parent's canonical location, revision, and exact text
as an immutable reference or retrievable captured text with a digest. Link the
canonical decomposition and record the child's precise contribution and
prerequisite outcomes. These references must be retrievable in a fresh checkout.
Use qualified obligations in durable cross-ticket references, for example
`.p2p/work/retry-safe-uploads/contract.md v2:R4`, or an unambiguous repository/source path, revision,
and ID for local work. Child IDs are local to the child contract. Its `R1` does
not mean parent `R1`; map each child row through its `Source` to the qualified
parent obligations it refines. Planning IDs such as `S1` are separate from both.

Judge a child by its own complete outcome and declared contribution, with all
applicable inherited boundaries, invariants, exclusions, and repository
constraints. The parent remains authoritative when a child omits or contradicts
them. Unrelated sibling functionality need not exist for child completion.
For obligations spanning slices, record each contribution, apply constraints to
every affected child, and name where the complete parent obligation will be
checked. A closed prerequisite ticket does not establish its required outcome;
the receiving workflow must confirm the needed artifact or behavior is available.

Consumers read the captured parent, current canonical agreement, source-linked
amendments, contribution mapping, and prerequisites. Capture applicable parent
identities with child reports and recheck them before handoff. If a material
parent change invalidates the mapping or inherited agreement, pause dependent
work and reconcile through `plan-acceptance` and the decomposition workflow.
Preserve prior snapshots and human edits. Regrouping unchanged promises changes
the plan, not the parent's semantic revision. Historical reports retain their
original meaning; they do not establish acceptance of a changed agreement.

Complete allocation is not acceptance evidence. Child proof evaluates the
child contract with its applicable inherited constraints. Final parent proof
evaluates every parent obligation, including interactions and shared invariants,
against one exact integrated candidate. Closed tickets and historical child
proofs do not compose into a parent verdict. Allocate actual integration work
to a named ticket when needed; ordinary parent-level `/prove` needs no separate
integration ticket. Existing review and merge conditions still apply.

## Epic delivery plans

`slice-contract` owns routing in `.p2p/work/<parent>/slicing.md`, alongside the
decomposition. Resolve that record through the child's existing Parent and
decomposition links. Unsliced work needs no plan. Do not copy destinations into
child contracts. Transfer the plan, its approval evidence, and retained history
with the work even though `.p2p/` stays outside product candidate identity.

Choose each child's destination by asking whether its complete intermediate
outcome would be acceptable at the final destination if the remaining children
never shipped. Existing flags can make that outcome acceptable. Dependencies,
release timing, hierarchy, and labels do not decide routing. Ask a focused
product-outcome question when intent is unclear.

The plan names the configured final destination, at most one integration branch,
a default choice of `independent` or `grouped`, and child exceptions. Resolve
`independent` to the final destination and `grouped` to the integration branch.
Mixed delivery is a default plus exceptions, not a third mode. Display each
child's resolved destination and reason, including which work can land first.

Keep exactly one `## Approved delivery plan` section in `slicing.md`. Its exact
UTF-8 bytes, from that heading through the byte before the next level-two heading
or EOF, identify the active decision. Use these fields and table so the existing
delivery controller can retain and check the same decision:

```markdown
## Approved delivery plan
Plan revision: v1
Approval source: <actual approval text and retrievable source>
Parent: .p2p/work/checkout/contract.md
Final destination: trunk
Integration branch: epic/checkout
Integration start: <full approved starting commit SHA>
Default choice: grouped

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
| .p2p/work/checkout-api/contract.md | independent | trunk | Useful without checkout. | remaining |
| .p2p/work/checkout-flow/contract.md | default | epic/checkout | Requires validation to be acceptable. | remaining |
| .p2p/work/checkout-validation/contract.md | default | epic/checkout | Completes checkout behavior. | remaining |

Parent completion: <contributions, interactions, inherited invariants and final integration checks>
Pending actions: <exact setup or strategy-change effects, authority, confirmed effects and unresolved state>
```

Use plain repository-relative child paths and branch names in the table. A row's
choice is `default`, `independent`, or `grouped`; its destination must agree with
that choice. Use `none` for both integration fields when no group exists. Retain
a confirmed final merge as `landed` with its historical destination and commit
reference. Future changes affect only remaining work. Approval must be explicit
and attributable. A label, saved draft, or heading is not approval evidence.

Save pending revisions under `## Proposed delivery plan`, leaving the active
approved section intact. Before activating an approved revision, retain the prior
file through the history rule. Retain referenced approval text and historical
plan bytes, not just a hash or vanished temporary path. Consumers record the
plan path, approved revision, SHA-256 of that exact section, and a recoverable
copy in their handoffs. Extract and hash the section as bytes with this same rule
used by routing, then retain `section` unchanged:

```python
data = path.read_bytes()
sections = re.findall(rb'^## Approved delivery plan\r?\n.*?(?=^## |\Z)', data, re.M | re.S)
assert len(sections) == 1
section = sections[0]
plan_sha256 = hashlib.sha256(section).hexdigest()
```

Include separators before the next heading and preserve CRLF, trailing spaces,
and EOF exactly. Do not trim, append a newline, or normalize the extracted text.
After saving a publication or readiness record, read back its retained section
bytes and hash and compare both with this extraction before claiming a handoff.
Use relative Markdown links for local approval receipts, such as
`[approval](approval.md)`. Existing bare `.md` paths in `Approval source:` are
resolved relative to the plan and retained without rewriting the approved text.
Missing referenced receipts block admission; changed or missing retained receipts
block resume before dispatch. Transfer these receipts and linked history together.
A pending proposal alone does not stale an active plan.
An affected destination or approved-plan change invalidates routing previews
without changing product candidate identity. Reconcile unchanged child routing
against the new plan before continuing; never treat old preview authority as
covering changed effects.

Normalize an older explicit, approved destination into this section without a
new strategy question. Preserve the original bytes, decision, and approval
source. Missing, conflicting, or proposed-only routing requires a focused
`/slice-contract <parent>` handoff before dependent work. Never infer a child's
destination from the default branch. An unresolved proposal does not override
an applicable approved decision.

Resolve routing before selecting an implementation starting point or comparison
base. For unsliced work, use an explicit workflow destination or one unambiguous
configured upstream. If neither resolves, block before dispatch without adding a
required destination argument. State the destination and unavailable prerequisite
outcomes. Confirm those outcomes in the actual candidate. Closed tickets do not
establish them. For a new delivery, resolve the intended target ref and record
its full tip SHA at admission. Require the requested base to match that tip.

Keep the admitted base fixed for the delivery. A later target move alone does not
invalidate the candidate, review, proof, or saved reports. Retain a separate
point-in-time destination observation with its tip, relationship to the frozen
base, and observation time. Classify it as `unchanged`, `fast-forward`,
`non-fast-forward`, or `unavailable`. For a direct review without an admitted
delivery, capture the target tip when review scope is established and keep that
scope fixed.
Changed candidate, agreement, approved routing, or adopted base still requires
fresh verification. Publication must inspect the current remote target when the
destination is remote.

If an integration branch is missing, name its approved starting SHA and the
specific local or remote creation needed. Planning changes no refs. A consuming
workflow may create only refs covered by existing explicit authority, then read
back their full SHAs. Reuse an existing ref only after confirming its approved
origin and any subsequent integrated changes. A same-name unrelated branch is a
conflict. Never overwrite it. An uncertain creation requires ref readback before
retrying. This is a handoff within existing skills, not a new user command.

Grouped child PRs target the integration branch directly and retain full child
review, proof, and publication obligations. Wait for prerequisites to be integrated
there, or use an existing explicitly approved shared-candidate exception with its
scope and verification intact. Grouping cannot make an incomplete child
publishable or permit unreviewed sibling payload. There is no stacked-PR path.
Required CI remains a readiness gate, not an unrelated proof or publication gate.

### Change an active strategy

Read the active plan, child work, reports, and known PR state. Preview old and new
destinations, reasons, affected children, exact branch or PR actions, and stale
verification. Keep unknown remote state unresolved. Preserve child identities,
contracts, dependency links, human edits, local candidates, and integration
history. Keep confirmed final merges recorded as landed. Unaffected children may
continue after their routing is reconciled. Saving a plan never changes a PR.

Independent delivery of previously integrated work requires a candidate containing
only the intended contribution and satisfied prerequisites. Inspect its full
diff against the final target for unfinished sibling work. Candidate extraction
or repair belongs to implementation; retargeting cannot repair scope.

Strategy approval and authority for branch creation, publication, retargeting,
and merging are distinct. Reuse unchanged grants within scope. A concrete grant
may approve a revision and listed effects together. Record confirmed effects and
outstanding actions after each step. Recheck current plan and relevant ref or PR
state immediately before each effect; reject a stale preview after concurrent
changes. Read back uncertain effects before retrying, preserving human changes
and avoiding duplicate branches or PRs. Ambiguity blocks further writes.

Destination-only changes do not revise acceptance contracts. A changed comparison
base requires fresh full review. Changed candidate content or binding agreements
require fresh full review and proof. Unchanged proof remains evidence only for
its exact candidate and agreement; it cannot manufacture a report pair for new
content. A changed product promise returns to `plan-acceptance`.

### Verify the assembled parent

Child completion, integration, and parent acceptance are separate events. Child
handoffs name remaining integration work and parent review and proof. Evaluate
all parent contributions, interactions, and inherited invariants on one exact
assembled candidate, including independently landed children and required
integration with the final destination. Closed issues, merge counts, green child
checks, and historical child proof do not establish parent acceptance. A failing
interaction leaves the parent unproven.

Publish a parent PR only after matching full parent review and proof. Final
readiness also requires the final destination's required CI and repository
approvals. Changed inputs require the ordinary verification refresh. When all
children land independently, verify the exact combined parent candidate without
creating an empty parent or integration PR. Readiness advice never grants merge
authority.

## Seams, oracles, and evidence plans

A seam is the highest meaningful public interface through which a requirement
can be observed. Reuse seams agreed in specification or TDD work. A consequential
new seam is an explicit design decision, not an implementation convenience.

An oracle is the independent source that determines whether an observation is
correct. Use the contract, a known-good example, or another independent source.
Copying production logic into the expected result is not an independent oracle.

Each row names its seam, oracle, and one primary evidence path:

- A behavioral test with a named case and an assertion of the promised outcome.
- An invariant with a named constraint or guard and a check that it prevents the
  counterexample through the relevant interface.
- An exact verification command and the condition its successful exit establishes.

`planned` means a credible, concrete path exists but has not established
acceptance. `gap` means the path, seam, or oracle is missing or inadequate.
Unresolved product decisions go in open questions, evidence limits in unresolved
gaps, and deliberate exclusions in out of scope. Planning does not run proof.

## Implementation and review handoffs

Implement the minimum complete solution inside the spec envelope. For every
requirement, reach the real observable outcome and implement the state,
invariant, and failure behavior it needs. Start evidence at the agreed public
seam. Prefer existing repository mechanisms and add machinery only where
correctness requires it. Preserve requirement IDs and promised outcomes.

`implement-contract` consumes the saved agreement and reports development work
for an exact candidate. `review-implementation` inspects a captured candidate against
the agreement, scope, and engineering obligations without repairing it. Neither
authors the contract, grants acceptance, or establishes merge readiness.
Specification, ticket slicing, and TDD may supply inputs without being required.

Implementation and review reports capture the canonical contract location,
revision, and exact text through an immutable reference or retrievable captured
text and digest. Capture the full candidate commit SHA or a reproducible snapshot
including relevant uncommitted and untracked files. A digest without recoverable
content is insufficient for transfer to another checkout. Review also preserves
the comparison base or merge base and included working-tree scope. Implementation
labels an unresolved review base instead of guessing it.

Save and reread reports under `.p2p/work/<slug>/`, outside the candidate
by definition. Mark storage pending only when saving or retrieval fails. A prior-session path alone is not a completed
handoff. Transfer the report and recoverable candidate when the next session uses
another checkout. Do not add another canonical contract store or require one
artifact per requirement.

Review findings use local IDs distinct from contract requirement IDs. Supported
corrections within the agreement go to an authorized `implement-contract`
invocation. Named gaps in a matching `NOT PROVEN` report go to `repair-gaps`.
Changed promises or consequential seam decisions return to `plan-acceptance`
through the source-linked amendment convention. These handoffs do not invoke
the next skill or grant publication authority.

Review and proof may run in either order or separately on the same fixed candidate.
Refresh review and any stale proof after candidate changes. Neither stage requires
an open PR or unrelated green CI. Only `prove` issues acceptance verdicts;
the existing merge conditions still apply.

## Proof and repair handoffs

Every proof run binds an exact contract revision to one exact candidate. Record
the full commit SHA or a reproducible snapshot covering relevant tracked and
untracked files. Preserve the exact contract text used, with an immutable
reference or captured content and digest, even when its revision did not change.
An issue number, branch name, or `HEAD` alone is not an exact identity.

Proof records each requirement's observation, independent oracle, durable
evidence reference, and verdict. Evidence references identify the assertion and
its saved output, artifact, or immutable run, with the command and environment
needed to interpret it. Checkbox state and green CI alone do not prove a ticket.

The saved proof report itself may contain the evidence: command, named assertion,
actual observation or relevant output, environment, and candidate identity.
Several requirements may reference the same report section or run. Separate
artifacts per requirement are unnecessary. Save the report outside the candidate
and provide a retrievable reference; a command without its result is not evidence.

- `proven`: credible evidence establishes the full requirement for this candidate.
- `disproven`: a concrete observation violates the requirement.
- `not proven`: evidence or identity is unavailable, weak, ambiguous, or inconclusive.

Overall `PROVEN` requires every material requirement to be proven, no unresolved
contract discrepancy, and unchanged candidate and contract throughout the run.
Otherwise the result is `NOT PROVEN`. Proof leaves product files and the
contract unchanged. Save its report and evidence under `.p2p/work/<slug>/`. Drift invalidates the
run rather than authorizing a repair during proof.

Repair means the smallest complete repair for the named requirements: narrow in
scope, complete in depth. Preserve valid checks and the contract. A repair never
silently weakens a promise or declares acceptance.

Any changed candidate requires fresh proof against all requirements before
acceptance. Prior proof describes only its original candidate. This includes CI
repairs that change product behavior, acceptance evidence, or relevant tests.
A green CI repair does not refresh proof automatically.

## Deterministic bundle inspection

After matching full `REVIEWED` and `PROVEN` reports exist for a reproducible
snapshot, an invoking workflow may normalize their normative claims into an
[acceptance bundle](./acceptance-bundle-v1.md). The checker recomputes exact
contract and candidate identities, checks complete requirement coverage,
resolves retained evidence, and rejects inconsistent decisions without another
model call.

The bundle is a derived inspection artifact, not another canonical contract or
report. A valid bundle does not establish evidence authenticity, evidence
adequacy, or merge readiness and does not create a new acceptance verdict.

## Pull-request publication handoff

`publish-pr` may prepare and, under exact publication authority, publish one
recoverable candidate with matching full `REVIEWED` and `PROVEN` reports as a
draft pull request. Its preview binds the candidate and agreement identities,
reports, destination, target and head refs, commit inputs, title, body, and
authorized commit, push, and pull-request effects. Changed inputs require a new
preview. Publication does not grant merge readiness or merge authority.

The model may invoke `publish-pr` to prepare its `DRAFT` preview without changing product files or remote state after
matching review and proof exist. Saving `.p2p/work/<slug>/publication.md` is a local report write, not a
publication effect. Model invocation grants no publication effect;
commit creation, push, and pull-request creation require the exact authority
bound by that preview.

Keep the review report's fixed comparison base A separate from the current
approved destination tip D. Require the same approved destination and classify
D as `unchanged` when D = A, or `fast-forward` when
`git merge-base --is-ancestor A D` succeeds. Either relation preserves the
candidate and report identities bound to C and A; ordinary fast-forward movement
alone does not require fresh full review. If A or D is unavailable, or D is not
a descendant of A, block publication with the observed condition. Do not replace
the frozen base, silently change routing, or transform the candidate.

The preview records A and D separately and says that saved acceptance evidence
does not establish compatibility with commits after A. Its draft body states
`Merge readiness: NOT ASSESSED`. Immediately before each publication effect,
re-read the destination and require its tip to equal the preview's D. Any drift
makes that preview and its exact authority stale. Prepare a new preview at the
latest tip; if it remains a descendant of A, retain the same C, agreement, and
report identities, then recheck a covering standing grant or obtain missing
exact authority for the changed preview before publishing. Merge readiness separately evaluates the actual current PR head and
target, compatibility and conflicts, report applicability, required CI,
repository approvals, and applicable rules.

The stable publication identity uses the candidate key to which review and proof
bind: `git:<full-object-id>` for a commit or
`snapshot:sha256:<64-lowercase-hex>` for a snapshot. Contract publication
identity uses SHA-256 of the exact canonical contract UTF-8 bytes with no text
normalization. A content-equivalent commit does not replace a report-bound
snapshot key.

When a snapshot needs a commit, create it in an isolated publication workspace
and compare its complete Git tree outside `.p2p/` with the captured candidate.
Exclude all `.p2p/**` records from the publication commit. If a durable handoff
is needed, use the separately authorized GitHub issue-record flow and verify its
readback; PR publication does not authorize an issue write. Record the exact
snapshot-to-commit mapping. A content-equivalent commit preserves candidate-bound
review and proof only when behaviorally relevant build and execution inputs are
unchanged or explicitly shown equivalent. These inputs include Git metadata when
the candidate reads it, generated artifacts, dependency resolution, timestamps,
signing inputs, and external build configuration. Record relevant inputs and
produced artifact digests. If publication changes a relevant input, rerun the
affected verification against the publishable artifact or return `BLOCKED`. Any
byte, path, mode, symlink, deletion, or included-fixture mismatch is a changed
candidate and cannot be published under those reports.
Persist and reread the created commit and mapping before remote effects. Resume
uses that retained commit; missing or conflicting mapping state blocks creating
a different publication commit from implicit Git metadata. If commit creation
already occurred but that required mapping cannot be established, publication is
`PARTIAL` even when no remote write began. `PARTIAL` consistently means an
authorized local or remote publication effect lacks required completion or
readback.

Push without force to one approved head branch and confirm the remote SHA before
creating a draft pull request. Use stable identity markers and readback to reuse
one exact existing effect after retries or lost responses. Conflicting refs,
ambiguous matches, or uncertain readback block repetition. Reread the pull
request and confirm its head, base, title, body, marker, and draft state before
reporting publication. Required CI, repository approvals, and merge policy remain
separate checks for `merge-readiness`.
