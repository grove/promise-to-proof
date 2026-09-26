#!/usr/bin/env python3
"""Replay the retained controller compatibility probe in a fresh output directory."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo', required=True, type=Path)
parser.add_argument('--fizz', required=True, type=Path)
parser.add_argument('--mbt', required=True, type=Path)
parser.add_argument('--output-dir', required=True, type=Path)
args = parser.parse_args()
repo, fizz, mbt, output = (p.resolve() for p in (args.repo,args.fizz,args.mbt,args.output_dir))
here = Path(__file__).resolve().parent
output.mkdir(parents=True, exist_ok=False)
commands = []

def run(command, log, expected=0, env=None):
    result = subprocess.run(list(map(str,command)),cwd=output,env=dict(os.environ,**(env or {})),text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (output/log).write_text(result.stdout)
    commands.append({'command':list(map(str,command)),'cwd':str(output),'environment':env,'output':log,'returncode':result.returncode,'expected':expected})
    (output/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    assert result.returncode == expected, result.stdout
    return result.stdout

# Verify release files against retained compatibility hashes, independent of old paths.
pins=json.loads((here/'SHA256SUMS.json').read_text())
for target,suffix in [(fizz,'/fizz'),(fizz.parent/'fizzbee','/fizzbee'),(fizz.parent/'parser/parser_bin','/parser/parser_bin'),(mbt/'fizzbee-mbt-runner','fizzbee-mbt-0.2.0-macos_arm/fizzbee-mbt-runner'),(mbt/'fizzbee-mbt-server','fizzbee-mbt-0.2.0-macos_arm/fizzbee-mbt-server')]:
    matching={v for k,v in pins.items() if k.endswith(suffix)}
    assert len(matching)==1 and hashlib.sha256(target.read_bytes()).hexdigest() in matching, str(target)
for name in ('package.json','package-lock.json','controller.fizz'):
    shutil.copy2(here/name,output/name)
shutil.copytree(here/'controller-generated',output/'controller-generated')
shutil.copy2(here/'portable-controller-adapters.ts',output/'controller-generated/controller_adapters.ts')
assert run(['node','--version'],'node-version.log').strip()=='v26.9.0'
assert run(['npm','--version'],'npm-version.log').strip()=='11.19.1'
run(['npm','ci','--ignore-scripts','--cache',output/'.npm-cache','--fetch-retries=0'],'npm-ci.log')

# Reuse only fixture construction, never its fake transport or test patches.
spec=importlib.util.spec_from_file_location('compatibility_fixture',repo/'checks/test_p2p_delivery.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
base=module.repo(output/'controller-fixture')
(output/'fixture.json').write_text(json.dumps({'helper':str(repo/'checks/test_p2p_delivery.py'),'base':base,'work':'work/tiny.md','state':'unstarted'},indent=2)+'\n')
run([fizz,'--output-dir','controller-graph','controller.fizz'],'checker.log')
run([output/'node_modules/.bin/tsc','--target','ES2022','--module','NodeNext','--moduleResolution','NodeNext','--strict','--skipLibCheck','--outDir','controller-dist',*sorted((output/'controller-generated').glob('*.ts'))],'compile.log')
command=[str(mbt/'fizzbee-mbt-server'),'--states_file','controller-graph']
with (output/'server.log').open('w') as log:
    server=subprocess.Popen(command,cwd=output,stdout=log,stderr=subprocess.STDOUT)
    try:
        for _ in range(100):
            assert server.poll() is None, 'server exited; see server.log'
            try:
                with socket.create_connection(('127.0.0.1',50051),timeout=.1): break
            except OSError: time.sleep(.05)
        else: raise RuntimeError('server did not start')
        env={'FIZZBEE_MBT_BIN':str(mbt/'fizzbee-mbt-runner'),'FIZZBEE_MBT_SEQ_SEED':'42','P2P_CONTROLLER':str(repo/'skills/productivity/deliver-issue/scripts/p2p_delivery.py')}
        for label,bad in [('good',False),('bad',True),('replay',True)]:
            text=run(['node','controller-dist/controller_test.js'],label+'.log',1 if bad else 0,dict(env,BAD_OBSERVATION='1' if bad else '0'))
            assert '"status":"BLOCKED"' in text and 'no delivery invocation exists' in text
            assert ('Return value mismatched' in text and '--seq-seed=42' in text) if bad else 'Runner exited successfully' in text
    finally:
        server.terminate()
        server.wait(timeout=5)
        commands.append({'command':command,'cwd':str(output),'output':'server.log','returncode':server.returncode,'termination':'explicit after trials'})
        (output/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
(output/'result.json').write_text(json.dumps({'result':'compatibility demonstrated','seed':42,'good_exit':0,'bad_exit':1,'replay_exit':1,'scope':'real public controller status on unstarted fixture; no lifecycle acceptance'},indent=2)+'\n')
print('PASS: real controller status accepted; wrong observation rejected and replayed at seed 42.')
