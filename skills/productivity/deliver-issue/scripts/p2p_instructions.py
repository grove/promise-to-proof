#!/usr/bin/env python3
"""Immutable, portable delivery instructions and their material Markdown imports."""
import base64
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import shlex
from urllib.parse import unquote
import zlib

import p2p_filesystem as fs


SCHEMA = 'promise-to-proof/instruction-bundle/v1'
ENVELOPE_SCHEMA = 'promise-to-proof/instruction-snapshot/v1'
MAX_BUNDLE_BYTES = 4 * 1024 * 1024
MAX_FILES = 256
SHA = re.compile(r'[a-f0-9]{64}\Z')
NAME = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def _identity(value):
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise ValueError('invalid retained instruction identity')
    return value


def _logical(path):
    if (not isinstance(path, str) or not path or '\\' in path or '\x00' in path or
            PurePosixPath(path).is_absolute() or
            any(part in ('', '.', '..') or part.lower() == '.git' for part in path.split('/'))):
        raise ValueError('unsafe instruction dependency path: ' + str(path))
    return path


def _relative(origin, target):
    if not isinstance(target, str) or '\\' in target or '\x00' in target:
        raise ValueError('unsafe instruction dependency: ' + str(target))
    target = unquote(target.split('#', 1)[0])
    if not target or PurePosixPath(target).is_absolute() or re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', target):
        raise ValueError('instruction dependencies must name local files: ' + target)
    return _logical(posixpath.normpath(posixpath.join(posixpath.dirname(origin), target)))


def _dependencies(text):
    """Explicit imports distinguish rules from explanatory links and examples."""
    visible = '\n'.join(fs.document_lines(text))
    declarations = re.findall(r'<!--\s*p2p-instruction-dependencies:\s*(.*?)\s*-->', visible, re.S)
    if len(declarations) > 1:
        raise ValueError('instruction document has multiple dependency declarations')
    if declarations:
        try:
            return sorted(set(shlex.split(declarations[0])))
        except ValueError as error:
            raise ValueError('invalid instruction dependency declaration') from error
    targets = []
    links = re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)', visible)
    links.extend(re.findall(r'^ {0,3}\[[^\]]+\]:\s*(.+)$', visible, re.M))
    for target in links:
        target = target.strip()
        if target.startswith('<') and '>' in target:
            target = target[1:target.index('>')]
        else:
            target = target.split()[0] if target else ''
        if (not target or target.startswith('#') or
                re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('//')):
            continue
        if unquote(target.split('#', 1)[0]).lower().endswith('.md'):
            targets.append(target)
    return sorted(set(targets))


def _compatibility(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        raise ValueError('stage instructions need p2p-instruction-compatibility metadata; retain the previous instructions')
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == '---')
    except StopIteration as error:
        raise ValueError('stage instruction metadata is incomplete') from error
    values, metadata = [], False
    for line in lines[1:end]:
        if line and not line[0].isspace():
            metadata = line.strip() == 'metadata:'
        if (line.startswith('p2p-instruction-compatibility:') or
                metadata and line.startswith('  p2p-instruction-compatibility:')):
            values.append(line.split(':', 1)[1].strip())
    if len(values) != 1 or not NAME.fullmatch(values[0]):
        raise ValueError('stage instructions need one explicit p2p-instruction-compatibility declaration; retain the previous instructions')
    return values[0]


def _checked(bundle):
    fields = {'schema', 'identity', 'compatibility', 'stages', 'files', 'texts'}
    if not isinstance(bundle, dict) or set(bundle) != fields or bundle['schema'] != SCHEMA:
        raise ValueError('unsupported instruction bundle schema; preserve the old instructions')
    _identity(bundle['identity'])
    if (not isinstance(bundle['compatibility'], str) or not NAME.fullmatch(bundle['compatibility']) or
            not isinstance(bundle['stages'], dict) or not bundle['stages'] or
            not isinstance(bundle['files'], list) or not bundle['files'] or len(bundle['files']) > MAX_FILES or
            not isinstance(bundle['texts'], dict)):
        raise ValueError('invalid instruction bundle manifest')
    for sha, text in bundle['texts'].items():
        _identity(sha)
        if not isinstance(text, str) or fs.digest(text.encode('utf-8')) != sha:
            raise ValueError('retained instruction text hash mismatch')
    files = {}
    for row in bundle['files']:
        if not isinstance(row, dict) or set(row) != {'path', 'sha256'}:
            raise ValueError('invalid instruction file entry')
        path, sha = _logical(row['path']), _identity(row['sha256'])
        if path in files or sha not in bundle['texts']:
            raise ValueError('duplicate or missing retained instruction file: ' + path)
        files[path] = sha
    if set(files.values()) != set(bundle['texts']):
        raise ValueError('instruction bundle contains unreferenced text')
    for stage, row in bundle['stages'].items():
        if (not isinstance(stage, str) or not NAME.fullmatch(stage) or not isinstance(row, dict) or
                set(row) != {'name', 'path'} or not isinstance(row['name'], str) or not NAME.fullmatch(row['name'])):
            raise ValueError('invalid instruction stage mapping')
        path = _logical(row['path'])
        if path != 'skills/productivity/' + row['name'] + '/SKILL.md' or path not in files:
            raise ValueError('missing retained stage instructions: ' + stage)
        if _compatibility(bundle['texts'][files[path]]) != bundle['compatibility']:
            raise ValueError('stage instruction compatibility declarations disagree')
    for path, sha in files.items():
        for dependency in _dependencies(bundle['texts'][sha]):
            if _relative(path, dependency) not in files:
                raise ValueError('missing retained instruction dependency: ' + dependency + ' from ' + path)
    payload = {key: value for key, value in bundle.items() if key != 'identity'}
    data = fs.canonical(payload)
    if len(data) > MAX_BUNDLE_BYTES:
        raise ValueError('instruction bundle is too large; preserve local inputs and narrow material imports')
    if fs.digest(data) != bundle['identity']:
        raise ValueError('retained instruction bundle identity mismatch')
    return bundle


def capture(installed, stages):
    """Read the exact installed stage bytes and their declared material imports."""
    if not isinstance(installed, dict) or set(installed) != set(stages) or not stages:
        raise ValueError('installed instruction stages do not match delivery stages')
    files, texts, sources, stage_rows, compatibilities = {}, {}, {}, {}, set()
    pending = []
    for stage, name in stages.items():
        if not isinstance(name, str) or not NAME.fullmatch(name):
            raise ValueError('invalid delivery skill name')
        logical = 'skills/productivity/' + name + '/SKILL.md'
        stage_rows[stage] = {'name': name, 'path': logical}
        pending.append((Path(installed[stage]['path']), logical, stage))
    while pending:
        source, logical, stage = pending.pop()
        _logical(logical)
        try:
            source = source.resolve(strict=True)
            if not source.is_file():
                raise ValueError('instruction dependency is not a file: ' + str(source))
            data = source.read_bytes()
            text = data.decode('utf-8')
        except (OSError, UnicodeError, RuntimeError) as error:
            raise ValueError('missing or unreadable instruction dependency: ' + str(source) + '; restore the exact input before continuing') from error
        sha = fs.digest(data)
        if stage is not None:
            if installed[stage].get('sha256') != sha:
                raise ValueError('installed stage instructions changed during capture: ' + stage)
            compatibilities.add(_compatibility(text))
        if logical in files:
            if files[logical] != sha:
                raise ValueError('conflicting material instruction dependency: ' + logical)
            continue
        files[logical], texts[sha], sources[source] = sha, text, sha
        if len(files) > MAX_FILES or sum(len(value.encode('utf-8')) for value in texts.values()) > MAX_BUNDLE_BYTES:
            raise ValueError('instruction imports exceed the supported bounded snapshot; retain the previous instructions')
        for dependency in _dependencies(text):
            target = _relative(logical, dependency)
            local = unquote(dependency.split('#', 1)[0])
            pending.append((source.parent / local, target, None))
    if len(compatibilities) != 1:
        raise ValueError('stage instruction compatibility declarations disagree')
    for source, sha in sources.items():
        if fs.digest(source.read_bytes()) != sha:
            raise ValueError('material instructions changed during capture: ' + str(source))
    payload = {'schema': SCHEMA, 'compatibility': compatibilities.pop(), 'stages': stage_rows,
               'files': [{'path': path, 'sha256': sha} for path, sha in sorted(files.items())], 'texts': texts}
    return _checked(payload | {'identity': fs.digest(fs.canonical(payload))})


def encode(bundle):
    """Compress instruction text only; candidate data and execution logs stay outside."""
    _checked(bundle)
    envelope = {'schema': ENVELOPE_SCHEMA, 'identity': bundle['identity'], 'encoding': 'zlib+base64',
                'content': base64.b64encode(zlib.compress(fs.canonical(bundle), 9)).decode('ascii')}
    return fs.canonical(envelope) + b'\n'


def decode(data, expected_identity=None):
    try:
        if len(data) > MAX_BUNDLE_BYTES:
            raise ValueError('retained instruction envelope is too large')
        envelope = json.loads(data)
        if (not isinstance(envelope, dict) or set(envelope) != {'schema', 'identity', 'encoding', 'content'} or
                envelope['schema'] != ENVELOPE_SCHEMA or envelope['encoding'] != 'zlib+base64'):
            raise ValueError('unsupported retained instruction envelope')
        _identity(envelope['identity'])
        if expected_identity is not None and envelope['identity'] != _identity(expected_identity):
            raise ValueError('retained instruction envelope identity mismatch')
        packed = base64.b64decode(envelope['content'], validate=True)
        decoder = zlib.decompressobj()
        unpacked = decoder.decompress(packed, MAX_BUNDLE_BYTES + 1)
        if len(unpacked) > MAX_BUNDLE_BYTES or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
            raise ValueError('invalid or oversized compressed instruction snapshot')
        bundle = _checked(json.loads(unpacked))
        if bundle['identity'] != envelope['identity']:
            raise ValueError('retained instruction envelope differs from its bundle')
        return bundle
    except (TypeError, KeyError, UnicodeError, zlib.error) as error:
        raise ValueError('invalid retained instruction snapshot; preserve local recovery inputs') from error


def _runtime(runtime):
    runtime = Path(os.path.abspath(runtime))
    for path in (runtime, *runtime.parents):
        if path.is_symlink():
            raise ValueError('symlink in retained instruction storage: ' + str(path))
    if runtime.exists() and not runtime.is_dir():
        raise ValueError('instruction runtime is not a directory')
    return runtime


def _mapping(runtime, bundle):
    files = {row['path']: row['sha256'] for row in bundle['files']}
    base = fs.safe(runtime, 'instructions/' + bundle['identity'])
    return {stage: {'path': str(fs.safe(base, row['path'])), 'sha256': files[row['path']]}
            for stage, row in bundle['stages'].items()}


def preserve(runtime, bundle):
    """Write once and materialize exact navigable files; never replace conflicting bytes."""
    _checked(bundle)
    runtime = _runtime(runtime)
    identity = bundle['identity']
    target = fs.safe(runtime, 'instructions/' + identity + '.json')
    if target.exists():
        if decode(target.read_bytes(), identity) != bundle:
            raise ValueError('conflicting retained instruction bundle; preserve both inputs')
        envelope = target.read_bytes()
    else:
        envelope = encode(bundle)
    base = fs.safe(runtime, 'instructions/' + identity)
    targets = [(target, envelope)] + [(fs.safe(base, row['path']), bundle['texts'][row['sha256']].encode('utf-8'))
                                     for row in bundle['files']]
    for path, data in targets:
        if path.exists() and (not path.is_file() or path.read_bytes() != data):
            raise ValueError('retained instruction file changed: ' + str(path) + '; restore its exact preserved bytes')
    for path, data in targets:
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            fs.atomic_write(path, data)
    return _mapping(runtime, bundle)


def load(runtime, identity):
    runtime = _runtime(runtime)
    path = fs.safe(runtime, 'instructions/' + _identity(identity) + '.json')
    try:
        return decode(path.read_bytes(), identity)
    except OSError as error:
        raise ValueError('retained instruction snapshot is unavailable: ' + str(path) +
                         '; recover the exact snapshot or its portable checkpoint') from error


def validate(runtime, identity):
    """Verify retained inputs without installation discovery, Git calls or writes."""
    runtime = _runtime(runtime)
    bundle = load(runtime, identity)
    base = fs.safe(runtime, 'instructions/' + identity)
    for row in bundle['files']:
        path = fs.safe(base, row['path'])
        if not path.is_file() or fs.digest(path.read_bytes()) != row['sha256']:
            raise ValueError('retained instruction file changed or is missing: ' + str(path) +
                             '; recover its exact preserved bytes before resuming')
    return _mapping(runtime, bundle)


def compatible(old, new):
    """An explicit common declaration permits transition; it grants no authority."""
    _checked(old)
    _checked(new)
    if old['compatibility'] != new['compatibility']:
        raise ValueError('instruction versions are incompatible (' + old['compatibility'] + ' to ' +
                         new['compatibility'] + '); resume the preserved version or use a supported migration')
    return True
