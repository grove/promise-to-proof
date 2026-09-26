# PROVEN: delivery completion integrity

Requirements: 10/10
Counterexamples tested: 14 deliberately broken variants, plus 18 reachable success/blocker witnesses and 11 finite baseline explorations.
Contract: `work/delivery-completion-integrity.md`, v1.
Contract snapshot: exact retained candidate manifest bytes, SHA-256 `7cfbf6558846415b06b130d4989ca88a93ea73f06cb341eb02b30e7ac4b02956`.
Candidate: `snapshot:sha256:be7ea1690adb91888d089ab36aa2a70f0069bb7c258e9d21bd22db9f7851ad98`.
Comparison base: `69c02fe5a0e876b104baacca2e4075f801974d40`.
Candidate stability: unchanged, complete inventory/bytes/modes/symlink targets validated before and after.
Contract stability: unchanged, exact bytes rehashed before and after.
Invocation: `/root/proof25_refresh`, independent installed `/Users/grove/.agents/skills/prove/SKILL.md` invocation.
Verification context: macOS-26.6.2-arm64-arm-64bit; Python 3.9.6; pinned FizzBee v0.5.3 macOS arm64. Candidate, base, and records were outside writable sandbox roots; no escalation, delegation, product writes, or contract writes. All generated files were confined to `/private/tmp`.
Storage: pending enclosing workflow retention and readback. Exact report returned at `/private/tmp/p2p-proof25-main69.md`; fresh evidence at `/private/tmp/p2p-proof25-main69-evidence`. Intended durable evidence root is `.p2p/work/delivery-completion-integrity/evidence/proof-main69/`, abbreviated `E/` below. Preserve this report verbatim and record storage confirmation separately.

## Outcome

The bounded model demonstrates successful initial delivery, repair with both fresh verifications, restart with durable repair accounting, and rejection of missing or stale completion evidence. Every deliberately weakened protection produced its corresponding concrete counterexample. These observations establish the requested model capability; they do not prove live-agent conformance or host isolation in the running workflow.

## Agreement and identity reconciliation

I read the entire v1 contract including its imported issue #24 text, the acceptance protocol, delivery skill, selected roadmap sections, README, model, runner, and planner reconciliation. No parent or prerequisite applies. The planner report says the updated roadmap preserves the selected completion-integrity promises and excludes later roadmap phases. I independently compared roadmap sections 8, 9, and 10 with the original source at `bb53d2472b37ef6c441c8121cecfd7e16814d465`; they are byte-identical. Current Phase 1 preserves the same outcomes. Its links to old results are historical attribution, not evidence for this proof. No material discrepancy remains and no requirement was narrowed.

The modeled protocol and delivery skill match the exact Git bytes at `41bebc726a8cc71c1d2f22d822ade006f4e78121`. The historical source handoff digest remains attribution to the earlier roadmap, while the captured live input has its new digest below. The README describes the older `f5917ce0471d56aac01711e720426748626c99d0` baseline and the current local work/record conventions.

Before and after execution, an independent inventory check compared all 112 candidate entries and all 108 base entries to the recoverable manifests, including exact file bytes, executable modes, symlink targets, and absence of extra files. The full base manifest also matched `git ls-tree` and every blob at the comparison-base SHA. Canonical JSON hashing of the complete candidate manifest reproduced the full candidate key. The work-item hash and every binding-input hash matched:

| Input | SHA-256 |
|---|---|
| `docs/acceptance-contract-protocol.md` | `bec3503abc6ebc40356e662ca0b279be73a4da482eb1616a5c5b435509184351` |
| `plans/promise_to_proof_optimization_handoff.md` | `c09ae44b02d167ae136cf173f3c8611115e4ee0eaeb295dcf2b9269e36b9a928` |
| `skills/productivity/deliver-issue/SKILL.md` | `9ecacf205eb6f399b9f487867cd1ddf2ec55155a9fef9878c79ae2ec8a41fbf1` |

The candidate/base metadata and reconciliation records were also hashed before and after; both inventories are identical. Evidence: `E/p2p-proof25-main69-before.txt`, `E/p2p-proof25-main69-after.txt`, and `E/p2p-proof25-main69-identities.py`. Recoverable candidate and base metadata came from the enclosing workflow's refresh25-main69 records, not a mutable branch name.

The concurrent PR #26 merge changed only `checks/publish-pr-scenarios.md` and `skills/productivity/publish-pr/SKILL.md`. I inspected that diff and established those are the only candidate changes since the previous refresh. They concern publication and checkout disposition, outside this model agreement. Contract and binding sources are byte-identical. The planner reconciliation remains applicable to the agreement; its old proposed comparison base is historical. This report binds the new base above, independently verified against Git objects in `/var/folders/vq/593qxcm57l90w1dlpywl_7nw0000gn/T/p2p-refresh-25-ktwpyoq5/repo`. An initial base-object lookup in the operator checkout failed because that checkout lacked the new commit; no identity claim relies on that lookup. A preliminary run was superseded by the full run below after successful complete identity verification.

## Fresh execution and independent observations

From `/Users/Shared/p2p-issue-24-6krj8of_/refresh25-main69/candidate`, I executed:

```sh
TMPDIR=/private/tmp python3 checks/delivery-model/check.py --fizz /private/tmp/p2p-fizzbee-24/fizzbee-v0.5.3-macos_arm/fizz --output-dir /private/tmp/p2p-proof25-main69-evidence
```

The command exited 0 and printed `PASS: 43 checks. Model evidence only; no live-agent conformance claim.` FizzBee subprocess time totaled 49.262 seconds. The runner verified all three executable pins, recorded in `E/summary.json`. The source model SHA-256 was `4ac1ae31fed4764475d582a563a294401830b99b7d844a0c45f8c14d660e6753`.

I inspected all 32 fresh ordered traces, their terminal states, model actions and mutation mechanisms. I also ran the separate `E/p2p-proof25-main69-inspect.py` audit, which asserted completion facts against the contract, checked that repair cleared old bindings and launched/returned both fresh stages, checked each mutation's concrete violation, and confirmed that retained models differ from the candidate model only in scenario/mutation/witness constants. Its result is retained in `E/p2p-proof25-main69-audit.txt`. No prior proof was used as an observation.

Each baseline returned successful finite exploration and stayed below the configured 64-action bound:

| Scenario | Nodes | Maximum actions |
|---|---:|---:|
| initial | 1575 | 15 |
| repair | 3148 | 20 |
| exhausted | 3148 | 20 |
| identity | 1699 | 15 |
| text | 7281 | 16 |
| candidate | 7281 | 16 |
| base | 7281 | 16 |
| report-lost | 2534 | 16 |
| report-access | 2534 | 16 |
| evidence-lost | 3299 | 20 |
| evidence-access | 3299 | 20 |

## Requirement verdicts

References below are beneath `E/`. Each named run retains its generated model, command, output, and observation. Witnesses and mutations additionally retain `trace.json` and `trace.txt`.

| ID | Observation and independent oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | Actions separately implement, launch/return two verifier roles, save/read back each artifact, repair, restart, and complete. Fresh traces exercise all lifecycle actions. Stage invocation IDs differ; trusted read-only isolation is explicitly an abstraction. This matches the issue's lifecycle scope. | `summary.json`, `baseline-*`, `witness-initial`, `witness-repair`, `witness-restart`; candidate model and README | proven |
| R2 | `SameReports`, `CurrentText`, `CurrentCandidate`, and `IndependentFullStages` hold in all baselines. Missing stages block; mismatched proof text identity 2 versus review 0 yields `identity`. Removing agreement checking reaches completion with those distinct bindings. Oracle is exact current contract/candidate agreement required by the protocol. | `witness-missing-stage`, `witness-identity`, `mutation-identity`, `baseline-*` | proven |
| R3 | Changing base to 1 leaves review base 0 and blocks with `base`. The weakened variant completes with that mismatch and fails `ComparisonBase`. | `baseline-base`, `witness-base`, `mutation-base` | proven |
| R4 | The text fault changes contract identity to 1 while `revision` remains `v1` and both reports bind 0. The intact model blocks with `text`; the weakened variant completes and fails `CurrentText`. Exact text, not revision label, is the independent protocol oracle. | `baseline-text`, `witness-text`, `mutation-text` | proven |
| R5 | Candidate drift to 1 leaves both report candidate identities at 0 and blocks. Its mutation completes illegally. Successful repair clears both bindings, then launches and returns both stages for candidate 1 with invocation IDs 3 and 4 before completion. | `baseline-candidate`, `witness-candidate`, `mutation-candidate`, `witness-repair`, independent audit | proven |
| R6 | Baselines assert reports/evidence both equal `[3,3]` at completion. Named witnesses block unsaved, unread, lost, inaccessible report/evidence states and evidence absent after interrupted saving plus restart. Each corresponding mutation completes with the deficient state and fails the artifact property. Absent reports also imply missing stages. Oracle is saved, reread, retrievable content, not path existence. | `witness-report-*`, `witness-evidence-*`, `witness-missing-stage`, `mutation-report-*`, `mutation-evidence-*` | proven |
| R7 | Restart success retains one actual/used repair and rereads saved artifacts. Repeated proof failure after repair and restart yields `repair-exhausted` with both counters 1. Resetting allowance on restart permits an actual second repair and fails `RepairBound`. | `witness-restart`, `witness-exhausted`, `mutation-repair-reset`, `baseline-exhausted` | proven |
| R8 | Initial success ends with both reports/evidence `[3,3]`, current bindings and distinct stages. Repair success and restart success are reachable. All 15 other witnesses expose the requested specific blockers. This is observed reachability, not a declared predicate alone. | All 18 `witness-*` runs, independent audit | proven |
| R9 | All 14 deliberate variants fail the expected named assertion with a concrete corresponding violation, never a parser error or unrelated assertion. The retained models preserve independent assertions; only operational mutation constants change. | All 14 `mutation-*` runs, `p2p-proof25-main69-audit.txt` | proven |
| R10 | Documented public command reproduced all checks with pinned tool and modeled repository revision. README maps properties to protocol and documents historical baseline differences, finite fault families, timing/cutoff handling, atomicity, lack of fairness, trusted stage judgments, and excluded live behavior. Actual environment, runtimes, node counts and maximum depths are retained. | README, runner, `summary.json`, baseline observations, `p2p-proof25-main69-run.txt` | proven |

## Mutation results

The retained traces demonstrate these exact failing facts:

| Variant | Assertion | Violating observation |
|---|---|---|
| identity | SameReports | Completion with review binding `[0,0]`, proof `[2,0]` |
| text | CurrentText | Completion with current contract 1, reports 0, revision still v1 |
| candidate | CurrentCandidate | Completion with current candidate 1, both reports 0 |
| base | ComparisonBase | Completion with current base 1, review base 0 |
| repair-reset | RepairBound | Restart followed by second actual repair; actual count 2, scheduler count 1 |
| report-save | DurableReports | Completion with reports `[1,1]` |
| report-read | DurableReports | Completion with reports `[2,2]` |
| report-lost | DurableReports | Completion with reports `[4,3]` |
| report-access | DurableReports | Completion with reports `[5,3]` |
| evidence-absent | DurableEvidence | Completion with evidence `[0,0]` after restart |
| evidence-save | DurableEvidence | Completion with evidence `[1,1]` |
| evidence-read | DurableEvidence | Completion with evidence `[2,2]` |
| evidence-lost | DurableEvidence | Completion with evidence `[4,3]` |
| evidence-access | DurableEvidence | Completion with evidence `[5,3]` |

## Bounds and unresolved gaps

No unresolved acceptance gap. Exploration is exhaustive within the eleven finite scenario families, not across every combination of faults or unbounded executions. One work item, two verifier roles, two artifacts per verifier, one restart and one repair are modeled. The broken reset variant reaches two repairs. Atomic actions abstract storage and threads; exact identities are integers rather than cryptographic hashes. Stage correctness and isolation are assumed. No fairness or universal eventual completion is claimed; deadlock detection is disabled. One environment fault can interleave with enabled work; repeated churn and post-completion changes are excluded. Witness/mutation searches stop at the first relevant failure and are not exhaustive enumerations. No timeout or cutoff occurred; no live-agent, host-adapter or real filesystem-conformance claim is made.

## Repairs needed

None. Any changed candidate requires fresh full proof and separate review.

Next steps:
1. Enclosing workflow saves this exact report and fresh evidence under the work item's durable records, rereads them, and confirms retention separately.
2. Compare this full proof with the independent full review for the same candidate and base; assess PR #25 through `/merge-readiness` with those saved references before merge.
