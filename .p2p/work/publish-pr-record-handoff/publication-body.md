## Summary

Completes the safety scenarios added by #26. The skill instructions already contain these protections; the documented checks now exercise them explicitly.

```diff
 Reconcile leftover local copies
+  reject mode-only and symlink-only matches
+  preserve tracked copies
+  require cleanup approval
 Publish later records
+  require approval for the follow-up commit and push
```

The product change adds 14 lines to scenarios 13–14. This PR also retains the canonical contract and the independent review/proof records for the skill handoff.

## Evidence

- **Before:** Full review found five omitted scenario variants.
- **After:** Each variant states its expected classification and no-move or no-write outcome.
- Full independent review and proof cover R1–R5, including instruction walkthroughs, disposable filesystem/Git checks, and standalone packaging validation. These checks establish instruction/scenario completeness, not universal agent compliance or live GitHub execution.

Contract: [work/publish-pr-record-handoff.md v1](https://github.com/grove/promise-to-proof/blob/fix/publish-pr-safety-scenarios/work/publish-pr-record-handoff.md), SHA-256 `656b4db8958e3877a166640adbf37338c6acfee38646e30a5185030855732d5a`.
Candidate: `snapshot:sha256:4ad7a1d6086cc3032d3b4ad67eba7d129b2398121cefdfeb84f2ae2e374f47de`.
Comparison base: `69c02fe5a0e876b104baacca2e4075f801974d40`.
[Review](https://github.com/grove/promise-to-proof/blob/fix/publish-pr-safety-scenarios/.p2p/work/publish-pr-record-handoff/review.md) and [proof](https://github.com/grove/promise-to-proof/blob/fix/publish-pr-safety-scenarios/.p2p/work/publish-pr-record-handoff/proof.md) include retained evidence and limitations.

## Merge Danger

**Door:** two-way. **Blast Radius:** scenario documentation.

No skill instructions or runtime behavior change. Merge readiness is assessed separately for the current remote head.

<!-- grove:publish-pr repo=grove/promise-to-proof candidate=snapshot:sha256:4ad7a1d6086cc3032d3b4ad67eba7d129b2398121cefdfeb84f2ae2e374f47de contract=sha256:656b4db8958e3877a166640adbf37338c6acfee38646e30a5185030855732d5a -->
