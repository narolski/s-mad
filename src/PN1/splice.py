"""PN1 amendment 8: frozen heads with spliced positives (arms S-a, S-b) beside A0 and B0, and the face-only /
face-blanked reads.  python3 -I splice.py [--backbones clip224,dinov3_512]
Outputs: experiments/PN1_.../splice/<bb>_<arm>_s<seed>.json and splice_summary.json."""
import argparse
import csv
import os
import pathlib
import sys

os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pn1lib as K  # noqa: E402
import reads as RD  # noqa: E402
import tier0 as T0  # noqa: E402


def splice_rows():
    lad, _ = K.split_tables()
    out = []
    for n in ("splice_nat", "splice_blank"):
        for r in csv.DictReader(open(K.PN1 / "lists" / f"{n}.csv")):
            h = r["p1"]
            base = r["rung"].split("_")[0]
            klass = "attack" if base in ("S4", "R4") else "single"
            persons = tuple(sorted({h, r["p2"]})) if base in ("S4", "R4") else (h,)
            role = lad[h]["role"]
            if role == "test" and lad[h]["test_read"] != "1":
                role = "excluded"
            if any(lad[p]["is_val"] == "1" for p in persons if p in lad):
                role = "excluded"
            out.append(dict(id=r["id"], path=r["path"], src=n, fam="splice", klass=klass, rung=r["rung"], strength="",
                            tool=r["tool"], pool="ladder_" + h.split(":")[0], host=h, persons=persons, role=role,
                            cell="", neutral=None, pair=h, field="", train_morph=lad[h]["train_morph"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbones", default="clip224,dinov3_512")
    a = ap.parse_args()
    cat = K.catalog()
    cat += T0.soft_cat_rows({r["id"] for r in cat})
    sp = splice_rows()
    sets = T0.train_sets(cat)
    trS4 = [r for r in sp if r["rung"] == "S4" and r["tool"] == "opencv" and r["role"] == "train" and r["train_morph"] == "1"]
    trS0 = [r for r in sp if r["rung"] == "S0" and r["tool"] == "opencv" and r["role"] == "train"]
    trS3 = [r for r in sp if r["rung"] == "S3" and r["tool"] == "opencv" and r["role"] == "train"]
    arms = {"A0": sets["A0"], "B0": sets["B0"], "S-a": trS4 + trS0, "S-b": sets["B0"] + trS4 + trS0 + trS3}
    # cues: 27 statistics (512) + 12 certificate cues (224) [+ sharpness ratio for natives]
    import cert as CE
    cues, names = {}, None
    for f in [K.AF0 / "cues" / "ar1.npz"] + sorted((K.PN1 / "cues").glob("*.npz")):
        if f.name.startswith(("cert_", "ratio_")) or "_limit" in f.name:
            continue
        z = np.load(f)
        names = [str(n) for n in z["names"]]
        cues.update({str(i): c for i, c in zip(z["ids"], z["cues"])})
    c224 = CE.load_cues("c224")
    cues = {i: np.r_[v, c224[i]] for i, v in cues.items() if i in c224}
    names = names + [n + "@224" for n in CE.PIX]
    zr = np.load(K.PN1 / "cues" / "ratio_splice.npz")
    ratio = {str(i): v for i, v in zip(zr["ids"], zr["ratio"])}
    cues_r = {i: np.r_[v, ratio[i]] for i, v in cues.items() if i in ratio}
    names_r = names + ["inside_outside_sharpness"]
    out = K.RES / "splice"
    out.mkdir(parents=True, exist_ok=True)
    summ = {}
    for bb in a.backbones.split(","):
        idx, X, _ = K.load_features(bb)
        rows_all = [r for r in cat + sp if r["id"] in idx]
        P = RD.pools([r for r in rows_all if r["fam"] != "splice"])
        for r in sp:
            if r["role"] == "test" and r["tool"] == "opencv" and r["id"] in idx:
                P.setdefault("T_" + r["rung"], []).append(r)
        for arm, rows in arms.items():
            rows = [r for r in rows if r["id"] in idx]
            rows, strata = T0.balance_rows(rows)
            y = np.array([1 if r["klass"] == "attack" else 0 for r in rows])
            Xtr = X[[idx[r["id"]] for r in rows]]
            for seed in (401, 402, 403, 404, 405):
                h = K.fit_head(Xtr, y, [r["persons"] for r in rows], seed)
                ids = list(idx)
                S = dict(zip(ids, K.head_score(h, X[[idx[i] for i in ids]]).tolist()))
                R = RD.all_reads(S, P, 0.0, (cues, names))
                R["splice"] = {
                    "S0_vs_S4": RD.paired(S, P, "T_S4", "T_S0", (cues_r, names_r)),
                    "S3_vs_S4": RD.paired(S, P, "T_S4", "T_S3"),
                    "R2w_vs_R4_native_with_ratio": RD.paired(S, P, "T_R4_opencv", "T_R2w_opencv", (cues_r, names_r)),
                    "S0_vs_S4_face_only": RD.paired(S, P, "T_S4_bg", "T_S0_bg", (cues, names)),
                    "S0_vs_S4_face_blanked": RD.paired(S, P, "T_S4_face", "T_S0_face", (cues, names)),
                    "R2w_vs_R4_face_only": RD.paired(S, P, "T_R4_bg", "T_R2w_bg", (cues, names)),
                    "R2w_vs_R4_face_blanked": RD.paired(S, P, "T_R4_face", "T_R2w_face", (cues, names)),
                    "R2w4_vs_R4_face_only": RD.paired(S, P, "T_R4_bg", "T_R2w4_bg", (cues, names)),
                    "R2w4_vs_R4_face_blanked": RD.paired(S, P, "T_R4_face", "T_R2w4_face", (cues, names))}
                R["marks"] = RD.marks_tier0(R)
                R["head"] = dict(C=h["C"], n_train=len(rows), n_unique=len({r["id"] for r in rows}), strata=strata)
                K.dump(R, out / f"{bb}_{arm}_s{seed}.json")
                if seed == 401:
                    sx = R["splice"]
                    g = lambda k: (round(sx[k].get("auc", float("nan")), 3), sx[k].get("best_stat_auc"))  # noqa: E731
                    summ[f"{bb}_{arm}"] = {k: g(k) for k in sx} | dict(
                        shift61=R["c"]["R0_to_R0_61"].get("shift_sd"), H1=R["d"].get("auc"),
                        mad_ocv_e7=R["e"]["OpenCV_e7"].get("eer_eer"), mad_wm_e7=R["e"]["Webmorph_e7"].get("eer_eer"),
                        cam_flag61=R["fixed"]["cam"]["T_R0_61"]["rate"],
                        cam_famiss=R["fixed"]["cam"]["_family_mean_miss_gating"]["mean"])
                print("DONE", bb, arm, seed, flush=True)
    K.dump(summ, out / "splice_summary.json")


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
