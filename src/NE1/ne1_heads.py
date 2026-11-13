"""NE1 heads, erasers and reads (experiments/NE1_nuisance-erasure/prereg.md sections 4-7, 9; pre-run fixes F1-F8).
DGX CPU, run once. In: --feats DIR with <net>__ne1_{gate,train,read}.npz (id, feat, logit) and gate.json; --man DIR with
ne1_train.csv, ne1_gate.csv, ne1_read.csv; --nets DIR (<net>/last_trainable.pt for H0's w, b). Out: --out JSON.
--mock: random unit features with the real manifests (code test only; nothing is read).
Every head is linear on (possibly erased) features: (eraser direction or None, w, b).
  python -I ne1_heads.py --feats F --man M --nets N --out ne1_read.json [--mock] [--only NET,...]"""
import argparse, csv, hashlib, json, pathlib
import numpy as np
from scipy.stats import rankdata
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold

NETS = [f"PN1_Sb_s{s}" for s in (403, 404, 405, 406, 407)]
CGRID = (0.01, 0.1, 1.0, 10.0)
NBOOT = 2000
NNULL = 20
S3K, S4K = "splice:S3::opencv", "splice:S4::opencv"
FLOOR = 0.01       # border: shift(H0) or shift(H1) at or below 1 percentile point -> seed is "floor"
SFLOOR = 0.02      # storage: shift(H0) at or below 0.02 -> seed is "floor"


def half_a(host):
    return int(hashlib.sha256(host.encode()).hexdigest()[0], 16) < 8


def auc(pos, neg):  # mid-rank AUC
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    r = rankdata(np.concatenate([pos, neg]))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def logreg(X, y, C=1.0, sw=None, balanced=True):
    m = LogisticRegression(C=C, max_iter=5000, class_weight="balanced" if balanced else None)
    m.fit(X, y, sample_weight=sw)
    return m


def group_weights(kind):
    u, inv, cnt = np.unique(np.asarray(kind), return_inverse=True, return_counts=True)
    w = 1.0 / cnt[inv]  # equal total weight per kind (each kind holds one label)
    return w * len(w) / w.sum()


def unit(d):
    return d / np.linalg.norm(d)


def erase(X, d):
    return X if d is None else X - np.outer(X @ d, d)


def head_of(m, d=None):
    return (d, m.coef_[0].astype(np.float64), float(m.intercept_[0]))


def score(h, X):
    d, w, b = h
    return erase(X, d) @ w + b


def prank(s, ref_sorted):
    """mid percentile rank of s in the reference scores (fraction in [0, 1])."""
    lo = np.searchsorted(ref_sorted, s, "left"); hi = np.searchsorted(ref_sorted, s, "right")
    return (lo + hi) / 2.0 / len(ref_sorted)


def thr_at_share(s_ref, k0):
    """old rule (printed only): smallest t with #(s_ref > t) <= k0."""
    s = np.sort(s_ref)[::-1]
    return float(s[k0]) if k0 < len(s) else -np.inf


def thr_at_recall(s_pos, rec):
    """largest t with share(s_pos > t) >= rec."""
    s = np.sort(s_pos)[::-1]; k = int(np.ceil(rec * len(s) - 1e-12))
    if k <= 0:
        return float(s[0])
    return float(np.nextafter(s[k - 1], -np.inf))


def qci(v):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    return [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))] if len(v) else [None, None]


def cv_worst(X, y, kind, groups, sw):
    """5-fold grouped CV: worst-group (kind) accuracy at decision 0 for each C, group-balanced weights."""
    out = {}
    for C in CGRID:
        oof = np.zeros(len(y))
        for tr, te in GroupKFold(5).split(X, y, groups):
            oof[te] = logreg(X[tr], y[tr], C, sw[tr], balanced=False).decision_function(X[te])
        acc = {k: float(((oof[kind == k] > 0).astype(int) == y[kind == k]).mean()) for k in np.unique(kind)}
        out[str(C)] = dict(worst=min(acc.values()), worst_kind=min(acc, key=acc.get), per_kind=acc)
    best = max(CGRID, key=lambda C: (out[str(C)]["worst"], -C))  # tie: smaller C
    return best, out


def probe_auc(X, y, groups):
    oof = np.zeros(len(y))
    for tr, te in GroupKFold(5).split(X, y, groups):
        oof[te] = logreg(X[tr], y[tr]).decision_function(X[te])
    return auc(oof[y == 1], oof[y == 0])


def load(feats, man, nets, n, mock):
    rows = {m: list(csv.DictReader(open(pathlib.Path(man) / f"ne1_{m}.csv"))) for m in ("train", "gate", "read")}
    import torch
    t = torch.load(pathlib.Path(nets) / n / "last_trainable.pt", map_location="cpu", weights_only=True)
    w = t["head.cls.weight"].float().numpy()[0].astype(np.float64); b = float(t["head.cls.bias"].float().numpy()[0])
    out = {}
    for m, rs in rows.items():
        if mock:
            g = np.random.default_rng(len(rs) + int(n[-3:]))
            F = g.normal(size=(len(rs), 512)); F /= np.linalg.norm(F, axis=1, keepdims=True); lg = F @ w + b
        else:
            z = np.load(pathlib.Path(feats) / f"{n}__ne1_{m}.npz")
            assert list(z["id"]) == [r["id"] for r in rs], (n, m)
            F = z["feat"].astype(np.float64); lg = z["logit"].astype(np.float64)
        out[m] = dict(F=F, logit=lg, id=np.array([r["id"] for r in rs]), y=np.array([int(r["label"]) for r in rs]),
                      kind=np.array([r["kind"] for r in rs]), host=np.array([r["host"] for r in rs]),
                      set=np.array([r["set"] for r in rs]), role=np.array([r.get("role", "") for r in rs]))
    return out, w, b


def sel(d, mask):
    return {k: v[mask] for k, v in d.items()}


def cat(a, b):
    return {k: np.concatenate([a[k], b[k]]) for k in a}


def one_net(D, w, b, rng_null):
    T, Gt, Rd = D["train"], D["gate"], D["read"]
    rcam = sel(Gt, Gt["kind"] == "R_cam")
    B = sel(Rd, Rd["set"] == "B"); L = sel(Rd, Rd["set"] == "L"); Cc = sel(Rd, Rd["set"] == "C"); S = sel(Rd, Rd["set"] == "S")
    hA = lambda d: np.array([half_a(h) for h in d["host"]])
    Ld, Lt = sel(L, L["role"] == "dev"), sel(L, L["role"] == "test")
    # reference pool P = R_cam + L ladder R0 (all strengths): camera photos only (lead's answer 2)
    P = cat(rcam, sel(L, np.char.startswith(L["kind"].astype(str), "ladder:R0:")))
    # border pairs (half B): bordered copy -> its unbordered R_cam photo
    BB = sel(B, ~hA(B)); ridx = {i: k for k, i in enumerate(rcam["id"])}
    bpair = np.array([ridx[i.split("__")[0][len("bref_"):]] for i in BB["id"]])
    # storage pairs (half B): copy -> the same person's native photo
    Sp = sel(S, np.char.startswith(S["kind"].astype(str), "photo:")); SB = sel(Sp, ~hA(Sp))
    sidx = {i: k for k, i in enumerate(SB["id"])}
    spair = {cp: (np.flatnonzero(SB["kind"] == f"photo:{cp}"),
                  np.array([sidx[i[:-len(cp) - 1]] for i in SB["id"][SB["kind"] == f"photo:{cp}"]])) for cp in ("fm61", "amsl112")}
    # erasers
    d3 = unit(B["F"][hA(B)].mean(0) - rcam["F"][hA(rcam)].mean(0))          # half A (registered)
    d3c = unit(BB["F"].mean(0) - rcam["F"][~hA(rcam)].mean(0))              # half B (ceiling; fitted on the read rows)
    sA = hA(Sp); nat = Sp["kind"] == "photo:"; sto = np.isin(Sp["kind"], ["photo:fm61", "photo:amsl112"])
    d4 = unit(Sp["F"][sA & sto].mean(0) - Sp["F"][sA & nat].mean(0))
    dm = unit(T["F"][T["y"] == 1].mean(0) - T["F"][T["y"] == 0].mean(0))     # erasure-works check direction
    # heads
    H = {"H0": (None, w, b), "H0e": (d3, w, b), "H0e4": (d4, w, b), "H0ec": (d3c, w, b), "H0em": (dm, w, b)}
    H["H1"] = head_of(logreg(T["F"], T["y"]))
    gw = group_weights(T["kind"]); C2, cv2 = cv_worst(T["F"], T["y"], T["kind"], T["host"], gw)
    H["H2"] = head_of(logreg(T["F"], T["y"], C2, gw, balanced=False))
    H["H1c"] = head_of(logreg(T["F"], T["y"], C2))
    H["H3"] = head_of(logreg(erase(T["F"], d3), T["y"]), d3)
    H["H3c"] = head_of(logreg(erase(T["F"], d3c), T["y"]), d3c)
    H["H4"] = head_of(logreg(erase(T["F"], d4), T["y"]), d4)
    gd = group_weights(Ld["kind"]); C2d, cv2d = cv_worst(Ld["F"], Ld["y"], Ld["kind"], Ld["host"], gd)
    H["H1d"] = head_of(logreg(Ld["F"], Ld["y"]))
    H["H2d"] = head_of(logreg(Ld["F"], Ld["y"], C2d, gd, balanced=False))
    H["H1dc"] = head_of(logreg(Ld["F"], Ld["y"], C2d))
    cov = np.cov(T["F"], rowvar=False)
    nulls = []
    for j in range(NNULL):
        dn = unit(rng_null.multivariate_normal(np.zeros(cov.shape[0]), cov, method="eigh"))
        H[f"N{j:02d}"] = head_of(logreg(erase(T["F"], dn), T["y"]), dn); nulls.append(f"N{j:02d}")
    names = list(H)
    sc = {h: {k: score(H[h], d["F"]) for k, d in (("P", P), ("rcam", rcam), ("BB", BB), ("SB", SB), ("C", Cc), ("Lt", Lt))} for h in names}
    res = dict(C_H2=C2, cv_H2_T=cv2, C_H2d=C2d, cv_H2d_Ldev=cv2d, n=dict(P=len(P["y"]), P_hosts=len(np.unique(P["host"])),
               border_pairs=len(bpair), border_hosts=len(np.unique(BB["host"])), Ldev_rows=len(Ld["y"]), Ldev_hosts=len(np.unique(Ld["host"])),
               Ltest_hosts=len(np.unique(Lt["host"])), S_halfB_hosts=len(np.unique(SB["host"]))),
               h0_linear_max=float(np.abs(sc["H0"]["rcam"] - rcam["logit"]).max()), T_in_sample=all(v["worst"] >= 0.98 for v in cv2.values()))

    # ---- reads
    def border_shift(h, Ps=None, bsel=None):
        ref = np.sort(sc[h]["P"] if Ps is None else sc[h]["P"][Ps])
        dlt = prank(sc[h]["BB"], ref) - prank(sc[h]["rcam"][bpair], ref)
        hosts = BB["host"] if bsel is None else BB["host"][bsel]
        dlt = dlt if bsel is None else dlt[bsel]
        u, inv = np.unique(hosts, return_inverse=True)
        return float((np.bincount(inv, dlt) / np.bincount(inv)).mean())

    def storage_shift(h, cp):
        ref = np.sort(sc[h]["P"]); ci_, ni = spair[cp]
        dlt = prank(sc[h]["SB"][ci_], ref) - prank(sc[h]["SB"][ni], ref)
        u, inv = np.unique(SB["host"][ci_], return_inverse=True)
        return float((np.bincount(inv, dlt) / np.bincount(inv)).mean())

    k0 = int((sc["H0"]["rcam"] > 0).sum())
    s3t, s4t = Lt["kind"] == S3K, Lt["kind"] == S4K
    rec0 = float((sc["H0"]["Lt"][s4t] > 0).mean())
    LtB = ~hA(Lt)
    erased = {"H0e", "H0e4", "H0ec", "H0em", "H3", "H3c", "H4"} | set(nulls)
    heads = {}
    for h in names:
        r = {}
        r["border_shift"] = border_shift(h)
        for cp in ("fm61", "amsl112"):
            r[f"storage_shift_{cp}"] = storage_shift(h, cp)
        sCc = sc[h]["C"]; pos = Cc["kind"] == "landmark_combined_orig"
        r["auc_lcomb"] = auc(sCc[pos], sCc[~pos])
        if h not in nulls:
            for q in (0.99, 0.95):
                t = float(np.quantile(sc[h]["P"], q)); tag = f"p{int(round(q * 100))}"
                r[f"thr_{tag}"] = t
                r[f"border_flag_{tag}"] = float((sc[h]["BB"] > t).mean()); r[f"photo_flag_{tag}"] = float((sc[h]["rcam"][bpair] > t).mean())
                r[f"border_flag_by_mask_{tag}"] = {k.split(":")[1]: float((sc[h]["BB"][BB["kind"] == k] > t).mean()) for k in np.unique(BB["kind"])}
                for cp in ("fm61", "amsl112"):
                    ci_, ni = spair[cp]
                    r[f"df_{cp}_{tag}"] = float((sc[h]["SB"][ci_] > t).mean() - (sc[h]["SB"][ni] > t).mean())
                r[f"lcomb_recall_{tag}"] = float((sCc[pos] > t).mean())
            t_old = 0.0 if h == "H0" else thr_at_share(sc[h]["rcam"], k0)
            r["old_rule"] = dict(thr=t_old, border_flags=int((sc[h]["BB"] > t_old).sum()), border_n=len(bpair))
            # splices: test hosts of L only; heads with an eraser: half-B test hosts only (F7)
            m = LtB if h in erased else np.ones(len(LtB), bool)
            sL = sc[h]["Lt"]; rr = float((sc["H0"]["Lt"][s4t & m] > 0).mean()); tr = thr_at_recall(sL[s4t & m], rr)
            r["splice_hosts"] = "test, half B" if h in erased else "test"
            r["s3_matched"] = float((sL[s3t & m] > tr).mean()); r["s4_recall_matched"] = float((sL[s4t & m] > tr).mean())
            r["s3_vs_s4_auc"] = auc(sL[s4t & m], sL[s3t & m])
        heads[h] = r
    res["heads"] = {h: v for h, v in heads.items() if h not in nulls}
    res["nulls"] = {h: dict(border_shift=heads[h]["border_shift"], storage_shift_amsl112=heads[h]["storage_shift_amsl112"],
                            auc_lcomb=heads[h]["auc_lcomb"]) for h in nulls}
    rem = lambda a, ref: None if heads[ref]["border_shift"] <= FLOOR else float(1 - heads[a]["border_shift"] / heads[ref]["border_shift"])
    res["border_floor"] = heads["H0"]["border_shift"] <= FLOOR or heads["H1"]["border_shift"] <= FLOOR
    res["removal"] = dict(H3_vs_H1=rem("H3", "H1"), H0e_vs_H0=rem("H0e", "H0"), H3c_vs_H1=rem("H3c", "H1"), H0ec_vs_H0=rem("H0ec", "H0"),
                          H1_vs_H0=rem("H1", "H0"), null_vs_H1=[rem(h, "H1") for h in nulls])
    nv = [x for x in res["removal"]["null_vs_H1"] if x is not None]
    res["removal"]["null_max"] = max(nv) if nv else None
    res["storage_floor"] = heads["H0"]["storage_shift_amsl112"] <= SFLOOR
    res["morph_check"] = dict(auc_H0=heads["H0"]["auc_lcomb"], auc_H0em=heads["H0em"]["auc_lcomb"],
                              drop=heads["H0"]["auc_lcomb"] - heads["H0em"]["auc_lcomb"])
    res["morph_check"]["guard_sensitive"] = bool(res["morph_check"]["drop"] >= 0.05)
    res["s4_recall_H0_test"] = rec0; res["k0_rcam"] = k0
    # probes (printed)
    Xb = np.concatenate([BB["F"], rcam["F"][~hA(rcam)]]); yb = np.r_[np.ones(len(BB["y"])), np.zeros(int((~hA(rcam)).sum()))].astype(int)
    gb = np.concatenate([BB["host"], rcam["host"][~hA(rcam)]])
    ys = (SB["kind"] != "photo:").astype(int)
    res["probes"] = dict(border_before=probe_auc(Xb, yb, gb), border_after_H3=probe_auc(erase(Xb, d3), yb, gb),
                         storage_before=probe_auc(SB["F"], ys, SB["host"]), storage_after_H4=probe_auc(erase(SB["F"], d4), ys, SB["host"]))
    # ---- bootstrap (persons); reference ranks and thresholds recomputed in every draw
    rng = np.random.default_rng(20261128)
    up = np.unique(P["host"]); pidx = {h: np.flatnonzero(P["host"] == h) for h in up}
    bh = {h: np.flatnonzero(BB["host"] == h) for h in np.unique(BB["host"])}
    BH = ("H0", "H0e", "H1", "H3", "H3c")
    bs = {h: [] for h in BH}; bd = {"H3-H1": [], "H0e-H0": []}
    for _ in range(NBOOT):
        dr = rng.choice(up, len(up)); Ps = np.concatenate([pidx[h] for h in dr])
        bsel = np.concatenate([bh[h] for h in dr if h in bh])
        v = {h: border_shift(h, Ps, bsel) for h in BH}
        for h in BH:
            bs[h].append(v[h])
        bd["H3-H1"].append(v["H3"] - v["H1"]); bd["H0e-H0"].append(v["H0e"] - v["H0"])
    ci = dict(border_shift={h: qci(x) for h, x in bs.items()}, border_shift_diff={k: qci(x) for k, x in bd.items()})
    ut = np.unique(Lt["host"]); lth = {h: np.flatnonzero(Lt["host"] == h) for h in ut}
    SH = ("H0", "H1d", "H1dc", "H2d", "H1", "H1c", "H2")
    ss = {h: [] for h in SH}; sd = {h: [] for h in SH[1:]}
    for _ in range(NBOOT):
        p = np.concatenate([lth[h] for h in rng.choice(ut, len(ut))]); k3, k4 = s3t[p], s4t[p]
        rr = float((sc["H0"]["Lt"][p][k4] > 0).mean())
        v = {}
        for h in SH:
            sL = sc[h]["Lt"][p]; v[h] = float((sL[k3] > thr_at_recall(sL[k4], rr)).mean())
            ss[h].append(v[h])
        for h in SH[1:]:
            sd[h].append(v[h] - v["H0"])
    ci["s3_matched"] = {h: qci(x) for h, x in ss.items()}; ci["s3_matched_minus_H0"] = {h: qci(x) for h, x in sd.items()}
    uc = np.unique(Cc["host"]); chh = {h: np.flatnonzero(Cc["host"] == h) for h in uc}; pos = Cc["kind"] == "landmark_combined_orig"
    AH = ("H0", "H1", "H3", "H4", "H0em")
    aa = {h: [] for h in AH}; ad = {"H3-H1": [], "H4-H1": []}
    for _ in range(NBOOT):
        p = np.concatenate([chh[h] for h in rng.choice(uc, len(uc))]); q = pos[p]
        v = {h: auc(sc[h]["C"][p][q], sc[h]["C"][p][~q]) for h in AH}
        for h in AH:
            aa[h].append(v[h])
        ad["H3-H1"].append(v["H3"] - v["H1"]); ad["H4-H1"].append(v["H4"] - v["H1"])
    ci["auc"] = {h: qci(x) for h, x in aa.items()}; ci["auc_diff"] = {k: qci(x) for k, x in ad.items()}
    res["ci"] = ci
    return res


def table(per, avail):
    """prereg.md section 7: a row holds if its condition is met on >= 4 seeds."""
    if len(avail) < 4:
        return {k: "not available" for k in ("border", "splices", "splices_training_list", "storage")}
    out = {}
    insens = [n for n in avail if not per[n]["morph_check"]["guard_sensitive"]]
    glab = f"; AUC guard insensitive on {','.join(insens)} (erasure-works check)" if insens else ""
    nf = [n for n in avail if not per[n]["border_floor"]]
    if len(nf) < 4:
        out["border"] = f"floor (not testable): H0 or H1 border shift <= {FLOOR} on {len(avail) - len(nf)} of {len(avail)} seeds"
    else:
        def sep(n):
            r, H = per[n]["removal"], per[n]["heads"]
            return (r["H3_vs_H1"] >= 0.70 and r["H0e_vs_H0"] >= 0.50 and H["H3"]["auc_lcomb"] >= H["H1"]["auc_lcomb"] - 0.01
                    and r["null_max"] is not None and r["H3_vs_H1"] > r["null_max"])
        cf = lambda n: per[n]["removal"]["H3c_vs_H1"] < 0.70
        nr = lambda n: (per[n]["removal"]["H3_vs_H1"] < 0.50
                        or per[n]["heads"]["H3"]["auc_lcomb"] < per[n]["heads"]["H1"]["auc_lcomb"] - 0.02)
        a, c, s = sum(map(sep, nf)), sum(map(cf, nf)), sum(map(nr, nf))
        v = ("the border shift is a separable rank-1 direction (beyond refitting and the random-direction null)" if a >= 4
             else "rank-1 erasure cannot test this (ceiling eraser removes < 70%)" if c >= 4
             else "the border shift is not removable by a rank-1 linear eraser; gradient-reversal arms get no support from NE1" if s >= 4
             else "inconclusive (border)")
        out["border"] = v + f" [separable {a}, ceiling-fail {c}, not-removable {s} of {len(nf)} non-floor seeds]" + glab

    def srow(h2, h1c, nets):
        mv = sum(per[n]["heads"][h2]["s3_matched"] <= per[n]["heads"]["H0"]["s3_matched"] - 0.05 for n in nets)
        nw = sum(abs(per[n]["heads"][h2]["s3_matched"] - per[n]["heads"]["H0"]["s3_matched"]) <= 0.03
                 and abs(per[n]["heads"][h2]["s3_matched"] - per[n]["heads"][h1c]["s3_matched"]) <= 0.03 for n in nets)
        ct = sum(per[n]["heads"][h1c]["s3_matched"] <= per[n]["heads"]["H0"]["s3_matched"] - 0.05 for n in nets)
        v = ("reweighting can move the trade-off" if mv >= 4
             else "reweighting the last layer on held-out development features does not move the trade-off" if nw >= 4
             else "inconclusive (splices)")
        v += f" [moves {mv}, no-change {nw} of {len(nets)} seeds; {h1c} control moves on {ct}]"
        return v + ("; attributed to refitting (control)" if mv >= 4 and ct >= 4 else "")
    out["splices"] = srow("H2d", "H1dc", avail)  # binding (lead's answer 1)
    ins = sum(per[n]["T_in_sample"] for n in avail)
    out["splices_training_list"] = ("not testable on in-sample features" if ins >= 4 else srow("H2", "H1c", avail).replace(
        "on held-out development features", "on the training list")) + f" [printed only; T worst-group accuracy >= 0.98 for every C on {ins} seeds]"
    ns = [n for n in avail if not per[n]["storage_floor"]]
    if len(ns) < 4:
        out["storage"] = f"floor (not testable): H0 amsl112 storage shift <= {SFLOOR} on {len(avail) - len(ns)} of {len(avail)} seeds"
    else:
        st = sum(per[n]["heads"]["H4"]["storage_shift_amsl112"] <= per[n]["heads"]["H1"]["storage_shift_amsl112"] - 0.02
                 and per[n]["heads"]["H0e4"]["storage_shift_amsl112"] <= per[n]["heads"]["H0"]["storage_shift_amsl112"] - 0.02
                 and per[n]["heads"]["H4"]["auc_lcomb"] >= per[n]["heads"]["H1"]["auc_lcomb"] - 0.01 for n in ns)
        out["storage"] = ("residual storage reaction is a separable direction" if st >= 4 else "no separable storage direction shown") \
            + f" [{st} of {len(ns)} non-floor seeds]" + glab
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feats", required=True); ap.add_argument("--man", required=True); ap.add_argument("--nets", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--mock", action="store_true"); ap.add_argument("--only", default="")
    a = ap.parse_args()
    nets = [n for n in NETS if not a.only or n in a.only.split(",")]
    gate = {"passed": nets} if a.mock else json.load(open(pathlib.Path(a.feats) / "gate.json"))
    rng_null = np.random.default_rng(20261129)
    per, avail = {}, []
    for n in nets:
        ok = a.mock or all((pathlib.Path(a.feats) / f"{n}__ne1_{m}.npz").exists() for m in ("train", "gate", "read"))
        if not ok:
            print("not available", n); continue
        D, w, b = load(a.feats, a.man, a.nets, n, a.mock)
        per[n] = one_net(D, w, b, rng_null); per[n]["platform"] = "certified" if n in gate["passed"] else "platform not certified"
        avail.append(n); print("read", n, flush=True)
    out = dict(mock=a.mock, nets=per, available=avail, certified=[n for n in avail if per[n]["platform"] == "certified"],
               table=table(per, avail), labels=["C and S are FFHQ: cross-domain for every refitted head (T has no FFHQ)"],
               sklearn=__import__("sklearn").__version__, numpy=np.__version__)
    if len(out["certified"]) < len(avail):
        out["labels"].append("platform not certified on " + ",".join(n for n in avail if n not in out["certified"]))
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(out["table"], indent=1))


if __name__ == "__main__":
    main()
