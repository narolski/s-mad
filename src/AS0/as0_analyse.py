"""Mirror-asymmetry test (AS0), step 4: registered contrasts, history shifts, dose curve, confound reads, verdict.

  python3 -I as0_analyse.py [--B 2000] [--sets ...]   -> experiments/AS0_mirror-asymmetry/{contrasts.csv, history.csv,
                                                        dose.csv, shares.csv, verdict.json, analysis.json}
Statistic L = ln(E_A / E_S) per band (B0..B6), channel (Y, R, G, B, RGB) and flip (F0, F1); score for "X against Y" is
-L, positive class X, AUC = P(L(X) < L(Y)). Bootstrap: AR1 stats.py (a41_read.Draw pigeonhole person bootstrap,
a36_read.wauc), imported unchanged; seed [20261111, 61].
"""
import argparse
import collections
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import as0_common as K  # noqa: E402

sys.path.insert(0, str(K.REPO / "src/AR1"))
import stats as ST  # noqa: E402  (AR1 stats.py: Draw, wauc_rep, ci)

SEED = [20261111, 61]
BANDS = ["B0", "B1", "B2", "B3", "B4", "B5", "B6", "BB"]
CHS = ["Y", "R", "G", "B", "RGB"]
MAD = pathlib.Path("/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z")
EVALCSV = K.MC / "smadcvpr_data/manifests/eval.csv"


class Data:
    def __init__(self):
        z = np.load(K.OUT / "meas_all.npz", allow_pickle=False)
        self.ids = z["ids"].tolist()
        self.ix = {i: n for n, i in enumerate(self.ids)}
        EA, ES = z["EA"], z["ES"]                        # [n, 4, 2, 7]
        EA = np.concatenate([EA, EA[:, 1:4].sum(1, keepdims=True)], 1)   # + RGB channel sum
        ES = np.concatenate([ES, ES[:, 1:4].sum(1, keepdims=True)], 1)
        bbA = EA[..., 1:6].sum(-1, keepdims=True)
        bbS = ES[..., 1:6].sum(-1, keepdims=True)
        EA = np.concatenate([EA, bbA], -1)
        ES = np.concatenate([ES, bbS], -1)
        with np.errstate(divide="ignore", invalid="ignore"):
            self.L = np.log(EA / ES)                      # [n, 5 ch, 2 flips, 8 bands]
        self.C = z["C"]
        self.cn = z["cov_names"].tolist()
        self.pix = z["pixhash"].tolist()
        self.items = {it["id"]: it for it in K.read_csv(K.OUT / "items.csv")}

    def cov(self, ids, name):
        j = self.cn.index(name)
        return np.array([self.C[self.ix[i], j] for i in ids])

    def ok(self, i):
        n = self.ix.get(i)
        if n is None:
            return False
        c = self.C[n]
        return c[self.cn.index("lm_ok")] == 1 and c[self.cn.index("mask0")] >= 1000 and np.isfinite(self.L[n, 0, 0, 1])

    def sel(self, pred):
        return [i for i, it in self.items.items() if pred(it) and self.ok(i)]

    def val(self, ids, ch="Y", flip=0, band="B1"):
        if band == "SH":
            return self.cov(ids, "shape_L")
        return np.array([self.L[self.ix[i], CHS.index(ch), flip, BANDS.index(band)] for i in ids])


def persons(D, ids):
    return [tuple(D.items[i]["persons"].split("|")) for i in ids]


def auc_ci(Dr, D, X, Y, **kw):
    x, y = -D.val(X, **kw), -D.val(Y, **kw)
    m = np.isfinite(x)
    n = np.isfinite(y)
    X2, Y2 = [i for i, k in zip(X, m) if k], [i for i, k in zip(Y, n) if k]
    x, y = x[m], y[n]
    a, (lo, hi) = ST.wauc_ci(Dr, x, persons(D, X2), y, persons(D, Y2))
    return dict(auc=round(a, 4), lo=round(float(lo), 4), hi=round(float(hi), 4), nX=len(x), nY=len(y),
                medLX=round(float(np.median(-x)), 4), medLY=round(float(np.median(-y)), 4))


def auc_scores(Dr, D, X, Y, sx, sy):
    a, (lo, hi) = ST.wauc_ci(Dr, sx, persons(D, X), sy, persons(D, Y))
    return dict(auc=round(a, 4), lo=round(float(lo), 4), hi=round(float(hi), 4), nX=len(sx), nY=len(sy))


def draw_for(D, ids, B):
    ps = sorted({p for i in ids for p in D.items[i]["persons"].split("|")})
    return ST.Draw(ps, B, SEED)


def wmedian(v, w):
    o = np.argsort(v)
    c = np.cumsum(w[o])
    return float(v[o][np.searchsorted(c, c[-1] / 2)])


class Out:
    def __init__(self):
        self.rows = []

    def add(self, family, contrast, subset, res, ch="Y", flip="F0", band=""):
        self.rows.append(dict(family=family, contrast=contrast, subset=subset, channel=ch, flip=flip, band=band, **res))


def run_contrasts(D, out, fam, X, Y, name, subset="all", B=2000, chans=("Y",), flips=(0,), bands=BANDS, shape=True,
                  Dr=None):
    Dr = Dr or draw_for(D, X + Y, B)
    for ch in chans:
        for fl in flips:
            for b in bands:
                out.add(fam, name, subset, auc_ci(Dr, D, X, Y, ch=ch, flip=fl, band=b), ch, f"F{fl}", b)
    if shape:
        out.add(fam, name, subset, auc_ci(Dr, D, X, Y, band="SH"), "shape", "-", "shape")
    return Dr


def paired(D, A_ids, B_ids, key):
    """pair two id lists by key(it) -> (a, b) lists of matched ids."""
    kb = {key(D.items[i]): i for i in B_ids}
    pa, pb = [], []
    for i in A_ids:
        k = key(D.items[i])
        if k in kb:
            pa.append(i)
            pb.append(kb[k])
    return pa, pb


def history_shift(D, nat, cop, Dr, ch="Y", flip=0, band="B1"):
    """d = mean(L(copy) - L(native)) / SD(L(native)); weights = person counts of the draw (bootstrap CI)."""
    a, b = D.val(nat, ch, flip, band), D.val(cop, ch, flip, band)
    m = np.isfinite(a) & np.isfinite(b)
    a, b = a[m], b[m]
    pp = [p for p, k in zip(persons(D, nat), m) if k]
    d0 = float((b - a).mean() / a.std(ddof=1))
    W = ST.weights(Dr, pp)
    reps = []
    for w in W:
        s = w.sum()
        if s <= 0:
            continue
        mu = (w * (b - a)).sum() / s
        ma = (w * a).sum() / s
        sd = np.sqrt((w * (a - ma) ** 2).sum() / s)
        reps.append(mu / sd)
    lo, hi = np.percentile(reps, [2.5, 97.5])
    return dict(d=round(d0, 4), lo=round(float(lo), 4), hi=round(float(hi), 4), n=int(m.sum()),
                mean_diff=round(float((b - a).mean()), 4), sd_native=round(float(a.std(ddof=1)), 4))


def cutoff_bands(scale, iod):
    fc = 0.5 * scale
    uc = np.log2(fc * iod)
    return [f"B{k}" for k in range(1, 6) if k + 0.5 <= uc], float(uc)


def residual_auc(D, Dr, X, Y, covs, band, ch="Y", flip=0):
    ids = X + Y
    yv = D.val(ids, ch, flip, band)
    Z = [np.ones(len(ids))]
    for c in covs:
        if c == "abs_yaw":
            Z.append(np.abs(D.cov(ids, "yaw")))
        else:
            Z.append(D.cov(ids, c))
    Z = np.stack(Z, 1)
    m = np.isfinite(yv) & np.isfinite(Z).all(1)
    beta = np.linalg.lstsq(Z[m], yv[m], rcond=None)[0]
    r = yv - Z @ beta
    nx = len(X)
    rx, ry = r[:nx], r[nx:]
    mx, my = m[:nx], m[nx:]
    Xk = [i for i, k in zip(X, mx) if k]
    Yk = [i for i, k in zip(Y, my) if k]
    return auc_scores(Dr, D, Xk, Yk, -rx[mx], -ry[my])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--test-permute", action="store_true",
                    help="code test only: rows of L shuffled (no real contrast), outputs to OUT/test_analysis")
    a = ap.parse_args()
    B = a.B
    D = Data()
    if a.test_permute:
        rng = np.random.default_rng(7)
        D.L = D.L[rng.permutation(len(D.L))]
        D.C[:, D.cn.index("shape_L")] = rng.permutation(D.C[:, D.cn.index("shape_L")])
        K.RES = K.OUT / "test_analysis"
        K.RES.mkdir(exist_ok=True)
    out = Out()
    res = {}
    nom = json.load(open(K.OUT / "iod_nominal.json"))
    excl = collections.Counter(it["set"] for i, it in D.items.items() if i in D.ix and not D.ok(i))
    missing = collections.Counter(it["set"] for i, it in D.items.items() if i not in D.ix)
    res["excluded_no_face_or_small_mask"] = dict(excl)
    res["not_measured"] = dict(missing)

    # ------------------------------------------------------------------ L: landmark ladder (primary)
    Lr = lambda role, tool=None: D.sel(lambda it: it["set"] == "L" and it["role"] == role and
                                       (tool is None or it["tool"] == tool))
    allL = D.sel(lambda it: it["set"] == "L")
    DrL = draw_for(D, allL + D.sel(lambda it: it["set"] == "R8"), B)
    for tool in (None, "opencv", "facemorpher"):
        sub = tool or "pooled"
        R0, S0 = Lr("R0"), Lr("S0")
        R2, R2w, R2wm, R3, R3m, R4 = (Lr(g, tool) for g in ("R2", "R2w", "R2wm", "R3", "R3m", "R4"))
        chans = CHS if tool is None else ("Y",)
        flips = (0, 1) if tool is None else (0,)
        for name, X, Y in (("K1 R4 vs R3", R4, R3), ("K2 R4 vs R2w", R4, R2w), ("K3 R3 vs R2w", R3, R2w),
                           ("K4 R2w vs R0", R2w, R0), ("K5 R3m vs R2w", R3m, R2w), ("R2 vs R0", R2, R0),
                           ("R2wm vs R0", R2wm, R0), ("S0 vs R0", S0, R0), ("R4 vs R0", R4, R0)):
            run_contrasts(D, out, "L", X, Y, name, sub, B, chans=chans if name.startswith("K1") else ("Y",),
                          flips=flips if name.startswith("K1") else (0,), Dr=DrL)
    # paired quantities per host: positive-control collapse, person-specific share, R4 shift
    shares = []
    for tool in ("opencv", "facemorpher", None):
        sub = tool or "pooled"
        tools = [tool] if tool else ["opencv", "facemorpher"]
        for b in BANDS:
            r3, r3m, r4 = [], [], []
            pp = []
            for t in tools:
                for it in [D.items[i] for i in Lr("R2w", t)]:
                    h = it["host"]
                    ids = {g: f"L|{h}|{t}|{g}" for g in ("R2w", "R3", "R3m", "R4")}
                    if not all(D.ok(x) for x in ids.values()):
                        continue
                    v = {g: D.val([x], band=b)[0] for g, x in ids.items()}
                    r3.append(np.exp(v["R3"] - v["R2w"]))
                    r3m.append(np.exp(v["R3m"] - v["R2w"]))
                    r4.append(np.exp(v["R4"] - v["R2w"]))
                    pp.append((h,))
            r3, r3m, r4 = map(np.array, (r3, r3m, r4))
            W = ST.weights(DrL, pp)
            reps = np.array([[wmedian(r3, w), wmedian(r3m, w), wmedian(r4, w)] for w in W[:500] if w.sum() > 0])
            q = np.percentile(reps, [2.5, 97.5], axis=0)
            m3, m3m, m4 = float(np.median(r3)), float(np.median(r3m)), float(np.median(r4))
            shares.append(dict(subset=sub, band=b, n_hosts_x_tools=len(r3), med_ratio_R3_over_R2w=round(m3, 4),
                               ci_R3=[round(x, 4) for x in q[:, 0]], person_share_pi=round(2 * m3 - 1, 4),
                               ci_pi=[round(2 * x - 1, 4) for x in q[:, 0]],
                               med_ratio_R4_over_R2w=round(m4, 4), ci_R4=[round(x, 4) for x in q[:, 2]],
                               predicted_R4=0.5, med_ratio_R3m_over_R2w=round(m3m, 4),
                               ci_R3m=[round(x, 4) for x in q[:, 1]]))
    K.write_csv(K.RES / "shares.csv", [{k: (json.dumps(v) if isinstance(v, list) else v) for k, v in r.items()}
                                       for r in shares])
    # dose curve
    dose = []
    G = {}
    for it in [D.items[i] for i in D.sel(lambda it: it["set"] == "L" and it["role"] == "G")]:
        G.setdefault(it["host"], {})[float(it["level"])] = it["id"]
    hosts = sorted(h for h, v in G.items() if len(v) == 6)
    levels = [0.1, 0.2, 0.3, 0.4, 0.5]
    pred = {m: float(np.log(m * m + (1 - m) ** 2)) for m in levels}
    for b in BANDS + ["SH"]:
        dl = np.array([[D.val([G[h][m]], band=b)[0] - D.val([G[h][0.0]], band=b)[0] for m in levels] for h in hosts])
        pv = np.array([pred[m] for m in levels])
        beta = float((dl * pv).sum() / (len(hosts) * (pv ** 2).sum()))
        W = ST.weights(DrL, [(h,) for h in hosts])
        reps = [float((w[:, None] * dl * pv).sum() / (w.sum() * (pv ** 2).sum())) for w in W if w.sum() > 0]
        lo, hi = np.percentile(reps, [2.5, 97.5])
        row = dict(band=b, n_hosts=len(hosts), beta=round(beta, 4), lo=round(float(lo), 4), hi=round(float(hi), 4),
                   reading=("follows the square-root law" if 0.7 <= beta <= 1.3 else
                            ("shrinks less" if beta < 0.7 else "shrinks more")))
        for j, m in enumerate(levels):
            row[f"med_dL_m{int(m * 100):02d}"] = round(float(np.median(dl[:, j])), 4)
            row[f"pred_m{int(m * 100):02d}"] = round(pred[m], 4)
            X = [G[h][m] for h in hosts]
            Y = [G[h][0.0] for h in hosts]
            row[f"auc_m{int(m * 100):02d}_vs_m00"] = auc_ci(DrL, D, X, Y, band=b)["auc"] if b != "SH" else \
                auc_ci(DrL, D, X, Y, band="SH")["auc"]
        dose.append(row)
    K.write_csv(K.RES / "dose.csv", dose)

    # confounds on K1 (pooled tools, Y, F0)
    R3all, R4all = Lr("R3"), Lr("R4")
    def gap(i):
        g = D.items[i]["gap_days"]
        return float(g) if g != "" else np.nan
    for lab, lo_, hi_ in (("gap<=60d", -1, 60), ("gap61-365d", 60, 365), ("gap>365d", 365, 1e9)):
        X = [i for i in R4all if lo_ < gap(i) <= hi_]
        Y = [i for i in R3all if lo_ < gap(i) <= hi_]
        if len(X) > 20 and len(Y) > 20:
            for b in BANDS:
                out.add("L-confound", "K1 R4 vs R3", lab, auc_ci(DrL, D, X, Y, band=b), "Y", "F0", b)
    # pose (|yaw| of the morph shape), pose gap, lighting gap tertiles
    hostcov = lambda pid, name: D.cov([f"L|{pid}|R0"], name)[0]
    partcov = lambda i, name: (D.cov([f"L|{D.items[i]['host']}|S0"], name)[0] if D.items[i]["role"] == "R3" else
                               D.cov([f"L|{D.items[i]['persons'].split('|')[1]}|S0"], name)[0])
    feats = {
        "abs_yaw": lambda i: abs(D.cov([i], "yaw")[0]),
        "pose_gap": lambda i: abs(hostcov(D.items[i]["host"], "yaw") - partcov(i, "yaw")),
        "light_gap": lambda i: abs(hostcov(D.items[i]["host"], "light") - partcov(i, "light")),
        "abs_light": lambda i: abs(D.cov([i], "light")[0]),
    }
    for fname, f in feats.items():
        vx = np.array([f(i) for i in R4all])
        vy = np.array([f(i) for i in R3all])
        cuts = np.percentile(np.concatenate([vx, vy]), [100 / 3, 200 / 3])
        for t, (lo_, hi_) in enumerate(((-np.inf, cuts[0]), (cuts[0], cuts[1]), (cuts[1], np.inf))):
            X = [i for i, v in zip(R4all, vx) if lo_ < v <= hi_]
            Y = [i for i, v in zip(R3all, vy) if lo_ < v <= hi_]
            for b in ("B1", "B2", "B3", "B4", "B5", "BB"):
                out.add("L-confound", "K1 R4 vs R3", f"{fname} tertile {t + 1} ({lo_:.3g},{hi_:.3g}]",
                        auc_ci(DrL, D, X, Y, band=b), "Y", "F0", b)
        res[f"K1_{fname}_median_R4_R3"] = [float(np.median(vx)), float(np.median(vy))]
    # partial out
    for b in ("B1", "B2", "B3", "B4", "B5", "BB"):
        for lab, cv in (("resid lap_mask", ["lap_mask"]), ("resid pose+light", ["abs_yaw", "yaw", "nose_off", "light"]),
                        ("resid all", ["lap_mask", "abs_yaw", "yaw", "nose_off", "light"])):
            out.add("L-confound", "K1 R4 vs R3", lab, residual_auc(D, DrL, R4all, R3all, cv, b), "Y", "F0", b)
    for c in ("lap_mask", "lap_full", "abs_yaw", "light", "mask0", "shape_L"):
        vx = np.abs(D.cov(R4all, "yaw")) if c == "abs_yaw" else D.cov(R4all, c)
        vy = np.abs(D.cov(R3all, "yaw")) if c == "abs_yaw" else D.cov(R3all, c)
        r_ = auc_scores(DrL, D, R4all, R3all, -vx, -vy)
        out.add("L-confound", "K1 R4 vs R3", f"covariate alone: -{c}", r_, c, "-", "-")
    # R8 same-session / cross-session (both engines pooled and per engine)
    for tool in (None, "opencv", "facemorpher"):
        sub = tool or "pooled"
        r8 = lambda ss: D.sel(lambda it: it["set"] == "R8" and str(it["same_session"]) == ss and
                              (tool is None or it["tool"] == tool))
        same, cross = r8("1"), r8("0")
        R4t = Lr("R4", tool)
        R3t = Lr("R3", tool)
        for name, X, Y in (("R8 cross vs R8 same", cross, same), ("R4 vs R8 same", R4t, same),
                           ("R4 vs R8 cross", R4t, cross), ("R8 cross vs L R3", cross, R3t)):
            for b in BANDS:
                out.add("R8", name, sub, auc_ci(DrL, D, X, Y, band=b), "Y", "F0", b)
            out.add("R8", name, sub, auc_ci(DrL, D, X, Y, band="SH"), "shape", "-", "shape")
        res[f"R8_counts_{sub}"] = dict(same=len(same), cross=len(cross))
        # expression-matched same-session subset (colorFERET fa+fa or fb+fb) and FRGC same-day
        fe_match = D.sel(lambda it: it["set"] == "R8" and str(it["same_session"]) == "1" and it["expr_a"] == it["expr_b"]
                         and (tool is None or it["tool"] == tool))
        if len(fe_match) > 20:
            for b in BANDS:
                out.add("R8", "R4 vs R8 same (same expression code)", sub, auc_ci(DrL, D, R4t, fe_match, band=b),
                        "Y", "F0", b)

    # ------------------------------------------------------------------ history controls
    hist = []
    def add_hist(set_, fam, nat, cop, scale, iod, flips=(0,), chans=("Y",)):
        Dr = draw_for(D, nat, B)
        below, uc = cutoff_bands(scale, iod) if scale else ([], np.nan)
        for ch in chans:
            for fl in flips:
                for b in BANDS:
                    r = history_shift(D, nat, cop, Dr, ch, fl, b)
                    hist.append(dict(set=set_, copy=fam, channel=ch, flip=f"F{fl}", band=b,
                                     below_cutoff=int(b in below), scale=round(scale, 4) if scale else "",
                                     u_cutoff=round(uc, 3), **r))
    canon_iod = nom["ar1_512"]["median"]
    # Fm
    e7 = {}
    for l in open(MAD / "e7_attempts.jsonl"):
        d = json.loads(l)
        if d.get("family") == "bona":
            e7[(d["target_family"], d["photo_id"])] = d.get("scale")
    for fam in ("FaceMorpher", "OpenCV", "Webmorph"):
        nat, cop = [], []
        sc = []
        for i in D.sel(lambda it: it["set"] == "Fm" and it["role"] == f"e7_{fam}"):
            s = D.items[i]["src"]
            if D.ok(s) and D.pix[D.ix[i]] != D.pix[D.ix[s]]:
                nat.append(s); cop.append(i)
                sc.append(e7.get((fam, s.split("|")[1]), 1.0))
        res[f"Fm_{fam}_differing_copies"] = len(cop)
        if len(cop) > 20:
            add_hist("Fm", fam, nat, cop, float(np.median(sc)), canon_iod,
                     flips=(0, 1) if fam == "FaceMorpher" else (0,), chans=CHS if fam == "FaceMorpher" else ("Y",))
    # Fe: target = median ied of the family's FRLL-Morphs morph rows (orig) in eval.csv
    tgt, nat_ied = collections.defaultdict(list), {}
    for r in csv.DictReader(open(EVALCSV)):
        if r["set"] != "frllm":
            continue
        if r["label"] == "1" and r["variant"] == "orig" and r["ied"]:
            tgt[r["family"]].append(float(r["ied"]))
        if r["label"] == "0" and r["variant"] == "orig" and r["ied"]:
            nat_ied[pathlib.Path(r["path"]).stem[:-5]] = float(r["ied"])
    for fam in ("amsl", "facemorpher", "opencv", "webmorph"):
        t = float(np.median(tgt[fam])) if tgt.get(fam) else None
        nat, cop, sc = [], [], []
        for i in D.sel(lambda it: it["set"] == "Fe" and it["role"] == f"e7_{fam}"):
            s = D.items[i]["src"]
            if D.ok(s) and D.pix[D.ix[i]] != D.pix[D.ix[s]]:
                nat.append(s); cop.append(i)
                ni = nat_ied.get(s.split("|")[1])
                sc.append(min(1.0, t / ni) if (t and ni) else np.nan)
        res[f"Fe_{fam}_differing_copies"] = len(cop)
        res[f"Fe_{fam}_target_ied"] = t
        if len(cop) > 20:
            add_hist("Fe", fam, nat, cop, float(np.nanmedian(sc)), canon_iod)
    # Lsoft
    soft = {r["path"]: r for r in K.read_csv(pathlib.Path("/mnt/t7/smad_next/AF0/soft_ar1soft_src.csv"))}
    for role in ("R0_amsl112", "R0_fm61", "R2w_amsl112", "R2w_fm61"):
        for tool in (("none",) if role.startswith("R0") else ("opencv", "facemorpher")):
            cop = D.sel(lambda it: it["set"] == "Lsoft" and it["role"] == role and it["tool"] == tool and
                        it["aligned"] == "True")        # copies that fell back to a plain resize are left out
            cop = [i for i in cop if D.ok(D.items[i]["src"])]
            nat = [D.items[i]["src"] for i in cop]
            sc = [float(soft[D.items[i]["path"]]["scale"]) for i in cop if soft[D.items[i]["path"]]["scale"]]
            if len(cop) > 20:
                add_hist("Lsoft", f"{role}|{tool}", nat, cop, float(np.median(sc)), nom["ar1_512"]["median"])
    # S (SMDD): copies at 80 px, nominal IOD of smdd80; the cut-off is the copy's own Nyquist (scale 1 in its frame)
    cop = D.sel(lambda it: it["set"] == "S" and it["role"] == "e7")
    cop = [i for i in cop if D.ok(D.items[i]["src"])]
    nat = [D.items[i]["src"] for i in cop]
    if cop:
        add_hist("S", "smdd_e7_80px", nat, cop, 1.0, nom["smdd80"]["median"])
    K.write_csv(K.RES / "history.csv", hist)

    # ------------------------------------------------------------------ GAN blocks
    g = lambda role, ss=None: D.sel(lambda it: it["set"] == "G" and it["role"] == role and
                                    (ss is None or str(it["same_session"]) == ss))
    allG = D.sel(lambda it: it["set"] == "G")
    if allG:
        DrG = draw_for(D, allG, B)
        for name, X, Y in (("x3 vs x2", g("x3"), g("x2")), ("x3 vs x1", g("x3"), g("x1")), ("x2 vs x1", g("x2"), g("x1")),
                           ("x1 vs x0", g("x1"), g("x0")), ("x3 vs x2 same-session x2", g("x3"), g("x2", "1")),
                           ("x3 vs x2 cross-session x2", g("x3"), g("x2", "0"))):
            run_contrasts(D, out, "G", X, Y, name, "all", B, chans=("Y", "RGB"), flips=(0, 1), Dr=DrG)
        res["G_x2_session_counts"] = dict(same=len(g("x2", "1")), cross=len(g("x2", "0")))
    # ------------------------------------------------------------------ diffusion ladder
    d = lambda set_, role: D.sel(lambda it: it["set"] == set_ and it["role"] == role)
    allD = D.sel(lambda it: it["set"] in ("D", "M"))
    if allD:
        DrD = draw_for(D, allD, B)
        for name, X, Y in (("B20 vs C20", d("D", "two20"), d("D", "same20")), ("B20 vs D20", d("D", "two20"), d("D", "rec20")),
                           ("C20 vs D20", d("D", "same20"), d("D", "rec20")), ("D20 vs photo", d("D", "rec20"), d("D", "photo")),
                           ("B100 vs D20", d("D", "two100"), d("D", "rec20")),
                           ("P_AF vs D20r (AD1b)", d("M", "mirror20"), d("M", "rec20r")),
                           ("P_AF vs D20 (all)", d("M", "mirror20"), d("D", "rec20"))):
            if X and Y:
                run_contrasts(D, out, "D", X, Y, name, "all", B, chans=("Y", "RGB"), flips=(0, 1), Dr=DrD)
        # replication of the lead's face-box statistic (medians)
        rep = {}
        for set_, role in (("D", "photo"), ("D", "rec20"), ("D", "same20"), ("D", "two20"), ("D", "two100"),
                           ("M", "mirror20"), ("M", "rec20r")):
            ids = d(set_, role)
            rep[f"{set_}|{role}"] = dict(n=len(ids), box_l1_median=round(float(np.nanmedian(D.cov(ids, "box_l1"))), 3),
                                         mask_l1_median=round(float(np.nanmedian(D.cov(ids, "l1_mask"))), 3))
            sm = [i for i in ids if D.items[i]["host"] in ("001", "002", "003", "004")]
            rep[f"{set_}|{role}"]["box_l1_median_persons_001_004"] = (round(float(np.nanmedian(D.cov(sm, "box_l1"))), 3)
                                                                      if sm else None)
        res["lead_statistic_replication"] = rep
    allDs = D.sel(lambda it: it["set"] == "Ds")
    if allDs:
        DrS = draw_for(D, allDs, B)
        for name, X, Y in (("B20 vs C20 (stored)", d("Ds", "two20"), d("Ds", "same20")),
                           ("B20 vs D20 (stored)", d("Ds", "two20"), d("Ds", "rec20")),
                           ("C20 vs D20 (stored)", d("Ds", "same20"), d("Ds", "rec20")),
                           ("D20 vs photo (stored)", d("Ds", "rec20"), d("Ds", "photo")),
                           ("published MorDIFF vs photo (stored)", d("Ds", "pub_mordiff"), d("Ds", "photo"))):
            run_contrasts(D, out, "Ds", X, Y, name, "all", B, chans=("Y",), flips=(1,), Dr=DrS)
    allX = D.sel(lambda it: it["set"] == "X")
    if allX:
        DrX = draw_for(D, allX, B)
        x = lambda role, ss=None: D.sel(lambda it: it["set"] == "X" and it["role"] == role and
                                        (ss is None or str(it["same_session"]) == ss))
        for name, X, Y in (("two vs same", x("two"), x("same")), ("two vs rec", x("two"), x("rec")),
                           ("same vs rec", x("same"), x("rec")), ("rec vs photo", x("rec"), x("photo")),
                           ("two vs same same-session", x("two"), x("same", "1")),
                           ("two vs same cross-session", x("two"), x("same", "0"))):
            run_contrasts(D, out, "X", X, Y, name, "all", B, chans=("Y",), flips=(0,), Dr=DrX)
        res["X_abs_yaw_median_by_role"] = {r: float(np.median(np.abs(D.cov(x(r), "yaw")))) for r in ("photo", "rec", "same", "two")}

    K.write_csv(K.RES / "contrasts.csv", out.rows)

    # ------------------------------------------------------------------ verdict (registered primary cell)
    def cell(fam, contrast, subset, band, ch="Y", flip="F0"):
        for r in out.rows:
            if (r["family"], r["contrast"], r["subset"], r["band"], r["channel"], r["flip"]) == \
                    (fam, contrast, subset, band, ch, flip):
                return r
    hmap = {(h["set"], h["copy"], h["channel"], h["flip"], h["band"]): h for h in hist}
    smap = {(s["subset"], s["band"]): s for s in shares}
    per_band = {}
    for b in ("B1", "B2", "B3", "B4", "B5"):
        k1 = cell("L", "K1 R4 vs R3", "pooled", b)
        k5 = cell("L", "K5 R3m vs R2w", "pooled", b)
        h = hmap.get(("Fm", "FaceMorpher", "Y", "F0", b))
        s = smap[("pooled", b)]
        collapse = s["med_ratio_R3m_over_R2w"] <= 0.25 and k5["auc"] >= 0.95
        per_band[b] = dict(K1_auc=k1["auc"], K1_ci=[k1["lo"], k1["hi"]], history_d=h["d"] if h else None,
                           history_ci=[h["lo"], h["hi"]] if h else None, history_below_cutoff=h["below_cutoff"] if h else None,
                           R3m_ratio=s["med_ratio_R3m_over_R2w"], K5_auc=k5["auc"], collapse=bool(collapse),
                           passes=bool(k1["auc"] >= 0.70 and h is not None and abs(h["d"]) < 0.1 and collapse))
    kill = all(v["K1_auc"] < 0.60 for v in per_band.values())
    passed = [b for b, v in per_band.items() if v["passes"]]
    verdict = "pass" if passed else ("kill" if kill else "weak")
    V = dict(verdict=verdict, passing_bands=passed, per_band=per_band,
             rule="kill: K1 < 0.60 in every band B1..B5; pass: K1 >= 0.70 and |d| < 0.1 (Fm E7 FaceMorpher) and "
                  "R3m collapse (median ratio <= 0.25 and AUC >= 0.95) in one band; else weak")
    json.dump(V, open(K.RES / "verdict.json", "w"), indent=1)
    res["verdict"] = V
    json.dump(res, open(K.RES / "analysis.json", "w"), indent=1, default=str)
    print(json.dumps(V, indent=1))


if __name__ == "__main__":
    main()
