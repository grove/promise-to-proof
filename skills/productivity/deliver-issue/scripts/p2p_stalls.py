"""Stall signals for the existing delivery controller, not a second recovery engine.

Compare observable obligations, failed checks and candidate history rather than
verifier prose. Keep this side-effect-free so healthy work pays no model cost.
"""
import json
import re


def named(text, requirements):
    return {r for r in requirements
            if re.search(r'(?<![\w-])' + re.escape(r) + r'(?![\w-])', str(text))}


def signals(findings, requirements):
    """Compact identity of failed behavior; no inference from similar-sounding prose."""
    known = set(requirements)
    ids, seams, failures = set(), set(), set()
    for phase in ('implementation', 'planning', 'review', 'review_gaps', 'proof_gaps'):
        for item in findings.get(phase, []) or []:
            ids.update(named(item, known))
            if phase == 'review' and isinstance(item, dict):
                source = item.get('source', '')
                location = re.sub(r':\d+(?::\d+)?(?:-\d+)?', '', item.get('location', ''))
                if source in known:
                    ids.add(source)
                if source and location:
                    seams.add((source, item.get('axis', ''), location))
    unproven = sorted(set(findings.get('unproven', [])) & known)
    ids.update(unproven)
    for check in findings.get('failed_checks', []):
        if not isinstance(check, dict) or check.get('result') != 'failed':
            continue
        command = ' '.join(str(check.get('command', '')).split())
        if command:
            failures.add(command)
            ids.update(set(check.get('requirement_ids', [])) & known)
    return {'requirements': sorted(ids), 'seams': sorted(seams),
            'failed_checks': sorted(failures), 'unproven': unproven}


def failed_checks(report):
    """Include only actual failing review commands, not unavailable probes."""
    return [{'command': item.get('command', ''), 'result': 'failed'}
            for item in report.get('checks', [])
            if item.get('result') == 'failed' and item.get('command', '').strip()]


def detect(findings, candidate, history, requirements):
    """A reset-worthy stall, or None for normal work and isolated transient errors."""
    completed = [r for r in history if r.get('status') in ('complete', 'worker-replaced')]
    if not completed:
        return None
    # Revisited exact product trees are stronger evidence than attempt counts.
    before = [r.get('candidate_before') for r in completed]
    if candidate in before and len(set(before + [candidate])) > 1:
        return {'kind': 'candidate_oscillation', 'candidate': candidate}
    last = completed[-1]
    old = signals(last.get('findings', {}), requirements)
    new = signals(findings, requirements)
    failed = sorted(set(old['failed_checks']) & set(new['failed_checks']))
    if failed:
        return {'kind': 'unchanged_failed_reproduction', 'checks': failed[:6],
                'requirements': sorted(set(old['requirements']) & set(new['requirements']))}
    if old['unproven'] and old['unproven'] == new['unproven']:
        return {'kind': 'unresolved_proof_behavior', 'requirements': old['unproven']}
    if (old['requirements'] and old['requirements'] == new['requirements']
            and old['seams'] == new['seams']):
        return {'kind': 'same_unresolved_obligations', 'requirements': new['requirements'],
                'seams': new['seams'][:6]}
    # Two identical no-op repairs with unchanged failures merit a fresh diagnosis.
    if (len(completed) >= 2 and
            all(r.get('candidate_before') == r.get('candidate_after') == candidate
                for r in completed[-2:]) and
            completed[-2].get('findings') == completed[-1].get('findings') == findings):
        return {'kind': 'repeated_nonprogress', 'candidate': candidate}
    return None


def strategy_repetition(plan, completed):
    """Disallow exhausted method identity or exact approach at the same capability."""
    for old in completed:
        if old.get('action') != plan.get('action'):
            continue
        same_key = bool(plan.get('strategy_key') and old.get('strategy_key') and
                        plan['strategy_key'] == old['strategy_key'])
        clean = lambda text: ' '.join(re.findall(r'\w+', (text or '').casefold()))
        same_text = clean(old.get('approach')) == clean(plan.get('approach'))
        if (same_key or same_text) and old.get('capability_check') == plan.get('capability_check'):
            return 'repeated an exhausted strategy without new capabilities'
    return None


def falsifiable(expected):
    """Concrete check/result language, not merely 'improve quality' or 'try again'."""
    value = ' '.join((expected or '').split())
    return (len(value) >= 20 and len(value.split()) >= 4 and bool(re.search(
        r'\b(?:test|tests|check|checks|assert|exit|status|stdout|stderr|error|'
        r'output|input|return|response|record|report|proof|review|command|'
        r'observe|observed|print|reject|accept|pass|fail|reproduc\w*|R\d+)\b',
        value, re.I)))


def recent(history, count=4):
    keys = ('action', 'strategy_key', 'approach', 'reason', 'difference_from_prior',
            'expected_result', 'candidate_before', 'candidate_after', 'result',
            'obligations', 'capability_check')
    return [{k: r[k] for k in keys if k in r} for r in history[-count:]]


def reset_context(state, work, findings, history, stall):
    """Bounded fresh-context orientation; deeper original records remain on disk."""
    agreement = state['contract']
    original = re.search(r'^Intended outcome:\s*(.+)$', agreement.get('content', ''), re.M)
    def brief(value, limit):
        result = json.dumps(value, sort_keys=True, ensure_ascii=False)
        return result if len(result) <= limit else result[:limit] + '… [inspect retained record]'
    return {
        'promise': original.group(1)[:1000] if original else agreement.get('source', ''),
        'agreement': {'path': work, 'sha256': agreement['sha256'],
                      'requirement_ids': state['requirements'],
                      'source': agreement.get('source', '')},
        'remaining_gaps': brief(findings, 4000),
        'stall': stall,
        'candidate': state['candidate'].get('key') or state['candidate'].get('commit'),
        'base': state['comparison_base'],
        'constraints': brief((state.get('autonomy') or {}).get('policy', {}).get('constraints', []), 1200),
        'prior_strategies': brief(recent(history), 3500),
        'deeper_history': 'Inspect original saved reports/receipts/generations only as necessary.',
    }
