---
name: repair-gaps
description: Repair named implementation or evidence gaps from a NOT PROVEN proof, report the change honestly, and require fresh proof without declaring acceptance.
disable-model-invocation: true
---

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

1. Read the exact source contract revision and the `NOT PROVEN` proof result.
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
6. Hand off the changed candidate for separate `/review-implementation` and fresh proof.
   End with: **Fresh `/prove` required before acceptance.**

## Outcomes

- `REPAIRED`: the scoped change was made and focused checks passed.
- `NO CHANGE`: no safe or necessary change was made; explain why.
- `BLOCKED`: the inputs or required capability are unavailable or stale.

None of these outcomes accepts the ticket. A new `/prove` run must evaluate the
changed candidate against every requirement.

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

After the handoff, end with `Next step:` and one copy-ready action. For
`REPAIRED`, give the exact next invocation(s):

```text
/review-implementation <changed candidate> against <comparison base>
/prove <saved contract>; candidate <changed candidate>
```

For `NO CHANGE` or `BLOCKED`, identify the requirement IDs and exact missing
input or decision; if a command can resolve it, give the configured command
and expected result. Do not request a new proof until the blocker is resolved.
