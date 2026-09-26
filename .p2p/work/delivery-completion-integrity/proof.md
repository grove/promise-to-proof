# PROVEN: issue #24, delivery completion integrity

Requirements: 10/10
Counterexamples tested: 14 deliberate mutations, each producing its named violation; 15 blocker witnesses and 3 successful witnesses
Contract: `work/delivery-completion-integrity.md`, v1
Contract snapshot: exact bytes recoverable from `candidate.json` manifest; SHA-256 `7cfbf6558846415b06b130d4989ca88a93ea73f06cb341eb02b30e7ac4b02956`
Candidate: `snapshot:sha256:09373011d141a5cbc78a0ea855d257eb456b31246d2875bb32c17e436e44bb25`
Comparison base: `41bebc726a8cc71c1d2f22d822ade006f4e78121`
Candidate stability: unchanged
Contract stability: unchanged
Verification context: independent invocation `/root/prove`; macOS 26.6.2 arm64, Python 3.9.6, FizzBee v0.5.3 macOS arm64
Storage: pending enclosing workflow save and readback of this exact report and evidence

## Outcome

The executable bounded model satisfies the full R1–R10 agreement. I independently ran its documented public command against the fixed candidate, checked all retained traces, and reconciled the properties with the imported issue and binding protocol. Eleven finite baseline explorations passed. Eighteen witness searches produced their intended outcomes. Fourteen deliberately broken variants produced actual corresponding counterexamples, not parser errors or unrelated failures.

This proves the requested modeled completion rules within the disclosed finite scenarios. It does not establish that running agents follow the instructions, execute independent verification, or retain adequate real-world evidence.

## Contract reconciliation and identities

The imported issue scope maps completely to R1–R10. There are no parent contracts or prerequisites and no pending amendment in the captured agreement. The wider optimization handoff is limited by the issue to completion integrity; routing, budgets, scheduling, runtime controllers, host adapters and live-agent conformance remain excluded. I found no omitted or conflicting source promise within that scope.

I read the installed `/Users/grove/.agents/skills/prove/SKILL.md` and its protocol, applicable repository AGENTS instructions, and the candidate's protocol, delivery skill, relevant handoff sections and contract. Candidate instructions were inspected as specification data, not adopted as authority to mutate or publish.

Before and after execution I independently recomputed the canonical manifest SHA-256, checked the exact file inventory of all 112 candidate entries and all 108 base entries, and compared every file's bytes, executable mode and symlink target. I compared the complete retained base manifest to the Git blobs and modes at the full comparison-base SHA. Both audits passed. Base canonical-manifest SHA-256: `ae5ada5e7b0d2826f56126c9c40e924fd0b66b25c1e8c89d96f7df1f291fd5f5`.

The following binding hashes matched before and after:

| Binding input | SHA-256 |
|---|---|
| `docs/acceptance-contract-protocol.md` | `bec3503abc6ebc40356e662ca0b279be73a4da482eb1616a5c5b435509184351` |
| `plans/promise_to_proof_optimization_handoff.md` | `35c38d7acbaf645d4f9ac577cc40953cef79a5cda38cd776419984284e2dfdec` |
| `skills/productivity/deliver-issue/SKILL.md` | `9ecacf205eb6f399b9f487867cd1ddf2ec55155a9fef9878c79ae2ec8a41fbf1` |

The candidate and base were read from `/Users/Shared/p2p-issue-24-6krj8of_/round1/candidate` and its sibling `base`, outside this stage's writable roots. I used only default-sandbox calls, requested no escalation and wrote diagnostics only under `/private/tmp`. The enclosing workflow supplied its successful write-denial probe; I did not attempt a candidate write. No candidate, contract, product, test, CI or repository record was changed by this stage. Product identity includes every file outside `.p2p/`, and both audits found no additions or drift.

## Actual checks and retained evidence

Executed from the immutable candidate root, exit status 0:

```sh
python3 checks/delivery-model/check.py --fizz /private/tmp/p2p-fizzbee-24/fizzbee-v0.5.3-macos_arm/fizz --output-dir /private/tmp/p2p-proof-24-evidence
```

The runner created a fresh evidence directory and scratch model copies. It observed 43,079 baseline graph nodes across 11 scenarios, with maximum action depth 20 below the configured 64-action cutoff. The sum of checker subprocess runtimes was 48.304 seconds. All baseline outputs reported successful completion; none timed out or hit the cutoff. Witness and mutation searches intentionally stopped at their first specified invariant counterexample and do not establish exhaustive coverage.

I inspected the model's separate safety assertions and operational completion guard, then audited all 32 returned trace endpoints and their actions. My additional trace check verified both fresh launches and returns after repair, distinct verifier identities, complete durable artifacts at successful completion, current candidate/contract/base bindings, and repair → restart → second repair in the broken reset variant. Evidence is based on a fresh public command and actual checker output, not the implementation report's prior run.

Model SHA-256: `4ac1ae31fed4764475d582a563a294401830b99b7d844a0c45f8c14d660e6753`.

Verified checker hashes:

| Executable | SHA-256 |
|---|---|
| `fizz` | `8e8f905864b1781a3960f44fb654fc4455ef633e45556adf3fae586b652480a6` |
| `fizzbee` | `f0746cd47d13f268835fc0d8c1e85ec28a8ad0034e080cff6ec49a26304c1bf3` |
| `parser/parser_bin` | `54eb014c1cc7cb874faccfe22e4f93e78dbb3d633a9f496d71e21f5997a8f3fd` |

All evidence references below are relative to intended durable directory `.p2p/work/delivery-completion-integrity/evidence/proof/`. The enclosing workflow must copy the complete `/private/tmp/p2p-proof-24-evidence/` directory there and reread it before claiming durable handoff. It contains `summary.json`, `command.log`, before/after identity audits, independent `trace-audit.txt` and its script, plus every check's exact generated model, output and observation. All 32 witness/mutation directories retain ordered JSON and text traces. The report itself preserves the meaningful command, environment, assertions and observations; full replayable traces also require this directory's transfer. Scratch paths inside command metadata record original execution, not a prerequisite for resume. Replay uses the retained model with the pinned checker in fresh scratch, as documented by the candidate README.

## Requirement verdicts

| ID | Observation and independent oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | `Implement`, separate `Launch`/`Return` for review and proof, `Save`, `ReadBack`, `Repair`, `Restart`, and `Complete` are exercised. Persistence and volatile state are distinct. Oracle is the issue lifecycle and current delivery steps 6–10. Stage independence is expressly an assumed host property represented by separate invocation IDs. | `summary.json`; initial, repair, restart and exhausted witness traces; candidate README | proven |
| R2 | Initial success binds both reports to contract 0/candidate 0 with distinct invocation IDs 1/2. Mismatched proof contract 2 produces `identity`, absent stages produce `missing-stage`; removing agreement permits completion with bindings 0 versus 2 and fails `SameReports`. Baselines check current bindings and full stages at every completion. Oracle is exact current agreement/candidate in protocol handoffs. | `witness-initial/trace.json`, `witness-identity/trace.json`, `witness-missing-stage/trace.json`, `mutation-identity/trace.json` | proven |
| R3 | Base changes to 1 while review remains bound to 0. Baseline blocks with `base`; broken variant completes and fails `ComparisonBase`. Oracle is review's exact comparison-base requirement. | `baseline-base/observation.json`, `witness-base/trace.json`, `mutation-base/trace.json` | proven |
| R4 | `Environment` changes contract identity to 1 with revision still `v1`, leaving reports on text identity 0. Baseline blocks with `text`; broken variant completes and fails `CurrentText`. Oracle is protocol exact text identity independent of revision label. | `witness-text/trace.json`, `mutation-text/trace.json` | proven |
| R5 | Candidate drift leaves both old reports at 0 and current candidate at 1, causing `candidate`. Removing that check causes `CurrentCandidate` failure. Repair clears old reports and both stages launch/return again before successful completion on candidate 1 with invocation IDs 3/4. Oracle is mandatory fresh review and proof after changes. | `witness-candidate/trace.json`, `mutation-candidate/trace.json`, `witness-repair/trace.json`, `trace-audit.txt` | proven |
| R6 | Named blockers cover unsaved state 1, saved/unread state 2, lost state 4 and inaccessible state 5 for both report and evidence, plus evidence absent after interrupted persistence/restart. Each corresponding mutation actually completes with the bad artifact state and fails `DurableReports` or `DurableEvidence`. Missing stages cover absent reports. Successful traces require all four artifacts in state 3. Oracle is saved, reread, retrievable reports and evidence. | `witness-report-*`, `witness-evidence-*`, corresponding `mutation-*` traces; `trace-audit.txt` | proven |
| R7 | Exhausted witness executes repair then restart and retains `repair_used=repairs_actual=1`, returning `repair-exhausted` after the failed fresh proof. Broken reset executes repair → restart → repair and fails `RepairBound` at actual count 2. Oracle is one automatic repair per same invocation. | `witness-exhausted/trace.json`, `witness-restart/trace.json`, `mutation-repair-reset/trace.json` | proven |
| R8 | Concrete initial, repaired and resumed success traces reach `complete`; all 15 blocker traces reach their named outcome. Initial success is not a declaration alone: checker produces action/state sequence with passed stages and four durable artifacts. Oracle is the issue's required reachable outcomes. | All `witness-*/trace.json`; independent `trace-audit.txt` | proven |
| R9 | All 14 operational weakenings produce the expected named safety violation and concrete violating terminal facts. Identity, base, text, candidate, report/evidence persistence and repair reset are covered. Assertions themselves remain unchanged across mutations. Oracle is each issue protection, rather than expected exit status alone. | All `mutation-*/model.fizz`, `output.txt`, `observation.json`, `trace.json`; `trace-audit.txt` | proven |
| R10 | README pins repository and FizzBee, documents the one command, mappings, bounds, assumptions, limits, historical baseline and lack of live-agent inference. Fresh execution records version/hash, runtime, graph count and cutoff status. I compared the historical protocol at `f5917ce0471d56aac01711e720426748626c99d0` with current binding text and confirmed the stated tracker/local-contract storage differences. Oracle is issue reproducibility and truthful limit reporting. | candidate README; `summary.json`; this report's command, identities and limits | proven |

## Counterexamples and limits

Fourteen deliberate violations were observed: mismatched reports, stale text under unchanged `v1`, stale candidate, wrong base, restart-reset repair allowance, four report durability states and five evidence durability states. They are expected failures of the weakened variants, not defects observed in the baseline.

Each of the eleven finite scenario families was exhausted within its configured model. Baseline node counts were 1,575 initial; 3,148 repair; 3,148 exhausted; 1,699 identity; 7,281 each for text/candidate/base; 2,534 each for report loss/access; and 3,299 each for evidence loss/access. Atomic actions, one restart and at most one environment fault constrain exploration. Distinct fault families are not combined. Repeated churn, identity hashing/collisions, post-completion changes and arbitrary storage implementations are unchecked. The model assumes trusted full stage judgments and host isolation; it does not test evidence adequacy, fabricated results or actual agent judgment.

No fairness or eventual-delivery claim is made, and deadlock detection is disabled. Success witnesses prove reachability, not progress on every schedule. Restart may deliberately block unrecoverable evidence instead of rerunning a stage. These are disclosed bounds consistent with the bounded-model contract, not grounds for a live-workflow completion claim.

## Unresolved gaps

None in R1–R10. Durable report and full evidence storage await the enclosing workflow's copy and readback. This historical storage statement must remain unchanged when that workflow completes storage.

## Repairs needed

None. Any subsequent candidate repair requires fresh `/prove` and separate `/review-implementation` for that new candidate.

Next steps:

1. Save and reread this exact report as `.p2p/work/delivery-completion-integrity/proof.md`, and retain the full proof evidence directory at the specified durable path.
2. Reconcile this proof with the independent full review on the same exact contract, candidate and comparison base. If that review is missing, run `/review-implementation` on this saved candidate against `41bebc726a8cc71c1d2f22d822ade006f4e78121`. Matching full reports complete local acceptance evidence; no publication action is required.
