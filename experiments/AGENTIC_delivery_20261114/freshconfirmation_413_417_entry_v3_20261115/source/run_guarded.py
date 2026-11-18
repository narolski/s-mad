"""Conditional executable entry. Requires an exact externally pinned root release."""
import argparse,hashlib,json,os,pathlib,signal,subprocess,sys,time
from authority_gate import control,validate_authority,verify_staged_bytes,parse_task_env,validate_task,need,Hold

def exclusive_json(path,record):
    with open(path,'x') as f:
        json.dump(record,f,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
def execute_claimed(command,env,durable,task_text):
    # An existing claim is terminal for this invocation; no auto retry/overwrite.
    durable.mkdir(mode=0o700) # parent created after authority validation
    exclusive_json(durable/'CLAIM.json',{'status':'CLAIMED','at':time.time(),'retry':False,'root_release_sha256':env.get('NEXT_ROOT_RELEASE_SHA256'),'task':durable.name})
    td=durable/'trusted_task';td.mkdir()
    with open(td/'task.env','x') as f:f.write(task_text);f.flush();os.fsync(f.fileno())
    os.chmod(td/'task.env',0o400)
    env=dict(env,TASK_DIR=str(td),NEXT_CONFIRM_TASK_DURABLE=str(durable))
    stdout=open(durable/'stdout.log','xb',buffering=0);stderr=open(durable/'stderr.log','xb',buffering=0)
    exclusive_json(durable/'STARTING.json',{'at':time.time(),'status':'STARTING'})
    child=None;old={};received=[]
    def stop(sig,frame):
        received.append(sig)
        if not (durable/'SIGNAL.json').exists():exclusive_json(durable/'SIGNAL.json',{'signal':sig,'at':time.time()})
        if child is not None:
            try:os.killpg(child.pid,sig)
            except ProcessLookupError:pass
    try:
        for s in (signal.SIGTERM,signal.SIGINT):old[s]=signal.signal(s,stop)
        child=subprocess.Popen(command,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
        exclusive_json(durable/'RUNNING.json',{'pid':child.pid,'at':time.time()})
        rc=child.wait()
        # Producer keeps the original full last checkpoint here before scoring.
        checkpoint=durable/'last.pt'
        status='COMPLETE' if rc==0 and checkpoint.is_file() and not received else 'FAILED_OR_INTERRUPTED'
        exclusive_json(durable/'TERMINAL.json',{'status':status,'exit_code':rc,'signals':received,'checkpoint_retained':checkpoint.is_file(),'at':time.time()})
        return 0 if status=='COMPLETE' else 1
    except BaseException as e:
        if not (durable/'TERMINAL.json').exists():exclusive_json(durable/'TERMINAL.json',{'status':'FAILED','error_type':type(e).__name__,'at':time.time()})
        raise
    finally:
        for s,h in old.items():signal.signal(s,h)
        stdout.close();stderr.close()
def prepare_execution(release_descriptor,policy,task_path):
    release=control(release_descriptor)
    branch,registration=validate_authority(release,policy)
    verify_staged_bytes(release,policy)
    task=parse_task_env(task_path);row=validate_task(task,branch,policy)
    return release,registration,task,row
def main():
    p=argparse.ArgumentParser();p.add_argument('--root-release',required=True);p.add_argument('--root-release-sha256',required=True);p.add_argument('--task-env',required=True);p.add_argument('--work-dir',required=True);a=p.parse_args()
    here=pathlib.Path(__file__).resolve().parent
    policy_path=here.parent/'POLICY.json';raw=policy_path.read_bytes();policy=json.loads(raw);policy['policy_sha256']=hashlib.sha256(raw).hexdigest()
    release,registration,task,row=prepare_execution({'path':a.root_release,'sha256':a.root_release_sha256},policy,a.task_env)
    # Task env was opened only after all authority and staged-byte checks.
    need(str(here)==policy['source_dir'],'exact staged source location required')
    work=pathlib.Path(a.work_dir).resolve();need(str(work).startswith('/tmp/') or str(work).startswith('/local/'),'local work required')
    need(work.is_dir() and not any(work.iterdir()),'fresh empty local work required')
    root=pathlib.Path(policy['durable_root'])
    need(root.resolve()==root,'symlinked durable namespace refused')
    need(not (root/task['TASK']).exists(),'existing task claim refused')
    for suffix in ('.tar','.tar.part','.tar.sha256'):
        need(not (root/'archives'/(task['TASK']+suffix)).exists(),'existing archive refused')
    root.mkdir(parents=True,exist_ok=True)
    task_text='TASK='+task['TASK']+'\nARM='+task['ARM']+'\nSEED='+task['SEED']+'\n'
    # Clean environment: no inherited script/test/LD/PYTHON/BASH_ENV/warmstart knobs.
    env={'PATH':'/usr/bin:/bin','HOME':release['runtime_home'],'LANG':'C.UTF-8','CUDA_VISIBLE_DEVICES':release['cuda_visible_devices'],'TASK_WORK':str(work),'PN1_ROOT':policy['hpc_root'],'PN1_PY':release['runtime_files']['python']['path'],'PN1_WORKERS':'7','NEXT_CONFIRM_AB1_RESULTS':str(root/'archives')}
    env.update(NEXT_ROOT_RELEASE=a.root_release,NEXT_ROOT_RELEASE_SHA256=a.root_release_sha256)
    return execute_claimed([release['runtime_files']['bash']['path'],str(here/'run_ab1_fresh.sh')],env,root/task['TASK'],task_text)
if __name__=='__main__':
    try:sys.exit(main())
    except (Hold,KeyError,ValueError,OSError) as e:
        print('HOLD: '+type(e).__name__+': '+str(e),file=sys.stderr);sys.exit(78)
