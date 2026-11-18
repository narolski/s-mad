import hashlib,json,pathlib
p=pathlib.Path('work/hn_smoke_review/evidence.json');e=json.loads(p.read_text());a=e['arms'];assert len(a)==2 and all(x['exists'] for x in a)
assert e['job_status_rc']==0 and e['job_status'].strip().split('|')[1:3]==['COMPLETED','0:0'],e['job_status']
expected={'dev':21277,'tt1':34411,'meds':1018,'gd':11042};reports=[]
for x in a:
 assert x['sha256']==x['sidecar_sha256'];assert x['source_sums_sha256']=='3640adc6a2204e1d82ce455167e00e433859f4b63bf63970f67d3ca0910ca793'
 g=x['gate'];assert g['n']==2496 and g['byte_identical'] and g['passed'] and g['gate_class']=='byte-gated' and g['n_differ']==g['max_abs']==0
 n=x['netcheck'];assert n['n_common']==21277 and n['passed'] and n['n_differ']==n['max_abs']==0
 assert x['battery_status']=='battery_rc=0\n';assert all(x['sets'][k]['n']==x['sets'][k]['n_scored']==v and x['sets'][k]['finite'] for k,v in expected.items())
 s=x['schedule'];assert s['steps']==s['exact_per_image_exposures']==2 and s['batch_size']==248 and s['total_image_exposures']==496 and s['seed']==531
 assert len(s['row_ids'])==len(set(s['row_ids']))==248
 assert sum(r.endswith('_P') for r in s['row_ids'])==124
 assert all(x['files'].get(k,0)>0 for k in ['last.pt','last_trainable.pt','meta.json','train.log','HN_warmstart.json'])
 w=x['warmstart'];assert w==a[0]['warmstart'] and w['trainable_parameter_names'] and len(set(w['trainable_parameter_names']))==len(w['trainable_parameter_names'])
 assert w['optimizer']=='fresh AdamW; no inherited moments' and w['conditioning']=='single admitted AB1 Sb408 initialization' and w['path'].endswith('/AB1_Sb_s408/last_trainable.pt')
 reports.append({'arm':x['arm'],'sha256':x['sha256'],'reference_bytegate':2496,'own_bytegate':21277,'finite_counts':expected,'rows':248,'image_exposures':496,'checkpoint_preserved':True,'task_info':x['task_info']})
normalize=lambda rr:[r.replace('_Nmatched','_N').replace('_Nself','_N') for r in rr]
assert normalize(a[0]['schedule']['row_ids'])==normalize(a[1]['schedule']['row_ids'])
report={'decision':'AUTHOR_TECHNICAL_PASS_INDEPENDENT_ROOT_RELEASE_REQUIRED','author_reviewer':'astra_sprint_plan_review','job':6321237,'job_status':e['job_status'].strip(),'scope':'author technical check, not independent methodology review; no scientific score payload opened','source_sums_sha256':a[0]['source_sums_sha256'],'evidence_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'warmstart':'same admitted AB1 Sb408 for both smoke arms','arms':reports,'next':'root independent review may release two arms x seeds531–535 x100updates; separate PREREAD required for scientific outputs'}
o=pathlib.Path('work/hn_smoke_review/AUTHOR_SMOKE_TECHNICAL_REVIEW.json');o.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));print('REVIEW_SHA256',hashlib.sha256(o.read_bytes()).hexdigest())
