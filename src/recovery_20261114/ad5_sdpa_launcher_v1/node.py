"""Allocation receipts and clean native env around unchanged reviewed synthetic worker."""
import hashlib,json,os,pathlib,subprocess,sys,datetime
ROOT=pathlib.Path('/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5')
J=ROOT/'dispatch/ad5_sdpa_launcher_v1_20261114'
def put(name,obj):
 with (J/name).open('x') as f:json.dump(obj,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
 rc=125;err=None
 try:
  assert os.isatty(0) and os.isatty(1)
  assert os.environ['SLURM_JOB_ID']==(J/'NATIVE_JOB_ID.txt').read_text().strip()
  assert os.environ['SLURM_JOB_PARTITION']=='lem-gpu-interactive' and os.environ['SLURM_CPUS_PER_TASK']=='8'
  assert os.environ.get('TMPDIR') and len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))==1
  worker=ROOT/'ad5_sdpa_probe_v1/worker.sh'
  assert hashlib.sha256(worker.read_bytes()).hexdigest()=='7c3b602bdf091bf4d593ed5d5c0c5874ecea10723538b4feb32f4d2df6b3a76d'
  env={k:v for k,v in os.environ.items() if k.startswith('SLURM_') or k in ('CUDA_VISIBLE_DEVICES','TMPDIR','TERM')}
  env.update(HOME='/home/narolski',USER='narolski',LOGNAME='narolski',PATH='/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin',SHELL='/bin/bash',LANG='C',LC_ALL='C')
  put('NODE_START.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native_job_id':os.environ['SLURM_JOB_ID'],'environment':env})
  rc=subprocess.call(['/bin/bash',str(worker)],env=env,cwd=ROOT)
 except BaseException as e:err=type(e).__name__+': '+str(e)
 finally:
  statuses={}
  keep=ROOT/'logs/keep/ad5_sdpa_probe_v1_20261114'
  for mode in ('default','math'):
   f=keep/(mode+'_exit.txt');statuses[mode]=f.read_text().strip() if f.is_file() else None
  put('NODE_EXIT.json',{'worker_exit':rc,'error':err,'backend_exit_text':statuses,'operator_verdict':'NOT_INFERRED_FROM_WORKER_EXIT','missing_status_is_incomplete':True})
 return rc if rc>=0 else 128-rc
if __name__=='__main__':sys.exit(main())
