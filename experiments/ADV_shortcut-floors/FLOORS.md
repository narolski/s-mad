# ADV floors: one line per contrast (standing adversary)

Registration: `prereg.md` with amendments 1, 2 and 3 (amendment 3 is post hoc). Every number here is copied from the committed JSON in `floors/`
(`floors/<contrast>.json`; held-out scores `floors/<contrast>_heldout.csv`; frozen by `floors/pins_stage<k>.sha256`).
Development data only. No network score was read to make this page. Network values quoted here come from reviewed result files, with their seeds stated (correction of 13 Nov, 21:14 by the machine clock, on the lead's note: an earlier text called the seeds-408-412 value 0.873-0.906 the frozen candidate's).

How to read a line:
- **ADV floor** = the best of three cross-fitted shortcut-only models (single statistic, logistic regression, boosted
  trees) on all 72 features, persons kept apart; 95% person-cluster interval. **Non-F27/non-BLEND floor (contains
  face-box texture)** = the same on the BORDER, RES, STORE and RENDER families (registered in amendment 2 as the
  "nuisance floor"; renamed in amendment 3 because RES and RENDER are partly measured on the face box, which blending
  changes, so this floor is partly a blend detector). The **surround floor** (amendment 3) uses only the surround ring
  outside the face box; the **face-box floor** only the face box; the **file floor** only PNG size and container values.
- **Must exceed** = the arm's network must exceed the floor by the registered rule (`src/adversary/check.py`
  `exceeds()`: 2.5% bound of network AUC minus floor AUC, same person draws, above 0). Quick bar: the floor's upper
  bound; a network AUC below it cannot pass.
- The ADV floor is printed beside an arm's own registered floor; it never replaces it.
- **Ceiling** lines (both sides genuine) say how visible a nuisance is to shortcut features; no exceeds rule.

## Stage 1a (lcomb and the test ladder)

| Contrast | Arm read | Rows (pos / neg; components) | ADV floor [95%] (model) | Carried by | Non-F27/non-BLEND floor [95%] | Pixel-only floor | In-sample best single (27 stats; all) | Must exceed (quick bar) |
|---|---|---|---|---|---|---|---|---|
| `lcomb` | Second engine H-fm1; Sbx, GX1, RZ1 guards; E3 contrast 1; SA1 row 18 | 1000 / 2000; 3000 | 0.982 [0.978, 0.986] (logreg) | F27 (alone 0.952) | 0.964 [0.958, 0.970] (gbt) | 0.982 | 0.886 (noise_std_face); 0.889 (RENDER:resid_corr_gb, a face-box noise-residual cross-channel correlation) | > 0.986 (ADV), > 0.970 (non-F27/non-BLEND) |
| `test_fm_R4_vs_R2w` | Second engine H-fm2 | 191 / 191; 130 | 0.993 [0.987, 0.998] (gbt) | RENDER (alone 0.973) | 0.996 [0.992, 0.999] (gbt) | 0.993 | 0.880 (b3_.125-.25); 0.880 (F27:b3_.125-.25) | > 0.998 (ADV), > 0.999 (non-F27/non-BLEND) |
| `test_cv_R4_vs_R2w` | Second engine H-fm3 (guard) | 191 / 191; 130 | 0.990 [0.981, 0.997] (gbt) | RENDER (alone 0.975) | 0.986 [0.974, 0.994] (gbt) | 0.990 | 0.876 (b3_.125-.25); 0.876 (F27:b3_.125-.25) | > 0.997 (ADV), > 0.994 (non-F27/non-BLEND) |
| `test_fm_R4_vs_R3` | Second engine, printed engine table | 191 / 191; 130 | 0.796 [0.762, 0.832] (logreg) | F27 (alone 0.737) | 0.725 [0.683, 0.769] (logreg) | 0.799 | 0.653 (b2_.063-.125); 0.653 (F27:b2_.063-.125) | > 0.832 (ADV), > 0.769 (non-F27/non-BLEND) |
| `test_cv_R4_vs_R3` | Second engine, printed engine table | 191 / 191; 130 | 0.774 [0.737, 0.813] (logreg) | F27 (alone 0.775) | 0.692 [0.646, 0.736] (gbt) | 0.769 | 0.670 (b2_.063-.125); 0.670 (F27:b2_.063-.125) | > 0.813 (ADV), > 0.736 (non-F27/non-BLEND) |

Regression gate (amendment 2 F3): on `lcomb` the in-sample best of the 27 statistics is noise_std_face 0.8856, which
reproduces the reviewed 0.886 (gate passed; `floors/lcomb.json` `regression_gate`). Frozen by `floors/pins_stage0.sha256`.
These floors were computed before any read of SbFM, Sbx, RZ1 or E3 (none of their results has been opened).

What these lines say, plainly:
- **FFHQ landmark_combined (`lcomb`).** Shortcut-only statistics fitted on this set separate it at 0.98; about 0.79
  comes from the surround alone (a resampling-history difference documented by the dataset), the rest from
  face-region smoothness, which blending also produces. (Reviewer's wording, REVIEW_ADV_STAGE1A; the amendment-3
  surround floor with 18 surround measures is 0.942, see below.) The candidate recipe Sb's 0.873-0.906 (seeds 408-412, H100,
  AB1/result.md:82, not the frozen networks) and the frozen candidate's 0.814-0.885, mean 0.860 (seeds 403-407,
  PN1/result.md:294) lie below these floors, but they are fitted in-distribution while the networks are zero-shot on this set;
  the comparable learner is the same-data shortcut learner of prereg section 5.3. A second single statistic, a
  face-box noise-residual cross-channel correlation, reaches 0.889. **On `lcomb` the "exceeds" test is predetermined:
  the quick bar is 0.986, so "within the ADV floor" there carries no information and must not be read as evidence of
  shortcut use.** This adds the surround / face split to PN1's earlier 0.948 (27 statistics) and 0.786
  (noise_std_border); it is a quantification, not a new discovery.
- **Test-ladder R4 against warp-only R2w, both engines.** Shortcut cues reach 0.99 and the non-F27/non-BLEND cues 0.986-0.996:
  the two-person morph and its warp-only image differ in rendering and resolution statistics (blending softens), so a
  high network AUC here is not evidence of a second identity. This is a pure blending contrast (same pipeline, same
  photos); a floor near 0.99 shows the control works, not a construction confound.
- **Test-ladder R4 against same-person morph R3.** With blending on both sides the floor falls to 0.774-0.796
  (non-F27/non-BLEND 0.692-0.725; the reviewer finds it is likely the blend difference D: two-person blends are softer); this is the most informative of the five: a network above 0.81-0.83 on these rows shows something the
  listed cues do not.



## Stage 3: same-person splice and RI1 / TB1 rows: simple morph-cue floors (amendment 4 naming; not shortcut floors)

| Contrast | Arm read | Rows (pos / neg; components) | ADV floor [95%] (model) | Non-F27/non-BLEND floor [95%] | Within BD1 D quintiles (single / logreg / gbt; pure-D reference; coverage) | Must exceed (quick bar) |
|---|---|---|---|---|---|---|
| `dev_S4_vs_S3` | ME1/RI1/TB1 S4 vs S3 (development hosts); SA1 row 8 | 100 / 100; 100 | 0.820 [0.774, 0.866] (logreg) | 0.739 [0.682, 0.795] | 0.652 / 0.785 / 0.700; 0.566; 0.60 | > 0.866 |
| `test_S4_vs_S3` | S4 vs S3 (test hosts; BD1 primary rows); SA1 row 8 | 191 / 191; 130 | 0.754 [0.712, 0.799] (logreg) | 0.676 [0.626, 0.724] | 0.652 / 0.744 / 0.728; 0.585; 1.00 | > 0.799 |
| `ri_S4_vs_S3` | RI1 S1 and TB1 S, all 291 BD1 hosts | 291 / 291; 110 | 0.773 [0.742, 0.805] (logreg) | 0.719 [0.687, 0.752] | 0.655 / 0.757 / 0.730; 0.572; 1.00 | > 0.805 |
| `ri_R4_vs_R3` | RI1 S1 signal R4 vs R3 (291 hosts) | 291 / 291; 110 | 0.793 [0.765, 0.821] (logreg) | 0.705 [0.677, 0.734] | n/a | > 0.821 |
| `ri_R4_vs_R0` | RI1 S1 signal R4 vs R0 (291 hosts) | 291 / 291; 110 | 1.000 [1.000, 1.000] (gbt) | 1.000 [0.999, 1.000] | n/a | > 1.000 |

Frozen by `floors/pins_stage3.sha256`. Within-D: BD1's rule (quintile edges of log D over the pooled rows, strata with at least 10 of each class, weighted by n_pos x n_neg) applied to the floor's held-out scores.

## landmark_combined: region floors and history balancing (amendment 3, post hoc)

- Region floors on all of `lcomb` (3,000 rows): surround 0.942 (gbt), face box 0.965, file 0.652.
- **lcomb_bal** (1:1 matching on the boosted-tree surround score and pre_ied; `floors/lcomb_bal_rows.csv`): converged True with **125 morphs and 125 genuine photos (below 150 per class)**; final surround floor single / logreg / gbt 0.474 / 0.565 / 0.524; file 0.444 / 0.466 / 0.460; **face box 0.876 / 0.941 / 0.936**; all-cue ADV floor 0.949 [0.917, 0.973]. Build timing: the rule was fixed after two builds ran (prereg amendment 3, item 3).
- **lcomb_ipw** (stabilised inverse-probability weights on the logreg surround score and pre_ied, trimmed at the 1st / 99th percentile; `floors/lcomb_ipw_weights.csv`): effective sample size **8.0 morphs** and 413.8 genuine; weighted surround floor single / logreg / gbt 0.701 / 0.485 / 0.404; file 0.642 / 0.543 (logreg / gbt); face box 0.629 / 0.745. **Not usable** (registered bar: effective sample size at least 300 per class): the surround score separates the classes so well that a handful of morphs carry the weight.
- Reading (post hoc, H-new-1 of the review): where the surround is balanced (lcomb_bal), the face box still separates morphs from genuine photos at about 0.94, so landmark_combined carries a face-region difference besides the surround history; the subset is small (125 per class) and selected on a score, so this is descriptive.


## Stage 1c and stage 2 (training rows, GX1 analogues on GD2, RI1/TB1 controls, the audit rows of the frozen candidate)

Stage-2 rows for the frozen candidate are labelled post hoc (after the frozen candidate's read; features designed with Sb's landmark_combined value known). The `train_lad_*` floors are context only (E3's gate is in-sample; E2 uses other folds). Frozen by `floors/pins_stage2.sha256`.

| Contrast | Kind | Rows (pos / neg; components) | ADV floor [95%] (model) | Non-F27/non-BLEND floor | Carried by | In-sample best single (all) |
|---|---|---|---|---|---|---|
| `train_lad_S4_vs_S3` | simple morph-cue floor | 124 / 156; 63 | 0.768 [0.712, 0.819] (logreg) | 0.697 | F27 | 0.658 (F27:b2_.063-.125) |
| `train_lad_S4_vs_S0` | context only | 124 / 156; 63 | 0.963 [0.943, 0.981] (gbt) | 0.910 | F27 | 0.841 (F27:mf_ratio_.125-.25) |
| `gd2_R4_vs_R3` | simple morph-cue floor | 74 / 119; 57 | 0.715 [0.649, 0.785] (logreg) | 0.673 | F27 | 0.692 (F27:b1_.031-.063) |
| `gd2_R4_vs_R2` | floor | 74 / 238; 57 | 0.946 [0.916, 0.969] (logreg) | 0.883 | F27 | 0.890 (F27:b2_.063-.125) |
| `gd2_R4_vs_R2s1` | floor | 74 / 119; 57 | 0.942 [0.908, 0.970] (gbt) | 0.887 | F27 | 0.915 (F27:b2_.063-.125) |
| `ri_R0s61_vs_R0` | ceiling (should not separate) | 291 / 291; 291 | 0.999 [0.998, 1.000] (logreg) | 0.999 | F27 | 0.994 (F27:b6_diag>.5) |
| `ri_S0_vs_R0` | ceiling (should not separate) | 291 / 291; 291 | 0.999 [0.998, 1.000] (gbt) | 0.998 | F27 | 0.873 (STORE:png_zlib_level) |
| `ri_R2w4_vs_R0` | ceiling (should not separate) | 291 / 291; 110 | 0.999 [0.998, 1.000] (gbt) | 0.999 | RENDER | 0.873 (STORE:png_zlib_level) |
| `dev_cv_R4_vs_R2w` | floor; post hoc (Sb read) | 100 / 100; 100 | 0.986 [0.972, 0.995] (gbt) | 0.964 | RENDER | 0.917 (F27:b3_.125-.25) |
| `dev_cv_R4_vs_R2w4` | floor; post hoc (Sb read) | 100 / 100; 100 | 0.983 [0.968, 0.995] (gbt) | 0.972 | RENDER | 0.920 (F27:b3_.125-.25) |
| `dev_cv_R4_vs_R3` | simple morph-cue floor; post hoc (Sb read) | 100 / 100; 100 | 0.748 [0.695, 0.800] (logreg) | 0.662 | F27 | 0.719 (F27:b2_.063-.125) |
| `dev_cv_R4_vs_R3m` | simple morph-cue floor; post hoc (Sb read) | 100 / 100; 100 | 1.000 [1.000, 1.000] (gbt) | 0.685 | BLEND | 1.000 (BLEND:mirror_mad_face) |
| `dev_fm_R4_vs_R2w` | floor | 100 / 100; 100 | 0.989 [0.979, 0.997] (logreg) | 0.989 | RENDER | 0.921 (F27:b3_.125-.25) |
| `dev_fm_R4_vs_R3` | simple morph-cue floor | 100 / 100; 100 | 0.762 [0.705, 0.816] (gbt) | 0.726 | F27 | 0.696 (F27:b2_.063-.125) |
| `dev_S4_vs_S0` | floor; post hoc (Sb read) | 100 / 100; 100 | 0.947 [0.915, 0.973] (gbt) | 0.885 | F27 | 0.862 (F27:b3_.125-.25) |
| `dev_S4bg_vs_S0bg` | floor; post hoc (Sb read) | 100 / 100; 100 | 0.959 [0.927, 0.984] (gbt) | 0.947 | F27 | 0.932 (F27:b3_.125-.25) |
| `dev_R4face_vs_R2wface` | floor; post hoc (Sb read) | 100 / 100; 100 | 0.948 [0.918, 0.976] (logreg) | 0.915 | F27 | 0.802 (STORE:dct_comb_score) |
| `ms1_morph_vs_photo_native` | floor; post hoc (Sb read) | 150 / 300; 150 | 0.999 [0.998, 1.000] (logreg) | 0.999 | F27 | 0.996 (F27:b6_diag>.5) |
| `af0_dev_u50_vs_photo` | floor; post hoc (Sb read) | 180 / 378; 26 | 0.991 [0.973, 1.000] (gbt) | 0.980 | RENDER | 0.945 (RENDER:chroma_noise_cr) |
| `hn2_lcomplete_vs_bona` | floor; post hoc (Sb read) | 1000 / 2000; 3000 | 0.996 [0.995, 0.998] (logreg) | 0.978 | F27 | 0.958 (F27:noise_std) |
| `gd1_X_vs_REC` | floor; post hoc (Sb read) | 191 / 191; 130 | 0.945 [0.920, 0.967] (logreg) | 0.910 | F27 | 0.750 (RENDER:chroma_noise_cb) |
| `gd1_X_vs_SAME` | simple morph-cue floor; post hoc (Sb read) | 191 / 191; 130 | 0.833 [0.791, 0.870] (logreg) | 0.812 | F27 | 0.786 (RENDER:chroma_noise_cr) |

In-sample gbt AUC on `train_lad_S4_vs_S3` (context for E3's in-sample gate): 1.000.

In-sample gbt AUC on `train_lad_S4_vs_S0` (context for E3's in-sample gate): 1.000.

## Same-data shortcut learner (prereg section 5.3; the fair comparator for networks that never saw the evaluation rows)

Fitted on the unique training rows of the arm's own training list (labels from the list), all 72 features, applied to the development rows; no fit on any evaluation row. Frozen candidate's list (`train_Sb`, 5,535 images, 1,342 attacks) first; the other arms follow in `floors/transfer_<arm>.json`. Frozen by `floors/pins_stage7.sha256` (and later stage files).

| Contrast | logreg AUC | gbt AUC |
|---|---|---|
| `lcomb` | 0.787 | 0.665 |
| `lcomb_bal` | 0.811 | 0.644 |
| `test_fm_R4_vs_R2w` | 0.978 | 0.976 |
| `test_cv_R4_vs_R2w` | 0.975 | 0.996 |
| `test_fm_R4_vs_R3` | 0.662 | 0.704 |
| `test_cv_R4_vs_R3` | 0.719 | 0.704 |
| `ri_R4_vs_R3` | 0.725 | 0.716 |
| `ri_S4_vs_S3` | 0.678 | 0.650 |
| `dev_S4_vs_S3` | 0.675 | 0.670 |
| `test_S4_vs_S3` | 0.681 | 0.640 |
| `dev_S4_vs_S0` | 0.898 | 0.956 |
| `test_S4bg_vs_S0bg` | 0.820 | 0.908 |
| `dev_cv_R4_vs_R3m` | 0.606 | 0.769 |
| `store_morph_vs_photo_fm61` | 0.764 | 0.806 |
| `store_morph_vs_photo_amsl112` | 0.758 | 0.914 |
| `hn2_lcomplete_vs_bona` | 0.892 | 0.749 |
| `gd2_R4_vs_R2s1` | 0.755 | 0.900 |
| `gd2_R4_vs_R3` | 0.579 | 0.708 |
| `gd1_X_vs_REC` | 0.430 | 0.495 |
| `gd1_X_vs_SAME` | 0.664 | 0.691 |

Own-rule flag shares of the same learner (logreg decision > 0 / gbt probability > 0.5):

| Pool | n | logreg | gbt |
|---|---|---|---|
| dev_R0 | 100 | 0.000 | 0.010 |
| af0_dev_photo | 378 | 0.156 | 0.040 |
| ffhq_bona_orig | 2000 | 0.202 | 0.005 |
| R_cam_border_originals | 226 | 0.031 | 0.004 |
| R_cam_border | 1582 | 0.344 | 0.000 |
| R_ffhq_border | 2000 | 0.327 | 0.001 |
| ms1_photo_native | 300 | 0.127 | 0.000 |
| ms1_photo_fm61 | 291 | 0.581 | 0.045 |
| ms1_photo_amsl112 | 290 | 0.507 | 0.021 |
| dev_S0 | 100 | 0.160 | 0.030 |
| dev_S3 | 100 | 0.480 | 0.440 |
| dev_S4 | 100 | 0.770 | 0.710 |
| dev_R3_cv | 100 | 0.720 | 0.860 |
| dev_R3_fm | 100 | 0.560 | 0.480 |
| dev_R2w_fm | 100 | 0.040 | 0.020 |
| dev_R4_cv | 100 | 0.960 | 0.970 |
| dev_R4_fm | 100 | 0.860 | 0.750 |
| lcomb_morph | 1000 | 0.851 | 0.097 |
| lcomb_genuine | 2000 | 0.459 | 0.048 |
| gd2_R2 | 238 | 0.588 | 0.210 |
| gd2_R4 | 74 | 0.932 | 0.865 |

Plainly (development data; no network score read here): trained on the frozen candidate's own training rows, a shortcut-only learner reaches 0.787 (logreg) / 0.665 (gbt) on landmark_combined, against the frozen candidate's 0.814-0.885, mean 0.860 (Sb seeds 403-407, PN1/result.md:294; the recipe at seeds 408-412 reaches 0.873-0.906, AB1/result.md:82); by the review's H-new-2 bars (supported ≥ 0.85, falsified ≤ 0.75) this is between the bars. On the pipeline-matched R4 vs R3 rows it reaches 0.72-0.74 (frozen candidate, seeds 403-407: 0.80-0.85, PR1/result.md:117); on test S4 vs S3 0.681 / 0.640 (frozen candidate, seeds 403-407: 0.716-0.744, PR1/result.md:21). It flags 44-48% of development same-person splices and 72-86% of OpenCV same-person morphs, close to the frozen candidate's 31-48% and 83-88% (seeds 403-407, PR1/result.md:19, :117). Seed table: RECORDS ledger entry 6 (ca47f00).

### Same-data shortcut learner for every arm's training list (logreg / gbt)

| Arm list | n train | lcomb | lcomb_bal | test OpenCV R4 vs R3 | test FM R4 vs R3 | test S4 vs S3 | dev S3 flag | dev R3 (OpenCV) flag | bordered camera flag | FFHQ hold-out photo flag native → fm61 → amsl112 (logreg) |
|---|---|---|---|---|---|---|---|---|---|---|
| Sb | 5535 | 0.787 / 0.665 | 0.811 / 0.644 | 0.719 / 0.704 | 0.662 / 0.704 | 0.681 / 0.640 | 0.48 / 0.44 | 0.72 / 0.86 | 0.34 / 0.00 | 0.13 → 0.58 → 0.51 |
| A | 1526 | 0.798 / 0.434 | 0.697 / 0.388 | 0.619 / 0.618 | 0.601 / 0.503 | 0.610 / 0.552 | 0.93 / 0.85 | 0.99 / 0.98 | 0.08 / 0.01 | 0.13 → 0.02 → 0.43 |
| B | 5099 | 0.822 / 0.619 | 0.825 / 0.567 | 0.686 / 0.656 | 0.579 / 0.610 | 0.605 / 0.494 | 0.37 / 0.32 | 0.79 / 0.90 | 0.34 / 0.00 | 0.03 → 0.41 → 0.33 |
| SbZ | 4649 | 0.803 / 0.665 | 0.826 / 0.625 | 0.720 / 0.705 | 0.660 / 0.707 | 0.682 / 0.653 | 0.47 / 0.42 | 0.72 / 0.86 | 0.31 / 0.00 | 0.11 → 0.52 → 0.49 |
| SbS | 4552 | 0.776 / 0.583 | 0.759 / 0.558 | 0.712 / 0.699 | 0.665 / 0.714 | 0.684 / 0.660 | 0.49 / 0.40 | 0.77 / 0.86 | 0.05 / 0.01 | 0.06 → 0.20 → 0.14 |
| Sp | 5223 | 0.777 / 0.620 | 0.783 / 0.572 | 0.705 / 0.696 | 0.684 / 0.693 | 0.671 / 0.601 | 0.66 / 0.71 | 0.75 / 0.89 | 0.47 / 0.00 | 0.18 → 0.52 → 0.44 |
| AS | 2146 | 0.808 / 0.609 | 0.766 / 0.577 | 0.623 / 0.618 | 0.587 / 0.541 | 0.584 / 0.539 | 0.93 / 0.88 | 0.99 / 0.98 | 0.37 / 0.00 | 0.14 → 0.33 → 0.77 |
| SbH | 3831 | 0.815 / 0.633 | 0.838 / 0.606 | 0.720 / 0.718 | 0.658 / 0.705 | 0.680 / 0.651 | 0.49 / 0.38 | 0.75 / 0.86 | 0.21 / 0.00 | 0.11 → 0.37 → 0.51 |
| SbR | 3831 | 0.772 / 0.652 | 0.789 / 0.609 | 0.721 / 0.707 | 0.668 / 0.704 | 0.674 / 0.620 | 0.50 / 0.45 | 0.71 / 0.85 | 0.45 / 0.00 | 0.12 → 0.58 → 0.51 |
| SbnS0 | 5379 | 0.789 / 0.654 | 0.802 / 0.617 | 0.719 / 0.711 | 0.668 / 0.703 | 0.688 / 0.644 | 0.50 / 0.46 | 0.70 / 0.85 | 0.34 / 0.00 | 0.17 → 0.57 → 0.49 |
| SbH61 | 5172 | 0.708 / 0.670 | 0.735 / 0.640 | 0.713 / 0.710 | 0.661 / 0.708 | 0.677 / 0.651 | 0.47 / 0.44 | 0.73 / 0.86 | 0.57 / 0.00 | 0.23 → 0.83 → 0.69 |
| SbnS3 | 5379 | 0.782 / 0.621 | 0.805 / 0.616 | 0.702 / 0.705 | 0.670 / 0.695 | 0.666 / 0.587 | 0.56 / 0.70 | 0.76 / 0.93 | 0.40 / 0.00 | 0.10 → 0.53 → 0.47 |
| SbSp | 4240 | 0.749 / 0.536 | 0.706 / 0.493 | 0.698 / 0.692 | 0.688 / 0.693 | 0.670 / 0.597 | 0.64 / 0.70 | 0.73 / 0.90 | 0.05 / 0.01 | 0.18 → 0.16 → 0.12 |
| SbFM | 5939 | 0.777 / 0.648 | 0.800 / 0.627 | 0.716 / 0.720 | 0.697 / 0.736 | 0.679 / 0.664 | 0.54 / 0.46 | 0.70 / 0.86 | 0.42 / 0.00 | 0.16 → 0.59 → 0.53 |
| Sbx | 6920 | 0.800 / 0.691 | 0.841 / 0.682 | 0.699 / 0.728 | 0.673 / 0.723 | 0.693 / 0.655 | 0.49 / 0.44 | 0.70 / 0.84 | 0.10 / 0.02 | 0.10 → 0.10 → 0.13 |

Frozen by `floors/pins_stage7.sha256` (Sb) and `floors/pins_stage8.sha256` (the other lists). Printed only (no verdict attaches; prereg section 5.3). An arm's network that does not exceed its own list's same-data learner on a contrast has not shown anything that shortcut-only learning on the same training rows does not also produce.

### AB1 batch C lists (amendment 6; frozen by `floors/pins_stage11.sha256`)

- **SpV** (list sha256 f6521d96de7d93ff…, 5223 unique images): lcomb 0.777 / 0.620; lcomb_bal 0.783 / 0.572; sel360 0.725 / 0.725; splice80 S4 vs S3 0.668 / 0.622; splice80 own-rule flags S4 / S3 / S0 logreg 0.93 / 0.75 / 0.35, gbt 0.94 / 0.72 / 0.15 (logreg / gbt throughout).
- **BN** (list sha256 c1b4497bb59343b7…, 5411 unique images): lcomb 0.822 / 0.639; lcomb_bal 0.836 / 0.592; sel360 0.719 / 0.686; splice80 S4 vs S3 0.597 / 0.457; splice80 own-rule flags S4 / S3 / S0 logreg 0.47 / 0.29 / 0.09, gbt 0.06 / 0.17 / 0.00 (logreg / gbt throughout).
- **BV** (amendment 6 addendum; list sha256 ee4e227b…; frozen by `floors/pins_stage12.sha256`): lcomb 0.822 / 0.619; sel360 0.716 / 0.667; splice80 S4 vs S3 0.620 / 0.481; flags S4 / S3 / S0 logreg 0.72 / 0.55 / 0.21, gbt 0.28 / 0.34 / 0.07. **Identical to B's learner** (max difference 0.0 on every contrast): train_BV holds exactly B's 5,099 unique images, and the learner fits each image once, so it cannot see the 312 added repetitions. For BV the comparator is therefore B's learner; the repetition effect is not measurable by this learner.
- Per-row scores: `floors/transfer_SpV_rows.csv`, `floors/transfer_BN_rows.csv` (set, id, rung, label, component, logreg, gbt). If the AB1 owner re-pins either list, these are recomputed and these files are labelled superseded.

## Descriptive reads of amendment 4 (registered at 1067700 before computing)

- **H-new-1** (F27 + BLEND alone on lcomb_bal, 250 rows): single / logreg / gbt 0.888 / 0.929 / 0.914: **supported** (bar ≥ 0.90). Where the surround history is balanced to within detection power, the remaining separation is carried by blend-texture statistics.
- **H-new-3** (chroma-only vs luma-only face statistics, R4 vs R3 within BD1 D quintiles): all 291 hosts chroma 0.540, luma 0.723; test hosts chroma 0.542, luma 0.723: **falsified**. At equal D the two-person excess sits in luma texture statistics (noise, Laplacian, gradient, band powers), not in colour mismatch.

## Amendment 5 products (selection rule; frozen by `floors/pins_stage9.sha256`)

- **lcomb_smatch** (1:1 greedy on logit(surround_gbt), caliper 0.1 SD, default_rng(20261117); `floors/lcomb_smatch_rows.csv`): 360 pairs. Refit balance on the matched rows (single / logreg / gbt): surround 0.542 / 0.662 / 0.463; file 0.557 / 0.549 / 0.515; face box 0.854 / 0.916 / 0.927; all-cue 0.838 / 0.952 / 0.945. **Known limit: surround-balanced only** — and only for the boosted-tree surround score it was matched on: the linear surround refit still reaches 0.662. (The selection rule draft v3 quotes 0.504 for its surround balance; that is the boosted-tree side, while the linear surround refit reaches 0.662.)
- **sel360** (OpenCV R4 and R3 of the 100 development hosts and the 80 test hosts clean of development; `floors/sel360_rows.csv`; 360 rows, 110 components): within-D simple morph-cue floor (held-out scores of `ri_R4_vs_R3`, edges over these rows) single 0.690 [0.640, 0.736], logreg 0.794 [0.748, 0.836], gbt 0.774 [0.726, 0.821]; pure-D reference 0.560; coverage 1.00.
- **Per-row same-data learner scores** `floors/transfer_Sb_rows.csv`, `floors/transfer_SbFM_rows.csv` (set, id, label, component, logreg, gbt) on lcomb, sel360 and lcomb_smatch. AUC logreg / gbt: train_Sb lcomb 0.787 / 0.665, sel360 0.739 / 0.750, lcomb_smatch 0.762 / 0.606; train_SbFM 0.777 / 0.648, 0.734 / 0.756, 0.752 / 0.590.

## GD0 (FFHQ-Morphs StyleGAN and DiffAE families; GX1 transfer reads, SA1 row 13 context; frozen by `floors/pins_stage10.sha256`; post hoc for Sb)

| Contrast | Rows (pos / neg) | ADV floor [95%] (model) | Non-F27/non-BLEND floor | In-sample best single (all) |
|---|---|---|---|---|
| `gd0_sgw_vs_resmatch` | 1000 / 2000 | 0.990 [0.988, 0.992] (gbt) | 0.973 | 0.910 (F27:b3_.125-.25) |
| `gd0_sgwp_vs_resmatch` | 1000 / 2000 | 0.980 [0.976, 0.983] (gbt) | 0.955 | 0.876 (F27:b3_.125-.25) |
| `gd0_diffae_vs_resmatch` | 1000 / 2000 | 0.966 [0.960, 0.971] (logreg) | 0.927 | 0.823 (RENDER:resid_corr_rg) |

## XF1: matched FaceMorpher render on FFHQ hold-out hosts (amendment 7; frozen by `floors/pins_stage13.sha256`; computed before any XF1 network score exists in this folder)

| Contrast | Binding unit | ADV floor [binding 95%; alternative-unit 95%] | Non-F27/non-BLEND | Surround only (single / logreg / gbt) | Face box (s / l / g) | File (s / l / g) | Pixel-only |
|---|---|---|---|---|---|---|---|
| `xf1_FMHB_vs_FMHH` | 12 pairing components (= cell) (alternative: host (299)) | 0.989 [0.986, 0.994; 0.983, 0.994] (gbt) | 0.969 | 0.775 / 0.839 / 0.849 | 0.888 / 0.952 / 0.964 | 0.696 / 0.675 / 0.621 | 0.989 |
| `xf1_FMHH_vs_H` | host (299) (alternative: cell (12)) | 0.587 [0.560, 0.615; 0.529, 0.612] (logreg) | 0.589 | 0.500 / 0.500 / 0.500 | 0.561 / 0.575 / 0.580 | 0.568 / 0.559 / 0.504 | 0.576 |

Same-data learner (logreg / gbt AUC; own-rule flag share of the positive / negative side, logreg):

- train_Sb: FM(H,B) vs FM(H,H) 0.897 / 0.945 (flags 0.78 / 0.14); FM(H,H) vs H 0.521 / 0.515 (flags 0.14 / 0.13).
- train_A: FM(H,B) vs FM(H,H) 0.901 / 0.775 (flags 0.77 / 0.13); FM(H,H) vs H 0.502 / 0.516 (flags 0.13 / 0.13).
- train_B: FM(H,B) vs FM(H,H) 0.898 / 0.893 (flags 0.27 / 0.03); FM(H,H) vs H 0.522 / 0.499 (flags 0.03 / 0.03).

Plainly: **the one-photo FaceMorpher render is pixel-identical to the plain photo in the surround ring** (all 18 surround measures equal row for row; surround floor exactly 0.500 for all three models), and the whole shortcut set separates the render from the photo only at 0.587 [0.560, 0.615] (face box 0.58, file 0.57). So a network's "render reaction" on FM(H,H) vs H cannot be a border, canvas or format read; whatever it reacts to is inside the face. The two-person morph against the render is separated at 0.989 by shortcut-only cues (face box 0.964, surround 0.849): FaceMorpher two-person morphs carry a strong blend signature, including outside the face box; the first contrast has only 12 person components, so its folds and intervals are coarse.

## Attack sets (requests to the DATA role through the lead; nothing built by the adversary)

Only allowed operations: the approved warp `h1_build.py`, the unchanged OpenCV and FaceMorpher morphers, constant-colour
region blanking, existing E7 outputs, lossless PNG. Items marked "author" need an operation that is the author's to
allow.

**Second-engine arm (SbFM).**
1. FaceMorpher same-person morphs and FaceMorpher warp-only images of new development hosts, at the same counts as the
   FaceMorpher R4 rows (morpher unchanged). Breaks the claim if SbFM's FaceMorpher gain is an engine-signature prior:
   it would flag these as often as R4.
2. Two-person FaceMorpher and OpenCV morphs of look-alike pairs (LA1 pairs, contributor cosine in the top decile) beside
   random-pair morphs of the same hosts. If detection rests on blend energy rather than two identities, look-alike
   morphs (low blend difference) are missed.
3. Self-morphs and warp-only images of FFHQ hold-out photos made with the unchanged OpenCV morpher at landmark_combined's
   frame (FFHQ, 1024 source): if SbFM's landmark_combined gain is a processing-history cue, it flags these too.

**Border-crossed arm (Sbx).**
1. The same camera photos and FFHQ photos with constant-colour borders of a non-black colour (mid-grey 128, white 255)
   and the same TT1 mask geometry. If Sbx learned "exactly-black region = ignore", the reaction returns at grey/white.
2. Border-blanked morphs: development R4, S4 and landmark_combined morphs with the same masks (Sbx trained bordered
   attacks at 25%). Tests whether detection survives the border and whether the border shifts misses (surround cue).
3. Masks from the largest-fraction TT1 frames (masked fraction above 0.55) that reach the face hull: partial-face
   blanking on camera photos and morphs; separates a border cue from a face-content read.

**GAN arms (GX, GXp).**
1. Look-alike two-person MIPGAN morphs (unchanged generator, LA1 pairs at contributor cosine above 0.30) against R3 of
   the same hosts: if GX's R4-vs-R3 separation rests on contributor dissimilarity, it collapses here.
2. A stratification product (no new image): GX1 held-out R4 and R3 rows binned by the latent distance from the mean
   code (PD1's "closeness to the mean latent" signal) and by contributor cosine, so the read can be taken at matched
   latent spread.
3. R3 made from two photos of one person with the largest available session gap (FERET fa/fb across years) against R4
   with small appearance difference: a same-person pair with large appearance change should not be flagged.

**Resolution and resize study (RZ1).**
1. Storage copies at sizes inside the mixR band (eye distance about 80-95 px), genuine and morph: existing E7 outputs if
   any exist at those sizes; otherwise **author** (new storage size). Tests whether the mixed-kernel arms learned
   invariance only to the trained band; morphs stored in-band could evade.
2. JPEG-history development genuine photos and morphs (**author**: JPEG re-encoding of development images, decision 5
   of the evening conclusions).
3. For the crop arms: "inverse splices" (two-person blend outside the face hull, warp-only inside), built with the
   existing PN1 splice code and swapped masks, if the lead rules that it is within the approved splice operation.
   A crop arm that "detects" these reads the hull edge or jaw, not the face.

**DINOv3 programme (E3, E2).** No new build needed first: the existing face-only same-person splices (S3_bg) against
S4_bg (identity on the face-only read), the border-blanked camera photos, and the GD2 one-photo renders. If those
show the CLIP pattern, request the SbFM and Sbx attack sets above for DINOv3.

**Frozen candidate (Sb).** 1. Look-alike two-person morphs against same-person morphs matched on BD1's D. 2. Grey and
white constant borders (as Sbx 1). 3. Border-blanked morphs (as Sbx 2).
