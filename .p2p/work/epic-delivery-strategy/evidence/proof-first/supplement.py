from pathlib import Path
import hashlib,json,re
r=Path('/private/var/tmp/p2p-issue33-verifier-8eh45dgs/supplement-first')
count=0
for d in r.iterdir():
 if not d.is_dir():continue
 for e in json.loads((d/'retention.json').read_text())['files']:
  p=r/e['saved'].split('/supplement-first/',1)[1]
  assert hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256'],str(p);count+=1
print('Supplement retained files exact hashes:',count)
for case in ['S9-default','S9-stale-plan','S9-concurrent-body','S9-after-effect']:
 d=r/case;events=[json.loads(x) for x in (d/'calls.jsonl').read_text().splitlines()];effects=[e for e in events if e['effect']];state=json.loads((d/'tracker.json').read_text());print(case,'effects',len(effects),'final base',state['prs']['17']['baseRefName'])
 if case=='S9-default':
  assert len(effects)==1 and effects[0]['effect']=={'changes':{'baseRefName':'epic/example'},'edit':'17'}
  assert effects[0]['exit_code']==1
  preview=json.loads((d/'repo/.p2p/work/lookup/evidence/retarget-preview.json').read_text())
  assert state['prs']['17']['body']==preview['pr_before']['body']
  assert len(state['prs'])==1
  assert any(e['sequence']>effects[0]['sequence'] and e['argv'][:2]==['pr','view'] and e['result'].get('baseRefName')=='epic/example' for e in events)
  print('Exact one base edit persisted despite exit 1; body preserved; successful subsequent readback; no duplicate')
 else:assert not effects
for case,slug in [('S9-default','lookup'),('S12-default','parent')]:
 d=r/case;data=(d/'repo/.p2p/work/parent/slicing.md').read_bytes()
 sec=re.findall(rb'^## Approved delivery plan\r?\n.*?(?=^## |\Z)',data,re.M|re.S);assert len(sec)==1
 exact=hashlib.sha256(sec[0]).hexdigest();normalized=hashlib.sha256(sec[0].rstrip()+b'\n').hexdigest()
 report=(d/'repo/.p2p/work'/slug/('merge-readiness.md' if slug=='lookup' else 'publication.md')).read_text()
 assert normalized in report and exact not in report
 print('COUNTEREXAMPLE',case,'exact',exact,'reported',normalized)
