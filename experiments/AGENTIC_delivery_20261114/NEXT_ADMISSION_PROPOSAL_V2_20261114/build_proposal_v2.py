"""Opaque-receipt and source-only v2; does not import or run NEXT."""
import pathlib,json,hashlib,subprocess,ast
R=pathlib.Path('/home/narolski/smad-next'); B=R/'experiments/AGENTIC_delivery_20261114'; V=B/'NEXT_ADMISSION_PROPOSAL_20261114'; O=B/'NEXT_ADMISSION_PROPOSAL_V2_20261114'
O.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(pathlib.Path(p).read_text())
def save(n,d):(O/n).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
a=read(V/'ADMISSION_PROPOSAL.json'); receipts=read(V/'ARRIVAL_RECEIPTS_DRAFT.json'); bindings=read(V/'SOURCE_BINDINGS.json')
p=B/'ROOT_AB1_TEN_COMPARATOR_OPAQUE_VERIFIED_20261114.json'; r=read(p)
bindings['sources'][str(p)]={'sha256':sha(p)}
for filename,e in r['archives'].items():
 key=filename[:-4]; arm=key.split('_')[1]; seed=int(key.rsplit('s',1)[1]); assert pathlib.Path(e['path']).is_file()
 a['networks'][key]={'archive':e['path'],'sha256':e['sha256'],'prefix':key,'arm':arm,'seed':seed,'format':'native_fit'}
 receipts[key]={'archive':e['path'],'sha256':e['sha256'],'hash_verified':True,'verified_at':r['at'],'evidence':str(p),'evidence_sha256':sha(p),'timestamp_interpretation':'fresh verification; no historical arrival inferred','local_exists':True,'producer_sha256':None,'producer_binding_status':'SOURCE_ONLY_RUNTIME_ATTESTATION_PENDING'}
for s in range(408,413):
 a['arms']['SbFM']['control'][str(s)]=f'AB1_A_s{s}'
 a['arms']['SbFM']['comparator'][str(s)]=f'AB1_Sb_s{s}'
 a['arms']['DINOv3']['comparator'][str(s)]=f'AB1_Sb_s{s}'
a['missing_archive_roles']=[]
man={x['key']:{'path':x['path'],'sha256':x['sha256']} for x in a['native_manifest_priors']}
support_path=R/'experiments/NEXT_method-selection-rule/inputs/support/support_v3.json'; support=read(support_path)
root='/mnt/t7/smad_next/'
paths={'fm_eval':'AB1/x/manifests/ab1x_eval.csv','train_A':'PN1/fs_tree/pn1/data/manifests/train_A.csv','train_Sb':'PN1/fs_tree/pn1/data/manifests/train_Sb.csv','train_SbFM':'AB1/fm/manifests/train_SbFM.csv','tt1':'TT1/tt1_score.csv','meds':'TT1/meds/meds_score.csv'}
for key,path in paths.items():
 expected=a['manifest_hash_priors'].get(key) or support['tt1_sha256' if key=='tt1' else 'meds_score_manifest_sha256']
 man[key]={'path':root+path,'sha256':expected}
for key,e in man.items():
 e['current_opaque_sha256']=sha(e['path']); e['matches_prior']=e['sha256']==e['current_opaque_sha256']; assert e['matches_prior'],key
a['native_manifests']={k:{'path':v['path'],'sha256':v['sha256']} for k,v in man.items()}
a['transfer_training_sha256']={k:man['train_'+k]['sha256'] for k in ('Sb','SbFM')}
for p in [support_path,R/'experiments/NEXT_method-selection-rule/inputs/support/pins.sha256',R/'src/NEXT/prepare_inputs.py',R/'src/NEXT/prepare_support.py',R/'src/RZ1/rz1_read.py',R/'src/TT1/tt1common.py']:
 bindings['sources'][str(p)]={'sha256':sha(p)}
for p in [R/'src/NEXT/read_selection.py',R/'src/NEXT/native_adapters.py']:
 assert bindings['sources'][str(p)]['sha256']==sha(p),'reader changed since v1'
bindings.update(head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(),parent_package_sha256=sha(V/'PACKAGE_SHA256SUMS'))
allow={}
for key,n in a['networks'].items():
 names=['gpu.txt','task_info.txt']
 if n['format']=='rz1_refit': names+=['gate.json']
 else:
  names+=['task.env','meta.json','train.log']
  if n['format']=='rz1_fit':names+=['rz1_transform.json','guard.log']
 allow[key]={'archive':n['archive'],'sha256':n['sha256'],'members':[n['prefix']+'/'+x for x in names],'basis':'src/NEXT/native_adapters.py:load_fit' if n['format']=='native_fit' else 'src/NEXT/read_selection.py:load_rz_network','metadata_gate_status':'NOT_READ','native_gate_implemented':n['arm']!='SbMR512'}
for key,sup in a['supplements'].items():
 if sup['format']=='sbfm_supplement':
  names=['config.json','pre_read_receipt.json','technical_status.json']+[f'gate_{origin}_s{s}.json' for origin in ('AB1FM_SbFM','AB1_Sb') for s in range(408,413)]
 else:
  names=['out/tasks.txt','out/gpu.txt','out/scripts.sha256','out/n_fail.txt','out/n_refused.txt']+[f'out/gate_BB2L_{arm}_s{s}.json' for arm in ('A','B','Sb') for s in range(403,408)]+[f'out/gate_AB1_Sb_s{s}.json' for s in range(408,413)]
 allow[key]={'archive':sup['archive'],'sha256':sup['sha256'],'members':names,'basis':'src/NEXT/native_adapters.py:load_'+sup['format'],'metadata_gate_status':'NOT_READ'}
assert len(a['networks'])==75
assert all(a['arms'][arm]['comparator'][str(s)]==f'RZ1_Sb0_s{s}' for arm in ('SbMR','SbM','Sb512','SbMR512','Sbc') for s in range(408,413))
assert all(a['networks'][a['arms'][arm][role][seed]]['seed']==int(seed) for arm in a['arms'] if arm!='GX' for role in ('candidate','control','comparator') for seed in a['arms'][arm][role])
save('ADMISSION_PROPOSAL.json',a);save('ARRIVAL_RECEIPTS_DRAFT.json',receipts);save('SOURCE_BINDINGS.json',bindings)
save('NATIVE_SOURCE_INVENTORY_DRAFT.json',{k:v['sha256'] for k,v in a['networks'].items() if v['format']=='native_fit'})
save('NATIVE_MANIFEST_BINDINGS_DRAFT.json',man)
save('TECHNICAL_METADATA_ALLOWLIST_PROPOSAL.json',{'schema':'next-technical-metadata-scope-proposal-v1','approved':False,'execution_authorized':False,'resource':'local CPU only, CUDA disabled','max_member_bytes':8388608,'archives':allow,'forbidden':['NPZ payload/header','weights','NEXT preflight/reader/journal','score metrics','archive extraction'],'output_policy':'exact metadata hashes and allowlisted technical identity/status fields; train.log finite-loss boolean only; no raw logs or scientific values','remaining':['collector implementation and independent review','explicit technical release','exposure attestation','author Sbc ruling','SbMR512 kernel and adapter review','GX source closure','clean final admission and independent scientific admission review']})
save('CHECKS.json',{'arm_order':list(a['arms']),'network_count':len(a['networks']),'new_unique_original_AB1':10,'filled_role_references':15,'native_manifests':len(man),'all_manifest_hashes_match':True,'missing_archive_roles':[],'source_reader_unchanged_from_v1':True,'all_status_HOLD':all(x['status']=='HOLD' for x in a['arms'].values()),'archive_members_opened':False,'scientific_read':False})
print(str(O))
