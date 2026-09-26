"""Disposable subprocess-backed system under test, state survives each process."""
import json
from pathlib import Path
import sys

state = Path('counter-state.json')
action = sys.argv[1]
value = 0 if action == 'Init' else json.loads(state.read_text())['value']
if action == 'Inc':
    value = min(value + 1, 3)
elif action == 'Dec':
    value = max(value - 1, 0)
elif action not in ('Init', 'Get'):
    raise ValueError(action)
observed = {'value': value}
state.write_text(json.dumps(observed))
print(json.dumps(observed))
