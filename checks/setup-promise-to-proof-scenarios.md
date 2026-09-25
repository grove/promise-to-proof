# Setup Promise to Proof checks

These are human-runnable scenarios, not execution results. Use disposable
repositories. Record the proposed and actual file changes for each invocation.

## 1. Configure a fresh GitHub project

Use a GitHub repository with an existing `AGENTS.md`, no `docs/agents/` files,
no domain glossary or ADRs, and the five default triage labels. Invoke
`/setup-promise-to-proof` without giving edit approval, then approve its draft.

Pass when the first invocation changes nothing and shows the destination and
all proposed file contents. After approval, `docs/agents/issue-tracker.md`,
`docs/agents/triage-labels.md`, and `docs/agents/domain.md` describe that
project; `AGENTS.md` links them. No GitHub labels, issues, or placeholder domain
files are created.

## 2. Preserve existing configuration on a rerun

Change an unrelated section of `AGENTS.md` and customize a tracker convention.
Invoke the setup skill again with the same choices.

Pass when the skill retains both edits, adds no duplicate `## Agent skills`
block, and leaves the files unchanged without a new approved change.

## 3. Use the project's labels and instructions

Use a GitHub repository with custom existing triage labels and both `AGENTS.md`
and `CLAUDE.md`. Leave one required label missing in GitHub. Invoke the skill.

Pass when it confirms the authoritative instruction file, previews mappings to
the existing labels, reports the missing destination label, and neither creates
that label nor writes a file before approval.

## 4. Reject an unsupported tracker assumption

Use a project that tracks work outside GitHub and has no GitHub destination.
Invoke the skill and propose a local issue-tracker convention.

Pass when it does not describe GitHub-only issue publication or triage as ready,
does not silently invent a GitHub destination, and names the incompatibility.