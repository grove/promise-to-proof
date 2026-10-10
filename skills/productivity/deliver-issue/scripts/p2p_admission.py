"""Deterministic admission decisions; no model or external effects.

The controller supplies checked current-host facts and original host receipts.
An exact identity is reusable only after the owning producer readbacks succeed.
"""
import hashlib
import json

SCHEMA = "promise-to-proof/admission/v1"
OWNERS = {"agreement": "plan-acceptance", "routing": "delivery routing",
          "workspace": "deliver-issue workspace isolation",
          "recovery": "deliver-issue recovery",
          "verifier": "deliver-issue host preflight",
          "prerequisites": "deliver-issue task readiness"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def facts(state, verifier, readiness):
    route = {k: v for k, v in state["routing"].items() if k != "target_tip"}
    return {
        "agreement": digest([state["contract"]["sha256"], state["contract"]["source"],
                             state["contract"]["revision"], state["binding_inputs"],
                             state["requirements"]]),
        "routing": digest([route, state.get("routing_records"), state["comparison_base"],
                           state["starting_commit"]]),
        "workspace": digest([state["invocation_id"], state["source_tree_key"],
                             state["source_index_sha256"], state["excluded_dirty"],
                             state["agreement_paths"]]),
        "recovery": digest([state["invocation_id"], state["base_tree_key"],
                            state["local_git_base"], state["previous_records"]]),
        "verifier": verifier, "prerequisites": digest(readiness)}


def applicability(previous, identities):
    """Unchanged exact material facts may be reused; unknown means recheck."""
    old = {row["name"]: row for row in previous.get("conditions", [])} if isinstance(previous, dict) else {}
    return {name: ("REUSABLE_AFTER_READBACK" if isinstance(value, str) and value and
                    old.get(name, {}).get("identity") == value and
                    old[name].get("status") == "READY" and old[name].get("evidence")
                    else "REFRESH_REQUIRED") for name, value in identities.items()}


def admitted(state, verifier, readiness, receipts, previous=None):
    """Persist only a summary of evidence validated by the actual controller."""
    if not all(receipts.get(k) for k in ("verifier", "prerequisites")):
        raise ValueError("admission requires verified host and prerequisite receipts")
    if state.get("task_readiness", {}).get("status") != "READY":
        raise ValueError("admission requires observed READY prerequisites")
    values = facts(state, verifier, readiness)
    reuse = applicability(previous, values)
    rows = []
    for name, value in values.items():
        evidence = receipts.get(name, "controller-checked-source-route-workspace-recovery")
        rows.append({"name": name, "owner": OWNERS[name], "identity": value,
                     "status": "READY", "evidence": evidence,
                     "applicability": ("REUSED" if reuse[name] == "REUSABLE_AFTER_READBACK"
                                       else "CHECKED")})
    return {"schema": SCHEMA, "status": "ADMITTED", "invocation_id": state["invocation_id"],
            "work_item": state["work_item"], "contract_sha256": state["contract"]["sha256"],
            "comparison_base": state["comparison_base"], "conditions": rows, "blocker": None}


def blocked(state, condition, reason, missing, action):
    if condition not in OWNERS:
        raise ValueError("unknown admission condition")
    return {"schema": SCHEMA, "status": "BLOCKED", "invocation_id": state["invocation_id"],
            "work_item": state["work_item"], "contract_sha256": state["contract"]["sha256"],
            "comparison_base": state["comparison_base"], "failed_condition": condition,
            "owner": OWNERS[condition], "blocker": str(reason),
            "missing_fact": missing, "next_action": action, "conditions": []}
