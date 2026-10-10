---
name: publish-pr-review
description: Publish the existing exact saved implementation review on its matching PR, with a read-only preview, explicit authority, and GitHub readback. Never perform another code review.
disable-model-invocation: true
---

# Publish a saved PR review

This is an optional expert entry point and the internal publication handoff used by
`/publish-pr` after the requested, authorized draft PR is confirmed. It reuses
`review.md` and the controller's original stage receipt. It does not run
`review-implementation`, change a verdict, prove, approve or merge anything.

## Preparation (no effects)

1. Read [the acceptance protocol](references/acceptance-contract-protocol.md)
   and `/publish-pr`'s required review/proof, immutable comparison-base,
   publication commit and candidate-to-commit equivalence rules.
2. Work from the repository that owns the canonical contract. Require a saved,
   current review with exact scope and contract/source binding, the correct
   published PR marker and same-repository current PR head. If a changed
   candidate or head has uncovered product files, or a mismatch cannot be
   resolved, block rather than pretending that a prior review is current.
   Confirm the publication commit mapping is retained if the original review
   covered a snapshot rather than this Git commit.
3. Prepare one exact review using the deterministic renderer:

   ```bash
   python3 <skill-dir>/scripts/publish_pr_review.py \
     --repo <root> --contract .p2p/work/<slug>/contract.md \
     --pr https://github.com/OWNER/REPO/pull/NUMBER \
     --head-repo <isolated-current-head-checkout> \
     --preview-out <retained-ignored-preview.json>
   ```

   It reads the **saved** independent review and original controller receipt;
   no model review is run. Show the concrete preview, effect type and digest
   before asking for any missing authority. Keep this preview under ignored
   `.p2p/work/<slug>/` to retain state across interruptions.

## Publication and readback

A clean `REVIEWED` verdict publishes **COMMENT**, not GitHub `APPROVE`.
Material `CHANGES NEEDED` findings require a separately granted
`pr-review-request-changes` effect (never infer it from a PR-create grant).
Do not publish a `BLOCKED` review. Leave inline comments out unless the
original saved finding identifies a line that still exists at the exact PR
head; a top-level review covers the normal case.

Use the existing controller's `authorize-effect` against this exact
preview SHA-256, with `--action pr-review-comment` (or
`pr-review-request-changes`), exact repository and PR URL. Alternatively
the human must expressly approve the complete exact preview and effect.
Approval of PR creation alone is not authority to submit a review.
Save the authorization result and reread it.

After authorizing, run with `--publish-preview <retained-ignored-preview.json>
--authorization <saved-authorization.json>` or an exact `--approved-sha256`
and retrievable `--approval-source` human approval. The script compares
the saved review, contract, source, PR metadata and current head again,
reads all existing reviews, and reconciles a matching prior effect first.
After any uncertain write, it reads all reviews again. Never repeat an
uncertain submission without first reconciling it by exact marker and body.
An unchanged retry reuses the same review; a new reviewed candidate has
a distinct identity and may receive a distinct separately authorized review.

Return the verified review URL, effect type, the saved review/proof status,
and the still-unassessed merge readiness. No publication action changes the
source issue, candidate, proof or human GitHub reviews. For read-only
reconciliation use `--status-preview <retained-ignored-preview.json>`.
If GitHub is unavailable or identities differ, preserve the preview and
report `PARTIAL` or `BLOCKED`; never claim that review was published.
