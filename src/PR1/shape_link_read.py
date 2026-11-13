"""PR1 amendment 5 (post hoc): does the training-side shape link to 32 test hosts change the candidate's test reads?
32 training hosts of the frozen candidate's list carry S3 and S0 negatives built on the landmarks of their pool partner,
and those 32 partners are read test hosts (DATA audit addendum, b0eb018). Reads per Sb seed on test hosts:
S4 vs S3 AUC and paired margin (median S4 - S3 logit), R4 vs R3 AUC (OpenCV native), own-rule flag rates on S3, S0,
R3, R4; on (a) all 191, (b) the 159 clean hosts, (c) the 32 shape-linked hosts, and (d) the 80 test hosts clean of
development persons (DATA list). Component-bootstrap intervals (host-partner person graph); paired difference (b) - (a);
null of (c) - (b) from random 32-of-191 splits (2,000 draws). Blocks: FS1 Sb 403-407 (decides), AB1 Sb 408-412 (printed).
Host ids stay on /mnt/t7 (only counts and statistics are written to the repository).
  python -I shape_link_read.py --out shape_link_read.json   [--mock]"""
import argparse
import csv
import io
import json
import pathlib
import sys
import tarfile

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/BD1")
from bd1_read import auc, sha  # noqa: E402

MAN = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv")
POOL = pathlib.Path("/mnt/t7/smad_next/AR1/pool.csv")
SPLIT = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/split/ladder_split.csv")
CLEAN_DEV = pathlib.Path("/mnt/t7/smad_next/DATA/overlap/test_hosts_clean_of_dev.csv")
BLOCKS = {"FS1": [(f"/mnt/t7/smad_next/PN1/results_fs/PN1_Sb_s{s}.tar", f"PN1_Sb_s{s}", s) for s in range(403, 408)],
          "AB1": [(f"/mnt/t7/smad_next/AB1/results/AB1_Sb_s{s}.tar", f"AB1_Sb_s{s}", s) for s in range(408, 413)]}
B = 2000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    lad = {r["pid"]: r for r in csv.DictReader(open(SPLIT))}
    pool = {r["pid"]: r for r in csv.DictReader(open(POOL))}
    man = [r for r in csv.DictReader(open(MAN)) if r["role"] == "test"]
    rows = {}
    for r in man:
        key = None
        if r["fam"] == "splice" and r["rung"] in ("S4", "S3", "S0"):
            key = r["rung"]
        elif r["fam"] == "ladder" and r["tool"] == "opencv" and r["strength"] == "" and r["rung"] in ("R4", "R3"):
            key = r["rung"]
        if key:
            rows.setdefault(r["host"], {})[key] = r["id"]
    hosts = sorted(h for h, d in rows.items() if all(k in d for k in ("S4", "S3", "S0", "R4", "R3")))
    assert len(hosts) == 191, len(hosts)
    train = [h for h, r in lad.items() if r["role"] == "train"]
    linked = {pool[h]["B_pid"] for h in train if h in pool and pool[h]["B_pid"] in set(hosts)}
    assert len(linked) == 32, len(linked)
    cdev = {r["host"] for r in csv.DictReader(open(CLEAN_DEV))}
    sets = {"all": hosts, "clean": [h for h in hosts if h not in linked], "linked": [h for h in hosts if h in linked],
            "clean_of_dev": [h for h in hosts if h in cdev]}
    out = dict(mock=a.mock, n={k: len(v) for k, v in sets.items()})
    # host-partner person graph components (for the bootstrap)
    par = {}

    def find(x):
        par.setdefault(x, x)
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for h in hosts:
        par[find(h)] = find(pool[h]["B_pid"])
    comp = {h: find(h) for h in hosts}

    def reads(L, hs):
        hs = list(hs)
        s4 = np.array([L[rows[h]["S4"]] for h in hs])
        s3 = np.array([L[rows[h]["S3"]] for h in hs])
        s0 = np.array([L[rows[h]["S0"]] for h in hs])
        r4 = np.array([L[rows[h]["R4"]] for h in hs])
        r3 = np.array([L[rows[h]["R3"]] for h in hs])
        return dict(S4_vs_S3=auc(s4, s3), margin=float(np.median(s4 - s3)), R4_vs_R3=auc(r4, r3),
                    flag_S3=float((s3 > 0).mean()), flag_S0=float((s0 > 0).mean()), flag_R3=float((r3 > 0).mean()),
                    flag_R4=float((r4 > 0).mean()))

    def cboot(L, hs, key, seed=20261201):
        cs = sorted({comp[h] for h in hs})
        mem = {c: [h for h in hs if comp[h] == c] for c in cs}
        rng = np.random.default_rng(seed)
        v = [reads(L, [h for p in rng.choice(len(cs), len(cs)) for h in mem[cs[p]]])[key] for _ in range(B if not a.mock else 50)]
        return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]

    for blk, nets in BLOCKS.items():
        res = {}
        for path, name, s in nets:
            if a.mock:
                rng = np.random.default_rng(s)
                L = {i: float(rng.normal()) for d in rows.values() for i in d.values()}
            else:
                assert sha(path) == pathlib.Path(path + ".sha256").read_text().split()[0]
                with tarfile.open(path) as tf:
                    z = np.load(io.BytesIO(tf.extractfile(f"{name}/scores_eval.npz").read()))
                L = dict(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
            r = {k: reads(L, v) for k, v in sets.items()}
            for k in ("all", "clean", "linked", "clean_of_dev"):
                r[k]["ci_S4_vs_S3"] = cboot(L, sets[k], "S4_vs_S3")
                r[k]["ci_flag_S3"] = cboot(L, sets[k], "flag_S3")
            r["clean_minus_all"] = {q: r["clean"][q] - r["all"][q] for q in ("S4_vs_S3", "margin", "R4_vs_R3", "flag_S3", "flag_S0", "flag_R3", "flag_R4")}
            r["linked_minus_clean"] = {q: r["linked"][q] - r["clean"][q] for q in ("S4_vs_S3", "flag_S3")}
            rng = np.random.default_rng(20261202)
            nd_auc, nd_flag = [], []
            for _ in range(B if not a.mock else 50):
                perm = rng.permutation(hosts)
                g32, g159 = perm[:32], perm[32:]
                x, y = reads(L, g32), reads(L, g159)
                nd_auc.append(x["S4_vs_S3"] - y["S4_vs_S3"])
                nd_flag.append(x["flag_S3"] - y["flag_S3"])
            r["null_32_of_191"] = dict(S4_vs_S3=[float(np.percentile(nd_auc, 2.5)), float(np.percentile(nd_auc, 97.5))],
                                       flag_S3=[float(np.percentile(nd_flag, 2.5)), float(np.percentile(nd_flag, 97.5))])
            res[str(s)] = r
        dif = [(v["linked_minus_clean"]["S4_vs_S3"], v["linked_minus_clean"]["flag_S3"], v["null_32_of_191"]) for v in res.values()]
        matters = sum(1 for da, df, _ in dif if da >= 0.05 or abs(df) >= 0.10)
        inside = all(nl["S4_vs_S3"][0] <= da <= nl["S4_vs_S3"][1] and nl["flag_S3"][0] <= df <= nl["flag_S3"][1] for da, df, nl in dif)
        verdict = "shape link matters" if matters >= 4 else ("no visible effect" if inside else "inconclusive")
        out[blk] = dict(per_seed=res, n_seeds_matter=matters, all_inside_null=bool(inside), verdict=verdict,
                        role="registered (decides)" if blk == "FS1" else "printed",
                        note="n = 32 linked hosts is small")
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: (v if k in ("n", "mock") else {kk: vv for kk, vv in v.items() if kk != "per_seed"}) for k, v in out.items()}, default=float)[:2000])


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()
