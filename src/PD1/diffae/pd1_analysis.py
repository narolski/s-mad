"""PD1 DiffAE family: Q1 to Q5 and the benchmark cells on cached frozen features (CPU only).

  pd1_analysis.py --first                 CLIP pooled, fold 0 only: Q1 and Q3 (first end-to-end pass)
  pd1_analysis.py --feats clip_pool,...   full analysis per feature set (all folds, Q1-Q5, external, benchmarks)
  pd1_analysis.py --smoke                 the full path on 8 blocks, B = 50 (command test)

Writes experiments/PD1_signal-isolation-paired-differences/diffae/{first_pass.json, results_<feat>.json} and
/mnt/t7/smad_next/PD1/diffae/heads/<feat>_<variant>_<head>.npz (final heads), oof_<feat>.npz.
Run: OMP_NUM_THREADS=2 nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/PD1/diffae/pd1_analysis.py ...
"""
import argparse, json, pathlib, sys, time
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pd1_common as K

RUNGS = ("x0", "x1", "x2", "x3")
CONTRASTS = (("x3", "x1"), ("x3", "x0"), ("x2", "x1"), ("x1", "x0"), ("x3", "x2"), ("x2", "x0"))
VARIANTS = ("none", "soft1", "soft5", "pipe", "soft1+pipe")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ============================================================== data
class Pool:
    def __init__(self, rows, feat, stats, B, max_blocks=0):
        self.byid = {r["id"]: r for r in rows}
        hosts = K.training_pool(rows)
        blocks = sorted({h["block"] for h in hosts})
        if max_blocks:
            keep = set(sorted(blocks, key=lambda b: K.hsh("PD1:" + b))[:max_blocks])
            hosts = [h for h in hosts if h["block"] in keep]
            blocks = sorted(keep)
        self.hosts, self.blocks = hosts, blocks
        self.fold = K.folds_of(blocks)
        self.ids = sorted({h[x] for h in hosts for x in RUNGS})
        self.ix = {i: k for k, i in enumerate(self.ids)}
        self.F = np.stack([feat[i] for i in self.ids])
        self.S = np.stack([stats[i] for i in self.ids]) if stats else None
        self.rung = np.array([self.byid[i]["rung"] for i in self.ids])
        self.iblock = np.array([self.byid[i]["block"] for i in self.ids])
        self.imfold = np.array([self.fold[b] for b in self.iblock])
        self.pp = [K.persons_of(self.byid[i]) for i in self.ids]
        self.H = {x: np.array([self.ix[h[x]] for h in hosts]) for x in RUNGS}
        self.hfold = np.array([self.fold[h["block"]] for h in hosts])
        self.hblock = np.array([h["block"] for h in hosts])
        self.hcohort = np.array([h["cohort"] for h in hosts])
        self.hpp1 = [(h["person"],) for h in hosts]
        self.hpp2 = [(h["person"], h["partner"]) for h in hosts]
        persons = sorted({p for pp in self.pp for p in pp})
        self.D = K.Draw(persons, B, K.SEED_TR)
        self.Wimg = self.D.w(self.pp)
        self.Wh1 = self.D.w(self.hpp1)
        self.Wh2 = self.D.w(self.hpp2)


def ext_matrix(rows, feat, sets):
    ids = [r["id"] for r in rows if r["set"] in sets and r["id"] in feat]
    return ids, (np.stack([feat[i] for i in ids]) if ids else np.zeros((0, 1)))


# ============================================================== metrics
def auc_ci(pos, neg, Wp, Wn):
    pt = K.auc(pos, neg)
    rep = K.wauc(np.asarray(pos, float), np.asarray(neg, float), Wp, Wn)
    return pt, rep


def contrast(pool, s, a, b, sel=None):
    """AUC of rung a against rung b on images with finite score s (optionally restricted by boolean sel)."""
    ok = np.isfinite(s) if sel is None else (np.isfinite(s) & sel)
    ia, ib = np.where(ok & (pool.rung == a))[0], np.where(ok & (pool.rung == b))[0]
    pt, rep = auc_ci(s[ia], s[ib], pool.Wimg[:, ia], pool.Wimg[:, ib])
    return pt, rep, len(ia), len(ib)


def paired_share(pool, s, a, b, hsel=None):
    """Weighted share of hosts with s(a of host) > s(b of host)."""
    ok = np.isfinite(s[pool.H[a]]) & np.isfinite(s[pool.H[b]])
    if hsel is not None:
        ok &= hsel
    h = np.where(ok)[0]
    v = (s[pool.H[a][h]] > s[pool.H[b][h]]).astype(float)
    W = (pool.Wh2 if "x3" in (a, b) else pool.Wh1)[:, h]
    return float(v.mean()), (W * v).sum(1) / np.maximum(W.sum(1), 1e-12), len(h)


def floor_for(pool, a, b, sel=None):
    """Best folded single-statistic AUC for rung a vs b, with its replicate vector (direction fixed at the point)."""
    ok = np.ones(len(pool.ids), bool) if sel is None else sel
    ia, ib = np.where(ok & (pool.rung == a))[0], np.where(ok & (pool.rung == b))[0]
    best, out = None, {}
    for j, nm in enumerate(STAT_NAMES):
        raw, rep = auc_ci(pool.S[ia, j], pool.S[ib, j], pool.Wimg[:, ia], pool.Wimg[:, ib])
        fl = raw < 0.5
        fa, frep = (1 - raw, 1 - rep) if fl else (raw, rep)
        out[nm] = dict(auc_folded=fa, ci=K.ci(frep), direction=f"{a} lower" if fl else f"{a} higher")
        if best is None or fa > best[1]:
            best = (nm, fa, frep)
    return best, out


# ============================================================== heads
def fit_head(pool, Fp, train_hosts, pos_rung, C=None, inner_k=3):
    """Paired head pos_rung vs x1 on the given training hosts. Standardisation over their x1 and pos images."""
    img = np.unique(np.r_[pool.H["x1"][train_hosts], pool.H[pos_rung][train_hosts]])
    mu, sd = Fp[img].mean(0), Fp[img].std(0) + 1e-8
    Z = (Fp - mu) / sd
    chosen = None
    if C is None:
        tb = sorted({pool.hblock[h] for h in train_hosts})
        inner = K.folds_of(tb, k=inner_k, salt="PD1inner:")
        hin = np.array([inner[pool.hblock[h]] for h in train_hosts])
        scores = []
        for c in K.CS:
            sh = []
            for j in range(inner_k):
                a, v = train_hosts[hin != j], train_hosts[hin == j]
                w = K.fit_pair_head(Z[pool.H[pos_rung][a]], Z[pool.H["x1"][a]], c)
                sh.append(float(((Z[pool.H[pos_rung][v]] - Z[pool.H["x1"][v]]) @ w > 0).mean()))
            scores.append(float(np.mean(sh)))
        k = int(np.argmax(np.array(scores) - 1e-9 * np.arange(len(scores))))   # ties to the smaller C
        C, chosen = K.CS[k], scores
    w = K.fit_pair_head(Z[pool.H[pos_rung][train_hosts]], Z[pool.H["x1"][train_hosts]], C)
    return dict(w=w, mu=mu, sd=sd, C=C, inner=chosen)


def score(head, F):
    return ((F - head["mu"]) / head["sd"]) @ head["w"]


# ============================================================== projections
def basis(vecs):
    q, _ = np.linalg.qr(np.stack(vecs, 1))
    return q


def soft_basis(smdd_fit_diffs, k):
    m = smdd_fit_diffs.mean(0)
    if k == 1:
        return basis([m / np.linalg.norm(m)])
    c = smdd_fit_diffs - m
    _, _, vt = np.linalg.svd(c, full_matrices=False)
    return basis([m / np.linalg.norm(m)] + [vt[i] for i in range(k - 1)])


def pipe_dir(pool, hosts_idx):
    d = (pool.F[pool.H["x1"][hosts_idx]] - pool.F[pool.H["x0"][hosts_idx]]).mean(0)
    return d / np.linalg.norm(d)


def projector(variant, pool, hosts_idx, U_soft1, U_soft5):
    if variant == "none":
        return None
    if variant == "soft1":
        return U_soft1
    if variant == "soft5":
        return U_soft5
    p = pipe_dir(pool, hosts_idx)
    if variant == "pipe":
        return basis([p])
    return basis([U_soft1[:, 0], p])


def project(F, U):
    return F if U is None else F - (F @ U) @ U.T


# ============================================================== Q1
def q1(pool, folds):
    res = {}
    for s, (a, b) in K.STEPS.items():
        t = np.full(len(pool.hosts), np.nan)
        proj = np.full(len(pool.ids), np.nan)
        for k in folds:
            tr, te = np.where(pool.hfold != k)[0], np.where(pool.hfold == k)[0]
            u = (pool.F[pool.H[b][tr]] - pool.F[pool.H[a][tr]]).mean(0)
            u /= np.linalg.norm(u)
            t[te] = (pool.F[pool.H[b][te]] - pool.F[pool.H[a][te]]) @ u
            im = pool.imfold == k
            proj[im] = pool.F[im] @ u
        h = np.where(np.isfinite(t))[0]
        v = (t[h] > 0).astype(float)
        W = (pool.Wh2 if s in ("I", "W", "G") else pool.Wh1)[:, h]
        rep = (W * v).sum(1) / np.maximum(W.sum(1), 1e-12)
        pt, arep, na, nb = contrast(pool, proj, b, a)
        share = float(v.mean())
        lo = K.ci(rep)[0]
        res[s] = dict(step=K.STEP_NAMES[s], hosts=int(len(h)), share=share, share_ci=K.ci(rep), proj_auc=pt, proj_auc_ci=K.ci(arep),
                      n_later=na, n_earlier=nb, reading="consistent direction" if (share >= 0.75 and lo > 0.65) else "not consistent")
    return res


# ============================================================== Q3 / Q4 per variant
def run_variant(pool, variant, folds, U_soft1, U_soft5, feat_all, rows, final=True, ext=True):
    """Out-of-fold H1 / H2 (+ statistics head for 'none'), metrics, floors; final heads and external scores."""
    out = {}
    oof = {}
    for head_name, pos in (("H1", "x2"), ("H2", "x3")):
        s = np.full(len(pool.ids), np.nan)
        Cs = {}
        for k in folds:
            tr = np.where(pool.hfold != k)[0]
            U = projector(variant, pool, tr, U_soft1, U_soft5)
            Fp = project(pool.F, U)
            hd = fit_head(pool, Fp, tr, pos)
            im = pool.imfold == k
            s[im] = score(hd, Fp[im])
            Cs[int(k)] = dict(C=hd["C"], inner=hd["inner"])
        oof[head_name] = s
        r = dict(C_by_fold=Cs, contrasts={}, paired={})
        for a, b in CONTRASTS:
            pt, rep, na, nb = contrast(pool, s, a, b)
            r["contrasts"][f"{a}_vs_{b}"] = dict(auc=pt, ci=K.ci(rep), n=[na, nb])
            if pool.S is not None:
                best, allst = floor_for(pool, a, b, sel=np.isfinite(s))
                ex = rep - best[2]
                r["contrasts"][f"{a}_vs_{b}"].update(floor_stat=best[0], floor_auc=best[1], floor_ci=K.ci(best[2]),
                                                     excess=pt - best[1], excess_ci=K.ci(ex))
                if (a, b) == ("x3", "x1"):
                    r["floor_all_stats_x3_vs_x1"] = allst
        for a, b in (("x3", "x1"), ("x2", "x1"), ("x1", "x0"), ("x3", "x0")):
            pt, rep, n = paired_share(pool, s, a, b)
            r["paired"][f"{a}_gt_{b}"] = dict(share=pt, ci=K.ci(rep), hosts=n)
        # per-fold AUC (descriptive)
        r["per_fold_x3_vs_x1"] = {int(k): K.auc(s[(pool.imfold == k) & (pool.rung == "x3")], s[(pool.imfold == k) & (pool.rung == "x1")]) for k in folds}
        out[head_name] = r
    # statistics head trained like H1 (descriptive), only unprojected
    if variant == "none" and pool.S is not None:
        sS = np.full(len(pool.ids), np.nan)
        LS = np.log1p(np.abs(pool.S)) * np.sign(pool.S)
        for k in folds:
            tr = np.where(pool.hfold != k)[0]
            hd = fit_head(pool, LS, tr, "x2")
            im = pool.imfold == k
            sS[im] = score(hd, LS[im])
        out["stat_head_H1recipe"] = {f"{a}_vs_{b}": dict(zip(("auc", "rep"), contrast(pool, sS, a, b)[:2])) for a, b in CONTRASTS}
        for kk, v in out["stat_head_H1recipe"].items():
            v["ci"] = K.ci(v.pop("rep"))
    if not final:
        return out, oof, None
    # final heads on all hosts, C by the 5-fold CV (pooled out-of-fold paired share)
    allh = np.arange(len(pool.hosts))
    U_fin = projector(variant, pool, allh, U_soft1, U_soft5)
    finals = {}
    for head_name, pos in (("H1", "x2"), ("H2", "x3")):
        cv = []
        for c in K.CS:
            sh = []
            for k in folds:
                tr, te = np.where(pool.hfold != k)[0], np.where(pool.hfold == k)[0]
                Fp = project(pool.F, projector(variant, pool, tr, U_soft1, U_soft5))
                hd = fit_head(pool, Fp, tr, pos, C=c)
                sh.append(((score(hd, Fp[pool.H[pos][te]]) - score(hd, Fp[pool.H["x1"][te]])) > 0).astype(float))
            cv.append(float(np.concatenate(sh).mean()))
        kbest = int(np.argmax(np.array(cv) - 1e-9 * np.arange(len(cv))))
        hd = fit_head(pool, project(pool.F, U_fin), allh, pos, C=K.CS[kbest])
        hd["cv_share_by_C"] = cv
        finals[head_name] = hd
        np.savez(K.BIG / "heads" / f"{FEAT}_{variant}_{head_name}.npz", w=hd["w"], mu=hd["mu"], sd=hd["sd"], C=hd["C"],
                 U=(U_fin if U_fin is not None else np.zeros((0,))))
        out[head_name]["final_C"] = hd["C"]
        out[head_name]["final_cv_share_by_C"] = cv
    if ext:
        ids, FX = ext_matrix(rows, feat_all, ("f256", "fr512", "ev", "smdd", "ad1b"))
        FXp = project(FX, U_fin)
        out["external"] = {h: external(rows, ids, score(finals[h], FXp)) for h in finals}
    return out, oof, finals


# ============================================================== external scoring (FRLL, SMDD, benchmarks)
def name_of(r):
    return pathlib.PurePath(r["path"]).stem


def external(rows, ids, s):
    byid = {r["id"]: r for r in rows}
    sc = dict(zip(ids, s))
    R = [byid[i] for i in ids]
    allp = K.frll_persons()          # the 102 FRLL persons (AD1's draw: sorted person set, seed [20261107, 43, 1])
    D = K.Draw(allp, NB_FRLL, K.SEED_FRLL)
    grp = {}
    for r in R:
        grp.setdefault((r["set"], r["arm"]), []).append(r)

    def a_vs(sa, aa, sb, ab, note="", expr=None):
        A = [r for r in grp.get((sa, aa), []) if expr is None or r["expr"] == expr]
        Bn = [r for r in grp.get((sb, ab), []) if expr is None or r["expr"] == expr]
        if not A or not Bn:
            return dict(n=[len(A), len(Bn)], note="not available")
        pa = np.array([sc[r["id"]] for r in A])
        pb = np.array([sc[r["id"]] for r in Bn])
        Wa, Wb = D.w([K.persons_of(r) for r in A]), D.w([K.persons_of(r) for r in Bn])
        pt, rep = auc_ci(pa, pb, Wa, Wb)
        return dict(auc=pt, ci=K.ci(rep), n=[len(A), len(Bn)], note=note)

    res = {"frll256": {}, "frll_stored": {}, "mirror": {}, "flag": {}, "bench": {}}
    c = "neutral+smiling mix: confounded, no conclusion"
    for pa, pb, note in (("B20", "D20", ""), ("B20", "a256", ""), ("D20", "a256", ""), ("C20", "D20", c), ("B100", "rec100", ""),
                         ("self100", "rec100", c), ("rec100", "a256", ""), ("B20", "C20", c)):
        res["frll256"][f"{pa}_vs_{pb}"] = a_vs("f256", pa, "f256", pb, note)
    res["frll256"]["B20_vs_D20_neutral_pairs"] = a_vs("f256", "B20", "f256", "D20", "neutral photos only", expr="03")
    # host-paired share at 256: B20 morph vs its first contributor's reconstruction D20
    d20 = {name_of(r): sc[r["id"]] for r in grp.get(("f256", "D20"), [])}
    b20 = [(sc[r["id"]], d20.get(name_of(r).split("_and_")[0][6:])) for r in grp.get(("f256", "B20"), [])]
    b20 = [(x, y) for x, y in b20 if y is not None]
    if b20:
        res["frll256"]["B20_gt_hostD20_share"] = dict(share=float(np.mean([x > y for x, y in b20])), n=len(b20))
    pub = "published MorDIFF step count not verified"
    for pa, pb, note in (("B20", "D20", ""), ("B", "D", ""), ("C20", "D20", c), ("C", "D", c), ("E", "R0", "photo stored small vs native"),
                         ("D20", "R0", ""), ("D", "R0", ""), ("A", "D", pub), ("A", "R0", pub), ("B20", "R0", ""), ("A", "B", "bridge, " + pub)):
        res["frll_stored"][f"{pa}_vs_{pb}"] = a_vs("fr512", pa, "fr512", pb, note)
    res["mirror"]["PAF_vs_D20r"] = a_vs("ad1b", "PAF", "ad1b", "D20r", "AD1b mirror mixes (n small if smoke only)")
    if ("ad1b", "PAF") in grp:
        pr = {name_of(r): sc[r["id"]] for r in grp[("ad1b", "D20r")]}
        v = [sc[r["id"]] > pr[name_of(r)] for r in grp[("ad1b", "PAF")] if name_of(r) in pr]
        res["mirror"]["PAF_gt_D20r_share"] = dict(share=float(np.mean(v)), n=len(v), source=grp[("ad1b", "PAF")][0]["split"])

    # flag rates on softened genuine photos
    def flag(native, soft, key, paired_names=True):
        s0 = np.array([sc[r["id"]] for r in native])
        s1 = np.array([sc[r["id"]] for r in soft])
        n0 = len(s0)
        kf = int(np.floor(0.05 * n0))
        t = float(np.sort(s0)[::-1][kf - 1])
        f0, f1 = s0 >= t, s1 >= t
        k1 = int(f1.sum())
        res["flag"][key] = dict(n_native=n0, n_soft=len(s1), threshold=t, flag_native=float(f0.mean()), flag_soft=float(f1.mean()),
                                flag_soft_ci=K.clopper(k1, len(s1)), shift_sd=float((s1.mean() - s0.mean()) / max(s0.std(), 1e-12)))
    if ("ev", "mordiff_bona|orig") in grp and ("ev", "mordiff|resmatch") in grp:
        flag(grp[("ev", "mordiff_bona|orig")], grp[("ev", "mordiff|resmatch")], "FRLL_E7_vs_native (primary)")
    if ("fr512", "R0") in grp and ("fr512", "E") in grp:
        flag(grp[("fr512", "R0")], grp[("fr512", "E")], "FRLL_stored_small_vs_native")
    if ("smdd", "orig") in grp:
        o = [r for r in grp[("smdd", "orig")] if r["split"] == "test"]
        e = [r for r in grp[("smdd", "e7")] if r["split"] == "test"]
        flag(o, e, "SMDD_test_shrunk_vs_original")
    # benchmark cells
    for fam in ("mordiff", "dim_a", "dim_c", "fast_dim", "fast_dim_ode", "greedy_dim", "greedy_dim_s"):
        M = grp.get(("ev", f"{fam}|orig"))
        if not M:
            continue
        nat = grp[("ev", "mordiff_bona|orig" if fam == "mordiff" else "dim_bona|orig")]
        e7 = grp[("ev", f"{fam}|resmatch")]
        pm = np.array([sc[r["id"]] for r in M])
        Wm = D.w([K.persons_of(r) for r in M])
        cell = {"n_morphs": len(M)}
        for gname, G in (("native", nat), ("E7", e7), ("native_neutral_only", [r for r in nat if r["expr"] == "03"])):
            pg = np.array([sc[r["id"]] for r in G])
            Wg = D.w([K.persons_of(r) for r in G])
            pt, rep = auc_ci(pm, pg, Wm, Wg)
            e = K.weer(pm, pg, np.ones((1, len(pm))), np.ones((1, len(pg))))[0]
            erep = K.weer(pm, pg, Wm, Wg)
            cell[gname] = dict(auc=pt, auc_ci=K.ci(rep), eer=float(e), eer_ci=K.ci(erep), n_genuine=len(G))
        s0 = np.array([sc[r["id"]] for r in nat])
        t = float(np.sort(s0)[::-1][int(np.floor(0.05 * len(s0))) - 1])
        s1 = np.array([sc[r["id"]] for r in e7])
        cell["E7_flag_at_native5pct"] = dict(rate=float((s1 >= t).mean()), ci=K.clopper(int((s1 >= t).sum()), len(s1)),
                                             morphs_flagged=float((pm >= t).mean()))
        res["bench"][fam] = cell
    return res


# ============================================================== Q2
def q2(pool, smdd_d, frll_dirs, R_point=200, B=1000, seed=20261111):
    rng = np.random.default_rng(seed)
    blocks = np.array(pool.blocks)
    bpos = {b: i for i, b in enumerate(blocks)}
    hb = np.array([bpos[b] for b in pool.hblock])
    # per-block summed host differences for each step
    Dsum = {}
    for s, (a, b) in K.STEPS.items():
        d = pool.F[pool.H[b]] - pool.F[pool.H[a]]
        M = np.zeros((len(blocks), d.shape[1]))
        np.add.at(M, hb, d)
        Dsum[s] = M
    names = list(K.STEPS) + ["S"]

    def dirs(cb, cs):
        out = {s: cb @ Dsum[s] for s in K.STEPS}
        out["S"] = cs @ smdd_d
        return {k: v / max(np.linalg.norm(v), 1e-12) for k, v in out.items()}

    def cosmat(c1b, c1s, c2b, c2s):
        u1, u2 = dirs(c1b, c1s), dirs(c2b, c2s)
        Mx = np.zeros((len(names), len(names)))
        for i, s in enumerate(names):
            for j, t in enumerate(names):
                Mx[i, j] = 0.5 * (u1[s] @ u2[t] + u2[s] @ u1[t]) if i != j else u1[s] @ u2[s]
        return Mx

    nb, ns = len(blocks), len(smdd_d)

    def halves(n):
        p = rng.permutation(n)
        h1 = np.zeros(n)
        h1[p[: n // 2]] = 1
        return h1, 1 - h1

    pts = []
    for _ in range(R_point):
        b1, b2 = halves(nb)
        s1, s2 = halves(ns)
        pts.append(cosmat(b1, s1, b2, s2))
    point = np.mean(pts, 0)
    reps = []
    for _ in range(B):
        b1, b2 = halves(nb)
        s1, s2 = halves(ns)
        cb1 = rng.multinomial(int(b1.sum()), b1 / b1.sum()).astype(float)
        cb2 = rng.multinomial(int(b2.sum()), b2 / b2.sum()).astype(float)
        cs1 = rng.multinomial(int(s1.sum()), s1 / s1.sum()).astype(float)
        cs2 = rng.multinomial(int(s2.sum()), s2 / s2.sum()).astype(float)
        reps.append(cosmat(cb1, cs1, cb2, cs2))
    reps = np.array(reps)
    rel = np.clip(np.diag(point), 1e-6, None)
    dis = point / np.sqrt(np.outer(rel, rel))
    res = dict(names=names, labels=[K.STEP_NAMES[n] for n in names], cos=point.tolist(),
               lo=np.percentile(reps, 2.5, 0).tolist(), hi=np.percentile(reps, 97.5, 0).tolist(), disattenuated=dis.tolist())
    i = {n: k for k, n in enumerate(names)}
    res["readings"] = {
        "M_W": dict(cos=point[i["M"], i["W"]], reading="the direction learned from same-person mixes is the direction of real morphs"
                    if point[i["M"], i["W"]] >= 0.5 else "not aligned"),
        "M_S": dict(cos=point[i["M"], i["S"]], reading="the mixing signal is softness" if point[i["M"], i["S"]] > 0.5 else "not softness (cos <= 0.5)"),
        "M_P": dict(cos=point[i["M"], i["P"]], reading="the mixing direction is largely the pipeline trace" if point[i["M"], i["P"]] > 0.5
                    else "not the pipeline trace (cos <= 0.5)")}
    # FRLL diagnostic directions (full data on both sides; independent samples): cos with full-pool training directions
    full = dirs(np.ones(nb), np.ones(ns))
    res["frll_diagnostic"] = {}
    for k, (d, note) in frll_dirs.items():
        u = d.mean(0)
        u /= np.linalg.norm(u)
        # split-half reliability of the FRLL direction
        rr = []
        for _ in range(200):
            h1, h2 = halves(len(d))
            a1, a2 = (h1 @ d), (h2 @ d)
            rr.append(a1 @ a2 / np.linalg.norm(a1) / np.linalg.norm(a2))
        res["frll_diagnostic"][k] = dict(n=len(d), note=note, split_half_reliability=float(np.mean(rr)),
                                         cos_with=dict({n: float(u @ full[n]) for n in names}))
    return res


# ============================================================== Q5
def q5(pool, oof_H1, fr, zsem):
    """Spearman rho of contributor dissimilarity with the morph's H1 score and with its paired step."""
    from scipy.stats import spearmanr
    rng = np.random.default_rng(20261111)
    x3 = np.where(pool.rung == "x3")[0]
    rows = []
    for i in x3:
        mid = pool.ids[i]
        hs = np.where(pool.H["x3"] == i)[0]
        step = float(np.mean([oof_H1[i] - oof_H1[pool.H["x1"][h]] for h in hs]))
        x0s = [pool.ids[pool.H["x0"][h]] for h in hs]
        e = [fr.get(x) for x in x0s]
        cos = float(e[0] @ e[1]) if all(v is not None for v in e) else np.nan
        z = [zsem.get(x) for x in x0s]
        zd = float(np.linalg.norm(z[0] - z[1])) if all(v is not None for v in z) else np.nan
        rows.append((mid, pool.iblock[i], oof_H1[i], step, 1 - cos, zd))
    blocks = sorted({r[1] for r in rows})
    bpos = {b: k for k, b in enumerate(blocks)}
    res = {}
    for key, col in (("fr_dissimilarity", 4), ("zsem_distance", 5)):
        v = np.array([[r[2], r[3], r[col]] for r in rows], float)
        okr = np.isfinite(v).all(1)
        v = v[okr]
        bi = np.array([bpos[r[1]] for r, o in zip(rows, okr) if o])
        out = dict(n=int(len(v)))
        for nm, j in (("score", 0), ("paired_step", 1)):
            rho = float(spearmanr(v[:, 2], v[:, j]).correlation)
            reps = []
            for _ in range(NB_Q5):
                bb = rng.integers(0, len(blocks), len(blocks))
                idx = np.concatenate([np.where(bi == b)[0] for b in bb])
                reps.append(spearmanr(v[idx, 2], v[idx, j]).correlation)
            lo, hi = K.ci(np.array(reps))
            out[nm] = dict(rho=rho, ci=[lo, hi], reading="the score rises with dissimilarity" if (rho > 0 and lo > 0) else "no rise detected")
        res[key] = out
    return res


# ============================================================== main
STAT_NAMES = ("hf_energy", "laplacian_var", "mirror_mad", "std_R", "std_G", "std_B", "png_bytes")
FEAT = "clip_pool"
NB_FRLL = 10000
NB_Q5 = 10000


def main():
    global FEAT, NB_FRLL, NB_Q5
    ap = argparse.ArgumentParser()
    ap.add_argument("--first", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--feats", default="clip_pool")
    ap.add_argument("--variants", default=",".join(VARIANTS))
    ap.add_argument("--B", type=int, default=10000)
    a = ap.parse_args()
    rows = K.items()
    stats, _ = K.load_stats(("tr",))
    (K.BIG / "heads").mkdir(parents=True, exist_ok=True)
    if a.first:
        FEAT = "clip_pool"
        feat = K.load_feats(FEAT, ("tr",))
        pool = Pool(rows, feat, stats, a.B)
        log("pool", len(pool.hosts), "hosts", len(pool.blocks), "blocks; fold 0 held out:", int((pool.hfold == 0).sum()), "hosts")
        r1 = q1(pool, [0])
        log("Q1 done")
        r3, oof, _ = run_variant(pool, "none", [0], None, None, None, rows, final=False, ext=False)
        log("Q3 done")
        K.dump(dict(feature=FEAT, folds=[0], hosts_heldout=int((pool.hfold == 0).sum()), B=a.B, Q1=r1, Q3=r3), "first_pass.json")
        return
    if a.smoke:
        NB_FRLL, NB_Q5 = 50, 50
    for FEAT in a.feats.split(","):
        t0 = time.time()
        feat = K.load_feats(FEAT, ("tr", "f256", "fr512", "ev", "smdd", "ad1b"))
        pool = Pool(rows, feat, stats, 50 if a.smoke else a.B, max_blocks=10 if a.smoke else 0)
        folds = list(range(5))
        sm = [r for r in rows if r["set"] == "smdd" and r["arm"] == "orig" and r["split"] == "fit" and r["id"] in feat]
        smdd_d = np.stack([feat[r["id"].replace("|orig|", "|e7|")] - feat[r["id"]] for r in sm])
        U1, U5 = soft_basis(smdd_d, 1), soft_basis(smdd_d, 5)
        log(FEAT, "pool", len(pool.hosts), "hosts; SMDD-fit pairs", len(smdd_d))
        res = dict(feature=FEAT, hosts=len(pool.hosts), blocks=len(pool.blocks), persons=len(pool.D.per), smdd_fit=len(smdd_d), B=pool.D.C.shape[0])
        res["Q1"] = q1(pool, folds)
        log("Q1 done")
        # FRLL diagnostic directions (Q1 shares with the full-pool direction, Q2 cosines)
        byid = {r["id"]: r for r in rows}
        grp = {}
        for r in rows:
            if r["id"] in feat:
                grp.setdefault((r["set"], r["arm"]), {})[pathlib.PurePath(r["path"]).stem] = r["id"]

        def pairdiff(ka, kb, keymap=lambda n: n):
            A, Bm = grp.get(ka, {}), grp.get(kb, {})
            pairs = [(Bm[n], A[keymap(n)]) for n in Bm if keymap(n) in A]
            return np.stack([feat[b] - feat[a] for b, a in pairs]) if pairs else np.zeros((0, pool.F.shape[1]))
        host_of = lambda n: n.split("_and_")[0][6:]  # noqa: E731
        frll_dirs = {
            "FRLL pipeline a256->D20 (256)": (pairdiff(("f256", "a256"), ("f256", "D20")), "diagnostic, FRLL"),
            "FRLL whole morph D20->B20 (256)": (pairdiff(("f256", "D20"), ("f256", "B20"), host_of), "diagnostic, FRLL"),
            "FRLL same-person mix D20->C20 (256)": (pairdiff(("f256", "D20"), ("f256", "C20"), lambda n: n[:3] + "_03"), "confounded, no conclusion"),
            "FRLL softening R0->E7 (frames)": (pairdiff(("ev", "mordiff_bona|orig"), ("ev", "mordiff|resmatch"),
                                                        lambda n: n.replace("_resmatch_mordiff", "_orig")), "diagnostic, FRLL"),
            "FRLL stored small R0->E (frames)": (pairdiff(("fr512", "R0"), ("fr512", "E"), lambda n: n + "_orig"), "diagnostic, FRLL"),
            "FRLL mirror mix D20r->PAF (256)": (pairdiff(("ad1b", "D20r"), ("ad1b", "PAF")), "diagnostic, FRLL, AD1b"),
        }
        frll_dirs = {k: v for k, v in frll_dirs.items() if len(v[0]) >= 4}
        # Q1 FRLL shares with full-pool training directions
        res["Q1_frll"] = {}
        for k, (d, note) in frll_dirs.items():
            stepkey = "P" if "pipeline" in k else "W" if "whole" in k else "M" if ("mix" in k) else None
            if stepkey is None:
                continue
            a_, b_ = K.STEPS[stepkey]
            u = (pool.F[pool.H[b_]] - pool.F[pool.H[a_]]).mean(0)
            u /= np.linalg.norm(u)
            res["Q1_frll"][k] = dict(n=len(d), share=float(((d @ u) > 0).mean()), training_step=stepkey, note=note)
        res["Q2"] = q2(pool, smdd_d, frll_dirs, R_point=20 if a.smoke else 200, B=20 if a.smoke else 1000)
        log("Q2 done")
        res["Q3Q4"] = {}
        oofs = {}
        for v in a.variants.split(","):
            r, oof, _ = run_variant(pool, v, folds, U1, U5, feat, rows, final=True, ext=True)
            res["Q3Q4"][v] = r
            oofs[v] = oof
            log("variant", v, "done; H1 x3_vs_x1", round(r["H1"]["contrasts"]["x3_vs_x1"]["auc"], 3))
        np.savez(K.BIG / f"oof_{FEAT}.npz", ids=np.array(pool.ids), **{f"{v}_{h}": oofs[v][h] for v in oofs for h in oofs[v]})
        # cohort transfer (expanded123 -> confirmation), descriptive, unprojected
        e = np.where(pool.hcohort == "e123")[0]
        c = np.where(pool.hcohort == "c64")[0]
        res["cohort_transfer"] = {}
        if len(c) and len(e):
            for hn, pos in (("H1", "x2"), ("H2", "x3")):
                hd = fit_head(pool, pool.F, e, pos)
                s = score(hd, pool.F)
                csel = np.isin(pool.iblock, pool.hblock[c])
                res["cohort_transfer"][hn] = {f"{x}_vs_{y}": dict(zip(("auc", "rep", "na", "nb"), contrast(pool, s, x, y, sel=csel)))
                                              for x, y in (("x3", "x1"), ("x2", "x1"), ("x1", "x0"))}
                for kk, vv in res["cohort_transfer"][hn].items():
                    vv["ci"] = K.ci(vv.pop("rep"))
        # Q5 contributor dissimilarity
        frp = K.BIG / "fr/tr_glint.npz"
        if frp.exists() and "none" in oofs:
            z = np.load(frp, allow_pickle=False)
            fr = {i: e_ for i, e_, f_ in zip(z["id"].tolist(), z["emb"], z["found"]) if f_}
            zs = {}
            for h in pool.hosts:
                r_ = byid[h["x0"]]
                p_ = pathlib.Path(r_["path"])
                lat = None
                for base in (p_.parent, pathlib.Path(str(p_.parent).replace("confirmation64-alignment-v1", "confirmation64-diffae-v1"))):
                    q = base / p_.name.replace("-aligned.png", "-latent.npz")
                    if q.exists():
                        lat = np.load(q, allow_pickle=False)["condition"].astype(np.float64)
                        break
                if lat is not None:
                    zs[h["x0"]] = lat
            res["Q5"] = q5(pool, oofs["none"]["H1"], fr, zs)
            log("Q5 done")
        res["seconds"] = time.time() - t0
        K.dump(res, f"results_{FEAT}{'_smoke' if a.smoke else ''}.json")
        log(FEAT, "written", round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
