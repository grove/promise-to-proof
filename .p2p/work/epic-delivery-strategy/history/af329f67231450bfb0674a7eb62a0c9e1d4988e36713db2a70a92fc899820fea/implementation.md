# PARTIAL: Independent, grouped, and mixed epic delivery

Contract: `work/epic-delivery-strategy.md`, v1, SHA-256 `78cad1d7f85183100214da15fdc8418ed2220ce1af80764d648e139fdd899895`.
Scope: R1–R30, whole approved contract. The user approved v1 and delivery without slicing. No acceptance requirement was removed.
Candidate before: `5e369c1b45ba817b8add6b20a9b7b1c97898fa12` on `main`.
Candidate after: Scoped working-tree changes; final fixed candidate capture belongs to the enclosing delivery after behavioral scenario observations. This interim report does not create or replace `candidate.json`.
Review base: `5e369c1b45ba817b8add6b20a9b7b1c97898fa12`, fixed by the enclosing delivery.
Changes: Shared epic-delivery protocol, seven consuming skills, existing controller routing/transfer/resume checks, direct regression tests, controlled tracker/disposable Git fixtures, scenario procedures, README walkthrough link, how-to, FAQ, and controller documentation. The approved contract bytes and unrelated work remain unchanged. No source-repository Git or remote effects occurred.

## Requirement handoff

Paths below are repository-relative. `protocol` means `docs/acceptance-contract-protocol.md`, Epic delivery plans. Skill paths are `skills/productivity/<name>/SKILL.md`. Scenario evidence in this table remains pending until actual fresh-agent observations are attached by the enclosing delivery; the fixture self-checks are not substitutes.

| ID | Implementation reference | Acceptance test/check or evidence path and observed result | Remaining gap |
|---|---|---|---|
| R1 | protocol; slice-contract outcome-based recommendation | S1–S3/S14 procedures and input fixtures materialized | Actual recommendation and ambiguous-intent runs |
| R2 | protocol plan section; slice-contract; `p2p_delivery.py:routing` | Controller child target, parent final target, custom `trunk`, and conflicting destination assertions passed | Actual S2/S3/S14 skill decisions |
| R3 | protocol approved/proposed sections and history; slice-contract | `test_child_routing_transfers_plan_and_binds_stage_inputs` passes pending-proposal continuity and approved revision invalidation | Actual S3/S5 save/restart runs |
| R4 | protocol transfer rules; controller `routing_records` and `source_stable` | Same test passes exact plan/history/linked approval transfer, history tamper rejection, and routing stage identity; parent plan loss test passed | Fresh child-path S4 actor transfer |
| R5 | deliver-issue, publication, readiness unsliced rules; controller no-plan path | Existing 19 controller tests retained and passed, including unsliced complete delivery | Unsliced S1 skill publication/readiness handoffs |
| R6 | protocol and consuming skills legacy normalization | S4 legacy fixture and procedure materialized | Actual normalization/restart observations |
| R7 | protocol; consumers; controller admission | `test_child_missing_conflicting_and_proposed_routing_never_dispatch` passed missing, duplicate, conflicting, fenced-example and proposed-only cases; zero stage effects | S5 skill blockers/active selection |
| R8 | delivery/implementation prerequisite checks in actual candidate | S14 missing/present executable prerequisite fixtures | Actual entry-point behavior |
| R9 | delivery/implementation destination before base; controller target-tree admission | `test_child_starting_tree_is_target_not_unrelated_head` passed and failed meaningfully on original code; source sibling bytes preserved | S2–S4/S13 skill handoffs |
| R10 | review current target-tip/inherited identity; controller base comparison | `test_child_target_advance_and_wrong_explicit_base_block` passed exact target advance and zero-dispatch checks | S10/S13 review refresh runs |
| R11 | publish-pr omitted/conflicting target and destination/body fields | S2/S3/S6 tracker fixture and procedures materialized | Actual publication previews and no-effect conflict run |
| R12 | merge-readiness expected/actual target blocker, no retarget | S6 fixture and readiness procedure materialized | Actual mismatch report and unchanged target |
| R13 | publication/readiness approved section revision/hash/text; controller routing identity | Controller active-plan mutation blocks resume without new dispatch, pending proposal does not | S9/S10 stale publication/readiness runs |
| R14 | protocol and delivery exact missing-branch setup/readback | `test_integration_missing_and_unrelated_ref_give_setup_handoff` passed exact SHA handoff, unrelated ancestry rejection, no ref replacement | S13 actual authorized setup/readback variants |
| R15 | protocol, slicing and publication child gates/shared-candidate exception | S2/S13 incomplete/prerequisite/CI/shared-candidate procedures materialized | Distinct actual skill handoffs |
| R16 | slice-contract strategy revision preview | S7–S10 fixtures retain work/PR states and proposals | Actual complete previews and unaffected-child continuation |
| R17 | slice-contract preservation and no effect from plan save | Fixtures and `verify --expect no-effects` assert contract/human-note/PR preservation | Actual S7 strategy apply observations |
| R18 | slice-contract, implementation, review and publication scope rules | Controller target-tree regression prevents unrelated HEAD import; S8 Git fixture contains recognizable sibling payload | Actual contaminated/scoped candidate publication handoffs |
| R19 | protocol and slicing landed history rules | S7 landed-child fixture | Actual preserved historical landing and remaining-child revision |
| R20 | protocol/skills separate strategy and effect authority | Tracker logs and ref inventories provide independent effect oracle | S7/S9/S13 exact authority variants |
| R21 | publish-pr known-open-PR retarget path and readback | Stateful controlled tracker self-check passed exact base-only persistence/readback | Actual fresh publisher success/rejection under exact verification and authority |
| R22 | protocol/publication stale preview, uncertain readback, partial/resume | Tracker self-check passed lost response, exact edit count, and concurrent change | Actual S9 interrupted/concurrent/restart skill runs |
| R23 | protocol/slicing/review exact candidate/base/agreement refresh distinctions | Controller base/plan drift checks passed; acceptance contract hash remains exact | Actual S10 base-only/repaired-candidate/changed-promise handoffs |
| R24 | protocol and prove assembled parent interaction requirements | Fixture development checks ran individually passing S11 children and actual failing parent; S12 combined behavior passed | Fresh independent parent proof/review skill observations |
| R25 | protocol/publication/readiness parent gates; child completion handoffs | S2/S11 gate fixture/procedures materialized | Actual missing-parent-proof/interaction/CI/approval blockers |
| R26 | protocol/prove all-independent combined verification without empty PR | S12 actual combined fixture behavior passed; tracker effect inspection available | Full parent review/proof actor runs and zero unnecessary PR creation |
| R27 | canonical protocol and seven consuming skill files; controller docs | All 17 shipped protocol links resolve to identical bytes; all repository unit checks pass | Actual S1–S14 installed-copy runs |
| R28 | README slicing link; docs/how-to.md mixed/change/parent walkthrough | Linked walkthrough materialized and inspected for three stages and named targets | Execute walkthrough against S3/S7/parent fixtures |
| R29 | docs/faq.md child completion/integration/parent acceptance | FAQ explicitly distinguishes events, final review/proof and CI/approval gates, and merge authority | Compare to actual S2/S11/S12 observed states |
| R30 | six existing scenario documents; `checks/epic-delivery-scenarios.md`; `checks/epic_delivery_fixture.py` | Plumbing self-check and representative fixture assertions passed; raw requests/oracle separation and installed hashes provided | All actual S1–S14 variants with retained actor/effect/state observations |

## Checks and limitations

Durable development evidence is in `evidence/implementation-development.json` and its two referenced logs. Fixture evidence is in `evidence/fixture-development.json`. Each was saved through `p2p_filesystem.save` and reread. The evidence records actual commands, outcomes, content hashes, and limitations.

- `python3 -m unittest discover -s checks -p 'test_*.py'`: 29 tests passed in 139.274 seconds; P2P filesystem checks passed. Final historical-link handling was then covered by the focused test below.
- `python3 checks/test_p2p_delivery.py`: expanded 25-test controller suite passed in 156.872 seconds. The original 19 tests also passed before adding routing cases.
- `python3 -m unittest discover -s checks -p 'test_p2p_delivery.py' -k child_routing_transfers_plan`: final focused transfer/history/approval/tamper/resume test passed in 11.365 seconds.
- The new unrelated-HEAD regression ran against the original controller loaded from the fixed base. It failed because `sibling.txt` appeared in the delivered candidate. It passes against the changed controller.
- `python3 checks/epic_delivery_fixture.py self-check`: persisted base edit, lost response, readback, exact effect count, and concurrent-change assertions passed against the simulated tracker.
- `git diff --check`: passed.
- All 17 `skills/**/references/acceptance-contract-protocol.md` paths resolve to canonical protocol bytes, SHA-256 `c916e48be9de29f423716518dc290a64b9c667bdf42b40da87dc346853957b43`.

Controller transport tests use the repository's existing explicit fake transport and do not establish live-host isolation or independent skill behavior. The tracker is a simulation; no live GitHub mutation or compatibility validation ran. No authenticated account files or credentials were read. The enclosing delivery separately owns host-boundary receipts and actual fresh skill contexts. Its behavioral scenario results must be retained before `IMPLEMENTED`; no acceptance verdict is claimed here.

## Decisions and next step

No contract amendment or product-outcome decision is pending. The approved delivery-without-slicing instruction overrides the contract's proposed slicing handoff, not R1–R30. The Markdown plan shape is an ordinary implementation choice; approval evidence remains explicit, and a heading alone cannot grant authority. Existing user authority for scoped local work was reused.

The enclosing delivery owns final candidate capture with this fixed review base and subsequent independent review/proof. Update this interim report through the history rule after attaching actual scenario observations. Preserve source work and all effect boundaries. The user's later standing GitHub CLI permission applies only to `gh pr` and `gh issue` escalations and does not expand this task's no-publication scope.

Report storage: `.p2p/work/epic-delivery-strategy/implementation.md`, saved and reread.

Implementation report only; independent acceptance requires /prove.

Next steps:

1. Execute the pending fresh skill runs and variants in `checks/epic-delivery-scenarios.md`, retaining each actual request, installed hashes, actor transcript, saved plan/report, refs, tracker calls/state, and assertions. Expected result: each R1–R30 planned evidence obligation has a meaningful observed result, including real controlled retarget success, rejected stale writes, resume without duplicates, and parent interaction failure.
2. Resolve observed product failures, then capture the exact final candidate and update this report with the candidate identity and requirement evidence. Hand that fixed candidate separately to `/review-implementation work/epic-delivery-strategy.md` and `/prove work/epic-delivery-strategy.md`.
