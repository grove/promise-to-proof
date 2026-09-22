# Promise to Proof + Atomic

Promise to Proof and Atomic solve two different parts of the same problem. Promise to Proof defines a disciplined way for an agent to carry a software change from an initial promise all the way to evidence-backed acceptance. Atomic provides the machinery for running multi-stage agent work as an explicit, durable workflow. Put together, the result could be a system where the engineering process is no longer something we repeatedly explain to an agent or manually shepherd from one prompt to the next. Instead, the process becomes executable: Atomic keeps track of where the work is, while Promise to Proof defines what each stage must accomplish and what evidence is required before the work can move forward.

The easiest way to understand the distinction is to imagine a construction project. Promise to Proof is the building standard and the set of specialist procedures. It says how the architect should turn the brief into precise requirements, how the builder should implement them, how an independent reviewer should inspect the result, and how an inspector should prove that the finished building actually satisfies the agreement. Atomic is closer to the site manager and project control system. It knows which specialist should work next, remembers what has already happened, keeps the plans and inspection reports attached to the job, pauses when approval is needed, and sends work back for correction when an inspection fails. Neither replaces the other. Promise to Proof provides the meaning of the work; Atomic provides the machinery that coordinates it.

## What Promise to Proof already gives us

Promise to Proof is built around a simple but important idea: agreeing on what should be delivered, implementing it, reviewing the implementation, and proving that the promised outcome works are different activities. They should not collapse into one long agent session where the same model writes some code, looks at its own work, declares it good, and moves on. Instead, the process produces durable handoffs. `plan-acceptance` turns the source ticket or specification into a versioned acceptance contract. `implement-contract` works against that exact agreement and produces a specific candidate. `review-implementation` inspects that candidate for fidelity, scope, and engineering quality. `prove` checks every promised outcome against evidence. If proof exposes a repairable gap, `repair-gaps` can correct that specific gap, but it cannot declare acceptance; fresh proof is required afterward.

This means Promise to Proof already contains many of the ingredients of a workflow. Its skills have defined responsibilities. They have recognizable outcomes such as `IMPLEMENTED`, `CHANGES NEEDED`, `PROVEN`, `NOT PROVEN`, and `REPAIRED`. They pass artifacts from one stage to another. They care about exact identities, such as the precise contract revision and the exact Git commit or snapshot being reviewed. They also define important rules about what happens after a change: if the candidate changes, old proof no longer describes the current candidate; if the promise changes, the contract must be revised rather than quietly adjusting the implementation target. In other words, Promise to Proof already defines much of the *logic* of a workflow. What it intentionally does not provide is the runtime that keeps that workflow moving.

Today, without such a runtime, a person or an enclosing agent session acts as the coordinator. Someone runs `plan-acceptance`, saves its result, then starts `implement-contract`, then invokes review and proof, then looks at the result and decides which command should run next. This is perfectly workable, but the coordination itself is manual. If the process stops halfway through, another session has to reconstruct what should happen next from the saved artifacts. If proof fails, someone has to notice which requirements failed and invoke the correct repair step. If a repair changes the candidate, someone needs to remember that the previous review and proof are stale. Promise to Proof describes all these rules, but it does not execute them.

## What Atomic adds

Atomic is interesting here because it already provides the missing orchestration layer. It is a coding-agent environment, but it also includes a workflow system where engineering processes can be expressed as TypeScript. A workflow can launch separate agent tasks, run independent tasks in parallel, branch according to results, ask a human for input, create bounded repair loops, retain artifacts, and checkpoint its progress so that a long-running job can be resumed instead of starting over. The workflow itself is explicit code rather than an instruction like “keep working until this is done,” which gives us a useful separation between the rules of the process and the judgment happening inside individual agent stages.

Atomic also supports Agent Skills, which is particularly important for this integration. We would not need to rewrite Promise to Proof as a collection of Atomic-specific prompts. The existing skills could remain the units that teach an agent how to plan acceptance, implement a contract, review a candidate, or prove it. Atomic would sit above them. A workflow stage could start a fresh agent context and explicitly tell it to use `plan-acceptance`; a later stage could start a different context and invoke `review-implementation`. This preserves the existing skill design while adding coordination around it.

A useful way to picture the combined system is this:

```text
                   Atomic workflow
                         │
                         ▼
                  plan-acceptance
                         │
                  saved contract
                         │
                         ▼
                 implement-contract
                         │
                 exact candidate
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
    review-implementation          prove
              │                     │
              └──────────┬──────────┘
                         │
                 inspect outcomes
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
       complete     implementation    proof gap
                       problem
                         │              │
                         ▼              ▼
                 implement again   repair-gaps
                         │              │
                         └──────┬───────┘
                                ▼
                       review + prove again
```

The important point is that Atomic does not need to understand how to perform acceptance planning or how to judge whether a requirement has been proven. Those are responsibilities of the Promise to Proof skills. Atomic only needs to understand the outputs well enough to enforce the protocol. If review says `CHANGES NEEDED`, the workflow knows that the candidate needs another implementation pass. If proof says `NOT PROVEN` and identifies repairable requirements, the workflow can invoke `repair-gaps`. If a repair produces a new candidate, the workflow knows that earlier review and proof belong to the old candidate and must be refreshed.

## Static rules, dynamic execution

This combination becomes especially useful when we distinguish the *workflow rules* from the *path a particular issue takes through those rules*. The rules should be relatively static. For example, proof cannot silently repair the candidate. A changed candidate requires new proof. A changed promise requires a contract revision. Child proofs do not add up to parent proof. Those are protocol invariants, and we do not want an agent deciding from one run to another whether they still apply.

The execution path, however, should be dynamic. A simple issue might pass through planning, implementation, review, and proof exactly once. Another issue might fail proof, receive a small repair, and pass on the second attempt. Another might receive a substantial review finding, return to implementation, then require another independent review and proof. A larger issue might be sliced into three independently useful child outcomes, each of which runs its own Promise to Proof workflow before the assembled result is finally proven against the parent contract. The workflow therefore behaves less like a fixed pipeline and more like a controlled state machine: the available moves are predetermined, but the actual route emerges from the evidence produced during the run.

Atomic's execution model fits this well. Even when the logical process feels like a loop, the recorded execution can remain a history of distinct stages. Instead of repeatedly reopening one abstract `prove` node, a run might contain `prove-1`, `repair-1`, `prove-2`, and so on. This is useful because the resulting graph tells the story of what actually happened. We can see which candidate was reviewed, what failed, what repair was attempted, and which later proof finally established the requirements. The workflow is dynamic, but its history remains inspectable.

## Why candidate identity matters so much

One of the strongest connections between the two projects is their emphasis on durable state. Promise to Proof is unusually strict about identifying exactly what was reviewed or proven. A branch name such as `feature/retries` is not enough because that branch can change. `HEAD` is not enough because it depends on where and when it is evaluated. Proof should be attached to an exact commit SHA or another reproducible snapshot. The same principle applies to the acceptance contract: it should have a known revision and recoverable contents.

Atomic can turn those identities into workflow state rather than relying on human memory. Imagine that proof runs against candidate `abc123` and returns `PROVEN`. Later, a review finding causes implementation to produce candidate `def456`. There is no need for an agent to reason vaguely about whether the old proof “probably still applies.” The runtime can compare the identities:

```text
proof candidate:    abc123
current candidate:  def456
```

They are different, so the earlier proof is stale. It remains an accurate historical statement about `abc123`, but it cannot establish acceptance of `def456`. The same rule can apply to review. This is a good example of something we should move out of model judgment and into deterministic workflow logic.

That distinction is important because a good agent workflow should not use an LLM for decisions that ordinary software can make exactly. Agents are valuable for understanding requirements, writing code, inspecting behavior, and evaluating evidence. They should not be responsible for remembering whether two SHA strings are equal or whether a report refers to the current contract revision. Atomic can provide the deterministic shell; the agents operate inside it where judgment is actually needed.

## Independent review and proof

Another appealing feature is that Atomic can give different workflow stages different contexts. The implementation stage can keep a rich context containing the contract, repository investigation, failed tests, and decisions made while developing the solution. Review and proof can then start in fresh contexts with the exact candidate and contract supplied explicitly.

This reinforces one of the central ideas in Promise to Proof: implementation, review, and proof answer different questions. The implementer asks, “How do I build the promised capability?” The reviewer asks, “Does this candidate faithfully implement the agreement, stay within scope, and meet engineering obligations?” Proof asks, “What evidence establishes that every promised outcome actually holds for this exact candidate?” Keeping those perspectives distinct reduces the temptation for the same conversational narrative to carry assumptions from implementation into verification.

Atomic can even run review and proof in parallel when both operate against the same frozen candidate. Neither needs to wait for the other because one is not a substitute for the other. When both finish, the workflow can evaluate their results together. If review is clean and proof succeeds, the candidate can advance. If review finds a material engineering concern despite successful proof, the candidate still needs correction. If review is clean but proof cannot establish one of the promised outcomes, the workflow follows the proof-repair path. This makes the distinction between “looks correctly engineered” and “is actually proven against the promise” operational rather than merely philosophical.

## Human decisions remain human decisions

A workflow runtime should automate coordination without quietly taking authority away from the person responsible for the work. This is another place where Atomic and Promise to Proof fit together nicely. Promise to Proof already distinguishes ordinary implementation decisions from consequential changes to the agreement. If implementation discovers that satisfying the original contract is impossible without changing a promised outcome, the correct response is not for the implementation agent to rewrite the contract. The issue must return to acceptance planning with the relevant amendment and appropriate authorization.

Atomic can make such boundaries explicit human gates. The workflow might stop and explain that `R4` cannot be satisfied under the current architecture without changing the externally visible behavior. It can present the proposed amendment and ask whether the agreement should change. If the answer is no, the workflow stops or returns to implementation under the original contract. If the answer is yes, it invokes `plan-acceptance` to produce a new revision and then proceeds using the new agreement.

The same approach can be used for publishing sliced tickets, pushing branches, creating pull requests, merging, or performing other consequential side effects. The runtime can know *where* an approval is required without deciding *for* the user whether approval should be granted. That gives us meaningful automation without turning the workflow into an autonomous system that silently expands its own authority.

## Machine-readable handoffs

There is one improvement that would make the integration considerably more robust. Today, Promise to Proof reports are designed primarily for people. They already have predictable headings and outcomes, but an orchestration system should ideally not have to read a Markdown report and guess what state it represents.

A small machine-readable result could accompany each report. For example, the proof stage might return something conceptually like:

```json
{
  "outcome": "NOT_PROVEN",
  "contractRevision": "v1",
  "candidate": "abc123",
  "report": ".p2p/runs/123/proof-1.md",
  "unresolvedRequirements": ["R3"]
}
```

The Markdown report would still contain the detailed reasoning, observations, evidence references, and explanation that a human needs. The structured result would simply tell Atomic what happened. The runtime could then branch on an enum rather than searching prose for the phrase `NOT PROVEN`.

Atomic supports schema-backed agent stages, so these result contracts can be explicit. `review-implementation` could return a structured outcome plus finding IDs. `implement-contract` could return its outcome and candidate identity. `repair-gaps` could return the new candidate and addressed requirement IDs. This does not change the intellectual work of the skills; it gives that work a reliable API.

## What happens when an issue is sliced

The combination becomes even more interesting for larger work. Promise to Proof already distinguishes between a parent contract and the child outcomes created by `slice-contract`. Each child gets its own contract and can be implemented, reviewed, and proven independently. But proving all the children does not prove the parent because the integrated system may have cross-slice behavior and shared invariants that no individual child candidate demonstrated.

Atomic supports nested workflows, so each child could simply become another Promise to Proof workflow:

```text
                    parent contract
                          │
                     slice-contract
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
         child A       child B       child C
            │             │             │
          P2P           P2P           P2P
         workflow       workflow       workflow
            │             │             │
            └─────────────┼─────────────┘
                          │
                   integrated candidate
                          │
                          ▼
                  prove parent contract
```

Atomic can coordinate parallel children where their prerequisites allow it and wait for necessary dependencies where they do not. Once the contributions are assembled into one exact candidate, the parent proof runs against the full parent contract. The runtime therefore automates the decomposition without weakening Promise to Proof's evidence model.

## What Atomic should not take over

It would be easy to overbuild this integration. Atomic has sophisticated workflow primitives, and that creates a temptation to move more and more Promise to Proof logic into TypeScript. I think that would be a mistake.

The workflow should know things such as “a changed candidate invalidates current proof,” “`CHANGES NEEDED` routes to implementation,” and “a material contract change requires acceptance planning.” It should not duplicate the detailed instructions for how to examine a contract, how to decide whether an oracle is independent, how to review scope fidelity, or how to hunt for counterexamples. Those belong in the skills. Keeping that line clear means Promise to Proof can continue improving its methodology independently of Atomic, while Atomic remains the execution environment.

A useful test is to ask whether a rule requires engineering judgment. If it does, it probably belongs in a skill. If it is an objective orchestration rule, it probably belongs in the workflow. “Does this test actually prove restart persistence?” requires judgment and belongs in `prove`. “Did the candidate SHA change after repair?” is deterministic and belongs in the runtime.

## What a first version could look like

We do not need to implement the entire vision immediately. The smallest meaningful experiment would handle one ordinary, unsliced issue:

```text
plan-acceptance
       ↓
implement-contract
       ↓
 ┌─────┴─────┐
 ▼           ▼
review      prove
 └─────┬─────┘
       ▼
   final state
```

The workflow would save the contract, capture the candidate identity, run review and proof against that candidate, and present the resulting state. At first, it could simply stop if either stage does not succeed. That alone would demonstrate that Atomic can execute the existing skills as separate phases and preserve their handoffs.

The next increment would add one repair route. `NOT PROVEN` with repairable requirement IDs would invoke `repair-gaps`, capture the resulting candidate, and automatically rerun both review and proof. After that, we could handle `CHANGES NEEDED`, contract-change gates, CI repair, and eventually child workflows for slicing.

This incremental approach is attractive because we would be testing the integration rather than designing an enormous new framework. Atomic already supplies the workflow runtime. Promise to Proof already supplies the engineering protocol. The experiment is mostly about creating a reliable seam between them.

## The resulting mental model

The combined system can be summarized as three layers:

```text
┌─────────────────────────────────────────────┐
│                   Atomic                    │
│                                             │
│ Runs, checkpoints, resume, branching,       │
│ parallelism, human gates, workflow UI       │
├─────────────────────────────────────────────┤
│          Promise to Proof workflow          │
│                                             │
│ Legal transitions, candidate invalidation,  │
│ phase ordering, repair routing              │
├─────────────────────────────────────────────┤
│           Promise to Proof skills           │
│                                             │
│ Plan, implement, review, prove, repair       │
│ using engineering judgment and evidence     │
└─────────────────────────────────────────────┘
```

Another way of saying the same thing is that **Atomic would own the process, while Promise to Proof would own the meaning of success**.

That feels like the most important idea behind the integration. We are not trying to turn Promise to Proof into a large orchestration framework, and we are not asking Atomic to invent our engineering methodology. We are using each system for what it is good at. Promise to Proof makes the promises, candidates, evidence, and acceptance boundaries precise. Atomic makes the resulting process executable, durable, observable, and resumable.

If this works well, the experience for the user could eventually become remarkably simple. Instead of manually conducting a sequence of skill invocations, someone could say:

`Run Promise to Proof for issue #123.`

Behind that simple command, the workflow could preserve the contract, isolate implementation from independent review, prove the exact candidate, route failures through bounded repairs, stop for real decisions, recover after interruptions, and leave behind a readable history showing exactly how the original promise became a proven result.

That is the opportunity in combining the two projects: **Promise to Proof stops being merely a workflow people follow and becomes a workflow the system can faithfully execute.**
