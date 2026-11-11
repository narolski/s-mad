# FZ1 result: do frozen foundation features read the mixing step of a DiffAE morph?

Owner run, 11 Nov 2026. **Rewritten 11 Nov 20:28 CET** after the independent review
(`experiments/reviews/REVIEW_FZ1_20261111.md`, verdict "needs qualification") and the registered post hoc
addendum A1 (`prereg.md`, registered 20:22, before any addendum number). The pre-review text is kept at
`/mnt/t7/smad_next/FZ1/result_before_review_rewrite.md` and in git. Prereg written 15:26 CET before any new number
(P1 post hoc; P2–P4 new). Runs 15:30–20:08 CET, addendum 20:23–20:25 CET, DGX only. Code `src/FZ1/`; small results
here; caches, heads and logs in `/mnt/t7/smad_next/FZ1/`. Intervals: AD1's two-way person (pigeonhole) draw (seed
[20261107, 43, 1], B = 10,000; EERs B = 2,000; Spearman B = 2,000) or AG5's pair draw for StyleGAN3. AUC: positive
class = first named. All numbers are "in our pipeline" (our 512 frames).

## Verdict in corrected wording (review section 3, with the addendum numbers)

1. **Registered rule:** supported under the registered rule (100 steps, point estimates); not supported on the
   20-step rungs that match the published morphs; neither contrast isolates mixing. Five SMDD-only heads on frozen
   CLIP ViT-L/14 give B vs D 0.79 [0.73, 0.85] (every lower bound below 0.75) and D vs R0 0.51; on the 20-step rungs
   (AD1's primary contrast) they give 0.63 [0.55, 0.70], which the same rule would read as falsified (below 0.70 in
   every seed and every resample). The reconstruction is the only arm decoded from its own photo's noise map, in
   both contrasts. PNG size (0.80) and central-crop sharpness (0.97) separate B from D, but the heads use neither:
   inside each arm the head's correlation with PNG bytes is about 0 (−0.11 to +0.02) and with central-crop
   Laplacian variance negative (−0.27 to −0.38; sharper images score lower), and inside PNG-size fifths B vs D stays
   at 0.779 [0.702, 0.858].
2. **Probes:** probes trained on each contrast separate every diffusion arm (0.945–1.000; "the arms are linearly
   separable"). One direction is shared by same-person and two-person mixes against the reconstruction (trained on
   C20 vs D20 it gives B20 vs D20 0.946 [0.907, 0.976] and ranks C20 above B20, 0.108); a second direction separates
   two-person morphs from same-person mixes (0.945 [0.908, 0.975]; not expression: 0.939 neutral pairs, 0.950
   smiling pairs; on single photos smiling vs neutral 0.456 (D20) and 0.543 (E)). Partner leakage is negligible
   (partner in the test fold vs in training: 0.989 vs 0.987, 0.993 vs 0.995, 0.934 vs 0.948). We cannot yet tell
   mixing from "not rendered from its own noise map".
3. **StyleGAN3:** matching the renders' latent spread removes most of the separation (0.89–0.94 → 0.58–0.63; lower
   bounds 0.551–0.603, still above chance). No identity reading (gate G-b fails, 48%).
4. **SMDD heads vs the release:** the frozen-encoder release's ladder ordering is reproduced by our SMDD-only heads
   (Spearman 0.87–0.88 with the release). At 20 steps the ordering is weak: two-person over same-person mix 0.62
   [0.53, 0.71], same-person mix vs reconstruction 0.51 [0.46, 0.56], D20 vs R0 0.53, R1 vs R0 0.52 (the pattern a
   weak second-person reader would show). **Limits:** it does not exceed the simple-statistic floor (best single
   statistic for B20 vs C20 is left-right asymmetry, 0.681, B20 lower; head − best −0.060 [−0.194, +0.074]; the
   7-statistic logistic gives 0.677); C20 is the neutral+smiling mix (expression-confounded, with the known coloured
   spots of such DiffAE mixes); inside A43 a second person and the disagreement between the two inputs cannot be
   separated (minimum source cosine 0.485 for B20 vs 0.868 for C20, no overlap; review F3); the head does not track
   identity cosine inside an arm (review's point estimates ρ −0.07 to +0.01; not rerun here). Wording: "weak ordering consistent with a second person, not shown to be
   identity". **Storage history:** the frozen ViT-L/14 heads do not move with it (R0 → R1 flag change 0.0 to +1.5
   points, intervals include 0; E vs R0 0.455–0.458; release −4.9 points and 0.380). This is a ViT-L/14 result; the
   frozen-encoder ViT-B/16 release moves +29.9 points. **Detection:** they detect published MorDIFF poorly (EER
   40.2–40.7%; release 34.8% on the same frames).
5. **Benchmark numbers:** on our frames the release misses its own training log in both directions: MorDIFF 34.8%
   against 22.9%; the landmark families 6 to 25 points better than the log (AMSL 21.6 vs 36.8, FaceMorpher 3.9 vs 9.6,
   OpenCV 4.4 vs 8.6, WebMorph 9.8 vs 35.1). Benchmark rows wait for the own-crop re-score (RS1); ladder contrasts
   stand as "in our pipeline". The log's genuine sets are not in the release; the rate steps in the log are
   consistent with 204 genuine images for FaceMorpher, OpenCV and all-attacks, but with 206–207 for MorDIFF, AMSL and
   StyleGAN (and 102 or 204 for WebMorph), so the log's genuine set cannot be confirmed as ours (204 FRLL photos).

## WITHDRAWN (with reasons)

- **Any sentence that explains the 100-step separation (B vs D 0.79–0.85) by the published MorDIFF files, the step
  count, sharpness or storage.** B and D are both our renders, both 100 steps, both stored the same way; the
  published files enter neither arm; the heads use neither PNG size nor sharpness (within-arm correlations above;
  PNG-stratified AUC unchanged). This covers README section 8 of the first version ("points to a texture / noise
  difference …", "the release head's ordering follows the statistics' ordering") and the lead's draft conclusion 1.
- **"5 of 5 seeds" as strength of evidence.** The five seed heads are effectively one network (spread ≤ 0.004,
  training AUC 1.000). The count stays only as the registered rule's mechanics. SMDD-resampled heads show a spread of
  0.016 on B vs D (addendum (c)).
- **"Readable from frozen features" where it means "the arms are linearly separable".** The registered G-c label is
  kept in `p2_probe.json` for traceability; in text it reads "linearly separable". Separability says nothing about
  which property is read.

## Deviations from the prereg

1. **Check (ii) failed its registered tolerance and the stop rule was not applied; ratified by the lead after the
   fact on the review's evidence (finding F7).** The released FE head on our features vs the stored scores: max
   |Δ score| 2.6e-3 on 72 images in fp32 (4.7e-3 TF32; 9.2e-3 over all 2,024 rows), above the registered 2e-3; mean
   4.6e-4; encoder tensors identical bit for bit (297); largest logit difference 0.024 against mean |logit| 5.2;
   Pearson 0.999997; wrong-channel control 0.98; every AUC within 2.7e-4 of the release and EERs within 0.07 points.
   The tolerance was ill-posed (a maximum in probability units over 8 images per arm); future registrations use a
   rank or AUC tolerance. The DINO rows, which need no check, give the same P2 readings.
2. fp32 for every evaluation feature (A43, StyleGAN3, eval set); the SMDD training features (P3 only) were extracted
   with TF32 for throughput (allowed by the prereg). P3 heads are labelled "our SMDD re-trains" (40,000 SMDD images
   against MADation's 39,730; weaker than the release: B vs D 0.79 vs 0.852).
3. SMDD features: one decode pass for original and flipped features; extracted as two parallel halves and merged
   with an id-order check (no effect on numbers).
4. DINOv3's timm pooled pre-logits are the mean of the patch tokens (`global_pool = avg`); DINOv2's are the CLS
   token.
5. P4 smoke used 30 images per arm (the nested CV cannot run on 8).
6. The hypothesis's third clause ("adapting the encoder replaces this with processing cues") was not tested: there
   is no adapted retrain in this experiment.

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


## P2: probes on frozen features (gate G-c; FRLL images = diagnostic of the images, not a detector)

AUC of pooled out-of-fold probabilities, fold seed 401 [95% person / pair bootstrap]; in brackets after it, the
range of point AUCs over fold seeds 401–405; then the fixed reading. clip_mad = OpenAI CLIP ViT-L/14 with the
MADation input (BGR, 0.5 / 0.5; primary for G-c), clip_native = same encoder with CLIP's own RGB mean / std.
n: B20 vs D20 and B vs D 200 vs 204; C20 vs D20 102 vs 204; B20 vs C20 200 vs 102; StyleGAN3 423 vs 423.

| Contrast | clip_mad | clip_native | dinov3 | dinov2 |
|---|---|---|---|---|
| B20 vs D20 | 0.987 [0.971, 0.997] (seeds 0.98–0.99); separable | 0.997 [0.992, 1.000] (seeds 0.99–1.00); separable | 0.998 [0.990, 1.000] (seeds 1.00–1.00); separable | 1.000 [0.999, 1.000] (seeds 1.00–1.00); separable |
| B vs D | 0.995 [0.988, 0.999] (seeds 0.99–1.00); separable | 0.999 [0.997, 1.000] (seeds 1.00–1.00); separable | 0.997 [0.993, 1.000] (seeds 1.00–1.00); separable | 0.993 [0.974, 1.000] (seeds 0.99–1.00); separable |
| C20 vs D20 | 0.991 [0.974, 1.000] (seeds 0.99–0.99); separable | 0.996 [0.987, 1.000] (seeds 0.99–1.00); separable | 0.999 [0.997, 1.000] (seeds 1.00–1.00); separable | 1.000 [1.000, 1.000] (seeds 1.00–1.00); separable |
| B20 vs C20 | 0.945 [0.908, 0.975] (seeds 0.94–0.96); separable | 0.979 [0.955, 0.995] (seeds 0.97–0.99); separable | 0.975 [0.951, 0.993] (seeds 0.97–0.99); separable | 0.982 [0.966, 0.994] (seeds 0.98–0.99); separable |
| morph vs render | 0.886 [0.868, 0.904] (seeds 0.87–0.89); separable | 0.919 [0.903, 0.935] (seeds 0.91–0.92); separable | 0.936 [0.923, 0.950] (seeds 0.93–0.94); separable | 0.892 [0.873, 0.911] (seeds 0.89–0.91); separable |
| morph vs spread | 0.615 [0.584, 0.645] (seeds 0.61–0.63); intermediate | 0.632 [0.603, 0.661] (seeds 0.63–0.64); intermediate | 0.617 [0.587, 0.648] (seeds 0.59–0.63); intermediate | 0.583 [0.551, 0.616] (seeds 0.56–0.58); not separable by this probe |

- Fixed readings applied (the registered label "readable from frozen features" is replaced by "the arms are
  linearly separable"; see WITHDRAWN): every A43 contrast, on all four feature sets, is linearly separable
  (AUC ≥ 0.945, lower bounds ≥ 0.908). StyleGAN3 morph vs one-identity render: separable on all four
  (0.886–0.936). StyleGAN3 morph vs spread-matched render: "intermediate" for both CLIP inputs and DINOv3
  (0.615–0.632), "not separable by this probe" for DINOv2 (0.583); all four are below the `11_AUDIT_PLAN.md`
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


## P3: five SMDD-only heads on frozen CLIP-L/14 (our re-trains of the MADation FE recipe), the H-new-3 test

Recipe as registered (release code and FE ViT-L/14 `training.log`): Linear(768, 2) on L2-normalised projected
CLIP embedding, BCE on one-hot targets, AdamW lr 0.01 (constant under the release's scheduler; printed per epoch),
wd 0.05, 40 epochs, batch 256, drop_last (156 steps per epoch), gradient clip 5, horizontal flip p 0.5; trained on
the 40,000 SMDD images only; last epoch; score = softmax probability of the attack class. Columns = seeds.

**End-to-end check first (released FE head on our features, all rows):** A43 max |Δ score| 9.2e-3, mean 4.6e-4
over 2,024 images; every A43 and StyleGAN3 contrast AUC within 2.7e-4 of the stored release value; benchmark EERs
within 0.07 points (`p3_heads.json` → `_release_head_on_our_features`).

| Contrast | 401 | 402 | 403 | 404 | 405 |
|---|---|---|---|---|---|
| B20 vs D20 | 0.626 [0.555, 0.698] | 0.628 [0.556, 0.700] | 0.626 [0.555, 0.698] | 0.626 [0.554, 0.698] | 0.626 [0.554, 0.698] |
| B vs D | 0.789 [0.725, 0.850] | 0.792 [0.728, 0.853] | 0.790 [0.726, 0.851] | 0.792 [0.728, 0.853] | 0.791 [0.726, 0.852] |
| C20 vs D20 | 0.511 [0.464, 0.559] | 0.512 [0.464, 0.560] | 0.512 [0.465, 0.561] | 0.510 [0.462, 0.558] | 0.514 [0.466, 0.562] |
| C vs D | 0.667 [0.617, 0.717] | 0.670 [0.619, 0.720] | 0.671 [0.620, 0.721] | 0.668 [0.618, 0.718] | 0.670 [0.621, 0.720] |
| B20 vs C20 | 0.621 [0.527, 0.711] | 0.621 [0.527, 0.712] | 0.620 [0.525, 0.710] | 0.622 [0.527, 0.712] | 0.618 [0.523, 0.707] |
| B vs C | 0.656 [0.558, 0.750] | 0.657 [0.558, 0.751] | 0.655 [0.557, 0.749] | 0.657 [0.559, 0.752] | 0.654 [0.555, 0.748] |
| D vs R0 | 0.512 [0.483, 0.542] | 0.511 [0.481, 0.540] | 0.510 [0.481, 0.540] | 0.508 [0.479, 0.538] | 0.510 [0.481, 0.539] |
| D20 vs R0 | 0.535 [0.504, 0.567] | 0.535 [0.504, 0.568] | 0.533 [0.502, 0.565] | 0.530 [0.499, 0.563] | 0.531 [0.501, 0.564] |
| E vs R0 | 0.458 [0.435, 0.480] | 0.456 [0.432, 0.478] | 0.457 [0.433, 0.479] | 0.455 [0.431, 0.476] | 0.455 [0.431, 0.477] |
| R1 vs R0 | 0.523 [0.506, 0.540] | 0.522 [0.505, 0.539] | 0.522 [0.505, 0.539] | 0.520 [0.504, 0.537] | 0.522 [0.506, 0.539] |
| A vs R0 | 0.649 [0.572, 0.727] | 0.650 [0.573, 0.728] | 0.647 [0.570, 0.725] | 0.644 [0.567, 0.721] | 0.645 [0.568, 0.723] |
| B20 vs R0 | 0.656 [0.578, 0.733] | 0.658 [0.579, 0.735] | 0.655 [0.577, 0.732] | 0.652 [0.573, 0.729] | 0.653 [0.575, 0.730] |
| B vs R0 | 0.796 [0.728, 0.860] | 0.798 [0.729, 0.861] | 0.796 [0.728, 0.860] | 0.795 [0.726, 0.859] | 0.795 [0.727, 0.859] |
| SG3 morph vs render | 0.502 [0.471, 0.533] | 0.503 [0.472, 0.534] | 0.503 [0.472, 0.534] | 0.501 [0.470, 0.533] | 0.503 [0.472, 0.534] |
| SG3 morph vs spread | 0.480 [0.451, 0.509] | 0.480 [0.451, 0.509] | 0.480 [0.450, 0.509] | 0.480 [0.451, 0.510] | 0.479 [0.450, 0.509] |
| flag rate R0 → R1 at own MorDIFF EER thr (pts) | 40.7% → 40.7% (+0.0 [-4.9, +4.9]) | 40.2% → 41.7% (+1.5 [-2.9, +5.9]) | 40.7% → 40.7% (+0.0 [-4.9, +4.9]) | 40.7% → 41.2% (+0.5 [-3.9, +4.9]) | 40.7% → 42.2% (+1.5 [-2.9, +5.9]) |
| same, threshold from the 200 sampled morphs | 41.2% → 42.6% (+1.5 [-2.9, +5.9]) | 40.7% → 42.6% (+2.0 [-2.5, +6.4]) | 41.2% → 42.6% (+1.5 [-2.9, +5.9]) | 41.7% → 42.2% (+0.5 [-4.4, +5.4]) | 41.7% → 44.1% (+2.5 [-2.5, +7.4]) |
| neutral above smiling, frll_bona | 0.598 [0.500, 0.686] | 0.588 [0.490, 0.676] | 0.608 [0.510, 0.696] | 0.588 [0.490, 0.676] | 0.588 [0.490, 0.676] |
| neutral above smiling, mordiff_bona_R0 | 0.441 [0.343, 0.539] | 0.441 [0.343, 0.539] | 0.451 [0.353, 0.549] | 0.422 [0.324, 0.520] | 0.431 [0.333, 0.529] |

| Benchmark EER % (native / E7) | 401 | 402 | 403 | 404 | 405 |
|---|---|---|---|---|---|
| FRLLM/amsl | 22.5 [17.7, 28.4] / 28.4 [23.1, 33.6] | 22.6 [17.7, 28.2] / 28.4 [23.1, 33.3] | 23.0 [17.7, 28.0] / 28.0 [23.1, 33.3] | 22.5 [17.7, 28.3] / 28.4 [23.1, 33.4] | 23.5 [17.9, 28.5] / 28.4 [23.5, 33.9] |
| FRLLM/facemorpher | 4.4 [1.9, 6.8] / 5.4 [2.5, 8.3] | 4.4 [1.8, 6.8] / 5.3 [2.5, 8.3] | 4.4 [1.7, 6.4] / 4.9 [2.4, 8.2] | 4.4 [1.9, 6.8] / 5.4 [2.5, 8.3] | 4.4 [1.9, 6.9] / 5.4 [2.5, 8.4] |
| FRLLM/opencv | 4.8 [2.4, 7.9] / 6.4 [3.0, 9.5] | 4.9 [2.3, 7.8] / 6.4 [3.0, 9.4] | 4.8 [2.2, 7.7] / 5.9 [3.0, 9.2] | 4.9 [2.3, 7.8] / 6.4 [3.0, 9.6] | 4.9 [2.4, 8.0] / 6.4 [3.1, 9.7] |
| FRLLM/webmorph | 7.9 [4.7, 11.3] / 11.3 [7.8, 15.7] | 7.9 [4.7, 11.3] / 11.8 [7.9, 15.7] | 8.3 [4.5, 11.3] / 11.3 [7.8, 15.7] | 8.3 [4.7, 11.3] / 11.8 [7.9, 15.7] | 7.9 [4.8, 11.3] / 12.3 [8.0, 16.1] |
| MorDIFF | 40.7 [35.4, 45.2] / 40.7 [35.8, 45.5] | 40.2 [35.3, 45.1] / 40.7 [35.8, 45.1] | 40.7 [35.8, 45.5] / 40.7 [36.1, 45.3] | 40.6 [35.8, 45.6] / 40.7 [36.3, 45.5] | 40.7 [35.8, 45.4] / 41.2 [36.3, 45.6] |

| | 401 | 402 | 403 | 404 | 405 |
|---|---|---|---|---|---|
| train AUC (SMDD) | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| Spearman vs released FE ViT-L/14 (A43 rows) | 0.876 | 0.879 | 0.874 | 0.877 | 0.877 |

**Prediction / falsifier (fixed in the prereg), per seed:**

| Seed | B vs D | D vs R0 | B vs D ≥ 0.75 and D vs R0 ≤ 0.60 | B vs D ≥ 0.70 |
|---|---|---|---|---|
| 401 | 0.789 [0.725, 0.850] | 0.512 [0.483, 0.542] | yes | yes |
| 402 | 0.792 [0.728, 0.853] | 0.511 [0.481, 0.540] | yes | yes |
| 403 | 0.790 [0.726, 0.851] | 0.510 [0.481, 0.540] | yes | yes |
| 404 | 0.792 [0.728, 0.853] | 0.508 [0.479, 0.538] | yes | yes |
| 405 | 0.791 [0.726, 0.852] | 0.510 [0.481, 0.539] | yes | yes |

- Fixed reading applied: the prediction is met (registered count 5 of 5 seeds, ≥ 4 required) → **"supported"
  under the registered rule (100 steps, point estimates)**; falsifier not met. Every lower bound (0.725–0.728) is
  below 0.75, and the five seeds are effectively one network (spread ≤ 0.004, training AUC 1.000), so the count
  carries no more evidence than one head (addendum A1 (c) replaces seeds by SMDD resamples).
- Same heads, descriptive: B20 vs D20 0.626–0.628; C vs D 0.667–0.671; C20 vs D20 0.510–0.514; B20 vs C20
  0.618–0.622; E vs R0 0.455–0.458; R1 vs R0 0.520–0.523; StyleGAN3 morph vs render 0.501–0.503, vs spread
  0.479–0.480. R0 → R1 flag change 0.0 to +1.5 points (intervals include 0). Neutral above smiling 0.588–0.608
  (FRLL-Morphs genuine). MorDIFF EER 40.2–40.7% native and 40.7–41.2% E7 (released FE head on the same frames:
  34.8 / 32.4); FRLL-Morphs landmark EERs close to the release's (e.g. FaceMorpher 4.4 vs 3.9, WebMorph 7.9–8.3
  vs 9.8).
- The five heads are nearly identical (all AUCs within 0.004 across seeds); Spearman correlation with the
  released FE ViT-L/14 scores on the A43 rows 0.874–0.879. SMDD training AUC 1.000 for every seed (final
  training loss 0.0085–0.0087).


## Post hoc addendum A1 (registered 20:22 CET; reviewer checks with intervals; zero GPU)

Files: `addendum_a1.json`, `addendum_heads_boot.json`; code `src/FZ1/fz1_addendum.py`, `src/FZ1/fz1_heads_boot.py`;
logs `/mnt/t7/smad_next/FZ1/logs/addendum_*.log`. Post hoc: the reviewer had printed most point estimates first.

**(a1) Head (seed 401) against PNG bytes and central-crop sharpness inside each arm** (Spearman, person bootstrap;
the other four seeds within ±0.01):

| Arm | ρ(head, PNG bytes) | ρ(head, centre-256 Laplacian variance) |
|---|---|---|
| B | +0.018 [-0.273, +0.293] | -0.265 [-0.493, +0.008] |
| D | -0.068 [-0.223, +0.087] | -0.349 [-0.486, -0.198] |
| B20 | -0.017 [-0.308, +0.265] | -0.338 [-0.567, -0.038] |
| D20 | -0.112 [-0.269, +0.041] | -0.382 [-0.522, -0.218] |

**(a2) PNG-size-stratified AUC (pooled fifths):** B vs D overall 0.789, within fifths
0.779 [0.702, 0.858] (PNG bytes alone 0.798); B20 vs D20 overall
0.626, within fifths 0.632 [0.551, 0.714] (PNG bytes alone 0.604).

**(a3) Partner split, clip_mad P2 probe (fold seed 401):**
B20 vs D20: partner in the test fold (n = 47) 0.989 [0.968, 0.999], partner in training (n = 153) 0.987 [0.967, 0.998];
B vs D: 0.993 [0.980, 1.000] vs 0.995 [0.988, 1.000];
B20 vs C20: 0.934 [0.877, 0.979] vs 0.948 [0.911, 0.977]
(differences +0.002, -0.002, -0.014; intervals in the json).

**(a4) Transfer matrix** (registered P2 routine with inner-CV C, FZ1 folds seed 401; each test image scored by the
model of its host's fold; diagonal = P2 values):

| Probe trained on | B20 vs D20 | C20 vs D20 | B20 vs C20 | B vs D | C vs D | B vs C | E vs D20 | E vs D |
|---|---|---|---|---|---|---|---|---|
| clip_mad, B20 vs D20 | 0.987 [0.971, 0.997] | 0.984 [0.970, 0.995] | 0.410 [0.331, 0.491] | 0.936 [0.904, 0.963] | 0.918 [0.888, 0.946] | 0.475 [0.401, 0.551] | 0.594 [0.561, 0.628] | 0.165 [0.129, 0.199] |
| clip_mad, C20 vs D20 | 0.946 [0.907, 0.976] | 0.991 [0.974, 1.000] | 0.108 [0.063, 0.160] | 0.902 [0.859, 0.938] | 0.992 [0.983, 0.999] | 0.085 [0.048, 0.124] | 0.586 [0.555, 0.620] | 0.263 [0.225, 0.299] |
| clip_mad, B20 vs C20 | 0.540 [0.468, 0.615] | 0.087 [0.054, 0.120] | 0.945 [0.908, 0.975] | 0.491 [0.421, 0.563] | 0.078 [0.048, 0.107] | 0.941 [0.903, 0.973] | 0.330 [0.293, 0.361] | 0.425 [0.398, 0.449] |
| clip_mad, B vs D | 0.898 [0.844, 0.941] | 0.920 [0.884, 0.952] | 0.356 [0.278, 0.437] | 0.995 [0.988, 0.999] | 0.995 [0.990, 0.999] | 0.464 [0.382, 0.543] | 0.518 [0.487, 0.550] | 0.459 [0.427, 0.490] |
| clip_mad, C vs D | 0.790 [0.713, 0.859] | 0.974 [0.950, 0.991] | 0.119 [0.073, 0.172] | 0.978 [0.958, 0.992] | 0.999 [0.998, 1.000] | 0.124 [0.077, 0.176] | 0.459 [0.424, 0.492] | 0.455 [0.419, 0.488] |
| dinov2, B20 vs D20 | 1.000 [0.999, 1.000] | 1.000 [1.000, 1.000] | 0.323 [0.241, 0.408] | 0.800 [0.735, 0.857] | 0.918 [0.894, 0.942] | 0.318 [0.241, 0.399] | 0.736 [0.701, 0.774] | 0.040 [0.020, 0.065] |
| dinov2, C20 vs D20 | 0.978 [0.957, 0.993] | 1.000 [1.000, 1.000] | 0.143 [0.093, 0.200] | 0.818 [0.759, 0.870] | 0.962 [0.947, 0.977] | 0.157 [0.106, 0.214] | 0.633 [0.605, 0.667] | 0.160 [0.131, 0.186] |
| dinov2, B20 vs C20 | 0.421 [0.351, 0.492] | 0.014 [0.005, 0.025] | 0.982 [0.966, 0.994] | 0.406 [0.338, 0.476] | 0.016 [0.006, 0.029] | 0.981 [0.964, 0.994] | 0.620 [0.589, 0.654] | 0.646 [0.624, 0.671] |
| dinov2, B vs D | 0.918 [0.857, 0.962] | 0.983 [0.967, 0.995] | 0.216 [0.152, 0.281] | 0.993 [0.974, 1.000] | 0.999 [0.998, 1.000] | 0.257 [0.186, 0.330] | 0.649 [0.617, 0.684] | 0.450 [0.418, 0.481] |
| dinov2, C vs D | 0.843 [0.776, 0.900] | 0.987 [0.975, 0.997] | 0.063 [0.030, 0.100] | 0.921 [0.873, 0.959] | 0.998 [0.995, 1.000] | 0.040 [0.016, 0.069] | 0.546 [0.518, 0.576] | 0.399 [0.365, 0.429] |

**(a5) Expression split.** Heads:

| Contrast | head s401 [95%] (5-seed range) | n |
|---|---|---|
| B20[03] vs C20 | 0.648 [0.538, 0.757] (0.644–0.649) | 100 / 102 |
| B20[08] vs C20 | 0.594 [0.488, 0.697] (0.591–0.595) | 100 / 102 |
| B[03] vs C | 0.730 [0.621, 0.834] (0.727–0.733) | 100 / 102 |
| B[08] vs C | 0.582 [0.462, 0.698] (0.580–0.583) | 100 / 102 |
| C20 vs D20[03] | 0.495 [0.446, 0.544] (0.495–0.499) | 102 / 102 |
| C20 vs D20[08] | 0.528 [0.474, 0.582] (0.525–0.529) | 102 / 102 |
| C vs D[03] | 0.632 [0.576, 0.688] (0.632–0.637) | 102 / 102 |
| C vs D[08] | 0.701 [0.648, 0.754] (0.701–0.706) | 102 / 102 |
| D20[03] vs D20[08] | 0.530 [0.493, 0.569] (0.527–0.531) | 102 / 102 |
| D[03] vs D[08] | 0.566 [0.525, 0.609] (0.564–0.567) | 102 / 102 |

clip_mad B20-vs-C20 probe direction: B20 neutral pairs vs C20 0.939 [0.893, 0.975]; smiling pairs vs C20
0.950 [0.914, 0.980]; D20 smiling vs neutral 0.456 [0.420, 0.491]; E smiling vs neutral 0.543 [0.505, 0.582].

**(b) Floors for the side contrasts** (seven P4 statistics; C and C20 statistics computed now,
`/mnt/t7/smad_next/FZ1/addendum_a1_stats_CC20.npz`; best statistic chosen from the data, so the floor is slightly
optimistic). Registered reading: the head exceeds the floor only if head − best lies above 0.

| Contrast | head s401 | best single statistic, view224 (folded) | head − best [95%] | 7-statistic logistic view224 | centre-256: best single; logistic | clip_mad probe |
|---|---|---|---|---|---|---|
| B20 vs C20 | 0.621 [0.527, 0.711] | mirror_mad 0.681 [0.590, 0.767] (B20 lower) | -0.060 [-0.194, +0.074] | 0.677 [0.603, 0.750] | laplacian_var 0.738; 0.793 | 0.945 [0.908, 0.975] |
| C20 vs D20 | 0.511 [0.464, 0.559] | png_bytes 0.736 [0.687, 0.785] (C20 higher) | -0.225 [-0.287, -0.165] | 0.739 [0.689, 0.790] | laplacian_var 0.840; 0.887 | 0.991 [0.974, 1.000] |
| B vs C | 0.656 [0.558, 0.750] | mirror_mad 0.706 [0.622, 0.785] (B lower) | -0.050 [-0.186, +0.084] | 0.727 [0.657, 0.793] | mirror_mad 0.749; 0.800 | — |
| C vs D | 0.667 [0.617, 0.717] | png_bytes 0.824 [0.780, 0.867] (C higher) | -0.158 [-0.219, -0.097] | 0.827 [0.782, 0.870] | laplacian_var 0.984; 0.991 | — |

Reading: the head does not exceed the floor in any of the four contrasts (B20 vs C20 and B vs C: interval includes 0;
C20 vs D20 and C vs D: the head is below the floor). The clip_mad probes exceed their floors (probe − best: B20 vs C20
+0.263 [+0.177, +0.355]; C20 vs D20 +0.255 [+0.203, +0.306]).

**(c) Five SMDD-bootstrap heads** (resample seeds 401–405, about 25,300 unique images each, initialisation seed 401):

| Contrast | 5 SMDD-resample heads (range of points) | 5 seed heads (P3) |
|---|---|---|
| B vs D | 0.782–0.798 | 0.789–0.792 |
| B20 vs D20 | 0.616–0.634 | 0.626–0.628 |
| B20 vs C20 | 0.619–0.627 | 0.618–0.622 |
| C20 vs D20 | 0.494–0.520 | 0.510–0.514 |
| C vs D | 0.650–0.678 | 0.667–0.671 |
| D vs R0 | 0.499–0.519 | 0.508–0.512 |
| D20 vs R0 | 0.522–0.539 | 0.530–0.535 |
| E vs R0 | 0.442–0.463 | 0.455–0.458 |
| R1 vs R0 | 0.509–0.528 | 0.520–0.523 |
| R0 → R1 flag change (points) | -0.5 to +2.0 | 0.0 to +1.5 |
| MorDIFF EER native (%) | 40.2–43.6 | 40.2–40.7 |
| Spearman with released FE head (A43) | 0.867–0.881 | 0.874–0.879 |

B vs D per resample: 0.782 [0.718, 0.845], 0.798 [0.733, 0.859], 0.789 [0.724, 0.851], 0.786 [0.722, 0.846], 0.798 [0.734, 0.857]. The registered rule, applied
descriptively to the resamples, is met by all five; no lower bound reaches 0.75.

## What could not be verified

- That our SMDD files equal MADation's `smdd_train_cropped.csv` (39,730 vs 40,000 images; crops not compared).
- The release's genuine test sets (not in the release; see verdict 5).
- Whether the frozen-feature separation on A43 is identity mixing or "not decoded from its own noise map" or a
  run-to-run difference between separately rendered arms (to be tested on the new diffusion ladder, FZ2).
- StyleGAN3 cells carry no identity reading (G-b fails).
- Second person vs input disagreement in the B20 vs C20 ordering (inseparable in A43).
