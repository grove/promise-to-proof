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



def persist(root, origin_work, decision, references):
    """Save readback-verified canonical slicing block and tiny unit pointers.

    No tracker, Git or candidate effects. Refuse to replace a conflicting
    identity; topology changes require explicit prior reconciliation.
    """
    import p2p_filesystem as fs
    root = __import__("pathlib").Path(root)
    if not fs.WORK.fullmatch(origin_work):
        raise ValueError("invalid original work path")
    if decision["origin"]["contract"] != origin_work:
        raise ValueError("origin contract differs from selected topology")
    record = project(decision, references)
    owner = f".p2p/work/{fs.work_slug(origin_work)}"
    plan = fs.safe(root, owner + "/slicing.md")
    if not plan.is_file() or plan.is_symlink():
        raise ValueError("existing canonical slicing plan is required")
    previous = plan.read_bytes()
    if previous.count(b"<!-- p2p-continuity-v1") > 1:
        raise ValueError("ambiguous prior continuity section")
    document = {"topology": decision, "continuity": record}
    content = json.dumps(document, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False).encode("utf-8")
    block = b"<!-- p2p-continuity-v1\\n" + content + b"\\n-->".replace(b"\\n", b"\n")
    from re import compile as regex
    pattern = regex(rb"<!-- p2p-continuity-v1\n.*?\n-->", re.S)
    old = pattern.search(previous)
    if old:
        prior = json.loads(old.group()[len(b"<!-- p2p-continuity-v1\n"):-len(b"\n-->")])
        if prior.get("topology", {}).get("identity") != decision["identity"]:
            raise ValueError("topology changed; reconcile old continuity and existing work first")
        changed = previous[:old.start()] + block + previous[old.end():]
    else:
        changed = previous + (b"\n" if previous and not previous.endswith(b"\n") else b"") + block + b"\n"
    # Reject colliding or unrecognized pointers before modifying any file.
    pointers = []
    for unit, ref in references.items():
        path = fs.safe(root, f".p2p/work/{fs.work_slug(ref['work_item'])}/continuity.json")
        if not fs.safe(root, ref["work_item"]).is_file():
            raise ValueError("unit contract missing: " + ref["work_item"])
        pointer = {"origin": origin_work, "unit": unit,
                   "topology_identity": decision["identity"],
                   "record_sha256": topology.digest(document)}
        data = json.dumps(pointer, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        if path.is_symlink():
            raise ValueError("continuity pointer is a symlink")
        if path.exists():
            previous_pointer = json.loads(path.read_bytes())
            if (previous_pointer.get("origin"), previous_pointer.get("unit")) != (origin_work, unit):
                raise ValueError("existing continuity pointer belongs to another origin/unit")
            if previous_pointer.get("topology_identity") != decision["identity"]:
                raise ValueError("unit topology changed; reconcile before writing")
        pointers.append((path, data))
    if previous != changed:
        archive = fs.safe(root, owner + "/history/" + fs.digest(previous) + "/slicing.md")
        archive.parent.mkdir(parents=True, exist_ok=True)
        if archive.exists() and archive.read_bytes() != previous:
            raise ValueError("conflicting retained slicing history")
        if not archive.exists():
            fs.atomic_write(archive, previous, ignored_root=root)
        fs.atomic_write(plan, changed, ignored_root=root)
        if plan.read_bytes() != changed:
            raise ValueError("origin slicing readback failed")
    for path, data in pointers:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_bytes() != data:
            fs.atomic_write(path, data, ignored_root=root)
        if path.read_bytes() != data:
            raise ValueError("unit continuity pointer readback failed")
        # Verify consumers retrieve the same single canonical record.
        view_result = load(root, references[next(k for k, v in references.items()
                             if fs.work_slug(v["work_item"]) == path.parent.name)]["work_item"])
        if view_result["topology_identity"] != decision["identity"]:
            raise ValueError("unit continuity readback identity mismatch")
    return {"status": "PRESERVED", "origin": origin_work,
            "topology_identity": decision["identity"],
            "record_sha256": topology.digest(document),
            "unit_count": len(pointers), "tracker_effects": 0}

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
