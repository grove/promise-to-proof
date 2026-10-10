#!/usr/bin/env python3
"""Deliver one local agreement through fresh, sandboxed Codex CLI stages."""
import argparse
import base64
from contextlib import contextmanager
import datetime
import fcntl
import json
import math
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

import p2p_filesystem as fs
import p2p_autonomy as autonomy
import p2p_applicability as applicability
import p2p_slices as slices
import p2p_instructions as instructions
import p2p_progress as progress_view
from p2p_delivery_measurements import build as delivery_measurement

import verify_acceptance_bundle as bundle
STAGES = {'implementation': 'implement-contract', 'review': 'review-implementation',
          'proof': 'prove', 'repair': 'repair-gaps'}
POLICY = 'macos-codex-local-v1'
HEARTBEAT_SECONDS = 30
RETAINED_ARTIFACTS = {'archive.md': 'Historical recovery map.',
                      'planning-handoff.md': 'Approval and contract provenance.'}
FINAL_RECORDS = {'candidate.json', 'delivery.json', 'review.md', 'proof.md'}
SUPERSEDED_RECORDS = {'candidate.json', 'implementation.md', 'review.md', 'proof.md', 'repair.md'}


class ContinuationRequired(ValueError):
    """The outer workflow can carry out a delegated planning/routing handoff."""


class WorkerRestartRequired(Exception):
    """A terminated idle worker has been retained and can be replaced safely."""


class ReportFormatError(ValueError):
    """A completed response is malformed; it is not an unavailable capability."""


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def encoded(value):
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False).encode() + b'\n'


def require_repo_local_ignored(root, path):
    path = Path(os.path.abspath(path))
    try:
        relative = path.relative_to(Path(root).resolve())
    except ValueError:  # External P2P execution data lives outside the project Git tree.
        return
    fs.require_ignored(root, relative.as_posix())


def save_final(root, work, name, data):
    _, artifact = delivery_paths(root, work)
    target = fs.safe(artifact, name)
    require_repo_local_ignored(root, target)
    relative = str(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    fs.atomic_write(target, data, ignored_root=root)
    if target.read_bytes() != data:
        raise ValueError('storage readback failed: ' + name)
    return relative


def check_final_footprint(root, work, values):
    _, artifact = delivery_paths(root, work)
    require_repo_local_ignored(root, artifact)
    artifact.mkdir(parents=True, exist_ok=True)
    allowed = set(values) | set(RETAINED_ARTIFACTS) | SUPERSEDED_RECORDS
    existing = [path for path in artifact.rglob('*') if path.is_file() or path.is_symlink()]
    unknown = [path.relative_to(artifact).as_posix() for path in existing
               if path.is_symlink() or not path.is_file() or
               path.relative_to(artifact).as_posix() not in allowed]
    if unknown:
        raise ValueError('unclassified local P2P artifacts block cleanup: ' + ', '.join(sorted(unknown)))
    count = len(set(path.relative_to(artifact).as_posix() for path in existing) | set(values))
    size = sum(len(data) for data in values.values()) + sum(
        path.stat().st_size for path in existing
        if path.relative_to(artifact).as_posix() not in values and path.is_file())
    if count > 12 or size > 262144:
        raise ValueError(f'local P2P footprint exceeds limits: {count} files, {size} logical bytes')
    return {path.relative_to(artifact).as_posix(): fs.digest(path.read_bytes())
            for path in existing if path.relative_to(artifact).as_posix() in SUPERSEDED_RECORDS
            and path.relative_to(artifact).as_posix() not in values}


def local_directory(root, work, *, _storage_checked=False):
    common = fs.git(root, 'rev-parse', '--path-format=absolute', '--git-common-dir').decode().strip()
    repo_id = Path(root).name + '-' + fs.digest(str(Path(common).resolve()).encode())[:16]
    root = Path(root).resolve()
    slug = fs.work_slug(work)
    repo_local = root / '.p2p' / 'work' / slug
    home = Path.home().resolve()
    local_root = home / '.p2p' / 'work'
    legacy = local_root / repo_id / slug
    legacy_orchestration = legacy / 'orchestration'
    # Reuse unresolved legacy records in place; contracts and final records remain repo-local.
    legacy_present = legacy.exists() and (any((legacy / name).exists() for name in ('delivery.json', 'runtime'))
                                          or (legacy / 'artifacts/delivery.json').is_file()
                                          or (legacy_orchestration.is_dir() and not legacy_orchestration.is_symlink()
                                              and any(legacy_orchestration.iterdir())))
    repo_local_present = repo_local.exists() and (any((repo_local / name).exists() for name in ('delivery.json', 'runtime'))
                                                   or (repo_local / 'artifacts/delivery.json').is_file()
                                                   or ((repo_local / 'orchestration').is_dir()
                                                       and not (repo_local / 'orchestration').is_symlink()
                                                       and any((repo_local / 'orchestration').iterdir())))
    if legacy_present and not repo_local_present:
        local = legacy
    elif legacy_present and repo_local_present:
        raise ValueError('both repo-local and legacy P2P state exist; reconcile without overwriting either')
    else:
        local = repo_local
        if not _storage_checked:
            fs.setup(root)
    for path in (root / '.p2p', root / '.p2p' / 'work', repo_local, home / '.p2p', local_root,
                 local_root / repo_id, legacy, legacy_orchestration, local):
        if path.is_symlink():
            raise ValueError('P2P state path contains a symlink: ' + str(path))
    return local


def execution_runtime(root, work, *, _local=None):
    """Keep delivery checkouts and their Git objects outside the source checkout."""
    external_directory = execution_directory(root, work)
    local = (_local if _local is not None else local_directory(root, work)) / 'runtime'
    external = external_directory / 'runtime'
    for path in (external_directory, external):
        if path.is_symlink():
            raise ValueError('external P2P execution path contains a symlink: ' + str(path))
    if local.exists() and external.exists():
        raise ValueError('both checkout-local and external execution runtimes exist; reconcile without overwriting either')
    return local if local.exists() else external


def execution_directory(root, work):
    """Return the stable user-local directory for one repository work item."""
    return fs.execution_directory(root, work)


def agreement_root(root, work, *, _local=None):
    local = (_local if _local is not None else local_directory(root, work)) / 'agreement'
    external = execution_directory(root, work) / 'agreement'
    if local.exists() and external.exists():
        raise ValueError('both checkout-local and external agreement copies exist; reconcile without overwriting either')
    path = local if local.exists() else external
    if path.is_symlink() or (path.exists() and not path.is_dir()):
        raise ValueError('P2P agreement path is not a directory')
    return path


def local_storage_directory(root, work, name, *, _local=None):
    path = (_local if _local is not None else local_directory(root, work)) / name
    if path.is_symlink() or (path.exists() and not path.is_dir()):
        raise ValueError('repo-local P2P ' + name + ' path is not a directory')
    return path


def agreement_bindings(root, work):
    local_item = fs.safe(agreement_root(root, work), work)
    if local_item.is_file():
        return fs.bindings(agreement_root(root, work), work, require_trackable=False)
    return fs.bindings(root, work)


def imported_issue_sources(root, work):
    item, _ = delivery_paths(root, work)
    paths = []
    for line in fs.document_lines(item.read_text()):
        if not re.match(r'^Source:\s*', line):
            continue
        for label, target in re.findall(r'\[([^\]]+)\]\(([^)]+)\)', line):
            if not label.lower().startswith('imported issue') or re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', target):
                continue
            relative = os.path.normpath(str(Path(work).parent / target.split('#', 1)[0]))
            fs.safe(root, relative)
            paths.append(relative)
    return sorted(set(paths))


def delivery_paths(root, work):
    """Resolve agreements and records inside this checkout's ignored P2P root."""
    source, _ = fs.paths(root, work)
    # fs.paths just checked storage. Reuse that check within this synchronous
    # resolution only; each later read/write operation validates current storage.
    local = local_directory(root, work, _storage_checked=True)
    agreement = fs.safe(agreement_root(root, work, _local=local), work)
    if not agreement.is_file():
        agreement = source
    return agreement, local_storage_directory(root, work, 'artifacts', _local=local)


def localize_agreement(root, work, bindings):
    agreement_directory = agreement_root(root, work)
    contract_source, _ = fs.paths(root, work)
    for relative in [work, *(item['path'] for item in bindings)]:
        target = fs.safe(agreement_directory, relative)
        source = contract_source if relative == work else fs.safe(root, relative)
        require_repo_local_ignored(root, target)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not source.is_file() and target.is_file():
            continue
        data = source.read_bytes()
        if target.exists() and target.read_bytes() != data:
            raise ValueError('repo-local agreement input changed: ' + relative)
        if not target.exists():
            fs.atomic_write(target, data, ignored_root=root)
        if fs.digest(target.read_bytes()) != fs.digest(data):
            raise ValueError('repo-local agreement readback failed: ' + relative)
    origin = fs.contract_origin(root, fs.work_slug(work))
    if origin is not None:
        for relative in (origin['path'], f".p2p/work/{fs.work_slug(work)}/contract-origin.json"):
            source = fs.safe(root, relative)
            target = fs.safe(agreement_directory, relative)
            if not source.is_file():
                raise ValueError('legacy contract origin input is missing: ' + relative)
            require_repo_local_ignored(root, target)
            target.parent.mkdir(parents=True, exist_ok=True)
            data = source.read_bytes()
            if target.exists() and target.read_bytes() != data:
                raise ValueError('repo-local agreement input changed: ' + relative)
            if not target.exists():
                fs.atomic_write(target, data, ignored_root=root)
            if target.read_bytes() != data:
                raise ValueError('repo-local agreement readback failed: ' + relative)
    return fs.safe(agreement_directory, work)


def local_save(root, work, name, data):
    directory = local_directory(root, work)
    local = fs.safe(directory, name)
    relative = local.relative_to(directory)
    if relative.parts[0] in ('runtime', 'attempts'):
        prefix = ('attempts',) if relative.parts[0] == 'attempts' else ()
        external = execution_runtime(root, work, _local=directory)
        local = fs.safe(external, '/'.join((*prefix, *relative.parts[1:])))
    require_repo_local_ignored(root, local)
    local.parent.mkdir(parents=True, exist_ok=True)
    fs.atomic_write(local, data, ignored_root=root)
    if local.read_bytes() != data:
        raise ValueError('local storage readback failed: ' + name)
    return local


def git_generation_tree(workspace, manifest):
    """Write the exact non-.p2p snapshot to a temporary index and return its tree."""
    git_dir = Path(fs.git(workspace, 'rev-parse', '--absolute-git-dir').decode().strip())
    index_dir = git_dir / 'p2p-indexes'
    index_dir.mkdir(exist_ok=True)
    index = index_dir / (uuid.uuid4().hex + '.index')
    env = os.environ | {'GIT_INDEX_FILE': str(index)}

    def run(*args, input=None, stdin=None):
        result = subprocess.run(['git', '-C', str(workspace), *args], input=input,
                                stdin=stdin, env=env, capture_output=True)
        if result.returncode:
            raise ValueError(result.stderr.decode().strip() or 'local generation Git command failed')
        return result.stdout

    try:
        run('read-tree', '--empty')
        # Blob-only fast-import writes exact binary bytes in one Git process. No
        # branch, commit or reset commands are sent, so source refs stay untouched.
        # Spool the input to avoid a second in-memory copy of the entire manifest.
        with tempfile.TemporaryFile(dir=index_dir) as stream:
            for mark, item in enumerate(manifest, 1):
                content = (base64.b64decode(item['content_base64'], validate=True)
                           if item['type'] == 'file' else item['target'].encode('utf-8'))
                stream.write(f'blob\nmark :{mark}\ndata {len(content)}\n'.encode())
                stream.write(content)
                stream.write(f'\nget-mark :{mark}\n'.encode())
            stream.write(b'done\n')
            stream.seek(0)
            objects = run('fast-import', '--quiet', '--done', stdin=stream).splitlines()
        if len(objects) != len(manifest) or any(not re.fullmatch(b'[0-9a-f]{40}|[0-9a-f]{64}', oid)
                                                for oid in objects):
            raise ValueError('local generation Git blob identity response is incomplete or malformed')
        entries = [item['mode'].encode() + b' ' + oid + b'\t' + item['path'].encode('utf-8') + b'\0'
                   for item, oid in zip(manifest, objects)]
        if entries:
            run('update-index', '--add', '-z', '--index-info', input=b''.join(entries))
        return run('write-tree').decode().strip()
    finally:
        index.unlink(missing_ok=True)
        Path(str(index) + '.lock').unlink(missing_ok=True)


def record_generation(delivery, candidate, stage, manifest=None):
    state = delivery.state
    generations = state.setdefault('local_git_generations', [])
    sequence = len(generations) + 1
    workspace = delivery.workspace
    repository = delivery.runtime / 'repository.git'
    generation_ref = f'refs/p2p/{fs.work_slug(delivery.work)}/generation-{sequence:06d}'
    existing_ref = subprocess.run(['git', '-C', str(repository), 'show-ref', '--verify', '--quiet', generation_ref]).returncode == 0
    path = f'runtime/generations/{sequence:06d}.json'
    target = fs.safe(delivery.runtime, path.removeprefix('runtime/'))
    require_repo_local_ignored(delivery.root, target)
    intent_path = target.with_suffix('.pending.json')
    source_attempt = next(({'attempt_id': attempt['id'], 'report_sha256': attempt.get('report_sha256'),
                            'inputs': attempt['inputs']}
                           for attempt in reversed(state['attempts'])
                           if attempt['stage'] == stage and attempt['status'] in ('complete', 'retired')), None)
    if stage not in ('admission', 'live-evaluation') and source_attempt is None:
        raise ValueError('candidate generation has no completed stage attempt: ' + stage)
    if stage == 'live-evaluation' and not state.get('live_evaluation'):
        raise ValueError('fixture candidate admission is reserved for explicit live evaluations')
    if manifest is None:
        manifest = fs.snapshot(workspace, exclude=delivery.state.get('agreement_paths', ()))
    if fs.snapshot_key(manifest) != candidate['key']:
        raise ValueError('candidate generation differs from its exact prepared snapshot')
    tree = git_generation_tree(workspace, manifest)
    parent = generations[-1]['commit'] if generations else state['local_git_base']['local_commit']
    intent = encoded({'stage': stage, 'candidate': candidate, 'parent': parent,
                      'tree': tree, 'source_attempt': source_attempt, 'contract_sha256': state['contract']['sha256']})
    if intent_path.exists():
        if intent_path.read_bytes() != intent:
            raise ValueError('conflicting pending candidate generation: ' + path)
    elif existing_ref or target.exists():
        raise ValueError('local generation exists outside recovery state: ' + path)
    else:
        intent_path.parent.mkdir(parents=True, exist_ok=True)
        fs.atomic_write(intent_path, intent, ignored_root=delivery.root)
    if existing_ref:
        commit = fs.git(repository, 'rev-parse', generation_ref).decode().strip()
        if (fs.git(repository, 'rev-parse', commit + '^{tree}').decode().strip() != tree or
                fs.git(repository, 'rev-parse', commit + '^').decode().strip() != parent):
            raise ValueError('pending generation ref has unexpected content or parent')
    else:
        commit = subprocess.run(['git', '-C', str(workspace), '-c', 'user.name=Promise-to-Proof',
                                 '-c', 'user.email=p2p@localhost', 'commit-tree', tree, '-p', parent,
                                 '-m', f'P2P {delivery.work} generation {sequence}'],
                                capture_output=True, text=True)
        if commit.returncode:
            raise ValueError('local Git generation commit failed: ' + commit.stderr.strip())
        commit = commit.stdout.strip()
        fs.git(repository, 'update-ref', generation_ref, commit)
    previous_key = generations[-1]['candidate_key'] if generations else None
    record = {'schema': 'promise-to-proof/local-generation/v1', 'sequence': sequence,
              'stage': stage, 'work_item': delivery.work,
              'repository_id': state['local_git_base']['repository_id'],
              'invocation_id': state['invocation_id'], 'comparison_base': state['comparison_base'],
              'base_tree': state['local_git_base']['tree'],
              'contract_sha256': state['contract']['sha256'], 'parent_commit': parent,
              'previous_candidate_key': previous_key, 'source_attempt': source_attempt,
              'candidate_key': candidate['key'],
              'changes': candidate['changes'], 'tree': tree, 'commit': commit,
              'ref': generation_ref}
    data = encoded(record)
    if target.exists() and target.read_bytes() != data:
        raise ValueError('conflicting pending generation record: ' + path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fs.atomic_write(target, data, ignored_root=delivery.root)
    if target.read_bytes() != data:
        raise ValueError('local generation record readback failed: ' + path)
    summary = record | {'record_path': path, 'record_sha256': fs.digest(data)}
    generations.append(summary)
    return summary


def materialize(root, manifest, ignored_root=None):
    if ignored_root is not None:
        require_repo_local_ignored(ignored_root, root)
    root.mkdir(parents=True, exist_ok=True)
    for entry in manifest:
        target = fs.safe(root, entry['path'])
        if ignored_root is not None:
            require_repo_local_ignored(ignored_root, target)
        target.parent.mkdir(parents=True, exist_ok=True)
        if entry['type'] == 'symlink':
            target.symlink_to(entry['target'])
        else:
            target.write_bytes(base64.b64decode(entry['content_base64'], validate=True))
            target.chmod(int(entry['mode'], 8) & 0o777)


def contract(root, work):
    item, _ = delivery_paths(root, work)
    return parse_contract(item.read_bytes())


def parse_contract(data):
    text = data.decode('utf-8')
    revision = re.findall(r'^Contract revision: (v[1-9][0-9]*)\r?$', text, re.M)
    heading = re.findall(r'^# Acceptance contract: ([^\r\n]+)\r?$', text, re.M)
    if len(revision) != 1 or len(heading) != 1:
        raise ValueError('established contract heading/revision is missing or ambiguous')
    result = dict(source=heading[0], revision=revision[0], content=text, sha256=fs.digest(data))
    issues = []
    _, _, _, requirements = bundle._validate_contract(result, issues)
    if issues:
        raise ValueError('agreement: ' + json.dumps(issues))
    return result, requirements


def identity(candidate):
    return {key: value for key, value in candidate.items() if key != 'manifest'}


def report_identity(candidate):
    return {key: value for key, value in identity(candidate).items() if key != 'changes'}


def candidate_key(candidate):
    return candidate.get('key') or 'git:' + candidate['commit']


ISSUE_RECORD_PREFIX = '<!-- promise-to-proof-delivery:v1:'


def issue_source(root, work, content):
    urls = re.findall(r'^Source attribution:\s*(https://github\.com/[^\s;]+/issues/\d+)',
                      content, re.M)
    if not urls:
        return None
    if len(set(urls)) != 1:
        raise ValueError('contract has conflicting GitHub source issues')
    match = re.fullmatch(r'https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/issues/(\d+)', urls[0])
    if not match:
        raise ValueError('contract GitHub source issue URL is invalid')
    sources = imported_issue_sources(root, work)
    if len(sources) != 1:
        raise ValueError('contract must bind exactly one imported issue source document')
    agreement, _ = delivery_paths(root, work)
    source = fs.safe(agreement.parent.parent, sources[0])
    if not source.is_file():
        source = fs.safe(root, sources[0])
    return {'repository': match[1] + '/' + match[2], 'issue': int(match[3]), 'url': urls[0],
            'body_sha256': fs.digest(source.read_bytes())}


def issue_record_preview(delivery, delivered_commit, pull_request=None):
    state = delivery.state
    if state.get('status') != 'REVIEWED_AND_PROVEN':
        raise ValueError('GitHub record requires a REVIEWED_AND_PROVEN delivery')
    source = issue_source(delivery.root, delivery.work, state['contract']['content'])
    if source is None:
        raise ValueError('work item has no imported GitHub issue source')
    if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', delivered_commit):
        raise ValueError('delivered commit must be a full commit SHA')
    if fs.full_commit(delivery.root, delivered_commit) != delivered_commit:
        raise ValueError('delivered commit identity changed')
    candidate = state['candidate']
    agreement_paths = state.get('agreement_paths', [delivery.work])
    tree_key = fs.snapshot_key(fs.snapshot(delivery.root, delivered_commit, exclude=agreement_paths))
    if tree_key != candidate_key(candidate):
        raise ValueError('delivered commit product tree does not match the accepted candidate')
    contract_text = state['contract']['content']
    if fs.digest(contract_text.encode()) != state['contract']['sha256']:
        raise ValueError('accepted contract text does not match its recorded digest')
    if pull_request is not None and not re.fullmatch(r'https://github\.com/[^/]+/[^/]+/pull/\d+', pull_request):
        raise ValueError('pull request must be a full GitHub pull request URL')
    record = {
        'schema': 'promise-to-proof/durable-delivery/v1',
        'id': state['invocation_id'],
        'work_item': delivery.work,
        'repository': source['repository'],
        'source_issue': {'url': source['url'], 'body_sha256': source['body_sha256']},
        'contract': {'revision': state['contract']['revision'], 'sha256': state['contract']['sha256'],
                     'text': contract_text},
        'comparison_base': state['comparison_base'],
        'candidate_key': candidate_key(candidate),
        'candidate_changes_sha256': fs.digest(fs.canonical(candidate.get('changes', []))),
        'review': {'status': 'REVIEWED', 'sha256': fs.digest(state['final_review'].encode())},
        'proof': {'status': 'PROVEN', 'sha256': fs.digest(state['final_proof'].encode())},
        'requirements': sorted(state['requirements']),
        'agreement_paths': agreement_paths,
        'delivered_commit': delivered_commit,
        'pull_request': pull_request,
        'completed_at': state['completed_at'],
    }
    marker = ISSUE_RECORD_PREFIX + state['invocation_id'] + ' -->'
    body = marker + '\n```json\n' + json.dumps(record, sort_keys=True, indent=2, ensure_ascii=False) + '\n```\n'
    if len(body.encode()) > 60000:
        raise ValueError('durable GitHub record exceeds the 60 KB comment limit')
    return {'repository': source['repository'], 'issue': source['issue'], 'id': state['invocation_id'],
            'record': record, 'body': body, 'sha256': fs.digest(body.encode())}


def github_issue(repository, issue):
    result = subprocess.run(['gh', 'api', f'repos/{repository}/issues/{issue}'],
                            capture_output=True, text=True)
    if result.returncode:
        raise ValueError('GitHub issue read failed: ' + result.stderr.strip())
    return json.loads(result.stdout)


def github_comments(repository, issue):
    result = subprocess.run(['gh', 'api', '--paginate', '--jq', '.[]',
                             f'repos/{repository}/issues/{issue}/comments'],
                            capture_output=True, text=True)
    if result.returncode:
        raise ValueError('GitHub issue comments read failed: ' + result.stderr.strip())
    return [json.loads(line) for line in result.stdout.splitlines() if line.strip()]


def github_create_comment(repository, issue, body):
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='', delete=True) as file:
        file.write(body)
        file.flush()
        result = subprocess.run(['gh', 'issue', 'comment', str(issue), '--repo', repository,
                                 '--body-file', file.name], capture_output=True, text=True)
    if result.returncode:
        raise ValueError('GitHub delivery record write failed; read comments before retrying: ' + result.stderr.strip())
    return result.stdout.strip()


def publish_issue_record(delivery, delivered_commit, pull_request, authorized_sha256):
    preview = issue_record_preview(delivery, delivered_commit, pull_request)
    if authorized_sha256 is None:
        mandate = delivery.state.get('autonomy')
        if not mandate:
            raise ValueError('publication requires exact preview authority or a standing issue-comment grant')
        autonomy.authorize(mandate, 'issue-comment', preview['repository'],
                           f'https://github.com/{preview["repository"]}/issues/{preview["issue"]}')
        authorized_sha256 = preview['sha256']
    if authorized_sha256 != preview['sha256']:
        raise ValueError('publication authorization does not match preview SHA-256 ' + preview['sha256'])
    issue = github_issue(preview['repository'], preview['issue'])
    if fs.digest((issue.get('body') or '').encode()) != preview['record']['source_issue']['body_sha256']:
        raise ValueError('source issue body changed since the accepted contract was captured')
    comments = github_comments(preview['repository'], preview['issue'])
    marker = ISSUE_RECORD_PREFIX + preview['id'] + ' -->'
    records = [comment for comment in comments if ISSUE_RECORD_PREFIX in comment.get('body', '')]
    matches = [comment for comment in records if marker in comment.get('body', '')]
    if len(records) > 1 or len(matches) > 1:
        raise ValueError('multiple durable delivery records exist on the source issue')
    if records and not matches:
        raise ValueError('source issue has a conflicting durable delivery record')
    if matches and matches[0].get('body') != preview['body']:
        raise ValueError('existing durable delivery record conflicts with this preview')
    if not matches:
        try:
            github_create_comment(preview['repository'], preview['issue'], preview['body'])
        except ValueError:
            # The server may have accepted a write whose response was lost; read before any retry.
            comments = github_comments(preview['repository'], preview['issue'])
            matches = [comment for comment in comments if marker in comment.get('body', '')]
            if len(matches) != 1 or matches[0].get('body') != preview['body']:
                raise
    comments = github_comments(preview['repository'], preview['issue'])
    matches = [comment for comment in comments if marker in comment.get('body', '')]
    if len(matches) != 1 or matches[0].get('body') != preview['body']:
        raise ValueError('durable GitHub record readback failed; local state retained')
    comment = matches[0]
    delivery.state['github_record'] = {'id': preview['id'], 'repository': preview['repository'],
                                       'issue': preview['issue'], 'url': comment.get('html_url'),
                                       'delivered_commit': delivered_commit, 'pull_request': pull_request,
                                       'body_sha256': preview['sha256'], 'verified_at': now()}
    delivery.save()
    delivery.checkpoint()
    return delivery.state['github_record']


def resolve_github_record(root, repository, issue_number):
    issue = github_issue(repository, issue_number)
    comments = github_comments(repository, issue_number)
    records = []
    for comment in comments:
        body = comment.get('body', '')
        if ISSUE_RECORD_PREFIX not in body:
            continue
        match = re.search(re.escape(ISSUE_RECORD_PREFIX) + r'([0-9a-f-]+) -->\n```json\n(.*?)\n```\n?$',
                          body, re.S)
        if not match:
            raise ValueError('durable GitHub delivery record is malformed')
        record = json.loads(match[2])
        if match[1] != record.get('id'):
            raise ValueError('durable GitHub delivery record marker conflicts with its identity')
        records.append((comment, record))
    if len(records) != 1:
        raise ValueError('expected exactly one durable delivery record on the source issue')
    comment, record = records[0]
    if (record.get('schema') != 'promise-to-proof/durable-delivery/v1' or
            record.get('repository') != repository or
            record.get('source_issue', {}).get('url') != f'https://github.com/{repository}/issues/{issue_number}'):
        raise ValueError('durable GitHub delivery record belongs to another source issue')
    contract = record.get('contract', {})
    if (not isinstance(contract.get('text'), str) or
            fs.digest(contract['text'].encode()) != contract.get('sha256') or
            not re.fullmatch(r'v[1-9][0-9]*', contract.get('revision', ''))):
        raise ValueError('durable GitHub record contract text or digest is invalid')
    source_names = re.findall(r'^# Acceptance contract: ([^\r\n]+)\r?$', contract['text'], re.M)
    if len(source_names) != 1:
        raise ValueError('durable GitHub record contract heading is invalid')
    issues = []
    _, _, _, requirement_ids = bundle._validate_contract(
        {'source': source_names[0], 'revision': contract['revision'], 'content': contract['text'],
         'sha256': contract['sha256']}, issues)
    if issues or record.get('requirements') != sorted(requirement_ids):
        raise ValueError('durable GitHub record requirement coverage does not match the exact contract')
    work = record.get('work_item', '')
    if not isinstance(work, str) or not fs.WORK.fullmatch(work):
        raise ValueError('durable GitHub delivery record has an invalid work item')
    sources = []
    for target in re.findall(r'\[Imported issue[^\]]*\]\(([^)]+)\)', contract['text'], re.I):
        if not re.match(r'[A-Za-z][A-Za-z0-9+.-]*:', target):
            sources.append(os.path.normpath(str(Path(work).parent / target.split('#', 1)[0])))
    expected_agreement_paths = sorted({work, *sources})
    if record.get('agreement_paths') != expected_agreement_paths:
        raise ValueError('durable GitHub record has invalid contract exclusion paths')
    for key in ('comparison_base', 'delivered_commit'):
        if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', record.get(key, '')):
            raise ValueError('durable GitHub delivery record has an invalid ' + key)
    if (not re.fullmatch(r'[0-9a-f]{64}', record.get('candidate_changes_sha256', '')) or
            not re.fullmatch(r'snapshot:sha256:[0-9a-f]{64}', record.get('candidate_key', '')) or
            not re.fullmatch(r'[0-9a-f]{64}', record.get('source_issue', {}).get('body_sha256', ''))):
        raise ValueError('durable GitHub delivery record has an invalid candidate or source digest')
    pull_request = record.get('pull_request')
    if pull_request is not None and not re.fullmatch(r'https://github\.com/[^/]+/[^/]+/pull/\d+', pull_request):
        raise ValueError('durable GitHub delivery record has an invalid pull request URL')
    for key, status in (('review', 'REVIEWED'), ('proof', 'PROVEN')):
        item = record.get(key, {})
        if item.get('status') != status or not re.fullmatch(r'[0-9a-f]{64}', item.get('sha256', '')):
            raise ValueError('durable GitHub record has invalid ' + key + ' status or digest')
    commit = fs.full_commit(root, record['delivered_commit'])
    if commit != record['delivered_commit']:
        raise ValueError('delivered commit identity changed')
    fs.full_commit(root, record['comparison_base'])
    ancestry = subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor',
                               record['comparison_base'], commit], capture_output=True)
    if ancestry.returncode:
        raise ValueError('delivered commit is not based on the frozen comparison base')
    tree_key = fs.snapshot_key(fs.snapshot(root, commit, exclude=record.get('agreement_paths', ())))
    if tree_key != record.get('candidate_key'):
        raise ValueError('delivered Git commit product tree does not match the accepted candidate')
    delivered_tree = fs.snapshot(root, commit, exclude=record['agreement_paths'])
    base_tree = fs.snapshot(root, record['comparison_base'], exclude=record['agreement_paths'])
    if fs.digest(fs.canonical(fs.tree_changes(base_tree, delivered_tree))) != record.get('candidate_changes_sha256'):
        raise ValueError('delivered Git commit changes do not match the accepted candidate digest')
    return {'status': 'REVIEWED_AND_PROVEN', 'repository': repository,
            'source_issue': {'url': f'https://github.com/{repository}/issues/{issue_number}',
                             'body_sha256': record['source_issue'].get('body_sha256')},
            'contract': contract, 'comparison_base': record['comparison_base'],
            'candidate_key': record['candidate_key'], 'candidate_changes_sha256': record['candidate_changes_sha256'],
            'review': record['review'], 'proof': record['proof'], 'requirements': record['requirements'],
            'delivered_commit': commit, 'pull_request': record.get('pull_request'),
            'completed_at': record['completed_at'], 'record_url': comment.get('html_url'),
            'record_sha256': fs.digest(comment['body'].encode()), 'live_issue_title': issue.get('title')}


def skills():
    result = {}
    for stage, name in STAGES.items():
        result[stage] = installed_skill(name)
    return result


def installed_skill(name):
    options = [Path.home() / '.agents/skills' / name / 'SKILL.md',
               Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'skills' / name / 'SKILL.md']
    found = next((path.resolve() for path in options if path.is_file()), None)
    if found is None:
        raise ValueError('installed skill unavailable: ' + name)
    return {'path': str(found), 'sha256': fs.digest(found.read_bytes())}


def instruction_ids(state):
    """Only retained instruction versions referenced by this delivery travel with it."""
    identities = {state['instruction_identity']} if state.get('instruction_identity') else set()
    for transition in state.get('instruction_history', []):
        identities.update((transition['from'], transition['to']))
    for attempt in state.get('attempts', []):
        if attempt.get('inputs', {}).get('instruction_identity'):
            identities.add(attempt['inputs']['instruction_identity'])
    return identities


def instruction_upgrade_authority(state):
    mandate = state.get('autonomy')
    if not mandate:
        raise ValueError('instruction upgrade needs a current local decision mandate; '
                         'continue with the pinned instructions or select a covering mandate through extend')
    autonomy.current(mandate)
    if not {'implementation', 'evidence'} <= set(mandate['policy']['decisions']):
        raise ValueError('instruction upgrade needs implementation and evidence decisions in the current mandate; '
                         'continue with the pinned instructions or select a covering mandate through extend')
    return {'mandate_sha256': mandate['sha256'],
            'mandate_policy_sha256': fs.digest(fs.canonical(mandate['policy']))}


def upstream_destination(root):
    """Resolve one configured upstream without guessing from the requested SHA."""
    try:
        branch = fs.git(root, 'symbolic-ref', '--quiet', '--short', 'HEAD').decode().strip()
        remotes = fs.git(root, 'config', '--get-all', f'branch.{branch}.remote').decode().splitlines()
        merges = fs.git(root, 'config', '--get-all', f'branch.{branch}.merge').decode().splitlines()
    except ValueError as error:
        raise ValueError('unsliced delivery needs --destination or one configured upstream') from error
    if len(remotes) != 1 or len(merges) != 1 or not merges[0].startswith('refs/heads/'):
        raise ValueError('unsliced delivery needs --destination or one unambiguous configured upstream')
    remote, branch_ref = remotes[0], merges[0]
    branch_name = branch_ref.removeprefix('refs/heads/')
    if remote == '.':
        destination, ref = branch_name, branch_ref
    else:
        destination, ref = f'{remote}/{branch_name}', f'refs/remotes/{remote}/{branch_name}'
    fs.git(root, 'check-ref-format', ref)
    return destination, ref


def explicit_destination(root, value):
    for prefix in ('refs/heads/', 'refs/remotes/'):
        if value.startswith(prefix):
            try:
                fs.git(root, 'check-ref-format', value)
            except ValueError:
                raise ValueError('invalid workflow destination: ' + value)
            return value.removeprefix(prefix), value
    if value.startswith('refs/'):
        raise ValueError('destination must be a local branch or remote-tracking ref')
    ref = 'refs/heads/' + value
    try:
        fs.git(root, 'check-ref-format', ref)
    except ValueError:
        raise ValueError('invalid workflow destination: ' + value)
    return value, ref


def routing(root, work, destination=None, require_tip=True):
    """Read the approved Markdown decision; never infer approval or a child target."""
    item, _ = delivery_paths(root, work)
    own_directory = local_directory(root, work) / 'artifacts'
    parents = []
    for line in fs.document_lines(item.read_text()):
        if re.match(r'^Parent(?: contract)?:', line):
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', line):
                parent = os.path.normpath(str(Path(work).parent / target.split('#', 1)[0]))
                fs.paths(root, parent)
                parents.append(parent)
    if len(parents) > 1:
        raise ValueError('conflicting parent routing; hand off to slice-contract')
    if not parents and not (own_directory / 'slicing.md').exists():
        if destination:
            target, ref = explicit_destination(root, destination)
        else:
            target, ref = upstream_destination(root)
        route = {'path': None, 'parent': None, 'revision': None, 'sha256': None, 'text': None,
                 'approval_source': None, 'destination': target, 'target_ref': ref,
                 'selection': 'explicit' if destination else 'upstream'}
    else:
        parent = parents[0] if parents else work
        _, directory = fs.paths(root, parent)
        path = fs.safe(root, str((directory / 'slicing.md').relative_to(root)))
        if not path.is_file():
            raise ValueError('missing approved routing; hand off to slice-contract ' + parent)
        data = path.read_bytes()
        sections = re.findall(rb'^## Approved delivery plan\r?\n.*?(?=^## |\Z)', data, re.M | re.S)
        if len(sections) != 1 or list(fs.document_lines(data.decode())).count('## Approved delivery plan') != 1:
            raise ValueError('missing/conflicting approved routing; normalize explicit legacy approval or hand off to slice-contract ' + parent)
        text = sections[0].decode()
        metadata = '\n'.join(fs.document_lines(text))
        def field(name):
            values = re.findall(r'^' + re.escape(name) + r': (.+)$', metadata, re.M)
            if len(values) != 1 or not values[0].strip():
                raise ValueError('missing/conflicting delivery plan field: ' + name)
            return values[0].strip()
        revision, approval = field('Plan revision'), field('Approval source')
        if not re.fullmatch(r'v[1-9][0-9]*', revision) or approval.lower() in ('none', 'pending', 'unknown'):
            raise ValueError('routing has no explicit approved revision/source; hand off to slice-contract ' + parent)
        if field('Parent') != parent:
            raise ValueError('delivery plan names a different parent')
        final, integration, start = field('Final destination'), field('Integration branch'), field('Integration start')
        default = field('Default choice')
        if default not in ('independent', 'grouped'):
            raise ValueError('invalid default delivery choice')
        for branch in (final, integration):
            if branch != 'none':
                fs.git(root, 'check-ref-format', 'refs/heads/' + branch)
        if final == 'none' or final == integration or (integration == 'none') != (start == 'none'):
            raise ValueError('conflicting final/integration destinations')
        if integration != 'none' and not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', start):
            raise ValueError('integration setup requires a full starting commit SHA')
        rows = {}
        for line in metadata.splitlines():
            if not line.startswith('|'):
                continue
            cells = [x.strip() for x in line.strip('|').split('|')]
            if not cells or cells[0] == 'Child' or re.fullmatch(r'[-: ]+', cells[0]):
                continue
            if len(cells) != 5:
                raise ValueError('invalid delivery child row')
            child, choice, row_destination, reason, state = cells
            fs.paths(root, child)
            if child in rows or state not in ('remaining', 'landed') or not reason:
                raise ValueError('duplicate or incomplete delivery child row: ' + child)
            choice = default if choice == 'default' else choice
            expected = {'independent': final, 'grouped': integration}.get(choice)
            if expected is None or row_destination == 'none' or row_destination != expected:
                raise ValueError('conflicting child destination: ' + child)
            if state == 'landed' and row_destination != final:
                raise ValueError('landed child must retain its final destination')
            rows[child] = row_destination
        if parents and work not in rows:
            raise ValueError('child missing from approved routing; hand off to slice-contract ' + parent)
        target = rows[work] if parents else final
        local_ref = f'refs/heads/{target}'
        ref = local_ref
        remote = target.partition('/')[0]
        if '/' in target and remote in fs.git(root, 'remote').decode().splitlines():
            remote_ref = f'refs/remotes/{target}'
            def exists(candidate):
                return subprocess.run(['git', '-C', str(root), 'show-ref', '--verify', '--quiet', candidate],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
            local_exists, remote_exists = exists(local_ref), exists(remote_ref)
            qualified = bool(destination and destination.startswith(('refs/heads/', 'refs/remotes/')))
            if local_exists and remote_exists and not qualified:
                raise ValueError('ambiguous approved destination: ' + target +
                                 ' exists as both local and remote-tracking refs; pass a fully qualified destination')
            if remote_exists or not local_exists:
                ref = remote_ref
        route = {'path': str(path.relative_to(root)), 'parent': parent, 'revision': revision,
                 'sha256': fs.digest(sections[0]), 'text': text, 'approval_source': approval,
                 'destination': target, 'target_ref': ref, 'selection': 'approved-plan'}
        if destination:
            requested, requested_ref = explicit_destination(root, destination)
            if requested != target:
                raise ValueError('workflow destination conflicts with approved delivery plan: ' + target)
            if destination.startswith('refs/'):
                ref = route['target_ref'] = requested_ref
    # An explicit local ref is required for local delivery. Skills inspect remote
    # state and perform any authorized setup before admitting this controller.
    try:
        tip = fs.full_commit(root, ref)
    except ValueError as error:
        if not require_tip:
            tip = None
        else:
            setup = f'; setup {ref} at {start} under covering authority and read back the ref' if route.get('path') and target == integration else ''
            raise ValueError('delivery destination missing: ' + ref + setup) from error
    if route.get('path') and target == integration and tip and require_tip:
        fs.full_commit(root, start)
        result = subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', start, tip], capture_output=True)
        if result.returncode:
            raise ValueError('integration branch conflicts with approved starting commit: ' + ref)
    return route | {'target_tip': tip}


def route_identity(route):
    identity = {key: value for key, value in route.items() if key != 'target_tip'}
    # Older retained routes predate `selection`. Their destination and plan
    # fields still identify the same choice, so normalize the added field.
    selection = identity.get('selection')
    if selection is None:
        selection = 'approved-plan' if identity.get('path') else 'explicit'
    if selection == 'approved-plan':
        identity.pop('selection', None)
    else:
        identity['selection'] = selection
    return identity


def route_record(route):
    return {key: value for key, value in route.items()
            if not (key == 'selection' and value == 'approved-plan')}


def destination_observation(root, route, base):
    observed = now()
    try:
        tip = fs.full_commit(root, route['target_ref'])
    except ValueError:
        tip = None
    relation = 'unavailable'
    if tip == base:
        relation = 'unchanged'
    elif tip is not None:
        result = subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', base, tip], capture_output=True)
        relation = 'fast-forward' if result.returncode == 0 else 'non-fast-forward' if result.returncode == 1 else 'unavailable'
    return {'destination': route['destination'], 'comparison_base': base,
            'observed_tip': tip, 'relation': relation, 'observed_at': observed}


def validate_sidecar_plan(root, decision, work):
    """Reject current sidecar plan identities that differ from the active route."""
    _, directory = fs.paths(root, work)
    for name in ('slicing.md', 'delivery-shape.md'):
        sidecar = directory / name
        if not sidecar.is_file():
            continue
        for line in fs.document_lines(sidecar.read_text()):
            if re.search(r'plan.*section.*SHA-256', line, re.IGNORECASE):
                hashes = re.findall(r'SHA-256\s+`?([0-9a-f]{64})', line)
                if hashes != [decision.get('sha256')]:
                    raise ValueError('current sidecar plan-section digest differs from active route; '
                                     'reconcile ' + str(sidecar.relative_to(root)))


def routing_records(root, decision, work):
    """Transfer approved routing and current work-item sizing evidence."""
    validate_sidecar_plan(root, decision, work)
    _, work_directory = fs.paths(root, work)
    path = fs.safe(root, decision['path']) if decision and decision.get('path') else None
    selected = set()
    if path:
        selected.add(path)
        selected.update(path.parent.glob('history/**/slicing.md'))
        approval = path.parent / 'planning-handoff.md'
        if approval.is_file():
            selected.add(approval)
    for name in ('slicing.md', 'delivery-shape.md'):
        sidecar = fs.safe(root, str(work_directory.relative_to(root) / name))
        if sidecar.is_file():
            selected.add(sidecar)
    selected.update(work_directory.glob('history/**/slicing.md'))
    selected.update(work_directory.glob('history/**/delivery-shape.md'))
    # Local Markdown references can carry approval and captured parent evidence.
    pending = list(selected)
    while pending:
        file = pending.pop()
        fs.safe(root, str(file.relative_to(root)))
        if file.suffix != '.md':
            continue
        # History retains the original bytes, including original relative links.
        origin = file.parent
        for owner in (work_directory, path.parent if path else None):
            if owner is not None and owner / 'history' in file.parents:
                origin = owner
                break
        text = file.read_text()
        targets = re.findall(r'\[[^\]]*\]\(([^)]+)\)', text)
        # Older approvals name bare local Markdown receipts. Keep their bytes and
        # authority intact while giving them the same transfer checks as links.
        for line in fs.document_lines(text):
            if line.startswith('Approval source:'):
                plain = re.sub(r'\[[^\]]*\]\([^)]+\)|[a-zA-Z][a-zA-Z0-9+.-]*://\S+', '', line)
                targets.extend(re.findall(r'(?<![\w/])([.\w/-]+\.md)(?=$|[\s.,;`])', plain))
        for target in targets:
            if re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', target):
                continue
            relative = os.path.normpath(str(origin.relative_to(root) / target.split('#', 1)[0]))
            if relative.startswith('.p2p/'):
                linked = fs.safe(root, relative)
                if not linked.is_file():
                    raise ValueError('routing evidence unavailable: ' + relative)
                if linked not in selected:
                    selected.add(linked)
                    pending.append(linked)
    return [{'path': str(file.relative_to(root)), 'sha256': fs.digest(file.read_bytes()),
             'content_base64': base64.b64encode(file.read_bytes()).decode(), 'type': 'file', 'mode': '100644'}
            for file in sorted(selected)]


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


def launch(args, prompt, event_path, error_path, deadline, idle_seconds=None):
    """Only transport seam. Tests replace it; the CLI has no fake-host switch."""
    started_epoch = time.time()
    started = time.monotonic()
    launch_started = datetime.datetime.fromtimestamp(started_epoch, datetime.timezone.utc).isoformat()
    remaining = None if deadline is None else max(0, deadline - time.time())
    stop = None if remaining is None else started + remaining
    with event_path.open('xb') as events, error_path.open('xb') as errors:
        process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=events, stderr=errors,
                                   start_new_session=True)
        outcome = 'finished'
        interrupted = False
        payload = prompt.encode()
        while True:
            remaining = None if stop is None else max(0, stop - time.monotonic())
            try:
                timeout = HEARTBEAT_SECONDS if remaining is None else min(HEARTBEAT_SECONDS, remaining)
                if idle_seconds is not None:
                    timeout = min(timeout, max(0.01, idle_seconds))
                process.communicate(payload, timeout=timeout)
                break
            except subprocess.TimeoutExpired:
                payload = None  # communicate resumes the original input after a timeout.
                activity = max(os.fstat(events.fileno()).st_mtime, os.fstat(errors.fileno()).st_mtime)
                if idle_seconds is not None and time.time() - activity >= idle_seconds:
                    outcome = 'stalled'
                    interrupted = True
                    break
                if stop is None or time.monotonic() < stop:
                    print(f'[{event_path.parent.name}] running {time.monotonic() - started:.0f}s; '
                          f'last log activity {max(0, time.time() - activity):.0f}s ago '
                          '(activity is not verified progress)', file=sys.stderr, flush=True)
                    continue
                interrupted = True
                break
        if interrupted:
            if outcome != 'stalled':
                outcome = 'interrupted'
            import signal
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
            # The parent can exit while descendants ignore TERM.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
        elapsed_seconds = max(0, time.monotonic() - started)
        launch_finished = datetime.datetime.fromtimestamp(started_epoch + elapsed_seconds,
                                                           datetime.timezone.utc).isoformat()
        events.flush()
        errors.flush()
        os.fsync(events.fileno())
        os.fsync(errors.fileno())
    return {'exit_code': process.returncode, 'outcome': outcome, 'finished': launch_finished,
            'launch_started': launch_started, 'launch_finished': launch_finished,
            'elapsed_seconds': elapsed_seconds}


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


def report_schema(stage, coverage=False, risks=False, implementation_slices=False):
    string = {'type': 'string'}
    def obj(properties):
        return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}
    evidence = obj({'assertion': string, 'observation': string, 'artifact': string})
    learning = obj({'scope': string, 'lesson': string, 'evidence': string, 'uncertainty': string})
    status = {'type': 'string'}
    if stage == 'review':
        status['enum'] = ['REVIEWED', 'CHANGES NEEDED', 'BLOCKED']
        row = obj({'id': string, 'observation': string})
        finding = obj({'id': string, 'source': string,
                       'axis': {'type': 'string', 'enum': ['Contract fidelity', 'Scope and simplicity', 'Engineering quality']},
                       'location': string, 'evidence': string, 'consequence': string, 'correction': string,
                       'handoff': {'type': 'string', 'enum': ['implement-contract', 'plan-acceptance']}})
        check = obj({'command': string,
                     'result': {'type': 'string', 'enum': ['passed', 'failed', 'observed', 'unavailable']},
                     'observation': string})
    else:
        row = obj({'id': string, 'verdict': string, 'observation': string,
                   'evidence': {'type': 'array', 'items': evidence}})
    properties = {'status': status, 'input_identity_json': string}
    if stage != 'review':
        properties['details'] = string
    properties.update(requirements={'type': 'array', 'items': row},
                      gaps={'type': 'array', 'items': string},
                      learning_candidates={'type': 'array', 'items': learning, 'maxItems': 5})
    if stage == 'review':
        properties.update(coverage=string, checks={'type': 'array', 'items': check},
                          limitations={'type': 'array', 'items': string},
                          findings={'type': 'array', 'items': finding},
                          missing_input=string, expected_result=string)
    if coverage:
        row = obj({'id': string, 'paths': {'type': 'array', 'items': string},
                   'existing': {'type': 'boolean'},
                   'evidence': {'type': 'array', 'items': string}})
        trace = obj({'requirements': {'type': 'array', 'items': row},
                     'supporting_changes': {'type': 'array', 'items': obj({'path': string, 'reason': string})}})
        if stage == 'review':
            trace['properties']['inspected_paths'] = {'type': 'array', 'items': string}
            trace['required'].append('inspected_paths')
        if risks:
            risk = obj({
                'id': string,
                'requirements': {'type': 'array', 'items': string},
                'paths': {'type': 'array', 'items': string},
                'reach': {'type': 'string', 'enum': ['bounded', 'uncertain']},
                'trigger': string,
                'why_applicable': string,
                'consequence': string,
                'evidence': {'type': 'array', 'items': string},
                'status': {'type': 'string', 'enum': ['addressed', 'unresolved']},
            })
            trace['properties']['risks'] = {'type': 'array', 'items': risk}
            trace['required'].append('risks')
        properties['coverage_trace'] = trace
    if stage == 'implementation' and implementation_slices:
        properties['implementation_slice'] = slices.schema()
    return obj(properties)


def coverage_markdown(report, scope=None):
    trace = report.get('coverage_trace')
    if trace is None:
        return ''
    lines = ['## Where the work and evidence are', '', 'Trace references do not grant proof verdicts.']
    for row in trace['requirements']:
        paths = ', '.join(row['paths'])
        source = paths or ('existing behavior' if row['existing'] else 'not yet identified')
        evidence = ', '.join(row['evidence']) or 'not yet established'
        lines.append(f"- {row['id']}: {source}; evidence: {evidence}")
    for extra in trace['supporting_changes']:
        lines.append(f"- Supporting change {extra['path']}: {extra['reason']}")
    for risk in trace.get('risks', []):
        lines.append(f"- Material risk {risk['id']} ({', '.join(risk['requirements'])}): "
                     f"{risk['trigger']} → {risk['consequence']}. "
                     f"Applies because {risk['why_applicable']}; "
                     f"checked by {', '.join(risk['evidence']) or 'not yet established'} "
                     f"({risk['status']}, reach {risk['reach']}).")
    if scope:
        lines.append(f"Exact reviewed product scope: {len(scope['inspected'])} inspected paths, "
                     f"{len(scope['changed_paths'])} changed paths, "
                     f"candidate {scope['candidate_key']}, base {scope['comparison_base']}; "
                     f"manifest SHA-256 {scope['manifest_sha256']}.")
    return '\n'.join(lines)


def learning_candidates_markdown(report):
    lines = ['## Learning candidates', '']
    candidates = report.get('learning_candidates', [])
    if not candidates:
        lines.append('None.')
    else:
        for index, item in enumerate(candidates, 1):
            lines.extend([
                f"### L{index}: {item['scope']}",
                '',
                item['lesson'],
                '',
                '- Evidence: ' + item['evidence'],
                '- Uncertainty: ' + item['uncertainty'],
                '- Status: candidate only; retrospective validation required.',
                '',
            ])
    return '\n'.join(lines).rstrip()


def report_markdown(report):
    lines = [f"# {report['status']}", '', '## Requirements', '']
    for row in report['requirements']:
        lines.extend([f"### {row['id']}", '', row['observation'], ''])
        if 'verdict' in row:
            lines.append('Verdict: ' + row['verdict'])
        for evidence in row.get('evidence', []):
            lines.extend(['', '#### Evidence', '- Assertion: ' + evidence['assertion'],
                          '- Observation: ' + evidence['observation'],
                          '- Artifact: ' + evidence['artifact']])
        lines.append('')
    if 'findings' in report:
        lines.extend(['## Findings', ''])
        lines.extend('- ' + item for item in report['findings'])
        if not report['findings']:
            lines.append('None.')
        lines.append('')
    lines.extend(['## Gaps', ''])
    lines.extend('- ' + item for item in report['gaps'])
    if not report['gaps']:
        lines.append('None.')
    lines.extend(['', learning_candidates_markdown(report)])
    return '\n'.join(lines).rstrip() + '\n'


REVIEW_AXES = ('Contract fidelity', 'Scope and simplicity', 'Engineering quality')


def review_markdown(report, work, contract, candidate, base_manifest, destination_observation=None,
                    environment=None, session_id=None, review_scope=None):
    key = candidate_key(candidate)
    if 'changes' in candidate:
        scope = [entry['path'] for entry in candidate['changes']]
    else:
        base = {entry['path']: entry for entry in base_manifest}
        current = {entry['path']: entry for entry in candidate.get('manifest', [])}
        scope = sorted(path for path in base.keys() | current.keys()
                       if base.get(path) != current.get(path))
    included = ', '.join(f'`{path}`' for path in scope) or '(no working-tree changes)'
    lines = [f"# {report['status']}: {work}", '',
             f"Contract: {work}, {contract['revision']}; SHA-256 `{contract['sha256']}`",
             f"Candidate: `{key}`; compact changed-file identity `{work.replace('work/', '.p2p/work/', 1)}/candidate.json`",
             f"Comparison: base `{candidate['comparison_base']}`; included working-tree scope: {included}",
             'Stability: candidate and contract unchanged at report receipt.',
             f"Environment: {environment or 'not recorded'}; session `{session_id or 'unknown'}`.",
             f"Coverage: {report['coverage']}"]
    if destination_observation:
        tip = destination_observation['observed_tip'] or 'unavailable'
        lines.insert(5, f"Destination observation: `{destination_observation['destination']}` {destination_observation['relation']} at `{tip}` ({destination_observation['observed_at']}).")
    coverage = coverage_markdown(report, review_scope)
    if coverage:
        lines.extend(['', coverage])
    for axis in REVIEW_AXES:
        lines.extend(['', '## ' + axis, ''])
        if axis == 'Contract fidelity':
            lines.extend(['Requirement coverage:', ''])
            lines.extend(f"- **{row['id']}**: {row['observation']}" for row in report['requirements'])
            lines.append('')
        findings = [item for item in report['findings'] if item['axis'] == axis]
        if not findings:
            lines.append('No material findings.')
        for item in findings:
            lines.extend([f"- **{item['id']} ({item['source']})** — {item['location']}",
                          f"  Evidence: {item['evidence']}",
                          f"  Consequence: {item['consequence']}",
                          f"  Smallest correction or next check: {item['correction']}",
                          f"  Handoff: `{item['handoff']}`"])
    lines.extend(['', '## Checks and limitations', '', 'Checks:'])
    lines.extend(f"- `{check['command']}` — {check['result']}: {check['observation']}"
                 for check in report['checks'])
    if not report['checks']:
        lines.append('No checks were run.')
    lines.extend(['', 'Limitations:'])
    lines.extend('- ' + item for item in report['limitations'])
    if not report['limitations']:
        lines.append('None.')
    lines.extend(['', 'Gaps:'])
    lines.extend('- ' + item for item in report['gaps'])
    if not report['gaps']:
        lines.append('None.')
    lines.extend(['', learning_candidates_markdown(report), '', '## Handoff', ''])
    if report['status'] == 'BLOCKED':
        lines.extend([f"Missing input or command: {report['missing_input']}",
                      f"Expected result: {report['expected_result']}"])
    elif report['findings']:
        for item in report['findings']:
            lines.append(f"{item['id']} ({item['source']}): `{item['handoff']}`")
    else:
        lines.append('No change handoff is required; acceptance proof remains separate.')
    lines.extend(['', 'Review only; acceptance proof and merge readiness are separate.', '', '## Next steps', ''])
    if report['status'] == 'BLOCKED':
        lines.append(f"1. Resolve `{report['missing_input']}` and establish `{report['expected_result']}`, then resume for a fresh review. Proof and repair remain stopped while review is blocked.")
    elif report['status'] == 'REVIEWED':
        lines.append(f"1. `/prove {work}; candidate {key}`")
    else:
        handoffs = {item['handoff'] for item in report['findings']}
        step = 1
        if 'plan-acceptance' in handoffs:
            lines.append(f"{step}. `/plan-acceptance {work}; amendment {work.replace('work/', '.p2p/work/', 1)}/review.md`; resume implementation only after the revised contract is approved and saved.")
            step += 1
        if 'implement-contract' in handoffs:
            lines.append(f"{step}. `/implement-contract {work}; findings {work.replace('work/', '.p2p/work/', 1)}/review.md`")
            step += 1
        if 'implement-contract' in handoffs:
            lines.append(f"{step}. Capture the changed candidate, then refresh review and full proof.")
    return '\n'.join(lines).rstrip() + '\n'


def proof_markdown(report, work, contract, candidate, environment, session_id):
    lines = [f"# {report['status']}: {work}", '',
             f"Contract: {contract['revision']}; SHA-256 `{contract['sha256']}`",
             f"Candidate: `{candidate_key(candidate)}`",
             f"Comparison base: `{candidate['comparison_base']}`",
             f"Environment: {environment}; session `{session_id or 'unknown'}`", '',
             '## Requirement verdicts', '']
    for row in report['requirements']:
        lines.extend([f"### {row['id']}: {row['verdict']}", '', row['observation'], ''])
        for evidence in row['evidence']:
            lines.extend(['- Assertion: ' + evidence['assertion'],
                          '  Observation: ' + evidence['observation'],
                          '  Artifact: ' + evidence['artifact']])
        lines.append('')
    lines.extend(['## Gaps', ''])
    lines.extend('- ' + item for item in report['gaps'])
    if not report['gaps']:
        lines.append('None.')
    facts = coverage_markdown(report)
    if facts:
        lines.extend(['', facts])
    lines.extend(['', '## Proof details', '', report['details']])
    return '\n'.join(lines).rstrip() + '\n'


def export_checkpoint(root, work, delivery=None, destination=None):
    """Retain stage facts and exact reports, without prompts or command transcripts."""
    if delivery is None:
        local = local_directory(root, work)
        lock_path = local.parent / (local.name + '.lock')
        require_repo_local_ignored(root, lock_path)
        with lock_path.open('a') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise ValueError('stop the controller before exporting a portable checkpoint')
            delivery = Delivery(root, work, json.loads((local / 'delivery.json').read_bytes()))
            delivery.read_only = True
            delivery.current()
            for name in delivery.state['reports']:
                delivery.read_report(name)
            return export_checkpoint(root, work, delivery=delivery, destination=destination)
    if any(a['status'] not in ('complete', 'retired') for a in delivery.state['attempts']):
        raise ValueError('uncertain dispatch prevents a portable checkpoint; reconcile its completion first')
    state = json.loads(json.dumps(delivery.state))
    state.pop('checkpoint', None)
    state.pop('controller_timing', None)
    state['host']['executable'] = 'codex'
    if state.get('restored_host'):
        state['restored_host']['executable'] = 'codex'
    for name, skill in state['skills'].items():
        skill['path'] = 'skill:' + STAGES[name]
    files = []
    def retain(scope, relative, path):
        if path.is_symlink() or not path.is_file():
            raise ValueError('missing or unsafe checkpoint input: ' + str(path))
        files.append((scope, relative, path.read_bytes()))
    for instruction_id in sorted(instruction_ids(state)):
        instructions.load(delivery.runtime, instruction_id)
        retain('runtime', f'instructions/{instruction_id}.json',
               delivery.runtime / 'instructions' / (instruction_id + '.json'))
    for attempt in state['attempts']:
        original = next(a for a in delivery.state['attempts'] if a['id'] == attempt['id'])
        attempt.setdefault('verification_environment', delivery.verification_environment())
        folder = delivery.runtime / 'attempts' / attempt['id']
        end = json.loads((folder / 'exit.json').read_bytes())
        if original['status'] == 'retired':
            if end.get('outcome') not in ('stalled', 'interrupted'):
                raise ValueError('retired stage lacks a confirmed termination receipt')
            existing = folder / 'portable-receipt.json'
            if existing.exists():
                receipt = json.loads(existing.read_bytes())
                if fs.digest(existing.read_bytes()) != original.get('portable_receipt_sha256') or receipt['exit'] != end:
                    raise ValueError('portable termination receipt changed')
            else:
                if fs.digest((folder / 'events.jsonl').read_bytes()) != end.get('event_sha256'):
                    raise ValueError('termination receipt event hash mismatch')
                receipt = {'attempt_id': attempt['id'], 'exit': end, 'host': None}
        else:
            host = delivery.receipt(original)
            executions = []
            for item in host['executions']:
                executions.append({key: item[key] for key in ('id', 'type', 'command', 'exit_code', 'status') if key in item} |
                                  {'output_sha256': item.get('output_sha256') or fs.digest(item.get('aggregated_output', '').encode())})
            receipt = {'attempt_id': attempt['id'], 'exit': end, 'host': host | {'executions': executions}}
        data = encoded(receipt)
        attempt['portable_receipt_sha256'] = fs.digest(data)
        attempt['scratch'] = 'local-scratch'
        files.append(('runtime', f'attempts/{attempt["id"]}/portable-receipt.json', data))
        retain('runtime', f'attempts/{attempt["id"]}/exit.json', folder / 'exit.json')
        if attempt.get('report'):
            retain('runtime', attempt['report'], fs.safe(delivery.runtime, attempt['report']))
    for generation in state['local_git_generations']:
        relative = generation['record_path'].removeprefix('runtime/')
        retain('runtime', relative, fs.safe(delivery.runtime, relative))
    retain('runtime', 'base-tree-key', delivery.runtime / 'base-tree-key')
    for prefix in ('previous-records', 'superseded-records'):
        for path in (delivery.runtime / prefix).rglob('*'):
            if path.is_file():
                retain('runtime', str(path.relative_to(delivery.runtime)), path)
    for name in ('implementation.md', 'repair.md', 'review.md', 'proof.md'):
        path = delivery.local / name
        if path.exists():
            retain('local', name, path)
    for relative in [work, *(row['path'] for row in state['binding_inputs'])]:
        retain('agreement', relative, fs.safe(agreement_root(root, work), relative))
    origin = fs.contract_origin(root, fs.work_slug(work))
    if origin:
        for relative in (f'.p2p/work/{fs.work_slug(work)}/contract-origin.json',
                         f'.p2p/work/{fs.work_slug(work)}/contract.md'):
            retain('agreement', relative, fs.safe(agreement_root(root, work), relative))
    for row in state.get('routing_records', []):
        retain('project', row['path'], fs.safe(root, row['path']))
        # The exact bytes are already in the project checkpoint's reference closure.
        state_row = next(r for r in state['routing_records'] if r['path'] == row['path'])
        state_row.pop('content_base64', None)
    mandate = state.get('autonomy')
    if mandate and mandate.get('path'):
        retain('local', 'mandate.json', Path(mandate['path']))
        mandate['path'] = '@checkpoint/mandate.json'
    for old in state.get('agreement_history', []):
        relative = f'.p2p/work/{fs.work_slug(work)}/history/{old["old_sha256"]}/contract.md'
        retain('project', relative, fs.safe(root, relative))
    candidate_commit = state['local_git_generations'][-1]['commit']
    # Transfer native Git objects locally; the operator must still authorize and
    # publish a reachable work branch before this checkpoint becomes portable.
    fs.git(root, 'fetch', '--no-tags', str(delivery.runtime / 'repository.git'), candidate_commit)
    return fs.checkpoint(root, work, destination, execution=state,
                         candidate_commit=candidate_commit, extra_files=files)


def restore_checkpoint(root, checkpoint, contents, checkpoint_data, *,
                       upgrade_instructions=False, authorize_upgrade=False):
    """Rehost a completed boundary; never reuse the old machine's sandbox preflight."""
    state = json.loads(json.dumps(checkpoint['execution']))
    checkpoint_sha256 = fs.digest(checkpoint_data)
    work = checkpoint['work_item']
    if (state.get('schema') != 'promise-to-proof/delivery/v1' or state.get('work_item') != work or
            state.get('policy') != POLICY or state.get('authority') != {'local_stages': True, 'external_effects': False} or
            any(a.get('status') not in ('complete', 'retired') for a in state['attempts']) or
            state['local_git_generations'][-1]['commit'] != checkpoint['candidate_commit']):
        raise ValueError('invalid or uncertain portable controller boundary')
    if authorize_upgrade and not upgrade_instructions:
        raise ValueError('--authorize-upgrade requires --upgrade-instructions; ordinary restore keeps pinned instructions')
    retained = {}
    for scope, relative, data in contents:
        match = re.fullmatch(r'instructions/([0-9a-f]{64})\.json', relative)
        if scope == 'runtime' and match:
            retained[match[1]] = instructions.decode(data, match[1])
    proposed = None
    if state.get('instruction_identity'):
        if instruction_ids(state) != set(retained):
            raise ValueError('checkpoint instruction inputs are missing; recover the complete original checkpoint')
        active_bundle = retained[state['instruction_identity']]
        expected_stages = {name: row['name'] for name, row in active_bundle['stages'].items()}
        if expected_stages != STAGES:
            raise ValueError('checkpoint instruction stages are incompatible with this controller; keep the original version')
        if upgrade_instructions:
            proposed = instructions.capture(skills(), STAGES)
            instructions.compatible(active_bundle, proposed)
            if proposed['identity'] != active_bundle['identity']:
                if not authorize_upgrade:
                    raise ValueError('instruction adoption requires --authorize-upgrade; '
                                     'omit --upgrade-instructions to restore the pinned version')
                # Validate the exact portable mandate before any restore write.
                # Its receiving-machine path does not exist yet, so verify the
                # checkpoint bytes here and recheck the materialized file below.
                authority_state = json.loads(json.dumps(state))
                mandate = authority_state.get('autonomy')
                if mandate and mandate.get('path'):
                    data = next((data for scope, relative, data in contents
                                 if scope == 'local' and relative == 'mandate.json'), None)
                    if (mandate['path'] != '@checkpoint/mandate.json' or data is None or
                            fs.digest(data) != mandate['sha256'] or json.loads(data) != mandate['policy']):
                        raise ValueError('checkpoint instruction upgrade lacks its exact mandate; restore that authority input')
                    mandate['path'] = None
                instruction_upgrade_authority(authority_state)
    else:
        if upgrade_instructions:
            raise ValueError('legacy checkpoint has no complete pinned instruction inputs; '
                             'restore with the original skill installation and resume without --upgrade-instructions')
        installed = skills()
        if {name: skill['sha256'] for name, skill in installed.items()} != {name: skill['sha256'] for name, skill in state['skills'].items()}:
            raise ValueError('installed stage skills differ from this legacy checkpoint; restore its original skill installation')
    if platform.system() != 'Darwin' or not shutil.which('codex'):
        raise ValueError('portable delivery restore requires the supported macOS Codex host')
    fs.check_index(root)
    if fs.snapshot_key(fs.snapshot(root)) != state['source_tree_key']:
        raise ValueError('receiving source checkout differs from the checkpoint admission; preserve local work')
    candidate = fs.snapshot(root, checkpoint['candidate_commit'])
    if (fs.snapshot_key(candidate) != state['candidate']['key'] or
            fs.tree_changes(fs.snapshot(root, state['comparison_base'], exclude=state.get('agreement_paths', ())), candidate) != state['candidate']['changes']):
        raise ValueError('portable candidate commit differs from its exact snapshot identity')
    local = fs.safe(root, f'.p2p/work/{fs.work_slug(work)}')
    runtime = fs.execution_directory(root, work) / 'runtime'
    if (runtime.exists() or (local / 'delivery.json').exists() or
            (local / 'runtime').exists()):
        raise ValueError('existing execution conflicts with checkpoint restore; preserve and reconcile it')
    targets = {}
    for scope, relative, data in contents:
        base = {'project': root, 'local': local, 'runtime': runtime,
                'agreement': runtime.parent / 'agreement'}[scope]
        target = fs.safe(base, relative)
        if target in targets and targets[target] != data:
            raise ValueError('conflicting checkpoint file destinations')
        if target.exists() and (not target.is_file() or target.read_bytes() != data):
            raise ValueError('checkpoint conflicts with local file: ' + str(target))
        targets[target] = data
    checkpoint_path, _ = fs.checkpoint_path(root, work, checkpoint['destination'])
    if checkpoint_path.exists() and fs.digest(checkpoint_path.read_bytes()) != checkpoint_sha256:
        raise ValueError('selected checkpoint conflicts with the restore source')
    if not state.get('instruction_identity'):
        state['skills'] = installed
    state['host']['executable'] = shutil.which('codex')
    version = subprocess.run([state['host']['executable'], '--version'], capture_output=True, text=True,
                             timeout=10, check=True).stdout.strip()
    state['restored_host'] = state['host'] | {'version': version}
    state['source_head'] = fs.full_commit(root, 'HEAD')
    state['source_index_sha256'] = fs.digest(fs.git(root, 'ls-files', '--stage', '-z'))
    state['source_product_index_sha256'] = fs.product_index_sha256(root)
    state['checkpoint_restored_from'] = checkpoint_sha256
    state.pop('checkpoint', None)
    for name in ('cleanup_verified_at', 'cleanup_source_identity_sha256', 'final_records_written', 'cleanup'):
        state.pop(name, None)
    for attempt in state['attempts']:
        attempt['scratch'] = str(runtime / 'scratch' / attempt['id'])
        if attempt['stage'].startswith('preflight-'):
            attempt['stage'] = 'prior-' + attempt['stage']
    state['preflight_complete'] = False
    if state.get('autonomy') and state['autonomy'].get('path'):
        if state['autonomy']['path'] != '@checkpoint/mandate.json':
            raise ValueError('checkpoint mandate location is not portable')
        state['autonomy']['path'] = str(local / 'mandate.json')
    # Routing records are exact project files. Restore their existing transfer
    # representation without changing the hashes used by completed stage inputs.
    for row in state.get('routing_records', []):
        file = fs.safe(root, row['path'])
        content = targets.get(file, file.read_bytes() if file.is_file() else None)
        if content is None or fs.digest(content) != row['sha256']:
            raise ValueError('checkpoint routing evidence is missing or changed')
        row['content_base64'] = base64.b64encode(content).decode()
    if any(scope == 'runtime' and relative == 'admission.json' for scope, relative, _ in contents):
        raise ValueError('checkpoint must not import a machine-specific admission')
    for file, data in targets.items():
        file.parent.mkdir(parents=True, exist_ok=True)
        if not file.exists():
            ignored = not file.is_relative_to(root) or file.is_relative_to(root / '.p2p')
            fs.atomic_write(file, data, ignored_root=root if ignored else None)
    if not checkpoint_path.exists():
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        fs.atomic_write(checkpoint_path, checkpoint_data,
                        ignored_root=root if checkpoint['destination']['kind'] == 'github' else None)
    fs.prepare_execution(root, work)
    for instruction_id, instruction_bundle in retained.items():
        mapping = instructions.preserve(runtime, instruction_bundle)
        if instruction_id == state['instruction_identity']:
            state['skills'] = mapping
    repository = runtime / 'repository.git'
    subprocess.run(['git', 'init', '--bare', '--quiet', str(repository)], check=True)
    for commit in (state['comparison_base'], checkpoint['candidate_commit']):
        fs.git(repository, 'fetch', '--no-tags', str(root), commit)
    for row in [state['local_git_base'], *state['local_git_generations']]:
        fs.git(repository, 'update-ref', row['ref'], row.get('commit', row.get('local_commit')))
    workspace = runtime / 'workspace'
    materialize(workspace, candidate, ignored_root=root)
    materialize(workspace, [{'path': row['path'], 'type': 'file', 'mode': '100644', 'content_base64': row['content_base64']}
                            for row in state.get('routing_records', [])], ignored_root=root)
    for scope, relative, data in contents:
        if scope == 'agreement':
            file = fs.safe(workspace, relative)
            file.parent.mkdir(parents=True, exist_ok=True)
            fs.atomic_write(file, data)
    (workspace / '.git').write_text('gitdir: ' + str(repository) + '\n')
    fs.git(workspace, 'config', '--local', 'core.bare', 'false')
    fs.git(workspace, 'update-ref', '--no-deref', 'HEAD', state['starting_commit'])
    fs.git(workspace, 'read-tree', state['starting_commit'])
    fs.save(workspace, work, 'candidate.json', encoded(state['candidate']))
    delivery = Delivery(root, work, state)
    keys = ('policy', 'invocation_id', 'work_item', 'comparison_base', 'contract', 'binding_inputs', 'source_tree_key',
            'source_head', 'source_index_sha256', 'source_product_index_sha256', 'excluded_dirty', 'agreement_paths', 'skills', 'routing', 'routing_records',
            'starting_commit', 'base_tree_key', 'local_git_base', 'previous_records', 'authority', 'autonomy', 'limits',
            'deadline', 'started_at', 'started_epoch', 'deadline_started_epoch', 'host')
    if state.get('instruction_identity'):
        keys += ('instruction_identity',)
    local_save(root, work, 'runtime/admission.json', encoded({key: state[key] for key in keys}))
    delivery.save()
    delivery.read_only = True
    delivery.current()
    for name in state['reports']:
        delivery.read_report(name)
    upgrade_result = None
    if proposed is not None:
        delivery.read_only = False
        upgrade_result = delivery.upgrade_instructions(authorize_upgrade, new_bundle=proposed)
    return {'status': 'RESTORED', 'work_item': work, 'checkpoint_sha256': checkpoint_sha256,
            'instruction_identity': delivery.state.get('instruction_identity'),
            'instruction_upgrade': upgrade_result,
            'resume': f'python3 {Path(__file__).resolve()} --repo {root} resume {work}',
            'next_action': 'Resume at the incomplete stage; the receiving host must pass fresh sandbox preflight.'}


class Delivery:
    def __init__(self, root, work, state):
        self.root, self.work, self.state = root, work, state
        self.read_only = False
        self.item, self.directory = delivery_paths(root, work)
        self.local = local_directory(root, work)
        self.runtime = execution_runtime(root, work)
        self.workspace = self.runtime / 'workspace'
        self._generation_chain_verified = False

    def save(self):
        if self.state.get('status') == 'REVIEWED_AND_PROVEN' and self.state.get('completed_at'):
            local_save(self.root, self.work, 'delivery.json', encoded(self.state))
            return
        started = time.monotonic()
        local_save(self.root, self.work, 'delivery.json', encoded(self.state))
        self._record_controller_time('persistence_readback', started)

    def checkpoint(self):
        try:
            value = export_checkpoint(self.root, self.work, delivery=self)
        except (ValueError, OSError, KeyError, TypeError, UnicodeError) as error:
            value = {'status': 'BLOCKED', 'blocker': str(error)}
        self.state['checkpoint'] = value
        local_save(self.root, self.work, 'delivery.json', encoded(self.state))
        return value

    def _record_controller_time(self, name, started):
        timings = self.state.setdefault('controller_timing', {})
        timings[name] = timings.get(name, 0) + time.monotonic() - started

    def verify_superseded_recovery(self):
        for name, expected in self.state.get('superseded_artifacts', {}).items():
            path = self.runtime / 'superseded-records' / name
            try:
                actual = fs.digest(path.read_bytes())
            except OSError as error:
                raise ValueError('missing local recovery input: runtime/superseded-records/' + name) from error
            if actual != expected:
                raise ValueError('retained superseded artifact changed or lost: ' + name)

    def verification_environment(self):
        host = self.state.get('restored_host') or self.state['host']
        return f"{host['name']} {host['version']}; policy {self.state['policy']}; enforced: {', '.join(host['enforced'])}"

    def source_stable(self):
        try:
            admission = json.loads((self.runtime / 'admission.json').read_text())
        except OSError as error:
            raise ValueError('missing local recovery input: runtime/admission.json') from error
        for key, value in admission.items():
            if self.state.get(key) != value:
                raise ValueError('persisted admission changed: ' + key)
        if self.state.get('autonomy'):
            autonomy.current(self.state['autonomy'])
        admitted_route = self.state['routing']
        selection = admitted_route.get('selection')
        explicit = (admitted_route['target_ref']
                    if selection == 'explicit' or (selection is None and not admitted_route.get('path'))
                    else None)
        active_route = routing(self.root, self.work, explicit, require_tip=False)
        validate_sidecar_plan(self.root, active_route, self.work)
        validate_sidecar_plan(self.workspace, admitted_route, self.work)
        if route_identity(active_route) != route_identity(admitted_route):
            raise ValueError('approved delivery plan or destination changed; reconcile routing before resume')
        if admitted_route.get('path') and route_identity(
                routing(self.workspace, self.work, admitted_route['target_ref'], require_tip=False)) != route_identity(admitted_route):
            raise ValueError('transferred approved delivery plan changed')
        for record in self.state.get('routing_records', []):
            if self.state['routing'].get('path') and record['path'] == self.state['routing']['path']:
                continue  # Pending proposals may change outside the approved section.
            for root in (self.root, self.workspace):
                if fs.digest(fs.safe(root, record['path']).read_bytes()) != record['sha256']:
                    raise ValueError('retained routing history/evidence changed: ' + record['path'])
        current = fs.snapshot(self.root)
        current_key = fs.snapshot_key(current)
        # The complete source snapshot already contains the product subset.
        # Filtering these exact bytes removes a redundant checkout scan while
        # preserving records-only vs product-change classification.
        applied_key = self.state.get('candidate', {}).get('key')
        candidate_applied = (self.state.get('status') == 'REVIEWED_AND_PROVEN' and
                             fs.snapshot_key([row for row in current
                                              if row['path'] not in self.state.get('agreement_paths', ())]) == applied_key)
        if current_key != self.state['source_tree_key'] and not candidate_applied:
            raise ValueError('source checkout changed since admission')
        if (self.workspace / '.git').read_text() != 'gitdir: ' + str(self.runtime / 'repository.git') + '\n':
            raise ValueError('isolated Git metadata pointer changed')
        head = fs.full_commit(self.root, 'HEAD')
        index = fs.digest(fs.git(self.root, 'ls-files', '--stage', '-z'))
        # Inspect committed HEAD and staged product identity only when a
        # checkout metadata change makes this distinction relevant. A normal
        # cold delivery still checks the live full source snapshot above.
        if head != self.state['source_head'] or index != self.state['source_index_sha256']:
            head_key = fs.snapshot_key(fs.snapshot(self.root, head))
            metadata_only = (self.state.get('source_product_index_sha256') ==
                             fs.product_index_sha256(self.root) and
                             head_key == self.state['source_tree_key'] and
                             current_key == self.state['source_tree_key'])
            if not metadata_only:
                committed_candidate = candidate_applied and head_key == applied_key
                staged_product = subprocess.run(['git', '-C', str(self.root), 'diff',
                                                 '--cached', '--quiet', '--',
                                                 ':(exclude).p2p', ':(exclude)p2p-state']).returncode
                if not committed_candidate or staged_product:
                    raise ValueError('source HEAD or index changed since admission')
        if fs.full_commit(self.workspace, self.state['comparison_base']) != self.state['comparison_base']:
            raise ValueError('comparison base unavailable')
        base_key = fs.snapshot_key(fs.snapshot(self.workspace, self.state['comparison_base']))
        try:
            retained_base_key = (self.runtime / 'base-tree-key').read_text()
        except OSError as error:
            raise ValueError('missing local recovery input: runtime/base-tree-key') from error
        if retained_base_key != base_key + '\n' or base_key != self.state['base_tree_key']:
            raise ValueError('retained comparison-base identity changed or lost')
        for name, expected in self.state.get('previous_records', {}).items():
            path = self.runtime / 'previous-records' / name
            try:
                actual = fs.digest(path.read_bytes())
            except OSError as error:
                raise ValueError('missing local recovery input: runtime/previous-records/' + name) from error
            if actual != expected:
                raise ValueError('retained prior delivery record changed or lost: ' + name)
        self.verify_superseded_recovery()
        if agreement_bindings(self.root, self.work) != self.state['binding_inputs']:
            raise ValueError('binding inputs changed')
        source_item, _ = fs.paths(self.root, self.work)
        if source_item.is_file() and fs.digest(source_item.read_bytes()) != self.state['contract']['sha256']:
            raise ValueError('work item changed')
        if fs.digest(self.item.read_bytes()) != self.state['contract']['sha256']:
            raise ValueError('work item changed')
        if self.state['authority'] != {'local_stages': True, 'external_effects': False} or self.state['policy'] != POLICY:
            raise ValueError('persisted authority or policy changed')
        if self.state.get('instruction_identity'):
            if instructions.validate(self.runtime, self.state['instruction_identity']) != self.state['skills']:
                raise ValueError('pinned stage instruction locations changed; restore the exact retained instruction bundle')
            for old_identity in instruction_ids(self.state) - {self.state['instruction_identity']}:
                instructions.load(self.runtime, old_identity)
        elif skills() != self.state['skills']:
            raise ValueError('installed stage skills changed; this legacy delivery has no complete pinned instructions; '
                             'restore its original skill installation and resume the same work item')
        self.state['destination_observation'] = destination_observation(
            self.root, active_route, self.state['comparison_base'])
        if not self.read_only:
            self.save()

    def timed_source_stable(self):
        started = time.monotonic()
        try:
            self.source_stable()
        finally:
            self._record_controller_time('identity_snapshot_validation', started)

    def capture(self, stage='implementation'):
        if stage == 'live-evaluation' and not self.state.get('live_evaluation'):
            raise ValueError('fixture candidate admission is not enabled in this delivery')
        started = time.monotonic()
        try:
            return self._capture(stage)
        finally:
            self._record_controller_time('identity_snapshot_validation', started)

    def _capture(self, stage='implementation'):
        if fs.digest((self.workspace / self.work).read_bytes()) != self.state['contract']['sha256']:
            raise ValueError('implementation changed the approved agreement')
        if fs.bindings(self.workspace, self.work) != self.state['binding_inputs']:
            raise ValueError('implementation changed binding inputs')
        excluded = self.state['excluded_dirty']
        base_entries = fs.snapshot(self.workspace, self.state['comparison_base'])
        actual_entries = fs.snapshot(self.workspace)
        base = {e['path']: e for e in base_entries}
        actual = {e['path']: e for e in actual_entries}
        changed = [p for p in excluded if actual.get(p) != base.get(p)]
        changed = [p for p in changed if p not in self.state.get('agreement_paths', ())]
        if changed:
            raise ValueError('implementation changed excluded scope paths: ' + ', '.join(changed))
        agreement_paths = set(self.state.get('agreement_paths', ()))
        candidate_entries = [entry for entry in actual_entries if entry['path'] not in agreement_paths]
        base_candidate_entries = [entry for entry in base_entries if entry['path'] not in agreement_paths]
        candidate = fs.capture(self.workspace, self.work, self.state['comparison_base'],
                               exclude=agreement_paths,
                               prepared=(candidate_entries, base_candidate_entries))
        self.state['candidate'] = candidate
        generation = record_generation(self, candidate, stage, manifest=candidate_entries)
        if stage == 'implementation' and self.state.get('implementation_slice_version') == 1:
            source = generation.get('source_attempt') or {}
            attempt = next((item for item in self.state['attempts']
                            if item['id'] == source.get('attempt_id')), None)
            if not attempt or not attempt.get('report'):
                raise ValueError('slice capture has no saved confirmed implementation report')
            data = fs.safe(self.runtime, attempt['report']).read_bytes()
            if fs.digest(data) != attempt['report_sha256']:
                raise ValueError('slice capture report differs from authenticated attempt')
            if attempt.get('report_validation') != 'rejected':
                slices.attach(self.state, attempt, json.loads(data), generation)
        self._generation_chain_verified = False
        return candidate

    def verify_generation_chain(self):
        if self._generation_chain_verified:
            return
        base = self.state.get('local_git_base')
        if not isinstance(base, dict) or base.get('source_commit') != self.state['comparison_base']:
            raise ValueError('missing or conflicting local Git comparison-base mapping')
        repository = self.runtime / 'repository.git'
        try:
            if (fs.full_commit(repository, base['source_commit']) != base['source_commit'] or
                    fs.git(repository, 'rev-parse', base['source_commit'] + '^{tree}').decode().strip() != base['source_tree']):
                raise ValueError('source comparison-base commit mapping changed')
            if fs.full_commit(repository, base['local_commit']) != base['local_commit']:
                raise ValueError('local Git comparison-base commit is missing')
            if fs.git(repository, 'rev-parse', base['local_commit'] + '^{tree}').decode().strip() != base['tree']:
                raise ValueError('local Git comparison-base tree mapping changed')
            if fs.git(repository, 'rev-parse', base['ref']).decode().strip() != base['local_commit']:
                raise ValueError('local Git comparison-base ref changed or is missing')
            source_base_snapshot = fs.snapshot(repository, base['source_commit'])
            if fs.snapshot_key(source_base_snapshot) != self.state['base_tree_key']:
                raise ValueError('source comparison-base content no longer matches its product identity')
            base_snapshot = fs.snapshot(repository, base['local_commit'])
        except (ValueError, OSError) as error:
            raise ValueError('missing or corrupt local Git comparison base: ' + str(error)) from error
        if (fs.snapshot_key(base_snapshot) != self.state['base_tree_key'] or
                base.get('tree_key') != self.state['base_tree_key']):
            raise ValueError('local Git comparison base does not match the frozen source base')
        generations = self.state.get('local_git_generations')
        if not isinstance(generations, list) or not generations:
            raise ValueError('missing local Git candidate generation history')
        parent = base['local_commit']
        previous_key = None
        for sequence, summary in enumerate(generations, 1):
            path = summary.get('record_path', '')
            try:
                data = fs.safe(self.runtime, path.removeprefix('runtime/')).read_bytes()
                record = json.loads(data)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                raise ValueError('missing or corrupt local Git generation record: ' + (path or str(sequence))) from error
            if (fs.digest(data) != summary.get('record_sha256') or record != {k: v for k, v in summary.items()
                                                                              if k not in ('record_path', 'record_sha256')} or
                    record.get('sequence') != sequence or record.get('work_item') != self.work or
                    record.get('repository_id') != base.get('repository_id') or
                    record.get('invocation_id') != self.state['invocation_id'] or
                    record.get('comparison_base') != self.state['comparison_base'] or
                    record.get('base_tree') != base['tree'] or
                    record.get('contract_sha256') not in ({self.state['contract']['sha256']} |
                        {entry['old_sha256'] for entry in self.state.get('agreement_history', [])}) or
                    record.get('parent_commit') != parent or
                    record.get('previous_candidate_key') != previous_key or
                    record.get('stage') not in ('admission', 'implementation', 'repair', 'planning-audit', 'live-evaluation') or
                    (sequence == 1) != (record.get('stage') == 'admission')):
                raise ValueError('local Git generation mapping changed: ' + path)
            source_attempt = record.get('source_attempt')
            if sequence == 1:
                if source_attempt is not None:
                    raise ValueError('admission generation unexpectedly names a stage attempt')
            elif record['stage'] == 'live-evaluation':
                # The trusted live suite admits fixed candidates; there was no implementation worker.
                # This path is deliberately unavailable to ordinary deliveries.
                if not self.state.get('live_evaluation') or source_attempt is not None:
                    raise ValueError('live evaluation generation has no admitted fixture provenance')
            else:
                attempt = next((item for item in self.state['attempts']
                                if item['id'] == (source_attempt or {}).get('attempt_id')), None)
                prior = generations[sequence - 2]
                expected_input = (attempt or {}).get('inputs', {}).get('local_git_generation', {})
                if (attempt is None or attempt.get('stage') != record['stage'] or
                        attempt.get('status') not in ('complete', 'retired') or
                        attempt.get('report_sha256') != source_attempt.get('report_sha256') or
                        source_attempt.get('inputs') != attempt.get('inputs') or
                        expected_input.get('commit') != prior.get('commit') or
                        record.get('previous_candidate_key') != prior.get('candidate_key')):
                    raise ValueError('local Git generation does not map to its completed stage attempt')
                if attempt['status'] == 'retired':
                    folder = self.runtime / 'attempts' / attempt['id']
                    end = json.loads((folder / 'exit.json').read_bytes())
                    portable = folder / 'portable-receipt.json'
                    if portable.exists():
                        data = portable.read_bytes()
                        receipt = json.loads(data)
                        if fs.digest(data) != attempt.get('portable_receipt_sha256') or receipt.get('exit') != end:
                            raise ValueError('portable worker termination receipt changed')
                        event_sha256 = end.get('event_sha256')
                    else:
                        event_sha256 = fs.digest((folder / 'events.jsonl').read_bytes())
                    if (end.get('attempt_id') != attempt['id'] or end.get('inputs') != attempt['inputs'] or
                            end.get('outcome') not in ('stalled', 'interrupted') or
                            end.get('event_sha256') != event_sha256):
                        raise ValueError('retired worker generation has no confirmed exit receipt')
            try:
                commit = fs.full_commit(repository, record['commit'])
                tree = fs.git(repository, 'rev-parse', commit + '^{tree}').decode().strip()
                if commit != record['commit'] or tree != record['tree']:
                    raise ValueError('generation commit/tree identity mismatch')
                manifest = fs.snapshot(repository, commit)
            except (ValueError, OSError, KeyError) as error:
                raise ValueError('missing or corrupt local Git generation object: ' + str(record.get('commit'))) from error
            if (fs.snapshot_key(manifest) != record['candidate_key'] or
                    fs.tree_changes(base_snapshot, manifest) != record['changes']):
                raise ValueError('local Git generation content does not match its exact candidate identity')
            if fs.git(repository, 'rev-parse', record['ref']).decode().strip() != commit:
                raise ValueError('local Git generation ref changed or is missing: ' + record['ref'])
            parent = commit
            previous_key = record['candidate_key']
        if generations[-1]['candidate_key'] != self.state.get('candidate', {}).get('key'):
            raise ValueError('local Git history does not map to the retained candidate')
        self._generation_chain_verified = True

    def current(self, check_source=True):
        started = time.monotonic()
        try:
            return self._current(check_source)
        finally:
            self._record_controller_time('identity_snapshot_validation', started)

    def _current(self, check_source=True):
        if check_source:
            self.source_stable()
        expected = self.state.get('candidate')
        if expected:
            self.verify_generation_chain()
            actual = fs.validate(self.workspace, self.work, self.state['comparison_base'],
                                 exclude=self.state.get('agreement_paths', ()))
            saved = json.loads((self.workspace / '.p2p/work' / fs.work_slug(self.work) / 'candidate.json').read_text())
            if actual != expected or saved != expected:
                raise ValueError('retained candidate identity changed')
        return expected

    def reserve(self, stage, inputs, scratch):
        self.timed_source_stable()
        limits = self.state['limits']
        if limits['dispatches'] is not None and len(self.state['attempts']) >= limits['dispatches']:
            raise ValueError('dispatch-count limit exhausted before ' + stage)
        if self.state['deadline'] is not None and time.time() >= self.state['deadline']:
            raise ValueError('elapsed-time limit exhausted before ' + stage)
        if limits.get('stage_seconds') == 0:
            raise ValueError('stage elapsed-time limit exhausted before ' + stage)
        if stage == 'repair':
            used = sum(a['stage'] == 'repair' for a in self.state['attempts'])
            allowed = limits.get('repairs', 1)  # Existing admissions retain their one-repair policy.
            if allowed is not None and used >= allowed:
                raise ValueError('automatic repair limit exhausted')
            self.state['repair_used'] = True
        attempt = {'id': str(uuid.uuid4()), 'stage': stage, 'inputs': inputs,
                   'status': 'reserved', 'started': now(), 'started_epoch': time.time(),
                   'finished': None, 'elapsed_seconds': 'unknown', 'usage': 'unknown',
                   'cost': 'unknown', 'scratch': str(scratch), 'session_id': None}
        deadlines = [self.state['deadline']]
        if limits.get('stage_seconds') is not None:
            deadlines.append(attempt['started_epoch'] + limits['stage_seconds'])
        attempt['deadline'] = min((value for value in deadlines if value is not None), default=None)
        self.state['attempts'].append(attempt)
        self.save()  # Admission and repair consumption precede any subprocess.
        return attempt

    def receipt(self, attempt):
        folder = self.runtime / 'attempts' / attempt['id']
        path = folder / 'exit.json'
        if not path.exists():
            raise ValueError('uncertain dispatch ' + attempt['id'] + ': missing controller host completion ' + str(path))
        end = json.loads(path.read_text())
        if end.get('attempt_id') != attempt['id'] or end.get('inputs') != attempt['inputs']:
            raise ValueError('late or conflicting host receipt: ' + attempt['id'])
        portable = folder / 'portable-receipt.json'
        if portable.exists():
            data = portable.read_bytes()
            record = json.loads(data)
            if (fs.digest(data) != attempt.get('portable_receipt_sha256') or
                    record.get('exit') != end or record.get('attempt_id') != attempt['id']):
                raise ValueError('portable host receipt changed: ' + attempt['id'])
            host = record['host']
        else:
            if end.get('event_sha256') != fs.digest((folder / 'events.jsonl').read_bytes()):
                raise ValueError('host event content changed: ' + attempt['id'])
            host = None
        attempt.update({k: end[k] for k in ('exit_code', 'outcome', 'finished', 'elapsed_seconds')})
        attempt['launch_started'] = end.get('launch_started')
        attempt['launch_finished'] = end.get('launch_finished')
        if end['outcome'] == 'interrupted':
            attempt['status'] = 'failed'
            if not self.read_only:
                self.save()
            raise ValueError(f'{attempt["stage"]} elapsed-time limit exhausted; host interrupted: {attempt["id"]}')
        try:
            host = host if host is not None else host_events(folder / 'events.jsonl')
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
        # Planning can stop between a saved proposal and its independent audit.
        # Reuse that exact completed response before reconciling a later reservation.
        if stage in ('planning', 'planning-audit'):
            completed = next((a for a in reversed(self.state['attempts'])
                              if a['stage'] == stage and a['inputs'] == inputs and
                              a['status'] == 'complete'), None)
            if completed:
                self.check_report_rejection(completed)
                return completed, self.receipt(completed)
        pending = [a for a in self.state['attempts'] if a['status'] in ('reserved', 'failed')]
        if pending:
            attempt = pending[-1]
            if attempt['stage'] != stage or attempt['inputs'] != inputs:
                raise ValueError('reserved stage inputs differ; uncertain dispatch: ' + attempt['id'])
            self.state['reconciliation_count'] = self.state.get('reconciliation_count', 0) + 1
            self.save()
            return attempt, self.receipt(attempt)
        scratch = writable or (self.runtime / 'scratch' / str(uuid.uuid4()))
        require_repo_local_ignored(self.root, scratch)
        scratch.mkdir(parents=True, exist_ok=True)
        require_repo_local_ignored(self.root, scratch / '.p2p/tmp')
        (scratch / '.p2p/tmp').mkdir(parents=True, exist_ok=True)
        attempt = self.reserve(stage, inputs, scratch)
        folder = self.runtime / 'attempts' / attempt['id']
        require_repo_local_ignored(self.root, folder)
        folder.mkdir(parents=True)
        if schema:
            local_save(self.root, self.work, f'attempts/{attempt["id"]}/schema.json', encoded(schema))
        args = command(self.state['host']['executable'], scratch, folder / 'schema.json' if schema else None)
        if attempt['deadline'] is not None:
            prompt += (f' Effective host deadline: Unix timestamp {attempt["deadline"]}; '
                       f'{max(0, attempt["deadline"] - time.time()):.1f} seconds remain. '
                       'Return an honest incomplete report with remaining gaps before this deadline '
                       'if the required work cannot finish. Do not weaken coverage or claim unverified success.')
        local_save(self.root, self.work, f'attempts/{attempt["id"]}/launch.json', encoded({
            'attempt_id': attempt['id'], 'stage': stage, 'inputs': inputs, 'command': args, 'prompt': prompt,
            'configuration': host_config(scratch), 'model_provenance': 'inherited configured preference'}))
        print(f'{stage} started [{attempt["id"]}]; deadline {attempt["deadline"]}', file=sys.stderr, flush=True)
        try:
            require_repo_local_ignored(self.root, folder / 'events.jsonl')
            require_repo_local_ignored(self.root, folder / 'stderr.txt')
            options = ([self.state['limits']['worker_idle_seconds']]
                       if self.state['limits'].get('worker_idle_seconds') is not None else [])
            result = launch(args, prompt, folder / 'events.jsonl', folder / 'stderr.txt', attempt['deadline'], *options)
            result.update(attempt_id=attempt['id'], inputs=inputs,
                          event_sha256=fs.digest((folder / 'events.jsonl').read_bytes()))
            local_save(self.root, self.work, f'attempts/{attempt["id"]}/exit.json', encoded(result))
            print(f'{stage} {result["outcome"]} [{attempt["id"]}]; '
                  f'{result["elapsed_seconds"]:.1f}s elapsed; exit {result["exit_code"]}', file=sys.stderr, flush=True)
        except BaseException:
            # No retry: a saved reservation with no exit receipt is intentionally uncertain.
            print(f'{stage} stopped [{attempt["id"]}]; completion receipt unavailable', file=sys.stderr, flush=True)
            raise
        if result['outcome'] == 'stalled' and self.state.get('autonomy'):
            self.reconcile_worker()
            raise WorkerRestartRequired()
        return attempt, self.receipt(attempt)

    def check_report_rejection(self, attempt):
        if attempt.get('report_validation') != 'rejected':
            return
        host = self.receipt(attempt)
        data = (self.runtime / attempt['report']).read_bytes()
        if fs.digest(data) != attempt['report_sha256'] or data != host['message'].encode():
            raise ValueError('rejected stage report changed: ' + attempt['id'])
        raise ValueError(attempt['stage'] + ' returned an invalid report: ' + attempt['report_error'] +
                         '; exact response retained at ' + str(self.runtime / attempt['report']))

    @contextmanager
    def report_validation(self, attempt, host):
        """A confirmed response can fail validation without becoming an uncertain launch."""
        try:
            yield
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            data = host['message'].encode()
            path = f'attempts/{attempt["id"]}/report.json'
            stored = self.runtime / path
            if stored.exists() and stored.read_bytes() != data:
                raise ValueError('conflicting rejected stage result: ' + attempt['id']) from error
            local_save(self.root, self.work, path, data)
            attempt.update(status='complete', report=path, report_sha256=fs.digest(data),
                           report_validation='rejected', report_error=str(error),
                           report_format_error=isinstance(error, ReportFormatError))
            self.save()
            # Capturing preserves the returned product bytes; it does not accept the
            # invalid report, mark implementation complete, or authorize verification.
            if attempt['stage'] in ('implementation', 'repair'):
                self.capture(attempt['stage'])
                self.save()
            if isinstance(error, ReportFormatError):
                raise
            raise ValueError(attempt['stage'] + ' returned an invalid report: ' + str(error) +
                             '; exact response retained at ' + str(stored)) from error
        else:
            attempt['report_validation'] = 'accepted'

    def preflight(self):
        # Product edits do not invalidate a successfully observed host prerequisite.
        # Keep the inspected candidate in the attempt identity, but reuse readiness
        # by agreement, binding inputs and the actual admitted/receiving host.
        readiness = {'contract_sha256': self.state['contract']['sha256'],
                     'binding_inputs': self.state['binding_inputs'],
                     'host': self.state.get('restored_host') or self.state['host'],
                     'policy': self.state['policy'], 'skills': self.state['skills']}
        fields = {key: {'type': 'string'} for key in
                  ('status', 'input_identity_json', 'reason', 'missing_input', 'expected_result')}
        fields['status']['enum'] = ['READY', 'BLOCKED']
        check_fields = {key: {'type': 'string'} for key in
                        ('kind', 'prerequisite', 'requirement_id', 'command', 'observation')}
        check_fields['kind']['enum'] = ['tool', 'input', 'runtime', 'service']
        check_fields['available'] = {'type': 'boolean'}
        fields['checks'] = {'type': 'array', 'maxItems': 12, 'items': {
            'type': 'object', 'properties': check_fields, 'required': list(check_fields),
            'additionalProperties': False}}
        schema = {'type': 'object', 'properties': fields, 'required': list(fields),
                  'additionalProperties': False}

        def same_command(recorded, reported):
            if not isinstance(recorded, str):
                return False
            if recorded == reported:
                return True
            # Codex may record its shell wrapper instead of the submitted command.
            # Accept only the exact body of that wrapper, never a substring match.
            try:
                parts = shlex.split(recorded)
            except (ValueError, TypeError):
                return False
            return (len(parts) == 3 and Path(parts[0]).name in ('sh', 'bash', 'zsh', 'dash') and
                    parts[1] in ('-c', '-lc', '-ic', '-lic') and parts[2] == reported)

        def validate_readiness(attempt, host):
            report = json.loads(host['message'])
            if (not isinstance(report, dict) or set(report) != set(fields) or
                    any(not isinstance(report[key], str) for key in fields if key != 'checks') or
                    report['status'] not in ('READY', 'BLOCKED') or not report['reason'].strip() or
                    json.loads(report['input_identity_json']) != attempt['inputs'] or
                    not isinstance(report['checks'], list) or len(report['checks']) > 12):
                raise ValueError('invalid or stale task-readiness report')
            unavailable = []
            for check in report['checks']:
                if (not isinstance(check, dict) or set(check) != set(check_fields) or
                        any(not isinstance(check[key], str) or not check[key].strip()
                            for key in check_fields if key != 'available') or
                        type(check['available']) is not bool or
                        check['kind'] not in check_fields['kind']['enum'] or
                        check['requirement_id'] not in self.state['requirements']):
                    raise ValueError('invalid task-readiness prerequisite')
                evidence = [event for event in host['executions']
                            if same_command(event.get('command'), check['command']) and
                            check['observation'] in event.get('aggregated_output', '') and
                            isinstance(event.get('exit_code'), int)]
                if not evidence or (check['available'] and not any(event['exit_code'] == 0 for event in evidence)):
                    raise ValueError('task readiness lacks host-recorded command evidence: ' + check['prerequisite'])
                if not check['available']:
                    unavailable.append(check['prerequisite'])
            if report['status'] == 'READY':
                if unavailable or report['missing_input'] or report['expected_result']:
                    raise ValueError('READY task readiness contains an unmet prerequisite')
            elif (not unavailable or report['missing_input'] not in unavailable or
                  not report['expected_result'].strip()):
                raise ValueError('BLOCKED task readiness needs an observed missing prerequisite and next result')
            return report

        for index in range(2):
            stage = 'preflight-' + str(index + 1)
            done = next((a for a in reversed(self.state['attempts'])
                         if a['stage'] == stage and a['status'] == 'complete'), None)
            if done:
                self.check_report_rejection(done)
                host = self.receipt(done)
                if index == 0:
                    continue
                # An instruction upgrade preserves the agreement and host. It does
                # not by itself invalidate observed tools, inputs or sandbox access.
                saved_readiness = done['inputs'].get('task_readiness', {})
                if ({k: v for k, v in saved_readiness.items() if k != 'skills'} ==
                        {k: v for k, v in readiness.items() if k != 'skills'} and done.get('report')):
                    data = (self.runtime / done['report']).read_bytes()
                    if fs.digest(data) != done['report_sha256'] or data != host['message'].encode():
                        raise ValueError('retained task-readiness report changed')
                    with self.report_validation(done, host):
                        report = validate_readiness(done, host)
                    if report['status'] == 'READY' and not self.state.get('task_readiness_invalidated'):
                        continue
                # A valid BLOCKED observation can be rechecked on an explicit resume
                # after its prerequisite is supplied. Legacy boundary-only attempts
                # likewise receive readiness once, without repeating preflight-1.
            if index == 1 and any(a['status'] in ('reserved', 'failed') and a['stage'] != stage
                                  for a in self.state['attempts']):
                # Adopt the already-dispatched response before starting this new
                # readiness check. A legacy reservation is not permission to launch
                # a competing worker, even when its output is now available.
                self.state['preflight_complete'] = False
                self.save()
                return False
            probe = self.runtime / ('probe-' + str(index) + '.py')
            git_dir = Path(fs.git(self.root, 'rev-parse', '--absolute-git-dir').decode().strip())
            protected = [git_dir / 'HEAD', git_dir / 'index', self.item, self.runtime / 'admission.json', self.runtime / 'base-tree-key', self.runtime / 'repository.git/HEAD',
                         self.workspace / self.work]
            protected += [self.workspace / item['path'] for item in self.state['binding_inputs']]
            sentinel = self.runtime / 'candidate-sentinel'
            require_repo_local_ignored(self.root, sentinel)
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
            require_repo_local_ignored(self.root, probe)
            probe.write_text(script)
            inputs = {'contract_sha256': self.state['contract']['sha256'], 'probe_sha256': fs.digest(probe.read_bytes())}
            prompt = ('Authorized local host preflight. Run exactly `python3 ' + str(probe) +
                      '` from your scratch workspace. It attempts denied writes to protected test inputs and a '
                      'network connection expected to fail, and writes allowed scratch. Do not escalate or '
                      'change inputs. Print actual available ALL_TOOLS names if that runtime is exposed. '
                      'Return the exact probe output and observed permissions. No other effects are authorized.')
            if index == 1:
                inputs.update(task_readiness=readiness, candidate=self.stage_inputs(self.state['candidate']))
                prompt += (
                    f' In this same preflight context, inspect task readiness for {self.workspace / self.work} '
                    f'and its binding sources in {self.workspace}. Exact input_identity_json: {json.dumps(inputs)}. '
                    'Read the agreed evidence paths and check only the small set of existing prerequisites '
                    'needed to implement and verify them: required tools/runtimes, supplied source evidence, '
                    'fixtures, and local services or sockets. Use safe, short read-only checks from this actual '
                    'worker boundary; network is denied, approval escalation and MCP/apps/plugins are disabled, '
                    'candidate/agreement/Git are protected, and only scratch is writable. Host tools available '
                    'to the enclosing workflow are not inherited. A successful version/help command does not '
                    'establish service or socket access: safely probe the actual required access. '
                    'Use short bounded probes; correct a malformed shell command or diagnostic query before '
                    'classifying availability. A syntax/type error is not evidence of a missing service. '
                    'Do not install dependencies, start services, fetch or copy evidence bundles, invoke another '
                    'model or run acceptance/full test suites here. This is readiness, not implementation or proof. '
                    'A product file, behavior or regression test the contract asks implementation to create is '
                    'unfinished work, NEVER a missing prerequisite. Ordinary local setup that implementation '
                    'can perform with available tools and inputs is also work, not a blocker. '
                    'Return the structured report. Every check names its requirement_id, concrete prerequisite '
                    'and kind (tool/input/runtime/service), exact command as recorded by the host, an exact '
                    'nonempty substring of its output as observation, and whether it is available. Base availability '
                    'on those actual observations, never an echo of a claimed capability. READY requires all '
                    'required prerequisites available; an empty checks list is allowed when no task-specific '
                    'prerequisite needs a check, with the reason explained. BLOCKED requires an actually unmet '
                    'pre-existing prerequisite: missing_input must name one unavailable prerequisite exactly, '
                    'and expected_result must say what supplying/fixing it will establish so this delivery can '
                    'resume. Otherwise leave missing_input and expected_result empty. Do not reinterpret the '
                    'promise or manufacture a prerequisite to demand completed product behavior before work starts.')
            attempt, host = self.dispatch(stage, inputs, prompt, schema=schema if index == 1 else None)
            with self.report_validation(attempt, host):
                expected_keys = {str(p) + ':' + mode for p in protected for mode in ('absolute', 'symlink', 'subprocess')} | {'network', 'scratch'}
                observations = []
                for event in host['executions']:
                    for line in event.get('aggregated_output', '').splitlines():
                        if line.startswith('P2P_BOUNDARY=') and event.get('exit_code') == 0:
                            observations.append(json.loads(line.split('=', 1)[1]))
                if not any(isinstance(o, dict) and set(o) == expected_keys and
                           all(v == ('ok' if k == 'scratch' else 'denied') for k,v in o.items()) for o in observations):
                    raise ValueError('host preflight did not establish all permission boundaries: ' + attempt['id'])
                if before != {str(p): fs.digest(p.read_bytes()) for p in protected}:
                    raise ValueError('host preflight changed protected inputs')
                if index == 1:
                    report = validate_readiness(attempt, host)
            if index == 1:
                self.current()
                data = host['message'].encode()
                path = f'attempts/{attempt["id"]}/report.json'
                local_save(self.root, self.work, path, data)
                attempt.update(report=path, report_sha256=fs.digest(data))
                self.state['task_readiness'] = {'status': report['status'], 'attempt_id': attempt['id'],
                                                'report': path, 'report_sha256': attempt['report_sha256']}
                self.state.pop('task_readiness_invalidated', None)
            attempt['status'] = 'complete'
            self.save()
            if index == 1 and report['status'] == 'BLOCKED':
                self.state['preflight_complete'] = False
                self.save()
                raise ValueError('task prerequisite unavailable before implementation: ' + report['missing_input'] +
                                 '; expected: ' + report['expected_result'] +
                                 '; supply the prerequisite and resume this delivery')
        self.state['preflight_complete'] = True
        self.save()
        return True

    def stage_inputs(self, candidate):
        result = report_identity(candidate)
        if self.state.get('instruction_identity'):
            result['instruction_identity'] = self.state['instruction_identity']
        if self.state.get('local_git_generations'):
            generation = self.state['local_git_generations'][-1]
            result['local_git_generation'] = {key: generation[key] for key in
                                               ('sequence', 'candidate_key', 'tree', 'commit', 'record_sha256')}
        if self.state.get('routing') is not None:
            result['routing'] = self.state['routing']
        if self.state.get('routing_records'):
            result['routing_records'] = [
                {key: record[key] for key in ('path', 'sha256')}
                for record in self.state['routing_records']]
        return result

    def verification_history(self, name):
        """Offer one verifier its own checked observations, never another actor's verdict."""
        if name not in ('review', 'proof'):
            return None
        current_inputs = self.stage_inputs(self.state['candidate'])
        agreement = {key: value for key, value in current_inputs.items()
                     if key not in ('key', 'commit', 'local_git_generation')}
        previous = next((attempt for attempt in reversed(self.state['attempts'])
                         if attempt['stage'] == name and attempt['status'] == 'complete'
                         and attempt.get('report_validation') != 'rejected'
                         and {key: value for key, value in attempt['inputs'].items()
                              if key not in ('key', 'commit', 'local_git_generation')} == agreement), None)
        if previous is None:
            return None
        unavailable = {'stage': name, 'available': False,
                       'reason': 'Earlier observations cannot be validated; perform fresh checks.'}
        # Portable receipts intentionally omit command output and scratch evidence.
        # Do not turn a restored report into a cache for a different machine.
        if ((self.runtime / 'attempts' / previous['id'] / 'portable-receipt.json').exists() or
                previous.get('verification_environment') != self.verification_environment()):
            return unavailable | {'reason': 'Earlier verification environment or local evidence is unavailable.'}
        try:
            report_path = fs.safe(self.runtime, previous['report'])
            data = report_path.read_bytes()
            host = self.receipt(dict(previous))
            if (fs.digest(data) != previous['report_sha256'] or
                    host['message'].encode('utf-8') != data or
                    json.loads(json.loads(data)['input_identity_json']) != previous['inputs']):
                return unavailable
            mapping = previous['inputs'].get('local_git_generation', {})
            generation = next((item for item in self.state['local_git_generations']
                               if all(item.get(key) == value for key, value in mapping.items())
                               and mapping and item['candidate_key'] == previous['inputs'].get('key')), None)
            if generation is None:
                return unavailable
            latest = self.state['local_git_generations'][-1]
            repository = self.runtime / 'repository.git'
            before = fs.snapshot(repository, generation['commit'])
            after = fs.snapshot(repository, latest['commit'])
            if (fs.snapshot_key(before) != generation['candidate_key'] or
                    fs.snapshot_key(after) != self.state['candidate']['key']):
                return unavailable
            events = fs.safe(self.runtime, f'attempts/{previous["id"]}/events.jsonl')
            delta = fs.tree_changes(before, after)
            advice = applicability.classify(
                json.loads(data), delta, self.state['requirements'], name,
                prior_candidate=generation['candidate_key'],
                report_sha256=previous['report_sha256'])
            return {'stage': name, 'available': True, 'attempt_id': previous['id'],
                    'report': {'path': str(report_path), 'sha256': previous['report_sha256']},
                    'command_evidence': {'path': str(events), 'sha256': fs.digest(events.read_bytes())},
                    'scratch': previous['scratch'], 'repository': str(repository),
                    'previous_candidate': {'key': generation['candidate_key'], 'commit': generation['commit']},
                    'current_candidate': {'key': latest['candidate_key'], 'commit': latest['commit']},
                    'complete_delta': delta, 'applicability': advice,
                    'verification_environment': previous['verification_environment']}
        except (OSError, ValueError, KeyError, TypeError):
            # History is optional. Missing old evidence means new observations,
            # not a weaker verdict or an unrelated storage-repair project.
            return unavailable

    def stage(self, name, reconcile=False):
        mandate = self.state.get('autonomy')
        if name == 'implementation' and not reconcile and mandate and 'implementation' not in mandate['policy']['decisions']:
            raise ValueError('implementation decision outside the standing mandate')
        if reconcile:
            self.timed_source_stable()
            self.verify_generation_chain()
        else:
            self.current()
        slices_enabled = name == 'implementation' and self.state.get('implementation_slice_version') == 1
        if slices_enabled:
            slices.verify_retained(self.state, self.runtime, self.receipt)
            if len(self.state.get('implementation_slices', [])) >= slices.MAX_SLICES:
                raise ValueError('implementation exhausted meaningful slice budget; reconcile the delivery boundary')
        inputs = self.stage_inputs(self.state['candidate'])
        prior = self.state.get('reports', {})
        skill_stage = self.state.get('repair_skill', 'repair') if name == 'repair' else name
        learning_format = ('learning_candidates is an array of at most five candidate lessons and is usually empty. '
                           'Include only durable, non-obvious, reusable delivery knowledge whose loss could cause '
                           'future mistakes or substantial rediscovery. Each item has nonblank scope, lesson, evidence, '
                           'and uncertainty. A learning candidate is advisory evidence only: it must not change the '
                           'contract, stage verdict, scope, repair allowance, or authority, and it is not accepted '
                           'project advice until retrospect validates it and a human explicitly accepts it. ')
        report_format = ('Review rows contain only id and observation. Include nonblank coverage; checks with '
                         'command, result (passed, failed, observed, or unavailable), and observation; and '
                         'limitations. Each finding has id, source (requirement ID or binding source), primary '
                         'axis (Contract fidelity, Scope and simplicity, or Engineering quality), location, '
                         'evidence, consequence, smallest correction or next check, and handoff '
                         '(implement-contract or plan-acceptance). REVIEWED requires empty findings and gaps; '
                         'CHANGES NEEDED requires a finding. For BLOCKED, name the exact missing input or '
                         'configured command and expected result in missing_input and expected_result; leave '
                         'both blank otherwise. Give a substantive observation for every requirement. Do not '
                         'assign review verdicts. '
                         if name == 'review' else
                         'Each row needs a substantive observation. Proof rows need command/output evidence in '
                         'artifact, an assertion, and observation. Use verdict proven for established proof rows; '
                         'otherwise name the gap. ')
        coverage_required = self.state.get('coverage_format_version') in (1, 2)
        risks_required = self.state.get('coverage_format_version') == 2
        coverage_prompt = (
            'Include coverage_trace. For each requirement ID give paths to real product files, '
            'existing=true only for already-sufficient unchanged behavior, and evidence refs. '
            'Use row for the saved stage requirement observation/evidence; check:N for an actual '
            'zero-based review check; file:PATH for exact candidate files; or '
            'record:ID@sha256:DIGEST for an existing verified Evidence Record v1. '
            'Never invent references. Explain necessary changed files outside requirement mappings '
            'as supporting_changes (path and reason). A missing implementation/evidence stays a gap. '
            'For review, inspected_paths names the exact existing product files actually inspected, '
            'including all changed files that still exist. Do not claim inspection you did not do. '
            'These are compact trace facts, not a duplicate proof or a new acceptance verdict. '
            if coverage_required else '')
        risk_prompt = (
            'Also include coverage_trace.risks: the few materially applicable candidate seams '
            'whose realistic failure triggers matter, with id S1/S2..., requirement IDs, '
            'exact product paths (including relevant existing callers/config/dependencies), '
            'reach bounded or uncertain, trigger, why_applicable, concrete consequence, '
            'saved evidence references, and addressed/unresolved status. Empty risks [] '
            'is correct for a genuinely low-risk change with no additional material risk; '
            'no quota or universal checklist. A static inspection can establish a material '
            'conditional risk even without an exploit. Review does not reproduce all proof. '
            'If a material risk or required check is unresolved, do not claim a successful '
            'stage or downgrade the risk merely to finish. For consequential uncertainty '
            'prefer one independently checked property/invariant, interleaving or fault '
            'scenario only if examples leave a real gap; do not impose it on the low-risk '
            'control. On repaired code inspect the complete diff and affected seams, '
            'recheck invalidated assumptions, and describe bounded applicability of prior '
            'observations instead of trusting small file-count deltas. '
            if risks_required else '')
        instruction_source = 'pinned' if self.state.get('instruction_identity') else 'original installed'
        prompt = (f'Invoke the {instruction_source} {STAGES[skill_stage]} skill at {self.state["skills"][skill_stage]["path"]}. '
                  f'Read it and its references. Work item {self.work}, workspace {self.workspace}. '
                  f'For bundled helper commands, use the compatible controller scripts at {Path(__file__).resolve().parent}; '
                  'the retained instruction tree contains normative text, not another controller installation. '
                  f'Comparison base {self.state["comparison_base"]} is the immutable admission base for this invocation. '
                  'Use it as the review comparison and proof binding; later destination movement is observational and '
                  'must not replace this base or trigger a verifier restart. Whole contract, full scope. '
                  f'Approved delivery routing (separate from product identity): {json.dumps(self.state.get("routing"))}. '
                  f'Latest destination observation (informational only): {json.dumps(self.state.get("destination_observation"))}. '
                  'Read the transferred approved plan, current sizing/shape records, and linked history; verify '
                  'their identities and prerequisite outcomes in the actual candidate. '
                  'The enclosing controller owns durable reports; return your full report in the required JSON '
                  'schema and it will save and reread it. Never mutate the source checkout, controller records, '
                  'agreement or binding inputs, or source/delivered Git metadata. Local stages and safe scratch '
                  'checks only; no external effects. No commits of delivery work, pushes, publication or cleanup. '
                  'Use fresh independent observations, do not trust previous judgments. '
                  f'Exact input_identity_json must encode this object: {json.dumps(inputs)}. '
                  f'Every requirement must occur exactly once: {self.state["requirements"]}. '
                  f'{report_format}{learning_format}{coverage_prompt}{risk_prompt}Status uses normal skill vocabulary. '
                  f'{"The controller renders review text from structured fields. Do not add free-text details or other top-level fields." if name == "review" else "details contains the full human report."} '
                  'Keep generated fixtures and verbose debug output in scratch. Return the relevant command, '
                  'assertion, result, and environment in the report; do not dump entire logs or workspaces. '
                  'Never fabricate results. '
                  f'Previous reports for repair only: {json.dumps(prior) if name == "repair" else "none"}. ')
        if self.state.get('autonomy'):
            prompt += ('Standing local decision mandate: ' + json.dumps(self.state['autonomy']['policy']) +
                       '. Apply authorized recommendations and resolve recoverable local gaps yourself. '
                       'Do not ask for another time bound or permission already delegated. External effects '
                       'remain disabled in this worker; the outer workflow owns granted publication effects. ')
        if name == 'repair':
            prompt += ('Recovery strategy: ' + json.dumps(self.state.get('recovery_history', [])[-1:]) +
                       '. Use the named new approach; preserve prior evidence and include any real local '
                       'prerequisite or integration work needed for these requirements. Evidence-only recovery '
                       'must preserve all product bytes. Do not substitute same-context fixtures for an '
                       'independent workflow observation. ')
        if name in ('review', 'proof'):
            history = self.verification_history(name)
            prompt += ('Candidate and Git metadata are protected outside writable scratch. Run checks against '
                       'the fixed workspace; place outputs and PYTHONPYCACHEPREFIX/TMPDIR in scratch. '
                       'Do not copy and edit product code to make a check pass. Inspect the full candidate. '
                       'Use the smallest sufficient checks for the material questions this stage owns. '
                       'Review is not a second exhaustive acceptance proof. Do not repeat an expensive full '
                       'suite merely to produce a fresh report; run it when a binding requirement or an '
                       'unbounded material regression risk needs it. '
                       'Earlier observations from this same stage only: ' + json.dumps(history) + '. '
                       'When available, inspect the retained same-stage report and checked command receipts. '
                       'The read-only applicability classification identifies candidate paths/requirements '
                       'that appear disjoint from the exact product delta, but it is an advisory check plan '
                       'NOT a cached result or permission to skip the current verdict. Independently assess '
                       'upstream dependencies, caller reach, risk assumptions, and all binding final checks. '
                       'For marked reusable observations cite their original candidate and exact evidence '
                       'and explain continued applicability; never copy an old verdict. Refresh all affected '
                       'checks, repaired gaps, tests/oracles and relevant interactions. FULL_RECHECK or missing '
                       'receipts means fresh broad observations. Unknown impact requires broad fresh checks '
                       'even for a one-file edit. Every run issues its own new full-contract independent '
                       'REVIEWED/PROVEN judgment bound to the new exact candidate. '
                       'Do not read the other verifier\'s reports. ')
        else:
            prompt += ('Implement the smallest complete change in the workspace. .p2p/tmp/ is disposable scratch; '
                       'do not include it in product content. Preserve agreement and binding inputs. '
                       'Use focused checks while making a correction. Once the candidate is ready, finish '
                       'the required repository checks; do not restart a full suite after each intermediate '
                       'edit or repeat an unchanged passing check without a concrete reason. ')
            if slices_enabled:
                progress = self.state.get('implementation_slices', [])
                prompt += (
                    'Plan the next useful implementation slice INSIDE THIS invocation, not via another '
                    'planner stage. Default to ONE whole-outcome slice and status IMPLEMENTED when this '
                    'change and all meaningful required checks fit coherently. Only if a concrete '
                    'dependency, separately observable outcome or recoverability boundary justifies '
                    'more work, finish and CHECK one slice, return status PARTIAL, and name the exact '
                    'next useful action and reason. WIP=1: never start more than one slice here, '
                    'do not invent micro-tasks, duplicate checks or seek extra approval. '
                    'Return implementation_slice as structured controller-owned slice facts: '
                    'I1/I2... in order, accepted requirement IDs, expected observable result, '
                    'changed/relevant paths, actual exercised checks (test, inspection or manual '
                    'with exact host command/result/output observation), VERIFIED or BLOCKED outcome, '
                    'justified boundary_reason, next_action, and any obsolete earlier slice IDs '
                    'with substantive retirement reasons. Never mark VERIFIED without real host '
                    'command/output evidence; non-test inspection is acceptable if observed. '
                    'IMPLEMENTED requires all accepted requirements covered by active verified '
                    'slices, no gaps and no next action. A partial VERIFIED result must name '
                    'remaining gaps. A blocked slice is not a passing checkpoint. '
                    'For a true structural split of the agreed outcome, retain progress and '
                    'use the existing /slice-contract handoff, not internal micro-slicing. '
                    'Resume from previously verified slices when their original dependencies '
                    'and current candidate bytes still apply, rechecking any changed assumptions. '
                    'Previous controller-verified implementation slices (history is not new proof): '
                    + json.dumps(progress) + '. ')
        attempt, host = self.dispatch(name, inputs, prompt,
                                      self.workspace if name in ('implementation', 'repair') else None,
                                      report_schema(name, coverage_required, risks_required,
                                                    slices_enabled))
        self.timed_source_stable()
        if name in ('review', 'proof'):
            # Source stability was just verified at this same receipt boundary.
            # Validate the exact candidate here without repeating that complete
            # source scan, pinned instruction and base preflight a second time.
            self.current(check_source=False)
        scope = None
        with self.report_validation(attempt, host):
            raw_report = host['message'].encode('utf-8')
            report = json.loads(raw_report)
            expected_fields = {'status', 'input_identity_json', 'requirements', 'gaps', 'learning_candidates'}
            if coverage_required:
                expected_fields.add('coverage_trace')
            if slices_enabled:
                expected_fields.add('implementation_slice')
            if name == 'review':
                expected_fields.update({'findings', 'coverage', 'checks', 'limitations', 'missing_input', 'expected_result'})
            else:
                expected_fields.add('details')
            if not isinstance(report, dict) or set(report) != expected_fields:
                raise ValueError('stage report contains unsupported or missing fields: ' + attempt['id'])
            learning_fields = {'scope', 'lesson', 'evidence', 'uncertainty'}
            candidates = report.get('learning_candidates')
            if (not isinstance(candidates, list) or len(candidates) > 5 or
                    any(not isinstance(item, dict) or set(item) != learning_fields or
                        any(not isinstance(item[key], str) or not item[key].strip() for key in learning_fields)
                        for item in candidates)):
                raise ValueError('stage report learning candidates are incomplete')
            if name == 'review' and report['status'] not in ('REVIEWED', 'CHANGES NEEDED', 'BLOCKED'):
                raise ValueError('review report has unsupported status')
            if json.loads(report['input_identity_json']) != inputs:
                raise ValueError('stage returned stale or mistyped input identity: ' + attempt['id'])
            rows = report['requirements']
            if sorted(row['id'] for row in rows) != sorted(self.state['requirements']):
                raise ValueError('stage omitted/duplicated full requirement coverage: ' + attempt['id'])
            if (name != 'review' and not report['details'].strip()) or any(not row['observation'].strip() for row in rows):
                raise ValueError('stage returned incomplete report observations: ' + attempt['id'])
            if name == 'review':
                if any(set(row) != {'id', 'observation'} for row in rows):
                    raise ValueError('review report rows must not contain verdicts or proof evidence')
                if not isinstance(report['coverage'], str) or not report['coverage'].strip():
                    raise ValueError('review report coverage is incomplete')
                findings = report.get('findings')
                finding_fields = {'id', 'source', 'axis', 'location', 'evidence', 'consequence', 'correction', 'handoff'}
                if not isinstance(findings, list) or any(not isinstance(item, dict) or set(item) != finding_fields or
                        any(not isinstance(item[key], str) or not item[key].strip() for key in finding_fields) or
                        item['axis'] not in REVIEW_AXES or item['handoff'] not in ('implement-contract', 'plan-acceptance')
                        for item in findings):
                    raise ValueError('review report findings are incomplete')
                if len({item['id'] for item in findings}) != len(findings):
                    raise ValueError('review report finding IDs are duplicated')
                check_fields = {'command', 'result', 'observation'}
                if not isinstance(report['checks'], list) or any(not isinstance(item, dict) or set(item) != check_fields or
                        any(not isinstance(item[key], str) or not item[key].strip() for key in check_fields) or
                        item['result'] not in ('passed', 'failed', 'observed', 'unavailable') for item in report['checks']):
                    raise ValueError('review report checks are incomplete')
                for field in ('gaps', 'limitations'):
                    if not isinstance(report[field], list) or any(not isinstance(item, str) or not item.strip() for item in report[field]):
                        raise ValueError('review report ' + field + ' are incomplete')
                if report['status'] == 'REVIEWED' and (findings or report['gaps']):
                    raise ValueError('REVIEWED review report contains findings or gaps')
                if report['status'] == 'CHANGES NEEDED' and not findings:
                    raise ValueError('CHANGES NEEDED review report has no findings')
                if report['status'] == 'BLOCKED':
                    if any(not isinstance(report[field], str) or not report[field].strip()
                           for field in ('missing_input', 'expected_result')):
                        raise ValueError('BLOCKED review report must name the missing input and expected result')
                elif report['missing_input'] or report['expected_result']:
                    raise ValueError('non-blocked review report contains blocked-only details')
            if slices_enabled:
                repository = self.runtime / 'repository.git'
                before = fs.snapshot(repository,
                                     self.state['local_git_generations'][-1]['commit'])
                current = fs.snapshot(self.workspace, exclude=self.state.get('agreement_paths', ()))
                slices.validate(report, self.state['requirements'],
                                self.state.get('implementation_slices', []),
                                host['executions'], current, before)
            if coverage_required:
                manifest = fs.snapshot(self.workspace, exclude=self.state.get('agreement_paths', ()))
                base = fs.snapshot(self.workspace, self.state['comparison_base'],
                                   exclude=self.state.get('agreement_paths', ()))
                changed = fs.tree_changes(base, manifest)
                records = fs.available_evidence_refs(
                    self.workspace, self.work, fs.snapshot_key(manifest),
                    self.state['contract']['sha256'])
                fs.validate_coverage_trace(report['coverage_trace'], self.state['requirements'],
                                           report, name, manifest, changed, records,
                                           risks=risks_required)
                if name == 'review':
                    scope = fs.review_scope(self.state['candidate'], manifest,
                                            self.state['local_git_generations'][-1]['commit'],
                                            report['coverage_trace']['inspected_paths'],
                                            self.state.get('agreement_paths', ()),
                                            report.get('limitations', ()), report['coverage_trace'],
                                            report.get('checks', ()))
            if name == 'proof' and report['status'] == 'PROVEN':
                if not host['executions'] or any(row['verdict'] != 'proven' or not row['evidence'] for row in rows):
                    raise ValueError('proof lacks full independently exercised evidence')
                for row in rows:
                    for evidence in row['evidence']:
                        if any(not evidence[k].strip() for k in ('assertion', 'observation', 'artifact')):
                            raise ValueError('proof evidence is incomplete: ' + row['id'])
        path = f'attempts/{attempt["id"]}/report.json'
        stored = self.runtime / path
        if stored.exists() and stored.read_bytes() != raw_report:
            raise ValueError('conflicting duplicate stage result: ' + attempt['id'])
        local_save(self.root, self.work, path, raw_report)
        attempt['destination_observation'] = self.state.get('destination_observation')
        attempt['verification_environment'] = self.verification_environment()
        summary = (review_markdown(report, self.work, self.state['contract'], self.state['candidate'],
                                   fs.snapshot(self.workspace, self.state['comparison_base']),
                                   attempt['destination_observation'], self.verification_environment(),
                                   attempt['session_id'], scope)
                   if name == 'review' else
                   report['details'].rstrip() + '\n\n' +
                   (coverage_markdown(report) + '\n\n' if coverage_required else '') +
                   learning_candidates_markdown(report) + '\n').encode()
        local_save(self.root, self.work, f'attempts/{attempt["id"]}/report.md', summary)
        local_save(self.root, self.work, name + '.md', summary)
        attempt.update(status='complete', report=path, report_sha256=fs.digest(raw_report))
        self.state.setdefault('reports', {})[name] = {
            'path': path, 'sha256': attempt['report_sha256'],
            'attempt_id': attempt['id'], 'inputs': inputs,
            **({'coverage_trace_sha256': fs.digest(fs.canonical(report['coverage_trace']))}
               if coverage_required else {}),
            **({'review_scope': scope} if scope else {}),
        }
        self.save()
        if name in ('review', 'proof'):
            self.checkpoint()
        return report

    def read_report(self, name):
        record = self.state['reports'][name]
        data = (self.runtime / record['path']).read_bytes()
        if fs.digest(data) != record['sha256']:
            raise ValueError('report/evidence content changed or lost: ' + name)
        attempt = next(a for a in self.state['attempts'] if a['id'] == record['attempt_id'])
        self.check_report_rejection(attempt)
        host = self.receipt(attempt)
        if host['message'].encode('utf-8') != data:
            raise ValueError('report differs from host return: ' + name)
        report = json.loads(data)
        if name == 'review' and 'coverage' in report:
            summary = review_markdown(report, self.work, self.state['contract'], self.state['candidate'],
                                      fs.snapshot(self.workspace, self.state['comparison_base']),
                                      attempt.get('destination_observation'),
                                      attempt.get('verification_environment', self.verification_environment()),
                                      attempt.get('session_id'), record.get('review_scope'))
        elif name == 'review' and 'details' in report:
            summary = report['details']
            if not isinstance(summary, str):
                raise ValueError('legacy review report details are invalid')
        else:
            summary = (report_markdown(report) if name == 'review' else
                       report['details'].rstrip() + '\n\n' +
                       (coverage_markdown(report) + '\n\n' if 'coverage_trace' in report else '') +
                       learning_candidates_markdown(report) + '\n')
        if 'coverage_trace' in report and record.get('coverage_trace_sha256') != fs.digest(
                fs.canonical(report['coverage_trace'])):
            raise ValueError('retained coverage facts changed or lost: ' + name)
        if (self.local / (name + '.md')).read_bytes() != summary.encode():
            raise ValueError('canonical report content changed or lost: ' + name)
        if name == 'review' and 'coverage' not in report:
            summary = report_markdown(report)
        report['details'] = summary
        return report

    def verified_unchanged_completion(self):
        """Read back exact final local acceptance without a new write/dispatch.

        May only run after admission to this very host has passed preflight.
        Restored checkpoints MUST pass receiving-host preflight before this path.
        """
        if (self.state.get('status') != 'REVIEWED_AND_PROVEN' or
                not self.state.get('completed_at') or
                not self.state.get('preflight_complete') or
                self.state.get('task_readiness_invalidated')):
            raise ValueError('completed delivery lacks current host readiness; resume at existing preflight')
        if any(a.get('status') not in ('complete', 'retired')
               for a in self.state.get('attempts', [])):
            raise ValueError('uncertain worker reservation must be reconciled before reuse')
        if any(entry.get('status') == 'reserved'
               for entry in self.state.get('recovery_history', [])) or (
                   self.state.get('recovery_decision', {}).get('status') in
                   ('pending', 'diagnosed', 'rejected')):
            raise ValueError('pending recovery needs reconciliation before reuse')
        for name in ('instruction-transition.json', 'agreement-transition.json',
                     'limit-extension.json'):
            journal = self.runtime / name
            if journal.is_file():
                record = json.loads(journal.read_bytes())
                if not (record.get('complete') is True or
                        (name == 'agreement-transition.json' and record.get('status') == 'complete')):
                    raise ValueError('unfinished ' + name + ' must be reconciled before reuse')
        candidate = self.current()
        if not candidate or not self.state.get('implementation_complete'):
            raise ValueError('completed implementation/candidate identity is unavailable')
        inputs = self.stage_inputs(candidate)
        sessions = []
        for name, verdict in (('review', 'REVIEWED'), ('proof', 'PROVEN')):
            if self.state.get('reports', {}).get(name, {}).get('inputs') != inputs:
                raise ValueError('stale ' + name + ' stage inputs prevent completed-stage reuse')
            report = self.read_report(name)
            if (report.get('status') != verdict or report.get('gaps') or
                    (name == 'review' and report.get('findings')) or
                    sorted(item['id'] for item in report['requirements']) !=
                    sorted(self.state['requirements']) or
                    (name == 'proof' and any(item.get('verdict') != 'proven' or
                                             not item.get('evidence')
                                             for item in report['requirements']))):
                raise ValueError('completed ' + name + ' evidence no longer establishes acceptance')
            attempt_id = self.state['reports'][name]['attempt_id']
            attempt = next(a for a in self.state['attempts'] if a['id'] == attempt_id)
            sessions.append(attempt.get('session_id'))
        if not all(sessions) or len(set(sessions)) != 2:
            raise ValueError('independent completed verifier sessions could not be established')
        checkpoint = self.state.get('checkpoint')
        if checkpoint and checkpoint.get('status') == 'LOCAL_ONLY':
            path = fs.safe(self.root, checkpoint['path'])
            if not path.is_file() or fs.digest(path.read_bytes()) != checkpoint['sha256']:
                raise ValueError('saved portable checkpoint changed or vanished; reconcile before reuse')
        return {'status': 'UNCHANGED_COMPLETION', 'candidate_key': candidate['key'],
                'review': 'REUSED', 'proof': 'REUSED',
                'checkpoint': checkpoint.get('status') if checkpoint else 'RESTORED',
                'new_model_calls': 0, 'new_canonical_writes': 0,
                'reason': 'Read back current exact candidate, both independent reports and host receipt identities.'}

    def final_record(self, cleanup=None, retained_artifacts=()):
        candidate = self.state['candidate']
        candidate_bytes = encoded(candidate)
        review_bytes = self.state['final_review'].encode()
        proof_bytes = self.state['final_proof'].encode()
        value = {
            'schema': 'promise-to-proof/delivery-record/v1',
            'status': 'REVIEWED_AND_PROVEN',
            'work_item': self.work,
            'invocation_id': self.state['invocation_id'],
            'contract': {key: self.state['contract'][key] for key in ('source', 'revision', 'sha256')},
            'binding_inputs': self.state['binding_inputs'],
            'comparison_base': self.state['comparison_base'],
            'candidate_key': candidate_key(candidate),
            'candidate_record_sha256': fs.digest(candidate_bytes),
            'candidate_changes_sha256': fs.digest(fs.canonical(candidate.get('changes', []))),
            'agreement_paths': self.state.get('agreement_paths', [self.work]),
            'review_sha256': fs.digest(review_bytes),
            'proof_sha256': fs.digest(proof_bytes),
            'completed_at': self.state['completed_at'],
            'autonomy': self.state.get('autonomy'),
            'limits': self.state['limits'],
            'recovery_count': len(self.state.get('recovery_history', [])),
            'agreement_history': self.state.get('agreement_history', []),
            'limit_extensions': self.state.get('limit_extensions', []),
            'instruction_identity': self.state.get('instruction_identity'),
            'instruction_history': self.state.get('instruction_history', []),
            'cleanup': cleanup or self.state.get('cleanup', 'awaiting source checkout verification'),
            'routing': route_record(self.state['routing']),
            'destination_observation': self.state.get('destination_observation'),
            **({'review_scope': self.state['reports']['review']['review_scope'],
                'coverage_trace_sha256': {
                    stage: item['coverage_trace_sha256'] for stage, item in self.state['reports'].items()
                    if 'coverage_trace_sha256' in item},
                } if 'review_scope' in self.state.get('reports', {}).get('review', {}) else {}),
        }
        if retained_artifacts:
            value['retained_artifacts'] = list(retained_artifacts)
        if self.state.get('github_record'):
            value['github_record'] = self.state['github_record']
        if self.state.get('cleanup_verified_at'):
            value.update(cleanup=self.state['cleanup'],
                         cleanup_source_identity_sha256=self.state['cleanup_source_identity_sha256'],
                         cleanup_verified_at=self.state['cleanup_verified_at'])
        return value

    def persist_final(self):
        candidate = self.state['candidate']
        retained_artifacts = []
        for name, reason in RETAINED_ARTIFACTS.items():
            path = self.directory / name
            if path.is_file() and not path.is_symlink():
                retained_artifacts.append({'path': name, 'reason': reason,
                                           'sha256': fs.digest(path.read_bytes())})
        values = {'candidate.json': encoded(candidate), 'review.md': self.state['final_review'].encode(),
                  'proof.md': self.state['final_proof'].encode()}
        values['delivery.json'] = encoded(self.final_record(retained_artifacts=retained_artifacts))
        compact = check_final_footprint(self.root, self.work, values)
        for name, expected in compact.items():
            previous = self.state.get('superseded_artifacts', {}).get(name)
            if previous is not None and previous != expected:
                raise ValueError('superseded durable artifact changed during cleanup: ' + name)
            data = fs.safe(self.directory, name).read_bytes()
            if fs.digest(data) != expected:
                raise ValueError('superseded durable artifact changed during cleanup: ' + name)
            local_save(self.root, self.work, 'runtime/superseded-records/' + name, data)
        self.state['superseded_artifacts'] = self.state.get('superseded_artifacts', {}) | compact
        self.save()
        for name, data in values.items():
            save_final(self.root, self.work, name, data)
        for name, data in values.items():
            if fs.safe(self.directory, name).read_bytes() != data:
                raise ValueError('durable completion record readback failed: ' + name)
        return compact

    def verify_final_readback(self, source_change_error):
        source = fs.snapshot(self.root, exclude=self.state.get('agreement_paths', ()))
        source_identity = fs.digest(fs.canonical(fs.tree_identity(source)))
        if source_identity != self.state.get('cleanup_source_identity_sha256'):
            raise ValueError(source_change_error)
        self.verify_superseded_recovery()
        value = completed_result(self.root, self.work, self.directory)
        if (value['invocation_id'] != self.state['invocation_id'] or
                value['candidate'] != identity(self.state['candidate']) or
                value['comparison_base'] != self.state['comparison_base'] or
                value['candidate'].get('binding_inputs') != self.state.get('binding_inputs')):
            raise ValueError('durable completed delivery unavailable: final records differ from local invocation identity')
        record = json.loads((self.directory / 'delivery.json').read_text())
        expected_contract = {key: self.state['contract'][key] for key in ('source', 'revision', 'sha256')}
        if (record.get('contract') != expected_contract or
                record.get('candidate_record_sha256') != fs.digest(encoded(self.state['candidate'])) or
                record.get('review_sha256') != fs.digest(self.state.get('final_review', '').encode()) or
                record.get('proof_sha256') != fs.digest(self.state.get('final_proof', '').encode())):
            raise ValueError('durable completed delivery unavailable: final records differ from local invocation identity')
        if record.get('autonomy') != self.state.get('autonomy') or record.get('agreement_history', []) != self.state.get('agreement_history', []):
            raise ValueError('durable completion mandate or planning receipts differ from local invocation')
        if record.get('github_record') != self.state.get('github_record'):
            raise ValueError('durable completed delivery unavailable: GitHub record receipt differs from local state')
        values = {name: fs.safe(self.directory, name).read_bytes()
                  for name in ('candidate.json', 'delivery.json', 'review.md', 'proof.md')}
        compact = check_final_footprint(self.root, self.work, values)
        if any(self.state.get('superseded_artifacts', {}).get(name) != digest
               for name, digest in compact.items()):
            raise ValueError('superseded durable artifacts changed after cleanup finalization')
        return value

    def remove_superseded_artifacts(self):
        for name, expected in self.state.get('superseded_artifacts', {}).items():
            if name in FINAL_RECORDS:
                continue
            path = fs.safe(self.directory, name)
            if not path.exists() and not path.is_symlink():
                continue
            if path.is_symlink() or not path.is_file() or fs.digest(path.read_bytes()) != expected:
                raise ValueError('superseded durable artifact changed during cleanup: ' + name)
            path.unlink()

    def remove_local_execution_state(self):
        attempts = self.runtime / 'attempts'
        if attempts.is_symlink():
            raise ValueError('local attempt records are a symlink')
        if attempts.exists():
            shutil.rmtree(attempts)
        agreement = agreement_root(self.root, self.work)
        if agreement.exists():
            shutil.rmtree(agreement)
        for name in ('implementation.md', 'repair.md', 'review.md', 'proof.md'):
            (self.local / name).unlink(missing_ok=True)
        (self.local / 'delivery.json').unlink(missing_ok=True)
        # Keep the isolated candidate checkout and its Git objects for publication.
        retained = {'workspace', 'repository.git', 'base-tree-key', 'generations'}
        for child in self.runtime.iterdir():
            if child.is_symlink():
                raise ValueError('execution runtime artifact is a symlink: ' + child.name)
            if child.name in retained:
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()

    def complete(self, check_source=True):
        candidate = self.current(check_source=check_source)
        review, proof = self.read_report('review'), self.read_report('proof')
        for name, report in (('review', review), ('proof', proof)):
            if json.loads(report['input_identity_json']) != self.stage_inputs(candidate):
                raise ValueError('stale ' + name + ' candidate/agreement/base identity')
            if sorted(row['id'] for row in report['requirements']) != sorted(self.state['requirements']):
                raise ValueError('incomplete ' + name + ' requirement coverage')
        if review['status'] != 'REVIEWED' or proof['status'] != 'PROVEN' or review['gaps'] or proof['gaps']:
            raise ValueError('full REVIEWED and PROVEN results are not available')
        if review.get('findings'):
            raise ValueError('review contains unresolved findings')
        if 'findings' not in review and any(row.get('verdict') != 'reviewed' for row in review['requirements']):
            raise ValueError('legacy review contains unresolved requirement findings')
        manifest = fs.snapshot(self.workspace, exclude=self.state.get('agreement_paths', ()))
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
        proof_attempt = next(a for a in self.state['attempts'] if a['id'] == self.state['reports']['proof']['attempt_id'])
        proof_environment = proof_attempt.get('verification_environment', self.verification_environment())
        normalized_proof = {'contract': contract_identity, 'candidate_key': key, 'status': 'PROVEN',
                            'stability': {'contract': 'unchanged', 'candidate': 'unchanged'},
                            'verification_context': proof_environment, 'verdicts': verdicts,
                            'evidence': evidence, 'details': text(proof['details'])}
        value = {'schema': bundle.SCHEMA, 'claim': 'REVIEWED_AND_PROVEN', 'contract': self.state['contract'],
                 'candidate': {'key': key, 'manifest': manifest, 'comparison_base': 'git:' + candidate['comparison_base']},
                 'review': normalized_review, 'proof': normalized_proof}
        issues = bundle.verify_bundle(value)
        if issues:
            raise ValueError('acceptance bundle rejected: ' + json.dumps(issues))
        local_save(self.root, self.work, 'runtime/acceptance-bundle.json', encoded(value))
        self.current(check_source=check_source)
        already_complete = (self.state.get('status') == 'REVIEWED_AND_PROVEN' and
                            self.state.get('completed_at'))
        if self.state.get('coverage_format_version') in (1, 2):
            for name in ('review', 'proof', 'implementation'):
                record = self.state.get('reports', {}).get(name)
                if record and 'coverage_trace_sha256' not in record:
                    raise ValueError('missing exact requirement/evidence trace for ' + name)
            if not self.state['reports']['review'].get('review_scope'):
                raise ValueError('missing exact inspected product scope for review')
        self.state.update(status='REVIEWED_AND_PROVEN' if already_complete else 'RUNNING',
                          blocker=None,
                          completed_at=self.state.get('completed_at') if already_complete else None,
                          ended_at=None,
                          final_review=review['details'],
                          final_proof=proof_markdown(proof, self.work, self.state['contract'], candidate,
                                                     proof_environment, proof_attempt['session_id']))
        self.save()
        if not already_complete:
            self.state.update(status='REVIEWED_AND_PROVEN', completed_at=now())
            try:
                local_save(self.root, self.work, 'delivery.json', encoded(self.state))
            except (ValueError, OSError) as error:
                self.state.update(status='BLOCKED',
                                  blocker='terminal measurement finalization failed: ' + str(error),
                                  completed_at=None, ended_at=now(), ended_epoch=time.time())
                raise
        self.checkpoint()

    def verify_github_readback(self):
        receipt = self.state.get('github_record')
        if not receipt:
            if issue_source(self.root, self.work, self.state['contract']['content']):
                raise ValueError('issue-backed cleanup requires a verified durable GitHub record')
            return
        preview = issue_record_preview(self, receipt['delivered_commit'], receipt.get('pull_request'))
        if (receipt.get('id') != preview['id'] or receipt.get('repository') != preview['repository'] or
                receipt.get('issue') != preview['issue'] or receipt.get('body_sha256') != preview['sha256']):
            raise ValueError('local GitHub record receipt does not match the accepted delivery preview')
        issue = github_issue(preview['repository'], preview['issue'])
        if fs.digest((issue.get('body') or '').encode()) != preview['record']['source_issue']['body_sha256']:
            raise ValueError('source issue body changed before cleanup')
        marker = ISSUE_RECORD_PREFIX + preview['id'] + ' -->'
        matches = [comment for comment in github_comments(preview['repository'], preview['issue'])
                   if marker in comment.get('body', '')]
        if len(matches) != 1 or matches[0].get('body') != preview['body'] or matches[0].get('html_url') != receipt.get('url'):
            raise ValueError('durable GitHub record readback changed before cleanup')
        receipt['cleanup_verified_at'] = now()
        self.save()

    def cleanup(self):
        if self.state.get('status') != 'REVIEWED_AND_PROVEN':
            raise ValueError('only a REVIEWED_AND_PROVEN delivery can be cleaned')
        if self.state.get('cleanup_verified_at') and self.state.get('final_records_written'):
            self.verify_final_readback('source checkout changed after cleanup identity verification')
            self.remove_superseded_artifacts()
            self.remove_local_execution_state()
            return
        self.timed_source_stable()
        self.complete(check_source=False)
        self.verify_github_readback()
        candidate_tree = fs.snapshot(self.workspace, exclude=self.state.get('agreement_paths', ()))
        source_tree = fs.snapshot(self.root, exclude=self.state.get('agreement_paths', ()))
        source_key = fs.snapshot_key(fs.snapshot(self.root))
        if source_key == self.state['source_tree_key']:
            cleanup = 'source checkout unchanged'
        elif source_tree == candidate_tree:
            cleanup = 'candidate already present in source checkout'
        else:
            raise ValueError('source checkout changed since admission; cleanup never applies the candidate')
        if fs.tree_changes(fs.snapshot(self.workspace, self.state['comparison_base'], exclude=self.state.get('agreement_paths', ())), candidate_tree) != self.state['candidate'].get('changes', []):
            raise ValueError('candidate compact identity changed before cleanup')
        source_identity = fs.digest(fs.canonical(fs.tree_identity(source_tree)))
        self.state.update(cleanup_verified_at=self.state.get('cleanup_verified_at') or now(),
                          cleanup_source_identity_sha256=source_identity,
                          cleanup=cleanup)
        self.persist_final()
        self.state['final_records_written'] = True
        self.save()
        self.verify_final_readback('source checkout changed during cleanup finalization')
        if self.checkpoint()['status'] == 'BLOCKED':
            raise ValueError('portable checkpoint unavailable; retain execution receipts before cleanup')
        self.remove_superseded_artifacts()
        self.remove_local_execution_state()

    def instruction_boundary(self):
        """Reconcile returned work under its old inputs, without starting a worker."""
        self.reconcile_worker()
        pending = [a for a in self.state['attempts'] if a['status'] in ('reserved', 'failed')]
        if pending:
            attempt = pending[-1]
            if len(pending) != 1 or attempt['stage'] not in STAGES:
                raise ValueError('instruction upgrade needs a reconciled stage boundary; '
                                 'resume the pinned delivery to reconcile ' + attempt['stage'])
            # stage(reconcile=True) can only consume this exact reserved response.
            # A missing/failed receipt exits here, before dispatch could be called.
            self.receipt(attempt)
            self.stage(attempt['stage'], reconcile=True)
        last = self.state['attempts'][-1] if self.state['attempts'] else None
        if last and last['stage'] in ('implementation', 'repair') and last['status'] == 'complete':
            self.check_report_rejection(last)
            report = self.read_report(last['stage'])
            generation = self.state['local_git_generations'][-1]
            if (generation.get('source_attempt') or {}).get('attempt_id') != last['id']:
                self.capture(last['stage'])
            if report['status'] in ('IMPLEMENTED', 'REPAIRED'):
                self.state['implementation_complete'] = True
            history = self.state.get('recovery_history', [])
            if last['stage'] == 'repair' and history and history[-1]['status'] == 'reserved':
                self.finish_recovery(history[-1], report)
            self.save()
        if (any(a['status'] not in ('complete', 'retired') for a in self.state['attempts']) or
                any(entry['status'] == 'reserved' for entry in self.state.get('recovery_history', []))):
            raise ValueError('instruction upgrade needs completed worker and recovery receipts; '
                             'resume the pinned delivery to reconcile them first')
        if self.pending_diagnosis() is not None:
            raise ValueError('instruction upgrade needs the retained recovery decision reconciled; '
                             'resume the pinned delivery to consume that decision first')
        self.current()
        for name in self.state.get('reports', {}):
            self.read_report(name)

    def upgrade_instructions(self, authorize_upgrade=False, new_bundle=None):
        """Preview or adopt compatible instructions while preserving completed work."""
        if authorize_upgrade:
            self.reconcile_extension()
            self.reconcile_agreement()
            self.reconcile_instruction_upgrade()
        if not self.state.get('instruction_identity'):
            raise ValueError('legacy delivery has no complete pinned instruction inputs; '
                             'restore the original skill installation and resume this work item; '
                             'do not reset state or invent historical protocol bytes')
        old = instructions.load(self.runtime, self.state['instruction_identity'])
        new = new_bundle if new_bundle is not None else instructions.capture(skills(), STAGES)
        instructions.compatible(old, new)
        before_files, after_files = ({row['path']: row['sha256'] for row in version['files']}
                                    for version in (old, new))
        preview = {'status': 'UNCHANGED' if old['identity'] == new['identity'] else 'UPGRADE_AVAILABLE',
                   'from': old['identity'], 'to': new['identity'],
                   'compatibility': new['compatibility'],
                   'changed_inputs': sorted(path for path in before_files.keys() | after_files.keys()
                                            if before_files.get(path) != after_files.get(path)),
                   'work_item': self.work, 'candidate_key': candidate_key(self.state['candidate']),
                   'refreshed_stages': [] if old['identity'] == new['identity'] else ['review', 'proof'],
                   'preserved': 'Agreement, comparison base, candidate, implementation, history, mandate and limits.',
                   'resume': result(self)['resume']}
        if old['identity'] == new['identity']:
            self.current()
            return preview
        if not authorize_upgrade:
            self.current()
            preview['next_action'] = (f'upgrade-instructions {self.work} --authorize-upgrade; '
                                      'no workers launch during adoption, then resume for review and proof')
            return preview
        authority = instruction_upgrade_authority(self.state)
        self.instruction_boundary()
        admission = json.loads((self.runtime / 'admission.json').read_bytes())
        installed = instructions.preserve(self.runtime, new)
        record = {'from': old['identity'], 'to': new['identity'],
                  'transition_id': fs.digest(fs.canonical([
                      'instruction-upgrade/v1', self.state['invocation_id'],
                      old['identity'], new['identity'], len(self.state.get('instruction_history', []))])),
                  'approved_at': now(), 'approval_source': 'Explicit upgrade-instructions --authorize-upgrade invocation',
                  **authority, 'candidate_key': candidate_key(self.state['candidate']),
                  'attempt_count': len(self.state['attempts']), 'refreshed_stages': ['review', 'proof']}
        transition = {'old_admission': admission,
                      'new_admission': admission | {'skills': installed, 'instruction_identity': new['identity']},
                      'record': record}
        # One write-ahead transition, then exact old/new reconciliation. No worker
        # reservation occurs until a later resume has completed this transaction.
        local_save(self.root, self.work, 'runtime/instruction-transition.json', encoded(transition))
        self.reconcile_instruction_upgrade()
        self.checkpoint()
        return preview | {'status': 'UPGRADED', 'transition_id': record['transition_id'],
                          'checkpoint': self.state['checkpoint'],
                          'next_action': 'Resume this delivery; review and proof refresh on the retained candidate.'}

    def reconcile_instruction_upgrade(self):
        path = self.runtime / 'instruction-transition.json'
        if not path.exists():
            return
        transition = json.loads(path.read_bytes())
        if transition.get('complete'):
            return
        old, new, record = (transition[key] for key in ('old_admission', 'new_admission', 'record'))
        if (new != old | {key: new[key] for key in ('skills', 'instruction_identity')} or
                record['from'] != old.get('instruction_identity') or record['to'] != new['instruction_identity']):
            raise ValueError('instruction transition changed unrelated admission fields; preserve and reconcile the journal')
        before, after = (instructions.load(self.runtime, value) for value in (record['from'], record['to']))
        instructions.compatible(before, after)
        if instructions.validate(self.runtime, record['to']) != new['skills']:
            raise ValueError('instruction transition has changed dispatch paths; recover the saved instruction snapshot')
        authority = instruction_upgrade_authority(self.state)
        if any(record.get(key) != value for key, value in authority.items()):
            raise ValueError('instruction transition mandate changed; restore its covering mandate before resume')
        admitted = json.loads((self.runtime / 'admission.json').read_bytes())
        if (admitted not in (old, new) or
                any(self.state.get(key) not in (old.get(key), new.get(key)) for key in old)):
            raise ValueError('conflicting instruction-transition admission; preserve both versions and reconcile')
        history = self.state.setdefault('instruction_history', [])
        existing = next((entry for entry in history if entry['transition_id'] == record['transition_id']), None)
        if existing is not None and existing != record:
            raise ValueError('instruction transition conflicts with its retained history')
        expected_id = fs.digest(fs.canonical(['instruction-upgrade/v1', self.state['invocation_id'],
                                             record['from'], record['to'],
                                             len(history) - (1 if existing else 0)]))
        if (record['transition_id'] != expected_id or record['attempt_count'] != len(self.state['attempts']) or
                record['candidate_key'] != candidate_key(self.state['candidate']) or
                record['refreshed_stages'] != ['review', 'proof'] or
                any(a['status'] not in ('complete', 'retired') for a in self.state['attempts'])):
            raise ValueError('instruction transition boundary changed; reconcile retained work before resume')
        # Validate the actual source/candidate against whichever exact admission
        # reached disk before an interruption. This shadow performs no writes.
        shadow = Delivery(self.root, self.work, json.loads(json.dumps(self.state)) | admitted)
        shadow.read_only = True
        shadow.current()
        self.state.update(new)
        if existing is None:
            history.append(record)
            self.state['reports'] = {name: value for name, value in self.state.get('reports', {}).items()
                                     if name not in ('review', 'proof')}
            self.state.update(status='RUNNING', blocker=None, ended_at=None)
            for name in ('completed_at', 'ended_epoch', 'final_review', 'final_proof',
                         'final_records_written', 'cleanup_verified_at', 'cleanup_source_identity_sha256', 'cleanup'):
                self.state.pop(name, None)
        self.save()
        local_save(self.root, self.work, 'runtime/admission.json', encoded(new))
        local_save(self.root, self.work, 'runtime/instruction-transition.json', encoded(transition | {'complete': True}))

    def extend(self, args):
        if not args.authorize_extension:
            raise ValueError('extension requires explicit --authorize-extension authority')
        self.timed_source_stable()
        changes = {key: autonomy.limit(getattr(args, name), integer=key in ('dispatches', 'repairs'))
                   for name, key in (('max_dispatches', 'dispatches'), ('max_seconds', 'elapsed_seconds'),
                       ('max_stage_seconds', 'stage_seconds'), ('max_repairs', 'repairs'))
                   if getattr(args, name) is not None}
        if not changes:
            raise ValueError('extension needs at least one explicit limit or unlimited')
        admission = json.loads((self.runtime / 'admission.json').read_bytes())
        limits = self.state['limits'] | changes
        deadline = self.state['deadline']
        if 'elapsed_seconds' in changes:
            deadline = None if changes['elapsed_seconds'] is None else time.time() + changes['elapsed_seconds']
        amended = admission | {'limits': limits, 'deadline': deadline}
        if args.mandate:
            amended['autonomy'] = autonomy.load(args.mandate)
        elif not amended.get('autonomy'):
            amended['autonomy'] = autonomy.local(f'Continue the agreed local delivery in {self.work}, preserving its outcome and binding sources.')
            amended['autonomy']['policy']['approval_source'] = 'Explicit extension of the previously authorized local delivery.'
        record = {'previous_limits': self.state['limits'], 'limits': limits,
                  'previous_deadline': self.state['deadline'], 'deadline': deadline,
                  'approved_at': now(), 'approval_source': 'Explicit extend --authorize-extension invocation',
                  'attempt_count': len(self.state['attempts'])}
        # Save the amendment first; startup reconciles either exact old or amended admission.
        local_save(self.root, self.work, 'runtime/limit-extension.json', encoded({
            'old_admission': admission, 'new_admission': amended, 'record': record}))
        self.reconcile_extension()

    def reconcile_extension(self):
        path = self.runtime / 'limit-extension.json'
        if not path.exists():
            return
        extension = json.loads(path.read_bytes())
        if extension.get('complete'):
            return
        old, new = extension['old_admission'], extension['new_admission']
        if new != old | {k: new[k] for k in ('limits', 'deadline', 'autonomy') if k in new}:
            raise ValueError('limit extension changed unrelated admission fields')
        admitted = json.loads((self.runtime / 'admission.json').read_bytes())
        if admitted not in (old, new) or any(self.state.get(k) not in (old.get(k), new.get(k)) for k in old):
            raise ValueError('conflicting limit-extension admission')
        if new.get('autonomy'):
            autonomy.current(new['autonomy'])
        self.state.update(new)
        history = self.state.setdefault('limit_extensions', [])
        if extension['record'] not in history:
            history.append(extension['record'])
        self.save()
        local_save(self.root, self.work, 'runtime/admission.json', encoded(new))
        local_save(self.root, self.work, 'runtime/limit-extension.json', encoded(extension | {'complete': True}))

    def handoff(self, action, reason):
        decision = 'planning' if action == 'plan-acceptance' else 'routing'
        mandate = self.state.get('autonomy')
        delegated = bool(mandate and decision in mandate['policy']['decisions'])
        self.state['continuation'] = {'action': action, 'work_item': self.work,
                                      'reason': reason, 'delegated': delegated,
                                      'mandate': mandate, 'candidate': identity(self.state['candidate'])}
        self.save()
        if delegated:
            if action == 'plan-acceptance':
                self.replan(reason)
                return
            raise ContinuationRequired('execute delegated ' + action + ' handoff, then resume delivery')
        raise ValueError('decision outside the standing mandate: ' + action + '; ' + reason)

    def diagnose(self, findings, history):
        """Retain and consume one diagnosis; correct malformed output once, never blind retry."""
        self.current()
        base_inputs = self.stage_inputs(self.state['candidate'])
        readiness = self.state.get('task_readiness', {})
        readiness = {key: readiness.get(key) for key in ('attempt_id', 'report_sha256')}
        active = self.state.get('recovery_decision', {})
        basis = {'inputs': base_inputs, 'findings': findings, 'history': history,
                 'receiving_checkpoint': self.state.get('checkpoint_restored_from')}
        if active.get('status') in ('pending', 'diagnosed', 'rejected') and 'readiness' in active:
            original_key = fs.digest(fs.canonical(basis | {'readiness': active['readiness']}))
            if original_key == active['context_sha256']:
                # A newly checked readiness prerequisite does not discard a valid,
                # unconsumed decision. A previously BLOCKED decision can be renewed.
                readiness = active['readiness']
        context_key = fs.digest(fs.canonical(basis | {'readiness': readiness}))
        inputs = base_inputs | {'recovery_context_sha256': context_key}
        last = next((attempt for attempt in reversed(self.state['attempts'])
                     if not attempt['stage'].startswith('preflight-')), None)
        # Older invocations did not bind findings to the diagnosis input. Adopt their
        # exact host response only while it is still the unconsumed final attempt.
        if (last and last['stage'] == 'diagnosis' and last['inputs'] == base_inputs and
                not last.get('recovery_context_sha256')):
            last['recovery_context_sha256'] = context_key
            inputs = base_inputs
        previous = [a for a in self.state['attempts'] if a['stage'] == 'diagnosis' and
                    (a['inputs'].get('recovery_context_sha256') or
                     a.get('recovery_context_sha256')) == context_key]
        self.state['recovery_decision'] = {'context_sha256': context_key, 'findings': findings,
                                            'readiness': readiness, 'status': 'pending'}
        self.save()
        properties = {key: {'type': 'string'} for key in
                      ('status', 'input_identity_json', 'action', 'approach', 'reason',
                       'missing_input', 'expected_result', 'capability_check')}
        properties['strategy_changed'] = {'type': 'boolean'}
        properties['status']['enum'] = ['ACTIONABLE', 'BLOCKED']
        properties['action']['enum'] = ['implementation', 'evidence', 'prerequisite', 'plan-acceptance', 'none']
        schema = {'type': 'object', 'properties': properties,
                  'required': list(properties), 'additionalProperties': False}
        prompt = (f'Read {self.state["skills"]["repair"]["path"]} and its references. '
                  'Diagnose these delivery gaps in a fresh read-only context. '
                  f'Fixed candidate workspace: {self.workspace}; contract: {self.work}. '
                  f'Exact input_identity_json: {json.dumps(inputs)}. '
                  f'Findings: {json.dumps(findings)}. Prior approaches: {json.dumps(history)}. '
                  f'Retained reports under {self.runtime}: {json.dumps(self.state.get("reports", {}))}. '
                  f'Most recent retained diagnosis: {json.dumps(self.state.get("last_diagnosis"))}. '
                  'On a receiving host, retain the prior proposed strategy and findings but freshly check '
                  'the specific capabilities needed here; prior host observations do not establish current '
                  'availability. Reuse the retained investigation instead of repeating unrelated exploration. '
                  'Inspect actual mechanisms and available local inputs. Choose a concrete different approach '
                  'that the implementation/evidence worker can execute, including local prerequisite work. '
                  'Repeated findings require a different method, not another copy of the previous attempt. '
                  'Judge strategy_changed by a materially different method or newly confirmed inputs/capabilities, '
                  'not by different wording. Compare unresolved requirement/source/location identities and '
                  'the entire candidate history: paraphrased findings and returning to an earlier candidate '
                  'do not establish useful progress. Check the actual worker boundary: network denied, approval '
                  'escalation disabled, MCP servers/apps/plugins disabled, and no enclosing-host tools inherited. '
                  'Implementation/repair can write the isolated candidate, but cannot alter protected agreement '
                  'or Git metadata. Diagnosis can write only scratch. Do not propose an unavailable host tool '
                  'or nested model call as worker-executable. For ACTIONABLE, run a safe capability probe and '
                  'print P2P_RECOVERY_CAPABILITY=<observation> only after it establishes the inputs/tools '
                  'needed by the proposed next step. Put that exact output line in capability_check; the '
                  'probe must exit zero. Explain how its observation supports the strategy in reason. '
                  'Do not weaken requirements, fabricate evidence, edit any inputs, or make external effects. '
                  'Use plan-acceptance for a necessary contract reconciliation. BLOCKED requires an exact '
                  'unavailable input or authority and its expected result; mere difficulty, elapsed time, or '
                  'a previous failed attempt is not a blocker. ACTIONABLE requires action, approach, and '
                  'reason, with missing_input and expected_result empty. Return the required JSON.')
        while True:
            last = previous[-1] if previous else None
            if last and last.get('report_validation') == 'rejected':
                if not last.get('report_format_error'):
                    self.check_report_rejection(last)
                if sum(a.get('report_format_error', False) for a in previous) >= 2:
                    self.state['recovery_decision']['status'] = 'rejected'
                    self.save()
                    raise ValueError('recovery diagnosis report is invalid after one format correction: ' +
                                     last['report_error'] + '; retained response: ' +
                                     str(self.runtime / last['report']))
                correction = (' Repair the response format from the retained diagnosis at ' +
                              str(self.runtime / last['report']) + '. Validation error: ' +
                              last['report_error'] + '. Reuse its useful observations and the retained reports; '
                              'do not restart implementation or repeat the full investigation. Return the '
                              'required JSON and substantiate any ACTIONABLE capability in this host receipt.')
                attempt, host = self.dispatch('diagnosis', inputs, prompt + correction, schema=schema)
                previous.append(attempt)
            elif last:
                attempt = last
                # A missing or conflicting receipt remains uncertain. It never earns
                # a correction attempt merely because the controller has restarted.
                host = self.receipt(attempt)
            else:
                attempt, host = self.dispatch('diagnosis', inputs, prompt, schema=schema)
                previous.append(attempt)
            self.current()
            try:
                with self.report_validation(attempt, host):
                    try:
                        report = json.loads(host['message'])
                    except (ValueError, TypeError) as error:
                        raise ReportFormatError('invalid recovery diagnosis JSON: ' + str(error)) from error
                    if (not isinstance(report, dict) or set(report) != set(properties) or
                            any(not isinstance(report[key], bool if field['type'] == 'boolean' else str)
                                for key, field in properties.items()) or
                            report['status'] not in properties['status']['enum'] or
                            report['action'] not in properties['action']['enum'] or not report['reason'].strip()):
                        raise ReportFormatError('invalid recovery diagnosis fields')
                    try:
                        reported_inputs = json.loads(report['input_identity_json'])
                    except ValueError as error:
                        raise ReportFormatError('invalid recovery diagnosis input identity JSON') from error
                    if reported_inputs != attempt['inputs']:
                        raise ValueError('stale recovery diagnosis input identity')
                    self.state['last_diagnosis'] = {'attempt_id': attempt['id'], 'report': report,
                                                    'context_sha256': context_key}
                    if report['status'] == 'BLOCKED':
                        if not report['missing_input'].strip() or not report['expected_result'].strip():
                            raise ReportFormatError('blocked diagnosis must name the unavailable input and expected result')
                    else:
                        if (report['action'] == 'none' or not report['approach'].strip() or
                                report['missing_input'] or report['expected_result']):
                            raise ReportFormatError('recovery diagnosis has no executable approach')
                        check = report['capability_check']
                        observed = [event for event in host['executions']
                                    if check in event.get('aggregated_output', '').splitlines() and
                                    event.get('exit_code') == 0]
                        if (not check.startswith('P2P_RECOVERY_CAPABILITY=') or
                                not check.split('=', 1)[1].strip() or not observed):
                            raise ValueError('recovery needs a successful host-recorded capability check for its next step: ' +
                                             report['approach'])
            except ReportFormatError:
                continue
            except ValueError:
                if attempt.get('report_validation') == 'rejected':
                    self.state['recovery_decision']['status'] = 'rejected'
                    self.save()
                raise
            data = host['message'].encode()
            path = f'attempts/{attempt["id"]}/report.json'
            stored = self.runtime / path
            if stored.exists() and stored.read_bytes() != data:
                raise ValueError('conflicting recovery diagnosis result')
            local_save(self.root, self.work, path, data)
            attempt.update(status='complete', report=path, report_sha256=fs.digest(data))
            self.state['recovery_decision'].update(status='blocked' if report['status'] == 'BLOCKED' else 'diagnosed',
                                                   attempt_id=attempt['id'])
            if report['status'] == 'BLOCKED':
                self.state['task_readiness_invalidated'] = report['missing_input'] + '; expected: ' + report['expected_result']
            self.save()
            if report['status'] == 'BLOCKED':
                raise ValueError('recovery needs ' + report['missing_input'] + '; expected: ' + report['expected_result'])
            return report

    def pending_diagnosis(self):
        decision = self.state.get('recovery_decision')
        if decision:
            return decision['findings'] if decision['status'] in ('pending', 'diagnosed', 'rejected') else None
        # Reconcile pre-upgrade local reservations/completions without requiring a
        # new delivery or reconstructing workflow state from conversation text.
        last = next((attempt for attempt in reversed(self.state['attempts'])
                     if not attempt['stage'].startswith('preflight-')), None)
        if not last or last['stage'] != 'diagnosis' or last['status'] == 'retired':
            return None
        if self.state.get('last_diagnosis', {}).get('report', {}).get('status') == 'BLOCKED':
            return None
        launch_path = self.runtime / 'attempts' / last['id'] / 'launch.json'
        launch = json.loads(launch_path.read_bytes())
        if launch.get('attempt_id') != last['id'] or launch.get('inputs') != last['inputs']:
            raise ValueError('conflicting retained diagnosis context')
        try:
            findings, _ = json.JSONDecoder().raw_decode(launch['prompt'].split('Findings: ', 1)[1])
        except (ValueError, KeyError, IndexError) as error:
            raise ValueError('retained diagnosis is missing its exact recovery findings') from error
        return findings

    def finish_recovery(self, entry, report):
        generation = self.state['local_git_generations'][-1]
        if (generation.get('source_attempt') or {}).get('attempt_id') != self.state['reports']['repair']['attempt_id']:
            self.capture('repair')
        if entry['action'] == 'evidence' and candidate_key(self.state['candidate']) != entry['candidate_before']:
            raise ValueError('evidence-only recovery changed product content')
        entry.update(status='complete', candidate_after=candidate_key(self.state['candidate']),
                     result=report['status'], completed_at=now())
        # Preserve all attempt reports; both current verifier records become historical.
        self.state['reports'] = {k: v for k, v in self.state['reports'].items() if k not in ('review', 'proof')}
        self.save()

    def recovery_obligations(self, findings):
        """Track unresolved promises/locations independently of a verifier's prose."""
        known = set(self.state['requirements'])
        keys = set()
        for phase in ('implementation', 'planning', 'review', 'review_gaps', 'proof_gaps'):
            values = findings.get(phase)
            if not values:
                continue
            named = set()
            for value in values:
                if isinstance(value, dict):
                    source = value.get('source', '')
                    # Line offsets and finding IDs can change after a repair while
                    # the same requirement at the same product seam remains open.
                    location = re.sub(r':\d+(?::\d+)?(?:-\d+)?', '', value.get('location', ''))
                    keys.add(('review', source, value.get('axis', ''), location))
                for requirement in known:
                    if re.search(r'(?<![\w-])' + re.escape(requirement) + r'(?![\w-])', str(value)):
                        named.add(requirement)
            if phase == 'implementation':
                keys.update(('implementation', requirement) for requirement in (named or known))
            elif phase in ('review', 'review_gaps') and not any(isinstance(value, dict) for value in values):
                keys.update(('review-gap', requirement) for requirement in (named or known))
            elif phase == 'planning':
                keys.update(('planning', requirement) for requirement in (named or known))
        unproven = set(findings.get('unproven', []))
        if findings.get('proof_gaps') or unproven:
            keys.update(('proof', requirement) for requirement in (unproven or known))
        if findings.get('missing_input'):
            keys.add(('review-prerequisite',))
        return [list(key) for key in sorted(keys)]

    def partial_recovery_progress(self, findings, history):
        if not history or 'implementation' not in findings:
            return False
        previous = history[-1]
        before = previous.get('findings', {}).get('implementation')
        after = findings['implementation']
        if not before or not after or previous.get('candidate_after') == previous['candidate_before']:
            return False
        known = set(self.state['requirements'])
        def named(gaps):
            rows = [{requirement for requirement in known
                     if re.search(r'(?<![\w-])' + re.escape(requirement) + r'(?![\w-])', gap)}
                    for gap in gaps if isinstance(gap, str)]
            return set().union(*rows) if len(rows) == len(gaps) and all(rows) else set()
        remaining, old = named(after), named(before)
        return bool(remaining and remaining < old)

    def recover(self, findings, proof=None, force_diagnosis=False):
        allowed = self.state['limits'].get('repairs', 1)
        used = sum(a['stage'] == 'repair' for a in self.state['attempts'])
        if allowed is not None and used >= allowed:
            raise ValueError('automatic repair limit exhausted; review/proof gaps remain')
        fingerprint = fs.digest(fs.canonical(findings))
        history = self.state.setdefault('recovery_history', [])
        obligations = self.recovery_obligations(findings)
        current_key = candidate_key(self.state['candidate'])
        completed = [entry for entry in history if entry['status'] in ('complete', 'worker-replaced')]
        cycle = any(entry['candidate_before'] == current_key for entry in completed)
        previous = [entry for entry in history if entry['status'] in ('complete', 'worker-replaced') and
                    (entry['fingerprint'] == fingerprint or
                     (obligations and entry.get('obligations', self.recovery_obligations(entry['findings'])) == obligations) or
                     entry.get('candidate_after') == entry['candidate_before'] == current_key or cycle)]
        if (self.partial_recovery_progress(findings, completed) and not cycle and
                self.state.get('recovery_decision', {}).get('status') not in ('pending', 'diagnosed', 'rejected')):
            force_diagnosis = False
        plan = {'action': 'implementation', 'approach': 'Correct the named implementation and evidence gaps.'}
        if force_diagnosis or previous:
            plan = self.diagnose(findings, history)
            if previous and not plan['strategy_changed']:
                raise ValueError('recovery diagnosis found no new executable strategy: ' + plan['reason'])
            method = lambda value: ' '.join(re.findall(r'\w+', value.casefold()))
            if previous and any(entry['action'] == plan['action'] and
                                method(entry['approach']) == method(plan['approach']) and
                                entry.get('capability_check') == plan.get('capability_check') for entry in completed):
                raise ValueError('recovery diagnosis repeated an exhausted strategy without new capabilities: ' +
                                 plan['approach'])
            if plan['action'] == 'plan-acceptance':
                self.handoff('plan-acceptance', plan['reason'])
                self.state['recovery_decision']['status'] = 'consumed'
                self.save()
                return {'status': 'REPLANNED'}
        policy = self.state.get('autonomy')
        decision = 'evidence' if plan['action'] == 'evidence' else 'repair'
        if policy and decision not in policy['policy']['decisions']:
            raise ValueError('recovery decision outside the standing mandate: ' + decision)
        # An old reserved diagnosis must finish before an upgraded readiness
        # context can launch. Establish that readiness before any new mutator.
        if not self.state.get('preflight_complete') and not self.preflight():
            raise ValueError('recovery is waiting for a retained stage response before task readiness')
        entry = {'fingerprint': fingerprint, 'findings': findings, 'obligations': obligations, 'action': plan['action'],
                 'approach': plan['approach'], 'candidate_before': current_key,
                 'status': 'reserved', 'started_at': now(), 'dispatch_offset': len(self.state['attempts'])}
        if 'capability_check' in plan:
            entry['capability_check'] = plan['capability_check']
            decision = self.state['recovery_decision']
            entry['diagnosis_attempt_id'] = decision['attempt_id']
            decision['status'] = 'consumed'
        history.append(entry)
        self.state['repair_skill'] = 'repair' if proof and proof['status'] != 'PROVEN' else 'implementation'
        self.save()
        report = self.stage('repair')
        self.finish_recovery(entry, report)
        return report

    def run(self):
        self.reconcile_extension()
        self.reconcile_agreement()
        self.reconcile_instruction_upgrade()
        self.reconcile_worker()
        # Mutating workers can return before the controller saves their new generation.
        # Validate their exact recorded receipt, never launch them a second time.
        last = self.state['attempts'][-1] if self.state['attempts'] else None
        history = self.state.get('recovery_history', [])
        if last and last['stage'] != 'diagnosis' and last.get('report_validation') == 'rejected':
            if last['stage'] in ('implementation', 'repair'):
                generation = self.state['local_git_generations'][-1]
                if (generation.get('source_attempt') or {}).get('attempt_id') != last['id']:
                    self.timed_source_stable()
                    self.capture(last['stage'])
                    self.save()
            self.check_report_rejection(last)
        if last and last['stage'] in ('implementation', 'repair') and last['status'] != 'retired':
            name = last['stage']
            if (name == 'implementation' and last['status'] == 'complete'
                    and name not in self.state.get('reports', {})
                    and self.state.get('implementation_slice_version') == 1
                    and any(item['attempt_id'] == last['id']
                            for item in self.state.get('implementation_slices', []))):
                # The previous VERIFIED/PARTIAL slice was checkpointed and its
                # current report slot deliberately freed. Reuse its exact
                # generation, not a stale report or another implementation call.
                self.timed_source_stable()
                slices.verify_retained(self.state, self.runtime, self.receipt)
                report = {'status': 'PARTIAL'}
            elif last['status'] in ('reserved', 'failed'):
                report = self.stage(name, reconcile=True)
            else:
                self.timed_source_stable()
                report = self.read_report(name)
            generation = self.state['local_git_generations'][-1]
            if (generation.get('source_attempt') or {}).get('attempt_id') != last['id']:
                self.capture(name)
            if report['status'] in ('IMPLEMENTED', 'REPAIRED'):
                self.state['implementation_complete'] = True
            if name == 'repair' and history and history[-1]['status'] == 'reserved':
                self.finish_recovery(history[-1], report)
            self.save()
        self.current()
        ready = self.preflight()
        if last and last['stage'] in ('review', 'proof') and last['status'] in ('reserved', 'failed'):
            self.stage(last['stage'])
            self.state['status'] = 'RUNNING'
            self.save()
            if not ready:
                self.preflight()
        pending_findings = self.pending_diagnosis()
        if pending_findings is not None:
            proof = self.read_report('proof') if 'proof' in self.state.get('reports', {}) else None
            self.recover(pending_findings, proof, force_diagnosis=True)
        while True:
            while not self.state.get('implementation_complete'):
                if 'repair' in self.state.get('reports', {}):
                    report = self.read_report('repair')
                elif 'implementation' in self.state.get('reports', {}):
                    report = self.read_report('implementation')
                else:
                    report = self.stage('implementation')
                    self.capture('implementation')
                if (report['status'] == 'PARTIAL' and self.state.get('implementation_slice_version') == 1
                        and self.state.get('implementation_slices')
                        and self.state['implementation_slices'][-1]['slice']['outcome'] == 'VERIFIED'):
                    # Checkpoint already verified slice; dispatch the next
                    # meaningful slice rather than diagnosing a failed worker.
                    self.state['reports'].pop('implementation', None)
                    self.save()
                    self.checkpoint()
                    continue
                if report['status'] not in ('IMPLEMENTED', 'REPAIRED'):
                    report = self.recover({'implementation': report['gaps']}, force_diagnosis=True)
                if report['status'] in ('IMPLEMENTED', 'REPAIRED'):
                    self.state['implementation_complete'] = True
                self.save()
                self.checkpoint()
            if self.state.get('implementation_slice_version') == 1:
                slices.verify_retained(self.state, self.runtime, self.receipt)
            if 'review' not in self.state.get('reports', {}):
                self.stage('review')
            review = self.read_report('review')
            if review['status'] == 'BLOCKED':
                if self.state['status'] == 'BLOCKED' and not any(
                        a['stage'] in ('diagnosis', 'planning', 'planning-audit') and
                        a['status'] in ('reserved', 'failed') for a in self.state['attempts']):
                    self.state['reports'].pop('review')
                    self.save()
                    review = self.stage('review')
                if review['status'] == 'BLOCKED':
                    if not self.state.get('autonomy'):
                        raise ValueError('review BLOCKED: missing input/command: ' + review['missing_input'] +
                                         '; expected result: ' + review['expected_result'])
                    self.recover({'review': review['gaps'], 'missing_input': review['missing_input'],
                                  'expected_result': review['expected_result']}, force_diagnosis=True)
                    continue
            if any(item['handoff'] == 'plan-acceptance' for item in review.get('findings', [])):
                if self.state.get('autonomy'):
                    reason = json.dumps(review['findings'])
                    if any(entry.get('reason') == reason for entry in self.state.get('agreement_history', [])):
                        self.recover({'planning': review['findings']}, force_diagnosis=True)
                    else:
                        self.handoff('plan-acceptance', reason)
                    continue
                raise ValueError('review requires plan-acceptance before automatic repair')
            if 'proof' not in self.state.get('reports', {}):
                self.stage('proof')
            proof = self.read_report('proof')
            if review['status'] == 'REVIEWED' and proof['status'] == 'PROVEN' and not review['gaps'] and not proof['gaps']:
                self.complete()
                return
            self.recover({'review': review.get('findings', []), 'review_gaps': review['gaps'],
                          'proof_gaps': proof['gaps'], 'unproven': [row['id'] for row in proof['requirements']
                                                               if row['verdict'] != 'proven']}, proof)

    def reconcile_worker(self):
        """Only a confirmed terminated worker can be replaced; uncertain launches stay blocked."""
        if not self.state.get('autonomy'):
            return
        pending = [a for a in self.state['attempts'] if a['status'] in ('reserved', 'failed')]
        if not pending:
            return
        attempt = pending[-1]
        path = self.runtime / 'attempts' / attempt['id'] / 'exit.json'
        if not path.is_file():
            return  # receipt() will report uncertainty; never launch a duplicate worker.
        end = json.loads(path.read_bytes())
        events = path.parent / 'events.jsonl'
        if (end.get('attempt_id') != attempt['id'] or end.get('inputs') != attempt['inputs'] or
                end.get('event_sha256') != fs.digest(events.read_bytes())):
            raise ValueError('conflicting terminated-worker receipt')
        extended = any(attempt in self.state['attempts'][:entry['attempt_count']]
                       for entry in self.state.get('limit_extensions', []))
        if end.get('outcome') != 'stalled' and not (extended and end.get('outcome') == 'interrupted'):
            return  # Explicit deadlines, cancellation, and invalid reports are not idle watchdogs.
        self.timed_source_stable()
        attempt.update(status='retired', outcome=end['outcome'], finished=end['finished'],
                       elapsed_seconds=end['elapsed_seconds'], exit_code=end['exit_code'])
        if attempt['stage'] in ('implementation', 'repair'):
            self.capture(attempt['stage'])
            self.state['reports'] = {k: v for k, v in self.state['reports'].items() if k not in ('review', 'proof')}
            for entry in self.state.get('recovery_history', [])[-1:]:
                if entry['status'] == 'reserved':
                    entry.update(status='worker-replaced', candidate_after=candidate_key(self.state['candidate']))
        self.state.setdefault('worker_recovery', []).append({'attempt_id': attempt['id'],
                                                            'stage': attempt['stage'], 'reason': 'confirmed worker termination; idle watchdog or authorized limit extension'})
        self.save()

    def planning_actor(self, stage, skill, inputs, prompt, fields):
        schema = {'type': 'object', 'properties': fields, 'required': list(fields), 'additionalProperties': False}
        prompt += (' Standing local mandate: ' + json.dumps(self.state['autonomy']['policy']) +
                   '. Return exactly the required JSON. Exact input_identity_json must encode ' + json.dumps(inputs) +
                   '. Candidate, contract, source and Git metadata are read-only. Only scratch checks are permitted. '
                   'No external effects. The controller saves your exact response and owns adoption.')
        attempt, host = self.dispatch(stage, inputs, f'Read {skill["path"]} and its references. ' + prompt, schema=schema)
        self.current()
        with self.report_validation(attempt, host):
            report = json.loads(host['message'])
            if (not isinstance(report, dict) or set(report) != set(fields) or
                    json.loads(report.get('input_identity_json', '{}')) != inputs):
                raise ValueError('invalid or stale ' + stage + ' result')
            for name, field in fields.items():
                if (field['type'] == 'string' and not isinstance(report[name], str) or
                        field['type'] == 'boolean' and not isinstance(report[name], bool) or
                        'enum' in field and report[name] not in field['enum']):
                    raise ValueError('invalid ' + stage + ' field: ' + name)
        data = host['message'].encode()
        path = f'attempts/{attempt["id"]}/report.json'
        stored = self.runtime / path
        if stored.exists() and stored.read_bytes() != data:
            raise ValueError('conflicting planning result: ' + attempt['id'])
        local_save(self.root, self.work, path, data)
        attempt.update(status='complete', report=path, report_sha256=fs.digest(data))
        self.save()
        return report, attempt

    def replan(self, reason):
        self.current()
        if fs.contract_origin(self.root, fs.work_slug(self.work)):
            raise ContinuationRequired('delegated plan-acceptance requires reconciliation of the retained legacy contract origin before adoption')
        planner, auditor = installed_skill('plan-acceptance'), installed_skill('audit-acceptance')
        inputs = self.stage_inputs(self.state['candidate'])
        fields = {name: {'type': 'string'} for name in ('input_identity_json', 'contract', 'reason')}
        proposal, planning = self.planning_actor('planning', planner, inputs,
            f'Reconcile {self.work} in {self.workspace} with its binding sources. Finding: {reason}. '
            'Standing mandate delegates acceptance planning while preserving the agreed outcome. '
            'Return the full proposed contract text in contract. Preserve the intended outcome, all binding '
            'links, every existing requirement ID and promise, exclusions and inherited constraints. '
            'Use the next contract revision and document the correction. Do not weaken or remove a requirement '
            'to make proof pass. You propose text; you do not approve or mutate it.', fields)
        data = proposal['contract'].encode('utf-8')
        new_contract, requirements = parse_contract(data)
        old = self.state['contract']
        binding_lines = lambda text: [line for line in fs.document_lines(text)
                                     if re.match(r'^(Source:|Parent:|Parent contract:|Intended outcome:)', line)]
        if (new_contract['source'] != old['source'] or new_contract['revision'] != 'v' + str(int(old['revision'][1:]) + 1) or
                not set(self.state['requirements']) <= set(requirements) or
                binding_lines(new_contract['content']) != binding_lines(old['content'])):
            raise ValueError('planning proposal changed the outcome, binding links, requirement IDs or revision sequence')
        proposal_path = local_save(self.root, self.work, f'runtime/planning/{planning["id"]}/contract.md', data)
        audit_inputs = inputs | {'proposed_contract_sha256': new_contract['sha256']}
        fields = {name: {'type': 'boolean'} for name in
                  ('preserves_outcome', 'preserves_constraints', 'source_reconciled', 'requirements_complete')}
        fields.update(input_identity_json={'type': 'string'}, reason={'type': 'string'})
        audit, auditing = self.planning_actor('planning-audit', auditor, audit_inputs,
            f'Independently audit the proposed contract at {proposal_path} against the existing contract '
            f'{self.workspace / self.work}, its full binding sources and this finding: {reason}. '
            'Check that all old promises and constraints survive, source promises are covered, and the new '
            'seams can establish the complete outcome. Return honest booleans for each named condition and '
            'a substantive reason. Standing authority permits source-preserving planning; the audit must '
            'reject a product change, weakened acceptance, or an unexplained scope expansion.', fields)
        if not audit['reason'].strip() or not all(audit[name] for name in fields if fields[name]['type'] == 'boolean'):
            raise ValueError('independent planning audit rejected autonomous adoption: ' + audit['reason'])
        admission_path = self.runtime / 'admission.json'
        admission = json.loads(admission_path.read_bytes())
        targets = []
        for target in dict.fromkeys((fs.safe(self.root, self.work), self.item, self.workspace / self.work)):
            before = target.read_bytes()
            if fs.digest(before) != old['sha256']:
                raise ValueError('agreement changed before delegated adoption')
            targets.append({'path': str(target), 'before': base64.b64encode(before).decode(),
                            'after': base64.b64encode(data).decode()})
        transition = {'status': 'pending', 'old_admission': admission,
                      'new_admission': admission | {'contract': new_contract, 'requirements': requirements},
                      'targets': targets, 'planner': planning['id'], 'audit': auditing['id'], 'reason': reason,
                      'approval_source': self.state['autonomy']['policy']['approval_source']}
        local_save(self.root, self.work, 'runtime/agreement-transition.json', encoded(transition))
        self.reconcile_agreement()
        self.preflight()

    def reconcile_agreement(self):
        path = self.runtime / 'agreement-transition.json'
        if not path.exists():
            return
        transition = json.loads(path.read_bytes())
        if transition['status'] == 'complete':
            return
        old, new = transition['old_admission'], transition['new_admission']
        if new != old | {'contract': new['contract'], 'requirements': new['requirements']}:
            raise ValueError('agreement transition changed unrelated admission authority')
        expected_targets = {str(p) for p in (fs.safe(self.root, self.work), self.item, self.workspace / self.work)}
        if {t['path'] for t in transition['targets']} != expected_targets:
            raise ValueError('agreement transition has unexpected destinations')
        if transition['approval_source'] != self.state['autonomy']['policy']['approval_source']:
            raise ValueError('agreement transition approval source changed')
        autonomy.current(self.state['autonomy'])
        if 'planning' not in self.state['autonomy']['policy']['decisions']:
            raise ValueError('agreement adoption outside the standing mandate')
        admission_path = self.runtime / 'admission.json'
        admitted = json.loads(admission_path.read_bytes())
        if admitted not in (transition['old_admission'], transition['new_admission']):
            raise ValueError('conflicting agreement-transition admission')
        # Reconcile only exact old/new bytes; preserve concurrent human changes.
        for target in transition['targets']:
            before, after = (base64.b64decode(target[name], validate=True) for name in ('before', 'after'))
            proposed, requirements = parse_contract(after)
            if fs.digest(before) != old['contract']['sha256'] or proposed != new['contract'] or requirements != new['requirements']:
                raise ValueError('agreement transition bytes do not match admission')
            actual = Path(target['path']).read_bytes()
            if actual not in (before, after):
                raise ValueError('agreement changed during delegated adoption: ' + target['path'])
        for name in ('planner', 'audit'):
            attempt = next(a for a in self.state['attempts'] if a['id'] == transition[name])
            host = self.receipt(attempt)
            data = (self.runtime / attempt['report']).read_bytes()
            if fs.digest(data) != attempt['report_sha256'] or host['message'].encode() != data:
                raise ValueError('delegated planning receipt changed or lost')
            report = json.loads(data)
            if name == 'planner' and report.get('contract') != new['contract']['content']:
                raise ValueError('planning receipt differs from proposed agreement')
            if name == 'audit' and (not all(report.get(k) is True for k in
                    ('preserves_outcome', 'preserves_constraints', 'source_reconciled', 'requirements_complete')) or
                    json.loads(report['input_identity_json']).get('proposed_contract_sha256') != new['contract']['sha256']):
                raise ValueError('agreement transition lacks passing independent audit')
        for target in transition['targets']:
            before, after = (base64.b64decode(target[name], validate=True) for name in ('before', 'after'))
            destination = Path(target['path'])
            archive = destination.parent / 'history' / fs.digest(before) / destination.name
            archive.parent.mkdir(parents=True, exist_ok=True)
            if archive.exists() and archive.read_bytes() != before:
                raise ValueError('conflicting contract history')
            fs.atomic_write(archive, before, ignored_root=self.root)
            fs.atomic_write(destination, after, ignored_root=self.root)
        self.state.update(transition['new_admission'])
        local_save(self.root, self.work, 'runtime/admission.json', encoded(transition['new_admission']))
        self.state['reports'] = {}
        self.state['implementation_complete'] = False
        self.state.pop('continuation', None)
        history = self.state.setdefault('agreement_history', [])
        adoption = {
            'old_sha256': transition['old_admission']['contract']['sha256'],
            'new_sha256': transition['new_admission']['contract']['sha256'],
            'planner': transition['planner'], 'audit': transition['audit'],
            'reason': transition['reason'],
            'planner_report_sha256': next(a['report_sha256'] for a in self.state['attempts'] if a['id'] == transition['planner']),
            'audit_report_sha256': attempt['report_sha256'], 'audit_report': report,
            'audit_session_id': attempt['session_id'],
            'approval_source': transition['approval_source']}
        if adoption not in history:
            history.append(adoption)
        if self.state['candidate']['work_item_sha256'] != transition['new_admission']['contract']['sha256']:
            self.capture('planning-audit')
        self.save()
        transition['status'] = 'complete'
        local_save(self.root, self.work, 'runtime/agreement-transition.json', encoded(transition))


def create(root, args, invocation_started_epoch=None, *, live_evaluation=False):
    agreement, requirements = contract(root, args.work)
    if not args.authorize_local:
        raise ValueError('local agent-stage authority missing; run requires --authorize-local')
    if args.hard_cost_cap is not None:
        raise ValueError('unsupported capability: no enforceable hard monetary cap')
    mandate = autonomy.load(args.mandate) if getattr(args, 'mandate', None) else autonomy.local(
        f'Deliver the complete agreed outcome in {args.work}, preserving its sources and exclusions.')
    if 'implementation' not in mandate['policy']['decisions']:
        raise ValueError('standing mandate does not delegate implementation')
    if platform.system() != 'Darwin':
        raise ValueError('unsupported host: Codex CLI on macOS required')
    executable = shutil.which('codex')
    if not executable:
        raise ValueError('unsupported host: codex executable missing')
    try:
        version = subprocess.run([executable, '--version'], capture_output=True, text=True,
                                  timeout=10, check=True).stdout.strip()
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as error:
        raise ValueError('unsupported host: codex version probe failed or timed out') from error
    if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', args.comparison_base):
        raise ValueError('comparison base must be an explicit full commit SHA')
    base = fs.full_commit(root, args.comparison_base)
    decision = routing(root, args.work, args.destination)
    if base != decision['target_tip']:
        raise ValueError('destination ' + decision['destination'] + ' is currently at ' + decision['target_tip'] +
                         '; requested comparison base ' + base + ' is stale; start a new delivery with --comparison-base ' + decision['target_tip'])
    records = routing_records(root, decision, args.work)
    installed = skills()
    instruction_bundle = instructions.capture(installed, STAGES)
    fs.check_index(root)
    current = fs.snapshot(root)
    head = fs.full_commit(root, 'HEAD')
    committed = fs.snapshot(root, head)
    old, new = ({e['path']: e for e in entries} for entries in (committed, current))
    dirty = {p for p in old.keys() | new.keys() if old.get(p) != new.get(p)}
    fs.prepare_execution(root, args.work)
    inputs = agreement_bindings(root, args.work)
    localize_agreement(root, args.work, inputs)
    agreement_paths = sorted({args.work, *imported_issue_sources(root, args.work)})
    agreements = {args.work} | {entry['path'] for entry in inputs}
    slug = fs.work_slug(args.work)
    origin = fs.contract_origin(root, slug)
    if origin is not None:
        fs.verify_contract_origin(root, slug, origin)
        agreements.update((origin['path'], f'.p2p/work/{slug}/contract-origin.json'))
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
    starting = base
    manifest = {e['path']: e for e in fs.snapshot(root, starting)}
    comparison = {e['path']: e for e in fs.snapshot(root, base)}
    for path in excluded:
        if path in comparison:
            manifest[path] = comparison[path]
        else:
            manifest.pop(path, None)
    for path in agreements:
        source = fs.safe(root, path)
        if source.is_file():
            entry = next((entry for entry in current if entry['path'] == path), None)
            if entry is None:
                data = source.read_bytes()
                entry = {'path': path, 'mode': '100755' if source.stat().st_mode & 0o111 else '100644',
                         'type': 'file', 'content_base64': base64.b64encode(data).decode()}
            manifest[path] = entry
        else:
            local_input = fs.safe(agreement_root(root, args.work), path)
            if not local_input.is_file():
                raise ValueError('agreement input missing from repo-local storage: ' + path)
            manifest[path] = {'path': path, 'mode': '100644', 'type': 'file',
                              'content_base64': base64.b64encode(local_input.read_bytes()).decode()}
    _, directory = delivery_paths(root, args.work)
    local = local_directory(root, args.work)
    repository_id = Path(execution_directory(root, args.work)).parent.name
    runtime = execution_runtime(root, args.work)
    if runtime.exists():
        raise ValueError('local runtime exists without an active delivery record; preserve it and reconcile admission')
    require_repo_local_ignored(root, runtime)
    runtime.mkdir(parents=True)
    installed = instructions.preserve(runtime, instruction_bundle)
    repository = runtime / 'repository.git'
    require_repo_local_ignored(root, repository)
    subprocess.run(['git', 'init', '--bare', '--quiet', str(repository)], check=True)
    result = subprocess.run(['git', '-C', str(repository), 'fetch', '--no-tags', '--depth=1',
                             str(root), base], capture_output=True)
    if result.returncode:
        raise ValueError('isolated exact-base fetch failed: ' + result.stderr.decode())
    base_manifest = fs.snapshot(repository, base)
    base_tree_key = fs.snapshot_key(base_manifest)
    base_tree = git_generation_tree(repository, base_manifest)
    local_base_ref = f'refs/p2p/{fs.work_slug(args.work)}/comparison-base'
    ref = subprocess.run(['git', '-C', str(repository), 'show-ref', '--verify', '--quiet', local_base_ref])
    if ref.returncode == 0:
        raise ValueError('local Git comparison-base ref already exists: ' + local_base_ref)
    if ref.returncode != 1:
        raise ValueError('cannot inspect local Git comparison-base ref: ' + local_base_ref)
    local_base = subprocess.run(['git', '-C', str(repository), '-c', 'user.name=Promise-to-Proof',
                                 '-c', 'user.email=p2p@localhost', 'commit-tree', base_tree,
                                 '-m', f'P2P product-only base for {args.work}'],
                                capture_output=True, text=True)
    if local_base.returncode:
        raise ValueError('local Git product-only base commit failed: ' + local_base.stderr.strip())
    local_base_commit = local_base.stdout.strip()
    fs.git(repository, 'update-ref', local_base_ref, local_base_commit)
    local_git_base = {'repository_id': repository_id, 'source_commit': base,
                      'source_tree': fs.git(repository, 'rev-parse', base + '^{tree}').decode().strip(),
                      'local_commit': local_base_commit, 'tree': base_tree,
                      'tree_key': base_tree_key, 'ref': local_base_ref}
    local_save(root, args.work, 'runtime/base-tree-key', (base_tree_key + '\n').encode())
    previous_records = {}
    for name in ('candidate.json', 'delivery.json', 'review.md', 'proof.md'):
        old = directory / name
        if old.is_file():
            data = old.read_bytes()
            local_save(root, args.work, 'runtime/previous-records/' + name, data)
            previous_records[name] = fs.digest(data)
    workspace = runtime / 'workspace'
    materialize(workspace, sorted(manifest.values(), key=lambda e:e['path']), ignored_root=root)
    materialize(workspace, records, ignored_root=root)
    git_pointer = workspace / '.git'
    require_repo_local_ignored(root, git_pointer)
    git_pointer.write_text('gitdir: ' + str(repository) + '\n')
    fs.git(workspace, 'config', '--local', 'core.bare', 'false')
    fs.git(workspace, 'update-ref', '--no-deref', 'HEAD', starting)
    fs.git(workspace, 'read-tree', starting)
    fs.workspace_access(workspace, local)
    # Git metadata is outside every worker writable root; never shared with source.
    deadline_started_epoch = time.time()
    state = {'schema': 'promise-to-proof/delivery/v1', 'policy': POLICY, 'invocation_id': str(uuid.uuid4()),
             'status': 'RUNNING', 'blocker': None, 'work_item': args.work, 'comparison_base': base,
             'contract': agreement, 'requirements': requirements, 'binding_inputs': inputs,
             'coverage_format_version': 2, 'implementation_slice_version': 1,
             'implementation_slices': [],
             'agreement_paths': agreement_paths,
             'source_tree_key': fs.snapshot_key(current), 'source_head': head,
             'source_index_sha256': fs.digest(fs.git(root, 'ls-files', '--stage', '-z')),
             'source_product_index_sha256': fs.product_index_sha256(root),
             'excluded_dirty': sorted(excluded), 'skills': installed,
             'instruction_identity': instruction_bundle['identity'], 'instruction_history': [],
             'routing': decision, 'routing_records': records, 'starting_commit': starting,
             'base_tree_key': base_tree_key,
             'local_git_base': local_git_base, 'local_git_generations': [],
             'previous_records': previous_records,
             'destination_observation': destination_observation(root, decision, base),
             'authority': {'local_stages': True, 'external_effects': False},
             'autonomy': mandate,
             'limits': {'dispatches': args.max_dispatches, 'elapsed_seconds': args.max_seconds,
                        'stage_seconds': args.max_stage_seconds,
                        'repairs': getattr(args, 'max_repairs', None),
                        'worker_idle_seconds': getattr(args, 'worker_idle_seconds', None)},
             'deadline': None if args.max_seconds is None else deadline_started_epoch + args.max_seconds,
             'deadline_started_epoch': deadline_started_epoch, 'started_epoch': invocation_started_epoch or time.time(),
             'started_at': datetime.datetime.fromtimestamp(invocation_started_epoch or time.time(),
                                                              datetime.timezone.utc).isoformat(),
             'ended_at': None, 'resume_count': 0,
             'created': now(), 'repair_used': False, 'recovery_history': [], 'attempts': [], 'reports': {},
             'host': {'name': 'Codex CLI on macOS', 'executable': executable,
                      'version': version,
                      'hard_monetary_cap': 'unsupported', 'cost': 'unknown',
                      'enforced': ['scratch-only verification writes', 'network denied', 'approval escalation disabled',
                                   'isolated configuration', 'dispatch admission', 'durable recovery reservations'],
                      'elapsed_limit': 'admission and process termination; provider billing may continue',
                      'trust': 'controller and OS trusted; no arbitrary same-user tamper resistance'}}
    if live_evaluation:
        state['live_evaluation'] = True
    delivery = Delivery(root, args.work, state)
    local_save(root, args.work, 'runtime/admission.json', encoded({k: state[k] for k in ('policy', 'invocation_id', 'work_item', 'comparison_base', 'contract', 'binding_inputs', 'source_tree_key', 'source_head', 'source_index_sha256', 'source_product_index_sha256', 'excluded_dirty', 'agreement_paths', 'skills', 'instruction_identity', 'routing', 'routing_records', 'starting_commit', 'base_tree_key', 'local_git_base', 'previous_records', 'authority', 'autonomy', 'limits', 'deadline', 'started_at', 'started_epoch', 'deadline_started_epoch', 'host', 'coverage_format_version',
                     'implementation_slice_version',
                     *(['live_evaluation'] if live_evaluation else []))}))
    delivery.save()
    delivery.capture('admission')
    delivery.save()
    return delivery


def controller_running(delivery):
    try:
        with (delivery.local.parent / (delivery.local.name + '.lock')).open('rb') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return True
    except FileNotFoundError:
        pass
    except OSError:
        return None  # Unavailable progress metadata must not hide a delivery blocker.
    return False


def result(delivery):
    state = delivery.state
    attempt = state['attempts'][-1] if state['attempts'] else None
    activity = []
    if attempt:
        for name in ('events.jsonl', 'stderr.txt'):
            path = delivery.runtime / 'attempts' / attempt['id'] / name
            try:
                activity.append(path.stat().st_mtime)
            except OSError:
                pass
    latest = max(activity) if activity else None
    running = controller_running(delivery)
    pending = running and attempt and attempt['status'] == 'reserved' and attempt['stage'] in ('implementation', 'repair')
    completion = delivery.runtime / 'attempts' / attempt['id'] / 'exit.json' if attempt else None
    uncertain = bool(attempt and attempt['status'] == 'reserved' and running is not True)
    status = 'BLOCKED' if uncertain else state['status']
    blocker = state['blocker']
    if uncertain and completion and not completion.is_file():
        blocker = f'uncertain dispatch {attempt["id"]}: missing controller host completion {completion}'
    elif uncertain and completion:
        blocker = f'controller stopped with unreconciled dispatch {attempt["id"]}; resume to reconcile {completion}'
    progress = {'stage': attempt['stage'] if attempt else None,
                'attempt_id': attempt['id'] if attempt else None,
                'status': attempt['status'] if attempt else None,
                'controller_running': running,
                'candidate_validation': 'pending active implementation or repair' if pending else 'not deferred',
                'elapsed_seconds': (max(0, time.time() - attempt['started_epoch']) if attempt['finished'] is None
                                    else attempt['elapsed_seconds']) if attempt else None,
                'deadline': attempt.get('deadline', state['deadline']) if attempt else state['deadline'],
                'last_activity_at': datetime.datetime.fromtimestamp(latest, datetime.timezone.utc).isoformat() if latest is not None else None,
                'last_activity_age_seconds': max(0, time.time() - latest) if latest is not None else None,
                'activity_meaning': 'Log file activity only; not verified useful progress.'}
    value = {'status': status, 'blocker': blocker} | {key: state[key] for key in (
        'invocation_id', 'work_item', 'comparison_base', 'limits', 'repair_used', 'host')} | {
        'routing': state.get('routing'),
        'contract': {name: state['contract'][name] for name in ('source', 'revision', 'sha256')},
        'agreement_paths': state.get('agreement_paths', [delivery.work]),
        'checkpoint_restored_from': state.get('checkpoint_restored_from'),
        'fresh_host_preflight_complete': bool(state.get('preflight_complete')),
        'implementation_complete': state.get('implementation_complete', False),
        'resume_count': state.get('resume_count', 0),
        'parent_has_children': any(line.strip() == '## Children' for line in
                                   fs.document_lines(state['contract']['content'])),
        'autonomy': state.get('autonomy'),
        'instruction_identity': state.get('instruction_identity'),
        'instruction_history': state.get('instruction_history', []),
        'checkpoint': state.get('checkpoint', {'status': 'LOCAL_ONLY', 'blocker': 'portable checkpoint not yet saved'}),
        'continuation': state.get('continuation'),
        'recovery_history': state.get('recovery_history', []),
        'destination_observation': state.get('destination_observation'),
        'completion_scope': ('Acceptance is for the exact candidate against the frozen comparison base; compatibility with the current destination is not established.'
                             if state['status'] == 'REVIEWED_AND_PROVEN' else None),
        'acceptance_boundary': ('Acceptance applies to the exact candidate against its frozen comparison base. '
                                'Compatibility with the current destination has not been established by this delivery.'),
        'progress': (progress | {'candidate_validation': 'verified durable compact identity'}
                     if state.get('cleanup_verified_at') else progress),
        'starting_commit': state.get('starting_commit'),
        'candidate': identity(state['candidate']) if state.get('candidate') else None,
        'candidate_workspace': str(delivery.workspace) if delivery.workspace.exists() else None,
        'reports': ({'review': {'path': str(delivery.directory / 'review.md')},
                     'proof': {'path': str(delivery.directory / 'proof.md')}}
                    if state.get('cleanup_verified_at') else state.get('reports', {})),
        'attempts': [] if state.get('cleanup_verified_at') else state['attempts'],
        'measurement': delivery_measurement(state, delivery.runtime),
        'work_selection': applicability.next_work(state),
        **({'implementation_progress': slices.progress_view(state)}
           if state.get('implementation_slice_version') == 1 else {}),
        'records': str(delivery.directory),
        'local_runtime': str(delivery.runtime) if delivery.runtime.exists() else None,
        'resume': f'python3 {Path(__file__).resolve()} --repo {delivery.root} resume {delivery.work}',
        'cleanup': f'python3 {Path(__file__).resolve()} --repo {delivery.root} cleanup {delivery.work}'}
    return {'human_progress': progress_view.explain(value), **value}


def completed_result(root, work, directory):
    try:
        record = json.loads((directory / 'delivery.json').read_text())
        candidate_path = directory / 'candidate.json'
        review_path, proof_path = directory / 'review.md', directory / 'proof.md'
        candidate_bytes = candidate_path.read_bytes()
        candidate = json.loads(candidate_bytes)
        review, proof = review_path.read_bytes(), proof_path.read_bytes()
        if record.get('schema') != 'promise-to-proof/delivery-record/v1' or record.get('status') != 'REVIEWED_AND_PROVEN':
            raise ValueError('durable completion record is malformed')
        if (record.get('work_item') != work or record.get('candidate_record_sha256') != fs.digest(candidate_bytes) or
                record.get('candidate_key') != candidate_key(candidate) or
                record.get('comparison_base') != candidate.get('comparison_base') or
                record.get('binding_inputs') != candidate.get('binding_inputs') or
                record.get('candidate_changes_sha256') != fs.digest(fs.canonical(candidate.get('changes', []))) or
                record.get('review_sha256') != fs.digest(review) or record.get('proof_sha256') != fs.digest(proof)):
            raise ValueError('durable completion record identity changed or lost')
        item, _ = delivery_paths(root, work)
        agreement, _ = contract(root, work)
        if record.get('autonomy'):
            autonomy.current(record['autonomy'])
        if record.get('contract') != {key: agreement[key] for key in ('source', 'revision', 'sha256')}:
            raise ValueError('durable completion record contract identity changed or lost')
        if issue_source(root, work, agreement['content']) and not record.get('github_record'):
            raise ValueError('issue-backed completion record has no verified GitHub record')
        if (candidate.get('work_item') != work or candidate.get('work_item_sha256') != fs.digest(item.read_bytes()) or
                candidate.get('binding_inputs') != agreement_bindings(root, work)):
            raise ValueError('contract or binding inputs changed since completion')
        retained = record.get('retained_artifacts', [])
        expected_retained = []
        for name, reason in RETAINED_ARTIFACTS.items():
            path = directory / name
            if path.is_file() and not path.is_symlink():
                expected_retained.append({'path': name, 'reason': reason,
                                          'sha256': fs.digest(path.read_bytes())})
        if retained != expected_retained:
            raise ValueError('durable retained-artifact receipts changed or lost')
        if not record.get('cleanup_verified_at') or record.get('cleanup') not in (
                'source checkout unchanged', 'candidate already present in source checkout',
                'source checkout identity verified'):
            raise ValueError('candidate cleanup has not been verified')
        workspace = execution_runtime(root, work) / 'workspace'
        if record.get('cleanup') == 'source checkout unchanged':
            if not workspace.is_dir():
                raise ValueError('retained isolated candidate workspace is missing')
            repository = workspace.parent / 'repository.git'
            if not repository.is_dir() or (workspace / '.git').read_text() != 'gitdir: ' + str(repository) + '\n':
                raise ValueError('retained isolated Git object store is missing or changed')
            recovered = fs.validate(workspace, work, record['comparison_base'],
                                    exclude=record.get('agreement_paths', (work,)))
            if candidate_key(recovered) != record['candidate_key']:
                raise ValueError('retained isolated candidate workspace changed')
        identity_sha = fs.digest(fs.canonical(fs.tree_identity(
            fs.snapshot(root, exclude=record.get('agreement_paths', (work,))))))
        if identity_sha != record.get('cleanup_source_identity_sha256'):
            raise ValueError('source checkout changed after cleanup identity verification')
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError('durable completed delivery unavailable: ' + str(error)) from error
    value = {
        'status': record['status'], 'blocker': None, 'invocation_id': record['invocation_id'],
        'work_item': work, 'comparison_base': record['comparison_base'],
        'candidate': identity(candidate), 'routing': record.get('routing'),
        'contract': record['contract'], 'agreement_paths': record.get('agreement_paths', [work]),
        'implementation_complete': True,
        'parent_has_children': any(line.strip() == '## Children' for line in
                                   fs.document_lines(agreement['content'])),
        'destination_observation': record.get('destination_observation'),
        'completion_scope': 'Acceptance is for the exact candidate against the frozen comparison base; compatibility with the current destination is not established.',
        'acceptance_boundary': 'Acceptance applies to the exact candidate against its frozen comparison base. Compatibility with the current destination has not been established by this delivery.',
        'progress': {'stage': 'complete', 'status': 'complete', 'controller_running': False,
                     'candidate_validation': 'verified durable compact identity'},
        'starting_commit': None, 'reports': {'review': {'path': 'review.md', 'sha256': record['review_sha256']},
                                             'proof': {'path': 'proof.md', 'sha256': record['proof_sha256']}},
        'attempts': [], 'records': str(directory),
        'local_runtime': str(execution_runtime(root, work)) if execution_runtime(root, work).exists() else None,
        'candidate_workspace': (str(workspace) if workspace.is_dir() else None),
        'github_record': record.get('github_record'),
        'cleanup': 'already complete',
        'resume': f'python3 {Path(__file__).resolve()} --repo {root} status {work}',
    }
    return {'human_progress': progress_view.explain(value), **value}


def completed_without_local_runtime(root, work, directory, missing_record):
    runtime = execution_runtime(root, work)
    completed_runtime = ((runtime / 'repository.git').is_dir() and
                         (directory / 'delivery.json').is_file())
    if runtime.exists() and not completed_runtime:
        raise ValueError('local execution state exists but its invocation record is missing')
    if not (directory / 'delivery.json').exists():
        raise ValueError(missing_record)
    return completed_result(root, work, directory)


def _saved_pr_hint(root, work):
    """A saved publication link is only a lookup hint, never proof of a write."""
    local = fs.safe(root, f'.p2p/work/{fs.work_slug(work)}/publication.md')
    if not local.is_file():
        return None
    urls = set(re.findall(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/pull/[1-9][0-9]*',
                          local.read_text(encoding='utf-8')))
    if len(urls) == 1:
        return next(iter(urls))
    if len(urls) > 1:
        return 'ambiguous saved pull-request URLs'
    return None


def _observed_status(root, work, result_value, requested_pr=None):
    """Add read-only current remote observations without modifying saved verdicts."""
    hint = requested_pr if requested_pr is not None else _saved_pr_hint(root, work)
    publication = None
    if hint == 'ambiguous saved pull-request URLs':
        publication = {'status': 'UNVERIFIED', 'verified': False,
                       'reason': 'More than one PR URL appears in the saved publication handoff.'}
    elif hint:
        publication = progress_view.inspect_github_pr(root, result_value, hint)
    result_value['human_progress'] = progress_view.explain(result_value, publication=publication)
    if publication is not None:
        result_value['publication_observation'] = publication
    return result_value


def _human_output(value):
    message = value['human_progress']
    return (message['message'] + '\n\nWhere the code is: ' + message['where_is_the_code'] +
            '\nUser action required: ' + ('yes' if message['requires_user_action'] else 'no') +
            '\nVerified milestones: ' + (' '.join(message['confirmed']) if message['confirmed'] else 'none yet') +
            '\n')


def main(argv=None):
    if sys.version_info < (3, 11):
        print('Python 3.11 or newer is required by the delivery controller.', file=sys.stderr)
        return 2
    invocation_started_epoch = time.time()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default='.')
    commands = parser.add_subparsers(dest='action', required=True)
    for name in ('run', 'resume', 'status', 'cleanup'):
        child = commands.add_parser(name)
        child.add_argument('work')
        if name == 'status':
            child.add_argument('--pr', help='read back the current matching pull request before reporting publication or merge')
            child.add_argument('--human', action='store_true', help='show only the plain-language status; standard JSON remains the default')
        if name == 'run':
            child.add_argument('--comparison-base', required=True)
            child.add_argument('--destination', help='explicit workflow destination for unsliced work')
            child.add_argument('--authorize-local', action='store_true')
            child.add_argument('--exclude-dirty', action='append', default=[])
            child.add_argument('--mandate', help='explicitly selected standing autonomy mandate JSON')
            child.add_argument('--max-dispatches', default=None, help='optional dispatch limit; default unlimited')
            child.add_argument('--max-seconds', default=None,
                               help='optional overall elapsed seconds; default unlimited')
            child.add_argument('--max-stage-seconds', default=None,
                               help='optional seconds per stage; default unlimited')
            child.add_argument('--max-repairs', default=None, help='optional repair limit; default unlimited')
            child.add_argument('--worker-idle-seconds', default=None,
                               help='optional idle-worker watchdog; replaces a confirmed terminated worker, not the delivery')
            child.add_argument('--hard-cost-cap', type=float)
    extension = commands.add_parser('extend', help='explicitly amend limits without losing the invocation or attempt history')
    extension.add_argument('work')
    extension.add_argument('--authorize-extension', action='store_true')
    extension.add_argument('--mandate')
    for flag in ('--max-dispatches', '--max-seconds', '--max-stage-seconds', '--max-repairs'):
        extension.add_argument(flag)
    upgrade = commands.add_parser('upgrade-instructions', help='preview a compatible instruction upgrade; preserve implementation and limits')
    upgrade.add_argument('work')
    upgrade.add_argument('--authorize-upgrade', action='store_true',
                         help='adopt the installed instruction version at a reconciled boundary; starts no workers')
    effect = commands.add_parser('authorize-effect', help='check a standing grant for an exact effect preview; performs no effect')
    effect.add_argument('work')
    effect.add_argument('--action', dest='effect_action', required=True, choices=sorted(autonomy.EFFECTS))
    effect.add_argument('--repository', required=True)
    effect.add_argument('--destination', required=True)
    effect.add_argument('--preview-sha256', required=True)
    preview = commands.add_parser('github-record-preview')
    preview.add_argument('work')
    preview.add_argument('--delivered-commit', required=True)
    preview.add_argument('--pull-request')
    publish = commands.add_parser('github-record-publish')
    publish.add_argument('work')
    publish.add_argument('--delivered-commit', required=True)
    publish.add_argument('--pull-request')
    publish.add_argument('--authorize-comment-sha256')
    github_status = commands.add_parser('github-status')
    github_status.add_argument('--repository', required=True)
    github_status.add_argument('--issue', required=True, type=int)
    args = parser.parse_args(argv)
    delivery = None
    lock = None
    try:
        if args.action == 'run':
            for name in ('max_dispatches', 'max_seconds', 'max_stage_seconds', 'max_repairs', 'worker_idle_seconds'):
                setattr(args, name, autonomy.limit(getattr(args, name), integer=name in ('max_dispatches', 'max_repairs')))
        root = Path(fs.git(Path(args.repo), 'rev-parse', '--show-toplevel').decode().strip()).resolve()
        if args.action == 'github-status':
            output = resolve_github_record(root, args.repository, args.issue)
            print(json.dumps(output, indent=2, ensure_ascii=False))
            return 0
        item, directory = delivery_paths(root, args.work)
        local = local_directory(root, args.work)
        state_path = local / 'delivery.json'
        if args.action == 'authorize-effect':
            if not re.fullmatch(r'[0-9a-f]{64}', args.preview_sha256):
                raise ValueError('effect authorization needs the SHA-256 of the exact saved preview')
            if state_path.is_file():
                delivery = Delivery(root, args.work, json.loads(state_path.read_text()))
                delivery.read_only = True
                delivery.current()
                effect_state = delivery.state
            else:
                completed_result(root, args.work, directory)
                effect_state = json.loads((directory / 'delivery.json').read_bytes())
            mandate = effect_state.get('autonomy')
            if not mandate:
                raise ValueError('no standing effect mandate was admitted')
            grant = autonomy.authorize(mandate, args.effect_action, args.repository, args.destination)
            repositories = {str(root)}
            for remote in fs.git(root, 'remote').decode().splitlines():
                url = fs.git(root, 'remote', 'get-url', remote).decode().strip()
                match = re.fullmatch(r'(?:https://github.com/|git@github.com:)([^/]+/[^/]+?)(?:\.git)?', url)
                if match:
                    repositories.add(match[1])
            if Path(args.repository).is_absolute() and Path(args.repository).resolve(strict=True) == root:
                repositories.add(args.repository)
            if args.repository not in repositories:
                raise ValueError('effect repository does not match this delivery repository')
            if args.effect_action in ('commit', 'push', 'pr-create', 'pr-update', 'pr-ready', 'merge', 'deploy'):
                if effect_state['status'] != 'REVIEWED_AND_PROVEN':
                    raise ValueError('effect requires current full REVIEWED and PROVEN results')
                if delivery:
                    for name, verdict in (('review', 'REVIEWED'), ('proof', 'PROVEN')):
                        report = delivery.read_report(name)
                        if (report['status'] != verdict or report['gaps'] or report.get('findings') or
                                json.loads(report['input_identity_json']) != delivery.stage_inputs(effect_state['candidate'])):
                            raise ValueError('effect requires current full ' + verdict + ' result')
            print(json.dumps({'status': 'AUTHORIZED', 'effect': grant, 'preview_sha256': args.preview_sha256,
                              'mandate_sha256': mandate['sha256'], 'approval_source': mandate['policy']['approval_source'],
                              'candidate': identity(effect_state['candidate']) if delivery else effect_state['candidate_key'],
                              'conditions': 'Existing publication, merge-readiness, deployment and readback requirements still apply; this command performs no effect.'}, indent=2))
            return 0
        if args.action == 'status':
            if not state_path.exists():
                output = completed_without_local_runtime(root, args.work, directory,
                                                          'no delivery invocation exists')
                output = _observed_status(root, args.work, output, getattr(args, 'pr', None))
                print(_human_output(output) if args.human else json.dumps(output, indent=2))
                return 0
            delivery = Delivery(root, args.work, json.loads(state_path.read_text()))
            delivery.read_only = True
            # A live writer legitimately changes the candidate before its next capture.
            progress = result(delivery)['progress']
            pending = progress['candidate_validation'] == 'pending active implementation or repair'
            if pending:
                delivery.timed_source_stable()
            elif delivery.state['status'] == 'REVIEWED_AND_PROVEN':
                delivery.current()
            else:
                delivery.current()
            for name in delivery.state.get('reports', {}):
                delivery.read_report(name)
            output = result(delivery)
            if pending:
                output.update(status='RUNNING', blocker=None)
            output = _observed_status(root, args.work, output, args.pr)
            print(_human_output(output) if args.human else json.dumps(output, indent=2))
            return 0 if output['status'] == 'REVIEWED_AND_PROVEN' else 1
        if args.action in ('run', 'resume') and state_path.exists():
            fs.workspace_access(execution_runtime(root, args.work) / 'workspace', local)
        lock_path = local.parent / (local.name + '.lock')
        require_repo_local_ignored(root, lock_path)
        require_repo_local_ignored(root, lock_path.parent)
        local.parent.mkdir(parents=True, exist_ok=True)
        lock = lock_path.open('a')
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('another controller holds the work-item lock')
        if args.action in ('github-record-preview', 'github-record-publish'):
            if not state_path.exists():
                raise ValueError('no local delivery invocation is available for the GitHub record')
            delivery = Delivery(root, args.work, json.loads(state_path.read_text()))
            delivery.complete(check_source=False)
            preview = issue_record_preview(delivery, args.delivered_commit, args.pull_request)
            if args.action == 'github-record-preview':
                print(json.dumps({key: preview[key] for key in ('repository', 'issue', 'id', 'body', 'sha256')},
                                 indent=2, ensure_ascii=False))
                return 0
            receipt = publish_issue_record(delivery, args.delivered_commit, args.pull_request,
                                           args.authorize_comment_sha256)
            print(json.dumps({'status': 'RECORDED', 'github_record': receipt}, indent=2))
            return 0
        if args.action == 'cleanup' and not state_path.exists():
            output = completed_without_local_runtime(root, args.work, directory,
                                                      'no local candidate workspace is available for cleanup')
            print(json.dumps(output, indent=2))
            return 0
        if state_path.exists():
            delivery = Delivery(root, args.work, json.loads(state_path.read_text()))
            if args.action == 'run':
                requested = {'dispatches': args.max_dispatches, 'elapsed_seconds': args.max_seconds,
                             'stage_seconds': args.max_stage_seconds, 'repairs': args.max_repairs,
                             'worker_idle_seconds': args.worker_idle_seconds}
                if 'autonomy' not in delivery.state:
                    requested.pop('repairs')
                    requested.pop('worker_idle_seconds')
                requested_destination = explicit_destination(root, args.destination)[0] if args.destination else None
                if (not args.authorize_local or args.hard_cost_cap is not None or
                    requested != delivery.state['limits'] or
                    (args.mandate and autonomy.load(args.mandate) != delivery.state.get('autonomy')) or
                    args.comparison_base != delivery.state['comparison_base'] or
                    sorted(args.exclude_dirty) != delivery.state['excluded_dirty'] or
                    (requested_destination and requested_destination != delivery.state['routing']['destination'])):
                    raise ValueError('run cannot change persisted authority, scope, base or limits; use resume')
        elif args.action == 'resume':
            # An already-compacted result is an exact readback, not a new delivery.
            if (directory / 'delivery.json').is_file():
                output = completed_without_local_runtime(root, args.work, directory,
                                                          'durable completed delivery unavailable')
                output['reuse'] = {'status': 'UNCHANGED_COMPLETION',
                                   'new_model_calls': 0, 'new_canonical_writes': 0,
                                   'reason': 'Validated immutable completed delivery records.'}
                print(json.dumps(output, indent=2))
                return 0
            raise ValueError('missing delivery invocation; no effects can be reconciled')
        elif args.action == 'run':
            delivery = create(root, args, invocation_started_epoch)
        if args.action == 'upgrade-instructions':
            if delivery is None:
                raise ValueError('missing active delivery invocation; restore its checkpoint before upgrading instructions')
            delivery.read_only = not args.authorize_upgrade
            output = delivery.upgrade_instructions(args.authorize_upgrade)
            print(json.dumps(output, indent=2))
            return 0
        if args.action == 'extend':
            if delivery is None:
                raise ValueError('missing delivery invocation; nothing to extend')
            delivery.extend(args)
            print(json.dumps({'status': 'EXTENDED', 'limits': delivery.state['limits'],
                              'deadline': delivery.state['deadline'], 'resume': result(delivery)['resume']}, indent=2))
            return 0
        if args.action in ('run', 'resume') and delivery.state.get('status') == 'REVIEWED_AND_PROVEN' and (
                delivery.state.get('preflight_complete') and
                not delivery.state.get('task_readiness_invalidated')):
            # Verify rather than render/rewrite the same authoritative stage
            # reports and portable checkpoint; no session or model call occurs.
            delivery.read_only = True
            reuse = delivery.verified_unchanged_completion()
            output = result(delivery)
            output['reuse'] = reuse
            print(json.dumps(output, indent=2))
            return 0
        if args.action == 'resume':
            delivery.state['resume_count'] = delivery.state.get('resume_count', 0) + 1
            delivery.state['ended_at'] = None
            delivery.save()
        if args.action == 'cleanup':
            delivery.cleanup()
        elif args.action == 'resume' or delivery.state['status'] != 'REVIEWED_AND_PROVEN':
            while True:
                try:
                    delivery.run()
                    break
                except WorkerRestartRequired:
                    continue
        print(json.dumps(result(delivery), indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, UnicodeError, subprocess.SubprocessError) as error:
        message = str(error)
        if delivery:
            if args.action in ('run', 'resume') and delivery.read_only and delivery.state.get('status') == 'REVIEWED_AND_PROVEN':
                # A rejected fast-path readback is NOT a new delivery failure.
                # Never destroy the last accepted immutable verdict or rewrite
                # its receipts to BLOCKED merely because a probe detected drift.
                output = result(delivery)
                output.update(status='BLOCKED', blocker=message,
                              reuse={'status': 'STALE', 'reason': message,
                                     'new_model_calls': 0, 'new_canonical_writes': 0})
                output['human_progress'] = progress_view.explain(output)
                print(json.dumps(output, indent=2))
                return 1
            if args.action == 'upgrade-instructions':
                output = result(delivery)
                output.update(status='BLOCKED', instruction_upgrade_status='BLOCKED',
                              delivery_status=delivery.state['status'], blocker=message)
                print(json.dumps(output, indent=2))
                return 1
            if args.action in ('github-record-preview', 'github-record-publish', 'authorize-effect'):
                output = result(delivery)
                output.update(blocker=message, **{('effect_status' if args.action == 'authorize-effect' else 'github_record_status'): 'BLOCKED'})
                print(json.dumps(output, indent=2))
                return 1
            if args.action == 'cleanup' and delivery.state.get('status') == 'REVIEWED_AND_PROVEN':
                output = result(delivery)
                output.update(blocker=message, cleanup_status='BLOCKED')
                print(json.dumps(output, indent=2))
                return 1
            if args.action != 'status':
                delivery.state.update(status='HANDOFF' if isinstance(error, ContinuationRequired) else 'BLOCKED', blocker=message,
                                      ended_at=delivery.state.get('ended_at') or now())
                delivery.state.setdefault('ended_epoch', time.time())
            if args.action != 'status':
                try:
                    delivery.save()
                    delivery.checkpoint()
                except (ValueError, OSError) as storage:
                    message += '; unable to persist blocker: ' + str(storage)
            output = result(delivery)
            output.update(status=delivery.state['status'] if isinstance(error, ContinuationRequired) else 'BLOCKED', blocker=message)
            output['human_progress'] = progress_view.explain(output)
        else:
            work = getattr(args, 'work', None)
            output = {'status': 'BLOCKED', 'blocker': message, 'work_item': work,
                      'invocation_exists': False,
                      'resume': None}
        output = {'human_progress': progress_view.explain(output), **output}
        print(_human_output(output) if args.action == 'status' and args.human else json.dumps(output, indent=2))
        return 1
    finally:
        if lock is not None:
            lock.close()


if __name__ == '__main__':
    sys.exit(main())
