"""Bounded metadata authority checks. No model import or scientific reader."""
import hashlib,json,os,pathlib,re,stat

class Hold(ValueError): pass
def need(ok,msg):
    if not ok: raise Hold(msg)
def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
def control(rec):
    need(set(rec)=={'path','sha256'},'control descriptor fields')
    need(re.fullmatch('[0-9a-f]{64}',rec['sha256']) is not None,'digest format')
    fd=os.open(rec['path'],os.O_RDONLY|os.O_NOFOLLOW)
    try:
        st=os.fstat(fd);need(stat.S_ISREG(st.st_mode) and st.st_size<=1048576,'bounded regular control required')
        data=b''
        while True:
            chunk=os.read(fd,65536)
            if not chunk:break
            data+=chunk;need(len(data)<=1048576,'control too large')
    finally:os.close(fd)
    need(hashlib.sha256(data).hexdigest()==rec['sha256'],'control pin mismatch')
    return json.loads(data)
def validate_authority(release,policy):
    # release itself MUST already match the externally supplied exact root SHA.
    need(release.get('schema')=='next-common-ab1-root-release-v3','release schema')
    need(release.get('decision')=='GO_FRESH_COMMON_AB1_FIT_AND_REGISTERED_DEV_NATIVE_SCORE','explicit fit+development scorer release absent')
    need(release.get('permissions')==['COMMON_AB1_FIT','AB1_REGISTERED_DEV_EVAL_AND_TRAIN_NATIVE_SCORE'],'permission scope')
    need(release.get('sealed_access') is False and release.get('scientific_confirmation_read') is False,'scope escalation')
    need(release.get('policy_sha256')==policy['policy_sha256'],'policy pin')
    for key,expected in policy['fixed'].items():
        need(release.get(key)==expected,'fixed authority mismatch: '+key)
    branch=release.get('selected_branch');need(branch in policy['branches'] and branch!='GX','unavailable branch')
    if branch=='Sbc':need(release.get('crop_ruling_admitted') is True,'crop ruling absent')
    selected=control(release['selection_record'])
    need(selected.get('schema')=='next-selection-result-v1' and selected.get('stage')=='selection','selection schema/stage')
    need(selected.get('rule_sha256')==policy['fixed']['rule_sha256'],'selection rule mismatch')
    need(selected.get('choice')==branch and set(selected.get('arms',{}))==set(policy['branches']),'selection winner/dispositions mismatch')
    admission=control(release['selection_admission'])
    need(admission.get('decision')=='ADMIT_ONCE_SELECTION_FOR_FRESH_CONFIRMATION','selection independent admission absent')
    need(admission.get('selection_sha256')==release['selection_record']['sha256'] and admission.get('selected_branch')==branch,'admitted selection mismatch')
    need(admission.get('independent_review_sha256')==release.get('selection_independent_review_sha256'),'selection review mismatch')
    need(re.fullmatch('[0-9a-f]{64}',release.get('selection_independent_review_sha256','')) is not None,'selection review pin absent')
    registration=control(release['registration'])
    need(registration.get('schema')=='next-fresh-common-ab1-registration-v3','registration schema')
    need(registration.get('selected_branch')==branch and registration.get('full_cohort')==policy['cohorts'][branch],'cohort mismatch')
    need(registration.get('common_ab1_tasks')==policy['ab1_tasks'][branch],'common role subset mismatch')
    need(registration.get('steps')==6250 and registration.get('batch')==256 and registration.get('final')=='last','recipe mutation')
    need(registration.get('native_eval_manifest')=='ab1_eval.csv' and registration.get('native_train_scoring') is True,'native scorer permission mismatch')
    need(registration.get('durable_root')==policy['durable_root'],'fixed output root mismatch')
    need(registration.get('source_pins')==policy['source_pins'],'registered source mismatch')
    for name,decision in [('source_review','GO_COMMON_AB1_V3_SOURCE_AND_METHOD'),('runtime_input_admission','ADMIT_EXACT_AB1_RUNTIME_AND_INPUTS'),('resource_budget_admission','GO_EXACT_COMMON_AB1_RESOURCES_AND_BUDGET'),('duplicate_check','NO_DUPLICATE_FRESH_TASKS')]:
        c=control(release[name]);need(c.get('decision')==decision,'missing admission: '+name)
        need(c.get('registration_sha256')==release['registration']['sha256'],'admission registration mismatch: '+name)
        need(c.get('selected_branch')==branch,'admission branch mismatch: '+name)
    native=control(release['runtime_input_admission'])
    need(native.get('runtime_files')==release.get('runtime_files'),'runtime pin receipt mismatch')
    for k in ('runtime_home','cuda_visible_devices'):
        need(native.get(k)==release.get(k) and isinstance(release.get(k),str) and release[k],'runtime environment pin absent: '+k)
    need(native.get('input_files')==policy['input_files'],'input pin receipt mismatch')
    need(native.get('gpu_model')=='H100' and native.get('recipe_build')=='ORIGINAL_AB1_EXACT','platform/build mismatch')
    resources=control(release['resource_budget_admission'])
    need(resources.get('capacity_verified') is True and resources.get('budget_allocated') is True and resources.get('durability_verified') is True,'resources/budget/durability HOLD')
    need(resources.get('resources')==release.get('resources'),'resource allocation pin mismatch')
    res=release.get('resources',{})
    need(res.get('gpu')=='H100' and res.get('gpu_count')==1 and res.get('cpus')==8 and res.get('ram_gb')==64 and res.get('local_disk_gb')==80,'original resource shape mismatch')
    need(type(res.get('walltime_seconds')) is int and res['walltime_seconds']>0,'actual reviewed walltime absent')
    need(release.get('owned_source_commit_clean') is True,'clean owned-source commit absent')
    need(re.fullmatch('[0-9a-f]{40}',release.get('owned_source_commit','')) is not None,'source commit absent')
    return branch,registration
def verify_staged_bytes(release,policy):
    # Called only AFTER authority validation; opaque hashes, never checkpoint decode.
    need(set(release['runtime_files'])=={'python','bash','bootstrap_python'},'runtime exact file roster')
    need(release['runtime_files']['bootstrap_python']['path']=='/usr/bin/python3','bootstrap path')
    for rec in release['runtime_files'].values():
        need(digest(rec['path'])==rec['sha256'],'staged runtime drift')
    for rec in policy['input_files'].values():
        need(digest(rec['path'])==rec['sha256'],'staged input drift')
    for path,h in policy['source_pins'].items():need(digest(path)==h,'staged source drift')
def parse_task_env(path):
    # NO shell source/eval. Exactly three literal assignments; untrusted code refused.
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        need(stat.S_ISREG(os.fstat(fd).st_mode),'regular task env required')
        data=os.read(fd,4097).decode();need(len(data)<=4096,'task env too large')
    finally:os.close(fd)
    result={}
    for line in data.splitlines():
        m=re.fullmatch('(TASK|ARM|SEED)=([A-Za-z0-9_]+)',line)
        need(m is not None and m[1] not in result,'task.env not literal')
        result[m[1]]=m[2]
    need(set(result)=={'TASK','ARM','SEED'},'task fields')
    need(result['SEED'] in ['413','414','415','416','417'],'fresh seed refusal')
    return result
def validate_task(task,branch,policy):
    rows=policy['ab1_tasks'][branch]
    row=next((r for r in rows if r['task']==task['TASK']),None)
    need(row is not None,'task not in selected branch')
    need(row['producer_arm']=='AB1_'+task['ARM'] and str(row['seed'])==task['SEED'],'role/seed mismatch')
    return row
