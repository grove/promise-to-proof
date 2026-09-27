# CHANGES NEEDED: delivery-review-report-contract

Contract: [work/delivery-review-report-contract.md](/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v4/work/delivery-review-report-contract.md), revision v2, SHA-256 `4b938335d31490f366ea712b2393dc10f4695246b96b5560c15d40257ce03316`

Candidate: `snapshot:sha256:2e5298d3e64288f72d441a2342874d4193cb1f078d8cbfe056a4ea28c6b75983`; recoverable manifest in [candidate.json](/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v4/.p2p/work/delivery-review-report-contract/candidate.json)

Comparison: base `a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412`; candidate includes changes to `checks/test_p2p_delivery.py` and `skills/productivity/deliver-issue/scripts/p2p_delivery.py`, plus the work item.

Stability: candidate key, comparison base, work-item digest, and contract digest matched before and after review. Candidate validation passed both times.

Coverage: R1 and R2; traced the review prompt, schema, receipt, persistence, dispatch, rendering, legacy readback, status/resume and repair paths, tests, and report consumers. Inspected the 127-entry manifest path/mode inventory.

## Contract fidelity

- **F1 — R2; source: [review-implementation/SKILL.md](/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v4/skills/productivity/review-implementation/SKILL.md:53).** The receipt accepts `BLOCKED` ([p2p_delivery.py](/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v4/skills/productivity/deliver-issue/scripts/p2p_delivery.py:482)), but `run()` still dispatches proof and chooses implementation repair whenever proof is `PROVEN` ([p2p_delivery.py](/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v4/skills/productivity/deliver-issue/scripts/p2p_delivery.py:613)). A blocked review caused by a necessary unknown can therefore trigger an automatic product change without an established correction. The skill defines `BLOCKED` for cases where reliable scope or a necessary fact is unavailable, and requires an exact missing-input handoff ([review-implementation/SKILL.md](/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v4/skills/productivity/review-implementation/SKILL.md:226)). The contract does not specify the blocked transition. Resolve it through `plan-acceptance`; the controller should preserve the blocker and avoid implementation repair for that status.

- **F2 — R2; source: review skill’s required report format.** The review schema permits only status, identity, requirements, findings, and gaps ([p2p_delivery.py](/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v4/skills/productivity/deliver-issue/scripts/p2p_delivery.py:183)); the renderer emits only Requirements, Findings, and Gaps ([p2p_delivery.py](/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v4/skills/productivity/deliver-issue/scripts/p2p_delivery.py:199)). The binding skill requires contract/candidate/comparison context, all three review axes, checks and limitations, handoff, and numbered next steps ([review-implementation/SKILL.md](/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v4/skills/productivity/review-implementation/SKILL.md:161)). The saved `review.md` and bundle details omit those sections. The contract must reconcile the structured-only boundary with the required report format before implementation proceeds.

## Scope and simplicity

No material findings.

## Engineering quality

No other material findings.

## Checks and limitations

- Scratch create/read/delete passed. A new-file write under the protected candidate directory was denied with `PermissionError`.
- The requested candidate validation command passed before and after review:

  ```sh
  PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/opt/python@3.14/bin/python3.14 /Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v4/skills/productivity/deliver-issue/scripts/p2p_filesystem.py --repo /Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v4 validate work/delivery-review-report-contract.md --base a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412 >/dev/null
  ```

- R1 checks are present: review rows require nonblank observations and exclude verdict/evidence fields. R2 allows exactly `REVIEWED`, `CHANGES NEEDED`, and `BLOCKED`; rejects extra fields and free-text details; requires empty findings/gaps for `REVIEWED` and a finding for `CHANGES NEEDED`. The non-review implementation, repair, and proof schemas retain the base schema.
- New review summaries are rendered from structured fields. Legacy readback derives the in-memory and bundle summary from the legacy structured report; the legacy `review.md` remains unchanged. The legacy status/resume fixture passed.
- The full requested controller suite passed: **26 tests**, 117.914 seconds. Environment: Python 3.14.7, `/opt/homebrew/opt/python@3.14/bin/python3.14`, macOS 26.6.2 arm64. The suite uses fixture transport; it does not establish live-host stage behavior. Sandbox PATH-alias warnings appeared during the run.
- No acceptance proof verdict is issued.

## Handoff

F1 and F2 return to `/plan-acceptance` because the agreement needs to define blocked-state handling and reconcile the structured report boundary with the binding report format. Authority to omit required report sections or alter the blocked handoff was not established by the inspected contract. Report storage: proposed destination `.p2p/work/delivery-review-report-contract/review.md`; storage pending.

Review only; acceptance proof and merge readiness are separate.

## Next steps

1. Save and reread this report at the proposed destination, then run `/plan-acceptance work/delivery-review-report-contract.md; amendment .p2p/work/delivery-review-report-contract/review.md` to resolve F1 and F2 and record any required authorization.
2. Resume implementation with `/implement-contract work/delivery-review-report-contract.md` only after the revised contract is approved and saved. After the candidate changes, capture it and refresh review and full proof.