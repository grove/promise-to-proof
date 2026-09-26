# Delivery status: BLOCKED

Issue: https://github.com/grove/promise-to-proof/issues/30
Work item: work/delivery-model-conformance.md
Agreement: imported planning input only; no contract revision, planner invocation, or approved acceptance matrix yet.
Imported work-item SHA-256: 9f05a105e038ceb3abe4c217cf2c8b95dc6e0158095eec99bcc60fb0a120cc5c
Repository: /Users/grove/projects/promise-to-proof
Starting branch: main
Starting commit: b217049db5de5df2cc5b138f5ce1cc64b68575fd
Starting tracked and untracked changes: none, from git status --short.
Candidate: not captured. No implementation stage ran.
Comparison base: not yet selected; starting commit recorded above is not a review verdict.
Review and proof: not invoked; no reports or acceptance claims.

## Blocker

The native host supports separate agent contexts but exposes no read-only launch setting. The actual probe /root/host_probe inherited repository write access. Prompting it to avoid writes does not satisfy the installed deliver-issue skill's requirement that the workspace sandbox protect verification inputs. No enforced read-only stage has been demonstrated.

The installed skill at /Users/grove/.agents/skills/deliver-issue/SKILL.md says: "When the enclosing host exposes separate agent contexts, launch stages directly through those host tools and retain their distinct invocation IDs; do not start a nested CLI process just to obtain isolation."

An explicit exception permitting fresh sandboxed Codex CLI stage contexts has been requested from the user and is pending. The executable /opt/homebrew/bin/codex exists; existence alone is not an isolation check. No nested process was launched. This is a capability/skill-rule blocker, not an automatic approval rejection.

## Retained observations

- host/probe.json records the actual collaboration.spawn_agent invocation identity, completion, inherited permissions, and successful read.
- evidence/issue-import.json retains the issue body, empty comments list, labels, and update identity. SHA-256: 049107b6d5334fdf7187e80473334c13229ed10c1195129758df68105896c430.
- evidence/pinned-optimization-handoff.md retains the exact source from git show 5c2c6b64b997dd2c04ac8ba85dcad8e08047eac2:plans/promise_to_proof_optimization_handoff.md. Its SHA-256 matched the issue's expected 7162a965fa53322a8805582756ea6137a847d72798e057dd751cc2e46c98f65a.
- The filesystem helper created and reread the imported work item, saved and reread both source records, and verified exact bytes and hashes. Durable storage works.
- Initial sandboxed GitHub read failed for network access; an approved escalated read succeeded. No tracker writes occurred.

Only imported planning input and local workflow records were added. No product implementation, test run, commit, push, or publication occurred. Planning has not selected an adapter language or treated prior model/controller evidence as current Phase 3 proof.

Next steps:

1. Resolve the verification-host restriction by explicitly allowing fresh sandboxed Codex CLI stages or supplying a host launch tool with enforced read-only verification. Resume delivery from work/delivery-model-conformance.md. The workflow must demonstrate actual isolation before dependent implementation, then invoke plan-acceptance for the full Phase 3 agreement.
