"""C1c: on each registered variant of the 204 FRLL photos, (1) does the C1 probe (fit on frll_bona orig) still order
smiling above neutral within person, (2) does the backdrop / mouth noise difference survive? Read-only decode.
Run: /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/C1c/c1c_variant_probe.py
"""
import csv, json, pathlib, re, sys
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/C1c")
import c1c_files as F  # noqa: E402  (frame_job: region noise + C1 probe feature)
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402
D = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr_data")
OUT = pathlib.Path("/home/narolski/smad-next/experiments/C1c_smiling-half-expression-or-detail")
rows = list(csv.DictReader(open(D / "manifests/eval.csv")))
V = {}
for r in rows:
    if r["label"] == "0" and r["set"] in ("frllm", "mordiff") and (r["family"] in ("frll_bona", "mordiff_bona") or r["variant"] == "resmatch"):
        k = f"resmatch:{r['family']}" if r["variant"] == "resmatch" else f"{r['family']}:{r['variant']}"
        m = re.match(r"^(\d{3})_(\d{2})_", r["path"].rsplit("/", 1)[1])
        V.setdefault(k, {})[m.groups()] = str(D / r["path"])
for r in rows:
    if r["label"] == "0" and r["set"] == "dim" and r["variant"] == "resmatch":
        m = re.match(r"^(\d{3})_(\d{2})_", r["path"].rsplit("/", 1)[1])
        V.setdefault(f"resmatch:{r['family']}", {})[m.groups()] = str(D / r["path"])
order = ["frll_bona:orig", "frll_bona:jpeg50", "frll_bona:blur1", "frll_bona:resample50", "resmatch:facemorpher", "resmatch:amsl", "resmatch:dim_a", "resmatch:mordiff", "mordiff_bona:orig"]
paths = sorted({p for k in order for p in V[k].values()})
with Pool(8) as pool:
    R = {o["path"]: o for o in pool.map(F.frame_job, paths, chunksize=16)}
P = sorted({p for p, e in V["frll_bona:orig"]})
X = np.array([R[V["frll_bona:orig"][(p, e)]]["mouth_feat"] for p in P for e in ("03", "08")]); y = np.array([0, 1] * len(P))
probe = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)).fit(X, y)
out = {}
for k in order:
    G = V[k]
    l3 = probe.decision_function(np.array([R[G[(p, "03")]]["mouth_feat"] for p in P])); l8 = probe.decision_function(np.array([R[G[(p, "08")]]["mouth_feat"] for p in P]))
    o = {"probe_share_08_gt_03": float(np.mean(l8 > l3)), "probe_flags_08": float(np.mean(l8 > 0)), "probe_flags_03": float(np.mean(l3 > 0))}
    for s in ("noise_bg_tl", "noise_bg_tr", "noise_forehead", "noise_mouth"):
        a = np.array([R[G[(p, "03")]][s] for p in P]); b = np.array([R[G[(p, "08")]][s] for p in P]); ok = (a > 0) & (b > 0)
        o[s] = {"share_08_gt_03": float(np.mean(b[ok] > a[ok])), "median_ratio": float(np.median(b[ok] / a[ok])), "median_03": float(np.median(a[ok]))}
    out[k] = o
    print(k, round(o["probe_share_08_gt_03"], 3), round(o["probe_flags_03"], 2), round(o["probe_flags_08"], 2), {s: (round(o[s]["share_08_gt_03"], 2), round(o[s]["median_ratio"], 2), round(o[s]["median_03"], 2)) for s in ("noise_bg_tl", "noise_bg_tr", "noise_forehead", "noise_mouth")}, flush=True)
json.dump(out, open(OUT / "c1c_variant_probe.json", "w"), indent=1)
