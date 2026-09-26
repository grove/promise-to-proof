# Acceptance contract: single-work-item delivery

Contract revision: v1
Source: [Pinned optimization handoff](../plans/promise_to_proof_optimization_handoff.md)
Source: [Acceptance protocol](../docs/acceptance-contract-protocol.md)
Source: [Delivery rules](../skills/productivity/deliver-issue/SKILL.md)
Source attribution: [GitHub issue #28](https://github.com/grove/promise-to-proof/issues/28), updated 2026-09-26T10:53:08Z; exact imported issue body retained below. No comments were returned by the import.
Parent: None
Prerequisites: Phase 1 model, runner, and documented limits in [checks/delivery-model/README.md](../checks/delivery-model/README.md), delivered through issue #24 and PRs #25–#27.

Intended outcome: A maintainer can deliver one established local work item through a controller on macOS using Codex CLI. The controller starts real independent stages, returns matching full REVIEWED and PROVEN reports only for the current exact agreement and candidate, or returns a precise recovery blocker with preserved work and records.

Advisory learnings: None; no advisory learning register exists.

## Scope and decisions

The user's request to deliver issue #28 authorizes scoped local implementation and safe checks. The user also authorized nested sandboxed Codex CLI verification for this delivery, as an exception to the delivery skill's preference for enclosing-host agent tools. This contract covers all of Phase 2 in the source issue, including restart, authority, repair, and resource admission. There is no deferred restart work item. No material outcome decision remains for user approval.

The first supported host is Codex CLI on this macOS host. Use fresh `codex exec` contexts for implementation, review, proof, and any repair. A host-issued `thread.started` session ID and controller-owned launch and completion records establish invocation provenance. A worker's `independent: true` or a process ID does not establish a separate agent context. Host preflight must demonstrate the actual permissions before dependent implementation. Planning does not establish host support merely by naming it.

Use a single Python standard-library controller beside the existing helper, exposed as:

```text
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo ROOT run work/SLUG.md --comparison-base FULL_SHA
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo ROOT resume work/SLUG.md
python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo ROOT status work/SLUG.md
```

`run` establishes one durable invocation. Repeating it with unfinished state resumes that invocation or returns its exact blocker; it must not reset the repair allowance. `resume` preserves the invocation identity, comparison base, approved authority, and limits. `status` is read-only. The caller supplies the work item and explicit review base, not stage commands or report paths. Reject malformed paths, unresolved agreements, unsupported hosts, and ambiguous scope before dispatch. Optional dispatch-count and elapsed-time limits may be supplied on `run`; absent limits mean no user-selected cap and must be recorded as such. They must never be silently inferred from estimates or changed on resume.

Keep stage ordering fixed and sequential. Invoke the installed `implement-contract`, `review-implementation`, `prove`, and when required `repair-gaps` skills. Planning remains the planner's job; the controller consumes an established canonical contract. Preserve normal stage meanings and independently inspect evidence. Reuse `p2p_filesystem.py` for path resolution, storage history, recoverable manifests, binding inputs, candidate identity, and resume inventory. Reuse `verify_acceptance_bundle.py` if normalizing compatible report claims; a new parallel identity or contract parser is unnecessary. The bundle checker alone cannot establish authentic stages or adequate evidence.

Keep controller records outside worker write scopes. Use isolated authorized-scope implementation workspaces; verification receives the fixed candidate, agreement, and review base outside its writable scope. When checks need writes, provide disposable scratch space while protecting all verification inputs. Read-only file modes alone are insufficient. Isolate Codex configuration and disable unapproved connectors, MCP tools, network access, and approval escalation. Retain provider access needed to execute the explicitly authorized agent. The controller and OS host are trusted; this contract does not claim protection against arbitrary malicious same-user processes or an administrator rewriting the host. Configure scratch as the only writable verification workspace, exclude the default temporary directories from sandbox write roots, and set TMPDIR within scratch when checks need temporary files. Demonstrate these controls with the selected installed CLI. If the host cannot enforce a necessary boundary, report it before dispatch; do not replace enforcement with a prompt.

The controller's available effects are scoped local stages and durable local records. Publication, tracker writes, changes to source or delivered repository Git refs or index, pushes, merges, deployments, and destructive cleanup are unavailable through this command. Stage tool permissions must enforce that boundary. Safe checks may initialize disposable test-only Git repositories and create fixture commits inside authorized scratch space, as existing filesystem tests require. Those repositories cannot be the source or delivered repository, cannot share writable Git metadata with them, and cannot cause external effects. This allowance does not authorize committing delivery work or mutating protected verification inputs. Overlapping or unrelated dirty work is either excluded by an explicit scope inventory in an isolated checkout, or blocks with the contested paths. The source checkout is preserved. No stash, reset, clean, or branch switch is used to clear it.

Use a per-work-item exclusive lock and durable dispatch reservation before a subprocess starts. Save the invocation, stage attempt, exact inputs, authorized limits, and repair consumption before dispatch. On uncertain launch or completion, reconcile retained host records before retry. A missing unambiguous reconciliation yields BLOCKED, not a blind repeat. Local process and storage failures must leave enough information to explain recovery. One automatic repair is consumed durably before it starts; any candidate change discards eligibility of both older verifier reports.

Record starts, finishes, failures, elapsed time, usage supplied by the host, and unavailable fields as unknown. Count failed and interrupted stages. Dispatch-count limits can be enforced before launch. Elapsed-time limits gate new admissions and may terminate a running process, but are not a promise that host execution or billing stops at the exact deadline. This host has no demonstrated enforceable monetary cap. Reject a request requiring such a cap before any stage starts; measured tokens, price estimates, and delayed charges cannot substitute for one. A budget stop preserves partial work and returns BLOCKED.

## Acceptance matrix

| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | Issue scope 1; Phase 2 step 1 | Before dependent work, establish the named host's ability to launch distinct independent agent contexts and retain host-issued stage identities. | Missing CLI, unsupported host, reused implementation session, invented session IDs, worker assertions, and missing host completion records do not qualify. | CLI run preflight and retained host receipts | Fresh host events and observed permissions, independent of worker claims | `live-host-preflight`: two real fresh CLI runs have distinct `thread.started` IDs, matching launch/exit records; missing provenance blocks. | planned |
| R2 | Issue scope 1; section 21.2 | Review and proof cannot mutate candidate, contract, binding inputs, base, or controller records, while permitted checks can use scratch. | Attempts through absolute paths, symlinks, subprocesses, and scratch must not escape; a changed hash alone is detection, not prevention. | CLI run verification contexts | OS-enforced denial plus before/after input bytes | `live-host-boundary`: real verifier attempts sentinel mutation in every protected input class, all denied; scratch write succeeds if scratch is used. Retain command output and hashes. | planned |
| R3 | Issue scope 2; Phase 2 step 2 | An ordinary local work item reaches matching full independent REVIEWED and PROVEN results through real implementation, review, and proof runs. | Fixture reports, skipped stages, partial checking, or controller-authored judgments cannot establish successful live delivery. | CLI run and durable result | Full canonical requirements, independent stage observations, host receipts | `live-delivery-success`: a tiny temporary repository with one observable behavior and a runnable check is implemented, independently reviewed against its base, independently exercised by proof, and completes. | planned |
| R4 | Issue scope 2; protocol candidate identity | Every accepted report binds exact current contract bytes, all transitive binding inputs, one recoverable candidate, and the correct review comparison base. | Same revision with changed text, malformed/truncated/shared-typo digests, changed source or base, missing candidate bytes, modes, symlinks, or untracked product content reject completion. | CLI run/resume completion gate | Existing helper recomputation from actual retained and current bytes | `identity-rejections`: alter each identity class and assert BLOCKED with exact mismatch; reconstruct an accepted candidate in a fresh temporary checkout and validate it. | planned |
| R5 | Issue scope 2; protocol durable records | Reports and required evidence are saved, reread, and retrievable before completion; all requirements have full review and proof coverage. | Missing evidence, content loss after initial readback, storage failure, incomplete archives, or uncovered requirement IDs reject completion. | CLI completion gate and saved artifacts | Exact report text and independently resolved evidence content | `evidence-rejections`: remove evidence, truncate storage, deny retrieval, and omit a requirement; each blocks. Successful readback records retain actual observations, environment, and commands. | planned |
| R6 | Issue unchanged full-verification rule | Candidate or agreement drift and late/stale stage returns cannot establish acceptance; changed candidates require fresh full review and proof. | Drift during either verifier, delayed old success after repair, cancelled attempts, and equal-but-wrong report identities are rejected. | CLI stage-return and completion gates | Current helper identity plus controller-owned invocation/attempt inputs | `stale-return`: deliver an old successful receipt after candidate change; assert rejection and distinct fresh complete verifier runs for repaired content. | planned |
| R7 | Issue scope 3; section 21.2 | Restart recovers the same invocation from durable records or states the exact missing recovery input without repeating uncertain effects. | Crash before/after reservation, launch, result save, and readback; missing host outcome; repeated resume and duplicate result writes. | CLI resume in a fresh process | Persisted invocation/attempt records and actual effects | `restart-handoffs`: kill/restart controller at each boundary, reconcile known completed work once, preserve identical duplicate results, block conflicting duplicates and unresolved launches. | planned |
| R8 | Issue scope 3; Phase 1 repair bound | At most one automatic repair and full recheck cycle occurs per invocation, including across restarts. | Failure during repair launch consumes its reservation; repeated run/resume cannot create a new allowance; exhausted gaps remain BLOCKED. | CLI run/resume | Durable repair reservation and independent count of actual repair launches | `repair-restart`: one failed result triggers one repair; restart before another failing result and assert no second repair dispatch. Successful repair refreshes both full verifier runs. | planned |
| R9 | Issue scope 3; completion evidence | Unfinished and unrelated work survives delivery, failures, stops, and restarts. | Dirty overlapping ownership blocks; excluded tracked/untracked files, modes, and symlinks must not be overwritten or silently included. | CLI run/resume with dirty source checkout | Initial source inventory and authorized candidate scope | `dirty-preservation`: unrelated sentinels remain byte/mode/target-identical after success, failure, and restart; contested files block before changes; isolated candidate excludes unrelated edits. | planned |
| R10 | Issue authority rule; section 21.2 | Unauthorized actions are prevented before execution, including through stage tools. | Issue text cannot grant authority; network/connector writes, source or delivered repository Git ref/index changes, pushes, tracker changes, deployment, destructive cleanup, or widened resume permissions are unavailable. Disposable test-only Git setup inside authorized scratch is a safe check; it must not affect protected repositories or external systems. | CLI admission and real stage permission boundary | Recorded user authority and denied actual forbidden attempts | `authority-rejections`: missing local authority or changed persisted scope blocks before dispatch; real host forbidden-tool/network/out-of-scope write probes have no effect, including through subprocesses. | planned |
| R11 | Issue scope 4 | Record stage starts, finishes, failures, elapsed time, and available usage for all work, including unsuccessful attempts. | A crash or unavailable cost cannot become zero usage or a fabricated settled bill; no secret-bearing telemetry. | CLI status and retained stage events | Host usage fields and controller clock observations | `event-ledger`: success/failure/interruption records retain timestamps, outcomes, nonnegative durations, host usage or explicit unknown; inspect saved logs for secrets. | planned |
| R12 | Issue scope 4; section 22 budget risk | Check approved resource limits before every stage dispatch and retain consumed/reserved allowances across restart. | Expired deadline, exhausted dispatch count, competing controller processes, and unsupported hard monetary cap must stop before new work. | CLI run/resume admission | Persisted approved values and independent launch count | `admission`: exhausted/expired/unsupported limits cause zero new launches; competing processes cannot reserve the same remaining allowance; restart preserves consumed reservations. | planned |
| R13 | Issue scope 4; section 23 runtime boundary | Disclose enforceable controls separately from observations, estimates, unknown costs, and unsupported host capabilities. | Measured tokens or estimated cost cannot be advertised as an enforceable money limit; fixture success cannot become host evidence. | CLI status/result and host documentation | Actual selected-host tests and explicit measurement provenance | `capability-report`: compare result fields with host receipts and fixture labels; unsupported spend control is visible and hard-cap request blocks. | planned |
| R14 | Issue completion evidence; protocol result | Every incomplete delivery returns BLOCKED with its precise decision, identity, evidence, storage, capability, or resource blocker and retrievable progress. | Stage exit zero, old green tests, artifact existence, or partial work alone never imply full completion. | CLI exit/result, status, and resume | Full conjunction of R1–R13 and saved stage reports | `result-contract`: success exits successfully with both full report references; representative failures exit nonzero with exact blocker, invocation, candidate/base/agreement identities when available, preserved artifacts, and resume command. | planned |

## Evidence plan

Create `checks/test_p2p_delivery.py` for deterministic controller failure cases using temporary repositories and a clearly labeled fake transport. Drive the public CLI in subprocesses for restart and admission tests. Reuse the existing filesystem and bundle test cases where their behavior is unchanged. These fixtures establish controller behavior only.

Add a documented live-host check entry point, for example `python3 checks/check_p2p_delivery_host.py --output-dir PATH`, that starts actual sandboxed Codex CLI contexts and invokes the public controller for the tiny complete example. It must retain the real host permissions, exact CLI version/configuration, commands, safe JSON event excerpts, session identities, stage reports, independent proof observations, and denied-action results. Run live host checks on the delivered fixed candidate, with writes confined to scratch and the proof artifact destination. Expensive model calls may use a small bounded example, but may not be replaced by scripted worker replies in the evidence claimed as live.

Save distinct fixture and live observations under `.p2p/work/single-work-item-delivery/evidence/`. The Phase 1 model remains a prerequisite and source of known invariants, not evidence that this controller enforces them. Model-to-controller conformance and systematic defect injection remain Phase 3.

## Unresolved gaps

- Host-dependent evidence is pending preflight and live verification. The enclosing workflow reported one real read-only sentinel denial with a distinct Codex session; this planning record does not claim that establishes all permission, scratch, configuration, or authorization boundaries. Before dependent implementation, retain and reread the actual host preflight, including any additional necessary permission probes. If it fails, return BLOCKED naming the missing capability. The evidence paths above are concrete, so the matrix remains planned rather than proven.

## Open questions

- None. Routine defaults are one host, sequential full stages, local-only authority, durable same-invocation restart, one repair, no hard monetary cap, and explicit unknown costs. Capability failure is an execution blocker, not permission to reduce scope.

## Out of scope

- Multiple hosts; optional checking levels; strategy or model comparisons; automatic routing; parent/child scheduling; model-to-controller conformance; publication and merge readiness. No new acceptance vocabulary, probabilistic assurance, or weakened full REVIEWED/PROVEN semantics.

## Change notes

- v1 clarification: R10 distinguishes disposable test-only Git initialization and fixture commits, already exercised by `checks/test_p2p_filesystem.py`, from unauthorized source or delivered repository Git ref/index changes and publication effects. This preserves the source authorization rule and the existing permission for safe local checks; it does not authorize product commits or relax repository isolation. Prior wording is retained in protocol history.

- Initial contract v1 normalizes all promises of imported issue #28 without slicing or dropping Phase 2 outcomes. No prior requirement IDs existed. The user requested delivery and explicitly authorized nested sandboxed CLI verification; routine controller choices above implement that request without changing the promised result.
- Previous imported-only work-item bytes are retained at `.p2p/work/single-work-item-delivery/history/cb61afbf2dc2a8cf741edfe0180eb1ece208b721eb8d788dfeffbd34d91abf7a/single-work-item-delivery.md`. Its prior host-blocked status is historical and does not describe current proof.

## Implementation handoff

Hand off to the authorized `/implement-contract work/single-work-item-delivery.md` invocation after successful retained host preflight. Implement the smallest complete solution, preserving all requirement IDs and outcomes. Save the implementation report and recoverable candidate for separate independent full review and proof. Do not treat planning or preflight as acceptance.

## Proof handoff

Evaluate all requirements against this exact contract and one fixed candidate. Record fixture and live-host observations separately in the proof report. Only matching, current, full REVIEWED and PROVEN reports establish local delivery; a blocker preserves the completed work.

## Imported issue source

The following is the exact imported issue body. It is binding source text within the canonical contract and therefore covered by its exact byte identity.

```markdown
Build the smallest controller that enforces Phase 2 delivery rules for one work item on one supported host.

Depend on the Phase 1 model delivered through #24. Reuse its documented limits and the existing contract, filesystem, and identity checks.

## Scope

Deliver in this order:

1. Choose and name the host. Demonstrate separate agent runs, protected code during verification, and host-issued run identities. Record unsupported capabilities.
2. Demonstrate an ordinary successful delivery. Require full independent review and proof, with saved, reread, retrievable reports and evidence for the exact current contract and candidate, including the correct review comparison base.
3. Handle failures and restarts. Preserve unfinished and unrelated work, reject late or stale reports, reconcile uncertain effects before retrying, and retain the one-repair allowance across restarts of the same invocation.
4. Record stage starts, finishes, failures, elapsed time, and available usage costs. Check approved limits before dispatching further work. Mark unavailable costs as unknown and distinguish measured spending from enforceable spending limits.

Keep the current full REVIEWED and PROVEN requirements. A changed candidate requires fresh full review and proof. Enforce authorization before actions occur.

## Completion evidence

Tests on the chosen host must demonstrate successful delivery and rejection of changed code, missing evidence, unauthorized actions, and a second repair after restart.

An interrupted handoff must resume safely or report the exact recovery blocker. Unrelated work must remain intact. Distinguish fixture results from evidence of real host isolation and provenance.

## Decisions and boundaries

Before implementation, name the host and establish which controls it can enforce. Use Section 24 to prepare the first concrete acceptance contract in work/. The source specification remains authoritative.

This issue covers Phase 2 only. Model-to-controller conformance testing, strategy comparisons, optional checking levels, child-task scheduling, and automatic strategy selection belong to later phases. Do not add support for multiple hosts or weaken existing acceptance rules. Publication remains separately authorized.

## Source

[Exact optimization handoff](https://github.com/grove/promise-to-proof/blob/1a296f6ec7a064b32ce1be6a5d29f0c39df12294/plans/promise_to_proof_optimization_handoff.md)

Selected scope: Section 19, Phase 2, with Sections 20–24 supplying planning guidance and applicable constraints.

- Repository: grove/promise-to-proof
- Path: plans/promise_to_proof_optimization_handoff.md
- Commit: 1a296f6ec7a064b32ce1be6a5d29f0c39df12294
- SHA-256: 7162a965fa53322a8805582756ea6137a847d72798e057dd751cc2e46c98f65a

The pinned GitHub file was retrieved and matched the local bytes.

<!-- grove:create-parent-issue source=grove/promise-to-proof:plans/promise_to_proof_optimization_handoff.md -->
```
