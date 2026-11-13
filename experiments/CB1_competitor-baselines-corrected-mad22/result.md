# Competitor baselines on the corrected MAD22 and FRLL-Morphs (CB1): result

Status 13 Nov 2026, 01:15 CET: task 1 done; task 2 readings for the es.pt networks of A12-BR (M1, M2, M5, M6, M8, M8O); last.pt, M4 and the A45 arms running; task 4 FD-MAD global 256 and fused 256 read, global/fused 512 running; task 3 IDistill waits on WCSS (smoke 6308827 pending). Full record `README.md`;
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

## Results (registered readings; amendments 1-2 committed before reading)

Full tables: `tables_es_and_fdmad.md` (per family, native and E7 pools, BPCER at APCER 1/5/10/20%), `cnn_es_per_arm.csv`,
`cnn_es_per_network.csv`, checks `cnn_es_c1_gate.csv`, `cnn_es_c1_verdicts.json`, `cnn_es_c2_pipeline_shift.csv`;
FD-MAD `fdmad_per_arm.csv`, `fdmad_c1f_gate.json`; released detectors (from RS1's scores) `cb1_released_rs1_bpcer.csv`.

### Checks

- C1 (scorer reproduces the stored WCSS scores of the same checkpoint, row by row, version without flip): passes for
  every seed of M1, M2, M6, M8, M8O (median row difference <= 4e-6 except M6 <= 2e-4; max <= 5e-3). PW-MAD M5 fails
  the max criterion on seeds 1, 2, 6 (max 0.016-0.030; EER within 0.5 in 9-10 of 10 cells): H100 vs GB10. By
  amendment 2, M5 is read on seeds 3, 4, 5, 7, 8.
- C2 (old-aligner vs CPU-backend frame of the same 204 FRLL photos): median |logit difference| 0.0001-0.016, Kendall
  tau >= 0.99 for every network: the alignment re-run does not move these networks.
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

With the history-matched (E7) genuine pools the five-family means rise in every arm (e.g. M8 MAD22 23.06 -> 31.03,
FaceMorpher 26.55 -> 65.12; M5 FaceMorpher 1.06 -> 17.74); MIPGAN cells are unchanged by construction (E7 leaves those
photos unchanged). Several FRLL-Morphs cells are above 50% (inverted ranking), as in A12-BR on the old subset.

### Task 4: FD-MAD re-implementation (a45_fdmad.py), native genuine pool

| Arm | Seeds | Corrected MAD22 mean | FRLL-Morphs mean | Reading vs published fused (6.12 / 1.85) |
|---|---|---|---|---|
| Global branch, 256 (A45 primary) | 3 | 56.08 [53.51, 58.77] | 83.02 [81.08, 84.92] | does not reproduce (worse); ranking inverted on most landmark cells |
| Fused (0.6 global + 0.4 local MRF), 256 | 3 | 56.08 [53.51, 58.77] | 83.02 [81.09, 84.93] | same as global: the local branch outputs P(bona) near 0 for every frame (median 7e-7), so fusion does not change the ranking |
| Global branch, 512 (disclosed variant) | 1 of 3 so far | 28.45 [25.99, 31.41] | 14.56 [12.93, 16.38] (AMSL 0.00, FaceMorpher 0.98, WebMorph 0.00, OpenCV 15.58, StyleGAN2 56.26) | seeds 2-3 running |

The paper's global-only means are 16.62 (MAD22) and 2.08 (FRLL); neither is reached. This is a partial
re-implementation on the 256-px SMDD copy with our frames, so the row label is "as reported, not verified"; our
numbers are not a failure to reproduce FD-MAD.

### Released detectors (cited from RS1; BPCER at APCER added from RS1's own score files)

`cb1_released_rs1_bpcer.csv`: MADation ViT-B/16, ViT-L/14 and MixFaceNet-MAD, both crop variants, corrected MAD22 (204 +
1,000 / 984 / 500 / 1,000 / 999) and FRLL-Morphs, native raw genuine, aligned native and aligned E7. EERs equal RS1's.
