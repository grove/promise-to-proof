import importlib.util,pathlib,tempfile,json,subprocess,base64,platform
root=pathlib.Path('/Users/Shared/p2p-issue-24-6krj8of_/refresh25-main69')
evidence=pathlib.Path('/private/tmp/p2p-review25-main69-evidence')
base=json.loads((root/'records/base.json').read_text())
entries={e['path']:e for e in base}
raw=subprocess.check_output(['git','-C','/var/folders/vq/593qxcm57l90w1dlpywl_7nw0000gn/T/p2p-refresh-25-ktwpyoq5/repo','ls-tree','-rz','--full-tree','69c02fe5a0e876b104baacca2e4075f801974d40'])
seen=set()
for row in raw.split(b'\0'):
 if not row:continue
 attrs,p=row.split(b'\t');mode,typ,obj=attrs.decode().split();p=p.decode()
 if p=='.p2p' or p.startswith('.p2p/'):continue
 seen.add(p);e=entries[p];assert e['mode']==mode
 blob=subprocess.check_output(['git','-C','/var/folders/vq/593qxcm57l90w1dlpywl_7nw0000gn/T/p2p-refresh-25-ktwpyoq5/repo','cat-file','blob',obj.decode() if isinstance(obj,bytes) else obj])
 assert blob==(e['target'].encode() if e['type']=='symlink' else base64.b64decode(e['content_base64'])),p
assert seen==set(entries)
print('Base full Git tree matched:',len(seen),'paths')
spec=importlib.util.spec_from_file_location('reviewed_check',root/'candidate/checks/delivery-model/check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
fizz=pathlib.Path('/private/tmp/p2p-fizzbee-24/fizzbee-v0.5.3-macos_arm/fizz')
for relative,h in m.PIN.items():assert m.digest(fizz.parent/relative)==h
runs=[]
with tempfile.TemporaryDirectory(prefix='p2p-review25-') as tmp:
 for kind,name,scenario,mutation,witness in [('witness','restart','repair','none','restart'),('mutation','repair-reset','exhausted','repair-reset','none'),('mutation','evidence-absent','initial','evidence-absent','none'),('mutation','text','text','text','none')]:
  runs.append(m.run(fizz,evidence,pathlib.Path(tmp),kind,name,scenario,mutation,witness))
(evidence/'diagnostics.json').write_text(json.dumps({'environment':platform.platform(),'python':platform.python_version(),'runs':runs},indent=2)+'\n')
