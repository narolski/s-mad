"""One NEW synthetic diagnostic, real tmux/srun PTY; no migration or cancellation."""
import datetime,hashlib,json,os,pathlib,subprocess,sys
ROOT=pathlib.Path('/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5')
J=ROOT/'dispatch/ad5_sdpa_launcher_v1_20261114'
SRC=ROOT/'ad5_sdpa_launcher_v1'
PROBE=ROOT/'ad5_sdpa_probe_v1'
REVIEW='7d2b92f9f814a35608abc26870609f8bee421788067225fd9e008aaa2df3a45e'
PREREG='d1d028032773f68541515cbd982c741ee031ef60cb5dc7ffb36be95416f6092a'
PROBE_MANIFEST='8138eb69a50c9724ca20417148e1b5373fd12d2e1c8d139710e8eb9b9bb54b5b'

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
 r=json.loads((J/'ROOT_RELEASE.json').read_text())
 assert r['decision']=='GO_ONE_NEW_SYNTHETIC_SDPA_INTERACTIVE_V1'
 assert r['scientific_read']=='HOLD' and r['automatic_retry'] is False
 assert r['author']!=r['reviewer'] and r['root_authorized'] is True
 assert r['source_design_review_sha256']==REVIEW and r['prereg_sha256']==PREREG
 assert r['probe_manifest_sha256']==PROBE_MANIFEST==sha(PROBE/'SHA256SUMS')
 for line in (PROBE/'SHA256SUMS').read_text().splitlines():
  h,n=line.split('  ',1);assert pathlib.Path(n).name==n and sha(PROBE/n)==h
 assert r['launcher_manifest_sha256']==sha(SRC/'SHA256SUMS')
 for line in (SRC/'SHA256SUMS').read_text().splitlines():
  h,n=line.split('  ',1);assert pathlib.Path(n).name==n and sha(SRC/n)==h
 for key in ('source_design_review','prereg','launcher_review','owned_source_commit_check','site_preflight'):
  name=r[key+'_file'];assert pathlib.Path(name).name==name
  assert sha(J/name)==r[key+'_sha256']
 assert r['owned_source_clean_committed'] is True and r['durable_free_gib']>=50
 assert r['old_failed_job']=='6321768_401' and r['old_job_action']=='NONE'
 assert sha(ROOT/'packs/ad5w_wheels39.tar')=='3bd18def4da9cbec2766896fa160c34c0364de464ca3abd02d675c72620cf13c'
 return r

def main():
 assert os.isatty(0) and os.isatty(1) and os.environ.get('TMUX_PANE'),'real tmux PTY required'
 verify_release()
 assert not (ROOT/'logs/keep/ad5_sdpa_probe_v1_20261114').exists(),'worker namespace exists'
 # Create/fsync permanent claim BEFORE tmux setup or allocation. Failure is terminal.
 write('CLAIM.json',{'utc':utc(),'release_sha256':sha(J/'ROOT_RELEASE.json'),'scope':'NEW_SYNTHETIC_SDPA_ONLY','automatic_retry':False})
 rc=125;error=None
 try:
  pane=os.environ['TMUX_PANE']
  assert subprocess.check_output(['tmux','display-message','-p','-t',pane,'#{pane_pipe}'],text=True).strip()=='0'
  subprocess.run(['tmux','set-option','-p','-t',pane,'remain-on-exit','on'],check=True)
  (J/'terminal.log').open('x').close()
  subprocess.run(['tmux','pipe-pane','-t',pane,'-o','cat >> '+str(J/'terminal.log')],check=True)
  cmd=['/opt/slurm/current/bin/srun','--verbose','--immediate=60','--job-name=ad5-sdpa-probe-v1','--partition=lem-gpu-interactive','--nodes=1','--ntasks=1','--cpus-per-task=8','--mem=120G','--gres=gpu:hopper:1,storage:local:150G','--time=00:15:00','--extra=FORCE_RM_TMPDIR','--pty','/bin/bash',str(SRC/'allocation_entry.sh')]
  env=dict(HOME='/home/narolski',USER='narolski',LOGNAME='narolski',PATH='/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin',SHELL='/bin/bash',LANG='C',LC_ALL='C',TERM=os.environ.get('TERM','xterm'))
  write('INTENT.json',{'utc':utc(),'argv':cmd,'environment':env,'scope':'synthetic only; individual backend statuses decide interpretation'})
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
