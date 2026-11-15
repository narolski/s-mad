"""V5: (A) face-only / surround-only heads on the v4 features; (B) own final heads on all 64 blocks scored on set H,
the softened FRLL photos (primary flag rate) and SMDD S_test.
Run: OMP_NUM_THREADS=2 nice -n 10 <spark python> -I v5_blank_and_final.py"""
import json, os, sys
import numpy as np
from scipy.stats import beta
sys.path.insert(0, os.path.dirname(__file__))
import vlib as V

items = V.rows("items.csv"); IT = {r["id"]: r for r in items}
hosts = V.rows("hosts.csv")
HG = [h for h in hosts if h["set"] == "G"]; HH = [h for h in hosts if h["set"] == "Hr"]; HS = [h for h in hosts if h["set"] == "S"]
blocks = sorted({h["cluster"] for h in HG})
ROLE = {r: sorted({h[r] for h in HG}) for r in ("x1", "x2", "x3")}
out = {}


def C(sc, p, n):
    sp, sn = [sc[i] for i in ROLE[p]], [sc[i] for i in ROLE[n]]
    return dict(auc=round(V.auc(sp, sn), 4), ci=[round(x, 4) for x in V.boot_auc(sp, [IT[i]["cluster"] for i in ROLE[p]], sn, [IT[i]["cluster"] for i in ROLE[n]])])


def oof(Ftr, Fte, typ, pos, seed):
    fo = V.block_folds(blocks, 5, seed)
    sc = {}
    for k in range(5):
        tr = [h for h in HG if fo[h["cluster"]] != k]; te = [h for h in HG if fo[h["cluster"]] == k]
        hd, _ = V.fit_head(typ, Ftr, [(h[pos], h["x1"]) for h in tr], [h["cluster"] for h in tr], seed * 10 + k)
        ids = sorted({h[r] for h in te for r in ("x1", "x2", "x3")})
        sc.update(zip(ids, hd(np.array([Fte[i] for i in ids])).tolist()))
    return sc


# ---------- (A) blanking ----------
z = np.load(V.OUT / "v4_blank_feats.npz")
ids = z["id"].tolist()
def nf(X):
    X = X.astype(np.float64); return dict(zip(ids, X / np.linalg.norm(X, axis=1, keepdims=True)))
bl = {}
for kind in ("pool", "patch"):
    Ffull = V.feats("clip", kind, ["G"])
    conds = {"face_only": nf(z[f"face_only_{kind}"]), "surround_only": nf(z[f"surround_only_{kind}"])}
    r = {}
    for cn, Fc in conds.items():
        for typ, pos, lab in (("paired", "x2", "O paired"), ("unpaired", "x2", "O unpaired"), ("paired", "x3", "T paired")):
            a31, a32 = [], []
            for seed in (7, 8, 9):
                sc = oof(Fc, Fc, typ, pos, seed)
                c31, c32 = C(sc, "x3", "x1"), C(sc, "x3", "x2")
                if seed == 7:
                    r[f"{cn} refit {lab} seed7"] = {"x3 vs x1": c31, "x3 vs x2": c32, "x2 vs x1": C(sc, "x2", "x1")}
                a31.append(c31["auc"]); a32.append(c32["auc"])
            r[f"{cn} refit {lab} x3 vs x1 seeds 7-9"] = a31
        sc = oof(Ffull, Fc, "paired", "x2", 7)
        r[f"{cn} full-frame-trained O paired applied"] = {"x3 vs x1": C(sc, "x3", "x1"), "x3 vs x2": C(sc, "x3", "x2")}
        print(kind, cn, {k: v for k, v in r.items() if k.startswith(cn) and ("seeds" in k or "applied" in k)}, flush=True)
    bl[f"clip_{kind}"] = r
out["blanking"] = bl


# ---------- (B) final heads ----------
def cp(k, n):
    return [0.0 if k == 0 else float(beta.ppf(.025, k, n - k + 1)), 1.0 if k == n else float(beta.ppf(.975, k + 1, n - k))]


fin = {}
for bb, kind in (("clip", "pool"), ("clip", "patch"), ("dinov3", "pool")):
    F = V.feats(bb, kind, ["G", "Hr", "Fm", "S"])
    for typ in ("paired", "unpaired"):
        hd, Cf = V.fit_head(typ, F, [(h["x2"], h["x1"]) for h in HG], [h["cluster"] for h in HG], 99)
        s = lambda L_: hd(np.array([F[i] for i in L_]))
        r = {"C": Cf}
        for p, n in (("x3", "x1"), ("x3", "x1s"), ("x1s", "x1")):
            sp, sn = s([h[p] for h in HH]), s([h[n] for h in HH])
            cl = [h["cluster"] for h in HH]
            r[f"H {p} vs {n}"] = dict(auc=round(V.auc(sp, sn), 4), ci=[round(x, 4) for x in V.boot_auc(sp, cl, sn, cl)])
        nat = sorted(i for i in F if i.startswith("Fm|") and IT[i]["role"] == "native")
        e7 = sorted(i for i in F if i.startswith("Fm|") and IT[i]["role"] == "e7_FaceMorpher")
        sn_, se = s(nat), s(e7)
        t = np.quantile(sn_, .95, method="higher"); k = int((se > t).sum())
        r["primary flag MAD22 E7 FaceMorpher"] = dict(k=k, n=len(se), rate=round(k / len(se), 4), cp=[round(x, 4) for x in cp(k, len(se))])
        te = [h for h in HS if h["part"] == "S_test"]
        a0, a1 = s([h["s0"] for h in te]), s([h["s1"] for h in te])
        t = np.quantile(a0, .95, method="higher"); k = int((a1 > t).sum())
        r["SMDD S_test E7 flag"] = dict(k=k, n=len(a1), rate=round(k / len(a1), 4))
        fin[f"{bb}_{kind}_O_{typ}"] = r
        print(bb, kind, typ, json.dumps(r), flush=True)
out["final_heads"] = fin
json.dump(out, open(V.OUT / "v5_blank_and_final.json", "w"), indent=1)
print("done")
