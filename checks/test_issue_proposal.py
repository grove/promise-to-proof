"""Offline checks for human-first issue acceptance rendering."""
import base64, hashlib, importlib.util, pathlib, sys, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/productivity/plan-acceptance/scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("proposal", SCRIPTS / "render_issue_proposal.py")
proposal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proposal)
WORK = ".p2p/work/demo/contract.md"
CONTRACT = """# Acceptance contract: demo

Contract revision: v1
Intended outcome: Save the report.

## Acceptance matrix

| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | source A | Save bytes | Keep permissions | save() | Exact contents | Read file | planned |
| R2 | source B | Raise error | Never create directories | save() | Original error | Denied path test | planned |

## Unresolved gaps

- None

## Open questions

- None

## Out of scope

- Remote uploads
"""
class IssueProposalTests(unittest.TestCase):
    def test_readable_and_recoverable(self):
        data = b"source without final newline"
        record = {"path": "source.md", "sha256": hashlib.sha256(data).hexdigest(), "base64": base64.b64encode(data).decode()}
        body = proposal.render(WORK, CONTRACT.encode(), [record])
        visible = body.split("<details>")[0]
        for value in ("R1", "R2", "Keep permissions", "Denied path test", "Remote uploads", "I approve contract v1"):
            self.assertIn(value, visible)
        self.assertEqual(proposal.recovery(body)[WORK], CONTRACT.encode())
        self.assertEqual(proposal.recovery(body)["source.md"], data)
        self.assertEqual(proposal.render(WORK, CONTRACT.encode(), [record]), body)
        with self.assertRaisesRegex(ValueError, "visible promises differ"):
            proposal.recovery(body.replace("Keep permissions", "Drop permissions", 1))
    def test_blocked_for_gap(self):
        raw = CONTRACT.replace("Read file | planned", "Read file | gap")
        text = proposal.render(WORK, raw.encode(), [])
        self.assertIn("Not ready for approval", text)
        self.assertNotIn("I approve contract", text)
    def test_rejects_missing_requirement_evidence(self):
        raw = CONTRACT.replace("Denied path test", "")
        with self.assertRaisesRegex(ValueError, "incomplete requirement"):
            proposal.render(WORK, raw.encode(), [])
if __name__ == "__main__": unittest.main()
