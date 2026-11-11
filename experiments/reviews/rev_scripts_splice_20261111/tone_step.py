import os, random
os.environ["OMP_NUM_THREADS"]="1"
import cv2, numpy as np
cv2.setNumThreads(1)
root="/mnt/t7/smad_next/AR1/img/frgcferet"
def auc(p,n):
    p=np.asarray(p);n=np.asarray(n); return float(((p[:,None]>n[None,:]).mean()+0.5*(p[:,None]==n[None,:]).mean()))
k=np.ones((3,3),np.uint8)
for tool in ["opencv"]:
    files=sorted(os.listdir(f"{root}/{tool}/S4")); random.Random(0).shuffle(files); files=files[:150]
    r={"S4":[], "S0":[]}; r2={"S4":[], "S0":[]}
    for f in files:
        base=cv2.imread(f"{root}/{tool}/R2w4/{f}").astype(np.float32)
        s4=cv2.imread(f"{root}/{tool}/S4/{f}").astype(np.float32)
        d=(np.abs(s4-base).max(2)>0).astype(np.uint8)
        hull=np.zeros(d.shape,np.uint8); cv2.fillConvexPoly(hull,cv2.convexHull(cv2.findNonZero(d)),1)
        rin=(hull-cv2.erode(hull,k,iterations=6)).astype(bool)
        bl=cv2.GaussianBlur  # analysis-only low-pass of a difference map, no image is written
        for a in r:
            x=s4 if a=="S4" else cv2.imread(f"{root}/{tool}/{a}/{f}").astype(np.float32)
            diff=x-base
            r[a].append(float(np.linalg.norm(diff[rin].mean(0))))        # signed tone offset in the inner ring
            lp=bl(diff,(0,0),4); r2[a].append(float(np.abs(lp[rin]).mean()))  # low-frequency step
    for name,v in [("tone_offset",r),("lowfreq_step",r2)]:
        print(tool,name,{a:round(float(np.median(x)),2) for a,x in v.items()},"AUC S4>S0",round(auc(v["S4"],v["S0"]),3))
