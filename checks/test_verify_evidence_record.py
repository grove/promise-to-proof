import copy
import json
import unittest
from pathlib import Path

from verify_evidence_record import evidence_id, render_record, verify_record


FIXTURES = Path(__file__).parent / "fixtures" / "evidence-record-v1"


def merge_patch(target, patch):
    if not isinstance(patch, dict):
        return copy.deepcopy(patch)
    if not isinstance(target, dict):
        target = {}
    result = copy.deepcopy(target)
    for key, value in patch.items():
        if value is None:
            result.pop(key, None)
        else:
            result[key] = merge_patch(result.get(key), value)
    return result


class EvidenceRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = json.loads((FIXTURES / "context.json").read_text(encoding="utf-8"))
        cls.command = json.loads((FIXTURES / "valid-command.json").read_text(encoding="utf-8"))
        cls.http = json.loads((FIXTURES / "valid-http.json").read_text(encoding="utf-8"))
        cls.manual = json.loads((FIXTURES / "valid-manual.json").read_text(encoding="utf-8"))
        cls.invalid_cases = json.loads((FIXTURES / "invalid-cases.json").read_text(encoding="utf-8"))

    def test_valid_fixture_types(self):
        for record in (self.command, self.http, self.manual):
            with self.subTest(evidence_type=record["type"]):
                self.assertEqual(verify_record(record, self.context), [])

    def test_identity_is_deterministic_and_body_sensitive(self):
        self.assertEqual(evidence_id(self.command), self.command["id"])
        rebuilt = json.loads(json.dumps(self.command, sort_keys=False))
        self.assertEqual(evidence_id(rebuilt), self.command["id"])
        changed = copy.deepcopy(self.command)
        changed["observation"] += " Additional fact."
        self.assertNotEqual(evidence_id(changed), self.command["id"])

    def test_seeded_invalid_records(self):
        for case in self.invalid_cases:
            with self.subTest(case=case["name"]):
                record = merge_patch(self.command, case["patch"])
                codes = {issue["code"] for issue in verify_record(record, self.context)}
                self.assertTrue(set(case["expected_codes"]).issubset(codes), codes)

    def test_manual_evidence_requires_authoritative_reference(self):
        record = copy.deepcopy(self.manual)
        record["reference"] = None
        record["id"] = evidence_id(record)
        codes = {issue["code"] for issue in verify_record(record, self.context)}
        self.assertIn("MISSING_AUTHORITATIVE_REFERENCE", codes)

    def test_interface_evidence_requires_observation_source(self):
        record = copy.deepcopy(self.http)
        record["execution"] = None
        record["reference"] = None
        record["id"] = evidence_id(record)
        codes = {issue["code"] for issue in verify_record(record, self.context)}
        self.assertIn("MISSING_OBSERVATION_SOURCE", codes)

    def test_executable_narrative_without_receipt_is_rejected(self):
        record = copy.deepcopy(self.command)
        record["execution"] = None
        record["observation"] = "The model says the command passed."
        record["id"] = evidence_id(record)
        codes = {issue["code"] for issue in verify_record(record, self.context)}
        self.assertIn("MISSING_EXECUTION_RECEIPT", codes)

    def test_renderer_is_deterministic_and_does_not_emit_requirement_verdict(self):
        first = render_record(self.command)
        second = render_record(json.loads(json.dumps(self.command)))
        self.assertEqual(first, second)
        self.assertIn(self.command["id"], first)
        self.assertIn("Result: **passed**", first)
        self.assertNotIn("PROVEN", first)
        self.assertNotIn("NOT PROVEN", first)

    def test_reference_structure_is_validated(self):
        record = copy.deepcopy(self.manual)
        record["reference"]["locator"] = ""
        record["reference"]["sha256"] = "bad"
        record["id"] = evidence_id(record)
        codes = {issue["code"] for issue in verify_record(record, self.context)}
        self.assertIn("EMPTY_VALUE", codes)
        self.assertIn("INVALID_DIGEST", codes)

    def test_packaged_prove_reference_matches_canonical_document(self):
        root = Path(__file__).resolve().parents[1]
        canonical = (root / "docs" / "evidence-record-v1.md").read_text(encoding="utf-8")
        packaged = (root / "skills" / "productivity" / "prove" / "references" / "evidence-record-v1.md").read_text(encoding="utf-8")
        self.assertEqual(canonical, packaged)


if __name__ == "__main__":
    unittest.main()
