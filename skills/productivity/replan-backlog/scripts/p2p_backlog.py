"""Pure affected-backlog decisions; observed evidence remains the caller's responsibility."""
from collections import defaultdict

CATEGORIES = {"SHIPPED", "PARTIAL", "PENDING_PR", "VALIDATION_PENDING", "UNRELATED", "UNKNOWN"}


def assess(issues, *, all_open=False):
    """Evaluate inspected obligations; no tracker reads/writes or claim of proof."""
    result = []
    for issue in issues:
        if not all_open and not issue.get("affected", False):
            continue
        if issue.get("state") != "open":
            continue
        promises = issue.get("obligations", [])
        if not promises or len({p["id"] for p in promises}) != len(promises):
            raise ValueError("issue requires distinct original obligations")
        states = {p["state"] for p in promises}
        if not states <= {"shipped", "missing", "pending_pr", "needs_validation", "unknown"}:
            raise ValueError("unknown obligation evidence state")
        for p in promises:
            if not p.get("promise") or p["state"] != "missing" and not p.get("evidence"):
                raise ValueError("non-missing obligation needs retrievable evidence and promise")
        if issue.get("active_contract"):
            kind, change = "UNKNOWN", "KEEP"
            reason = "Active accepted delivery remains pinned; use plan-acceptance for material amendments."
        elif states == {"shipped"}:
            kind, change = "SHIPPED", "CLOSE"
            reason = "All original obligations have concrete shipped evidence; propose historical completion."
        elif "pending_pr" in states and not (states - {"pending_pr", "missing"}):
            kind, change = "PENDING_PR", "KEEP"
            reason = "Changes are not landed; keep the issue open."
        elif "needs_validation" in states:
            kind, change = "VALIDATION_PENDING", "VERIFY"
            reason = "Required validation is not established; do not mark delivered."
        elif "unknown" in states:
            kind, change = "UNKNOWN", "RECONCILE"
            reason = "A material outcome or its source applicability is unverified."
        elif "shipped" in states:
            kind, change = "PARTIAL", "NARROW"
            reason = "Preserve shipped work as history and narrow to unfulfilled obligations."
        else:
            kind, change = "UNRELATED" if not issue.get("affected") else "UNKNOWN", "KEEP"
            reason = "No evidenced shipped contribution to remove."
        remaining = [p["id"] for p in promises if p["state"] != "shipped"]
        result.append({"id": issue["id"], "category": kind, "action": change,
                       "reason": reason, "remaining": remaining,
                       "shipped": [p["id"] for p in promises if p["state"] == "shipped"],
                       "active_contract": bool(issue.get("active_contract")),
                       "amendment_handoff": "plan-acceptance" if issue.get("material_amendment") else None})
    return result


def roadmap(items):
    """Stable hard-dependency waves; preferred order is advisory, not a hard edge."""
    ids = {item["id"] for item in items}
    if len(ids) != len(items):
        raise ValueError("duplicate roadmap issue")
    required = {}
    for item in items:
        deps = item.get("hard_dependencies", [])
        if len(set(deps)) != len(deps):
            raise ValueError("duplicate hard prerequisite")
        unknown = set(deps) - ids
        if unknown:
            raise ValueError("unresolved prerequisite: " + ", ".join(sorted(map(str, unknown))))
        required[item["id"]] = set(deps)
    outstanding = set(ids)
    waves = []
    while outstanding:
        ready = sorted((i for i in outstanding if not required[i] & outstanding), key=str)
        if not ready:
            raise ValueError("hard prerequisite cycle: " + ", ".join(sorted(map(str, outstanding))))
        waves.append(ready)
        outstanding -= set(ready)
    return {"parallel_waves": waves,
            "next": waves[0][0] if waves and waves[0] else None,
            "preferred_order": [item["id"] for item in sorted(items, key=lambda x: (x.get("preferred_rank", 9999), str(x["id"])))],
            "hard_dependencies": {str(k): sorted(v, key=str) for k, v in required.items()}}
