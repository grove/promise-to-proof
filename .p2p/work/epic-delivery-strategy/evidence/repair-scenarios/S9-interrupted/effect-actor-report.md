# PARTIAL: PR17 retarget effect

Actual actor context: /root/scenario_post_effect_preview

Exact grant: /private/tmp/p2p-epic-repair-cases/S9-interrupted/repair-effect-grant.md SHA-256 277b523d65b98fbbb2056035080df9eb06d63839da4fa361ebd0b9bbb98cb5fb. Exact approved preview: /private/tmp/p2p-epic-repair-cases/S9-interrupted/repair-preview/retarget-preview.json SHA-256 a083ca106d45955427bde61633277b21347e853089798ab3fbbf282a9ff30152. All embedded inputs, original PR fields, actual target/head refs, product/index and exact approved-section bytes matched immediately before the effect. Historical grants were not used.

Evaluator-controlled interruption after edit command response. No post-effect PR/ref readback or approved-plan recheck performed. Edit response is retained, not treated as confirmation. Fresh actor must read complete PR/ref state and exact approved plan before any retry; reuse confirmed exact target without another edit.

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
null
```

Retained approved plan at preview SHA-256 b86ffd9b9b6ccbd0615efbcc57d3da023e1a8a0c185303a28832aafc0490ffe2; exact bytes in preview JSON. Post-effect approved-plan observation:
```json
null
```

Complete exact commands/output: /private/tmp/p2p-epic-repair-cases/S9-interrupted/effect-command-evidence.jsonl. Checkout unchanged; reports and receipts remain local-only. No ref/product/contract/report repairs, commit, push, new PR, human-text edit, or merge performed. Changed paths: effect-actor-report.md, effect-command-evidence.jsonl, canonical publication.md and helper history only.

Merge readiness: NOT ASSESSED

Next steps:
1. Fresh actor reads `gh pr view 17 --json url,number,state,headRefName,headRefOid,baseRefName,baseRefOid,title,body,isDraft`, local bare refs and exact approved section before resolving the interrupted effect. Do not repeat an already confirmed edit.
2. Retain and transfer reports, plan approval/history, preview, grant and effect receipt for downstream readiness; parent still needs full assembled review and proof.
