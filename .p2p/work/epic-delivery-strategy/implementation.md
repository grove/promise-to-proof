# IMPLEMENTED: Independent, grouped, and mixed epic delivery scoped repair

Contract: `work/epic-delivery-strategy.md` v1, SHA-256 `78cad1d7f85183100214da15fdc8418ed2220ce1af80764d648e139fdd899895`. Byte-identical to the approved agreement.
Binding source: `plans/epic-delivery-strategy-spec.md`, SHA-256 `7a231d84f739a459f770870d23038fbc4946c759f04241c87f2a6322d9a1645e`.
Scope: saved review F1/F2 and matching proof G1/G2, plus the requested G3 deterministic post-edit fixture support. Evidence-only completion incorporates the enclosing workflow's now-retained G1/G2/G3 observations; no additional product edit, test run, or repair cycle occurred.
Candidate before: `snapshot:sha256:8ff16e4594d451c80b5c1cb7225874bb89b4190a6448dba86ee146e025ab0dd8`.
Candidate after: `snapshot:sha256:7e5c54fa4183651c94b4f6b83bea7cc841b2722a5693047c5c8be8faaf8f41e8`; complete recoverable manifest in `candidate.json`.
Review base: `5e369c1b45ba817b8add6b20a9b7b1c97898fa12`.
Repository: `/Users/grove/projects/promise-to-proof2`, branch `main`, starting HEAD `5e369c1b45ba817b8add6b20a9b7b1c97898fa12`. Existing first-candidate changes preserved; no project Git write, commit, publication or external effect.

The installed implement-contract and repair-gaps skills were read and applied together. Installed filesystem validation succeeded before edits against the exact first candidate, agreement, binding source and full comparison base. The enclosing workflow reserved repair cycle 1 in `evidence/repair-cycle.json`. No second cycle was opened.

## Changes

Bare local `.md` receipt references on `Approval source:` now follow the same retention path as Markdown links. Plan and historical approval bytes stay intact. Initial admission rejects a missing receipt; retained hashes detect changed or missing receipts before resume dispatch. The shipped fixture now emits an explicit Markdown link.

The protocol includes the exact byte extraction already used by routing. Publication and readiness explicitly use that extraction and read back retained section bytes and hash. The rule preserves separators, CRLF, trailing spaces and EOF. All 17 shipped protocol references resolve to canonical SHA-256 `209562cadbad5a945998fe1fb370ffab5ab4ea648fc4ac720888c2d3a3ca634d`.

S11 keeps all child functions, child contracts, and complete child assertions intact. A parent-owned `greet` wrapper supplies an uppercased argument to capture. Direct capture/lookup/summary retain Ada; the parent workflow returns Welcome ADA and fails its original-case promise. The original direct composition assertion also remains.

The tracker supports one-shot `after_edit` injection after a real edit has been written to tracker state. `plan_text` supplies an exact complete revised plan; the evaluator retains its approval/history before arming it. Events distinguish `after_persisted_edit` from call-number races. This is fixture behavior, not a canned actor result. Scenario instructions avoid the flattened copied controller layout; public controller coverage uses the complete repository with its required bundle checker.

Changed files:
- `checks/epic-delivery-scenarios.md`
- `checks/epic_delivery_fixture.py`
- `checks/test_p2p_delivery.py`
- `docs/acceptance-contract-protocol.md`
- `skills/productivity/deliver-issue/scripts/p2p_delivery.py`
- `skills/productivity/merge-readiness/SKILL.md`
- `skills/productivity/publish-pr/SKILL.md`

## Requirement handoff

This table closes development implementation/evidence handoff for the selected repair scope. It does not issue requirement acceptance verdicts. Paths below are relative to this work item's `evidence/` directory. `repair-scenarios/<case>/repo/.p2p/work/` contains the actual saved stage reports; adjacent actor reports and command logs identify their execution. Retention manifests map historical scratch paths to durable copies and Git bundles.

| Gap and requirements | Completed observation and durable evidence | Development status |
|---|---|---|
| F1/G1, R3/R4/R27 | Public CLI red/green regression retains receipt/history, recovers in a new clone with a fresh process, and rejects missing/drifted receipts before dispatch. `repair-red.log`, `repair-green.log`. Fresh child-only actors on `repair-scenarios/S4-transfer` and `S4-legacy-transfer` recover target, approval and exact normalization history from transferred durable inputs without prior scratch or another strategy decision. | Scoped repair/checks complete. |
| G1, R13/R27 | Repaired publisher/readiness actors retain exact section bytes and hash in `S9-hash-gates`, `S3-publication`, `S11-parent-only`, both S12 gate variants and S9 resume cases. Direct read-only inspection of retained S9/S3/S12 section files matches source bytes, including separators. S9 current hash is b86ffd9b9b6ccbd0615efbcc57d3da023e1a8a0c185303a28832aafc0490ffe2; S12 is 6ddc21b5453e16b607299bb1789e3ad93a137c9442ddb373b1665302d16e25f5. | Actual reruns observed; old normalized-hash reports remain historical. |
| F2/G2, R24/R30 | `S11-parent-only` actual child proof reports each cover 1/1; full parent review reports CHANGES NEEDED and proof reports 3/4 with R4 disproven. Publication/readiness block despite green simulated CI and repository approval. `repair-s11-independent-assertions.json` retains passing mixed-case literal child assertions and failure specifically at `greet('Ada') == 'Welcome Ada'`. | Complete children/parent-only failure observed. |
| G3, R1/R30 | `S1-ambiguous` saves a focused unresolved intermediate-outcome question without guessing routing; `S1-release` retains independent trunk routing despite a shared release date. Actual slicing records and `handoff-command-evidence.jsonl` retained. | Missing variants executed. |
| G3, R4/R6/R30 | `S4-transfer` and `S4-legacy-transfer` above were rebuilt from durable records/bundles and inspected by a fresh child-path actor. Legacy approval and original normalization bytes remain retrievable. | Restart variants executed. |
| G3, R11/R30 | `S3-publication` actual DRAFT includes complete proposed PR body with discovered epic/example destination, full base, exact plan identity and required parent handoff. `S2-shared` also previews grouped publication. These are previews, not created PRs. | Omitted-target grouped/mixed preview observed. |
| G3, R15/R30 | `S2-incomplete` actual capture review/proof pass while incomplete lookup gets CHANGES NEEDED/NOT PROVEN and publication blocks. `S2-shared` actual capture and lookup verification pass and approved shared-candidate publication reaches DRAFT at epic/example. Prior pending-CI observations remain in original evidence. | Distinct required variants executed. |
| G3, R16/R30 | `S7-unknown` failed current PR read stays unresolved in the saved proposal; no effect inferred. `S7-unaffected` actual capture continuation runs its check and captures the already-landed exact candidate on trunk without sibling blocking or reapproval. Its base records are `supplement-first/S7-default`; its retention manifest records that relationship. | Unknown-state and unaffected continuation observed. |
| G3, R18/R30 | `S8-clean` separate implementation removes only sibling payload from the working candidate, preserving original integration refs/history. Fresh actual full lookup review/proof succeed at trunk. Publisher inspects the clean snapshot but blocks retarget because existing PR17 still has the contaminated old head. Clean snapshot already equals trunk; it does not create an empty or duplicate PR. | Required scoped-candidate positive inspection completed; no successful retarget falsely claimed. |
| G3, R22/R30 | `S9-post-effect` actual sequence 4 base edit persists, then approved v2 changes lookup routing. Actor and fresh resume retain the confirmed edit and block further writes. `S9-interrupted` stops after edit response; fresh actor reads back and reuses it. Both full logs contain one exact base-only edit and later reads, unchanged human body/title/head/draft, one PR and no retry. `repair-effect-assertions.json` maps those assertions and exact plan/report hashes. | Actual after-effect and interruption/resume observed. |
| G3, R23/R30 | `S10-base-only` fresh full review names advanced full target SHA and retains exact-candidate proof; `S10-candidate-change` actual changed candidate blocks for fresh capture/full review/proof; `S10-promise-change` material Unicode amendment returns to plan-acceptance without changing approved contract bytes. Distinct actual reports and command logs retain before/after inputs. | All three distinctions observed. |
| G3, R25/R30 | `S12-parent-ci` and `S12-parent-approval` use otherwise matching full parent review/proof. Readiness separately blocks current IN_PROGRESS CI and REVIEW_REQUIRED repository approval, respectively. No PR/body/merge effect occurs. | Final-parent gates independently observed. |
| G3, R14/R30 setup record | `S13-setup` retains all 32 command records, including initial missing-ref inspection exit 128, corrected absence inspection, exact create with zero old SHA, non-force local-bare-origin push, local/remote readbacks, and repeated matching-ref reuse without writes. | Complete new setup action record observed. |

`repair-scenario-hosts.json` identifies actual actor contexts, stages and permissions. Some unaffected handoff scenarios retain original c916e48b protocol package identities; their reports identify those exact inputs. Exact-byte publication/readiness, repaired S11 and transfer/effect runs record the repaired 209562ca protocol and relevant repaired skills. No earlier package execution is silently relabeled as a repaired-package run. The old S11 direct child violation, old normalized hashes, and misnamed before-effect race remain in original scenario evidence and report history; these fresh cases supplement them.

## Checks and limitations

- `/opt/homebrew/bin/python3.14 -B -m unittest discover -s checks -p test_p2p_delivery.py -k public_cli_retains`: before fix, failed at absent transferred approval receipt; after fix, one test passed in 6.136 seconds. Evidence: `evidence/repair-red.log`, `evidence/repair-green.log`.
- `/opt/homebrew/bin/python3.14 -B checks/epic_delivery_fixture.py self-check`: passed tracker and S11 independent assertions. Evidence: `evidence/repair-fixture.log`.
- `PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.14 -B -m unittest discover -s checks -p 'test_*.py'`: all 30 tests passed in 135.901 seconds; filesystem checks passed. Evidence: `evidence/repair-suite.log`. Codex version probes reported denied PATH-alias creation; no test failed.
- `git diff --check`: passed.
- Installed filesystem `capture` then `validate` retained and reread the exact candidate above. Contract and binding source hashes unchanged. All 130 manifest entries are recoverable. Old candidate/report bytes preserved by installed `fs.save` history.

The retained actor runs now supply the required controlled-interface agent observations. Development checks and actor reports do not establish live GitHub compatibility or acceptance. Existing failed review/proof remain historical for the first candidate. No reports were manually upgraded and no contract row was edited.

## Decisions and next step

The selected local repair and its mandatory development evidence are complete. This evidence-only followup inspected the durable actor reports, saved stage reports, independent assertion records and actual effect logs listed above. It changed only this implementation/repair handoff and history; no product bytes, test execution or new repair cycle was introduced. The exact candidate, agreement, binding source and comparison base revalidate unchanged.

Fresh full independent review and proof of this candidate are in progress in the enclosing workflow. Their findings and acceptance verdicts remain independent; this IMPLEMENTED outcome is limited to the stated repair/evidence scope. No remaining development gap is known from this inspection. Live-service validation remains explicitly unexecuted under the available authority; tracker observations are controlled simulations.

Report storage: `.p2p/work/epic-delivery-strategy/implementation.md`, saved and read back through installed `fs.save`. The earlier PARTIAL implementation, repair report and failure observations remain in history; `evidence/repair-implementation.md` retains the pre-completion repair-stage account.

Implementation report only; independent acceptance requires /prove.

Next steps:

1. Complete the in-progress `/review-implementation work/epic-delivery-strategy.md` against `5e369c1b45ba817b8add6b20a9b7b1c97898fa12` for `snapshot:sha256:7e5c54fa4183651c94b4f6b83bea7cc841b2722a5693047c5c8be8faaf8f41e8`.
2. Complete the in-progress `/prove work/epic-delivery-strategy.md; candidate snapshot:sha256:7e5c54fa4183651c94b4f6b83bea7cc841b2722a5693047c5c8be8faaf8f41e8` against the full unchanged contract and retained observations.
