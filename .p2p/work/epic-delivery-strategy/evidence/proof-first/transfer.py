from pathlib import Path
import subprocess,sys,json,tempfile
root=Path(tempfile.mkdtemp(prefix='transfer-public-',dir='/private/tmp/p2p-independent-proof'))
def git(*args):return subprocess.check_output(['git','-C',str(root),*args],stderr=subprocess.STDOUT,text=True).strip()
git('init','-b','trunk');git('config','user.name','Proof fixture');git('config','user.email','fixture@example.invalid')
(root/'spec.txt').write_text('greet.py prints hello followed by newline.\n');(root/'greet.py').write_text("print('hello')\n");(root/'work').mkdir()
contract='''# Acceptance contract: greeting
Contract revision: v1
Source: [Specification](../spec.txt)

## Acceptance matrix

| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | spec.txt | greet.py prints hello and exits zero. | Wrong text fails. | python3 greet.py | hello plus newline and zero | Run and compare exact output | planned |
'''
(root/'work/parent.md').write_text(contract);(root/'work/child.md').write_text(contract+'\nParent: [Parent](parent.md)\n');git('add','.');git('commit','-m','Fixture');sha=git('rev-parse','HEAD');git('branch','epic/greeting',sha)
p=root/'.p2p/work/parent';p.mkdir(parents=True);(p/'approval.md').write_text('Fixture owner: approve v1 exact destinations. Strategy only.\n')
(p/'slicing.md').write_text(f'''# Slicing
## Approved delivery plan
Plan revision: v1
Approval source: Fixture owner approved v1 in the retained receipt approval.md.
Parent: work/parent.md
Final destination: trunk
Integration branch: epic/greeting
Integration start: {sha}
Default choice: grouped

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
| work/child.md | default | epic/greeting | Requires parent assembly. | remaining |

Parent completion: Prove the combined greeting.
Pending actions: None.
''')
cli='/private/var/tmp/p2p-issue33-verifier-8eh45dgs/first-candidate/candidate/skills/productivity/deliver-issue/scripts/p2p_delivery.py'
command=[sys.executable,'-B',cli,'--repo',str(root),'run','work/child.md','--comparison-base',sha,'--authorize-local','--max-dispatches','0']
res=subprocess.run(command,capture_output=True,text=True);(root.parent/'transfer-public-cli.json').write_text(res.stdout)
result=json.loads(res.stdout);workspace=root/'.p2p/work/child/runtime/workspace'
print('command:', ' '.join(command));print('exit:',res.returncode);print('blocker:',result.get('blocker'));print('source receipt:',(p/'approval.md').exists());print('workspace plan:',(workspace/'.p2p/work/parent/slicing.md').exists());print('workspace receipt:',(workspace/'.p2p/work/parent/approval.md').exists());print('attempts:',len(result.get('attempts',[])))
assert (workspace/'.p2p/work/parent/slicing.md').exists()
assert not (workspace/'.p2p/work/parent/approval.md').exists()
assert result['blocker']=='dispatch-count limit exhausted before preflight-1'
print('CONFIRMED COUNTEREXAMPLE: approved plan transfers without its referenced receipt')
