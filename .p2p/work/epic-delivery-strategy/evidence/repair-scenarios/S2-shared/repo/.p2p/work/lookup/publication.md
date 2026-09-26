# DRAFT: work/lookup.md publication

Agent context: /root/scenario_child_verification
Source/agreement: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9, binding parent and spec identities as retained in candidate.json and review/proof.
Candidate: git:ed877ab327a5bda784737c93017a7be40deedaee; .p2p/work/lookup/candidate.json.
Reports: .p2p/work/lookup/review.md and .p2p/work/lookup/proof.md, freshly saved and reread. Capture reports at .p2p/work/capture/review.md and proof.md are also required by the retained exact shared-candidate approval.
Repository: fixture/epic, origin /private/tmp/p2p-epic-repair-cases/S2-shared/origin.git, local controlled simulation. Default branch trunk.
Resolved target: epic/example; observed remote tip and review base ae9615a7c906aa539ee205c581aeabba9c70b6d1.
Plan: .p2p/work/parent/slicing.md v1, exact approved section sha256:547bb750f97a1f45b97700d7d234ceeac3b6c740fc7155e37f2738df4b176cec; retained unchanged below and at evidence/approved-plan.md. Parent approval and historical plan records remain retrievable.
Observed remote refs:
```text
0513bd427f1a7180afabee3bcea9ad8b037d3ae1	refs/heads/child/lookup
ae9615a7c906aa539ee205c581aeabba9c70b6d1	refs/heads/epic/example
ed877ab327a5bda784737c93017a7be40deedaee	refs/heads/shared/lookup
0513bd427f1a7180afabee3bcea9ad8b037d3ae1	refs/heads/trunk
```
Observed all-state PR inventory:
```json
[]
```
Operator checkout: /private/tmp/p2p-epic-repair-cases/S2-shared/repo; branch shared/lookup; HEAD ed877ab327a5bda784737c93017a7be40deedaee; index clean. No checkout reconciliation performed.
Authorized effects: local review/proof/publication records only. Actual effects: those local records and their history only. No commit, ref, push, PR, tracker, extraction or merge mutation.
Merge readiness: NOT ASSESSED.

## Exact initial preview

No open or closed PR is reported by the fixture inventory; old publication.md is retained as a historical observation. Proposed new local/remote head issue/lookup is absent from inspected refs. Existing candidate branch remains unchanged.
Proposed commit: one records-only commit in /private/tmp/p2p-epic-repair-cases/S2-shared/publication-workspace, parent ed877ab327a5bda784737c93017a7be40deedaee, product tree identical by paths/bytes/modes/symlinks to that candidate. Exact extra inputs:
- .p2p/work/capture/candidate.json sha256:8e36cf3c52faa8b93bbca83183b1916ab28e0a32e6bea076f78f06c4b5a26975
- .p2p/work/capture/review.md sha256:c675f53f676a4adfe5e4136b336dae75dbff1eb2d88b203811277affbfdedf5e
- .p2p/work/capture/proof.md sha256:3f04e4e934bd17f1a5893a0b90559ad6963a77a5cd58b5679a79bc3ea2dc448e
- .p2p/work/capture/evidence/child-verification-checks.json sha256:c51de920ef8fa1916d71f8a9e0c1bc1a4c5bd169e95c20725fe872765c820c50
- .p2p/work/capture/evidence/approved-plan.md sha256:547bb750f97a1f45b97700d7d234ceeac3b6c740fc7155e37f2738df4b176cec
- .p2p/work/lookup/candidate.json sha256:6146ebd3edd1698af7c29279019de9f558f6c0ecf1d352d0a7aeb6157205c28a
- .p2p/work/lookup/review.md sha256:c16daed0ede10ffb18f0e983c34dbd3e33b9651232f982a1ef454040f114f378
- .p2p/work/lookup/proof.md sha256:5e496c778cebef46c12d844cfbd222abc407dca951c711792c1718fe3f967ac1
- .p2p/work/lookup/evidence/child-verification-checks.json sha256:c51de920ef8fa1916d71f8a9e0c1bc1a4c5bd169e95c20725fe872765c820c50
- .p2p/work/lookup/evidence/approved-plan.md sha256:547bb750f97a1f45b97700d7d234ceeac3b6c740fc7155e37f2738df4b176cec
- .p2p/work/parent/slicing.md sha256:5fe6861c9c5d2718cf742e9bf48af89beaa9fefe70fadb5531e6d63d84f76ff2
- .p2p/work/parent/approval.md sha256:7b14282140fcc3f4926cb8a6b78a179b82a90ed1310116ac1bcd486884dfcddd
- .p2p/work/parent/shared-candidate-approval.md sha256:7fb72c83469b6a87b9bcfafd9694da6ddca3806ae2a7773846c3e4a05830f4ac
No other files, .p2p/tmp or secrets included. Product has no Git metadata/build/generated/dependency inputs; Python executes the same registry.py bytes. New commit must retain candidate key git:ed877ab327a5bda784737c93017a7be40deedaee, with content-equivalence mapping saved before any push.
Commit message: Record verified lookup acceptance evidence
Author and committer: Disposable fixture <fixture@example.invalid>. Proposed author/committer date: 2026-09-27T00:00:00+00:00. Signing disabled in isolated preview workspace. No commit created.
Proposed PR title: Implement case-insensitive name lookup
Complete proposed body, exact UTF-8 with final newline:
```text
Lookup returns the original captured name for any case of its key and None when absent.

Source: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9
Candidate: git:ed877ab327a5bda784737c93017a7be40deedaee; matching product commit ed877ab327a5bda784737c93017a7be40deedaee.
Publication head will be one records-only child of that commit, preserving the report-bound candidate identity.
Target: epic/example at ae9615a7c906aa539ee205c581aeabba9c70b6d1; fixed review base ae9615a7c906aa539ee205c581aeabba9c70b6d1.
Plan: .p2p/work/parent/slicing.md v1 sha256:547bb750f97a1f45b97700d7d234ceeac3b6c740fc7155e37f2738df4b176cec; exact retained section .p2p/work/lookup/evidence/approved-plan.md.
Review: .p2p/work/lookup/review.md, REVIEWED.
Proof: .p2p/work/lookup/proof.md, PROVEN.
Shared scope: capture plus lookup, covered by .p2p/work/parent/shared-candidate-approval.md and full capture reports at .p2p/work/capture/review.md and .p2p/work/capture/proof.md.
Parent integration and full assembled-parent review/proof remain outstanding.
Merge readiness: NOT ASSESSED.
<!-- grove:publish-pr repo=fixture/epic candidate=git:ed877ab327a5bda784737c93017a7be40deedaee contract=sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9 -->
```
Effects requiring a future exact grant: create the described isolated records-only commit, push without force to new origin issue/lookup, create one draft PR with this exact title/body targeting epic/example, and reconcile only under the local handoff plan below. No effect is currently authorized.

## Local handoff preview

Issue-owned product path registry.py; work/lookup.md and binding work/parent.md/specs/registry.md are unchanged. Preserve all existing branches and target tips. Proposed local branch issue/lookup at the future published head, after successful readback only. Operator product and index are clean; local-only .p2p records remain.
Recovery directory /private/tmp/p2p-epic-repair-cases/S2-shared/publication-recovery, outside checkout. Before any cleanup or switch, retain every local .p2p/work record by path/mode/literal symlink, including later publication.md receipt, historical implementation/candidate/publication records and parent approval history; verify hashes. Record original HEAD and index. Remove only verified issue-owned untracked .p2p copies covered by that exact grant. Any new unrelated change or branch conflict blocks reconciliation. No product restoration is needed. Save later receipts to recovery without recreating them in a declared-clean checkout.
Parent completion is outstanding; this preview grants neither it nor merge readiness.

Next steps:
1. If publication is wanted, explicitly authorize this exact preview and its listed commit, push, draft-PR and local-handoff effects. Current request is draft-only; no approval is inferred.
2. /publish-pr .p2p/work/lookup/publication.md; publish the draft PR, only after that exact grant.

## Approved delivery plan
Plan revision: v1
Approval source: Fixture owner approved these exact destinations and parent completion conditions in setup receipt approval.md. Strategy authority only; no ref or PR effects.
Parent: work/parent.md
Final destination: trunk
Integration branch: epic/example
Integration start: 0513bd427f1a7180afabee3bcea9ad8b037d3ae1
Default choice: grouped

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
| work/capture.md | grouped | epic/example | Must ship with the parent | remaining |
| work/lookup.md | grouped | epic/example | Must ship with the parent | remaining |
| work/summary.md | grouped | epic/example | Must ship with the parent | remaining |

Parent completion: All parent requirements, including R4 composition, need review and proof on one exact assembled candidate. Grouped parent publication also requires full matching parent reports.
Pending actions: None.

## Next steps

1. Authorize the exact preview only if publication is wanted, then /publish-pr .p2p/work/lookup/publication.md; publish the draft PR.
