"""PR1 amendment 5 / 5a (post hoc): do the 32 shape-linked test hosts read differently from the 159 clean test hosts?
Amendment 5a (pre-run check PRERUN_PR1_A5_20261113.md, fixes 1-6; the lead's original rule withdrawn):
- Primary statistic: linked-minus-clean difference in each host's mean logit over S3, S0 and S4 (predicted direction:
  lower for linked hosts), decided on the 5-seed mean (FS1 Sb 403-407) against a joint null: the same 2,000 random
  splits for all seeds, stratified by database x (partner is a development host), with the 32's make-up.
- "shape link visible" if the 5-seed mean lies below the 95% null (predicted direction); "no effect detectable at
  n = 32" if the primary and the two-sided S4-vs-S3 AUC difference both lie inside the null; otherwise "inconclusive".
  Smallest detectable sizes printed as (1.96 + 0.84) x null SD.
- Printed: S4-vs-S3 AUC, paired margin, S4 miss rate, median logit per rung, flags on S3, S0, R3, R4; R4 vs R3 as the
  low-link control; sets all 191 / clean 159 / linked 32 / clean of development 80, and linked vs clean within the
  clean-of-development hosts (n = 11); covariates; the 191- and 159-host values always side by side.
- Tar sha256 values pinned in shape_link_tar_pins.txt and asserted. AB1 Sb 408-412 printed only. Host ids stay on /mnt/t7.
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
KEYS = ("mean_logit", "S4_vs_S3", "margin", "miss_S4", "flag_S3", "flag_S0", "R4_vs_R3")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--pins", default="/home/narolski/smad-next/src/PR1/shape_link_tar_pins.txt")
    a = ap.parse_args()
    pins = {l.split()[1]: l.split()[0] for l in open(a.pins).read().splitlines() if l.strip()}
    assert len(pins) == 10
    lad = {r["pid"]: r for r in csv.DictReader(open(SPLIT))}
    pool = {r["pid"]: r for r in csv.DictReader(open(POOL))}
    rows = {}
    for r in csv.DictReader(open(MAN)):
        if r["role"] != "test":
            continue
        key = None
        if r["fam"] == "splice" and r["rung"] in ("S4", "S3", "S0"):
            key = r["rung"]
        elif r["fam"] == "ladder" and r["tool"] == "opencv" and r["strength"] == "" and r["rung"] in ("R4", "R3"):
            key = r["rung"]
        if key:
            assert key not in rows.get(r["host"], {})
            rows.setdefault(r["host"], {})[key] = r["id"]
    hosts = sorted(h for h, d in rows.items() if all(k in d for k in ("S4", "S3", "S0", "R4", "R3")))
    assert len(hosts) == 191
    hs_set = set(hosts)
    train = [h for h, r in lad.items() if r["role"] == "train"]
    linked = {pool[h]["B_pid"] for h in train if h in pool and pool[h]["B_pid"] in hs_set}
    assert len(linked) == 32
    cdev = {r["host"] for r in csv.DictReader(open(CLEAN_DEV))}
    clean = [h for h in hosts if h not in linked]
    sets = {"all": hosts, "clean": clean, "linked": sorted(linked), "clean_of_dev": [h for h in hosts if h in cdev],
            "clean_of_dev_linked": [h for h in hosts if h in cdev and h in linked],
            "clean_of_dev_clean": [h for h in hosts if h in cdev and h not in linked]}
    pdev = {h: lad.get(pool[h]["B_pid"], {}).get("role") == "dev" for h in hosts}
    strat = {h: (pool[h]["db"], pdev[h]) for h in hosts}
    cov = {}
    for k in ("linked", "clean", "all"):
        hs = sets[k]
        cov[k] = dict(n=len(hs), frgc=sum(pool[h]["db"] == "frgc" for h in hs), partner_dev=sum(pdev[h] for h in hs),
                      cos_HB_median=float(np.median([float(pool[h]["cos_HB"]) for h in hs])),
                      cos_HS_median=float(np.median([float(pool[h]["cos_HS"]) for h in hs])))
    out = dict(mock=a.mock, n={k: len(v) for k, v in sets.items()}, covariates=cov,
               mechanism=("The evaluation hull of a linked test host is not the training hull of its partner (0 of 32 pairs "
                          "equal); the training hull uses the test person's S-photo landmarks for half its points; the link is "
                          "partial landmark shape, not a duplicated item."))

    def reads(L, hs):
        g = lambda k: np.array([L[rows[h][k]] for h in hs])   # noqa: E731
        s4, s3, s0, r4, r3 = g("S4"), g("S3"), g("S0"), g("R4"), g("R3")
        return dict(mean_logit=float(np.mean((s3 + s0 + s4) / 3)), S4_vs_S3=auc(s4, s3), margin=float(np.median(s4 - s3)),
                    miss_S4=float((s4 <= 0).mean()), med_S4=float(np.median(s4)), med_S3=float(np.median(s3)),
                    med_S0=float(np.median(s0)), med_R4=float(np.median(r4)), med_R3=float(np.median(r3)),
                    flag_S3=float((s3 > 0).mean()), flag_S0=float((s0 > 0).mean()),
                    R4_vs_R3=auc(r4, r3), flag_R3=float((r3 > 0).mean()), flag_R4=float((r4 > 0).mean()))

    # the same stratified splits (32 hosts with the linked make-up) for every seed and block
    rng = np.random.default_rng(20261202)
    need, by_s = {}, {}
    for h in linked:
        need[strat[h]] = need.get(strat[h], 0) + 1
    for h in hosts:
        by_s.setdefault(strat[h], []).append(h)
    out["strata_linked"] = {f"{k[0]}|partner_dev={k[1]}": v for k, v in sorted(need.items())}
    out["strata_all"] = {f"{k[0]}|partner_dev={k[1]}": len(v) for k, v in sorted(by_s.items())}
    splits = []
    for _ in range(B if not a.mock else 100):
        g = set()
        for s_, k in sorted(need.items()):
            g |= set(rng.choice(by_s[s_], k, replace=False).tolist())
        splits.append((sorted(g), [h for h in hosts if h not in g]))
    for blk, nets in BLOCKS.items():
        per, nulls = {}, {k: np.zeros(len(splits)) for k in KEYS}
        for path, name, s in nets:
            if a.mock:
                rr = np.random.default_rng(s)
                L = {i: float(rr.normal()) for d in rows.values() for i in d.values()}
            else:
                assert sha(path) == pins[pathlib.Path(path).name], f"{path} off its pinned sha256"
                with tarfile.open(path) as tf:
                    z = np.load(io.BytesIO(tf.extractfile(f"{name}/scores_eval.npz").read()))
                L = dict(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
            r = {k: reads(L, v) for k, v in sets.items()}
            r["linked_minus_clean"] = {k: r["linked"][k] - r["clean"][k] for k in r["linked"]}
            r["all191_vs_clean159"] = {k: [r["all"][k], r["clean"][k]] for k in r["all"]}
            r["within_clean_of_dev_linked_minus_clean_n11"] = {k: r["clean_of_dev_linked"][k] - r["clean_of_dev_clean"][k]
                                                              for k in r["linked"]}
            for j, (g, c) in enumerate(splits):
                x, y = reads(L, g), reads(L, c)
                for k in KEYS:
                    nulls[k][j] += (x[k] - y[k]) / len(nets)
            per[str(s)] = r
        mean_obs = {k: float(np.mean([per[str(s)]["linked_minus_clean"][k] for _, _, s in nets])) for k in KEYS}
        null_ci = {k: [float(np.percentile(nulls[k], 2.5)), float(np.percentile(nulls[k], 97.5))] for k in KEYS}
        detect = {k: float(2.8 * nulls[k].std()) for k in KEYS}
        inside = lambda k: null_ci[k][0] <= mean_obs[k] <= null_ci[k][1]   # noqa: E731
        if mean_obs["mean_logit"] < null_ci["mean_logit"][0]:
            v = "shape link visible"
        elif inside("mean_logit") and inside("S4_vs_S3"):
            v = "no effect detectable at n = 32"
        else:
            v = "inconclusive"
        five = {st: {k: float(np.mean([per[str(s)][st][k] for _, _, s in nets])) for k in per[str(nets[0][2])][st]}
                for st in sets}
        out[blk] = dict(role="registered (decides)" if blk == "FS1" else "printed", verdict=v,
                        five_seed_mean_linked_minus_clean=mean_obs, joint_null_95=null_ci, smallest_detectable=detect,
                        five_seed_mean_per_set=five, per_seed=per)
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    short = {k: v for k, v in out.items() if k not in ("FS1", "AB1")}
    for blk in BLOCKS:
        short[blk] = {k: v for k, v in out[blk].items() if k not in ("per_seed", "five_seed_mean_per_set")}
    print(json.dumps(short, default=float))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()
