"""OCC1: actual constant-occlusion responses, no export of source face pixels."""
import argparse,csv,hashlib,importlib.util,json,os
from pathlib import Path
import sys,time
from datetime import datetime,timezone

import numpy as np


def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()


def write(p,x):
 with p.open('x') as f:
  json.dump(x,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())


def prep(array,res):
 """Exact ImageItems.load/__getitem__ pixel operations, in-memory input only."""
 import torch
 from PIL import Image
 im=Image.fromarray(array).convert('RGB')
 if im.size!=(res,res):im=im.resize((res,res),Image.BILINEAR)
 return torch.from_numpy(np.asarray(im,np.float32)/255.).permute(2,0,1)


def mask_grid():
 return [(y,x) for y in range(0,512,64) for x in range(0,512,64)]


def occlude(a,box,fill):
 y,x=box;b=a.copy();b[y:y+64,x:x+64]=fill;return b


def selftest():
 a=np.arange(512*512*3,dtype=np.uint32).reshape(512,512,3).astype(np.uint8)
 orig=a.copy();b=occlude(a,(64,128),128)
 changed=np.zeros((512,512),bool);changed[64:128,128:192]=True
 assert np.array_equal(a,orig) and np.array_equal(b[~changed],a[~changed])
 assert (b[changed]==128).all() and changed.sum()==4096
 noop=a.copy();noop[changed]=a[changed];assert np.array_equal(noop,a)
 # Linear score makes replacement effect sign and magnitude exactly testable.
 z=lambda v:float(v.astype(float).sum())
 expected=float((128.-a[changed].astype(float)).sum())
 assert z(b)-z(a)==expected
 assert len(mask_grid())==64 and len(set(mask_grid()))==64
 cover=np.zeros((512,512),int)
 for y,x in mask_grid():cover[y:y+64,x:x+64]+=1
 assert (cover==1).all()
 print('PASS synthetic fixed-area/support, no source mutation, identity sham, signed linear delta and full tiling')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true')
 ap.add_argument('--inventory',type=Path);ap.add_argument('--model');ap.add_argument('--out',type=Path)
 ap.add_argument('--smoke',action='store_true');a=ap.parse_args()
 if a.self_test:selftest();return
 if not sys.flags.isolated:raise RuntimeError('python -I required')
 if not(a.inventory and a.model and a.out):ap.error('inventory/model/out required')
 inv=json.loads(a.inventory.read_text());cfg=inv['models'][a.model]
 if inv['runner_sha256']!=sha(__file__):raise ValueError('unpinned runner')
 for p in inv['sources']+inv['inputs']+cfg['checkpoints']:
  if sha(p['path'])!=p['sha256']:raise ValueError('pin mismatch: '+p['path'])
 if inv['source_pixel_export_allowed'] is not False:raise ValueError('This runner is numeric-only; no face export')
 if __import__('shutil').disk_usage('/mnt/t7').free<50*1024**3:raise RuntimeError('50GiB floor')
 a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 rec=dict(model=a.model,smoke=a.smoke,status='STARTED',started_utc=datetime.now(timezone.utc).isoformat(),
          inventory_sha256=sha(a.inventory),runner_sha256=sha(__file__),source_pixels_exported=False,
          source_pixel_export_allowed=False,scope='Internal development descriptive constant-occlusion only')
 write(a.out/'started.json',rec)
 try:
  import cv2,torch
  from PIL import Image
  torch.set_num_threads(2);torch.manual_seed(20261114);np.random.seed(20261114)
  torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
  os.environ['HF_HOME']=inv['hf_home'];os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
  dev='cuda' if torch.cuda.is_available() else 'cpu';sys.path.insert(0,cfg['code'])
  import common as C
  if cfg['kind']=='own':
   meta=json.loads(Path(cfg['meta']).read_text())
   if meta['seed']!=403 or meta['final']!='last':raise ValueError('fixed model identity')
   model,_=C.build_run_model(meta);state=torch.load(cfg['checkpoint'],map_location='cpu',weights_only=True)
   if set(state)!={n for n,p in model.named_parameters() if p.requires_grad}:raise ValueError('trainable key mismatch')
   inc=model.load_state_dict(state,strict=False)
   if inc.unexpected_keys or set(inc.missing_keys)!=set(model.state_dict())-set(state):raise ValueError('frozen base mismatch')
   fwd=lambda x:C.forward_logit(model,x)[0].float().reshape(-1);res=meta['res']
  else:
   import a12_released as R
   R.torch,R.np,R.C=torch,np,C;spec=R.RELEASES[a.model];model=R.build_release(spec)
   model.load_state_dict(R.extract_state(R.load_release(Path(cfg['checkpoint'])),spec),strict=True)
   fwd=lambda x:R.head_logit(model(R.adapt_input(x,spec)),spec['classes'],spec['morph_index']);res=spec['res']
  model.to(dev).eval()
  for p in model.parameters():p.requires_grad_(False)
  names=[r['condition'] for r in inv['inputs']]
  imgs={r['condition']:np.asarray(Image.open(r['path']).convert('RGB')) for r in inv['inputs']}
  if any(v.shape!=(512,512,3) for v in imgs.values()):raise ValueError('input RGB shape')
  # Reuse exact original hull helper, not an approximate facial region.
  sys.path.insert(0,inv['ar1_source'])
  s=importlib.util.spec_from_file_location('occ1_splice',Path(inv['ar1_source'])/'splice.py')
  sp=importlib.util.module_from_spec(s);s.loader.exec_module(sp)
  h=sp.hull(inv['H_tem'],inv['B_tem'],imgs['S4'].shape)
  for arm,outside,inside in (('S4','R2w4','R4'),('S3','R2w','R3'),('S0','R2w4','R2w')):
   if not(np.array_equal(imgs[arm][~h],imgs[outside][~h]) and np.array_equal(imgs[arm][h],imgs[inside][h])):
    raise ValueError('shared-hull7b compositing invalid: '+arm)
  ring=cv2.dilate(h.astype('uint8'),np.ones((17,17),'uint8')).astype(bool)&~cv2.erode(h.astype('uint8'),np.ones((17,17),'uint8')).astype(bool)
  surround=~cv2.dilate(h.astype('uint8'),np.ones((33,33),'uint8')).astype(bool)
  interior=cv2.erode(h.astype('uint8'),np.ones((33,33),'uint8')).astype(bool)
  boxes=mask_grid();seams=[];backs=[];cores=[];category=[];areas=[]
  for i,(y,x) in enumerate(boxes):
   cut=(slice(y,y+64),slice(x,x+64));sf=float(ring[cut].mean())
   seam=sf>=.10;bg=bool(surround[cut].all());face=bool(interior[cut].all())
   if seam:seams.append(i)
   if bg:backs.append(i)
   if face:cores.append(i)
   category.append(dict(index=i,y=y,x=x,native_area=4096,seam_fraction=sf,seam=seam,surround=bg,interior=face))
   m=np.zeros((512,512,3),'uint8');m[cut]=255
   q=prep(m,res).numpy()[0]
   areas.append(dict(index=i,soft_area_after_standard_preprocess=float(q.sum()),support_after_standard_preprocess=int((q>0).sum())))
  if not seams or len(backs)<len(seams):raise ValueError('insufficient matched-area spatial controls')
  controls=backs[:len(seams)]
  ds=C.ImageItems([(r['path'],0) for r in inv['inputs']],res,root='/')
  for i,n in enumerate(names):
   if not torch.equal(prep(imgs[n],res),ds[i][0]):raise ValueError('memory/native preprocessing mismatch: '+n)
  # Each image baseline/repeat/no-op independently before the occlusion sweep.
  base=[];checks=[]
  with torch.no_grad():
   for n in names:
    xx=prep(imgs[n],res).unsqueeze(0).to(dev);v=fwd(xx).item();again=fwd(xx).item()
    batch_reference=fwd(xx.repeat(8,1,1,1)).cpu().numpy().astype(float)
    if not np.isfinite(batch_reference).all() or np.max(np.abs(batch_reference-v))>1e-4:
     raise ValueError('batch1/batch8 baseline parity gate')
    sham=imgs[n].copy();sham[h]=imgs[n][h]
    if not np.array_equal(sham,imgs[n]):raise ValueError('identity sham pixels')
    nv=fwd(prep(sham,res).unsqueeze(0).to(dev)).item()
    if max(abs(v-again),abs(v-nv))>1e-5:raise ValueError('repeat/noop score gate')
    if not np.isfinite([v,again,nv]).all():raise ValueError('nonfinite baseline')
    base.append(v);checks.append(dict(condition=n,logit=v,repeated_logit=again,noop_logit=nv,
                                    batch8_reference_logits=batch_reference.tolist(),batch_parity_max_abs=float(np.max(np.abs(batch_reference-v)))))
  # Smoke uses first8 fixed (fill,cell) views per rung; full uses every view.
  tasks=[(f,i) for f in (0,128) for i in range(64)]
  if a.smoke:tasks=tasks[:8]
  logits=np.full((len(names),2,64),np.nan,dtype=np.float64)
  rows=[]
  with torch.no_grad():
   for j,n in enumerate(names):
    for offset in range(0,len(tasks),8):
     chunk=tasks[offset:offset+8]
     xx=torch.stack([prep(occlude(imgs[n],boxes[i],fill),res) for fill,i in chunk]).to(dev)
     vals=fwd(xx).cpu().numpy().astype(float)
     if not np.isfinite(vals).all():raise ValueError('nonfinite occluded output')
     for (fill,i),v in zip(chunk,vals):
      fi=0 if fill==0 else 1;logits[j,fi,i]=v;delta=float(v-base[j])
      rows.append(dict(condition=n,fill_rgb=fill,patch_index=i,y=boxes[i][0],x=boxes[i][1],
                       original_logit=base[j],occluded_logit=float(v),delta_logit=delta,
                       original_uncalibrated_score=float(torch.sigmoid(torch.tensor(base[j],dtype=torch.float64))),
                       occluded_uncalibrated_score=float(torch.sigmoid(torch.tensor(v,dtype=torch.float64)))))
    print(a.model,n,'actual occlusions',len(tasks),flush=True)
  delta=logits-np.array(base)[:,None,None]
  if not a.smoke and not np.isfinite(delta).all():raise ValueError('incomplete full grid')
  np.savez(a.out/'raw_responses.npz',conditions=np.array(names),fills=np.array([0,128]),
           baseline_logits=np.array(base),occluded_logits=logits.reshape(len(names),2,8,8),
           delta_logits=delta.reshape(len(names),2,8,8),grid_yx=np.array(boxes),
           hull=h,seam_ring=ring,surround=surround,interior=interior,
           seam_cell_indices=np.array(seams),matched_surround_indices=np.array(controls))
  with (a.out/'per_patch_scores.csv').open('x',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
  regional=[];paired=[]
  if not a.smoke:
   for j,n in enumerate(names):
    for fi,fill in enumerate((0,128)):
     sr=float(delta[j,fi,seams].mean());bg=float(delta[j,fi,controls].mean())
     regional.append(dict(condition=n,fill_rgb=fill,seam_mean_delta=sr,matched_surround_mean_delta=bg,
                          seam_minus_surround=sr-bg,interior_mean_delta=float(delta[j,fi,cores].mean()) if cores else None,
                          seam_cells=len(seams),matched_surround_cells=len(controls),interior_cells=len(cores)))
   for first,second in (('S4','S0'),('S4','S3'),('S0','R2w4'),('S3','R2w'),('S4','R2w4')):
    k,l=names.index(first),names.index(second);contrast=delta[k]-delta[l]
    for fi,fill in enumerate((0,128)):
     paired.append(dict(first=first,second=second,fill_rgb=fill,baseline_logit_difference=base[k]-base[l],
                        seam_mean_difference_of_delta=float(contrast[fi,seams].mean()),
                        matched_surround_mean_difference_of_delta=float(contrast[fi,controls].mean()),
                        all_patch_delta_difference=contrast[fi].reshape(8,8).tolist()))
  rec.update(status='SMOKE_PASS' if a.smoke else 'COMPLETE',seconds=time.monotonic()-start,
             completed_utc=datetime.now(timezone.utc).isoformat(),baselines=checks,categories=category,
             post_preprocess_areas=areas,seam_cells=seams,matched_surround_cells=controls,interior_cells=cores,
             regional_effects=regional,paired_rung_effects=paired,
             finite_views=len(rows),uncomputed_smoke_entries_are_nan=a.smoke,
             no_source_pixels_in_npz=True,raw_npz_sha256=sha(a.out/'raw_responses.npz'),
             score_csv_sha256=sha(a.out/'per_patch_scores.csv'),
             device=torch.cuda.get_device_name(0) if dev=='cuda' else dev,
             versions=dict(torch=torch.__version__,numpy=np.__version__,python=sys.version),
             precision='float32 TF32off noTTA aligned-frame adapters; uncalibrated head scores',
             interpretation='Constant-fill conditional response; not isolated causal seam/identity mechanism')
  write(a.out/'result.json',rec)
 except Exception as e:
  rec.update(status='FAILED',error=repr(e),seconds=time.monotonic()-start);write(a.out/'failure.json',rec);raise


if __name__=='__main__':main()
