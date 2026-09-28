# Acceptance planning handoff: issue #37

Status: Approved in the planning conversation; issue-only recovery requires transfer of this receipt.
Canonical contract: [work/frozen-delivery-base.md](../../../work/frozen-delivery-base.md)
Contract revision: v2
Contract SHA-256: `3925c513a6702b94fbc2fcfc30f7d2d057638a275ae103056031cb3ca38aa0a9`
Planning comment: https://github.com/grove/promise-to-proof/issues/37#issuecomment-5856184632
Comment ID: `5856184632`
Comment last updated at readback: 2026-09-27T13:16:32Z
Comment body SHA-256: `aa7e6abe92cae3ce70ba9f6893a22cb7c03c103d2014d1ea27efb2d87a241ab7`
Readback verified: 2026-09-27T13:17:24.213859+00:00

Binding source: [plans/frozen-delivery-under-moving-targets.md](../../../plans/frozen-delivery-under-moving-targets.md)
Binding source SHA-256: `c570232a7371a53fd6dad954ec9d53f7940ecba171b3a2080fd995a6bd9a77d2`
Source commit: `39cf3a96aaf89789fceed9b0454682f9e88bc0b8`
Source issue: https://github.com/grove/promise-to-proof/issues/37
Issue updated at import: 2026-09-27T13:07:41Z
Imported issue body SHA-256: `40b775d1eeea58c5e7dc3e59a554434c772b4fb85b9f4d609692e0d6d99d109c`
The exact issue body is embedded in the contract. No comments, existing handoffs, approvals, amendments, or parent decomposition were present before publication. The needs-triage label was not changed or treated as approval.

## Authority and decisions

The user directly invoked plan-acceptance on issue #37. Its standalone planning rule authorizes this proposal comment and readback. It does not authorize implementation, staging, commits, label edits, issue-body replacement, PRs, or merging.

The user resolved the unsliced admission question in this conversation. Exact question: "Use this rule for unsliced runs: resolve an explicit workflow destination or an unambiguous configured upstream, block before dispatch if neither can be established, and add no required CLI argument?"

Exact response: "Yes, include that rule in the proposal."

Source: request_user_input_async call `call_AMcJo3OYbsQ3dhkWkfdYZAS7`, question 0, user reply in this conversation. This approves inclusion of that rule, not the full contract. The published contract retains this decision for issue-only retrieval.

Contract approver: The user in the planning conversation.
Contract approval evidence: "I approve it"
Approval source: User message immediately following the assistant's final planning handoff identifying contract v2 and https://github.com/grove/promise-to-proof/issues/37#issuecomment-5856184632, on 2026-09-27.
Approved contract SHA-256: `3925c513a6702b94fbc2fcfc30f7d2d057638a275ae103056031cb3ca38aa0a9`
Approved binding source SHA-256: `c570232a7371a53fd6dad954ec9d53f7940ecba171b3a2080fd995a6bd9a77d2`

The reference "it" unambiguously identifies the exact published v2 proposal presented in the immediately preceding response. Recomputed the contract and source hashes before recording approval. Approval changes this receipt only; the approved contract bytes remain unchanged, including their historical proposal wording. This approval does not itself invoke implementation or authorize additional tracker writes.

Approval is retained locally in this receipt. It has not been posted to the issue. A delivery started from the issue alone needs this receipt transferred explicitly or the human's approval recorded on the issue.

## Retention and validation

Saved and reread the full v2 contract. Retained the unpublished v1 bytes at [history/18656d2203d78d76d0740ab4dc1a69e50b3b5dbd365048ca3ba49185d1ca99fe/frozen-delivery-base.md](history/18656d2203d78d76d0740ab4dc1a69e50b3b5dbd365048ca3ba49185d1ca99fe/frozen-delivery-base.md).

Verified 21 unique requirement IDs, eight matrix columns, planned-only states, resolved outcome decision, exact imported issue body, final contract newline, source hash, and unchanged issue body before posting. Readback extracted the exact contract and decoded the source block; both matched local bytes and SHA-256 identities. Full comment bytes matched the submitted text.

Initial source fencing needed correction because the specification has no final newline. Updated only this invocation's proposal comment to encode that source as base64, then repeated readback successfully. Contract bytes and hash did not change.

These are planning-document and publication-integrity checks. No implementation, acceptance tests, review stage, or proof ran. Controller fixture transport is not evidence of live-host enforcement or agent judgment.

## Recovery

Restore the Markdown block from the comment to `work/frozen-delivery-base.md`, preserving its final newline. Decode the base64 block to `plans/frozen-delivery-under-moving-targets.md`; that source has no final newline. Verify the recorded hashes before reuse. Reconcile existing differing files instead of overwriting them. Read later issue amendments and exact-proposal approval before implementation.

Next steps:

1. `/deliver-issue https://github.com/grove/promise-to-proof/issues/37`; use this saved approval receipt at `.p2p/work/frozen-delivery-base/planning-handoff.md`. Transfer it with the contract and binding source if using another checkout; issue-only retrieval does not yet contain approval.
