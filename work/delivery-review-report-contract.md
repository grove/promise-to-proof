# Acceptance contract: delivery review report contract

Contract revision: v3
Source: [Review implementation skill](../skills/productivity/review-implementation/SKILL.md)
Parent: None
Prerequisites: None

Intended outcome: The delivery controller validates review reports, preserves the review skill's required human-readable report, and stops safely when review is blocked.

Advisory learnings: None; no advisory learning register is present.

## Acceptance matrix

| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | Review implementation skill, report rules | The review prompt requires a substantive observation for each requirement. The controller accepts only review rows with an ID and nonblank observation, and rejects review verdict or proof-evidence fields. The review and proof stages judge whether observations are meaningful. | The controller checks report structure and blank text, not semantic quality. A nonblank placeholder such as `x` can pass receipt; it does not establish a meaningful review. | Review prompt, output schema, and report receipt | The review skill requires evidence-based findings without assigning acceptance verdicts. The proof stage independently evaluates the candidate against this contract. | `test_review_prompt_requires_substantive_observations` checks the prompt; `test_review_rejects_blank_observation` and `test_review_rejects_proof_verdict_at_receipt` check receipt behavior. | planned |
| R2 | Authorized controller report-boundary decision; review implementation skill report template | The controller accepts only the defined review fields and outcomes `REVIEWED`, `CHANGES NEEDED`, or `BLOCKED`. It validates status against structured findings and gaps, then renders the complete report required by the review skill from structured data and controller-known identities. The report includes contract, candidate, comparison, stability, coverage, all three review axes, checks and limitations, handoff, the review-only statement, and numbered next steps. | `REVIEWED` requires empty findings and gaps; `CHANGES NEEDED` requires a finding. Findings identify their primary axis, evidence, consequence, smallest correction, and handoff to implementation or planning. Findings handed to `plan-acceptance` stop before proof and automatic repair until the agreement is revised and approved. `BLOCKED` requirements are in R3. Free-text details, unknown top-level fields, proof verdicts on requirements, and unsupported outcomes such as `PROVEN` are rejected. The controller checks structure and nonblank text, not review quality. | Review prompt, schema, receipt, Markdown renderer, and report readback | The review skill's report template and outcome definitions; structured fields determine status and the controller derives the saved report text. | `test_review_rejects_unsupported_status`, `test_review_rejects_free_text_status_conflict`, `test_reviewed_report_cannot_contain_findings`, and `test_success_source_preservation_and_retrieval` check receipt, routing, and rendering. | planned |
| R3 | Review implementation skill, blocked outcome and delivery handoff | A `BLOCKED` review records the exact missing input or configured command and expected result, is durably saved with the delivery state as `BLOCKED`, and stops before proof or automatic repair. Resuming that delivery does not dispatch proof or repair while the saved review remains blocked. | No claim is made that the controller resolves the missing input or decides whether it has been supplied. It must not treat blocked findings as permission to modify the candidate. | Review receipt and `Delivery.run()` state transitions | The saved structured report and delivery record retain the blocker; attempt records show no proof or repair dispatch after the blocked review. | `test_blocked_review_stops_before_proof_and_repair` checks initial run and resume; report assertions check the missing input and expected result in the rendered handoff. | planned |

## Unresolved gaps

None.

## Open questions

None.

## Out of scope

- Having the controller score the semantic quality of review observations or findings.
- Changing proof acceptance, delivery limits, or repair behavior for non-blocked reviews.
- Proving live-host behavior through fixture transport.

## Change notes

- v3: R2 now requires the complete report template defined by the bound review skill, represented by validated structured fields. R3 defines the `BLOCKED` state transition so a necessary unknown cannot trigger proof or automatic repair. This implements the user's standing authorization to make the delivery report contract work, given on 2026-09-26: "Just make it work. I approve." The exact v2 text is preserved at `.p2p/work/delivery-review-report-contract/history/4b938335d31490f366ea712b2393dc10f4695246b96b5560c15d40257ce03316/delivery-review-report-contract.md`.
- v2: R1 clarifies that the controller checks review structure and nonblank observations while review and proof judge meaning. R2 rejects free-text review fields and derives saved review text from structured data. The v1 text is preserved at `.p2p/work/delivery-review-report-contract/history/4f892ad68cfb47492c3e9066ae64c614bef3dda5a950a439b161dde04cc5fc63/delivery-review-report-contract.md`.
- v1: Initial standalone contract for the authorized controller report-format fix. This work does not amend the Phase 4 pilot agreement.

## Implementation handoff

Implement the report schema, receipt checks, complete report rendering, and blocked-review stop required by R1–R3. Preserve existing delivery and proof policies outside these requirements. Capture the exact candidate before review and proof.

## Proof handoff

Evaluate R1–R3 against this contract revision and one fixed candidate. Retain actual commands, observations, and environment. Fixture transport does not establish live-host behavior.

Next steps:

1. Implement and test the v3 report format and blocked-review state transition.
2. Capture one exact candidate and run independent review and proof against it.
