# Host preflight after authorized CLI exception

Status: basic independent execution and filesystem boundary established.
Full controller-specific capability checks remain implementation obligations.

User approved separate sandboxed CLI sessions after the installed delivery skill's
host-tools preference was explained. Earlier BLOCKED preflights are historical.

Host: Codex CLI 0.157.1 on macOS, /opt/homebrew/bin/codex.
Base/start: 1a296f6ec7a064b32ce1be6a5d29f0c39df12294, main.
Contract: work/single-work-item-delivery.md v1, SHA-256
245208f2f343cc39f1e9dae892117ae910b2d12da4839c8594061f36b32768d1.

## Actual executions

1. Fresh CLI thread 01a0dd5d-c0b0-7e71-97c8-6f5c3fd6cc56, exit 0.
   --sandbox read-only -c approval_policy='"never"'.
   Sentinel overwrite command failed with operation not permitted, exit 1.
   Readback found original bytes. events.jsonl retains the actual shell output.
2. Fresh CLI thread 01a0dd5f-7461-7b92-8ec2-889d1a77f192, exit 0.
   --sandbox workspace-write -c approval_policy='"never"'
   -c sandbox_workspace_write.exclude_slash_tmp=true
   -c sandbox_workspace_write.exclude_tmpdir_env_var=true
   -c sandbox_workspace_write.network_access=false
   -C /private/tmp/p2p-issue-28-verifier-scratch --skip-git-repo-check.
   Scratch write/read succeeded. Candidate sentinel outside scratch was readable
   and write-denied, exit 1, with original bytes confirmed. A heredoc using the
   default temporary directory was denied; use TMPDIR inside scratch for checks.

Records retained and reread in host/cli-probe/. Each contains host thread.started
and turn.completed events with usage, actual commands, and command outcomes.
Controller-specific configuration/tool/network probes remain to be established
by implementation before relying on them; these probes do not establish
arbitrary same-user host tamper resistance or monetary limits.

## Next steps

1. Complete implement-contract in /root/implement_issue_28, then capture one
   fixed candidate for independent full review and proof using the verified boundary.
