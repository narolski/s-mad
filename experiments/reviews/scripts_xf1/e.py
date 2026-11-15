import csv, numpy as np, cv2
m=list(csv.DictReader(open("/mnt/t7/smad_next/DATA/D12a/manifest.csv")))
def hf(X):
    X=X.astype(np.float64).mean(2); return np.abs(np.diff(X,axis=1)).mean()
def auc(p,n):
    p=np.asarray(p);n=np.asarray(n); return ((p[:,None]>n[None,:]).mean()+0.5*(p[:,None]==n[None,:]).mean())
ex=[];hH=[];hR=[];hM=[];inhull=[];fs=[[],[],[]]
import os
for r in m:
    H=cv2.imread(r["frame_host"]); B=cv2.imread(r["frame_partner"]); R=cv2.imread(r["d1d_render_host"]); M=cv2.imread(r["out"])
    bh=H.max(2)==0; bb=B.max(2)==0
    ex.append((bh^bb).mean())
    hH.append(hf(H));hR.append(hf(R));hM.append(hf(M))
    for i,p in enumerate((r["frame_host"],r["d1d_render_host"],r["out"])): fs[i].append(os.path.getsize(p))
ex=np.array(ex); print("frac px black in exactly one of H,B", np.percentile(ex,[10,50,90]).round(4), "share>0.01", (ex>0.01).mean().round(3))
print("HF mean |dx|: H",np.median(hH).round(3),"R",np.median(hR).round(3),"M",np.median(hM).round(3))
print("AUC low-HF => morph  M vs R", round(auc(-np.array(hM),-np.array(hR)),4), " R vs H", round(auc(-np.array(hR),-np.array(hH)),4))
print("filesize medians",[int(np.median(f)) for f in fs], "AUC smaller file => morph M vs R", round(auc(-np.array(fs[2]),-np.array(fs[1])),4), "R vs H", round(auc(-np.array(fs[1]),-np.array(fs[0])),4))
