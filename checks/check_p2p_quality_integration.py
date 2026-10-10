#!/usr/bin/env python3
"""Small live integration gate for #40; reuses #72 fixed-truth stage evaluations.

This is a TEST harness, not a new production stage. Requires macOS, an
authenticated Codex CLI, and installed audit-acceptance and delivery skills.
Offline transport/unit tests cannot establish live model judgment quality.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time

import check_p2p_judgments_host as judgments
from test_p2p_delivery import d


SELECTION = Path(__file__).resolve().parent / "fixtures/quality-integration/selection.json"
SCHEMA = "promise-to-proof/quality-integration/v1"


def selection():
    content = SELECTION.read_bytes()
    data = json.loads(content)
    fixtures, fixture_sha = judgments.load_manifest()
    ids = [case["id"] for case in fixtures["cases"]]
    chosen = data.get("cases")
    audits = data.get("audit")
    if (data.get("schema") != SCHEMA or not isinstance(chosen, list) or not chosen or
            len(set(chosen)) != len(chosen) or not set(chosen) <= set(ids) or
            not isinstance(audits, list) or len(audits) != 2 or
            {row.get("expected") for row in audits} != {"READY_FOR_APPROVAL", "BLOCKED"} or
            not isinstance(data.get("optional_advice"), str) or
            data.get("low_risk_case") not in chosen):
        raise ValueError("incomplete integrated quality fixture selection")
    for audit in audits:
        if (set(audit) != {"id", "expected", "spec_suffix"}
                or not all(isinstance(audit[k], str) for k in audit)):
            raise ValueError("malformed pre-implementation audit fixture")
    return data, fixtures, d.fs.digest(content), fixture_sha


def audit_schema():
    text = {"type": "string"}
    conflict = {"type": "object", "properties": {
        "first_source_excerpt": text, "second_source_excerpt": text,
        "consequence": text, "needed_decision": text,
    }, "required": ["first_source_excerpt", "second_source_excerpt",
                    "consequence", "needed_decision"], "additionalProperties": False}
    props = {"status": {"type": "string", "enum": [
        "READY_FOR_APPROVAL", "CHANGES_NEEDED", "BLOCKED"]},
        "input_identity_json": text, "coverage": text, "reason": text,
        "conflicts": {"type": "array", "items": conflict}}
    return {"type": "object", "properties": props, "required": list(props),
            "additionalProperties": False}


def assess_audit(report, expected, identity, source):
    issues = []
    if not isinstance(report, dict) or set(report) != set(audit_schema()["properties"]):
        return ["audit report has unsupported or missing fields"]
    if report["status"] != expected:
        issues.append(f"expected {expected}, observed {report['status']}")
    try:
        if json.loads(report["input_identity_json"]) != identity:
            issues.append("audit is not bound to exact source/proposal bytes")
    except (ValueError, TypeError):
        issues.append("audit returned invalid input identity")
    if any(not isinstance(report.get(field), str) or not report[field].strip()
           for field in ("coverage", "reason")):
        issues.append("audit did not explain source/contract coverage")
    conflicts = report.get("conflicts")
    if not isinstance(conflicts, list):
        issues.append("audit conflict observations are malformed")
        return issues
    if expected == "READY_FOR_APPROVAL" and conflicts:
        issues.append("sound control invented a material source contradiction")
    if expected == "BLOCKED" and not conflicts:
        issues.append("contradiction was not traced to conflicting source statements")
    for finding in conflicts:
        if not isinstance(finding, dict) or set(finding) != {
                "first_source_excerpt", "second_source_excerpt", "consequence", "needed_decision"}:
            issues.append("audit finding lacks source excerpts and next decision")
            continue
        for key in ("first_source_excerpt", "second_source_excerpt"):
            snippet = finding[key]
            if not isinstance(snippet, str) or len(snippet.strip()) < 12 or snippet not in source:
                issues.append("audit source excerpt is not backed by the original source: " + key)
        if (finding["first_source_excerpt"] == finding["second_source_excerpt"] or
                not all(isinstance(finding[key], str) and len(finding[key].strip()) >= 8
                        for key in ("consequence", "needed_decision"))):
            issues.append("audit did not explain a distinct material contradiction")
    return issues


def audit_one(output, fixture, data, executable, skill, max_stage_seconds, position):
    """Exercise the *existing* audit-acceptance skill before any delivery worker."""
    directory = output / f"audit-{position:02d}"
    directory.mkdir()
    case = {"spec_suffix": fixture["spec_suffix"]}
    root, base = judgments.source_repo(directory, data, case)
    item = root / judgments.WORK
    source = (root / "spec.md").read_text()
    identity = {"source_sha256": d.fs.digest(source.encode()),
                "contract_sha256": d.fs.digest(item.read_bytes()),
                "comparison_base": base, "proposal": judgments.WORK}
    before_tree = d.fs.snapshot(root)
    before_index = d.fs.git(root, "ls-files", "--stage", "-z")
    before_contract = item.read_bytes()
    scratch = directory / "scratch"
    scratch.mkdir()
    (scratch / ".p2p/tmp").mkdir(parents=True)
    schema = audit_schema()
    schema_path = directory / "schema.json"
    judgments.write_json(schema_path, schema)
    args = d.command(executable, scratch, schema_path)
    prompt = (
        f"Invoke the installed audit-acceptance skill at {skill['path']}. "
        "Read its references. This is an independent, read-only evaluation of "
        f"the *proposed, unapproved* acceptance contract {item} against its "
        f"source {root / 'spec.md'} in repository {root}. "
        "Compare every material source promise and counterexample with the "
        "proposed contract. Identify outcome-defining contradictions rather than "
        "silently choosing a convenient interpretation. Do not edit or approve "
        "the contract, implement the feature, start another actor, run proof, "
        "publish an effect, or write under the source repository. The evaluating "
        "controller will retain this report outside the candidate. "
        "Inspect source and proposal using local read-only commands. "
        "Return only the required JSON report; conflicts quote two exact distinct "
        "source excerpts and explain the material consequence and smallest "
        "decision required. For a sound contract, conflicts must be empty. "
        "READY_FOR_APPROVAL is advice, not an approval. "
        f"Exact input_identity_json must encode: {json.dumps(identity)}."
    )
    receipt = {"args": args, "input_identity": identity, "skill_sha256": skill["sha256"]}
    judgments.write_json(directory / "launch.json", receipt)
    events = directory / "events.jsonl"
    stderr = directory / "stderr.txt"
    response = d.launch(args, prompt, events, stderr, time.time() + max_stage_seconds)
    host = d.host_events(events)
    report = json.loads(host["message"])
    (directory / "report.json").write_bytes(host["message"].encode())
    (directory / "exit.json").write_bytes(d.encoded(response))
    issues = assess_audit(report, fixture["expected"], identity, source)
    if response["exit_code"] != 0 or response["outcome"] != "finished":
        issues.append("real audit host did not finish successfully")
    if not host["executions"]:
        issues.append("auditor returned no host-recorded source inspection")
    if (d.fs.snapshot(root) != before_tree or
            d.fs.git(root, "ls-files", "--stage", "-z") != before_index or
            item.read_bytes() != before_contract):
        issues.append("pre-implementation audit changed product, index or proposal")
    return {
        "id": fixture["id"], "expected": fixture["expected"],
        "observed": report.get("status"), "passed": not issues,
        "issues": issues, "source_sha256": identity["source_sha256"],
        "contract_sha256": identity["contract_sha256"],
        "skill_sha256": skill["sha256"],
        "session_id": host["session_id"],
        "event_sha256": d.fs.digest(events.read_bytes()),
        "report_sha256": d.fs.digest((directory / "report.json").read_bytes()),
        "receipt": str(directory / "exit.json"),
        "source": str(root / "spec.md"),
        "report": str(directory / "report.json"),
        "host_version": response.get("outcome"),
    }


def assess_case(result, case, contract):
    """Check cross-stage *identity and ownership*, not another model verdict."""
    problems = []
    if not result.get("passed"):
        problems.append("independently known judgment or private product oracle failed")
    if result.get("error"):
        problems.append("fixture execution: " + str(result["error"]))
    _, requirements = d.parse_contract(contract.encode())
    required = set(requirements)
    sessions = []
    identities = []
    for candidate in result.get("candidates", []):
        name = candidate["name"]
        saved = candidate.get("candidate")
        if not saved:
            problems.append(name + ": missing exact candidate identity")
            continue
        key = saved["key"]
        identities.append(key)
        if (candidate.get("generation", {}).get("candidate_key") != key or
                saved.get("comparison_base") != result.get("source_base")):
            problems.append(name + ": retained Git generation or frozen base differs")
        attempts = candidate.get("stage_attempts", [])
        if [attempt["stage"] for attempt in attempts] != ["review", "proof"]:
            problems.append(name + ": unexpected or missing independent verifier dispatch")
        if len(attempts) != 2 or any(not a.get("session_id") for a in attempts):
            problems.append(name + ": missing real host stage sessions")
        for attempt in attempts:
            sessions.append(attempt.get("session_id"))
            inputs = attempt.get("inputs", {})
            if (inputs.get("key") != key or
                    inputs.get("comparison_base") != saved.get("comparison_base") or
                    inputs.get("work_item_sha256") != result.get("contract_sha256")):
                problems.append(name + ": stage input differs from reviewed candidate or contract")
        for stage in ("review", "proof"):
            report = candidate.get("observed", {}).get(stage, {})
            try:
                values = json.loads(report["input_identity_json"])
                linked = next(a["inputs"] for a in attempts if a["stage"] == stage)
                if values != linked:
                    problems.append(name + ": " + stage + " judgment is bound to other inputs")
            except (KeyError, StopIteration, ValueError, TypeError):
                problems.append(name + ": missing exact " + stage + " report/input linkage")
            if {row["id"] for row in report.get("requirements", [])} != required:
                problems.append(name + ": " + stage + " omitted an accepted requirement")
            trace = report.get("coverage_trace", {})
            if {r["id"] for r in trace.get("requirements", [])} != required:
                problems.append(name + ": " + stage + " omitted implementation/evidence links")
        scope = candidate.get("review_scope")
        review = candidate.get("observed", {}).get("review", {})
        if not isinstance(scope, dict):
            problems.append(name + ": missing exact reviewed product scope")
        else:
            if (scope.get("candidate_key") != key or
                    scope.get("comparison_base") != saved.get("comparison_base") or
                    scope.get("contract_sha256") != result.get("contract_sha256") or
                    scope.get("changed_paths") != saved.get("changes")):
                problems.append(name + ": reviewed scope is not this candidate")
            if scope.get("trace_sha256") != d.fs.digest(d.fs.canonical(
                    review.get("coverage_trace"))):
                problems.append(name + ": review scope does not bind its risk/evidence trace")
        if case["id"] == "review-meaningful-tests":
            if review.get("coverage_trace", {}).get("risks") != []:
                problems.append(name + ": low-risk change acquired unnecessary material risk work")
        if not candidate.get("oracle", {}).get("passed"):
            problems.append(name + ": public-interface oracle did not confirm fixture truth")
        if not candidate.get("guard_sensitivity", {}).get("passed"):
            problems.append(name + ": existing regression guards disagree with fixture sensitivity")
    if not result.get("candidates"):
        problems.append("no candidate independently reviewed and proven")
    if len(sessions) != len(set(sessions)):
        problems.append("independent stages reused a host session")
    if len(identities) > 1 and len(identities) != len(set(identities)):
        problems.append("changed-candidate re-verification did not bind new product bytes")
    if case["id"] == "review-reconcile-corrected-finding":
        candidates = result.get("candidates", [])
        if (len(candidates) != 2 or
                [c.get("observed", {}).get("review", {}).get("status") for c in candidates] !=
                ["CHANGES NEEDED", "REVIEWED"] or
                [c.get("observed", {}).get("proof", {}).get("status") for c in candidates] !=
                ["NOT PROVEN", "PROVEN"] or
                not all(candidate.get("previous_same_stage_history", {}).get(stage, {}).get("available")
                        for candidate in candidates[1:] for stage in ("review", "proof"))):
            problems.append("localized repair did not reconcile both verifier judgments on exact new bytes")
    return problems


def compact_case(result, case, problems):
    return {
        "fixture": case["id"],
        "passed": not problems,
        "issues": problems,
        "source_base": result.get("source_base"),
        "contract_sha256": result.get("contract_sha256"),
        "instruction_identity": result.get("instruction_identity"),
        "host": result.get("host", {}).get("version"),
        "candidates": [{
            "name": c["name"],
            "candidate_key": c.get("candidate", {}).get("key"),
            "expected": {k: c.get("expected", {}).get(k) for k in ("review", "proof")},
            "observed": {stage: c.get("observed", {}).get(stage, {}).get("status")
                         for stage in ("review", "proof")},
            "stage_sessions": {a["stage"]: a.get("session_id")
                               for a in c.get("stage_attempts", [])},
            "scope_sha256": (d.fs.digest(d.fs.canonical(c["review_scope"]))
                             if c.get("review_scope") else None),
        } for c in result.get("candidates", [])],
    }


def integrate(output, manifest, audits, cases, *, live_evidence, host_version=None):
    """One compact report referencing the #72 evidence directories, not copying them."""
    selected = manifest["cases"]
    errors = [f"audit {a['id']}: " + "; ".join(a["issues"]) for a in audits if not a["passed"]]
    errors += [f"fixture {c['fixture']}: " + "; ".join(c["issues"])
               for c in cases if not c["passed"]]
    observed = {row["fixture"] for row in cases}
    if set(selected) != observed or len(cases) != len(selected):
        errors.append("the integrated fixture set was not completely exercised")
    if {item["id"] for item in audits} != {item["id"] for item in manifest["audit"]}:
        errors.append("clear and ambiguous pre-implementation agreements were not both audited")
    report = {
        "schema": SCHEMA, "status": ("UNAVAILABLE" if not live_evidence and not audits and not cases
                                   else "PASS" if not errors and live_evidence else "FAIL"),
        "live_host_evidence": live_evidence, "host_version": host_version,
        "selection_sha256": d.fs.digest(SELECTION.read_bytes()),
        "fixture_manifest_sha256": judgments.load_manifest()[1],
        "contract_audits": audits, "candidate_checks": cases,
        "errors": errors, "not_claimed": [
            "No new ordinary P2P stage or quality gate",
            "No universal prevention of regressions or guaranteed model behavior",
            "No automatic reuse or performance improvement measured by this suite",
            "The fixed-candidate live runner does not exercise autonomous implementation",
        ],
        "evidence_directory": str(output),
    }
    judgments.write_json(output / "quality-integration.json", report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path,
                        help="new persistent directory for exact receipts and compact integration report")
    parser.add_argument("--max-stage-seconds", type=int, default=180,
                        help="real host deadline for each audit/review/proof call")
    args = parser.parse_args(argv)
    if args.max_stage_seconds < 1:
        parser.error("--max-stage-seconds must be positive")
    output = args.output_dir.expanduser().resolve()
    if output.exists():
        parser.error("output directory must be new; do not overwrite saved evidence")
    output.mkdir(parents=True)
    audits, cases = [], []
    host_version = None
    try:
        manifest, fixtures, identity, fixture_sha = selection()
        if platform.system() != "Darwin":
            raise ValueError("real integration evidence requires macOS, authenticated Codex CLI and installed skills")
        executable = shutil.which("codex")
        if not executable:
            raise ValueError("Codex CLI is not installed; no fake-host fallback")
        version = subprocess.run([executable, "--version"], check=True, capture_output=True,
                                 text=True, timeout=10)
        host_version = version.stdout.strip()
        skill = d.installed_skill("audit-acceptance")
        os.environ["P2P_EXECUTION_ROOT"] = str(output / "executions")
        (output / "executions").mkdir()
        for position, fixture in enumerate(manifest["audit"], 1):
            audits.append(audit_one(output, fixture, fixtures, executable,
                                    skill, args.max_stage_seconds, position))
            # Contradictory sources never enter implementation; neither does
            # the unapproved good audit fixture, which is only an audit control.
        for position, name in enumerate(manifest["cases"], 1):
            original = next(c for c in fixtures["cases"] if c["id"] == name)
            case = dict(original)
            if name == manifest["low_risk_case"]:
                case["spec_suffix"] = case.get("spec_suffix", "") + manifest["optional_advice"]
            result = judgments.run_case(output, fixtures, case, fixture_sha,
                                        args.max_stage_seconds, position)
            issues = assess_case(result, case, case.get("contract", fixtures["contract"]))
            cases.append(compact_case(result, case, issues))
        report = integrate(output, manifest, audits, cases, live_evidence=True,
                           host_version=host_version)
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        data = json.loads(SELECTION.read_bytes()) if SELECTION.is_file() else {"audit": [], "cases": []}
        report = integrate(output, data, audits, cases, live_evidence=False,
                           host_version=host_version)
        report["status"] = "UNAVAILABLE" if not audits and not cases else "FAIL"
        report["errors"].append(str(error))
        judgments.write_json(output / "quality-integration.json", report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
