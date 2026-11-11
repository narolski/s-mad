"""PN1: mean patch-token features from the alpha-field probe's token caches (read only):
/mnt/t7/smad_next/AF0/feat/<backbone>/<list>.tokens.npy (N, T, 1024) float16 -> mean over T in float32 ->
/mnt/t7/smad_next/PN1/feat/<backbone>/af0_<list>.mean.npy (N, 1024) float32 + .ids.npy (copied) + .meta.json.
A list is pooled only when its <list>.done equals its row count (complete extraction).
  python3 -I featpool.py clip224:ar1 dinov3_512:ar1 ...
"""
import json
import pathlib
import sys
import time

import numpy as np

SRC = pathlib.Path("/mnt/t7/smad_next/AF0/feat")
OUT = pathlib.Path("/mnt/t7/smad_next/PN1/feat")


class Tok:
    """(N, T, D) .npy rows by os.preadv (the same reading scheme as AF0's af0lib.Tok)."""

    def __init__(self, path):
        import os
        with open(path, "rb") as f:
            ver = np.lib.format.read_magic(f)
            hdr = np.lib.format.read_array_header_1_0(f) if ver == (1, 0) else np.lib.format.read_array_header_2_0(f)
            self.offset = f.tell()
        self.shape, self.dtype = hdr[0], np.dtype(hdr[2])
        assert not hdr[1]
        self.row = int(np.prod(self.shape[1:])) * self.dtype.itemsize
        self.fd = os.open(str(path), os.O_RDONLY)

    def read(self, a, b):
        import os
        n = (b - a) * self.row
        buf = bytearray(n)
        mv, got = memoryview(buf), 0
        while got < n:
            k = os.preadv(self.fd, [mv[got:]], self.offset + a * self.row + got)
            assert k > 0, "short read"
            got += k
        return np.frombuffer(buf, self.dtype).reshape((b - a,) + tuple(self.shape[1:]))


def pool(bb, name, chunk=256):
    d = SRC / bb
    ids = np.load(d / f"{name}.ids.npy")
    done = int((d / f"{name}.done").read_text())
    if done != len(ids):
        print(f"SKIP {bb}:{name}: done {done} of {len(ids)}", flush=True)
        return False
    o = OUT / bb
    o.mkdir(parents=True, exist_ok=True)
    f = o / f"af0_{name}.mean.npy"
    if f.exists():
        print("exists", f)
        return True
    tok = Tok(d / f"{name}.tokens.npy")   # pread reader (memory-map page faults crawl on this machine, AF0 README)
    assert tok.shape[0] == len(ids)
    out = np.zeros((len(ids), tok.shape[2]), np.float32)
    t0 = time.time()
    for i in range(0, len(ids), chunk):
        out[i:i + chunk] = tok.read(i, min(len(ids), i + chunk)).astype(np.float32).mean(1)
    np.save(o / f"af0_{name}.ids.npy", ids)
    np.save(f, out)
    json.dump(dict(source=str(d / f"{name}.tokens.npy"), shape=list(tok.shape), meta=json.load(open(d / f"{name}.meta.json")),
                   seconds=round(time.time() - t0, 1)), open(o / f"af0_{name}.meta.json", "w"), indent=1)
    print(f"DONE {bb}:{name} {tok.shape} {time.time() - t0:.0f} s", flush=True)
    return True


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    for a in sys.argv[1:]:
        bb, name = a.split(":")
        pool(bb, name)
