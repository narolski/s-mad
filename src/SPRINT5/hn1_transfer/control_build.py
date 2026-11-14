"""Self-target H/S control for matched-target HN transfer pilot; no detector fit."""
import argparse,csv,hashlib,importlib.util,json,pathlib,shutil,time
import numpy as np
import cv2
ap=argparse.ArgumentParser();ap.add_argument('--count',type=int,choices=[8,124],required=True);ap.add_argument('--release',type=pathlib.Path,required=True);ap.add_argument('--out',type=pathlib.Path,required=True);a=ap.parse_args()
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r=json.loads(a.release.read_text());assert r['decision']=='GO_HN_CONTROL_BUILD' and r['count']==a.count and r['reviewer']!=r['author'];assert r['script_sha256']==sha(__file__)
for p,h in r['pins'].items():assert sha(p)==h,p
if a.count==124:
 sm=json.loads(pathlib.Path(r['smoke_receipt_path']).read_text());assert sha(r['smoke_receipt_path'])==r['smoke_receipt_sha256'];assert sm['status']=='PASS' and sm['count']==8 and sm['script_sha256']==sha(__file__)
assert not a.out.exists();assert shutil.disk_usage('/mnt/t7').free>=50*(1<<30);a.out.mkdir(parents=True)
src=pathlib.Path('/home/narolski/smad-next/src/SPRINT5/hn1/build_pilot.py');spec=importlib.util.spec_from_file_location('original_hn',src);B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)
ks=importlib.util.spec_from_file_location('original_triangle',B.KERNEL);K=importlib.util.module_from_spec(ks);ks.loader.exec_module(K)
pool={x['pid']:x for x in csv.DictReader(B.POOL.open())};split={x['pid']:x for x in csv.DictReader(B.SPLIT.open())};original=pathlib.Path('/mnt/t7/smad_next/SPRINT5_2/train124_native_floor_v1/pilot.json');records=json.loads(original.read_text());assert len(records)==124
assert [x['host'] for x in records]==sorted(x['host'] for x in records);chosen=records[:a.count];out=[];t0=time.monotonic()
for old in chosen:
 rec={'host':old['host'],'partner':old['partner'],'source':old['source']};t=time.monotonic()
 try:
  assert old['status']=='BUILT';p=pool[old['host']];assert split[old['host']]['role']==split[p['B_pid']]['role']=='train'
  for path,h in old['input_pins'].items():assert sha(path)==h,path
  for key in ['P','N']:assert sha(old['outputs'][key]['path'])==old['outputs'][key]['sha256']
  H=cv2.imread(p['H']);S=cv2.imread(p['S']);assert H is not None and S is not None and H.shape==S.shape==(512,512,3)
  lh,ls=B.tem(p['H']),B.tem(p['S']);target,tri,corners=B.geometry(lh,ls,512,512)
  wh=B.warp(H,lh,target,tri,corners,K);ws=B.warp(S,ls,target,tri,corners,K)
  negative=np.clip(.5*wh.astype(np.float32)+.5*ws.astype(np.float32),0,255).astype(np.uint8)
  folder=a.out/old['host'].replace(':','_');folder.mkdir();outputs={}
  for name,img in [('Nself',negative),('WHself',wh),('WSself',ws)]:
   path=folder/(name+'.png');assert cv2.imwrite(str(path),img);assert np.array_equal(cv2.imread(str(path)),img)
   outputs[name]={'path':str(path),'sha256':sha(path),'pixel_sha256':hashlib.sha256(img.tobytes()).hexdigest()}
  rec.update(status='PASS',input_pins=old['input_pins'],common_positive=old['outputs']['P'],matched_negative=old['outputs']['N'],outputs=outputs,target_sha256=hashlib.sha256(target.tobytes()).hexdigest(),triangles_sha256=hashlib.sha256(json.dumps(tri).encode()).hexdigest(),warps_per_layer=1,blend_weight=.5,target='mean(H_landmarks,S_landmarks)',processing='native PNG; no stored-small transformation',target_differs_from_matched=hashlib.sha256(target.tobytes()).hexdigest()!=old['target_sha256'])
 except Exception as e:rec.update(status='FAIL',error=repr(e))
 rec['seconds']=time.monotonic()-t;out.append(rec);(a.out/'records.json').write_text(json.dumps(out,indent=2)+'\n')
 if rec['status']!='PASS':break
status='PASS' if len(out)==a.count and all(x['status']=='PASS' for x in out) else 'FAIL'
report={'status':status,'count':a.count,'completed':len(out),'script_sha256':sha(__file__),'original_pilot_sha256':sha(original),'release_sha256':sha(a.release),'seconds':time.monotonic()-t0,'records_sha256':sha(a.out/'records.json'),'scope':'TRAINnativecontrolconstruction only, no detector/candidate read'}
(a.out/'RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(status!='PASS')
