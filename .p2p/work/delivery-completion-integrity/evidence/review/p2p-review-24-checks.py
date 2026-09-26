import importlib.util,json,tempfile
from pathlib import Path
source=Path('/Users/Shared/p2p-issue-24-6krj8of_/round1/candidate/checks/delivery-model/check.py')
spec=importlib.util.spec_from_file_location('delivery_check',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
fizz=Path('/private/tmp/p2p-fizzbee-24/fizzbee-v0.5.3-macos_arm/fizz')
for rel,hash in m.PIN.items():assert m.digest(fizz.parent/rel)==hash
out=Path('/private/tmp/p2p-review-24-focused');out.mkdir()
observations=[]
with tempfile.TemporaryDirectory(prefix='p2p-review-scratch-') as scratch:
 for kind,name,scenario,mutation,witness in [('witness','repair','repair','none','repair'),('witness','exhausted','exhausted','none','exhausted'),('mutation','repair-reset','exhausted','repair-reset','none'),('mutation','evidence-lost','evidence-lost','evidence-lost','none')]:
  observations.append(m.run(fizz,out,Path(scratch),kind,name,scenario,mutation,witness))
for name in ['witness-repair','witness-exhausted','mutation-repair-reset','mutation-evidence-lost']:
 t=json.loads((out/name/'trace.json').read_text()); print(name,[s['Name'] for s in t]);print('terminal',json.dumps(t[-1]['Node']['state'],sort_keys=True))
(out/'review-observations.json').write_text(json.dumps(observations,indent=2)+'\n')
