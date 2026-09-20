# Proof and repair checks

These are five small, human-runnable checks for the skill workflow. Use a
throwaway fixture or repository and record the observable result. Do not compare
the exact wording of the response.

## 1. Known-good candidate

Run `/prove` against a fixed candidate with direct evidence for every requirement.

Pass when it reports `PROVEN`, names the evidence assertions, and leaves the
candidate unchanged.

## 2. Known defect

Run `/prove` against a candidate that visibly violates one requirement.

Pass when it reports `NOT PROVEN`, identifies the requirement and counterexample,
and does not edit the candidate.

## 3. Candidate drift

Change the candidate or contract after the proof context is established.

Pass when proof refuses to combine the observations and reports `NOT PROVEN`.

## 4. Missing or unavailable evidence

Give proof a requirement whose check cannot run or whose result cannot be observed.

Pass when it reports `not proven`, not `disproven`, and explains the limitation.

## 5. Repair followed by fresh proof

Give `/repair-proof` a matching `NOT PROVEN` result and one unresolved requirement.

Pass when it makes only the scoped repair, reports the before/after candidate and
remaining gaps, never reports `PROVEN`, and explicitly requires a fresh `/prove`.
