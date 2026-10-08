---
name: setup-promise-to-proof
description: Set up ignored .p2p workflow storage, with optional tracker, triage labels, and domain-doc pointers.
disable-model-invocation: true
---

# Set up Promise to Proof

Configure the repository where the skills will run, not the skill collection's
source repository. Invocation authorizes the standard local filesystem setup.
Inspect and preserve existing files; ask only about unresolved consequential
configuration choices. Do not create tracker issues or labels,
change remotes, or create domain documents during setup.

## Inspect the repository

Read existing `AGENTS.md` or `CLAUDE.md`, `docs/agents/`, Git remotes, and any
existing issue or label conventions. Look for `CONTEXT.md`, `CONTEXT-MAP.md`,
and relevant ADR locations. When possible, inspect the destination's existing
GitHub labels with `gh` before proposing a mapping. Keep existing configuration
and human edits; a rerun must not replace them with defaults.

## Choose the configuration

- **Issue tracker (optional):** Local planning and delivery need no tracker.
  Configure GitHub only when requested or already in use. Confirm the
  target GitHub repository from the remote or ask for it when ambiguous. Draft
  `docs/agents/issue-tracker.md` with the destination, how to read, search,
  create, edit, label, and verify issues using `gh`, and whether PRs count as
  incoming requests (default: no). If the project uses another tracker, report
  that its tracker-writing skills are not ready; do not claim that a generic
  tracker configuration makes the GitHub-specific skills work.
- **Triage labels (only with a tracker):** Draft `docs/agents/triage-labels.md` mapping the five roles
  `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and
  `wontfix` to actual destination label strings. Recommend identical names when
  the project has no mapping; confirm overrides before writing. A file alone
  does not create labels in GitHub: report missing labels separately.
- **Domain docs:** Draft `docs/agents/domain.md` describing where to find the
  project's glossary/context and architectural decisions. Use the existing
  layout, or propose root `CONTEXT.md` and `docs/adr/` for a single-context
  project. Treat absent domain files as optional; do not create placeholder
  `CONTEXT.md`, `CONTEXT-MAP.md`, or ADRs.

Resolve repository conventions from existing configuration. Present any unresolved
tracker destination, label overrides, or domain layout choices for a decision;
continue independent local filesystem setup.

## Write and verify

Create `.p2p/work/` and `.p2p/tmp/` without replacing existing content. Do
not create `specs/` or `work/`; projects may use either directory for their own
files. Add `/.p2p/` to `.gitignore`, preserving unrelated rules and comments.
Check effective ignore rules for probes under both `.p2p` directories, including
repository, global, and `.git/info/exclude` rules. The repository rule must
ignore `.p2p` state.
Report setup errors and use `git check-ignore -v` to locate conflicting patterns;
do not hide them with force-add or silently rewrite unrelated policy. Empty directories need no
placeholder files. Run `python3 <skill-dir>/scripts/p2p_filesystem.py --repo <root> setup`;
its error output identifies conflicts.

Use `p2p-state/<slug>.json` as the default portable checkpoint destination;
keep it trackable and reserve it for compact P2P metadata. Do not create empty
checkpoint files. An explicitly selected GitHub issue is the alternative per
work item; do not establish competing synchronized stores. Explain that local
writes are not remote preservation, and that candidate/source commits must also
be retrievable before portability is claimed. Neither setup nor checkpoint
creation authorizes commits, pushes or issue comments.

Create or update resolved `docs/agents/` configuration files. Add
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
name that tracker and the setup capability it lacks. Once setup is verified, give `/plan-acceptance <project source path or agreed text>`;
optional source files may live in `specs/`, `work/`, or another project path.
Generated contracts go under `.p2p/work/<slug>/contract.md`. Optionally give
`/triage-issue <issue URL>` when the user has chosen a tracker. Saving setup files never stages, commits,
pushes, or creates external records.
