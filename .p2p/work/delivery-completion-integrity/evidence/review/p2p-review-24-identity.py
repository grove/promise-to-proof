import base64, hashlib, json, os, subprocess
from pathlib import Path
root=Path('/Users/Shared/p2p-issue-24-6krj8of_/round1')
record=json.loads((root/'records/candidate.json').read_text())
base=json.loads((root/'records/base.json').read_text())
canonical=lambda x: json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
sha=lambda x: hashlib.sha256(x).hexdigest()
assert record['key']=='snapshot:sha256:'+sha(canonical(record['manifest']))
for name,manifest in [('candidate',record['manifest']),('base',base)]:
 tree=root/name
 actual={str(p.relative_to(tree)) for p in tree.rglob('*') if p.is_symlink() or p.is_file()}
 assert actual=={e['path'] for e in manifest}
 for e in manifest:
  p=tree/e['path']; mode='120000' if p.is_symlink() else '100755' if p.stat().st_mode&0o111 else '100644'
  assert mode==e['mode'],e['path']
  if p.is_symlink(): assert os.readlink(p)==e['target']
  else: assert p.read_bytes()==base64.b64decode(e['content_base64']),e['path']
 print(name,len(manifest),'inventory, bytes, symlinks and modes verified')
assert sha((root/'candidate'/record['work_item']).read_bytes())==record['work_item_sha256']
for e in record['binding_inputs']:
 assert sha((root/'candidate'/e['path']).read_bytes())==e['sha256']
 print('binding',e['path'],e['sha256'])
repo='/Users/grove/projects/promise-to-proof'
rows=subprocess.check_output(['git','-C',repo,'ls-tree','-rz',record['comparison_base']]).split(b'\0')
expected={e['path']:e for e in base}
seen=set()
for row in filter(None,rows):
 meta,name=row.split(b'\t'); mode,kind,oid=meta.split(); path=name.decode()
 if path.startswith('.p2p/'):continue
 seen.add(path); e=expected[path]
 assert mode.decode()==e['mode']
 data=subprocess.check_output(['git','-C',repo,'cat-file','blob',oid.decode()])
 assert data==(e['target'].encode() if e['type']=='symlink' else base64.b64decode(e['content_base64']))
assert seen==set(expected)
a={e['path']:e for e in record['manifest']};b=expected
print('base matches Git tree',record['comparison_base'])
print('changed paths', sorted(p for p in a.keys()|b.keys() if a.get(p)!=b.get(p)))
print('candidate',record['key']); print('contract',record['work_item_sha256'])
