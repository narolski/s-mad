"""SM1 amendment A12 item 1 (post hoc): the partner audit against the evaluation-split partners (KE).

For every score set (releases on crops, releases on whole files, every frozen head and seed, the FE header):
per key the mean logit with the 5 trained partners (P), the 5 evaluation partners (E), the 5 matched unused (U);
gap(trained - KE) = mean_k(P - E), gap(KE - U) = mean_k(E - U), gap(trained - U) (the registered row); 10,000 key
bootstrap draws (seed 20261111, the same draws for every score set); own-rule miss rate (logit < 0) per partner kind;
heads: 5-seed means with the bootstrap of the seed mean, and DiD of gap(trained - KE) between head arms.

  python3 -I a12_partner_ref.py [--heads-dir D --name N --no-releases] -> RES/<N, default a12_partner_ref>.json
"""
import argparse
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402

B = 10000
RELS = ("madation_vitb16", "madation_vitl14", "madation_fe_vitb16", "madation_fe_vitl14", "mixfacenet_mad_smdd",
        "madation_fs_vitb16", "madation_fs_vitl14")
ARMS = ("a", "a256", "b", "d5", "d50", "d500", "bp", "cr", "c", "d", "dplus", "e", "f")


def setup():
    meta = list(csv.DictReader(open(K.OUT / "flists/audit.csv")))
    keys = sorted({r["key"] for r in meta if r["kind"] == "KP"})
    idx = {}
    for r in meta:
        if r["kind"] in ("KP", "KE", "KU"):
            idx[(r["kind"], r["key"], int(r["slot"]))] = r["id"]
    kinds = {}
    for r in meta:
        kinds.setdefault(r["kind"], []).append(r["id"])
    draws = np.random.default_rng(K.SEED).integers(0, len(keys), (B, len(keys)))
    return meta, keys, idx, kinds, draws


def per_key(z, keys, idx):
    M = {}
    for kind in ("KP", "KE", "KU"):
        M[kind] = np.array([[z[idx[(kind, k, j)]] for j in range(5)] for k in keys]).mean(1)
    return M


def miss(z, kinds):
    return {k: round(float(np.mean([z[i] < 0 for i in ids if i in z])), 4) for k, ids in kinds.items()
            if k in ("KP", "KE", "KU", "KX", "PP", "UU")}


def gaps(Ms, draws):
    """Ms: list of per-key dicts (one per seed) -> point and bootstrap interval of the seed-mean gaps."""
    out = {}
    for name, (x, y) in {"trained_minus_KE": ("KP", "KE"), "KE_minus_U": ("KE", "KU"),
                         "trained_minus_U_registered": ("KP", "KU")}.items():
        d = np.mean([M[x] - M[y] for M in Ms], 0)
        bt = d[draws].mean(1)
        out[name] = dict(gap=round(float(d.mean()), 4), ci=[round(v, 4) for v in S.ci(bt)],
                         seeds=[round(float((M[x] - M[y]).mean()), 4) for M in Ms])
        out[name]["_d"] = d
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--heads-dir", default=None, help="head score folder (default OUT/heads); e.g. OUT/heads_fz1")
    ap.add_argument("--name", default="a12_partner_ref")
    ap.add_argument("--no-releases", action="store_true")
    ap.add_argument("--arms", default=",".join(ARMS))
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    hd = pathlib.Path(a.heads_dir) if a.heads_dir else K.OUT / "heads"
    meta, keys, idx, kinds, draws = setup()
    load = lambda f, key: {str(i): float(v) for i, v in zip(np.load(f)["id"], np.load(f)[key])}  # noqa: E731
    res = {"releases_crop": {}, "releases_whole": {}, "heads": {}}
    for det in (() if a.no_releases else RELS):
        for tag, d in (("releases_crop", K.OUT / "p2scores"), ("releases_whole", K.OUT / "p2scores/whole")):
            f = d / f"scores_rel_{det}.npz"
            if f.exists():
                z = load(f, "logit_noTTA")
                g = gaps([per_key(z, keys, idx)], draws)
                for v in g.values():
                    v.pop("_d")
                res[tag][det] = dict(gaps=g, own_rule_miss=miss(z, kinds))
    dvec = {}
    for arm in tuple(a.arms.split(",")) + ("feref",):
        files = [K.OUT / "heads/feref.npz"] if arm == "feref" else \
            [hd / f"{arm}_s{s}.npz" for s in K.SEEDS]
        files = [f for f in files if f.exists()]
        if not files:
            continue
        zs = [load(f, "logit") for f in files]
        g = gaps([per_key(z, keys, idx) for z in zs], draws)
        dvec[arm] = g["trained_minus_KE"].pop("_d")
        for v in g.values():
            v.pop("_d", None)
        ms = [miss(z, kinds) for z in zs]
        res["heads"][arm] = dict(gaps=g, own_rule_miss={k: round(float(np.mean([m[k] for m in ms])), 4) for k in ms[0]},
                                 n_seeds=len(files))
    did = {}
    for x in ("a", "b", "a256", "feref"):
        for y in ("bp", "cr", "c", "d50", "d500", "d5"):
            if x in dvec and y in dvec:
                d = dvec[x] - dvec[y]
                did[f"{x}-{y}"] = dict(did=round(float(d.mean()), 4), ci=[round(v, 4) for v in S.ci(d[draws].mean(1))])
    res["heads_did_trained_minus_KE"] = did
    res["note"] = ("post hoc (A12 item 1); trained - U is the registered row, biased (U matched only on cosine to keys, "
                   "IOD and yaw); the reported size of the trace is trained - KE")
    res["heads_dir"] = str(hd)
    json.dump(res, open(K.RES / f"{a.name}.json", "w"), indent=1)
    for tag in ("releases_crop", "releases_whole"):
        for det, o in res[tag].items():
            g = o["gaps"]
            print(tag, det, "T-KE", g["trained_minus_KE"]["gap"], g["trained_minus_KE"]["ci"], "KE-U",
                  g["KE_minus_U"]["gap"], g["KE_minus_U"]["ci"], "T-U", g["trained_minus_U_registered"]["gap"],
                  "miss", o["own_rule_miss"])
    for arm, o in res["heads"].items():
        g = o["gaps"]
        print("head", arm, "T-KE", g["trained_minus_KE"]["gap"], g["trained_minus_KE"]["ci"], "KE-U",
              g["KE_minus_U"]["gap"], "T-U", g["trained_minus_U_registered"]["gap"], "miss", o["own_rule_miss"])
    print(json.dumps(did))


if __name__ == "__main__":
    main()
