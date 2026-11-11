"""SM1 amendment A1.3 pool-cue check: can the Part 3 head recipe tell the genuine-render pool (os25k_bf_t) from the
morph-source pool (os25k_m_t, non-contributors) on frozen features? 5,000 + 5,000 renders, 5-fold, seed 401,
out-of-fold AUC (0.5 = the two pools look alike to the head; they were split at random by SMDD).

  python3 -I pool_cue.py -> RES/pool_cue.json
"""
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import heads as H  # noqa: E402
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402


def main():
    import torch
    torch.set_num_threads(1)
    H.DEV = "cuda" if torch.cuda.is_available() else "cpu"
    _, fb = H.load("train_bf")
    _, fs = H.load("train_srcm_cue")
    rng = np.random.default_rng(401)
    fb = fb[rng.choice(len(fb), size=len(fs), replace=False)]
    X = np.concatenate([fb, fs])
    y = np.r_[np.zeros(len(fb)), np.ones(len(fs))]
    fold = rng.permutation(len(X)) % 5
    oof = np.zeros(len(X))
    for k in range(5):
        tr, te = fold != k, fold == k
        W, b, _ = H.train(X[tr & (y == 0)], X[tr & (y == 1)], 401, False)
        oof[te] = X[te] @ W + b
    auc = float(S.wauc(oof[y == 1], oof[y == 0], np.ones((1, int(y.sum()))), np.ones((1, int((1 - y).sum()))))[0])
    out = dict(n_bf=len(fb), n_srcm=len(fs), oof_auc=auc)
    json.dump(out, open(K.RES / "pool_cue.json", "w"), indent=1)
    print(out)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
