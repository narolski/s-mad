"""Native batch envelope and allocation-start validation before real work."""
import datetime,json,os,pathlib,re,subprocess,sys,time
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import verify
from supervise import put,run

def main(seed):
 j=verify.JOURNAL/('s%d'%seed);keep=verify.ROOT/'logs/keep/ad5_full_math_v2_20261114'/('s%d'%seed);rc=94
 try:
  verify.release(seed)
  assert os.environ['SLURM_JOB_ID']==(j/'NATIVE_JOB_ID.txt').read_text().strip()
  assert os.environ['SLURM_JOB_PARTITION']=='lem-gpu-short' and os.environ['SLURM_CPUS_PER_TASK']=='8' and os.environ['SLURM_MEM_PER_NODE']=='122880'
  assert len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))==1 and os.environ['TMPDIR'].startswith('/mnt/lscratch/')
  raw=(j/'NATIVE_ALLOCATION.txt').read_text();d=dict(re.findall(r'(\w+)=([^ ]+)',raw))
  assert d['JobId']==os.environ['SLURM_JOB_ID'] and d['TimeLimit']=='06:00:00' and d['StartTime'] not in ('Unknown','N/A')
  start=float(subprocess.check_output(['/usr/bin/date','-d',d['StartTime'],'+%s'],text=True));assert 0<=time.time()-start<21000
  keep.mkdir();(keep/'technical').mkdir();(keep/'original_run').mkdir()
  env={k:v for k,v in os.environ.items() if k.startswith('SLURM_') or k in ('CUDA_VISIBLE_DEVICES','TMPDIR')}
  env.update(HOME='/home/narolski',USER='narolski',LOGNAME='narolski',PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',SHELL='/bin/bash')
  os.environ.clear();os.environ.update(env)
  put(j/'NODE_START.json',dict(seed=seed,native_start_epoch=start,environment=env))
  rc=run(keep,pathlib.Path(env['TMPDIR'])/('ad5_full_math_v2_s%d'%seed)/'run',['/bin/bash',str(verify.SOURCE/'body.sh'),str(seed)],start,21000,10,300)
 except BaseException as e:
  put(j/'NODE_FAILURE.json',dict(error_type=type(e).__name__,error=str(e),automatic_retry=False))
 finally:put(j/'NODE_EXIT.json',dict(node_exit=rc,seed=seed,status='COMPLETE_PENDING_REVIEW' if rc==0 else 'INCOMPLETE_OR_FAILED'))
 return rc
if __name__=='__main__':sys.exit(main(int(sys.argv[1])))
