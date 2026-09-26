# REVIEWED: issue #28, single-work-item delivery

Contract: `work/single-work-item-delivery.md` v1; SHA-256 `e447f13a94dae84b9af2dfc06cfb6be36900eee2c0e381a3942015245b48826d`  
Parent context: None. Binding sources are recorded in `candidate.json`.  
Candidate: `snapshot:sha256:847704b1ef38871fc2e62529426105cc31ae029a79c11e8190c00fcb3b519259`; recoverable manifest at `candidate/.p2p/work/single-work-item-delivery/candidate.json`.  
Comparison: Full base commit `1a296f6ec7a064b32ce1be6a5d29f0c39df12294`; review scope is the complete product snapshot, excluding `.p2p/` as specified by the protocol.  
Stability: Candidate, contract, binding inputs, and comparison base matched their captured identities at final recheck.  
Coverage: Full R1–R14 review. Examined the controller, filesystem helper changes, host-check entry point, added tests and documentation, contract, binding sources, and retained live evidence.

## Contract fidelity

No material findings.

Coverage map:

- **R1–R2:** `p2p_delivery.py` host command/configuration and `preflight()` establish separate host sessions, protected writes, scratch writes, and network denial. The live project-config probe supplies additional evidence for hostile project configuration.
- **R3:** `stage()`, `run()`, and `complete()` require implementation, review, proof, matching identities, and complete requirement coverage. Retained live-delivery records contain separate host receipts for the stages.
- **R4:** `p2p_filesystem.py` snapshot/binding logic and `source_stable()`, `capture()`, and `current()` check contract, binding, candidate, and base identity.
- **R5–R6:** `stage()`, `read_report()`, `complete()`, and the repair path retain reports, verify readback, and reject incomplete or stale results.
- **R7–R8:** `reserve()`, `receipt()`, `dispatch()`, and `run()` persist reservations, reconcile uncertain launches, and consume the single repair allowance before dispatch.
- **R9–R10:** `create()` captures dirty-scope decisions and isolates the workspace; authority admission and `host_config()` restrict stages to local effects.
- **R11–R13:** Attempt receipts and result reporting preserve timestamps, outcomes, elapsed time, usage or `unknown`, and unsupported hard monetary limits.
- **R14:** `complete()`, `result()`, and the CLI error path require matching full reports for success and return a blocker for incomplete runs.

## Scope and simplicity

No material findings. The added controller, host probe, tests, and documentation address the single-host Phase 2 contract. The filesystem helper change makes durable report replacement atomic. I found no material expansion into publication, multi-host support, or optional verification profiles.

## Engineering quality

No material findings.

The earlier F1 concern is resolved. The retained project-config probe used the production command with `--ignore-user-config`, `--ignore-rules`, `--strict-config`, and `--sandbox workspace-write`, without extra trust flags. Its disposable `.codex/config.toml` requested `danger-full-access`, approval escalation, network access, an outside writable root, and an enabled MCP server. The actual host record shows the probe session `01a0dd82-b854-7bd3-ba99-1e8a4e124501` exited 0; an outside write was denied, scratch writing succeeded, the protected sentinel remained unchanged, and the MCP canary was absent. The recorded runtime tools were `apply_patch`, `clock__curr_time`, `exec_command`, `view_image`, and `write_stdin`. The host excerpt records `approval_policy: never`, `workspace-write`, network disabled, and temporary-directory exclusions enabled. It also records inherited user trust paths; those do not override the observed sandbox result. The raw event hash matches the probe receipt.

## Checks and limitations

The required append-open attempt on the disposable candidate sentinel raised `PermissionError` before writing.

I independently recomputed the snapshot digest from the retained manifest and compared the live `p2p_filesystem.snapshot()` to that manifest. The digest matched the recorded key; all 118 entries matched their bytes, modes, and symlink targets. The contract hash, all three binding-source hashes, and the full comparison-base commit also matched `candidate.json`. The final live snapshot still equaled the retained manifest.

For live-delivery evidence, I inspected the retained invocation, `stdout.json`, `delivery.json`, attempt exit receipts, raw host-event files, and proof report. The tiny delivery record has five finished, exit-zero attempts: two distinct preflight sessions, then distinct implementation, review, and proof sessions. Its review and proof bind to the tiny candidate and base; its final status is `REVIEWED_AND_PROVEN`. The retained independent greet output is exactly `b'hello\n'`, with empty stderr.

The live summary’s auxiliary `product_entries_sha256` map does not match the frozen candidate tree, so I did not use that map as candidate identity evidence. The summary’s product key matches the frozen snapshot, and the controller and filesystem-helper bytes used by the run match the frozen candidate. The proof report records the actual 23-test suite command and result; I did not rerun that suite as part of this review.

No tests or mutating diagnostics were run in this review. The product snapshot excludes `.p2p/`; the candidate clone reports `.p2p/` artifact removals and the disposable sentinel separately from the reviewed product identity. No candidate, contract, or report files were changed.

## Handoff

No finding requires a code or contract change. F1 is resolved by the actual hostile project-config probe and its host receipts. This review is not an acceptance verdict or merge approval.

Report storage: Pending. Proposed destination: `.p2p/work/single-work-item-delivery/review.md`; the enclosing workflow must save and reread this report.

## Next steps

1. Save and reread this exact report at the proposed destination. The existing full proof at `/Users/grove/projects/promise-to-proof/.p2p/work/single-work-item-delivery/proof.md` matches this contract and candidate; once this report is saved, the matching full review and proof provide complete acceptance evidence for this candidate.
2. No PR exists. No further action is required unless publication is later wanted.