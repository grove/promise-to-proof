# Recover the issue 33 verification handoff

The canonical agreement is `work/epic-delivery-strategy.md`. The current snapshot and full comparison base are embedded in `candidate.json` and `evidence/comparison-base-manifest.json` in this directory. Current review and proof bind that snapshot, not a later records-bearing Git commit.

Read `review.md`, `proof.md`, and `planning-handoff.md` first. The original execution paths in those records identify historical locations. Their files are retained here: every scenario `retention.json` maps original paths to repository-relative saved paths and SHA-256 values. Use those saved paths in a fresh checkout. Current and historical reports retain their original bytes and verdicts.

For a temporary candidate or comparison tree, use the corresponding manifest with the shipped `p2p_delivery.py` materialize function, or decode each file's `content_base64`, preserve its mode, and create literal symlinks from their recorded targets. Verify all paths, bytes, modes and targets and the manifest's canonical JSON SHA-256 before using the tree. Never restore over newer local work.

Scenario Git bundles are full disposable fixture histories. Read their retained request, tracker state, calls and actor reports before reconstructing them. Bundles restore tracked candidates; retained product files or embedded snapshot manifests additionally preserve uncommitted extraction and human notes. Controlled tracker operations are simulations. No credential or external account is needed to inspect the retained observations.

The included `publication-records.json` lists every newly published durable record with exact byte hash and mode. Previously committed records outside this work item remain inherited from the named parent. This publication carries all current evidence and its required history. No old temporary directory is the sole copy of required evidence.

The exact publication preview, approval, resulting snapshot-to-commit mapping and later readback/handoff receipts are local-only records retained in the separately approved recovery directory. A later records-only commit would need separate authority. The PR head supplies the publication commit SHA; comparing its complete product tree with `candidate.json` establishes its mapping to the original snapshot.
