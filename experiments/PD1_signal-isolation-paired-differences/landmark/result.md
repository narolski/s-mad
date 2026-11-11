# Signal isolation by paired differences (PD1), landmark family: result

Owner's page. Facts only; the lead draws conclusions. Pre-registration: `prereg.md` beside this file (written
11 Nov 17:05 CET, before any number; amendment 1 at 18:25 and amendment 2 at 18:40, both before their numbers).
Status: complete (11 Nov, 20:00 CET). Not reviewed.

Terms (as in `prereg.md`): host photo **x0** (landmark ladder rung R0); warp-only image **x1** (R2w: the host warped
by the tool's own routine to the mean shape of host and same-person photo, texture from the host only); mirror
warp-only image **x1m** (R2wm); mirror self-morph **xm** (R3m); same-person morph **x2** (R3); two-person morph
**x3** (R4). "One-person head" = linear head trained with a within-host paired loss on (x2, x1) and (xm, x1) only;
"two-person head" = the same on (x3, x1). AUC = area under the ROC curve, later rung positive, 0.5 is chance.
Intervals = 95% pigeonhole person bootstrap (2,000 draws) unless stated. Floor = best single simple statistic
(folded AUC among 27) on the same images. E7 = the existing shrink-and-enlarge history control.

## Inventory (11 Nov, 17:00 CET)

| Item | Where | Count | State |
|---|---|---|---|
| Landmark ladder (AR1) rungs, primary pool | `/mnt/t7/smad_next/AR1/img/frgcferet/{opencv,facemorpher}/{R2w,R2wm,R3m,R3,R4}`, R0 = `AR1/src` frames | 536 hosts x 2 engines x 5 rungs + 536 photos | all built by the AR1 owner (warp-only and mirror rungs included), nothing built here |
| Graded mixing set (landmark dose curve, AR2) | `AR1/img/frgcferet/fm_graded/m000..m050` | 300 hosts x 6 levels | built (FaceMorpher library) |
| FRLL ladder pool | `AR1/img/frll/...` | 102 persons | built; diagnostic only (smiling photo in every rung beyond x0) |
| Alpha-field probe images (AF0) | `/mnt/t7/smad_next/AF0/img` | photos 715, zero field 1,000, uniform 0.25 1,000, uniform 0.5 1,000 | built; the warped halves of the 1,000 uniform-0.5 morphs appeared at 18:02 (used under amendment 1) |
| Shrink-and-enlarge copies of 200 hosts (AF0 wave 4) | `AF0/img/soft/{amsl112,fm61}` | x0 and x1 (both engines) of 200 hosts at 2 strengths, 1,200 images | appeared at 17:57 (used under amendment 1) |
| SMDD renders and stored-small copies | `smadcvpr_data/train/smdd/os25k_bf_t` (256 px), `a47/data47/i3/train/smdd_a47e7` (80 px) | 25,000 pairs; 1,500 drawn | existing |
| FRLL-Morphs and corrected MAD22 landmark cells | AF0's `lists/bench_s.csv` | 600 morphs per cell (MAD22 Webmorph 500), genuine 204 native + 204 E7 per family | existing |
| Approved Poisson set (H1) | `/mnt/t7/smad_heldout/h1_poisson` | 598 + 598 | existing |
| DINOv3 ViT-L/16 512 patch tokens (AF0 cache) | `AF0/feat/dinov3_512/{ar1,af0_w1,af0_w2,bench_s,h1,ar1g,af0_h}` | all complete during the run | reused (mean patch token); x1m, SMDD and the softened hosts extracted here |
| CLIP ViT-L/14 224 patch tokens (AF0 cache) | `AF0/feat/clip224/` | patch tokens only, no class token | CLIP re-run here for the class token; the same pass gives the mean patch token, equal to AF0's cache (64 images: max abs difference 0.0003 against mean magnitude 0.40, minimum cosine 0.9999998; `check_clip_mean_vs_af0.json`) |
| CLIP class token / DINOv3 pooled (identity-shrinkage triage, ID0) | `ID0/feat/part_cd_*` | being extracted (DINOv3 at 256 px, fp16 weights) | not used (incomplete, other resolution and precision) |
| Simple statistics (AF0) | `AF0/cues/{ar1,h1,bench_s,af0_w1}.npz` | complete during the run | reused; x1m, softened hosts, AF0 halves and AF0 zero / u50 / photos computed here with the same unchanged function |

Nothing was built, written as an image, resized or blurred here. Fits used only the 536 FRGC and colorFERET hosts
(asserted in code); FRLL, MAD22, SMDD test pairs, H1 and AF0 images were only scored (SMDD fit pairs only estimate
the softening direction).

## First small pass (11 Nov, 17:47 CET): DINOv3 mean patch token, OpenCV-style engine, fold 0 only

Written as soon as the numbers existed. Fold 0: 107 held-out hosts; one-person head trained on 426 hosts
(C = 0.01 by inner CV), two-person head on 423 hosts (C = 1). Source: `first_pass_dino_opencv_fold0.json`.

| Contrast (held-out hosts) | One-person head | Two-person head |
|---|---|---|
| warp-only x1 vs two-person morph x3 (main) | 0.933 [0.885, 0.973] | 0.980 [0.963, 0.994] |
| simple-statistic floor, same images (band power 0.125 to 0.25 cycles/px) | 0.912 [0.870, 0.952] | same |
| excess over the floor | 0.021 [-0.037, 0.081] | 0.068 [0.026, 0.114] |
| Laplacian variance alone (folded) | 0.80 (whole frame), 0.87 (face box) | same |
| photo x0 vs x3 | 0.944 [0.898, 0.980] | 0.986 [0.972, 0.997] |
| same-person morph x2 vs x3 | 0.652 [0.562, 0.740] | 0.759 [0.683, 0.838] |
| mirror self-morph xm vs x3 | 0.486 [0.391, 0.584] | 0.694 [0.605, 0.780] |
| photo x0 vs warp-only x1 | 0.543 [0.538, 0.557] | 0.564 [0.554, 0.584] |

## Q3, the author's test, with the fixed reading (all five folds, out-of-fold over 536 hosts)

OpenCV-style engine, one-person head. Point estimates decide (registered). Flag rate = share of E7 genuine frames at
or above the score of the 11th highest of 204 untouched frames (11/204 = 5.4% of untouched photos are flagged by
construction). Source: `readings_*.json`, `verdict.json`.

| Feature | AUC x1 vs x3 | Floor | Excess | Flag FRLL E7 OpenCV (i) | Flag MAD22 E7 OpenCV (ii) | Fixed reading |
|---|---|---|---|---|---|---|
| CLIP class token | 0.998 [0.995, 1.000] | 0.886 [0.862, 0.907] | 0.112 [0.092, 0.136] | 5.4% (11/204) | 5.4% (11/204) | works |
| CLIP mean patch token | 0.987 [0.979, 0.993] | 0.886 | 0.101 [0.080, 0.125] | 3.9% (8/204) | 4.9% (10/204) | works |
| DINOv3 mean patch token | 0.934 [0.918, 0.950] | 0.886 | 0.049 [0.022, 0.079] | 5.9% (12/204) | 4.9% (10/204) | mixed (excess 0.0485 < 0.05) |
| *Control, amendment 2: 27 simple statistics* | 0.853 [0.827, 0.876] | 0.886 | -0.033 [-0.051, -0.016] | 70.1% (143/204) | 9.8% (20/204) | fails (descriptive, not part of the vote) |

**Family verdict by the registered rule (works for at least 2 of the 3 features): "idea works".** It also holds
under every projection variant (table Q4). The floor statistic is band power at 0.125 to 0.25 cycles per pixel;
Laplacian variance alone reaches 0.774 (frame) and 0.775 (face box) on x1 vs x3.

All held-out contrasts (OpenCV-style engine, both heads, `q3q4.csv`):

| Feature | Head | x1 vs x3 | x0 vs x3 | x2 vs x3 | xm vs x3 | x0 vs x1 | One minus two-person head on x1 vs x3 |
|---|---|---|---|---|---|---|---|
| CLIP class token | one-person | 0.998 [0.995, 1.000] | 0.999 [0.996, 1.000] | 0.795 [0.758, 0.826] | 0.595 [0.548, 0.638] | 0.536 [0.531, 0.542] | +0.004 [0.000, 0.009] |
| CLIP class token | two-person | 0.995 [0.987, 0.999] | 0.995 [0.988, 0.999] | 0.828 [0.793, 0.856] | 0.674 [0.625, 0.718] | 0.512 [0.507, 0.517] | |
| CLIP mean patch | one-person | 0.987 [0.979, 0.993] | 0.987 [0.978, 0.993] | 0.769 [0.731, 0.805] | 0.439 [0.396, 0.483] | 0.498 [0.493, 0.503] | -0.009 [-0.015, -0.003] |
| CLIP mean patch | two-person | 0.996 [0.991, 0.999] | 0.996 [0.991, 0.999] | 0.849 [0.821, 0.875] | 0.705 [0.665, 0.742] | 0.497 [0.493, 0.502] | |
| DINOv3 mean patch | one-person | 0.934 [0.918, 0.950] | 0.946 [0.931, 0.961] | 0.643 [0.607, 0.682] | 0.496 [0.452, 0.541] | 0.534 [0.532, 0.539] | -0.051 [-0.065, -0.039] |
| DINOv3 mean patch | two-person | 0.986 [0.978, 0.992] | 0.990 [0.983, 0.994] | 0.751 [0.718, 0.785] | 0.707 [0.670, 0.744] | 0.550 [0.547, 0.556] | |
| 27 statistics (control) | one-person | 0.853 [0.827, 0.876] | 0.914 [0.896, 0.930] | 0.570 [0.534, 0.604] | 0.540 [0.504, 0.575] | 0.795 [0.772, 0.817] | -0.049 [-0.063, -0.036] |
| 27 statistics (control) | two-person | 0.902 [0.878, 0.921] | 0.946 [0.932, 0.959] | 0.641 [0.606, 0.675] | 0.619 [0.581, 0.653] | 0.798 [0.777, 0.818] | |

Floors on the same images: x0 vs x3 0.928 (excess of the one-person head: CLIP class 0.071 [0.053, 0.090], CLIP mean
0.059 [0.039, 0.079], DINOv3 0.018 [-0.004, 0.042]); x2 vs x3 0.689; xm vs x3 0.641; x0 vs x1 0.812 (noise
residual of the face box). Cross-engine (descriptive): the OpenCV-trained one-person head scores FaceMorpher x1 vs x3
at 0.999 / 0.992 / 0.945 (CLIP class / CLIP mean / DINOv3), the FaceMorpher-trained one at OpenCV images 0.998 /
0.984 / 0.941. FaceMorpher-trained, FaceMorpher-scored (descriptive engine): 0.999 / 0.991 / 0.952.
Regularisation chosen by inner CV for the final unprojected OpenCV heads: one-person C = 0.1 (CLIP class), 0.001
(CLIP mean, the grid's lower end), 0.01 (DINOv3), 1.0 (statistics, the upper end); two-person heads 1.0 (upper end).

### Flag rates on softened genuine photos (final OpenCV heads; set (iii) out-of-fold)

Registered sets (i), (ii); the other columns are descriptive. Set (iii) (amendment 1): the 200 hosts' own photos
after the existing shrink-and-enlarge path at the two registered strengths, threshold at 5% of the untouched x0 of
all 536 hosts. SMDD test: 500 renders vs their stored-small (80 px) copies, threshold at 5% of the renders.

| Feature | Head / projection | (i) FRLL E7 OpenCV | (ii) MAD22 E7 OpenCV | FRLL E7 AMSL | MAD22 E7 FaceMorpher | SMDD stored-small | (iii) hosts, AMSL strength | (iii) hosts, MAD22-FaceMorpher strength |
|---|---|---|---|---|---|---|---|---|
| CLIP class token | one-person | 5.4% | 5.4% | 5.9% | 9.3% | 22.0% (110/500) | 14.0% (28/200) | **27.5% (55/200)** |
| CLIP class token | two-person | 4.4% | 5.4% | 3.9% | 7.4% | 2.0% | 12.5% | 18.0% |
| CLIP class token | one-person, host-softening projected out | 5.4% | 5.4% | 4.4% | 4.4% | 3.2% | 2.0% | 4.5% |
| CLIP mean patch | one-person | 3.9% | 4.9% | 4.9% | 4.9% | 3.0% | 7.0% | 7.5% |
| CLIP mean patch | two-person | 4.9% | 4.9% | 5.4% | 6.4% | 2.6% | 10.0% | 11.5% |
| DINOv3 mean patch | one-person | 5.9% | 4.9% | 5.4% | 9.3% | 1.4% | 5.5% | 7.0% |
| DINOv3 mean patch | two-person | 5.9% | 4.9% | 5.9% | 11.3% | 2.2% | 4.0% | 6.0% |
| 27 statistics (control) | one-person | 70.1% | 9.8% | 82.4% | 100% | n/a | 26.0% | 93.5% |

The fixed reading uses (i) and (ii) only, as registered. On the hosts' own softened photos at the stronger strength
the CLIP class-token one-person head flags 27.5% [21.4, 34.2] (Clopper-Pearson), above the 15% bound that applies
to (i) and (ii); the CLIP mean patch and DINOv3 heads stay at or below 7.5%. Full table: `external_sets.csv`,
`softened_hosts_*.json`.

Softened one-person images against two-person morphs (amendment 1, 200 hosts, out-of-fold): AUC x3 vs softened x1
(MAD22-FaceMorpher strength) 0.990 [0.973, 0.999] (CLIP class), 0.974 [0.950, 0.990] (CLIP mean), 0.928 [0.899,
0.955] (DINOv3), against 0.998 / 0.984 / 0.941 for unsoftened x1 of the same hosts. The statistics head drops to
0.120 [0.068, 0.189] (it ranks softened one-person images above two-person morphs). The floor for this contrast is
1.0 in the reverse direction (the softened images have less high-frequency energy than the morphs), so its excess is
not informative.

## Q4 Trace subtraction (directions estimated without held-out hosts)

| Feature | Projection | AUC x1 vs x3 | Excess | Flag (i) / (ii) | Keeps separation | Loses reaction (i, ii) | (iii) hosts AMSL / FaceMorpher strength |
|---|---|---|---|---|---|---|---|
| CLIP class token | none | 0.998 | 0.112 | 5.4 / 5.4% | | | 14.0 / 27.5% |
| CLIP class token | softening (SMDD), (a) | 0.998 | 0.112 | 5.9 / 4.9% | yes | yes | 10.5 / 20.0% |
| CLIP class token | pipeline x0 to x1, (b) | 0.997 | 0.111 | 5.9 / 5.4% | yes | yes | 7.0 / 12.5% |
| CLIP class token | both, (c) | 0.997 | 0.111 | 4.9 / 5.4% | yes | yes | 7.0 / 10.0% |
| CLIP class token | host softening (amendment 1) | 0.997 | 0.112 | 5.4 / 5.4% | yes | yes | 2.0 / 4.5% |
| CLIP mean patch | none / (a) / (b) / (c) / host | 0.987 / 0.987 / 0.987 / 0.987 / 0.986 | 0.101 to 0.100 | 3.9 to 4.4 / 4.4 to 5.4% | yes | yes | none 7.0 / 7.5; (a) 8.0 / 10.5; (b) 10.0 / 10.0; (c) 10.0 / 11.5; host 2.5 / 1.5% |
| DINOv3 mean patch | none / (a) / (b) / (c) / host | 0.934 / 0.935 / 0.922 / 0.922 / 0.931 | 0.049 / 0.049 / 0.036 / 0.036 / 0.046 | 5.4 to 5.9 / 4.4 to 4.9% | yes | yes | none 5.5 / 7.0; (a) 4.5 / 7.5; (b) 3.5 / 3.5; (c) 3.5 / 3.5; host 4.5 / 4.5% |
| 27 statistics (control) | none / (b) / host | 0.853 / 0.920 / 0.907 | -0.033 / 0.035 / 0.021 | 70.1 / 9.8; 26.0 / 6.4; 15.7 / 6.4% | yes | no | 26.0 / 93.5; 16.5 / 79.5; 4.5 / 18.5% |

The fixed readings of Q3 do not change under any projection (CLIP: works; DINOv3: mixed). For the feature heads the
registered flag rates were already at the untouched level before projection, so "loses its reaction" holds
trivially on (i) and (ii); the change is visible only on set (iii).

## Q1 Direction consistency (held-out hosts, `q1.csv`)

Every step is consistent by the registered rule (share at least 0.75, lower bound above 0.65) for every feature and
both engines. OpenCV-style engine:

| Step | CLIP class: share / AUC of the projection | CLIP mean | DINOv3 mean |
|---|---|---|---|
| pipeline trace x0 to x1 | 0.978 / 0.665 [0.651, 0.681] | 0.847 / 0.548 [0.543, 0.553] | 0.983 / 0.715 [0.702, 0.730] |
| mirror mixing x1 to xm | 1.000 / 0.993 | 1.000 / 0.993 | 1.000 / 0.983 |
| mirror mixing, matched x1m to xm | 1.000 / 0.993 | 1.000 / 0.993 | 1.000 / 0.982 |
| same-person mixing x1 to x2 | 0.991 / 0.924 | 1.000 / 0.906 | 1.000 / 0.819 |
| second identity x2 to x3 | 0.856 [0.803, 0.902] / 0.825 | 0.884 [0.836, 0.927] / 0.821 | 0.853 [0.801, 0.901] / 0.699 |
| whole morph x1 to x3 | 1.000 / 0.982 | 0.994 / 0.982 | 1.000 / 0.894 |
| photo to morph x0 to x3 | 1.000 / 0.985 | 0.994 / 0.983 | 1.000 / 0.926 |

The pipeline step is consistent too (share 0.85 to 0.98), so the criterion separates "a step changes the features
the same way in every host" from nothing; it does not separate morph signal from processing traces.

## Q2 Geometry (cross-validated cosines, mean over 20 split halves, OpenCV-style engine; `q2_*.json`)

| Cosine | CLIP class | CLIP mean | DINOv3 mean | 27 statistics (control) |
|---|---|---|---|---|
| same-person mixing, whole morph | **0.89** [0.87, 0.91] | **0.83** | **0.91** | 0.96 |
| mirror mixing, whole morph | 0.88 | 0.69 | 0.57 | 0.97 |
| same-person mixing, second identity | 0.73 | 0.51 | 0.61 | 0.48 |
| same-person mixing, pipeline | -0.01 | -0.06 | 0.31 | 0.83 |
| whole morph, pipeline | -0.07 | -0.06 | 0.28 | 0.72 |
| same-person mixing, softening (SMDD) | 0.04 | -0.05 | -0.04 | n/a |
| same-person mixing, softening on hosts (amendment 1) | 0.14 | 0.16 | 0.12 | 0.75 |
| mirror mixing, softening on hosts | 0.10 | 0.15 | 0.15 | 0.76 |
| pipeline, softening on hosts | 0.67 | 0.31 | 0.52 | 0.86 |
| softening on hosts, SMDD softening | 0.36 | 0.29 | 0.28 | n/a |
| one-person head weights, two-person head weights | 0.79 | 0.80 | 0.86 | 0.71 |
| split-half reliability (same-person / mirror / whole / pipeline) | 0.98 / 0.99 / 0.99 / 0.95 | 0.96 / 0.99 / 0.97 / 0.67 | 0.97 / 0.99 / 0.98 / 0.99 | 0.99 / 1.00 / 0.99 / 1.00 |

Fixed readings: "the signal learned from same-person morphs is the signal of real morphs" (cosine at least 0.5)
holds for all three features, for same-person and for mirror mixing. "The signal is softness" (cosine above 0.5
with softening) holds for none of the three features, with either softening direction; in the space of the 27 simple
statistics it would hold (0.75). The pipeline direction is aligned with softening (0.31 to 0.67), the mixing
directions are not. FaceMorpher gives the same pattern (`q2_readings.csv`).

## Q5 Dose and second identity (`q5_*.json`)

- Graded FaceMorpher set (300 hosts, out-of-fold, descriptive engine): every head's mean score rises monotonically
  with the mixing fraction (Page test p below 1e-279 for all features, heads and training engines). OpenCV-trained
  one-person CLIP class head, AUC against m = 0: 0.82 (m = 0.1), 0.97 (0.2), 0.99 (0.3), 1.00 (0.5); DINOv3: 0.76,
  0.87, 0.92, 0.96 (FaceMorpher-trained heads within 0.03 of these).
- OpenCV-style engine dose (AF0 images, unseen persons, zero field / 0.25 / 0.5): Spearman with the mixing
  fraction 0.81 [0.79, 0.82] (CLIP class, one-person), 0.79 [0.77, 0.80] (CLIP mean), 0.71 [0.69, 0.73] (DINOv3):
  "rises" for all.
- Contributor dissimilarity (1 - glintr100 cosine of the two source photos), Spearman with s(x3) - s(x1),
  one-person head: CLIP class 0.03 [-0.05, 0.11] (does not rise), CLIP mean 0.13 [0.05, 0.21] (rises), DINOv3
  0.01 [-0.08, 0.10] (does not rise). Two-person head: 0.15 [0.07, 0.23], 0.16 [0.08, 0.24], 0.11 [0.03, 0.20]
  (rises for all). The partners are look-alikes by construction (median cosine 0.23).

## Unseen persons, matched geometry, unseen tool (final heads, no refit; descriptive)

| Feature | Head | AF0: 0.5 blend vs zero field | AF0: zero field vs photo | AF0 halves: morph vs its own two warped halves (amendment 1) | morph above both halves | floor for halves | AF0 halves flagged at photo 5% | H1 Poisson: morph vs genuine | H1 morphs flagged at genuine 5% |
|---|---|---|---|---|---|---|---|---|---|
| CLIP class | one-person | 0.999 | 0.562 | 0.999 | 100.0% | 0.831 | 5.6% | 0.890 | 61.9% |
| CLIP class | two-person | 0.999 | 0.556 | 0.999 | 100.0% | 0.831 | 5.1% | 0.920 | 73.6% |
| CLIP mean | one-person | 0.992 | 0.483 | 0.993 | 99.9% | 0.831 | 3.8% | 0.835 | 42.8% |
| CLIP mean | two-person | 0.998 | 0.469 | 0.999 | 100.0% | 0.831 | 4.8% | 0.881 | 57.5% |
| DINOv3 mean | one-person | 0.971 | 0.549 | 0.970 | 99.9% | 0.831 | 8.3% | 0.772 | 34.6% |
| DINOv3 mean | two-person | 0.995 | 0.524 | 0.994 | 100.0% | 0.831 | 4.8% | 0.767 | 31.8% |
| 27 statistics | one-person | (u0.25 missing) | | 0.803 | 91.5% | 0.831 | 3.9% | 0.715 | 6.2% |

The AF0 halves contrast has exactly matched geometry and storage (the reviewer's floor setting; Laplacian variance
alone 0.72 folded here). H1: 598 Poisson morphs of CASIA pairs against genuine photos of third CASIA persons.

## Benchmark cells (final OpenCV heads, no refit; descriptive)

AUC morph vs native genuine / vs neutral-only native / vs E7 genuine of the family; flag rate of morphs at the 5%
native threshold. One-person heads (two-person heads in `bench.csv`).

| Cell | CLIP class | CLIP mean | DINOv3 mean | 27 statistics (control) |
|---|---|---|---|---|
| FRLL-Morphs AMSL | 0.857 / 0.849 / 0.838; 50.8% | 0.881 / 0.849 / 0.879; 59.0% | 0.758 / 0.724 / 0.756; 11.3% | 0.997 / 0.994 / 0.703; 97.5% |
| FRLL-Morphs FaceMorpher | 0.998 / 0.998 / 0.998; 99.7% | 0.998 / 0.997 / 0.997; 99.5% | 0.935 / 0.920 / 0.937; 57.3% | 0.975 / 0.957 / 0.597; 83.8% |
| FRLL-Morphs OpenCV | 0.999 / 0.999 / 0.999; 99.5% | 0.997 / 0.997 / 0.997; 99.5% | 0.959 / 0.949 / 0.958; 75.2% | 0.943 / 0.905 / 0.373; 61.3% |
| FRLL-Morphs WebMorph | 0.893 / 0.886 / 0.879; 63.7% | 0.949 / 0.933 / 0.947; 78.5% | 0.918 / 0.902 / 0.917; 54.8% | 0.989 / 0.982 / 0.603; 95.5% |
| corrected MAD22 FaceMorpher | 1.000 / 1.000 / 1.000; 100% | 0.998 / 0.998 / 0.997; 100% | 0.942 / 0.929 / 0.909; 64.5% | 0.999 / 0.999 / 0.648; 99.3% |
| corrected MAD22 OpenCV | 0.950 / 0.946 / 0.948; 68.0% | 0.936 / 0.915 / 0.937; 71.3% | 0.915 / 0.898 / 0.916; 51.7% | 0.980 / 0.965 / 0.963; 85.7% |
| corrected MAD22 Webmorph | 0.909 / 0.902 / 0.905; 57.0% | 0.932 / 0.911 / 0.932; 67.4% | 0.892 / 0.872 / 0.894; 46.0% | 0.923 / 0.879 / 0.874; 60.4% |

The statistics control separates FRLL-Morphs morphs from native genuine frames at 0.94 to 1.00 and falls to 0.37 to
0.70 against E7 frames; the feature heads keep their AUC against E7 frames (largest drop 0.033).

## FRLL ladder (diagnostic only, every rung beyond x0 involves a smiling photo; no conclusion)

One-person OpenCV heads on the 102 FRLL persons: x1 vs x3 0.980 (CLIP class), 0.955 (CLIP mean), 0.938 (DINOv3);
xm vs x3 0.43 / 0.31 / 0.41. `frll_diagnostic_*.json`.

## What failed, what is weak, what could not be verified

- DINOv3: excess over the floor 0.0485, just below the registered 0.05, hence "mixed"; its one-person head is 0.051
  [0.039, 0.065] below its two-person head on x1 vs x3.
- The one-person heads do not separate mirror self-morphs from two-person morphs (xm vs x3: 0.44 to 0.60) and only
  partly separate same-person morphs (x2 vs x3: 0.64 to 0.80): what transfers is blending of two captures, not a
  second identity. Under the proposed class definitions (`14_CLASS_DEFINITIONS.md`) these heads would place
  same-person and mirror morphs with the attacks.
- Softness, descriptive sets: the CLIP class-token one-person head flags 27.5% of the hosts' own shrink-and-enlarge
  copies at the stronger registered strength and 22.0% of SMDD stored-small copies; projecting out the
  host-softening direction brings these to 4.5% and 3.2% with x1 vs x3 unchanged (0.997). The registered sets (i),
  (ii) are mild histories at which every feature head stays at the untouched rate.
- Geometry: x1 is warped toward the same person's shape, x3 toward the mean with another person's shape (a larger
  warp). The matched-geometry AF0 halves contrast gives 0.970 to 0.999 for the feature heads (floor 0.831), but on
  other persons (AF0's 663) and with the OpenCV-style engine only.
- Not tested: where in the frame the heads read blending (face, hair or surround; no blanked rerun), WebMorph or
  AMSL as training engines, any generator family.
- The person bootstrap does not include the variability of fitting the head; folds are fixed (seed 20261111).
  Regularisation sits at the grid's edge for the CLIP mean one-person head (0.001), the statistics control (1.0)
  and the two-person heads (1.0).
- Benchmark frames (prep_eval alignment) differ from the training frames (73_delin_align); benchmark numbers are
  descriptive and use AF0's 600-morph subsample.
- The SMDD softening direction comes from 256 px synthetic renders and 80 px copies, both passed through each
  backbone's own resize; the host-softening direction (amendment 1) exists for 200 of the 536 hosts.
- Operational: the DGX was heavily shared (load 75 to 100); one DINOv3 smoke run hit a CUDA allocation failure and
  succeeded on retry. One extraction process at a time throughout.

## Files

- Pre-registration and this page: `experiments/PD1_signal-isolation-paired-differences/landmark/{prereg,result}.md`.
- Tables: `q1.csv`, `q3q4.csv`, `external_sets.csv`, `bench.csv`, `q2_readings.csv`, `q5.csv`, `verdict.json`; per
  feature `readings_*.json`, `q1_*.json`, `q2_*.json`, `q3q4_contrasts_*.json`, `external_*.json`,
  `softened_hosts_*.json`, `q5_*.json`, `frll_diagnostic_*.json`, `meta_*.json`; `first_pass_dino_opencv_fold0.json`,
  `lists_summary.json`, `check_clip_mean_vs_af0.json`.
- Code: `src/PD1/landmark/` (`lists.py`, `feat.py`, `af0_means.py`, `cues.py`, `pd1_common.py`, `pd1_lib.py`,
  `analyse.py`, `summarize.py`, `run_feats.sh`, `run_feats2.sh`, `wait_af0_means.sh`).
- Large outputs: `/mnt/t7/smad_next/PD1/landmark/` (lists, features, statistics, out-of-fold scores, logs; 362 MB).
  Code-path test outputs (one C, 200 draws) are in `/mnt/t7/smad_next/PD1/landmark/test_res/`.
