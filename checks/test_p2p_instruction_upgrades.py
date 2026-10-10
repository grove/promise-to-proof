#!/usr/bin/env python3
"""Pinned instruction upgrades through deterministic fixtures, never live models."""
import base64
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zlib

import test_p2p_checkpoints as checkpoints
import test_p2p_delivery as fixture

import p2p_instructions as instructions

d = fixture.d
WORK = '.p2p/work/tiny/contract.md'


def installed_skills(root):
    result = {}
    for stage, name in d.STAGES.items():
        path = root / name / 'SKILL.md'
        result[stage] = {'path': str(path), 'sha256': d.fs.digest(path.read_bytes())}
    return result


class InstructionSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.installed = self.root / 'installed'
        shutil.copytree(fixture.FIXTURE_SKILLS, self.installed)

    def capture(self):
        return instructions.capture(installed_skills(self.installed), d.STAGES)

    def test_identity_includes_transitive_symlink_content_and_survives_relocation(self):
        protocol = self.installed / 'protocol.md'
        protocol.write_text('<!-- p2p-instruction-dependencies: rules.md -->\n' +
                            protocol.read_text() + '\nSee the explanatory [guide](uninstalled-guide.md).\n')
        rules = self.installed / 'rules.md'
        target = self.installed / 'actual-rules.md'
        rules.rename(target)
        rules.symlink_to(target.name)
        before = self.capture()
        relocated = self.root / 'another-installation'
        shutil.copytree(self.installed, relocated, symlinks=True)
        moved = instructions.capture(installed_skills(relocated), d.STAGES)
        self.assertEqual(moved['identity'], before['identity'])
        self.assertIn('skills/productivity/rules.md', {row['path'] for row in before['files']})
        self.assertFalse(any(row['path'].endswith('uninstalled-guide.md') for row in before['files']))

        stage_files = installed_skills(self.installed)
        target.write_text(target.read_text() + '\nRequire the exact exit status.\n')
        changed_rule = self.capture()
        self.assertNotEqual(changed_rule['identity'], before['identity'])
        self.assertEqual(installed_skills(self.installed), stage_files)
        skill = self.installed / 'prove/SKILL.md'
        skill.write_text(skill.read_text() + '\nInspect all promised CLI output.\n')
        self.assertNotEqual(self.capture()['identity'], changed_rule['identity'])

    def test_preserved_instructions_outlive_installation_and_reject_changed_files(self):
        bundle = self.capture()
        runtime = self.root / 'runtime'
        mapping = instructions.preserve(runtime, bundle)
        shutil.rmtree(self.installed)
        self.assertEqual(instructions.load(runtime, bundle['identity']), bundle)
        self.assertEqual(instructions.validate(runtime, bundle['identity']), mapping)
        self.assertEqual(instructions.preserve(runtime, bundle), mapping)
        pinned = Path(mapping['review']['path'])
        original = pinned.read_bytes()
        pinned.write_bytes(original + b'\nChanged after admission.\n')
        with self.assertRaisesRegex(ValueError, 'changed'):
            instructions.validate(runtime, bundle['identity'])
        with self.assertRaisesRegex(ValueError, 'changed'):
            instructions.preserve(runtime, bundle)
        self.assertEqual(pinned.read_bytes(), original + b'\nChanged after admission.\n')

    def test_missing_dependencies_and_incompatible_versions_are_actionable(self):
        original = self.capture()
        rules = self.installed / 'rules.md'
        data = rules.read_bytes()
        rules.unlink()
        with self.assertRaisesRegex(ValueError, 'missing.*instruction dependency.*restore'):
            self.capture()
        rules.write_bytes(data)
        for name in d.STAGES.values():
            path = self.installed / name / 'SKILL.md'
            path.write_text(path.read_text().replace('delivery-v1', 'delivery-v2'))
        changed = self.capture()
        with self.assertRaisesRegex(ValueError, 'incompatible.*resume the preserved version'):
            instructions.compatible(original, changed)
        skill = self.installed / 'prove/SKILL.md'
        skill.write_text(skill.read_text().replace('p2p-instruction-compatibility: delivery-v2\n', ''))
        with self.assertRaisesRegex(ValueError, 'compatibility'):
            self.capture()

    def test_portable_bundle_checks_text_identity_and_unsafe_paths(self):
        bundle = self.capture()
        self.assertEqual(instructions.decode(instructions.encode(bundle), bundle['identity']), bundle)
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            instructions.decode(instructions.encode(bundle), '0' * 64)
        for defect in ('text', 'path'):
            with self.subTest(defect=defect):
                forged = copy.deepcopy(bundle)
                if defect == 'text':
                    sha = next(iter(forged['texts']))
                    forged['texts'][sha] += '\nChanged rule.\n'
                else:
                    forged['files'][0]['path'] = '../outside-snapshot.md'
                forged['identity'] = d.fs.digest(d.fs.canonical({
                    key: value for key, value in forged.items() if key != 'identity'}))
                envelope = {'schema': 'promise-to-proof/instruction-snapshot/v1',
                            'identity': forged['identity'], 'encoding': 'zlib+base64',
                            'content': base64.b64encode(zlib.compress(d.fs.canonical(forged))).decode()}
                with self.assertRaisesRegex(ValueError, 'hash mismatch|unsafe instruction'):
                    instructions.decode(d.fs.canonical(envelope))


class InstructionUpgradeFixture(unittest.TestCase):
    def setUp(self):
        self.case = fixture.DeliveryTests()
        self.case.setUp()
        self.addCleanup(self.case.tearDown)
        self.root = self.case.root
        self.installed = Path(self.case.temp.name) / 'installed-skills'
        shutil.copytree(fixture.FIXTURE_SKILLS, self.installed)

        def installed(name):
            path = self.installed / name / 'SKILL.md'
            return {'path': str(path), 'sha256': d.fs.digest(path.read_bytes())}

        self.skill_patch = patch.object(d, 'installed_skill', side_effect=installed)
        self.skill_patch.start()
        self.addCleanup(self.skill_patch.stop)

    def change_rules(self):
        path = self.installed / 'rules.md'
        path.write_text(path.read_text() + '\nUse exact stdout and exit-status observations.\n')

    def boundary(self, stage='review', *args):
        original = d.Delivery.stage

        def pause(delivery, name, *positional, **options):
            if name == stage:
                raise ValueError('fixture completed instruction-upgrade boundary')
            return original(delivery, name, *positional, **options)

        with patch.object(d.Delivery, 'stage', pause):
            code, result = self.case.cli('run', *args)
        self.assertEqual(code, 1, result)
        self.assertIn('fixture completed instruction-upgrade boundary', result['blocker'])
        return self.case.state()

    def raw_reports(self, state):
        return {attempt['id']: (self.case.runtime() / attempt['report']).read_bytes()
                for attempt in state['attempts'] if attempt.get('report')}

    def assert_work_preserved(self, before, after):
        for field in ('invocation_id', 'contract', 'requirements', 'comparison_base', 'candidate',
                      'source_tree_key', 'source_head', 'source_index_sha256', 'source_product_index_sha256',
                      'binding_inputs', 'routing', 'routing_records', 'local_git_base', 'local_git_generations',
                      'authority', 'autonomy', 'limits', 'deadline', 'started_at', 'started_epoch',
                      'deadline_started_epoch', 'implementation_complete'):
            self.assertEqual(after.get(field), before.get(field), field)
        self.assertEqual(after['attempts'][:len(before['attempts'])], before['attempts'])


class InstructionUpgradeTests(InstructionUpgradeFixture):
    def test_pinned_resume_ignores_changed_installation_without_repeating_completed_work(self):
        before = self.boundary('proof')
        original_installed = installed_skills(self.installed)
        self.change_rules()
        self.assertEqual(installed_skills(self.installed), original_installed)
        current = instructions.capture(installed_skills(self.installed), d.STAGES)
        self.assertNotEqual(current['identity'], before['instruction_identity'])
        calls = list(self.case.fake.calls)
        shutil.rmtree(self.installed)
        code, result = self.case.cli('resume')
        self.assertEqual(code, 0, result)
        after = self.case.state()
        self.assertEqual(after['instruction_identity'], before['instruction_identity'])
        self.assertEqual(after['reports']['review'], before['reports']['review'])
        self.assertEqual(after['candidate'], before['candidate'])
        self.assertEqual(self.case.fake.calls, calls + ['proof'])
        for stage in ('review', 'proof'):
            self.assertIn(before['instruction_identity'],
                          next(prompt for name, prompt in self.case.fake.prompts if name == stage))
        calls = list(self.case.fake.calls)
        self.assertEqual(self.case.cli('resume')[0], 0)
        self.assertEqual(self.case.fake.calls, calls)

    def test_upgrade_preserves_work_refreshes_only_verifiers_and_is_idempotent(self):
        code, result = self.case.cli('run', '--max-dispatches', '20', '--max-seconds', '600',
                                     '--max-stage-seconds', '30', '--max-repairs', '2')
        self.assertEqual(code, 0, result)
        before = self.case.state()
        reports = self.raw_reports(before)
        calls = list(self.case.fake.calls)
        self.change_rules()
        code, result = self.case.cli('upgrade-instructions', '--authorize-upgrade')
        self.assertEqual(code, 0, result)
        upgraded = self.case.state()
        self.assert_work_preserved(before, upgraded)
        self.assertEqual(self.case.fake.calls, calls)
        self.assertNotEqual(upgraded['instruction_identity'], before['instruction_identity'])
        self.assertEqual(len(upgraded['instruction_history']), 1)
        self.assertEqual(set(upgraded['reports']), {'implementation'})
        self.assertEqual(self.raw_reports(upgraded), reports)
        for report in before['reports'].values():
            self.assertEqual(report['inputs']['instruction_identity'], before['instruction_identity'])

        stale = copy.deepcopy(upgraded)
        stale['reports'] = before['reports']
        delivery = d.Delivery(self.root, WORK, stale)
        delivery.read_only = True
        with self.assertRaisesRegex(ValueError, 'stale|instruction'):
            delivery.complete()

        self.assertEqual(self.case.cli('upgrade-instructions', '--authorize-upgrade')[0], 0)
        self.assertEqual(self.case.state()['instruction_history'], upgraded['instruction_history'])
        code, result = self.case.cli('resume')
        self.assertEqual(code, 0, result)
        after = self.case.state()
        self.assertEqual(self.case.fake.calls, calls + ['review', 'proof'])
        self.assert_work_preserved(before, after)
        for stage in ('review', 'proof'):
            self.assertEqual(after['reports'][stage]['inputs']['instruction_identity'], upgraded['instruction_identity'])
            self.assertNotEqual(after['reports'][stage]['attempt_id'], before['reports'][stage]['attempt_id'])
        current_reports = self.raw_reports(after)
        self.assertEqual({attempt: current_reports[attempt] for attempt in reports}, reports)
        calls = list(self.case.fake.calls)
        self.assertEqual(self.case.cli('upgrade-instructions', '--authorize-upgrade')[0], 0)
        self.assertEqual(self.case.cli('resume')[0], 0)
        self.assertEqual(self.case.fake.calls, calls)

    def test_preview_is_read_only_and_missing_mandate_decision_blocks_adoption(self):
        policy = d.autonomy.local('Deliver the agreed CLI')['policy']
        policy['decisions'] = ['implementation']
        mandate = Path(self.case.temp.name) / 'mandate.json'
        mandate.write_text(json.dumps(policy))
        before = self.boundary('review', '--mandate', str(mandate))
        state_path = d.local_directory(self.root, WORK) / 'delivery.json'
        state_bytes = state_path.read_bytes()
        self.change_rules()
        calls = list(self.case.fake.calls)
        code, result = self.case.cli('upgrade-instructions')
        self.assertEqual(code, 0, result)
        self.assertEqual(state_path.read_bytes(), state_bytes)
        self.assertEqual(self.case.fake.calls, calls)
        self.assertIn('--authorize-upgrade', json.dumps(result))
        code, result = self.case.cli('upgrade-instructions', '--authorize-upgrade')
        self.assertEqual(code, 1, result)
        self.assertRegex(result['blocker'], 'mandate|authority|evidence')
        self.assertEqual(self.case.state()['instruction_identity'], before['instruction_identity'])
        self.assertEqual(self.case.fake.calls, calls)

    def test_upgrade_cannot_reset_an_exhausted_dispatch_budget(self):
        code, result = self.case.cli('run', '--max-dispatches', '5')
        self.assertEqual(code, 0, result)
        before = self.case.state()
        calls = list(self.case.fake.calls)
        self.change_rules()
        self.assertEqual(self.case.cli('upgrade-instructions', '--authorize-upgrade')[0], 0)
        code, result = self.case.cli('resume')
        self.assertEqual(code, 1, result)
        self.assertIn('dispatch-count limit', result['blocker'])
        self.assertEqual(self.case.state()['limits'], before['limits'])
        self.assertEqual(len(self.case.state()['attempts']), 5)
        self.assertEqual(self.case.fake.calls, calls)

    def test_uncertain_worker_blocks_upgrade_without_a_duplicate_launch(self):
        self.case.fake.mode = 'uncertain'
        code, result = self.case.cli()
        self.assertEqual(code, 1, result)
        before = self.case.state()
        calls = list(self.case.fake.calls)
        self.change_rules()
        for _ in range(2):
            code, result = self.case.cli('upgrade-instructions', '--authorize-upgrade')
            self.assertEqual(code, 1, result)
            self.assertRegex(result['blocker'], 'uncertain|missing controller host completion')
            after = self.case.state()
            self.assertEqual(after['instruction_identity'], before['instruction_identity'])
            self.assertEqual(after['attempts'], before['attempts'])
            self.assertEqual(self.case.fake.calls, calls)

    def test_known_mutator_completion_is_reconciled_once_before_upgrade(self):
        original = d.Delivery.receipt
        interrupted = False

        def pause(delivery, attempt):
            nonlocal interrupted
            if attempt['stage'] == 'implementation' and not interrupted:
                interrupted = True
                raise OSError('fixture lost controller after worker completion')
            return original(delivery, attempt)

        with patch.object(d.Delivery, 'receipt', pause):
            code, result = self.case.cli()
        self.assertEqual(code, 1, result)
        before = self.case.state()
        attempt = before['attempts'][-1]
        self.assertEqual(attempt['status'], 'reserved')
        self.assertTrue((self.case.runtime() / 'attempts' / attempt['id'] / 'exit.json').is_file())
        calls = list(self.case.fake.calls)
        self.change_rules()
        code, result = self.case.cli('upgrade-instructions', '--authorize-upgrade')
        self.assertEqual(code, 0, result)
        upgraded = self.case.state()
        self.assertEqual(self.case.fake.calls, calls)
        self.assertTrue(upgraded['implementation_complete'])
        self.assertEqual(upgraded['attempts'][-1]['id'], attempt['id'])
        self.assertEqual(upgraded['attempts'][-1]['status'], 'complete')
        self.assertEqual(len(upgraded['local_git_generations']), len(before['local_git_generations']) + 1)
        self.assertEqual((self.case.runtime() / 'workspace/greet.py').read_text(), "print('hello')\n")
        self.assertEqual(self.case.cli('upgrade-instructions', '--authorize-upgrade')[0], 0)
        self.assertEqual(self.case.state()['local_git_generations'], upgraded['local_git_generations'])
        code, result = self.case.cli('resume')
        self.assertEqual(code, 0, result)
        self.assertEqual(self.case.fake.calls, calls + ['review', 'proof'])

    def test_interrupted_transition_replays_each_durable_boundary_without_duplicate_work(self):
        self.boundary('proof')
        class PowerLoss(BaseException):
            pass

        for interrupted_file in ('runtime/instruction-transition.json', 'delivery.json', 'runtime/admission.json'):
            with self.subTest(interrupted_file=interrupted_file):
                before = self.case.state()
                self.change_rules()
                original = d.local_save
                interrupted = False

                def save(root, work, relative, data):
                    nonlocal interrupted
                    result = original(root, work, relative, data)
                    if relative == interrupted_file and not interrupted:
                        value = json.loads(data)
                        changed = value.get('new_admission', value)
                        if changed.get('instruction_identity') != before['instruction_identity']:
                            interrupted = True
                            raise PowerLoss()
                    return result

                calls = list(self.case.fake.calls)
                with patch.object(d, 'local_save', save), self.assertRaises(PowerLoss):
                    self.case.cli('upgrade-instructions', '--authorize-upgrade')
                self.assertTrue(interrupted)
                self.assertEqual(self.case.fake.calls, calls)
                code, result = self.case.cli('resume')
                self.assertEqual(code, 0, result)
                after = self.case.state()
                self.assert_work_preserved(before, after)
                self.assertEqual(len(after['instruction_history']), len(before['instruction_history']) + 1)
                self.assertEqual(self.case.fake.calls, calls + ['review', 'proof'])
                history = after['instruction_history']
                calls = list(self.case.fake.calls)
                self.assertEqual(self.case.cli('upgrade-instructions', '--authorize-upgrade')[0], 0)
                self.assertEqual(self.case.cli('resume')[0], 0)
                self.assertEqual(self.case.state()['instruction_history'], history)
                self.assertEqual(self.case.fake.calls, calls)

    def test_missing_old_snapshot_and_incompatible_installation_preserve_current_work(self):
        before = self.boundary()
        calls = list(self.case.fake.calls)
        bundle = self.case.runtime() / 'instructions' / (before['instruction_identity'] + '.json')
        original = bundle.read_bytes()
        bundle.unlink()
        self.change_rules()
        code, result = self.case.cli('upgrade-instructions', '--authorize-upgrade')
        self.assertEqual(code, 1, result)
        self.assertRegex(result['blocker'], 'snapshot.*unavailable.*recover|missing.*instruction')
        self.assertEqual(self.case.state()['instruction_identity'], before['instruction_identity'])
        self.assertEqual(self.case.fake.calls, calls)
        bundle.write_bytes(original)
        for name in d.STAGES.values():
            skill = self.installed / name / 'SKILL.md'
            skill.write_text(skill.read_text().replace('delivery-v1', 'delivery-v2'))
        code, result = self.case.cli('upgrade-instructions', '--authorize-upgrade')
        self.assertEqual(code, 1, result)
        self.assertIn('incompatible', result['blocker'])
        self.assertEqual(self.case.state()['instruction_identity'], before['instruction_identity'])
        self.assertEqual(self.case.fake.calls, calls)
        self.assertEqual(self.case.cli('resume')[0], 0)
        self.assertEqual(self.case.fake.calls, calls + ['review', 'proof'])

    def test_legacy_admission_resumes_matching_skills_and_blocks_unrecoverable_upgrade(self):
        code, result = self.case.cli('run', '--max-dispatches', '0')
        self.assertEqual(code, 1, result)
        state = self.case.state()
        state.pop('instruction_identity')
        state.pop('instruction_history', None)
        state['skills'] = installed_skills(self.installed)
        admission_path = self.case.runtime() / 'admission.json'
        admission = json.loads(admission_path.read_bytes())
        admission.pop('instruction_identity', None)
        admission.pop('instruction_history', None)
        admission['skills'] = state['skills']
        admission_path.write_bytes(d.encoded(admission))
        (d.local_directory(self.root, WORK) / 'delivery.json').write_bytes(d.encoded(state))
        code, result = self.case.cli('resume')
        self.assertEqual(code, 1, result)
        self.assertIn('dispatch-count limit', result['blocker'])
        self.assertEqual(self.case.cli('extend', '--authorize-extension', '--max-dispatches', '5')[0], 0)
        code, result = self.case.cli('resume')
        self.assertEqual(code, 0, result)
        self.assertEqual(self.case.fake.calls, ['preflight', 'preflight', 'implementation', 'review', 'proof'])
        self.assertNotIn('instruction_identity', self.case.state()['reports']['proof']['inputs'])
        calls = list(self.case.fake.calls)
        self.assertEqual(self.case.cli('resume')[0], 0)
        self.assertEqual(self.case.fake.calls, calls)
        self.change_rules()
        code, result = self.case.cli('upgrade-instructions', '--authorize-upgrade')
        self.assertEqual(code, 1, result)
        self.assertRegex(result['blocker'], 'legacy|original|missing.*instruction')
        self.assertNotIn('instruction_identity', self.case.state())
        self.assertEqual(self.case.fake.calls, calls)


class PortableInstructionUpgradeTests(InstructionUpgradeFixture):
    def checkpoint_clone(self):
        checkpoint = json.loads((self.root / 'p2p-state/tiny.json').read_bytes())
        publisher = checkpoints.CheckpointTests()
        publisher.fixture, publisher.root, publisher.work = self.case, self.root, WORK
        _, clone = publisher.publish_fixture(checkpoint)
        return clone, (self.root / 'p2p-state/tiny.json').read_bytes()

    def test_portable_restore_retains_pinned_instructions_and_completed_review(self):
        before = self.boundary('proof')
        clone, data = self.checkpoint_clone()
        calls = list(self.case.fake.calls)
        self.change_rules()
        shutil.rmtree(self.case.runtime())
        shutil.rmtree(self.installed)
        restored = d.fs.restore_checkpoint(clone, data)
        self.assertEqual(restored['status'], 'RESTORED')
        self.assertEqual(self.case.fake.calls, calls)
        code, result = self.case.run_root(clone, WORK, self.case.base, 'resume')
        self.assertEqual(code, 0, result)
        after = json.loads((d.local_directory(clone, WORK) / 'delivery.json').read_bytes())
        self.assertEqual(after['instruction_identity'], before['instruction_identity'])
        self.assertEqual(after['candidate'], before['candidate'])
        self.assertEqual(after['reports']['review'], before['reports']['review'])
        self.assertEqual(self.case.fake.calls, calls + ['preflight', 'preflight', 'proof'])

    def test_portable_upgrade_requires_authority_and_refreshes_verifiers_after_host_checks(self):
        before = self.boundary('proof', '--max-dispatches', '12')
        clone, data = self.checkpoint_clone()
        self.change_rules()
        calls = list(self.case.fake.calls)
        with self.assertRaisesRegex(ValueError, 'authorize-upgrade|authority|authorization'):
            d.fs.restore_checkpoint(clone, data, upgrade_instructions=True)
        self.assertFalse((clone / '.p2p/work/tiny/delivery.json').exists())
        self.assertEqual(self.case.fake.calls, calls)
        restored = d.fs.restore_checkpoint(clone, data, upgrade_instructions=True, authorize_upgrade=True)
        self.assertEqual(restored['status'], 'RESTORED')
        adopted = json.loads((d.local_directory(clone, WORK) / 'delivery.json').read_bytes())
        self.assertEqual(self.case.fake.calls, calls)
        self.assertNotEqual(adopted['instruction_identity'], before['instruction_identity'])
        self.assertEqual(adopted['candidate'], before['candidate'])
        self.assertEqual(adopted['limits'], before['limits'])
        self.assertEqual(len(adopted['instruction_history']), 1)
        self.assertEqual(set(adopted['reports']), {'implementation'})
        code, result = self.case.run_root(clone, WORK, self.case.base, 'resume')
        self.assertEqual(code, 0, result)
        self.assertEqual(self.case.fake.calls, calls + ['preflight', 'preflight', 'review', 'proof'])
        after = json.loads((d.local_directory(clone, WORK) / 'delivery.json').read_bytes())
        for stage in ('review', 'proof'):
            self.assertEqual(after['reports'][stage]['inputs']['instruction_identity'], adopted['instruction_identity'])


if __name__ == '__main__':
    unittest.main()
