# Promise to Proof
## Adaptive delivery and assurance optimization
### Detailed technical handoff

**Status:** Delivery roadmap and supporting research; each delivery still needs its own acceptance contract.

**Roadmap updated:** September 26, 2026.

**Prepared:** September 25, 2026.

**Audience:** Promise to Proof maintainers, implementing agents, formal-model authors, and evaluation owners.

**Original research baseline:** `grove/promise-to-proof` at `f5917ce0471d56aac01711e720426748626c99d0`.

**Primary scope:** `/deliver-issue`, with a later extension to `/slice-contract` dependency graphs.

**Companion formats:** The Word edition contains the original research handoff. This Markdown roadmap has since been updated.

> **Product direction:** Choose a delivery strategy that balances assurance, elapsed time, monetary cost, and developer attention. Model choice, verification depth, retries, decomposition, and scheduling are controls—not goals in themselves. Lower assurance can be a legitimate choice; misleading claims and unauthorized effects cannot.

## Start here

We want software delivery that is reliable, affordable, and easy to follow. First we check the rules. Then we make the running software enforce them. Only after that do we try to make delivery faster or cheaper.

Issue #24 is closed. Its completion-integrity model and publication safety work were merged in [PR #25](https://github.com/grove/promise-to-proof/pull/25), [PR #26](https://github.com/grove/promise-to-proof/pull/26), and [PR #27](https://github.com/grove/promise-to-proof/pull/27). The model has 43 checks, including deliberately broken versions that it correctly rejects. It checks a simplified lifecycle; it does not establish that real agents always follow the rules.

The next delivery is a small program that enforces those rules on one supported agent host. A host is the application that starts agents and controls their access to files and tools.

Read [the delivery phases in order](#19-delivery-phases-in-order) for what we will build and how we will know each phase is finished. That section is the implementation order and takes precedence over earlier research suggestions about doing work in parallel. The remaining technical sections explain the background and possible designs.

## Reading guide

Read Sections 1–5 for the product decisions and compatibility boundaries. Sections 6–10 describe the proposed architecture and FizzBee model. Sections 11–15 cover economics, models, scheduling, and optimization opportunities. Sections 16–21 define measurements, experiments, delivery work, and acceptance gates. Sections 22–24 provide risks, open decisions, and the next-agent assignment. Appendices contain illustrative schemas, terminology, and source references.

**Evidence labels used throughout:** “Current” means supported by the inspected repository. “Direction” means an expressed user preference from this discussion. “Proposal” means a design recommendation that still needs review. “Hypothesis” means an effect to measure, not an established performance claim. Numeric examples are synthetic unless explicitly described otherwise.

**Historical execution status:** The September 25 research handoff did not implement or execute a model, controller, or optimization experiment. Section 19 now records the later issue #24 delivery separately. Claims labeled “current” in the original research describe its pinned baseline, not every later repository change.

# 1. Executive handoff

## 1.1 The objective

Develop Promise to Proof toward an adaptive delivery system that chooses an appropriate execution policy for a task, rather than always following one fixed, maximum-effort pipeline. The user explicitly wants tradeoffs across assurance, time, and money; human attention is a useful fourth outcome to expose. Assurance need not be maximized for every task.

The optimization target is the complete delivery episode: planning, implementation, checks, review, proof, repair, interruptions, recovery, and—when work is sliced—integration and parent verification. A cheap model call is not necessarily a cheap completed issue. Equally, a fast run that merely stops early or overlooks a defect is not automatically an improvement.

The proposed system should present a small number of understandable options, such as a lower-cost policy, a faster policy, and a more thorough policy, together with their evidence commitments, expected resource use, and uncertainty. It should not disguise an uncertain forecast as an assurance guarantee.

## 1.2 Decisions to carry forward

**D01 — Optimize outcomes, not token prices.** Evaluate total spend, elapsed time, useful completion, and human intervention over the same workload. Include failed and abandoned runs.

**D02 — Make assurance adjustable and explicit.** Separate task requirements from the depth of verification. A user may authorize a less thoroughly checked result without changing what the software is supposed to do.

**D03 — Preserve integrity in every mode.** Identity matching, truthful reporting, authorization, evidence provenance, and preservation of unrelated work are not optional savings opportunities.

**D04 — Treat model choice as a policy decision.** Choose models per stage and, potentially, per repair attempt. Measure whether economical models increase rework; do not assume price or a generic “strength” label predicts performance on a particular stage.

**D05 — Use dependency graphs, not artificial serial order.** Run genuinely ready children concurrently when allowed by resource and isolation constraints. Preserve final verification of the integrated parent candidate.

**D06 — Use FizzBee as an analysis and checking tool.** Start with protocol checking, then cost/latency experiments and implementation conformance. Do not assume FizzBee automatically designs the best workflow or measures real-world assurance.

**D07 — Introduce narrow deterministic enforcement.** Agent instructions alone are not an enforcement boundary. Prefer small host-facing gates and a minimal controller over a universal workflow platform.

**D08 — Measure before enabling adaptive behavior.** Build a baseline, evaluate candidate policies offline, run them in shadow mode, then enable an explicitly authorized subset.

These are the working design directions of this handoff. They do not authorize changing the repository protocol or issuing weaker results under existing acceptance labels.

## 1.3 Delivery order

Deliver the completion-rule model first, then enforce the rules in a running program and test that program against the model. Compare speed and cost only after that foundation works. User-selectable checking levels, parallel child tasks, and automatic strategy selection come later, in that order.

[Section 19](#19-delivery-phases-in-order) defines the deliverables and completion checks. Issue #24 delivered the selected completion-integrity model. It did not deliver the whole optimization roadmap or authorize weaker checks.

# 2. Verified repository baseline

## 2.1 Snapshot and existing ambition

The inspected `main` commit is `f5917ce0471d56aac01711e720426748626c99d0`, titled “Document formal verification ambitions.” The README now explicitly identifies a FizzBee lifecycle model and later model-based testing of a deterministic orchestration layer as goals. It also states that the workflow is not yet formally verified or fully automated. This handoff builds on that direction rather than claiming those capabilities already exist. [R01]

Issue #23 specifies issue-first delivery for one coherent existing issue. It remains open in the inspected tracker snapshot. Its scope excludes automatic large-issue splitting, automatic publication, and combining child proofs into parent acceptance. Its implementation-ready label does not approve another issue’s contract or this optimization proposal. [R02]

## 2.2 Current components and implications

| Component | Current responsibility | Implication for optimization |
|---|---|---|
| `/plan-acceptance` | Sole author of acceptance-contract revisions under the shared protocol. | An optimizer must not silently rewrite promises or exclusions. |
| `/implement-contract` | Implement the saved agreement and report development work. | Its self-checks are useful evidence inputs, not an independent acceptance verdict. |
| `/review-implementation` | Review the fixed candidate against the contract and comparison base. | Changing the candidate or comparison can invalidate reuse. |
| `/prove` | Issue requirement verdicts and overall acceptance results for an exact candidate. | Full `PROVEN` retains its existing meaning. |
| `/repair-gaps` | Repair named gaps under the existing agreement. | Repair does not itself establish acceptance. |
| `/deliver-issue` | Coordinate saved contracts, candidates, separate stages, report storage, and recovery. | It owns handoffs, not a new acceptance judgment. |
| `/slice-contract` | Decompose a parent, allocate coverage, establish real dependencies, and publish only with authority. | It exposes a graph that a later scheduler can consume; it is not already that scheduler. |
| Acceptance-bundle checker | Check a derived bundle’s structure, identities, coverage, and consistency. | Useful deterministic foundation, not proof of evidence authenticity or adequacy. |

Sources for these responsibilities: the shared protocol, delivery and slicing skills, and bundle specification. [R03, R04, R05, R06]

## 2.3 Current rules that an optimization must respect

The current successful `/deliver-issue` result requires full matching `REVIEWED` and `PROVEN` reports from the required independent read-only contexts. The reports must identify the current exact contract and one unchanged, recoverable candidate. They and their evidence must be retained and reread. A changed candidate requires fresh full review and proof; the skill allows at most one automatic repair/recheck cycle per invocation. [R04]

Current slicing rules call for the fewest useful outcome-oriented slices, not division by files, layers, or available agents. The dependency graph must remain acyclic and contain real prerequisites. A separately derived stable topological sequence supports a single engineer without turning that sequence into additional dependencies. Final parent proof concerns one integrated candidate; historical child verdicts do not compose into a parent verdict. [R05]

These details matter. Three successive model-escalation attempts, selective proof reuse after code changes, automatically running all child issues, or accepting a no-review result as normal completion are proposed protocol extensions—not existing features that can simply be switched on.

## 2.4 Existing validation is a starting point, not universal evidence

The repository’s September 25 delivery validation notes report a local D1 success on a supported host. They mark GitHub-specific D2 and D3–D10 as unexecuted complete cases, while documenting some observed subcases and earlier rejected successes. The scenario document itself is a human-runnable test specification, not an execution record. [R08, R09]

The new work should reuse those scenarios and their `save_report` fixture, but must keep simulated, model-checked, adapter-tested, and live-host results distinct. A missing host or tracker capability is not a passed integration test. [R02, R08, R10]

# 3. Objectives, controls, and constraints

## 3.1 Headline outcome dimensions

| Dimension | What to optimize or expose | What not to substitute for it |
|---|---|---|
| Assurance | Strength and coverage of evidence; independently evaluated residual-error behavior where measurable. | A model’s self-confidence, an unexplained percentage, or the word `PROVEN` alone. |
| Time | End-to-end elapsed time, including queues, human waiting, repairs, and integration; report median and tails. | Sum of model inference times or successful runs only. |
| Money | All attributable delivery spend, including unsuccessful attempts, tools, compute, storage, and cancellations. | Price per token or per model call. |
| Human attention | Active decision/review effort, interruption count, and avoidable context reconstruction. | Passive waiting time alone or a zero-interruption policy that silently makes product decisions. |

Useful completion rate and quality of the delivered result must accompany these axes. Otherwise, a policy that rejects every issue appears cheap, fast, and free of accepted defects. A sound blocker is valuable, but it must not be counted as a delivered feature.

## 3.2 Controls available to a policy

The proposed control space includes model and tool selection by stage; context selection; verification methods and depth; optional stages; review/proof ordering; permitted parallelism; bounded retries and escalation; safe reuse; decomposition; dependency scheduling; environment choice; speculative work; and human escalation thresholds.

Some controls operate only within the current protocol. Others require a new authorized profile or protocol revision. The controller must know the difference before dispatching work, not infer it from a final report.

## 3.3 Constraints and stakeholder preferences

Hard constraints can include repository standards, required approval, minimum verification for designated changes, data-exposure restrictions, tool permissions, maximum authorized spend, supported hosts, concurrency limits, and artifact-retention requirements. User preferences select among policies that satisfy those constraints; they do not silently override them.

Privacy and permitted model providers are usually better represented as eligibility constraints than as a score to trade against money. Likewise, a deadline may be a hard stop, a target with a tolerated overrun probability, or simply a preference. These meanings require different enforcement and must be recorded explicitly.

## 3.4 Optimization formulation

Let a policy specify the permitted actions and model/tool choices as work progresses. For a defined workload, compare each eligible policy’s distribution of cost, duration, attention, evidence coverage, and evaluated errors.

A practical first approach is constrained comparison: minimize expected spend subject to an approved evidence profile, a minimum useful-completion rate, and a chosen latency target. A second approach holds a spend/deadline envelope fixed and selects the strongest feasible evidence profile. Neither approach requires inventing a universal numeric assurance score.

Return a Pareto set when no option dominates: a policy is dominated only when another is no worse on every relevant outcome and strictly better on at least one, under the stated estimates. With uncertain estimates, report that apparent dominance may not be statistically established.

# 4. Adjustable assurance without misleading claims

## 4.1 Separate three different questions

**What was promised?** The acceptance contract describes the required behavior, boundaries, exclusions, and inherited constraints.

**What checking was requested and performed?** A versioned assurance policy describes the verification methods, coverage, independence, and resources to use.

**What can honestly be concluded?** The reports describe the actual evidence, gaps, uncertainty, and existing stage verdicts.

Reducing assurance changes the second question. It does not automatically narrow the first or justify a stronger answer to the third. A policy may finish its authorized work while the full acceptance contract remains unproven.

## 4.2 Integrity floor versus configurable depth

| Always preserve | Potentially adjustable after explicit policy design |
|---|---|
| Accurate candidate and contract identity. | Extra checks, test breadth, and evidence depth beyond binding requirements. |
| No fabricated actions, observations, or provenance. | Optional audits, redundant reviewers, or additional verification methods. |
| Scope-bound permission before effects. | Eligible models, reasoning settings, environments, and context strategies. |
| Honest gaps and uncertainty. | Whether a lower-assurance profile omits a normally required stage, with a distinct result meaning. |
| No stale evidence presented as fresh. | Scheduling, parallelism, allowed spending, and appropriately bounded repair. |
| Preservation of unrelated work and binding constraints. | User-selected tolerance for incomplete verification where the repository permits it. |

The right column is a proposed product design space, not blanket authority to weaken the current protocol. In particular, the current delivery skill still requires independent review and proof for its complete result. [R04]

## 4.3 Proposed profiles

**Current full-delivery profile.** Preserve the existing full matching reports, independent contexts, complete requirement evidence, identity checks, and repair bound. This is the compatibility baseline, not a claim of perfect assurance.

**Limited-check profile.** Potential future opt-in for exploratory or lower-consequence work. It could perform selected checks without full review or proof. Its result must clearly identify unchecked requirements and omitted stages. It must not emit an equivalent of full acceptance merely because its smaller checklist was exhausted.

**Extended-verification profile.** Potential opt-in that retains the baseline and adds chosen checks, such as targeted adversarial cases, integration environments, or a second independent method. Additional effort is not automatically additional assurance; evaluate its incremental defect detection and cost.

Avoid hard-coding “Fast” as both cheapest and fastest. A policy can reduce spend but increase duration, or buy shorter latency with more parallel work. Describe the actual tradeoff rather than promising all improvements simultaneously.

## 4.4 Result vocabulary and migration requirement

Keep the existing `REVIEWED`, `PROVEN`, `NOT PROVEN`, and `BLOCKED` meanings intact. Introduce any future lower-assurance workflow disposition separately, for example an explicitly proposed `POLICY_FINISHED_WITH_GAPS` disposition. Such a disposition would describe work performed under a policy, not invent an acceptance verdict. The name is illustrative and requires review.

A user-facing summary should state the selected policy and version, exact artifacts, completed and omitted checks, stage verdicts actually issued, residual unknowns, and the authorized boundary of further actions. Never infer publication or merge readiness from local policy completion. [R03, R04]

# 5. Policy selection and user control

## 5.1 Minimum policy contract

A proposed policy should identify its version, governing protocol, applicability, authorized assurance profile, mandatory and optional checks, stage/model assignments, allowed tool methods, resource limits, escalation rules, reuse rules, privacy constraints, and permitted terminal outcomes.

Policy approval and contract approval are related but distinct. A changed behavioral promise goes through contract revision; a consequential reduction in verification requires approval under policy governance. Store a link between them so a resumed run cannot accidentally apply a cheaper policy to an earlier full-assurance request.

The current protocol’s single canonical contract remains authoritative. Policy metadata and telemetry are derived execution material, not a second requirement checklist or competing acceptance store. [R03]

## 5.2 Reasonable selection process

First filter out ineligible policies: forbidden providers, missing host isolation, insufficient permissions, unmet repository verification floors, or unavailable evidence environments. Then estimate feasible alternatives using measurements for similar work. Present material assurance reductions or budget exceptions for approval unless already delegated within explicit bounds.

Begin with a small catalog of understandable policies. Do not start with an unconstrained agent that invents its own checking standard, model routing, and acceptance criteria during execution.

## 5.3 Runtime adaptation

Adaptation may choose among preauthorized alternatives—for example, switch the repair stage to a different eligible model while preserving the contract, required checks, and remaining repair budget. Unexpected product ambiguity, a required policy downgrade, or a resource-limit change returns a decision rather than automatic permission.

When estimates are unreliable, use the approved baseline or report an explicit uncertainty. Do not claim an assurance target has been achieved solely because a predictor assigned a high score.

# 6. Proposed architecture

## 6.1 Two planes, not one autonomous optimizer

Use an offline analysis plane to compare policies and a narrow runtime plane to enforce the chosen one. FizzBee belongs primarily in the analysis and validation plane; it need not sit in the latency-sensitive path of every issue.

| Layer | Responsibility | Trust boundary |
|---|---|---|
| Canonical source and contracts | Preserve approved behavioral obligations and amendments. | Agent summaries do not replace authoritative artifacts. |
| Policy catalog | Describe eligible workflows and their authorized assurance commitments. | Changes are versioned and reviewed. |
| Policy selector | Recommend or select an allowed policy from task features and estimates. | It cannot grant itself permission or redefine acceptance. |
| Minimal controller | Schedule stages, maintain budgets, validate identities, and manage recovery. | Critical transitions are deterministically checked. |
| Host adapters | Invoke actual isolated stages and mediate allowed effects. | Provenance and capability checks come from the host, not model prose. |
| Stage workers | Plan, implement, inspect, gather evidence, and propose repairs. | Outputs and action requests are untrusted inputs to the controller. |
| Artifact and event layer | Retain snapshots, reports, observations, identities, and execution records. | Derived execution state must remain reconcilable with canonical sources. |
| Analysis and evaluation | Run models, compare policies, audit real traces, and evaluate quality. | Predicted performance is not observed performance. |

## 6.2 Keep enforcement small

Start with executable gates around snapshot validation, report identity matching, permitted stage dispatch, retry accounting, and effect authorization. Reuse existing stage responsibilities and tracker conventions. Issue #23 explicitly excludes building a universal runtime or tracker SDK; broader scheduler work should be a separately scoped extension. [R02]

A post-run validator can detect a forbidden push, but cannot undo the fact that it happened. To claim prevention, mediate the action before execution and ensure the worker lacks an unchecked alternative tool route. The same principle applies to candidate mutation during read-only verification.

## 6.3 Trust and failure model

Model agent requests and reports as arbitrary, including stale, contradictory, incomplete, or fabricated claims. Trust only the specified host mechanisms for invocation identity, permission enforcement, and observed tool results. A digest protects a content association under its assumptions; it does not authenticate who produced the content or whether a test is meaningful.

For a first model, treat byte identities as abstract exact identities. Document the later mapping to digest-based implementation and its assumptions. Use immutable snapshots where possible; checking the same digest before and after a run alone does not rule out a change-and-restore event during that run.

# 7. What FizzBee contributes

## 7.1 Three complementary uses

**Protocol exploration.** Represent stages, artifact state, failures, and ordering choices; check invariants and obtain counterexamples. The official design tutorial demonstrates state-machine modeling and assertions. A successful run supports the stated model within its exploration configuration, not arbitrary executions of a Markdown skill. [F01]

**Conditional cost and latency analysis.** FizzBee documents probabilistic branches and performance counters, including cost and latency distributions. Use these to compare specified policies under explicit workload assumptions. Real defect rates, model capabilities, and inference costs still have to be supplied or measured. [F03, F04]

**Implementation conformance testing.** FizzBee’s model-based testing quick start demonstrates an adapter connecting a model to a Go implementation, including sequential and concurrent tests. The Promise to Proof adapter must still be built. The documented random concurrent testing is not a universal proof of all implementation executions. [F05]

## 7.2 What it does not supply automatically

FizzBee is not the source of truth for user intention, test adequacy, hidden defects, or model quality. It is not assumed here to provide an automatic multiobjective scheduler or a turnkey adapter for every agent host. A surrounding comparison script and, where needed, a separate simulator or scheduling component are proposed parts of the solution.

Do not infer real wall-clock parallel latency by merely adding per-action duration counters. First validate how concurrency and elapsed time are represented. A separate event-based evaluator is an acceptable companion when it is simpler or better matched to the required scheduling semantics.

## 7.3 Tool-selection checkpoint

FizzBee is the working first choice because the repository now names it and this handoff focuses on maintainable protocol models connected to tests. Retain a checkpoint after the first model: can maintainers run it reproducibly, understand counterexamples, and represent required concurrency and performance behavior without unreasonable complexity?

Pin the tested tool version or commit. Its documentation notes Python-like language restrictions and interleaving subtleties; do not treat a `.fizz` file as ordinary Python. [F06] Reassess the tool choice if the required assurance or analysis exceeds what the demonstrated integration supports.

# 8. Formal model scope and state

## 8.1 Start with the existing single-issue protocol

The first model should reproduce current full delivery, not mix new profiles, a large child graph, learned probabilities, and a production scheduler into one state space. Add those dimensions in separately reviewable increments.

Represent the environment nondeterministically for safety checking: storage can fail, source text can change, reports can arrive late, and host capabilities can disappear. A low probability must not remove a relevant unsafe transition from the safety model. Attach calibrated probabilities only in the performance view.

## 8.2 Suggested state inventory

| State group | Suggested representation | Why it matters |
|---|---|---|
| Source and agreement | Stable source key, exact contract identity, revision label, material-amendment state. | Text changes can matter even when a revision label does not change. |
| Approval and policy | Approval-required flag, exact approved identity, policy/version, permitted effects. | Prevent self-approval and policy substitution. |
| Candidate | Content identity, comparison base, recoverability, fixed/live state, owned scope. | A hash or branch name alone is not a transferable candidate. |
| Stage invocation | Stage, invocation ID, role, read-only capability, bound inputs, execution state. | A report is not proof that its stage ran. |
| Reports and evidence | Bound identities, status, scope, evidence references, provenance, saved/readback state. | Prevent stale or incomplete completion. |
| Recovery | Durable records, volatile session state, pending writes, uncertain outcomes. | A restart must not invent completed effects. |
| Limits | Invocation repair count, study-wide episode ID, pending work, budgets. | Prevent loops, restart budget laundering, and oversubscription. |
| Terminal result | Current stage results, blocker reason, claimed assurance, partial effects. | Stop conditions must remain truthful. |

For a later multi-issue model, add child contract/parent identities, direct prerequisite outcomes, satisfied-artifact identities, ready/running sets, worker slots, conflict resources, integration identity, and parent verification state.

## 8.3 Actions to represent explicitly

Include resolving the issue; checking host/storage capabilities; planning; obtaining required approval; saving and rereading the contract; implementing; capturing and reconstructing a candidate; launching and completing each verifier; storing and rereading reports; checking eligibility for the final result; routing one repair; recapturing; restarting; reconciling uncertain writes; and returning a specific blocker.

Add separate environment actions for source amendments, candidate drift, loss of access, interrupted persistence, delayed stage completion, conflicting work, and budget exhaustion. The model should not assume those actions occur only between convenient phases.

A proposed action vocabulary can be descriptive without prescribing implementation call order. The repository scenarios judge externally observable outcomes rather than prompt wording or incidental internal sequencing. [R08]

## 8.4 Pseudocode for the claim boundary

The following is a specification sketch, not executable FizzBee syntax:

```text
may_report_current_full_delivery(state):
    approval is satisfied whenever required
    saved contract identity equals the current resolved identity
    fixed candidate is reconstructible and unchanged
    review is a full REVIEWED report for that contract/candidate/base
    proof is a full PROVEN report for that contract/candidate
    required independent invocations have host-established provenance
    required reports and evidence are saved, reread, and retrievable
    no unresolved discrepancy invalidates these claims
```

This predicate is not the whole verification exercise. The difficult obligation is showing that actual state transitions cannot reach a stronger claim using missing, stale, or untrusted facts. Avoid defining success as “all rules hold” and then treating that definition as proof that the implementation enforces the rules.

# 9. Properties and traceability

## 9.1 Integrity and compatibility properties

The identifiers below are proposed model/test identifiers, not new contract requirement IDs. Properties derived from the current protocol should trace to its authoritative text; new policy and scheduler properties need their own approved scope. [R02–R05, R08]

| ID | Property to check | Example counterexample to reject |
|---|---|---|
| I01 | Required approval binds to the exact contract before dependent implementation. | Approve text A, edit to B, then implement B using the old approval. |
| I02 | A current full-delivery claim binds review and proof to one exact contract and candidate. | Combine review of candidate A with proof of candidate B. |
| I03 | Review also binds to the required comparison base and declared scope. | Reuse a review after changing the base that defines the diff. |
| I04 | Changed candidates cannot inherit current full review/proof validity. | Repair only tests, then reuse the old candidate’s green reports. |
| I05 | Contract text drift is checked independently of its revision label. | Change an outcome but leave the label at v1. |
| I06 | Claimed independent stages have actual, distinct, appropriate host invocations. | The enclosing agent writes both reports itself. |
| I07 | Verification cannot modify the candidate under a read-only claim. | A proof worker fixes code before recording a passing result. |
| I08 | Completed handoffs require saved, reread, retrievable content. | A chat summary or an inaccessible path is treated as durable storage. |
| I09 | A claimed recoverable candidate can be reconstructed in the required context. | A changed-files-only archive lacks the base tree needed to restore it. |
| I10 | Full proof retains complete material requirement coverage and evidence references. | One unverified requirement is silently omitted from the summary. |
| I11 | Effects occur only within exact prior authority. | An issue body instructs the agent to push or change labels. |
| I12 | Uncertain effect outcomes are reconciled before repetition. | A lost response causes duplicate tracker writes without readback. |
| I13 | Existing unrelated work is preserved and excluded from the delivered change. | A snapshot absorbs another developer’s dirty configuration edit. |
| I14 | Automatic repair stays within the current per-invocation bound. | Restart or recursive dispatch silently resets the repair counter. |
| I15 | Historical reports remain historical rather than being rewritten as fresh observations. | Storage readback edits the verifier’s original account of its run. |
| I16 | A new assurance profile cannot silently relabel a partial check as full acceptance. | A limited-check run emits the normal full-delivery completion. |
| I17 | Budget admission counts in-flight reservations as well as settled spend. | Two workers each spend the same remaining budget concurrently. |
| I18 | Parent completion uses current integrated evidence, not an aggregation of child verdicts. | All child issues are closed, so the parent is marked proven. |

I16–I17 explicitly concern proposed policy/controller extensions. I18 is already a parent-proof rule but enters the formal model only when multi-issue scheduling is added. The model must distinguish a report’s claim that something happened from trusted evidence that it happened.

## 9.2 Existing scenario mapping

| Existing scenario | Primary model coverage | Additional implementation evidence needed |
|---|---|---|
| D1: one issue reference | Valid full-delivery path and truthful final artifacts. | Actual stage invocations and independent public-seam observations. |
| D2: configured source | Source identity and tracker configuration. | Live tracker adapter resolution, including separate source/code repositories. |
| D3: outcomes and approval | I01, I05; amendment and decision paths. | Human approval association and source readback. |
| D4: canonical storage | I08, I12; uncertain writes and conflicting pointers. | Actual persistence and readback behavior. |
| D5: existing/concurrent work | I13 and drift handling. | Byte/mode comparisons and isolated workspace behavior. |
| D6: candidate recovery | I08, I09; restart and missing artifacts. | Restoration into a separate checkout. |
| D7: stale observations | I02–I05; incorrect/truncated digests. | Recomputed full identities from retained bytes. |
| D8: review defect | Correct implementation repair route and rechecks. | A real supported finding with unchanged contract. |
| D9: proof gap and repair bound | I04, I14; named gaps and repeated failure. | Actual repair and both full fresh verifications. |
| D10: independence/authority | I06, I07, I11; host/storage failure. | Host-enforced restrictions and adversarial issue text. |

This map supplements the repository scenarios; it does not replace their externally observed pass/fail criteria. [R08]

## 9.3 Deliberate invalid variants

Maintain small model mutations that must fail: remove the candidate match; accept a revision label without text identity; trust a model-supplied session ID; permit completion before report readback; let resume clear the repair count; allow a policy switch to reduce required evidence silently; omit an in-flight budget reservation; and mark the parent complete from child status alone.

A useful checker should produce a concrete witness for each mutation. Record the mutation, violated property, and replayable trace. This tests whether the specification actually detects the error rather than merely passing a model that cannot exercise it.

# 10. Progress, failure semantics, and model limits

## 10.1 Meaningful progress obligations

Check that valid full delivery is reachable under appropriate inputs. Check that unavailable approval, permissions, evidence, or host isolation produces a specific blocker rather than false completion. A system that always blocks must not satisfy the complete set of evaluation goals.

For termination, state the environment assumptions: enabled controller actions eventually run; external operations either return or time out; and the host can persist or accurately report inability to persist. Under those assumptions, an invocation should finish or return an honest blocker. Do not assume an agent eventually produces correct code merely to make liveness pass.

FizzBee distinguishes safety from liveness and documents fairness settings. These settings must match the intended scheduler and failure model; they are assumptions, not observed provider reliability. [F02]

## 10.2 Bounded repairs are not unrestricted eventual success

The current delivery skill allows one automatic repair/recheck cycle per invocation. Treat an initial attempt plus that cycle as the first model’s limit. A new user-authorized invocation may legitimately begin another episode, but restarting the same work must not silently create unlimited automatic retries. Track both invocation identity and a broader analysis episode to account for cumulative spend and attention. [R04]

A time limit requires more than a retry count: one model call, test, or human decision can remain outstanding. Define stage deadlines, cancellation behavior, and whether elapsed human waiting counts toward the selected target. Cancellation must be reported as requested, confirmed, failed, or uncertain; it must not be assumed to eliminate already-incurred cost.

## 10.3 Suggested initial abstraction

Start with one issue, two contract identities, three candidate identities, two verifier roles, a single permitted repair, small report histories, and a few discrete storage outcomes. These are suggested modeling bounds, not sufficient evidence by themselves. Increase bounds and compare discovered behaviors before treating the abstraction as stable.

Model durable and volatile state separately. Restart should discard volatile assumptions and reconstruct from readable artifacts. Do not model every write as one atomic step when the real implementation can be interrupted between issuing it, receiving confirmation, and retaining its identity.

Record the model version, policy, constants, exploration limits, fairness settings, runtime, state count, and whether exploration exhausted the intended state space or stopped early. A timeout or depth cutoff is incomplete coverage, not an unconditional pass.

# 11. Monetary and time economics

## 11.1 Optimize the full episode

Define an episode as one agreed analysis unit, such as an issue delivery including its initial attempt, permitted repair, and terminal outcome. Include model calls, verification tools, dependency/environment setup, queues, snapshot transfer, artifact storage, abandoned work, and human intervention. For a parent, include all contributing children and final integration.

Track both spend per submitted issue and aggregate spend per independently satisfactory completion. The latter allocates the cost of failures across the successful outcomes in the cohort. Neither metric should hide completion rate or severity of escaped defects.

## 11.2 A bounded retry model

For an initial complete attempt costing `C0`, with probability `q0` of entering one allowed repair/recheck cycle costing `C1`:

```text
Expected episode spend = C0 + q0 * C1
```

This expression assumes those are the only chargeable paths and that `C1` is the conditional mean cost when repair occurs. Add other branches for blockers, timeouts, host failures, or setup costs. It does not assume each model call has the same cost.

For a simplified sequential case with corresponding elapsed times, the same structure gives `T0 + q0 * T1`. Parallel stages require their actual overlap and queueing behavior, not the sum of durations.

If initial and repaired success probabilities are `p0` and `p1`, then `p0 + (1 - p0) * p1` is a useful two-attempt illustration only when every initial failure proceeds to repair and success/failure is correctly recognized. Real evaluation must separately represent bad candidates that checks miss, valid candidates that checks reject, and failures that are not repairable.

## 11.3 Synthetic example: cheapest call versus cheapest outcome

The following inputs are invented to illustrate accounting. Each attempt includes its associated verification, and the example assumes perfect recognition of correct versus incorrect output. It is not a forecast for any provider or Promise to Proof run.

| Synthetic policy | Initial cost / time / success | Conditional repair cost / time / success |
|---|---|---|
| Economy then economy | $0.10 / 2 min / 50% | $0.12 / 2 min / 60% |
| Stronger then stronger | $0.16 / 2.5 min / 90% | $0.18 / 2.5 min / 80% |
| Economy then stronger | $0.10 / 2 min / 50% | $0.18 / 2.5 min / 80% |

| Synthetic policy | Expected spend | Expected time | Completion probability | Cohort spend per success |
|---|---|---|---|---|
| Economy then economy | $0.160 | 3.00 min | 80% | $0.200 |
| Stronger then stronger | $0.178 | 2.75 min | 98% | $0.182 |
| Economy then stronger | $0.190 | 3.25 min | 90% | $0.211 |

Here, the stronger policy costs more per submitted issue than economy-only, but less per successful completion, and has lower expected duration. Escalation is not automatically best either. Different measured inputs can reverse these rankings.

Do not use an unlimited geometric retry formula as the production model for a workflow with bounded repair, correlated errors, different repair models, or persistent blockers.

## 11.4 Time, money, and attention require separate ledgers

Parallel work reduces elapsed time when it shortens the critical path. It does not necessarily increase total spend: if the same calls execute once at the same prices, their summed call cost can be unchanged. Additional cost arises from duplicated or speculative work, lost cancellation opportunities, retries, contention, or changed pricing.

Similarly, human waiting and active human effort are different. A workflow can spend more on computation to avoid a difficult interruption, but saving a minute of passive waiting is not the same benefit as saving a minute of careful review. Report both rather than assigning a hidden monetary conversion.

# 12. Model and tool selection by stage

## 12.1 Treat capability as measured and task-dependent

The user’s hypothesis is important: an economical model may produce more incorrect work, triggering extra review, proof, and repairs. That can make it slower and more expensive overall. It is a hypothesis to test by stage and task class, not a universal rule that cheaper models are always weaker or slower.

Record model identifier/version, relevant configuration, tool access, context policy, and prompt/skill revision. A model comparison is not interpretable when those factors change unnoticed. Avoid provider rankings or current price assumptions in the policy specification; load permitted models and price snapshots from versioned configuration.

## 12.2 Candidate routing strategies

Compare a fixed baseline assignment, economical models throughout, stronger implementation with unchanged verifiers, economical planning with stronger implementation, and one permitted escalation on repair. Also compare model calls with suitable deterministic tools where the tool directly checks the required property.

Treat planner, implementer, reviewer, and proof worker quality separately. A planner that omits a promise can cause every downstream stage to agree on the wrong task. A cheap verifier may report fewer defects because it misses them, not because the implementation improved.

## 12.3 Error correlation and diversity

Maintain the distinction between separate execution contexts and statistically independent errors. Distinct host sessions are observable. Independence of reasoning mistakes is an empirical question.

Evaluate combinations of implementer and verifier models, prompts, tools, and oracles. Different providers or model families may or may not provide useful diversity. Shared training, shared context, copied expected outputs, or a common faulty contract can create common-mode failures even when session IDs differ. Avoid multiplying independent failure probabilities without evidence for that assumption.

## 12.4 Bounded escalation and stopping

Keep escalation within the currently allowed repair cycle unless a separately approved policy changes that bound. Before escalating, classify the cause: implementation defect, inadequate evidence, contract ambiguity, unavailable infrastructure, or missing authority. Spending on a larger model cannot by itself resolve a missing permission or absent external test system.

A useful stop rule considers remaining budget, expected benefit, mandatory checks still outstanding, and whether the next action can change the decision. It must not lower the evidence standard retrospectively to make the current work look successful.

# 13. Verification ordering and parallelism

## 13.1 Policies to compare

Compare review then proof, proof then review, and concurrent review/proof on an immutable candidate. Independently compare a cheap deterministic preflight before those stages. Preserve the same required final reports for the current full-delivery profile. The protocol permits review and proof in either order; actual concurrent execution still requires compatible host isolation and resource handling. [R03, R04]

A sequential order saves call cost only if it avoids or changes work on some branch. If both verifiers always run, reordering them alone does not reduce their summed model spend. Early rejection or short-circuit behavior must be checked against the existing dispatch/repair contract before implementation.

## 13.2 First-pass check-ordering heuristic

For two checks with fixed costs and a rule that stops after the first decisive blocker, a simple ordering favors the larger ratio of blocker probability to cost. This follows by comparing `cA + (1 - qA)cB` with `cB + (1 - qB)cA` under the simplified assumptions.

Use this as a starting heuristic, not a global optimizer. Checks can be correlated, expose complementary findings, alter repair cost, or have different queue delays. A first failure may not be enough information for an efficient repair. A policy that gathers both findings before one repair can outperform repeated narrow fixes.

## 13.3 Parallel elapsed time

For fixed, immediately available workers, two independent verification durations contribute approximately `max(review_time, proof_time)` to wall-clock time, while their direct compute costs add. For variable durations, `E[max(R, P)]` is generally not `max(E[R], E[P])`. Tail latency must be calculated from a justified joint model or measured executions.

Account for worker startup, rate-limit queues, tool contention, environment provisioning, and final artifact readback. Keep candidate and contract immutable across both verifiers. A verifier may write evidence to an authorized external location without gaining permission to change the candidate.

## 13.4 Cancellation is a policy, not a free optimization

When one verifier finds a decisive blocker, define whether the other continues to collect repair information, receives a cancellation request, or finishes because cancellation is ineffective. Record the actual outcome and billable work. A canceled or incomplete verifier cannot be treated as a completed passing stage.

# 14. Slicing and dependency-graph scheduling

## 14.1 Preserve the actual graph

The current slicing skill already separates real dependencies from a linear implementation sequence. A future scheduler should consume the direct-prerequisite graph rather than serializing children just because they appear one after another in a plan. [R05]

A simple graph is:

```text
          +--> B --+
A --------+--> C --+--> E
          +--> D --+
```

Here B, C, and D all require A, and E requires all three. There is no dependency among B, C, and D merely because the document lists them in that order.

## 14.2 Readiness has several conditions

A child is not ready solely because its graph predecessors are marked done. Check that prerequisite outcomes/artifacts are available at the required identities, the child contract and any approval exist, parent constraints are current, necessary host capabilities are available, and resource/budget admission succeeds. Closed tickets are not proof of prerequisites. [R03, R05]

Separate semantic dependencies from conflict and resource constraints. Two children may have no behavioral dependency yet both need an exclusive test database or modify a shared generated file. These constraints can restrict concurrent execution without falsely rewriting the contract’s dependency graph.

## 14.3 Optimize the critical path

Synthetic example: let A take 1 minute, B 2, C 5, D 3, and E 1.5. Assume each child duration includes its required work and E includes the stipulated integration/final checking. Ignore resource contention for this illustration.

Serial execution takes 12.5 minutes. Running B, C, and D in parallel after A takes `1 + max(2, 5, 3) + 1.5 = 7.5` minutes. Reducing B from 2 minutes to 1 does not improve this schedule while C still takes 5. Reducing C to 3 minutes reduces the total to 5.5 minutes.

This motivates spending stronger-model or additional-tool effort where it reduces the uncertain critical path, rather than making every child individually faster at any price.

## 14.4 Decomposition quality is also a control

Compare alternative valid decompositions for coordination overhead, critical path, interface uncertainty, likely rework, and integration burden. More slices are not automatically better. Every additional child can add contract work, context setup, verification, artifacts, and integration effort.

Preserve the skill’s preference for coherent observable outcomes and the fewest useful tickets. Do not create artificial slices around available agents, split tests away from their behavior, or remove a real prerequisite to manufacture parallelism. Consequential allocation and dependency changes may need renewed approval. [R05]

## 14.5 Isolated implementation and controlled integration

Use separate authorized workspaces for concurrently running implementations. Do not run multiple writers against one live worktree and rely on agents to avoid conflicts. Capture each child’s exact inputs, outputs, parent mapping, and verification context.

Integrate through a controlled step that detects conflicts, preserves unrelated work, and creates a new exact candidate. Merge conflict resolution, rebasing, shared configuration changes, and interaction fixes can change the candidate. Child green reports remain historical evidence for those child candidates; they are not the final parent verdict. [R03, R05]

A child-scheduling extension must also preserve the current publication boundaries. Separate branches, child PRs, integration branches, and tracker publication each require their applicable authority. The slicing skill does not itself authorize creating branches or publishing stacked PRs. [R05]

## 14.6 Speculation as a later experiment

A policy might start work that is independent of an unresolved prerequisite, or prepare a downstream child against a pinned provisional interface. This is speculative work, not confirmation that the prerequisite is satisfied.

Record assumptions and the exact upstream artifact. If the assumption changes, invalidate affected work, cancel or rework it, and account for the loss. Speculation must not bypass required contract approval, permit unauthorized effects, or let a parent complete before current integrated verification. Begin with non-speculative scheduling; add speculation only after useful baseline data exists.

# 15. Optimization opportunities to investigate

All entries below are hypotheses and experiment candidates. The table does not claim measured savings. “Current-compatible” means potentially compatible when implemented without weakening existing obligations; it is not a completed implementation review.

| Opportunity | Experiment and expected mechanism | Main guardrail |
|---|---|---|
| Contract quality | Compare additional source reconciliation or an optional audit with downstream rework. | Do not use implementation agreement as proof the original promise was captured. |
| Context efficiency | Compare full context with traceable, stage-specific retrieval bundles. | Preserve every binding requirement, exclusion, amendment, and needed interface. |
| Deterministic preflight | Catch invalid storage, identities, capabilities, and snapshots before costly stages. | Keep real host-isolation checks; a command’s presence is not capability proof. |
| Tool substitution | Compare a suitable type/test/static/property check with another model call. | The tool must establish the relevant property through an adequate oracle. |
| Verification ordering | Compare serial orders, concurrency, and authorized short-circuit variants. | Keep required completion evidence and account for complementary findings. |
| Same-candidate resume | Reuse valid saved work when identities, policy, environment, and provenance still permit it. | Reread artifacts; do not reconstruct state from chat memory. |
| Setup and content caching | Reuse pinned dependencies, immutable context fragments, and prepared environments. | Cache keys must include relevant inputs; a cache hit is not acceptance evidence. |
| Incremental evidence | Investigate dependency-backed reuse of unaffected evidence after a change. | This changes current full-recheck semantics and needs a separate soundness argument. |
| Model routing | Compare stage-specific assignments, not one global cheapest model. | Evaluate detection quality and correlated errors, not pass rates alone. |
| Repair diagnosis | Route product ambiguity, evidence gaps, infrastructure, and code defects differently. | Never turn an unresolved decision into a guessed requirement. |
| Human-question batching | Gather related blocking decisions into one clear request. | Do not delay a truly blocking question or obscure individual approvals. |
| Environment selection | Compare suitably representative local, isolated, and integration checks. | Explicitly state what the environment does and does not exercise. |
| DAG scheduling | Compare fixed order, ready-set scheduling, and critical-path priorities. | Respect actual prerequisites, worker limits, isolated writes, and parent proof. |
| Adaptive stopping | Avoid optional work unlikely to change a decision. | Required evidence remains required; uncertainty must remain visible. |
| Retention and transfer | Measure report/snapshot transfer and storage overhead. | Retain the artifacts needed to substantiate claims and resume correctly. |
| Run-history learning | Improve estimates using observed stage outcomes and costs. | Use controlled evaluation, data minimization, and versioned predictors. |

## 15.1 Safe reuse versus incremental verification

These are different projects. Reusing a report for the same unchanged candidate, contract, appropriate base, valid context, and retrievable evidence is a recovery optimization. Reusing evidence after the candidate changes requires reasoning about what the change cannot affect.

For incremental verification, define dependencies of requirements on code, tests, configuration, runtime inputs, external services, and inherited constraints. A path-only diff or unchanged public function signature is not sufficient to establish non-interference. Until an approved protocol and adequate dependency argument exist, retain fresh full review and proof for changed candidates. [R03, R04]

## 15.2 Minimize total verification overhead

A sophisticated optimizer can cost more than it saves. Measure context classification, policy selection, forecasting, model checking, telemetry, and report-generation overhead. Keep model checking primarily in development/CI and policy analysis, not as an expensive new agent phase on every trivial issue.

Treat a simple fixed policy as a serious baseline. The adaptive system must outperform it on useful outcomes after its own costs are included.

# 16. Measuring assurance and useful outcomes

## 16.1 Start with an evidence profile, not a confidence percentage

Represent assurance through observable dimensions: source-to-contract reconciliation, requirement coverage, public-seam observations, verification methods, independence of execution, environmental realism, adversarial boundaries exercised, and unresolved gaps. State what was checked and the limitations of those checks.

A later numerical estimate should identify its meaning, population, measurement method, and uncertainty. For example, an observed defect-escape rate on a held-out class of tasks is different from a probability that one particular patch is correct. Do not translate a profile called “extended” into a claim such as “93% assured” without a validated interpretation.

## 16.2 Establish outcome labels independently

Use independently specified requirements and expected behavior, withheld evaluation cases, seeded defects, and expert adjudication where appropriate. Include cases that expose an omitted contract promise, a bad oracle, misleading green tests, irrelevant checks, and a verifier that merely agrees with implementation prose.

For each requirement or task, keep the evaluation outcome distinct from the workflow’s report: independently satisfactory, independently defective, or unresolved. Unknown ground truth must remain unknown. A `PROVEN` report is an object to evaluate, not its own correctness label.

## 16.3 Required measures

| Measure | Definition or reporting rule |
|---|---|
| Useful completion rate | Independently satisfactory completed tasks divided by assigned tasks, with eligibility rules fixed in advance. |
| Accepted defect rate | Independently defective accepted results divided by adjudicated accepted results; disclose how many remain unevaluated. |
| Defect-detection rate | Known defective cases detected by the policy, broken down by defect type and severity. |
| Unnecessary rejection | Independently satisfactory cases blocked or rejected for reasons the selected policy did not require. |
| Evidence coverage | Obligations with the selected evidence path actually exercised, alongside omitted obligations and method limitations. |
| Cost and duration | Per submitted episode and per useful completion; report distribution, failures, and unfinished observations. |
| Human effort | Active review/decision time, interruption count, and unresolved decisions. |
| Rework | Repairs, repeated verifications, invalidated downstream work, and discarded speculative effort. |
| Operational integrity | Unauthorized effects, false provenance, stale acceptance attempts, and failed recovery checks. |

Choose observation windows and task populations before comparing policies. Report severity separately; ten superficial findings are not automatically more valuable than one serious escaped defect.

## 16.4 Avoid biased comparisons

Keep a held-out evaluation set. Compare policies on matched or randomized task groups where practical. Record task difficulty features, repository/tool changes, model versions, and environment differences. Otherwise a policy receiving easier tasks can look better for reasons unrelated to its design.

Do not tune on every observed run and report the same runs as independent validation. Include confidence intervals or sensitivity ranges when data supports them, and explicitly label sparse categories. Rare severe failures cannot be declared impossible merely because none appeared in a small sample.

Treat economical-model retry behavior, reviewer diversity, extra audits, and context compression as separate hypotheses. An increase in `BLOCKED` may reflect improved defect detection, worse tool reliability, or unnecessary caution; diagnose it before optimizing it away.

# 17. Telemetry, budgets, and privacy

## 17.1 Event record requirements

Use a versioned event schema with a stable episode ID, invocation ID, parent/child association, stage, attempt, policy version, exact contract/candidate identities, comparison base where relevant, and environment/context identities. Record model/tool/configuration revisions and host-issued provenance separately from worker prose.

Capture requested, started, completed, canceled, and uncertain operation states. Store monotonic duration measurements where available, wall-clock timestamps for audit, and causal links for concurrent operations. Include queue time, execution time, and human waiting separately.

Cost fields should distinguish estimates, reservations, accrued usage, settled charges, pricing configuration, and unknown amounts. Token categories should preserve whatever the provider actually bills rather than collapsing cached input, output, or other chargeable categories into an invented universal rate.

## 17.2 Budget accounting

Before launching a stage, reserve an authorized allowance against the episode and parent budgets. The remaining admission budget is the cap minus settled/accrued spend and outstanding reservations, without counting the same cost twice. Reconcile reservations when usage becomes known.

A hard monetary cap is credible only when the call/tool interfaces can enforce or conservatively bound spending, including in-flight and delayed charges. Otherwise describe the limit as a forecast-based admission policy with possible overruns. Do not promise an exact dollar ceiling that the infrastructure cannot enforce.

Likewise, treat a deadline as elapsed-time policy, not a promise that canceled provider work ceases instantly. Define graceful termination, retained partial artifacts, and escalation for uncertain charges or effects.

## 17.3 Privacy and retention

Default to local or explicitly approved telemetry storage. Record stable digests and structured observations rather than copying full private code, issue bodies, prompts, or secrets into analytics. Content-bearing evidence may still be required for acceptance; retain it in the authorized artifact store with appropriate access controls.

Aggregation or removal of obvious names does not automatically make repository data anonymous. Establish retention, deletion, access, and provider-exposure policies. A learned routing service must not send private task content to an unapproved model simply because that route is cheaper.

## 17.4 Retain enough to reproduce decisions

Retain the policy version, feature inputs used for selection, available eligible alternatives, forecast snapshot, selected action, reason, random seed where relevant, and observed results. A future maintainer should be able to explain why a model or schedule was chosen without assuming the predictor has stayed unchanged.

Derived execution indexes may be rebuilt from retained artifacts, but they must not become an alternative authority for requirement content or acceptance. This preserves the repository’s canonical-contract design. [R03]

# 18. Experiment portfolio

The following experiments are proposed work packages. Each needs an approved scope, fixed baseline, independent outcome assessment, and resource envelope before execution. No savings percentage is promised in advance.

| ID | Question | Compare | Primary evidence |
|---|---|---|---|
| E01 | Does mechanical preflight avoid expensive doomed runs? | Existing baseline versus deterministic preflight. | Spend avoided, added overhead, false blockers, retained integrity. |
| E02 | Which verification order fits this workload? | Review-first, proof-first, concurrent; approved early-stop variants separately. | Total spend, elapsed distribution, complementary findings, repair success. |
| E03 | Which stage deserves a more capable model? | Controlled per-stage routing changes. | Useful completions, escaped defects, repairs, total episode cost. |
| E04 | Does one-step escalation beat starting stronger? | Fixed assignment versus one allowed escalation. | Conditional repair results, duration tails, failed-run spend. |
| E05 | Can smaller context preserve evidence quality? | Full context versus traceable retrieval bundles. | Omitted constraints, defect detection, tokens, latency, rework. |
| E06 | Is additional planning/audit effort worthwhile? | Baseline contract preparation versus targeted extra reconciliation. | Source omissions and downstream repair/attention cost. |
| E07 | How much valid work can resume retain? | Full restart versus same-candidate validated resume. | Reused work, restoration success, stale-report rejection, saved cost/time. |
| E08 | Which child scheduling policy shortens parent delivery? | Stable serial sequence versus ready-set and critical-path scheduling. | Parent completion time, integration failures, peak usage, total spend. |
| E09 | Does another verification method add useful detection? | Extra model review versus a suitable independent tool/evidence path. | New defect classes found and incremental cost per useful finding. |
| E10 | What is the cost/quality tradeoff of a limited-check profile? | Approved profile variants on eligible held-out tasks. | Explicit gaps, independent errors, useful completion, saved effort. |
| E11 | Can speculative work pay for its waste? | Non-speculative baseline versus bounded, assumption-tracked speculation. | Critical-path reduction, discarded work, propagation of stale inputs. |
| E12 | Can selected evidence survive candidate changes soundly? | Fresh full verification versus an approved dependency-backed experimental method. | Counterexamples, non-interference evidence, independent quality and cost. |

Run E01–E07 before assuming an adaptive multi-issue scheduler is necessary. E10 requires new result semantics; E11 and E12 are later research, not shortcuts to enable during the baseline phase.

## 18.1 Evaluation protocol

Predefine the task set, eligibility, budget, baseline, primary metrics, and stopping rules. Retain every assigned task, including blockers and interruptions. Mark unexecuted configurations honestly. Use the existing fixture for repeatable behavior and add held-out tasks that exercise different requirements and failure modes. [R08, R10]

For every policy comparison, produce an assumptions table, observed or synthetic parameter provenance, counterexample/check results, cost/time distributions, assurance evidence, and the reasons alternatives were rejected. A favorable mean is not enough when tail latency or severe errors worsen materially.

## 18.2 Sensitivity before real deployment

Vary repair probability, detection quality, startup time, queue delay, cost uncertainty, and environment failure rates. Identify the parameter ranges in which the preferred policy changes. A policy that wins only under a narrowly chosen success rate should not be sold as generally optimal.

The safety view must still explore relevant failures regardless of their estimated rarity. The performance view can weight them, but a low-probability integrity violation is not made acceptable by a good expected-cost result.

# 19. Delivery phases in order

Implement these phases in order. Finish the required checks and integrate the result before starting the next dependent phase. A phase may need several small work items. Give each work item a saved acceptance contract in `work/` that says what must be true when it is finished.

This roadmap sets the order. It does not approve future product decisions, spending, publication, or weaker verification. Resolve the decisions listed for each phase before work depends on them.

## The route at a glance

| Phase | What we deliver | What it gives us | Position as of September 26, 2026 |
|---|---|---|---|
| 0 | A recorded starting point | Everyone uses the same rules and definitions | Baseline recorded for issue #24; confirm host capabilities and remaining definitions before Phase 2 |
| 1 | An executable model of completion rules | We can find cases where the rules could wrongly allow “done” | Complete for issue #24; PRs #25–#27 merged September 26, 2026 |
| 2 | A small program that enforces the rules | A real delivery cannot bypass the required checks | Next development phase |
| 3 | Tests that compare the program with the model | We can catch differences between the design and the running program | After Phase 2 |
| 4 | A repeatable comparison of delivery strategies | We can see which choices save time or money and at what cost | After Phase 3 |
| 5 | Clearly described levels of checking | Users can make an informed, authorized choice | After Phase 4 |
| 6 | Safe execution of several related tasks | Independent tasks can run together without losing the final combined check | After Phase 5 |
| 7 | A limited trial of automatic strategy selection | We can test improvements on real work and turn them off safely | After Phase 6 |

## Phase 0: Agree on the starting point

Record which repository version and delivery rules we are using. Define the few terms needed to judge results: one delivery attempt, a restart of that attempt, a repair, a completed task, and a blocked task.

Deliver a short record linking the rules, existing checks, supported environment, and known gaps. Separate requirements that already apply from proposed changes that need approval.

Done when two people can use that record to agree whether an example task is complete, blocked, or still in progress. Unknown host capabilities must be listed rather than assumed.

For issue #24, the recorded baseline is `41bebc726a8cc71c1d2f22d822ade006f4e78121`. Before Phase 2, confirm the host's capabilities and the remaining definitions needed for real execution. Definitions for optional checking levels can wait until Phase 5.

## Phase 1: Check whether the completion rules hold

Build a small executable model of one delivery. FizzBee, the tool that explores possible sequences of events, checks the model's rules.

Deliver:

- A model of implementation, separate review and proof, saved reports, one repair, and restart.
- Checks that reports refer to the same current code and requirements, with the correct comparison base.
- Checks that missing evidence prevents completion and restarting does not reset the repair allowance.
- Examples of successful delivery and specific blockers, plus deliberately broken rules that produce visible failures.
- One repeatable command, a fixed tool version, and a plain statement of what the model does not cover.

Done when valid examples can finish, invalid examples are rejected for the expected reason, and another person can reproduce the results.

Issue #24 is complete. PR #25 merged the model with 43 passing checks, including 14 deliberately broken variants, and separate review and proof for all ten requirements. PRs #26 and #27 completed the publication handoff and safety scenarios. [The delivered README](https://github.com/grove/promise-to-proof/blob/3ef1651418b44c3d0ee59e81cf3aec3c22e36454/checks/delivery-model/README.md) explains the command and model limits. [The proof report](https://github.com/grove/promise-to-proof/blob/3ef1651418b44c3d0ee59e81cf3aec3c22e36454/.p2p/work/delivery-completion-integrity/proof.md) retains the observations.

This model covers a limited set of failures and one restart. It assumes that the host really provides separate, protected verification runs. It does not prove that assumption. The model is now merged and can inform Phase 2, but the selected host's protections still need direct evidence.

## Phase 2: Make the running workflow enforce the rules

Build the smallest program that controls one work item's delivery on one supported host. This program is the controller. It starts the required stages and checks their records before allowing the result to be called complete.

Deliver the work in this order:

1. Choose the first host. Demonstrate that it can run separate agents, protect the code during verification, and identify the runs it actually started. Record unsupported capabilities.
2. Deliver one ordinary successful run. Reuse existing contract, file-storage, and identity checks. Require saved, readable review and proof for the exact current code and requirements.
3. Add failure and restart handling. Preserve unfinished work, reject late or stale reports, and retain the one-repair allowance when the same attempt restarts.
4. Record stage starts, finishes, failures, elapsed time, and available usage costs. Track any approved limits before starting more work. Mark unavailable costs as unknown and distinguish measured spending from an enforceable spending limit.

Done when tests on the chosen host demonstrate a successful delivery and reject changed code, missing evidence, unauthorized actions, and a second repair after restart. An interrupted handoff must resume safely or explain exactly what prevents recovery. Unrelated work must remain intact.

Decision before implementation: name the host and the controls it can actually enforce. Keep the existing full review and proof requirements. Do not add automatic strategy selection or support for several hosts in this phase.

## Phase 3: Test the real program against the model

Connect model actions to the controller's real operations. For example, a modeled restart must restart the controller and inspect what it recovered from saved records.

Deliver:

- Repeatable tests that drive the actual controller through success, failure, and restart sequences.
- Tests for overlapping operations where the supported host permits them.
- Saved failure sequences that another person can run again.
- Deliberately introduced controller defects that these tests detect.

Done when removing a real protection, such as the stale-report check, makes a test fail. The test must inspect the controller's returned result and saved state. Running a second copy of the model alone does not satisfy this phase.

Choose the test adapter language only after demonstrating that the pinned FizzBee tools can drive it. Document which cases use a real host and which use substitutes. Extend the model if a required controller behavior is outside its current bounds. [F05]

## Phase 4: Find out what saves time and money

Compare a few fixed ways to deliver one task while keeping the same full checking requirements. Start with review first, proof first, and both together where the host permits it. Compare agent model choices only when they meet the same permissions and checking requirements.

Deliver a repeatable comparison using a small representative set of tasks. Record total elapsed time, total cost, successful completions, missed defects, and the human work needed. Include failed attempts, repairs, waiting, and the cost of the comparison itself.

Done when the calculations match simple examples checked by hand, the same inputs reproduce the results, and the report clearly separates estimates from measurements. Show how the recommendation changes when costs or failure rates change. Running two checks together must count their overlapping time correctly.

Decide the task set, who judges correctness, and what improvement would justify the added machinery before evaluating it. This phase recommends choices; it does not automatically change how live tasks run.

## Phase 5: Let users choose a level of checking

Use the comparison results to define a small number of understandable choices. Each choice must say which checks run, which checks are skipped, and what can honestly be concluded.

Deliver:

- Examples of the result a user sees after normal, limited, and extended checking.
- Rules for who may select each choice and which requirements can never be skipped.
- A saved choice that survives restart and cannot silently become weaker.
- Evaluation on tasks that were not used to design the choices.

Done when users can explain the tradeoff and tests show that a partly checked task cannot receive the normal full-acceptance result. Existing meanings of `REVIEWED` and `PROVEN` must remain intact. Do not present an unsupported confidence percentage as a probability of correctness.

Obtain approval for the choices and result wording before enabling them. A choice can change the amount of checking only where allowed; it cannot silently change what the task promises to deliver.

## Phase 6: Run related tasks together safely

Extend the working single-task system to a larger task divided into smaller tasks. Run a smaller task only when the results it needs are available. Keep simultaneous work separate until it is ready to combine.

Deliver:

- A record of which tasks depend on which results.
- Rules that prevent two workers from changing the same shared resource at once.
- Spending and time limits for the whole task, with room reserved for combining and checking the results.
- A controlled way to combine completed work and verify the whole result.

Done when independent tasks can run together, dependent tasks wait, duplicate starts are rejected, and changed prerequisite results are detected. Passing each small task separately must never replace checking the combined result. Restart must not spend the same remaining allowance twice.

Agree who owns the combined result and which shared resources need exclusive access before implementation. Publishing any result remains a separate authorized action. [R03, R05]

## Phase 7: Try automatic choices on real work

Start by letting the system recommend a strategy while the approved normal strategy still runs. Compare its predictions with what actually happens. Then run a small, explicitly approved trial of automatic choices.

Deliver a defined trial population, approved limits, monitoring of results and cost, and a switch that restores the previous strategy. Record which strategy each task used so a restart does not change the agreement.

Done when measured improvements hold on new tasks within the approved limits. Demonstrate that automatic choices can be disabled without losing work or rewriting earlier results. A failed trial returns to the previous strategy rather than lowering the success criteria.

Decide the trial size, stop conditions, and who can enable or stop it before launch. Expand only after reviewing the trial's evidence.

# 20. How to turn each phase into deliverable work

Start with the next unfinished phase in Section 19. Create the fewest work items that each deliver a useful, testable result. Complete those items in their dependency order before advancing to the next phase. Do not start the former parallel workstreams as separate projects.

For each work item, record:

- The outcome a user or maintainer can observe.
- What is included and what waits for a later phase.
- The earlier result it depends on.
- The command or demonstration that shows it works, including a failure case.
- Any decision or permission needed before implementation.

Use the repository's existing `work/` contracts and `.p2p/work/` delivery records. Keep review and proof tied to the exact delivered version. Do not create a second checklist that competes with the acceptance contract.

Phase 1's model, runner, and explanation live in `checks/delivery-model/` in PR #25. Reuse them. Choose locations for later implementation files when the relevant work begins; do not create empty frameworks for the whole roadmap.

# 21. Acceptance gates and operational checks

## 21.1 Design and model gates

The handoff is ready for implementation only when the chosen increment has a clear scope, owner, source baseline, and acceptance criteria. The model gate requires traceable properties, explicit assumptions, meaningful reachable success and blocker states, and failing invalid variants. An incomplete exploration must be visible in the result.

Keep behavioral model checks separate from performance forecasts in CI. A probabilistic cost report must not make an unsafe policy eligible. Conversely, changing a performance parameter must not silently erase safety transitions.

## 21.2 Implementation and conformance gates

Test unauthorized actions before execution, stale and mistyped identities, candidate mutation during verification, incomplete archives, report-storage interruption, late results, duplicate writes, repeated resume, and contested dirty files. Test real host provenance rather than accepting a worker-supplied `independent: true` field.

Retain fixture-level and live-host evidence separately. A passing mock tracker test does not establish live tracker readback or real sandbox isolation. The repository’s scenario suite already calls for these distinctions. [R08, R09]

## 21.3 Profile and scheduler gates

A profile downgrade requires applicable authority and leaves a visible record. A deadline/budget stop preserves partial work and cannot become full acceptance. A parent schedule must enforce prerequisites, prevent conflicting writers, include integration cost, and check the current integrated candidate.

Test cases should include simultaneous budget admissions, changed upstream artifacts after child start, duplicate child dispatch, delayed child completion after cancellation, unavailable shared environments, and a parent contract amendment during execution.

## 21.4 Rollout and rollback

Begin with shadow policy selection: recommend a policy while executing the approved baseline, then compare predictions with observed outcomes. Enable selected policies only for an approved task population with spending and attention limits.

Monitor completion quality, integrity events, overruns, tail latency, and unexpected human intervention. Keep a stable fallback policy and a way to disable adaptation independently of the stage skills. Restoring a policy must not rewrite earlier reports or retroactively change the assurance promised for an in-flight episode.

# 22. Risks and mitigations

| Risk | Consequence | Proposed mitigation |
|---|---|---|
| Model/implementation drift | A verified design no longer describes the running skill/controller. | Versioned mapping, conformance tests, and review of protocol changes. |
| Weak verifier mistaken for strong implementer | Fewer reported defects appear to be improved quality. | Independent outcome labels and held-out adversarial cases. |
| False precision in assurance | Users interpret a profile or score as a correctness probability. | Evidence vectors, explicit limitations, calibrated metrics only. |
| Correlated failures | Multiple agreeing agents miss the same problem. | Evaluate combinations and independent methods; model common causes. |
| Optimizing only accepted runs | Policies hide costly failures or block difficult work. | Report all assigned episodes and useful completion rates. |
| State-space explosion | Model checks become expensive or incomplete. | Incremental models, justified abstraction, explicit cutoffs and coverage. |
| Excessive architecture | The optimizer costs more to build and operate than it saves. | Narrow first increment, fixed-policy baseline, measured overhead. |
| Budget races or delayed billing | Parallel work exceeds the intended monetary limit. | Reservations, reconciliation, conservative bounds, honest cap semantics. |
| Unsafe reuse | A small change invalidates evidence outside the detected dependency set. | Preserve full rechecks until non-interference is adequately established. |
| Parallel integration failures | Locally correct children interact incorrectly. | Isolated work, explicit interfaces, controlled integration and parent proof. |
| Hidden privacy leakage | Telemetry or routing exposes source material. | Local-first minimization, provider allowlists, access and retention controls. |
| Policy drift during recovery | A resumed run uses weaker checks than originally selected. | Persist policy identity; require authority for material changes. |
| Invalid performance assumptions | A predicted best policy performs poorly on real work. | Sensitivity analysis, task stratification, uncertainty, and shadow rollout. |
| Misleading completion vocabulary | A finished limited policy looks like full `PROVEN`. | Distinct workflow disposition and explicit gaps; preserve current verdicts. |

# 23. Open decisions for maintainers

Resolve these before the relevant phase, not necessarily before building the initial baseline model.

**Assurance governance:** Which tasks may use limited checking? Who can authorize that choice? Which repository obligations remain mandatory? Is a profile chosen per issue, per parent, or per requirement, and how do inherited constraints limit children?

**Result semantics:** What wording clearly distinguishes a finished policy from an accepted contract? How will existing consumers of `REVIEWED`/`PROVEN` avoid interpreting a new profile incorrectly?

**Runtime boundary:** Which host will be supported first? What can it actually enforce around model/tool access, read-only verification, provenance, timeouts, and spend? Which checks remain observations rather than enforced prevention?

**Modeling boundary:** What operations are atomic? Which interruptions are represented? What constitutes the same invocation after a crash? How are comparison-base, contract-text, and environment changes represented?

**Economics and evaluation:** What is the first representative workload? Who independently judges correctness? How are human attention, late defects, incomplete episodes, and severity recorded? What improvement is large enough to justify optimizer overhead?

**Scheduling and integration:** When are prerequisite outcomes considered sufficient to start a child? Which shared resources require serialization? Who owns integration? How are parent budgets and final verification reserves allocated?

**Adaptation:** Which decisions are delegated to the optimizer, which require user approval, and what happens when no feasible policy meets the requested constraints? How are policy changes versioned, tested, and rolled back?

**Tool fit:** Does the pinned FizzBee version demonstrate the necessary model, performance, and adapter behavior? What is the fallback when its performance semantics do not represent the required parallel timing accurately?

# 24. The next delivery to prepare

Issue #24 is closed, and PRs #25–#27 are merged. Phase 1 is complete. Prepare the first Phase 2 work item: demonstrate an enforceable delivery process on one named host. Read the current repository instructions and protocol, the delivered model's limits, and the existing filesystem helper before proposing new code.

The proposal must answer these questions in plain language:

1. Which host will we support first?
2. How will it prove that separate review and proof runs actually happened and could not change the code?
3. Which existing file and report checks can the controller reuse?
4. What is the smallest successful end-to-end example, and what missing or stale evidence must it reject?
5. Which decisions remain before implementation, and what follows in the restart-handling work item?

Save the agreed scope and its concrete checks in a canonical `work/` contract. Use Phase 2's ordered steps to decide whether host support and the first successful run fit one coherent item or need two dependent items.

Keep cost comparisons, optional checking levels, child-task scheduling, and automatic strategy selection in their later phases. This planning update does not create issues, authorize publication, or change the current acceptance rules.

# Appendix A. Illustrative policy schema

This is a proposed data shape, not an existing Promise to Proof configuration or validated FizzBee input. Model names are logical roles, not recommendations for current providers. Resource limits remain unset until explicitly supplied.

```yaml
schema: p2p-policy-draft/v1
policy_id: current-full-delivery-baseline
policy_version: 1
protocol_source: pinned-acceptance-contract-protocol
assurance_profile: current-full

required_stages:
  - implementation
  - independent_review
  - independent_proof

verification:
  ordering: parallel_if_host_supported
  candidate_mutation: forbidden
  required_scope: all_material_requirements
  reuse: exact_identity_and_valid_context_only

models:
  planning: approved_planner
  implementation: approved_implementer
  review: approved_reviewer
  proof: approved_proof_worker
  repair: approved_repair_worker

limits:
  automatic_repairs_per_invocation: 1
  episode_cost_cap: null
  deadline: null
  max_concurrent_stages: null
  parent_final_verification_reserve: null

integrity:
  exact_contract_approval_when_required: true
  host_attested_stage_provenance: true
  uncertain_effects_require_reconciliation: true
  external_effects_require_separate_authority: true
  preserve_unrelated_work: true

reporting:
  full_delivery_requires_matching_review_and_proof: true
  disclose_unexecuted_checks: true
  disclose_unknown_costs_and_partial_effects: true
```

Implementation review must determine defaults and reject ambiguous missing limits where they are required. Setting `parallel_if_host_supported` is not evidence that a host supports it. The approval source for this policy and the exact contract approval must be retained separately.

# Appendix B. Illustrative stage-event schema

This example contains placeholders and null measurements. It is not a live execution record. Context, evidence, and host provenance should reference protected artifacts where needed rather than exposing sensitive content in analytics.

```json
{
  "schema": "p2p-stage-event-draft/v1",
  "episode_id": "example-episode",
  "invocation_id": "example-invocation",
  "parent_episode_id": null,
  "source_key": "configured-tracker-stable-key",
  "stage": "review",
  "attempt": 0,
  "policy": {"id": "current-full-delivery-baseline", "version": 1},
  "identity": {
    "contract": "exact-contract-key",
    "candidate": "exact-candidate-key",
    "comparison_base": "exact-base-key",
    "environment": "environment-manifest-key"
  },
  "executor": {
    "model_version": "configured-model-version",
    "skill_revision": "pinned-skill-revision",
    "context_manifest": "retained-context-manifest",
    "host_invocation_ref": "protected-host-record"
  },
  "event": "stage_finished",
  "outcome": "not_recorded_in_this_example",
  "duration_ms": {"queue": null, "execution": null, "human_wait": null},
  "cost": {
    "currency": "configured-currency",
    "estimated": null,
    "reserved": null,
    "settled": null,
    "pricing_snapshot": "configured-pricing-version"
  },
  "usage": {},
  "artifact_refs": [],
  "evaluation_label": "unknown"
}
```

# Appendix C. Terminology

| Term | Meaning in this handoff |
|---|---|
| Acceptance contract | The authoritative statement of promised behavior and binding constraints. |
| Assurance profile | The selected verification commitments and their limits, not a probability of correctness. |
| Integrity floor | Rules that preserve truthfulness, identity, authorization, and valid claims in every profile. |
| Policy | Versioned rules for eligible actions, models/tools, resource use, and stopping. |
| Episode | The analysis unit used to account for complete delivery effort, including failures and repair. |
| Invocation | A specific workflow execution with its own current repair bound and provenance. |
| Candidate | Exact recoverable implementation content with relevant identities and context. |
| Oracle | An independent basis for deciding whether an observed behavior is correct. |
| Useful completion | A result independently assessed as satisfactory under the evaluation definition. |
| Safety property | A rule excluding an undesirable modeled state or transition. |
| Liveness property | A progress obligation under explicitly stated scheduling and environment assumptions. |
| Counterexample | An execution trace demonstrating violation of a modeled property. |
| Conformance testing | Exercising an implementation and comparing observable behavior with its model. |
| DAG | Directed acyclic dependency graph; not merely the order tasks appear in a document. |
| Critical path | A dependency path limiting completion time under the specified schedule and durations. |
| Pareto set | Options not dominated across the selected objectives under the stated estimates. |
| Incremental verification | Reusing justified evidence after a change based on its dependencies and non-interference. |
| Speculation | Starting provisional work before an assumption is confirmed, with explicit invalidation and waste accounting. |

# Appendix D. Sources and verification notes

Repository sources below are pinned to commit `f5917ce0471d56aac01711e720426748626c99d0` unless they are tracker links. Official FizzBee documentation was consulted on September 25, 2026. A documentation claim is not a local execution result; verify commands and capabilities against the version selected for implementation.

## Repository references

- **[R01] README and formal-verification ambition.** [Pinned README](https://github.com/grove/promise-to-proof/blob/f5917ce0471d56aac01711e720426748626c99d0/README.md). Establishes current product description and the explicit FizzBee/automation goal. The inspected commit changes the README relative to the earlier `8f9ddd400d46` snapshot discussed in the conversation.
- **[R02] Issue #23: Deliver a coherent issue through review and proof from one request.** [Issue](https://github.com/grove/promise-to-proof/issues/23). Defines the single-issue scope, authority boundaries, repair bound, host prerequisite, and testing expectations. Tracker state can change after this inspection.
- **[R03] Acceptance contract protocol.** [Pinned protocol](https://github.com/grove/promise-to-proof/blob/f5917ce0471d56aac01711e720426748626c99d0/docs/acceptance-contract-protocol.md). Authority for contract identity, revisions, handoffs, proof, parent/child composition, and publication separation.
- **[R04] `/deliver-issue` skill.** [Pinned skill](https://github.com/grove/promise-to-proof/blob/f5917ce0471d56aac01711e720426748626c99d0/skills/productivity/deliver-issue/SKILL.md). Operational instructions for actual host checks, fixed candidates, separate contexts, durable reports, exact digests, bounded repair, and resume.
- **[R05] `/slice-contract` skill.** [Pinned skill](https://github.com/grove/promise-to-proof/blob/f5917ce0471d56aac01711e720426748626c99d0/skills/productivity/slice-contract/SKILL.md). Outcome-oriented slicing, coverage maps, real dependency graph versus linear sequence, publication authority, and integrated parent completion.
- **[R06] Acceptance bundle v1.** [Pinned specification](https://github.com/grove/promise-to-proof/blob/f5917ce0471d56aac01711e720426748626c99d0/docs/acceptance-bundle-v1.md). Defines structural consistency checks and explicitly excludes evidence authenticity, adequacy, and full human-intention coverage from the checker’s assurance.
- **[R07] Deterministic acceptance-bundle checker.** [Pinned checker](https://github.com/grove/promise-to-proof/blob/f5917ce0471d56aac01711e720426748626c99d0/checks/verify_acceptance_bundle.py). Existing implementation to inspect and test before adding new deterministic gates. This handoff does not assert a formal proof of that code.
- **[R08] Issue-first delivery scenarios.** [Pinned scenarios](https://github.com/grove/promise-to-proof/blob/f5917ce0471d56aac01711e720426748626c99d0/checks/deliver-issue-scenarios.md). Human-runnable D1–D10 cases; not execution results.
- **[R09] Issue-first delivery validation.** [Pinned validation notes](https://github.com/grove/promise-to-proof/blob/f5917ce0471d56aac01711e720426748626c99d0/checks/deliver-issue-validation.md). Repository-authored local results, earlier rejected claims, and explicit unexecuted cases; not independently replayed here.
- **[R10] Proof and repair scenarios.** [Pinned fixture and scenarios](https://github.com/grove/promise-to-proof/blob/f5917ce0471d56aac01711e720426748626c99d0/checks/proof-repair-scenarios.md). Prior art for the public `save_report` fixture and independent expected outcomes referenced by the delivery tests.

## FizzBee primary references

- **[F01] Design quick start.** [Official tutorial](https://fizzbee.io/design/tutorials/quick-start/). State-machine modeling, assertions, and model-checking workflow.
- **[F02] Liveness and fairness.** [Official tutorial](https://fizzbee.io/design/tutorials/liveness/). Progress properties, fairness, and reachability concepts; assumptions must be made explicit.
- **[F03] Probabilistic modeling.** [Official tutorial](https://fizzbee.io/design/tutorials/probabilistic-modeling/). Branch probabilities and conditional analysis. The documented tooling can assign default equal probabilities; production estimates must not rely on that default without justification.
- **[F04] Performance modeling.** [Official tutorial](https://fizzbee.io/design/tutorials/performance-modeling/). Performance counters, multiple metrics, and distributions. This is not evidence that an arbitrary concurrent delivery scheduler is modeled correctly by summing counters.
- **[F05] Model-based testing quick start.** [Official tutorial](https://fizzbee.io/testing/tutorials/quick-start/). Demonstrated Go adapter, sequential/concurrent tests, and replayable test traces. Promise to Proof integration remains to be built.
- **[F06] Current language limitations.** [Official limitations](https://fizzbee.io/design/tutorials/limitations/). Python-like syntax has restrictions; expression structure and interleavings require care. Confirm the chosen version’s actual behavior.

## Conversation-derived direction

The configurable-assurance goal, monetary/time optimization, per-stage model choice, retry coupling, human-attention dimension, and dependency-graph parallelization come from this conversation. They are design inputs, not measurements or already approved repository changes. This handoff supersedes the earlier narrower framing that assurance must always remain fixed, while preserving explicit compatibility with the current protocol until changes are authorized.

**Final principle:** Spend verification effort deliberately, report exactly what it establishes, and optimize the whole delivery—not the appearance of a cheap green result.
