# Frozen delivery base under moving targets

**Status:** Proposed implementation specification, version 1.0. Not an approved acceptance contract or implementation.  
**Prepared:** 27 September 2026.  
**Suggested repository destination:** `plans/frozen-delivery-base-spec.md`.  
**Repository baseline inspected:** `grove/promise-to-proof` at `9384d662d425d222df3f5547bcbf84ba7cd10973`.

> `deliver-issue` proves one fixed candidate against one fixed agreement and one fixed repository base. A destination branch moving afterward does not invalidate that proof. Compatibility with the newer destination is a later integration and merge-readiness question.

## 1. Outcome

`deliver-issue` can complete reliably while its destination branch continues to receive commits.

Before admitting a delivery, it resolves the intended destination and captures that destination's exact current tip as the delivery's comparison base. That comparison base is then frozen for the lifetime of the delivery.

After admission, movement of the destination ref does not by itself invalidate implementation, review, proof, or resume. Review and proof remain about the exact candidate constructed from the frozen base.

Candidate changes, agreement changes, binding-input changes, approved routing changes, or corruption/loss of the frozen base remain invalidating as today.

Publication and merge readiness remain responsible for determining whether the accepted candidate can be integrated into the destination as it exists later.

## 2. Problem

The current workflow correctly uses exact candidate and contract identities, but it also treats movement of the destination branch as comparison-base drift.

For example, the controller currently supports this behavior:

```text
main/target = A
deliver-issue starts from A
candidate C is created

main/target advances to B

resume:
BLOCKED because destination tip changed
```

The delivery has not actually changed:

- its agreement is unchanged;
- candidate `C` is unchanged;
- its captured base `A` is unchanged;
- review/proof can still inspect exactly `C` relative to `A`.

Only the mutable destination ref has changed.

On an active repository this can make successful delivery depend on finding a period during which no other work reaches the destination. Repeatedly refreshing to the latest target can also produce an unbounded sequence:

```text
capture A
target moves to B
refresh to B
target moves to C
refresh to C
...
```

`deliver-issue` should not need repository-wide quiescence to decide whether one exact candidate satisfies one exact agreement.

## 3. Core distinction

The workflow must distinguish these identities:

```text
destination
    Mutable branch/ref such as main or epic/checkout.

comparison base
    Exact commit at the destination when this delivery is admitted.

candidate
    Exact product state being reviewed and proven.
```

Example:

```text
destination: main

admission:
    main -> A
    comparison_base = A

delivery:
    candidate C = A + issue-owned change

concurrent repository activity:
    main -> B

acceptance:
    agreement A1 + candidate C + comparison base A
    remain internally consistent

integration:
    compatibility of C with B is not yet established
```

The comparison base is an immutable input to one delivery.

The destination ref is a mutable external observation.

Changing the second must not be represented as changing the first.

## 4. Required behavior

### R1 — Resolve the current destination before admission

Before a new delivery is admitted, resolve its approved destination using the existing routing rules.

Resolve the destination ref to an exact full commit SHA.

That exact commit becomes the delivery's comparison base.

An explicitly supplied comparison base that does not equal the resolved destination tip at admission remains a blocker.

Therefore this remains invalid:

```text
current destination = B
caller requests comparison base A

A != B

=> BLOCKED before dispatch
```

This requirement preserves the existing protection against accidentally starting new work from a stale or unrelated target.

### R2 — Freeze the comparison base at admission

After admission, persist the exact comparison base and never replace it merely because the destination ref moves.

Resume must reuse the persisted comparison base.

A caller may not change the comparison base of an existing invocation.

The retained base commit and bytes must remain recoverable under the existing candidate-recovery rules.

### R3 — Destination movement after admission is observational

After admission, movement of the destination ref alone must not invalidate:

- implementation;
- candidate capture;
- review;
- proof;
- saved reports;
- resume;
- successful `REVIEWED` + `PROVEN` completion.

The workflow may observe the destination again during resume or completion, but this observation does not become the comparison base.

For example:

```text
comparison_base = A
current destination = B

candidate unchanged
agreement unchanged
routing unchanged

=> continue against A
```

### R4 — Preserve actual invalidation rules

The following continue to invalidate or block the affected delivery exactly as appropriate under existing rules:

- candidate content changes;
- contract text or semantic agreement changes;
- binding parent/spec input changes;
- approved delivery-plan or destination decision changes;
- candidate recovery failure;
- comparison-base bytes or retained Git objects becoming unavailable or inconsistent;
- report identity mismatch;
- missing or changed evidence;
- explicit adoption of a new comparison base.

A mutable branch moving from `A` to `B` is not comparison-base corruption.

Changing or losing the retained representation of `A` is.

### R5 — Review the admitted change set

`review-implementation` must support two comparison-base modes.

For a new direct review without a previously admitted delivery, resolve the intended target and freeze its exact tip when review scope is captured.

For review launched from `deliver-issue`, a validated delivery/candidate handoff supplies the authoritative frozen comparison base. The reviewer must review the candidate against that base even if the mutable destination has since advanced.

The reviewer may report:

```text
Comparison base: A
Destination observed now: B
Destination has advanced since delivery admission.
```

That observation alone must not prevent `REVIEWED`.

A changed candidate, changed agreement, changed approved destination, or explicitly adopted new base still requires fresh review according to existing rules.

### R6 — Proof remains candidate-bound

`prove` continues to judge the exact agreement and exact candidate.

Destination movement alone does not change either and therefore does not invalidate `PROVEN`.

No proof report may claim that the candidate has been verified against destination commits added after its frozen base unless those commits are actually part of the candidate.

### R7 — Resume must not chase the destination

The controller must not block resume solely because the destination ref differs from its admission-time tip.

This current sequence:

```text
run at destination A
destination moves to B
resume
=> BLOCKED: destination tip changed
```

must become:

```text
run at destination A
destination moves to B
resume
=> continue using comparison base A
```

Resume must still block if the approved routing itself changed.

Resume must also reject an attempt to replace persisted `comparison_base=A` with `B`.

Starting a genuinely new delivery against `B` remains possible through the normal new-admission path.

### R8 — Record destination freshness separately

The controller should retain an observational destination record outside candidate identity.

For example:

```json
{
  "destination_observation": {
    "destination": "main",
    "comparison_base": "aaaaaaaa...",
    "observed_tip": "bbbbbbbb...",
    "relationship": "fast-forward",
    "observed_at": "2026-09-27T00:00:00Z"
  }
}
```

`relationship` should be one of:

- `unchanged`;
- `fast-forward`;
- `non-fast-forward`;
- `unavailable`.

This object is informational.

It does not alter candidate identity, report identity, the comparison base, or acceptance status.

Do not require continuous monitoring of the destination. Each observation is only a point-in-time fact.

### R9 — Completion reports the boundary clearly

A successful delivery whose destination has moved should still return the existing successful acceptance outcome.

Human-facing output must distinguish acceptance from integration freshness.

Example:

```text
REVIEWED and PROVEN

Candidate:
  snapshot:sha256:...

Comparison base:
  aaaaaaaa...

Destination:
  main

Current destination observation:
  bbbbbbbb...

The candidate is accepted against the frozen comparison base.
The destination has advanced since admission.
Compatibility with the newer destination has not been established by this delivery.
```

Do not label the candidate stale, unproven, or unreviewed solely because the destination moved.

Do not claim it is ready to merge into the newer target.

### R10 — No automatic rebasing or refreshing

`deliver-issue` must not automatically:

- rebase the candidate;
- merge a newer destination into it;
- rebuild it on a newer base;
- replace the comparison base;
- restart review merely because the destination moved;
- restart proof merely because the destination moved.

If later integration produces a different candidate, normal candidate-change rules apply.

That new candidate receives fresh verification as required by the existing protocol.

## 5. Publication and merge boundary

This proposal deliberately does not weaken publication or merge readiness.

`deliver-issue` answers:

> Does this exact candidate correctly satisfy this exact agreement in the repository state from which it was built?

`merge-readiness` answers:

> Is the exact candidate represented by this PR currently ready to enter its actual destination?

Those are different questions.

Suppose:

```text
deliver-issue base: A
candidate: C
REVIEWED + PROVEN

main later becomes B
```

The acceptance evidence for `C` remains valid.

If `C` can be represented unchanged on a PR whose current comparison against `B` remains covered by the saved review, existing publication/readiness rules determine that.

If rebasing, merging, conflict resolution, integration, or another transformation changes candidate content or makes review scope uncertain, the existing fresh-review/full-proof rules apply.

`merge-readiness` remains strict about:

- the actual current PR head;
- the actual current target;
- current CI;
- repository approvals;
- merge rules;
- whether saved review/proof actually cover the candidate and applicable comparison.

A successful `deliver-issue` result is not a claim of permanent merge readiness.

## 6. Controller changes

The controller currently treats destination-tip equality as an ongoing admission invariant.

Change that invariant to an admission-time invariant.

### New run

At admission:

```text
resolve destination
resolve destination tip B0
require requested comparison base == B0
persist comparison_base = B0
retain B0 and required Git objects
```

After persistence, `comparison_base` is immutable.

### Resume

On resume:

```text
validate persisted agreement
validate persisted routing decision
validate persisted comparison base and retained bytes
validate candidate/reports/evidence

optionally observe current destination tip B1

if B1 != B0:
    record observation
    continue

if routing decision changed:
    block

if caller attempts comparison_base != B0:
    block
```

A destination observation failure must not by itself invalidate an otherwise recoverable local delivery. Record it as `unavailable`.

Publication or readiness can later require a successful current destination observation.

## 7. Review skill changes

Replace the current unconditional idea that an advanced destination always requires a fresh comparison base with a lifecycle-sensitive rule.

Suggested semantics:

> Before a delivery or direct review captures its scope, use the intended destination's current exact tip as the comparison base. Once a delivery has been admitted and its candidate handoff binds an exact comparison base, that base remains authoritative for review of that candidate. Later movement of the mutable destination does not by itself stale the review. A changed candidate, changed agreement, changed approved destination, or explicitly adopted new base requires the applicable fresh verification.

The review report should distinguish:

```text
Comparison: fixed comparison base used to define the reviewed change set
Destination observation: optional later observation of the mutable target
```

Do not silently substitute the latter for the former.

## 8. Delivery model changes

The bounded delivery model currently uses one mutable `base` value for two concepts:

1. the base captured by the verification stages; and
2. the mutable external destination state.

Separate them.

For example:

```text
admission_base = 0
destination_tip = 0
```

Verifier bindings record:

```text
contract
candidate
admission_base
invocation
```

The `admission_base` does not change during one modeled invocation.

A new environment action may change only:

```text
destination_tip = 1
```

Completion must continue to require:

```text
review/proof binding base == admission_base
```

It must not require:

```text
review/proof binding base == destination_tip
```

Add an assertion equivalent to:

```text
if outcome == complete:
    both reports bind the persisted admission base
```

Add a witness demonstrating:

```text
admit on base 0
launch verification
destination tip changes to 1
both verifiers finish against base 0
reports/evidence are saved and reread
outcome == complete
```

Retain mutations showing that changing or ignoring the actual persisted comparison-base identity remains unsafe.

## 9. Required scenarios

### T1 — Pre-admission target advance

```text
caller expects A
destination is already B
```

Expected:

```text
BLOCKED before dispatch
```

The blocker names the actual destination and tells the caller to start a new delivery using `B`.

This preserves today's stale-start protection.

### T2 — Target advances after admission

```text
destination = A
delivery admitted with comparison_base A
implementation begins
destination advances to B
candidate remains unchanged
```

Expected:

```text
delivery continues
review uses A
proof uses exact candidate
successful matching reports may complete
destination observation reports B
```

### T3 — Target advances while review/proof are running

Advance the target after one or both verifier contexts have launched.

Expected:

```text
their reports remain valid when they bind the admitted agreement,
candidate, and base A
```

No verifier is relaunched solely because the target moved.

### T4 — Target advances after reports return

Obtain complete matching reports, then advance the target before final controller completion.

Expected:

```text
completion succeeds
destination movement is reported observationally
```

### T5 — Resume after target advance

Interrupt a delivery after admission.

Move the destination from `A` to descendant `B`.

Resume.

Expected:

```text
resume uses A
no comparison-base rewrite
no target-movement blocker
only missing stages continue
```

### T6 — Non-fast-forward target movement

After admission on `A`, move the destination ref to a commit that is not a descendant of `A`.

Expected:

```text
local delivery may still complete against retained A
destination observation = non-fast-forward
no claim of integration or merge readiness
```

This scenario demonstrates that acceptance belongs to the snapshot, not to continued ownership of a mutable ref.

### T7 — Destination becomes unavailable

After admission, delete or make the destination ref unavailable while the retained comparison base remains recoverable.

Expected:

```text
local delivery may complete
destination observation = unavailable
publication/readiness remains a separate unresolved step
```

### T8 — Approved routing changes

After admission, change the approved plan so the work now targets another destination.

Expected:

```text
BLOCKED
```

This is a changed delivery decision, not ordinary branch movement.

Existing reconciliation rules apply.

### T9 — Candidate changes

Move the destination and also mutate candidate content.

Expected:

```text
candidate change invalidates reports
```

The target movement must not hide the real candidate drift.

### T10 — Comparison-base recovery changes

Keep the destination unchanged but corrupt, replace, or lose the retained base bundle/manifest required to reconstruct `A`.

Expected:

```text
BLOCKED
```

This demonstrates the distinction between a mutable destination ref and the immutable comparison-base artifact.

### T11 — Explicitly adopt the newer base

Start with accepted candidate `C` against `A`.

Explicitly choose to rebuild or integrate onto `B`.

Expected:

```text
new candidate identity
fresh affected verification
```

Prior reports remain historical evidence about the old candidate.

### T12 — Busy destination does not prevent termination

During one delivery, advance the destination several times:

```text
A -> B -> C -> D
```

Leave the contract, frozen base, and candidate unchanged.

Expected:

```text
deliver-issue can still reach REVIEWED + PROVEN
comparison_base remains A
latest observed destination may be D
```

No repeated refresh loop occurs.

## 10. Existing tests to change

The controller test currently covering target movement combines two behaviors that should be separated.

The pre-admission portion remains:

```text
destination already advanced
explicit old comparison base supplied
=> block before dispatch
```

The post-admission portion changes from:

```text
successful admission on A
destination moves to B
resume
=> destination tip changed blocker
```

to:

```text
successful admission on A
destination moves to B
resume
=> continue/succeed against A
```

Add assertions that:

- persisted comparison base remains `A`;
- candidate identity remains unchanged;
- existing matching reports are not invalidated solely by the ref movement;
- destination observation records `B`;
- no additional review/proof dispatch occurs when already-complete reports remain valid.

Keep independent tests for candidate, agreement, binding-input, routing, retained-base, and report drift.

## 11. Compatibility

No existing command needs a new required argument.

`--comparison-base` retains its meaning for a new invocation: the exact base from which this delivery starts.

Its semantics become clearer on resume: it is a persisted immutable delivery input, not an alias for “whatever the destination points to now.”

Existing candidate records remain valid because they already retain an exact comparison base.

Legacy controller runs that were blocked only because their target advanced may be resumed under the new semantics only if all persisted identities and retained base material can still be validated. Do not silently reinterpret incomplete or corrupt historical state.

No report verdict names change.

No additional merge authority is granted.

## 12. Non-goals

This proposal does not:

- make `deliver-issue` prove compatibility with future repository states;
- weaken candidate, contract, evidence, or routing identity checks;
- permit review against an arbitrary convenient base;
- remove the requirement to start new work from the correct destination;
- automatically rebase, merge, or resolve conflicts;
- make `PROVEN` equivalent to merge readiness;
- weaken current CI or repository approval requirements;
- guarantee that an accepted candidate will integrate without conflict later;
- create repository-wide locking;
- require the repository to stop changing.

## 13. Acceptance conditions

The change is ready when all of the following hold:

1. A new delivery still rejects a comparison base that is stale relative to its intended destination at admission.
2. After admission, the persisted comparison base is immutable for that invocation.
3. Destination-ref movement alone does not block implementation, review, proof, resume, or completion.
4. Review and proof remain bound to the exact admitted agreement and candidate.
5. Candidate, agreement, binding-input, routing, report, evidence, and retained-base drift still fail safely.
6. The controller records target movement separately from candidate/comparison-base identity.
7. The delivery model contains a successful trace where the destination moves during verification and completion still succeeds against the frozen base.
8. Model mutations still demonstrate that accepting a mismatched actual comparison base would violate the invariant.
9. Controller tests distinguish pre-admission stale-base rejection from post-admission target movement.
10. `review-implementation` no longer replaces a valid admitted comparison base merely because the destination ref later advanced.
11. `merge-readiness` retains its current-target checks.
12. Documentation clearly states that successful delivery establishes acceptance for an exact snapshot, not compatibility with arbitrary later destination commits.

## 14. Intended mental model

The workflow should be understandable as:

```text
Before delivery:

main -> A
        │
        └── freeze A
             │
             ├── implement
             ├── candidate C
             ├── review C against A
             └── prove C

Meanwhile:

main -> B -> C2 -> D
```

The movement on the second line does not alter the first line.

At completion:

```text
Candidate C:
    REVIEWED
    PROVEN
    against base A

Current main:
    D

Integration with D:
    not decided by deliver-issue
```

The rule is:

> **Freeze the repository state needed to judge the delivery. Let the repository continue moving. Reconcile with the current destination only when an operation actually needs the current destination.**

## 15. Source context

This proposal was prepared against repository commit `9384d662d425d222df3f5547bcbf84ba7cd10973`.

Relevant existing locations include:

- `skills/productivity/deliver-issue/SKILL.md` — destination selection, comparison-base capture, review/proof orchestration, resume and completion.
- `skills/productivity/deliver-issue/scripts/p2p_delivery.py` — executable controller behavior.
- `docs/p2p-delivery-controller.md` — currently documents target advance as a resume blocker.
- `skills/productivity/review-implementation/SKILL.md` — currently requires fresh review when an integration branch advances.
- `skills/productivity/prove/SKILL.md` — exact agreement/candidate proof semantics.
- `skills/productivity/merge-readiness/SKILL.md` — current PR head, base, CI and repository-gate checks.
- `checks/test_p2p_delivery.py` — currently tests both pre-admission base mismatch and post-admission destination-tip blocking.
- `checks/delivery-model/delivery.fizz` — currently models comparison-base drift as a completion blocker.
- `checks/delivery-model/README.md` and `checks/delivery-model/check.py` — model requirements and mutation checks.

These references describe the inspected baseline. They do not establish that this proposal has been implemented or accepted.