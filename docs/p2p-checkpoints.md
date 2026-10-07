# Move P2P work between computers

P2P saves small, portable checkpoints at meaningful boundaries. `.p2p/` and
`~/.p2p/` are local working storage; neither directory needs to be copied to a
second computer after the checkpoint and its Git objects have been published.
The canonical rules are in the
[acceptance contract protocol](acceptance-contract-protocol.md#portable-checkpoints).

The default record is `p2p-state/<slug>.json`. It contains exact agreements,
approval receipts and referenced historical inputs, child scopes/dependencies,
routing, completed reports, compact host receipts, and the controller's next
stage, blocker, limits and effect receipts. Identical text is stored once.
Matching committed project documents are references to full commits and paths.
Candidate code is a Git commit reference, never an embedded repository snapshot.
Git retains checkpoint revisions instead of a second exported `history/` tree.

The record is capped at **256 KiB**. There are no prompts, conversation dumps,
ordinary logs, scratch directories or installed dependencies. Large essential
evidence must have a retrievable durable reference; a checksum alone does not
preserve it. Exceeding the budget reports a blocker and keeps local data intact.
The limit applies to the current checkpoint, not the project's accumulated Git
history or ordinary implementation code.

## Save and publish with Git

The installed filesystem helper is available with each P2P skill. Below,
`<helper>` means that skill's `scripts/p2p_filesystem.py`. Use Python 3.11+.
For controller checkpoints and delivery restoration, use the helper bundled with
`deliver-issue`, which also contains the controller needed to rebuild execution.
Planning saves refresh the checkpoint automatically; planning/slicing workflows
also refresh it after approval and before a handoff. The delivery controller
refreshes it after implementation, review, proof and completion.

```sh
python3 <helper> --repo /path/to/project checkpoint .p2p/work/example/contract.md
python3 <helper> --repo /path/to/project checkpoint-status .p2p/work/example/contract.md
```

`LOCAL_ONLY` means written and read back locally. `COMMITTED` means the exact
record exists in the current Git commit. Neither means backed up remotely.
Under explicit commit/push authority, commit `p2p-state/example.json` and publish
it normally. For unfinished controller work, the checkpoint's `candidate_commit`
is already imported into the operator repository's Git object database. Under
covering authority, retain it on an ordinary work branch and push that branch.
Do not put product payloads inside the JSON or force-push a branch.

```sh
python3 <helper> --repo /path/to/project checkpoint-status .p2p/work/example/contract.md --remote origin
```

This performs read-only remote inspection and local Git fetches. It checks current
remote branch tips, exact checkpoint bytes and reachability of every required
commit. Only verified readback returns `PORTABLE`. Fetches do not authorize a
push. A missing candidate branch, source commit or checkpoint blocks portability.
Excluded, uncommitted source changes can also prevent reconstructing the original
admission. Preserve and reconcile them before transfer; a candidate checkpoint
does not archive unrelated local work.

## Recover on another computer

Stop the controller on the old computer first. Clone/fetch the published record
and candidate branches on the receiving computer. Keep its source checkout at
the original admitted product tree; checkpoint-only commits do not change it.
The checkpoint records its exact `execution.source_recovery_commit` when Git can
reconstruct that tree. If another source commit is needed, preserve the exact
checkpoint while changing checkout; `git restore --source <checkpoint-branch>
-- p2p-state/<slug>.json` can retrieve the record again without changing product
files. Missing recovery commits block portability rather than losing local work.

```sh
python3 <helper> --repo /path/to/new-clone checkpoint-restore .p2p/work/example/contract.md
```

Restore validates hashes, Git objects, receipt/report bindings and all file
conflicts before writing. Differing local agreements, product documents or an
existing execution require reconciliation; restore never resets or overwrites
them. Planning restoration retains exact approval evidence without granting new
approval. Delivery restoration rebuilds an isolated local candidate and returns
the existing controller `resume` command. The comparison base, completed stage
identities and limits stay fixed. The receiving machine must have the same stage
skill versions and the currently supported macOS/Codex host; resume performs fresh
sandbox preflight before dispatching an incomplete stage. A transfer does not
restart a running agent or grant new publication/merge authority.

Uncertain or unreconciled dispatches cannot be exported as resumable boundaries.
Keep their local state and reconcile completion first. A failed checkpoint leaves
the previous record intact and is reported separately from acceptance. Old work
without a checkpoint still needs its original local recovery inputs.

## Use a GitHub issue instead

Select the issue before the first checkpoint. Git and GitHub are alternative
destinations, not synchronized sources of truth. An existing destination cannot
be silently changed. Issue checkpoints are cached under ignored `.p2p/`, not in
the tracked `p2p-state/` directory.
When creating a contract with the helper's `create --from ...` command, pass
`--github OWNER/REPO --issue 42` there to select its first checkpoint destination.

```sh
python3 <helper> --repo /path/to/project checkpoint .p2p/work/example/contract.md --github OWNER/REPO --issue 42
python3 <helper> --repo /path/to/project checkpoint-github-preview .p2p/work/example/contract.md
python3 <helper> --repo /path/to/project checkpoint-github-publish .p2p/work/example/contract.md --authorize-comment-sha256 EXACT_PREVIEW_BODY_SHA256
python3 <helper> --repo /path/to/project checkpoint-github-status .p2p/work/example/contract.md --remote origin
```

Publication uses one immutable comment per checkpoint, preserves prior versions
and human content, reuses an identical existing comment, and reads it back.
Ambiguous duplicates or uncertain writes block further publication. The issue
transport has a smaller **60,000-character** comment budget; larger records need
Git or smaller metadata. The preview authorizes neither posting nor approval of
its contents. Posting requires authority for that exact comment body hash.
`RECORDED` means the comment was read back; `PORTABLE` additionally requires its
referenced Git commits available on the selected remote's branches.

On the receiving machine, fetch the required Git branches, then select the exact
published checkpoint hash:

```sh
python3 <helper> --repo /path/to/new-clone checkpoint-github-restore --repository OWNER/REPO --issue 42 --sha256 EXACT_CHECKPOINT_SHA256
```

Use the checkpoint hash from publication, not the preview comment-body hash.
No issue label, mutable branch name, local absolute path, or chat summary can
substitute for the exact checkpoint and retrievable Git objects.
