# Retrieve issue #28 delivery records

The reviewed product is the exact snapshot in candidate.json. The current review.md,
proof.md and implementation.md are unchanged stage reports. The publication commit
adds records under .p2p/ without rebinding those reports to its new Git commit ID.

## Evidence locations

The directly committed reports, host records and selected summaries are convenient
copies. publication-evidence.tar.gz contains the complete pre-publication artifact
tree, including historical reports, both live-delivery runs, nested test Git stores,
base bundles, the project configuration probe, and raw host receipts.
publication-evidence-index.json lists every archive member with its byte digest,
mode, or symlink target, plus the archive SHA-256. Every member was reread and
compared with its original bytes or target during preview preparation.

Member paths are relative to .p2p/work/single-work-item-delivery/. A reference to
evidence/live-delivery-final/summary.json therefore names that archive member.
The original prefix /Users/grove/projects/promise-to-proof maps to the new checkout
for product paths, and to this artifact directory for retained .p2p references.
The old protected candidate prefix /Users/Shared/p2p-issue-28-fixed-8lm678wl/candidate
maps to the full product manifest in candidate.json. Reports' abbreviated
candidate/.p2p/work/single-work-item-delivery/candidate.json refers to that same
canonical retained manifest. snapshots/base-manifest.json retains the full review
base product tree, and the publication commit's parent retains its Git objects.

## Inspect safely

Read individual regular-file members with Python's tarfile.extractfile without
executing archived scripts or following symlinks. The archive deliberately keeps
absolute symlinks used by permission-denial probes as historical metadata. Do not
follow those links on another machine or extract them over a working checkout.
Nested .git files also retain original absolute gitdir pointers. They describe the
observed run; do not rewrite them as if they were new execution evidence.

To reconstruct a tiny candidate elsewhere, use its retained base.bundle in a new
disposable Git repository, then materialize its candidate.json file contents,
executable modes, deletions and symlink targets. The source_manifest and base
manifest retained beside it allow independent source/base comparisons. Recompute
the snapshot digest over the canonical manifest, and compare actual restored files.
Keep original receipts and manifests unchanged. Recorded controller invocations
contain original absolute paths; inspecting their evidence is portable, but a
new-path live controller resume is not promised by these historical records.

## Publication boundary

The exact new commit inputs are listed in publication-inputs.json, with that
manifest's own digest bound by the local publication.md preview. Earlier .p2p
records already present in the approved parent remain unchanged. The preview and
later snapshot-to-commit mapping, remote ref readback, PR readback and checkout
reconciliation are local-only publication receipts unless separately authorized.
Isolated publication leaves the operator's current copies and Git index in place.

The product is stdlib-only and has no build, dependency-resolution, generated,
signing, or timestamp-derived product artifacts. Controller Git reads address
supplied delivery repositories; tests create their own disposable repositories.
The live runner's outer product identity excludes .p2p/. Thus adding these records
and commit metadata preserves the report-bound product snapshot; the explicit
comparison base and archived tiny Git inputs remain unchanged.
