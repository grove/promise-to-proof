#!/usr/bin/env python3
"""Pinned FizzBee MBT against fresh CLI processes and one saved invocation per trace."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time

import check

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
CASES = ['successful-delivery', 'blocked-failure', 'known-result-restart',
         'uncertain-launch-restart', 'repair-restart-exhaustion', 'successful-repair',
         'unauthorized-before-dispatch', 'stale-identity', 'mistyped-identity',
         'candidate-mutated-during-verification', 'incomplete-archive',
         'interrupted-report-storage', 'late-stage-result', 'duplicate-report-write',
         'repeated-resume', 'contested-dirty-file', 'concurrent-resume']
FAULTS = {'stale-identity', 'mistyped-identity', 'candidate-mutated-during-verification',
          'incomplete-archive', 'late-stage-result', 'duplicate-report-write'}
MBT_PIN = {'fizzbee-mbt-runner': '7e4ca5e3f1e8183d3d335f5878128f6c5cbb01398bbbc377166afc3fa7464c65',
           'fizzbee-mbt-server': '767f8b192d0e5d3e098064ef2afe99aac7ccdf25ca8ff45c8e6231d0cecd4d1a'}
# Every edit targets actual production guard source. Oracles and adapters stay fixed.
MUTATIONS = {
    'stale-report-guard-removed': ('stale-identity',
        "if json.loads(report['input_identity_json']) != inputs:", 'if False:'),
    'duplicate-report-guard-removed': ('duplicate-report-write',
        'if stored.exists() and stored.read_bytes() != encoded(report):', 'if False:'),
    'late-receipt-guard-removed': ('late-stage-result',
        "if end.get('attempt_id') != attempt['id'] or end.get('inputs') != attempt['inputs']:", 'if False:'),
    'repair-bound-removed': ('repair-restart-exhaustion',
        "if self.state['repair_used']:", 'if False:'),
    'authority-guard-removed': ('unauthorized-before-dispatch',
        'if not args.authorize_local:', 'if False:'),
}


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def run(command, destination, env=None, cwd=None):
    result = subprocess.run(list(map(str, command)), cwd=cwd, env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
    destination.write_text(result.stdout)
    return result


def required(case):
    counts = {'Start': 1, 'Resume': 2}
    if case in ('unauthorized-before-dispatch', 'contested-dirty-file'):
        return counts
    counts['Restart'] = 1
    if case == 'uncertain-launch-restart':
        return counts
    counts.update(Review=1, Proof=1)
    if case in ('repair-restart-exhaustion', 'successful-repair', 'blocked-failure'):
        counts.update(Review=2, Proof=2, Restart=2)
    if case == 'interrupted-report-storage':
        counts['Restart'] = 2
    if case in FAULTS:
        counts['Corrupt'] = 1
    if case == 'concurrent-resume':
        del counts['Review']
        counts['Overlap'] = 1
    return counts


def execute(args, runtime, output, case, seed, product, mutation=None):
    target = output / (case + '-' + str(seed) + ('-' + mutation if mutation else ''))
    target.mkdir()
    source = (HERE / 'conformance.fizz').read_text().replace('CASE = "successful-delivery"', 'CASE = ' + json.dumps(case))
    model = target / 'conformance.fizz'
    model.write_text(source)
    graph = target / 'graph'
    checked = run([args.fizz, '--output-dir', graph, model], target / 'model.log')
    assert checked.returncode == 0 and 'PASSED: Model checker completed successfully' in checked.stdout, checked.stdout
    nodes = [node for path in graph.glob('nodes_*.pb') for node in check.nodes(path)]
    depth = max(n['stats']['totalActions'] for n in nodes)
    assert depth < 256, 'model action cutoff reached'
    env = dict(os.environ, P2P_REPO=str(product), P2P_TRACE_DIR=str(target / 'fixture'),
               P2P_MBT_CASE=case, FIZZBEE_MBT_BIN=str(args.mbt / 'fizzbee-mbt-runner'),
               FIZZBEE_MBT_SEQ_SEED=str(seed), PYTHON=sys.executable, PYTHONDONTWRITEBYTECODE='1')
    server_command = [str(args.mbt / 'fizzbee-mbt-server'), '--states_file', str(graph)]
    command = ['node', str(runtime / 'dist/conformance_test.js')]
    with (target / 'server.log').open('w') as stream:
        server = subprocess.Popen(server_command, stdout=stream, stderr=subprocess.STDOUT)
        try:
            for _ in range(200):
                assert server.poll() is None, (target / 'server.log').read_text()
                try:
                    with socket.create_connection(('127.0.0.1', 50051), timeout=.1):
                        break
                except OSError:
                    time.sleep(.025)
            else:
                raise AssertionError('MBT localhost server did not start')
            result = run(command, target / 'mbt.log', env=env, cwd=runtime)
        finally:
            server.terminate()
            server.wait(timeout=5)
    trace_path = target / 'fixture/actions.jsonl'
    trace = [json.loads(line) for line in trace_path.read_text().splitlines()] if trace_path.exists() else []
    counts = Counter(x['action'] for x in trace)
    observation = {'case': case, 'seed': seed, 'mutation': mutation,
                   'evidence_class': 'substitute-backed actual controller CLI',
                   'command': command, 'server_command': server_command,
                   'environment': {k: env[k] for k in ('P2P_REPO', 'P2P_TRACE_DIR', 'P2P_MBT_CASE', 'FIZZBEE_MBT_BIN', 'FIZZBEE_MBT_SEQ_SEED')},
                   'exit': result.returncode, 'model_nodes': len(nodes), 'model_max_depth': depth,
                   'actions': dict(counts), 'trace': 'fixture/actions.jsonl',
                   'replay': f'python3 checks/delivery-model/conformance.py --case {case} --seed {seed}' +
                             (f' --mutation {mutation}' if mutation else '') + ' --output-dir NEW_DIRECTORY'}
    save(target / 'observation.json', observation)
    if mutation:
        assert result.returncode != 0 and 'Return value mismatched' in result.stdout, result.stdout
        assert trace and counts['Start'] == 1, 'mutant never reached real CLI'
    else:
        assert result.returncode == 0 and 'Runner exited successfully' in result.stdout, result.stdout
        server_log = (target / 'server.log').read_text()
        assert 'STATUS_EXECUTION_FAILED' not in server_log and 'No matching Source Link' not in server_log, server_log
        for action, count in required(case).items():
            assert counts[action] == count, f'{case}: missing real action {action}: {counts}'
        # The model's final response must have been compared, including repeated resume.
        assert trace[-1]['action'] == 'Resume', counts
    print(f'{target.name}: ' + ('caught controller mutation' if mutation else 'PASS'), flush=True)
    return observation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fizz', type=Path, default=os.environ.get('FIZZBEE'))
    parser.add_argument('--mbt', type=Path, default=os.environ.get('FIZZBEE_MBT'))
    parser.add_argument('--node-modules', type=Path, help='existing pinned npm installation; otherwise npm ci in output scratch')
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--case', choices=CASES)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--mutation', choices=MUTATIONS)
    parser.add_argument('--all-mutations', action='store_true')
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        parser.error('Python 3.11 or newer is required by the real controller')
    if not args.fizz or not args.mbt:
        parser.error('set FIZZBEE and FIZZBEE_MBT or pass --fizz and --mbt')
    args.fizz, args.mbt = args.fizz.resolve(), args.mbt.resolve()
    fizz_pins = dict(check.PIN, **{'mbt_gen.zip': 'eec23ba20eab09a1ffb6e77a93f77017ded75f77a773369986b9f0c3bb652d93'})
    for name, digest in fizz_pins.items():
        assert check.digest(args.fizz.parent / name) == digest, 'unrecognized FizzBee binary: ' + name
    for name, digest in MBT_PIN.items():
        assert check.digest(args.mbt / name) == digest, 'unrecognized MBT binary: ' + name
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    runtime = output / 'runtime'
    runtime.mkdir()
    for name in ('package.json', 'package-lock.json'):
        shutil.copyfile(HERE / name, runtime / name)
    if args.node_modules:
        (runtime / 'node_modules').symlink_to(args.node_modules.resolve(), target_is_directory=True)
        for package, version in json.loads((HERE / 'package.json').read_text())['dependencies'].items():
            assert json.loads((runtime / 'node_modules' / package / 'package.json').read_text())['version'] == version
    else:
        installed = run(['npm', 'ci', '--ignore-scripts', '--cache', str(output / 'npm-cache')], output / 'npm.log', cwd=runtime)
        assert installed.returncode == 0, installed.stdout
    model = runtime / 'conformance.fizz'
    shutil.copyfile(HERE / 'conformance.fizz', model)
    generated = run([sys.executable, args.fizz.parent / 'mbt_gen.zip', '--lang', 'typescript',
                     '--gen-adapter', '--out-dir', runtime, model], output / 'generation.log')
    assert generated.returncode == 0, generated.stdout
    shutil.copyfile(HERE / 'conformance-adapters.ts', runtime / 'conformance_adapters.ts')
    compiled = run([runtime / 'node_modules/.bin/tsc', '--target', 'ES2022', '--module', 'NodeNext',
                    '--moduleResolution', 'NodeNext', '--strict', '--skipLibCheck', '--outDir', runtime / 'dist',
                    *runtime.glob('*.ts')], output / 'compile.log', cwd=runtime)
    assert compiled.returncode == 0, compiled.stdout
    summary = {'pins': {'fizzbee': '0.5.3', 'mbt': '0.2.0', 'npm': '0.1.2'},
               'model_sha256': check.digest(HERE / 'conformance.fizz'), 'runs': []}
    try:
        if not args.mutation:
            for case in ([args.case] if args.case else CASES):
                summary['runs'].append(execute(args, runtime, output, case, args.seed, PROJECT))
        mutations = list(MUTATIONS) if args.all_mutations else [args.mutation] if args.mutation else []
        for mutation in mutations:
            case, original, replacement = MUTATIONS[mutation]
            product = output / ('controller-' + mutation)
            # Copy the product for intentional defects. No Git data, caches, or evidence.
            sys.path.insert(0, str(PROJECT / 'checks'))
            import test_p2p_delivery as fixture
            fixture.d.materialize(product, fixture.d.fs.snapshot(PROJECT))
            path = product / 'skills/productivity/deliver-issue/scripts/p2p_delivery.py'
            source = path.read_text()
            count = source.count(original)
            assert count == (2 if mutation == 'repair-bound-removed' else 1), (mutation, count)
            path.write_text(source.replace(original, replacement))
            save(product / 'mutation.json', {'path': str(path.relative_to(product)), 'before': original, 'after': replacement, 'count': count})
            summary['runs'].append(execute(args, runtime, output, case, args.seed, product, mutation))
        summary['result'] = 'PASS'
    except Exception as error:
        summary.update(result='FAIL', error=str(error))
        raise
    finally:
        save(output / 'summary.json', summary)
    print(f'PASS: {len(summary["runs"])} traces; worker replies are substitutes, not live host evidence.')


if __name__ == '__main__':
    main()
