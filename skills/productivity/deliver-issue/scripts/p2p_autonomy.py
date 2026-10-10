"""Standing delivery mandates. Scope grants authorize effects, never establish proof."""
import hashlib
import json
from pathlib import Path

SCHEMA = 'promise-to-proof/autonomy/v1'
DECISIONS = {'planning', 'sizing', 'routing', 'implementation', 'evidence', 'repair'}
EFFECTS = {'issue-create', 'issue-update', 'issue-comment', 'issue-label',
           'issue-relationship', 'issue-close', 'branch-create', 'commit', 'push', 'pr-create',
           'pr-update', 'pr-ready', 'pr-review-comment', 'pr-review-request-changes', 'merge', 'deploy'}


def limit(value, integer=False):
    """Use JSON null for unlimited; numeric zero remains a deliberate stop."""
    if str(value).lower() in ('none', 'null', 'unlimited', 'infinite', 'inf', 'infinity'):
        return None
    import math
    try:
        number = int(value) if integer else float(value)
        if not math.isfinite(number) or number < 0:
            raise ValueError()
        return number
    except (ValueError, OverflowError):
        raise ValueError('limits must be nonnegative numbers or unlimited')


def validate(policy):
    fields = {'schema', 'objective', 'constraints', 'decisions', 'effects', 'approval_source'}
    if not isinstance(policy, dict) or set(policy) != fields or policy['schema'] != SCHEMA:
        raise ValueError('invalid autonomy mandate schema or fields')
    for name in ('objective', 'approval_source'):
        if not isinstance(policy[name], str) or not policy[name].strip():
            raise ValueError('autonomy mandate needs ' + name)
    for name in ('constraints', 'decisions'):
        values = policy[name]
        if not isinstance(values, list) or any(not isinstance(v, str) or not v.strip() for v in values):
            raise ValueError('invalid autonomy mandate ' + name)
        if len(set(values)) != len(values):
            raise ValueError('duplicate autonomy mandate ' + name)
    if not set(policy['decisions']) <= DECISIONS:
        raise ValueError('unsupported delegated decision')
    if not isinstance(policy['effects'], list):
        raise ValueError('invalid autonomy mandate effects')
    for grant in policy['effects']:
        if (not isinstance(grant, dict) or set(grant) != {'action', 'repository', 'destination'} or
                any(not isinstance(v, str) or not v.strip() for v in grant.values()) or
                grant['action'] not in EFFECTS or
                any(c in grant['repository'] + grant['destination'] for c in '*?[')):
            raise ValueError('effects need a supported action, exact repository and exact destination')
    return policy


def load(path):
    source = Path(path).resolve()
    data = source.read_bytes()
    policy = validate(json.loads(data))
    return {'path': str(source), 'sha256': hashlib.sha256(data).hexdigest(), 'policy': policy}


def local(objective):
    return {'path': None, 'sha256': None, 'policy': {
        'schema': SCHEMA, 'objective': objective,
        'constraints': ['Preserve the agreed outcome, exclusions, and binding inputs.'],
        'decisions': sorted(DECISIONS), 'effects': [],
        'approval_source': 'Invoking run --authorize-local grants local delivery decisions.'}}


def current(record):
    validate(record['policy'])
    if record['path'] and load(record['path']) != record:
        raise ValueError('standing autonomy mandate changed; reconcile before continuing')


def authorize(record, action, repository, destination):
    current(record)
    requested = {'action': action, 'repository': repository, 'destination': destination}
    if requested not in record['policy']['effects']:
        raise ValueError('effect outside the standing mandate: ' + action + ' ' + repository + ' ' + destination)
    return requested
