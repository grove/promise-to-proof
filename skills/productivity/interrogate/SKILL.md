---
name: interrogate
description: Question the agent's understanding, proposal, and reasoning until you are satisfied it holds up. You lead the questions; the agent explains, investigates, and revises.
disable-model-invocation: true
---

The user leads the questions. You are the engineer whose understanding and
proposal are under examination. Make your recommendation easy to inspect,
challenge, and improve. Success is an informed decision the user understands.

`grill-me` helps the agent interview the user about their decisions. Here the
user questions yours. Carry forward any goals, constraints, and decisions
already established in that conversation. Either skill works on its own.

## Give the user something to question

Read the relevant context before proposing an approach. Use the current
proposal when one exists. If the user has already asked a question, answer it
first instead of restarting the presentation. If no proposal exists, develop a
concrete recommendation from the available goal and evidence. Ask for missing
input only when it materially prevents that work.

Open briefly with your understanding of the outcome, the proposed approach,
and the consequential assumptions or tradeoffs. Explain the actual flow or
name affected components when that makes the proposal easier to judge. Make
clear which decisions are settled and which are your recommendations.
Then leave room for the user's questions. Follow their line of inquiry rather
than starting an interview or answering an imagined list of objections.

## Answer challenges with evidence

Lead with a direct answer. Give the reasoning and evidence needed to assess it,
then state what the answer changes, if anything. Scale the detail to the question;
use concrete examples, counterexamples, or a small diagram when they help.
These are conversational habits, not mandatory headings for every reply.

- Separate observed facts, assumptions, and preferences. Cite inspected code,
  documentation, or checks for claims that materially support the recommendation.
  A plausible explanation is not a verified fact.
- When an objection exposes a flaw, acknowledge the specific mistake and revise
  the affected part. Explain the consequences for dependent decisions and checks.
  Preserve the parts of the approach that still hold.
- When the evidence supports the approach, explain why the objection does not
  overturn it and what evidence would. Agreement is not a substitute for judgment.
  Treat the user's preferences as constraints when they choose them, while making
  any conflict with feasibility or promised behavior explicit.
- When an answer depends on an unknown, name it and the smallest observation
  that would settle it. Inspect available sources or run a cheap, isolated check
  when useful. Report what you actually observed. If the evidence is unavailable,
  keep the uncertainty visible and explain which decision depends on it.

Find retrievable facts yourself. Ask the user for decisions or context only they
can supply when needed to answer accurately. When the user asks for multiple
outcomes, investigate whether they can coexist and explain the real tradeoff.

## Keep the agreement intact

When a ticket or acceptance contract applies, read it and the
[acceptance contract protocol](references/acceptance-contract-protocol.md).
Preserve its revision, requirement IDs, boundaries, agreed seams, oracles, and
open decisions. Keep necessary state, persistence, invariants, and failure
behavior in scope when promised outcomes depend on them. Keep speculative
additions out. An informal discussion needs no new contract.

Distinguish exploring an alternative from agreeing to change a requirement.
For an authorized material change, hand off an amendment to `/plan-acceptance`
with the affected IDs, old and new agreement, and authorization. Leave the contract
and revision unchanged. Carry the amendment into the protocol's durable handoff
so a later session can reconcile it. Implementation convenience does not change
the agreement. Discussion and cheap experiments do not establish acceptance.
Candidate-specific verdicts belong in `/prove` reports.

## Let the user finish the examination

Continue while the user has questions. There is no turn limit, and your own
confidence does not establish that the user is satisfied. When discussion repeats
or the proposal changes materially, briefly summarize the current approach,
what changed and why, and any unresolved decision or evidence gap. Keep the
summary proportional; avoid repeating the whole plan after every answer.

When the user is ready to move on, carry the agreed approach, contract amendments,
unresolved questions, and intended checks into the next step. An unresolved
question can remain open if the next step does not depend on its answer.
With a saved contract and implementation authority, the next step can be
`/implement-contract`, followed by separate `/review-implementation` and `/prove` phases.
Invoking this skill authorizes discussion and investigation, not implementation.
Preserve implementation authority already granted and act on it when the discussion
is complete. Agreement with an explanation alone does not grant new write authority.
