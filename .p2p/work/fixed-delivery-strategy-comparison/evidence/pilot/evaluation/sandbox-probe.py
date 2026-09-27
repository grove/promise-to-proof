from pathlib import Path
import json,socket,sys
p=Path(sys.argv[1]); observations={}
try:
 p.write_text("unexpected write")
 observations["protected_write"]="ALLOWED"
except PermissionError:
 observations["protected_write"]="denied"
Path("scratch.txt").write_text("allowed scratch")
observations["scratch_write"]="allowed"
s=socket.socket(); s.settimeout(2)
try:
 s.connect(("1.1.1.1",443)); observations["network"]="ALLOWED"
except PermissionError:
 observations["network"]="denied"
except OSError as e:
 observations["network"]="unresolved:"+str(e)
print(json.dumps(observations))
assert observations=={"protected_write":"denied","scratch_write":"allowed","network":"denied"}, observations
