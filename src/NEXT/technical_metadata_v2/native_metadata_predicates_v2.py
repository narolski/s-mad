"""Pure source-bound metadata predicates. Inputs never serialized wholesale."""
import hashlib
import math
import re

LOSS_PATTERN = r'loss[ =:]+(-?(?:inf|nan)|[-+0-9.eE]+)'


def loss_predicate(text):
    matches=re.findall(LOSS_PATTERN,text,re.I)
    # Native load_fit uses generator/all short circuit. RZ first converts the
    # list. Preserve both results when a later malformed token is present.
    result={'presence':bool(matches),'count':len(matches)}
    for branch in ('native_fit','rz1_fit'):
        try:
            finite=all(math.isfinite(float(v)) for v in matches) if branch=='native_fit' else all(math.isfinite(v) for v in [float(x) for x in matches])
            result[branch]={'status':'PASS' if matches and finite else 'FAIL','all_finite':finite,'reason':'FINITE_LEXICAL_MATCHES' if matches and finite else 'ABSENT_OR_NONFINITE'}
        except (ValueError,OverflowError):
            result[branch]={'status':'UNKNOWN','all_finite':None,'reason':'LOSS_CONVERSION_ERROR'}
    return result


def state(value):return 'UNKNOWN' if value is None else ('PASS' if value else 'FAIL')


def row(identifier,source,evidence,native,integrity=None,raw_type='unavailable',reason='SOURCE_PREDICATE'):
    return {'predicate':identifier,'source':source,'evidence':evidence,'raw_type':raw_type,
            'native_status':state(native),'strict_integrity_status':state(integrity),
            'reason':reason if native is not None or reason!='SOURCE_PREDICATE' else 'MISSING_OR_UNRESOLVED_EVIDENCE'}


def typespec(value,spec):
    t=spec['type']
    return {'int':type(value) is int,'number':type(value) in (int,float),'str':type(value) is str,'bool':type(value) is bool}[t]


def compare_json(matrix,prefix,obj,schema,source,member,ignore=()):
    for field,spec in schema.items():
        if field in ignore or not isinstance(spec,dict) or 'type' not in spec:continue
        present=isinstance(obj,dict) and field in obj;v=obj.get(field) if present else None
        expected=spec.get('equals');native=None
        if present and 'equals' in spec:
            native=(v is expected) if spec['type']=='bool' else v==expected
        strict=typespec(v,spec) if present else None
        if strict and 'equals' in spec:strict=v==expected
        if spec.get('prospective_integrity_only'):native=None
        matrix.append(row(prefix+'.'+field,source,member,native,strict,type(v).__name__ if present else 'missing'))


def evaluate(record,evidence):
    """evidence contains only selected JSON leaves and allowlisted TXT bytes."""
    matrix=[];fmt=record.get('format');prefix=record.get('prefix','');kind=record.get('kind')
    for member,spec in record['members'].items():
        source=spec['source'];x=evidence.get(member);base=member.rsplit('/',1)[-1]
        if x is None:
            matrix.append(row(base,source,member,None,None,reason='MISSING_OR_REFUSED_MEMBER'));continue
        if spec.get('integrity_only'):
            if spec['kind']=='json':
                temporary=[];compare_json(temporary,base,x,spec['schema'],source,member)
                for r in temporary:r['native_status']='UNKNOWN';r['reason']='TECHNICAL_PROVENANCE_ONLY_NOT_NATIVE_REQUIREMENT'
                matrix.extend(temporary)
            else:matrix.append(row(base,source,member,None,None,'str','TECHNICAL_ENV_NOT_SCORER_RUNTIME'))
            continue
        if spec['kind']=='json':
            if base in ('config.json','technical_status.json') or base.startswith('gate_'):continue
            ignore=('manifest',) if fmt=='rz1_refit' and base=='gate.json' else ()
            compare_json(matrix,base,x,spec['schema'],source,member,ignore)
            if fmt=='rz1_refit' and base=='gate.json':
                device=x.get('device');matrix=[r for r in matrix if r['predicate']!='gate.json.device']
                matrix.append(row('gate.device_H100_substring',source,member,'H100' in device if type(device) is str else None,type(device) is str,type(device).__name__))
                matrix.append(row('gate.manifest_prospective_only',source,member,None,x.get('manifest')=='ab1_eval.csv',type(x.get('manifest')).__name__,'NOT_NATIVE_REQUIREMENT'))
        elif spec['kind']=='loss':
            result=loss_predicate(x);branch=result['rz1_fit' if fmt=='rz1_fit' else 'native_fit']
            matrix.append(dict(row('whole_log_lexical_loss',source,member,True if branch['status']=='PASS' else False if branch['status']=='FAIL' else None,None,'str',branch['reason']),lexical_presence=result['presence'],lexical_count=result['count'],all_finite=branch['all_finite'],conversion_reason=branch['reason']))
        elif spec['kind']=='gpu':
            needle='NVIDIA H100' if kind=='dinov3_w2' else 'H100'
            matrix.append(row('gpu_substring',source,member,needle in x,None,'str'))
        elif spec['kind']=='guard':
            matrix.append(row('pre_post_guard',source,member,'RZ1 GUARD pre ok' in x and 'RZ1 GUARD post ok' in x,None,'str'))
        elif spec['kind']=='env':
            lines=x.splitlines()
            for k,v in spec['expected'].items():
                native=(f'{k}={v}\n' in x+'\n') if fmt=='rz1_fit' else lines.count(f'{k}={v}')==1
                if fmt=='rz1_fit' and k=='TASK':native=None
                strict=sum(line.startswith(k+'=') for line in lines)==1 and lines.count(f'{k}={v}')==1
                matrix.append(row('task_env.'+k,source,member,native,strict,'str','TASK_IS_INTEGRITY_ONLY' if fmt=='rz1_fit' and k=='TASK' else 'SOURCE_PREDICATE'))
        elif spec['kind']=='tokens':
            tokens=x.split()
            for i,fragment in enumerate(spec.get('native_fragments',[])):
                matrix.append(row('recipe.grouped_fragment_'+str(i),source,member,fragment in x+' ',None,'str'))
            for k,vs in spec['expected'].items():
                indices=[i for i,t in enumerate(tokens) if t==k]
                strict=len(indices)==1 and tokens[indices[0]+1:indices[0]+1+len(vs)]==vs
                if fmt=='rz1_refit':native=(k+' '+' '.join(vs)) in x
                elif fmt=='rz1_fit':native=(k+' '+' '.join(vs)+' ') in x+' '
                else:native=strict
                if fmt=='native_fit' and prefix.startswith('BB2L') and k in ('bs','accum') and record.get('submitted_batch_proof') is None:native=None;strict=None
                matrix.append(row('recipe.'+k,source,member,native,strict,'str'))
        elif spec['kind']=='opaque':
            matrix.append(row('opaque_receipt_hash',source,member,hashlib.sha256(x).hexdigest()==spec['expected_sha256'],True,'bytes'))
        elif spec['kind']=='count':
            try:
                n=int(x);native=n>=0;strict=re.fullmatch(r'[0-9]{1,9}\s*',x) is not None
                matrix.append(dict(row(base,source,member,native,strict,'str'),nonnegative_count=n if n>=0 else None))
            except (ValueError,OverflowError):matrix.append(row(base,source,member,None,False,'str','INT_CONVERSION_ERROR'))
        elif spec['kind']=='scripts':
            lines=[line.split() for line in x.splitlines()]
            native=len(lines)==len(spec['expected']) and all(len(a)==2 for a in lines)
            if native:native={a[1].rsplit('/',1)[-1]:a[0] for a in lines}==spec['expected']
            matrix.append(row('script_pins',source,member,native,native,'str'))
        elif spec['kind']=='tasks':
            tasks=x.splitlines();unique=len(tasks)==len(set(tasks))
            matrix.append(row('planned20_tasks_integrity',source,member,None,unique and set(tasks)==set(spec['expected']),'str','SUBMITTED_INTEGRITY_NOT_NATIVE_FULLSET'))
            for name in spec['expected']:
                matrix.append(row('task_source.'+name,source,member,unique and tasks.count(name)==1,None,'str'))
    if fmt=='native_fit' and prefix.startswith('BB2L'):
        proof=record.get('submitted_batch_proof')
        matrix.append(row('exact_submitted_batch','native_adapters.py:215-220','source-bound submitted proof',None if proof is None else proof['batch_spec'] in ([256,1],[128,2]),None,'missing' if proof is None else 'dict','NO_POSTHOC_BATCH_CHOICE'))
    if record.get('kernel_support_metadata'):
        matrix.append(row('trainable_checkpoint_digest','src/RZ1/rz1_score.py:64-68,123-129','last_trainable.pt descriptor only; info.last_pt_sha256 binds full last.pt',None,None,'missing','NO_RECORDED_TRAINABLE_DIGEST_NO_WEIGHT_ACCESS'))
        matrix.append(row('scorer_TF32_noTTA_runtime','src/RZ1/rz1_score.py:56-57,79-86,94-96','source prior only; env.txt is a fresh process',None,None,'missing','SOURCE_PRIOR_NOT_RUNTIME_ATTESTATION'))
    if kind=='sbfm_supplement':matrix+=supplement(record,evidence)
    if kind=='dinov3_w2':
        for model in record['models']:
            name=model['name'];member='out/gate_'+name+'.json';obj=evidence.get(member)
            if obj is None:matrix.append(row('exact_gate.'+name,'native_adapters.py:75-81',member,None));continue
            compare_json(matrix,'exact_gate.'+name,obj,record['members'][member]['schema'],'native_adapters.py:75-81',member)
    matrix.append(row('scientific_payload_and_eligibility','registered NEXT once reader','NPZ/row IDs/floors/C2P/NI/kernel/exposure',None,None,reason='DEFERRED_TO_REGISTERED_ONCE_READER'))
    return matrix


def supplement(record,evidence):
    source='native_adapters.py:108-153';m=[];cfg=evidence.get('config.json');status=evidence.get('technical_status.json')
    for member,obj in [('config.json',cfg),('technical_status.json',status)]:
        if obj is None:m.append(row(member,source,member,None));continue
        compare_json(m,member,obj,record['members'][member]['schema'],source,member)
    m.append(row('config_opaque_digest',source,'config.json',evidence.get('_config_digest')==record['config_sha256'] if '_config_digest' in evidence else None,True,'sha256'))
    planned=[x['name'] for x in record['models']]
    for member,obj in [('config.json',cfg),('technical_status.json',status)]:
        models=obj.get('models') if isinstance(obj,dict) else None
        names=[x.get('name') for x in models if isinstance(x,dict)] if isinstance(models,list) else []
        integrity=isinstance(models,list) and len(names)==len(models)==len(planned) and all(type(x) is str for x in names) and sorted(names)==sorted(planned)
        m.append(row('planned_model_association_integrity.'+member,source,member,None,integrity if models is not None else None,'list' if models is not None else 'missing','STRICT_PLANNED_ROSTER_NOT_GLOBAL_NATIVE_GATE'))
    for model in record['models']:
        name=model['name'];cg=cfg.get('models') if isinstance(cfg,dict) else None;sg=status.get('models') if isinstance(status,dict) else None
        cr=[x for x in cg if isinstance(x,dict) and x.get('name')==name] if isinstance(cg,list) else []
        sr=[x for x in sg if isinstance(x,dict) and x.get('name')==name] if isinstance(sg,list) else []
        exact=len(cr)==1 and all(cr[0].get(k)==v for k,v in model.items())
        m.append(row('configured_tuple.'+name,source,'config.json',exact if cg is not None else None,exact,'list' if cg is not None else 'missing'))
        if len(cr)==1:
            compare_json(m,'configured_field.'+name,cr[0],{k:{'type':'int' if type(v) is int else 'str','equals':v} for k,v in model.items()},source,'config.json')
        unique=len(sr)==1;m.append(row('status_unique_seed_gate.'+name,source,'technical_status.json',unique and sr[0].get('seed')==model['seed'] and sr[0].get('gate')=='passed' if sg is not None else None,unique,'list' if sg is not None else 'missing'))
        fam=sr[0].get('families') if unique else None
        valid=isinstance(fam,list) and len(fam)==2 and all(isinstance(f,dict) and type(f.get('name')) is str for f in fam) and {f.get('name') for f in fam}=={'tt1','meds'}
        m.append(row('families_exact.'+name,source,'technical_status.json',valid if fam is not None else None,valid,'list' if isinstance(fam,list) else 'missing'))
        for family in ('tt1','meds'):
            fs=[f for f in fam if isinstance(f,dict) and f.get('name')==family] if isinstance(fam,list) else []
            native=len(fs)==1 and fs[0].get('valid') is True
            strict=native and type(fs[0].get('sha256')) is str and re.fullmatch('[0-9a-f]{64}',fs[0]['sha256']) is not None
            m.append(row('family_valid_digest.'+name+'.'+family,source,'technical_status.json',native if fam is not None else None,strict,'list'))
        member='gate_'+name+'.json';obj=evidence.get(member)
        if obj is None:m.append(row('exact_gate.'+name,source,member,None));continue
        compare_json(m,'exact_gate.'+name,obj,record['members'][member]['schema'],'native_adapters.py:75-81',member)
    return m
