# Work item: Test the delivery controller against the FizzBee model

Source attribution: https://github.com/grove/promise-to-proof/issues/30
Imported update: 2026-09-26T14:34:22Z

Status: Imported planning input. No acceptance contract revision has been authored.

## Imported issue body

Connect the Phase 1 FizzBee model to the real single-work-item delivery controller from #28 and merged PR #29, so tests detect differences between the model and the running program.

## Scope

- Drive the actual controller through repeatable success, failure, and restart sequences. A modeled restart must restart the controller and inspect recovery from saved records.
- Test overlapping operations where the supported host permits them.
- Retain failure sequences that another person can replay.
- Introduce deliberate controller defects and demonstrate that the tests detect them. Removing a real protection, such as stale-report rejection, must make a test fail. Inspect both returned results and persisted state.
- Cover applicable Section 21.2 cases: unauthorized actions, stale or mistyped identities, candidate mutation, incomplete archives, interrupted report storage, late results, duplicate writes, repeated resume, and contested dirty files. Check real host provenance.

Demonstrate that the pinned FizzBee tools can drive the adapter before choosing its language. Reuse the delivered model and controller fixtures. Extend the bounded model where required controller behavior falls outside its current scope. Document bounds and distinguish model checks, substitute-backed controller tests, and live-host evidence. Running a second copy of the model alone does not satisfy this work.

## Boundaries

Phase 3 only. Preserve full independent REVIEWED and PROVEN requirements, exact identities, authorization, durable evidence, unrelated work, and the repair bound across restart. Strategy comparisons, optional checking levels, child scheduling, and automatic strategy selection remain in later phases. Do not add support for additional hosts as part of this issue.

Use /plan-acceptance to establish the canonical work/ contract. This source issue does not approve implementation, decomposition, or publication of delivery results.

## Source

[Exact optimization handoff](https://github.com/grove/promise-to-proof/blob/5c2c6b64b997dd2c04ac8ba85dcad8e08047eac2/plans/promise_to_proof_optimization_handoff.md)

Selected scope: Section 19, Phase 3, with Section 20 and applicable Section 21 constraints. The source specification remains authoritative.

- Repository: grove/promise-to-proof
- Path: plans/promise_to_proof_optimization_handoff.md
- Commit: 5c2c6b64b997dd2c04ac8ba85dcad8e08047eac2
- SHA-256: 7162a965fa53322a8805582756ea6137a847d72798e057dd751cc2e46c98f65a

The pinned file was retrieved and matched the local bytes before the separately requested status update. That local update records Phase 2 completion and Phase 3 as next; it is not included in this pinned revision.

This issue selects Phase 3. Closed issues #24 and #28 cover earlier phases of the same roadmap.

<!-- grove:create-parent-issue source=grove/promise-to-proof:plans/promise_to_proof_optimization_handoff.md -->


## Imported comments

None returned.
