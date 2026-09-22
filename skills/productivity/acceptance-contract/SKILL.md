---
name: acceptance-contract
description: Turn a spec, ticket, or conversation into a versioned acceptance contract with stable requirements, seams, oracles, and evidence plans.
disable-model-invocation: true
---

Turn source promises into a candidate-independent acceptance contract. This skill
plans acceptance. It does not implement, verify, or publish.

Before planning, read the [acceptance contract protocol](references/acceptance-contract-protocol.md).
It defines the spec envelope, revision rules, evidence terms, and handoffs.

## Build the contract

1. Resolve the canonical contract location using the protocol's durable handoff
   convention. Read the source, existing contract, pending amendments, and
   applicable parent contract. If the source cannot be established, report the
   gap and stop.
   For a sliced child, retrieve its decomposition, precise contribution,
   prerequisites, and exact parent snapshot under the protocol's parent/child
   rules. Compare the current parent and pending amendments before planning;
   resolve material mismatches rather than silently adopting a changed parent.
2. Reconcile existing acceptance criteria, including GitHub checkboxes, with
   the contract. Extract every material promise and necessary invariant. Keep
   source references so each criterion maps to its requirements without duplication.
   Map child rows through `Source` to qualified parent obligations. Preserve
   applicable inherited boundaries and exclusions while requiring only the
   child's outcome and contribution, not unrelated sibling functionality.
3. Give each independently falsifiable promise one row. Split compound criteria,
   merge duplicate claims, and record ID mappings when restructuring existing
   rows. Preserve existing IDs across reruns and allocate unused IDs for new rows.
4. Record boundaries supported by the source or required outcome: empty inputs,
   retries, restart, authorization, concurrency, or partial failure where relevant.
   Keep speculative behavior outside the contract.
5. Inspect agreed specification and TDD seams, public interfaces, existing tests,
   constraints, and configured commands. Reuse those seams and name an independent
   oracle and concrete evidence path for each row. Mark missing credible paths
   `gap` and explain what is missing.
6. Apply the protocol's revision rules. Record authorized material changes and
   retain prior revisions. Surface unresolved changes as questions rather than
   silently altering the agreement.

## Audit and hand off

Account for every source promise and justify every added invariant by the outcome
that requires it. Trace the workflow through completion, including necessary
state, persistence, and failure behavior. Check both missing substance and
unrequested scope. Keep implementation preferences out of requirements.

Return the contract using the shape below. Use only `planned` or `gap` for plan
state. Move any legacy proof verdicts into a separately identified proof report
with their original candidate and context, or flag missing provenance as a gap.

Include a storage handoff naming the canonical destination and revision, and
whether saving remains pending. The invoking workflow saves the returned text
and confirms retrieval as the protocol requires; planning does not publish it.

For a tracked child, hand readiness reconciliation to that invoking workflow.
After saving and rereading the contract, it checks configured triage meanings,
required approvals, unresolved decisions, and availability of prerequisite
outcomes. With label-edit authority, it applies `ready-for-agent` only when the
child is ready for unattended implementation and preserves unrelated labels.
Otherwise report the remaining blockers or pending label update. Recheck when a
prerequisite becomes available; contract creation alone does not grant readiness.

## Output

```markdown
# Acceptance contract: <source>

Contract revision: v1
Source: <issue/spec and precise criterion references>
Parent contract: <canonical location and revision, or None>
Parent snapshot: <immutable reference or retrievable captured text and digest; omit if none>
Contribution: <decomposition reference, qualified parent obligations and precise contribution; omit if none>
Prerequisites: <references and required outcomes, or None>

Intended outcome: <observable user or operator outcome>

## Acceptance matrix

| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | <criterion> | <one observable promise> | <what would falsify it> | <agreed public interface> | <independent expected result> | <named case and assertion, invariant check, or exact command> | planned |

## Unresolved gaps

- <missing evidence path, seam, or oracle, or None>

## Open questions

- <unresolved product or design decision, or None>

## Out of scope

- <excluded nearby concern, or None>

## Change notes

- <revision, affected IDs, old/new agreement and authorization; ID mappings, or Initial contract>

## Implementation handoff

Hand off to an explicitly authorized /implement-contract invocation.
Implement the smallest complete solution inside the spec envelope.
Preserve requirement IDs and promised outcomes.
Capture the resulting candidate for separate /review-contract and /prove phases.

## Proof handoff

Evaluate every requirement against this contract revision and one fixed candidate.
Record actual evidence and verdicts in a separate proof report.
```
