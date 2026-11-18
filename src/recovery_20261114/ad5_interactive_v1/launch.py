"""One-shot reviewed migration launcher; run only inside dedicated real tmux PTY."""
import datetime,hashlib,json,os,pathlib,subprocess,sys
ROOT=pathlib.Path('/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5')
J=ROOT/'dispatch/ad5_firstbackward_interactive_v1'
SRC=ROOT/'ad5_interactive_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,obj):
 with (J/name).open('x') as f:json.dump(obj,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
assert os.isatty(0) and os.isatty(1) and os.environ.get('TMUX_PANE'),'dedicated tmux PTY required'
release=json.loads((J/'MIGRATION_RELEASE.json').read_text())
assert release['decision']=='GO_ONE_INTERACTIVE_AFTER_CANCELLED_UNSTARTED'
assert release['original_job']=='6321768_401'
assert release['native_cancelled'] is True and release['ever_started'] is False
assert release['root_authorized'] is True and release['independent_review_sha256']
assert release['source_hashes']=={n:sha(SRC/n) for n in ('launch.py','worker.py')}
for name,h in release['evidence_hashes'].items():
 assert pathlib.Path(name).name==name and sha(J/name)==h
assert release['evidence_hashes'],'native hold/cancel/accounting evidence required'
assert not (ROOT/'logs/keep/madation_B_s401_smoke_diag_firstbackward_20261114').exists()
# Atomic one-shot claim; failure after claim is NOT permission to invoke again.
(J/'CLAIM').mkdir()
pane=os.environ['TMUX_PANE']
assert subprocess.check_output(['tmux','display-message','-p','-t',pane,'#{pane_pipe}'],text=True).strip()=='0'
(J/'terminal.log').open('x').close()
subprocess.run(['tmux','pipe-pane','-t',pane,'-o','cat >> '+str(J/'terminal.log')],check=True)
cmd=['/opt/slurm/current/bin/srun','--immediate=60','--job-name=ad5w-firstbackward-interactive-v1','--partition=lem-gpu-interactive','--nodes=1','--ntasks=1','--cpus-per-task=8','--mem=120G','--gres=gpu:hopper:1,storage:local:150G','--time=00:15:00','--extra=FORCE_RM_TMPDIR','--pty','python3','-I',str(SRC/'worker.py')]
env=dict(HOME='/home/narolski',USER='narolski',LOGNAME='narolski',PATH='/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin',SHELL='/bin/bash',LANG='C',LC_ALL='C',TERM=os.environ.get('TERM','xterm'))
put('LAUNCH_INTENT.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv':cmd,'environment':env,'original_job':'6321768_401','release_sha256':sha(J/'MIGRATION_RELEASE.json')})
rc=subprocess.call(cmd,cwd=ROOT,env=env)
put('LAUNCH_EXIT.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'srun_exit':rc,'node_started':(J/'NODE_START.json').exists(),'automatic_retry':False})
print('AD5_INTERACTIVE_LAUNCH_FINISHED',rc,flush=True)
sys.exit(rc if rc>=0 else 128-rc)
