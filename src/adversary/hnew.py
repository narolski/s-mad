"""ADV amendment 4 (descriptive): H-new-1 (F27 + BLEND floor on lcomb_bal) and H-new-3 (chroma-only vs luma-only
floors on R4 vs R3 within BD1 D quintiles). Writes floors/hnew1_lcomb_bal.json and floors/hnew3_<contrast>.json."""
import json
import sys

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/adversary")
import contrasts as C  # noqa: E402
import feats as F  # noqa: E402
import floor as FL  # noqa: E402
import run_floors as RF  # noqa: E402

CHROMA = ["FACE:chroma_cb", "FACE:chroma_cr", "FACE:resid_corr_rg", "FACE:resid_corr_gb", "F27:sat_face"]
LUMA = ["FACE:noise_std_Y", "FACE:lapvar", "FACE:grad_energy", "FACE:resid_kurt", "FACE:mean_Y", "FACE:std_Y",
        "FACE:band0", "FACE:band1", "FACE:band2", "FACE:band3"]


def full(rl):
    X, nm = RF.X_of(rl)
    rg = RF.regmap()
    R = np.stack([rg[p] for _, p, _, _ in rl])
    return np.c_[X, R], nm + F.REGION_NAMES


def fit(X, y, pers):
    g = FL.components(pers)
    fl = FL.folds(y, g)
    sc, auc = {}, {}
    for k in ("single", "logreg", "gbt"):
        s, _ = FL.crossfit(X, y, g, k, fl)
        sc[k], auc[k] = s, FL.auc(s, y)
    return sc, auc


def main():
    rl = C.build("lcomb_bal")
    X, nm = full(rl)
    y = np.array([l for _, _, l, _ in rl])
    cols = [i for i, n in enumerate(nm) if n.startswith(("F27:", "BLEND:"))]
    _, a = fit(X[:, cols], y, [p for *_, p in rl])
    best = max(a.values())
    rep = dict(hypothesis="H-new-1", rows=len(y), families=["F27", "BLEND"], auc=a, best=best,
               reading="supported" if best >= 0.90 else ("falsified" if best <= 0.80 else "between the bars"))
    (RF.FDIR / "hnew1_lcomb_bal.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep), flush=True)
    for n in ("ri_R4_vs_R3", "test_cv_R4_vs_R3"):
        rl = C.build(n)
        X, nm = full(rl)
        y = np.array([l for _, _, l, _ in rl])
        ids = [i for i, *_ in rl]
        out = dict(hypothesis="H-new-3", contrast=n)
        for name, fs in (("chroma", CHROMA), ("luma", LUMA)):
            cols = [nm.index(f) for f in fs]
            sc, a = fit(X[:, cols], y, [p for *_, p in rl])
            out[name] = dict(overall=a, within_D=RF.within_d(ids, y, sc, rows_d=True))
        cw = max(v for k, v in out["chroma"]["within_D"].items() if k in ("single", "logreg", "gbt"))
        lw = max(v for k, v in out["luma"]["within_D"].items() if k in ("single", "logreg", "gbt"))
        out["chroma_within_D_best"], out["luma_within_D_best"] = cw, lw
        out["reading"] = "supported" if (cw >= 0.70 and lw <= 0.62) else "falsified"
        (RF.FDIR / f"hnew3_{n}.json").write_text(json.dumps(out, indent=1))
        print(json.dumps({k: out[k] for k in ("contrast", "chroma_within_D_best", "luma_within_D_best", "reading")}),
              flush=True)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
