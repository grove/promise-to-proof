# Skills

Practical agent skills for turning requirements into implementation, proof, and repair.

The skills are written for agent-skill-compatible coding tools. They keep the
source ticket's promises visible, make evidence explicit, and carry unresolved
questions into the next step. They do not provide a workflow runtime.

Follow [How to take a ticket from promise to proof](./docs/promise-to-proof.md)
for the native delivery workflow. Matt Pocock's planning and TDD skills are
optional additions. The [acceptance contract protocol](./docs/acceptance-contract-protocol.md)
defines the shared contract, revision, and proof rules.

Issues and specifications for this repository live in [GitHub Issues](https://github.com/grove/skills/issues).

## Choose a skill

| Skill | Use it when | It gives you |
|---|---|---|
| [`critique`](./skills/productivity/critique/SKILL.md) | You explicitly request an independent review of a proposal against its intended outcome | Evidence-backed advice and a recommendation |
| [`interrogate`](./skills/productivity/interrogate/SKILL.md) | You want to question the agent's proposal and reasoning | Evidence-backed answers, a revised approach, and explicit unknowns |
| [`acceptance-contract`](./skills/productivity/acceptance-contract/SKILL.md) | A ticket needs clear acceptance criteria | A candidate-independent revision with stable requirement IDs and evidence plans |
| [`slice-contract`](./skills/productivity/slice-contract/SKILL.md) | A parent contract is too large for one coherent task | A traceable breakdown and, when authorized, published child tickets |
| [`implement-contract`](./skills/productivity/implement-contract/SKILL.md) | An agreed contract is ready to implement | Scoped implementation, development checks, and a recoverable candidate handoff |
| [`review-contract`](./skills/productivity/review-contract/SKILL.md) | A captured implementation is ready to inspect | Findings on contract fidelity, scope, and engineering quality |
| [`prove`](./skills/productivity/prove/SKILL.md) | Implementation is ready to verify | `PROVEN` or `NOT PROVEN` with evidence |
| [`repair-proof`](./skills/productivity/repair-proof/SKILL.md) | Proof found a specific gap | A scoped repair report; fresh proof is still required |
| [`fix-pr`](./skills/productivity/fix-pr/SKILL.md) | A pull request's CI failed | `FIXED` or `NOT FIXED` for the target workflow |

## Typical workflow

Optionally invoke `critique` to assess an idea, issue, specification, plan, or
proposal before committing to it. Its advice requires no downstream skill.

```text
Source → acceptance-contract → saved contract → implement-contract
       → captured candidate → review-contract → prove
       → repair-proof if needed → fresh proof and review
```

1. **Plan acceptance.** Run `acceptance-contract` on the ticket or specification.
   It records a revision such as `v1`, stable `R` IDs, boundaries, seams,
   independent oracles, and planned evidence. Plan state is `planned` or `gap`.
   Save its output using the [durable handoff convention](./docs/acceptance-contract-protocol.md#durable-contract-handoff)
   before passing its location and revision to another session.
2. **Implement.** Run `implement-contract` to build the smallest complete change,
   including necessary invariants, state, failure handling, and persistence.
   Save its report and recoverable candidate content for the next session.
3. **Review.** Run `review-contract` against that candidate and a fixed comparison
   base. Pass supported findings to a separately authorized `implement-contract`
   invocation. Review does not edit the candidate.
4. **Prove.** Run `prove` against the exact contract and candidate. Each row gets
   `proven`, `disproven`, or `not proven` with durable evidence.
5. **Repair only named proof gaps.** If proof is `NOT PROVEN`, pass its unresolved
   requirement IDs to `repair-proof` for the smallest complete repair.
6. **Refresh results.** Every candidate change needs fresh proof of every row and
   refreshed review. A changed agreement returns to `acceptance-contract` first.

For large work, optionally insert `slice-contract` after saving the parent
contract. Approve the breakdown and authorize publication to the named tracker
or local destination. Then plan each child's contract before implementation.
Small work keeps the direct path above; `NO SPLIT` is a valid result.

```text
saved parent contract → slice-contract → approved/published child tickets
→ acceptance-contract for each child → implementation, review, and child proof
→ integrated candidate → final integration review when needed → full parent prove
```

Slicing defaults to inspection and a draft. Publication needs authority for the
approved tickets, metadata, and links. An unchanged approved plan retains its
authority on rerun. Resume partial publication from the saved mapping, confirm
uncertain writes before retrying, and preserve successful tickets and human edits.
See the [slicing guide](./docs/promise-to-proof.md#divide-large-work-without-changing-the-agreement)
for recovery and durable handoffs. Complete allocation and child proofs do not
establish parent acceptance.

Review and proof can run in either order against the same fixed candidate.
Each phase is an explicit handoff, not an automatic loop. Neither review nor proof
requires an open PR or unrelated green CI. Merge still requires current proof,
green required checks, and the repository's review requirements.

Save implementation and review reports at a supplied or documented destination.
Otherwise propose a destination outside the candidate and mark storage pending
until the authorized workflow saves and rereads the report. Transfer recoverable
candidate content, contract text, and review comparison identities across
checkouts. A digest or a path available only in a previous session is insufficient.

Keep requirement IDs stable. Increment the revision for authorized material
changes to promises, boundaries, outcomes, or exclusions. Evidence paths, test
paths, and wording changes that preserve meaning do not increment it. Reconcile
GitHub checkboxes with the contract, but never use them as proof.

## Important boundaries

| Skill | Responsibility | Boundary |
|---|---|---|
| `critique` | Give optional, agent-led advice on a proposal | Does not edit the artifact, repository, or acceptance contract, publish findings, or implement |
| `acceptance-contract` | Plan requirements and evidence | Does not implement or verify |
| `slice-contract` | Allocate parent obligations and publish approved tickets | Does not author contracts, implement, prove, or close work |
| `implement-contract` | Implement the agreed scope and run development checks | Does not revise the contract, declare acceptance, or implicitly run review or proof |
| `review-contract` | Inspect a fixed implementation and comparison scope | Does not edit, repair, approve, or declare acceptance |
| `prove` | Verify one fixed candidate | Does not edit, commit, push, or publish |
| `repair-proof` | Repair named implementation or evidence gaps | Does not declare acceptance |
| `fix-pr` | Repair a failed PR workflow | Does not prove the whole ticket |
| `interrogate` | Let you examine the agent's proposal through questions | You lead the discussion; invocation does not grant implementation authority |

Explicit `implement-contract` invocation authorizes scoped local edits and safe
checks. `review-contract` authorizes inspection and safe isolated diagnostics.
Neither invocation alone authorizes commits, pushes, publication, deployments,
destructive changes, or merges.

## What the results mean

- Slicing returns **DRAFT**, **PUBLISHED**, **PARTIAL**, **BLOCKED**, or **NO SPLIT**.
  **PUBLISHED** confirms saved tickets and required links, not implementation readiness.
- **IMPLEMENTED** means the requested scope is implemented and its material
  development checks passed. **PARTIAL** exposes incomplete work or validation.
- **REVIEWED** means the captured scope has no material review findings.
  **CHANGES NEEDED** names supported corrections. **BLOCKED** means a necessary
  input or capability prevents the relevant phase from completing.
- Implementation and review outcomes establish neither acceptance nor merge readiness.
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
/slice-contract #123; draft only
/implement-contract #123
/review-contract <saved implementation handoff> against <comparison base>
/prove <saved contract>; candidate <saved implementation handoff>
/repair-proof <matching proof report>; candidate <saved candidate handoff>; requirements <IDs>
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
├── implement-contract/
├── interrogate/
├── prove/
├── repair-proof/
├── review-contract/
└── slice-contract/
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
