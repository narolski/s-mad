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
