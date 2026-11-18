"""Isolated stdlib node guard; no target import until its separate claimed grant."""
import hashlib,json,os,pathlib,subprocess,sys,time
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from contract import validate,OUTPUT,BASE

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(4<<20),b''):h.update(b)
 return h.hexdigest()
def put(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 fd=os.open(p.parent,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def main():
 path,expected=sys.argv[1:];raw=pathlib.Path(path).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('config')
 c=json.loads(raw);validate(c);j=pathlib.Path(c['driver_dir'])
 if not (j/'CLAIM.json').is_file() or not (j/'NATIVE_JOB_ID.txt').is_file():raise ValueError('preallocation/native proof')
 if os.environ.get('SLURM_JOB_PARTITION')!='lem-gpu-interactive' or os.environ.get('SLURM_CPUS_PER_TASK')!='2' or os.environ.get('SLURM_MEM_PER_NODE')!='8192':raise ValueError('native envelope')
 put(j/'NODE_CLAIM.json',dict(scope='RUNTIME_IMPORT_ONLY',scientific_read='HOLD'))
 start=time.monotonic()
 try:
  # No broad discovery. These are granted config/tool/source bytes, not user payloads.
  for p,h in c['content_pins'].items():
   if sha(p)!=h:raise ValueError('exact granted pin changed')
  source=pathlib.Path(c['worker_dir']);names=set()
  for line in pathlib.Path(c['source_manifest_path']).read_text().splitlines():
   h,n=line.split('  ',1)
   if n in names or pathlib.Path(n).is_absolute() or '..'in pathlib.Path(n).parts:raise ValueError('manifest')
   names.add(n);p=source/n
   if p.is_symlink() or sha(p)!=h:raise ValueError('source changed')
  if 'probe.py'not in names:raise ValueError('probe source absent')
  env={'HOME':'/home/narolski','PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','HF_DATASETS_OFFLINE':'1'}
  for k in ('CUDA_VISIBLE_DEVICES','SLURM_JOB_ID','SLURM_JOB_PARTITION','SLURM_CPUS_PER_TASK','TMPDIR'):
   if k in os.environ:env[k]=os.environ[k]
  with (j/'stdout.txt').open('xb') as out,(j/'stderr.txt').open('xb') as err:
   p=subprocess.run([c['python'],'-I','-S','-B',str(source/'probe.py'),c['runtime_grant'],c['content_pins'][c['runtime_grant']]],env=env,stdout=out,stderr=err,timeout=240,check=False)
   out.flush();os.fsync(out.fileno());err.flush();os.fsync(err.fileno())
  put(j/'PROCESS.json',dict(exit_code=p.returncode,elapsed_seconds=time.monotonic()-start,status='AWAIT_OTHER_ACTUAL_REVIEW',scientific_read='HOLD'))
  return p.returncode
 except BaseException as e:put(j/'FAILED.json',dict(error_type=type(e).__name__,status='HOLD_NO_RETRY'));raise
if __name__=='__main__':sys.exit(main())
