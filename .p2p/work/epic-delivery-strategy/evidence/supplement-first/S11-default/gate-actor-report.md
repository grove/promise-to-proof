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

Stage reports saved through installed history helper and reread. Changed paths: review.md for S12/S1, proof.md for S1 only, publication.md, merge-readiness.md where invoked, evidence/gate-command-log.jsonl, helper history, and case-root gate reports/log. Product, contracts, refs and PR bodies unchanged.

# BLOCKED: https://fixture.invalid/epic/pull/18

Actor context: /root/scenario_publication_gates. Read-only assessment at 2026-09-26T22:24:07.026694+00:00.
Destination: trunk; actual base trunk at 159b5f50400479e1e5429b26b6c75e6d5f45682f; exact head 49fe63e3dd9a23776f2d7aba5b8f3152c3c2700c. Contract work/parent.md v1 SHA-256 38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada. Full product tree and all binding hashes validated against candidate.json. Current PR was reread through the configured simulator, and actual origin tips match.

Policy supplied by fixture owner: required-ci COMPLETED SUCCESS for current head and current repository approval. reviewDecision APPROVED is authoritative. Observed checks: [{"name": "required-ci", "status": "COMPLETED", "conclusion": "SUCCESS"}]. Approval: APPROVED. Saved review .p2p/work/parent/review.md and proof .p2p/work/parent/proof.md were separately evaluated.

Gates: Missing current full REVIEWED: report review.md; Missing current full PROVEN: report proof.md

Approved plan v1 SHA-256 7c433c3b4058d4953de87ae0408c29c7001c1d095ac5d60fae445fde5fd4b3c1; exact retained text in publication.md and .p2p/work/parent/slicing.md. Grouped child parent integration/review/proof remain separate.

Draft state observed: True. READY here assesses supplied gates; it does not change draft state, authorize merge, or perform the separate human ready-for-review transition. Required check status is the current-head rollup from the fixture service; no separate run SHA is exposed.
Synchronization: skipped by explicit read-only request. PR body unchanged. Evidence: evidence/gate-command-log.jsonl.

Proposed entry: Merge readiness: BLOCKED; observed 2026-09-26T22:24:07.026694+00:00; head 49fe63e3dd9a23776f2d7aba5b8f3152c3c2700c; base 159b5f50400479e1e5429b26b6c75e6d5f45682f; local report .p2p/work/parent/merge-readiness.md; Missing current full REVIEWED: report review.md; Missing current full PROVEN: report proof.md. Applies only to this observed state.

Next steps:
1. /repair-gaps .p2p/work/parent/proof.md; after authorized repair refresh full /prove work/parent.md and /review-implementation work/parent.md against current trunk, then rerun /merge-readiness https://fixture.invalid/epic/pull/18; read-only.

Final validation succeeded; git diff --exit-code passed and only .p2p/ is untracked. Evidence saved and reread through installed history helper. No live services were called.
