import sys, csv, numpy as np
RAW=sys.argv[1]; rows=list(csv.DictReader(open("/mnt/t7/smad_next/SM1/flists/test_eval.csv")))+list(csv.DictReader(open("/mnt/t7/smad_next/SM1/flists/test_ar1.csv")))
def conv(i): i=str(i); return i if i.startswith(("ev:","ar1:")) else "ev:"+i
for fit in sys.argv[2:]:
    z={}
    for sub in ("ad4eval","ar1eval"):
        f=np.load(f"{RAW}/{fit}/{sub}/scores_eval.npz"); p=np.clip(f["score_noTTA"].astype(float),1e-7,1-1e-7); z.update(dict(zip(map(conv,f["id"]),np.log(p/(1-p)))))
    s=lambda c,l,h=None: np.array([z[r["id"]] for r in rows if r["cell"]==c and r["label"]==l and (h is None or r["hist"]==h) and r["id"] in z])
    r0=s("ar1:frgcferet:none:R0","0"); tau=np.quantile(r0,.95); m=s("mordiff:mordiff","1","morph"); g=s("mordiff:bona","0","native"); e7=s("mordiff:mordiff","0","e7")
    print(fit,"MorDIFF miss own",round((m<0).mean(),3),"cam",round((m<tau).mean(),3),"| native genuine flagged cam",round((g>=tau).mean(),3),"E7 flagged cam",round((e7>=tau).mean(),3), "| tau-R0median",round(tau-np.median(r0),3))
