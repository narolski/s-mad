# What the smiling half carries: expression or capture detail (C1c)

Written 11 Nov 2026, 16:35 CET, before this owner computed anything new for this study. Follow-up to the
expression cue use study (C1b) after its independent review (`experiments/reviews/REVIEW_C1b_20261111.md`).
Zero GPU; existing per-image scores and existing image files only; nothing is re-encoded or written as
an image.

Abbreviations. FRLL = Face Research Lab London set (102 persons; photo 03 = neutral, 08 = smiling).
FERET = the colour FERET database (fa = regular expression, fb = alternative expression, taken in the same
session). FRGC = Face Recognition Grand Challenge 2.0 stills. CLIP = the pretrained image–text model;
ViT-B/16, ViT-L/14 = its vision transformers. MADation = CLIP fine-tuned with low-rank adapters for morph
detection; FE = its frozen-encoder variant (only the head trained); FS = its from-scratch variant. M3 / M3L =
our retrains of the MADation recipe on ViT-B/16 / ViT-L/14; es = early-stopped checkpoint, last = last
checkpoint. EER = equal error rate; APCER / BPCER = share of morphs accepted / genuine photos flagged;
AUC = area under the ROC curve. "Share" = share of pairs in which the less-smiling photo gets the higher
morph score.

## What was seen before this page (post hoc portion)

- The review and its preview output (`rev_scripts_c1b_20261111/main_out.txt`, read in full) and the lead's
  summary: in the FRLL files the smiling photo is larger in 102 of 102 persons (median byte ratio 1.43,
  same pixel size and JPEG tables) and its backdrop about five times noisier; ViT-L/14 release share 0.99 on
  our FRLL frames, 0.78 on the registered variant downsampled to 256-px resolution, 0.53 at about 150 px;
  FERET probe-clear pairs 0.564 [0.517, 0.613] (ties as half), FRGC 0.51; on FERET probe-clear pairs
  M3 last 0.49–0.57 per seed, M3L last 0.45–0.54, M3L es 0.63–0.74, M3 es 0.60–0.76, FE ViT-B/16 release
  0.32, FE ViT-L/14 0.38, SelfMAD (our pipeline) 0.555, MixFaceNet 0.593 (all ties as half).
- Therefore **H1, H3 and the es part of H2 are post hoc** (the reviewer's numbers on the same FERET
  pairs were seen). New relative to the preview: ties excluded and counted, the FRGC same-session pair
  definition, the untrained-network part of H2, H4, the owner's eye labels, and all recipe rows not
  printed by the reviewer.
- Own numbers already known from C1b (FRLL frames, EER tables).

## Hypotheses and falsifiers (fixed by the lead, applied unchanged)

Primary pair set for "those pairs": **FERET fa/fb same-session pairs that are probe-clear** (the FRLL-trained
expression probe of the cue checks (C1) gives one photo logit > 0 and the other < 0); the less-smiling photo
is the one with the lower probe logit. Probe labels are not ground truth. Secondary: FRGC same-session
pairs (below), probe-clear; all FERET pairs ordered by the probe difference (descriptive).
Share = above / (above + below); ties are counted and printed and do not enter the share. If ties exceed
10% of a network's pairs, its share is marked "saturated".

- **H1 (detail, not expression, for last-checkpoint ViT-B/16 retrains):** the 8 M3 last networks have a
  share ≤ 0.60 on the primary pairs. **Falsified if at least 5 of 8 reach 0.65.** Between: "not
  falsified".
- **H2 (near-pretrained CLIP features read expression):** (i) at least 10 of the 13 es retrains (M3 es
  seeds 1–8, M3L es seeds 1–5) reach a share ≥ 0.60 on the primary pairs; (ii) the untrained networks of
  the morph-free networks experiment (AD4; `/mnt/t7/smad_next/AD4/zero_step/<m3|m3l>/scores_eval.npz`)
  have a share on the 204 FRLL frames at least 0.15 away from 0.5 (≤ 0.35 or ≥ 0.65; these networks were
  not scored on FERET or FRGC, so part (ii) is on FRLL frames, where detail and expression are mixed).
  **Falsified if (i) fails or (ii) fails** for every untrained network that exists at analysis time; if the
  ViT-L/14 untrained scores do not exist yet, (ii) is decided on ViT-B/16 alone and marked incomplete.
- **H3 (the ViT-L/14 release does not read expression):** share ≤ 0.60 on the primary pairs.
  **Falsified at 0.80 or above.** Between: "not falsified".
- **H4 (the release's benchmark change is a threshold-placement effect):** with the threshold fixed on the
  development genuine photos (`eval.csv` set `devbona`, 5,033 FERET and FRGC photos, variant orig) at
  BPCER_dev = 5% (primary; 1% and 10% printed), the ViT-L/14 release's flag rate on the 204 FRLL genuine
  frames changes by **under 1 point** between neutral-only and all genuine photos, while its EER change
  (C1b, mean over 11 cells) is about +4.5. **Falsified if |flag rate(neutral-only) − flag rate(all)| ≥ 1
  point** at the primary threshold. Person bootstrap interval printed. The flag rate is
  the same for all 11 cells (one genuine frame set), and APCER at a fixed threshold does not depend on the
  genuine subset.

## Data

- FRLL raw files: `/mnt/t7/Datasety/downloads/frll_base/extracted/{neutral,smiling}_front/NNN_0{3,8}.jpg`.
- Scores: `mambamorph-code/smadcvpr_runs/A12_scored/` (9 release score sets, keys as in C1b:
  `score_noTTA` for releases, `score` for recipes; SelfMAD own preprocessing
  `experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz`), 51 primary recipe networks × {es,
  last}; AD4 untrained networks (`score` key or as stored; read-only). Total 111 score sets + untrained.
- Registered variants of the same 204 FRLL photos in `eval.csv`: `frll_bona` orig, jpeg90, jpeg70, jpeg50,
  chip, resample50, blur1; `resmatch` photos for every morph family (downsampled to that family's median
  morph eye distance: AMSL ≈ 113 px, WebMorph ≈ 112, OpenCV ≈ 130, FaceMorpher ≈ 138, DiM ≈ 63 at
  256-px files, MorDIFF ≈ 65 at 152-px files; StyleGAN resmatch = orig, no resampling); `mordiff_bona`
  orig (MorDIFF's own crop). Variants a score file does not cover are reported as missing.
- FERET: `devbona` rows named `SSSSS_YYMMDD_fa[_x]` / `_fb[_x]`, paired by subject, date and suffix
  (1,268 pairs, 936 subjects). FRGC: `devbona` rows `nd1_<season>_<subject>d<n>`; a same-session pair =
  two photos of one subject in the same season folder with consecutive recording numbers (n, n + 1),
  an operational definition not checked against the FRGC metadata (677 pairs by listing).
- Note: `devbona` includes 2,178 captures that are training data of our FERET/FRGC-trained (d1) arms;
  none of the networks scored here was trained on FERET or FRGC (releases and recipes are SMDD-trained).
  No `valx` file is opened.
- Expression probe: the C1 probe, unchanged (features from `src/C_cue_checks/c_checks.py` `stats_job`,
  logistic regression C = 0.1 fit on the 204 FRLL frames, label 08).

## Step 2: file and frame tables

Per person, neutral vs smiling raw FRLL file: bytes, pixel size, JPEG quantisation tables (identical or
not), chroma subsampling, backdrop noise = mean squared finite difference of the grey image in two backdrop
boxes (top-left and top-right 120 × 120 px at 20 px from the corners) and their standard deviation. On our
aligned 512 frames, by region (background top-left 5:90 × 5:40 and top-right 5:90 × 472:507; forehead
90:150 × 200:310; mouth 300:432 × 150:366): the same noise statistic and mean luminance. Same region
statistics on FERET and FRGC pair frames (does the more-smiling photo also have the noisier backdrop?).
Output: per-person CSV, share of persons with 08 > 03, median ratio.

## Step 3: separation checks (every score set)

Counts above / below / tied and share for: (a) FRLL frames; (b) every registered variant above; (c) FERET
probe-clear pairs, FRGC probe-clear same-session pairs, and all FERET pairs by probe-difference tertile.
95% intervals: person bootstrap for FRLL (B = 10,000), subject bootstrap for FERET / FRGC (B = 10,000),
seed 20261111.

**Eye labels.** The owner labels by eye a random sample (seed 20261111) of 40 FERET probe-clear pairs and
20 FRGC probe-clear pairs, viewing the two aligned frames, as "first more smiling / second more smiling /
no visible difference". Reported: agreement with the probe. These are an AI owner's labels, not ground
truth; the pair lists (`*_pairs.csv`, with paths and probe logits) are written for the author to label.

## Step 4: benchmark tables

The 12 imbalanced cells (11 scored; corrected MAD22 Webmorph has no detector score): EER with
neutral-only genuine photos as the headline column, all photos beside it, smiling-only last; BPCER at
APCER 5% likewise; mean over the 11 cells and rank among the 9 release score sets under both; paired
differences with the two-way person bootstrap of C1b (its stored replicates,
`/mnt/t7/smad_next/C1b/c1b_eer_bootstrap_reps.npz`, B = 2,000; the interval of the mean over cells is
computed from the same replicates).

## Reading (fixed now)

Per detector group (releases; M3/M3L es; M3/M3L last; CNN recipes): "evidence for expression" = share
≥ 0.60 (or ≤ 0.40, reversed) on FERET probe-clear pairs with the interval excluding 0.5, and in the same
direction on FRGC. "Evidence for capture detail" = the FRLL share falls toward 0.5 as resolution is
removed (orig → resmatch DiM / MorDIFF) while the probe still separates the photos, and the other-pool
share is within 0.40–0.60. Neither = undetermined.

## Stop rule, budget, commands

CPU only, under 2 hours. Python `/home/narolski/mambamorph-code/.venv-spark/bin/python -I`.
- `src/C1c/c1c_files.py [--smoke]` (step 2; smoke = 8 persons)
- `src/C1c/c1c_sep.py [--smoke]` (steps 3 and H1–H4; smoke = 3 score sets, B = 50)
- `src/C1c/c1c_bench.py` (step 4, from C1b outputs)
Outputs in `experiments/C1c_smiling-half-expression-or-detail/`; large files in `/mnt/t7/smad_next/C1c/`.

- **Pre-run review:** not run (zero-compute; lead to decide).
- **Result:** `result.md`.
