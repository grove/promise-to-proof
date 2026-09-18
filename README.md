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
The agent immediately exposes its posture in a structured opening statement:
- **What it believes is true**
- **What it proposes doing**
- **What assumptions the proposal depends on**
- **What it is uncertain about**
- **What alternatives it considered**
- **What evidence would cause it to change its mind**
- *1–2 sharp, concrete follow-up questions highlighting key tradeoffs*

### 3. The Cross-Examination
You attack the proposal. The agent adheres to strict rules of engagement:
- **Direct answers only**: No evasion, topic-broadening, or generic deflections.
- **Structured claims**: Break down responses into *Claim*, *Why*, *Evidence*, *Assumptions*, *Uncertainty*, *Alternatives*, and *Consequence*.
- **Autonomous fact-finding**: The agent inspects code, tools, and docs itself—it never burdens you with questions it can answer with codebase tools.
- **No defensive pride**: If an assumption is busted, it admits it immediately and updates its position.
- **Sharp technical follow-ups**: Instead of *"What do you think?"*, it asks probing questions like *"Given S3 write latency, does your workload tolerate 100ms or 2s freshness?"*.

### 4. The Verdict
When you are satisfied or say wrap up, the session concludes with a concise synthesis:
1. What survived the interrogation
2. What changed
3. What remains uncertain
4. The final, robust implementation plan

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
