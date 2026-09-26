import hashlib,json,os,pathlib,stat,sys
root=pathlib.Path('/private/var/tmp/p2p-issue33-verifier-8eh45dgs')
result={}
for name in ['second-candidate','second-review-records','repair-scenarios-completed']:
 tree=root/name; entries=[]
 for p in sorted(tree.rglob('*')):
  s=p.lstat(); item={'path':str(p.relative_to(tree)),'mode':stat.S_IMODE(s.st_mode)}
  if p.is_symlink(): item.update(type='symlink',target=os.readlink(p))
  elif p.is_file(): item.update(type='file',sha256=hashlib.sha256(p.read_bytes()).hexdigest())
  elif p.is_dir(): item.update(type='directory')
  else: raise AssertionError(p)
  entries.append(item)
 result[name]=entries
encoded=json.dumps(result,sort_keys=True,separators=(',',':')).encode()
file=pathlib.Path('/private/tmp/p2p-final-review/protected-inventory.json')
if sys.argv[1]=='before': file.write_bytes(encoded)
else: assert file.read_bytes()==encoded
print('protected full inventories',hashlib.sha256(encoded).hexdigest(),[(n,len(e)) for n,e in result.items()])
