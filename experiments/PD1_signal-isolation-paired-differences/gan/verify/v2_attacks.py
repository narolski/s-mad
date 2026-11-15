"""V2: refutation attempts on cached features: latent averageness, one-identity spread direction from set H,
simple statistics fitted the one-person way (several sets). Run after v1 and v3.
Run: OMP_NUM_THREADS=2 nice -n 10 <spark python> -I v2_attacks.py"""
import json, os, sys
import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
sys.path.insert(0, os.path.dirname(__file__))
import vlib as V

items = V.rows("items.csv"); IT = {r["id"]: r for r in items}
hosts = V.rows("hosts.csv")
HG = [h for h in hosts if h["set"] == "G"]
HH = [h for h in hosts if h["set"] == "Hr"]
blocks = sorted({h["cluster"] for h in HG})
ROLE = {r: sorted({h[r] for h in HG}) for r in ("x0", "x1", "x2", "x3")}
out = {}


def C(sc, p, n):
    sp, sn = [sc[i] for i in ROLE[p]], [sc[i] for i in ROLE[n]]
    return dict(auc=round(V.auc(sp, sn), 4), ci=[round(x, 4) for x in V.boot_auc(sp, [IT[i]["cluster"] for i in ROLE[p]], sn, [IT[i]["cluster"] for i in ROLE[n]])])


def three(sc):
    return {f"{p} vs {n}": C(sc, p, n) for p, n in (("x3", "x1"), ("x3", "x2"), ("x2", "x1"))}


# ---------- latent distance to the mean code ----------
lz = np.load(V.BIG / "latents.npz"); LAT = dict(zip(lz["key"].tolist(), lz["w"].astype(np.float64)))
mG = np.mean([v for k, v in LAT.items() if k.startswith("G|")], 0)
dm = {}
for r in items:
    if r["set"] == "G" and r["role"] != "x0":
        w = np.mean([LAT["G|" + s] for s in r["src"].split(";")], 0)
        dm[r["id"]] = float(np.linalg.norm(w - mG))
negd = {k: -v for k, v in dm.items()}
out["latent_closeness_alone"] = three(negd)
# also distance with per-layer mean of only training blocks would be the same up to noise; report raw medians
out["latent_dist_median_by_rung"] = {r: float(np.median([dm[i] for i in ROLE[r]])) for r in ("x1", "x2", "x3")}

# ---------- head OOF scores from v1 (seed 7) ----------
z = np.load(V.OUT / "v1_oof.npz")
OOF = {k: {a: float(b) for a, b in z[k]} for k in z.files}


def bstat(fn, B=2000, seed=5):
    rng = np.random.default_rng(seed)
    v = []
    for _ in range(B):
        bs = rng.choice(blocks, len(blocks))
        try:
            v.append(fn(list(bs)))
        except Exception:
            pass
    return [round(float(np.quantile(v, .025)), 3), round(float(np.quantile(v, .975)), 3)]


lat = {}
for key in ("clip_pool_O_paired", "clip_patch_O_paired", "dinov3_pool_O_paired", "clip_pool_T_paired", "clip_pool_O_unpaired"):
    sc = OOF[key]
    r = {}
    for role in ("x1", "x2", "x3"):
        ids = ROLE[role]
        rho = spearmanr([sc[i] for i in ids], [negd[i] for i in ids]).statistic

        def f(bs, role=role):
            ii = [i for b in bs for i in ROLE[role] if IT[i]["cluster"] == b]
            return spearmanr([sc[i] for i in ii], [negd[i] for i in ii]).statistic
        r[f"spearman_score_vs_closeness_within_{role}"] = dict(rho=round(float(rho), 3), ci=bstat(f, B=500))
    # residual test: score ~ a + b*closeness fitted on one-person renders (x1, x2) only
    one = ROLE["x1"] + ROLE["x2"]
    A = np.c_[np.ones(len(one)), [negd[i] for i in one]]
    coef = np.linalg.lstsq(A, np.array([sc[i] for i in one]), rcond=None)[0]
    res = {i: sc[i] - coef[0] - coef[1] * negd[i] for i in dm}
    r["residual_after_closeness_fit_on_one_person"] = three(res)
    # x3 vs x2 matched on closeness: nearest x2 (any block) within 0.25 latent units
    d2 = np.array([dm[i] for i in ROLE["x2"]]); s2 = np.array([sc[i] for i in ROLE["x2"]])
    wins, n = [], 0
    for i in ROLE["x3"]:
        j = np.argmin(np.abs(d2 - dm[i]))
        if abs(d2[j] - dm[i]) < 0.25:
            wins.append(sc[i] > s2[j])
    r["x3_beats_closeness_matched_x2"] = dict(share=round(float(np.mean(wins)), 3) if wins else None, n=len(wins))
    lat[key] = r
out["latent_vs_head"] = lat

# ---------- regressors and directions with no mixing at all ----------
nomix = {}
for bb, kind in (("clip", "pool"), ("clip", "patch"), ("dinov3", "pool")):
    F = V.feats(bb, kind, ["G", "Hr"])
    rr = {}
    # (a) ridge predicting closeness from features, trained on x1 reconstructions only, block-OOF
    fo = V.block_folds(blocks, 5, 7)
    sc = {}
    for k in range(5):
        tr = [i for i in ROLE["x1"] if fo[IT[i]["cluster"]] != k]
        te = [i for r_ in ("x1", "x2", "x3") for i in ROLE[r_] if fo[IT[i]["cluster"]] == k]
        st = V.Std().fit(np.array([F[i] for i in tr]))
        y = np.array([negd[i] for i in tr])
        # alpha by inner block CV (correlation)
        best, ba = -9, None
        fi = V.block_folds(sorted({IT[i]["cluster"] for i in tr}), 3, 70 + k)
        for a in (1, 10, 100, 1000, 10000):
            cc = []
            for j in range(3):
                a_tr = [i for i in tr if fi[IT[i]["cluster"]] != j]; a_te = [i for i in tr if fi[IT[i]["cluster"]] == j]
                m = Ridge(alpha=a).fit(st(np.array([F[i] for i in a_tr])), [negd[i] for i in a_tr])
                cc.append(np.corrcoef(m.predict(st(np.array([F[i] for i in a_te]))), [negd[i] for i in a_te])[0, 1])
            if np.mean(cc) > best:
                best, ba = np.mean(cc), a
        m = Ridge(alpha=ba).fit(st(np.array([F[i] for i in tr])), y)
        sc.update(zip(te, m.predict(st(np.array([F[i] for i in te]))).tolist()))
    rr["closeness_regressor_trained_on_reconstructions_only"] = three(sc)
    rr["closeness_regressor_within_x1_oof_spearman"] = round(float(spearmanr([sc[i] for i in ROLE["x1"]], [negd[i] for i in ROLE["x1"]]).statistic), 3)
    # (b) set H one-identity spread direction (x1 -> x1s, CASIA, no G data), raw frame
    u = np.mean([F[h["x1s"]] - F[h["x1"]] for h in HH], 0)
    rr["H_spread_direction_projection"] = three({i: float(F[i] @ u) for i in dm})
    # (c) set H paired head x1s vs x1 (one identity, spread only), C fixed 0.01, applied to G
    imgs = sorted({h[r] for h in HH for r in ("x1", "x1s")})
    hd = V.fit_paired(np.array([F[i] for i in imgs]), np.array([F[h["x1s"]] for h in HH]), np.array([F[h["x1"]] for h in HH]), 0.01)
    rr["H_spread_head_on_G"] = three(dict(zip(list(dm), hd(np.array([F[i] for i in dm])).tolist())))
    # (d) set H 'morph beyond spread' head (x3 vs x1s) applied to G
    imgs = sorted({h[r] for h in HH for r in ("x3", "x1s")})
    hd = V.fit_paired(np.array([F[i] for i in imgs]), np.array([F[h["x3"]] for h in HH]), np.array([F[h["x1s"]] for h in HH]), 0.01)
    rr["H_beyond_spread_head_on_G"] = three(dict(zip(list(dm), hd(np.array([F[i] for i in dm])).tolist())))
    nomix[f"{bb}_{kind}"] = rr
    print(bb, kind, json.dumps(rr), flush=True)
out["no_mixing_signals_on_G"] = nomix

# ---------- simple statistics fitted the one-person way ----------
z7 = np.load(V.BIG / "stats.npz"); S7 = dict(zip(z7["id"].tolist(), z7["S"].astype(float)))
z3 = np.load(V.OUT / "v3_stats.npz"); S3 = dict(zip(z3["id"].tolist(), z3["S"].astype(float))); N3 = list(z3["names"])
sets = {"owner 7 statistics (224 view)": {i: S7[i] for i in S3},
        "own 37 statistics (native, whole+face+surround+bands)": S3,
        "own whole-image only (file bytes, 9 whole, 8 bands, mirror)": {i: S3[i][[0] + list(range(1, 10)) + list(range(28, 37))] for i in S3},
        "own face-ellipse only (9)": {i: S3[i][10:19] for i in S3},
        "own surround only (9)": {i: S3[i][19:28] for i in S3},
        "own 3 numbers: file bytes, all log Laplacian var, all log median |Laplacian|": {i: S3[i][[0, 1, 2]] for i in S3}}
single = {}
for j, nm in enumerate(N3):
    a = V.auc([S3[i][j] for i in ROLE["x3"]], [S3[i][j] for i in ROLE["x1"]])
    single[nm] = round(max(a, 1 - a), 3)
out["own_single_statistic_best_folded_x3_vs_x1"] = sorted(single.items(), key=lambda t: -t[1])[:6]
sh = {}
for nm, SS in sets.items():
    r = {}
    for typ in ("paired", "unpaired"):
        for pos, lab in (("x2", "one-person"), ("x3", "two-person")):
            aucs = []
            for seed in (7, 8, 9):
                fo = V.block_folds(blocks, 5, seed)
                sc = {}
                for k in range(5):
                    tr = [h for h in HG if fo[h["cluster"]] != k]; te = [h for h in HG if fo[h["cluster"]] == k]
                    hd, _ = V.fit_head(typ, SS, [(h[pos], h["x1"]) for h in tr], [h["cluster"] for h in tr], seed * 10 + k)
                    ids = sorted({h[r_] for h in te for r_ in ("x1", "x2", "x3")})
                    sc.update(zip(ids, hd(np.array([SS[i] for i in ids])).tolist()))
                if seed == 7:
                    r[f"{lab} {typ} seed7"] = three(sc)
                aucs.append(V.auc([sc[i] for i in ROLE["x3"]], [sc[i] for i in ROLE["x1"]]))
            r[f"{lab} {typ} x3 vs x1 seeds 7-9"] = [round(a, 3) for a in aucs]
    sh[nm] = r
    print(nm, {k: v for k, v in r.items() if "seeds" in k}, flush=True)
out["statistics_heads"] = sh
json.dump(out, open(V.OUT / "v2_attacks.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("latent_closeness_alone", "latent_dist_median_by_rung", "own_single_statistic_best_folded_x3_vs_x1")}, indent=1))
print(json.dumps(out["latent_vs_head"], indent=1))
