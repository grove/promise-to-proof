from pathlib import Path
import json,base64,hashlib,os,subprocess
root=Path('/private/var/tmp/p2p-issue33-verifier-8eh45dgs/second-candidate'); rec=root/'records'; c=json.loads((rec/'candidate.json').read_text())
hash=lambda b:hashlib.sha256(b).hexdigest()
for name,m in [('candidate',c['manifest']),('base',json.loads((rec/'comparison-base-manifest.json').read_text()))]:
 t=root/name; paths={str(p.relative_to(t)) for p in t.rglob('*') if p.is_file() or p.is_symlink()}; assert paths=={e['path'] for e in m}
 for e in m:
  p=t/e['path']; assert not e['path'].startswith('.p2p/')
  if e['type']=='symlink': assert p.is_symlink() and os.readlink(p)==e['target']
  else: assert not p.is_symlink() and p.read_bytes()==base64.b64decode(e['content_base64']) and ('100755' if p.stat().st_mode&0o111 else '100644')==e['mode'],e['path']
 print(name,len(m),'all paths, bytes, executable modes and symlinks match',hash(json.dumps(m,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()))
 if name=='candidate':assert c['key']=='snapshot:sha256:'+hash(json.dumps(m,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())
 else:
  out=subprocess.check_output(['git','ls-tree','-rz',c['comparison_base']],cwd='/Users/grove/projects/promise-to-proof2')
  git_entries={}
  for line in out.split(b'\0'):
   if not line:continue
   fields,path=line.split(b'\t');mode,typ,obj=fields.decode().split(); path=path.decode()
   if path.startswith('.p2p/'):continue
   git_entries[path]=(mode,obj)
  assert set(git_entries)=={e['path'] for e in m}
  for e in m:
   mode,obj=git_entries[e['path']];assert mode==e['mode']; actual=subprocess.check_output(['git','cat-file','blob',obj],cwd='/Users/grove/projects/promise-to-proof2');assert actual==(e['target'].encode() if e['type']=='symlink' else base64.b64decode(e['content_base64']))
  print('base matches full Git object',c['comparison_base'])
for e in [{'path':c['work_item'],'sha256':c['work_item_sha256']}]+c['binding_inputs']:
 actual=hash((root/'candidate'/e['path']).read_bytes());assert actual==e['sha256'];print(e['path'],actual)
p=root/'candidate/docs/acceptance-contract-protocol.md'; copies=list((root/'candidate/skills').rglob('acceptance-contract-protocol.md'));assert all(q.read_bytes()==p.read_bytes() for q in copies);print('protocol',len(copies),hash(p.read_bytes()))
r=Path('/private/var/tmp/p2p-issue33-verifier-8eh45dgs/second-proof-records');n=0
for f in (r/'evidence').rglob('retention.json'):
 d=json.loads(f.read_text())
 for e in d.get('files',[]):
  saved=e['saved'];target=r/saved.split('.p2p/work/epic-delivery-strategy/',1)[1] if '.p2p/work/epic-delivery-strategy/' in saved else f.parent/saved
  assert target.is_file(),(f,target)
  assert hash(target.read_bytes())==e['sha256'],target
  n+=1
print('retention hashes',n,'PASS')
