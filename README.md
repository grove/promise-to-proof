# ⚡ Skills

**Curated agent skills that turn AI coding assistants into sharper, pragmatic engineering partners.**

[![skills.sh](https://skills.sh/b/grove/skills)](https://skills.sh/grove/skills)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](./LICENSE)
[![Compatibility](https://img.shields.io/badge/Works%20with-Claude%20Code%20•%20Antigravity%20•%20Cursor%20•%20Codex-brightgreen)](https://skills.sh)

---

### Quick Install

```bash
# Add to your project or agent environment
npx skills@latest add grove/skills
```

Compatible out of the box with **Claude Code**, **Google Antigravity**, **Cursor**, **Codex**, **Amp**, **Cline**, and any harness supporting [Agent Skills](https://skills.sh).

The skills share one agreement: preserve the ticket's promises, identify what
success looks like, and carry evidence and unresolved gaps into the next step.

| Skill | Use it to | Result |
|---|---|---|
| [`interrogate`](./skills/productivity/interrogate/SKILL.md) | Stress-test a proposal and agree on changes | An agreed approach, explicit decisions, and checks for success |
| [`acceptance-matrix`](./skills/productivity/acceptance-matrix/SKILL.md) | Make a ticket's promises testable before implementation | Stable requirement IDs, observable results, evidence plans, and gaps |
| [`prove`](./skills/productivity/prove/SKILL.md) | Verify the implementation against the agreement without changing it | Every requirement reconciled with evidence and an overall `PROVEN` or `NOT PROVEN` verdict |
| [`repair-proof`](./skills/productivity/repair-proof/SKILL.md) | Repair named proof gaps | A scoped repair report that always requires fresh proof |
| [`fix-pr`](./skills/productivity/fix-pr/SKILL.md) | Repair failed PR workflows without weakening the agreement | `FIXED` or `NOT FIXED` for the workflow on the repaired commit |

A typical workflow is:

```text
Ticket or spec → /acceptance-matrix → implementation → /prove → /repair-proof if needed → /prove again → code review
```

Use `/interrogate` when the design needs discussion and `/fix-pr` when CI fails.
Each skill also works independently. `/to-spec`, `/to-tickets`, `/implement`, and
`/code-review` are optional integrations from other skill collections, not skills
shipped here.

Keep the outcome and matrix with the ticket or implementation plan. Later steps
account for every requirement ID, preserve required results, and report authorized
scope changes. Evidence may be replaced when it still establishes the same promise.
Unresolved requirements prevent declaring the ticket complete.

Matrix rows use `planned`, `proven`, `not proven`, or `disproven`. Only `/prove`
accepts a row as `proven`; its overall verdict is `PROVEN` or `NOT PROVEN`.
`FIXED` means CI was repaired, not that the whole ticket is proven. Proof records
the implementation state and environment; changes to requirements, code, or evidence
require reassessing affected verdicts. Code review still checks code quality.

These handoffs do not automatically invoke other skills or authorize publishing.
`/acceptance-matrix` produces a planning artifact. `/interrogate` implements only
when authorized, `/prove` only reports gaps, and `/repair-proof` handles scoped
repairs without declaring acceptance. Invoking `/fix-pr`
also authorizes scoped commit, push, and workflow reruns for its target.

---

## 🎯 Featured Skill: `interrogate`

> **Don't let your coding agent run off with half-baked assumptions.**  
> Put the design on the whiteboard first—stress-test it together, surface blind spots, and move straight to execution.

### Why `interrogate`?

Most agent workflows fall into one of two traps:
1. **The Speculative Sprint**: The agent writes 500 lines of complex code based on unstated, fragile assumptions that break the moment you test them.
2. **The Passive Interview** (e.g. `grill-me`): The agent interrogates *you* with long lists of basic clarifying questions instead of reading the code.

**`interrogate` flips the dynamic.**  
The agent autonomously checks the codebase, forms a concrete technical proposal, and presents its assumptions and tradeoffs transparently so you can poke holes in them.

| Dimension | `grill-me` | `interrogate` |
| :--- | :--- | :--- |
| **Who presents?** | You describe what you need | The agent presents a concrete design |
| **Who evaluates?** | The agent probes your requirements | **You** stress-test the agent's proposal |
| **Fact-checking** | Agent asks you for context | Agent autonomously inspects code, git & docs |
| **Tone** | Requirements questionnaire | Collegial, high-signal RFC / design review |
| **Outcome** | Long specification list | **Agreed architecture, verified code & closed loop** |

---

## ✨ See It in Action

An illustrative design review that separates implementation checks from outstanding scale and latency evidence:

```text
User:   /interrogate How should we make the Rockstream storage layer scale to multi-terabyte state?

Agent:  Inspecting crates/rockstream-storage/src...

        Proposed Approach:
        Keep active differential traces (L0/L1 spines) in memory, targeting sub-millisecond frontier steps,
        and offload compacted, immutable historical batches to SlateDB/object storage asynchronously.

        Key Assumptions & Tradeoffs:
        • Frontier progression can tolerate background compaction latency without stalling pipelines.
        • Historical join latency on cache misses needs measurement against the agreed latency budget.

        Recommendation:
        Support both memory-first and tiered storage via per-view configuration:
        `WITH (residency = 'memory_only' | 'tiered')`.

User:   Makes sense. Let's make tiered the default, but memory_only for real-time views. Go ahead and build it.

Agent:  I'll implement that policy. Hot-path latency and RAM use at multi-terabyte scale still need measurement.

        Agreed Plan:
        1. Add ResidencyPolicy enum to storage config (default: Tiered).
        2. Route memory_only views directly to in-memory spine bypass in shard_db.rs.
        3. Verify with `cargo test -p rockstream-storage`.
        4. Measure RAM use and latency under a representative multi-terabyte workload before claiming the scale goal is met.

        [Applies changes to crates/rockstream-storage/src/shard_db.rs]
        [Runs `cargo test -p rockstream-storage`]

        Unit tests: 14 passed, 0 failed.
        • Added ResidencyPolicy with Tiered and MemoryOnly variants.
        • Verified bypass path. Implementation ready to review.
        • Outstanding: multi-terabyte workload evidence for RAM use, frontier latency, and historical join latency.
          The scale goal and sub-millisecond hot-path target remain unverified.
```

---

## 💡 What It's Great For

### 🏗️ 1. Architecture Sanity-Checks
Before committing to an expensive refactor, database schema change, or new pipeline:
- Demand the agent reveal its hidden dependencies, resource limits, and discarded alternatives.
- Align on data structures and boundaries in 2 minutes instead of debugging for 2 hours.

### 🔍 2. Root-Cause Diagnosis Verification
When tracking down an elusive production bug or performance bottleneck:
- Insist on **observable evidence** (logs, profiler findings, git history) rather than probabilistic guesses.
- The skill forbids the agent from guessing or asking you to check files it can inspect itself.

### 🛡️ 3. Pre-Implementation Risk Reviews
Before letting an agent write large multi-file changes:
- Surface edge cases early: *"What happens during network partitions?"*, *"How does rollback behave?"*
- Agree on concrete automated tests and verification steps before editing code.

---

## 🚀 How It Works

`/interrogate` inspects the code, presents a proposal, incorporates feedback,
converges on a plan, then implements and verifies it when authorized. See the
[`interrogate` skill](./skills/productivity/interrogate/SKILL.md).

---

## 🎯 Featured Skill: `prove`

> **"Looks good to me" is not evidence.**  
> Map every material requirement in an issue to observable evidence, hunt concrete counterexamples, report gaps, and refuse to declare success until proven.

### Why `prove`?

Traditional code reviews and test suites leave dangerous blind spots:
- Diffs look clean and faithful to the spec, but a core negative requirement was never tested.
- Tests pass, but they mock the world so thoroughly that the system under test cannot realistically fail.
- Regressions hide in state transitions, idempotency gaps, or concurrency check-then-write boundaries.

**`prove` works from requirements to evidence, not from diff to opinions.**  
It reads the originating ticket, spec, or agreed conversation, reconciles any
existing acceptance matrix, audits evidence, and reports issue-scoped gaps.
Missing requirements are reported; existing promises cannot quietly disappear.

| Skill | Phase | Question |
| :--- | :--- | :--- |
| **`/interrogate`** | Design discussion | *Does the approach deliver the agreed outcome?* |
| **`/acceptance-matrix`** | Acceptance planning | *What must the PR deliver, and how will we check it?* |
| **`/prove`** | Acceptance verification | *Does the fixed candidate fulfill every promise?* |
| **`/repair-proof`** | Scoped repair | *Can we address a named proof gap without accepting the result?* |
| **`/fix-pr`** | CI repair | *Is the workflow repaired without weakening its checks or the ticket's promises?* |

---

### ✨ See It in Action

Verifying an issue resolution with independent falsification:

```text
User:   /prove #482

Agent:  Contract: Issue #482 — Retry failed payment capture
        R1. Failed captures can be retried.
        R2. Retry cannot result in a duplicate charge.
        R3. Original invoice association must survive retry.
        R4. Successful retry clears failure state.

        Auditing Evidence & Hunting Counterexamples...
        • R1: Verified by payment_retry_test.go.
        • R2: Existing check uses a weak mock. R2 is NOT PROVEN.
        • R3: No direct assertion found. R3 is NOT PROVEN.
        • R4: Verified by clear_failure_test.go.

        Running full verification suite (412 tests passed, 0 failed)...

        ============================================================
        NOT PROVEN — Issue #482
        Requirements: 2/4 demonstrated
        Counterexamples tested: 3 (2 evidence gaps reported)
        ============================================================
        No candidate changes made. Use /repair-proof for the named gaps, then run /prove again.
```

---

### 🛡️ The 8-Phase Proof Loop

`/prove` reads the contract, maps and audits evidence, hunts counterexamples,
reports issue-local gaps, verifies the fixed candidate, and reports `PROVEN` or
`NOT PROVEN`. See the [`prove` skill](./skills/productivity/prove/SKILL.md).

---

## 📦 Installation & Usage

### 1. Install via `skills.sh`

```bash
# Add all skills from this repository
npx skills@latest add grove/skills

# Or install individual skills
npx skills@latest add grove/skills --skill interrogate
npx skills@latest add grove/skills --skill acceptance-matrix
npx skills@latest add grove/skills --skill prove
npx skills@latest add grove/skills --skill repair-proof
npx skills@latest add grove/skills --skill fix-pr
```

### 2. Update to Latest

```bash
npx skills@latest update interrogate
npx skills@latest update acceptance-matrix
npx skills@latest update prove
npx skills@latest update repair-proof
npx skills@latest update fix-pr
```

### 3. Use in Your Chat

Invoke the skill for the work you need:

```text
/interrogate Should we migrate from WebSockets to Server-Sent Events for live dashboard updates?
```

```text
/acceptance-matrix #482
```

```text
/prove #482
```

```text
/repair-proof #482
```

```text
/fix-pr #123
```

---

## 🗂️ Repository Structure

```text
skills/productivity/
├── acceptance-matrix/
├── fix-pr/
├── interrogate/
├── prove/
├── repair-proof/
└── README.md
```

Each skill directory contains `SKILL.md` and `agents/openai.yaml`. List the
installed source files with `rg --files skills/productivity`.

---

## 🤝 Contributing

Have ideas for improving `interrogate` or want to contribute new skills?  
Pull requests and discussions are very welcome!

1. Fork the repository
2. Create your branch (`git checkout -b feature/my-skill`)
3. Commit your changes (`git commit -m "feat: add my-skill"`)
4. Push to your branch and open a Pull Request

---

## 📄 License

Distributed under the [Apache-2.0](./LICENSE) License.
