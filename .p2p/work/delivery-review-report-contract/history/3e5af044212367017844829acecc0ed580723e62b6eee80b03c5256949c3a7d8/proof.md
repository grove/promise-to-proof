# PROVEN: delivery review report contract

Requirements: 2/2  
Counterexamples tested: 6

Contract: `/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v2/work/delivery-review-report-contract.md` v2  
Contract snapshot: SHA-256 `3f7baf42d4ec009e43faf74f2bd0f0943a3f205d34e76b9d1ab01af07c915baf`  
Candidate: `snapshot:sha256:441855d0b43448858285af22c319701a8303ac8918694d158708c982ca99beea`  
Comparison base: `a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412`  
Candidate stability: unchanged; validation passed before and after checks. The 127-entry manifest excludes `.p2p/`.  
Contract stability: unchanged; the exact-byte digest matched before and after checks.  
Verification context: Python 3.14.7 at `/opt/homebrew/opt/python@3.14/bin/python3.14`, macOS 26.6.2 arm64; `PYTHONDONTWRITEBYTECODE=1`; `TMPDIR=/private/tmp/p2p-delivery-review-report-contract-v2-proof-scratch`.

## Outcome

The boundary probe passed: create/read/delete worked in the writable cwd; creating a file beside the candidate record was denied with `PermissionError: Operation not permitted`. No candidate-area file was created.

The required candidate validation command exited 0 before and after checks:

```text
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/opt/python@3.14/bin/python3.14 /Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v2/skills/productivity/deliver-issue/scripts/p2p_filesystem.py --repo /Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v2 validate work/delivery-review-report-contract.md --base a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412 >/dev/null
```

Full controller suite command and result:

```text
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp/p2p-delivery-review-report-contract-v2-proof-scratch /opt/homebrew/opt/python@3.14/bin/python3.14 -m unittest discover -s /Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v2/checks -p 'test_p2p_delivery.py' -v

Ran 24 tests in 143.618s
OK
exit=0
```

The fixture suite emitted repeated PATH-alias permission warnings; all tests passed. These fixtures establish controller behavior, not live model behavior. I read the repository constraints, `deliver-issue` skill, and the `review-implementation` source skill. No conflicting source promise was found.

## Requirement verdicts

| ID | Observation and oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | The controller’s review prompt says, “Give a substantive observation for every requirement.” The review schema permits only `id` and `observation`; receipt rejects blank text and rows containing verdict/evidence fields. The review skill requires requirement coverage and evidence-based findings. The proof stage receives the fixed contract and candidate and is prompted to make fresh independent observations; it does not receive or grade the review row. This is the semantic boundary: the controller checks structure, while the stages own substantive judgment. | Full suite: `test_review_prompt_requires_substantive_observations`, `test_review_rejects_blank_observation`, `test_review_rejects_proof_verdict_at_receipt`. Focused fixture probes confirmed whitespace-only observations and proof-evidence fields fail before review storage or proof dispatch. A nonblank `x` observation was accepted and stored, as v2 allows. | proven |
| R2 | Exact top-level fields are checked before persistence, so extra `details` is rejected. `REVIEWED` with findings is rejected before storage or proof dispatch; `CHANGES NEEDED` requires a finding. Successful-path checks confirmed review JSON is rendered into both Markdown copies, while implementation and proof Markdown still equal their `details` fields. Comparison with the base schema found the implementation, repair, and proof field/constraint shapes unchanged; only the order of schema property declarations differs, which does not change JSON Schema semantics. | Full suite: `test_review_rejects_free_text_status_conflict`, `test_reviewed_report_cannot_contain_findings`, `test_success_source_preservation_and_retrieval`. Focused probes asserted no stored review and no proof dispatch for a contradictory finding or extra `details`; rendering and other-stage persistence assertions passed. | proven |

## Unresolved gaps

- No implementation gap remains. The fixture transport does not establish that a live model always follows the substantive-observation instruction. The accepted `x` case confirms that receipt does not enforce semantic quality; this is the explicit v2 boundary, not a controller guarantee.

## Repairs needed

- None.

Fresh `/prove` is required after any repair. Refresh `/review-implementation` separately for any changed candidate.

## Next steps

1. Run `/review-implementation .p2p/work/delivery-review-report-contract/candidate.json against a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412` in a separate review context. This verifier did not inspect or rely on any review report.
2. Treat acceptance evidence as complete only after a matching full `REVIEWED` report is confirmed for this contract and candidate. No further local proof action is required unless publication is wanted.