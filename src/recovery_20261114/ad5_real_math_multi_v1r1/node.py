"""Allocation receipts and clean native env for the new36-update worker."""
import hashlib,json,os,pathlib,subprocess,sys,datetime
ROOT=pathlib.Path('/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5')
J=ROOT/'dispatch/ad5_real_math_multi_v1r1_20261114'
def put(name,obj):
 with (J/name).open('x') as f:json.dump(obj,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
 rc=125;err=None
 try:
  assert os.isatty(0) and os.isatty(1)
  assert os.environ['SLURM_JOB_ID']==(J/'NATIVE_JOB_ID.txt').read_text().strip()
  assert os.environ['SLURM_JOB_PARTITION']=='lem-gpu-interactive' and os.environ['SLURM_CPUS_PER_TASK']=='8'
  assert os.environ.get('TMPDIR','').startswith('/mnt/lscratch/') and len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))==1
  assert os.environ.get('SLURM_MEM_PER_NODE')=='122880'
  worker=ROOT/'ad5_real_math_multi_v1r1/worker.sh'
  import importlib.util
  spec=importlib.util.spec_from_file_location('step_verify',ROOT/'ad5_real_math_multi_v1r1/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);v.release()
  env={k:v for k,v in os.environ.items() if k.startswith('SLURM_') or k in ('CUDA_VISIBLE_DEVICES','TMPDIR','TERM')}
  env.update(HOME='/home/narolski',USER='narolski',LOGNAME='narolski',PATH='/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin',SHELL='/bin/bash',LANG='C',LC_ALL='C')
  put('NODE_START.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native_job_id':os.environ['SLURM_JOB_ID'],'environment':env})
  rc=subprocess.call(['/bin/bash',str(worker)],env=env,cwd=ROOT)
 except BaseException as e:err=type(e).__name__+': '+str(e)
 finally:
  keep=ROOT/'logs/keep/ad5_real_math_multi_v1r1_20261114'
  path=keep/'technical/MULTI_RESULT.json';step=None
  try:step=json.loads(path.read_text()) if path.is_file() else None
  except (ValueError,OSError) as e:err=(err+'; ' if err else '')+'incomplete step receipt: '+str(e)
  if step is not None and not isinstance(step,dict):err=(err+'; ' if err else '')+'invalid step receipt type';step=None
  worker_rc=rc
  supervisor=keep/'SUPERVISOR_EXIT.json'
  try:
   control=json.loads(supervisor.read_text())
   if not control.get('eligible_for_technical_review',False):rc=94 if rc==0 else rc
  except (ValueError,OSError):rc=94 if rc==0 else rc
  if rc==0 and (step is None or step.get('status')!='THIRTY_SIX_REAL_MATH_UPDATES_AND_CHECKPOINT_ROUNDTRIP_COMPLETE'):rc=94
  put('NODE_EXIT.json',{'worker_exit':worker_rc,'node_exit':rc,'error':err,'step_receipt_status':step.get('status') if step else None,
   'technical_smoke_not_production_recovery':True,'missing_status_is_incomplete':True})
 return rc if rc>=0 else 128-rc
if __name__=='__main__':sys.exit(main())
