# PUBLISHED: resumed PR17 retarget

Actual fresh actor context: /root/scenario_post_effect_resume

Interrupted base edit confirmed by fresh readback. Reused the exact existing effect; no retry performed.

Source specs/registry.md via work/parent.md. Agreement work/lookup.md v1 SHA-256 fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9. Candidate-to-commit mapping git:c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f -> c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f. Full matching reports .p2p/work/lookup/review.md and .p2p/work/lookup/proof.md were reread and exact hashes checked. Comparison base c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f. Destination fixture/epic; remote /private/tmp/p2p-epic-repair-cases/S9-interrupted/origin.git; head child/lookup at c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f; PR https://fixture.invalid/epic/pull/17, draft True. Observed base epic/example at c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f.

Existing covering grant /private/tmp/p2p-epic-repair-cases/S9-interrupted/repair-effect-grant.md binds preview /private/tmp/p2p-epic-repair-cases/S9-interrupted/repair-preview/retarget-preview.json; only one base edit from trunk to epic/example was authorized. That prior effect is confirmed, not repeated. No new authority inferred. No unrelated PR changes observed. No product, contract, ref, commit, push, new PR, or other tracker mutations performed.

Exact active plan retained in .p2p/work/lookup/evidence/resume-approved-plan.md, SHA-256 b86ffd9b9b6ccbd0615efbcc57d3da023e1a8a0c185303a28832aafc0490ffe2; bytes including trailing separators were extracted by the protocol regex and reread unchanged. Original approved section and approvals remain in repair-preview, prior publication and parent history. Identity observations and installed hashes:

```json
{
  "actor": "/root/scenario_post_effect_resume",
  "installed_sha256": {
    "installed-repair/publish-pr/SKILL.md": "c1c0c65b5d588bba53f464a2b52ca2c4eb239d390d2c470e89b4f2a7ce8f0884",
    "installed-repair/publish-pr/references/acceptance-contract-protocol.md": "209562cadbad5a945998fe1fb370ffab5ab4ea648fc4ac720888c2d3a3ca634d",
    "installed-repair/publish-pr/agents/openai.yaml": "b285275d57f932bec2077fffa9adb02767907d4818e70abc9145fd7d5c3ce6e2",
    "installed-repair/publish-pr/scripts/p2p_filesystem.py": "90e0856bd73cbf3912c5e57a6ef80b63fdb1e81771cb8d0a7c91fe401b8b4cd2"
  },
  "preview_sha256": "a083ca106d45955427bde61633277b21347e853089798ab3fbbf282a9ff30152",
  "grant_sha256": "277b523d65b98fbbb2056035080df9eb06d63839da4fa361ebd0b9bbb98cb5fb",
  "input_checks": {
    "AGENTS.md": true,
    "registry.py": true,
    "check.py": true,
    "work/lookup.md": true,
    "work/parent.md": true,
    "specs/registry.md": true,
    ".p2p/work/lookup/candidate.json": true,
    ".p2p/work/lookup/review.md": true,
    ".p2p/work/lookup/proof.md": true,
    ".p2p/work/lookup/evidence/review-commands.txt": true,
    ".p2p/work/lookup/evidence/proof-commands.txt": true,
    ".p2p/work/lookup/evidence/common-identity.txt": true,
    ".p2p/work/parent/slicing.md": true,
    ".p2p/work/parent/approval.md": true,
    ".p2p/work/lookup/history/dcc06525940357283ffde291a1d2852d433ac70afef6bf41d4961a10cca999a1/publication.md": true,
    ".p2p/work/lookup/history/999ebe002c1ce7bb6767ee587234f948a9987dcd8e6bffcea946a20ca8888401/publication.md": true,
    ".p2p/work/lookup/history/6101aecfb5a9d96570c178d75af992ff45d931151e24dde820a2846dd2244b7f/publication.md": true
  },
  "pr_readback": {
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
  },
  "refs_readback": "c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f\trefs/heads/child/lookup\nc2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f\trefs/heads/epic/example\nc2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f\trefs/heads/trunk\n",
  "plan_sha256": "b86ffd9b9b6ccbd0615efbcc57d3da023e1a8a0c185303a28832aafc0490ffe2",
  "plan_text": "## Approved delivery plan\nPlan revision: v1\nApproval source: Fixture owner approved these exact destinations and parent completion conditions in setup receipt approval.md. Strategy authority only; no ref or PR effects.\nParent: work/parent.md\nFinal destination: trunk\nIntegration branch: epic/example\nIntegration start: c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f\nDefault choice: grouped\n\n| Child | Choice | Destination | Reason | State |\n|---|---|---|---|---|\n| work/capture.md | grouped | epic/example | Must ship with the parent | remaining |\n| work/lookup.md | grouped | epic/example | Must ship with the parent | remaining |\n| work/summary.md | grouped | epic/example | Must ship with the parent | remaining |\n\nParent completion: All parent requirements, including R4 composition, need review and proof on one exact assembled candidate. Grouped parent publication also requires full matching parent reports.\nPending actions: None.\n\n",
  "approved_preview_plan_sha256": "b86ffd9b9b6ccbd0615efbcc57d3da023e1a8a0c185303a28832aafc0490ffe2",
  "plan_matches_preview": true,
  "prior_publication_sha256": "ba652859d93c89261a1fee2077a28fadb898af0688f12832ebd313c096d48b43",
  "section_save_readback": "exact bytes and SHA-256 matched"
}
```

Checkout remains on trunk at c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f; index and tracked product unchanged. Git status: ?? .p2p/. Local-only records remain in .p2p/work/lookup and .p2p/work/parent; preview, grant, previous effect receipt and this resume report/log remain at /private/tmp/p2p-epic-repair-cases/S9-interrupted. No checkout handoff or records publication authorized. Changed paths: resume-actor-report.md, resume-command-evidence.jsonl, resume-approved-plan.md, canonical publication.md, evidence/resume-approved-plan.md, and helper publication history. Prior publication bytes retained by helper under history/ba652859d93c89261a1fee2077a28fadb898af0688f12832ebd313c096d48b43/publication.md.

Commands/output: /private/tmp/p2p-epic-repair-cases/S9-interrupted/resume-command-evidence.jsonl. Runner: /private/tmp/p2p-resume-observe.py; final verification/save script: /private/tmp/p2p-resume-finish.py. All tracker readback used the controlled case PATH and EPIC_TRACKER_ROOT.

Merge readiness: NOT ASSESSED

Next steps:
1. /merge-readiness https://fixture.invalid/epic/pull/17; review .p2p/work/lookup/review.md; proof .p2p/work/lookup/proof.md when approaching a merge decision. Required CI and approvals have not been assessed.
2. Transfer local reports, approvals, plan history, preview, grant and effect/resume receipts with the candidate Git object. Parent completion still requires full assembled-parent review and proof.
