"""AB1 follow-up batch B2: the single registered read (prereg_b2.md). Development data only.

Inputs: B2 tars AB1B2_<arm>_s<seed>.tar (+ .sha256) for SbR, SbH61, SbSp, SbnS0, SbnS3 in --res2 (default
/mnt/t7/smad_next/AB1/b2/results) and the already-read AB1 tars of A, Sb, Sp, SbH, SbS in --res (default
/mnt/t7/smad_next/AB1/results). Uses ab1_read.py (load, pools, share, verdict; unchanged) with the B2 overlay and
manifest folder for B2 tars, and c2p_read.py (holdout, net_stats) unchanged.
  python3 -I ab1b2_read.py --out OUT.json
  python3 -I ab1b2_read.py --mock [--mock-drop SbR_s408] --out MOCK.json"""
import argparse
import csv
import importlib.util
import json
import math
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent


def _mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


A = _mod("ab1_read", HERE / "ab1_read.py")
C2 = A.C2
AB1_READ_SHA = "74ecdf7a2ecb35812dcf4e5d5b9f5c3b1f095fc6846ae6f4813bfb28404d035b"
B2_OVERLAY = "d2038b98af8b4d835091f80c7034c41bb7dce1a16fab8781e65c44abaabedc5e"
B2_MANDIR = pathlib.Path("/mnt/t7/smad_next/AB1/b2/manifests")
SEEDS = A.SEEDS
B2_ARMS = ("SbR", "SbH61", "SbSp", "SbnS0", "SbnS3")
AB1_ARMS = ("A", "Sb", "Sp", "SbH", "SbS")


def load_b2(tar, arm):
    o_ov, o_md = A.OVERLAY["AB1"], A.MANDIR
    A.OVERLAY["AB1"], A.MANDIR = B2_OVERLAY, B2_MANDIR
    try:
        return A.load(tar, "AB1", arm)
    finally:
        A.OVERLAY["AB1"], A.MANDIR = o_ov, o_md


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default="/mnt/t7/smad_next/AB1/results")
    ap.add_argument("--res2", default="/mnt/t7/smad_next/AB1/b2/results")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--mock-drop", default="")
    a = ap.parse_args()
    assert A.sha(HERE / "ab1_read.py") == AB1_READ_SHA, "ab1_read.py not at its pin"
    assert A.sha(HERE.parent / "PN1" / "c2p_read.py") == A.C2P_SHA, "c2p_read.py not at its pin"   # check F5
    assert A.sha(A.EVAL) == A.EVAL_SHA, "ab1_eval.csv not at its pin"
    drop = set(x for x in a.mock_drop.split(",") if x)
    M = list(csv.DictReader(open(A.EVAL)))
    P = A.pools(M)
    natp, natm, pairs, mpairs = C2.holdout(M)
    rng = np.random.default_rng(C2.RNG_G)
    boot = {z: [rng.integers(0, len(pairs[z]), len(pairs[z])) for _ in range(C2.B_BOOT)] for z in A.SIZES}
    need = set(natp) | set(natm) | {f"{i}_{z}" for z in A.SIZES for i in pairs[z]} | \
        {f"{i}_{z}" for z in A.SIZES for i in mpairs[z]} | {i for k in ("lc_m", "lc_g", "S3", "S4") for i in P[k]}
    R = dict(mock=a.mock, networks={}, status={})
    nets = {}
    for arm in AB1_ARMS + B2_ARMS:
        for s in SEEDS:
            key = f"{arm}_s{s}"
            if a.mock:
                if key in drop:
                    R["status"][key] = "mock: dropped"
                    continue
                r = np.random.default_rng(s * 100 + sum(map(ord, arm)) + 7)
                x = {rr["id"]: float(r.normal(1.0 if rr["label"] == "1" else -2.0, 1.5)) for rr in M}
                why = "mock"
            elif arm in B2_ARMS:
                x, _, why = load_b2(pathlib.Path(a.res2) / f"AB1B2_{arm}_s{s}.tar", arm)
            else:
                x, _, why = A.load(pathlib.Path(a.res) / f"AB1_{arm}_s{s}.tar", "AB1", arm)
            if x is None:
                R["status"][key] = why
                continue
            if not need <= set(x) or not all(math.isfinite(x[i]) for i in need):
                R["status"][key] = "incomplete or non-finite scores"
                continue
            R["status"][key] = "read"
            m = [x[i] for i in P["lc_m"]]; g = [x[i] for i in P["lc_g"]]
            st = dict(lcomb_auc=C2.fauc(m, g), S3=A.share(x, P["S3"]), S3_count=int(sum(x[i] > 0 for i in P["S3"])),
                      S3_vs_S4_auc=C2.fauc([x[i] for i in P["S4"]], [x[i] for i in P["S3"]]),
                      c2p=C2.net_stats(x, natp, natm, pairs, mpairs, boot))
            nets[(arm, s)] = st
            R["networks"][key] = st

    def ok(*ks):
        return all(k in nets for k in ks)

    def rule(arms, sup, fal):
        """per-seed booleans; verdict by ab1_read.verdict (supported / falsified on >= 4 of 5, 4 of 4; n <= 3 not read)"""
        rd = [s for s in SEEDS if ok(*[(x, s) for x in arms])]
        ps = {s: bool(sup(s)) for s in rd}
        pf = {s: bool(fal(s)) for s in rd}
        return dict(read_seeds=rd, supported_on=ps, falsified_on=pf,
                    verdict=A.verdict(sum(ps.values()), sum(pf.values()), len(rd)))
    n = lambda arm, s: nets[(arm, s)]
    V = {}
    # B2-1: SbH's S3 and landmark changes reproduced (>= half) by the random-drop control
    V["B2_1_repeats"] = rule(("SbR", "SbH", "Sb"),
        lambda s: (n("SbR", s)["S3_count"] - n("Sb", s)["S3_count"]) * 2 <= (n("SbH", s)["S3_count"] - n("Sb", s)["S3_count"])
        and (n("SbR", s)["lcomb_auc"] - n("Sb", s)["lcomb_auc"]) <= 0.5 * (n("SbH", s)["lcomb_auc"] - n("Sb", s)["lcomb_auc"])
        and (n("SbH", s)["S3_count"] - n("Sb", s)["S3_count"]) < 0 and (n("SbH", s)["lcomb_auc"] - n("Sb", s)["lcomb_auc"]) < 0,
        # check F3: falsified if SbR reproduces less than a quarter of SbH's change in both reads (SbH - Sb < 0 in both)
        lambda s: (n("SbH", s)["S3_count"] - n("Sb", s)["S3_count"]) < 0 and (n("SbH", s)["lcomb_auc"] - n("Sb", s)["lcomb_auc"]) < 0
        and (n("SbR", s)["S3_count"] - n("Sb", s)["S3_count"]) * 4 > (n("SbH", s)["S3_count"] - n("Sb", s)["S3_count"])
        and (n("SbR", s)["lcomb_auc"] - n("Sb", s)["lcomb_auc"]) > 0.25 * (n("SbH", s)["lcomb_auc"] - n("Sb", s)["lcomb_auc"]))
    V["B2_1_repeats"]["values"] = {s: dict(SbR_S3=n("SbR", s)["S3"] - n("Sb", s)["S3"], SbH_S3=n("SbH", s)["S3"] - n("Sb", s)["S3"],
                                          SbR_lcomb=n("SbR", s)["lcomb_auc"] - n("Sb", s)["lcomb_auc"],
                                          SbH_lcomb=n("SbH", s)["lcomb_auc"] - n("Sb", s)["lcomb_auc"],
                                          SbR_minus_SbH_S3=n("SbR", s)["S3"] - n("SbH", s)["S3"],
                                          SbR_minus_SbH_lcomb=n("SbR", s)["lcomb_auc"] - n("SbH", s)["lcomb_auc"])
                                   for s in V["B2_1_repeats"]["read_seeds"]}
    # B2-2: reverse storage cue from the stored copies of halves
    dm = lambda arm, s: n(arm, s)["c2p"]["amsl112"]["d_mean_sd"]
    V["B2_2_reverse_cue"] = rule(("SbH61", "Sb"), lambda s: dm("SbH61", s) - dm("Sb", s) >= 0.02,   # check F1: dose about +0.025
                                 lambda s: dm("SbH61", s) - dm("Sb", s) <= 0)
    V["B2_2_reverse_cue"]["values"] = {s: dm("SbH61", s) - dm("Sb", s) for s in V["B2_2_reverse_cue"]["read_seeds"]}
    # B2-3: two additive storage routes
    df = lambda arm, s: n(arm, s)["c2p"]["fm61"]["d_flag"]
    V["B2_3_additive"] = rule(("SbSp", "SbS", "Sb"),
                              lambda s: df("SbSp", s) - df("Sb", s) >= 0.06 and df("SbSp", s) - df("SbS", s) >= 0.01,  # check F2
                              lambda s: df("SbSp", s) - df("SbS", s) <= 0)
    V["B2_3_additive"]["values"] = {s: dict(SbSp_minus_Sb=df("SbSp", s) - df("Sb", s), SbS_minus_Sb=df("SbS", s) - df("Sb", s),
                                            SbSp_minus_SbS=df("SbSp", s) - df("SbS", s),
                                            Sp_minus_Sb=(df("Sp", s) - df("Sb", s)) if ok(("Sp", s)) else None)
                                    for s in V["B2_3_additive"]["read_seeds"]}
    # B2-5: which matched negative carries the S3 effect
    rd5 = [s for s in SEEDS if ok(("SbnS0", s), ("SbnS3", s), ("Sb", s), ("Sp", s))]
    sup5 = {s: bool(abs(n("SbnS0", s)["S3_count"] - n("Sb", s)["S3_count"]) <= 10
                    and abs(n("SbnS0", s)["lcomb_auc"] - n("Sb", s)["lcomb_auc"]) <= 0.03
                    and abs(n("SbnS3", s)["S3_count"] - n("Sp", s)["S3_count"]) <= 10) for s in rd5}
    fal5 = {s: bool(n("SbnS0", s)["S3_count"] - n("Sb", s)["S3_count"] >= 15) for s in rd5}
    k_s, k_f, nn = sum(sup5.values()), sum(fal5.values()), len(rd5)
    if nn <= 3:
        v5 = "not read (too few seeds)"
    elif k_f >= 2:
        v5 = "falsified"
    elif (nn == 5 and k_s >= 4) or (nn == 4 and k_s == 4):
        v5 = "supported"
    else:
        v5 = "inconclusive, no claim"
    V["B2_5_S3_vs_S0"] = dict(read_seeds=rd5, supported_on=sup5, falsified_on=fal5, verdict=v5,
                              values={s: dict(SbnS0_minus_Sb_S3=n("SbnS0", s)["S3"] - n("Sb", s)["S3"],
                                              SbnS0_minus_Sb_lcomb=n("SbnS0", s)["lcomb_auc"] - n("Sb", s)["lcomb_auc"],
                                              SbnS3_minus_Sp_S3=n("SbnS3", s)["S3"] - n("Sp", s)["S3"],
                                              SbnS3_minus_Sb_S3=n("SbnS3", s)["S3"] - n("Sb", s)["S3"],
                                              S3_vs_S4_auc=dict(SbnS0=n("SbnS0", s)["S3_vs_S4_auc"], SbnS3=n("SbnS3", s)["S3_vs_S4_auc"],
                                                                Sb=n("Sb", s)["S3_vs_S4_auc"], Sp=n("Sp", s)["S3_vs_S4_auc"]))
                                      for s in rd5})
    # B2-5b threshold-free companion (check improvement 2): S3-vs-S4 AUC, SbnS0 within 0.03 of Sb and SbnS3 within 0.03 of Sp
    au = lambda arm, s: n(arm, s)["S3_vs_S4_auc"]
    V["B2_5b_S3_vs_S4_auc"] = rule(("SbnS0", "SbnS3", "Sb", "Sp"),
                                   lambda s: abs(au("SbnS0", s) - au("Sb", s)) <= 0.03 and abs(au("SbnS3", s) - au("Sp", s)) <= 0.03,
                                   lambda s: au("SbnS0", s) - au("Sb", s) <= -0.05)
    V["B2_5b_S3_vs_S4_auc"]["values"] = {s: dict(SbnS0_minus_Sb=au("SbnS0", s) - au("Sb", s), SbnS3_minus_Sp=au("SbnS3", s) - au("Sp", s))
                                         for s in V["B2_5b_S3_vs_S4_auc"]["read_seeds"]}
    # printed: C2P per-seed passes against A for SbSp (C2P.3 X rule)
    ctrl = {z: {s: ok(("A", s)) and n("A", s)["c2p"][z]["d_flag"] >= 0.05 and n("A", s)["c2p"][z]["d_mean_sd"] > 0 for s in SEEDS}
            for z in A.SIZES}
    V["printed_SbSp_c2p_pass"] = {z: {s: bool(ctrl[z][s] and ok(("SbSp", s)) and
                                             n("SbSp", s)["c2p"][z]["d_flag"] <= n("A", s)["c2p"][z]["d_flag"] / 3 and
                                             abs(n("SbSp", s)["c2p"][z]["d_mean_sd"]) <= n("A", s)["c2p"][z]["d_mean_sd"] / 3 and
                                             n("SbSp", s)["c2p"][z]["d_flag"] <= 0.05 and n("SbSp", s)["c2p"][z]["d_flag_upper95"] <= 0.08)
                                        for s in SEEDS} for z in A.SIZES}
    R["verdicts"] = V
    json.dump(R, open(a.out, "w"), indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o))
    print(json.dumps({k: v["verdict"] for k, v in V.items() if isinstance(v, dict) and "verdict" in v}, indent=1))
    print("not read:", {k: v for k, v in R["status"].items() if v != "read"})


if __name__ == "__main__":
    main()
