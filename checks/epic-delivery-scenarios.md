# Epic delivery scenario fixtures

These are evaluator instructions and expected observations, not execution
results. Keep this document, the fixture builder, and `oracle.json` out of the
actor's inputs. Execute the installed skills on real disposable Git repositories.
The `gh` substitute is a **controlled tracker simulation**; live-service behavior
remains unexecuted unless a separate run records it.

## Prepare and invoke a case

From the source repository, run:

```sh
python3 checks/epic_delivery_fixture.py self-check
python3 checks/epic_delivery_fixture.py prepare S3 /private/tmp/epic-S3
python3 checks/epic_delivery_fixture.py check-candidates /private/tmp/epic-S3
```

Use a new absolute output directory for each case or variant. The command refuses
to replace an existing fixture. It creates:

- `repo/`: contracts, executable registry behavior, exact Git objects, durable
  plans, candidate records, and a local bare `origin`.
- `installed/`: copies of the candidate's skill packages, resolving shared
  protocol and script symlinks. `oracle.json` records every installed file hash.
- `request.md`: the raw actor request and tool configuration, without the oracle.
- `bin/gh`: a persistent tracker CLI with JSON reads, writes, fault injection,
  and a complete `calls.jsonl` operation log outside the product candidate.
- `oracle.json`: evaluator-only input hashes, Git refs, candidate identity,
  expected destinations, original PR state, and installed instruction hashes.

Before actor launch, `check-candidates` invokes the installed filesystem helper
to validate both saved candidate records and their canonical binding-input order.
It retains actual commands and output in `candidate-validation.json`. S7
intentionally retains human edits outside a historical candidate; advanced or
conflicting integration tips intentionally differ from its saved comparison base.
Those differences are asserted and recorded separately from invalid metadata.

The copied packages support instruction invocations and the filesystem helper.
Run controller CLI checks from the complete source repository, whose
`checks/verify_acceptance_bundle.py` is required by that controller. Do not invoke
the controller from this flattened fixture package layout. The public CLI
receipt-transfer regression in `checks/test_p2p_delivery.py` uses the complete
layout and fresh processes with a zero dispatch budget.

Launch a fresh actor with only `request.md`, its named repository, and installed
skills. Require it to read the named `SKILL.md` and bundled references, use the
provided tracker CLI, and save reports and actual commands/output. The evaluator
retains the actor transcript separately. Do not put expected verdicts in the
request or accept the final response as evidence of saved state.

For a fresh-session transfer, copy `repo/` including `.git` and `.p2p/work/` to
another disposable location; delete `.p2p/tmp/` if present. Transfer the installed
skill package separately. Give the new actor only the child work path and tool
configuration. Retain the original and transferred file hashes.

After each invocation, inspect and assert actual effects:

```sh
python3 checks/epic_delivery_fixture.py inspect /private/tmp/epic-S3
python3 checks/epic_delivery_fixture.py verify /private/tmp/epic-S3 --expect no-effects
```

`inspect` reports observations without a pass claim. `verify` independently
asserts contract/source/human-note preservation and selected effect properties;
it does not establish the skill's full acceptance. Compare saved reports with
the source scenario requirements and exact candidate, base, and plan identities.
A blocked positive case is a gap, not a pass merely because no effects occurred.

The baseline fixtures supply implementation inputs, **not** invented review or
proof verdicts. Positive publication and retargeting require actual fresh review
and proof invocations before the publisher can proceed.

## Execute S1–S14 and their boundaries

The following observations are withheld from actors. Each `prepare` accepts
`--variant <name>` where specified. Other variations below are evaluator setup
steps, performed before capturing the actor's starting input inventory.

| Source case | Entry points and fixture | Independent observations |
|---|---|---|
| S1 | `prepare S1`; slicing plus unsliced `work/solo.md` delivery, publication preview, and readiness | Independent children resolve `trunk` without waiting for unrelated siblings. Unsliced work requires no parent plan. Obtain real solo review/proof for positive publication; absence of a PR is an ordinary readiness handoff. |
| S2 | `prepare S2`; slicing, each child delivery/publication, and parent publication | Child previews use `epic/example`. Remove one child obligation's behavior: grouping cannot make it complete. Withhold parent proof: no parent PR creation. Separately set unrelated required CI pending: proof/publication may proceed, readiness may not. |
| S3 | `prepare S3`; slicing then child delivery/publication | Capture resolves `trunk`; lookup and summary resolve `epic/example`. Saved reasons match acceptable intermediate outcomes. Approve a concrete proposal and save it; a subsequent pending proposal leaves that exact approved revision active. |
| S4 | `prepare S4`; fresh child-only implementation and delivery | Recover parent, approved v1, target, and history without repeated strategy questions. Repeat `--variant legacy` and retain legacy approval bytes through normalization. Transfer durable files before another fresh invocation; no scratch data or manual report paths. |
| S5 | `prepare S5 --variant missing`, `conflicting`, `proposed-only`, and `pending` | First three block dependent effects with a focused slicing handoff. Pending v2 leaves approved v1 applicable. Check refs, PR state, and preserved contracts as well as the report. |
| S6 | `prepare S6`; explicit `trunk` publication and actual PR readiness | Expected `epic/example` versus actual/explicit `trunk` appears in blockers. Neither stage edits the PR or silently substitutes a target. Required report gaps may also be reported; run actual verification first to isolate the destination gate. |
| S7 | `prepare S7`; slice a strategy change | Capture stays landed on `trunk`. Existing human notes, unstarted contracts, dependency links, local candidate, and PR17 survive. Preview names remaining children, old/new targets, stale reports, and pending actions. Save under exact strategy approval and repeat with separately covered ref/PR effects. Unknown tracker state remains unresolved. |
| S8 | `prepare S8`; strategy change, publication candidate inspection | `unfinished-sibling.txt` exists in the integrated candidate. Its recognizable payload must not reach `trunk` through retargeting. Return extraction to implementation; preserve integration history. Prepare a scoped child candidate in another disposable branch, run actual fresh review/proof against `trunk`, and then exercise retargeting. |
| S9 | `prepare S9`; preview, exact approval, injected faults, fresh resume | Preserve confirmed edits, reject changed preview inputs, reread after uncertainty, and produce no duplicate PR/ref effects. Use the phase procedure below. A base-only edit preserves the exact human body and marker. |
| S10 | `prepare S10`; review plus strategy-change handoff | Integration tip differs from recorded comparison base: require fresh review against the exact current tip. Run actual review/proof first, then change only the destination and save an approved plan revision. Unchanged proof remains tied to its original candidate; a repaired/rebased candidate needs full fresh review/proof. A changed promise returns to acceptance planning. Contract hashes stay unchanged for destination-only changes. |
| S11 | `prepare S11`; child verification, parent proof and publication/readiness | Every child function and its unchanged full check preserves the original name. Parent-owned `greet` passes an uppercased argument into capture, so the actual public workflow returns Welcome ADA for Ada. Assert the literal child outcomes independently, then run `verify --expect parent-fails`. Parent remains unproven and unpublished despite complete children; inspect the failed parent assertion and actual proof report. |
| S12 | `prepare S12`; full parent review/proof and completion | Candidate is on `trunk`, all contributions exist, and `verify --expect parent-passes` passes. Parent review/proof must cover all requirements on that exact candidate. No empty parent PR is created. |
| S13 | `prepare S13 --variant missing`, `conflicting`, and `advanced`; delivery/direct implementation/review | Missing names exact approved starting SHA and local/remote setup without effects. Conflicting branch has unrelated ancestry and is not reused/overwritten. Advanced branch requires exact-base refresh. Repeat matching branch and exact authorized setup with ref readback, incomplete child, missing actual prerequisite, and explicitly approved shared candidate. |
| S14 | `prepare S14` then `--variant present`; slicing and implementation | The existing flag permits independent delivery to custom default `trunk`. Closed issue 101 does not satisfy capture while executable behavior raises. Supplying the actual behavior changes the prerequisite handoff. An ambiguous acceptable intermediate outcome triggers a focused product question; hierarchy and release date never substitute for the answer. |

Some cases need several skill invocations. Preserve each phase and state snapshot,
including blockers. Do not claim an entire S ID was executed from a single
baseline invocation when its listed variants remain outstanding.

## Obtain genuine verification before retargeting

Prepare a new S9 fixture from the frozen candidate. Give separate fresh actors
these requests with the fixture's normal tool configuration:

```text
/review-implementation work/lookup.md
/prove work/lookup.md
/publish-pr work/lookup.md; inspect existing PR 17 and prepare the retargeting preview to its approved destination; local reports only
```

The reviewer and proof actor inspect actual code and save their own complete
reports. The publisher must discover those reports through the work path.
If verification or identity is insufficient, retain the blocker and repair the
fixture or candidate through the owning workflow; never fabricate a verdict.

Inspect the concrete publication preview. Give a follow-up that quotes its exact
candidate, comparison base, contract hashes, plan revision/hash, PR URL, old/new
target, current PR head/title/body/draft state, and preview identity. Authorize
only that PR's base edit. Strategy approval is not this effect grant. Preserve
the approval text in the evidence.

After authorized execution:

```sh
python3 checks/epic_delivery_fixture.py verify /private/tmp/epic-S9 --expect retarget
```

This asserts exactly one PR17 base-only edit to `epic/example`, unchanged human
text, no duplicate PR, and successful subsequent target readback. Invoke readiness
before and after the edit; its state follows the actual target plus all other
gates. Readiness may write its own approved managed report; compare that separately
from the narrower retarget assertion.

## Inject faults and concurrent changes

Only the evaluator edits `tracker.json`. Actors see state through `gh`. Arm a
lost edit response after the exact preview and approval but before application:

```python
import json
from pathlib import Path
p = Path('/private/tmp/epic-S9/tracker.json')
s = json.loads(p.read_text())
s['lose_next_edit_response'] = True
p.write_text(json.dumps(s, indent=2) + '\n')
```

The next edit persists but exits 1. Save its log, then restart with a fresh actor
and the same durable authority. It must read current state before retrying. A
successful readback of the target makes another edit unnecessary. The effect
assertion still expects exactly one edit.

Schedule a concurrent change at a specific subsequent tracker call:

```python
s['inject'] = {
    'on_call': s['calls'] + 1,
    'pr': 17,
    'pr_changes': {'body': 'Concurrent human edit: preserve this text.'},
}
p.write_text(json.dumps(s, indent=2) + '\n')
```

Use a new fixture to test each race. For a concurrent plan change, append a
material field or row change **inside** the approved section after preview
approval; record before/after section hashes. A proposed-only section is the
negative control and does not change the active plan identity. Reinvoke the
publisher with the stale approval, then inspect zero unauthorized edits.
For a change during application, arm `after_edit` instead of guessing a call
number. It runs once after the next PR edit has persisted, before its response:

```python
s['after_edit'] = {'plan_text': revised_approved_plan_text}
p.write_text(json.dumps(s, indent=2) + '\n')
```

Prepare the exact approved replacement and its authority in advance. Retain the
old plan through the history rule before arming replacement. `plan_text` replaces
the whole file; `plan_append` and `pr_changes` are also supported. Inspect the
event's `after_persisted_edit` phase, actual effect, and changed section bytes.
Retain confirmed effects and outstanding actions; a before-edit race is a
different boundary and cannot establish this one.

For interruption after a confirmed effect, stop the actor after the edit log
appears and before its final report. Transfer durable records and restart a
fresh actor with retained approval. Compare logs across both invocations, not
just the second. Do not repeat a successful effect to make a run look complete.

## Retain evidence

Keep the fixture directory or a recoverable archive, actor request/transcript,
installed hashes, exact skill outputs, before/after plan bytes, candidate/contract
identities, refs, tracker state and complete operation log. Save the evaluator's
commands and assertions with actual output under the work item's evidence directory.
Record the model/host identifier if exposed; otherwise state that it was unavailable.
Record simulated tracker validation and unexecuted live-service checks separately.
