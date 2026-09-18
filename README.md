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

A quick 2-minute design review that cuts through ambiguity, verifies in code, and closes the loop:

```text
User:   /interrogate How should we make the Rockstream storage layer scale to multi-terabyte state?

Agent:  Inspecting crates/rockstream-storage/src...

        Proposed Approach:
        Keep active differential traces (L0/L1 spines) in memory for sub-millisecond frontier steps, 
        and offload compacted, immutable historical batches to SlateDB/object storage asynchronously.

        Key Assumptions & Tradeoffs:
        • Frontier progression can tolerate background compaction latency without stalling pipelines.
        • Cache misses on cold tiered storage will add 20–50ms latency on historical joins.

        Recommendation:
        Support both memory-first and tiered storage via per-view configuration:
        `WITH (residency = 'memory_only' | 'tiered')`.

User:   Makes sense. Let's make tiered the default, but memory_only for real-time views. Go ahead and build it.

Agent:  Perfect. That keeps the hot path sub-millisecond while protecting overall RAM limits.

        Agreed Plan:
        1. Add ResidencyPolicy enum to storage config (default: Tiered).
        2. Route memory_only views directly to in-memory spine bypass in shard_db.rs.
        3. Verify with `cargo test -p rockstream-storage`.

        [Applies changes to crates/rockstream-storage/src/shard_db.rs]
        [Runs `cargo test -p rockstream-storage`]

        Verification complete: 14 passed, 0 failed.
        • Added ResidencyPolicy with Tiered and MemoryOnly variants.
        • Verified bypass path. All unit tests green. Ready to review.
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

```text
  ┌────────────────────────────────────────────────────────┐
  │ 1. Trigger: `/interrogate <goal or proposal>`          │
  └───────────────────────────┬────────────────────────────┘
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 2. Agent inspects code & presents concrete proposal    │
  │    (Approach • Assumptions • Tradeoffs • Blocking Qs)  │
  └───────────────────────────┬────────────────────────────┘
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 3. You stress-test, adjust, or challenge the plan      │
  │    (Agent adapts without ego, defense, or sycophancy)  │
  └───────────────────────────┬────────────────────────────┘
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 4. Bounded Convergence (by Turn 5)                     │
  │    (Stops branching • Summarizes plan & tradeoffs)     │
  └───────────────────────────┬────────────────────────────┘
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 5. Authorized Implementation & Verification            │
  │    (Apply changes • Run tests/checks • Close loop)     │
  └────────────────────────────────────────────────────────┘
```

---

## 📦 Installation & Usage

### 1. Install via `skills.sh`

```bash
# Add all skills from this repository
npx skills@latest add grove/skills

# Or install only interrogate
npx skills@latest add grove/skills --skill interrogate
```

### 2. Update to Latest

```bash
npx skills@latest update interrogate
```

### 3. Use in Your Chat

Type `/interrogate` in any supported AI assistant:

```text
/interrogate Should we migrate from WebSockets to Server-Sent Events for live dashboard updates?
```
*(or simply say: "Let's interrogate your proposal before writing any code.")*

---

## 🗂️ Repository Structure

```text
skills/
├── productivity/
│   └── interrogate/
│       ├── SKILL.md             # Core skill instructions
│       └── agents/
│           └── openai.yaml      # Harness compatibility metadata
├── README.md                    # Documentation & guides
└── LICENSE                      # Apache-2.0
```

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
