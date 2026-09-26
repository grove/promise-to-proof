import json,hashlib,base64,os,pathlib,sys
root=pathlib.Path('/Users/Shared/p2p-issue-24-6krj8of_/refresh25-main69')
results={}
for name in ['candidate','base']:
 d=json.loads((root/'records'/f'{name}.json').read_text())
 if isinstance(d,list): d={'manifest':d}
 m=d['manifest']
 h=hashlib.sha256(json.dumps(sorted(m,key=lambda e:e['path']),sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
 assert d.get('key','snapshot:sha256:'+h)=='snapshot:sha256:'+h
 d['key']='snapshot:sha256:'+h
 actual={str(p.relative_to(root/name)) for p in (root/name).rglob('*') if not p.is_dir()}
 assert actual=={e['path'] for e in m},(actual-{e['path'] for e in m})
 for e in m:
  p=root/name/e['path']
  if e['type']=='file':
   assert not p.is_symlink() and p.read_bytes()==base64.b64decode(e['content_base64']),e['path']
   assert ('100755' if p.stat().st_mode&0o111 else '100644')==e['mode'],e['path']
  else: assert p.is_symlink() and os.readlink(p)==e['target'] and e['mode']=='120000'
 bindings={}
 for e in d.get('binding_inputs',[])+([{'path':d['work_item'],'sha256':d['work_item_sha256']}] if 'work_item' in d else []):
  actual_hash=hashlib.sha256((root/name/e['path']).read_bytes()).hexdigest();assert actual_hash==e['sha256'];bindings[e['path']]=actual_hash
 results[name]={'key':d['key'],'paths':len(m),'comparison_base':d.get('comparison_base'),'bindings':bindings}
a=json.loads((root/'records/candidate.json').read_text());b={'manifest':json.loads((root/'records/base.json').read_text())}
assert a['comparison_base']=='69c02fe5a0e876b104baacca2e4075f801974d40'
aa={e['path']:e for e in a['manifest']};bb={e['path']:e for e in b['manifest']}
results['changed']=[p for p in sorted(aa.keys()|bb.keys()) if aa.get(p)!=bb.get(p)]
print(json.dumps(results,indent=2))
