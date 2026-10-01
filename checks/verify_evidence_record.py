#!/usr/bin/env python3
"""Validate and render Evidence Record v1 using only the standard library."""
import argparse
from datetime import datetime
import hashlib
import json
import re

from verify_acceptance_bundle import HEX_64, GIT_KEY, SNAPSHOT_KEY, REQUIREMENT_ID, _contract_requirements

SCHEMA = "promise-to-proof/evidence-record/v1"
FIELDS = {"schema", "id", "candidate", "contract", "requirements", "type", "assertion",
          "observation", "oracle", "outcome", "environment", "timestamp", "limitations"}
OPTIONAL = {"execution", "provenance", "interpretation", "artifacts"}
FACTS = {"identity", "exit_status", "started_at", "finished_at"}
OUTPUT = {"output_sha256", "result"}
RUNNER_KEYS = FACTS | OUTPUT | {"command", "tool", "interface", "output_digest"}


def canonical_bytes(obj):
    """Sorted, compact, non-ASCII-escaped UTF-8 JSON; no non-finite numbers."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def record_digest(record):
    return hashlib.sha256(canonical_bytes(record)).hexdigest()


def verify_record(record, context=None):
    issues = []

    def add(code, path, message):
        issues.append({"code": code, "path": path, "message": message})

    def shape(value, required, optional, path):
        if not isinstance(value, dict):
            add("INVALID_TYPE", path, "must be an object")
            return {}
        for key in sorted(required - value.keys()):
            add("MISSING_FIELD", f"{path}.{key}", "required field is missing")
        for key in sorted(value.keys() - required - optional):
            add("UNKNOWN_FIELD", f"{path}.{key}", "field is not defined by v1")
        return value

    def text(value, path):
        if not isinstance(value, str) or not value.strip():
            add("INVALID_TEXT", path, "must be a nonempty string")
            return False
        return True

    def digest(value, path):
        if not isinstance(value, str) or HEX_64.fullmatch(value) is None:
            add("INVALID_DIGEST", path, "must be 64 lowercase hexadecimal characters")

    def candidate(value, path):
        if not isinstance(value, str) or not (GIT_KEY.fullmatch(value) or SNAPSHOT_KEY.fullmatch(value)):
            add("INVALID_CANDIDATE", path, "must be an exact git or SHA-256 snapshot key")

    def timestamp(value, path):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                raise ValueError("timezone required")
            return parsed
        except (ValueError, TypeError, AttributeError):
            add("INVALID_TIMESTAMP", path, "must be an ISO 8601 timestamp with timezone")
            return None

    def integer(value, path):
        if type(value) is not int:
            add("INVALID_RESULT", path, "must be an integer")

    def execution(value, path, receipt=False):
        required = FACTS | ({"id", "candidate", "environment"} if receipt else set())
        value = shape(value, required, OUTPUT | (set() if receipt else {"receipt"}), path)
        text(value.get("identity"), f"{path}.identity")
        integer(value.get("exit_status"), f"{path}.exit_status")
        start = timestamp(value.get("started_at"), f"{path}.started_at")
        finish = timestamp(value.get("finished_at"), f"{path}.finished_at")
        if start and finish and finish < start:
            add("INCONSISTENT_RESULT", path, "execution finished before it started")
        if len(OUTPUT & value.keys()) != 1:
            add("INVALID_OUTPUT", path, "provide exactly one output_sha256 or compact result")
        if "output_sha256" in value:
            digest(value["output_sha256"], f"{path}.output_sha256")
        if "result" in value:
            text(value["result"], f"{path}.result")
        if receipt:
            text(value.get("id"), f"{path}.id")
            candidate(value.get("candidate"), f"{path}.candidate")
            text(value.get("environment"), f"{path}.environment")
        return value

    def misplaced(value, path):
        if isinstance(value, dict):
            for key in sorted(value):
                if key in RUNNER_KEYS:
                    add("MISPLACED_EXECUTION_FACT", f"{path}.{key}", "runner facts belong in execution")
                misplaced(value[key], f"{path}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                misplaced(item, f"{path}[{index}]")

    try:
        canonical_bytes(record)
        if context is not None:
            canonical_bytes(context)
    except (TypeError, ValueError, UnicodeError):
        return [{"code": "INVALID_JSON", "path": "$", "message": "must contain finite JSON values"}]
    record = shape(record, FIELDS, OPTIONAL, "$")
    if record.get("schema") != SCHEMA:
        add("UNSUPPORTED_SCHEMA", "schema", f"must be {SCHEMA}")
    for field in ("id", "type", "assertion", "observation", "environment"):
        text(record.get(field), field)
    candidate(record.get("candidate"), "candidate")
    contract = shape(record.get("contract"), {"source", "revision", "sha256"}, set(), "contract")
    text(contract.get("source"), "contract.source")
    if not isinstance(contract.get("revision"), str) or re.fullmatch(r"v[1-9][0-9]*", contract["revision"]) is None:
        add("INVALID_CONTRACT_REVISION", "contract.revision", "must match v[1-9][0-9]*")
    digest(contract.get("sha256"), "contract.sha256")
    requirements = record.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        add("INVALID_REQUIREMENTS", "requirements", "must be a nonempty array")
        requirements = []
    for index, item in enumerate(requirements):
        if not isinstance(item, str) or not REQUIREMENT_ID.fullmatch(item):
            add("INVALID_REQUIREMENTS", f"requirements[{index}]", "must match R[1-9][0-9]*")
        if item in requirements[:index]:
            add("DUPLICATE_REQUIREMENT", f"requirements[{index}]", "requirement IDs must be unique")
    oracle = shape(record.get("oracle"), {"expected_result"}, {"expected_exit_status"}, "oracle")
    text(oracle.get("expected_result"), "oracle.expected_result")
    if "expected_exit_status" in oracle:
        integer(oracle["expected_exit_status"], "oracle.expected_exit_status")
    if record.get("outcome") not in ("passed", "failed", "inconclusive"):
        add("INVALID_OUTCOME", "outcome", "must be passed, failed, or inconclusive; never a requirement verdict")
    timestamp(record.get("timestamp"), "timestamp")
    limitations = record.get("limitations")
    if not isinstance(limitations, list):
        add("INVALID_LIMITATIONS", "limitations", "must be an explicit array (empty means none stated)")
    else:
        for index, item in enumerate(limitations):
            text(item, f"limitations[{index}]")
    for field in ("interpretation", "provenance"):
        if field in record:
            text(record[field], field)
    for key in sorted(record.keys() - {"execution"}):
        misplaced({key: record[key]}, "$")
    artifacts = record.get("artifacts", [])
    if not isinstance(artifacts, list):
        add("INVALID_ARTIFACT", "artifacts", "must be an array")
    else:
        for index, artifact in enumerate(artifacts):
            path = f"artifacts[{index}]"
            artifact = shape(artifact, {"reference", "sha256"}, {"limitation"}, path)
            text(artifact.get("reference"), f"{path}.reference")
            digest(artifact.get("sha256"), f"{path}.sha256")
            if "limitation" in artifact:
                text(artifact["limitation"], f"{path}.limitation")
    facts = execution(record["execution"], "execution") if "execution" in record else {}
    receipt_ref = facts.get("receipt")
    if record.get("type") in ("command", "test") and receipt_ref is None:
        add("MISSING_RECEIPT", "execution.receipt", "command/test evidence needs a trusted receipt reference")
    if receipt_ref is None:
        if not text(record.get("provenance"), "provenance"):
            add("MISSING_PROVENANCE", "provenance", "name the strongest available authoritative reference")
    else:
        receipt_ref = shape(receipt_ref, {"id", "sha256"}, set(), "execution.receipt")
        text(receipt_ref.get("id"), "execution.receipt.id")
        digest(receipt_ref.get("sha256"), "execution.receipt.sha256")
    if record.get("outcome") == "passed" and "expected_exit_status" in oracle:
        if facts.get("exit_status") != oracle["expected_exit_status"]:
            add("INCONSISTENT_RESULT", "execution.exit_status", "passed observation disagrees with oracle exit status")
    if context is not None:
        context = shape(context, {"candidate", "contract", "receipts"}, set(), "context")
        candidate(context.get("candidate"), "context.candidate")
        if record.get("candidate") != context.get("candidate"):
            add("CANDIDATE_MISMATCH", "candidate", "candidate differs from proof context")
        expected = shape(context.get("contract"), {"source", "revision", "sha256", "content"}, set(), "context.contract")
        digest(expected.get("sha256"), "context.contract.sha256")
        text(expected.get("source"), "context.contract.source")
        if not isinstance(expected.get("revision"), str) or re.fullmatch(r"v[1-9][0-9]*", expected["revision"]) is None:
            add("INVALID_CONTRACT_REVISION", "context.contract.revision", "must match v[1-9][0-9]*")
        if text(expected.get("content"), "context.contract.content"):
            if hashlib.sha256(expected["content"].encode("utf-8")).hexdigest() != expected.get("sha256"):
                add("CONTRACT_DIGEST_MISMATCH", "context.contract", "digest differs from exact UTF-8 contract text")
            matrix_issues = []
            known = _contract_requirements(expected["content"], matrix_issues)
            # Evidence can observe a planned gap; a record does not assert bundle acceptance.
            issues.extend(item for item in matrix_issues if item["code"] != "CONTRACT_HAS_GAP")
            for item in requirements:
                if item not in known:
                    add("UNKNOWN_REQUIREMENT", "requirements", f"{item!r} is absent from context contract")
        for key in ("source", "revision", "sha256"):
            if contract.get(key) != expected.get(key):
                add("CONTRACT_MISMATCH", f"contract.{key}", "identity differs from proof context")
        receipts = context.get("receipts")
        if not isinstance(receipts, list):
            add("INVALID_TYPE", "context.receipts", "must be an array")
            receipts = []
        if receipt_ref is not None:
            matches = [item for item in receipts if isinstance(item, dict) and item.get("id") == receipt_ref.get("id")]
            if len(matches) != 1:
                add("MISSING_RECEIPT", "context.receipts", "must supply exactly one matching trusted receipt")
            else:
                receipt = execution(matches[0], "context.receipts", receipt=True)
                if record_digest(receipt) != receipt_ref.get("sha256"):
                    add("RECEIPT_DIGEST_MISMATCH", "execution.receipt", "digest differs from supplied receipt facts")
                if receipt.get("candidate") != record.get("candidate"):
                    add("RECEIPT_CANDIDATE_MISMATCH", "execution.receipt", "receipt candidate differs from record")
                if receipt.get("environment") != record.get("environment"):
                    add("RECEIPT_ENVIRONMENT_MISMATCH", "environment", "receipt environment differs from record")
                for key in sorted(FACTS | OUTPUT):
                    if facts.get(key) != receipt.get(key):
                        add("EXECUTION_FACT_MISMATCH", f"execution.{key}", "fact differs from trusted receipt")
    return issues


def render_record(record):
    """Render facts, without assigning requirement verdicts. Validate before calling."""
    lines = [f"### Evidence {record['id']}", "",
             f"Reference: `{record['id']}@sha256:{record_digest(record)}`", ""]
    for key in ("candidate", "contract", "requirements", "type", "assertion", "oracle",
                "observation", "outcome", "environment", "timestamp", "execution",
                "provenance", "interpretation", "artifacts", "limitations"):
        if key in record:
            value = canonical_bytes(record[key]).decode("utf-8")
            lines.append(f"- {key.replace('_', ' ').title()}: {value}")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record")
    parser.add_argument("--context")
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args(argv)
    try:
        with open(args.record, encoding="utf-8") as stream:
            record = json.load(stream)
        context = None
        if args.context:
            with open(args.context, encoding="utf-8") as stream:
                context = json.load(stream)
    except (OSError, ValueError, UnicodeError) as error:
        print(f"INPUT_ERROR $: {error}")
        return 1
    issues = verify_record(record, context)
    if issues:
        for item in issues:
            print(f"{item['code']} {item['path']}: {item['message']}")
        return 1
    print(render_record(record) if args.render else f"VALID {args.record}", end="" if args.render else "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
