"""Training-only anchor/reference preparation for constrained tail continuation."""
import argparse
import collections
import hashlib
import json
import os
import pathlib
import sys

import numpy as np
import torch


def main():
    ap=argparse.ArgumentParser()
    for key in ('code','hf-home','net','metadata','data','out'):ap.add_argument('--'+key,required=True)
    ap.add_argument('--battery-code',required=True);ap.add_argument('--workers',type=int,default=7)
    a=ap.parse_args();out=pathlib.Path(a.out);assert not out.exists();out.mkdir(parents=True)
    sys.path.insert(0,str(pathlib.Path(a.battery_code)/'src'))
    from battery import backbones
    torch.backends.cuda.matmul.allow_tf32=True;torch.backends.cudnn.allow_tf32=True
    torch.backends.cudnn.benchmark=False
    assert torch.cuda.is_available() and 'H100' in torch.cuda.get_device_name()
    model,meta,C,trainable,prov=backbones.load('clip_vitb16_lora',a.net,a.code,'cuda',a.hf_home)
    assert meta['seed']==408 and meta['arch']=='a12_clip_vitb16_madation' and meta['res']==224
    import csv
    p=pathlib.Path(a.metadata);rows=list(csv.DictReader(p.open()))
    assert len(rows)==5535 and len({r['path'] for r in rows})==5535
    assert {r['group'] for r in rows}=={'feret/native','feret/s61','frgc/native','frgc/s61'}
    assert all(r['path'].startswith('train/') for r in rows)
    assert not any(any(s in r['path'].lower() for s in ('valx','fst','a12sp','mad22','mordiff','frll')) for r in rows)
    ds=C.ImageItems([(r['path'],int(r['label'])) for r in rows],224,root=a.data)
    loader=torch.utils.data.DataLoader(ds,batch_size=64,num_workers=a.workers)
    logits=[]
    with torch.no_grad():
        for x,_ in loader:logits.extend(C.forward_logit(model,x.to('cuda'))[0].float().cpu().tolist())
    z=np.asarray(logits,dtype=np.float32);assert len(z)==5535 and np.isfinite(z).all()
    np.savez(out/'TRAIN_ONLY_logits.npz',id=np.array([r['id'] for r in rows]),path=np.array([r['path'] for r in rows]),logit=z)
    groups=sorted({r['group'] for r in rows})
    bygroup={g:collections.defaultdict(list) for g in groups}
    for i,r in enumerate(rows):
        if r['label']=='0' and r['camera_genuine']=='True':bygroup[r['group']][r['contributing_ids']].append(i)
    values=[];weights=[]
    for g,ids in bygroup.items():
        for indices in ids.values():values.append(float(z[indices].mean()));weights.append(1/(len(groups)*len(ids)))
    order=np.argsort(values,kind='stable');cum=np.cumsum(np.asarray(weights)[order])
    anchor=float(np.asarray(values)[order[min(int(np.searchsorted(cum,.95,side='left')),len(order)-1)]])
    negative_loss=np.logaddexp(0,z.astype(float)-anchor)
    positive_loss=np.logaddexp(0,-z.astype(float)+anchor)
    eta={g:float(np.quantile([negative_loss[ii].mean() for ii in ids.values()],.9,method='linear')) for g,ids in bygroup.items()}
    refs={}
    for family in sorted({r['kind'] for r in rows if r['label']=='1'}):
        ids=collections.defaultdict(list)
        for i,r in enumerate(rows):
            if r['label']=='1' and r['kind']==family:ids[r['contributing_ids']].append(i)
        refs[family]=float(np.mean([positive_loss[ii].mean() for ii in ids.values()]))
    ref={'scope':'TRAINING_ONLY warm-start continuation constants; not evaluation calibration or performance',
      'reference_network':'AB1_Sb_s408','reference_meta_sha256':prov['meta_sha256'],'reference_weights_sha256':prov['weights_sha256'],
      'metadata_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
      'anchor':anchor,'anchor_rule':'95th weighted quantile of training camera identity-mean logits; each source/processing group totalweight1/4, eachidentityequalwithin group; firstcumulativeweight>=.95',
      'eta':eta,'eta_rule':'TRAINcamera identity-mean softplus(z-anchor),90%linearquantile','eta_optimizer_lr':.01,
      'positive_reference':refs,'positive_epsilon':.02,'q':.1,'tail_weight':.1,'dual_step':.01,'dual_cap':10,
      'negative_group_identity_counts':{g:len(ids) for g,ids in bygroup.items()},
      'negative_group_image_counts':{g:sum(map(len,ids.values())) for g,ids in bygroup.items()},
      'evaluation_calibration':'SEPARATE; never derive adoption threshold from these constants',
      'score_code_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
    (out/'TRAIN_ONLY_reference.json').write_text(json.dumps(ref,indent=2)+'\n')
    print('TRAINING_ONLY_REFERENCE_COMPLETE images=5535 groups=4 families=4')


if __name__=='__main__':main()
