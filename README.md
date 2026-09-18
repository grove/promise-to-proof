# Skills

[![skills.sh](https://skills.sh/b/grove/skills)](https://skills.sh/grove/skills)

A collection of agent skills for AI coding assistants and agents (Claude Code, Codex, Antigravity, Amp, Cline, Cursor, and more).

## Installation

Install using [`skills.sh`](https://skills.sh/):

```bash
# Install interactively or pick skills
npx skills@latest add grove/skills

# Install the interrogate skill directly
npx skills@latest add grove/skills --skill interrogate
```

To update installed skills:

```bash
npx skills@latest update interrogate
```

---

## Skills

### Productivity

- [**`interrogate`**](./skills/productivity/interrogate/SKILL.md) — Let the user interrogate the agent's understanding, proposal, design, or reasoning until they are satisfied it holds up.
  - *Opposite of [`grill-me`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me)*: In `grill-me`, the agent interviews the user. In `interrogate`, the user is the interrogator and the agent is the witness—exposing assumptions, uncertainties, and reasoning so the user can challenge them.

---

## License

[Apache-2.0](./LICENSE)
