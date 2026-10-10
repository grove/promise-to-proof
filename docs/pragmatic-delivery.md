# Pragmatic delivery

P2P should be hard to fool, not hard to satisfy. Once the accepted outcome has
credible evidence and no material blocker remains, finish. A possible improvement
is not automatically a reason to send working code through another repair cycle.
The normative rules live in the [acceptance contract protocol](./acceptance-contract-protocol.md#pragmatic-assurance).

## How P2P should communicate

Pragmatic delivery should also feel pragmatic to the person using it. P2P should
explain the current situation in plain language, surface the important tradeoff or
blocker, and propose the smallest useful next move. It should look for leverage in
what already exists before suggesting new machinery.

This does not soften the proof standard. A concise explanation of a failed
requirement is still a failure, and a friendly recommendation is still only a
recommendation. Exact contracts, independent review, proof, candidate identity,
and authority remain binding.

When technical details such as hashes, requirement IDs, controller state, or report
paths matter, keep them available but explain their practical meaning first. The
canonical [voice and working style](./acceptance-contract-protocol.md#voice-and-working-style)
defines the normative behavior.

## What changes in ordinary work

Planning keeps the promise small and clear without omitting requested behavior.
Review blocks concrete material defects and necessary unknowns, not taste or
speculative improvements. Proof selects the smallest credible checks for the
actual risk instead of treating every possible edge case as a mandatory task.
An independent verifier can inspect and run existing tests; independence does
not require writing another test suite that checks the same outcome.

A full suite is still required when the contract or repository standards require
it, or when focused checks cannot establish confidence in a material regression
risk. Relevant failing checks, missing outcomes and important evidence gaps still
block. This is not a waiver of the repository's test instructions.

During a correction, run focused checks first. Run the required full suite once
the candidate is ready for that gate, and repeat it only when a later change or
a specific material risk invalidates the result. Review investigates engineering
and scope concerns; it should not routinely duplicate the entire proof workload.
Another report is useful only if it answers a question that is still open.

Before implementation starts, the controller's existing host checks also inspect
the task's required tools and evidence inputs. If, for example, the accepted
evidence needs a service that the actual worker cannot reach, P2P reports that
specific blocker immediately. It does not spend an implementation attempt
rediscovering the same restriction. This inspection uses small prerequisite
checks, and does not demand that the feature being implemented already exists.

## What happens after a small repair

A changed candidate still gets fresh independent review and proof reports. Full
coverage means every obligation is accounted for, not that every observation must
be regenerated. When the exact prior evidence and candidates are safely available,
the verifier can inspect the complete delta, establish which observations remain
applicable, and run fresh checks for the repair and affected interactions. The
new report distinguishes fresh results from earlier observations and records why
the latter still apply. An unchanged filename or small diff is not enough.

Missing history, changed assumptions or uncertain impact require fresh checking,
possibly the full set. Old verdicts never become verdicts for new code. The
[focused re-verification rules](./acceptance-contract-protocol.md#focused-re-verification-after-a-repair)
define the boundary. This change does not implement an automatic evidence cache,
skip controller verifier dispatches, or widen verifier access to obtain history.

The controller now gives each verifier its own latest compatible report,
command-evidence references, exact earlier and current Git generations, and the
complete delta. Review never receives proof's report, and proof never receives
review's report. Missing or corrupt optional history requires fresh observations;
it does not create a separate repair project. A portable report without the
original local command output is not treated as reusable local evidence.

## Resume existing work

Use the existing status and resume workflow with the invocation's admitted
stage-skill versions. A worker already running with old instructions does not
automatically reload them. The controller still rejects changed installed stage
skills; refreshing them is not an instruction-migration procedure. Supported
instruction upgrades for an active delivery remain tracked in
[#85](https://github.com/grove/promise-to-proof/issues/85). Preserve the retained
state and original skill versions instead of editing admission hashes or
resetting the delivery to hide that mismatch. New deliveries use the installed
versions at their own admission.

Keep the existing contract, requirement IDs, frozen comparison base, candidate
workspace, execution location and history. Do not rewrite the acceptance contract
to get an easier pass or rebase the in-flight candidate merely because P2P's own
rules changed. Resolve remaining material findings, leave optional polishing out,
and finish once current review and proof genuinely establish the accepted result.

For interrupted deliveries, a recorded process exit and an accepted stage report
are separate facts. Invalid returned JSON must not leave a finished worker marked
as an uncertain launch. The controller retains rejected output and a precise
report error. A malformed read-only recovery diagnosis can receive one format
correction against unchanged inputs; an actually uncertain process is never
silently relaunched. Both fresh verifier verdicts are still required to finish.

## Verification of these rule changes

`python3 checks/test_pragmatic_verification.py` checks the shipped instructions
for required safeguards and contradictory mandatory wording. It is a structural
regression check, not an experiment showing that models follow the rules or that
delivery is faster. The [behavioral scenarios](../checks/pragmatic-verification-scenarios.md)
exercise both false blocking and false acceptance on a supported live host.
