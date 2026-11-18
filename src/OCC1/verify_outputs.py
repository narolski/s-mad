"""Verify actual OCC1 numerical outputs; no models or source image decoding."""
import csv,hashlib,json,math
from pathlib import Path
import numpy as np

O=Path('/mnt/t7/smad_next/OCC1/20261114')
models=['A','B','Sb','madation_vitb16','madation_vitl14','mixfacenet_mad_smdd','selfmad_hrnet_w18']
names=['R0','R2w','R2w4','R3','R4','S0','S3','S4']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sigmoid(x):return 1/(1+math.exp(-x)) if x>=0 else math.exp(x)/(1+math.exp(x))
reports=[];regional=[];paired=[];baseline=[];failures=[]
for model in models:
 d=O/(model+'_full');p=d/'result.json'
 if not p.exists():
  failed=O/(model+'_smoke')/'failure.json';r=json.loads(failed.read_text())
  assert r['status']=='FAILED' and not d.exists()
  failures.append(dict(model=model,disposition='FAILED_SMOKE_NO_FULL_SWEEP',reason=r['error'],failure_json=str(failed),sha256=sha(failed)))
  continue
 r=json.loads(p.read_text());assert r['status']=='COMPLETE' and r['finite_views']==1024
 assert r['source_pixels_exported'] is False and r['no_source_pixels_in_npz'] is True
 assert sha(d/'raw_responses.npz')==r['raw_npz_sha256']
 assert sha(d/'per_patch_scores.csv')==r['score_csv_sha256']
 with np.load(d/'raw_responses.npz',allow_pickle=False) as z:
  allowed={'conditions','fills','baseline_logits','occluded_logits','delta_logits','grid_yx','hull','seam_ring','surround','interior','seam_cell_indices','matched_surround_indices'}
  assert set(z.files)==allowed and z['conditions'].tolist()==names and z['fills'].tolist()==[0,128]
  assert z['occluded_logits'].shape==z['delta_logits'].shape==(8,2,8,8)
  for k in ('baseline_logits','occluded_logits','delta_logits'):assert np.isfinite(z[k]).all()
  np.testing.assert_array_equal(z['occluded_logits']-z['baseline_logits'][:,None,None,None],z['delta_logits'])
  grid=z['grid_yx'];delta=z['delta_logits'].reshape(8,2,64);occ=z['occluded_logits'].reshape(8,2,64);bas=z['baseline_logits']
  seams=z['seam_cell_indices'];controls=z['matched_surround_indices'];assert len(seams)==len(controls)==17
  rows=list(csv.DictReader((d/'per_patch_scores.csv').open()));assert len(rows)==1024
  ids=set()
  for x in rows:
   j=names.index(x['condition']);fi=[0,128].index(int(x['fill_rgb']));i=int(x['patch_index']);ids.add((j,fi,i))
   assert float(x['original_logit'])==bas[j] and float(x['occluded_logit'])==occ[j,fi,i] and float(x['delta_logit'])==delta[j,fi,i]
   assert [int(x['y']),int(x['x'])]==grid[i].tolist()
   assert abs(float(x['occluded_uncalibrated_score'])-sigmoid(float(x['occluded_logit'])))<1e-12
  assert len(ids)==1024
  for x in r['regional_effects']:
   j=names.index(x['condition']);fi=[0,128].index(x['fill_rgb'])
   sr=float(delta[j,fi,seams].mean());bg=float(delta[j,fi,controls].mean())
   assert x['seam_mean_delta']==sr and x['matched_surround_mean_delta']==bg and x['seam_minus_surround']==sr-bg
   regional.append(dict(model=model,**x))
  for x in r['paired_rung_effects']:
   a,b=names.index(x['first']),names.index(x['second']);fi=[0,128].index(x['fill_rgb']);dd=delta[a,fi]-delta[b,fi]
   np.testing.assert_array_equal(np.array(x['all_patch_delta_difference']),dd.reshape(8,8))
   assert x['baseline_logit_difference']==bas[a]-bas[b]
   assert x['seam_mean_difference_of_delta']==float(dd[seams].mean())
   assert x['matched_surround_mean_difference_of_delta']==float(dd[controls].mean())
   paired.append({k:v for k,v in dict(model=model,**x).items() if k!='all_patch_delta_difference'})
  for j,n in enumerate(names):baseline.append(dict(model=model,condition=n,logit_morph=float(bas[j]),uncalibrated_morph_score=sigmoid(float(bas[j]))))
 reports.append(dict(model=model,full_result_sha256=sha(p),seconds=r['seconds'],views=len(rows),passed=True,
                     files=[dict(path=str(q),sha256=sha(q),bytes=q.stat().st_size) for q in sorted(d.iterdir()) if q.is_file()]))
for name,rows in [('baseline_scores.csv',baseline),('regional_effects.csv',regional),('paired_rung_effects.csv',paired)]:
 with (O/name).open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
report=dict(status='COMPLETE_SWEEPS_VERIFIED_WITH_EXPLICIT_SMOKE_FAILURES',requested_models=7,complete_models=len(reports),complete_input_rungs=8,fills=2,patches_per_condition=64,
            actual_full_occluded_forwards=len(reports)*1024,source_pixels_exported=False,allowed_use='numeric-only in-place internalresearch; no sourceface/overlay export',
            checks=reports,failed_or_incomplete_full_runs=failures,
            caveats=['One fixed development host, not population evidence.',
                     'Seam-overlapping64pxpatches remove other facial content too.',
                     'Spatial controls area/shape-matched only, not texture/position.',
                     'Constant fill effects include replacement artifacts; twofills do not eliminate them.',
                     'Negative delta means less attack-like; scores uncalibrated; not error rates.',
                     'No source image pixels permitted in artifacts.'])
with (O/'NUMERICAL_OUTPUT_VERIFICATION.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print('PASS:',len(reports),'complete models,',len(reports)*1024,'actual fullocclusions;',len(failures),'explicit smokefailures; allCSV/NPZ/regional/paired identities',sha(O/'NUMERICAL_OUTPUT_VERIFICATION.json'))
