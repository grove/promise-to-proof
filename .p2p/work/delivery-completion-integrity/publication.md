# PUBLISHED: issue #24

Source: https://github.com/grove/promise-to-proof/issues/24
Contract: `work/delivery-completion-integrity.md`, v1, SHA-256 `7cfbf6558846415b06b130d4989ca88a93ea73f06cb341eb02b30e7ac4b02956`.
Report-bound candidate: `snapshot:sha256:09373011d141a5cbc78a0ea855d257eb456b31246d2875bb32c17e436e44bb25`.
Publication commit: `3ef1651418b44c3d0ee59e81cf3aec3c22e36454`.
Commit tree: `f6e5efacb60d7de9049236f16d138b140680eb63`.
Comparison base, commit parent and observed main tip: `41bebc726a8cc71c1d2f22d822ade006f4e78121`.
Destination: grove/promise-to-proof, https://github.com/grove/promise-to-proof.git.
Remote head: `issue/24` at `3ef1651418b44c3d0ee59e81cf3aec3c22e36454`.
Target: `main`.
Pull request: https://github.com/grove/promise-to-proof/pull/25, OPEN and DRAFT confirmed by readback.
Title: Model delivery completion integrity with FizzBee.

## Authority and effects

The user approved the complete exact preview with "i approve". Approved preview SHA-256 `9a5e8dbb77097ef54bc607dabbbd1a56e637a3d3c788e3fc0877487c214f95c6` is retained at `history/9a5e8dbb77097ef54bc607dabbbd1a56e637a3d3c788e3fc0877487c214f95c6/publication.md`. The approval covered isolated commit creation, non-force push and draft PR creation. All three effects completed and were verified. No merge, readiness change, reviewer request, issue closure, label or comment occurred.

## Candidate mapping and recovery

The publication commit's complete product tree matches every byte, path, mode and symlink in the reviewed/proven 112-entry manifest. The 436 approved added records and 7 inherited records match the exact artifact inventory and hashes. Parent, author, committer, message and unsigned policy match the approved inputs. Both timestamps are `2026-09-26T09:57:23 +0000`. Commit metadata is not a behavioral input to this model runner; model and pinned checker inputs are unchanged.

The original reports remain bound to the snapshot, not relabeled to the new commit:

- `review.md`: full REVIEWED, SHA-256 `b1f1f30f5843081be54dcfcaee3058508a73892e56e5456f7ae5ad99c918305d`.
- `proof.md`: full PROVEN, R1–R10, SHA-256 `5af136791ee5a51d9e04ce18089b2204a0a789a37502ad55ab9dfe1652cab7f8`.
- `candidate.json`: recoverable report-bound product tree and binding inputs.
- `publication-inputs.json`: exact approved record inputs.
- `publication.bundle`: retained commit and history, SHA-256 `b5340b25d382a29fca8097f550c7486c557359d8644e63337d00c37b4b2e5905`.
- `publication-state.json`: full commit mapping and execution metadata.
- `publication-readback.json`: exact GitHub fields and body after creation.

Isolated workspace: `/var/folders/vq/593qxcm57l90w1dlpywl_7nw0000gn/T/p2p-publication-24-fllgjpeb/repo`. The operator's working checkout, branch and index were not used to publish and remain unchanged apart from authorized durable publication records. Its product tree still validates against the captured candidate.

## Readback

Confirmed the remote head SHA, target tip, repository URL, head/base branch names, title, exact approved body, source #24, stable candidate/contract marker, OPEN state and draft flag. No publication uncertainty remains. CI and merge approvals were not assessed or awaited.

Merge readiness: NOT ASSESSED

Next steps:

1. When the PR approaches a merge decision, invoke `/merge-readiness https://github.com/grove/promise-to-proof/pull/25; review .p2p/work/delivery-completion-integrity/review.md; proof .p2p/work/delivery-completion-integrity/proof.md`.
