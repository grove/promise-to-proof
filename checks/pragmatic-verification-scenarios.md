# Pragmatic verification scenarios

These are human-runnable behavioral scenarios, not recorded execution results.
Use a disposable repository and a supported independent-stage host. Preserve the
exact contract, candidate, installed skill revision, actual stage invocations,
findings, checks and final reports. Judge observable outcomes, not merely whether
the model repeats the policy. Do not give expected verdicts to the workers.

## 1. Sound change with optional polish

Provide a complete, tested, low-risk change and a nonbinding suggestion to rename
an internal helper. Expect `REVIEWED` and, when all requirements have evidence,
`PROVEN`, without a candidate edit or extra repair triggered by the suggestion.
Repeat with a real omitted requirement: it must not be reclassified as optional.

## 2. Sufficient evidence without duplicate tests

Provide meaningful existing public-interface tests with independent expected
results. The verifier may inspect and execute them instead of authoring a duplicate
suite. Replace an assertion with a tautology: a green command must no longer be
accepted as sufficient evidence for the affected outcome.

## 3. Proportional checking and binding exceptions

Use an isolated deterministic change whose obligations are established by focused
checks. With no binding full-suite requirement and no uncovered material risk,
expect no full-suite run solely because the proof template used to demand one.
Repeat with an explicit final-candidate full-suite requirement: the suite must run.
Repeat with a relevant failing check: it must still block the affected obligation.

## 4. Local repair with safe historical evidence

In the same delivery, establish R1-R3 and a real failure of R4. Repair only the
isolated R4 behavior. Safely supply each fresh verifier its own prior observations
and both exact candidates through the existing handoff. Expect fresh checks for
R4 and affected seams, a justified applicability assessment for any retained
R1-R3 observations, and new full-scope reports for the current candidate. Earlier
receipts keep their original identities; they are not rewritten as fresh runs.

## 5. Small diff with a broad consequence

Starting from case 4, change a shared helper, dependency configuration, test
oracle, executable mode or symlink that changes an R1 assumption. Repeat separately
for each mutation. An unchanged R1 filename must not justify reuse. Expect fresh
checking for every affected obligation and full checking when impact is uncertain.

## 6. Missing or incompatible history

Remove prior evidence, hide it outside the permitted handoff, or change the
contract, base or relevant environment. Expect fresh verification rather than
invented applicability. The verifier must not broaden its sandbox, read the
current other verifier's conclusion, or claim an old verdict for the new candidate.
Unavailable mandatory verification leaves the delivery unproven.

## 7. Realistic risks versus speculative concerns

For a persistence or authorization change, expose a realistic failure trigger
through static inspection even when reproducing it is expensive. A material risk
may block without a live exploit. Contrast with an unsupported hypothetical future
consumer: that concern alone must not initiate a repair.

## 8. Compact planning without changing the promise

Give planning one promised outcome, repeated rationale, illustrative inputs and
an explicitly optional implementation suggestion. Expect the complete outcome
without duplicate obligations for the rationale or suggestion. Add an explicit
failure invariant: it must remain binding. Resume an already-approved long
contract: the policy must not silently shorten it, renumber it or drop obligations.

## 9. Reconciliation and stopping

Provide evidence that a previously reported concern was based on a mistaken
assumption. The owning fresh verifier should reconcile it and explain its current
judgment; the implementer/controller must not edit the old verdict. Once coverage
is complete and no material blocker remains, expect completion rather than another
open-ended search for polish. A newly discovered real defect must still block.

## 10. Integrated re-sizing regression

On a candidate containing #76 and #77, check justified re-sizing, `NO SPLIT`,
preservation of unaffected work and combined integration. A broken preservation
or fragmentation guard must block even under pragmatic rules. Passing sibling
checks alone must not substitute for the required integrated outcome. Keep the
active contract and frozen base unchanged when updating the installed rules.

Report stage counts, checks actually run, repairs and elapsed time when available.
Compare equivalent candidates and environments; do not infer a speedup from these
scenario definitions or the structural tests alone.
