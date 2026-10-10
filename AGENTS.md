# Promise to Proof agent map

Use this file as a router. Keep detailed protocol, workflow, and domain rules in
their canonical documents instead of copying them here.

## Start here

1. Read `README.md` for the product shape and repository layout.
2. Read the `SKILL.md` for the skill you are changing.
3. For planning, delivery, verification, publication, or resume behavior, read
   `docs/acceptance-contract-protocol.md`.
4. Follow `docs/agents/domain.md` before exploring domain-sensitive code. It
   points to `CONTEXT.md` and relevant ADRs when they exist.
5. Keep the change scoped to one agreed work item. Do not silently expand an
   implementation into adjacent cleanup, refactoring, or product behavior.

## User-facing behavior

Conversation behavior is product behavior. Keep technical rigor in the durable
records while user-facing replies use plain language and make the practical
meaning obvious. Be clear-eyed about uncertainty and downsides, opportunistic
about useful leverage, pragmatic about the smallest complete step, and proactive
about proposing a concrete response instead of stopping at diagnosis.

Do not use this working style to weaken contracts, bypass independent review or
proof, hide blockers, or expand authority. Prefer one obvious next action, and
keep hashes, IDs, report mechanics, and controller detail secondary unless they
matter to the user's decision or to diagnosing a problem.

## Where changes belong

- `skills/productivity/<skill>/SKILL.md`: agent-facing skill behavior.
- `skills/productivity/deliver-issue/scripts/`: delivery controller, storage,
  candidate identity, recovery, and host orchestration.
- `docs/acceptance-contract-protocol.md`: canonical agreement, identity,
  evidence, authority, and handoff rules.
- `docs/`: user-facing workflow and reference documentation.
- `checks/test_*.py`: deterministic regression and controller fixture tests.
- `checks/delivery-model/`: bounded model and controller-conformance checks.
- `checks/*-scenarios.md` and validation documents: retained scenario coverage
  and evidence expectations.
- `specs/` and `plans/`: project-owned requirements and planning material for
  this repository.

When changing a protocol rule, update its canonical definition first, then update
affected skills, checks, and user documentation. Do not create a second source of
truth for the same rule.

## Verification

During implementation and repair, run focused checks for the behavior being
changed. Once the candidate is ready, run the repository's default deterministic
suite once after the final functional changes:

```bash
python3 -c 'import sys; assert sys.version_info >= (3, 11), f"Python 3.11+ required; found {sys.version.split()[0]}"' &&
python3 -m unittest discover -s checks -p 'test_*.py'
```

Do not repeat this full suite after every intermediate edit or merely because
another stage needs a report. Repeat it when a later functional change invalidates
its result or a concrete material risk requires it. Independent review and proof
still inspect their own evidence and run the focused checks their conclusions
need. The default suite uses an explicitly offline fixture host and requires no
installed or authenticated Codex CLI; it is not live model or sandbox evidence.

Historical comparison fixtures also need Git revisions
`cc27a47f5ee765cff3cf13b21c36f974cb1234ae` (controller) and
`eb84d66dd70ce8998cd43e951741785e8520c301` (agreement). If a checkout lacks
either object, fetch that exact revision from `origin` before running the suite.

The controller uses `tomllib`, which is included in Python starting with 3.11.
Keep the version check when running the suite so an older `python3` fails before
the controller tests start.

For delivery-controller or filesystem changes, the focused checks are:

```bash
python3 checks/test_p2p_delivery.py
python3 checks/test_p2p_filesystem.py
python3 checks/test_verify_acceptance_bundle.py
```

For model/conformance changes, follow `checks/delivery-model/README.md`; those
checks have pinned tool and platform requirements.

For real host-boundary behavior, follow `docs/p2p-delivery-controller.md` and
run its live host check only with explicit authorization for real model calls.
Fixture transport tests are not live host evidence.

If a required check cannot run in the current environment, say exactly which
check was not run and why. Never treat an unavailable check as a pass.

## State and handoffs

Do not add `PROGRESS.md`, a feature-list file, or another checklist to mirror
P2P workflow state.

- Project-authored requirements stay in their existing project-owned source.
- The canonical P2P acceptance contract is
  `.p2p/work/<slug>/contract.md`.
- Generated project-local P2P records stay under ignored
  `.p2p/work/<slug>/`; compact completed delivery records live under its
  `artifacts/` directory.
- Portable checkpoints live at `p2p-state/<slug>.json` and may be committed under
  explicit authority. GitHub issue checkpoints are an alternative destination.
  Follow the canonical checkpoint protocol; raw local execution data stays ignored.
- Active controller execution, candidate workspaces, reports, and recovery state
  live in the retained external execution root documented in
  `docs/p2p-delivery-controller.md`.
- Use the existing controller `status` and `resume` paths to recover active
  work. Do not reconstruct progress from chat history or create parallel state.
  On another computer, restore the portable checkpoint before using those paths.
- Never commit generated `.p2p/` state.

The repository and retained P2P records are the handoff between agent sessions.
A fresh session should be able to recover the agreement, exact candidate
identity, verification state, blocker, and next supported action from those
records.

## Issue tracker

GitHub is an optional import and publication destination. Local planning,
delivery, and resume do not require it. Read `docs/agents/issue-tracker.md`
before tracker operations.

Remote writes require explicit authority. Importing or reading an issue does not
authorize comments, labels, publication, closing, or other GitHub mutations.

Use the default triage labels: `needs-triage`, `needs-info`,
`ready-for-agent`, `ready-for-human`, and `wontfix`. See
`docs/agents/triage-labels.md`.

## Domain docs

This is a single-context repo. Follow `docs/agents/domain.md` and use the
project's established vocabulary and ADRs when present.
