# CHANGES NEEDED: Independent, grouped, and mixed epic delivery

Contract: `work/epic-delivery-strategy.md`, v1, SHA-256 `78cad1d7f85183100214da15fdc8418ed2220ce1af80764d648e139fdd899895`.
Binding source: `plans/epic-delivery-strategy-spec.md`, SHA-256 `7a231d84f739a459f770870d23038fbc4946c759f04241c87f2a6322d9a1645e`.
Candidate: `snapshot:sha256:8ff16e4594d451c80b5c1cb7225874bb89b4190a6448dba86ee146e025ab0dd8`.
Recoverable content: `/private/var/tmp/p2p-issue33-verifier-8eh45dgs/first-candidate/candidate`, with the complete manifest in sibling `records/candidate.json`.
Comparison: full supplied base `5e369c1b45ba817b8add6b20a9b7b1c97898fa12`, reconstructed in sibling `base`; complete base manifest in `records/evidence/comparison-base-manifest.json`, record SHA-256 `2b4320ec8d952a8e02cad14c4ee2d7d0a6a0409a1011b33a6c247a5d8f68b030`.
Stability: candidate, contract, binding source, and base inventory unchanged at final recheck. All 130 candidate and 127 base entries match their manifests by complete path inventory, bytes, executable modes, types, and literal symlink targets. The candidate key was independently recomputed from canonical manifest JSON.
Reviewer context: independent agent `/root/review_epic_delivery`; installed `/Users/grove/.agents/skills/review-implementation/SKILL.md`; no delegated reviewers.
Authority: exact-v1 approval and the explicit unsliced-delivery override were read from `records/planning-handoff.md`. The approved contract was not revised. No parent contract applies to this review.
Coverage: FULL R1–R30 inspection across contract fidelity, scope and simplicity, and engineering quality. This report contains no acceptance verdicts.

## Contract fidelity

### F1: A referenced approval receipt can disappear during controller transfer

Category: demonstrated transfer defect. Requirements: R4, with R3 and the shared protocol's approval-evidence retention rules also affected.

Location: `skills/productivity/deliver-issue/scripts/p2p_delivery.py:180`, especially selection at lines 185–199; its consumers are `create` at line 753 and `source_stable` at line 331. The shipped example is `checks/epic_delivery_fixture.py:243`, which names `approval.md` in ordinary text and creates that receipt at line 272.

`routing()` accepts the fixture's approved plan. `routing_records()` copies the plan, retained slicing history, an optional `planning-handoff.md`, and Markdown-linked records. It does not copy the actual `approval.md` named by this accepted plan. Preparing the unchanged S4 fixture and calling these functions returned only `.p2p/work/parent/slicing.md`, although the source receipt existed.

A second reproduction used the existing explicit FakeTransport solely to exercise controller storage and resume. It completed with `approval_copied: false`. Deleting the source receipt afterward still produced status exit 0 and `REVIEWED_AND_PROVEN`. These are observed controller outputs, not reviewer-issued proof claims. Because the receipt never enters `routing_records`, its loss is also absent from the stability check.

Consequence: a fresh child workspace lacks a required approval source, and subsequent loss of that source does not invalidate the retained routing claim. This contradicts the requirement that necessary approval records travel with the work.

Smallest correction: make local approval references consistently resolvable by the transfer mechanism. An explicit Markdown-link convention is sufficient if both producers and admission enforce it; update the shipped fixture and reject or normalize an unresolved required receipt before dispatch. Retain a regression that checks the actual receipt in the transferred workspace and rejects its later loss. No general artifact framework is needed.

Evidence: `approval-transfer-check.py` and `approval-transfer-check.log` in the scratch evidence directory below; unchanged S4 fixture at `s4-transfer/`.

No other material contract-fidelity defect was established by this inspection. Pending independent scenario executions remain a disclosed execution limit.

## Scope and simplicity

No material findings. The change uses the existing Markdown plan, history mechanism, controller, and workflow skills. It adds no scheduler, tracker policy service, dependency, merge operation, or additional integration-group model. The routing helper has required consumers in admission, stage identity, resume, and completion. The controlled tracker and disposable Git fixtures serve the explicitly requested scenario checks.

## Engineering quality

### F2: S11 weakens a child check instead of preserving a complete child outcome

Category: demonstrated acceptance-check weakness. Requirements: R24 and R30; source scenario S11.

Location: `checks/epic_delivery_fixture.py:215`, the S11 branch that uppercases captured values and changes the standalone capture assertion; compare the child agreement generated at lines 164–176 and the ordinary assertion at line 186.

S11 changes `capture` to return `name.upper()` as the stored value, then changes its child check to use uppercase-only input. The child's contract still requires the original value for ASCII names. In the generated fixture:

- `check.py capture`, `lookup`, and `summary` each exited 0.
- `check.py parent` exited 1.
- The independent child-contract assertion `capture('Ada') == {'ada': 'Ada'}` also exited 1; actual output was `{'ada': 'ADA'}`.

Consequence: the fixture demonstrates that a weak child check can miss a direct child defect. It does not exercise the required case of complete child outcomes whose assembled interaction fails. A correct full child review or proof would reject capture before the intended parent-only failure, so running more agents on these same bytes does not resolve this test-design problem.

Smallest correction: make S11's child agreements and independent child assertions hold while a parent-owned composition or integration invariant fails. Keep the full child assertions intact and independently exercise the parent failure. Update the S11 description to match that actual setup. The broader parent-verification instructions themselves preserve the required gate.

Evidence: `s11-check.log` and the generated `s11-interaction/` fixture in the scratch evidence directory.

## Coverage inspected

This is an inspection map, not a proof matrix. Skill paths are under `skills/productivity/`; controller means `deliver-issue/scripts/p2p_delivery.py`.

| Requirements | Implementation and checks inspected |
|---|---|
| R1–R2 | Protocol outcome-based destination choice and plan fields; `slice-contract`; controller final/integration/default/exception parsing; S1–S3/S14 procedures and custom `trunk` fixtures. |
| R3–R4 | Approved/proposed separation, revision/hash capture, history/approval transfer, child-path resolution, `routing_records`, and resume checks. F1 applies. |
| R5–R7 | Unsliced no-plan path, legacy normalization instructions, missing/duplicate/conflicting/fenced/proposed-only rejection, and pending-proposal continuity. |
| R8–R10 | Delivery/implementation prerequisite instructions, actual-target starting tree, exact full comparison base, parent final routing, review inherited inputs, target-advance rejection, and S14 missing/present behavior. |
| R11–R13 | Publication target discovery/conflict checks, readiness target mismatch, approved-plan identity retention, stale-preview checks, exact review-base matching. |
| R14–R15 | Missing-ref starting-SHA handoff, unrelated ancestry rejection, branch readback instructions, full child verification, integrated prerequisites/shared-candidate exception, CI gate separation. |
| R16–R19 | Strategy-change preview, work/human-edit/history preservation, landed-child handling, integrated-sibling contamination and extraction handoff; S7/S8/S10 procedures and fixture trees. |
| R20–R22 | Separate strategy/effect authority, known-PR base-only retarget, exact preview inputs, pre-write checks, readback, lost-response reconciliation, partial effects, and simulation fault injection. Initial publication and narrow retarget paths were read together. No confirmed instruction contradiction was found. |
| R23 | Destination-only versus base-only versus candidate/agreement changes in protocol and consuming skills; stale controller inputs and historical reports remain bound to their original identities. |
| R24–R26 | Exact assembled-parent review/proof, independent contributions, parent publication/readiness gates, and all-independent completion without an empty PR. S11 has F2; S12 provides the complementary combined-outcome path. |
| R27 | Canonical protocol, all seven changed consuming skills, unchanged surrounding identity/storage/publication safeguards, controller callers and error paths, and all 17 distributed protocol references. |
| R28–R29 | README slicing link, mixed-plan/open-PR-change/final-parent how-to, and FAQ separation of child completion, integration, parent verification, CI, approvals, and merge authority. |
| R30 | All six existing scenario-document extensions, full S1–S14 procedure, disposable Git/tracker builder, effect assertions, genuine-verification prerequisites, race/restart variants, withheld-oracle instructions, and simulation labels. F2 affects one mandatory scenario. |

## Checks and limitations

The default-sandbox probe attempted a disposable sibling directory under `/private/var/tmp/p2p-issue33-verifier-8eh45dgs/first-candidate` using `tempfile.TemporaryDirectory`. It raised `PermissionError(1, 'Operation not permitted')`. No escalation was requested. Candidate, base, records, and source repository were not modified. Diagnostics used `/private/tmp/p2p-review-epic-delivery/`; no live GitHub operation or credential access occurred.

Inspection used `diff -qr base candidate` followed by complete focused diffs and surrounding code reads for every changed implementation, documentation, and scenario file. Both supplied trees lack `.git`; their full content was checked against the retained manifests rather than against the mutable source checkout. The comparison SHA is the enclosing workflow's fixed supplied identity; this context verified its reconstructed manifest content.

Commands run from the fixed candidate, with `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp`:

- `/opt/homebrew/bin/python3.14 -m unittest discover -s checks -p 'test_p2p_delivery.py' -k child`: 4 tests passed in 28.456 seconds.
- The same command with `-k integration_missing`: 1 test passed in 0.805 seconds.
- With `-k parent_uses`: 1 test passed in 10.451 seconds.
- With `-k success_source`: 1 test passed in 7.888 seconds.
- `python3 checks/epic_delivery_fixture.py prepare S4 /private/tmp/p2p-review-epic-delivery/s4-transfer`: prepared the unchanged approval-transfer example. Direct `routing`/`routing_records` inspection showed the omitted receipt.
- `/opt/homebrew/bin/python3.14 /private/tmp/p2p-review-epic-delivery/approval-transfer-check.py`: reproduced missing transfer and unchanged successful controller status after receipt deletion.
- `/opt/homebrew/bin/python3.14 checks/epic_delivery_fixture.py prepare S11 /private/tmp/p2p-review-epic-delivery/s11-interaction`, followed by the four checks and independent child assertion documented above: observed exits `0, 0, 0, 1, 1`.
- `/opt/homebrew/bin/python3.14 /private/tmp/p2p-review-epic-delivery/stability-check.py`: complete candidate/base identity checks passed; all 17 protocol references match canonical SHA-256 `c916e48be9de29f423716518dc290a64b9c667bdf42b40da87dc346853957b43`.

The first focused test attempt used system Python 3.9.6 and failed to import `tomllib` in three tests. The controller documents Python 3.11 or newer. The supported Python 3.14 rerun passed; the unsupported-environment failure is not a product finding. Codex version probes printed a denied PATH-alias warning; no actual model stage was launched by the explicit fixture transport.

The implementation report is honestly PARTIAL pending fresh S1–S14 actor observations. The checks and execution procedures exist and were inspected. I did not label pending runs as missing test paths or perform a second exhaustive acceptance proof. Actual installed-skill behavior across all scenario variants, retarget mutations, and restart races remains for the enclosing execution/evidence workflow. Controlled tracker behavior does not establish live GitHub compatibility. No live-service validation was performed or required here.

## Handoff

F1 requires an in-scope transfer correction for R3/R4. F2 requires an in-scope scenario correction for R24/R30. No acceptance-contract amendment is needed. Neither correction was applied during review.

Scratch report and evidence: `/private/tmp/p2p-review-epic-delivery/review.md` and adjacent named scripts/logs. Proposed durable report destination: `.p2p/work/epic-delivery-strategy/review.md`. The enclosing workflow must save and reread this exact report and retain its referenced evidence under the history/transfer rules; durable repository storage is pending.

Review only; acceptance proof and merge readiness are separate.

## Next steps

1. Invoke `/implement-contract work/epic-delivery-strategy.md; findings .p2p/work/epic-delivery-strategy/review.md` after the enclosing workflow saves this report. Correct F1 and F2 without changing the approved contract.
2. Capture the changed candidate against `5e369c1b45ba817b8add6b20a9b7b1c97898fa12`, refresh full `/review-implementation work/epic-delivery-strategy.md`, and run full `/prove work/epic-delivery-strategy.md` for that exact candidate. Retain the corrected transfer/S11 checks and all required independent S1–S14 observations; earlier reports remain historical.
