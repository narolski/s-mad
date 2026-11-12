# Competitor baselines on the corrected MAD22 and FRLL-Morphs (CB1): result

Status 12 Nov 2026, 23:58 CET: task 1 (inventory and plan) done; no CB1 score read. Full record `README.md`;
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

## Results

None yet.
