"""PD1 landmark: mean patch tokens from the alpha-field probe's (AF0) token caches, read only.

For each AF0 cache /mnt/t7/smad_next/AF0/feat/<backbone>/<name>.tokens.npy (float16, (N, T, 1024), patch tokens after
the final norm) that is complete (<name>.done == N), the mean over the T patch tokens is written to
OUT/feat/<backbone>/af0_<name>_mean.npz (ids, mean float32). Read in chunks (memory-safe).

  python3 -I af0_means.py dinov3_512 ar1 af0_w1 af0_w2 bench_s h1 ar1g
"""
import json
import pathlib
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pd1_common as K  # noqa: E402


def main():
    bb, names = sys.argv[1], sys.argv[2:]
    od = K.OUT / "feat" / bb
    od.mkdir(parents=True, exist_ok=True)
    for n in names:
        d = K.AF0 / "feat" / bb
        out = od / f"af0_{n}_mean.npz"
        if out.exists():
            print("exists", out)
            continue
        try:
            meta = json.load(open(d / f"{n}.meta.json"))
            done = int((d / f"{n}.done").read_text())
        except FileNotFoundError:
            print("missing", bb, n)
            continue
        if done != meta["n"]:
            print("incomplete", bb, n, done, meta["n"])
            continue
        tok = np.load(d / f"{n}.tokens.npy", mmap_mode="r")
        ids = np.load(d / f"{n}.ids.npy")
        t0 = time.time()
        M = np.zeros((len(ids), tok.shape[2]), np.float32)
        for i in range(0, len(ids), 64):
            M[i:i + 64] = tok[i:i + 64].astype(np.float32).mean(1)
        np.savez(out, ids=ids, mean=M)
        print("done", bb, n, M.shape, f"{time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
