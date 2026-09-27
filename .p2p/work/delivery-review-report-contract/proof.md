# PROVEN: delivery review report contract

Requirements: 3/3  
Counterexamples tested: 9  
Contract: `work/delivery-review-report-contract.md`, revision v3  
Contract snapshot: SHA-256 `b490dc25a68ba6521282128bcf60bc3f77e8a11b907b0c9b385402fa230677cb`  
Candidate: `snapshot:sha256:049685d89b12994ec0ba84cf9bc451badba0de16c147c5e911a093a0f83f6d31`  
Comparison base: `18bab308a297b9af978d6dcf3e1107cd5eaedce5`
Candidate stability: unchanged; before/after validation matched the same recorded snapshot  
Contract stability: unchanged; before/after SHA-256 matched  
Verification context: Candidate root `/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-report-contract-candidate-v6`; Python 3.14; requested `TMPDIR`, `PYTHONPYCACHEPREFIX`, and `PYTHONDONTWRITEBYTECODE` settings. Suite output included sandbox PATH-alias warnings; tests passed.

## Outcome

The v3 contract reconciles with its linked review skill. The skill requires complete review coverage, three review axes, findings and handoff, checks and limitations, a review-only statement, and numbered next steps. The contract specifies how the controller validates structured inputs and renders those required sections. Its boundary that the controller checks structure and nonblank text, while review and proof assess meaning, is consistent with the skill.

The candidate is the exact recorded working-tree snapshot. Its comparison base is `18bab308a297b9af978d6dcf3e1107cd5eaedce5`, also the candidate’s `HEAD`. Comparing the captured snapshot with that base yielded exactly:

- `checks/test_p2p_delivery.py`
- `skills/productivity/deliver-issue/scripts/p2p_delivery.py`
- `work/delivery-review-report-contract.md`

The renderer derives included scope from the base and current snapshots. Fixture evidence checks that the rendered comparison includes the expected fixture paths and candidate identity. This establishes controller behavior through fixtures, not live-host behavior.

Checks run:

- Before and after: `/opt/homebrew/opt/python@3.14/bin/python3.14 skills/productivity/deliver-issue/scripts/p2p_filesystem.py --repo /Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-report-contract-candidate-v6 validate work/delivery-review-report-contract.md --base 18bab308a297b9af978d6dcf3e1107cd5eaedce5` — both validations passed; after-validation confirmed the expected candidate key and base.
- `/opt/homebrew/opt/python@3.14/bin/python3.14 -m unittest checks.test_p2p_delivery -v` — 35 tests passed.
- `git diff --check 18bab308a297b9af978d6dcf3e1107cd5eaedce5` — passed.

The suite log is retained at `/private/tmp/p2p-delivery-report-contract-v6-proof-scratch/unittest.log`; validation output is at `/private/tmp/p2p-delivery-report-contract-v6-proof-scratch/validate-after.json`. The contract, binding skill, and candidate snapshot matched their captured identities after verification.

## Requirement verdicts

| ID | Observation and oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | The review prompt requests a substantive observation for every requirement; receipt rejects blank observations and review rows carrying proof verdicts. This matches the contract’s explicit boundary: receipt validates structure and nonblank text, while review/proof assess meaning. | `checks.test_p2p_delivery.DeliveryTests.test_review_prompt_requires_substantive_observations`, `test_review_rejects_blank_observation`, and `test_review_rejects_proof_verdict_at_receipt`; source in `p2p_delivery.py` stage prompt and receipt validation. Full suite log above. | proven |
| R2 | Receipt rejects unsupported outcomes, extra/free-text fields and contradictory status/findings. It enforces status relationships and required structured fields. The renderer builds the complete review report from validated data and controller identities, including comparison base and included scope. Fixture assertions check all required headings, review-only text, candidate identity, and included scope. | `checks.test_p2p_delivery.DeliveryTests.test_review_rejects_unsupported_status`, `test_review_rejects_free_text_status_conflict`, `test_reviewed_report_cannot_contain_findings`, and `test_success_source_preservation_and_retrieval`; source in `p2p_delivery.py` `review_markdown`, `stage`, and `read_report`. Candidate/base scope independently compared as listed above. | proven |
| R3 | A `BLOCKED` review renders its missing input and expected result, stops before proof or repair, and remains blocked on resume. A `plan-acceptance` finding also stops before proof or automatic repair. These outcomes match the contract’s state and handoff rules. | `checks.test_p2p_delivery.DeliveryTests.test_blocked_review_stops_before_proof_and_repair` and `test_plan_acceptance_handoff_stops_before_proof_and_repair`; source in `p2p_delivery.py` `Delivery.run()`. Full suite log above. | proven |

**Counterexamples tested (fixture evidence):** blank observation; proof verdict on review row; unsupported status; free-text/status conflict; `REVIEWED` with findings; incomplete coverage/evidence; `BLOCKED` initial run and resume; `plan-acceptance` handoff; complete report sections, candidate identity, and included comparison scope.

## Unresolved gaps

- None for R1–R3. Fixture transport does not establish live-host behavior, which the contract excludes from fixture proof.

## Repairs needed

- None

Fresh `/prove` is required after any repair.  
Refresh `/review-implementation` for the changed candidate as a separate phase.

Next steps:

1. Acceptance evidence is complete for this candidate; no further action is required unless publication is wanted.

Durable evidence: the unedited host transcript is at `evidence/host/proof-v6-final.jsonl`; the complete unittest output is at `evidence/host/proof-v6-unittest.log`. The scratch paths in the original host report were staging paths.
