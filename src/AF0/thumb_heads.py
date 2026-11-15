"""32-pixel thumbnail baselines on the same tasks (prereg guard), from thumbs.py features (16 x 16 block means).
  thumb_img   : image-level L2 logistic regression (C = 1, standardised) on the flattened 32 x 32 x 3 thumbnail,
                uniform 0.5 (1) vs zero field (0), AF0 training images -- the thumbnail version of baseline (iii)
  thumb_dense : per-patch ridge on the 32 x 32 grid: features = RGB block means of the 3 x 3 neighbourhood (27) and
                the same minus the image's mean RGB (27); target = per-patch mean of a(x) (32 x 32 grid, as DINOv3);
                image score = mean prediction inside the face hull; lambda by 3-fold CV over training hosts
Writes heads/thumb/<tag>/pred_<head>_<list>.npz in heads.py's format.
  python3 -I thumb_heads.py --train af0_w1 --eval af0_w1,ar1 --tag first
"""
import argparse
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402

GRID = [1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0]


def load(n):
    z = np.load(L.OUT / "thumbs" / f"{n}.npz")
    return z["ids"], z["thumb"]


def dense_feats(T):
    P = np.pad(T, ((0, 0), (1, 1), (1, 1), (0, 0)), mode="edge")
    nb = np.concatenate([P[:, dy:dy + 32, dx:dx + 32] for dy in range(3) for dx in range(3)], -1)   # (N,32,32,27)
    rel = nb - np.tile(T.mean((1, 2), keepdims=True), (1, 1, 1, 9))
    return np.concatenate([nb, rel], -1).reshape(len(T), 1024, 54) / 255.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", required=True)
    ap.add_argument("--eval", required=True)
    ap.add_argument("--tag", required=True)
    a = ap.parse_args()
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    od = L.OUT / "heads" / "thumb" / a.tag
    od.mkdir(parents=True, exist_ok=True)
    tr_rows, tr_T, tr_y = [], [], []
    for n in a.train.split(","):
        ids, T = load(n)
        R = L.rows(n)
        pr = L.prep(n, 32)
        assert list(ids) == [r["id"] for r in R]
        for i, r in enumerate(R):
            if r["set"] == "af0" and r["cell"] == "train":
                tr_rows.append(r)
                tr_T.append(T[i])
                tr_y.append(pr["target"][i])
    tr_T, tr_y = np.stack(tr_T), np.stack(tr_y)
    # image-level
    m = np.array([r["rung"] in ("u50", "zero") for r in tr_rows])
    X = tr_T[m].reshape(m.sum(), -1)
    y = np.array([r["rung"] == "u50" for r in np.array(tr_rows)[m]], int)
    sc = StandardScaler().fit(X)
    clf = LogisticRegression(C=1.0, max_iter=5000).fit(sc.transform(X), y)
    # dense ridge, lambda by host-grouped 3-fold CV
    F = dense_feats(tr_T)
    mu, sd = F.reshape(-1, 54).mean(0), F.reshape(-1, 54).std(0) + 1e-6
    hosts = sorted({r["p1"] for r in tr_rows})
    fold = {h: k % 3 for k, h in enumerate(np.random.default_rng(401).permutation(hosts))}
    f = np.array([fold[r["p1"]] for r in tr_rows])
    Z = lambda F_: np.concatenate([(F_.reshape(-1, 54) - mu) / sd, np.ones((F_.size // 54, 1))], 1)  # noqa
    XtX = [None] * 3
    Xty = [None] * 3
    yty = np.zeros(3)
    nn = np.zeros(3)
    for k in range(3):
        Xk, yk = Z(F[f == k]), tr_y[f == k].reshape(-1)
        XtX[k], Xty[k], yty[k], nn[k] = Xk.T @ Xk, Xk.T @ yk, yk @ yk, len(yk)
    tot, toty = sum(XtX), sum(Xty)
    scale = np.trace(tot[:54, :54]) / 54
    Pm = np.eye(55)
    Pm[54, 54] = 0
    cv = []
    for r_ in GRID:
        mse = 0
        for k in range(3):
            w = np.linalg.solve(tot - XtX[k] + r_ * scale * Pm, toty - Xty[k])
            mse += w @ XtX[k] @ w - 2 * w @ Xty[k] + yty[k]
        cv.append(mse / nn.sum())
    lam = GRID[int(np.argmin(cv))]
    w = np.linalg.solve(tot + lam * scale * Pm, toty)
    print("thumb_dense lambda", lam, flush=True)
    for n in a.eval.split(","):
        ids, T = load(n)
        face = L.prep(n, 32)["face"] >= L.FACE_MIN
        np.savez(od / f"pred_thumb_img_{n}.npz", ids=ids,
                 score=clf.decision_function(sc.transform(T.reshape(len(T), -1))))
        P = (Z(dense_feats(T)) @ w).reshape(len(T), 1024)
        np.savez(od / f"pred_thumb_dense_{n}.npz", ids=ids, patch=P.astype(np.float16),
                 score=np.array([p[mm].mean() for p, mm in zip(P, face)]))
    print("done", a.tag)


if __name__ == "__main__":
    main()
