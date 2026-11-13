import sys, csv, numpy as np
sys.path.insert(0,"/home/narolski/smad-next/src/BD1")
from bd1_read import auc, strat_auc
from scipy.stats import spearmanr
R=list(csv.DictReader(open("/mnt/t7/smad_next/TB1/tb1_feats.csv"))); hosts=[r["host"] for r in R]
pool={r["pid"]:r for r in csv.DictReader(open("/mnt/t7/smad_next/AR1/pool.csv"))}
D={r["id"]:r for r in csv.DictReader(open("/mnt/t7/smad_next/BD1/d_values.csv"))}
z=np.load("/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/tb1/oof.npz"); sp,sn=z["sp"],z["sn"]
def tem(p): return np.loadtxt(p[:-4]+".tem",skiprows=1,max_rows=106)
W4=[];W3=[]
for h in hosts:
  P=pool[h]; H=tem(P["H"]); W4.append(np.linalg.norm(H-tem(P["B"]),axis=1).mean()); W3.append(np.linalg.norm(H-tem(P["S"]),axis=1).mean())
W4,W3=np.array(W4),np.array(W3); db=np.array([r["db"] for r in R]); fr=db=="frgc"
print("W median 2p",np.median(W4),"1p",np.median(W3),"AUC W",auc(W4,W3), "frgc",auc(W4[fr],W3[fr]),"feret",auc(W4[~fr],W3[~fr]))
print("profile within W quintiles",strat_auc(sp,sn,W4,W3))
D4=np.array([float(D[r["S4_id"]]["D"]) for r in R]); D3=np.array([float(D[r["S3_id"]]["D"]) for r in R])
print("rho(sn,W3)",spearmanr(sn,W3)[0],"rho(sp,W4)",spearmanr(sp,W4)[0])
# joint D x W: tertiles each
qD=np.quantile(np.r_[D4,D3],[1/3,2/3]); qW=np.quantile(np.r_[W4,W3],[1/3,2/3])
bins=lambda x,q: np.searchsorted(q,x)
num=den=0
for i in range(3):
  for j in range(3):
    pm=(bins(D4,qD)==i)&(bins(W4,qW)==j); nm=(bins(D3,qD)==i)&(bins(W3,qW)==j)
    if pm.sum()>=10 and nm.sum()>=10:
      a=auc(sp[pm],sn[nm]); w=pm.sum()*nm.sum(); num+=a*w; den+=w; print(f" D{i} W{j} n {pm.sum()}/{nm.sum()} auc {a:.3f}")
print("joint DxW weighted",num/den if den else None)
