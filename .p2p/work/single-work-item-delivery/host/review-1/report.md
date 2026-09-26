# BLOCKED: issue #28 — single-work-item delivery

**Contract:** [`work/single-work-item-delivery.md`](/Users/grove/projects/promise-to-proof/work/single-work-item-delivery.md), v1, SHA-256 `e447f13a94dae84b9af2dfc06cfb6be36900eee2c0e381a3942015245b48826d`.

**Parent context:** None.

**Candidate:** `snapshot:sha256:847704b1ef38871fc2e62529426105cc31ae029a79c11e8190c00fcb3b519259`. Recoverable 118-entry manifest: [`candidate.json`](/Users/Shared/p2p-issue-28-fixed-8lm678wl/candidate/.p2p/work/single-work-item-delivery/candidate.json), SHA-256 `f3da09c0f3b4ae6088940a1c4d7931eea003ba36725e2e7bbcb57e4160f340d2`.

**Comparison:** Full base commit `1a296f6ec7a064b32ce1be6a5d29f0c39df12294`; retained base manifest SHA-256 `dff8d6d1461adbb82502b96c021f79ce35b8a46acd9c1ae3c7d7f186d4feb736`. Scope is the complete candidate snapshot, with `.p2p/` excluded. Relative to the base, it contains two modified tracked files and five added files.

**Stability:** Candidate validation reproduced the supplied snapshot key at both identity checks. The canonical contract hash and comparison base also matched. No candidate or contract drift was observed during review.

**Coverage:** Inspected all R1–R14 against the controller, filesystem helper, host-check script, docs, tests, pinned source handoff, and imported issue text. R10 remains unresolved as described in F1. No nested agents or live Codex CLI checks were used.

## Contract fidelity

Reviewed R1–R9 and R11–R14 across host preflight, candidate capture and report gates, restart and repair handling, source preservation, resource admission, and result reporting. No additional material finding.

**F1 — Decision-blocking unknown, R10.** The agreement requires isolating Codex configuration and enforcing stage-tool permissions before dispatch. In [`p2p_delivery.py`](/Users/Shared/p2p-issue-28-fixed-8lm678wl/candidate/skills/productivity/deliver-issue/scripts/p2p_delivery.py:93), the command ignores user config and rules and sets CLI overrides for selected controls, but does not establish whether a trusted project-local `.codex/config.toml` can affect effective permissions or tools. The preflight at line 333 probes selected protected paths and network access, but does not test a repository containing project-local Codex configuration.

The trigger is a delivery repository with trusted project config that adds writable roots or another tool route. The retained `config-probe` records used temporary directories, not a repository with `.codex/config.toml`; the fixture tests also contain no project-config case. Those observations do not establish whether the installed CLI ignores, overrides, or applies such configuration. Without that fact, I cannot conclude that R10’s permission boundary holds for repositories this controller accepts. The smallest useful check is an authorized real-host run using the candidate’s exact CLI arguments and trust conditions against a disposable project with a config requesting an out-of-scratch writable root and an extra tool route. Retain effective permission/tool observations and verify that the controller fails closed before dependent work if those permissions survive.

## Scope and simplicity

No material findings. The implementation remains within the one-host, one-work-item Phase 2 scope. The later strategy, scheduling, and model-conformance phases remain excluded.

## Engineering quality

F1 is the only review finding. No other material issue was established from the inspected code and retained evidence.

## Checks and limitations

- Candidate append-open on the designated sentinel raised `PermissionError`; a write in review scratch succeeded. The candidate sentinel remained absent.
- Read-only helper validation succeeded: 118 manifest entries; snapshot key, contract hash, and comparison base matched the supplied identities.
- Inspected the retained fixture log: 19 tests passed. This is recorded evidence, not a test run by this reviewer.
- The final live-delivery directory had an invocation record, but its `stdout.json` and `stderr.txt` were both empty (0 bytes), and no summary was present. I observed no final live-run result and make no claim of success.
- I did not run the live nested Codex check, as instructed for this network-restricted review environment.

## Handoff

F1 concerns R10. The review is blocked on the project-local configuration behavior described above. If the real-host probe shows permissions survive, correct the controller and recapture the candidate before a fresh full review and proof.

**Report storage:** Pending. This read-only review returns the exact report for the enclosing workflow to save and reread.

Review only; acceptance proof and merge readiness are separate.

## Next steps

1. Run the authorized macOS project-config isolation probe described in F1 with the candidate’s exact CLI arguments and trust conditions. Retain its effective configuration and host events. Expected result: extra permissions are either demonstrably ignored or denied, or the controller blocks before dependent stages. Then rerun the full review against the unchanged candidate if the boundary is established.