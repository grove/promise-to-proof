# DRAFT strategy preview

## Proposed delivery plan
Plan revision: v2
Approval source: Pending exact proposal approval; request.md authorizes this preview only.
Parent: work/parent.md
Final destination: trunk
Integration branch: epic/example
Integration start: bffb5b8ebba1e5bc10aa2767f70e020365e4c577
Default choice: grouped

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
| work/capture.md | independent | trunk | Already landed; retained historical destination, commit bffb5b8ebba1e5bc10aa2767f70e020365e4c577. | landed |
| work/lookup.md | default | epic/example | User wants lookup and summary to ship together. | remaining |
| work/summary.md | default | epic/example | User wants summary and lookup to ship together. | remaining |

Parent completion: Review and prove all work/parent.md v1:R1–R4 on one exact assembled candidate, including independently landed contributions, capture/lookup/summary composition and inherited ASCII/plain-text/no-network/no-persistence constraints. Final parent PR needs matching full parent review and proof; CI and repository approvals are separate readiness gates. No merge authority.
Pending actions: Reuse existing local and remote epic/example at bffb5b8ebba1e5bc10aa2767f70e020365e4c577 after rechecking its unchanged origin; no branch creation is required. Proposed PR effect: gh pr edit 17 --base epic/example, changing only base from trunk. Preserve head child/lookup, title, body and human note exactly. No branch or PR effect is authorized.

## Strategy preview observations
Outcome: DRAFT. Agent context: /root/scenario_strategy_recovery. Run label: S7-default.
Parent v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada; source specs/registry.md sha256:64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9. Exact contract and source bytes retrievable from git:bffb5b8ebba1e5bc10aa2767f70e020365e4c577; all work items unchanged.
Active approved v1 remains authoritative, sha256:fb431ad4877524bdfbd034978abfc78e891d292d3e1247ebd68f9a3d2133b59e. Prior slicing.md bytes retained by save history. This proposed section does not activate v2 or stale the active plan.
Inspected candidate: bffb5b8ebba1e5bc10aa2767f70e020365e4c577; final target trunk local and remote: bffb5b8ebba1e5bc10aa2767f70e020365e4c577; integration local and remote: bffb5b8ebba1e5bc10aa2767f70e020365e4c577. Remote state inspected via local disposable origin, no network.
PR 17: OPEN child/lookup at bffb5b8ebba1e5bc10aa2767f70e020365e4c577, current base trunk. Future base epic/example. Title and body including human note remain unchanged.
Capture remains landed at trunk bffb5b8ebba1e5bc10aa2767f70e020365e4c577 based on user statement, active plan and actual code inspected. Issue 101 being CLOSED is not the evidence of behavior. python3 -B check.py capture passed; trunk and epic/example have identical capture implementation. Existing integration ref equals its approved origin; no subsequent changes. human-notes.txt sha256:406db673b27baa14dd56db5770cc5e7752ee45d796f213f64b42ce85c13641a6 retained exactly. Lookup and summary change trunk -> epic/example; capture stays trunk. Current tracked diff is empty, so no new implementation payload or useful PR delta should be invented.
Verification refresh: Routing/publication previews must be regenerated against v2 if approved. Both target tips currently equal bffb5b8ebba1e5bc10aa2767f70e020365e4c577, so destination-name change alone does not demand new content proof or a different-base review. There are no full REVIEWED/PROVEN reports; obtain full lookup review/proof before publication. If the target advances, fresh full review is required.

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
2. After strategy activation, recheck refs and PR 17 and obtain explicit authority for only the listed base retarget. Refresh full lookup reports before publication; preserve local notes.
3. Complete matching child review/proof and eventual full assembled parent review/proof; no merge authorized.
