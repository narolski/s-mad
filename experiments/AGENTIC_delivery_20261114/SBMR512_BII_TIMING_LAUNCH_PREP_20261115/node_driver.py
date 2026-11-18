"""Conditional native-node driver. SOURCE ONLY: not launched by package author."""
import hashlib,json,os,pathlib,resource,subprocess,sys,time
from contract import validate,OUTPUT

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(4<<20),b''):h.update(b)
 return h.hexdigest()
def put(p,x):
 with open(p,'x') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
 fd=os.open(pathlib.Path(p).parent,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def main():
 if sys.flags.optimize: raise ValueError('optimized Python forbidden')
 config_path,expected=sys.argv[1:];raw=pathlib.Path(config_path).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('external config pin')
 c=json.loads(raw);validate(c)
 # Read only root-adopted typed admissions before exclusive launch claim.
 for a in c['admissions'].values():
  if sha(a['path'])!=a['sha256']:raise ValueError('admission changed')
 if os.environ.get('SLURM_JOB_PARTITION')!='lem-gpu-interactive' or not os.environ.get('SLURM_JOB_ID'):raise ValueError('native interactive allocation required')
 parent=pathlib.Path(c['durable_parent'])
 if not parent.is_dir() or pathlib.Path(OUTPUT).exists():raise ValueError('fixed durable output unavailable/already claimed')
 driver=pathlib.Path(c['driver_dir']);driver.mkdir(exist_ok=False)
 put(driver/'CLAIM.json',dict(scope='TECHNICAL_FIRST_BATCH_ONLY',config_sha256=expected,job_id=os.environ['SLURM_JOB_ID'],scientific_read='HOLD'))
 start=time.monotonic()
 try:
  # Actual input/model/library bytes are not accessed until this released claim.
  for p,h in c['content_pins'].items():
   if sha(p)!=h:raise ValueError('content pin mismatch')
  # No optimization/determinism/cache changes. No inherited Python/HF/network settings.
  env={'PATH':'/usr/bin:/bin','HOME':c['isolated_home'],'LANG':'C.UTF-8','PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1','HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','HF_DATASETS_OFFLINE':'1'}
  env.update(c['runtime_env'])
  for k in ('CUDA_VISIBLE_DEVICES','SLURM_JOB_ID','SLURM_JOB_PARTITION','SLURM_CPUS_PER_TASK','TMPDIR'):
   if k in os.environ:env[k]=os.environ[k]
  put(driver/'PRE_WORKER.json',dict(elapsed_content_verification_seconds=time.monotonic()-start,argv=[c['python'],'-E','-s',c['worker_dir']+'/produce.py','--release',c['worker_release'],'--seed','408','--mode','timing']))
  launched=time.monotonic()
  with open(driver/'stdout.txt','xb') as out,open(driver/'stderr.txt','xb') as err:
   p=subprocess.run([c['python'],'-E','-s',c['worker_dir']+'/produce.py','--release',c['worker_release'],'--seed','408','--mode','timing'],env=env,cwd=c['worker_dir'],stdout=out,stderr=err,check=False)
   out.flush();os.fsync(out.fileno());err.flush();os.fsync(err.fileno())
  # Root collects opaque files only; this driver never opens reference/worker results.
  put(driver/'PROCESS.json',dict(exit_code=p.returncode,worker_total_process_seconds=time.monotonic()-launched,verification_plus_process_seconds=time.monotonic()-start,child_maxrss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,status='AWAIT_OTHER_TECHNICAL_REVIEW',scientific_read='HOLD'))
  return p.returncode
 except BaseException as e:
  put(driver/'FAILED.json',dict(error_type=type(e).__name__,status='HOLD_NO_AUTOMATIC_RETRY'));raise
if __name__=='__main__':sys.exit(main())
