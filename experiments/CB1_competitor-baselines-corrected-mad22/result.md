# Competitor baselines on the corrected MAD22 and FRLL-Morphs (CB1): result

Status 13 Nov 2026, 03:55 CET: tasks 1, 2 and 4 read (FD-MAD fused 512 seed 3 still running); task 3 IDistill running on the DGX GPU (amendment 3; autoencoder 3.0 it/s, projected end 14 Nov 04:00-08:30). Full record `README.md`;
registration `prereg.md`.

## Task 1: what exists per competitor row, how it was evaluated, what a valid row needs

"Old subset" = the incomplete MAD22 copy (185 genuine + 4,069 morphs; `Datasety/downloads/MAD22`, the mad22 rows of
`smadcvpr_data/manifests/eval.csv`, frames from the old run of our aligner). "Corrected" = 204 genuine + 4,483 morphs.
"Our frames" = our 512-px two-eye-aligned frame resized to the network input. BK = `/mnt/t7/wcss_backups/smadcvpr/runs/A12BR/`;
L = `/lustre/pd03/hpc-narolski-1790461090/smadcvpr/runs/` (WCSS).

| Paper row | Released weights | Our retrain / re-implementation (where) | Evaluation so far, MAD22 copy, preprocessing | Needed for a valid row (corrected MAD22 x5 + FRLL-Morphs x5, EER + BPCER@APCER 1/5/10/20, E7 pools) |
|---|---|---|---|---|
| PW-MAD | none published | M5, DenseNet-121 + pixel map, our pipeline, 224, 8 seeds (BK es.pt + last.pt; meta and stored scores on L) | A12-BR: eval.csv = **old subset** + FRLL-Morphs, our frames, es.pt; "falsified" (TOST) | re-score M5 on corrected set + FRLL (running, DGX). No published MAD22 number: MAD22 row descriptive |
| MixFaceNet-MAD | yes (SMDD release, local) | M8 (our pipeline, ImageNet norm) and M8O (official procedure re-implemented, BGR/0.5), 224, 5 + 5 seeds, BK; AD5 retrains with the authors' code on WCSS (other owner) | Release: RS1, raw corrected MAD22 + raw FRLL, authors' crop (reproduces 9 of 9 cells, variant 1). M8/M8O: A12-BR, **old subset**, our frames; O x d0 MAD22-5 35.78 vs 13.69 | release row: cite RS1 (BPCER@APCER from RS1 scores to add). M8/M8O: re-score (running) |
| Inception-MAD | none published | M1, Inception-v3 scratch, 299, 5 seeds (BK); A45 incep_ofc, official SMDD procedure, 224, 5 seeds (**WCSS only**, L/A45) | A12-BR (M1) and A45 (incep_ofc): **old subset**, our frames; A45 MAD22-5 32.72 vs 10.53, gate FAIL | re-score M1 (running); copy incep_ofc from WCSS and re-score |
| OrthoMAD | none (training code only, no LICENSE) | M6, ResNet-18 + orthogonal heads, 224, 5 seeds (BK) | A12-BR, **old subset**, our frames; falsified | re-score M6 (running). No published MAD22 number. Published FRLL AMSL differs between sources (9.50 manuscript, 14.80 IDistill Table I) |
| MorphHRNet | none published | M2, HRNet-W48 scratch, 256, 5 seeds (BK); A45 hrnet_w18, 256, 5 seeds (**WCSS only**) | A12-BR / A45, **old subset**, our frames; A45 W18 40.91, W48 34.93 vs 9.42 | re-score M2 (running); copy hrnet_w18 and re-score. No per-family FRLL number published |
| MADation (ViT-B/16, ViT-L/14) | yes (local) | M3 / M3L recipe re-implementations (BK); AD5 authors'-code retrains on WCSS (other owner, not duplicated) | Release: RS1 on raw **corrected** MAD22 and raw FRLL, own crop. ViT-B/16 reproduces 4 MAD22 + 4 FRLL cells | cite RS1; add BPCER@APCER from RS1 scores |
| IDistill | none | none | never evaluated | retrain from the authors' code (commit 0473bb43, no LICENSE) on SMDD, WCSS; plan in prereg section 7 |
| SelfMAD | yes (WCSS `L/A12REL`; RS1 scored it on the DGX) | M4 SelfMAD-style, HRNet-W18, 384, 5 seeds (BK; descriptive); AD5 authors'-code retrains on WCSS (other owner) | Release: RS1 FRLL rows (own dlib crop, raw files). Not in the MAD22 table | cite RS1 for FRLL; M4 re-scored descriptively |
| FD-MAD | none (no code released) | A45 global-branch re-implementation (CPU RBF-SVM; scores only, no stored model), `/mnt/t7/smad_heldout/a45/fdmad/`; code `/home/narolski/mambamorph-code-a45/smadcvpr/a45_fdmad.py` (git 8e7731d); fused branch coded, never run (needs 5-point landmarks) | A45: eval.csv **old subset** + FRLL, our frames, features at 256 / 512 | retrain (minutes, CPU) and score on the CB1 list; fused branch only if landmarks exist |

Background fact (a), checked: the "did not reproduce" verdicts of A12-BR (TOST; report
`mambamorph-code/experiments/A12-BR_benchmark_recipes/raw/A12_3e_report.json`, manifest eval.csv sha256 86d055d3...)
and of A45 (`smadcvpr/results/A45/a45_read.md`, same eval.csv, score_noTTA, last.pt primary) were measured on the old
185 + 4,069 MAD22 subset in our old-aligner frames, plus FRLL-Morphs in our frames. A45 itself says "the evaluated MAD22
subset differs from the full benchmark". They are not statements about the corrected MAD22. The FRLL-Morphs part of
those verdicts is not affected by the MAD22 correction, but it too is "in our pipeline", not the authors'.

Background fact (b), checked: as released we have scored MADation (all variants), MixFaceNet-MAD and SelfMAD (RS1).
Every other row in the manuscript tables is currently "as reported, not verified".

## Results (registered readings; amendments 1-2 committed before reading; amendment 4 after the results review)

Full tables: `tables_all.md` (all arms; es/last/A45/FD-MAD) (per family, native and E7 pools, BPCER at APCER 1/5/10/20%), `cnn_es_per_arm.csv`,
`cnn_es_per_network.csv`, checks `cnn_es_c1_gate.csv`, `cnn_es_c1_verdicts.json`, `cnn_es_c2_pipeline_shift.csv`;
FD-MAD `fdmad_per_arm.csv`, `fdmad_c1f_gate.json`; released detectors (from RS1's scores) `cb1_released_rs1_bpcer.csv`.

### Checks

- C1 (scorer reproduces the stored WCSS scores of the same checkpoint, row by row, version without flip): passes for
  every seed of M1, M2, M6, M8, M8O (median row difference <= 4e-6 except M6 <= 2e-4; max <= 5e-3). PW-MAD M5 fails
  the max criterion on seeds 1, 2, 6 (max 0.016-0.030; EER within 0.5 in 9-10 of 10 cells): H100 vs GB10. By
  amendment 2, M5 is read on seeds 3, 4, 5, 7, 8.
- C2 (old-aligner vs CPU-backend frame of the same 204 FRLL photos), all 58 networks: median |logit difference| at most
  0.035 (M4), Kendall tau at least 0.990: the alignment re-run does not move these networks.
- C3: no row of the old MAD22 subset enters any result table (the gate rows are used only in C1 and in the A12-style
  comparison below, labelled).
- FD-MAD C1-F: global 256 seeds 1-3 and 512 seed 1 reproduce the stored A45 scores (max 1.3e-4 / 0 / 9e-7 / 2.5e-3;
  10 of 10 cells). Fused 256: its global part equals the gated global run exactly (max 0).

### Task 2: our CNN retrains (A12-BR R x d0, es.pt), native genuine pool, five-family mean EER (seed mean, 95% person bootstrap)

| Arm (method) | Seeds | Corrected MAD22 | vs published | Reading | FRLL-Morphs | vs published | Reading |
|---|---|---|---|---|---|---|---|
| M1 Inception-v3 299 (Inception-MAD) | 5 | 13.31 | 10.53 | inconclusive (delta +2.78 [-0.23, +5.80], M 3.16) | 34.46 | 8.11 | does not reproduce (worse) |
| M2 HRNet-W48 256 (MorphHRNet) | 5 | 33.74 | 9.42 | does not reproduce (worse) | see tables | none per family | descriptive |
| M5 DenseNet-121 + pixel map (PW-MAD) | 5 of 8 | 21.14 [19.06, 23.45] | none | descriptive | 17.41 [13.85, 21.02] | 10.62 | inconclusive (delta +6.79 [-1.55, +15.14], M 3.19) |
| M6 ResNet-18 orthogonal (OrthoMAD) | 5 | 23.98 [21.30, 27.08] | none | descriptive | 61.26 [58.36, 64.02] | 6.60 (14.80 in IDistill Table I) | does not reproduce (worse) |
| M8 MixFaceNet-S, our pipeline (MixFaceNet-MAD) | 5 | 23.06 [20.23, 26.20] | 13.69 | inconclusive (delta +9.37 [-0.32, +19.05], M 4.11) | 47.80 [44.91, 50.99] | 8.96 | does not reproduce (worse) |
| M8O MixFaceNet-S, official procedure re-implemented | 5 | 27.59 [24.56, 30.32] | 13.69 | does not reproduce (worse) | 61.66 [58.36, 64.94] | 8.96 | does not reproduce (worse) |
| M4 SelfMAD-style HRNet-W18 384 (descriptive) | 4 of 5 (seed 3 fails C1) | 46.48 [44.75, 48.38] | none | descriptive | 75.72 [74.02, 77.53] | (not read: M4 is descriptive) | descriptive |
| A45 incep_ofc, Inception-v3 by the official SMDD procedure, last.pt (A45 primary) | 5 | 32.20 [29.12, 35.23] | 10.53 | does not reproduce (worse) | 44.50 [41.45, 47.64] | 8.11 | does not reproduce (worse) |
| A45 hrnet_w18, MorphHRNet recipe at W18, last.pt (A45 primary) | 5 | 40.33 [37.10, 43.63] | 9.42 | does not reproduce (worse) | 63.87 [60.30, 67.28] | none per family | descriptive |

Secondary checkpoints (same rule): A12-BR last.pt: M1 MAD22 16.19 (inconclusive), FRLL 40.50 (does not reproduce); M2
MAD22 34.60 (does not); M8 25.83 / 42.85 (does not / does not); M8O 34.56 / 54.83 (does not / does not); M6 FRLL 68.79
(does not); M5 last.pt withheld (6 of 8 seeds fail C1); M4 last.pt not scored (pass stopped at 03:00 to free the GPU
for IDistill; descriptive arm). A45 es.pt: incep_ofc 21.38 / 39.98 (does not / does not); hrnet_w18 MAD22 29.04 (does
not). C1 passes for all 20 A45 networks.

Robustness of the seed exclusions (`review_addons/all_seed_readings.csv`): PW-MAD with all 8 seeds FRLL 16.58, delta
+5.96 [+0.78, +11.13], M 3.19: still inconclusive (the excluded seeds average 15.18, the included 17.41); MAD22 21.31.
M4 with all 5 seeds: MAD22 46.72, FRLL 76.11 (its seed-3 C1 failure is an EER tie artefact on saturated probabilities;
row agreement holds, median 0, max 0.008).

Cells above 50% EER are true inversions (AUC per family in `review_addons/auc_native.csv`; e.g. M4 AMSL and WebMorph AUC
0.000, M6 OpenCV 0.04): these networks rank the FRLL-Morphs classes almost perfectly in the wrong direction.

### What the earlier "did not reproduce" verdicts measured (results review F1; `review_addons/a12style_vs_cb1.csv`)

The A12-BR ledger EERs (`A12_3e_report.json`, `family_eer`) are computed on the E7 history-matched genuine pool with the
flip-averaged probability; the published numbers use the native genuine pool. Five-family means:

| Arm | MAD22, A12 style, old subset | MAD22, A12 style, corrected | MAD22, CB1 registered (native, logit), corrected | FRLL, A12 style | FRLL, CB1 registered |
|---|---|---|---|---|---|
| M1 Inception-v3 | 20.61 | 20.11 | 13.31 | 49.43 | 34.46 |
| M2 HRNet-W48 | 38.88 | 38.34 | 33.74 | 75.03 | 71.48 |
| M5 PW-MAD (8 seeds) | 24.85 | 24.90 | 21.31 | 26.46 | 16.58 |
| M6 OrthoMAD | 29.75 | 28.91 | 23.98 | 66.60 | 61.26 |
| M8 MixFaceNet | 31.57 | 30.92 | 23.06 | 58.72 | 47.80 |
| M8O MixFaceNet official | 36.33 | 35.98 | 27.59 | 67.58 | 61.66 |
| M4 SelfMAD-style (5 seeds) | 51.76 | 51.46 | 46.72 | 77.49 | 76.11 |
| A45 incep_ofc (last) | 39.29 | 38.96 | 32.20 | 52.23 | 44.50 |
| A45 hrnet_w18 (last) | 44.69 | 44.28 | 40.33 | 69.41 | 63.87 |

So the correction of the MAD22 copy itself changes these networks by less than 1 point; what changed the numbers is
the genuine pool (E7 vs native) and the score version. The old verdicts compared E7-pool EERs with native-pool published
numbers. With the registered native-pool reading the conclusion is unchanged for every arm except Inception-MAD M1 on
MAD22 (now inconclusive) and MixFaceNet M8 on MAD22 (inconclusive).

### Where the retrain gap comes from: MixFaceNet-MAD release vs our retrains (results review F2)

Released MixFaceNet-MAD weights through their own crop (RS1, crop v1, five-family mean): FRLL 9.19, MAD22 13.66; with
our aligned genuine frames as the genuine class (`cb1_released_rs1_bpcer.csv`, pool aligned_native): FRLL 12.54, MAD22
17.09. Our retrains on our frames: M8 47.80 / 23.06, M8O 61.66 / 27.59. The test frames cost about 3 points; our
training pipeline (SMDD in our frames, forbidden augmentations removed, our early stopping) costs 35-49 points on
FRLL-Morphs. The retrain rows therefore measure our pipeline, not the published methods.

With the history-matched (E7) genuine pools the five-family means rise in every arm (e.g. M8 MAD22 23.06 -> 31.03,
FaceMorpher 26.55 -> 65.12; M5 FaceMorpher 1.06 -> 17.74); MIPGAN cells are unchanged by construction (E7 leaves those
photos unchanged). Several FRLL-Morphs cells are above 50% (inverted ranking), as in A12-BR on the old subset.

### Task 4: FD-MAD partial re-implementation (a45_fdmad.py), native genuine pool (prereg section 8, amendment 4)

Partial re-implementation: 256-px SMDD copy (the paper used 1024 px), our 512-px frames, fixed windows. Resolution
mismatch disclosed in the code: at 256 the evaluation frames are reduced x2 by the loader, at 512 the SMDD training
files are enlarged x2; for a frequency-domain method this is the main confound and fits the polarity change between
256 (inverted) and 512.

| Arm | Seeds | Corrected MAD22 mean | FRLL-Morphs mean | Published global-only (16.62 / 2.08) | Published fused (6.12 / 1.85) |
|---|---|---|---|---|---|
| Global, 256 (A45 primary) | 3 (C1-F pass) | 56.08 [53.51, 58.77] | 83.02 [81.08, 84.92] (inverted) | does not reach | does not reach |
| Global, 512 (disclosed variant) | 3 (C1-F pass) | 28.13 [25.55, 30.79] | 14.90 [13.25, 16.59] (AMSL 0.02, FaceMorpher 0.98, OpenCV 14.83, StyleGAN2 58.64, WebMorph 0.00) | does not reach | does not reach |
| Fused, 256 | 3 | no reading: local branch not functional (s_local median about 1e-6, 90th percentile <= 1.1e-4), fused = global | | | |
| Fused, 512 (96-px windows as built) | 3 (global part equals the gated global run) | 33.01 | 19.04 | does not reach | does not reach |

Label: "partial re-implementation; does not reach the published number"; never a failure to reproduce FD-MAD.

### Released detectors (cited from RS1; BPCER at APCER added from RS1's own score files)

`cb1_released_rs1_bpcer.csv`: MADation ViT-B/16, ViT-L/14 and MixFaceNet-MAD, both crop variants, corrected MAD22 (204 +
1,000 / 984 / 500 / 1,000 / 999) and FRLL-Morphs, native raw genuine, aligned native and aligned E7. EERs equal RS1's.

### Task 5: paper label per method row (after the results review; IDistill pending)

| Row | Label for the paper | Basis |
|---|---|---|
| PW-MAD | as reported, not verified (no release; our pipeline re-implementation in the supplement) | M5 FRLL 17.41 vs 10.62 inconclusive (8 seeds: 16.58, inconclusive); no published MAD22 number |
| MixFaceNet-MAD | released weights, our scoring (RS1) | release reproduces 9 of 9 FRLL + MAD22 cells through its own crop |
| Inception-MAD | as reported, not verified (no release; our pipeline re-implementations in the supplement) | M1 MAD22 13.31 vs 10.53 inconclusive, FRLL 34.46; A45 32.20 / 44.50 |
| OrthoMAD | as reported, not verified (no release; supplement); **the manuscript's AMSL value is wrong** | The OrthoMAD paper (arXiv 2208.07841, Table II, local copy `/mnt/t7/smad_next/CB1/literature/orthomad.txt`) gives FRLL-AMSL EER 14.80 (BPCER@1 65.05, @20 10.89); 9.50 in the manuscript is the BPCER@APCER20 of OrthoMAD's WebMorph row (15.23 / 70.92 / 9.50). Correct OrthoMAD row: 14.80 / 0.98 / 0.73 / 6.54 / 15.23, mean 7.66 (manuscript 6.60). M6 FRLL 61.26 does not reproduce against either value |
| MorphHRNet | as reported, not verified (no release; supplement) | M2 33.74, A45 W18 40.33 vs 9.42 |
| MADation | released weights, our scoring (RS1) | ViT-B/16 reproduces 4 FRLL + 4 MAD22 cells |
| SelfMAD | released weights, our scoring (RS1), FRLL only; no MAD22 row scored | RS1 run A |
| FD-MAD | as reported, not verified (no code; partial re-implementation does not reach the published numbers) | best configuration global 512: FRLL 14.90, MAD22 28.13 |
| IDistill | pending (DGX run, amendment 3); fallback "as reported, not verified; the authors' code selects its checkpoint on the FRLL-Morphs test sets" | |

Proposed supplement caption for the retrain rows: "Re-implementations in our training pipeline (our 512-px frames of
SMDD, blur / resampling / JPEG augmentations removed, early stopping on our validation set). The released MixFaceNet-MAD
weights reach 12.5 / 17.1 (FRLL-Morphs / MAD22) with the same genuine frames, so these gaps measure our pipeline, not the
methods." Every table row should show both genuine pools (native and E7): swapping the pool alone moves single cells by
up to 99 points (e.g. M4 MAD22 FaceMorpher 99.6 vs 0.6).

## SA1 gap item 10: released-detector cells (amendments 5-6; reviewed 13 Nov, corrections applied)

Benchmark audits of released weights, our scoring. Independent review: `experiments/reviews/REVIEW_CB1_SA1CELLS_20261113.md`
(results-reviewer, opus; "qualification, not withdrawal"; every value traced to its file). Corrections applied: F1 (the
MixFaceNet-MAD reversal on our frames is a border effect: the release reads the black border as genuine; post hoc
mechanism, not separately tested), F2 (SelfMAD bridge with one score field: unchanged), F3 (4-ViTL uninformative), F4
(19-MFN complete range), F5 (16-MFN: own-crop value in the cell; our frames not interpretable; post hoc presentation
choice), F6 (14-MFN: no numbers in the cell), F7 (13-MFN bootstrap B 10,000 as AD1; 5-ViTL led by the share rising).
New scoring: MixFaceNet-MAD release in the 'rel' mode (our frames), DGX CPU, `src/CB1/score_mfn_rel.py`; reproduction
gate on 212 eval.csv rows against the stored A12REL scores: median |logit difference| 0.0057, max 0.070 (pass); A43
consistency check on 608 eval.csv frames: median 0.025, max 0.100 (pass).

| Cell | Audit-table text (reviewed) | Numbers and source (file, line or key) |
|---|---|---|
| 5-ViTL | Frame alone: 93% of photos rise, +0.07 logit [0.06, 0.08] (our frames, saturated scale); own crop +0.02 / +0.03 | our frames: `experiments/EV1_fixed-threshold-reread/AM2_B4_border_pairing.csv` line 8 (median 0.0668 [0.0583, 0.0835], share up 0.926); own crop: `experiments/CB1_competitor-baselines-corrected-mad22/sa1_cells/rs1_existing.json` keys madation_vitl14_v1 (+0.024 [0.019, 0.028], n 201) and _v2 (+0.029 [0.025, 0.034], n 204); border after own crop: `experiments/RS1_own-crop-rescore/rs1_border.csv` lines 30-31, 88-89 (MorDIFF frame 5.0% / 8.3% black, FRLL orig 0.0%) |
| 5-MFN | **Used, toward genuine**: frame alone −38.8 logit, 0% of photos rise (our frames); own crop (5-8% border) −3.7 / −3.9. The release reads the black border as genuine, consistent with its reversal on FRLL-Morphs cells where only morphs carry a border (post hoc) | our frames: `AM2_B4_border_pairing.csv` line 44 (−38.76 [−39.85, −37.20], share up 0.0); same file line 43: with the border equal the 65 px history moves it +4.80 [4.45, 5.26] toward morph; own crop: `experiments/CB1_competitor-baselines-corrected-mad22/sa1_cells/rs1_existing.json` keys mixfacenet_mad_smdd_v1 (−3.66 [−4.80, −2.76], 25% rise) and _v2 (−3.92 [−4.91, −2.96], 18% rise) |
| 13-MFN | Partly: morph vs reconstruction 0.59 [0.53, 0.65] (our frames, validity passed, frames border-matched); own crop 0.49 [0.41, 0.57]; crop-path dependent | `experiments/CB1_competitor-baselines-corrected-mad22/sa1_cells/a43_mfn.json`: "R4 (B20) vs R2 (D20) [AD1 main]" 0.589 [0.527, 0.654], B 10,000; validity "published MorDIFF (A) vs FRLL photos R0" 0.800 [0.735, 0.862]; C20 vs D20 0.428 [0.392, 0.463]; B20 vs C20 0.671 [0.599, 0.743]; own crop: `experiments/RS1_own-crop-rescore/result.md` line 185 (0.489 [0.410, 0.567]) |
| 14-MFN | Not interpretable (registered validity rule failed: R0 vs published MIPGAN-I 0.55 [0.47, 0.62]; border-mismatched) | `experiments/CB1_competitor-baselines-corrected-mad22/sa1_cells/ag1_mfn/ag1_read.json` key "mip1/frll/mixfacenet_mad_smdd__rel" → "R0>PUB" 0.548 [0.473, 0.623], benchmark_eer_pct 46.2. Detail only (border-matched ranks), key "mip1/primary/...": R2>R3 0.657 [0.635, 0.680], R3>R4 0.575 [0.510, 0.642], R2>R4 0.722 [0.649, 0.793]; flag rates not shown (threshold from a border-mismatched contrast) |
| 16-MFN | Change under 1 pt, own crop (5 FRLL families, mean −0.6); our frames reversed, not interpretable | own crop: `experiments/RS1_own-crop-rescore/rs1_expression.csv` lines 138-146 (neutral only) against `rs1_reproduction.csv` (all genuine): v1 −0.45 / −0.62 / −0.99 / −0.49 / −0.37 (AMSL, FaceMorpher, OpenCV, WebMorph, StyleGAN2), mean −0.58; v2 −0.50 to 0.00; per-family intervals about ±4 points; our frames: `experiments/C1b/result.md` line 111 (mean −0.26, EERs 75-98% on four cells) |
| 10-SelfMAD | Crop-path dependent: FRLL five-family mean EER 5.6 → 10.2 with our aligned genuine frames (SelfMAD's own dlib preprocessing; same raw morphs) | `experiments/CB1_competitor-baselines-corrected-mad22/sa1_cells/selfmad_croppath_bridge.json` (one score field, logit_noTTA, both pools): raw genuine 5.55 (AMSL 2.44, FaceMorpher 0.98, OpenCV 0.37, StyleGAN2 16.60, WebMorph 7.36), aligned genuine 10.24 (4.91, 1.51, 0.49, 28.50, 15.79); the mixed-field version `selfmad_croppath.json` gives the same values |
| 4-ViTL | Uninformative: 0.0% of FFHQ flagged, but the same rule catches only 0.3% of AMSL (own crop, saturated) | `experiments/RS1_own-crop-rescore/rs1_pool_rates.csv` line 258 (FFHQ 0.0%, n 1,934, crop v1; v2 n 1,997 line 1378), lines 298 / 301 / 310 (AMSL 0.3%, WebMorph 4.3%, MAD22 FaceMorpher 90.3%) |
| 19-MFN | Own 0.5 rule: 0.5% of photos flagged; catches 10-94% of FRLL / MAD22 morphs and 0-48% of diffusion morphs (own crop) | `rs1_pool_rates.csv` line 642 (raw FRLL photos 0.5% [0.0, 1.5]); lines 778-794: AMSL 12.5, FRLL FaceMorpher 83.1, OpenCV 62.4, WebMorph 10.0, StyleGAN2 33.9, MorDIFF 26.6, DiM-A 1.0, DiM-C 29.8, Fast-DiM 2.8, Fast-DiM-ODE 0.0, Greedy-DiM 10.2, Greedy-DiM-S 48.2, MAD22 FaceMorpher 93.9, MIPGAN-I 12.0, MIPGAN-II 9.1, OpenCV 49.5, Webmorph 14.2 (%, intervals in the file) |

Answer to the lead's question (review section 3.2): show numbers for 5-MFN (it measures exactly that row's cue) and
13-MFN (valid, border-matched); 14-MFN only "not interpretable"; 16-MFN the own-crop value, with our frames "not
interpretable (reversed)". Risk noted by the review: released detectors are not neutral to our aligner's black frame;
tables that score them on our frames should carry a border-matched caveat. Open, zero GPU (review H-new-1): MixFaceNet
logit against border share and border-matched FRLL-Morphs AUC.

## Black frame vs storage history (amendment 7, post hoc, zero GPU; reviewed 13 Nov, corrections applied)

Review: `experiments/reviews/REVIEW_CB1_BORDER_HISTORY_20261113.md` (results-reviewer, opus; "needs qualification").
Corrections applied: F1 (the history column is aligned-frame E7, not pure storage history), F2 (MorDIFF aligned pools
do carry black frame on the own crop path; not used in the table), F3 (bootstrap bug fixed: resamples without weight are
dropped), F4 (quartile dose-response; exact-zero subset; threshold label corrected), F5 (aligner step has no interval;
StyleGAN2 / MIPGAN rises are aligner-only), F6 (SelfMAD aligned-path border not measured).

**Reviewed answer for the comparison table** (the reviewer's wording): On each released detector's own crop path, no
genuine or morph pool behind the table's native and history-matched cells contains black-frame pixels
(`experiments/RS1_own-crop-rescore/rs1_border.csv`; MorDIFF aligned pools excepted, not used). A border-matched column
is therefore not needed for those rows. The history-matched column there is not pure storage history: for FRLL landmark
and MAD22 cells the history is applied to our aligned frames, and where raw-file history exists (DiM-A, Greedy-DiM) the
aligned-frame history effect exceeds the raw-file effect by 7-22 EER points (ViT-L/14: raw −7.8, aligned +14.2 on DiM-A)
without any black pixels. The column is labelled "aligned-frame E7 (our aligner + history)" and the aligned-native EER is
shown beside it. On our frames, morphs carry 3-26% black frame and photos none; MixFaceNet-MAD's AUC falls monotonically
with border share and a frame-only edit moves its logit by −38.8 toward genuine, so our-frames numbers for released
detectors carry a border caveat. A border-matched column is not feasible (no border-free FaceMorpher / OpenCV morphs;
n = 10-74 elsewhere).

### (A) MixFaceNet-MAD on our frames against black-border share (`border/border_mfn_corrected.json`; rows `border/border_mfn_rows.csv`)

Black share = pixels with R = G = B = 0 in the 512-px frame; FRLL photos median 0, max 2.3e-5; E7 pools median 0; morph
medians AMSL 0.053, FaceMorpher 0.260, OpenCV 0.192, StyleGAN2 0.032, WebMorph 0.051.

| Family | Spearman (logit, border), morphs | AUC all morphs vs photos | AUC by border quartile (low -> high) | border <= 0.005 (n, persons) | border exactly 0 (n) |
|---|---|---|---|---|---|
| AMSL | −0.80 | 0.100 [0.058, 0.151] | 0.25 / 0.13 / 0.02 / 0.00 | 0.462 [0.295, 0.652] (26, 13): at chance | 0.43 (2; too few) |
| FaceMorpher | −0.39 | 0.002 [0.000, 0.006] | 0.00 / 0.00 / 0.00 / 0.00 | none | none |
| OpenCV | −0.46 | 0.003 [0.000, 0.010] | 0.01 / 0.00 / 0.00 / 0.00 | none | none |
| StyleGAN2 | −0.50 | 0.768 [0.697, 0.830] | 0.89 / 0.87 / 0.80 / 0.51 | 0.908 [0.706, 0.991] (10, 10) | (1; too few) |
| WebMorph | −0.90 | 0.168 [0.111, 0.229] | 0.46 / 0.18 / 0.03 / 0.01 | 0.761 [0.614, 0.881] (74, 41) | 0.914 [0.817, 0.982] (18) |

Border-free subsets are selected by face geometry, not random, and small; the evidence is the monotone dose-response
together with the paired frame-only edit (−38.8 logit, `experiments/EV1_fixed-threshold-reread/AM2_B4_border_pairing.csv`
line 44).

### (B) The history-matched rise on each release's own crop path (`border/history_split_own_crop.csv`, 60 rows, recomputed by the reviewer with 0 mismatches)

| Release | Cell | raw genuine | aligned native | aligned-frame E7 (our aligner + history) | aligned native − raw (no interval) | aligned E7 − aligned native |
|---|---|---|---|---|---|---|
| MADation ViT-B/16 | AMSL | 3.91 | 5.45 | 24.42 | +1.54 | +18.97 |
| MADation ViT-B/16 | WebMorph | 2.33 | 2.94 | 15.71 | +0.61 | +12.77 |
| MADation ViT-B/16 | OpenCV | 1.97 | 2.96 | 6.86 | +0.99 | +3.90 |
| MADation ViT-B/16 | MAD22 FaceMorpher | 0.00 | 0.05 | 13.66 | +0.05 | +13.61 |
| MADation ViT-L/14 | all 10 cells | | | | −3.87 to +0.07 | −0.54 to +1.98 |
| MixFaceNet-MAD | AMSL | 15.16 | 21.57 | 41.19 | +6.41 | +19.62 |
| MixFaceNet-MAD | WebMorph | 12.27 | 17.26 | 35.79 | +4.99 | +18.53 |
| MixFaceNet-MAD | OpenCV | 4.89 | 5.87 | 11.75 | +0.98 | +5.88 |
| MixFaceNet-MAD | MAD22 FaceMorpher | 4.90 | 4.95 | 13.32 | +0.05 | +8.37 |
| MixFaceNet-MAD | StyleGAN2 / MIPGAN-I / MIPGAN-II | 9.20 / 16.24 / 20.60 | 13.21 / 21.58 / 26.00 | same as aligned native | +4.01 / +5.34 / +5.40 | 0 by construction: these "history-matched" rises are the aligner step alone |

Black fraction after the own crop (crop v1 and v2): 0.0000 for raw genuine photos, aligned native frames, every aligned
E7 pool used in the table and every raw morph set (largest FRLL WebMorph 0.0002); MorDIFF aligned pools 0.047-0.083
(not used in the table; there MixFaceNet-MAD's native EER falls 6.36 -> 2.97 and its history effect halves, +40.4 raw
vs +20.2 aligned, as expected if it reads black as genuine). Size of the aligner x history interaction where raw-file E7
exists (`experiments/RS1_own-crop-rescore/rs1_history.csv`, crop v1): DiM-A raw vs aligned history effect ViT-B/16 +34.4
vs +52.9, ViT-L/14 −7.8 vs +14.2, MixFaceNet-MAD +41.2 vs +48.1; Greedy-DiM +49.5 vs +61.7, −4.0 vs +10.8, +38.1 vs
+46.8; SelfMAD MorDIFF +43.7 vs +71.1. SelfMAD (own preprocessing): raw 2.44 -> aligned native 4.91 -> aligned E7 49.02
on AMSL; black fraction on its aligned path not measured.

**Files that allow the split without new scoring:** RS1 release score files (both crop variants) for raw, aligned-native
and aligned-E7 pools, `rs1_border.csv`, `rs1_history.csv`; SelfMAD A41 x7 / A43 own logits. **What would need new
data (author item, hard rule 3: storage / resampling code):** raw-file E7 versions of the FRLL photos for the landmark
families and MAD22 (history without our aligner), then under 1 GPU-hour of scoring; optionally an aligned frame with the
padding filled by content. Paired intervals for the aligner step are computable now from the RS1 files (not yet done).
