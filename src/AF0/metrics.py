"""AF0 metrics F1, F2, F3, F5 (+ descriptive contrasts) from heads.py outputs; F4 is in f4.py.

  F1  validation persons, images with a non-constant field (grad, bump): Spearman between predicted and true per-patch a
      over the patches inside the face hull, per image, averaged; 95% interval = cluster bootstrap over host persons.
  F2  AR1 ladder, pool frgcferet, FaceMorpher: AUC R2 vs R4 (R4 positive), interval = AR1's two-way pigeonhole person
      bootstrap (a41_read.Draw, B = 2,000, seed [20261111, 1]); also R2w vs R4 (lead), R0 vs R4, R3 vs R4, R2 vs R3,
      R3m vs R4, OpenCV, and the FRLL pool (descriptive).
  F3  genuine-photo shift in R0 standard deviations: FRLL R0 (frll_bona orig frames) -> R1 (existing E7 'resmatch'
      frames of each tool), and primary pool R0 -> R2 and R0 -> R2w per tool; person bootstrap interval.
  F5  EER per benchmark landmark cell, genuine native and E7 (person bootstrap interval).
  python3 -I metrics.py --backbone dinov3_512 --tag first --af0 af0_w1 [--heads ridge,...]
"""
import argparse
import collections
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402


def load(bb, tag, head, lst):
    p = L.OUT / "heads" / bb / tag / f"pred_{head}_{lst}.npz"
    if not p.exists():
        return None
    z = np.load(p)
    return dict(ids=z["ids"], score=z["score"], patch=z["patch"] if "patch" in z else None)


def f1(bb, tag, head, af0lists):
    from scipy.stats import spearmanr
    g = L.GRID[bb]
    vals, hosts, vals_all, fields = [], [], [], []
    per_field = collections.defaultdict(list)
    for lst in af0lists:
        P = load(bb, tag, head, lst)
        if P is None or P["patch"] is None:
            return None
        R = L.rows(lst)
        pr = L.prep(lst, g)
        idx = {r["id"]: i for i, r in enumerate(R)}
        for k, iid in enumerate(P["ids"]):
            r = R[idx[iid]]
            if r["cell"] != "val":
                continue
            per_field[r["rung"]].append(float(P["score"][k]))
            if r["rung"] not in ("grad", "bump"):
                continue
            m = pr["face"][idx[iid]] >= L.FACE_MIN
            t = pr["target"][idx[iid]]
            p = P["patch"][k].astype(np.float32)
            vals.append(spearmanr(p[m], t[m])[0])
            vals_all.append(spearmanr(p, t)[0])
            hosts.append(r["p1"])
            fields.append(r["rung"])
    mean, ci = L.cluster_mean_ci(vals, hosts)
    mean_all, ci_all = L.cluster_mean_ci(vals_all, hosts)
    by = {f: float(np.mean([v for v, ff in zip(vals, fields) if ff == f])) for f in ("grad", "bump")}
    out = dict(rho_face=mean, rho_face_ci=ci, rho_all=mean_all, rho_all_ci=ci_all, n_images=len(vals),
               n_hosts=len(set(hosts)), by_field=by,
               val_mean_score_by_field={f: [float(np.mean(v)), len(v)] for f, v in sorted(per_field.items())})
    # validation AUCs (descriptive): u50 vs zero, u50 vs photo, zero vs photo
    for pos, neg in (("u50", "zero"), ("u50", "photo"), ("zero", "photo"), ("u25", "zero")):
        if per_field.get(pos) and per_field.get(neg):
            out[f"val_auc_{pos}_vs_{neg}"] = L.stats().auc(per_field[pos], per_field[neg])
    return out


def ar1_scores(bb, tag, head):
    P = load(bb, tag, head, "ar1")
    if P is None:
        return None
    R = {r["id"]: r for r in L.rows("ar1")}
    S = collections.defaultdict(lambda: ([], []))
    for iid, s in zip(P["ids"], P["score"]):
        r = R[iid]
        key = (r["cell"], r["tool"], r["rung"])
        S[key][0].append(float(s))
        S[key][1].append((r["p1"], r["p2"]) if r["p1"] != r["p2"] else (r["p1"],))
    return S


CONTRASTS = [("R2vsR4", "R4", "R2"), ("R2wvsR4", "R4", "R2w"), ("R0vsR4", "R4", "R0"), ("R3vsR4", "R4", "R3"),
             ("R2vsR3", "R3", "R2"), ("R2wvsR3", "R3", "R2w"), ("R3mvsR4", "R4", "R3m"), ("R2wvsR3m", "R3m", "R2w"),
             ("NCvsR3", "NC", "R3"), ("R0vsR2", "R2", "R0"), ("R0vsR2w", "R2w", "R0")]


def ladder(S, cell, tool):
    out = {}
    pers = sorted({x for k, (s, pp) in S.items() if k[0] == cell for p in pp for x in p})
    if not pers:
        return out
    St = L.stats()
    D = St.Draw(pers, 2000, [20261111, 1])

    def get(rung):
        k = (cell, "none", "R0") if rung == "R0" else (cell, tool, rung)
        return S.get(k, ([], []))

    for name, pos, neg in CONTRASTS:
        (ps, pp), (ns, npp) = get(pos), get(neg)
        if len(ps) < 5 or len(ns) < 5:
            continue
        a, c = L.auc_ci(ps, pp, ns, npp, D=D)
        out[name] = dict(auc=round(a, 4), ci=[round(x, 4) for x in c], n=[len(ps), len(ns)])
    for rung in ("R0", "R2", "R2w", "R3", "R3m", "R4", "NC"):
        s, _ = get(rung)
        if s:
            out.setdefault("mean", {})[rung] = [round(float(np.mean(s)), 4), round(float(np.std(s)), 4), len(s)]
    return out


def bench_scores(bb, tag, head):
    P = load(bb, tag, head, "bench")
    if P is None:
        return None
    R = {r["id"]: r for r in L.rows("bench")}
    S = collections.defaultdict(lambda: ([], []))
    for iid, s in zip(P["ids"], P["score"]):
        r = R[iid]
        S[(r["cell"], r["rung"])][0].append(float(s))
        S[(r["cell"], r["rung"])][1].append((r["p1"], r["p2"]))
    return S


def f3(S_ar1, S_b):
    out = {}
    if S_b is not None:
        (b0, p0) = S_b.get(("frllm_frll_bona", "native"), ([], []))
        for fam in ("opencv", "facemorpher", "amsl", "webmorph"):
            (b1, p1) = S_b.get((f"frllm_{fam}", "e7"), ([], []))
            if b0 and b1:
                pt, c = L.shift_ci(b0, p0, b1, p1)
                out[f"FRLL_R0_to_R1_{fam}"] = dict(shift=round(pt, 3), ci=[round(x, 3) for x in c], n=[len(b0), len(b1)])
    if S_ar1 is not None:
        for cell in ("frgcferet", "frll"):
            (b0, p0) = S_ar1.get((cell, "none", "R0"), ([], []))
            for tool in ("facemorpher", "opencv"):
                for rung in ("R2", "R2w"):
                    (b1, p1) = S_ar1.get((cell, tool, rung), ([], []))
                    if b0 and b1:
                        pt, c = L.shift_ci(b0, p0, b1, p1)
                        out[f"{cell}_R0_to_{rung}_{tool}"] = dict(shift=round(pt, 3), ci=[round(x, 3) for x in c],
                                                                 n=[len(b0), len(b1)])
    return out


def f5(S_b):
    out = {}
    if S_b is None:
        return out
    cells = [("frllm", f, "frllm_frll_bona") for f in ("amsl", "facemorpher", "opencv", "webmorph")] + \
            [("mad22", f, "mad22_BonaFide") for f in ("FaceMorpher", "OpenCV", "Webmorph")]
    for ds, fam, bona in cells:
        m, mp = S_b.get((f"{ds}_{fam}", "morph"), ([], []))
        for gen, key in (("native", (bona, "native")), ("e7", (f"{ds}_{fam}", "e7"))):
            b, bp = S_b.get(key, ([], []))
            if m and b:
                e, c = L.eer_ci(b, [(p[0],) for p in bp], m, mp)
                out[f"{ds}_{fam}_{gen}"] = dict(eer=round(e, 2), ci=[round(x, 2) for x in c], n=[len(b), len(m)])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbone", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--af0", default="af0_w1")
    ap.add_argument("--heads", default=None)
    a = ap.parse_args()
    d = L.OUT / "heads" / a.backbone / a.tag
    lists = ("af0_w1", "af0_w2", "ar1", "bench")
    found = set()
    for p in d.glob("pred_*.npz"):
        stem = p.name[5:-4]
        for lst in lists:
            if stem.endswith("_" + lst):
                found.add(stem[: -len(lst) - 1])
    heads = a.heads.split(",") if a.heads else sorted(found)
    res = {}
    for h in heads:
        r = {}
        r["F1"] = f1(a.backbone, a.tag, h, a.af0.split(","))
        S = ar1_scores(a.backbone, a.tag, h)
        if S is not None:
            r["ladder"] = {f"{c}/{t}": ladder(S, c, t) for c in ("frgcferet", "frll") for t in ("facemorpher", "opencv")}
        Sb = bench_scores(a.backbone, a.tag, h)
        r["F3"] = f3(S, Sb)
        r["F5"] = f5(Sb)
        res[h] = r
        f2 = r.get("ladder", {}).get("frgcferet/facemorpher", {}).get("R2vsR4")
        print(h, "F1", None if r["F1"] is None else (round(r["F1"]["rho_face"], 3), r["F1"]["rho_face_ci"]),
              "F2", f2, flush=True)
    out = L.RES / f"metrics_{a.backbone}_{a.tag}.json"
    json.dump(res, open(out, "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
