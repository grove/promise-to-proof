"""Portable handoffs in disposable repositories; no live model or GitHub calls."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import test_p2p_delivery as fixture

d = fixture.d


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture.DeliveryTests('test_clean_project_delivery_uses_local_contract_and_records')
        self.fixture.setUp()
        self.root = self.fixture.root
        self.work = '.p2p/work/tiny/contract.md'

    def tearDown(self):
        self.fixture.tearDown()

    def publish_fixture(self, checkpoint):
        remote = Path(self.fixture.temp.name) / 'remote.git'
        d.fs.git(self.root, 'init', '--bare', '-q', str(remote))
        if checkpoint['candidate_commit']:
            d.fs.git(self.root, 'branch', 'checkpoint-candidate', checkpoint['candidate_commit'])
        d.fs.git(self.root, 'add', 'p2p-state')
        d.fs.git(self.root, 'commit', '-qm', 'Preserve checkpoint')
        d.fs.git(self.root, 'push', '-q', str(remote), '--all')
        clone = Path(self.fixture.temp.name) / 'different-computer'
        subprocess.run(['git', 'clone', '-q', str(remote), str(clone)], check=True)
        return remote, clone

    def test_planning_round_trip_preserves_approval_history_without_scratch(self):
        owner = self.root / '.p2p/work/tiny'
        historical = owner / 'history' / d.fs.digest(b'approved earlier text\r\n') / 'contract.md'
        historical.parent.mkdir(parents=True)
        historical.write_bytes(b'approved earlier text\r\n')
        receipt = f'Approval: "I approve"\nApproval source: [exact proposal](history/{historical.parent.name}/contract.md)\n'
        d.fs.save(self.root, self.work, 'planning-handoff.md', receipt.encode())
        (owner / 'scratch.log').write_text('x' * 1000000)
        checkpoint_path = self.root / 'p2p-state/tiny.json'
        data = checkpoint_path.read_bytes()
        value = json.loads(data)
        self.assertLess(len(data), 10000)
        self.assertNotIn('scratch.log', data.decode())
        remote, clone = self.publish_fixture(value)
        self.assertEqual(d.fs.checkpoint_status(self.root, self.work, str(remote))['status'], 'PORTABLE')
        source = self.root / 'spec.txt'
        original_source = source.read_bytes()
        source.write_bytes(b'new local requirements\n')
        with self.assertRaisesRegex(ValueError, 'checkpoint is stale'):
            d.fs.checkpoint_status(self.root, self.work, str(remote))
        source.write_bytes(original_source)
        shutil.rmtree(self.root / '.p2p')
        result = d.fs.restore_checkpoint(clone, data)
        self.assertEqual(result['status'], 'RESTORED')
        self.assertEqual((clone / self.work).read_bytes(), (self.root / self.work).read_bytes() if (self.root / self.work).exists()
                         else next(text.encode() for text in value['texts'].values() if text.startswith('# Acceptance contract: tiny')))
        self.assertEqual((clone / '.p2p/work/tiny/planning-handoff.md').read_bytes(), receipt.encode())
        self.assertEqual((clone / historical.relative_to(self.root)).read_bytes(), b'approved earlier text\r\n')
        self.assertEqual(d.fs.restore_checkpoint(clone, data)['status'], 'RESTORED')

    def test_conflicts_tampering_and_size_limit_preserve_previous_checkpoint(self):
        saved = d.fs.checkpoint(self.root, self.work)
        path = self.root / saved['path']
        before = path.read_bytes()
        value = json.loads(before)
        clone = Path(self.fixture.temp.name) / 'conflict'
        subprocess.run(['git', 'clone', '-q', str(self.root), str(clone)], check=True)
        (clone / 'spec.txt').write_text('human edit\n')
        with self.assertRaisesRegex(ValueError, 'conflicts with local file'):
            d.fs.restore_checkpoint(clone, before)
        self.assertFalse((clone / self.work).exists())
        self.assertEqual((clone / 'spec.txt').read_text(), 'human edit\n')
        bad = copy.deepcopy(value)
        bad['files'][0]['path'] = '../escape'
        with self.assertRaisesRegex(ValueError, 'unsafe repository path'):
            d.fs.restore_checkpoint(clone, d.fs.canonical(bad))
        bad = copy.deepcopy(value)
        sha = next(iter(bad['texts']))
        bad['texts'][sha] += 'tampered'
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            d.fs.restore_checkpoint(clone, d.fs.canonical(bad))
        with self.assertRaisesRegex(ValueError, '256 KiB'):
            d.fs.save(self.root, self.work, 'planning-handoff.md', b'essential approval\n' + b'x' * d.fs.CHECKPOINT_LIMIT)
        self.assertEqual(path.read_bytes(), before)
        self.assertTrue((self.root / '.p2p/work/tiny/planning-handoff.md').exists())
        with self.assertRaisesRegex(ValueError, 'destination changed'):
            d.fs.checkpoint(self.root, self.work, {'kind': 'github', 'repository': 'owner/repo', 'issue': 1})

    def test_completed_stage_resumes_on_another_computer_without_old_execution(self):
        # Stop at a completed review boundary; proof has not dispatched.
        with patch.object(d.Delivery, 'stage', autospec=True, side_effect=self.stop_before_proof(d.Delivery.stage)):
            code, result = self.fixture.cli()
        self.assertEqual(code, 1, result)
        self.assertIn('fixture transfer boundary', result['blocker'])
        path = self.root / 'p2p-state/tiny.json'
        value = json.loads(path.read_bytes())
        self.assertIsNotNone(value['execution'], result.get('checkpoint'))
        self.assertLess(path.stat().st_size, d.fs.CHECKPOINT_LIMIT)
        self.assertEqual(set(value['execution']['reports']), {'implementation', 'review'})
        self.assertFalse(any(row['path'].endswith(('events.jsonl', 'launch.json', 'stderr.txt')) for row in value['files']))
        remote, clone = self.publish_fixture(value)
        self.assertEqual(d.fs.checkpoint_status(self.root, self.work, str(remote))['status'], 'PORTABLE')
        local_state = self.root / '.p2p/work/tiny/delivery.json'
        original_state = local_state.read_bytes()
        uncertain = json.loads(original_state)
        uncertain['attempts'].append({'id': 'not-yet-reconciled', 'status': 'reserved'})
        local_state.write_bytes(d.encoded(uncertain))
        with self.assertRaisesRegex(ValueError, 'uncertain dispatch prevents portability'):
            d.fs.checkpoint_status(self.root, self.work, str(remote))
        local_state.write_bytes(original_state)
        delivery = d.Delivery(self.root, self.work, json.loads(original_state))
        delivery.source_stable()  # Committing checkpoint metadata preserves admission.
        with patch.object(d, 'controller_running', return_value=None):
            with self.assertRaisesRegex(ValueError, 'stop the active controller'):
                d.fs.checkpoint_status(self.root, self.work, str(remote))
        published_bytes = path.read_bytes()
        self.assertEqual(d.export_checkpoint(self.root, self.work)['status'], 'LOCAL_ONLY')
        d.fs.read_checkpoint(self.root, path.read_bytes())
        path.write_bytes(published_bytes)
        unrecoverable_source = copy.deepcopy(value)
        unrecoverable_source['execution']['source_tree_key'] = '0' * 64
        _, inputs = d.fs.read_checkpoint(self.root, published_bytes)
        with self.assertRaisesRegex(ValueError, 'source admission has no recoverable Git commit'):
            d.fs.checkpoint_current(self.root, unrecoverable_source, inputs)
        before_key = value['execution']['candidate']['key']
        before_review = value['execution']['reports']['review']['sha256']
        shutil.rmtree(self.root / '.p2p')
        shutil.rmtree(Path(self.fixture.temp.name) / 'home/.p2p')
        restored = d.fs.restore_checkpoint(clone, path.read_bytes())
        self.assertEqual(restored['status'], 'RESTORED')
        code, result = self.fixture.run_root(clone, self.work, self.fixture.base, 'resume')
        self.assertEqual(code, 0, result)
        self.assertEqual(result['status'], 'REVIEWED_AND_PROVEN')
        self.assertEqual(result['candidate']['key'], before_key)
        state = json.loads((clone / '.p2p/work/tiny/delivery.json').read_bytes())
        self.assertEqual(state['reports']['review']['sha256'], before_review)
        stages = [a['stage'] for a in state['attempts']]
        self.assertEqual(stages.count('implementation'), 1)
        self.assertEqual(stages.count('review'), 1)
        self.assertEqual(stages.count('proof'), 1)
        self.assertEqual(stages.count('prior-preflight-1'), 1)
        self.assertEqual(stages.count('preflight-1'), 1)
        self.assertEqual(state['comparison_base'], self.fixture.base)
        proof_attempt = next(a for a in state['attempts'] if a['stage'] == 'proof')
        proof_environment = proof_attempt['verification_environment']
        state['restored_host']['version'] = 'later host version'
        delivery = d.Delivery(clone, self.work, state)
        with patch.object(d, 'skills', return_value=state['skills']):
            delivery.complete()
        acceptance = json.loads((delivery.runtime / 'acceptance-bundle.json').read_bytes())
        self.assertEqual(acceptance['proof']['verification_context'], proof_environment)
        self.assertIn(proof_environment, state['final_proof'])

    def test_github_publication_is_exact_idempotent_and_reconciles_lost_response(self):
        destination = {'kind': 'github', 'repository': 'owner/repo', 'issue': 42}
        source = Path(self.fixture.temp.name) / 'approved-contract.md'
        source.write_bytes((self.root / self.work).read_bytes())
        (self.root / self.work).unlink()
        self.assertEqual(d.fs.main(['--repo', str(self.root), 'create', self.work, '--from', str(source),
                                   '--github', 'owner/repo', '--issue', '42']), 0)
        result = d.fs.checkpoint(self.root, self.work, destination)
        data = (self.root / result['path']).read_bytes()
        body = d.fs.checkpoint_github_body(data)
        comments, writes = [], []
        original = subprocess.run
        def run(args, **kwargs):
            if args[0] != 'gh':
                return original(args, **kwargs)
            if args[1] == 'api':
                return subprocess.CompletedProcess(args, 0, '\n'.join(json.dumps(c) for c in comments), '')
            content = Path(args[args.index('--body-file') + 1]).read_text()
            writes.append(content)
            comments.append({'body': content, 'html_url': 'https://github.com/owner/repo/issues/42#issuecomment-1'})
            return subprocess.CompletedProcess(args, 1, '', 'response lost')
        with patch.object(d.fs.subprocess, 'run', side_effect=run):
            with self.assertRaisesRegex(ValueError, 'exact checkpoint comment body'):
                d.fs.checkpoint_github_publish(self.root, self.work, '0' * 64)
            receipt = d.fs.checkpoint_github_publish(self.root, self.work, d.fs.digest(body.encode()))
            self.assertEqual(receipt['status'], 'RECORDED')
            self.assertEqual(d.fs.checkpoint_github_publish(self.root, self.work, d.fs.digest(body.encode())), receipt)
            self.assertEqual(writes, [body])
            clone = Path(self.fixture.temp.name) / 'issue-checkpoint-clone'
            subprocess.run(['git', 'clone', '-q', str(self.root), str(clone)], check=True)
            self.assertEqual(d.fs.main(['--repo', str(clone), 'checkpoint-github-restore',
                                       '--repository', 'owner/repo', '--issue', '42', '--sha256', d.fs.digest(data)]), 0)
            self.assertEqual((clone / self.work).read_bytes(), (self.root / self.work).read_bytes())
            self.assertEqual((clone / '.p2p/work/tiny/checkpoint.json').read_bytes(), data)
            comments.append(dict(comments[0]))
            with self.assertRaisesRegex(ValueError, 'ambiguous GitHub checkpoint'):
                d.fs.checkpoint_github_publish(self.root, self.work, d.fs.digest(body.encode()))
            self.assertEqual(writes, [body])
        self.assertFalse((self.root / 'p2p-state/tiny.json').exists())

    def test_uncommitted_candidate_cannot_be_declared_portable(self):
        (self.root / 'greet.py').write_text('print("hello")\n')
        candidate = d.fs.capture(self.root, self.work, self.fixture.base)
        self.assertNotIn('commit', candidate)
        d.fs.checkpoint(self.root, self.work)
        with self.assertRaisesRegex(ValueError, 'no recoverable Git commit'):
            d.fs.checkpoint_status(self.root, self.work)
        self.assertTrue((self.root / 'greet.py').exists())

    def test_previous_agreement_bytes_are_referenced_from_git_instead_of_duplicated(self):
        original = (self.root / self.work).read_bytes()
        d.fs.checkpoint(self.root, self.work)
        d.fs.git(self.root, 'add', 'p2p-state')
        d.fs.git(self.root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                 'commit', '-qm', 'Preserve approved agreement')
        checkpoint_commit = d.fs.full_commit(self.root, 'HEAD')
        receipt = b'Approval: requester approved the exact previous agreement\n'
        d.fs.save(self.root, self.work, 'planning-handoff.md', receipt)
        data = (self.root / 'p2p-state/tiny.json').read_bytes()
        value, restored = d.fs.read_checkpoint(self.root, data)
        row = next(row for row in value['files'] if row['path'] == self.work)
        self.assertEqual(row, {'scope': 'project', 'path': self.work, 'sha256': d.fs.digest(original),
                               'git_commit': checkpoint_commit, 'checkpoint_path': 'p2p-state/tiny.json'})
        self.assertNotIn(d.fs.digest(original), value['texts'])
        self.assertIn(('project', self.work, original), restored)

    @staticmethod
    def stop_before_proof(original):
        def stage(delivery, name, *args, **kwargs):
            if name == 'proof':
                raise ValueError('fixture transfer boundary')
            return original(delivery, name, *args, **kwargs)
        return stage


if __name__ == '__main__':
    unittest.main()
