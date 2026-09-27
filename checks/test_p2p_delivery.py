#!/usr/bin/env python3
"""Deterministic fixture transport tests. These are NOT live host evidence."""
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
sys.path.insert(0, str(SCRIPTS))
import p2p_delivery as d

CONTRACT = '''# Acceptance contract: tiny

Contract revision: v1
Source: [Specification](../spec.txt)

Intended outcome: greet.py prints hello.

## Acceptance matrix

| ID | Source | Requirement | Boundaries / counterexamples | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | spec.txt | greet.py prints hello and exits zero. | Wrong text or failure is rejected. | python3 greet.py | hello plus newline and exit zero | Run python3 greet.py and assert exact output and status. | planned |

## Unresolved gaps

None.
'''


def repo(path):
    path.mkdir()
    subprocess.run(['git', 'init', '-q', str(path)], check=True)
    (path / '.gitignore').write_text('/.p2p/tmp/\n')
    (path / 'spec.txt').write_text('A CLI prints hello followed by a newline and exits zero.\n')
    subprocess.run(['git', '-C', str(path), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(path), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                    'commit', '-qm', 'Fixture base'], check=True)
    (path / 'work').mkdir()
    (path / 'work/tiny.md').write_text(CONTRACT)
    return subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()


class FakeTransport:
    """Clearly labeled fixture that supplies host-shaped records, never host proof."""
    def __init__(self, mode='success'):
        self.mode, self.calls, self.prompts = mode, [], []

    def __call__(self, args, prompt, event_path, error_path, deadline):
        attempt = json.loads((event_path.parent / 'launch.json').read_text())
        inputs = attempt['inputs']
        stage = 'preflight' if 'probe_sha256' in inputs else attempt['stage']
        self.calls.append(stage)
        self.prompts.append((stage, prompt))
        workspace = Path(args[args.index('-C') + 1])
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
        else:
            if stage in ('implementation','repair'):
                (workspace / 'greet.py').write_text("print('hello')\n" + ("# repaired fixture\n" if stage == 'repair' else ''))
            status = {'implementation':'IMPLEMENTED','repair':'REPAIRED','review':'REVIEWED','proof':'PROVEN'}[stage]
            gap = self.mode in ('repair','exhausted') and stage == 'proof' and (self.mode == 'exhausted' or self.calls.count('proof') == 1)
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
                      'gaps':['fixture gap'] if gap else []}
            if stage == 'review':
                report.update(findings=[], coverage='R1; inspected greet.py and the delivery checks.',
                              checks=[{'command':'python3 greet.py','result':'passed',
                                       'observation':'Fixture output hello newline, exit zero.'}],
                              limitations=['Fixture transport does not establish live-host behavior.'],
                              missing_input='', expected_result='')
                if self.mode == 'blocked':
                    report.update(status='BLOCKED', missing_input='configured command `python3 greet.py`',
                                  expected_result='exit zero and print `hello\\n`')
                if self.mode == 'review-plan-handoff':
                    report.update(status='CHANGES NEEDED', findings=[{
                        'id':'F1','source':'R2','axis':'Contract fidelity','location':'work/tiny.md',
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
            output = 'hello\n'
            report = json.dumps(report)
        events += [{'type':'item.completed','item':{'type':'command_execution','command':'FIXTURE python3 greet.py',
                                                    'aggregated_output':output,'exit_code':0}},
                   {'type':'item.completed','item':{'type':'agent_message','text':report}},
                   {'type':'turn.completed','usage':{'input_tokens':7,'output_tokens':3}}]
        event_path.write_text(''.join(json.dumps(e)+'\n' for e in events))
        error_path.write_text('FIXTURE TRANSPORT\n')
        return {'exit_code':0,'outcome':'finished','finished':d.now(),'elapsed_seconds':0.01}


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'source'
        self.base = repo(self.root)
        self.fake = FakeTransport()
        self.patch = patch.object(d, 'launch', self.fake)
        self.patch.start()
        self.host = patch.object(d.platform, 'system', lambda:'Darwin')
        self.host.start()

    def tearDown(self):
        self.patch.stop(); self.host.stop(); self.temp.cleanup()

    def cli(self, action='run', *extra):
        args = ['--repo', str(self.root), action, 'work/tiny.md']
        if action == 'run': args += ['--comparison-base', self.base, '--authorize-local']
        output = io.StringIO()
        with contextlib.redirect_stdout(output): code = d.main(args + list(extra))
        return code, json.loads(output.getvalue())

    def state(self):
        return json.loads((self.root / '.p2p/work/tiny/delivery.json').read_text())

    def planned_child(self, choice='grouped'):
        d.fs.git(self.root, 'branch', 'trunk', self.base)
        d.fs.git(self.root, 'branch', 'epic/tiny', self.base)
        (self.root / 'work/parent.md').write_text(CONTRACT.replace('tiny', 'parent'))
        (self.root / 'work/tiny.md').write_text(CONTRACT + '\nParent: [Parent](parent.md)\n')
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
| work/tiny.md | default | {'epic/tiny' if choice == 'grouped' else 'trunk'} | Complete acceptable fixture outcome. | remaining |

Parent completion: Run combined greeting.
Pending actions: none.

'''
        d.fs.save(self.root, 'work/parent.md', 'slicing.md', text.encode())
        return self.root / '.p2p/work/parent/slicing.md'

    def test_child_routing_transfers_plan_and_binds_stage_inputs(self):
        path = self.planned_child()
        d.fs.save(self.root, 'work/parent.md', 'approval.md', b'User: approve routing v1.\n')
        path.write_text(path.read_text().replace('retained fixture request.', '[retained fixture request](approval.md).'))
        old = path.read_bytes()
        d.fs.save(self.root, 'work/parent.md', 'slicing.md', old + b'## Proposed delivery plan\nNot approved.\n')
        code, value = self.cli()
        self.assertEqual(code, 0, value)
        state = self.state()
        self.assertEqual(value['routing']['destination'], 'epic/tiny')
        workspace = self.root / '.p2p/work/tiny/runtime/workspace'
        self.assertEqual((workspace / path.relative_to(self.root)).read_bytes(), path.read_bytes())
        history = '.p2p/work/parent/history/' + d.fs.digest(old) + '/slicing.md'
        self.assertEqual((workspace / history).read_bytes(), old)
        (workspace / history).write_bytes(b'changed historical routing')
        code, value = self.cli('status')
        self.assertEqual(code, 1)
        self.assertIn('retained routing history/evidence changed', value['blocker'])
        (workspace / history).write_bytes(old)
        self.assertFalse(any(e['path'].startswith('.p2p/') for e in state['candidate']['manifest']))
        for stage in ('implementation', 'review', 'proof'):
            self.assertEqual(state['reports'][stage]['inputs']['routing'], state['routing'])
        # A saved proposal changes neither the active decision nor candidate bytes.
        d.fs.save(self.root, 'work/parent.md', 'slicing.md', old + b'## Proposed delivery plan\nAnother proposal.\n')
        self.assertEqual(self.cli('resume')[0], 0)
        changed = old.replace(b'Plan revision: v1', b'Plan revision: v2')
        d.fs.save(self.root, 'work/parent.md', 'slicing.md', changed)
        before = len(self.fake.calls)
        code, value = self.cli('resume')
        self.assertEqual(code, 1)
        self.assertIn('approved delivery plan changed', value['blocker'])
        self.assertEqual(len(self.fake.calls), before)

    def test_public_cli_retains_plain_approval_on_transfer_and_fresh_recovery(self):
        path = self.planned_child()
        path.write_text(path.read_text().replace('retained fixture request.', 'retained receipt approval.md.'))
        receipt = path.parent / 'approval.md'
        original = path.read_bytes()
        d.fs.save(self.root, 'work/parent.md', 'slicing.md', original + b'## Proposed delivery plan\nPending.\n')

        def cli(root, action):
            command = [sys.executable, str(SCRIPTS / 'p2p_delivery.py'), '--repo', str(root), action, 'work/tiny.md']
            if action == 'run':
                command += ['--comparison-base', self.base, '--authorize-local', '--max-dispatches', '0']
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            return json.loads(result.stdout)

        self.assertIn('routing evidence unavailable', cli(self.root, 'run')['blocker'])
        self.assertFalse((self.root / '.p2p/work/tiny/delivery.json').exists())
        receipt.write_bytes(b'User approved these exact v1 destinations.\n')
        self.assertIn('dispatch-count limit', cli(self.root, 'run')['blocker'])
        workspace = self.root / '.p2p/work/tiny/runtime/workspace'
        self.assertEqual((workspace / receipt.relative_to(self.root)).read_bytes(), receipt.read_bytes())
        history = '.p2p/work/parent/history/' + d.fs.digest(original) + '/slicing.md'
        self.assertEqual((workspace / history).read_bytes(), original)
        self.assertEqual(self.state()['attempts'], [])

        recovered = Path(self.temp.name) / 'recovered'
        subprocess.run(['git', 'clone', '-q', str(self.root), str(recovered)], check=True)
        d.fs.git(recovered, 'branch', 'trunk', self.base)
        d.fs.git(recovered, 'branch', 'epic/tiny', self.base)
        shutil.copytree(workspace / 'work', recovered / 'work')
        shutil.copytree(workspace / '.p2p/work/parent', recovered / '.p2p/work/parent')
        self.assertIn('dispatch-count limit', cli(recovered, 'run')['blocker'])
        self.assertEqual((recovered / '.p2p/work/tiny/runtime/workspace/.p2p/work/parent/approval.md').read_bytes(), receipt.read_bytes())
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
        self.assertNotIn('sibling.txt', [e['path'] for e in self.state()['candidate']['manifest']])
        self.assertEqual(value['starting_commit'], self.base)
        self.assertNotEqual(self.state()['source_head'], self.base)
        self.assertEqual((self.root / 'sibling.txt').read_text(), 'unfinished sibling payload\n')
        self.assertEqual(d.fs.full_commit(self.root / '.p2p/work/tiny/runtime/workspace', 'HEAD'), self.base)

    def advance_target(self, parent=None):
        tree = d.fs.git(self.root, 'rev-parse', self.base + '^{tree}').decode().strip()
        args = ['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                '-c', 'user.email=fixture@localhost', 'commit-tree', tree]
        if parent is not None:
            args += ['-p', parent]
        tip = subprocess.check_output(args, input=('Fixture destination ' + str(time.time_ns()) + '\n').encode()).decode().strip()
        d.fs.git(self.root, 'update-ref', 'refs/heads/epic/tiny', tip)
        return tip

    def test_child_stale_admission_blocks_but_target_advance_preserves_completed_reports(self):
        self.planned_child()
        newer = self.advance_target(self.base)
        code, value = self.cli()
        self.assertEqual(code, 1)
        self.assertIn('comparison base conflicts with approved destination epic/tiny', value['blocker'])
        self.assertIn(newer, value['blocker'])
        self.assertEqual(self.fake.calls, [])
        d.fs.git(self.root, 'update-ref', 'refs/heads/epic/tiny', self.base)
        self.assertEqual(self.cli()[0], 0)
        before = self.state()
        admission = (self.root / '.p2p/work/tiny/admission.json').read_bytes()
        reports = {name: (self.root / '.p2p/work/tiny' / record['path']).read_bytes()
                   for name, record in before['reports'].items()}
        self.assertEqual(before['destination_observation']['relationship'], 'unchanged')
        d.fs.git(self.root, 'update-ref', 'refs/heads/epic/tiny', newer)
        code, value = self.cli('resume')
        self.assertEqual(code, 0, value)
        self.assertEqual(value['status'], 'REVIEWED_AND_PROVEN')
        self.assertEqual(value['comparison_base'], self.base)
        self.assertEqual(value['destination_observation']['observed_tip'], newer)
        self.assertEqual(value['destination_observation']['relationship'], 'fast-forward')
        self.assertIn('Compatibility with the current destination has not been established', value['acceptance_boundary'])
        after = self.state()
        for key in ('candidate', 'routing', 'reports', 'attempts'):
            self.assertEqual(after[key], before[key])
        self.assertEqual((self.root / '.p2p/work/tiny/admission.json').read_bytes(), admission)
        for name, record in before['reports'].items():
            self.assertEqual((self.root / '.p2p/work/tiny' / record['path']).read_bytes(), reports[name])
        self.assertEqual(self.fake.calls, ['preflight', 'preflight', 'implementation', 'review', 'proof'])
        code, value = self.cli('run', '--comparison-base', newer)
        self.assertEqual(code, 1)
        self.assertIn('cannot change persisted', value['blocker'])

    def test_busy_destination_during_stages_and_completion_keeps_frozen_base(self):
        self.planned_child()
        tips = [self.base]
        original = self.fake
        def moving(*args):
            result = original(*args)
            if self.fake.calls[-1] in ('implementation', 'review', 'proof'):
                tips.append(self.advance_target(tips[-1]))
            return result
        complete = d.Delivery.complete
        def moved_after_reports(delivery):
            self.assertEqual(set(delivery.state['reports']), {'implementation', 'review', 'proof'})
            tips.append(self.advance_target(tips[-1]))
            return complete(delivery)
        with patch.object(d, 'launch', moving), patch.object(d.Delivery, 'complete', moved_after_reports):
            code, value = self.cli()
        self.assertEqual(code, 0, value)
        self.assertEqual(len(tips), 5)
        self.assertEqual(value['destination_observation']['observed_tip'], tips[-1])
        self.assertEqual(value['comparison_base'], self.base)
        self.assertEqual(self.fake.calls, ['preflight', 'preflight', 'implementation', 'review', 'proof'])
        for report in self.state()['reports'].values():
            self.assertEqual(report['inputs']['comparison_base'], self.base)
            self.assertEqual(report['inputs']['routing']['target_tip'], self.base)
            self.assertNotIn('destination_observation', report['inputs'])

    def test_rewritten_and_missing_destination_are_observations_only(self):
        self.planned_child()
        self.assertEqual(self.cli()[0], 0)
        candidate = self.state()['candidate']
        unrelated = self.advance_target()
        code, value = self.cli('resume')
        self.assertEqual(code, 0, value)
        self.assertEqual(value['destination_observation']['relationship'], 'non-fast-forward')
        self.assertEqual(value['destination_observation']['observed_tip'], unrelated)
        d.fs.git(self.root, 'update-ref', '-d', 'refs/heads/epic/tiny')
        before = (self.root / '.p2p/work/tiny/delivery.json').read_bytes()
        code, value = self.cli('status')
        self.assertEqual(code, 0, value)
        self.assertEqual(value['destination_observation']['relationship'], 'unavailable')
        self.assertIsNone(value['destination_observation']['observed_tip'])
        self.assertEqual((self.root / '.p2p/work/tiny/delivery.json').read_bytes(), before)
        self.assertEqual(self.cli('resume')[0], 0)
        self.assertEqual(self.state()['destination_observation']['relationship'], 'unavailable')
        self.assertEqual(self.state()['candidate'], candidate)
        self.assertEqual(len(self.fake.calls), 5)

    def test_resume_missing_stages_after_destination_advance(self):
        self.planned_child()
        original = d.Delivery.stage
        def pause(delivery, name):
            if name == 'review':
                raise OSError('fixture pause before review dispatch')
            return original(delivery, name)
        with patch.object(d.Delivery, 'stage', pause):
            self.assertEqual(self.cli()[0], 1)
        candidate = self.state()['candidate']
        newer = self.advance_target(self.base)
        code, value = self.cli('resume')
        self.assertEqual(code, 0, value)
        self.assertEqual(self.state()['candidate'], candidate)
        self.assertEqual(value['destination_observation']['observed_tip'], newer)
        self.assertEqual(self.fake.calls, ['preflight', 'preflight', 'implementation', 'review', 'proof'])

    def test_moving_destination_does_not_hide_candidate_source_or_base_drift(self):
        self.planned_child()
        self.assertEqual(self.cli()[0], 0)
        newer = self.advance_target(self.base)
        directory = self.root / '.p2p/work/tiny'
        for relative, replacement, message in [
                ('runtime/workspace/greet.py', b"print('wrong')\n", 'product candidate changed'),
                ('candidate.json', b'{}', 'malformed candidate metadata'),
                ('delivery.json', d.encoded(dict(self.state(), comparison_base=newer)), 'persisted admission changed: comparison_base'),
                ('base-manifest.json', b'[]', 'retained comparison-base content changed'),
                ('runtime/repository.git/objects/' + self.base[:2] + '/' + self.base[2:], b'corrupt', None)]:
            path = directory / relative
            before = path.read_bytes()
            path.write_bytes(replacement)
            code, value = self.cli('resume')
            self.assertEqual(code, 1, value)
            if message is not None:
                self.assertIn(message, value['blocker'])
            path.write_bytes(before)
        # Source HEAD and index remain independent protections even for identical trees.
        head = d.fs.full_commit(self.root, 'HEAD')
        newer = self.advance_target(self.base)
        d.fs.git(self.root, 'update-ref', 'HEAD', newer)
        code, value = self.cli('resume')
        self.assertEqual(code, 1, value)
        self.assertIn('source HEAD changed', value['blocker'])
        d.fs.git(self.root, 'update-ref', 'HEAD', head)
        d.fs.git(self.root, 'add', 'work/tiny.md')
        code, value = self.cli('resume')
        self.assertEqual(code, 1, value)
        self.assertIn('source index changed', value['blocker'])

    def test_legacy_target_movement_blocker_resumes_without_rewriting_admission(self):
        self.planned_child()
        self.assertEqual(self.cli()[0], 0)
        directory = self.root / '.p2p/work/tiny'
        state = self.state()
        state.pop('destination_observation')
        state.update(status='BLOCKED', blocker='approved delivery plan or destination tip changed; reconcile routing and refresh review')
        (directory / 'delivery.json').write_bytes(d.encoded(state))
        admission = (directory / 'admission.json').read_bytes()
        newer = self.advance_target(self.base)
        code, value = self.cli('resume')
        self.assertEqual(code, 0, value)
        self.assertEqual(value['destination_observation']['observed_tip'], newer)
        self.assertEqual((directory / 'admission.json').read_bytes(), admission)
        self.assertEqual(self.state()['reports'], state['reports'])
        self.assertEqual(len(self.fake.calls), 5)

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
        parent_route = d.routing(self.root, 'work/parent.md')
        self.assertEqual(parent_route['destination'], 'trunk')
        self.assertEqual(parent_route['target_tip'], self.base)
        self.assertEqual(self.cli()[0], 0)
        workspace = self.root / '.p2p/work/tiny/runtime/workspace'
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
        review=(self.root/'.p2p/work/tiny/review.md').read_text()
        for heading in ('## Contract fidelity','## Scope and simplicity','## Engineering quality',
                        '## Checks and limitations','## Handoff','## Next steps',
                        'Review only; acceptance proof and merge readiness are separate.'):
            self.assertIn(heading,review)
        self.assertIn(f"Candidate: `{self.state()['candidate']['key']}`",review)
        self.assertIn('included working-tree scope:', review)
        self.assertIn('`greet.py`', review)
        self.assertIn('`work/tiny.md`', review)
        self.assertFalse((self.root / 'greet.py').exists())
        self.assertEqual((self.root / 'unrelated').read_text(), 'keep me')
        self.assertEqual((self.root / 'unrelated').stat().st_mode & 0o777, 0o755)
        self.assertEqual(os.readlink(self.root / 'link'), 'unrelated')
        state = self.state()
        manifest = state['candidate']['manifest']
        self.assertNotIn('unrelated', [x['path'] for x in manifest])
        restored = Path(self.temp.name) / 'restored'
        d.materialize(restored, manifest)
        self.assertEqual(subprocess.check_output([sys.executable, str(restored/'greet.py')]), b'hello\n')
        before = (self.root / '.p2p/work/tiny/delivery.json').read_bytes()
        self.assertEqual(self.cli('status')[0], 0)
        self.assertEqual(before, (self.root / '.p2p/work/tiny/delivery.json').read_bytes())
        self.assertEqual(self.cli('resume')[0], 0)
        self.assertEqual(len(self.fake.calls), 5)
        proof = self.root / '.p2p/work/tiny' / state['reports']['proof']['path']
        proof.write_text('{}')
        code, value = self.cli('resume')
        self.assertEqual(code,1)
        self.assertIn('report/evidence content changed',value['blocker'])

    def test_legacy_review_readback_uses_structured_summary(self):
        code,value=self.cli()
        self.assertEqual(code,0,value)
        state=self.state()
        report_record=state['reports']['review']
        attempt=next(a for a in state['attempts'] if a['id']==report_record['attempt_id'])
        folder=self.root/'.p2p/work/tiny/attempts'/attempt['id']
        report_path=self.root/'.p2p/work/tiny'/report_record['path']
        current=json.loads(report_path.read_bytes())
        legacy={'status':'REVIEWED','input_identity_json':current['input_identity_json'],
                'requirements':[dict(row,verdict='reviewed') for row in current['requirements']],
                'gaps':[],'details':'# REVIEWED\n\nLegacy free-text summary.'}
        report_bytes=d.encoded(legacy)
        report_path.write_bytes(report_bytes)
        for path in (self.root/'.p2p/work/tiny/review.md',folder/'report.md'):
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
        (self.root/'.p2p/work/tiny/delivery.json').write_bytes(d.encoded(state))
        calls=len(self.fake.calls)
        self.assertEqual(self.cli('status')[0],0)
        self.assertEqual(self.cli('resume')[0],0)
        self.assertEqual(len(self.fake.calls),calls)
        bundle=json.loads((self.root/'.p2p/work/tiny/acceptance-bundle.json').read_bytes())
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

    def test_missing_authority_dispatches_nothing(self):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            code=d.main(['--repo',str(self.root),'run','work/tiny.md','--comparison-base',self.base])
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
        code,value=self.cli()
        self.assertEqual(code,1,value)
        self.assertIn('repair exhausted',value['blocker'])
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
        self.assertIn('review BLOCKED',value['blocker'])
        self.assertEqual(self.fake.calls,['preflight','preflight','implementation','review'])
        report=(self.root/'.p2p/work/tiny/review.md').read_text()
        self.assertIn('configured command `python3 greet.py`',report)
        self.assertIn('exit zero and print `hello\\n`',report)
        code,value=self.cli('resume')
        self.assertEqual(code,1,value)
        self.assertIn('review BLOCKED',value['blocker'])
        self.assertEqual(self.fake.calls,['preflight','preflight','implementation','review','review'])
        self.assertNotIn('proof',self.fake.calls)
        self.assertNotIn('repair',self.fake.calls)

    def test_plan_acceptance_handoff_stops_before_proof_and_repair(self):
        self.fake.mode='review-plan-handoff'
        code,value=self.cli()
        self.assertEqual(code,1,value)
        self.assertIn('requires plan-acceptance',value['blocker'])
        self.assertEqual(self.fake.calls,['preflight','preflight','implementation','review'])

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
        self.assertEqual(state['limits']['dispatches'],8)
        self.assertEqual(state['host']['cost'],'unknown')

    def test_persisted_scope_cannot_widen(self):
        self.cli('run','--max-dispatches','0')
        path=self.root/'.p2p/work/tiny/delivery.json'
        state=json.loads(path.read_text())
        state['limits']['dispatches']=999
        path.write_text(json.dumps(state))
        code,value=self.cli('resume')
        self.assertEqual(code,1)
        self.assertIn('persisted admission changed: limits',value['blocker'])
        self.assertEqual(self.fake.calls,[])

    def test_finite_defaults_progress_and_read_only_status(self):
        progress=io.StringIO()
        with contextlib.redirect_stderr(progress):
            code,value=self.cli()
        self.assertEqual(code,0,value)
        self.assertEqual(value['limits'],{'dispatches':8,'elapsed_seconds':1800,'stage_seconds':600})
        self.assertIn('implementation started',progress.getvalue())
        self.assertIn('proof finished',progress.getvalue())
        self.assertEqual(value['progress']['stage'],'proof')
        self.assertIsNotNone(value['progress']['last_activity_at'])
        self.assertEqual(value['progress']['elapsed_seconds'],0.01)
        before=(self.root/'.p2p/work/tiny/delivery.json').read_bytes()
        self.assertEqual(self.cli('status')[0],0)
        self.assertEqual(before,(self.root/'.p2p/work/tiny/delivery.json').read_bytes())

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
        for limit in ('-1','nan','inf'):
            code,value=self.cli('run','--max-stage-seconds',limit)
            self.assertEqual(code,1,value)
            self.assertIn('finite and nonnegative',value['blocker'])
            self.assertFalse((self.root/'.p2p/work/tiny/delivery.json').exists())

    def test_zero_stage_limit_never_dispatches(self):
        code,value=self.cli('run','--max-stage-seconds','0')
        self.assertEqual(code,1,value)
        self.assertIn('stage elapsed-time limit',value['blocker'])
        self.assertEqual(self.fake.calls,[])

    def test_unavailable_progress_does_not_hide_identity_blocker(self):
        self.cli('run','--max-dispatches','0')
        path=self.root/'.p2p/work/tiny/delivery.json'
        state=self.state()
        state['attempts']=[{'id':'pending','stage':'implementation','status':'reserved',
                            'started_epoch':time.time(),'finished':None,'elapsed_seconds':'unknown'}]
        path.write_bytes(d.encoded(state))
        (self.root/'spec.txt').write_text('changed source')
        original_open,original_stat=Path.open,Path.stat
        def unavailable_open(path,*args,**kwargs):
            if path.name=='delivery.lock':
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
                path=self.root/'.p2p/work/tiny/delivery.json'
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
        directory=self.root/'.p2p/work/tiny'
        for name in ('delivery.json','admission.json'):
            path=directory/name
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
        with patch.object(d,'HEARTBEAT_SECONDS',0.03), contextlib.redirect_stderr(progress):
            result=d.launch([sys.executable,'-c',command],
                            '',events,errors,time.time()+0.3)
        self.assertEqual(result['outcome'],'interrupted')
        self.assertLess(time.monotonic()-started,3)
        self.assertNotEqual(result['exit_code'],0)
        self.assertIn('log activity',progress.getvalue())
        self.assertIn('activity\n',events.read_text())
        self.assertIn('child-ready\n',events.read_text())
        time.sleep(0.9)
        self.assertFalse(marker.exists(),'worker child survived process-group termination')

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
        code = "import sys;sys.path.insert(0," + repr(str(Path(__file__).parent)) + ");import test_p2p_delivery as t;d=t.d;d.launch=t.FakeTransport();" + setup + ";sys.exit(d.main(sys.argv[1:]))"
        args=[sys.executable,'-c',code,'--repo',str(self.root),action,'work/tiny.md']
        if action=='run':args+=['--comparison-base',self.base,'--authorize-local']
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
        with (self.root/'.p2p/work/tiny/delivery.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            other=self.subprocess_cli('pass','resume')
        self.assertEqual(other.returncode,1)
        self.assertIn('another controller holds',other.stdout)
        self.assertEqual(len(self.state()['attempts']),0)

    def test_concurrent_worktree_deliveries_share_moving_destination(self):
        """Real controller processes and Git worktrees; stage transport remains a fixture."""
        plan = self.planned_child()
        coordination = Path(self.temp.name) / 'coordination'
        coordination.mkdir()
        processes, roots = [], []
        script = '''import sys, time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import test_p2p_delivery as t
d = t.d
d.platform.system = lambda: 'Darwin'
root, base, gates = Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
transport = t.FakeTransport()
def pause(stage):
    (gates / (root.name + '-' + stage)).touch()
    deadline = time.monotonic() + 60
    while not (gates / ('release-' + stage)).exists():
        if time.monotonic() > deadline:
            raise TimeoutError('fixture coordination timed out: ' + stage)
        time.sleep(0.02)
def launch(*args):
    result = transport(*args)
    stage = transport.calls[-1]
    if stage in ('implementation', 'review', 'proof'):
        pause(stage)
    return result
d.launch = launch
complete = d.Delivery.complete
def completing(delivery):
    pause('completion')
    return complete(delivery)
d.Delivery.complete = completing
sys.exit(d.main(['--repo', str(root), 'run', 'work/tiny.md', '--comparison-base', base, '--authorize-local']))
'''
        tip = self.base
        try:
            for name in ('first', 'second'):
                root = Path(self.temp.name) / name
                d.fs.git(self.root, 'worktree', 'add', '--detach', str(root), self.base)
                shutil.copytree(self.root / 'work', root / 'work')
                d.fs.save(root, 'work/parent.md', 'slicing.md', plan.read_bytes())
                roots.append(root)
                processes.append(subprocess.Popen([sys.executable, '-c', script, str(Path(__file__).parent),
                                                   str(root), self.base, str(coordination)],
                                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
            for stage in ('implementation', 'review', 'proof', 'completion'):
                deadline = time.monotonic() + 60
                while not all((coordination / (root.name + '-' + stage)).exists() for root in roots):
                    for process in processes:
                        if process.poll() is not None:
                            stdout, stderr = process.communicate()
                            self.fail('controller exited before ' + stage + ': ' + stdout + stderr)
                    if time.monotonic() > deadline:
                        self.fail('controllers did not both reach ' + stage)
                    time.sleep(0.02)
                self.assertTrue(all(process.poll() is None for process in processes))
                tip = self.advance_target(tip)
                for root in roots:
                    self.assertEqual(d.fs.full_commit(root, 'refs/heads/epic/tiny'), tip)
                    self.assertEqual(d.fs.full_commit(root, 'HEAD'), self.base)
                (coordination / ('release-' + stage)).touch()
            invocations = set()
            for root, process in zip(roots, processes):
                stdout, stderr = process.communicate(timeout=30)
                self.assertEqual(process.returncode, 0, stdout + stderr)
                value = json.loads(stdout)
                self.assertEqual(value['status'], 'REVIEWED_AND_PROVEN')
                self.assertEqual(value['destination_observation']['observed_tip'], tip)
                self.assertEqual(value['destination_observation']['relationship'], 'fast-forward')
                self.assertEqual(value['comparison_base'], self.base)
                self.assertEqual([a['stage'] for a in value['attempts']],
                                 ['preflight-1', 'preflight-2', 'implementation', 'review', 'proof'])
                invocations.add(value['invocation_id'])
                for name in ('review', 'proof'):
                    self.assertEqual(value['reports'][name]['inputs']['comparison_base'], self.base)
                # Read back through a separate process: moving refs do not cause redispatch.
                resumed = subprocess.run([sys.executable, str(SCRIPTS / 'p2p_delivery.py'), '--repo', str(root),
                                          'resume', 'work/tiny.md'], capture_output=True, text=True, timeout=30)
                self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
                self.assertEqual(json.loads(resumed.stdout)['attempts'], value['attempts'])
            self.assertEqual(len(invocations), 2)
        finally:
            for process in processes:
                if process.poll() is None:
                    process.kill()
                process.communicate()

    def test_reconstruct_candidate_with_retained_base(self):
        self.assertEqual(self.cli()[0],0)
        state=self.state()
        restored=Path(self.temp.name)/'fresh'
        metadata=Path(self.temp.name)/'fresh.git'
        archive=self.root/'.p2p/work/tiny/runtime/base.bundle'
        subprocess.run(['git','clone','--bare',str(archive),str(metadata)],check=True,capture_output=True)
        d.materialize(restored,state['candidate']['manifest'])
        (restored/'.git').write_text('gitdir: '+str(metadata)+'\n')
        d.fs.git(restored,'config','core.bare','false')
        d.fs.git(restored,'read-tree',state['source_head'])
        d.fs.save(restored,'work/tiny.md','candidate.json',d.encoded(state['candidate']))
        self.assertEqual(d.fs.validate(restored,'work/tiny.md',self.base),state['candidate'])

    def test_source_agreement_binding_base_and_report_loss(self):
        self.assertEqual(self.cli()[0],0)
        for relative,replacement in [('work/tiny.md',CONTRACT+'same revision changed bytes\n'),
                                      ('spec.txt','changed binding\n'),
                                      ('.p2p/work/tiny/base-manifest.json','[]'),
                                      ('.p2p/work/tiny/proof.md','truncated')]:
            file=self.root/relative
            previous=file.read_bytes()
            file.write_text(replacement)
            code,value=self.cli('status')
            self.assertEqual(code,1,(relative,value))
            self.assertEqual(value['status'],'BLOCKED')
            file.write_bytes(previous)
        self.assertEqual(self.cli('status')[0],0)

    def test_storage_failure_is_recoverable_from_exact_host_return(self):
        original=d.retained
        def fail(root,work,name,data):
            if name=='proof.md': raise OSError('fixture evidence destination unavailable')
            return original(root,work,name,data)
        with patch.object(d,'retained',fail):
            code,value=self.cli()
        self.assertEqual(code,1)
        self.assertIn('destination unavailable',value['blocker'])
        before=len(self.fake.calls)
        self.assertEqual(self.cli('resume')[0],0)
        self.assertEqual(len(self.fake.calls),before)

    def test_atomic_storage_preserves_old_bytes_on_replace_failure(self):
        directory=self.root/'.p2p/work/tiny'
        d.fs.save(self.root,'work/tiny.md','storage.txt',b'old')
        original=d.fs.os.replace
        def fail(source,target):
            if Path(target)==directory/'storage.txt':raise OSError('fixture interrupted replacement')
            return original(source,target)
        with patch.object(d.fs.os,'replace',fail):
            with self.assertRaises(OSError):d.fs.save(self.root,'work/tiny.md','storage.txt',b'new')
        self.assertEqual((directory/'storage.txt').read_bytes(),b'old')
        self.assertEqual((directory/'history'/d.fs.digest(b'old')/'storage.txt').read_bytes(),b'old')

    def test_agreement_and_candidate_drift(self):
        self.assertEqual(self.cli()[0],0)
        state=self.state()
        candidate=self.root/'.p2p/work/tiny/runtime/workspace/greet.py'
        candidate.write_text("print('wrong')\n")
        code,value=self.cli('resume')
        self.assertEqual(code,1);self.assertIn('product candidate changed',value['blocker'])


if __name__ == '__main__':
    unittest.main()
