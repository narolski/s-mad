"""Wave 3, control 6: pooling audit from saved patch predictions on genuine photos.
For FRLL native frames, FRLL E7 frames (opencv, facemorpher) and AR1 R0 / R2w: where the top tenth of in-hull patches
lies (share inside the inner-face hull = eyebrows, eyes, nose, mouth; share in the outer ring of the face hull), and a
heat map of how often each patch is in the top tenth (PNG). History shifts under mean, top-tenth and median pooling are
in metrics_<bb>_<tag>.json (keys score, score_top10, score_median).
  python3 -I pooling_audit.py --backbone dinov3_512 --tag full --head mlp_s401
"""
import argparse
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbone", required=True)
    ap.add_argument("--tag", default="full")
    ap.add_argument("--head", default="mlp_s401")
    a = ap.parse_args()
    g = L.GRID[a.backbone]
    groups = {"FRLL native": ("bench_s", lambda r: r["cell"] == "frllm_frll_bona"),
              "FRLL E7 opencv": ("bench_s", lambda r: r["cell"] == "frllm_opencv" and r["rung"] == "e7"),
              "FRLL E7 facemorpher": ("bench_s", lambda r: r["cell"] == "frllm_facemorpher" and r["rung"] == "e7"),
              "AR1 R0": ("ar1", lambda r: r["cell"] == "frgcferet" and r["rung"] == "R0"),
              "AR1 R2w opencv": ("ar1", lambda r: r["cell"] == "frgcferet" and r["tool"] == "opencv" and r["rung"] == "R2w"),
              "AR1 R4 opencv": ("ar1", lambda r: r["cell"] == "frgcferet" and r["tool"] == "opencv" and r["rung"] == "R4")}
    out, heat = {}, {}
    for name, (lst, fn) in groups.items():
        z = np.load(L.OUT / "heads" / a.backbone / a.tag / f"pred_{a.head}_{lst}.npz")
        R = L.rows(lst)
        pr = L.prep(lst, g)
        inner = L.prep_inner(lst, g)
        idx = {r["id"]: i for i, r in enumerate(R)}
        sh_in, sh_ring, H = [], [], np.zeros(g * g)
        for k, iid in enumerate(z["ids"]):
            r = R[idx[iid]]
            if not fn(r):
                continue
            m = pr["face"][idx[iid]] >= L.FACE_MIN
            mi = inner[idx[iid]] >= L.FACE_MIN
            p = z["patch"][k].astype(np.float32)
            cand = np.where(m)[0]
            top = cand[np.argsort(p[cand])[-max(1, int(round(0.1 * len(cand)))):]]
            sh_in.append(mi[top].mean())
            sh_ring.append((~mi[top]).mean())
            H[top] += 1
        out[name] = dict(n=len(sh_in), share_top10_in_inner_face=round(float(np.mean(sh_in)), 3),
                         share_top10_in_outer_ring=round(float(np.mean(sh_ring)), 3),
                         inner_share_of_hull_patches=round(float(np.mean(
                             [(inner[idx[i]] >= L.FACE_MIN)[pr["face"][idx[i]] >= L.FACE_MIN].mean()
                              for i in z["ids"] if fn(R[idx[i]])])), 3))
        heat[name] = H / max(len(sh_in), 1)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, len(heat), figsize=(3 * len(heat), 3.2))
    for x, (k, v) in zip(ax, heat.items()):
        x.imshow(v.reshape(g, g), cmap="magma", vmin=0, vmax=max(1e-6, max(h.max() for h in heat.values())))
        x.set_title(k, fontsize=8)
        x.axis("off")
    plt.suptitle(f"share of images in which a patch is in the top tenth ({a.backbone}, {a.head})", fontsize=9)
    plt.tight_layout()
    plt.savefig(L.RES / f"pooling_top10_heat_{a.backbone}_{a.head}.png", dpi=70)
    json.dump(out, open(L.RES / f"wave3_pooling_{a.backbone}_{a.head}.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
