# Skills

Practical agent skills for turning requirements into implementation, proof, and repair.

The skills are written for agent-skill-compatible coding tools. They keep the
source ticket's promises visible, make evidence explicit, and carry unresolved
questions into the next step. They do not provide a workflow runtime.

Follow [How to take a ticket from promise to proof](./docs/promise-to-proof.md)
for an end-to-end workflow that uses every skill in this repository.

Issues and specifications for this repository live in [GitHub Issues](https://github.com/grove/skills/issues).

## Choose a skill

| Skill | Use it when | It gives you |
|---|---|---|
| [`critique`](./skills/productivity/critique/SKILL.md) | You explicitly request an independent review of a proposal against its intended outcome | Evidence-backed advice and a recommendation |
| [`interrogate`](./skills/productivity/interrogate/SKILL.md) | A design needs stress-testing | An agreed approach, assumptions, and open decisions |
| [`acceptance-matrix`](./skills/productivity/acceptance-matrix/SKILL.md) | A ticket needs clear acceptance criteria | Stable requirements and evidence plans |
| [`prove`](./skills/productivity/prove/SKILL.md) | Implementation is ready to verify | `PROVEN` or `NOT PROVEN` with evidence |
| [`repair-proof`](./skills/productivity/repair-proof/SKILL.md) | Proof found a specific gap | A scoped repair report; fresh proof is still required |
| [`fix-pr`](./skills/productivity/fix-pr/SKILL.md) | A pull request's CI failed | `FIXED` or `NOT FIXED` for the target workflow |

## Typical workflow

Optionally invoke `critique` to assess an idea, issue, specification, plan, or
proposal before committing to it. Its advice requires no downstream skill.

```text
Ticket/spec → acceptance-matrix → implementation → prove
           → repair-proof if needed → prove again → review
```

1. **Plan acceptance.** Run `acceptance-matrix` on the ticket or specification.
   It turns broad promises into stable, observable requirements.
2. **Implement.** Build the requested behavior while keeping the matrix with the
   work.
3. **Prove.** Run `prove` against the fixed candidate. It checks the requirements,
   hunts realistic counterexamples, and reports the evidence.
4. **Repair only named gaps.** If proof is `NOT PROVEN`, pass its unresolved
   requirement IDs to `repair-proof`.
5. **Prove again.** A repair never counts as acceptance by itself. Review the
   changed candidate after fresh proof.

## Important boundaries

| Skill | Responsibility | Boundary |
|---|---|---|
| `critique` | Give optional, agent-led advice on a proposal | Does not edit the artifact, repository, or acceptance contract, publish findings, or implement |
| `acceptance-matrix` | Plan requirements and evidence | Does not implement or verify |
| `prove` | Verify one fixed candidate | Does not edit, commit, push, or publish |
| `repair-proof` | Repair named implementation or evidence gaps | Does not declare acceptance |
| `fix-pr` | Repair a failed PR workflow | Does not prove the whole ticket |
| `interrogate` | Reach a design decision | Does not imply implementation authority |

## What the results mean

- **PROVEN** means every material requirement has credible evidence, no contract
  discrepancy remains, and the candidate stayed fixed during verification.
- **NOT PROVEN** means evidence is missing, weak, unavailable, contradictory, or
  tied to the wrong candidate. It is a useful result, not a failure of the skill.
- **FIXED** means the target CI workflow was repaired and its required checks pass.
  It does not mean the ticket is fully proven.
- **NOT FIXED** means the workflow is still unresolved or verification could not
  establish a durable repair.

## Use a skill

```text
/critique <idea, document path, or GitHub issue reference>
/interrogate Should we use approach A or B?
/acceptance-matrix #123
/prove #123
/repair-proof #123
/fix-pr #456
```

The skills also accept direct ticket URLs or a specification when their skill
instructions describe that input.

## Install and update

Install the full collection:

```bash
npx skills@latest add grove/skills
```

Install one skill:

```bash
npx skills@latest add grove/skills --skill prove
```

Update one installed skill:

```bash
npx skills@latest update prove
```

## Repository structure

```text
skills/productivity/
├── acceptance-matrix/
├── critique/
├── fix-pr/
├── interrogate/
├── prove/
└── repair-proof/
```

Each skill has a `SKILL.md`. Some also have an `agents/openai.yaml` display
metadata file. The [`checks/`](./checks/) directory contains small, human-runnable
workflow checks.

## Contributing

1. Read [AGENTS.md](./AGENTS.md).
2. Find or create the relevant GitHub issue.
3. Change the smallest relevant skill.
4. Run the checks described by that skill.
5. Open a pull request that explains the behavior and evidence.

## License

Apache-2.0. See [LICENSE](./LICENSE).
