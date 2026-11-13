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

## SA1 gap item 10: released-detector cells (amendments 5-6; benchmark audit, our scoring, not reviewed)

Files: `sa1_cells/` (rs1_existing.json, selfmad_croppath.json, a43_mfn.json, ag1_mfn/). New scoring: MixFaceNet-MAD
release, 'rel' mode (our frames), DGX CPU; reproduction gate on 212 eval.csv rows against the stored A12REL scores:
median |logit difference| 0.0057, max 0.070: pass; A43 consistency check (608 eval.csv frames): median 0.025, max
0.100: pass.

| Cell | Value | Path / source |
|---|---|---|
| 5-ViTL (frame alone, MorDIFF tight frame vs FRLL orig, same 204 photos) | +0.067 logit [0.058, 0.084] (93% of photos rise) | our frames, EV1 `AM2_B4_border_pairing.csv` (computed 11 Nov, not stated in EV1's result) |
| 5-ViTL, own crop | +0.024 [0.019, 0.028] (crop v1, n 201); +0.029 [0.025, 0.034] (v2, n 204) | RS1 scores; own crop keeps the border (black fraction MorDIFF frame 5.0% / 8.3%, FRLL orig 0.0%) |
| 5-MFN | −38.8 logit [−39.8, −37.2] (0% rise) | our frames, EV1 file; MixFaceNet is reversed on our frames (C1b), so not interpretable as a border cue |
| 5-MFN, own crop | −3.66 [−4.80, −2.76] (v1); −3.92 [−4.91, −2.96] (v2); 18-25% of photos rise | RS1 scores: the tight frame makes photos look more genuine |
| 13-MFN (diffusion render path: B20 morph vs D20 reconstruction, AUC) | 0.589 [0.527, 0.656]; same-person mix C20 vs D20 0.428; B20 vs C20 0.671; validity (published MorDIFF vs photos) 0.800 [0.732, 0.865]: valid | our frames, new scores, `a43_mfn.json` (person bootstrap B 2,000) |
| 13-MFN, own crop | 0.489 [0.410, 0.567] | RS1 corrected crop (existing) |
| 16-MFN (EER change, neutral-only minus all genuine) | our frames: mean −0.26 (C1b; reversed release, EERs 75-98% on four cells, descriptive); own crop: −0.37 to −0.99 (v1, five FRLL families, mean −0.58), −0.50 to 0.00 (v2) | C1b result; RS1 `rs1_expression.csv` |
| 10-SelfMAD (crop path; SelfMAD's own dlib preprocessing, not the SMDD crop script) | FRLL five-family mean EER 5.55 with raw genuine photos → 10.24 with our aligned genuine frames (AMSL 2.44 → 4.91, FaceMorpher 0.98 → 1.51, OpenCV 0.37 → 0.49, StyleGAN2 16.60 → 28.50, WebMorph 7.36 → 15.79); same raw-file morphs | existing scores (A41 x7, A32-RSX) via RS1's pools |
| 4-ViTL (own rule on FFHQ, own crop) | 0.0% of 1,934 (v1) / 1,997 (v2) FFHQ photos flagged; same rule catches AMSL 0.3%, WebMorph 4.3%, MAD22 FaceMorpher 90.3% (v1) | RS1 pool rates |
| 19-MFN (own 0.5 rule, own crop v1) | raw FRLL photos flagged 0.5%; morphs caught: AMSL 12.5%, WebMorph 10.0%, StyleGAN2 33.9%, OpenCV 62.4%, MAD22 FaceMorpher 93.9%, MIPGAN-I 12.0%, MIPGAN-II 9.1% | RS1 `rs1_pool_rates.csv` |
| 14-MFN (GAN one-person render, AG1) | **not interpretable** by the registered validity rule: on our frames the release does not rank the benchmark (FRLL R0 vs the published MIPGAN-I files AUC 0.548 [0.473, 0.623]; benchmark EER 46.2%). Descriptive, mip1/primary: R2 > R3 0.657 [0.635, 0.680], R3 > R4 0.575 [0.510, 0.642], R2 > R4 0.722; at the (near-chance) benchmark threshold same-person R3 flagged 69.5% [62.6, 75.8], two-person R4 78.0%, camera photos R0 42.8%. mip1/frll beside: R2 > R3 0.650, R3 > R4 0.677, R3 41.2%, R4 67.6% | our frames, new scores (7,229 AG1 frames; ids and finiteness checked), AG1 reader imported unchanged; `sa1_cells/ag1_mfn/ag1_read.json` |
