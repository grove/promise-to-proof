# PROVEN: work/lookup.md

Requirements: 1/1
Agent context: /root/scenario_child_verification. Review and proof are separate passes in this same context; no independent-context claim.
Contract: work/lookup.md v1 sha256:fae82a64da6322f136f724c54d4d8377332d3a632a9444a58d229e2758a8d0d9; exact text recoverable from candidate.json manifest or candidate Git object.
Parent context: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada; specs/registry.md sha256:64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9. Child R1 contributes parent R2. Decomposition: .p2p/work/parent/slicing.md. Parent R3/R4 and whole-parent delivery are outside this child verdict. Capture already exists at the target; candidate adds no prerequisite payload.
Candidate: git:6200ab72615e708585b48bcf3cbb7f9c45d3573e; recoverable .p2p/work/lookup/candidate.json.
Comparison: resolved epic/example at c74003fe4a40add496b1888ded0706494f49a47d; full product scope, including staged/unstaged/deleted/untracked files outside .p2p. Fixed target equals candidate.json comparison_base and observed remote tip.
Plan: v1 sha256:f97a0dda89221fcb76d436094a5cccc88b931ba77c0b8da35c2efaec49e6f304; recoverable exact bytes .p2p/work/lookup/evidence/approved-plan.md; source .p2p/work/parent/slicing.md, approval receipts retained with parent records.
Stability: installed helper validate passed before and after behavioral checks, including complete product content, canonical contract and transitive binding hashes. No candidate/ref/contract edits during review or proof.

Verification context: local disposable repository, Python 3, PYTHONDONTWRITEBYTECODE=1, fixture gh only. Review/proof did not change product files.

## Outcome

The complete child outcome is established through its public function using literal contract oracles.

## Requirement verdicts

| ID | Observation and oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | Actual captured Ada is returned for ada/ADA/aDa; missing keys give None; empty and multi-name cases pass without mutation. | evidence/child-verification-checks.json, commands and output below | proven |

Inherited constraints: source inspection found only pure dictionary/string operations, no network, persistence, or merge. ASCII is the input domain. Capture prerequisite passes, independently of the lookup failure.
Counterexamples: lookup missing, empty, mixed-case, multiple entries and mutation checks passed.

## Commands and actual observations

```json
{
  "actor": "/root/scenario_child_verification",
  "cwd": "/private/tmp/p2p-epic-repair-cases/S3-publication/repo",
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
  "cwd": "/private/tmp/p2p-epic-repair-cases/S3-publication/repo",
  "argv": [
    "python3",
    "check.py",
    "lookup"
  ],
  "stdout": "lookup: PASS\n",
  "stderr": "",
  "returncode": 0
}
```
```json
{
  "actor": "/root/scenario_child_verification",
  "cwd": "/private/tmp/p2p-epic-repair-cases/S3-publication/repo",
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
  "cwd": "/private/tmp/p2p-epic-repair-cases/S3-publication/repo",
  "argv": [
    "python3",
    "-c",
    "from registry import capture,lookup; items=capture('Ada'); assert all(lookup(items,k)=='Ada' for k in ['ada','ADA','aDa']); assert lookup({},'ADA') is None; assert lookup(items,'missing') is None; assert lookup(capture(''),'')==''; multi=dict(items,bob='Bob'); before=multi.copy(); assert lookup(multi,'BOB')=='Bob'; assert multi==before; print('lookup actual capture/mixed/missing/empty/many/no mutation: PASS')"
  ],
  "stdout": "lookup actual capture/mixed/missing/empty/many/no mutation: PASS\n",
  "stderr": "",
  "returncode": 0
}
```

## Unresolved gaps and repairs

None for this child. Parent R1-R4 combined verification and final integration remain outstanding.
Candidate and contract stability: validation succeeded before and after; exact identities unchanged.
Report storage: .p2p/work/lookup/proof.md, saved and reread with history.

Next steps:
1. Matching full child review and proof are complete for this exact candidate. Publication remains separately assessed in .p2p/work/lookup/publication.md.
2. Full assembled-parent review and proof remain required before parent completion.
