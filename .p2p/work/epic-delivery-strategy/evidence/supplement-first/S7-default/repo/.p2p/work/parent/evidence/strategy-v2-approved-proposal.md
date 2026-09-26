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

