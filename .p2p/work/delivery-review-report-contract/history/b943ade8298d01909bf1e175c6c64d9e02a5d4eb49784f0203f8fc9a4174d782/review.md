# CHANGES NEEDED: delivery review report contract

Contract: `/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v2/work/delivery-review-report-contract.md`, revision v2, SHA-256 `3f7baf42d4ec009e43faf74f2bd0f0943a3f205d34e76b9d1ab01af07c915baf`  
Binding source: `skills/productivity/review-implementation/SKILL.md`, SHA-256 `e5b8ade59142779914780d5ec35acafc9a087fd3087904c43d8e356ffc3005b7`  
Candidate: `snapshot:sha256:441855d0b43448858285af22c319701a8303ac8918694d158708c982ca99beea`; recoverable manifest: `/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v2/.p2p/work/delivery-review-report-contract/candidate.json`  
Comparison: `a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412`; full snapshot path and mode inventory reviewed, with `.p2p/` excluded.  
Stability: candidate and contract were unchanged. Validation passed before and after review; the candidate key, contract digest, binding source digest, and comparison base match the expected identities.

Coverage: R1 and R2 reviewed against the full candidate. For R1, the prompt requests substantive observations; receipt requires complete requirement coverage, nonblank observations, and rows containing only `id` and `observation`. The controller does not assess observation quality, as the contract assigns that judgment to review and proof. For R2, receipt restricts top-level fields, enforces the stated `REVIEWED` and `CHANGES NEEDED` findings/gaps rules, rejects free-text review details, and derives and rechecks rendered review text. F1 identifies a remaining status validation gap.

## Contract fidelity

**F1 — R2, malformed review status is accepted.** In `skills/productivity/deliver-issue/scripts/p2p_delivery.py:187-194, 487-496`, the review schema accepts any string for `status`, and receipt checks consistency only for `REVIEWED` and `CHANGES NEEDED`. A fixture-shaped transport returned an otherwise valid review with status `PROVEN`, empty findings, and empty gaps. Receipt accepted it, and the controller dispatched proof before attempting repair. `PROVEN` is not an outcome defined by the review skill, so this malformed review report should be rejected before proof. Validate review status against the skill’s outcomes (`REVIEWED`, `CHANGES NEEDED`, `BLOCKED`) and add a fixture asserting an unknown status prevents proof dispatch.

## Scope and simplicity

No material findings.

## Engineering quality

No separate finding. F1 also concerns input validation at the stage boundary.

## Checks and limitations

- Write-boundary probe passed: create/read/delete in the writable cwd succeeded; creating a probe under the candidate’s `.p2p/work/delivery-review-report-contract/` failed with `PermissionError`.
- Ran the requested controller suite with the exact command: `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp/p2p-delivery-review-report-contract-v2-review-scratch /opt/homebrew/opt/python@3.14/bin/python3.14 -m unittest discover -s /Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v2/checks -p 'test_p2p_delivery.py' -v`. Result: **24 tests passed** in 111.810 seconds. Python 3.14.7, macOS 26.6.2 arm64. The run emitted PATH alias permission warnings; no tests failed.
- The suite covers substantive-observation prompting, blank-observation rejection, structured review findings, review verdict rejection, and free-text status conflict rejection. The status probe above used fixture transport. These checks establish controller behavior only, not live-host stage behavior.
- Confirmed implementation, repair, and proof retain their prior field sets and value shapes: `status`, `input_identity_json`, `details`, `requirements` with verdict/observation/evidence, and `gaps`. The review-specific schema and renderer do not change those stage formats.
- No acceptance proof verdict was issued.

## Handoff

Send F1/R2 to `/implement-contract`; it is an in-scope controller fix. Report storage is pending. The enclosing workflow should save this report as `/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v2/.p2p/work/delivery-review-report-contract/review.md`.

Review only; acceptance proof and merge readiness are separate.

## Next steps

1. Run `/implement-contract work/delivery-review-report-contract.md; findings .p2p/work/delivery-review-report-contract/review.md` to reject statuses outside the review skill’s outcomes and add a fixture for rejection before proof dispatch.
2. Capture the changed candidate, then run a fresh full review and `/prove work/delivery-review-report-contract.md; candidate <new exact candidate key>` against that same candidate.