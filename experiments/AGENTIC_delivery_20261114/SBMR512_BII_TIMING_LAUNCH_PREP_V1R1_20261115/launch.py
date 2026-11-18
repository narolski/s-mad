"""Durable first-batch control plane. SOURCE ONLY; root executes after OTHER/release."""
import datetime,hashlib,json,os,pathlib,subprocess,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from contract import validate,OUTPUT
BASE=pathlib.Path(OUTPUT).parent
J=BASE/'dispatch_s408'
SRC=BASE/'source'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(4<<20),b''):h.update(b)
 return h.hexdigest()
def put(name,obj):
 with (J/name).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
 fd=os.open(J,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def main():
 path,expected=sys.argv[1:]
 if sys.flags.optimize or sha(path)!=expected:raise ValueError('bootstrap/config binding')
 c=json.loads(pathlib.Path(path).read_bytes());validate(c)
 if not (os.isatty(0) and os.isatty(1) and os.environ.get('TMUX_PANE')):raise ValueError('real detached tmux PTY required')
 # All opaque admissions/config/source checked before permanent preallocation claim.
 for a in c['admissions'].values():
  if sha(a['path'])!=a['sha256']:raise ValueError('admission hash')
 if pathlib.Path(OUTPUT).exists():raise ValueError('worker output exists; no retry')
 if not BASE.is_dir():raise ValueError('root must pre-admit native durable parent')
 J.mkdir(exist_ok=False)
 put('CLAIM.json',dict(scope='FIRST_BATCH_ONLY',config_sha256=expected,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),automatic_retry=False,scientific_read='HOLD'))
 rc=125;error=None
 try:
  pane=os.environ['TMUX_PANE']
  if subprocess.check_output(['/usr/bin/tmux','display-message','-p','-t',pane,'#{pane_pipe}'],text=True).strip()!='0':raise ValueError('existing tmux pipe')
  subprocess.run(['/usr/bin/tmux','set-option','-p','-t',pane,'remain-on-exit','on'],check=True)
  (J/'terminal.log').open('x').close()
  subprocess.run(['/usr/bin/tmux','pipe-pane','-t',pane,'-o','/usr/bin/cat >> '+str(J/'terminal.log')],check=True)
  srun=['/opt/slurm/current/bin/srun','--verbose','--immediate=60','--job-name=sbmr512-bii-timing-s408','--partition=lem-gpu-interactive','--nodes=1','--ntasks=1','--cpus-per-task=8','--mem=32G','--gres=gpu:hopper:1,storage:local:8G','--time=00:15:00','--extra=FORCE_RM_TMPDIR','--pty','/bin/bash',str(SRC/'allocation_entry.sh'),path,expected,c['node_bootstrap']]
  cmd=['/usr/bin/timeout','--signal=TERM','--kill-after=10s','1200s']+srun
  env=dict(HOME='/home/narolski',USER='narolski',LOGNAME='narolski',PATH='/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin',SHELL='/bin/bash',LANG='C',LC_ALL='C',TERM=os.environ.get('TERM','screen'))
  put('INTENT.json',dict(argv=cmd,srun_argv=srun,environment=env,source_manifest_sha256=c['worker_source_manifest_sha256'],native_partition_proof=c['admissions']['worker_policy'],automatic_retry=False))
  rc=subprocess.call(cmd,cwd=BASE,env=env)
 except BaseException as e:error=type(e).__name__
 finally:
  jid=(J/'NATIVE_JOB_ID.txt').read_text().strip() if (J/'NATIVE_JOB_ID.txt').is_file() else None
  put('TERMINAL.json',dict(srun_wrapper_exit=rc,error_type=error,native_job_id=jid,status='RECONCILE_NATIVE_TERMINAL_STATE',operator_verdict='NOT_INFERRED_FROM_EXIT',automatic_retry=False))
 return rc if rc>=0 else 128-rc
if __name__=='__main__':sys.exit(main())
