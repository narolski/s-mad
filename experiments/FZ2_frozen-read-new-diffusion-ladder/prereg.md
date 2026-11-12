# FZ2 Frozen read of the new diffusion ladder: pre-registration

Written 11 Nov 2026, 20:32 CET, by the frozen-features owner, **before any feature, head score, probe or statistic of
any image of the diffusion-autoencoder generation (DG1) was computed**. Known before writing: the DG1 set A validity
table and amendment 1 / 2 of `experiments/DG1_diffusion-generation-athena/prereg.md`; the frozen-features experiment
(FZ1) results, its independent review (`experiments/reviews/REVIEW_FZ1_20261111.md`, section 4 = the hypotheses below)
and FZ1 addendum A1. No DG1 image of set B or of the add-on has been looked at by this owner.

Question in plain words: on new persons and a ladder with the missing rungs (fresh-noise renders, noise-only and
semantic-only mixes, cross-session same-person mixes, dose series), do frozen CLIP / DINOv2 features and the frozen
SMDD heads read **mixing**, or only "not rendered from its own noise map"; and does the two-person-against-same-person
direction read a **second person** or **input disagreement**?

## Images (no new image; reading rules of DG1 amendment 1 apply in full)

- **Primary: the DG1 add-on run** (amendment 2; `gen_run = athena_DG1_addon`; Athena array 3545907, result tars
  `.../smad-next/results/DG1/DG1_addon_s<k>.tar`, k = 0–7), set B (FRGC 427 + colorFERET 109 hosts = 536), one process
  per host. Rungs at 20 decoding steps: REC (reconstruction from the photo's own noise map), SAME (host H mixed with
  the same person's other-session photo S), X (H mixed with the partner's S), MIR (H mixed with its mirror image),
  FRESH1 / FRESH2 (render(ε_k, z(H)), fresh noise), NOISEX / NOISES (z(H) with the slerped noise map of the mix with the
  partner / with S), SEMX / SEMS (the lerped semantic code with x_T(H)), DOSEX / DOSES (α = 0.1–0.4, 255 dose hosts);
  at 100 steps: REC, SAME, X, FRESH1.
- **Secondary (replication only): DG1 production set B** (`gen_run = athena_DG1`, tars `DG1_setB_s0..3.tar`): REC20,
  SAME20, X20, MIR20, DOSE α 0.1–0.4 (100 hosts). Never combined with add-on images inside one contrast.
- Not used: set A (FRLL), smoke and DGX test images.
- Missing shards at analysis time: analysed as available, counts printed, missing persons excluded from every
  contrast.

## Features and heads (all frozen; nothing is trained on DG1 images except the out-of-fold probes and baselines)

- Input: the 256-px DG1 PNG through the existing loader `mambamorph-code/smadcvpr/common.py` `ImageItems(res=224)`
  (PIL bilinear, the only resize; the MADation release's own preprocessing is the same resize of the file). Unchanged
  `common.py` is packed (sha256 ee71517a…).
- **clip_mad (primary):** OpenAI CLIP ViT-L/14 (timm `vit_large_patch14_clip_quickgelu_224`, the encoder tensors stored
  in the released MADation FE ViT-L/14 file, bit-identical to OpenAI CLIP in FZ1), MADation input (BGR, (x − 0.5)/0.5),
  768-d projected embedding, L2-normalised. **dinov2 (second):** timm `vit_large_patch14_dinov2.lvd142m` at 224, CLS.
- Computed on Athena in the container image `smad_torch221_cu121_v1.sif` (sha256 fedeff10…; torch 2.2.1, timm
  1.0.27), fp32, TF32 off. **Cross-environment check, before any DG1 feature is used** (tolerances in rank / logit
  terms, FZ1 review F7): the same job computes 64 A43 frames (8 per arm A, B, B20, C, C20, D, D20, E) that FZ1 computed
  on the DGX; passes if the FZ1 P3 head (seed 401) scores agree with Spearman ≥ 0.999 and max |Δ logit| ≤ 0.05, and
  the minimum feature cosine is ≥ 0.9995 (clip_mad) and ≥ 0.999 (dinov2). If it fails, Athena features are not used;
  features are recomputed on the DGX with FZ1's code.
- **Heads, no refit:** the five FZ1 SMDD heads (`/mnt/t7/smad_next/FZ1/heads/head_s40{1..5}.pt`; **seed 401 is the
  primary head**, the other four printed as a range) and the released MADation FE ViT-L/14 head (its own row). Score =
  softmax probability of the attack class.

## Statistics, folds, baselines

- AUC (positive = first named) with the two-way person bootstrap (`a41_read.py` pigeonhole method; persons = the 536
  set-B ids; image weight = count(host) × count(partner), one-person images count(host)); B = 10,000, seed
  [20261112, 2, 1]; 95% intervals; paired differences on the same draw.
- **Probes:** StandardScaler + L2 logistic, C from {1e-3, 1e-2, 1e-1, 1, 10} by inner 3-fold CV grouped by partner cycle;
  outer 5 folds from `src/AR1/folds.py` `person_fold_map()` (whole partner cycles dealt to folds, seed 20261113): an
  image is tested in fold k only if all its persons are in fold k and trained on only if none is. So no training row
  touches a test person. Transfer: a probe trained on one contrast scores images of other rungs out of fold (each image
  by the model of its fold).
- **Baselines (DG1 amendment 1), computed by this experiment on the same images:** PNG bytes; Laplacian variance in
  the face box (grey `cv2.Laplacian`, CV_64F, rows 70–220, columns 64–192, as `dg1_validity.py`); left-right asymmetry
  in the face box (same definition); thumb32 (32 × 32 × 3 block means of the whole image, logistic, same folds);
  surround-only thumbnail (face box set to grey 128, same block means, logistic). Scalars are folded (orientation from
  the point estimate, marked). **Best baseline** = the highest of the five AUCs for that contrast (chosen from the data,
  marked). **Excess** = paired bootstrap of (detector or probe AUC − best baseline AUC).
- Sensitivity (amendment 1): each primary number also without flagged items (black wedge, greyscale input, the two
  probable twin pairs, shared capture date; DG1 manifest columns, or recomputed with `dg1_manifest_extra.py`'s
  definitions if the add-on manifest is not ready) and per database (FRGC, colorFERET).
- Pair disagreement d = mean |first input − second input| in the face box of the DiffAE-aligned 256 inputs
  (`dg1_manifest_extra.py` definition), from the DG1 manifest or recomputed identically.
- Wording rule: "separable" for a probe AUC; "reads X" only where a hypothesis below says so.

## Hypotheses, contrasts and fixed readings (review section 4; 20 steps primary unless stated)

**H-new-1 (own-noise render).** Probe D_SR = SAME vs REC. Measured: D_SR applied out of fold to FRESH1 vs REC
(transfer AUC), and a probe trained on SAME vs FRESH1.
- Supported: FRESH1 vs REC along D_SR ≥ 0.90 with lower bound ≥ 0.85, **and** probe SAME vs FRESH1 ≤ 0.80 with upper
  bound ≤ 0.85.
- Falsified: FRESH1 vs REC along D_SR ≤ 0.65 with upper bound ≤ 0.70, **and** probe SAME vs FRESH1 ≥ 0.95 with lower
  bound ≥ 0.92.
- Otherwise not decided. Descriptive: the same with X vs REC as the direction, FRESH2 instead of FRESH1, FRESH1 vs
  FRESH2, the 100-step rungs; baselines and excess for every contrast; both feature sets (clip_mad decides).

**H-new-2 (noise map against semantic code).** Probes trained on NOISES vs REC and SEMS vs REC (primary: same-person
halves), NOISEX vs REC and SEMX vs REC (secondary), NOISES vs SEMS; D_SR applied to NOISES, SEMS, NOISEX, SEMX vs REC;
Laplacian-variance AUC of each against REC.
- Supported ("the noise map carries the mix direction"): probe NOISES vs REC ≥ 0.95 (lower bound ≥ 0.90), probe SEMS
  vs REC ≤ 0.85 (upper bound ≤ 0.90), and along D_SR NOISES vs REC exceeds SEMS vs REC by ≥ 0.10 (paired lower
  bound > 0).
- Falsified: probe SEMS vs REC ≥ probe NOISES vs REC (point estimates).
- Otherwise not decided. The review's Laplacian prediction (noise-only ≥ 0.90, semantic-only ≤ 0.65) was written for
  100 steps; the add-on has these mixes at 20 steps only, so it is printed descriptively.

**H-new-3 (weak second-person ordering of the frozen SMDD heads, on fresh persons).** Head s401 (and the release
head, separately): X vs SAME, SAME vs FRESH1, and the excess of X vs SAME over the best baseline of X vs SAME.
- Supported: X vs SAME ≥ 0.58 with lower bound > 0.50, SAME vs FRESH1 within [0.44, 0.56], and excess ≥ 0.05 with
  lower bound > 0.
- Falsified: X vs SAME < 0.55, or the excess interval includes 0 or lies below it (a simple statistic matches it).
- Otherwise not decided. Descriptive: the other four heads, REC / MIR / FRESH / dose rungs, 100 steps, the production
  replication (X20 vs SAME20), flag rates are not computed (no development-pool threshold is fixed here).

**H-new-4 (input disagreement).** Probe P_XS = X vs SAME (out of fold); d as above.
- Unstratified AUC A0 = P_XS on X vs SAME. Stratified A_s = pair-weighted mean of the within-stratum AUCs over the
  pooled quintiles of d (strata without both classes skipped; counts printed). Δ = A0 − A_s.
- Also A_hi = AUC of X against the SAME images in the top quintile of d among SAME images.
- Supported ("the direction reads input disagreement"): Δ ≥ 0.15 and A_hi ≤ 0.60.
- Falsified: Δ ≤ 0.05.
- Otherwise not decided. Descriptive: dose curves (mean P_XS score and AUC DOSEX_α vs DOSES_α per α; Spearman of the
  score with α·d inside two-person and inside same-person images), dinov2, production replication.

## Compute, commands, stop rules

- Athena feature extraction, account `plgmultivision-gpu-a100`, partition `plgrid-gpu-a100`, `-C memfs`,
  `--exclude=t0010`, 1 A100, `-c 8 --mem=96G`, container image, at most 1 A100-hour in total (estimate 0.1–0.3).
  Job 1 (when this file exists and the 8-image check has run): cross-environment check + production set B features;
  job 2: add-on features when its tars exist. Results copied back with sha256 to `/mnt/t7/smad_next/FZ2/`.
- Code `src/FZ2/` (`fz2_feats.py` extraction, `fz2_job.sbatch`, `fz2_pack.sh`, `fz2_read.py` analysis). 8-image
  check: `fz2_feats.py` on 8 production images on the DGX with its real command line before the first submission.
- Heads, probes, baselines and bootstrap on the DGX CPU (at most 4 processes).
- Stop: cross-environment check fails → DGX features; a shard tar fails its sha256 → that shard excluded and reported.
- Pre-run review: not run by the owner; the lead decides.
- Result: `result.md` in this folder; full record `README.md`.

## Deviations (dated)

- 11 Nov 21:31: Athena's start estimate for job 3545969 was 12 Nov 04:27 (most nodes unavailable). Features of the
  production set B are computed on the DGX instead, with `fz2_feats.py` in FZ1's environment (it reproduced FZ1's
  DGX features exactly on the 64 A43 frames, `envcheck_dgx_vs_fz1.json`), so no cross-environment check is needed for
  them. The Athena job stays queued; its check decides whether Athena features may be used for the add-on. Within one
  run (production or add-on) all features come from one source.
- 12 Nov 03:10 (recorded 12 Nov after the review, finding F7): the add-on features too were computed on the DGX
  (`src/FZ2/fz2_dgx_feats.sh` via `fz2_dgx_addon_watch.sh`, all 8 shards, done 03:10), not on Athena; Athena job
  3545969 was cancelled before it started, so the registered cross-environment check never ran and no Athena feature was
  used. Shards 2–7 were generated on a rented RTX 3090 (DG1), not on Athena.

## Amendment 1 (12 Nov 2026, registered and committed before any of its numbers is computed): post hoc follow-ups of the review

**Post hoc in substance**: ordered by the lead after the independent review (`experiments/reviews/REVIEW_FZ2_AR1A10_20261112.md`),
which already printed point estimates for θ and Laplacian checks. Zero GPU, existing features and images only, no image
written; DGX, `OMP_NUM_THREADS=2`, `nice -n 10`. Same folds (whole partner cycles), same two-way person bootstrap
(B = 10,000, seed [20261112, 2, 1]) and same probe routine as the registered read. Code `src/FZ2/fz2_amend1.py`, output
`amend1.json`.

- **(i) H-A transfer part (coherent-noise sharpening).** P_XS (clip_mad, trained X20 vs SAME20, out of fold) and D_SR
  applied to NOISEX20, NOISES20, SEMX20, SEMS20. Predictions: P_XS NOISEX vs NOISES ≥ 0.90 and SEMX vs SEMS ≤ 0.65.
  Reading: supported if both hold with NOISEX-vs-NOISES lower bound ≥ 0.85 and SEMX-vs-SEMS upper bound ≤ 0.70;
  falsified if NOISEX vs NOISES ≤ 0.65 or SEMX vs SEMS ≥ 0.85; otherwise not decided. Beside it: θ (angle between the
  two inverted noise maps, `theta_xT` of the DG1 add-on `gen_rows.csv`) alone as a score for X vs SAME; P_XS on X vs SAME
  stratified by pooled θ fifths and by pooled face-box Laplacian-variance fifths (pair-weighted within-stratum AUC, strata
  lacking a class skipped and counted), each with the bootstrap and Δ = A0 − A_s; Spearman of P_XS with θ and with
  Laplacian inside X and inside SAME. dinov2 descriptive.
- **(ii) H-B (render path, not content).** For every FZ2 contrast of the add-on read: the AR1 amendment-10 feature
  families computed on the 256-px DG1 images with the DG1 face box (rows 70–220, columns 64–192) as the inside mask in
  place of the landmark hull: 10 simple statistics (Laplacian variance inside/outside ratio, inside Laplacian variance,
  seam luma / red-green / absolute step, five spectral band shares; `src/AR1/floors10.py` definitions) and 12 residual
  statistics (first-order luma differences in x and y, inside and outside, std / mean absolute / kurtosis). Floors: best
  single statistic (folded, from the data), residual-12 logistic, simple-10 logistic, combined-22 logistic (out of
  fold); floor = the highest. Paired excess of each registered probe and head over the floor. Prediction (review): the
  residual-12 floor ≥ 0.95 on NOISES20 vs REC20 and FRESH1_20 vs REC20 (supported if both); falsified if it is ≤ 0.85 on
  both; otherwise not decided.
- **(iii) H-C on FZ1's A43 frames (heads read sharpness).** Head s401 on B20 vs C20 (FZ1 terms for X vs SAME at 20 steps)
  stratified by pooled fifths of the centre-256 Laplacian variance of the 512 frame (FZ1 P4 / addendum A1 values),
  pair-weighted, AD1 person bootstrap. Prediction ≤ 0.62 (supported); falsified if ≥ 0.65; otherwise not decided.
- **(iv) P_XS from DG1 on A43 frames.** A logistic probe with the registered routine trained on all add-on X20 vs SAME20
  clip_mad features (C chosen by the inner partner-cycle CV), applied to FZ1's A43 clip_mad features (512 frames;
  different persons and pipeline): AUCs B20 vs C20, B vs C, C20 vs D20, B20 vs D20, B vs D, and mean score per arm;
  dinov2 the same. Descriptive.

## Amendment 2 (12 Nov 2026, registered and committed before any of its numbers is computed): shared noise structure from the saved codes

**Post hoc in substance** (review of the SAME_orth draft, `experiments/reviews/PRERUN_DG1_SAMEORTH_20261112.md`, F2; the
reviewer printed shard-2 medians of the band and low-pass cosines). Zero GPU, measurement only, no image written; DGX
CPU, `OMP_NUM_THREADS=2`, `nice -n 10`. Code `src/FZ2/fz2_amend2.py`, output `amend2.json`.

- **Data.** Saved codes (`codes.npz`, noise maps x_T float32, read from the tars in memory) of add-on shards 2–6, the only
  local ones: `/mnt/t7/smad_next/DG1/rented_results/DG1_addon_s{2..6}_codes.tar` (sha256 in the `.sha256` beside each,
  checked), 335 hosts. Shards 0 and 1 have their codes on Athena (not fetched); shard 7's codes were never copied back
  and no longer exist (DG1 README). Per host: a = x_T(H), b = x_T(S) (same person), p = x_T(partner's S) (other person).
- **Measures per pair (a, b) and (a, p).** θ = arccos(cos(a, b)) (whole-map angle, recomputed); cosines in four radial
  frequency bands of the 2-D FFT per channel (bands r < 1/32, [1/32, 1/8), [1/8, 1/4), [1/4, 0.75) cycles/pixel; the
  reviewer's definition); cosine of the 8 × 8 block-mean low-pass maps. **Primary predictor: the lowest-band cosine
  c0(a, ·).**
- **Outcomes.** FZ2's face-box Laplacian variance L and the clip_mad P_XS score (out of fold, `read_addon_items.csv`) of
  the host's SAME20 and X20 image.
- **Statistics.** Spearman correlations within SAME and within X with a person bootstrap (B = 2,000; SAME: host resampled;
  X: two-way weights of host and partner); AUC of c0, low-pass cosine and θ for X vs SAME with the two-way person
  bootstrap (B = 10,000, seed [20261112, 2, 1]); joint model within SAME: OLS of rank(L) on rank(c0) and rank(θ) (ranks
  scaled to [0, 1]); ΔR² from adding θ to c0, bootstrap interval (B = 2,000, hosts resampled).
- **Fixed reading, H-A (shared structure).** Supported if, within SAME, Spearman(c0, L) ≥ 0.30 with lower bound > 0.10,
  **and** θ adds nothing beyond it (ΔR² interval includes 0 or ΔR² < 0.02). Falsified if Spearman(c0, L) within SAME has
  upper bound < 0.10, **or** θ adds beyond c0 (ΔR² ≥ 0.02 with lower bound > 0). Otherwise not decided. Note: θ and c0 are
  both functions of the same pair; the reading asks which summary carries the sharpness.
- Descriptive: the same with P_XS as outcome; the same within X; all bands and the low-pass cosine; which of c0,
  low-pass cosine and θ best separates X from SAME on these 335 hosts (θ was 0.916 on all 536).
