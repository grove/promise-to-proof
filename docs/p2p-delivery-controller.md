# Deliver a local work item with Codex CLI

The controller runs one established `.p2p/work/<slug>/contract.md` agreement on macOS with
Python 3.11 or newer, Git, and an authenticated Codex CLI. Install the
`implement-contract`, `review-implementation`, `prove`, and `repair-gaps` skills
in `~/.agents/skills/` or `$CODEX_HOME/skills/`. The controller packages its
autonomy, measurement and acceptance-bundle modules in its own `scripts/` directory;
it does not require this development repository after installation. It inherits
the configured OpenAI model and reasoning preference. Other model providers are unsupported.

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
the next repair must use a different executable approach. Confirmed unavailable
inputs or missing authority remain concrete blockers.

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

`status` reads and validates existing records without writing. `resume` continues
the same invocation. Repeating `run` with the exact original arguments also
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

The admitted comparison base remains fixed on resume. A destination move alone
does not invalidate reports or trigger another verifier run. `delivery.json` and
the public result retain a separate observation with the destination tip, its
relationship to the frozen base, and the observation time. A changed approved
plan still blocks resume. Successful completion means the exact candidate was
reviewed and proven against the frozen base. It does not establish compatibility
with the current destination.

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

## Host boundary and checks

Each invocation first launches two fresh real Codex contexts. They attempt writes
to protected candidate, agreement, binding inputs, comparison-base and controller
records through absolute paths, symlinks, and subprocesses. They also attempt a
numeric-IP network connection. Scratch writes must succeed and every protected
write and network attempt must be denied. The controller checks the actual command
output, original bytes, distinct host-issued session IDs, and completion receipts.

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
