import base64,hashlib,json,os,stat,subprocess
from pathlib import Path
r=Path('/Users/Shared/p2p-issue-24-6krj8of_/refresh26')
def sha(b): return hashlib.sha256(b).hexdigest()
def verify(root,manifest):
 expected={x['path']:x for x in manifest}; actual={}
 for p,ds,fs in os.walk(root,followlinks=False):
  for n in list(ds):
   q=Path(p)/n
   if q.is_symlink(): fs.append(n);ds.remove(n)
  for n in fs:
   q=Path(p)/n;actual[q.relative_to(root).as_posix()]=q
 assert actual.keys()==expected.keys(), (actual.keys()-expected.keys(),expected.keys()-actual.keys())
 for rel,e in expected.items():
  q=actual[rel];st=q.lstat()
  mode='120000' if stat.S_ISLNK(st.st_mode) else '100755' if st.st_mode&0o111 else '100644'
  assert mode==e['mode'],rel
  if mode=='120000': assert os.readlink(q)==e['target'],rel
  else: assert q.read_bytes()==base64.b64decode(e['content_base64']),rel
 return len(expected)
d=json.loads((r/'records/candidate.json').read_bytes());m=d['manifest']
assert 'snapshot:sha256:'+sha(json.dumps(m,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())==d['key']
assert d['key']=='snapshot:sha256:55a37b29398c49f1b91ff8672f04d599d8cb0deb4de1c2ba0c4fadd92ca29d01'
assert sha((r/'candidate'/d['work_item']).read_bytes())==d['work_item_sha256']=='656b4db8958e3877a166640adbf37338c6acfee38646e30a5185030855732d5a'
for e in d['binding_inputs']: assert sha((r/'candidate'/e['path']).read_bytes())==e['sha256']
b=json.loads((r/'records/base.json').read_bytes())
assert d['comparison_base']=='5a98bbcbeed9bbddce40d1b8158e0592bb10d13f'
# Compare retained base manifest with actual Git object, not only metadata.
raw=subprocess.check_output(['git','ls-tree','-rz',d['comparison_base']],cwd='/Users/grove/projects/promise-to-proof')
gitentries={}
for entry in raw.split(b'\0'):
 if not entry:continue
 meta,path=entry.split(b'\t');mode,kind,oid=meta.decode().split();name=path.decode()
 if name=='.p2p' or name.startswith('.p2p/'):continue
 content=subprocess.check_output(['git','cat-file','blob',oid],cwd='/Users/grove/projects/promise-to-proof')
 e={'path':name,'mode':mode,'type':'symlink' if mode=='120000' else 'file'}
 if mode=='120000': e['target']=content.decode()
 else:e['content_base64']=base64.b64encode(content).decode()
 gitentries[name]=e
assert gitentries=={e['path']:e for e in b}
print('PASS candidate entries',verify(r/'candidate',m),'base entries',verify(r/'base',b),'base Git object matches, candidate key, work item and all binding hashes match')
