# Promise to Proof: Filesystem Model

**Implementation specification · Version 2.0 · 26 September 2026**

This document replaces the earlier filesystem specification, including its instruction to ignore `.p2p/`. It defines the agreed implementation target; it does not claim the changes are already implemented.

## 1. Repository layout and Git rules

> Commit the durable project record. Ignore temporary execution material. Never commit secrets.

```text
repo/
├── docs/
│   ├── specs/                 # COMMIT: product specifications
│   └── work/                  # COMMIT: work items and contracts
├── src/                       # COMMIT: product implementation
├── tests/                     # COMMIT: product tests
└── .p2p/
    ├── README.md              # COMMIT: explains these rules
    ├── work/                  # COMMIT: generated P2P records
    │   └── retry-safe-uploads-api/
    │       ├── implementation.md
    │       ├── candidate.json
    │       ├── review.md
    │       ├── proof.md
    │       └── evidence/
    └── tmp/                   # IGNORE: scratch, caches, experiments
```

The P2P-specific ignore rule is:

```gitignore
/.p2p/tmp/
```

Do not ignore `.p2p/` or `.p2p/work/`. Preserve unrelated repository ignore rules, but check that they do not accidentally hide durable P2P records.

**P2P chooses the right location.** Users should not have to classify generated files one by one. Retained reports, useful logs and evidence go in `.p2p/work/`; disposable output goes in `.p2p/tmp/` or operating-system temporary storage. Product files follow the repository’s normal conventions, regardless of whether a person or an agent wrote them.

**Safe exceptions.** Redact sensitive output before retaining it. For evidence too large or sensitive for Git, commit a safe description, a non-secret durable reference and a checksum instead. Use an approved existing storage destination; if none is available, report the evidence as unavailable. Never commit credentials or access tokens.

**Commit policy is not commit permission.** Durable files belong in the next authorized commit. Creating them does not authorize staging, committing or pushing. P2P must distinguish “saved locally” from “committed” and “published”.

## 2. Specifications, work items and naming

**Specifications** in `docs/specs/` describe lasting product behavior or design. **Work items** in `docs/work/` describe a particular delivery and contain its acceptance contract. A small work item can stand alone; do not require a separate specification or parent when neither adds useful information.

Use lowercase kebab-case Markdown filenames: `retry-safe-uploads.md`. Keep both directories flat in this version. Names must be unique within each directory; resolve collisions explicitly, never by overwriting an unrelated file. Do not add dates, version suffixes or synthetic IDs to these names.

A parent and its children use the same format. Name a child `<parent-stem>-<slice>.md`, for example `retry-safe-uploads-api.md`. A work item’s repository-relative path is its identity; its artifact directory uses exactly the filename without `.md`:

```text
docs/work/retry-safe-uploads-api.md
.p2p/work/retry-safe-uploads-api/
```

Keep filenames stable when titles change. A deliberate rename must update current links and move the matching artifact directory. Historical reports keep their original recorded identities. Use Markdown links relative to the containing file.

### Minimal work-item format

```markdown
# API retry safety

Source: [Upload specification](../specs/retry-safe-uploads.md)
Parent: [Retry-safe uploads](retry-safe-uploads.md)
Covers: Parent R1 and the API contribution to parent R3.

## Outcome
Owners can repeat an upload request without creating duplicates.

## Acceptance
- R1: A retry returns the original stored upload and metadata.
- R2: Concurrent retries create exactly one stored upload.

## Scope
Includes owner checks. Excludes browser changes.

## Verification
R1: Retry via the public API; compare IDs and stored metadata.
R2: Race requests; assert one stored record and equal IDs.

## Dependencies
None.
```

Omit inapplicable sections. Add boundaries, unresolved decisions and approval information when needed. Keep requirement IDs stable; child IDs are local to that child. The work-item file is the one canonical contract, not a second checklist alongside another contract file. Planning proposes or revises it; required approval remains explicit.

A parent adds a `Children` section with links and each child’s contribution. Children identify their parent obligations and needed prerequisite outcomes. Splitting work does not create more specs by default. Child success does not prove the parent: the complete parent outcome still needs proof on one integrated candidate, with integration review where required.

## 3. Generated records and their history

All retained P2P output for `docs/work/<slug>.md` goes under `.p2p/work/<slug>/`. These files are tracked in Git and normally updated by the workflow, not hand-edited to change a verdict.

| Name | Contents |
| --- | --- |
| `implementation.md` | What changed, checks run, limitations and handoff. |
| `candidate.json` | Exact candidate, comparison base and governing work-item identity. |
| `review.md` | Review result, findings, scope and exact input identities. |
| `proof.md` | Requirement verdicts, observations and evidence references. |
| `evidence/` | Retained outputs needed to interpret or reproduce the result. |
| `runs/` | Earlier local records that would otherwise be lost on replacement. |

Create files only when needed. Other stages use equally predictable names, such as `audit.md`, `repair.md`, `publication.md` and `retrospective.md`. Additional evidence uses descriptive kebab-case names with the appropriate extension, such as `concurrent-retries.log`. Do not scatter reports in the repository root or unrelated documentation directories.

### Keep the current view simple

The top-level report names are the current working view, not an assertion that they are valid for today’s code. Their recorded identities determine whether they still apply.

Use Git as the normal history. Before replacing a report, ensure its previous report, candidate reference and required evidence are recoverable together in Git. If they are not yet committed, preserve that set under `runs/<UTC-timestamp>/` first; for example, `runs/20260926T012400Z/`. Add `-02`, `-03`, etc. if the directory already exists. Never overwrite an existing archive.

When the candidate or agreement changes, retain the old records and remove stale reports from the current view before producing replacements. Do not silently change a report’s candidate or contract identity. There is no need for a separate event database, latest pointer or status file.

### Evidence must remain useful

Evidence can be embedded in a report; separate files are not mandatory. Record the command or inspection, actual observation, expected result, relevant environment and exact candidate. A command without its observed result is not evidence.

Use relative links for repository files. External evidence needs a durable reference and checksum, plus any access limitation. A checksum identifies bytes; it does not preserve them or make them accessible.

Temporary files may be deleted. Before reporting a completed handoff, copy required evidence into the retained record or preserve the relevant observations in the report. A required artifact available only in `/tmp`, a cache or `.p2p/tmp/` means the handoff is incomplete. Never delete the only recoverable evidence merely because a newer run exists.

### Make the Git decision visible

Setup creates `.p2p/README.md` with the commit/ignore rule. Each stage’s completion summary identifies its durable files to commit, ignored temporary output and any unavailable evidence. Preserve unrelated user changes; do not silently include them in the work item or a commit.

## 4. Candidate identity and acceptance

**Committed with the project does not mean part of the product being proved.** `.p2p/` contains workflow records. Product code, tests, specifications, work items, build settings and other product inputs remain outside it. The product must not depend on `.p2p/` contents for its build or behavior.

Review and proof must use a fixed candidate, never a moving branch or an assumed `HEAD`. For a committed candidate, `candidate.json` records at least:

```json
{
  "commit": "<full candidate commit SHA>",
  "comparison_base": "<full comparison-base commit SHA>",
  "work_item": "docs/work/retry-safe-uploads-api.md",
  "work_item_sha256": "<SHA-256 of the exact work-item bytes>"
}
```

Review and proof repeat these identities and capture any governing specification or parent inputs. Required approvals must refer to the exact agreement. Unresolved source changes return to planning rather than silently changing acceptance.

For uncommitted work, reuse the existing reproducible-snapshot mechanism. It must preserve the complete selected candidate, including relevant tracked, staged, unstaged, deleted and untracked content, while excluding `.p2p/`. Retain the actual snapshot or a retrievable durable reference; a digest alone is insufficient. Preserve exact uncommitted agreement text as historical input, not a competing editable contract.

Review and proof may save records under `.p2p/`, but must not change the captured product or agreement. Run potentially mutating checks in an isolated copy of the fixed candidate.

### Recording proof does not prove a new commit

```text
A: product candidate
   review and proof examine A
B: authorized commit adding the reports under .p2p/
```

The reports still prove **A**, not B merely because B is now `HEAD`. Creating or committing the reports must not silently replace the recorded candidate.

To use those results for publication of B, deterministically compare A and B’s complete tracked trees outside `.p2p/`, including paths, contents and file modes, and recheck the exact agreement. If identical, report B as carrying the same verified product content while retaining both commit identities. Any other change requires a new candidate and fresh review/proof. Apply the equivalent check to retained snapshots. If the build or checks depend on the commit ID or changed environment, tree equality is not sufficient; rerun the affected verification. This does not replace existing comparison-base, authorization, CI or merge-readiness checks.

Referenced candidates must remain retrievable after transfer or publication. If a squash or history rewrite would lose the only copy, retain a recoverable snapshot or other approved durable reference first.

### Derive acceptance, do not store a flag

A current acceptance result requires full matching `REVIEWED` and `PROVEN` reports, complete requirement coverage and accessible evidence for the exact current agreement and candidate. Changed product or agreement inputs make old results historical, not current. A changed comparison base also requires a fresh review. A filename, issue closure or manually edited `accepted: true` field is never sufficient.

## 5. Changes to the workflow and rollout

Keep the existing stage responsibilities and approval boundaries. Change their common storage and lookup rules rather than building a new workflow engine.

| Area | Required behavior |
| --- | --- |
| Setup | Explain the layout, write `.p2p/README.md`, ignore only P2P temporary material and check durable records are visible to Git. |
| Work creation and planning | Create or update `docs/work/<slug>.md`; keep the approved acceptance contract in that file. No external issue is required. |
| Slicing | Create local child work-item files, parent/child links, contribution mappings and prerequisite descriptions. |
| Implementation and repair | Modify authorized product files; save reports in the matching artifact directory and capture the resulting candidate. |
| Review and proof | Inspect fixed inputs, retain independent results and evidence, and reject stale or unavailable inputs. Preserve existing host-isolation requirements. |
| Delivery and resume | Accept a local work-item path and discover its source, relationships, candidate, reports and next action without chat history or manual artifact paths. |
| Optional integrations | Read or publish supported external references only when selected; keep existing publication and merge-readiness gates, including the candidate-equivalence check in section 4. |

Existing issue-oriented entry points may resolve an external issue to a local work item. Store its external reference in that Markdown file and reuse it on subsequent invocations. Ambiguous matches require resolution, not duplicate files. External discussion can propose amendments, but it does not automatically rewrite the local agreement.

External issues are optional links or published views, not a second canonical contract. Local delivery must work without tracker configuration. No new public command name is required just to implement this storage change.

### Migrate without losing evidence

1. Update the shared protocol, installation references, setup guidance and file examples to this layout. All skills must resolve paths the same way.
2. Inspect existing `.p2p/` content before removing a blanket ignore rule. Move disposable files to `tmp/`, redact sensitive records and flag large evidence needing external storage. Do not bulk-stage newly exposed files.
3. Use the new convention for new work. Move active work only deliberately, preserving exact historical identities and updating current links. Keep older contracts and reports readable; do not convert the entire backlog automatically.
4. Exercise local planning, implementation, review and proof first; then apply the same convention to slicing, resumption and existing optional integrations. Run the checks in section 6 before declaring the migration complete.

### Keep the implementation bounded

Use Markdown, normal Git history and the existing candidate-capture facilities. Add only small shared path-resolution or validation helpers where needed. This change does not require synthetic work-item IDs, metadata sidecars for every file, a database, a daemon, a generic tracker SDK, automatic synchronization or a new artifact service.

Normal Git commits and transfer carry the tracked record. A local save is not a shared handoff until the required files and referenced candidates are available to the receiving checkout. Missing storage, evidence or authority must be reported explicitly, not treated as success.

## 6. Implementation acceptance checks

Demonstrate these behaviors in a disposable repository. Check actual files, Git visibility, recoverability and stage results, not just instruction wording. Existing review/proof quality and authorization checks remain applicable.

| ID | Required observation |
| --- | --- |
| AC1 — Obvious Git rules | Specs, work items, `.p2p/README.md` and durable `.p2p/work/` records are eligible for tracking. `.p2p/tmp/` is ignored. Setup detects conflicting ignore rules and explains the distinction. |
| AC2 — Predictable names | A work-item path resolves to exactly the matching artifact directory. Parent/child filenames and links follow section 2. A collision cannot overwrite unrelated work; a deliberate rename updates current links. |
| AC3 — Local work and slicing | A spec can become a parent and children without a tracker. Each work-item file contains its own contract and relevant mappings. No duplicate contract or unnecessary child spec is created. Child success alone does not complete the parent. |
| AC4 — Safe durable evidence | Required observations survive deletion of temporary files. Missing external evidence prevents a complete handoff. A secret-bearing output is redacted or excluded, never committed; retained external references contain no credentials. |
| AC5 — Exact candidate, later report commit | Review and proof name candidate A. Saving reports leaves the product unchanged. Report-only commit B is recognized as product-equivalent only after the explicit comparison; the reports are not relabeled as proof of B. |
| AC6 — Stale results rejected | Change a product file, governing work item or binding parent/spec input: old acceptance no longer applies. Change the comparison base: old review is not reused. Editing only a success label cannot restore acceptance. |
| AC7 — Recoverable dirty work | Capture a candidate with modified, deleted and untracked product files. Restore the exact content without `.p2p/` records and without absorbing unrelated edits. A missing or corrupted required snapshot blocks reuse. |
| AC8 — No lost run history | Replacing a report preserves its old candidate and required evidence in Git or a non-overwritten `runs/` archive. Prior uncommitted reports are not silently lost. Current outputs do not present retired results as current. |
| AC9 — Fresh-checkout resume | After authorized commit and transfer, a fresh checkout given only the work-item path finds its spec, relationships, exact candidate, reports and evidence without chat history. Missing inputs produce a specific blocker. |
| AC10 — No unintended effects | Saving a local record does not stage, commit, push, create/edit external issues, publish a PR, merge or deploy without applicable authority. Completion summaries list files to commit and preserve unrelated user changes. |

**Implementation outcome:** a developer can understand what belongs in Git from the path alone, find all work-related records from one work-item file, and tell exactly which implementation the saved review and proof establish.
