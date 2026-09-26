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
