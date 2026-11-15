import sys, csv, numpy as np
RAW=sys.argv[1]; rows=list(csv.DictReader(open("/mnt/t7/smad_next/SM1/flists/test_eval.csv")))
def conv(i): i=str(i); return i if i.startswith("ev:") else "ev:"+i
def eer(g,m):
    t=np.unique(np.concatenate([g,m])); fpr=np.array([(g>=x).mean() for x in t]); fnr=np.array([(m<x).mean() for x in t]); j=np.argmin(abs(fpr-fnr)); return 100*(fpr[j]+fnr[j])/2
for fit in sys.argv[2:]:
    f=np.load(f"{RAW}/{fit}/ad4eval/scores_eval.npz"); p=np.clip(f["score_noTTA"].astype(float),1e-7,1-1e-7); z=dict(zip(map(conv,f["id"]),np.log(p/(1-p))))
    s=lambda c,l,h: np.array([z[r["id"]] for r in rows if r["cell"]==c and r["label"]==l and r["hist"]==h and r["id"] in z])
    m=s("mordiff:mordiff","1","morph"); n=eer(s("mordiff:bona","0","native"),m); e=eer(s("mordiff:mordiff","0","e7"),m)
    print(fit,"MorDIFF native",round(n,2),"E7",round(e,2),"rise",round(e-n,2), "n morph",len(m))
