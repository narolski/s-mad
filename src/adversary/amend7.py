"""ADV amendment 7: floors and same-data learner for XF1 (FFHQ hold-out hosts: H, FM(H,H), FM(H,B)).
python3 -I amend7.py   (features, floors, region floors, alternative bootstraps, learner per-row scores)
No network score is read."""
import csv
import hashlib
import json
import sys
import types

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/adversary")
import contrasts as C  # noqa: E402
import feats as F  # noqa: E402
import floor as FL  # noqa: E402
import run_floors as RF  # noqa: E402

NAMES = ("xf1_FMHB_vs_FMHH", "xf1_FMHH_vs_H")


def ensure_features():
    assert hashlib.sha256(open(C.XF1, "rb").read()).hexdigest() == C.XF1_SHA
    R = C.rows(C.XF1)
    for r in R:                                    # per-row file hashes of the registered rows
        assert hashlib.sha256(open(C.resolve(r["path"]), "rb").read()).hexdigest() == r["sha256"], r["id"]
    paths = sorted({C.resolve(r["path"]) for r in R})
    f1, f2 = RF.OUT / "feats" / "xf1.npz", RF.OUT / "feats_regional" / "xf1.npz"
    if not f1.exists():
        np.savez(f1, paths=np.array(paths), X=F.compute(paths, workers=2), names=np.array(F.names()))
    if not f2.exists():
        np.savez(f2, paths=np.array(paths), X=F.compute_regional(paths, workers=2), names=np.array(F.REGION_NAMES))
    RF._FE.clear()
    RF._RG.clear()


def boot(s, y, g, n=2000, seed=20261114):
    rng = np.random.default_rng(seed)
    ug = np.unique(g)
    idx = {k: np.where(g == k)[0] for k in ug}
    out = []
    for _ in range(n):
        ii = np.concatenate([idx[k] for k in rng.choice(ug, len(ug), replace=True)])
        if 0 < y[ii].sum() < len(ii):
            out.append(FL.auc(s[ii], y[ii]))
    return [float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))]


def alt_bootstraps():
    """Printed beside the binding interval: for FMHB vs FMHH (binding unit = the 12 pairing components) a host-level
    bootstrap; for FMHH vs H (binding unit = host, no partner involved) a cell-level bootstrap."""
    cell = {r["id"]: r["cell"] for r in C.rows(C.XF1)}
    host = {r["id"]: r["host"] for r in C.rows(C.XF1)}
    out = {}
    for n in NAMES:
        R = list(csv.DictReader(open(RF.FDIR / f"{n}_heldout.csv")))
        rep = json.loads((RF.FDIR / f"{n}.json").read_text())
        y = np.array([int(r["label"]) for r in R])
        alt = host if n == "xf1_FMHB_vs_FMHH" else cell
        g = np.array([hash(alt[r["id"]]) % (2 ** 31) for r in R])
        res = {}
        for key, col in (("floor", rep["floor"]["model"]), ("nuisance_floor", "nu_" + rep["nuisance_floor"]["model"])):
            s = np.array([float(r[col]) for r in R])
            res[key] = dict(auc=FL.auc(s, y), ci_alt=boot(s, y, g), ci_binding=rep[key]["ci"])
        R2 = list(csv.DictReader(open(RF.FDIR / f"{n}_regional_heldout.csv")))
        reg = json.loads((RF.FDIR / f"{n}_regional.json").read_text())
        for k in ("surround", "face", "file"):
            col = f"{k}_{reg[k + '_floor']['model']}"
            s = np.array([float(r[col]) for r in R2])
            res[k + "_floor"] = dict(auc=FL.auc(s, y), ci_alt=boot(s, y, g), ci_binding=reg[k + "_floor"]["ci"])
        out[n] = dict(binding_unit="12 pairing components (= cell)" if n == "xf1_FMHB_vs_FMHH" else "host (299)",
                      alt_unit="host (299)" if n == "xf1_FMHB_vs_FMHH" else "cell (12)", floors=res)
    (RF.FDIR / "xf1_bootstrap_units.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out), flush=True)


def learner_rows():
    for arm in ("Sb", "A", "B"):
        T = C.train_rows(arm)
        rl = [(r["id"], C.resolve(r["path"]), int(r["label"]), C.train_persons(r)) for r in T]
        X, nm = RF.X_of(rl)
        y = np.array([l for _, _, l, _ in rl])
        Xc, _, keep = FL._clean(X, X[:1])
        med = np.nanmedian(np.where(np.isfinite(X), X, np.nan), 0)
        models = {k: FL._model(k).fit(Xc, y) for k in ("logreg", "gbt")}
        out, summ = [], {}
        for n in NAMES:
            rows_ = C.build(n)
            comp = {r["id"]: int(r["component"]) for r in csv.DictReader(open(RF.FDIR / f"{n}_heldout.csv"))}
            Z, _ = RF.X_of(rows_)
            Z = np.where(np.isfinite(Z), Z, med)[:, keep]
            lr, gb = models["logreg"].decision_function(Z), models["gbt"].predict_proba(Z)[:, 1]
            yy = np.array([l for _, _, l, _ in rows_])
            summ[n] = dict(logreg=FL.auc(lr, yy), gbt=FL.auc(gb, yy),
                           flag_pos_logreg=float(np.mean(lr[yy == 1] > 0)), flag_neg_logreg=float(np.mean(lr[yy == 0] > 0)),
                           flag_pos_gbt=float(np.mean(gb[yy == 1] > 0.5)), flag_neg_gbt=float(np.mean(gb[yy == 0] > 0.5)))
            for k, (i, _, l, _) in enumerate(rows_):
                out.append([n, i, l, comp[i], repr(float(lr[k])), repr(float(gb[k]))])
        with open(RF.FDIR / f"xf1_transfer_{arm}_rows.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["contrast", "id", "label", "component", "logreg", "gbt"])
            w.writerows(out)
        (RF.FDIR / f"xf1_transfer_{arm}.json").write_text(json.dumps(dict(arm=arm, n_train=len(y), summary=summ),
                                                                       indent=1))
        print(arm, json.dumps(summ), flush=True)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    ensure_features()
    RF.cmd_floors(types.SimpleNamespace(only=list(NAMES), stage=0))
    RF.cmd_regionfloors(types.SimpleNamespace(only=list(NAMES)))
    alt_bootstraps()
    learner_rows()
