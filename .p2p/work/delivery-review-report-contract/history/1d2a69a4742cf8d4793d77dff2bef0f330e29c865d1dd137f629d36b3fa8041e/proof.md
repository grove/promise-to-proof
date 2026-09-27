# NOT PROVEN: delivery review report contract

Requirements: 1/2  
Counterexamples tested: 3 contract-focused counterexamples  
Contract: [`work/delivery-review-report-contract.md`](</Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate/work/delivery-review-report-contract.md:3>), revision v1  
Contract snapshot: SHA-256 `4f892ad68cfb47492c3e9066ae64c614bef3dda5a950a439b161dde04cc5fc63`; source binding `skills/productivity/review-implementation/SKILL.md`, SHA-256 `e5b8ade59142779914780d5ec35acafc9a087fd3087904c43d8e356ffc3005b7`  
Parent context: None  
Candidate: `snapshot:sha256:e5d92bc5f1600e0f6d66ac585d4959b1c75c384c7969b498c9f266a95994d14b`; comparison base `a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412`  
Candidate stability: unchanged; candidate validation succeeded before and after checks, with matching snapshot key and comparison base  
Contract stability: unchanged; pre-check and post-check SHA-256 matched  
Verification context: macOS Darwin 25.6.0 arm64, Python 3.14.7, cwd `/private/tmp/p2p-delivery-review-report-contract-proof-scratch`. Fixture temp data used `TMPDIR` in that directory. No live-host stage run.

## Outcome

R2 is proven at the controller receipt and dispatch seam. A contradictory `REVIEWED` report was rejected before it was stored as a completed review or proof was dispatched. The clean fixture path proceeded through the separate proof stage.

R1 is disproven: the receipt accepts and stores a `REVIEWED` report whose per-requirement observation is only `"x"`, then reserves proof dispatch. The controller checks that observations are nonblank, not that they are substantive. Its review row schema otherwise permits only `id` and `observation`, and places `findings` and `gaps` at report level. The source skill assigns acceptance verdicts to `/prove` ([review skill](</Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate/skills/productivity/review-implementation/SKILL.md:159>)); the controller’s row shape follows that rule.

Validation command, run before and after checks, exited successfully both times:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 /Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate/skills/productivity/deliver-issue/scripts/p2p_filesystem.py --repo /Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate validate work/delivery-review-report-contract.md --base a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412 >/dev/null
```

The contract hash was also checked with `sha256sum` before and after; both matched the recorded SHA-256 above.

Controller suite command and result:

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp/p2p-delivery-review-report-contract-proof-scratch python3 -m unittest discover -s /Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate/checks -p 'test_p2p_delivery.py' -v
```

Result: `Ran 21 tests in 141.476s — OK`. The run emitted nonfatal PATH-alias warnings.

The fixture tests are explicitly controller-transport tests. The contract and controller docs state they do not establish live-host behavior ([contract](</Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate/work/delivery-review-report-contract.md:42>), [controller docs](</Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate/docs/p2p-delivery-controller.md:113>)). No live-host behavior is claimed here.

## Requirement verdicts

| ID | Observation and oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | The review schema restricts rows to `id` and `observation`; receipt checks exact requirement-ID coverage and rejects extra row keys. However, it accepts any nonblank observation. A scratch-only fixture probe replaced the review row observation with `"x"` and asserted that the saved review contained `"x"` and that proof dispatch was reserved. Both assertions passed. This violates R1’s substantive-observation promise. | [Controller schema](</Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate/skills/productivity/deliver-issue/scripts/p2p_delivery.py:183>), [receipt checks](</Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate/skills/productivity/deliver-issue/scripts/p2p_delivery.py:450>); `test_review_rejects_proof_verdict_at_receipt` also injects `verdict: proven` and asserts review blocks without proof dispatch ([test](</Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate/checks/test_p2p_delivery.py:211>)). The report-level `findings` and `gaps` are in the root schema ([schema](</Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate/skills/productivity/deliver-issue/scripts/p2p_delivery.py:187>)). | disproven |
| R2 | The `REVIEWED` plus findings fixture was rejected. A scratch-only receipt probe asserted there was no completed review in `state.reports`, the review attempt remained uncompleted, and no proof call occurred; all passed. The clean success fixture asserted `REVIEWED_AND_PROVEN` and the stage order `implementation, review, proof`. | [Receipt validation precedes report persistence](</Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate/skills/productivity/deliver-issue/scripts/p2p_delivery.py:458>), [persistence follows validation](</Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate/skills/productivity/deliver-issue/scripts/p2p_delivery.py:473>); `test_reviewed_report_cannot_contain_findings` ([test](</Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate/checks/test_p2p_delivery.py:218>)) and `test_success_source_preservation_and_retrieval` ([test](</Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate/checks/test_p2p_delivery.py:131>)). | proven |

The three contract-focused counterexamples were: a proof verdict in a review row, findings on a `REVIEWED` report, and a non-substantive `"x"` observation. The suite and direct probes exercised fixture transport only.

## Unresolved gaps

- R1: Receipt validation treats any nonblank string as a substantive observation. The `"x"` counterexample was stored as a completed review, and proof dispatch was reserved.

## Repairs needed

- R1: Make the substantive-observation check independently decidable at receipt, and reject the `"x"` counterexample before storing a completed review or dispatching proof. Preserve the review-only row shape and the valid clean-review-to-proof path.

Fresh `/prove` is required after any repair.  
Refresh `/review-implementation` for the changed candidate as a separate phase.

Next steps:

1. Run `/repair-gaps <saved proof>` scoped to R1.
2. After repair, capture the changed candidate, refresh review, and run fresh proof. Rerun the recorded controller suite; expect it to pass and the added `"x"` boundary assertion to show rejection before review storage and proof dispatch.