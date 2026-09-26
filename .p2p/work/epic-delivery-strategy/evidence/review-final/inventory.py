import base64,hashlib,json,os,pathlib,stat
root=pathlib.Path('/private/var/tmp/p2p-issue33-verifier-8eh45dgs/second-candidate')
record=json.loads((root/'records/candidate.json').read_text())
basefile=root/'records/comparison-base-manifest.json'
b=json.loads(basefile.read_text()); print('base keys', list(b) if isinstance(b,dict) else 'list')
def inspect(name,manifest):
 tree=root/name
 actual=sorted(str(p.relative_to(tree)) for p in tree.rglob('*') if not p.is_dir() or p.is_symlink())
 assert actual==sorted(e['path'] for e in manifest)
 for e in manifest:
  p=tree/e['path']; s=p.lstat()
  if e['type']=='file':
   assert stat.S_ISREG(s.st_mode); assert p.read_bytes()==base64.b64decode(e['content_base64'])
   assert ('100755' if s.st_mode&0o111 else '100644')==e['mode']
  else: assert p.is_symlink() and os.readlink(p)==e['target']
 digest=hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
 print(name,len(actual),digest)
inspect('candidate',record['manifest']); inspect('base',b['manifest'] if isinstance(b,dict) else b)
for p,w in [(record['work_item'],record['work_item_sha256'])]+[(e['path'],e['sha256']) for e in record['binding_inputs']]:
 assert hashlib.sha256((root/'candidate'/p).read_bytes()).hexdigest()==w; print(p,w)
protocol=(root/'candidate/docs/acceptance-contract-protocol.md').read_bytes()
copies=list((root/'candidate/skills').glob('*/**/references/acceptance-contract-protocol.md'))
assert all(p.read_bytes()==protocol for p in copies)
print('protocol',len(copies),hashlib.sha256(protocol).hexdigest())
