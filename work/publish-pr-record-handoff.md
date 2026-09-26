# Acceptance contract: publication records and checkout handoff

Contract revision: v1
Source: [Shared acceptance contract protocol](../docs/acceptance-contract-protocol.md)
Source attribution: User conversation on 2026-09-26, retained verbatim below; related PR https://github.com/grove/promise-to-proof/pull/26
Parent: None
Prerequisites: None

Intended outcome: The publish-pr instructions explain how to publish the records needed to retrieve a verified handoff, handle later receipts, and safely reconcile leftover local copies. This is an instruction and scenario change, not an executable workflow controller.

Advisory learnings: None; no learning register exists in this checkout.

## Retained source request

The user asked:

> what do we do about the uncommited files in the project directory? these where created by you (and promise to proof). The PR description references them, so I think we should commit and push them. Maybe the publish-pr skill need to be updated to handle the p2p files properly?

The user answered "Yes—publish records, clean checkout, fix skill" to this question:

> The model, contract, and review/proof evidence are already in PR #25. Only the later publication records are local. I can publish those as a follow-up commit, then archive the matching local copies so your main checkout is clean. Should I also fix the publish-pr skill in a separate commit?

The user then requested:

> Can't add fix/publish-pr-record-handoff to the same PR, alternatively create a separate PR for it.

After the separate PR was created, the user requested:

> ok, do the next steps now.

The shared protocol supplies the existing authority, candidate identity, durable records, and preservation boundaries. The implementation files are inspection targets, not binding sources or independent oracles.

## Acceptance matrix

| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | Retained request: referenced files should be committed; shared protocol durable handoff | The publication instructions require the exact preview to include the paths and byte identities of reports, evidence, and recovery records needed to retrieve referenced handoffs, and explain that isolated publication leaves local copies and can produce later receipts. | A referenced handoff depends on omitted local-only bytes; later receipts are falsely described as already published; temporary files or secrets enter the preview. | publish-pr preview instructions | Retained source request and shared protocol's retrievable records and exact authority rules | Independent preview walkthrough with one report, its evidence, a recovery snapshot and a later receipt; record required inclusion and the local disposition explanation in proof. | planned |
| R2 | Retained request: understand untracked files and clean checkout | The handoff instructions classify issue-owned local files as identical published copies, differing files, or local-only records by comparing path, bytes, mode and symlink target against retrievable published content. | Untracked status alone is treated as missing publication; a mode or symlink difference is misclassified; the final report omits remaining records or their locations. | publish-pr handoff and report instructions | A disposable file inventory with independently chosen known equal and unequal cases | Independent instruction walkthrough and safe sandbox fixture containing equal bytes, changed bytes, executable mode and symlink differences, a local-only receipt and an unrelated file; retain observed classification. | planned |
| R3 | Retained approval: publish later records; shared protocol identity and authority | The instructions permit a separately authorized frozen records-only follow-up on an existing PR, with exact parent and content checks, unchanged complete product tree and original review/proof bytes, original candidate mapping, remote SHA readback, and unchanged PR title, body and ready/draft state. | Remote head differs from named parent; attempted product or report change; missing authority; force push; another receipt commit required just to record the previous receipt commit. Each conflict stops before push. Git ancestry and remote SHA finish the follow-up without a recursive receipt cycle. | publish-pr records-only follow-up instructions | Retained approval plus shared protocol exact authority and content-equivalence rules | Independent walkthrough of an authorized frozen receipt and separate head-drift, changed-report and product-addition cases; safe local Git fixture checks unchanged product/report content and ancestry. Preserve walkthrough results in proof. | planned |
| R4 | Retained approval: archive matching local copies; shared protocol preservation | The cleanup instructions require existing or specific cleanup authority, move only issue-owned untracked copies confirmed in a retrievable remote commit, preserve a local recovery copy, and report its location and final Git status. | Changed, local-only, unrelated or tracked files are removed; cleanup is inferred from publication alone; duplicate product files are staged on the target branch solely to make status clean. | publish-pr cleanup instructions | Retained request authorizes reversible cleanup of matching copies only | Independent walkthrough with and without cleanup authority; safe sandbox archive exercise verifies matching copies remain recoverable and changed/local-only/unrelated files remain untouched. | planned |
| R5 | Retained request: fix the skill; shared protocol concrete verification | The repository documents reproducible scenarios for leftover-copy reconciliation and frozen receipt publication, including the conflicting cases above, while retaining valid skill packaging and existing publication authority boundaries. | Scenarios claim execution results without runs; ready PR becomes draft; new instructions bypass original publication authority; frontmatter or standalone references become invalid. | publish-pr skill and checks/publish-pr-scenarios.md | R1–R4 and existing shared protocol publication rules | Independent static walkthrough of documented scenarios and unchanged boundaries; run the installed skill frontmatter validator, copy the skill with references dereferenced to scratch, and confirm readable matching protocol and YAML metadata. This validates packaging, not installed agent behavior. | planned |

## Unresolved gaps

- None for the instruction and scenario scope. Live agent and GitHub behavior remain outside this contract.

## Open questions

- None.

## Out of scope

- A runtime controller or a guarantee that every model follows the instructions.
- Live GitHub publication, cleanup of the operator's checkout, or installation behavior as acceptance evidence for this documentation change.
- Reimplementing publication, altering reviewed product content, merge approval, or changes to PR #25's model.

## Change notes

- v1: Initial canonical contract for the already requested skill fix. No prior contract or IDs existed. The retained request authorizes the scope; no material outcome decision remains open. Preservation and authority checks are necessary boundaries of publishing and cleanup, not added product features.

## Implementation handoff

Inspect the existing scoped skill and scenario changes against R1–R5. Make only corrections needed by this agreement through the enclosing authorized workflow. Preserve these IDs and capture the complete candidate for separate review and proof.

## Proof handoff

Evaluate every row against this revision and one fixed candidate. Record each independent walkthrough, safe sandbox observation and packaging result in the proof report. Distinguish instruction completeness from live agent compliance.
