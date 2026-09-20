# Skills

Practical agent skills for turning requirements into implementation, proof, and repair.

## Quick install

```bash
npx skills@latest add grove/skills
```

| Skill | Use it for |
|---|---|
| [`interrogate`](./skills/productivity/interrogate/SKILL.md) | Stress-test a design before implementation |
| [`acceptance-matrix`](./skills/productivity/acceptance-matrix/SKILL.md) | Turn promises into a testable checklist |
| [`prove`](./skills/productivity/prove/SKILL.md) | Verify a fixed candidate without changing it |
| [`repair-proof`](./skills/productivity/repair-proof/SKILL.md) | Repair named proof gaps and require fresh proof |
| [`fix-pr`](./skills/productivity/fix-pr/SKILL.md) | Repair failed PR workflows without weakening checks |

Typical workflow:

```text
Ticket/spec → acceptance-matrix → implementation → prove
           → repair-proof if needed → prove again → review
```

These skills preserve the source ticket's promises, make evidence explicit, and
keep unresolved requirements visible. They do not provide a workflow runtime.

## Use a skill

```text
/interrogate Should we use approach A or B?
/acceptance-matrix #123
/prove #123
/repair-proof #123
/fix-pr #456
```

Install one skill directly:

```bash
npx skills@latest add grove/skills --skill prove
```

Update an installed skill:

```bash
npx skills@latest update prove
```

## Repository structure

```text
skills/productivity/
├── acceptance-matrix/
├── fix-pr/
├── interrogate/
├── prove/
└── repair-proof/
```

Each skill has a `SKILL.md`. Some also have an `agents/openai.yaml` display
metadata file.

## Contributing

1. Fork the repository.
2. Create a branch.
3. Change the smallest relevant skill.
4. Run the checks described by that skill.
5. Open a pull request.

See [AGENTS.md](./AGENTS.md) for repository guidance.

## License

Apache-2.0. See [LICENSE](./LICENSE).
