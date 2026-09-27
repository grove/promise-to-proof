# CHANGES NEEDED: delivery review report contract

Contract: `work/delivery-review-report-contract.md`, revision v2; SHA-256 `4b938335d31490f366ea712b2393dc10f4695246b96b5560c15d40257ce03316`

Candidate: `snapshot:sha256:ddce1e6befec6c3c226e34dfa936ffdae14a5d17ddaa5f72a03f34903d3093ee`; recoverable manifest: `.p2p/work/delivery-review-report-contract/candidate.json`

Comparison: base `a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412`; validated snapshot contains the candidate product tree and contract, with `.p2p/` excluded.

Stability: candidate key, comparison base, contract path, and contract digest matched before and after review.

Coverage: R1 and R2, full work item. Inspected review prompt, schema, receipt, dispatch, persistence, rendering, readback, status/resume paths, tests, and callers. Compared implementation, repair, and proof schemas with the base. Contract explicitly leaves semantic observation quality to review and proof.

## Contract fidelity

R1: The review prompt asks for a substantive observation per requirement; review rows contain only `id` and `observation`, and receipt rejects blank observations. The controller does not score semantic quality, as required.

R2: Review reports are limited to `REVIEWED`, `CHANGES NEEDED`, or `BLOCKED`. Receipt rejects extra fields and review-row verdict/evidence fields; `REVIEWED` requires empty findings and gaps, and `CHANGES NEEDED` requires a finding. Saved review Markdown is rendered from structured fields. Free-text `details` is rejected.

## Scope and simplicity

No material scope findings. The change stays within the review report boundary.

## Engineering quality

**F1 — Persisted review compatibility; R2 and the acceptance protocol’s durable-record/resume rules.** In [p2p_delivery.py](/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v3/skills/productivity/deliver-issue/scripts/p2p_delivery.py:534), `read_report` always renders review Markdown using the new structured format and compares it with the saved `review.md`. A `delivery/v1` record created before this change saved the review’s free-text `details` as `review.md`, so an intact prior review report fails readback. Both `run()` and `status` call `read_report` before proceeding; the legacy fallback in `complete()` at line 552 cannot help because readback fails first. Resuming an interrupted older delivery can therefore block with “canonical report content changed or lost.” Preserve legacy readback for the old report shape, or explicitly migrate/invalidate it, and cover status/resume with a legacy-record check.

## Checks and limitations

- Workspace probe: create/read/delete succeeded in the writable cwd. Candidate-directory write probe was denied with `PermissionError`; no candidate probe file was created.
- Candidate validation passed before and after review using the requested `p2p_filesystem.py validate` command. Candidate key, comparison base, and contract SHA-256 matched the expected identities.
- Compared `report_schema()` at the base with current schemas: implementation, repair, and proof JSON schemas are identical.
- Required controller suite passed: **25 tests**, `OK`. Python: `/opt/homebrew/opt/python@3.14/bin/python3.14`, version 3.14.7, macOS 26.6.2 arm64. The fixture run emitted PATH-alias setup warnings; assertions passed.
- The suite covers prompt wording, blank observations, review-row shape, structured-finding contradiction, free-text details, unsupported status, and report retrieval. Its fake transport establishes controller behavior only; it does not establish live-host stage behavior.
- No historical review or proof reports were used.

## Handoff

F1 affects R2 and persisted-record compatibility. Route it to `/implement-contract` within the existing agreement.

Report storage: proposed `.p2p/work/delivery-review-report-contract/review.md`; storage pending in this read-only review stage.

Review only; acceptance proof and merge readiness are separate.

## Next steps

1. `/implement-contract work/delivery-review-report-contract.md; findings .p2p/work/delivery-review-report-contract/review.md`
2. After correction, capture the changed candidate and refresh full review and proof against that exact candidate.