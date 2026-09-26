import sys,json
from pathlib import Path
candidate=Path('/private/var/tmp/p2p-issue33-verifier-8eh45dgs/first-candidate/candidate')
sys.path.insert(0,str(candidate/'checks'))
from test_p2p_delivery import DeliveryTests
case=DeliveryTests()
case.setUp()
try:
 plan=case.planned_child()
 receipt=plan.parent/'approval.md'
 receipt.write_text('User: approve exact routing v1.\n')
 plan.write_text(plan.read_text().replace('in retained fixture request.','in setup receipt approval.md.'))
 code,value=case.cli()
 assert code==0,value
 workspace=case.root/'.p2p/work/tiny/runtime/workspace'
 paths=[x['path'] for x in case.state()['routing_records']]
 copied=(workspace/receipt.relative_to(case.root)).exists()
 receipt.unlink()
 code_after,value_after=case.cli('status')
 observation={'transport':'explicit existing FakeTransport; controller diagnostic only','initial_exit':code,'transferred_paths':paths,'approval_copied':copied,'status_after_source_receipt_deletion':code_after,'status':value_after['status']}
 print(json.dumps(observation,indent=2))
 assert not copied
 assert code_after==0,value_after
finally:
 case.tearDown()
