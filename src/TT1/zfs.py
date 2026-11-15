"""TT1-FS post-result items Z1-Z4 (prereg.md section 12, commit 62139a7). Zero GPU, development data only.
  python -I zfs.py -> experiments/TT1_.../zfs.json"""
import csv
import json
import pathlib
import sys

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tt1common as T  # noqa: E402

NETS = pathlib.Path("/mnt/t7/smad_next/TT1/nets_fs")
EV = list(csv.DictReader(open(T.PN1T / "data" / "manifests" / "pn1_eval.csv")))
SEEDS = (403, 404, 405, 406, 407)


def main():
    fs = json.load(open(T.RES / "tt1_read_fs.json"))["nets"]
    old = json.load(open(T.RES / "tt1_read.json"))["nets"]
    out = {}
    # Z1
    pools = {"ladder_R4": lambda r: r["fam"] == "ladder" and r["rung"] == "R4" and r["strength"] == "" and r["label"] == "1",
             "af0_u50": lambda r: r["fam"] == "af0" and r["rung"] == "u50" and r["label"] == "1",
             "splice_S4": lambda r: r["fam"] == "splice" and r["rung"] == "S4" and r["label"] == "1"}
    ids = {k: [r["id"] for r in EV if f(r)] for k, f in pools.items()}
    for k, f in pools.items():
        for r in EV:
            if f(r):
                assert r["fam"] in ("ladder", "af0", "splice") and r["path"].startswith("eval/pn1/"), r
    rows = {}
    for a in ("A", "B", "Sb"):
        for s in SEEDS:
            n = f"PN1_{a}_s{s}"
            z = np.load(NETS / n / "scores_eval.npz")
            L = dict(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
            miss = {k: float(np.mean([L[i] <= 0 for i in v])) for k, v in ids.items()}
            rows[n] = dict(Fbar=fs[n]["r5"]["Fbar"], miss=miss, y=float(np.mean(list(miss.values()))))
    names = list(rows)
    x = np.array([rows[n]["Fbar"] for n in names]); y = np.array([rows[n]["y"] for n in names])
    rho = float(spearmanr(x, y)[0])
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    rng = np.random.default_rng(20261124)
    obs = np.corrcoef(rx, ry)[0, 1]
    perm = np.array([np.corrcoef(rx, rng.permutation(ry))[0, 1] for _ in range(200000)])
    per_seed = {s: dict(B_minus_A_y=rows[f"PN1_B_s{s}"]["y"] - rows[f"PN1_A_s{s}"]["y"],
                        Sb_minus_B_y=rows[f"PN1_Sb_s{s}"]["y"] - rows[f"PN1_B_s{s}"]["y"],
                        B_minus_A_pools={k: rows[f"PN1_B_s{s}"]["miss"][k] - rows[f"PN1_A_s{s}"]["miss"][k] for k in ids},
                        Sb_minus_B_pools={k: rows[f"PN1_Sb_s{s}"]["miss"][k] - rows[f"PN1_B_s{s}"]["miss"][k] for k in ids}) for s in SEEDS}
    pays = sum(per_seed[s]["B_minus_A_y"] > 0.02 for s in SEEDS) >= 4
    out["Z1"] = dict(label="post hoc", pools={k: len(v) for k, v in ids.items()}, per_net=rows, spearman=rho,
                     perm_p_one_sided_le=float(np.mean(perm <= obs)), per_seed=per_seed,
                     verdict="B pays in misses" if pays else "no B-against-A miss cost shown")
    # Z2
    A = [f"PN1_A_s{s}" for s in SEEDS]
    F = [fs[n]["r5"]["Fbar"] for n in A]
    G = [fs[n]["printed"]["geo_flag"]["g112"] for n in A]
    RL = [abs(fs[n]["r4"]["lfw"]["rho"]) for n in A]
    r_g, r_l = float(spearmanr(F, G)[0]), float(spearmanr(F, RL)[0])
    v = lambda r: "related (>= 0.7)" if r >= 0.7 else ("not related (< 0.3)" if r < 0.3 else "weak")
    post = json.load(open(T.RES / "posthoc_review.json"))["nets"]
    out["Z2"] = dict(label="descriptive", Fbar=F, geo112_flag=G, abs_rho_lfw=RL, spearman_F_geo112=r_g, spearman_F_rho_lfw=r_l,
                     verdict_geo112=v(r_g), verdict_rho_lfw=v(r_l),
                     seeds_401_402_printed={n: dict(Fbar=old[n]["r5"]["Fbar"], geo112_flag=post[n]["geo_g112"]["flag"],
                                                    abs_rho_lfw=abs(old[n]["r4"]["lfw"]["rho"])) for n in ("PN1_A_s401", "PN1_A_s402")})
    # Z3
    z3 = {}
    for s in SEEDS:
        b, sb = fs[f"PN1_B_s{s}"], fs[f"PN1_Sb_s{s}"]
        z3[s] = dict(border_flag_Sb_minus_B={f: sb["printed"]["border_flag"][f] - b["printed"]["border_flag"][f] for f in T.FAMILIES},
                     R3c_cfp_Sb_minus_B=sb["auc"]["cfp_ff"]["c"]["auc"] - b["auc"]["cfp_ff"]["c"]["auc"],
                     border_flag_cfp=dict(Sb=sb["printed"]["border_flag"]["cfp_ff"], B=b["printed"]["border_flag"]["cfp_ff"]))
    above = sum(z3[s]["border_flag_Sb_minus_B"]["cfp_ff"] > 0 for s in SEEDS)
    flat = sum(z3[s]["border_flag_Sb_minus_B"]["cfp_ff"] <= 0.005 for s in SEEDS) >= 4
    out["Z3"] = dict(label="descriptive", per_seed=z3, n_seeds_Sb_above_B_cfp=int(above),
                     verdict="not a border cue on CFP" if flat else (f"Sb above B on {above} of 5 seeds"))
    # Z4
    Bn = [("PN1_B_s401", old), ("PN1_B_s402", old)] + [(f"PN1_B_s{s}", fs) for s in SEEDS]
    ff = [src[n]["pools"]["R_ffhq"]["flag"] for n, src in Bn]
    fb = [src[n]["r5"]["Fbar"] for n, src in Bn]
    r4 = float(spearmanr(ff, fb)[0])
    out["Z4"] = dict(label="descriptive; seeds 401/402 trained on pn1a/pn1b and scored on tt1c, 403-407 on pn1fs",
                     networks=[n for n, _ in Bn], ffhq_flag=ff, Fbar=fb, spearman=r4,
                     verdict="one seed-level instability consistent" if r4 >= 0.7 else ("not consistent" if r4 < 0.3 else "weak"))
    (T.RES / "zfs.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: (v.get("verdict") or (v.get("verdict_geo112"), v.get("verdict_rho_lfw"))) for k, v in out.items()}, indent=1))
    print("Z1 rho", rho, "p", out["Z1"]["perm_p_one_sided_le"])
    for s in SEEDS:
        print(s, {k: round(v, 3) for k, v in per_seed[s]["B_minus_A_pools"].items()}, round(per_seed[s]["B_minus_A_y"], 3), round(per_seed[s]["Sb_minus_B_y"], 3))
    print("Z2", F, G, RL, r_g, r_l)
    print("Z3", {s: (round(z3[s]["border_flag_cfp"]["Sb"], 3), round(z3[s]["border_flag_cfp"]["B"], 3), round(z3[s]["R3c_cfp_Sb_minus_B"], 3)) for s in SEEDS})
    print("Z4", ff, fb, r4)


if __name__ == "__main__":
    main()
