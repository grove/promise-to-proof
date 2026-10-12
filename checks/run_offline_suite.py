#!/usr/bin/env python3
"""Run the documented default offline unittest discovery with a complete-file gate.

The fixture suite does not launch Codex, call a model, or claim live-host evidence.
"""

import os
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATTERN = "test_*.py"


def cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases(item)
        else:
            yield item


def run_suite(directory, *, stream=None, summary_path=None):
    """Return nonzero on test failures, import errors, or incomplete discovery."""
    if sys.version_info < (3, 11):
        print(f"Python 3.11+ required; found {sys.version.split()[0]}", file=sys.stderr)
        return 1

    directory = Path(directory).resolve()
    expected = {path.stem for path in directory.glob(PATTERN) if path.is_file()}
    if not expected:
        print(f"Offline suite FAILED: no {PATTERN} files in {directory}", file=sys.stderr)
        return 1

    # Same discovery as the documented python3 -m unittest command.
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(directory), pattern=PATTERN)
    collected = suite.countTestCases()
    modules = {test.__class__.__module__.rsplit(".", 1)[-1] for test in cases(suite)}
    missing = sorted(expected - modules)
    print(f"Offline discovery: {len(expected)} files; {len(expected) - len(missing)} files collected; "
          f"{collected} test cases", flush=True)
    if missing:
        print("Not collected: " + ", ".join(missing), file=sys.stderr, flush=True)

    start = time.monotonic()
    result = unittest.TextTestRunner(verbosity=2, stream=stream).run(suite)
    duration = time.monotonic() - start
    passed = result.wasSuccessful() and not missing and result.testsRun == collected
    status = "PASS" if passed else "FAIL"
    details = (f"Offline suite {status}: {result.testsRun}/{collected} tests executed; "
               f"{len(result.failures)} failures, {len(result.errors)} errors, "
               f"{len(result.skipped)} skipped; {duration:.1f}s")
    print(details, flush=True)

    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as report:
            report.write("## Complete offline regression suite (not live evidence)\n\n")
            report.write(f"**{status}** — {len(expected)} test files, "
                         f"{len(expected) - len(missing)} collected; "
                         f"{result.testsRun}/{collected} tests executed; "
                         f"{len(result.failures)} failures, {len(result.errors)} errors, "
                         f"{len(result.skipped)} skipped; {duration:.1f}s.\n\n")
            if missing:
                report.write("Uncollected files: " + ", ".join(f"{name}.py" for name in missing) + "\n\n")
            report.write("Discovery: python3 -m unittest discover -s checks -p 'test_*.py'. "
                         "See job logs for individual cases and failure tracebacks.\n")

    return 0 if passed else 1


if __name__ == "__main__":
    # Running directly excludes the repo root from sys.path; match module discover.
    sys.path.insert(0, str(ROOT))
    sys.exit(run_suite(ROOT / "checks", summary_path=os.environ.get("GITHUB_STEP_SUMMARY")))
