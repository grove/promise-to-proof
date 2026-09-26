# REVIEWED: delivery completion integrity, issue #24 / PR #25

Contract: `work/delivery-completion-integrity.md`, revision v1, SHA-256 `7cfbf6558846415b06b130d4989ca88a93ea73f06cb341eb02b30e7ac4b02956`.
Candidate: `snapshot:sha256:be7ea1690adb91888d089ab36aa2a70f0069bb7c258e9d21bd22db9f7851ad98`.
Recoverable content: `/Users/Shared/p2p-issue-24-6krj8of_/refresh25-main69/records/candidate.json`, with the complete 112-path manifest and materialized sibling `candidate/`.
Comparison: fixed base commit `69c02fe5a0e876b104baacca2e4075f801974d40`; full 108-path base tree retained in sibling `base/` and `records/base.json`. Its reconstructed manifest identity is `snapshot:sha256:2f82a8cb8b1ca472db38aa87dfdbddb19bace52b846cc40eb8bfc3077b720453`.
Stability: complete candidate and base inventories, bytes, executable modes, symlink targets, contract hash, and binding hashes checked before and after inspection; unchanged. The base manifest also matches every path, mode, and blob in the named Git commit outside `.p2p/`.
Coverage: whole contract, R1–R10. No parent, prerequisites, or excluded requirement subset.

Actual stage invocation: `collaboration.followup_task` to independent review host agent `/root/review25_refresh`, applying installed `/Users/grove/.agents/skills/review-implementation/SKILL.md`. This stage read its protocol reference, the candidate protocol, contract, binding sources, repository instructions, and complete added implementation. Default workspace-write sandbox permits writes in the assigned workspace and temporary roots; `/Users/Shared/` candidate, base, and agreement inputs are outside its writable roots. No escalation, delegation, product edits, Git writes, or remote effects were used. All diagnostic/report writes were under `/private/tmp/`; Python bytecode writes were disabled for imports from the candidate.

## Contract fidelity

No material findings.

The scope over the new base consists of exactly four added files: `checks/delivery-model/README.md`, `checks/delivery-model/check.py`, `checks/delivery-model/delivery.fizz`, and the canonical contract. The roadmap already belongs to this comparison base. The new base adds only changes to `skills/productivity/publish-pr/SKILL.md` and `checks/publish-pr-scenarios.md` relative to `5a98bbcbeed9bbddce40d1b8158e0592bb10d13f`. I inspected their full diff, retained as `base-change.diff`. They require complete publication records, distinguish later receipts, authorize records-only follow-ups separately, and constrain cleanup to verified published copies. Those publication and cleanup operations are outside this model's explicit scope; they neither modify its execution inputs nor change the completion-integrity contract. Both changed files are identical between this candidate and its new base.

I compared the complete previous and current candidate manifests. Only those two publication files changed; all 110 other paths, including the model, runner, README, contract, binding sources, and repository instructions, remain byte/mode identical. `previous-candidate-comparison.json` retains that check. I carried forward my earlier source/code inspections of those unchanged bytes, reread the model transitions, and evaluated every R1–R10 obligation and all three review axes against the new base. The source reconciliation still records the earlier base; I use it only for its unchanged-source reconciliation, not as a current comparison identity. No new contract promise follows from the publication changes. This report is a refreshed review conclusion, not reuse of the old report or its candidate identity. All four execution observations below were generated again on this new candidate.

| Requirement | Implementation examined and review observation |
|---|---|
| R1 | `Implement`, `Launch`, `Return`, separate `Save`/`ReadBack`, `Repair`, `Restart`, and `Complete` model the lifecycle. Distinct verifier IDs represent independence, with trusted host isolation explicitly disclosed as an assumption. |
| R2 | `Complete` checks both report bindings and the current inputs; separate `SameReports`, `CurrentText`, `CurrentCandidate`, and `IndependentFullStages` assertions constrain claimed completion. Missing stages cannot complete. |
| R3 | Review binding captures base at launch; completion and `ComparisonBase` require the current base. The base scenario can drift while verification is running or after return. |
| R4 | `Environment` changes text identity while revision stays v1. The text mutation removes the operational guard while retaining `CurrentText`; my fresh trace reaches precisely that violation. |
| R5 | Candidate drift checks current bindings; `Repair` increments candidate and clears both stage results and their bindings. My repair/restart witness returns both new verifications bound to candidate 1, invocation IDs 3 and 4. |
| R6 | Separate artifact states distinguish volatile, saved, reread, lost, and inaccessible content for both reports and evidence. Restart discards unsaved evidence and readback knowledge. Fresh evidence-absent mutation completes with reports `[3,3]` but evidence `[0,0]`, triggering `DurableEvidence`. |
| R7 | Durable `repair_used` survives normal restart; independent `repairs_actual` detects allowance reset. My mutation trace reaches two repairs after restart and fails `RepairBound`. |
| R8 | Named witnesses query reachable completion and specific blockers rather than merely declaring success. The fresh successful repair/restart witness completes with both reports and evidence reread and current. All witness definitions and terminal-state checks were inspected. |
| R9 | Fourteen mutations cover the selected protections. The runner demands the named invariant and concrete terminal violation, retains the substituted model and ordered trace, and rejects wrong assertions or parse failures. Three representative mutations were rerun here; the complete mutation suite belongs to fresh proof. |
| R10 | README and runner pin FizzBee v0.5.3 binaries and modeled repository revision `41bebc726a8cc71c1d2f22d822ade006f4e78121`. They state the command, platform, finite scenario bounds, timeout/cutoff rejection, observations, lack of fairness guarantee, and unchecked agent behavior. Current protocol and delivery skill bytes match that modeled revision; the older protocol contains the documented `docs/acceptance-contracts/` location. |

## Scope and simplicity

No material findings. The implementation adds one finite model, one standard-library runner, and maintainer documentation. Scenario substitution happens in scratch files. It adds no dependencies, runtime controller, host adapter, publication effects, workflow changes, or broader roadmap implementation. The narrow macOS arm64 binary pin and single-fault scenario families are explicit limits allowed by the contract.

## Engineering quality

No material findings. I inspected the whole runner, model transitions, safety assertions, mutation and witness inventories, trace checks, timeout handling, binary pins, output-directory creation, and cutoff accounting. The runner checks FizzBee verdict text because its wrapper can return zero on an invariant failure; an unrelated failure cannot satisfy a mutation. Existing evidence directories are not overwritten. Safety assertions remain independent of mutation switches. Report absence is constrained by lifecycle state reset, while content loss and interrupted saving have explicit cases.

## Checks and limitations

Evidence root for this invocation: `/private/tmp/p2p-review25-main69-evidence/`. Retain this directory as `.p2p/work/delivery-completion-integrity/evidence/review-main69/`.

- `validate.py`, `identity-before.json`, and `identity-after.json` record full manifest and binding validation. Before/after outputs compare equal.
- `diagnostic.py` used the read-only Git object store at `/var/folders/vq/593qxcm57l90w1dlpywl_7nw0000gn/T/p2p-refresh-25-ktwpyoq5/repo` and independently compared the retained base with `git ls-tree` and blob content from the fixed base commit, then imported the candidate runner without bytecode writes. It invoked four focused FizzBee checks through the runner's `run` function. Command: `PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/p2p-review25-main69-evidence/diagnostic.py`.
- Executable: `/private/tmp/p2p-fizzbee-24/fizzbee-v0.5.3-macos_arm/fizz`. All three executable hashes matched the runner's pins before execution. `diagnostics.json` retains environment, exact commands, times, substituted model hashes, and observations. Each check directory retains its output, model, observation, and complete trace.
- `witness-restart`: `Witness` counterexample, successful completion after one repair and restart; candidate 1, current bindings, reports and evidence `[3,3]`; 1.31 seconds.
- `mutation-repair-reset`: `RepairBound` counterexample with `repairs_actual=2`, `repair_used=1`, and `restarted=true`; 0.92 seconds.
- `mutation-evidence-absent`: `DurableEvidence` counterexample with claimed completion and absent evidence after restart; 0.76 seconds.
- `mutation-text`: `CurrentText` counterexample with claimed completion, current text identity 1, both report text identities 0, and revision v1; 2.41 seconds.

This review did not rerun the full 43-check acceptance command or duplicate exhaustive baseline exploration. The four searches intentionally stop at their first expected counterexample. Remaining requirements were reviewed through their implementation, source obligations, and runner checks, not declared proven. Fresh full proof is a separate stage. Earlier static observations are retained only where full byte/mode equivalence was established above. No old review, proof, implementation report, or roadmap status was used to establish fresh execution. This model cannot establish real-agent conformance, actual host isolation, evidence adequacy, or eventual success on every schedule.

Exact live binding hashes, checked before and after:

| Binding input | SHA-256 |
|---|---|
| `docs/acceptance-contract-protocol.md` | `bec3503abc6ebc40356e662ca0b279be73a4da482eb1616a5c5b435509184351` |
| `plans/promise_to_proof_optimization_handoff.md` | `c09ae44b02d167ae136cf173f3c8611115e4ee0eaeb295dcf2b9269e36b9a928` |
| `skills/productivity/deliver-issue/SKILL.md` | `9ecacf205eb6f399b9f487867cd1ddf2ec55155a9fef9878c79ae2ec8a41fbf1` |

## Handoff

No change-required findings or decision-blocking unknowns for R1–R10. This report makes a fresh review conclusion for the stated snapshot and updated base. It grants neither acceptance nor merge approval.

Report storage: exact report saved and reread at `/private/tmp/p2p-review25-main69.md`; canonical storage at `.p2p/work/delivery-completion-integrity/review.md` and evidence transfer remain pending in the enclosing workflow. Preserve prior records before replacement. Retain the recoverable candidate/base manifests and host invocation records alongside this handoff.

Review only; acceptance proof and merge readiness are separate.

## Next steps

1. Save and reread this exact report and its evidence under the canonical work-item directory, retaining the prior report history and actual `/root/review25_refresh` invocation record.
2. Complete `/prove work/delivery-completion-integrity.md; candidate snapshot:sha256:be7ea1690adb91888d089ab36aa2a70f0069bb7c258e9d21bd22db9f7851ad98` in the separate fresh proof context. Compare all contract, candidate, binding, base, and coverage identities before claiming matching acceptance evidence.
3. When PR #25 approaches a merge decision, use `/merge-readiness https://github.com/grove/promise-to-proof/pull/25; review .p2p/work/delivery-completion-integrity/review.md; proof .p2p/work/delivery-completion-integrity/proof.md` after that proof is saved. This review does not assess current PR gates or authorize merging.
