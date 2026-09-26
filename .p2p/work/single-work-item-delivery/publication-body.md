## Summary

Adds the single-work-item delivery controller for #28 on macOS Codex CLI.

```text
run or resume
  persist stage reservation
  implement in an isolated workspace
  review and prove the fixed candidate independently
  accept matching full reports, or retain an exact blocker
```

Preserve unrelated work, reject stale or missing evidence, and retain the one-repair allowance across restarts. Record usage and enforce supported admission limits. Hard monetary caps remain unsupported.

Contract: [work/single-work-item-delivery.md v1](https://github.com/grove/promise-to-proof/blob/issue/28/work/single-work-item-delivery.md), SHA-256 `e447f13a94dae84b9af2dfc06cfb6be36900eee2c0e381a3942015245b48826d`.
Candidate: `snapshot:sha256:847704b1ef38871fc2e62529426105cc31ae029a79c11e8190c00fcb3b519259`.
Comparison base and observed target tip: `1a296f6ec7a064b32ce1be6a5d29f0c39df12294`.

Publication creates one content-equivalent commit from this snapshot plus the listed delivery records. The resulting PR head records the snapshot-to-commit mapping; the reports remain bound to the snapshot.

## Evidence

- **Before:** Delivery rules and the Phase 1 model existed, but no controller enforced the full single-work-item lifecycle.
- **After:** 19 controller tests and four existing filesystem/bundle tests passed independently. A real host run completed implementation, review and proof. Protected-write, network and hostile project-configuration probes passed.
- [REVIEWED](https://github.com/grove/promise-to-proof/blob/issue/28/.p2p/work/single-work-item-delivery/review.md) and [PROVEN, R1–R14](https://github.com/grove/promise-to-proof/blob/issue/28/.p2p/work/single-work-item-delivery/proof.md) match the exact contract and candidate.
- [Evidence and recovery guide](https://github.com/grove/promise-to-proof/blob/issue/28/.p2p/work/single-work-item-delivery/publication-recovery.md) retains the live records, prior failed runs, host provenance and complete recovery archive. Fixture results remain distinct from real-host evidence.

## Merge Danger

**Door:** two-way. **Blast Radius:** delivery workflow.

Adds an opt-in controller and atomic report writes in the shared filesystem helper. Supports one macOS Codex CLI host; it does not add publication or weaker acceptance modes.

Merge readiness: NOT ASSESSED.

<!-- grove:publish-pr repo=grove/promise-to-proof candidate=snapshot:sha256:847704b1ef38871fc2e62529426105cc31ae029a79c11e8190c00fcb3b519259 contract=sha256:e447f13a94dae84b9af2dfc06cfb6be36900eee2c0e381a3942015245b48826d -->
