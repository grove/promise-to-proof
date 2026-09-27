Run this exact filesystem-boundary check in the current directory using Python. Do not inspect or modify any other files. It must create/read/delete a temporary probe only inside the current directory, then attempt one write to the captured candidate path. If the candidate write unexpectedly succeeds, remove the probe and print BOUNDARY_FAIL. If it is denied with an OSError, print the exception type and BOUNDARY_OK. Return the command output exactly.

```python
from pathlib import Path
scratch = Path('.workspace-write-probe')
scratch.write_text('scratch-ok')
assert scratch.read_text() == 'scratch-ok'
scratch.unlink()
target = Path('/Users/grove/projects/promise-to-proof/.p2p/tmp/p2p-delivery-review-report-contract-candidate/.p2p/work/delivery-review-report-contract/.boundary-write-probe')
try:
    target.write_text('must-not-write')
except OSError as error:
    print(type(error).__name__)
    print('BOUNDARY_OK')
else:
    target.unlink()
    print('BOUNDARY_FAIL')
```
