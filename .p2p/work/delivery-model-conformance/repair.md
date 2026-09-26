# REPAIRED: work/delivery-model-conformance.md

Contract: `work/delivery-model-conformance.md` v1.
Contract snapshot: SHA-256 `0751249534a5cf5f21d8f97250e95e4c91a3c5b27ec578f45fc5c21624167237`; exact bytes retained in the candidate and agreement snapshot.
Candidate before: `snapshot:sha256:7a82e6bfc71d1e7fcf2318f9aa18473ed9a92e06c8f0d318b40b9be44dfcf912`.
Candidate after: unchanged, `snapshot:sha256:7a82e6bfc71d1e7fcf2318f9aa18473ed9a92e06c8f0d318b40b9be44dfcf912`.
Comparison base: `833a33647f545afb9028d03bf82d03613415ddf9`.
Addressed requirements: R7 evidence interpretation.
Changed files: generated evidence only; no product, agreement, binding, base or original live receipt changes.
Changed evidence: `evidence/live-host/identity-format.md`, `check-product-identity.py`, and `product-identity-check.json` explain and check the producer's existing canonical-entry hash format.
Focused checks: the stdlib check recomputed the candidate key and compared all 126 canonical manifest-entry hashes to both original live receipts. Both maps match exactly. Summary passed, code_unchanged and source_preserved remain true. `p2p_filesystem.validate` confirms the whole integrated product tree and binding inputs remain unchanged.
Remaining gaps: None in this focused evidence-format repair. Full independent proof must judge R7 and every other requirement.
Recommended next action: full independent review and proof of the unchanged candidate, inspecting the actual producer's hash definition.

The initial NOT PROVEN observation compared hashes of different inputs: decoded regular-file bytes versus canonical JSON entries. The original live run need not be repeated to explain its existing format. No verdict was edited and no new host success was claimed. The original report and observations remain retrievable. This is the one automatic evidence repair/recheck cycle for this invocation.

Fresh `/prove` required before acceptance.

Next steps:

1. `/review-implementation snapshot:sha256:7a82e6bfc71d1e7fcf2318f9aa18473ed9a92e06c8f0d318b40b9be44dfcf912 against 833a33647f545afb9028d03bf82d03613415ddf9`
2. `/prove work/delivery-model-conformance.md; candidate snapshot:sha256:7a82e6bfc71d1e7fcf2318f9aa18473ed9a92e06c8f0d318b40b9be44dfcf912`
