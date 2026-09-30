# Evidence Record v1

A Promise to Proof Evidence Record represents one concrete observation used by
proof. It is a compact protocol object, not a requirement verdict, test DSL, or
permanent evidence store.

Validate a record with:

```bash
python3 checks/verify_evidence_record.py <record.json>
```

When the proof context is available, bind the record to the exact contract,
candidate, and known requirements too:

```bash
python3 checks/verify_evidence_record.py <record.json> --context <context.json>
```

Add `--render` to produce deterministic Markdown derived from the normalized
facts. The rendering is a view, not a second source of truth.

## Schema and canonical identity

`schema` is exactly `promise-to-proof/evidence-record/v1`. A record has exactly
these top-level fields:

| Field | Meaning |
|---|---|
| `schema` | Evidence Record v1 schema identifier. |
| `id` | `evidence:sha256:<digest>` canonical identity. |
| `contract` | Exact acceptance-contract source, revision, and SHA-256. |
| `candidate_key` | Exact `snapshot:sha256:...` or full `git:...` candidate identity. |
| `requirements` | One or more requirement IDs supported by the observation. |
| `type` | Small evidence-type classification. |
| `assertion` | The concrete proposition being checked. |
| `observation` | What was actually observed. |
| `oracle` | The independent expected result or comparison rule. |
| `result` | Observation result: `passed`, `failed`, or `inconclusive`. |
| `environment` | Stable environment identity plus readable description. |
| `observed_at` | Time of observation with timezone. |
| `execution` | Trusted execution facts, or `null` when not applicable. |
| `reference` | Authoritative non-command/interface provenance, or `null`. |
| `artifact` | Retained artifact/reference and digest, or `null`. |
| `limitations` | Explicit limits, unavailable context, or access restrictions. |

To compute the evidence ID, remove only `id`, serialize the remaining object as
UTF-8 JSON with sorted object keys, `ensure_ascii=false`, and separators `,` and
`:` with no extra whitespace, then SHA-256 those exact bytes. Prefix the lowercase
hex digest with `evidence:sha256:`.
Requirement IDs are a canonical numeric-order array (`R1`, `R2`, ...), not an
unordered set with multiple encodings. Duplicate or out-of-order IDs are invalid.

The same exact observation reconstructed from the same facts therefore has the
same identity. Changing the candidate, contract, execution receipt, observation,
reference, limitation, timestamp, or any other fact changes the identity.

## Evidence types and observation sources

Version 1 keeps the type system deliberately small:

`test`, `command`, `http`, `browser`, `static-analysis`, `invariant`, `ci`,
`manual`, `external`, and `other`.

Executable evidence (`test`, `command`, `static-analysis`, `invariant`, `ci`)
must carry `execution`. The execution object records:

- stable receipt identity;
- the exact candidate identity;
- the exact environment identity;
- tool/interface and command;
- machine exit status and the expected exit status for this observation;
- SHA-256 of retained or compact output;
- start and finish timestamps.

The execution candidate and environment must match the enclosing record. This
prevents a prover from satisfying executable-evidence fields merely by restating
an unsupported command/result narrative. Structural validation does **not** prove
that the receipt producer was trusted; trust in the runner remains an external
assurance obligation.

Manual and external observations require `reference` with its kind, locator, and
optional SHA-256. HTTP/browser evidence requires either an execution receipt or
an authoritative reference. `artifact`, when present, identifies retained
supporting material by name, SHA-256, and safe locator.

A record's `assertion`, `observation`, and `oracle` remain separate. The record
contains the observation result, but it does not encode `PROVEN`, `NOT PROVEN`,
or `DISPROVEN` as an intrinsic property. `/prove` remains responsible for the
requirement-level judgment and for deciding whether the oracle and evidence are
sufficient.

## Proof-context validation

Intrinsic validation can check schema, identities, canonicalization, internal
consistency, required execution/reference facts, and digest structure. It cannot
know whether `R7` exists in a particular acceptance contract unless that context
is supplied.

A proof-context JSON object has exactly:

```json
{
  "contract": {"source": "work/example.md", "revision": "v1", "sha256": "<64 hex>"},
  "candidate_key": "snapshot:sha256:<64 hex>",
  "requirement_ids": ["R1", "R2"]
}
```

With `--context`, the validator rejects contract mismatch, candidate mismatch,
and requirement IDs unknown to that proof context.

## Human-readable rendering

`--render` produces a compact Markdown summary from the normalized fields. Do not
maintain a separately authored evidence summary with independent facts. A proof
report may quote or embed the deterministic rendering and add its own reasoning
about what the evidence establishes.

## Storage and retention

Normalized evidence may live under ignored `.p2p/work/<slug>/evidence/` while a
delivery is active. Normalization is for precision, not retention expansion.
After successful completion, keep separate evidence records or artifacts only
when the final proof/delivery record cannot adequately substantiate the claim by
summary and digest. Raw transcripts, verbose logs, generated fixtures, and other
execution exhaust remain disposable under the shared protocol.

Requirement traceability may reference an evidence ID without copying the record.
A later delivery record may retain selected evidence IDs/digests without requiring
every local record to survive cleanup.

Evidence Record v1 is additive to the existing `acceptance-bundle/v1` format. It
does not silently change that bundle's embedded evidence shape. `/prove` may use
normalized records as observation inputs; requirement traceability may point to
their IDs; a later durable delivery format may retain selected IDs or digests.

## Assurance boundary

A valid Evidence Record v1 establishes only that the record:

- is structurally consistent and deterministically identified;
- names an exact acceptance contract and candidate;
- names concrete requirements, assertion, observation, oracle, and result;
- carries the required execution or reference facts for its evidence type;
- matches a supplied proof context when context validation is requested.

It does **not** establish that the observation is authentic, that a referenced
runner or source is trustworthy, that the oracle is correct, that the check is
sufficient for a requirement, that the environment represents production, or
that an untrusted producer did not fabricate the record. Those are separate
assurance obligations evaluated by `/prove` and the surrounding delivery process.

## Conformance fixtures

`checks/fixtures/evidence-record-v1/` contains valid command/test, HTTP/interface,
and manual/external examples plus a proof context and deliberately corrupted
variants. `checks/test_verify_evidence_record.py` checks deterministic identity,
validation, context mismatch handling, trusted-execution requirements, and
stable Markdown rendering.
