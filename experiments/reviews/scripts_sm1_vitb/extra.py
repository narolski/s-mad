import sys, json, csv, numpy as np, torch
S=sys.argv[1]
for f in ("a_s401","e_s401"):
    sd=torch.load(f"{S}/pt/SM1B_{f}/ad4eval/last_trainable.pt",map_location="cpu",weights_only=True)
    if isinstance(sd,dict) and "state_dict" in sd: sd=sd["state_dict"]
    hk=[k for k in sd if ("head" in k or "fc" in k or "classifier" in k)]
    print(f,[ (k,tuple(sd[k].shape)) for k in hk][:6])
    for k in hk:
        t=sd[k].float()
        if t.ndim==2: print(" rows norms",k,[round(float(x),3) for x in t.norm(dim=1)], "diff-row norm",round(float((t[-1]-t[0]).norm()),3) if t.shape[0]==2 else "")
        if t.ndim==1: print(" bias",k,[round(float(x),3) for x in t])
sys.path.insert(0,S+"/scripts")
