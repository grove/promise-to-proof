import pathlib,json,base64,hashlib,os
root=pathlib.Path('/private/var/tmp/p2p-issue33-verifier-8eh45dgs')
records=root/'first-proof-records'; c=json.loads((records/'candidate.json').read_text())
def digest(x):return hashlib.sha256(x).hexdigest()
def verify(name,manifest):
 tree=root/'first-candidate'/name
 actual={str(p.relative_to(tree)) for p in tree.rglob('*') if p.is_symlink() or p.is_file()}
 assert actual=={e['path'] for e in manifest},(actual ^ {e['path'] for e in manifest})
 for e in manifest:
  p=tree/e['path']
  if e['type']=='symlink':
   assert p.is_symlink() and os.readlink(p)==e['target'],e
  else:
   assert not p.is_symlink() and p.read_bytes()==base64.b64decode(e['content_base64']),e['path']
   assert ('100755' if p.stat().st_mode & 0o111 else '100644')==e['mode'],e['path']
 print(name,len(manifest),'complete paths/bytes/modes/symlinks PASS')
verify('candidate',c['manifest'])
verify('base',json.loads((records/'evidence/comparison-base-manifest.json').read_text()))
h=digest(json.dumps(c['manifest'],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()); assert c['key']=='snapshot:sha256:'+h;print(c['key'])
for e in [{'path':c['work_item'],'sha256':c['work_item_sha256']}]+c['binding_inputs']:
 h=digest((root/'first-candidate/candidate'/e['path']).read_bytes());assert h==e['sha256'];print(e['path'],h)
protocol=root/'first-candidate/candidate/docs/acceptance-contract-protocol.md'
copies=list((root/'first-candidate/candidate/skills').rglob('acceptance-contract-protocol.md'))
assert all(x.read_bytes()==protocol.read_bytes() for x in copies)
print('protocol copies',len(copies),'all match',digest(protocol.read_bytes()))
