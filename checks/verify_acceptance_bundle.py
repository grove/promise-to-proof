#!/usr/bin/env python3
"""Validate a Promise to Proof acceptance bundle without external packages."""

import argparse
import base64
import binascii
import hashlib
import json
import re
from pathlib import PurePosixPath


SCHEMA = "promise-to-proof/acceptance-bundle/v1"
MATRIX_HEADER = [
    "ID",
    "Source",
    "Requirement",
    "Boundaries / counterexamples",
    "Seam",
    "Oracle",
    "Planned evidence",
    "Plan state",
]
HEX_64 = re.compile(r"[0-9a-f]{64}\Z")
REQUIREMENT_ID = re.compile(r"R[1-9][0-9]*\Z")
EVIDENCE_ID = re.compile(r"E[1-9][0-9]*\Z")
GIT_KEY = re.compile(r"git:(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
SNAPSHOT_KEY = re.compile(r"snapshot:sha256:([0-9a-f]{64})\Z")


def _add(issues, code, path, message):
    issues.append({"code": code, "path": path, "message": message})


def _object(parent, key, path, issues):
    if key not in parent:
        _add(issues, "MISSING_FIELD", path, "required object is missing")
        return {}
    value = parent[key]
    if not isinstance(value, dict):
        _add(issues, "INVALID_TYPE", path, "must be an object")
        return {}
    return value


def _string(parent, key, path, issues, allow_empty=False):
    if key not in parent:
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


def _array(parent, key, path, issues):
    if key not in parent:
        _add(issues, "MISSING_FIELD", path, "required array is missing")
        return []
    value = parent[key]
    if not isinstance(value, list):
        _add(issues, "INVALID_TYPE", path, "must be an array")
        return []
    return value


def _keys(value, required, path, issues):
    missing = sorted(set(required) - set(value))
    unknown = sorted(set(value) - set(required))
    for key in missing:
        _add(issues, "MISSING_FIELD", f"{path}.{key}", "required field is missing")
    for key in unknown:
        _add(issues, "UNKNOWN_FIELD", f"{path}.{key}", "field is not defined by v1")


def _text_digest(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _text_object(value, path, issues, digest_code="CONTENT_DIGEST_MISMATCH"):
    if not isinstance(value, dict):
        _add(issues, "INVALID_TYPE", path, "must be an object")
        return None
    _keys(value, {"content", "sha256"}, path, issues)
    content = _string(value, "content", f"{path}.content", issues)
    digest = _string(value, "sha256", f"{path}.sha256", issues)
    if digest is not None and not HEX_64.fullmatch(digest):
        _add(issues, "INVALID_DIGEST", f"{path}.sha256", "must be 64 lowercase hexadecimal characters")
    if content is not None and digest is not None and HEX_64.fullmatch(digest):
        if _text_digest(content) != digest:
            _add(issues, digest_code, path, "digest does not match exact UTF-8 content")
    return content


def _split_markdown_row(line):
    if not line.startswith("|") or not line.endswith("|"):
        return None
    cells = []
    current = []
    index = 1
    while index < len(line) - 1:
        character = line[index]
        if character == "\\" and index + 1 < len(line) - 1 and line[index + 1] == "|":
            current.append("|")
            index += 2
            continue
        if character == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(character)
        index += 1
    cells.append("".join(current).strip())
    return cells


def _contract_requirements(content, issues):
    lines = content.splitlines()
    headings = [index for index, line in enumerate(lines) if line == "## Acceptance matrix"]
    if len(headings) != 1:
        _add(issues, "AMBIGUOUS_ACCEPTANCE_MATRIX", "contract.content", "must contain exactly one acceptance matrix")
        return []

    cursor = headings[0] + 1
    while cursor < len(lines) and not lines[cursor]:
        cursor += 1
    if cursor + 1 >= len(lines):
        _add(issues, "MALFORMED_ACCEPTANCE_MATRIX", "contract.content", "matrix header or separator is missing")
        return []

    header = _split_markdown_row(lines[cursor])
    separator = _split_markdown_row(lines[cursor + 1])
    if header != MATRIX_HEADER:
        _add(issues, "MALFORMED_ACCEPTANCE_MATRIX", "contract.content", "matrix header does not match v1")
        return []
    if separator is None or len(separator) != len(MATRIX_HEADER) or any(
        re.fullmatch(r":?-{3,}:?", cell) is None for cell in separator
    ):
        _add(issues, "MALFORMED_ACCEPTANCE_MATRIX", "contract.content", "matrix separator does not match v1")
        return []

    requirement_ids = []
    plan_states = []
    cursor += 2
    while cursor < len(lines) and lines[cursor].startswith("|"):
        cells = _split_markdown_row(lines[cursor])
        row_path = f"contract.content:matrix-row-{len(requirement_ids) + 1}"
        if cells is None or len(cells) != len(MATRIX_HEADER) or any(not cell for cell in cells):
            _add(issues, "MALFORMED_ACCEPTANCE_ROW", row_path, "row must contain eight nonempty cells")
            cursor += 1
            continue
        requirement_id = cells[0]
        if REQUIREMENT_ID.fullmatch(requirement_id) is None:
            _add(issues, "INVALID_REQUIREMENT_ID", row_path, "ID must match R[1-9][0-9]*")
        if requirement_id in requirement_ids:
            _add(issues, "DUPLICATE_REQUIREMENT", row_path, f"{requirement_id} appears more than once")
        if cells[7] not in {"planned", "gap"}:
            _add(issues, "INVALID_PLAN_STATE", row_path, "plan state must be planned or gap")
        requirement_ids.append(requirement_id)
        plan_states.append(cells[7])
        cursor += 1

    if not requirement_ids:
        _add(issues, "EMPTY_ACCEPTANCE_MATRIX", "contract.content", "matrix must contain at least one requirement")
    if "gap" in plan_states:
        _add(issues, "CONTRACT_HAS_GAP", "contract.content", "a REVIEWED_AND_PROVEN bundle cannot contain a gap row")
    return requirement_ids


def _validate_contract(contract, issues):
    _keys(contract, {"source", "revision", "content", "sha256"}, "contract", issues)
    source = _string(contract, "source", "contract.source", issues)
    revision = _string(contract, "revision", "contract.revision", issues)
    content = _string(contract, "content", "contract.content", issues)
    digest = _string(contract, "sha256", "contract.sha256", issues)
    if digest is not None and not HEX_64.fullmatch(digest):
        _add(issues, "INVALID_DIGEST", "contract.sha256", "must be 64 lowercase hexadecimal characters")
    if content is not None and digest is not None and HEX_64.fullmatch(digest):
        if _text_digest(content) != digest:
            _add(issues, "CONTRACT_DIGEST_MISMATCH", "contract", "digest does not match exact UTF-8 contract content")
    if revision is not None and re.fullmatch(r"v[1-9][0-9]*", revision) is None:
        _add(issues, "INVALID_CONTRACT_REVISION", "contract.revision", "must match v[1-9][0-9]*")
    if content is None:
        return source, revision, digest, []
    if source is not None and f"# Acceptance contract: {source}" not in content.splitlines():
        _add(issues, "CONTRACT_SOURCE_MISMATCH", "contract.content", "heading does not match contract.source")
    revision_lines = [line for line in content.splitlines() if line.startswith("Contract revision:")]
    expected_revision = f"Contract revision: {revision}" if revision is not None else None
    if len(revision_lines) != 1 or revision_lines[0] != expected_revision:
        _add(issues, "CONTRACT_REVISION_MISMATCH", "contract.content", "revision line does not match contract.revision")
    return source, revision, digest, _contract_requirements(content, issues)


def _valid_path(path):
    if not path or path.startswith("/") or "\\" in path or "\0" in path:
        return False
    parts = PurePosixPath(path).parts
    return all(part not in {"", ".", ".."} for part in parts)


def _validate_candidate(candidate, issues):
    _keys(candidate, {"key", "manifest", "comparison_base"}, "candidate", issues)
    candidate_key = _string(candidate, "key", "candidate.key", issues)
    comparison_base = _string(candidate, "comparison_base", "candidate.comparison_base", issues)
    manifest = _array(candidate, "manifest", "candidate.manifest", issues)
    if comparison_base is not None and GIT_KEY.fullmatch(comparison_base) is None:
        _add(issues, "INVALID_COMPARISON_BASE", "candidate.comparison_base", "must be git: followed by a full object ID")

    canonical_entries = []
    paths = set()
    for index, entry in enumerate(manifest):
        path = f"candidate.manifest[{index}]"
        if not isinstance(entry, dict):
            _add(issues, "INVALID_TYPE", path, "must be an object")
            continue
        entry_type = entry.get("type")
        required = {"path", "type", "mode", "content_base64"} if entry_type == "file" else {"path", "type", "mode", "target"}
        _keys(entry, required, path, issues)
        entry_path = _string(entry, "path", f"{path}.path", issues)
        mode = _string(entry, "mode", f"{path}.mode", issues)
        if entry_path is not None:
            if not _valid_path(entry_path):
                _add(issues, "INVALID_CANDIDATE_PATH", f"{path}.path", "must be a relative POSIX path without dot segments")
            if entry_path in paths:
                _add(issues, "DUPLICATE_CANDIDATE_PATH", f"{path}.path", "path appears more than once")
            paths.add(entry_path)
        if entry_type == "file":
            if mode not in {"100644", "100755"}:
                _add(issues, "INVALID_FILE_MODE", f"{path}.mode", "file mode must be 100644 or 100755")
            encoded = _string(entry, "content_base64", f"{path}.content_base64", issues, allow_empty=True)
            if entry_path is None or mode is None or encoded is None:
                continue
            try:
                decoded = base64.b64decode(encoded, validate=True)
            except (binascii.Error, ValueError):
                _add(issues, "INVALID_BASE64", f"{path}.content_base64", "must be valid canonical base64")
                continue
            canonical_base64 = base64.b64encode(decoded).decode("ascii")
            if canonical_base64 != encoded:
                _add(issues, "NONCANONICAL_BASE64", f"{path}.content_base64", "must use canonical base64 encoding")
            canonical_entries.append({"path": entry_path, "type": "file", "mode": mode, "content_base64": canonical_base64})
        elif entry_type == "symlink":
            if mode != "120000":
                _add(issues, "INVALID_FILE_MODE", f"{path}.mode", "symlink mode must be 120000")
            target = _string(entry, "target", f"{path}.target", issues)
            if target is not None and "\0" in target:
                _add(issues, "INVALID_SYMLINK_TARGET", f"{path}.target", "must not contain NUL")
            if entry_path is not None and mode is not None and target is not None:
                canonical_entries.append({"path": entry_path, "type": "symlink", "mode": mode, "target": target})
        else:
            _add(issues, "INVALID_ENTRY_TYPE", f"{path}.type", "must be file or symlink")

    key_match = SNAPSHOT_KEY.fullmatch(candidate_key or "")
    if key_match is None:
        _add(issues, "UNSUPPORTED_CANDIDATE_KEY", "candidate.key", "v1 requires snapshot:sha256:<digest>")
    elif len(canonical_entries) == len(manifest) and len(paths) == len(manifest):
        canonical_entries.sort(key=lambda entry: entry["path"])
        encoded_manifest = json.dumps(
            canonical_entries, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        actual_digest = hashlib.sha256(encoded_manifest).hexdigest()
        if actual_digest != key_match.group(1):
            _add(issues, "CANDIDATE_DIGEST_MISMATCH", "candidate", "key does not match the canonical manifest")
    return candidate_key, comparison_base


def _validate_identity(value, path, expected, issues):
    if not isinstance(value, dict):
        _add(issues, "INVALID_TYPE", path, "must be an object")
        return
    _keys(value, {"source", "revision", "sha256"}, path, issues)
    observed = (
        _string(value, "source", f"{path}.source", issues),
        _string(value, "revision", f"{path}.revision", issues),
        _string(value, "sha256", f"{path}.sha256", issues),
    )
    if all(item is not None for item in observed) and observed != expected:
        _add(issues, "CONTRACT_IDENTITY_MISMATCH", path, "does not match the retained contract")


def _validate_id_list(values, path, pattern, duplicate_code, issues):
    observed = []
    for index, value in enumerate(values):
        item_path = f"{path}[{index}]"
        if not isinstance(value, str) or pattern.fullmatch(value) is None:
            _add(issues, "INVALID_ID", item_path, "has an invalid identifier")
            continue
        if value in observed:
            _add(issues, duplicate_code, item_path, f"{value} appears more than once")
        observed.append(value)
    return observed


def _validate_stability(value, path, issues):
    if not isinstance(value, dict):
        _add(issues, "INVALID_TYPE", path, "must be an object")
        return
    _keys(value, {"contract", "candidate"}, path, issues)
    contract = _string(value, "contract", f"{path}.contract", issues)
    candidate = _string(value, "candidate", f"{path}.candidate", issues)
    if contract is not None and contract != "unchanged":
        _add(issues, "REPORT_STALE", f"{path}.contract", "must be unchanged")
    if candidate is not None and candidate != "unchanged":
        _add(issues, "REPORT_STALE", f"{path}.candidate", "must be unchanged")


def _validate_review(review, contract_identity, candidate_key, comparison_base, requirement_ids, issues):
    required = {"contract", "candidate_key", "comparison_base", "coverage", "status", "stability", "details"}
    _keys(review, required, "review", issues)
    _validate_identity(review.get("contract"), "review.contract", contract_identity, issues)
    _validate_stability(review.get("stability"), "review.stability", issues)
    review_candidate = _string(review, "candidate_key", "review.candidate_key", issues)
    review_base = _string(review, "comparison_base", "review.comparison_base", issues)
    status = _string(review, "status", "review.status", issues)
    coverage = _validate_id_list(
        _array(review, "coverage", "review.coverage", issues),
        "review.coverage",
        REQUIREMENT_ID,
        "DUPLICATE_REVIEW_COVERAGE",
        issues,
    )
    if review_candidate is not None and review_candidate != candidate_key:
        _add(issues, "CANDIDATE_IDENTITY_MISMATCH", "review.candidate_key", "does not match candidate.key")
    if review_base is not None and review_base != comparison_base:
        _add(issues, "COMPARISON_BASE_MISMATCH", "review.comparison_base", "does not match candidate.comparison_base")
    if status is not None and status != "REVIEWED":
        _add(issues, "REVIEW_NOT_COMPLETE", "review.status", "the combined claim requires REVIEWED")
    if len(coverage) != len(requirement_ids) or set(coverage) != set(requirement_ids):
        _add(issues, "REVIEW_COVERAGE_MISMATCH", "review.coverage", "must cover every contract requirement exactly once")
    _text_object(review.get("details"), "review.details", issues)


def _validate_proof(proof, contract_identity, candidate_key, requirement_ids, issues):
    required = {
        "contract",
        "candidate_key",
        "status",
        "stability",
        "verification_context",
        "verdicts",
        "evidence",
        "details",
    }
    _keys(proof, required, "proof", issues)
    _validate_identity(proof.get("contract"), "proof.contract", contract_identity, issues)
    _validate_stability(proof.get("stability"), "proof.stability", issues)
    proof_candidate = _string(proof, "candidate_key", "proof.candidate_key", issues)
    status = _string(proof, "status", "proof.status", issues)
    _string(proof, "verification_context", "proof.verification_context", issues)
    if proof_candidate is not None and proof_candidate != candidate_key:
        _add(issues, "CANDIDATE_IDENTITY_MISMATCH", "proof.candidate_key", "does not match candidate.key")
    if status is not None and status != "PROVEN":
        _add(issues, "PROOF_NOT_COMPLETE", "proof.status", "the combined claim requires PROVEN")

    evidence_by_id = {}
    for index, evidence in enumerate(_array(proof, "evidence", "proof.evidence", issues)):
        path = f"proof.evidence[{index}]"
        if not isinstance(evidence, dict):
            _add(issues, "INVALID_TYPE", path, "must be an object")
            continue
        _keys(evidence, {"id", "result", "assertion", "observation", "artifact"}, path, issues)
        evidence_id = _string(evidence, "id", f"{path}.id", issues)
        result = _string(evidence, "result", f"{path}.result", issues)
        _string(evidence, "assertion", f"{path}.assertion", issues)
        _string(evidence, "observation", f"{path}.observation", issues)
        _text_object(evidence.get("artifact"), f"{path}.artifact", issues)
        if evidence_id is not None and EVIDENCE_ID.fullmatch(evidence_id) is None:
            _add(issues, "INVALID_EVIDENCE_ID", f"{path}.id", "must match E[1-9][0-9]*")
        if evidence_id in evidence_by_id:
            _add(issues, "DUPLICATE_EVIDENCE", f"{path}.id", f"{evidence_id} appears more than once")
        if result not in {"passed", "failed", "inconclusive"}:
            _add(issues, "INVALID_EVIDENCE_RESULT", f"{path}.result", "must be passed, failed, or inconclusive")
        if evidence_id is not None:
            evidence_by_id[evidence_id] = result

    verdict_ids = []
    referenced_evidence = set()
    for index, verdict in enumerate(_array(proof, "verdicts", "proof.verdicts", issues)):
        path = f"proof.verdicts[{index}]"
        if not isinstance(verdict, dict):
            _add(issues, "INVALID_TYPE", path, "must be an object")
            continue
        _keys(verdict, {"id", "verdict", "evidence"}, path, issues)
        requirement_id = _string(verdict, "id", f"{path}.id", issues)
        verdict_value = _string(verdict, "verdict", f"{path}.verdict", issues)
        evidence_refs = _validate_id_list(
            _array(verdict, "evidence", f"{path}.evidence", issues),
            f"{path}.evidence",
            EVIDENCE_ID,
            "DUPLICATE_EVIDENCE_REFERENCE",
            issues,
        )
        if requirement_id is not None:
            if REQUIREMENT_ID.fullmatch(requirement_id) is None:
                _add(issues, "INVALID_REQUIREMENT_ID", f"{path}.id", "must match R[1-9][0-9]*")
            if requirement_id in verdict_ids:
                _add(issues, "DUPLICATE_PROOF_VERDICT", f"{path}.id", f"{requirement_id} appears more than once")
            verdict_ids.append(requirement_id)
        if verdict_value not in {"proven", "disproven", "not_proven"}:
            _add(issues, "INVALID_VERDICT", f"{path}.verdict", "must be proven, disproven, or not_proven")
        if status == "PROVEN" and verdict_value != "proven":
            _add(issues, "PROOF_STATUS_CONTRADICTION", path, "PROVEN cannot contain a non-proven verdict")
        if verdict_value == "proven" and not evidence_refs:
            _add(issues, "MISSING_EVIDENCE", f"{path}.evidence", "a proven verdict needs retained evidence")
        for evidence_ref in evidence_refs:
            referenced_evidence.add(evidence_ref)
            if evidence_ref not in evidence_by_id:
                _add(issues, "MISSING_EVIDENCE", f"{path}.evidence", f"{evidence_ref} is not retained")
            elif verdict_value == "proven" and evidence_by_id[evidence_ref] != "passed":
                _add(issues, "EVIDENCE_NOT_PASSING", f"{path}.evidence", f"{evidence_ref} did not pass")

    if len(verdict_ids) != len(requirement_ids) or set(verdict_ids) != set(requirement_ids):
        _add(issues, "PROOF_COVERAGE_MISMATCH", "proof.verdicts", "must cover every contract requirement exactly once")
    for evidence_id in sorted(set(evidence_by_id) - referenced_evidence):
        _add(issues, "UNREFERENCED_EVIDENCE", "proof.evidence", f"{evidence_id} is not referenced by a verdict")
    _text_object(proof.get("details"), "proof.details", issues)


def verify_bundle(bundle):
    issues = []
    if not isinstance(bundle, dict):
        return [{"code": "INVALID_TYPE", "path": "$", "message": "bundle must be an object"}]
    _keys(bundle, {"schema", "claim", "contract", "candidate", "review", "proof"}, "$", issues)
    schema = _string(bundle, "schema", "schema", issues)
    claim = _string(bundle, "claim", "claim", issues)
    if schema is not None and schema != SCHEMA:
        _add(issues, "UNSUPPORTED_SCHEMA", "schema", f"must be {SCHEMA}")
    if claim is not None and claim != "REVIEWED_AND_PROVEN":
        _add(issues, "UNSUPPORTED_CLAIM", "claim", "v1 checks only REVIEWED_AND_PROVEN claims")

    contract = _object(bundle, "contract", "contract", issues)
    candidate = _object(bundle, "candidate", "candidate", issues)
    review = _object(bundle, "review", "review", issues)
    proof = _object(bundle, "proof", "proof", issues)
    source, revision, digest, requirement_ids = _validate_contract(contract, issues)
    candidate_key, comparison_base = _validate_candidate(candidate, issues)
    contract_identity = (source, revision, digest)
    _validate_review(review, contract_identity, candidate_key, comparison_base, requirement_ids, issues)
    _validate_proof(proof, contract_identity, candidate_key, requirement_ids, issues)
    return issues


def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify a Promise to Proof acceptance bundle v1")
    parser.add_argument("bundle", help="path to the retained JSON bundle")
    args = parser.parse_args(argv)
    try:
        with open(args.bundle, "r", encoding="utf-8") as bundle_file:
            bundle = json.load(bundle_file)
    except (OSError, json.JSONDecodeError) as error:
        print(f"INVALID {args.bundle}")
        print(f"INPUT_ERROR $: {error}")
        return 1

    issues = verify_bundle(bundle)
    if issues:
        print(f"INVALID {args.bundle}")
        for issue in issues:
            print(f"{issue['code']} {issue['path']}: {issue['message']}")
        return 1
    print(f"VALID {args.bundle}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())