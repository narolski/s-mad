"""Actual FS1 loader check on all ten 32-image allocation manifests, CPU only."""
import collections
import json
import os
import pathlib
import sys

import torch

repo=pathlib.Path('/home/narolski/smad-next')
base=pathlib.Path('/mnt/t7/smad_next/PN1/fs_tree/pn1')
meta=pathlib.Path('/mnt/t7/smad_next/SPRINT5_4/cpu_loader_check/data')
(meta/'manifests').mkdir(parents=True,exist_ok=True)
link=meta/'train'
if not link.exists():link.symlink_to(base/'data/train')
os.environ['SMAD_DATA']=str(meta)
sys.path.insert(0,str(base/'code/smadcvpr'))
import common as C

report=[]
for seed in (511,512,513,514,515):
    for arm in ('narrow_more_variants','broad_fewer_variants'):
        src=repo/f'src/SPRINT5/breadth_fit/train_{arm}_s{seed}.csv'
        (meta/'manifests/train.csv').write_bytes(src.read_bytes())
        rows=C.run_rows('d0','train90','none',(),False,None)
        assert len(rows)==32 and not C.train_items('d0','val10','none')
        C.seed_all(seed) if hasattr(C,'seed_all') else torch.manual_seed(seed)
        loader=C.train_loader(rows,224,32,0,seed,'v1','prior',aug='flip')
        assert len(loader)==1
        counts=collections.Counter()
        for epoch in range(2):
            for x,y,idx in loader:
                assert tuple(x.shape)==(32,3,224,224) and torch.isfinite(x).all() and int(y.sum())==16
                counts.update(idx.tolist())
        assert counts=={i:2 for i in range(32)}
        report.append({'seed':seed,'arm':arm,'rows':32,'epochs':2,'actual_images_loaded':64,'all_row_indices_twice':True,'val10':0})
(repo/'experiments/SPRINT5_20261114/breadth/CPU_REAL_LOADER_SMOKE.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'actual_manifest_cases':len(report),'actual_images_loaded':640,'status':'PASS'}))
