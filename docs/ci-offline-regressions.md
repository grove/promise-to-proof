# Complete offline CI regression gate (issue #114)

The `.github/workflows/live-judgments-offline.yml` workflow now runs the **complete documented default offline unittest suite** once on every pull request and main push. The stable CI job name is **Complete offline unittest suite (not live evidence)**. The runner `checks/run_offline_suite.py` uses the same unittest discovery as `python3 -m unittest discover -s checks -p 'test_*.py'`, checks that every matching file contributes collected tests, and reports test counts, failure/error/skip counts and test runtime in the job log and GitHub Actions step summary. Import errors, missing collections, and test failures make the job fail. Test details and tracebacks appear in the logs.

## Measured prior baseline and coverage gap

At main commit `a26e0a9` on October 12, 2026, **38** `checks/test_*.py` files exist. Five original CI workflows explicitly invoke tests from **25 distinct files**; some use `-k` to execute only a subset of their cases. **13 files were never explicitly invoked**:

`test_compare_delivery_strategies.py`, `test_issue_proposal.py`, `test_learning_candidates.py`, `test_p2p_checkpoints.py`, `test_p2p_delivery_measurements.py`, `test_p2p_delivery_record.py`, `test_p2p_execution_access.py`, `test_p2p_filesystem.py`, `test_p2p_finalization.py`, `test_p2p_single_entry.py`, `test_run_delivery_comparison.py`, `test_verify_acceptance_bundle.py`, and `test_verify_evidence_record.py`.

The former unconditional *partial* fixture workflow's successful hosted run [38207308940](https://github.com/grove/promise-to-proof/actions/runs/38207308940) took **138 seconds** (05:17:40–05:19:58 UTC). This is a partial-suite baseline, **not** a claim that the complete suite passed. The new suite's step summary and CI job duration enable a direct hosted after-change comparison.

## Cost and authority

The complete suite **replaces** the old unconditional selected-test workflow, rather than adding a second full-suite job. Existing path-triggered suites remain useful for early focused feedback, despite some overlap; they never execute the whole default suite. The old unconditional standalone first-pass/incremental benchmarks are still available as opt-in local scripts but are not part of default unittest discovery. Avoid extra partitioning or caching until new hosted runtime is measured.

CI runs Python 3.11 with full Git history and verifies pinned fixture commit objects `cc27a47f5ee765cff3cf13b21c36f974cb1234ae` and `eb84d66dd70ce8998cd43e951741785e8520c301`, fetching exact missing revisions from origin or failing. Tests are **offline fixture/mocked-host regressions**, never authenticated Codex or live model/sandbox evidence. Real host checks remain separate and require explicit authorization.

Documentation-only PRs run the same suite rather than being skipped: this avoids brittle change classification and missing required checks, and protocol docs may alter acceptance behavior. `checks/test_offline_suite_gate.py` exercises a deliberately failing newly introduced test and a file that collects no tests using temporary disposable fixtures, verifying that neither can produce a green gate.

**Enforcement:** as inspected October 12, 2026, `main` has no GitHub branch protection or repository rulesets. Therefore **GitHub does not currently enforce the required status check before merging**. A maintainer must configure a ruleset/branch protection to require the exact CI job name above. This GitHub connector cannot modify protection; do not describe the gate as branch-enforced without that setting.
