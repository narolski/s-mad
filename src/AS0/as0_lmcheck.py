"""Mirror-asymmetry test (AS0): check of the landmark sources (no asymmetry statistic).
(a) insightface landmarks detected on 48 AR1 photos (R0) against their .tem files (the record's landmarks);
(b) landmarks detected on 48 AF0 softened copies against the source .tem used for their mask (realignment jitter).
  python3 -I as0_lmcheck.py -> OUT/lmcheck.json (copy in the experiment folder)"""
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import as0_common as K  # noqa: E402
import as0_landmarks as LD  # noqa: E402

items = K.read_csv(K.OUT / "items.csv")
byid = {it["id"]: it for it in items}
app = LD.make_app(2)
out = {}
for name, sel in (("R0_vs_tem", [it for it in items if it["set"] == "L" and it["role"] == "R0"][::11][:48]),
                  ("soft_vs_source_tem", [it for it in items if it["set"] == "Lsoft" and it["aligned"] == "True"][::25][:48])):
    d, dx, ratio = [], [], []
    for it in sel:
        r = LD.detect(app, it["path"])
        if not r or r["n"] == 0:
            continue
        src = it if name == "R0_vs_tem" else byid[it["src"]]
        spec = src["lm"]
        if spec.startswith("tem:"):
            t = K.read_tem(spec[4:])
        else:
            a, b, w = spec[4:].split(";")
            t = (1 - float(w)) * K.read_tem(a) + float(w) * K.read_tem(b)
        lm = r["lm"].astype(np.float64)
        iod = np.linalg.norm(t[K.PUPIL_R] - t[K.PUPIL_L])
        d.append(float(np.linalg.norm(lm - t, axis=1).mean() / iod))
        dx.append(float((lm[:, 0].mean() - t[:, 0].mean())))
        ratio.append(float(np.linalg.norm(lm[K.PUPIL_R] - lm[K.PUPIL_L]) / iod))
    out[name] = dict(n=len(d), mean_point_error_over_iod_median=float(np.median(d)), q90=float(np.percentile(d, 90)),
                     midline_shift_px_median=float(np.median(dx)), midline_shift_px_abs_q90=float(np.percentile(np.abs(dx), 90)),
                     iod_ratio_median=float(np.median(ratio)))
json.dump(out, open(K.OUT / "lmcheck.json", "w"), indent=1)
json.dump(out, open(K.RES / "lmcheck.json", "w"), indent=1)
print(json.dumps(out, indent=1))
