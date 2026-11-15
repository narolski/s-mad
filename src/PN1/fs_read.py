"""PN1 registration FS1 reader (fresh seeds, development data only), implementing prereg_fresh_seeds_v4_frozen.md.
Written and committed before any fresh-seed tar is pulled. Inputs: /mnt/t7/smad_next/PN1/results_fs/PN1_<arm>_s<seed>.tar
(+ .sha256), the development pack's pn1_eval.csv (pinned), cues/a14_lcomb.npz (pinned via tier1_a14/a14_lcomb_floor.sha256),
pn1a's A seed 401 (results_rented) for HN9. Benchmark rows are not in the manifest; none is read.
  python3 -I fs_read.py -> experiments/PN1_.../tier_fs/fs.json"""
import csv
import hashlib
import pathlib
import sys
import tarfile

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pn1lib as K  # noqa: E402
import reads as RD  # noqa: E402

RF = K.PN1 / "results_fs"
EVAL = K.PN1 / "fs_tree" / "pn1" / "data" / "manifests" / "pn1_eval.csv"
EVAL_SHA = "f0f29f2201bd3a1dc67f24772347960ba7a383a9e5c1fa8920d0cc1b854a5045"
FLOOR = K.PN1 / "cues" / "a14_lcomb.npz"
FLOOR_SHA = K.RES / "tier1_a14" / "a14_lcomb_floor.sha256"
SEEDS = (403, 404, 405, 406, 407)
MACHINE = {403: "m1 (GPU 0)", 405: "m1 (GPU 0)", 407: "m1 (GPU 0)", 404: "m2 (GPU 1)", 406: "m2 (GPU 1)"}  # "machine" = GPU/queue
ARMS = ("A", "B", "Sb")


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def fauc(pos, neg):
    from scipy.stats import rankdata
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    r = rankdata(np.r_[pos, neg])[: len(pos)]
    return (r.sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def load(tar):
    if not tar.exists() or not (tar.parent / (tar.name + ".sha256")).exists():
        return None
    if sha(tar) != (tar.parent / (tar.name + ".sha256")).read_text().split()[0]:
        return None
    d = tar.parent / "unpacked"
    if not (d / tar.name[:-4]).exists():
        with tarfile.open(tar) as t:
            t.extractall(d)
    z = np.load(d / tar.name[:-4] / "scores_eval.npz")
    s = dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))
    return s if all(np.isfinite(list(s.values()))) else None


def count(meets, n):
    k = sum(meets)
    if n <= 3:
        return "not read (too few seeds)"
    if (n == 5 and k >= 4) or (n == 4 and k == 4):
        return "replicated"
    if k <= 1:
        return "not replicated"
    return "inconclusive, no claim"


# ---------------- printed reads R1-R6 (registered e95656a; print only, no verdict)
R1_EDGES = [0.302886, 0.362101, 0.378055, 0.394011, 0.410915, 0.430752, 0.453196, 0.479793, 0.516776, 0.571266, 3.38642]


def strata(v):
    k = np.searchsorted(np.array(R1_EDGES), v, side="right") - 1
    return np.clip(k, 0, 9)


def r1_auc(m, g, km, kg):
    num = den = 0.0
    for k in range(10):
        a, b = m[km == k], g[kg == k]
        if len(a) and len(b):
            w = len(a) * len(b)
            num += w * fauc(a, b)
            den += w
    return num / den if den else float("nan")


def cv_auc(X, y):
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    oof = np.zeros(len(y))
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=0).split(X, y):
        mdl = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000)).fit(X[tr], y[tr])
        oof[te] = mdl.decision_function(X[te])
    return fauc(oof[y == 1], oof[y == 0])


def rreads(nets, lc_m, lc_g, cid, names, comp_m=None, comp_g=None, pair_keys=None):
    """nets: {name: score dict}. lc_m / lc_g: landmark_combined orig morph / resmatch genuine ids; comp_m / comp_g:
    landmark_complete orig morph / resmatch genuine ids; pair_keys: [(complete morph id, combined morph id)]."""
    from scipy.stats import spearmanr
    jf, jb = names.index("noise_std_face"), names.index("noise_std_border")
    CM = np.array([cid[i] for i in lc_m], float); CG = np.array([cid[i] for i in lc_g], float)
    fm, fg = CM[:, jf], CG[:, jf]
    km, kg = strata(fm), strata(fg)
    sdf = np.std(np.r_[fm, fg])
    y = np.r_[np.ones(len(lc_m)), np.zeros(len(lc_g))]
    Xall = np.r_[CM, CG]
    base_face = cv_auc(Xall[:, [jf]], y)
    base_27 = cv_auc(Xall, y)
    r5 = fauc(CM[:, jb], CG[:, jb])
    rng = np.random.default_rng(20261119)
    draws = [(rng.integers(0, len(lc_m), len(lc_m)), rng.integers(0, len(lc_g), len(lc_g))) for _ in range(2000)]
    out = {"R3_base": dict(noise_std_face=base_face, all_27=base_27),
           "R5_noise_std_border_auc": dict(auc=float(r5), direction_free=float(max(r5, 1 - r5)))}
    r1d = {}
    for n, x in nets.items():
        m = np.array([x[i] for i in lc_m]); g = np.array([x[i] for i in lc_g])
        r1 = r1_auc(m, g, km, kg)
        r1d[n] = np.array([r1_auc(m[im], g[ig], km[im], kg[ig]) for im, ig in draws])
        r2 = {f"{c}_{cls}": float(spearmanr(v, cue).correlation)
              for c, j in (("noise_std_face", jf), ("noise_std_border", jb))
              for cls, v, cue in (("morph", m, CM[:, j]), ("genuine", g, CG[:, j]))}
        lg = np.r_[m, g][:, None]
        f1 = cv_auc(np.c_[Xall[:, [jf]], lg], y); f27 = cv_auc(np.c_[Xall, lg], y)
        # R4: each morph vs the nearest genuine on noise_std_face within 0.1 SD (with replacement)
        order = np.argsort(fg); fs = fg[order]
        wins = []
        for i in range(len(m)):
            p = np.searchsorted(fs, fm[i])
            cand = [q for q in (p - 1, p) if 0 <= q < len(fs)]
            q = min(cand, key=lambda q: abs(fs[q] - fm[i]))
            if abs(fs[q] - fm[i]) <= 0.1 * sdf:
                gv = g[order[q]]
                wins.append(1.0 if m[i] > gv else 0.5 if m[i] == gv else 0.0)
        rec = dict(R1_strat_auc=float(r1), R1_ci=[float(np.percentile(r1d[n], 2.5)), float(np.percentile(r1d[n], 97.5))],
                   R2=r2, R3=dict(face_plus_logit=f1, inc_over_face=f1 - base_face, all27_plus_logit=f27, inc_over_27=f27 - base_27),
                   R4_matched_auc=float(np.mean(wins)) if wins else None, R4_n_matched=len(wins))
        if comp_m is not None:
            cm_ = np.array([x[i] for i in comp_m]); cg_ = np.array([x[i] for i in comp_g])
            dd = np.array([x[a] - x[b] for a, b in pair_keys])
            rec["R6"] = dict(auc_complete=float(fauc(cm_, cg_)), auc_combined=float(fauc(m, g)),
                             auc_loss=float(fauc(cm_, cg_) - fauc(m, g)), share_complete_higher=float(np.mean(dd > 0)),
                             mean_logit_drop=float(dd.mean()), genuine_sd_combined=float(np.std(g)))
        out[n] = rec
    if "Sb" in nets and "B" in nets:
        dd = r1d["Sb"] - r1d["B"]
        out["R1_Sb_minus_B"] = dict(point=out["Sb"]["R1_strat_auc"] - out["B"]["R1_strat_auc"],
                                    ci=[float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5))])
        out["R3_Sb_inc27_minus_B"] = out["Sb"]["R3"]["inc_over_27"] - out["B"]["R3"]["inc_over_27"]
    return out


def prestated(recs, c1_meeting_seeds):
    """recs: {seed: rreads output}. Registered sentence if contrast 1 replicates and the floor is not exceeded.
    R2 condition read as: every |rho| of Sb (both statistics, morphs and genuine) <= 0.2 on every read seed."""
    a = all(recs[s]["R1_Sb_minus_B"]["point"] >= 0.05 for s in c1_meeting_seeds)
    b = all(max(abs(v) for v in recs[s]["Sb"]["R2"].values()) <= 0.2 for s in recs)
    c = int(sum(bool(recs[s]["R3_Sb_inc27_minus_B"] > 0) for s in recs)) >= 4
    ok = bool(a and b and c)
    return dict(R1_ok=bool(a), R2_ok=bool(b), R3_ok=bool(c), sentence=(
        "Sb's gain over B on this development set is not explained by the best single simple statistic or by the 27 "
        "statistics combined; Sb does not exceed the best statistic's own AUC, and still reads the surround (R6)."
        if ok else "The gain is not separated from simple statistics."))


def main():
    assert sha(EVAL) == EVAL_SHA
    assert sha(FLOOR) == FLOOR_SHA.read_text().split()[0]
    man = list(csv.DictReader(open(EVAL)))
    lc_m = [r["id"] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_orig"]
    lc_g = [r["id"] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_resmatch"]
    nat = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "ffhq_bona_orig"}
    rm = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_resmatch"}
    keys = sorted(set(nat) & set(rm))
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
    z = np.load(FLOOR)
    cid = {str(i): c for i, c in zip(z["ids"], z["cues"])}
    CM = np.array([cid[i] for i in lc_m]); CG = np.array([cid[i] for i in lc_g])
    rng = np.random.default_rng(20261118)
    draws = [(rng.integers(0, len(lc_m), len(lc_m)), rng.integers(0, len(lc_g), len(lc_g))) for _ in range(2000)]

    def fmax(im, ig):
        v = [fauc(CM[im, j], CG[ig, j]) for j in range(CM.shape[1])]
        return max(max(u, 1 - u) for u in v)
    fdraw = np.array([fmax(im, ig) for im, ig in draws])
    out = {"floor_best_auc": float(fmax(np.arange(len(lc_m)), np.arange(len(lc_g)))), "seeds": {}}
    read = []
    for s in SEEDS:
        S = {a: load(RF / f"PN1_{a}_s{s}.tar") for a in ARMS}
        rec = {"gpu_queue": MACHINE[s], "read": all(v is not None for v in S.values())}
        if rec["read"]:
            read.append(s)
            for a in ARMS:
                x = S[a]
                m = np.array([x[i] for i in lc_m]); g = np.array([x[i] for i in lc_g])
                sd = np.array([fauc(m[im], g[ig]) for im, ig in draws])
                d = np.array([x[rm[k]] - x[nat[k]] for k in keys])
                pb = [np.mean(d[rng.integers(0, len(d), len(d))] > 0) for _ in range(2000)]
                fo = RD.paired(x, P, "T_S4_bg", "T_S0_bg")
                fb = RD.paired(x, P, "T_R4_face", "T_R2w_face")
                rec[a] = dict(lcomb_auc=float(fauc(m, g)), lcomb_ci=[float(np.percentile(sd, 2.5)), float(np.percentile(sd, 97.5))],
                              lcomb_minus_floor_lo=float(np.percentile(sd - fdraw, 2.5)),
                              share_rising=float(np.mean(d > 0)), share_ci=[float(np.percentile(pb, 2.5)), float(np.percentile(pb, 97.5))],
                              faceonly_test=fo.get("auc"), faceonly_test_ci=[fo.get("lo"), fo.get("hi")],
                              faceonly_dev=RD.paired(x, P, "D_S4_bg", "D_S0_bg").get("auc"),
                              faceblanked_test=fb.get("auc"), faceblanked_dev=RD.paired(x, P, "D_R4_face", "D_R2w_face").get("auc"),
                              flags_own={p: float(np.mean(RD.scores_of(x, P[p]) > 0)) for p in ("D_R0", "D_R0_61", "D_R0_112", "V_photo") if P.get(p)} |
                              {"ffhq_bona_orig": float(np.mean([x[nat[k]] > 0 for k in keys]))})
            A, B, Sb = (rec[a] for a in ARMS)
            rec["c1_testable"] = B["lcomb_auc"] < 0.95
            rec["c1_meets"] = bool(Sb["lcomb_auc"] - B["lcomb_auc"] >= 0.05 and Sb["lcomb_auc"] - A["lcomb_auc"] >= -0.02)
            rec["c1_floor_exceeded"] = Sb["lcomb_minus_floor_lo"] > 0
            rec["c2"] = {a: rec[a]["share_rising"] <= 0.65 for a in ARMS}
            rec["c3_meets"] = bool(Sb["faceonly_test"] - B["faceonly_test"] >= 0.05)
        out["seeds"][str(s)] = rec
    names = [str(n) for n in z["names"]]
    cmp_m = [r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_orig"]
    cmp_g = [r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_resmatch"]
    hc = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_orig"}
    hb_ = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_orig"}
    pk = [(hc[k], hb_[k]) for k in sorted(set(hc) & set(hb_))]
    RR_ = {}
    for s in read:
        nets = {a: load(RF / f"PN1_{a}_s{s}.tar") for a in ARMS}
        RR_[s] = rreads(nets, lc_m, lc_g, cid, names, cmp_m, cmp_g, pk)
    out["printed_R1_R6"] = {str(s): v for s, v in RR_.items()}
    R = [out["seeds"][str(s)] for s in read]
    t1 = [r for r in R if r["c1_testable"]]
    c1 = count([r["c1_meets"] for r in t1], len(t1))
    floor_all = bool(t1) and all(r["c1_floor_exceeded"] for r in t1)
    a_fail = sum(not r["c2"]["A"] for r in R)
    control = len(R) >= 4 and a_fail >= len(R) - 1
    c2 = {a: (count([r["c2"][a] for r in R], len(R)) if control else "uninformative on these seeds") for a in ("B", "Sb")}
    c3 = count([r["c3_meets"] for r in R], len(R))
    claims = []
    if c1 == "replicated":
        claims.append("Spliced positives raise detection of face-spliced morphs over protocol-only training on a development "
                      "set with an unseen splice engine (FFHQ landmark_combined), 5 seeds" if floor_all else
                      "Higher AUC than B, but not shown beyond simple statistics")
        if not floor_all:
            meet = [s for s in read if out["seeds"][str(s)]["c1_testable"] and out["seeds"][str(s)]["c1_meets"]]
            out["printed_R1_R6_sentence"] = prestated(RR_, meet)
            claims.append("Printed (R1-R6): " + out["printed_R1_R6_sentence"]["sentence"])
    elif c3 == "replicated":
        claims.append("Engine-specific: the gain holds on our OpenCV ladder splices only")
    elif c1 == "not replicated" and c3 == "not replicated":
        claims.append("The Sb lead was selection or seed noise")
    if control and c2["B"] == "replicated" and c2["Sb"] == "replicated":
        claims.append("The protocol removes the storage reaction on a development source not used in training (already read on seeds 401/402), 5 seeds")
    if not claims:
        claims.append("inconclusive, no claim")
    out.update(read_seeds=read, contrast1=c1, contrast1_testable_seeds=len(t1), floor_exceeded_all=floor_all,
               contrast2=c2, contrast2_positive_control=control, contrast3=c3, claims=claims)
    rep = load(RF / "PN1_Arep_s401.tar")
    orig = load(K.PN1 / "results_rented" / "PN1_A_s401.tar")
    if rep is not None:
        fl = float(np.mean([rep[nat[k]] > 0 for k in keys]))
        common = [i for i in rep if orig is not None and i in orig]
        out["HN9"] = dict(label="platform plus nondeterminism", ffhq_flag_own=fl,
                          reading="platform plus nondeterminism" if abs(fl - 0.225) > 0.03 else "consistent with seed-driven",
                          max_abs_logit_diff_vs_pn1a_common_dev_rows=float(max(abs(rep[i] - orig[i]) for i in common)) if common else None)
    d = K.RES / "tier_fs"
    d.mkdir(parents=True, exist_ok=True)
    K.dump(out, d / "fs.json")
    print("read seeds", read, "| c1", c1, "floor", floor_all, "| c2", c2, "control", control, "| c3", c3)
    print("claims", claims)


def a14test():
    """R1-R6 on the 401/402 amendment-14 data only (test of the extension; no fresh-seed tar is touched)."""
    A14 = K.PN1 / "results_a14" / "unpacked" / "PN1_A14"
    U = K.PN1 / "results_rented" / "unpacked"
    man = list(csv.DictReader(open(K.PN1 / "a14_tree" / "pn14" / "data" / "manifests" / "pn1_a14.csv")))
    lc_m = [r["id"] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_orig"]
    lc_g = [r["id"] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_resmatch"]
    cmp_m = [r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_orig"]
    cmp_g = [r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_resmatch"]
    hc = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_orig"}
    hb_ = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_orig"}
    pk = [(hc[k], hb_[k]) for k in sorted(set(hc) & set(hb_))]
    assert sha(FLOOR) == FLOOR_SHA.read_text().split()[0]
    z = np.load(FLOOR)
    cid = {str(i): c for i, c in zip(z["ids"], z["cues"])}
    names = [str(n) for n in z["names"]]

    def npz(p):
        q = np.load(p)
        return dict(zip([str(i) for i in q["id"]], q["logit"].astype(float)))
    res = {}
    for s in (401, 402):
        nets = {}
        for a in ("A", "B", "Sb"):
            x = npz(A14 / f"PN1_{a}_s{s}__ffhq_lcomb.npz")
            x.update(npz(U / f"PN1_HN2_s{s}" / f"scores_hn2_{a}.npz") if a != "Sb" else npz(A14 / f"PN1_Sb_s{s}__ffhq.npz"))
            nets[a] = x
        res[str(s)] = rreads(nets, lc_m, lc_g, cid, names, cmp_m, cmp_g, pk)
    res["prestated_test"] = prestated({int(k): v for k, v in res.items()}, [401, 402])
    d = K.RES / "tier1_a14"
    K.dump(dict(post_hoc=True, note="test of fs_read.py R1-R6 on seeds 401/402 (amendment-14 scores)", **res), d / "r1_r6_401_402.json")
    for s in ("401", "402"):
        r = res[s]
        print(s, "R1 Sb-B", round(r["R1_Sb_minus_B"]["point"], 3), "R3 base", {k: round(v, 3) for k, v in r["R3_base"].items()},
              "R5", round(r["R5_noise_std_border_auc"]["direction_free"], 3))
        for a in ("A", "B", "Sb"):
            q = r[a]
            print("  ", a, "R1", round(q["R1_strat_auc"], 3), "R2", {k: round(v, 2) for k, v in q["R2"].items()},
                  "R3 inc27", round(q["R3"]["inc_over_27"], 3), "R4", round(q["R4_matched_auc"], 3), q["R4_n_matched"],
                  "R6 loss", round(q["R6"]["auc_loss"], 3), "share", round(q["R6"]["share_complete_higher"], 3))
    print(res["prestated_test"])


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    a14test() if "--a14test" in sys.argv[1:] else main()
