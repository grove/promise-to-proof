# PROVEN: delivery review report contract

Requirements: 2/2  
Counterexamples tested: 5  
Contract: [work/delivery-review-report-contract.md](/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v3/work/delivery-review-report-contract.md) v2  
Contract snapshot: SHA-256 `4b938335d31490f366ea712b2393dc10f4695246b96b5560c15d40257ce03316`  
Candidate: `snapshot:sha256:ddce1e6befec6c3c226e34dfa936ffdae14a5d17ddaa5f72a03f34903d3093ee`  
Comparison base: `a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412`  
Candidate stability: unchanged  
Contract stability: unchanged  
Verification context: Python 3.14.7 CPython; macOS 26.6.2 arm64; cwd and `TMPDIR` `/private/tmp/p2p-delivery-review-report-contract-v3-proof-scratch`.

## Outcome

The candidate and v2 contract identities validated before and after checks. The review prompt, schema, receipt checks, persistence, rendering, and source skill instructions satisfy R1 and R2. The review outcome vocabulary matches the source skill; no contract discrepancy was found.

## Requirement verdicts

| ID | Observation and oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | The review prompt explicitly requests a substantive observation for every requirement. The review schema permits only `id` and `observation`; receipt checks reject blank observations, review verdicts, and proof evidence. The review and proof instructions assign semantic judgment to those stages: review requires evidence-based findings, while proof requires observations and independent oracles. | `p2p_delivery.py`: `report_schema`, `stage`, and receipt checks; `review-implementation/SKILL.md`; `prove/SKILL.md`; full suite’s `test_review_prompt_requires_substantive_observations`, `test_review_rejects_blank_observation`, and `test_review_rejects_proof_verdict_at_receipt`. | proven |
| R2 | Review status is limited to `REVIEWED`, `CHANGES NEEDED`, or `BLOCKED`. Exact field checks reject free-text details and extra fields; `REVIEWED` requires empty findings and gaps; `CHANGES NEEDED` requires a finding. The controller renders Markdown from validated structured fields and checks that rendering on readback. Non-review schemas exactly match the base schemas. | Full suite’s five rejection cases and `test_success_source_preservation_and_retrieval`; schema comparison output below. | proven |

## Verification observations

- Boundary probe: scratch cwd create/read/delete **PASS**. Candidate-directory write probe **denied** with `PermissionError: [Errno 1] Operation not permitted`; no probe file remained.
- Before and after checks, the requested `p2p_filesystem.py validate ... --base a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412` command exited 0. The work-item SHA-256 matched the contract digest; candidate key and comparison base matched the values above. The candidate record was read only for identity fields and manifest path/mode inventory; base64 manifest data was not printed.
- Read-only schema comparison against base `a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412` reported:
  - `implementation schema exactly matches base: True`
  - `proof schema exactly matches base: True`
  - `repair schema exactly matches base: True`

Full controller suite command:

```text
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp/p2p-delivery-review-report-contract-v3-proof-scratch /opt/homebrew/opt/python@3.14/bin/python3.14 -m unittest discover -s /Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate-v3/checks -p 'test_p2p_delivery.py' -v
```

Result:

```text
Ran 25 tests in 119.909s

OK
exit_code=0
```

The five rejection cases exercised unsupported `PROVEN` status, free-text details, a review-row proof verdict, findings with `REVIEWED`, and a whitespace-only observation. Tests emitted PATH-alias permission warnings in some cases; the affected tests passed.

**R1 boundary:** the receipt check tests only `observation.strip()`, so a nonblank placeholder such as `x` can pass controller receipt. That matches the contract’s explicit structural boundary; semantic quality relies on stage instructions and judgment. Fixture transport establishes controller behavior, not that a live model always follows the substantive-observation prompt.

## Unresolved gaps

- No unmet contract requirement. Live-model compliance with the substantive-observation instruction is not established by fixture transport.

## Repairs needed

- None.

Fresh `/prove` is required after any repair.  
Refresh `/review-implementation` for the changed candidate as a separate phase.

Next steps:

1. The matching review report was not inspected, as instructed. If one is absent for this candidate and base, run `/review-implementation .p2p/work/delivery-review-report-contract/candidate.json against a557e05ef0f4267a3ce1b45d1b6cc93b03b3d412`.
2. After this proof is saved, if a matching full `REVIEWED` report exists, acceptance evidence is complete for this candidate.