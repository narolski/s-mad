"""Compute-node adapter; launches exact reviewed diagnostic without changing its bytes."""
import hashlib,json,os,pathlib,subprocess,sys,datetime
ROOT=pathlib.Path('/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5')
J=ROOT/'dispatch/ad5_firstbackward_interactive_v1'
def put(name,obj):
 with (J/name).open('x') as f:json.dump(obj,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
assert os.isatty(0) and os.isatty(1),'real srun PTY required'
assert os.environ.get('SLURM_JOB_PARTITION')=='lem-gpu-interactive'
assert os.environ.get('SLURM_CPUS_PER_TASK')=='8'
assert os.environ.get('TMPDIR') and os.environ.get('SLURM_JOB_ID')
assert os.environ.get('CUDA_VISIBLE_DEVICES') and len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))==1
for name,h in {'ad5w_firstbackward_diagnostic.sbatch':'e090bd45f69cbc30b58ac1faa5c711cde672a75d842e944e5882a1c0eb4e7f92','ad5_backward_instrument.py':'04668b872d83171bf7a2ae909a7955f266fd44b51237805e0b629e955b309f0f'}.items():assert sha(ROOT/name)==h,name
for name,h in {'ad5w_code':'94964c3689aa866ad7700f4b86496590c1b353e8e8be59173158e7b46c35d6ee','ad5w_wheels39':'3bd18def4da9cbec2766896fa160c34c0364de464ca3abd02d675c72620cf13c','smdd_train_cropped':'3189e52af12e2853b06c86993b1b8b5cfef891fda749395778492e3445924900'}.items():assert sha(ROOT/'packs'/(name+'.tar'))==h,name
assert not (ROOT/'logs/keep/madation_B_s401_smoke_diag_firstbackward_20261114').exists()
env={k:v for k,v in os.environ.items() if k.startswith('SLURM_') or k in ('CUDA_VISIBLE_DEVICES','TMPDIR','TERM')}
env.update(HOME='/home/narolski',USER='narolski',LOGNAME='narolski',PATH='/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin',SHELL='/bin/bash',LANG='C',LC_ALL='C',ARM='B',SMOKE='1',SLURM_ARRAY_TASK_ID='401',AD5_BACKWARD_PATCHER=str(ROOT/'ad5_backward_instrument.py'))
# Array task id is the original seed input, not an assertion of native array scheduling.
put('NODE_START.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native_job_id':os.environ['SLURM_JOB_ID'],'native_array':False,'seed_array_adapter':401,'environment':env,'workload_sha256':sha(ROOT/'ad5w_firstbackward_diagnostic.sbatch')})
rc=subprocess.call(['/bin/bash',str(ROOT/'ad5w_firstbackward_diagnostic.sbatch')],cwd=ROOT,env=env)
put('NODE_EXIT.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'child_exit':rc,'scientific_read_authorized':False})
sys.exit(rc if rc>=0 else 128-rc)
