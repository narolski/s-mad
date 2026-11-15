import csv, hashlib, sys, numpy as np
from scipy.stats import rankdata, spearmanr
A14="/mnt/t7/smad_next/PN1/results_a14/unpacked/PN1_A14/"
RR="/mnt/t7/smad_next/PN1/results_rented/unpacked/"
M="/mnt/t7/smad_next/PN1/a14_tree/pn14/data/manifests/pn1_a14.csv"
F="/mnt/t7/smad_next/PN1/cues/a14_lcomb.npz"
print("floor sha", hashlib.sha256(open(F,'rb').read()).hexdigest())
man=list(csv.DictReader(open(M)))
def ld(p):
    z=np.load(p); return dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))
def auc(p,n):
    r=rankdata(np.r_[p,n])[:len(p)]; return (r.sum()-len(p)*(len(p)+1)/2)/(len(p)*len(n))
lc={r['id']:r for r in man if r['fam']=='ffhq_lcomb'}
mo=sorted(i for i,r in lc.items() if r['rung']=='landmark_combined_orig')
gb=sorted(i for i,r in lc.items() if r['rung']=='landmark_combined_resmatch')
nets=[(a,s) for s in (401,402) for a in ("A","B","Bn","C","Sb","Bv")]
S={k:ld(A14+f"PN1_{k[0]}_s{k[1]}__ffhq_lcomb.npz") for k in nets}
res={}
for k in nets:
    m=np.array([S[k][i] for i in mo]); b=np.array([S[k][i] for i in gb])
    res[k]=auc(m,b)
    print(k, round(res[k],4), "miss", np.mean(m<=0), "flag", np.mean(b>0))
for s in (401,402):
    print(s,"Sb-B",round(res[('Sb',s)]-res[('B',s)],4),"Sb-A",round(res[('Sb',s)]-res[('A',s)],4))
z=np.load(F); names=[str(n) for n in z['names']]; cid={str(i):c for i,c in zip(z['ids'],z['cues'])}
CM=np.array([cid[i] for i in mo]); CG=np.array([cid[i] for i in gb])
fa=[(auc(CM[:,j],CG[:,j]),names[j]) for j in range(len(names))]
for a,n in sorted(fa,key=lambda t:-max(t[0],1-t[0]))[:8]: print("cue",n,round(a,4))
# gate
for arm,s in (("A",401),("B",402)):
    new=ld(A14+f"PN1_{arm}_s{s}__ffhq.npz"); old=ld(RR+f"PN1_HN2_s{s}/scores_hn2_{arm}.npz")
    ks=sorted(new); d=np.array([new[i]-old[i] for i in ks])
    print("gate",arm,s,len(ks),set(new)==set(old),np.abs(d).max(),
      hashlib.sha256(open(A14+f"PN1_{arm}_s{s}__ffhq.npz",'rb').read()).hexdigest()[:16],
      hashlib.sha256(open(RR+f"PN1_HN2_s{s}/scores_hn2_{arm}.npz",'rb').read()).hexdigest()[:16])
    print(open(RR+f"PN1_HN2_s{s}/gpu.txt").read().strip())
# paired complete - combined
h={r['id']:r for r in man if r['fam']=='ffhq'}
comp={r['host']:i for i,r in h.items() if r['rung']=='landmark_complete_orig'}
comb={r['host']:i for i,r in lc.items() if r['rung']=='landmark_combined_orig'}
keys=sorted(set(comp)&set(comb)); print("pairs",len(keys))
for k in nets:
    a,s=k
    full = ld(RR+f"PN1_HN2_s{s}/scores_hn2_{a}.npz") if a in ("A","B","Bn","C") else ld(A14+f"PN1_{a}_s{s}__ffhq.npz")
    d=np.array([full[comp[q]]-S[k][comb[q]] for q in keys])
    print("paired",k,round(d.mean(),3),round(np.median(d),3),round(np.mean(d>0),3))
np.save("/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/a14rev/ok.npy",np.array([1]))
