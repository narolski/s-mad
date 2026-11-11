"""Mirror distance (lead's addition 2): no training. Per image, mean over the patches inside the face hull of the L2
distance between the image's patch tokens and the left-right flipped image's tokens (feat.py --flip):
  content-aligned (primary)  : token (i, j) vs flipped-image token (i, n-1-j)  -- same image content, mirrored
  position-aligned (second)  : token (i, j) vs flipped-image token (i, j)      -- left half vs mirrored right half
AUC (higher rung positive) for R2 vs R4, R2w vs R4, R3 vs R4 per tool (landmark ladder, both pools), FRLL R0 vs R1
(native vs E7 frames per tool), and the benchmark cells (morph vs native / E7), with AR1's person bootstrap.
Falsifier (lead): no value for landmark morphs if R2 vs R4 < 0.60; not history-blind if FRLL R0 vs R1 > 0.60.
  python3 -I mirror.py --backbone clip224
"""
import argparse
import collections
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402


def scores(bb, name, k):
    M = L.load_mirror(bb, name)
    tok, ids, done = L.load_tokens(bb, name)
    face = L.prep(name, L.GRID[bb])["face"][:done] >= L.FACE_MIN
    s = np.array([M[i, :, k].astype(np.float32)[face[i]].mean() for i in range(done)])
    R = L.rows(name)[:done]
    return R, s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbone", required=True)
    a = ap.parse_args()
    res = {}
    for k, kind in ((0, "content_aligned"), (1, "position_aligned")):
        out = {}
        R, s = scores(a.backbone, "ar1", k)
        G = collections.defaultdict(lambda: ([], []))
        for r, v in zip(R, s):
            G[(r["cell"], r["tool"], r["rung"])][0].append(float(v))
            G[(r["cell"], r["tool"], r["rung"])][1].append((r["p1"], r["p2"]) if r["p1"] != r["p2"] else (r["p1"],))
        for cell in ("frgcferet", "frll"):
            for tool in ("facemorpher", "opencv"):
                for name, pos, neg in (("R2vsR4", "R4", "R2"), ("R2wvsR4", "R4", "R2w"), ("R3vsR4", "R4", "R3"),
                                       ("R0vsR4", "R4", "R0"), ("R3mvsR4", "R4", "R3m")):
                    P = G[(cell, tool, pos)]
                    N = G[(cell, "none", "R0")] if neg == "R0" else G[(cell, tool, neg)]
                    if len(P[0]) > 4 and len(N[0]) > 4:
                        au, ci = L.auc_ci(P[0], P[1], N[0], N[1])
                        out[f"{cell}/{tool}/{name}"] = dict(auc=round(au, 4), folded=round(max(au, 1 - au), 4),
                                                            ci=[round(x, 4) for x in ci], n=[len(P[0]), len(N[0])])
        if (L.OUT / "feat" / a.backbone / "bench_s.mirror.npy").exists():
            R, s = scores(a.backbone, "bench_s", k)
            B = collections.defaultdict(lambda: ([], []))
            for r, v in zip(R, s):
                B[(r["cell"], r["rung"])][0].append(float(v))
                B[(r["cell"], r["rung"])][1].append((r["p1"], r["p2"]) if r["p1"] != r["p2"] else (r["p1"],))
            n0 = B[("frllm_frll_bona", "native")]
            for fam in ("opencv", "facemorpher", "amsl", "webmorph"):
                e7 = B[(f"frllm_{fam}", "e7")]
                m = B[(f"frllm_{fam}", "morph")]
                for name, P, N in (("FRLL_R0vsR1", e7, n0), ("morph_vs_native", m, n0), ("morph_vs_e7", m, e7)):
                    if len(P[0]) > 4 and len(N[0]) > 4:
                        au, ci = L.auc_ci(P[0], P[1], N[0], N[1])
                        out[f"frllm_{fam}/{name}"] = dict(auc=round(au, 4), folded=round(max(au, 1 - au), 4),
                                                          ci=[round(x, 4) for x in ci], n=[len(P[0]), len(N[0])])
            n0 = B[("mad22_BonaFide", "native")]
            for fam in ("FaceMorpher", "OpenCV", "Webmorph"):
                e7, m = B[(f"mad22_{fam}", "e7")], B[(f"mad22_{fam}", "morph")]
                for name, P, N in (("R0vsR1", e7, n0), ("morph_vs_native", m, n0), ("morph_vs_e7", m, e7)):
                    if len(P[0]) > 4 and len(N[0]) > 4:
                        au, ci = L.auc_ci(P[0], P[1], N[0], N[1])
                        out[f"mad22_{fam}/{name}"] = dict(auc=round(au, 4), folded=round(max(au, 1 - au), 4),
                                                          ci=[round(x, 4) for x in ci], n=[len(P[0]), len(N[0])])
        res[kind] = out
    json.dump(res, open(L.RES / f"mirror_{a.backbone}.json", "w"), indent=1)
    for kind, out in res.items():
        print(kind)
        for k2, v in out.items():
            print("  ", k2, v)


if __name__ == "__main__":
    main()
