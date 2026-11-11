# Signal isolation by paired differences (PD1), GAN latent morphs: result

Owner run, 11 Nov 2026, 17:00 to 19:30 CET. Pre-registration: `prereg.md` (written before any number below).
Code `src/PD1/gan/` (`pd1_manifest.py`, `pd1_feats.py`, `pd1_stats.py`, `pd1_first.py`, `pd1_analysis.py`,
`pd1_summary.py`); large files `/mnt/t7/smad_next/PD1/gan/` (features, statistics, manifest, byte copies,
out-of-fold scores). Tables in this folder: `q1_directions.csv`, `q2_cosines.csv`, `q3_heads.csv`,
`q3_flag_rates.csv`, `q4_trace_subtraction.csv`, `q5_dissimilarity.csv`, `benchmarks.csv`, `summary.json`;
full numbers in `res_<backbone>_<feature>.json`.

Abbreviations: AUC = area under the ROC curve (0.5 = chance); CI = 95% cluster-bootstrap interval (blocks for
set G, pairs for set H, FRLL persons for benchmark cells; B = 10,000 / 10,000 / 2,000); CP = exact
Clopper-Pearson interval; OOF = out-of-fold (5 folds by block, seed 401); W+ = StyleGAN latent code; FR = face
recognition; E7 = the approved shrink-and-enlarge history control.

Rungs: camera photo (x0); one-photo reconstruction, the pass-through (x1); same-person mix of two photos of
one person (x2); two-person morph (x3); spread-matched one-identity render (x1s, set H only: a render of the
host whose latent was moved to the morph's distance from the latent mean). Mirror self-morphs do not exist for
this family.

## Data actually used

- **Set G** (GAN32, StyleGAN3-T FFHQ-1024 inversions of FERET and FRGC photos): 64 blocks, 128 persons (none in
  two blocks), 256 hosts; 256 x0, 256 x1, 128 x2, 128 x3 (raw 1024 renders, sha256 checked against the
  generation records; camera photos copied byte-for-byte out of volatile `/tmp/opencode` into
  `/mnt/t7/smad_next/PD1/gan/anchors`, 256 of 256 sha256 equal to the generation `SOURCES.json`).
- **Set H** (H3 + A37, StyleGAN3-T on CASIA-WebFace): 423 pairs; x1 = H3 render of the shown contributor (one of
  the two contributors of the morph: A in 202, B in 221 pairs), x1s = A37 spread-matched render, x3 = H3
  morph. Raw 1024 frame (primary; H3 raw PNGs copied byte-for-byte out of the 12 generation tars, tar sha256
  checked) and the aligned eval frame (descriptive).
- **Set S** (softening): 2,000 SMDD genuine renders with their existing E7 copies (morph-free networks data,
  `a47/data47/i3`); 1,000 fit the softening direction, 1,000 held out.
- **Set F** (softened genuine photos, scoring only): 204 FRLL photos, corrected MAD22 canonical frame, native
  vs E7 copies with the FaceMorpher history (primary; 204 of 204 differ from native), OpenCV (96 differ) and
  Webmorph (100 differ); FRLL-Morphs eval frame, native vs `resmatch` of AMSL, FaceMorpher, OpenCV, Webmorph
  (204 each).
- **Benchmark cells**: FRLL-Morphs StyleGAN (1,222 morphs; its history-matched genuine copies are
  byte-identical to native for 204 of 204 photos), corrected MAD22 MIPGAN-I (1,000) and MIPGAN-II (999; E7
  copies byte-identical to native for 204 of 204), genuine = the 204 native FRLL photos.
- **Not used**: MIPGAN one-person controls (AG1): only 7 local smoke images (FRLL persons), incomplete. No
  image was generated.
- **Features** (frozen, existing loader at 224 px, TF32 on): CLIP ViT-L/14 pooled (primary) and CLIP mean
  patch token; DINOv3 ViT-L/16 pooled. The registered "DINOv3 mean patch token" turned out to be **identical**
  to "DINOv3 pooled" (timm's DINOv3 pools by averaging patch tokens; max |difference| 0.0), so DINOv3 is one
  feature here. Check against the cache of frozen features read mixing (FZ1): our CLIP pooled on the 1,269
  aligned H images differs from `FZ1/feats/clip_native/sg3.npz` by at most 0.32% (relative L2; TF32 and batch
  effects).

## What the earlier GAN heads of the Codex loop did, and what this adds

The folders `gan-native-heads-v1`, `gan32-frozen-v1` and `multigenerator-dro-v1` have no README; I read their
`INTENT`, `RESULT`, `TRAINING_AUDIT`, `LINEAGE_AUDIT` and `VERIFICATION` files. They trained 135 (and 150, 10)
small heads on frozen CLIP features of the first 32 GAN32 blocks only, with **16 training blocks**, positives
always two-person morphs (against reconstructions, same-person mixes or both), diagnostics on 8 + 8 reused
blocks: reconstructions separated at 0.73 to 0.78 on FERET, no transfer to DiffAE (0.26 to 0.32). New here:
all 64 blocks (4 times the training blocks); a within-host paired loss; a head trained on **one-person images
only**; camera photos as a rung; step directions and their geometry; the softening direction and the flag rate
on softened genuine photos; image-statistic floors; the latent-averageness statistic; and the spread-matched
reference in the same raw frame as the training renders.

## First small end-to-end pass (17:40 CET; CLIP pooled, fold 0 held out, point estimates)

13 held-out blocks (52 hosts). Q1 shares: pipeline 1.00, same-person mixing 0.79, second identity 0.63, whole
morph 0.73. One-person head: x3 vs x1 0.78, x3 vs x0 0.83, x3 vs x2 0.58; two-person head: 0.77, 0.84, 0.65
(`first_pass_clip_pool_fold0.json`). The full run below supersedes these.

## Q1 Direction consistency (held-out hosts; "consistent" = share ≥ 0.75 and lower bound > 0.65)

Share of held-out hosts whose paired difference moves along the training-fold mean direction [CI]; projection
AUC in `q1_directions.csv`.

| Step | CLIP pooled | CLIP mean patch | DINOv3 pooled | Consistent |
|---|---|---|---|---|
| G pipeline x0 → x1 | 1.00 [1.00, 1.00] | 1.00 | 1.00 | yes (all) |
| G same-person mixing x1 → x2 | 0.76 [0.70, 0.81] | 0.87 [0.82, 0.91] | 0.79 [0.75, 0.83] | yes (all) |
| G second identity x2 → x3 | 0.68 [0.62, 0.75] | 0.73 [0.68, 0.79] | 0.65 [0.60, 0.71] | no (all) |
| G whole morph x1 → x3 | 0.80 [0.76, 0.84] | 0.91 [0.87, 0.94] | 0.84 [0.79, 0.88] | yes (all) |
| H whole morph x1 → x3 | 0.88 [0.85, 0.91] | 0.94 | 0.93 | yes (all) |
| H latent spread x1 → x1s (one identity) | 0.995 [0.99, 1.00] | 1.00 | 1.00 | yes (all) |
| H morph beyond spread x1s → x3 | 0.61 [0.56, 0.65] | 0.62 | 0.63 | no (all) |
| S softening (SMDD render → E7 copy) | 1.00 | 1.00 | 1.00 | yes (all) |

Projection AUCs (CLIP pooled): pipeline 0.99, same-person mixing 0.64 [0.61, 0.67], second identity 0.62,
whole morph 0.72 [0.69, 0.75]; H whole morph 0.81, H latent spread 0.84, H beyond spread 0.59 [0.56, 0.62].

## Q2 Geometry (cosines between step directions)

Same set: cross-fitted over 200 half-splits (mean, 2.5–97.5 percentiles); across sets: full directions with a
cluster-bootstrap interval (these intervals are shifted downward by resampling noise and sometimes do not
cover the point value; read them as rough).

| Cosine with G same-person mixing | CLIP pooled | CLIP mean patch | DINOv3 pooled |
|---|---|---|---|
| G whole morph (reading: ≥ 0.5) | **0.70** [0.63, 0.74] | **0.67** [0.64, 0.70] | **0.81** [0.77, 0.83] |
| H latent spread (one identity, latent moved toward the mean) | 0.66 [0.51, 0.67] | 0.66 [0.53, 0.67] | 0.78 [0.69, 0.79] |
| H morph beyond spread | 0.11 [−0.15, 0.33] | −0.13 [−0.22, 0.02] | −0.20 [−0.33, 0.06] |
| S softening (reading: > 0.5 = softness) | 0.24 [0.05, 0.35] | 0.24 [0.16, 0.27] | 0.24 [0.18, 0.28] |
| FRLL softening (diagnostic of FRLL images) | −0.01 | 0.09 | −0.12 |
| G pipeline | −0.12 | −0.13 | −0.25 |
| split-half reliability of the mixing direction | 0.69 | 0.70 | 0.82 |

Also: G whole morph vs H latent spread 0.72 / 0.79 / 0.82; H whole morph vs H latent spread 0.90 / 0.92 /
0.94 (cross-fitted). **Fixed readings:** "the signal learned from same-person mixes is the signal of real
morphs" holds in all three features (cosine 0.67 to 0.81); "the signal is softness" does not hold (0.24). The
mixing direction is, however, nearly as aligned with the one-identity latent-spread direction (0.66 to 0.78) as
with the whole-morph direction, and not with the part of the morph that remains after spread matching
(−0.20 to 0.11).

## Q3 The author's test: learn from one person, detect two

One-person head O: trained only on x2 (positive) against x1 of the same host. Two-person head T (comparator):
x3 against x1. Set G numbers are OOF over 5 folds by block; set H and all other numbers come from one final head
per arm fitted on all 64 blocks. Floor = best of the seven image statistics (folded); latent = AUC of
"closer to the mean W+ code" alone (not part of the registered floor).

| Contrast | head | CLIP pooled | CLIP mean patch | DINOv3 pooled | image floor | latent statistic |
|---|---|---|---|---|---|---|
| **G x3 vs x1 (primary)** | O | **0.80** [0.77, 0.84] | 0.80 [0.76, 0.84] | 0.78 [0.74, 0.82] | 0.60 (mirror asymmetry) | **1.00** |
| | T | 0.81 [0.77, 0.85] | 0.80 [0.76, 0.84] | 0.83 [0.79, 0.87] | | |
| excess over the image floor | O | +0.20 [0.16, 0.25] | +0.20 [0.15, 0.25] | +0.17 [0.13, 0.22] | | |
| G x3 vs x2 (same-person-mix reference) | O | 0.61 [0.57, 0.65] | 0.63 [0.59, 0.67] | 0.57 [0.54, 0.61] | 0.52 | 0.95 |
| | T | 0.66 [0.62, 0.71] | 0.66 [0.62, 0.71] | 0.60 [0.56, 0.65] | | |
| G x2 vs x1 | O | 0.69 | 0.70 | 0.71 | 0.61 | 0.92 |
| G x3 vs x0 (camera photo) | O | 0.85 [0.81, 0.90] | 0.75 | 0.71 | 1.00 (file bytes) | — |
| G x1 vs x0 | O | 0.52 [0.48, 0.57] | 0.40 | 0.39 | 1.00 | — |
| H x3 vs x1 (transfer) | O | 0.82 [0.80, 0.85] | 0.85 | 0.86 | 0.61 | 1.00 |
| **H x3 vs x1s (spread-matched reference)** | O | **0.47** [0.44, 0.50] | **0.46** [0.44, 0.49] | **0.48** [0.45, 0.51] | 0.54 | 0.35 |
| | T | 0.47 [0.44, 0.50] | 0.44 [0.42, 0.47] | 0.44 [0.42, 0.47] | | |
| H x1s vs x1 (one identity, spread only) | O | 0.84 [0.82, 0.86] | 0.88 | 0.87 | 0.63 | 1.00 |

Paired win rates (G, hosts with s(x3) > s(x1)): head O 0.90 / 0.93 / 0.93. One-person minus two-person head,
G x3 vs x1: −0.007 [−0.036, 0.023] (CLIP pooled), +0.001 (CLIP patch), −0.05 (DINOv3). Fold-seed robustness
(seeds 402 to 405), head O, CLIP pooled: 0.785 to 0.800. Regularisation: C chosen mostly at 0.001 to 0.01 (0.001
is the edge of the grid). H aligned frame (descriptive): head O x3 vs x1 0.81, x3 vs x1s 0.47 (CLIP pooled).

**Softened genuine photos** (flag = score above the value that flags 5% of the 204 native photos of the same
frame; native flagged 10 of 204):

| Softened set | O, CLIP pooled | O, CLIP mean patch | O, DINOv3 pooled |
|---|---|---|---|
| **MAD22 E7, FaceMorpher history (primary)** | 9/204 = **4.4%** [CP 2.0, 8.2] | 17/204 = 8.3% [4.9, 13.0] | 10/204 = 4.9% [2.4, 8.8] |
| MAD22 E7, OpenCV / Webmorph | 8.3% / 7.0% | 7.3% / 5.0% | 3.1% / 2.0% |
| FRLL-Morphs E7 (AMSL, FaceMorpher, OpenCV, Webmorph) | 3.9 to 4.4% | 5.9 to 6.4% | 5.4 to 5.9% |
| SMDD renders, E7 copy (held-out 1,000) | 6.6% [5.1, 8.3] | 11.4% | 10.0% |

Mean shift of FRLL photo scores under softening: −0.13 to +0.06 native standard deviations; SMDD renders
+0.33 to +0.55.

**Fixed reading (registered) for the one-person head: works** in all three features (G x3 vs x1 ≥ 0.75, excess
over the image floor ≥ 0.05, primary flag rate ≤ 15%). **Family verdict by the registered rule: idea works.**

**Registered qualifier (latent averageness): fires in all three features.** The one-person head reaches 0.78
to 0.80 on set G but 0.46 to 0.48 against spread-matched one-identity renders on set H, and it ranks those
one-identity renders above plain reconstructions at 0.84 to 0.88, as strongly as it ranks two-person morphs
above reconstructions (0.82 to 0.86). The latent statistic "distance of the W+ code from the mean code" alone
separates x3 from x1 at 1.00 on set G and on set H, and x3 from x2 at 0.95. The two-person head behaves the
same (0.44 to 0.47 against spread-matched renders). The separation does not survive spread matching.

## Q4 Trace subtraction (one direction projected out of the features before fitting and scoring)

| Removed | head O, G x3 vs x1 (before 0.80 / 0.80 / 0.78) | primary flag rate | H x3 vs x1s |
|---|---|---|---|
| (a) softening (SMDD) | 0.80 / 0.81 / 0.77 | 3.9% / 6.9% / 5.9% | 0.47 / 0.46 / 0.48 |
| (b) pipeline x0 → x1 | 0.81 / 0.80 / 0.79 | 4.4% / 7.4% / 5.4% | 0.47 / 0.46 / 0.48 |
| (c) both | 0.80 / 0.79 / 0.78 | 3.9% / 6.4% / 5.9% | 0.47 / 0.46 / 0.48 |
| (d) H latent spread (G numbers only; descriptive) | 0.72 / 0.67 / 0.66 | 4.9% / 6.9% / 4.9% | not valid (direction estimated on H) |

(CLIP pooled / CLIP mean patch / DINOv3 pooled.) Removing softening or the pipeline direction leaves the
separation (drop ≤ 0.02, "keeps separation") and the flag rate (already ≤ 8.3% before) unchanged. Removing the
single latent-spread direction learned on set H lowers the set G separation by 0.08 to 0.12. Two-person head:
same pattern (`q4_trace_subtraction.csv`).

## Q5 Dose and second identity

- Graded mixing: **not testable**; no graded GAN latent mixes exist (GAN32 and H3 hold midpoints only; the GAN
  dose curve (AG3) was not run).
- Contributor dissimilarity (1 − FR cosine of the two contributors), Spearman ρ with the paired gain
  s(x3) − s(x1):
  - set G, 64 blocks, head O: 0.08 [−0.18, 0.34] / 0.11 [−0.15, 0.37] / −0.03 [−0.30, 0.22]: does not rise;
    head T: 0.28 [0.05, 0.49] / 0.21 [−0.03, 0.43] / 0.24 [0.02, 0.45]: rises for CLIP pooled and DINOv3.
  - set H, 423 pairs, head O: x3 − x1 gain 0.05 / 0.09 / 0.05 (intervals include 0); x3 − x1s gain 0.10
    [0.005, 0.19] / 0.14 [0.05, 0.23] / 0.09 [−0.01, 0.19].
  - Descriptive: gain against the latent distance of the two codes, ρ 0.18 to 0.33 (hosts), 0.27 to 0.36 (x2
    and x3 pooled). More dissimilar contributors also have more distant codes, so these do not separate
    identity from latent displacement.

## Benchmark cells (descriptive, no refit; native genuine only)

| Cell | head O, CLIP pooled | O, CLIP mean patch | O, DINOv3 pooled | head T, CLIP pooled |
|---|---|---|---|---|
| FRLL-Morphs StyleGAN | 0.72 [0.67, 0.77], EER 0.33 | 0.64 | 0.75 | 0.75 |
| corrected MAD22 MIPGAN-I | 0.73 [0.67, 0.78], EER 0.31 | 0.48 | 0.45 | 0.70 |
| corrected MAD22 MIPGAN-II | 0.64 [0.58, 0.69], EER 0.39 | 0.38 | 0.49 | 0.64 |

The neutral-only genuine column is higher in every row (e.g. 0.81, 0.81, 0.73 for head O, CLIP pooled); per
the rule on FRLL neutral-plus-smiling pairs, no conclusion is drawn from that. Q4 variants (a) and (b) are in
`benchmarks.csv` (CLIP pooled head O with softening removed: 0.67 / 0.62 / 0.53).

## Deviations, what failed, what could not be verified

- GPU time: feature extraction took about 67 minutes of wall time on the shared GB10 (two backbones, 12,151
  images each, GPU at 96% use by other jobs; peak memory 1.7 GB), above the registered 1 GB10-hour.
- The first pass (one single-thread process, about 20 s) ran while the CLIP extraction used four processes:
  five processes for that time, above the registered four.
- The registered DINOv3 mean patch token equals DINOv3 pooled (see above); DINOv3 contributes one feature, not
  two. A DINOv3 CLS-token feature was not extracted.
- Cross-set cosine intervals are bootstrap percentiles of a biased statistic (see Q2).
- Q4 (d) on set H is in-sample for the removed direction and is not reported as a result.
- Not available for this family: mirror self-morphs (would need new GAN inversions), graded mixing, camera
  photos for set H (CASIA crops are 112 px), same-person mixes for set H.
- Not verified: whether the set G morphs carry both identities (no FR check of the renders was run; for H3 the
  potency gate failed earlier, 48%); whether the set G camera-photo frame matches the render frame (it does not
  exactly: x0 → x1 includes frame, background and resolution changes).
- Set G is small (64 blocks); G intervals are about ±0.04 for the primary AUC.
