"""Mean-pooled patch tokens (float32, (N, 1024)) next to each full token cache, so the full 512-px DINOv3 caches can be
removed if the author agrees (lead's disk rule, 11 Nov 20:45). Writes feat/<backbone>/<list>.meanpool.npy (+ ids).
  python3 -I pool_tokens.py dinov3_512 af0_w1 af0_w2 af0_h ar1 bench_s h1 ar1g ladsoft
"""
import sys
import pathlib

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402
import heads as HD  # noqa: E402


def main():
    bb = sys.argv[1]
    for n in sys.argv[2:]:
        d = L.OUT / "feat" / bb
        out = d / f"{n}.meanpool.npy"
        if out.exists():
            continue
        tok, ids, done = L.load_tokens(bb, n)
        assert done == len(ids)
        m = HD.pooled_gpu(tok, done, "cuda").astype(np.float32)
        np.save(out, m)
        print(n, m.shape, flush=True)


if __name__ == "__main__":
    main()
