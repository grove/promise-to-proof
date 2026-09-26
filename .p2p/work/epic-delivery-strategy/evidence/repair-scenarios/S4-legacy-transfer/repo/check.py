import sys
from registry import capture, lookup, summary
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
else:
    raise ValueError(case)
print(case + ': PASS')
