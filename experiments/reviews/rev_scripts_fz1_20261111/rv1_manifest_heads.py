"""Reviewer check rv1 (read-only, post hoc, point estimates unless stated): A43 arm attributes; P3 head (seed 401)
expression split, within-arm correlation with PNG bytes / centre Laplacian, AUC within PNG-size strata; partner leakage
in the clip_mad P2 probe."""
import sys, csv, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/FZ1")
import fz1_common as K
from fz1_probe import person_folds
from scipy.stats import spearmanr
rows = K.a43_rows(); g = K.a43_groups(rows)
byid = {r["id"]: r for r in rows}
print("arm  n  native_w(med) native_h(med) file_bytes(med) border_frac(med) steps expr-counts")
for a in ["A","B","B20","C","C20","D","D20","E"]:
    rr = [rows[i] for i in g[a]]
    f = lambda k: np.median([float(r[k]) for r in rr if r[k] != ""]) if any(r[k] != "" for r in rr) else float("nan")
    ex = {}
    for r in rr: ex[r["expr"]] = ex.get(r["expr"], 0) + 1
    ws = sorted({r["native_w"] for r in rr})
    print(a, len(rr), f("native_w"), f("native_h"), f("file_bytes"), round(f("border_frac"),4), sorted({r["steps"] for r in rr}), ex, "n distinct widths", len(ws))
H = np.load(K.BIG / "heads/scores_a43.npz"); hid = {k: i for i, k in enumerate(H["id"].tolist())}
s = H["s401_a43"]
S = np.load(K.BIG / "p4_stats_values.npz"); sid = {k: i for i, k in enumerate(S["ids"].tolist())}
def sc(a): return np.array([s[hid[rows[i]["id"]]] for i in g[a]])
print("\nP3 head s401, expression split (B arm expr = pair expression)")
for big, small in [("B20","C20"),("B","C"),("B20","D20"),("B","D")]:
    for e in ["03","08"]:
        ii = [i for i in g[big] if rows[i]["expr"] == e]
        pos = np.array([s[hid[rows[i]["id"]]] for i in ii])
        print(f"  {big}[expr {e}] vs {small}: n={len(ii)} AUC={K.auc(pos, sc(small)):.3f}")
    for e in ["03","08"]:
        if small.startswith("D"):
            jj = [i for i in g[small] if rows[i]["src_a"][4:6] == e]
            print(f"  {big}[expr {e}] vs {small}[photo {e}]: AUC={K.auc(np.array([s[hid[rows[i]['id']]] for i in g[big] if rows[i]['expr']==e]), np.array([s[hid[rows[j]['id']]] for j in jj])):.3f} (n_neg={len(jj)})")
print("\nWithin-arm Spearman of P3 head s401 with stats (view224 png_bytes = col 6; center256 laplacian = col 1)")
for a in ["B","D","B20","D20"]:
    ii = [i for i in g[a] if rows[i]["id"] in sid]
    hs = np.array([s[hid[rows[i]["id"]]] for i in ii]); st = S["view224"][[sid[rows[i]["id"]] for i in ii]]; sc2 = S["center256"][[sid[rows[i]["id"]] for i in ii]]
    print(f"  {a}: n={len(ii)} rho(head,png)={spearmanr(hs, st[:,6])[0]:+.3f} rho(head,lap_c256)={spearmanr(hs, sc2[:,1])[0]:+.3f} rho(head,lap_224)={spearmanr(hs, st[:,1])[0]:+.3f}")
print("\nP3 head s401 B vs D within PNG-size quintiles (pooled B u D quintile edges)")
for b_, d_ in [("B","D"),("B20","D20")]:
    ib = [i for i in g[b_]]; idd = [i for i in g[d_]]
    pb = np.array([float(rows[i]["file_bytes"]) for i in ib]); pd = np.array([float(rows[i]["file_bytes"]) for i in idd])
    print(f"  {b_} vs {d_}: AUC(png bytes, morph higher) = {K.auc(pb, pd):.3f}")
    edges = np.quantile(np.r_[pb, pd], [0, .2, .4, .6, .8, 1])
    num = den = 0
    for q in range(5):
        lo, hi = edges[q], edges[q+1] + (1 if q == 4 else 0)
        mb = (pb >= lo) & (pb < hi); md = (pd >= lo) & (pd < hi)
        if mb.sum() and md.sum():
            a = K.auc(sc(b_)[mb], sc(d_)[md]); num += a * mb.sum() * md.sum(); den += mb.sum() * md.sum()
            print(f"    q{q}: nB={mb.sum()} nD={md.sum()} AUC={a:.3f}")
    print(f"    pair-weighted within-stratum AUC = {num/den:.3f}")
print("\nPartner leakage, clip_mad P2 probe, fold seed 401: test morphs whose partner shares the host's fold vs not")
O = np.load(K.BIG / "probe_oof.npz")
for c in ["B20_vs_D20","B_vs_D","B20_vs_C20"]:
    oo = O[f"clip_mad__{c}"]; ids = O[f"clip_mad__{c}__ids"].tolist()
    P = [K.pers_a43(byid[i]) for i in ids]
    fold = person_folds([p for t in P for p in t], 401)
    p, y = oo[:,0], oo[:,1].astype(int)
    neg = p[y == 0]
    same = np.array([len(t) == 2 and t[0] != t[1] and fold[t[0]] == fold[t[1]] for t in P])
    m1 = (y == 1) & same; m2 = (y == 1) & ~same & np.array([len(t) == 2 and t[0] != t[1] for t in P])
    print(f"  {c}: partner in same fold n={m1.sum()} AUC={K.auc(p[m1], neg):.3f} | partner in training n={m2.sum()} AUC={K.auc(p[m2], neg):.3f} | all {K.auc(p[y==1], neg):.3f}")
