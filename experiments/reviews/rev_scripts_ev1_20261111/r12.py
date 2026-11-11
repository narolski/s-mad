import sys, csv, re, numpy as np, pathlib, collections, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib import *
R = rows_eval(); ids = [r["id"] for r in R]; dev = sel(R, "devbona","devbona","orig","0")
sL = rel("madation_vitl14", ids); sB = rel("madation_vitb16", ids)
def common(f):
    by = {}
    for v in ("orig","jpeg90","jpeg70","jpeg50","blur1","resample50"):
        by[v] = {re.sub(r"_%s\.png$" % v, "", R[i]["name"]): i for i in sel(R,"frllm",f,v,"1")}
    c = sorted(set.intersection(*[set(by[v]) for v in by if v != "orig"])); assert set(c) <= set(by["orig"]), f
    return np.array([by["orig"][k] for k in c])
g50 = sel(R,"frllm","frll_bona","jpeg50","0"); n50 = np.array([R[i]["name"][4:6]=="03" for i in g50])
for f in ("amsl","stylegan"):
    m = common(f); print(f, len(m), "ViT-L/14 AUC morph orig vs genuine JPEG50: neutral-only %.3f all %.3f" % (auc(sL[m], sL[g50][n50]), auc(sL[m], sL[g50])))
gd = sel(R,"dim","greedy_dim","orig","1"); e7 = sel(R,"dim","greedy_dim","resmatch","0"); ne = np.array([R[i]["name"][4:6]=="03" for i in e7])
print("ViT-B/16 Greedy-DiM vs its E7: neutral %.3f all %.3f" % (auc(sB[gd], sB[e7][ne]), auc(sB[gd], sB[e7])))
da = sel(R,"dim","dim_a","orig","1"); e7a = sel(R,"dim","dim_a","resmatch","0"); nea = np.array([R[i]["name"][4:6]=="03" for i in e7a])
print("ViT-B/16 DiM-A vs its E7: neutral %.3f all %.3f" % (auc(sB[da], sB[e7a][nea]), auc(sB[da], sB[e7a])))
# A5 StyleGAN3
H3 = list(csv.DictReader(open("/mnt/t7/smad_heldout/h3_sg3/data/manifests/h3sg3.csv"))); hid = [r["id"] for r in H3]
hm = [i for i, r in enumerate(H3) if r["family"]=="h3_sg3" and r["variant"]=="orig"]; hb = [i for i, r in enumerate(H3) if r["family"]=="h3_bona" and r["variant"]=="orig"]
for nm, d, s in (("ViT-L/14","madation_vitl14", sL), ("ViT-B/16","madation_vitb16", sB)):
    t = thr(s[dev], .05); sh = rel(d, hid, "h3sg3")
    print(f"{nm}: StyleGAN3 one-identity render FA at dev thr {100*(sh[hb]>t).mean():.1f}% (n={len(hb)}); two-identity morph miss {100*(sh[hm]<=t).mean():.1f}% (n={len(hm)}); at 0.5 rule render flagged {100*(sh[hb]>0).mean():.1f}% morph detected {100*(sh[hm]>0).mean():.1f}%; AUC morph vs render {auc(sh[hm], sh[hb]):.3f}")
