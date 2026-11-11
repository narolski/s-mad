import csv, pathlib, numpy as np, hashlib, re
from scipy.stats import mannwhitneyu, spearmanr
MC = pathlib.Path("/home/narolski/mambamorph-code"); S = MC/"smadcvpr_runs/A12_scored"
H3 = "/mnt/t7/smad_heldout/h3_sg3/data/manifests/h3sg3.csv"; EVAL = MC/"smadcvpr_data/manifests/eval.csv"
hr = list(csv.DictReader(open(H3)))
ev = [r for r in csv.DictReader(open(EVAL)) if r["family"]=="frll_bona" and r["variant"]=="orig"]
R4 = [r for r in hr if r["family"]=="h3_sg3" and r["variant"]=="orig"]; R2 = [r for r in hr if r["family"]=="h3_bona" and r["variant"]=="orig"]
thr = 0.23939879320561908
mc = np.array([min(float(r["cos_glint_a"]), float(r["cos_glint_b"])) for r in R4]); pot = mc >= thr
print("n R4", len(R4), "R2", len(R2), "R0", len(ev), "potent", int(pot.sum()), f"{pot.mean():.4f}")
print("native sizes R4/R2:", set((r["native_w"],r["native_h"]) for r in R4), set((r["native_w"],r["native_h"]) for r in R2), " R0:", set((r["native_w"],r["native_h"]) for r in ev))
def auc(p,n): return mannwhitneyu(p,n).statistic/(len(p)*len(n))
rng = np.random.default_rng(7)
pairs = sorted({int(r["pair"]) for r in hr}); ppos = {p:i for i,p in enumerate(pairs)}
i4 = np.array([ppos[int(r["pair"])] for r in R4]); i2 = np.array([ppos[int(r["pair"])] for r in R2])
def wauc(pos, neg, wp, wn):
    ob = np.argsort(neg, kind="stable"); ns = neg[ob]; cw = np.r_[0,np.cumsum(wn[ob])]
    lo = np.searchsorted(ns,pos,"left"); hi = np.searchsorted(ns,pos,"right")
    return float((wp*(cw[lo]+0.5*(cw[hi]-cw[lo]))).sum()/(wp.sum()*cw[-1]))
for lab, fh, fe, key in (("SelfMAD own", MC/"smadcvpr_runs/A36/selfmad_own/own_h3sg3.npz", MC/"experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz", "score"),
                         ("ViT-B/16 rel", S/"A12REL/madation_vitb16/scores_h3sg3.npz", S/"A12REL/madation_vitb16/scores_eval.npz", "score_noTTA"),
                         ("ViT-L/14 rel", S/"A12REL/madation_vitl14/scores_h3sg3.npz", S/"A12REL/madation_vitl14/scores_eval.npz", "score_noTTA")):
    z = np.load(fh, allow_pickle=False); m = dict(zip(z["id"].tolist(), z[key].astype(float)))
    ze = np.load(fe, allow_pickle=False); me = dict(zip(ze["id"].tolist(), ze[key].astype(float)))
    s4 = np.array([m[r["id"]] for r in R4]); s2 = np.array([m[r["id"]] for r in R2]); s0 = np.array([me[r["id"]] for r in ev])
    reps = []
    for _ in range(2000):
        c = np.bincount(rng.integers(0,len(pairs),len(pairs)), minlength=len(pairs)).astype(float)
        reps.append(wauc(s4, s2, c[i4], c[i2]))
    ci = np.percentile(reps,[2.5,97.5])
    rho, p = spearmanr(s4, mc)
    print(f"{lab:14s} R0vsR4 {auc(s4,s0):.3f}  R0vsR2 {auc(s2,s0):.3f}  R2vsR4 {auc(s4,s2):.3f} [{ci[0]:.3f},{ci[1]:.3f}]  potent-only R2vsR4 {auc(s4[pot],s2):.3f}  non-potent {auc(s4[~pot],s2):.3f}  Spearman(score, min-cos | morphs) {rho:+.3f} (p={p:.2g})")
