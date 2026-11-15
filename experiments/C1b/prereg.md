# C1b Is the expression imbalance of the benchmarks used by detectors?

Written 11 Nov 2026, 15:25 CET, before this owner opened any per-image score file. Only manifests
(`eval.csv`), directory listings and the sha1 of the 204 genuine frames were read so far.

## What was seen before this page (post hoc portion)

The task message quotes an independent reviewer's preview (`expr_use.py`, `expr_recipes.py` in the
reviewer scratchpad; scripts read, outputs not seen): MADation ViT-L/14 release scores the neutral photo
above the smiling one in 101 of 102 persons (pooled neutral-vs-smiling AUC 0.855); its AMSL EER is 17.7
with all genuine photos and 24.5 with neutral-only genuine; CNN recipes and the SelfMAD release do not
show the pattern. `expr_use.py` read the release score files; `expr_recipes.py` read the 51 primary
recipe networks at their registered early-stopped checkpoint (`scores_eval_es.npz`).
**Therefore every release row and every early-stopped (es) recipe row below is post hoc.** The
last-checkpoint recipe files (`scores_eval_last.npz`) were not read by either preview script; H1 and H2
are decided on those files only.

## Hypotheses and falsifiers (fixed by the lead, applied unchanged)

- **H1 (smile direction):** CLIP-based MADation networks lower the morph score for smiling genuine
  faces. Test set: the 13 last-checkpoint MADation-recipe retrains, M3 ViT-B/16 seeds 1–8 and M3L
  ViT-L/14 seeds 1–5 (R × d0, `A36_networks.tsv` primary rows, `scores_eval_last.npz`).
  **Falsified if fewer than 10 of the 13 have a within-person neutral-above-smiling AUC ≥ 0.65**
  (point estimate). Otherwise "not falsified".
- **H2 (training length):** the 8 last-checkpoint M3 networks sit at or below 0.60 on the same
  statistic. **Falsified if their mean is ≥ 0.70.** Reading: mean ≤ 0.60 "prediction met";
  0.60 < mean < 0.70 "not falsified, prediction not met". The number of the 8 at or below 0.60 is printed.
- Note: H1 and H2 largely compete. If H2's prediction is met, H1 needs at least 5 of the 8 M3 networks at
  ≥ 0.65 despite a mean ≤ 0.60, which is unlikely. Both are evaluated as written.
- Existing networks use seeds 1–8 (A12-BR); no network is trained here.

## Statistic (a): within-person neutral-above-smiling AUC

For each of the 102 FRLL persons, the genuine class holds photo `NNN_03` (neutral) and `NNN_08`
(smiling). AUC_wp = mean over persons of 1[s(03) > s(08)] + 0.5·1[s(03) = s(08)] (s = morph score,
higher = more morph-like, as in the A12 scorer, AD1 and AG5; no flipping). AUC_wp > 0.5 means neutral
photos look more morph-like. Interval: person bootstrap, B = 10,000, seed 20261111, percentile 95%.
Secondary columns: pooled AUC (102 neutral vs 102 smiling, unpaired), sign-test p, and the same on the
MorDIFF genuine frames.

Frames: registered eval frames (`eval.csv`, variant `orig`). `frll_bona` and `dim_bona` are
byte-identical (204 of 204 sha1 equal, checked); `mordiff_bona` is a different alignment (0 of 204
equal) and gives the secondary column. SelfMAD with its own preprocessing uses
`experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz` (its own crop of the same rows).

## Detectors (one network per row; no fusion, no seed picking)

- Releases (post hoc): MADation ViT-B/16, ViT-L/14, FE ViT-B/16, FE ViT-L/14, FS ViT-B/16,
  FS ViT-L/14 (`A12_scored/A12REL/<name>/scores_eval.npz`, key `score_noTTA`); SelfMAD own
  preprocessing (`selfmad_own_eval.npz`, key `score`, primary for SelfMAD) and our pipeline
  (`A12REL/selfmad_hrnet_w18`, descriptive); MixFaceNet-MAD release (`A12REL/mixfacenet_mad_smdd`, our
  frames, descriptive because its own MTCNN crop branch is suspended). The dnorm / dscale diagnostics
  are not included.
- Recipes: the 51 primary R × d0 networks of `A36_networks.tsv` (M1 5, M2 5, M3 8, M3L 5, M4 5, M5 8,
  M6 5, M8 5, M8O 5), each at both checkpoints: es (`scores_eval_es.npz`, post hoc) and last
  (`scores_eval_last.npz`, pre-registered). Key `score`. All 102 files exist (checked by listing).
- Score root: `/home/narolski/mambamorph-code/smadcvpr_runs/A12_scored/` (the AD1 / AG5 location).
  `/mnt/t7/wcss_backups/smadcvpr/runs/A12BR/` holds weights only (es.pt, last.pt), no scores.

## Cells

- Available (12): FRLL-Morphs amsl, facemorpher, opencv, stylegan, webmorph (genuine `frll_bona`);
  DiM-A, DiM-C, Fast-DiM, Fast-DiM-ODE, Greedy-DiM, Greedy-DiM-S (genuine `dim_bona`); MorDIFF
  (genuine `mordiff_bona`). Morphs = `eval.csv` rows with label 1, variant `orig`.
- **Corrected MAD22 (5 cells): left out.** No score on the corrected MAD22 exists (canonical164
  cancelled; WCSS job 6299123 pending, start forecast 13 Nov). The `eval.csv` `mad22` rows are the old
  185 + 4,069 subset and are never read. MAD22c Webmorph, an imbalanced cell, is therefore missing.
- Imbalanced cells among the 12: FRLL-Morphs ×5 and DiM ×6 (11). Balanced: MorDIFF.

## Statistic (b): error rates by genuine subset, per cell

Genuine class G ∈ {all 204, neutral-only 102, smiling-only 102}; morph class unchanged.
Flag = score ≥ t. APCER(t) = share of morphs with score < t; BPCER(t) = share of G with score ≥ t.
EER: t over all unique scores of the cell, the t minimising |APCER − BPCER|, EER = mean of the two
(the AD1 convention). BPCER@APCER α (α = 5%, 10%): t = the largest morph score with APCER(t) ≤ α; the
threshold depends on morphs only, so changes are genuine-side. Paired differences neutral-only − all
and smiling-only − all for EER, BPCER@5, BPCER@10. Interval: two-way (pigeonhole) person bootstrap of
AD1 (`src/AD1/ad1_read.py` Draw): the 102 persons ~ Multinomial(102, 1/102); photo weight = its
person's count; morph weight = product of its two contributors' counts; one draw shared by all
detectors, cells and subsets; B = 2,000, seed 20261111; percentile 95%. Weighted EER and BPCER use the
same definitions with weights.

## Statistic (c): rank changes

For each of the 11 imbalanced cells, rank the rows by EER under "all genuine" and under "neutral-only
genuine". Rows: 9 releases + 18 recipe-checkpoint rows (seed mean of the per-network EERs; a summary,
not a fused score). Printed: both ranks, Kendall τ between the two orders, every row whose rank moves,
and every pair of rows whose order flips. A flip is "beyond noise" if the paired bootstrap interval of
the pair's EER gap changes sign between the two conditions (computed for release pairs only).

## Probe validation (step 3)

The C1 probe unchanged: features = `src/C_cue_checks/c_checks.py` `stats_job(…, "al")["mouth"]`
(imported, no new image code), fit = StandardScaler + LogisticRegression(C = 0.1) on the 204 `frll_bona`
frames, label 08 = smiling. Applied to aligned morphs with expression in the file name: corrected MAD22
FaceMorpher, MIPGAN-I, MIPGAN-II, OpenCV, Webmorph (`mad22_canonical_E7_inputs_v3_20261109T113746Z/
native`), MorDIFF (eval frames). Reported: accuracy at p = 0.5, sensitivity (smiling morphs flagged),
specificity (neutral morphs not flagged), AUC, with Clopper–Pearson / bootstrap intervals. Then the
smiling share of FRLL-Morphs ×5 and DiM ×6 is corrected for misclassification (Rogan–Gladen, with the
validation family of the closest type: landmark tools for amsl / facemorpher / opencv / webmorph;
MIPGAN for stylegan; MorDIFF for DiM) with a bootstrap interval over validation and target images.
**Fixed reading:** the neutral-only status of an FRLL-Morphs family is "supported" if the upper 95%
bound of its corrected smiling share is ≤ 10%; otherwise "not supported". Documentary support:
`/mnt/t7/Datasety/downloads/FRLL-Morphs/facelab_london/preprocess.py`, its README, and the dataset paper
(Sarkar et al.; web check allowed, marked checked or not).

## Cue-matrix reading rule (row 15)

A detector is listed as "uses expression" (row 15 USED by …) if AUC_wp ≥ 0.65 with lower bound > 0.5
**and** in at least 6 of the 11 imbalanced cells the neutral-only − all EER difference has a lower bound
> 0. "Not used by" if AUC_wp folded around 0.5 is below 0.60 with upper bound below 0.65 (the audit
plan's no-reading rule). Otherwise "undetermined". Recipe rows: per network, then counted per recipe.
The restriction of the genuine class is a matched comparison (same person, session and camera; only the
expression differs), not an image intervention; this is stated next to the reading.

## Guards and caveats fixed now

- The 03 and 08 photos of a person may differ in more than expression (small pose or lighting changes);
  not separable here.
- Neutral-only genuine has 102 photos against 204: intervals widen; differences are paired on one draw.
- The MorDIFF cell is balanced; restricting its genuine class creates an imbalance, so its rows are
  descriptive.

## Stop rule, budget, commands

CPU only (DGX), under one hour, zero GPU, no image re-encoded or written.
Python: `/home/narolski/mambamorph-code/.venv-spark/bin/python -I`.
- `src/C1b/c1b_read.py [--smoke]` (statistics a, b, c; smoke = 2 detectors, 2 cells, B = 50).
- `src/C1b/c1b_probe.py [--smoke]` (probe validation; smoke = 8 images per family).
Outputs: `experiments/C1b/*.csv|json`; nothing large expected (`/mnt/t7/smad_next/C1b/` if needed).

- **Pre-run review:** not run (zero-compute re-read; lead to decide).
- **Result:** `experiments/C1b/result.md`.
