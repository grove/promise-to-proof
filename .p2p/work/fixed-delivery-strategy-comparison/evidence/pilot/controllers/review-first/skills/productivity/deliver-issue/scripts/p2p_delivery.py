#!/usr/bin/env python3
"""Deliver one local agreement through fresh, sandboxed Codex CLI stages."""
import argparse
import base64
import datetime
import fcntl
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time
import uuid

import p2p_filesystem as fs

CHECKER = Path(__file__).resolve().parents[4] / 'checks/verify_acceptance_bundle.py'
spec = importlib.util.spec_from_file_location('acceptance_bundle', CHECKER)
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)
STAGES = {'implementation': 'implement-contract', 'review': 'review-implementation',
          'proof': 'prove', 'repair': 'repair-gaps'}
POLICY = 'macos-codex-local-v1'


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def encoded(value):
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False).encode() + b'\n'


def retained(root, work, name, data):
    path = fs.save(root, work, name, data)
    if fs.safe(root, path).read_bytes() != data:
        raise ValueError('storage readback failed: ' + name)
    return path


def materialize(root, manifest):
    root.mkdir(parents=True, exist_ok=True)
    for entry in manifest:
        target = fs.safe(root, entry['path'])
        target.parent.mkdir(parents=True, exist_ok=True)
        if entry['type'] == 'symlink':
            target.symlink_to(entry['target'])
        else:
            target.write_bytes(base64.b64decode(entry['content_base64'], validate=True))
            target.chmod(int(entry['mode'], 8) & 0o777)


def contract(root, work):
    item, _ = fs.paths(root, work)
    text = item.read_text()
    revision = re.findall(r'^Contract revision: (v[1-9][0-9]*)$', text, re.M)
    heading = re.findall(r'^# Acceptance contract: (.+)$', text, re.M)
    if len(revision) != 1 or len(heading) != 1:
        raise ValueError('established contract heading/revision is missing or ambiguous')
    result = dict(source=heading[0], revision=revision[0], content=text, sha256=fs.digest(item.read_bytes()))
    issues = []
    _, _, _, requirements = bundle._validate_contract(result, issues)
    if issues:
        raise ValueError('agreement: ' + json.dumps(issues))
    return result, requirements


def identity(candidate):
    return {key: value for key, value in candidate.items() if key != 'manifest'}


def candidate_key(candidate):
    return candidate.get('key') or 'git:' + candidate['commit']


def skills():
    result = {}
    for stage, name in STAGES.items():
        options = [Path.home() / '.agents/skills' / name / 'SKILL.md',
                   Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'skills' / name / 'SKILL.md']
        found = next((path.resolve() for path in options if path.is_file()), None)
        if found is None:
            raise ValueError('installed skill unavailable: ' + name)
        result[stage] = {'path': str(found), 'sha256': fs.digest(found.read_bytes())}
    return result


def host_config(scratch):
    # Read only these preference keys. Credentials stay in their existing store.
    import tomllib
    home = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    source = home / 'config.toml'
    preferences = tomllib.loads(source.read_text()) if source.exists() else {}
    if preferences.get('model_provider', 'openai') != 'openai':
        raise ValueError('unsupported host: only the configured OpenAI provider is supported')
    config = {'approval_policy': 'never', 'web_search': 'disabled', 'mcp_servers': {},
              'apps._default.enabled': False, 'sandbox_workspace_write.network_access': False,
              'sandbox_workspace_write.exclude_slash_tmp': True,
              'sandbox_workspace_write.exclude_tmpdir_env_var': True,
              'shell_environment_policy.inherit': 'none',
              'shell_environment_policy.set': {'PATH': os.defpath + ':/opt/homebrew/bin',
                                               'HOME': str(Path.home()), 'TMPDIR': str(scratch / '.p2p/tmp'),
                                               'PYTHONDONTWRITEBYTECODE': '1'}}
    for key in ('model', 'model_reasoning_effort'):
        if key in preferences:
            config[key] = preferences[key]
    for name in ('apps', 'plugins', 'remote_plugin', 'hooks', 'multi_agent', 'goals',
                 'computer_use', 'browser_use', 'browser_use_external', 'in_app_browser',
                 'image_generation', 'memories', 'shell_snapshot', 'in_app_local_automation',
                 'workspace_dependencies'):
        config['features.' + name] = False
    return config


def toml_value(value):
    if isinstance(value, dict):
        return '{' + ','.join(json.dumps(k) + '=' + toml_value(v) for k, v in value.items()) + '}'
    return json.dumps(value)


def command(executable, scratch, schema=None):
    args = [executable, 'exec', '--ignore-user-config', '--ignore-rules', '--strict-config',
            '--sandbox', 'workspace-write', '--skip-git-repo-check', '--json', '-C', str(scratch)]
    for key, value in host_config(scratch).items():
        args += ['-c', key + '=' + toml_value(value)]
    if schema:
        args += ['--output-schema', str(schema)]
    return args + ['-']


def launch(args, prompt, event_path, error_path, deadline):
    """Only transport seam. Tests replace it; the CLI has no fake-host switch."""
    started = time.monotonic()
    with event_path.open('xb') as events, error_path.open('xb') as errors:
        process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=events, stderr=errors,
                                   start_new_session=True)
        outcome = 'finished'
        try:
            timeout = None if deadline is None else max(0, deadline - time.time())
            process.communicate(prompt.encode(), timeout=timeout)
        except subprocess.TimeoutExpired:
            outcome = 'interrupted'
            import signal
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
        events.flush()
        errors.flush()
        os.fsync(events.fileno())
        os.fsync(errors.fileno())
    return {'exit_code': process.returncode, 'outcome': outcome, 'finished': now(),
            'elapsed_seconds': max(0, time.monotonic() - started)}


def host_events(path):
    records = [json.loads(line) for line in path.read_text().splitlines() if line]
    sessions = [event['thread_id'] for event in records if event.get('type') == 'thread.started']
    completed = [event for event in records if event.get('type') == 'turn.completed']
    if len(sessions) != 1 or len(completed) != 1:
        raise ValueError('missing unambiguous host session/completion receipt: ' + str(path))
    messages = [event['item']['text'] for event in records if event.get('type') == 'item.completed'
                and event.get('item', {}).get('type') == 'agent_message']
    executions = [event['item'] for event in records if event.get('type') == 'item.completed'
                  and event.get('item', {}).get('type') == 'command_execution']
    return {'session_id': sessions[0], 'usage': completed[0].get('usage', 'unknown'),
            'message': messages[-1] if messages else '', 'executions': executions}


def report_schema():
    string = {'type': 'string'}
    def obj(properties):
        return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}
    evidence = obj({'assertion': string, 'observation': string, 'artifact': string})
    row = obj({'id': string, 'verdict': string, 'observation': string,
               'evidence': {'type': 'array', 'items': evidence}})
    return obj({'status': string, 'input_identity_json': string, 'details': string,
                'requirements': {'type': 'array', 'items': row},
                'gaps': {'type': 'array', 'items': string}})


class Delivery:
    def __init__(self, root, work, state):
        self.root, self.work, self.state = root, work, state
        self.read_only = False
        self.item, self.directory = fs.paths(root, work)
        self.runtime = self.directory / 'runtime'
        self.workspace = self.runtime / 'workspace'

    def save(self):
        retained(self.root, self.work, 'delivery.json', encoded(self.state))

    def source_stable(self):
        admission = json.loads((self.directory / 'admission.json').read_text())
        for key, value in admission.items():
            if self.state.get(key) != value:
                raise ValueError('persisted admission changed: ' + key)
        current = fs.snapshot(self.root)
        if current != self.state['source_manifest']:
            old = {x['path']: x for x in self.state['source_manifest']}
            new = {x['path']: x for x in current}
            changed = sorted(p for p in old.keys() | new.keys() if old.get(p) != new.get(p))
            raise ValueError('source checkout changed since admission: ' + ', '.join(changed))
        if (self.workspace / '.git').read_text() != 'gitdir: ' + str(self.runtime / 'repository.git') + '\n':
            raise ValueError('isolated Git metadata pointer changed')
        if fs.full_commit(self.root, 'HEAD') != self.state['source_head']:
            raise ValueError('source HEAD changed since admission')
        if fs.digest(fs.git(self.root, 'ls-files', '--stage', '-z')) != self.state['source_index_sha256']:
            raise ValueError('source index changed since admission')
        if json.loads((self.directory / 'base-manifest.json').read_text()) != fs.snapshot(self.workspace, self.state['comparison_base']):
            raise ValueError('retained comparison-base content changed')
        if fs.full_commit(self.root, self.state['comparison_base']) != self.state['comparison_base']:
            raise ValueError('comparison base unavailable')
        if fs.bindings(self.root, self.work) != self.state['binding_inputs']:
            raise ValueError('binding inputs changed')
        if fs.digest(self.item.read_bytes()) != self.state['contract']['sha256']:
            raise ValueError('work item changed')
        if self.state['authority'] != {'local_stages': True, 'external_effects': False} or self.state['policy'] != POLICY:
            raise ValueError('persisted authority or policy changed')
        if skills() != self.state['skills']:
            raise ValueError('installed stage skills changed; prior invocation inputs are no longer available')

    def capture(self):
        if fs.digest((self.workspace / self.work).read_bytes()) != self.state['contract']['sha256']:
            raise ValueError('implementation changed the approved agreement')
        if fs.bindings(self.workspace, self.work) != self.state['binding_inputs']:
            raise ValueError('implementation changed binding inputs')
        excluded = self.state['excluded_dirty']
        base = {e['path']: e for e in fs.snapshot(self.workspace, self.state['comparison_base'])}
        actual = {e['path']: e for e in fs.snapshot(self.workspace)}
        changed = [p for p in excluded if actual.get(p) != base.get(p)]
        if changed:
            raise ValueError('implementation changed excluded scope paths: ' + ', '.join(changed))
        candidate = fs.capture(self.workspace, self.work, self.state['comparison_base'])
        retained(self.root, self.work, 'candidate.json', encoded(candidate))
        self.state['candidate'] = candidate
        return candidate

    def current(self):
        self.source_stable()
        expected = self.state.get('candidate')
        if expected:
            actual = fs.validate(self.workspace, self.work, self.state['comparison_base'])
            saved = json.loads((self.directory / 'candidate.json').read_text())
            if actual != expected or saved != expected:
                raise ValueError('retained candidate identity changed')
        return expected

    def reserve(self, stage, inputs, scratch):
        self.source_stable()
        limits = self.state['limits']
        if limits['dispatches'] is not None and len(self.state['attempts']) >= limits['dispatches']:
            raise ValueError('dispatch-count limit exhausted before ' + stage)
        if self.state['deadline'] is not None and time.time() >= self.state['deadline']:
            raise ValueError('elapsed-time limit exhausted before ' + stage)
        if stage == 'repair':
            if self.state['repair_used']:
                raise ValueError('one automatic repair already consumed')
            self.state['repair_used'] = True
        attempt = {'id': str(uuid.uuid4()), 'stage': stage, 'inputs': inputs,
                   'status': 'reserved', 'started': now(), 'started_epoch': time.time(),
                   'finished': None, 'elapsed_seconds': 'unknown', 'usage': 'unknown',
                   'cost': 'unknown', 'scratch': str(scratch), 'session_id': None}
        self.state['attempts'].append(attempt)
        self.save()  # Admission and repair consumption precede any subprocess.
        return attempt

    def receipt(self, attempt):
        folder = self.directory / 'attempts' / attempt['id']
        path = folder / 'exit.json'
        if not path.exists():
            raise ValueError('uncertain dispatch ' + attempt['id'] + ': missing controller host completion ' + str(path))
        end = json.loads(path.read_text())
        if end.get('attempt_id') != attempt['id'] or end.get('inputs') != attempt['inputs']:
            raise ValueError('late or conflicting host receipt: ' + attempt['id'])
        if end.get('event_sha256') != fs.digest((folder / 'events.jsonl').read_bytes()):
            raise ValueError('host event content changed: ' + attempt['id'])
        attempt.update({k: end[k] for k in ('exit_code', 'outcome', 'finished', 'elapsed_seconds')})
        try:
            host = host_events(folder / 'events.jsonl')
        except ValueError:
            attempt['status'] = 'failed'
            if not self.read_only:
                self.save()
            raise
        previous = [a.get('session_id') for a in self.state['attempts'] if a['id'] != attempt['id']]
        if host['session_id'] in previous:
            raise ValueError('host reused a stage session: ' + host['session_id'])
        attempt.update(session_id=host['session_id'], usage=host['usage'])
        if end['exit_code'] != 0 or end['outcome'] != 'finished':
            attempt['status'] = 'failed'
            if not self.read_only:
                self.save()
            raise ValueError('host stage failed/interrupted: ' + attempt['id'])
        return host

    def dispatch(self, stage, inputs, prompt, writable=None, schema=None):
        pending = [a for a in self.state['attempts'] if a['status'] in ('reserved', 'failed')]
        if pending:
            attempt = pending[-1]
            if attempt['stage'] != stage or attempt['inputs'] != inputs:
                raise ValueError('reserved stage inputs differ; uncertain dispatch: ' + attempt['id'])
            return attempt, self.receipt(attempt)
        scratch = writable or (self.runtime / 'scratch' / str(uuid.uuid4()))
        scratch.mkdir(parents=True, exist_ok=True)
        (scratch / '.p2p/tmp').mkdir(parents=True, exist_ok=True)
        attempt = self.reserve(stage, inputs, scratch)
        folder = self.directory / 'attempts' / attempt['id']
        folder.mkdir(parents=True)
        if schema:
            retained(self.root, self.work, f'attempts/{attempt["id"]}/schema.json', encoded(schema))
        args = command(self.state['host']['executable'], scratch, folder / 'schema.json' if schema else None)
        retained(self.root, self.work, f'attempts/{attempt["id"]}/launch.json', encoded({
            'attempt_id': attempt['id'], 'stage': stage, 'inputs': inputs, 'command': args, 'prompt': prompt,
            'configuration': host_config(scratch), 'model_provenance': 'inherited configured preference'}))
        try:
            result = launch(args, prompt, folder / 'events.jsonl', folder / 'stderr.txt', self.state['deadline'])
            result.update(attempt_id=attempt['id'], inputs=inputs,
                          event_sha256=fs.digest((folder / 'events.jsonl').read_bytes()))
            retained(self.root, self.work, f'attempts/{attempt["id"]}/exit.json', encoded(result))
        except BaseException:
            # No retry: a saved reservation with no exit receipt is intentionally uncertain.
            raise
        return attempt, self.receipt(attempt)

    def preflight(self):
        for index in range(2):
            stage = 'preflight-' + str(index + 1)
            done = next((a for a in self.state['attempts'] if a['stage'] == stage and a['status'] == 'complete'), None)
            if done:
                self.receipt(done)
                continue
            probe = self.runtime / ('probe-' + str(index) + '.py')
            git_dir = Path(fs.git(self.root, 'rev-parse', '--absolute-git-dir').decode().strip())
            protected = [git_dir / 'HEAD', git_dir / 'index', self.item, self.directory / 'admission.json', self.directory / 'base-manifest.json', self.runtime / 'repository.git/HEAD',
                         self.workspace / self.work]
            protected += [self.workspace / item['path'] for item in self.state['binding_inputs']]
            sentinel = self.runtime / 'candidate-sentinel'
            sentinel.write_text('protected\n')
            protected.append(sentinel)
            before = {str(p): fs.digest(p.read_bytes()) for p in protected}
            script = '''import json, os, pathlib, socket, subprocess, sys
paths = PROTECTED
results = {}
for index, name in enumerate(paths):
    link = pathlib.Path('input-link-' + str(index))
    link.symlink_to(name)
    for mode, target in [('absolute', name), ('symlink', str(link))]:
        try:
            with open(target, 'ab') as stream: stream.write(b'UNAUTHORIZED')
        except PermissionError: results[name + ':' + mode] = 'denied'
        else: results[name + ':' + mode] = 'ALLOWED'
    child = subprocess.run([sys.executable, '-c', 'import sys;open(sys.argv[1], "ab").write(b"UNAUTHORIZED")', name], capture_output=True)
    results[name + ':subprocess'] = 'denied' if child.returncode != 0 and b'PermissionError' in child.stderr else 'ALLOWED'
pathlib.Path('scratch-write').write_text('ok')
results['scratch'] = pathlib.Path('scratch-write').read_text()
try:
    connection = socket.socket()
    connection.settimeout(3)
    connection.connect(('1.1.1.1', 443))
except PermissionError: results['network'] = 'denied'
except Exception as error: results['network'] = type(error).__name__
else: results['network'] = 'ALLOWED'
print('P2P_BOUNDARY=' + json.dumps(results, sort_keys=True))
assert all(v == 'denied' for k,v in results.items() if k != 'scratch')
assert results['scratch'] == 'ok'
'''.replace('PROTECTED', repr([str(p) for p in protected]))
            probe.write_text(script)
            inputs = {'contract_sha256': self.state['contract']['sha256'], 'probe_sha256': fs.digest(probe.read_bytes())}
            prompt = ('Authorized local host preflight. Run exactly `python3 ' + str(probe) +
                      '` from your scratch workspace. It attempts denied writes to protected test inputs and a '
                      'network connection expected to fail, and writes allowed scratch. Do not escalate or '
                      'change inputs. Print actual available ALL_TOOLS names if that runtime is exposed. '
                      'Return the exact probe output and observed permissions. No other effects are authorized.')
            attempt, host = self.dispatch(stage, inputs, prompt)
            expected_keys = {str(p) + ':' + mode for p in protected for mode in ('absolute', 'symlink', 'subprocess')} | {'network', 'scratch'}
            observations = []
            for event in host['executions']:
                for line in event.get('aggregated_output', '').splitlines():
                    if line.startswith('P2P_BOUNDARY=') and event.get('exit_code') == 0:
                        observations.append(json.loads(line.split('=', 1)[1]))
            if not any(set(o) == expected_keys and all(v == ('ok' if k == 'scratch' else 'denied') for k,v in o.items()) for o in observations):
                raise ValueError('host preflight did not establish all permission boundaries: ' + attempt['id'])
            if before != {str(p): fs.digest(p.read_bytes()) for p in protected}:
                raise ValueError('host preflight changed protected inputs')
            attempt['status'] = 'complete'
            self.save()
        self.state['preflight_complete'] = True
        self.save()

    def stage(self, name):
        self.current()
        inputs = identity(self.state['candidate'])
        prior = self.state.get('reports', {})
        skill_stage = self.state.get('repair_skill', 'repair') if name == 'repair' else name
        prompt = (f'Invoke the installed {STAGES[skill_stage]} skill at {self.state["skills"][skill_stage]["path"]}. '
                  f'Read it and its references. Work item {self.work}, workspace {self.workspace}. '
                  f'Comparison base {self.state["comparison_base"]}. Whole contract, full scope. '
                  'The enclosing controller owns durable reports; return your full report in the required JSON '
                  'schema and it will save and reread it. Never mutate the source checkout, controller records, '
                  'agreement or binding inputs, or source/delivered Git metadata. Local stages and safe scratch '
                  'checks only; no external effects. No commits of delivery work, pushes, publication or cleanup. '
                  'Use fresh independent observations, do not trust previous judgments. '
                  f'Exact input_identity_json must encode this object: {json.dumps(inputs)}. '
                  f'Every requirement must occur exactly once: {self.state["requirements"]}. '
                  'Each row needs a substantive observation; proof rows need actual command/output evidence '
                  'in artifact, an assertion, and observation. Use verdict proven for established proof rows, '
                  'reviewed for review rows without findings; otherwise name the gap. Status uses normal skill '
                  'vocabulary. details contains the full human report. Never fabricate results. '
                  f'Previous reports for repair only: {json.dumps(prior) if name == "repair" else "none"}. ')
        if name in ('review', 'proof'):
            prompt += ('Candidate and Git metadata are protected outside writable scratch. Run checks against '
                       'the fixed workspace; place outputs and PYTHONPYCACHEPREFIX/TMPDIR in scratch. '
                       'Do not copy and edit product code to make a check pass. Inspect the full candidate. ')
        else:
            prompt += ('Implement the smallest complete change in the workspace. .p2p/tmp/ is disposable scratch; '
                       'do not include it in product content. Preserve agreement and binding inputs. ')
        attempt, host = self.dispatch(name, inputs, prompt,
                                      self.workspace if name in ('implementation', 'repair') else None,
                                      report_schema())
        self.source_stable()
        if name in ('review', 'proof'):
            self.current()
        report = json.loads(host['message'])
        if json.loads(report['input_identity_json']) != inputs:
            raise ValueError('stage returned stale or mistyped input identity: ' + attempt['id'])
        rows = report['requirements']
        if sorted(row['id'] for row in rows) != sorted(self.state['requirements']):
            raise ValueError('stage omitted/duplicated full requirement coverage: ' + attempt['id'])
        if not report['details'].strip() or any(not row['observation'].strip() for row in rows):
            raise ValueError('stage returned incomplete report observations: ' + attempt['id'])
        if name == 'proof' and report['status'] == 'PROVEN':
            if not host['executions'] or any(row['verdict'] != 'proven' or not row['evidence'] for row in rows):
                raise ValueError('proof lacks full independently exercised evidence')
            for row in rows:
                for evidence in row['evidence']:
                    if any(not evidence[k].strip() for k in ('assertion', 'observation', 'artifact')):
                        raise ValueError('proof evidence is incomplete: ' + row['id'])
        path = f'attempts/{attempt["id"]}/report.json'
        stored = self.directory / path
        if stored.exists() and stored.read_bytes() != encoded(report):
            raise ValueError('conflicting duplicate stage result: ' + attempt['id'])
        retained(self.root, self.work, path, encoded(report))
        retained(self.root, self.work, f'attempts/{attempt["id"]}/report.md', report['details'].encode())
        retained(self.root, self.work, name + '.md', report['details'].encode())
        attempt.update(status='complete', report=path, report_sha256=fs.digest(encoded(report)))
        self.state.setdefault('reports', {})[name] = {'path': path, 'sha256': attempt['report_sha256'],
                                                     'attempt_id': attempt['id'], 'inputs': inputs}
        self.save()
        return report

    def read_report(self, name):
        record = self.state['reports'][name]
        data = (self.directory / record['path']).read_bytes()
        if fs.digest(data) != record['sha256']:
            raise ValueError('report/evidence content changed or lost: ' + name)
        attempt = next(a for a in self.state['attempts'] if a['id'] == record['attempt_id'])
        host = self.receipt(attempt)
        if encoded(json.loads(host['message'])) != data:
            raise ValueError('report differs from host return: ' + name)
        report = json.loads(data)
        if (self.directory / (name + '.md')).read_bytes() != report['details'].encode():
            raise ValueError('canonical report content changed or lost: ' + name)
        return report

    def complete(self):
        candidate = self.current()
        review, proof = self.read_report('review'), self.read_report('proof')
        for name, report in (('review', review), ('proof', proof)):
            if json.loads(report['input_identity_json']) != identity(candidate):
                raise ValueError('stale ' + name + ' candidate/agreement/base identity')
            if sorted(row['id'] for row in report['requirements']) != sorted(self.state['requirements']):
                raise ValueError('incomplete ' + name + ' requirement coverage')
        if review['status'] != 'REVIEWED' or proof['status'] != 'PROVEN' or review['gaps'] or proof['gaps']:
            raise ValueError('full REVIEWED and PROVEN results are not available')
        if any(row['verdict'] != 'reviewed' for row in review['requirements']):
            raise ValueError('review contains unresolved requirement findings')
        manifest = candidate.get('manifest') or fs.snapshot(self.workspace, candidate['commit'])
        key = 'snapshot:sha256:' + fs.digest(fs.canonical(manifest))
        contract_identity = {k: self.state['contract'][k] for k in ('source', 'revision', 'sha256')}
        text = lambda content: {'content': content, 'sha256': fs.digest(content.encode())}
        normalized_review = {'contract': contract_identity, 'candidate_key': key,
                             'comparison_base': 'git:' + candidate['comparison_base'],
                             'coverage': [r['id'] for r in review['requirements']], 'status': 'REVIEWED',
                             'stability': {'contract': 'unchanged', 'candidate': 'unchanged'},
                             'details': text(review['details'])}
        evidence, verdicts = [], []
        for row in proof['requirements']:
            ids = []
            for item in row['evidence']:
                eid = 'E' + str(len(evidence) + 1)
                ids.append(eid)
                evidence.append({'id': eid, 'result': 'passed', 'assertion': item['assertion'],
                                 'observation': item['observation'], 'artifact': text(item['artifact'])})
            verdicts.append({'id': row['id'], 'verdict': row['verdict'], 'evidence': ids})
        normalized_proof = {'contract': contract_identity, 'candidate_key': key, 'status': 'PROVEN',
                            'stability': {'contract': 'unchanged', 'candidate': 'unchanged'},
                            'verification_context': json.dumps(self.state['host']), 'verdicts': verdicts,
                            'evidence': evidence, 'details': text(proof['details'])}
        value = {'schema': bundle.SCHEMA, 'claim': 'REVIEWED_AND_PROVEN', 'contract': self.state['contract'],
                 'candidate': {'key': key, 'manifest': manifest, 'comparison_base': 'git:' + candidate['comparison_base']},
                 'review': normalized_review, 'proof': normalized_proof}
        issues = bundle.verify_bundle(value)
        if issues:
            raise ValueError('acceptance bundle rejected: ' + json.dumps(issues))
        retained(self.root, self.work, 'acceptance-bundle.json', encoded(value))
        self.current()
        self.state.update(status='REVIEWED_AND_PROVEN', blocker=None)
        self.save()

    def run(self):
        self.current()
        self.preflight()
        if not self.state.get('implementation_complete'):
            result = self.stage('implementation')
            self.capture()
            if result['status'] != 'IMPLEMENTED':
                raise ValueError('implementation incomplete: ' + '; '.join(result['gaps']))
            self.state['implementation_complete'] = True
            self.save()
        while True:
            for name in ('review', 'proof'):
                if name not in self.state.get('reports', {}):
                    self.stage(name)
            review, proof = self.read_report('review'), self.read_report('proof')
            if review['status'] == 'REVIEWED' and proof['status'] == 'PROVEN' and not review['gaps'] and not proof['gaps']:
                self.complete()
                return
            if self.state['repair_used']:
                raise ValueError('one automatic repair exhausted; review/proof gaps remain')
            # Review findings belong to implement-contract; proof gaps to repair-gaps.
            self.state['repair_skill'] = 'repair' if proof['status'] != 'PROVEN' else 'implementation'
            self.save()
            result = self.stage('repair')
            self.capture()
            self.state['reports'] = {k:v for k,v in self.state['reports'].items() if k not in ('review', 'proof')}
            self.save()
            if result['status'] not in ('REPAIRED', 'IMPLEMENTED'):
                raise ValueError('automatic repair incomplete: ' + '; '.join(result['gaps']))


def create(root, args):
    agreement, requirements = contract(root, args.work)
    if not args.authorize_local:
        raise ValueError('local agent-stage authority missing; run requires --authorize-local')
    if args.hard_cost_cap is not None:
        raise ValueError('unsupported capability: no enforceable hard monetary cap')
    if platform.system() != 'Darwin':
        raise ValueError('unsupported host: Codex CLI on macOS required')
    executable = shutil.which('codex')
    if not executable:
        raise ValueError('unsupported host: codex executable missing')
    if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', args.comparison_base):
        raise ValueError('comparison base must be an explicit full commit SHA')
    base = fs.full_commit(root, args.comparison_base)
    installed = skills()
    fs.check_index(root)
    current = fs.snapshot(root)
    head = fs.full_commit(root, 'HEAD')
    committed = fs.snapshot(root, head)
    old, new = ({e['path']: e for e in entries} for entries in (committed, current))
    dirty = {p for p in old.keys() | new.keys() if old.get(p) != new.get(p)}
    inputs = fs.bindings(root, args.work)
    agreements = {args.work} | {entry['path'] for entry in inputs}
    excluded = set(args.exclude_dirty)
    for path in excluded:
        fs.safe(root, path, leaf_symlink=True)
    if excluded & agreements:
        raise ValueError('cannot exclude agreement or binding input')
    contested = dirty - agreements - excluded
    if contested:
        raise ValueError('contested dirty paths require explicit --exclude-dirty: ' + ', '.join(sorted(contested)))
    if excluded - dirty:
        raise ValueError('--exclude-dirty names paths that are not dirty: ' + ', '.join(sorted(excluded - dirty)))
    manifest = {e['path']: e for e in committed}
    comparison = {e['path']: e for e in fs.snapshot(root, base)}
    for path in excluded:
        if path in comparison:
            manifest[path] = comparison[path]
        else:
            manifest.pop(path, None)
    for path in agreements:
        if path not in new:
            raise ValueError('agreement input missing from candidate: ' + path)
        manifest[path] = new[path]
    _, directory = fs.paths(root, args.work)
    runtime = directory / 'runtime'
    if runtime.exists():
        raise ValueError('runtime exists without a delivery record; preserve it and reconcile admission')
    runtime.mkdir(parents=True)
    repository = runtime / 'repository.git'
    result = subprocess.run(['git', 'clone', '--bare', '--no-hardlinks', '--', str(root), str(repository)], capture_output=True)
    if result.returncode:
        raise ValueError('isolated Git metadata copy failed: ' + result.stderr.decode())
    fs.git(root, 'bundle', 'create', str(runtime / 'base.bundle'), 'HEAD', base)
    retained(root, args.work, 'base-manifest.json', encoded(fs.snapshot(root, base)))
    workspace = runtime / 'workspace'
    materialize(workspace, sorted(manifest.values(), key=lambda e:e['path']))
    (workspace / '.git').write_text('gitdir: ' + str(repository) + '\n')
    fs.git(workspace, 'config', '--local', 'core.bare', 'false')
    fs.git(workspace, 'read-tree', head)
    # Git metadata is outside every worker writable root; never shared with source.
    state = {'schema': 'promise-to-proof/delivery/v1', 'policy': POLICY, 'invocation_id': str(uuid.uuid4()),
             'status': 'RUNNING', 'blocker': None, 'work_item': args.work, 'comparison_base': base,
             'contract': agreement, 'requirements': requirements, 'binding_inputs': inputs,
             'source_manifest': current, 'source_head': head,
             'source_index_sha256': fs.digest(fs.git(root, 'ls-files', '--stage', '-z')),
             'excluded_dirty': sorted(excluded), 'skills': installed,
             'authority': {'local_stages': True, 'external_effects': False},
             'limits': {'dispatches': args.max_dispatches, 'elapsed_seconds': args.max_seconds},
             'deadline': None if args.max_seconds is None else time.time() + args.max_seconds,
             'created': now(), 'repair_used': False, 'attempts': [], 'reports': {},
             'host': {'name': 'Codex CLI on macOS', 'executable': executable,
                      'version': subprocess.check_output([executable, '--version'], text=True).strip(),
                      'hard_monetary_cap': 'unsupported', 'cost': 'unknown',
                      'enforced': ['scratch-only verification writes', 'network denied', 'approval escalation disabled',
                                   'isolated configuration', 'dispatch admission', 'one repair reservation'],
                      'elapsed_limit': 'admission and process termination; provider billing may continue',
                      'trust': 'controller and OS trusted; no arbitrary same-user tamper resistance'}}
    delivery = Delivery(root, args.work, state)
    retained(root, args.work, 'admission.json', encoded({k: state[k] for k in ('policy', 'invocation_id', 'work_item', 'comparison_base', 'contract', 'binding_inputs', 'source_manifest', 'source_head', 'source_index_sha256', 'excluded_dirty', 'skills', 'authority', 'limits', 'deadline', 'host')}))
    delivery.save()
    delivery.capture()
    delivery.save()
    return delivery


def result(delivery):
    state = delivery.state
    return {key: state[key] for key in ('status', 'blocker', 'invocation_id', 'work_item', 'comparison_base',
                                      'limits', 'repair_used', 'host')} | {
        'candidate': identity(state['candidate']) if state.get('candidate') else None,
        'reports': state.get('reports', {}), 'attempts': state['attempts'],
        'records': str(delivery.directory),
        'resume': f'python3 {Path(__file__).resolve()} --repo {delivery.root} resume {delivery.work}'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default='.')
    commands = parser.add_subparsers(dest='action', required=True)
    for name in ('run', 'resume', 'status'):
        child = commands.add_parser(name)
        child.add_argument('work')
        if name == 'run':
            child.add_argument('--comparison-base', required=True)
            child.add_argument('--authorize-local', action='store_true')
            child.add_argument('--exclude-dirty', action='append', default=[])
            child.add_argument('--max-dispatches', type=int)
            child.add_argument('--max-seconds', type=float)
            child.add_argument('--hard-cost-cap', type=float)
    args = parser.parse_args(argv)
    delivery = None
    lock = None
    try:
        root = Path(fs.git(Path(args.repo), 'rev-parse', '--show-toplevel').decode().strip()).resolve()
        item, directory = fs.paths(root, args.work)
        state_path = directory / 'delivery.json'
        if args.action == 'status':
            if not state_path.exists():
                raise ValueError('no delivery invocation exists')
            delivery = Delivery(root, args.work, json.loads(state_path.read_text()))
            delivery.read_only = True
            # Read-only status rechecks retained claims without creating a lock or records.
            delivery.current()
            for name in delivery.state.get('reports', {}):
                delivery.read_report(name)
            print(json.dumps(result(delivery), indent=2))
            return 0 if delivery.state['status'] == 'REVIEWED_AND_PROVEN' else 1
        directory.mkdir(parents=True, exist_ok=True)
        lock = (directory / 'delivery.lock').open('a')
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('another controller holds the work-item lock')
        if state_path.exists():
            delivery = Delivery(root, args.work, json.loads(state_path.read_text()))
            if args.action == 'run':
                requested = {'dispatches': args.max_dispatches, 'elapsed_seconds': args.max_seconds}
                if (not args.authorize_local or args.hard_cost_cap is not None or
                    requested != delivery.state['limits'] or args.comparison_base != delivery.state['comparison_base'] or
                    sorted(args.exclude_dirty) != delivery.state['excluded_dirty']):
                    raise ValueError('run cannot change persisted authority, scope, base or limits; use resume')
        elif args.action == 'resume':
            raise ValueError('missing delivery invocation; no effects can be reconciled')
        else:
            if args.max_dispatches is not None and args.max_dispatches < 0 or args.max_seconds is not None and (not math.isfinite(args.max_seconds) or args.max_seconds < 0):
                raise ValueError('resource limits must be finite and nonnegative')
            delivery = create(root, args)
        if delivery.state['status'] == 'REVIEWED_AND_PROVEN':
            delivery.complete()
        else:
            delivery.run()
        print(json.dumps(result(delivery), indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, UnicodeError, subprocess.SubprocessError) as error:
        message = str(error)
        if delivery:
            delivery.state.update(status='BLOCKED', blocker=message)
            if args.action != 'status':
                try:
                    delivery.save()
                except (ValueError, OSError) as storage:
                    message += '; unable to persist blocker: ' + str(storage)
            output = result(delivery)
            output.update(status='BLOCKED', blocker=message)
        else:
            output = {'status': 'BLOCKED', 'blocker': message, 'work_item': args.work,
                      'resume': f'python3 {Path(__file__).resolve()} --repo {args.repo} resume {args.work}'}
        print(json.dumps(output, indent=2))
        return 1
    finally:
        if lock is not None:
            lock.close()


if __name__ == '__main__':
    sys.exit(main())
