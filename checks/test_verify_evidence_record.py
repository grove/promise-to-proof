import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from verify_evidence_record import canonical_bytes, record_digest, render_record, verify_record
from test_verify_acceptance_bundle import merge_patch

FIXTURES = Path(__file__).parent / "fixtures" / "evidence-record-v1"
CHECKER = Path(__file__).parent / "verify_evidence_record.py"


class EvidenceRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = {name: json.loads((FIXTURES / name).read_text(encoding="utf-8"))
                       for name in ("command.json", "http.json", "manual.json")}
        cls.context = json.loads((FIXTURES / "context.json").read_text(encoding="utf-8"))
        cls.digests = json.loads((FIXTURES / "digests.json").read_text(encoding="utf-8"))
        cls.cases = json.loads((FIXTURES / "invalid-cases.json").read_text(encoding="utf-8"))

    def test_valid_fixtures(self):
        for name, record in self.records.items():
            with self.subTest(name=name):
                self.assertEqual(verify_record(record), [])
                self.assertEqual(verify_record(record, self.context), [])
                for contextual in (False, True):
                    args = [sys.executable, str(CHECKER), str(FIXTURES / name)]
                    if contextual:
                        args += ["--context", str(FIXTURES / "context.json")]
                    observed = subprocess.run(args, capture_output=True, text=True)
                    self.assertEqual(observed.returncode, 0, observed.stdout + observed.stderr)

    def test_seeded_invalid_records(self):
        with tempfile.TemporaryDirectory() as scratch:
            for case in self.cases:
                with self.subTest(case=case["name"]):
                    record = merge_patch(self.records[case["fixture"]], case["patch"])
                    context = merge_patch(self.context, case.get("context_patch", {}))
                    expected = set(case["expected_codes"])
                    diagnostics = verify_record(record, context)
                    self.assertTrue(expected <= {item["code"] for item in diagnostics}, diagnostics)
                    self.assertEqual(diagnostics, verify_record(record, context))
                    for item in diagnostics:
                        self.assertEqual(set(item), {"code", "path", "message"})
                    record_path = Path(scratch) / "record.json"
                    context_path = Path(scratch) / "context.json"
                    record_path.write_text(json.dumps(record), encoding="utf-8")
                    context_path.write_text(json.dumps(context), encoding="utf-8")
                    observed = subprocess.run([sys.executable, str(CHECKER), str(record_path),
                                               "--context", str(context_path)], capture_output=True, text=True)
                    self.assertEqual(observed.returncode, 1, observed.stdout + observed.stderr)
                    self.assertTrue(all(code in observed.stdout for code in expected), observed.stdout)
                    self.assertNotIn("Traceback", observed.stderr)

    def test_digest_stable_under_reformatting(self):
        for name, record in self.records.items():
            reordered = json.loads(json.dumps(record, indent=4, ensure_ascii=True),
                                   object_pairs_hook=lambda items: dict(reversed(items)))
            self.assertEqual(canonical_bytes(record), canonical_bytes(reordered))
            self.assertEqual(record_digest(record), self.digests[name])
            independent = json.dumps(reordered, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")
            self.assertEqual(hashlib.sha256(independent).hexdigest(), self.digests[name])
        self.assertIn('“Ready”'.encode("utf-8"), canonical_bytes(self.records["manual.json"]))

    def test_digest_changes_with_fact(self):
        record = self.records["command.json"]
        for field, value in (("timestamp", "2026-09-30T10:00:02Z"), ("outcome", "failed")):
            changed = {**record, field: value}
            self.assertNotEqual(record_digest(record), record_digest(changed))
            self.assertNotEqual(render_record(record), render_record(changed))

    def test_render_deterministic(self):
        for name, record in self.records.items():
            reordered = json.loads(json.dumps(record), object_pairs_hook=lambda pairs: dict(reversed(pairs)))
            self.assertEqual(render_record(record), render_record(reordered))
            observed = subprocess.run([sys.executable, str(CHECKER), str(FIXTURES / name), "--render"],
                                      capture_output=True, text=True)
            self.assertEqual(observed.returncode, 0)
            self.assertEqual(observed.stdout, render_record(record))

    def test_render_contains_facts(self):
        for record in self.records.values():
            rendered = render_record(record)
            self.assertIn(f"{record['id']}@sha256:{record_digest(record)}", rendered)
            for field in ("candidate", "requirements", "assertion", "oracle", "observation", "outcome",
                          "environment", "limitations", "execution"):
                if field in record:
                    self.assertIn(field.title() + ": " + canonical_bytes(record[field]).decode("utf-8"), rendered)

    def test_failed_or_inconclusive_exit_mismatch_allowed(self):
        for outcome in ("failed", "inconclusive"):
            record = copy.deepcopy(self.records["command.json"])
            record["outcome"] = outcome
            record["execution"]["exit_status"] = 1
            # No context: a well-formed referenced observation can describe failure.
            self.assertEqual(verify_record(record), [])

    def test_fail_closed_for_malformed_types(self):
        for value in (None, [], True, "record", 42, {"outcome": []}, {"type": {}}, {"execution": []}):
            self.assertTrue(verify_record(value, self.context))
        for value in (None, [], True, "", {}, {"receipts": 3}):
            if value is not None:
                self.assertTrue(verify_record(self.records["command.json"], value))
        for field in ("assertion", "observation", "outcome", "execution", "contract", "oracle",
                      "requirements", "environment", "timestamp", "artifacts", "limitations"):
            record = {**self.records["command.json"], field: {} if field in ("artifacts", "limitations") else []}
            self.assertTrue(verify_record(record, self.context))
        record = {**self.records["command.json"], "assertion": float("nan")}
        self.assertEqual(verify_record(record)[0]["code"], "INVALID_JSON")


if __name__ == "__main__":
    unittest.main()
