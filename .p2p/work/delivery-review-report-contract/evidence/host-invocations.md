# Host invocations and isolation evidence

Host: Codex CLI 0.157.1 on macOS Darwin 25.6.0 arm64; Python 3.14.7. Each final stage ran in a fresh `codex exec` session with a separate `/private/tmp` scratch workspace. The candidate lived in the repository's ignored `.p2p/tmp/` directory and was validated before and after each stage.

## Historical v5 candidate

- Candidate: `snapshot:sha256:ba332bf48e9ff1a00853a6b6ecc3d604016cb2be5c2ce5354c8b1ac8962610f4`; base `d0467b7bbaed2078e7e677b6ce3be407d4fb2058`.
- Review session `01a0e001-dd21-7032-840e-891cf39fe257`: `REVIEWED`; nine focused tests passed in 42.635 seconds. Raw output and prompt are preserved as `evidence/host/review-v5-final.jsonl` and `review-v5.prompt.md`.
- Proof session `01a0e00f-9b7e-74d3-b9ff-b2a4da5948c0`: `NOT PROVEN`, R2. The generated comparison line omitted included working-tree scope. The report is retained in `history/`; raw output and prompt are `evidence/host/proof-v5-final.jsonl` and `proof-v5.prompt.md`.
- The R2 repair now lists exact changed paths and is covered by the generated-report assertion.

## Current v6 candidate

- Candidate: `snapshot:sha256:049685d89b12994ec0ba84cf9bc451badba0de16c147c5e911a093a0f83f6d31`.
- Contract: `work/delivery-review-report-contract.md` v3, SHA-256 `b490dc25a68ba6521282128bcf60bc3f77e8a11b907b0c9b385402fa230677cb`.
- Comparison base: `18bab308a297b9af978d6dcf3e1107cd5eaedce5`; this was both `HEAD` and `origin/main` at capture. The exact base-to-candidate scope is the controller, its test file, and the new contract.
- Review session `01a0e01d-f4de-7be3-820f-a9f1a292c18e`: `REVIEWED`, no material findings; nine focused tests passed in 44.375 seconds. The raw host report contains a one-character digest transcription error; `review.md` corrects that display and records the correction. Raw JSONL and prompt are retained as `evidence/host/review-v6-final.jsonl` and `review-v6.prompt.md`.
- Proof session `01a0e022-a390-7d01-aac5-382f3e6ce8e3`: `PROVEN`, 3/3 requirements. The full controller suite passed: 35 tests in 170.263 seconds. The full suite log and raw host transcript are `evidence/host/proof-v6-unittest.log` and `proof-v6-final.jsonl`; the prompt is `proof-v6.prompt.md`.
- The review and proof scratch paths were separate and outside the candidate. Fixture transport does not establish live-host behavior; the contract excludes live-host claims from this fixture evidence.

## Rebase state

The final checkout is on `main` at the same commit as `origin/main`: `18bab308a297b9af978d6dcf3e1107cd5eaedce5`. No local commits remained to replay onto that tip, so it is also the v6 comparison base. The earlier v5 base is historical and is not used by the final review or proof.
