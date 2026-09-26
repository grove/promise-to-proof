# DRAFT: standalone existing publication

Target trunk is explicit and matches saved comparison base. No parent plan is supplied or required. PR 19 and real solo local/bare-origin ref already identify this exact candidate; do not create a duplicate or empty PR. Full local REVIEWED and PROVEN reports now exist. Existing PR title/body/draft state retained. This preview proposes zero remote effects.

Actor context: /root/scenario_publication_gates. One actual shared context; no independent reviewers or delegation.
Contract: work/solo.md v1 sha256:294bc01757864083fefd58e5f95e3ffd357a4d83201394d1eac39018aaccac23; exact bytes recoverable with git show f62b5329a22f996af6bb550cc1c7d75223af303c:work/solo.md.
Candidate: git:f62b5329a22f996af6bb550cc1c7d75223af303c; comparison base f62b5329a22f996af6bb550cc1c7d75223af303c. Full committed product tree and binding inputs validated by installed helper; no product drift.
Evidence: evidence/gate-command-log.jsonl contains exact commands, outputs, exit status and environment. Python 3.14.7. Initial validate invocation omitted required --base; corrected validation passed. No product/ref/PR effects authorized or performed.

Report identities:
- .p2p/work/solo/candidate.json sha256:069e6712a30abc1d7e00bf7512cccf82225b3a96dc126e585e6c8fb9bef6490b
- .p2p/work/solo/review.md sha256:926e635ba43f92f62811a1b17fe1b63edcaff5eea6574314506ab2f88aee1cca
- .p2p/work/solo/proof.md sha256:a5b32c1fbd9912aa937041f2a011dee92726ae750a1bdb326561756ce9541dcc

Stage reports saved through installed history helper and reread. Changed paths: review.md for S12/S1, proof.md for S1 only, publication.md, merge-readiness.md where invoked, evidence/gate-command-log.jsonl, helper history, and case-root gate reports/log. Product, contracts, refs and PR bodies unchanged.

# READY: https://fixture.invalid/epic/pull/19

Actor context: /root/scenario_publication_gates. Read-only assessment at 2026-09-26T22:24:07.737461+00:00.
Destination: trunk; actual base trunk at f62b5329a22f996af6bb550cc1c7d75223af303c; exact head f62b5329a22f996af6bb550cc1c7d75223af303c. Contract work/solo.md v1 SHA-256 294bc01757864083fefd58e5f95e3ffd357a4d83201394d1eac39018aaccac23. Full product tree and all binding hashes validated against candidate.json. Current PR was reread through the configured simulator, and actual origin tips match.

Policy supplied by fixture owner: required-ci COMPLETED SUCCESS for current head and current repository approval. reviewDecision APPROVED is authoritative. Observed checks: [{"name": "required-ci", "status": "COMPLETED", "conclusion": "SUCCESS"}]. Approval: APPROVED. Saved review .p2p/work/solo/review.md and proof .p2p/work/solo/proof.md were separately evaluated.

Gates: All supplied candidate, agreement, full report, required CI and repository approval gates pass for this observed state.

Standalone Parent: None; no parent delivery plan required.

Draft state observed: True. READY here assesses supplied gates; it does not change draft state, authorize merge, or perform the separate human ready-for-review transition. Required check status is the current-head rollup from the fixture service; no separate run SHA is exposed.
Synchronization: skipped by explicit read-only request. PR body unchanged. Evidence: evidence/gate-command-log.jsonl.

Proposed entry: Merge readiness: READY; observed 2026-09-26T22:24:07.737461+00:00; head f62b5329a22f996af6bb550cc1c7d75223af303c; base f62b5329a22f996af6bb550cc1c7d75223af303c; local report .p2p/work/solo/merge-readiness.md; supplied gates pass; draft state unchanged; separate merge authority required. Applies only to this observed state.

Next steps:
1. Retain this read-only assessment. Any readiness-body synchronization, draft transition or merge requires separate authorization; reread exact head and gates before that decision.

Final validation succeeded; git diff --exit-code passed and only .p2p/ is untracked. Evidence saved and reread through installed history helper. No live services were called.
