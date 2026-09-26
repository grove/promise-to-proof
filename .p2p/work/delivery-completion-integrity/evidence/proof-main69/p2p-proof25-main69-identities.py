import base64,hashlib,json,os,stat,subprocess
from pathlib import Path
root=Path('/Users/Shared/p2p-issue-24-6krj8of_/refresh25-main69'); meta=json.loads((root/'records/candidate.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
for name,manifest in [('candidate',meta['manifest']),('base',json.loads((root/'records/base.json').read_text()))]:
 actual=[]
 for parent,ds,fs in os.walk(root/name,followlinks=False):
  for f in fs+ [d for d in ds if (Path(parent)/d).is_symlink()]:
   p=Path(parent)/f; rel=p.relative_to(root/name).as_posix(); s=p.lstat()
   if stat.S_ISLNK(s.st_mode): e=dict(path=rel,type='symlink',mode='120000',target=os.readlink(p))
   else: e=dict(path=rel,type='file',mode='100755' if s.st_mode & 0o111 else '100644',content_base64=base64.b64encode(p.read_bytes()).decode())
   actual.append(e)
 actual.sort(key=lambda e:e['path']);assert actual==manifest,name
 print(name,len(actual),'full inventory bytes/modes/symlinks match')
 if name=='base':
  entries=subprocess.check_output(['git','ls-tree','-r',meta['comparison_base']],cwd='/var/folders/vq/593qxcm57l90w1dlpywl_7nw0000gn/T/p2p-refresh-25-ktwpyoq5/repo').decode().splitlines()
  gitpaths=[]
  for line in entries:
   h,path=line.split('\t'); mode,typ,obj=h.split()
   if path.startswith('.p2p/'):continue
   gitpaths.append(path); e=next(x for x in actual if x['path']==path);assert mode==e['mode'];b=subprocess.check_output(['git','cat-file','blob',obj],cwd='/var/folders/vq/593qxcm57l90w1dlpywl_7nw0000gn/T/p2p-refresh-25-ktwpyoq5/repo');assert b==(e['target'].encode() if typ=='blob' and mode=='120000' else base64.b64decode(e['content_base64']))
  assert sorted(gitpaths)==[e['path'] for e in actual];print('base full tree verified against git:'+meta['comparison_base'])
key='snapshot:sha256:'+sha(json.dumps(meta['manifest'],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode());assert key==meta['key'];print(key)
for i in [dict(path=meta['work_item'],sha256=meta['work_item_sha256'])]+meta['binding_inputs']:
 assert sha((root/'candidate'/i['path']).read_bytes())==i['sha256'];print(i['path'],i['sha256'])
for p in sorted((root/'records').iterdir()):print('record',p.name,sha(p.read_bytes()))
