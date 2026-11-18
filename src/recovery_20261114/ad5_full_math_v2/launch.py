"""Root-only one-seed batch launch after separately adopted placement; never automatic retry."""
import json,os,pathlib,subprocess,sys,time
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import verify
from supervise import put

def main(seed):
 r=verify.release(seed,submission=True);j=verify.JOURNAL/('s%d'%seed)
 assert not (verify.ROOT/'logs/keep/ad5_full_math_v2_20261114'/('s%d'%seed)).exists()
 put(j/'CLAIM.json',dict(seed=seed,release_sha256=verify.sha(j/'ROOT_RELEASE.json'),at=time.time(),automatic_retry=False))
 cmd=['/opt/slurm/current/bin/sbatch','--parsable','--no-requeue','--partition=lem-gpu-short','--nodes=1','--ntasks=1','--cpus-per-task=8','--mem=120G','--gres=gpu:hopper:1,storage:local:150G','--time=06:00:00','--extra=FORCE_RM_TMPDIR','--export=NONE','--job-name=ad5-fullB-v2-s%d'%seed,'--output='+str(j/'native-%j.out'),str(verify.SOURCE/'allocation_entry.sh'),str(seed)]
 put(j/'INTENT.json',dict(argv=cmd,profile=r['resource_profile']))
 try:
  x=subprocess.run(cmd,env=dict(HOME='/home/narolski',USER='narolski',LOGNAME='narolski',PATH='/usr/bin:/bin',LANG='C',LC_ALL='C'),capture_output=True,text=True)
  native=x.stdout.strip().split(';')[0];valid=x.returncode==0 and native.isdigit()
  put(j/'SUBMISSION.json',dict(returncode=x.returncode,stdout=x.stdout,stderr=x.stderr,native_job_id=native if valid else None,status='SUBMITTED_NOT_COMPLETED' if valid else 'UNKNOWN_RECONCILE_NO_RETRY',automatic_retry=False))
  return 0 if valid else 94
 except BaseException as e:
  put(j/'SUBMISSION_ERROR.json',dict(error=repr(e),status='UNKNOWN_RECONCILE_NO_RETRY'));return 94
if __name__=='__main__':sys.exit(main(int(sys.argv[1])))
