#!/usr/bin/env python3
"""One fixture operation per MBT callback. Worker replies are substitutes only."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

PROJECT = Path(os.environ.get('P2P_REPO', Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(PROJECT / 'checks'))
import test_p2p_delivery as fixture

d = fixture.d
ROOT = Path(os.environ['P2P_TRACE_DIR'])
SOURCE = ROOT / 'source'
DIRECTORY = SOURCE / '.p2p/work/tiny'
CASE = os.environ['P2P_MBT_CASE']


def read(path):
    return json.loads(path.read_text())


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def state():
    path = DIRECTORY / 'delivery.json'
    return read(path) if path.exists() else None


def child():
    """Inject replies and boundary interruptions, then invoke the real CLI main."""
    settings = read(ROOT / 'command.json')
    fake = fixture.FakeTransport('exhausted' if CASE in ('repair-restart-exhaustion', 'blocked-failure') else 'success')
    if CASE == 'successful-repair' and not (state() or {}).get('repair_used'):
        fake.mode = 'exhausted'
    if CASE == 'uncertain-launch-restart':
        fake.mode = 'uncertain'
    d.launch = fake
    original_reserve = d.Delivery.reserve
    def reserve(self, stage, inputs, scratch):
        if stage == settings.get('stop_before'):
            os._exit(77)
        return original_reserve(self, stage, inputs, scratch)
    d.Delivery.reserve = reserve
    original_receipt = d.Delivery.receipt
    def receipt(self, attempt):
        if settings.get('pause_proof') and attempt['stage'] == 'proof':
            os._exit(77)
        return original_receipt(self, attempt)
    d.Delivery.receipt = receipt
    if settings.get('storage_failure'):
        original_retained = d.retained
        def retained(root, work, name, data):
            if name == 'proof.md':
                raise OSError('fixture interrupted report storage')
            return original_retained(root, work, name, data)
        d.retained = retained
    if settings.get('hold_lock'):
        original_run = d.Delivery.run
        def run(self):
            (ROOT / 'lock-held').write_text(str(os.getpid()))
            deadline = time.monotonic() + 20
            while not (ROOT / 'release-lock').exists():
                if time.monotonic() > deadline:
                    raise RuntimeError('overlap release timed out')
                time.sleep(.02)
            return original_run(self)
        d.Delivery.run = run
    # Mutation source is a copy of the real controller, installed by the runner.
    sys.exit(d.main(sys.argv[2:]))


def command(action='resume', **settings):
    write(ROOT / 'command.json', settings)
    args = [sys.executable, str(Path(__file__).resolve()), 'child', '--repo', str(SOURCE), action, 'work/tiny.md']
    if action == 'run':
        args += ['--comparison-base', (ROOT / 'base').read_text()]
        if CASE != 'unauthorized-before-dispatch':
            args += ['--authorize-local']
    return args


def invoke(action='resume', **settings):
    args = command(action, **settings)
    result = subprocess.run(args, text=True, capture_output=True, timeout=60)
    output = json.loads(result.stdout) if result.stdout.strip() else None
    assert result.returncode in (0, 1, 77), result.stderr + result.stdout
    if result.returncode != 77:
        assert output is not None, result.stderr
    return result.returncode, output, {'command': args, 'pid_kind': 'fresh controller subprocess',
                                     'exit': result.returncode, 'stdout': output, 'stderr': result.stderr}


def corrupt():
    saved = state()
    attempt = saved['attempts'][-1]
    folder = DIRECTORY / 'attempts' / attempt['id']
    if CASE == 'candidate-mutated-during-verification':
        (DIRECTORY / 'runtime/workspace/greet.py').write_text("print('mutated after launch')\n")
    elif CASE == 'incomplete-archive':
        # This is the actual retained comparison base, not the redundant bundle.
        write(DIRECTORY / 'base-manifest.json', [])
    elif CASE == 'late-stage-result':
        value = read(folder / 'exit.json')
        value['attempt_id'] = 'late-result-from-another-launch'
        write(folder / 'exit.json', value)
    elif CASE == 'duplicate-report-write':
        write(folder / 'report.json', {'status': 'conflicting existing write'})
    else:
        events = [json.loads(line) for line in (folder / 'events.jsonl').read_text().splitlines()]
        message = next(e['item'] for e in events if e.get('item', {}).get('type') == 'agent_message')
        report = json.loads(message['text'])
        if CASE == 'stale-identity':
            # Real earlier identity, before implementation changed the candidate.
            report['input_identity_json'] = json.dumps(saved['attempts'][2]['inputs'])
            assert json.loads(report['input_identity_json']) != attempt['inputs']
        elif CASE == 'mistyped-identity':
            report['input_identity_json'] = '{not-json'
        else:
            raise AssertionError('unsupported corruption: ' + CASE)
        message['text'] = json.dumps(report)
        (folder / 'events.jsonl').write_text(''.join(json.dumps(e) + '\n' for e in events))
        end = read(folder / 'exit.json')
        end['event_sha256'] = hashlib.sha256((folder / 'events.jsonl').read_bytes()).hexdigest()
        write(folder / 'exit.json', end)


def projection(code, saved):
    if saved is None:
        return f'{code}|ABSENT|0|0||0|0|0|0|1'
    attempts = saved['attempts']
    manifest = saved.get('candidate', {}).get('manifest', [])
    entries = {x['path']: x for x in manifest}
    generation = 0
    if 'greet.py' in entries:
        import base64
        content = base64.b64decode(entries['greet.py']['content_base64'])
        generation = 2 if b'repaired fixture' in content else 1
    verifiers = []
    expected_identity = {k: v for k, v in saved['candidate'].items() if k != 'manifest'}
    for name, passing in [('review', 'REVIEWED'), ('proof', 'PROVEN')]:
        record = saved.get('reports', {}).get(name)
        if not record:
            verifiers.append(0)
            continue
        report = read(DIRECTORY / record['path'])
        exact = json.loads(report['input_identity_json']) == expected_identity
        full = [row['id'] for row in report['requirements']] == ['R1']
        verifiers.append(generation if exact and full and report['status'] == passing and not report['gaps'] else -1)
    current = int(d.fs.snapshot(DIRECTORY / 'runtime/workspace') == manifest)
    return '|'.join(map(str, [code, saved['status'], len(attempts),
                             sum(a['status'] == 'complete' for a in attempts),
                             ','.join(sorted(saved.get('reports', {}))),
                             int(saved['repair_used']), generation, *verifiers, current]))


def main(action):
    if action == 'Init':
        # MBT initializes once per trace. Refuse accidental fixture reuse.
        ROOT.mkdir(parents=True, exist_ok=True)
        base = fixture.repo(SOURCE)
        (ROOT / 'base').write_text(base)
        if CASE == 'contested-dirty-file':
            (SOURCE / 'dirty').write_text('untouched\n')
        print('initialized')
        return
    before = state()
    detail = {}
    if action == 'Start':
        code, output, detail = invoke('run', stop_before='review')
    elif action == 'Review':
        code, output, detail = invoke(stop_before='proof')
    elif action == 'Proof':
        code, output, detail = invoke(pause_proof=True)
    elif action == 'Corrupt':
        corrupt()
        code, output = 0, None
    elif action == 'Restart':
        storage = CASE == 'interrupted-report-storage' and not (ROOT / 'storage-injected').exists()
        if storage:
            (ROOT / 'storage-injected').touch()
        code, output, detail = invoke(stop_before='review', storage_failure=storage)
    elif action == 'Inspect':
        code, output, detail = invoke('status')
        assert before == state(), 'read-only status changed saved state'
    elif action == 'Resume':
        code, output, detail = invoke(stop_before='review')
    elif action == 'Overlap':
        args = command(hold_lock=True, stop_before='proof')
        first = subprocess.Popen(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + 20
            while not (ROOT / 'lock-held').exists():
                assert first.poll() is None, 'first controller exited before acquiring lock'
                assert time.monotonic() < deadline, 'lock rendezvous timed out'
                time.sleep(.02)
            # Both processes remain live until the second has returned.
            loser_code, loser, loser_detail = invoke()
            assert loser_code == 1 and 'another controller holds' in loser['blocker'], loser
            assert state() == before, 'losing overlapping resume mutated persisted state'
        finally:
            (ROOT / 'release-lock').touch()
            stdout, stderr = first.communicate(timeout=60)
        code, output = first.returncode, json.loads(stdout) if stdout else None
        assert code == 77, stderr + stdout
        detail = {'winner_command': args, 'winner_pid': first.pid,
                  'loser': loser_detail, 'loser_state_unchanged': True}
    else:
        raise AssertionError(action)
    after = state()
    if output is not None:
        assert output['status'] in ('RUNNING', 'BLOCKED', 'REVIEWED_AND_PROVEN')
        if after is not None:
            for key in ('invocation_id', 'attempts', 'reports', 'repair_used'):
                assert output[key] == after[key], (key, output, after)
        else:
            assert output['status'] == 'BLOCKED'
    if before and after:
        assert before['invocation_id'] == after['invocation_id'], 'trace changed delivery invocation'
    if CASE == 'contested-dirty-file':
        assert (SOURCE / 'dirty').read_text() == 'untouched\n'
    # Full real state and public output are retained before MBT compares its oracle.
    observed = projection(code, after)
    trace = ROOT / 'actions.jsonl'
    with trace.open('a') as stream:
        stream.write(json.dumps({'action': action, 'observed': observed, 'controller': detail,
                                'before': before, 'after': after}) + '\n')
    print(observed)


if __name__ == '__main__':
    if sys.argv[1] == 'child':
        child()
    else:
        main(sys.argv[1])
