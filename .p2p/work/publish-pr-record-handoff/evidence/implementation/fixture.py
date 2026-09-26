from pathlib import Path
import os,shutil,stat,subprocess,tempfile
with tempfile.TemporaryDirectory(prefix='p2p-26-check-') as tmp:
 root=Path(tmp);published=root/'published';local=root/'local';archive=root/'archive'
 for p in (published,local,archive):p.mkdir()
 for name in ('equal','changed','mode'):(published/name).write_text('published\n');(local/name).write_text('published\n')
 (local/'changed').write_text('local edit\n');(local/'mode').chmod(0o755)
 (published/'link').symlink_to('equal');(local/'link').symlink_to('changed')
 (local/'receipt').write_text('later receipt\n');(local/'unrelated').write_text('user work\n')
 def identity(p):
  if p.is_symlink():return ('symlink',os.readlink(p))
  return ('file',bool(p.stat().st_mode&0o111),p.read_bytes())
 observed={name:'same' if identity(local/name)==identity(published/name) else 'different' for name in ('equal','changed','mode','link')}
 assert observed=={'equal':'same','changed':'different','mode':'different','link':'different'}
 assert not (published/'receipt').exists()
 shutil.move(str(local/'equal'),str(archive/'equal'));assert (archive/'equal').read_bytes()==(published/'equal').read_bytes()
 assert sorted(p.name for p in local.iterdir())==['changed','link','mode','receipt','unrelated']
 repo=root/'git';repo.mkdir()
 def git(*args):return subprocess.check_output(['git','-C',str(repo),*args],stderr=subprocess.STDOUT)
 git('init','-q');git('config','user.name','Fixture');git('config','user.email','fixture@example.invalid');git('config','commit.gpgsign','false')
 (repo/'product').write_text('fixed\n');(repo/'review.md').write_text('REVIEWED\n');(repo/'proof.md').write_text('PROVEN\n');git('add','.');git('commit','-qm','base');before=git('rev-parse','HEAD').decode().strip()
 (repo/'.p2p').mkdir();(repo/'.p2p/receipt.md').write_text('frozen receipt\n');git('add','.p2p');git('commit','-qm','receipt');after=git('rev-parse','HEAD').decode().strip()
 assert git('diff','--name-only',before,after).decode().splitlines()==['.p2p/receipt.md'];assert git('rev-parse','HEAD^').decode().strip()==before
 for name in ('product','review.md','proof.md'):assert git('show',before+':'+name)==git('show',after+':'+name)
 print('PASS: equal/changed/mode/symlink classification; recoverable matching-only archive; changed/local-only/unrelated preservation; records-only Git ancestry and unchanged product/reports.')
 print('Fixture checks filesystem and Git facts only; instruction compliance requires the recorded walkthroughs, not this fixture alone.')
