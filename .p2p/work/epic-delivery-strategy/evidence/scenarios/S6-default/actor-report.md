# BLOCKED: publish-pr work/lookup.md
Agent context: /root/scenario_routing_batch (shared host context; fixtures are separate)
Run ID: S6-default-10138930-ac74-4d5a-bca4-01d6b067e69d
Contract: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9
Parent: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada
Candidate: 991b57f28c07887b5e395b020971f4d5bf510a51
Plan: .p2p/work/parent/slicing.md v1 sha256:3465dcdb6f9ec04d686cc2db0f48f16a863bd0ec8497e41dd22cccb03976252e; exact text retained in command-evidence.txt.

Expected destination epic/example (approved v1 grouped plan); requested/actual PR destination trunk. Plan approval is strategy-only and cannot authorize a PR base edit. Existing reports include no full REVIEWED or PROVEN verdicts, so publication additionally lacks required report pair.
No preview for trunk can be authorized under current routing. No commit, push, PR creation, retarget or body edit performed.
Next steps:
1. For a desired strategy change, /slice-contract work/parent.md; resolve the changed product delivery intent and approve exact routing before publication.
2. Otherwise retain epic/example, obtain full /review-implementation work/lookup.md against its current target tip and /prove work/lookup.md, then /publish-pr work/lookup.md; target epic/example; draft only.

# BLOCKED: merge-readiness PR 17
Agent context: /root/scenario_routing_batch (shared host context; fixtures are separate)
Run ID: S6-default-10138930-ac74-4d5a-bca4-01d6b067e69d
Contract: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9
Parent: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada
Candidate: 991b57f28c07887b5e395b020971f4d5bf510a51
Plan: .p2p/work/parent/slicing.md v1 sha256:3465dcdb6f9ec04d686cc2db0f48f16a863bd0ec8497e41dd22cccb03976252e; exact text retained in command-evidence.txt.

Expected destination epic/example (approved v1 grouped plan); requested/actual PR destination trunk. Plan approval is strategy-only and cannot authorize a PR base edit. Existing reports include no full REVIEWED or PROVEN verdicts, so publication additionally lacks required report pair.
PR https://fixture.invalid/epic/pull/17 is OPEN at head/base 991b57f28c07887b5e395b020971f4d5bf510a51. Simulated required-ci SUCCESS and reviewDecision APPROVED do not cure destination mismatch or missing reports. Grouped parent integration, full parent review/proof and final readiness remain separate. Synchronization skipped: request explicitly withholds tracker writes; human body is preserved.
Proposed readiness entry: Merge readiness: BLOCKED — observed 2026-09-27; exact head/base 991b57f28c07887b5e395b020971f4d5bf510a51, actual target trunk, expected epic/example, missing matching full review/proof; local report .p2p/work/lookup/merge-readiness.md. Applies only to this observed state.
Next steps:
1. /publish-pr work/lookup.md; prepare a verified retarget preview for https://fixture.invalid/epic/pull/17 from trunk to epic/example after full review and proof; request explicit authority for that exact base edit.
2. Reassess /merge-readiness https://fixture.invalid/epic/pull/17 after confirmed retarget and fresh applicable reports.

Retained command evidence: .p2p/work/lookup/evidence/scenario-command-evidence.txt sha256:991b57af92f96e578edeacb94ff8d5a036538ad27e9cdca9385f3ecad774e460
