# NOT PROVEN: delivery review report contract

Requirements: 2/3 proven  
Counterexamples tested: 8  
Contract: `work/delivery-review-report-contract.md`, v3  
Contract snapshot: candidate file, SHA-256 `b490dc25a68ba6521282128bcf60bc3f77e8a11b907b0c9b385402fa230677cb`  
Candidate: `snapshot:sha256:ba332bf48e9ff1a00853a6b6ecc3d604016cb2be5c2ce5354c8b1ac8962610f4`; comparison base `d0467b7bbaed2078e7e677b6ce3be407d4fb2058`  
Candidate stability: unchanged; the before and after validations confirmed the same snapshot key  
Contract stability: unchanged; its SHA-256 matched before and after  
Verification context: candidate root; Python 3.14. The required temp directory, `TMPDIR`, `PYTHONPYCACHEPREFIX`, and `PYTHONDONTWRITEBYTECODE` settings were used. Fixture tests ran in disposable repositories; fixture transport does not establish live-host behavior.

## Outcome

R1 and R3 have credible prompt, source, and fixture-test evidence. R2 is **disproven**: reconciling the contract with the linked review skill shows the report must state the included working-tree scope. The renderer reports only the comparison base and a count of snapshot paths, so its generated report omits that required scope. The candidate stayed fixed during verification.

## Requirement verdicts

| ID | Observation and oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | The review prompt requires a substantive observation for every requirement. Receipt enforces full requirement coverage and nonblank observations, and rejects review rows containing verdicts or proof evidence. The review skill assigns acceptance proof to `/prove`, consistent with the contract’s boundary that semantic quality is judged by review and proof. | `skills/productivity/deliver-issue/scripts/p2p_delivery.py` prompt construction and receipt checks; `checks/test_p2p_delivery.py::test_review_prompt_requires_substantive_observations`, `test_review_rejects_blank_observation`, `test_review_rejects_proof_verdict_at_receipt`. Full suite passed. | proven |
| R2 | The schema accepts only structured review fields and the three supported outcomes; receipt checks status/findings consistency and rejects free-text details. The renderer emits the contract and candidate identities, sections for all three axes, checks, limitations, handoff, the review-only statement, and numbered next steps. However, the linked skill’s report template requires comparison base **and included working-tree scope**. The renderer’s `Comparison` line contains the base and snapshot-path count, not the included scope. That is a concrete omission from the required complete report. | `review-implementation/SKILL.md` report template; `p2p_delivery.py::review_markdown`; fixture assertions in `test_success_source_preservation_and_retrieval`, `test_review_rejects_free_text_status_conflict`, `test_review_rejects_unsupported_status`, and `test_reviewed_report_cannot_contain_findings`. | disproven |
| R3 | Initial `BLOCKED` review records the missing command and expected result in the rendered report and stops before proof or repair. Resume retries review and remains blocked; no proof or repair dispatch occurs. Controller exception handling persists delivery status as `BLOCKED`. A `plan-acceptance` finding also stops before proof and repair. These are fixture observations, not live-host claims. | `p2p_delivery.py::Delivery.run` and CLI exception handling; `checks/test_p2p_delivery.py::test_blocked_review_stops_before_proof_and_repair`, `test_plan_acceptance_handoff_stops_before_proof_and_repair`. | proven |

## Unresolved gaps

- **R2:** Render the included working-tree scope required by the linked review template, then verify the complete report output.

## Repairs needed

- **R2:** Add the included scope to the renderer’s comparison section using controller-known candidate data, and add an assertion that the generated report contains it. This report is returned here; it was not saved under the candidate because the candidate was kept unchanged.

Fresh `/prove` is required after any repair.  
Refresh `/review-implementation` for the changed candidate as a separate phase.

Next steps:

1. Save this proof report under `.p2p/work/delivery-review-report-contract/proof.md`, then run `/repair-gaps .p2p/work/delivery-review-report-contract/proof.md`.
2. Capture the repaired candidate and refresh its full review and proof against the same contract and comparison base.
