# P2P Evidence Record v1

<!-- p2p-instruction-dependencies: -->

One record describes one concrete observation. It captures facts, while `/prove`
chooses checks and oracles and decides requirement verdicts in `proof.md`.
Records are optional. A valid record never implies a requirement is proven.
The stdlib checker lives in `checks/`, following acceptance bundle v1; it is not
bundled into installed skills. No runner or receipt producer is provided.

## Record schema

The JSON object has these required fields. Unknown fields are rejected, including
`verdict` and a self-declared record digest. Strings must contain non-whitespace text.

| Field | Representation |
|---|---|
| `schema` | Exactly `promise-to-proof/evidence-record/v1` |
| `id` | Stable nonempty evidence ID, chosen by the producer (for example `E7`) |
| `candidate` | `git:` plus 40 or 64 lowercase hex characters, or `snapshot:sha256:` plus 64 lowercase hex characters; never a branch or `HEAD` |
| `contract` | Object containing only nonempty `source`, revision `v[1-9][0-9]*`, and `sha256` of exact UTF-8 contract text (64 lowercase hex) |
| `requirements` | Nonempty array of unique IDs matching `R[1-9][0-9]*` |
| `type` | Nonempty method name; `command` and `test` require receipts; examples include `http`, `browser`, `manual`, `external`, `static`, `invariant`, `ci` or another explicit method |
| `assertion` | Explicit statement being checked |
| `observation` | Explicit observed result |
| `oracle` | Object with nonempty `expected_result`, optionally integer `expected_exit_status`; describes the expected result, never an observed execution fact |
| `outcome` | Only `passed`, `failed`, or `inconclusive`, describing this observation; never `proven`, `not proven`, `disproven`, `PROVEN`, or `NOT PROVEN` |
| `environment` | Nonempty observation/execution environment identity and description |
| `timestamp` | ISO 8601 observation timestamp with timezone |
| `limitations` | Explicit array of nonempty limitation/unavailable-context/access-restriction statements; `[]` explicitly means none stated |

Optional fields:

| Field | Representation |
|---|---|
| `execution` | Runner-observed facts defined below; required for `command` and `test` |
| `provenance` | Nonempty statement naming the strongest available authoritative reference; required whenever there is no receipt, including manual/external and HTTP/browser observations |
| `interpretation` | Separately named, nonempty prover-authored explanation; may exist without execution for manual evidence |
| `artifacts` | Optional array (may be empty) of objects with nonempty `reference`, 64-lowercase-hex `sha256`, and optional nonempty `limitation`; no raw artifacts are required |

The checker validates artifact reference structure, not referenced bytes or access.

## Execution facts and trusted receipts

`execution` contains only the following fields:

- `identity`: nonempty command, tool, or interface identity (for example the exact
  command line or HTTP method and URL).
- `exit_status`: integer observed exit status or equivalent interface machine status.
- Exactly one of `output_sha256` (64 lowercase hex) or `result` (nonempty compact
  machine result identity); raw output is never required.
- `started_at` and `finished_at`: timezone-bearing ISO 8601 timestamps. Finish
  cannot precede start.
- Optional `receipt`: object containing only nonempty `id` and 64-lowercase-hex
  `sha256`. This reference is mandatory for `command` and `test` evidence.

Runner-observed fact keys (`identity`, `exit_status`, output fields and start/finish
fields, or `command`, `tool`, `interface`, `output_digest`) anywhere outside
`execution`, including inside interpretation objects, are rejected. The top-level
`environment` is explicitly the observation environment and must match its receipt.
A `passed` outcome with an oracle `expected_exit_status` must match the observed
`execution.exit_status`; `failed` and `inconclusive` may describe a mismatch.

A trusted receipt is a JSON object with the same execution facts (without a
`receipt` reference), plus nonempty `id`, exact `candidate`, and nonempty
`environment`. Its digest uses the same canonical rule below. The proof context
supplies receipts obtained from its trusted host/controller, not manufactured by
the prover. All fields are required except the alternative output/result fields.

Standalone checking validates structure and the presence of a receipt reference;
it cannot establish that the receipt exists or that it is trusted. Context checking
requires exactly one matching receipt ID, recomputes the receipt digest, and checks
candidate, environment, identity, exit status, output/result, and timestamps for
exact equality. A command narrative without a receipt reference is rejected.
Until a host emits receipts, `/prove` continues documenting self-run commands in
`proof.md`; evidence records remain optional. Fixtures illustrate the receipt
shape and do not claim to have implemented a trusted runner.

## Proof context

`verify_record(record, context=None)` returns deterministic diagnostics, each with
`code`, `path`, and `message`. No context means structural validation only.
A supplied context has only `candidate`, `contract`, and `receipts`:

- `candidate`: the exact candidate key.
- `contract`: record contract identity fields plus `content`, the exact UTF-8
  acceptance contract text. Its SHA-256 is recomputed; record source, revision,
  digest and candidate must match this context.
- `receipts`: an array of trusted receipts (may be empty for non-command evidence).

Every referenced requirement ID must occur in the acceptance matrix parsed by
`checks/verify_acceptance_bundle.py`. A matrix row with plan state `gap` may have
an observation; it does not make this record a `REVIEWED_AND_PROVEN` bundle.
Unknown fields, malformed types, invalid identities, result inconsistencies,
missing receipts/provenance and mismatching context facts cause diagnostics.

## Canonicalization and reference

`canonical_bytes(obj)` is UTF-8 JSON with sorted object keys, no ASCII escaping,
`,` and `:` separators and no trailing newline. Non-finite numbers are rejected.
There is no Unicode normalization or timestamp rewriting: changed facts change
identity. `record_digest(record)` is SHA-256 of these canonical bytes, computed
externally to the record. The same rule digests receipts. Contract digests instead
hash exact UTF-8 contract text, including its retained whitespace and final newline.

The stable compact reference is `<id>@sha256:<record-digest>`, for example an
`E7@sha256:…` reference with all 64 digest characters. Requirement traceability
(#41) can cite this reference without copying assertion or observation content.
`render_record(record)` deterministically derives Markdown only from the record,
including its compact reference, candidate, contract, requirements, assertion,
oracle, observation, outcome, environment, receipt, and limitations. Validate
before rendering; rendering assigns no requirement verdict.

```sh
python3 checks/verify_evidence_record.py checks/fixtures/evidence-record-v1/command.json
python3 checks/verify_evidence_record.py checks/fixtures/evidence-record-v1/command.json --context checks/fixtures/evidence-record-v1/context.json --render
python3 checks/test_verify_evidence_record.py
```

CLI exit 0 means valid; invalid input or diagnostics exit 1. `--render` emits
exactly the function's Markdown on success. Fixtures include command/test, HTTP,
and manual evidence, pinned record digests, a proof context, and deliberate
corruptions expressed as RFC 7396 merge patches with expected diagnostic codes.
No fixture contains raw logs.

## Storage and retention

During active work records may live under ignored `.p2p/work/<slug>/evidence/`.
`proof.md` may retain important observations directly; Delivery Record v1 (#50)
may retain only the reference, digest, and summary. Separate records stay durable
only when a claim cannot otherwise be substantiated by final proof/delivery
records. Routine records, raw transcripts, verbose logs and temporary execution
exhaust need not survive cleanup. Nothing in the checker requires permanent
retention or resolves stored record files after cleanup.

## Assurance boundary

A valid record establishes only structural consistency and binding to the named
contract/candidate and, when supplied, receipt. It does not establish authenticity
of the observation, oracle correctness, sufficiency for a requirement, production
representativeness of the environment, or absence of fabrication by an untrusted
producer. Trust in the receipt source and the meaning of its result remain
separate assurance obligations. This format adds no signing, attestation, database,
evidence service, test DSL or universal verification strategy.
