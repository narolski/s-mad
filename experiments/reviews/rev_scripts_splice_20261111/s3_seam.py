import os, random
os.environ["OMP_NUM_THREADS"]="1"
import cv2, numpy as np
cv2.setNumThreads(1)
root="/mnt/t7/smad_next/AR1/img/frgcferet"
def auc(p,n):
    p=np.asarray(p);n=np.asarray(n); return float(((p[:,None]>n[None,:]).mean()+0.5*(p[:,None]==n[None,:]).mean()))
k=np.ones((3,3),np.uint8)
for tool in ["opencv","facemorpher"]:
    files=sorted(os.listdir(f"{root}/{tool}/S4")); random.Random(0).shuffle(files); files=files[:150]
    R={a:{"absstep":[],"tone":[],"outside_eq":[]} for a in ["S4","S0","S3"]}
    for f in files:
        b4=cv2.imread(f"{root}/{tool}/R2w4/{f}").astype(np.float32); bw=cv2.imread(f"{root}/{tool}/R2w/{f}").astype(np.float32)
        s4=cv2.imread(f"{root}/{tool}/S4/{f}").astype(np.float32)
        d=(np.abs(s4-b4).max(2)>0).astype(np.uint8)
        hull=np.zeros(d.shape,np.uint8); cv2.fillConvexPoly(hull,cv2.convexHull(cv2.findNonZero(d)),1)
        rin=(hull-cv2.erode(hull,k,iterations=3)).astype(bool); outm=~cv2.dilate(hull,k,iterations=2).astype(bool)
        for a in R:
            x=s4 if a=="S4" else cv2.imread(f"{root}/{tool}/{a}/{f}").astype(np.float32)
            e4=float((np.abs(x-b4).max(2)==0)[outm].mean()); ew=float((np.abs(x-bw).max(2)==0)[outm].mean())
            base=b4 if e4>=ew else bw
            R[a]["outside_eq"].append("R2w4" if e4>=ew else "R2w")
            diff=x-base
            R[a]["absstep"].append(float(np.abs(diff[rin]).mean())); R[a]["tone"].append(float(np.linalg.norm(diff[rin].mean(0))))
    for m in ["absstep","tone"]:
        print(tool,m,{a:round(float(np.median(v[m])),2) for a,v in R.items()},"S4>S0",round(auc(R["S4"][m],R["S0"][m]),3),"S4>S3",round(auc(R["S4"][m],R["S3"][m]),3))
    print(tool,"outside base",{a:max(set(v["outside_eq"]),key=v["outside_eq"].count) for a,v in R.items()})
