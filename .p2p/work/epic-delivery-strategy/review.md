# REVIEWED: Independent, grouped, and mixed epic delivery

Contract: `work/epic-delivery-strategy.md` v1, SHA-256 `78cad1d7f85183100214da15fdc8418ed2220ce1af80764d648e139fdd899895`.
Binding source: `plans/epic-delivery-strategy-spec.md`, SHA-256 `7a231d84f739a459f770870d23038fbc4946c759f04241c87f2a6322d9a1645e`.
Candidate: `snapshot:sha256:7e5c54fa4183651c94b4f6b83bea7cc841b2722a5693047c5c8be8faaf8f41e8`.
Recoverable content: `/private/var/tmp/p2p-issue33-verifier-8eh45dgs/second-candidate/candidate`, with the complete embedded manifest at sibling `records/candidate.json`.
Comparison: ORIGINAL full base `5e369c1b45ba817b8add6b20a9b7b1c97898fa12`, reconstructed in sibling `base` from `records/comparison-base-manifest.json`. This is a full re-review, not a repair-only diff review.
Stability: candidate and base match all 130 and 127 manifest entries respectively by path inventory, type, bytes, executable mode and literal symlink target. Canonical manifest hashes independently recompute to candidate `7e5c54fa4183651c94b4f6b83bea7cc841b2722a5693047c5c8be8faaf8f41e8` and base `60b794847ee5831aba43cbd702b15e4ba8938930a244a14b19f5f43a27a8d416`. Contract and binding source match the candidate record. Final recheck found no drift in either manifest or the protected record/evidence inventories.
Reviewer: independent context `/root/review_epic_delivery_final`; installed `/Users/grove/.agents/skills/review-implementation/SKILL.md` and its protocol. No delegated reviewers.
Authority: exact-v1 approval and explicit coordinated unsliced delivery override read from protected `records/planning-handoff.md`. Only the slicing handoff is overridden; R1–R30 and agreement bytes remain binding. No parent contract applies to this implementation review.
Coverage: FULL R1–R30 across contract fidelity, scope and simplicity, and engineering quality. No acceptance verdicts are issued here.

## Contract fidelity

No material change-required findings.

Historical F1 is repaired. `routing_records` now follows relative Markdown receipts and legacy bare local `.md` approval references, including references in retained historical plan text. `create` gathers those records before admission; `source_stable` checks their retained hashes in source and transferred workspace before subsequent dispatch. The public CLI regression uses fresh processes and a zero dispatch budget. It observed rejection of a missing receipt before admission, exact receipt/history transfer, successful fresh-checkout admission from transferred records, and blocking after receipt replacement or loss in either source or recovered workspace. No model response substitutes for those assertions.

The exact-byte repair for historical proof gap G1 is also present in protocol, publication, and readiness instructions. The section extraction preserves separators, trailing spaces, CRLF and EOF; consumers must read back the saved bytes and hash. I independently extracted the completed S9 actor's current plan and compared it with both current reports and the retained raw section. All match SHA-256 `b86ffd9b9b6ccbd0615efbcc57d3da023e1a8a0c185303a28832aafc0490ffe2`. Their recorded installed skill/protocol hashes match this candidate. Historical top-level copies with the earlier shortened hash remain historical, not the current repaired outputs.

The controller binds the active plan separately from the product manifest, starts sliced delivery from the intended target, rejects a conflicting base, and checks both source and transferred routing during resume. Pending proposals remain outside the active section. The consuming skills retain prerequisite, scope, authority, verification and parent-completion obligations.

## Scope and simplicity

No material findings.

The change extends existing skills, Markdown plans/history, controller admission/resume and scenario conventions. The routing helper has actual consumers in admission, stage inputs and completion. Disposable Git and tracker fixtures serve the specified behavioral checks. There is no new scheduler, runtime dependency, policy service, tracker requirement, multiple-integration-group model or automatic merge path. New fixture and documentation files have required consumers; no speculative abstraction was identified.

## Engineering quality

No material change-required findings.

Historical F2 and the fixture defect underlying G2 are repaired. S11 leaves `capture`, `lookup`, `summary` and their full child checks unchanged. Only parent-owned `greet` supplies an uppercased value to capture. The runnable self-check independently asserts the original-case child outcomes, observes the faulty public workflow's `Welcome ADA`, and requires the parent check to fail. All three child checks pass and the parent check fails. This now represents a parent composition defect rather than a weakened child check.

The tracker self-check also exercises an edit persisted before a lost response, subsequent readback with one effect, a concurrent human body edit, and a plan replacement after a persisted base edit. Its output establishes fixture behavior, not installed-skill acceptance. The public scenario procedure requires separate actual skill observations for these phases and labels controlled simulation explicitly.

All 17 shipped protocol references resolve to exact canonical bytes, SHA-256 `209562cadbad5a945998fe1fb370ffab5ab4ea648fc4ac720888c2d3a3ca634d`. The added retarget instructions were read with the surrounding initial-publication and readiness rules; their narrow base-only authority does not authorize commit, push, replacement PR, body replacement or merge.

## Coverage inspected

This is an inspection map, not an acceptance matrix. Skill paths below are under `skills/productivity/`.

| Requirements | Implementation and evidence examined |
|---|---|
| R1–R2 | Outcome-based recommendation and default/exception plan rules in protocol and slicing; controller field/table parsing; S1–S3/S14 and custom `trunk` fixtures. |
| R3–R4 | Active/proposed separation, history/receipt transfer, child-parent resolution, exact section identity, public CLI fresh-transfer and receipt-loss regression. F1 repaired. |
| R5–R7 | Unsliced path and source-preservation regression; legacy-normalization instructions; missing/conflicting/fenced/proposed-only rejection; pending proposal continuity. |
| R8–R10 | Actual prerequisite checks in delivery/implementation, intended target starting tree, exact base matching, inherited agreement and target-advance refresh; controller child tests and S14 missing/present setup. |
| R11–R13 | Omitted-target discovery, explicit/actual target conflicts, initial preview/body, retarget/readiness instructions, exact plan bytes and history. Current S3 initial preview and repaired S9 reports inspected. |
| R14–R15 | Missing/conflicting integration-ref handoff, approved start/ancestry, authorization/readback, complete child verification and shared-candidate exception. Focused ref test passed; completed S2 shared/incomplete reports inspected. |
| R16–R19 | Strategy preview and preservation of contracts, local work, human edits, integrated history and landed children; S7–S10 procedures and S8 clean-candidate publication blocker, which rejects the old PR's sibling-contaminated head. |
| R20–R22 | Strategy/effect authority separation, exact known-PR base-only operation, pre-effect checks, post-effect readback, uncertainty/restart rules and phase-specific tracker injection. Fixture self-check passed. Final S9 post-effect and interrupted-resume logs independently show one base-only edit per case and no repeated effect after fresh resume. |
| R23 | Destination-only, base-only, candidate/agreement and promise changes in protocol and consumers; preserved historical report identities and controller stale-input checks. |
| R24–R26 | Complete assembled-parent review/proof and gates, independent contributions, corrected S11 composition defect and S12 all-independent flow. Current S12 readiness reports separately block pending CI and missing repository approval with otherwise matching parent reports. |
| R27 | Entire original-base diff, surrounding consumer rules and controller callers/error paths; all 17 distributed protocol copies; unchanged candidate/history/authorization safeguards. |
| R28–R29 | README link, mixed-destination/open-PR-change/final-parent walkthrough, and FAQ definitions and next actions. |
| R30 | All six extended scenario documents, complete S1–S14 procedure, fixture builder/tracker, withheld oracle, exact installed identities, restart/race procedures, actual effects and simulation labels. Corrected checks and selected completed actor outputs examined; no exhaustive second proof performed. |

## Checks and limitations

The first boundary check was `mkdir /private/var/tmp/p2p-issue33-verifier-8eh45dgs/review-boundary-probe`. It exited 1 with `Operation not permitted`. No existing input file was targeted. All operations used the default sandbox; no escalation, live network, GitHub call or credential inspection occurred. Candidate/base/records and the live project were not modified. Diagnostics wrote only under `/private/tmp/p2p-final-review` or disposable temporary repositories.

Inspection covered every changed implementation/document/scenario file against the original full base, with byte equality used for repeated protocol copies. Both protected trees have no `.git`; their complete reconstructed manifests were verified. The supplied base SHA is the enclosing workflow's fixed comparison identity; this context independently verifies its materialized full content rather than substituting the mutable source checkout.

Commands ran from the fixed candidate with `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp` and supported `/opt/homebrew/bin/python3.14`:

- `-m unittest discover -s checks -p test_p2p_delivery.py -k public_cli`: 1 test passed in 5.277 seconds. Actual receipt transfer/admission/resume assertions are described above.
- Same command with `-k child`: 4 tests passed in 25.205 seconds, covering transferred plan/history, absent/conflicting/proposed decisions, intended starting tree, and target/base drift.
- With `-k integration_missing`: 1 test passed in 0.395 seconds, covering missing and unrelated refs without overwriting them.
- With `-k success_source`: 1 test passed in 6.667 seconds, covering ordinary unsliced delivery and source preservation through the explicit fixture transport.
- `checks/epic_delivery_fixture.py self-check`: exit 0; persisted edit/lost response/readback/effect count, post-edit plan replacement, complete child outcomes and parent-only failure assertions passed.
- `inventory.py`: complete candidate/base manifest, contract/source and 17 protocol-copy checks passed.
- `evidence-check.py`: all 716 file entries in completed repair-scenario retention records matched their saved SHA-256 values. Current S9 raw section/report bytes and installed hashes match. Current S12 CI/approval reports retain exact raw section SHA-256 `6ddc21b5453e16b607299bb1789e3ad93a137c9442ddb373b1665302d16e25f5`; both cases have four tracker reads and zero effects.

Final protected inventory comparison passed for candidate/base/records and completed repair evidence, including all path types, permission modes, symlink targets and file hashes. The full inventory digest is `445dbce47b2b7d89bb0e219773c86aca6ffb0aa9bd476b1e04f2cf98d3004c79`. The final supplement is separately checked against every retained file hash.

Codex version probes in fixture-transport tests printed denied PATH-alias warnings. Tests nevertheless passed; these tests did not launch model stages. No unsupported Python test result is counted.

Completed supplemental evidence inspected at `/private/var/tmp/p2p-issue33-verifier-8eh45dgs/repair-scenarios-completed`, with exact original-to-saved mappings in each case's `retention.json`. Relevant current reports are nested under each case's `repo/.p2p/work/`; older top-level reports retain historical meaning. This review does not adopt author or proof statuses as its own evidence. The exact-byte assertions and effect logs were checked directly.

The final supplemental was inspected at `/private/var/tmp/p2p-issue33-verifier-8eh45dgs/repair-final-supplement`. All 180 retention entries match their saved hashes. Fresh S11 child reports each cover their complete child requirement, while parent proof records R4 failure and publication/readiness block despite green CI and repository approval. I reran the retained fixture checks read-only: capture, lookup and summary pass; parent exits 1 at the public `greet` assertion. Tracker logs contain no effects. S9 post-effect and interrupted-resume each contain exactly one PR17 base-only edit, later readback, unchanged title/body/head/draft, one PR, and exact current plan retention. The post-effect log places replacement after persistence; its active plan hash is `89c07679eeb571d6fddf1a85067c69c24571efd4d503845851d4fb1048725575`. The interrupted case retains `b86ffd9b9b6ccbd0615efbcc57d3da023e1a8a0c185303a28832aafc0490ffe2`. Fresh resume reports respectively block superseded routing and reuse the confirmed effect without another write. These observations resolve the repair-specific review uncertainty; full acceptance of all S1–S14 variants still belongs to the separate fresh proof stage. Missing matching proof is not itself a review defect. Controlled tracker behavior does not establish live GitHub compatibility; live-service validation was not performed. No merge-readiness or acceptance claim is made for this product candidate.

## Handoff

No material remaining findings from full inspection. Historical F1/F2 require no further implementation change on this candidate. Historical G1 is addressed by inspected repaired byte-retention behavior; G2 corrected child/parent separation and G3 post-effect/resume behavior have also been independently cross-checked in the final supplement. Full requirement verdicts remain for fresh proof. No contract amendment is needed and no repair was performed during review.

Scratch report: `/private/tmp/p2p-final-review/review.md`. Evidence consists of adjacent `inventory.py`, `inventory-before.log`, `inventory-after.log`, `protected-inventory.py`, `protected-inventory.json`, `protected-before.log`, `protected-after.log`, `evidence-check.py`, `evidence-check.log`, `final-evidence-check.py`, `final-evidence-check.log`, `receipt-regression.log`, `child-regressions.log`, `setup-regression.log`, `unsliced-regression.log`, and `fixture-regression.log`. Retain these narrow evidence files with this exact report. Proposed durable destination: `.p2p/work/epic-delivery-strategy/review.md`; enclosing workflow storage and reread are pending. Existing reports remain historical under the protocol's retention rule.

Review only; acceptance proof and merge readiness are separate.

## Next steps

1. Save and reread this exact report and its narrow evidence under `.p2p/work/epic-delivery-strategy/`, preserving the prior review and its evidence.
2. Complete `/prove work/epic-delivery-strategy.md; candidate snapshot:sha256:7e5c54fa4183651c94b4f6b83bea7cc841b2722a5693047c5c8be8faaf8f41e8`, against comparison base `5e369c1b45ba817b8add6b20a9b7b1c97898fa12`, using the same contract/source hashes and all required repaired actor observations. No second automatic repair is authorized by this review.
