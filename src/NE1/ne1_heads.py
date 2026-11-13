"""NE1 heads, erasers and reads (experiments/NE1_nuisance-erasure/prereg.md sections 4-7, 9). DGX CPU, run once.
In: --feats DIR with <net>__ne1_{gate,train,read}.npz (id, feat, logit) and gate.json; --man DIR with ne1_train.csv,
ne1_gate.csv, ne1_read.csv; --nets DIR (<net>/last_trainable.pt for H0's w, b). Out: --out JSON.
--mock: random features with the real manifests (code test only; nothing is read).
  python -I ne1_heads.py --feats F --man M --nets N --out ne1_read.json [--mock]"""
import argparse, csv, hashlib, json, os, pathlib, sys
import numpy as np
from scipy.stats import rankdata
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold

NETS = [f"PN1_Sb_s{s}" for s in (403, 404, 405, 406, 407)]
CGRID = (0.01, 0.1, 1.0, 10.0)
NBOOT = 2000
HEADS = ("H0", "H1", "H2", "H3", "H4")


def half_a(host):
    return int(hashlib.sha256(host.encode()).hexdigest()[0], 16) < 8


def auc(pos, neg):  # mid-rank AUC
    r = rankdata(np.concatenate([pos, neg]))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def logreg(X, y, C=1.0, sw=None, balanced=True):
    m = LogisticRegression(C=C, max_iter=5000, class_weight="balanced" if balanced else None)
    m.fit(X, y, sample_weight=sw)
    return m


def group_weights(kind):
    k = np.asarray(kind); u, inv, cnt = np.unique(k, return_inverse=True, return_counts=True)
    w = 1.0 / cnt[inv]  # equal total weight per kind (each kind holds one label, so class balance within a kind is trivial)
    return w * len(k) / w.sum()


def eraser(d):
    d = d / np.linalg.norm(d)
    return lambda X: X - np.outer(X @ d, d)


def thr_at_share(s_ref, k0):
    """smallest t with #(s_ref > t) <= k0 (flag rule s > t)."""
    s = np.sort(s_ref)[::-1]
    return float(s[k0]) if k0 < len(s) else -np.inf


def thr_at_recall(s_pos, rec):
    """largest t with share(s_pos > t) >= rec: the cut that keeps recall at least rec."""
    s = np.sort(s_pos)[::-1]; k = int(np.ceil(rec * len(s) - 1e-12))
    if k <= 0:
        return float(s[0])
    return float(np.nextafter(s[k - 1], -np.inf))


def boot_ci(hosts, fn, rng):
    u = np.unique(hosts); idx = {h: np.flatnonzero(hosts == h) for h in u}; v = []
    for _ in range(NBOOT):
        pick = np.concatenate([idx[h] for h in rng.choice(u, len(u))])
        v.append(fn(pick))
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    return [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))] if len(v) else [None, None]


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
                      set=np.array([r["set"] for r in rs]))
    return out, w, b


def sel(d, mask):
    return {k: v[mask] for k, v in d.items()}


def one_net(D, w, b):
    T, Gt, Rd = D["train"], D["gate"], D["read"]
    rcam = sel(Gt, Gt["kind"] == "R_cam")
    B = sel(Rd, Rd["set"] == "B"); L = sel(Rd, Rd["set"] == "L"); Cc = sel(Rd, Rd["set"] == "C"); S = sel(Rd, Rd["set"] == "S")
    hA = lambda d: np.array([half_a(h) for h in d["host"]])
    # erasers (fitted on half A only)
    bA, rA = B["F"][hA(B)], rcam["F"][hA(rcam)]
    e3 = eraser(bA.mean(0) - rA.mean(0))
    Sp = sel(S, np.char.startswith(S["kind"].astype(str), "photo:")); sA = hA(Sp)
    nat = Sp["kind"] == "photo:"; sto = np.isin(Sp["kind"], ["photo:fm61", "photo:amsl112"])
    e4 = eraser(Sp["F"][sA & sto].mean(0) - Sp["F"][sA & nat].mean(0))
    ident = lambda X: X
    # heads -> (transform, score fn)
    H = {"H0": (ident, lambda X: X @ w + b)}
    m1 = logreg(T["F"], T["y"]); H["H1"] = (ident, m1.decision_function)
    gw = group_weights(T["kind"]); cv = {}
    for C in CGRID:
        oof = np.zeros(len(T["y"]))
        for tr, te in GroupKFold(5).split(T["F"], T["y"], T["host"]):
            oof[te] = logreg(T["F"][tr], T["y"][tr], C, gw[tr], balanced=False).decision_function(T["F"][te])
        acc = {k: float(((oof[T["kind"] == k] > 0).astype(int) == T["y"][T["kind"] == k]).mean()) for k in np.unique(T["kind"])}
        cv[str(C)] = dict(worst=min(acc.values()), worst_kind=min(acc, key=acc.get))
    Cb = max(CGRID, key=lambda C: (cv[str(C)]["worst"], -C))  # tie: smaller C (stronger L2)
    m2 = logreg(T["F"], T["y"], Cb, gw, balanced=False); H["H2"] = (ident, m2.decision_function)
    m3 = logreg(e3(T["F"]), T["y"]); H["H3"] = (e3, m3.decision_function)
    m4 = logreg(e4(T["F"]), T["y"]); H["H4"] = (e4, m4.decision_function)
    sc = lambda h, d: H[h][1](H[h][0](d["F"]))
    # H0 sanity: recomputed logit equals the extracted one
    h0_lin = float(np.abs(sc("H0", rcam) - rcam["logit"]).max())
    k0 = int((sc("H0", rcam) > 0).sum())
    thr = {"H0": 0.0}
    for h in HEADS[1:]:
        thr[h] = thr_at_share(sc(h, rcam), k0)
    s3, s4 = L["kind"] == "splice:S3::opencv", L["kind"] == "splice:S4::opencv"
    rec0 = float((sc("H0", sel(L, s4)) > 0).mean())
    Bb = sel(B, ~hA(B)); Sb_ = sel(Sp, ~hA(Sp))
    res = dict(C_H2=Cb, cv_H2=cv, k0_rcam=k0, rcam_n=int(len(rcam["y"])), h0_linear_max=h0_lin, s4_recall_H0=rec0, heads={})
    for h in HEADS:
        t = thr[h]; r = dict(thr=t)
        r["rcam_share"] = float((sc(h, rcam) > t).mean())
        fb = sc(h, Bb) > t
        r["border_flags"] = int(fb.sum()); r["border_n"] = int(len(fb)); r["border_share"] = float(fb.mean())
        r["border_by_mask"] = {k.split(":")[1]: float(fb[Bb["kind"] == k].mean()) for k in np.unique(Bb["kind"])}
        sL = sc(h, L); tr = thr_at_recall(sL[s4], rec0)
        r["s4_recall_at_matched"] = float((sL[s4] > tr).mean()); r["s3_share_matched"] = float((sL[s3] > tr).mean())
        r["s3_share_own"] = float((sL[s3] > t).mean()); r["s4_recall_own"] = float((sL[s4] > t).mean())
        r["front"] = [[float(np.quantile(sL[s4], q)), float((sL[s4] > np.quantile(sL[s4], q)).mean()),
                       float((sL[s3] > np.quantile(sL[s4], q)).mean())] for q in (0.05, 0.1, 0.2, 0.3, 0.5)]
        sC = sc(h, Cc); r["auc_lcomb"] = auc(sC[Cc["kind"] == "landmark_combined_orig"], sC[Cc["kind"] == "landmark_combined_resmatch"])
        r["lcomb_recall_own"] = float((sC[Cc["kind"] == "landmark_combined_orig"] > t).mean())
        sS = sc(h, Sb_) > t; nh = Sb_["host"]
        for cp in ("fm61", "amsl112"):
            mc = Sb_["kind"] == f"photo:{cp}"; mn = (Sb_["kind"] == "photo:") & np.isin(nh, nh[mc])
            r[f"df_{cp}"] = float(sS[mc].mean() - sS[mn].mean())
        r["df_n_hosts"] = int(len(np.unique(nh[Sb_["kind"] == "photo:amsl112"])))
        res["heads"][h] = r
    f0 = res["heads"]["H0"]["border_flags"]
    for h in HEADS:
        res["heads"][h]["border_removal"] = None if f0 < 10 else float(1 - res["heads"][h]["border_flags"] / f0)
    res["border_floor"] = f0 < 10
    # probes (printed): border presence on half-B bordered copies + half-B R_cam photos; stored vs native on S photos
    Xb = np.concatenate([Bb["F"], rcam["F"][~hA(rcam)]]); yb = np.r_[np.ones(len(Bb["y"])), np.zeros(int((~hA(rcam)).sum()))]
    gb = np.concatenate([Bb["host"], rcam["host"][~hA(rcam)]])
    ms = (Sb_["kind"] != "photo:") ; Xs = Sb_["F"]; ys = ms.astype(int)
    res["probes"] = dict(border_before=probe_auc(Xb, yb, gb), border_after_H3=probe_auc(e3(Xb), yb, gb),
                         storage_before=probe_auc(Xs, ys, Sb_["host"]), storage_after_H4=probe_auc(e4(Xs), ys, Sb_["host"]))
    # bootstrap (persons): border share, S3 share at matched recall, AUC; per head and as difference to H0
    rng = np.random.default_rng(20261128); ci = {}
    sB = {h: sc(h, Bb) > thr[h] for h in HEADS}
    ci["border_share"] = {h: boot_ci(Bb["host"], lambda p, h=h: sB[h][p].mean(), rng) for h in HEADS}
    ci["border_share_minus_H0"] = {h: boot_ci(Bb["host"], lambda p, h=h: sB[h][p].mean() - sB["H0"][p].mean(), rng) for h in HEADS[1:]}
    Ls = sel(L, s3 | s4); s3s = Ls["kind"] == "splice:S3::opencv"
    trm = {h: thr_at_recall(sc(h, Ls)[~s3s], rec0) for h in HEADS}; f3 = {h: (sc(h, Ls) > trm[h]) for h in HEADS}
    ci["s3_matched"] = {h: boot_ci(Ls["host"], lambda p, h=h: f3[h][p][s3s[p]].mean(), rng) for h in HEADS}
    ci["s3_matched_minus_H0"] = {h: boot_ci(Ls["host"], lambda p, h=h: f3[h][p][s3s[p]].mean() - f3["H0"][p][s3s[p]].mean(), rng) for h in HEADS[1:]}
    pos = Cc["kind"] == "landmark_combined_orig"; sCc = {h: sc(h, Cc) for h in HEADS}

    def auc_p(p, h):
        q = pos[p]
        return auc(sCc[h][p][q], sCc[h][p][~q]) if q.any() and (~q).any() else np.nan
    ci["auc"] = {h: boot_ci(Cc["host"], lambda p, h=h: auc_p(p, h), rng) for h in HEADS}
    ci["auc_minus_H0"] = {h: boot_ci(Cc["host"], lambda p, h=h: auc_p(p, h) - auc_p(p, "H0"), rng) for h in HEADS[1:]}
    res["ci"] = ci
    return res


def table(per, avail):
    """prereg.md section 7: each row holds if its condition is met on >= 4 of 5 seeds."""
    def count(cond, nets):
        return sum(1 for n in nets if cond(per[n]["heads"]))
    out = {}
    nf = [n for n in avail if not per[n]["border_floor"]]
    if len(avail) < 4:
        return {k: "not available" for k in ("border", "splices", "storage")}
    if len(nf) < 4:
        out["border"] = f"floor (H0 has < 10 half-B border flags on {len(avail) - len(nf)} of {len(avail)} seeds)"
    else:
        sep = count(lambda H: H["H3"]["border_removal"] >= 0.70 and H["H3"]["auc_lcomb"] >= H["H0"]["auc_lcomb"] - 0.01, nf)
        sha = count(lambda H: H["H3"]["border_removal"] < 0.50 or H["H3"]["auc_lcomb"] < H["H0"]["auc_lcomb"] - 0.02, nf)
        ctl = count(lambda H: H["H1"]["border_removal"] >= 0.70 and H["H1"]["auc_lcomb"] >= H["H0"]["auc_lcomb"] - 0.01, nf)
        out["border"] = ("separable direction" if sep >= 4 else "border and detection share features" if sha >= 4
                         else "inconclusive (border)") + f" [separable {sep}, shared {sha} of {len(nf)} seeds; H1 control meets the separable row on {ctl}]"
        if sep >= 4 and ctl >= 4:
            out["border"] += "; attributed to refitting (H1 control)"
    mv = count(lambda H: H["H2"]["s3_share_matched"] <= H["H0"]["s3_share_matched"] - 0.05, avail)
    nw = count(lambda H: abs(H["H2"]["s3_share_matched"] - H["H0"]["s3_share_matched"]) <= 0.03
               and abs(H["H2"]["s3_share_matched"] - H["H1"]["s3_share_matched"]) <= 0.03, avail)
    ctl = count(lambda H: H["H1"]["s3_share_matched"] <= H["H0"]["s3_share_matched"] - 0.05, avail)
    out["splices"] = ("reweighting can move the trade-off" if mv >= 4 else "not a weighting problem" if nw >= 4
                      else "inconclusive (splices)") + f" [moves {mv}, no-change {nw} of {len(avail)} seeds; H1 control moves on {ctl}]"
    if mv >= 4 and ctl >= 4:
        out["splices"] += "; attributed to refitting (H1 control)"
    st = count(lambda H: H["H4"]["df_amsl112"] <= H["H0"]["df_amsl112"] - 0.02 and H["H4"]["auc_lcomb"] >= H["H0"]["auc_lcomb"] - 0.01, avail)
    ctl = count(lambda H: H["H1"]["df_amsl112"] <= H["H0"]["df_amsl112"] - 0.02 and H["H1"]["auc_lcomb"] >= H["H0"]["auc_lcomb"] - 0.01, avail)
    out["storage"] = ("residual storage reaction is a separable direction" if st >= 4 else "no separable storage direction shown") \
        + f" [{st} of {len(avail)} seeds; H1 control {ctl}]" + ("; attributed to refitting (H1 control)" if st >= 4 and ctl >= 4 else "")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feats", required=True); ap.add_argument("--man", required=True); ap.add_argument("--nets", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--mock", action="store_true"); ap.add_argument("--only", default="")
    a = ap.parse_args()
    nets = [n for n in NETS if not a.only or n in a.only.split(",")]
    gate = {"passed": nets} if a.mock else json.load(open(pathlib.Path(a.feats) / "gate.json"))
    per, avail = {}, []
    for n in nets:
        ok = a.mock or all((pathlib.Path(a.feats) / f"{n}__ne1_{m}.npz").exists() for m in ("train", "gate", "read"))
        if not ok:
            print("not available", n); continue
        D, w, b = load(a.feats, a.man, a.nets, n, a.mock)
        per[n] = one_net(D, w, b); per[n]["platform"] = "certified" if n in gate["passed"] else "platform not certified"
        avail.append(n); print("read", n, flush=True)
    out = dict(mock=a.mock, nets=per, available=avail, certified=[n for n in avail if per[n]["platform"] == "certified"],
               table=table(per, avail), sklearn=__import__("sklearn").__version__, numpy=np.__version__)
    if len(out["certified"]) < len(avail):
        out["table_label"] = "platform not certified on " + ",".join(n for n in avail if n not in out["certified"])
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(out["table"], indent=1))


if __name__ == "__main__":
    main()
