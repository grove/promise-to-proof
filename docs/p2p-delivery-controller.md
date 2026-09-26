# Deliver a local work item with Codex CLI

The controller runs one established `work/<slug>.md` agreement on macOS with
Python 3.11 or newer, Git, and an authenticated Codex CLI. Install the
`implement-contract`, `review-implementation`, `prove`, and `repair-gaps` skills
in `~/.agents/skills/` or `$CODEX_HOME/skills/`. It inherits the configured OpenAI
model and reasoning preference. Other model providers are unsupported.

Run from this repository, replacing the work item, source repository, and full
comparison-base SHA:

```sh
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo /path/to/source run work/example.md --comparison-base FULL_SHA --authorize-local
```

`--authorize-local` grants scoped local agent stages and safe checks. The
controller copies the candidate into a persistent isolated workspace and leaves
the source checkout untouched. A successful result identifies that workspace's
recoverable candidate and matching full `REVIEWED` and `PROVEN` reports. Applying
the result to the source checkout or publishing it is a separate operation.

Dirty agreement inputs enter the candidate. Other dirty paths block admission.
Use repeated `--exclude-dirty relative/path` options only for work you explicitly
identify as unrelated. The controller records that inventory, uses comparison-base
bytes for those paths in its workspace, and rejects implementation changes to
them. It preserves original source bytes, executable modes, and symlink targets.
Partially staged paths must be resolved before admission.

Optional `--max-dispatches N` and `--max-seconds SECONDS` limit admissions. The two
live preflight sessions count as dispatches, as do failed or interrupted stages.
An ordinary delivery needs five dispatches; one repair and both fresh verifiers
need three more. Without these flags there is no user-selected limit. Resume
cannot widen the recorded limits or change the comparison base, scope, or authority.
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

Records live under `.p2p/work/<slug>/`. `delivery.json` contains the invocation,
reservations, usage, and precise blocker. `admission.json` retains its fixed
inputs and authority. `attempts/` retains each actual CLI command, safe prompt,
host JSON events, process completion receipt, and exact returned report.
`candidate.json` contains the recoverable candidate; `base-manifest.json` and
`runtime/base.bundle` retain comparison-base content and Git objects. The runtime
workspace and its separate Git metadata remain available for recovery.
`review.md`, `proof.md`, and `acceptance-bundle.json` expose the current completed
reports. Replaced records retain their previous bytes under `history/`.

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
