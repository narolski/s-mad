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
lp4,lp3=np.log(col("P4","p")+1e-12),np.log(col("P3","p")+1e-12)
M,g=T.fold_models(lp4,lp3,hosts,f); sp,sn=T.score_oof(M,g,lp4),T.score_oof(M,g,lp3)
print("auc",auc(sp,sn), "withinD",strat_auc(sp,sn,dv("S4","D"),dv("S3","D"))[0])
G4,G3=dv("S4","G"),dv("S3","G"); print("G identical per host:",np.allclose(G4,G3))
db=np.array([r["db"] for r in R])
E4=col("P4","p")*np.array([float(r["P4_Etot"]) for r in R])[:,None]; E3=col("P3","p")*np.array([float(r["P3_Etot"]) for r in R])[:,None]
P4,P3=col("P4","p"),col("P3","p")
for k in range(5):
  print(f"B{k+1} median p 2p/1p {np.median(P4[:,k]):.3f}/{np.median(P3[:,k]):.3f} AUC p {auc(P4[:,k],P3[:,k]):.3f} AUC E {auc(E4[:,k],E3[:,k]):.3f}  frgc p {auc(P4[db=='frgc',k],P3[db=='frgc',k]):.3f} feret p {auc(P4[db=='feret',k],P3[db=='feret',k]):.3f} | med frgc 2p/1p {np.median(P4[db=='frgc',k]):.3f}/{np.median(P3[db=='frgc',k]):.3f} feret {np.median(P4[db=='feret',k]):.3f}/{np.median(P3[db=='feret',k]):.3f}")
# coefficients full fit
from sklearn.linear_model import LogisticRegression
X=np.r_[lp4,lp3]; y=np.r_[np.ones(len(R)),np.zeros(len(R))]; mu,sd=X.mean(0),X.std(0)
print("coef",LogisticRegression(max_iter=5000).fit((X-mu)/sd,y).coef_.round(2))
# reciprocal pairs, person overlap
B={h:pool[h]["B_pid"] for h in hosts}; hs=set(hosts)
print("partners that are hosts",sum(B[h] in hs for h in hosts),"reciprocal",sum(B.get(B[h])==h for h in hosts))
# semester / session analysis FRGC
sem=lambda p: p.split("/")[-1].split("_")[0]
same_HS=np.array([sem(pool[h]["H"])==sem(pool[h]["S"]) for h in hosts]); same_HB=np.array([sem(pool[h]["H"])==sem(pool[h]["B"]) for h in hosts])
m=db=="frgc"
print("FRGC same-semester H-S",same_HS[m].mean(),"H-B",same_HB[m].mean())
for a in (True,False):
  for b in (True,False):
    pm=m&(same_HB==a); nm=m&(same_HS==b)
    if pm.sum()>5 and nm.sum()>5: print(f" HB same={a} n={pm.sum()} vs HS same={b} n={nm.sum()}: AUC {auc(sp[pm],sn[nm]):.3f}")
# semester of each
import collections
print(collections.Counter((sem(pool[h]["H"]),sem(pool[h]["S"])) for h in np.array(hosts)[m]).most_common(9))
print(collections.Counter((sem(pool[h]["H"]),sem(pool[h]["B"])) for h in np.array(hosts)[m]).most_common(9))
np.savez("/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/tb1/oof.npz",sp=sp,sn=sn)
