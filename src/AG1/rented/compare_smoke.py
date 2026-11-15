"""AG1 rented-machine first check (registered in prereg amendment 4 before it runs): the smoke shard AG1_smoke_mip1 made
on the rented GPU against the same shard made on Athena (job 3544209).
PASS requires: the same 11 stems; every PNG 1024 x 1024 RGB with only IHDR / IDAT / IEND chunks; for every optimised
image the final loss within 10% (relative) of Athena's (generation is not bitwise repeatable: on one A100 two identical
runs end max |w| 0.38 apart, and RT vs R3 differ by 2.6 grey levels mean; no pixel tolerance is claimed, the mean
|pixel difference| is printed only).
Rule b (only if registered as an amendment before use): count and format exact; median relative final-loss difference
<= 5%, and every optimised image within max(10% relative, 0.25 absolute).
Usage: python -I compare_smoke.py RENTED.tar ATHENA.tar [strict|b]
"""
import csv
import io
import sys
import tarfile

import numpy as np
from PIL import Image


def load(t):
    tf = tarfile.open(t)
    root = tf.getnames()[0].split("/")[0]
    log = {r["stem"]: r for r in csv.DictReader(io.StringIO(tf.extractfile(f"{root}/log.csv").read().decode()))}
    imgs = {}
    for s in log:
        raw = tf.extractfile(f"{root}/png/{s}.png").read()
        i, ch = 8, set()
        while i < len(raw):
            n = int.from_bytes(raw[i:i + 4], "big")
            ch.add(raw[i + 4:i + 8].decode())
            i += 12 + n
        im = Image.open(io.BytesIO(raw))
        imgs[s] = (im.size, im.mode, ch, np.asarray(im.convert("RGB")).astype(int))
    return log, imgs


def main():
    rule = sys.argv[3] if len(sys.argv) > 3 else "strict"
    lr, ir = load(sys.argv[1])
    rels = []
    la, ia = load(sys.argv[2])
    ok = set(lr) == set(la) and len(lr) == 11
    print(f"stems rented {len(lr)} athena {len(la)} same {set(lr) == set(la)}")
    for s in sorted(la):
        if s not in ir:
            continue
        size, mode, ch, a = ir[s]
        fmt = size == (1024, 1024) and mode == "RGB" and ch <= {"IHDR", "IDAT", "IEND"}
        l1, l2 = lr[s]["loss"], la[s]["loss"]
        rel = None
        if l2 not in ("", "nan") and l1 not in ("", "nan"):
            rel = abs(float(l1) - float(l2)) / max(abs(float(l2)), 1e-9)
            rels.append(rel)
        if rule == "b":
            good = fmt and (rel is None or rel <= 0.10 or abs(float(l1) - float(l2)) <= 0.25)
        else:
            good = fmt and (rel is None or rel <= 0.10)
        ok = ok and good
        print(f"{s:28s} format {fmt} loss rented {float(l1):.3f} athena {float(l2):.3f} rel {rel if rel is None else round(rel, 4)} "
              f"mean|px diff| {np.abs(a - ia[s][3]).mean():.2f} {'ok' if good else 'FAIL'}")
    if rule == "b":
        med = float(np.median(rels)) if rels else 1.0
        print(f"rule b: median relative loss difference {med:.4f} (limit 0.05)")
        ok = ok and med <= 0.05
    print(f"rule {rule}")
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
