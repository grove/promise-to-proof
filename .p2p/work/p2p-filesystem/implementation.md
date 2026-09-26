# Filesystem implementation

Status: IMPLEMENTED
Work item: work/p2p-filesystem.md
Contract revision: v1
Contract SHA-256: 32bb5c28ffaba76a789f0d25c51aab5c2fe3579cfd4274bb787169315891862e
Candidate: snapshot:sha256:19cbdc8dd558bce2402a046af22e82854cd995bf6a5bc0d03bd30702349e9aab
Comparison base: f3f94647da0cc6b4864667bd79cab3ab17f11ef3
Binding inputs: [{"path": "plans/p2p-filesystem-implementation-spec.md", "sha256": "fbb89a8e1e7a8157734cce9699c0ec52425b62127eececd555cb38ed5a51f163"}]

## Changes

Canonical work files, durable .p2p/work records, temporary-only ignores, local
slicing, and optional tracker imports/mirrors now share one protocol across all
17 skills. Each skill ships the same stdlib path/candidate helper. Updated
setup, review, proof, repair, publication, resume, and user documentation.
Kept the acceptance matrix and existing recoverable snapshot serialization.

## Validation

- R1-R2: Disposable Git repositories check trackability, conflicting ignore
  rules, strict paths, exclusive creation, symlinks, and collisions.
- R3: Manual local planning, implementation, independent review, and independent
  CLI proof completed without tracker access. Both reports match the retained
  snapshot and exact agreement. All 17 copied standalone skill packages run
  their helper without sibling installations.
- R4: Local parent/child fixture checks source and parent discovery, transitive
  hashes, children inventory, and invalid child paths. Slicing instructions
  were independently inspected for local defaults, contribution mappings, no
  extra specifications, and separate integrated parent proof.
- R5: Report replacement preserves history and rejects ignored archive paths.
  The live fixture resumed from a fresh clone after deletion of its original
  temporary repository. Its retained Git bundle was independently cloned and
  validated again, with review, proof, and evidence retrievable.
- R6: Evidence instructions require redaction before retention, safe durable
  references and checksums for unsuitable output, and unavailable-evidence
  reporting. Retained fixtures contain only synthetic inputs, code, contracts,
  and test observations. Secret classification remains a stage responsibility;
  the helper is not a general secret scanner or remote artifact service.
- R7-R8: Tests cover A-to-artifact-B identity, exact snapshot retention, changed
  product/work/parent/spec/base, untracked additions, deletion, symlink targets,
  executable modes, staged-content ambiguity, and malformed candidate records.
- R9: Both committed and snapshot candidates resume in fresh clones. A work path
  locates linked agreements and durable records. The fixture bundle retains
  comparison-base Git objects as well as candidate content and reports.
- R10: Helper code issues read-only Git commands only. Tests check the index
  remains unchanged through capture; fixture commits and clones are explicit
  validation operations. Skills retain separate external-effect authority.

Automated command: python3 -m unittest discover -s checks -p 'test_*.py' -v
Result: 4 tests passed, including the multi-case filesystem scenario and all
existing valid/invalid acceptance-bundle fixtures. See evidence/checks.log.
All local README/documentation link targets exist. git diff --check passed.

Independent review found staged-mode and ignored-history bugs, plus a reserved
history-path bypass. Using this repository's work item exposed fenced Markdown
examples incorrectly parsed as live links. All four were fixed and covered by
regression assertions before this candidate was captured.

## Retained evidence and limits

- evidence/local-delivery.bundle: complete disposable local workflow repository,
  including candidate snapshot, contracts, code, tests, stage reports, and proof.
- evidence/local-delivery.json: fixture identities, context names, bundle checksum,
  observed transfer result, and validation boundary.
- evidence/checks.log: latest automated check output. Prior output is retained
  under history/.

The live exercise used manually dispatched independent stage contexts. It does
not claim to validate the coordinator's host-enforced verifier sandbox, which
remains host-dependent. Tracker publication, PR creation, merge, and deployment
were not exercised or performed. Human scenario documents describe those checks.
The helper rejects unsupported submodules and mixed staged/unstaged content or
mode choices rather than silently dropping inputs.

This implementation report does not issue an acceptance or merge verdict.
The user authorized the final repository commit; pushing was not requested.
