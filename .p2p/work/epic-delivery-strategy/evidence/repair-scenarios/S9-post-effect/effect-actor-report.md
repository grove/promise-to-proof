# BLOCKED: PR17 retarget effect

Actual actor context: /root/scenario_post_effect_preview

Exact grant: /private/tmp/p2p-epic-repair-cases/S9-post-effect/repair-effect-grant.md SHA-256 035af113a97a92fa7ef0472bb4a2da481024413c7a1934af6c47681c00a11a27. Exact approved preview: /private/tmp/p2p-epic-repair-cases/S9-post-effect/repair-preview/retarget-preview.json SHA-256 6db61e095bf68281b8feeb6ef8c120f6f32ae82da0cf67720e2bcf572252b7e1. All embedded inputs, original PR fields, actual target/head refs, product/index and exact approved-section bytes matched immediately before the effect. Historical grants were not used.

Base edit confirmed at epic/example with all unrelated PR fields preserved. Approved plan changed after the effect; the observed effect remains recorded. Stale routing blocks further writes and requires strategy reconciliation and a fresh exact preview. No automatic rollback or second edit performed.

Source: specs/registry.md via work/parent.md; agreement work/lookup.md v1 SHA-256 fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9. Candidate-to-publication mapping: git:c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f -> c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f. Comparison base c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f. Full matching review .p2p/work/lookup/review.md and proof .p2p/work/lookup/proof.md remain referenced by exact preview hashes; no verifier rerun claimed. Destination fixture/epic, PR https://fixture.invalid/epic/pull/17, head child/lookup. Approved target trunk -> epic/example; observed pre-effect tips c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f and c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f.

Effect command/response:
```json
{
  "argv": [
    "gh",
    "pr",
    "edit",
    "https://fixture.invalid/epic/pull/17",
    "--base",
    "epic/example"
  ],
  "returncode": 0,
  "stdout": "{\n  \"url\": \"https://fixture.invalid/epic/pull/17\"\n}\n",
  "stderr": ""
}
```

Post-effect PR readback:
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

Retained approved plan at preview SHA-256 b86ffd9b9b6ccbd0615efbcc57d3da023e1a8a0c185303a28832aafc0490ffe2; exact bytes in preview JSON. Post-effect approved-plan observation:
```json
{
  "text": "## Approved delivery plan\nPlan revision: v2\nApproval source: Fixture owner approved this v2 destination in [concurrent approval](post-effect-approval.md). Strategy authority only; no ref or PR effects.\nParent: work/parent.md\nFinal destination: trunk\nIntegration branch: epic/example\nIntegration start: c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f\nDefault choice: grouped\n\n| Child | Choice | Destination | Reason | State |\n|---|---|---|---|---|\n| work/capture.md | grouped | epic/example | Must ship with the parent | remaining |\n| work/lookup.md | independent | trunk | Lookup is now acceptable without summary | remaining |\n| work/summary.md | grouped | epic/example | Must ship with the parent | remaining |\n\nParent completion: All parent requirements, including R4 composition, need review and proof on one exact assembled candidate. Grouped parent publication also requires full matching parent reports.\nPending actions: None.\n\n",
  "sha256": "89c07679eeb571d6fddf1a85067c69c24571efd4d503845851d4fb1048725575"
}
```

Complete exact commands/output: /private/tmp/p2p-epic-repair-cases/S9-post-effect/effect-command-evidence.jsonl. Checkout unchanged; reports and receipts remain local-only. No ref/product/contract/report repairs, commit, push, new PR, human-text edit, or merge performed. Changed paths: effect-actor-report.md, effect-command-evidence.jsonl, canonical publication.md and helper history only.

Merge readiness: NOT ASSESSED

Next steps:
1. Reconcile changed active routing with /slice-contract work/parent.md; retain this confirmed base edit and obtain a fresh exact preview before any further effect.
2. Retain and transfer reports, plan approval/history, preview, grant and effect receipt for downstream readiness; parent still needs full assembled review and proof.
