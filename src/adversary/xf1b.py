"""ADV amendment 8: the XF1 revision-b gate and floors. Rows /mnt/t7/smad_next/XF1/xf1b_rows.csv (sha256 asserted;
each image's sha256 checked against the row; image = the `src` column). Contrast: klass FMHB (1) against klass WARP
(0), per form ("face", "whole"); rows selected by klass and form, never by label. Cross-fitting unit: `component`;
bootstrap unit: `block` (2,000 draws, numpy default_rng(20261120)). No network score is read.
  python3 -I xf1b.py"""
import csv
import hashlib
import json
import sys

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/adversary")
import contrasts as C  # noqa: E402
import feats as F  # noqa: E402
import floor as FL  # noqa: E402
import run_floors as RF  # noqa: E402

ROWS = "/mnt/t7/smad_next/XF1/xf1b_rows.csv"
SHA = "4adcf914fba651f3b1b1ccfc5ea4b3e03155357aa5c84804180513da5925b271"


def load():
    assert hashlib.sha256(open(ROWS, "rb").read()).hexdigest() == SHA, "xf1b_rows.csv changed"
    R = list(csv.DictReader(open(ROWS)))
    for r in R:
        assert hashlib.sha256(open(r["src"], "rb").read()).hexdigest() == r["sha256"], r["id"]
    return R


def ensure_features(R):
    paths = sorted({r["src"] for r in R})
    f1, f2 = RF.OUT / "feats" / "xf1b.npz", RF.OUT / "feats_regional" / "xf1b.npz"
    if not f1.exists():
        np.savez(f1, paths=np.array(paths), X=F.compute(paths, workers=2), names=np.array(F.names()))
    if not f2.exists():
        np.savez(f2, paths=np.array(paths), X=F.compute_regional(paths, workers=2), names=np.array(F.REGION_NAMES))
    RF._FE.clear()
    RF._RG.clear()


def bboot(s, y, b, n=2000, seed=20261120):
    rng = np.random.default_rng(seed)
    ub = np.unique(b)
    idx = {k: np.where(b == k)[0] for k in ub}
    out = []
    for _ in range(n):
        ii = np.concatenate([idx[k] for k in rng.choice(ub, len(ub), replace=True)])
        if 0 < y[ii].sum() < len(ii):
            out.append(FL.auc(s[ii], y[ii]))
    return [float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))]


def rows_of(R, form):
    sel = [r for r in R if r["form"] == form and r["klass"] in ("FMHB", "WARP")]
    y = np.array([1 if r["klass"] == "FMHB" else 0 for r in sel])
    return sel, y, np.array([int(r["component"]) for r in sel]), np.array([int(r["block"]) for r in sel])


def main():
    R = load()
    ensure_features(R)
    out = dict(rows_sha256=SHA, unit_crossfit="component", unit_bootstrap="block")
    per_row = []
    # (1)-(2) same-data learner: train_Sb (the gate), train_A, train_B
    learners = {}
    for arm in ("Sb", "A", "B"):
        T = C.train_rows(arm)
        rl = [(r["id"], C.resolve(r["path"]), int(r["label"]), C.train_persons(r)) for r in T]
        X, nm = RF.X_of(rl)
        y = np.array([l for _, _, l, _ in rl])
        Xc, _, keep = FL._clean(X, X[:1])
        med = np.nanmedian(np.where(np.isfinite(X), X, np.nan), 0)
        learners[arm] = ({k: FL._model(k).fit(Xc, y) for k in ("logreg", "gbt")}, keep, med)
    for form in ("face", "whole"):
        sel, y, comp, blk = rows_of(R, form)
        rl = [(r["id"], r["src"], int(yy), (r["host"],)) for r, yy in zip(sel, y)]
        X, nm = RF.X_of(rl)
        res = {}
        for arm, (models, keep, med) in learners.items():
            Z = np.where(np.isfinite(X), X, med)[:, keep]
            lr, gb = models["logreg"].decision_function(Z), models["gbt"].predict_proba(Z)[:, 1]
            res[arm] = dict(logreg=FL.auc(lr, y), logreg_ci=bboot(lr, y, blk), gbt=FL.auc(gb, y), gbt_ci=bboot(gb, y, blk),
                            flag_FMHB_logreg=float(np.mean(lr[y == 1] > 0)), flag_WARP_logreg=float(np.mean(lr[y == 0] > 0)))
            for k, r in enumerate(sel):
                per_row.append(["learner_" + arm, form, r["id"], r["klass"], int(y[k]), int(comp[k]), int(blk[k]),
                                repr(float(lr[k])), repr(float(gb[k]))])
        out[f"learner_{form}"] = res
        # (3) in-distribution floors, cross-fitted by component
        rg = RF.regmap()
        Rg = np.stack([rg[p] for _, p, _, _ in rl])
        sets = {"all_cue": X, "surround": Rg[:, [i for i, n in enumerate(F.REGION_NAMES) if n.startswith("SURR:")]],
                "face_box": Rg[:, [i for i, n in enumerate(F.REGION_NAMES) if n.startswith("FACE:")]],
                "file": X[:, [i for i, n in enumerate(nm) if n in RF.FILE_SIZE]]}
        fl = FL.folds(y, comp)
        fres = {}
        for k, Xs in sets.items():
            fres[k] = {}
            for m in ("single", "logreg", "gbt"):
                s, _ = FL.crossfit(Xs, y, comp, m, fl)
                fres[k][m] = dict(auc=FL.auc(s, y), ci=bboot(s, y, blk))
                for j, r in enumerate(sel):
                    per_row.append([f"floor_{k}_{m}", form, r["id"], r["klass"], int(y[j]), int(comp[j]), int(blk[j]),
                                    repr(float(s[j])), ""])
        out[f"floors_{form}"] = fres
    g = out["learner_face"]["Sb"]
    out["gate"] = dict(value=max(g["logreg"], g["gbt"]), model="logreg" if g["logreg"] >= g["gbt"] else "gbt",
                       rule="train_Sb learner on the face-only form; >= 0.90 closes XF1 as not run")
    out["gate"]["closes_xf1"] = bool(out["gate"]["value"] >= 0.90)
    (RF.FDIR / "xf1b_gate_and_floors.json").write_text(json.dumps(out, indent=1))
    with open(RF.FDIR / "xf1b_rows_scores.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "form", "id", "klass", "label", "component", "block", "score", "score_gbt"])
        w.writerows(per_row)
    print(json.dumps(out["gate"]), flush=True)
    print(json.dumps({k: v for k, v in out.items() if k.startswith(("learner", "floors"))}), flush=True)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
