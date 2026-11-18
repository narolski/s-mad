"""Bind completed outputs; no model inference or closed scientific reads."""
import csv,hashlib,json
from pathlib import Path
import numpy as np
R=Path('/home/narolski/smad-next')
O=R/'manuscript_cvpr2027/figures/shortcut_attribution_20261114'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
dirs=['A_fp32','B_fp32','Sb_fp64','madation_vitb16_fp32','madation_vitl14_fp32','mixfacenet_mad_smdd_fp32','selfmad_hrnet_w18_fp32']
allrows=[]; receipts=[]
for directory in dirs:
 p=O/directory/'result.json'
 if not p.is_file():raise ValueError('Missing accepted complete output: '+str(p))
 x=json.loads(p.read_text())
 assert x['status']=='COMPLETE' and x['head_zero_algebraic_check']['passed']
 assert [r['condition'] for r in x['results']]==['native','storage','border']
 for r in x['results']:
  n=O/directory/(r['condition']+'_raw.npz')
  assert sha(n)==r['raw_npz_sha256']
  with np.load(n,allow_pickle=False) as z:
   assert set(z.files)=={'input','gradient','gradient_times_input','signed','magnitude','gradient_magnitude'}
   assert all(np.isfinite(z[k]).all() for k in z.files)
   assert z['input'].shape==z['gradient'].shape==z['gradient_times_input'].shape
   np.testing.assert_array_equal(z['input']*z['gradient'],z['gradient_times_input'])
   np.testing.assert_array_equal(z['gradient_times_input'].sum(0),z['signed'])
  allrows.append(dict(model=x['model'],precision_directory=directory,condition=r['condition'],
                      logit_morph=r['logit_morph'],probability_morph_noTTA=r['score_noTTA'],
                      probability_morph_flipTTA=r['score_TTA'],logit_delta_from_native=r['logit_delta_from_native'],
                      raw_npz=str(n),raw_npz_sha256=sha(n),result_json=str(p),result_sha256=sha(p)))
 receipts.append(dict(directory=directory,result_sha256=sha(p),seconds=x['seconds'],
                      files=[dict(name=q.name,bytes=q.stat().st_size,sha256=sha(q)) for q in sorted((O/directory).iterdir()) if q.is_file()]))
out=O/'per_image_scores.csv'
with out.open('x',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
report=dict(scope='Private single-person descriptive gradient sensitivity pilot; not benchmark or inferential evidence',
             complete_models=7,conditions=3,raw_map_files=21,receipts=receipts,
             score_csv_sha256=sha(out),failed_attempts=[dict(path=str(O/d/'failure.json'),sha256=sha(O/d/'failure.json')) for d in ('A','Sb_fp32')],
             caveats=['Sb maps use higher-precision network/input arithmetic, other6 use float32; no cross-model magnitude inference.',
                      'Only existing aligned-frame preprocessing; SelfMAD is not own-crop evaluation.',
                      'Signed grad-times-input zeroes black input; raw gradient magnitude is separately preserved.',
                      'All3fixed conditions share deterministic maximum scale per model/type.',
                      'Private CC BY-NC draft; publication/likeness clearance pending.'])
with (O/'OUTPUT_MANIFEST.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print('PASS seven completed models,21maps, rawarray identity and exact file hashes',sha(O/'OUTPUT_MANIFEST.json'))
