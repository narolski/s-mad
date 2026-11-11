"""SM1 arm compositions: which images form the genuine and the morph class of each arm and seed (Part 3 frozen heads
and the Athena LoRA fits use the same lists). Everything is drawn from the feature lists in OUT/flists, in their row
order, with numpy default_rng(seed).

Arms (N = 14,734 release pairs with both contributors admissible):
  a     genuine 25,000 renders (train_bf)            morphs: release files of the N pairs (train_arma)
  a256  as a, release files 256 x 256 only           b, bp, c, cr, d50, d500: renders + that arm's N morphs
  d     genuine 12,500 renders + 12,500 halves (both halves of 6,250 (c) pairs)          morphs: (c)
  dplus genuine 25,000 renders + 12,500 halves                                          morphs: (c)   (descriptive)
  e     genuine 6,250 renders + 6,250 shrunk renders + 6,250 halves + 6,250 shrunk halves;
        morphs N/2 (c) morphs + the shrunk copies of the other N/2 (amendment A4)
  smoke (heads.py --smoke): 500 morphs of lists/smoke_<arm>.csv + 834 seeded renders; d: 417 renders + 417 halves

  python3 -I compose.py [--smoke]   -> OUT/compose[/smoke]/<arm>_s<seed>.json  {"genuine": [ids], "morph": [ids]}
"""
import argparse
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402

FL = K.OUT / "flists"
SRC = {"a": "arma", "a256": "arma", "b": "armb", "bp": "armbp", "c": "armc", "cr": "armcr", "d": "armc",
       "dplus": "armc", "d50": "armd50", "d500": "armd500", "e": "armc", "f": "armc",
       "d5": "armd5"}                              # A12 item 11: five random pool partners
ARMS = tuple(SRC)


def ids(name):
    return [r["id"] for r in csv.DictReader(open(FL / f"{name}.csv"))]


def jpeg_map():
    """A10: image id -> id of its JPEG copy (fixed assignment of jpeg_arm.py)."""
    return {r["id"]: r["id"] + ("_J90" if r["op"] == "jpeg90" else "_J70")
            for r in csv.DictReader(open(K.OUT / "lists/jpeg_assign.csv"))}


def compose(arm, seed, smoke=False):
    if arm == "f":                          # A10: arm (e) with every assigned image replaced by its JPEG copy
        c = compose("e", seed, smoke)
        jm = jpeg_map()
        return dict(arm="f", seed=seed, genuine=[jm.get(i, i) for i in c["genuine"]],
                    morph=[jm.get(i, i) for i in c["morph"]])
    rng = np.random.default_rng(seed)
    bf = ids("train_bf")
    if smoke:
        bf = [bf[i] for i in np.sort(np.random.default_rng(K.SEED + 17).choice(len(bf), size=834, replace=False))]
        keep = {r["id"] for r in csv.DictReader(open(K.OUT / "lists" / f"smoke_{SRC[arm]}.csv"))}
        mor = [x for x in ids(f"train_{SRC[arm]}") if x in keep]
    else:
        mor = ids(f"train_{SRC[arm]}")
    if arm == "a256":
        sz = {r["id"]: r["size"] for r in csv.DictReader(open(FL / "train_arma.csv"))}
        mor = [x for x in mor if sz[x] == "256x256"]
    gen = list(bf)
    if arm in ("d", "dplus"):
        hid = ids("train_armc_halves")
        hid = [h for h in hid if h.rsplit("_h", 1)[0] in set(mor)]
        pairs = np.array(sorted(set(mor)))
        n_h = len(bf) // 2
        pick = set(rng.choice(pairs, size=n_h // 2, replace=False).tolist())
        hsel = [h for h in hid if h.rsplit("_h", 1)[0] in pick]
        if arm == "d":
            g = [bf[i] for i in rng.choice(len(bf), size=len(bf) - len(hsel), replace=False)]
            gen = g + hsel
        else:
            gen = bf + hsel
    if arm == "e":
        assert not smoke
        bfs = ids("train_arme_bfS")
        hid, hsid, csid = ids("train_armc_halves"), ids("train_arme_hS"), ids("train_arme_cS")
        assert [x[4:] for x in bfs] == [x[3:] for x in bf] and [x[:-2] for x in hsid] == hid
        assert [x[:-2] for x in csid] == mor
        q = len(bf) // 4
        pb, ph = rng.permutation(len(bf)), rng.permutation(len(hid))
        gen = [bf[i] for i in pb[:q]] + [bfs[i] for i in pb[q:2 * q]] + [hid[i] for i in ph[:q]] + \
              [hsid[i] for i in ph[q:2 * q]]
        pm = rng.permutation(len(mor))
        h2 = len(mor) // 2
        mor = [mor[i] for i in pm[:h2]] + [csid[i] for i in pm[h2:]]
    return dict(arm=arm, seed=seed, genuine=gen, morph=mor)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    od = K.OUT / ("compose/smoke" if a.smoke else "compose")
    od.mkdir(parents=True, exist_ok=True)
    arms = ("a", "b", "bp", "c", "cr", "d") if a.smoke else ARMS
    for arm in arms:
        for s in ((401,) if a.smoke else K.SEEDS):
            c = compose(arm, s, a.smoke)
            json.dump(c, open(od / f"{arm}_s{s}.json", "w"))
            print(arm, s, len(c["genuine"]), len(c["morph"]))


if __name__ == "__main__":
    main()
