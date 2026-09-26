# PROVEN: work/capture.md

Requirements: 1/1
Agent context: /root/scenario_child_verification. Review and proof are separate passes in this same context; no independent-context claim.
Contract: work/capture.md v1 sha256:fb7eaa80f5385b531cb598ba642eeb2ede2a32a75ce3faca2bb1c7e92c25877b; exact text recoverable from candidate.json manifest or candidate Git object.
Parent context: work/parent.md v1 sha256:38c29dec4bdd45e3ea03c015e482b509ec72cabb70f59b4a930e30240f7d0ada; specs/registry.md sha256:64f91b9c11cbd07a51679bf23ed50b70201e51622cd38d011ee0f46d936fedb9. Child R1 contributes parent R1. Decomposition: .p2p/work/parent/slicing.md. Parent R3/R4 and whole-parent delivery are outside this child verdict. Exact shared-candidate approval at .p2p/work/parent/shared-candidate-approval.md covers capture plus lookup only; each child has a separate full report. Capture is not integrated in the target.
Candidate: git:ed877ab327a5bda784737c93017a7be40deedaee; recoverable .p2p/work/capture/candidate.json.
Comparison: resolved epic/example at ae9615a7c906aa539ee205c581aeabba9c70b6d1; full product scope, including staged/unstaged/deleted/untracked files outside .p2p. Fixed target equals candidate.json comparison_base and observed remote tip.
Plan: v1 sha256:547bb750f97a1f45b97700d7d234ceeac3b6c740fc7155e37f2738df4b176cec; recoverable exact bytes .p2p/work/capture/evidence/approved-plan.md; source .p2p/work/parent/slicing.md, approval receipts retained with parent records.
Stability: installed helper validate passed before and after behavioral checks, including complete product content, canonical contract and transitive binding hashes. No candidate/ref/contract edits during review or proof.

Verification context: local disposable repository, Python 3, PYTHONDONTWRITEBYTECODE=1, fixture gh only. Review/proof did not change product files.

## Outcome

The complete child outcome is established through its public function using literal contract oracles.

## Requirement verdicts

| ID | Observation and oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | Capture Ada equals literal ada: Ada; empty and mixed ASCII retain original values. | evidence/child-verification-checks.json, commands and output below | proven |

Inherited constraints: source inspection found only pure dictionary/string operations, no network, persistence, or merge. ASCII is the input domain. No prerequisite.
Counterexamples: capture empty and mixed ASCII passed.

## Commands and actual observations

```json
{
  "actor": "/root/scenario_child_verification",
  "cwd": "/private/tmp/p2p-epic-repair-cases/S2-shared/repo",
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
  "cwd": "/private/tmp/p2p-epic-repair-cases/S2-shared/repo",
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

## Unresolved gaps and repairs

None for this child. Parent R1-R4 combined verification and final integration remain outstanding.
Candidate and contract stability: validation succeeded before and after; exact identities unchanged.
Report storage: .p2p/work/capture/proof.md, saved and reread with history.

Next steps:
1. Matching full child review and proof are complete for this exact candidate. Publication remains separately assessed in .p2p/work/lookup/publication.md.
2. Full assembled-parent review and proof remain required before parent completion.
