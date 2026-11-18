"""Constrained per-processing/source genuine-tail training [SPRINT5-3]."""
import torch
import torch.nn.functional as F


class TailObjective(torch.nn.Module):
    def __init__(self,negative_groups,positive_reference,mode,q=.10,weight=.1,epsilon=.02,dual_step=.01,dual_cap=10.):
        super().__init__()
        assert mode in ('mean','cvar') and 0<q<=1
        self.groups=tuple(sorted(negative_groups))
        self.families=tuple(sorted(positive_reference))
        self.eta=torch.nn.Parameter(torch.zeros(len(self.groups)))
        self.register_buffer('dual',torch.zeros(len(self.families)))
        self.register_buffer('reference',torch.tensor([positive_reference[k] for k in self.families],dtype=torch.float32))
        self.mode,self.q,self.weight=mode,q,weight
        self.epsilon,self.dual_step,self.dual_cap=epsilon,dual_step,dual_cap
        self.register_buffer('last_dual_step',torch.tensor(-1,dtype=torch.long))

    def initialize_eta(self,training_negative_losses):
        """Baseline TRAINING-only identity losses, fixed before intervention fitting."""
        assert set(training_negative_losses)==set(self.groups)
        with torch.no_grad():
            for j,g in enumerate(self.groups):
                values=torch.as_tensor(training_negative_losses[g],device=self.eta.device,dtype=self.eta.dtype)
                assert values.ndim==1 and len(values)>0 and torch.isfinite(values).all()
                self.eta[j].copy_(torch.quantile(values,1-self.q))

    def eta_optimizer(self):
        """Explicit scalar optimizer; never inherit tiny encoder learning rate."""
        return torch.optim.Adam([self.eta],lr=.01)

    def update_dual(self,violation,effective_step):
        """Caller aggregates all microbatches then commits exactly once per step."""
        assert effective_step==int(self.last_dual_step)+1,'duplicate/skipped dual commit'
        value=torch.as_tensor(violation,device=self.dual.device,dtype=self.dual.dtype)
        assert value.shape==self.dual.shape and torch.isfinite(value).all()
        with torch.no_grad():
            self.dual.add_(self.dual_step*value).clamp_(0,self.dual_cap)
            self.last_dual_step.fill_(effective_step)

    @staticmethod
    def identity_means(loss,positions,identities):
        units=sorted({identities[i] for i in positions})
        return torch.stack([loss[[i for i in positions if identities[i]==u]].mean() for u in units])

    def forward(self,logits,labels,identities,groups,families,anchor):
        assert len(logits)==len(labels)==len(identities)==len(groups)==len(families)
        margins=logits-anchor
        negative=F.softplus(margins)
        positive=F.softplus(-margins)
        terms,violations,counts,tail_counts=[],[],{},{}
        for j,g in enumerate(self.groups):
            pos=[i for i in range(len(logits)) if labels[i]==0 and groups[i]==g]
            if not pos:raise ValueError('each effective batch must contain each negative source/processing group')
            values=self.identity_means(negative,pos,identities)
            counts[g]=len(values)
            tail_counts[g]=int((values.detach()>self.eta[j].detach()).sum())
            if self.mode=='mean':terms.append(values.mean())
            else:terms.append(self.eta[j]+torch.relu(values-self.eta[j]).mean()/self.q)
        for j,f in enumerate(self.families):
            pos=[i for i in range(len(logits)) if labels[i]==1 and families[i]==f]
            if not pos:raise ValueError('each effective batch must contain each positive family')
            values=self.identity_means(positive,pos,identities)
            violations.append(values.mean()-self.reference[j]-self.epsilon)
        violation=torch.stack(violations)
        # Forward is pure with respect to dual state, including accumulation passes.
        penalty=self.weight*torch.stack(terms).mean()+(self.dual.detach().clone()*violation).mean()
        return penalty,{'effective_negative_identities':counts,'violation':violation.detach().tolist(),
                       'dual':self.dual.detach().tolist(),'eta':self.eta.detach().tolist(),
                       'tail_occupancy':tail_counts}


def smoke():
    report={}
    for mode in ('mean','cvar'):
        z=torch.tensor([-2.,2.,-1.,1.,-2.,-2.],requires_grad=True)
        obj=TailObjective(['a/native','b/native'],{'attack':.1},mode)
        obj.initialize_eta({'a/native':[.01,.1,.2,.5],'b/native':[.01,.1,.2,.5]})
        assert obj.eta_optimizer().param_groups[0]['lr']==.01
        loss,meta=obj(z,[0,0,0,0,1,1],list('abcdef'),['a/native']*2+['b/native']*2+['-']*2,['-']*4+['attack']*2,0.)
        loss.backward()
        assert torch.isfinite(loss) and torch.isfinite(z.grad).all()
        assert (z.grad[:4]>=0).all() and (z.grad[:4]>0).any()
        if mode=='mean':assert (z.grad[:4]>0).all()
        assert obj.dual[0]==0       # forward does not mutate dual
        obj.update_dual(meta['violation'],0)
        assert obj.dual[0]>0       # poor positive detection activates constraint
        # Next optimization step must push attack logits up via the dual.
        z2=z.detach().clone().requires_grad_(True)
        loss2,_=obj(z2,[0,0,0,0,1,1],list('abcdef'),['a/native']*2+['b/native']*2+['-']*2,['-']*4+['attack']*2,0.)
        loss2.backward();assert (z2.grad[4:]<0).all()
        report[mode]={'finite':True,'activated_detection_dual':obj.dual.tolist(),'negative_gradients':z.grad[:4].tolist(),'positive_gradients_nextstep':z2.grad[4:].tolist(),'counts':meta['effective_negative_identities']}
    return report


if __name__=='__main__':
    import json
    print(json.dumps(smoke(),indent=2))
