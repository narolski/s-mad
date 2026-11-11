# independent reviewer loader (does not import the study's code)
import csv, pathlib, re, numpy as np
MC = pathlib.Path("/home/narolski/mambamorph-code")
EVAL = MC/"smadcvpr_data/manifests/eval.csv"
GTEST = MC/"smadcvpr_data/manifests/gtest.csv"
FFHQM = pathlib.Path("/mnt/t7/smad_heldout/ffhq_morphs/manifests/ffhqm.csv")
A12REL = MC/"smadcvpr_runs/A12_scored/A12REL"
A12BR = MC/"smadcvpr_runs/A12_scored/A12BR"
OWN = MC/"experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz"
A43 = pathlib.Path("/mnt/t7/smad_heldout/a43")
FRLLM = ("amsl","facemorpher","opencv","stylegan","webmorph")
DIM = ("dim_a","dim_c","fast_dim","fast_dim_ode","greedy_dim","greedy_dim_s")
FAMS = FRLLM + ("mordiff",) + DIM
SETOF = {**{f:"frllm" for f in FRLLM}, "mordiff":"mordiff", **{f:"dim" for f in DIM}}
NATB = {**{f:("frllm","frll_bona") for f in FRLLM}, "mordiff":("mordiff","mordiff_bona"), **{f:("dim","dim_bona") for f in DIM}}
def ok(p):
    s = str(p).lower()
    assert not (("fst" in s) or ("a12sp" in s) or ("a12-sp" in s) or ("valx" in s and "valx_a.csv" not in s)), p
    return p
def rows_eval():
    R = [r for r in csv.DictReader(open(EVAL)) if r["set"] != "mad22" and r["variant"] != "chip"]
    for r in R: r["name"] = pathlib.PurePath(r["path"]).name
    return R
def sel(R, st, fam, var, lab):
    return np.array([i for i, r in enumerate(R) if r["set"]==st and r["family"]==fam and r["variant"]==var and r["label"]==lab])
def load(p, ids, key):
    z = np.load(ok(p), allow_pickle=False)
    m = dict(zip(z["id"].tolist(), z[key].astype(np.float64)))
    return np.array([m.get(i, np.nan) for i in ids])
def rel(name, ids, which="eval", key="logit_noTTA"):
    return load(A12REL/name/f"scores_{which}.npz", ids, key)
def thr(x, a):
    # smallest value t among scores with share(x > t) <= a
    x = np.sort(np.asarray(x, float)); n = len(x)
    for t in np.unique(x):
        if (x > t).mean() <= a + 1e-12: return float(t)
def auc(pos, neg):
    pos = np.asarray(pos, float); neg = np.sort(np.asarray(neg, float))
    lo = np.searchsorted(neg, pos, "left"); hi = np.searchsorted(neg, pos, "right")
    return float((lo + 0.5*(hi-lo)).sum() / (len(pos)*len(neg)))
def eer(b, m):
    t = np.unique(np.r_[b, m]); bs, ms = np.sort(b), np.sort(m)
    fpr = 1 - np.searchsorted(bs, t, "left")/len(b); fnr = np.searchsorted(ms, t, "left")/len(m)
    i = int(np.argmin(np.abs(fpr-fnr))); return 100*(fpr[i]+fnr[i])/2
