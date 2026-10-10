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

This is a **small specified-error detector**, not universal model reliability,
a numerical quality score, or the larger #52 benchmark. It does not establish
a speedup without matched measurements. #73 can later extend the same follow-up
case through automatic applicability selection; no #73 functionality is assumed
here.
