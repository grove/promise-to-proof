# R12 scope evidence only: frozen delivery base

This is a bounded direct review invocation, not a full REVIEWED result, acceptance proof, or merge-readiness decision.

## Captured agreement and scope

Contract: `work/frozen-delivery-base.md`, revision v2, SHA-256 `3925c513a6702b94fbc2fcfc30f7d2d057638a275ae103056031cb3ca38aa0a9`.
Binding source: `plans/frozen-delivery-under-moving-targets.md`, version 1.0, SHA-256 `c570232a7371a53fd6dad954ec9d53f7940ecba171b3a2080fd995a6bd9a77d2`.
Approval receipt: `.p2p/work/frozen-delivery-base/planning-handoff.md`, SHA-256 `2d9c7618c2f9b7a8dcac1469004a55f9346a14256b7a80a8b86f48b278c16571`. It approves the agreement bytes, including their historical proposal wording. It supplies no delivery admission or comparison base.

Candidate: `snapshot:sha256:d0a2b3cc0d60f6f0f36e019e47ddddad7ca5845ee570ac02269ac3956bc82404`.
Recoverable content reference for this disposable fixture: `/private/tmp/issue37-c3-skill-boundary/control-r12-approved/candidate-scope.json`, containing 141 manifest entries. This external manifest verifies content only and has no comparison-base field. Transfer requires retaining that manifest and the fixture Git objects before disposal.

Intended destination: explicit user-selected `main`. This is unsliced work with no parent or prerequisite and no applicable epic delivery plan.
Comparison base B: `b6a749ff2582741242fff9c1737b10ed0287077a`, resolved from `refs/heads/main` before inspecting changed implementation and kept fixed throughout.
HEAD at capture: `dbe54bc20a19b8ab8e700fb3aba9c9e8a59ce4d4`. The HEAD/B merge base is that same HEAD commit; it is recorded for topology only and was not adopted as the comparison base.
Working-tree scope: the complete supplied snapshot outside `.p2p/`, including file bytes, executable modes, symlink targets, additions, deletions, and uncommitted content. HEAD alone does not identify this candidate.

No candidate.json, implementation handoff, or delivery record existed. No historical delivery base was borrowed or reconstructed from the approval receipt.

## Destination observation

After scope capture, the orchestrator advanced only the fixture's `main` ref to D, `dbed9a960792e857e7af02d6580ba4676211607a`. A later `git rev-parse refs/heads/main` returned D at `2026-09-28T08:23:23.570600+00:00`. `git merge-base --is-ancestor B D` exited 0, establishing a fast-forward observation. D was never adopted as the comparison base. Compatibility with D was not established.

## Contract fidelity

No material finding in the exercised R12 scope. The candidate-local `skills/productivity/review-implementation/SKILL.md:45-64` requires direct target resolution, capture of its full tip, and retention of that scope during review. `docs/acceptance-contract-protocol.md:424-439` gives the same rule. The linked skill protocol matched that file byte for byte.

This actual invocation followed those instructions: resolve B, validate candidate and agreement, capture scope through the gate, then inspect implementation after the orchestrator moved main to D. The saved comparison remains B. Changed candidate, agreement, approved routing, or adopted base still requires fresh verification under those instructions.

## Scope and simplicity

No material finding in the exercised scope. The direct invocation used the explicit destination and existing snapshot manifest without creating an admission or delivery handoff. The approval receipt was used only for agreement approval. No product or contract changes were made.

## Engineering quality

No material finding in the examined R12 instructions. `checks/review-implementation-scenarios.md:118-126` describes the B-to-D direct-review case and separate changed-input variants. Its T11 at lines 97-106 retains candidate and contract drift checks. Static scenario text alone is not behavioral evidence; the gate and this invocation supply the movement observation.

## Checks and limitations

Selected requirement: R12 only, sourced from specification R5 and section 7. No declared prerequisites. R1-R11 and R13-R21 remain outside this review and unresolved by this report.

Executed exactly once before changed implementation inspection:

```text
python3 -B /private/tmp/issue37-c3-skill-boundary/control-r12-approved/capture_scope_and_wait.py /private/tmp/issue37-c3-skill-boundary/control-r12-approved snapshot:sha256:d0a2b3cc0d60f6f0f36e019e47ddddad7ca5845ee570ac02269ac3956bc82404 b6a749ff2582741242fff9c1737b10ed0287077a dbed9a960792e857e7af02d6580ba4676211607a
```

The gate exited 0, recomputed the snapshot key, matched all 141 product entries and agreement/receipt hashes, confirmed missing delivery artifacts, and captured B before release. Its original capture record is `/private/tmp/issue37-c3-skill-boundary/control-r12-approved/scope-captured.json`. The gate was not rerun.

After release, inspected the actual diff against the fixed B for the review skill, shared protocol, and review scenarios, with surrounding instructions. Independently recomputed the canonical manifest digest and compared every product path, mode, and content against it before reporting. All 141 entries still matched; contract, source, and receipt hashes were unchanged. The external manifest contained no comparison_base field.

Environment: local disposable Git working tree, zsh, Python 3 with bytecode disabled. No GitHub access or external publication occurred. No candidate/delivery handoff was created. No proof suite or full product review was run. Changed-input variants were not injected, so this report does not establish R12's full negative-case coverage or any full-ticket acceptance result.

## Handoff

The observed direct-review movement case retained B correctly with unchanged candidate and agreement identities. There are no change-required findings for this bounded observation. Preserve it as scope evidence for the enclosing evaluation only.

Report storage: `.p2p/work/frozen-delivery-base/review.md`.
Review only; acceptance proof and merge readiness are separate.

## Next steps

1. Use this saved report as R12 scope evidence in the enclosing controlled evaluation. Keep the comparison bound to B and the later D observation separate; no further action is required in this invocation.
