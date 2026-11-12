import csv, numpy as np
from scipy.stats import rankdata
A14="/mnt/t7/smad_next/PN1/results_a14/unpacked/PN1_A14/"
RR="/mnt/t7/smad_next/PN1/results_rented/unpacked/"
M="/mnt/t7/smad_next/PN1/a14_tree/pn14/data/manifests/pn1_a14.csv"
man=list(csv.DictReader(open(M)))
def ld(p):
    z=np.load(p); return dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))
def auc(p,n):
    r=rankdata(np.r_[p,n])[:len(p)]; return (r.sum()-len(p)*(len(p)+1)/2)/(len(p)*len(n))
rows=lambda fam,rung:[r for r in man if r['fam']==fam and r['rung']==rung]
co=rows('ffhq','landmark_complete_orig'); cg=rows('ffhq','landmark_complete_resmatch'); bo=rows('ffhq','ffhq_bona_orig')
mo=rows('ffhq_lcomb','landmark_combined_orig'); gb=rows('ffhq_lcomb','landmark_combined_resmatch')
cmap={r['host']:r['id'] for r in co}; mmap={r['host']:r['id'] for r in mo}; keys=sorted(set(cmap)&set(mmap))
for s in (401,402):
  for a in ("A","B","Bn","C","Sb","Bv"):
    H = ld(RR+f"PN1_HN2_s{s}/scores_hn2_{a}.npz") if a in ("A","B","Bn","C") else ld(A14+f"PN1_{a}_s{s}__ffhq.npz")
    L = ld(A14+f"PN1_{a}_s{s}__ffhq_lcomb.npz")
    G=np.array([L[r['id']] for r in gb]); Gc=np.array([H[r['id']] for r in cg])
    C=np.array([H[cmap[k]] for k in keys]); X=np.array([L[mmap[k]] for k in keys])
    # percentile within genuine (combined resmatch) pool
    pc=lambda v: np.searchsorted(np.sort(G),v)/len(G)
    print(a,s,"AUC complete vs hm-gen %.3f"%auc(C,Gc),"combined vs hm-gen %.3f"%auc(X,G),
      "| genuine-percentile median complete %.3f combined %.3f"%(np.median(pc(C)),np.median(pc(X))),
      "| frac combined above genuine median %.3f"%np.mean(X>np.median(G)),
      "| sat: share complete>3.8 %.2f, gen SD %.2f, range %.2f..%.2f"%(np.mean(C>3.8),G.std(),min(C.min(),G.min()),max(C.max(),X.max())))
