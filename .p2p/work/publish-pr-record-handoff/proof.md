# PROVEN: publication records and checkout handoff

Requirements: 5/5
Counterexamples tested: 17 families through independent instruction walkthroughs and applicable filesystem/Git observations.
Contract: `work/publish-pr-record-handoff.md` v1
Contract snapshot: SHA-256 `656b4db8958e3877a166640adbf37338c6acfee38646e30a5185030855732d5a`; exact text retained in `evidence/proof-followup/contract.md`.
Candidate: `snapshot:sha256:4ad7a1d6086cc3032d3b4ad67eba7d129b2398121cefdfeb84f2ae2e374f47de`
Comparison base: `69c02fe5a0e876b104baacca2e4075f801974d40`
Binding input: `docs/acceptance-contract-protocol.md`, SHA-256 `bec3503abc6ebc40356e662ca0b279be73a4da482eb1616a5c5b435509184351`.
Candidate stability: unchanged; complete manifest checked before and after.
Contract stability: unchanged; exact bytes and binding hash checked before and after.
Verification context: independent full `/prove` invocation using `/Users/grove/.agents/skills/prove/SKILL.md` and its linked protocol, 2026-09-26, Darwin arm64 25.6.0, Python 3.14.7, Git 2.54.0. Input candidate, base and records were outside writable roots and treated as read-only. All calls used the default sandbox. No escalation, candidate edit, remote write, delegation, or operator cleanup occurred. Only disposable scratch Git repositories received commits.

## Outcome

The complete skill instructs publication of retrievable records, comparison and reconciliation of leftover copies, separately authorized frozen receipt follow-ups, and reversible cleanup. The scenarios now include the missing preservation and authority boundaries. All five requirements are established for the instruction-and-scenario scope. These findings do not claim universal model compliance, installed-agent behavior, or successful live GitHub execution.

The retained user request and shared protocol agree with v1. There is no parent, prerequisite or unresolved amendment in the provided contract. The request to publish records and clean matching copies does not authorize deleting changed, unrelated, tracked or local-only content. No contract change was needed. The original PR is merged; this candidate is for a new follow-up PR and no new PR was created during proof.

## Requirement verdicts

Evidence paths below are relative to `.p2p/work/publish-pr-record-handoff/`.

| ID | Observation and independent oracle | Evidence reference | Verdict |
|---|---|---|---|
| R1 | Against the retained request and shared protocol, walked a preview containing a report, its evidence and recovery snapshot. Instructions require exact paths and byte identities, exclude temporary/secret content, explain isolated local copies, and identify later receipts as unpublished until a subsequent operation. | `evidence/proof-followup/walkthrough.md`, R1 | proven |
| R2 | Independently chosen equal/changed/mode/symlink/tracked/local-only/unrelated inventory gave the expected three classes. Instructions compare path, bytes, mode and target, reject untracked-only inference and require remaining-record locations. | `evidence/proof-followup/fixture.py`, `fixture.txt`; walkthrough R2/R4 | proven |
| R3 | Walked exact authority, parent equality, unchanged complete product tree and original reports, identity retention, non-force push, remote SHA readback and unchanged ready/title/body requirements. Scratch Git fixture produced one receipt-only child with unchanged product/report bytes. Drift, report edits, product addition, missing authority and force push conflict with explicit preconditions before push; no recursive receipt commit is required. | `evidence/proof-followup/walkthrough.md`, R3; `fixture.py`, `fixture.txt` | proven |
| R4 | Walked with/without cleanup authority using the retained approval and preservation rules as oracle. Only the identical issue-owned untracked copy moved in the disposable exercise; the archived bytes remained recoverable and all six ineligible files stayed unchanged. Final Git status was captured. The skill requires retrievable remote content and recovery location before actual cleanup. | `evidence/proof-followup/walkthrough.md`, R2/R4; `fixture.txt` | proven |
| R5 | Read all scenarios and complete skill; scenarios 13/14 explicitly include mode, symlink, tracked, missing-cleanup-authority and missing-follow-up-authority cases. Packaging validator passed; dereferenced copy has readable regular files, matching protocol and valid YAML metadata. Existing publication authority boundaries remain explicit. | `evidence/proof-followup/walkthrough.md`, R5; `packaging.py`, `packaging.txt` | proven |

## Commands, assertions and actual results

`python3 evidence/proof-followup/identity.py` was run before and after verification against the supplied immutable inputs. Both outputs match exactly. It enumerates every filesystem entry, compares exact bytes, Git modes and symlink targets, recomputes the canonical manifest snapshot hash, validates work-item/binding hashes and base identity, and independently compares base entries with read-only `git ls-tree`/`git cat-file` observations from the supplied repository. The candidate has 109 entries and base 108. Only `checks/publish-pr-scenarios.md` and `work/publish-pr-record-handoff.md` differ from base. Full record hashes also remained unchanged. See `identity-before.txt` and `identity-after.txt`. The captured `candidate.json` manifest remains the recoverable candidate authority; the script's original input paths describe this run and are not a substitute for the durable handoff.

`python3 evidence/proof-followup/fixture.py` passed. Expected classification was equal and tracked = identical; changed, mode and link = differing; receipt = local-only. All seven files initially remained. With simulated cleanup approval, only equal moved into the archive. Its content was recoverable, and changed, mode, link, tracked, receipt and unrelated stayed unchanged. Final status listed only changed, link, mode, receipt and unrelated as untracked. A scratch receipt commit had exactly the expected parent and a one-commit ancestry, changed only `.p2p/publication.md`, and preserved the full product tree and review/proof bytes. The changed-report and product-addition adversarial cases were observable as differences. Scratch repositories were removed afterward; the script and observed output are retained.

`uv run --offline --cache-dir /private/tmp/p2p-skill-validation-cache --with pyyaml --python /opt/homebrew/bin/python3 evidence/proof-followup/packaging.py` passed. It copies the skill with symlinks dereferenced, asserts readable regular files, compares the protocol bytes, parses both YAML documents, checks implicit invocation policy and runs the installed `quick_validate.py`. Output includes `Skill is valid!`. The direct validator invocation against the input skill also exited zero. This establishes packaging only, as required by v1.

The manual walkthrough records seventeen counterexample families and the particular instruction that rejects each. Authority and PR-state conclusions come from independently reading the complete instructions against the contract, not executing a replacement workflow or treating fixture checks as agent enforcement.

## Storage and limits

This read-only stage wrote exact report text to `/private/tmp/p2p-proof26-followup.md` and safe evidence to `/private/tmp/p2p-proof26-followup-evidence/`. The enclosing workflow must save these exact bytes as `proof.md` and `evidence/proof-followup/` under the work-item records, then reread them. Durable storage is pending that step and is not claimed complete here. The report contains the meaningful commands, assertions and observations; scripts and logs provide reproducibility and detail. No implementation-report claim was used as acceptance evidence.

Live GitHub execution, supported CLI installation and agent invocation are outside this contract. The disposable filesystem exercise uses a local Git object as the published-content stand-in; it does not establish remote retrievability or actual PR state. Static obligations for those properties were assessed at the promised instruction seam. Required CI and merge readiness were not assessed.

## Unresolved gaps

None within the v1 instruction-and-scenario scope.

## Repairs needed

None. Any later product or agreement change requires fresh proof and separate review for that candidate.

Next steps:
1. Save and reread this exact report and retained evidence using the enclosing workflow's filesystem helper.
2. Pair it with full matching review for this snapshot against `69c02fe5a0e876b104baacca2e4075f801974d40`. No further proof work is required for this fixed candidate; publication remains a separately authorized step.
