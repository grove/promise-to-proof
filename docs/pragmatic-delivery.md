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

## What makes a regression test trustworthy?

A green test is useful when it would turn red for a meaningful failure of the
behavior it promises to protect. Review looks at the assertions and the real
interface being exercised, not just test counts. For example, a whitespace
validation test that compares a result to itself can pass whether the
validator works or not. A test that mocks out that same validator can be
equally misleading. An assertion that executes only on some wall-clock
seconds is unreliable even when the suite happens to be green.

On the other hand, a small existing test that calls the actual public
interface and compares its output with an independently known expected result
is strong evidence. Review should accept it rather than making a second test
suite for the sake of process. Mocks and helpers are fine when they do not
remove the important decision from the check. Test maintainability, security,
state and concurrency matter when they have realistic consequences; stylistic
preferences do not create repair requirements.

The [live review-quality fixtures](../checks/fixtures/live-judgments/README.md#review-quality-and-stopping-issue-43)
give P2P known-good and known-bad candidates, including tests that stay green
after a deliberate regression. The independent fixture oracle runs outside
the workers; it is not another mandatory code-review stage. These cases must
actually run on a supported macOS/Codex host to become live judgment evidence.

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

Use the existing status and resume workflow. A delivery keeps a preserved copy
of its stage instructions and their material reference documents. Installing a
P2P update leaves those instructions pinned, so ordinary resume can finish the
same work. An already-running worker does not automatically reload new rules.

To apply an update to retained work, ask P2P to upgrade that delivery's
instructions and continue. The controller previews the exact change through
`upgrade-instructions <contract>`, then adopts it with `--authorize-upgrade`
under covering local authority. This is a deterministic transition with no
extra model stage. It preserves completed implementation and runs fresh
independent review and proof on the same candidate. Those verifiers still use
the smallest sufficient checks; an upgrade is not a reason to rerun every test.
Selecting the same instructions again is a no-op. See the
[controller upgrade recipe](./p2p-delivery-controller.md#upgrade-an-active-deliverys-instructions)
for commands and recovery details.

Keep the existing contract, requirement IDs, frozen comparison base, candidate
workspace, execution location and history. Do not rewrite the acceptance contract
to get an easier pass or rebase the in-flight candidate merely because P2P's own
rules changed. Resolve remaining material findings, leave optional polishing out,
and finish once current review and proof genuinely establish the accepted result.

Upgrade only after the current worker has a reconciled completion. If its exit
is uncertain, preserve the run and resolve that receipt first. Missing prior
instruction snapshots, incompatible versions or missing authority produce a
specific blocker. Legacy work without complete snapshots keeps its existing
resume path with the original installation; never reset it or edit admission
hashes to make a mismatch disappear.

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
