---
name: repair-proof
description: Repair named implementation or evidence gaps from a NOT PROVEN proof, report the change honestly, and require fresh proof without declaring acceptance.
disable-model-invocation: true
---

`/repair-proof` is the repair step after `/prove`. It consumes the source
contract, the proof result, the matching candidate, and specific unresolved
requirement IDs. It repairs only those gaps and never replaces fresh proof.

## Guardrails

- Confirm that the proof, contract, and candidate still match before editing.
- Edit only the implementation or evidence needed for the named requirements.
- Preserve the source requirements and existing valid checks.
- Do not publish, commit, push, or declare `PROVEN`.
- If inputs are stale, ambiguous, or unavailable, report `BLOCKED` without editing.

## Workflow

1. Read the source contract and the `NOT PROVEN` proof result.
2. Confirm the candidate identity and the unresolved requirement IDs.
3. Apply the smallest scoped implementation or evidence repair, when editing is authorized.
4. Run the focused check and inspect the resulting diff.
5. Report the candidate before and after, changed files, addressed requirements,
   changed evidence, and remaining gaps.
6. End with: **Fresh `/prove` required before acceptance.**

## Outcomes

- `REPAIRED`: the scoped change was made and focused checks passed.
- `NO CHANGE`: no safe or necessary change was made; explain why.
- `BLOCKED`: the inputs or required capability are unavailable or stale.

None of these outcomes accepts the ticket. A new `/prove` run must evaluate the
changed candidate against every requirement.

## Handoff format

```markdown
# <REPAIRED | NO CHANGE | BLOCKED> — <source>

Candidate before: <identity>
Candidate after: <identity or unchanged>
Addressed requirements: <IDs or None>
Changed files: <files or None>
Focused checks: <observations and assertions>
Remaining gaps: <IDs and reasons, or None>

Fresh `/prove` required before acceptance.
```
