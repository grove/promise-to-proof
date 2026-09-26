# DRAFT: PR 17 retargeting preview

Actor: /root/scenario_retarget_publisher

Exact preview: evidence/retarget-preview.json sha256:2db3b2bbd545f144f87974d9f0aa70411efae90f883749b91369a53ded2e98e2

{
  "status": "DRAFT",
  "actor": "/root/scenario_retarget_publisher",
  "repository": "fixture/epic",
  "remote": "/private/tmp/p2p-epic-valid-v1isv6j3/S9-default/origin.git",
  "source": "specs/registry.md via work/parent.md",
  "contract_revision": "v1",
  "candidate": "git:c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f",
  "publication_commit": "c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f",
  "candidate_record": {
    "commit": "c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f",
    "comparison_base": "c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f",
    "work_item": "work/lookup.md",
    "work_item_sha256": "fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9",
    "binding_inputs": [
      {
        "path": "specs/registry.md",
        "sha256": "64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9"
      },
      {
        "path": "work/parent.md",
        "sha256": "38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada"
      }
    ]
  },
  "identities_sha256": {
    "work/lookup.md": "fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9",
    "work/parent.md": "38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada",
    "specs/registry.md": "64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9",
    ".p2p/work/lookup/candidate.json": "b0cd299b9b80d0d792cf373cccbb1b53dc21b67d4aed43fc5c7dbac82cc306bb",
    ".p2p/work/lookup/review.md": "cfd128e974196ba5b9f9820306ebe27eb74b306b10428b09e64db9397e109af2",
    ".p2p/work/lookup/proof.md": "1b2f31d7bd4444bcb1beca9c4ee37296320a9bb5507297f78fe42b59936c9afa",
    ".p2p/work/lookup/evidence/review-commands.txt": "5ba667a692599ef25236872c7f6fe396aa0c9978a9aabd891e9114148d080fda",
    ".p2p/work/lookup/evidence/proof-commands.txt": "221489aac2e13cdb1f072620322d8288912d512fbeac56f5d272880ddfb3e291",
    ".p2p/work/lookup/evidence/common-identity.txt": "c047ac1703e5a2244f3495b15b9d4eefafbb67bb05dbdee248bf2c93420d0bb7",
    ".p2p/work/lookup/evidence/approved-plan.md": "b86ffd9b9b6ccbd0615efbcc57d3da023e1a8a0c185303a28832aafc0490ffe2",
    ".p2p/work/parent/slicing.md": "64ff1e1837c2600fe816fff70614377a3aa63dd7113d252c584d2e8de9718597",
    ".p2p/work/parent/approval.md": "7b14282140fcc3f4926cb8a6b78a179b82a90ed1310116ac1bcd486884dfcddd",
    ".p2p/work/lookup/publication.md": "999ebe002c1ce7bb6767ee587234f948a9987dcd8e6bffcea946a20ca8888401",
    ".p2p/work/lookup/evidence/publication-inspection.txt": "0cb3fa4e696406c4d4c74752aa54d1d6cceccd6109a488c7c866e2aba4368242"
  },
  "review_status": "REVIEWED",
  "proof_status": "PROVEN",
  "plan_revision": "v1",
  "plan_sha256": "b86ffd9b9b6ccbd0615efbcc57d3da023e1a8a0c185303a28832aafc0490ffe2",
  "plan_text": "## Approved delivery plan\nPlan revision: v1\nApproval source: Fixture owner approved these exact destinations and parent completion conditions in setup receipt approval.md. Strategy authority only; no ref or PR effects.\nParent: work/parent.md\nFinal destination: trunk\nIntegration branch: epic/example\nIntegration start: c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f\nDefault choice: grouped\n\n| Child | Choice | Destination | Reason | State |\n|---|---|---|---|---|\n| work/capture.md | grouped | epic/example | Must ship with the parent | remaining |\n| work/lookup.md | grouped | epic/example | Must ship with the parent | remaining |\n| work/summary.md | grouped | epic/example | Must ship with the parent | remaining |\n\nParent completion: All parent requirements, including R4 composition, need review and proof on one exact assembled candidate. Grouped parent publication also requires full matching parent reports.\nPending actions: None.\n\n",
  "pr_before": {
    "url": "https://fixture.invalid/epic/pull/17",
    "number": 17,
    "state": "OPEN",
    "headRefName": "child/lookup",
    "headRefOid": "c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f",
    "baseRefName": "trunk",
    "baseRefOid": "c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f",
    "title": "Lookup names",
    "body": "Human note: keep this sentence byte-for-byte.\n<!-- grove:publish-pr repo=fixture/epic candidate=git:c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f contract=sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9 -->\n",
    "isDraft": true
  },
  "old_target": "trunk",
  "old_target_tip": "c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f",
  "new_target": "epic/example",
  "new_target_tip": "c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f",
  "comparison_base": "c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f",
  "effect": [
    "gh",
    "pr",
    "edit",
    "https://fixture.invalid/epic/pull/17",
    "--base",
    "epic/example"
  ],
  "effect_authority": "None yet; strategy-only approval does not authorize PR edit.",
  "preserve": [
    "headRefName",
    "headRefOid",
    "title",
    "body",
    "isDraft",
    "number",
    "url",
    "state"
  ],
  "checkout": {
    "path": "/private/tmp/p2p-epic-valid-v1isv6j3/S9-default/repo",
    "branch": "trunk",
    "HEAD": "c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f",
    "index": "clean",
    "local_records": ".p2p/ untracked; retained in place",
    "handoff": "publication-only retarget; no checkout reconciliation"
  },
  "scope": "Candidate equals both target tips. Complete diff empty, no sibling payload introduced. Capture prerequisite verified by saved full reports.",
  "record_availability": "Reports and plan are local-only, absent from existing PR commit. Retarget creates no records commit. Retain and transfer local records for readiness.",
  "merge_readiness": "NOT ASSESSED"
}

Observed effects: none. Local reports only. Previous publication observation retained through filesystem history. No commit, push, new branch, replacement PR, body edit, or checkout handoff proposed. Repository has no additional template/contribution rules. Simulator repository identity, marker, origin refs and unique PR agree; optional head repository fields unavailable.

Remaining work: exact simulator base-edit grant; immediately recheck plan, reports, PR and refs; perform one base-only edit; read back all state and recheck plan. Assembled-parent review/proof including R4 remain separate. Local records need transfer and are not claimed published.

Merge readiness: NOT ASSESSED

Next steps:
1. Authorize exact JSON preview SHA-256 for the one simulator PR base edit.
2. Resume `/publish-pr` with that grant and retain full readback.
