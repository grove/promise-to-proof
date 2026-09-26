import pathlib,json
p=pathlib.Path('/private/tmp/p2p-proof-24-evidence')
s=json.loads((p/'summary.json').read_text()); assert s['result']=='PASS' and len(s['runs'])==43
for r in s['runs']:
 n=r['kind']+'-'+r['name']
 if r['kind']=='baseline':
  assert r['max_actions_observed']<64; print(n,r['nodes'],r['max_actions_observed']); continue
 t=json.loads((p/n/'trace.json').read_text()); f=t[-1]['Node']['state']; actions=[x['Name'] for x in t]
 if r['kind']=='witness' and f['outcome']=='complete':
  assert f['stages']==[2,2] and f['passed']==[True,True] and f['reports']==f['evidence']==[3,3]
  assert all(b[:2]==[f['contract'],f['candidate']] for b in f['bindings'])
  assert f['bindings'][0][2]==f['base'] and f['bindings'][0][3]!=f['bindings'][1][3]
  if r['name'] in ['repair','restart']:
   repair=max(i for i,x in enumerate(actions) if x=='Repair')
   assert actions[repair+1:].count('Launch')==2 and actions[repair+1:].count('Return')==2
  if r['name']=='initial': assert f['repairs_actual']==0 and not f['restarted']
 if r['name']=='repair-reset':
  assert f['repairs_actual']==2
  positions=[i for i,a in enumerate(actions) if a=='Repair']; restart=actions.index('Restart'); assert positions[0]<restart<positions[1]
 print(n,'property='+r['property'],'actions='+','.join(actions),'final='+json.dumps(f,sort_keys=True))
print('ALL OBSERVED TRACES AUDITED')
