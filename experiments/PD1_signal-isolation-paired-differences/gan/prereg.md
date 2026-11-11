# Signal isolation by paired differences (PD1), GAN latent morphs: pre-registration

Written 11 Nov 2026, 17:00 CET, by the owner of the GAN family of signal isolation by paired differences
(PD1), **before any feature, statistic, head or score of this experiment was computed**. Known before
writing: the earlier GAN heads of the Codex loop (`/mnt/t7/smad_research/gan-native-heads-v1`, 135 heads on
16 training blocks; reconstruction separation 0.73 to 0.78 on FERET diagnostics, no transfer to DiffAE), the
StyleGAN3 ladder re-read (AG5: no network separates H3 morphs from one-identity renders, best 0.61;
spread-matched renders 0.42 to 0.52), and the review number that Laplacian variance alone separates a
landmark morph from its own halves at AUC 0.76 to 0.87. Inventory checks done before writing (no outcome):
file counts, hashes, byte identity of history-matched copies, person uniqueness.

Abbreviations: AUC = area under the ROC curve (0.5 = chance); CI = 95% bootstrap interval; W+ = the StyleGAN
latent code (16 × 512); FR = face recognition; E7 = the existing, approved shrink-and-enlarge history
control; OOF = out-of-fold (scored by a head that did not see the image's block).

## The idea under test (author, 11 Nov)

"By making morphs of the same input image (and of the same person) we can learn something useful for
detection: we can clearly catch the signal." For one host photo and one pipeline, paired differences inside
the host isolate what each step adds; everything constant for the host cancels.

## Images (all exist; nothing is generated)

**Set G, primary (GAN32, StyleGAN3-T FFHQ-1024 inversions, Codex loop).** 64 blocks (32 in
`vast-gan32-v1-results`, 32 in `vast-gan32-trainplus-shard{0,1-v2,2,3}-results`), 32 FERET + 32 FRGC,
128 persons (each in one block only; checked), 256 captures. A block has persons A and B with two captures
each (a0, a1, b0, b1). Every capture is a host. For host a0:

| Rung | Image | File |
|---|---|---|
| camera photo (x0) | the shared-512 photo that was the inversion source (sha256 equal to `SOURCES.json` for 256 of 256; copied byte-for-byte out of `/tmp/opencode/capture-shared-alignment-v1/anchors` into `/mnt/t7/smad_next/PD1/gan/anchors`) | |
| one-photo reconstruction, the pass-through (x1) | G(w_a0) | `RA0` |
| same-person mix (x2) | G((w_a0 + w_a1)/2), two photos of one person | `SA` |
| two-person morph (x3) | G((w_a0 + w_b0)/2) | `P0` |
| mirror self-morph (xm) | **not available**: needs a new GAN inversion of the mirror image (x86 only; generation not requested) | — |

Renders are read from `raw1024/` (native StyleGAN frame). FERET a0/a1 are mostly fa/fb (same session,
expression change), FRGC a0/a1 are two stills; x2 therefore mixes two captures that differ in expression or
session. x1 is a single W+ code, x2 and x3 are midpoints of two codes ("latent averageness": a midpoint lies
nearer the mean code). The camera photo x0 is in a different frame and resolution from the renders, so the
step x0 → x1 contains frame, background and resolution changes besides the generator.

**Set H, transfer (H3 + A37 spread-matched, StyleGAN3-T, CASIA-WebFace).** 423 pairs, 846 persons, each used
once. Host = the contributor shown in the H3 one-identity render (one of the two contributors: A in 202, B
in 221 pairs; checked against the manifest). x1 = H3 render G(w_C) (`h3_bona`); x1s = A37 spread-matched
render of the same contributor (latent moved to the morph's distance from the latent mean; `a37spread`);
x3 = H3 morph G((w_A + w_B)/2) (`h3_sg3`). No x0 (CASIA crops are 112 px) and no x2 exist.
Frames: **raw 1024 StyleGAN output (primary, the same frame as set G)**, H3 raw PNGs copied byte-for-byte
out of `h3_sg3/work/gen_tars/*.tar` (kept pairs only), A37 raw from `a37_sg3ctl/work/gen/a37spread/raw/bona`;
and the aligned 512 eval frame (`orig` variant; descriptive, and to check our CLIP features against the
cache of frozen features read mixing (FZ1), `FZ1/feats/clip_native/sg3.npz`).

**Set S, softening (SMDD).** 2,000 SMDD genuine renders (`train/smdd/os25k_bf_t`) drawn with seed 401 from
the 25,000 pairs of the morph-free networks data (`a47/data47/i3/manifests/train.csv`), each with its
existing E7 copy (`data47/i3/train/smdd_a47e7`). First 1,000 of the draw = S_fit (softening direction),
last 1,000 = S_test (held-out check). Set G hosts have no E7 or stored-small copies, so this is the
softening direction the task names as fallback.

**Set F, softened genuine photos (scoring only; FRLL persons never enter a fit).**
Primary: corrected MAD22 canonical frame, native `BonaFide` (204) against the E7 copies with the
FaceMorpher history (`e7/FaceMorpher`, 204; every copy differs from its native photo). Secondary: corrected
MAD22 `e7/OpenCV` and `e7/Webmorph` (the copies that differ from native), FRLL-Morphs eval frame
`frll_bona/orig` (204) against `resmatch_{amsl,facemorpher,opencv,webmorph}` (204 each).

**Benchmark cells (descriptive, no refit).** FRLL-Morphs StyleGAN (`eval/frllm/stylegan/*_orig`, 1,222)
against `frll_bona/orig` (204); its history-matched copies `resmatch_stylegan` are byte-identical to native
(30 of 30 checked; all 204 will be checked), so only native applies. Corrected MAD22 MIPGAN-I (1,000) and
MIPGAN-II (999) against native `BonaFide` (204), canonical frame; E7 copies byte-identical to native, so only
native applies. Genuine column also given neutral-only (102); no conclusion is drawn from an FRLL
neutral-plus-smiling pair.

**MIPGAN one-person controls (AG1).** Only 7 local smoke images exist (FRLL persons); not complete, not used.

## Features (frozen; extraction only)

Input through the existing loader `smadcvpr/common.ImageItems(res=224)` (its PIL bilinear resize is the only
resize; no new image code). fp32 weights, TF32 matmuls on (as FZ1). All vectors L2-normalised.

| Feature | Model | Vector |
|---|---|---|
| **CLIP pooled (primary)** | OpenAI CLIP ViT-L/14, timm `vit_large_patch14_clip_quickgelu_224` loaded as in FZ1, CLIP RGB mean/std | 768-d projected image embedding |
| CLIP mean patch token | same pass | mean of the 256 patch tokens after the final LayerNorm (1024-d) |
| DINOv3 pooled | timm `vit_large_patch16_dinov3.lvd1689m`, its mean/std | timm pooled pre-logits (1024-d) |
| DINOv3 mean patch token (descriptive) | same pass | mean of patch tokens after the final norm, CLS and registers excluded |

Check: CLIP pooled on the aligned H3/A37 images against FZ1's cache; max |Δ| reported.

## Simple statistics (the floor)

FZ1's seven statistics on the same 224 loader view: high-frequency energy share, Laplacian variance, mean
|image − mirror image|, standard deviation of R, G, B, file bytes. For every contrast each statistic's AUC
is folded around 0.5 (direction not fixed; conservative for us); **floor = the largest folded AUC of the
seven**. Excess = head AUC − floor, CI from the paired cluster bootstrap. Also reported, not part of the
floor: the latent statistic "distance of the W+ code from the mean code of its set" (latent averageness).

## Folds, bootstrap

Set G: 5 folds by block (blocks permuted with seed 401); a block's persons and images are always in one fold.
Set H: 5 folds by pair (seed 401). Set S: 5 folds by image (seed 401). Fold seeds 402 to 405: robustness
range for the Q3 primary number. Intervals: cluster bootstrap over blocks (G), pairs (H), images (S), FRLL
persons with the two-way draw of the MorDIFF ladder re-read (AD1) for morph cells; B = 10,000 for G and H,
2,000 otherwise; seeds [20261111, 71..74, 1]. Exact Clopper-Pearson intervals for flag rates.

## Questions and fixed readings

**Q1 Direction consistency.** Step directions: G: pipeline x0 → x1, same-person mixing x1 → x2, second
identity x2 → x3, whole morph x1 → x3 (and x0 → x3, descriptive); H: whole morph x1 → x3, latent spread
x1 → x1s, morph beyond spread x1s → x3; S: softening (render → E7 copy). Per fold, u = unit mean paired
difference over training hosts; on held-out hosts: share of hosts whose difference has positive projection
on u, and AUC of the projection score f(x)·u (after against before). **Consistent = share ≥ 0.75 with lower
bound > 0.65.**

**Q2 Geometry.** Cosines between step directions. Same set: 200 random half-splits of clusters (seed 401),
one direction from each half; mean and 2.5/97.5 percentiles; split-half reliability of each direction beside
it. Different sets: cosine of full-set directions, interval from cluster bootstrap of both sets (B = 1,000).
Extra direction, labelled a diagnostic of FRLL images: FRLL softening (native → MAD22 FaceMorpher E7).
**Readings:** cos(same-person mixing, whole morph) ≥ 0.5 = "the signal learned from same-person mixes is the
signal of real morphs" (in this feature space); cos(same-person mixing, softening) > 0.5 = "the signal is
softness"; cosines with the pipeline and latent-spread directions are reported beside.

**Q3 The author's test: learn from one person, detect two.** Linear heads with a within-host paired loss:
logistic loss on z(positive) − z(negative), no intercept (both signs fed); z = features standardised on the
training images of the head; L2 penalty C from {1e-3, 1e-2, 1e-1, 1, 10} by inner 3-fold grouped CV
(paired AUC; ties to the smaller C).
- **One-person head (O):** positives x2 (same-person mixes), negatives x1 of the same host; set G only. (Mirror
  self-morphs do not exist for this family.)
- **Two-person head (T), comparator:** positives x3, negatives x1 of the same host; set G.
OOF scores on G (5 folds by block). One final head per arm fitted on all 64 blocks scores everything else
(sets H, S, F, benchmarks); no fold averaging.
Reported for O and T: G OOF AUCs x3 vs x1 (**primary**), x3 vs x0, x3 vs x2, x2 vs x1, x1 vs x0, paired win
rates; O − T difference; each AUC with its floor and excess; H transfer x3 vs x1, **x3 vs x1s
(spread-matched)**, x1s vs x1; flag rate on softened genuine photos.
Flag rate: t = score that flags 5% of the native photos of the same frame (204, numpy quantile 0.95,
"higher"); flag = score > t; primary = share of FaceMorpher-history E7 copies flagged; secondary F sets each
with their own native threshold; S_test likewise (renders).
**Fixed reading per feature, one-person head:** works if G OOF AUC(x3 vs x1) ≥ 0.75 AND excess over the
floor ≥ 0.05 AND primary flag rate ≤ 15%. Fails if AUC(x3 vs x1) < 0.60 OR excess ≤ 0. Otherwise
in-between. **Family verdict** = the reading on CLIP pooled ("works" → idea works, "fails" → idea fails,
in-between → mixed); "mixed" also if another feature gives the opposite clear reading.
**Registered qualifier (latent averageness):** if the one-person head reaches ≥ 0.75 on G but its H AUC
x3 vs x1s is < 0.60, result.md states that the separation does not survive spread matching.

**Q4 Trace subtraction.** Q3 repeated after projecting out of the L2-normalised features (a) the softening
direction (from S_fit), (b) the pipeline direction x0 → x1 (from the training blocks of each fold; from all
64 blocks for the final head), (c) both; (d) the latent-spread direction from set H (G metrics only,
descriptive). Reported: G AUC x3 vs x1, primary flag rate, H x3 vs x1s, before and after. "Keeps
separation" = AUC drop ≤ 0.05; "loses its reaction to softening" = primary flag rate ≤ 15% after projection.

**Q5 Dose and second identity.** Graded mixing: none exists for this family (GAN32 and H3 hold midpoints only;
the GAN dose curve (AG3) was not run) → not testable. Contributor dissimilarity: Spearman ρ between the
paired gain s(x3) − s(x1) (OOF on G, block means; final head on H, per pair) and 1 − FR cosine of the two
contributors (G: the w600k person templates in `data.npz`; H: `pair_cos_a2f_template`). Also against the
latent distance ‖w_A − w_B‖ (descriptive). **Rises** = ρ > 0 with CI excluding 0.

**Benchmarks.** Final O and T heads (and the Q4 (a)/(b) variants) on the three cells: AUC and equal error
rate, native genuine only (both history-matched copies are byte-identical), all and neutral-only genuine.

## Guards and limits

Heads are linear on frozen features; nothing is trained on FRLL, H3 or benchmark images. No ensembles,
score fusion or seed picking. The one-person head sees no two-person image. Set G is small (64 blocks): an
AUC interval is about ±0.07. The G-b potency gate failed for H3 (48% of morphs verify against both
contributors), so H numbers are read as presence or absence of a separating direction, not identity
reading. Frames differ between G/H-raw (StyleGAN FFHQ frame) and F/benchmarks (eval frames): those scores
are descriptive transfer numbers.

**Budget and stop rule.** Feature extraction ≤ 1 shared GB10-hour, GPU memory < 12 GB (batch ≤ 32; checked
with nvidia-smi before each run), at most 4 CPU processes, `nice -n 10`. Heads on CPU. Every command first
run on 8 images. Copies: anchors and H3 raw PNGs are byte copies (sha256 verified); no other image is
written.

**Order.** Inventory → this file → first end-to-end pass (CLIP pooled, fold 1 of set G: Q1 shares and the Q3
one-person head) written into result.md at once → all features, folds, questions.

**Code** `src/PD1/gan/`; outputs `experiments/PD1_signal-isolation-paired-differences/gan/`; large files
`/mnt/t7/smad_next/PD1/gan/`. Pre-run review: not run (CPU heads on cached features; lead to decide).
