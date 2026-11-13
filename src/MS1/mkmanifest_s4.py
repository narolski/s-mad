"""MS1 part 4 (G3): SbM3-S manifest = SbM3's unique rows with part of the spliced-morph (lad_S4) rows entered twice before
the per-stratum balance, so that the splice share of attack rows equals Sb's (0.1026). Which S4 rows are doubled:
the first k of numpy.random.default_rng(20261141).permutation(S4 unique rows, sorted by id); k is the smallest count
whose resulting share is closest to 0.1026. Balance: src/PN1/mkmanifests.py `balanced`, imported unchanged, with the
seeds of mkmanifest.py (Sb strata 20261111 + index; new strata 20261111 + 100 + index). No new image.
  python3 -I mkmanifest_s4.py -> OUT/manifests/train_SbM3S.csv, experiments/MS1.../manifest_SbM3S_summary.json
"""
import collections
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ms1common as C  # noqa: E402
import mkmanifest as MK  # noqa: E402

TARGET = 0.1026
OLD = [("feret", "native"), ("feret", "s61"), ("frgc", "native"), ("frgc", "s61")]


def build(U, dup):
    MM = C.load(C.SRC / "PN1/mkmanifests.py", "pn1mk")
    out = []
    new = sorted({(r["db"], r["hist"]) for r in U} - set(OLD))
    for st in sorted({(r["db"], r["hist"]) for r in U}):
        seed = 20261111 + OLD.index(st) if st in OLD else 20261111 + 100 + new.index(st)
        rs = []
        for r in U:
            if (r["db"], r["hist"]) == st:
                rs += [r] * (2 if r["id"] in dup else 1)
        b, _, _ = MM.balanced(rs, seed=seed)
        out += b
    att = [r for r in out if r["label"] == "1"]
    return out, sum(r["kind"] == "lad_S4" for r in att) / len(att)


def main():
    rows = list(csv.DictReader(open(C.OUT / "manifests/train_SbM3.csv")))
    assert C.sha(C.OUT / "manifests/train_SbM3.csv").startswith("885dff9d")
    uniq = {}
    for r in rows:
        uniq.setdefault(r["id"], r)
    U = list(uniq.values())
    s4 = sorted(r["id"] for r in U if r["kind"] == "lad_S4")
    perm = [s4[i] for i in np.random.default_rng(20261141).permutation(len(s4))]
    best = None
    for k in range(len(s4) + 1):
        _, sh = build(U, set(perm[:k]))
        if best is None or abs(sh - TARGET) < best[1] - 1e-12:
            best = (k, abs(sh - TARGET), sh)
        if sh > TARGET:
            break
    k = best[0]
    out, sh = build(U, set(perm[:k]))
    mf = C.OUT / "manifests/train_SbM3S.csv"
    with open(mf, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MK.TRCOLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)
    summ = dict(rows=len(out), unique=len(U), s4_unique=len(s4), s4_doubled=k, splice_share_of_attack_rows=sh,
                target=TARGET, by_db=dict(collections.Counter(r["db"] for r in out)), sha256=C.sha(mf))
    json.dump(summ, open(C.RES / "manifest_SbM3S_summary.json", "w"), indent=1)
    print(json.dumps(summ))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
