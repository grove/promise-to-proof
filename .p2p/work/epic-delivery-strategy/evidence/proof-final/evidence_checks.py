from pathlib import Path
import hashlib,json,re,subprocess
root=Path('/private/var/tmp/p2p-issue33-verifier-8eh45dgs');r=root/'second-proof-records/evidence';c=root/'second-candidate/candidate';h=lambda b:hashlib.sha256(b).hexdigest()
package=json.loads((r/'repair-scenarios/S3-publication/repaired-package-hashes.json').read_text())
for p,digest in package.items():assert h((c/'skills/productivity'/p).read_bytes())==digest,p
print('installed repaired package identities',len(package),'match exact candidate')
for name in ['S2-incomplete','S2-shared','S3-publication','S8-clean']:
 repo=r/'repair-scenarios'/name/'repo';source=(repo/'.p2p/work/parent/slicing.md').read_bytes();section=re.findall(rb'^## Approved delivery plan\r?\n.*?(?=^## |\Z)',source,re.M|re.S);assert len(section)==1
 saved=(repo/'.p2p/work/lookup/evidence/approved-plan.md').read_bytes();assert saved==section[0]
 pub=(repo/'.p2p/work/lookup/publication.md').read_bytes();assert h(saved).encode() in pub
 if name in ['S2-shared','S3-publication']:
  assert pub.startswith(b'# DRAFT') and b'Target: epic/example' in pub and b'Complete proposed body' in pub
 else:assert pub.startswith(b'# BLOCKED')
 print(name,'current plan saved byte-exact',h(saved),'publication',pub.splitlines()[0].decode())
for name in ['S4-transfer','S4-legacy-transfer']:
 repo=r/'repair-scenarios'/name/'repo';assert (repo/'.p2p/work/parent/approval.md').is_file()
 if 'legacy' in name:assert list((repo/'.p2p/work/parent/history').rglob('slicing.md'))
 print(name,'retained local approval/history reachable; actor request supplies only child path and new fixture location')
for name in ['S9-default','S9-concurrent-body','S9-stale-plan']:
 d=r/'supplement-first'/name;calls=[json.loads(x) for x in (d/'calls.jsonl').read_text().splitlines()];effects=[x for x in calls if x.get('effect')];assert len(effects)==(1 if name=='S9-default' else 0)
 if name=='S9-default':assert effects[0]['exit_code']==1;assert any(x.get('result',{}).get('baseRefName')=='epic/example' for x in calls if isinstance(x.get('result'),dict))
 print(name,'actual total effects',len(effects))
print('saved-state and effect assertions PASS')
