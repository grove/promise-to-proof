# NOT PROVEN: Independent, grouped, and mixed epic delivery

Requirements: 16/30 proven; 3 disproven; 11 not proven.
Counterexamples tested: 12 scenario-boundary categories plus complete identity and retention checks, detailed below.
Contract: `work/epic-delivery-strategy.md v1`.
Contract snapshot: SHA-256 `78cad1d7f85183100214da15fdc8418ed2220ce1af80764d648e139fdd899895`, exact recoverable bytes in the candidate manifest.
Binding source: `plans/epic-delivery-strategy-spec.md`, SHA-256 `7a231d84f739a459f770870d23038fbc4946c759f04241c87f2a6322d9a1645e`.
Candidate: `snapshot:sha256:8ff16e4594d451c80b5c1cb7225874bb89b4190a6448dba86ee146e025ab0dd8`.
Comparison base: `5e369c1b45ba817b8add6b20a9b7b1c97898fa12`.
Candidate stability: unchanged. All 130 paths, bytes, executable modes and symlink targets rechecked against the recoverable manifest before and after verification.
Contract and binding-source stability: unchanged; exact hashes rechecked.
Verifier: actual agent context `/root/prove_epic_delivery`. No subagents spawned. Model identifier was not separately exposed.
Verification context: macOS 26.6.2, build 25G83, arm64; Python 3.14.7 at `/opt/homebrew/bin/python3.14`; Git 2.54.0, Apple Git-157. Default sandbox only, no escalation. Bytecode disabled. Diagnostics and disposable Git repositories were written only under `/private/tmp`. No real GitHub, network, credential, publication or merge operation occurred.

## Outcome and contract reconciliation

The candidate implements much of the routing and strategy workflow, but does not establish the complete approved capability. Actual controller transfer loses an accepted approval receipt, and actual installed-skill publication/readiness records sometimes identify normalized plan text instead of its exact bytes. Several expressly planned scenario observations are also missing or inconclusive.

The source and R1–R30 reconcile without a material omitted source promise. The protected planning receipt records the exact contract approval, “Approve v1; deliver without slicing,” against the contract hash above. This overrides the slicing handoff for this delivery only. It does not narrow any requirement or authorize external effects. The contract's historical pending-approval wording does not override that later explicit receipt. There is no parent agreement for this implementation work item. No amendment was supplied in this proof stage.

I read the installed prove skill, its protocol, the frozen source and contract, applicable repository instructions, changed workflow instructions, scenario procedure, actual fixture records, and complete candidate/base inventories. I did not use the implementation author's claimed result or the separate implementation-review verdict as proof.

## Evidence references

Paths below are relative to `.p2p/work/epic-delivery-strategy/` when the enclosing workflow retains this report.

- **E1, identity and boundary:** this report's Identity and stability section; `candidate.json`, `evidence/comparison-base-manifest.json`, and `planning-handoff.md`.
- **E2, initial public invocations:** `evidence/scenarios/<case>/`, including actor requests, installed-file hashes in `oracle.json`, actual command evidence, stage reports, tracker logs/state, and recoverable `fixture.bundle`.
- **E3, supplemental public invocations:** `evidence/supplement-first/<case>/`, including `retention.json`, `supplement-fixture.bundle`, command evidence, exact reports, plan history, grants and tracker logs. Cases include S4, legacy S4, S7/S8 activation, S9 retarget/retry/races, S10 and publication/readiness gates for S1/S11/S12.
- **E4, authorized setup:** `evidence/supplement-setup/S13-missing/`, including the exact grant, setup script, command/readback evidence and `supplement-fixture.bundle`. `evidence/supplement-notes/human-notes.txt` retains S7's untracked human edit.
- **E5, independent executable checks:** the commands, assertions and results in this report's Independent observations section. Diagnostic scripts and logs were returned separately for selective retention; the observations and reproduction steps here do not require those temporary directories to survive.
- **E6, documentary outcomes:** `README.md`, `docs/how-to.md`, `docs/faq.md`, the canonical protocol and its 17 shipped copies in this exact candidate.

All 307 initial retention entries, 336 first-supplement entries and 30 setup entries matched their recorded hashes. S7's separately retained human note matched its original oracle hash. Supplemental Git bundles were recovered into fresh scratch checkouts; all six contract/source files per S4, legacy S4, S7, S8, S9 and S10 fixture matched their original oracle hashes. All 12 supplemental packages' installed skill, reference and filesystem-helper hashes matched the frozen candidate. Initial S11/S12 packages differ only in the unused delivery-controller script; their invoked prove skill, protocol and filesystem helper match. Bytecode files were excluded from source-file comparison.

## Requirement verdicts

| ID | Observation and independent oracle | Evidence | Verdict |
|---|---|---|---|
| R1 | S1/S2/S3 outputs use the stated acceptable outcomes and configured `trunk`; S14 respects the existing flag. The expressly planned ambiguous-intent question and release-timing boundary were not executed. | E2 S1/S2/S3/S14; G3 | not proven |
| R2 | Saved independent, grouped and mixed tables resolve one destination per child using `trunk`, one optional integration branch, a default and exceptions. Actual controller tests reject inconsistent rows and use the named target. | E2 S1/S2/S3; E5 controller checks | proven |
| R3 | S5 pending v2 leaves approved v1 active. S7/S8 activation preserves prior full plan bytes, exact approval receipts, revisions, parent completion and pending effects. Recomputed active hashes match saved sections. | E2 S5-pending; E3 S7/S8 history and activation | proven |
| R4 | The public controller accepts a plan naming an existing local `approval.md`, then transfers the approved plan without that receipt. The required approval evidence does not travel. S4 inspection alone also does not establish the prescribed transferred fresh-session restart. | E5 C1; E3 S4; G1/G3 | disproven |
| R5 | Unsliced `work/solo.md` needs no plan. Installed implementation inspection, full solo verification, publication inspection and read-only readiness preserve the ordinary workflow. The existing solo PR is READY under supplied gates without inventing an epic dependency. | E2 S1; E3 S1 gate reports/logs | proven |
| R6 | Legacy routing was normalized without another strategy question and its original bytes/approval were retained. No fresh restart after transfer of that normalized decision was executed, as explicitly planned for this row. | E3 S4-legacy; G3 | not proven |
| R7 | Missing, conflicting and proposed-only plans block without selecting a default; pending v2 retains v1. Actual logs/ref inventories show no dependent effects, and controller cases reject the same states before dispatch. | E2 all S5 variants; E5 | proven |
| R8 | Closed issue 101 does not overcome a failing actual capture prerequisite. The supplied-behavior variant checks capture and changes to an implementation handoff. Independent bundle replays reproduce the failing/passing prerequisite. | E2 S14 absent/present; E5 | proven |
| R9 | Direct implementation states destination and exact target tip. Delivery inspection rejects missing/conflicting refs and names the advanced tip. Production controller tests select the intended target tree and exclude unrelated committed sibling payload while preserving the source checkout. | E2 S13/S14; E3 S4; E5 | proven |
| R10 | Actual S9 full child review records the intended target's full SHA and inherited agreement. S10/S13 advancement inspections reject historical bases and require fresh full review at the observed tip. No stale report is presented as current. | E3 S9 verification and S10; E2 S13-advanced | proven |
| R11 | S9 discovers an omitted target and produces a concrete retarget preview; S6 blocks expected `epic/example` versus requested `trunk` with zero writes. New grouped/mixed child publication with the required destination in its complete PR description was not exercised. Base-only retargeting preserves the existing body and does not supply that missing observation. | E2 S6; E3 S9; G3 | not proven |
| R12 | Actual PR target mismatch produces BLOCKED with expected/actual targets and no silent retarget. Later readiness checks actual `epic/example` and separately blocks pending CI. READY remains advice and no merge occurs. | E2 S6 tracker log; E3 S9/S1 gate records | proven |
| R13 | Earlier retarget records retain the correct exact section identity, but later S9 readiness and S12 publication records use hashes of trimmed-and-renewlined text. Their claimed exact plan hashes do not identify the approved section bytes. | E5 C2; E3 gate reports | disproven |
| R14 | Missing/conflicting/advanced branches yield exact setup or refresh handoffs and preserve conflicts. Under a concrete later grant, the missing local and bare-origin refs appear at the approved full SHA and two actual readbacks confirm them; repeat inspection does not recreate or overwrite them. Original first-run raw output loss limits the action-log completeness, but retained initial absence, script, grant, subsequent state and readbacks establish the setup outcome. | E2 S13 variants; E4 | proven |
| R15 | Missing verification is not bypassed, and pending unrelated CI blocks readiness while publication inspection remains available. The explicitly planned incomplete-child and approved shared-candidate exception variants were not run. | E2 S2; E3 S9 gates; G3 | not proven |
| R16 | S7/S8 previews name old/new destinations, affected children, preserved work, exact PR actions and required verification. The explicit unknown-remote-state variant and actual continuation of unaffected work were not observed. | E3 S7/S8/S10; G3 | not proven |
| R17 | Exact strategy-only activation retains contracts, child identities/dependency links, existing candidate records, original plan/approval history and the original S7 human note. PR17 and refs remain unchanged; prerequisites, scope and outstanding verification/actions are stated. | E3 S7 activation and command evidence; E4 human note | proven |
| R18 | S8's actual Git candidate contains `UNFINISHED_SIBLING_DO_NOT_SHIP`; the strategy actor preserves it and requires extraction and fresh verification. The required clean scoped-candidate positive path and publication inspection were not performed. | E3 S8; independent bundle inspection; G3 | not proven |
| R19 | S7 retains capture as landed on `trunk` at the confirmed fixture commit. Only lookup/summary change routing; activation does not rewrite the landed history. | E3 S7 original plan, proposal, active v2 and preserved Git | proven |
| R20 | Strategy-only S7/S8 approvals change records without ref/PR effects. S13 uses separate exact ref authority. S9 performs only the granted base edit, and a fresh retry reuses the unchanged grant/effect without another question or write. No merge authority is inferred. | E3 S7/S8/S9 grants and logs; E4 | proven |
| R21 | A separate publisher checks actual full review/proof and exact new-target identities, previews one PR17 base edit, receives exact authority, sends that edit only, and reads back target and preserved fields after a lost response. Independent log assertions find one base-only edit, unchanged human body/marker, one PR, and later target readback. | E3 S9 preview/grant/execution/readback; E5 | proven |
| R22 | Lost-response readback and fresh retry avoid a duplicate; stale plan and concurrent human-body changes block with zero writes. `S9-after-effect` actually injected ambiguity before any edit. It does not test interruption or plan change after a confirmed effect, as explicitly required. | E3 S9 variants and actual sequence log; G3 | not proven |
| R23 | Destination-only activation leaves acceptance bytes unchanged; S10 correctly describes base-only refresh. Actual changed/rebased-candidate and changed-product-promise variants were not run, so the complete distinction is not established. | E3 S7/S8/S10; G3 | not proven |
| R24 | S12 checks all contributions and composition on one exact candidate. S11 correctly fails parent proof, but its `capture('Ada')` also violates the child's own contract. Passing weak child checks do not make the children complete. The mandatory parent-only failing-interaction boundary is therefore not established. | E2 S11/S12; E3 S12 review; E5 literal replay; G2 | not proven |
| R25 | S11 blocks parent publication/readiness without matching full parent reports, despite green simulated CI/approval. Child pending-CI behavior is observed. Final-parent readiness with a matching parent report pair but missing required CI or repository approval was not exercised, so the entire final-target gate is not independently demonstrated. | E3 S11/S9 gates; G3 | not proven |
| R26 | S12's exact `trunk` candidate passes full parent proof and later full parent review. Publication explicitly proposes no empty parent/integration PR; tracker logs contain no creation. | E2/E3 S12; E5 replay | proven |
| R27 | All 17 protocol copies match and affected skills consistently state the routing rules. Nevertheless the actual controller receipt loss and exact-plan-identity failure violate the shared retention/identity safeguards. Required behavioral coverage is incomplete. | E1/E5 C1/C2; E6; G1/G3 | disproven |
| R28 | README's slicing entry links to the real mixed-destination walkthrough. It covers mixed routing, an open-PR strategy change, extraction/verification, exact retarget approval and final parent verification, with named destinations and next actions. Documentary outcome established; unexecuted behavioral steps remain covered by their specific rows and R30. | E6; compared with S3/S7/S8/S12 observations | proven |
| R29 | FAQ expressly distinguishes child completion, integration and full parent acceptance; it separates CI/repository approval and merge authority. Its statements agree with the actual child, failed-parent and combined-parent observations. | E6; E2/E3 S2/S11/S12 | proven |
| R30 | Every S ID has some retained execution, but several required variants are absent, S11 does not isolate its promised boundary, and S9's named after-effect case is a before-effect race. Controlled mutation success and rejected stale writes are real, but those partial results cannot establish the full scenario contract. | E2/E3/E4; G2/G3 | not proven |

## Independent observations

The 12 boundary categories examined were missing/conflicting/proposed routing; pending proposal versus active approval; absent/present actual prerequisite despite closed status; missing/conflicting/advanced integration refs; unrelated starting-tree payload; lost-response retarget and retry; stale-plan preview; concurrent PR-body edit; integrated sibling contamination; parent composition versus child checks; approval-receipt transfer; and exact plan bytes versus normalized identity.

### C1: accepted receipt is omitted from actual controller transfer

In a disposable Git repo, create valid parent and child contracts, `trunk`, an `epic/greeting` branch, and an approved plan in the documented format. Put the actual approval in `.p2p/work/parent/approval.md`. Its plan field is:

```text
Approval source: Fixture owner approved v1 in the retained receipt approval.md.
```

Invoke the frozen candidate's actual public controller:

```text
/opt/homebrew/bin/python3.14 -B skills/productivity/deliver-issue/scripts/p2p_delivery.py --repo <fixture> run work/child.md --comparison-base <full-target-SHA> --authorize-local --max-dispatches 0
```

Observed target SHA: `36ea472983748b1345a7cc65196b1e2a2676b4cd`.
Observed command exit: 1, with `dispatch-count limit exhausted before preflight-1` and zero attempts. This deliberate limit prevents any actor dispatch while executing real admission and materialization.

Independent filesystem assertions after admission:

```text
source approval.md exists: True
runtime/workspace/.p2p/work/parent/slicing.md exists: True
runtime/workspace/.p2p/work/parent/approval.md exists: False
```

The plan is accepted and copied while its actual receipt is missing. `routing_records` follows Markdown links and the special `planning-handoff.md` name, but not this accepted plain local receipt reference. The same omission was independently reproduced with the retained S3 plan using production routing/transfer functions. No candidate repair occurred.

### C2: exact approved section hashes are changed by trimming

The protocol defines the section as its heading through the byte immediately before the next level-two heading or EOF. I extracted its bytes without normalization:

```python
section = re.findall(rb'^## Approved delivery plan\r?\n.*?(?=^## |\Z)', data, re.M | re.S)
assert len(section) == 1
expected = hashlib.sha256(section[0]).hexdigest()
```

Actual S9 approved section:
`b86ffd9b9b6ccbd0615efbcc57d3da023e1a8a0c185303a28832aafc0490ffe2`.

Latest S9 readiness report instead records:
`b67b46a4cba48649504916d2b2e873fdc0fc642d0f7fdfa7a32b41fd27cf79cd`.

Actual S12 approved section:
`6ddc21b5453e16b607299bb1789e3ad93a137c9442ddb373b1665302d16e25f5`.

Latest S12 publication report instead records:
`39b3fe1ae2b4f26df4b9e1eed5e4741e151b23a2b8424ff0aa4e404a1bc6b6eb`.

Both reported values equal `sha256(section.rstrip() + b'\n')`. The canonical plan did not change. Earlier S9 publisher/retry records retain the correct value, so this is an observed later workflow failure, not a different approved plan. Preserve the failed records as history; manually substituting hashes would not prove the skill behaves correctly.

### Executable and mutation checks

- Ran `PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.14 -B -m unittest discover -s checks -p 'test_*.py'` in the protected candidate. Result: 29 tests passed in 141.448 seconds; filesystem checks passed. Controller tests execute real routing, materialization and persistence with explicitly simulated workers. They do not establish real agent behavior or live host isolation.
- Ran the candidate fixture's `self-check`. It passed persisted edit, lost response, readback, effect-count and concurrent-change assertions. This establishes the tracker simulator, not the publisher's behavior.
- Recovered S11/S12/S14 fixture Git bundles in new scratch checkouts. S11's three supplied child checks exit 0, parent exits 1, and the independent literal assertion `capture('Ada') == {'ada': 'Ada'}` also fails. S12 all four supplied checks and independent original-case/composition assertions pass. S14 absent capture and parent checks fail; the supplied-behavior variant passes all four.
- Recovered S9's supplemental bundle and independently executed capture, lookup and parent checks. All pass on `c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f`.
- Parsed actual S9 tracker events. Exactly one effect is `{'edit':'17','changes':{'baseRefName':'epic/example'}}`, at sequence 10, returning exit 1 after persistence. A later successful read shows `epic/example`. Final body equals the exact preview's original human body; one PR remains. Fresh retry adds no effect. Stale-plan, concurrent-body and the misnamed after-effect cases contain zero effects.
- Recomputed S7/S8 approved-section hashes and checked retained history/approval records. S7's human note matches its initial SHA-256 `406db673b27baa14dd56db5770cc5e7752ee45d796f213f64b42ce85c13641a6`. S8's recovered Git tree still contains the recognizable unfinished sibling file.
- Verified S13's retained supplemental bundle contains local and remote-tracking `epic/example` at `99faa2ff62394a0d48d13f45d29a5edffb1f8069`. Two retained actual local/bare-origin readbacks agree. The setup actor honestly reports that raw first-run output was lost on a later script exception. Its script, first-stage report and subsequent readbacks are retained; a complete original action transcript cannot be claimed.

## Identity and stability

The harmless sibling creation probe outside the writable roots failed with `PermissionError: [Errno 1] Operation not permitted` at `/private/var/tmp/p2p-issue33-verifier-8eh45dgs/prove-harmless-boundary-probe`. It created nothing. Candidate/base trees were outside writable roots; no escalation was requested.

I reconstructed the candidate manifest's canonical JSON digest and independently compared all file inventories, bytes, executable modes and symlink targets. The 127-entry base manifest also matches the repository's actual `git ls-tree -rz 5e369c1b45ba817b8add6b20a9b7b1c97898fa12` blob hashes and modes outside `.p2p/`; the full Git tree is `a9f5312ae61f62db2e16b65af369cee390036cb7`. Thus base identity is supported by Git objects, not only a named manifest.

All 17 resolved protocol copies equal the canonical bytes, SHA-256 `c916e48be9de29f423716518dc290a64b9c667bdf42b40da87dc346853957b43`. Final complete-tree, contract and binding-source checks returned the exact original identities. Generated observations and retained scenario updates are outside the fixed product candidate.

## Unresolved gaps and repairs needed

**G1, concrete product/workflow failures, R4/R13/R27.** Make every approval receipt accepted by the routing consumer recoverable in the isolated/transferred workspace. Safely normalize or retain valid existing references while preserving their original approval and history; do not require another strategy decision. Add a public-command regression asserting the receipt exists after transfer and fresh child-path recovery. Make publication/readiness compute and retain the exact approved section bytes, including trailing separators, without `strip`, `rstrip`, newline replacement or Unicode normalization. Use the shared exact extraction rule and actual rerun observations. Preserve current failed records as history.

**G2, defective required scenario, R24/R30.** Replace S11's child-contract violation with a genuine parent-owned interaction failure while every child's full actual contract still passes. Run fresh child verification as appropriate, then full parent proof and publication/readiness. Expected result: child success cannot overcome the actual failed parent interaction. Retain literal independent assertions; uppercase-only child checks are insufficient.

**G3, mandatory missing observations from the approved rows/evidence procedure.** These are expressly planned checks, not extra optional testing:

- R1/R30: ambiguous acceptable-intermediate-outcome question and distinction between release timing and merge acceptability.
- R4/R6/R30: transfer durable plan/history/approval records, remove scratch dependence, then use a fresh actor given only the child path; repeat after legacy normalization. Existing S4 actors inspect original case directories and do not establish that restart procedure.
- R11/R30: actual grouped/mixed child publication preview with omitted target and the required destination/plan identity in the complete proposed PR description.
- R15/R30: incomplete child and explicitly approved shared-candidate exception variants. Pending unrelated CI has already been observed and need not be relabeled unexecuted.
- R16/R30: unknown PR/remote-state preview and continuation of unaffected child work under the applicable approved routing.
- R18/R30: a correctly scoped independent candidate after extraction of integrated work, with intended prerequisites and full applicable verification against the final destination. Preserve the contaminated candidate and integration history as the negative case.
- R22/R30: interrupt after a confirmed effect and resume in a fresh context; also make a genuine plan/PR change after an effect during application. Assert confirmed effects, outstanding actions and total effect counts. The existing S9-after-effect case has no prior effect and cannot substitute.
- R23/R30: actual base-only, changed/rebased candidate, and changed-product-promise variants, with exact before/after contract/candidate/base identities and the distinct owning-stage handoffs. S10's prospective instructions alone do not establish all three.
- R25/R30: final-parent required-CI and repository-approval gate observations with otherwise matching full parent reports, so missing parent proof does not mask those gates.
- R30: retain a complete action record for authorized setup on a fresh fixture, including successful commands and rejected/reused operations. Current ref outcomes are established, but original first-run output is lost. Keep the tracker explicitly simulated and live-service validation explicitly unexecuted.

No additional optional stress tests are required by this report. Live GitHub validation remains unexecuted under the supplied authority; controlled tracker coverage is the required available seam. The installed copied delivery controller's import failure in S13 is retained as a fixture/package execution limitation, not silently counted as a completed controller run. Setup was performed through the actual installed skill instructions, and the independent public-controller counterexample used the complete frozen repository.

Fresh full proof is required after any product repair. Refresh implementation review separately for the changed candidate. This report establishes neither acceptance nor publication/merge readiness.

Next steps:

1. `/repair-gaps .p2p/work/epic-delivery-strategy/proof.md` for G1, G2 and the specific mandatory G3 evidence gaps; preserve the approved contract and current failed evidence.
2. Capture the repaired exact candidate and rerun full independent `/review-implementation` and `/prove` for R1–R30 against the recorded full comparison base.
