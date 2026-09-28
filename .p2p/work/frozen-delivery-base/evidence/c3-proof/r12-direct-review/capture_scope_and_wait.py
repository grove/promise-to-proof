#!/usr/bin/env python3
import base64,hashlib,json,os,pathlib,subprocess,sys,time
control=pathlib.Path(sys.argv[1]); expected=sys.argv[2]; target_b=sys.argv[3]; target_d=sys.argv[4]; repo=pathlib.Path.cwd()
def git(*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
def sha(b):return hashlib.sha256(b).hexdigest()
d=json.loads((control/'candidate-scope.json').read_text()); manifest=d['manifest']
assert d['key']==expected
key='snapshot:sha256:'+sha(json.dumps(sorted(manifest,key=lambda e:e['path']),sort_keys=True,ensure_ascii=False,separators=(',',':')).encode());assert key==expected
actual={}
for p in repo.rglob('*'):
 rel=p.relative_to(repo).as_posix()
 if rel=='.git' or rel.startswith('.git/') or rel=='.p2p' or rel.startswith('.p2p/'):continue
 if p.is_dir() and not p.is_symlink():continue
 mode='120000' if p.is_symlink() else ('100755' if p.stat().st_mode&0o111 else '100644')
 actual[rel]=(mode,os.readlink(p) if p.is_symlink() else base64.b64encode(p.read_bytes()).decode())
expected_entries={e['path']:(e['mode'],e.get('target') if e['type']=='symlink' else e['content_base64']) for e in manifest}
assert actual==expected_entries, 'C3 product tree mismatch'
contract=repo/'work/frozen-delivery-base.md';source=repo/'plans/frozen-delivery-under-moving-targets.md';receipt=repo/'.p2p/work/frozen-delivery-base/planning-handoff.md'
assert sha(contract.read_bytes())==d['work_item_sha256'];assert sha(source.read_bytes())==d['binding_inputs'][0]['sha256']
assert sha(receipt.read_bytes())=='2d9c7618c2f9b7a8dcac1469004a55f9346a14256b7a80a8b86f48b278c16571'
head=git('rev-parse','HEAD');tip=git('rev-parse','refs/heads/main')
record={'candidate':expected,'contract_sha256':sha(contract.read_bytes()),'source_sha256':sha(source.read_bytes()),'head_at_scope_capture':head,'intended_target':'main','comparison_scope_captured':tip,'target_B_expected':target_b,'target_D_expected':target_d,'planning_handoff_sha256':sha(receipt.read_bytes()),'candidate_json_absent':not (repo/'.p2p/work/frozen-delivery-base/candidate.json').exists(),'delivery_record_absent':not (repo/'.p2p/work/frozen-delivery-base/delivery.json').exists(),'implementation_handoff_absent':not (repo/'.p2p/work/frozen-delivery-base/implementation.md').exists(),'product_tree_entries':len(actual),'all_manifest_entries_match':True}
assert tip==target_b;assert record['candidate_json_absent'] and record['delivery_record_absent'] and record['implementation_handoff_absent']
marker=control/'scope-captured.json';marker.write_text(json.dumps(record,indent=2)+'\n')
release=control/'release'
while not release.exists():time.sleep(.1)
release.unlink();print(json.dumps(record,sort_keys=True));print('Direct R12 scope captured; orchestrator moved main from B to D.')
