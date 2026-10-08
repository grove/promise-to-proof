# Getting started: your first Promise to Proof delivery

This guide takes you through one complete Promise to Proof delivery from a small
human promise to matching `REVIEWED` and `PROVEN` results. You do not need to
understand the acceptance protocol, recovery model, publication workflow, or the
full P2P skill set before you begin. Those pieces are important, but they make much
more sense after you have seen the basic loop work once.

The mental model to keep in your head is simple:

```text
PROMISE
   ↓
make "done" precise
   ↓
IMPLEMENT
   ↓
REVIEW + PROVE
   ↓
DELIVER
```

For this walkthrough, imagine your project already has a public way to create or
validate usernames, and you want one small behavior:

> **Empty usernames must be rejected with a clear validation error.**

If your project has no username concept, use any similarly small real change from
your own repository. The important thing is to choose one coherent outcome that is
easy to observe. Your first P2P delivery is a much better place to learn the
workflow than to tackle a large migration, a multi-service feature, or an epic that
needs slicing.

## Before you start

The production-validated coordinated controller currently runs on **macOS with
Codex CLI**. Direct controller execution also requires **Python 3.11+**, Git, an
authenticated Codex CLI, and the P2P stage skills. Standalone skills are packaged
for agent-skill-compatible tools, but this tutorial assumes the coordinated setup
so that implementation, independent review, and proof can all run as one delivery.

GitHub is optional. You can complete this entire tutorial from a local agreed
outcome without creating or updating an issue.

P2P will keep generated project-local workflow records under ignored `.p2p/`.
That directory is for P2P state, not product code. Active controller execution and
recovery state lives outside the source checkout so a long or interrupted delivery
can resume without mixing orchestration state into your repository.

That external storage must be writable from the session doing the work. The
default is `~/.p2p/executions`; for new work, `P2P_EXECUTION_ROOT` may select
another persistent, absolute directory outside the source checkout. Delivery
checks access before implementation and retains the chosen location. Publication
checks its own session's access before requesting approval, including both the
candidate workspace and its separate Git directory. See the
[storage and access instructions](./p2p-delivery-controller.md) for the commands.

If you want the exact host and controller details before continuing, read the
[delivery controller guide](./p2p-delivery-controller.md). Otherwise, the steps
below are enough for a normal first run.

## Step 1: install Promise to Proof

Install the full skill collection:

```bash
npx skills@latest add grove/promise-to-proof
```

### What you are doing

You are installing the P2P skills that plan the acceptance contract, implement the
agreement, independently review the candidate, prove the promised behavior, and
coordinate those stages.

### What P2P is doing

Nothing has changed in your project yet. Installing the skills makes the workflow
available to your coding agent; it does not modify the repository, create issues,
or authorize publication.

### What you should expect afterward

Your host should be able to discover P2P skills such as
`/setup-promise-to-proof`, `/plan-acceptance`, and `/deliver-issue`. If your
host cannot discover them, fix that before continuing rather than trying to work
around the missing stage definitions.

## Step 2: set up the repository

Open the repository you want P2P to work on and run:

```text
/setup-promise-to-proof
```

### What you are doing

You are giving P2P a safe local place to keep its generated contracts, compact
records, and temporary workflow data.

### What P2P is doing

Setup creates `.p2p/work/` and `.p2p/tmp/` if they do not already exist and
makes sure `/.p2p/` is ignored by Git. It preserves existing project files and
configuration. It does not create project-owned `specs/` or `work/`
directories, and it does not require a tracker.

If your repository already has GitHub or project-domain conventions, setup can
record pointers to those conventions without turning GitHub into a requirement for
local delivery.

### What you should expect afterward

The important result is simple: `.p2p/` is available for P2P and ignored by Git.
A repeat setup with the same configuration should be harmless rather than creating
a second competing setup.

You can verify the core idea yourself:

```text
product code and tests → normal repository history
P2P working state     → ignored .p2p/
Portable checkpoints  → p2p-state/<slug>.json (Git), or a selected GitHub issue
```

## Step 3: start with one small promise

Now give P2P the outcome you want:

```text
/plan-acceptance "Reject an empty username with a clear validation error."
```

You can also plan from a project document or a tracker issue, but direct agreed
text is the cleanest first example.

### What you are doing

You are not asking the agent to code yet. You are asking it to turn an informal
request into a precise agreement about what must be true before the work counts as
delivered.

This separation is one of the most important ideas in P2P. If implementation
begins while “done” is still vague, the coding agent can accidentally decide the
meaning of the request while it is already building the solution. P2P makes that
agreement explicit first.

### What P2P is doing

`/plan-acceptance` reads the relevant repository context and turns the promise
into independently checkable requirements. It records the important boundaries,
where the behavior can be observed, what the expected result is, and what evidence
should establish it. It also keeps unrelated behavior out of scope.

The generated contract is saved at:

```text
.p2p/work/<slug>/contract.md
```

Use the exact path P2P returns. The slug is derived from the work item and should
not be guessed when another path has already been reported.

### What you should expect afterward

The real contract is more structured than this, but a simplified view of this
example might look like:

```text
R1 — Empty usernames are rejected.
Expected:
The normal username-creation path returns the agreed validation failure for an
empty username.

R2 — Valid usernames still succeed.
Expected:
Existing valid username behavior remains unchanged.
```

A real P2P row also records boundaries or counterexamples, the observation seam,
an independent oracle, and the planned evidence. The point is not to create more
paperwork. The point is to make it hard for “implemented something nearby” to be
confused with “delivered the promise.”

If planning discovers a real product decision that could change correctness or
scope, it should surface that question instead of guessing. Resolve the question
before implementation. If it finds only an evidence gap, it should tell you what
observation path is missing.

## Step 4: inspect and approve the agreement

Read the proposed contract before you let implementation continue.

You are looking for a straightforward question:

> **If every requirement in this contract were true, would I agree that my
> original promise had been delivered — without adding behavior I did not ask for?**

### What you are doing

You are approving the meaning of the work, not approving an implementation. This
is the moment to correct a missing requirement, a wrong boundary, or an accidental
scope expansion while doing so is still cheap.

Approval should apply to the exact proposal you inspected. Generating a contract
does not approve it, an audit does not approve it, and a tracker label does not
approve it.

### What P2P is doing

P2P preserves the contract revision, requirement identities, and exact agreement
needed by later stages. That lets implementation, review, and proof talk about the
same promise even if the conversation is long, the delivery is interrupted, or a
later stage runs in a fresh context.

### What you should expect afterward

You should have one canonical saved contract under
`.p2p/work/<slug>/contract.md`, with no unresolved decision that would materially
change the work. If the contract needs a material change later, P2P treats that as
an agreement revision rather than silently rewriting history.

For a first local delivery, you do not need a planning PR or a GitHub issue.

## Step 5: deliver the contract

Now hand the saved agreement to the coordinated workflow:

```text
/deliver-issue .p2p/work/<slug>/contract.md
```

Again, use the exact contract path returned by planning.

### What you are doing

You are asking P2P to carry one agreed work item through implementation,
independent review, and proof. You are not manually telling each stage what the
previous stage said; the saved contract and candidate handoffs carry that context.

### What P2P is doing

At a high level, coordinated delivery does this:

```text
approved contract
      ↓
implement the smallest complete solution
      ↓
freeze the exact candidate
      ↓
independent review ──┐
                     ├─ same contract + same candidate
independent proof  ──┘
      ↓
REVIEWED + PROVEN
```

The implementation stage builds against the approved contract. When it has a
candidate ready for scrutiny, P2P identifies that exact candidate rather than
relying on a moving branch name.

Review and proof then run independently against the fixed inputs. Review asks
whether the implementation is faithful to the agreement, stays in scope, and is
engineering-sound. Proof asks whether credible evidence actually establishes every
material promised outcome.

The controller continues autonomously through scoped repairs and rechecks, with
unlimited duration and attempts by default. Repeated gaps trigger fresh diagnosis
and a different approach. Explicit limits remain available. A standing mandate
can also delegate planning and exact publication or merge effects, so the outer
workflow can apply its recommendations without repeated approval. Independent
review and proof still must establish the complete agreed outcome. See
[controller options and mandates](p2p-delivery-controller.md#standing-mandates).

### What you should expect afterward

A successful run conceptually ends with:

```text
IMPLEMENTED
REVIEWED
PROVEN
```

If something is missing, P2P should return a specific blocker or gap with
recoverable state rather than pretending the delivery succeeded.

The words mean different things:

**IMPLEMENTED** means the implementation stage believes the exact candidate is
ready for independent scrutiny. It is not self-approval.

**REVIEWED** means independent implementation review found the candidate faithful
to the contract, appropriately scoped, and acceptable on its engineering
obligations for that review.

**PROVEN** means every material requirement has credible evidence on the exact
candidate and agreement being evaluated, with no unresolved discrepancy.

That separation is useful in practice. A candidate can be well engineered but fail
the promised behavior. It can also appear to satisfy the visible behavior while an
independent review finds a serious scope, integrity, compatibility, or
maintainability problem.

## Step 6: understand the exact-candidate rule

This is the one “strict” idea worth learning early because it explains much of
P2P's design.

Suppose review and proof both examine candidate A:

```text
candidate A → REVIEWED
candidate A → PROVEN
```

If the implementation later changes into candidate B, the old reports do not
magically become reports about B:

```text
candidate B ≠ automatically REVIEWED
candidate B ≠ automatically PROVEN
```

P2P therefore records a full commit identity or another reproducible candidate
snapshot. It also keeps the exact contract and comparison base needed to interpret
the result. This prevents a common failure mode where a project says “the code was
reviewed” even though the reviewed code is no longer the code being accepted.

You do not need to manage those identities by hand during normal coordinated
delivery. The controller does that work so the result remains meaningful.

## Step 7: know what success does not authorize

A `REVIEWED + PROVEN` delivery is evidence-backed acceptance of one exact
candidate under one exact agreement. It is not blanket permission to perform every
next action.

P2P deliberately keeps authority separate. A successful local delivery does not,
by itself, authorize a commit, push, tracker update, pull request, merge, or
deployment. Those effects belong to separately authorized workflows such as
`/publish-pr` and, later, the repository's real merge process.

Likewise, `PROVEN` does not mean regressions are impossible forever. It means the
promised behavior has credible evidence on the candidate that was actually proven.
Long-lived repository tests and other durable guards still matter because future
changes create new candidates.

## The four terms you now know

After one delivery, most of P2P becomes easier to understand because four words
have concrete meaning:

**Acceptance contract** — the saved definition of what must be true before the
work counts as delivered.

**Candidate** — the exact implementation version being reviewed and proven.

**Review** — the independent engineering and scope check.

**Proof** — the evidence-backed check that the promised behavior actually holds.

You will also see **comparison base**, which simply means the exact project version
P2P compares the delivery against. The controller freezes it for the delivery so a
moving target branch does not silently change what the result means.

## Which path should you use next?

The normal one-item path should remain your default until the work itself gives you
a reason to choose something else.

| What you have | Good next path |
|---|---|
| Another small local outcome | `/plan-acceptance` → `/deliver-issue` |
| An existing GitHub issue | `/plan-acceptance <issue>` → `/deliver-issue <issue>` |
| A project specification | `/plan-acceptance <path>` |
| One contract that is genuinely too large for one coherent delivery | `/slice-contract` after planning the parent |
| A reviewed and proven candidate that should become a draft PR | `/publish-pr` |
| An existing PR approaching the merge decision | `/merge-readiness` |
| A proof report with named repairable gaps | `/repair-gaps`, followed by fresh proof |
| A failed PR workflow | `/fix-pr` |

Do not reach for slicing, repair, publication, or retrospective workflows simply
because they exist. P2P is easiest to use when the workflow stays proportional to
the work.

## Where to go from here

If you want practical recipes for issues, slicing, publication, repair, cleanup,
and recovery, continue with the [HOW-TO](./how-to.md).

If you have a conceptual question — for example, why review and proof are separate,
why candidate identity matters, or whether every child proof proves the parent —
use the [FAQ](./faq.md).

If you need the exact binding rules for agreement revisions, identities, evidence,
handoffs, and reuse, read the
[acceptance contract protocol](./acceptance-contract-protocol.md). That document is
the reference; this tutorial is intentionally the beginner path.

For direct controller commands, host preflight behavior, execution storage, resume,
status, and cleanup, use the
[delivery controller guide](./p2p-delivery-controller.md).

The important thing after your first run is not to memorize every P2P concept. It
is to keep the core habit:

> **Agree on what success means, build against that agreement, and only accept the
> exact implementation that independent review and evidence actually support.**
