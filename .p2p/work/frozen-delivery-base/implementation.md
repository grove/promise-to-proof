# IMPLEMENTED: Issue #37 — frozen delivery bases under moving targets

Contract: `work/frozen-delivery-base.md` v2, SHA-256 `3925c513a6702b94fbc2fcfc30f7d2d057638a275ae103056031cb3ca38aa0a9`  
Binding source: `plans/frozen-delivery-under-moving-targets.md`, SHA-256 `c570232a7371a53fd6dad954ec9d53f7940ecba171b3a2080fd995a6bd9a77d2`  
Approval: `.p2p/work/frozen-delivery-base/planning-handoff.md`  
Comparison base B: `dbe54bc20a19b8ab8e700fb3aba9c9e8a59ce4d4`  
Candidate C3: `snapshot:sha256:d0a2b3cc0d60f6f0f36e019e47ddddad7ca5845ee570ac02269ac3956bc82404`, 141 manifest entries.

## Repairs

The delivery controller now rejects revision expressions supplied as fully qualified `refs/heads/...` or `refs/remotes/...` destinations by validating the complete ref before resolving it. A controller regression covers both forms and verifies that rejection occurs before stage dispatch. The earlier execution-limit and process-group cleanup repair remains covered by the current candidate tests.

## Verification

- Full C3 review: `review.md`, `REVIEWED`, SHA-256 `3f0c1cfb0599abc88c567086ec37a7a91c90ec3f3170872b8722c57284e408fc`.
- Full C3 proof: `proof.md`, `PROVEN 21/21`, SHA-256 `00c97e81d139b05da6b6c2ca2a44cdb6cc1a958a65cc773f8da0fdcd6104515a`.
- Controller suite: 57 tests passed; `evidence/controller-tests-c3.stdout`, SHA-256 `25094101b20f0508035d38da717de8a06126451a8f403f8d804fb0ed4d7ef076`.
- Bounded model: 48 checks passed (14 baselines, 19 witnesses, 15 mutations); `evidence/model-c3/summary.json`, SHA-256 `f57e04b74e242e23b44f5229a8ce5082b8ae5203dd6ab182fd533a55505ba866`.
- Focused revision-expression regression: `evidence/controller-test-c3-focused.md`, SHA-256 `037fa5068ff0ce399f9508be81f4038d0d43e6436e6490f8a9e116b06da48162`.
- Exact B recovery after source pruning: `evidence/comparison-base-c3.json`, SHA-256 `2e32b00b9d63cd9352ab656368177dbcb6086234082e6f0fe8cfb637217cab90`; retained bundle SHA-256 `66801edaf265b33fbd28b7a2cedadae1a4b596dd52a430588459ce4436b42a56`.

The proof report records the controlled C′ limitation for publication/readiness checks, R12 changed-input variants not separately injected, and that merge readiness was not assessed. Contract, source, candidate, and base identities match the saved reports. No commit, push, pull request, or merge-readiness assessment has occurred.

Next step: the exact draft publication preview is being saved in `.p2p/work/frozen-delivery-base/publication.md` for review before any publication effect.
