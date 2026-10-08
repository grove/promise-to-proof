# Move existing P2P state out of Git

This guide applies to raw legacy records. Current compact
`p2p-state/<slug>.json` checkpoints are intentionally trackable; do not migrate
them out of Git. For cross-computer preservation and recovery, use
[portable checkpoints](p2p-checkpoints.md).

New active deliveries keep canonical contracts and compact records under
`.p2p/work/<slug>/`; their execution workspace and candidate stay outside the
checkout under `~/.p2p/executions/<repo-id>/<slug>/`. Unresolved state from the
legacy `~/.p2p/work/<repo-id>/<work-item>/` layout must remain there until it
is reconciled. This procedure applies when selected
P2P-owned files are already tracked in Git; it does not migrate or delete
unresolved runtime state.

This removes P2P-owned files, including tracked `.p2p/**` records and P2P-owned `work/*.md` files, from the current Git tree without rewriting prior
commits. Earlier history continues to contain the old files. Keep the backup
outside the checkout while active work still needs it.

1. Pause deliveries and inspect `git status --short` and `git ls-files -- .p2p work`. Classify each path: keep project-authored files, including files under `work/`, and migrate only P2P-owned state. Include any equivalent P2P records stored elsewhere, such as generated reports or snapshots at custom paths.
2. Choose a new, empty user-local backup directory outside the checkout. Copy each selected path there, preserving its relative path and current contents. For example:

   ```sh
   backup="$HOME/.p2p/migrations/$(basename "$PWD")-$(date +%Y%m%d-%H%M%S)"
   mkdir -p "$backup/.p2p/work" "$backup/work"
   cp -a .p2p/work/example "$backup/.p2p/work/"
   cp -a work/example.md "$backup/work/"
   # Repeat cp -a for every other selected P2P-owned path.
   ```

   Check the backup against the source before removing anything. Do not overwrite an existing backup. If a selected tracked file has staged, unstaged, or unresolved changes, preserve and reconcile those bytes before continuing; do not force removal.
3. Remove only the selected tracked P2P paths and inspect the resulting tree:

   ```sh
   git rm -r -- .p2p/work/example work/example.md
   # Include each other selected path; leave project-owned paths intact.
   git status --short
   git diff --cached --stat
   ```

4. Commit the reviewed deletions normally. This adds a new commit; it does not rewrite history. Verify with `git ls-files -- .p2p work` and inspect the commit diff. Keep the local backup until no active or unresolved delivery needs it.

The example paths are placeholders for paths you classified in step 1. Do not
remove all of `work/`, `specs/`, or another mixed-use directory. Never use
history-rewriting commands as a routine migration step. If history must later
be rewritten for a separate reason, plan that separately with repository
owners and backups.
