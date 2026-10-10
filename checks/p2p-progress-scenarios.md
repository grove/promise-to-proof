# Human-readable progress scenarios for issue #84

These are **human-runnable presentation checks**, not live Codex host evidence.
They use the same deterministic explanation function as the existing controller.
The source of truth remains the real contract, controller result, candidate,
portable checkpoint, PR readback and (when available) final receipt. This
script does not create a work item, authorize an effect, contact GitHub, or
start a worker.

From the repository root, run:

```bash
python3 -m unittest discover -s checks -p 'test_p2p_progress.py' -v

python3 - <<'PY'
import sys
sys.path.insert(0, "skills/productivity/deliver-issue/scripts")
import p2p_progress as progress

base = {
    "work_item": ".p2p/work/example/contract.md",
    "status": "RUNNING", "blocker": None,
    "candidate": {"key": "snapshot:sha256:" + "a" * 64},
    "candidate_workspace": "/retained/execution/runtime/workspace",
    "progress": {"stage": "implementation", "controller_running": True},
    "reports": {}, "attempts": [],
}
cases = [
    ("PLANNING AWAITING APPROVAL", {
        "status": "AWAITING_APPROVAL", "candidate_workspace": None,
    }, None),
    ("EXECUTING", {}, None),
    ("#85 BLOCKED HOST AFTER AUDIT", {
        "status": "BLOCKED",
        "blocker": "Codex app-server initialization failed (Operation not permitted)",
        "attempts": [
            {"stage": "planning", "status": "complete"},
            {"stage": "planning-audit", "status": "complete"},
        ],
        "progress": {"stage": "preflight", "controller_running": False},
        "resume_count": 1,
    }, None),
    ("RESTORED ON A NEW HOST", {
        "checkpoint_restored_from": "f" * 64,
        "fresh_host_preflight_complete": False,
        "progress": {"stage": "review", "controller_running": False},
    }, None),
    ("LOCAL REVIEWED + PROVEN", {
        "status": "REVIEWED_AND_PROVEN",
        "progress": {"stage": "proof", "controller_running": False},
    }, None),
    ("OPEN PR", {
        "status": "REVIEWED_AND_PROVEN",
    }, {
        "verified": True, "status": "OPEN", "url": "https://github.com/owner/repo/pull/9",
        "is_draft": True, "target": "main",
    }),
    ("MERGED BUT RECEIPT PENDING", {
        "status": "REVIEWED_AND_PROVEN",
    }, {
        "verified": True, "status": "MERGED", "url": "https://github.com/owner/repo/pull/9",
        "is_draft": False, "target": "main", "merge_commit": "1" * 40,
    }),
]
for label, changes, publication in cases:
    shown = progress.explain(base | changes, publication=publication)
    print("\n### " + label + "\n" + shown["message"])
    print("WHERE:", shown["where_is_the_code"])
    print("USER ACTION:", shown["requires_user_action"])
    print("NOT ESTABLISHED:", ", ".join(shown["not_yet_established"]))
PY
```

After reading the output **without consulting raw controller state**, ask:

1. In the #85 blocked-host example, did implementation or independent live
   review/proof start? **No**. Did the independent audit itself approve the
   exact agreement? **No**. What is the next workable response? Resolve the
   host restriction or obtain a supported execution path, reconcile retained
   state; do not blindly retry the identical failed command.
2. In the restored case, what survived? Saved work and earlier evidence.
   What is still missing? A fresh preflight and evidence of a current worker
   on the receiving host.
3. After local REVIEWED + PROVEN, where are the files? In the isolated candidate
   workspace, not implicitly copied into the operator's checkout or merged.
   Is publication authority inferred? **No**.
4. Is the open PR merged? **No**. What must happen before a merge claim?
   Authoritative current PR state and product-tree identity readback.
5. If GitHub confirms the matching PR was merged, may the assistant claim
   final delivery receipt or verified mapping to squash/rebase output?
   **No**. The #50/#47 finalization receipt remains pending.
6. Does a closed child issue or successful child delivery prove its parent?
   **No**. Its assembled candidate requires full independent parent acceptance.
7. Can a log timestamp, an invalid response or an audit's
   `READY_FOR_APPROVAL` be described as a verified successful stage or user
   approval? **No**.

The full focused suite additionally asserts that changing the PR's head tree,
publication marker, contract hash, destination branch or merged-at/commit facts
cannot turn unverified external state into a published/merged claim. The tests
also exercise the actual offline controller transport to verify that status
and `status --human` reuse retained records with **zero new model dispatches**.

On a real supported macOS/Codex host, invoke an existing retained delivery's
read-only `status .p2p/work/<slug>/contract.md --human`. With an authorized,
already published matching PR, add `--pr https://github.com/OWNER/REPO/pull/N`.
Compare the explanation with the current PR page and candidate report; this
requires no remote write or extra approval. If the host is blocked, do not
run a fresh model or change the recovered invocation just for this check.

Report unavailable live-host or GitHub credentials honestly. Fixture results
demonstrate deterministic rendering, not live agent correctness.
