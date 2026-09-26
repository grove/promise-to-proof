# Delivery experience records

## Implementation proposal for Promise to Proof

**Status:** Proposed specification, version 1.0. Not an approved acceptance contract, an implementation, or a proof result.  
**Prepared:** 27 September 2026.  
**Suggested repository destination:** `specs/delivery-experience.md`.  
**Repository baseline inspected:** `grove/promise-to-proof` at `5e369c1b45ba817b8add6b20a9b7b1c97898fa12`.  
**First delivery:** Record significant experience during delivery and make it recoverable and readable.  
**Not part of this delivery:** Automatic learning, automatic changes to P2P, or a new acceptance decision.

> Record what happened, what we tried, and what happened next. Preserve the evidence and uncertainty. Decide what to change in P2P separately.

## 1. Outcome

Given only a work-item path, a developer or a fresh agent session can recover the significant discoveries, unsuccessful approaches, repairs, and remaining unknowns from delivering that work. They can follow a finding through an intervention to its subsequent evaluation, without reconstructing the story from chat or confusing historical results with the current candidate's acceptance.

The feature works before acceptance and for blocked or abandoned work. An ordinary delivery with no noteworthy discoveries remains an ordinary delivery: the feature must not manufacture lessons or demand a retrospective.

This specification uses **must** for required behavior, **should** for a preference with a documented reason for departure, and **may** for an optional implementation choice.

## 2. The motivating example

The user supplied a screenshot describing this sequence:

| Working version | Reported experience | What must be preserved |
|---|---|---|
| V1 | A review marked `REVIEWED` could contain contradictory prose saying `CHANGES NEEDED`. A placeholder observation such as `x` also passed structural checks. | The observed boundary problem, the source report or reproduction, and the distinction between structural checks and meaningful judgment. |
| V2 | Agent-written review summaries were removed in favor of rendering structured fields. The suite passed, but independent review found that `PROVEN` could still be accepted as a review status. | The attempted fix, its reported test result, the later counterexample, and their relationship. |
| V3 | The allowed review statuses were restricted and a regression test was added. Full tests and fresh review/proof were still pending. | The new candidate, the intended fix, and the fact that its full verification was not yet established. |

This screenshot is an attributed account, not independently replayed execution evidence. The referenced local V3 snapshot was not retrieved for this specification. Do not infer that it has since passed verification.

V1–V3 are labels in that account, not necessarily contract revisions or controller invocation IDs. Production records must use the actual identities.

The feature must preserve this kind of story. It must **not** conclude that the fix worked merely because it was written, or turn the possible lesson “validate allowed status values” into a binding project rule.

## 3. Existing behavior and compatibility

The inspected controller already retains an invocation, attempt reservations, host receipts, returned reports, candidate identity, and recovery state. Its implementation includes `Delivery.reserve`, `receipt`, `dispatch`, `stage`, `capture`, `complete`, and `run`; the CLI exposes `run`, `resume`, and read-only `status`. Reuse those boundaries rather than introducing a second workflow engine. [S1, S2]

The filesystem helper provides safe repository paths, canonical serialization, SHA-256 digests, atomic replacement, and preservation of previous records. The protocol excludes `.p2p/` from candidate identity and requires exact, recoverable evidence rather than a mutable filename alone. [S3, S4]

The following boundaries remain unchanged:

- Full completion still requires matching independent review and proof for the exact agreement and candidate. Experience never substitutes for either.
- One controller invocation still allows at most one automatic repair/recheck cycle. Experience grouping never resets that allowance or authorizes another invocation.
- `/retrospect` retains its requirement for a matching full `PROVEN` result. Pre-acceptance experience is a different artifact, not a relaxation of that requirement.
- Saving local records does not authorize commits, pushes, tracker updates, publication, or changes to project rules. [S4, S5, S6]

The current controller uses a closed report schema. Therefore v1 experience notes use a **separate sidecar**, not an additional required field in review/proof reports. Do not replace or undo separately developed stage-specific report schemas while adding this feature. [S1]

## 4. Scope and deliberate exclusions

### In scope

Capture a small set of controller-observed milestones automatically; accept significant notes from a worker or an authorized enclosing session; preserve links among findings, interventions, and evaluations; retain incomplete and historical records; render a deterministic timeline; and export the same records as JSON Lines for later analysis.

The first supported automatic producer is the existing controller on its supported host. The same storage helper must also accept records from skill-led delivery and explicitly supplied historical material. This prevents the feature from depending on every real delivery having used the CLI controller.

### Out of scope

No database, remote telemetry service, dashboard, vector search, cross-project aggregation, new host adapter, automatic policy selection, extra model call, automatic causal inference, or numerical learning score. No automatic promotion into `docs/retrospective-learnings.md`, changes to `SKILL.md`, or new `/analyze-experience` skill.

This feature does not repair the review-status bug in the example, redesign report validation, or create a way to bypass current recovery blockers.

## 5. User experience

For a newly admitted controller invocation with existing local-write authority, experience capture is enabled without another question. Workers can emit notes during their existing stage execution. At normal completion, a blocker, or a handled interruption, the controller imports available notes and refreshes the saved timeline.

The delivery result includes an additional observational `experience` object:

```json
{
  "experience": {
    "capture_status": "available",
    "records_path": ".p2p/work/example/experience/records",
    "summary_path": ".p2p/work/example/experience/summary.md",
    "warnings": []
  }
}
```

`capture_status` is one of `available`, `partial`, or `unavailable`. **Available does not mean every thought or every exploration was captured.** It means the configured capture operations succeeded through the reported checkpoint. Legacy or unrecoverably missing capture is `partial`; no usable experience record is `unavailable`.

When the view cannot be saved, `summary_path` is null and a warning explains why. Do not advertise a stale summary as current. Ordinary delivery status and exit-code semantics remain unchanged.

A developer can ask to view experience with only `work/<slug>.md`. Viewing does not launch workers, resume delivery, modify reports, or make new findings. Explicitly abandoning work can be recorded as a human decision; inactivity or a `BLOCKED` result must not be interpreted as abandonment.

## 6. Storage and ownership

Use the existing work-item directory:

```text
.p2p/work/<slug>/
├── delivery.json                     # Existing delivery authority
├── candidate.json                    # Existing current candidate record
├── attempts/                         # Existing receipts and reports
├── evidence/                         # Existing retained evidence
└── experience/
    ├── records/
    │   └── <event-id>.json            # Canonical immutable experience records
    ├── evidence/
    │   └── <sha256>.txt              # Only small additional safe evidence, when needed
    ├── events.jsonl                  # Derived machine-readable view
    └── summary.md                    # Derived human-readable view
```

The canonical record is one file per event. `events.jsonl` is a view, not a second writable ledger. This implements a logically append-only history without relying on crash-safe in-place appends to one large file.

An event may contain a worker's claim, but only the controller or authorized enclosing workflow writes the canonical experience directory. Workers do not gain write access to it.

Reuse existing snapshots and reports; do not archive entire scratch directories or duplicate candidates. Save derived views at delivery checkpoints or on explicit request, not after every shell command. Use the existing retention rules for replaced views; do not introduce a general exception to report history. [S3, S4]

A work-item path groups the history. `invocation_id` and `attempt_id` distinguish actual executions inside it. There is no new episode state machine, mutable `accepted` flag, or automatic invocation-creation API.

## 7. Canonical record format

Use schema identifier `promise-to-proof/experience-record/v1`. UTF-8 JSON is required. Canonical hashing uses the existing `p2p_filesystem.canonical` serialization.

### 7.1 Common fields

| Field | Required meaning |
|---|---|
| `schema` | Exact schema identifier above. |
| `event_id` | `exp-` followed by a full SHA-256 digest, derived from the source identity below. |
| `sequence` | Positive integer allocated under the work-item lock. It orders durable recording, not necessarily real-world execution. |
| `recorded_at` | Recorder's UTC timestamp, preserved on retry. |
| `observed_at` | Source timestamp in UTC, or null when unavailable. Never invent an earlier timestamp during backfill. |
| `work_item` | Canonical repository-relative `work/<slug>.md` path. |
| `invocation_id` | Existing controller ID, actual enclosing-workflow ID, or null. Do not manufacture a controller invocation for historical notes. |
| `attempt_id` | Actual stage attempt ID, or null. |
| `stage` | One of `preflight`, `planning`, `implementation`, `review`, `proof`, `repair`, `delivery`. |
| `origin` | Object containing `producer`, `producer_id`, `source_key`, and `local_order` (a positive integer for a note; null for a controller milestone). |
| `kind` | One of the event kinds in section 7.2. |
| `identity` | Exact candidate/contract context described below. |
| `requirement_ids` | Array of requirement IDs within that exact contract; empty when not applicable or unknown. |
| `statement` | Concise observation or attributed explanation; 1–2,000 Unicode characters after rejecting blank-only input. |
| `data` | Kind-specific object, with the fields defined in section 7.2. |
| `evidence` | Array of references defined in section 8. |
| `links` | Array of `{relation, event_id}` references to earlier retained events. |

`origin.producer` is `controller`, `worker`, `human`, or `backfill`. A human name supplied by an agent is attribution, not authenticated authorization. `producer_id` identifies the actual source session or an explicitly labeled historical import. `source_key` is a stable per-producer key, not a random value regenerated on retry.

For imported notes, use `source_key = note/<local_id>` within the original producer/attempt identity. Each attempt must have a distinct `producer_id`; an enclosing-session batch uses a stable, explicitly supplied import identity. Changing the note order is a conflicting resubmission, not a new note.

Compute the event ID as:

```text
exp- + sha256(canonical({work_item, producer_id, source_key}))
```

Identity is an object with exactly these fields:

```text
candidate_key:       full git:<SHA> or snapshot:sha256:<digest>, or null
contract_revision:   exact revision label, or null
contract_sha256:     full digest of exact contract bytes, or null
comparison_base:    full Git commit SHA, or null
binding_inputs:     [{path, sha256}], copied from known candidate context, or null
```

Unknown is null; an empty `binding_inputs` array means the known binding set is empty. Null identity must carry an unavailable-evidence explanation. A digest identifies bytes but does not establish that they can be recovered. `p2p_revision` identifies the executed P2P code or its content digest when known; do not substitute the target application's Git HEAD for the P2P version. Existing installed-skill hashes and host configuration remain available through referenced invocation records.

The recorder assigns context from retained controller inputs, not worker-supplied identity fields. For skill-led and historical imports, the enclosing workflow supplies context with evidence references; unconfirmed context remains unknown. Validate requirement IDs against the retained contract when available, not the current contract with the same revision label.

### 7.2 Event kinds and `data`

All listed fields in each `data` object are present; nullable values use JSON null. Reject unknown fields in v1 rather than silently interpreting them.

| Kind | Required `data` fields | Meaning |
|---|---|---|
| `invocation_started` | `capture_mode`: `live` or `backfill`; `p2p_revision`: string or null; `worker_notes`: `outbox-v1` or `unavailable` | A real admitted invocation became observable. |
| `attempt_reserved` | `worker_skill`: string or null for preflight; `automatic_repair`: boolean | A durable reservation exists. It is not evidence of process launch. |
| `attempt_finished` | `outcome`: `finished`, `failed`, `interrupted`, or `unknown`; `exit_code`: integer or null; `elapsed_seconds`: nonnegative number or null | What the process receipt establishes. Exit zero is not acceptance. |
| `report_recorded` | `disposition`: `saved` or `rejected`; `reported_status`: string or null; `rejection_reason`: string or null | The controller's handling of a report. `reported_status` is quoted source data, including invalid values. It is not a new verdict. |
| `candidate_captured` | `previous_candidate_key`: string or null | A recoverable candidate was captured; `identity.candidate_key` identifies the new candidate. |
| `delivery_checkpoint` | `status`: `RUNNING`, `BLOCKED`, or `REVIEWED_AND_PROVEN`; `reason`: string or null | An existing controller result, not an experience-derived decision. |
| `observation` | `expected`: string or null; `consequence`: string or null | Something noteworthy was observed or reported. |
| `hypothesis` | `proposed_check`: string or null | A possible explanation, explicitly unconfirmed. |
| `intervention` | `disposition`: `proposed`, `performed`, or `discarded` | What was tried or proposed, including discarded experiments and attributed human decisions. |
| `evaluation` | `result`: `passed`, `failed`, `inconclusive`, `unavailable`, or `pending`; `check`: string or null | The reported result of a named check. A focused pass is not full proof. |
| `lesson_candidate` | `scope`: nonblank string; `disposition`: exactly `pending` | A potentially reusable suggestion, not accepted advice. |
| `correction` | `reason`: nonblank string | A later correction of a prior record; requires a `corrects` link. |
| `capture_gap` | `reason`: nonblank string | A known limitation in capture or recovery, without an invented outcome. |

Automated controller events cite actual saved inputs or results. Worker notes and historical imports remain visibly attributed even when their reference hashes match. Hash validation establishes reference integrity, not the truth of an interpretation.

Allowed link relations are `responds_to`, `evaluates`, `supports`, `supported_by`, `refutes`, `corrects`, and `follows`. A link reads from the current event to its target: an intervention responds to a finding; an evaluation evaluates an intervention; new evidence supports or refutes an earlier hypothesis; a lesson is supported by earlier observations. `follows` records sequence only, not causation. A timestamp or a matching requirement ID is insufficient to infer causation. The recorder creates only mechanically established links or links explicitly supplied with attribution. It never invents a root cause or an `introduced_by` claim.

### 7.3 Version and input validation

Validate types, required fields, finite numeric values, enumerated control values, identities, references, and nonblank strings. Boolean values must not pass integer validation. Duplicate JSON keys, non-finite numbers, unknown schemas, and malformed paths are errors.

A string such as `x` may be structurally valid and still useless. Do not claim that this validator judges significance or meaning. Skill behavior and real invocation evaluation must assess that separately.

Unknown schema versions are not silently skipped or reinterpreted. Viewing marks the history partial and displays a diagnostic; writing refuses to extend an unverifiable canonical history. Neither action modifies delivery acceptance.

## 8. Evidence and historical identity

An evidence reference has these fields:

```text
path:          repository-relative path, or null
sha256:        expected full digest, or null
git_commit:    full immutable recovery commit, or null
locator:       descriptive location inside the referenced bytes, or null
availability: retained | unavailable
description:  short description or explanation of the limitation
```

`retained` requires a path and digest, and requires successful readback when the event is stored. For unavailable evidence, the description states what is missing; a known hash may still be retained, but must not be presented as recoverable content.

Reference resolution checks exact bytes in this order: the named current file; the named immutable Git commit, when supplied; the protocol's work-item history location for those bytes; then an applicable explicit archive recovery entry. Never silently substitute today's `proof.md` or `candidate.json` when the digest differs. Do not scan all Git history or restore over newer files automatically.

Prefer immutable per-attempt reports to top-level mutable reports. For candidate captures, retain a reference to the recoverable candidate record and contract context, not only a friendly label. Follow the existing history rule before later replacement. [S4]

A worker may cite a discarded experiment. Its evidence must identify it as an experiment in writable scratch, not as behavior of the unchanged proven candidate. During implementation or repair, the working copy may change before a new candidate is captured: the recorder must label such notes as intermediate work in `statement` or evidence description, and must not imply that the incoming candidate hash identifies those intermediate bytes.

Later discovery that evidence is unavailable does not rewrite the event. Viewing shows the failure to resolve it. A substantive correction is a new linked event.

## 9. Capturing experience during work

### 9.1 Controller-observed milestones

Record only after the authoritative operation has durably succeeded, except that a rejection records the rejection itself rather than a successful operation.

| Existing boundary | Experience action |
|---|---|
| Admission persisted | Record `invocation_started`. No feature-specific record is created before existing local authority is established. |
| `Delivery.reserve` persisted | Record `attempt_reserved`; retain actual stage and selected worker skill. Review-led correction can use `implement-contract` even when its orchestration stage is `repair`. |
| Validated process completion receipt | Record `attempt_finished` with observed outcome and elapsed time. Keep token usage as an evidence reference; do not infer money from it. |
| Report saved and reread | Record `report_recorded` with disposition `saved`, its source status, and immutable report reference. |
| Report rejected by an existing guard | Record `report_recorded` with disposition `rejected` and the actual reason, when safe source evidence is retained. Do not parse arbitrary stderr to invent a semantic failure category. |
| Candidate captured and delivery state persisted | Record `candidate_captured`, preserving the previous candidate when known. |
| Completion or blocker persisted | Record `delivery_checkpoint`, import available notes, and refresh derived views. |

Feature-specific admission rejection logging before an invocation exists is outside v1. Where the controller cannot safely retain a rejection reason, expose a capture warning rather than invent a durable rejection record.

Capture must not run a validator with different acceptance rules from the controller or mutate a report to make it fit experience storage. A malformed acceptance report remains governed by the existing delivery rules.

Normalize existing `preflight-1` and `preflight-2` names to stage `preflight`; their actual attempt IDs keep them distinct.

Use stable keys such as `<invocation-id>/started`, `<attempt-id>/reserved`, `<attempt-id>/finished`, and `<attempt-id>/report/<saved-or-rejected>/<source-digest>`. Candidate keys include the producing attempt or `admission`, plus the exact candidate key. A repeated checkpoint uses the invocation ID plus a digest of its stable status, blocker, candidate, attempt IDs, and report identities; omit observation-clock values from that digest.

### 9.2 Worker notes: a separate outbox

For an instrumented attempt, the enclosing controller creates an outbox inside that worker's already authorized writable root:

```text
<worker-writable-root>/.p2p/experience-outbox/<attempt-id>/
    notes/<local-id>.json
    evidence/<descriptive-name>.txt
```

The outbox is staging, not canonical evidence. It must not be placed in a disposable `.p2p/tmp/` directory or deleted before import. It must stay outside product candidate content and outside shared controller records. No new writable root, network permission, or subprocess escalation is granted.

Add a short instruction to the stage invocation and relevant skills:

> When an observation materially changes the approach, record the observation, any attempted response, and its result. Cite evidence. Distinguish an observation from a hypothesis. Empty output is valid. Do not write internal reasoning or a diary. Experience notes do not change your report or verdict.

A note uses `promise-to-proof/experience-note/v1` with exactly:

```text
schema
observed_at    # Source UTC timestamp, or null; never inferred from import time
local_id       # Stable within the attempt; [A-Za-z0-9][A-Za-z0-9_-]{0,63}
local_order    # Positive integer; unique within the attempt
kind           # observation, hypothesis, intervention, evaluation, lesson_candidate
               # record additionally accepts correction; emit does not
statement
requirement_ids
data           # Same kind-specific fields as canonical records
evidence       # Note reference descriptors below
links          # References to earlier local notes or existing event IDs
```

The worker does not supply canonical sequence, recorder timestamp, invocation identity, or candidate identity. A controller importer assigns those fields from its context.

Note evidence descriptors use these exact shapes (the values below describe types):

```text
{type: "report", locator: string-or-null, description: string}
{type: "outbox_file", path: string, sha256: full-digest, description: string}
{type: "retained", reference: section-8-reference}
{type: "unavailable", description: string}
```

A `report` descriptor identifies this attempt's eventual retained report; missing reports become unavailable references. An `outbox_file` path is relative to the supplied outbox and must start with `evidence/`; retain its safe bytes before referring to them. A `retained` reference must resolve to exact bytes. `unavailable` preserves a limitation, including a transient observation that cannot be recovered. Public historical `record` accepts only `retained` and `unavailable` descriptors; it does not guess a worker outbox or eventual report.

A note link names a relation plus either `local_id` or `event_id`, never both. All textual fields in note `data`, reference descriptions, and locators are subject to the total note byte limit. A public `record` batch applies the per-attempt note/evidence limits to its supplied context, even when no controller attempt ID exists. Local links must resolve to earlier `local_order` values. Import notes in that order and convert local links to canonical event IDs. Do not silently drop an unresolved link; skip that note with a warning, allowing an explicit corrected resubmission under the same identity when nothing was accepted.

A note is worth emitting when a check disproves an assumption, a repair fails or is discarded, verification is unavailable or misleading, a new finding changes direction, or a consequential human decision changes the work. No minimum note count is imposed.

Emit notes during the existing worker session; do not make an extra model call to explain a finished run. Import after the process stops and before cleanup, including on handled failure. On restart, import intact remaining outbox files without relaunching the worker.

**Durability boundary:** a worker emission is only staged. It becomes a durable experience record after canonical save and readback. A host crash or missing outbox before that point can lose an unimported note; disclose partial capture rather than claiming full recovery. Preserving such unacknowledged notes against every host failure is outside v1.

### 9.3 Skill-led delivery and historical import

The authorized enclosing session can submit the same note form with an explicit context manifest. Use `promise-to-proof/experience-context/v1`, with exactly these fields:

```text
schema
work_item
producer        # worker, human, or backfill; public record cannot assert controller
producer_id     # Stable actual source session/attempt or labeled historical import
invocation_id   # Actual ID or null
attempt_id      # Actual ID or null
stage           # Same enum as a canonical record
identity        # Same object as a canonical record, including explicit nulls
evidence        # Section 8 references supporting the context itself
```

The work item in the manifest must match the command argument. Each note's evidence is combined with context evidence, deduplicating exact reference objects. `record` adds no authority merely because a context file asserts it. Correction notes require an existing `corrects` link, retain their source, and leave the original event unchanged.

The helper records `origin.producer` as `human`, `worker`, or `backfill`, as appropriate. It must not relabel these records as controller-observed events or infer independent verification from prose.

Historical import requires an explicit saved source such as a report, sanitized conversation excerpt, or screenshot. The new small-text importer need not copy a screenshot; it may reference an already retained safe image with its exact digest. Missing candidate content stays unknown. Import does not claim that old records were captured live, and does not synthesize the failed attempts or commands absent from the source.

Do not automatically parse every old transcript. Backfill only mechanically recoverable controller facts and explicitly supplied notes.

## 10. Persistence, idempotency, and concurrency

All canonical experience writes for a work item use the existing `delivery.lock`. A controller already holding the lock calls an internal locked function; it must not reacquire the lock through a child process. An external writer uses the same nonblocking lock and returns a retryable busy result without writing if another process owns it.

Under the lock:

1. Validate the accepted canonical record set and input. Resolve references and retain any new safe evidence first.
2. Compute the event ID from stable source identity.
3. If that ID already exists, compare normalized submitted content, excluding recorder-assigned `sequence` and `recorded_at`. Identical submission returns the existing receipt without a write; conflicting content is an error, not a new event.
4. Allocate `sequence = highest retained sequence + 1` and assign the recorder timestamp.
5. Write the complete new JSON file using existing atomic storage, then reread and compare exact bytes.
6. Return the event ID and saved path only after readback succeeds.

Missing historical evidence degrades reference availability but does not by itself prohibit appending a new well-formed record. Corrupt canonical JSON, schema incompatibility, or sequence/identity conflicts are different: refuse extension and name the affected record. Recovery must restore verified original bytes or use an explicitly approved reconciliation; there is no force-overwrite option.

A stable source key is a uniqueness key, not permission to overwrite. A correction after acceptance uses a new event linked with `corrects`. A changed payload under an already accepted local note ID is rejected.

Record order is persistence order. Preserve `observed_at` and local note order, but do not claim that backfilled or concurrent observations happened in sequence order. Corrected earlier events remain readable.

Readers accept only fully written canonical `.json` files whose filenames match event IDs. Temporary files are not events. Duplicate or missing interior sequences, corrupt canonical records, missing required identities without an explanation, or incompatible schemas make the view partial and prevent extending that record set until explicitly reconciled. Do not silently renumber or delete history.

The guarantee covers cooperating writers on the supported local filesystem using the shared lock. It does not claim protection against arbitrary same-user tampering, multiple unsynchronized checkout writers, or manual Git merge corruption. A merged record conflict must be reported, not automatically repaired.

## 11. Restart and capture failures

### Recovery without new work

Before resuming new stage work, reconcile experience with available persisted controller records. For a source-derived ID that already exists, verify its original source references and leave its original live/backfill provenance and timestamp intact; do not resubmit a newly synthesized copy with different recording provenance. A changed source under that same ID is a conflict. Import intact pending notes. Stable source keys prevent duplicate events. Recovery must never launch a worker, spend a new repair allowance, or reinterpret an unknown dispatch as a completed attempt merely to fill the timeline.

A crash between delivery persistence and experience persistence may leave a missing milestone. Backfill a fact only if its retained source unambiguously establishes it. Use `origin.producer = backfill`, retain the original observed timestamp when known, and use the new actual recording timestamp. Do not infer overwritten historical checkpoints from current state. Record a capture gap for known missing coverage when storage becomes available.

After a crash following event persistence but preceding receipt return or rendering, a retry finds the identical event and rebuilds views. No duplicate note or stage invocation is created.

### Separate capture health from acceptance

An experience-only schema, storage, or rendering error produces a warning and `partial` or `unavailable` capture. It does not change a valid review/proof verdict, disable an acceptance guard, or turn an existing `BLOCKED` result into success.

If the shared disk is also unable to retain required acceptance evidence, normal delivery storage rules still block completion. Only optional experience failure is non-gating. Do not catch and suppress unrelated delivery errors inside the experience wrapper.

When no warning can itself be persisted, return it in the CLI result or stderr. Never claim the lost note was saved. On a later successful reconciliation, retain an explicit capture-gap record when the loss is known.

`status` and default viewing remain read-only: no lock file creation, outbox draining, cache refresh, timestamp update, or attempt launch. They may report stale or partial experience. Explicit `sync` is the write operation.

## 12. Deterministic views

`events.jsonl` contains canonical records in ascending sequence, one canonical JSON object and one newline per record. It can be regenerated entirely from `records/`.

`summary.md` is a rendering, not an LLM-generated retrospective. Its contents are a deterministic function of the retained record set, explicit reference-availability inspection results, and renderer version. Identical inputs produce identical bytes; a newly unavailable source may legitimately change the evidence diagnostics. Do not insert the current clock time or inferred conclusions.

The view includes the work item, record count and maximum sequence, renderer version, latest recorded delivery checkpoint, capture limitations, and a timeline grouped by actual invocation/attempt/candidate identities. Within each group, show the supplied observation, attempted response, evaluation, and explicit links. Distinguish these labels:

```text
Controller recorded
Worker reported
Human reported
Imported historical account
Hypothesis — unconfirmed
Lesson candidate — pending
Evidence unavailable
```

Show “latest recorded state,” not “current acceptance,” because a historical renderer does not re-prove the candidate. A note that a focused check passed cannot become `PROVEN`; a V3 fix awaiting verification must remain pending.

Render source links using resolvable local paths or pinned references. Escape untrusted text so notes cannot become active HTML, scripts, remote images, or misleading headings. Do not execute embedded commands or fetch URLs while rendering.

At minimum, a rendered version of the motivating example should convey:

```text
V1: contradictory review representation reported.
Response: remove agent-written summary; derive it from structured fields.
V2: suite reported passing; independent review reported an invalid-status gap.
Response: constrain allowed statuses and add regression coverage.
V3: changed candidate recorded; full verification pending.
Possible lesson: validate stage-specific value domains. Disposition: pending.
```

The renderer cannot invent this narrative from bare timestamps. The human/worker notes supply its meaning; the renderer supplies organization and provenance.

## 13. Privacy, isolation, and resource limits

This is local-first recording with no automatic export. Local records may later be committed under separate authority, so local storage is not a license to retain secrets. Apply the protocol's safe-evidence rules before importing notes or copying supporting text. [S4]

Only allowlisted structured fields enter canonical records. Do not copy entire prompts, model transcripts, environment variables, credentials, arbitrary stderr, or private internal reasoning. Prefer existing safe report references. An observation containing sensitive material must be rewritten as a safe description with an explicit evidence limitation; it must not be copied into canonical files or their history.

Basic secret-pattern checks and test fixtures are useful safeguards, not a guarantee that all secrets are detected. State that limitation. A discovered secret must not be “fixed” only by adding a correction while leaving the secret in a shareable history; use the repository's separately authorized sensitive-data remediation procedure.

For v1, enforce these implementation limits:

| Item | Limit and behavior |
|---|---|
| Note JSON file | At most 16 KiB. Reject larger notes with an explicit warning. |
| Statement | At most 2,000 Unicode characters. |
| Notes per attempt | At most 100, ordered by `local_order`; report omitted capture rather than silently truncating. |
| New outbox evidence file | Regular UTF-8 text only, at most 256 KiB. Reject symlinks, devices, directories, and traversal. |
| New outbox evidence per attempt | At most 1 MiB retained in total. Larger evidence uses an already retained safe reference or is marked unavailable. |

These are initial bounds, not measured optimal values. Validate source paths against explicitly allowed roots; reject absolute note paths, `..`, `.git`, symlink escapes, and conflicting output destinations. A worker-supplied hash is checked against actual safe bytes.

Review and proof do not receive earlier experience narratives as additional input. Keep their existing independent contexts. Repair continues to receive only the prior findings authorized by its existing workflow; recording history does not create permission to bias future verifiers.

## 14. Implementation interfaces and file scope

Add a small standard-library module and CLI at:

```text
skills/productivity/deliver-issue/scripts/p2p_experience.py
```

Reuse `p2p_filesystem.py` for safe paths, digests, atomic writing, and retention. Read-only historical viewing must not depend on successful validation of today's candidate: a malformed or changed current candidate must not make retained experience unreadable.

Provide these operations; they are proposed interfaces, not existing commands:

```sh
# Worker: stage a note inside the already authorized outbox.
python3 p2p_experience.py emit --outbox "$P2P_EXPERIENCE_OUTBOX" --from note.json

# Enclosing session: record an explicitly supplied note batch and context.
python3 p2p_experience.py --repo ROOT record work/example.md \
  --context context.json --from notes.json

# Recover available facts/notes and save the views; never execute delivery work.
python3 p2p_experience.py --repo ROOT sync work/example.md

# Read only, to stdout. --format accepts markdown or jsonl.
python3 p2p_experience.py --repo ROOT show work/example.md --format markdown
```

The controller supplies the outbox location explicitly in the worker's prompt and environment. `emit` returns a **staged** receipt, not a durable-capture claim. Its atomic file creation is idempotent for the same local ID and content. Duplicate local orders with different IDs are rejected.

`record` accepts a JSON array of notes plus one context manifest, preserves that batch's local ordering, and returns durable receipts. CLI input filenames are relative to the caller's working directory; evidence paths are relative to `--repo`. A batch is not an all-or-nothing transaction: retain valid independent notes, skip invalid notes and unresolved dependents, and return receipts and explicit per-note errors. A partial batch returns exit code 1 and can be retried with the same source keys. Refresh views after the batch when possible.

`sync` imports only from retained, explicitly associated controller attempts and their outboxes; it does not search arbitrary files for possible lessons. To retry a historical batch, explicitly invoke `record` again with the source inputs. Running it again without new sources is a no-op except repairing missing or stale derived views.

Helper exit codes: `0` successful operation, `1` validation/storage/conflict or incomplete synchronization, `2` invalid CLI usage, `3` busy lock. Diagnostics identify the source and whether anything was actually saved. These codes do not replace controller exit codes.

Expose internal equivalents so the controller can record while already holding the lock. Keep functions small: validate note/record, resolve evidence, store idempotently, import an outbox, reconcile retained sources, and render views. Do not implement a generic event bus.

### Expected changes

| Area | Bounded change |
|---|---|
| `p2p_experience.py` | New helper, format validation, storage, import, rendering, CLI. |
| `p2p_delivery.py` | Capture hooks, outbox setup/import, isolated warnings, additive experience result metadata. Preserve report schemas and acceptance decisions. |
| `deliver-issue/SKILL.md` | Explain capture ownership, skill-led recording, and the experience handoff. |
| `implement-contract`, `review-implementation`, `prove`, `repair-gaps` skills | Short optional-note guidance and access to the shared helper through the repository's existing shared-script convention. Do not duplicate the format specification into every skill. |
| `docs/acceptance-contract-protocol.md` | Document experience as non-authoritative durable records; workers stage notes and enclosing workflows retain them. Preserve retrospective semantics. |
| Controller guide / HOW-TO | Explain viewing, partial capture, explicit import, and recovery. |
| `checks/test_p2p_experience.py` and controller tests | Add observable behavior and fault-injection coverage. |
| Existing live-host check or a focused companion | Demonstrate actual worker note emission/import under unchanged isolation. |

Use installed-script symlinks in the same manner as the existing filesystem helper. Verify standalone skill installation resolves dependencies; do not assume a checkout-relative import exists in an installed skill. [S7]

Do not add a new slash command, a mandatory retrospective, new setup placeholders, or a new top-level work-item type.

## 15. Acceptance criteria and tests

The following are proposed requirements to carry into one canonical `work/` acceptance contract through `/plan-acceptance`. They are not evidence that any check has been run.

| ID | Required observable result | Test and independent oracle |
|---|---|---|
| R1 | A supported successful delivery records admission, each real reservation/completion, saved reports, candidate changes, and the final checkpoint. | Run the existing controlled transport fixture; compare experience with retained attempt IDs, receipts, reports, and candidate digests. A reservation must not render as a launch. |
| R2 | Significant worker notes survive durable import with their attributed finding → intervention → evaluation links. An empty notes set is valid. | Emit ordered notes and safe evidence through the public helper; import, reopen in a fresh process, and compare exact fields and linked IDs. Include a normal run with no notes. |
| R3 | Failed, blocked, interrupted, and explicitly abandoned work can contribute experience without claiming acceptance. | Exercise failure, repair exhaustion, and unavailable proof. Record abandonment as a separately attributed human decision; do not infer it from the blocker. |
| R4 | Replay, repeated `resume`, and repeated `sync` do not duplicate events or dispatch workers for logging. | Stop after event save but before acknowledgment, then retry in a fresh process. Assert the same event ID/sequence and unchanged host launch count and repair allowance. |
| R5 | Recording failure cannot corrupt existing experience or required delivery records. | Inject failure before atomic replacement and after source evidence is retained. Old events remain byte-identical; unmatched extra evidence is not rendered as an event. |
| R6 | Concurrent writes use the shared lock and cannot assign conflicting sequences. | Hold the work-item lock, call external `record` and `sync`, assert busy/no writes; then release and retry. Test internal controller recording without nested lock acquisition. |
| R7 | Historical references remain tied to exact bytes across candidate/report replacement and authorized archival. | Replace top-level reports using existing retention; resolve old records to original bytes. Remove recovery content and confirm the view says unavailable instead of citing the new file. |
| R8 | Facts, hypotheses, focused results, pending lessons, and current acceptance remain distinct. | Feed a `passed` evaluation, invalid raw status `PROVEN` from a review, and a pending lesson. The view quotes their origin and does not infer full proof, execute instructions, or update a learning register. |
| R9 | Experience failures are non-gating, but required proof-storage failures remain gating. | Run the same fixture with working, missing, malformed, oversized, and unwritable experience inputs; compare acceptance and stage dispatches. Separately fail `proof.md` persistence and assert the existing blocker remains. |
| R10 | `status` and `show` are genuinely read-only; views are deterministic and reconstructible. | Compare full file inventory/bytes before and after reads. Render the same records and evidence-availability inputs twice byte-for-byte; regenerate missing views with `sync` without model calls. |
| R11 | Schema, size, privacy, and path boundaries are enforced honestly. | Test invalid enums, boolean sequence, duplicate JSON keys, conflicting IDs, wrong hashes, unresolved links, traversal, symlinks, oversize notes, and planted secret-bearing content. No prohibited bytes enter canonical records; limits produce warnings. |
| R12 | Skill-led/historical experience can be recorded without inventing controller provenance or widening repair policy. | Use the motivating three-version fixture described below, including unknown inputs. Compare the saved history with declared source artifacts and authorization boundaries. |
| R13 | Actual supported-host use demonstrates notes without new acceptance or sandbox authority. | Run a bounded live worker fixture with a checkable surprising outcome; retain host identities, an emitted note, its imported event, and protected-write denial evidence. Repeat with an unremarkable control; zero invented lessons is acceptable. |
| R14 | Existing delivery, filesystem, bundle, and relevant conformance behavior remains intact. | Run the existing suites; compare public controller observations and persisted state. Fixture success must not be described as live-host proof. |

### The three-version regression fixture

Create reproducible synthetic candidates C1, C2, and C3 with actual retained bytes and independently specified expected behavior. Do not use the screenshot's unavailable snapshot digest as fixture evidence.

C1 permits contradictory review representation. A recorded intervention leads to C2, whose focused check passes but which still permits an invalid review status. Record that new finding. C3 adds the relevant restriction; its initial timeline must show full review/proof pending.

**Respect the existing repair bound.** Use one controller invocation for at most one automatic repair, ending blocked when findings remain. Represent the later correction through a separately authorized skill-led repair and fresh stage handoff, with distinct actual execution identity and retained authority attribution. Do not delete `delivery.json`, reset `repair_used`, or introduce a second automatic repair to make the fixture convenient. [S6]

Assert that a fresh session can recover all three identities, both findings, the attempted responses, the focused pass, and the remaining verification gap. Re-render after any later full verification as additional historical events, not edits to the earlier pending observation.

## 16. Implementation order and rollout

**Increment A — Storage and readable history.** Implement validation, evidence references, idempotent storage, explicit recording, and deterministic views. Use the synthetic three-version example and crash/lock tests. This makes the format independently usable before controller hooks exist.

**Increment B — Capture during delivery.** Add controller hooks and worker outboxes, including failed-attempt import, best-effort recovery, and non-gating diagnostics. Add the small skill instructions and isolated live-host demonstration.

**Increment C — Compatibility and handoff.** Run the existing regression/conformance suites, document installation and recovery, and prove the complete agreed contract against one exact implementation candidate. A storage-only increment is not full delivery of this specification.

Activate worker instrumentation only for new invocations prepared with the new feature. Do not silently rewrite prompts, schemas, installed-skill hashes, or permissions of an already reserved attempt. Older records remain viewable through explicit, visibly partial backfill. Existing controller compatibility checks continue to decide whether an interrupted invocation can resume.

Rollback removes or disables the optional capture hooks for new runs without deleting history or rewriting delivery evidence; v1 does not require a new runtime feature-flag system. A reader for the retained format should remain available. Never roll back acceptance protections merely to keep experience capture working.

Before implementation, inspect the then-current repository and any in-flight report-boundary changes. Resolve collisions with those changes rather than treating this inspected baseline as permission to overwrite them. Save the agreed scope in `work/delivery-experience.md` through the existing planning workflow; this document does not itself approve implementation or publication.

## 17. How this supports later improvement

This delivery creates inputs for later analysis, not the analysis engine. A future improvement proposal can cite exact experience event IDs, identify a reusable hypothesis, make an authorized P2P change, and evaluate it against reproductions and separate cases.

The strategy-comparison work in issue #32 is a potential consumer because it already calls for accounting for failures, repair, waiting, and human work. Experience records must not pretend to supply independent correctness labels, monetary costs, or complete human-effort measurements that were never collected. [S8]

Success for this first feature is simpler: the next time someone asks **“What have we learned so far?”**, P2P can show a sourced, recoverable history of what changed our understanding, including what remains unverified.

## 18. Sources and verification limits

Repository facts above were checked against the pinned baseline. Proposed event names, commands, limits, and file layout are design decisions in this specification, not existing repository features. Repository tests and the user's local V3 candidate were not executed while preparing it.

- **[S1] Controller implementation.** [p2p_delivery.py, pinned](https://github.com/grove/promise-to-proof/blob/5e369c1b45ba817b8add6b20a9b7b1c97898fa12/skills/productivity/deliver-issue/scripts/p2p_delivery.py). Existing stage/report schema, dispatch, receipts, reservation, capture, and CLI behavior.
- **[S2] Controller guide.** [p2p-delivery-controller.md, pinned](https://github.com/grove/promise-to-proof/blob/5e369c1b45ba817b8add6b20a9b7b1c97898fa12/docs/p2p-delivery-controller.md). Supported host, saved records, recovery, and boundaries.
- **[S3] Filesystem implementation.** [p2p_filesystem.py, pinned](https://github.com/grove/promise-to-proof/blob/5e369c1b45ba817b8add6b20a9b7b1c97898fa12/skills/productivity/deliver-issue/scripts/p2p_filesystem.py). Safe paths, canonical hashing, atomic writes, and history preservation.
- **[S4] Shared protocol.** [acceptance-contract-protocol.md, pinned](https://github.com/grove/promise-to-proof/blob/5e369c1b45ba817b8add6b20a9b7b1c97898fa12/docs/acceptance-contract-protocol.md). Authority, identity, recoverable records, safe evidence, and archival rules.
- **[S5] Retrospective skill.** [retrospect/SKILL.md, pinned](https://github.com/grove/promise-to-proof/blob/5e369c1b45ba817b8add6b20a9b7b1c97898fa12/skills/productivity/retrospect/SKILL.md). Requires matching full proof and keeps proposed learning separate from accepted advice and binding authority.
- **[S6] Delivery skill.** [deliver-issue/SKILL.md, pinned](https://github.com/grove/promise-to-proof/blob/5e369c1b45ba817b8add6b20a9b7b1c97898fa12/skills/productivity/deliver-issue/SKILL.md). Independent stages, scoped repairs, one automatic repair cycle per invocation, and external-effect separation.
- **[S7] Repository README.** [README.md, pinned](https://github.com/grove/promise-to-proof/blob/5e369c1b45ba817b8add6b20a9b7b1c97898fa12/README.md). Shared-script installation convention and repository structure.
- **[S8] Fixed-strategy comparison.** [Issue #32](https://github.com/grove/promise-to-proof/issues/32), retrieved 27 September 2026. A future consumer; tracker contents are mutable and this issue does not authorize the present proposal.
- **[S9] User-provided example.** Screenshot and discussion in the conversation requesting this specification. Attributed, not independently verified; preserve a safe copy with any future historical import.


## Appendix A. Concrete example inputs

The companion package contains `examples/context.json`, `examples/notes.json`, a synthetic work item, and a source excerpt under `examples/.p2p/work/example/evidence/`. These are **documentation fixtures, not execution evidence**. Their reference digests are computed from the included exact bytes.

The example deliberately leaves candidate and execution identities unknown. It records seven linked notes: a finding, an intervention, a reported focused pass, another finding, a follow-up intervention, pending full verification, and a pending lesson. It does not simulate a second automatic controller repair.

One note in that batch has this form:

```json
{
  "schema": "promise-to-proof/experience-note/v1",
  "observed_at": null,
  "local_id": "E2",
  "local_order": 6,
  "kind": "evaluation",
  "statement": "Full tests and fresh review/proof of the fictional V3 remain pending.",
  "requirement_ids": [],
  "data": {
    "result": "pending",
    "check": "Full tests, independent review, and proof."
  },
  "evidence": [
    {
      "type": "unavailable",
      "description": "No full verification execution is supplied in this synthetic example."
    }
  ],
  "links": [
    {"relation": "evaluates", "local_id": "I2"}
  ]
}
```

This standalone excerpt relies on the batch's earlier `I2` and context manifest; it is not a complete import by itself. The packaged batch additionally cites its retained synthetic source. Once the helper exists, the example README gives the intended import command and expected rendering behavior.
