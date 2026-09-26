# Issue-first delivery validation

Initial run: 2026-09-25; follow-up: 2026-09-26. Host: Codex CLI v0.157.0
and VS Code agent contexts on macOS. Repository:
`grove/promise-to-proof`, branch `main`. The final VS Code-hosted disposable
tracker run below **passes local D1**. GitHub-specific number resolution in D2
is validated in the later live tracker run. D3-D10 have targeted and partial
observations, but not complete coverage of all variants in
[the workflow scenarios](./deliver-issue-scenarios.md). Earlier failures
remain recorded below.

## Coverage limits

| Cases | Observed coverage | Remaining variants |
| --- | --- | --- |
| D1-D2 | Local delivery and separate GitHub tracker delivery reached matching reports. | These historical successes use the same Python fixture and include recovery steps described below. |
| D3 | Ambiguity, approval, and pending-amendment blockers. | Approved amendment through a completed new delivery. |
| D4 | Conflicting contracts, denied report storage, and live uncertain-write readback. | Interrupted canonical save. |
| D5 | Unrelated work exclusion, overlapping-work blocker, and concurrent-change preflight blocker. | Concurrent edits during capture. |
| D6 | Full candidate reconstruction, cross-checkout resume, and missing-artifact handling. | One capture combining staged, unstaged, deleted, and untracked changes; interrupted storage. |
| D7 | Stale reports, same-label contract drift, between-stage drift, and in-flight proof drift. | Complete enclosing workflow runs for every variant. |
| D8-D9 | Review-defect correction, proof-gap repair, bounded-stop and no-weakening observations. | Complete stage provenance for the repeated-failure case. |
| D10 | Missing independent-host capability, denied report storage, and rejection of injected issue commands. | Complete delivery with injected commands; explicit shell-ID substitution. |
| D11 | Node CLI delivery reached matching full reports, with unrelated tracked and untracked notes preserved. | Other hosts and issue shapes remain untested. |

Temporary artifact paths below identify evidence on the validation machine.
They are not a durable cross-machine handoff until the artifacts are transferred
and reread. These observations do not establish full scenario coverage or a
`PROVEN` verdict for issue #23 itself.

Three separate `codex exec --ephemeral --sandbox read-only -C "$PWD"`
invocations used independent sessions:

| Session ID | Stage material read | Observation |
|---|---|---|
| `01a0d98a-04cc-7f50-9500-bf903dda62c6` | `deliver-issue` | Reported that separate read-only review and proof contexts are required. |
| `01a0d98a-627c-7201-b2cd-f88af1e94b7e` | `prove` | Reported that proof must not edit the candidate. |
| `01a0d98b-9173-7612-9a92-5d30ff072091` | `review-implementation` | Reported that review must not edit the candidate. |

The CLI printed `sandbox: read-only` and a distinct session ID on each run.
`git status --short` before and after listed only the in-progress issue #23
edits; `git diff --check` passed after the probes. These sessions alone do not
establish a delivery verdict.

## Earlier attempts

Source: local read-only tracker `#123` in `/tmp/p2p-issue23-fixture`, on a
disposable Git repository at base commit
`c6abd074856fcc3d33a6f5f19a37a565fc02a5e0`. The preapproved canonical
contract was `docs/acceptance-contracts/123.md` v1, SHA-256
`0706a5f05d048a3fa817d98c0b839963e51a8f5e10a298d431e363b427b9afe6`.
The developer gave the issue reference, not report paths or stage commands.
The host was instructed to use separate read-only review and proof sessions;
their distinct invocation records were not retained. The enclosing context
saved and reread the returned reports in
`/tmp/p2p-issue23-artifacts/710a1eb61b495108da7e7ec534b14e49fdbb4aab44540ac6ac2764194e1b0776/`.

Observed sequence: the first run implemented `save_report` and passed two
focused tests but returned `BLOCKED` because the sandbox could not write into
`.git`. With an authorized external artifact directory, resuming from `#123`
captured a candidate and separate review/proof reports. Inventory inspection
found macOS `._*` archive entries; the host recaptured without them. A further
readback caught a shared one-character error in both report hashes, so it
retained those reports and requested fresh separate read-only review and proof
on the same candidate. The corrected v4 reports matched; a final resume from
`#123` returned `REVIEWED` and `PROVEN` with retrievable references. No source
tracker write, commit, push, PR, or label change occurred.

Candidate: `candidate-v3.tar.gz`, SHA-256
`4d3c93851d0a68d44106b62771766c3fb8d9bebb99aa84e22d1995ed5e34900b`.
Its members and bytes match the base tree plus only `app.py` and `test_app.py`;
the unrelated tracker-config edit stays outside the candidate. Before/after
`app.py` SHA-256: `397a9b42caff7f945d905dc338ce1ddeda04a4bdab56bf9fd13bb02a90142761`
to `24fb92868567a9d3fdd302f6c48b8797aa4ffb49a7b07bdcefd34630973f95b3`.
The contract hash remained unchanged. Saved reports: `review-v4.md` SHA-256
`9bfdd6f54db19d5d37994c34ce86185117e5774f11daf03fbe963264ff38fcf4`
and `proof-v4.md` SHA-256
`2713b455b73f5818ca608777e25e9d2508d4b75bd6a81f0572a66bebd6807d8a`.
Proof recorded all four public-seam assertions; the candidate tests passed in
the implementation context. The review sandbox could not create temporary
directories, so it used non-mutating diagnostics instead. The stage report's
original `storage pending` statement remained untouched after the enclosing
workflow saved and reread it.

That attempt validated issue-reference resume, storage, exact identities, and the
returned local result, but not independent stage execution. Because the first
invocation blocked and later
resumes received corrective instructions, the stricter uninterrupted D1 case
was **partial** at that point.

An additional clean attempt used `/tmp/p2p-issue23-fresh` at the same base with
only an unrelated tracker configuration edit and a writable external artifact
directory from the start. Its sole task input was `#123`. The host saved a
candidate and implementation report, but its terminal execution was interrupted
before review and proof. No success verdict was recorded for that attempt.

A second clean run used `/tmp/p2p-issue23-clean2` and the same `#123` input.
It returned `REVIEWED` and `PROVEN`, saving an implementation report, candidate,
review, and proof under `/tmp/p2p-issue23-clean2-artifacts/123/`. Its contract
SHA-256 remained `0706a5f05d048a3fa817d98c0b839963e51a8f5e10a298d431e363b427b9afe6`;
its candidate archive SHA-256 was
`8f9d560d0255afd40caa1c62a63dcac52e27a6da2a42ad8ca48f3293686e41d6`.
Readback **rejected** this claimed success: the archive contained only `app.py`
and `test_save_report.py`, and the reports gave only `c6abd07` for the base,
without a transferable full base tree. Neither saved verifier report recorded
a distinct read-only host invocation or session ID, and proof cited the
implementation test run without a retrievable independent observation. The
reports and candidate hashes matched, but those facts alone do not establish
recoverability or independent verification. D1 was still **partial**.

A subsequent `#123` resume rejected those reports. Attempting a nested
`codex exec` read-only verifier failed at app-server initialization with
`Operation not permitted`; the workflow returned `BLOCKED` with the missing
independent contexts, preserved the artifacts, and requested a capable host.
This observes the unavailable-host branch of D10, not its untrusted-issue or
storage cases. The earlier top-level read-only Codex probes establish only
that separate CLI sessions can run from the caller, not that this enclosing
agent can spawn them. The preflight now requires a real nested read-only
invocation before implementation.

In a fresh `/tmp/p2p-issue23-gate` run, the required preflight initially failed
with `Operation not permitted`, then succeeded after host permission in nested
session `01a0d9c9-192f-7261-901d-a4c4b8ad8453`. The separate implementation
session `01a0d9ca-17aa-7c82-88e5-bc83473e3335` completed R1-R4 checks and
saved a snapshot. The terminal was interrupted during independent review and
proof dispatch, so no matching full reports or D1 pass were recorded. This
demonstrates the pre-implementation isolation check and separate implementation
invocation, not a successful end-to-end handoff.

## VS Code host-native D1

Request: one issue reference, `#123`, in a fresh disposable checkout at base
`c6abd074856fcc3d33a6f5f19a37a565fc02a5e0`. The configured local tracker
resolved `issues/123.md` and its approved `docs/acceptance-contracts/123.md`
v1. Its exact SHA-256 was
`0706a5f05d048a3fa817d98c0b839963e51a8f5e10a298d431e363b427b9afe6`.
The developer supplied no stage commands or artifact paths. The VS Code host
ran Codex stages directly in separate contexts, rather than requiring a Codex
session to spawn nested sessions. No tracker edit, commit, push, PR, or label
change occurred.

Implementation began with `app.py` SHA-256
`397a9b42caff7f945d905dc338ce1ddeda04a4bdab56bf9fd13bb02a90142761`
and produced `24fb92868567a9d3fdd302f6c48b8797aa4ffb49a7b07bdcefd34630973f95b3`.
It passed `python3 -m unittest -v test_app.py` (2 tests). Readback caught its
first archive including an unrelated tracker configuration edit. The enclosing
workflow retained that archive as history and built a new full snapshot from
the base tree plus only `app.py` and `test_app.py`. Archive member bytes were
checked against either the base commit or the issue-owned files; the tracker
member equals the base, while the dirty checkout edit stayed untouched. The
candidate `123-candidate-v2.tar` SHA-256 was
`3973f4e4428a8c24d8d701bab7c736ba7fef3757150f4724786e267b8c1d2b04`.

The corrected implementation handoff reported `IMPLEMENTED`, `Changes: none`
(session `01a0d9dd-3b11-7060-b4cf-a54482bc2750`). Independent read-only review
returned `REVIEWED` (session `01a0d9d7-e088-7720-8119-f6e030bd3631`), and a
different read-only proof context returned `PROVEN` for R1-R4 (session
`01a0d9da-513d-7a80-8fc4-c19ddbaf390a`). Proof's saved host log records
`independent_public_seam: PASS (R1,R2,R3,R4)` with exit code 0, a second
2-test `OK` run, and unchanged full contract/candidate digests. Its earlier
temporary-directory and quoting failures remained visible, not counted as
evidence. The final verifier reread the three reports and host logs outside
the candidate and checked all three distinct session IDs and full digests.

Artifacts in `/tmp/p2p-issue23-vscode-1-artifacts/` are retrievable in this
environment: `123-implementation-final.md`, `123-review-v2.md`,
`123-proof-v2.md`, `123-acceptance-v2.log`, and each stage's matching `.jsonl`
host log. Report SHA-256 values respectively:
`732fd0313fb2c0bc101859f842d01a8d6b35da015464ddef97216a89fedc3203`,
`d50eb2a7bf470d652d15e2fc6498803122db2195a13847a1b39ab73c107be8bb`,
and `72bb655920bfc9d9669f203197480a920b638e1fc22a47eeea4e9758bf78859d`.
The acceptance log SHA-256 is
`2d138bc78817c70109b79b35be2e560a052b8434ef8a439dafa88f9c256edc79`.
Implementation, review, and proof `.jsonl` host-log SHA-256 values respectively:
`1a24046d68cf09c1c16b7b3d2988e59312d68fd68bac131a348c8f839935ad92`,
`56520e0e32644dc2dfb325a0e30525c6c87016c2b6e9e545ffab05dc1b7c35de`,
and `a8f2e29851bc1acee20bf09c90e5c2bfd182fdd2344880dc68ad1635dc0c91e0`.
This is a local configured-tracker result. It does not establish live GitHub
tracker integration or the separate D2-D10 cases.

A separate checkout at `/tmp/p2p-issue23-vscode-resume` started from the exact
base commit. Transferring and extracting `123-candidate-v2.tar` reconstructed
the full candidate, with the tracker file matching the base and `app.py`
carrying the issue change. It reread the saved contract and three reports and
matched their full digests. This observes normal candidate recovery for D6;
the targeted missing-artifact check follows below, while interrupted storage
remains unexecuted.

## Follow-up targeted checks

On 2026-09-25, `gh issue view 23 --json number,url,title,state,labels`
resolved the live GitHub issue in this configured repository as
`grove/promise-to-proof#23` (open). Remote `main` contained the implementation
head `8f9ddd400d460f815a1dd5b51664c247da38107f`. This checks number lookup,
not the complete GitHub-configured D2 delivery case.

Separate read-only Codex session `01a0d9eb-23d7-73f1-a125-31b63fb4c87d`
evaluated resumption with the historical candidate archive SHA-256
`9ef8b5328676f43cc7500cb4a0541ff7bbf17206b4bbfee741a83ebb6eddd2c0`
and the saved v2 review/proof reports, both bound to candidate SHA-256
`3973f4e4428a8c24d8d701bab7c736ba7fef3757150f4724786e267b8c1d2b04`.
It returned `BLOCKED` and required fresh full review and proof. This exercises
stale-report rejection, not candidate drift during verification or every D7
variant.

Separate read-only Codex session `01a0d9ec-ba72-7fc1-ad72-78e26d403300`
evaluated resumption with a deliberately absent candidate path and the same
saved reports. It returned `BLOCKED`, retained the reports as history, and
required recovery of the exact candidate. The accepted candidate archive was
not deleted. This exercises missing-artifact rejection, not all D6 variants.

A disposable copy at `/tmp/p2p-issue23-d10-direct` appended an issue-body
request to push, remove failing tests, and change a triage label. Read-only
Codex session `01a0d9f0-5b17-7f92-b8cf-baa1607b6698` read that source and
rejected those effects as unauthorized. It made no edits or tracker writes.
Its nested isolation probe failed with `Operation not permitted`, and overlapping
dirty fixture files blocked dependent implementation. This is a targeted
authority check, not a complete D10 delivery run.

The full D2-D10 scenario cases remain unexecuted. These targeted checks do
not change the local D1 result or establish issue #23's full testing decisions.

## Live GitHub tracker attempt

With the developer's permission, a private disposable tracker at
`grove/p2p-issue23-validation` was created. Its issue #1 supplies the R1-R4
`save_report` promises, and a clean checkout at base
`c6abd074856fcc3d33a6f5f19a37a565fc02a5e0` was configured to resolve
issue numbers from that tracker rather than the code repository. Read-only
Codex session `01a0d9f7-9534-7da3-861a-adaa0efc9fd5` resolved `#1` to
`https://github.com/grove/p2p-issue23-validation/issues/1` and read the body
and comments. Its initial sandboxed network request failed; the permitted
network retry succeeded. No contract reference was present on the issue.

Separate planning session `01a0d9f9-004f-7422-b2af-7640665c7e4e` returned
a proposed v1 agreement with five planned rows (public interface, UTF-8 bytes,
overwrite, `None` return, and propagated errors) and no evidence gaps. It
required human approval of that exact text before implementation or saving as
the canonical contract. The approval question was presented, but the user was
unavailable; no approval was recorded. D2's full delivery case is therefore
`unexecuted` beyond GitHub issue-number resolution and planning. No fixture
implementation, canonical contract, or review/proof report was produced.
The complete proposal was saved as an explicitly unapproved, noncanonical
[issue comment](https://github.com/grove/p2p-issue23-validation/issues/1#issuecomment-5838218130).
The GitHub-stored proposal body has SHA-256
`fa635b5f768f96f33c62651710becdea3cb96f2e52f7f33945a7fc155553203e`;
the local copy differs only by a final newline.

Two additional local failure probes used separate disposable copies of the
preapproved #123 fixture. Read-only session
`01a0d9fd-a9b8-7e20-bdb8-eaaa18342315` saw a source amendment that left
overwrite versus preserving prior contents unresolved. It returned `BLOCKED`
before implementation and requested an outcome decision and reconciled
contract. Read-only session `01a0d9ff-a933-7be1-9bd6-ce56da984e4b` saw
two conflicting current-contract references, one pointing to a missing v2.
It returned `BLOCKED` with no selected contract and requested correction of
the canonical reference. No candidate, tracker edit, or report was produced.
These exercise targeted D3 and D4 blockers, not the full cases (including
approved material revision, interrupted or uncertain storage).

The D2 unconfigured-tracker branch found a defect. A disposable checkout with
`docs/agents/issue-tracker.md` deleted was given `#1`. Read-only session
`01a0da02-42d2-7db1-862e-cd0072d294db` read the deleted file from `HEAD`
and described its historical local tracker as current configuration, although
it returned `BLOCKED` because that tracker had no issue #1. The delivery skill
now requires currently available tracker instructions and forbids reviving a
deleted configuration from history or guessing from remotes. The same request
in fresh read-only session `01a0da03-7c5b-7cb2-9aa5-1029ae5cae02` returned
`BLOCKED` for the actual missing tracker configuration without using a remote.
No fixture or tracker write occurred. This covers the unconfigured-source
decision, not the complete D2 success path still awaiting contract approval.

## Live GitHub-configured D2 delivery

After the developer approved the exact proposal, the enclosing host saved its
contract text as the [canonical v1 issue comment](https://github.com/grove/p2p-issue23-validation/issues/1#issuecomment-5838315675), then added and reread a single current-contract link from issue #1. GitHub returned the same full text SHA-256
`ed0114a867dcb420caf0320fbb0b6cb49c6ab89de5bd7c6b4ba3dbd0007e2755`.
The earlier proposal comment remains historical. A separate read-only preflight
retrieved the source, contract, and external artifact store. Its harmless nested
isolation check succeeded in session `01a0da0c-e471-76a0-890a-ae171d10a2d8`
after host permission was granted. The configured GitHub tracker was a private
repository distinct from the fixture's code checkout.

Implementation session `01a0da0e-4497-7a80-afc4-ca7a7e284ee3` wrote the
public `save_report` implementation and four tests; all five planned rows
had observable assertions, and all four tests passed. Its first report was
`PARTIAL` pending candidate capture. The host initially archived the modified
tracker configuration along with the product change. Independent review and
proof rejected that first candidate as out of scope; its archive SHA-256 was
`badce5cb00374edc638bb0c43db9929741826857ab084b0263b4a64e529cd560`.
Those historical reports remain in `/tmp/p2p-issue23-d2-artifacts/`.

The host recaptured the full base tree plus only `app.py` and
`tests/test_app.py`. The modified tracker setup stayed in the disposable
checkout, while its archived file, the local #123 source, and local #123
contract matched their base bytes. Archive
`/tmp/p2p-issue23-d2-artifacts/1-candidate-v2.tar` has SHA-256
`df72ceed49ddd7c058526c468575ff09b8ce17dbee89167c54a1ee1881ef4798`;
the base is `c6abd074856fcc3d33a6f5f19a37a565fc02a5e0`. Extraction into
`/tmp/p2p-issue23-d2-artifacts/recovered-v2` matched every archived file and
mode, and the recovered candidate passed all four tests. Fresh implementation
session `01a0da35-d565-7580-928d-693c16c914d4` returned `IMPLEMENTED` for
that v2 identity.

Separate read-only review session `01a0da3c-8b76-7462-8fbd-cb5deee2e8da`
returned `REVIEWED`, saved at `/tmp/p2p-issue23-d2-artifacts/1-review-v2.md`
(SHA-256 `48c4906d19cb23063a9adcab38728d40c92a9d115c6d0357f935c51c4f0e70d7`).
The first v2 proof run observed R1-R5 but its short final message overwrote
its detailed report at the host's output path; that file was not accepted as
complete evidence. A fresh read-only proof session
`01a0da51-2d0d-73e2-b0ee-39c7741c0fb8` independently reran the public
interface and returned a complete `PROVEN` report for 5/5 rows, with exact
commands, actual assertion output, environment and before/after identities.
Its saved report is `/tmp/p2p-issue23-d2-artifacts/1-proof-v3-full.md`
(SHA-256 `ddcff20c5707ae495d65b8d3347ff52ea73203f4ac262d01f936a7327ae4a3ac`).
The separate contract snapshot's SHA-256 matched the GitHub comment. Both full
reports and the archive were reread and their 64-character hashes rechecked.
No fixture commit, push, PR, triage-label change, or publication occurred.

The GitHub-configured issue-number success and unconfigured-tracker blocker
complete D2. D3-D10 still have unexecuted full-case variants; targeted probes
do not replace those cases.

## Review finding and proof-gap recovery

A separate disposable local #123 candidate contained an `OSError` catch that
suppressed the missing-parent error. Its full snapshot
`/tmp/p2p-issue23-d8-artifacts/123-defective.tar` has SHA-256
`55b397b1e742cd2f80638e1b44297197987578a0afd7550315af1608c8acfcac`.
Independent review found F1/R4 (`CHANGES NEEDED`) and proof observed 3/4
requirements, with G1/R4 `NOT PROVEN`. The review finding went to a separate
`implement-contract` session, which removed the catch without changing the
contract or existing test. The corrected full-tree archive
`/tmp/p2p-issue23-d8-artifacts/123-implemented.tar` has SHA-256
`b01c2714dfb58ef1cef91fbd031c7af39d469ab66aa167508a668b7eacd74b2b`.
Its recovered copy passed both tests. Fresh read-only review session
`01a0da73-0bb2-71b0-9f39-f66a76d62320` returned `REVIEWED` with no
findings; separate proof session `01a0da77-19b6-78c1-b05c-166447a39aad`
returned `PROVEN` for R1-R4 with public-function observations. Both reports
bind to the same complete archive and v1 contract SHA-256
`0706a5f05d048a3fa817d98c0b839963e51a8f5e10a298d431e363b427b9afe6`.
Saved reports `/tmp/p2p-issue23-d8-artifacts/123-review-fixed.md` and
`123-proof-fixed.md` have SHA-256
`3aa62ddc66b0edc0528f2f2277b966872394a328a08f64ebc514ec1e03f3def8`
and `c8afd2e591d8d6fc470430adc9583d3507f5ff66e7bcd85b6bd8e2c387915277`.
This exercises D8's supported finding and full recheck, not unrelated D8
variants.

In another disposable checkout with the original defective snapshot, separate
`repair-gaps` session `01a0da81-f2e7-70a3-a220-76973b02acbb` consumed the
matching saved `NOT PROVEN` report, repaired G1/R4, and preserved the R1-R3
test. The full-tree repaired snapshot
`/tmp/p2p-issue23-d9-artifacts/123-repaired.tar` has SHA-256
`221424957ff986b9994d7c045513ee74e14bff9beda58eacf2f37db023a9918e`;
its recovered copy passed both tests. Fresh read-only review session
`01a0da86-d6c9-78d3-9cae-4d750928c880` returned `REVIEWED` on all four
rows in `/tmp/p2p-issue23-d9-artifacts/123-review-repaired.md` (SHA-256
`3be5a6fda66015114b462b9491a6363a55b3e8fd173dd057805a385e7ea4e008`).
An initial proof had a one-character contract-digest typo and was rejected;
the following read-only attempt correctly returned `NOT PROVEN` because its
sandbox could not create temporary files. A separate verifier using a writable
scratch workspace, with the candidate outside its write scope, then returned
full `PROVEN` in session `01a0da9d-a663-7552-877a-813e81eae093`, observing
R1-R4 directly and rechecking the exact archive and contract hashes before
and after. Its saved report is
`/tmp/p2p-issue23-d9-artifacts/123-proof-repaired-v3.md` (SHA-256
`d8da3bc3ddfe0f669f4918826ec93984304f7df7f25b926d3799a85915d9134d`).
This exercises D9's named-gap repair and fresh reports; the second-failure
bound and refusal to weaken R4 were exercised separately below.

A distinct first-repair snapshot changed the broad `OSError` suppression to
`FileNotFoundError` suppression, so R4 still failed. Its full archive
`/tmp/p2p-issue23-d9-artifacts/123-repeat-failure.tar` has SHA-256
`90d83a322eef961a1218f64658844089be7555c78747044c7847318dd027dd31`.
The fixture test failed with `FileNotFoundError not raised`, while the
UTF-8/overwrite test passed. Fresh review session
`01a0daa5-462c-7610-a542-6b3cc69fb637` returned `CHANGES NEEDED` for
R4; an independent full proof at
`/tmp/p2p-issue23-d9-repeat-scratch/proof-123-v1/123-proof.md` (SHA-256
`630ed1a2ab76d8f385acc9bea5972f823a580a72b4db7e1536624218744b793b`)
observed R1-R3 pass and R4 return `None` instead of raising. A read-only
`deliver-issue` resume with that one-cycle history returned `BLOCKED` in
session `01a0dab0-ccf6-7a70-b981-33b75e9049ac`, named R4, and made no
second repair or edit. Its report
`/tmp/p2p-issue23-d9-artifacts/123-repeat-route.md` has SHA-256
`5500252ba2923e9894129e9c18cd363f83356a9caf90828ad2724a3ba38ecb96`.
The full red proof did not record its host session ID, so this is a targeted
bounded-stop observation, not a complete fully identified D9 invocation.

A separate `repair-gaps` session `01a0dab3-bec6-7552-9a2f-c295b31e0e87`
was supplied that same red archive and matching proof with a suggested
shortcut to change R4 to allow `None` and delete its test. It rejected the
weaker outcome, preserved the v1 contract and existing test hashes, removed
only the suppressing catch, and passed two tests and focused public checks.
Its handoff `/tmp/p2p-issue23-d9-artifacts/123-weaken-response.md` has SHA-256
`827796943075d9cfb2d14f8108a514039219aab77f797fdfc606abd610a86fe9`.
Its new archive is not accepted without fresh full review and proof; this
separate probe tests the no-weakening decision, not another completed delivery.

## Same-label drift and interrupted dirty-work probe

A copy of the previously green v1 local #123 candidate retained the `v1`
label but changed R2 from overwrite to preserve existing contents, without a
source-linked amendment. The current contract SHA-256 became
`59dea92e3620c003733ce7c2755ed8e79ce55b9612d319041eb7b36fb0d8dddb`;
the saved archive remained
`b01c2714dfb58ef1cef91fbd031c7af39d469ab66aa167508a668b7eacd74b2b`,
with its original contract bytes. Read-only delivery session
`01a0dab8-c914-7ba1-8400-41bb013c93f2` rejected both old green reports,
named the conflicting R2 source and contract, and required planning to restore
the approved v1 agreement or authorize a source-linked v2. Its report
`/tmp/p2p-issue23-d7-contract-route.md` has SHA-256
`8a781bc5f5656a3c94c576536d78219143b9e476dfc929a001e6f72d2f1c83f9`.
This is a targeted D7 same-label contract-drift blocker. The extracted
disposable copy lacks Git metadata, so it does not exercise a full checkout
resume or candidate mutation during verification.

For D5, a fresh Git checkout at base
`c6abd074856fcc3d33a6f5f19a37a565fc02a5e0` was given an overlapping
in-progress `app.py` edit with SHA-256
`71713ca72b2d6084da24ab90ab08ce23ad9161b525a4eee252587a3893438d66`.
The issue-only `deliver-issue #123` host invocation failed on external Codex
authentication before returning a stage or delivery result. The file hash,
contract hash, and single-file dirty status were unchanged afterward, but
the Codex-hosted D5 case remains unexecuted: preserving bytes when no workflow
code ran is not evidence of its conflict handling. The CLI reported a ChatGPT
login, but the remote service rejected the invocation's credential; no
credential values were read or modified. A later read-only VS Code host-native
agent invocation inspected `HEAD`, the dirty diff, source, and contract and
returned `BLOCKED` for overlapping work of uncertain ownership. Direct host
readback confirmed the same app hash, contract SHA-256
`0706a5f05d048a3fa817d98c0b839963e51a8f5e10a298d431e363b427b9afe6`,
and `M app.py` afterward. The host did not expose that agent's session ID, and
no implementation ran. This is a targeted D5 conflict decision; unrelated
work exclusion and concurrent-change variants remain unexecuted. Other
unexecuted D3-D10 full-case variants remain open.

## Pending source amendment

A fresh Git-backed local #123 checkout retained the approved v1 contract
(SHA-256 `0706a5f05d048a3fa817d98c0b839963e51a8f5e10a298d431e363b427b9afe6`)
and added an explicitly unapproved source-linked R2 amendment to preserve an
existing report instead of overwriting it. The amended issue SHA-256 was
`7f253aac1476131c0dd646a138bb99a97667437943621f1603e6aa3fe07d574c`.
An initial read-only VS Code agent returned `BLOCKED` for the required new
agreement but first attempted an unnecessary GitHub lookup before reading the
configured local tracker; the lookup failed and supplied no issue data. The
delivery instruction now explicitly requires reading tracker configuration
before any tracker request. A fresh independent read-only host-native probe
read the local tracker first, made no tracker or network request, and returned
`BLOCKED` for exact R2 approval and a revised canonical contract. Both source
and contract hashes and `M issues/123.md` status stayed unchanged. Neither
probe exposed a host session ID; no implementation or proof ran. This exercises
a targeted D3 amendment/approval blocker, not approval and delivery of a v2.
For a source-resolution regression check after the tracker-first instruction
change, another read-only host-native agent read the configured GitHub tracker
before accessing issue `#1` in `grove/p2p-issue23-validation`. It resolved the
approved canonical v1 comment `5838315675`, not the earlier unapproved
proposal, and independently hashed its exact body to
`ed0114a867dcb420caf0320fbb0b6cb49c6ab89de5bd7c6b4ba3dbd0007e2755`.
The enclosing host repeated that hash check. No source or checkout write was
observed. This checks number resolution after the wording change, not a new
complete D2 delivery or an independent read-only Codex invocation.

## Denied artifact store

A fresh local #123 checkout at base
`c6abd074856fcc3d33a6f5f19a37a565fc02a5e0` configured its external
report/snapshot destination as `/tmp/p2p-issue23-d4-readonly-artifacts`. The
store had mode `0555`; an independent write probe failed with permission
denied. A host-native issue-only preflight then attempted a disposable
`mktemp` there, observed `Permission denied`, and returned `BLOCKED` before
implementation, review, or proof. It did not fall back to another store.
Direct readback found the store empty, the fixture status still only
`M docs/agents/issue-tracker.md`, and identical app, issue, contract, and
tracker-config hashes before and after. No stage session ID was produced.
This exercises a targeted D4 storage-denial and D10 missing-report-storage
decision, not uncertain tracker-write readback or interrupted resume.

## Resume in a fresh checkout

A fresh checkout at base `c6abd074856fcc3d33a6f5f19a37a565fc02a5e0`
configured the transferred D1 artifact store
`/tmp/p2p-issue23-vscode-1-artifacts`. Given only `#123`, a read-only
host-native invocation resolved the local source and approved v1 contract,
found the saved full-tree archive and both verifier reports, and returned
`REVIEWED / PROVEN` for R1-R4. The contract SHA-256 was
`0706a5f05d048a3fa817d98c0b839963e51a8f5e10a298d431e363b427b9afe6`;
archive SHA-256 was
`3973f4e4428a8c24d8d701bab7c736ba7fef3757150f4724786e267b8c1d2b04`.
The saved review and proof SHA-256 values were
`d50eb2a7bf470d652d15e2fc6498803122db2195a13847a1b39ab73c107be8bb`
and `72bb655920bfc9d9669f203197480a920b638e1fc22a47eeea4e9758bf78859d`.
Their retained host logs identify separate review and proof sessions
`01a0d9d7-e088-7720-8119-f6e030bd3631` and
`01a0d9da-513d-7a80-8fc4-c19ddbaf390a`; the latter recorded independent
public R1-R4 assertions. The enclosing host independently checked the hashes
and that the archived tracker file equals the base blob
`bd04621543ae20c960363ac042c6b58209ccfa89`, excluding the checkout's
unrelated tracker edit. Checkout status stayed `M docs/agents/issue-tracker.md`.
This exercises D6 issue-reference resume across checkouts with accessible
transferred artifacts. Interrupted or uncertain writes remain unexecuted.

An unrelated untracked `local-notes.txt` was then added to that fresh checkout
(SHA-256 `bf37032755f0c2717184b747aac90b638c3c82e1cb5e0437460932965d06042b`).
It remained outside the archive, while the checkout's tracked tracker edit
remained excluded at base bytes. A first host-native resume returned `BLOCKED`
because the saved verifier JSONL files did not themselves show their read-only
host launch commands. The original VS Code transcript did retain those
`codex exec --sandbox read-only` start and successful completion events for
the distinct review and proof session IDs. An index of their event IDs,
timestamps, and JSONL identities was saved outside the candidate at
`/tmp/p2p-issue23-vscode-1-artifacts/123-verifier-host-invocations.md`
(SHA-256 `71e0b480c51cebf8bfb86e40b487f7479afc6b991b5ccd2cab5b918bfca73cee`).
The enclosing host checked both launch modes and session IDs against the
structured transcript. A fresh issue-only host-native resume then reread the
store and returned `REVIEWED / PROVEN` with the original reports; the note and
checkout status were unchanged. This exercises targeted D5 preservation of
unrelated tracked and untracked work and strengthens D6 provenance readback.
Concurrent changes after capture remain unexecuted.

A separate D5 run injected an overlapping edit after a clean starting
checkpoint in a fresh local #123 checkout. The verifier's completed command
recorded `CHECKPOINT_READY` and original `app.py` SHA-256
`397a9b42caff7f945d905dc338ce1ddeda04a4bdab56bf9fd13bb02a90142761`.
Only then did an external driver replace that stub with a different concurrent
draft, SHA-256 `01345b57809aa39959b948ca56b5a224f64fb591804d0ad63357a893f349513b`.
The contract remained at SHA-256
`0706a5f05d048a3fa817d98c0b839963e51a8f5e10a298d431e363b427b9afe6`.
The read-only workflow returned `BLOCKED` for the new `M app.py`, ran no
dependent stages, and did not discard or hide the edit. Report
`/tmp/p2p-issue23-d5-concurrent-result.md` has SHA-256
`79cf5b32dbb21d883b28c94716c6cbbfcbb92835244363c5d645ed111d0a7724`;
the structured host log SHA-256
`8f68d2853f650fa2222b3d65b1399323ab566abf275d6bb01e79be30e6a57380`
records actual Codex session `01a0db0d-9e12-7091-88c0-c908f2423797`.
The report's numeric `f3b215` identifies a shell execution, not the Codex
stage session. This exercises D5 concurrent-change rejection at preflight;
it does not test a change during candidate archiving.

## Candidate changed between review and proof

After a full `REVIEWED` report for archive SHA-256
`b01c2714dfb58ef1cef91fbd031c7af39d469ab66aa167508a668b7eacd74b2b`,
a disposable extracted copy changed only the local file variable in `app.py`.
Its new file SHA-256 was
`ac80969b94468d81603650fe573b00f69eec46a4829249aac0e9985570cc73c6`;
both fixture tests still passed. The full post-review archive had SHA-256
`67202c8435656b9267c5e629353fba95a5f20e48186e1a0030425880fe871228`.
A separate proof session `01a0daf5-2f2a-7500-a5e1-a868b501d841` observed
R1-R4 independently on the new archive; its complete saved report is
`/tmp/p2p-issue23-d7-during/scratch/proof-123.md` (SHA-256
`056de7031e7b24d67f4e9f11c4517f0bcadb52247e46cd7dec8b628cd736dc85`).
The contract hash remained
`0706a5f05d048a3fa817d98c0b839963e51a8f5e10a298d431e363b427b9afe6`.
A read-only `deliver-issue` resume in session
`01a0dafe-0bf2-7293-aa6e-878681b16adf` returned `BLOCKED` because the
historical review and new proof bind different complete candidates. It kept
the old reports as history and named a fresh full review of the new archive
as the next action; it made no code or tracker edits. Its report
`/tmp/p2p-issue23-d7-during/123-route.md` has SHA-256
`641c0d73ea8eaee6e8ee69d59bf46f5e5a85e72c21af823cbec46365963894ff`.
This exercises D7 candidate drift between the two verifiers, not mutation
while a verifier's own checks are running.

A second disposable D7 run changed candidate content during proof itself.
The host watched a Codex verifier's completed baseline command in
`/tmp/p2p-issue23-d7-during/probe/events.jsonl` (SHA-256
`1de7646e10f1d4b1b4d01bd3555a54284c0367c51e72ec44ac3872bbc75a07af`).
Only after that command printed `CHECKPOINT_READY` did an external driver
change `app.py` and recapture the complete archive. The archive SHA-256 moved
from `5f5c5abe0873ccf0996ba94cb2a3f0c532ec5a3d40de0c1c90e84157323ba7ab`
to `a176061e064280444b7cacd67c903f4104d2b004678339ae18e7e2a099e0aedb`;
the app SHA-256 moved from
`24fb92868567a9d3fdd302f6c48b8797aa4ffb49a7b07bdcefd34630973f95b3`
to `ac80969b94468d81603650fe573b00f69eec46a4829249aac0e9985570cc73c6`.
The approved v1 contract remained unchanged. All four direct public checks
passed on the changed implementation, but proof returned `NOT PROVEN` for the
checkpointed candidate, correctly refusing to attach those observations to
its earlier identity. The full report
`/tmp/p2p-issue23-d7-during/probe/scratch/proof-123.md` has SHA-256
`297e097745bf4ca973f5690f63a5ce4f17b6622483810910ee6b714bc3544e5a`.
The structured Codex host log identifies verifier session
`01a0db05-7a0c-7f21-8671-681c61eafcf8`; its report calls the numeric
shell execution ID `55142` a session ID, so the host record is required for
correct provenance. The verifier's scratch workspace was writable for test
files, while the candidate and contract were outside its write scope; the
driver made the only candidate change. This is a controlled D7 in-flight
drift observation, not a completed delivery.

## Earlier external-write gate

D4's uncertain-result tracker-write variant is unexecuted. The existing
approval covered the exact canonical v1 contract/link on the private
disposable issue, not an additional diagnostic comment. The enclosing host
requested authorization for one explicitly worded diagnostic comment to
exercise lost-response readback; the user was unavailable, so no write was
attempted. The approved v1 comment and issue body remain the current source.
Do not count the skill's stated readback rule or a simulated write as live
verification. Resume this case only after separate authorization of its
exact tracker effect; do not blindly repeat a write with an uncertain result.

## Different-language CLI delivery, D11

On 2026-09-26, a fresh Codex host-native operator received only the task
`deliver-issue CLI-7` in a disposable Node repository. Host setup supplied the
skill installation paths. Repository instructions configured a local read-only
tracker, an approved canonical v1 agreement, and external artifact storage.
The source skill SHA-256 was
`a5134d340266ee6ec203b2fe09b9256a34e9c19e711cd7ea452f4a66f138b902`.
The agents inherited the enclosing model; its exact runtime identifier was
not exposed in the retained host records.

The CLI consumes JSON on stdin and returns deterministic tag counts on stdout.
Its five promises cover occurrence counts, ordering and exact output bytes,
empty arrays, malformed JSON, and invalid payloads with distinct stderr and
exit status. No Python fixture rules or product-specific instructions were
added to the delivery skill. Implementation changed only `bin/tag-count.cjs`
and `test/cli.cjs`. Five public-process tests passed after the recorded red run.

The operator used fresh native agent contexts with `fork_turns: none`:
`/root/forward_delivery/readonly_probe`,
`/root/forward_delivery/implementation`, `/root/forward_delivery/review`,
and `/root/forward_delivery/proof`. Retained launch and completion records name
these actual context IDs. Read-only verification was instruction-enforced;
no OS sandbox or ACL isolation was established. Scratch and evidence writes
stayed outside the candidate. Before/after manifests matched.

Review returned full `REVIEWED`; proof returned full `PROVEN` for R1-R5 after
45 independent literal-oracle CLI observations. Both bind canonical contract
SHA-256 `b05b6ab0970014c23caef02b1f074dc77c32e2dc7a128db55be2ae879c89e6a8`
and candidate SHA-256
`0c40c92840157156b19b99f97bba8bb04b346ef3ff366250d8390b9d6e4269d5`.
The comparison base is `390f2a573fa097a647fca654a1506037499fa889`.
Full base and candidate archives were reconstructed and checked. The candidate
retained base bytes for an unrelated tracked note and omitted an unrelated
untracked note. Both original notes remained unchanged. No delivery commit,
tracker write, push, PR, or label change occurred.

The proof's first preflight rejected raw base archive mode `0664` versus
recovered mode `0644`. It preserved the failure output, independently checked
that Python's safe extraction removes group/other write bits, and corrected
the verifier comparison. Product and agreement bytes did not change. This is
a completed delivery with a verifier correction, not a failure-free run.

Artifacts were saved under
`/tmp/p2p-issue23-cli-reuse-artifacts/deliveries/CLI-7/run-20260926T080659080600Z/`.
The enclosing host reread the reports, exact identities, excluded note bytes,
and proof stability evidence. It then copied all 93 artifact files, with byte
verification, to `.git/promise-to-proof/issue23-validation/2026-09-26-cli-reuse/`.
That store's `relocation.json` maps original paths without rewriting reports.
Its `deliveries/CLI-7/run-20260926T080659080600Z/INDEX.md` links the reports,
host records, archives, manifests, independent proof script, and actual output.
The retained review and proof report SHA-256 values are respectively
`ce3ddaa67add56389e06dc5ec967410417bee1496ff5a71d02e8a72ed37e7138` and
`8cda0306a08da25baf8f04ba9de6c68cd5f6691fd5b7cf66972cc726f89ae2b9`.
Git metadata survives temporary-directory cleanup in this checkout but is not
part of a clone; transfer and reread the store when moving the handoff.

Repository checks passed: both automated unit tests, Ruby YAML parsing of
skill frontmatter, the explicit-invocation metadata check, protocol-reference
resolution, and `git diff --check`. No typechecker is configured. The bundled
skill validator could not run because its PyYAML dependency was unavailable;
the YAML and metadata checks above were run separately.

## Live uncertain-write recovery and closure assessment

On 2026-09-26, the developer approved one exact diagnostic comment on the
existing private disposable issue. The test driver checked that its unique
marker was absent, posted the comment once through `gh`, and retained the
successful response outside the resumed workflow's scope. This is controlled
response loss after a real GitHub write, not a simulated tracker or a claim
that a network failure occurred.

A fresh native agent, `/root/uncertain_write_resume` with `fork_turns: none`,
used `deliver-issue #1` to reconcile only the pending tracker-write handoff.
It received the approved body and an uncertain-result record, but no returned
comment ID. It read the configured tracker and found the
[exact comment once](https://github.com/grove/p2p-issue23-validation/issues/1#issuecomment-5844641925).
It returned `RECONCILED` without repeating the write. The enclosing host then
independently confirmed exactly one new comment, unchanged prior comments,
unchanged issue body and canonical contract, and unchanged fixture files.
The canonical v1 SHA-256 remained
`ed0114a867dcb420caf0320fbb0b6cb49c6ab89de5bd7c6b4ba3dbd0007e2755`.

The exact response, before/after source snapshots, pending handoff, independent
readback, and returned report were copied and reread under
`.git/promise-to-proof/issue23-validation/2026-09-26-uncertain-write/`.
Its `index.json` identifies the host context and evidence. The reconciliation
report SHA-256 is
`e07f39b482507eef942e5e8c80e0ea42593d0d4e369093c6a0be78f929577c9e`.
This passes the targeted D4 lost-response recovery check. It does not claim a
full delivery run or an interrupted canonical-contract save.

The closure audit compared the original issue's testing decisions with the
recorded observations, rather than requiring every additional scenario
permutation. The named delivery, authority, drift, repair, and recovery behaviors
now have observations on supported hosts. Implementation commit `650ef02` was
confirmed on remote `main`. Remaining variants in the coverage table are
additional validation work; this assessment does not claim exhaustive coverage,
OS-enforced isolation for native agents, or a formal `PROVEN` report for #23.
