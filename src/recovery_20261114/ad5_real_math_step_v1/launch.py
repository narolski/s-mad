"""One NEW real one-effective-step technical smoke, real tmux/srun PTY; no migration or cancellation."""
import datetime,hashlib,json,os,pathlib,subprocess,sys
ROOT=pathlib.Path('/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5')
J=ROOT/'dispatch/ad5_real_math_step_v1_20261114'
SRC=ROOT/'ad5_real_math_step_v1'

def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()

def write(name,obj):
 p=J/name
 with p.open('x') as f:json.dump(obj,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 fd=os.open(J,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()

def verify_release():
 import importlib.util
 spec=importlib.util.spec_from_file_location('step_verify',SRC/'verify.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 return module.release()


def main():
 assert os.isatty(0) and os.isatty(1) and os.environ.get('TMUX_PANE'),'real tmux PTY required'
 verify_release()
 assert not (ROOT/'logs/keep/ad5_real_math_step_v1_20261114').exists(),'worker namespace exists'
 # Create/fsync permanent claim BEFORE tmux setup or allocation. Failure is terminal.
 write('CLAIM.json',{'utc':utc(),'release_sha256':sha(J/'ROOT_RELEASE.json'),'scope':'NEW_REAL_ONE_EFFECTIVE_STEP_MATH_ONLY','automatic_retry':False})
 rc=125;error=None
 try:
  pane=os.environ['TMUX_PANE']
  assert subprocess.check_output(['tmux','display-message','-p','-t',pane,'#{pane_pipe}'],text=True).strip()=='0'
  subprocess.run(['tmux','set-option','-p','-t',pane,'remain-on-exit','on'],check=True)
  (J/'terminal.log').open('x').close()
  subprocess.run(['tmux','pipe-pane','-t',pane,'-o','cat >> '+str(J/'terminal.log')],check=True)
  cmd=['/opt/slurm/current/bin/srun','--verbose','--immediate=60','--job-name=ad5-real-math-step-v1','--partition=lem-gpu-interactive','--nodes=1','--ntasks=1','--cpus-per-task=8','--mem=120G','--gres=gpu:hopper:1,storage:local:150G','--time=00:15:00','--extra=FORCE_RM_TMPDIR','--pty','/bin/bash',str(SRC/'allocation_entry.sh')]
  env=dict(HOME='/home/narolski',USER='narolski',LOGNAME='narolski',PATH='/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin',SHELL='/bin/bash',LANG='C',LC_ALL='C',TERM=os.environ.get('TERM','xterm'))
  write('INTENT.json',{'utc':utc(),'argv':cmd,'environment':env,'scope':'one real first effective step only; technical receipt and independent review decide interpretation'})
  rc=subprocess.call(cmd,cwd=ROOT,env=env)
 except BaseException as e:
  error=type(e).__name__+': '+str(e)
 finally:
  jid=(J/'NATIVE_JOB_ID.txt').read_text().strip() if (J/'NATIVE_JOB_ID.txt').is_file() else None
  write('TERMINAL.json',{'utc':utc(),'srun_exit':rc,'error':error,'native_job_id':jid,
   'allocation_status':'NATIVE_ID_RECORDED_RECONCILE_TERMINAL_STATE' if jid else 'UNKNOWN_REQUIRES_ROOT_RECONCILIATION',
   'operator_verdict':'NOT_INFERRED_FROM_SRUN_OR_WORKER_EXIT','automatic_retry':False})
 return rc if rc>=0 else 128-rc
if __name__=='__main__':sys.exit(main())
