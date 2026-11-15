# Signal isolation by paired differences (PD1), diffusion-autoencoder family: pre-registration

Written 11 Nov 2026, 16:56 CET, by the owner of the diffusion-autoencoder (DiffAE; MorDIFF and DiM style) family,
**before any feature, statistic, head or score of this experiment was computed**. Known before writing (from the
record, not recomputed): the MorDIFF ladder re-read (AD1: adapted releases do not rank morphs above one-photo
reconstructions, 0.40 to 0.49; the frozen-encoder MADation FE ViT-L/14 release does, 0.66 at 20 steps and 0.85 at 100,
and separates same-person mixes from reconstructions at 0.72); the FZ1 pre-registration (frozen features read mixing;
its result page is still empty); the identical-and-mirrored-inputs check (AD1b) smoke result (4 FRLL persons: a mix of
a photo with its mirror image gives a nearly symmetric face; identical inputs give NaN in the A43 slerp). No score file
of AD1, FZ1, AD1b or the Codex readouts (`diffae-roi102-v1`) was opened by this owner.

Terms. AUC = area under the ROC curve (0.5 = chance). Host = one capture (photo) A of one person. Step = the change
from one image of a host to another. Two-way person bootstrap = the pigeonhole person bootstrap of AD1 (`a41_read.py`
method: persons ~ Multinomial(n, 1/n); an image's weight is the product of the counts of the persons it shows).
FR = face recognition (glintr100). E7 = the existing, approved shrink-and-enlarge history control.

## Hypothesis (the author's idea, plain words)

For one host photo and one DiffAE pipeline, the family of images x0 (genuine photo), x1 (pipeline run on the photo
alone = reconstruction), x2 (mix of two photos of the same person), x3 (two-person morph) isolates by paired differences
what each step adds, because everything constant for the host cancels. A linear head trained only on one-person images
(x2 against x1 of the same host) then detects two-person morphs (x3 against x1).

## Images (no new image is made)

**Training hosts (non-FRLL; FERET and FRGC persons).** Complete blocks of the Codex DiffAE runs: 102 of
`/mnt/t7/smad_research/diffae-expanded123-v1/run/<block>/` and 28 of `/mnt/t7/smad_research/confirmation64-diffae-v1/<block>/`
(aligned originals for these in `/mnt/t7/smad_research/confirmation64-alignment-v1/<block>/`). `diffae-roi102-v1` is a
feature read-out of the same 102 expanded123 blocks (no images of its own; its features are a different model and
are not used). One confirmation block, `confirm64-feret-F-05`, is **excluded before any computation**: its person A is a
val10 subject by the `prep_train.is_val` sha1 rule (sealed VAL-X persons stay out of every fit). Result: 129 blocks,
258 persons (each person in exactly one block; checked: 0 shared subjects between the two runs), 516 hosts.
A block holds persons A and B with captures a0, a1, b0, b1. Images per block (all 256 × 256, lossless PNG; every render
uses the same pinned DiffAE FFHQ256 autoencoder, semantic lerp + stochastic slerp at α = 0.5, 250 encoding and **20
decoding steps**; checked in the generation code `core.py` / `generate.py` and the call counters):

| Rung | Host a0 (likewise a1, b0, b1) | File |
|---|---|---|
| x0 genuine photo | the capture through DiffAE's FFHQ aligner | `a0-aligned.png` |
| x1 pass-through (reconstruction) | render of the codes of a0 | `RA0.png` |
| x2 same-person mix | mix of a0 and a1 (shared by both hosts of person A) | `SA.png` |
| x3 two-person morph | mix of a0 and b0 (shared by hosts a0 and b0) | `P0.png` |

There is no mirror mix and no graded mix for these hosts. Equal step count (20) and equal storage hold for all renders.

**FRLL images: evaluation and diagnostics only (never in a fit of a reported head or projection).**
- 256 lossless (A43 / A41 generator outputs): x0 = `a41_diffae/.../a256/png256` (204); x1 = A43 `gen/D20/png256` (204,
  20 steps) and A41 `rec/png256` (204, 100 steps); x2 = A43 `gen/C20/png256` (102, 20 steps) and A41 `self/png256` (102,
  100 steps), both mix the neutral and the smiling photo of one person; x3 = A43 `gen/B20/png256` (200, 20 steps) and
  `gen/B/png256` (200, 100 steps), same pairs as the published MorDIFF sample.
- Stored at the published size (A43 `frames/`, 512 frames the releases scored): A (200 published MorDIFF), B, B20, C,
  C20, D, D20, E (photo through the aligner and stored small); R0 = `mordiff_bona` native (204); R1 = its E7 copy.
- Mirror mixes xm: the AD1b renders of a photo mixed with its mirror image (20 steps, 256), if its full run has
  written them when the analysis runs; otherwise its 4 smoke persons, descriptive only.
- **Never draw a conclusion from an FRLL neutral-plus-smiling pair** (the smiling photos differ in capture detail in
  102 of 102 persons): the FRLL x2 (C, C20) rows are printed and marked "confounded, no conclusion".

**Softening material (Q2, Q4).** No shrink-and-enlarge or stored-small copy exists for the training hosts (checked:
`train.csv` has no E7 rows for FERET or FRGC). The softening direction is therefore fitted on SMDD genuine renders
against their existing shrunk copies (`/mnt/t7/smad_heldout/a47/data47/i3/train/smdd_a47e7/os25k_bf_t/`, 80 px; the
originals 256 px in `smadcvpr_data/train/smdd/os25k_bf_t/`). 1,200 pairs, the first 1,200 file names when sorted by
sha256("PD1:" + name): the first 600 fit the direction ("SMDD-fit"), the other 600 are held out for flag rates
("SMDD-test"). FRLL R0 → R1 and R0 → E differences are computed as diagnostics only.

**Benchmark cells (descriptive, no refit).** Registered evaluation manifest `smadcvpr_data/manifests/eval.csv`
(sha 86d055d3…, the one AD1 used): MorDIFF (1,000 morphs; genuine `mordiff_bona` native 204 and `mordiff` resmatch 204)
and the six DiM families `dim_a`, `dim_c`, `fast_dim`, `fast_dim_ode`, `greedy_dim`, `greedy_dim_s` (499 or 500 each;
genuine `dim_bona` native 204 and each family's resmatch 204). No MAD22 row.

## Features

All images through the existing loader `smadcvpr/common.ImageItems(res=224)` (its PIL bilinear resize is the only
resize). No new image operation. GPU under 12 GB (checked with `nvidia-smi` before launch), loader with 3 workers
(4 processes in total), `nice -n 10`, fp32 without TF32.

| Feature set | Model (local cache, offline, `weights_only=True` or safetensors) | Vector |
|---|---|---|
| **CLIP pooled (primary)** | OpenAI CLIP ViT-L/14, timm `vit_large_patch14_clip_quickgelu_224` (FZ1's build), CLIP-native input (RGB, CLIP mean/std) | 768-d projected image embedding |
| CLIP mean patch token | same forward pass | mean of the 256 patch tokens after the final norm, 1,024-d |
| DINOv3 pooled | timm `vit_large_patch16_dinov3.lvd1689m` (FZ1's build) | pooled pre-logits, 1,024-d |
| DINOv3 mean patch token (descriptive) | same forward pass | mean of the patch tokens (prefix tokens excluded) |

Every vector is L2-normalised before use. Reuse check: on the A43 frames my CLIP pooled and DINOv3 pooled vectors must
equal FZ1's caches (`/mnt/t7/smad_next/FZ1/feats/{clip_native,dinov3}/a43.npz`) to within 1e-4 max |Δ|; if they do, the
FZ1 caches are used read-only for the A43 frames' pooled vectors, and only the missing ones are extracted. The AF0 and
ID0 caches hold none of these images.

## Folds and bootstrap

- Five folds by block (both persons of a block always together; persons are unique to blocks): blocks sorted by
  sha256("PD1:" + block), fold = rank mod 5. Every out-of-fold number pools the five held-out folds.
- Intervals: two-way person bootstrap, B = 10,000, seed [20261111, 1, 1] for the training-host pool (258 persons);
  AD1's draw (seed [20261107, 43, 1], all A43 persons) for FRLL. Percentile 95% intervals. Replicates are drawn on
  out-of-fold values without refitting.

## Steps (paired differences inside one host)

pipeline trace P (x0 → x1); same-person mixing M (x1 → x2); second identity I (x2 → x3); whole morph W (x1 → x3);
genuine to morph G (x0 → x3, descriptive); softening S (SMDD original → its shrunk copy; FRLL R0 → R1 and R0 → E as
diagnostics); mirror mixing Mm (FRLL x1 → xm, diagnostic, if available).

## Q1 Direction consistency

Per step and feature set: direction u = mean of the training-fold differences d(h) = f(later) − f(earlier), normalised.
Held-out host projection t(h) = d(h) · u. Report (a) the share of held-out hosts with t > 0 (weighted by the person
counts), (b) the AUC of the projection score f(x) · u, later image against earlier image, over held-out images.
**Fixed reading:** "consistent direction" if share ≥ 0.75 and its lower bound > 0.65; otherwise "not consistent".

## Q2 Geometry

Cosine between step directions, cross-validated: in each of 1,000 bootstrap replicates (blocks resampled), the
resampled blocks are split at random into two halves; cos(u_s(half 1), u_t(half 2)) averaged over both orders;
diagonal = split-half reliability of each direction. Point value = mean over 200 random half splits of the full set;
interval = percentiles of the replicates. Softening direction: SMDD-fit pairs, split into halves the same way. The
disattenuated cosine cos / √(rel_s · rel_t) is printed, descriptive.
**Fixed readings (on the cross-validated cosine, point value):**
- cos(M, W) ≥ 0.5: "the direction learned from same-person mixes is the direction of real morphs"; below: "not aligned".
- cos(M, S) > 0.5: "the mixing signal is softness".
- cos(M, P) > 0.5: "the mixing direction is largely the pipeline trace".

## Q3 The author's test: learn from one person, detect two

- **One-person head (H1):** linear, no intercept, paired logistic loss on the pairs (x2, x1) of each training host
  (logistic regression on the difference vectors with both orientations). Features standardised with the training
  fold's mean and standard deviation over its x1 and x2 images. L2 penalty C from {1e-3, 1e-2, 1e-1, 1, 10} by inner
  3-fold block-grouped CV (maximum inner held-out paired share s(x2) > s(x1); ties to the smaller C), then refit on the
  training part. Score s(x) = w · z(x).
- **Two-person head (H2, comparator):** same recipe on the pairs (x3, x1).
- Convex fits, no seed. One head per result; no ensembles, no fusion.
- **Reported (held-out hosts, pooled out-of-fold, person bootstrap):** AUC x3 vs x1 (primary), x3 vs x0, x2 vs x1,
  x1 vs x0, x3 vs x2, x2 vs x0; paired share s(x3) > s(x1).
- **Simple-statistic floor:** seven statistics, FZ1's set (high-frequency energy share of the luma spectrum above half
  Nyquist; Laplacian variance, `cv2.Laplacian` ksize 1 on luma; mean |image − mirror image|; standard deviation of R, G,
  B; PNG file size), computed on the same 224 loader input the features see (PNG size from the file). Per contrast:
  folded AUC of each statistic alone (direction chosen by its point estimate, so the floor is optimistic); floor = the
  largest. Excess = head AUC − floor, interval from the paired bootstrap with the floor statistic and its direction
  fixed at the point estimate. Descriptive: a head on the seven standardised statistics trained the same way (H1 recipe,
  same folds) and its x3-vs-x1 AUC.
- **Softened genuine photos:** final heads (fit on all 516 hosts, C chosen by the 5-fold CV) scored on FRLL R0 (native,
  512 eval frames) and R1 (their E7 copies). Threshold t = the 95th percentile of the R0 scores (flag = s ≥ t, at most
  5% of R0 flagged); flag rate of R1 at t with exact 95% interval. Secondary (reported, not in the reading): FRLL E
  (stored small) against R0, and SMDD-test shrunk copies at the 5% threshold of the SMDD-test originals. Also the
  native-to-softened mean shift in units of the R0 standard deviation.
- **Fixed reading, per feature set (point values):** the idea **works** for this family if H1 reaches AUC ≥ 0.75 for
  x3 vs x1 on held-out hosts AND exceeds the floor by ≥ 0.05 AND flags ≤ 15% of the FRLL E7 genuine photos at the
  threshold that flags 5% of untouched FRLL photos. It **fails** if x3 vs x1 < 0.60 or the excess is ≤ 0.
  Otherwise **mixed**. The family verdict is the reading on CLIP pooled (primary); if both other feature sets give the
  opposite end reading (works against fails), the verdict is "mixed, backbone-dependent".
- External scoring (final heads, no refit, FRLL, descriptive, equal step count and equal storage only): 256 lossless at
  20 steps (B20 vs D20, B20 vs a256, D20 vs a256, C20 vs D20 confounded), at 100 steps (B vs A41 rec, A41 self vs A41
  rec confounded); stored frames (B20 vs D20, B vs D, C20 vs D20 confounded, C vs D confounded, E vs R0, D20 vs R0, A vs
  D and A vs R0 with "published step count not verified"); mirror mixes vs D20 if available. Also a cohort transfer:
  heads fit on expanded123 only, scored on the 27 confirmation blocks.

## Q4 Trace subtraction

Repeat Q3 (same folds, same recipe, both heads) after removing from every L2-normalised feature vector, before
standardisation, (a) the softening direction (SMDD-fit, k = 1; descriptive k = 5: the span of the mean difference and
the top four principal components of the 600 SMDD-fit differences), (b) the pipeline direction (x0 → x1, estimated on
the training folds only, inside each fold; on all hosts for the final heads), (c) both. Projection f ← f − U Uᵀ f.
**Fixed readings:** "keeps its separation" if H1's x3-vs-x1 AUC falls by less than 0.05; "loses its reaction to
softened genuine photos" if the FRLL E7 flag rate is ≤ 15% and below the unprojected head's rate.

## Q5 Dose and second identity

- Graded mixing: not available in this family (all renders at α = 0.5): **not testable**.
- Contributor dissimilarity: glintr100 cosine between the two contributors' aligned photos (AR1's registered route
  `src/AR1/fr.py`, imported unchanged) for the training-host morphs; for FRLL B20 pairs, AR1's
  `frll_src_emb.npz`. Spearman ρ between 1 − cosine and (i) the morph's out-of-fold H1 score, (ii) the morph's paired
  step, mean over its two hosts of s(x3) − s(x1). Interval: bootstrap over blocks (B = 10,000).
  **Fixed reading:** "the score rises with dissimilarity" if ρ > 0 with lower bound > 0; otherwise "no rise detected".
  Descriptive: the same with the DiffAE semantic-code distance of the two contributors.

## Benchmark cells (descriptive, no refit)

Final H1 and H2, unprojected and with the Q4 projections, scored on MorDIFF and the six DiM families: AUC and equal
error rate against native and against history-matched genuine photos (two-way person bootstrap), the neutral-only
genuine column (102 `_03` photos) beside them, and the share of the history-matched photos flagged at the 5% threshold
of the native photos. Frames differ from the training framing (512 canonical frames against DiffAE's 256 FFHQ crops);
this is printed beside every cell.

## Guards, budget, commands

- FRLL persons never enter a fit (heads, standardisation, C choice, projections). SMDD renders enter only the softening
  direction. No sealed file is opened; no train90 or val10 score is read.
- Budget: at most 2 shared GB10-hours of feature extraction (about 12,000 images × 2 models), GPU memory < 12 GB; heads
  and statistics on CPU, at most 4 processes, `nice -n 10`. Stop if extraction would exceed 3 GB10-hours.
- Order: one backbone (CLIP pooled) and one fold end to end first, numbers into `result.md` at once; then the rest.
- Commands (each tested on 8 images with the real command line first): `src/PD1/diffae/pd1_items.py`,
  `pd1_feats.py`, `pd1_stats.py`, `pd1_fr.py`, `pd1_analysis.py`. Large outputs `/mnt/t7/smad_next/PD1/diffae/`.
- Pre-run review: not run by the owner (CPU heads on cached frozen features; the workflow's sceptic reviews the result).
- Result: `result.md` in this folder.
