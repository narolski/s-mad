"""Contact sheet per backbone: 20 validation images (6 gradient, 6 bump, 2 u25, 2 u50, 2 zero-field, 2 photos; fixed
seed), each as image | true per-patch target | predicted per-patch map (same colour scale 0..0.5), face hull outlined.
  python3 -I sheets.py --backbone dinov3_512 --tag full --head ridge --lists af0_w1,af0_w2
"""
import argparse
import pathlib
import random
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbone", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--head", default="ridge")
    ap.add_argument("--lists", default="af0_w1")
    ap.add_argument("--target", default="alpha")
    a = ap.parse_args()
    import cv2
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    g = L.GRID[a.backbone]
    items = []
    for n in a.lists.split(","):
        z = np.load(L.OUT / "heads" / a.backbone / a.tag / f"pred_{a.head}_{n}.npz")
        pr = L.prep(n, g)
        R = L.rows(n)
        idx = {r["id"]: i for i, r in enumerate(R)}
        for k, iid in enumerate(z["ids"]):
            r = R[idx[iid]]
            if r["cell"] == "val":
                items.append((r, z["patch"][k].astype(np.float32), pr["target"][idx[iid]], pr["face"][idx[iid]]))
    rng = random.Random(401)
    pick = []
    for f, k in (("grad", 6), ("bump", 6), ("u25", 2), ("u50", 2), ("zero", 2), ("photo", 2)):
        c = [it for it in items if it[0]["rung"] == f]
        pick += rng.sample(c, min(k, len(c)))
    fig, ax = plt.subplots(len(pick) // 4 + (len(pick) % 4 > 0), 12, figsize=(30, 2.6 * (len(pick) // 4 + 1)))
    ax = np.atleast_2d(ax)
    for j, (r, p, t, fc) in enumerate(pick):
        row, col = divmod(j, 4)
        im = cv2.imread(r["path"])[:, :, ::-1]
        ax[row, 3 * col].imshow(im)
        ax[row, 3 * col].set_title(f"{r['rung']} {r['tool']}", fontsize=8)
        ax[row, 3 * col + 1].imshow(t.reshape(g, g), vmin=0, vmax=0.5, cmap="viridis")
        ax[row, 3 * col + 1].contour(fc.reshape(g, g) >= L.FACE_MIN, levels=[0.5], colors="w", linewidths=0.6)
        ax[row, 3 * col + 1].set_title("true a", fontsize=8)
        ax[row, 3 * col + 2].imshow(p.reshape(g, g), vmin=0, vmax=0.5, cmap="viridis")
        ax[row, 3 * col + 2].contour(fc.reshape(g, g) >= L.FACE_MIN, levels=[0.5], colors="w", linewidths=0.6)
        ax[row, 3 * col + 2].set_title(f"pred ({a.head})", fontsize=8)
    for x in ax.flat:
        x.axis("off")
    plt.suptitle(f"AF0 {a.backbone} {a.head} ({a.tag}): validation persons, image | true | predicted", fontsize=11)
    plt.tight_layout()
    out = L.RES / f"contact_{a.backbone}_{a.head}_{a.tag}.png"
    plt.savefig(out, dpi=55)
    print(out)


if __name__ == "__main__":
    main()
