# CHANGES NEEDED: work/publish-pr-record-handoff.md

Contract: work/publish-pr-record-handoff.md v1, SHA-256 656b4db8958e3877a166640adbf37338c6acfee38646e30a5185030855732d5a.
Candidate: snapshot:sha256:55a37b29398c49f1b91ff8672f04d599d8cb0deb4de1c2ba0c4fadd92ca29d01. Recoverable manifest: candidate.json supplied in /Users/Shared/p2p-issue-24-6krj8of_/refresh26/records; candidate tree: sibling candidate directory.
Comparison: 5a98bbcbeed9bbddce40d1b8158e0592bb10d13f, verified against its Git object and retained base manifest/tree. Scope includes all 109 candidate manifest entries, the entire diff, and R1–R5. No parent or prerequisite is declared.
Binding input: docs/acceptance-contract-protocol.md, SHA-256 bec3503abc6ebc40356e662ca0b279be73a4da482eb1616a5c5b435509184351.
Invocation: /root/review26, installed /Users/grove/.agents/skills/review-implementation/SKILL.md. Read-only review; diagnostics and report written only under /private/tmp. No delegation or escalation.
Stability: before/after manifest inventory, bytes, executable modes and symlink targets matched. Snapshot key, contract, binding hashes and base identity matched throughout.

## Contract fidelity

F1. R5 requires documented reproducible scenarios including the conflicting cases in R1–R4, but the reconciliation scenario does not supply the mode-only, symlink-only, tracked-copy or absent-cleanup-authority cases. Location: checks/publish-pr-scenarios.md:170–182. Its complete input contains untracked copies, one changed local file, a later receipt and one unrelated file. Its cleanup pass condition only addresses cleanup with authority. Scenario 14 at lines 184–195 likewise supplies an authorized records follow-up and head/report/product conflicts, but no missing follow-up-authority variant.

These omissions matter because R2 expressly distinguishes mode and symlink differences, R4 excludes tracked files and cleanup inferred from publication, and R3 requires separate follow-up authority. Running the written scenarios can satisfy all their pass conditions while those specific protections remain unexamined. Scenario 3 tests modes/symlinks during initial commit reconstruction, and scenarios 1/6 test initial publication authority; neither exercises the new reconciliation/cleanup or records-only exception. This is a missing part of the promised scenario documentation, not a demand for universal model compliance or a new controller.

Smallest correction: extend scenarios 13 and 14 with these concrete variants and their expected no-move/no-publication outcomes. Retain the current successful cases and instruction boundaries. No contract change is needed.

Coverage:

| Requirement | Inspection |
|---|---|
| R1 | Skill requires all referenced reports/evidence/recovery inputs with exact paths and byte identities, excludes temporary files/secrets, explains unchanged local copies and later receipts. No material instruction defect found. |
| R2 | Handoff explicitly compares path, bytes, mode and symlink target and classifies equal/differing/local-only records. Report requires remaining locations. Instruction is complete; missing scenario variants are F1. |
| R3 | Read the complete initial-publication and separate follow-up flow. Follow-up freezes parent/paths/bytes/message/destination/head; requires separate explicit authority and matching remote parent; preserves complete product tree, original review/proof, original mapping and PR content/state; non-force push/readback and ancestry avoid recursive receipts. Existing global identity rechecks remain applicable. No material instruction defect found; scenario authority omission is F1. |
| R4 | Cleanup exception is explicitly separately authorized; only issue-owned untracked copies confirmed remotely may move, with local recovery and status reporting. Differing/local-only/unrelated files remain. No material instruction defect found; missing negative variants are F1. |
| R5 | Read all 14 scenarios, full skill diff and packaging metadata; packaging checks passed. Scenarios honestly label themselves human-runnable scenarios rather than run results. Coverage defect F1 remains. |

## Scope and simplicity

No material findings. The diff changes the publish-pr skill, its scenarios and the canonical contract only. It adds no workflow controller, dependency, product functionality or remote operation.

## Engineering quality

F1 is also an evidence-coverage concern. Otherwise no material findings. The separate follow-up exception does not authorize product/report edits or force push. Cleanup has an explicit exception to the operator-checkout preservation rule and does not override preservation or authority requirements. Stale evidence cannot be made current by an artifact commit: the shared protocol and skill require complete product equality, current work-item/binding/base identity and unchanged relevant execution inputs. Review/proof remain attached to the original candidate.

## Checks and limitations

Inspected the entire diff, full publish-pr skill, all scenarios, full canonical contract, shared protocol and installed review protocol, tracker/domain instructions and YAML metadata. The two protocol copies are byte-identical. No CONTEXT.md or ADR files were present. Implementation.md was read only as a handoff/navigation record; its reported checks were not used as correctness evidence.

Ran `python3 /private/tmp/p2p-review26-evidence/identity.py` before and after review. Both returned: `PASS candidate entries 109 base entries 108 base Git object matches, candidate key, work item and all binding hashes match`. The script checks exact inventory including extra paths, bytes, mode and symlink targets, recalculates the canonical manifest digest, validates the agreement and all bindings, and compares the full retained base with `git ls-tree`/`git cat-file` on the named base object. Retained scripts and output accompany this report.

Ran the installed validator with `uv run --offline --cache-dir /private/tmp/p2p-skill-validation-cache --with pyyaml --python /opt/homebrew/bin/python3 /Users/grove/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/Shared/p2p-issue-24-6krj8of_/refresh26/candidate/skills/productivity/publish-pr`. Actual result: `Skill is valid!`, exit 0. An initial attempt with a fresh private cache failed because offline PyYAML was absent; the existing scratch cache supplied it without network access.

Ran `uv run --offline --cache-dir /private/tmp/p2p-skill-validation-cache --with pyyaml --python /opt/homebrew/bin/python3 /private/tmp/p2p-review26-evidence/packaging.py`. Actual result: `PASS standalone dereferenced protocol, regular readable files, frontmatter and agent YAML parse, implicit invocation true`, exit 0. The scratch copy's protocol matched the candidate shared protocol byte-for-byte.

These observations establish instruction/scenario review and packaging, not installed-agent compliance or GitHub behavior. No live publication, operator cleanup, or exhaustive acceptance proof was performed. The requested review scope is complete, with F1 remaining.

## Handoff

F1 is an in-scope R5 correction with R2/R3/R4 boundary coverage. Return it to an authorized implement-contract invocation. Do not modify a verdict to accept the unchanged candidate.
Report storage: exact report saved and reread at /private/tmp/p2p-review26.md; evidence at /private/tmp/p2p-review26-evidence. Durable storage pending enclosing workflow save and reread at .p2p/work/publish-pr-record-handoff/review.md and evidence/review, preserving prior runs. Temporary candidate paths require the retained candidate.json and base objects for transfer.

Review only; acceptance proof and merge readiness are separate.

## Next steps

1. `/implement-contract work/publish-pr-record-handoff.md; findings .p2p/work/publish-pr-record-handoff/review.md` to add the missing scenario variants from F1.
2. Capture the changed candidate and rerun full `/review-implementation work/publish-pr-record-handoff.md` and `/prove work/publish-pr-record-handoff.md` against that exact candidate and comparison base.
