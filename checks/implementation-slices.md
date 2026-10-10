# Verified implementation slices (#55)

A normal small or coherent change is one implementation slice. A genuinely
multi-part change can return `PARTIAL` **only after one useful, independently
observed result**, with accepted requirement IDs, relevant paths, a real
command/output observation, a justified boundary and one next action. WIP=1
means one active slice, not per-file tasks. There is no additional model
planner, user approval, code commit or progress archive.

The controller accepts `VERIFIED` only with a completed implementation
host receipt and concrete matching command/output evidence. The captured
Git generation, saved report hash and original stage attempt are retained.
No matching evidence means the slice is unverified. Actual non-test
inspection/manual observations are supported. Later edits to paths protected
by a previous slice require an explicit retirement reason and new checked
replacement; obsolete internal strategy never changes the accepted promise.

At a verified partial boundary, the existing #82 portable checkpoint carries
the exact controller state and candidate Git objects. Resume continues
the first unfinished slice rather than repeating earlier verified work,
including after a checkpoint → Git remote → clone → receiving-host restore.
That receiving host must still perform fresh preflight and capability checks.
Uncertain worker completion remains blocked; its evidence is never fabricated.
The final `IMPLEMENTED` handoff covers every accepted requirement and the
exact current candidate, **not** independent REVIEWED, PROVEN or publication.

## Validate

```sh
python3 -m unittest discover -s checks -p 'test_p2p_slices.py' -v
```

Tests exercise one-slice and two-slice implementations, interrupted and
portable intra-stage resume, verified Git generations, missing/mismatched
checks, relevant manual inspection, retired internal plans and invalidated
previous paths. The existing review, proof, recovery, checkpoint and #73
regressions remain active in CI.

These are offline fixtures with a simulated host, **not authenticated live
model behavior**. There is no claim about real Codex completion-time savings.
The live-host boundary and independent verifier quality must still be checked
on supported macOS/Codex execution.
