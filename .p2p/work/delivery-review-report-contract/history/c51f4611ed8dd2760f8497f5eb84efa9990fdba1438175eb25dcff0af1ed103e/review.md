# CHANGES NEEDED: work/delivery-review-report-contract.md

Contract: `work/delivery-review-report-contract.md`, v1, SHA-256 `4f892ad68cfb47492c3e9066ae64c614bef3dda5a950a439b161dde04cc5fc63`

Candidate: `snapshot:sha256:e5d92bc5f1600e0f6d66ac585d4959b1c75c384c7969b498c9f266a95994d14b`; recoverable record at `/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate/.p2p/work/delivery-review-report-contract/candidate.json`

Comparison: full base `a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412`; 127-path snapshot, with `.p2p/` excluded. The product diff changes `checks/test_p2p_delivery.py` and `skills/productivity/deliver-issue/scripts/p2p_delivery.py`, and includes the untracked contract.

Stability: candidate, contract, and bound review skill remained unchanged. Validation passed before and after review.

Coverage: full R1 and R2. Inspected the contract and source skill, controller schema, prompt, receipt, persistence and dispatch paths, changed tests, controller documentation, and acceptance protocol. No parent contract or requirement omissions.

## Contract fidelity

**F1 — R2: the receipt check trusts structured findings even when the full report contradicts them.** In [p2p_delivery.py](/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate/skills/productivity/deliver-issue/scripts/p2p_delivery.py:455), validation checks `status` against the structured `findings` and `gaps`. The prompt says `details` contains the full human report, but the controller saves that text verbatim at lines 474–475 without checking it against those fields. A scratch-only fixture reproduction returned `status: REVIEWED`, `findings: []`, and details headed `CHANGES NEEDED` with finding F1. The controller persisted the review, dispatched proof, and returned success. This violates R2. Make the saved human report consistent with the validated fields—by deriving it from them or rejecting contradictions—before persistence and proof dispatch; add a fixture case for this mismatch.

**F2 — R1: a nonempty placeholder passes as a substantive per-requirement observation.** [p2p_delivery.py](/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate/skills/productivity/deliver-issue/scripts/p2p_delivery.py:450) rejects only blank observations. The review-specific prompt at lines 409–426 specifies row fields but omits the substantive-observation instruction used for other stages. A scratch-only fixture reproduction changed the review row observation to `x`; the controller stored it, dispatched proof, and returned `REVIEWED_AND_PROVEN`. This violates R1’s substantive-observation requirement. Restore that instruction for review rows and reject obvious placeholder observations at receipt; add a fixture case.

## Scope and simplicity

No material findings.

## Engineering quality

No separate material findings. F1 and F2 identify missing receipt checks and corresponding fixture cases.

## Checks and limitations

- `PYTHONDONTWRITEBYTECODE=1 python3 <candidate>/skills/productivity/deliver-issue/scripts/p2p_filesystem.py --repo <candidate> validate work/delivery-review-report-contract.md --base a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412 >/dev/null` passed before and after review. The contract and bound skill hashes matched the candidate record.
- `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp/p2p-delivery-review-report-contract-review-scratch python3 -m unittest discover -s <candidate>/checks -p 'test_p2p_delivery.py' -v` passed: 21 tests, `OK`. This includes the new proof-verdict rejection, structured-findings rejection, and valid review-to-proof fixture path.
- `git diff --check a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412 -- skills/productivity/deliver-issue/scripts/p2p_delivery.py checks/test_p2p_delivery.py` passed.
- The suite and reproductions use fixture transport; they establish controller behavior only, not live-host isolation or independent live review/proof behavior. An initial incomplete suite attempt used a mistyped `TMPDIR`; its temporary-directory location is unconfirmed, so only the later completed run is reported as evidence.

## Handoff

F1 affects R2 and F2 affects R1. Both are in-scope corrections under the current agreement; hand them to an explicitly authorized `/implement-contract` invocation. No acceptance proof verdict or merge-readiness assessment is issued.

Report storage: proposed destination `.p2p/work/delivery-review-report-contract/review.md`; storage pending for the enclosing workflow.

Review only; acceptance proof and merge readiness are separate.

## Next steps

1. Run `/implement-contract work/delivery-review-report-contract.md; findings .p2p/work/delivery-review-report-contract/review.md` to address F1 and F2.
2. After correction, capture a new candidate against base `a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412` and refresh full review and proof against that candidate.