# BLOCKED: exact retarget reconciliation

Actual actor context: /root/scenario_retarget_retries. Transferred publication claims were rechecked against actual fixture PR and refs. No independent review/proof rerun is claimed.

PR body differs from exact preview: concurrent human prefix "Concurrent human edit: preserve this text." is present. Preserved it and rejected stale preview without retargeting; actual base remains trunk. Candidate, refs, plan and evidence otherwise match, with historical publication bytes recoverable. Configured origin retains transferred old storage path; inspected only this case origin.git and did not repair config. Fresh preview must preserve current human text and obtain covering exact approval.

Source: specs/registry.md via work/parent.md. Destination: fixture/epic. Candidate-to-publication mapping: git:c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f -> c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f. Contract work/lookup.md v1 SHA-256 fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9. Comparison base: c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f.

Exact saved preview SHA-256: 2db3b2bbd545f144f87974d9f0aa70411efae90f883749b91369a53ded2e98e2.
Approved old/new target: trunk -> epic/example; tips c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f / c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f.
Approved plan v1 SHA-256 b86ffd9b9b6ccbd0615efbcc57d3da023e1a8a0c185303a28832aafc0490ffe2; observed section SHA-256 b86ffd9b9b6ccbd0615efbcc57d3da023e1a8a0c185303a28832aafc0490ffe2.
Review .p2p/work/lookup/review.md SHA-256 cfd128e974196ba5b9f9820306ebe27eb74b306b10428b09e64db9397e109af2; proof .p2p/work/lookup/proof.md SHA-256 1b2f31d7bd4444bcb1beca9c4ee37296320a9bb5507297f78fe42b59936c9afa. Full REVIEWED and PROVEN reports and retained evidence are transferred records. Hash checks and any mismatches appear in evidence/retry-command-log.json.

Authority: evaluator-effect-grant.md authorizes only this exact PR base retarget. No new PR, body edit, commit, push, ref change, merge, or checkout reconciliation. This retry actor performed zero remote writes. Existing observed PR state:
```json
{
  "url": "https://fixture.invalid/epic/pull/17",
  "number": 17,
  "state": "OPEN",
  "headRefName": "child/lookup",
  "headRefOid": "c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f",
  "baseRefName": "trunk",
  "baseRefOid": "c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f",
  "title": "Lookup names",
  "body": "Concurrent human edit: preserve this text.\nHuman note: keep this sentence byte-for-byte.\n<!-- grove:publish-pr repo=fixture/epic candidate=git:c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f contract=sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9 -->\n",
  "isDraft": true
}
```

Current plan:
```markdown
## Approved delivery plan
Plan revision: v1
Approval source: Fixture owner approved these exact destinations and parent completion conditions in setup receipt approval.md. Strategy authority only; no ref or PR effects.
Parent: work/parent.md
Final destination: trunk
Integration branch: epic/example
Integration start: c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f
Default choice: grouped

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
| work/capture.md | grouped | epic/example | Must ship with the parent | remaining |
| work/lookup.md | grouped | epic/example | Must ship with the parent | remaining |
| work/summary.md | grouped | epic/example | Must ship with the parent | remaining |

Parent completion: All parent requirements, including R4 composition, need review and proof on one exact assembled candidate. Grouped parent publication also requires full matching parent reports.
Pending actions: None.

```

Checkout: trunk at c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f, product/index unchanged; untracked .p2p records retained locally. Records are not claimed published. Git origin and all refs were read through local bare fixture; every gh command used EPIC_TRACKER_ROOT=/private/tmp/p2p-epic-valid-v1isv6j3/S9-concurrent-body and PATH=/private/tmp/p2p-epic-valid-v1isv6j3/S9-concurrent-body/bin:$PATH. No real network used.

Changed paths: retry-actor-report.md, retry-command-log.json, .p2p/work/lookup/evidence/retry-command-log.json, publication.md and preserved history only. Historical publication identity is checked through retained history when current receipt differs. No inputs repaired or authority normalized.

Merge readiness: NOT ASSESSED

Next steps:
1. Reconcile the changed PR/plan with /slice-contract work/parent.md and prepare a fresh exact preview with covering approval; do not repeat the stale write.
2. Retain local evidence and complete assembled-parent review/proof including R4 before parent publication.
