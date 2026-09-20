# Proof and repair checks

These are five small, human-runnable checks for the skill workflow. Use a
throwaway fixture or repository and record the observable result. Do not compare
the exact wording of the response.

## 1. Known-good candidate

Run `/prove` against a fixed candidate with direct evidence for every requirement.
Record the candidate identity before and after the run.

Pass when it reports `PROVEN`, names the evidence assertions, and the recorded
candidate identity and acceptance source are unchanged.

## 2. Known defect

Run `/prove` against a candidate that visibly violates one requirement.

Pass when it reports `NOT PROVEN`, identifies the requirement and counterexample,
and the candidate identity and acceptance source are unchanged.

## 3. Candidate drift during proof

Establish the candidate and contract identity, then change either one before the
proof finishes. In a throwaway fixture, also test the case where a failing check
tempts the verifier to modify the candidate.

Pass when proof detects the mismatch or mutation, refuses to use observations
from the changed state, reports `NOT PROVEN`, and does not silently repair it.

## 4. Missing or unavailable evidence

Give proof a requirement whose check cannot run or whose result cannot be observed.

Pass when it reports `not proven`, not `disproven`, and explains the limitation.

## 5. Repair followed by fresh proof

Give `/repair-proof` a matching `NOT PROVEN` result and one unresolved requirement.

Pass when it makes only the scoped repair, reports the before/after candidate and
remaining gaps, preserves the acceptance source, never reports `PROVEN`, and
explicitly requires a fresh `/prove`.
