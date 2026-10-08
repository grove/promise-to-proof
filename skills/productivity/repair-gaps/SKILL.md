---
name: repair-gaps
description: Repair named implementation or evidence gaps from a NOT PROVEN proof, report the change honestly, and require fresh proof without declaring acceptance.
disable-model-invocation: true
---

## Delegated continuation

In an enclosing autonomous delivery, apply a covering in-scope recovery
recommendation and continue to both independent verifiers without asking again.
For a read-only diagnosis dispatch, inspect mechanisms and return the controller's
requested diagnosis schema; make no edits and do not claim REPAIRED. Choose a
concrete different method after repeated gaps, including evidence or local
prerequisite work. Name an exact unavailable input only when recovery cannot act.
Evidence-only recovery must leave product bytes unchanged. Planning decisions
return to the delegated planner/auditor; repair cannot weaken the agreement.


`/repair-gaps` is the repair step after `/prove`. It consumes the source
contract, the proof result, the matching candidate, and specific unresolved
requirement IDs. It repairs only those gaps and never replaces fresh proof.
Review-only findings belong to an authorized `/implement-contract` invocation;
they do not replace the matching `NOT PROVEN` proof this skill requires.

Before repair, read the [acceptance contract protocol](references/acceptance-contract-protocol.md).
Make the smallest complete repair for the named requirements: narrow in scope,
complete in depth.

## Guardrails

- Confirm that the proof's exact contract revision and captured text match the
  current contract, and that the exact candidate identity still matches.
- Edit only the implementation or evidence needed for the named requirements.
- Preserve the source requirements and existing valid checks.
- Implement all state, invariant, persistence, and failure behavior necessary
  for the named outcomes. Those IDs do not authorize unrelated improvements or
  speculative machinery. Reuse the agreed seams and independent oracles.
- Never weaken the contract to fit a repair. If a changed promise or consequential
  new seam is needed, report the decision as blocked and hand it back for explicit
  resolution. An authorized material change requires a new revision and proof.
- Do not publish, commit, push, or declare `PROVEN`.
- If inputs are stale, ambiguous, or unavailable, report `BLOCKED` without editing.

## Workflow

1. Accept `.p2p/work/<slug>/contract.md` and discover its linked inputs, `candidate.json`,
   and `proof.md` under `.p2p/work/<slug>/`; also accept an explicit proof
   reference that resolves to the same work item. Read the exact local contract
   revision and matching `NOT PROVEN` proof result. Recheck binding parent/spec
   hashes and comparison base; local `.p2p/` record updates preserve candidate
   identity and must stay out of Git history.
2. Confirm the candidate identity and the unresolved requirement IDs.
3. Apply the smallest complete implementation or evidence repair for the named
   requirements, when editing is authorized. Preserve authorization already given.
4. Run the focused check and inspect the resulting diff.
5. Recheck the contract and report the candidate before and after, changed files,
   addressed requirements, changed evidence, and remaining gaps. When gaps remain,
   recommend one smallest concrete next action. Name the affected IDs and the exact
   command, missing input, or human decision needed; `None` is valid only when no
   gaps remain. The candidate may change only in the scoped repair; the acceptance
   requirements stay intact.
6. Save and reread `.p2p/work/<slug>/repair.md`, retained evidence, and the
   updated compact `candidate.json` identity. Keep payload required to resume an
   active run in ignored local storage, not in the durable candidate record.
   Preserve previous reports and candidate records under the protocol's history
   rule before replacement. Exclude `.p2p/` from the candidate. Changed product
   or binding inputs make old review/proof historical; neither accepts the
   repaired candidate.
   Hand off the changed candidate for separate `/review-implementation` and fresh proof.
   End with: **Fresh `/prove` required before acceptance.**

## Outcomes

- `REPAIRED`: the scoped change was made and focused checks passed.
- `NO CHANGE`: no safe or necessary change was made; explain why.
- `BLOCKED`: the inputs or required capability are unavailable or stale.

None of these outcomes accepts the ticket. A new `/prove` run must evaluate the
changed candidate against every requirement.


## Preserve reusable delivery learning

If this run reveals durable, non-obvious knowledge that is likely to help future
delivery work, include it as a **learning candidate**. Empty output is valid and
preferred over inventing a lesson. A candidate must state its scope, the reusable
lesson, the concrete evidence that suggested it, and important uncertainty.

When the enclosing controller requests structured JSON, put these in its
`learning_candidates` array. Otherwise add a short `## Learning candidates`
section to the report.

Learning candidates are leads for `/retrospect`, not accepted advice. They must
not change the contract, requirement IDs, stage verdict, scope, repair allowance,
or authority. Do not promote them into project rules or the advisory learning
register from this skill.

## Handoff format

```markdown
# <REPAIRED | NO CHANGE | BLOCKED>: <source>

Contract: <source and exact revision>
Contract snapshot: <same immutable reference or captured text and digest as proof>
Candidate before: <identity>
Candidate after: <identity or unchanged>
Addressed requirements: <IDs or None>
Changed files: <files or None>
Changed evidence: <assertions/artifacts and affected IDs, or None>
Focused checks: <observations and assertions>
Remaining gaps: <IDs and reasons, or None>
Recommended next action: <one concrete action for the remaining IDs, or None>

Fresh `/prove` required before acceptance.
```

After the handoff, end with `Next steps:` and a numbered list (`1.`, `2.`, ...)
of applicable actions in order, so each can be referenced by number. For
`REPAIRED`, give the exact next invocation(s):

```text
/review-implementation <changed candidate> against <comparison base>
/prove <saved contract>; candidate <changed candidate>
```

For `NO CHANGE` or `BLOCKED`, identify the requirement IDs and exact missing
input or decision; if a command can resolve it, give the configured command
and expected result. Do not request a new proof until the blocker is resolved.
