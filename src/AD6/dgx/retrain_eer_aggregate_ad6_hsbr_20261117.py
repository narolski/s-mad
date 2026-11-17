"""AD6 Hsbr per-family EER aggregate (2026-11-17, H1 B + H3 X scored 20/20; H2 L appended when its 5 seeds land).

Adaptation of the AD5 pattern (src/AD5/score/retrain_eer_aggregate_20261116.py, commit c745230) for the
AD6 matched-recipe retrains ("Hsbr", WCSS ad6w arrays v3, tag h_*__ad6v1/ad6v2): SAME 17 cells, SAME id
space (prod / RS1 regen pack athena_manifest.csv; npz ids verified 28,253/28,253 in-manifest for s401 v1),
SAME metric (final_metrics.eer on logit_noTTA, no threshold tuning). Only the npz source and the emitted
blocks differ: per-seed EER + 5-seed mean±sd per arm (madation_B, mixfacenet_X; madation_L when 5/5).

  /home/narolski/mambamorph-code/.venv-spark/bin/python -I retrain_eer_aggregate_ad6_hsbr_20261117.py

Create-only output under experiments/AGENTIC_delivery_20261114/ (space policy: /mnt/t7 full):
  AD6_H_SBR_EER_20261117/ad6_h_sbr_eer.csv  (per-seed columns + mean/sd/n)
  AD6_H_SBR_EER_20261117/ad6_h_sbr_eer.md   (blocks also appended to RETRAIN_COHORT_EER_TABLE_20261116.md)
Reads scores_h_<name>__ad6<v>.npz from /home/narolski/ad6_stage/scores_h_sbr/.
"""
import csv
import hashlib
import pathlib
import sys

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/FINAL")
import final_metrics as FM  # noqa: E402

OUT = pathlib.Path("/home/narolski/smad-next/experiments/AGENTIC_delivery_20261114/AD6_H_SBR_EER_20261117")
COHORT = OUT.parent / "RETRAIN_COHORT_EER_TABLE_20261116.md"
PACKMAN = "/mnt/t7/smad_next/RS1/regen_pack/manifests/athena_manifest.csv"
SCORES = pathlib.Path("/home/narolski/ad6_stage/scores_h_sbr")

FRL = ["amsl", "facemorpher", "opencv", "stylegan", "webmorph"]
M22 = ["FaceMorpher", "OpenCV", "Webmorph", "MIPGAN_I", "MIPGAN_II"]
MADD = {"DiM-MvM(dim_a)": "M_dim_a", "DiM-MvM(dim_c)": "M_dim_c", "DiM-LM2(fast_dim)": "M_fast_dim",
        "DiM-LM2-ODE(fast_dim_ode)": "M_fast_dim_ode", "DiM-MI(greedy_dim)": "M_greedy_dim",
        "DiM-MI-Semantic(greedy_dim_s)": "M_greedy_dim_s", "MorDiff": "M_mordiff"}
CELLS = [(f"FRLL/{f}", "M_" + f, "G_raw") for f in FRL] + [(f"MAD22/{f}", "M22_" + f, "G22all") for f in M22] + \
        [("MAD22/" + k, v, "G22all") for k, v in MADD.items()]
ARMS = {"B": "madation_B_sbr_s40", "L": "madation_L_sbr_s40", "X": "mixfacenet_X_sbr_s40"}


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


def all_cells(scores, tagmap):
    pos = {cp[0]: [] for cp in CELLS}
    neg = {"G_raw": [], "G22all": []}
    missing = 0
    for i, v in scores.items():
        t = tagmap.get(i)
        if t is None:
            missing += 1
            continue
        st, lab = t
        for name, pset, nset in CELLS:
            if st == pset and lab == 1:
                pos[name].append(v)
        if st == "G_raw" and lab == 0:
            neg["G_raw"].append(v)
        elif st in ("G22_raw", "G22_aln") and lab == 0:
            neg["G22all"].append(v)
    ids = set(scores)
    res = {}
    for name, pset, nset in CELLS:
        npos = pos[name]
        nneg = neg[nset]
        res[name] = (eer_pct(npos + nneg, [1] * len(npos) + [0] * len(nneg)), len(npos), len(nneg)) \
            if npos and nneg else None
    return res, missing, sum(1 for i in ids if i in set(scores)) - missing


def main():
    assert sys.flags.isolated, "run with python -I"
    tags = {r["id"]: (r["set"], int(r["label"])) for r in csv.DictReader(open(PACKMAN)) if r["label"] != ""}
    receipts, rows, ncell = [], {}, {}
    for arm, pat in ARMS.items():
        for v in ("v1", "v2"):
            cells5, shas, miss_total = [], [], 0
            for s in range(1, 6):
                f = SCORES / f"scores_h_{pat}{s}__ad6{v}.npz"
                if not f.exists():
                    continue
                sc = load_scores(f)
                cells, missing, _ = all_cells(sc, tags)
                miss_total += missing
                cells5.append(cells)
                shas.append(sha(f))
                rows[f"Hsbr{arm}_s{s}__{v}"] = cells
            rows[f"Hsbr{arm}__{v}_list"] = cells5
            for name, _, _ in CELLS:
                vals = [c[name][0] for c in cells5 if c and c.get(name)]
                if vals:
                    ncell[f"Hsbr{arm}__{v}::{name}"] = (vals,
                                                        float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
                                                        cells5[0][name][1] if cells5[0].get(name) else 0,
                                                        cells5[0][name][2] if cells5[0].get(name) else 0,
                                                        len(vals))
            if cells5:
                receipts.append(f"Hsbr{arm} {v}: seeds scored {len(cells5)}/5 shas {shas[0][:16]}..{shas[-1][:16]}"
                                f" missing_ids_total {miss_total}")
    # receipts csv (RECEIPTS_sha256.csv) cross-check: every scores npz sha
    rec_csv = SCORES / "RECEIPTS_sha256.csv"

    OUT.mkdir(parents=True, exist_ok=True)
    fam_order = [c[0] for c in CELLS]
    # ---- csv: per-seed EER + mean/sd ----
    with open(OUT / "ad6_h_sbr_eer.csv", "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["family", "n_morph_v1", "n_genuine_v1"] +
                   [f"Hsbr{arm}_{v}_s{s}_eer" for arm in ("B", "X") for v in ("v1", "v2") for s in range(1, 6)] +
                   [f"Hsbr{arm}_{v}_{k}" for arm in ("B", "X") for v in ("v1", "v2") for k in ("mean", "sd", "k", "n_morph", "n_genuine")])
        for fam in fam_order:
            nm, ng = ncell.get(f"HsbrB__v1::{fam}", ([], 0, 0, 0, 0))[2:4]
            row = [fam, nm, ng]
            for arm in ("B", "X"):
                for v in ("v1", "v2"):
                    c = ncell.get(f"Hsbr{arm}__{v}::{fam}")
                    row += [f"{x:.2f}" for x in c[0]] if c else [""] * 5
                    row += ([f"{np.mean(c[0]):.2f}", f"{c[1]:.2f}", c[4], c[2], c[3]] if c else ["", "", 0, "", ""])
            w.writerow(row)

    def block(arm, label):
        lines = [f"## AD6 Hsbr {label} retrains (matched-recipe, WCSS ad6w v3; own crops, prod id space)"
                 f"{' — 5/5 seeds' if arm != 'L' else ' — L rows appended when 5/5'}",
                 "",
                 "| family (n morph, n genuine) | s401 | s402 | s403 | s404 | s405 | mean±sd (v1) | mean±sd (v2) |",
                 "|---|---|---|---|---|---|---|---|"]
        for fam in fam_order:
            per = []
            for s in range(1, 6):
                c = rows.get(f"Hsbr{arm}_s{s}__v1", {}).get(fam)
                per.append(f"{c[0]:.2f}" if c else "n/a")
            m1 = ncell.get(f"Hsbr{arm}__v1::{fam}")
            m2 = ncell.get(f"Hsbr{arm}__v2::{fam}")
            ms1 = f"{np.mean(m1[0]):.2f}±{m1[1]:.2f} (k={m1[4]}/5)" if m1 else "n/a"
            ms2 = f"{np.mean(m2[0]):.2f}±{m2[1]:.2f} (k={m2[4]}/5)" if m2 else "n/a"
            nm = m1[2] if m1 else "?"
            ng = m1[3] if m1 else "?"
            lines.append(f"| {fam} ({nm}, {ng}) | {', '.join(per)} | {ms1} | {ms2} |")
        return "\n".join(lines)

    md = ["# AD6 Hsbr (matched-recipe retrains) — per-family EER (%) — 2026-11-17", "",
          "Hsbr rows = AD6 matched-recipe retrains trained on the WCSS ad6w arrays (v3 wheel set), scored through the SAME",
          "Athena-registered path as AD5 (ad5_score_athena.py, frozen RS1 regen crops, score_v1/score_v2 manifests, pins",
          "56bb1244/42806acb asserted), tags h_<name>__ad6v1/ad6v2. v1 primary, v2 validation. Metric: EER on logit_noTTA",
          "(final_metrics pin; ties-halved, no threshold fitting). Id space: prod athena_manifest.csv (missing_ids 0", ""]
    md.append(block("B", "madation_B (ViT-B/16)"))
    md.append("")
    md.append(block("X", "mixfacenet_X"))
    if any(("HsbrL_s" in r) or (f"HsbrL__" in str(rows.keys())) for r in [str(rows.keys())]):
        md.append("")
        md.append(block("L", "madation_L (ViT-L/14)"))
    md += ["", "## Receipts (SHA256, scores npz; feat npz in scores_h_sbr/RECEIPTS_sha256.csv)", "", "```",
           "\n".join(receipts),
           f"receipts_csv {rec_csv}: lines {sum(1 for _ in open(rec_csv))}", "```", "",
           "Adaptation notes vs AD5 aggregate (c745230): source npz scores_h_<scriptname>__ad6<v>.npz in",
           "/home/narolski/ad6_stage/scores_h_sbr/ (script names; WCSS tars madation_B_v3sbr_s40N.tar renamed at pull stage",
           "after sha256 verification — scoring path unchanged); madation_L block pending (H2 lands ~02:30-03:30Z 17 Nov).",
           "Space policy: /mnt/t7 full -> outputs under experiments/. Pulled tars + converted weights deleted by the scoring",
           "script per seed after receipts (sha256 preserved in RECEIPTS_sha256.csv).", ""]
    (OUT / "ad6_h_sbr_eer.md").write_text("\n".join(md))

    # ---- append blocks to the cohort table (idempotent via marker) ----
    marker = "## AD6 Hsbr madation_B (ViT-B/16)"
    cohort = COHORT.read_text() if COHORT.exists() else ""
    add = "\n".join([block("B", "madation_B (ViT-B/16)"), "", block("X", "mixfacenet_X")])
    if ("## AD6 Hsbr madation_L" not in cohort) and any(rows.get(f"HsbrL_s{j}__v1") is not None for j in range(1, 6)):
        add += "\n\n" + block("L", "madation_L (ViT-L/14)")
    if marker not in cohort:
        with open(COHORT, "a") as fo:
            fo.write("\n\n" + add + "\n")
        print(f"APPENDED blocks to {COHORT}")
    else:
        print("cohort table already contains AD6 Hsbr blocks (marker found); not re-appending")
    print("AD6_H_SBR_AGGREGATE_DONE", OUT)


if __name__ == "__main__":
    main()
