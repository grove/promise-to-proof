#!/usr/bin/env python3
"""Compare retained P2P measurements without inferring cost, effort, or correctness."""
import argparse
import json
from pathlib import Path
import sys

from p2p_delivery_measurements import EXPORT_SCHEMA, SCHEMA


def compare(data):
    if not isinstance(data, dict) or data.get("schema") != EXPORT_SCHEMA:
        raise ValueError("measurement export schema is unsupported")
    episodes = data.get("episodes")
    if not isinstance(episodes, list) or len(episodes) < 2:
        raise ValueError("at least two episode measurements are required")
    if any(not isinstance(row, dict) or row.get("schema") != SCHEMA for row in episodes):
        raise ValueError("episode measurement schema is unsupported")
    identities = [row.get("episode_id") for row in episodes]
    if any(not isinstance(value, str) or not value for value in identities) or len(set(identities)) != len(identities):
        raise ValueError("episode identities must be present and unique")
    groups = {}
    for episode in episodes:
        contract = episode.get("contract")
        if not isinstance(contract, dict):
            contract = {}
        key = (episode.get("repository_id"), episode.get("work_item"), contract.get("revision"),
               contract.get("sha256"), episode.get("comparison_base"))
        if any(not isinstance(value, str) or not value.strip() for value in key):
            continue
        groups.setdefault(key, []).append(episode)
    adjudications = data.get("independent_adjudications", {})
    if not isinstance(adjudications, dict):
        raise ValueError("independent_adjudications must be an object")
    rows = []
    for key, members in sorted(groups.items(), key=lambda item: tuple(str(v or "") for v in item[0])):
        if len(members) < 2:
            continue
        members = sorted(members, key=lambda row: row["episode_id"])
        stages = sorted({stage for row in members for stage in (row.get("stages") or {})})
        stage_values = {}
        for stage in stages:
            stage_values[stage] = []
            for row in members:
                attempts = [attempt for attempt in row.get("attempts", []) if attempt.get("stage") == stage]
                categories = ("input_tokens", "output_tokens", "cached_input_tokens", "reasoning_tokens")
                token_usage = {
                    key: (sum(attempt["usage"][key] for attempt in attempts)
                          if attempts and all(attempt.get("usage", {}).get(key) is not None for attempt in attempts)
                          else None)
                    for key in categories}
                other_keys = {key for attempt in attempts for key in attempt.get("usage", {}).get("other", {})}
                token_usage["other"] = {
                    key: (sum(attempt["usage"]["other"][key] for attempt in attempts)
                          if attempts and all(key in attempt.get("usage", {}).get("other", {}) for attempt in attempts)
                          else None)
                    for key in sorted(other_keys)}
                other_keys = {key for attempt in attempts for key in attempt.get("usage", {}).get("other", {})}
                token_usage["other"] = {
                    key: (sum(attempt["usage"]["other"][key] for attempt in attempts)
                          if attempts and all(key in attempt.get("usage", {}).get("other", {}) for attempt in attempts)
                          else None)
                    for key in sorted(other_keys)}
                stage_values[stage].append({
                    "episode_id": row["episode_id"],
                    "attempt_seconds": (row.get("stages") or {}).get(stage, {}).get("attempt_seconds"),
                    "attempt_count": (row.get("stages") or {}).get(stage, {}).get("attempt_count", 0),
                    "tokens": token_usage})
        configurations = [row.get("host_configurations", []) for row in members]
        fields = sorted({field for values in configurations for config in values for field in config})
        differences = {field: sorted({config.get(field) for values in configurations for config in values},
                                     key=lambda value: "" if value is None else str(value))
                       for field in fields
                       if len({json.dumps(config.get(field), sort_keys=True) for values in configurations for config in values}) > 1}
        candidate_differences = {}
        for field in ("candidate_key", "candidate_generations"):
            values = {json.dumps(row.get(field), sort_keys=True) for row in members}
            if len(values) > 1:
                candidate_differences[field] = [json.loads(value) for value in sorted(values)]
        configuration_unknowns = []
        for episode in members:
            fields = sorted({field for config in episode.get("host_configurations", [])
                             for field, value in config.items()
                             if value is None or isinstance(value, str) and not value.strip()})
            if fields:
                configuration_unknowns.append({"episode_id": episode["episode_id"], "fields": fields})
        compared = []
        for episode in members:
            independent = adjudications.get(episode["episode_id"])
            if independent is not None and (not isinstance(independent, dict) or
                    independent.get("outcome") not in ("satisfactory", "defective", "unresolved") or
                    not isinstance(independent.get("source"), str) or not independent["source"].strip()):
                raise ValueError("independent adjudication requires an outcome and separate source")
            compared.append({
                "episode_id": episode["episode_id"],
                "candidate_key": episode.get("candidate_key"),
                "candidate_generations": episode.get("candidate_generations"),
                "elapsed_seconds": episode.get("elapsed_seconds"),
                "stages": {stage: (episode.get("stages") or {}).get(stage, {}).get("attempt_seconds")
                           for stage in stages},
                "tokens": {key: sum(attempt["usage"][key] for attempt in episode.get("attempts", []))
                           if episode.get("attempts") and all(attempt.get("usage", {}).get(key) is not None
                                                               for attempt in episode.get("attempts", [])) else None
                           for key in ("input_tokens", "output_tokens", "cached_input_tokens", "reasoning_tokens")},
                "other_tokens": {key: sum(attempt["usage"]["other"][key] for attempt in episode.get("attempts", []))
                                 if episode.get("attempts") and all(key in attempt.get("usage", {}).get("other", {})
                                                                    for attempt in episode.get("attempts", [])) else None
                                 for key in sorted({key for attempt in episode.get("attempts", [])
                                                    for key in attempt.get("usage", {}).get("other", {})})},
                "terminal_outcome": episode.get("terminal_outcome"),
                "independent_outcome": independent,
                "configuration": episode.get("host_configurations", []),
            })
        rows.append({
            "identity": {"repository_id": key[0], "work_item": key[1],
                         "contract_revision": key[2], "contract_sha256": key[3],
                         "comparison_base": key[4]},
            "episodes": compared, "stages": stage_values,
            "configuration_differences": differences,
            "configuration_unknowns": configuration_unknowns,
            "candidate_identity_differences": candidate_differences,
            "unknowns": sorted({
                metric for episode in compared
                for metric, value in [("elapsed_seconds", episode["elapsed_seconds"]),
                                      *[("stage:" + stage, seconds) for stage, seconds in episode["stages"].items()],
                                      *[("tokens:" + token, value) for token, value in episode["tokens"].items()]]
                if value is None}),
        })
    return {"schema": "promise-to-proof/delivery-measurement-comparison/v1",
            "compatible_groups": rows,
            "unmatched_episode_ids": sorted(set(identities) -
                                            {row["episode_id"] for group in rows for row in group["episodes"]}),
            "limits": ["Only episodes with known repository, work item, contract revision/hash, and comparison base are grouped; incomplete identities remain unmatched.",
                       "Configuration differences are disclosed; durations and token counts are observations.",
                       "Unknown values remain unavailable; no cost, human effort, correctness, priority, or assurance is inferred.",
                       "Independent outcomes are included only from the separate independent_adjudications input."]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.input.read_text(),
                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite JSON number " + value)))
        print(json.dumps(compare(data), indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print("comparison input error: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
