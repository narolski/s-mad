import sys, csv, numpy as np
RAW=sys.argv[1]; rows=list(csv.DictReader(open("/mnt/t7/smad_next/SM1/flists/test_eval.csv")))
def conv(i): i=str(i); return i if i.startswith("ev:") else "ev:"+i
def eer(g,m):
    t=np.unique(np.concatenate([g,m])); fpr=np.array([(g>=x).mean() for x in t]); fnr=np.array([(m<x).mean() for x in t]); j=np.argmin(abs(fpr-fnr)); return 100*(fpr[j]+fnr[j])/2
for fit in sys.argv[2:]:
    f=np.load(f"{RAW}/{fit}/ad4eval/scores_eval.npz"); p=np.clip(f["score_noTTA"].astype(float),1e-7,1-1e-7); z=dict(zip(map(conv,f["id"]),np.log(p/(1-p))))
    s=lambda c,l,h: np.array([z[r["id"]] for r in rows if r["cell"]==c and r["label"]==l and r["hist"]==h and r["id"] in z])
    out=[]
    for fam in ("facemorpher","opencv"):
        m=s(f"frllm:{fam}","1","morph"); out.append(round(eer(s(f"frllm:{fam}","0","e7"),m),2))
    print(fit,"FRLL FM/OpenCV E7 EER",out)
