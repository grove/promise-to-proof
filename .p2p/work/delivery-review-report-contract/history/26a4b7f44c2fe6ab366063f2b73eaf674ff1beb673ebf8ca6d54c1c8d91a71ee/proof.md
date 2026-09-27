# PROVEN: delivery review report contract

Requirements: 2/2  
Counterexamples tested: 8 rejected inputs, plus one allowed placeholder boundary  
Contract: `work/delivery-review-report-contract.md`, revision v2  
Contract snapshot: SHA-256 `4b938335d31490f366ea712b2393dc10f4695246b96b5560c15d40257ce03316`  
Candidate: `snapshot:sha256:2e5298d3e64288f72d441a2342874d4193cb1f078d8cbfe056a4ea28c6b75983`  
Comparison base: `a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412`  
Candidate stability: unchanged; validation passed before and after checks  
Contract stability: unchanged; digest matched before and after checks  
Verification context: Python 3.14.7, macOS 26.6.2 arm64; cwd and `TMPDIR` were `/private/tmp/p2p-delivery-review-report-contract-v4-proof-scratch`.

## Outcome

R1 and R2 are proven for this candidate. The required validation command passed before and after verification. Both times, the work-item hash, candidate key, comparison base, and binding-input identity matched the expected values; validation also confirmed the candidate snapshot remained unchanged.

The scratch boundary probe passed create/read/delete. A new-file write under `.p2p/work/delivery-review-report-contract/` failed with `PermissionError`.

The controller suite passed: `Ran 26 tests in 118.965s`, `OK`, exit 0. Its `FakeTransport` fixtures establish controller behavior only. No live model was invoked, so this run does not establish that a model will follow the substantive-observation instruction.

## Requirement verdicts

| ID | Observation and oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | The review prompt requests a substantive observation for every requirement. The schema permits only `id` and `observation` in review rows, and receipt rejects blank observations and extra verdict/evidence fields. The prompt and receipt match the contract’s boundary: meaningfulness is judged by review/proof stages, not scored by the controller. | `p2p_delivery.py` `stage`, `report_schema`, and receipt checks; full suite cases `test_review_prompt_requires_substantive_observations`, `test_review_rejects_blank_observation`, `test_review_rejects_proof_verdict_at_receipt`; controlled fixture probe confirmed an `evidence` row field is rejected before report storage or proof dispatch. A separate fixture probe confirmed `x` passes structural receipt while the substantive prompt remains present. | proven |
| R2 | Review output has a strict top-level field set and allows only `REVIEWED`, `CHANGES NEEDED`, or `BLOCKED`. Receipt rejects `PROVEN`, extra free-text `details`, row verdict/evidence fields, `REVIEWED` with findings or gaps, and `CHANGES NEEDED` without a finding before storing the review or dispatching proof. Saved review text is rendered from structured fields. Legacy review text remains readable by status/resume; the normalized summary is derived from structured fields. | Full suite cases `test_review_rejects_unsupported_status`, `test_review_rejects_free_text_status_conflict`, `test_review_rejects_proof_verdict_at_receipt`, `test_reviewed_report_cannot_contain_findings`, and `test_legacy_review_readback_uses_structured_summary`; controlled fixture probes rejected row evidence, `REVIEWED` with a gap, and `CHANGES NEEDED` without a finding before storage or proof dispatch. The legacy case passed both status and resume and confirmed the acceptance bundle summary excludes old free text. An AST comparison of generated schemas against the comparison-base version found implementation, repair, and proof schemas identical; each had canonical schema SHA-256 `b29bf22f2b13df9d761f8d4f788adc248623070c8c59a0f1c02f5fa1f977e961`. | proven |

## Unresolved gaps

- None within R1 and R2. Fixture transport does not establish live-model compliance or semantic judgment beyond the supplied prompt and stage instructions.

## Repairs needed

- None.

Fresh `/prove` is required after any repair. Refresh `/review-implementation` for a changed candidate as a separate phase.

Next steps:

1. The review report was not inspected in this verification. Check separately for a full `REVIEWED` report matching this candidate, contract digest, and comparison base. If absent, run `/review-implementation work/delivery-review-report-contract.md; candidate .p2p/work/delivery-review-report-contract/candidate.json against a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412`.