"""Reviewer: dose reading from existing registered scores - share of E7 (history-matched) FRLL photos flagged vs the morph family's stored size."""
import csv, pathlib, numpy as np, statistics
from scipy.stats import spearmanr
MC = pathlib.Path("/home/narolski/mambamorph-code")
rows = [r for r in csv.DictReader(open(MC/"smadcvpr_data/manifests/eval.csv")) if r["set"] in ("frllm","dim","mordiff")]
fams = [("frllm","amsl","frll_bona"),("frllm","facemorpher","frll_bona"),("frllm","opencv","frll_bona"),("frllm","stylegan","frll_bona"),("frllm","webmorph","frll_bona"),
        ("dim","dim_a","dim_bona"),("dim","greedy_dim","dim_bona"),("mordiff","mordiff","mordiff_bona")]
DETS = [("ViT-B/16 rel","smadcvpr_runs/A12_scored/A12REL/madation_vitb16/scores_eval.npz","score_noTTA"),("ViT-L/14 rel","smadcvpr_runs/A12_scored/A12REL/madation_vitl14/scores_eval.npz","score_noTTA"),
        ("SelfMAD own","experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz","score")]
print(f"{'family':12s} {'morph med width':>15s} " + " ".join(f"{d[0]+' flagged@5%':>26s}" for d in DETS))
res = {d[0]: [] for d in DETS}; widths = []
for st,f,bf in fams:
    m = [r for r in rows if r["set"]==st and r["family"]==f and r["label"]=="1" and r["variant"]=="orig"]
    b = [r for r in rows if r["set"]==st and r["family"]==bf and r["variant"]=="orig"]
    e = [r for r in rows if r["set"]==st and r["family"]==f and r["label"]=="0" and r["variant"]=="resmatch"]
    w = statistics.median(float(r["native_w"]) for r in m); widths.append(w); cells = []
    for lab,fn,key in DETS:
        z = np.load(MC/fn, allow_pickle=False); em = dict(zip(z["id"].tolist(), z[key].astype(float)))
        if not all(r["id"] in em for r in b+e): cells.append("n/a"); res[lab].append(np.nan); continue
        sb = np.array([em[r["id"]] for r in b]); se = np.array([em[r["id"]] for r in e]); t = np.quantile(sb, 0.95, method="higher")
        fr = float((se>t).mean()); res[lab].append(fr); cells.append(f"{100*float((sb>t).mean()):4.1f}% -> {100*fr:5.1f}%")
    print(f"{f:12s} {w:15.0f} " + " ".join(f"{c:>26s}" for c in cells))
for lab in res:
    x = np.array(widths); y = np.array(res[lab]); ok = ~np.isnan(y); rho,p = spearmanr(x[ok], y[ok]); print(f"Spearman(stored width, E7 flag rate) {lab}: {rho:+.2f} (n={ok.sum()} families, p={p:.3f})")
