#!/usr/bin/env python3
"""Replay the Phase 4 pilot: python3 checks/compare_delivery_strategies.py INPUT.json.

Schema v1: episodes contain id, task, strategy, evidence (synthetic/substitute/live/unexecuted),
host and config objects, start/end epoch seconds (null if missing), attempts,
reported_complete, adjudication, human, and costs. Attempts have stable id, stage,
start/end and cost. Cost is {kind: measured|estimated|unknown, amount, provenance};
known amounts require provenance. Estimated costs may instead contain usage and
rates mappings with matching keys (amount = sum(usage[k] * rates[k])). Human fields
are active_seconds, waiting_seconds, interruptions, each nullable. Adjudication
has outcome (satisfactory/defective/unresolved), missed_defects, provenance.
Top-level overhead has costs and human fields; maintenance_seconds is nullable.
Sensitivity entries have name, a_base, a_repair, b_base, b_repair, failure_rates,
and provenance. They are assumptions, never measurements. All money uses one
caller-declared currency. Output is deterministic JSON; this pilot cannot pick a
supported winner. Null means unavailable, never zero.
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
from statistics import median


STRATEGIES = ('review-first', 'proof-first', 'concurrent')
HUMAN = ('active_seconds', 'waiting_seconds', 'interruptions')


def number(value, name, nullable=False):
    if value is None and nullable:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f'{name} must be a finite nonnegative number')
    return value


def label(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{name} must be a nonempty string')
    return value


def obj(value, name):
    if not isinstance(value, dict):
        raise ValueError(f'{name} must be an object')
    return value


def array(value, name):
    if not isinstance(value, list):
        raise ValueError(f'{name} must be an array')
    return value


def interval(record):
    start = number(record.get('start'), 'start', True)
    end = number(record.get('end'), 'end', True)
    if start is not None and end is not None and end < start:
        raise ValueError('end precedes start')
    return start, end


def cost(record):
    obj(record, 'cost')
    kind = record.get('kind')
    if kind not in ('unknown', 'estimated', 'measured'):
        raise ValueError('invalid cost kind')
    if kind == 'unknown':
        if record.get('amount') is not None:
            raise ValueError('unknown cost cannot carry an amount')
        return {'kind': kind, 'amount': None, 'provenance': record.get('provenance')}
    provenance = label(record.get('provenance'), 'cost provenance')
    if 'usage' in record or 'rates' in record:
        usage, rates = obj(record.get('usage'), 'usage'), obj(record.get('rates'), 'rates')
        if kind != 'estimated' or not usage or usage.keys() != rates.keys():
            raise ValueError('priced estimates require matching nonempty usage and rates')
        amount = sum(number(v, 'usage') * number(rates[k], 'rate') for k, v in usage.items())
        if 'amount' in record and record['amount'] != amount:
            raise ValueError('estimate amount disagrees with usage and rates')
    else:
        amount = record.get('amount')
    return {'kind': kind, 'amount': number(amount, 'cost amount'), 'provenance': provenance}


def ledger(records):
    records = [cost(r) for r in records]
    measured = sum(r['amount'] for r in records if r['kind'] == 'measured')
    estimated = sum(r['amount'] for r in records if r['kind'] == 'estimated')
    unknown = sum(r['kind'] == 'unknown' for r in records)
    return {'measured_subtotal': measured, 'estimated_subtotal': estimated,
            'unknown_components': unknown, 'total': None if unknown else measured + estimated,
            'kind': 'unknown' if unknown else 'estimated' if any(r['kind'] == 'estimated' for r in records) else 'measured',
            'components': records}


def complete_sum(values):
    return None if any(v is None for v in values) else sum(values)


def human(record):
    obj(record, 'human')
    result = {key: number(record.get(key), key, True) for key in HUMAN}
    if result['interruptions'] is not None and result['interruptions'] % 1:
        raise ValueError('interruptions must be an integer')
    return result


def episode(record):
    obj(record, 'episode')
    for key in ('id', 'task'):
        label(record.get(key), key)
    if record.get('strategy') not in STRATEGIES or record.get('evidence') not in ('synthetic', 'substitute', 'live', 'unexecuted'):
        raise ValueError('invalid strategy or evidence classification')
    for key in ('host', 'config'):
        obj(record.get(key), key)
    if type(record.get('reported_complete')) is not bool:
        raise ValueError('reported_complete must be boolean')
    start, end = interval(record)
    attempts = {}
    for attempt in array(record.get('attempts'), 'attempts'):
        obj(attempt, 'attempt')
        aid = label(attempt.get('id'), 'attempt id')
        label(attempt.get('stage'), 'attempt stage')
        if aid in attempts and attempts[aid] != attempt:
            raise ValueError(f'conflicting attempt {aid}')
        attempts[aid] = attempt
    intervals, costs = [], list(array(record.get('costs', []), 'episode costs'))
    for attempt in attempts.values():
        a, b = interval(attempt)
        if (start is not None and a is not None and a < start) or (end is not None and b is not None and b > end):
            raise ValueError('attempt outside episode boundaries')
        intervals.append((a, b))
        costs.append(attempt.get('cost', {'kind': 'unknown'}))
    complete = bool(intervals) and all(a is not None and b is not None for a, b in intervals)
    union, cursor = 0, None
    if complete:
        for a, b in sorted(intervals):
            union += max(0, b - max(a, cursor if cursor is not None else a))
            cursor = max(cursor if cursor is not None else b, b)
    verdict = obj(record.get('adjudication', {}), 'adjudication')
    outcome = verdict.get('outcome', 'unresolved')
    if outcome not in ('satisfactory', 'defective', 'unresolved'):
        raise ValueError('invalid independent outcome')
    missed = number(verdict.get('missed_defects'), 'missed_defects', True)
    if missed is not None and missed % 1:
        raise ValueError('missed_defects must be an integer')
    if outcome != 'unresolved':
        label(verdict.get('provenance'), 'adjudication provenance')
    if outcome == 'satisfactory' and missed != 0:
        raise ValueError('satisfactory adjudication must explicitly establish zero missed defects')
    if record['reported_complete'] and outcome == 'defective' and missed == 0:
        raise ValueError('false-green defective completion must record missed defects or unknown')
    config = record['config']
    eligible = (record['evidence'] != 'unexecuted' and config.get('required_checks') == ['review', 'proof'] and config.get('repair_limit') == 1
                and all(isinstance(config.get(k), str) and config[k] for k in ('model', 'controller', 'permissions')))
    # The approved pilot has no demonstrated live concurrency capability.
    if record['strategy'] == 'concurrent':
        eligible = False
    checks = [a for a in attempts.values() if a['stage'] in ('review', 'proof')]
    if record['strategy'] != 'concurrent' and all(a.get('start') is not None and a.get('end') is not None for a in checks):
        checks.sort(key=lambda a: (a['start'], a['end'], a['id']))
        for previous, current in zip(checks, checks[1:]):
            if current['start'] < previous['end']:
                raise ValueError('serial strategy contains overlapping verification')
        first = 'review' if record['strategy'] == 'review-first' else 'proof'
        if checks and checks[0]['stage'] != first:
            raise ValueError('verification order contradicts strategy')
    if record['reported_complete'] and set(a['stage'] for a in checks) != {'review', 'proof'}:
        eligible = False
    if record['strategy'] != 'concurrent' and checks:
        expected = ['review', 'proof'] if record['strategy'] == 'review-first' else ['proof', 'review']
        if any(a['stage'] != expected[i % 2] for i, a in enumerate(checks)):
            raise ValueError('verification sequence contradicts fixed strategy')
    if sum(a['stage'] == 'repair' for a in attempts.values()) > 1:
        eligible = False
    return {**record, 'attempts': list(attempts.values()), 'cost': ledger(costs or [{'kind': 'unknown'}]), 'human': human(record.get('human', {})),
            'outcome': outcome, 'missed_defects': missed, 'eligible': eligible,
            'elapsed_seconds': None if start is None or end is None else end - start,
            'stage_seconds': sum(b-a for a, b in intervals) if complete else None,
            'occupied_seconds': union if complete else None}


def summarize(episodes):
    n = len(episodes)
    successes = sum(e['outcome'] == 'satisfactory' and e['reported_complete'] for e in episodes)
    costs = ledger([c for e in episodes for c in e['cost']['components']])
    elapsed = [e['elapsed_seconds'] for e in episodes]
    known = sorted(v for v in elapsed if v is not None)
    return {'assigned': n, 'useful_completions': successes,
            'outcomes': dict(sorted(Counter(e['outcome'] for e in episodes).items())),
            'satisfactory_without_workflow_completion': sum(e['outcome'] == 'satisfactory' and not e['reported_complete'] for e in episodes),
            'completion_rate': successes / n if n else None, 'cost': costs,
            'cost_per_assigned': costs['total'] / n if n and costs['total'] is not None else None,
            'cost_per_useful_completion': costs['total'] / successes if successes and costs['total'] is not None else None,
            'elapsed_seconds': {'total': complete_sum(elapsed), 'observed': len(known),
                                'median': median(known) if known else None, 'min': min(known) if known else None,
                                'max': max(known) if known else None, 'values': known},
            'missed_defects': complete_sum([e['missed_defects'] for e in episodes]),
            'human': {k: complete_sum([e['human'][k] for e in episodes]) for k in HUMAN},
            'ineligible_episodes': [e['id'] for e in episodes if not e['eligible']]}


def sensitivity(record):
    obj(record, 'sensitivity')
    name, provenance = label(record.get('name'), 'sensitivity name'), label(record.get('provenance'), 'sensitivity provenance')
    ab, ar, bb, br = [number(record.get(k), k) for k in ('a_base', 'a_repair', 'b_base', 'b_repair')]
    values = []
    for q in array(record.get('failure_rates'), 'failure_rates'):
        number(q, 'failure probability')
        if q > 1:
            raise ValueError('failure probability exceeds one')
        a, b = ab + ar*q, bb + br*q
        values.append({'failure_probability': q, 'a_expected_cost': a, 'b_expected_cost': b,
                       'preference': 'tie' if a == b else 'a' if a < b else 'b'})
    cross = (bb-ab)/(ar-br) if ar != br else None
    return {'name': name, 'provenance': provenance, 'kind': 'estimated',
            'assumptions': 'Same full checks and useful-completion probability; one repair at most. Costs are supplied assumptions.',
            'crossover_failure_probability': cross if cross is not None and 0 <= cross <= 1 else None,
            'values': values}


def analyze(data):
    obj(data, 'input')
    if data.get('schema_version') != 1:
        raise ValueError('schema_version must be 1')
    label(data.get('currency'), 'currency')
    episodes = [episode(e) for e in array(data.get('episodes'), 'episodes')]
    if len({e['id'] for e in episodes}) != len(episodes):
        raise ValueError('duplicate episode id')
    episodes.sort(key=lambda e: e['id'])
    for e in episodes:
        for c in e.get('costs', []) + [a.get('cost', {}) for a in e['attempts']]:
            if c.get('currency', data['currency']) != data['currency']:
                raise ValueError('mixed currencies are not supported')
    overhead = obj(data.get('overhead', {}), 'overhead')
    overhead_records = array(overhead.get('costs', [{'kind': 'unknown'}]), 'overhead costs')
    for c in overhead_records:
        obj(c, 'overhead cost')
        if c.get('currency', data['currency']) != data['currency']:
            raise ValueError('mixed currencies are not supported')
    overhead_cost = ledger(overhead_records)
    overhead_human = human(overhead)
    prepare_elapsed = number(overhead.get('prepare_elapsed_seconds'), 'prepare_elapsed_seconds', True)
    maintenance = number(data.get('maintenance_seconds'), 'maintenance_seconds', True)
    groups = {s: summarize([e for e in episodes if e['strategy'] == s]) for s in STRATEGIES}
    a, b = groups['review-first'], groups['proof-first']
    ma, mb = a['elapsed_seconds']['median'], b['elapsed_seconds']['median']
    matched = lambda s: Counter((e['task'], json.dumps(e['host'], sort_keys=True), json.dumps(e['config'], sort_keys=True), e['evidence']) for e in episodes if e['strategy'] == s)
    comparable = (bool(a['assigned'] and b['assigned']) and matched('review-first') == matched('proof-first')
                  and not a['ineligible_episodes'] and not b['ineligible_episodes']
                  and all(e['outcome'] != 'unresolved' and e['elapsed_seconds'] is not None for e in episodes if e['strategy'] != 'concurrent'))
    improvement = (ma-mb)/ma if comparable and ma else None
    quality = (comparable and a['missed_defects'] is not None and b['missed_defects'] is not None
               and b['completion_rate'] >= a['completion_rate'] and b['missed_defects'] <= a['missed_defects'])
    effort = (a['human']['active_seconds'], b['human']['active_seconds'])
    human_ok = None if any(v is None for v in effort) else effort[1] <= effort[0]
    investment = complete_sum([overhead_human['active_seconds'], maintenance])
    human_saving = (effort[0] - effort[1]) / a['assigned'] if comparable and all(v is not None for v in effort) else None
    threshold = None if improvement is None or human_ok is None else improvement >= .2 and quality and human_ok
    total = summarize(episodes)
    known_elapsed = [e['elapsed_seconds'] for e in episodes if e['elapsed_seconds'] is not None]
    if prepare_elapsed is not None:
        known_elapsed.append(prepare_elapsed)
    total['cost'] = ledger(total['cost']['components'] + overhead_cost['components'])
    total['cost_per_assigned'] = total['cost']['total']/len(episodes) if episodes and total['cost']['total'] is not None else None
    total['cost_per_useful_completion'] = total['cost']['total']/total['useful_completions'] if total['useful_completions'] and total['cost']['total'] is not None else None
    return {'schema_version': 1, 'calculation_version': 1, 'currency': data['currency'], 'episodes': episodes,
            'strategies': groups, 'overall': total, 'overhead': {'cost': overhead_cost, **overhead_human, 'prepare_elapsed_seconds': prepare_elapsed},
            'elapsed_including_overhead': {'known_subtotal_seconds': sum(known_elapsed) if known_elapsed else None,
                                         'total_seconds': None, 'status': 'partial',
                                         'scope': 'Sum of observed episode elapsed durations and preparation elapsed; other comparison overhead remains unknown.'},
            'human_including_overhead': {k: complete_sum([total['human'][k], overhead_human[k]]) for k in HUMAN},
            'sensitivity': [sensitivity(s) for s in array(data.get('sensitivity', []), 'sensitivity')],
            'decision': {'status': 'inconclusive', 'supported_winner': None, 'matched_comparable_cohort': comparable,
                         'proof_first_elapsed_improvement_fraction': improvement, 'descriptive_threshold_met': threshold,
                         'threshold_fraction': .2, 'break_even_episodes': None,
                         'active_human_break_even_episodes': investment/human_saving if investment is not None and human_saving and human_saving > 0 else None,
                         'break_even_limit': 'Elapsed and monetary overhead or approved payback horizon unavailable. Active-human payback uses only active-human savings; no exchange between ledgers.',
                         'reason': 'Feasibility pilot only; confirmatory matched repetitions and stopping rules are not agreed. No general winner.'},
            'limits': ['Host and configuration scope is exactly the retained episode provenance.',
                       'Concurrent verification is unavailable in the approved pilot; synthetic overlap is not live capability.',
                       'Strategy totals exclude shared comparison overhead; overall totals include it.',
                       'Unknown costs, human observations and adjudication remain unavailable.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(), parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f'nonfinite JSON number {value}')))
        print(json.dumps(analyze(data), indent=2, sort_keys=True, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(2, f'comparison input error: {error}\n')


if __name__ == '__main__':
    main()
