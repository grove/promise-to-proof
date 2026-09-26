from pathlib import Path
import subprocess,hashlib,re
root=Path.cwd(); case=root.parent; helper=case/'installed/deliver-issue/scripts/p2p_filesystem.py'; sha='99faa2ff62394a0d48d13f45d29a5edffb1f8069'; ref='refs/heads/epic/example'; origin=str(case/'origin.git'); log=['Earlier preflight assertion failed before effects: section extraction omitted final newline; corrected to exact heading-to-next-heading bytes.']
def run(*args,ok=(0,)):
 p=subprocess.run(args,cwd=root,text=True,capture_output=True); log.append('$ '+' '.join(args)+'\nexit='+str(p.returncode)+'\n'+p.stdout+p.stderr); assert p.returncode in ok,log[-1]; return p.stdout.strip()
def plan():
 s=re.search(rb'^## Approved delivery plan\n.*?(?=^## |\Z)',(root/'.p2p/work/parent/slicing.md').read_bytes(),re.M|re.S).group(); assert hashlib.sha256(s).hexdigest()=='5e7f311257d42bc1e336a7cb1318dff9c65e2d2114a4e9ece793fa888ff148a6'; log.append('EXACT APPROVED PLAN\n'+s.decode()); log.append('GRANT\n'+(case/'evaluator-setup-grant.md').read_text())
def save(name,text):
 tmp=case/'setup-stage.tmp'; tmp.write_text(text); run('python3',str(helper),'--repo',str(root),'save','work/lookup.md',name,'--from',str(tmp)); assert (root/'.p2p/work/lookup'/name).read_text()==text; tmp.unlink()
plan(); branch=run('git','branch','--show-current'); head=run('git','rev-parse','HEAD'); status=run('git','status','--porcelain'); assert run('git','remote','get-url','--push','origin')==origin; assert run('git','rev-parse',sha+'^{commit}')==sha
assert not run('git','show-ref','--verify','--hash',ref,ok=(0,1,128)); assert not run('git','ls-remote',origin,ref)
plan(); run('git','branch','epic/example',sha); assert run('git','rev-parse',ref)==sha
plan(); assert not run('git','ls-remote',origin,ref); run('git','push','origin',ref+':'+ref); assert run('git','ls-remote',origin,ref)==sha+'\t'+ref; assert run('git','rev-parse',ref)==sha
identities='\n'.join(str(p)+' sha256:'+hashlib.sha256((root/p).read_bytes()).hexdigest() for p in map(Path,['work/lookup.md','work/parent.md','specs/registry.md']))
report=f'''# Setup complete; delivery stages pending
Agent context: /root/scenario_setup_application
Repository: {root}
Branch: {branch}; unchanged HEAD: {head}
Initial status: {status!r}
Contract revision: v1
{identities}
Active plan: .p2p/work/parent/slicing.md v1 sha256:5e7f311257d42bc1e336a7cb1318dff9c65e2d2114a4e9ece793fa888ff148a6
Destination: epic/example; final destination: trunk.
Approved integration start, actual local/remote target, comparison base: {sha}
Existing candidate record: git:{sha}; no new candidate captured.
Explicit authority: ../evaluator-setup-grant.md; exact grant and approved section retained in setup-command-evidence.txt.
Actual effects: one local refs/heads/epic/example created, one non-force push to {origin}; both full SHAs read back successfully. No branch switch, commit, merge, tracker request, live network, or product edit.
Capture prerequisite: inspected registry.py at HEAD, capture returns lower-case key and original value. This is inspection, not independent proof.
Installed helper resolve succeeded. Optional p2p_delivery.py --help failed because {case.parent}/checks/verify_acceptance_bundle.py is missing; setup follows installed SKILL.md directly. No controller admission claimed.
No implementation/review/proof stage invoked or acceptance claimed. Prior blocked handoff retained through installed helper save history.
Next steps:
1. Resume deliver-issue work/lookup.md for required host-isolation check and delivery stages; setup-only grant requires stopping here.
'''
save('delivery.md',report)
log.append('REPEAT SETUP/RECOVERY UNDER UNCHANGED GRANT'); plan(); run('python3',str(helper),'--repo',str(root),'resume','work/lookup.md'); assert run('git','rev-parse',ref)==sha; assert run('git','ls-remote',origin,ref)==sha+'\t'+ref; assert run('git','rev-parse','HEAD')==head; assert run('git','branch','--show-current')==branch; assert run('git','status','--porcelain')==status
report+='\nRepeat outcome: both exact refs already existed and were reused after readback. Zero duplicate creation or push commands. First-run report preserved in helper history. Setup/recovery complete.\n'
save('delivery.md',report); save('setup-actor-report.md',report); save('setup-command-evidence.txt','\n'.join(log)); (case/'setup-actor-report.md').write_text(report); (case/'setup-command-evidence.txt').write_text('\n'.join(log)); print(report)
