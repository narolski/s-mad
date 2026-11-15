"""PN1 amendment 11: post hoc items (labelled post hoc), face-only heads (H-new-3), face-blanked benchmark reads (H-new-5).
  python3 -I posthoc2.py  -> experiments/PN1_.../posthoc2/posthoc2.json"""
import csv
import os
import pathlib
import sys

os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pn1lib as K  # noqa: E402
import reads as RD  # noqa: E402
import splice as SP  # noqa: E402
import tier0 as T0  # noqa: E402
import cert as CE  # noqa: E402
import bracket as BR  # noqa: E402


def floor3():
    """dev-fitted logistic on seam tone (2), sharpness ratio, band5@224 for S0 vs S4 natives -> score per id."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    zt = np.load(K.PN1 / "cues" / "tone_splice.npz")
    tone = {str(i): v for i, v in zip(zt["ids"], zt["tone"])}
    zr = np.load(K.PN1 / "cues" / "ratio_splice.npz")
    rat = {str(i): v for i, v in zip(zr["ids"], zr["ratio"])}
    c224 = CE.load_cues("c224")
    b5 = CE.PIX.index("band5")
    lad, _ = K.split_tables()
    feats, lab, role, ids = [], [], [], []
    for i in tone:
        rung = i.split("_")[1]
        if rung not in ("S0", "S4") or i not in rat or i not in c224:
            continue
        host = ":".join(i.split("_")[3:5])
        feats.append([tone[i][0], tone[i][1], np.log(rat[i] + 1e-6), c224[i][b5]])
        lab.append(1 if rung == "S4" else 0)
        role.append(lad[host]["role"])
        ids.append(i)
    X, y, role = np.array(feats), np.array(lab), np.array(role)
    dev = role == "dev"
    sc = StandardScaler().fit(X[dev])
    m = LogisticRegression(max_iter=5000).fit(sc.transform(X[dev]), y[dev])
    s = m.decision_function(sc.transform(X))
    te = role == "test"
    return dict(zip(ids, s)), dict(test_auc=K.auc(s[te & (y == 1)], s[te & (y == 0)]),
                                   dev_auc=K.auc(s[dev & (y == 1)], s[dev & (y == 0)]), coef=m.coef_.ravel().tolist())


def main():
    cat = K.catalog()
    cat += T0.soft_cat_rows({r["id"] for r in cat})
    sp = SP.splice_rows()
    sets = T0.train_sets(cat)
    trS4 = [r for r in sp if r["rung"] == "S4" and r["tool"] == "opencv" and r["role"] == "train" and r["train_morph"] == "1"]
    trS0 = [r for r in sp if r["rung"] == "S0" and r["tool"] == "opencv" and r["role"] == "train"]
    trS3 = [r for r in sp if r["rung"] == "S3" and r["tool"] == "opencv" and r["role"] == "train"]
    lad, _ = K.split_tables()
    fo = []
    for r in csv.DictReader(open(K.PN1 / "lists" / "faceonly_train.csv")):
        base = r["rung"].split("_")[0]
        att = base in ("S4", "R4")
        fo.append(dict(id=r["id"], fam="splice", klass="attack" if att else "single", rung=r["rung"], strength="",
                       tool="opencv", pool="ladder_" + r["p1"].split(":")[0], host=r["p1"],
                       persons=tuple(sorted({r["p1"], r["p2"]})) if att else (r["p1"],), role="train"))
    arms = {"A0": sets["A0"], "B0": sets["B0"], "Bn0": sets["Bn0"], "S-a": trS4 + trS0, "S-b": sets["B0"] + trS4 + trS0 + trS3,
            "F-faceonly": fo}
    fl_score, fl_info = floor3()
    out = {"post_hoc": True, "floor3": fl_info}
    # cues for the 39-statistic floor on blanked copies
    cues, names = {}, None
    for f in [K.AF0 / "cues" / "ar1.npz"] + sorted((K.PN1 / "cues").glob("*.npz")):
        if f.name.startswith(("cert_", "ratio_", "tone_")) or "_limit" in f.name:
            continue
        z = np.load(f)
        names = [str(n) for n in z["names"]]
        cues.update({str(i): c for i, c in zip(z["ids"], z["cues"])})
    c224 = CE.load_cues("c224")
    cues = {i: np.r_[v, c224[i]] for i, v in cues.items() if i in c224}
    names = names + [n + "@224" for n in CE.PIX]
    bb_rows = list(csv.DictReader(open(K.PN1 / "lists" / "bench_blank.csv")))
    rng = np.random.default_rng(20261124)
    for bb in ("clip224", "dinov3_512"):
        idx, X, _ = K.load_features(bb)
        P = RD.pools([r for r in cat if r["id"] in idx])
        for r in sp:
            if r["role"] == "test" and r["tool"] == "opencv" and r["id"] in idx:
                P.setdefault("T_" + r["rung"], []).append(r)
        PB = {}
        for r in bb_rows:
            if r["id"] in idx:
                c = r["cell"]
                if r["set"] == "h1" or c.startswith("h1"):
                    PB.setdefault("H1_" + ("morph" if r["rung"] == "morph" else "bona"), []).append(r)
                elif c == "mad22_BonaFide":
                    PB.setdefault("MAD22_bona_native", []).append(r)
                else:
                    fam = c.split("_", 1)[1]
                    PB.setdefault(f"MAD22_{fam}_{'morph' if r['rung'] == 'morph' else 'e7'}", []).append(r)
        for arm, rows0 in arms.items():
            rows0 = [r for r in rows0 if r["id"] in idx]
            rows, _ = T0.balance_rows(rows0)
            y = np.array([1 if r["klass"] == "attack" else 0 for r in rows])
            h = K.fit_head(X[[idx[r["id"]] for r in rows]], y, [r["persons"] for r in rows], 401)
            ids = list(idx)
            S = dict(zip(ids, K.head_score(h, X[[idx[i] for i in ids]]).tolist()))
            res = {}
            x = RD.paired(S, P, "T_S4", "T_S0")
            pos = [r for r in P["T_S4"]]
            neg = [r for r in P["T_S0"]]
            ex = K.paired_auc_ci(RD.scores_of(S, pos), RD.scores_of(S, neg), [RD.unit(r) for r in pos], [RD.unit(r) for r in neg],
                                 extra={"floor3": (np.array([fl_score[r["id"]] for r in pos]), np.array([fl_score[r["id"]] for r in neg]))})
            res["S0_vs_S4_excess_floor3"] = {k: ex[k] for k in ("auc", "lo", "hi", "best_stat_auc", "excess", "excess_lo", "excess_hi")}
            for k, (p1, p2) in {"faceonly_S0_vs_S4": ("T_S4_bg", "T_S0_bg"), "faceonly_R2w4_vs_R4": ("T_R4_bg", "T_R2w4_bg"),
                                "faceblanked_R2w_vs_R4": ("T_R4_face", "T_R2w_face")}.items():
                z = RD.paired(S, P, p1, p2, (cues, names))
                res[k] = {kk: z.get(kk) for kk in ("auc", "lo", "hi", "best_stat", "best_stat_auc", "excess", "excess_lo", "excess_hi")}
            T = RD.thresholds(S, P, 0.0)
            # brackets (c) margin and (d) fixed threshold, (a) face-only
            a_ = {r["host"]: S[r["id"]] for r in P["T_R4_opencv"]}
            b_ = {r["host"]: S[r["id"]] for r in P["T_R2w_opencv"]}
            c_ = {r["host"]: S[r["id"]] for r in P["T_R2w_opencv_61"]}
            r0 = {r["host"]: S[r["id"]] for r in P["T_R0"]}
            r61 = {r["host"]: S[r["id"]] for r in P["T_R0_61"]}
            hs = sorted(set(a_) & set(b_) & set(c_) & set(r0) & set(r61))
            un = [RD.cyc(h_) for h_ in hs]
            res["bracket_c_margin"] = BR.share_ci(np.array([a_[q] - max(b_[q], c_[q]) > (r61[q] - r0[q]) for q in hs]), un)
            res["bracket_d_tau_cam"] = BR.share_ci(np.array([a_[q] > T["cam"] and b_[q] <= T["cam"] and c_[q] <= T["cam"] for q in hs]), un)
            fa = {r["host"]: S[r["id"]] for r in P["T_S4_bg"]}
            fb = {r["host"]: S[r["id"]] for r in P["T_S0_bg"]}
            hf = sorted(set(fa) & set(fb))
            res["bracket_a_faceonly_S4_above_S0"] = BR.share_ci(np.array([fa[q] > fb[q] for q in hf]), [RD.cyc(q) for q in hf])
            # H-new-5: native against face-blanked benchmark copies
            for fam in ("OpenCV", "Webmorph"):
                for g in ("native", "e7"):
                    neg_n = "MAD22_bona_native" if g == "native" else f"MAD22_{fam}_e7"
                    nat = RD.unpaired(S, P, f"MAD22_{fam}_morph", neg_n)
                    blk = RD.unpaired(S, PB, f"MAD22_{fam}_morph", neg_n)
                    res[f"MAD22_{fam}_{g}_EER_native_vs_faceblanked"] = (nat.get("eer_eer"), blk.get("eer_eer"))
            res["H1_AUC_native_vs_faceblanked"] = (RD.unpaired(S, P, "H1_morph", "H1_bona").get("auc"),
                                                    RD.unpaired(S, PB, "H1_morph", "H1_bona").get("auc"))
            # training-person resampling (10 draws)
            pers = sorted({p for r in rows0 for p in r["persons"]})
            ee, mm = [], []
            for k in range(10):
                draw = rng.choice(pers, len(pers), replace=True)
                cnt = {p: 0 for p in pers}
                for p in draw:
                    cnt[p] += 1
                rr = []
                for r in rows0:
                    m_ = min(cnt[p] for p in r["persons"])
                    rr += [r] * m_
                rr, _ = T0.balance_rows(rr)
                yy = np.array([1 if r["klass"] == "attack" else 0 for r in rr])
                hk = K.fit_head(X[[idx[r["id"]] for r in rr]], yy, [r["persons"] for r in rr], 401, Cs=(h["C"],))
                Sk = dict(zip(ids, K.head_score(hk, X[[idx[i] for i in ids]]).tolist()))
                Rk = RD.all_reads(Sk, P, 0.0)
                ee.append((Rk["e"]["OpenCV_e7"]["eer_eer"], Rk["e"]["Webmorph_e7"]["eer_eer"]))
                mm.append(Rk["fixed"]["cam"]["_family_mean_miss_gating"]["mean"])
            ee = np.array(ee)
            res["resampling_10"] = dict(mad22_ocv_e7_eer=[float(np.min(ee[:, 0])), float(np.median(ee[:, 0])), float(np.max(ee[:, 0]))],
                                        mad22_wm_e7_eer=[float(np.min(ee[:, 1])), float(np.median(ee[:, 1])), float(np.max(ee[:, 1]))],
                                        cam_gating_miss=[float(np.min(mm)), float(np.median(mm)), float(np.max(mm))])
            out[f"{bb}_{arm}"] = res
            print("DONE", bb, arm, flush=True)
    d = K.RES / "posthoc2"
    d.mkdir(parents=True, exist_ok=True)
    K.dump(out, d / "posthoc2.json")


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
