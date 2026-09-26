import pathlib,json,hashlib,re,subprocess,os
r=pathlib.Path('/private/var/tmp/p2p-issue33-verifier-8eh45dgs/repair-final-supplement'); count=0
for record in r.glob('*/retention.json'):
 d=json.loads(record.read_text())
 for e in d['files']:
  suffix=e['saved'].split('/repair-scenarios/',1)[1]
  assert hashlib.sha256((r/suffix).read_bytes()).hexdigest()==e['sha256']; count+=1
print('final retention entries verified',count)
for name in ['S9-post-effect','S9-interrupted']:
 c=r/name; events=[json.loads(x) for x in (c/'calls.jsonl').read_text().splitlines()]; effects=[e for e in events if e.get('effect')]
 assert len(effects)==1 and effects[0]['effect']=={'edit':'17','changes':{'baseRefName':'epic/example'}}
 assert any(e['sequence']>effects[0]['sequence'] and e['argv'][:2]==['pr','view'] for e in events)
 if name=='S9-post-effect': assert effects[0]['injection_phase']=='after_persisted_edit'
 oracle=json.loads((c/'oracle.json').read_text()); actual=json.loads((c/'tracker.json').read_text())['prs']; assert list(actual)==['17']
 for field in ['title','body','headRefOid','isDraft']: assert actual['17'][field]==oracle['pr_before'][field]
 section=re.findall(rb'^## Approved delivery plan\r?\n.*?(?=^## |\Z)',(c/'repo/.p2p/work/parent/slicing.md').read_bytes(),re.M|re.S)[0]
 assert section==(c/'repo/.p2p/work/lookup/evidence/resume-approved-plan.md').read_bytes()
 report=(c/'repo/.p2p/work/lookup/publication.md').read_text(); assert hashlib.sha256(section).hexdigest() in report
 print(name,'one base-only effect, later readback, preserved PR fields, exact plan',hashlib.sha256(section).hexdigest())
c=r/'S11-parent-only'; repo=c/'repo'
for child in ['capture','lookup','summary']:
 p=repo/'.p2p/work'/child/'proof.md'; assert p.read_text().startswith('# PROVEN:')
 result=subprocess.run(['/opt/homebrew/bin/python3.14','check.py',child],cwd=repo,capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
 assert result.returncode==0; print(child,result.stdout.strip())
result=subprocess.run(['/opt/homebrew/bin/python3.14','check.py','parent'],cwd=repo,capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
assert result.returncode==1; print('parent exit',result.returncode, result.stderr)
assert (repo/'.p2p/work/parent/proof.md').read_text().startswith('# NOT PROVEN:')
for report in ['publication.md','merge-readiness.md']: assert (repo/'.p2p/work/parent'/report).read_text().startswith('# BLOCKED:')
assert not any(json.loads(e).get('effect') for e in (c/'calls.jsonl').read_text().splitlines())
print('S11 actual checks, child/parent report separation and zero-effects gates match')
