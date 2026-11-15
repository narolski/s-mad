"""Signal isolation by paired differences (PD1), GAN family: Q1 to Q5 and the benchmark cells, one feature per run.

  pd1_analysis.py --feat clip:pool|clip:patch|dinov3:pool|dinov3:patch [--B 10000]
Writes experiments/PD1_signal-isolation-paired-differences/gan/res_<backbone>_<kind>.json.
Definitions: prereg.md of this folder. Run: OMP_NUM_THREADS=2 nice -n 10 <spark python> -I src/PD1/gan/pd1_analysis.py ...
"""
import argparse, json, pathlib, sys, time
import numpy as np
from scipy.stats import beta, spearmanr
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pd1_lib as L

SEED_G, SEED_H, SEED_FR, SEED_S = [20261111, 71, 1], [20261111, 72, 1], [20261111, 73, 1], [20261111, 74, 1]
G_STEPS = {"pipeline x0->x1": ("x0", "x1"), "same-person mixing x1->x2": ("x1", "x2"),
           "second identity x2->x3": ("x2", "x3"), "whole morph x1->x3": ("x1", "x3"), "camera to morph x0->x3": ("x0", "x3")}
H_STEPS = {"H whole morph x1->x3": ("x1", "x3"), "H latent spread x1->x1s": ("x1", "x1s"),
           "H morph beyond spread x1s->x3": ("x1s", "x3")}
G_CONTRASTS = (("x3", "x1"), ("x3", "x0"), ("x3", "x2"), ("x2", "x1"), ("x1", "x0"))
H_CONTRASTS = (("x3", "x1"), ("x3", "x1s"), ("x1s", "x1"))


def cp(k, n):
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return [lo, hi]


class Ctx:
    def __init__(self, backbone, kind, B):
        t0 = time.time()
        self.B = B
        self.F = L.load_feats(backbone, kind, ["G", "Hr", "Ha", "S", "Fm", "Fe", "Bm", "Be"])
        self.items = {r["id"]: r for r in L.items()}
        H = L.hosts()
        self.HG = [h for h in H if h["set"] == "G" and h["x0"] in self.F]
        self.HHr = [h for h in H if h["set"] == "Hr" and h["x1"] in self.F]
        self.HHa = [h for h in H if h["set"] == "Ha" and h["x1"] in self.F]
        self.HS = [h for h in H if h["set"] == "S" and h["s0"] in self.F]
        z = np.load(L.BIG / "stats.npz", allow_pickle=False) if (L.BIG / "stats.npz").exists() else None
        self.stat_names = list(z["names"]) if z is not None else []
        self.S = dict(zip(z["id"].tolist(), z["S"])) if z is not None else {}
        lz = np.load(L.BIG / "latents.npz", allow_pickle=False)
        lat = dict(zip(lz["key"].tolist(), lz["w"].astype(np.float64)))
        tz = np.load(L.BIG / "templates.npz", allow_pickle=False)
        self.tmpl = dict(zip(tz["key"].tolist(), tz["t"].astype(np.float64)))
        self.lat = lat
        # latent distance to the set mean code (latent averageness); x0 photos have none
        mG = np.mean([v for k, v in lat.items() if k.startswith("G|")], 0)
        mH = np.mean([v for k, v in lat.items() if k.startswith("H|") and k.endswith("|x1")], 0)
        self.dmean = {}
        for i, r in self.items.items():
            if r["set"] == "G" and r["role"] != "x0":
                w = np.mean([lat[f"G|{n}"] for n in r["src"].split(";")], 0)
                self.dmean[i] = float(np.linalg.norm(w - mG))
            elif r["set"] in ("Hr", "Ha"):
                self.dmean[i] = float(np.linalg.norm(lat[f"H|{r['pair']}|{r['role']}"] - mH))
        self.foG = L.folds([h["cluster"] for h in self.HG], 5, 401)
        self.foH = L.folds([h["cluster"] for h in self.HHr], 5, 401)
        self.foS = L.folds([h["cluster"] for h in self.HS], 5, 401)
        self.DG = L.Draw([h["cluster"] for h in self.HG], B, SEED_G)
        self.DH = L.Draw([h["cluster"] for h in self.HHr], B, SEED_H)
        self.DS = L.Draw([h["cluster"] for h in self.HS], min(B, 2000), SEED_S)
        frp = sorted({self.items[i]["photo"][:3] for i in self.F if i.startswith(("Fe|", "Fm|"))})
        self.DFR = L.Draw(frp, min(B, 2000), SEED_FR)
        print(f"context {backbone}:{kind}: {len(self.F)} vectors, G hosts {len(self.HG)}, H {len(self.HHr)}, S {len(self.HS)}"
              f" ({time.time() - t0:.0f}s)", flush=True)


# ---------------- Q1 ----------------
def q1_set(F, Hs, steps, fo, D):
    out = {}
    for nm, (a, b) in steps.items():
        p, hcl, simg = [], [], {}
        for k in range(5):
            tr = [h for h in Hs if fo[h["cluster"]] != k]
            te = [h for h in Hs if fo[h["cluster"]] == k]
            if not te:
                continue
            u = L.unit(np.mean([F[h[b]] - F[h[a]] for h in tr], 0))
            for h in te:
                p.append((F[h[b]] - F[h[a]]) @ u)
                hcl.append(h["cluster"])
                for r in (a, b):
                    simg[(r, h[r])] = (F[h[r]] @ u, h["cluster"])
        p = np.array(p)
        wh = D.w(hcl)
        shb = (wh * (p > 0)).sum(1) / wh.sum(1)
        A = [(v, c) for (r, i), (v, c) in simg.items() if r == b]
        Bn = [(v, c) for (r, i), (v, c) in simg.items() if r == a]
        sa, sb = np.array([v for v, _ in A]), np.array([v for v, _ in Bn])
        ab = L.wauc(sa, sb, D.w([c for _, c in A]), D.w([c for _, c in Bn]))
        share = float(np.mean(p > 0))
        out[nm] = dict(n_hosts=len(p), share=share, share_ci=L.ci(shb), proj_auc=L.auc(sa, sb), proj_auc_ci=L.ci(ab),
                       consistent=bool(share >= 0.75 and L.ci(shb)[0] > 0.65))
    return out


def q1(c):
    r = q1_set(c.F, c.HG, G_STEPS, c.foG, c.DG)
    r.update(q1_set(c.F, c.HHr, H_STEPS, c.foH, c.DH))
    r.update({k.replace("H ", "H aligned frame "): v for k, v in q1_set(c.F, c.HHa, H_STEPS, c.foH, c.DH).items()})
    r.update(q1_set(c.F, c.HS, {"softening SMDD render->E7 copy": ("s0", "s1")}, c.foS, c.DS))
    return r


# ---------------- Q2 ----------------
def dirs_weighted(F, Hs, a, b, w=None):
    d = np.array([F[h[b]] - F[h[a]] for h in Hs])
    if w is None:
        return L.unit(d.mean(0))
    return (w @ d) / w.sum(1, keepdims=True)


def frll_soft_hosts(c):
    nat = {c.items[i]["photo"]: i for i in c.F if i.startswith("Fm|") and c.items[i]["role"] == "native"}
    e7 = {c.items[i]["photo"]: i for i in c.F if i.startswith("Fm|") and c.items[i]["role"] == "e7_FaceMorpher"}
    return [dict(cluster=p[:3], s0=nat[p], s1=e7[p]) for p in sorted(set(nat) & set(e7))]


def q2(c, nsplit=200):
    defs = {"G pipeline": (c.HG, "x0", "x1"), "G same-person mixing": (c.HG, "x1", "x2"),
            "G second identity": (c.HG, "x2", "x3"), "G whole morph": (c.HG, "x1", "x3"),
            "H whole morph": (c.HHr, "x1", "x3"), "H latent spread": (c.HHr, "x1", "x1s"),
            "H morph beyond spread": (c.HHr, "x1s", "x3"),
            "S softening (SMDD)": (c.HS, "s0", "s1"),
            "FRLL softening (diagnostic of FRLL images)": (frll_soft_hosts(c), "s0", "s1")}
    names = list(defs)
    setof = {n: n.split()[0] for n in names}
    full = {n: dirs_weighted(c.F, *defs[n]) for n in names}
    M, R = {}, {}
    rng = np.random.default_rng(401)
    for st in ("G", "H"):
        nn = [n for n in names if setof[n] == st]
        Hs = defs[nn[0]][0]
        cl = sorted({h["cluster"] for h in Hs})
        vals = {(x, y): [] for x in nn for y in nn}
        for _ in range(nsplit):
            perm = rng.permutation(len(cl))
            half = {cl[j]: (i < len(cl) // 2) for i, j in enumerate(perm)}
            hA = [h for h in Hs if half[h["cluster"]]]
            hB = [h for h in Hs if not half[h["cluster"]]]
            uA = {n: dirs_weighted(c.F, hA, *defs[n][1:]) for n in nn}
            uB = {n: dirs_weighted(c.F, hB, *defs[n][1:]) for n in nn}
            for x in nn:
                for y in nn:
                    vals[(x, y)].append(float(uA[x] @ uB[y]))
        for (x, y), v in vals.items():
            if x == y:
                R[x] = dict(mean=float(np.mean(v)), pct=[float(np.quantile(v, .025)), float(np.quantile(v, .975))])
            elif names.index(x) < names.index(y):
                vv = np.array(v) * 0.5 + np.array(vals[(y, x)]) * 0.5
                M[f"{x} | {y}"] = dict(cos=float(np.mean(vv)), interval=[float(np.quantile(vv, .025)), float(np.quantile(vv, .975))],
                                       method="cross-fitted half splits (200)")
    # different sets: full directions, cluster bootstrap of both sets
    Bq = 1000
    boot = {}
    for n in names:
        Hs, a, b = defs[n]
        D = L.Draw([h["cluster"] for h in Hs], Bq, [20261111, 75, names.index(n)])
        v = dirs_weighted(c.F, Hs, a, b, D.w([h["cluster"] for h in Hs]))
        boot[n] = v / np.linalg.norm(v, axis=1, keepdims=True)
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            if setof[x] == setof[y] and setof[x] in ("G", "H"):
                continue
            cb = (boot[x] * boot[y]).sum(1)
            M[f"{x} | {y}"] = dict(cos=float(full[x] @ full[y]), interval=L.ci(cb), method="full directions, cluster bootstrap")
    for n in names:
        if n not in R:
            Hs, a, b = defs[n]
            cl = sorted({h["cluster"] for h in Hs})
            v = []
            for _ in range(nsplit):
                perm = rng.permutation(len(cl))
                half = {cl[j]: (i < len(cl) // 2) for i, j in enumerate(perm)}
                v.append(float(dirs_weighted(c.F, [h for h in Hs if half[h["cluster"]]], a, b)
                               @ dirs_weighted(c.F, [h for h in Hs if not half[h["cluster"]]], a, b)))
            R[n] = dict(mean=float(np.mean(v)), pct=[float(np.quantile(v, .025)), float(np.quantile(v, .975))])
    key = lambda x, y: f"{x} | {y}" if f"{x} | {y}" in M else f"{y} | {x}"
    readings = {
        "mixing aligned with whole morph (cos >= 0.5)": M[key("G same-person mixing", "G whole morph")]["cos"] >= 0.5,
        "mixing is softness (cos with SMDD softening > 0.5)": M[key("G same-person mixing", "S softening (SMDD)")]["cos"] > 0.5,
    }
    return dict(cosines=M, split_half_reliability=R, readings=readings), full


# ---------------- heads ----------------
def head_pairs(Hs, pos):
    return [(h[pos], h["x1"]) for h in Hs]


def oof_scores(F, Hs, fo, pos, seed, U_fn=None):
    """OOF scores of every G image (x0..x3) from the head trained on the other folds. U_fn(train_hosts) -> rows to
    project out (or None)."""
    sc, Cs = {}, []
    for k in range(5):
        tr = [h for h in Hs if fo[h["cluster"]] != k]
        te = [h for h in Hs if fo[h["cluster"]] == k]
        U = U_fn(tr) if U_fn else None
        ids = sorted({h[r] for h in Hs for r in ("x0", "x1", "x2", "x3")})
        Fk = {i: L.project_out(F[i][None], U)[0] for i in ids} if U is not None else F
        pairs = head_pairs(tr, pos)
        imgs = sorted({i for pr in pairs for i in pr})
        hd, C = L.fit_head(Fk, pairs, [h["cluster"] for h in tr], imgs, seed + k)
        Cs.append(C)
        tid = sorted({h[r] for h in te for r in ("x0", "x1", "x2", "x3")})
        s = hd.score(np.array([Fk[i] for i in tid]))
        sc.update(zip(tid, s.tolist()))
    return sc, Cs


def final_head(F, Hs, fo, pos, U=None):
    ids = sorted({h[r] for h in Hs for r in ("x0", "x1", "x2", "x3")})
    Fk = {i: L.project_out(F[i][None], U)[0] for i in ids} if U is not None else F
    pairs = head_pairs(Hs, pos)
    # C by the registered 5 folds (paired AUC), ties to the smaller C
    best, bestC = -1, None
    for Cc in L.CS:
        acc = 0
        for k in range(5):
            tr = [h for h in Hs if fo[h["cluster"]] != k]
            te = [h for h in Hs if fo[h["cluster"]] == k]
            ptr = head_pairs(tr, pos)
            hd = L.PairHead(Cc).fit(np.array([Fk[i] for i in sorted({i for pr in ptr for i in pr})]),
                                    np.array([Fk[p] for p, _ in ptr]), np.array([Fk[n] for _, n in ptr]))
            pte = head_pairs(te, pos)
            acc += L.paired_auc(hd.score(np.array([Fk[p] for p, _ in pte])), hd.score(np.array([Fk[n] for _, n in pte]))) * len(pte)
        acc /= len(pairs)
        if acc > best + 1e-12:
            best, bestC = acc, Cc
    imgs = sorted({i for pr in pairs for i in pr})
    hd = L.PairHead(bestC).fit(np.array([Fk[i] for i in imgs]), np.array([Fk[p] for p, _ in pairs]), np.array([Fk[n] for _, n in pairs]))

    def score(ids_, Fext):
        X = np.array([Fext[i] for i in ids_])
        if U is not None:
            X = L.project_out(X, U)
        return dict(zip(ids_, hd.score(X).tolist()))
    return score, bestC


def contrast(c, sc, Hs, D, p, n, with_floor=True):
    ip = sorted({h[p] for h in Hs})
    inn = sorted({h[n] for h in Hs})
    clp = [c.items[i]["cluster"] for i in ip]
    cln = [c.items[i]["cluster"] for i in inn]
    wp, wn = D.w(clp), D.w(cln)
    sp, sn = np.array([sc[i] for i in ip]), np.array([sc[i] for i in inn])
    hb = L.wauc(sp, sn, wp, wn)
    out = dict(n_pos=len(ip), n_neg=len(inn), auc=L.auc(sp, sn), ci=L.ci(hb))
    # paired win rate over hosts
    d = np.array([sc[h[p]] - sc[h[n]] for h in Hs])
    wh = D.w([h["cluster"] for h in Hs])
    out["paired_win"] = float(np.mean(d > 0))
    out["paired_win_ci"] = L.ci((wh * (d > 0)).sum(1) / wh.sum(1))
    if with_floor and c.S:
        fl = {}
        best, bestj, bestflip, bestrep = -1, None, None, None
        for j, nm in enumerate(c.stat_names):
            xp, xn = np.array([c.S[i][j] for i in ip]), np.array([c.S[i][j] for i in inn])
            raw = L.auc(xp, xn)
            rep = L.wauc(xp, xn, wp, wn)
            flip = raw < 0.5
            fa, frep = (1 - raw, 1 - rep) if flip else (raw, rep)
            fl[nm] = dict(auc_folded=fa, ci=L.ci(frep), direction="positive lower" if flip else "positive higher")
            if fa > best:
                best, bestj, bestflip, bestrep = fa, nm, flip, frep
        out["floor"] = dict(best=bestj, auc=best, per_stat=fl)
        out["excess_over_floor"] = dict(point=out["auc"] - best, ci=L.ci(hb - bestrep))
        if all(i in c.dmean for i in ip + inn):
            xp, xn = -np.array([c.dmean[i] for i in ip]), -np.array([c.dmean[i] for i in inn])
            raw = L.auc(xp, xn)
            rep = L.wauc(xp, xn, wp, wn)
            out["latent_averageness_auc"] = dict(auc_closer_to_mean_is_positive=raw, ci=L.ci(rep))
    return out, hb


def flag_rates(score, c):
    out = {}
    groups = {"Fm": ("native", ("e7_FaceMorpher", "e7_OpenCV", "e7_Webmorph")),
              "Fe": ("native", ("e7_amsl", "e7_facemorpher", "e7_opencv", "e7_webmorph"))}
    for st, (nat, softs) in groups.items():
        nid = sorted(i for i in c.F if i.startswith(st + "|") and c.items[i]["role"] == nat)
        s = score(nid, c.F)
        sn = np.array([s[i] for i in nid])
        t = float(np.quantile(sn, 0.95, method="higher"))
        byphoto = {c.items[i]["photo"]: s[i] for i in nid}
        out[f"{st} native"] = dict(n=len(sn), threshold=t, flagged=int((sn > t).sum()))
        for so in softs:
            sid = sorted(i for i in c.F if i.startswith(st + "|") and c.items[i]["role"] == so)
            ss = score(sid, c.F)
            v = np.array([ss[i] for i in sid])
            k = int((v > t).sum())
            sh = np.array([ss[i] - byphoto[c.items[i]["photo"]] for i in sid])
            out[f"{st} {so}"] = dict(n=len(v), flagged=k, rate=k / len(v), cp95=cp(k, len(v)),
                                     mean_shift_in_native_sd=float(sh.mean() / sn.std()),
                                     share_scored_above_own_native=float(np.mean(sh > 0)))
    tid = [h for h in c.HS if h["part"] == "S_test"]
    s0 = score([h["s0"] for h in tid], c.F)
    s1 = score([h["s1"] for h in tid], c.F)
    a0 = np.array([s0[h["s0"]] for h in tid])
    a1 = np.array([s1[h["s1"]] for h in tid])
    t = float(np.quantile(a0, 0.95, method="higher"))
    k = int((a1 > t).sum())
    out["S_test SMDD render E7 copy"] = dict(n=len(a1), flagged=k, rate=k / len(a1), cp95=cp(k, len(a1)),
                                             mean_shift_in_native_sd=float((a1 - a0).mean() / a0.std()),
                                             share_scored_above_own_native=float(np.mean(a1 > a0)))
    out["primary"] = out["Fm e7_FaceMorpher"]["rate"]
    return out


def eer(pos, neg):
    t = np.unique(np.r_[pos, neg])
    best = (2, None)
    for th in t:
        fr = np.mean(pos < th)
        fa = np.mean(neg >= th)
        if abs(fr - fa) < best[0]:
            best = (abs(fr - fa), (fr + fa) / 2)
    return float(best[1])


def bench(score, c):
    out = {}
    cells = {"FRLL-Morphs StyleGAN": ("Be|", "morph_stylegan", "Fe|"), "corrected MAD22 MIPGAN-I": ("Bm|", "morph_MIPGAN_I", "Fm|"),
             "corrected MAD22 MIPGAN-II": ("Bm|", "morph_MIPGAN_II", "Fm|")}
    for nm, (pre, role, gpre) in cells.items():
        mid = sorted(i for i in c.F if i.startswith(pre) and c.items[i]["role"] == role)
        gid = sorted(i for i in c.F if i.startswith(gpre) and c.items[i]["role"] == "native")
        if not mid:
            continue
        sm, sg = score(mid, c.F), score(gid, c.F)
        vm, vg = np.array([sm[i] for i in mid]), np.array([sg[i] for i in gid])
        wm = c.DFR.w([(c.items[i]["pa"][:3], c.items[i]["pb"][:3]) for i in mid])
        wg = c.DFR.w([c.items[i]["photo"][:3] for i in gid])
        ab = L.wauc(vm, vg, wm, wg)
        neu = [k for k, i in enumerate(gid) if c.items[i]["photo"].endswith("_03")]
        abn = L.wauc(vm, vg[neu], wm, wg[:, neu])
        t = float(np.quantile(vg, 0.95, method="higher"))
        out[nm] = dict(n_morph=len(vm), n_genuine=len(vg), auc=L.auc(vm, vg), ci=L.ci(ab), eer=eer(vm, vg),
                       auc_neutral_genuine_only=L.auc(vm, vg[neu]), ci_neutral=L.ci(abn),
                       morphs_flagged_at_native_5pct=float(np.mean(vm > t)))
    return out


def h_transfer(c, score, Hs, D):
    sc = score(sorted({h[r] for h in Hs for r in ("x1", "x3", "x1s")}), c.F)
    out = {}
    for p, n in H_CONTRASTS:
        out[f"{p} vs {n}"] = contrast(c, sc, Hs, D, p, n, with_floor=(Hs is c.HHr))[0]
    return out, sc


def reading(auc31, excess, flag):
    if auc31 >= 0.75 and excess >= 0.05 and flag <= 0.15:
        return "works"
    if auc31 < 0.60 or excess <= 0:
        return "fails"
    return "in-between"


def run_heads(c, U_oof=None, U_final=None, label="none", robust=False):
    res = {}
    for hname, pos in (("one-person head O (x2 vs x1)", "x2"), ("two-person head T (x3 vs x1)", "x3")):
        sc, Cs = oof_scores(c.F, c.HG, c.foG, pos, 401, U_oof)
        r = dict(C_per_fold=Cs)
        boots = {}
        for p, n in G_CONTRASTS:
            r[f"G {p} vs {n}"], boots[(p, n)] = contrast(c, sc, c.HG, c.DG, p, n)
        if robust:
            rr = []
            for fs in (402, 403, 404, 405):
                fo2 = L.folds([h["cluster"] for h in c.HG], 5, fs)
                s2, _ = oof_scores(c.F, c.HG, fo2, pos, fs, U_oof)
                rr.append(L.auc([s2[h] for h in sorted({x["x3"] for x in c.HG})], [s2[h] for h in sorted({x["x1"] for x in c.HG})]))
            r["robustness_fold_seeds_402_405_auc_x3_vs_x1"] = rr
        U = U_final
        score, Cf = final_head(c.F, c.HG, c.foG, pos, U)
        r["final_head_C"] = Cf
        r["H raw frame (transfer)"], hsc = h_transfer(c, score, c.HHr, c.DH)
        r["H aligned frame (transfer, descriptive)"], _ = h_transfer(c, score, c.HHa, c.DH)
        r["flag_rates"] = flag_rates(score, c)
        r["benchmarks"] = bench(score, c)
        g = r["G x3 vs x1"]
        r["reading"] = reading(g["auc"], g["excess_over_floor"]["point"], r["flag_rates"]["primary"])
        r["_oof"] = sc
        r["_boot31"] = boots[("x3", "x1")]
        r["_hsc"] = hsc
        res[hname] = r
    o, t = res["one-person head O (x2 vs x1)"], res["two-person head T (x3 vs x1)"]
    d = o["_boot31"] - t["_boot31"]
    res["O minus T, G x3 vs x1"] = dict(point=o["G x3 vs x1"]["auc"] - t["G x3 vs x1"]["auc"], ci=L.ci(d))
    return res


def q5(c, res):
    out = {}
    for hname in ("one-person head O (x2 vs x1)", "two-person head T (x3 vs x1)"):
        sc, hsc = res[hname]["_oof"], res[hname]["_hsc"]
        blocks = sorted({h["cluster"] for h in c.HG})
        gain = {b: np.mean([sc[h["x3"]] - sc[h["x1"]] for h in c.HG if h["cluster"] == b]) for b in blocks}
        dis = {}
        for h in c.HG:
            if h["slot"] == "a0":
                ta, tb = c.tmpl[h["own_tmpl"]], c.tmpl[h["partner_tmpl"]]
                dis[h["cluster"]] = 1 - float(ta @ tb / np.linalg.norm(ta) / np.linalg.norm(tb))
        g = np.array([gain[b] for b in blocks])
        dd = np.array([dis[b] for b in blocks])
        rng = np.random.default_rng(401)
        bs = []
        for _ in range(2000):
            j = rng.integers(0, len(blocks), len(blocks))
            bs.append(spearmanr(g[j], dd[j]).statistic)
        r = dict(G_blocks=len(blocks), rho_gain_vs_FR_dissimilarity=float(spearmanr(g, dd).statistic), ci=L.ci(bs))
        r["rises"] = bool(r["rho_gain_vs_FR_dissimilarity"] > 0 and r["ci"][0] > 0)
        # latent displacement (descriptive): host-level, and pooled x2/x3 "graded" distance
        lg, ld, pg, pd_ = [], [], [], []
        for h in c.HG:
            wo = c.lat[f"G|{h['own_tmpl']}"]
            wp = c.lat[f"G|{h['partner_lat']}"]
            ws = c.lat[f"G|{h['same_lat']}"]
            lg.append(sc[h["x3"]] - sc[h["x1"]])
            ld.append(np.linalg.norm(wo - wp))
            pg += [sc[h["x2"]] - sc[h["x1"]], sc[h["x3"]] - sc[h["x1"]]]
            pd_ += [np.linalg.norm(wo - ws), np.linalg.norm(wo - wp)]
        r["rho_host_gain_vs_latent_distance_descriptive"] = float(spearmanr(lg, ld).statistic)
        r["rho_pooled_x2_x3_gain_vs_latent_distance_descriptive"] = float(spearmanr(pg, pd_).statistic)
        # H: final head per pair
        hp = c.HHr
        gx = np.array([hsc[h["x3"]] - hsc[h["x1"]] for h in hp])
        gs = np.array([hsc[h["x3"]] - hsc[h["x1s"]] for h in hp])
        dh = np.array([1 - float(h["pair_cos"]) for h in hp])
        bx, bs2 = [], []
        for _ in range(2000):
            j = rng.integers(0, len(hp), len(hp))
            bx.append(spearmanr(gx[j], dh[j]).statistic)
            bs2.append(spearmanr(gs[j], dh[j]).statistic)
        r["H_rho_gain_x3_minus_x1_vs_dissimilarity"] = dict(rho=float(spearmanr(gx, dh).statistic), ci=L.ci(bx))
        r["H_rho_gain_x3_minus_x1s_vs_dissimilarity"] = dict(rho=float(spearmanr(gs, dh).statistic), ci=L.ci(bs2))
        out[hname] = r
    out["graded mixing"] = "not testable: no graded GAN latent mixes exist (GAN32 and H3 are midpoints; the GAN dose curve (AG3) was not run)"
    return out


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if not str(k).startswith("_")}
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feat", required=True)
    ap.add_argument("--B", type=int, default=10000)
    a = ap.parse_args()
    bb, kind = a.feat.split(":")
    t0 = time.time()
    c = Ctx(bb, kind, a.B)
    out = dict(feature=L.FNAME[(bb, kind)], B=a.B)
    out["Q1"] = q1(c)
    print(f"Q1 done {time.time() - t0:.0f}s", flush=True)
    out["Q2"], full = q2(c)
    print(f"Q2 done {time.time() - t0:.0f}s", flush=True)
    base = run_heads(c, robust=True)
    out["Q3"] = strip(base)
    print(f"Q3 done {time.time() - t0:.0f}s", flush=True)
    u_soft = dirs_weighted(c.F, [h for h in c.HS if h["part"] == "S_fit"], "s0", "s1")
    u_pipe_all = dirs_weighted(c.F, c.HG, "x0", "x1")
    u_spread = dirs_weighted(c.F, c.HHr, "x1", "x1s")
    pipe_fn = lambda tr: L.unit(np.mean([c.F[h["x1"]] - c.F[h["x0"]] for h in tr], 0))[None]
    variants = {"(a) softening removed": (lambda tr: u_soft[None], u_soft[None]),
                "(b) pipeline removed": (pipe_fn, u_pipe_all[None]),
                "(c) softening and pipeline removed": (lambda tr: np.r_[u_soft[None], pipe_fn(tr)], np.r_[u_soft[None], u_pipe_all[None]]),
                "(d) latent spread (set H) removed, G only, descriptive": (lambda tr: u_spread[None], u_spread[None])}
    q4 = {}
    for vn, (fo_fn, Uf) in variants.items():
        rv = run_heads(c, U_oof=fo_fn, U_final=Uf, label=vn)
        q4[vn] = {}
        for hname in ("one-person head O (x2 vs x1)", "two-person head T (x3 vs x1)"):
            r, b0 = rv[hname], base[hname]
            q4[vn][hname] = dict(
                G_x3_vs_x1=r["G x3 vs x1"]["auc"], G_x3_vs_x1_ci=r["G x3 vs x1"]["ci"],
                G_x3_vs_x1_before=b0["G x3 vs x1"]["auc"], drop=b0["G x3 vs x1"]["auc"] - r["G x3 vs x1"]["auc"],
                G_x3_vs_x2=r["G x3 vs x2"]["auc"], G_x2_vs_x1=r["G x2 vs x1"]["auc"], G_x3_vs_x0=r["G x3 vs x0"]["auc"],
                excess_over_floor=r["G x3 vs x1"]["excess_over_floor"]["point"],
                primary_flag_rate=r["flag_rates"]["primary"], primary_flag_rate_before=b0["flag_rates"]["primary"],
                primary_flag_cp95=r["flag_rates"]["Fm e7_FaceMorpher"]["cp95"],
                S_test_flag_rate=r["flag_rates"]["S_test SMDD render E7 copy"]["rate"],
                H_x3_vs_x1=r["H raw frame (transfer)"]["x3 vs x1"]["auc"], H_x3_vs_x1s=r["H raw frame (transfer)"]["x3 vs x1s"]["auc"],
                keeps_separation=bool(b0["G x3 vs x1"]["auc"] - r["G x3 vs x1"]["auc"] <= 0.05),
                loses_softening_reaction=bool(r["flag_rates"]["primary"] <= 0.15),
                reading=r["reading"],
                benchmarks={k: dict(auc=v["auc"], ci=v["ci"], eer=v["eer"]) for k, v in r["benchmarks"].items()} if not vn.startswith("(c)") and not vn.startswith("(d)") else None)
        print(f"Q4 {vn} done {time.time() - t0:.0f}s", flush=True)
    out["Q4"] = q4
    out["Q5"] = q5(c, base)
    out["seconds"] = time.time() - t0
    L.dump(out, f"res_{bb}_{kind}.json")
    # OOF scores for the record (large-ish): big disk
    so, st = base["one-person head O (x2 vs x1)"]["_oof"], base["two-person head T (x3 vs x1)"]["_oof"]
    np.savez(L.BIG / f"oof_{bb}_{kind}.npz", O_id=np.array(list(so)), O_score=np.array(list(so.values())),
             T_id=np.array(list(st)), T_score=np.array(list(st.values())))
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
