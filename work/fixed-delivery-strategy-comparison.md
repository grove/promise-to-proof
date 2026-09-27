# Acceptance contract: Compare fixed delivery strategies on the supported Codex host

Contract revision: v2
Source: [Optimization handoff, selected Phase 4 scope](../plans/promise_to_proof_optimization_handoff.md)
Source: [Acceptance contract protocol](../docs/acceptance-contract-protocol.md)
Source attribution: [GitHub issue #32](https://github.com/grove/promise-to-proof/issues/32), retrieved 2026-09-26 at 18:25 UTC, last updated `2026-09-26T18:15:33Z`. The issue body is retained verbatim below; its UTF-8 SHA-256 is `f08d81a0b76cddc2b2163e36d239bfd26ffc485666528bc229add56e5f3e55cb`. No comments or amendments were returned. The linked roadmap matches commit `cc27a47f5ee765cff3cf13b21c36f974cb1234ae`, SHA-256 `39a41f7cb454febb61cb96bed2426456fbaf5a58ec9a18f149f255fa3d581626`.
Parent: None
Prerequisites: The Phase 2 [delivery controller](../skills/productivity/deliver-issue/scripts/p2p_delivery.py) and [documented public commands](../docs/p2p-delivery-controller.md), integrated through PR #29; Phase 3 [conformance suite](../checks/delivery-model/conformance.py) and its [retained proof](../.p2p/work/delivery-model-conformance/proof.md), integrated through PR #31. Their source files and retained records are present. These are prerequisites, not inherited parent contracts or fresh proof of host capabilities.

Intended outcome: A maintainer can reproduce a comparison of fixed single-task delivery strategies on macOS Codex CLI, inspect complete cost, time, correctness, and human-effort accounting, and understand conditional recommendations without changing live delivery policy.

Advisory learnings: None; no advisory learning register is present.

Planning status: Approved for the bounded pilot. After receiving the three-task, independent-oracle, 20% threshold, and six-episode recommendations, the user replied “I approve. Do it.” This authorizes scoped local implementation and the six pilot episodes. It does not authorize additional episodes, publication, or a live policy change. The completion below may be an inconclusive comparison; no improvement is promised.

## Acceptance matrix

| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | Issue planning decisions; roadmap §19 Phase 4, §24, §18.1 | Fix the representative task set and evaluation protocol before evaluation, including eligibility, baseline, primary metrics, resource envelope, stopping rules, and independent assessment method. | Selecting only favorable completed tasks or changing the population after seeing results invalidates a comparison. Repeated greeting fixtures alone do not establish representativeness. | Retained evaluation input manifest and report | Approved pilot population and protocol below | Case `evaluation-preregistered`: compare the recorded task identities and rules with every assigned episode and the dated agreement; reject silent substitutions and report unexecuted configurations. | planned |
| R2 | Issue scope bullets 1–2; roadmap §13.1, §19 Phase 4 | Compare review-first and proof-first fixed strategies, and concurrent review/proof where supported, under the same full checking obligations. Model-choice comparisons, if included, obey the same permissions and checking requirements. | Reordering two checks that both always run cannot by itself reduce their summed direct cost. A missing check, extra repair allowance, or weaker model permission makes a strategy ineligible. Unexecuted alternatives remain explicitly estimated or unavailable. | Documented repeatable comparison command and resulting strategy report, using retained episode inputs | Declared strategy definitions and unchanged protocol obligations | Case `same-checks-different-order`: both serial orders consume the same two fixed checks and cost inputs; case `ineligible-strategy` excludes omitted required checks. Record concurrency eligibility separately under R9. | planned |
| R3 | Issue scope bullet 4; roadmap §19 Phase 4 | Identical retained inputs reproduce comparison calculations and conclusions through a documented command. | Fresh stochastic agent runs need not be identical. Reproducibility concerns retained inputs, parameters, calculation version, and any analysis seed. Empty cohorts cannot yield fabricated savings or a best strategy. | Comparison command and report | Fixed input records and independently calculated expected values | Case `repeat-inputs`: run the documented command twice from retained inputs and compare all result values and conclusions. Case `empty-cohort` reports unavailable rates and no evidence-based recommendation. Retain command, inputs, and outputs for another checkout. | planned |
| R4 | Issue scope bullet 3; roadmap §11.1, §16.3, §18.1 | Account for every assigned episode, including failures, interruptions, blocked or abandoned work, one allowed repair, repeated verification, and comparison overhead. Report totals per submitted episode and per independently satisfactory completion with explicit denominators. | Failed work cannot disappear from totals. Reconciled receipts for the same attempt cannot be charged twice. With zero useful completions, cost per completion is undefined rather than zero. | Episode inventory, attempt receipts, and aggregate report | Hand-counted episode ledger with stable episode and attempt identities | Case `cohort-accounting`: use two synthetic assigned episodes costing 3 and 5 units, only one satisfactory; assert total 8, mean 4 per assigned episode, 8 per useful completion, and completion rate 1/2. Add repair, exhausted repair, and resumed known-attempt cases from existing controller fixtures; assert all actual attempts and overhead are included exactly once. | planned |
| R5 | Issue scope bullet 3; roadmap §16.2–16.4, §24 | Judge successful completions and missed defects independently of workflow verdicts, retaining satisfactory, defective, and unresolved outcomes with denominators and evaluation limits. | REVIEWED or PROVEN is not its own correctness oracle. An unjudged result is not satisfactory or defect-free. Known defects missed by both verifiers still count as missed defects. | Independent task oracle and adjudication record joined to workflow outcomes | Approved prewritten behavioral checks and maintainer adjudication for ambiguous outcomes | Case `false-green`: supply a known defective result with passing workflow reports and require defective adjudication. Case `unknown-outcome` preserves unresolved status. Inspect agreed task oracles and held-out checks separately from worker reports before evaluating the cohort. | planned |
| R6 | Issue scope bullets 3–4; roadmap §11.4, §13.3 | Calculate end-to-end elapsed time with overlap, queueing, startup, waiting, repairs, and final readback accounted for without double-counting simultaneous work. Report distributions and incomplete observations honestly. | Summed parallel stage durations are compute time, not elapsed time. Missing intervals cannot silently become zero. Restart waiting remains part of the agreed episode. | Episode timeline and duration report | Hand-checked interval arithmetic and recorded episode boundaries | Case `overlap`: synthetic review interval [0,6] and proof [2,10] yield elapsed 10 and summed stage time 14. Case `serial`: [0,6] then [6,14] yields elapsed 14. Add separate setup, waiting, repair, and readback intervals and assert the independently calculated episode duration; identify incomplete timing. | planned |
| R7 | Issue scope bullets 3, 5; roadmap §11, §17.1–17.2 | Report total monetary cost with measured charges, estimates, and unknown amounts distinguished. Retain provenance for prices and cost assumptions. Include failed work and evaluation overhead. | Token usage is not settled spend. Missing costs are not zero. Estimated prices do not create a hard spending guarantee. A known subtotal plus unknown components is not a known total. | Cost ledger and report linked to attempt usage and charge inputs | Recorded settled charges where available; independently supplied price snapshot and hand calculations for estimates | Case `unknown-cost`: ingest a current controller receipt with cost `unknown` and preserve an unknown total. Case `priced-estimate`: apply declared synthetic rates to known usage and label the result estimated. Case `partial-cost`: preserve a known subtotal and identify missing components. | planned |
| R8 | Issue scope bullet 3; roadmap §3.1, §11.4, §16.3 | Record active human work, interruptions, and passive waiting separately, including independent judging and comparison preparation effort. | Passive waiting cannot stand in for active effort. Missing manual observations remain unknown rather than zero. | Human-effort observations and report | Independently recorded durations and interruption counts | Case `human-ledger`: 3 active minutes, 10 waiting minutes, and 2 interruptions remain distinct; include evaluator effort in comparison overhead without double-counting it. A missing effort entry is reported unavailable. | planned |
| R9 | Issue host limitation and boundaries; roadmap §19 Phase 4, §21.2 | Bind measurements to the actual host/version, controller and model configuration, exact inputs, and evidence type. Claim live concurrent verification only when supported-host evidence establishes it. | Model schedules, fake transport, and competing resume processes do not establish live concurrent review/proof. Single-host observations cannot establish results for another host. | Report provenance, actual host receipts, and concurrency capability evidence | Host-issued session and completion receipts, protected fixed-candidate identities, and observed overlapping intervals | Case `evidence-classification`: distinguish synthetic schedules, substitute controller results, and actual host measurements. Case `unsupported-overlap`: absent live capability evidence leaves concurrency unexecuted or estimated. Any measured concurrency claim must retain distinct verifier receipts and demonstrate protected unchanged inputs and actual overlap. | planned |
| R10 | Issue scope bullet 5; roadmap §18.2, §19 Phase 4 | Show how recommendations depend on changes in costs and failure rates, including ranges where the preference changes or no choice clearly wins. | A single favorable point estimate cannot establish general superiority. Performance probabilities cannot remove safety obligations. Sparse evidence and unevaluated outcomes stay visible. | Sensitivity inputs and comparison report | Hand-checked synthetic break-even cases, separate from measured parameters | Case `sensitivity-crossover`: synthetic A costs 2 plus repair cost 8 with probability q; B costs 5. At q=0.25 A costs 4, at q=0.5 A costs 6, and at q=0.375 they tie. Hold checking and useful-completion assumptions explicit. Assert the corresponding cost preference and disclose that these are synthetic assumptions. | planned |
| R11 | Issue planning decisions; roadmap §15.2, §19 Phase 4, §24 | Assess recommendations against the improvement threshold agreed before evaluation, after comparison costs and correctness outcomes are included. Report inconclusive or unfavorable findings without promising savings. | A faster result with more missed defects cannot be called an unqualified improvement. The threshold cannot be selected after observing which strategy wins. | Final recommendation and retained decision record | Approved provisional 20% elapsed-time rule and quality constraints below | Case `threshold-boundary`: test cases below, at, and above the agreed rule with evaluation overhead included. Case `no-supported-winner` reports no justified change when evidence or quality is insufficient. | planned |
| R12 | Issue boundaries; roadmap §19 Phase 4, §24; current protocol | Keep the comparison advisory and preserve full independent review/proof, exact identities, authorization, durable evidence, unrelated work, and the existing one-repair limit. | Evaluation must not silently switch live delivery policy, weaken acceptance labels, reuse reports for a changed candidate, or reset repair allowance on restart. | Delivered comparison, controller public operations, retained reports, and source checkout | Existing protocol and controller invariants | Case `advisory-only`: generating recommendations leaves live policy unchanged. Reuse `test_repair_refreshes_both_and_exhaustion_persists`, `test_successful_repair_rereviews_and_reproves`, and identity/authority fixtures when affected code changes. Inspect any evaluation dispatch for matching full reports and separate authority; retain all result evidence under the canonical work item. | planned |

## Existing seams and evidence limits

The current public delivery seam is `python3 skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo <source> run work/<task>.md --comparison-base <full-sha> --authorize-local`, with `status` and `resume` commands. Reading records is sufficient for offline calculations; planning runs no delivery commands.

`Delivery.run()` currently invokes review then proof. It has no strategy selector. The exclusive work-item lock prevents a second mutating controller from proceeding; it does not implement parallel verifiers. The Phase 3 proof describes one small serial live-host run, not measured strategy comparisons.

Existing records include `delivery.json`, `admission.json`, and `attempts/<id>/launch.json`, `events.jsonl`, and `exit.json`. Attempts record wall-clock starts/finishes, subprocess elapsed time, available token usage, identities, and literal `unknown` cost. They do not separately supply human effort, queue time, judging cost, or all comparison overhead. Missing observations must be collected or disclosed before drawing conclusions.

Reusable accounting cases in `checks/test_p2p_delivery.py` cover success, successful repair, repair exhaustion, known-result resume, and uncertain launch. They mostly use substitute transport against one greeting task. They establish useful accounting boundaries, not representative task difficulty or independent quality labels.

The proposed comparison seam is one documented reproducible command and its retained report. The exact implementation path and data format are implementation choices, not a requirement for a new framework. Approval of this proposed contract would establish that public outcome. Live nonbaseline execution requires demonstrated capability; estimates alone cannot satisfy the representative evaluation or independent outcome requirements.

## Unresolved gaps

- No missing planned seam or oracle. Actual measurements, host access, and task outcomes are execution evidence to gather, not inferred results.
- The baseline records monetary charges as unknown. Preserve that limitation and any missing human-effort observations. Do not recommend adoption when required quality, effort, cost, or payback evidence is unavailable.
- Live concurrent verification is not established. This pilot compares the two serial orders; concurrency is an explicitly synthetic overlap calculation unless separately demonstrated and authorized within the episode envelope.

## Approved pilot decisions

Authorization: The user approved the recommendations with “I approve. Do it.” after the saved v1 proposal and six-episode pilot recommendation. This v2 fixes those choices before evaluation. Initial implementation baseline and comparison base: `cc27a47f5ee765cff3cf13b21c36f974cb1234ae`. Earlier proposal bytes are retained under the work item's history directory.

1. **Task population.** Three bounded Python tasks: the existing greeting task as a smoke baseline; implement `save_report(path, text)` with UTF-8 Unicode, overwrite, return-None, and propagated-I/O-error requirements; repair an existing `save_report` implementation that swallows `OSError`. Reuse the task requirements in `checks/check_p2p_delivery_host.py` and `checks/proof-repair-scenarios.md`. These tasks represent small Python delivery and repair only. Failure, exhausted repair, restart, missing-cost, and overlap cases remain separate accounting checks.
2. **Independent correctness.** Write executable expected-output and error-behavior checks from the task requirements before workers run. Keep evaluation-only checks and seeded-defect details outside worker context. The maintainer adjudicates ambiguous outcomes; until then they remain unresolved. Workflow REVIEWED and PROVEN reports remain mandatory but never supply their own correctness labels. For greeting, the oracle checks exact stdout `hello\n` and exit zero. For `save_report`, it checks UTF-8 bytes after creation and overwrite, `None` returns, and an `OSError` from a path with a missing parent. Before evaluation, verify the oracle passes the independently specified valid behavior and rejects the seeded swallowed-error behavior.
3. **Fixed strategies.** Run review-first and proof-first once per task, six assigned episodes total, in fresh isolated task repositories. Keep the configured model and reasoning settings fixed; the inspected configuration is `gpt-6-luna`, `xhigh`, with the OpenAI provider and Codex CLI `0.157.1`. Record actual version and configuration and stop rather than mixing changed settings. Alternate which order runs first across tasks to avoid assigning one strategy only earlier run positions. Both required verifiers run before any repair; changed candidates receive both fresh checks. Use experimental copies for order changes and retain their exact differences from the controller baseline. Do not change the normal controller's policy.
4. **Bounds.** Admit no more than six episodes. Each episode permits at most eight dispatches, including the two host preflights, and at most 1,800 elapsed seconds. These are conservative execution ceilings selected for the approved pilot, not new product behavior or an enforceable monetary limit. Preserve the one-repair allowance and controller authority boundaries. Stop on unavailable host protections or uncertain dispatch rather than repeating a possibly completed effect. Retain blocked episodes in the assigned cohort. Do not authorize more episodes from a favorable intermediate result.
5. **Decision rule.** The provisional improvement target is at least 20% lower median end-to-end elapsed time, no lower useful-completion rate, no additional independently observed missed defects, and no increased active human effort on the same cohort. Count failed episodes, report tails, and include all comparison overhead. Report a separate break-even calculation when cost/effort inputs are available; otherwise report its missing inputs. Adoption remains unsupported without an acceptable payback horizon. This six-episode feasibility pilot is too small to establish reliable comparative performance, so it may describe observed differences and the threshold calculation but must conclude that adoption evidence is inconclusive. No confirmatory evaluation is included.
6. **Measurement.** Use retained episode and host receipts for elapsed time, attempts, and available usage. Monetary charges, human active time, waiting, and interruptions remain unknown where not observed. Do not invent zero effort for autonomous work. Preserve task identities, independent oracle results, host/configuration identity, controller-copy hashes, inputs, outputs, and the exact reproducible analysis command under `.p2p/work/fixed-delivery-strategy-comparison/`. Keep source content and private prompts out of analytics beyond the authorized local evidence.

## Open questions

- None blocks this bounded pilot. A later confirmatory evaluation needs its own repetition count, stopping rule, resource authority, and accepted payback horizon. Any ambiguous task result requires maintainer adjudication before it can count as satisfactory; this pilot can retain it as unresolved.

## Out of scope

- Phase 4.1 host support, cross-OS portability, optional checking profiles, child-task scheduling, automatic strategy selection, and production rollout.
- Weaker REVIEWED or PROVEN semantics, omitted required checks, extra automatic repairs, and evidence reuse across changed candidates.
- A universal workflow platform, telemetry service, provider ranking, or mandatory model-choice experiment. Model comparisons are conditional on agreed eligible configurations.
- Publication, tracker edits, commits, merges, deployment, and implementation or evaluation during this planning invocation.

## Source reconciliation

- Issue scope bullet 1 maps to R2 and R9; bullet 2 to R1–R3; bullet 3 to R4–R8; bullet 4 to R3 and R6; bullet 5 to R7 and R10; bullet 6 to R9.
- The required decisions map to R1, R5, and R11. The controller reuse, concurrency caveat, and unchanged rules map to the prerequisites, existing-seam notes, R9, and R12.
- Roadmap §19 Phase 4 and §24 control this scope. Sections 11, 13, 16, and 18 supply applicable accounting and evaluation meaning; their later-phase experiments are not imported wholesale.
- Stable attempt accounting is necessary to include failures and repairs without double-counting resumed work. Unknown values and zero-success boundaries are necessary to avoid false totals and success rates. These are consequences of the promised comparison, not added product features.
- No child decomposition or parent contract applies. No existing requirement IDs or proof verdicts were imported.

## Imported issue text

The following body is retained verbatim from the attributed issue import.

```markdown
Compare fixed delivery strategies on macOS Codex CLI to identify time and cost savings while preserving the same full checking requirements.

## Scope

- Compare review-first, proof-first, and concurrent review/proof where the host permits it. Compare agent model choices only under the same permissions and checking requirements.
- Deliver a repeatable comparison using a small representative task set.
- Record total elapsed time, total cost, independently judged successful completions, missed defects, and human effort. Include failed attempts, repairs, waiting, and comparison costs.
- Verify calculations against simple hand-checked examples, reproduce results from identical inputs, and count overlapping execution time correctly.
- Separate estimates from measurements, mark unknown costs, and show how recommendations change with costs or failure rates.
- Identify the actual host and version. Do not generalize single-host measurements to other hosts.

Reuse the delivered controller, available timing and usage records, and representative fixtures. Phase 3 conformance work was integrated through PR #31; its limited live-host evidence does not establish concurrency support.

## Planning decisions and boundaries

Before evaluation, agree on the representative tasks, who independently judges correctness including missed defects, and what improvement justifies the comparison and added machinery.

Use /plan-acceptance to save the agreed scope and checks in a canonical work/ contract before implementation or evaluation. Retain current full independent REVIEWED and PROVEN requirements, exact identities, authorization, durable evidence, and repair limits.

Phase 4 recommends choices without automatically changing live delivery. Additional hosts, optional checking levels, child-task scheduling, automatic strategy selection, and weaker acceptance semantics are excluded.

## Source

[Exact optimization handoff](https://github.com/grove/promise-to-proof/blob/cc27a47f5ee765cff3cf13b21c36f974cb1234ae/plans/promise_to_proof_optimization_handoff.md)

Selected scope: Section 19, Phase 4, and Section 24, with applicable accounting, evaluation, and planning guidance. Section 19 controls delivery order. The source specification remains authoritative.

- Repository: grove/promise-to-proof
- Path: plans/promise_to_proof_optimization_handoff.md
- Commit: cc27a47f5ee765cff3cf13b21c36f974cb1234ae
- SHA-256: 39a41f7cb454febb61cb96bed2426456fbaf5a58ec9a18f149f255fa3d581626

The pinned GitHub file was retrieved and matched the local bytes.

This issue selects Phase 4. Issues #24, #28, and #30 cover earlier phases of the same roadmap.

<!-- grove:create-parent-issue source=grove/promise-to-proof:plans/promise_to_proof_optimization_handoff.md -->
```

## Change notes

- Initial proposed contract v1, R1–R12. Created under the user's `/plan-acceptance` request for issue #32. Open evaluation decisions remain visible; no threshold, judge, workload, or live spending authority is inferred. Recommendations requested during planning were recorded as pending choices without changing requirement IDs or material promises. No implementation or acceptance verdict is claimed.

- v2: User approval settled R1, R5, and R11 inputs and authorized the scoped pilot. Requirements R1–R12 retain their meanings and IDs; missing-input plan states become planned. The approved decisions now fix workload, judge, model configuration, six episodes, reporting limits, and the provisional decision rule. Retained v1 remains historical.

## Implementation handoff

The user authorized local implementation and the bounded pilot with “I approve. Do it.” Use the approved decisions above. Implement the smallest complete solution inside the Phase 4 scope, preserve IDs and promises, and capture one resulting candidate for separate review and proof. Keep durable execution records under `.p2p/work/fixed-delivery-strategy-comparison/`. The six-episode feasibility comparison is authorized; ambiguous judgments remain unresolved pending the maintainer.

## Proof handoff

Evaluate every requirement against this exact contract revision and one fixed candidate. Inspect the retained input cohort, independent outcome labels, hand-calculated examples, reproducibility, measured-versus-estimated distinctions, host evidence, and conditional recommendations. Record observations and verdicts in a separate proof report. Planning states remain `planned` or `gap`.

Next steps:

1. Implement and run the approved six-episode pilot within its limits.
2. Save the implementation report and exact candidate for separate review and proof.
