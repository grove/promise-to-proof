# Imported GitHub source: issue #48

Source URL: https://github.com/grove/promise-to-proof/issues/48
Repository: grove/promise-to-proof
Issue updated at: 2026-09-29T08:53:16Z
Retrieved at: 2026-09-29 10:49 UTC
Title: Use disposable local Git repositories for P2P execution and recovery state
State: OPEN
Issue body SHA-256: 9bfb0fee960a8cacf4307781dc49a4b70400475908e69766a055bc2f05dafde1

## Body (verbatim)
Follow-up to #38 and intended precursor to #46.

Promise to Proof should use disposable local Git storage to make active delivery state cheaper, more exact, and easier to recover without putting P2P state into the project's Git history.

## Goal

Establish a local Git-backed execution/recovery substrate that P2P can use for active work.

The source repository remains the project repository. P2P's temporary candidate, recovery, repair, comparison, and experimental state should live in disposable local storage outside the project's tracked history.

This issue should provide the local-state mechanism that #46 can later make the default architecture.

## Simple model

```text
project Git repository
        |
        | source/base inputs
        v
local P2P state
  disposable Git repository/workspace
    - frozen comparison base
    - candidate snapshots
    - implementation state
    - repair generations
    - exact diffs
    - recoverable Git objects
        |
        v
review / proof / publication handoffs

project Git history contains no P2P runtime/recovery state
```

## Why local Git

Use Git where it provides concrete advantages over copied snapshots and ad-hoc file manifests:

- exact candidate identities via commits, trees, blobs, and modes;
- cheap diffs between base, implementation, repair, and final candidate;
- object deduplication instead of repeatedly copying unchanged files;
- reliable reconstruction and rollback;
- preservation of executable bits, symlinks, deletions, and renames;
- isolated branches/worktrees for bounded experiments or repairs;
- straightforward detection of what actually changed between generations;
- a natural foundation for later incremental verification and targeted re-review.

Do not require committing temporary P2P state to the source repository to obtain these benefits.

## Scope

- Add a local P2P state location outside tracked project Git state.
- Allow an active delivery to create or reuse a disposable Git repository/workspace keyed to the repository and work item.
- Materialize the admitted comparison base and issue-owned candidate state there without importing unrelated dirty work.
- Represent candidate generations using Git-native identities where practical instead of full-tree copied snapshots.
- Preserve enough information to resume an interrupted delivery safely on the same machine.
- Keep exact mappings between:
  - source repository;
  - work item;
  - comparison base;
  - contract identity;
  - candidate generation;
  - review/proof reports;
  - repair generations.
- Reuse Git objects or copy-on-write mechanisms where practical instead of duplicating entire trees.
- Support garbage collection/final cleanup only when the surrounding lifecycle says the local state is no longer required.
- Keep the design capable of using more than one disposable repo/worktree later when real isolation or concurrency requires it, without requiring multiple repositories for ordinary delivery.

## Default shape

Start simple:

> **One local P2P Git-backed state/workspace per active delivery unless another isolation boundary is actually needed.**

Do not introduce multiple repositories, branches, or worktrees merely because Git makes them possible.

## Recovery and resume

A fresh local session should be able to locate the active work item and determine:

- what contract/base was admitted;
- the latest valid candidate generation;
- which implementation/review/proof/repair stages completed;
- which saved results still apply to that exact candidate;
- what changed since an earlier generation;
- the earliest stage that genuinely needs to run again.

Do not infer completion from file presence alone. Reuse still depends on exact matching identities and valid retained evidence.

If required local Git objects or state are missing or corrupt, report a blocker rather than guessing or silently rebuilding uncertain history.

## Relationship to #38

#38 establishes the local-vs-durable retention boundary and reduces the current artifact footprint.

Do not reopen or expand #38 to implement this architecture.

This issue should build on #38's result and use local Git to improve the active-state representation rather than reintroducing bulky permanent artifacts elsewhere.

## Relationship to #46

#46 should be able to adopt this local Git-backed state as part of the default zero-P2P-state-in-Git architecture.

This issue does **not** itself need to complete the full #46 migration of contracts, reports, publication records, or final durable metadata out of Git.

It establishes the execution/recovery substrate first.

## Boundaries

- Do not weaken contract, candidate, comparison-base, review, proof, routing, or authorization identities.
- Do not make the disposable local repository a second permanent project history.
- Do not require users to manage its branches or commits manually.
- Do not publish or push the disposable repository by default.
- Do not treat local Git commits as permission to commit to the source repository.
- Do not add a database, cloud artifact service, or mandatory remote state backend.
- Do not add incremental verification semantics in this issue; only make the state model capable of supporting that later.
- Do not require multiple local repositories unless a demonstrated isolation/concurrency need justifies them.

## Acceptance

Demonstrate that:

1. An active delivery can use a disposable local Git-backed state/workspace without adding P2P runtime or recovery files to the project's Git history.
2. A small product change does not require copying the complete product tree into a large P2P snapshot for each candidate generation.
3. Comparison base and candidate generations have exact recoverable identities, including file contents, modes, symlinks, additions, and deletions.
4. Implementation and repair generations can be diffed exactly and reconstructed from retained local state.
5. Repeating/resuming a delivery can reuse completed stages whose contract/base/candidate/evidence identities still match rather than rerunning them solely because a new session started.
6. Changed candidate state is detected precisely and stale review/proof is not reused.
7. Unrelated dirty source-repository work is not silently imported into the P2P candidate.
8. Missing or corrupt required local Git state returns a precise blocker rather than guessed success or unsafe retry.
9. The ordinary design uses one local P2P Git-backed workspace per active delivery, while the data model does not prevent later use of additional isolated repos/worktrees.
10. The disposable local state can be safely removed when the surrounding lifecycle has established that recovery is no longer needed.
11. Existing integrity, isolation, and delivery-controller checks continue to pass with regression coverage for Git-backed state and resume.
12. #46 can use this mechanism as the local active-state substrate without requiring P2P runtime state to be committed to the source repository.

Goal:

> **Use disposable local Git to make P2P state exact, compact, resumable, and cheap—while keeping that execution machinery out of the project's Git history.**

## Comments and amendments
### https://github.com/grove/promise-to-proof/issues/48#issuecomment-5886918706
Author: grove
Created at: 2026-09-29T08:53:15Z
Body SHA-256: 6c6de86b5c9ea5ce6518f0326542e1882c973330439beaa93cbb83269e461cb0

Implementation note: use a portable user-level default local state root such as `~/.p2p/work/<repo-id>/<work-item>/`. The disposable local Git repository/workspace and related active runtime/recovery state can live underneath that directory. The important property is that this stays outside the source checkout and outside the project's Git history.

