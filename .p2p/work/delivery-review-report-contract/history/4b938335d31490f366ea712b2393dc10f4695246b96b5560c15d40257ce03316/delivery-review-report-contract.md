# Acceptance contract: delivery review report contract

Contract revision: v2
Source: [Review implementation skill](../skills/productivity/review-implementation/SKILL.md)
Parent: None
Prerequisites: None

Intended outcome: The delivery controller accepts reports whose structured fields agree, rejects malformed or contradictory review results before proof, and retains readable reports derived from those fields.

Advisory learnings: None; no advisory learning register is present.

## Acceptance matrix

| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | Review implementation skill, report rules | The review prompt requires a substantive observation for each requirement. The controller accepts only review rows with an ID and nonblank observation, and rejects review verdict or proof-evidence fields. The review and proof stages judge whether observations are meaningful. | The controller checks report structure and blank text, not semantic quality. A nonblank placeholder such as `x` can pass receipt; it does not establish a meaningful review. | Review prompt, output schema, and report receipt | The review skill requires evidence-based findings without assigning acceptance verdicts. The proof stage independently evaluates the candidate against this contract. | `test_review_prompt_requires_substantive_observations` checks the prompt; `test_review_rejects_blank_observation` and `test_review_rejects_proof_verdict_at_receipt` check receipt behavior. | planned |
| R2 | Authorized controller report-boundary decision | The controller accepts only defined review report fields and outcomes: `REVIEWED`, `CHANGES NEEDED`, or `BLOCKED`. Review status must agree with structured findings and gaps: `REVIEWED` requires both lists to be empty, and `CHANGES NEEDED` requires a finding. The controller derives saved review text from validated structured fields. | An unsupported outcome such as `PROVEN`, agent-written review details, and other extra review fields are rejected before proof dispatch. Other stage report formats remain unchanged. | Review report schema, receipt, and saved report rendering | The review skill defines the allowed outcomes. The controller's structured status and findings checks decide whether review can proceed. Derived review text cannot override those fields. | `test_review_rejects_unsupported_status` and `test_review_rejects_free_text_status_conflict` verify rejection before storage or proof dispatch; `test_reviewed_report_cannot_contain_findings` checks structured contradiction; `test_success_source_preservation_and_retrieval` checks the full path. | planned |

## Unresolved gaps

None.

## Open questions

None.

## Out of scope

- Having the controller score the semantic quality of review observations. The review and proof stages own that judgment.
- Changing proof acceptance, delivery limits, repair allowance, or normal execution policy beyond the report format.
- Revising the approved Phase 4 v2 contract or running additional comparison episodes.

## Change notes

- v2: R1 clarifies that the controller checks review structure and nonblank observations while review and proof judge meaning. R2 rejects free-text review fields and derives saved review text from structured data. The user authorized this boundary on 2026-09-26 with "Just make it work. I approve." The v1 text is preserved in `.p2p/work/delivery-review-report-contract/history/4f892ad68cfb47492c3e9066ae64c614bef3dda5a950a439b161dde04cc5fc63/delivery-review-report-contract.md`.
- v2 clarification: Review outcomes are limited to the review skill's `REVIEWED`, `CHANGES NEEDED`, and `BLOCKED` values. Review found that the controller also accepted `PROVEN`; this clarification records the existing skill boundary and adds a receipt check. The prior v2 text is preserved in `.p2p/work/delivery-review-report-contract/history/3f7baf42d4ec009e43faf74f2bd0f0943a3f205d34e76b9d1ab01af07c915baf/delivery-review-report-contract.md`.
- v1: Initial standalone contract for the authorized controller report-format fix. This work does not amend the Phase 4 pilot agreement.

## Implementation handoff

Implement the report schema, receipt checks, and report rendering required by R1 and R2. Preserve the existing delivery and proof policies. Capture the exact candidate before review and proof.

## Proof handoff

Evaluate R1 and R2 against this contract revision and one fixed candidate. Retain actual commands, observations, and environment. Fixture transport does not establish live-host behavior.

Next steps:

1. Implement and test the v2 report boundary.
2. Capture the exact candidate and run independent review and proof against it.
