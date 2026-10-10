# From proven to confirmed delivered

The **Promise to Proof** controller can establish that one exact version of
your code passed independent review and proof. It cannot infer from that result
that GitHub merged a pull request or that the final code was retained.

Finalization is the last, separately authorized part of that same delivery.
It confirms the code actually landed, verifies its relationship to the proven
candidate, and stores one retrievable completion receipt. The original
[Delivery Record v1](delivery-record-v1.md) stays the single machine-readable
record: finalization uses its optional `landing` fields, not a new schema.

## What the statuses mean

| Status | What you can rely on |
|---|---|
| Local `REVIEWED_AND_PROVEN` | P2P reviewed and proved one unchanged candidate; publication is **not** established |
| `READY_TO_MERGE` | The open PR's saved READY assessment and current GitHub gates match; the merge is **not** authorized or executed by a preview |
| `PARTIAL` | A merge or receipt effect may have happened, or a delivered mapping could not be verified. The retained work is recoverable; P2P does not dispatch a duplicate effect |
| `READY_TO_RECORD` | The actual delivered Git mapping, saved proof, and #82 published checkpoint were verified. Receipt publication is **not** yet confirmed |
| `FINALIZED` | GitHub/remote code, #50 mapping, portable checkpoint and exact durable receipt were independently read back and agree |

A receipt is not a claim that regressions can never happen. It records which
change was reviewed, proven, and delivered under one exact agreement.

## Normal one-request flow

If the original `/deliver-issue` request includes publication and final
delivery, and the standing mandate grants the exact effects, the outer
workflow continues through `publish-pr`, `merge-readiness`, and finalization
without asking you to select additional stages or copy internal paths.

The finalizer rereads current PR, target branch, review approvals, effective
branch rules and required checks. A passing integration check must apply to the
exact current head/target pair. It never treats green head-only CI, a clean
mergeability flag, or a readiness comment as sufficient by itself.

A covering `merge` grant applies to the exact PR URL. The operation reserves
one durable intent in the **existing** `merge-readiness.md` report immediately
before the effect. A lost response requires readback, never a blind second merge.
For a previously merged PR it skips the merge and checks actual ordinary,
squash, or rebase Git history with #50.

A confirmed merge is still **partial** if its resulting tree, remote candidate
objects, portable #82 checkpoint or final receipt cannot be recovered. The
workflow does not delete its local workspace during that uncertainty.

## Inspect or resume the same work

The read-only preview and authorized completion use the same arguments, and
both consume the existing compact `delivery.json` and #82 checkpoint.
Use the exact files produced for your work item:

```bash
python3 skills/productivity/deliver-issue/scripts/p2p_finalize.py \
  --repo /my/project preview .p2p/work/example/artifacts/delivery.json \
  --checkpoint p2p-state/example.json \
  --repository OWNER/REPO --remote origin --method squash \
  --pr https://github.com/OWNER/REPO/pull/123 \
  --readiness .p2p/work/example/merge-readiness.md

python3 skills/productivity/deliver-issue/scripts/p2p_finalize.py \
  --repo /my/project finalize .p2p/work/example/artifacts/delivery.json \
  --checkpoint p2p-state/example.json \
  --repository OWNER/REPO --remote origin --method squash \
  --pr https://github.com/OWNER/REPO/pull/123 \
  --readiness .p2p/work/example/merge-readiness.md \
  --mandate /path/to/approved-mandate.json
```

For an **already merged** PR, the current GitHub readback supplies the actual
delivered commit and merge time; no READY assessment or merge effect is needed.
A rebased result additionally needs `--before FULL_PRE_MERGE_TARGET_SHA`:
that predecessor cannot safely be guessed from a squashed or rewritten history.

For an issue-less, no-PR **direct** delivery or independently assembled
parent, supply `--method direct` or `--method integrated`,
`--before FULL_SHA --after FULL_SHA --confirmed-at ISO_TIME`, and
`--receipt-ref refs/heads/p2p/receipts/example`. The target code and
published checkpoint must already exist. A standing mandate with exact
`branch-create`, `commit` and `push` grants can create the receipt branch
automatically from a single published checkpoint base. The resulting commit
uses a private temporary Git index and does not change your checkout or
staging area. No synthetic GitHub issue or parent PR is needed.

## Where the receipt goes

P2P prefers the original source issue when the agreement came from GitHub.
Otherwise it uses the matching PR's comments. Those writes require a precise
`issue-comment` grant for the destination URL. If neither exists, it uses
an explicitly selected Git receipt branch with exact effect grants.

The receipt is the **same** canonical Delivery Record v1 and its stable #50
receipt ID. Comments and Git receipt objects are checked before writing and
read back after any attempted write. For GitHub comments, an exact attempted
write is reserved in the existing `publication.md` handoff before POST. A
lost response stays `PARTIAL` and a later session reconciles the remote
comment; it never blindly posts a second copy. Identical confirmed retries
reuse one verified receipt, while conflicts or duplicate records block.
Git receipt pushes use deterministic commits and check the exact remote ref
after every response.

The remote must also retain the original #82 checkpoint bytes and reachable
source/candidate Git objects. A portable checkpoint is an evidence handoff,
not permission to merge, and the final record adds no raw logs or temporary
execution archive.

## Safety boundary

The finalizer runs no implementation, proof or review workers, and issues no
automatic cleanup or issue closure. It grants no new permissions. A separate
`issue-update` grant is needed to close a source issue; GitHub's reply must
also be read back. Existing controller cleanup may be used **only after**
complete finalization, applying its normal safe retention checks.

A missing authority, pending CI, changed PR head/base, unknown branch policy,
merge queue requiring a currently unsupported path, overlapping delivered
changes, or missing remote record yields a specific blocker or partial result.
A saved READY report by itself can never authorize a merge.

For developers, deterministic offline tests live in
`checks/test_p2p_finalization.py`. They use fixture Git repositories and
simulated GitHub readback. They are **not** evidence of a live Codex/macOS
delivery or a real repository merge.
