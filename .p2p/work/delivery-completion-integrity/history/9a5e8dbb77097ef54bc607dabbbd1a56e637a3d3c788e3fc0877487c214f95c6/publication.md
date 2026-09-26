# DRAFT: issue #24 publication preview

Source: https://github.com/grove/promise-to-proof/issues/24
Agreement: `work/delivery-completion-integrity.md`, v1, SHA-256 `7cfbf6558846415b06b130d4989ca88a93ea73f06cb341eb02b30e7ac4b02956`.
Candidate: `snapshot:sha256:09373011d141a5cbc78a0ea855d257eb456b31246d2875bb32c17e436e44bb25`.
Review: `review.md`, SHA-256 `b1f1f30f5843081be54dcfcaee3058508a73892e56e5456f7ae5ad99c918305d`, full REVIEWED.
Proof: `proof.md`, SHA-256 `5af136791ee5a51d9e04ce18089b2204a0a789a37502ad55ab9dfe1652cab7f8`, full PROVEN R1–R10.

## Destination and state

Repository: `grove/promise-to-proof`.
Remote: `origin`, `https://github.com/grove/promise-to-proof.git`.
Target/default branch: `main`.
Observed target tip and fixed comparison base: `41bebc726a8cc71c1d2f22d822ade006f4e78121`.
Proposed new head: `issue/24`.
Observed remote and local head state: absent. All three existing pull requests were inspected across all states; none matches this head or candidate marker.
No PR template, contribution file or additional branch naming rule was found. Applicable repository AGENTS/tracker instructions were read.

## Exact commit plan

Create one local publication commit in a new isolated workspace reconstructed from the full parent tree and recoverable candidate. Do not alter the operator checkout or its Git refs/index.
Parent: `41bebc726a8cc71c1d2f22d822ade006f4e78121`.
Product tree: exact 112-entry manifest in `candidate.json`, excluding `.p2p/` by definition.
Durable record inputs: the exact 436 additional paths, modes and byte hashes enumerated in `publication-inputs.json`, SHA-256 `b3a833d5ed81cd0c14aa287c9e451f804a2ec74703da60245b6afbac26f39315`, totaling 7,447,702 bytes. This explicitly includes implementation, review, proof, delivery, candidate/base recovery records, host invocation records and their evidence/history. Retain the parent's existing tracked `.p2p/` files unchanged. No other generated records are commit inputs; this preview, its body file, input index, and later publication mapping stay local.
Commit message, one line followed by newline: `Model delivery completion integrity with FizzBee (#24)`.
Author and committer: `Geir Ove Grønmo <grove@geirove.org>`.
Timestamp policy: set author and committer date to the same actual UTC timestamp at commit creation and retain the exact value in the mapping.
Signing policy: unsigned, matching unset `commit.gpgsign`; no configured signing requirement or active repository hook was found.
After commit creation, verify the full product tree, approved record bytes/modes, parent and metadata. Retain and reread the commit and snapshot-to-commit mapping before any remote write. Preserve the report-bound snapshot key.

## Equivalence and evidence checks

Current helper validation passed for the whole product tree, work-item hash, all binding input hashes and comparison base. Review/proof hashes and all 420 implementation/review/proof evidence checksums passed. Source issue and comments are unchanged on recheck. Candidate, report and artifact content were inspected; credential-pattern scan found no private keys or token patterns. Known machine paths in reports identify the actual stage environment, not credentials.
The executable model/runner reads model bytes and pinned FizzBee binaries, not Git metadata or commit timestamps. No compilation, dependency installation, signing transformation or code generation occurs during publication. Keep product bytes and modes unchanged; publication adds only the enumerated durable records. Formal-check observations remain bound to the original model and checker hashes. No verification rerun or code change is authorized by this preview.

## Proposed title

Model delivery completion integrity with FizzBee

## Complete proposed body

The exact UTF-8 body is `publication-body.md`, SHA-256 `0a9463b0835563fcbad67e01efa4652c3e4cad823f3f2a790eaa6174026b5e33`. Its bytes are reproduced below.

## Summary

Adds a bounded executable model for #24 that rejects stale or incomplete delivery evidence.

```text
checks/delivery-model/
  delivery.fizz  lifecycle and safety assertions
  check.py       reproducible checks and retained traces
  README.md      pins, traceability, bounds and limits
```

Contract: [work/delivery-completion-integrity.md v1](https://github.com/grove/promise-to-proof/blob/issue/24/work/delivery-completion-integrity.md), SHA-256 `7cfbf6558846415b06b130d4989ca88a93ea73f06cb341eb02b30e7ac4b02956`.
Candidate: `snapshot:sha256:09373011d141a5cbc78a0ea855d257eb456b31246d2875bb32c17e436e44bb25`.
Comparison base and observed `main` tip: `41bebc726a8cc71c1d2f22d822ade006f4e78121`.

Publication creates one content-equivalent commit from this snapshot plus the approved durable records. The resulting PR head SHA records the commit side of that mapping; the reports remain bound to the snapshot.

## Evidence

- **Before:** No executable completion-integrity model for this issue.
- **After:** 43 checks passed independently: 11 baseline explorations, 18 success/blocker witnesses and 14 deliberate mutation counterexamples. Maximum action depth was 20/64.
- [REVIEWED](https://github.com/grove/promise-to-proof/blob/issue/24/.p2p/work/delivery-completion-integrity/review.md) and [PROVEN, R1–R10](https://github.com/grove/promise-to-proof/blob/issue/24/.p2p/work/delivery-completion-integrity/proof.md), with retained evidence alongside the reports.

The pinned runner uses FizzBee v0.5.3 on macOS arm64. Checks cover finite single-fault scenarios and do not establish live-agent conformance.

## Merge Danger

**Door:** two-way. **Blast Radius:** model checks and documentation. Existing workflow behavior and verdicts are unchanged.

Merge readiness: NOT ASSESSED

<!-- grove:publish-pr repo=grove/promise-to-proof candidate=snapshot:sha256:09373011d141a5cbc78a0ea855d257eb456b31246d2875bb32c17e436e44bb25 contract=sha256:7cfbf6558846415b06b130d4989ca88a93ea73f06cb341eb02b30e7ac4b02956 -->

## Authority and observed effects

Authorized so far: local preview preparation and use of `gh` outside the sandbox for inspection.
Publication authority: pending explicit approval of this complete preview and its hashed inputs.
Effects observed: local preview/body/input-index saved; no commit, branch, push or PR created.

The requested exact approval covers all three effects together:

1. Create the one local publication commit from the specified parent, product manifest, enumerated durable records and metadata policy in an isolated workspace.
2. Push that exact commit without force to the absent `refs/heads/issue/24` in `grove/promise-to-proof`.
3. Create one draft PR from `issue/24` to `main` with the exact title/body above and verify readback.

Any changed candidate, agreement, reports, target tip, head state, commit inputs, title or body requires a new preview. No merge, readiness change, reviewer request, issue closure, label or comment is authorized.

Merge readiness: NOT ASSESSED

Next steps:

1. Authorize this exact preview and all three listed publication effects.
2. `/publish-pr .p2p/work/delivery-completion-integrity/publication.md; publish the draft PR`.
