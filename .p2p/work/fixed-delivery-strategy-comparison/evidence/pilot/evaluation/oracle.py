# Evaluation only. Execute only inside an OS sandbox, never in a worker prompt.
import importlib.util
from pathlib import Path
import subprocess
import sys
candidate, task = Path(sys.argv[1]), sys.argv[2]
if task == "greeting":
    result = subprocess.run([sys.executable, "-B", str(candidate / "greet.py")], capture_output=True, timeout=15)
    assert result.returncode == 0, repr(result.stderr)
    assert result.stdout == b"hello\n", repr(result.stdout)
else:
    spec = importlib.util.spec_from_file_location("delivered_report", candidate / "report.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    target = Path("report-output.txt")
    for text in ("hëllo 世界\n", "replacement\n", ""):
        assert module.save_report(target, text) is None, "successful return must be None"
        assert target.read_bytes() == text.encode("utf-8"), "UTF-8 or overwrite mismatch"
    try:
        module.save_report(Path("absent-parent") / "report.txt", "failure")
    except OSError:
        pass
    else:
        raise AssertionError("I/O error was swallowed")
print("public behavior checks passed")
