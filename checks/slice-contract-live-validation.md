# Live slice-contract validation, 2026-09-22

This follow-up exercises real GitHub publication in the user-authorized private
[disposable repository](https://github.com/grove/slice-contract-live-validation).
It supplements the earlier [local and simulated validation](./slice-contract-validation.md).
GitHub persisted all reported issues, comments, labels, and native relationships.
The evaluator injected capability failures and lost responses in the client adapter;
these were not GitHub outages.

## Environment and scope

Baseline: `23ab711c45198b0b41bff8d3ca8f0353700aeaba`, plus the parent-index marker
and readiness-handoff edits under test. Host: macOS 26.6.2 arm64; Python 3.14.7;
GitHub CLI 2.101.0. Repository privacy and administrator access were read back.
Fresh delegated actor sessions received the skill, a parent or child URL, and
scoped authorization. They did not receive expected outcomes or prior actor
reports. The inherited model identifier was not independently exposed.

Actors used copied standalone skill folders with resolved protocol references.
This run did not repeat the installer evaluation. All tracker operations used a
logging adapter around the real `gh` executable. Native relationship mutations
used supported CLI flags; independent REST reads verified the saved directions.
See GitHub's [sub-issue API](https://docs.github.com/en/rest/issues/sub-issues) and
[dependency API](https://docs.github.com/en/rest/issues/issue-dependencies).

Local raw evidence: `/private/tmp/grove-slice-live.UTKCoq`. This directory holds
actor requests/reports, body files, command outputs, fault settings, snapshots,
and runnable fixture/check scripts. Transfer it to retain raw local evidence.
The linked private GitHub issues retain the source, contracts, plans, and comments.
No commits, pushes, closures, or deletions were performed.

| Input | SHA-256 |
|---|---|
| Slice skill | `282ec0a4a439c3e932f12e37999e2c2a6f556f0c52e1fc3691e886b5e8536a7f` |
| Publication reference | `e62cb429d50dd0d8cb8e947356ef8ce6e47ed9aaeb779cb090dacad317ac4dd1` |
| Acceptance skill | `76df953a48f998642acfdd1ea0d68cd18aebe2bf91b849fefe355d56bccf535e` |
| Shared protocol | `b16ed56bef714e6ac55dc2d37ddf4cd971f65f89df31568fb0c4204e804256c9` |
| Parent v1 text | `f54d91b7e4b1a49c40eabc0ef107086b37267db316224ce834d03df5b1f460b6` |

## Publication observations

The approved fixture divides retry-safe uploads into API and browser outcomes.
Both inherit persistence, original metadata, ownership, and restart obligations.
S2 requires the usable S1 API and owns mixed-channel integration work. Each parent
retains the full contract and approved coverage allocation. Initial children have
`needs-triage` and an unrelated `fixture-keep` label, without `ready-for-agent`.

| Scenario | Observed result | Live evidence |
|---|---|---|
| T11, native publication | PUBLISHED; two children, two native parent edges, and S2 blocked by S1 | [Parent #1 and index](https://github.com/grove/slice-contract-live-validation/issues/1#issuecomment-5774267708), children #7 and #9 |
| T12, optional textual fallback | PUBLISHED; parent/blocker references saved as text after the adapter rejected native writes; native edges remained absent | [Parent #3 and index](https://github.com/grove/slice-contract-live-validation/issues/3#issuecomment-5774266365), children #6 and #8 |
| T12/T15, required edges unavailable | PARTIAL; retained both children and index, with two parent links and one blocker link pending | [Parent #2 and index](https://github.com/grove/slice-contract-live-validation/issues/2#issuecomment-5774258583), children #4 and #5 |
| T15, index response lost | GitHub created the comment, adapter returned exit 124 without its URL, actor found the unique marker and updated that same comment | Same #2 index; `recovery-operations.jsonl` |
| T15, fresh resume | PUBLISHED; reused #4/#5, added only the three missing edges, and updated the same index | Same #2 index; `resume-operations.jsonl` |
| T15, child-create response lost | GitHub saved S1 #11, adapter returned exit 124 without the URL; a fresh actor recovered #11 by identity and created only S2 #12 | [Parent #10 and index](https://github.com/grove/slice-contract-live-validation/issues/10#issuecomment-5774362120); `lostcreate-operations.jsonl`, `lostresume-operations.jsonl` |
| T14, unchanged fresh-session rerun | PUBLISHED; same #7/#9 and index, zero writes; seven tracker reads plus CLI help | Same #1 index; `rerun-operations.jsonl` |

Independent `initial-publications.json` readback and `verify.py` confirmed the
reported edges, exact parent-body hashes, unique slice/index identities, labels,
and preserved human comments. No child contract or implementation readiness was
claimed by publication.

## Readiness-label lifecycle

A fresh acceptance-planning actor received only native child references #7 and #9.
The enclosing workflow was expressly authorized to save and reread contracts,
link them from their child bodies, and reconcile readiness labels. It preserved
qualified parent mappings and the exact parent snapshot in both agreements.

- [S1 contract v1](https://github.com/grove/slice-contract-live-validation/issues/7#issuecomment-5774394132)
  was saved and reread. With no work prerequisites and approved decisions, the
  workflow replaced `needs-triage` with `ready-for-agent` on #7.
- [S2 contract v1](https://github.com/grove/slice-contract-live-validation/issues/9#issuecomment-5774395870)
  was saved and reread. The workflow retained `needs-triage` on #9 because its
  usable API prerequisite was unavailable. Saving the agreement did not promote it.
- Independent `lifecycle-after-contracts.json` readback confirmed both states and
  preservation of `fixture-keep`. The actor's report and contract bodies are in
  `lifecycle/actor/`.

The evaluator then supplied a
[recoverable prerequisite artifact](https://github.com/grove/slice-contract-live-validation/issues/7#issuecomment-5774437642)
in an S1 comment. Its temporary Python/SQLite API preserved original IDs and metadata on retry,
rejected cross-owner retries and missing authentication, and retained records
through a real process restart with the same database. The comment contains the complete source,
runnable check, source digest, and observed restart result. This is a disposable
dependency fixture, not S1 implementation proof or parent acceptance.

A second fresh session retrieved S2 and its linked prerequisite, verified the
published source digest, inspected the check source, and exercised the live API.
It replaced `needs-triage` with `ready-for-agent` on #9. Contracts, source text,
`fixture-keep`, and the logical blocked-by relationship were unchanged. The same
session repeated reconciliation against unchanged state: checks passed again,
five tracker reads, zero writes. Evidence: `ready/actor/report.md`,
`ready/actor/rerun-report.md`, `ready-operations.jsonl`, and
`readyrerun-operations.jsonl`.

The invoking workflow performed the label transitions after contract storage and
prerequisite checks. Acceptance planning alone performed neither transition.
No issue closure or historical proof supplied prerequisite availability.

## Final independent verification

The final REST snapshot contains exactly four parents, eight children, and four
unique marked indices. All issues remain open. Native hierarchies and blocker
directions match the approved plans in the native and two recovery fixtures.
The textual-fallback fixture has no native edges and retains readable links.
Only native children #7 and #9 have `ready-for-agent`; every issue retains
`fixture-keep`. All four original parent bodies match their saved SHA-256 values.
Original parent notes, existing child text, and saved child contracts are intact.

Both the fresh publication rerun and the readiness rerun made zero writes. The
same canonical index identifiers survived recovery; successful children were
reused rather than recreated. Runnable checks and captured results are local:

```sh
python3 /private/tmp/grove-slice-live.UTKCoq/verify.py final-state
```

`verification-result.json` records the passing assertions and final ticket/index
map. `final-state.json` contains independent raw readback; adapter logs retain each
actual command, result and injected fault. The temporary API process was stopped
after evaluation. Its complete source remains in the linked prerequisite comment.
The private repository is retained for inspection.

## Fault-injection correction

The first adapter version accidentally consumed the issue-create response-loss
hook on `issue create --help`. The original recovery children therefore had
normal successful create responses. This is an evaluator defect, not evidence of
child-create recovery. The hook was corrected to exclude help, and a separate
#10 fixture exercised actual successful creation followed by a withheld response.
The unedited logs and `harness-correction.txt` preserve the distinction.

## Validation limits

These are sampled publication and readiness observations, not a full-suite pass.
The plans were already approved. This run does not evaluate decomposition quality
or prove the upload product. The local prerequisite exists only for the lifecycle
fixture and does not establish S1 or parent acceptance.

Client-injected failures do not establish GitHub outage behavior. There were no
concurrent publishers, genuinely unreadable remote state, or server-side timeout
experiments. Native capability and account permissions are established only for
this repository/account at this time. Actor isolation used instructions and
separate working directories, not filesystem enforcement.

Comments and issue lists were paginated, but no target was placed beyond a full
page. Legacy unmarked indices, conflicting duplicate markers, reordered/closed
existing slices, human edits to active children, and the lifecycle variant without
label-edit authority remain unexecuted. Existing parent notes and unrelated labels
were preserved. The migration scenario remains unexecuted. Full product delivery and proof were
not repeated; consult the earlier record for those observations.
