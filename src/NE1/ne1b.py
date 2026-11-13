"""NE1b (experiments/NE1_nuisance-erasure/prereg_ne1b.md): CPU-only follow-ups on the saved NE1 features.
Part A (H-new-3): splice feature ceiling. Probes for two-person (S4) against same-person (S3) splices, fitted on the
development hosts of L, read on the test hosts, against the frozen head H0.
Part B (H-new-1): rank-7 border erasers (per-mask mean-difference span E7; LEACE on photo + 7 mask classes), fitted on
half-A persons, read on half-B, with two-sided removal in logits, flags and ranks, per-mask reads, recall at each head's
own 99th-percentile camera cut, an isotropic and a covariance null. Storage is not read (dropped from NE1b).
  python -I ne1b.py --feats F --man M --nets N --out ne1b_read.json [--mock] [--only NET,...] [--nboot 2000]"""
import argparse, json, pathlib, sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.neural_network import MLPClassifier

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ne1_heads as N  # noqa: E402  (registered NE1 reader: load, half_a, auc, prank, logreg, sel, cat)

NETS = N.NETS
CGRID = (0.01, 0.1, 1.0, 10.0)
NNULL = 20
TWO = 0.3          # two-sided: |1 - removal| <= 0.3
MASKFRAC = 0.3     # per-mask: |dlogit_m(head)| <= 0.3 * |pooled dlogit(ref)|
MASKMIN = 6        # ... on at least 6 of the 7 masks
RECALL_LOSS = 0.02
AUC_LOSS = 0.01
NULL_MAX_PASS = 1  # at most 1 of 20 isotropic nulls may pass two-sided (logits and flags)
FLOOR_DLOGIT, FLOOR_FLAGS = 0.05, 0.01
SPLICE_FIT = {"splice:S3::opencv": 0, "splice:S3_bg::opencv": 0, "splice:S3_face::opencv": 0,
              "splice:S4::opencv": 1, "splice:S4_bg::opencv": 1, "splice:S4_face::opencv": 1}
S3K, S4K = "splice:S3::opencv", "splice:S4::opencv"
R4K = ("ladder:R4::opencv", "ladder:R4::facemorpher")


# ------------------------------------------------------------------ erasers (functions X -> X')
def span_eraser(D):
    Q, _ = np.linalg.qr(D)
    return lambda X: X - (X @ Q) @ Q.T


def leace_eraser(X, z, floor=1e-8):
    """LEACE (Belrose et al. 2023), closed form: r(x) = x - W^+ P W (x - mu), W = Sigma^{-1/2}, P = projection onto
    colspace(W Sigma_XZ); z = integer class labels (one-hot). Eigenvalues below floor * max are dropped."""
    mu = X.mean(0); Xc = X - mu
    S = Xc.T @ Xc / len(X); ev, V = np.linalg.eigh(S); keep = ev > floor * ev.max()
    V, ev = V[:, keep], ev[keep]
    W = (V / np.sqrt(ev)) @ V.T; Wp = (V * np.sqrt(ev)) @ V.T
    Z = np.eye(z.max() + 1)[z]; Zc = Z - Z.mean(0)
    A = W @ (Xc.T @ Zc / len(X))
    U, s, _ = np.linalg.svd(A, full_matrices=False); U = U[:, s > 1e-10 * s.max()]
    M = Wp @ U @ U.T @ W
    return lambda Y: Y - (Y - mu) @ M.T, int(U.shape[1])


def lin(m):
    return m.coef_[0].astype(np.float64), float(m.intercept_[0])


# ------------------------------------------------------------------ part A
def part_a(D, w, b):
    L = N.sel(D["read"], D["read"]["set"] == "L")
    dev, tst = N.sel(L, L["role"] == "dev"), N.sel(L, L["role"] == "test")
    fit = N.sel(dev, np.isin(dev["kind"], list(SPLICE_FIT)))
    yf = np.array([SPLICE_FIT[k] for k in fit["kind"]])
    cv = {}
    for C in CGRID:
        oof = np.zeros(len(yf))
        for tr, te in GroupKFold(5).split(fit["F"], yf, fit["host"]):
            oof[te] = N.logreg(fit["F"][tr], yf[tr], C).decision_function(fit["F"][te])
        cv[str(C)] = N.auc(oof[yf == 1], oof[yf == 0])
    Cb = max(CGRID, key=lambda C: (cv[str(C)], -C))
    pl = N.logreg(fit["F"], yf, Cb)
    mlp = MLPClassifier(hidden_layer_sizes=(256,), alpha=1e-3, max_iter=2000, random_state=0).fit(fit["F"], yf)
    T = D["train"]; tm = np.isin(T["kind"], ["lad_S3", "lad_S4"])
    pt = N.logreg(T["F"][tm], (T["kind"][tm] == "lad_S4").astype(int), 1.0)
    core = np.isin(tst["kind"], [S3K, S4K]); y4 = tst["kind"] == S4K
    var = np.isin(tst["kind"], list(SPLICE_FIT)); yv = np.array([SPLICE_FIT.get(k, -1) for k in tst["kind"]])
    sc = dict(H0=tst["F"] @ w + b, lin=pl.decision_function(tst["F"]), mlp=mlp.predict_proba(tst["F"])[:, 1],
              lin_T=pt.decision_function(tst["F"]))
    out = dict(C_lin=Cb, cv_auc=cv, n_fit=int(len(yf)), n_fit_hosts=int(len(np.unique(fit["host"]))),
               n_test_hosts=int(len(np.unique(tst["host"][core]))))
    for k, s in sc.items():
        out[f"auc_core_{k}"] = N.auc(s[core & y4], s[core & ~y4])
        out[f"auc_variants_{k}"] = N.auc(s[var & (yv == 1)], s[var & (yv == 0)])
    return out, sc, tst, core, y4


# ------------------------------------------------------------------ part B
def part_b(D, w, b, rng_null):
    T, Gt, Rd = D["train"], D["gate"], D["read"]
    rcam = N.sel(Gt, Gt["kind"] == "R_cam"); B = N.sel(Rd, Rd["set"] == "B"); L = N.sel(Rd, Rd["set"] == "L")
    Cc = N.sel(Rd, Rd["set"] == "C")
    hA = lambda d: np.array([N.half_a(h) for h in d["host"]])
    P = N.cat(rcam, N.sel(L, np.char.startswith(L["kind"].astype(str), "ladder:R0:")))
    Lt = N.sel(L, L["role"] == "test"); R4 = N.sel(Lt, np.isin(Lt["kind"], R4K))
    BA, BB = N.sel(B, hA(B)), N.sel(B, ~hA(B)); rA = N.sel(rcam, hA(rcam))
    ridx = {i: k for k, i in enumerate(rcam["id"])}
    bpair = np.array([ridx[i.split("__")[0][len("bref_"):]] for i in BB["id"]])
    masks = sorted({k.split(":")[1] for k in B["kind"]})
    bm = np.array([k.split(":")[1] for k in BB["kind"]])
    # erasers fitted on half A
    d1 = N.unit(BA["F"].mean(0) - rA["F"].mean(0))
    D7 = np.stack([BA["F"][BA["kind"] == f"border:{m}"].mean(0) - rA["F"].mean(0) for m in masks], 1)
    XL = np.concatenate([rA["F"], BA["F"]]); zL = np.r_[np.zeros(len(rA["F"]), int), [1 + masks.index(k.split(":")[1]) for k in BA["kind"]]]
    Eleace, rank_leace = leace_eraser(XL, zL)
    ER = {"E1": span_eraser(d1[:, None]), "E7": span_eraser(D7), "LEACE": Eleace}
    cov = np.cov(T["F"], rowvar=False)
    for j in range(NNULL):
        ER[f"I{j:02d}"] = span_eraser(rng_null.normal(size=(512, 7)))
    for j in range(NNULL):
        ER[f"V{j:02d}"] = span_eraser(rng_null.multivariate_normal(np.zeros(512), cov, size=7, method="eigh").T)
    heads = {"H0": (None, w, b), "H1": (None,) + lin(N.logreg(T["F"], T["y"]))}
    for e, f in ER.items():
        heads[f"{e}r"] = (f,) + lin(N.logreg(f(T["F"]), T["y"]))
        if not e.startswith(("I", "V")):
            heads[f"{e}o"] = (f, w, b)
    sets = dict(P=P, rcam=rcam, BB=BB, C=Cc, R4=R4)
    sc = {h: {k: (d["F"] if f is None else f(d["F"])) @ ww + bb for k, d in sets.items()} for h, (f, ww, bb) in heads.items()}
    hu, hinv = np.unique(BB["host"], return_inverse=True)
    pos = Cc["kind"] == "landmark_combined_orig"

    def reads(h, Ps=None, sel_hosts=None):
        s = sc[h]; ref = np.sort(s["P"] if Ps is None else s["P"][Ps])
        t = float(np.quantile(s["P"] if Ps is None else s["P"][Ps], 0.99))
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
        R[h]["auc_C"] = N.auc(sc[h]["C"][pos], sc[h]["C"][~pos])
        R[h]["recall_C_p99"] = float((sc[h]["C"][pos] > t).mean())
        R[h]["recall_R4_p99"] = float((sc[h]["R4"] > t).mean())
    return R, heads, reads, sc, dict(masks=masks, rank_leace=rank_leace, n_pairs=len(bpair), n_hosts=len(hu),
                                     P=len(P["y"]), R4=len(R4["y"]), hu=hu, P_host=P["host"], C_host=Cc["host"], pos=pos)


def removal(R, h, ref, unit):
    v = R[ref][unit]
    return None if abs(v) < 1e-12 else float(1 - R[h][unit] / v)


def two(x):
    return x is not None and abs(1 - x) <= TWO


def judge(R, e, ref="H1"):
    """per-seed conditions for eraser e (refit head vs H1)."""
    h = f"{e}r"
    rm = {u: removal(R, h, ref, u) for u in ("dlogit", "dflag", "drank")}
    mask_ok = sum(abs(R[h]["dlogit_mask"][m]) <= MASKFRAC * abs(R[ref]["dlogit"]) for m in R[h]["dlogit_mask"])
    c = dict(removal=rm, two_logit=two(rm["dlogit"]), two_flag=two(rm["dflag"]), two_rank=two(rm["drank"]), masks_ok=int(mask_ok),
             recall_C_loss=R[ref]["recall_C_p99"] - R[h]["recall_C_p99"], recall_R4_loss=R[ref]["recall_R4_p99"] - R[h]["recall_R4_p99"],
             auc_loss=R[ref]["auc_C"] - R[h]["auc_C"])
    c["removed"] = c["two_logit"] and c["two_flag"] and c["two_rank"] and mask_ok >= MASKMIN
    c["no_cost"] = c["recall_C_loss"] <= RECALL_LOSS and c["recall_R4_loss"] <= RECALL_LOSS and c["auc_loss"] <= AUC_LOSS
    return c


def one_net(D, w, b, rng_null, rng_boot, nboot):
    A, scA, tst, core, y4 = part_a(D, w, b)
    R, heads, reads, sc, info = part_b(D, w, b, rng_null)
    floor = R["H1"]["dlogit"] <= FLOOR_DLOGIT or R["H1"]["dflag"] <= FLOOR_FLAGS
    J = {e: judge(R, e) for e in ("E1", "E7", "LEACE")}
    Jo = {e: {u: removal(R, f"{e}o", "H0", u) for u in ("dlogit", "dflag", "drank")} for e in ("E1", "E7", "LEACE")}
    iso = [judge(R, f"I{j:02d}") for j in range(NNULL)]; cvn = [judge(R, f"V{j:02d}") for j in range(NNULL)]
    nulls = dict(iso_pass=sum(x["two_logit"] and x["two_flag"] for x in iso), cov_pass=sum(x["two_logit"] and x["two_flag"] for x in cvn),
                 iso_removal_flag=[x["removal"]["dflag"] for x in iso], cov_removal_flag=[x["removal"]["dflag"] for x in cvn],
                 iso_removal_logit=[x["removal"]["dlogit"] for x in iso], cov_removal_logit=[x["removal"]["dlogit"] for x in cvn],
                 iso_auc_C=[R[f"I{j:02d}r"]["auc_C"] for j in range(NNULL)], cov_auc_C=[R[f"V{j:02d}r"]["auc_C"] for j in range(NNULL)])
    for e in J:
        J[e]["clean"] = J[e]["removed"] and J[e]["no_cost"] and nulls["iso_pass"] <= NULL_MAX_PASS
    # bootstrap (hosts): part A probe - H0 AUC on test hosts; part B removal (logits, flags) and recall loss per eraser
    ut = np.unique(tst["host"][core]); th = {h: np.flatnonzero((tst["host"] == h) & core) for h in ut}
    ciA = {k: [] for k in ("lin", "mlp")}
    up = np.unique(info["P_host"]); pidx = {h: np.flatnonzero(info["P_host"] == h) for h in up}; hpos = {h: i for i, h in enumerate(info["hu"])}
    ciB = {f"{e}_{u}": [] for e in ("E7", "LEACE") for u in ("dlogit", "dflag")}
    uc = np.unique(info["C_host"]); ch = {h: np.flatnonzero(info["C_host"] == h) for h in uc}; ciC = {e: [] for e in ("E7", "LEACE")}
    for _ in range(nboot):
        p = np.concatenate([th[h] for h in rng_boot.choice(ut, len(ut))]); q = y4[p]
        a0 = N.auc(scA["H0"][p][q], scA["H0"][p][~q])
        for k in ciA:
            ciA[k].append(N.auc(scA[k][p][q], scA[k][p][~q]) - a0)
        dr = rng_boot.choice(up, len(up)); Ps = np.concatenate([pidx[h] for h in dr])
        selh = np.array([hpos[h] for h in dr if h in hpos], int)
        rb = {h: reads(h, Ps, selh) for h in ("H1", "E7r", "LEACEr")}
        for e in ("E7", "LEACE"):
            for u in ("dlogit", "dflag"):
                ciB[f"{e}_{u}"].append(removal(rb, f"{e}r", "H1", u))
        pc = np.concatenate([ch[h] for h in rng_boot.choice(uc, len(uc))]); qc = info["pos"][pc]
        for e in ("E7", "LEACE"):
            t1, te = R["H1"]["thr"], R[f"{e}r"]["thr"]
            ciC[e].append(float((sc["H1"]["C"][pc][qc] > t1).mean() - (sc[f"{e}r"]["C"][pc][qc] > te).mean()))
    q = lambda v: N.qci([x for x in v if x is not None])
    keep = [h for h in heads if not h.startswith(("I", "V"))]
    return dict(partA=A, partA_ci={f"{k}_minus_H0": q(v) for k, v in ciA.items()},
                partB=dict(info={k: v for k, v in info.items() if k in ("masks", "rank_leace", "n_pairs", "n_hosts", "P", "R4")},
                           heads={h: R[h] for h in keep}, judge=J, frozen_head_removal=Jo, nulls=nulls, floor=floor,
                           ci={**{k: q(v) for k, v in ciB.items()}, **{f"{e}_recall_C_loss": q(v) for e, v in ciC.items()}}))


def table(per, avail):
    if len(avail) < 4:
        return dict(splice_ceiling="not available", border="not available")
    out = {}
    g = lambda n: per[n]["partA"]
    low = sum(g(n)["auc_core_lin"] <= g(n)["auc_core_H0"] + 0.03 and g(n)["auc_core_mlp"] <= g(n)["auc_core_H0"] + 0.05 for n in avail)
    bot = sum(g(n)["auc_core_lin"] >= max(0.85, g(n)["auc_core_H0"] + 0.10) for n in avail)
    nlo = sum(g(n)["auc_core_lin"] <= g(n)["auc_core_H0"] + 0.03 and g(n)["auc_core_mlp"] >= g(n)["auc_core_H0"] + 0.10 for n in avail)
    out["splice_ceiling"] = ("low ceiling: the frozen features lack a usable same-person vs two-person distinction; no head-level method can supply it" if low >= 4
                             else "head is the bottleneck: the distinction is linearly present in the features" if bot >= 4
                             else "present nonlinearly only" if nlo >= 4
                             else "intermediate (probe above H0 but below the bottleneck bar)") + f" [low {low}, bottleneck {bot}, nonlinear-only {nlo} of {len(avail)}]"
    nf = [n for n in avail if not per[n]["partB"]["floor"]]
    if len(nf) < 4:
        out["border"] = f"floor (not testable) on {len(avail) - len(nf)} of {len(avail)} seeds"
        return out
    J = lambda n, e: per[n]["partB"]["judge"][e]
    res = []
    for e in ("E7", "LEACE"):
        cl = sum(J(n, e)["clean"] for n in nf); rc = sum(J(n, e)["removed"] and not J(n, e)["no_cost"] for n in nf)
        rmv = sum(J(n, e)["removed"] for n in nf); nr = sum(not (J(n, e)["two_logit"] and J(n, e)["two_flag"]) for n in nf)
        res.append((e, cl, rc, rmv, nr))
    clean = [e for e, cl, *_ in res if cl >= 4]
    if clean:
        v = f"clean two-sided removal without recall loss ({', '.join(clean)}): a training-time debiasing arm is worth H100 hours"
    elif any(rc >= 4 for e, cl, rc, rmv, nr in res):
        v = "removable only at a detection cost: border and detection share features; no debiasing arm licensed"
    elif all(nr >= 4 for e, cl, rc, rmv, nr in res):
        v = "not removable two-sidedly by a rank <= 7 linear eraser; no debiasing arm licensed by NE1b"
    else:
        v = "inconclusive (border)"
    out["border"] = v + " [" + "; ".join(f"{e}: clean {cl}, removed-with-cost {rc}, removed {rmv}, not-removed {nr}" for e, cl, rc, rmv, nr in res) + f" of {len(nf)} non-floor seeds]"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feats", required=True); ap.add_argument("--man", required=True); ap.add_argument("--nets", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--mock", action="store_true"); ap.add_argument("--only", default="")
    ap.add_argument("--nboot", type=int, default=2000)
    a = ap.parse_args()
    nets = [n for n in NETS if not a.only or n in a.only.split(",")]
    gate = {"passed": nets} if a.mock else json.load(open(pathlib.Path(a.feats) / "gate.json"))
    rng_null, rng_boot = np.random.default_rng(20261130), np.random.default_rng(20261131)
    per, avail = {}, []
    for n in nets:
        ok = a.mock or all((pathlib.Path(a.feats) / f"{n}__ne1_{m}.npz").exists() for m in ("train", "gate", "read"))
        if not ok:
            print("not available", n); continue
        D, w, b = N.load(a.feats, a.man, a.nets, n, a.mock)
        per[n] = one_net(D, w, b, rng_null, rng_boot, a.nboot)
        per[n]["platform"] = "certified" if n in gate["passed"] else "platform not certified"
        avail.append(n); print("read", n, flush=True)
    out = dict(mock=a.mock, nets=per, available=avail, table=table(per, avail),
               labels=["C is FFHQ: cross-domain for refitted heads; L R4 recall is in-domain", "storage not read in NE1b (dropped)"],
               sklearn=__import__("sklearn").__version__, numpy=np.__version__)
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(out["table"], indent=1))


if __name__ == "__main__":
    main()
