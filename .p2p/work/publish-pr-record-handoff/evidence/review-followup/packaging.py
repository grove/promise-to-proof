from pathlib import Path
import shutil,tempfile,yaml
root=Path('/Users/Shared/p2p-issue-24-6krj8of_/followup26-main69/candidate')
dest=Path(tempfile.mkdtemp(prefix='p2p-review26-package-',dir='/private/tmp'))/'publish-pr'
shutil.copytree(root/'skills/productivity/publish-pr',dest,symlinks=False)
for name in ['SKILL.md','agents/openai.yaml','references/acceptance-contract-protocol.md']:
 p=dest/name
 assert p.is_file() and not p.is_symlink()
assert (dest/'references/acceptance-contract-protocol.md').read_bytes()==(root/'docs/acceptance-contract-protocol.md').read_bytes()
front=yaml.safe_load((dest/'SKILL.md').read_text().split('---',2)[1]); meta=yaml.safe_load((dest/'agents/openai.yaml').read_text())
assert front['name']=='publish-pr' and 'disable-model-invocation' not in front
assert meta['policy']['allow_implicit_invocation'] is True
print('PASS standalone dereferenced protocol, regular readable files, frontmatter and agent YAML parse, implicit invocation true')
