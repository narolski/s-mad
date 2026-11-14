"""Fixed256-row source/processing-balanced continuation stream and objective hooks."""
import collections
import csv
import hashlib
import json
import os
import pathlib
import random

import torch
from objective import TailObjective


def make_plan(rows,metadata,seed,steps):
    first={}
    for i,r in enumerate(rows):first.setdefault(r['path'],i)
    assert len(first)==len(metadata)==5535 and set(first)==set(metadata)
    negatives=collections.defaultdict(lambda:collections.defaultdict(list))
    positives=collections.defaultdict(lambda:collections.defaultdict(list))
    controls=[]
    for path,m in metadata.items():
        i=first[path]
        if m['label']=='1':positives[m['kind']][m['contributing_ids']].append(i)
        elif m['camera_genuine']=='True':negatives[m['group']][m['contributing_ids']].append(i)
        else:controls.append(i)
    assert len(negatives)==4 and len(positives)==4
    assert sorted(len(v) for v in negatives.values())==[22,170,220,467]
    rng=random.Random(seed);batches=[]
    for step in range(steps):
        batch=[]
        for group,ids in sorted(negatives.items()):
            units=rng.sample(sorted(ids),min(32,len(ids)))
            batch.extend(rng.choice(ids[u]) for u in units)
        assert len(batch)==118
        for family,ids in sorted(positives.items()):
            assert len(ids)>=32
            batch.extend(rng.choice(ids[u]) for u in rng.sample(sorted(ids),32))
        batch.extend(rng.sample(controls,10));rng.shuffle(batch)
        assert len(batch)==256 and sum(int(rows[i]['label']) for i in batch)==128
        batches.append(batch)
    return batches


class Context:
    def __init__(self,rows,device,out):
        self.rows=rows;self.arm=os.environ['TAIL_ARM']
        assert self.arm in ('bce','mean','cvar')
        source=pathlib.Path(os.environ['SPRINT_SOURCE'])
        self.metadata={r['path']:r for r in csv.DictReader((source/'training_identity_groups.csv').open())}
        self.reference_path=pathlib.Path(os.environ['TAIL_REFERENCE_JSON'])
        self.reference=json.loads(self.reference_path.read_text())
        assert (self.reference['q'],self.reference['tail_weight'],self.reference['positive_epsilon'],
                self.reference['dual_step'],self.reference['dual_cap'])==(.1,.1,.02,.01,10)
        assert self.reference['reference_weights_sha256']==hashlib.sha256(pathlib.Path(os.environ['TAIL_WARMSTART']).read_bytes()).hexdigest()
        assert self.reference['metadata_sha256']==hashlib.sha256((source/'training_identity_groups.csv').read_bytes()).hexdigest()
        self.obj=TailObjective(sorted(self.reference['eta']),self.reference['positive_reference'],
                               'cvar' if self.arm=='cvar' else 'mean').to(device)
        with torch.no_grad():
            self.obj.eta.copy_(torch.tensor([self.reference['eta'][g] for g in self.obj.groups],device=device))
        self.eta_opt=self.obj.eta_optimizer()
        self.pending=None;self.out=pathlib.Path(out)
        self.model=None
        (self.out/'TRAIN_ONLY_reference.json').write_bytes(self.reference_path.read_bytes())

    def fail_closed(self,stage):
        record={'stage':stage,'arm':self.arm,'pending':self.pending,
                'eta':self.obj.eta.detach().cpu().tolist(),'dual':self.obj.dual.detach().cpu().tolist()}
        (self.out/'tail_failure.json').write_text(json.dumps(record,indent=2)+'\n')
        torch.save({'objective':self.obj.state_dict(),'eta_optimizer':self.eta_opt.state_dict()},
                   self.out/'FAILED_tail_objective_state.pt')
        if self.model is not None:torch.save(self.model.state_dict(),self.out/'FAILED_detector_state.pt')
        raise FloatingPointError('TAIL_FAIL_CLOSED '+stage)

    def loader(self,C,res,bs,workers,seed,steps):
        assert bs==256 and steps in (2,100)
        batches=make_plan(self.rows,self.metadata,seed,steps)
        receipt={'seed':seed,'steps':steps,'bs':256,'row_exposures':256*steps,
                 'schedule_sha256':hashlib.sha256(json.dumps(batches,separators=(',',':')).encode()).hexdigest(),
                 'camera_per_step':118,'positive_per_step':128,'protocol_controls_per_step':10,
                 'smallest_camera_group_ids':22,'common_warmstart':'AB1_Sb_s408; conditional continuation'}
        (self.out/'sprint_schedule.json').write_text(json.dumps(receipt,indent=2)+'\n')
        ds=C.ImageItems([(r['path'],int(r['label'])) for r in self.rows],res,aug='flip',with_index=True)
        return torch.utils.data.DataLoader(ds,batch_sampler=batches,num_workers=workers,pin_memory=True,
                   persistent_workers=workers>0,generator=torch.Generator().manual_seed(seed+2))

    def penalty(self,logit,idx):
        if not torch.isfinite(logit).all():self.fail_closed('nonfinite_logits')
        if self.arm=='bce':return logit.sum()*0
        self.eta_opt.zero_grad(set_to_none=True)
        m=[self.metadata[self.rows[i]['path']] for i in idx.tolist()]
        labels=[1 if r['label']=='1' else (0 if r['camera_genuine']=='True' else -1) for r in m]
        value,stats=self.obj(logit,labels,[r['contributing_ids'] for r in m],
                     [r['group'] for r in m],[r['kind'] for r in m],self.reference['anchor'])
        self.pending=stats
        if not torch.isfinite(value).all():self.fail_closed('nonfinite_auxiliary_loss')
        return value

    def after_step(self,step):
        if self.arm=='bce':return
        assert self.pending is not None
        if self.obj.eta.grad is not None and not torch.isfinite(self.obj.eta.grad).all():
            self.fail_closed('nonfinite_eta_gradient')
        if self.arm=='cvar':self.eta_opt.step()
        if not torch.isfinite(self.obj.eta).all() or not torch.isfinite(self.obj.dual).all():
            self.fail_closed('nonfinite_eta_or_dual_after_eta_step')
        self.obj.update_dual(self.pending['violation'],step)
        if not torch.isfinite(self.obj.dual).all():self.fail_closed('nonfinite_dual_after_commit')
        stats=dict(self.pending,step=step,dual_after=self.obj.dual.detach().tolist(),eta_after=self.obj.eta.detach().tolist())
        with (self.out/'tail_trace.jsonl').open('a') as f:f.write(json.dumps(stats)+'\n')
        torch.save({'objective':self.obj.state_dict(),'eta_optimizer':self.eta_opt.state_dict(),
                    'effective_step':step},self.out/'tail_objective_state.pt')
        if step<2 or step%25==0:print('TAIL_TRACE',json.dumps(stats),flush=True)
        self.pending=None


def smoke_plan(metadata_path,train_path):
    meta={r['path']:r for r in csv.DictReader(open(metadata_path))}
    rows=list(csv.DictReader(open(train_path)));report=[]
    for seed in (521,522,523,524,525):
        plan=make_plan(rows,meta,seed,100)
        assert len(plan)==100 and all(len(b)==256 for b in plan)
        h=hashlib.sha256(json.dumps(plan,separators=(',',':')).encode()).hexdigest()
        report.append({'seed':seed,'steps':100,'image_exposures_per_arm':25600,'shared_schedule_sha256':h})
    return report
