#!/usr/bin/env python3
"""Live Codex CLI isolation and tiny delivery; retains actual host receipts."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from test_p2p_delivery import repo, d


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    destination = Path(args.output_dir).resolve()
    if destination.exists():
        parser.error('output directory must be new; previous evidence is never overwritten')
    destination.mkdir(parents=True)
    root = destination / 'tiny-source'
    base = repo(root)
    # Retain all runtime and source artifacts; no temporary path is required to resume.
    script = Path(__file__).resolve().parents[1] / 'skills/productivity/deliver-issue/scripts/p2p_delivery.py'
    command = [sys.executable, str(script), '--repo', str(root), 'run', 'work/tiny.md',
               '--comparison-base', base, '--authorize-local', '--max-dispatches', '7']
    project = Path(__file__).resolve().parents[1]
    product = d.fs.snapshot(project)
    product_key = 'snapshot:sha256:' + d.fs.digest(d.fs.canonical(product))
    hashes = {entry['path']: d.fs.digest(d.fs.canonical(entry)) for entry in product}
    (destination / 'invocation.json').write_text(json.dumps({'kind':'LIVE HOST, not fixture transport', 'product_key': product_key, 'product_entries_sha256': hashes,
                                                           'command':command, 'base':base}, indent=2))
    with (destination / 'stdout.json').open('w') as stdout, (destination / 'stderr.txt').open('w') as stderr:
        completed = subprocess.run(command, stdout=stdout, stderr=stderr)
    result = json.loads((destination / 'stdout.json').read_text())
    success = completed.returncode == 0 and result.get('status') == 'REVIEWED_AND_PROVEN'
    unchanged = d.fs.snapshot(project) == product
    success = success and unchanged
    summary = {'kind':'live-host', 'exit_code':completed.returncode, 'passed':success,
               'product_key': product_key, 'product_entries_sha256': hashes, 'code_unchanged': unchanged,
               'controller_result':result, 'source_preserved':not (root/'greet.py').exists()}
    (destination/'summary.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps({'passed':success, 'summary':str(destination/'summary.json'),
                      'blocker':result.get('blocker')}, indent=2))
    return 0 if success and summary['source_preserved'] else 1


if __name__ == '__main__':
    sys.exit(main())
