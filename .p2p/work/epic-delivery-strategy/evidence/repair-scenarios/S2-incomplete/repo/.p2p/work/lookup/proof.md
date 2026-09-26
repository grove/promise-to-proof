# NOT PROVEN: work/lookup.md

Requirements: 0/1
Agent context: /root/scenario_child_verification. Review and proof are separate passes in this same context; no independent-context claim.
Contract: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9; exact text recoverable from candidate.json manifest or candidate Git object.
Parent context: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada; specs/registry.md sha256:64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9. Child R1 contributes parent R2. Decomposition: .p2p/work/parent/slicing.md. Parent R3/R4 and whole-parent delivery are outside this child verdict. Exact shared-candidate approval at .p2p/work/parent/shared-candidate-approval.md covers capture plus lookup only; each child has a separate full report. Capture is not integrated in the target.
Candidate: git:194af4c2baba22b019b76bb36be64bf7c3b1b589; recoverable .p2p/work/lookup/candidate.json.
Comparison: resolved epic/example at 66a04c3617995cce9bf4cbd282e28d8f09cfd906; full product scope, including staged/unstaged/deleted/untracked files outside .p2p. Fixed target equals candidate.json comparison_base and observed remote tip.
Plan: v1 sha256:a7f70fc11fc26bd176526c63c3fd344a62da1d15dfcb14e05b0992c3ff6eeeb9; recoverable exact bytes .p2p/work/lookup/evidence/approved-plan.md; source .p2p/work/parent/slicing.md, approval receipts retained with parent records.
Stability: installed helper validate passed before and after behavioral checks, including complete product content, canonical contract and transitive binding hashes. No candidate/ref/contract edits during review or proof.

Verification context: local disposable repository, Python 3, PYTHONDONTWRITEBYTECODE=1, fixture gh only. Review/proof did not change product files.

## Outcome

The promised lookup outcome is disproven by NotImplementedError. A shared-candidate exception does not permit incomplete child behavior.

## Requirement verdicts

| ID | Observation and oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | Captured Ada lookup raises at registry.py:7 instead of returning literal Ada. | evidence/child-verification-checks.json, commands and output below | disproven |

Inherited constraints: source inspection found only pure dictionary/string operations, no network, persistence, or merge. ASCII is the input domain. Capture prerequisite passes, independently of the lookup failure.
Counterexamples: Lookup experiment stops at the first demonstrated failure; later cases not claimed as exercised.

## Commands and actual observations

```json
{
  "actor": "/root/scenario_child_verification",
  "cwd": "/private/tmp/p2p-epic-repair-cases/S2-incomplete/repo",
  "argv": [
    "python3",
    "check.py",
    "capture"
  ],
  "stdout": "capture: PASS\n",
  "stderr": "",
  "returncode": 0
}
```
```json
{
  "actor": "/root/scenario_child_verification",
  "cwd": "/private/tmp/p2p-epic-repair-cases/S2-incomplete/repo",
  "argv": [
    "python3",
    "check.py",
    "lookup"
  ],
  "stdout": "",
  "stderr": "Traceback (most recent call last):\n  File \"/private/tmp/p2p-epic-repair-cases/S2-incomplete/repo/check.py\", line 7, in <module>\n    assert lookup({'ada': 'Ada'}, 'ADA') == 'Ada'\n           ~~~~~~^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/private/tmp/p2p-epic-repair-cases/S2-incomplete/repo/registry.py\", line 7, in lookup\n    raise NotImplementedError(\"lookup unfinished\")\nNotImplementedError: lookup unfinished\n",
  "returncode": 1
}
```
```json
{
  "actor": "/root/scenario_child_verification",
  "cwd": "/private/tmp/p2p-epic-repair-cases/S2-incomplete/repo",
  "argv": [
    "python3",
    "-c",
    "from registry import capture; assert capture('Ada') == {'ada':'Ada'}; assert capture('') == {'':''}; assert capture('xY-19') == {'xy-19':'xY-19'}; print('capture original/empty/ASCII: PASS')"
  ],
  "stdout": "capture original/empty/ASCII: PASS\n",
  "stderr": "",
  "returncode": 0
}
```
```json
{
  "actor": "/root/scenario_child_verification",
  "cwd": "/private/tmp/p2p-epic-repair-cases/S2-incomplete/repo",
  "argv": [
    "python3",
    "-c",
    "from registry import capture,lookup; items=capture('Ada'); assert all(lookup(items,k)=='Ada' for k in ['ada','ADA','aDa']); assert lookup({},'ADA') is None; assert lookup(items,'missing') is None; assert lookup(capture(''),'')==''; multi=dict(items,bob='Bob'); before=multi.copy(); assert lookup(multi,'BOB')=='Bob'; assert multi==before; print('lookup actual capture/mixed/missing/empty/many/no mutation: PASS')"
  ],
  "stdout": "",
  "stderr": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\n    from registry import capture,lookup; items=capture('Ada'); assert all(lookup(items,k)=='Ada' for k in ['ada','ADA','aDa']); assert lookup({},'ADA') is None; assert lookup(items,'missing') is None; assert lookup(capture(''),'')==''; multi=dict(items,bob='Bob'); before=multi.copy(); assert lookup(multi,'BOB')=='Bob'; assert multi==before; print('lookup actual capture/mixed/missing/empty/many/no mutation: PASS')\n                                                                      ^^^\n  File \"<string>\", line 1, in <genexpr>\n    from registry import capture,lookup; items=capture('Ada'); assert all(lookup(items,k)=='Ada' for k in ['ada','ADA','aDa']); assert lookup({},'ADA') is None; assert lookup(items,'missing') is None; assert lookup(capture(''),'')==''; multi=dict(items,bob='Bob'); before=multi.copy(); assert lookup(multi,'BOB')=='Bob'; assert multi==before; print('lookup actual capture/mixed/missing/empty/many/no mutation: PASS')\n                                                                          ~~~~~~^^^^^^^^^\n  File \"/private/tmp/p2p-epic-repair-cases/S2-incomplete/repo/registry.py\", line 7, in lookup\n    raise NotImplementedError(\"lookup unfinished\")\nNotImplementedError: lookup unfinished\n",
  "returncode": 1
}
```

## Unresolved gaps and repairs

R1: implement registry.lookup, preserving case-insensitive capture lookup and None for missing keys. No repair performed.
Candidate and contract stability: validation succeeded before and after; exact identities unchanged.
Report storage: .p2p/work/lookup/proof.md, saved and reread with history.

Next steps:
1. /repair-gaps .p2p/work/lookup/proof.md under explicit repair authority; then capture the changed candidate and refresh full review and proof.
2. Full assembled-parent review and proof remain required before parent completion.
