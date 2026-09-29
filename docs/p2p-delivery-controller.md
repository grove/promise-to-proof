# Deliver a local work item with Codex CLI

The controller runs one established `work/<slug>.md` agreement on macOS with
Python 3.11 or newer, Git, and an authenticated Codex CLI. Install the
`implement-contract`, `review-implementation`, `prove`, and `repair-gaps` skills
in `~/.agents/skills/` or `$CODEX_HOME/skills/`. It inherits the configured OpenAI
model and reasoning preference. Other model providers are unsupported.

Run from this repository, replacing the work item, source repository, and full
comparison-base SHA. For unsliced work, add `--destination BRANCH` when the
workflow has an explicit destination.

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source run work/example.md --comparison-base FULL_SHA --authorize-local
```

`--authorize-local` grants scoped local agent stages and safe checks. The
Python controller keeps its isolated Git workspace under
`~/.p2p/work/<repo-id>/<work-item>/` and its execution records, attempts,
launch prompts, events, receipts, reports, and runtime scratch under that work
item's `runtime/` directory, keyed by source repository and work item, outside
the source checkout. The outer `deliver-issue` workflow keeps its invocation
record, fixed review snapshot, reports, and scratch under the work root's
`orchestration/` directory. A successful
controller result identifies the workspace and matching full `REVIEWED` and
`PROVEN` reports. The controller leaves the source checkout untouched. Apply
the candidate to the source checkout yourself, then run the explicit cleanup
command:

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source cleanup work/example.md
```

Cleanup compares the complete source tree with the accepted candidate, reads
back the compact candidate identity and final review, proof, and delivery
records, then removes superseded implementation, repair, and generated history
reports. It records hashes and reasons for retained planning and archive
receipts, blocks on unclassified or staged extras, and removes the ignored
workspace only after another final-record readback. A mismatch keeps the
workspace. Cleanup does not apply, commit, publish, or merge code.

## Record an issue-backed delivery

For a contract imported from one GitHub issue, apply and commit the accepted
product candidate first. Preview the compact issue comment using the full
delivered commit SHA:

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source github-record-preview work/example.md --delivered-commit FULL_SHA
```

The JSON output contains the exact comment body and its SHA-256. Publication
requires an explicit grant for that preview hash:

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source github-record-publish work/example.md --delivered-commit FULL_SHA --authorize-comment-sha256 PREVIEW_SHA256
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

New invocations default to eight dispatches, 1,800 seconds overall, and 600 seconds
per stage. Override these defaults with `--max-dispatches N`, `--max-seconds SECONDS`,
and `--max-stage-seconds SECONDS` when the task needs a different allowance.
Limits must be finite and nonnegative; zero stops before dispatch. The two live
preflight sessions count as dispatches, as do failed or interrupted stages.
An ordinary delivery needs five dispatches; one repair and both fresh verifiers
need three more. Each stage stops at the earlier of its own deadline and the
overall deadline. These are execution guardrails, not promised completion times.
The overall deadline starts at admission after workspace setup; local setup,
identity checks, and record persistence are not subject to process termination.
Resume cannot widen the recorded limits or change the comparison base, scope,
or authority. Existing admissions keep their saved limits, including legacy
invocations with no deadline. New defaults do not retrofit a running process.
`--hard-cost-cap` always returns `BLOCKED` before dispatch because this host cannot
enforce a monetary ceiling. Recorded token usage is an observation; cost is unknown.
An elapsed-time deadline can terminate the local process, but provider work or
billing may continue after that deadline.

## Read progress and resume

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source status work/example.md
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source resume work/example.md
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
identity, and candidate generations live under
`~/.p2p/work/<repo-id>/<work-item>/`. Its delivery records, attempts,
acceptance bundle, stage commands, prompts, events, receipts, reports, and
runtime scratch live under that work item's `runtime/` directory. The outer
`deliver-issue` workflow keeps its fixed review snapshot, invocation record,
reports, and scratch under the work root's `orchestration/` directory. Retain
the work root while a run is active, blocked, interrupted, or uncertain. The controller reuses
local Git objects when Git can safely hard-link them.

After completion and explicit cleanup, `.p2p/work/<slug>/` retains only
`candidate.json`, `delivery.json`, `review.md`, and `proof.md` as generated
delivery records. `candidate.json` stores the exact candidate key and only
base-relative changed paths, modes, types, and content digests. The product
payload stays in the ignored workspace until the source checkout matches it.
Cleanup enforces six generated files and 65,536 logical bytes across the entire
work-item directory before writing the final set. Any previous uncommitted
completion records stay in ignored local recovery until readback succeeds. The
acceptance bundle is checked while the workspace is present and is deleted with
other run-only data.

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
