"""AF0 metrics from heads.py outputs (F4 in f4.py; CN0 in cn0.py; mirror distance in mirror.py).

  F1  validation persons, images with a non-constant field (gradient, bump): Spearman between predicted and true
      per-patch target over the patches inside the face hull, per image, averaged; 95% interval = cluster bootstrap
      over host persons. Wave 2/3: the same on every non-zero validation morph with a measured target; template
      baseline (correlation of each true map with the mean training map) and the correlation after removing it.
  F2  landmark ladder (AR1): AUC (higher rung positive) with AR1's pigeonhole person bootstrap (a41_read.Draw,
      B = 2,000, seed [20261111, 1]); R2 vs R4 FaceMorpher is the registered cell; R2w vs R4 etc. descriptive.
  F3  genuine-photo shift in R0 standard deviations: FRLL native frames -> existing E7 frames per family (and
      corrected MAD22 native -> E7), primary pool R0 -> R2 and R0 -> R2w per tool; person bootstrap interval.
  F5  EER per benchmark landmark cell, genuine native and E7 (person bootstrap interval); Poisson set (A27) AUC / EER.
  Floor (wave 3, control 1): for every AUC, the AUC of -lapvar (Laplacian variance alone, lower = positive) and the
      best folded AUC among the 27 simple statistics (cue_floor + PNG bytes); 'excess' = head AUC - floor.
Score keys: score (mean in hull), score_top10, score_median, score_inner, score_periph (patch heads); logreg: score.
  python3 -I metrics.py --backbone dinov3_512 --tag full --af0 af0_w1,af0_w2 --bench bench_s [--heads ...] [--key score]
"""
import argparse
import collections
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402

_ROWS, _CUES = {}, {}


def rows(lst):
    if lst not in _ROWS:
        _ROWS[lst] = {r["id"]: r for r in L.rows(lst)}
    return _ROWS[lst]


def cues(lst):
    if lst not in _CUES:
        p = L.OUT / "cues" / f"{lst}.npz"
        if not p.exists():
            _CUES[lst] = None
        else:
            z = np.load(p)
            _CUES[lst] = (dict(zip(z["ids"], z["cues"])), list(z["names"]))
    return _CUES[lst]


def load(bb, tag, head, lst, key="score"):
    p = L.OUT / "heads" / bb / tag / f"pred_{head}_{lst}.npz"
    if not p.exists():
        return None
    z = np.load(p)
    k = key if key in z.files else "score"
    return dict(zip(z["ids"], z[k])), (z["patch"] if "patch" in z.files else None), z["ids"]


def pp(r):
    return (r["p1"], r["p2"]) if r["p1"] != r["p2"] else (r["p1"],)


def contrast(S, lst, pos_fn, neg_fn, D=None, floor=True):
    R = rows(lst)
    pos = [r for i, r in R.items() if i in S and pos_fn(r)]
    neg = [r for i, r in R.items() if i in S and neg_fn(r)]
    if len(pos) < 5 or len(neg) < 5:
        return None
    ps, ns = [float(S[r["id"]]) for r in pos], [float(S[r["id"]]) for r in neg]
    a, c = L.auc_ci(ps, [pp(r) for r in pos], ns, [pp(r) for r in neg], D=D)
    out = dict(auc=round(a, 4), ci=[round(x, 4) for x in c], n=[len(pos), len(neg)])
    C = cues(lst) if floor else None
    if C is not None:
        cd, names = C
        if all(r["id"] in cd for r in pos + neg):
            Xp = np.stack([cd[r["id"]] for r in pos])
            Xn = np.stack([cd[r["id"]] for r in neg])
            j = names.index("lapvar")
            St = L.stats()
            lap = St.auc(-Xp[:, j], -Xn[:, j])
            best, bname = 0.5, None
            for k, nm in enumerate(names):
                if not (np.isfinite(Xp[:, k]).all() and np.isfinite(Xn[:, k]).all()):
                    continue
                au = St.auc(Xp[:, k], Xn[:, k])
                if max(au, 1 - au) > best:
                    best, bname = max(au, 1 - au), nm
            out.update(lapvar_floor=round(lap, 4), excess_over_lapvar=round(a - lap, 4), best_simple=bname,
                       best_simple_auc=round(best, 4), excess_over_best_simple=round(a - best, 4))
    return out


def shift(S, lst, base_fn, new_fn):
    R = rows(lst)
    b = [r for i, r in R.items() if i in S and base_fn(r)]
    n = [r for i, r in R.items() if i in S and new_fn(r)]
    if len(b) < 5 or len(n) < 5:
        return None
    pt, c = L.shift_ci([float(S[r["id"]]) for r in b], [(r["p1"],) for r in b],
                       [float(S[r["id"]]) for r in n], [(r["p1"],) for r in n])
    return dict(shift=round(pt, 3), ci=[round(x, 3) for x in c], n=[len(b), len(n)])


def eer(S, lst, bona_fn, morph_fn):
    R = rows(lst)
    b = [r for i, r in R.items() if i in S and bona_fn(r)]
    m = [r for i, r in R.items() if i in S and morph_fn(r)]
    if len(b) < 5 or len(m) < 5:
        return None
    e, c = L.eer_ci([float(S[r["id"]]) for r in b], [(r["p1"],) for r in b],
                    [float(S[r["id"]]) for r in m], [(r["p1"], r["p2"]) for r in m])
    return dict(eer=round(e, 2), ci=[round(x, 2) for x in c], n=[len(b), len(m)])


LADDER = [("R2vsR4", "R4", "R2"), ("R2wvsR4", "R4", "R2w"), ("R0vsR4", "R4", "R0"), ("R3vsR4", "R4", "R3"),
          ("R2vsR3", "R3", "R2"), ("R2wvsR3", "R3", "R2w"), ("R3mvsR4", "R4", "R3m"), ("R2wvsR3m", "R3m", "R2w"),
          ("R0vsR2", "R2", "R0"), ("R0vsR2w", "R2w", "R0")]


def panel(get, bench="bench_s"):
    """get(list) -> {id: score} or None. Returns the standard panel of contrasts."""
    out = {}
    S = get("ar1")
    if S:
        for cell in ("frgcferet", "frll"):
            for tool in ("facemorpher", "opencv"):
                d = {}
                for name, pos, neg in LADDER:
                    pf = (lambda r, pos=pos: r["cell"] == cell and r["tool"] == tool and r["rung"] == pos)
                    nf = (lambda r, neg=neg: r["cell"] == cell and r["rung"] == "R0") if neg == "R0" else \
                        (lambda r, neg=neg: r["cell"] == cell and r["tool"] == tool and r["rung"] == neg)
                    c = contrast(S, "ar1", pf, nf)
                    if c:
                        d[name] = c
                for rung in ("R2", "R2w"):
                    s_ = shift(S, "ar1", lambda r: r["cell"] == cell and r["rung"] == "R0",
                               lambda r, rung=rung: r["cell"] == cell and r["tool"] == tool and r["rung"] == rung)
                    if s_:
                        d[f"shift_R0_to_{rung}"] = s_
                out[f"ladder/{cell}/{tool}"] = d
    S = get(bench)
    if S:
        d = {}
        for fam in ("opencv", "facemorpher", "amsl", "webmorph"):
            s_ = shift(S, bench, lambda r: r["cell"] == "frllm_frll_bona", lambda r, f=fam: r["cell"] == f"frllm_{f}" and r["rung"] == "e7")
            if s_:
                d[f"FRLL_native_to_E7_{fam}"] = s_
            for gen in ("native", "e7"):
                bf = (lambda r: r["cell"] == "frllm_frll_bona") if gen == "native" else \
                    (lambda r, f=fam: r["cell"] == f"frllm_{f}" and r["rung"] == "e7")
                e = eer(S, bench, bf, lambda r, f=fam: r["cell"] == f"frllm_{f}" and r["rung"] == "morph")
                if e:
                    d[f"EER_frllm_{fam}_{gen}"] = e
                c = contrast(S, bench, lambda r, f=fam: r["cell"] == f"frllm_{f}" and r["rung"] == "morph", bf)
                if c:
                    d[f"AUC_frllm_{fam}_{gen}"] = c
        for fam in ("FaceMorpher", "OpenCV", "Webmorph"):
            s_ = shift(S, bench, lambda r: r["cell"] == "mad22_BonaFide", lambda r, f=fam: r["cell"] == f"mad22_{f}" and r["rung"] == "e7")
            if s_:
                d[f"MAD22_native_to_E7_{fam}"] = s_
            for gen in ("native", "e7"):
                bf = (lambda r: r["cell"] == "mad22_BonaFide") if gen == "native" else \
                    (lambda r, f=fam: r["cell"] == f"mad22_{f}" and r["rung"] == "e7")
                e = eer(S, bench, bf, lambda r, f=fam: r["cell"] == f"mad22_{f}" and r["rung"] == "morph")
                if e:
                    d[f"EER_mad22_{fam}_{gen}"] = e
                c = contrast(S, bench, lambda r, f=fam: r["cell"] == f"mad22_{f}" and r["rung"] == "morph", bf)
                if c:
                    d[f"AUC_mad22_{fam}_{gen}"] = c
        out["bench"] = d
    S = get("h1")
    if S:
        out["poisson_h1"] = dict(auc=contrast(S, "h1", lambda r: r["rung"] == "morph", lambda r: r["rung"] == "bona"),
                                 eer=eer(S, "h1", lambda r: r["rung"] == "bona", lambda r: r["rung"] == "morph"))
    S = get("ar1g")
    if S:
        R = rows("ar1g")
        lv = collections.defaultdict(list)
        for i, s in S.items():
            lv[R[i]["rung"]].append(float(s))
        d = {k: [round(float(np.mean(v)), 4), len(v)] for k, v in sorted(lv.items())}
        for k in sorted(lv):
            if k != "m0.0":
                c = contrast(S, "ar1g", lambda r, k=k: r["rung"] == k, lambda r: r["rung"] == "m0.0", floor=False)
                if c:
                    d[f"AUC_{k}_vs_m0.0"] = c
        try:
            from scipy.stats import page_trend_test
            hosts = sorted({R[i]["p1"] for i in S})
            levels = sorted(lv)
            M = {(R[i]["p1"], R[i]["rung"]): float(s) for i, s in S.items()}
            data = np.array([[M[(h, k)] for k in levels] for h in hosts if all((h, k) in M for k in levels)])
            d["page_trend_p"] = float(page_trend_test(data).pvalue)
        except Exception as e:  # noqa: BLE001
            d["page_trend_error"] = repr(e)
        out["graded_ar1g"] = d
    return out


def f1(bb, tag, head, af0lists, target="alpha"):
    from scipy.stats import spearmanr
    g = L.GRID[bb]
    vals, hosts, tvals, rvals = [], [], [], []
    per_field = collections.defaultdict(list)
    tmpl_num, tmpl_n = 0, 0
    data = []
    for lst in af0lists:
        P = load(bb, tag, head, lst)
        if P is None or P[1] is None:
            continue
        S, patch, ids = P
        R = L.rows(lst)
        idx = {r["id"]: i for i, r in enumerate(R)}
        pr = L.prep(lst, g)
        T = pr["target"]
        if target != "alpha":
            z = np.load(L.OUT / "ghost_targets.npz")
            gt = dict(zip(z["ids"], z[f"{target}{g}"]))
        for k, iid in enumerate(ids):
            r = R[idx[iid]]
            t = T[idx[iid]] if target == "alpha" else (gt.get(iid) if r["rung"] not in ("photo", "zero", "halfA", "halfB") else None)
            if r["cell"] == "train" and t is not None and r["rung"] not in ("photo", "zero", "halfA", "halfB"):
                tmpl_num = tmpl_num + np.asarray(t, np.float64)
                tmpl_n += 1
            if r["cell"] != "val":
                continue
            per_field[r["rung"]].append(float(S[iid]))
            ok = r["rung"] in (("grad", "bump") if target == "alpha" else ("u25", "u50", "grad", "bump"))
            if ok and t is not None:
                data.append((r, patch[k].astype(np.float32), np.asarray(t, np.float32), pr["face"][idx[iid]] >= L.FACE_MIN))
    if not data:
        return None
    tmpl = tmpl_num / max(tmpl_n, 1)
    for r, p, t, m in data:
        vals.append(spearmanr(p[m], t[m])[0])
        tvals.append(spearmanr(tmpl[m], t[m])[0])
        rvals.append(spearmanr(p[m] - tmpl[m] * (p[m] @ tmpl[m]) / max(tmpl[m] @ tmpl[m], 1e-12),
                               t[m] - tmpl[m] * (t[m] @ tmpl[m]) / max(tmpl[m] @ tmpl[m], 1e-12))[0])
        hosts.append(r["p1"])
    out = {}
    for name, v in (("rho_face", vals), ("template_rho", tvals), ("rho_after_template", rvals)):
        v = np.nan_to_num(np.array(v, float))
        m, c = L.cluster_mean_ci(v, hosts)
        out[name] = round(m, 4)
        out[name + "_ci"] = [round(x, 4) for x in c]
    out["n_images"], out["n_hosts"] = len(vals), len(set(hosts))
    out["val_mean_score_by_field"] = {f: [round(float(np.mean(v)), 4), len(v)] for f, v in sorted(per_field.items())}
    for pos, neg in (("u50", "zero"), ("u50", "photo"), ("zero", "photo"), ("u50", "halfA"), ("u50", "halfB")):
        if per_field.get(pos) and per_field.get(neg):
            out[f"val_auc_{pos}_vs_{neg}"] = round(L.stats().auc(per_field[pos], per_field[neg]), 4)
    return out


def pair_swap(bb, tag, head, af0lists, target="alpha"):
    """predicted map vs own target minus vs the target of another validation morph with the same host
    (Spearman over in-hull patches); mean and host-cluster bootstrap interval."""
    from scipy.stats import spearmanr
    g = L.GRID[bb]
    items = []
    for lst in af0lists:
        P = load(bb, tag, head, lst)
        if P is None or P[1] is None:
            continue
        S, patch, ids = P
        R = L.rows(lst)
        idx = {r["id"]: i for i, r in enumerate(R)}
        pr = L.prep(lst, g)
        if target != "alpha":
            z = np.load(L.OUT / "ghost_targets.npz")
            gt = dict(zip(z["ids"], z[f"{target}{g}"]))
        for k, iid in enumerate(ids):
            r = R[idx[iid]]
            if r["cell"] != "val" or r["rung"] not in (("grad", "bump") if target == "alpha" else ("u25", "u50", "grad", "bump")):
                continue
            t = pr["target"][idx[iid]] if target == "alpha" else gt.get(iid)
            if t is None:
                continue
            items.append((r["p1"], patch[k].astype(np.float32), np.asarray(t, np.float32), pr["face"][idx[iid]] >= L.FACE_MIN))
    by = collections.defaultdict(list)
    for it in items:
        by[it[0]].append(it)
    d, hosts = [], []
    for h, lst in by.items():
        if len(lst) < 2:
            continue
        for j, (_, p, t, m) in enumerate(lst):
            _, _, t2, m2 = lst[(j + 1) % len(lst)]
            mm = m & m2
            d.append(spearmanr(p[mm], t[mm])[0] - spearmanr(p[mm], t2[mm])[0])
            hosts.append(h)
    if not d:
        return None
    m, c = L.cluster_mean_ci(np.nan_to_num(np.array(d)), hosts)
    return dict(mean=round(m, 4), ci=[round(x, 4) for x in c], n=len(d), n_hosts=len(set(hosts)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbone", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--af0", default="af0_w1")
    ap.add_argument("--bench", default="bench_s")
    ap.add_argument("--heads", default=None)
    ap.add_argument("--keys", default="score,score_top10,score_median")
    ap.add_argument("--target", default="alpha")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    d = L.OUT / "heads" / a.backbone / a.tag
    lists = ("af0_w1", "af0_w2", "af0_h", "ar1", "bench", "bench_s", "h1", "ar1g")
    found = set()
    for p in d.glob("pred_*.npz"):
        stem = p.name[5:-4]
        for lst in lists:
            if stem.endswith("_" + lst):
                found.add(stem[: -len(lst) - 1])
    heads = a.heads.split(",") if a.heads else sorted(found)
    res = {}
    for h in heads:
        r = {"F1": f1(a.backbone, a.tag, h, a.af0.split(","), a.target),
             "pair_swap": pair_swap(a.backbone, a.tag, h, a.af0.split(","), a.target)}
        for key in a.keys.split(","):
            if h == "logreg" or h.startswith("thumb_img"):
                if key != "score":
                    continue
            r[key] = panel(lambda lst, key=key: (load(a.backbone, a.tag, h, lst, key) or (None,))[0], a.bench)
        res[h] = r
        f2 = r.get("score", {}).get("ladder/frgcferet/facemorpher", {}).get("R2vsR4")
        print(h, "F1", None if not r["F1"] else (r["F1"]["rho_face"], r["F1"]["rho_face_ci"]), "F2", f2, flush=True)
    out = a.out or (L.RES / f"metrics_{a.backbone}_{a.tag}.json")
    json.dump(res, open(out, "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
