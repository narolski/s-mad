"""CPU actual eight-image loader and pair gradient smoke; never constructs model."""
import csv
import importlib.util
import json
import os
import pathlib
import sys
import torch
import paired

root=pathlib.Path('/mnt/t7/smad_next/PN1/fs_tree/pn1')
meta=pathlib.Path(__file__).resolve().parents[3]/'experiments/SPRINT5_20261114/paired_ranking/cpu_metadata'
(meta/'manifests').mkdir(parents=True,exist_ok=True)
link=meta/'manifests/train.csv'
if not link.exists(): link.symlink_to(root/'data/manifests/train_Sb.csv')
os.environ['SMAD_DATA']=str(meta)
sys.path.insert(0,str(root/'code'/'smadcvpr'))
import common as C
assert not C.train_items('d0','val10','none')
rows=list(csv.DictReader(open(root/'data'/'manifests'/'train_Sb.csv')))
unit=next(u for u in paired.units(rows) if len(u)==2)
chosen=list(unit)+[i for i in range(6)]
ds=C.ImageItems([(rows[i]['path'],int(rows[i]['label'])) for i in chosen],224,root=root/'data')
for i in range(8):
    x,y=ds[i]
    assert tuple(x.shape)==(3,224,224) and torch.isfinite(x).all()
z=torch.zeros(8,requires_grad=True)
loss=paired.rank_loss(z,torch.tensor(chosen),rows)
loss.backward()
assert z.grad[0]<0 and z.grad[1]>0 and torch.equal(z.grad[2:],torch.zeros(6))
assert abs(loss.item()-torch.nn.functional.softplus(torch.tensor(1.)).item())<1e-6
zero=paired.rank_loss(z,torch.tensor([0]*8),rows)
assert zero.item()==0
pair_counts=[]
for batch in paired.plan(rows,501,2,256,'paired_rank')[0]:
    _,count=paired.rank_loss(torch.zeros(256),torch.tensor(batch),rows,return_count=True)
    assert count>0
    pair_counts.append(count)
print(json.dumps({'actual_images':8,'shape':[3,224,224],'rank_loss':loss.item(),'gradient':z.grad.tolist(),'status':'PASS','val10_rows':0,'smoke_pair_counts':pair_counts,'no_pair_loss':zero.item()}))
