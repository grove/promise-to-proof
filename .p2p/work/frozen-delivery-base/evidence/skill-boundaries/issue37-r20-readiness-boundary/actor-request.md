# Actor request

Apply the exact merge-readiness instructions in `actor-resources/merge-readiness-SKILL.md` with the protocol in `actor-resources/acceptance-contract-protocol.md` and the controlled fixture at `repo/`. The scenario definitions are in `actor-resources/merge-readiness-scenarios.md`.

Assess the open PR identified in `controlled-input.json` as a read-only request. Use only the saved contract, candidate, matching review and proof reports, local fixture refs, and the controlled repository observations. Do not call GitHub, the network, or any tracker. Do not update a PR body. Verify report identities and candidate/head/base from the fixture. Save the assessment as `repo/.p2p/work/delivery-review-report-contract/merge-readiness.md`, then return the exact saved Markdown report and the proposed readiness paragraph. Do not assume or state that the fixture is a live PR.
