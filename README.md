# Skills

Practical agent skills for turning requirements into implementation, proof, and repair.

The skills are written for agent-skill-compatible coding tools. They keep the
source ticket's promises visible, make evidence explicit, and carry unresolved
questions into the next step. They do not provide a workflow runtime.

Follow [How to take a ticket from promise to proof](./docs/promise-to-proof.md)
for the workflow alongside Matt Pocock's planning, implementation, TDD, and
review skills. The [acceptance contract protocol](./docs/acceptance-contract-protocol.md)
defines the shared contract, revision, and proof rules.

Issues and specifications for this repository live in [GitHub Issues](https://github.com/grove/skills/issues).

## Choose a skill

| Skill | Use it when | It gives you |
|---|---|---|
| [`critique`](./skills/productivity/critique/SKILL.md) | You explicitly request an independent review of a proposal against its intended outcome | Evidence-backed advice and a recommendation |
| [`interrogate`](./skills/productivity/interrogate/SKILL.md) | You want to question the agent's proposal and reasoning | Evidence-backed answers, a revised approach, and explicit unknowns |
| [`acceptance-contract`](./skills/productivity/acceptance-contract/SKILL.md) | A ticket needs clear acceptance criteria | A candidate-independent revision with stable requirement IDs and evidence plans |
| [`prove`](./skills/productivity/prove/SKILL.md) | Implementation is ready to verify | `PROVEN` or `NOT PROVEN` with evidence |
| [`repair-proof`](./skills/productivity/repair-proof/SKILL.md) | Proof found a specific gap | A scoped repair report; fresh proof is still required |
| [`fix-pr`](./skills/productivity/fix-pr/SKILL.md) | A pull request's CI failed | `FIXED` or `NOT FIXED` for the target workflow |

## Typical workflow

Optionally invoke `critique` to assess an idea, issue, specification, plan, or
proposal before committing to it. Its advice requires no downstream skill.

```text
Ticket/spec → acceptance-contract → implementation → prove
           → repair-proof if needed → prove again → review
```

1. **Plan acceptance.** Run `acceptance-contract` on the ticket or specification.
   It records a revision such as `v1`, stable `R` IDs, boundaries, seams,
   independent oracles, and planned evidence. Plan state is `planned` or `gap`.
2. **Implement.** Use the existing implementation and TDD workflow to build the
   smallest complete change within the specification, including necessary
   invariants, state, failure handling, and persistence. Skip speculative machinery.
3. **Prove.** Bind the report to the exact contract revision and candidate. Each
   row gets `proven`, `disproven`, or `not proven` with durable evidence.
4. **Repair only named gaps.** If proof is `NOT PROVEN`, pass its unresolved
   requirement IDs to `repair-proof` for the smallest complete repair.
5. **Prove again.** A repair never counts as acceptance by itself. Review the
   changed candidate after fresh full proof of every row.

Keep requirement IDs stable. Increment the revision for authorized material
changes to promises, boundaries, outcomes, or exclusions. Evidence paths, test
paths, and wording changes that preserve meaning do not increment it. Reconcile
GitHub checkboxes with the contract, but never use them as proof.

## Important boundaries

| Skill | Responsibility | Boundary |
|---|---|---|
| `critique` | Give optional, agent-led advice on a proposal | Does not edit the artifact, repository, or acceptance contract, publish findings, or implement |
| `acceptance-contract` | Plan requirements and evidence | Does not implement or verify |
| `prove` | Verify one fixed candidate | Does not edit, commit, push, or publish |
| `repair-proof` | Repair named implementation or evidence gaps | Does not declare acceptance |
| `fix-pr` | Repair a failed PR workflow | Does not prove the whole ticket |
| `interrogate` | Let you examine the agent's proposal through questions | You lead the discussion; invocation does not grant implementation authority |

## What the results mean

- **PROVEN** means every material requirement has credible, durable evidence for
  the exact contract revision and candidate, with no unresolved discrepancy.
- **NOT PROVEN** means evidence is missing, weak, unavailable, contradictory, or
  tied to the wrong candidate. It is a useful result, not a failure of the skill.
- **FIXED** means the target CI workflow was repaired and its required checks pass.
  Green CI does not establish acceptance. Any changed candidate needs fresh
  full proof, including product, acceptance evidence, and relevant test changes.
- **NOT FIXED** means the workflow is still unresolved or verification could not
  establish a durable repair.

## Use a skill

```text
/critique <idea, document path, or GitHub issue reference>
/interrogate Walk me through your proposal so I can question it.
/acceptance-contract #123
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
├── acceptance-contract/
├── critique/
├── fix-pr/
├── interrogate/
├── prove/
└── repair-proof/
```

Each skill has a `SKILL.md`. Some also have an `agents/openai.yaml` display
metadata file. The [`checks/`](./checks/) directory contains small, human-runnable
workflow checks.

Shared protocol references are symlinks to `docs/acceptance-contract-protocol.md`.
The installer copies their contents into each selected skill, so individual
installs keep the protocol. Edit the canonical document to change shared rules.

## Contributing

1. Read [AGENTS.md](./AGENTS.md).
2. Find or create the relevant GitHub issue.
3. Change the smallest relevant skill.
4. Run the checks described by that skill.
5. Open a pull request that explains the behavior and evidence.

## License

Apache-2.0. See [LICENSE](./LICENSE).
