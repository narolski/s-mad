import sys, csv, numpy as np
sys.path.insert(0,"/home/narolski/smad-next/src/BD1"); sys.path.insert(0,"/home/narolski/smad-next/src/TB1"); sys.path.insert(0,"/home/narolski/smad-next/src/RI1")
from bd1_read import auc, strat_auc
import tb1_read as T
R=list(csv.DictReader(open("/mnt/t7/smad_next/TB1/tb1_feats.csv")))
hosts=[r["host"] for r in R]; f=T.folds_of(hosts)
D={r["id"]:r for r in csv.DictReader(open("/mnt/t7/smad_next/BD1/d_values.csv"))}
for r in csv.DictReader(open("/mnt/t7/smad_next/BD1/d_feats.csv")): D[r["id"]].update(r)
pool={r["pid"]:r for r in csv.DictReader(open("/mnt/t7/smad_next/AR1/pool.csv"))}
col=lambda pre,n: np.array([[float(r[f"{pre}_{n}{k}"]) for k in range(1,6)] for r in R])
dv=lambda img,key: np.array([float(D[r[f"{img}_id"]][key]) for r in R])
z=np.load("/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/tb1/oof.npz"); sp,sn=z["sp"],z["sn"]
db=np.array([r["db"] for r in R]); fr=db=="frgc"
Et4=np.array([float(r["P4_Etot"]) for r in R]); Et3=np.array([float(r["P3_Etot"]) for r in R])
P4,P3=col("P4","p"),col("P3","p"); E4,E3=P4*Et4[:,None],P3*Et3[:,None]
print("Etot AUC",auc(Et4,Et3),"Etot within D",strat_auc(Et4,Et3,dv("S4","D"),dv("S3","D"))[0])
print("profile within Etot quintiles",strat_auc(sp,sn,Et4,Et3))
for key in ("D_Y","D_int","D_band","D_ac"):
  print("profile within",key,strat_auc(sp,sn,dv("S4",key)+1e-9,dv("S3",key)+1e-9)[0], "pure",strat_auc(dv("S4",key)+1e-9,dv("S3",key)+1e-9,dv("S4",key)+1e-9,dv("S3",key)+1e-9)[0])
for k in range(5):
  print(f"B{k+1}: E within D {strat_auc(E4[:,k],E3[:,k],dv('S4','D'),dv('S3','D'))[0]:.3f}; frgc E auc {auc(E4[fr,k],E3[fr,k]):.3f} feret E auc {auc(E4[~fr,k],E3[~fr,k]):.3f}")
# per-db within D
for m,name in ((fr,"frgc"),(~fr,"feret")):
  print(name,"within D",strat_auc(sp[m],sn[m],dv("S4","D")[m],dv("S3","D")[m])[:2], "D alone",auc(dv("S4","D")[m],dv("S3","D")[m]))
# simple 1-feature: log(E5/Etot) etc
print("B5-share alone within D", strat_auc(-P4[:,4],-P3[:,4],dv("S4","D"),dv("S3","D"))[0])
print("B4+B5 share alone within D", strat_auc(-(P4[:,3]+P4[:,4]),-(P3[:,3]+P3[:,4]),dv("S4","D"),dv("S3","D"))[0])
print("B1 share alone within D", strat_auc(P4[:,0],P3[:,0],dv("S4","D"),dv("S3","D"))[0])
# cos_HS within S3, cos_HB: does profile score track FR similarity within class?
from scipy.stats import spearmanr
cHS=np.array([float(pool[h]["cos_HS"]) for h in hosts]); cHB=np.array([float(pool[h]["cos_HB"]) for h in hosts])
print("rho(sn,cos_HS)",spearmanr(sn,cHS)[0],"frgc",spearmanr(sn[fr],cHS[fr])[0],"rho(sp,cos_HB)",spearmanr(sp,cHB)[0])
# session gap days
import datetime
def dt(s):
  s=s.strip()
  try: return datetime.date.fromisoformat(s)
  except: return datetime.datetime.strptime(s,"%y%m%d").date()
gap=np.array([abs((dt(pool[h]["H_session"])-dt(pool[h]["S_session"])).days) for h in hosts])
print("median days H-S frgc",np.median(gap[fr]),"feret",np.median(gap[~fr]))
print("rho(sn,gap) frgc",spearmanr(sn[fr],gap[fr])[0],"feret",spearmanr(sn[~fr],gap[~fr])[0])
# B session vs H session gap
gapB=np.array([abs((dt(pool[h]["H_session"])-dt(pool[pool[h]["B_pid"]]["H_session"])).days) if pool[h]["B"]==pool[pool[h]["B_pid"]]["H"] else -1 for h in hosts])
print("B image is partner's H image:",(gapB>=0).mean())
# same-day pairs (same session) two-person
ok=gapB>=0
print("2p same-day n",(gapB[ok]==0).sum())
same=ok&(gapB==0)
if same.sum()>=5: print("2p same-day vs all 1p AUC",auc(sp[same],sn), "frgc", auc(sp[same&fr],sn[fr]) if (same&fr).sum()>4 else None)
# H-B gap matched to H-S gap bins in frgc
for lo,hi in ((0,30),(30,120),(120,400),(400,5000)):
  pm=fr&ok&(gapB>=lo)&(gapB<hi); nm=fr&(gap>=lo)&(gap<hi)
  if pm.sum()>4 and nm.sum()>4: print(f"frgc gap [{lo},{hi}) n2p={pm.sum()} n1p={nm.sum()} AUC {auc(sp[pm],sn[nm]):.3f}")
for lo,hi in ((0,200),(200,500),(500,5000)):
  pm=~fr&ok&(gapB>=lo)&(gapB<hi); nm=~fr&(gap>=lo)&(gap<hi)
  print(f"feret gap [{lo},{hi}) n2p={pm.sum()} n1p={nm.sum()}", auc(sp[pm],sn[nm]) if pm.sum()>2 and nm.sum()>2 else None)
