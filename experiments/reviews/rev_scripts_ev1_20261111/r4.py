import sys, csv, numpy as np, pathlib, collections, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib import *
from scipy.stats import kendalltau
OUT = pathlib.Path("/home/narolski/smad-next/experiments/EV1_fixed-threshold-reread")
FM = [r for r in csv.DictReader(open(OUT/"A2_family_means.csv")) if r["alpha"] == "0.05"]
print(len(FM), collections.Counter(r["block"] for r in FM))
rel = [r for r in FM if r["block"] == "release" and "own preprocessing" not in r["detector"]]
def seedmean(m, col): return float(np.mean([float(r[col]) for r in FM if r["block"] == m]))
rows = [(r["detector"], float(r["native_family_mean_eer_pct"]), 100*float(r["native_family_mean_miss"]), 100*float(r["worst_pool_family_mean_miss"]), 100*float(r["family_worst_pool_mean_miss"]), r["binding_pool"]) for r in rel]
for m in ("M3","M3L"):
    rows.append((m+" seed mean", seedmean(m,"native_family_mean_eer_pct"), 100*seedmean(m,"native_family_mean_miss"), 100*seedmean(m,"worst_pool_family_mean_miss"), 100*seedmean(m,"family_worst_pool_mean_miss"), ""))
print(f"{'detector':48s} natEER  natMiss5  wpMiss5  famWP  binding")
for r in rows: print(f"{r[0]:48s} {r[1]:6.1f} {r[2]:8.1f} {r[3]:8.1f} {r[4]:6.1f}  {r[5]}")
e = [r[1] for r in rows]; n = [r[2] for r in rows]; w = [r[3] for r in rows]; fw = [r[4] for r in rows]
k = lambda a, b: "tau %.3f p %.3f" % (kendalltau(a, b).statistic, kendalltau(a, b).pvalue)
print("12 rows: EER vs worst-pool miss   ", k(e, w))
print("12 rows: EER vs native miss@5     ", k(e, n), " <- metric change alone, no pool change")
print("12 rows: native miss@5 vs worst   ", k(n, w), " <- pool change alone")
print("12 rows: EER vs family worst-pool ", k(e, fw))
# drop rows that are broken on our frames / diagnostic variants
keep = [i for i, r in enumerate(rows) if not any(x in r[0] for x in ("dnorm", "dscale", "SelfMAD release, our pipeline", "MixFaceNet"))]
print("kept rows:", [rows[i][0] for i in keep])
g = lambda L: [L[i] for i in keep]
print(f"{len(keep)} rows: EER vs worst-pool miss   ", k(g(e), g(w)))
print(f"{len(keep)} rows: EER vs native miss@5     ", k(g(e), g(n)))
print(f"{len(keep)} rows: native miss@5 vs worst   ", k(g(n), g(w)))
# bootstrap-free uncertainty of tau: leave-one-out range
taus = [kendalltau([e[j] for j in range(len(e)) if j != i], [w[j] for j in range(len(e)) if j != i]).statistic for i in range(len(e))]
print("leave-one-row-out tau range (EER vs worst-pool):", round(min(taus),3), round(max(taus),3))
# worst-pool thresholds: realised FA on devbona and FRLL orig
PA = json.load(open(OUT/"A_partA.json"))
for nm in ("MADation ViT-L/14 release","MADation ViT-B/16 release","SelfMAD release, own preprocessing","MADation FE ViT-L/14 release"):
    m = PA["meta"][nm]; print(nm, "t5", round(m["t_0.05"],4), "t_wp", round(m["t_wp_0.05"],4), "binding", m["wp_binding_pool_0.05"], "FA at wp on FRLL orig", m["fa_at_wp_0.05"].get("FRLL orig"))
