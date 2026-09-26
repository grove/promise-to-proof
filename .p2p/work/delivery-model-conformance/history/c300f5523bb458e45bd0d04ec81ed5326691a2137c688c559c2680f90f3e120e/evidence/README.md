# Development evidence

- `compatibility/`: R1's pre-language-choice experiment, original tool checksums, actual status callback, caught mismatch, and portable seed-42 replay. Copied unchanged from the enclosing workflow's retained checkpoint.
- `model-checks/`: the unchanged Phase 1 model's 43 checks. This is model evidence only.
- `controller-conformance/`: 17 complete stateful baseline traces and five caught production guard mutations. Each trace retains the FizzBee model, model and MBT logs, observation, actual fixture repository, controller output, saved state, and records. Worker replies and session IDs are substitutes.
- `controller-replay/`: a second seed-42 execution of the stale-report-guard mutant. `development/replay-comparison.json` establishes identical enabled action order and observed projections.
- `development/`: original 19 controller tests, model-run command output, generator pin verification, candidate capture output, and replay comparison.
- `invalidated-development/`: preserved debugging runs. These do not establish conformance, even when a historical driver printed success. Read its README for the specific reasons.
- `live-host/`: reserved for the enclosing workflow's actual host check against the fixed reconstructed candidate. It is absent until that check is retained and inspected.

`summary.json` in each successful controller directory records case, seed, mutation, tool configuration, command, action counts, and graph measurements. `fixture/actions.jsonl` records actual enabled operations with public results and before/after saved state. `server.log` retains every FizzBee driver proposal, including DISABLED no-ops and model comparisons. Model graph binaries are omitted because each retained model regenerates them. Generated TypeScript and lockfiles are retained under `runtime/`, without a machine-local node_modules link. Mutation directories retain the actual edited controller and reproducible edit.

Paths inside raw invocation and controller records identify the original run. Replay creates a fresh fixture and needs no old installation or temporary fixture path. Set FIZZBEE and FIZZBEE_MBT to verified local releases and use the replay command in each observation. The runner installs pinned npm dependencies in the new output directory, or accepts --node-modules for an existing matching installation.

The normalized projection is `exit|saved-status|attempts|completed-attempts|report-names|repair-used|candidate-generation|review-generation|proof-generation|current-candidate`. Generation zero means absent. A verifier generation of -1 means its saved report is not a full passing report against the exact current candidate. UUIDs, timestamps, disposable Git base IDs, and scratch paths are deliberately absent from this projection but remain in raw records.
