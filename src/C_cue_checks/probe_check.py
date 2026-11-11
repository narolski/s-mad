"""Validation of the C1 expression probe on morphs with known expression (MorDIFF and corrected-MAD22 FaceMorpher/OpenCV names)."""
import sys, json, pathlib, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/C_cue_checks")
import c_checks as K
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
C = K.cells()
gb = C["FRLL-Morphs/amsl"]["b_al"]
Xg = np.array([K.stats_job((str(p), "al"))["mouth"] for p in gb]); yg = np.array([K.persons(p.name)[1][0] == "08" for p in gb]).astype(int)
probe = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)).fit(Xg, yg)
out = {}
for cn in ("MorDIFF", "MAD22c/FaceMorpher", "MAD22c/OpenCV", "MAD22c/Webmorph"):
    ps = C[cn]["m_al"]
    X = np.array([K.stats_job((str(p), "al"))["mouth"] for p in ps]); y = np.array([K.persons(pathlib.Path(p).name)[1][0] == "08" for p in ps])
    pr = probe.predict_proba(X)[:, 1]
    out[cn] = {"n": len(ps), "true_smiling_share": float(y.mean()), "probe_frac_gt_0.5": float((pr > 0.5).mean()),
               "auc_probe_vs_true": K.auc(pr[y], pr[~y]) if y.any() and (~y).any() else None,
               "probe_frac_gt_0.5_on_true_smiling": float((pr[y] > 0.5).mean()) if y.any() else None}
    print(cn, out[cn], flush=True)
json.dump(out, open("/home/narolski/smad-next/experiments/C_cue_checks/probe_check.json", "w"), indent=1)
