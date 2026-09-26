# Parent repair actor report

Actor: /root/scenario_parent_repaired. Actual installed skills invoked: prove (three children and full parent), review-implementation (full parent), publish-pr (draft-only admission), merge-readiness (read-only PR18). No delegation. No repair executed.

Candidate: 2a7733c6ac449ab6203d856f090c2e67173daace; parent base 928231303f30c9c01d93754ce5653e9b27b42399; child metadata recovered/captured against current approved integration tip 2a7733c6ac449ab6203d856f090c2e67173daace. Lookup prior candidate metadata retained in helper history. No product/ref/contract/tracker edits.

Actual outcomes: capture PROVEN 1/1; lookup PROVEN 1/1; summary PROVEN 1/1; parent review CHANGES NEEDED; parent proof NOT PROVEN 3/4, R4 disproven; parent publication BLOCKED; PR18 readiness BLOCKED despite current successful required-ci rollup and APPROVED repository decision.

Root cause observed: registry.py:13 calls capture(name.upper()). greet('Ada') actually returns Welcome ADA. The independent literal oracle requires Welcome Ada. Full parent check fails; direct primitive composition and all child checks pass. Exact commands, exit statuses and output are retained in parent-repair-command-evidence.jsonl and behavior evidence, including initial helper validate invocations missing --base and successful corrected validations. No outcome inferred from fixture name.

Plan extraction: exact repaired-protocol regex; revision v1; sha256:787c4a50a0828bba064b7ca5b817f17ac3657cd88b51e3a4df9c838f75cc02db. Both publication/readiness retained section files are read back and compared byte-for-byte and by digest, including trailing separator. Approval receipt remains retrievable. Package hashes: .p2p/work/parent/evidence/installed-package-hashes.json.

Durable reports saved and reread via installed filesystem helpers with history: .p2p/work/{capture,lookup,summary}/proof.md and .p2p/work/parent/{review,proof,publication,merge-readiness}.md. Commands use only supplied fixture gh, EPIC_TRACKER_ROOT and bin PATH; origin is local bare repo. No oracle/tracker/builder/main-project reads.

Next steps:
1. Repair parent R4 only when authorized, then capture fresh candidate and refresh full parent review and proof.
2. Reconsider publication/readiness only with matching successful reports and current gates.
