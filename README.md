# Promise to Proof

Promise to Proof helps coding agents deliver what was actually agreed: **no missing
behavior, no accidental scope expansion, and no “done” claim without evidence**.

A normal coding workflow can blur several different questions into one. Did we
understand the request correctly? Did we implement all of it? Is the implementation
sound? Does the promised behavior actually work? Promise to Proof keeps those
questions separate, ties them to one exact implementation candidate, and carries the
agreement all the way from the original promise to evidence-backed acceptance.

> **Start with a promise. Make “done” precise. Build it. Review it. Prove it.**

## The idea in 30 seconds

```text
PROMISE
   ↓
PLAN WHAT "DONE" MEANS
   ↓
IMPLEMENT
   ↓
REVIEW + PROVE
   ↓
DELIVER
```

The core stage skills mirror that flow:

```text
/plan-acceptance
      ↓
/implement-contract
      ↓
/review-implementation + /prove
```

For one coherent work item, `/deliver-issue` coordinates the normal end-to-end
path when the host can provide the separate implementation, review, and proof
contexts that P2P requires. The stages remain available individually when you want
more control.

The result is intentionally stronger than “the agent says it is done.” P2P asks
what was promised, what evidence would establish it, what exact candidate was
checked, and whether independent review and proof agree about that same candidate.

## Why use Promise to Proof?

Coding agents are very good at moving quickly, but speed makes a few failure modes
especially easy to miss. An implementation can satisfy the obvious happy path while
quietly missing another requirement. A test suite can be green without checking the
specific outcome you asked for. A review can describe commit A while later changes
produce commit B. An agent can also add abstractions, cleanup, or product behavior
that sounded helpful but was never part of the agreement.

P2P is designed to make those gaps visible. It turns the requested outcome into an
acceptance contract with independently checkable promises, builds against that
contract, independently reviews the implementation, and then proves the promised
behavior on the exact candidate being accepted. Review and proof are separate on
purpose: good code can still fail the promised behavior, and behavior can appear to
work while the implementation contains an important engineering or scope problem.

## Supported today

Promise to Proof has two related ways to use the project: individual skills and the
coordinated delivery controller. The skills are packaged for agent-skill-compatible
coding tools. The production-validated direct controller path is currently narrower.

| Capability | Supported today |
|---|---|
| Standalone P2P skills | Agent-skill-compatible coding tools, subject to the host capabilities required by the selected skill |
| Coordinated local delivery controller | **macOS + Codex CLI** |
| Controller prerequisites | **Python 3.11+**, Git, an authenticated Codex CLI, and the required P2P stage skills |
| GitHub | Optional. It can be used for issue import, planning handoffs, completion records, and PR workflows, but local planning and delivery do not require it |
| P2P project state | Generated project-local records live under ignored `.p2p/`; active controller execution and recovery state lives outside the source checkout |

If the coordinated host cannot establish fresh stage contexts, protect the fixed
candidate and agreement during verification, or retain the required handoffs, P2P
blocks instead of quietly weakening review or proof. See the
[delivery controller guide](./docs/p2p-delivery-controller.md) for the exact current
host assumptions and checks.

## 5-minute quick start

This is the shortest path from “I have a small change” to a real P2P delivery.
For a complete walkthrough with explanations and a concrete example, use
[Getting Started](./docs/getting-started.md).

### 1. Install the skills

```bash
npx skills@latest add grove/promise-to-proof
```

### 2. Set up your project

From the project you want P2P to work on, run:

```text
/setup-promise-to-proof
```

Setup creates the ignored local P2P workspace and checks the repository's ignore
rules. It does **not** require GitHub, and it does not take over project-owned
`specs/` or `work/` directories.

### 3. Turn a small promise into an acceptance contract

You can start from an issue, a project document, or simply agreed text:

```text
/plan-acceptance "Reject an empty username with a clear validation error."
```

P2P turns that informal outcome into a saved acceptance contract under
`.p2p/work/<slug>/contract.md`. The contract says what must be true, what would
falsify it, and what evidence should establish it. Inspect the proposal and approve
the exact agreement before implementation proceeds.

### 4. Deliver the saved contract

Use the exact path returned by planning:

```text
/deliver-issue .p2p/work/<slug>/contract.md
```

The coordinated path implements the contract, freezes an exact candidate, runs
independent implementation review and proof, and returns either matching
`REVIEWED` + `PROVEN` results or a specific blocker/gap that still needs work.

### 5. Read the result correctly

A successful delivery separates three claims:

```text
IMPLEMENTED  → the candidate is ready for independent scrutiny
REVIEWED     → the implementation passed independent engineering/scope review
PROVEN       → the promised behavior has credible evidence on that exact candidate
```

Those claims are deliberately not interchangeable. A later candidate change can
make an older review or proof inapplicable; green CI alone does not prove every
promise; and acceptance does not itself authorize a commit, push, publication,
merge, or deployment.

**Ready to try the whole flow with a tiny example?** Follow
[Your first Promise to Proof delivery](./docs/getting-started.md).

## Which path should I use?

Most work should begin with the first row. The other paths are there when the shape
of the work actually requires them.

| I have… | Start here |
|---|---|
| An agreed outcome | `/plan-acceptance` → P2P recommends the next route |
| A GitHub issue | `/plan-acceptance <issue>` → follow the saved P2P recommendation |
| A project specification | `/plan-acceptance <path>` → direct delivery or sizing inspection |
| A sizing inspection recommended after planning | Plan the parent → `/slice-contract` |
| A proven candidate that should become a draft PR | `/publish-pr` |
| An existing PR near the merge decision | `/merge-readiness` |
| A failed PR workflow | `/fix-pr` |

You do not need to choose direct delivery or slicing in advance. After
`plan-acceptance` establishes the outcome, it recommends direct delivery for a
manageable unit or `/slice-contract` when sizing needs inspection. `NO SPLIT` is
a normal result. Direct delivery still passes through `/deliver-issue` and its
#60 admission before implementation.

The [HOW-TO](./docs/how-to.md) covers these task-oriented paths in more detail.

## A few P2P terms, in plain language

**Acceptance contract** — the written definition of what must be true before the
work counts as delivered. P2P gives each independently checkable promise a stable
requirement ID and records its important boundaries, observation seam, expected
result, and planned evidence.

**Candidate** — the exact version of the implementation being reviewed and proven.
A moving branch name is not enough; P2P binds results to a full commit or a
reproducible snapshot.

**Review** — the independent engineering check. It asks whether the candidate is
faithful to the contract, stays in scope, and is sound enough to hand forward.

**Proof** — evidence that the promised behavior actually holds on that exact
candidate. Proof evaluates the contract requirement by requirement; it does not
repair the implementation.

**Comparison base** — the exact project version P2P compares the delivery against.
The coordinated controller freezes that base at admission instead of silently
changing it when the destination branch moves later.

For the precise rules behind these terms, read the
[acceptance contract protocol](./docs/acceptance-contract-protocol.md).

## The core workflow

### Plan what “done” means

[`/plan-acceptance`](./skills/productivity/plan-acceptance/SKILL.md) turns a
ticket, specification, or agreed outcome into a versioned acceptance contract. It
separates observable promises, keeps speculative behavior out of scope, and names
credible evidence paths before implementation begins.

An optional
[`/audit-acceptance`](./skills/productivity/audit-acceptance/SKILL.md) can
independently inspect one exact proposed contract before a human approval decision.

### Implement the agreement

[`/implement-contract`](./skills/productivity/implement-contract/SKILL.md)
builds the smallest complete solution inside the approved contract. It does not get
to silently redefine the promise, approve its own candidate, or claim proof.

### Review and prove independently

[`/review-implementation`](./skills/productivity/review-implementation/SKILL.md)
asks whether the implementation is faithful, appropriately scoped, and
engineering-sound.

[`/prove`](./skills/productivity/prove/SKILL.md) separately asks whether every
material promised outcome has credible evidence on that same fixed candidate.

For ordinary one-item delivery,
[`/deliver-issue`](./skills/productivity/deliver-issue/SKILL.md) coordinates
those handoffs and preserves the identities needed to resume safely after
interruption.

## More capabilities, when you need them

You do not need to learn these before your first delivery. They exist for specific
situations that appear later in real work.

<details>
<summary>Show the wider P2P skill set</summary>

| Skill | Use it when |
|---|---|
| [`/setup-promise-to-proof`](./skills/productivity/setup-promise-to-proof/SKILL.md) | A repository needs ignored local P2P storage and optional tracker/domain pointers |
| [`/audit-acceptance`](./skills/productivity/audit-acceptance/SKILL.md) | A proposed contract needs an independent pre-approval check |
| [`/slice-contract`](./skills/productivity/slice-contract/SKILL.md) | One parent contract is too large for one coherent delivery |
| [`/repair-gaps`](./skills/productivity/repair-gaps/SKILL.md) | Proof found named repairable gaps |
| [`/publish-pr`](./skills/productivity/publish-pr/SKILL.md) | A reviewed and proven candidate should become a draft PR |
| [`/merge-readiness`](./skills/productivity/merge-readiness/SKILL.md) | An existing PR is near a merge decision |
| [`/fix-pr`](./skills/productivity/fix-pr/SKILL.md) | A pull request workflow failed |
| [`/retrospect`](./skills/productivity/retrospect/SKILL.md) | A proven delivery has concrete experience worth learning from |
| [`/triage-issue`](./skills/productivity/triage-issue/SKILL.md) | A tracker issue needs a next action or triage label |
| [`/create-parent-issue`](./skills/productivity/create-parent-issue/SKILL.md) | A local specification needs an optional GitHub source issue |
| [`/critique`](./skills/productivity/critique/SKILL.md) | You want an independent assessment of a proposal |
| [`/interrogate`](./skills/productivity/interrogate/SKILL.md) | You want to question the agent's proposal and reasoning |

</details>

## Where P2P keeps its state

For normal project use, the simple rule is:

> **P2P keeps generated project-local workflow records under ignored `.p2p/`, so
> they do not pollute your product history.**

Acceptance contracts and compact final records use
`.p2p/work/<slug>/`. Temporary project-local scratch may use `.p2p/tmp/`.
The coordinated controller keeps its active candidate workspace, invocation
records, reports, and recovery state outside the checkout under the user-level P2P
execution root. That lets interrupted delivery resume without mixing controller
state into the product tree.

You only need the deeper storage rules when debugging, migrating older state, or
operating the controller directly. See the
[controller guide](./docs/p2p-delivery-controller.md) and
[state migration guide](./docs/p2p-state-migration.md).

## What P2P does — and does not — establish

P2P is intentionally careful about the claims it makes. A matching review and
proof say something strong about **one exact agreement and one exact candidate**.
They do not prove that every future change is safe, that every possible environment
has been explored, or that the repository is automatically ready to merge.

Likewise, a test suite is evidence only to the extent that its checks actually
establish the promised outcomes. P2P prefers behavioral evidence through real
interfaces and independent expected results, while still allowing other credible
evidence paths for work that is not naturally test-driven.

The project also has model-based and deterministic checks for controller
invariants, artifact identity, restart behavior, and other workflow properties.
Those checks strengthen the orchestration layer; they do not magically prove the
quality of every future agent judgment. See the
[delivery-model documentation](./checks/delivery-model/README.md) for the exact
scope of those checks.

## Project status

P2P currently has an executable local delivery controller, durable acceptance
handoffs, independent review/proof stages, bounded repair and resume behavior,
compact completion records, deterministic artifact checks, and a bounded FizzBee
delivery model with conformance tests.

The current production controller path is macOS + Codex CLI. Work on broader host
portability is tracked separately so new adapters can preserve the same
`REVIEWED` and `PROVEN` meanings rather than creating weaker host-specific
workflows. Fixed delivery-strategy comparison and further optimization work remain
separate from the assurance semantics.

## Documentation

**New here?** Start with
[Getting Started](./docs/getting-started.md). It walks through one complete small
delivery and explains what each stage is doing while you use it.

**Know the basics and need a recipe?** Use the
[HOW-TO](./docs/how-to.md) for issues, slicing, publication, repair, recovery, and
other task-oriented paths.

**Have a conceptual question?** Read the [FAQ](./docs/faq.md) for the difference
between review and proof, candidate identity, parent/child acceptance, merge
readiness, and other common questions.

**Need the exact rules?** The
[acceptance contract protocol](./docs/acceptance-contract-protocol.md) defines
agreement ownership, revisions, candidate identity, evidence, durable handoffs,
and applicability. The
[delivery controller guide](./docs/p2p-delivery-controller.md) documents the
current direct controller environment and operations.

Additional references:

- [Detailed Promise to Proof workflow](./docs/promise-to-proof.md)
- [Evidence Record v1](./docs/evidence-record-v1.md)
- [Acceptance Bundle v1](./docs/acceptance-bundle-v1.md)
- [State migration](./docs/p2p-state-migration.md)
- [Delivery strategy comparison](./docs/delivery-strategy-comparison.md)

## Repository structure

```text
skills/productivity/   P2P skills
docs/                  user, workflow, and protocol documentation
checks/                deterministic, scenario, model, and conformance checks
specs/                 project-owned specifications used by this repository
plans/                 project planning material
```

Each skill has a `SKILL.md`. Shared protocol references resolve to the canonical
documentation so individual skill installs keep the rules they depend on.

Run the repository's Python checks with:

```bash
python3 -m unittest discover -s checks -p 'test_*.py'
```

The model/conformance checks and live host checks have additional pinned
requirements documented in their own guides.

## Contributing

Please read [CONTRIBUTING.md](./CONTRIBUTING.md) before starting work. This project
uses an issue-first contribution model, and substantial pull requests should follow
an agreed issue and maintainer invitation.

## License

Apache-2.0. See [LICENSE](./LICENSE).
