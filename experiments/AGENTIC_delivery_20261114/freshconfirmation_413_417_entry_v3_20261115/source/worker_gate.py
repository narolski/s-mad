"""Rechecks authority before the native shell may source its generated literal task."""
import hashlib,json,os,pathlib,sys
from authority_gate import need,Hold
from run_guarded import prepare_execution,exclusive_json
def main():
    here=pathlib.Path(__file__).resolve().parent
    raw=(here.parent/'POLICY.json').read_bytes();policy=json.loads(raw);policy['policy_sha256']=hashlib.sha256(raw).hexdigest()
    release,registration,task,row=prepare_execution({'path':os.environ['NEXT_ROOT_RELEASE'],'sha256':os.environ['NEXT_ROOT_RELEASE_SHA256']},policy,pathlib.Path(os.environ['TASK_DIR'])/'task.env')
    need(str(here)==policy['source_dir'],'source location mismatch')
    durable=pathlib.Path(policy['durable_root'])/task['TASK']
    need(pathlib.Path(os.environ['TASK_DIR'])==durable/'trusted_task','untrusted task dir')
    need(pathlib.Path(os.environ['NEXT_CONFIRM_TASK_DURABLE'])==durable,'durable path mismatch')
    need(durable.resolve()==durable,'durable symlink refused')
    claim=json.loads((durable/'CLAIM.json').read_text())
    need(claim.get('root_release_sha256')==os.environ['NEXT_ROOT_RELEASE_SHA256'] and claim.get('task')==task['TASK'] and claim.get('retry') is False,'claim mismatch')
    exclusive_json(durable/'WORKER_ENTERED.json',{'status':'ENTERED_ONCE','task':task['TASK'],'root_release_sha256':os.environ['NEXT_ROOT_RELEASE_SHA256']})
if __name__=='__main__':
    try:main()
    except (Hold,KeyError,ValueError,OSError) as e:
        print('HOLD worker: '+type(e).__name__+': '+str(e),file=sys.stderr);sys.exit(78)
