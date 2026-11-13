import numpy as np
rng=np.random.default_rng(2); N=200000
def paired(delta,sig,tau): return delta+tau*rng.standard_normal((N,1))+np.sqrt(2)*sig*rng.standard_normal((N,5))
# ladder candidate rule: mean>=-0.02 and min>=-0.06
for tau,sig in [(0,0.015),(0.01,0.02),(0.02,0.025)]:
    for d in [0,-0.03]:
        D=paired(d,sig,tau); p=(D.mean(1)>=-0.02)&(D.min(1)>=-0.06)
        print(f"ladder tau={tau} sig={sig} true={d}: pass mean>=-0.02&min>=-0.06 {p.mean():.2f}")
# lcomb candidate: mean>=0.025 & >0 on 4/5
for tau,sig in [(0,0.012),(0.007,0.016)]:
    for g in [0,0.015,0.03,0.045]:
        D=paired(g,sig,tau); p=(D.mean(1)>=0.025)&((D>0).sum(1)>=4)
        print(f"lcomb tau={tau} sig={sig} g={g}: mean>=.025&>0 4/5 {p.mean():.3f}")
# DINOv3 unpaired route (i): median(ch)>=0.922 (fixed) & U<=4 ; comparator mu=0.892 sd 0.012
from itertools import product
for g in [0,0.03,0.045]:
    for sd in [0.012,0.02]:
        c=0.892+sd*rng.standard_normal((N,5)); x=0.892+g+sd*rng.standard_normal((N,5))
        U=(x[:,:,None]<c[:,None,:]).sum((1,2))  # count comparator > challenger
        p=(np.median(x,1)>=0.922)&(U<=4)
        print(f"DINO (i) g={g} sd={sd}: pass {p.mean():.2f}")
# DINOv3 ladder median rule vs paired vote, equal arm
for sig in [0.015,0.02,0.025]:
    c=sig*rng.standard_normal((N,5)); x=sig*rng.standard_normal((N,5))
    print(f"DINO (ii) sig={sig} equal arm fail {(np.median(x,1)<np.median(c,1)-0.01).mean():.2f}")
