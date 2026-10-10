"""Issue tracker *shape* after an existing evidence-backed sizing decision.

Pure, conservative validation. It does not size work, edit contracts, create
issues, migrate candidates, or perform remote effects. The canonical record
belongs in the originating work item's existing slicing.md. Remote closure is
a separately authorized, readback-first workflow.
"""
import hashlib
import json
import re

import p2p_autonomy as autonomy

SCHEMA = "promise-to-proof/issue-topology/v1"
SHAPES = {"standalone-sequence", "parent-tree"}
HEX = re.compile(r"[0-9a-f]{64}\Z")
ISSUE = re.compile(r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#([1-9][0-9]*)\Z")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def require_text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(name + " must be nonempty")
    return value


def _ordered_unique(values, name):
    if not isinstance(values, list) or not values or any(
            not isinstance(x, str) or not x.strip() for x in values) or len(values) != len(set(values)):
        raise ValueError(name + " must be a nonempty list of distinct references")
    return values


def choose(request):
    """Use #76/#77-established units only; do not invent a new sizing judgment.

    A requested linear order is an implementation preference, NOT an implicit
    prerequisite edge. The caller must supply separately justified blockers.
    """
    if not isinstance(request, dict):
        raise ValueError("missing topology request")
    origin = request.get("origin")
    sizing = request.get("sizing")
    factors = request.get("factors")
    units = request.get("units")
    order = request.get("order")
    if not isinstance(origin, dict) or not isinstance(sizing, dict) or not isinstance(factors, dict):
        raise ValueError("origin, existing sizing and topology factors are required")
    for name in ("reference", "contract", "revision", "promise"):
        require_text(origin.get(name), "origin." + name)
    if not HEX.fullmatch(str(origin.get("sha256", ""))):
        raise ValueError("exact originating contract sha256 required")
    obligations = _ordered_unique(origin.get("obligations"), "origin.obligations")
    if sizing.get("decision") != "SPLIT" or not HEX.fullmatch(str(sizing.get("identity", ""))):
        raise ValueError("topology requires an exact existing #76/#77 SPLIT decision")
    require_text(sizing.get("evidence"), "retained sizing evidence")
    require_text(sizing.get("reason"), "retained sizing rationale")
    flags = ("naturally_sequential", "parallel_ownership", "long_lived_aggregate",
             "independent_parent_integration")
    if any(type(factors.get(name)) is not bool for name in flags):
        raise ValueError("topology factors need explicit true/false observations")
    require_text(factors.get("reason"), "topology reason")
    if not isinstance(units, list) or len(units) < 2:
        raise ValueError("sizing must establish at least two useful delivery units")
    ids = []
    allocations = {name: [] for name in obligations}
    for unit in units:
        if not isinstance(unit, dict):
            raise ValueError("malformed sizing unit")
        name = require_text(unit.get("id"), "unit id")
        if not re.fullmatch(r"S[1-9][0-9]*", name) or name in ids:
            raise ValueError("duplicate or invalid stable unit id: " + name)
        ids.append(name)
        require_text(unit.get("outcome"), "unit outcome")
        contributions = _ordered_unique(unit.get("contributes"), name + " contributions")
        for obligation in contributions:
            if obligation not in allocations:
                raise ValueError(name + " invents an originating obligation: " + obligation)
            allocations[obligation].append(name)
        if unit.get("status") not in ("pending", "active", "historical-complete"):
            raise ValueError("unit status must be pending, active, or historical-complete")
        blocked_by = unit.get("blocked_by")
        if not isinstance(blocked_by, list) or any(not isinstance(x, str) for x in blocked_by):
            raise ValueError("actual blockers must be an explicit list")
        if len(blocked_by) != len(set(blocked_by)):
            raise ValueError("duplicate unit blocker")
    if any(not rows for rows in allocations.values()):
        raise ValueError("unallocated original obligations: " +
                         ", ".join(name for name, rows in allocations.items() if not rows))
    if set(ids) != set(_ordered_unique(order, "sizing order")):
        raise ValueError("order must include each exact sized unit once")
    pos = {name: i for i, name in enumerate(order)}
    for unit in units:
        for prerequisite in unit["blocked_by"]:
            if prerequisite not in pos or pos[prerequisite] >= pos[unit["id"]]:
                raise ValueError("unknown, cyclic or out-of-order material prerequisite: " +
                                 prerequisite + " -> " + unit["id"])
    work = request.get("existing_work", [])
    if not isinstance(work, list):
        raise ValueError("existing-work inventory is required")
    seen = set()
    for item in work:
        if not isinstance(item, dict):
            raise ValueError("malformed existing work inventory")
        ref = require_text(item.get("reference"), "retained candidate/PR/review reference")
        if ref in seen:
            raise ValueError("duplicate existing work reference")
        seen.add(ref)
        if item.get("ownership") not in (*ids, "shared", "historical", "unresolved"):
            raise ValueError("existing work needs an explicit attribution")
        require_text(item.get("identity"), "retained work identity")
        if type(item.get("affects_boundary")) is not bool:
            raise ValueError("existing work needs explicit boundary impact")
    parent_reasons = [name for name in flags[1:] if factors[name]]
    shape = ("standalone-sequence" if factors["naturally_sequential"] and
             not parent_reasons else "parent-tree")
    indexed = {row["id"]: row for row in units}
    pending = [name for name in order if indexed[name]["status"] != "historical-complete"]
    active = [name for name in pending if indexed[name]["status"] == "active"]
    final_owner = order[-1] if shape == "standalone-sequence" else origin["reference"]
    status = "RECOMMENDED"
    reason = (factors["reason"] + (" A useful persistent parent is needed for " +
              ", ".join(parent_reasons) + "." if parent_reasons else
              " The final replacement owns complete cross-step acceptance; no parent lifecycle is needed.")
              if shape == "parent-tree" or factors["naturally_sequential"] else
              factors["reason"] + " Natural sequential delivery was not established; retain the existing useful parent.")
    if shape == "standalone-sequence" and len(active) > 1:
        status = "BLOCKED"
        reason = "Several standalone units are active; reconcile one current issue without changing their saved work."
    unresolved = [row["reference"] for row in work
                  if row["ownership"] == "unresolved" and row["affects_boundary"]]
    if unresolved:
        status = "BLOCKED"
        reason = "Ownership affects the proposed boundary and is unresolved: " + ", ".join(unresolved)
    previous = request.get("existing_shape")
    if previous is not None and previous not in SHAPES:
        raise ValueError("unknown existing topology")
    if status != "BLOCKED" and previous is not None and previous != shape:
        status = "RECONCILIATION_REQUIRED"
        reason += " Existing tracker shape differs: preview exact retained links, PRs and approvals before any change."
    result = {
        "schema": SCHEMA, "status": status, "shape": shape,
        "origin": origin, "sizing": sizing, "topology_reason": reason,
        "order": order, "allocations": allocations,
        "units": [{**indexed[name], "next": (order[i + 1] if i + 1 < len(order) else None)}
                  for i, name in enumerate(order)],
        "current": active[0] if active else (pending[0] if pending else None),
        "next": next((name for name in pending
                      if name != (active[0] if active else (pending[0] if pending else None))), None),
        "remaining_obligations": obligations,
        "final_acceptance": {
            "owner": final_owner, "covers": obligations,
            "requires": "Fresh independent review and proof of the complete originating promise "
                        "on one exact combined candidate and base; earlier reports never compose into proof."},
        "existing_work": work, "existing_shape": previous,
        "tracker_effects_authorized": False,
    }
    result["identity"] = digest(result)
    return result


def supersession_preview(decision, origin_issue, replacements):
    """Read-only exact closure preview; neither a planning decision nor a grant."""
    if (decision.get("status") != "RECOMMENDED" or
            decision.get("shape") != "standalone-sequence"):
        raise ValueError("closure requires a reconciled standalone topology decision")
    match = ISSUE.fullmatch(decision["origin"]["reference"])
    if not match:
        raise ValueError("origin is not one exact GitHub issue")
    repository, number = match.groups()
    if not isinstance(origin_issue, dict) or (
            origin_issue.get("repository"), origin_issue.get("number"),
            origin_issue.get("state")) != (repository, int(number), "open"):
        raise ValueError("originating issue identity or open state changed")
    require_text(origin_issue.get("body"), "originating issue body")
    if len(replacements) != len(decision["order"]):
        raise ValueError("every replacement must have a confirmed tracker issue")
    lines = [
        f"<!-- grove:issue-topology-supersession origin={decision['origin']['reference']} plan={decision['identity']} -->",
        "This originating issue is **superseded for tracking only**, not delivered.",
        "Its original promise and historical discussion remain intact.",
        "",
        "Replacement sequence (complete original obligations retained):",
    ]
    refs = set()
    for i, name in enumerate(decision["order"], 1):
        row = replacements[i - 1]
        if not isinstance(row, dict) or row.get("id") != name:
            raise ValueError("replacement order/identity changed")
        url = row.get("url")
        pattern = r"https://github\.com/" + re.escape(repository) + r"/issues/[1-9][0-9]*"
        if not isinstance(url, str) or not re.fullmatch(pattern, url) or url in refs:
            raise ValueError("each replacement needs a distinct exact GitHub issue URL")
        refs.add(url)
        body = require_text(row.get("body"), "replacement issue body")
        marker = f"<!-- grove:issue-topology origin={decision['origin']['reference']} unit={name} -->"
        if marker not in body or decision["origin"]["reference"] not in body:
            raise ValueError("replacement source link or stable identity marker missing: " + name)
        lines.append(f"{i}. [{name}: {decision['units'][i - 1]['outcome']}]({url})")
        if decision["units"][i - 1]["blocked_by"]:
            lines.append("   Real prerequisites: " + ", ".join(decision["units"][i - 1]["blocked_by"]))
    lines += ["", "Final acceptance owner: " + replacements[-1]["url"],
              "The final replacement must independently review and prove the complete original "
              "agreement, including every original obligation and cross-step interaction. "
              "Earlier ticket closure, PR merges, and separate proof reports do not establish this.",
              "Original requirements: " + ", ".join(decision["remaining_obligations"])]
    body = "\n".join(lines) + "\n"
    value = {"schema": SCHEMA, "origin": decision["origin"]["reference"],
             "repository": repository, "number": int(number),
             "plan_identity": decision["identity"],
             "origin_body_sha256": digest(origin_issue["body"]),
             "replacements": [{"id": row["id"], "url": row["url"],
                               "body_sha256": digest(row["body"])} for row in replacements],
             "comment": body, "close_reason": "not_planned", "effect": "superseded_not_delivered"}
    value["sha256"] = digest(value)
    return value


def authorize_supersession(preview, mandate, approval, origin_issue, replacements):
    """Check *separate* exact effect grants, approval and fresh readbacks.

    Return executable intentions only. The configured tracker workflow owns
    writing a comment, closing with not_planned and checking the results.
    """
    if not isinstance(approval, dict) or approval.get("preview_sha256") != preview.get("sha256"):
        raise ValueError("exact supersession preview approval is missing or stale")
    require_text(approval.get("source"), "separate supersession approval source")
    if digest(origin_issue.get("body")) != preview["origin_body_sha256"] or (
            origin_issue.get("repository"), origin_issue.get("number"),
            origin_issue.get("state")) != (preview["repository"], preview["number"], "open"):
        raise ValueError("origin changed before approved tracker effects")
    if [{"id": row.get("id"), "url": row.get("url"),
         "body_sha256": digest(row.get("body"))} for row in replacements] != preview["replacements"]:
        raise ValueError("replacement issue identity or human edits changed since preview")
    destination = "#" + str(preview["number"])
    for effect in ("issue-comment", "issue-close"):
        autonomy.authorize(mandate, effect, preview["repository"], destination)
    return {"status": "AUTHORIZED_NOT_EXECUTED", "comment": preview["comment"],
            "close_reason": "not_planned", "origin": preview["origin"],
            "preview_sha256": preview["sha256"], "effects": ["issue-comment", "issue-close"]}


def supersession_readback(preview, origin_issue, comments):
    """Never turn uncertain tracker effects into a completed-product claim."""
    if (origin_issue.get("repository") != preview["repository"] or
            origin_issue.get("number") != preview["number"] or
            digest(origin_issue.get("body")) != preview["origin_body_sha256"]):
        return {"status": "PARTIAL", "reason": "originating issue changed; preserve links and reconcile"}
    seen = [row for row in comments if isinstance(row, dict) and
            row.get("body") == preview["comment"] and row.get("url")]
    if len(seen) != 1 or origin_issue.get("state") != "closed" or (
            origin_issue.get("state_reason") != "not_planned"):
        return {"status": "PARTIAL", "reason": "exact comment and not-planned closure need readback"}
    return {"status": "SUPERSEDED", "issue": preview["origin"],
            "comment_url": seen[0]["url"], "reason": "tracking replaced; outcome not delivered",
            "final_acceptance_owner": preview["replacements"][-1]["url"]}
