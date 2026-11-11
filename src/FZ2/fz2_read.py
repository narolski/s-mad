"""Frozen read of the new diffusion ladder (FZ2): registered analysis (experiments/FZ2_frozen-read-new-diffusion-ladder/
prereg.md). CPU only, on cached frozen features.

  python -I fz2_read.py --run prod|addon --feats-dir DIR [--smoke]
     prod : DG1 production set B (setB_s0..3), secondary: H-new-3 (X20 vs SAME20) and H-new-4 replication, descriptive rungs
     addon: DG1 add-on (addon_s0..7), primary: H-new-1 .. H-new-4
Reads DIR/{clip_mad,dinov2}_<list>.npz (fz2_feats.py output), DG1 job lists (metadata), the DG1 images under
/mnt/t7/smad_next/DG1/gen/<list>/ (baselines) and the DiffAE-aligned inputs /mnt/t7/smad_next/DG1/pool_a256/ (pair
disagreement and input flags, dg1_manifest_extra.py definitions). Writes experiments/FZ2_.../read_<run>.json and
/mnt/t7/smad_next/FZ2/read_<run>_items.csv (per image: metadata, baselines, head and probe scores).
"""
import argparse, csv, json, os, pathlib, sys, warnings
import numpy as np
import torch

sys.path.insert(0, "/home/narolski/smad-next/src/AR1")
sys.path.insert(0, "/home/narolski/smad-next/src/FZ1")
import fz1_common as K1  # noqa: E402  (wauc, Draw, ci, auc)

OUTX = pathlib.Path("/home/narolski/smad-next/experiments/FZ2_frozen-read-new-diffusion-ladder")
BIG = pathlib.Path("/mnt/t7/smad_next/FZ2")
DG1 = pathlib.Path("/mnt/t7/smad_next/DG1")
POOL = pathlib.Path("/home/narolski/smad-next/experiments/AR1/pool.csv")
FZ1 = pathlib.Path("/mnt/t7/smad_next/FZ1")
BOX = (slice(70, 221), slice(64, 193))
TWINS = ({"frgc:04637", "frgc:04638"}, {"frgc:04692", "frgc:04856"})
CGRID = (1e-3, 1e-2, 1e-1, 1.0, 10.0)
SEED = [20261112, 2, 1]
BB = ("clip_mad", "dinov2")


def ci(x):
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


# ---------------------------------------------------------------- metadata
def pool_info():
    pool = {r["pid"]: r for r in csv.DictReader(open(POOL))}
    cyc, n = {}, 0
    for p in sorted(pool):
        if p in cyc:
            continue
        q = p
        while q not in cyc:
            cyc[q] = n
            q = pool[q]["B_pid"]
        n += 1
    return pool, cyc


def job_rows(run):
    if run == "prod":
        files = [DG1 / "jobs" / f"setB_s{k}.csv" for k in range(4)]
    else:
        files = [DG1 / "addon_jobs" / f"addon_s{k}.csv" for k in range(8)]
    out = {}
    for f in files:
        lst = f.stem
        for r in csv.DictReader(open(f)):
            out[(lst, r["pool"], r["name"])] = r
    return out


def load_items(run, feats_dir, smoke):
    jobs = job_rows(run)
    lists = sorted({k[0] for k in jobs})
    pool, cyc = pool_info()
    items, F = [], {b: [] for b in BB}
    for lst in lists:
        fz = {b: feats_dir / f"{b}_{lst}.npz" for b in BB}
        if not all(p.exists() for p in fz.values()):
            print(f"{lst}: features missing, skipped", flush=True)
            continue
        Z = {b: np.load(fz[b], allow_pickle=False) for b in BB}
        ids = Z["clip_mad"]["id"].tolist()
        assert ids == Z["dinov2"]["id"].tolist()
        for j, rel in enumerate(ids):
            parts = rel.split("/")
            key = (lst, parts[-2], parts[-1])
            if key not in jobs:
                continue                                  # e.g. files that are not job outputs
            r = jobs[key]
            if r["rung"] == "G":
                continue                                  # genuine writes: no registered contrast uses them
            h, p = r["host"], r["partner"]
            pers = (h, p) if p else (h,)
            items.append(dict(id=rel, list=lst, pool=r["pool"], key=r["pool"].split("_", 1)[1], rung=r["rung"],
                              steps=int(r["steps"]), alpha=r["alpha"], host=h, partner=p, persons=pers, cycle=cyc[h],
                              db=h.split(":")[0], src_a=r["src_a"], src_b=r["src_b"], path=str(DG1 / "gen" / lst / rel)))
            for b in BB:
                F[b].append(Z[b]["feat"][j])
    if smoke:
        keep = sorted({it["host"] for it in items})[:120]
        sel = [i for i, it in enumerate(items) if it["host"] in keep]
        items = [items[i] for i in sel]
        F = {b: [F[b][i] for i in sel] for b in BB}
    return items, {b: np.asarray(F[b], np.float64) for b in BB}, pool


def add_input_columns(items, pool):
    """dg1_manifest_extra.py definitions: wedge_in, grey_in, twin_pair, same_date, pair_disagree (face box)."""
    from PIL import Image
    al = DG1 / "pool_a256"
    arr, st = {}, {}

    def inp(stem):
        if stem not in arr:
            x = np.asarray(Image.open(al / f"{stem}.png").convert("RGB")).astype(np.int16)
            arr[stem] = x
            st[stem] = {"black": float((x.max(2) == 0).mean()),
                        "grey": bool((x[..., 0] == x[..., 1]).all() and (x[..., 1] == x[..., 2]).all())}
        return arr[stem], st[stem]

    for it in items:
        h, p = it["host"], it["partner"]
        stems = sorted({s.replace("__flip", "") for s in (it["src_a"], it["src_b"]) if s})
        s2 = [inp(s)[1] for s in stems]
        it["wedge_in"] = int(any(s["black"] > 0.01 for s in s2))
        it["grey_in"] = int(any(s["grey"] for s in s2))
        it["twin_pair"] = int(bool(p) and p != h and {h, p} in TWINS)
        it["same_date"] = int(bool(p) and p != h and pool[h]["H_session"] == pool[p]["S_session"])
        it["flagged"] = int(it["wedge_in"] or it["grey_in"] or it["twin_pair"] or it["same_date"])
        it["d"] = float(np.abs(inp(it["src_a"])[0][BOX] - inp(it["src_b"])[0][BOX]).mean()) \
            if it["src_b"] and not it["src_b"].endswith("__flip") else float("nan")


def add_baselines(items, workers=4):
    if workers <= 1:
        res = [_base_one(it["path"]) for it in items]
    else:
        from multiprocessing import Pool
        with Pool(workers) as pl:
            res = pl.map(_base_one, [it["path"] for it in items], chunksize=64)
    for it, r in zip(items, res):
        it.update(r)


def _blocks(img):
    return img.reshape(32, img.shape[0] // 32, 32, img.shape[1] // 32, 3).mean((1, 3)).ravel().astype(np.float32)


def _base_one(path):
    import cv2
    im = cv2.imread(path)
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    a = im.astype(np.float64)
    box = a[BOX]
    sur = im.astype(np.float32).copy()
    sur[BOX] = 128.0
    return {"png_bytes": float(os.path.getsize(path)), "lapvar_box": float(cv2.Laplacian(g[BOX], cv2.CV_64F).var()),
            "asym_box": float(np.abs(box - box[:, ::-1]).mean()), "thumb32": _blocks(im.astype(np.float32)),
            "surround32": _blocks(sur)}


# ---------------------------------------------------------------- models
def fit_model(X, y, groups):
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    mk = lambda c: make_pipeline(StandardScaler(), LogisticRegression(C=c, max_iter=5000))  # noqa: E731
    best, bestc = -1, None
    for c in CGRID:
        oof = np.zeros(len(y))
        for tr, va in GroupKFold(n_splits=3).split(X, y, groups):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                oof[va] = mk(c).fit(X[tr], y[tr]).predict_proba(X[va])[:, 1]
        a = K1.auc(oof[y == 1], oof[y == 0])
        if a > best + 1e-12:
            best, bestc = a, c
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return mk(bestc).fit(X, y), bestc


class Reader:
    def __init__(self, items, F, B):
        import folds
        self.items, self.F = items, F
        self.fmap = folds.person_fold_map()
        self.fold = np.array([self.fmap[it["host"]] for it in items])
        for it, k in zip(items, self.fold):
            assert all(self.fmap[p] == k for p in it["persons"]), "image straddles folds"
        allp = sorted({r["pid"] for r in csv.DictReader(open(POOL))})
        self.D = K1.Draw(allp, B, SEED)
        self.byk = {}
        for i, it in enumerate(items):
            self.byk.setdefault(it["key"], []).append(i)
        self.cyc = np.array([it["cycle"] for it in items])

    def idx(self, key, mask=None):
        ii = self.byk.get(key, [])
        return [i for i in ii if mask is None or mask(self.items[i])]

    def W(self, ii):
        return self.D.w([self.items[i]["persons"] for i in ii])

    def auc(self, s, ia, ib):
        s = np.asarray(s, float)
        rep = K1.wauc(s[ia], s[ib], self.W(ia), self.W(ib))
        return K1.auc(s[ia], s[ib]), rep

    def probe(self, X, pos, neg, apply=None):
        """OOF scores of a probe trained on pos vs neg (keys) for every image of pos, neg and apply keys."""
        ip, ineg = self.byk[pos], self.byk[neg]
        tr_all = np.array(ip + ineg)
        y_all = np.r_[np.ones(len(ip)), np.zeros(len(ineg))].astype(int)
        keys = [pos, neg] + [k for k in (apply or []) if k in self.byk and k not in (pos, neg)]
        target = np.array(sorted({i for k in keys for i in self.byk[k]}))
        s = np.full(len(self.items), np.nan)
        cs = []
        for k in range(5):
            m = self.fold[tr_all] != k
            if m.sum() == 0:
                continue
            model, c = fit_model(X[tr_all[m]], y_all[m], self.cyc[tr_all[m]])
            cs.append(c)
            te = target[self.fold[target] == k]
            if len(te):
                s[te] = model.decision_function(X[te])
        return s, cs


def heads(Fc):
    from safetensors.torch import load_file
    Xn = Fc / np.linalg.norm(Fc, axis=1, keepdims=True)
    out = {}
    for sd in (401, 402, 403, 404, 405):
        w = torch.load(FZ1 / "heads" / f"head_s{sd}.pt", map_location="cpu", weights_only=True)
        z = Xn @ w["weight"].double().numpy().T + w["bias"].double().numpy()
        out[f"smdd_s{sd}"] = 1 / (1 + np.exp(-(z[:, 0] - z[:, 1])))
    r = load_file(str(FZ1 / "release" / "madation_fe_vitl14_model.safetensors"))
    z = Xn @ r["head.weight"].double().numpy().T + r["head.bias"].double().numpy()
    out["release_fe_vitl14"] = 1 / (1 + np.exp(-(z[:, 0] - z[:, 1])))
    return out


# ---------------------------------------------------------------- baselines per contrast
_BCACHE = {}


def baselines(R, pos, neg, mask=None):
    if mask is None and (pos, neg) in _BCACHE:
        return _BCACHE[(pos, neg)]
    ia, ib = R.idx(pos, mask), R.idx(neg, mask)
    res, reps = {}, {}
    for nm in ("png_bytes", "lapvar_box", "asym_box"):
        s = np.array([it[nm] for it in R.items])
        pt, rep = R.auc(s, ia, ib)
        flip = pt < 0.5
        res[nm] = {"auc_folded": 1 - pt if flip else pt, "direction": f"{pos} lower" if flip else f"{pos} higher"}
        res[nm]["ci"] = ci(1 - rep if flip else rep)
        reps[nm] = 1 - rep if flip else rep
    for nm in ("thumb32", "surround32"):
        X = np.array([it[nm] for it in R.items], np.float64)
        s, cs = R.probe(X, pos, neg)
        pt, rep = R.auc(s, ia, ib)
        res[nm] = {"auc": pt, "ci": ci(rep), "Cs": cs}
        reps[nm] = rep
    best = max(res, key=lambda k: res[k].get("auc_folded", res[k].get("auc")))
    if mask is None:
        _BCACHE[(pos, neg)] = (res, reps, best)
    return res, reps, best


def excess(R, s, pos, neg, mask=None, base=None):
    ia, ib = R.idx(pos, mask), R.idx(neg, mask)
    pt, rep = R.auc(s, ia, ib)
    bres, breps, best = base if base is not None else baselines(R, pos, neg, mask)
    bpt = bres[best].get("auc_folded", bres[best].get("auc"))
    d = rep - breps[best]
    return {"auc": pt, "ci": ci(rep), "best_baseline": best, "best_auc": bpt, "excess": pt - bpt, "excess_ci": ci(d)}


def fmt(x):
    return f"{x['auc']:.3f} [{x['ci'][0]:.3f}, {x['ci'][1]:.3f}]"


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, choices=["prod", "addon"])
    ap.add_argument("--feats-dir", required=True)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    B = 300 if a.smoke else 10000
    items, F, pool = load_items(a.run, pathlib.Path(a.feats_dir), a.smoke)
    print(f"{len(items)} images; keys: " + ", ".join(f"{k}:{n}" for k, n in sorted({it['key']: 0 for it in items}.items())), flush=True)
    add_input_columns(items, pool)
    add_baselines(items, a.workers)
    R = Reader(items, F, B)
    counts = {k: len(v) for k, v in R.byk.items()}
    print("counts", counts, flush=True)
    H = heads(F["clip_mad"])
    out = {"run": a.run, "B": B, "smoke": a.smoke, "counts": counts, "n_hosts": len({it["host"] for it in items})}
    unfl = lambda it: it["flagged"] == 0  # noqa: E731
    masks = {"all": None, "unflagged": unfl, "frgc": lambda it: it["db"] == "frgc", "feret": lambda it: it["db"] == "feret"}

    def sens(s, pos, neg):
        r = {}
        for nm, m in masks.items():
            ia, ib = R.idx(pos, m), R.idx(neg, m)
            if len(ia) > 5 and len(ib) > 5:
                pt, rep = R.auc(s, ia, ib)
                r[nm] = {"auc": pt, "ci": ci(rep), "n": [len(ia), len(ib)]}
        return r

    have = lambda *ks: all(k in R.byk for k in ks)  # noqa: E731
    scores = {}
    # ---------------- H-new-3 (heads, no refit)
    h3 = {}
    if have("X20", "SAME20"):
        base_xs = baselines(R, "X20", "SAME20")
        h3["baselines_X20_vs_SAME20"] = base_xs[0]
        for hn, s in H.items():
            d = {"X20 vs SAME20": excess(R, s, "X20", "SAME20", base=base_xs)}
            d["X20 vs SAME20"]["sensitivity"] = sens(s, "X20", "SAME20")
            for pos, neg in (("SAME20", "FRESH1_20"), ("SAME20", "FRESH2_20"), ("SAME20", "REC20"), ("X20", "REC20"),
                             ("FRESH1_20", "REC20"), ("MIR20", "REC20"), ("X100", "SAME100"), ("SAME100", "FRESH1_100"),
                             ("NOISEX20", "NOISES20"), ("SEMX20", "SEMS20")):
                if have(pos, neg):
                    pt, rep = R.auc(s, R.idx(pos), R.idx(neg))
                    d[f"{pos} vs {neg}"] = {"auc": pt, "ci": ci(rep)}
            h3[hn] = d
        prim = h3["smdd_s401"]
        xs = prim["X20 vs SAME20"]
        if "SAME20 vs FRESH1_20" in prim:
            sf = prim["SAME20 vs FRESH1_20"]["auc"]
            sup = xs["auc"] >= 0.58 and xs["ci"][0] > 0.50 and 0.44 <= sf <= 0.56 and xs["excess"] >= 0.05 and xs["excess_ci"][0] > 0
            fal = xs["auc"] < 0.55 or xs["excess_ci"][0] <= 0
            h3["reading_smdd_s401"] = "supported" if sup else ("falsified" if fal else "not decided")
            rl = h3["release_fe_vitl14"]
            rxs, rsf = rl["X20 vs SAME20"], rl["SAME20 vs FRESH1_20"]["auc"]
            sup = rxs["auc"] >= 0.58 and rxs["ci"][0] > 0.50 and 0.44 <= rsf <= 0.56 and rxs["excess"] >= 0.05 and rxs["excess_ci"][0] > 0
            fal = rxs["auc"] < 0.55 or rxs["excess_ci"][0] <= 0
            h3["reading_release"] = "supported" if sup else ("falsified" if fal else "not decided")
        else:
            h3["reading_smdd_s401"] = "not applicable to this run (no FRESH rung): X vs SAME and excess only"
        print("H-new-3:", {hn: fmt(h3[hn]["X20 vs SAME20"]) + f" excess {h3[hn]['X20 vs SAME20']['excess']:+.3f}" for hn in H}, h3.get("reading_smdd_s401"), flush=True)
    out["H3"] = h3
    for hn, s in H.items():
        scores[hn] = s
    # ---------------- probes per feature set
    for b in BB:
        X = F[b]
        res = {}
        # H-new-1
        if have("SAME20", "REC20"):
            apply = ["FRESH1_20", "FRESH2_20", "X20", "MIR20", "NOISES20", "SEMS20", "NOISEX20", "SEMX20"]
            s_sr, cs = R.probe(X, "SAME20", "REC20", apply)
            scores[f"{b}|D_SR"] = s_sr
            d = {"Cs": cs}
            for pos, neg in (("SAME20", "REC20"), ("FRESH1_20", "REC20"), ("FRESH2_20", "REC20"), ("X20", "REC20"),
                             ("SAME20", "FRESH1_20"), ("X20", "SAME20"), ("MIR20", "REC20"), ("NOISES20", "REC20"),
                             ("SEMS20", "REC20"), ("NOISEX20", "REC20"), ("SEMX20", "REC20")):
                if have(pos, neg):
                    pt, rep = R.auc(s_sr, R.idx(pos), R.idx(neg))
                    d[f"{pos} vs {neg}"] = {"auc": pt, "ci": ci(rep)}
                    if pos in ("NOISES20", "SEMS20"):
                        d[f"_rep_{pos}"] = rep
            if have("FRESH1_20", "REC20"):
                d["FRESH1_20 vs REC20"]["sensitivity"] = sens(s_sr, "FRESH1_20", "REC20")
            if have("NOISES20", "SEMS20", "REC20"):
                diff = d.pop("_rep_NOISES20") - d.pop("_rep_SEMS20")
                d["NOISES minus SEMS along D_SR"] = {"point": d["NOISES20 vs REC20"]["auc"] - d["SEMS20 vs REC20"]["auc"], "ci": ci(diff)}
            res["D_SR (probe SAME20 vs REC20) transfer"] = d
        trained = {}
        for pos, neg in (("SAME20", "FRESH1_20"), ("FRESH1_20", "REC20"), ("FRESH1_20", "FRESH2_20"), ("X20", "REC20"),
                         ("X20", "FRESH1_20"), ("NOISES20", "REC20"), ("SEMS20", "REC20"), ("NOISEX20", "REC20"),
                         ("SEMX20", "REC20"), ("NOISES20", "SEMS20"), ("MIR20", "REC20"),
                         ("SAME100", "REC100"), ("SAME100", "FRESH1_100"), ("FRESH1_100", "REC100"), ("X100", "SAME100")):
            if have(pos, neg):
                s, cs = R.probe(X, pos, neg)
                pt, rep = R.auc(s, R.idx(pos), R.idx(neg))
                ex = excess(R, s, pos, neg) if b == "clip_mad" else None
                trained[f"{pos} vs {neg}"] = {"auc": pt, "ci": ci(rep), "Cs": cs, **({"excess": ex["excess"], "excess_ci": ex["excess_ci"], "best_baseline": ex["best_baseline"], "best_auc": ex["best_auc"]} if ex else {})}
                if f"{pos} vs {neg}" in ("SAME20 vs FRESH1_20", "NOISES20 vs REC20", "SEMS20 vs REC20", "X20 vs SAME20"):
                    trained[f"{pos} vs {neg}"]["sensitivity"] = sens(s, pos, neg)
        if have("SAME100", "REC100", "FRESH1_100"):
            s100, _ = R.probe(X, "SAME100", "REC100", ["FRESH1_100", "X100"])
            pt, rep = R.auc(s100, R.idx("FRESH1_100"), R.idx("REC100"))
            trained["D_SR100 transfer: FRESH1_100 vs REC100"] = {"auc": pt, "ci": ci(rep)}
        res["probes trained on the contrast"] = trained
        # H-new-4
        if have("X20", "SAME20"):
            dose_keys = [k for k in R.byk if k.startswith("DOSE")]
            s_xs, cs = R.probe(X, "X20", "SAME20", dose_keys + ["REC20", "MIR20", "FRESH1_20"])
            scores[f"{b}|P_XS"] = s_xs
            ix, isame = R.idx("X20"), R.idx("SAME20")
            A0, rep0 = R.auc(s_xs, ix, isame)
            dd = np.array([it["d"] for it in items])
            pooled = np.r_[dd[ix], dd[isame]]
            edges = np.quantile(pooled, [0, .2, .4, .6, .8, 1])
            num = np.zeros(R.D.C.shape[0]); den = np.zeros(R.D.C.shape[0]); n1 = d1 = 0.0
            wx, ws = R.W(ix), R.W(isame)
            strata = []
            for q in range(5):
                lo, hi = edges[q], edges[q + 1] + (1e-9 if q == 4 else 0)
                mx = (dd[ix] >= lo) & (dd[ix] < hi); ms = (dd[isame] >= lo) & (dd[isame] < hi)
                strata.append({"q": q, "range": [float(lo), float(edges[q + 1])], "nX": int(mx.sum()), "nSAME": int(ms.sum())})
                if mx.sum() == 0 or ms.sum() == 0:
                    continue
                sx, ss = s_xs[np.array(ix)[mx]], s_xs[np.array(isame)[ms]]
                r = K1.wauc(sx, ss, wx[:, mx], ws[:, ms]); mass = wx[:, mx].sum(1) * ws[:, ms].sum(1)
                num += r * mass; den += mass
                ap_ = K1.auc(sx, ss); n1 += ap_ * mx.sum() * ms.sum(); d1 += mx.sum() * ms.sum()
                strata[-1]["auc"] = ap_
            As = n1 / d1 if d1 else float("nan")
            repS = num / np.maximum(den, 1e-12)
            top = np.quantile(dd[isame], 0.8)
            ihi = [i for i in isame if dd[i] >= top]
            Ahi, repH = R.auc(s_xs, ix, ihi)
            h4 = {"Cs": cs, "A0": {"auc": A0, "ci": ci(rep0)}, "A_s": {"auc": As, "ci": ci(repS[den > 0])},
                  "delta": {"point": A0 - As, "ci": ci((rep0 - repS)[den > 0])}, "A_hi": {"auc": Ahi, "ci": ci(repH), "n_hi": len(ihi)},
                  "strata": strata, "d_median": {"X20": float(np.median(dd[ix])), "SAME20": float(np.median(dd[isame]))},
                  "sensitivity_A0": sens(s_xs, "X20", "SAME20")}
            from scipy.stats import spearmanr
            h4["spearman_score_d"] = {"X20": float(spearmanr(s_xs[ix], dd[ix])[0]), "SAME20": float(spearmanr(s_xs[isame], dd[isame])[0])}
            dose = {}
            for k in sorted(dose_keys):
                ii = R.idx(k)
                dose[k] = {"n": len(ii), "mean_score": float(np.mean(s_xs[ii])), "auc_vs_SAME20": R.auc(s_xs, ii, isame)[0],
                           "auc_vs_REC20": R.auc(s_xs, ii, R.idx("REC20"))[0] if have("REC20") else None}
            for al in ("10", "20", "30", "40"):
                kx, ks = f"DOSEX{al}_20", f"DOSES{al}_20"
                if have(kx, ks):
                    pt, rep = R.auc(s_xs, R.idx(kx), R.idx(ks))
                    dose[f"{kx} vs {ks}"] = {"auc": pt, "ci": ci(rep)}
            for k in ("REC20", "MIR20", "FRESH1_20"):
                if have(k):
                    dose[f"{k} mean score"] = float(np.mean(s_xs[R.idx(k)]))
            dose["X20 mean score"] = float(np.mean(s_xs[ix])); dose["SAME20 mean score"] = float(np.mean(s_xs[isame]))
            two = [i for k in dose_keys if k.startswith(("DOSEX", "DOSE1", "DOSE2", "DOSE3", "DOSE4")) for i in R.idx(k)] + ix
            one = [i for k in dose_keys if k.startswith("DOSES") for i in R.idx(k)] + isame
            alpha = np.array([float(it["alpha"]) if it["alpha"] else 0.0 for it in items])
            if len(two) > 10:
                h4["spearman_score_alpha_d_two_person"] = float(spearmanr(s_xs[two], alpha[two] * dd[two])[0])
            if len([i for i in one if i not in isame]) > 10:
                h4["spearman_score_alpha_d_same_person"] = float(spearmanr(s_xs[one], alpha[one] * dd[one])[0])
            h4["dose"] = dose
            if b == "clip_mad":
                sup = (A0 - As) >= 0.15 and Ahi <= 0.60
                fal = (A0 - As) <= 0.05
                h4["reading"] = "supported" if sup else ("falsified" if fal else "not decided")
            res["H4 (probe X20 vs SAME20)"] = h4
        out[b] = res
        print(f"== {b} done", flush=True)
    # ---------------- readings H-new-1, H-new-2 (clip_mad decides)
    c = out["clip_mad"]
    if "D_SR (probe SAME20 vs REC20) transfer" in c and "SAME20 vs FRESH1_20" in c["probes trained on the contrast"]:
        t = c["D_SR (probe SAME20 vs REC20) transfer"]["FRESH1_20 vs REC20"]
        p = c["probes trained on the contrast"]["SAME20 vs FRESH1_20"]
        sup = t["auc"] >= 0.90 and t["ci"][0] >= 0.85 and p["auc"] <= 0.80 and p["ci"][1] <= 0.85
        fal = t["auc"] <= 0.65 and t["ci"][1] <= 0.70 and p["auc"] >= 0.95 and p["ci"][0] >= 0.92
        out["reading_H1"] = "supported" if sup else ("falsified" if fal else "not decided")
    tc = c["probes trained on the contrast"]
    if "NOISES20 vs REC20" in tc and "SEMS20 vs REC20" in tc:
        n_, s_ = tc["NOISES20 vs REC20"], tc["SEMS20 vs REC20"]
        dd_ = c["D_SR (probe SAME20 vs REC20) transfer"]["NOISES minus SEMS along D_SR"]
        sup = n_["auc"] >= 0.95 and n_["ci"][0] >= 0.90 and s_["auc"] <= 0.85 and s_["ci"][1] <= 0.90 and dd_["point"] >= 0.10 and dd_["ci"][0] > 0
        fal = s_["auc"] >= n_["auc"]
        out["reading_H2"] = "supported" if sup else ("falsified" if fal else "not decided")
        lap = {}
        for k in ("NOISES20", "SEMS20", "NOISEX20", "SEMX20", "SAME20", "X20", "FRESH1_20"):
            if have(k, "REC20"):
                s = np.array([it["lapvar_box"] for it in items])
                pt, rep = R.auc(s, R.idx(k), R.idx("REC20"))
                lap[f"{k} vs REC20"] = {"auc_raw_higher": pt, "ci": ci(rep)}
        out["H2_laplacian_descriptive"] = lap
    for key in ("reading_H1", "reading_H2"):
        print(key, out.get(key), flush=True)
    print("H4 reading", out["clip_mad"].get("H4 (probe X20 vs SAME20)", {}).get("reading"), flush=True)
    tag = f"{a.run}{'_smoke' if a.smoke else ''}"
    json.dump(out, open(OUTX / f"read_{tag}.json", "w"), indent=1, default=float)
    cols = ["id", "list", "key", "rung", "steps", "alpha", "host", "partner", "cycle", "db", "flagged", "d", "png_bytes",
            "lapvar_box", "asym_box"]
    with open(BIG / f"read_{tag}_items.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols + list(scores))
        for i, it in enumerate(items):
            w.writerow([it[k] for k in cols] + [f"{scores[k][i]:.6g}" for k in scores])
    print("wrote", OUTX / f"read_{tag}.json", flush=True)


if __name__ == "__main__":
    main()
