import pathlib,tempfile,shutil,yaml,subprocess
c=pathlib.Path('/Users/Shared/p2p-issue-24-6krj8of_/followup26-main69/candidate');p=pathlib.Path(tempfile.mkdtemp(prefix='p2p-proof26-package-'))/'publish-pr'
shutil.copytree(c/'skills/productivity/publish-pr',p,symlinks=False)
for n in ('SKILL.md','agents/openai.yaml','references/acceptance-contract-protocol.md'):
 f=p/n;assert f.is_file() and not f.is_symlink();print('readable regular file',n,len(f.read_bytes()))
assert (p/'references/acceptance-contract-protocol.md').read_bytes()==(c/'docs/acceptance-contract-protocol.md').read_bytes()
m=yaml.safe_load((p/'SKILL.md').read_text().split('---',2)[1]);u=yaml.safe_load((p/'agents/openai.yaml').read_text());assert 'disable-model-invocation' not in m;assert u['policy']['allow_implicit_invocation'] is True
print('protocol bytes equal; YAML parsed; implicit invocation allowed; disable-model-invocation absent')
r=subprocess.run(['python3','/Users/grove/.codex/skills/.system/skill-creator/scripts/quick_validate.py',str(c/'skills/productivity/publish-pr')],capture_output=True,text=True);print(r.stdout);assert r.returncode==0
print('packaging only; installed agent invocation not claimed')
shutil.rmtree(p.parent)
