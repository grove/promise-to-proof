# DRAFT: work/lookup.md publication

Agent context: /root/scenario_child_verification
Source/agreement: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9, binding parent and spec identities as retained in candidate.json and review/proof.
Candidate: git:6200ab72615e708585b48bcf3cbb7f9c45d3573e; .p2p/work/lookup/candidate.json.
Reports: .p2p/work/lookup/review.md and .p2p/work/lookup/proof.md, freshly saved and reread. 
Repository: fixture/epic, origin /private/tmp/p2p-epic-repair-cases/S3-publication/origin.git, local controlled simulation. Default branch trunk.
Resolved target: epic/example; observed remote tip and review base c74003fe4a40add496b1888ded0706494f49a47d.
Plan: .p2p/work/parent/slicing.md v1, exact approved section sha256:f97a0dda89221fcb76d436094a5cccc88b931ba77c0b8da35c2efaec49e6f304; retained unchanged below and at evidence/approved-plan.md. Parent approval and historical plan records remain retrievable.
Observed remote refs:
```text
bb61c3a7696003d174133c7ca6250af601901899	refs/heads/child/lookup
c74003fe4a40add496b1888ded0706494f49a47d	refs/heads/epic/example
6200ab72615e708585b48bcf3cbb7f9c45d3573e	refs/heads/feature/lookup
bb61c3a7696003d174133c7ca6250af601901899	refs/heads/trunk
```
Observed all-state PR inventory:
```json
[]
```
Operator checkout: /private/tmp/p2p-epic-repair-cases/S3-publication/repo; branch feature/lookup; HEAD 6200ab72615e708585b48bcf3cbb7f9c45d3573e; index clean. No checkout reconciliation performed.
Authorized effects: local review/proof/publication records only. Actual effects: those local records and their history only. No commit, ref, push, PR, tracker, extraction or merge mutation.
Merge readiness: NOT ASSESSED.

## Exact initial preview

No open or closed PR is reported by the fixture inventory; old publication.md is retained as a historical observation. Proposed new local/remote head issue/lookup is absent from inspected refs. Existing candidate branch remains unchanged.
Proposed commit: one records-only commit in /private/tmp/p2p-epic-repair-cases/S3-publication/publication-workspace, parent 6200ab72615e708585b48bcf3cbb7f9c45d3573e, product tree identical by paths/bytes/modes/symlinks to that candidate. Exact extra inputs:
- .p2p/work/lookup/candidate.json sha256:0e904bf9d0c3d6daf0d50a488faef1f3e282b0f31c57bb4e8499cc87150882ac
- .p2p/work/lookup/review.md sha256:70676c73ab9daef15ab58c5ab0b27a46a58828ed4a97f7c004d32ebcb4538c39
- .p2p/work/lookup/proof.md sha256:a963f840ee6a5cf201240521b0f3fb153198c24125885a4b21c216ce841a0f4c
- .p2p/work/lookup/evidence/child-verification-checks.json sha256:8d03f312fcccddee7c582bde457e93f75803a7a7a9661f840f203989b4c9e690
- .p2p/work/lookup/evidence/approved-plan.md sha256:f97a0dda89221fcb76d436094a5cccc88b931ba77c0b8da35c2efaec49e6f304
- .p2p/work/parent/slicing.md sha256:ca21961260a9ceef96737031111e1a8de1312c43fc4ef08c3042060343d17983
- .p2p/work/parent/approval.md sha256:7b14282140fcc3f4926cb8a6b78a179b82a90ed1310116ac1bcd486884dfcddd
No other files, .p2p/tmp or secrets included. Product has no Git metadata/build/generated/dependency inputs; Python executes the same registry.py bytes. New commit must retain candidate key git:6200ab72615e708585b48bcf3cbb7f9c45d3573e, with content-equivalence mapping saved before any push.
Commit message: Record verified lookup acceptance evidence
Author and committer: Disposable fixture <fixture@example.invalid>. Proposed author/committer date: 2026-09-27T00:00:00+00:00. Signing disabled in isolated preview workspace. No commit created.
Proposed PR title: Implement case-insensitive name lookup
Complete proposed body, exact UTF-8 with final newline:
```text
Lookup returns the original captured name for any case of its key and None when absent.

Source: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9
Candidate: git:6200ab72615e708585b48bcf3cbb7f9c45d3573e; matching product commit 6200ab72615e708585b48bcf3cbb7f9c45d3573e.
Publication head will be one records-only child of that commit, preserving the report-bound candidate identity.
Target: epic/example at c74003fe4a40add496b1888ded0706494f49a47d; fixed review base c74003fe4a40add496b1888ded0706494f49a47d.
Plan: .p2p/work/parent/slicing.md v1 sha256:f97a0dda89221fcb76d436094a5cccc88b931ba77c0b8da35c2efaec49e6f304; exact retained section .p2p/work/lookup/evidence/approved-plan.md.
Review: .p2p/work/lookup/review.md, REVIEWED.
Proof: .p2p/work/lookup/proof.md, PROVEN.
Capture prerequisite is integrated at the target.
Parent integration and full assembled-parent review/proof remain outstanding.
Merge readiness: NOT ASSESSED.
<!-- grove:publish-pr repo=fixture/epic candidate=git:6200ab72615e708585b48bcf3cbb7f9c45d3573e contract=sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9 -->
```
Effects requiring a future exact grant: create the described isolated records-only commit, push without force to new origin issue/lookup, create one draft PR with this exact title/body targeting epic/example, and reconcile only under the local handoff plan below. No effect is currently authorized.

## Local handoff preview

Issue-owned product path registry.py; work/lookup.md and binding work/parent.md/specs/registry.md are unchanged. Preserve all existing branches and target tips. Proposed local branch issue/lookup at the future published head, after successful readback only. Operator product and index are clean; local-only .p2p records remain.
Recovery directory /private/tmp/p2p-epic-repair-cases/S3-publication/publication-recovery, outside checkout. Before any cleanup or switch, retain every local .p2p/work record by path/mode/literal symlink, including later publication.md receipt, historical implementation/candidate/publication records and parent approval history; verify hashes. Record original HEAD and index. Remove only verified issue-owned untracked .p2p copies covered by that exact grant. Any new unrelated change or branch conflict blocks reconciliation. No product restoration is needed. Save later receipts to recovery without recreating them in a declared-clean checkout.
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
Integration start: bb61c3a7696003d174133c7ca6250af601901899
Default choice: grouped

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
| work/capture.md | independent | trunk | Acceptable if no sibling ships | remaining |
| work/lookup.md | grouped | epic/example | Must ship with the parent | remaining |
| work/summary.md | grouped | epic/example | Must ship with the parent | remaining |

Parent completion: All parent requirements, including R4 composition, need review and proof on one exact assembled candidate. Grouped parent publication also requires full matching parent reports.
Pending actions: None.

