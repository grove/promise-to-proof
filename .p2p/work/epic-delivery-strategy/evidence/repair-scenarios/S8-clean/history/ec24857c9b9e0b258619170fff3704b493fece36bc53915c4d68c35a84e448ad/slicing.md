# Registry decomposition

## Approved delivery plan
Plan revision: v1
Approval source: Fixture owner approved these exact destinations and parent completion conditions in setup receipt approval.md. Strategy authority only; no ref or PR effects.
Parent: work/parent.md
Final destination: trunk
Integration branch: epic/example
Integration start: d4125733f93c976ce218833dc8c995b58f0cbdf4
Default choice: grouped

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
| work/capture.md | grouped | epic/example | Must ship with the parent | remaining |
| work/lookup.md | grouped | epic/example | Must ship with the parent | remaining |
| work/summary.md | grouped | epic/example | Must ship with the parent | remaining |

Parent completion: All parent requirements, including R4 composition, need review and proof on one exact assembled candidate. Grouped parent publication also requires full matching parent reports.
Pending actions: None.

## Contributions
Capture contributes R1, lookup R2, summary R3; full R4 is verified on the assembled parent. Lookup requires actual capture behavior. Parent text sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada.

## Proposed delivery plan
Plan revision: v2
Approval source: Pending exact proposal approval; request.md authorizes this preview only.
Parent: work/parent.md
Final destination: trunk
Integration branch: epic/example
Integration start: d4125733f93c976ce218833dc8c995b58f0cbdf4
Default choice: grouped

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
| work/capture.md | default | epic/example | Existing grouped decision unchanged. | remaining |
| work/lookup.md | independent | trunk | User confirms lookup acceptable without remaining siblings. | remaining |
| work/summary.md | default | epic/example | Existing grouped decision unchanged. | remaining |

Parent completion: Review and prove all work/parent.md v1:R1–R4 on one exact assembled candidate, including independently landed contributions, capture/lookup/summary composition and inherited ASCII/plain-text/no-network/no-persistence constraints. Final parent PR needs matching full parent review and proof; CI and repository approvals are separate readiness gates. No merge authority.
Pending actions: Implementation must extract only the lookup contribution from child/lookup against trunk, preserving unfinished-sibling.txt on the existing integration candidate. Proposed later PR effect: gh pr edit 17 --base trunk only after a clean scoped candidate, refreshed reports, and explicit effect authority. Retargeting now is blocked by sibling payload; no automatic head rewrite or force push. No branch setup required; preserve epic/example and all existing refs.

## Strategy preview observations
Outcome: DRAFT. Agent context: /root/scenario_strategy_recovery. Run label: S8-default.
Parent v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada; source specs/registry.md sha256:64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9. Exact contract and source bytes retrievable from git:bc225942a47f3474210c2410c50679fb5238bd2f; all work items unchanged.
Active approved v1 remains authoritative, sha256:f4e65699e8863a786220dd178bd46d85b44d551288dff85b9ee1cad9703eced4. Prior slicing.md bytes retained by save history. This proposed section does not activate v2 or stale the active plan.
Inspected candidate: bc225942a47f3474210c2410c50679fb5238bd2f; final target trunk local and remote: d4125733f93c976ce218833dc8c995b58f0cbdf4; integration local and remote: bc225942a47f3474210c2410c50679fb5238bd2f. Remote state inspected via local disposable origin, no network.
PR 17: OPEN child/lookup at bc225942a47f3474210c2410c50679fb5238bd2f, current base epic/example. Future base trunk. Title and body including human note remain unchanged.
Lookup changes epic/example -> trunk; capture and summary retain their grouped destinations. Full git diff trunk HEAD contains only unfinished-sibling.txt with UNFINISHED_SIBLING_DO_NOT_SHIP. Therefore the existing candidate is unsuitable for independent lookup publication despite passing capture and lookup checks. Capture already exists in trunk and actual candidate; no unmet behavior prerequisite. Extracting away the sibling currently yields the existing trunk product tree: do not manufacture an empty lookup PR. Implementation must reconcile whether any intended lookup contribution remains.
Verification refresh: Historical comparison base d4125733f93c976ce218833dc8c995b58f0cbdf4 is already trunk, while actual old integration target is bc225942a47f3474210c2410c50679fb5238bd2f. Reconcile the exact comparison base and do fresh full review for the independently scoped candidate; extraction changes product identity and therefore requires fresh full proof too. Existing implementation/publication observations are not REVIEWED/PROVEN reports. Never relabel historical proof as a pair for new content.

## Coverage and dependency handoff
| Slice | Child | Qualified contribution | Direct prerequisite | Completion check |
|---|---|---|---|---|
| S1 | work/capture.md | work/parent.md v1:R1; child R1 | None | python3 check.py capture |
| S2 | work/lookup.md | work/parent.md v1:R2; child R1 | Actual capture outcome, confirmed in candidate | python3 check.py lookup |
| S3 | work/summary.md | work/parent.md v1:R3; child R1 | None | python3 check.py summary |
| Parent | work/parent.md | work/parent.md v1:R4; all three contributions | One assembled candidate | python3 check.py parent |
All children retain ASCII/no-network/no-persistence constraints; missing lookup returns None, original case is retained, summary stays plain text. Existing check.py asserts literal contract outcomes through registry public functions. S1 -> S2 is the only blocker edge. Stable topological sequence S1, S2, S3 is not additional dependency. Parent owns composition verification. Child contracts and existing decomposition links remain intact; no new tickets, links, or acceptance revisions.
Unchanged children may continue under the active approved plan; changed routing awaits approval. No ref or PR effects performed, no product files changed.
Evidence: case-root command-evidence.txt includes exact commands and output. Saved and reread slicing.md and actor-report.md. Changes limited to slicing.md and retained history, plus case-root reports.

Next steps:
1. Approve the exact v2 proposal in .p2p/work/parent/slicing.md; this is strategy approval only. Concrete proposal is ready for evaluator approval phase.
2. After strategy activation, /implement-contract work/lookup.md must resolve sibling-free candidate scope and recapture identity. Do not retarget PR 17 before scope is repaired and exact effect authority exists.
3. Complete matching child review/proof and eventual full assembled parent review/proof; no merge authorized.
