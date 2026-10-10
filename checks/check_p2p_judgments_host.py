#!/usr/bin/env python3
"""Live fixed-candidate judgments, independently scored; not a mock or a benchmark.

Requires the supported macOS + authenticated Codex CLI host and installed skills.
Each fixture runs the *real* deliver-issue review/proof stage and retains host
receipts. Expected judgments and oracle outputs never enter the worker workspace.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from types import SimpleNamespace

# Reuse the same production controller, host transport, stage schema and #59 metrics.
from test_p2p_delivery import d


MANIFEST = Path(__file__).resolve().parent / "fixtures/live-judgments/manifest.json"
WORK = ".p2p/work/live-judgment/contract.md"
SCHEMA = "promise-to-proof/live-judgments/v1"


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def load_manifest(path=MANIFEST):
    raw = path.read_bytes()
    data = json.loads(raw)
    if data.get("schema") != SCHEMA or not data.get("cases"):
        raise ValueError("invalid live-judgments manifest")
    ids = [case["id"] for case in data["cases"]]
    if len(set(ids)) != len(ids) or any(not case.get("candidates") for case in data["cases"]):
        raise ValueError("duplicate or missing fixture candidates")
    return data, d.fs.digest(raw)


def product_file(root, name, content):
    if (not isinstance(name, str) or not d.fs.product_path(name) or
            name.split("/", 1)[0] in (".git", "p2p-state") or
            not isinstance(content, str)):
        raise ValueError("invalid fixture product path/content: " + repr(name))
    target = d.fs.safe(root, name, leaf_symlink=True)
    if target.is_symlink() or (target.exists() and not target.is_file()):
        raise ValueError("unexpected fixture path: " + name)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)


def source_repo(case_dir, data, case):
    root = case_dir / "source"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    d.fs.git(root, "config", "user.name", "P2P Live Fixture")
    d.fs.git(root, "config", "user.email", "fixture@localhost")
    for path, content in data["base_files"].items():
        if path == "spec.md":
            content += case.get("spec_suffix", "")
        product_file(root, path, content)
    d.fs.git(root, "add", ".")
    d.fs.git(root, "commit", "-qm", "Fixed live behavioral source")
    base = d.fs.full_commit(root, "HEAD")
    d.fs.git(root, "branch", "delivery-target", base)
    agreement = root / WORK
    agreement.parent.mkdir(parents=True)
    agreement.write_text(data["contract"])
    return root, base


def admit(root, base, count, stage_seconds):
    # This is a verification-only fixture, never a normal delivery success/merge.
    args = SimpleNamespace(
        work=WORK, comparison_base=base, destination="delivery-target",
        authorize_local=True, hard_cost_cap=None, mandate=None, exclude_dirty=[],
        max_dispatches=2 * count, max_seconds=None, max_stage_seconds=stage_seconds,
        max_repairs=0, worker_idle_seconds=None,
    )
    return d.create(root, args, live_evaluation=True)


def candidate_files(data, candidate):
    files = dict(data["implementations"][candidate["implementation"]])
    files.update(candidate.get("changes", {}))
    return files


def capture_fixed_candidate(delivery, files):
    for path, content in files.items():
        product_file(delivery.workspace, path, content)
    # Each fixed fixture version becomes a separately hash-bound local Git
    # generation. A normal delivery cannot admit this non-worker stage.
    candidate = delivery.capture("live-evaluation")
    delivery.state["reports"] = {}
    delivery.save()
    delivery.current()
    return candidate


def observed_defect(report, expected):
    wanted = expected.get("review_finding")
    if not wanted:
        return True
    for finding in report.get("findings", []):
        if wanted.get("axis") and finding.get("axis") != wanted["axis"]:
            continue
        if wanted.get("source") and finding.get("source") != wanted["source"]:
            continue
        # Material scope location/behavior, not arbitrary finding prose.
        path = wanted.get("path")
        if path and path not in " ".join(str(finding.get(k, "")) for k in
                                       ("location", "evidence", "consequence")):
            continue
        return True
    return False


def judgment_mismatches(review, proof, expected):
    errors = []
    for stage, report in (("review", review), ("proof", proof)):
        if report.get("status") != expected[stage]:
            errors.append(f"{stage}: expected {expected[stage]}, observed {report.get('status')}")
    if not observed_defect(review, expected):
        errors.append("review did not identify the independently specified material defect")
    rows = {r["id"]: r for r in proof.get("requirements", [])}
    for requirement in expected.get("missing_proof", []):
        if requirement not in rows or rows[requirement].get("verdict") == "proven":
            errors.append(f"proof falsely accepted missing obligation {requirement}")
    if expected["proof"] == "PROVEN" and any(row.get("verdict") != "proven" for row in rows.values()):
        errors.append("PROVEN result contains an unproven requirement")
    return errors


def observable_checks(delivery, candidate, case_dir):
    """Run a private, deterministic CLI oracle *after* both model stages.

    Expectations are independently authored in the harness manifest. Neither the
    oracle answers nor the observed results are passed to review/proof workers.
    """
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    outcomes = []
    for probe in candidate["oracle"]:
        cmd = [sys.executable, "-B", *probe["args"]]
        try:
            result = subprocess.run(cmd, cwd=delivery.workspace, env=env,
                                    capture_output=True, text=True, timeout=15)
            actual = {"exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
        except subprocess.TimeoutExpired as error:
            actual = {"timeout": str(error)}
        expected = {key: probe[key] for key in ("exit", "stdout", "stderr")}
        outcomes.append({"id": probe["id"], "command": cmd, "expected": expected,
                         "observed": actual, "match": actual == expected})
    suite = subprocess.run(
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        cwd=delivery.workspace, env=env, capture_output=True, text=True, timeout=30,
    )
    result = {"probes": outcomes,
              "supplied_tests": {"command": "python3 -B -m unittest discover -s tests -p test_*.py",
                                 "exit": suite.returncode, "stdout": suite.stdout, "stderr": suite.stderr},
              "passed": all(item["match"] for item in outcomes) and suite.returncode == 0}
    write_json(case_dir / "oracle.json", result)
    return result


def run_case(output, data, case, fixture_sha, stage_seconds):
    case_dir = output / case["id"]
    case_dir.mkdir()
    summary = {"fixture": case["id"], "rationale": case["rationale"],
               "manifest_sha256": fixture_sha, "kind": "live-host (Codex CLI; no fixture transport)",
               "candidates": [], "passed": False}
    delivery = None
    try:
        root, base = source_repo(case_dir, data, case)
        delivery = admit(root, base, len(case["candidates"]), stage_seconds)
        summary.update(invocation_id=delivery.state["invocation_id"],
                       source_base=base, contract_sha256=delivery.state["contract"]["sha256"],
                       instruction_identity=delivery.state["instruction_identity"],
                       installed_skills=delivery.state["skills"], host=delivery.state["host"],
                       runtime=str(delivery.runtime))
        former_key = None
        for index, spec in enumerate(case["candidates"]):
            entry = {"name": spec["name"], "expected": spec["expected"], "passed": False}
            summary["candidates"].append(entry)
            write_json(case_dir / "summary.json", summary)
            before_attempts = len(delivery.state["attempts"])
            captured = capture_fixed_candidate(delivery, candidate_files(data, spec))
            entry["candidate"] = d.identity(captured)
            entry["generation"] = delivery.state["local_git_generations"][-1]
            history = {stage: delivery.verification_history(stage) for stage in ("review", "proof")}
            entry["previous_same_stage_history"] = history
            errors = []
            if index:
                if captured["key"] == former_key:
                    errors.append("follow-up did not change the candidate key")
                if spec.get("requires_previous_observations") and not all(
                        item and item.get("available") for item in history.values()):
                    errors.append("follow-up did not offer independently retrievable same-stage history")
            elif any(history.values()):
                errors.append("first candidate unexpectedly has prior verifier history")
            former_key = captured["key"]
            # Independent real stage contexts, regardless of the other's verdict.
            review = delivery.stage("review")
            proof = delivery.stage("proof")
            # These readbacks validate the genuine host message, saved report and
            # exact candidate/contract/skill identities through production checks.
            review = delivery.read_report("review")
            proof = delivery.read_report("proof")
            entry["observed"] = {"review": review, "proof": proof}
            entry["stage_attempts"] = [{
                "stage": a["stage"], "attempt_id": a["id"], "session_id": a.get("session_id"),
                "inputs": a["inputs"], "report": a.get("report"),
                "receipt": str(delivery.runtime / "attempts" / a["id"] / "exit.json"),
                "events": str(delivery.runtime / "attempts" / a["id"] / "events.jsonl"),
            } for a in delivery.state["attempts"][before_attempts:]]
            errors.extend(judgment_mismatches(review, proof, spec["expected"]))
            if d.identity(delivery.current()) != d.identity(captured):
                errors.append("verifier mutated fixed candidate")
            if any(a["stage"] in ("implementation", "repair") for a in
                   delivery.state["attempts"][before_attempts:]):
                errors.append("evaluation unexpectedly ran implementation or repair")
            oracle = observable_checks(delivery, spec, case_dir / spec["name"])
            entry["oracle"] = oracle
            if not oracle["passed"]:
                errors.append("independent CLI observations or supplied green tests disagreed")
            if d.identity(delivery.current()) != d.identity(captured):
                errors.append("oracle probes mutated the fixed candidate")
            entry.update(passed=not errors, mismatches=errors)
            write_json(case_dir / "summary.json", summary)
        summary["passed"] = all(item["passed"] for item in summary["candidates"])
        summary["measurement"] = d.result(delivery)["measurement"]  # Existing #59 accounting.
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as error:
        summary["error"] = f"{type(error).__name__}: {error}"
        if delivery:
            summary["runtime"] = str(delivery.runtime)
            summary["measurement"] = d.result(delivery)["measurement"]
        summary["passed"] = False
    write_json(case_dir / "summary.json", summary)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path,
                        help="new, durable evidence directory (never overwrites old runs)")
    parser.add_argument("--only", action="append", help="run named fixture(s); default is the whole gate")
    parser.add_argument("--max-stage-seconds", type=int, default=240,
                        help="finite per-verifier host budget; default 240 seconds")
    args = parser.parse_args(argv)
    if args.max_stage_seconds < 1:
        parser.error("--max-stage-seconds must be positive")
    output = args.output_dir.expanduser().resolve()
    if output.exists():
        parser.error("output directory must be new; retained evidence is never overwritten")
    output.mkdir(parents=True)
    started = time.monotonic()
    summary = {"kind": "live judgment evaluation", "live_evidence": False,
               "passed": False, "cases": [], "elapsed_seconds": None,
               "invocation_command": [sys.executable, str(Path(__file__).resolve()),
                                      *(sys.argv[1:] if argv is None else argv)]}
    try:
        data, identity = load_manifest()
        all_ids = {case["id"] for case in data["cases"]}
        if args.only and not set(args.only) <= all_ids:
            raise ValueError("unknown fixture(s): " + ", ".join(sorted(set(args.only) - all_ids)))
        summary["fixture_manifest_sha256"] = identity
        selected = [case for case in data["cases"] if not args.only or case["id"] in args.only]
        summary["selected"] = [case["id"] for case in selected]
        if platform.system() != "Darwin":
            raise ValueError("unsupported live host: macOS and authenticated Codex CLI required; no mock fallback")
        execution = output / "executions"
        execution.mkdir()
        os.environ["P2P_EXECUTION_ROOT"] = str(execution)
        for case in selected:
            result = run_case(output, data, case, identity, args.max_stage_seconds)
            summary["cases"].append({"fixture": case["id"], "passed": result["passed"],
                                     "summary": str(output / case["id"] / "summary.json")})
            write_json(output / "summary.json", summary)
        summary["passed"] = all(item["passed"] for item in summary["cases"])
        # A platform check or attempted admission alone is not live evidence.
        # Both independent stages must have real, read-back host receipts.
        receipts = []
        for case in selected:
            case_result = json.loads((output / case["id"] / "summary.json").read_text())
            for candidate in case_result["candidates"]:
                attempts = candidate.get("stage_attempts", [])
                verified = {a["stage"] for a in attempts if a.get("session_id") and
                            Path(a["receipt"]).is_file() and Path(a["events"]).is_file()}
                receipts.append(verified == {"review", "proof"})
        summary["live_evidence"] = bool(receipts) and all(receipts)
    except (ValueError, OSError, KeyError, TypeError) as error:
        summary["error"] = str(error)
    summary["elapsed_seconds"] = round(time.monotonic() - started, 3)
    write_json(output / "summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0 if summary["passed"] and summary["live_evidence"] else 1


if __name__ == "__main__":
    sys.exit(main())
