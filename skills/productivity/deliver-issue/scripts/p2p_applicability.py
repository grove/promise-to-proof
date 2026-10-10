"""Conservative, read-only reuse decisions from already validated P2P stage facts.

This module never transfers a review/proof verdict, verifies a model observation,
or authorizes an effect. The owning verifier receives a proposed *check plan* for
a fresh complete-contract judgment bound to the current exact candidate.
"""
import hashlib
import json
from pathlib import PurePosixPath


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def _risk_sensitive_path(path):
    parts = PurePosixPath(path).parts
    name = parts[-1].lower()
    return (any(part in ("test", "tests", "fixtures", "specs", "migrations", ".github")
                for part in parts) or
            name.startswith(("test_", "conftest", "pytest", "pyproject", "setup.cfg")) or
            name in ("package.json", "package-lock.json", "requirements.txt",
                     "tox.ini", "pytest.ini", "mypy.ini", "tsconfig.json",
                     "dockerfile", "makefile", ".env", "cargo.toml", "cargo.lock"))


def classify(report, changes, requirements, stage, *, prior_candidate, report_sha256):
    """Determine potentially reusable *observations*, not reusable verdicts.

    Called only after the controller authenticates the previous host receipt,
    report hash, source candidate Git generation and current generation, and
    checks contract/skill/host inputs. Unlisted dependencies and unclear reach
    require fresh full-scope checks. Even SELECTIVE means the new independent
    stage issues a *new, complete* review/proof result.
    """
    expected = sorted(requirements)
    changed_paths = sorted({row["path"] for row in changes})
    result = {"status": "FULL_RECHECK", "stage": stage,
              "previous_candidate": prior_candidate,
              "previous_report_sha256": report_sha256,
              "changed_paths": changed_paths,
              "potentially_reusable": [], "refresh_requirements": expected,
              "reason": None, "new_full_verdict_required": True}

    def full(reason):
        return result | {"reason": reason}

    if stage not in ("review", "proof") or not isinstance(report, dict):
        return full("No supported, checked independent-stage report.")
    rows = report.get("requirements")
    trace = report.get("coverage_trace")
    if (not isinstance(rows, list) or not isinstance(trace, dict) or
            not isinstance(trace.get("requirements"), list) or
            not isinstance(trace.get("risks"), list) or
            not isinstance(trace.get("supporting_changes"), list)):
        return full("Prior report lacks complete requirement/seam traceability.")
    try:
        indexed = {row["id"]: row for row in rows}
        mapped = {row["id"]: row for row in trace["requirements"]}
        if (len(indexed) != len(rows) or len(mapped) != len(trace["requirements"])
                or sorted(indexed) != expected or sorted(mapped) != expected):
            return full("Prior requirement IDs differ from the current complete agreement.")

        if not changed_paths:
            return result | {"status": "UNCHANGED", "reason":
                             "Identical product bytes; retain exact reports only when their complete stage inputs also match.",
                             "potentially_reusable": [], "refresh_requirements": []}
        affected = set()
        known_paths = set()
        unknown = set()
        for name, item in mapped.items():
            paths = item["paths"]
            if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
                return full("Prior implementation paths are malformed.")
            known_paths.update(paths)
            if not paths:
                unknown.add(name)
            if set(paths) & set(changed_paths):
                affected.add(name)

        supporting = {item["path"] for item in trace["supporting_changes"]}
        known_paths.update(supporting)
        for risk in trace["risks"]:
            linked = risk["requirements"]
            risk_paths = risk["paths"]
            known_paths.update(risk_paths)
            if risk["reach"] == "uncertain":
                return full("A saved material seam has uncertain behavioral reach.")
            if risk["status"] != "addressed":
                affected.update(linked)
            if set(risk_paths) & set(changed_paths):
                affected.update(linked)
        if set(changed_paths) - known_paths:
            return full("Changed product paths are not covered by saved implementation/seam dependencies.")
        if set(changed_paths) & supporting:
            return full("A shared supporting change has unknown downstream applicability.")
        if any(_risk_sensitive_path(path) for path in changed_paths):
            return full("A test, oracle, migration or binding configuration changed; refresh dependent checks.")
        if unknown:
            return full("Prior unchanged behavior lacks explicit dependency paths.")

        for finding in (report.get("findings") or []):
            source = finding.get("source")
            if source not in indexed:
                return full("Earlier material finding has unresolved cross-requirement reach.")
            affected.add(source)
        for name, row in indexed.items():
            if (not isinstance(row.get("observation"), str) or not row["observation"].strip()
                    or (stage == "proof" and
                        (row.get("verdict") != "proven" or not row.get("evidence")))):
                affected.add(name)

        reusable = []
        for name in expected:
            if name in affected:
                continue
            # This fingerprint identifies an exact original observation; it is
            # never relabeled as an observation made on the new candidate.
            reusable.append({"id": name, "observation_sha256": digest(indexed[name]),
                             "from_candidate": prior_candidate})
        if not reusable:
            return full("All requirements depend on changed or unresolved evidence.")
        if not affected:
            # A changed candidate still requires a fresh whole-contract verdict.
            return result | {"status": "SELECTIVE", "potentially_reusable": reusable,
                             "refresh_requirements": [],
                             "reason": "Dependencies are explicitly disjoint; independently confirm assumptions and final-candidate checks."}
        return result | {"status": "SELECTIVE", "potentially_reusable": reusable,
                         "refresh_requirements": sorted(affected),
                         "reason": "Recheck affected seams and independently verify each retained observation's applicability."}
    except (KeyError, TypeError, ValueError):
        return full("Prior trace has incomplete or malformed dependencies.")


def next_work(state):
    """Explain only retained stage inputs and the next existing work item."""
    fresh_host = bool(state.get("checkpoint_restored_from"))
    first = (("receiving-host preflight" if fresh_host else "host preflight")
             if not state.get("preflight_complete") else None)
    pending = [a for a in state.get("attempts", []) if a.get("status") in ("reserved", "failed")]
    if pending:
        first = "reconcile uncertain " + pending[-1].get("stage", "worker")
    reports = state.get("reports", {})
    candidate = state.get("candidate")
    current_generation = (state.get("local_git_generations") or [None])[-1]
    facts = {}
    for stage in ("implementation", "review", "proof"):
        row = reports.get(stage)
        if stage == "implementation" and state.get("implementation_complete"):
            source = (current_generation or {}).get("source_attempt") or {}
            writer = reports.get("repair" if source.get("attempt_id") ==
                                 reports.get("repair", {}).get("attempt_id") else "implementation")
            if (writer and writer.get("attempt_id") == source.get("attempt_id") and
                    writer.get("sha256") == source.get("report_sha256")):
                facts[stage] = "REUSED"
                continue
        if not row:
            facts[stage] = "MISSING"
        elif not candidate or not current_generation:
            facts[stage] = "STALE"
        elif row.get("inputs", {}).get("key") != candidate.get("key"):
            facts[stage] = "STALE"
        elif row.get("inputs", {}).get("instruction_identity") != state.get("instruction_identity"):
            facts[stage] = "STALE"
        elif row.get("inputs", {}).get("local_git_generation") != {
                k: current_generation[k] for k in
                ("sequence", "candidate_key", "tree", "commit", "record_sha256")}:
            facts[stage] = "STALE"
        else:
            facts[stage] = "REUSED"
    if not first and state.get("status") in ("BLOCKED", "HANDOFF"):
        first = "resolve recorded blocker or authorized handoff"
    elif not first and state.get("status") == "REVIEWED_AND_PROVEN" and all(
            facts[s] == "REUSED" for s in ("review", "proof")):
        first = "none — current local completion already established"
    elif not first:
        first = next((name for name in ("implementation", "review", "proof")
                      if facts[name] != "REUSED"), "check saved completion")
    return {"stages": facts, "next": first,
            "preflight": "READY" if state.get("preflight_complete") else "MISSING",
            "basis": "Existing exact candidate, stage input and host facts; no verdict transferred."}
