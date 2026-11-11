"""Graded mixing set (AR1's AR2 FaceMorpher library set, m = 0, 0.1, ..., 0.5 on the same 300 hosts): mean image score
per level, AUC of each level against m = 0 (AR1's person bootstrap), Page trend test over hosts (scipy).
  python3 -I graded.py clip224:full clip224:w2_alpha ...
"""
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402
import metrics as M  # noqa: E402


def main():
    out = {}
    R = M.rows("ar1g")
    for spec in sys.argv[1:]:
        bb, tag = spec.split(":")
        d = L.OUT / "heads" / bb / tag
        for p in sorted(d.glob("pred_*_ar1g.npz")):
            h = p.name[5:-9]
            S = dict(zip(np.load(p)["ids"], np.load(p)["score"]))
            levels = sorted({R[i]["rung"] for i in S})
            means = {k: round(float(np.mean([S[i] for i in S if R[i]["rung"] == k])), 4) for k in levels}
            aucs = {}
            for k in levels[1:]:
                c = M.contrast(S, "ar1g", lambda r, k=k: r["rung"] == k, lambda r: r["rung"] == "m0.0", floor=False)
                aucs[k] = c and [c["auc"], c["ci"]]
            from scipy.stats import page_trend_test
            hosts = sorted({R[i]["p1"] for i in S})
            Mx = {(R[i]["p1"], R[i]["rung"]): float(S[i]) for i in S}
            data = np.array([[Mx[(hh, k)] for k in levels] for hh in hosts if all((hh, k) in Mx for k in levels)])
            pt = page_trend_test(data)
            out[f"{bb}/{tag}/{h}"] = dict(mean_by_level=means, auc_vs_m0=aucs, page_L=float(pt.statistic),
                                          page_p=float(pt.pvalue), n_hosts=len(data))
            print(bb, tag, h, means, {k: v[0] for k, v in aucs.items() if v}, "Page p", f"{pt.pvalue:.2e}", flush=True)
    json.dump(out, open(L.RES / "graded_ar1g.json", "w"), indent=1)


if __name__ == "__main__":
    main()
