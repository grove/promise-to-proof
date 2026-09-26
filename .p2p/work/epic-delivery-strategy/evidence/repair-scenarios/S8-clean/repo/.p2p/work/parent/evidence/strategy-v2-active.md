## Approved delivery plan
Plan revision: v2
Approval source: Evaluator explicitly approved exact proposed v2 sha256:166d7d93ecb4bd3b8f3a3b1306119fa176c68dce65cff9c558f3e8d71a385945; exact grant retained at evidence/strategy-v2-approval.md, approved proposal bytes at evidence/strategy-v2-approved-proposal.md. Authority: local plan-record activation only; no ref, PR, tracker, publication, merge, or candidate-extraction effects.
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

