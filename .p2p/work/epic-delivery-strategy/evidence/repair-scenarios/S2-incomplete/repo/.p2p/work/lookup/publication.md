# BLOCKED: work/lookup.md publication

Agent context: /root/scenario_child_verification
Source/agreement: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9, binding parent and spec identities as retained in candidate.json and review/proof.
Candidate: git:194af4c2baba22b019b76bb36be64bf7c3b1b589; .p2p/work/lookup/candidate.json.
Reports: .p2p/work/lookup/review.md and .p2p/work/lookup/proof.md, freshly saved and reread. Capture reports at .p2p/work/capture/review.md and proof.md are also required by the retained exact shared-candidate approval.
Repository: fixture/epic, origin /private/tmp/p2p-epic-repair-cases/S2-incomplete/origin.git, local controlled simulation. Default branch trunk.
Resolved target: epic/example; observed remote tip and review base 66a04c3617995cce9bf4cbd282e28d8f09cfd906.
Plan: .p2p/work/parent/slicing.md v1, exact approved section sha256:a7f70fc11fc26bd176526c63c3fd344a62da1d15dfcb14e05b0992c3ff6eeeb9; retained unchanged below and at evidence/approved-plan.md. Parent approval and historical plan records remain retrievable.
Observed remote refs:
```text
e178ae560d8e8720598fcd825f007d63b86f51a1	refs/heads/child/lookup
66a04c3617995cce9bf4cbd282e28d8f09cfd906	refs/heads/epic/example
194af4c2baba22b019b76bb36be64bf7c3b1b589	refs/heads/shared/lookup
e178ae560d8e8720598fcd825f007d63b86f51a1	refs/heads/trunk
```
Observed all-state PR inventory:
```json
[
  {
    "number": 17,
    "url": "https://fixture.invalid/epic/pull/17",
    "headRefName": "shared/lookup",
    "headRefOid": "194af4c2baba22b019b76bb36be64bf7c3b1b589",
    "baseRefName": "epic/example",
    "title": "Lookup names",
    "body": "Work item: work/lookup.md\nHuman note: keep this sentence byte-for-byte.\n<!-- grove:publish-pr repo=fixture/epic candidate=git:194af4c2baba22b019b76bb36be64bf7c3b1b589 contract=sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9 -->\n",
    "isDraft": true
  }
]
```
Operator checkout: /private/tmp/p2p-epic-repair-cases/S2-incomplete/repo; branch shared/lookup; HEAD 194af4c2baba22b019b76bb36be64bf7c3b1b589; index clean. No checkout reconciliation performed.
Authorized effects: local review/proof/publication records only. Actual effects: those local records and their history only. No commit, ref, push, PR, tracker, extraction or merge mutation.
Merge readiness: NOT ASSESSED.

## Blocker and remaining work

Lookup R1 is disproven and review requires changes; complete shared approval cannot waive that failure. Existing PR 17 remains untouched.
No publication commit, snapshot-to-commit mapping, ref or PR change was attempted. This is BLOCKED, not PARTIAL. Approval of routing v2 alone grants no publication effect.
No local handoff is proposed while publication subject reconciliation is unresolved; existing records and worktree remain intact.

Next steps:
1. /repair-gaps .p2p/work/lookup/proof.md under repair authority, then full fresh review and proof of both shared contributions.
2. Reinvoke /publish-pr work/lookup.md; draft only after the blocker is resolved. Parent completion remains separately unproven.

## Approved delivery plan
Plan revision: v1
Approval source: Fixture owner approved these exact destinations and parent completion conditions in setup receipt approval.md. Strategy authority only; no ref or PR effects.
Parent: work/parent.md
Final destination: trunk
Integration branch: epic/example
Integration start: e178ae560d8e8720598fcd825f007d63b86f51a1
Default choice: grouped

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
| work/capture.md | grouped | epic/example | Must ship with the parent | remaining |
| work/lookup.md | grouped | epic/example | Must ship with the parent | remaining |
| work/summary.md | grouped | epic/example | Must ship with the parent | remaining |

Parent completion: All parent requirements, including R4 composition, need review and proof on one exact assembled candidate. Grouped parent publication also requires full matching parent reports.
Pending actions: None.

## Next steps

1. Resolve the blocker above before /publish-pr work/lookup.md; draft only.
