"""Replay only disposable compatibility checks. Run from this directory."""
import json
import os
from pathlib import Path
import socket
import subprocess
import time

fizz = Path('/private/tmp/p2p-fizzbee-24/fizzbee-v0.5.3-macos_arm')
mbt = Path('fizzbee-mbt-0.2.0-macos_arm').resolve()
commands = []
def run(command, log, expected=0, extra=None):
    result = subprocess.run(command, env=dict(os.environ, **(extra or {})), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    Path(log).write_text(result.stdout)
    commands.append(dict(command=command, environment=extra, output=log, returncode=result.returncode, expected=expected))
    Path('commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    assert result.returncode == expected, result.stdout
    return result.stdout

for name, generated, compiled, graph in [('counter','generated','dist','graph'), ('controller','controller-generated','controller-dist','controller-graph')]:
    run([str(fizz/'fizz'), '--output-dir', graph, name+'.fizz'], name+'-checker-replay.log')
    run(['./node_modules/.bin/tsc','--target','ES2022','--module','NodeNext','--moduleResolution','NodeNext','--strict','--skipLibCheck','--outDir',compiled,*map(str,Path(generated).glob('*.ts'))], name+'-compile-replay.log')
    command = [str(mbt/'fizzbee-mbt-server'),'--states_file',graph]
    with open(name+'-server-replay.log','w') as log:
        server = subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
        try:
            for _ in range(100):
                assert server.poll() is None, 'server exited'
                try:
                    with socket.create_connection(('127.0.0.1',50051),timeout=.1): break
                except OSError: time.sleep(.05)
            else: raise RuntimeError('server did not start')
            env = dict(FIZZBEE_MBT_BIN=str(mbt/'fizzbee-mbt-runner'), FIZZBEE_MBT_SEQ_SEED='42')
            for label, bad in [('good',False),('bad',True),('replay',True)]:
                output = run(['node',compiled+'/'+name+'_test.js'],name+'-'+label+'-verified.log',1 if bad else 0,dict(env,BAD_OBSERVATION='1' if bad else '0'))
                assert ('Return value mismatched' in output) if bad else ('Runner exited successfully' in output)
                if bad: assert '--seq-seed=42' in output
        finally:
            server.terminate()
            server.wait(timeout=5)
print('Both trials passed; deliberate bad observations failed and replayed at seed 42.')
