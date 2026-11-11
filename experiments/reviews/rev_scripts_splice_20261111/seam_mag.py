import os, sys, random
os.environ["OMP_NUM_THREADS"]="1"
import cv2, numpy as np
cv2.setNumThreads(1)
root="/mnt/t7/smad_next/AR1/img/frgcferet"
def auc(p,n):
    p=np.asarray(p);n=np.asarray(n)
    return float(((p[:,None]>n[None,:]).mean()+0.5*(p[:,None]==n[None,:]).mean()))
k=np.ones((3,3),np.uint8)
for tool in ["opencv","facemorpher"]:
    files=sorted(os.listdir(f"{root}/{tool}/S4")); random.Random(0).shuffle(files); files=files[:150]
    res={a:{"step":[],"grad":[]} for a in ["S4","S0","S3"]}
    for f in files:
        base=cv2.imread(f"{root}/{tool}/R2w4/{f}").astype(np.float32)
        s4=cv2.imread(f"{root}/{tool}/S4/{f}").astype(np.float32)
        d=(np.abs(s4-base).max(2)>0).astype(np.uint8)
        pts=cv2.findNonZero(d)
        if pts is None: continue
        hull=np.zeros(d.shape,np.uint8); cv2.fillConvexPoly(hull,cv2.convexHull(pts),1)
        rin=hull-cv2.erode(hull,k,iterations=3); rout=cv2.dilate(hull,k,iterations=3)-hull
        ring=(rin|rout).astype(bool)
        gb=np.hypot(cv2.Sobel(base.mean(2),cv2.CV_32F,1,0),cv2.Sobel(base.mean(2),cv2.CV_32F,0,1))
        for a in ["S4","S0","S3"]:
            x=s4 if a=="S4" else cv2.imread(f"{root}/{tool}/{a}/{f}").astype(np.float32)
            res[a]["step"].append(float(np.abs(x-base)[rin.astype(bool)].mean()))
            g=np.hypot(cv2.Sobel(x.mean(2),cv2.CV_32F,1,0),cv2.Sobel(x.mean(2),cv2.CV_32F,0,1))
            res[a]["grad"].append(float((g-gb)[ring].mean()))
    for m in ["step","grad"]:
        print(tool,m,{a:round(float(np.median(v[m])),2) for a,v in res.items()},
              "AUC S4>S0",round(auc(res["S4"][m],res["S0"][m]),3),"S4>S3",round(auc(res["S4"][m],res["S3"][m]),3),"n",len(res["S4"][m]))
