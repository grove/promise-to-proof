---
name: plan-acceptance
description: Plan a spec, ticket, or conversation as a versioned acceptance contract with stable requirements, seams, oracles, and evidence plans.
disable-model-invocation: true
---

## Delegated continuation

When an enclosing workflow delegates planning through a selected standing
mandate, resolve in-scope questions and apply source-preserving recommendations
without asking again. Preserve promises, exclusions, constraints, links and IDs.
Adoption requires a new revision when material, retained prior bytes, independent
audit, and recorded mandate attribution. In controller planning sessions return
the proposed text in the requested schema; the controller owns storage/adoption.
A product change outside the mandate still names the missing decision authority.


Turn source promises into a candidate-independent acceptance contract. This skill
plans acceptance. It does not implement or verify. A direct issue invocation
also publishes a planning handoff under the protocol's standalone planning rules.

Before planning, read the [acceptance contract protocol](references/acceptance-contract-protocol.md).
It defines the spec envelope, revision rules, evidence terms, and handoffs.

## Build the contract

1. Accept a supported tracker issue, direct agreed text, or project-authored
   source file from any repository path, including `specs/` and `work/`. Derive
   the work-item slug and save the generated contract at
   `.p2p/work/<slug>/contract.md`; check for conflicts before writing.
   For an issue input, read the configured tracker instructions and the issue's
   body, comments, existing planning handoffs, approvals, and amendments first.
   A standalone local work item needs neither a specification nor a tracker.
   Normalize minimal acceptance bullets into the matrix in the generated contract;
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
7. Before presenting a proposal, audit the source and relevant project context
   for applicable ambiguity, contradiction, missing success or failure behavior,
   important implied edges or invariants, regression constraints, unclear scope,
   unverifiable promises, unavailable evidence or authority, and assumptions
   about environment, data, timing, ordering, permissions, compatibility, or
   external systems. For each material finding, capture the accepted outcome or
   boundary, a named evidence gap, or an open question. Apply only relevant
   categories; do not invent requirements or force every category into each
   contract. Keep the audit concise and proportional to risk.
8. Gate each accepted row on an observable expected result, an agreed credible
   seam, an independent oracle, and a concrete evidence path; name the missing
   seam, oracle, or evidence when one is unavailable. Keep evidence gaps distinct
   from unresolved product decisions. Ask the requester and block implementation
   only when uncertainty could change correctness or scope; do not guess. Do not
   hand off as ready while such a question remains open.
9. When rerunning planning for an approved contract, verify and preserve its exact
   approved bytes, revision, requirement IDs, and approval binding. Unchanged or
   evidence-only reruns keep those identities unchanged. A material change may
   replace the canonical contract only through the normal explicitly authorized
   revision process; record the authorization, old and proposed agreement, and
   any ID mapping, and retain the prior exact bytes. Without that authorization,
   leave the approved contract unchanged and surface the proposed change as an
   open question.

## Assess and retain delivery shape

After the promised outcome and acceptance rows are clear, ask whether the complete
work item can reasonably be implemented, independently reviewed, and proven as
one bounded delivery. Recommend one advisory route:

- `Direct delivery` when the outcome is clearly coherent and manageable in one
  delivery cycle.
- `Sizing inspection` when the outcome is clearly broad, or boundary uncertainty
  materially affects reliable implementation, independent review, or proof.
- `Deferred` only while an unresolved product outcome prevents the agreement
  from being established. Resolve that outcome through acceptance planning; do
  not use slicing to decide it.

Do not trigger sizing from multiple acceptance rows, ordinary implementation
uncertainty, unfamiliarity, a difficult algorithm, missing historical
measurements, or file, line, word, test, time, token, story-point, component, or
child counts. These may be recorded as observations, never as thresholds.

Save and read back `.p2p/work/<slug>/delivery-shape.md` under the existing local
P2P storage and history rules. Bind it to the exact canonical contract path,
revision, and SHA-256 plus every applicable source, specification, parent, and
approved-plan identity. Include the route, a concise evidence-based reason,
inspected context with retrievable paths/revisions, assumptions, the applicable
slicing result (`none`, exact `NO SPLIT`, or the approved plan identity), one
earliest next action, and outstanding gates. Keep rationale concise; do not
store hidden reasoning. Recompute hashes after readback. A contract or binding
input change makes the recommendation stale and requires a fresh assessment;
preserve prior records.

Use exactly one immediate next action: resolve an open outcome, obtain required
approval, resolve a material evidence gap or prerequisite, repair storage, run
`/deliver-issue <contract>` for direct delivery, or run
`/slice-contract <contract>` for sizing inspection. When a gate is pending,
record the recommended later route separately but make that gate the sole next
action. Direct delivery is advisory only: it changes neither the agreement nor
readiness/admission state and authorizes no external effect.

## Audit and hand off

Account for every source promise and justify every added invariant by the outcome
that requires it. Trace the workflow through completion, including necessary
state, persistence, and failure behavior. Check both missing substance and
unrequested scope. Keep implementation preferences out of requirements.

Return the contract using the shape below. Use only `planned` or `gap` for plan
state. Move any legacy proof verdicts into a separately identified proof report
with their original candidate and context, or flag missing provenance as a gap.

Save and reread the contract at `.p2p/work/<slug>/contract.md` before handing off. Keep a
lasting optional specification in `specs/`, and link it with `Source`. Link a
parent work item with `Parent` and retain its exact snapshot and contribution
mapping. Preserve previous revisions under the protocol's history rule. If
this context cannot write, return the exact text to the enclosing workflow to
save and reread, and report storage pending until it confirms retrieval.
Saving local files does not authorize staging, commits, or tracker publication.

Refresh the portable checkpoint after saving the proposal, approval receipt or
approved revision and before handing off: `python3 <skill-dir>/scripts/p2p_filesystem.py
--repo <root> checkpoint .p2p/work/<slug>/contract.md`. The default
`p2p-state/<slug>.json` is suitable for Git; an explicitly selected issue is the
alternative under the protocol's portable checkpoint rules. Preserve exact
approval-bound history and binding inputs. Report its path, bytes and
`LOCAL_ONLY`/`COMMITTED`/`PORTABLE` preservation status separately from approval.
Never call local files disposable without verified shared readback.

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

For `Direct delivery`, hand off through `/deliver-issue`; its existing #60
admission must pass before it invokes implementation. For `Sizing inspection`,
hand off to `/slice-contract` before implementation. Implement the smallest
complete solution inside the spec envelope, preserve requirement IDs and
promised outcomes, and capture the candidate for separate
/review-implementation and /prove phases.

## Proof handoff

Evaluate every requirement against this contract revision and one fixed candidate.
Record actual evidence and verdicts in a separate proof report.
```

After the contract, end with `Next steps:` and a numbered list (`1.`, `2.`, ...)
of applicable actions in order, so each can be referenced by number. The sole
immediate action follows the saved delivery-shape record: `/deliver-issue
<contract>` for `Direct delivery`, or `/slice-contract <contract>` for
`Sizing inspection`. If approval, an open outcome, evidence gap, storage failure,
or prerequisite is pending, name that gate as the sole next action and keep the
route conditional. The optional audit is `/audit-acceptance <proposed
contract> against <source>`. Never bypass direct routing or #60 admission by
handing straight to `/implement-contract`. Do not invoke the next skill.
