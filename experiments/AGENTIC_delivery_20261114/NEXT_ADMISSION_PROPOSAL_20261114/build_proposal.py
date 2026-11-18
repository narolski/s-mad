"""Source/receipt-only draft builder. Never imports reader or opens archives."""
import ast, hashlib, json, pathlib, subprocess
R=pathlib.Path('/home/narolski/smad-next'); C=pathlib.Path('/mnt/t7/smad_next/coordination_20261114')
O=R/'experiments/AGENTIC_delivery_20261114/NEXT_ADMISSION_PROPOSAL_20261114'
O.mkdir(exist_ok=False)
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def j(p): return json.loads(pathlib.Path(p).read_text())
def save(n,x): (O/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
sources={}
def source(p):
 p=pathlib.Path(p); sources[str(p)]={'sha256':sha(p)}; return j(p)
old=source(R/'experiments/NEXT_method-selection-rule/OPENCODE_ADMISSION_READINESS_20261114.json')
receipts={}
def add(p,entry,local,time):
 name=pathlib.Path(local).name
 receipts[name[:-4]]={'archive':str(local),'sha256':entry['sha256'],'hash_verified':True,'verified_at':time,'evidence':str(p),'evidence_sha256':sha(p),'local_exists':pathlib.Path(local).is_file(),'producer_sha256':None,'producer_binding_status':'SOURCE_ONLY_RUNTIME_ATTESTATION_PENDING'}
p=pathlib.Path('/mnt/t7/smad_next/recovery_20261114_MAIN/COLLECTION_VERIFIED.json'); d=source(p)
for e in d['archives']:
 if pathlib.Path(e['path']).name.startswith(('AB1_','AB1FM_','BB2L_','RZ1_')): add(p,e,e['path'],d['at'])
for folder in ['next_final_output_collection_20261114T185258Z','sbfm_collection_20261114T160056Z']:
 p=C/folder/'COLLECTION_VERIFIED.json'; d=source(p)
 for e in d['files']:
  if e['name'].endswith('.tar'): add(p,e,C/folder/e['name'],d.get('at',d.get('observed_at')))
p=R/'experiments/AGENTIC_delivery_20261114/ROOT_RZ1_FIFTEEN_OPAQUE_ARRIVAL_VERIFIED_20261114.json'; d=source(p)
for name,e in d['archives'].items():
 q=pathlib.Path(e['source_receipt']); z=source(q)
 add(q,{'sha256':e['archive_sha256']},e['archive_path'],z.get('at',z.get('observed_at')))
text=(R/'src/NEXT/read_selection.py').read_text(); constants={}
for node in ast.parse(text).body:
 if isinstance(node,ast.Assign):
  for t in node.targets:
   if isinstance(t,ast.Name) and t.id in ['AB1_SB_SOURCE_PINS','NATIVE_PRODUCERS','NATIVE_MANIFEST_PINS']:
    constants[t.id]=ast.literal_eval(node.value)
net={}; arms={}; missing=[]
def network(prefix,arm,seed,fmt):
 if prefix not in receipts: missing.append(prefix); return None
 n={k:receipts[prefix][k] for k in ['archive','sha256']}; n.update(prefix=prefix,arm=arm,seed=seed,format=fmt)
 if prefix.startswith('BB2L_'): n['batch_spec']=[256,1]
 if fmt=='rz1_refit': n['source_network']={'name':f'AB1_Sb_s{seed}.tar','sha256':constants['AB1_SB_SOURCE_PINS'][seed]}
 net[prefix]=n; return prefix
for name in ['SbFM','GX','SbMR','SbM','Sb512','SbMR512','Sbc','DINOv3']:
 seeds=list(range(403,408)) if name=='DINOv3' else list(range(408,413))
 a={'status':'HOLD','proposed_final_disposition':None,'seeds':seeds,'pre_binding_scientific_open':None,'eligibility_review':None}
 if name=='GX': a['blockers']=['Amendment-2 inputs, generation/training provenance, floors, ten fits and native adapter evidence unresolved']; arms[name]=a; continue
 if name in ('SbFM','DINOv3'):
  for role,arm,ss in [('candidate','Sb' if name=='DINOv3' else 'SbFM',seeds),('control','A',seeds),('comparator','Sb',list(range(408,413)))]+([('fit_guard','B',seeds)] if name=='DINOv3' else []):
   origin='BB2L' if name=='DINOv3' and role!='comparator' else ('AB1FM' if role=='candidate' else 'AB1')
   a[role]={str(s):network(f'{origin}_{arm}_s{s}',arm,s,'native_fit') for s in ss}
  a['supplement']='BB2LW2' if name=='DINOv3' else 'AB1FMSUPP_20261114'
 else:
  for role,arm in [('candidate',name),('comparator','Sb0'),('control','A512' if name in ('Sb512','SbMR512') else 'A0'),('yardstick','Sb')]:
   a[role]={str(s):network(f'RZ1R_Sb_s{s}' if role=='yardstick' else f'RZ1_{arm}_s{s}',arm,s,'rz1_refit' if role=='yardstick' else 'rz1_fit') for s in seeds}
 a['blockers']=['Independent exposure/eligibility attestation','Technical metadata release and verified runtime gates','Clean committed exact admission and independent review']
 if name=='Sbc': a['blockers']+=['Author crop ruling pending; no presumed answer']; a['crop_scope_ruling']=None
 if name=='SbMR512': a['blockers']+=['Prospective registered kernel check and reviewed native adapter; code gap is not scientific ineligibility']
 arms[name]=a
supp={}
for key,fmt in [('BB2LW2','dinov3_w2'),('AB1FMSUPP_20261114','sbfm_supplement')]:
 prod,h=constants['NATIVE_PRODUCERS'][fmt]
 supp[key]={k:receipts[key][k] for k in ['archive','sha256']}; supp[key].update(format=fmt,producer_source=prod,producer_sha256=h,runtime_producer_verified=False)
 if fmt=='sbfm_supplement': supp[key].update(config='src/recovery_20261114/sbfm_supplement/config.json',config_sha256=sha(R/'src/recovery_20261114/sbfm_supplement/config.json'))
for p in ['src/NEXT/read_selection.py','src/NEXT/native_adapters.py','experiments/NEXT_method-selection-rule/prereg_draft_v3.md','experiments/reviews/PRERUN_NEXT_NATIVE_OPENCODE_20261114.md','experiments/BB2_second-backbone/seed_mode_L.json','experiments/RZ1_input-resolution-and-resize/prereg.md','experiments/NEXT_method-selection-rule/inputs/SHA256SUMS','experiments/NEXT_method-selection-rule/support/SHA256SUMS']:
 if (R/p).is_file(): sources[str(R/p)]={'sha256':sha(R/p)}
save('ADMISSION_PROPOSAL.json',dict(schema='next-admission-proposal-v1',approved=False,batch_closed=False,status='NOT_ADMITTED',stage='selection',deadline='2026-11-15T18:00:00+01:00',arms=arms,networks=net,supplements=supp,native_source_inventory='NATIVE_SOURCE_INVENTORY_DRAFT.json',native_manifest_priors=old['native_manifest_inventory_additions'],manifest_hash_priors=constants['NATIVE_MANIFEST_PINS'],dinov3_seed_mode='experiments/BB2_second-backbone/seed_mode_L.json',receipt_manifest='ARRIVAL_RECEIPTS_DRAFT.json',missing_archive_roles=missing))
save('NATIVE_SOURCE_INVENTORY_DRAFT.json',{k:v['sha256'] for k,v in net.items() if v['format']=='native_fit'})
save('ARRIVAL_RECEIPTS_DRAFT.json',{k:v for k,v in receipts.items() if k in net or k in supp or k.startswith('RZ1R_A_')})
save('SOURCE_BINDINGS.json',dict(head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(),sources=sources,producer_priors=constants['NATIVE_PRODUCERS'],production_code_imported=False,archive_members_opened=False,scientific_read=False))
save('CHECKS.json',dict(arm_order=list(arms),network_count=len(net),missing_archive_roles=missing,missing_local_paths=[k for k,v in receipts.items() if (k in net or k in supp) and not v['local_exists']],draft_only=True))
print(json.dumps({'path':str(O),'networks':len(net),'missing':missing}))
