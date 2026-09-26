import os,json,hashlib,base64,subprocess,sys
from pathlib import Path
root=Path('/Users/Shared/p2p-issue-24-6krj8of_/followup26-main69')
repo='/var/folders/vq/593qxcm57l90w1dlpywl_7nw0000gn/T/p2p-scenario-followup-pmmvcei_/repo'
d=json.loads((root/'records/candidate.json').read_bytes()); b=json.loads((root/'records/base.json').read_bytes())
def sha(x):return hashlib.sha256(x).hexdigest()
def content(e):return e['target'].encode() if e['type']=='symlink' else base64.b64decode(e['content_base64'],validate=True)
def check_tree(name,entries):
 tree=root/name
 actual=set()
 for p,ds,fs in os.walk(tree,followlinks=False):
  for n in ds[:]:
   if (Path(p)/n).is_symlink():fs.append(n);ds.remove(n)
  for n in fs:actual.add(str((Path(p)/n).relative_to(tree)))
 assert actual=={e['path'] for e in entries}, (name,'paths mismatch')
 for e in entries:
  p=tree/e['path'];sy=p.is_symlink(); mode='120000' if sy else '100755' if p.stat().st_mode&0o111 else '100644'
  assert mode==e['mode'],(name,e['path'],'mode')
  assert (os.readlink(p).encode() if sy else p.read_bytes())==content(e),(name,e['path'],'bytes')
 print(name,'full paths, bytes, modes, symlinks match',len(entries))
check_tree('candidate',d['manifest']);check_tree('base',b)
key='snapshot:sha256:'+sha(json.dumps(d['manifest'],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())
assert key==d['key']=='snapshot:sha256:4ad7a1d6086cc3032d3b4ad67eba7d129b2398121cefdfeb84f2ae2e374f47de'
assert d['comparison_base']=='69c02fe5a0e876b104baacca2e4075f801974d40'
assert sha((root/'candidate'/d['work_item']).read_bytes())==d['work_item_sha256']=='656b4db8958e3877a166640adbf37338c6acfee38646e30a5185030855732d5a'
for e in d['binding_inputs']:assert sha((root/'candidate'/e['path']).read_bytes())==e['sha256']
raw=subprocess.check_output(['git','-C',repo,'ls-tree','-rz',d['comparison_base']]);objects={}
for r in raw.split(b'\0'):
 if not r:continue
 meta,path=r.split(b'\t',1);mode,kind,oid=meta.decode().split();path=path.decode()
 if path.startswith('.p2p/'):continue
 objects[path]=(mode,oid)
assert set(objects)=={e['path'] for e in b}
for e in b:
 mode,oid=objects[e['path']];assert mode==e['mode'];assert subprocess.check_output(['git','-C',repo,'cat-file','blob',oid])==content(e)
print('base manifest matches actual Git tree outside .p2p; object',d['comparison_base'])
print('candidate',key,'contract',d['work_item_sha256'],'bindings',d['binding_inputs'])
old={e['path']:e for e in b};new={e['path']:e for e in d['manifest']}
print('changed product paths',[p for p in sorted(old.keys()|new.keys()) if old.get(p)!=new.get(p)])
print('record hashes',{p.name:sha(p.read_bytes()) for p in sorted((root/'records').iterdir())})
