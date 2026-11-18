import collections,csv,hashlib,json,pathlib
import numpy as np
from PIL import Image
R=pathlib.Path('/home/narolski/smad-next');D=pathlib.Path('/mnt/t7/smad_next/SPRINT5_5/lowres_cpu2000_v2');O=R/'experiments/SPRINT5_20261114/la1'
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
assert (D/'result.json').exists(),'Full result not yet finalized'
r=json.loads((D/'result.json').read_text());release=json.loads((O/'CPU2000_RELEASE_ROOT_V2.json').read_text())
assert sha(R/'src/SPRINT5/la1_calibration/run_cpu.py')==release['script_sha256']==r['script_sha256']=='66f6621bfaa8e63fa3a021716ac6713d69bf64e9ff131bfa9eb41939ec126f2e'
assert sha(D/'selection.csv')==release['selection_sha256']==r['selection_sha256']=='2ba96c20a3b214be6cacfd951937077e98160d1b57c857a5c7948e5dc6054e52'
assert sha(D/'review_receipt.json')==sha(O/'CPU2000_RELEASE_ROOT_V2.json')
assert sha(release['independent_review_path'])==release['independent_review_sha256']
assert sha(release['cpu8_result_path'])==release['cpu8_result_sha256']
rows=list(csv.DictReader((D/'selection.csv').open()));labels=np.array([x['person_id'] for x in rows]);parts=np.array([x['partition'] for x in rows]);ids=[x['image_id'] for x in rows]
assert len(rows)==len(set(ids))==2000;assert set(parts)=={'calibration','validation'}
cp=set(labels[parts=='calibration']);vp=set(labels[parts=='validation']);assert len(cp)==len(vp)==500 and not cp&vp
assert set(collections.Counter(labels).values())=={2}
z=np.load(D/'embeddings_progress.npz',allow_pickle=False);E=z['emb'];f=z['found'];assert E.shape==(2000,512) and f.shape==(2000,) and f.dtype==bool and np.isfinite(E).all();assert np.array_equal(z['image_id'],ids) and np.array_equal(z['person'],labels)
norms=np.linalg.norm(E[f],axis=1);assert np.max(np.abs(norms-1))<1e-4
sizes=[]
for x in rows:
 assert sha(x['path'])==x['sha256']
 with Image.open(x['path']) as im:sizes.append(im.size)
dim=json.loads((D/'actual_image_dimensions.json').read_text());assert dim==r['actual_image_dimensions'];assert dict(collections.Counter(f'{w}x{h}' for w,h in sizes))==dim['histogram'];assert dim['width_range']==[66,147] and dim['height_range']==[79,169] and dim['exact128square']==sum(w==h==128 for w,h in sizes)==19
complete={p for p in set(labels) if np.all(f[labels==p])};keep=np.array([p in complete for p in labels]);e,l,part=E[keep],labels[keep],parts[keep];cal=part=='calibration';val=part=='validation'
cs=[]
for p in sorted(set(l[cal])):
 pair=e[cal][l[cal]==p];assert len(pair)==2;cs.append(float(pair[0]@pair[1]))
sorted_cos=np.sort(cs);pos=.01*(len(cs)-1);lo=int(np.floor(pos));threshold=float(sorted_cos[lo]+(pos-lo)*(sorted_cos[min(lo+1,len(cs)-1)]-sorted_cos[lo]))
v=e[val];vl=l[val];S=v@v.T
# Independent vectorized per-identity medians, excluding each query only in its own identity.
def classify(lab):
 groups=sorted(set(lab));med=np.stack([np.median(S[:,lab==p],axis=1) for p in groups],axis=1);lookup={p:i for i,p in enumerate(groups)};own=np.full(len(lab),np.nan)
 for i,p in enumerate(lab):
  others=np.flatnonzero(lab==p);others=others[others!=i]
  if len(others):own[i]=np.median(S[i,others])
  med[i,lookup[p]]=-np.inf
 return np.isnan(own)|(own<threshold)|(own<=med.max(axis=1))
clean=classify(vl);rng=np.random.default_rng(2026111406);n=max(1,int(.1*len(vl)));chosen=np.sort(rng.choice(len(vl),n,replace=False));noisy=vl.copy();people=sorted(set(vl))
for i in chosen:noisy[i]=rng.choice([p for p in people if p!=vl[i]])
assert np.all(noisy[chosen]!=vl[chosen]);flags=classify(noisy);truth=np.zeros(len(vl),bool);truth[chosen]=True
pairs={}
for t in [.6,.7,.77]:
 mask=np.triu(S>=t,1)&(vl[:,None]!=vl[None,:]);ii,jj=np.nonzero(mask);edges={(min(vl[i],vl[j]),max(vl[i],vl[j])) for i,j in zip(ii,jj)};pairs[str(t)]={'raw_image_pairs':len(ii),'unique_identity_edges':len(edges)}
computed={'found_images':int(f.sum()),'complete_pair_images':int(keep.sum()),'calibration_persons':len(set(l[cal])),'validation_persons':len(set(vl)),'fixed_own_genuine_cosine_p01':threshold,'clean_validation_flag_rate':float(clean.mean()),'injected_labels':n,'injected_noise_detection_rate':float(flags[truth].mean()),'uninjected_false_flag_rate_after_noise':float(flags[~truth].mean()),'raw_cosine_tails':pairs}
for k,vv in computed.items():
 if isinstance(vv,float):assert abs(vv-r[k])<1e-7,(k,vv,r[k])
 else:assert vv==r[k],(k,vv,r[k])
assert r['actual_device']=='cpu' and not (D/'FAILED.json').exists()
out={'decision':'PASS_VARIABLE_RESOLUTION_SOURCE_CALIBRATION_DIAGNOSTIC_ONLY','reviewer':'astra_sprint_plan_review','author':'sol_sprint_experiments','result_sha256':sha(D/'result.json'),'embeddings_sha256':sha(D/'embeddings_progress.npz'),'selection_sha256':sha(D/'selection.csv'),'audit_script_sha256':sha(__file__),'embedding_shape':list(E.shape),'norm_range':[float(norms.min()),float(norms.max())],'selected_person_partitions':[500,500],'person_overlap':0,'dimensions':{k:dim[k] for k in ['n','width_range','height_range','exact128square']},'recomputed':computed,'clean_flag_count':int(clean.sum()),'injected_detected_count':int(flags[truth].sum()),'uninjected_flag_count':int(flags[~truth].sum()),'noise_created_singleton_images':sum(collections.Counter(noisy)[p]==1 for p in noisy),'seconds_reported':r['seconds'],'limits':['HQ mapping remains BLOCKED. No LA1 training admission.','Wrong-label reassignment is not a count-preserving permutation; singleton ambiguity remains.','Raw cross-identity edges lack pose/W/sex/disjoint-triplet eligibility.','No candidate detector outputs opened; no model rerun or new images.','CPU8 and failed v1 history left unchanged.']}
(O/'ASTRA_LOWRES_CPU2000_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));print('REVIEW_SHA256',sha(O/'ASTRA_LOWRES_CPU2000_REVIEW.json'))
