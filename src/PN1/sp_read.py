"""PN1 arm Sp reader (registration 1b8fe48; written before any Sp tar is pulled). Development data only: development
ladder (100 hosts) and FFHQ; the 191-host test ladder is not read.
Per seed 403, 404, 405 (read only if the Sp tar and FS1's Sb tar are both verified and finite):
  prediction 1: own-rule (logit > 0) flag share of the 100 development-ladder S0 images: Sp >= max(2*Sb, Sb + 0.10)
  prediction 2: raw development S0-vs-S4 AUC (field `auc` of K.paired_auc_ci, as sb_read's D_ii; native OpenCV,
                100 vs 100): Sp <= Sb - 0.05
  printed: development S3 own-rule flags, excess over floor3 and face-only AUC (development), landmark_combined AUC,
           R1-R6 (fs_read.rreads), FFHQ storage share rising; B's development S0 flags as reference.
  reading: supported if both predictions hold on >= 2 of 3 read seeds; falsified if neither holds on >= 2 of 3; with
           exactly 2 read seeds both must agree; fewer than 2: "not read"; otherwise "inconclusive, no claim".
  python3 -I sp_read.py [--test401]  -> experiments/PN1_.../tier_fs/sp.json  (--test401: Bv stands in for Sp and Sb is
  the 401/402 Sb, on already-read tars, to test the code only; output tier1_sb/sp_read_test.json)"""
import csv
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pn1lib as K  # noqa: E402
import reads as RD  # noqa: E402
import fs_read as F  # noqa: E402
import posthoc2 as PH  # noqa: E402


def main():
    test = "--test401" in sys.argv[1:]
    man = list(csv.DictReader(open(F.EVAL)))
    lad = [dict(r, fam="ladder", _splice=True) if r["fam"] == "splice" else r for r in man if r["fam"] in ("ladder", "splice", "af0")]
    cat = {r["id"]: r for r in K.catalog()}
    for r in lad:
        c = cat.get(r["id"])
        r["persons"] = c["persons"] if c else (r["host"],)
        r["neutral"] = False
        r.setdefault("field", "")
        r["pool"] = c["pool"] if c else "ladder"
    P = RD.pools([r for r in lad if not r.get("_splice")])
    for r in lad:
        if r.get("_splice"):
            P.setdefault(("T_" if r["role"] == "test" else "D_") + r["rung"], []).append(r)
    fl, flinfo = PH.floor3()
    g = lambda fam, rung: [r["id"] for r in man if r["fam"] == fam and r["rung"] == rung]
    lc_m, lc_g = g("ffhq_lcomb", "landmark_combined_orig"), g("ffhq_lcomb", "landmark_combined_resmatch")
    cmp_m, cmp_g = g("ffhq", "landmark_complete_orig"), g("ffhq", "landmark_complete_resmatch")
    hc = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_orig"}
    hb = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_orig"}
    pk = [(hc[k], hb[k]) for k in sorted(set(hc) & set(hb))]
    nat = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "ffhq_bona_orig"}
    rm = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_resmatch"}
    keys = sorted(set(nat) & set(rm))
    z = np.load(F.FLOOR)
    cid = {str(i): c for i, c in zip(z["ids"], z["cues"])}
    names = [str(n) for n in z["names"]]
    if test:
        R_ = K.PN1 / "results_rented"
        seeds = (401, 402)
        src = {s: {"Sp": R_ / f"PN1_Bv_s{s}.tar", "Sb": R_ / f"PN1_Sb_s{s}.tar", "B": R_ / f"PN1_B_s{s}.tar"} for s in seeds}
    else:
        seeds = (403, 404, 405)
        src = {s: {"Sp": F.RF / f"PN1_Sp_s{s}.tar", "Sb": F.RF / f"PN1_Sb_s{s}.tar", "B": F.RF / f"PN1_B_s{s}.tar"} for s in seeds}
    out = {"floor3": flinfo, "seeds": {}}
    read = []
    for s in seeds:
        S = {a: F.load(t) for a, t in src[s].items()}
        if test and S["B"] is not None:          # B 401/402 was scored on pack 1; its splice rows are in Brescore
            import tarfile as _t
            rt = K.PN1 / "results_rented" / f"PN1_Brescore_s{s}.tar"
            zz = np.load(K.PN1 / "results_rented" / "unpacked" / f"PN1_Brescore_s{s}" / "scores_splice.npz")
            S["B"].update(dict(zip([str(i) for i in zz["id"]], zz["logit"].astype(float))))
        rec = {"read": S["Sp"] is not None and S["Sb"] is not None}
        if rec["read"]:
            read.append(s)
            for a in ("Sp", "Sb", "B"):
                x = S[a]
                if x is None:
                    continue
                pos, neg = P["D_S4"], P["D_S0"]
                have = all(r["id"] in x for r in pos + neg)
                d2 = K.paired_auc_ci(RD.scores_of(x, pos), RD.scores_of(x, neg), [RD.unit(r) for r in pos], [RD.unit(r) for r in neg],
                                     extra={"floor3": (np.array([fl[r["id"]] for r in pos]), np.array([fl[r["id"]] for r in neg]))}) if have else {}
                rec[a] = dict(dev_S0_flag_own=float(np.mean(RD.scores_of(x, P["D_S0"]) > 0)),
                              dev_S3_flag_own=float(np.mean(RD.scores_of(x, P["D_S3"]) > 0)),
                              dev_S0_vs_S4_auc=d2.get("auc"), dev_excess_floor3=d2.get("excess"),
                              dev_faceonly=RD.paired(x, P, "D_S4_bg", "D_S0_bg").get("auc"))
                if a != "B" and not test:
                    rr = F.rreads({a: x}, lc_m, lc_g, cid, names, cmp_m, cmp_g, pk)
                    d = np.array([x[rm[k]] - x[nat[k]] for k in keys])
                    rec[a].update(lcomb_auc=rr[a]["R6"]["auc_combined"], R1_R6=rr[a], storage_share_rising=float(np.mean(d > 0)))
            sp, sb = rec["Sp"], rec["Sb"]
            rec["p1"] = bool(sp["dev_S0_flag_own"] >= max(2 * sb["dev_S0_flag_own"], sb["dev_S0_flag_own"] + 0.10))
            rec["p2"] = bool(sp["dev_S0_vs_S4_auc"] <= sb["dev_S0_vs_S4_auc"] - 0.05)
        out["seeds"][str(s)] = rec
    R = [out["seeds"][str(s)] for s in read]
    n = len(R)
    both = sum(r["p1"] and r["p2"] for r in R)
    none = sum((not r["p1"]) and (not r["p2"]) for r in R)
    if n < 2:
        v = "not read"
    elif n == 2:
        v = "supported" if both == 2 else "falsified" if none == 2 else "inconclusive, no claim"
    else:
        v = "supported" if both >= 2 else "falsified" if none >= 2 else "inconclusive, no claim"
    out.update(read_seeds=read, verdict=v, test_mode=test,
               label="development, n = 3 seeds; not about SBI or SelfMAD; no S0 vs S3 attribution; no benchmark claim")
    d = K.RES / ("tier1_sb" if test else "tier_fs")
    d.mkdir(parents=True, exist_ok=True)
    K.dump(out, d / ("sp_read_test.json" if test else "sp.json"))
    for s in read:
        r = out["seeds"][str(s)]
        print(s, {a: {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r[a].items() if k in ("dev_S0_flag_own", "dev_S3_flag_own", "dev_S0_vs_S4_auc", "dev_faceonly", "lcomb_auc", "storage_share_rising")} for a in ("Sp", "Sb", "B") if a in r}, "p1", r["p1"], "p2", r["p2"])
    print("verdict", v)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
