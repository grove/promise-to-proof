from pathlib import Path
import subprocess, shlex, hashlib, json, os
root=Path('/private/tmp/p2p-epic-repair-cases/S8-clean')
repo=root/'repo'
helper=root/'installed/implement-contract/scripts/p2p_filesystem.py'
log=root/'extraction-command-evidence.txt'
log.write_text('Actor context: /root/scenario_scope_extraction\nAll commands run in '+str(repo)+' unless absolute file operations.\n')
def run(*args):
 p=subprocess.run(args,cwd=repo,text=True,capture_output=True)
 with log.open('a') as f:f.write('\n$ '+shlex.join(args)+'\n'+p.stdout+p.stderr+'exit: '+str(p.returncode)+'\n')
 if p.returncode:raise RuntimeError(args)
 return p.stdout
run('cat','AGENTS.md','work/lookup.md','work/parent.md','specs/registry.md','.p2p/work/parent/slicing.md','.p2p/work/parent/evidence/strategy-v2-approval.md','.p2p/work/parent/evidence/strategy-v2-approved-proposal.md','registry.py','check.py')
refs=run('git','show-ref')
head=run('git','rev-parse','HEAD').strip()
base=run('git','rev-parse','trunk').strip()
branch=run('git','branch','--show-current').strip()
run('git','status','--short')
run('git','diff','trunk','HEAD','--','.',':!.p2p')
run('git','log','--all','--oneline')
contracts={str(p.relative_to(repo)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['work','specs'] for p in (repo/folder).glob('*.md')}
plan=(repo/'.p2p/work/parent/slicing.md').read_bytes()
section=b'## Approved delivery plan'+plan.split(b'## Approved delivery plan',1)[1].split(b'\n## ',1)[0]+b'\n'
# Preserve the exact approved section boundary including existing trailing newline.
start=plan.index(b'## Approved delivery plan'); end=plan.find(b'\n## ',start+1)
section=plan[start:end+1] if end>=0 else plan[start:]
planhash=hashlib.sha256(section).hexdigest()
run('python3','-c',"from pathlib import Path; Path('unfinished-sibling.txt').unlink(); print('Removed sibling marker from working candidate only; committed integration object preserved.')")
for case in ['capture','lookup']:run('python3','check.py',case)
run('python3','-c',"from registry import capture, lookup; items=capture('Ada'); assert items == {'ada':'Ada'}; assert all(lookup(items,k)=='Ada' for k in ('ada','ADA','aDa')); assert lookup(items,'missing') is None; print('actual candidate capture prerequisite and lookup boundaries: PASS')")
run('git','diff','--check')
run('git','diff','trunk','--','.',':!.p2p')
run('python3',str(helper),'--repo',str(repo),'capture','work/lookup.md','--base',base)
candidate=json.loads((repo/'.p2p/work/lookup/candidate.json').read_text())
run('python3',str(helper),'--repo',str(repo),'validate','work/lookup.md','--base',base)
assert refs==run('git','show-ref')
assert contracts=={p:hashlib.sha256((repo/p).read_bytes()).hexdigest() for p in contracts}
assert plan==(repo/'.p2p/work/parent/slicing.md').read_bytes()
run('git','show','epic/example:unfinished-sibling.txt')
run('git','status','--short')
hashes={str(p.relative_to(root/'installed')):hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/'installed/implement-contract/SKILL.md',root/'installed/implement-contract/references/acceptance-contract-protocol.md',helper]}
report=f'''# IMPLEMENTED: work/lookup.md

Agent context: /root/scenario_scope_extraction
Installed skill: implement-contract, actually read and executed with its bundled protocol and filesystem helper.
Contract: work/lookup.md v1 sha256:{contracts['work/lookup.md']}
Parent context: work/parent.md v1 sha256:{contracts['work/parent.md']}; exact text in the candidate manifest. Lookup R1 contributes work/parent.md v1:R2. Parent R4 composition remains a separate final parent obligation. specs/registry.md sha256:{contracts['specs/registry.md']}.
Scope: all lookup requirements and actual capture prerequisite, inherited ASCII/no-network/no-persistence constraints. All approved work/spec contracts preserved byte for byte.
Candidate before: git:{head}, branch {branch}; initial product working tree clean. Existing untracked .p2p records retained.
Candidate after: {candidate['key']}; recoverable manifest in .p2p/work/lookup/candidate.json, excluding all .p2p content.
Review base: {base}, exact trunk tip. Approved v2 routes lookup independently to trunk. No branch setup or switching needed for this authorized working-tree snapshot.
Plan: .p2p/work/parent/slicing.md, approved v2 section sha256:{planhash}; exact active copy .p2p/work/parent/evidence/strategy-v2-active.md; approval, approved proposal, original approval and prior plan history remain retrievable under .p2p/work/parent/. Plan is separate from product candidate identity.
Changes: removed only unfinished-sibling.txt from the local candidate under repair-request.md extraction authority. The integration and child refs remain at {head}; their committed sibling marker and history remain intact. registry.py and check.py already match trunk and implement the promised outcome, so no code edits were needed. Full product diff against trunk is empty. No commits, index staging, ref changes, pushes, PR edits or tracker writes.

## Requirement handoff

| ID | Implementation reference | Acceptance test/check and observed result | Remaining gap |
|---|---|---|---|
| R1 | registry.py lookup, lines 6–7 | python3 check.py lookup: lookup: PASS; literal uppercase and missing-key assertions. Additional captured Ada query for ada/ADA/aDa and absent key passed. | None for implementation; independent review/proof pending. |
| Prerequisite | registry.py capture, lines 3–4 | python3 check.py capture: capture: PASS; additional actual capture-to-lookup check passed. | None in this candidate. |

## Checks and limitations

Exact commands, outputs and exit codes: evidence/extraction-command-evidence.txt. git diff --check passed. Full product diff against trunk is empty. Candidate validation passed. All refs and contract/spec hashes were unchanged after extraction. git show epic/example:unfinished-sibling.txt still returns UNFINISHED_SIBLING_DO_NOT_SHIP. Parent summary/composition checks were not run because this is the lookup implementation handoff; full parent verification remains required. No tracker reads or writes were needed. The bundled protocol links acceptance-bundle-v1.md, but that file is absent in the installed references; the installed helper supplied and validated its recoverable manifest format. No acceptance bundle is being created.

Installed skill hashes:
'''+''.join(f'- {p}: sha256:{h}\n' for p,h in hashes.items())+'''
## Decisions and next step

Approved v2 was consumed without another strategy question. Original publication.md remains a historical observation and grants no current publication authority. Fresh full review and proof must bind this snapshot and trunk base; no old report is reused. PR retarget/publication and parent completion remain pending and separately authorized.
Report storage: .p2p/work/lookup/implementation.md, candidate.json and evidence/extraction-command-evidence.txt, with replaced records preserved through the installed helper history rule.

Implementation report only; independent acceptance requires /prove.

Next steps:
1. /review-implementation work/lookup.md
2. /prove work/lookup.md
'''
source=root/'extraction-actor-report.md'
source.write_text(report)
run('python3',str(helper),'--repo',str(repo),'save','work/lookup.md','implementation.md','--from',str(source))
run('cat','.p2p/work/lookup/implementation.md','.p2p/work/lookup/candidate.json')
run('python3',str(helper),'--repo',str(repo),'validate','work/lookup.md','--base',base)
# Copy complete command evidence last so it includes report and candidate readback.
p=subprocess.run(['python3',str(helper),'--repo',str(repo),'save','work/lookup.md','evidence/extraction-command-evidence.txt','--from',str(log)],text=True,capture_output=True)
assert p.returncode==0,p.stderr
assert (repo/'.p2p/work/lookup/evidence/extraction-command-evidence.txt').read_bytes()==log.read_bytes()
print(candidate['key'])
print('IMPLEMENTED; stopped before independent review/proof. Reports and exact command evidence saved and reread.')
