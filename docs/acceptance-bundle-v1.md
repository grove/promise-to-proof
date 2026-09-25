# Acceptance bundle v1

An acceptance bundle lets an independent process check whether retained
`REVIEWED` and `PROVEN` claims are internally consistent without another model
call. Version 1 supports exact contracts and reproducible snapshot candidates.

Run the checker with:

```bash
python3 checks/verify_acceptance_bundle.py <bundle.json>
```

The checker exits zero only when the bundle is valid and its
`REVIEWED_AND_PROVEN` claim follows from a complete `REVIEWED` report and a
complete `PROVEN` report.

## Normative fields

The top-level object has exactly these fields:

| Field | Meaning |
|---|---|
| `schema` | Must be `promise-to-proof/acceptance-bundle/v1`. |
| `claim` | Must be `REVIEWED_AND_PROVEN`. Other combinations are outside v1. |
| `contract` | Exact approved contract and its identity. |
| `candidate` | Recoverable snapshot, identity, and comparison base. |
| `review` | Normalized full-review claim and retained details. |
| `proof` | Normalized full-proof claim, evidence, and retained details. |

All `sha256` fields contain 64 lowercase hexadecimal characters. A retained
text object has exactly `content` and `sha256`; its digest is computed over the
exact UTF-8 bytes of `content` with no text normalization.

### Contract

`contract` has `source`, `revision`, `content`, and `sha256`. Its content follows
the `/plan-acceptance` template and contains exactly one `## Acceptance matrix`.
The matrix header has these columns in this order:

```text
ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state
```

Rows are pipe-delimited, `\|` represents a literal pipe, IDs match `R[1-9][0-9]*`,
and plan state is `planned` or `gap`. IDs are unique. A
`REVIEWED_AND_PROVEN` bundle cannot contain a `gap` row. The contract heading
and `Contract revision` line must match the structured source and revision.

### Candidate

`candidate` has `key`, `manifest`, and `comparison_base`. Version 1 accepts only
`snapshot:sha256:<digest>` keys. The manifest contains every candidate path as
one of:

```json
{"path":"src/app.txt","type":"file","mode":"100644","content_base64":"..."}
{"path":"bin/run","type":"file","mode":"100755","content_base64":"..."}
{"path":"current","type":"symlink","mode":"120000","target":"src/app.txt"}
```

Paths are unique relative POSIX paths without `.` or `..` segments. File content
uses canonical base64. To compute the snapshot digest, sort entries by path and
serialize the array as UTF-8 JSON with sorted object keys, no ASCII escaping, and
separators `,` and `:` without added whitespace. Hash those exact bytes with
SHA-256. `comparison_base` is `git:` followed by a full 40- or 64-character
lowercase object ID.

### Review and proof

Both records repeat `{source, revision, sha256}` for the contract and the exact
candidate key. Each has `stability` with `contract` and `candidate` both set to
`unchanged`. Review also repeats the comparison base and lists every contract
requirement exactly once in `coverage`. Its status must be `REVIEWED`.

Proof lists every contract requirement exactly once in `verdicts`. Its status
must be `PROVEN`, every verdict must be `proven`, and every verdict must reference
at least one retained evidence record whose result is `passed`. Evidence records
have a unique `E[1-9][0-9]*` ID, nonempty assertion and observation, and a retained
text artifact. Every evidence record is referenced. `verification_context`
records the environment needed to interpret the observations.

Review and proof each retain a `details` text object. These details preserve the
human report but are explanatory. The structured fields above are the normative
summary, so implementations should render human summaries from them rather than
maintain a second independently authored verdict.

## Assurance limit

The checker establishes bundle structure, exact identities, coverage, evidence
resolution, and decision consistency. It does not establish that an evidence
artifact is authentic, that an assertion proves its requirement, or that the
contract captures every human intention. Those remain separate assurance
obligations.

## Conformance fixtures

[`valid.json`](../checks/fixtures/acceptance-bundle-v1/valid.json) is the shared
valid bundle. Each entry in
[`invalid-cases.json`](../checks/fixtures/acceptance-bundle-v1/invalid-cases.json)
applies an RFC 7396 JSON Merge Patch to that bundle and names the diagnostic
codes a conforming checker must return. Arrays in a patch replace the base array.