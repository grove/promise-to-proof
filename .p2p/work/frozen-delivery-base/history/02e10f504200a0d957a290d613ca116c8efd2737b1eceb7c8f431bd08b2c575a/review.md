# CHANGES NEEDED: Issue #37 — frozen delivery bases under moving targets

Contract: `work/frozen-delivery-base.md` v2, SHA-256 `3925c513a6702b94fbc2fcfc30f7d2d057638a275ae103056031cb3ca38aa0a9`. The bound file labels v2 an unapproved proposal; this review evaluates the implementation against these exact bytes and does not establish contract approval.
Binding source: `plans/frozen-delivery-under-moving-targets.md`, SHA-256 `c570232a7371a53fd6dad954ec9d53f7940ecba171b3a2080fd995a6bd9a77d2`.
Candidate: `snapshot:sha256:0cafb1cbafac730a2fa2df2939039a970a808827a72181e9573b9e01584566e3`; recoverable from `.p2p/work/frozen-delivery-base/candidate.json` (141 manifest entries).
Comparison: `dbe54bc20a19b8ab8e700fb3aba9c9e8a59ce4d4` (B). Compared the full candidate manifest, excluding `.p2p/`, with B: candidate has 141 entries versus B's 140 and differs at 19 paths (18 modified tracked paths plus the new work contract).
Stability: Candidate and agreement identities revalidated after review checks; comparison base remains B. No product or contract files were changed during this review.
Coverage: Full requirements R1–R21 reviewed. Controller, lifecycle tests, routing and stage instructions, protocol/controller docs, scenario guidance, and bounded model/checker were inspected. Compact map: R1 admission/routing; R2–R4 frozen identity, movement and integrity; R5–R6 review/proof bindings; R7–R11 resume, observations and retained-base recovery; R12 direct-review scope; R13–R15 legacy recovery, CLI and verdict compatibility; R16–R18 model state, witness and mutations; R19–R20 publication/readiness boundaries; R21 cross-stage instructions and scenarios. No acceptance proof was run.

## Contract fidelity

- **F1 (R1; admission destination identity):** `skills/productivity/deliver-issue/scripts/p2p_delivery.py:115–127` returns fully qualified `refs/heads/...` and `refs/remotes/...` inputs without `git check-ref-format`. `routing()` then passes the value to `fs.full_commit()` at line 217, which resolves Git revision expressions. For an unsliced run, `run()` compares the supplied full SHA to that resolved value at lines 1082–1086. A revision expression can therefore masquerade as the named destination's current tip and admit work from a stale base.

  Exact read-only reproducer from the current candidate/repository: `explicit_destination(root, "refs/heads/main~1")` returned `("main~1", "refs/heads/main~1")`; `git check-ref-format refs/heads/main~1` exited 1; `fs.full_commit(root, "refs/heads/main~1")` resolved to `833815c9030136662f7caed0a004e783bc953f7c`, while `refs/heads/main` was `39cf3a96aaf89789fceed9b0454682f9e88bc0b8`. Supplying the expression with comparison base `833815c9030136662f7caed0a004e783bc953f7c` makes the current base-equality guard compare against the ancestor rather than the named branch tip.

  Smallest effective correction: run `git check-ref-format` on every accepted fully qualified local or remote-tracking ref before resolution, and add controller cases rejecting `refs/heads/main~1` and `refs/remotes/origin/main~1` before dispatch. This is a demonstrated R1 admission defect and requires candidate repair.

The previous review's F1 (preserve execution limits and process cleanup) is resolved in this candidate. `launch()` sends TERM, waits, and then KILLs the process group; `test_real_transport_timeout_and_heartbeat` uses a SIGTERM-ignoring child and asserts the child does not survive. The frozen-base movement behavior also remains: the lifecycle test moves the target during implementation, review and proof and asserts that candidate, review, proof and reports retain admission base A; repeated movement, unavailable/non-fast-forward observations, fresh-process resume, and no redispatch after completed reports have targeted controller coverage.

## Scope and simplicity

No material scope finding. The changes remain within the contract's frozen-base behavior; publication and merge-readiness instructions retain checks against the current target and exact reviewed candidate. No automatic integration behavior or added verdict was found.

## Engineering quality

The fully qualified ref bypass is also a Git revision-injection/data-integrity defect at the admission boundary (F1 above). The earlier timeout/process-group regression is covered by a real subprocess test and appears fixed. No other material engineering finding was established in the inspected candidate.

## Checks and limitations

- Validated the candidate record against B with `p2p_filesystem.py validate`; requested candidate key, base, work-item hash and binding-source hash matched. Manually compared the complete manifest with B outside `.p2p/`.
- Ran `python3 -m unittest checks.test_p2p_delivery.DeliveryTests.test_real_transport_timeout_and_heartbeat checks.test_p2p_delivery.DeliveryTests.test_movement_during_implementation_review_and_proof_keeps_all_bindings_fixed`: 2 tests passed in 11.625 seconds. The environment emitted a non-fatal PATH-alias permission warning.
- Inspected controller routing/admission and lifecycle tests, including stale-base blocking, destination movement/recovery, retained-base validation, and actual timeout process cleanup. Inspected review/proof/delivery instructions, protocol/controller documentation, publication/readiness and stage scenarios, and the model plus trace checker.
- The implementation report records a 56-test controller-suite pass, but I did not rerun that suite. I inspected the Fizz model and its assertions/mutations but did not execute the model runner. Direct skill scenarios were inspected, not invoked. This is a review, not `/prove`; proof remains separate as requested.
- The contract remains explicitly unapproved in its own text. This report does not resolve that status. No external tracker or PR state was checked.

## Handoff

F1 requires an in-scope R1 correction through `/implement-contract`; after repair, capture the changed candidate against the intended base and refresh both full review and proof. Keep this C2 finding bound to candidate `snapshot:sha256:0cafb1cbafac730a2fa2df2939039a970a808827a72181e9573b9e01584566e3` and B `dbe54bc20a19b8ab8e700fb3aba9c9e8a59ce4d4`.
Report storage: `.p2p/work/frozen-delivery-base/review.md`. Replaced prior uncommitted report bytes were retained at `.p2p/work/frozen-delivery-base/history/e07488d7c0827da68bb4d68187c83af92586832e9107b2eb792e74aba4dbf54e/review.md`, SHA-256 `e07488d7c0827da68bb4d68187c83af92586832e9107b2eb792e74aba4dbf54e`.

Review only; acceptance proof and merge readiness are separate.

## Next steps

1. `/implement-contract work/frozen-delivery-base.md; findings .p2p/work/frozen-delivery-base/review.md` — reject revision expressions in fully qualified destination refs and add pre-dispatch controller coverage.
2. After that repair, capture the changed candidate against the intended comparison base, then run a fresh full `/review-implementation` and `/prove` bound to that candidate. Leave proof to its separate context.
