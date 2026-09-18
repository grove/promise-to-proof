# Skills

[![skills.sh](https://skills.sh/b/grove/skills)](https://skills.sh/grove/skills)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](./LICENSE)

A curated collection of agent skills for AI coding assistants (Claude Code, Codex, Antigravity, Amp, Cline, Cursor, and more).

---

## The Spotlight Skill: `interrogate`

> **Stop your coding agent from running off with half-baked assumptions. Put it on the witness stand.**

### Why `interrogate`?

In standard workflows or interview skills like [`grill-me`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me), the agent interviews **you** to clarify requirements. 

**`interrogate` reverses the courtroom.**

When an agent proposes a complex architecture, a non-trivial refactor, or a bug diagnosis, it often hides fragile assumptions behind polite, confident prose. When casually challenged, models either defensively double down or sycophantically flip 180°.

`interrogate` forces the agent into the role of an **expert witness under cross-examination**:

| Dimension | `grill-me` | `interrogate` |
| :--- | :--- | :--- |
| **Interrogator** | The Agent | **The User (You)** |
| **On the Stand** | The User | **The Agent** |
| **Goal** | Extract what *you* want built | Stress-test what the *agent* thinks and plans |
| **Target** | Ambiguous user requirements | Shaky agent assumptions, hidden risks, hallucinations |
| **Output** | Requirements tree | Battle-tested implementation plan & verified facts |

---

## What It Enables (Possibilities & Use Cases)

### 1. Architectural Stress-Testing
Before committing to an expensive redesign, data model change, or distributed pipeline:
- Demand the agent list its core claims, hidden prerequisites, and discarded alternatives.
- Challenge latency, consistency, or cost assumptions. The agent must defend them or concede and pivot.

### 2. Root-Cause Diagnosis Cross-Examination
When an agent diagnoses an elusive production bug or performance regression:
- Force the agent to present **observed evidence** (logs, profiler outputs, git bisect) rather than inferences.
- The skill forbids the agent from presenting an inference as a fact or asking you to check things it can inspect itself.

### 3. Pre-Implementation Risk Verification
Before letting an agent write 500 lines of speculative code:
- Probe the edge cases: *"What happens if the upstream stream drops out?"*, *"How does this migration handle zero-downtime rollbacks?"*
- Walk away with a clear ledger of which design claims survived scrutiny and which were revised.

---

## How It Works in Practice

### 1. Trigger the Skill
Invoke the skill directly in your agent:

```text
/interrogate
```
*(or tell the agent: "Let's interrogate your proposal before writing any code.")*

### 2. The Agent Takes the Stand
The agent immediately exposes its posture in a compact opening statement:
- **Goal & Stance**: What it proposes doing to achieve your objective.
- **Key Assumptions**: What must hold true for this to work.
- **Uncertainty & Alternatives**: Key unknowns and why alternative options were discarded.
- **Falsifiability**: What evidence or constraint would change its mind.
- *1 sharp, concrete tradeoff question to kick off the interrogation.*

### 3. The Cross-Examination
You attack the proposal. The agent adheres to strict rules of engagement:
- **Hard brevity budget**: Every response is under 150 words or 3–4 bullet points with zero conversational filler.
- **Direct answers first**: Answers the question in the very first sentence without evading.
- **Lean format**: Breaks down responses into *Stance*, *Evidence* (observed code vs inference), and *Risk/Consequence*.
- **Autonomous fact-finding**: Inspects the codebase, tools, and git history itself—never asking you to look up facts it can check.
- **Zero defensive pride**: Concedes invalid assumptions immediately and pivots without excuses.
- **Targeted technical follow-ups**: Max 1 concrete tradeoff question (e.g., *"Can this pipeline tolerate 2s read lag, or is read-after-write consistency required?"*).

### 4. Direct Handoff to Action
When you are satisfied or say wrap up, the session concludes with an immediate transition to work:
1. **Settled Plan**: The design that survived scrutiny.
2. **Discarded / Revised**: Assumptions and options dropped during the session.
3. **Next Step**: An immediate, actionable implementation step or diff ready to run.

---

## Installation

Install using [`skills.sh`](https://skills.sh/):

### Interactive / Pick Skills
```bash
npx skills@latest add grove/skills
```

### Install `interrogate` Directly
```bash
npx skills@latest add grove/skills --skill interrogate
```

### Update Skills
```bash
npx skills@latest update interrogate
```

Compatible with:
- [Claude Code](https://claude.ai/code)
- [Antigravity](https://github.com/google-deepmind)
- [Codex](https://github.com/openai/codex)
- [Amp](https://ampcode.com)
- [Cline](https://github.com/cline/cline)
- [Cursor](https://www.cursor.com)
- Any harness compatible with [Agent Skills](https://skills.sh)

---

## Repository Structure

```text
skills/
├── productivity/
│   └── interrogate/
│       ├── SKILL.md             # The core interrogation instructions
│       └── agents/
│           └── openai.yaml      # Harness compatibility metadata
├── README.md                    # This guide
└── LICENSE                      # Apache-2.0
```

---

## Contributing & Feedback

Have suggestions for improving `interrogate` or want to add complementary skills? Open an issue or submit a pull request on [GitHub](https://github.com/grove/skills).

## License

[Apache-2.0](./LICENSE)
