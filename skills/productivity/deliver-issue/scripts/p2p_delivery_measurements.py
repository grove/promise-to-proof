"""Compact privacy-safe P2P delivery measurement records (stdlib only)."""
import datetime
import json
import math
import os
from pathlib import Path

SCHEMA = "promise-to-proof/delivery-measurement/v1"
EXPORT_SCHEMA = "promise-to-proof/delivery-measurement-export/v1"
CATEGORIES = ("input_tokens", "output_tokens", "cached_input_tokens", "reasoning_tokens")


def _epoch(value):
    if not value:
        return None
    try:
        return datetime.datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except (AttributeError, TypeError, ValueError):
        return None


def _number(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0 else None


def _interval_union(attempts, start, end):
    if start is None or end is None or end < start:
        return None
    intervals = []
    for attempt in attempts:
        left, right = _epoch(attempt.get("start")), _epoch(attempt.get("end"))
        if left is None or right is None or right < left:
            return None
        duration = attempt.get("elapsed_seconds")
        if duration is None or abs((right - left) - duration) > 0.001:
            return None
        if left < start or right > end:
            return None
        if right > left:
            intervals.append((left, right))
    total = 0
    rightmost = None
    for left, right in sorted(intervals):
        if rightmost is None or left > rightmost:
            total += right - left
            rightmost = right
        elif right > rightmost:
            total += right - rightmost
            rightmost = right
    return total


def usage(value):
    result = {key: None for key in CATEGORIES}
    extra = {}
    if isinstance(value, dict):
        aliases = {
            "cached_input_tokens": ("cached_input_tokens", "cache_read_input_tokens"),
            "reasoning_tokens": ("reasoning_tokens", "reasoning_output_tokens"),
        }
        for key in ("input_tokens", "output_tokens"):
            result[key] = _number(value.get(key))
        for key, names in aliases.items():
            result[key] = next((_number(value[name]) for name in names if name in value), None)
        known = {name for names in aliases.values() for name in names} | {"input_tokens", "output_tokens"}
        extra = {key: _number(item) for key, item in sorted(value.items())
                 if key not in known and _number(item) is not None}
    return {**result, "other": extra}


def _configuration(state, attempt, runtime):
    host = state.get("host") or {}
    executable = host.get("executable")
    result = {"host": host.get("name"), "host_version": host.get("version"),
              "controller": state.get("policy"),
              "tool": Path(executable).name if isinstance(executable, str) and executable else None,
              "model": None, "model_reasoning_effort": None}
    launch = Path(runtime) / "attempts" / attempt["id"] / "launch.json"
    try:
        config = json.loads(launch.read_text()).get("configuration", {})
    except (OSError, ValueError, TypeError):
        config = {}
    for key in ("model", "model_reasoning_effort"):
        value = config.get(key)
        if isinstance(value, str) and value.strip():
            result[key] = value
    return result


def build(state, runtime, now_epoch=None):
    """Build from retained controller receipts; never reads prompts or response bodies."""
    start = state.get("started_at") or state.get("created")
    end = state.get("ended_at") or state.get("completed_at")
    start_epoch = _epoch(start)
    end_epoch = _epoch(end)
    if end_epoch is None and state.get("status") == "RUNNING" and now_epoch is not None:
        end_epoch = now_epoch
    valid_episode_window = (start_epoch is not None and end_epoch is not None and end_epoch >= start_epoch)
    elapsed = end_epoch - start_epoch if valid_episode_window else None
    attempts = []
    seen = {}
    for item in state.get("attempts", []):
        aid = item.get("id")
        if not isinstance(aid, str) or not aid:
            raise ValueError("attempt identity is missing")
        if aid in seen:
            if seen[aid] != item:
                raise ValueError("conflicting duplicate attempt " + aid)
            continue
        seen[aid] = item
        start = item.get("launch_started")
        finish = item.get("launch_finished")
        reported_duration = _number(item.get("elapsed_seconds"))
        left, right = _epoch(start), _epoch(finish)
        coherent = (valid_episode_window and left is not None and right is not None and right >= left
                    and start_epoch <= left and right <= end_epoch and reported_duration is not None
                    and abs((right - left) - reported_duration) <= 0.001)
        duration = reported_duration if coherent else None
        attempts.append({
            "id": aid, "stage": item.get("stage", "unknown"),
            "reserved_at": item.get("started"), "start": start, "end": finish,
            "elapsed_seconds": duration,
            "status": item.get("status", "unknown"),
            "outcome": item.get("outcome", "unknown"),
            "candidate_key": (item.get("inputs") or {}).get("candidate_key"),
            "usage": usage(item.get("usage")),
            "configuration": _configuration(state, item, runtime),
        })
    attempts.sort(key=lambda row: (row["start"] or "", row["id"]))
    attempt_seconds = (sum(row["elapsed_seconds"] for row in attempts)
                       if all(row["elapsed_seconds"] is not None for row in attempts) else None)
    stage_values = {}
    for row in attempts:
        stage = row["stage"]
        value = stage_values.setdefault(stage, {"attempt_count": 0, "complete_attempts": 0,
                                                 "attempt_seconds": 0, "seconds_known": True})
        value["attempt_count"] += 1
        if row["status"] == "complete":
            value["complete_attempts"] += 1
        if row["elapsed_seconds"] is None:
            value["seconds_known"] = False
        else:
            value["attempt_seconds"] += row["elapsed_seconds"]
    for value in stage_values.values():
        value["attempt_seconds"] = value["attempt_seconds"] if value["seconds_known"] else None
        del value["seconds_known"]
    deadline_start = _number(state.get("deadline_started_epoch"))
    deadline_epoch = _number(state.get("deadline"))
    valid_deadline_window = (valid_episode_window and deadline_start is not None
                             and start_epoch <= deadline_start <= end_epoch)
    pre_deadline = deadline_start - start_epoch if valid_deadline_window else None
    execution_window = end_epoch - deadline_start if valid_deadline_window else None
    attempt_wall_seconds = _interval_union(attempts, start_epoch, end_epoch)
    controller_seconds = (max(0, elapsed - attempt_wall_seconds)
                          if elapsed is not None and attempt_wall_seconds is not None else None)
    controller_timing = state.get("controller_timing", {})
    preflight_attempts = [row for row in attempts if row["stage"].startswith("preflight-")]
    preflight_seconds = (sum(row["elapsed_seconds"] for row in preflight_attempts)
                         if all(row["elapsed_seconds"] is not None for row in preflight_attempts) else None)
    status = state.get("status", "unknown")
    outcomes = {row["outcome"] for row in attempts}
    if status == "REVIEWED_AND_PROVEN":
        outcome = "successful"
    elif status == "RUNNING" and end is None:
        outcome = "running"
    elif "interrupted" in outcomes:
        outcome = "interrupted"
    elif any(row["status"] == "failed" for row in attempts):
        outcome = "failed"
    elif status == "BLOCKED":
        outcome = "blocked"
    else:
        outcome = "unknown"
    contract = state.get("contract", {})
    host_configs = sorted({json.dumps(row["configuration"], sort_keys=True) for row in attempts})
    return {
        "schema": SCHEMA,
        "episode_id": state.get("invocation_id"),
        "work_item": state.get("work_item"),
        "repository_id": (state.get("local_git_base") or {}).get("repository_id"),
        "contract": {"revision": contract.get("revision"), "sha256": contract.get("sha256")},
        "comparison_base": state.get("comparison_base"),
        "candidate_key": (state.get("candidate") or {}).get("key"),
        "candidate_generations": [row.get("candidate_key") for row in state.get("local_git_generations", [])],
        "started_at": start, "ended_at": end,
        "elapsed_seconds": elapsed,
        "pre_deadline_setup_seconds": pre_deadline,
        "deadline_started_at": (datetime.datetime.fromtimestamp(deadline_start, datetime.timezone.utc).isoformat()
                                if deadline_start is not None else None),
        "execution_deadline_at": (datetime.datetime.fromtimestamp(deadline_epoch, datetime.timezone.utc).isoformat()
                                  if deadline_epoch is not None else None),
        "execution_window_seconds": execution_window,
        "controller_seconds": controller_seconds,
        "controller_breakdown_seconds": {
            "setup_admission": pre_deadline,
            "identity_snapshot_validation": _number(controller_timing.get("identity_snapshot_validation")),
            "persistence_readback": _number(controller_timing.get("persistence_readback")),
            "preflight_host_check_attempts": preflight_seconds,
        },
        "attempt_seconds": attempt_seconds,
        "stages": dict(sorted(stage_values.items())),
        "attempts": attempts,
        "dispatch_count": len(attempts),
        "preflight_attempt_count": sum(row["stage"].startswith("preflight-") for row in attempts),
        "repair_count": sum(row["stage"] == "repair" for row in attempts),
        "resume_count": int(state.get("resume_count", 0)),
        "reconciliation_count": int(state.get("reconciliation_count", 0)),
        "retry_count": sum(max(0, count - 1) for count in
                           __import__("collections").Counter(row["stage"] for row in attempts).values()),
        "repair_used": bool(state.get("repair_used", False)),
        "terminal_status": status,
        "terminal_outcome": outcome,
        "host_configurations": [json.loads(value) for value in host_configs],
    }


def write_export(path, record):
    """Write one explicit export without replacing an existing file."""
    path = Path(path).expanduser()
    if path.exists() or path.is_symlink():
        raise ValueError("measurement export already exists: " + str(path))
    if not path.parent.is_dir():
        raise ValueError("measurement export parent directory must already exist")
    payload = json.dumps({"schema": EXPORT_SCHEMA, "episodes": [record]},
                         indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    if path.read_text(encoding="utf-8") != payload:
        raise ValueError("measurement export readback failed")
    return path
