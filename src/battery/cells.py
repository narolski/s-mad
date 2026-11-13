"""Shared test battery (BATTERY): cell-level check of the regression. For each listed cell of the shortcut audit table
(SA1 result.md at c4cd8dc), the range the table states is recomputed from the battery's records built from stored logits
(battery.stored) and compared at the table's own precision. A cell passes when min and max over the stated seeds,
rounded as printed, equal the printed bounds. Statistics only; nothing is decided here.
  cd src && python -m battery.cells --stored /mnt/t7/smad_next/BATTERY/stored --out ../experiments/BATTERY_shared-test-battery/cells_check_v1.json"""
import argparse
import json
import pathlib
import statistics

from .rows import get

# (cell, table text, arms, block set, block, paths (pooled), scale, decimals, lo, hi, kind)
# kind "range": min and max over seeds (and pooled paths); "mean_sd": mean and SD (ddof 1) over seeds
C = [
    ("1-A", "FFHQ own-rule flags native 6.4-10.7%", ["A"], "FS1block", "FS1", ["record/flags_own/ffhq_bona_orig"], 100, 1, 6.4, 10.7, "range"),
    ("1-A", "paired share rising [0.527, 0.626]", ["A"], "FS1block", "FS1", ["record/share_rising"], 1, 3, 0.527, 0.626, "range"),
    ("1-B", "share rising [0.180, 0.326]", ["B"], "FS1block", "FS1", ["record/share_rising"], 1, 3, 0.180, 0.326, "range"),
    ("1-Sb", "share rising [0.084, 0.175]", ["Sb"], "FS1block", "FS1", ["record/share_rising"], 1, 3, 0.084, 0.175, "range"),
    ("1-Sb (C2P)", "+1.0 to +3.8 points at 61.2 px (4 gate-passed seeds)", ["Sb"], "FS1block", "C2P", ["fm61/d_flag"], 100, 1, 1.0, 3.8, "range"),
    ("1-Sb (C2P)", "-0.3 to +3.4 points at 112.7 px", ["Sb"], "FS1block", "C2P", ["amsl112/d_flag"], 100, 1, -0.3, 3.4, "range"),
    ("2-Sb", "morph shift +0.06 to +0.11 SD at 61.2 px", ["Sb"], "FS1block", "C2P", ["fm61/d_mean_att_sd"], 1, 2, 0.06, 0.11, "range"),
    ("2-Sb", "morph shift -0.02 to +0.04 SD at 112.7 px", ["Sb"], "FS1block", "C2P", ["amsl112/d_mean_att_sd"], 1, 2, -0.02, 0.04, "range"),
    ("4-A (MEDS)", "flag shares A 0.013-0.051", ["A"], "FS1block", "MEDS", ["flag"], 1, 3, 0.013, 0.051, "range"),
    ("4-B (MEDS)", "B 0.001-0.029", ["B"], "FS1block", "MEDS", ["flag"], 1, 3, 0.001, 0.029, "range"),
    ("4-Sb (MEDS)", "Sb 0.001-0.005", ["Sb"], "FS1block", "MEDS", ["flag"], 1, 3, 0.001, 0.005, "range"),
    ("4-Sp (MEDS)", "Sp 0.003-0.013 (printed)", ["Sp"], "FS1block", "MEDS", ["flag"], 1, 3, 0.003, 0.013, "range"),
    ("4-A", "F-bar 0.023 +- 0.019", ["A"], "FS1block", "TT1", ["r5/Fbar"], 1, 3, 0.023, 0.019, "mean_sd"),
    ("4-Sb", "F-bar 0.020 +- 0.012", ["Sb"], "FS1block", "TT1", ["r5/Fbar"], 1, 3, 0.020, 0.012, "mean_sd"),
    ("4-Sp", "F-bar 0.023 / 0.030 / 0.033", ["Sp"], "FS1block", "TT1", ["r5/Fbar"], 1, 3, 0.023, 0.033, "range"),
    ("4-Sp", "F_max 0.060-0.114", ["Sp"], "FS1block", "TT1", ["r5/Fmax"], 1, 3, 0.060, 0.114, "range"),
    ("5-Sb (Z3)", "CFP-FF-shaped border blanked in: Sb 0.029-0.163", ["Sb"], "FS1block", "TT1", ["printed/border_flag/cfp_ff"], 1, 3, 0.029, 0.163, "range"),
    ("5-B (Z3)", "B 0.000-0.019", ["B"], "FS1block", "TT1", ["printed/border_flag/cfp_ff"], 1, 3, 0.000, 0.019, "range"),
    ("6-A", "R2w flagged 0%", ["A"], "FS1block", "PR1", ["pools/lad_R2w_opencv_test_nat/above_own"], 100, 1, 0.0, 0.0, "range"),
    ("6-A, 6-B, 6-Sb", "R4 vs R2w 1.000", ["A", "B", "Sb"], "FS1block", "PR1", ["auc/R4_vs_R2w_opencv_test"], 1, 3, 1.000, 1.000, "range"),
    ("6-Sb", "R2w flagged 0-0.5%", ["Sb"], "FS1block", "PR1", ["pools/lad_R2w_opencv_test_nat/above_own"], 100, 1, 0.0, 0.5, "range"),
    ("7-A", "R3 flagged 94.8-99.5%", ["A"], "FS1block", "PR1", ["pools/lad_R3_opencv_test_nat/above_own"], 100, 1, 94.8, 99.5, "range"),
    ("7-A", "R4 vs R3 0.72-0.75", ["A"], "FS1block", "PR1", ["auc/R4_vs_R3_opencv_test"], 1, 2, 0.72, 0.75, "range"),
    ("7-A", "R3m 97.9-99.5%", ["A"], "FS1block", "PR1", ["pools/lad_R3m_opencv_test_nat/above_own"], 100, 1, 97.9, 99.5, "range"),
    ("7-A", "R4 vs R3m 0.77-0.79", ["A"], "FS1block", "PR1", ["auc/R4_vs_R3m_opencv_test"], 1, 2, 0.77, 0.79, "range"),
    ("7-B", "R3 90.6-95.3%", ["B"], "FS1block", "PR1", ["pools/lad_R3_opencv_test_nat/above_own"], 100, 1, 90.6, 95.3, "range"),
    ("7-B", "R4 vs R3 0.75-0.79", ["B"], "FS1block", "PR1", ["auc/R4_vs_R3_opencv_test"], 1, 2, 0.75, 0.79, "range"),
    ("7-B", "R3m 94.8-97.4%", ["B"], "FS1block", "PR1", ["pools/lad_R3m_opencv_test_nat/above_own"], 100, 1, 94.8, 97.4, "range"),
    ("7-Sb", "R3 83.2-88.5%", ["Sb"], "FS1block", "PR1", ["pools/lad_R3_opencv_test_nat/above_own"], 100, 1, 83.2, 88.5, "range"),
    ("7-Sb", "R4 vs R3 0.80-0.85", ["Sb"], "FS1block", "PR1", ["auc/R4_vs_R3_opencv_test"], 1, 2, 0.80, 0.85, "range"),
    ("7-Sb", "R3m 95.8-96.9%", ["Sb"], "FS1block", "PR1", ["pools/lad_R3m_opencv_test_nat/above_own"], 100, 1, 95.8, 96.9, "range"),
    ("8-A", "test S3 flagged 2.1-5.8%", ["A"], "FS1block", "PR1", ["pools/spl_S3_test/above_own"], 100, 1, 2.1, 5.8, "range"),
    ("8-B", "test S3 flagged 0.5-3.7%", ["B"], "FS1block", "PR1", ["pools/spl_S3_test/above_own"], 100, 1, 0.5, 3.7, "range"),
    ("8-Sb", "test S3 flagged 37.2-48.2%", ["Sb"], "FS1block", "PR1", ["pools/spl_S3_test/above_own"], 100, 1, 37.2, 48.2, "range"),
    ("8-Sb", "S4 vs S3 0.72-0.74", ["Sb"], "FS1block", "PR1", ["auc/S4_vs_S3_test"], 1, 2, 0.72, 0.74, "range"),
    ("8-Sb (BD1)", "S4 vs S3 within D quintiles 0.697-0.729 (FS1)", ["Sb"], "FS1block", "BD1", ["primary"], 1, 3, 0.697, 0.729, "range"),
    ("8-Sb (BD1)", "pure-D reference 0.557", ["Sb"], "FS1block", "BD1", ["reference"], 1, 3, 0.557, 0.557, "range"),
    ("8-Sp", "development S3 flagged 0.65-0.73", ["Sp"], "FS1block", "PR1", ["pools/spl_S3_dev/above_own"], 1, 2, 0.65, 0.73, "range"),
    ("9-A", "S0 flagged 0-0.5%", ["A"], "FS1block", "PR1", ["pools/spl_S0_test/above_own"], 100, 1, 0.0, 0.5, "range"),
    ("9-A", "S4 vs S0 0.75-0.83", ["A"], "FS1block", "PR1", ["auc/S4_vs_S0_test"], 1, 2, 0.75, 0.83, "range"),
    ("9-B", "S0 flagged 0%", ["B"], "FS1block", "PR1", ["pools/spl_S0_test/above_own"], 100, 1, 0.0, 0.0, "range"),
    ("9-B", "S4 vs S0 0.68-0.78", ["B"], "FS1block", "PR1", ["auc/S4_vs_S0_test"], 1, 2, 0.68, 0.78, "range"),
    ("9-Sb", "S4 vs S0 0.985-0.994", ["Sb"], "FS1block", "PR1", ["auc/S4_vs_S0_test"], 1, 3, 0.985, 0.994, "range"),
    ("9-Sb", "development S0 0 of 100 on all five", ["Sb"], "FS1block", "PR1", ["pools/spl_S0_dev/above_own"], 100, 0, 0, 0, "range"),
    ("9-Sp", "dev S0 flagged Sp 0.01-0.03", ["Sp"], "FS1block", "PR1", ["pools/spl_S0_dev/above_own"], 1, 2, 0.01, 0.03, "range"),
    ("10-A, B, Sb", "224 px camera-photo flags 0-1.2% for every network", ["A", "B", "Sb"], "FS1block", "TT1", ["printed/geo_flag/g224"], 100, 1, 0.0, 1.2, "range"),
    ("10-A", "112 px path A 0.185-0.504", ["A"], "FS1block", "TT1", ["printed/geo_flag/g112"], 1, 3, 0.185, 0.504, "range"),
    ("10-B", "112 px path B 0.000-0.012", ["B"], "FS1block", "TT1", ["printed/geo_flag/g112"], 1, 3, 0.000, 0.012, "range"),
    ("10-Sb", "112 px path Sb 0.022-0.091", ["Sb"], "FS1block", "TT1", ["printed/geo_flag/g112"], 1, 3, 0.022, 0.091, "range"),
    ("10-Sp", "geometry-112 flag 0.024-0.084", ["Sp"], "FS1block", "TT1", ["printed/geo_flag/g112"], 1, 3, 0.024, 0.084, "range"),
    ("12-Sb", "R6 AUC loss 0.11-0.18", ["Sb"], "FS1block", "FS1", ["printed_R1_R6/R6/auc_loss"], 1, 2, 0.11, 0.18, "range"),
    ("12-Sp", "R6 surround loss Sp 0.073-0.114", ["Sp"], "FS1block", "FS1", ["printed_R1_R6/R6/auc_loss"], 1, 3, 0.073, 0.114, "range"),
    ("13-A", "two-person mix vs reconstruction A 0.526-0.659", ["A"], "FS1block", "GD", ["gd1/X_vs_REC/auc"], 1, 3, 0.526, 0.659, "range"),
    ("13-B", "B 0.459-0.558", ["B"], "FS1block", "GD", ["gd1/X_vs_REC/auc"], 1, 3, 0.459, 0.558, "range"),
    ("13-Sb", "Sb 0.529-0.595", ["Sb"], "FS1block", "GD", ["gd1/X_vs_REC/auc"], 1, 3, 0.529, 0.595, "range"),
    ("13-A, B, Sb", "reconstruction vs camera photo in the same frame 0.924-0.996", ["A", "B", "Sb"], "FS1block", "GD", ["gd1/REC_vs_G/auc"], 1, 3, 0.924, 0.996, "range"),
    ("14-A", "one-photo MIPGAN render flagged A 57-72%", ["A"], "FS1block", "GD", ["gd2/flags_own/R2"], 100, 0, 57, 72, "range"),
    ("14-B", "B 30-67%", ["B"], "FS1block", "GD", ["gd2/flags_own/R2"], 100, 0, 30, 67, "range"),
    ("14-Sb", "Sb 78-90%", ["Sb"], "FS1block", "GD", ["gd2/flags_own/R2"], 100, 0, 78, 90, "range"),
    ("17-A", "rho(logit, log sharpness) in LFW -0.28 to -0.54", ["A"], "FS1block", "TT1", ["r4/lfw/rho"], 1, 2, -0.54, -0.28, "range"),
    ("17-Sb (Z6)", "S4 vs S3 within lapvar strata 0.71-0.75", ["Sb"], "FS1block", "PR1", ["z6/strat_auc_S4_vs_S3"], 1, 2, 0.71, 0.75, "range"),
    ("18-Sb", "Sb 0.860 +- 0.030", ["Sb"], "FS1block", "FS1", ["record/lcomb_auc"], 1, 3, 0.860, 0.030, "mean_sd"),
    ("18-Sp", "landmark_combined AUC Sp 0.879 / 0.917 / 0.884", ["Sp"], "FS1block", "FS1", ["record/lcomb_auc"], 1, 3, 0.879, 0.917, "range"),
    ("18-Sp", "R1 floor-stratified Sp 0.863-0.891", ["Sp"], "FS1block", "FS1", ["printed_R1_R6/R1_strat_auc"], 1, 3, 0.863, 0.891, "range"),
    ("19-Sb (Z2a)", "Sb flags 32-43% of dev S3 at tau5", ["Sb"], "FS1block", "PR1", ["pools/spl_S3_dev/above_t5"], 100, 0, 32, 43, "range"),
    ("20-A, B, Sb", "AUC(R4 vs R2w) 1.0000 for both engines", ["A", "B", "Sb"], "FS1block", "PR1", ["z3/test/auc_cv", "z3/test/auc_fm"], 1, 4, 1.0, 1.0, "range"),
    ("20-A, B, Sb", "misses 0-0.5%", ["A", "B", "Sb"], "FS1block", "PR1", ["z3/test/miss_own_cv", "z3/test/miss_own_fm"], 100, 1, 0.0, 0.5, "range"),
    # second seed block (AB1, H100, 408-412)
    ("1-A (AB1)", "A's control: delta-f fm61 +0.265 to +0.385", ["A"], "AB1block", "AB1", ["c2p/fm61/d_flag"], 1, 3, 0.265, 0.385, "range"),
    ("1-A (AB1)", "amsl112 +0.055 to +0.152", ["A"], "AB1block", "AB1", ["c2p/amsl112/d_flag"], 1, 3, 0.055, 0.152, "range"),
    ("1-Sb (AB1)", "Sb at most +0.045 at the trained size", ["Sb"], "AB1block", "AB1", ["c2p/fm61/d_flag"], 1, 3, None, 0.045, "max"),
    ("1-Sb (AB1)", "at most +0.021 at 112.7 px", ["Sb"], "AB1block", "AB1", ["c2p/amsl112/d_flag"], 1, 3, None, 0.021, "max"),
    ("2-B (AB1)", "delta-m_att between -0.00 and +0.07 SD at both sizes", ["B"], "AB1block", "AB1", ["c2p/fm61/d_mean_att_sd", "c2p/amsl112/d_mean_att_sd"], 1, 2, 0.0, 0.07, "range"),
    ("2-Sb (AB1)", "falsified again for Sb (delta-m_att -0.06 to +0.04 SD)", ["Sb"], "AB1block", "AB1", ["c2p/fm61/d_mean_att_sd", "c2p/amsl112/d_mean_att_sd"], 1, 2, -0.06, 0.04, "range"),
    ("6-Sp (AB1)", "development warp-only placed 0.016-0.040", ["Sp"], "AB1block", "AB1", ["warp"], 1, 3, 0.016, 0.040, "range"),
    ("6-Sp (AB1)", "(Sb 0.000-0.022", ["Sb"], "AB1block", "AB1", ["warp"], 1, 3, 0.000, 0.022, "range"),
    ("6-Sp (AB1)", "A 0.000-0.005)", ["A"], "AB1block", "AB1", ["warp"], 1, 3, 0.000, 0.005, "range"),
    ("8-Sb (AB1)", "dev S3 placed Sb 0.36-0.41", ["Sb"], "AB1block", "AB1", ["S3"], 1, 2, 0.36, 0.41, "range"),
    ("8-Sp (AB1)", "Sp 0.70-0.74", ["Sp"], "AB1block", "AB1", ["S3"], 1, 2, 0.70, 0.74, "range"),
    ("9-Sp (AB1)", "Sp S0 placed 0.01-0.04", ["Sp"], "AB1block", "AB1", ["S0"], 1, 2, 0.01, 0.04, "range"),
    ("9-Sp (AB1)", "S0-vs-S4 AUC Sp 0.989-0.994", ["Sp"], "AB1block", "AB1", ["S0_vs_S4_auc"], 1, 3, 0.989, 0.994, "range"),
    ("9-Sp (AB1)", "Sb 0.989-0.992", ["Sb"], "AB1block", "AB1", ["S0_vs_S4_auc"], 1, 3, 0.989, 0.992, "range"),
    ("18-Sb (AB1)", "Sb 0.873-0.906", ["Sb"], "AB1block", "AB1", ["lcomb_auc"], 1, 3, 0.873, 0.906, "range"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stored", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    recs = [json.load(open(p)) for p in sorted(pathlib.Path(a.stored).glob("*/battery.json"))]
    res = []
    for cell, text, arms, bset, blk, paths, scale, dec, lo, hi, kind in C:
        vals, seeds = [], []
        for r in recs:
            if r["arm"] in arms and r["block_set"] == bset and "not_computed" not in r["blocks"].get(blk, {}):
                for p in paths:
                    v = get(r["blocks"][blk], p)
                    if v is not None:
                        vals.append(v * scale)
                seeds.append(f"{r['arm']}_s{r['seed']}")
        rd = lambda x: round(x + 0.0, dec)   # noqa: E731
        if not vals:
            got, ok = None, False
        elif kind == "range":
            got = [rd(min(vals)), rd(max(vals))]
            ok = got == [rd(lo), rd(hi)]
        elif kind == "max":
            got = [None, rd(max(vals))]
            ok = got[1] == rd(hi)
        else:
            got = [rd(statistics.mean(vals)), rd(statistics.stdev(vals))]
            ok = got == [rd(lo), rd(hi)]
        res.append(dict(cell=cell, table_text=text, arms=arms, block_set=bset, block=blk, paths=paths, kind=kind,
                        table=[lo, hi], battery=got, seeds=sorted(seeds), n_values=len(vals), match=bool(ok)))
        print(("MATCH " if ok else "DIFF  ") + f"{cell:16s} {text:62s} table {lo}..{hi}  battery {got}  ({len(seeds)} nets)")
    out = dict(source_table="experiments/SA1_shortcut-audit-table/result.md", n=len(res), matched=sum(r["match"] for r in res), cells=res)
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1))
    print("CELLS", out["matched"], "of", out["n"], "match")


if __name__ == "__main__":
    main()
