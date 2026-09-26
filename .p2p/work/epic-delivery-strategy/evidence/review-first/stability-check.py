import base64,hashlib,json,os
from pathlib import Path
p=Path('/private/var/tmp/p2p-issue33-verifier-8eh45dgs/first-candidate')
c=json.loads((p/'records/candidate.json').read_text()); b=json.loads((p/'records/evidence/comparison-base-manifest.json').read_text())
result={}
for name,entries in [('candidate',c['manifest']),('base',b)]:
 root=p/name
 actual={str(f.relative_to(root)) for f in root.rglob('*') if f.is_file() or f.is_symlink()}
 assert actual=={e['path'] for e in entries}
 for e in entries:
  f=root/e['path']; symlink=f.is_symlink()
  assert e['type']==('symlink' if symlink else 'file')
  assert e['mode']==('120000' if symlink else '100755' if f.stat().st_mode&0o111 else '100644')
  data=os.readlink(f).encode() if symlink else f.read_bytes()
  assert data==(e['target'].encode() if symlink else base64.b64decode(e['content_base64'],validate=True))
 result[name+'_manifest']={'entries':len(entries),'complete_inventory_bytes_modes_symlinks':'unchanged'}
sha=lambda data:hashlib.sha256(data).hexdigest()
assert c['key']=='snapshot:sha256:'+sha(json.dumps(c['manifest'],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())
for e in [{'path':c['work_item'],'sha256':c['work_item_sha256']}]+c['binding_inputs']:
 assert sha((p/'candidate'/e['path']).read_bytes())==e['sha256']
initial=json.loads(Path('/private/tmp/p2p-review-epic-delivery/initial-identities.json').read_text())
assert initial=={'candidate':c['key'],'base':c['comparison_base'],'contract':c['work_item_sha256'],'binding_inputs':c['binding_inputs']}
canonical=(p/'candidate/docs/acceptance-contract-protocol.md').read_bytes()
links=list((p/'candidate/skills').glob('**/references/acceptance-contract-protocol.md'))
assert len(links)==17
assert all(link.read_bytes()==canonical for link in links)
result.update(initial)
result['protocol_copies']={'count':len(links),'sha256':sha(canonical),'all_match':True}
result['base_manifest_record_sha256']=sha((p/'records/evidence/comparison-base-manifest.json').read_bytes())
print(json.dumps(result,indent=2))
