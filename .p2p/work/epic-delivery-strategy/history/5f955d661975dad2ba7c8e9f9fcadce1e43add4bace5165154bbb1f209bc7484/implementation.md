# PARTIAL: Independent, grouped, and mixed epic delivery scoped repair

Contract: `work/epic-delivery-strategy.md` v1, SHA-256 `78cad1d7f85183100214da15fdc8418ed2220ce1af80764d648e139fdd899895`. Byte-identical to the approved agreement.
Binding source: `plans/epic-delivery-strategy-spec.md`, SHA-256 `7a231d84f739a459f770870d23038fbc4946c759f04241c87f2a6322d9a1645e`.
Scope: saved review F1/F2 and matching proof G1/G2, plus the requested G3 deterministic post-edit fixture support. Remaining G3 actor observations belong to the enclosing workflow.
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

| IDs | Implementation and direct check | Observed result | Remaining gap |
|---|---|---|---|
| R3/R4/R27, F1/G1 | `routing_records`; public CLI test `test_public_cli_retains_plain_approval_on_transfer_and_fresh_recovery` | Red before fix: transferred receipt absent. Green after fix: missing initial receipt blocks; actual CLI transfers receipt/history; a new clone and fresh CLI recover from child path; drift/disappearance block; zero dispatches throughout. | Fresh installed-skill transfer/normalization actor observations remain with the enclosing workflow. |
| R13/R27, G1 | Protocol byte extraction and publication/readiness save/readback steps | All 17 protocol copies identical; existing controller uses identical byte extraction. | Fresh publication/readiness actors must retain exact approved-section bytes and hash. Instructions alone do not establish behavioral acceptance. |
| R24/R30, F2/G2 | S11 fixture and `epic_delivery_fixture.py self-check` | Three full child checks and literal mixed-case child assertions pass; parent public workflow returns Welcome ADA and parent check fails. | Fresh full child/parent review/proof and parent publication/readiness observations remain with the enclosing workflow. |
| R22/R30, G3 support | `after_edit` tracker injection and self-check | Real edit persisted, plan replaced, event recorded after_persisted_edit; existing lost response/readback/effect-count/concurrent-body checks retained and pass. | Actual interrupted/concurrent publisher and fresh-resume observations, plus other G3 cases in saved proof, remain pending here. |

## Checks and limitations

- `/opt/homebrew/bin/python3.14 -B -m unittest discover -s checks -p test_p2p_delivery.py -k public_cli_retains`: before fix, failed at absent transferred approval receipt; after fix, one test passed in 6.136 seconds. Evidence: `evidence/repair-red.log`, `evidence/repair-green.log`.
- `/opt/homebrew/bin/python3.14 -B checks/epic_delivery_fixture.py self-check`: passed tracker and S11 independent assertions. Evidence: `evidence/repair-fixture.log`.
- `PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.14 -B -m unittest discover -s checks -p 'test_*.py'`: all 30 tests passed in 135.901 seconds; filesystem checks passed. Evidence: `evidence/repair-suite.log`. Codex version probes reported denied PATH-alias creation; no test failed.
- `git diff --check`: passed.
- Installed filesystem `capture` then `validate` retained and reread the exact candidate above. Contract and binding source hashes unchanged. All 130 manifest entries are recoverable. Old candidate/report bytes preserved by installed `fs.save` history.

These development checks do not establish real agent behavior, live GitHub compatibility, or acceptance. Existing failed review/proof remain historical for the first candidate. No reports were manually upgraded and no contract row was edited.

## Decisions and next step

Continue the already authorized enclosing G3 evidence work, including fresh exact-byte publication/readiness and corrected S11 actor runs. Full independent review and proof must evaluate the repaired candidate and retained observations. This report is PARTIAL because those material scenario observations are not produced by this repair context.

Report storage: `.p2p/work/epic-delivery-strategy/implementation.md`, saved and read back through installed `fs.save`.

Implementation report only; independent acceptance requires /prove.

Next steps:

1. Execute the fresh actor variants explicitly listed in saved `proof.md` G1/G2/G3 using the repaired installed packages and fixtures; retain their actual state, commands and effects under `evidence/`. Expected observations are defined in `checks/epic-delivery-scenarios.md`; no missing outcome decision was introduced.
2. `/review-implementation work/epic-delivery-strategy.md` against `5e369c1b45ba817b8add6b20a9b7b1c97898fa12` for `snapshot:sha256:7e5c54fa4183651c94b4f6b83bea7cc841b2722a5693047c5c8be8faaf8f41e8`.
3. `/prove work/epic-delivery-strategy.md; candidate snapshot:sha256:7e5c54fa4183651c94b4f6b83bea7cc841b2722a5693047c5c8be8faaf8f41e8` after the enclosing workflow has retained the required scenario observations.
