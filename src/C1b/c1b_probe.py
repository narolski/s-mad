"""C1b step 3: validate the C1 expression probe on aligned morphs whose expression is in the file name
(corrected MAD22 FaceMorpher, MIPGAN-I, MIPGAN-II, OpenCV, Webmorph; MorDIFF), then correct the probe's
smile-like rate on FRLL-Morphs x5 and DiM x6 for misclassification (Rogan-Gladen) with a bootstrap interval.
Features and fit are the C1 ones, imported unchanged (src/C_cue_checks/c_checks.py, probe_check.py); no image is written.
Run: /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/C1b/c1b_probe.py [--smoke]
"""
import json, pathlib, sys
from multiprocessing import Pool
import numpy as np
from scipy.stats import beta

SMOKE = "--smoke" in sys.argv
sys.argv = [a for a in sys.argv if a != "--smoke"]          # c_checks reads --smoke itself; keep its full cell lists
sys.path.insert(0, "/home/narolski/smad-next/src/C_cue_checks")
import c_checks as K  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402

OUT = pathlib.Path("/home/narolski/smad-next/experiments/C1b")
VAL = ("MAD22c/FaceMorpher", "MAD22c/MIPGAN_I", "MAD22c/MIPGAN_II", "MAD22c/OpenCV", "MAD22c/Webmorph", "MorDIFF")
TGT = [f"FRLL-Morphs/{f}" for f in K.FRLLM] + [f"DiM/{f}" for f in K.DIM]
REF = {"landmark": ("MAD22c/FaceMorpher", "MAD22c/OpenCV", "MAD22c/Webmorph"), "mipgan": ("MAD22c/MIPGAN_I", "MAD22c/MIPGAN_II"), "mordiff": ("MorDIFF",)}
MAP = {**{f"FRLL-Morphs/{f}": "landmark" for f in ("amsl", "facemorpher", "opencv", "webmorph")}, "FRLL-Morphs/stylegan": "mipgan",
       **{f"DiM/{f}": "mordiff" for f in K.DIM}}
B = 50 if SMOKE else 10000
rng = np.random.default_rng(20261111)


def feat(paths):
    with Pool(6) as pool:
        R = pool.map(K.stats_job, [(str(p), "al") for p in paths], chunksize=16)
    bad = [r["path"] for r in R if "error" in r]
    assert not bad, bad[:3]
    return np.array([r["mouth"] for r in R])


def cp(k, n):
    return [0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1)), 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))]


def main():
    C = K.cells()
    gb = C["FRLL-Morphs/amsl"]["b_al"]
    Xg = feat(gb)
    yg = np.array([K.persons(p.name)[1][0] == "08" for p in gb]).astype(int)
    probe = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)).fit(Xg, yg)
    out = {"probe": "C1 probe: StandardScaler + LogisticRegression(C=0.1) on 204 frll_bona lower-face 22x36 thumbnails (label 08)",
           "validation": {}, "targets": {}, "pooled_refs": {}}
    P = {}
    for cn in VAL + tuple(TGT):
        ps = C[cn]["m_al"]
        if SMOKE:
            ps = ps[:4] + ps[-4:]
        P[cn] = (ps, probe.predict_proba(feat(ps))[:, 1])
    for cn in VAL:
        ps, pr = P[cn]
        ee = [K.persons(pathlib.Path(p).name)[1] for p in ps]
        assert all(a == b for a, b in ee), "mixed-expression pair"
        y = np.array([a == "08" for a, _ in ee])
        pred = pr > 0.5
        o = {"n": len(ps), "n_smiling_true": int(y.sum()), "accuracy": float((pred == y).mean()), "accuracy_ci": cp(int((pred == y).sum()), len(y)),
             "flagged_share": float(pred.mean())}
        if y.any():
            o["sensitivity"] = float(pred[y].mean()); o["sensitivity_ci"] = cp(int(pred[y].sum()), int(y.sum()))
        if (~y).any():
            o["specificity"] = float((~pred[~y]).mean()); o["specificity_ci"] = cp(int((~pred[~y]).sum()), int((~y).sum()))
        if y.any() and (~y).any():
            o["auc"] = K.auc(pr[y], pr[~y])
            bt = [K.auc(rng.choice(pr[y], y.sum()), rng.choice(pr[~y], (~y).sum())) for _ in range(min(B, 2000))]
            o["auc_ci"] = [float(np.percentile(bt, 2.5)), float(np.percentile(bt, 97.5))]
        out["validation"][cn] = o
        print(cn, json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in o.items()}), flush=True)
    # pooled reference sensitivity / specificity per morph type
    ref = {}
    for t, cns in REF.items():
        pos = np.concatenate([P[c][1][np.array([K.persons(pathlib.Path(p).name)[1][0] == "08" for p in P[c][0]])] for c in cns]) > 0.5
        neg = np.concatenate([P[c][1][np.array([K.persons(pathlib.Path(p).name)[1][0] == "03" for p in P[c][0]])] for c in cns]) > 0.5
        ref[t] = (pos, neg)
        out["pooled_refs"][t] = {"families": cns, "n_smiling": int(len(pos)), "sensitivity": float(pos.mean()), "n_neutral": int(len(neg)),
                                 "specificity": float(1 - neg.mean()), "accuracy": float((pos.sum() + (~neg).sum()) / (len(pos) + len(neg)))}
    for cn in TGT:
        ps, pr = P[cn]
        pos, neg = ref[MAP[cn]]
        r = (pr > 0.5).mean()

        def rg(r_, se, fp):
            return float(np.clip((r_ - fp) / max(se - fp, 1e-9), 0, 1))
        pt = rg(r, pos.mean(), neg.mean())
        bt = np.array([rg((rng.random(len(pr)) < r).mean(), rng.choice(pos, len(pos)).mean(), rng.choice(neg, len(neg)).mean()) for _ in range(B)])
        lo, hi = float(np.percentile(bt, 2.5)), float(np.percentile(bt, 97.5))
        o = {"n": len(ps), "ref": MAP[cn], "flagged_share": float(r), "flagged_ci": cp(int((pr > 0.5).sum()), len(pr)), "mean_p_smiling": float(pr.mean()),
             "corrected_smiling_share": pt, "ci": [lo, hi]}
        if cn.startswith("FRLL-Morphs"):
            o["neutral_only_status"] = "supported" if hi <= 0.10 else "not supported"
        out["targets"][cn] = o
        print(cn, json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in o.items()}), flush=True)
    if SMOKE:
        print("smoke ok")
        return
    json.dump(out, open(OUT / "c1b_probe.json", "w"), indent=1)


if __name__ == "__main__":
    main()
