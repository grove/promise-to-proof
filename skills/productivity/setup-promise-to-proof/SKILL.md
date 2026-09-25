---
name: setup-promise-to-proof
description: Set up a repository's issue tracker, triage labels, and domain-doc pointers for Promise to Proof skills.
disable-model-invocation: true
---

# Set up Promise to Proof

Configure the repository where the skills will run, not the skill collection's
source repository. This is an interactive local setup: inspect, propose exact
files, obtain approval, then write. Do not create tracker issues or labels,
change remotes, or create domain documents during setup.

## Inspect the repository

Read existing `AGENTS.md` or `CLAUDE.md`, `docs/agents/`, Git remotes, and any
existing issue or label conventions. Look for `CONTEXT.md`, `CONTEXT-MAP.md`,
and relevant ADR locations. When possible, inspect the destination's existing
GitHub labels with `gh` before proposing a mapping. Keep existing configuration
and human edits; a rerun must not replace them with defaults.

## Choose the configuration

- **Issue tracker:** These skills publish and triage GitHub issues. Confirm the
  target GitHub repository from the remote or ask for it when ambiguous. Draft
  `docs/agents/issue-tracker.md` with the destination, how to read, search,
  create, edit, label, and verify issues using `gh`, and whether PRs count as
  incoming requests (default: no). If the project uses another tracker, report
  that its tracker-writing skills are not ready; do not claim that a generic
  tracker configuration makes the GitHub-specific skills work.
- **Triage labels:** Draft `docs/agents/triage-labels.md` mapping the five roles
  `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and
  `wontfix` to actual destination label strings. Recommend identical names when
  the project has no mapping; confirm overrides before writing. A file alone
  does not create labels in GitHub: report missing labels separately.
- **Domain docs:** Draft `docs/agents/domain.md` describing where to find the
  project's glossary/context and architectural decisions. Use the existing
  layout, or propose root `CONTEXT.md` and `docs/adr/` for a single-context
  project. Treat absent domain files as optional; do not create placeholder
  `CONTEXT.md`, `CONTEXT-MAP.md`, or ADRs.

Present the proposed contents of each new or changed file and the supporting
findings before editing. Ask for confirmation of the destination, labels,
domain layout, and exact local edits; unresolved choices stay pending.

## Write and verify

After approval, create or update only the approved `docs/agents/` files. Add
short pointers to them under `## Agent skills` in an existing `AGENTS.md` or
`CLAUDE.md`; if both exist, confirm which is authoritative. If neither exists,
ask whether to create `AGENTS.md`. Preserve other instructions and update
existing pointers in place instead of appending duplicates. Point only to
files actually written.

Read back each changed file and check the pointers, destination, and all five
label mappings. Report what was configured, any missing labels or unsupported
tracker, and what still needs a decision. A repeat invocation with unchanged
answers should leave the files unchanged.

End with `Next steps:` and a numbered list (`1.`, `2.`, ...) of applicable
actions in order, so each can be referenced by number. If approval is pending,
name the exact files and decision. For each missing GitHub label, give
`gh label create "<label>" --repo <owner/repo>`. For an unsupported tracker,
name that tracker and the setup capability it lacks. Once setup is verified,
give `/triage-issue <issue URL>` for an existing issue or
`/plan-acceptance <source reference>` for an agreed source ready to plan.