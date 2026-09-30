#!/usr/bin/env python3
"""Validate and render Promise to Proof Evidence Record v1 objects."""

import argparse
import hashlib
import json
import re
from datetime import datetime


SCHEMA = "promise-to-proof/evidence-record/v1"
ID_PREFIX = "evidence:sha256:"
HEX_64 = re.compile(r"[0-9a-f]{64}\Z")
REQUIREMENT_ID = re.compile(r"R[1-9][0-9]*\Z")
CONTRACT_REVISION = re.compile(r"v[1-9][0-9]*\Z")
CANDIDATE_KEY = re.compile(
    r"(?:snapshot:sha256:[0-9a-f]{64}|git:(?:[0-9a-f]{40}|[0-9a-f]{64}))\Z"
)
RESULTS = {"passed", "failed", "inconclusive"}
EVIDENCE_TYPES = {
    "test", "command", "http", "browser", "static-analysis",
    "invariant", "ci", "manual", "external", "other",
}
EXECUTION_TYPES = {"test", "command", "static-analysis", "invariant", "ci"}
REFERENCE_TYPES = {"manual", "external"}


def _add(issues, code, path, message):
    issues.append({"code": code, "path": path, "message": message})


def _keys(value, required, path, issues):
    if not isinstance(value, dict):
        _add(issues, "INVALID_TYPE", path, "must be an object")
        return False
    for key in sorted(set(required) - set(value)):
        _add(issues, "MISSING_FIELD", f"{path}.{key}", "required field is missing")
    for key in sorted(set(value) - set(required)):
        _add(issues, "UNKNOWN_FIELD", f"{path}.{key}", "field is not defined by v1")
    return True


def _string(parent, key, path, issues, allow_empty=False):
    if not isinstance(parent, dict) or key not in parent:
        _add(issues, "MISSING_FIELD", path, "required string is missing")
        return None
    value = parent[key]
    if not isinstance(value, str):
        _add(issues, "INVALID_TYPE", path, "must be a string")
        return None
    if not allow_empty and not value:
        _add(issues, "EMPTY_VALUE", path, "must not be empty")
        return None
    return value


def _canonical_body(record):
    body = dict(record)
    body.pop("id", None)
    return json.dumps(
        body, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def evidence_id(record):
    return ID_PREFIX + hashlib.sha256(_canonical_body(record)).hexdigest()


def _timestamp(value, path, issues):
    if not isinstance(value, str) or not value:
        _add(issues, "INVALID_TIMESTAMP", path, "must be a nonempty RFC 3339 timestamp")
        return
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _add(issues, "INVALID_TIMESTAMP", path, "must be an RFC 3339 timestamp")
        return
    if parsed.tzinfo is None:
        _add(issues, "INVALID_TIMESTAMP", path, "must include a timezone")


def _digest(value, path, issues):
    if not isinstance(value, str) or HEX_64.fullmatch(value) is None:
        _add(issues, "INVALID_DIGEST", path, "must be 64 lowercase hexadecimal characters")


def _validate_contract(contract, path, issues):
    if not _keys(contract, {"source", "revision", "sha256"}, path, issues):
        return (None, None, None)
    source = _string(contract, "source", f"{path}.source", issues)
    revision = _string(contract, "revision", f"{path}.revision", issues)
    digest = _string(contract, "sha256", f"{path}.sha256", issues)
    if revision is not None and CONTRACT_REVISION.fullmatch(revision) is None:
        _add(issues, "INVALID_CONTRACT_REVISION", f"{path}.revision", "must match v[1-9][0-9]*")
    if digest is not None:
        _digest(digest, f"{path}.sha256", issues)
    return (source, revision, digest)


def _validate_requirements(values, issues):
    if not isinstance(values, list) or not values:
        _add(issues, "INVALID_REQUIREMENTS", "requirements", "must be a nonempty array")
        return []
    seen = []
    for index, value in enumerate(values):
        path = f"requirements[{index}]"
        if not isinstance(value, str) or REQUIREMENT_ID.fullmatch(value) is None:
            _add(issues, "INVALID_REQUIREMENT_ID", path, "must match R[1-9][0-9]*")
            continue
        if value in seen:
            _add(issues, "DUPLICATE_REQUIREMENT", path, f"{value} appears more than once")
        seen.append(value)
    if seen and seen != sorted(seen, key=lambda item: int(item[1:])):
        _add(issues, "NONCANONICAL_REQUIREMENT_ORDER", "requirements", "must be in ascending numeric requirement-ID order")
    return seen


def _validate_environment(value, issues):
    path = "environment"
    if not _keys(value, {"id", "description"}, path, issues):
        return None
    environment_id = _string(value, "id", f"{path}.id", issues)
    _string(value, "description", f"{path}.description", issues)
    return environment_id


def _validate_artifact(value, issues):
    if value is None:
        return
    path = "artifact"
    if not _keys(value, {"name", "sha256", "locator"}, path, issues):
        return
    _string(value, "name", f"{path}.name", issues)
    digest = _string(value, "sha256", f"{path}.sha256", issues)
    _string(value, "locator", f"{path}.locator", issues)
    if digest is not None:
        _digest(digest, f"{path}.sha256", issues)


def _validate_reference(value, issues):
    if value is None:
        return
    path = "reference"
    if not _keys(value, {"kind", "locator", "sha256"}, path, issues):
        return
    _string(value, "kind", f"{path}.kind", issues)
    _string(value, "locator", f"{path}.locator", issues)
    digest = value.get("sha256")
    if digest is not None:
        _digest(digest, f"{path}.sha256", issues)


def _validate_execution(value, candidate_key, environment_id, result, issues):
    if value is None:
        return
    path = "execution"
    required = {
        "receipt_id", "candidate_key", "environment_id", "tool", "command",
        "exit_status", "expected_exit_status", "output_sha256", "started_at", "finished_at",
    }
    if not _keys(value, required, path, issues):
        return
    _string(value, "receipt_id", f"{path}.receipt_id", issues)
    observed_candidate = _string(value, "candidate_key", f"{path}.candidate_key", issues)
    observed_environment = _string(value, "environment_id", f"{path}.environment_id", issues)
    _string(value, "tool", f"{path}.tool", issues)
    _string(value, "command", f"{path}.command", issues)
    exit_status = value.get("exit_status")
    expected_exit_status = value.get("expected_exit_status")
    if not isinstance(exit_status, int) or isinstance(exit_status, bool):
        _add(issues, "INVALID_EXIT_STATUS", f"{path}.exit_status", "must be an integer")
    if not isinstance(expected_exit_status, int) or isinstance(expected_exit_status, bool):
        _add(issues, "INVALID_EXIT_STATUS", f"{path}.expected_exit_status", "must be an integer")
    if isinstance(exit_status, int) and isinstance(expected_exit_status, int):
        if result == "passed" and exit_status != expected_exit_status:
            _add(issues, "EXECUTION_RESULT_CONFLICT", path, "passed result conflicts with exit status")
        if result == "failed" and exit_status == expected_exit_status:
            _add(issues, "EXECUTION_RESULT_CONFLICT", path, "failed result conflicts with expected exit status")
    output_digest = _string(value, "output_sha256", f"{path}.output_sha256", issues)
    if output_digest is not None:
        _digest(output_digest, f"{path}.output_sha256", issues)
    _timestamp(value.get("started_at"), f"{path}.started_at", issues)
    _timestamp(value.get("finished_at"), f"{path}.finished_at", issues)
    if observed_candidate is not None and observed_candidate != candidate_key:
        _add(issues, "EXECUTION_CANDIDATE_MISMATCH", f"{path}.candidate_key", "must match candidate_key")
    if observed_environment is not None and observed_environment != environment_id:
        _add(issues, "EXECUTION_ENVIRONMENT_MISMATCH", f"{path}.environment_id", "must match environment.id")


def _validate_context(record, context, issues):
    if context is None:
        return
    if not _keys(context, {"contract", "candidate_key", "requirement_ids"}, "context", issues):
        return
    expected_contract = _validate_contract(context.get("contract"), "context.contract", issues)
    expected_candidate = _string(context, "candidate_key", "context.candidate_key", issues)
    known = context.get("requirement_ids")
    if not isinstance(known, list):
        _add(issues, "INVALID_TYPE", "context.requirement_ids", "must be an array")
        known = []
    record_contract = record.get("contract") if isinstance(record.get("contract"), dict) else {}
    if tuple(record_contract.get(k) for k in ("source", "revision", "sha256")) != expected_contract:
        _add(issues, "CONTRACT_IDENTITY_MISMATCH", "contract", "does not match proof context")
    if expected_candidate is not None and record.get("candidate_key") != expected_candidate:
        _add(issues, "CANDIDATE_IDENTITY_MISMATCH", "candidate_key", "does not match proof context")
    for requirement in record.get("requirements", []):
        if requirement not in known:
            _add(issues, "UNKNOWN_REQUIREMENT", "requirements", f"{requirement} is not in proof context")


def verify_record(record, context=None):
    issues = []
    if not isinstance(record, dict):
        return [{"code": "INVALID_TYPE", "path": "$", "message": "record must be an object"}]
    required = {
        "schema", "id", "contract", "candidate_key", "requirements", "type",
        "assertion", "observation", "oracle", "result", "environment",
        "observed_at", "execution", "reference", "artifact", "limitations",
    }
    _keys(record, required, "$", issues)
    schema = _string(record, "schema", "schema", issues)
    record_id = _string(record, "id", "id", issues)
    if schema is not None and schema != SCHEMA:
        _add(issues, "UNSUPPORTED_SCHEMA", "schema", f"must be {SCHEMA}")
    if record_id is not None:
        if not record_id.startswith(ID_PREFIX) or HEX_64.fullmatch(record_id[len(ID_PREFIX):]) is None:
            _add(issues, "INVALID_EVIDENCE_ID", "id", f"must be {ID_PREFIX}<64 lowercase hex>")
        elif record_id != evidence_id(record):
            _add(issues, "EVIDENCE_ID_MISMATCH", "id", "does not match canonical record body")

    _validate_contract(record.get("contract"), "contract", issues)
    candidate_key = _string(record, "candidate_key", "candidate_key", issues)
    if candidate_key is not None and CANDIDATE_KEY.fullmatch(candidate_key) is None:
        _add(issues, "INVALID_CANDIDATE_KEY", "candidate_key", "must be a full git or snapshot identity")
    _validate_requirements(record.get("requirements"), issues)
    evidence_type = _string(record, "type", "type", issues)
    if evidence_type is not None and evidence_type not in EVIDENCE_TYPES:
        _add(issues, "INVALID_EVIDENCE_TYPE", "type", "is not a v1 evidence type")
    _string(record, "assertion", "assertion", issues)
    _string(record, "observation", "observation", issues)
    _string(record, "oracle", "oracle", issues)
    result = _string(record, "result", "result", issues)
    if result is not None and result not in RESULTS:
        _add(issues, "INVALID_EVIDENCE_RESULT", "result", "must be passed, failed, or inconclusive")
    environment_id = _validate_environment(record.get("environment"), issues)
    _timestamp(record.get("observed_at"), "observed_at", issues)
    _validate_execution(record.get("execution"), candidate_key, environment_id, result, issues)
    _validate_reference(record.get("reference"), issues)
    _validate_artifact(record.get("artifact"), issues)
    limitations = record.get("limitations")
    if not isinstance(limitations, list) or any(not isinstance(item, str) or not item for item in limitations):
        _add(issues, "INVALID_LIMITATIONS", "limitations", "must be an array of nonempty strings")

    execution = record.get("execution")
    reference = record.get("reference")
    if evidence_type in EXECUTION_TYPES and execution is None:
        _add(issues, "MISSING_EXECUTION_RECEIPT", "execution", "executable evidence requires trusted execution facts")
    if evidence_type in REFERENCE_TYPES and reference is None:
        _add(issues, "MISSING_AUTHORITATIVE_REFERENCE", "reference", "manual/external evidence requires a provenance reference")
    if evidence_type in {"http", "browser"} and execution is None and reference is None:
        _add(issues, "MISSING_OBSERVATION_SOURCE", "$", "interface evidence requires an execution receipt or authoritative reference")
    _validate_context(record, context, issues)
    return issues


def render_record(record):
    requirements = ", ".join(record["requirements"])
    lines = [
        f"### Evidence {record['id']}",
        "",
        f"- Type: `{record['type']}`",
        f"- Requirements: {requirements}",
        f"- Candidate: `{record['candidate_key']}`",
        f"- Contract: `{record['contract']['source']} {record['contract']['revision']}` (`{record['contract']['sha256']}`)",
        f"- Observed at: `{record['observed_at']}`",
        f"- Result: **{record['result']}**",
        f"- Assertion: {record['assertion']}",
        f"- Observation: {record['observation']}",
        f"- Oracle: {record['oracle']}",
        f"- Environment: `{record['environment']['id']}` - {record['environment']['description']}",
    ]
    if record.get("execution") is not None:
        execution = record["execution"]
        lines.extend([
            f"- Execution receipt: `{execution['receipt_id']}`",
            f"- Command/tool: `{execution['tool']}` / `{execution['command']}`",
            f"- Exit status: `{execution['exit_status']}` (expected `{execution['expected_exit_status']}`)",
            f"- Output digest: `{execution['output_sha256']}`",
        ])
    if record.get("reference") is not None:
        reference = record["reference"]
        lines.append(f"- Reference: `{reference['kind']}` {reference['locator']}")
    if record.get("artifact") is not None:
        artifact = record["artifact"]
        lines.append(f"- Retained artifact: `{artifact['name']}` `{artifact['sha256']}` at {artifact['locator']}")
    if record["limitations"]:
        lines.append("- Limitations: " + "; ".join(record["limitations"]))
    return "\n".join(lines) + "\n"


def _load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify a Promise to Proof Evidence Record v1")
    parser.add_argument("record", help="path to an evidence record JSON file")
    parser.add_argument("--context", help="optional proof-context JSON for contract/candidate/requirement checks")
    parser.add_argument("--render", action="store_true", help="render deterministic Markdown after validation")
    parser.add_argument("--print-id", action="store_true", help="print the canonical evidence ID for the supplied body")
    args = parser.parse_args(argv)
    try:
        record = _load_json(args.record)
        context = _load_json(args.context) if args.context else None
    except (OSError, json.JSONDecodeError) as error:
        print(f"INVALID {args.record}")
        print(f"INPUT_ERROR $: {error}")
        return 1
    if args.print_id:
        print(evidence_id(record))
    issues = verify_record(record, context)
    if issues:
        print(f"INVALID {args.record}")
        for issue in issues:
            print(f"{issue['code']} {issue['path']}: {issue['message']}")
        return 1
    print(f"VALID {args.record}")
    if args.render:
        print(render_record(record), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
