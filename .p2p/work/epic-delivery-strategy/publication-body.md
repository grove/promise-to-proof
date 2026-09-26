## Summary

Give each child an approved destination and preserve that decision across delivery, publication, and strategy changes.

```text
approved parent plan
├─ independent child → final destination
└─ grouped child → integration branch → full parent verification → final destination
```

Retargeting requires exact authority and verified inputs. Transfer and retry preserve approvals, human edits, and confirmed effects. Parent acceptance still checks the assembled interaction.

Source: #33. Contract: [`work/epic-delivery-strategy.md`](https://github.com/grove/promise-to-proof/blob/issue/33/work/epic-delivery-strategy.md) v1, SHA-256 `78cad1d7f85183100214da15fdc8418ed2220ce1af80764d648e139fdd899895`.

Candidate: `snapshot:sha256:7e5c54fa4183651c94b4f6b83bea7cc841b2722a5693047c5c8be8faaf8f41e8`.
Publication commit: this PR's head, created from that snapshot with parent `5e369c1b45ba817b8add6b20a9b7b1c97898fa12`. The [candidate record](https://github.com/grove/promise-to-proof/blob/issue/33/.p2p/work/epic-delivery-strategy/candidate.json) retains the original snapshot identity and recoverable content.
Target: `main`, observed tip and fixed review base `5e369c1b45ba817b8add6b20a9b7b1c97898fa12`.

## Evidence

- **Before:** Controller transfer dropped a referenced approval receipt, and the original parent-failure fixture violated a child contract. [Recorded regression](https://github.com/grove/promise-to-proof/blob/issue/33/.p2p/work/epic-delivery-strategy/evidence/repair-red.log).
- **After:** The public CLI transfer regression passes. Complete children still cannot override a failing parent interaction. All 30 repository tests passed; S1–S14 and required recovery variants were exercised.
- Full [REVIEWED report](https://github.com/grove/promise-to-proof/blob/issue/33/.p2p/work/epic-delivery-strategy/review.md) and [PROVEN report](https://github.com/grove/promise-to-proof/blob/issue/33/.p2p/work/epic-delivery-strategy/proof.md): all 30 requirements, one unchanged candidate. [Record manifest](https://github.com/grove/promise-to-proof/blob/issue/33/.p2p/work/epic-delivery-strategy/publication-records.json) and [recovery guide](https://github.com/grove/promise-to-proof/blob/issue/33/.p2p/work/epic-delivery-strategy/publication-recovery.md).
- Tracker tests use controlled simulations. Live GitHub retargeting validation remains unexecuted.

## Merge Danger

**Door:** Two-way. The implementation and instruction changes can be reverted without a data migration.

**Blast Radius:** Workflows. Slicing, delivery, review, publication, and readiness consume the saved destinations; unsliced behavior remains covered.

Merge readiness: NOT ASSESSED

<!-- grove:publish-pr repo=grove/promise-to-proof candidate=snapshot:sha256:7e5c54fa4183651c94b4f6b83bea7cc841b2722a5693047c5c8be8faaf8f41e8 contract=sha256:78cad1d7f85183100214da15fdc8418ed2220ce1af80764d648e139fdd899895 -->
