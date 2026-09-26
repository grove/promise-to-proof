import json, os, pathlib, socket, subprocess, sys
paths = ['/Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/live-host/tiny-source/.git/HEAD', '/Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/live-host/tiny-source/.git/index', '/Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/live-host/tiny-source/work/tiny.md', '/Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/live-host/tiny-source/.p2p/work/tiny/admission.json', '/Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/live-host/tiny-source/.p2p/work/tiny/base-manifest.json', '/Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/live-host/tiny-source/.p2p/work/tiny/runtime/repository.git/HEAD', '/Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/live-host/tiny-source/.p2p/work/tiny/runtime/workspace/work/tiny.md', '/Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/live-host/tiny-source/.p2p/work/tiny/runtime/workspace/spec.txt', '/Users/grove/projects/promise-to-proof/.p2p/work/delivery-model-conformance/evidence/live-host/tiny-source/.p2p/work/tiny/runtime/candidate-sentinel']
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
