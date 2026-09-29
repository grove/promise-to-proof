# Imported GitHub source: issue #38

Source URL: https://github.com/grove/promise-to-proof/issues/38
Repository: grove/promise-to-proof
Issue: #38
Issue updated at: 2026-09-27T21:29:41Z
Retrieved at: 2026-09-28 10:46:53 UTC
Title: Minimize cumulative Promise to Proof artifact footprint

## Body (verbatim)

Promise to Proof should leave **as little generated material in Git as practical** while still establishing the thing we actually care about:

> What was promised, what exact code was checked, what evidence supported acceptance, and what exact code was delivered.

The artifacts are a means to that end. Raw execution history is not valuable merely because P2P generated it.

The footprint matters cumulatively: every delivery can otherwise add candidate snapshots, history, raw host logs, evidence, runtime state, and fixture output. Even modest per-delivery overhead becomes significant in a long-lived repository.

## Current motivation

At `main` commit `dbe54bc20a19b8ab8e700fb3aba9c9e8a59ce4d4`, tracked file content is roughly 57 MB, of which about 56 MB is under `.p2p/`. The largest contributors include candidate snapshots, retained evidence, history, and raw JSONL host/event logs.

The current snapshot format is particularly expensive for dirty candidates: `candidate.json` can embed the complete product tree with base64 file contents even when the actual change is small.

## Desired default

**Keep temporary and diagnostic P2P artifacts on the developer's computer, outside Git. Check only the minimum durable delivery record into Git.**

A normal successful delivery should not leave raw model transcripts, event streams, temporary repositories, full candidate copies, repeated history, or other execution exhaust in source history.

The permanent Git record should be small enough that using P2P repeatedly does not materially grow the repository.

## What belongs in Git

Keep only records needed to establish the durable delivery chain, for example:

- the acceptance contract / exact promise;
- the exact candidate identity;
- the comparison-base identity when relevant;
- the final review conclusion;
- the final proof conclusion and the observations needed to justify it;
- a small delivery/publication identity showing that the checked candidate is the thing actually delivered;
- any genuinely necessary small evidence that cannot be expressed adequately in the reports themselves.

Prefer references, hashes, commands, assertions, observations, and Git commit identities over copied file contents.

A typical successful work item should aim for something close to:

```text
work/foo.md

.p2p/work/foo/
    candidate.json       # small identity, not a repository snapshot
    review.md
    proof.md
    delivery.json        # small final identity/result summary
```

The exact set may differ, but every committed generated artifact should have a clear reason it is necessary after successful delivery.

## What should stay local and ignored

During execution, P2P may retain whatever it needs for safety and recovery, but this material should be local by default, for example:

- raw agent/model transcripts;
- host JSONL/event logs;
- prompts and intermediate responses;
- runtime workspaces;
- scratch directories;
- isolated/bare Git repositories;
- candidate/base bundles used only for active recovery;
- intermediate snapshots;
- retry/debug state;
- superseded reports and temporary history;
- large diagnostic evidence;
- generated fixture repositories and other reproducible test output.

Use an ignored local area such as `.p2p/tmp/`, `.p2p/runtime/`, or another clearly local P2P directory.

Do not move the same large artifact set to another permanent store merely to avoid Git. First ask whether the artifact is needed after successful delivery at all.

## Lifecycle

```text
ACTIVE
  keep detailed local state needed for safe execution/recovery

BLOCKED / INTERRUPTED / UNCERTAIN
  keep relevant local state until resolved or explicitly abandoned
  do not commit it merely because the run failed

REVIEWED + PROVEN
  verify the final durable record is sufficient
  discard redundant local execution artifacts

DELIVERED / PUBLISHED
  retain in Git only the compact promise -> candidate -> evidence -> delivered identity chain
  garbage-collect remaining local runtime data
```

If local recovery material disappears before an unresolved run is reconciled, report that honestly as unavailable/blocked. Do not infer success from a small Git record.

## Scope

- Replace full-tree dirty candidate snapshots with a compact representation. During execution, changed bytes may live only in local recovery storage. Once the candidate is committed/published, prefer the Git commit/tree identity as the durable candidate identity.
- Avoid putting full file contents in Git-resident manifests used only for identity or stability checks. Use path, mode, digest/blob identity, and the actual Git candidate where possible.
- Separate runtime/recovery storage from durable Git records.
- Add safe finalization/compaction that removes local execution artifacts after the durable successful result has been validated.
- Do not retain raw host/event transcripts in Git by default. Final reports should carry the relevant command/assertion/observation/environment needed to justify their conclusions.
- Keep large forensic material only for runs where it is actually needed while resolving uncertainty. It does not automatically become permanent evidence.
- Deduplicate local recovery data when practical.
- Reuse Git objects/copy-on-write mechanisms where helpful rather than duplicating complete repositories for each active delivery.
- For P2P's own tests, retain source fixtures/builders and expected assertions in Git, not complete generated repositories and verbose run output unless a specific regression fixture genuinely requires those exact bytes.
- Coordinate with #35 so experience capture does not turn normal execution exhaust into permanent Git history. Persist only useful conclusions/lessons when required; reference the existing final delivery record rather than copying it.
- Make footprint measurable: record Git-resident generated bytes/files per completed delivery so footprint regressions can be detected.

## Required safety properties

Reducing storage must not weaken delivery integrity.

- Contract, candidate, comparison-base, binding-input, review, proof, routing, authorization, and delivered-code identities remain exact where applicable.
- Review and proof still apply to one exact candidate.
- The final record cannot claim success merely because local raw logs were deleted.
- Final reports contain enough concrete observations to justify their verdicts without requiring the entire model transcript.
- Active, blocked, interrupted, or uncertain runs preserve the local state actually needed for safe recovery until resolved or abandoned.
- Missing local recovery state is reported honestly; P2P must not silently retry or reconstruct uncertain effects.
- Candidate transformation after verification still requires the existing applicable fresh verification.
- Publication and merge-readiness semantics remain unchanged.
- No automatic Git-history rewriting is required for normal operation.

## Acceptance

Demonstrate that:

1. A dirty candidate changing a small number of files no longer writes a full copy of the repository into Git-resident P2P records.
2. Normal execution artifacts are created only under ignored/local storage unless explicitly promoted because they are genuinely required in the final durable record.
3. A successful delivery can delete its local temporary/recovery artifacts and still retain enough Git-resident information to establish:
   - what was promised;
   - what exact candidate was accepted;
   - what review concluded;
   - what proof observed;
   - what exact candidate was delivered/published when applicable.
4. Final `review.md` and `proof.md` remain useful and evidence-backed without depending on raw model transcripts.
5. Interrupted/uncertain runs retain local recovery material and are not compacted into a misleading success record.
6. Loss of unresolved local recovery material produces a precise blocker rather than an inferred success or automatic retry.
7. Existing integrity/conformance/model checks continue to pass, with new tests for the local-vs-Git retention boundary.
8. Record before/after Git-resident generated file count and byte size for at least:
   - a tiny delivery;
   - a delivery in the Promise to Proof repository itself;
   - a small change in a substantially larger synthetic repository.
9. Define and enforce a small steady-state Git-footprint expectation for an ordinary successful delivery. Any large committed P2P artifact must have a documented reason it is necessary after delivery.
10. Repeated completed deliveries should grow Git primarily by their compact final records and application changes, not by raw execution history.

## Boundaries

This work is storage/retention optimization, not weaker acceptance semantics or fewer required checks.

Do not introduce a database, cloud artifact service, or permanent external artifact store as part of the default design. Such a facility can be considered later only if a concrete requirement shows that a large artifact genuinely must survive across machines and cannot be represented adequately by the compact Git record.

Do not treat "generated" as synonymous with "must retain."

The goal is:

> **Keep detailed execution artifacts local and temporary. Put only the minimum trustworthy record of promise, accepted candidate, evidence-backed conclusion, and delivered identity into Git.**
