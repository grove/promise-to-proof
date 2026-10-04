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

Run the repository's default deterministic checks after functional changes:

```bash
python3 -c 'import sys; assert sys.version_info >= (3, 11), f"Python 3.11+ required; found {sys.version.split()[0]}"' &&
python3 -m unittest discover -s checks -p 'test_*.py'
```

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
- Active controller execution, candidate workspaces, reports, and recovery state
  live in the retained external execution root documented in
  `docs/p2p-delivery-controller.md`.
- Use the existing controller `status` and `resume` paths to recover active
  work. Do not reconstruct progress from chat history or create parallel state.
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
