# Host invocations and isolation evidence

Host: Codex CLI 0.157.1 on macOS Darwin 25.6.0 arm64; Python 3.14.7. Each successful stage used a fresh `codex exec` session. Raw JSONL output and prompts are retained under `evidence/host/`. Stage commands were launched from the enclosing session with the environment approval path; none was rejected.

## Capability probe

- Read-only separate-context probe: `codex exec --sandbox read-only --json -C /private/tmp/p2p-delivery-review-report-contract-candidate 'Print exactly P2P_STAGE_PROBE_OK. Do not inspect or modify repository files.'`
- Session `01a0df77-eded-7073-b59b-e772a5a8ffb7`, exit 0; output contained `P2P_STAGE_PROBE_OK` and `turn.completed`.
- An earlier unapproved nested attempt failed to initialize with `Operation not permitted`; the same harmless probe succeeded through the environment approval path.

## Initial read-only stage attempts

- Review session `01a0df7a-e6e3-7203-b4ab-c27ca5335184`; proof session `01a0df7b-b3c5-7362-b6bf-a2696755b022`.
- Both used `codex exec --sandbox read-only --json -C /private/tmp/p2p-delivery-review-report-contract-candidate -` with the corresponding saved prompt. Test setup could not create temporary directories in read-only mode (`No usable temporary directory found`). Both sessions were interrupted with exit 130 before returning reports. Their partial output is preserved as `review-readonly-attempt.jsonl` and `proof-readonly-attempt.jsonl`; these are not the accepted reports.

## Scratch write-boundary checks

- Initial boundary probes used `--sandbox workspace-write` with separate scratch directories under `/private/tmp` while the candidate was also under `/private/tmp`. Sessions `01a0df80-8f24-7ec3-87d3-d6f6046aa62a` and `01a0df80-97b6-75b0-a591-11b2f3a32906` returned `BOUNDARY_FAIL`: the sandbox treats the temporary directory as writable. Each probe removed its own test file; the candidate was revalidated afterward. Logs are preserved as `review-boundary-temp.jsonl` and `proof-boundary-temp.jsonl`.
- The candidate was reconstructed from the full comparison-base tree plus the two committed product changes and approved contract in a second isolated clone; its capture produced the same snapshot key. It was then cloned to `/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate`, outside the scratch workspaces. New probes in fresh sessions `01a0df82-ab3a-7fc2-8764-bfcdf8b0f5e0` and `01a0df82-c8fe-7ed3-90c1-76a6654032fd` could write/read/delete in their own scratch directories and received `PermissionError` writing the candidate. Both returned `BOUNDARY_OK`; candidate validation passed. Logs are `review-boundary-protected.jsonl` and `proof-boundary-protected.jsonl`.

## Final independent stages

- Review: `codex exec --sandbox workspace-write --skip-git-repo-check --json -C /private/tmp/p2p-delivery-review-report-contract-review-scratch -` with `review.prompt.md`, teeing to `review-final.jsonl`. Session `01a0df85-57f5-7663-ad39-c93fae750eb6`, exit 0; returned `CHANGES NEEDED`.
- Proof: `codex exec --sandbox workspace-write --skip-git-repo-check --json -C /private/tmp/p2p-delivery-review-report-contract-proof-scratch -` with `proof.prompt.md`, teeing to `proof-final.jsonl`. Session `01a0df85-542c-78d1-bcdc-f68895a28a9b`, exit 0; returned `NOT PROVEN`.
- For both stages, the Codex workspace and `TMPDIR` were the separate scratch directories. The candidate was outside them and its write-denial boundary had been tested in separate contexts. `PYTHONDONTWRITEBYTECODE=1` avoided candidate bytecode writes.
- Both independent controller-suite runs passed all 21 tests. Review ran 21 tests twice (`111.545s` and `107.961s`); proof ran 21 tests once (`141.476s`). Both also ran fixture-backed sensitivity probes described in the reports. No live Codex stage behavior is claimed.

## Exact result references

- Contract: `work/delivery-review-report-contract.md`, v1; SHA-256 `4f892ad68cfb47492c3e9066ae64c614bef3dda5a950a439b161dde04cc5fc63`.
- Candidate: `snapshot:sha256:e5d92bc5f1600e0f6d66ac585d4959b1c75c384c7969b498c9f266a95994d14b`; comparison base `a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412`.
- Final reports: `review.md` and `proof.md`. Full launch/completion JSONL is retained in the evidence directory; each file is linked to its session above.
