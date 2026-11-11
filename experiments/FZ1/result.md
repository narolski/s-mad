# FZ1 result: do frozen foundation features read the mixing step of a DiffAE morph?

Owner run, 11 Nov 2026. Prereg (`prereg.md`) written about 15:25 CET before any new number was computed
(P1 is a post hoc re-read; P2–P4 are new). Runs 15:30–RUN_END CET, DGX only (shared GB10; peak GPU memory of
our processes 2.3 GB; at most 6 of our CPU processes at a time). Code in `src/FZ1/`; small results in
`experiments/FZ1/`; feature caches, out-of-fold probabilities, head weights and logs in `/mnt/t7/smad_next/FZ1/`.
Every interval is a 95% bootstrap interval: A43 / FRLL contrasts use AD1's two-way person (pigeonhole) draw
(seed [20261107, 43, 1], B = 10,000; benchmark EERs B = 2,000 from the same draw), StyleGAN3 contrasts AG5's pair
draw (seed [20261111, 5, 1], B = 10,000). AUC: positive class = first named.

## Sources

- A43: manifest `/mnt/t7/smad_heldout/a43/data/manifests/a43.csv` (sha ce3a264a…, asserted), 512 frames under
  `a43/data/a43/frames/` and `smadcvpr_data/eval/`; release scores `a43_out/a43/<net>/rel/scores_a43.npz`
  (`score_noTTA`; R0 rows equal the eval-file scores to ≤ 3e-8).
- R1 (E7), benchmarks, `frll_bona`: `smadcvpr_data/manifests/eval.csv` (sha 86d055d3…, asserted) and
  `smadcvpr_runs/A12_scored/A12REL/<net>/scores_eval.npz`. Old MAD22 rows not used.
- StyleGAN3: `h3_sg3/data/manifests/h3sg3.csv` (`orig`), `a37_sg3ctl/data/manifests/a37spread.csv` (`orig`);
  release scores `A12REL/<net>/scores_h3sg3.npz`, `a41g/a41g_out/x4/<net>/rel/scores_a37spread.npz`.
- SMDD (P3 training only): the 40,000 `source = smdd` rows of `smadcvpr_data/manifests/train.csv` (25,000 bona
  fide, 15,000 morphs, 256-px files).
- Weights: OpenAI CLIP ViT-L/14 from the local timm cache (`vit_large_patch14_clip_224.openai`,
  `pytorch_model.bin`, loaded with `weights_only=True`, OpenAI layout converted by timm's `checkpoint_filter_fn`
  into `vit_large_patch14_clip_quickgelu_224`); DINOv3 `vit_large_patch16_dinov3.lvd1689m` and DINOv2
  `vit_large_patch14_dinov2.lvd142m` (safetensors, local cache, offline). MADation FE release head from
  `/mnt/t7/wcss_backups/madation_official_upload/madation_official.tar` (`A12REL/madation_fe_vitl14`), extracted
  to the session scratchpad for reading only. MADation training code: `mambamorph-code/baselines/MADation/src`
  (same tree as in the release tar); the FE ViT-L/14 `training.log` (scratchpad `ext/madation_weights/vitl14_fe/`)
  confirms `MAD_training_only_header`, lr_header 0.01, wd 0.05, 40 epochs, batch 32, train set 39,730 images,
  6,207 steps (global batch 256).

## Deviations from the prereg

1. **Check (ii) missed its tolerance; CLIP rows were not stopped.** The released FE head applied to our CLIP
   features reproduces the stored A43 FE ViT-L/14 scores (72 images, 8 per arm) with max |Δ score| 2.6e-3 in fp32
   (4.7e-3 with TF32), above the pre-registered 2e-3; mean |Δ| 4.7e-4, max |Δ logit| 0.024 (mean |logit| 5.2),
   Pearson 0.999997. The encoder tensors equal the release's frozen encoder exactly (297 tensors, max |Δ| 0).
   Calibration control (same check with the channel order deliberately wrong, RGB instead of BGR): max |Δ score|
   0.98, mean 0.37, Pearson 0.42. The stored scores were computed on an H100 with TF32; I read the residual as
   cross-device arithmetic and continued. End-to-end check on all rows: see P3 ("release head on our features").
   The lead may treat the CLIP rows as conditional on this reading.
2. fp32 (TF32 off) for every feature, chosen after the check (the prereg allowed either).
3. Feature extraction for SMDD was done in one decode pass producing original and flipped features (no
   change to the numbers, only to run time).
4. DINOv3's timm pooled pre-logits are the mean of the patch tokens (`global_pool = avg`); DINOv2's are the CLS
   token. The prereg said "timm pooled pre-logits" without naming the pooling.
5. P4: 30 images per arm were used for the 8-image smoke test, because the nested CV cannot run on 8.

## P1: released MADation FE / FS re-read (post hoc; existing score files only)

**Reproduction: yes.** All six preview point AUCs recomputed to three decimals (B20 vs D20 0.655, B vs D 0.852,
C vs D 0.721, D vs R0 0.459, D20 vs R0 0.561, StyleGAN3 morph vs render 0.505). Intervals below use AD1's draw;
the two intervals quoted in the task differ by 0.001 (B20 vs D20 [0.580, 0.730], B vs D [0.798, 0.902]).
For reference (G-a style, not a gate here): the FE ViT-L/14 release's own `training.log`, epoch 39, on its own
crops, prints EER MorDIFF 22.9%, FRLL-Morphs AMSL 36.8%, FaceMorpher 9.6%, OpenCV 8.6%, WebMorph 35.1%; on our
frames the same network gives 34.8 / 21.6 / 3.9 / 4.4 / 9.8% (table below), so its benchmark numbers are not
reproduced within 3 points in our pipeline (descriptive).

| Contrast | FE ViT-L/14 | FE ViT-B/16 | FS ViT-L/14 | FS ViT-B/16 | full ViT-L/14 (reference) | full ViT-B/16 (reference) |
|---|---|---|---|---|---|---|
| B20 vs D20 | 0.655 [0.580, 0.730] | 0.532 [0.432, 0.626] | 0.584 [0.499, 0.670] | 0.502 [0.424, 0.581] | 0.486 [0.384, 0.588] | 0.480 [0.382, 0.578] |
| B vs D | 0.852 [0.798, 0.902] | 0.572 [0.479, 0.665] | 0.569 [0.481, 0.656] | 0.531 [0.451, 0.611] | 0.515 [0.417, 0.604] | 0.366 [0.277, 0.456] |
| C20 vs D20 | 0.498 [0.443, 0.552] | 0.493 [0.453, 0.533] | 0.546 [0.488, 0.604] | 0.489 [0.432, 0.548] | 0.444 [0.396, 0.492] | 0.266 [0.216, 0.315] |
| C vs D | 0.721 [0.673, 0.769] | 0.534 [0.488, 0.580] | 0.519 [0.460, 0.579] | 0.517 [0.465, 0.573] | 0.628 [0.578, 0.681] | 0.315 [0.265, 0.364] |
| B20 vs C20 | 0.653 [0.562, 0.741] | 0.544 [0.431, 0.649] | 0.541 [0.443, 0.644] | 0.514 [0.425, 0.603] | 0.541 [0.422, 0.652] | 0.706 [0.625, 0.785] |
| B vs C | 0.670 [0.582, 0.755] | 0.539 [0.426, 0.648] | 0.547 [0.454, 0.640] | 0.517 [0.422, 0.611] | 0.395 [0.289, 0.497] | 0.539 [0.443, 0.631] |
| D vs R0 | 0.459 [0.426, 0.492] | 0.706 [0.681, 0.735] | 0.470 [0.422, 0.517] | 0.333 [0.285, 0.380] | 0.742 [0.713, 0.776] | 0.896 [0.863, 0.927] |
| D20 vs R0 | 0.561 [0.528, 0.597] | 0.607 [0.577, 0.638] | 0.484 [0.433, 0.535] | 0.310 [0.260, 0.359] | 0.877 [0.848, 0.907] | 0.992 [0.982, 0.999] |
| E vs R0 | 0.380 [0.354, 0.402] | 0.690 [0.668, 0.717] | 0.502 [0.457, 0.547] | 0.303 [0.258, 0.348] | 0.625 [0.601, 0.652] | 0.856 [0.823, 0.889] |
| R1 vs R0 | 0.465 [0.448, 0.481] | 0.711 [0.689, 0.738] | 0.495 [0.466, 0.525] | 0.397 [0.365, 0.425] | 0.645 [0.616, 0.681] | 0.894 [0.863, 0.924] |
| A vs R0 | 0.703 [0.632, 0.772] | 0.640 [0.542, 0.733] | 0.617 [0.537, 0.696] | 0.249 [0.174, 0.333] | 0.825 [0.746, 0.896] | 0.986 [0.970, 0.997] |
| B20 vs R0 | 0.690 [0.617, 0.762] | 0.632 [0.530, 0.728] | 0.570 [0.485, 0.659] | 0.285 [0.205, 0.371] | 0.836 [0.759, 0.904] | 0.988 [0.974, 0.997] |
| B vs R0 | 0.806 [0.745, 0.864] | 0.757 [0.677, 0.833] | 0.540 [0.449, 0.631] | 0.356 [0.272, 0.445] | 0.742 [0.653, 0.820] | 0.782 [0.701, 0.855] |
| SG3 morph vs render | 0.505 [0.474, 0.536] | 0.514 [0.486, 0.541] | 0.540 [0.509, 0.572] | 0.511 [0.473, 0.549] | 0.427 [0.399, 0.455] | 0.554 [0.526, 0.582] |
| SG3 morph vs spread | 0.475 [0.445, 0.505] | 0.451 [0.424, 0.477] | 0.470 [0.440, 0.499] | 0.466 [0.429, 0.503] | 0.445 [0.417, 0.472] | 0.423 [0.395, 0.451] |
| flag rate R0 → R1 at own MorDIFF EER thr (pts) | 34.8% → 29.9% (-4.9 [-9.3, -0.5]) | 39.7% → 69.6% (+29.9 [+23.5, +36.3]) | 43.1% → 41.2% (-2.0 [-7.4, +3.4]) | 67.6% → 53.9% (-13.7 [-19.1, -8.8]) | 28.9% → 52.9% (+24.0 [+17.2, +31.4]) | 4.9% → 53.9% (+49.0 [+41.2, +56.9]) |
| same, threshold from the 200 sampled morphs | 35.8% → 30.9% (-4.9 [-9.3, -1.0]) | 40.2% → 70.6% (+30.4 [+24.0, +36.8]) | 42.2% → 40.2% (-2.0 [-7.4, +3.4]) | 69.6% → 53.9% (-15.7 [-21.6, -10.3]) | 26.0% → 51.0% (+25.0 [+18.1, +32.4]) | 5.4% → 53.9% (+48.5 [+40.7, +56.4]) |
| neutral above smiling, frll_bona | 0.343 [0.255, 0.431] | 0.088 [0.039, 0.147] | 0.500 [0.402, 0.598] | 0.539 [0.441, 0.637] | 0.990 [0.971, 1.000] | 0.578 [0.480, 0.676] |
| neutral above smiling, mordiff_bona_R0 | 0.206 [0.127, 0.284] | 0.098 [0.049, 0.157] | 0.520 [0.422, 0.618] | 0.657 [0.559, 0.745] | 0.794 [0.716, 0.873] | 0.529 [0.431, 0.627] |

| Benchmark EER % (native / E7) | FE ViT-L/14 | FE ViT-B/16 | FS ViT-L/14 | FS ViT-B/16 | full ViT-L/14 (reference) | full ViT-B/16 (reference) |
|---|---|---|---|---|---|---|
| FRLLM/amsl | 21.6 [16.7, 26.0] / 23.0 [18.1, 27.4] | 26.0 [22.0, 29.9] / 38.7 [33.0, 43.1] | 39.2 [34.9, 44.1] / 39.7 [35.3, 44.6] | 40.6 [35.7, 45.2] / 40.7 [36.3, 45.7] | 17.7 [13.7, 22.2] / 14.7 [10.7, 19.6] | 15.1 [10.4, 18.8] / 28.9 [23.2, 33.8] |
| FRLLM/facemorpher | 3.9 [2.0, 6.7] / 4.4 [2.0, 7.4] | 16.7 [12.3, 21.0] / 22.6 [17.7, 26.5] | 38.2 [32.8, 43.7] / 37.7 [32.5, 43.2] | 16.7 [10.6, 21.1] / 17.3 [11.9, 22.3] | 1.0 [0.1, 1.9] / 1.0 [0.1, 1.7] | 2.8 [0.9, 4.9] / 4.4 [2.1, 6.9] |
| FRLLM/opencv | 4.4 [2.0, 6.9] / 4.9 [2.0, 7.4] | 18.6 [13.7, 22.1] / 26.0 [20.1, 29.4] | 31.9 [27.0, 38.6] / 32.8 [27.5, 38.8] | 3.9 [1.8, 6.3] / 5.4 [3.0, 8.3] | 1.0 [0.1, 2.7] / 1.0 [0.1, 2.7] | 2.9 [1.0, 4.9] / 4.4 [2.1, 7.3] |
| FRLLM/webmorph | 9.8 [6.2, 12.8] / 10.3 [6.8, 13.2] | 22.5 [17.6, 27.4] / 31.9 [25.6, 38.5] | 32.9 [28.4, 38.1] / 32.8 [28.4, 37.8] | 32.1 [25.5, 38.2] / 34.8 [28.1, 39.7] | 4.9 [2.9, 7.8] / 4.4 [2.5, 7.4] | 4.9 [2.4, 8.2] / 10.8 [7.5, 14.7] |
| MorDIFF | 34.8 [29.9, 40.2] / 32.4 [27.1, 36.3] | 39.7 [33.9, 44.2] / 53.5 [48.6, 58.0] | 43.0 [37.4, 47.6] / 42.1 [37.3, 47.0] | 67.6 [63.2, 73.7] / 62.2 [57.0, 66.6] | 28.9 [22.2, 34.8] / 39.7 [32.8, 45.1] | 4.9 [2.9, 8.1] / 19.6 [15.0, 24.8] |

R1 = E7 copy of the R0 photo. Flag-rate change: same 204 photos, threshold fixed at the network's MorDIFF EER
threshold (full cell, 1,000 morphs), person bootstrap of the paired difference. Neutral above smiling: share of
the 102 persons whose neutral photo scores above their smiling photo (0.5 = no preference). Full releases are
reference rows (AD1 already reported them).

## P2: readability probe on frozen features (gate G-c; FRLL images = diagnostic of the images, not a detector)

AUC of pooled out-of-fold probabilities, fold seed 401 [95% person / pair bootstrap]; in brackets after it, the
range of point AUCs over fold seeds 401–405; then the fixed reading. clip_mad = OpenAI CLIP ViT-L/14 with the
MADation input (BGR, 0.5 / 0.5; primary for G-c), clip_native = same encoder with CLIP's own RGB mean / std.
n: B20 vs D20 and B vs D 200 vs 204; C20 vs D20 102 vs 204; B20 vs C20 200 vs 102; StyleGAN3 423 vs 423.

| Contrast | clip_mad | clip_native | dinov3 | dinov2 |
|---|---|---|---|---|
| B20 vs D20 | 0.987 [0.971, 0.997] (seeds 0.98–0.99); readable from frozen features | 0.997 [0.992, 1.000] (seeds 0.99–1.00); readable from frozen features | 0.998 [0.990, 1.000] (seeds 1.00–1.00); readable from frozen features | 1.000 [0.999, 1.000] (seeds 1.00–1.00); readable from frozen features |
| B vs D | 0.995 [0.988, 0.999] (seeds 0.99–1.00); readable from frozen features | 0.999 [0.997, 1.000] (seeds 1.00–1.00); readable from frozen features | 0.997 [0.993, 1.000] (seeds 1.00–1.00); readable from frozen features | 0.993 [0.974, 1.000] (seeds 0.99–1.00); readable from frozen features |
| C20 vs D20 | 0.991 [0.974, 1.000] (seeds 0.99–0.99); readable from frozen features | 0.996 [0.987, 1.000] (seeds 0.99–1.00); readable from frozen features | 0.999 [0.997, 1.000] (seeds 1.00–1.00); readable from frozen features | 1.000 [1.000, 1.000] (seeds 1.00–1.00); readable from frozen features |
| B20 vs C20 | 0.945 [0.908, 0.975] (seeds 0.94–0.96); readable from frozen features | 0.979 [0.955, 0.995] (seeds 0.97–0.99); readable from frozen features | 0.975 [0.951, 0.993] (seeds 0.97–0.99); readable from frozen features | 0.982 [0.966, 0.994] (seeds 0.98–0.99); readable from frozen features |
| morph vs render | 0.886 [0.868, 0.904] (seeds 0.87–0.89); readable from frozen features | 0.919 [0.903, 0.935] (seeds 0.91–0.92); readable from frozen features | 0.936 [0.923, 0.950] (seeds 0.93–0.94); readable from frozen features | 0.892 [0.873, 0.911] (seeds 0.89–0.91); readable from frozen features |
| morph vs spread | 0.615 [0.584, 0.645] (seeds 0.61–0.63); intermediate | 0.632 [0.603, 0.661] (seeds 0.63–0.64); intermediate | 0.617 [0.587, 0.648] (seeds 0.59–0.63); intermediate | 0.583 [0.551, 0.616] (seeds 0.56–0.58); not readable by this probe |

- Fixed readings applied: every A43 contrast, on all four feature sets, is "readable from frozen features"
  (AUC ≥ 0.945, lower bounds ≥ 0.908). StyleGAN3 morph vs one-identity render: readable on all four
  (0.886–0.936). StyleGAN3 morph vs spread-matched render: "intermediate" for both CLIP inputs and DINOv3
  (0.615–0.632), "not readable by this probe" for DINOv2 (0.583); all four are below the `11_AUDIT_PLAN.md`
  G-c bar of 0.65.
- G-b context: holds for A43 (AD1), fails for StyleGAN3 (48% of H3 morphs verify against both contributors).
- Chosen C (inner CV) per outer fold is in `p2_probe.json`; the A43 contrasts mostly chose C = 1 or 10, the
  StyleGAN3 contrasts mostly C = 0.001–0.01.
- Limitation fixed in the prereg: a test morph's second contributor can be in the training part (both classes).

## P4: simple-statistic floors (A43, B vs D and B20 vs D20)

Folded AUC = AUC oriented by its own point estimate (direction chosen from the data, so slightly optimistic);
"probe − stat" = paired bootstrap difference against the clip_mad P2 probe of the same contrast (same draw); the
fixed rule calls a statistic a match when that interval includes 0 or lies below it. view224 = the 224 loader
input the features see (primary); center256 = central 256 × 256 of the 512 frame, inside the photo for every
A43 file (descriptive). PNG size is the same file in both views.

**view224|B vs D**

| Statistic | folded AUC [95%] | direction | probe − stat [95%] | matches probe |
|---|---|---|---|---|
| hf_energy | 0.511 [0.448, 0.574] | morph higher | +0.484 [+0.420, +0.549] | False |
| laplacian_var | 0.548 [0.469, 0.621] | morph lower | +0.447 [+0.374, +0.524] | False |
| mirror_mad | 0.588 [0.506, 0.666] | morph lower | +0.407 [+0.329, +0.489] | False |
| std_R | 0.520 [0.444, 0.595] | morph lower | +0.475 [+0.399, +0.551] | False |
| std_G | 0.521 [0.442, 0.600] | morph lower | +0.474 [+0.395, +0.553] | False |
| std_B | 0.525 [0.447, 0.607] | morph lower | +0.470 [+0.388, +0.548] | False |
| png_bytes | 0.798 [0.723, 0.862] | morph higher | +0.197 [+0.132, +0.272] | False |
| logistic on all 7 (5-fold by person) | 0.849 [0.797, 0.895] | — | +0.146 [+0.099, +0.198] | False |

**view224|B20 vs D20**

| Statistic | folded AUC [95%] | direction | probe − stat [95%] | matches probe |
|---|---|---|---|---|
| hf_energy | 0.506 [0.438, 0.574] | morph lower | +0.482 [+0.412, +0.551] | False |
| laplacian_var | 0.573 [0.492, 0.649] | morph lower | +0.415 [+0.339, +0.495] | False |
| mirror_mad | 0.577 [0.498, 0.654] | morph lower | +0.410 [+0.332, +0.490] | False |
| std_R | 0.519 [0.442, 0.594] | morph lower | +0.468 [+0.392, +0.545] | False |
| std_G | 0.518 [0.438, 0.597] | morph lower | +0.469 [+0.389, +0.550] | False |
| std_B | 0.523 [0.445, 0.606] | morph lower | +0.464 [+0.381, +0.544] | False |
| png_bytes | 0.604 [0.515, 0.688] | morph higher | +0.383 [+0.296, +0.475] | False |
| logistic on all 7 (5-fold by person) | 0.633 [0.561, 0.701] | — | +0.355 [+0.283, +0.429] | False |

**center256|B vs D**

| Statistic | folded AUC [95%] | direction | probe − stat [95%] | matches probe |
|---|---|---|---|---|
| hf_energy | 0.596 [0.523, 0.670] | morph higher | +0.399 [+0.325, +0.471] | False |
| laplacian_var | 0.966 [0.940, 0.986] | morph higher | +0.029 [+0.007, +0.056] | False |
| mirror_mad | 0.520 [0.450, 0.591] | morph lower | +0.474 [+0.403, +0.545] | False |
| std_R | 0.547 [0.488, 0.607] | morph lower | +0.447 [+0.387, +0.507] | False |
| std_G | 0.549 [0.482, 0.618] | morph lower | +0.446 [+0.378, +0.512] | False |
| std_B | 0.535 [0.468, 0.606] | morph lower | +0.460 [+0.390, +0.526] | False |
| png_bytes | 0.798 [0.723, 0.862] | morph higher | +0.197 [+0.132, +0.272] | False |
| logistic on all 7 (5-fold by person) | 0.988 [0.976, 0.996] | — | +0.007 [-0.003, +0.019] | True |

**center256|B20 vs D20**

| Statistic | folded AUC [95%] | direction | probe − stat [95%] | matches probe |
|---|---|---|---|---|
| hf_energy | 0.537 [0.452, 0.618] | morph lower | +0.450 [+0.365, +0.538] | False |
| laplacian_var | 0.661 [0.569, 0.749] | morph higher | +0.326 [+0.238, +0.418] | False |
| mirror_mad | 0.558 [0.487, 0.627] | morph lower | +0.430 [+0.358, +0.503] | False |
| std_R | 0.557 [0.498, 0.617] | morph lower | +0.430 [+0.369, +0.491] | False |
| std_G | 0.557 [0.490, 0.626] | morph lower | +0.430 [+0.361, +0.499] | False |
| std_B | 0.550 [0.483, 0.620] | morph lower | +0.437 [+0.366, +0.506] | False |
| png_bytes | 0.604 [0.515, 0.688] | morph higher | +0.383 [+0.296, +0.475] | False |
| logistic on all 7 (5-fold by person) | 0.695 [0.616, 0.771] | — | +0.293 [+0.215, +0.371] | False |

- Fixed reading, primary view: **no single statistic and not the 7-statistic logistic matches the probe** for
  either contrast. Best single statistic: PNG size, 0.798 (B vs D) and 0.604 (B20 vs D20).
- Descriptive view (center 256): for B vs D, **Laplacian variance alone gives 0.966 [0.940, 0.986]** (morphs
  have the higher variance; probe − stat +0.029 [+0.007, +0.056], so not a match under the rule), and the
  7-statistic logistic gives 0.988, which matches the probe (+0.007 [−0.003, +0.019]). For B20 vs D20 the same
  statistics reach 0.661 (Laplacian) and 0.695 (logistic), far below the probe (0.987).
- Post hoc, descriptive (not pre-registered): Spearman correlation of the released FE ViT-L/14 score with the
  center-256 Laplacian variance is 0.41 over B ∪ D pooled, but −0.22 within B and −0.16 within D; over
  B20 ∪ D20 it is −0.14 (within −0.28 / −0.21).

PENDING
