# Issue tracker: GitHub

Canonical acceptance contracts live in `work/<slug>.md`; lasting specifications
live in `specs/`. GitHub Issues are optional import, mirror, and publication
destinations. Local planning, slicing, delivery, and resume need no tracker.
Use the `gh` CLI for explicitly authorized GitHub operations. Importing an issue
does not authorize comments, labels, links, or other remote writes.
Direct `/plan-acceptance <issue>` is the scoped exception: it posts a proposal
comment for approval under the protocol's standalone planning rules. Local-only
and draft-only requests suppress publication. Planning inside delivery stays local.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

For pull requests, inspect all states before creating one and use exact head and
base refs. Create a draft with `gh pr create --draft`, supplying explicit base,
head, title, and body arguments. Read it back with `gh pr view` and explicit JSON
fields for URL, head SHA, base branch, title, body, and draft state. Never infer
publication from a successful command without readback.

Infer the repo from `git remote -v`; `gh` does this automatically when run inside a clone.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats external PRs as feature requests; `/triage-issue` reads this flag.)_

When set to `yes`, PRs run through the same labels and states as issues, using the `gh pr` equivalents.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.
