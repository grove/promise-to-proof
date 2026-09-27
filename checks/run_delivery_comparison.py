#!/usr/bin/env python3
"""Prepare and run the six-episode serial-order pilot. prepare makes no model calls."""
import argparse
import difflib
import fcntl
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

PROJECT = Path(__file__).resolve().parents[1]
CONTROLLER_BASE = 'cc27a47f5ee765cff3cf13b21c36f974cb1234ae'
SCRIPT = 'skills/productivity/deliver-issue/scripts/p2p_delivery.py'
sys.path.insert(0, str(PROJECT / Path(SCRIPT).parent))
import p2p_delivery as d

ORDER = "            for name in ('review', 'proof'):"
TASKS = ('greeting', 'save-report', 'repair-report')
STRATEGIES = ('review-first', 'proof-first')
FILES = (SCRIPT, 'skills/productivity/deliver-issue/scripts/p2p_filesystem.py',
         'checks/verify_acceptance_bundle.py')
ORACLE = '''# Evaluation only. Execute only inside an OS sandbox, never in a worker prompt.
import importlib.util
from pathlib import Path
import subprocess
import sys
candidate, task = Path(sys.argv[1]), sys.argv[2]
if task == "greeting":
    result = subprocess.run([sys.executable, "-B", str(candidate / "greet.py")], capture_output=True, timeout=15)
    assert result.returncode == 0, repr(result.stderr)
    assert result.stdout == b"hello\\n", repr(result.stdout)
else:
    spec = importlib.util.spec_from_file_location("delivered_report", candidate / "report.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    target = Path("report-output.txt")
    for text in ("hëllo 世界\\n", "replacement\\n", ""):
        assert module.save_report(target, text) is None, "successful return must be None"
        assert target.read_bytes() == text.encode("utf-8"), "UTF-8 or overwrite mismatch"
    try:
        module.save_report(Path("absent-parent") / "report.txt", "failure")
    except OSError:
        pass
    else:
        raise AssertionError("I/O error was swallowed")
print("public behavior checks passed")
'''


def save(path, value):
    data = d.encoded(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != data:
        old = path.read_bytes()
        history = path.parent / 'history' / d.fs.digest(old) / path.name
        history.parent.mkdir(parents=True, exist_ok=True)
        d.fs.atomic_write(history, old)
    d.fs.atomic_write(path, data)
    if path.read_bytes() != data:
        raise ValueError('readback failed: ' + str(path))


def configured():
    config = d.host_config(Path('/unused-comparison-scratch'))
    if not config.get('model'):
        raise ValueError('pilot requires an explicit configured model')
    executable = shutil.which('codex')
    if not executable:
        raise ValueError('codex executable unavailable')
    return {'model': config['model'], 'reasoning': config.get('model_reasoning_effort', 'default'),
            'executable': executable,
            'version': subprocess.check_output([executable, '--version'], text=True).strip(),
            'os': platform.platform(), 'skills': d.skills()}


def fixture(root, task):
    root.mkdir(parents=True)
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    (root / '.gitignore').write_text('/.p2p/tmp/\n')
    if task == 'greeting':
        requirements = [('greet.py prints hello followed by a newline and exits zero.',
                         'python3 greet.py', 'exact stdout and exit status')]
    else:
        requirements = [
            ('report.py exports save_report(path, text), saving supplied text as UTF-8.', 'save_report(path, text)', 'expected UTF-8 bytes'),
            ('Overwrite an existing report at the supplied path.', 'save_report(path, text)', 'replacement contents'),
            ('Return None after success.', 'save_report(path, text)', 'return identity is None'),
            ('Propagate I/O errors to the caller.', 'save_report(path, text)', 'missing parent raises OSError')]
        if task == 'repair-report':
            (root / 'report.py').write_text('from pathlib import Path\n\ndef save_report(path, text):\n    try:\n        Path(path).write_text(text, encoding="utf-8")\n    except OSError:\n        pass\n')
    description = '\n'.join(r[0] for r in requirements) + '\n'
    description += 'Parent creation, atomic replacement and crash durability are excluded.\n'
    (root / 'spec.txt').write_text(description)
    subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(root), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                    'commit', '-qm', 'Pilot task input'], check=True,
                   env={**os.environ, 'GIT_AUTHOR_DATE': '2026-09-26T00:00:00Z', 'GIT_COMMITTER_DATE': '2026-09-26T00:00:00Z'})
    base = d.fs.full_commit(root, 'HEAD')
    (root / 'work').mkdir()
    text = f'# Acceptance contract: {task}\n\nContract revision: v1\nSource: [Specification](../spec.txt)\n\nIntended outcome: Implement the supplied public behavior.\n\n## Acceptance matrix\n\n'
    text += '| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |\n|---|---|---|---|---|---|---|---|\n'
    for index, (requirement, seam, oracle) in enumerate(requirements, 1):
        text += f'| R{index} | spec.txt | {requirement} | Incorrect output, return, or error handling fails. | {seam} | {oracle} | Execute the public seam and retain assertions and observations. | planned |\n'
    text += '\n## Unresolved gaps\n\nNone.\n'
    (root / f'work/{task}.md').write_text(text)
    d.contract(root, f'work/{task}.md')
    return base


def prepare(destination):
    started = time.time()
    host = configured()
    destination.mkdir(parents=True, exist_ok=False)
    sources = {name: subprocess.check_output(['git', '-C', str(PROJECT), 'show',
                                               f'{CONTROLLER_BASE}:{name}'])
               for name in FILES}
    original = sources[SCRIPT].decode()
    if original.count(ORDER) != 1 or ORDER not in original.split('    def run(self):', 1)[1]:
        raise ValueError('controller ordering seam changed; inspect before preparing')
    hashes = {}
    for strategy in STRATEGIES:
        hashes[strategy] = {}
        for name, data in sources.items():
            target = destination / 'controllers' / strategy / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if name == SCRIPT and strategy == 'proof-first':
                data = original.replace(ORDER, ORDER.replace("'review', 'proof'", "'proof', 'review'")).encode()
            target.write_bytes(data)
            hashes[strategy][name] = d.fs.digest(data)
    diff = ''.join(difflib.unified_diff(original.splitlines(True),
               (destination / 'controllers/proof-first' / SCRIPT).read_text().splitlines(True),
               fromfile='review-first/p2p_delivery.py', tofile='proof-first/p2p_delivery.py'))
    (destination / 'controller-order.diff').write_text(diff)
    oracle = destination / 'evaluation/oracle.py'
    oracle.parent.mkdir()
    oracle.write_text(ORACLE)
    agreement = (PROJECT / 'work/fixed-delivery-strategy-comparison.md').read_bytes()
    (destination / 'evaluation/pilot-contract.md').write_bytes(agreement)
    episodes = []
    for index, task in enumerate(TASKS):
        for strategy in (STRATEGIES if index % 2 == 0 else STRATEGIES[::-1]):
            episode_id = task + '-' + strategy
            relative = 'episodes/' + episode_id + '/source'
            root = destination / relative
            base = fixture(root, task)
            episodes.append({'id': episode_id, 'task': task, 'strategy': strategy,
                             'source': relative, 'work': f'work/{task}.md', 'base': base,
                             'input_manifest': d.fs.snapshot(root)})
    manifest = {'schema': 'p2p-delivery-pilot/v1', 'created': d.now(), 'host': host,
                'base_controller_sha256': d.fs.digest(sources[SCRIPT]),
                'pilot_contract_sha256': d.fs.digest(agreement),
                'runner_sha256': d.fs.digest(Path(__file__).read_bytes()),
                'controller_files': hashes, 'oracle_sha256': d.fs.digest(oracle.read_bytes()),
                'limits': {'max_dispatches': 8, 'max_seconds': 1800, 'hard_monetary_cap': 'unsupported'},
                'evaluation': 'Public-behavior oracle; ambiguous outcomes require maintainer adjudication.',
                'concurrency': 'unexecuted: unsupported by serial controller',
                'episodes': episodes, 'prepare_elapsed_seconds': time.time() - started,
                'human': {'active_seconds': None, 'passive_wait_seconds': None, 'interruptions': None}}
    save(destination / 'manifest.json', manifest)
    return manifest


def validate(destination, manifest):
    if configured() != manifest['host']:
        raise ValueError('configured host/model/reasoning/skills changed since preregistration')
    for strategy, files in manifest['controller_files'].items():
        for name, digest in files.items():
            if d.fs.digest((destination / 'controllers' / strategy / name).read_bytes()) != digest:
                raise ValueError('retained controller changed: ' + strategy + '/' + name)
    if d.fs.digest((destination / 'evaluation/oracle.py').read_bytes()) != manifest['oracle_sha256']:
        raise ValueError('preregistered independent oracle changed')


def run_episode(destination, manifest, episode):
    folder = destination / 'episodes' / episode['id']
    with (folder / 'runner.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if (folder / 'finished.json').exists():
            validate(destination, manifest)
            return json.loads((folder / 'finished.json').read_text())
        if (folder / 'started.json').exists():
            raise ValueError('uncertain prior invocation; collect existing receipts; do not redispatch ' + episode['id'])
        validate(destination, manifest)
        root = destination / episode['source']
        if d.fs.snapshot(root) != episode['input_manifest'] or d.fs.full_commit(root, 'HEAD') != episode['base']:
            raise ValueError('preregistered task input changed: ' + episode['id'])
        command = [sys.executable, '-B', str(destination / 'controllers' / episode['strategy'] / SCRIPT),
                   '--repo', str(root), 'run', episode['work'], '--comparison-base', episode['base'],
                   '--authorize-local', '--max-dispatches', '8', '--max-seconds', '1800']
        started = time.time()
        save(folder / 'started.json', {'started': started, 'command': command})
        with (folder / 'stdout.json').open('xb') as stdout, (folder / 'stderr.txt').open('xb') as stderr:
            completed = subprocess.run(command, stdout=stdout, stderr=stderr)
        result = {'started': started, 'finished': time.time(), 'returncode': completed.returncode}
        save(folder / 'finished.json', result)
        validate(destination, manifest)
        return result


def epoch(value):
    return d.datetime.datetime.fromisoformat(value).timestamp() if value else None


def collect(destination, manifest):
    episodes = []
    for episode in manifest['episodes']:
        folder = destination / 'episodes' / episode['id']
        records = destination / episode['source'] / '.p2p/work' / episode['task']
        state = json.loads((records / 'delivery.json').read_text()) if (records / 'delivery.json').exists() else {}
        timing = json.loads((folder / 'finished.json').read_text()) if (folder / 'finished.json').exists() else {}
        start = json.loads((folder / 'started.json').read_text()).get('started') if (folder / 'started.json').exists() else None
        adjudication = json.loads((folder / 'adjudication.json').read_text()) if (folder / 'adjudication.json').exists() else {
            'outcome': 'unresolved', 'missed_defects': None, 'provenance': 'Independent sandboxed oracle has not been adjudicated.'}
        attempts = []
        mismatches = []
        for saved_attempt in state.get('attempts', []):
            attempt = dict(saved_attempt)
            receipt_folder = records / 'attempts' / attempt['id']
            exit_path = receipt_folder / 'exit.json'
            if exit_path.exists():
                receipt = json.loads(exit_path.read_text())
                if (receipt.get('attempt_id') != attempt['id'] or receipt.get('inputs') != attempt['inputs'] or
                    receipt.get('event_sha256') != d.fs.digest((receipt_folder / 'events.jsonl').read_bytes())):
                    raise ValueError('conflicting completion receipt: ' + attempt['id'])
                attempt['finished'] = receipt['finished']
                try:
                    attempt['usage'] = d.host_events(receipt_folder / 'events.jsonl')['usage']
                except ValueError:
                    pass  # An incomplete host event stream is still a charged attempt with unknown usage.
            launch_path = records / 'attempts' / attempt['id'] / 'launch.json'
            if launch_path.exists():
                config = json.loads(launch_path.read_text())['configuration']
                if (config.get('model') != manifest['host']['model'] or
                    config.get('model_reasoning_effort', 'default') != manifest['host']['reasoning']):
                    mismatches.append(attempt['id'])
            attempts.append({'id': attempt['id'], 'stage': attempt['stage'],
                             'start': epoch(attempt.get('started')), 'end': epoch(attempt.get('finished')),
                             'cost': {'kind': 'unknown'}, 'usage': attempt.get('usage', 'unknown'),
                             'status': attempt['status'], 'receipts': str(launch_path.parent.relative_to(destination))})
        if mismatches:
            raise ValueError('model configuration drift in actual dispatches: ' + ', '.join(mismatches))
        episodes.append({'id': episode['id'], 'task': episode['task'], 'strategy': episode['strategy'],
                         'evidence': 'live' if attempts else 'unexecuted', 'host': manifest['host'],
                         'config': {'required_checks': ['review', 'proof'], 'repair_limit': 1,
                                    'model': manifest['host']['model'], 'reasoning': manifest['host']['reasoning'],
                                    'controller': manifest['base_controller_sha256'], 'permissions': d.POLICY},
                         'start': start, 'end': timing.get('finished'),
                         'reported_complete': state.get('status') == 'REVIEWED_AND_PROVEN',
                         'workflow_status': state.get('status', 'unexecuted'),
                         'blocker': state.get('blocker'), 'adjudication': adjudication,
                         'human': {'active_seconds': None, 'waiting_seconds': None, 'interruptions': None},
                         'attempts': attempts, 'costs': [{'kind': 'unknown', 'provenance': 'Episode setup and readback charges are unavailable.'}],
                         'raw_records': str(records.relative_to(destination))})
    sensitivity_path = destination / 'evaluation/sensitivity.json'
    sensitivity = json.loads(sensitivity_path.read_text()) if sensitivity_path.exists() else []
    result = {'schema_version': 1, 'currency': 'USD', 'episodes': episodes, 'sensitivity': sensitivity,
              'overhead': {'costs': [{'kind': 'unknown'}], 'active_seconds': None,
                           'waiting_seconds': None, 'interruptions': None,
                           'prepare_elapsed_seconds': manifest['prepare_elapsed_seconds']},
              'maintenance_seconds': None, 'preregistration': 'manifest.json',
              'concurrency': manifest['concurrency']}
    save(destination / 'comparison-input.json', result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'run', 'collect'))
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--episode', help='one preregistered episode; omit to run all six')
    parser.add_argument('--authorize-live', action='store_true', help='authorize model calls; costs are unknown')
    args = parser.parse_args(argv)
    destination = args.output_dir.resolve()
    try:
        if args.action == 'prepare':
            prepare(destination)
        else:
            manifest = json.loads((destination / 'manifest.json').read_text())
            if args.action == 'run':
                if not args.authorize_live:
                    raise ValueError('run requires --authorize-live; no monetary cap can be enforced')
                selected = [e for e in manifest['episodes'] if args.episode is None or e['id'] == args.episode]
                if not selected:
                    raise ValueError('unknown episode')
                for episode in selected:
                    result = run_episode(destination, manifest, episode)
                    print(json.dumps({'episode': episode['id'], **result}), flush=True)
                    if result['returncode'] != 0:
                        collect(destination, manifest)
                        raise ValueError('cohort stopped after unsuccessful episode: ' + episode['id'])
            collect(destination, manifest)
        print(json.dumps({'output_directory': str(destination), 'action': args.action}))
        return 0
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
