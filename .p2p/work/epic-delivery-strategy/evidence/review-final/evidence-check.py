import hashlib,json,pathlib,re
root=pathlib.Path('/private/var/tmp/p2p-issue33-verifier-8eh45dgs/repair-scenarios-completed')
candidate=pathlib.Path('/private/var/tmp/p2p-issue33-verifier-8eh45dgs/second-candidate/candidate')
count=0
for record in root.glob('*/retention.json'):
 data=json.loads(record.read_text())
 for e in data['files']:
  suffix=e['saved'].split('/repair-scenarios/',1)[1]
  p=root/suffix
  assert hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256'],p
  count+=1
print('retention entries verified',count)
for case,slug,names in [('S9-hash-gates','lookup',['publication.md','merge-readiness.md']),('S12-parent-ci','parent',['merge-readiness.md']),('S12-parent-approval','parent',['merge-readiness.md'])]:
 repo=root/case/'repo'; section=re.findall(rb'^## Approved delivery plan\r?\n.*?(?=^## |\Z)',(repo/'.p2p/work/parent/slicing.md').read_bytes(),re.M|re.S)[0]
 h=hashlib.sha256(section).hexdigest(); directory=repo/'.p2p/work'/slug
 assert (directory/'evidence/transfer-approved-plan.md').read_bytes()==section
 for name in names:
  report=(directory/name).read_bytes()
  assert h.encode() in report and b'```markdown\n'+section+b'```' in report
  for skill in ['publish-pr','merge-readiness'] if name=='publication.md' else ['merge-readiness']:
   for path in ['SKILL.md','references/acceptance-contract-protocol.md']:
    assert hashlib.sha256((candidate/'skills/productivity'/skill/path).read_bytes()).hexdigest().encode() in report
 print(case, h, 'raw bytes, reports, installed skill/protocol identities match')
for case in ['S12-parent-ci','S12-parent-approval']:
 c=root/case; events=[json.loads(x) for x in (c/'calls.jsonl').read_text().splitlines()]
 assert not any(e.get('effect') for e in events)
 print(case,'no tracker effects',len(events),'reads')
