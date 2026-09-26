import json,re
from pathlib import Path
p=Path('/private/tmp/p2p-proof25-refresh-evidence')
s=json.loads((p/'summary.json').read_text());assert s['result']=='PASS' and len(s['runs'])==43
original=Path('/Users/Shared/p2p-issue-24-6krj8of_/refresh25/candidate/checks/delivery-model/delivery.fizz').read_text()
normalize=lambda x:re.sub(r'^(SCENARIO|MUTATION|WITNESS) = .*$',r'\1 = "ignored"',x,flags=re.M)
for run in s['runs']:
 d=p/(run['kind']+'-'+run['name']);assert normalize((d/'model.fizz').read_text())==normalize(original)
 if run['kind']=='baseline':
  assert run['max_actions_observed']<64
  continue
 t=json.loads((d/'trace.json').read_text());v=t[-1]['Node']['state'];n=run['name']
 if run['kind']=='witness':
  expected={'initial':'complete','repair':'complete','restart':'complete','exhausted':'repair-exhausted'}.get(n,n);assert v['outcome']==expected
  if expected=='complete':
   assert v['reports']==v['evidence']==[3,3] and all(v['passed']) and v['stages']==[2,2]
   assert all(b[:2]==[v['contract'],v['candidate']] for b in v['bindings']) and v['bindings'][0][2]==v['base']
  if n in ['repair','restart']:
   pos=next(i for i,x in enumerate(t) if x['Name']=='Repair');assert t[pos]['Node']['state']['bindings']==[[],[]]
   assert sum(x['Name']=='Launch' for x in t[pos+1:])==2 and sum(x['Name']=='Return' for x in t[pos+1:])==2
  if n=='exhausted':assert v['repair_used']==v['repairs_actual']==1 and v['restarted']
 else:
  if n=='repair-reset':assert v['repairs_actual']==2 and v['restarted']
  else:
   assert v['outcome']=='complete'
   if n=='identity':assert v['bindings'][0][:2]!=v['bindings'][1][:2]
   elif n=='text':assert v['revision']=='v1' and any(b[0]!=v['contract'] for b in v['bindings'])
   elif n=='candidate':assert all(b[1]!=v['candidate'] for b in v['bindings'])
   elif n=='base':assert v['bindings'][0][2]!=v['base']
   else:
    artifact,suffix=n.split('-');state={'absent':0,'save':1,'read':2,'lost':4,'access':5}[suffix];assert state in v['reports' if artifact=='report' else 'evidence']
 print(d.name,run.get('property'),v['outcome'])
print('PASS: independent terminal-state audit; successful repair resets and reruns both stages; all retained models change only scenario/mutation/witness constants')
