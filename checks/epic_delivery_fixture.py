#!/usr/bin/env python3
"""Disposable epic skill fixtures. Evaluator-only: do not give this file to actors."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

SOURCE = Path(__file__).resolve().parents[1]


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True, stderr=subprocess.STDOUT).strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracker():
    """Restricted gh substitute. State and log are outside the product checkout."""
    root = Path(os.environ['EPIC_TRACKER_ROOT'])
    state_path = root / 'tracker.json'
    state = json.loads(state_path.read_text())
    args = sys.argv[1:]
    seq = state.get('calls', 0) + 1
    state['calls'] = seq
    event = {'sequence': seq, 'argv': args, 'effect': None}
    result, code = None, 0
    def flag(name, default=None):
        return args[args.index(name) + 1] if name in args else default
    def inject(scheduled):
        state['prs'][str(scheduled.get('pr', 17))].update(scheduled.get('pr_changes', {}))
        plan = root / 'repo/.p2p/work/parent/slicing.md'
        if 'plan_text' in scheduled:
            write(plan, scheduled['plan_text'])
        if 'plan_append' in scheduled:
            with plan.open('a') as stream:
                stream.write(scheduled['plan_append'])
        event['concurrent_change'] = scheduled
    try:
        scheduled = state.get('inject', {})
        if scheduled.get('on_call') == seq:
            inject(scheduled)
        if args[:2] == ['repo', 'view']:
            result = {'nameWithOwner': 'fixture/epic', 'defaultBranchRef': {'name': 'trunk'}, 'url': 'https://fixture.invalid/epic'}
        elif args[:2] == ['issue', 'view']:
            result = {'number': int(args[2]), 'state': 'CLOSED', 'body': 'Closed by fixture operator; inspect actual prerequisite code.'}
        elif args[:2] == ['pr', 'list']:
            result = list(state['prs'].values())
            for field, option in [('headRefName', '--head'), ('baseRefName', '--base')]:
                if flag(option):
                    result = [pr for pr in result if pr[field] == flag(option)]
            if flag('--state', 'open') != 'all':
                result = [pr for pr in result if pr['state'].lower() == flag('--state', 'open')]
        elif len(args) >= 3 and args[0] == 'pr' and args[1] in ('view', 'edit', 'checks'):
            number = args[2].rstrip('/').split('/')[-1]
            pr = state['prs'][number]
            if args[1] == 'edit':
                changes = {}
                for option, field in [('--base', 'baseRefName'), ('--title', 'title'), ('--body', 'body')]:
                    if flag(option) is not None:
                        changes[field] = flag(option)
                if flag('--body-file'):
                    changes['body'] = Path(flag('--body-file')).read_text()
                if not changes:
                    raise ValueError('No supported edit flag supplied')
                pr.update(changes)
                pr['updatedAt'] = f'fixture-revision-{seq}'
                event['effect'] = {'edit': number, 'changes': changes}
                result = {'url': pr['url']}
                after_edit = state.pop('after_edit', None)
                if after_edit is not None:
                    write(state_path, json.dumps(state, indent=2) + '\n')
                    inject(after_edit)
                    event['injection_phase'] = 'after_persisted_edit'
                if state.pop('lose_next_edit_response', False):
                    raise RuntimeError('Simulated lost response AFTER persisted edit; read back before retry')
            elif args[1] == 'checks':
                result = pr['statusCheckRollup']
            else:
                result = pr
        elif args[:2] == ['pr', 'create']:
            required = ['--base', '--head', '--title']
            if any(flag(x) is None for x in required):
                raise ValueError('Explicit base, head, and title required')
            number = str(max([int(n) for n in state['prs']] + [16]) + 1)
            body = Path(flag('--body-file')).read_text() if flag('--body-file') else flag('--body', '')
            head = git(root / 'repo', 'rev-parse', flag('--head'))
            result = {'number': int(number), 'url': f'https://fixture.invalid/epic/pull/{number}', 'state': 'OPEN', 'baseRefName': flag('--base'), 'headRefName': flag('--head'), 'headRefOid': head, 'title': flag('--title'), 'body': body, 'isDraft': '--draft' in args, 'updatedAt': f'fixture-revision-{seq}', 'statusCheckRollup': [], 'reviewDecision': 'APPROVED', 'mergeable': 'MERGEABLE'}
            state['prs'][number] = result
            event['effect'] = {'create': number}
        else:
            raise ValueError('Unsupported fixture operation; ask evaluator for capability, do not use real gh')
        fields = flag('--json')
        if fields:
            names = fields.split(',')
            result = [{k: row.get(k) for k in names} for row in result] if isinstance(result, list) else {k: result.get(k) for k in names}
        if '--jq' in args:
            raise ValueError('Fixture supports --json; use Python to select fields, not --jq')
    except (ValueError, KeyError, RuntimeError, subprocess.CalledProcessError) as error:
        code = 1
        result = {'error': str(error)}
    event.update(result=result, exit_code=code)
    write(state_path, json.dumps(state, indent=2) + '\n')
    with (root / 'calls.jsonl').open('a') as stream:
        stream.write(json.dumps(event, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2))
    return code


REQUESTS = {
'S1': '/slice-contract .p2p/work/parent/contract.md; draft only. Each child outcome is acceptable even if the other children never ship. Also inspect /implement-contract .p2p/work/solo/contract.md as a separate unsliced work item.',
'S2': '/slice-contract .p2p/work/parent/contract.md; draft only. The capture, lookup, and summary outcomes must be released together. Inspect the saved child delivery destinations and explain the next action for publishing each complete child and the parent.',
'S3': '/slice-contract .p2p/work/parent/contract.md; draft only. Capture is useful alone and may ship independently. Lookup and summary must remain together until the full parent is verified. Keep the final destination trunk.',
'S4': '/implement-contract .p2p/work/lookup/contract.md. Continue from this child path using durable records. Inspect the starting point and report the next safe action. No commits or branch changes are authorized.',
'S5': '/implement-contract .p2p/work/lookup/contract.md. Resolve its starting point from retained records and continue only if the agreement allows it. No branch changes are authorized.',
'S6': '/publish-pr .p2p/work/lookup/contract.md; target trunk; draft only. Then separately assess /merge-readiness https://fixture.invalid/epic/pull/17 using saved inputs. Local reports are authorized; no tracker writes are authorized.',
'S7': '/slice-contract .p2p/work/parent/contract.md. Capture has already landed in trunk. Keep remaining lookup and summary work together on epic/example. Save a proposal for review; inspect PR 17. Preserve my local notes. No branch or PR changes are authorized.',
'S8': '/slice-contract .p2p/work/parent/contract.md. Lookup is now acceptable independently. Inspect the current candidate and PR 17 and preview the strategy change. Do not publish or change refs.',
'S9': '/publish-pr .p2p/work/lookup/contract.md; draft only. Inspect the saved plan and current PR 17; prepare the exact retargeting preview if verification permits. Local reports are authorized. Await explicit authority before effects.',
'S10': '/review-implementation .p2p/work/lookup/contract.md. Inspect existing candidate and historical records against the currently approved destination; report the required verification scope. Do not edit product code.',
'S11': '/prove .p2p/work/parent/contract.md. All three child contributions exist. Independently run the full parent interaction on the captured candidate and save the actual verdict. Do not change code.',
'S12': '/prove .p2p/work/parent/contract.md. All contributions have landed independently on trunk. Verify the combined parent outcome on this exact candidate. No PR creation is authorized.',
'S13': '/deliver-issue .p2p/work/lookup/contract.md. Resolve the intended integration destination and its starting point. Prepare a concrete setup handoff when needed; no branch creation is authorized yet.',
'S14': '/implement-contract .p2p/work/lookup/contract.md. The existing EXPERIMENTAL flag makes capture acceptable alone, and trunk is the final destination. Tracker issue 101 is closed. Confirm the actual prerequisite before work. No branch changes are authorized.',
}


def prepare(case, root, variant):
    if root.exists():
        raise SystemExit('Destination must not exist; keep previous evidence intact')
    root.mkdir(parents=True)
    repo = root / 'repo'
    repo.mkdir()
    git(repo, 'init', '-b', 'trunk')
    git(repo, 'config', 'user.name', 'Disposable fixture')
    git(repo, 'config', 'user.email', 'fixture@example.invalid')
    write(repo / '.gitignore', '/.p2p/\n__pycache__/\n')
    write(repo / 'AGENTS.md', '''# Disposable epic fixture
Read the applicable installed skill and its bundled protocol. Generated P2P contracts are in .p2p/work/<slug>/contract.md; project-owned specs/ and work/ files remain valid inputs.
Durable records are in .p2p/work/. Final destination is trunk.
Tracker is a controlled simulation. Use only the gh executable on the supplied PATH.
It supports pr view/list/edit/create/checks, issue view, and repo view with --json.
Do not use real network, other gh installations, or mutate tracker.json directly.
Git origin is a local bare fixture repository. No merge authority is granted.
Record commands, outputs, and changed paths in your durable stage report.
''')
    parent = '''# Acceptance contract: Name registry
Contract revision: v1
Source: [Registry specification](../../../specs/registry.md)
Parent: None
Prerequisites: None

| ID | Source | Requirement | Boundaries | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | Registry specification | Capture maps a name to a lower-case dictionary key and its original value. | ASCII names; no persistence or network. | registry.capture | Ada becomes {ada: Ada}. | python3 check.py capture | planned |
| R2 | Registry specification | Lookup returns the original captured name for any case of its key. | Missing names return None. | registry.lookup | Captured Ada can be read as ADA. | python3 check.py lookup | planned |
| R3 | Registry specification | Summary prefixes a supplied name with Welcome and one space. | Plain text only. | registry.summary | Ada becomes Welcome Ada. | python3 check.py summary | planned |
| R4 | Registry specification | Capture then lookup then summary preserves Ada as Welcome Ada. | The same candidate supplies all functions. | public function composition | Literal Welcome Ada. | python3 check.py parent | planned |
'''
    write(repo / 'work/project-notes.md', 'Project-owned notes remain ordinary input files.\n')
    write(repo / 'specs/registry.md', '# Registry specification\nCapture names under lower-case keys, read them without case sensitivity, and display Welcome followed by the original name. Preserve the original case through the combined workflow. ASCII only. No network or persistence.\n')
    write(repo / '.p2p/work/parent/contract.md', parent)
    phash = digest(repo / '.p2p/work/parent/contract.md')
    for child, row, requirement in [('capture', 'R1', 'Capture a name under its lower-case key with its original value.'), ('lookup', 'R2', 'Lookup a captured name using any case of its key; a missing key returns None.'), ('summary', 'R3', 'Prefix the supplied original name with Welcome and one space.')]:
        write(repo / f'.p2p/work/{child}/contract.md', f'''# Acceptance contract: {child}
Contract revision: v1
Source: [Parent contract](../parent/contract.md)
Parent: [Parent contract](../parent/contract.md) v1 sha256:{phash}; exact text remains at the canonical parent path.
Decomposition: [Parent slicing plan](../parent/slicing.md)
Prerequisites: {'Capture outcome must exist in the actual candidate; issue 101 state alone is insufficient.' if child == 'lookup' else 'None.'}
Inherited constraints: ASCII names; no persistence, network, or automatic merge.

| ID | Source | Requirement | Boundaries | Seam | Oracle | Planned evidence | Plan state |
|---|---|---|---|---|---|---|---|
| R1 | .p2p/work/parent/contract.md v1:{row} | {requirement} | Parent constraints apply. | registry.{child} | Literal examples in check.py. | python3 check.py {child} | planned |

Parent R4 composition remains part of final parent verification.
''')
    write(repo / '.p2p/work/solo/contract.md', '# Acceptance contract: Sum\nContract revision: v1\nParent: None\nSource: The request is to preserve ordinary integer addition.\n\n| ID | Requirement | Seam | Oracle | Planned evidence | Plan state |\n|---|---|---|---|---|---|\n| R1 | sum([2, 3]) returns 5 | Python sum | Literal 5 | python3 -c "assert sum([2, 3]) == 5" | planned |\n')
    write(repo / 'registry.py', 'EXPERIMENTAL = True\n\ndef capture(name):\n    return {name.lower(): name}\n\ndef lookup(items, key):\n    return items.get(key.lower())\n\ndef summary(name):\n    return "Welcome " + name\n\ndef greet(name):\n    return summary(lookup(capture(name), name))\n')
    write(repo / 'check.py', '''import sys
from registry import capture, lookup, summary, greet
case = sys.argv[1]
if case == 'capture':
    assert capture('Ada') == {'ada': 'Ada'}
elif case == 'lookup':
    assert lookup({'ada': 'Ada'}, 'ADA') == 'Ada'
    assert lookup({}, 'ADA') is None
elif case == 'summary':
    assert summary('Ada') == 'Welcome Ada'
elif case == 'parent':
    assert summary(lookup(capture('Ada'), 'ADA')) == 'Welcome Ada'
    assert greet('Ada') == 'Welcome Ada'
else:
    raise ValueError(case)
print(case + ': PASS')
''')
    git(repo, 'add', '.')
    git(repo, 'commit', '-m', 'Fixture contracts and registry')
    start = git(repo, 'rev-parse', 'HEAD')
    git(repo, 'init', '--bare', str(root / 'origin.git'))
    git(repo, 'remote', 'add', 'origin', str(root / 'origin.git'))
    git(repo, 'push', '-u', 'origin', 'trunk')
    grouped = case not in ('S1', 'S7', 'S12', 'S14')
    choices = {name: ('grouped' if grouped else 'independent') for name in ('capture', 'lookup', 'summary')}
    if case == 'S3':
        choices['capture'] = 'independent'
    if case != 'S13' or variant != 'missing':
        git(repo, 'branch', 'epic/example', start)
    if case == 'S13' and variant == 'conflicting':
        unrelated = git(repo, 'commit-tree', git(repo, 'rev-parse', 'HEAD^{tree}'), '-m', 'Unrelated integration history')
        git(repo, 'update-ref', 'refs/heads/epic/example', unrelated)
    if case in ('S8', 'S10', 'S11') or (case == 'S13' and variant == 'advanced'):
        git(repo, 'checkout', 'epic/example')
        if case == 'S8':
            write(repo / 'unfinished-sibling.txt', 'UNFINISHED_SIBLING_DO_NOT_SHIP\n')
        elif case == 'S11':
            # Parent wiring supplies the wrong argument; every child stays correct.
            write(repo / 'registry.py', (repo / 'registry.py').read_text().replace('lookup(capture(name), name)', 'lookup(capture(name.upper()), name)'))
        else:
            write(repo / 'integration-note.txt', 'Advanced integration tip\n')
        git(repo, 'add', '.')
        git(repo, 'commit', '-m', 'Fixture integrated contribution')
    if case == 'S14' and variant != 'present':
        write(repo / 'registry.py', (repo / 'registry.py').read_text().replace('return {name.lower(): name}', 'raise NotImplementedError("capture not integrated")'))
        git(repo, 'add', '.')
        git(repo, 'commit', '-m', 'Fixture missing prerequisite')
    candidate = git(repo, 'rev-parse', 'HEAD')
    git(repo, 'branch', 'child/lookup', candidate)
    git(repo, 'push', 'origin', '--all')
    if case == 'S4':
        git(repo, 'checkout', 'child/lookup')
    if case == 'S7':
        write(repo / 'human-notes.txt', 'Preserve this uncommitted human edit.\n')
    integration = 'epic/example' if grouped or case == 'S7' else 'none'
    table = '\n'.join(f'| .p2p/work/{name}/contract.md | {choice} | {"epic/example" if choice == "grouped" else "trunk"} | {"Must ship with the parent" if choice == "grouped" else "Acceptable if no sibling ships"} | {"landed" if case == "S7" and name == "capture" else "remaining"} |' for name, choice in choices.items())
    plan = f'''# Registry decomposition

## Approved delivery plan
Plan revision: v1
Approval source: Fixture owner approved these exact destinations and parent completion conditions in [setup receipt](approval.md). Strategy authority only; no ref or PR effects.
Parent: .p2p/work/parent/contract.md
Final destination: trunk
Integration branch: {integration}
Integration start: {start if integration != 'none' else 'none'}
Default choice: {'grouped' if grouped else 'independent'}

| Child | Choice | Destination | Reason | State |
|---|---|---|---|---|
{table}

Parent completion: All parent requirements, including R4 composition, need review and proof on one exact assembled candidate. Grouped parent publication also requires full matching parent reports.
Pending actions: {'Create epic/example at ' + start + ' only under branch setup authority.' if case == 'S13' and variant == 'missing' else 'None.'}

## Contributions
Capture contributes R1, lookup R2, summary R3; full R4 is verified on the assembled parent. Lookup requires actual capture behavior. Parent text sha256:{phash}.
'''
    if case == 'S5':
        if variant == 'missing':
            plan = '# Registry decomposition\nNo delivery decision has been approved.\n'
        elif variant == 'conflicting':
            plan += '\n' + plan[plan.index('## Approved delivery plan'):]
        elif variant == 'proposed-only':
            plan = plan.replace('## Approved delivery plan', '## Proposed delivery plan').replace('Fixture owner approved', 'Fixture owner has not approved')
        else:
            plan += '\n## Proposed delivery plan\nPlan revision: v2\nProposed lookup destination: trunk. Approval pending.\n'
    if case == 'S4' and variant == 'legacy':
        plan = f'# Legacy decomposition\n\nParent: .p2p/work/parent/contract.md\nApproval source: Fixture owner explicitly approved lookup -> epic/example and capture -> trunk, summary -> epic/example on 2026-09-26; strategy only.\nFinal destination: trunk\nIntegration branch: epic/example\nIntegration start: {start}\n\nChild lookup: .p2p/work/lookup/contract.md -> epic/example. Reason: ships with summary.\nChild capture: .p2p/work/capture/contract.md -> trunk. Reason: acceptable alone.\nChild summary: .p2p/work/summary/contract.md -> epic/example. Reason: ships with lookup.\nParent completion: Review and prove all parent requirements on the assembled candidate.\n'
    write(repo / '.p2p/work/parent/slicing.md', plan)
    write(repo / '.p2p/work/parent/approval.md', ('No delivery plan is approved.\n' if case == 'S5' and variant in ('missing', 'proposed-only') else 'Fixture owner approves the approved delivery plan section exactly as captured in slicing.md at fixture preparation. This covers strategy and local record retention only. No ref, PR, publication, or merge effects are authorized.\n'))
    write(repo / '.p2p/work/lookup/candidate.json', json.dumps({'commit': candidate, 'comparison_base': start, 'work_item': '.p2p/work/lookup/contract.md', 'work_item_sha256': digest(repo / '.p2p/work/lookup/contract.md'), 'binding_inputs': [{'path': 'specs/registry.md', 'sha256': digest(repo / 'specs/registry.md')}, {'path': '.p2p/work/parent/contract.md', 'sha256': phash}]}, indent=2) + '\n')
    write(repo / '.p2p/work/parent/candidate.json', json.dumps({'commit': candidate, 'comparison_base': start, 'work_item': '.p2p/work/parent/contract.md', 'work_item_sha256': phash, 'binding_inputs': [{'path': 'specs/registry.md', 'sha256': digest(repo / 'specs/registry.md')}]}, indent=2) + '\n')
    for slug in ('lookup', 'parent'):
        write(repo / f'.p2p/work/{slug}/implementation.md', f'# Fixture implementation handoff\n\nContract: .p2p/work/{slug}/contract.md v1 sha256:{digest(repo / f".p2p/work/{slug}/contract.md")}\nCandidate: {candidate}\nReview base: {start}\nExisting code is supplied for independent inspection. No review or proof verdict is seeded.\nChecks: run python3 check.py capture, lookup, summary, and parent separately.\nScope: all requirements of this contract.\n')
    pr = {'number': 17, 'url': 'https://fixture.invalid/epic/pull/17', 'state': 'OPEN', 'baseRefName': 'trunk' if case in ('S6', 'S7', 'S9') else 'epic/example', 'headRefName': 'child/lookup', 'headRefOid': candidate, 'title': 'Lookup names', 'body': f'Human note: keep this sentence byte-for-byte.\n<!-- grove:publish-pr repo=fixture/epic candidate=git:{candidate} contract=sha256:{digest(repo / ".p2p/work/lookup/contract.md")} -->\n', 'isDraft': True, 'updatedAt': 'fixture-revision-0', 'statusCheckRollup': [{'name': 'required-ci', 'status': 'COMPLETED', 'conclusion': 'SUCCESS'}], 'reviewDecision': 'APPROVED', 'mergeable': 'MERGEABLE', 'baseRefOid': start}
    write(repo / '.p2p/work/lookup/publication.md', f'# Existing publication observation\n\nPR: {pr["url"]}\nCandidate: git:{candidate}\nPublication commit: {candidate}\nPublished head: child/lookup\nObserved base: {pr["baseRefName"]}\nContract: .p2p/work/lookup/contract.md v1 sha256:{digest(repo / ".p2p/work/lookup/contract.md")}\nThis is a fixture observation of an existing PR, not a current preview, report pair, or effect authority.\n')
    write(root / 'tracker.json', json.dumps({'prs': {'17': pr}, 'calls': 0}, indent=2) + '\n')
    write(root / 'calls.jsonl', '')
    shutil.copyfile(__file__, root / 'tracker.py')
    write(root / 'bin/gh', '#!/bin/sh\nexec python3 "$EPIC_TRACKER_ROOT/tracker.py" tracker "$@"\n')
    (root / 'bin/gh').chmod(0o755)
    shutil.copytree(SOURCE / 'skills/productivity', root / 'installed', symlinks=False)
    write(root / 'request.md', REQUESTS[case] + '\n\nWork in ' + str(repo) + '. Installed skills are at ' + str(root / 'installed') + '. Read the invoked SKILL.md and bundled references. Use `export EPIC_TRACKER_ROOT=' + str(root) + '; export PATH=' + str(root / 'bin') + ':$PATH` for every tracker command. This is simulated tracker state and real disposable Git. Do not read fixture builder, oracle.json, or tracker.json. You may inspect tracker state only through gh. No real network. Do not delegate. Save exact command/output evidence and stage reports; final response alone is insufficient.\n')
    before = {str(path.relative_to(repo)): digest(path) for path in repo.rglob('*') if path.is_file() and '.git' not in path.parts}
    write(root / 'oracle.json', json.dumps({'case': case, 'variant': variant, 'start': start, 'candidate': candidate, 'destinations': choices, 'before': before, 'refs_before': git(repo, 'show-ref'), 'pr_before': pr, 'request_sha256': digest(root / 'request.md'), 'installed_hashes': {str(p.relative_to(root / 'installed')): digest(p) for p in (root / 'installed').rglob('*') if p.is_file()}}, indent=2) + '\n')
    print(json.dumps({'repo': str(repo), 'request': str(root / 'request.md'), 'oracle_withhold': str(root / 'oracle.json'), 'tracker_log': str(root / 'calls.jsonl')}, indent=2))


def inspect(root):
    oracle = json.loads((root / 'oracle.json').read_text())
    repo = root / 'repo'
    events = [json.loads(line) for line in (root / 'calls.jsonl').read_text().splitlines()]
    changed = [name for name, old in oracle['before'].items() if not (repo / name).exists() or digest(repo / name) != old]
    result = {'case': oracle['case'], 'variant': oracle['variant'], 'changed_input_paths': changed, 'refs_before': oracle['refs_before'], 'refs_after': git(repo, 'show-ref'), 'tracker_effects': [e for e in events if e['effect']], 'tracker_calls': len(events), 'reports': [str(p.relative_to(repo)) for p in (repo / '.p2p/work').rglob('*.md')]}
    print(json.dumps(result, indent=2))


def verify(root, expectation):
    """Assertions about real effects; never a substitute for reading skill reports."""
    oracle = json.loads((root / 'oracle.json').read_text())
    repo = root / 'repo'
    events = [json.loads(line) for line in (root / 'calls.jsonl').read_text().splitlines()]
    effects = [event['effect'] for event in events if event['effect']]
    state = json.loads((root / 'tracker.json').read_text())
    for name, before in oracle['before'].items():
        if name.startswith(('work/', 'specs/')) or name == 'human-notes.txt':
            assert (repo / name).is_file() and digest(repo / name) == before, name + ' changed'
    if expectation == 'no-effects':
        assert not effects, effects
        assert git(repo, 'show-ref') == oracle['refs_before'], 'Git refs changed without authority'
        assert state['prs'] == {'17': oracle['pr_before']}, 'PR state changed'
    elif expectation == 'retarget':
        assert len(effects) == 1 and effects[0].get('edit') == '17', effects
        assert effects[0]['changes'] == {'baseRefName': 'epic/example'}, effects
        assert state['prs']['17']['baseRefName'] == 'epic/example'
        assert state['prs']['17']['body'] == oracle['pr_before']['body'], 'Human text changed'
        assert len(state['prs']) == 1, 'Duplicate PR'
        effect_sequence = next(e['sequence'] for e in events if e['effect'])
        assert any(e['sequence'] > effect_sequence and e['argv'][:3] == ['pr', 'view', '17'] and e['result'].get('baseRefName') == 'epic/example' for e in events), 'Missing successful target readback'
    elif expectation in ('parent-fails', 'parent-passes'):
        result = subprocess.run([sys.executable, 'check.py', 'parent'], cwd=repo, capture_output=True, text=True)
        assert (result.returncode != 0) == (expectation == 'parent-fails'), result.stdout + result.stderr
        assert not any('create' in effect for effect in effects), 'Unexpected parent PR'
        print(result.stdout + result.stderr, end='')
    print('PASS: ' + expectation + ' effect assertions; separately inspect skill verdicts and identities')


def check_candidates(root):
    """Use the installed helper, retaining its exact commands and results."""
    oracle = json.loads((root / 'oracle.json').read_text())
    repo = root / 'repo'
    helper = root / 'installed/implement-contract/scripts/p2p_filesystem.py'
    observations = []
    for slug in ('lookup', 'parent'):
        work = f'.p2p/work/{slug}/contract.md'
        record = json.loads((repo / f'.p2p/work/{slug}/candidate.json').read_text())
        resolve = [sys.executable, str(helper), '--repo', str(repo), 'resolve', work]
        resolved = subprocess.run(resolve, capture_output=True, text=True)
        assert resolved.returncode == 0, resolved.stderr
        assert record['binding_inputs'] == json.loads(resolved.stdout)['binding_inputs'], 'Noncanonical binding metadata'
        command = [sys.executable, str(helper), '--repo', str(repo), 'validate', work, '--base', record['comparison_base']]
        result = subprocess.run(command, capture_output=True, text=True)
        expected = 'product candidate changed' if oracle['case'] == 'S7' else None
        if expected:
            assert result.returncode == 1 and expected in result.stderr, result.stdout + result.stderr
        else:
            assert result.returncode == 0, result.stdout + result.stderr
        observations.append({'command': command, 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr, 'intentional_difference': 'Preserved uncommitted human notes are outside the historical candidate' if expected else None})
        if slug == 'lookup' and oracle['destinations']['lookup'] == 'grouped':
            ref = subprocess.run(['git', '-C', str(repo), 'rev-parse', '--verify', 'epic/example'], capture_output=True, text=True)
            if ref.returncode == 0 and ref.stdout.strip() != record['comparison_base']:
                command = command[:-1] + [ref.stdout.strip()]
                result = subprocess.run(command, capture_output=True, text=True)
                assert result.returncode == 1 and 'comparison base changed' in result.stderr, result.stdout + result.stderr
                observations.append({'command': command, 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr, 'intentional_difference': 'Integration target differs from historical review base; skill must refresh or reject unrelated history'})
    write(root / 'candidate-validation.json', json.dumps(observations, indent=2) + '\n')
    print('PASS: ' + oracle['case'] + '/' + oracle['variant'] + ' candidate metadata; intentional drift recorded separately')


def self_check():
    with tempfile.TemporaryDirectory(prefix='epic-tracker-check-') as temp:
        root = Path(temp)
        write(root / 'tracker.json', json.dumps({'prs': {'17': {'number': 17, 'baseRefName': 'trunk', 'body': 'human', 'url': 'fixture'}}, 'lose_next_edit_response': True}))
        env = dict(os.environ, EPIC_TRACKER_ROOT=str(root))
        command = [sys.executable, __file__, 'tracker']
        first = subprocess.run(command + ['pr', 'edit', '17', '--base', 'epic/example'], env=env, capture_output=True)
        assert first.returncode == 1
        readback = subprocess.check_output(command + ['pr', 'view', '17'], env=env, text=True)
        assert json.loads(readback)['baseRefName'] == 'epic/example'
        assert json.loads(readback)['body'] == 'human'
        events = [json.loads(line) for line in (root / 'calls.jsonl').read_text().splitlines()]
        assert sum(e['effect'] is not None for e in events) == 1
        state = json.loads((root / 'tracker.json').read_text())
        state['inject'] = {'on_call': 3, 'pr': 17, 'pr_changes': {'body': 'concurrent human edit'}}
        write(root / 'tracker.json', json.dumps(state))
        readback = subprocess.check_output(command + ['pr', 'view', '17'], env=env, text=True)
        assert json.loads(readback)['body'] == 'concurrent human edit'
        plan = root / 'repo/.p2p/work/parent/slicing.md'
        write(plan, '## Approved delivery plan\nPlan revision: v1\n')
        state = json.loads((root / 'tracker.json').read_text())
        changed_plan = '## Approved delivery plan\nPlan revision: v2\n'
        state['after_edit'] = {'plan_text': changed_plan}
        write(root / 'tracker.json', json.dumps(state))
        subprocess.run(command + ['pr', 'edit', '17', '--base', 'trunk'], env=env, check=True, capture_output=True)
        assert json.loads((root / 'tracker.json').read_text())['prs']['17']['baseRefName'] == 'trunk'
        assert plan.read_text() == changed_plan
        event = json.loads((root / 'calls.jsonl').read_text().splitlines()[-1])
        assert event['effect']['changes'] == {'baseRefName': 'trunk'}
        assert event['injection_phase'] == 'after_persisted_edit'
        case = root / 's11'
        prepare('S11', case, 'default')
        for child in ('capture', 'lookup', 'summary'):
            subprocess.run([sys.executable, 'check.py', child], cwd=case / 'repo', check=True, capture_output=True)
        literal = "from registry import capture, lookup, summary, greet; assert capture('Ada') == {'ada': 'Ada'}; assert lookup(capture('Ada'), 'ADA') == 'Ada'; assert summary('Ada') == 'Welcome Ada'; assert greet('Ada') == 'Welcome ADA'"
        subprocess.run([sys.executable, '-c', literal], cwd=case / 'repo', check=True)
        assert subprocess.run([sys.executable, 'check.py', 'parent'], cwd=case / 'repo', capture_output=True).returncode == 1
    print('PASS: persisted edit, lost response, readback, effect counts, post-edit plan change, complete children and parent-only failure')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'tracker':
        del sys.argv[1]
        sys.exit(tracker())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['prepare', 'inspect', 'verify', 'check-candidates', 'self-check'])
    parser.add_argument('case_or_path', nargs='?')
    parser.add_argument('path', nargs='?')
    parser.add_argument('--variant', default='default')
    parser.add_argument('--expect', choices=['no-effects', 'retarget', 'parent-fails', 'parent-passes'], default='no-effects')
    args = parser.parse_args()
    if args.operation == 'self-check':
        self_check()
    elif args.operation == 'prepare':
        if args.case_or_path not in REQUESTS or not args.path:
            parser.error('prepare requires S1..S14 and a new absolute output directory')
        prepare(args.case_or_path, Path(args.path).resolve(), args.variant)
    elif args.operation == 'check-candidates':
        check_candidates(Path(args.case_or_path).resolve())
    elif args.operation == 'verify':
        verify(Path(args.case_or_path).resolve(), args.expect)
    else:
        inspect(Path(args.case_or_path).resolve())
