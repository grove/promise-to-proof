# Pragmatic delivery stabilization: validation

## Observed mechanisms and changes

The reported failures were investigated against `dfe436aa3050ef0d94d2a5a56ae35b84e5dcd11e`.
Controller inspection and deterministic fixtures establish these mechanisms:

- Report validation happened before terminal bookkeeping: a worker that exited successfully with malformed JSON could remain reserved. Rejected responses now retain their exact bytes and terminal status; supported resume reconciles recorded completion before another dispatch. A malformed read-only diagnosis gets one bounded format correction; uncertain execution is never silently retried.
- Repeated recovery could confuse changed wording or candidate bytes with progress. Recovery now tracks unresolved requirements and strategy/capability evidence, reuses an applicable retained decision, and diagnoses stalled progress instead of repeating an ineffective method.
- Isolation probes did not establish task readiness. The existing second preflight now checks known tools, supplied evidence, runtimes, and service access under actual worker permissions. Missing prerequisites stop implementation; product behavior still to be built is not a prerequisite. Resolved blockers can be rechecked on resume.
- Git snapshots and generation writes launched a process for each file; storage writes repeatedly scanned ignored records. Batched blob reads, generation writes, ignore checks, and shared path resolution remove this repeated work while preserving exact identities and storage validation.
- Fresh verifier contexts received no usable same-stage history. Review and proof now receive their own validated observations plus the complete candidate delta. Each still makes a fresh judgment, covers every requirement, and preserves mandatory final-candidate checks. The workflow calls for focused checks during edits and one required suite after the candidate is ready.

## Controlled Git/storage benchmark

Both variants use the **current controller**. The baseline substitutes only the original
Git/storage helper functions from the revision above; it is not an old-controller versus
new-controller comparison. The recorded sample uses 163 committed product files and
zero live model calls. Snapshot identity and generation tree are identical.

The offline delivery fixture took **46.975 → 8.154 seconds**, with **17,962 → 1,756 Git
process launches**, in this single sample. These are controller/fixture measurements,
not end-to-end live delivery timings or an estimate of every repository's speedup.

Reproduce from the repository root with the explicit historical helper revision:

```bash
python3 checks/benchmark_p2p_git.py --baseline-ref dfe436aa3050ef0d94d2a5a56ae35b84e5dcd11e --delivery
```

The benchmark uses the current `HEAD` for its product fixture; its file count and
identities can differ after this patch is committed. Exact retained sample output:

```json
{
  "repository_commit": "dfe436aa3050ef0d94d2a5a56ae35b84e5dcd11e",
  "files": 163,
  "live_model_calls": 0,
  "baseline": {
    "snapshot": {
      "elapsed_seconds": 0.402307,
      "git_processes": 164,
      "snapshot_key": "snapshot:sha256:9307a2df0eccaa755e3e55989205af6d6e3be48c25ed7b1a8601760ca8132aed"
    },
    "generation": {
      "elapsed_seconds": 0.465139,
      "git_processes": 167,
      "tree": "00368102d0f77ef23dba67d94be61b466d247d5b"
    },
    "fixture_delivery": {"elapsed_seconds": 46.974853, "git_processes": 17962}
  },
  "current": {
    "snapshot": {
      "elapsed_seconds": 0.020423,
      "git_processes": 2,
      "snapshot_key": "snapshot:sha256:9307a2df0eccaa755e3e55989205af6d6e3be48c25ed7b1a8601760ca8132aed"
    },
    "generation": {
      "elapsed_seconds": 0.136959,
      "git_processes": 5,
      "tree": "00368102d0f77ef23dba67d94be61b466d247d5b"
    },
    "fixture_delivery": {"elapsed_seconds": 8.15425, "git_processes": 1756}
  },
  "identical_snapshot": true,
  "identical_generation_tree": true
}
```

## Regression evidence

All tests below use deterministic fixture transport; none establishes a live model's judgment or sandbox enforcement.

| Coverage | Evidence |
| --- | --- |
| Early missing input/service detection, observed commands, identity binding, bounded resume, legacy readiness upgrade | [test_p2p_readiness.py](test_p2p_readiness.py): 9 passed in 29.595 s during focused implementation verification. |
| Retained malformed reports, legacy reserved diagnosis, interruption, bounded correction, progress and strategy handling | [test_p2p_recovery.py](test_p2p_recovery.py); included in full discovery below. |
| Receiving-host capability recheck and preservation of rejected mutator work without acceptance | [test_p2p_portable_recovery.py](test_p2p_portable_recovery.py): independent focused run, 2 passed in 10.323 s. |
| Same-stage isolation, complete content/mode/symlink delta, corrupt evidence and changed identity/environment | [test_p2p_verification_history.py](test_p2p_verification_history.py): independent focused run, 4 passed in 19.273 s. |
| Existing completed-stage portable continuation | `CheckpointTests.test_completed_stage_resumes_on_another_computer_without_old_execution`: 1 passed in 6.049 s. |
| Exact binary/path/mode/symlink handling, invalid or missing objects, ignored-state validation, unchanged refs/index/worktree | [test_p2p_filesystem.py](test_p2p_filesystem.py) and `GenerationTreeTests` in [test_p2p_delivery.py](test_p2p_delivery.py); included in full discovery below. |

### Full discovery and final focused recheck

The repository's default Python 3.11+ gate ran **259 tests in 533.185 s** on Linux
with Python 3.12.14 and Git 2.51.1. Its initial result was four assertion failures,
three historical-fixture errors, and one environment skip. The controller's
functional code was unchanged throughout that run and the corrections below.

All seven failing cases were resolved:

- Two existing Markdown assertions now normalize line wrapping while retaining
  every required authority phrase.
- The blocked-review assertion includes the intentional readiness refresh and
  still forbids proof or repair while the prerequisite remains unavailable.
- A fresh-process CLI fixture now explicitly supplies the offline host so it can
  reach and verify approval transfer and routing behavior.
- Historical comparison fixtures use the original agreement bytes from
  `eb84d66dd70ce8998cd43e951741785e8520c301`, preserve its hash, and explicitly
  supply the old controller's offline host. The live comparison runner is unchanged.
  The missing pinned controller revision was fetched into this checkout.

The final combined recheck covered **all seven corrected cases plus both new
portable recovery cases: 9 tests passed in 24.670 s**. The historical comparison
module also passed all four tests in 6.872 s. All other completed discovery cases
passed; the one skip checks directory-mode denial that root bypasses. Across
discovery and focused rechecks, 260 distinct cases passed and one was skipped.
This is not a claim that the initial full discovery exited successfully. The full
suite was not repeated after changes limited to test fixtures/assertions and docs.

```bash
PYTHONPATH=checks python3 -m unittest -v \
  test_learning_candidates.LearningCandidateTests.test_skill_boundaries_keep_retrospect_as_promoter \
  test_p2p_delivery.DeliveryTests.test_blocked_review_stops_before_proof_and_repair \
  test_p2p_delivery.DeliveryTests.test_public_cli_retains_plain_approval_on_transfer_and_fresh_recovery \
  test_working_style.WorkingStyleRules.test_pragmatism_preserves_rigor_and_authority \
  test_run_delivery_comparison.PilotTests.test_blocked_episode_stops_cohort_and_post_run_configuration_drift \
  test_run_delivery_comparison.PilotTests.test_copied_controllers_repair_order_and_exhaustion \
  test_run_delivery_comparison.PilotTests.test_preparation_order_identity_and_uncertain_repeat \
  test_p2p_portable_recovery
```

The historical tests need the controller revision
`cc27a47f5ee765cff3cf13b21c36f974cb1234ae` and the agreement revision above in
local Git history. Fetch each exact missing revision from `origin` before the
suite when using a checkout without those objects. No model calls are involved.

`git diff --check` passes.

## Boundaries of the evidence

The user's original retained execution directory and failure receipts were not supplied or replayed.
No live macOS worker-boundary check or authenticated model delivery was executed.
The changes and fixture evidence therefore do not establish that the user's interrupted run has recovered.

This report describes the patch under review. It makes no claim that GitHub `main` or installed
workflows are repaired before merge and installation. Active runs retain their admitted stage-skill
hashes: refreshing installed skills does not migrate those runs. Preserve their retained state and
original skill versions; do not edit admission hashes to force an instruction upgrade.
