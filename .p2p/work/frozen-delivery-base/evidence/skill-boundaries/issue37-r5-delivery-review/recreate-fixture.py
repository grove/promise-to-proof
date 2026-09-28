import base64, importlib.util, json, os, pathlib, shutil, subprocess, tempfile
REPO = pathlib.Path('/Users/grove/projects/promise-to-proof')
ART = REPO / '.p2p/work/frozen-delivery-base'
source = json.loads((ART / 'candidate.json').read_text())
base = source['comparison_base']
root = pathlib.Path(tempfile.mkdtemp(prefix='issue37-r5-delivery-', dir='/private/tmp'))
fixture = root / 'delivery-review-fixture'

def call(args, *, cwd=None, env=None):
    result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f'{args}: {result.returncode}\n{result.stdout}\n{result.stderr}')
    return result.stdout.strip()

commands = []
def run(args, *, cwd=None, env=None):
    commands.append(' '.join(map(str, args)))
    return call(args, cwd=cwd, env=env)

run(['git', 'clone', '--shared', '--quiet', '--no-checkout', REPO, fixture])
run(['git', 'checkout', '--quiet', '--detach', base], cwd=fixture)
run(['git', 'branch', '--force', 'main', base], cwd=fixture)
run(['git', 'checkout', '--quiet', 'main'], cwd=fixture)
marker = fixture / '.r5-target-only'
marker.write_text('This content exists only at the moved destination B.\n')
run(['git', 'add', '.r5-target-only'], cwd=fixture)
run(['git', 'commit', '--quiet', '-m', 'controlled target B', '--date=2026-09-27T00:00:00+00:00'], cwd=fixture,
    env={**os.environ, 'GIT_AUTHOR_DATE':'2026-09-27T00:00:00+00:00', 'GIT_COMMITTER_DATE':'2026-09-27T00:00:00+00:00'})
target = run(['git', 'rev-parse', 'refs/heads/main'], cwd=fixture)
for child in list(fixture.iterdir()):
    if child.name == '.git':
        continue
    if child.is_symlink() or child.is_file():
        child.unlink()
    else:
        shutil.rmtree(child)
for entry in source['manifest']:
    path = fixture.joinpath(*pathlib.PurePosixPath(entry['path']).parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    if entry['type'] == 'symlink':
        os.symlink(entry['target'], path)
    else:
        path.write_bytes(base64.b64decode(entry['content_base64']))
        path.chmod(0o755 if entry['mode'] == '100755' else 0o644)
for name in ('candidate.json', 'planning-handoff.md'):
    path = fixture / '.p2p/work/frozen-delivery-base' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ART / name, path)
spec = importlib.util.spec_from_file_location('p2pfs', REPO / 'skills/productivity/deliver-issue/scripts/p2p_filesystem.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
key = 'snapshot:sha256:' + helper.digest(helper.canonical(helper.snapshot(fixture)))
assert key == source['key']
assert run(['git', 'rev-parse', 'HEAD'], cwd=fixture) == target
assert run(['git', 'rev-parse', 'main^'], cwd=fixture) == base
assert not (fixture / '.p2p/work/frozen-delivery-base/review.md').exists()
(root / 'fixture-path.txt').write_text(str(fixture) + '\n')
observation = {
    'fixture': str(fixture), 'candidate': key, 'comparison_base': base,
    'target_main': target, 'target_parent': base, 'target_relation': 'fast-forward',
    'candidate_entries': len(source['manifest']), 'candidate_record_base': source['comparison_base'],
    'approval_receipt_present': (fixture / '.p2p/work/frozen-delivery-base/planning-handoff.md').is_file(),
    'b_only_marker_in_candidate': '.r5-target-only' in {entry['path'] for entry in source['manifest']},
    'prior_review_absent': not (fixture / '.p2p/work/frozen-delivery-base/review.md').exists(),
    'commands': commands,
}
(root / 'fixture-observation.json').write_text(json.dumps(observation, indent=2) + '\n')
print(json.dumps(observation, indent=2))
