# REVIEWED: R5-only scope evidence for frozen delivery base

This controlled local invocation reviews only the R5 delivery-review scope boundary. It does not review the full implementation or issue all 21 requirements. It is not a full REVIEWED report, acceptance proof, publication approval, or merge-readiness assessment.

Contract: `work/frozen-delivery-base.md`, v2, SHA-256 `3925c513a6702b94fbc2fcfc30f7d2d057638a275ae103056031cb3ca38aa0a9`.
Binding source: `plans/frozen-delivery-under-moving-targets.md`, SHA-256 `c570232a7371a53fd6dad954ec9d53f7940ecba171b3a2080fd995a6bd9a77d2`.
Candidate: `snapshot:sha256:d0a2b3cc0d60f6f0f36e019e47ddddad7ca5845ee570ac02269ac3956bc82404`, recoverable from `candidate.json` alongside this report, with 141 manifest entries.

## Saved comparison scope

Comparison base: `dbe54bc20a19b8ab8e700fb3aba9c9e8a59ce4d4`.
Retained base tree: `c8bfbe410b902c57d2b52d6f609f5c3cb659637c`.
Scope: the exact candidate manifest against that frozen commit, including current tracked and relevant untracked product content, modes, symlink targets, and deletions. The entire `.p2p/` directory is excluded. This snapshot has 19 changed product paths against the base; their complete list is retained in `evidence/r5-scope-validation.json`. The selected review examines R5-related instructions and scope handling within that change set, not all 19 paths for all obligations.

The scope comes from the validated `candidate.json` and `implementation.md` handoff. Both bind this candidate to the same saved base, and the implementation handoff explicitly names `main`. The candidate-local skill's admitted-delivery rule retains that base. This is not a new direct review under R12, and no newer base has been adopted.

`planning-handoff.md` records approval of the exact v2 contract and source hashes checked here. Its retained approval resolves the historical proposal wording still present in the unchanged contract. This unsliced work declares no parent or prerequisites; no epic delivery plan applies. No linked pending amendment changes R5. This validation uses the transferred local receipt, not remote approval verification or a reconstruction of a controller admission history.

## Current destination observation

Destination: local `refs/heads/main`.
Observed tip: `7ebbc1438ef7cafc6de2935e6d15260ffff49c04`.
Observed at: `2026-09-28T08:05:45.990414+00:00`.
Relationship to saved comparison base: `fast-forward`.
Git merge base of saved base and current main: `dbe54bc20a19b8ab8e700fb3aba9c9e8a59ce4d4`.

The destination tip differs from the frozen base. `git diff <base> refs/heads/main --stat -- . ':!.p2p'` was empty, so this local advance contains no product-tree difference outside `.p2p/`. That does not replace the saved comparison SHA. Compatibility with the current destination and publication or merge gates are outside this invocation.

## Contract fidelity

No material findings within the bounded R5 scope. The actual skill invocation retained the validated delivery base despite the different current main tip. `skills/productivity/review-implementation/SKILL.md`, under Capture the agreement and review scope, explicitly distinguishes admitted delivery from direct review. The linked protocol's Epic delivery plans section preserves that distinction and separates destination observations. The reference protocol and `docs/acceptance-contract-protocol.md` compare byte-for-byte equal.

Static inspection of `skills/productivity/deliver-issue/scripts/p2p_delivery.py:stage` shows that its prompt passes the persisted comparison base as immutable, prohibits replacing it on destination movement, and labels the latest destination observation informational. This invocation exercises the candidate-local review procedure with the transferred handoff. It does not claim to have dispatched a live controller worker.

## Scope and simplicity

No material findings within the bounded R5 scope. The saved review compares C against the handed-off base. The newer main tip remains a separate observation. No rebase, merge, base refresh, verifier restart, or product change was performed.

## Engineering quality

No material findings within the bounded R5 scope. Identity checks precede scope adoption; the author's implementation report supplied navigation and handoff claims, not validation results. The report and evidence remain outside the product candidate.

## Checks and limitations

Independent Python checks recomputed SHA-256 over the exact contract and source bytes and canonical sorted manifest JSON. They compared the manifest path set with `git ls-files -z --cached --others --exclude-standard`, excluded `.p2p/`, and compared every existing product path's bytes or symlink target and executable mode. All 141 entries matched; the recomputed key matched the saved key.

`git cat-file -t <base>` returned `commit`. Rehashing the raw commit with its Git object header reproduced the saved base SHA. `git ls-tree -rz <base>` and `git cat-file blob <oid>` recovered all 140 base product entries; rehashing each blob reproduced its object ID. Thus the retained base is recoverable in this fixture independently of using the mutable main ref. No external bundle or fresh-checkout transfer test was performed.

The repository helper `p2p_filesystem.validate(root, work_item, comparison_base)` also passed, including binding-link discovery and index checks. `git rev-parse refs/heads/main`, `git merge-base --is-ancestor <base> <tip>`, and `git merge-base <base> <tip>` established the separate destination observation. Exact observations were saved and reread in `evidence/r5-scope-validation.json`.

Before report storage, the helper validation passed again and main still resolved to the observed tip. Candidate, contract, binding source, and adopted base remained unchanged. No prior `review.md` existed in this fixture, so no replacement history was needed.

Coverage: R5's controlled delivery-review scope scenario only. R2/R4/R11 supply relevant identity and recovery constraints checked narrowly here; their complete behavior is not reviewed. R1–R4 and R6–R21 remain unreviewed by this invocation. No full controller suite, proof, direct-review scenario, remote lookup, publication, or merge ran.

## Handoff

No change-required findings for this bounded scope. Retain this report as R5 scope evidence for the separate full review and proof workflow. Do not use its REVIEWED heading as a whole-contract delivery result.

Report storage: `.p2p/work/frozen-delivery-base/review.md`.
Review only; acceptance proof and merge readiness are separate.

## Next steps

1. No further action is required for this controlled R5-only invocation. The enclosing full review/proof workflow may consume this report and `evidence/r5-scope-validation.json` for candidate `snapshot:sha256:d0a2b3cc0d60f6f0f36e019e47ddddad7ca5845ee570ac02269ac3956bc82404` against `dbe54bc20a19b8ab8e700fb3aba9c9e8a59ce4d4`. It must independently cover the remaining obligations before issuing full review or acceptance results.
