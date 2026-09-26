# BLOCKED: changed candidate lacks matching reports

Actor: /root/scenario_remaining_handoffs. One actual shared context for these cases; no delegation or independent reviewer contexts claimed.
Installed skill: /private/tmp/p2p-epic-repair-cases/S10-candidate-change/installed/publish-pr/SKILL.md sha256:cf9dcc91fe43e0ff75967b316abacdb02503e2d0f49f67c1ad54ccac869aabb0.
Bundled protocol: sha256:c916e48be9de29f423716518dc290a64b9c667bdf42b40da87dc346853957b43.
Commands and exact output: /private/tmp/p2p-epic-repair-cases/S10-candidate-change/handoff-command-evidence.jsonl. Only supplied fixture gh was used when tracker inspection was needed. No live network.
Authority: repair-request.md, local inspection and stage records only. No product, contract, ref, push, tracker, or merge effects performed.
Parent: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada; source specs/registry.md sha256:64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9.
Exact approved agreement bytes recoverable using `git show c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f:work/parent.md` and the same commit's specs/registry.md. Work files remain unchanged.

Contract: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9; source and parent agreement unchanged.
Saved candidate: git:c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f, recoverable from Git; saved comparison base c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f.
Current working candidate differs in registry.py: two trailing lines add `# Candidate repair preserves behavior.` Current registry.py sha256:e08c50ed582f802b9a99d90d09caad93c76796c8ccd5c82adf007e29a24dff15. Installed validation reports "product candidate changed". Even a comment-only product byte change invalidates exact candidate reuse under the installed protocol. No changed candidate is silently substituted into prior reports.
Review: .p2p/work/lookup/review.md; proof: .p2p/work/lookup/proof.md. Both retain historical meaning for git:c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f and its exact v1 agreement, not this changed working tree. Neither was rewritten or relabeled. No verification is manufactured.
Plan: .p2p/work/parent/slicing.md v1, exact approved section sha256:b67b46a4cba48649504916d2b2e873fdc0fc642d0f7fdfa7a32b41fd27cf79cd; lookup resolves grouped to epic/example, final parent destination trunk. Recoverable approved section follows.

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

Scope: full lookup R1, qualified parent v1:R2, capture prerequisite and inherited ASCII/no persistence/network constraints. Parent R4 still requires assembled-parent review/proof. This local byte change supplies no new product promise and needs no contract revision. No in-scope implementation defect was established by publication inspection.
Destination: fixture/epic; retained publication records describe PR 17 head child/lookup and base epic/example, but no current remote readback or usable exact preview is claimed after early candidate validation failure. Local target and HEAD remain c2e77a15fe58ecbd3a7b6b32be5516e4bf78d52f. Prior preview is stale. No ref, push, PR, code or contract action authorized or performed.
Only this publication report and retained history change. Working checkout remains untouched with its modified registry.py. No commit inputs/title/body are invented for an unverified candidate. Merge readiness: NOT ASSESSED.

Next steps:
1. Capture the intended complete changed candidate, preserving the old candidate/history: `python3 ../installed/publish-pr/scripts/p2p_filesystem.py --repo . capture work/lookup.md --base epic/example`. Inspect and retain its recoverable snapshot.
2. `/review-implementation work/lookup.md` against the actual approved target tip, and `/prove work/lookup.md` for the full contract on that same exact changed candidate. Both must be fresh; previous proof is historical only for old bytes.
3. Once matching full reports exist, `/publish-pr work/lookup.md; draft only` to recheck routing, remote state and prepare an exact current preview. No publication effects are authorized by this handoff.
