"""LA1-0 variable-resolution aligned-crop calibration. CPU-only existing image pipeline."""
import argparse
import csv
import hashlib
import json
import os
import pathlib
import random
import sys
import time

os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ.setdefault('OMP_NUM_THREADS','2')
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
os.environ.setdefault('MKL_NUM_THREADS','2')

import numpy as np
import torch

REPO=pathlib.Path('/home/narolski/smad-next')
MC=pathlib.Path('/home/narolski/mambamorph-code')
PINS={
 REPO/'src/AR1/fr.py':'eb425605480f8bdfa51acff27fc5c490e3e32151b0d18c589ca5a267050aa238',
 MC/'smadcvpr/prep_eval.py':'374408ab3a886e6df25b563bc2344d190efe2ab7b3163efbb17c9b6ca9100628',
 pathlib.Path('/mnt/t7/smad_heldout/arc2face/scripts/a2f_common.py'):'d27701dbe187dd6fcc2b50f21e3631a1c1a0678cfdc9d5a6989cd9c355bfcc3c',
 MC/'dmad/quads/gpuface.py':'61ad42f78778bdd0e09f7f8b9150d4805adb32a82b265eeda6cb133e76f23f81',
 pathlib.Path('/home/narolski/.insightface/models/antelopev2/glintr100.onnx'):'4ab1d6435d639628a6f3e5008dd4f929edf4c4124b1a7169e1048f9fef534cdf',
 pathlib.Path('/home/narolski/.insightface/models/buffalo_l/det_10g.onnx'):'5838f7fe053675b1c7a08b633df49e7af5495cee0493c7dcf6697200b85b5b91'}


def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def cpu_backend():
    assert not torch.cuda.is_available(),'GPU forbidden in CPU calibration'
    assert all(sha(p)==h for p,h in PINS.items()),'source/model pin mismatch'
    sys.path.insert(0,str(REPO/'src/AR1'))
    import fr as FR
    PE,A2F=FR._mods()
    from dmad.quads.gpuface import gpu_face_app,TorchSession
    from insightface.model_zoo import get_model
    # Same shipped model graphs/preprocessing; only TorchSession device changes.
    PE._APP=gpu_face_app('buffalo_l',['detection'],det_size=(512,512),device='cpu')
    model=get_model(str(A2F.FR_FILES['glint']),providers=['CPUExecutionProvider'])
    model.session=TorchSession(model.session,str(A2F.FR_FILES['glint']),'cpu')
    A2F._FR['glint']=model
    assert model.session.device=='cpu' and all(p.device.type=='cpu' for p in model.session.model.parameters())
    assert all(m.session.device=='cpu' for m in PE._APP.models.values())
    return FR


def flags(E,labels,threshold):
    S=E@E.T;out=[]
    for i,p in enumerate(labels):
        own=np.where(labels==p)[0];own=own[own!=i]
        others=[]
        for q in sorted(set(labels)):
            if q!=p:others.append(float(np.median(S[i,labels==q])))
        own_median=float(np.median(S[i,own])) if len(own) else None
        out.append(own_median is None or own_median<threshold or own_median<=max(others))
    return np.asarray(out,dtype=bool)


def summarize(E,found,rows):
    labels=np.asarray([r['person_id'] for r in rows])
    partition=np.asarray([r['partition'] for r in rows])
    # Keep complete originally selected pairs only; never replace missing identities.
    complete={p for p in labels if found[labels==p].all()}
    ok=np.array([p in complete for p in labels]);E=E[ok];labels=labels[ok];partition=partition[ok]
    cal=partition=='calibration';val=partition=='validation'
    def own_cos(e,l):
        return np.asarray([float(e[np.where(l==p)[0][0]]@e[np.where(l==p)[0][1]]) for p in sorted(set(l))])
    genuine_cal=own_cos(E[cal],labels[cal]);assert len(genuine_cal)>0
    threshold=float(np.quantile(genuine_cal,.01,method='linear'))
    ev,lv=E[val],labels[val];assert len(set(lv))>1
    clean_flags=flags(ev,lv,threshold)
    # A fixed10% image-label permutation; no visual edits or inferred truth.
    rng=np.random.default_rng(2026111406);n=max(1,int(.1*len(lv)))
    chosen=np.sort(rng.choice(len(lv),n,replace=False));noisy=lv.copy()
    allpersons=sorted(set(lv))
    for i in chosen:noisy[i]=rng.choice([p for p in allpersons if p!=lv[i]])
    noisy_flags=flags(ev,noisy,threshold);truth=np.zeros(len(lv),bool);truth[chosen]=True
    S=ev@ev.T;ii,jj=np.triu_indices(len(lv),1);different=lv[ii]!=lv[jj]
    tails={}
    for t in (.60,.70,.77):
        keep=different&(S[ii,jj]>=t)
        pairs={tuple(sorted((lv[i],lv[j]))) for i,j in zip(ii[keep],jj[keep])}
        tails[str(t)]={'raw_image_pairs':int(keep.sum()),'unique_identity_edges':len(pairs)}
    return {'scope':'VARIABLE_RESOLUTION_ALIGNED_CELEBA calibration only, NOT HQ/local-binding/mining/train admission',
       'selected':2000,'found_images':int(found.sum()),'complete_pair_images':int(ok.sum()),
       'calibration_persons':int(len(set(labels[cal]))),'validation_persons':int(len(set(lv))),
       'fixed_own_genuine_cosine_p01':threshold,'clean_validation_flag_rate':float(clean_flags.mean()),
       'injected_labels':n,'injected_noise_detection_rate':float(noisy_flags[truth].mean()),
       'uninjected_false_flag_rate_after_noise':float(noisy_flags[~truth].mean()),'raw_cosine_tails':tails,
       'limitations':['Only2images/identity: noise injection can leave singletons and cannot unambiguously identify every mislabeled image.',
       'No pose/W/sex matching here; raw edges are NOT disjoint eligible triples and cannot trigger LA1go.',
       'CPU backend measured independently; do not pool with prior GPU embeddings without a separate correspondence gate.']}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--selection',type=pathlib.Path,required=True)
    ap.add_argument('--out',type=pathlib.Path,required=True);ap.add_argument('--smoke',action='store_true')
    ap.add_argument('--review-receipt',type=pathlib.Path,required=True);a=ap.parse_args()
    review=json.loads(a.review_receipt.read_text());assert review['decision'] in ('GO_CPU_SMOKE','GO_CPU_CALIBRATION')
    assert review['scope']=='LA1-0 labelled variable-resolution aligned CelebA crops only; no HQ admission'
    assert review['reviewer']!=review['author'] and review['reviewer']
    assert review['script_sha256']==sha(__file__) and review['selection_sha256']==sha(a.selection)
    assert sha(review['independent_review_path'])==review['independent_review_sha256']
    if not a.smoke:
        assert review['decision']=='GO_CPU_CALIBRATION' and review['cpu8_smoke_pass'] is True
        assert sha(review['cpu8_result_path'])==review['cpu8_result_sha256']
        smoke=json.loads(pathlib.Path(review['cpu8_result_path']).read_text())
        assert smoke['scope']=='CPU8INFRASTRUCTURE_SMOKE' and smoke['images']==8 and smoke['actual_device']=='cpu'
    assert not a.out.exists();a.out.mkdir(parents=True)
    rows=list(csv.DictReader(a.selection.open()));assert len(rows)==2000
    cp={r['person_id'] for r in rows if r['partition']=='calibration'};vp={r['person_id'] for r in rows if r['partition']=='validation'}
    assert len(cp)==len(vp)==500 and not(cp&vp)
    rows=rows[:8] if a.smoke else rows
    for r in rows:assert sha(r['path'])==r['sha256']
    # Read existing image headers only; preserve every selected pixel/file unchanged.
    from PIL import Image
    dimensions=[]
    for r in rows:
        with Image.open(r['path']) as image:dimensions.append(tuple(image.size))
    dimension_report={'n':len(dimensions),'width_range':[min(w for w,h in dimensions),max(w for w,h in dimensions)],
      'height_range':[min(h for w,h in dimensions),max(h for w,h in dimensions)],
      'histogram':dict(__import__('collections').Counter(f'{w}x{h}' for w,h in dimensions)),
      'exact128square':sum(w==128 and h==128 for w,h in dimensions),'operation':'read headers only; no resizing/filtering/reselection'}
    (a.out/'actual_image_dimensions.json').write_text(json.dumps(dimension_report,indent=2)+'\n')
    (a.out/'selection.csv').write_bytes(a.selection.read_bytes())
    (a.out/'review_receipt.json').write_bytes(a.review_receipt.read_bytes())
    E=[];F=[];t=time.monotonic()
    try:
        FR=cpu_backend()
        for i in range(0,len(rows),32):
            e,f=FR.embed_paths([r['path'] for r in rows[i:i+32]],chunk=32)
            assert e.shape==(len(f),512) and np.isfinite(e).all()
            assert (np.abs(np.linalg.norm(e[f],axis=1)-1)<1e-4).all()
            E.extend(e);F.extend(f)
            np.savez(a.out/'embeddings_progress.npz',emb=np.asarray(E),found=np.asarray(F),
                     image_id=np.asarray([r['image_id'] for r in rows[:len(E)]]),person=np.asarray([r['person_id'] for r in rows[:len(E)]]))
            print(f'LA1_CPU_EMBEDDED {len(E)}/{len(rows)} seconds={time.monotonic()-t:.1f}',flush=True)
        report={'scope':'CPU8INFRASTRUCTURE_SMOKE','images':8,'found':int(np.sum(F))} if a.smoke else summarize(np.asarray(E),np.asarray(F),rows)
        report.update(actual_image_dimensions=dimension_report,seconds=time.monotonic()-t,actual_device='cpu',script_sha256=sha(__file__),selection_sha256=sha(a.selection),
                      source_model_pins={str(p):h for p,h in PINS.items()})
        (a.out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
        print('LA1_CPU_COMPLETE',len(E),flush=True)
    except BaseException as e:
        (a.out/'FAILED.json').write_text(json.dumps({'error':repr(e),'completed_embeddings':len(E),'seconds':time.monotonic()-t},indent=2)+'\n')
        raise


if __name__=='__main__':main()
