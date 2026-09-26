from pathlib import Path
import json,hashlib,subprocess,re,os,importlib.util
r=Path('/private/var/tmp/p2p-issue33-verifier-8eh45dgs/second-proof-records/evidence'); f=Path('/private/var/tmp/p2p-issue33-verifier-8eh45dgs/repair-final-supplement'); scratch=Path('/private/tmp/p2p-final-proof');py='/opt/homebrew/bin/python3.14'
h=lambda b:hashlib.sha256(b).hexdigest();total=0
for d in f.iterdir():
 if not d.is_dir():continue
 for e in json.loads((d/'retention.json').read_text())['files']:
  p=d/e['saved'].split('/'+d.name+'/',1)[1];assert p.exists(),p;assert h(p.read_bytes())==e['sha256'],p;total+=1
print('final retention',total,'file hashes verified')
for name in ['S9-post-effect','S9-interrupted']:
 d=f/name;calls=[json.loads(x) for x in (d/'calls.jsonl').read_text().splitlines()];edits=[x for x in calls if x.get('effect')];assert len(edits)==1 and edits[0]['sequence']==4;assert edits[0]['effect']=={'changes':{'baseRefName':'epic/example'},'edit':'17'}
 before=calls[0]['result'];after=calls[-1]['result'];assert before['baseRefName']=='trunk' and after['baseRefName']=='epic/example';assert {k:v for k,v in before.items() if k!='baseRefName'}=={k:v for k,v in after.items() if k!='baseRefName'}
 t=json.loads((d/'tracker.json').read_text());assert len(t['prs'])==1
 plan=(d/'resume-approved-plan.md').read_bytes(); assert h(plan) in (d/'resume-actor-report.md').read_text()
 if name=='S9-post-effect':
  assert edits[0]['injection_phase']=='after_persisted_edit';assert b'Plan revision: v2' in plan;assert b'| work/lookup.md | independent | trunk |' in plan;assert (d/'resume-actor-report.md').read_text().startswith('# BLOCKED')
 else: assert b'Plan revision: v1' in plan and (d/'resume-actor-report.md').read_text().startswith('# PUBLISHED')
 print(name,'one exact base edit; all human/identity fields retained; fresh resume zero effects; plan',h(plan))
for name,source,commit,expected in [('S11',f/'S11-parent-only','2a7733c6ac449ab6203d856f090c2e67173daace',1),('S12',r/'scenarios/S12-default','159b5f50400479e1e5429b26b6c75e6d5f45682f',0)]:
 out=scratch/name
 bundle=source/('retained-fixture.bundle' if name=='S11' else 'fixture.bundle')
 subprocess.run(['git','clone','-q',str(bundle),str(out)],check=True);subprocess.run(['git','checkout','-q','--detach',commit],cwd=out,check=True)
 for case in ['capture','lookup','summary','parent']:
  p=subprocess.run([py,'-B','check.py',case],cwd=out,text=True,capture_output=True);assert p.returncode==(expected if case=='parent' else 0),(name,case,p.stderr);print(name,commit,case,'exit',p.returncode,p.stdout.strip())
 spec=importlib.util.spec_from_file_location(name,out/'registry.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 assert mod.capture('Ada')=={'ada':'Ada'};assert mod.lookup({'ada':'Ada'},'ADA')=='Ada';assert mod.lookup({},'Ada') is None;assert mod.summary('Ada')=='Welcome Ada';assert mod.summary(mod.lookup(mod.capture('Ada'),'ADA'))=='Welcome Ada'
 if name=='S11':assert mod.greet('Ada')=='Welcome ADA';print('S11 independent child literal oracles pass; greet Ada -> Welcome ADA violates parent-only R4')
print('behavior assertions PASS')
