# Delivery Record v1: local acceptance and actual delivered code

One existing record, two distinct claims. The controller's compact
`promise-to-proof/delivery-record/v1` remains the normative machine-readable
record for an accepted work item. The new optional `landing` section describes
a candidate-to-delivered-code mapping. It does **not** replace the local record,
change the contract, create a second status store, or perform a merge.

## What can we truthfully claim?

| Evidence | Meaning |
|---|---|
| `status: REVIEWED_AND_PROVEN`, no `landing` | One **local** exact candidate has matching independent review and proof. Nothing here says a branch, PR or destination was updated |
| Validated `landing.status: LANDED` extension | The recorded delivered Git commit and product tree match the reviewed candidate on the recorded destination history, under the *current local reference observation*. The old top-level local verdict is unchanged |
| Remotely published and read-back completion receipt | **Not established by this read-only validator.** The [authorized #47 workflow](finalization.md) performs and verifies separately granted merge and receipt effects |

A new `landing` may be constructed only from a passing local record and
recoverable #82 checkpoint. A GitHub PR title, merge note, agent assertion, an
issue label or a digest pointing to deleted raw logs cannot substitute for that
evidence. Every stage verdict remains attached to its original candidate/base.

## Existing local format

The stored compact `artifacts/delivery.json` already contains:

- `schema`, `status`, `work_item`, unique `invocation_id`;
- the exact contract's `source`, `revision`, `sha256`, and binding-input
  path/digest pairs;
- frozen `comparison_base`, full candidate product-tree key,
  `candidate_record_sha256`, canonical `candidate_changes_sha256`,
  `agreement_paths` excluded from the product candidate;
- independent `review_sha256`, `proof_sha256`, `completed_at`;
- admitted mandate/limits/history/routing, cleanup receipt, and any existing
  issue publication fact.

Earlier valid local records retain this meaning *byte for byte*. This change
adds no required fields to old records. The verifier recomputes agreement and
candidate hashes and reads back retained review/proof content rather than
accepting a digest with no retrievable supporting bytes.

## Optional `landing` object

A completed mapping extends the **same** record:

```json
{
  "status": "LANDED",
  "event_id": "<64 lowercase hex>",
  "receipt_id": "sha256:<64 lowercase hex>",
  "method": "merge",
  "repository": "OWNER/REPO",
  "destination": {
    "ref": "refs/heads/main",
    "before": "<full exact destination predecessor commit>",
    "after": "<full exact delivered commit>",
    "tree": "<actual Git tree object ID for after>"
  },
  "candidate_commit": "<full exact retained #82 candidate commit>",
  "pull_request": {
    "url": "https://github.com/OWNER/REPO/pull/42",
    "head": "<full exact PR head commit>",
    "merged_at": "2026-10-10T12:00:00+00:00"
  },
  "checkpoint_sha256": "<exact bytes of existing #82 checkpoint>",
  "confirmed_at": "2026-10-10T12:01:00+00:00",
  "evidence_refs": []
}
```

`pull_request` may be `null` for direct/spec-based work or parent integration.
`method` is one of `merge`, `squash`, `rebase`, `direct`, or
`integrated` (an assembled parent already landed without a new parent PR).
`evidence_refs` contains only essential, retrievable, SHA-256-checked optional
normalized evidence (issue #51) and may be empty when the full proof report is
sufficient. A normalized observation does not itself award `PROVEN`.

The mapping validator confirms that:

1. The exact contract and all accepted binding inputs are retrievable from
   the existing #82 checkpoint or compact artifacts and match their saved
   digests. The candidate product tree, base and changed-file identity match.
2. The #82 execution checkpoint retains both **full** independent review and
   proof reports with their original input identities, requirement coverage,
   accepted host-stage receipts and distinct verifier sessions. Proving
   evidence is present for every accepted requirement.
3. The retained candidate commit has the exact originally accepted tree, and
   its change set applied to the recorded target predecessor produces **all
   and only** the delivered product tree. Independent changes on unrelated
   destination paths are allowed, overlapping unreviewed edits are rejected.
4. For an ordinary merge, the delivered commit has the correct first parent
   (destination predecessor) and reviewed PR-head second parent. Squash/direct
   commits must have the exact predecessor as their sole parent; rebases are
   a verifiable linear chain. A separately assembled parent must have current
   combined parent acceptance and no fictitious parent PR.
5. The delivered commit is in the recorded local destination ref's ancestry,
   and the target, PR (if any), Git tree and stable event/receipt IDs match.
   **This is local Git evidence, not proof the remote was updated**. #47 must
   independently read back remote state immediately before and after effects.

No unknown merge strategy, missing/changed record, forged path, stale PR head,
unsupported parent shortcut, unreviewed scope expansion or broken source
identity can silently become a completed mapping.

## Stable identity and retries

Use the repository's canonical JSON: UTF-8, sorted keys, separators `,` and
`:`, no ASCII escaping and no trailing newline for hashing. The stable
`receipt_id` hashes the accepted invocation, contract, frozen base, exact
candidate and changed scope, delivery method, repository, destination history,
source candidate commit and optional PR URL/head. `event_id` hashes the
invocation, repository, destination ref and delivered commit.

Observation timestamp, transcript location, checkpoint publication transport,
and retry time do **not** change those IDs. Identical replays reuse the
original record and its confirmed timestamp; attempts to replace an event with
a conflicting mapping are rejected. Timestamps still require ISO 8601 offsets,
and the original human-approved contract bytes are never normalized.

## Portable recovery without retaining a new archive

Use one #82 `p2p-state/<slug>.json` or selected GitHub issue checkpoint, and
the published candidate/source Git objects. The validator reads and validates
the existing checkpoint, its contract and bindings, stage reports and receipts.
No whole execution workspace, raw logs or extra completion database is needed.

The checkpoint must be actually made portable and its destination verified by
the existing #82 transport before #47 claims a durable external receipt.
This module validates **bytes and local Git reachability**, not a remote write.

## Preview and validate (no effects)

```bash
python3 skills/productivity/deliver-issue/scripts/p2p_delivery_record.py \
  --repo /source validate .p2p/work/example/artifacts/delivery.json \
  --artifacts .p2p/work/example/artifacts

python3 skills/productivity/deliver-issue/scripts/p2p_delivery_record.py \
  --repo /source preview DELIVERY_RECORD_JSON \
  --checkpoint p2p-state/example.json \
  --method squash --repository OWNER/REPO \
  --destination-ref refs/heads/main \
  --before FULL_PREVIOUS_SHA --after FULL_LANDED_SHA \
  --confirmed-at 2026-10-10T12:01:00+00:00
```

For a merge-backed mapping pass `--pull-request URL --pr-head FULL_SHA
--merged-at OFFSET_ISO_TIME`. An approved #47 workflow provides those facts
after authoritative readback. The preview prints an **unpublished** record
and verification result; it never commits, pushes, creates a PR, merges,
publishes a receipt, closes an issue, or changes effect authority.

The exact machine record is the sole normative source. The renderer derives
ordinary words from the validated record, without a parallel approved summary.

Test locally with `python3 checks/test_p2p_delivery_record.py`. These are
deterministic disposable Git fixtures, **not live macOS/Codex evidence**.
