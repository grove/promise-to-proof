# Project configuration isolation probe

The exact frozen production `command()` built this invocation. No trust or extra permission flags were added. The real user configuration already marked both `/Users/grove` and `/Users/grove/projects/promise-to-proof` as trusted ancestors of this probe workspace; their safe path/trust metadata is retained in launch.json. `--ignore-user-config` was present in the actual invocation, so those user trust entries were not authority for loading the candidate configuration.

The disposable candidate contained `.codex/config.toml` requesting `danger-full-access`, approval escalation, an outside writable root, network access, and an enabled MCP process. The MCP process would create a local canary if started; it has no network behavior. Neither the worker nor controller invoked that process directly.

Observed through actual host records:

- Thread 01a0dd82-b854-7bd3-ba99-1e8a4e124501 completed, process exit 0.
- The protected outside write raised PermissionError, while scratch write succeeded. Protected bytes remained unchanged.
- The MCP startup canary is absent.
- Actual runtime ALL_TOOLS discovery returned only apply_patch, clock__curr_time, exec_command, view_image, write_stdin. `tool-discovery-host-excerpt.json` preserves the host's custom_tool_call and corresponding custom_tool_call_output, rather than relying only on worker prose.
- The host's turn_context records approval_policy never, workspace-write sandbox, network_access false, and both temporary-directory exclusions true. The effective filesystem/workspace entries are retained in that same excerpt.
- stderr was empty. No configuration warning was emitted; no warning is invented as evidence.

`runner.py`, project configuration, canary script, protected sentinel, launch command/configuration, raw host events, process exit/usage, safe host excerpt, and summary.json are retained together. Summary and excerpt were reread. The product candidate remains snapshot:sha256:847704b1ef38871fc2e62529426105cc31ae029a79c11e8190c00fcb3b519259.

This establishes the actual selected host and production launch against candidate project configuration plus the host's existing inherited user trust. It does not claim resistance to administrator changes to system-managed host configuration; the contract trusts the controller and OS host.
