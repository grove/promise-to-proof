# Delivery completion model

This bounded FizzBee model checks one local `work/` item's completion rules at
repository revision `41bebc726a8cc71c1d2f22d822ade006f4e78121`. It models the
protocol, not execution of Markdown instructions by an agent. A passing run
provides no evidence that a real host enforced isolation, ran a stage, or retained
adequate proof.

## Run

The tested tool is [FizzBee v0.5.3](https://github.com/fizzbee-io/fizzbee/releases/tag/v0.5.3).
This first runner supports the macOS arm64 release and Python 3.9 or newer.
Download and unpack `fizzbee-v0.5.3-macos_arm.tar.gz` from that release. Verify
its SHA-256 before use:

```text
bc702e3a15a4720509bcf70e38bf95ad1b7586dc69d54848deb1cc9674043a50
```

Keep the extracted directory intact. The runner checks the release's `fizz`,
`fizzbee`, and parser executable hashes. It refuses other versions. From the
repository root, run this one check command, substituting your installation path:

```sh
python3 checks/delivery-model/check.py --fizz /path/to/fizzbee-v0.5.3-macos_arm/fizz --output-dir /tmp/delivery-check-new
```

The output directory must not exist. Omit `--output-dir` to allocate a fresh OS
temporary directory. `FIZZBEE` can also supply the executable path. The runner
writes nothing beside its source, so checks can run against an immutable
candidate. Durable delivery evidence belongs in a new directory beneath
`.p2p/work/delivery-completion-integrity/evidence/`.

Expect 43 checks: 11 baseline explorations, 18 reachable witnesses, and 14
mutation counterexamples. Each baseline must finish successfully without reaching
the 64-action cutoff. Each witness intentionally falsifies only the negated
reachability assertion `Witness`. Each mutation must fail its named safety
property and the Python runner checks the final trace's concrete violating facts.
A FizzBee parse error, wrong assertion, timeout, or missing trace fails the command.
FizzBee's wrapper returns zero for some invariant failures, so the runner checks
the actual verdict text as well as the process exit status.

`summary.json` records the environment, exact model and binary hashes, commands,
runtimes, graph node counts, maximum action depths, reachable outcomes, and action
coverage. Each check retains `model.fizz`, `output.txt`, and `observation.json`.
Witnesses and mutations also retain complete ordered `trace.json` and `trace.txt`
action/state records. To reproduce an individual counterexample, run the pinned
`fizz` against that retained `model.fizz`, with `--output-dir` pointing at a new
scratch directory. Breadth-first exploration regenerates the trace; no Python
simulator substitutes for the FizzBee check. Copy the model into scratch first
when the evidence directory is read-only, because FizzBee writes its parsed AST
beside its input.

## State and transitions

`Implement` produces the first candidate. `Launch` captures exact inputs for
review or proof; `Return` creates their volatile report and evidence. Launch and
return are distinct so source changes can race a delayed verifier. Review and
proof may run and return in either order. Each is a separate abstract invocation,
with different IDs; the model assumes that trusted read-only host isolation
exists. It does not establish that assumption.

`Save` and `ReadBack` act separately on each report and evidence artifact.
Artifact states are 0 absent, 1 volatile, 2 saved but not reread, 3 reread and
retrievable, 4 content lost, and 5 inaccessible. `Environment` can change exact
contract text, candidate or review base, or lose content/access after readback.
The text identity changes while the revision stays `v1`. An `identity` scenario
also permits an old mismatched proof report to arrive.

`Repair` changes the candidate, discards both earlier reports, and requires new
review and proof. It increments durable `repair_used`; the independent
`repairs_actual` history checks that the scheduler cannot launder this allowance.
`Restart` loses volatile results and readback knowledge, preserves saved content,
and retains the repair count. Saved reports must be reread. Evidence that never
finished saving is absent after restart. This model deliberately blocks when
that missing evidence cannot be recovered; it does not model rerunning such a
stage as an additional recovery strategy.

`Complete` is an operational decision, with named blockers. Separate `always
assertion` properties inspect any claimed completion. They contain no mutation
switches. The runner weakens operational checks in scratch copies, leaving these
oracles intact. A weakened identity guard can violate both report agreement and
current text; `SameReports` is the required first counterexample in that case.

## Traceability

The authoritative sources are the pinned [acceptance protocol](../../docs/acceptance-contract-protocol.md),
[current delivery skill](../../skills/productivity/deliver-issue/SKILL.md), and
[contract v1](../../work/delivery-completion-integrity.md). The I-numbers below
come from section 9 of the [optimization handoff](../../plans/promise_to_proof_optimization_handoff.md).

| Requirement / property | Protocol obligation and model oracle | Retained checks |
|---|---|---|
| R1, R8 | Implementation/review/proof handoffs; stage separation, persistence, repair and resume | `baseline-*`; `witness-initial`, `witness-repair`, `witness-restart`, `witness-exhausted` |
| R2 / I02 | Candidate identity and proof handoffs: reports agree and bind the current input; `SameReports`, `CurrentText`, `CurrentCandidate`, `IndependentFullStages` | `identity`, `missing-stage` witnesses; `mutation-identity` |
| R3 / I03 | Implementation and review handoffs: exact comparison base; `ComparisonBase` | `base` baseline, witness, mutation |
| R4 / I05 | Requirements/revisions and proof handoffs: exact text independent of revision; `CurrentText` | `text` baseline, witness, mutation with `v1` unchanged |
| R5 / I04 | Proof/repair handoffs: both verifiers refresh after candidate changes; `CurrentCandidate` | `candidate` baseline, witness, mutation; successful fresh `repair` witness |
| R6 / I08 | Durable generated records: saved, reread, retrievable report/evidence content; `DurableReports`, `DurableEvidence` | `report-save/read/lost/access`, `evidence-save/read/lost/access/absent` witnesses and mutations |
| R7 / I14 | Delivery step 9: at most one automatic repair per invocation; `RepairBound` | `exhausted`, `restart`; `mutation-repair-reset` |
| R9 | Each protection must reject its deliberate weakening | All 14 `mutation-*` retained traces; independent terminal-state checks in `check_trace` |
| R10 | Reproducibility and truthful exploration claims | This file, binary pins, `summary.json`, cutoff/timeout rejection |

## Bounds and limits

The state space has one work item, two verifiers, two artifacts per verifier,
one optional restart, and at most one automatic repair. The broken repair-reset
variant can reach two repairs and must fail. Exact identities are abstract integer
values; there is no hashing or collision model. Revision is always `v1`.
Stage judgments are trusted complete judgments: both pass initially, proof fails
once in the repair scenario, and repeatedly in the exhausted scenario. The model
does not assess test adequacy, fabricated evidence, partial requirement coverage,
or actual agent judgment.

Exploration is exhaustive **within each finite scenario**, not exhaustive over
all possible faults. Eleven scenario families isolate source, candidate, base,
report and evidence failures; they do not combine independent fault families.
Normal persistence interruption and restart can interleave with each family.
`Environment` occurs at most once and can race any enabled nonterminal action,
subject to content/access loss requiring a prior successful readback. This covers
loss between readback and completion, but not arbitrary repeated churn or
change-and-restore attacks. Terminal claims freeze state; post-claim changes
belong to a later invocation and are unchecked.

All actions are atomic with one scheduler action at a time. The stage launch /
return split permits verifier overlap, but no real threads or storage atomicity
are modeled. No fairness or eventual-completion assumption is made. Stopping
with a blocker is valid; deadlock detection is disabled. Reachable completion
witnesses prevent an always-blocking model from passing the suite. They prove
existence of successful paths, not eventual delivery on every schedule.

The configured cap is 64 actions. With one restart and one repair, the lifecycle
cannot need that many changing actions; the runner additionally reads every
retained graph node's action depth and refuses a baseline reaching the cap.
Baseline exploration must exhaust its queue. Per-run timeout is 120 seconds;
a timeout reports failure, never partial exploration as a pass. Failed mutation
and witness searches stop at their first counterexample and do not claim full
state enumeration. Raw graph files are disposable; their measured counts,
action coverage, and maximum depth remain in the retained observations.

The [FizzBee configuration reference](https://fizzbee.io/design/tutorials/frontmatter/)
describes action bounds, and the [safety tutorial](https://fizzbee.io/design/tutorials/getting-started/)
describes invariant counterexamples. The runner reads the v0.5.3 node-file format
to detect cutoff; this format dependency is why a different release is rejected.

## Historical baseline

The handoff was written against `f5917ce0471d56aac01711e720426748626c99d0`.
The modeled revision is `41bebc726a8cc71c1d2f22d822ade006f4e78121`, not that older
tree. In the older protocol, a tracker could locate the canonical agreement and
local storage defaulted to `docs/acceptance-contracts/`. The current protocol uses
canonical `work/<slug>.md`, optional tracker imports, durable `.p2p/work/<slug>/`
records, exact binding-input hashes, recoverable candidate manifests, and a
filesystem helper. Current delivery also specifies host invocation records and
read-only verification boundaries more explicitly.

This model consequently starts with an established local agreement and durable
local records. Planning, approval, source imports, filesystem path resolution,
candidate reconstruction, real host isolation, publication authority, parent or
child work, and cross-candidate evidence reuse remain outside this increment.
The repair allowance belongs to the same invocation across restart under both
the issue's requirement and the current delivery rule. No existing workflow
instructions or acceptance verdicts change.
