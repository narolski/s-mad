"""Validity checks of R2w and R3m (lead request): pixel difference from H; glintr100 cosine to H and to the independent
reference R (primary pool) for R2w, R3m, R3, R4 of the same hosts. Gate R3m: median cos(R3m, H) >= median cos(R3, H).
  python3 -I verify_variants.py --limit 8 --smoke     (smoke dirs)       python3 -I verify_variants.py   (full)
Writes experiments/AR1/variants_check[_smoke].json and a contact sheet in OUT.
"""
import argparse
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ar1_common as K  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    import cv2
    import fr
    out = {}
    sheet = []
    for pool, pcsv in (("frgcferet", "pool.csv"), ("frll", "pool_frll.csv")):
        rows = list(csv.DictReader(open(K.OUT / pcsv)))[: a.limit or None]
        for tool in ("opencv", "facemorpher"):
            paths = {}
            for r in rows:
                s = r["pid"].replace(":", "_") + ".png"
                base = K.OUT / "img"
                paths[r["pid"]] = dict(
                    H=r["H"], R=r["R"] or None,
                    R2w=str(base / ((("smoke_" + pool) if a.smoke else pool)) / tool / "R2w" / s),
                    R3m=str(base / ((("smoke_" + pool) if a.smoke else pool)) / tool / "R3m" / s),
                    R2wm=str(base / ((("smoke_" + pool) if a.smoke else pool)) / tool / "R2wm" / s),
                    R3=str(base / pool / tool / "R3" / s), R4=str(base / pool / tool / "R4" / s))
            flat = sorted({p for d in paths.values() for p in d.values() if p})
            E, Fd = {}, {}
            for c in ("fr_emb_built.npz", "pool_src_emb.npz", "fr_emb_variants.npz"):
                if (K.OUT / c).exists():
                    z = np.load(K.OUT / c)
                    E.update(zip(z["path"].tolist(), z["emb"]))
                    Fd.update(zip(z["path"].tolist(), z["found"]))
            zf = np.load(K.OUT / "frll_src_emb.npz")
            for st, e, f in zip(zf["stem"].tolist(), zf["emb"], zf["found"]):
                E[str(K.OUT / "frll_src" / f"{st}.png")], Fd[str(K.OUT / "frll_src" / f"{st}.png")] = e, f
            new = [p for p in flat if p not in E]
            if new:
                emb, found = fr.embed_paths(new)
                E.update(zip(new, emb))
                Fd.update(zip(new, found))
                if not a.smoke:
                    old = np.load(K.OUT / "fr_emb_variants.npz") if (K.OUT / "fr_emb_variants.npz").exists() else None
                    P_ = (old["path"].tolist() if old is not None else []) + new
                    np.savez(K.OUT / "fr_emb_variants.npz", path=np.array(P_), emb=np.stack([E[q] for q in P_]),
                             found=np.array([Fd[q] for q in P_]))
            res = {}
            for g in ("R2w", "R2wm", "R3m", "R3", "R4"):
                cH = [float(E[d[g]] @ E[d["H"]]) for d in paths.values() if Fd[d[g]] and Fd[d["H"]]]
                cR = [float(E[d[g]] @ E[d["R"]]) for d in paths.values() if d["R"] and Fd[d[g]] and Fd[d["R"]]]
                mad = [float(np.abs(cv2.imread(d[g]).astype(int) - cv2.imread(d["H"]).astype(int)).mean())
                       for d in paths.values()]
                res[g] = dict(n=len(paths), no_face=int(sum(not Fd[d[g]] for d in paths.values())),
                              cos_H_median=float(np.median(cH)), cos_H_q10=float(np.quantile(cH, 0.1)),
                              cos_R_median=float(np.median(cR)) if cR else None,
                              mean_abs_diff_vs_H_median=float(np.median(mad)), min_mean_abs_diff=float(np.min(mad)),
                              identical_to_H=int(sum(m == 0 for m in mad)))
            res["gate_R3m_cosH_ge_R3"] = bool(res["R3m"]["cos_H_median"] >= res["R3"]["cos_H_median"])
            res["R2w_cosH_vs_R3"] = res["R2w"]["cos_H_median"] - res["R3"]["cos_H_median"]
            out[f"{pool}/{tool}"] = res
            print(pool, tool, json.dumps(res), flush=True)
            d = paths[rows[0]["pid"]]
            sheet.append(np.hstack([cv2.imread(d[g])[::2, ::2] for g in ("H", "R2w", "R2wm", "R3m", "R3", "R4")]))
    json.dump(out, open(K.RES / ("variants_check_smoke.json" if a.smoke else "variants_check.json"), "w"), indent=1)
    cv2.imwrite(str(K.OUT / ("variants_sheet_smoke.png" if a.smoke else "variants_sheet.png")), np.vstack(sheet))


if __name__ == "__main__":
    main()
