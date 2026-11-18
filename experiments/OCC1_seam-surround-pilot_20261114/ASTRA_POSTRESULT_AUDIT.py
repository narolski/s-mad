import csv,json,hashlib,math,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
R=Path('/home/narolski/smad-next'); E=R/'experiments/OCC1_seam-surround-pilot_20261114'; O=Path('/mnt/t7/smad_next/OCC1/20261114'); hashes={}
def pin(p):
 p=Path(p); h=hashlib.sha256(p.read_bytes()).hexdigest();hashes[str(p)]=h;return h
def rows(p):pin(p);return list(csv.DictReader(p.open()))
def eq(a,b):assert abs(float(a)-float(b))<1e-12,(a,b)
a=json.loads((E/'PARENT_INTERNAL_RESEARCH_ADMISSION_20261114.json').read_text())
for p,h in a['pins'].items():assert pin(R/p)==h
for p in ['PARENT_INTERNAL_RESEARCH_ADMISSION_20261114.json','ASTRA_PRERUN_REVIEW_20261114.md','result.md']:pin(E/p)
for p in ['FIGURES_OWNER_HANDOFF_20261114.md','SOL_FIGURES.md']:pin(R/'experiments/AGENTIC_delivery_20261114'/p)
for p in ['render_numeric_v2.py','verify_outputs.py']:pin(R/'src/OCC1'/p)
base=rows(O/'baseline_scores.csv'); reg=rows(O/'regional_effects.csv'); pair=rows(O/'paired_rung_effects.csv');assert (len(base),len(reg),len(pair))==(40,80,50)
models=['A','B','Sb','mixfacenet_mad_smdd','selfmad_hrnet_w18'];names=['R0','R2w','R2w4','R3','R4','S0','S3','S4']; summary=[]
for m in models:
 d=O/(m+'_full');pin(d/'result.json');r=json.loads((d/'result.json').read_text());assert r['status']=='COMPLETE' and r['finite_views']==1024 and not r['smoke'];assert not r['source_pixels_exported']
 assert pin(d/'raw_responses.npz')==r['raw_npz_sha256']; assert pin(d/'per_patch_scores.csv')==r['score_csv_sha256']
 with np.load(d/'raw_responses.npz',allow_pickle=False) as z:
  assert set(z.files)=={'conditions','fills','baseline_logits','occluded_logits','delta_logits','grid_yx','hull','seam_ring','surround','interior','seam_cell_indices','matched_surround_indices'}
  assert z['conditions'].tolist()==names and z['fills'].tolist()==[0,128]
  b=z['baseline_logits']; q=z['occluded_logits']; delta=q-b[:,None,None,None];assert q.shape==(8,2,8,8) and np.isfinite(q).all();np.testing.assert_array_equal(delta,z['delta_logits']);flat=delta.reshape(8,2,64)
  grid=np.array([(y,x) for y in range(0,512,64) for x in range(0,512,64)]);np.testing.assert_array_equal(grid,z['grid_yx'])
  seam=np.array([i for i,(y,x) in enumerate(grid) if z['seam_ring'][y:y+64,x:x+64].mean()>=.1]);sur=np.array([i for i,(y,x) in enumerate(grid) if z['surround'][y:y+64,x:x+64].all()])[:len(seam)]
  np.testing.assert_array_equal(seam,z['seam_cell_indices']);np.testing.assert_array_equal(sur,z['matched_surround_indices']);assert len(seam)==len(sur)==17 and seam[0]==18
  seen=set()
  for x in rows(d/'per_patch_scores.csv'):
   j=names.index(x['condition']);f=[0,128].index(int(x['fill_rgb']));i=int(x['patch_index']);seen.add((j,f,i));eq(x['original_logit'],b[j]);eq(x['occluded_logit'],q.reshape(8,2,64)[j,f,i]);eq(x['delta_logit'],flat[j,f,i]);assert [int(x['y']),int(x['x'])]==grid[i].tolist();eq(x['occluded_uncalibrated_score'],1/(1+np.exp(-float(x['occluded_logit']))))
  assert len(seen)==1024
  for x in [v for v in base if v['model']==m]:
   j=names.index(x['condition']);eq(x['logit_morph'],b[j]);eq(x['uncalibrated_morph_score'],1/(1+np.exp(-b[j])))
  for x in r['regional_effects']+[v for v in reg if v['model']==m]:
   j=names.index(x['condition']);f=[0,128].index(int(x['fill_rgb']));s=sum(flat[j,f,i] for i in seam)/17;c=sum(flat[j,f,i] for i in sur)/17
   eq(x['seam_mean_delta'],s);eq(x['matched_surround_mean_delta'],c);eq(x['seam_minus_surround'],s-c)
  for x in r['paired_rung_effects']+[v for v in pair if v['model']==m]:
   j,k=names.index(x['first']),names.index(x['second']);f=[0,128].index(int(x['fill_rgb']));dd=flat[j,f]-flat[k,f];eq(x['baseline_logit_difference'],b[j]-b[k]);eq(x['seam_mean_difference_of_delta'],sum(dd[i] for i in seam)/17);eq(x['matched_surround_mean_difference_of_delta'],sum(dd[i] for i in sur)/17)
   if 'all_patch_delta_difference' in x:np.testing.assert_array_equal(dd.reshape(8,8),x['all_patch_delta_difference'])
  summary.append({'model':m,'views':1024,'scale_maxabs_all_rungs':float(abs(delta).max()),'P18_yx':grid[18].tolist(),'seam_cells':17,'control_cells':17})
failed=[]
for m in ['madation_vitb16','madation_vitl14']:
 p=O/(m+'_smoke')/'failure.json';pin(p);r=json.loads(p.read_text());assert r['status']=='FAILED' and not (O/(m+'_full')).exists();failed.append({'model':m,'error':r['error']})
F=O/'numeric_print_v2';pin(F/'FIGURE_MANIFEST.json');pin(F/'SVG_PRINT_SIZE_FONT_QA.json');pin(O/'NUMERICAL_OUTPUT_VERIFICATION.json');manifest=json.loads((F/'FIGURE_MANIFEST.json').read_text());pdf=[]
for x in manifest['files']:
 p=Path(x['path']);assert pin(p)==x['sha256']
 if p.suffix!='.pdf':continue
 info=subprocess.check_output(['pdfinfo',str(p)],text=True);assert '510.236 x 595.276 pts' in info
 xml=ET.fromstring(subprocess.check_output(['pdftohtml','-i','-xml','-stdout','-zoom','1',str(p)]));sizes=[int(v.attrib['size']) for v in xml.findall('.//fontspec')];assert min(sizes)>=8
 pdf.append({'file':p.name,'min_font_pt_poppler':min(sizes),'page_points':[510.236,595.276]})
out={'verdict':'PASS_NUMERICAL_INTERNAL_ONLY','checks':'Independent delta, CSV, scalar sigmoid, geometry-derived cell membership, regional and paired contrast recomputation; all 30 figure manifest file hashes and ten PDF dimensions/font sizes verified.','models':summary,'failures_preserved':failed,'pdf':pdf,'input_sha256':hashes,'scope':'No source images, candidate archives, checkpoint, inference or retries. Numeric-only PDF raster inspection separately recorded in Markdown.'}
p=E/'ASTRA_POSTRESULT_NUMERICAL_CHECK.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'report':str(p),'sha256':pin(p),'models':summary,'failures':failed},indent=2))
