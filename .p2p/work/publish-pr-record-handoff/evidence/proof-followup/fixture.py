import os,subprocess,tempfile,shutil,json,hashlib
from pathlib import Path
root=Path(tempfile.mkdtemp(prefix='p2p-proof26-fixture-')); pub=root/'published';local=root/'operator';archive=root/'archive'
for p in (pub,local,archive):p.mkdir()
def git(where,*args):return subprocess.check_output(['git','-C',str(where),*args],stderr=subprocess.STDOUT).decode().strip()
for p in (pub,local):
 git(p,'init','-q');git(p,'config','user.name','Proof fixture');git(p,'config','user.email','proof@example.invalid');git(p,'config','commit.gpgsign','false')
for name in ('equal','changed','mode','tracked'):(pub/name).write_text('original\n')
(pub/'link').symlink_to('equal')
(pub/'.p2p').mkdir();(pub/'.p2p/review.md').write_text('review original\n');(pub/'.p2p/proof.md').write_text('proof original\n')
git(pub,'add','.');git(pub,'commit','-qm','fixture parent');parent=git(pub,'rev-parse','HEAD')
for name in ('equal','changed','mode','tracked'):shutil.copy2(pub/name,local/name)
(local/'changed').write_text('different\n');(local/'mode').chmod(0o755);(local/'link').symlink_to('changed');(local/'receipt').write_text('later receipt\n');(local/'unrelated').write_text('user work\n')
git(local,'add','tracked');git(local,'commit','-qm','operator tracked copy')
def state(p):return ('120000',os.readlink(p)) if p.is_symlink() else ('100755' if p.stat().st_mode&0o111 else '100644',p.read_bytes())
observed={}
for n in ('equal','changed','mode','link','tracked','receipt'):
 observed[n]='local-only' if not (pub/n).exists() else 'identical' if state(pub/n)==state(local/n) else 'differing'
assert observed=={'equal':'identical','changed':'differing','mode':'differing','link':'differing','tracked':'identical','receipt':'local-only'}
print('classification',observed)
# Apply the documented cleanup manually to its one eligible file; tracked identity alone never permits movement.
before={n:state(local/n) for n in observed}|{'unrelated':state(local/'unrelated')}
print('without cleanup authority: inspected only; all seven files remain')
assert all(state(local/n)==s for n,s in before.items())
shutil.move(local/'equal',archive/'equal')
assert state(archive/'equal')==before['equal']
for n,s in before.items():
 if n!='equal':assert state(local/n)==s
print('authorized archive: equal recoverable; changed, mode, link, tracked, receipt, unrelated unchanged')
print('operator final git status',git(local,'status','--porcelain=v1'))
# A frozen receipt is the only addition to this disposable Git history.
(pub/'.p2p/publication.md').write_text('frozen first-publication receipt\n')
git(pub,'add','.p2p/publication.md');git(pub,'commit','-qm','frozen receipt');followup=git(pub,'rev-parse','HEAD')
assert git(pub,'rev-parse','HEAD^')==parent
assert git(pub,'diff','--name-only',parent,followup)==' .p2p/publication.md'.strip()
assert git(pub,'diff',parent,followup,'--','.',':(exclude).p2p')==''
for n in ('review.md','proof.md'):assert git(pub,'show',parent+':.p2p/'+n)==git(pub,'show',followup+':.p2p/'+n)
assert git(pub,'rev-list','--count',parent+'..'+followup)=='1'
print('receipt-only commit',followup,'parent',parent,'original report bytes unchanged; one descendant; no receipt recursion')
# Independent adversarial Git objects make changes visible without altering either candidate input.
(pub/'.p2p/review.md').write_text('tampered report\n');assert git(pub,'diff','--name-only')=='.p2p/review.md'
(pub/'addition').write_text('new product\n');assert '?? addition' in git(pub,'status','--porcelain=v1')
print('counterexamples visible: changed report and untracked product addition; parent != later head detects head drift')
assert parent!=followup
print('scope: manual instruction exercise and actual local Git/filesystem observations; no agent, network or PR-state enforcement tested')
shutil.rmtree(root)
