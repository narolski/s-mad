"""Retrains of released methods (AD5): SelfMAD oracle-epoch diagnostic on Athena (prereg amendment 2).

Scores many SelfMAD weight files on the cached own-preprocessing arrays of the 7,265 FRLL-cell images
(`selfmad_oracle.py cache`, packs/AD5/selfmad_oracle_cache.tar; checked equal to score.py --mode own within 9e-4 in
logit). Network builder: score.py's own-mode builder a41g_score.selfmad_net (a12_released spec selfmad_hrnet_w18,
strict load, 'net.' stripped), from the unpacked RS1 pack (code/smadcvpr, pins checked as in RS1's athena_run.py).
One npz per weight file: id, score (softmax[:, 1]), logit_noTTA (z1 - z0), cropped, weights_sha256.

  python3 -I selfmad_oracle_athena.py ROOT CACHE_DIR OUT_DIR NAME=WEIGHTS [NAME=WEIGHTS ...]
"""
import hashlib
import pathlib
import sys

import numpy as np


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


ROOT, CACHE, OUT = (pathlib.Path(x) for x in sys.argv[1:4])
JOBS = [a.split("=", 1) for a in sys.argv[4:]]
RS1 = ROOT / "code" / "rs1"
sys.path.insert(0, str(RS1))
import ar1_common as K  # noqa: E402

old = K.W46 / "smadcvpr"
K.MC = ROOT / "code"
K.W46 = ROOT / "code"
K.PINS = {K.W46 / "smadcvpr" / p.name: h for p, h in K.PINS.items() if p.parent == old}
K.add_paths(K.MC, K.W46 / "smadcvpr")
for p, h in K.PINS.items():
    assert sha(p) == h, p
import torch  # noqa: E402
import common as C  # noqa: E402
import a12_released as R  # noqa: E402
import a41g_score as S  # noqa: E402

R.np, R.torch, R.C = np, torch, C
m = np.load(CACHE / "meta.npz")
x = np.load(CACHE / "x_u8.npy", mmap_mode="r")
OUT.mkdir(parents=True, exist_ok=True)
for name, w in JOBS:
    model = S.selfmad_net(R, w, torch).eval().cuda()
    logits, scores = [], []
    with torch.no_grad():
        for i in range(0, len(x), 32):
            b = torch.from_numpy(np.asarray(x[i:i + 32]).astype(np.float32) / 255).cuda()
            out = model(b).float()
            scores += out.softmax(1)[:, 1].cpu().tolist()
            logits += (out[:, 1] - out[:, 0]).cpu().tolist()
    np.savez(OUT / f"oracle_{name}.npz", id=m["id"], score=np.array(scores, np.float32),
             score_noTTA=np.array(scores, np.float32), logit_noTTA=np.array(logits, np.float32), cropped=m["cropped"],
             weights_sha256=sha(w))
    print(name, len(logits), flush=True)
