"""Shared test battery (BATTERY): the 20 rows of the shortcut audit table (SA1, experiments/SA1_shortcut-audit-table/result.md)
and the battery statistics that fill each row for one network. Statistics only: no verdict, rule or threshold is attached.
Row names follow SA1 (owner of the row definitions). Each statistic is (label, block, path in the block's output)."""

ROWS = {
    1: dict(name="Storage history of genuine photos (shrink and re-store)", stats=[
        ("FFHQ share rising, history-matched vs native (FS1)", "FS1", "record/share_rising"),
        ("FFHQ genuine own-rule flags, native (FS1)", "FS1", "record/flags_own/ffhq_bona_orig"),
        ("dev camera photos own-rule flags, native / 61 px / 112 px (FS1)", "FS1", ["record/flags_own/D_R0", "record/flags_own/D_R0_61", "record/flags_own/D_R0_112"]),
        ("C2P hold-out: native flag", "C2P", "native_flag"),
        ("C2P hold-out: delta own-rule flags at 61.2 px (upper 95%)", "C2P", ["fm61/d_flag", "fm61/d_flag_upper95"]),
        ("C2P hold-out: delta own-rule flags at 112.7 px (upper 95%)", "C2P", ["amsl112/d_flag", "amsl112/d_flag_upper95"]),
        ("C2P hold-out: mean shift in genuine SD, 61.2 / 112.7 px", "C2P", ["fm61/d_mean_sd", "amsl112/d_mean_sd"]),
        ("AB1 development storage rise (soft minus camera)", "AB1", "dsoft"),
    ]),
    2: dict(name="Storage history of morphs (stored-small morph missed)", stats=[
        ("C2P hold-out: morph mean shift in genuine SD, 61.2 / 112.7 px", "C2P", ["fm61/d_mean_att_sd", "amsl112/d_mean_att_sd"]),
        ("C2P hold-out: stored-morph miss, 61.2 / 112.7 px", "C2P", ["fm61/miss_stored", "amsl112/miss_stored"]),
        ("C2P hold-out: native-morph miss", "C2P", "miss_native"),
    ]),
    3: dict(name="JPEG history", stats=[], missing="no development JPEG pool exists (author item: the author builds the JPEG pack; "
                                                  "agents only score it). Battery v1 has no set for this row."),
    4: dict(name="Unseen camera source (source comparison, not paired)", stats=[
        ("TT1 mean family own-rule flag F-bar", "TT1", "r5/Fbar"),
        ("TT1 largest family flag F-max", "TT1", "r5/Fmax"),
        ("TT1 family flags (replay, msu, oulu, casia_fasd, lfw_calfw, cfp_ff, agedb)", "TT1",
         ["fam_flag/replay_attack", "fam_flag/msu_mfsd", "fam_flag/oulu_npu", "fam_flag/casia_fasd", "fam_flag/lfw_calfw", "fam_flag/cfp_ff", "fam_flag/agedb_30"]),
        ("TT1 training-source camera photos R_cam flag", "TT1", "pools/R_cam/flag"),
        ("FFHQ genuine own-rule flags (FS1)", "FS1", "record/flags_own/ffhq_bona_orig"),
        ("MEDS own-rule flag (primary pool) and 240x240 group", "MEDS", ["flag", "flag_240px"]),
        ("MEDS AUC vs R_cam", "MEDS", "auc_vs_R_cam"),
    ]),
    5: dict(name="Image border / frame (black border alone)", stats=[
        ("TT1 camera photos with a blanked-in border, own-rule flag per family", "TT1",
         ["printed/border_flag/replay_attack", "printed/border_flag/msu_mfsd", "printed/border_flag/oulu_npu", "printed/border_flag/casia_fasd",
          "printed/border_flag/lfw_calfw", "printed/border_flag/cfp_ff", "printed/border_flag/agedb_30"]),
        ("TT1 AUC border vs no border: FFHQ (d) and camera CFP-FF (e)", "TT1", ["auc/d_ffhq_border/auc", "auc/e_cam_border/cfp_ff/auc"]),
    ]),
    6: dict(name="Warp only, no second person (R2w)", stats=[
        ("test ladder R2w own-rule flag (OpenCV)", "PR1", "pools/lad_R2w_opencv_test_nat/above_own"),
        ("test ladder AUC R4 vs R2w (OpenCV)", "PR1", "auc/R4_vs_R2w_opencv_test"),
        ("AB1 development warp-only placed", "AB1", "warp"),
    ]),
    7: dict(name="Same-person morph (R3)", stats=[
        ("test ladder R3 / R3m own-rule flag (OpenCV)", "PR1", ["pools/lad_R3_opencv_test_nat/above_own", "pools/lad_R3m_opencv_test_nat/above_own"]),
        ("test ladder AUC R4 vs R3 / R4 vs R3m (OpenCV)", "PR1", ["auc/R4_vs_R3_opencv_test", "auc/R4_vs_R3m_opencv_test"]),
    ]),
    8: dict(name="Same-person face splice (S3)", stats=[
        ("test / dev S3 own-rule flag", "PR1", ["pools/spl_S3_test/above_own", "pools/spl_S3_dev/above_own"]),
        ("test AUC S4 vs S3", "PR1", "auc/S4_vs_S3_test"),
        ("AB1 development S3 placed", "AB1", "S3"),
        ("BD1 S4 vs S3 within blend-difference quintiles; pure-D reference; excess", "BD1", ["primary", "reference", "primary_minus_ref"]),
    ]),
    9: dict(name="Blending seam (S0 seam-only negative)", stats=[
        ("test / dev S0 own-rule flag", "PR1", ["pools/spl_S0_test/above_own", "pools/spl_S0_dev/above_own"]),
        ("test AUC S4 vs S0", "PR1", "auc/S4_vs_S0_test"),
        ("AB1 development S0 placed; S0-vs-S4 AUC", "AB1", ["S0", "S0_vs_S4_auc"]),
    ]),
    10: dict(name="Alignment or crop path", stats=[
        ("TT1 camera photos through the 224 px / 112 px geometry, own-rule flag", "TT1", ["printed/geo_flag/g224", "printed/geo_flag/g112"]),
        ("TT1 AUC geometry reference vs R_cam, 224 / 112", "TT1", ["auc/f_geo/g224/auc", "auc/f_geo/g112/auc"]),
    ]),
    11: dict(name="Data volume", stats=[], missing="between-arm control (Bn, Bv, SbV), not a per-network statistic; read from the arms' own registrations."),
    12: dict(name="Surround blend (whole-frame tools)", stats=[
        ("R6 AUC loss complete -> combined; share complete higher; mean logit drop", "FS1",
         ["printed_R1_R6/R6/auc_loss", "printed_R1_R6/R6/share_complete_higher", "printed_R1_R6/R6/mean_logit_drop"]),
        ("face-blanked R4 vs R2w, test / dev", "FS1", ["record/faceblanked_test", "record/faceblanked_dev"]),
    ]),
    13: dict(name="Diffusion render path (one-photo reconstruction)", stats=[
        ("GD1 AUC two-person mix vs reconstruction; reconstruction vs camera photo in frame", "GD", ["gd1/X_vs_REC/auc", "gd1/REC_vs_G/auc"]),
        ("GD1 AUC same-person mix vs reconstruction; two-person vs same-person", "GD", ["gd1/SAME_vs_REC/auc", "gd1/X_vs_SAME/auc"]),
        ("GD1 own-rule flags in the DiffAE frame: camera G, reconstruction REC", "GD", ["gd1/flags_own_frame_confounded/G", "gd1/flags_own_frame_confounded/REC"]),
    ]),
    14: dict(name="GAN one-person render (MIPGAN)", stats=[
        ("GD2 one-photo MIPGAN render R2 own-rule flag", "GD", "gd2/flags_own/R2"),
        ("GD2 AUC R4 vs R2; R3 vs R0; R4 vs R3", "GD", ["gd2/R4_vs_R2/auc", "gd2/R3_vs_R0/auc", "gd2/R4_vs_R3/auc"]),
        ("GD0 StyleGAN wplus / w AUC", "GD", ["gd0/stylegan_wplus/auc", "gd0/stylegan_w/auc"]),
    ]),
    15: dict(name="Training-partner trace", stats=[], missing="manifest audit (SA1 G9, src/SA1/g9_partners.py), not a score of the network; "
                                                              "SA1 runs it on the new arm's training manifest."),
    16: dict(name="Expression / capture detail (smiling half)", stats=[], missing="no development expression pool is aligned and packed "
             "(G11 found CFD 158 + KDEF 70 persons with neutral and happy images; alignment with the unchanged aligner, registration and the lead's approval needed)."),
    17: dict(name="Softness / detail loss", stats=[
        ("TT1 rho(logit, log sharpness) in LFW / CALFW / CFP-FF / AgeDB", "TT1", ["r4/lfw/rho", "r4/calfw/rho", "r4/cfp_ff/rho", "r4/agedb_30/rho"]),
        ("PR1 Z6: S4 vs S3 within lapvar strata; R4 vs R2w within lapvar strata (cover)", "PR1",
         ["z6/strat_auc_S4_vs_S3", "z6/strat_auc_R4_vs_R2w", "z6/cover"]),
    ]),
    18: dict(name="Processing cue in the surround of the development set (FFHQ landmark_combined)", stats=[
        ("landmark_combined AUC; lower bound of AUC minus best single statistic", "FS1", ["record/lcomb_auc", "record/lcomb_minus_floor_lo"]),
        ("best single statistic AUC (floor, same for every network)", "FS1", "context/floor_best_auc"),
        ("R1 floor-stratified AUC; R3 increment over 27 statistics", "FS1", ["printed_R1_R6/R1_strat_auc", "printed_R1_R6/R3/inc_over_27"]),
        ("R2 rho with noise_std_border, genuine", "FS1", "printed_R1_R6/R2/noise_std_border_genuine"),
    ]),
    19: dict(name="Operating point / bounded output scale", stats=[
        ("tau5 (smallest cut-off with <= 5% flags in each calibration source)", "PR1", "tau5"),
        ("G_max at tau5; landmark_combined miss at tau5", "PR1", ["z2a/G_max", "z2a/lcomb_miss_t5"]),
        ("FFHQ genuine flag x_own; mean miss of three attack pools y_own", "PR1", ["z2rho/x_own", "z2rho/y_own"]),
        ("dev S3 flag at tau5", "PR1", "pools/spl_S3_dev/above_t5"),
        ("TT1 median shift of FFHQ morphs from camera photos u", "TT1", "u"),
    ]),
    20: dict(name="Morph engine of the training morphs (OpenCV-style trained, FaceMorpher held out)", stats=[
        ("test ladder R4 vs R2w AUC, OpenCV / FaceMorpher; difference", "PR1", ["z3/test/auc_cv", "z3/test/auc_fm", "z3/test/delta"]),
        ("test ladder R4 own-rule miss, OpenCV / FaceMorpher", "PR1", ["z3/test/miss_own_cv", "z3/test/miss_own_fm"]),
        ("test ladder R4 vs R3 AUC, OpenCV / FaceMorpher", "PR1", ["auc/R4_vs_R3_opencv_test", "auc/R4_vs_R3_facemorpher_test"]),
    ]),
}


def get(d, path):
    for k in path.split("/"):
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def extract(blocks):
    """{row: {name, stats: [{label, block, values: [..]}], missing?}} for one network."""
    out = {}
    for r, spec in ROWS.items():
        rec = dict(name=spec["name"], stats=[])
        if spec.get("missing"):
            rec["missing"] = spec["missing"]
        for label, blk, paths in spec["stats"]:
            b = blocks.get(blk) or {}
            ps = paths if isinstance(paths, list) else [paths]
            if "not_computed" in b:
                rec["stats"].append(dict(label=label, block=blk, paths=ps, values=None, not_computed=b["not_computed"]))
                continue
            rec["stats"].append(dict(label=label, block=blk, paths=ps, values=[get(b, p) for p in ps]))
        out[str(r)] = rec
    return out
