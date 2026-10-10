#!/usr/bin/env python3
"""Deterministic fixture transport tests. These are NOT live host evidence."""
import argparse
import base64
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/productivity/deliver-issue/scripts'
FIXTURE_SKILLS = Path(__file__).resolve().parent / 'fixtures/skills'
sys.path.insert(0, str(SCRIPTS))
import p2p_delivery as d

CONTRACT = '''# Acceptance contract: tiny

Contract revision: v1
Source: [Specification](../../../spec.txt)

Intended outcome: greet.py prints hello.

## Acceptance matrix

| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | spec.txt | greet.py prints hello and exits zero. | Wrong text or failure is rejected. | python3 greet.py | hello plus newline and exit zero | Run python3 greet.py and assert exact output and status. | planned |

## Unresolved gaps

None.
'''


@contextlib.contextmanager
def fixture_host():
    """Supply version/skill discovery for offline fixtures; never launch a model."""
    executable = Path(__file__).resolve().parent / 'fixtures/codex'
    original_which = shutil.which
    original_run = subprocess.run

    def which(name, *args, **kwargs):
        return str(executable) if name == 'codex' else original_which(name, *args, **kwargs)

    def installed(name):
        # Small, real instruction packages exercise pinning and portable restore
        # without pretending that fixture responses followed production skills.
        path = FIXTURE_SKILLS / name / 'SKILL.md'
        return {'path': str(path), 'sha256': d.fs.digest(path.read_bytes())}

    def run(args, *positional, **kwargs):
        if args and str(args[0]) == str(executable):
            if list(args[1:]) != ['--version']:
                raise AssertionError('offline fixture requires injected stage transport')
            return subprocess.CompletedProcess(args, 0, 'FIXTURE codex 0.0.0 (not live host evidence)\n', '')
        return original_run(args, *positional, **kwargs)

    with patch.object(d.platform, 'system', lambda: 'Darwin'), \
            patch.object(d.shutil, 'which', side_effect=which), \
            patch.object(d.subprocess, 'run', side_effect=run), \
            patch.object(d, 'installed_skill', side_effect=installed):
        yield


def repo(path):
    path.mkdir()
    subprocess.run(['git', 'init', '-q', str(path)], check=True)
    d.fs.git(path, 'config', 'user.name', 'Fixture')
    d.fs.git(path, 'config', 'user.email', 'fixture@localhost')
    (path / '.gitignore').write_text('/.p2p/\n')
    (path / 'spec.txt').write_text('A CLI prints hello followed by a newline and exits zero.\n')
    subprocess.run(['git', '-C', str(path), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(path), 'commit', '-qm', 'Fixture base'], check=True)
    (path / 'work').mkdir()
    (path / '.p2p/work/tiny/contract.md').parent.mkdir(parents=True)
    (path / '.p2p/work/tiny/contract.md').write_text(CONTRACT)
    base = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
    subprocess.run(['git', '-C', str(path), 'branch', 'delivery-target', base], check=True)
    return base


def apply_candidate(root, workspace):
    records = list((workspace / '.p2p/work').glob('*/candidate.json'))
    if len(records) != 1:
        raise AssertionError('expected one captured product candidate')
    candidate = json.loads(records[0].read_text())
    entries = {entry['path']: entry for entry in d.fs.snapshot(workspace)}
    current = {entry['path']: entry for entry in d.fs.snapshot(root)}
    for change in candidate['changes']:
        path = change['path']
        target = root / path
        if change['state'] == 'deleted':
            if target.is_symlink() or target.is_file():
                target.unlink()
            current.pop(path, None)
        else:
            entry = entries[path]
            if current.get(path) != entry:
                if target.is_symlink() or target.is_file():
                    target.unlink()
                d.materialize(root, [entry])
            current[path] = entry


def p2p_metrics(root, tree, slug):
    prefix = f'.p2p/work/{slug}/'
    records = d.fs.git(root, 'ls-tree', '-rlz', '--full-tree', tree).split(b'\0')
    entries = []
    for record in filter(None, records):
        metadata, raw_path = record.split(b'\t', 1)
        mode, kind, oid, size = metadata.decode().split()
        path = raw_path.decode()
        if path.startswith(prefix) and kind == 'blob':
            entries.append((path, int(size)))
    return {'files': len(entries), 'bytes': sum(size for _, size in entries), 'paths': entries}


def print_p2p_footprint(scenario, before_tree, before, after_tree, after, **facts):
    metric = lambda tree, value: {'tree': tree, 'files': value['files'],
                                  'logical_bytes': value['bytes'], 'paths': value['paths']}
    print('P2P_FOOTPRINT=' + json.dumps({'scenario': scenario,
          'before': metric(before_tree, before), 'after': metric(after_tree, after), **facts},
          sort_keys=True))


def p2p_repo(path, work='work/p2p-self-delivery.md'):
    source = Path(__file__).resolve().parents[1]
    subprocess.run(['git', 'clone', '--shared', '--quiet', str(source), str(path)], check=True, capture_output=True)
    d.fs.git(path, 'config', 'user.name', 'Fixture')
    d.fs.git(path, 'config', 'user.email', 'fixture@localhost')
    ignore = path / '.gitignore'
    old_ignore = ignore.read_bytes() if ignore.exists() else b''
    if '/.p2p/' not in ignore.read_text().splitlines():
        separator = b'' if not old_ignore or old_ignore.endswith(b'\n') else b'\n'
        ignore.write_bytes(old_ignore + separator + b'/.p2p/\n')
    d.fs.setup(path)
    if ignore.read_bytes() != old_ignore:
        d.fs.git(path, 'add', '--', '.gitignore')
        d.fs.git(path, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                 'commit', '-qm', 'Fixture local P2P ignore rule')
    base = d.fs.full_commit(path, 'HEAD')
    d.fs.git(path, 'update-ref', 'refs/heads/delivery-target', base)
    (path / 'spec.txt').write_text('A CLI prints hello followed by a newline and exits zero.\n')
    (path / 'work').mkdir(exist_ok=True)
    (path / work).write_text(CONTRACT.replace('../../../spec.txt', '../spec.txt'))
    return base


def tree_blob_bytes(root, tree):
    records = d.fs.git(root, 'ls-tree', '-rlz', '--full-tree', tree).split(b'\0')
    return sum(int(record.split(b'\t', 1)[0].decode().split()[3]) for record in filter(None, records))


class FakeTransport:
    """Clearly labeled fixture that supplies host-shaped records, never host proof."""
    def __init__(self, mode='success', output_path='greet.py'):
        self.mode, self.calls, self.prompts = mode, [], []
        self.messages = []
        self.output_path = output_path
        self.on_stage = None

    def __call__(self, args, prompt, event_path, error_path, deadline, idle_seconds=None):
        attempt = json.loads((event_path.parent / 'launch.json').read_text())
        inputs = attempt['inputs']
        stage = 'preflight' if 'probe_sha256' in inputs else attempt['stage']
        self.calls.append(stage)
        self.prompts.append((stage, prompt))
        workspace = Path(args[args.index('-C') + 1])
        if self.on_stage:
            self.on_stage(stage)
        if self.mode == 'uncertain' and stage == 'implementation':
            raise OSError('fixture crash after durable reservation')
        events = [{'type': 'thread.started', 'thread_id': 'fixture-' + __import__('uuid').uuid4().hex}]
        if stage == 'preflight':
            probe = Path(prompt.split('`python3 ', 1)[1].split('`')[0])
            protected = __import__('ast').literal_eval(probe.read_text().split('paths = ',1)[1].split('\n')[0])
            observation = {p + ':' + m: 'denied' for p in protected for m in ('absolute','symlink','subprocess')}
            observation.update(scratch='ok', network='denied')
            output = 'P2P_BOUNDARY=' + json.dumps(observation)
            report = 'FIXTURE host preflight, not live evidence'
            if 'task_readiness' in inputs:
                readiness_command = 'FIXTURE python3 --version'
                readiness_output = 'Python 3.11 fixture runtime available'
                events.append({'type': 'item.completed', 'item': {'type': 'command_execution',
                    'command': readiness_command, 'aggregated_output': readiness_output, 'exit_code': 0}})
                report = json.dumps({'status': 'READY', 'input_identity_json': json.dumps(inputs),
                    'checks': [{'kind': 'runtime', 'prerequisite': 'Python 3.11', 'requirement_id': 'R1',
                                'command': readiness_command, 'observation': readiness_output, 'available': True}],
                    'reason': 'Fixture runtime is available; greet.py is the product to implement, not a prerequisite.',
                    'missing_input': '', 'expected_result': ''})
        elif stage == 'diagnosis':
            blocked = self.mode in ('blocked', 'exhausted')
            report = json.dumps({'status': 'BLOCKED' if blocked else 'ACTIONABLE',
                'input_identity_json': json.dumps(inputs),
                'action': 'none' if blocked else ('evidence' if self.mode == 'evidence' else 'implementation'),
                'approach': '' if blocked else (
                    'Inspect partial recovery step ' + str(self.calls.count('diagnosis'))
                    if self.mode == 'partial-repair' else
                    'Inspect the actual local seam and replace the failed approach.'),
                'reason': 'Fixture independent diagnosis.',
                'strategy_changed': not blocked and (self.calls.count('diagnosis') == 1 or self.mode == 'partial-repair'),
                'capability_check': '' if blocked else 'P2P_RECOVERY_CAPABILITY=fixture local CLI available',
                'missing_input': 'configured command `python3 greet.py`' if blocked else '',
                'expected_result': 'exit zero and print `hello\\n`' if blocked else ''})
            output = 'P2P_RECOVERY_CAPABILITY=fixture local CLI available'
        elif stage == 'planning':
            proposed = CONTRACT.replace('Contract revision: v1', 'Contract revision: v2')
            if self.mode == 'planning-weaken':
                proposed = proposed.replace('R1', 'R2')
            report = json.dumps({'input_identity_json': json.dumps(inputs), 'contract': proposed,
                                 'reason': 'Fixture source-preserving reconciliation.'})
            output = 'FIXTURE planning'
        elif stage == 'planning-audit':
            report = json.dumps({'input_identity_json': json.dumps(inputs),
                **{key: self.mode != 'planning-reject' for key in ('preserves_outcome', 'preserves_constraints',
                    'source_reconciled', 'requirements_complete')}, 'reason': 'Fixture independent audit.'})
            output = 'FIXTURE planning audit'
        else:
            if stage in ('implementation','repair'):
                (workspace / self.output_path).write_text("print('hello')\n" + ("# repaired fixture\n" if stage == 'repair' else ''))
            status = {'implementation':'IMPLEMENTED','repair':'REPAIRED','review':'REVIEWED','proof':'PROVEN'}[stage]
            gap = self.mode in ('repair','exhausted') and stage == 'proof' and (self.mode == 'exhausted' or self.calls.count('proof') == 1)
            gap |= self.mode in ('multi-repair', 'evidence') and stage == 'proof' and self.calls.count('proof') <= 2
            if gap:
                status = 'NOT PROVEN'
            row = {'id':'R1','verdict':'proven' if stage == 'proof' else 'reviewed',
                   'observation':'Fixture observes hello newline and exit zero.',
                   'evidence':[{'assertion':'stdout equals hello newline and status zero',
                                'observation':'fixture output hello newline, status zero',
                                'artifact':'FIXTURE command python3 greet.py; stdout hello\\n; exit 0'}]}
            if stage == 'review': row = {'id':'R1','observation':'Fixture observes hello newline and exit zero.'}
            report = {'status':status, 'input_identity_json':json.dumps(inputs),
                      'requirements':[row],
                      'gaps':['fixture gap'] if gap else [],
                      'learning_candidates':[]}
            if self.mode == 'learning-candidate' and stage == 'implementation':
                report['learning_candidates'] = [{
                    'scope':'Python CLI output checks',
                    'lesson':'Prefer an exact stdout assertion over exit-code-only coverage for this behavior.',
                    'evidence':'The implementation stage exercised greet.py and observed exact hello newline output.',
                    'uncertainty':'This is candidate advice until retrospect checks it against final review and proof.'
                }]
            if self.mode in ('partial-repair','partial-implementation') and stage == 'implementation':
                report.update(status='PARTIAL', gaps=['original implementation gap'])
            if self.mode == 'partial-repair' and stage == 'repair' and self.calls.count('repair') == 1:
                report.update(status='PARTIAL', gaps=['remaining repair gap'])
            if stage == 'review':
                report.update(findings=[], coverage='R1; inspected greet.py and the delivery checks.',
                              checks=[{'command':'python3 greet.py','result':'passed',
                                       'observation':'Fixture output hello newline, exit zero.'}],
                              limitations=['Fixture transport does not establish live-host behavior.'],
                              missing_input='', expected_result='')
                if self.mode == 'blocked':
                    report.update(status='BLOCKED', missing_input='configured command `python3 greet.py`',
                                  expected_result='exit zero and print `hello\\n`')
                if self.mode in ('review-plan-handoff', 'planning-reject', 'planning-weaken') and self.calls.count('review') == 1:
                    report.update(status='CHANGES NEEDED', findings=[{
                        'id':'F1','source':'R2','axis':'Contract fidelity','location':'.p2p/work/tiny/contract.md',
                        'evidence':'The fixture requires a contract decision.',
                        'consequence':'Implementation must wait for the agreement.',
                        'correction':'Revise and approve the acceptance contract.',
                        'handoff':'plan-acceptance'}])
            else: report['details'] = '# ' + status + '\n\nFIXTURE ONLY; full R1 observation retained.'
            if self.mode == 'review-proof-verdict' and stage == 'review':
                row['verdict'] = 'proven'
            if self.mode == 'review-conflict' and stage == 'review':
                report['findings'] = [{'id':'F1','source':'R1','axis':'Contract fidelity',
                                      'location':'greet.py:1','evidence':'Fixture found an omitted requirement.',
                                      'consequence':'The reviewed outcome is incomplete.',
                                      'correction':'Implement the missing behavior.',
                                      'handoff':'implement-contract'}]
            if self.mode == 'review-prose-conflict' and stage == 'review':
                report['details'] = '# CHANGES NEEDED\n\nF1: contradictory free-text summary'
            if self.mode == 'review-invalid-status' and stage == 'review':
                report['status'] = 'PROVEN'
            if self.mode == 'review-blank-observation' and stage == 'review':
                row['observation'] = '  \n'
            if self.mode == 'omit' and stage == 'proof': report['requirements'] = []
            if self.mode == 'stale' and stage == 'proof':
                report['input_identity_json'] = json.dumps(dict(inputs, work_item_sha256='0'*64))
            if stage in ('implementation', 'repair', 'review', 'proof'):
                # Explicitly OFFLINE fixture trace; not a real reviewer judgment.
                product = Path(prompt.split('workspace ', 1)[1].split('. ', 1)[0])
                # The controller's exact admitted agreement paths include not
                # only this contract/spec, but parent sources and transferred
                # routing inputs. Reuse its identity boundary in the *fixture*
                # instead of inventing a second coverage scope.
                admission = json.loads((event_path.parents[2] / 'admission.json').read_text())
                excluded = admission['agreement_paths']
                manifest = d.fs.snapshot(product, exclude=excluded)
                changed = d.fs.tree_changes(d.fs.snapshot(product, inputs['comparison_base'], exclude=excluded), manifest)
                paths = [item['path'] for item in changed]
                report['coverage_trace'] = {
                    'requirements': [{'id': row['id'], 'paths': paths,
                                      'existing': not bool(paths), 'evidence': ['row']}
                                     for row in report['requirements']],
                    'supporting_changes': [],
                    **({'inspected_paths': sorted({item['path'] for item in manifest} & set(paths))}
                       if stage == 'review' else {}),
                }
            output = 'hello\n'
            report = json.dumps(report)
        self.messages.append((stage, report))
        events += [{'type':'item.completed','item':{'type':'command_execution','command':'FIXTURE python3 greet.py',
                                                    'aggregated_output':output,'exit_code':0}},
                   {'type':'item.completed','item':{'type':'agent_message','text':report}},
                   {'type':'turn.completed','usage':{'input_tokens':7,'output_tokens':3}}]
        event_path.write_text(''.join(json.dumps(e)+'\n' for e in events))
        error_path.write_text('FIXTURE TRANSPORT\n')
        return {'exit_code':0,'outcome':'finished','finished':d.now(),'elapsed_seconds':0.01}


class RuntimeRequirementTests(unittest.TestCase):
    def test_controller_rejects_python_before_311_clearly(self):
        stderr = io.StringIO()
        with patch.object(d.sys, 'version_info', (3, 10)), contextlib.redirect_stderr(stderr):
            self.assertEqual(d.main([]), 2)
        self.assertIn('Python 3.11 or newer is required', stderr.getvalue())


class GenerationTreeTests(unittest.TestCase):
    def test_generation_batches_exact_blobs_without_changing_refs_or_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'source'
            repo(root)
            original = d.fs.snapshot(root)
            refs = d.fs.git(root, 'for-each-ref')
            index = (root / '.git/index').read_bytes()
            manifest = [{'path': f'new-{i}.bin', 'type': 'file', 'mode': '100644',
                         'content_base64': base64.b64encode(bytes([i]) + b'\0\nblob\ndone\n').decode()}
                        for i in range(24)]
            manifest.extend([
                {'path': 'empty', 'type': 'file', 'mode': '100755', 'content_base64': ''},
                {'path': 'line\nbreak\tø.txt', 'type': 'file', 'mode': '100644',
                 'content_base64': base64.b64encode(b'exact text').decode()},
                {'path': 'link', 'type': 'symlink', 'mode': '120000', 'target': 'line\nbreak\tø.txt'}])
            with patch.object(d.subprocess, 'run', wraps=d.subprocess.run) as processes:
                tree = d.git_generation_tree(root, manifest)
            self.assertLessEqual(processes.call_count, 5, 'generation cost must not spawn once per file')
            self.assertEqual(d.fs.snapshot(root, tree), sorted(manifest, key=lambda entry: entry['path']))
            self.assertEqual(d.fs.git(root, 'for-each-ref'), refs)
            self.assertEqual((root / '.git/index').read_bytes(), index)
            self.assertEqual(d.fs.snapshot(root), original)
            self.assertEqual(list((root / '.git/p2p-indexes').iterdir()), [])


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        test_home = Path(self.temp.name) / 'home'
        test_home.mkdir()
        self.home_patch = patch.dict(os.environ, {'HOME': str(test_home)})
        self.home_patch.start()
        self.root = Path(self.temp.name) / 'source'
        self.base = repo(self.root)
        self.fake = FakeTransport()
        self.patch = patch.object(d, 'launch', self.fake)
        self.patch.start()
        self.host = fixture_host()
        self.host.__enter__()

    def tearDown(self):
        self.patch.stop(); self.host.__exit__(None, None, None); self.home_patch.stop(); self.temp.cleanup()

    def cli(self, action='run', *extra):
        return self.cli_item('.p2p/work/tiny/contract.md', action, *extra)

    def cli_item(self, work, action='run', *extra):
        args = ['--repo', str(self.root), action, work]
        if action == 'run':
            args += ['--comparison-base', self.base, '--authorize-local']
            if not (self.root / '.p2p/work/parent/slicing.md').exists():
                args += ['--destination', 'delivery-target']
        output = io.StringIO()
        with contextlib.redirect_stdout(output): code = d.main(args + list(extra))
        return code, json.loads(output.getvalue())

    def run_root(self, root, work, base, action='run', *extra):
        args = ['--repo', str(root), action, work]
        if action == 'run':
            args += ['--comparison-base', base, '--authorize-local', '--destination', 'delivery-target']
        output = io.StringIO()
        with contextlib.redirect_stdout(output): code = d.main(args + list(extra))
        return code, json.loads(output.getvalue())

    def state(self):
        return json.loads((d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'delivery.json').read_text())

    def runtime(self, root=None, work='.p2p/work/tiny/contract.md'):
        return d.execution_runtime(root or self.root, work)

    def assert_candidate_workspace_retained(self, local):
        root = local.parents[2]
        runtime = d.execution_runtime(root, f'.p2p/work/{local.name}/contract.md')
        self.assertTrue((runtime / 'workspace').is_dir())
        self.assertTrue((runtime / 'repository.git').is_dir())

    def complete_and_cleanup(self):
        code, value = self.cli()
        self.assertEqual(code, 0, value)
        self.assertEqual(value['status'], 'REVIEWED_AND_PROVEN')
        self.assertTrue((self.root / '.p2p/work/tiny').is_dir())
        source_key = self.state()['source_tree_key']
        code, cleaned = self.cli('cleanup')
        self.assertEqual(code, 0, cleaned)
        local = d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        self.assert_candidate_workspace_retained(local)
        self.assertFalse((local / 'attempts').exists())
        self.assertFalse((local / 'delivery.json').exists())
        self.assertEqual(d.fs.snapshot_key(d.fs.snapshot(self.root)), source_key)
        self.assertTrue((d.delivery_paths(self.root, '.p2p/work/tiny/contract.md')[1] / 'delivery.json').is_file())
        return cleaned

    def run_without_destination(self):
        output = io.StringIO()
        args = ['--repo', str(self.root), 'run', '.p2p/work/tiny/contract.md',
                '--comparison-base', self.base, '--authorize-local']
        with contextlib.redirect_stdout(output):
            code = d.main(args)
        return code, json.loads(output.getvalue())

    def test_migration_guidance_covers_legacy_state_without_history_rewrite(self):
        guide = (Path(__file__).resolve().parents[1] / 'docs/p2p-state-migration.md').read_text()
        for promised in ("`.p2p/**`", "P2P-owned", "equivalent P2P records",
                         "git rm", "without rewriting", "project-owned paths"):
            self.assertIn(promised, guide)

        legacy = self.root
        (legacy / '.p2p/work/legacy').mkdir(parents=True)
        (legacy / '.p2p/work/legacy/candidate.json').write_text('{"legacy":true}\n')
        (legacy / 'work/legacy.md').write_text('P2P contract\n')
        (legacy / 'work/project-plan.md').write_text('Project-authored plan\n')
        (legacy / 'p2p-state.json').write_text('{"legacy":true}\n')
        d.fs.git(legacy, 'add', '-f', '--', '.p2p/work/legacy/candidate.json')
        d.fs.git(legacy, 'add', '--', 'work/legacy.md', 'work/project-plan.md', 'p2p-state.json')
        d.fs.git(legacy, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                 'commit', '-qm', 'Add legacy P2P state')
        old_head = d.fs.full_commit(legacy, 'HEAD')

        backup = Path(self.temp.name) / 'local-backup'
        for relative in ('.p2p/work/legacy', 'work/legacy.md', 'p2p-state.json'):
            source, target = legacy / relative, backup / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, target, symlinks=True)
            else:
                shutil.copy2(source, target, follow_symlinks=False)
        d.fs.git(legacy, 'rm', '-r', '--', '.p2p/work/legacy', 'work/legacy.md', 'p2p-state.json')
        d.fs.git(legacy, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                 'commit', '-qm', 'Move P2P state out of the current tree')

        new_head = d.fs.full_commit(legacy, 'HEAD')
        self.assertNotEqual(old_head, new_head)
        self.assertEqual(d.fs.git(legacy, 'rev-parse', 'HEAD^').decode().strip(), old_head)
        self.assertEqual(set(d.fs.git(legacy, 'ls-files').decode().splitlines()),
                         {'spec.txt', '.gitignore', 'work/project-plan.md'})
        self.assertTrue((backup / '.p2p/work/legacy/candidate.json').is_file())
        self.assertEqual((backup / 'work/legacy.md').read_text(), 'P2P contract\n')
        self.assertTrue((backup / 'p2p-state.json').is_file())
        self.assertEqual(d.fs.git(legacy, 'cat-file', '-e', old_head + ':.p2p/work/legacy/candidate.json'), b'')
        self.assertEqual(d.fs.git(legacy, 'cat-file', '-e', old_head + ':work/legacy.md'), b'')

    def test_clean_project_delivery_uses_local_contract_and_records(self):
        root = Path(self.temp.name) / 'clean'
        root.mkdir()
        d.fs.git(root, 'init', '-q')
        d.fs.git(root, 'config', 'user.name', 'Fixture')
        d.fs.git(root, 'config', 'user.email', 'fixture@localhost')
        (root / '.gitignore').write_text('/.p2p/\n')
        (root / 'spec.txt').write_text('A CLI prints hello followed by a newline and exits zero.\n')
        d.fs.git(root, 'add', '.gitignore', 'spec.txt')
        d.fs.git(root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                 'commit', '-qm', 'Clean project base')
        base = d.fs.full_commit(root, 'HEAD')
        d.fs.git(root, 'branch', 'delivery-target', base)
        agreement = d.agreement_root(root, '.p2p/work/tiny/contract.md')
        (agreement / 'work').mkdir(parents=True)
        source = agreement / 'work/tiny-source.md'
        source.write_text('Imported issue source text.\n')
        contract = CONTRACT.replace('Source: [Specification](../../../spec.txt)',
                                    'Source: [Imported issue #46](../../../work/tiny-source.md)')
        contract_sha = d.fs.digest(contract.encode())
        (agreement / '.p2p/work/tiny/contract.md').parent.mkdir(parents=True, exist_ok=True)
        (agreement / '.p2p/work/tiny/contract.md').write_text(contract)
        (agreement / 'spec.txt').write_text((root / 'spec.txt').read_text())

        code, value = self.run_root(root, '.p2p/work/tiny/contract.md', base)
        self.assertEqual(code, 0, value)
        self.assertEqual(value['status'], 'REVIEWED_AND_PROVEN')
        local = d.local_directory(root, '.p2p/work/tiny/contract.md')
        apply_candidate(root, d.execution_runtime(root, '.p2p/work/tiny/contract.md') / 'workspace')
        d.fs.git(root, 'add', '--', 'greet.py')
        d.fs.git(root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                 'commit', '-qm', 'Apply product candidate')
        code, cleaned = self.run_root(root, '.p2p/work/tiny/contract.md', base, 'cleanup')
        self.assertEqual(code, 0, cleaned)
        self.assertEqual(cleaned['status'], 'REVIEWED_AND_PROVEN')
        self.assert_candidate_workspace_retained(local)
        self.assertFalse((local / 'delivery.json').exists())
        self.assertFalse((root / 'work').exists())
        self.assertFalse((root / 'specs').exists())
        self.assertTrue((root / '.p2p/work/tiny/artifacts/delivery.json').is_file())
        self.assertEqual([item['path'] for item in value['candidate']['changes']], ['greet.py'])
        tree = d.fs.git(root, 'ls-tree', '-r', '--name-only', 'HEAD').decode().splitlines()
        self.assertEqual(set(tree), {'.gitignore', 'spec.txt', 'greet.py'})
        self.assertEqual(d.fs.git(root, 'diff', '--name-only', base, 'HEAD').decode().splitlines(), ['greet.py'])
        artifacts = d.delivery_paths(root, '.p2p/work/tiny/contract.md')[1]
        candidate_path, delivery_path = artifacts / 'candidate.json', artifacts / 'delivery.json'
        review_path, proof_path = artifacts / 'review.md', artifacts / 'proof.md'
        candidate = json.loads(candidate_path.read_text())
        delivery = json.loads(delivery_path.read_text())
        self.assertEqual(delivery['contract']['sha256'], contract_sha)
        self.assertEqual(delivery['comparison_base'], base)
        self.assertEqual(delivery['candidate_key'], candidate['key'])
        for report_path in (review_path, proof_path):
            report = report_path.read_text()
            self.assertIn(contract_sha, report)
            self.assertIn(base, report)
            self.assertIn(candidate['key'], report)
        self.assertEqual(delivery['review_sha256'], d.fs.digest(review_path.read_bytes()))
        self.assertEqual(delivery['proof_sha256'], d.fs.digest(proof_path.read_bytes()))
        self.assertEqual(sorted(path.name for path in artifacts.iterdir()),
                         ['candidate.json', 'delivery.json', 'proof.md', 'review.md'])
        self.assertFalse((agreement / '.p2p/work/tiny/contract.md').exists())
        self.assertFalse(source.exists())

    def test_final_footprint_counts_replaced_record_size(self):
        artifacts = d.delivery_paths(self.root, '.p2p/work/tiny/contract.md')[1]
        artifacts.mkdir(parents=True)
        (artifacts / 'candidate.json').write_bytes(b'old')
        with self.assertRaisesRegex(ValueError, 'local P2P footprint exceeds limits'):
            d.check_final_footprint(self.root, '.p2p/work/tiny/contract.md', {'candidate.json': b'x' * 262145})

    def test_symlinked_local_storage_roots_block_reads_and_writes(self):
        local = d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        self.assertTrue(local.is_dir())
        outside = Path(self.temp.name) / 'outside'
        outside.mkdir()
        for name in ('agreement', 'artifacts'):
            (local / name).symlink_to(outside, target_is_directory=True)
            expected = 'P2P agreement path is not a directory' if name == 'agreement' else 'repo-local P2P artifacts'
            with self.assertRaisesRegex(ValueError, expected):
                d.delivery_paths(self.root, '.p2p/work/tiny/contract.md')
            (local / name).unlink()

    def test_unsliced_admission_requires_explicit_or_unambiguous_upstream(self):
        code, value = self.run_without_destination()
        self.assertEqual(code, 1)
        self.assertIn('needs --destination or one configured upstream', value['blocker'])
        self.assertEqual(self.fake.calls, [])

        branch = d.fs.git(self.root, 'symbolic-ref', '--quiet', '--short', 'HEAD').decode().strip()
        d.fs.git(self.root, 'config', '--add', f'branch.{branch}.remote', 'origin')
        d.fs.git(self.root, 'config', '--add', f'branch.{branch}.remote', 'other')
        d.fs.git(self.root, 'config', '--add', f'branch.{branch}.merge', 'refs/heads/main')
        code, value = self.run_without_destination()
        self.assertEqual(code, 1)
        self.assertIn('unambiguous configured upstream', value['blocker'])
        self.assertEqual(self.fake.calls, [])
        self.assertEqual(self.fake.messages, [])
        local = d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        self.assertFalse((local / 'delivery.json').exists())
        self.assertFalse((self.runtime() / 'attempts').exists())

        d.fs.git(self.root, 'config', '--unset-all', f'branch.{branch}.remote')
        d.fs.git(self.root, 'config', '--add', f'branch.{branch}.remote', 'origin')
        d.fs.git(self.root, 'update-ref', 'refs/remotes/origin/main', self.base)
        code, value = self.run_without_destination()
        self.assertEqual(code, 0, value)
        self.assertEqual(value['routing']['destination'], 'origin/main')
        self.assertEqual(value['routing']['selection'], 'upstream')
        self.assertEqual(value['destination_observation']['relation'], 'unchanged')

    def test_unsliced_stale_explicit_base_names_current_destination(self):
        tree = d.fs.git(self.root, 'rev-parse', self.base + '^{tree}').decode().strip()
        newer = subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                    '-c', 'user.email=fixture@localhost', 'commit-tree', tree, '-p', self.base],
                    input=b'Advance target\n').decode().strip()
        d.fs.git(self.root, 'update-ref', 'refs/heads/delivery-target', newer)
        output = io.StringIO()
        args = ['--repo', str(self.root), 'run', '.p2p/work/tiny/contract.md', '--comparison-base', self.base,
                '--destination', 'delivery-target', '--authorize-local']
        with contextlib.redirect_stdout(output):
            code = d.main(args)
        value = json.loads(output.getvalue())
        self.assertEqual(code, 1)
        self.assertIn('destination delivery-target is currently at ' + newer, value['blocker'])
        self.assertIn('--comparison-base ' + newer, value['blocker'])
        self.assertEqual(self.fake.calls, [])

    def test_fully_qualified_destination_rejects_revision_expressions(self):
        tree = d.fs.git(self.root, 'rev-parse', self.base + '^{tree}').decode().strip()
        newer = subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                    '-c', 'user.email=fixture@localhost', 'commit-tree', tree, '-p', self.base],
                    input=b'Advance target\n').decode().strip()
        d.fs.git(self.root, 'update-ref', 'refs/heads/delivery-target', newer)
        d.fs.git(self.root, 'update-ref', 'refs/remotes/origin/delivery-target', newer)

        for destination in ('refs/heads/delivery-target~1', 'refs/remotes/origin/delivery-target~1'):
            output = io.StringIO()
            args = ['--repo', str(self.root), 'run', '.p2p/work/tiny/contract.md', '--comparison-base', self.base,
                    '--destination', destination, '--authorize-local']
            with contextlib.redirect_stdout(output):
                code = d.main(args)
            value = json.loads(output.getvalue())
            self.assertEqual(code, 1)
            self.assertIn('invalid workflow destination', value['blocker'])
            self.assertEqual(self.fake.calls, [])

    def test_explicit_remote_tracking_destination_resumes_from_stored_ref(self):
        d.fs.git(self.root, 'update-ref', 'refs/remotes/origin/main', self.base)
        output = io.StringIO()
        args = ['--repo', str(self.root), 'run', '.p2p/work/tiny/contract.md', '--comparison-base', self.base,
                '--destination', 'refs/remotes/origin/main', '--authorize-local']
        with contextlib.redirect_stdout(output):
            code = d.main(args)
        value = json.loads(output.getvalue())
        self.assertEqual(code, 0, value)
        self.assertEqual(value['routing']['destination'], 'origin/main')
        self.assertEqual(value['routing']['target_ref'], 'refs/remotes/origin/main')
        calls = self.fake.calls[:]

        tree = d.fs.git(self.root, 'rev-parse', self.base + '^{tree}').decode().strip()
        newer = subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                    '-c', 'user.email=fixture@localhost', 'commit-tree', tree, '-p', self.base],
                    input=b'Advance remote-tracking destination\n').decode().strip()
        d.fs.git(self.root, 'update-ref', 'refs/remotes/origin/main', newer)
        code, resumed = self.cli('resume')
        self.assertEqual(code, 0, resumed)
        self.assertEqual(resumed['comparison_base'], self.base)
        self.assertEqual(resumed['destination_observation']['observed_tip'], newer)
        self.assertEqual(resumed['destination_observation']['relation'], 'fast-forward')
        self.assertEqual(self.fake.calls, calls)

    def test_non_fast_forward_and_missing_destination_do_not_invalidate_acceptance(self):
        self.assertEqual(self.cli()[0], 0)
        original = self.state()
        calls = self.fake.calls[:]
        tree = d.fs.git(self.root, 'rev-parse', self.base + '^{tree}').decode().strip()
        unrelated = subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                    '-c', 'user.email=fixture@localhost', 'commit-tree', tree],
                    input=b'Non-fast-forward target\n').decode().strip()
        d.fs.git(self.root, 'update-ref', 'refs/heads/delivery-target', unrelated)
        code, value = self.cli('resume')
        self.assertEqual(code, 0, value)
        self.assertEqual(value['destination_observation']['relation'], 'non-fast-forward')
        self.assertEqual(value['destination_observation']['observed_tip'], unrelated)
        self.assertEqual(value['comparison_base'], self.base)
        self.assertEqual(value['candidate'], d.identity(original['candidate']))
        d.fs.git(self.root, 'update-ref', '-d', 'refs/heads/delivery-target')
        code, value = self.cli('resume')
        self.assertEqual(code, 0, value)
        self.assertEqual(value['destination_observation']['relation'], 'unavailable')
        self.assertIsNone(value['destination_observation']['observed_tip'])
        self.assertEqual(value['candidate'], d.identity(original['candidate']))
        self.assertEqual(self.fake.calls, calls)

    def test_busy_destination_moves_repeatedly_without_refreshing_completed_stages(self):
        self.assertEqual(self.cli()[0], 0)
        original = self.state()
        calls = self.fake.calls[:]
        tip = self.base
        for message in ('B', 'C', 'D'):
            tree = d.fs.git(self.root, 'rev-parse', tip + '^{tree}').decode().strip()
            tip = subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                        '-c', 'user.email=fixture@localhost', 'commit-tree', tree, '-p', tip],
                        input=(message + '\n').encode()).decode().strip()
            d.fs.git(self.root, 'update-ref', 'refs/heads/delivery-target', tip)
            code, value = self.cli('resume')
            self.assertEqual(code, 0, value)
            self.assertEqual(value['comparison_base'], self.base)
            self.assertEqual(value['candidate'], d.identity(original['candidate']))
        self.assertEqual(value['destination_observation']['observed_tip'], tip)
        self.assertEqual(value['destination_observation']['relation'], 'fast-forward')
        self.assertEqual(self.state()['routing']['target_tip'], self.base)
        self.assertEqual(self.fake.calls, calls)

    def test_movement_during_implementation_review_and_proof_keeps_all_bindings_fixed(self):
        tip = [self.base]
        def advance(stage):
            if stage not in ('implementation', 'review', 'proof'):
                return
            tree = d.fs.git(self.root, 'rev-parse', tip[0] + '^{tree}').decode().strip()
            tip[0] = subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                        '-c', 'user.email=fixture@localhost', 'commit-tree', tree, '-p', tip[0]],
                        input=(stage + '\n').encode()).decode().strip()
            d.fs.git(self.root, 'update-ref', 'refs/heads/delivery-target', tip[0])
        self.fake.on_stage = advance
        code, value = self.cli()
        self.assertEqual(code, 0, value)
        self.assertEqual(value['status'], 'REVIEWED_AND_PROVEN')
        self.assertEqual(value['comparison_base'], self.base)
        self.assertEqual(value['destination_observation']['observed_tip'], tip[0])
        self.assertEqual([stage for stage, _ in self.fake.prompts].count('review'), 1)
        self.assertEqual([stage for stage, _ in self.fake.prompts].count('proof'), 1)
        for stage in ('review', 'proof'):
            prompt = next(prompt for actual, prompt in self.fake.prompts if actual == stage)
            self.assertIn('Comparison base ' + self.base + ' is the immutable admission base', prompt)
        self.assertEqual(self.state()['reports']['review']['inputs']['comparison_base'], self.base)
        self.assertEqual(self.state()['reports']['proof']['inputs']['comparison_base'], self.base)
        review = (d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'review.md').read_text()
        self.assertIn('Comparison: base `' + self.base + '`', review)
        self.assertIn('Destination observation:', review)

    def test_target_advance_after_reports_return_does_not_refresh_verifiers(self):
        original_complete = d.Delivery.complete
        moved = []
        def move_before_completion(delivery):
            if not moved:
                tree = d.fs.git(self.root, 'rev-parse', self.base + '^{tree}').decode().strip()
                newer = subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                            '-c', 'user.email=fixture@localhost', 'commit-tree', tree, '-p', self.base],
                            input=b'After reports returned\n').decode().strip()
                d.fs.git(self.root, 'update-ref', 'refs/heads/delivery-target', newer)
                moved.append(newer)
            return original_complete(delivery)
        with patch.object(d.Delivery, 'complete', move_before_completion):
            code, value = self.cli()
        self.assertEqual(code, 0, value)
        self.assertEqual(value['destination_observation']['observed_tip'], moved[0])
        self.assertIn('compatibility with the current destination is not established', value['completion_scope'])
        self.assertEqual([stage for stage, _ in self.fake.prompts].count('review'), 1)
        self.assertEqual([stage for stage, _ in self.fake.prompts].count('proof'), 1)

    def test_fresh_process_resumes_missing_stages_after_target_advance(self):
        setup = "original=d.Delivery.stage\ndef stop(self,name):\n if name=='review': __import__('os')._exit(77)\n return original(self,name)\nd.Delivery.stage=stop"
        first = self.subprocess_cli('exec(' + repr(setup) + ')')
        self.assertEqual(first.returncode, 77, first.stderr + first.stdout)
        before = self.state()
        self.assertTrue(before['implementation_complete'])
        self.assertNotIn('review', before['reports'])
        tree = d.fs.git(self.root, 'rev-parse', self.base + '^{tree}').decode().strip()
        newer = subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                    '-c', 'user.email=fixture@localhost', 'commit-tree', tree, '-p', self.base],
                    input=b'Advance during interruption\n').decode().strip()
        d.fs.git(self.root, 'update-ref', 'refs/heads/delivery-target', newer)
        resumed = self.subprocess_cli('pass', 'resume')
        self.assertEqual(resumed.returncode, 0, resumed.stderr + resumed.stdout)
        after = self.state()
        self.assertEqual(after['comparison_base'], self.base)
        self.assertEqual(after['candidate'], before['candidate'])
        self.assertEqual([a['stage'] for a in after['attempts']].count('implementation'), 1)
        self.assertEqual([a['stage'] for a in after['attempts']].count('review'), 1)
        self.assertEqual([a['stage'] for a in after['attempts']].count('proof'), 1)
        self.assertEqual(after['destination_observation']['observed_tip'], newer)

    def test_legacy_approved_route_resumes_after_target_move_when_base_is_recoverable(self):
        self.planned_child()
        original_run = d.Delivery.run
        def run_with_legacy_records(delivery):
            delivery.state['routing'].pop('selection')
            delivery.save()
            admission_path = delivery.runtime / 'admission.json'
            admission = json.loads(admission_path.read_text())
            admission['routing'].pop('selection')
            admission_path.write_bytes(d.encoded(admission))
            return original_run(delivery)
        with patch.object(d.Delivery, 'run', run_with_legacy_records):
            self.assertEqual(self.cli()[0], 0)
        state_path = d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'delivery.json'
        state = json.loads(state_path.read_text())
        tree = d.fs.git(self.root, 'rev-parse', self.base + '^{tree}').decode().strip()
        newer = subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                    '-c', 'user.email=fixture@localhost', 'commit-tree', tree, '-p', self.base],
                    input=b'Legacy target movement\n').decode().strip()
        d.fs.git(self.root, 'update-ref', state['routing']['target_ref'], newer)
        result = self.subprocess_cli('pass', 'resume')
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        resumed = self.state()
        self.assertEqual(resumed['comparison_base'], self.base)
        self.assertEqual(resumed['destination_observation']['observed_tip'], newer)

    def planned_child(self, choice='grouped'):
        d.fs.git(self.root, 'branch', 'trunk', self.base)
        d.fs.git(self.root, 'branch', 'epic/tiny', self.base)
        (self.root / 'work/parent.md').write_text(
            CONTRACT.replace('tiny', 'parent').replace('../../../spec.txt', '../spec.txt'))
        (self.root / '.p2p/work/tiny/contract.md').write_text(CONTRACT + '\nParent: [Parent](../../../work/parent.md)\n')
        text = f'''# Slicing

## Approved delivery plan
Plan revision: v1
Approval source: User approved v1 and these destinations in retained fixture request.
Parent: work/parent.md
Final destination: trunk
Integration branch: epic/tiny
Integration start: {self.base}
Default choice: {choice}

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
| .p2p/work/tiny/contract.md | default | {'epic/tiny' if choice == 'grouped' else 'trunk'} | Complete acceptable fixture outcome. | remaining |

Parent completion: Run combined greeting.
Pending actions: none.

'''
        d.fs.save(self.root, 'work/parent.md', 'slicing.md', text.encode())
        return self.root / '.p2p/work/parent/slicing.md'

    def test_child_routing_resolves_approved_remote_tracking_destination(self):
        path = self.planned_child(choice='independent')
        d.fs.git(self.root, 'remote', 'add', 'origin', 'https://example.invalid/repo.git')
        d.fs.git(self.root, 'update-ref', 'refs/remotes/origin/main', self.base)
        old = path.read_text()
        new = (old.replace('Final destination: trunk', 'Final destination: origin/main')
                  .replace('Integration branch: epic/tiny', 'Integration branch: none')
                  .replace('Integration start: ' + self.base, 'Integration start: none')
                  .replace('| .p2p/work/tiny/contract.md | default | trunk |', '| .p2p/work/tiny/contract.md | default | origin/main |'))
        self.assertNotEqual(old, new)
        d.fs.save(self.root, 'work/parent.md', 'slicing.md', new.encode())
        code, value = self.cli()
        self.assertEqual(code, 0, value)
        self.assertEqual(value['routing']['destination'], 'origin/main')
        self.assertEqual(value['routing']['target_ref'], 'refs/remotes/origin/main')
        self.assertEqual(value['routing']['target_tip'], self.base)
        self.assertEqual(value['destination_observation']['relation'], 'unchanged')

    def test_child_routing_rejects_ambiguous_local_and_remote_destination(self):
        path = self.planned_child(choice='independent')
        d.fs.git(self.root, 'remote', 'add', 'origin', 'https://example.invalid/repo.git')
        d.fs.git(self.root, 'branch', 'origin/main', self.base)
        d.fs.git(self.root, 'update-ref', 'refs/remotes/origin/main', self.base)
        old = path.read_text()
        new = (old.replace('Final destination: trunk', 'Final destination: origin/main')
                  .replace('| .p2p/work/tiny/contract.md | default | trunk |',
                           '| .p2p/work/tiny/contract.md | default | origin/main |'))
        d.fs.save(self.root, 'work/parent.md', 'slicing.md', new.encode())
        with self.assertRaisesRegex(ValueError, 'ambiguous approved destination'):
            d.routing(self.root, '.p2p/work/tiny/contract.md')

        local = d.routing(self.root, '.p2p/work/tiny/contract.md', 'refs/heads/origin/main')
        remote = d.routing(self.root, '.p2p/work/tiny/contract.md', 'refs/remotes/origin/main')
        self.assertEqual(local['target_ref'], 'refs/heads/origin/main')
        self.assertEqual(remote['target_ref'], 'refs/remotes/origin/main')

    def test_current_sidecar_rejects_wrong_plan_section_before_reuse(self):
        self.planned_child()
        work = '.p2p/work/tiny/contract.md'
        route = d.routing(self.root, work)
        for name in ('slicing.md', 'delivery-shape.md'):
            sidecar = self.root / '.p2p/work/tiny' / name
            sidecar.write_text('Approved parent-plan contribution: S1 section SHA-256 ' + '0' * 64 + '\n')
            with self.assertRaisesRegex(ValueError, 'sidecar plan-section digest differs'):
                d.routing_records(self.root, route, work)
            sidecar.write_text(sidecar.read_text().replace('0' * 64, route['sha256']))
            records = d.routing_records(self.root, route, work)
            self.assertIn(str(sidecar.relative_to(self.root)), [r['path'] for r in records])
        d.fs.save(self.root, work, 'delivery-shape.md', b'Approved plan section SHA-256 ' + b'0' * 64 + b'\n')
        with self.assertRaisesRegex(ValueError, 'sidecar plan-section digest differs'):
            d.validate_sidecar_plan(self.root, route, work)
        d.fs.save(self.root, work, 'delivery-shape.md', ('Approved plan section SHA-256 ' + route['sha256'] + '\n').encode())
        self.assertTrue(d.routing_records(self.root, route, work))

    def test_child_routing_transfers_plan_and_binds_stage_inputs(self):
        path = self.planned_child()
        child_dir = self.root / '.p2p/work/tiny'
        evidence = child_dir / 'artifacts/sizing-evidence.md'
        evidence.parent.mkdir(parents=True)
        evidence.write_text('Sizing evidence retained with the current result.\n')
        old_sizing = b'# Previous sizing result\n'
        d.fs.save(self.root, '.p2p/work/tiny/contract.md', 'slicing.md', old_sizing)
        sizing = b'# Current sizing result\n\nEvidence: [inspection](artifacts/sizing-evidence.md)\n'
        d.fs.save(self.root, '.p2p/work/tiny/contract.md', 'slicing.md', sizing)
        old_shape = b'# Previous delivery shape\n'
        d.fs.save(self.root, '.p2p/work/tiny/contract.md', 'delivery-shape.md', old_shape)
        shape = b'# Current delivery shape\n\nSizing: [current result](slicing.md)\n'
        d.fs.save(self.root, '.p2p/work/tiny/contract.md', 'delivery-shape.md', shape)
        d.fs.save(self.root, 'work/parent.md', 'approval.md', b'User: approve routing v1.\n')
        path.write_text(path.read_text().replace('retained fixture request.', '[retained fixture request](approval.md).'))
        old = path.read_bytes()
        d.fs.save(self.root, 'work/parent.md', 'slicing.md', old + b'## Proposed delivery plan\nNot approved.\n')
        code, value = self.cli()
        self.assertEqual(code, 0, value)
        state = self.state()
        self.assertEqual(value['routing']['destination'], 'epic/tiny')
        workspace = self.runtime() / 'workspace'
        self.assertEqual((workspace / path.relative_to(self.root)).read_bytes(), path.read_bytes())
        self.assertEqual((workspace / '.p2p/work/tiny/slicing.md').read_bytes(), sizing)
        self.assertEqual((workspace / '.p2p/work/tiny/delivery-shape.md').read_bytes(), shape)
        self.assertEqual((workspace / '.p2p/work/tiny/artifacts/sizing-evidence.md').read_bytes(),
                         evidence.read_bytes())
        for name, previous in (('slicing.md', old_sizing), ('delivery-shape.md', old_shape)):
            history = '.p2p/work/tiny/history/' + d.fs.digest(previous) + '/' + name
            self.assertEqual((workspace / history).read_bytes(), previous)
        history = '.p2p/work/parent/history/' + d.fs.digest(old) + '/slicing.md'
        self.assertEqual((workspace / history).read_bytes(), old)
        (workspace / history).write_bytes(b'changed historical routing')
        code, value = self.cli('status')
        self.assertEqual(code, 1)
        self.assertIn('retained routing history/evidence changed', value['blocker'])
        (workspace / history).write_bytes(old)
        self.assertFalse(any(e['path'].startswith('.p2p/') for e in state['candidate']['changes']))
        for stage in ('implementation', 'review', 'proof'):
            self.assertEqual(state['reports'][stage]['inputs']['routing'], state['routing'])
            self.assertIn({'path': '.p2p/work/tiny/slicing.md', 'sha256': d.fs.digest(sizing)},
                          state['reports'][stage]['inputs']['routing_records'])
            self.assertIn({'path': '.p2p/work/tiny/delivery-shape.md', 'sha256': d.fs.digest(shape)},
                          state['reports'][stage]['inputs']['routing_records'])
        # A saved proposal changes neither the active decision nor candidate bytes.
        d.fs.save(self.root, 'work/parent.md', 'slicing.md', old + b'## Proposed delivery plan\nAnother proposal.\n')
        self.assertEqual(self.cli('resume')[0], 0)
        tree = d.fs.git(self.root, 'rev-parse', self.base + '^{tree}').decode().strip()
        advanced = subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                    '-c', 'user.email=fixture@localhost', 'commit-tree', tree, '-p', self.base],
                    input=b'Plan drift target movement\n').decode().strip()
        d.fs.git(self.root, 'update-ref', 'refs/heads/epic/tiny', advanced)
        changed = old.replace(b'Plan revision: v1', b'Plan revision: v2')
        d.fs.save(self.root, 'work/parent.md', 'slicing.md', changed)
        before = len(self.fake.calls)
        code, value = self.cli('resume')
        self.assertEqual(code, 1)
        self.assertIn('approved delivery plan or destination changed', value['blocker'])
        self.assertEqual(len(self.fake.calls), before)

    def test_public_cli_retains_plain_approval_on_transfer_and_fresh_recovery(self):
        path = self.planned_child()
        path.write_text(path.read_text().replace('retained fixture request.', 'retained receipt approval.md.'))
        receipt = path.parent / 'approval.md'
        original = path.read_bytes()
        pending = original + b'## Proposed delivery plan\nPending.\n'
        with self.assertRaisesRegex(ValueError, 'missing checkpoint input: .*approval.md'):
            d.fs.save(self.root, 'work/parent.md', 'slicing.md', pending)
        self.assertEqual(path.read_bytes(), pending)

        def cli(root, action):
            # Keep a fresh interpreter and the public argument parser, while giving
            # this offline fixture the same explicit host boundary as in-process tests.
            bootstrap = ('import sys;sys.path.insert(0,' + repr(str(Path(__file__).parent)) +
                         ');import test_p2p_delivery as t\nwith t.fixture_host():\n'
                         ' t.d.launch=t.FakeTransport();sys.exit(t.d.main(sys.argv[1:]))')
            command = [sys.executable, '-c', bootstrap, '--repo', str(root), action, '.p2p/work/tiny/contract.md']
            if action == 'run':
                command += ['--comparison-base', self.base, '--authorize-local', '--max-dispatches', '0']
                if not (root / '.p2p/work/parent/slicing.md').exists():
                    command += ['--destination', 'delivery-target']
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            return json.loads(result.stdout)

        self.assertIn('routing evidence unavailable', cli(self.root, 'run')['blocker'])
        self.assertFalse((d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'delivery.json').exists())
        receipt.write_bytes(b'User approved these exact v1 destinations.\n')
        self.assertIn('dispatch-count limit', cli(self.root, 'run')['blocker'])
        workspace = self.runtime() / 'workspace'
        self.assertEqual((workspace / receipt.relative_to(self.root)).read_bytes(), receipt.read_bytes())
        history = '.p2p/work/parent/history/' + d.fs.digest(original) + '/slicing.md'
        self.assertEqual((workspace / history).read_bytes(), original)
        self.assertEqual(self.state()['attempts'], [])

        recovered = Path(self.temp.name) / 'recovered'
        subprocess.run(['git', 'clone', '-q', str(self.root), str(recovered)], check=True)
        d.fs.git(recovered, 'branch', 'trunk', self.base)
        d.fs.git(recovered, 'branch', 'epic/tiny', self.base)
        recovered = recovered.resolve()
        shutil.copytree(workspace / 'work', recovered / 'work')
        checkpoint = (self.root / 'p2p-state/tiny.json').read_bytes()
        saved = json.loads(checkpoint)
        commit = saved['candidate_commit']
        self.assertEqual(d.fs.snapshot_key(d.fs.snapshot(self.root, saved['execution']['source_recovery_commit'])),
                         saved['execution']['source_tree_key'])
        d.fs.git(recovered, 'fetch', '--no-tags', str(self.root), commit)
        self.assertEqual(d.fs.restore_checkpoint(recovered, checkpoint)['status'], 'RESTORED')
        recovered_runtime = d.execution_runtime(recovered, '.p2p/work/tiny/contract.md')
        recovered_workspace = recovered_runtime / 'workspace'
        self.assertIn('dispatch-count limit', cli(recovered, 'run')['blocker'])
        self.assertEqual((recovered_workspace / '.p2p/work/parent/approval.md').read_bytes(), receipt.read_bytes())
        receipt.write_bytes(b'Changed approval.\n')
        self.assertIn('retained routing history/evidence changed', cli(self.root, 'resume')['blocker'])
        receipt.unlink()
        self.assertIn('approval.md', cli(self.root, 'resume')['blocker'])
        self.assertEqual(self.state()['attempts'], [])
        missing = recovered / '.p2p/work/parent/approval.md'
        missing.unlink()
        self.assertIn('approval.md', cli(recovered, 'resume')['blocker'])

    def test_child_missing_conflicting_and_proposed_routing_never_dispatch(self):
        path = self.planned_child()
        good = path.read_bytes()
        for data, message in [(None, 'missing approved routing'),
                              (good.replace(b'Approved delivery plan', b'Proposed delivery plan'), 'approved routing'),
                              (good + good, 'conflicting approved routing'),
                              (b'```markdown\n' + good + b'```\n', 'approved routing'),
                              (good.replace(b'| default | epic/tiny |', b'| default | trunk |'), 'conflicting child destination')]:
            if data is None:
                path.unlink()
            else:
                path.write_bytes(data)
            code, value = self.cli()
            self.assertEqual(code, 1, value)
            self.assertIn(message, value['blocker'])
            self.assertEqual(self.fake.calls, [])

    def test_child_starting_tree_is_target_not_unrelated_head(self):
        self.planned_child('independent')
        (self.root / 'sibling.txt').write_text('unfinished sibling payload\n')
        d.fs.git(self.root, 'add', 'sibling.txt')
        d.fs.git(self.root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                 'commit', '-qm', 'Unrelated branch work')
        code, value = self.cli()
        self.assertEqual(code, 0, value)
        workspace = self.runtime() / 'workspace'
        self.assertNotIn('sibling.txt', [e['path'] for e in d.fs.snapshot(workspace)])
        self.assertEqual(value['starting_commit'], self.base)
        self.assertNotEqual(self.state()['source_head'], self.base)
        self.assertEqual((self.root / 'sibling.txt').read_text(), 'unfinished sibling payload\n')
        self.assertEqual(d.fs.full_commit(self.runtime() / 'workspace', 'HEAD'), self.base)

    def test_child_stale_admission_blocks_but_target_advance_after_admission_is_observational(self):
        self.planned_child()
        tree = d.fs.git(self.root, 'rev-parse', self.base + '^{tree}').decode().strip()
        newer = subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                    '-c', 'user.email=fixture@localhost', 'commit-tree', tree, '-p', self.base], input=b'Advance target\n').decode().strip()
        d.fs.git(self.root, 'update-ref', 'refs/heads/epic/tiny', newer)
        code, value = self.cli()
        self.assertEqual(code, 1)
        self.assertIn('destination epic/tiny is currently at ' + newer, value['blocker'])
        self.assertIn('start a new delivery with --comparison-base ' + newer, value['blocker'])
        self.assertIn(newer, value['blocker'])
        self.assertEqual(self.fake.calls, [])
        d.fs.git(self.root, 'update-ref', 'refs/heads/epic/tiny', self.base)
        self.assertEqual(self.cli()[0], 0)
        initial = self.state()
        calls = self.fake.calls[:]
        d.fs.git(self.root, 'update-ref', 'refs/heads/epic/tiny', newer)
        code, value = self.cli('resume')
        self.assertEqual(code, 0, value)
        self.assertEqual(value['status'], 'REVIEWED_AND_PROVEN')
        self.assertEqual(value['comparison_base'], self.base)
        self.assertEqual(value['candidate'], d.identity(initial['candidate']))
        self.assertEqual(value['destination_observation']['observed_tip'], newer)
        self.assertEqual(value['destination_observation']['relation'], 'fast-forward')
        self.assertEqual(self.state()['routing']['target_tip'], self.base)
        self.assertEqual(self.fake.calls, calls)

    def test_integration_missing_and_unrelated_ref_give_setup_handoff(self):
        self.planned_child()
        d.fs.git(self.root, 'branch', '-D', 'epic/tiny')
        code, value = self.cli()
        self.assertEqual(code, 1)
        self.assertIn('setup refs/heads/epic/tiny at ' + self.base, value['blocker'])
        self.assertEqual(self.fake.calls, [])
        tree = d.fs.git(self.root, 'rev-parse', self.base + '^{tree}').decode().strip()
        unrelated = subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                    '-c', 'user.email=fixture@localhost', 'commit-tree', tree], input=b'Unrelated\n').decode().strip()
        d.fs.git(self.root, 'branch', 'epic/tiny', unrelated)
        code, value = self.cli()
        self.assertEqual(code, 1)
        self.assertIn('conflicts with approved starting commit', value['blocker'])
        self.assertEqual(d.fs.full_commit(self.root, 'epic/tiny'), unrelated)
        self.assertEqual(self.fake.calls, [])

    def test_parent_uses_final_destination_and_plan_loss_blocks_resume(self):
        path = self.planned_child()
        parent_route = d.routing(self.root, 'work/parent.md', 'trunk')
        self.assertEqual(parent_route['destination'], 'trunk')
        self.assertEqual(parent_route['target_tip'], self.base)
        self.assertEqual(self.cli()[0], 0)
        workspace = self.runtime() / 'workspace'
        (workspace / path.relative_to(self.root)).unlink()
        code, value = self.cli('resume')
        self.assertEqual(code, 1)
        self.assertIn('missing approved routing', value['blocker'])

    def test_success_source_preservation_and_retrieval(self):
        (self.root / 'unrelated').write_text('keep me')
        os.chmod(self.root / 'unrelated', 0o755)
        (self.root / 'link').symlink_to('unrelated')
        code, value = self.cli('run', '--exclude-dirty', 'unrelated', '--exclude-dirty', 'link')
        self.assertEqual(code, 0, value)
        self.assertEqual(value['status'], 'REVIEWED_AND_PROVEN')
        self.assertEqual(self.fake.calls, ['preflight','preflight','implementation','review','proof'])
        review=(d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'review.md').read_text()
        for heading in ('## Contract fidelity','## Scope and simplicity','## Engineering quality',
                        '## Checks and limitations','## Handoff','## Next steps',
                        'Review only; acceptance proof and merge readiness are separate.'):
            self.assertIn(heading,review)
        self.assertIn(f"Candidate: `{self.state()['candidate']['key']}`",review)
        self.assertIn('included working-tree scope:', review)
        self.assertIn('`greet.py`', review)
        self.assertIn('.p2p/work/tiny/contract.md', review)
        self.assertFalse((self.root / 'greet.py').exists())
        self.assertEqual((self.root / 'unrelated').read_text(), 'keep me')
        self.assertEqual((self.root / 'unrelated').stat().st_mode & 0o777, 0o755)
        self.assertEqual(os.readlink(self.root / 'link'), 'unrelated')
        state = self.state()
        workspace = self.runtime() / 'workspace'
        manifest = d.fs.snapshot(workspace)
        self.assertNotIn('unrelated', [x['path'] for x in state['candidate']['changes']])
        restored = Path(self.temp.name) / 'restored'
        d.materialize(restored, manifest)
        self.assertEqual(subprocess.check_output([sys.executable, str(restored/'greet.py')]), b'hello\n')
        before = (d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'delivery.json').read_bytes()
        self.assertEqual(self.cli('status')[0], 0)
        self.assertEqual(before, (d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'delivery.json').read_bytes())
        self.assertEqual(self.cli('resume')[0], 0)
        self.assertEqual(len(self.fake.calls), 5)
        proof = self.runtime() / state['reports']['proof']['path']
        proof.write_text('{}')
        code, value = self.cli('resume')
        self.assertEqual(code,1)
        self.assertIn('report/evidence content changed',value['blocker'])

    def test_runtime_artifacts_live_outside_the_source_checkout(self):
        source_tree = d.fs.snapshot(self.root)
        source_index = d.fs.git(self.root, 'ls-files', '--stage', '-z')
        code, value = self.cli('run', '--max-dispatches', '0')
        self.assertEqual(code, 1)
        local = d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        self.assertTrue((self.runtime() / 'workspace').is_dir())
        self.assertTrue((self.runtime() / 'repository.git/HEAD').is_file())
        self.assertNotIn(self.root.resolve(), self.runtime().parents)
        self.assertFalse((local / 'runtime').exists())
        agreement = d.agreement_root(self.root, '.p2p/work/tiny/contract.md')
        self.assertNotIn(self.root.resolve(), agreement.parents)
        self.assertFalse((local / 'agreement').exists())
        self.assertEqual(local, (self.root / '.p2p/work/tiny').resolve())
        self.assertIn(self.root.resolve(), local.parents)
        outer = local / 'orchestration'
        outer.mkdir()
        invocation = outer / 'invocation.json'
        invocation.write_text('{}')
        self.assertEqual(invocation.read_text(), '{}')
        self.assertEqual(source_tree, d.fs.snapshot(self.root))
        self.assertEqual(source_index, d.fs.git(self.root, 'ls-files', '--stage', '-z'))
        self.assertEqual(local, (self.root / '.p2p/work/tiny').resolve())
        self.assertFalse((self.root / '.p2p/tmp/deliver-issue').exists())

    def test_execution_access_denied_stops_before_implementation(self):
        before = d.fs.snapshot(self.root)
        with patch.object(d.fs.tempfile, 'TemporaryFile', side_effect=PermissionError('session denied writes')):
            code, value = self.cli()
        self.assertEqual(code, 1)
        self.assertIn('write access required for', value['blocker'])
        self.assertEqual(self.fake.calls, [])
        self.assertEqual(d.fs.snapshot(self.root), before)
        self.assertFalse((self.root / '.p2p/work/tiny/execution-location.json').exists())

    def test_resume_checks_narrower_session_before_any_dispatch_or_record_change(self):
        self.assertEqual(self.cli('run', '--max-dispatches', '0')[0], 1)
        state_path = d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'delivery.json'
        before = state_path.read_bytes()
        git_dir = self.runtime() / 'repository.git'
        real_probe = d.fs.tempfile.TemporaryFile

        def denied(*args, **kwargs):
            if Path(kwargs['dir']) == git_dir:
                raise PermissionError('resumed session only permits workspace writes')
            return real_probe(*args, **kwargs)

        with patch.object(d.fs.tempfile, 'TemporaryFile', side_effect=denied):
            code, value = self.cli('resume')
        self.assertEqual(code, 1)
        self.assertIn(str(git_dir), value['blocker'])
        self.assertEqual(self.fake.calls, [])
        self.assertEqual(state_path.read_bytes(), before)

    def test_configured_execution_location_survives_cleanup_and_environment_change(self):
        execution_root = Path(self.temp.name).resolve() / 'configured-executions'
        original_tree = d.fs.snapshot(self.root)
        with patch.dict(os.environ, {'P2P_EXECUTION_ROOT': str(execution_root)}):
            code, value = self.cli()
            self.assertEqual(code, 0, value)
            retained = self.runtime()
            self.assertIn(execution_root, retained.parents)
        with patch.dict(os.environ, {'P2P_EXECUTION_ROOT': str(execution_root.parent / 'changed-root')}):
            self.assertEqual(self.runtime(), retained)
            code, value = self.cli('cleanup')
            self.assertEqual(code, 0, value)
            final = json.loads((self.root / '.p2p/work/tiny/artifacts/delivery.json').read_text())
            self.assertEqual(final['cleanup'], 'source checkout unchanged')
            self.assertEqual(self.runtime(), retained)
            self.assertEqual(self.cli('status')[0], 0)
        self.assertTrue((retained / 'workspace/.git').is_file())
        self.assertTrue((retained / 'repository.git/HEAD').is_file())
        self.assertTrue((self.root / '.p2p/work/tiny/execution-location.json').is_file())
        self.assertFalse((execution_root.parent / 'changed-root').exists())
        self.assertEqual(d.fs.snapshot(self.root), original_tree)

    def test_runtime_writes_ignore_checkout_ignore_rules(self):
        (self.root / '.gitignore').write_text(
            '/.p2p/\n!/.p2p/\n!/.p2p/work/\n/.p2p/work/*\n'
            '!/.p2p/work/tiny/\n/.p2p/work/tiny/*\n!/.p2p/work/tiny/runtime/\n'
            '/.p2p/work/tiny/runtime/*\n!/.p2p/work/tiny/runtime/admission.json\n')
        d.local_save(self.root, '.p2p/work/tiny/contract.md', 'runtime/admission.json', b'{}\n')
        self.assertEqual((self.runtime() / 'admission.json').read_bytes(), b'{}\n')
        self.assertFalse((self.root / '.p2p/work/tiny/runtime/admission.json').exists())

    def test_work_item_lock_must_remain_ignored(self):
        contract = self.root / '.p2p/work/tiny/contract.md'
        original = contract.read_bytes()
        (self.root / '.gitignore').write_text(
            '/.p2p/\n!/.p2p/\n!/.p2p/work/\n/.p2p/work/*\n!/.p2p/work/tiny.lock\n')
        self.assertEqual(d.fs.git(self.root, 'check-ignore', '--no-index', '.p2p/work/probe')
                         .decode().strip(), '.p2p/work/probe')
        code, value = self.cli('run', '--max-dispatches', '0')
        self.assertEqual(code, 1)
        self.assertIn('repo-local artifact path is not ignored: .p2p/work/tiny.lock', value['blocker'])
        self.assertEqual(contract.read_bytes(), original)
        self.assertFalse((self.root / '.p2p/work/tiny.lock').exists())
        self.assertFalse((d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'delivery.json').exists())
        self.assertFalse(self.runtime().exists())
        self.assertEqual(self.fake.calls, [])

    def test_atomic_write_checks_its_temporary_sibling_ignore_rule(self):
        (self.root / '.gitignore').write_text(
            '/.p2p/\n!/.p2p/\n!/.p2p/work/\n/.p2p/work/*\n'
            '!/.p2p/work/tiny/\n/.p2p/work/tiny/*\n!/.p2p/work/tiny/runtime/\n'
            '/.p2p/work/tiny/runtime/*\n/.p2p/work/tiny/runtime/admission.json\n'
            '!/.p2p/work/tiny/runtime/admission.json.*\n')
        self.assertEqual(d.fs.git(self.root, 'check-ignore', '--no-index', '.p2p/work/probe')
                         .decode().strip(), '.p2p/work/probe')
        target = self.root / '.p2p/work/tiny/runtime/admission.json'
        target.parent.mkdir(parents=True)
        self.assertEqual(d.fs.git(self.root, 'check-ignore', '--no-index',
                                  '.p2p/work/tiny/runtime/admission.json').decode().strip(),
                         '.p2p/work/tiny/runtime/admission.json')
        with self.assertRaisesRegex(ValueError, r'not ignored'):
            d.fs.atomic_write(target, b'{}\n', ignored_root=self.root)
        self.assertFalse(target.exists())
        self.assertEqual(list(target.parent.iterdir()), [])

    def test_tracked_repo_local_state_blocks_admission_unchanged(self):
        state = self.root / '.p2p/work/prior/state.json'
        state.parent.mkdir(parents=True)
        state.write_text('user data\n')
        d.fs.git(self.root, 'add', '-f', '--', '.p2p/work/prior/state.json')
        d.fs.git(self.root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                 'commit', '-qm', 'Existing tracked state')
        before = d.fs.full_commit(self.root, 'HEAD')
        code, value = self.cli()
        self.assertEqual(code, 1)
        self.assertIn('tracked P2P state blocks', value['blocker'])
        self.assertEqual(d.fs.full_commit(self.root, 'HEAD'), before)
        self.assertEqual(state.read_text(), 'user data\n')
        self.assertEqual(self.fake.calls, [])

    def test_legacy_user_local_state_remains_recognized_until_reconciled(self):
        local = d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        repository_id = self.root.name + '-' + d.fs.digest(str(Path(d.fs.git(
            self.root, 'rev-parse', '--path-format=absolute', '--git-common-dir').decode().strip()).resolve()).encode())[:16]
        legacy = Path.home().resolve() / '.p2p/work' / repository_id / 'tiny'
        legacy.parent.mkdir(parents=True, exist_ok=True)
        legacy.mkdir(parents=True, exist_ok=True)
        (legacy / 'delivery.json').write_text('{"legacy":true}\n')
        self.assertEqual(d.local_directory(self.root, '.p2p/work/tiny/contract.md'), legacy)
        self.assertEqual(d.delivery_paths(self.root, '.p2p/work/tiny/contract.md')[1], legacy / 'artifacts')
        (local / 'delivery.json').write_text('{"repo_local":true}\n')
        with self.assertRaisesRegex(ValueError, 'both repo-local and legacy'):
            d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        shutil.rmtree(local)
        shutil.rmtree(legacy)

    def test_legacy_orchestration_only_state_remains_recognized_until_reconciled(self):
        local = d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        repository_id = self.root.name + '-' + d.fs.digest(str(Path(d.fs.git(
            self.root, 'rev-parse', '--path-format=absolute', '--git-common-dir').decode().strip()).resolve()).encode())[:16]
        legacy = Path.home().resolve() / '.p2p/work' / repository_id / 'tiny'
        invocation = legacy / 'orchestration/invocation.json'
        invocation.parent.mkdir(parents=True)
        invocation.write_text('{"status":"RUNNING"}\n')
        self.assertFalse((legacy / 'delivery.json').exists())
        self.assertFalse((legacy / 'runtime').exists())
        self.assertEqual(d.local_directory(self.root, '.p2p/work/tiny/contract.md'), legacy)
        repo_local_invocation = local / 'orchestration/invocation.json'
        repo_local_invocation.parent.mkdir(parents=True)
        repo_local_invocation.write_text('{"status":"RUNNING"}\n')
        with self.assertRaisesRegex(ValueError, 'both repo-local and legacy'):
            d.local_directory(self.root, '.p2p/work/tiny/contract.md')

    def test_shallow_exact_base_excludes_500mb_irrelevant_history_and_resumes(self):
        root = Path(self.temp.name) / 'large-history'
        repo(root)
        history = root / 'irrelevant.bin'
        history.write_bytes(os.urandom(500 * 1024 * 1024))
        d.fs.git(root, 'add', '--', 'irrelevant.bin')
        d.fs.git(root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                 'commit', '-qm', 'Large irrelevant history')
        old_blob = d.fs.git(root, 'rev-parse', 'HEAD:irrelevant.bin').decode().strip()
        history.unlink()
        d.fs.git(root, 'add', '-u', '--', 'irrelevant.bin')
        d.fs.git(root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                 'commit', '-qm', 'Small delivery base')
        base = d.fs.full_commit(root, 'HEAD')
        d.fs.git(root, 'update-ref', 'refs/heads/delivery-target', base)
        self.base = base
        code, value = self.run_root(root, '.p2p/work/tiny/contract.md', base)
        self.assertEqual(code, 0, value)
        self.assertEqual(value['status'], 'REVIEWED_AND_PROVEN')
        local = d.local_directory(root, '.p2p/work/tiny/contract.md')
        repository = self.runtime(root) / 'repository.git'
        self.assertEqual(value['comparison_base'], base)
        self.assertEqual(d.fs.full_commit(repository, base), base)
        self.assertEqual(int(d.fs.git(root, 'cat-file', '-s', old_blob).decode()), 500 * 1024 * 1024)
        missing_blob = subprocess.run(['git', '-C', str(repository), 'cat-file', '-e', old_blob], capture_output=True)
        self.assertNotEqual(missing_blob.returncode, 0)
        footprint = sum(path.stat().st_size for path in local.rglob('*') if path.is_file())
        self.assertLess(footprint, 32 * 1024 * 1024, f'active P2P footprint: {footprint} bytes')
        state = json.loads((local / 'delivery.json').read_text())
        delivery = d.Delivery(root, '.p2p/work/tiny/contract.md', state)
        delivery.verify_generation_chain()
        code, resumed = self.run_root(root, '.p2p/work/tiny/contract.md', base, 'resume')
        self.assertEqual(code, 0, resumed)
        self.assertEqual(resumed['status'], 'REVIEWED_AND_PROVEN')
        self.assertEqual(resumed['candidate'], value['candidate'])
        self.assertEqual(resumed['comparison_base'], base)
        self.assertEqual(json.loads((local / 'delivery.json').read_text())['local_git_base'],
                         state['local_git_base'])

    def test_local_workspace_is_keyed_by_repository_and_work_item(self):
        first = d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        self.assertEqual(first, d.local_directory(self.root, '.p2p/work/tiny/contract.md'))
        self.assertNotEqual(first, d.local_directory(self.root, 'work/other.md'))
        other = Path(self.temp.name) / 'other-source'
        repo(other)
        self.assertNotEqual(first, d.local_directory(other, '.p2p/work/tiny/contract.md'))

    def test_local_git_generations_reconstruct_reuse_objects_and_bind_reports(self):
        self.fake.mode = 'repair'
        code, value = self.cli()
        self.assertEqual(code, 0, value)
        state = self.state()
        generations = state['local_git_generations']
        self.assertEqual([item['stage'] for item in generations], ['admission', 'implementation', 'repair'])
        local = d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        workspace = self.runtime() / 'workspace'
        repository = self.runtime() / 'repository.git'
        base = state['local_git_base']
        self.assertEqual(base['source_commit'], self.base)
        self.assertEqual(d.fs.full_commit(repository, base['source_commit']), base['source_commit'])
        self.assertNotEqual(base['local_commit'], base['source_commit'])
        self.assertEqual(d.fs.full_commit(repository, base['local_commit']), base['local_commit'])
        self.assertEqual(d.fs.git(repository, 'rev-list', '--parents', '-n', '1', base['local_commit']).decode().split(),
                         [base['local_commit']])
        self.assertEqual(d.fs.git(repository, 'rev-parse', base['ref']).decode().strip(), base['local_commit'])
        source_paths = d.fs.git(repository, 'ls-tree', '-r', '--name-only', base['source_commit']).decode().splitlines()
        self.assertNotIn('.p2p/work/prior/state.json', source_paths)
        local_base_paths = d.fs.git(repository, 'ls-tree', '-r', '--name-only', base['local_commit']).decode().splitlines()
        self.assertNotIn('.p2p/work/prior/state.json', local_base_paths)
        base_snapshot = d.fs.snapshot(repository, base['local_commit'])
        self.assertEqual(d.fs.snapshot_key(base_snapshot), state['base_tree_key'])
        base_files = {entry['path']: entry for entry in base_snapshot}
        self.assertFalse(any(path == '.p2p' or path.startswith('.p2p/') for path in base_files))
        for index, generation in enumerate(generations):
            record_path = generation['record_path'].removeprefix('runtime/')
            record = json.loads((self.runtime() / record_path).read_bytes())
            self.assertEqual(record['commit'], generation['commit'])
            reconstructed = d.fs.snapshot(repository, record['commit'])
            self.assertEqual(d.fs.snapshot_key(reconstructed), record['candidate_key'])
            self.assertEqual(d.fs.tree_changes(base_snapshot, reconstructed), record['changes'])
            raw_diff = d.fs.git(repository, 'diff', '--no-renames', '--name-status', '-z',
                                base['local_commit'], record['commit']).split(b'\0')
            git_changes = {raw_diff[i + 1].decode(): raw_diff[i].decode()
                           for i in range(0, len(raw_diff) - 1, 2) if raw_diff[i + 1]}
            self.assertFalse(any(path.startswith('.p2p/') for path in git_changes))
            expected_status = {'deleted': 'D', 'added': 'A', 'modified': 'M'}
            self.assertEqual(git_changes, {item['path']: expected_status[item['state']]
                                           for item in record['changes']})
            self.assertEqual(d.fs.full_commit(repository, record['commit']), record['commit'])
            self.assertEqual(d.fs.git(repository, 'rev-parse', record['ref']).decode().strip(), record['commit'])
            if index:
                self.assertEqual(record['parent_commit'], generations[index - 1]['commit'])
            files = {entry['path']: entry for entry in reconstructed}
            self.assertEqual(files['spec.txt'], base_files['spec.txt'])
        review_input = state['reports']['review']['inputs']['local_git_generation']
        proof_input = state['reports']['proof']['inputs']['local_git_generation']
        self.assertEqual(review_input['commit'], generations[-1]['commit'])
        self.assertEqual(proof_input, review_input)
        for stage in ('review', 'proof'):
            raw = next(message for name, message in self.fake.messages if name == stage)
            attempt = next(item for item in state['attempts'] if item['stage'] == stage)
            self.assertEqual((self.runtime() / attempt['report']).read_bytes(), raw.encode('utf-8'))
            self.assertEqual(attempt['report_sha256'], d.fs.digest(raw.encode('utf-8')))
        self.assertEqual(len([path for path in self.runtime().glob('workspace')]), 1)
        blob = d.fs.git(repository, 'rev-parse', generations[-1]['commit'] + ':spec.txt').decode().strip()
        base_blob = d.fs.git(repository, 'rev-parse', self.base + ':spec.txt').decode().strip()
        self.assertEqual(blob, base_blob)

    def test_local_git_generation_round_trips_modes_symlinks_additions_and_deletions(self):
        self.assertEqual(self.cli()[0], 0)
        state = self.state()
        local = d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        repository = self.runtime() / 'repository.git'
        base = state['local_git_base']
        original = d.fs.snapshot(repository, base['local_commit'])
        fixture = [dict(entry) for entry in original]
        mode_entry = next(entry for entry in fixture if entry['type'] == 'file')
        mode_entry['mode'] = '100755' if mode_entry['mode'] == '100644' else '100644'
        deleted = next(entry for entry in fixture if entry['type'] == 'file' and entry is not mode_entry)
        fixture.remove(deleted)
        fixture.extend([
            {'path': 'generation-link', 'mode': '120000', 'type': 'symlink', 'target': 'missing-target'},
            {'path': 'generation-added', 'mode': '100644', 'type': 'file',
             'content_base64': 'bmV3IGZpbGUK'},
        ])
        fixture.sort(key=lambda entry: entry['path'])
        tree = d.git_generation_tree(repository, fixture)
        commit = d.fs.git(repository, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                          'commit-tree', tree, '-p', base['local_commit'], '-m', 'fixture generation').decode().strip()
        recovered = d.fs.snapshot(repository, commit)
        self.assertEqual(d.fs.snapshot_key(recovered), d.fs.snapshot_key(fixture))
        changes = {item['path']: item for item in d.fs.tree_changes(original, recovered)}
        self.assertEqual(changes[mode_entry['path']]['mode'], mode_entry['mode'])
        self.assertEqual(changes[deleted['path']]['state'], 'deleted')
        self.assertEqual(changes['generation-link']['type'], 'symlink')
        self.assertEqual(changes['generation-link']['sha256'], d.fs.digest(b'missing-target'))
        self.assertEqual(changes['generation-added']['state'], 'added')
        raw_diff = d.fs.git(repository, 'diff', '--no-renames', '--name-status', '-z',
                            base['local_commit'], commit).split(b'\0')
        git_changes = {raw_diff[i + 1].decode(): raw_diff[i].decode()
                       for i in range(0, len(raw_diff) - 1, 2) if raw_diff[i + 1]}
        self.assertEqual(git_changes, {path: {'deleted': 'D', 'added': 'A', 'modified': 'M'}[row['state']]
                                      for path, row in changes.items()})

    def test_missing_local_generation_object_blocks_resume_without_dispatch(self):
        code, value = self.cli()
        self.assertEqual(code, 0, value)
        local = d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        state = self.state()
        generation = state['local_git_generations'][-1]
        repository = self.runtime() / 'repository.git'
        blob = d.fs.git(repository, 'rev-parse', generation['commit'] + ':greet.py').decode().strip()
        object_path = repository / 'objects' / blob[:2] / blob[2:]
        self.assertTrue(object_path.exists(), object_path)
        object_path.unlink()
        calls = len(self.fake.calls)
        code, blocked = self.cli('resume')
        self.assertEqual(code, 1)
        self.assertIn('missing or corrupt local Git generation object', blocked['blocker'])
        self.assertEqual(len(self.fake.calls), calls)

    def test_success_prunes_execution_state_but_retains_candidate_workspace(self):
        cleaned = self.complete_and_cleanup()
        self.assertEqual(cleaned['status'], 'REVIEWED_AND_PROVEN')
        self.assertEqual(cleaned['progress']['candidate_validation'], 'verified durable compact identity')
        artifact = d.delivery_paths(self.root, '.p2p/work/tiny/contract.md')[1]
        records = sorted(path.name for path in artifact.iterdir())
        self.assertEqual(records, ['candidate.json', 'delivery.json', 'proof.md', 'review.md'])
        self.assertFalse(any('experience' in path.name or 'transcript' in path.name
                             for path in artifact.rglob('*')))
        self.assertEqual(self.cli('status')[0], 0)

    def test_completed_identity_record_survives_local_cleanup(self):
        self.complete_and_cleanup()
        directory = d.delivery_paths(self.root, '.p2p/work/tiny/contract.md')[1]
        candidate = json.loads((directory / 'candidate.json').read_bytes())
        delivery = json.loads((directory / 'delivery.json').read_bytes())
        review = (directory / 'review.md').read_text()
        proof = (directory / 'proof.md').read_text()
        self.assertNotIn('manifest', candidate)
        self.assertIn('snapshot:sha256:', candidate['key'])
        self.assertEqual(delivery['candidate_key'], candidate['key'])
        self.assertEqual(delivery['candidate_changes_sha256'], d.fs.digest(d.fs.canonical(candidate['changes'])))
        self.assertEqual(delivery['cleanup'], 'source checkout unchanged')
        self.assertIn(candidate['key'], review)
        self.assertIn(candidate['key'], proof)
        self.assertIn('Environment:', review)
        self.assertIn('session `fixture-', proof)
        self.assertIn('Assertion: stdout equals hello newline and status zero', proof)
        self.assertIn('Observation: fixture output hello newline, status zero', proof)

    def test_issue_record_requires_preview_bound_write_and_fresh_status(self):
        source_body = 'Issue request body captured for the accepted contract.\n'
        (self.root / 'work/tiny-source.md').write_text(source_body)
        contract = CONTRACT.replace('Source: [Specification](../../../spec.txt)',
            'Source: [Imported issue #46](../../../work/tiny-source.md)\n'
            'Source attribution: https://github.com/grove/promise-to-proof/issues/46; captured fixture source. ')
        (self.root / '.p2p/work/tiny/contract.md').write_text(contract)

        code, value = self.cli()
        self.assertEqual(code, 0, value)
        local = d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        apply_candidate(self.root, self.runtime() / 'workspace')
        d.fs.git(self.root, 'add', '--', 'greet.py')
        d.fs.git(self.root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                 'commit', '-qm', 'Deliver accepted product candidate')
        commit = d.fs.full_commit(self.root, 'HEAD')

        code, blocked = self.cli('cleanup')
        self.assertEqual(code, 1)
        self.assertIn('requires a verified durable GitHub record', blocked['blocker'])
        self.assertTrue((self.runtime()).is_dir())

        code, preview = self.cli_item('.p2p/work/tiny/contract.md', 'github-record-preview',
                                      '--delivered-commit', commit)
        self.assertEqual(code, 0, preview)
        self.assertEqual(preview['sha256'], d.fs.digest(preview['body'].encode()))
        self.assertIn(d.fs.digest(source_body.encode()), preview['body'])
        self.assertIn(d.fs.digest(contract.encode()), preview['body'])

        with patch.object(d, 'github_issue') as issue_read, \
             patch.object(d, 'github_comments') as comment_read, \
             patch.object(d, 'github_create_comment') as comment_write:
            code, denied = self.cli_item('.p2p/work/tiny/contract.md', 'github-record-publish',
                '--delivered-commit', commit, '--authorize-comment-sha256', '0' * 64)
        self.assertEqual(code, 1)
        self.assertIn('publication authorization does not match preview', denied['blocker'])
        issue_read.assert_not_called(); comment_read.assert_not_called(); comment_write.assert_not_called()
        self.assertEqual(self.state()['status'], 'REVIEWED_AND_PROVEN')

        comments = []
        def create_comment(repository, issue, body):
            comments.append({'body': body, 'html_url': 'https://github.com/grove/promise-to-proof/issues/46#issuecomment-1'})
            raise ValueError('fixture lost the write response')
        with patch.object(d, 'github_issue', return_value={'body': source_body, 'title': 'Issue 46'}), \
             patch.object(d, 'github_comments', side_effect=lambda *args: list(comments)), \
             patch.object(d, 'github_create_comment', side_effect=create_comment) as comment_write:
            code, published = self.cli_item('.p2p/work/tiny/contract.md', 'github-record-publish',
                '--delivered-commit', commit, '--authorize-comment-sha256', preview['sha256'])
        self.assertEqual(code, 0, published)
        self.assertEqual(comment_write.call_count, 1)
        self.assertEqual(published['status'], 'RECORDED')
        self.assertEqual(self.state()['github_record']['body_sha256'], preview['sha256'])

        with patch.object(d, 'github_issue', return_value={'body': source_body, 'title': 'Issue 46'}), \
             patch.object(d, 'github_comments', side_effect=lambda *args: list(comments)), \
             patch.object(d, 'github_create_comment') as retry_write:
            code, retried = self.cli_item('.p2p/work/tiny/contract.md', 'github-record-publish',
                '--delivered-commit', commit, '--authorize-comment-sha256', preview['sha256'])
        self.assertEqual(code, 0, retried)
        retry_write.assert_not_called()
        self.assertEqual(len(comments), 1)

        changed_comments = [{'body': comments[0]['body'] + '\nchanged', 'html_url': comments[0]['html_url']}]
        with patch.object(d, 'github_issue', return_value={'body': source_body}), \
             patch.object(d, 'github_comments', return_value=changed_comments):
            code, changed = self.cli('cleanup')
        self.assertEqual(code, 1)
        self.assertIn('readback changed before cleanup', changed['blocker'])
        self.assertTrue((self.runtime()).is_dir())
        self.assertFalse((d.delivery_paths(self.root, '.p2p/work/tiny/contract.md')[1] / 'delivery.json').exists())

        with patch.object(d, 'github_issue', return_value={'body': source_body, 'title': 'Issue 46'}), \
             patch.object(d, 'github_comments', side_effect=lambda *args: list(comments)):
            code, cleaned = self.cli('cleanup')
        self.assertEqual(code, 0, cleaned)
        self.assert_candidate_workspace_retained(local)
        self.assertFalse((local / 'attempts').exists())
        self.assertFalse((local / 'delivery.json').exists())
        (self.root / 'work/tiny-source.md').unlink()
        self.assertFalse((self.root / 'work/tiny.md').exists())

        args = ['--repo', str(self.root), 'github-status', '--repository', 'grove/promise-to-proof', '--issue', '46']
        output = io.StringIO()
        with patch.object(d, 'github_issue', return_value={'body': source_body, 'title': 'Issue 46'}), \
             patch.object(d, 'github_comments', return_value=comments):
            with contextlib.redirect_stdout(output): status_code = d.main(args)
        status = json.loads(output.getvalue())
        self.assertEqual(status_code, 0, status)
        preview_record = json.loads(preview['body'].split('```json\n', 1)[1].rsplit('\n```', 1)[0])
        self.assertEqual(status['status'], 'REVIEWED_AND_PROVEN')
        self.assertEqual(status['contract']['text'], contract)
        self.assertEqual(status['contract']['sha256'], d.fs.digest(contract.encode()))
        self.assertEqual(status['delivered_commit'], commit)
        self.assertEqual(status['candidate_key'], preview_record['candidate_key'])

        with patch.object(d, 'github_issue', return_value={'body': source_body}), \
             patch.object(d, 'github_comments', return_value=comments * 2):
            output = io.StringIO()
            with contextlib.redirect_stdout(output): duplicate_code = d.main(args)
        duplicate = json.loads(output.getvalue())
        self.assertEqual(duplicate_code, 1)
        self.assertIn('exactly one durable delivery record', duplicate['blocker'])

    def test_review_report_remains_evidence_backed_after_runtime_cleanup(self):
        self.complete_and_cleanup()
        directory = d.delivery_paths(self.root, '.p2p/work/tiny/contract.md')[1]
        review = (directory / 'review.md').read_text()
        self.assertIn('## Contract fidelity', review)
        self.assertIn('python3 greet.py', review)
        self.assertIn('Environment:', review)

    def test_proof_report_remains_evidence_backed_after_runtime_cleanup(self):
        self.complete_and_cleanup()
        proof = (d.delivery_paths(self.root, '.p2p/work/tiny/contract.md')[1] / 'proof.md').read_text()
        self.assertIn('## Requirement verdicts', proof)
        self.assertIn('### R1: proven', proof)
        self.assertIn('## Proof details', proof)
        self.assert_candidate_workspace_retained(d.local_directory(self.root, '.p2p/work/tiny/contract.md'))

    def test_footprint_metrics_tiny_delivery(self):
        before = d.fs.git(self.root, 'write-tree').decode().strip()
        before_metrics = p2p_metrics(self.root, before, 'tiny')
        self.assertEqual((before_metrics['files'], before_metrics['bytes']), (0, 0))
        self.complete_and_cleanup()
        after = d.fs.git(self.root, 'write-tree').decode().strip()
        metrics = p2p_metrics(self.root, after, 'tiny')
        self.assertEqual(after, before)
        self.assertEqual(metrics['files'], 0)
        self.assertEqual(metrics['bytes'], 0)
        self.assertEqual(metrics['files'], 0)
        self.assertLessEqual(metrics['bytes'], 65536)
        print_p2p_footprint('tiny-delivery', before, before_metrics, after, metrics)

    def test_steady_state_footprint_ceiling(self):
        self.complete_and_cleanup()
        tree = d.fs.git(self.root, 'write-tree').decode().strip()
        metrics = p2p_metrics(self.root, tree, 'tiny')
        self.assertEqual(metrics['files'], 0)
        artifact = d.delivery_paths(self.root, '.p2p/work/tiny/contract.md')[1]
        self.assertEqual(sorted(path.name for path in artifact.iterdir()),
                         ['candidate.json', 'delivery.json', 'proof.md', 'review.md'])

    def test_cleanup_blocks_over_limit_durable_artifacts(self):
        self.assertEqual(self.cli()[0], 0)
        workspace = self.runtime() / 'workspace'
        apply_candidate(self.root, workspace)
        artifact = d.delivery_paths(self.root, '.p2p/work/tiny/contract.md')[1]
        artifact.mkdir(parents=True, exist_ok=True)
        extra = artifact / 'archive.md'
        extra.write_bytes(b'x' * 262145)
        code, value = self.cli('cleanup')
        self.assertEqual(code, 1)
        self.assertIn('local P2P footprint exceeds limits', value['blocker'])
        self.assertTrue(workspace.is_dir())
        self.assertFalse((artifact / 'candidate.json').exists())
        extra.unlink()
        self.assertEqual(self.cli('cleanup')[0], 0)

    def test_cleanup_compacts_superseded_records_and_keeps_receipts(self):
        artifact = d.delivery_paths(self.root, '.p2p/work/tiny/contract.md')[1]
        artifact.mkdir(parents=True)
        (artifact / 'implementation.md').write_text('old implementation report\n')
        (artifact / 'repair.md').write_text('old repair report\n')
        support = {'planning-handoff.md': 'approved contract receipt\n',
                   'archive.md': 'historical recovery map\n'}
        for name, content in support.items():
            (artifact / name).write_text(content)

        self.assertEqual(self.cli()[0], 0)
        workspace = self.runtime() / 'workspace'
        apply_candidate(self.root, workspace)
        original = d.save_final
        def fail_delivery(root, work, name, data):
            if name == 'delivery.json':
                raise OSError('fixture interruption before final readback')
            return original(root, work, name, data)
        with patch.object(d, 'save_final', fail_delivery):
            code, value = self.cli('cleanup')

        self.assertEqual(code, 1)
        local = self.runtime() / 'superseded-records'
        self.assertEqual((local / 'implementation.md').read_text(), 'old implementation report\n')
        self.assertTrue((artifact / 'implementation.md').is_file())

        code, value = self.cli('cleanup')

        self.assertEqual(code, 0, value)
        records = sorted(path.relative_to(artifact).as_posix() for path in artifact.rglob('*') if path.is_file())
        self.assertEqual(records, ['archive.md', 'candidate.json', 'delivery.json', 'planning-handoff.md',
                                   'proof.md', 'review.md'])
        delivery = json.loads((artifact / 'delivery.json').read_bytes())
        self.assertEqual({item['path']: item['reason'] for item in delivery['retained_artifacts']}, {
            'archive.md': 'Historical recovery map.',
            'planning-handoff.md': 'Approval and contract provenance.'})
        metrics = p2p_metrics(self.root, d.fs.git(self.root, 'write-tree').decode().strip(), 'tiny')
        self.assertEqual(metrics['files'], 0)
        self.assertLessEqual(metrics['bytes'], 65536)
        self.assert_candidate_workspace_retained(d.local_directory(self.root, '.p2p/work/tiny/contract.md'))

    def test_cleanup_preserves_uncommitted_final_records_until_readback(self):
        artifact = d.delivery_paths(self.root, '.p2p/work/tiny/contract.md')[1]
        artifact.mkdir(parents=True)
        previous = {'candidate.json': b'{"work_item":".p2p/work/tiny/contract.md","note":"old candidate"}\n',
                    'review.md': b'old review\n',
                    'proof.md': b'old proof\n'}
        for name, data in previous.items():
            (artifact / name).write_bytes(data)

        code, value = self.cli()
        self.assertEqual(code, 0, value)
        apply_candidate(self.root, self.runtime() / 'workspace')

        def interrupt_after_readback(delivery, source_change_error):
            raise OSError('fixture interruption after final record readback')

        with patch.object(d.Delivery, 'verify_final_readback', interrupt_after_readback):
            code, value = self.cli('cleanup')

        self.assertEqual(code, 1)
        self.assertIn('fixture interruption after final record readback', value['blocker'])
        recovery = self.runtime() / 'previous-records'
        for name, data in previous.items():
            self.assertEqual((recovery / name).read_bytes(), data)
            self.assertNotEqual((artifact / name).read_bytes(), data)

        code, value = self.cli('cleanup')
        self.assertEqual(code, 0, value)
        self.assert_candidate_workspace_retained(d.local_directory(self.root, '.p2p/work/tiny/contract.md'))
        self.assertTrue(all((artifact / name).is_file() for name in previous))

    def test_cleanup_retry_rechecks_durable_records_before_deleting_recovery(self):
        self.assertEqual(self.cli()[0], 0)
        local = d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        workspace = self.runtime() / 'workspace'
        apply_candidate(self.root, workspace)
        with patch.object(d.Delivery, 'remove_local_execution_state',
                          side_effect=OSError('fixture interruption')):
            code, blocked = self.cli('cleanup')
        self.assertEqual(code, 1)
        self.assertEqual(blocked['cleanup_status'], 'BLOCKED')
        self.assertTrue(local.is_dir())

        review = d.delivery_paths(self.root, '.p2p/work/tiny/contract.md')[1] / 'review.md'
        original = review.read_bytes()
        review.unlink()
        dispatches = len(self.fake.calls)
        code, blocked = self.cli('cleanup')
        self.assertEqual(code, 1)
        self.assertIn('durable completed delivery unavailable', blocked['blocker'])
        self.assertTrue(workspace.is_dir())
        self.assertFalse(review.exists())
        self.assertEqual(len(self.fake.calls), dispatches)

        review.write_bytes(original)
        self.assertEqual(self.cli('cleanup')[0], 0)
        self.assert_candidate_workspace_retained(local)

    def test_cleanup_blocks_if_repo_local_state_becomes_tracked(self):
        self.assertEqual(self.cli()[0], 0)
        local = d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        workspace = self.runtime() / 'workspace'
        apply_candidate(self.root, workspace)
        extra = local / 'tracked-extra.md'
        extra.write_text('staged after admission\n')
        relative = '.p2p/work/tiny/tracked-extra.md'
        d.fs.git(self.root, 'add', '-f', '--', relative)
        index_before = d.fs.git(self.root, 'ls-files', '--stage', '-z')
        dispatches = len(self.fake.calls)

        code, value = self.cli('cleanup')

        self.assertEqual(code, 1)
        self.assertEqual(value['status'], 'BLOCKED')
        self.assertIn('tracked P2P state blocks repo-local storage', value['blocker'])
        self.assertTrue(workspace.is_dir())
        self.assertTrue(extra.is_file())
        self.assertEqual(d.fs.git(self.root, 'ls-files', '--stage', '-z'), index_before)
        self.assertEqual(len(self.fake.calls), dispatches)

    def test_status_and_cleanup_block_missing_state_with_local_runtime(self):
        self.complete_and_cleanup()
        local = d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        workspace = self.runtime() / 'workspace'
        saved_workspace = self.runtime() / 'workspace.saved'
        workspace.rename(saved_workspace)
        durable_record = (d.delivery_paths(self.root, '.p2p/work/tiny/contract.md')[1] / 'delivery.json').read_bytes()
        dispatches = len(self.fake.calls)

        for action in ('status', 'cleanup'):
            code, value = self.cli(action)
            self.assertEqual(code, 1, value)
            self.assertIn('retained isolated candidate workspace is missing', value['blocker'])
            self.assertTrue(saved_workspace.is_dir())
            self.assertEqual((d.delivery_paths(self.root, '.p2p/work/tiny/contract.md')[1] / 'delivery.json').read_bytes(), durable_record)
        saved_workspace.rename(workspace)
        code, value = self.cli('resume')
        self.assertEqual(code, 1, value)
        self.assertIn('missing delivery invocation; no effects can be reconciled', value['blocker'])
        self.assertEqual(len(self.fake.calls), dispatches)

    def test_cleanup_rechecks_source_after_final_records_are_written(self):
        self.assertEqual(self.cli()[0], 0)
        workspace = self.runtime() / 'workspace'
        apply_candidate(self.root, workspace)
        spec = self.root / 'spec.txt'
        accepted = spec.read_bytes()
        persist = d.Delivery.persist_final

        def persist_then_drift(delivery):
            persist(delivery)
            spec.write_bytes(accepted + b'changed during cleanup\n')

        with patch.object(d.Delivery, 'persist_final', persist_then_drift):
            code, value = self.cli('cleanup')
        self.assertEqual(code, 1)
        self.assertIn('source checkout changed during cleanup finalization', value['blocker'])
        self.assertTrue(workspace.is_dir())
        self.assertTrue((d.delivery_paths(self.root, '.p2p/work/tiny/contract.md')[1] / 'candidate.json').is_file())

        spec.write_bytes(accepted)
        self.assertEqual(self.cli('cleanup')[0], 0)
        self.assert_candidate_workspace_retained(d.local_directory(self.root, '.p2p/work/tiny/contract.md'))

    def test_incomplete_run_preserves_local_recovery_artifacts(self):
        for mode in ('blocked', 'uncertain', 'interrupted'):
            with self.subTest(mode=mode):
                root = Path(self.temp.name) / mode
                base = repo(root)
                self.fake.calls.clear()
                self.fake.mode = 'success' if mode == 'interrupted' else mode
                transport = self.fake
                if mode == 'interrupted':
                    original = transport
                    def interrupt(*args, original=original):
                        result = original(*args)
                        result.update(exit_code=-15, outcome='interrupted')
                        return result
                    transport = interrupt
                with patch.object(d, 'launch', transport):
                    code, value = self.run_root(root, '.p2p/work/tiny/contract.md', base)
                self.assertEqual(code, 1)
                local = d.local_directory(root, '.p2p/work/tiny/contract.md')
                self.assertTrue((local / 'delivery.json').is_file())
                self.assertTrue((self.runtime(root) / 'workspace').is_dir())
                self.assertTrue(any((self.runtime(root) / 'attempts').rglob('launch.json')))
                self.assertEqual(local, (root / '.p2p/work/tiny').resolve())
                self.assertTrue((root / '.p2p/work/tiny/delivery.json').is_file())

    def test_missing_recovery_artifact_blocks_without_dispatch(self):
        self.fake.mode = 'uncertain'
        code, value = self.cli()
        self.assertEqual(code, 1)
        calls = len(self.fake.calls)
        base_key = self.runtime() / 'base-tree-key'
        base_key.unlink()
        code, value = self.cli('resume')
        self.assertEqual(code, 1)
        self.assertIn('missing local recovery input: runtime/base-tree-key', value['blocker'])
        self.assertEqual(len(self.fake.calls), calls)
        self.assertEqual(value['status'], 'BLOCKED')
        self.assertTrue((self.runtime() / 'workspace').is_dir())

    def test_exact_base_fetch_preserves_git_object_identity(self):
        large = self.root / 'large.bin'
        large.write_bytes(b'P2P repeated fixture payload\n' * 32768)
        d.fs.git(self.root, 'add', '--', 'large.bin')
        d.fs.git(self.root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                 'commit', '-qm', 'Large local object')
        self.base = d.fs.full_commit(self.root, 'HEAD')
        d.fs.git(self.root, 'update-ref', 'refs/heads/delivery-target', self.base)
        code, value = self.cli('run', '--max-dispatches', '0')
        self.assertEqual(code, 1)
        repository = self.runtime() / 'repository.git'
        oid = d.fs.git(self.root, 'rev-parse', 'HEAD:large.bin').decode().strip()
        source_object = self.root / '.git/objects' / oid[:2] / oid[2:]
        cloned_object = repository / 'objects' / oid[:2] / oid[2:]
        self.assertTrue(source_object.is_file())
        self.assertTrue(cloned_object.is_file())
        self.assertEqual(d.fs.git(repository, 'cat-file', '-t', oid).decode().strip(), 'blob')
        self.assertEqual(d.fs.git(repository, 'cat-file', '-s', oid).decode().strip(), str(large.stat().st_size))
        workspace_file = self.runtime() / 'workspace/large.bin'
        self.assertNotEqual(large.stat().st_ino, workspace_file.stat().st_ino)

    def test_delivery_identity_matches_candidate_when_published(self):
        self.complete_and_cleanup()
        directory = d.delivery_paths(self.root, '.p2p/work/tiny/contract.md')[1]
        candidate = json.loads((directory / 'candidate.json').read_bytes())
        delivery = json.loads((directory / 'delivery.json').read_bytes())
        review = (directory / 'review.md').read_text()
        proof = (directory / 'proof.md').read_text()
        self.assertEqual(delivery['candidate_key'], candidate['key'])
        self.assertIn(candidate['key'], review)
        self.assertIn(candidate['key'], proof)
        self.assertNotIn('publication', delivery)

    def test_footprint_metrics_p2p_self_delivery(self):
        root = Path(self.temp.name) / 'p2p-self'
        work = 'work/p2p-self-delivery.md'
        base = p2p_repo(root, work)
        before = d.fs.git(root, 'rev-parse', base + '^{tree}').decode().strip()
        before_metrics = p2p_metrics(root, before, 'p2p-self-delivery')
        self.assertEqual((before_metrics['files'], before_metrics['bytes']), (0, 0))
        code, value = self.run_root(root, work, base)
        self.assertEqual(code, 0, value)
        workspace = d.execution_runtime(root, work) / 'workspace'
        apply_candidate(root, workspace)
        code, value = self.run_root(root, work, base, 'cleanup')
        self.assertEqual(code, 0, value)
        after = d.fs.git(root, 'write-tree').decode().strip()
        metrics = p2p_metrics(root, after, 'p2p-self-delivery')
        self.assertEqual(after, before)
        self.assertEqual((metrics['files'], metrics['bytes']), (0, 0))
        print_p2p_footprint('p2p-self-delivery', before, before_metrics, after, metrics)

    def test_footprint_metrics_large_synthetic_repository(self):
        payloads = self.root / 'payloads'
        payloads.mkdir()
        for index in range(32):
            (payloads / f'{index:02}.bin').write_bytes(bytes([index]) * 65536)
        d.fs.git(self.root, 'add', '--', 'payloads')
        d.fs.git(self.root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                 'commit', '-qm', 'Large synthetic base')
        self.base = d.fs.full_commit(self.root, 'HEAD')
        d.fs.git(self.root, 'update-ref', 'refs/heads/delivery-target', self.base)
        before = d.fs.git(self.root, 'rev-parse', self.base + '^{tree}').decode().strip()
        before_metrics = p2p_metrics(self.root, before, 'tiny')
        self.assertEqual((before_metrics['files'], before_metrics['bytes']), (0, 0))
        source_bytes = tree_blob_bytes(self.root, self.base)
        self.assertGreaterEqual(source_bytes, 2 * 1024 * 1024)
        code, value = self.cli()
        self.assertEqual(code, 0, value)
        state = self.state()
        workspace = self.runtime() / 'workspace'
        manifest = {entry['path']: entry for entry in d.fs.snapshot(workspace)}
        change_bytes = sum(len(manifest[row['path']]['target'].encode()
                               if manifest[row['path']]['type'] == 'symlink'
                               else __import__('base64').b64decode(manifest[row['path']]['content_base64']))
                           for row in state['candidate']['changes'] if row['state'] != 'deleted')
        self.assertLess(change_bytes, 4096)
        apply_candidate(self.root, workspace)
        self.assertEqual(self.cli('cleanup')[0], 0)
        after = d.fs.git(self.root, 'write-tree').decode().strip()
        metrics = p2p_metrics(self.root, after, 'tiny')
        self.assertEqual(after, before)
        self.assertEqual((metrics['files'], metrics['bytes']), (0, 0))
        print_p2p_footprint('large-synthetic-repository', before, before_metrics, after, metrics,
                            source_repository_bytes=source_bytes, changed_blob_bytes=change_bytes)

    def test_repeated_deliveries_retain_only_final_record_growth(self):
        self.complete_and_cleanup()
        apply_candidate(self.root, self.runtime() / 'workspace')
        d.fs.git(self.root, 'add', '-A')
        d.fs.git(self.root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                 'commit', '-qm', 'Apply first candidate')
        self.base = d.fs.full_commit(self.root, 'HEAD')
        d.fs.git(self.root, 'update-ref', 'refs/heads/delivery-target', self.base)
        next_work = 'work/tiny-next.md'
        (self.root / next_work).write_text(CONTRACT.replace('Acceptance contract: tiny', 'Acceptance contract: tiny next')
                                          .replace('../../../spec.txt', '../spec.txt'))
        self.fake.output_path = 'second.py'
        code, value = self.cli_item(next_work)
        self.assertEqual(code, 0, value)
        apply_candidate(self.root, d.execution_runtime(self.root, next_work) / 'workspace')
        code, value = self.cli_item(next_work, 'cleanup')
        self.assertEqual(code, 0, value)
        tree = d.fs.git(self.root, 'write-tree').decode().strip()
        retained_paths = [path for path, _ in p2p_metrics(self.root, tree, 'tiny')['paths']]
        retained_paths += [path for path, _ in p2p_metrics(self.root, tree, 'tiny-next')['paths']]
        self.assertEqual(len(retained_paths), 0)
        next_local = d.local_directory(self.root, next_work)
        self.assertTrue((next_local / 'artifacts/candidate.json').is_file())
        self.assert_candidate_workspace_retained(next_local)

    def test_fixture_generators_leave_no_generated_repository_or_logs_tracked(self):
        source_tree = d.fs.git(self.root, 'rev-parse', 'HEAD^{tree}')
        source_index = d.fs.git(self.root, 'ls-files', '--stage', '-z')
        generated = Path(self.temp.name) / 'generated-fixture'
        base = repo(generated)
        self.assertEqual(d.fs.full_commit(generated, 'HEAD'), base)
        self.assertEqual(d.fs.git(self.root, 'rev-parse', 'HEAD^{tree}'), source_tree)
        self.assertEqual(d.fs.git(self.root, 'ls-files', '--stage', '-z'), source_index)
        self.assertFalse(any(path.is_file() for path in generated.glob('**/*.jsonl')))

    def test_legacy_review_readback_uses_structured_summary(self):
        code,value=self.cli()
        self.assertEqual(code,0,value)
        state=self.state()
        report_record=state['reports']['review']
        attempt=next(a for a in state['attempts'] if a['id']==report_record['attempt_id'])
        folder=self.runtime() / 'attempts'/attempt['id']
        report_path=self.runtime()/report_record['path']
        current=json.loads(report_path.read_bytes())
        legacy={'status':'REVIEWED','input_identity_json':current['input_identity_json'],
                'requirements':[dict(row,verdict='reviewed') for row in current['requirements']],
                'gaps':[],'details':'# REVIEWED\n\nLegacy free-text summary.'}
        report_bytes=d.encoded(legacy)
        report_path.write_bytes(report_bytes)
        for path in (d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'review.md',folder/'report.md'):
            path.write_bytes(legacy['details'].encode())
        events_path=folder/'events.jsonl'
        events=[json.loads(line) for line in events_path.read_text().splitlines() if line]
        for event in events:
            item=event.get('item',{})
            if event.get('type')=='item.completed' and item.get('type')=='agent_message':
                item['text']=report_bytes.decode()
        events_bytes=(''.join(json.dumps(event)+'\n' for event in events)).encode()
        events_path.write_bytes(events_bytes)
        exit_path=folder/'exit.json'
        receipt=json.loads(exit_path.read_bytes())
        receipt['event_sha256']=d.fs.digest(events_bytes)
        exit_path.write_bytes(d.encoded(receipt))
        digest=d.fs.digest(report_bytes)
        report_record['sha256']=digest
        attempt['report_sha256']=digest
        (d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'delivery.json').write_bytes(d.encoded(state))
        calls=len(self.fake.calls)
        self.assertEqual(self.cli('status')[0],0)
        self.assertEqual(self.cli('resume')[0],0)
        self.assertEqual(len(self.fake.calls),calls)
        bundle=json.loads((self.runtime() / 'acceptance-bundle.json').read_bytes())
        summary=bundle['review']['details']['content']
        self.assertIn('## Requirements',summary)
        self.assertNotIn('Legacy free-text summary.',summary)

    def test_admission_no_new_effects(self):
        code, value = self.cli('run','--max-dispatches','0')
        self.assertEqual(code,1); self.assertIn('dispatch-count',value['blocker'])
        self.assertEqual(self.fake.calls,[])
        code, value = self.cli('run','--max-dispatches','2')
        self.assertIn('cannot change persisted',value['blocker'])
        self.assertEqual(self.fake.calls,[])

    def test_codex_version_timeout_leaves_no_delivery_state(self):
        contract = self.root / '.p2p/work/tiny/contract.md'
        original = contract.read_bytes()
        run = d.subprocess.run
        def timeout_version(args, *positional, **options):
            if len(args) == 2 and args[0].endswith('/codex') and args[1] == '--version':
                raise subprocess.TimeoutExpired(args, options['timeout'])
            return run(args, *positional, **options)
        with patch.object(d.subprocess, 'run', side_effect=timeout_version):
            code, value = self.cli()
        self.assertEqual(code, 1)
        self.assertIn('version probe failed or timed out', value['blocker'])
        local = d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        self.assertEqual(contract.read_bytes(), original)
        self.assertFalse((local / 'delivery.json').exists())
        self.assertFalse(self.runtime().exists())

    def test_repeated_run_cannot_replace_frozen_base_after_target_moves(self):
        code, value = self.cli('run', '--max-dispatches', '0')
        self.assertEqual(code, 1)
        admitted = self.state()
        tree = d.fs.git(self.root, 'rev-parse', self.base + '^{tree}').decode().strip()
        newer = subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                    '-c', 'user.email=fixture@localhost', 'commit-tree', tree, '-p', self.base],
                    input=b'Advance target\n').decode().strip()
        d.fs.git(self.root, 'update-ref', 'refs/heads/delivery-target', newer)
        code, value = self.cli('run', '--max-dispatches', '0', '--comparison-base', newer)
        self.assertEqual(code, 1)
        self.assertIn('cannot change persisted', value['blocker'])
        self.assertEqual(self.state()['comparison_base'], admitted['comparison_base'])
        self.assertEqual(self.state()['candidate'], admitted['candidate'])
        self.assertEqual(self.fake.calls, [])

    def test_adopting_new_base_uses_new_candidate_and_fresh_report_bindings(self):
        self.assertEqual(self.cli()[0], 0)
        old = self.state()
        tree = d.fs.git(self.root, 'rev-parse', self.base + '^{tree}').decode().strip()
        newer = subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                    '-c', 'user.email=fixture@localhost', 'commit-tree', tree, '-p', self.base],
                    input=b'Adopted integration base\n').decode().strip()
        d.fs.git(self.root, 'update-ref', 'refs/heads/delivery-target', newer)
        integrated = Path(self.temp.name) / 'integrated-source'
        subprocess.run(['git', 'clone', '-q', str(self.root), str(integrated)], check=True)
        d.fs.git(integrated, 'checkout', '-q', '-B', 'delivery-target', newer)
        (integrated / 'work').mkdir(exist_ok=True)
        (integrated / '.p2p/work/tiny').mkdir(parents=True, exist_ok=True)
        (integrated / '.p2p/work/tiny/contract.md').write_bytes((self.root / '.p2p/work/tiny/contract.md').read_bytes())
        output = io.StringIO()
        args = ['--repo', str(integrated), 'run', '.p2p/work/tiny/contract.md', '--comparison-base', newer,
                '--destination', 'delivery-target', '--authorize-local']
        with contextlib.redirect_stdout(output):
            code = d.main(args)
        self.assertEqual(code, 0, output.getvalue())
        new = json.loads((d.local_directory(integrated, '.p2p/work/tiny/contract.md') / 'delivery.json').read_text())
        self.assertEqual(new['comparison_base'], newer)
        self.assertNotEqual(new['candidate'], old['candidate'])
        self.assertEqual(new['candidate']['key'], old['candidate']['key'])
        self.assertNotEqual(new['reports']['review']['inputs'], old['reports']['review']['inputs'])
        self.assertNotEqual(new['reports']['proof']['inputs'], old['reports']['proof']['inputs'])
        self.assertEqual(json.loads((d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'delivery.json').read_text())['comparison_base'], self.base)

    def test_missing_authority_dispatches_nothing(self):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            code=d.main(['--repo',str(self.root),'run','.p2p/work/tiny/contract.md','--comparison-base',self.base])
        value=json.loads(output.getvalue())
        self.assertEqual(code,1)
        self.assertIn('authority missing',value['blocker'])
        self.assertEqual(self.fake.calls,[])

    def test_contested_dirty_blocks(self):
        (self.root/'dirty').write_text('untouched')
        code,value=self.cli()
        self.assertEqual(code,1);self.assertIn('contested dirty paths',value['blocker'])
        self.assertEqual(self.fake.calls,[])

    def test_uncertain_launch_never_repeats(self):
        self.fake.mode='uncertain'
        code,value=self.cli()
        self.assertEqual(code,1)
        before=len(self.fake.calls)
        code,value=self.cli('resume')
        self.assertEqual(code,1);self.assertIn('missing controller host completion',value['blocker'])
        self.assertEqual(len(self.fake.calls),before)
        self.assertEqual(len(self.state()['attempts']),3)

    def test_repair_refreshes_both_and_exhaustion_persists(self):
        self.fake.mode='exhausted'
        code,value=self.cli('run','--max-repairs','1')
        self.assertEqual(code,1,value)
        self.assertIn('repair limit exhausted',value['blocker'])
        self.assertEqual(self.fake.calls.count('repair'),1)
        self.assertEqual(self.fake.calls.count('review'),2)
        self.assertEqual(self.fake.calls.count('proof'),2)
        before=len(self.fake.calls)
        self.assertEqual(self.cli('resume')[0],1)
        self.assertEqual(len(self.fake.calls),before)
        self.assertTrue(self.state()['repair_used'])

    def test_stale_and_missing_coverage_rejected(self):
        self.fake.mode='stale'
        code,value=self.cli()
        self.assertEqual(code,1);self.assertIn('stale or mistyped',value['blocker'])

    def test_review_rejects_proof_verdict_at_receipt(self):
        self.fake.mode='review-proof-verdict'
        code,value=self.cli()
        self.assertEqual(code,1,value)
        self.assertIn('review report',value['blocker'])
        self.assertEqual(self.fake.calls,['preflight','preflight','implementation','review'])

    def test_reviewed_report_cannot_contain_findings(self):
        self.fake.mode='review-conflict'
        code,value=self.cli()
        self.assertEqual(code,1,value)
        self.assertIn('review report',value['blocker'])
        self.assertEqual(self.fake.calls,['preflight','preflight','implementation','review'])

    def test_review_rejects_free_text_status_conflict(self):
        self.fake.mode='review-prose-conflict'
        code,value=self.cli()
        self.assertEqual(code,1,value)
        self.assertIn('unsupported or missing fields',value['blocker'])
        self.assertNotIn('review',self.state().get('reports',{}))
        self.assertEqual(self.fake.calls,['preflight','preflight','implementation','review'])

    def test_review_rejects_unsupported_status(self):
        self.fake.mode='review-invalid-status'
        code,value=self.cli()
        self.assertEqual(code,1,value)
        self.assertIn('unsupported status',value['blocker'])
        self.assertNotIn('review',self.state().get('reports',{}))
        self.assertEqual(self.fake.calls,['preflight','preflight','implementation','review'])

    def test_review_rejects_blank_observation(self):
        self.fake.mode='review-blank-observation'
        code,value=self.cli()
        self.assertEqual(code,1,value)
        self.assertIn('incomplete report observations',value['blocker'])
        self.assertEqual(self.fake.calls,['preflight','preflight','implementation','review'])

    def test_blocked_review_stops_before_proof_and_repair(self):
        self.fake.mode='blocked'
        code,value=self.cli()
        self.assertEqual(code,1,value)
        self.assertIn('recovery needs',value['blocker'])
        self.assertEqual(self.fake.calls,['preflight','preflight','implementation','review','diagnosis'])
        report=(d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'review.md').read_text()
        self.assertIn('configured command `python3 greet.py`',report)
        self.assertIn('exit zero and print `hello\\n`',report)
        code,value=self.cli('resume')
        self.assertEqual(code,1,value)
        self.assertIn('recovery needs',value['blocker'])
        self.assertEqual(self.fake.calls,['preflight','preflight','implementation','review','diagnosis',
                                         'preflight','review','diagnosis'])
        self.assertNotIn('proof',self.fake.calls)
        self.assertNotIn('repair',self.fake.calls)

    def test_delegated_planning_is_audited_adopted_and_reimplemented(self):
        self.fake.mode='review-plan-handoff'
        code,value=self.cli()
        self.assertEqual(code,0,value)
        self.assertEqual(self.fake.calls.count('implementation'),2)
        self.assertEqual(self.fake.calls.count('planning-audit'),1)
        self.assertEqual(self.state()['contract']['revision'],'v2')
        self.assertEqual(len(self.state()['agreement_history']),1)
        self.assertTrue(list((self.root / '.p2p/work/tiny/history').glob('*/contract.md')))

    def test_planning_rejects_weakened_ids_and_independent_audit_refusal(self):
        self.fake.mode='planning-weaken'
        code,value=self.cli()
        self.assertEqual(code,1,value)
        self.assertIn('requirement IDs',value['blocker'])
        self.assertEqual(self.state()['contract']['revision'],'v1')

    def test_planning_audit_refusal_preserves_agreement(self):
        self.fake.mode='planning-reject'
        code,value=self.cli()
        self.assertEqual(code,1,value)
        self.assertIn('independent planning audit rejected',value['blocker'])
        self.assertEqual((self.root / '.p2p/work/tiny/contract.md').read_text(),CONTRACT)

    def test_multiple_repairs_use_fresh_diagnosis_and_both_verifiers(self):
        self.fake.mode='multi-repair'
        code,value=self.cli()
        self.assertEqual(code,0,value)
        self.assertEqual(self.fake.calls.count('repair'),2)
        self.assertEqual(self.fake.calls.count('diagnosis'),1)
        self.assertEqual(self.fake.calls.count('review'),3)
        self.assertEqual(self.fake.calls.count('proof'),3)
        self.assertEqual(len(self.state()['recovery_history']),2)

    def test_partial_repair_uses_latest_gaps_before_both_verifiers(self):
        self.fake.mode='partial-repair'
        code,value=self.cli('run','--max-dispatches','10')
        self.assertEqual(code,0,value)
        diagnoses=[prompt for stage,prompt in self.fake.prompts if stage=='diagnosis']
        findings=json.loads(diagnoses[1].split('Findings: ',1)[1].split('. Prior approaches:',1)[0])
        self.assertEqual(findings,{'implementation':['remaining repair gap']})
        self.assertEqual(self.fake.calls,['preflight','preflight','implementation','diagnosis','repair',
                                         'diagnosis','repair','review','proof'])

    def test_resume_partial_repair_uses_latest_gaps(self):
        self.fake.mode='partial-repair'
        code,value=self.cli('run','--max-dispatches','5')
        self.assertEqual(code,1,value)
        self.assertIn('dispatch-count limit',value['blocker'])
        code,value=self.cli('extend','--authorize-extension','--max-dispatches','10')
        self.assertEqual(code,0,value)
        code,value=self.cli('resume')
        self.assertEqual(code,0,value)
        diagnoses=[prompt for stage,prompt in self.fake.prompts if stage=='diagnosis']
        findings=json.loads(diagnoses[1].split('Findings: ',1)[1].split('. Prior approaches:',1)[0])
        self.assertEqual(findings,{'implementation':['remaining repair gap']})
        self.assertEqual(self.fake.calls.count('repair'),2)

    def test_resume_completed_repair_does_not_repeat_original_implementation(self):
        self.fake.mode='partial-implementation'
        finish=d.Delivery.finish_recovery
        def interrupted(delivery,entry,report):
            finish(delivery,entry,report)
            raise OSError('fixture interruption after saved repair')
        with patch.object(d.Delivery,'finish_recovery',interrupted):
            code,value=self.cli()
        self.assertEqual(code,1,value)
        self.assertIn('fixture interruption',value['blocker'])
        self.assertEqual(self.state()['recovery_history'][-1]['status'],'complete')
        code,value=self.cli('resume')
        self.assertEqual(code,0,value)
        self.assertEqual(self.fake.calls,['preflight','preflight','implementation','diagnosis','repair',
                                         'review','proof'])

    def test_actionable_diagnosis_requires_successful_capability_receipt(self):
        self.fake.mode='partial-implementation'
        original=self.fake
        def failed_probe(*args):
            result=original(*args)
            if original.calls[-1]=='diagnosis':
                path=args[2]
                events=[json.loads(line) for line in path.read_text().splitlines()]
                execution=next(e['item'] for e in events if e.get('item',{}).get('type')=='command_execution')
                execution['exit_code']=1
                path.write_text(''.join(json.dumps(e)+'\n' for e in events))
            return result
        with patch.object(d,'launch',failed_probe):
            code,value=self.cli()
        self.assertEqual(code,1,value)
        self.assertIn('successful host-recorded capability check',value['blocker'])
        self.assertNotIn('repair',self.fake.calls)
        self.assertEqual(self.state()['last_diagnosis']['report']['status'],'ACTIONABLE')
        prompt=next(prompt for stage,prompt in self.fake.prompts if stage=='diagnosis')
        self.assertIn('no enclosing-host tools inherited',prompt)
        self.assertIn('MCP servers/apps/plugins disabled',prompt)

    def test_explicit_extension_preserves_invocation_and_attempt_budget(self):
        code,value=self.cli('run','--max-dispatches','0')
        self.assertEqual(code,1,value)
        original=self.state()['invocation_id']
        code,value=self.cli('extend','--authorize-extension','--max-dispatches','infinite',
                            '--max-seconds','unlimited','--max-stage-seconds','null','--max-repairs','inf')
        self.assertEqual(code,0,value)
        self.assertEqual(self.state()['invocation_id'],original)
        self.assertEqual(len(self.state()['limit_extensions']),1)
        code,value=self.cli('resume')
        self.assertEqual(code,0,value)
        self.assertEqual(value['invocation_id'],original)
        self.assertEqual(len(value['attempts']),5)

    def test_extension_requires_explicit_authority(self):
        self.cli('run','--max-dispatches','0')
        before=self.state()['limits']
        code,value=self.cli('extend','--max-dispatches','unlimited')
        self.assertEqual(code,1,value)
        self.assertIn('explicit --authorize-extension',value['blocker'])
        self.assertEqual(self.state()['limits'],before)

    def test_standing_effect_check_is_read_only_scoped_and_rechecks_mandate(self):
        policy=d.autonomy.local('Deliver and commit locally')['policy']
        policy['effects']=[{'action':'commit','repository':str(self.root),'destination':'feature/tiny'}]
        mandate=Path(self.temp.name)/'mandate.json'
        mandate.write_text(json.dumps(policy))
        code,value=self.cli('run','--mandate',str(mandate))
        self.assertEqual(code,0,value)
        state_path=d.local_directory(self.root,'.p2p/work/tiny/contract.md')/'delivery.json'
        before=state_path.read_bytes()
        args=['--repository',str(self.root),'--destination','feature/tiny','--preview-sha256','a'*64]
        code,value=self.cli('authorize-effect','--action','commit',*args)
        self.assertEqual(code,0,value)
        self.assertEqual(value['status'],'AUTHORIZED')
        self.assertEqual(state_path.read_bytes(),before)
        code,value=self.cli('authorize-effect','--action','push',*args)
        self.assertEqual(code,1,value)
        self.assertIn('outside the standing mandate',value['blocker'])
        self.assertEqual(state_path.read_bytes(),before)
        mandate.write_text(mandate.read_text()+'\n')
        code,value=self.cli('resume')
        self.assertEqual(code,1,value)
        self.assertIn('mandate changed',value['blocker'])

    def test_confirmed_stalled_worker_is_replaced_without_duplicate_uncertain_launch(self):
        original=self.fake
        def stalled(*args):
            result=original(*args)
            if original.calls.count('implementation') == 1 and original.calls[-1] == 'implementation':
                result.update(exit_code=-15,outcome='stalled')
            return result
        with patch.object(d,'launch',stalled):
            code,value=self.cli('run','--worker-idle-seconds','30')
        self.assertEqual(code,0,value)
        self.assertEqual(self.fake.calls.count('implementation'),2)
        self.assertEqual(sum(a['status']=='retired' for a in self.state()['attempts']),1)
        self.assertEqual(len(self.state()['worker_recovery']),1)

    def test_repeated_findings_stop_when_diagnosis_has_no_new_strategy(self):
        self.fake.mode='multi-repair'
        original=self.fake
        def persistent(*args):
            result=original(*args)
            if original.calls[-1]=='proof':
                path=args[2]
                events=[json.loads(line) for line in path.read_text().splitlines()]
                message=next(e['item'] for e in events if e.get('item',{}).get('type')=='agent_message')
                report=json.loads(message['text'])
                report.update(status='NOT PROVEN',gaps=['fixture gap'])
                message['text']=json.dumps(report)
                path.write_text(''.join(json.dumps(e)+'\n' for e in events))
            if original.calls[-1]=='diagnosis' and original.calls.count('diagnosis') == 2:
                path=args[2]
                events=[json.loads(line) for line in path.read_text().splitlines()]
                message=next(e['item'] for e in events if e.get('item',{}).get('type')=='agent_message')
                report=json.loads(message['text'])
                report.update(approach='Repeat the same local seam inspection, expressed in different words.',
                              strategy_changed=False)
                message['text']=json.dumps(report)
                path.write_text(''.join(json.dumps(e)+'\n' for e in events))
            return result
        with patch.object(d,'launch',persistent):
            code,value=self.cli()
        self.assertEqual(code,1,value)
        self.assertIn('no new executable strategy',value['blocker'])
        self.assertEqual(self.fake.calls.count('repair'),2)
        self.assertEqual(self.fake.calls.count('diagnosis'),2)

    def test_review_prompt_requires_substantive_observations(self):
        code,value=self.cli()
        self.assertEqual(code,0,value)
        prompt=next(prompt for stage,prompt in self.fake.prompts if stage=='review')
        self.assertIn('Give a substantive observation for every requirement.',prompt)

    def test_missing_coverage_and_evidence(self):
        self.fake.mode='omit'
        code,value=self.cli()
        self.assertEqual(code,1)
        self.assertIn('requirement coverage',value['blocker'])

    def test_authority_hard_cap_and_expired_admission(self):
        for extra, expected in [(['--hard-cost-cap','1'],'hard monetary cap'),
                                (['--max-seconds','0'],'elapsed-time limit')]:
            code,value=self.cli('run',*extra)
            self.assertEqual(code,1)
            self.assertIn(expected,value['blocker'])
            self.assertEqual(self.fake.calls,[])
        state=self.state()
        self.assertIsNone(state['limits']['dispatches'])
        self.assertEqual(state['host']['cost'],'unknown')

    def test_persisted_scope_cannot_widen(self):
        self.cli('run','--max-dispatches','0')
        path=d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'delivery.json'
        state=json.loads(path.read_text())
        state['limits']['dispatches']=999
        path.write_text(json.dumps(state))
        code,value=self.cli('resume')
        self.assertEqual(code,1)
        self.assertIn('persisted admission changed: limits',value['blocker'])
        self.assertEqual(self.fake.calls,[])

    def test_unlimited_defaults_progress_and_read_only_status(self):
        progress=io.StringIO()
        with contextlib.redirect_stderr(progress):
            code,value=self.cli()
        self.assertEqual(code,0,value)
        self.assertEqual(value['limits'],dict.fromkeys(('dispatches','elapsed_seconds','stage_seconds','repairs','worker_idle_seconds')))
        self.assertIn('implementation started',progress.getvalue())
        self.assertIn('proof finished',progress.getvalue())
        self.assertEqual(value['progress']['stage'],'proof')
        self.assertIsNotNone(value['progress']['last_activity_at'])
        self.assertEqual(value['progress']['elapsed_seconds'],0.01)
        before=(d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'delivery.json').read_bytes()
        self.assertEqual(self.cli('status')[0],0)
        self.assertEqual(before,(d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'delivery.json').read_bytes())

    def test_status_blocks_on_orphaned_reserved_dispatch(self):
        self.assertEqual(self.cli()[0],0)
        local=d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        path=local / 'delivery.json'
        state=self.state()
        attempt=state['attempts'][-1]
        attempt.update(status='reserved',finished=None,elapsed_seconds='unknown')
        state.update(status='RUNNING',blocker=None)
        path.write_bytes(d.encoded(state))
        completion=self.runtime() / 'attempts' / attempt['id'] / 'exit.json'
        completion.unlink()

        code,value=self.cli('status')
        self.assertEqual(code,1)
        self.assertEqual(value['status'],'BLOCKED')
        self.assertIn('uncertain dispatch ' + attempt['id'],value['blocker'])
        self.assertIn('missing controller host completion',value['blocker'])
        self.assertEqual(self.state()['status'],'RUNNING')

    def test_stage_deadline_uses_smaller_remaining_allowance(self):
        code,value=self.cli('run','--max-seconds','900','--max-stage-seconds','20')
        self.assertEqual(code,0,value)
        state=self.state()
        for attempt in state['attempts']:
            self.assertEqual(attempt['deadline'],attempt['started_epoch']+20)
        self.assertTrue(all('Effective host deadline:' in prompt for _,prompt in self.fake.prompts))
        original=state['deadline']
        self.assertEqual(self.cli('resume')[0],0)
        self.assertEqual(self.state()['deadline'],original)

    def test_overall_deadline_caps_stage_and_interruption_does_not_repeat(self):
        original=self.fake
        def interrupted(*args):
            result=original(*args)
            result.update(exit_code=-15,outcome='interrupted')
            args[2].write_text('')
            return result
        with patch.object(d,'launch',interrupted):
            code,value=self.cli('run','--max-seconds','20','--max-stage-seconds','900')
        self.assertEqual(code,1,value)
        self.assertIn('elapsed-time limit',value['blocker'])
        state=self.state()
        self.assertEqual(state['attempts'][0]['deadline'],state['deadline'])
        calls=len(self.fake.calls)
        self.assertEqual(self.cli('resume')[0],1)
        self.assertEqual(len(self.fake.calls),calls)

    def test_invalid_stage_limits_never_admit(self):
        for limit in ('-1','nan','-inf'):
            code,value=self.cli('run','--max-stage-seconds='+limit)
            self.assertEqual(code,1,value)
            self.assertIn('nonnegative numbers or unlimited',value['blocker'])
            self.assertFalse((d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'delivery.json').exists())

    def test_zero_stage_limit_never_dispatches(self):
        code,value=self.cli('run','--max-stage-seconds','0')
        self.assertEqual(code,1,value)
        self.assertIn('stage elapsed-time limit',value['blocker'])
        self.assertEqual(self.fake.calls,[])

    def test_unavailable_progress_does_not_hide_identity_blocker(self):
        self.cli('run','--max-dispatches','0')
        path=d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'delivery.json'
        state=self.state()
        state['attempts']=[{'id':'pending','stage':'implementation','status':'reserved',
                            'started_epoch':time.time(),'finished':None,'elapsed_seconds':'unknown'}]
        path.write_bytes(d.encoded(state))
        (self.root/'spec.txt').write_text('changed source')
        original_open,original_stat=Path.open,Path.stat
        def unavailable_open(path,*args,**kwargs):
            if path.name=='tiny.lock':
                raise PermissionError('fixture lock inaccessible')
            return original_open(path,*args,**kwargs)
        def unavailable_stat(path,*args,**kwargs):
            if path.name in ('events.jsonl','stderr.txt'):
                raise PermissionError('fixture logs inaccessible')
            return original_stat(path,*args,**kwargs)
        with patch.object(Path,'open',unavailable_open),patch.object(Path,'stat',unavailable_stat):
            code,value=self.cli('status')
        self.assertEqual(code,1,value)
        self.assertIn('source checkout changed',value['blocker'])
        self.assertIsNone(value['progress']['controller_running'])
        self.assertIsNone(value['progress']['last_activity_at'])

    def test_status_during_active_implementation_defers_candidate_check(self):
        original=self.fake
        observed=[]
        def inspect(*args):
            result=original(*args)
            if self.fake.calls[-1]=='implementation':
                path=d.local_directory(self.root, '.p2p/work/tiny/contract.md') / 'delivery.json'
                before=path.read_bytes()
                code,value=self.cli('status')
                self.assertEqual(code,1)
                self.assertEqual(value['status'],'RUNNING',value)
                self.assertTrue(value['progress']['controller_running'])
                self.assertEqual(value['progress']['candidate_validation'],'pending active implementation or repair')
                self.assertGreaterEqual(value['progress']['elapsed_seconds'],0)
                self.assertEqual(before,path.read_bytes())
                observed.append(value)
            return result
        with patch.object(d,'launch',inspect):
            code,value=self.cli()
        self.assertEqual(code,0,value)
        self.assertEqual(len(observed),1)

    def test_completed_legacy_admission_keeps_limits_on_readback(self):
        self.assertEqual(self.cli()[0],0)
        directory=d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        for path in (directory/'delivery.json', self.runtime()/'admission.json'):
            state=json.loads(path.read_bytes())
            state['limits']={'dispatches':None,'elapsed_seconds':None}
            state['deadline']=None
            for attempt in state.get('attempts',[]):
                attempt.pop('deadline',None)
            path.write_bytes(d.encoded(state))
        before=(directory/'delivery.json').read_bytes()
        self.assertEqual(self.cli('status')[0],0)
        self.assertEqual(before,(directory/'delivery.json').read_bytes())
        count=len(self.fake.calls)
        self.assertEqual(self.cli('resume')[0],0)
        self.assertEqual(len(self.fake.calls),count)
        self.assertEqual(self.state()['limits'],{'dispatches':None,'elapsed_seconds':None})
        self.assertIsNone(self.state()['deadline'])

    def test_real_transport_timeout_and_heartbeat(self):
        folder=Path(self.temp.name)
        events,errors=folder/'events.jsonl',folder/'stderr.txt'
        progress=io.StringIO()
        # This invokes the actual transport, never the fixture host.
        self.patch.stop()
        started=time.monotonic()
        marker=folder/'child-survived'
        child='import pathlib,signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); print("child-ready",flush=True); time.sleep(0.8); pathlib.Path('+repr(str(marker))+').touch()'
        command='import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",'+repr(child)+']); print("activity",flush=True); time.sleep(10)'
        with patch.object(d,'HEARTBEAT_SECONDS',0.03,create=True), contextlib.redirect_stderr(progress):
            result=d.launch([sys.executable,'-c',command],
                            '',events,errors,time.time()+0.3)
        self.assertEqual(result['outcome'],'interrupted')
        self.assertLess(time.monotonic()-started,3)
        self.assertNotEqual(result['exit_code'],0)
        time.sleep(0.9)
        self.assertEqual(('log activity' in progress.getvalue(), marker.exists()),
                         (True,False),'heartbeat and worker process-group termination must both hold')
        self.assertIn('activity\n',events.read_text())
        self.assertIn('child-ready\n',events.read_text())

    def test_successful_repair_rereviews_and_reproves(self):
        self.fake.mode='repair'
        code,value=self.cli()
        self.assertEqual(code,0,value)
        self.assertEqual(self.fake.calls,['preflight','preflight','implementation','review','proof','repair','review','proof'])
        state=self.state()
        ids=[a['session_id'] for a in state['attempts']]
        self.assertEqual(len(ids),len(set(ids)))
        for attempt in state['attempts']:
            self.assertIsNotNone(attempt['started'])
            self.assertIsNotNone(attempt['finished'])
            self.assertGreaterEqual(attempt['elapsed_seconds'],0)
            self.assertEqual(attempt['usage'],{'input_tokens':7,'output_tokens':3})
            self.assertEqual(attempt['cost'],'unknown')

    def subprocess_cli(self, setup, action='run', *extra):
        # Fixture injection lives only in this test launcher, never in production CLI.
        code = "import sys;sys.path.insert(0," + repr(str(Path(__file__).parent)) + ");import test_p2p_delivery as t;d=t.d\nwith t.fixture_host():\n d.launch=t.FakeTransport();" + setup + ";sys.exit(d.main(sys.argv[1:]))"
        args=[sys.executable,'-c',code,'--repo',str(self.root),action,'.p2p/work/tiny/contract.md']
        if action=='run':
            args+=['--comparison-base',self.base,'--authorize-local']
            if not (self.root / '.p2p/work/parent/slicing.md').exists():
                args+=['--destination','delivery-target']
        return subprocess.run(args+list(extra),capture_output=True,text=True)

    def test_fresh_process_recovers_known_completion_once(self):
        setup = "original=d.Delivery.receipt\ndef stop(self,a):\n if a['stage']=='proof': __import__('os')._exit(77)\n return original(self,a)\nd.Delivery.receipt=stop"
        first=self.subprocess_cli("exec("+repr(setup)+")")
        self.assertEqual(first.returncode,77,first.stderr+first.stdout)
        state=self.state()
        self.assertEqual(state['attempts'][-1]['status'],'reserved')
        before=len(state['attempts'])
        resumed=self.subprocess_cli('pass','resume')
        self.assertEqual(resumed.returncode,0,resumed.stderr+resumed.stdout)
        self.assertEqual(len(self.state()['attempts']),before)
        again=self.subprocess_cli('pass','resume')
        self.assertEqual(again.returncode,0,again.stderr+again.stdout)
        self.assertEqual(len(self.state()['attempts']),before)

    def test_fresh_process_uncertain_launch_blocks(self):
        first=self.subprocess_cli("d.launch=t.FakeTransport('uncertain')")
        self.assertEqual(first.returncode,1)
        before=len(self.state()['attempts'])
        resumed=self.subprocess_cli('pass','resume')
        self.assertEqual(resumed.returncode,1)
        self.assertIn('missing controller host completion',resumed.stdout)
        self.assertEqual(len(self.state()['attempts']),before)

    def test_concurrent_controller_cannot_reserve(self):
        import fcntl
        self.cli('run','--max-dispatches','0')
        local = d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        with (local.parent / (local.name + '.lock')).open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            other=self.subprocess_cli('pass','resume')
        self.assertEqual(other.returncode,1)
        self.assertIn('another controller holds',other.stdout)
        self.assertEqual(len(self.state()['attempts']),0)

    def test_reconstruct_candidate_with_retained_base(self):
        self.assertEqual(self.cli()[0],0)
        state=self.state()
        d.fs.git(self.root, 'update-ref', '-d', 'refs/heads/delivery-target')
        code, value = self.cli('resume')
        self.assertEqual(code, 0, value)
        self.assertEqual(value['destination_observation']['relation'], 'unavailable')
        restored=Path(self.temp.name)/'fresh'
        metadata=Path(self.temp.name)/'fresh.git'
        metadata=self.runtime() / 'repository.git'
        subprocess.run(['git','clone','-q',str(metadata),str(restored)],check=True,capture_output=True)
        d.materialize(restored,d.fs.snapshot(self.runtime() / 'workspace'))
        restored_contract = restored / '.p2p/work/tiny/contract.md'
        restored_contract.parent.mkdir(parents=True, exist_ok=True)
        restored_contract.write_bytes((self.runtime() / 'workspace/.p2p/work/tiny/contract.md').read_bytes())
        self.assertEqual(d.fs.full_commit(restored, self.base), self.base)
        self.assertEqual(d.fs.snapshot_key(d.fs.snapshot(restored, self.base)), (self.runtime() / 'base-tree-key').read_text().strip())
        d.fs.save(restored,'.p2p/work/tiny/contract.md','candidate.json',d.encoded(state['candidate']))
        self.assertEqual(d.fs.validate(restored,'.p2p/work/tiny/contract.md',self.base,
                                       exclude=state['agreement_paths']),state['candidate'])

    def test_resume_rereads_reports_after_source_prunes_base_commit(self):
        tree=d.fs.git(self.root,'rev-parse',self.base+'^{tree}').decode().strip()
        unrelated_head=subprocess.check_output(['git','-C',str(self.root),'-c','user.name=Fixture',
                    '-c','user.email=fixture@localhost','commit-tree',tree],input=b'Unrelated source HEAD\n').decode().strip()
        branch=d.fs.git(self.root,'symbolic-ref','--short','HEAD').decode().strip()
        d.fs.git(self.root,'update-ref','refs/heads/'+branch,unrelated_head)
        self.assertEqual(self.cli()[0],0)
        calls=list(self.fake.calls)

        d.fs.git(self.root,'update-ref','-d','refs/heads/delivery-target')
        d.fs.git(self.root,'reflog','expire','--expire=now','--all')
        d.fs.git(self.root,'gc','--prune=now')
        with self.assertRaises(ValueError):
            d.fs.full_commit(self.root,self.base)

        code,value=self.cli('resume')
        self.assertEqual(code,0,value)
        self.assertEqual(value['status'],'REVIEWED_AND_PROVEN')
        self.assertEqual(value['destination_observation']['relation'],'unavailable')
        self.assertEqual(self.fake.calls,calls)

    def test_source_agreement_binding_base_and_report_loss(self):
        self.assertEqual(self.cli()[0],0)
        tree = d.fs.git(self.root, 'rev-parse', self.base + '^{tree}').decode().strip()
        newer = subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                    '-c', 'user.email=fixture@localhost', 'commit-tree', tree, '-p', self.base],
                    input=b'Drift with a moving destination\n').decode().strip()
        d.fs.git(self.root, 'update-ref', 'refs/heads/delivery-target', newer)
        local = d.local_directory(self.root, '.p2p/work/tiny/contract.md')
        for file,replacement in [(self.root/'.p2p/work/tiny/contract.md',CONTRACT+'same revision changed bytes\n'),
                                      (self.root/'spec.txt','changed binding\n'),
                                      (self.runtime()/'base-tree-key','[]'),
                                      (self.runtime()/'repository.git/HEAD','damaged git metadata'),
                                      (local/'proof.md','truncated')]:
            previous=file.read_bytes()
            file.write_text(replacement)
            code,value=self.cli('status')
            self.assertEqual(code,1,(str(file),value))
            self.assertEqual(value['status'],'BLOCKED')
            file.write_bytes(previous)
        self.assertEqual(self.cli('status')[0],0)

    def test_legacy_reconciliation_localization_preserves_origin_on_resume(self):
        root = Path(self.temp.name) / 'legacy-localization'
        root.mkdir()
        d.fs.git(root, 'init', '-q')
        d.fs.git(root, 'config', 'user.name', 'Fixture')
        d.fs.git(root, 'config', 'user.email', 'fixture@localhost')
        (root / '.gitignore').write_text('/.p2p/\n')
        (root / 'specs').mkdir()
        (root / 'work').mkdir()
        source = root / 'specs/source.md'
        source.write_text('Original specification bytes\n')
        legacy = root / 'work/legacy.md'
        contract = (CONTRACT.replace('# Acceptance contract: tiny', '# Acceptance contract: legacy')
                    .replace('Contract revision: v1', 'Contract revision: v4')
                    .replace('Source: [Specification](../../../spec.txt)',
                             'Source: [Specification](../specs/source.md)'))
        legacy.write_text(contract)
        d.fs.git(root, 'add', '.gitignore', 'specs/source.md', 'work/legacy.md')
        d.fs.git(root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                 'commit', '-qm', 'Legacy P2P contract')

        original_bindings = d.fs.bindings(root, 'work/legacy.md')
        d.fs.reconcile(root, 'work/legacy.md')
        active = '.p2p/work/legacy/contract.md'
        origin = root / '.p2p/work/legacy/contract-origin.json'
        origin_bytes = origin.read_bytes()
        self.assertEqual((root / active).read_text(), contract)
        self.assertEqual(d.fs.bindings(root, active), original_bindings)

        d.localize_agreement(root, active, original_bindings)
        localized = d.agreement_root(root, active) / active
        localized_origin = d.agreement_root(root, active) / '.p2p/work/legacy/contract-origin.json'
        self.assertEqual(localized.read_text(), contract)
        self.assertEqual(localized_origin.read_bytes(), origin_bytes)
        self.assertEqual((d.agreement_root(root, active) / 'work/legacy.md').read_text(), contract)
        # A fresh resolver call exercises the resumed, localized agreement path.
        self.assertEqual(d.agreement_bindings(root, active), original_bindings)
        self.assertEqual(d.contract(root, active)[0]['sha256'], d.fs.digest(contract.encode()))
        self.assertEqual(source.read_text(), 'Original specification bytes\n')

    def test_legacy_origin_binding_survives_workspace_creation_and_resume(self):
        root = Path(self.temp.name) / 'legacy-workspace'
        root.mkdir()
        d.fs.git(root, 'init', '-q')
        d.fs.git(root, 'config', 'user.name', 'Fixture')
        d.fs.git(root, 'config', 'user.email', 'fixture@localhost')
        (root / '.gitignore').write_text('/.p2p/\n')
        (root / 'specs').mkdir()
        (root / 'work').mkdir()
        (root / 'specs/source.md').write_text('Legacy-bound specification bytes\n')
        contract = CONTRACT.replace('Source: [Specification](../../../spec.txt)',
                                    'Source: [Specification](../specs/source.md)')
        (root / 'work/legacy.md').write_text(contract)
        d.fs.git(root, 'add', '.gitignore', 'specs/source.md', 'work/legacy.md')
        d.fs.git(root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                 'commit', '-qm', 'Legacy contract base')
        base = d.fs.full_commit(root, 'HEAD')
        d.fs.git(root, 'branch', 'delivery-target', base)
        d.fs.reconcile(root, 'work/legacy.md')

        work = '.p2p/work/legacy/contract.md'
        args = argparse.Namespace(work=work, authorize_local=True, hard_cost_cap=None,
                                  comparison_base=base, destination='delivery-target',
                                  exclude_dirty=[], max_dispatches=8, max_seconds=1800,
                                  max_stage_seconds=600)
        delivery = d.create(root, args)
        self.assertEqual(delivery.current(), delivery.state['candidate'])
        self.assertEqual(d.fs.bindings(delivery.workspace, work), delivery.state['binding_inputs'])

        resumed = d.Delivery(root, work, json.loads((delivery.local / 'delivery.json').read_text()))
        self.assertEqual(resumed.current(), resumed.state['candidate'])

    def test_storage_failure_is_recoverable_from_exact_host_return(self):
        self.assertEqual(self.cli()[0],0)
        before=len(self.fake.calls)
        workspace=self.runtime() / 'workspace'
        apply_candidate(self.root,workspace)
        original=d.save_final
        def fail(root,work,name,data):
            if name=='proof.md': raise OSError('fixture evidence destination unavailable')
            return original(root,work,name,data)
        with patch.object(d,'save_final',fail):
            code,value=self.cli('cleanup')
        self.assertEqual(code,1)
        self.assertIn('destination unavailable',value['blocker'])
        self.assertTrue((self.runtime() / 'workspace').is_dir())
        self.assertEqual(self.cli('cleanup')[0],0)
        self.assertEqual(len(self.fake.calls),before)

    def test_atomic_storage_preserves_old_bytes_on_replace_failure(self):
        directory=self.root/'.p2p/work/tiny'
        d.fs.save(self.root,'.p2p/work/tiny/contract.md','storage.txt',b'old')
        original=d.fs.os.replace
        def fail(source,target):
            if Path(target)==directory/'storage.txt':raise OSError('fixture interrupted replacement')
            return original(source,target)
        with patch.object(d.fs.os,'replace',fail):
            with self.assertRaises(OSError):d.fs.save(self.root,'.p2p/work/tiny/contract.md','storage.txt',b'new')
        self.assertEqual((directory/'storage.txt').read_bytes(),b'old')
        self.assertEqual((directory/'history'/d.fs.digest(b'old')/'storage.txt').read_bytes(),b'old')

    def test_agreement_and_candidate_drift(self):
        self.assertEqual(self.cli()[0],0)
        state=self.state()
        tree = d.fs.git(self.root, 'rev-parse', self.base + '^{tree}').decode().strip()
        newer = subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                    '-c', 'user.email=fixture@localhost', 'commit-tree', tree, '-p', self.base],
                    input=b'Candidate drift with moving destination\n').decode().strip()
        d.fs.git(self.root, 'update-ref', 'refs/heads/delivery-target', newer)
        candidate=self.runtime() / 'workspace/greet.py'
        original = candidate.read_bytes()
        original_mode = candidate.stat().st_mode & 0o777
        candidate.write_text("print('wrong')\n")
        code,value=self.cli('resume')
        self.assertEqual(code,1);self.assertIn('product candidate changed',value['blocker'])
        candidate.write_bytes(original)
        candidate.chmod(0o755)
        code,value=self.cli('resume')
        self.assertEqual(code,1);self.assertIn('product candidate changed',value['blocker'])
        candidate.chmod(original_mode)
        moved = candidate.with_name('moved-greet.py')
        candidate.rename(moved)
        code,value=self.cli('resume')
        self.assertEqual(code,1);self.assertIn('product candidate changed',value['blocker'])
        moved.rename(candidate)
        candidate.unlink()
        candidate.symlink_to('spec.txt')
        code,value=self.cli('resume')
        self.assertEqual(code,1);self.assertIn('product candidate changed',value['blocker'])
        candidate.unlink()
        candidate.write_bytes(original)
        candidate.chmod(original_mode)


class ConformanceBridgeTests(unittest.TestCase):
    def test_successful_delivery_uses_current_controller_paths_and_identity(self):
        project = Path(__file__).resolve().parents[1]
        bridge = project / 'checks/delivery-model/conformance_bridge.py'
        with tempfile.TemporaryDirectory() as temporary:
            trace = Path(temporary) / 'trace'
            scratch = Path(temporary) / 'scratch'
            home = Path(temporary) / 'home'
            scratch.mkdir()
            home.mkdir()
            env = os.environ | {'P2P_REPO': str(project), 'P2P_TRACE_DIR': str(trace),
                                'HOME': str(home),
                                'P2P_MBT_CASE': 'successful-delivery',
                                'PYTHONPYCACHEPREFIX': str(scratch / 'pycache'),
                                'TMPDIR': str(scratch)}

            def invoke(action):
                result = subprocess.run([sys.executable, str(bridge), action], cwd=project, env=env,
                                        text=True, capture_output=True, timeout=60)
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                return result.stdout.strip()

            self.assertEqual(invoke('Init'), 'initialized')
            base = (trace / 'base').read_text() if (trace / 'base').exists() else None
            start = invoke('Start').split('|')
            self.assertEqual(start[:2], ['77', 'RUNNING'])
            self.assertEqual((start[6], start[9]), ('1', '1'))
            for action in ('Review', 'Proof'):
                result = invoke(action).split('|')
                self.assertEqual(result[:2], ['77', 'RUNNING'])
                self.assertEqual(result[9], '1')
            finished = invoke('Restart').split('|')
            self.assertEqual(finished[:2], ['0', 'REVIEWED_AND_PROVEN'])
            self.assertEqual((finished[7], finished[8], finished[9]), ('1', '1', '1'))

            source = trace / 'source'
            with patch.dict(os.environ, {'HOME': str(home)}):
                local = d.local_directory(source, '.p2p/work/tiny/contract.md')
                runtime = d.execution_runtime(source, '.p2p/work/tiny/contract.md')
            saved = json.loads((local / 'delivery.json').read_text())
            self.assertIn('key', saved['candidate'])
            self.assertIn('changes', saved['candidate'])
            self.assertNotIn('manifest', saved['candidate'])
            self.assertTrue((runtime / 'workspace/.git').is_file())
            self.assertTrue(all((runtime / report['path']).is_file()
                                for report in saved['reports'].values()))
            # The bridge computes expected report identity independently of the
            # controller. A passing candidate alone cannot hide stale instructions.
            with patch.dict(os.environ, env):
                spec = importlib.util.spec_from_file_location('conformance_bridge_check', bridge)
                adapter = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(adapter)
                for stage, index in (('review', 7), ('proof', 8)):
                    report_path = runtime / saved['reports'][stage]['path']
                    original = report_path.read_bytes()
                    try:
                        for defect in ('missing', 'changed'):
                            with self.subTest(stage=stage, instruction_identity=defect):
                                report = json.loads(original)
                                inputs = json.loads(report['input_identity_json'])
                                self.assertEqual(inputs['instruction_identity'], saved['instruction_identity'])
                                if defect == 'missing':
                                    inputs.pop('instruction_identity')
                                else:
                                    inputs['instruction_identity'] = '0' * 64
                                report['input_identity_json'] = json.dumps(inputs)
                                report_path.write_bytes(d.encoded(report))
                                projected = adapter.projection(0, saved).split('|')
                                expected = ['1', '1', '1']
                                expected[index - 7] = '-1'
                                self.assertEqual(projected[7:10], expected)
                    finally:
                        report_path.write_bytes(original)
            actions = [json.loads(line) for line in (trace / 'actions.jsonl').read_text().splitlines()]
            self.assertIn('--destination', actions[0]['controller']['command'])
            self.assertIn('delivery-target', actions[0]['controller']['command'])
            self.assertEqual(d.fs.git(source, 'rev-parse', 'HEAD').decode().strip(), base)
            self.assertEqual(d.fs.git(source, 'rev-parse', 'delivery-target').decode().strip(), base)


if __name__ == '__main__':
    unittest.main()
