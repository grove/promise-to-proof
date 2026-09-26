---
name: plan-acceptance
description: Plan a spec, ticket, or conversation as a versioned acceptance contract with stable requirements, seams, oracles, and evidence plans.
disable-model-invocation: true
---

Turn source promises into a candidate-independent acceptance contract. This skill
plans acceptance. It does not implement or verify. A direct issue invocation
also publishes a planning handoff under the protocol's standalone planning rules.

Before planning, read the [acceptance contract protocol](references/acceptance-contract-protocol.md).
It defines the spec envelope, revision rules, evidence terms, and handoffs.

## Build the contract

1. Resolve `work/<slug>.md` using the protocol's naming and collision rules.
   For an issue input, read the configured tracker instructions and the issue's
   body, comments, existing planning handoffs, approvals, and amendments first.
   A standalone local work item needs neither a specification nor a tracker.
   Normalize minimal acceptance bullets into the matrix below in that same file;
   preserve existing IDs and promises. Import external source promises locally
   when requested; the tracker remains an optional source or mirror. Retain
   imported binding text in the work item or a linked local source file, with
   its external URL and retrieval identity as attribution. An external URL alone
   is not a live hashable binding input.
   Read the source, existing contract, pending amendments, and
   applicable parent contract. If the source cannot be established, report the
   gap and stop.
   For a sliced child, retrieve its decomposition, precise contribution,
   prerequisites, and exact parent snapshot under the protocol's parent/child
   rules. Compare the current parent and pending amendments before planning;
   resolve material mismatches rather than silently adopting a changed parent.
   When present, read the project's advisory learning register (by default
   `docs/retrospective-learnings.md`). Consider relevant `active` accepted
   learnings; record which were used with their IDs and evaluation references,
   and why others were inapplicable. Superseded advice and an absent register
   are not planning blockers. A learning is advice, never authority to add a
   requirement, exclusion, standard, or revision without support from the
   current source and its approval process.
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

Save and reread the contract at `work/<slug>.md` before handing off. Keep a
lasting optional specification in `specs/`, and link it with `Source`. Link a
parent work item with `Parent` and retain its exact snapshot and contribution
mapping. Preserve previous revisions under the protocol's history rule. If
this context cannot write, return the exact text to the enclosing workflow to
save and reread, and report storage pending until it confirms retrieval.
Saving local files does not authorize staging, commits, or tracker publication.

For a direct user invocation on an issue, publish and verify the shared planning
handoff under the protocol's standalone planning rules. A local-only or draft-only
request suppresses that write. An invocation inside delivery stays local under
the enclosing workflow's authority. Return the comment URL and exact proposal
needing approval; publication does not approve it. If publication or readback
fails, retain the local proposal and report the incomplete issue handoff.

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
Source: <relative Markdown link to binding local spec/source text; omit for a standalone work item>
Source attribution: <external issue/spec URL and retrieval identity, if imported>
Parent: <relative Markdown link to parent work item and revision, or None>
Parent snapshot: <immutable reference or retrievable captured text and digest; omit if none>
Contribution: <decomposition reference, qualified parent obligations and precise contribution; omit if none>
Prerequisites: <references and required outcomes, or None>

Intended outcome: <observable user or operator outcome>

Advisory learnings: <active IDs considered and why used or inapplicable; None if no register>

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
Capture the resulting candidate for separate /review-implementation and /prove phases.

## Proof handoff

Evaluate every requirement against this contract revision and one fixed candidate.
Record actual evidence and verdicts in a separate proof report.
```

After the contract, end with `Next steps:` and a numbered list (`1.`, `2.`, ...)
of applicable actions in order, so each can be referenced by number. When the
contract is saved, approved, and has no blocking gaps, give
`/deliver-issue <issue>` for a published issue handoff, otherwise
`/implement-contract <canonical contract reference>`; the optional audit is
`/audit-acceptance <proposed contract> against <source>`. If saving or approval
is pending, name the exact destination or proposal needing approval. If a row
is `gap`, state its missing seam, oracle, or evidence input and do not direct
the user to implementation until it is resolved. Do not invoke the next skill.
