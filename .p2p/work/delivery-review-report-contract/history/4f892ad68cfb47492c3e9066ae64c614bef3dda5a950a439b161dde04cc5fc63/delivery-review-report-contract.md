# Acceptance contract: delivery review report contract

Contract revision: v1
Source: [Review implementation skill](../skills/productivity/review-implementation/SKILL.md)
Parent: None
Prerequisites: None

Intended outcome: The delivery controller accepts reports that follow the review role, rejects contradictory review results when received, and preserves the separate full proof requirement.

Advisory learnings: None; no advisory learning register is present.

## Acceptance matrix

| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | Review implementation skill, report rules | Review reports cover each contract requirement exactly once with an ID and substantive observation, carry findings and gaps at report level, and contain no per-requirement verdict or proof-evidence fields. | A proof-style verdict such as `proven` in a review row is invalid. Proof reports keep their existing verdict and evidence requirements. | Review stage output schema and report receipt | Review skill says review does not issue acceptance verdicts; `/prove` owns them. | `test_review_rejects_proof_verdict_at_receipt` rejects a proof-style row before proof dispatch; `test_success_source_preservation_and_retrieval` exercises a valid review report through the full controller path. | planned |
| R2 | Authorized controller bug-fix request | A `REVIEWED` report with any findings is rejected at receipt before the controller stores it as a completed review or dispatches proof. | A clean `REVIEWED` report with full coverage and no findings or gaps may proceed to the unchanged full proof stage. | Review stage report validation and stage dispatch | `REVIEWED` means no material change-required findings; the structured finding list must agree with that status. | `test_reviewed_report_cannot_contain_findings` asserts the controller blocks the contradiction before proof dispatch. | planned |

## Unresolved gaps

None.

## Open questions

None.

## Out of scope

- Changing proof acceptance, delivery limits, repair allowance, or normal execution policy beyond the review report format.
- Revising the approved Phase 4 v2 contract or running additional comparison episodes.

## Change notes

- v1: Initial standalone contract for the authorized controller report-format fix. This work does not amend the Phase 4 pilot agreement.

## Implementation handoff

The implementation is already committed. Capture the exact candidate after this contract is approved. Repair only if review or proof finds a gap and repair is authorized.

## Proof handoff

Evaluate R1 and R2 against one fixed candidate and this exact contract revision. Retain the actual command, fixture-backed observations, and environment. Fixture transport does not establish live-host behavior.

Next steps:

1. Review and approve this contract or request edits.
2. Capture the exact candidate and comparison base, then run independent review and proof against the matching identities.
