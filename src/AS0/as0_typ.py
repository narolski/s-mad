"""Mirror-asymmetry test (AS0), amendment A10 (review of ID0, hypothesis H-new-2): shape statistics on landmarks
DETECTED on the built ladder images, against the same statistics calculated from source landmark files.

(a) typicality: the identity-shrinkage triage (ID0) statistic, imported unchanged (src/ID0/iss.py ISS and
    analyse.landmark_features / gpa / procrustes_to / fit_rows); fit = ID0's 1,395 genuine fit photos, kmax 64.
    AUC = P(score(two-person) > score(other)), scores iss and typ.
(b) shape asymmetry L_shape (as0_measure.shape_asym), AUC = P(L(X) < L(Y)).
Persons: AR1 pid; bootstrap AR1 stats.Draw, B = 2000, seed [20261111, 61]. With and without the 8 validation-reserved
persons (A12).
  python3 -I as0_typ.py -> experiments/AS0_mirror-asymmetry/typ_detected.csv, typ_detected.json
"""
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import as0_common as K  # noqa: E402
import as0_measure as M  # noqa: E402

sys.path.insert(0, str(K.REPO / "src/ID0"))
import analyse as IA  # noqa: E402  (ID0 analysis module, unchanged; its main() is not run)
import id0_common as IC  # noqa: E402
from iss import ISS  # noqa: E402

sys.path.insert(0, str(K.REPO / "src/AR1"))
import stats as ST  # noqa: E402

SEED = [20261111, 61]


def valbad(p):
    db, s = p.split(":", 1)
    return db in ("frgc", "feret") and IC.is_val(s)


def main():
    items = {it["id"]: it for it in K.read_csv(K.OUT / "items.csv")}
    L = M.LM(items)
    fit = IA.fit_rows()
    T = [IC.read_tem(r["tem"]) for r in fit]
    ref = IA.gpa(T)
    Xfit = np.array([IA.procrustes_to(t, ref).ravel() for t in T])
    model = ISS(Xfit, [r["pid"] for r in fit], kmax=64)

    def feats(lm):
        return IA.procrustes_to(lm, ref).ravel()

    rows, res = [], dict(fit=model.summary())
    groups = {}
    for i, it in items.items():
        if it["set"] in ("LD1", "LD2", "LD3"):
            lm = L.of(it)
            src = items[it["src"]]
            ex = L.of(src)                       # the shape calculated from source landmark files
            key = (src["role"], src["tool"], src.get("level", ""))
            groups.setdefault(key, []).append((src["persons"], lm, ex, src["host"]))
    res["n_detected"] = {f"{k[0]}|{k[1]}|{k[2]}": sum(1 for g in v if g[1] is not None) for k, v in groups.items()}
    allp = sorted({p for v in groups.values() for g in v for p in g[0].split("|")})
    Dr = ST.Draw(allp, 2000, SEED)

    def score_sets(key, kind, stat):
        out = []
        for pers, lm, ex, host in groups.get(key, []):
            s = lm if kind == "detected" else ex
            if s is None or not np.isfinite(s).all():
                continue
            if stat == "shape_L":
                v = -M.shape_asym(s, 512)                      # higher = more symmetric
            else:
                v = model.scores(feats(s)[None])[stat][0]      # higher = more typical
            out.append((tuple(pers.split("|")), v, host))
        return out

    contrasts = [("R4 vs R3", ("R4",), ("R3",)), ("R4 vs R0", ("R4",), ("R0",)), ("R3 vs R0", ("R3",), ("R0",)),
                 ("R4 vs R2w", ("R4",), ("R2w",)), ("R3m vs R2w", ("R3m",), ("R2w",)), ("R4 vs S0", ("R4",), ("S0",)),
                 ("S0 vs R0", ("S0",), ("R0",))]
    for kind in ("detected", "calculated from source landmark files"):
        for stat in ("iss", "typ", "shape_L"):
            for tool in ("pooled", "opencv", "facemorpher"):
                for name, xr, yr in contrasts:
                    def coll(roles):
                        o = []
                        for r in roles:
                            tl = ["none"] if r in ("R0", "S0") else (["opencv", "facemorpher"] if tool == "pooled" else [tool])
                            for t in tl:
                                o += score_sets((r, t, ""), kind, stat)
                        return o
                    X, Y = coll(xr), coll(yr)
                    for drop in (False, True):
                        if drop:
                            X2 = [x for x in X if not any(valbad(p) for p in x[0])]
                            Y2 = [y for y in Y if not any(valbad(p) for p in y[0])]
                        else:
                            X2, Y2 = X, Y
                        if len(X2) < 20 or len(Y2) < 20:
                            continue
                        a, (lo, hi) = ST.wauc_ci(Dr, np.array([x[1] for x in X2]), [x[0] for x in X2],
                                                 np.array([y[1] for y in Y2]), [y[0] for y in Y2])
                        rows.append(dict(kind=kind, stat=stat, engine=tool, contrast=name,
                                         is_val_dropped=int(drop), auc=round(a, 4), lo=round(float(lo), 4),
                                         hi=round(float(hi), 4), nX=len(X2), nY=len(Y2)))
    # detection error of the photos against their .tem files, and of morphs against the calculated target shape
    err = {}
    for key, v in groups.items():
        e = [float(np.linalg.norm(lm - ex, axis=1).mean() / np.linalg.norm(ex[K.PUPIL_R] - ex[K.PUPIL_L]))
             for _, lm, ex, _ in v if lm is not None and ex is not None]
        if e:
            err[f"{key[0]}|{key[1]}|{key[2]}"] = dict(n=len(e), median=round(float(np.median(e)), 4),
                                                      q90=round(float(np.percentile(e, 90)), 4))
    res["detected_vs_calculated_mean_point_error_over_iod"] = err
    # registered reading (A10): typicality, detected, R4 vs R3, pooled engines, is_val dropped
    r = [x for x in rows if x["kind"] == "detected" and x["stat"] == "iss" and x["engine"] == "pooled" and
         x["contrast"] == "R4 vs R3" and x["is_val_dropped"] == 1]
    if r:
        a = r[0]["auc"]
        res["H_new_2_reading"] = dict(auc=a, ci=[r[0]["lo"], r[0]["hi"]],
                                      reading="supported (>= 0.65)" if a >= 0.65 else
                                      ("falsified (< 0.60): the landmark number stays a calculation" if a < 0.60 else
                                       "in between (0.60 to 0.65)"))
    K.write_csv(K.RES / "typ_detected.csv", rows)
    json.dump(res, open(K.RES / "typ_detected.json", "w"), indent=1, default=str)
    print(json.dumps(res.get("H_new_2_reading"), indent=1))


if __name__ == "__main__":
    main()
