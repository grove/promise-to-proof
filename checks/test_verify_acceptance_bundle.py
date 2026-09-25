import copy
import json
import unittest
from pathlib import Path

from verify_acceptance_bundle import verify_bundle


FIXTURES = Path(__file__).parent / "fixtures" / "acceptance-bundle-v1"


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


class AcceptanceBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.valid = json.loads((FIXTURES / "valid.json").read_text(encoding="utf-8"))
        cls.invalid_cases = json.loads((FIXTURES / "invalid-cases.json").read_text(encoding="utf-8"))

    def test_valid_bundle(self):
        self.assertEqual(verify_bundle(self.valid), [])

    def test_seeded_invalid_bundles(self):
        for case in self.invalid_cases:
            with self.subTest(case=case["name"]):
                bundle = merge_patch(self.valid, case["patch"])
                codes = {issue["code"] for issue in verify_bundle(bundle)}
                self.assertTrue(set(case["expected_codes"]).issubset(codes), codes)


if __name__ == "__main__":
    unittest.main()