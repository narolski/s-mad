"""Source-only scope compilation. No candidate archive operations."""
import ast,hashlib,json,pathlib
R=pathlib.Path('/home/narolski/smad-next');B=R/'experiments/AGENTIC_delivery_20261114';V=B/'NEXT_TECHNICAL_COLLECTOR_V1_20261114';P=B/'NEXT_ADMISSION_PROPOSAL_V2_20261114';O=B/'NEXT_TECHNICAL_COLLECTOR_V2_20261114'
assert not (O/'PACKAGE_SHA256SUMS').exists(),'frozen package must not be overwritten'
O.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
scope=read(V/'TYPED_SCOPE.json');a=read(P/'ADMISSION_PROPOSAL.json');cfg=read(R/'src/recovery_20261114/sbfm_supplement/config.json')
pins={}
for node in ast.parse((R/'src/NEXT/read_selection.py').read_text()).body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PINS' for t in node.targets):pins={k.arg:ast.literal_eval(k.value) for k in node.value.keywords}
unknown=[]
for key,rec in scope['archives'].items():
 n=a['networks'].get(key)
 if n:
  rec.update(format=n['format'],prefix=n['prefix'],arm=n['arm'],seed=n['seed'])
  if key.startswith('BB2L'):
   rec['submitted_batch_proof']=None;unknown.append({'record':key,'gap':'EXACT_SUBMITTED_BS_ACCUM_PROOF','allowed_registered_pairs':[[256,1],[128,2]],'status':'UNKNOWN','not_acceptable_as_proof':'old draft unconditional batch_spec or posthoc observed task_info'})
  if n['format']=='rz1_refit':
   spec=rec['members'][key+'/task_info.txt'];spec['expected'].update({k:[v] for k,v in pins.items()});spec['expected'].update(rz1_rescore=['02628562fb495cfedabd0e409db1b397fd0fb2d90ff4886ce4f865764b94bfd6'],train_manifest=['train_A.csv' if n['arm']=='A' else 'train_Sb.csv'])
  if key.startswith('BB2L'):
   spec=rec['members'][key+'/task_info.txt'];spec['expected'].pop('bs',None);spec['expected'].pop('accum',None)
  if n['arm']=='SbMR512':
   rec['kernel_support_metadata']={'full_checkpoint_descriptor':'original training run last.pt; opaque hash only if present in info.last_pt_sha256','trainable_checkpoint_member':key+'/last_trainable.pt','trainable_checkpoint_sha256':None,'weights_access_authorized':False,'scorer_source_sha256':sha(R/'src/RZ1/rz1_score.py'),'runtime_TF32':None,'source_TF32_prior':True,'source_read_value':'float32 forward_logit without flip; source also computes separate TTA output','scientific_rebuild_or_kernel_admission':False}
   schema={'torch':{'type':'str','emit_version':True},'device':{'type':'str','emit_gpu':True},'seed':{'type':'int','equals':n['seed']},'steps':{'type':'int','equals':6250},'res':{'type':'int','equals':512},'primary':{'type':'str','equals':'fixed:pil_bilinear'},'last_pt_sha256':{'type':'str','sha256':True,'emit_hex':True},'common_py_sha256':{'type':'str','sha256':True,'emit_hex':True},'rz1_kernels_sha256':{'type':'str','equals':sha(R/'src/RZ1/rz1_kernels.py'),'emit_hex':True},'limit':{'type':'int','equals':0}}
   rec['members'][key+'/info.json']={'kind':'json','schema':schema,'integrity_only':True}
   rec['members'][key+'/env.txt']={'kind':'technical_env','integrity_only':True}
   rec['members'][key+'/meta.json']['schema']['arch']={'type':'str','equals':'a12_clip_vitb16_madation','prospective_integrity_only':True}
   rec['members'][key+'/rz1_transform.json']['schema']['res512']={'type':'str','equals':'1','prospective_integrity_only':True}
 else:
  sup=a['supplements'][key];rec['kind']=sup['format']
  if rec['kind']=='sbfm_supplement':
   rec['models']=[{k:m[k] for k in ('name','seed','sha256','gate_manifest','gate_rows')} for m in cfg['models']];rec['config_sha256']=sup['config_sha256']
  else:rec['models']=[{'name':k,'sha256':v['sha256']} for k,v in a['networks'].items() if k.startswith('BB2L_') or k.startswith('AB1_Sb_')]
 for member,spec in rec['members'].items():
  base=member.rsplit('/',1)[-1]
  if n:
   source='src/NEXT/native_adapters.py:192-234:load_fit' if n['format']=='native_fit' else 'src/NEXT/read_selection.py:543-606:load_rz_network'
  else:source='src/NEXT/native_adapters.py:108-153:load_sbfm_supplement' if rec['kind']=='sbfm_supplement' else 'src/NEXT/native_adapters.py:165-189:load_dinov3_w2'
  spec['source']=source
  if base=='info.json':spec['source']='src/RZ1/rz1_score.py:123-129:info_selected_keys_only'
  if base=='env.txt':spec['source']='src/RZ1/run_rz1.sh:119:fresh_env_process'
  if n and n['format']=='rz1_fit' and base=='task_info.txt':
   e=spec['expected'];spec['native_fragments']=['res '+e['res'][0]+' bs '+e['bs'][0]+' accum '+e['accum'][0]+' ','steps 6250 limit 0 skip_tt1 0']
scope['schema']='next-typed-technical-scope-v2';scope['known_partial_checks']=['BB2 exact per-record submitted batch proof missing:15 UNKNOWN','Scientific NPZ/ID/floors/C2P/NI/kernel/exposure DEFERRED','No Sbc or SbMR512 policy ruling']
paths=[V/'TYPED_SCOPE.json',B/'ROOT_NEXT_V2_IMPLEMENTATION_ADOPTION_20261114T192658Z.json',B/'NEXT_ELIGIBILITY_UNBLOCK_PLAN_20261114.md',B/'NEXT_ELIGIBILITY_SOURCE_REVIEW_20261114/INDEPENDENT_PLAN_REVIEW.md',B/'NEXT_ELIGIBILITY_SOURCE_REVIEW_20261114/SOURCE_GRAMMAR_MAP.json']
grammar=read(paths[-1]);receipt=pathlib.Path('/mnt/t7/smad_next/coordination_20261114/next_training_source_only_20261114T192658Z/SOURCE_EXTRACTION_RECEIPT.json');sourcefiles=read(receipt)['files'];paths.append(receipt)
assert len(sourcefiles)==65
for x in sourcefiles:
 p=pathlib.Path(x['source_path']);assert sha(p)==x['sha256'];scope['pins'][str(p)]=x['sha256']
for p in paths:scope['pins'][str(p)]=sha(p)
for p in [R/'src/RZ1/rz1_score.py',R/'src/RZ1/run_rz1.sh',R/'src/RZ1/rz1_train.py',R/'src/RZ1/rz1_kernels.py']:scope['pins'][str(p)]=sha(p)
scope['whole_log_authorization']={'adoption':str(paths[1]),'output_scope':'presence/count/finite booleans; no captures/values/lines/labels','real_access_now':False}
(O/'TYPED_SCOPE.json').write_text(json.dumps(scope,indent=2)+'\n')
(O/'UNKNOWN_PROOFS.json').write_text(json.dumps({'per_record':unknown,'global':['Independent implementation review','Root technical-only release','Per-arm exposure/eligibility','Sbc author ruling','GX closure','SbMR512 separate adoption','Registered scientific payload checks']},indent=2)+'\n')
(O/'SOURCE_PREDICATE_MAP.json').write_text(json.dumps({'archives':{k:{m:{'kind':s['kind'],'source':s['source'],'fields':list(s.get('schema',s.get('expected',{}))) if isinstance(s.get('schema',s.get('expected',{})),dict) else None} for m,s in r['members'].items()} for k,r in scope['archives'].items()},'registered_seed_denominator':5,'scientific_predicates':'DEFERRED_TO_REGISTERED_ONCE_READER'},indent=2)+'\n')
print('V2_SCOPE_PREPARED_77_RECORDS_15_BATCH_PROOF_UNKNOWNS')
