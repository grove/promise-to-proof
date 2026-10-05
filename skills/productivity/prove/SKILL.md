---
name: prove
description: Verify an implemented issue against its promises without changing the candidate, and report PROVEN or NOT PROVEN with concrete evidence.
disable-model-invocation: true
---

`/prove` checks whether a ticket, specification, or agreed outcome is actually
met. It verifies a fixed candidate and reports gaps; it does not repair the
candidate. Use `/repair-gaps` for scoped repairs, then run `/prove` again.
`/implement-contract` develops the candidate; `/review-implementation` separately
examines contract fidelity, scope, and engineering quality. Neither replaces proof.

Before verification, read the [acceptance contract protocol](references/acceptance-contract-protocol.md).
It defines the spec envelope, identities, evidence, and verdicts.

Optional [evidence-record v1](../../../docs/evidence-record-v1.md) records may be cited
by evidence ID and computed SHA-256 digest, and their deterministic Markdown
rendering may be embedded in `proof.md`. Validate records against the exact proof
context when available. Records are optional and a valid record never implies a
verdict: requirement-level `proven`, `not proven`, and `disproven` judgments remain
in `proof.md`, owned by `/prove`. Without host-issued command/test receipts, keep
self-run command observations directly in `proof.md`.

## Verdicts

- `PROVEN`: every material requirement has credible evidence, no contract
  discrepancy remains, and the candidate stayed fixed during verification.
- `NOT PROVEN`: any requirement lacks evidence, a counterexample remains, the
  contract is incomplete or ambiguous, required verification is unavailable,
  or candidate identity is uncertain.
- A concrete violation is `disproven`; unavailable or inconclusive evidence is
  `not proven`, not `disproven`.

## Rules

- Reconcile the versioned acceptance contract with the source and authorized
  amendments. Report discrepancies without narrowing or rewriting the contract.
- Judge requirement evidence independently of overall PR status, following the
  protocol's proof and merge readiness rules. Leave unrelated CI repair to
  `/fix-pr` without waiting for green checks or making it a prerequisite to proof.
- Use a clean commit as the candidate when possible. A dirty or changing
  worktree is `NOT PROVEN` unless its exact snapshot can be established.
- A proof run may not mutate product files, the candidate, or contract. If any such
  change occurs, return `NOT PROVEN` and discard observations from the changed
  state; the repair belongs to `/repair-gaps` and requires a fresh `/prove`.
- Do not edit product code, tests, CI configuration, or the acceptance contract.
- Do not commit, push, publish, or declare a repair.
- Prefer behavioral evidence through public interfaces and independent oracles.
- A test that only runs a path, uses a tautological assertion, or relies on a
  mock that cannot fail does not prove the promised result.
- Reject stubbed or fixture-specific behavior, mock-only substitutes, and
  evidence that bypasses required production state. Distinguish a demonstrated
  violation from a weak check that leaves the outcome unknown.
- Judge the complete promised capability. Do not penalize a small implementation
  for lacking unnecessary architecture. Report unrequested scope against the
  contract's exclusions or source reconciliation, not architectural taste.


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

## Workflow

### 1. Establish the contract

Accept `.p2p/work/<slug>/contract.md` and discover its linked inputs, `candidate.json`, and
reports in `.p2p/work/<slug>/` using the protocol's durable handoff convention.
Read the source, pending amendments, applicable parent constraints,
and exact acceptance contract revision. Preserve all requirement IDs, boundaries,
seams, oracles, open questions, and exclusions. Report omitted, conflicting, or
ambiguous source promises instead of editing the contract. If no versioned
contract can be established, report `NOT PROVEN` and hand off to
`/plan-acceptance`; do not create or revise it during proof.

For a sliced child, retrieve the decomposition, contribution mapping, parent
snapshot, and prerequisite outcomes. Follow the protocol's parent/child rules
to reconcile the current parent and amendments. Judge the child's own contract
with applicable inherited constraints; unrelated sibling functionality is not
a child requirement. A material unresolved parent change is `NOT PROVEN` for
the current agreement. Capture and recheck applicable parent identities with
the child contract. For parent proof, evaluate all parent obligations and
cross-slice interactions on one exact integrated candidate. Historical child
proofs and closed issues are references, not an aggregated parent verdict.
Recover the approved delivery plan and parent completion conditions under the
protocol's Epic delivery plans rules. Include independently landed contributions
and required final-destination integration in the exact parent candidate. A
failing interaction leaves the parent unproven even when every child passed.
All-independent delivery needs combined parent verification, not an empty PR.
A destination-only change does not change product promises or establish proof
of a different candidate.

### 2. Identify the candidate

Record the full commit SHA or exact snapshot, contract source and revision,
captured contract identity, target or base when relevant, and verification
environment. Follow the protocol's identity rules and confirm both identities
before checks begin. Validate the work-item hash, binding parent/spec hashes,
and comparison-base SHA against `candidate.json`. Compare product content
outside `.p2p/`; local `.p2p/` record updates retain the original candidate
identity and stay out of Git history.
If any identity cannot be established, return `NOT PROVEN`.
If the candidate or contract drifts, or observations cannot be tied to them,
return `NOT PROVEN`.

For an admitted delivery, bind proof to its validated comparison base and exact
candidate. A later destination move alone does not change either identity. Proof
does not establish that the candidate is compatible with newer destination
commits.

### 3. Map and audit evidence

For every requirement, name the observation and the independent oracle that says
whether it passes. Check existing tests, invariants, schemas, and commands at the
agreed public seam. If a seam or oracle needs a consequential change, report the
decision as a gap rather than silently replacing it. A passing suite or checked
GitHub criterion does not cover a promise whose result is never asserted.

### 4. Hunt counterexamples

Check realistic boundaries: empty/one/many, state transitions, retries, restart,
authorization, concurrency, and the final workflow outcome. When useful, run a
controlled sensitivity check only in a disposable copy; discard it afterward.

### 5. Verify without mutation

Run the smallest high-signal checks that establish the requirements. Preserve
durable evidence outside the candidate and tie each reference to its observation,
assertion, command, and environment. The saved proof report may hold the evidence
itself under the protocol's evidence rules. Check product content outside
`.p2p/`, the candidate, and captured contract again afterward. Never fix a failure in this skill. Report
the smallest complete repair needed and name the affected requirement IDs for
`/repair-gaps`.

Before a long suite, verify its setup in the exact disposable workspace that will
run it: interpreter path and version, required imports, working directory, clean
`.p2p/` state, and candidate identity. A check from the source checkout does not
establish the nested runner's environment. Save this preflight with the command
and environment. Run the full suite once on a clean copy of the final frozen
candidate; use focused checks to guide repairs before that run. If setup invalidates
an attempt, correct the setup and rerun once. Do not launch duplicate full-suite
attempts in parallel or treat setup failures as candidate evidence.

### 6. Report

Save and reread `.p2p/work/<slug>/proof.md` and safe retained evidence in
`evidence/`, preserving prior runs under the protocol's history rule. Saving
generated records outside the product candidate is permitted. A read-only
stage context returns exact text for the enclosing workflow to save and reread.
Temporary files cannot be required to resume. For unsuitable evidence, retain
a safe durable reference, checksum, description, and access limits; without
a safe durable copy, report that evidence unavailable.

Return the intended outcome, contract reconciliation, candidate, environment,
every requirement verdict, evidence observations, counterexamples, candidate
stability, and unresolved gaps. A proof result must account for every requirement
ID and must not hide an unmet promise.

## Output

```markdown
# <PROVEN | NOT PROVEN>: <source>

Requirements: <proven>/<total>
Counterexamples tested: <count>
Contract: <.p2p/work/<slug>/contract.md and exact revision>
Contract snapshot: <immutable reference or captured text and digest>
Parent context: <parent identity, snapshot, contribution mapping and prerequisites; omit if none>
Candidate: <commit or exact snapshot>
Candidate stability: <unchanged or NOT PROVEN>
Contract stability: <unchanged or NOT PROVEN>
Verification context: <environment>

## Outcome

<intended result and why it is or is not established>

## Requirement verdicts

| ID | Observation and oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | <observed outcome and independent expected result> | <saved report section, artifact, or run; command and assertion> | proven |

## Unresolved gaps

- <requirement, counterexample, or limitation, or "None">

## Repairs needed

- <requirement ID and smallest complete repair, or "None">

Fresh `/prove` is required after any repair.
Refresh `/review-implementation` for the changed candidate as a separate phase.
```

After the report, end with `Next steps:` and a numbered list (`1.`, `2.`, ...)
of only the applicable actions, in order, so each can be referenced by number.
For `PROVEN`, if review is missing give `/review-implementation <saved candidate>
against <comparison base>`. When matching full review and proof exist, state
that acceptance evidence is complete for this candidate. For an existing PR
near merge, give
`/merge-readiness <PR URL>; review <saved review>; proof <saved proof>`.
For an existing PR not yet near merge, mention any known pending gates and
give `/merge-readiness <PR URL>; review <saved review>; proof <saved proof>`
for when the PR approaches a merge decision; do not assess PR gates in this proof.
If no PR exists, say no further action is required unless publication is wanted;
only then give this optional publication preview invocation with the saved references:

```text
/publish-pr <candidate handoff>; review <saved review>; proof <saved proof>; target <branch>; draft only
```

For `NOT PROVEN`, give
`/repair-gaps <saved proof>` for scoped repair or
`/plan-acceptance <source>` for a missing or changed agreement. If candidate
identity or evidence is uncertain, state the exact identity/evidence needed;
when rerunning a check, include its recorded command and expected result.
