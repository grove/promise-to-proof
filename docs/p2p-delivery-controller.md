# Deliver a local work item with Codex CLI

The controller runs one established `.p2p/work/<slug>/contract.md` agreement on macOS with
Python 3.11 or newer, Git, and an authenticated Codex CLI. Install the
`implement-contract`, `review-implementation`, `prove`, and `repair-gaps` skills
in `~/.agents/skills/` or `$CODEX_HOME/skills/`. The controller packages its
autonomy, measurement and acceptance-bundle modules in its own `scripts/` directory;
it does not require this development repository after installation. It inherits
the configured OpenAI model and reasoning preference. Other model providers are unsupported.

At admission it preserves the stage skills and their material rule/protocol
dependencies. Stages read those snapshots, so a later installation update does
not silently change an active delivery. Use the
[instruction upgrade command](#upgrade-an-active-deliverys-instructions) to adopt
a compatible update without discarding completed implementation.

The execution root defaults to `~/.p2p/executions`. For new work, set
`P2P_EXECUTION_ROOT` to an absolute, persistent directory outside the source
checkout that the current session can write. For example:

```sh
export P2P_EXECUTION_ROOT=/absolute/writable/p2p-executions
python3 skills/productivity/deliver-issue/scripts/p2p_filesystem.py --repo /path/to/source execution-access .p2p/work/example/contract.md
```

The helper probes write/read access and saves the selected location in ignored
`.p2p/work/example/execution-location.json`. Resume and cleanup reuse that
location even if the environment changes. Existing default executions stay
where they are; changing configuration does not migrate a candidate. The
controller checks access before implementation and when resuming delivery.
Paths under `~/.p2p/executions` below use the retained root when configured.

Before publication approval, run the following in the publication session:

```sh
python3 skills/productivity/publish-pr/scripts/p2p_filesystem.py --repo /path/to/source publication-access .p2p/work/example/contract.md --workspace /retained/execution/runtime/workspace
```

The worktree and its actual Git directory must both be writable. The controller
uses a `.git` pointer to the sibling `runtime/repository.git`, whose index,
objects, and refs are required for commit creation. Local publication records
also need write access. If access is denied, resolve it before requesting effect
approval; approving publication cannot change sandbox permissions. Verification
workers still receive only their scoped writable scratch/workspace, so these
publication checks do not broaden stage access.

Run from this repository, replacing the work item, source repository, and full
comparison-base SHA. For unsliced work, add `--destination BRANCH` when the
workflow has an explicit destination.

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source run .p2p/work/example/contract.md --comparison-base FULL_SHA --authorize-local
```

`--authorize-local` grants scoped local stages, safe checks and source-preserving
local planning/recovery decisions; it grants no remote writes. The
Python controller keeps its isolated Git workspace and execution records under
`~/.p2p/executions/<repo-id>/<slug>/runtime/`, with temporary agreement copies
in the sibling `agreement/` directory. The outer `deliver-issue`
workflow keeps its invocation record, fixed review snapshot, reports, and
scratch under the sibling `orchestration/` directory. Canonical contracts and
compact final records stay under `.p2p/work/<slug>/`. An unresolved delivery
from the legacy `~/.p2p/work/<repo-id>/<work-item>/` layout stays there until
reconciliation. The repository ID is the repository directory name plus the
first 16 hex characters of SHA-256 over the absolute Git common directory.
An existing checkout-local runtime stays in place until that delivery is
reconciled.
A successful controller result identifies the isolated workspace and matching
full `REVIEWED` and `PROVEN` reports. Product files in the source checkout remain
untouched. The controller also writes a bounded portable checkpoint in
`p2p-state/<slug>.json`, or the selected ignored GitHub checkpoint cache.
Its `checkpoint` result distinguishes local preservation from remote portability.
See [portable checkpoints](p2p-checkpoints.md) for publication and recovery.
Run explicit cleanup without applying the candidate:

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source cleanup .p2p/work/example/contract.md
```

Cleanup verifies that the source tree still matches admission, reads back the
compact candidate identity and final review, proof, and delivery records, then
removes superseded reports and execution logs. It records hashes and reasons
for retained planning and archive receipts, blocks on unclassified or staged
extras, and keeps the isolated candidate workspace and Git objects under
`~/.p2p/executions/<repo-id>/<slug>/runtime/`, outside the checkout. Cleanup does not apply, commit, publish, or merge
code. It must save/read back the portable checkpoint before removing host
receipts. Neither a local checkpoint nor cleanup authorizes deleting both local
P2P roots; verify the published checkpoint and candidate commits first.

## Inspect a delivery record and landed-code mapping

Local `REVIEWED_AND_PROVEN` remains distinct from confirmed landed code. The
controller writes the existing
`promise-to-proof/delivery-record/v1` under
`.p2p/work/<slug>/artifacts/delivery.json` after cleanup. Its old
status and exact contract/candidate/report identities are unchanged. To
check it without new model calls or effects:

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_delivery_record.py \
  --repo /path/to/source validate .p2p/work/example/artifacts/delivery.json \
  --artifacts .p2p/work/example/artifacts
```

The same bundled helper can preview an optional `landing` extension after
a merge, squash, rebase or direct delivery has actually been observed. It
uses the exact existing #82 checkpoint, product-tree and target-commit
checks. It does **not** merge, push, record a remote receipt, or change
authority. It returns `LANDED_MAPPING_VERIFIED` for internally consistent
Git mapping, not a claim that remote publication/readback occurred.
The [authorized finalization workflow](finalization.md) consumes that
same record and the published #82 checkpoint to perform and verify exact
externally permitted effects. Local/source/spec delivery has no
automatic issue or PR requirement. See the
[Delivery Record v1 reference](delivery-record-v1.md) for exact preview and
validation commands and the stable retry identity.

## Record an issue-backed delivery

For a contract imported from one GitHub issue, use the isolated publication
workspace to create the approved product commit. Preview the compact issue
comment using the full delivered commit SHA:

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source github-record-preview .p2p/work/example/contract.md --delivered-commit FULL_SHA
```

The JSON output contains the exact comment body and its SHA-256. Publication
requires an explicit grant for that preview hash:

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source github-record-publish .p2p/work/example/contract.md --delivered-commit FULL_SHA --authorize-comment-sha256 PREVIEW_SHA256
```

The controller writes one comment only, reads it back exactly, and retains local
recovery state if the write is uncertain or conflicts with an existing record.
Issue-backed cleanup checks the comment again before deleting local execution
state. A fresh checkout with the delivered commit can inspect completed status
without prior P2P files:

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source github-status --repository OWNER/REPO --issue NUMBER
```

Status requires exactly one valid record and verifies its contract digest,
requirement coverage, frozen base, candidate tree, candidate changes, and
delivered commit against local Git history. It reports a blocker on missing,
duplicate, conflicting, or unavailable inputs.

For sliced work, resolve the approved plan through the child's Parent link before
running the controller. Use the resolved destination's current local tip for
`--comparison-base`. The controller starts from that destination tree, retains
the plan and history outside product identity, and binds the approved plan text
to stage inputs. It rejects a missing decision, conflicting base, missing ref,
or integration ref unrelated to the approved starting commit. An assembled
parent uses its own plan's final destination. For unsliced work, the controller
uses the explicit `--destination` when supplied. Otherwise, it resolves one
unambiguous upstream from the current branch. It blocks before dispatch if neither
is available. `--comparison-base` remains required and must equal the resolved
destination tip. The controller starts from that exact tree.

Use the ordinary delivery skill to normalize an explicitly approved older plan
or arrange missing branch setup under covering authority. The controller creates
no destination branch and infers no approval. On resume, an approved-plan change
or missing transferred plan evidence blocks further dispatch. A target advance
alone does not. A pending proposal leaves the active decision applicable.
Preserve the prior run and reconcile changed routing before a new delivery.

Dirty agreement inputs enter the candidate. Other dirty paths block admission.
Use repeated `--exclude-dirty relative/path` options only for work you explicitly
identify as unrelated. The controller records that inventory, uses comparison-base
bytes for those paths in its workspace, and rejects implementation changes to
them. It preserves original source bytes, executable modes, and symlink targets.
Partially staged paths must be resolved before admission.

New invocations default to unlimited overall duration, stage duration, dispatches
and repairs. State uses JSON `null` and no synthetic deadline. Optional
`--max-dispatches N`, `--max-seconds SECONDS`, `--max-stage-seconds SECONDS`
and `--max-repairs N` impose explicit nonnegative limits; `unlimited`, `infinite`,
`inf` and `null` mean no limit. Zero stops at the corresponding boundary.
Failed stages and preflights count as dispatches. Both independent verifiers run
again after each recovery. Repeated gaps invoke a fresh read-only diagnosis;
the next repair must use a materially different executable approach, supported
by a successful safe capability check in its host receipt. Different wording
alone does not establish a new method. Diagnosis uses the latest partial repair
gaps and the retained approach history, including on resume. Worker permissions
and available tools must cover its proposed next step; unavailable host tools,
inputs or missing authority remain concrete blockers for the enclosing workflow.

Repetition detection uses named obligations and candidate history as well as exact
finding text. Rewording the same requirement/location or cycling back to an earlier
candidate triggers diagnosis. Repeating an exhausted method with the same
capability observation is not a new strategy. A partial repair that changes the
candidate and strictly reduces explicitly named remaining requirement IDs can
continue without another diagnostic model call; vague or unchanged gaps still
need diagnosis.

After a repair, each verifier receives its own latest compatible observations and
the complete delta between exact candidate generations. It independently decides
which evidence still applies and runs fresh affected checks. Both reports still
cover the whole agreement. This makes focused re-verification executable without
sharing the other verifier's verdict or automatically accepting cached results.

`--worker-idle-seconds SECONDS` optionally detects idle event/error logs, stops
the process group, saves its exit receipt and replaces that worker. Partial
candidate generations and retired attempts remain recoverable. Activity alone
is not proof of useful progress. No watchdog is imposed by default. A reserved
launch without a confirmed exit stays uncertain and is never blindly duplicated.

Saved invocations keep their original limits. To apply an explicitly requested
extension without resetting history:

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source extend .p2p/work/example/contract.md --authorize-extension --max-seconds unlimited --max-stage-seconds unlimited --max-dispatches unlimited --max-repairs unlimited
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source resume .p2p/work/example/contract.md
```

An extension retains old limits, elapsed observations, consumed attempts and the
same base. `--mandate FILE` on extension can explicitly adopt standing authority.
Legacy local-only invocations acquire the source-preserving local mandate on
explicit extension; no remote effects are granted. A finite elapsed extension
supplies a new remaining interval from extension time;
dispatch/repair limits remain total counts, not additional allowances.

### Standing mandates

`--authorize-local` delegates source-preserving local planning, sizing, routing,
implementation, evidence and repair. It grants no remote effects. For selected
standing authority, pass `--mandate /absolute/path/mandate.json` at admission:

```json
{
  "schema": "promise-to-proof/autonomy/v1",
  "objective": "Deliver the agreed feature and open its draft PR",
  "constraints": ["Preserve the source promises and exclusions"],
  "decisions": ["planning", "sizing", "routing", "implementation", "evidence", "repair"],
  "effects": [
    {"action": "commit", "repository": "OWNER/REPO", "destination": "feature/example"},
    {"action": "push", "repository": "OWNER/REPO", "destination": "feature/example"},
    {"action": "pr-create", "repository": "OWNER/REPO", "destination": "main"}
  ],
  "approval_source": "User instruction granting these actions and destinations"
}
```

Select the file through actual user authority; its `approval_source` is attribution,
not a self-issued grant. The controller records exact bytes/hash and refuses a
changed file. Only granted decision types may be applied. Source-preserving
replanning runs separate planner/auditor sessions, retains the prior revision,
then reruns implementation and both verifiers. Requirement IDs and binding links
cannot be removed. Existing product changes cannot be approved by changing prose.

Before effects, save/reread the complete preview and check each grant:

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source authorize-effect .p2p/work/example/contract.md --action push --repository OWNER/REPO --destination feature/example --preview-sha256 FULL_PREVIEW_SHA256
```

This command is read-only and returns the exact preview hash, candidate and
covering mandate. Product publication effects require current full matching
review and proof. Scope checks do not replace publication/readiness/readback
conditions. Exact destinations are branch names for commit/push/branch-create,
target branches for pr-create, exact issue/PR URLs for edits/comments/readiness/
merge, the repository URL for issue-create, and a named environment for deploy.
No wildcard or force-push grant is accepted. The outer workflow executes these
steps; the Python controller runs local stages and the compact issue-comment
publisher. A covering `issue-comment` grant permits `github-record-publish`
without another `--authorize-comment-sha256` approval; the exact preview is still
created and checked immediately before writing.

`--hard-cost-cap` always returns `BLOCKED` before dispatch because this host cannot
enforce a monetary ceiling. Recorded token usage is an observation; cost is unknown.
An elapsed-time deadline can terminate the local process, but provider work or
billing may continue after that deadline.

## Read progress and resume

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source status .p2p/work/example/contract.md
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source resume .p2p/work/example/contract.md
```

`status` reads and validates existing records without writing. It places
`human_progress` **first** in the JSON response: a deterministic account of
what happened, why it matters, the work's actual location, whether a decision
is required, and the next supported action. All original raw fields remain.
For a readable terminal paragraph, or to inspect an exact known PR:

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source status .p2p/work/example/contract.md --human
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source status .p2p/work/example/contract.md --pr https://github.com/OWNER/REPO/pull/123 --human
```

The optional PR lookup uses read-only GitHub CLI readback and verifies the
current PR head's complete product tree, destination branch and stable
contract/candidate publication identity before claiming a publication or
merge. One unambiguous saved PR URL in `publication.md` may supply a lookup
hint; a note alone never establishes publication. If GitHub access or the
candidate's exact Git objects are unavailable, the external effect stays
**unconfirmed**. An open PR is not merged; a verified merge is not a
completed-delivery receipt until the separately planned #50/#47 finalization
is implemented. A local accepted candidate remains in the isolated workspace
and does not modify the operator checkout.

A restored checkpoint carries earlier evidence but does not prove that a
worker is active or the receiving host's preflight passed. When host
initialization fails, `human_progress` names the blocker and preserved
work rather than claiming implementation, review, or proof ran. The
independent audit's `READY_FOR_APPROVAL` is not human approval.
`resume` continues the same invocation. Repeating `run` with the exact original arguments also
resumes it. A changed argument blocks instead of creating a new repair allowance.
One exclusive lock covers admission, dispatch, and result persistence.

Stage starts, periodic activity updates, and finishes go to standard error.
Standard output remains one JSON result. The result's progress information names
the latest stage, its elapsed time and deadline, and the last host-log activity.
It also reports whether a controller holds the work-item lock. During active
implementation or repair, candidate validation is marked pending because the
worker is editing it. Agreement and source checks still apply. Once the worker
finishes, ordinary candidate validation is required before acceptance.
Log activity establishes neither useful progress nor successful completion.
Use the retained events to distinguish new observations from repeated checks.
A timeout names the interrupted stage and retains its candidate workspace, event
log, and process receipt. Resume does not repeat that uncertain or failed stage.

A finished worker with an invalid report is recorded as a terminal rejected
response, with the exact bytes and validation error retained. It is not left
reserved. Invalid mutating output preserves the partial candidate without marking
implementation complete. A malformed read-only diagnosis gets at most one
format-only correction for its unchanged context; stale identities, missing
capability evidence and uncertain exits still block. Resume consumes an already
valid retained diagnosis instead of launching another diagnosis or restarting
implementation.

The admitted comparison base remains fixed on resume. A destination move alone
does not invalidate reports or trigger another verifier run. `delivery.json` and
the public result retain a separate observation with the destination tip, its
relationship to the frozen base, and the observation time. A changed approved
plan still blocks resume. Successful completion means the exact candidate was
reviewed and proven against the frozen base. It does not establish compatibility
with the current destination.

## Upgrade an active delivery's instructions

Install the desired P2P version, then preview its effect on the retained delivery:

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source upgrade-instructions .p2p/work/example/contract.md
```

The preview is read-only. It identifies the preserved and proposed instruction
sets, changed inputs and compatibility, and explains which verification becomes
historical. Ordinary `resume` continues with the preserved instructions even
when the installation has changed.

When the user has requested the compatible upgrade and the current mandate
covers local implementation and evidence decisions, adopt it and continue:

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source upgrade-instructions .p2p/work/example/contract.md --authorize-upgrade
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source resume .p2p/work/example/contract.md
```

Adoption performs no model call. It preserves the exact contract, binding inputs,
candidate, frozen base, source checkout, routing, completed implementation,
attempts, recovery history, mandate and existing limits/deadlines. New independent
review and proof contexts use the updated instructions and assess the retained
candidate. They make fresh observations under the changed instructions, using
the smallest sufficient checks and issuing their own reports. An unchanged
agreement and host retain valid readiness observations, so this local update
does not repeat host preflight. Implementation runs
again only when a material finding needs a repair. Old reports and their exact
instruction identities remain historical evidence.

Selecting the already-effective instruction set changes nothing and launches
no worker. If adoption is interrupted, run ordinary `resume`: its retained
transition is reconciled once without resetting counters or duplicating stages.
This operation adds no time or attempt allowance; explicitly requested limit
extensions still use `extend` separately.

| If adoption is blocked | Next action |
|---|---|
| A worker is still running or its exit is uncertain | Keep its records and establish completion through the existing recovery path. A known finished worker is reconciled under its original inputs before adoption. |
| A required old instruction snapshot is missing | Recover the exact retained input. For legacy work without snapshots, recover the original installation/version and use its existing resume path. |
| The installed instructions declare incompatible delivery meanings | Install a compatible version. Do not edit compatibility metadata to force adoption. |
| The requested upgrade or covering local authority is missing | Obtain the specific missing grant, preserving the existing delivery and preview. |

The compatibility family covers agreement, candidate, authority and stage-report
meanings. Skill and rule authors must retain material dependency declarations;
the [canonical instruction rules](acceptance-contract-protocol.md#delivery-instruction-identity-and-upgrades)
define that boundary. Neither a matching family nor faster checking can weaken
the accepted outcome, independent verification or authority requirements.

Checkpoint restoration uses the same mechanism: it restores pinned instructions
by default, or adopts the compatible installation when both
`--upgrade-instructions --authorize-upgrade` are explicitly selected. See
[moving work between computers](p2p-checkpoints.md#recover-on-another-computer).
The supported live controller remains macOS with Codex CLI. Deterministic fixture
checks establish state preservation and dispatch behavior, not measured model
delivery times or a live host upgrade result.

## Check target movement

`checks/test_p2p_delivery.py` keeps the required movement cases distinct:

| Case | Assertion |
|---|---|
| T1 | `test_child_stale_admission_blocks_but_target_advance_after_admission_is_observational` rejects the old base before dispatch. |
| T2 | The same test admits at A, moves the target to B, and completes against A. |
| T3 | `test_movement_during_implementation_review_and_proof_keeps_all_bindings_fixed` moves the target while stages run. |
| T4 | `test_target_advance_after_reports_return_does_not_refresh_verifiers` moves it after reports return. |
| T5 | `test_fresh_process_resumes_missing_stages_after_target_advance` resumes in a new process against A. |
| T6 and T7 | `test_non_fast_forward_and_missing_destination_do_not_invalidate_acceptance` records non-fast-forward and unavailable observations. |
| T8 | `test_parent_uses_final_destination_and_plan_loss_blocks_resume` keeps approved-plan loss as a blocker. |
| T9 and T10 | `test_agreement_and_candidate_drift` and `test_source_agreement_binding_base_and_report_loss` retain integrity blockers while the target moves. |
| T11 | `test_repeated_run_cannot_replace_frozen_base_after_target_moves` blocks base replacement; `test_adopting_new_base_uses_new_candidate_and_fresh_report_bindings` checks a new delivery at B. |
| T12 | `test_busy_destination_moves_repeatedly_without_refreshing_completed_stages` completes after repeated target moves. |

Run the controller suite to exercise these assertions. The result records the
frozen SHA separately from each observed destination tip.

The Python controller's active workspace, Git metadata, comparison-base
identity, candidate generations, delivery records, attempts, acceptance
bundle, prompts, receipts, and runtime scratch live under
`~/.p2p/executions/<repo-id>/<slug>/runtime/`. The outer `deliver-issue`
workflow keeps its fixed review snapshot, invocation record, reports, and
scratch under the sibling `orchestration/` directory. Retain that external work
root while a run is active,
blocked, interrupted, or uncertain. The controller fetches only the exact
comparison base and reuses local Git objects across candidate generations.

After completion and explicit cleanup, `.p2p/work/<slug>/artifacts/` retains
`candidate.json`, `delivery.json`, `review.md`, and `proof.md` as generated
delivery records. `candidate.json` stores the exact candidate key and only
base-relative changed paths, modes, types, and content digests. The product
payload stays in the isolated external workspace for publication while the
source checkout remains unchanged. Cleanup enforces the generated-record
footprint before writing the final set. Any previous uncommitted completion
records stay in ignored local recovery until readback succeeds. The acceptance
bundle and other execution logs are deleted after final readback.

A reserved attempt with an unambiguous saved process completion is reconciled
without rerunning it. Missing launch/completion evidence returns `BLOCKED` and
names the exact missing record. Preserve the directory and investigate that
attempt. Never delete a reservation to retry it. A completed implementation
followed by interrupted candidate capture can block on changed candidate bytes;
the controller preserves those bytes instead of guessing whether to repeat work.

Exit zero means the current candidate has both full matching reports with
retrievable evidence. Other completed commands return JSON with `BLOCKED`, the
specific cause, identities available so far, retained progress, and a resume
command. A stage's exit zero alone cannot establish delivery.

## Where each promise is implemented and what review actually covered

New deliveries retain a small `coverage_trace` in their existing stage reports.
Each requirement points to actual product files or sufficient unchanged behavior
and to retained observations, checks, exact candidate files or existing
[Evidence Record v1](./evidence-record-v1.md) references. Necessary supporting
changes have a short justification. The controller checks the references and
records the exact inspected product paths, blob/mode identities, frozen base,
candidate key and local Git generation in the saved review scope. This is not a
new agent or proof stage.

To compare an already-reviewed candidate against a PR checkout or another exact
product tree, run this **read-only** command:

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_filesystem.py --repo /path/to/source \
  review-scope-status .p2p/work/example/contract.md \
  --current-repo /path/to/pr-checkout
```

Use `--current-ref FULL_SHA` to inspect a specific Git revision instead of the
checked-out working tree. `COVERED` means product bytes match the saved review;
`UNCOVERED_DELTA` names the exact changed, added or deleted files; `UNKNOWN`
means the saved scope or original candidate is unavailable and requires a fresh
inspection. A missing scope in historical reports is not silently inferred from a
changed-file count. The command cannot confer review, proof or merge approval:
a known narrow delta still needs targeted independent inspection and fresh
current-candidate verification, while an unchanged candidate still needs a
current-target compatibility check.

## Risk-driven checks for changed seams and moving targets

The existing stage reports now retain an optional compact material-risk
mapping alongside #41 requirement coverage. Each applicable item identifies
requirements, touched code/dependency paths, a realistic trigger, why it
matters, an observation/check and its resolved or unresolved status. Low-risk
changes can legitimately have no additional risk items. A risk that remains
materially unresolved cannot appear as successfully addressed by a current
stage. These facts are checked for real references and retained in the existing
review/delivery records; there is no extra actor or assessment stage.

When a PR target advances, use the frozen review base and exact PR-head/target
commits to identify only relevant *additional* compatibility checks:

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_filesystem.py \
  --repo /path/to/source \
  target-risk-status .p2p/work/example/contract.md \
  --destination-repo /path/to/checkout-with-required-git-objects \
  --head-ref FULL_PR_HEAD_SHA --destination-ref FULL_TARGET_SHA
```

`TARGETED_CHECKS_REQUIRED` names changed paths intersecting saved seams;
`NO_ADDITIONAL_RISK_CHECKS` means there is no extra check from the recorded
dependencies, not that merge readiness has passed. `UNKNOWN` reports
missing history, non-fast-forward target movement, or a different PR head.
A known direct intersection merits focused current-head/target verification;
uncertain reach merits broader checking. Ordinary exact-pair CI, current
target compatibility, review/proof identities and merge authority remain
separate mandatory decisions. The CLI is read-only and returns nonzero when
more checks or a resolution are needed.

The [live judgment fixtures](../checks/fixtures/live-judgments/README.md)
include a low-risk control and durable booking scenarios with an independent
public-CLI restart and competing-process oracle. Offline fixture checks
establish only runner/trace behavior, not live model quality.

## Host boundary and checks

Each invocation first launches two fresh real Codex contexts. They attempt writes
to protected candidate, agreement, binding inputs, comparison-base and controller
records through absolute paths, symlinks, and subprocesses. They also attempt a
numeric-IP network connection. Scratch writes must succeed and every protected
write and network attempt must be denied. The controller checks the actual command
output, original bytes, distinct host-issued session IDs, and completion receipts.

The second context also checks task readiness using the actual worker permissions.
It inspects only pre-existing tools, evidence inputs, runtimes and services needed
by the accepted task. Each reported check must match a command and observation in
the host receipt. Missing required evidence or a denied service/socket blocks
before implementation with the exact missing input and expected result. The
feature being built is not a prerequisite, and readiness does not run a full test
suite. This uses the existing two contexts, without another initial model call.
An applicable successful check is reused across ordinary repairs; a resolved
blocker or changed agreement/host refreshes the affected readiness. A retained
boundary-only invocation receives one second-context readiness refresh.

Implementation can write only its isolated workspace. Its Git metadata is outside
that writable root. Review and proof receive the fixed candidate outside their
writable scratch directories. Configuration ignores user config and exec rules,
disables apps, plugins, MCP servers, web/browser/computer tools, hooks, and approval
escalation, and denies shell network access. Default temporary roots are excluded;
`TMPDIR` is set inside authorized scratch. Provider access needed by Codex remains
available. Safe checks may create Git fixture repositories in scratch. Source and
delivered Git refs/index remain protected. The controller and OS are trusted;
these controls do not claim protection against arbitrary same-user host tampering.

Run deterministic fixture tests:

```sh
python3 checks/test_p2p_delivery.py
python3 checks/test_p2p_filesystem.py
python3 checks/test_verify_acceptance_bundle.py
```

Run the real host check in a **new** output directory. This authorizes real model
calls and local disposable fixture setup:

```sh
python3 checks/check_p2p_delivery_host.py --output-dir /path/to/new-live-evidence
```

The host check creates a tiny repository whose contract requires `greet.py` to
print `hello` and exit zero. The public controller runs real implementation,
independent review, and independent proof stages. The check retains exact executed
file hashes, all host receipts, protected-write results, reports, evidence, source
and candidate content. Fixture transport tests establish controller decisions;
they are never treated as live host isolation or independent stage evidence.

### Independently known live review/proof outcomes

The end-to-end tiny-host check above verifies isolation and basic completion; it
is not a quality regression gate for review/proof *judgments*. The independent
fixture suite exercises correct behavior, missing whitespace validation despite
green supplied tests, unrelated scope expansion, optional polish, and a follow-up
edit that invalidates an earlier outcome. Expected outcomes and private CLI oracles
stay outside the candidate workspace and are never supplied to model stages.

Run on an explicitly authorized supported **macOS + authenticated Codex CLI** host:

```sh
python3 checks/check_p2p_judgments_host.py --output-dir /path/to/new-live-judgment-evidence
```

Each case retains its exact contract, candidate generations, pinned instructions,
real review/proof host events and receipts, stage reports, external public-interface
oracle observations, and expected-versus-observed results. The aggregate exits
nonzero on any disagreement. For a narrow diagnostic rerun, use `--only CASE_ID`
and a new output directory. The tests in `checks/test_live_judgments.py` are
specifically labeled **offline**; they validate setup and the harness without
claiming live model judgments. See the
[fixture guide](../checks/fixtures/live-judgments/README.md) for cases and limits.



## Delivery measurements

Every controller result includes one versioned measurement keyed by the invocation
ID. It records the canonical repository ID, admitted work item, contract revision
and hash, frozen base,
candidate identity when available, host/model configuration, unique attempt IDs,
terminal outcome, dispatch/resume/repair counts, preflight usage, and stage
intervals. Episode elapsed time is measured from controller invocation entry;
setup before the execution deadline is shown separately. Stage durations remain
separate and are not added to episode elapsed time.

Controller wall time excludes the union of complete host-launch intervals and is
unavailable if any launch boundary is missing or incoherent. The reservation
timestamp remains the admission/deadline boundary; launch intervals begin after
dispatch preparation and are recorded separately in the host receipt. Summed
attempt seconds may exceed wall time when attempts overlap. The controller
breakdown reports setup/admission, identity/snapshot/validation, and state
persistence/readback, with preflight host-check attempts shown separately. These
descriptive buckets can overlap and must not be summed.

Provider input, output, cached, reasoning, and other numeric usage are kept in
separate fields. A missing value is null (unavailable), never zero. The record
contains identities and measurements only; it omits prompts, responses, logs,
and product source. It is an observation of this host and configuration, not an
assurance claim, a price, or a measure of human effort.

Retention is opt-in. While the invocation record is available, explicitly export
one compact record to a new caller-selected file:

    python3 checks/export_p2p_delivery_measurement.py --repo . --work .p2p/work/example/contract.md --output /path/to/new-measurement.json

The command refuses to replace an existing file. Ordinary cleanup does not need
an export and removes temporary attempt telemetry with the rest of runtime data.
To compare retained records, combine them into an export document and run
python3 checks/compare_p2p_delivery_measurements.py measurements.json.
The report groups only matching work item, contract revision/hash, and comparison
base, discloses host/model/tool configuration differences, and leaves unavailable
metrics unknown. Independent correctness outcomes may be supplied in the separate
independent_adjudications input; controller verdicts are never used as ground
truth. Time and token observations do not estimate monetary cost or human effort,
and do not create numeric priority scores.
