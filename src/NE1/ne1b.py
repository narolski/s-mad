"""NE1b (experiments/NE1_nuisance-erasure/prereg_ne1b.md, pre-run fixes 1-7 of PRERUN_NE1B_20261113.md): CPU-only
follow-ups on the saved NE1 features. Storage is not read (dropped from NE1b).
Part A (H-new-3): splice feature ceiling. Binding: 5-fold cross-fitting over connected components of the person graph
(host - partner edges, AR1 pool) of all 291 L hosts; probes for two-person (S4) against same-person (S3) splices; the
frozen head H0 on the same out-of-fold rows. Printed: the 80 clean test hosts, the old 191-host read, a learning curve,
a host-level label-permutation null, a core-only probe and the training-list probe.
Part B (H-new-1): rank-7 border erasers (E7 per-mask mean-difference span; LEACE with Ledoit-Wolf covariance), fitted on
half-A persons, read on half B; ceiling eraser E7c (half B) checked first; two-sided removal in logits, flags and
ranks; per-mask reads; binding cost on in-domain L test-host (half B) R4 recall at each head's own 99th-percentile
camera cut and R4-vs-R0 AUC, tolerance referenced to isotropic nulls; FFHQ landmark_combined printed only.
  python -I ne1b.py --feats F --man M --nets N --out ne1b_read.json [--mock] [--only NET,...] [--nboot 2000]"""
import argparse, csv, json, pathlib, sys
import numpy as np
from sklearn.covariance import LedoitWolf
from sklearn.model_selection import GroupKFold
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ne1_heads as N  # noqa: E402  (registered NE1 reader: load, half_a, auc, prank, logreg, sel, cat, unit, qci)

NETS = N.NETS
POOL = pathlib.Path("/mnt/t7/smad_next/AR1/pool.csv")
CLEAN_LIST = pathlib.Path("/mnt/t7/smad_next/DATA/overlap/test_hosts_clean_of_dev.csv")  # DATA audit 1b05940
CGRID = (0.01, 0.1, 1.0, 10.0)
AGRID = (1e-3, 1e-1, 1.0, 10.0)
NNULL = 20
NPERM = 20
LCURVE = (25, 50, 75, 100)
TWO = 0.3          # two-sided: |1 - removal| <= 0.3
MASKFRAC = 0.3     # per-mask: |dlogit_m(head)| <= 0.3 * |pooled dlogit(ref)|
MASKMIN = 6        # ... on at least 6 of the 7 masks
RECALL_TOL = 0.02  # recall loss tolerance floor; the binding tolerance is max(0.02, largest isotropic-null loss)
AUC_LOSS = 0.01
FLOOR_DLOGIT, FLOOR_FLAGS = 0.05, 0.01
SPLICE_FIT = {"splice:S3::opencv": 0, "splice:S3_bg::opencv": 0, "splice:S3_face::opencv": 0,
              "splice:S4::opencv": 1, "splice:S4_bg::opencv": 1, "splice:S4_face::opencv": 1}
S3K, S4K = "splice:S3::opencv", "splice:S4::opencv"
R4K = ("ladder:R4::opencv", "ladder:R4::facemorpher")
R0K = "ladder:R0::none"


# ------------------------------------------------------------------ helpers
def components(hosts, pool):
    par = {}

    def find(x):
        par.setdefault(x, x)
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for h in hosts:
        a, b = find(h), find(pool[h]["B_pid"])
        par[a] = b
    return {h: find(h) for h in hosts}


def span_eraser(D):
    Q, _ = np.linalg.qr(D)
    return (lambda X: X - (X @ Q) @ Q.T), Q


def leace_eraser(X, z, floor=1e-8):
    """LEACE (Belrose et al. 2023), closed form, Ledoit-Wolf shrunk covariance (pre-run fix 6):
    r(x) = x - W^+ P W (x - mu), W = Sigma^{-1/2}, P = projection onto colspace(W Sigma_XZ)."""
    mu = X.mean(0); Xc = X - mu
    S = LedoitWolf().fit(Xc).covariance_; ev, V = np.linalg.eigh(S); keep = ev > floor * ev.max()
    diag = dict(cond=float(ev[keep].max() / ev[keep].min()), kept=int(keep.sum()), dim=int(len(ev)))
    V, ev = V[:, keep], ev[keep]
    W = (V / np.sqrt(ev)) @ V.T; Wp = (V * np.sqrt(ev)) @ V.T
    Z = np.eye(z.max() + 1)[z]; Zc = Z - Z.mean(0)
    A = W @ (Xc.T @ Zc / len(X))
    U, s, _ = np.linalg.svd(A, full_matrices=False); U = U[:, s > 1e-10 * s.max()]
    M = Wp @ U @ U.T @ W
    diag["rank"] = int(U.shape[1])
    return (lambda Y: Y - (Y - mu) @ M.T), diag


def lin(m):
    return m.coef_[0].astype(np.float64), float(m.intercept_[0])


def mlp_logit(sc, m, X):
    """pre-sigmoid output of a fitted MLPClassifier (no saturation)."""
    h = sc.transform(X)
    for i, (Wt, bt) in enumerate(zip(m.coefs_, m.intercepts_)):
        h = h @ Wt + bt
        if i < len(m.coefs_) - 1:
            h = np.maximum(h, 0)
    return h[:, 0]


def fit_lin(X, y, g):
    """class-balanced logistic; C by 5-fold GroupKFold (AUC), ties -> smaller C."""
    cv = {}
    k = min(5, len(np.unique(g)))
    for C in CGRID:
        oof = np.zeros(len(y))
        for tr, te in GroupKFold(k).split(X, y, g):
            oof[te] = N.logreg(X[tr], y[tr], C).decision_function(X[te])
        cv[C] = N.auc(oof[y == 1], oof[y == 0])
    Cb = max(CGRID, key=lambda C: (cv[C], -C))
    return N.logreg(X, y, Cb), Cb


def fit_mlp(X, y, g):
    """StandardScaler + MLP (256 hidden), alpha by 5-fold GroupKFold (AUC) (pre-run fix 7)."""
    k = min(5, len(np.unique(g))); cv = {}
    for a in AGRID:
        oof = np.zeros(len(y))
        for tr, te in GroupKFold(k).split(X, y, g):
            s = StandardScaler().fit(X[tr]); m = MLPClassifier((256,), alpha=a, max_iter=2000, random_state=0).fit(s.transform(X[tr]), y[tr])
            oof[te] = mlp_logit(s, m, X[te])
        cv[a] = N.auc(oof[y == 1], oof[y == 0])
    ab = max(AGRID, key=lambda a: (cv[a], a))  # ties -> larger alpha (stronger regularisation)
    s = StandardScaler().fit(X); m = MLPClassifier((256,), alpha=ab, max_iter=2000, random_state=0).fit(s.transform(X), y)
    return (lambda Z: mlp_logit(s, m, Z)), ab


# ------------------------------------------------------------------ part A
def part_a(D, w, b, pool, rng_a, nboot):
    L = N.sel(D["read"], D["read"]["set"] == "L")
    hosts = sorted(set(L["host"])); comp = components(hosts, pool)
    cs = sorted(set(comp.values())); fold_of = dict(zip(cs, rng_a.permutation(len(cs)) % 5))
    fold = np.array([fold_of[comp[h]] for h in L["host"]]); cid = np.array([comp[h] for h in L["host"]])
    fitm = np.isin(L["kind"], list(SPLICE_FIT)); yall = np.array([SPLICE_FIT.get(k, -1) for k in L["kind"]])
    core = np.isin(L["kind"], [S3K, S4K]); y4 = L["kind"] == S4K
    X = L["F"]; h0 = X @ w + b
    oof = {k: np.full(len(X), np.nan) for k in ("lin", "mlp", "lin_core")}
    lc = {n: np.full(len(X), np.nan) for n in LCURVE + ("all",)}
    perm = [np.full(len(X), np.nan) for _ in range(NPERM)]
    chosen = []
    for f in range(5):
        tr = fitm & (fold != f); te = core & (fold == f)
        m, Cb = fit_lin(X[tr], yall[tr], cid[tr]); oof["lin"][te] = m.decision_function(X[te])
        mf, ab = fit_mlp(X[tr], yall[tr], cid[tr]); oof["mlp"][te] = mf(X[te])
        trc = core & (fold != f); mc, _ = fit_lin(X[trc], yall[trc], cid[trc]); oof["lin_core"][te] = mc.decision_function(X[te])
        chosen.append(dict(fold=f, C=Cb, alpha=ab, n_fit_hosts=int(len(set(L["host"][tr])))))
        trh = sorted(set(L["host"][tr])); order = rng_a.permutation(len(trh))
        for n in LCURVE + ("all",):
            keep = set(np.array(trh)[order[: (len(trh) if n == "all" else n)]])
            tm = tr & np.isin(L["host"], list(keep))
            lc[n][te] = N.logreg(X[tm], yall[tm], Cb).decision_function(X[te])
        for j in range(NPERM):
            flip = {h: bool(rng_a.integers(2)) for h in trh}
            yp = np.array([(1 - y) if flip.get(h, False) else y for y, h in zip(yall, L["host"])])
            perm[j][te] = N.logreg(X[tr], yp[tr], Cb).decision_function(X[te])
    T = D["train"]; tm = np.isin(T["kind"], ["lad_S3", "lad_S4"])
    pt = N.logreg(T["F"][tm], (T["kind"][tm] == "lad_S4").astype(int), 1.0); linT = pt.decision_function(X)
    A = lambda s, m=core: N.auc(s[m & y4], s[m & ~y4])
    out = dict(n_hosts=len(hosts), n_components=len(cs), folds=chosen,
               auc_H0=A(h0), auc_lin=A(oof["lin"]), auc_mlp=A(oof["mlp"]), auc_lin_core=A(oof["lin_core"]), auc_lin_T=A(linT),
               learning_curve={str(n): A(lc[n]) for n in LCURVE + ("all",)},
               perm_null=[A(p) for p in perm])
    sizes = {c: len({h for h in hosts if comp[h] == c}) for c in cs}; big = max(cs, key=lambda c: (sizes[c], c))
    nb = cid != big
    out["largest_component"] = dict(n_hosts=sizes[big], auc_H0_without=A(h0, core & nb), auc_lin_without=A(oof["lin"], core & nb),
                                    auc_mlp_without=A(oof["mlp"], core & nb), fold_hosts=[int(len(set(L["host"][fold == f]))) for f in range(5)])
    # printed: the 80 clean test hosts (fit on dev hosts) and the old 191-host read
    dev = L["role"] == "dev"; devh = set(L["host"][dev]); devp = {pool[h]["B_pid"] for h in devh}
    clean = np.array([(r == "test") and pool[h]["B_pid"] not in devh and h not in devp for h, r in zip(L["host"], L["role"])])
    m, _ = fit_lin(X[fitm & dev], yall[fitm & dev], L["host"][fitm & dev]); sd = m.decision_function(X)
    aud = {r["host"] for r in csv.DictReader(open(CLEAN_LIST))}
    assert set(L["host"][clean]) == aud, "clean test hosts differ from the DATA audit list"
    out["clean_test"] = dict(n_hosts=int(len(set(L["host"][clean]))), auc_H0=A(h0, core & clean), auc_lin=A(sd, core & clean))
    tst = L["role"] == "test"
    out["old_191"] = dict(n_hosts=int(len(set(L["host"][tst]))), auc_H0=A(h0, core & tst), auc_lin=A(sd, core & tst))
    # bootstrap over components: lin - H0, mlp - H0 (out-of-fold scores fixed)
    uc = np.array(cs); cix = {c: np.flatnonzero(core & (cid == c)) for c in cs}
    bl, bm = [], []
    for _ in range(nboot):
        p = np.concatenate([cix[c] for c in rng_a.choice(uc, len(uc))]); q = y4[p]
        a0 = N.auc(h0[p][q], h0[p][~q])
        bl.append(N.auc(oof["lin"][p][q], oof["lin"][p][~q]) - a0); bm.append(N.auc(oof["mlp"][p][q], oof["mlp"][p][~q]) - a0)
    out["ci_lin_minus_H0"] = N.qci(bl); out["ci_mlp_minus_H0"] = N.qci(bm)
    return out


# ------------------------------------------------------------------ part B
def part_b(D, w, b, rng_null):
    T, Gt, Rd = D["train"], D["gate"], D["read"]
    d = T["F"].shape[1]
    rcam = N.sel(Gt, Gt["kind"] == "R_cam"); B = N.sel(Rd, Rd["set"] == "B"); L = N.sel(Rd, Rd["set"] == "L")
    Cc = N.sel(Rd, Rd["set"] == "C")
    hA = lambda x: np.array([N.half_a(h) for h in x["host"]])
    P = N.cat(rcam, N.sel(L, np.char.startswith(L["kind"].astype(str), "ladder:R0:")))
    LtB = N.sel(L, (L["role"] == "test") & ~hA(L))   # in-domain reads: half-B test hosts (pre-run fix 7)
    R4 = N.sel(LtB, np.isin(LtB["kind"], R4K)); R0 = N.sel(LtB, LtB["kind"] == R0K)
    BA, BB = N.sel(B, hA(B)), N.sel(B, ~hA(B)); rA, rB = N.sel(rcam, hA(rcam)), N.sel(rcam, ~hA(rcam))
    ridx = {i: k for k, i in enumerate(rcam["id"])}
    bpair = np.array([ridx[i.split("__")[0][len("bref_"):]] for i in BB["id"]])
    masks = sorted({k.split(":")[1] for k in B["kind"]})
    bm = np.array([k.split(":")[1] for k in BB["kind"]])
    d1 = N.unit(BA["F"].mean(0) - rA["F"].mean(0))
    D7 = np.stack([BA["F"][BA["kind"] == f"border:{m}"].mean(0) - rA["F"].mean(0) for m in masks], 1)
    D7c = np.stack([BB["F"][BB["kind"] == f"border:{m}"].mean(0) - rB["F"].mean(0) for m in masks], 1)
    XL = np.concatenate([rA["F"], BA["F"]]); zL = np.r_[np.zeros(len(rA["F"]), int), [1 + masks.index(k.split(":")[1]) for k in BA["kind"]]]
    Eleace, ldiag = leace_eraser(XL, zL)
    E1, _ = span_eraser(d1[:, None]); E7, Q7 = span_eraser(D7); E7c, _ = span_eraser(D7c)
    ER = {"E1": E1, "E7": E7, "E7c": E7c, "LEACE": Eleace}
    cov = np.cov(T["F"], rowvar=False); wh = w / np.linalg.norm(w); a7 = float(np.linalg.norm(Q7.T @ wh))
    for j in range(NNULL):
        ER[f"I{j:02d}"] = span_eraser(rng_null.normal(size=(d, 7)))[0]
    for j in range(NNULL):
        ER[f"V{j:02d}"] = span_eraser(rng_null.multivariate_normal(np.zeros(d), cov, size=7, method="eigh").T)[0]
    for j in range(NNULL):   # head-matched: |projection of w-hat on the span| = E7's (pre-run fix 3c)
        R_ = rng_null.normal(size=(d, 7)); R_ -= np.outer(wh, wh @ R_); Qr, _ = np.linalg.qr(R_)
        u = a7 * wh + np.sqrt(max(0.0, 1 - a7 ** 2)) * Qr[:, 0]
        ER[f"M{j:02d}"] = span_eraser(np.c_[u, Qr[:, 1:7]])[0]
    heads = {"H0": (None, w, b), "H1": (None,) + lin(N.logreg(T["F"], T["y"]))}
    for e, f in ER.items():
        heads[f"{e}r"] = (f,) + lin(N.logreg(f(T["F"]), T["y"]))
        if e in ("E1", "E7", "E7c", "LEACE"):
            heads[f"{e}o"] = (f, w, b)
    sets = dict(P=P, rcam=rcam, BB=BB, C=Cc, R4=R4, R0=R0)
    sc = {h: {k: (x["F"] if f is None else f(x["F"])) @ ww + bb for k, x in sets.items()} for h, (f, ww, bb) in heads.items()}
    hu, hinv = np.unique(BB["host"], return_inverse=True)
    pos = Cc["kind"] == "landmark_combined_orig"

    def reads(h, Ps=None, sel_hosts=None):
        s = sc[h]; Pv = s["P"] if Ps is None else s["P"][Ps]; ref = np.sort(Pv); t = float(np.quantile(Pv, 0.99))
        dl = s["BB"] - s["rcam"][bpair]; dr = N.prank(s["BB"], ref) - N.prank(s["rcam"][bpair], ref)
        fx = (s["BB"] > t).astype(float) - (s["rcam"][bpair] > t).astype(float)
        wgt = np.ones(len(hu)) if sel_hosts is None else np.bincount(sel_hosts, minlength=len(hu)).astype(float)

        def hm(v, m=None):
            m = np.ones(len(v), bool) if m is None else m
            num = np.bincount(hinv[m], v[m], minlength=len(hu)); den = np.bincount(hinv[m], minlength=len(hu))
            ok = (den > 0) & (wgt > 0)
            return float((wgt[ok] * num[ok] / den[ok]).sum() / wgt[ok].sum())
        r = dict(dlogit=hm(dl), drank=hm(dr), dflag=hm(fx), thr=t)
        r["dlogit_mask"] = {m: hm(dl, bm == m) for m in masks}; r["dflag_mask"] = {m: hm(fx, bm == m) for m in masks}
        return r
    R = {h: reads(h) for h in heads}
    for h in heads:
        t = R[h]["thr"]
        R[h]["recall_R4_p99"] = float((sc[h]["R4"] > t).mean()); R[h]["auc_R4_R0"] = N.auc(sc[h]["R4"], sc[h]["R0"])
        R[h]["auc_C"] = N.auc(sc[h]["C"][pos], sc[h]["C"][~pos]); R[h]["recall_C_p99"] = float((sc[h]["C"][pos] > t).mean())
    # LEACE diagnostics: residual class-mean spread on half B (pre-run fix 6)
    XB = np.concatenate([rB["F"], BB["F"]]); zB = np.r_[np.zeros(len(rB["F"]), int), [1 + masks.index(k.split(":")[1]) for k in BB["kind"]]]
    spread = lambda Y: float(max(np.linalg.norm(Y[zB == k].mean(0) - Y[zB == 0].mean(0)) for k in range(1, 8)))
    ldiag.update(halfB_spread_before=spread(XB), halfB_spread_after=spread(Eleace(XB)), halfB_spread_after_E7=spread(E7(XB)))
    info = dict(masks=masks, leace=ldiag, a7_w_on_E7=a7, n_pairs=len(bpair), n_hosts=len(hu), P=len(P["y"]), R4=len(R4["y"]), R0=len(R0["y"]),
                hu=hu, P_host=P["host"])
    return R, heads, reads, sc, info


def removal(R, h, ref, unit):
    v = R[ref][unit]
    return None if abs(v) < 1e-12 else float(1 - R[h][unit] / v)


def two(x):
    return x is not None and abs(1 - x) <= TWO


def judge(R, e, tol, ref="H1"):
    h = f"{e}r"
    rm = {u: removal(R, h, ref, u) for u in ("dlogit", "dflag", "drank")}
    mask_ok = sum(abs(R[h]["dlogit_mask"][m]) <= MASKFRAC * abs(R[ref]["dlogit"]) for m in R[h]["dlogit_mask"])
    c = dict(removal=rm, two_logit=two(rm["dlogit"]), two_flag=two(rm["dflag"]), two_rank=two(rm["drank"]), masks_ok=int(mask_ok),
             recall_R4_loss=R[ref]["recall_R4_p99"] - R[h]["recall_R4_p99"], auc_R4_R0_loss=R[ref]["auc_R4_R0"] - R[h]["auc_R4_R0"],
             recall_C_loss=R[ref]["recall_C_p99"] - R[h]["recall_C_p99"], auc_C_loss=R[ref]["auc_C"] - R[h]["auc_C"])
    c["removed"] = bool(c["two_logit"] and c["two_flag"] and c["two_rank"] and mask_ok >= MASKMIN)
    c["no_cost"] = bool(c["recall_R4_loss"] <= tol and c["auc_R4_R0_loss"] <= AUC_LOSS)
    c["clean"] = c["removed"] and c["no_cost"]
    return c


def one_net(D, w, b, pool, rng_a, rng_null, rng_boot, nboot):
    A = part_a(D, w, b, pool, rng_a, nboot)
    R, heads, reads, sc, info = part_b(D, w, b, rng_null)
    floor = R["H1"]["dlogit"] <= FLOOR_DLOGIT or R["H1"]["dflag"] <= FLOOR_FLAGS
    iso_loss = [R["H1"]["recall_R4_p99"] - R[f"I{j:02d}r"]["recall_R4_p99"] for j in range(NNULL)]
    tol = max(RECALL_TOL, max(iso_loss))
    J = {e: judge(R, e, tol) for e in ("E1", "E7", "E7c", "LEACE")}
    Jo = {e: {u: removal(R, f"{e}o", "H0", u) for u in ("dlogit", "dflag", "drank")} for e in ("E1", "E7", "E7c", "LEACE")}
    nulls = {}
    for tag in ("I", "V", "M"):
        js = [judge(R, f"{tag}{j:02d}", tol) for j in range(NNULL)]
        nulls[tag] = dict(two_sided_pass=sum(x["two_logit"] and x["two_flag"] for x in js),
                          removal_logit=[x["removal"]["dlogit"] for x in js], removal_flag=[x["removal"]["dflag"] for x in js],
                          recall_R4_loss=[x["recall_R4_loss"] for x in js], auc_R4_R0_loss=[x["auc_R4_R0_loss"] for x in js])
    up = np.unique(info["P_host"]); pidx = {h: np.flatnonzero(info["P_host"] == h) for h in up}; hpos = {h: i for i, h in enumerate(info["hu"])}
    ci = {f"{e}_{u}": [] for e in ("E7", "LEACE") for u in ("dlogit", "dflag")}
    for _ in range(nboot):
        dr = rng_boot.choice(up, len(up)); Ps = np.concatenate([pidx[h] for h in dr])
        selh = np.array([hpos[h] for h in dr if h in hpos], int)
        rb = {h: reads(h, Ps, selh) for h in ("H1", "E7r", "LEACEr")}
        for e in ("E7", "LEACE"):
            for u in ("dlogit", "dflag"):
                ci[f"{e}_{u}"].append(removal(rb, f"{e}r", "H1", u))
    keep = [h for h in heads if not h[0] in "IVM"]
    return dict(partA=A, partB=dict(info={k: v for k, v in info.items() if k not in ("hu", "P_host")}, heads={h: R[h] for h in keep},
                                    judge=J, frozen_head_removal=Jo, nulls=nulls, recall_tol=tol, floor=bool(floor),
                                    ci={k: N.qci([x for x in v if x is not None]) for k, v in ci.items()}))


def table(per, avail):
    if len(avail) < 4:
        return dict(splice_ceiling="not available", border="not available")
    out = {}
    g = lambda n: per[n]["partA"]
    lc = lambda n: g(n)["learning_curve"]
    low = sum(g(n)["ci_lin_minus_H0"][1] <= 0.05 and g(n)["auc_mlp"] <= g(n)["auc_H0"] + 0.05
              and lc(n)["100"] <= lc(n)["50"] + 0.02 and lc(n)["all"] <= lc(n)["100"] + 0.02
              and g(n)["auc_lin_T"] <= g(n)["auc_H0"] + 0.05 for n in avail)
    bot = sum(g(n)["auc_lin"] >= max(0.85, g(n)["auc_H0"] + 0.10) for n in avail)
    nlo = sum(g(n)["auc_lin"] <= g(n)["auc_H0"] + 0.03 and g(n)["auc_mlp"] >= g(n)["auc_H0"] + 0.10 for n in avail)
    out["splice_ceiling"] = ("low ceiling: a linear or small-MLP head fitted on these development hosts does not separate S4 from S3 better than the "
                             "frozen head; evidence, not proof, that the features lack the distinction" if low >= 4
                             else "head is the bottleneck: the distinction is linearly present (a targeted head refit may be registered as a post-freeze ablation only)" if bot >= 4
                             else "present nonlinearly only (post-freeze ablation only)" if nlo >= 4
                             else "intermediate (probe above H0 but below the bottleneck bar)") + f" [low {low}, bottleneck {bot}, nonlinear-only {nlo} of {len(avail)}]"
    nf = [n for n in avail if not per[n]["partB"]["floor"]]
    if len(nf) < 4:
        out["border"] = f"floor (not testable) on {len(avail) - len(nf)} of {len(avail)} seeds"
        return out
    J = lambda n, e: per[n]["partB"]["judge"][e]
    ceil = sum(J(n, "E7c")["clean"] for n in nf)
    res = []
    for e in ("E7", "LEACE"):
        cl = sum(J(n, e)["clean"] for n in nf); rc = sum(J(n, e)["removed"] and not J(n, e)["no_cost"] for n in nf)
        rmv = sum(J(n, e)["removed"] for n in nf); nr = sum(not (J(n, e)["two_logit"] and J(n, e)["two_flag"]) for n in nf)
        res.append((e, cl, rc, rmv, nr))
    clean = [e for e, cl, *_ in res if cl >= 4]
    if ceil < 4:
        v = "criteria unreachable (inconclusive by design): the half-B ceiling eraser E7c is not clean"
    elif clean:
        v = (f"clean ({', '.join(clean)}): a post-hoc linear eraser removes the border response on frozen features; a training-time "
             "debiasing arm may be registered as a post-freeze ablation beside Sbx (author approval; the result does not predict that "
             "adversarial training succeeds)")
    elif any(rc >= 4 for e, cl, rc, rmv, nr in res):
        v = "removable only at a detection cost: border and detection share features; no debiasing arm licensed"
    elif all(nr >= 4 for e, cl, rc, rmv, nr in res):
        v = "not removable two-sidedly by a rank <= 7 linear eraser; no debiasing arm licensed by NE1b"
    else:
        v = "inconclusive (border)"
    out["border"] = v + f" [E7c clean {ceil}; " + "; ".join(f"{e}: clean {cl}, removed-with-cost {rc}, removed {rmv}, not-removed {nr}" for e, cl, rc, rmv, nr in res) + f" of {len(nf)} non-floor seeds]"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feats", required=True); ap.add_argument("--man", required=True); ap.add_argument("--nets", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--mock", action="store_true"); ap.add_argument("--only", default="")
    ap.add_argument("--nboot", type=int, default=2000)
    a = ap.parse_args()
    nets = [n for n in NETS if not a.only or n in a.only.split(",")]
    gate = {"passed": nets} if a.mock else json.load(open(pathlib.Path(a.feats) / "gate.json"))
    pool = {r["pid"]: r for r in csv.DictReader(open(POOL))}
    rng_a, rng_null, rng_boot = np.random.default_rng(20261132), np.random.default_rng(20261130), np.random.default_rng(20261131)
    per, avail = {}, []
    for n in nets:
        ok = a.mock or all((pathlib.Path(a.feats) / f"{n}__ne1_{m}.npz").exists() for m in ("train", "gate", "read"))
        if not ok:
            print("not available", n); continue
        D, w, b = N.load(a.feats, a.man, a.nets, n, a.mock)
        per[n] = one_net(D, w, b, pool, rng_a, rng_null, rng_boot, a.nboot)
        per[n]["platform"] = "certified" if n in gate["passed"] else "platform not certified"
        avail.append(n); print("read", n, flush=True)
    out = dict(mock=a.mock, nets=per, available=avail, table=table(per, avail),
               labels=["L R4 / R0 reads are in-domain (half-B test hosts); C is FFHQ, printed only", "storage not read in NE1b (dropped)"],
               sklearn=__import__("sklearn").__version__, numpy=np.__version__)
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(out["table"], indent=1))


if __name__ == "__main__":
    main()
