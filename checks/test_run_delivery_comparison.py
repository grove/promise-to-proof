#!/usr/bin/env python3
"""Offline runner checks. No model calls and no delivered candidate execution."""
import contextlib
import io
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import run_delivery_comparison as pilot

HOST = {'model': 'fixture-model', 'reasoning': 'fixture', 'version': 'fixture', 'skills': {}}
AGREEMENT_BASE = 'eb84d66dd70ce8998cd43e951741785e8520c301'


@contextlib.contextmanager
def historical_agreement():
    """Supply the pilot's exact old agreement without restoring local workflow state."""
    relative = 'work/fixed-delivery-strategy-comparison.md'
    path = pilot.PROJECT / relative
    agreement = subprocess.check_output(
        ['git', '-C', str(pilot.PROJECT), 'show', f'{AGREEMENT_BASE}:{relative}'])
    read_bytes = Path.read_bytes

    def fixture_bytes(source):
        return agreement if source == path else read_bytes(source)

    # The repository intentionally removed old work/ agreements in 5f163407.
    # This fixture retains the original bytes, not a replacement pilot agreement.
    with patch.object(Path, 'read_bytes', fixture_bytes):
        yield agreement


class PilotTests(unittest.TestCase):
    def test_preparation_order_identity_and_uncertain_repeat(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(pilot, 'configured', return_value=HOST), \
                historical_agreement() as agreement:
            root = Path(temp) / 'pilot'
            manifest = pilot.prepare(root)
            self.assertEqual((root / 'evaluation/pilot-contract.md').read_bytes(), agreement)
            self.assertEqual(manifest['pilot_contract_sha256'], pilot.d.fs.digest(agreement))
            self.assertEqual(len(manifest['episodes']), 6)
            self.assertEqual([e['strategy'] for e in manifest['episodes']],
                             ['review-first', 'proof-first', 'proof-first', 'review-first', 'review-first', 'proof-first'])
            a = (root / 'controllers/review-first' / pilot.SCRIPT).read_text()
            b = (root / 'controllers/proof-first' / pilot.SCRIPT).read_text()
            self.assertEqual(b, a.replace(pilot.ORDER, pilot.ORDER.replace("'review', 'proof'", "'proof', 'review'")))
            for task in pilot.TASKS:
                pair = [e for e in manifest['episodes'] if e['task'] == task]
                self.assertEqual(pair[0]['input_manifest'], pair[1]['input_manifest'])
                self.assertEqual(pair[0]['base'], pair[1]['base'])
                self.assertFalse(any('oracle' in e['path'] for e in pair[0]['input_manifest']))
            episode = manifest['episodes'][0]
            folder = root / 'episodes' / episode['id']
            pilot.save(folder / 'started.json', {'started': 3})
            with patch.object(pilot.subprocess, 'run') as run:
                with self.assertRaisesRegex(ValueError, 'uncertain'):
                    pilot.run_episode(root, manifest, episode)
                run.assert_not_called()
            assumptions = [{'name': 'test only', 'provenance': 'synthetic fixture'}]
            pilot.save(root / 'evaluation/sensitivity.json', assumptions)
            result = pilot.collect(root, manifest)
            self.assertEqual(result['sensitivity'], assumptions)
            self.assertEqual(len(result['episodes']), 6)
            self.assertTrue(all(e['evidence'] == 'unexecuted' for e in result['episodes']))
            self.assertIsNone(result['episodes'][0]['end'])
            self.assertEqual(result['episodes'][0]['adjudication']['outcome'], 'unresolved')
            self.assertEqual(result['overhead']['costs'], [{'kind': 'unknown'}])
            records = root / episode['source'] / '.p2p/work' / episode['task']
            attempt = {'id': 'known-attempt', 'inputs': {}, 'stage': 'preflight-1',
                       'status': 'reserved', 'started': '2026-09-26T00:00:00+00:00'}
            pilot.save(records / 'delivery.json', {'attempts': [attempt]})
            receipt_folder = records / 'attempts/known-attempt'
            receipt_folder.mkdir(parents=True)
            events = [{'type': 'thread.started', 'thread_id': 'fixture'},
                      {'type': 'turn.completed', 'usage': {'input_tokens': 7}}]
            event_path = receipt_folder / 'events.jsonl'
            event_path.write_text(''.join(json.dumps(e) + '\n' for e in events))
            pilot.save(receipt_folder / 'exit.json', {
                'attempt_id': 'known-attempt', 'inputs': {}, 'finished': '2026-09-26T00:00:02+00:00',
                'event_sha256': pilot.d.fs.digest(event_path.read_bytes())})
            collected = pilot.collect(root, manifest)['episodes'][0]['attempts']
            self.assertEqual(len(collected), 1)
            self.assertEqual(collected[0]['end'] - collected[0]['start'], 2)
            self.assertEqual(collected[0]['usage'], {'input_tokens': 7})
            self.assertEqual(collected, pilot.collect(root, manifest)['episodes'][0]['attempts'])
            event_path.write_text('changed')
            with self.assertRaisesRegex(ValueError, 'conflicting completion'):
                pilot.collect(root, manifest)
            with self.assertRaises(FileExistsError):
                pilot.prepare(root)
            with patch.object(pilot, 'configured', return_value={**HOST, 'model': 'changed'}):
                with self.assertRaisesRegex(ValueError, 'changed'):
                    pilot.validate(root, manifest)

    def test_blocked_episode_stops_cohort_and_post_run_configuration_drift(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(pilot, 'configured', return_value=HOST), \
                historical_agreement():
            root = Path(temp) / 'pilot'
            manifest = pilot.prepare(root)
            with patch.object(pilot, 'run_episode', return_value={'returncode': 1}) as run, \
                    patch.object(pilot, 'collect') as collect, \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(pilot.main(['run', '--output-dir', str(root), '--authorize-live']), 1)
                self.assertEqual(run.call_count, 1)
                collect.assert_called_once()
            episode = manifest['episodes'][0]
            with patch.object(pilot, 'validate', side_effect=[None, ValueError('configuration drift')]) as validate, \
                    patch.object(pilot.d.fs, 'snapshot', return_value=episode['input_manifest']), \
                    patch.object(pilot.d.fs, 'full_commit', return_value=episode['base']), \
                    patch.object(pilot.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)) as dispatch:
                with self.assertRaisesRegex(ValueError, 'configuration drift'):
                    pilot.run_episode(root, manifest, episode)
                self.assertEqual(validate.call_count, 2)
                dispatch.assert_called_once()
            # The completed process stays recorded even when the post-run configuration check fails.
            self.assertTrue((root / 'episodes' / episode['id'] / 'finished.json').exists())

    def test_copied_controllers_repair_order_and_exhaustion(self):
        from test_p2p_delivery import CONTRACT, FakeTransport, fixture_host, repo

        class BaselineTransport:
            def __init__(self, mode):
                self.transport = FakeTransport(mode)
                self.calls = self.transport.calls

            def __call__(self, args, prompt, event_path, error_path, deadline):
                result = self.transport(args, prompt, event_path, error_path, deadline)
                attempt = json.loads((event_path.parent / 'launch.json').read_text())
                if attempt['stage'] != 'review':
                    return result
                events = [json.loads(line) for line in event_path.read_text().splitlines()]
                for event in events:
                    item = event.get('item', {})
                    if item.get('type') != 'agent_message':
                        continue
                    report = json.loads(item['text'])
                    if report.get('status') == 'REVIEWED':
                        report.setdefault('details', 'FIXTURE review; not live evidence.')
                        for row in report['requirements']:
                            row.setdefault('verdict', 'reviewed')
                        item['text'] = json.dumps(report)
                event_path.write_text(''.join(json.dumps(event) + '\n' for event in events))
                return result

        with tempfile.TemporaryDirectory() as temp, patch.object(pilot, 'configured', return_value=HOST), \
                historical_agreement():
            destination = Path(temp) / 'pilot'
            pilot.prepare(destination)
            for strategy in pilot.STRATEGIES:
                script = destination / 'controllers' / strategy / pilot.SCRIPT
                spec = importlib.util.spec_from_file_location('pilot_controller', script)
                controller = importlib.util.module_from_spec(spec)
                current_filesystem = sys.modules.pop('p2p_filesystem', None)
                sys.path.insert(0, str(script.parent))
                try:
                    spec.loader.exec_module(controller)
                finally:
                    sys.path.remove(str(script.parent))
                    sys.modules.pop('p2p_filesystem', None)
                    if current_filesystem is not None:
                        sys.modules['p2p_filesystem'] = current_filesystem
                order = ['review', 'proof'] if strategy == 'review-first' else ['proof', 'review']
                for mode in ('repair', 'exhausted'):
                    with self.subTest(strategy=strategy, mode=mode):
                        root = Path(temp) / (strategy + '-' + mode)
                        base = repo(root)
                        # CONTROLLER_BASE predates ignored repo-local P2P state and expects these records trackable.
                        (root / '.gitignore').write_text('')
                        (root / 'work/tiny.md').write_text(CONTRACT.replace('../../../spec.txt', '../spec.txt'))
                        subprocess.run(['git', '-C', str(root), 'add', '--', '.gitignore', 'work/tiny.md'], check=True)
                        subprocess.run(['git', '-C', str(root), '-c', 'user.name=Fixture',
                                        '-c', 'user.email=fixture@localhost', 'commit', '-qm',
                                        'Add legacy contract fixture'], check=True)
                        base = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
                        subprocess.run(['git', '-C', str(root), 'update-ref', 'refs/heads/delivery-target', base],
                                       check=True)
                        fake = BaselineTransport(mode)
                        args = ['--repo', str(root), 'run', 'work/tiny.md', '--comparison-base', base,
                                '--authorize-local', '--max-dispatches', '8', '--max-seconds', '1800']
                        # This pinned controller predates installed_skill(). Its
                        # discovery still uses the same repository-backed fixture skills.
                        with fixture_host(), patch.object(controller, 'launch', fake), \
                                patch.object(controller, 'skills', side_effect=lambda: {
                                    stage: pilot.d.installed_skill(name)
                                    for stage, name in controller.STAGES.items()}), \
                                contextlib.redirect_stdout(io.StringIO()):
                            code = controller.main(args)
                            state = json.loads((root / '.p2p/work/tiny/delivery.json').read_text())
                            self.assertEqual(code, 0 if mode == 'repair' else 1, state.get('blocker'))
                            self.assertEqual(fake.calls, ['preflight', 'preflight', 'implementation'] + order + ['repair'] + order)
                            self.assertEqual(state['limits'], {'dispatches': 8, 'elapsed_seconds': 1800})
                            self.assertTrue(state['repair_used'])
                            self.assertEqual(len(state['attempts']), 8)
                            for name in ('review', 'proof'):
                                report = json.loads((root / '.p2p/work/tiny' / state['reports'][name]['path']).read_text())
                                self.assertEqual(json.loads(report['input_identity_json']), controller.identity(state['candidate']))
                                self.assertEqual([row['id'] for row in report['requirements']], ['R1'])
                            if mode == 'repair':
                                bundle = json.loads((root / '.p2p/work/tiny/acceptance-bundle.json').read_text())
                                self.assertEqual(controller.bundle.verify_bundle(bundle), [])
                            else:
                                self.assertIn('repair exhausted', state['blocker'])
                            self.assertEqual(controller.main(['--repo', str(root), 'resume', 'work/tiny.md']), code)
                            self.assertEqual(len(fake.calls), 8)

    def test_oracle_against_known_behavior_and_swallowed_error(self):
        # Only trusted, fixed fixture code authored here executes without a sandbox.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            oracle = root / 'oracle.py'
            oracle.write_text(pilot.ORACLE)
            candidate = root / 'candidate'
            candidate.mkdir()
            (candidate / 'greet.py').write_text("print('hello')\n")
            good = 'from pathlib import Path\ndef save_report(path, text):\n    Path(path).write_text(text, encoding="utf-8")\n'
            (candidate / 'report.py').write_text(good)
            for task in ('greeting', 'save-report'):
                scratch = root / task
                scratch.mkdir()
                result = subprocess.run([sys.executable, '-B', str(oracle), str(candidate), task], cwd=scratch, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            (candidate / 'report.py').write_text('from pathlib import Path\ndef save_report(path, text):\n    try:\n        Path(path).write_text(text, encoding="utf-8")\n    except OSError:\n        pass\n')
            result = subprocess.run([sys.executable, '-B', str(oracle), str(candidate), 'repair-report'], cwd=root / 'save-report', capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b'I/O error was swallowed', result.stderr)


if __name__ == '__main__':
    unittest.main()
