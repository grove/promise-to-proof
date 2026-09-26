# IMPLEMENTED: PR #26 publication handoff instructions

Contract: work/publish-pr-record-handoff.md, v1, SHA-256 656b4db8958e3877a166640adbf37338c6acfee38646e30a5185030855732d5a.
Candidate: snapshot:sha256:55a37b29398c49f1b91ff8672f04d599d8cb0deb4de1c2ba0c4fadd92ca29d01.
Comparison base: 5a98bbcbeed9bbddce40d1b8158e0592bb10d13f.
Existing implementation commit: 78ebc4ea344db271b24355ba0455bbdc1b530fe5. Current main was merged without conflict in this isolated checkout. No implementation corrections were needed; the added canonical contract records the already requested scope.
Implementation context: /root, workspace-write; safe diagnostics in temporary directories. Independent review/proof remain separate.

## Requirement observations

| ID | Implementation and observed check | Gap |
|---|---|---|
| R1 | Local work and durable records requires exact report/evidence/recovery inputs. Preview explains leftover copies and later receipts. Walkthrough: report+evidence+snapshot enter preview; post-publication receipt is explicitly later; temp files and secrets excluded. | None for instruction scope |
| R2 | Finish the local handoff compares paths, bytes, modes and symlink targets and distinguishes same/different/local-only. Fixture confirmed equal, changed bytes, executable mode, changed symlink and absent receipt cases. | None for instruction scope |
| R3 | Follow-up freezes inputs/parent and demands authority, remote parent check, unchanged product and original report bytes, non-force push and readback; keeps PR state/title/body. Head drift and product/report changes fail those conditions. Fixture's two commits changed only .p2p receipt and preserved ancestry and all three product/report files. Ancestry/readback closes receipt without recursive commit. | None for instruction scope |
| R4 | Cleanup requires authority and moves only verified issue-owned untracked copies to recovery storage. Fixture archived only equal file and retained changed, mode, symlink, local-only receipt and unrelated file. Without authority the instructions require exact proposed paths instead of cleanup. | None for instruction scope |
| R5 | Scenarios 13–14 cover copies, receipts, conflicts and human-ready PR. Validator returned Skill is valid. Standalone copy dereferenced protocol exactly, both YAML documents parsed, identity and implicit invocation policy preserved. git diff --check passed. | None for instruction scope |

## Checks and limits

`python3 /private/tmp/p2p-26-fixture.py` passed. Exact script and output are retained under evidence/implementation. The fixture verifies independently chosen filesystem/Git facts, not a runtime implementation of these prose instructions.
`uv run --offline --cache-dir /private/tmp/p2p-skill-validation-cache --with pyyaml --python /opt/homebrew/bin/python3 /Users/grove/.codex/skills/.system/skill-creator/scripts/quick_validate.py <workspace>/skills/productivity/publish-pr` returned Skill is valid.
A scratch shutil.copytree with symlinks=False produced standalone readable protocol bytes equal to docs/acceptance-contract-protocol.md; yaml.safe_load parsed SKILL frontmatter and agents/openai.yaml successfully. These packaging observations establish packaging, not installed agent behavior.
No live GitHub action or operator cleanup was performed as evidence. No universal compliance guarantee is claimed. Instructions and documented cases are the implementation under this agreement.

Next steps:

1. Independent full review and proof of this captured candidate.
