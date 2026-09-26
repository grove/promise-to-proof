# BLOCKED: parent publication

Expected final destination trunk. Saved parent proof is NOT PROVEN: R1 and R4 are disproven on this exact assembled candidate. Full parent review is absent. Passing child reports or CI cannot replace the missing full matching parent report pair. No draft PR creation or repair is performed. Existing proof retained byte-for-byte.

Actor context: /root/scenario_publication_gates. One actual shared context; no independent reviewers or delegation.
Contract: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada; exact bytes recoverable with git show 49fe63e3dd9a23776f2d7aba5b8f3152c3c2700c:work/parent.md.
Candidate: git:49fe63e3dd9a23776f2d7aba5b8f3152c3c2700c; comparison base 159b5f50400479e1e5429b26b6c75e6d5f45682f. Full committed product tree and binding inputs validated by installed helper; no product drift.
Evidence: evidence/gate-command-log.jsonl contains exact commands, outputs, exit status and environment. Python 3.14.7. Initial validate invocation omitted required --base; corrected validation passed. No product/ref/PR effects authorized or performed.
Plan: .p2p/work/parent/slicing.md v1; exact approved section sha256:7c433c3b4058d4953de87ae0408c29c7001c1d095ac5d60fae445fde5fd4b3c1. Approval source .p2p/work/parent/approval.md.
```markdown
## Approved delivery plan
Plan revision: v1
Approval source: Fixture owner approved these exact destinations and parent completion conditions in setup receipt approval.md. Strategy authority only; no ref or PR effects.
Parent: work/parent.md
Final destination: trunk
Integration branch: epic/example
Integration start: 159b5f50400479e1e5429b26b6c75e6d5f45682f
Default choice: grouped

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
| work/capture.md | grouped | epic/example | Must ship with the parent | remaining |
| work/lookup.md | grouped | epic/example | Must ship with the parent | remaining |
| work/summary.md | grouped | epic/example | Must ship with the parent | remaining |

Parent completion: All parent requirements, including R4 composition, need review and proof on one exact assembled candidate. Grouped parent publication also requires full matching parent reports.
Pending actions: None.
```

Report identities:
- .p2p/work/parent/candidate.json sha256:954a81c1dfbb3d63ebf8bed7f4134abaf6d96645360fbbc8055fd2ef6902b9a9
- .p2p/work/parent/proof.md sha256:6a9821b8e3b1c00e906a0ee16ecce6ece4146746fc87ce96fbdc5f32e5a5905f

Destination repository: fixture/epic. Git origin is the case-local bare repository. No new commit inputs or proposed branch are necessary for this no-effect assessment. Local checkout remains at its existing HEAD and branch; only durable records change. Records are local, not claimed present in the remote commit.

Merge readiness: NOT ASSESSED

Next steps:
1. /repair-gaps .p2p/work/parent/proof.md, then fresh full /prove work/parent.md and /review-implementation work/parent.md against current trunk before another publication preview.
