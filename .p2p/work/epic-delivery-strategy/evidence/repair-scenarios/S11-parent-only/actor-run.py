import subprocess, pathlib, json, os, hashlib, datetime, sys
root=pathlib.Path('/private/tmp/p2p-epic-repair-cases/S11-parent-only'); repo=root/'repo'
env=os.environ.copy(); env.update(EPIC_TRACKER_ROOT=str(root),PATH=str(root/'bin')+':'+env['PATH'],PYTHONDONTWRITEBYTECODE='1')
log=root/'parent-repair-command-evidence.jsonl'
def run(args):
 p=subprocess.run(args,cwd=repo,env=env,text=True,capture_output=True)
 record=dict(command=args,cwd=str(repo),environment={'EPIC_TRACKER_ROOT':str(root),'PATH_prefix':str(root/'bin'),'PYTHONDONTWRITEBYTECODE':'1'},stdout=p.stdout,stderr=p.stderr,returncode=p.returncode,time=datetime.datetime.now(datetime.timezone.utc).isoformat(),actor='/root/scenario_parent_repaired')
 with log.open('a') as f:f.write(json.dumps(record)+'\n')
 print(json.dumps(record)); return p
if __name__=='__main__':run(sys.argv[1:])
