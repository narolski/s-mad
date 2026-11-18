import base64,hashlib,io,json,math,pathlib,torch
p=pathlib.Path('/tmp/tail_smoke_evidence.json');a=json.loads(p.read_text());assert len(a)==3 and all(x['exists'] for x in a)
expected={'dev':21277,'tt1':34411,'meds':1018,'gd':11042};reports=[]
def finite(x):
 if isinstance(x,dict):return all(finite(v) for v in x.values())
 if isinstance(x,list):return all(finite(v) for v in x)
 return not isinstance(x,(int,float)) or math.isfinite(x)
for x in a:
 assert x['sha256']==x['sidecar_sha256'];assert x['source_sums_sha256']=='9b50eff7aa5a90f72be7330e3550b0f8a76917dcac9b89516cc0a64ae7086ae1'
 g=x['gate'];assert g['n']==2496 and g['byte_identical'] and g['passed'] and g['gate_class']=='byte-gated' and g['n_differ']==g['max_abs']==0
 n=x['netcheck'];assert n['n_common']==21277 and n['passed'] and n['n_differ']==n['max_abs']==0
 assert x['battery_status']=='battery_rc=0\n'
 assert all(x['sets'][k]['n']==x['sets'][k]['n_scored']==v and x['sets'][k]['finite'] for k,v in expected.items())
 assert x['schedule']==a[0]['schedule'] and x['schedule']['steps']==2 and x['schedule']['row_exposures']==512
 assert x['reference']==a[0]['reference']
 assert all(x['files'].get(k,0)>0 for k in ['last.pt','last_trainable.pt','last_pt.sha256','meta.json','train.log','TRAIN_ONLY_reference.json'])
 report={'arm':x['arm'],'sha256':x['sha256'],'reference_bytegate':2496,'own_bytegate':21277,'finite_counts':expected,'checkpoint_preserved':True,'schedule_sha256':x['schedule']['schedule_sha256']}
 if x['arm']!='bce':
  tr=x['trace'];assert len(tr)==2 and [z['step'] for z in tr]==[0,1] and finite(tr)
  for i,z in enumerate(tr):
   assert sorted(z['effective_negative_identities'].values())==[22,32,32,32]
   assert all(0<=v<=z['effective_negative_identities'][k] for k,v in z['tail_occupancy'].items())
   assert all(abs(max(0,min(10,d+.01*v))-n)<1e-7 for d,v,n in zip(z['dual'],z['violation'],z['dual_after']))
   if i:assert z['dual']==tr[i-1]['dual_after'] and z['eta']==tr[i-1]['eta_after']
  state=torch.load(io.BytesIO(base64.b64decode(x['objective_state_base64'])),map_location='cpu',weights_only=True)
  assert state['effective_step']==1 and int(state['objective']['last_dual_step'])==1
  assert state['objective']['eta'].tolist()==tr[-1]['eta_after'] and state['objective']['dual'].tolist()==tr[-1]['dual_after']
  assert all(torch.isfinite(v).all() for v in state['objective'].values())
  if x['arm']=='cvar':
   assert any(tr[0]['eta'][j]!=tr[-1]['eta_after'][j] for j in range(4))
   assert len(state['eta_optimizer']['state'])==1
   assert all(float(v['step'])==2 for v in state['eta_optimizer']['state'].values())
  else:assert tr[0]['eta']==tr[-1]['eta_after'] and not state['eta_optimizer']['state']
  report.update(dual_commits=2,final_effective_step=1,final_eta=tr[-1]['eta_after'],final_dual=tr[-1]['dual_after'],tail_occupancy=[z['tail_occupancy'] for z in tr])
 reports.append(report)
out={'decision':'GO_15_PILOT_FITS_TECHNICAL','reviewer':'astra_sprint_plan_review','author':'sol_sprint_experiments','job':6321199,'source_sums_sha256':a[0]['source_sums_sha256'],'evidence_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scope':'metadata, byte gates, training traces and tiny objective-state tensors only; no scientific score arrays deserialized','fits':15,'steps_per_fit':100,'seeds':[521,522,523,524,525],'conditioning':'one admitted AB1 Sb408 common warmstart; stochastic continuation only','reader':'independent PREREAD required before scientific interpretation','arms':reports}
path=pathlib.Path('/home/narolski/smad-next/experiments/SPRINT5_20261114/tail/ASTRA_SMOKE_TECHNICAL_REVIEW.json');path.write_text(json.dumps(out,indent=2)+'\n');print(path,hashlib.sha256(path.read_bytes()).hexdigest());print(json.dumps(out,indent=2))
