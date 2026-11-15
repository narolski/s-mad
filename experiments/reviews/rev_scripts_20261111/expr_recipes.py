"""Reviewer: expression reading for the 51 primary recipe networks (registered es.pt eval scores). No bootstrap; per-network point values."""
import csv, re, pathlib, numpy as np, collections
from scipy.stats import mannwhitneyu
MC = pathlib.Path("/home/narolski/mambamorph-code"); S = MC/"smadcvpr_runs/A12_scored/A12BR"
rows = [r for r in csv.DictReader(open(MC/"smadcvpr_data/manifests/eval.csv")) if r["set"] in ("frllm","dim") and r["variant"]=="orig"]
bona = [r for r in rows if r["family"]=="frll_bona"]
ex = np.array([pathlib.PurePath(r["path"]).name[4:6] for r in bona]); per = np.array([pathlib.PurePath(r["path"]).name[:3] for r in bona])
cells = {f: [r for r in rows if r["family"]==f and r["label"]=="1"] for f in ("amsl","stylegan","webmorph")}
dimb = [r for r in rows if r["family"]=="dim_bona"]; exd = np.array([pathlib.PurePath(r["path"]).name[4:6] for r in dimb])
cells_d = {f: [r for r in rows if r["family"]==f and r["label"]=="1"] for f in ("dim_a","greedy_dim")}
def auc(p,n): return mannwhitneyu(p,n).statistic/(len(p)*len(n))
def eer(b,m):
    t = np.unique(np.r_[b,m]); fpr = np.array([(b>=x).mean() for x in t]); fnr = np.array([(m<x).mean() for x in t]); i = int(np.argmin(np.abs(fpr-fnr))); return 100*(fpr[i]+fnr[i])/2
out = collections.OrderedDict()
for ln in open(MC/"experiments/A36_published-detector-shortcuts/raw/A36_networks.tsv"):
    if ln.startswith("#") or not ln.strip(): continue
    run, ck, _s, grp, method, arm, seed = ln.rstrip("\n").split("\t")
    if grp != "primary": continue
    name = run.rsplit("/",1)[1]; f = S/name/("scores_eval_es.npz" if ck=="es.pt" else "scores_eval.npz")
    z = np.load(f, allow_pickle=False); em = dict(zip(z["id"].tolist(), z["score"].astype(float)))
    sb = np.array([em[r["id"]] for r in bona]); g = auc(sb[ex=="03"], sb[ex=="08"])
    pn = dict(zip(per[ex=="03"], sb[ex=="03"])); ps = dict(zip(per[ex=="08"], sb[ex=="08"])); k = sum(pn[p]>ps[p] for p in pn)
    d = {}
    for c, mr in cells.items():
        sm = np.array([em[r["id"]] for r in mr]); d[c] = (eer(sb,sm), eer(sb[ex=="03"],sm), eer(sb[ex=="08"],sm))
    sbd = np.array([em[r["id"]] for r in dimb])
    for c, mr in cells_d.items():
        sm = np.array([em[r["id"]] for r in mr]); d[c] = (eer(sbd,sm), eer(sbd[exd=="03"],sm), eer(sbd[exd=="08"],sm))
    out.setdefault(f"{method} | {arm}", []).append((seed, g, k, d))
print(f"{'row':38s} n  P(neu>smi) range [per-seed]            persons neu>smi /102      EER all->neutral-only (mean over seeds): amsl | stylegan | webmorph | dim_a | greedy_dim")
for row, L in out.items():
    gs = [x[1] for x in L]; ks = [x[2] for x in L]
    def m(c): 
        a = np.mean([x[3][c][0] for x in L]); n = np.mean([x[3][c][1] for x in L]); s = np.mean([x[3][c][2] for x in L]); sd = np.std([x[3][c][1]-x[3][c][0] for x in L], ddof=1)
        return f"{a:5.1f}->{n:5.1f} ({n-a:+.1f}±{sd:.1f}; smi {s:5.1f})"
    print(f"{row:38s} {len(L)}  {min(gs):.3f}-{max(gs):.3f} [{' '.join(f'{g:.2f}' for g in gs)}]  {min(ks)}-{max(ks)}   " + " | ".join(m(c) for c in ("amsl","stylegan","webmorph","dim_a","greedy_dim")))
