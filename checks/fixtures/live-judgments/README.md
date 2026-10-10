# Small live review/proof regression gate

This suite tests judgments, **not** whether the delivery controller can execute a
mocked transport. The oracle and expected stage outcomes were written before
execution and are kept in `manifest.json` on the **harness** side. The candidate
workspace contains only the source checkout, product changes, and acceptance
contract, never the fixture's expected verdicts or oracle answers. Worker prompts
also never include the expected outcomes.

Run the real supported host path from the repository root on **macOS**, with
Python 3.11+, Git, authenticated Codex CLI and the installed P2P stage skills:

```sh
python3 checks/check_p2p_judgments_host.py --output-dir /absolute/new/evidence/directory
```

The output directory must be new and persistent. The runner creates isolated Git
repositories, externally retained controller workspaces, real Codex review/proof
stage receipts, CLI oracle outputs, per-candidate summaries, and an aggregate
`summary.json`. Any stage mismatch, missing material finding, false proof,
unverified follow-up history or fixture-oracle mismatch exits nonzero. Inspect
each case's `summary.json` for the expected and observed judgments; inspect the
retained `runtime/attempts/<id>/` receipts and independent reports to diagnose
disagreement. The runner reuses the controller's existing #59 measurement
accounting; it adds no new cost or scoring schema. To target a single case while
diagnosing, use `--only green-but-incomplete` (repeatable); the default command
gates all cases.

Cases, each with explicit independently fixed outcomes:

* **Correct control**: REVIEWED + PROVEN, with three observable promised
  behaviors. A review that blocks everything fails.
* **Green-but-incomplete**: supplied unit tests pass, while the actual CLI
  accepts whitespace-only usernames. Review must flag R2 and proof must return
  NOT PROVEN with R2 unproven. Correct handling of the empty string is insufficient.
* **Unrelated-scope-expansion**: R1–R3 function correctly, but a separate
  pre-existing fee calculation is changed. Proof remains PROVEN for the promises;
  review must return CHANGES NEEDED and name the material scope defect.
* **Optional-polish**: complete low-risk behavior with a nonbinding helper-name
  suggestion. No candidate mutation or repair is allowed; both stages pass.
* **Follow-up-regression**: a passing first candidate is followed by a one-line
  edit to a shared normalizer. R2 then fails. The same normal production stage
  path receives its own checked earlier observations and must evaluate the new
  exact candidate independently, rather than carrying a stale verdict forward.
  Both stage reports must bind the new candidate generation.

The harness intentionally uses a dedicated **evaluation-only** candidate
generation (there is no implementation worker). This does not change normal
`deliver-issue` admission or allow a production delivery to bypass implementation.
It invokes the **existing** independent review/proof stage and focused
re-verification code. The tiny delivery check in
`checks/check_p2p_delivery_host.py` remains the end-to-end smoke test.

`python3 -m unittest discover -s checks -p 'test_live_judgments.py'` checks
fixture setup, the private CLI oracle, exact candidate identity and runner failure
behavior **offline**. It never substitutes for a live-host run. A Linux runner,
a mock or an attempted admission is explicitly **not** live judgment evidence.
The live suite cannot run on unsupported hosts and reports that limitation
instead of silently simulating success.

## Review quality and stopping: issue #43

The same live-host command also evaluates independent review judgments on
correct and deliberately defective candidates. It does not start another
reviewer, benchmark engine, or mandatory test-writing stage.

* **Meaningful existing public-interface tests:** independently assert actual
  CLI exit status, stderr and stdout for empty, whitespace-only and visible
  usernames. Review accepts them as adequate without a duplicate suite.
* **Tautological and circular oracles:** supplied unit tests are green but
  compare a result to itself or compute the expected answer using production
  code. Review must identify that R2 is not protected.
* **Over-mocked boundary:** tests patch out the validator they purport to
  exercise. Review must name the production decision that a regression could
  bypass.
* **Unreliable timing-based guard:** an R2 assertion is skipped on alternate
  seconds. A reviewer must flag the material CI regression gap, not a cosmetic
  test-style preference.
* **Sample-only implementation:** a public CLI works for supplied examples but
  rejects another ordinary visible name. Review and proof flag R3.
* **Real conditional security risk:** a CLI dispatches untrusted input through
  a shell. Review must name the applicable injection trigger and smallest safe
  correction. A harmless metacharacter counterexample also demonstrates R3
  is broken; proof must not pass.
* **Reconciled finding:** a deliberately broken R2 candidate has a material
  review finding. The next exact candidate fixes R2 and adds meaningful tests;
  the same reviewer stage gets its own checked previous observations and must
  produce a fresh clean judgment without rewriting the original failing report.

The harness performs **private disposable regression-sensitivity probes after
the two independent stages**. Each probe substitutes a known-broken R2
implementation *outside* the candidate and reruns the supplied tests. Hollow
tests remain green; meaningful guards fail; a timing-dependent guard shows
both outcomes under frozen time inputs. These probes establish human-authored
fixture validity, **not** a mutation-testing requirement for normal review.
Reviewer workers never receive these expected results or probes, and the
harness uses neutral candidate directory names to avoid labeling the intended
judgment in their workspace paths.

To investigate one example without paying for the whole suite, use the same
command with `--only review-overmocked-boundary` or another case ID. The
default live gate exercises all cases. The runner retains independent oracle
outputs and actual model reports so a disagreement can be diagnosed. None of
these scenarios claims universal review reliability until it has been run on
the real supported host; offline fixture checks are explicitly not live
evidence.

This is a **small specified-error detector**, not universal model reliability,
a numerical quality score, or the larger #52 benchmark. It does not establish
a speedup without matched measurements. #73 can later extend the same follow-up
case through automatic applicability selection; no #73 functionality is assumed
here.
