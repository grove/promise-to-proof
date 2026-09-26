import pathlib,json,hashlib,base64,os,stat,subprocess,sys
root=pathlib.Path('/Users/Shared/p2p-issue-24-6krj8of_/round1'); meta=json.loads((root/'records/candidate.json').read_text())
canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
hash=lambda b:hashlib.sha256(b).hexdigest()
def verify(tree,manifest):
 actual={str(p.relative_to(tree)) for p in tree.rglob('*') if p.is_symlink() or p.is_file()}
 assert actual=={e['path'] for e in manifest}, (actual ^ {e['path'] for e in manifest})
 for e in manifest:
  p=tree/e['path']; mode='120000' if p.is_symlink() else '100755' if p.stat().st_mode & 0o111 else '100644'
  assert mode==e['mode'], e['path']
  if e['type']=='symlink': assert os.readlink(p)==e['target']
  else: assert p.read_bytes()==base64.b64decode(e['content_base64']),e['path']
 return len(actual)
assert meta['key']=='snapshot:sha256:'+hash(canon(meta['manifest']))
result={'candidate':meta['key'],'candidate_entries':verify(root/'candidate',meta['manifest']),'base_entries':verify(root/'base',json.loads((root/'records/base.json').read_text())),'comparison_base':meta['comparison_base']}
for e in [{'path':meta['work_item'],'sha256':meta['work_item_sha256']}]+meta['binding_inputs']:
 assert hash((root/'candidate'/e['path']).read_bytes())==e['sha256'];result[e['path']]=e['sha256']
base=meta['comparison_base']; entries=json.loads((root/'records/base.json').read_text()); gitlist=subprocess.check_output(['git','ls-tree','-r',base],cwd='/Users/grove/projects/promise-to-proof',text=True).splitlines(); gitmap={l.split('\t')[1]:l.split('\t')[0].split() for l in gitlist if not l.split('\t')[1].startswith('.p2p/')}; assert set(gitmap)=={e['path'] for e in entries}
for e in entries:
 mode,typ,obj=gitmap[e['path']]; assert mode==e['mode']; b=subprocess.check_output(['git','cat-file','blob',obj],cwd='/Users/grove/projects/promise-to-proof'); assert b==(e['target'].encode() if e['type']=='symlink' else base64.b64decode(e['content_base64']))
result['base_manifest_sha256']=hash(canon(entries)); result['status']='PASS'; print(json.dumps(result,indent=2))
