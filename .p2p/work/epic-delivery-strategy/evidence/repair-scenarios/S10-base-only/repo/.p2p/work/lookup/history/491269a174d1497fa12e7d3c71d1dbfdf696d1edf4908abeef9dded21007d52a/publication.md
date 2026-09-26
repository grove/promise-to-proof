# PUBLISHED: PR 17 retarget confirmed

Actual publication actor context: /root/scenario_retarget_publisher. Review and proof were performed together in distinct context /root/scenario_retarget_verification, not by this publication actor.

Authorized and observed effect: one simulator-only base edit of https://fixture.invalid/epic/pull/17 from trunk to epic/example. Edit returned exit 1 with a simulated lost-response error after persistence. Immediate readback confirmed the exact requested base and every preserved field. No retry occurred. No pending or ambiguous retarget effect remains.

Source: specs/registry.md via work/parent.md. Contract work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9. Candidate and publication commit mapping: git:c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f -> c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f. Comparison base, old and new target tips, and head child/lookup all remain c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f. Destination fixture/epic, local fixture origin /private/tmp/p2p-epic-valid-v1isv6j3/S9-default/origin.git.

Review: .p2p/work/lookup/review.md sha256:cfd128e974196ba5b9f9820306ebe27eb74b306b10428b09e64db9397e109af2 (full REVIEWED). Proof: .p2p/work/lookup/proof.md sha256:1b2f31d7bd4444bcb1beca9c4ee37296320a9bb5507297f78fe42b59936c9afa (full PROVEN). Plan .p2p/work/parent/slicing.md v1 approved section sha256:b86ffd9b9b6ccbd0615efbcc57d3da023e1a8a0c185303a28832aafc0490ffe2. Exact plan and all agreement/binding identities are retained in unchanged preview. All were rechecked before effect; approved plan checked after effect.

PR remains OPEN and draft. Complete readback:
```json
{
  "url": "https://fixture.invalid/epic/pull/17",
  "number": 17,
  "state": "OPEN",
  "headRefName": "child/lookup",
  "headRefOid": "c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f",
  "baseRefName": "epic/example",
  "baseRefOid": "c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f",
  "title": "Lookup names",
  "body": "Human note: keep this sentence byte-for-byte.\n<!-- grove:publish-pr repo=fixture/epic candidate=git:c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f contract=sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9 -->\n",
  "isDraft": true
}
```

Retained evidence byte identities:
```json
{
  ".p2p/work/lookup/evidence/retarget-preview.json": "2db3b2bbd545f144f87974d9f0aa70411efae90f883749b91369a53ded2e98e2",
  ".p2p/work/lookup/evidence/retarget-effect-grant.md": "d0961eea6cc8b4d01083c6f7db70e87b4a9ea56e2d13c9c237dee73dc3fc6a5b",
  ".p2p/work/lookup/evidence/retarget-execution.txt": "65af07cc8bdc302104753cf03a4211a4a78fb33103eedb0a451682b8874b0169",
  ".p2p/work/lookup/evidence/retarget-readback.json": "f170e79c506632d40f410c903c79f4aed4f59b450637cf68c7349dea88cdfaca"
}
```

The exact evaluator grant is retained in evidence/retarget-effect-grant.md. Preview and prior publication observations remain retained, with replaced publication reports preserved through filesystem history. There were no commits, pushes, ref changes, body changes, duplicate PRs, or merges. Local checkout remains trunk at the same commit, index and product clean, with untracked .p2p records retained in place. No checkout reconciliation was authorized. Reports, plan and receipts remain local-only and require transfer for another checkout; no records publication is claimed.

Remaining work: assembled-parent verification including R4, plus merge readiness and its CI/review gates. No readiness evaluation or merge authority is implied.

Merge readiness: NOT ASSESSED

Next steps:
1. When approaching a merge decision, invoke `/merge-readiness https://fixture.invalid/epic/pull/17; review .p2p/work/lookup/review.md; proof .p2p/work/lookup/proof.md`. Required CI and repository approvals have not been assessed.
2. Retain or explicitly transfer the local reports and plan; complete assembled-parent review and proof before parent publication.
