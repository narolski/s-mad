import json, numpy as np
from scipy.stats import t as T
R=json.load(open("rec.json")); J=json.load(open("/home/narolski/smad-next/experiments/AB1_protocol-ablation-and-replication/ab1_read.json"))
S=[408,409,410,411,412]; Z=["fm61","amsl112"]
g=lambda a,s:R[f"{a}_{s}"]
# agreement check
mx=0
for k,v in J["networks"].items():
    a,s=k.split("_s"); r=g(a,int(s))
    for kk,rk in [("lcomb_auc","lc"),("S3","S3"),("S0","S0"),("warp","warp"),("dsoft","dsoft"),("S3_vs_S4_auc","S3vS4"),("S0_vs_S4_auc","S0vS4"),("halves","halves")]:
        mx=max(mx,abs(v[kk]-r[rk]))
    for z in Z:
        for kk,rk in [("d_flag","df"),("d_mean_sd","dm"),("d_flag_upper95","up95"),("d_mean_att_sd","dmatt")]:
            mx=max(mx,abs(v["c2p"][z][kk]-r[z][rk]))
print("max abs diff vs ab1_read.json", mx)
print("status", set(J["status"].values()))
ctrl={z:{s:g("A",s)[z]["df"]>=0.05 and g("A",s)[z]["dm"]>0 for s in S} for z in Z}; print("ctrl",ctrl)
def xp(X,s,z):
    x,A=g(X,s)[z],g("A",s)[z]
    c=[x["df"]<=A["df"]/3, abs(x["dm"])<=A["dm"]/3, x["df"]<=0.05, x["up95"]<=0.08]
    return all(c),c
for X in ["Sb","B","SbS","AS","SbZ","SbH","Sp"]:
    for z in Z:
        print(X,z,[ (s,xp(X,s,z)[0], [int(c) for c in xp(X,s,z)[1]], round(g(X,s)[z]["df"],3), round(g(X,s)[z]["dm"],3), round(g("A",s)[z]["dm"]/3,3)) for s in S])
print("Hnew1 dmatt", {X:{z:[round(g(X,s)[z]["dmatt"],3) for s in S] for z in Z} for X in ["Sb","B"]})
for s in S: print("C1",s, round(g("Sb",s)["lc"]-g("B",s)["lc"],3), round(g("Sb",s)["lc"]-g("A",s)["lc"],3), J["networks"][f"Sb_s{s}"]["lcomb_minus_floor_lo"])
print("rho",{z:[round(g("SbS",s)[z]["df"]/g("A",s)[z]["df"],3) for s in S] for z in Z})
def rr(X,k,base="Sb"):
    v=np.array([g(X,s)[k]-g(base,s)[k] for s in S]); m=v.mean(); h=T.ppf(.975,4)*v.std(ddof=1)/5**.5
    return [round(x,4) for x in v], round(m,4), (round(m-h,4), round(m+h,4))
print("Hab2",rr("SbZ","warp")); print("Hab3",rr("SbH","dsoft")); print("Hab3s",rr("SbS","dsoft"))
print("Hsp1",[round(g("Sp",s)["lc"]-g("Sb",s)["lc"],4) for s in S])
print("Hsp2",[round(g("Sp",s)["amsl112"]["df"]-g("Sb",s)["amsl112"]["df"],4) for s in S])
print("Hsp3",[round(g("Sp",s)["S3"]-g("Sb",s)["S3"],3) for s in S])
print("Hsp3b",[round(g("Sp",s)["S3vS4"]-g("Sb",s)["S3vS4"],4) for s in S])
print("Hab4",[(g("Sp",s)["S0"],g("Sb",s)["S0"],round(g("Sp",s)["S0vS4"]-g("Sb",s)["S0vS4"],4)) for s in S])
print({k:J["verdicts"][k]["verdict"] if isinstance(J["verdicts"][k],dict) and "verdict" in J["verdicts"][k] else None for k in J["verdicts"]})
print(J["verdicts"]["R1_Sb"]["verdict"],J["verdicts"]["R1_B"]["verdict"])
