import csv, numpy as np
from scipy.stats import rankdata, spearmanr
A14="/mnt/t7/smad_next/PN1/results_a14/unpacked/PN1_A14/"
RR="/mnt/t7/smad_next/PN1/results_rented/unpacked/"
M="/mnt/t7/smad_next/PN1/a14_tree/pn14/data/manifests/pn1_a14.csv"
F="/mnt/t7/smad_next/PN1/cues/a14_lcomb.npz"
man=list(csv.DictReader(open(M)))
def ld(p):
    z=np.load(p); return dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))
def auc(p,n):
    r=rankdata(np.r_[p,n])[:len(p)]; return (r.sum()-len(p)*(len(p)+1)/2)/(len(p)*len(n))
lc={r['id']:r for r in man if r['fam']=='ffhq_lcomb'}
mo=sorted(i for i,r in lc.items() if r['rung']=='landmark_combined_orig'); gb=sorted(i for i,r in lc.items() if r['rung']=='landmark_combined_resmatch')
ids=mo+gb; y=np.r_[np.ones(len(mo)),np.zeros(len(gb))]
z=np.load(F); names=[str(n) for n in z['names']]; cid={str(i):c for i,c in zip(z['ids'],z['cues'])}
X=np.array([cid[i] for i in ids],float)
for n in ['noise_std_face','noise_std_border','noise_face_over_border','lapvar_face','lapvar_border','lap_face_over_border','noise_std','png_bytes','b4_.25-.375']:
    j=names.index(n); a=auc(X[y==1,j],X[y==0,j]); print(n, round(max(a,1-a),3), "morph lower" if a<.5 else "morph higher")
for k in [("B",401),("Sb",401),("B",402),("Sb",402)]:
    S=ld(A14+f"PN1_{k[0]}_s{k[1]}__ffhq_lcomb.npz"); L=np.array([S[i] for i in ids])
    print(k, {n: (round(spearmanr(L[y==1],X[y==1,names.index(n)]).correlation,2), round(spearmanr(L[y==0],X[y==0,names.index(n)]).correlation,2)) for n in ['noise_std_border','noise_face_over_border','lapvar_face','png_bytes']})
# contrast-2-type paired storage share, printed for Sb, Bv (and A,B from HN2 files for reference)
h=[r for r in man if r['fam']=='ffhq']
bo={r['host']:r['id'] for r in h if r['rung']=='ffhq_bona_orig'}; br={r['host']:r['id'] for r in h if r['rung']=='landmark_complete_resmatch'}
keys=sorted(set(bo)&set(br)); print("persons",len(keys))
for s in (401,402):
  for a in ("A","B","Sb","Bv"):
    H = ld(RR+f"PN1_HN2_s{s}/scores_hn2_{a}.npz") if a in ("A","B") else ld(A14+f"PN1_{a}_s{s}__ffhq.npz")
    d=np.array([H[br[q]]-H[bo[q]] for q in keys]); print("storage share",a,s,round(np.mean(d>0),3))
