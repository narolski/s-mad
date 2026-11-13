import csv, numpy as np, cv2, sys
def tem(p):
    L=open(p).read().splitlines(); n=int(L[0]); return np.array([list(map(float,L[i].split())) for i in range(1,n+1)],np.float32)
S="/mnt/t7/smad_next/MS1/ffhq/src/"
rows=list(csv.DictReader(open("/mnt/t7/smad_next/DATA/D12b/manifest.csv")))
face={}
for r in csv.DictReader(open("/mnt/t7/smad_next/XF1/xf1b_rows.csv")):
    if r["form"]=="face": face[(r["klass"],r["host"])]=r["src"]
ringfrac=[];okW=okF=0;n=0;sF=[];sW=[];sFi=[];sWi=[];sFr=[];sWr=[]; agree=0
def g(img,m):
    d=np.abs(np.diff(img.astype(np.float32),axis=1)).mean(2); mm=m[:,1:]&m[:,:-1]; return d[mm].mean()
for r in rows:
    h,b=r["host"].split(":")[1],r["partner"].split(":")[1]
    H=cv2.imread(S+h+".png");B=cv2.imread(S+b+".png");F=cv2.imread(r["d12a_morph"]);W=cv2.imread(r["out"])
    ph,pb=tem(S+h+".tem"),tem(S+b+".tem")
    pts=np.rint((ph+pb)/2).astype(int)
    me=np.zeros(H.shape[:2],np.uint8);cv2.fillConvexPoly(me,cv2.convexHull(pts),255);me=cv2.erode(me,np.ones((10,10),np.uint8))>0
    hull=np.zeros(H.shape[:2],np.uint8);cv2.fillConvexPoly(hull,cv2.convexHull(np.rint(0.5*ph+0.5*pb).astype(np.int32)),1);hull=hull>0
    agree+= (np.rint(0.5*ph+0.5*pb).astype(int)==pts).all()
    ring=hull&~me
    ringfrac.append(ring.sum()/hull.sum())
    okW+=(W[ring]==H[ring]).all(); okF+=(F[ring]==cv2.addWeighted(H,0.5,B,0.5,0)[ring]).all(); n+=1
    # face-only copies equal whole inside hull?
    Ff=cv2.imread(face[("FMHB",r["host"])]);Wf=cv2.imread(face[("WARP",r["host"])])
    assert (Ff[hull]==F[hull]).all() and (Wf[hull]==W[hull]).all()
    sF.append(g(F,hull));sW.append(g(W,hull));sFi.append(g(F,me));sWi.append(g(W,me))
    sFr.append(g(F,ring));sWr.append(g(W,ring))
def auc(pos,neg):
    pos,neg=np.array(pos),np.array(neg); return ((pos[:,None]>neg[None]).mean()+0.5*(pos[:,None]==neg[None]).mean())
rf=np.array(ringfrac)
print("pairs",n,"pts agree",agree,"ring==H in W",okW,"ring==avg(H,B) in FM",okF)
print("ring share of hull: median %.3f min %.3f max %.3f"%(np.median(rf),rf.min(),rf.max()))
print("AUC (lower grad = morph) hull %.3f  eroded-mask only %.3f  ring only %.3f"%(auc(-np.array(sF),-np.array(sW)),auc(-np.array(sFi),-np.array(sWi)),auc(-np.array(sFr),-np.array(sWr))))
