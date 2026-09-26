# Promise to Proof: Repository Filesystem Model

**Implementation specification · Version 3.0 · 26 September 2026**

**Status: Implemented in commit `70b27bb` on 26 September 2026.**

Automated checks and a manual local delivery/fresh-checkout exercise passed.
See the [implementation report](../.p2p/work/p2p-filesystem/implementation.md)
for validation details and limits. This specification is retained as the source
agreement; the report and candidate record describe the implementation before
this status note was added.

This document defines the filesystem and Git conventions for Promise to Proof. It is intentionally small: ordinary Markdown files hold specifications and work items, Git holds the durable project record, and `.p2p/` holds generated Promise to Proof records.

## 1. Mental model

Promise to Proof uses three obvious locations:

```text
repo/
├── specs/              # what the product/system should do
├── work/               # what work we are doing
└── .p2p/               # what P2P generated while doing/verifying it
```

The governing rule is:

> **Commit everything durable. Ignore only explicitly temporary material.**

More specifically:

- `specs/` is committed.
- `work/` is committed.
- `.p2p/work/` is committed.
- `.p2p/tmp/` is ignored.
- Product code, tests, configuration and documentation follow the repository's normal Git rules.
- Secrets are never committed.
- Evidence that is too large, sensitive or machine-specific for Git is represented by a committed description, durable reference and checksum instead.

Promise to Proof must choose the correct location automatically. Users should not have to decide file-by-file whether generated P2P output belongs in Git.

## 2. Repository layout

The default layout is:

```text
repo/
├── specs/
│   └── retry-safe-uploads.md
├── work/
│   ├── retry-safe-uploads.md
│   ├── retry-safe-uploads-api.md
│   └── retry-safe-uploads-browser.md
├── src/
├── tests/
└── .p2p/
    ├── work/
    │   ├── retry-safe-uploads/
    │   ├── retry-safe-uploads-api/
    │   └── retry-safe-uploads-browser/
    └── tmp/
```

The P2P-specific ignore rule is:

```gitignore
/.p2p/tmp/
```

Do not ignore `.p2p/` or `.p2p/work/`.

Projects may configure different locations later if needed, but version 1 of this implementation should use these defaults and keep all skills consistent.

## 3. Naming conventions

Use lowercase kebab-case throughout.

### Specifications

```text
specs/<descriptive-name>.md
```

Example:

```text
specs/retry-safe-uploads.md
```

### Work items

```text
work/<descriptive-name>.md
```

A child work item should normally use the parent stem plus a short slice name:

```text
work/retry-safe-uploads.md
work/retry-safe-uploads-api.md
work/retry-safe-uploads-browser.md
```

Do not add synthetic IDs, dates or version numbers to filenames unless the project already has a reason to do so. The repository-relative work-item path is its durable identity.

### P2P artifact directory

The artifact directory mirrors the work-item filename without `.md`:

```text
work/retry-safe-uploads-api.md
.p2p/work/retry-safe-uploads-api/
```

Use predictable filenames inside it:

```text
implementation.md
candidate.json
review.md
proof.md
evidence/
```

Other stages may use similarly obvious names such as `audit.md`, `repair.md`, `publication.md`, and `retrospective.md`.

Evidence files use descriptive kebab-case names, for example:

```text
evidence/concurrent-retries.log
evidence/restart-result.json
```

## 4. Specifications and work items

### Specifications

A specification describes lasting product or system behavior. It belongs in `specs/` when that document is useful independently of one particular delivery.

A specification is optional. Small work may start directly as a work item.

### Work items

A work item describes one coherent delivery and contains its acceptance requirements. It replaces the workflow role previously played by a parent or child issue.

A minimal work item looks like:

```markdown
# API retry safety

Source: [Retry-safe uploads](../specs/retry-safe-uploads.md)
Parent: [Retry-safe uploads](retry-safe-uploads.md)

## Outcome
Owners can repeat an upload request without creating duplicates.

## Acceptance
- R1: A retry returns the original stored upload and metadata.
- R2: Concurrent retries create exactly one stored upload.

## Scope
Includes API behavior and owner checks. Excludes browser changes.

## Verification
- R1: Retry through the public API and compare IDs and stored metadata.
- R2: Race requests and assert one stored record.
```

Omit sections that are not useful. Requirement IDs should remain stable when downstream review, proof, repair or parent/child mapping needs them.

The work-item Markdown file is the canonical acceptance contract. Promise to Proof must not create a second competing contract file elsewhere.

### Parent and child work

A parent work item lists its children and explains their contribution. Each child links back to its parent and states a complete child outcome.

Example parent section:

```markdown
## Children
- [API retry safety](retry-safe-uploads-api.md) — R1 and API contribution to R3-R5
- [Browser retry safety](retry-safe-uploads-browser.md) — R2 and browser/cross-channel contribution to R3-R5
```

Slicing work does not create additional specifications by default. A child gets its own specification only when it represents a genuinely reusable product/design concept.

Child completion does not prove the parent. The integrated parent outcome still requires parent-level proof on an exact integrated candidate.

## 5. Generated P2P records

All durable generated output for a work item goes under its matching `.p2p/work/<slug>/` directory.

Example:

```text
.p2p/work/retry-safe-uploads-api/
├── implementation.md
├── candidate.json
├── review.md
├── proof.md
└── evidence/
```

These files are part of the durable project record and should be committed to Git.

`.p2p/tmp/` is for scratch files, caches, disposable experiments and transient command output. Files there may be deleted at any time and must not be required to resume or understand the work.

Operating-system temporary directories such as `/tmp` or `/private/tmp` are also temporary. Before a stage claims a durable handoff, anything required later must be copied into `.p2p/work/...` or summarized in a durable report.

### Large or sensitive evidence

Do not commit credentials, tokens or secrets.

If evidence is unsuitable for Git because it is large, sensitive or machine-specific, commit a small record containing:

- what the evidence is;
- where its durable copy is stored;
- its checksum;
- any access limitation needed to interpret the result.

If no safe durable location exists, report the evidence as unavailable rather than pretending the handoff is complete.

### Editing generated records

`specs/` and `work/` are normal human-editable project files.

`.p2p/work/` is primarily generated workflow state. It may be inspected and reviewed like any other committed file, but verdicts and identities should normally be changed by rerunning the relevant P2P stage rather than hand-editing them.

## 6. Candidate identity

Because `.p2p/work/` is committed after implementation, the current Git `HEAD` is not automatically the candidate that was reviewed or proven.

Every candidate-bound report must name the exact candidate it applies to.

For a committed candidate, `candidate.json` records at least:

```json
{
  "commit": "<full candidate commit SHA>",
  "comparison_base": "<full comparison-base commit SHA>",
  "work_item": "work/retry-safe-uploads-api.md",
  "work_item_sha256": "<SHA-256 of the exact work-item bytes>"
}
```

Review and proof repeat or reference these identities.

Example lifecycle:

```text
A  product candidate
│  review and proof examine A
│
B  later commit records review/proof under .p2p/
```

The reports still establish results for candidate **A**. Committing the reports does not silently make **B** the proven candidate.

When deciding whether a later commit contains the same product candidate, compare the complete tracked tree outside `.p2p/` and recheck the exact work item. Any product or binding agreement change requires fresh candidate-bound review/proof.

For uncommitted work, use the existing reproducible snapshot mechanism. The snapshot must include all relevant tracked, staged, unstaged, deleted and untracked product files and must exclude `.p2p/`.

Acceptance is derived from matching current artifacts. Do not add an authoritative `accepted: true` flag.

## 7. Required skill behavior

The implementation should change storage and lookup conventions, not invent a new workflow engine.

| Area | Required behavior |
| --- | --- |
| Setup | Establish `specs/`, `work/`, `.p2p/work/` and `.p2p/tmp/`; ensure only `.p2p/tmp/` is ignored by the P2P convention. |
| Planning | Create or update `work/<slug>.md`; keep the acceptance contract there. |
| Slicing | Create child files in `work/`, add parent/child links and contribution mappings. External child issues are optional. |
| Implementation | Modify authorized product files, save `implementation.md`, and capture the exact candidate. |
| Review | Read a fixed candidate and exact work item; save `review.md` under the matching artifact directory. |
| Proof | Read the same fixed candidate and exact work item; save `proof.md` and retained evidence under the matching artifact directory. |
| Repair | Modify the candidate only within authorized scope, then require fresh candidate-bound review/proof as appropriate. |
| Resume | Given a work-item path, find its spec, parent/children, candidate, reports and evidence without chat history or manually supplied artifact paths. |
| External trackers | Optional import/mirror/publication surfaces only. They must not become a second canonical contract. |

Saving files locally does not authorize staging, committing, pushing, creating issues, publishing PRs, merging or deploying. Existing authority rules remain unchanged.

## 8. Implementation acceptance checks

A disposable repository must demonstrate the following:

1. **Git rules are obvious.** `specs/`, `work/` and `.p2p/work/` are trackable; `.p2p/tmp/` is ignored; conflicting ignore rules are detected.
2. **Names are predictable.** `work/foo-bar.md` resolves to `.p2p/work/foo-bar/`; parent/child names follow the convention and collisions do not overwrite unrelated work.
3. **Local-only workflow works.** A specification or standalone work item can be planned, implemented, reviewed and proven without an external issue tracker.
4. **Slicing stays local by default.** A parent can create child work items with links and contribution mappings without creating tracker issues or extra specs.
5. **Durable evidence survives temp cleanup.** Deleting `.p2p/tmp/` and OS temp files does not remove anything required to understand or resume completed work.
6. **Secrets are not committed.** Secret-bearing output is redacted/excluded; large or unsuitable evidence uses a safe durable reference plus checksum.
7. **Candidate identity stays exact.** Review/proof of candidate A remain explicitly bound to A after a later commit records `.p2p/` artifacts.
8. **Stale results are rejected.** Changing product files, the work item, a binding parent/spec input or the review comparison base prevents reuse of incompatible old results.
9. **Fresh-checkout resume works.** After an authorized commit and transfer, a fresh checkout given only `work/<slug>.md` can find the relevant durable P2P state and continue safely.
10. **No unintended external effects occur.** Creating durable files does not itself stage, commit, push, modify trackers, publish a PR, merge or deploy.

## 9. Implementation boundary

Keep this change small.

Use Markdown, ordinary Git history and the existing candidate/snapshot mechanisms. Add only the shared path-resolution and validation helpers needed to make the conventions consistent across skills.

Do **not** add, as part of this change:

- synthetic work-item IDs;
- a workflow database;
- metadata sidecars for every file;
- a daemon;
- a generic tracker SDK;
- automatic cross-machine synchronization;
- a new artifact service;
- automatic Git commits or pushes.

The target mental model should remain understandable from the repository tree alone:

```text
specs/          What should the product do?
   ↓
work/           What work are we doing?
   ↓
src/ + tests/   What did we build?
   ↓
.p2p/work/      What did P2P do, review and prove?

.p2p/tmp/       Disposable scratch only
```
