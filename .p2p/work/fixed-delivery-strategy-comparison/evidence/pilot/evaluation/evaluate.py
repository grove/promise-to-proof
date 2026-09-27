"""Independent bounded public-behavior evaluation; no model calls."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

pilot = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(pilot / 'controllers/review-first/skills/productivity/deliver-issue/scripts'))
import p2p_delivery as d

manifest = json.loads((pilot / 'manifest.json').read_text())
episode = next(e for e in manifest['episodes'] if e['id'] == sys.argv[1])
folder = pilot / 'episodes' / episode['id']
assert (folder / 'finished.json').is_file(), 'episode is not finished'
assert not (folder / 'adjudication.json').exists(), 'retain existing adjudication; do not overwrite'
records = pilot / episode['source'] / '.p2p/work' / episode['task']
state = json.loads((records / 'delivery.json').read_text())
candidate = records / 'runtime/workspace'
before = d.fs.validate(candidate, episode['work'], episode['base'])
assert before == state['candidate']
assert before == json.loads((records / 'candidate.json').read_text())
oracle = pilot / 'evaluation/oracle.py'
assert hashlib.sha256(oracle.read_bytes()).hexdigest() == manifest['oracle_sha256']
scratch = folder / 'oracle-scratch'
scratch.mkdir(exist_ok=False)
(scratch / '.p2p/tmp').mkdir(parents=True)
command = [manifest['host']['executable'], 'sandbox', '--permission-profile', ':workspace',
           '-c', 'sandbox_workspace_write.network_access=false',
           '-c', 'sandbox_workspace_write.exclude_slash_tmp=true',
           '-c', 'sandbox_workspace_write.exclude_tmpdir_env_var=true',
           '-C', str(scratch), sys.executable, '-B', str(oracle), str(candidate), episode['task']]
env = {'PATH': os.defpath + ':/opt/homebrew/bin', 'HOME': str(Path.home()),
       'TMPDIR': str(scratch / '.p2p/tmp'), 'PYTHONDONTWRITEBYTECODE': '1'}
started = time.monotonic()
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, start_new_session=True)
try:
    stdout, stderr = process.communicate(timeout=30)
    timed_out = False
except subprocess.TimeoutExpired:
    os.killpg(process.pid, signal.SIGKILL)
    stdout, stderr = process.communicate()
    timed_out = True
elapsed = time.monotonic() - started
after = d.fs.validate(candidate, episode['work'], episode['base'])
assert after == before, 'candidate changed during independent oracle'
observation = {'command': command, 'returncode': process.returncode, 'timed_out': timed_out,
               'stdout': stdout.decode(errors='replace'), 'stderr': stderr.decode(errors='replace'),
               'elapsed_seconds': elapsed, 'candidate_key': d.candidate_key(before),
               'candidate_stable': True, 'oracle_sha256': manifest['oracle_sha256'],
               'sandbox_probe': '../../evaluation/sandbox-probe-result.json'}
(folder / 'oracle-result.json').write_bytes(d.encoded(observation))
passed = process.returncode == 0 and stdout == b'public behavior checks passed\n' and not timed_out
outcome = 'satisfactory' if passed else 'defective' if b'AssertionError' in stderr and not timed_out else 'unresolved'
judgment = {'outcome': outcome,
            'missed_defects': 0 if passed else 1 if outcome == 'defective' and state['status'] == 'REVIEWED_AND_PROVEN' else None,
            'provenance': str((folder / 'oracle-result.json').relative_to(pilot)),
            'limits': 'Prewritten finite public-behavior checks; zero means no defect observed by these checks. Setup failures and timeouts require maintainer adjudication.'}
(folder / 'adjudication.json').write_bytes(d.encoded(judgment))
assert json.loads((folder / 'adjudication.json').read_text()) == judgment
print(json.dumps({'episode': episode['id'], **judgment}))
