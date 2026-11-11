"""PN1: install the DINOv3 means extracted on Athena (smoke job, featx) and run the 64-image platform check.
  python3 -I postfeatx.py install      # hash check, unpack to /mnt/t7/smad_next/PN1/featx_out/, copy means (not eq64)
  python3 -I postfeatx.py check        # eq64: A100 means against the DGX means (PD1 / AF0 caches); head-score check
Registered tolerance (prereg section 3): head probability difference at most 0.01 on every one of the 64 images, with
the named B0 DINOv3 head; else the Athena-extracted DINOv3 reads are marked "platform-mixed".
"""
import hashlib
import json
import pathlib
import shutil
import sys
import tarfile

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pn1lib as K  # noqa: E402

T = K.PN1 / "featx_out.tar"
D = K.PN1 / "featx_out"
FD = K.PN1 / "feat" / "dinov3_512"


def install():
    h = hashlib.sha256(T.read_bytes()).hexdigest()
    assert h == (K.PN1 / "featx_out.tar.sha256").read_text().split()[0], "featx_out sha256"
    if not D.exists():
        with tarfile.open(T) as t:
            t.extractall(D)
    src = D / "out" / "dinov3_512"
    for f in sorted(src.glob("*.mean.npy")):
        n = f.name[: -len(".mean.npy")]
        if n == "eq64":
            continue
        for ext in (".mean.npy", ".ids.npy", ".meta.json"):
            shutil.copy2(src / (n + ext), FD / (f"ath_{n}" + ext))
        print("installed", n, np.load(f).shape)


def check():
    src = D / "out" / "dinov3_512"
    ids = [str(i) for i in np.load(src / "eq64.ids.npy")]
    A = np.load(src / "eq64.mean.npy")
    idx, X, _ = K.load_features("dinov3_512", want=set(ids))
    G = X[[idx[i] for i in ids]]
    res = dict(n=len(ids), feat_max_abs_diff=float(np.abs(A - G).max()), feat_mean_abs=float(np.abs(G).mean()),
               corr=float(np.corrcoef(A.ravel(), G.ravel())[0, 1]))
    hz = np.load(K.PN1 / "tier0" / "dinov3_512" / "B0_s401_head.npz") if (K.PN1 / "tier0" / "dinov3_512" /
                                                                            "B0_s401_head.npz").exists() else None
    if hz is not None:
        w, b, mu, sd = hz["coef"], hz["intercept"], hz["mean"], hz["scale"]
        pa = 1 / (1 + np.exp(-(((A - mu) / sd) @ w + b)))
        pg = 1 / (1 + np.exp(-(((G - mu) / sd) @ w + b)))
        res.update(head_prob_max_abs_diff=float(np.abs(pa - pg).max()), head_logit_max_abs_diff=float(
            np.abs(np.log(pa / (1 - pa)) - np.log(pg / (1 - pg))).max()), within_tolerance=bool(np.abs(pa - pg).max() <= 0.01))
    K.dump(res, K.RES / "featx_platform_check.json")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    {"install": install, "check": check}[sys.argv[1]]()
