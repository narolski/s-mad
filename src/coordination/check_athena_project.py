"""Hourly read-only Athena association check; no jobs submitted or modified."""
import datetime,json,pathlib,subprocess,shutil
ROOT=pathlib.Path('/mnt/t7/smad_next/coordination_20261114/athena_project_watch')
ROOT.mkdir(parents=True,exist_ok=True)
remote="sacctmgr -nP show assoc user=plgpnarolski format=Account,Partition"
cmd=['flock','-w','10','/tmp/smadnext-athena-cmd.lock','ssh','-o','BatchMode=yes','-o','ConnectTimeout=15','plgpnarolski@athena.cyfronet.pl',remote]
r={'checked_at':datetime.datetime.now().astimezone().isoformat(),'project':'plgmorphgeneral'}
try:
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=45)
 r.update(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
 accounts=[line.split('|')[0] for line in p.stdout.splitlines()]
 r['association_visible']=p.returncode==0 and any(a in ('plgmorphgeneral','plgmorphgeneral-gpu-a100') for a in accounts)
 r['status']='association_visible_needs_partition_validation' if r['association_visible'] else 'not_available' if p.returncode==0 else 'check_failed'
 if 'Permission denied' in p.stderr or 'Authentication failed' in p.stderr:
  r['status']='authentication_failed_checks_stopped'
  subprocess.run(['systemctl','--user','stop','smad-athena-project.timer'],capture_output=True)
 if r['association_visible']:
  subprocess.run(['systemctl','--user','stop','smad-athena-project.timer'],capture_output=True)
  if shutil.which('notify-send'):
   subprocess.run(['notify-send','Athena project available','plgmorphgeneral is now visible in Slurm. Validate partition access and move pending jobs.'],capture_output=True,timeout=10)
except (subprocess.TimeoutExpired,OSError) as e:
 r.update(status='check_failed',error=type(e).__name__)
with (ROOT/'checks.jsonl').open('a') as f:f.write(json.dumps(r)+'\n')
tmp=ROOT/'latest.tmp';tmp.write_text(json.dumps(r,indent=2)+'\n');tmp.replace(ROOT/'latest.json')
print(json.dumps(r))
