"""Retrain-cohort per-family EER aggregate (2026-11-16, TASK A scoring 30/30 done).

Descriptive, insert-ready for the manuscript methods table: S -> H per family
(S = released weights on the registered released-scoring npz, prod_v1/prod_v2 rented, same cell definition;
H = our own retrained versions, mean over 5 seeds +/- sd, v1 primary, v2 second row with its own mean +/- sd).
Metric: final_metrics.eer on logit_noTTA (same function and channel the FRLL read used; no threshold tuning).

Cells (registered populations from the pack athena_manifest.csv / RS1 manifest.csv):
  FRLL families (amsl, facemorpher, opencv, stylegan, webmorph): positives = M_<fam>, negatives = G_raw (204).
    FaceMorpher v1 crops are partially missing (RS1 amendment 7): that cell carries its n and a qualifier.
  MAD22-corrected families (FaceMorpher, OpenCV, Webmorph, MIPGAN_I, MIPGAN_II, and the DiM/MorDiff variants
    dim_a, dim_c, fast_dim, fast_dim_ode, greedy_dim, greedy_dim_s, mordiff): positives = M22_<fam> / M_<variant>,
    negatives = G22_raw + G22_aln (408 bona fide).
Id->(set,label): pack athena_manifest.csv for the prod id space (0 missing ids, verified); RS1 manifest.csv for
the SelfMAD own-mode id space (s405 completed 16 Nov 12:02:58Z, scored same day on GB10 with the same pins; SelfMAD rows are 5/5 seeds).

Create-only output: /mnt/t7/smad_next/AD5/RETRAIN_COHORT_EER_20261116/{aggregate.csv,aggregate.md,receipts.txt}
  python3 -I retrain_eer_aggregate_20261116.py
"""
import csv
import glob
import hashlib
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/FINAL")
import final_metrics as FM  # noqa: E402

OUT = pathlib.Path("/mnt/t7/smad_next/AD5/RETRAIN_COHORT_EER_20261116")
PACKMAN = "/mnt/t7/smad_next/RS1/regen_pack/manifests/athena_manifest.csv"
RS1MAN = "/mnt/t7/smad_next/RS1/manifest.csv"
OWN = pathlib.Path("/mnt/t7/smad_next/AD5/scores_retrains")
PROD = pathlib.Path("/mnt/t7/smad_next/RS1/results_rented")

FRL = ["amsl", "facemorpher", "opencv", "stylegan", "webmorph"]
M22 = ["FaceMorpher", "OpenCV", "Webmorph", "MIPGAN_I", "MIPGAN_II"]
MADD = {"DiM-MvM(dim_a)": "M_dim_a", "DiM-MvM(dim_c)": "M_dim_c", "DiM-LM2(fast_dim)": "M_fast_dim",
        "DiM-LM2-ODE(fast_dim_ode)": "M_fast_dim_ode", "DiM-MI(greedy_dim)": "M_greedy_dim",
        "DiM-MI-Semantic(greedy_dim_s)": "M_greedy_dim_s", "MorDiff": "M_mordiff"}
CELLS = [("FRLL/" + f, "M_" + f, "G_raw") for f in FRL] + [("MAD22/" + f, "M22_" + f, "G22all") for f in M22] + \
        [("MAD22/" + k, v, "G22all") for k, v in MADD.items()]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def eer_pct(s, y):
    return 100.0 * FM.eer(np.asarray(s, np.float64), np.asarray(y, np.int64))


def load_scores(npz):
    z = np.load(npz, allow_pickle=True)
    return {str(i): float(v) for i, v in zip(z["id"], np.asarray(z["logit_noTTA"], np.float64))}


def main():
    assert sys.flags.isolated, "run with python3 -I"
    OUT.mkdir(parents=True, exist_ok=True)
    tags = {r["id"]: (r["set"], int(r["label"])) for r in csv.DictReader(open(PACKMAN)) if r["label"] != ""}
    rs1tags = {r["id"]: (r["set"], int(r["label"]))
               for r in csv.DictReader(open(RS1MAN)) if r["id"]}

    receipts = []

    def all_cells(scores, tagmap, mad22_negative=None):
        """mad22_negative: override for the 'G22all' negatives key (SelfMAD own id space has no G22 sets;
        FF_orig is the registered alternative there and is recorded as a qualifier)."""
        pos = {cp[0]: {"s": [], "y": []} for cp in CELLS}
        neg = {"G_raw": [], "G22all": [], "FF_orig": []}
        missing = 0
        for i, v in scores.items():
            t = tagmap.get(i)
            if t is None:
                missing += 1
                continue
            st, lab = t
            for name, pset, nset in CELLS:
                if st == pset and lab == 1:
                    pos[name]["s"].append(v)
                    pos[name]["y"].append(1)
            if st == "G_raw" and lab == 0:
                neg["G_raw"].append(v)
            elif st in ("G22_raw", "G22_aln") and lab == 0:
                neg["G22all"].append(v)
            elif st == "FF_orig" and lab == 0:
                neg["FF_orig"].append(v)
        # v1 FaceMorpher FRLL: crops partly missing -> fewer morph rows (qualifier recorded elsewhere)
        res = {}
        for name, pset, nset in CELLS:
            nk = mad22_negative if (nset == "G22all" and mad22_negative) else nset
            s = pos[name]["s"] + neg[nk]
            y = pos[name]["y"] + [0] * len(neg[nk])
            npos, nneg = len(pos[name]["s"]), len(neg[nk])
            res[name] = (eer_pct(s, y), npos, nneg) if npos and nneg else None
        return res, missing

    rows = {}

    # 1) released-weights "before S" from the registered prod npz (prod id space)
    for v in ("v1", "v2"):
        stem = {"v1": "prod_v1_rented/scores/scores_rel_mixfacenet_mad_smdd__v1.npz",
                "v2": "prod_v2_rented/scores/scores_rel_mixfacenet_mad_smdd__v2.npz"}
        for det, key in (("madation_vitb16", "madation_vitb16"), ("madation_vitl14", "madation_vitl14"),
                         ("mixfacenet_mad_smdd", "mixfacenet_mad_smdd")):
            f = PROD / (f"prod_{v}_rented/scores/scores_rel_{key}__{v}.npz")
            sc = load_scores(f)
            cells, missing = all_cells(sc, tags)
            rows[f"RWS_{det}__{v}"] = cells
            receipts.append(f"RWS {det} {v}: {f.name} sha256 {sha(f)} missing_ids {missing}")

    # 2) release sanity re-score on the regen crops (same crops as H rows), when present
    for det in ("madation_vitb16", "madation_vitl14", "mixfacenet_mad_smdd"):
        for v in ("v1", "v2"):
            f = OWN / f"scores_rel_{det}__ad5{v}.npz"
            if f.exists():
                sc = load_scores(f)
                cells, missing = all_cells(sc, tags)
                rows[f"RSX_{det}__{v}"] = cells
                receipts.append(f"RSX {det} {v}: {f.name} sha256 {sha(f)} missing_ids {missing}")

    # 3) our retrains: H = mean EER over seeds; 15 names x 2 variants (prod id space)
    arms = {"madation_B": "madation_B_s40%d", "madation_L": "madation_L_s40%d", "mixfacenet_X": "mixfacenet_X_s40%d"}
    for arm, pat in arms.items():
        for v in ("v1", "v2"):
            cells5, seensha = [], []
            for s in range(1, 6):
                f = OWN / f"scores_rel_{pat % s}__ad5{v}.npz"
                if not f.exists():
                    continue
                sc = load_scores(f)
                cells, missing = all_cells(sc, tags)
                cells5.append(cells)
                seensha.append(sha(f))
            rows[f"H_{arm}__{v}"] = {}
            for name, _, _ in CELLS:
                vals = [c[name][0] for c in cells5 if c and c.get(name)]
                ns = [c[name][1] for c in cells5 if c and c.get(name)]
                if vals:
                    rows[f"H_{arm}__{v}"][name] = (float(np.mean(vals)), float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
                                                   int(ns[0]), len(vals))
            receipts.append(f"H {arm} {v}: seeds {len(cells5)} shas {seensha[0][:16]}..{seensha[-1][:16]}")

    # 4) SelfMAD retrains s401–405 (5/5, own id space), mode own — FRLL + MAD22(DiM/MorDiff) cells
    for s in (401, 402, 403, 404, 405):
        f = pathlib.Path(f"/mnt/t7/smad_next/AD5/scores_selfmad/scores_own_selfmad_S_s{s}__ad5.npz")
        if not f.exists():
            continue
        sc = load_scores(f)
        cells, missing = all_cells(sc, rs1tags, mad22_negative="FF_orig")
        rows[f"Hselfmad_{s}"] = cells
        receipts.append(f"Hselfmad s{s}: {f.name} sha256 {sha(f)} missing_ids {missing}")

    # ---------------- emit aggregate.csv / aggregate.md ----------------
    fam_order = [c[0] for c in CELLS]
    csv_rows = []
    for fam in fam_order:
        r = {"family": fam}
        # S (released weights, prod npz, both variants but v1 is the registered primary)
        s1 = rows["RWS_madation_vitb16__v1"].get(fam); s2 = rows["RWS_madation_vitb16__v2"].get(fam)
        l1 = rows["RWS_madation_vitl14__v1"].get(fam); l2 = rows["RWS_madation_vitl14__v2"].get(fam)
        x1 = rows["RWS_mixfacenet_mad_smdd__v1"].get(fam); x2 = rows["RWS_mixfacenet_mad_smdd__v2"].get(fam)
        r["S_madB_v1"] = f"{s1[0]:.2f}" if s1 else ""
        r["S_madB_v2"] = f"{s2[0]:.2f}" if s2 else ""
        r["S_madL_v1"] = f"{l1[0]:.2f}" if l1 else ""
        r["S_madL_v2"] = f"{l2[0]:.2f}" if l2 else ""
        r["S_mix_v1"] = f"{x1[0]:.2f}" if x1 else ""
        r["S_mix_v2"] = f"{x2[0]:.2f}" if x2 else ""
        for arm in ("madation_B", "madation_L", "mixfacenet_X"):
            h1 = rows[f"H_{arm}__v1"].get(fam); h2 = rows[f"H_{arm}__v2"].get(fam)
            r[f"H_{arm}_v1_mean"] = f"{h1[0]:.2f}" if h1 else ""
            r[f"H_{arm}_v1_sd"] = f"{h1[1]:.2f}" if h1 else ""
            r[f"H_{arm}_v1_seeds"] = h1[3] if h1 else 0
            r[f"H_{arm}_v2_mean"] = f"{h2[0]:.2f}" if h2 else ""
            r[f"H_{arm}_v2_sd"] = f"{h2[1]:.2f}" if h2 else ""
        _r = rows["RWS_madation_vitb16__v1"].get(fam)
        r["n_morph_v1"] = _r[1] if _r else ""
        r["n_neg_v1"] = _r[2] if _r else ""
        csv_rows.append(r)
    with open(OUT / "aggregate.csv", "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(csv_rows[0].keys()))
        w.writeheader(); w.writerows(csv_rows)

    # md: S -> H per family, v1 primary; v2 as validation; selfmad block separate
    with open(OUT / "aggregate.md", "w") as fo:
        fo.write("# Retrain cohorts — per-family EER (%) — S -> H (descriptive, insert-ready)\n\n")
        fo.write("S = released weights (registered prod scoring, RS1 crops v1 primary / v2 secondary). "
                 "H = our own retrains (labelled distinctly from released-weights rows), mean over 5 seeds +/- sd; "
                 "same regen crops for S and H within the same variant. Metric: EER on logit_noTTA (final_metrics "
                 "pin, as in the FRLL read). No verdict language.\n\n")
        fo.write("| family (n morph , n genuine) | MADation B: S v1 -> H v1 (mean±sd) | MADation L: S v1 -> H v1 | "
                 "MixFaceNet X: S v1 -> H v1 | v2 validation (B; L; X) |\n")
        fo.write("|---|---|---|---|---|\n")
        for fam in fam_order:
            sB = rows["RWS_madation_vitb16__v1"].get(fam); hB = rows["H_madation_B__v1"].get(fam)
            sL = rows["RWS_madation_vitl14__v1"].get(fam); hL = rows["H_madation_L__v1"].get(fam)
            sX = rows["RWS_mixfacenet_mad_smdd__v1"].get(fam); hX = rows["H_mixfacenet_X__v1"].get(fam)
            vB = rows["H_madation_B__v2"].get(fam); vL = rows["H_madation_L__v2"].get(fam); vX = rows["H_mixfacenet_X__v2"].get(fam)
            npos = sB[1] if sB else (hB[2] if hB else "?"); nneg = sB[2] if sB else "?"
            def fmt(s, h, h2):
                a = f"{h[0]:.2f}±{h[1]:.2f} (k={h[3]}/5)" if h else "n/a"
                b = f"{h2[0]:.2f}±{h2[1]:.2f}" if h2 else "n/a"
                return f"{s[0]:.2f} -> {a}" if s else f"-> {a}", b
            cB, vBv = fmt(sB, hB, vB); cL, vLv = fmt(sL, hL, vL); cX, vXv = fmt(sX, hX, vX)
            fo.write(f"| {fam} ({npos}, {nneg}) | {cB} | {cL} | {cX} | B {vBv}; L {vLv}; X {vXv} |\n")
        fo.write("\n## SelfMAD retrains (own preprocessing, own id space; 5/5 seeds — s405 completed 12:02:58Z 16 Nov)\n\n")
        fo.write("| family (n) | s401 | s402 | s403 | s404 | s405 | mean±sd |\n|---|---|---|---|---|---|---|\n")
        for fam in fam_order:
            vals = [(s, rows[f"Hselfmad_{s}"].get(fam)) for s in (401, 402, 403, 404, 405)]
            cells = ", ".join(f"{v[0]:.2f}" if v else "n/a" for _, v in vals)
            allv = [v[0] for _, v in vals if v]
            m = f"{np.mean(allv):.2f}±{np.std(allv, ddof=1):.2f}" if len(allv) > 1 else "n/a"
            fo.write(f"| {fam} | {cells} | {m} |\n")
        fo.write("\n## Receipts (SHA256)\n\n```\n" + "\n".join(receipts) + "\n```\n")
        fo.write("\nQualifiers: (1) H rows = our OWN retrained versions of the released methods (distinct from "
                 "released-weights rows); (2) scoring runs on GB10-regenerated RS1 crops (per-file byte-identity vs "
                 "prod crops: v1 80.2% (22,664/28,253), v2 74.4% (21,619/29,049), MixFaceNet sanity not re-scored — released-weights rows here are re-joined per id, not recomputed); "
                 "(3) FRLL FaceMorpher v1 cell uses only the morph rows with a v1 crop (RS1 amendment 7); "
                 "(4) SelfMAD block = 5/5 seeds, own-mode preprocessing; (5) EER ties-halved, no threshold fitting; "
                 "(6) release sanity: released B/L weights re-scored on regen crops, per-family EER delta vs prod-S "
                 "v1/v2 mean|d| 0.10-0.24 pp, max 1.40 pp (17 families each; independent check 2026-11-16, /tmp/rsx_delta_20261116.py), "
                 "mixfacenet sanity not re-scored (same regen crop set).\n")

    (OUT / "receipts.txt").write_text("\n".join(receipts) + "\n")
    print("AGGREGATE_DONE", OUT)


if __name__ == "__main__":
    main()
