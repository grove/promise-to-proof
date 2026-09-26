#!/usr/bin/env python3
"""Deterministic fixture transport tests. These are NOT live host evidence."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
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
        self.mode, self.calls = mode, []

    def __call__(self, args, prompt, event_path, error_path, deadline):
        attempt = json.loads((event_path.parent / 'launch.json').read_text())
        inputs = attempt['inputs']
        stage = 'preflight' if 'probe_sha256' in inputs else attempt['stage']
        self.calls.append(stage)
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
            report = {'status':status, 'input_identity_json':json.dumps(inputs),
                      'requirements':[row], 'details':'# ' + status + '\n\nFIXTURE ONLY; full R1 observation retained.',
                      'gaps':['fixture gap'] if gap else []}
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

    def test_success_source_preservation_and_retrieval(self):
        (self.root / 'unrelated').write_text('keep me')
        os.chmod(self.root / 'unrelated', 0o755)
        (self.root / 'link').symlink_to('unrelated')
        code, value = self.cli('run', '--exclude-dirty', 'unrelated', '--exclude-dirty', 'link')
        self.assertEqual(code, 0, value)
        self.assertEqual(value['status'], 'REVIEWED_AND_PROVEN')
        self.assertEqual(self.fake.calls, ['preflight','preflight','implementation','review','proof'])
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
        path=self.root/'.p2p/work/tiny/delivery.json'
        state=json.loads(path.read_text())
        state['limits']['dispatches']=999
        path.write_text(json.dumps(state))
        code,value=self.cli('resume')
        self.assertEqual(code,1)
        self.assertIn('persisted admission changed: limits',value['blocker'])
        self.assertEqual(self.fake.calls,[])

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
