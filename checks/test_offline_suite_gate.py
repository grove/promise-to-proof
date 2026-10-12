"""Offline gate self-tests."""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest

import run_offline_suite as gate


class OfflineGateTests(unittest.TestCase):
    def fixture(self, files):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            for name, source in files.items():
                (directory / name).write_text(source)
            report = directory / "summary.md"
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
                status = gate.run_suite(directory, stream=stream, summary_path=report)
            return status, stream.getvalue(), report.read_text()

    def test_new_failing_test_fails_gate(self):
        status, output, report = self.fixture({
            "test_new.py": "import unittest\nclass New(unittest.TestCase):\n    def test_failure(self):\n        self.fail('injected regression')\n"})
        self.assertEqual(status, 1)
        self.assertIn("injected regression", output)
        self.assertIn("**FAIL**", report)

    def test_empty_test_file_fails_gate(self):
        status, output, report = self.fixture({
            "test_empty.py": "# no collected tests\n",
            "test_valid.py": "import unittest\nclass Valid(unittest.TestCase):\n    def test_ok(self):\n        pass\n"})
        self.assertEqual(status, 1)
        self.assertIn("Not collected: test_empty", output)
        self.assertIn("test_empty.py", report)

    def test_passing_test_passes_gate(self):
        status, output, report = self.fixture({
            "test_passing.py": "import unittest\nclass Passing(unittest.TestCase):\n    def test_ok(self):\n        pass\n"})
        self.assertEqual(status, 0)
        self.assertIn("Offline suite PASS", output)
        self.assertIn("**PASS**", report)
