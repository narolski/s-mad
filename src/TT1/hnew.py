"""TT1 amendments H-new-1, H-new-2, H-new-4 (prereg.md section 8, commit 5954c12; registered before computing).
Zero GPU, development data only. Output: experiments/TT1_.../hnew.json
  python -I hnew.py"""
import csv
import json
import pathlib
import sys
from itertools import permutations

import cv2
import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tt1common as T  # noqa: E402

PN1R = pathlib.Path("/mnt/t7/smad_next/PN1/results_rented/unpacked")
A14 = pathlib.Path("/mnt/t7/smad_next/PN1/results_a14/unpacked/PN1_A14")
TT1S = pathlib.Path("/mnt/t7/smad_next/TT1/results/unpacked_tt1c/TT1_A100_tt1c_full/scores")
EV = list(csv.DictReader(open(T.PN1T / "data" / "manifests" / "pn1_eval.csv")))


def stored(net):
    z = np.load(PN1R / net / "scores_eval.npz")
    return dict(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))


def hnew2():
    out = {}
    pairs = {}
    for r in EV:
        if r["label"] != "0":
            continue
        if (r["fam"] == "ladder" and r["role"] == "dev" and r["rung"] == "R0") or (r["fam"] == "af0" and r["rung"] == "photo"):
            pairs.setdefault((r["fam"], r["host"]), {})[r["strength"]] = r["id"]
    pairs = {k: v for k, v in pairs.items() if all(s in v for s in ("", "61", "112"))}
    for a in ("A", "B", "Bn", "C", "Sb", "Bv"):
        for s in (401, 402):
            L = stored(f"PN1_{a}_s{s}")
            o = {"n_pairs": len(pairs)}
            for st in ("61", "112"):
                d = [L[v[st]] - L[v[""]] for v in pairs.values()]
                o[st] = dict(paired_median_shift=float(np.median(d)), copy_flag=float(np.mean([L[v[st]] > 0 for v in pairs.values()])))
            o["native_flag"] = float(np.mean([L[v[""]] > 0 for v in pairs.values()]))
            out[f"{a}_s{s}"] = o
    fals = any(out[f"A_s{s}"]["61"]["paired_median_shift"] <= out[f"B_s{s}"]["61"]["paired_median_shift"] + 0.1 for s in (401, 402))
    return dict(per_net=out, verdict="falsified" if fals else "not falsified (A's 61 px shift exceeds B's + 0.1 on both seeds)")


def facebox_var(path):
    g = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2GRAY)[170:400, 170:342]
    return float(cv2.Laplacian(g, cv2.CV_64F).var())


def hnew1():
    lst = list(csv.DictReader(open(T.OUT / "tt1_score.csv")))
    tt = {r["id"]: r for r in T.tt1_rows()}
    geo = {r["id"]: r for r in csv.DictReader(open(T.OUT / "geo_ref.csv")) if r["group"] == "g112" and r["aligned"] == "1"}
    packs = [i for i, r in tt.items() if r["source"] in ("lfw", "calfw", "cfp_ff", "agedb_30") and r["primary"]]
    vg = {i: facebox_var(r["path"]) for i, r in geo.items()}
    vp = {i: facebox_var(tt[i]["aligned_path"]) for i in packs}
    out = dict(n_geo=len(vg), n_packs=len(vp), median_var_geo112=float(np.median(list(vg.values()))),
               median_var_packs=float(np.median(list(vp.values()))), per_seed={})
    big = True
    for s in (401, 402):
        z = np.load(TT1S / f"PN1_A_s{s}__tt1.npz")
        L = dict(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
        lg, lp = [L[i] for i in vg], [L[i] for i in vp]
        diff = float(np.median(lg) - np.median(lp))
        x = np.log(np.array(list(vg.values()) + list(vp.values())))
        y = np.array(lg + lp)
        slope = float(np.polyfit(x, y, 1)[0])
        out["per_seed"][s] = dict(median_logit_geo112_minus_packs=diff, ols_slope_logit_on_log_facebox_var=slope)
        big &= diff > 2
    fals = out["median_var_geo112"] >= out["median_var_packs"] and big
    out["verdict"] = "falsified" if fals else "not falsified"
    return out


def hnew4():
    pools = {"ladder_R4": lambda r: r["fam"] == "ladder" and r["rung"] == "R4" and r["strength"] == "" and r["label"] == "1",
             "af0_u50": lambda r: r["fam"] == "af0" and r["rung"] == "u50" and r["label"] == "1",
             "splice_S4": lambda r: r["fam"] == "splice" and r["rung"] == "S4" and r["label"] == "1"}
    ids = {k: [r["id"] for r in EV if f(r)] for k, f in pools.items()}
    for k, f in pools.items():
        for r in EV:
            if f(r):
                assert r["fam"] in ("ladder", "af0", "splice") and r["path"].startswith("eval/pn1/"), r
    read = json.load(open(T.RES / "tt1_read.json"))
    nets = [f"PN1_{a}_s{s}" for a in ("A", "B", "Sb", "C", "Bv") for s in (401, 402)]
    rows = {}
    for n in nets:
        a, s = n[4:].rsplit("_s", 1)
        L = stored(n)
        if a == "B":
            z = np.load(PN1R / f"PN1_Brescore_s{s}" / "scores_splice.npz")
            L.update(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
        elif a in ("A", "C"):
            z = np.load(A14 / f"{n}__splice.npz")
            L.update(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
        miss = {k: float(np.mean([L[i] <= 0 for i in v])) for k, v in ids.items()}
        rows[n] = dict(Fbar=read["nets"][n]["r5"]["Fbar"], miss=miss, y=float(np.mean(list(miss.values()))))
    x = np.array([rows[n]["Fbar"] for n in nets])
    y = np.array([rows[n]["y"] for n in nets])
    rho = float(spearmanr(x, y)[0])
    # exact permutation p (one-sided, rho <= observed), 10! = 3.6M is too many: use 200,000 fixed-seed permutations
    rng = np.random.default_rng(20261123)
    rx = np.argsort(np.argsort(x))
    ry = np.argsort(np.argsort(y))
    perm = np.array([np.corrcoef(rx, rng.permutation(ry))[0, 1] for _ in range(200000)])
    p = float(np.mean(perm <= np.corrcoef(rx, ry)[0, 1]))
    v = "falsified" if rho >= 0 else ("supported" if rho <= -0.6 else "weak (not decided)")
    return dict(pools={k: len(v) for k, v in ids.items()}, per_net=rows, spearman=rho, perm_p_one_sided=p,
                perm_note="200,000 permutations (default_rng(20261123)); exact enumeration of 10! replaced for cost",
                verdict=v)


def main():
    out = dict(label="post-result amendments (prereg section 8, 5954c12); zero GPU; development data only",
               H_new_2=hnew2(), H_new_4=hnew4(), H_new_1=hnew1())
    (T.RES / "hnew.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: (v.get("verdict") if isinstance(v, dict) else v) for k, v in out.items()}, indent=1))
    print(json.dumps({n: (o["61"], o["112"]) for n, o in out["H_new_2"]["per_net"].items()}, indent=0)[:2500])
    print(json.dumps({n: (round(o["Fbar"], 3), round(o["y"], 3), {k: round(v, 3) for k, v in o["miss"].items()}) for n, o in out["H_new_4"]["per_net"].items()}, indent=0))
    print(out["H_new_4"]["spearman"], out["H_new_4"]["perm_p_one_sided"])
    print({k: out["H_new_1"][k] for k in ("median_var_geo112", "median_var_packs", "per_seed", "verdict")})


if __name__ == "__main__":
    main()
