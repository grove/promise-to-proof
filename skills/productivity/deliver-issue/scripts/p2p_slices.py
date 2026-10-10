"""Bounded, evidence-backed implementation slices on existing delivery state.

No new checkpoint transport, model stage, commit requirement or acceptance verdict.
The controller alone admits a slice after a confirmed worker report, real host
command evidence and an exact Git candidate generation have been saved.
"""
import json
import re
import shlex

import p2p_filesystem as fs

MAX_SLICES = 8
MAX_CHECKS = 6
SLICE_FIELDS = {"id", "requirement_ids", "expected_result", "checks", "paths",
                "outcome", "boundary_reason", "next_action", "retires"}
CHECK_FIELDS = {"kind", "command", "result", "observation"}
RETIRE_FIELDS = {"id", "reason"}


def schema():
    string = {"type": "string"}
    def obj(fields):
        return {"type": "object", "properties": fields, "required": list(fields),
                "additionalProperties": False}
    return obj({
        "id": string,
        "requirement_ids": {"type": "array", "items": string},
        "expected_result": string,
        "checks": {"type": "array", "maxItems": MAX_CHECKS, "items": obj({
            "kind": {"type": "string", "enum": ["test", "inspection", "manual"]},
            "command": string,
            "result": {"type": "string", "enum": ["passed", "observed"]},
            "observation": string,
        })},
        "paths": {"type": "array", "items": string},
        "outcome": {"type": "string", "enum": ["VERIFIED", "BLOCKED"]},
        "boundary_reason": string,
        "next_action": string,
        "retires": {"type": "array", "items": obj({"id": string, "reason": string})},
    })


def _bounded(value, limit=450):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= limit


def _command_matches(recorded, requested):
    if recorded == requested:
        return True
    try:
        parts = shlex.split(recorded)
    except (TypeError, ValueError):
        return False
    return (len(parts) == 3 and parts[0].rsplit("/", 1)[-1] in
            ("sh", "bash", "zsh", "dash") and
            parts[1] in ("-c", "-lc", "-ic", "-lic") and parts[2] == requested)


def active(records):
    retired = {old["id"] for record in records for old in record["slice"]["retires"]}
    return [row for row in records if row["slice"]["id"] not in retired]


def validate(report, requirements, records, host_executions, current_manifest,
             prior_manifest, *, stage="implementation"):
    """Reject unsupported progress before the report is accepted or captured."""
    progress = report.get("implementation_slice")
    if stage != "implementation" or not isinstance(progress, dict) or set(progress) != SLICE_FIELDS:
        raise ValueError("implementation requires exactly one bounded slice progress record")
    if len(records) >= MAX_SLICES:
        raise ValueError("implementation slice budget reached; diagnose a delivery boundary rather than micro-slice")
    expected_id = f"I{len(records) + 1}"
    if progress["id"] != expected_id:
        raise ValueError("implementation slice ID must be " + expected_id)
    ids = progress["requirement_ids"]
    if (not isinstance(ids, list) or not ids or len(ids) != len(set(ids)) or
            not set(ids) <= set(requirements) or not all(isinstance(i, str) for i in ids)):
        raise ValueError("slice requirement IDs are not an exact subset of the accepted contract")
    for key in ("expected_result",):
        if not _bounded(progress[key]):
            raise ValueError("slice expected observable result is missing or excessive")
    for key in ("boundary_reason", "next_action"):
        if not isinstance(progress[key], str) or len(progress[key]) > 450:
            raise ValueError("slice " + key + " is not bounded")
    paths = progress["paths"]
    old_paths = {row["path"] for row in prior_manifest}
    new_paths = {row["path"] for row in current_manifest}
    if (not isinstance(paths, list) or len(set(paths)) != len(paths) or
            any(not isinstance(p, str) or not fs.product_path(p) or
                p not in old_paths | new_paths for p in paths)):
        raise ValueError("slice paths must identify actual old/current product files")
    changes = fs.tree_changes(prior_manifest, current_manifest)
    changed = {item["path"] for item in changes}
    if progress["outcome"] == "VERIFIED" and changed - set(paths):
        raise ValueError("verified slice did not account for all changed product paths")
    checks = progress["checks"]
    if not isinstance(checks, list) or len(checks) > MAX_CHECKS:
        raise ValueError("implementation slice checks are malformed or excessive")
    for check in checks:
        if not isinstance(check, dict) or set(check) != CHECK_FIELDS:
            raise ValueError("slice check has missing or unsupported fields")
        if (check["kind"] not in ("test", "inspection", "manual") or
                check["result"] not in ("passed", "observed") or
                not _bounded(check["command"], 400) or
                not _bounded(check["observation"], 400)):
            raise ValueError("slice check lacks a meaningful observable result")
        executions = [event for event in host_executions
                      if _command_matches(event.get("command"), check["command"])
                      and check["observation"] in event.get("aggregated_output", "")
                      and isinstance(event.get("exit_code"), int)
                      and (check["result"] != "passed" or event["exit_code"] == 0)]
        if not executions:
            raise ValueError("slice check is not grounded in matching host command/output evidence")
    if not isinstance(progress["retires"], list):
        raise ValueError("slice retirements must be explicit")
    previously_active = {item["slice"]["id"] for item in active(records)}
    retired = set()
    for old in progress["retires"]:
        if (not isinstance(old, dict) or set(old) != RETIRE_FIELDS or
                not isinstance(old["id"], str) or old["id"] not in previously_active or
                old["id"] in retired or not _bounded(old["reason"], 240)):
            raise ValueError("slice retirement requires a prior active ID and substantive replacement reason")
        retired.add(old["id"])
    invalidated = {item["slice"]["id"] for item in active(records)
                   if set(item["slice"]["paths"]) & changed}
    if invalidated - retired:
        raise ValueError("changed previously verified slice paths need an explicit checked replacement")
    if progress["outcome"] == "VERIFIED":
        if not checks:
            raise ValueError("verified slice requires exercised test or approved non-test evidence")
        if report["status"] not in ("PARTIAL", "IMPLEMENTED"):
            raise ValueError("verified slice cannot accompany a blocked/incomplete worker verdict")
        if report["status"] == "PARTIAL":
            if not progress["boundary_reason"].strip() or not progress["next_action"].strip():
                raise ValueError("partial implementation needs a justified next complete outcome")
            if not changes and any(item["slice"]["checks"] == checks for item in records):
                raise ValueError("partial implementation repeated an old check without product progress")
            if not report["gaps"]:
                raise ValueError("partial implementation must name its remaining obligation")
        else:
            if report["gaps"] or progress["next_action"].strip():
                raise ValueError("IMPLEMENTED may not leave slice or contract work unfinished")
            covered = set(ids)
            for item in active(records):
                if item["slice"]["id"] not in retired:
                    covered.update(item["slice"]["requirement_ids"])
            if covered != set(requirements):
                raise ValueError("final implementation slices do not cover every accepted obligation")
    elif progress["outcome"] == "BLOCKED":
        if report["status"] in ("IMPLEMENTED", "REPAIRED"):
            raise ValueError("a blocked slice cannot complete implementation")
        if not report["gaps"] or not progress["next_action"].strip():
            raise ValueError("blocked slice needs a real gap and next recovery action")
        if progress["retires"]:
            raise ValueError("blocked work cannot silently retire verified slices")
    else:
        raise ValueError("unsupported slice outcome")
    return progress


def attach(state, attempt, report, generation):
    """Seal one verified slice to its existing attempt, report and Git generation."""
    if state.get("implementation_slice_version") != 1:
        return None
    progress = report["implementation_slice"]
    if progress["outcome"] != "VERIFIED":
        return None
    records = state.setdefault("implementation_slices", [])
    if not generation or (generation.get("source_attempt") or {}).get("attempt_id") != attempt["id"]:
        raise ValueError("slice has no exact completed worker Git generation")
    if (generation["candidate_key"] != state["candidate"]["key"] or
            (generation.get("source_attempt") or {}).get("report_sha256") != attempt.get("report_sha256")):
        raise ValueError("slice Git generation does not bind its saved host report")
    sealed = {
        "slice": progress, "attempt_id": attempt["id"],
        "report_sha256": attempt["report_sha256"],
        "candidate_key": generation["candidate_key"],
        "generation_commit": generation["commit"],
        "generation_record_sha256": generation["record_sha256"],
    }
    previous = next((item for item in records if item["attempt_id"] == attempt["id"]), None)
    if previous:
        if previous != sealed:
            raise ValueError("existing verified implementation slice has conflicting evidence")
        return previous
    if len(records) >= MAX_SLICES or progress["id"] != f"I{len(records) + 1}":
        raise ValueError("unexpected implementation slice sequence")
    records.append(sealed)
    return sealed


def verify_retained(state, runtime, receipts):
    """Validate retained slice references without rerecording them or launching work.

    receipts(attempt) validates current local/portable host exit, report and
    session using the normal delivery controller's established receipt path.
    """
    records = state.get("implementation_slices", [])
    if not records:
        return []
    attempts = {a["id"]: a for a in state["attempts"]}
    generations = state.get("local_git_generations", [])
    ids = []
    for record in records:
        if not isinstance(record, dict) or set(record) != {
                "slice", "attempt_id", "report_sha256", "candidate_key",
                "generation_commit", "generation_record_sha256"}:
            raise ValueError("retained slice has malformed controller identity")
        attempt = attempts.get(record["attempt_id"])
        generation = next((row for row in generations
                           if row.get("commit") == record["generation_commit"]), None)
        if (not attempt or attempt.get("stage") != "implementation" or
                attempt.get("status") != "complete" or
                attempt.get("report_validation") == "rejected" or
                attempt.get("report_sha256") != record["report_sha256"] or
                not generation or
                generation.get("record_sha256") != record["generation_record_sha256"] or
                generation.get("candidate_key") != record["candidate_key"] or
                (generation.get("source_attempt") or {}).get("attempt_id") != attempt["id"]):
            raise ValueError("retained implementation slice references a stale or unverified stage")
        host = receipts(dict(attempt))
        report_data = fs.safe(runtime, attempt["report"]).read_bytes()
        if (fs.digest(report_data) != record["report_sha256"] or
                host["message"].encode() != report_data or
                json.loads(report_data).get("implementation_slice") != record["slice"]):
            raise ValueError("retained slice report changed or lost")
        if record["slice"]["id"] != f"I{len(ids) + 1}":
            raise ValueError("retained slice order is inconsistent")
        ids.append(record["slice"]["id"])
    return records


def progress_view(state):
    records = state.get("implementation_slices", [])
    latest = records[-1] if records else None
    active_ids = [row["slice"]["id"] for row in active(records)] if records else []
    finished = state.get("implementation_complete") is True
    next_action = ("Independent review then proof" if finished else
                   latest["slice"]["next_action"] if latest else
                   "Implement the smallest complete accepted outcome")
    return {
        "verified": len(active_ids), "active": active_ids,
        "retired": sum(len(row["slice"]["retires"]) for row in records),
        "working_candidate": state.get("candidate", {}).get("key"),
        "next_slice": f"I{len(records) + 1}" if not finished else None,
        "next_action": next_action,
        "status": "IMPLEMENTED" if finished else "IN_PROGRESS",
        "authority": "Only saved verified implementation; independent review and proof still required.",
    }
