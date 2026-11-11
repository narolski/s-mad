# Fixed-threshold re-read of existing scores (EV1): full record

Owner: hypothesis-owner agent (Opus), for the lead. Started 11 Nov 2026 15:35 CET. This README is the full record;
`result.md` is the short reading; `prereg.md` holds the registration and its two amendments.
Experiment folder `/home/narolski/smad-next/experiments/EV1_fixed-threshold-reread/`, code
`/home/narolski/smad-next/src/EV1/`, large outputs `/mnt/t7/smad_next/EV1/`.

Abbreviations used throughout. FA = false-alarm rate (share of genuine images flagged as morphs). Miss = share of
morphs not flagged. EER = equal error rate. AUC = area under the ROC curve (0.5 = chance); O = max(AUC, 1 − AUC) of a
single attribute. CP = exact Clopper–Pearson 95% interval. devbona = the 5,033 development genuine photos of
`eval.csv` (FERET and FRGC photos used as D-MAD probes). E5 variants = the registered benign variants JPEG 90, JPEG
70, JPEG 50, blur1 (Gaussian blur) and resample50 of `eval.csv`. E7 = the shrink-and-enlarge history-matched copies
of the 204 FRLL genuine photos, one pool per morph family (`resmatch`; each pool is shrunk to its morph family's
median inter-eye distance and enlarged again). IED = inter-eye distance in pixels. "0.5 rule" = a release's own
decision, probability of morph above 0.5. δ = 1 − face-recognition cosine of a morph's two contributors. ρ =
Spearman rank correlation. glintr100 = the ArcFace R100 face-recognition network trained on Glint360K. FRLL = Face
Research Lab London set; FRLL-Morphs, MorDIFF, DiM = the morph benchmarks built on its 102 persons.

## 1. Question and current answer

Status 11 Nov 2026 17:55 CET: finished. Registered run, Amendment 1, the post hoc gender check and Amendment 2
(after the independent review) are complete; `result.md` rewritten with the review's corrected statements; no process
running.

Question: if each detector keeps one threshold fixed on development genuine photos, how many processed genuine
photos does it flag and how many morphs does it miss; can morph-blind models already solve each benchmark cell; and
does a detector's score inside one morph family rise with the dissimilarity of the two contributors?

Answer so far, on our 512-pixel frames (the releases' published numbers are not reproduced there): the SelfMAD
release with its own crop flags genuine photos that carry the benchmarks' own storage history at about the rate of
morphs (100% of E7 diffusion pools and of photos stored at the MorDIFF size at a threshold set on FRLL photos);
MADation ViT-B/16 flags 22 to 36% of the DiM and MorDIFF E7 pools; the MADation ViT-L/14 release's scores are
saturated on our frames, so its threshold-based figures are not evidence about that release (withdrawn by the
review). Miss rates depend strongly on which genuine pool sets the threshold. In all 17 cells a stored-file attribute
separates the classes perfectly (0 diagnostic cells). The pooled identity-dose slopes (+0.1 to +0.2) disappear
within gender: they are a gender-composition effect, not evidence of identity reading.

## 2. Timeline (11 Nov 2026, CET; times from file stamps and logs)

| time | step | command / output |
|---|---|---|
| 15:35 | Read `OWNER_BRIEF.md`, `NOTEBOOK.md`, `11_AUDIT_PLAN.md`, `10_ASSET_INVENTORY.md`, `12_STATE_AT_HANDOVER.md`, `ideas/CONSOLIDATED_v1.md`, the review of the MorDIFF ladder re-read (AD1) and the StyleGAN3 ladder (AG5), the cue checks (C1 to C4) result, and the four idea entries of `ideas/ROUND1_raw.json` (evaluation 0 and 1, invariance 0, identity 1). Inventory of manifests, npz key names and ids only (no score values). | — |
| 15:38 | `prereg.md` written (its header says 15:40), before any score value was read. Falsifiers copied verbatim. | `prereg.md` |
| 15:39 | Unit tests of the statistics helpers against brute force and scipy (threshold, EER, weighted Spearman). | passed |
| 15:41 | Part A smoke (8 items per pool) then full run. Killed at 15:46 after 2 detectors because each took 45 to 225 s on the loaded machine. | `ev1_partA.py` |
| 15:44–15:48 | Feature smoke (144 images took 350 s: chunk size 32 and contention). | `ev1_feat.py --smoke` |
| 15:47 | Part A patched: the 38-network descriptive block gets point estimates only; restarted. Finished 16:07. | `A1_*`, `A2_*`, `A3_*`, `A_partA.json` |
| 15:50 | Part B smoke: first failure (A41 table holds `None` for attributes that do not apply), fixed; passed. | `ev1_partB.py --smoke` |
| 15:51 | Full feature extraction (chunk size 8): 32,310 images, 0 errors, 2,247 s, finished 16:26. | `/mnt/t7/smad_next/EV1/feat.npz` |
| 15:52 | Part C full run started; oracle check written 15:52 before any detector score. Killed: 257 s per bootstrapped detector. | — |
| 15:58 | Part C patched with cached weighted ranks (`RankCache`, float32; max difference 1.7e-6); restarted, finished 16:04. | `C_oracle.*`, `C_dose.csv`, `C_partC.json` |
| 16:26–16:43 | Part B full run. | `B_*.csv`, `B_partB.json` |
| ~16:35 | Lead's message: six new requirements (class policies, NIST-style block, smiling half, dose controls, split-half null, scope statement). Read `ideas/CONSOLIDATED_v2.md` and `experiments/reviews/REVIEW_C1b_20261111.md`. | — |
| 16:38:52 | Amendment 1 appended to `prereg.md` (header first said 16:45 by mistake; corrected at 16:47). | `prereg.md` |
| 16:41–16:49 | Amendment runs: `ev1_amend.py` (A1, A2, A3), `ev1_partC2.py` (A4), `ev1_partB2.py` (A3 neutral headline, A5) to 16:56. | `AM_*` files |
| 16:48–16:49 | Post hoc gender check (not registered), after the MorDIFF gender strata were read. | `PH_gender_*` |
| 16:56–17:00 | `result.md` written, verified number by number against the CSVs (four errors in the first draft fixed, section 7). Report to the lead. | `result.md` |
| 17:27 | Resumed for the independent review (`experiments/reviews/REVIEW_EV1_20261111.md`, verdict: corrections required, numbers correct) and for this README. | — |
| 17:29 | Amendment 2 appended to `prereg.md` (header first said 17:40 by mistake; corrected at 17:30). | `prereg.md` |
| 17:31–17:43 | Border measurement of the E5 and E7 frames (`ev1_border.py`); first version via `stats_job` too slow (1.4 s per frame), replaced by the same definition computed directly and checked equal on 20 frames; 4,080 frames, 695 s. | `/mnt/t7/smad_next/EV1/border_e5e7.npz` |
| 17:36 | Amendment 2 smoke passed (`ev1_amend2.py --smoke`). | — |
| 17:44–17:51 | Amendment 2 full run (nice 10). | `AM2_*` files |
| 17:52–17:58 | `result.md` rewritten: new top section with the review's corrected statements, a withdrawn-statements table, in-place WITHDRAWN markers; numbers checked against the `AM2_*` files (two wordings fixed: share rising 97.5–100%, effect of adding devbona to the full-frame set). | `result.md` |

## 3. Data

All inputs existed before this experiment; nothing was generated. Hashes of every input file are in
`/mnt/t7/smad_next/EV1/input_sha256.txt` (written by `src/EV1/ev1_hashes.py`); hashes of every output in
`/home/narolski/smad-next/experiments/EV1_fixed-threshold-reread/output_sha256.txt`. All files are on the DGX
(local disk `/home/narolski` and the T7 drive `/mnt/t7`); none on WCSS, Athena or rented machines.

Manifests (sha256 checked by the code at every run):

| file | rows | sha256 | used |
|---|---|---|---|
| `/home/narolski/mambamorph-code/smadcvpr_data/manifests/eval.csv` | 44,666 (used: all rows except set mad22 (old 185 + 4,069 subset) and variant chip) | 86d055d349c63a225893ace30cb3db8b1e9aea4e72350d78152126d7a49d56c9 | every part |
| `/home/narolski/mambamorph-code/smadcvpr_data/manifests/gtest.csv` | 1,385 (FEI genuine: 198 neutral, 187 smiling; subject id = file stem) | 5ededd6fbeded7f2d480fe10838cfb7de82319ef5772771ac73eebcefb556a9b | FEI pools |
| `/mnt/t7/smad_heldout/ffhq_morphs/manifests/ffhqm.csv` | 17,000 (FFHQ genuine 2,000 orig + 5 E7 pools of 2,000) | 732b53c8a8c4b875645c99f11f81b401550a4050361090dea90998d45035234c | FFHQ pools |
| `/mnt/t7/smad_heldout/a43/data/manifests/a43.csv` (the earlier MorDIFF ladder study, A43) | 2,224 | ce3a264adb30928d6ae3abfb63619ed4b35fcb0ebb7fcca7e5001b212a5df4b8 | stored-small arm E, reconstructions D/D20, same-person mixes C/C20, morphs A/B/B20 |
| `/mnt/t7/smad_heldout/h3_sg3/data/manifests/h3sg3.csv` (StyleGAN3 set H3) | 1,692 (423 morphs, 423 one-identity renders, orig and pp) | 4b29a7c9d755e385a9c86fafc69fed84af8285efe132eb157e0637c05f05a6de | class policies |
| `/mnt/t7/smad_heldout/a37_sg3ctl/data/manifests/a37spread.csv` (spread-matched renders) | 846 | 28bde1efa6c3525f… (full hash in `input_sha256.txt`) | class policies |
| `/home/narolski/mambamorph-code/experiments/A36_published-detector-shortcuts/raw/A36_networks.tsv` | 51 primary R × d0 networks | in `input_sha256.txt` | recipe network list |

Score files (per-image detector outputs; all made by earlier experiments, read only):

- Releases: `/home/narolski/mambamorph-code/smadcvpr_runs/A12_scored/A12REL/<release>/scores_{eval,gtest,ffhqm,h3sg3}.npz`
  for madation_vitb16, madation_vitl14, madation_fe_vitb16, madation_fe_vitl14, madation_fs_vitb16,
  madation_fs_vitl14, madation_vitb16_dnorm, madation_vitb16_dscale (eval only), selfmad_hrnet_w18 (our pipeline),
  mixfacenet_mad_smdd. Keys `score_noTTA` (probability of morph) and `logit_noTTA`. Scored on our 512-pixel aligned
  frames. Never opened: `scores_valx_a.npz` and any name with fst / valx / A12SP.
- SelfMAD release with its own preprocessing: `/home/narolski/mambamorph-code/experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz`
  (26,077 rows; key `score`; no devbona, no JPEG 90 / 70, blur1, FEI or FFHQ rows); `smadcvpr_runs/A36/selfmad_own/own_h3sg3.npz`.
- Recipe retrains (A12-BR, last checkpoint): `/home/narolski/mambamorph-code/smadcvpr_runs/A12_scored/A12BR/<run>/scores_eval_last.npz`
  and `scores_gtest_last.npz`, key `score`; the 51 primary R × d0 networks (M1 Inception 5, M2 HRNet-W48 5, M3 MADation
  ViT-B/16 8, M3L MADation ViT-L/14 5, M4 SelfMAD-style HRNet-W18 5, M5 PW-MAD DenseNet 8, M6 OrthoMAD ResNet-18 5, M8
  MixFaceNet 5, M8O MixFaceNet official code 5). No last-checkpoint FFHQ, H3 or A43 scores exist for them.
- Morph-free networks of the morph-free study (A47), arm I-3: `/mnt/t7/smad_heldout/a47/runs/A47I3/<run>/scores_eval_last.npz`
  (M1 and M3, seeds 1 to 3).
- A43 scores: `/mnt/t7/smad_heldout/a43/a43_out/a43/<release>/{rel,own}/scores_a43.npz` (6 MADation releases, SelfMAD own
  and our pipeline).
- Spread-matched render scores: `/mnt/t7/smad_heldout/a41g/a41g_out/x4/<release>/{rel,own}/scores_a37spread.npz`,
  MixFaceNet `/mnt/t7/smad_heldout/a46/a41g_out/a46x4/mixfacenet_mad_smdd/rel/scores_a37spread.npz`.
- File table of the file-table study (A41): `/home/narolski/mambamorph-code/experiments/A41_shortcut-proof-zero-gpu/raw/results/a41_files.json`.

Embeddings (glintr100, precomputed elsewhere): `/mnt/t7/smad_heldout/a46/feat/a46_feat.npz` (5,146 keys: group raw =
204 FRLL photos; pub_mordiff 1,000, pub_dim_c, pub_greedy_dim, pub_greedy_dim_s 500 each), `/mnt/t7/smad_next/AR1/frll_src_emb.npz`
(204 photos, cross-check), `/mnt/t7/smad_heldout/a41_diffae/work/glint_embeddings.npz` (dim_a_pub, 100 DiM-A morphs).

Images read (decoded, never written) for Part B features and Amendment 2 borders: the aligned eval frames under
`/home/narolski/mambamorph-code/smadcvpr_data/eval/`; raw FRLL `/mnt/t7/Datasety/downloads/frll_base/extracted/{neutral,smiling}_front/`;
FRLL-Morphs `/mnt/t7/Datasety/downloads/FRLL-Morphs/facelab_london/morph_*`; MorDIFF `/mnt/t7/Datasety/downloads/MorDIFF/MorDIFF_crop/*/morphed/`;
DiM `/mnt/t7/Datasety/downloads/DiM-FRLL-Morphs/morphs/*`; corrected MAD22 raw
`/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted/` and aligned
`/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/native/`; FEI captures
`/mnt/t7/Datasety/downloads/FEI/extracted/<subj>-11.jpg` and `-12.jpg` (corner check only).

Sets produced (all on the T7 drive, `/mnt/t7/smad_next/EV1/`):

| file | content |
|---|---|
| `feat.npz` (45 MB) | per image: six colour statistics, zero-border fraction, 32 × 32 grey thumbnail of 16,155 aligned frames; size, bytes, container, chroma subsampling and colour statistics of 16,155 stored files (17 cells of the cue checks). Built by `ev1_feat.py` |
| `border_e5e7.npz` | zero-border fraction of 4,080 aligned genuine frames (FRLL orig and E5 variants, DiM copy, MorDIFF alignment, 12 E7 pools). Built by `ev1_border.py` |
| `feat_smoke.npz`, `border_e5e7_smoke.npz` | smoke outputs |
| `*.log`, `report_*.md` | run logs; markdown renderings of the tables by `ev1_report.py` |
| `input_sha256.txt` | hashes of all inputs |
| `scratch_copies/partB_section.md` | copy of the Part B text drafted in the session scratchpad (already merged into `result.md`) |

Items dropped: set mad22 of `eval.csv` (old incomplete subset) and variant chip, as registered; 10 FRLL-Morphs
self-pair "morphs" (same person twice) in Part C only; nothing else.

## 4. Code

Environment: DGX (ARM, GB10), Python 3.12.3 (`/home/narolski/mambamorph-code/.venv-spark/bin/python -I`), numpy
1.26.4, scipy 1.17.1, scikit-learn 1.9.0, Pillow 12.2.0. No model weights were loaded; no GPU used. Bootstrap seed
20261111 (numpy default_rng), B = 2,000 (B = 50 in smoke runs). Logistic regressions: scikit-learn StandardScaler +
LogisticRegression (C = 1, max_iter 2,000; thumbnail C = 0.1, max_iter 5,000).

| script | job | run order and arguments |
|---|---|---|
| `ev1_common.py` | loaders (manifests, detectors, score files with key rule), the person bootstrap `Draw` and `wauc` copied from `src/AD1/ad1_read.py`, thresholds `thr_at`, `flag_rate`, EER, CP, weighted Spearman, `RankCache` | library |
| `ev1_partA.py` | Part A: devbona thresholds, false alarms per pool, misses at native and worst-pool thresholds, crossed table, Kendall ranking | 1: `--smoke`, then no argument |
| `ev1_feat.py` | per-image features for Part B (imports `src/C_cue_checks/c_checks.py` unchanged) | 2: `--smoke`, then none |
| `ev1_partB.py` | Part B: null rows, diagnostic count, paired excess, null-conditional AUC, expression-balanced EER | 3 (needs `feat.npz`) |
| `ev1_partC.py` | Part C: oracle power check (written first), detector slopes | 4 |
| `ev1_amend.py` | Amendment 1 A1 (class policies), A2 (per-pool block), A3 (corner check, neutral-above-smiling share, neutral-only Part A) | 5 |
| `ev1_partC2.py` | Amendment 1 A4 (dose-slope controls, MorDIFF gender strata) | 6 |
| `ev1_partB2.py` | Amendment 1 A3 (neutral-only Part B) and A5 (split-half null choice) | 7 |
| `ev1_posthoc_gender.py` | post hoc: oracle and slopes within gender for every family | 8 |
| `ev1_border.py` | Amendment 2 B4: zero-border fraction of the E5 / E7 frames | 9, `nice -n 10` |
| `ev1_amend2.py` | Amendment 2 B1 (0.5 rule), B2 (logit shifts, saturation), B3 (threshold pool as a column), B4 (MorDIFF border pairing), B5 (paired FFHQ) | 10, `nice -n 10` |
| `ev1_report.py` | renders the CSVs as markdown tables (`A`, `B`, `C`, `amA`, `amB`, `amC`) | any time |
| `ev1_hashes.py` | sha256 of inputs and outputs | last |

Score-key rule: releases use `logit_noTTA` (checked to order rows exactly as `score_noTTA` for all 10, avoiding
float32 ties at thresholds); SelfMAD own uses `score`; recipes and morph-free networks use `score`. The 0.5 rule uses
`score_noTTA > 0.5` for releases (identical to `logit_noTTA > 0`, checked), `score > 0.5` otherwise. Threshold rule:
the smallest score t of the pool with share(score > t) ≤ α; flag = score > t.

## 5. Results

The reading with all main tables is in `result.md` (same folder). Every CSV below is the full table.

| file | rows | content (columns) |
|---|---|---|
| `A1_false_alarms.csv` | 3,596 | detector, block, α, threshold source, key, threshold, pool, n, FA, person-bootstrap 95% (FEI subject bootstrap; FFHQ CP) |
| `A2_miss.csv` | 4,464 | miss per family at native, worst-pool and per-family worst-pool thresholds, with intervals (primary networks) |
| `A2_family_means.csv` | 124 | per network: thresholds, binding pool, native family-mean EER, family-mean miss native / worst-pool, group means |
| `A3_crossed.csv` | 15,949 | morph variant × genuine variant per family: AUC [95%], miss at 5% FA on that genuine variant, margins, cell label |
| `A_partA.json` | — | per-network metadata (thresholds, ties, realised devbona FA, native EER and AUC), Kendall ranking, falsifier reading |
| `B_null_rows.csv` | 353 | every null per cell: AUC or O [95%], kind, note |
| `B_cells.csv` | 17 | best non-content null, diagnostic flags, best aligned null, thumbnail, best morph-free AUC |
| `B_detectors.csv` | 744 | detector AUC [95%], paired excess over the best null [95%], null-conditional AUCs |
| `B_expression.csv` | 744 | AUC all / neutral-only / smiling-only with paired differences, EERs |
| `C_oracle.csv`, `C_oracle.json` | 13 | oracle power per family and stratum, δ medians, AR1 cross-check |
| `C_dose.csv` | 806 | ρ(score, δ) [95%] per detector, family, stratum |
| `AM_A1_class_policies.csv` | 594 | MorDIFF controls and StyleGAN3 renders under both class policies (rates, CP) |
| `AM_A2_pool_block.csv` | 5,070 | per-pool FA [CP], neutral-only and all, photos changing side, persons, exact McNemar p |
| `AM_A3_neutral_above_smiling.csv` | 1,245 | within-person neutral-above-smiling share [95%] per detector and pool, FEI label |
| `AM_A3_worstpool_neutral.csv` | 2,976 | miss with the neutral-only and all-photo worst-pool thresholds |
| `AM_A3_crossed_neutral.csv` | 5,880 | crossed-table AUC with neutral-only genuine photos |
| `AM_corner_check.json` | — | backdrop corner-noise check for FEI and FRLL |
| `AM_B_cells_neutral.csv`, `AM_B_detectors_neutral.csv`, `AM_B_splithalf.csv`, `AM_partB.json` | 29 / 1,426 / 58 | Part B with the neutral-only headline; split-half null choice |
| `AM_C_controls.csv`, `AM_C_mordiff_gender.csv`, `AM_partC.json` | 119 / 248 | dose-slope controls; MorDIFF gender strata; readings |
| `PH_gender_oracle.csv`, `PH_gender_slopes.csv`, `PH_gender.json` | 48 / 624 | post hoc within-gender oracle and slopes |
| `AM2_*` | see 5a | Amendment 2 |

Headline numbers (all on our 512-pixel frames; the releases' published numbers are not reproduced there; the
own-crop re-score of the audit rows (RS1) redoes the key rows):

- SelfMAD release, own preprocessing, threshold fitted at 5% on the 204 FRLL photos (no development pool scored):
  flags 95.1% [CP 91–98] of resample50 photos, 53.9 to 85.3% of the FRLL-Morphs E7 pools except StyleGAN (4.9%), 100%
  of the 7 diffusion E7 pools and 100% [98–100] of the stored-small photos (`AM_A2_pool_block.csv`).
- MADation ViT-B/16 release: 30.9 to 32.8% of the 6 DiM E7 pools and 35.8% of the MorDIFF E7 pool at the devbona 5%
  threshold, each photo pair +59 to +69 flagged only after the history, 0 the other way (`AM_A2_pool_block.csv`).
- Miss rates: family mean at the devbona threshold 48.6% (ViT-L/14), 49.8% (ViT-B/16), 8.2% (SelfMAD own, test-fitted);
  at the worst-pool threshold 66.1 / 78.8 / 86.8% (`A2_family_means.csv`). Kendall τ native EER vs worst-pool miss
  0.394 (12 rows; metric kept).
- Null rows: best non-content null O = 1.000 in all 17 cells (stored width; chroma subsampling for corrected MAD22
  Webmorph); 0 diagnostic cells under every variant of the count; 3 of 17 below 0.90 if only aligned-frame nulls count.
- Identity dose: oracle power in MorDIFF, DiM-C, Greedy-DiM, Greedy-DiM-S only; pooled slopes of the releases +0.0 to
  +0.2; within gender every interval of the ViT-L/14 release includes 0 (`PH_gender_slopes.csv`).

### 5a. Amendment 2 results (after the independent review; files `AM2_*`, written 17:51)

All on our 512-pixel frames (SelfMAD own preprocessing excepted); the releases' published numbers are not reproduced
there; the own-crop re-score of the audit rows (RS1) redoes the key rows. The corrected statements with these numbers
are the top section of `result.md`.

| file | rows | content (columns) |
|---|---|---|
| `AM2_B1_rule05.csv` | 2,074 | flag rate at the 0.5 rule per detector, pool (genuine, genuine-side controls, morph families and morph variants), subset (all / neutral-only), n, k, CP, median effective IED, median border |
| `AM2_B2_logit_shift.csv` | 206 | paired logit shift against the same photos' FRLL orig: median and mean [95% person bootstrap], share rising [CP], crossings of the devbona 5% threshold and of the 0.5 rule in each direction, effective IED |
| `AM2_B2_saturation.csv` | 153 | logit 1st / 50th / 99th percentile for devbona, FRLL orig and each morph family |
| `AM2_B3_miss_by_threshold_pool.csv` | 1,242 | family-mean and per-family miss at 5% / 10% false alarms on each threshold pool or pool set |
| `AM2_B3_summary_ci.csv` | 66 | the unprocessed, full-frame ≥ 100 px and every-pool rules with person-bootstrap intervals (threshold refit) |
| `AM2_B4_border_pairing.csv`, `AM2_B4_mordiff_auc.csv` | 49 / 22 | MorDIFF tight-frame pairings; MorDIFF morph AUC against tight-frame genuine pools |
| `AM2_B5_ffhq_paired.csv` | 40 | FFHQ orig against each E7 pool, 2,000 pairs |
| `AM2.json` | — | pool median effective IED and border, family medians, stored-small IED and border |

Key numbers (each with its file):
- SelfMAD own, 0.5 rule (`AM2_B1_rule05.csv`): FRLL orig 0/204 [CP 0–1.7%]; resample50 91/204 = 44.6% [37.6–51.7];
  E7 MorDIFF 161/204 = 78.9% [72.6–84.3]; E7 DiM 113 to 120/204 = 55.4–58.8%; stored-small 198/204 = 97.1%
  [93.7–98.9]; E7 FRLL-Morphs 8.3–24.0% (StyleGAN pool 0%); morphs detected: FaceMorpher 99.0, OpenCV 99.8, MorDIFF
  57.9, DiM-A 24.8, Greedy-DiM 1.0%. Family-mean miss at the 0.5 rule 57.7%.
- ViT-B/16, 0.5 rule: FRLL orig 0.0%, E7 DiM 10.2–11.2%, E7 MorDIFF 4.9%, stored-small 3.9%; morphs detected:
  FaceMorpher 77.8, OpenCV 82.8, MorDIFF 55.5, Greedy-DiM 0.0%; family-mean miss 70.6%.
- ViT-L/14, 0.5 rule: 0.0% of every FRLL pool, 0.3% of devbona; morphs detected: FaceMorpher 72.5, OpenCV 82.5,
  WebMorph 15.7, Greedy-DiM-S 36.2, AMSL 0.0, StyleGAN 0.0%; family-mean miss 82.3%.
- Paired logit shifts (`AM2_B2_logit_shift.csv`), median [95%]: SelfMAD own resample50 +4.42 [4.17, 4.68], E7 MorDIFF
  +5.32 [5.13, 5.50], stored-small +7.10 [6.65, 7.36]; ViT-B/16 E7 MorDIFF +1.63 [1.33, 2.00], E7 DiM +1.26 to +1.33,
  stored-small +1.34 [1.16, 1.53], resample50 +0.36 [0.32, 0.43]; ViT-L/14 JPEG 50 +0.130 [0.126, 0.140] (43 up / 1 down
  across the devbona threshold, 0 across the 0.5 rule), resample50 −0.006, E7 MorDIFF +0.109.
- Saturation (`AM2_B2_saturation.csv`): ViT-L/14 FRLL orig logits −12.75 (1st) / −12.66 (50th) / −12.41 (99th).
- Threshold pool as a column (`AM2_B3_*`), family-mean miss at 5%: ViT-L/14 devbona 48.6, unprocessed FRLL 39.3
  [28–52], full-frame ≥ 100 px 49.2 [43–57], every pool 66.1 [62–70]; ViT-B/16 49.8 / 27.4 [21–45] / 54.8 [44–65] /
  78.8 [73–87]; SelfMAD own – / 8.2 [4–28] / 86.8 [84–90] / 86.8 [84–90].
- Border (`AM2.json`): every FRLL, E5 and non-MorDIFF E7 genuine pool median 0.000; MorDIFF alignment 0.544, E7 MorDIFF
  0.545, stored-small 0.543; morph families 0.031 (DiM-A) to 0.26 (FaceMorpher), MorDIFF 0.526.
- MorDIFF tight frame (`AM2_B4_*`): history alone with the border equal (E7 MorDIFF against MorDIFF alignment) ViT-B/16
  +1.35 [1.14, 1.55], SelfMAD own +4.64 [4.37, 4.82], ViT-L/14 +0.033, FE ViT-L/14 −0.52; frame alone (MorDIFF alignment
  against FRLL orig) ViT-B/16 +0.42, SelfMAD own +0.72, FE ViT-L/14 +5.49, FE ViT-B/16 +5.80. MorDIFF morphs against E7
  MorDIFF: AUC ViT-B/16 0.885 [0.844, 0.923], ViT-L/14 0.682, FE ViT-L/14 0.736, SelfMAD own 0.321 [0.272, 0.370].
- FFHQ paired (`AM2_B5_ffhq_paired.csv`): ViT-B/16 65 px histories +0.36 [0.34, 0.38] logits, 99% rising, 0.5 rule
  0.10 → 2.5–2.6%, devbona threshold 0.3 → 8.3–8.8%; FE ViT-B/16 +3.75, 0.5 rule 0.75 → 4.4%; SelfMAD our pipeline
  +2.57, 0.5 rule 18.4 → 64.0%; ViT-L/14 −0.02 (saturated); the two StyleGAN-matched E7 pools (history at 260 px,
  above the photos' resolution) are effectively unprocessed (median shift 0.000).

## 6. Checks

Verified:
- Statistics helpers against brute force on 200 random cases (threshold with and without weights) and against scipy
  (Spearman, weighted Spearman equals replicated-sample Spearman; EER vectorised equals loop).
- Loader: native EERs reproduce the record (released ViT-L/14 AMSL 17.7%, Greedy-DiM 9.8%, MorDIFF 28.9%; ViT-B/16
  MorDIFF 4.9%; the C1b review's AMSL 17.7 → 24.5 with neutral-only genuine photos).
- Every manifest sha256 asserted at load; every score file's `manifest_sha256` field asserted equal to its manifest.
- `logit_noTTA` orders rows exactly as `score_noTTA` for the 10 releases; the 0.5 rule on `score_noTTA` equals
  `logit_noTTA > 0` for all 10 (agreement 1.000, `/mnt/t7/smad_next/EV1/amend2.log`).
- Amendment 2 reproduces the review's recomputation: SelfMAD 0.5-rule rates (0 / 44.6 / 55–79 / 97.1%), the MorDIFF
  79 vs 58% comparison, ViT-B/16 shifts of 1.3 to 1.6 logits and FFHQ +0.36, the threshold-pool family means
  (39 / 27 / 8; 66 / 79 / 87; 49 / 55 / 87%). The review's ViT-L/14 JPEG 50 crossing count was 42; here 43 up and 1 down.
- A43 files: the re-scored registered MorDIFF genuine frames equal the eval file's scores to ≤ 2.4e-6 (MADation logits)
  and ≤ 1.5e-3 (SelfMAD), so devbona thresholds transfer.
- `RankCache` (float32) against the float64 weighted Spearman: max difference 1.7e-6 over 2,000 replicates.
- Border fraction computed directly equals `c_checks.stats_job`'s value on the first 20 frames (asserted in code).
- Realised devbona FA 4.9 to 5.0% at the 5% threshold for every network except M1 seed 3 (ties, 0%) and M2 seed 2 (4.79%).
- The independent review recomputed every number it checked and found them matching.
- Every script was run with `--smoke` (8 items per pool or the cue checks' smoke subset, B = 50) before the full run.

Not verified:
- Each release on its own crop (except SelfMAD); the own-crop re-score of the audit rows (RS1) is doing that.
- Oracle power for the five FRLL-Morphs families, Fast-DiM and Fast-DiM-ODE (no morph embeddings exist).
- SelfMAD own preprocessing on a development pool, JPEG 90 / 70, blur1, FEI, FFHQ (no scores exist).
- Detector scores on the corrected MAD22 (none exist; null rows only).
- FRLL-Morphs morph expression (inferred by a probe); the passport minimum IED of 90 px quoted by the review (clause
  not checked).
- The logistic nulls let a morph's second contributor appear in training folds (C3 fold rule).

## 7. Dead ends, failures, bugs, withdrawn statements

Runs and bugs:
- Part A first full run (15:41) killed after 2 detectors: 45 to 225 s per detector at load 75 to 90 with swap full.
  Fix: point estimates only for the 38 descriptive recipe networks (deviation 1 in `result.md`).
- Feature smoke took 350 s for 144 images: `pool.map` chunk size 32 left most of 8 workers idle; contention. Fix:
  chunk size 8 (full run 2,247 s for 32,310 images).
- Part B smoke failed: `TypeError` on `float(None)`; the A41 file table holds `None` for attributes that do not apply
  (JPEG quality on PNG cells). Fix: skip `None`. Smoke subset lacked some cells: `C17.get` with a smoke-only skip.
- Part C first full run killed: 257 s per bootstrapped detector (two weighted-rank passes on 2,000 × 2,175 arrays).
  Fix: `RankCache` (δ ranks once per stratum, float32), 8 times faster.
- `pkill -f "ev1_partA.py"` (and later pattern kills) killed my own shell because the shell's command line contained the
  pattern; three times. No data were affected (the target processes also stopped). Rule adopted: kill by PID in a
  separate command, bracket pattern, nothing else on that command line.
- A completion monitor fired "partC done" early because the oracle log line also contains "written". No harm.
- Amendment 1 header time 16:45 (true 16:38:52) and Amendment 2 header time 17:40 (true 17:29); both corrected with a
  note in `prereg.md`.
- `eval.csv`'s `ied` column holds the original photo's 202.3 px for every FRLL-derived pool (E5, E7, MorDIFF alignment),
  not the history's resolution. Amendment 2 uses the effective IED instead: E7 pool = its morph family's median native
  IED (the `prep_eval.py` resmatch target), resample50 = half the original; stated in the outputs.
- The border measurement through `c_checks.stats_job` ran at 1.4 s per frame at nice 10 (load 110); replaced by the
  identical definition computed directly, checked equal on 20 frames.
- FFHQ loader in `ev1_amend2.py` first rebuilt a dictionary per row (quadratic); fixed before the full run.
- Null-conditional AUC (registered): with a perfect stored-file null no stratum holds both classes except one in
  MorDIFF, where width still separates the classes inside the stratum; the statistic cannot measure anything here.
- First draft of `result.md`: four numbers were wrong and were fixed before delivery: E7 FRLL-Morphs range for ViT-L/14
  neutral-only 2.9–6.9 → 3.9–6.9; SelfMAD our pipeline maximum FA 1.6 → 3.2% (FEI smiling); M4 range 85–100 → 74–100%;
  dnorm wording.

Degenerate or odd detectors (reported, not corrected): M1 seed 3 has 275 devbona scores saturated at 1.0 (its 5%
threshold flags nothing); the MixFaceNet-MAD release on our frames has AUC 0.002 to 0.168 on four FRLL-Morphs cells;
the SelfMAD release in our pipeline scores devbona high, flags ≤ 3.2% of any genuine pool and misses 50 to 100% of
morphs at its devbona threshold.

Statements withdrawn after the independent review (`experiments/reviews/REVIEW_EV1_20261111.md`), kept and marked in
`result.md`:
1. Released MADation ViT-L/14 "24 to 34% at JPEG 50, 24.5% stored small, 22% FFHQ": withdrawn as evidence about this
   release; its scores are saturated on our frames (all genuine logits within about 0.3 logits; the JPEG 50 shift of
   0.13 logits moves 42 photos across the development threshold and none across its own 0.5 rule). Awaits RS1.
2. "No detector beats the best non-content null": withdrawn; it is true of any detector when the null is perfect.
3. The identity-dose slope as an effect: withdrawn; within gender the slopes are not distinguishable from zero, the
   pooled slope is a gender-composition effect.
4. "Benign processing" for histories below 90 px between the eyes (the DiM and MorDIFF E7 pools at 63 to 65 px, the
   stored-small photos at about 64 px): replaced by "the benchmark's own storage history".
Earlier, under Amendment 1: the cue named "expression" was renamed "smiling half" (C1b review).

## 8. Observations outside the question

- Gender composition: all FRLL-Morphs, MorDIFF and DiM pairs are same-gender (gender taken from the MorDIFF folder
  names, 102 of 102 persons, no conflict). Pooling female and male pairs creates the dose slopes; within gender the
  oracle keeps power (ρ 0.44 to 0.65) while detector slopes vanish. Any future dose or similarity analysis on these
  benchmarks must stratify by gender.
- The MorDIFF alignment of the same 204 photos (a tight frame with about 54% zero border) is flagged by released FE
  ViT-L/14 at 35.8% and by the ViT-L/14 recipe retrains at 43 to 75% at their devbona thresholds: the frame itself
  moves scores (Amendment 2 B4 isolates it).
- The SelfMAD release in our pipeline puts devbona above FRLL: the development pool is not exchangeable with the test
  photos for that scorer; fixed thresholds from devbona are uninformative for it.
- FRLL corner noise (my statistic: first differences in the corners): smiling / neutral 1.24, 85% of persons; FEI
  0.99, 44%. The C1b review's "about five times" used another statistic; both say the FRLL smiling captures are noisier.
- MixFaceNet-MAD release (our frames) orders FEI neutral above smiling in 0.94 of subjects, the opposite of most
  MADation rows (0.15 to 0.41).
- Both dose-slope control slopes found are negative (file size in DiM-C −0.22; morph-free M3 in FRLL StyleGAN −0.11,
  −0.13), opposite in sign to the detector slopes.
- The morph-free MADation-recipe network reaches EER ≤ 2.6% on 9 to 10 of the 12 scored cells (A47 I-3).
- The tight MorDIFF frame alone moves the frozen-encoder releases strongly (FE ViT-L/14 +5.49, FE ViT-B/16 +5.80 logits
  at full resolution), more than the 65 px history does; for the fine-tuned ViT-B/16 the history dominates (+1.35
  against +0.42). A frame-matched control is therefore needed before reading any frozen-encoder row on MorDIFF.
- The FRLL-Morphs StyleGAN E7 pool (target 254 px) and the FFHQ StyleGAN E7 pools (260 px) are copies of the
  unprocessed photos in effect (median shift 0.000): their "history-matched" label carries no history.
- MixFaceNet-MAD release logits on our frames are extreme (FRLL orig median −18.7; MorDIFF alignment shifts −38.8);
  its rows on our frames are not interpretable.

## 9. Open items and next steps

1. Own-crop re-score of the audit rows (RS1): amend before reading to include JPEG, resample, DiM history, FFHQ and FEI
   pools through each MADation crop, the 0.5 rule, both genuine-class definitions for SelfMAD (review follow-up 2).
2. Border test for the landmark cells (border-matched history control or border blanking) (review follow-up 3).
3. Oracle embeddings for the FRLL-Morphs, Fast-DiM and Fast-DiM-ODE morphs (about 8,500 images through the existing
   glintr100 route; needs CPU provider or a GPU slot) so the registered landmark falsifier can be applied.
4. A development genuine pool scored through SelfMAD's own preprocessing (FERET / FRGC D-MAD probes), so its threshold
   is not test-fitted.
5. Detector scores on the corrected MAD22 (pending elsewhere); then the 5 MAD22 cells get detector rows.
6. Verify the passport IED clause (90 px) quoted in the review.

## 10. Handover state

No process running (checked 17:55 CET). Nothing queued on WCSS, Athena or Vast. Every script is idempotent: rerunning
it overwrites its outputs. Compute spent: 0 GPU-hours, 0 USD; CPU about 3 core-hours on the DGX (11 Nov 15:40–17:51).

## 11. Reproduce from scratch

```bash
cd /home/narolski/smad-next
PY="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"
$PY src/EV1/ev1_partA.py --smoke && $PY src/EV1/ev1_partA.py
$PY src/EV1/ev1_feat.py --smoke && $PY src/EV1/ev1_feat.py
$PY src/EV1/ev1_partB.py --smoke && $PY src/EV1/ev1_partB.py
$PY src/EV1/ev1_partC.py --smoke && $PY src/EV1/ev1_partC.py
$PY src/EV1/ev1_amend.py --smoke && $PY src/EV1/ev1_amend.py      # needs A_partA.json
$PY src/EV1/ev1_partC2.py --smoke && $PY src/EV1/ev1_partC2.py
$PY src/EV1/ev1_partB2.py --smoke && $PY src/EV1/ev1_partB2.py    # needs feat.npz
$PY src/EV1/ev1_posthoc_gender.py --smoke && $PY src/EV1/ev1_posthoc_gender.py
$PY src/EV1/ev1_border.py --smoke && $PY src/EV1/ev1_border.py
$PY src/EV1/ev1_amend2.py --smoke && $PY src/EV1/ev1_amend2.py    # needs border_e5e7.npz, A_partA.json, feat.npz
$PY src/EV1/ev1_report.py > /mnt/t7/smad_next/EV1/report_all.md
$PY src/EV1/ev1_hashes.py
```
Smoke runs write only `*_smoke.npz` or nothing; full runs overwrite the CSV / JSON files in the experiment folder.
