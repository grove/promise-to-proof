"""Promise continuity projection from an exact #78 decision, never a new sizing pass."""
import json
import re
from pathlib import PurePosixPath
import p2p_issue_topology as topology

SCHEMA = "promise-to-proof/continuity/v1"


def project(decision, references):
    """Bind existing issue/contract references to all original obligations."""
    if decision.get("schema") != topology.SCHEMA or decision.get("identity") != topology.digest(
            {k: v for k, v in decision.items() if k != "identity"}):
        raise ValueError("unverified topology identity")
    if decision["status"] not in ("RECOMMENDED", "RECONCILIATION_REQUIRED"):
        raise ValueError("topology is blocked")
    names = decision["order"]
    if not isinstance(references, dict) or set(references) != set(names):
        raise ValueError("complete unit references are required")
    for name, ref in references.items():
        if not isinstance(ref, dict) or set(ref) != {"work_item", "issue"}:
            raise ValueError("unit needs exact work item and optional issue")
        if not isinstance(ref["work_item"], str) or not re.fullmatch(
                r"\.p2p/work/[a-z0-9-]+/contract\.md", ref["work_item"]):
            raise ValueError("unit contract reference is invalid")
        if ref["issue"] is not None and not re.fullmatch(
                r"https://github\.com/[\w.-]+/[\w.-]+/issues/[1-9]\d*", ref["issue"]):
            raise ValueError("invalid exact issue reference")
    owner = decision["final_acceptance"]["owner"]
    return {"schema": SCHEMA, "topology_identity": decision["identity"],
            "origin": decision["origin"], "shape": decision["shape"],
            "order": names, "references": references,
            "allocation": decision["allocations"],
            "unit_outcomes": {row["id"]: row["outcome"] for row in decision["units"]},
            "prerequisites": {row["id"]: row["blocked_by"] for row in decision["units"]},
            "final_owner": owner, "existing_work": decision["existing_work"]}


def view(record, decision, unit, *, established=()):
    """One current/next action without promoting partial work to full proof."""
    if record.get("schema") != SCHEMA or record.get("topology_identity") != decision.get("identity"):
        raise ValueError("stale origin continuity; reconcile the exact topology")
    if record != project(decision, record["references"]):
        raise ValueError("continuity identity or obligations changed")
    if unit not in record["order"]:
        raise ValueError("unit is absent from originating promise")
    done = set(established)
    if not done <= set(record["order"]):
        raise ValueError("unknown confirmed contribution")
    outstanding = [name for name in record["order"] if name not in done]
    current = record["references"][unit]
    remaining = {ob: [x for x in units if x not in done] for ob, units in record["allocation"].items()}
    next_id = next((name for name in outstanding if name != unit and
                    all(p in done for p in record["prerequisites"][name])), None)
    unresolved = [name for name in outstanding if name != unit]
    if next_id is not None:
        action = "Continue " + (record["references"][next_id]["issue"] or record["references"][next_id]["work_item"])
    elif unresolved:
        action = "Verify prerequisites for " + (record["references"][unresolved[0]]["issue"] or
                                                  record["references"][unresolved[0]]["work_item"])
    else:
        action = "Obtain fresh complete original-promise review and proof from " + str(record["final_owner"])
    return {"origin": record["origin"]["reference"],
            "promise": record["origin"]["promise"], "shape": record["shape"],
            "contribution": record["unit_outcomes"][unit], "unit": unit,
            "unit_reference": current, "remaining_obligations": remaining,
            "final_acceptance_owner": record["final_owner"],
            "complete_original_promise": False,
            "next_action": action,
            "unfinished_units": outstanding,
            "topology_identity": record["topology_identity"]}


def load(root, work, *, checkpoint_files=None):
    """Resolve saved continuity from a unit's existing canonical pointer.

    A pointer is a small file in the unit's normal work directory, not a second
    source of truth. The source remains the origin's slicing.md.
    """
    import p2p_filesystem as fs
    root = __import__("pathlib").Path(root)
    if not fs.WORK.fullmatch(work):
        raise ValueError("invalid work item")
    relative = f".p2p/work/{fs.work_slug(work)}/continuity.json"
    indexed = {(scope, path): data for scope, path, data in (checkpoint_files or [])}
    pointer = indexed.get(("project", relative))
    if pointer is None:
        path = fs.safe(root, relative)
        if not path.is_file():
            return None
        pointer = path.read_bytes()
    value = json.loads(pointer)
    if set(value) != {"origin", "unit", "topology_identity", "record_sha256"}:
        raise ValueError("malformed continuity pointer")
    origin = value["origin"]
    if not fs.WORK.fullmatch(origin):
        raise ValueError("invalid continuity origin")
    location = f".p2p/work/{fs.work_slug(origin)}/slicing.md"
    data = indexed.get(("project", location))
    if data is None:
        path = fs.safe(root, location)
        if not path.is_file():
            raise ValueError("missing originating continuity plan: " + location)
        data = path.read_bytes()
    # One machine-readable fenced block, inside the existing canonical plan.
    matches = re.findall(rb"<!-- p2p-continuity-v1\n(.*?)\n-->", data, re.S)
    if len(matches) != 1:
        raise ValueError("missing or ambiguous continuity in originating slicing plan")
    document = json.loads(matches[0])
    if topology.digest(document) != value["record_sha256"]:
        raise ValueError("origin continuity record changed")
    decision = document["topology"]
    projection = document["continuity"]
    if decision["identity"] != value["topology_identity"]:
        raise ValueError("origin topology changed")
    inspected = view(projection, decision, value["unit"])
    if projection["references"][value["unit"]]["work_item"] != work:
        raise ValueError("continuity points to another work item")
    return inspected


def publication_guard(continuity, body):
    """PRs cannot close an unfinished originating promise by keyword."""
    if continuity is None:
        return body
    origin = continuity["origin"]
    ref = re.escape(origin.split("#")[-1])
    unsafe = re.search(r"(?im)\b(?:close[sd]?|fix(?:es|ed)?|resolve[sd]?)\s*:?[ ]+#" + ref +
                       r"\b|\b(?:close[sd]?|fix(?:es|ed)?|resolve[sd]?)\s+" +
                       re.escape(origin) + r"\b", body)
    if unsafe:
        raise ValueError("PR closes an unfinished originating promise: " + origin)
    return body
