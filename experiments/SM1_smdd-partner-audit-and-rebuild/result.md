# SMDD five-partner audit and rebuild of the standard training set (SM1): result

Owner run, 11 Nov 2026. Pre-registration: `prereg.md` (amendments A1 to A11; A12 is the post hoc addendum after the
independent review `experiments/reviews/REVIEW_SM1_20261111.md`, registered before each A12 item ran). Code:
`src/SM1/`. Large outputs: `/mnt/t7/smad_next/SM1/`. Full record: `README.md`.

Status 12 Nov 17:00: Part 1, T-A, T-B, T-C, Part 2, Part 3 frozen heads (14 arms x 5 seeds, incl. five random
partners), A12 items 1 to 9, 11, 13, 2 ViT-L/14 LoRA fits (Athena), all 12 ViT-B/16 LoRA fits (rented RTX 6000 Ada;
A13), A15 and A17 (development data) are read; corrections of the reviews `REVIEW_SM1_VITB_20261112.md` and
`REVIEW_SM1_12FITS_A15_20261112.md` applied. Waiting: ViT-L/14 audit scoring (Athena 3547052, rank rule A14). The
other 23 ViT-L/14 fits stay queued on Athena (forecast late December).

**Development exposure (author's ruling, 12 Nov).** Every benchmark-cell number of the remedy arms c, d, d+, e and f
(frozen heads, release-recipe heads, LoRA fits) is development exposure: no benchmark set may be used to develop a
method, so these rows are never benchmark results of a proposed method (list of cells: `README.md` §1a). The audit
arms are unaffected.

**Labels.** Every Part 3 number in this file is **"our frames, first-test data, arms fixed in advance"**: frozen CLIP
ViT-L/14 features in the FE release's input convention, our linear head recipe, our aligned evaluation frames (morph
frames carry our aligner's border, genuine frames none; review F8), benchmark cells read for the first time by arms
that were fixed before any score. Every rebuilt arm is still separable by sharpness (see Part 3), so Part 3 is
descriptive. A12 rows are post hoc.

## Conclusions (wording of the review, section 3; sizes from A12)

1. **Follows.** In the SMDD release as distributed, all 15,000 training morphs share five second contributors
   (evaluation split: five others); the paper reads naturally as five partners per key image. The content check
   (A12 item 8) agrees with the names (named partner the most similar of the five for 97 and 98 of 100 morphs). To
   be printed only after the question to the SMDD authors. Never called a bug.
2. **Partly follows.** Released SMDD-trained detectors carry a trace of the five training partner images: with unseen
   first contributors, a morph with a training partner scores above one with an SMDD evaluation partner. The margin
   (trained − KE, release crop path) is 0.43 [0.34, 0.54] and 0.95 [0.78, 1.12] logit for the adapted MADation
   ViT-B/16 and ViT-L/14 releases, which sit near their score ceiling, and 3.87, 3.76 and 13.36 logits for the
   frozen-encoder releases (FE ViT-B/16, FE ViT-L/14) and MixFaceNet-MAD. The five rank above 25 untrained partners
   (placebo p ≤ 0.0044). On frozen CLIP features, training on the five produces the trace (trained − KE 4.0 to 4.4)
   and training without them does not (−1.15 to −0.03); difference-in-differences a − b′ 5.25 [5.14, 5.36].
   The trace is an additive bonus: untrained-partner morphs are still caught (own-rule miss 1.4 to 18.4% with
   evaluation partners against 0.0 to 0.3% with trained partners).
3. **Replaced.** Benchmarks contain no training partner, so the trace has no direct effect on them. It matters where
   the five reappear (any validation split drawn from SMDD's training split) and possibly in what is learned
   (conclusion 4).
4. **Descriptive, with its cost.** On frozen CLIP ViT-L/14 features (FE convention, our linear recipe, our frames),
   50 or more partners instead of SMDD's five lower native landmark EER from 7.6 to 4.2–4.8% and diffusion EER from
   20 to 9–10%, but raise flags on history-matched genuine photos (MorDIFF E7 pool 21 → 65% at the own rule; b → b′
   +0.12 [+0.07, +0.18] at the camera-photo threshold). One draw of five random partners recovers most of the gain (b → d5 −2.5
   [−4.2, −0.9]; d5 → K = 50 −0.3 [−1.3, +0.9]) and raises history-pool flags (MorDIFF 0.21 → 0.46). SMDD's
   particular five, not the count, account for most of the gap; the variance between partner sets is unmeasured.
5. **Rewritten (F5).** Halves lower the diffusion rise (+21.4 → +7.2) and lower flagged halves at the head's EER
   threshold (7.2 → 2.6%), but not at the camera-photo threshold (7.2 → 8.8%). History crossing brings the rise to
   +3.5, the released FE header's level (+3.3), at +6.1 landmark points against arm (c) and +2.0 against the release,
   and with 12–14% of untouched FRLL photos flagged at the camera threshold (arm c 2.6%). JPEG 90 / 70 copies did not
   lower a JPEG-50 reaction that history crossing had already cut to +3 points (JPEG 50 − untouched at the camera
   threshold: a +0.196, c +0.121, d +0.072, e +0.032, f +0.068). The landmark cost of halves (c → d +4.2) sits in the
   cells whose morph frames carry our aligner's border (+6.0); on the two border-free cells it is −0.3 [−2.0, +1.3]
   (A12 item 6; two corrected-MAD22 cells only). The size of the storage failure depends on the head
   recipe (F4; A12 item 5): with the release recipe arm (a) rises +6.7 (ours +11.3) and arm (e) +0.0; the cost in
   flagged untouched photos is larger with the release recipe.
6. **Rewritten.** One number, the variance of the Laplacian of the grey image, separates SMDD's training morphs from
   its renders at 0.993 (2,000 v 2,000, 256 px; 0.988 at the loader's 224 px). Part of this is blending itself (a
   morph against its own warped halves: 0.88). Inside each storage size, the rebuilt arms stay at 0.89–0.96 (two-
   variable rule, stratum plus sharpness: 0.93–0.95), so none is close to the registered 0.65.

## Withdrawn statements

- **WITHDRAWN: the gap against the matched unused partners (U) as "the size" of the partner effect** (earlier
  wording: releases 1.7 to 16.2 logits, frozen heads 5.8 to 6.1). Reason (F1): U was matched only on cosine to the
  keys, inter-ocular distance and yaw; on heads that saw none of the 15 partners U scores 0.9 to 1.8 logits below the
  evaluation-split partners. The registered rows stay in Part 2 as registered; the reported size is trained − KE.
- **WITHDRAWN: "identity", "memorisation of the partners' identities", and "shown causally in the releases".**
  Reason (F7): each partner is one StyleGAN2 render, so a partner image (texture, hair, background) cannot be
  separated from its identity; the causal arms are frozen linear heads; the release evidence is a ranking test. The
  registered verdict label "partner memorisation" (A1.1) is kept only as the name of that rule's outcome.
- **WITHDRAWN: "for the other four releases the evaluation split costs 4 to 9.5 points" as partner evidence.**
  Reason (F6): T-A compares the releases' own training images with evaluation images, so it cannot separate partners
  from image memorisation; with training EER 0.00 (both adapted releases) the threshold sits at a single training
  image. T-A stays as a registered descriptive row.
- **WITHDRAWN: "(e) moves the sharpness AUC from 0.99 to 0.72" and any reading of the pooled 0.72 as progress.**
  Reason (F2): 0.72 pools two storage sizes; inside each size the AUC is 0.90 to 0.95 (A12 item 2).
- **WITHDRAWN: any sentence on partner diversity or halves that omits its cost** (earlier: "50 or more partners
  lower the landmark-cell EER by about 3 points"; "halves flag rate halved, the halves arm does not fail the
  registered rule"). Reason (F3, F5): partner diversity raises flags on history-matched genuine photos; at the
  camera-photo threshold halves are flagged more often (0.072 → 0.088) and untouched FRLL photos 2.6% → 11.6%.

- **WITHDRAWN (12 Nov): "history crossing removes the storage rise without a landmark-EER cost"** (ViT-B/16 reading).
  Reason (ViT-B/16 review F1): the history-crossed fits lose MorDIFF detection (native EER 34 / 47% and 32 / 40%;
  own-rule miss 95 to 99%), so their negative rise reflects that loss; diffusion-7 native EER doubles (6.4 → 13.8).
  Also withdrawn: every between-arm statement at the camera threshold of the LoRA fits ("e doubles the flags, f
  brings both below a"), because those thresholds sit on the floor of a bounded head (F2).

## Part 1: documentation (done; no score involved)

Source: `p1_structure.json` (`src/SM1/p1_document.py`, PNG headers and file names of the release on disk).

| | Training release | Evaluation release |
|---|---|---|
| Morph files | 15,000 | 15,000 |
| First contributors | 3,853 (1 to 5 morphs each) | 3,919 |
| Second contributors | **5**: img054553 3,444; img282038 3,310; img496816 3,260; img337488 2,813; img099545 2,173 | **5**: img279570 3,536; img226436 3,331; img141280 3,232; img042475 2,988; img005071 1,913 |
| Contributor among genuine renders | 0 of 3,858 | 0 of 3,924 |
| Morph files not 256 x 256 | 733 (4.89%; 256 x 257 to 256 x 264, one 260 x 258) | 417 (2.78%) |
| Genuine / source renders | 25,000 / 25,000, all 256 x 256 | same |

No contributor, genuine render or source render is shared between the two splits. Every contributor is a file of the
split's morph-source folder (`os25k_m_t`, `os25k_m_e`). That the genuine renders never contribute to a morph is
SMDD's documented design (see the paper quote below), not a finding. Part 1 is a fact about the file names; the
names agree with the image content (A12 item 8, below).

T-C, file names (`tc_files.json`): the release's `train.csv` and `evaluation.csv` list 40,000 files each, no duplicates,
none missing, none unlisted; labels agree with the folders (attack 15,000 in `m15k_*`, bonafide 25,000 in
`os25k_bf_*`); all 15,000 morph names of each split parse as `morphed_<first>_<second>.png`.

**What the paper says (checked, arXiv 2203.06691 HTML, Section 4):** "5k of these images are chosen randomly as the
key morphing images, each is paired with 5 images chosen randomly from the 20k left images of the 25k images aimed to
create the attacks. This results in 25k morphing pairs. The morphing pairs are selected randomly to allow for a
larger variety of similarities between the pairs." And: "setting the blending factor to 0.5 and choosing the warping
factor randomly from the range [0.0,1.0]"; after filtering, "the final set of 15k MAs". The 25k genuine half "will
not go into a morphing process" (stated, and matches the release). **The release differs from the natural reading of
the paper:** the sentence reads as five randomly chosen partners per key image; on disk each split has five partner
images in total, shared by all keys. The paper does not say which was intended.

**Terms (checked, 11 Nov 16:37; project README at
github.com/naserdamer/SMDD-Synthetic-Face-Morphing-Attack-Detection-Development-dataset, raw README.md):** for both the
training and the evaluation source images: "The morphing pairs follow the file names of the morphing attacks in the
training split. Please note that any morphing attacks based on this source data and/or pairing must be (1) made
public, (2) shared with the authors of this work, and (3) linked to this repository and share don this repository."
Licence section: "The dataset, the implementation, or trained models, use is restricted to research purpuses. The
use of the dataset or the implementation/trained models for product development or product competetions (incl. NIST
FRVT MORPH) is not allowed. This project is licensed under the terms of the Attribution-NonCommercial-ShareAlike 4.0
International (CC BY-NC-SA 4.0) license." On disk: no README or licence file in either release zip or folder
(checked; the zips hold only the image folders, the CSVs and, in the evaluation zip, `crop_images_224.py`). Where the
`os25k_m_t` / `os25k_m_e` folders on disk came from is not recorded next to them (not verified). Covered by the
quoted condition: the Part 2 audit morphs (keys and partners are `os25k_m_t` source renders), arms (b), (b′), the
dose arms and the five-random-partner arm (release source data and pairing). Arms (c), (c′), (d) use the genuine
renders only, which the sentence does not name, but CC BY-NC-SA share-alike applies to any distribution. All rebuilt
images stay internal (T7, the leaseB work folder while it exists, Athena project space).

## Expression (A3 substitute, geometry only; `expr_geom.json`)

Logistic mouth-shape probe trained on the AR1 FRLL frames (neutral vs smiling; 5-fold-by-person accuracy 0.79,
0.88, 0.88, 0.90, 0.95). Applied to SMDD: genuine renders 77.7% "smiling" (24,997), release morphs by the mean of
their two contributors' points 97.1% (15,000), contributor renders 84.9% (3,858); the five training partners have
smile probabilities 0.88, 1.00, 1.00, 0.77, 1.00. Domain shift from FRLL photos to StyleGAN2 renders makes the
absolute rates uncertain; the direction (morph class more "smiling" than the genuine class) is descriptive only. The
registered pixel probe of the cue checks could not run as is (fixed box of the eye-aligned 512 frame).

## Build facts (no score involved)

- N = 14,734 release pairs have both contributors admissible under A5 (266 dropped); every arm uses N morphs.
- All rebuilt morphs: 0 engine failures over 30,000 (c, c′) + 58,936 (b, b′, K = 50, K = 500) + 9,520 (audit) + 536
  (AR1) + 14,734 (A12: five random partners, `armd5`) pairs; halves average within 0.5 grey level of the morph on
  every pair with halves (16,036 checked by assertion: 15,000 + 536 + 500 smoke).
- Cross-machine equality: leaseB (x86, OpenCV 4.11.0) outputs equal the DGX (ARM, OpenCV 4.11.0) outputs on every
  compared file (32 per task, 8 for `armd5`, plus the 2,000 smoke files of c and c′); our 536 AR1 morphs equal AR1's
  own OpenCV R4 files (`ar1h_vs_ar1_r4.json`).
- `armd5` (A12 item 11, `pairs_d5.json`): partners img083441, img516393, img182102, img157635, img448540 (each used
  2,946 or 2,947 times; none an audit render, a training or an evaluation partner); the pool reconstruction
  reproduces `armd50.csv` and `armd500.csv` exactly; 3 rows needed the backward swap (K = 5 only).
- Class balance of arm f inside storage strata, all five seeds (`a12_armf_strata.json`; morph share per stratum
  256 px / 256 px + JPEG / 80 px / 80 px + JPEG): 401 0.367 / 0.379 / 0.370 / 0.372; 402 0.368 / 0.377 / 0.375 /
  0.363; 403 0.369 / 0.373 / 0.372 / 0.369; 404 0.367 / 0.378 / 0.370 / 0.372; 405 0.370 / 0.373 / 0.375 / 0.363
  (range 0.363 to 0.379; the arm's overall share is 0.371).

## T-A and T-B: tests with no new image (A3, A8; `tab_sub.json`; registered, descriptive)

Whole-file path (A6), registered subsample (A8: per split 500 morphs per partner, 1,000 genuine, 400 non-contributor
source renders, the 5 partner renders). Threshold t = EER threshold of the training split. Miss rate in %, interval
from 2,000 bootstrap draws over first contributors. **T-A cannot measure partners** (F6): the training morphs are
these detectors' own training images, and for the two adapted releases (training EER 0.00) t sits at a single
training-morph score. Cleaner reading: own EER on the evaluation split against the training split, 0.20 vs 0.00
(ViT-B/16), 0.02 vs 0.00 (ViT-L/14), 3.42 vs 0.51, 2.09 vs 0.62, 2.20 vs 0.60.

| Release | train-split EER | miss at t, training morphs | miss at t, evaluation morphs | difference [95%] | within 1 point | false alarms on evaluation genuine at t | evaluation-split own EER |
|---|---|---|---|---|---|---|---|
| MADation ViT-B/16 | 0.00 | 0.00 | 0.64 | +0.64 [0.36, 1.00] | yes | 0.1 | 0.20 |
| MADation ViT-L/14 | 0.00 | 0.00 | 5.00 | +5.00 [4.18, 5.82] | no | 0.0 | 0.02 |
| MADation FE ViT-B/16 | 0.51 | 0.52 | 9.28 | +8.76 [7.64, 9.90] | no | 0.5 | 3.42 |
| MADation FE ViT-L/14 | 0.62 | 0.64 | 4.72 | +4.08 [3.19, 5.00] | no | 0.4 | 2.09 |
| MixFaceNet-MAD | 0.60 | 0.60 | 10.08 | +9.48 [8.22, 10.81] | no | 0.4 | 2.20 |
| MADation FS ViT-B/16 (descriptive) | 0.11 | 0.12 | 19.76 | +19.64 [17.90, 21.37] | no | 0.0 | 1.62 |
| MADation FS ViT-L/14 (descriptive) | 13.80 | 13.8 | 26.08 | +12.28 [10.03, 14.55] | no | 13.2 | 18.11 |

Per-partner miss at t (training five; evaluation five): ViT-B/16 all 0.0; 1.0, 0.0, 1.8, 0.2, 0.2. ViT-L/14 all 0.0;
8.2, 1.8, 11.0, 4.0, 0.0. FE ViT-B/16 0.2, 0.4, 0.0, 2.0, 0.0; 31.8, 7.0, 3.4, 3.0, 1.2. FE ViT-L/14 0.0, 0.0, 0.0,
0.8, 2.4; 14.8, 1.6, 0.6, 5.8, 0.8. MixFaceNet 1.0, 0.0, 1.2, 0.8, 0.0; 21.8, 19.8, 5.2, 0.6, 3.0 (evaluation partner
order img005071, img042475, img141280, img226436, img279570; img005071 is the hardest for four of five releases).
Partner-level variance of the evaluation-split error rates (H-new-6): A12 item 7 below.

T-B, rank of the unblended partner renders among 400 source renders of their split (share of renders scoring lower):

| Release | training partners (img054553, img099545, img282038, img337488, img496816) | in top 10% (binomial p) | evaluation partners (control) | in top 10% (p) |
|---|---|---|---|---|
| MADation ViT-B/16 | 0.87, 0.81, 0.98, 0.67, 1.00 | 2 (0.081) | 0.69, 0.73, 0.82, 0.84, 0.84 | 0 (1) |
| MADation ViT-L/14 | 0.04, 0.11, 0.62, 0.13, 0.13 | 0 (1) | 0.30, 0.05, 0.40, 0.73, 0.24 | 0 (1) |
| MADation FE ViT-B/16 | 0.99, 0.81, 0.98, 0.78, 0.98 | 3 (0.0086) | 0.37, 0.95, 0.93, 0.81, 0.93 | 3 (0.0086) |
| MADation FE ViT-L/14 | 1.00, 0.92, 0.87, 0.99, 0.98 | 4 (0.00046) | 0.16, 0.91, 0.77, 0.06, 0.84 | 1 (0.41) |
| MixFaceNet-MAD | 0.98, 1.00, 0.80, 0.57, 1.00 | 3 (0.0086) | 0.86, 0.52, 0.69, 0.94, 0.68 | 1 (0.41) |
| FS ViT-B/16 (descriptive) | 0.61, 0.99, 0.02, 0.06, 1.00 | 2 (0.081) | 0.74, 0.33, 0.33, 0.48, 0.17 | 0 (1) |
| FS ViT-L/14 (descriptive) | 0.96, 0.76, 0.70, 0.68, 1.00 | 2 (0.081) | 0.24, 0.55, 0.81, 0.72, 0.66 | 0 (1) |

## Part 2: partner audit of released detectors

Audit set: 500 keys (unused `os25k_m_t` renders) x 5 trained partners (KP), x 5 matched unused partners (KU),
x 5 evaluation-split partners (KE; never trained by any release, made by our engine); first 100 keys x 20 placebo
partners (KX); our engine at 256 px; 10,055 images, all MTCNN crops retained. Placebo p = exact permutation p that
the 5 trained partners rank above the 25 unused (5 matched + 20 placebo) on the first 100 keys (floor 1/C(30,5) =
7.0e-6; the five p values share the same 30 partners and 100 keys, so they are not independent).

**Reported size: against the evaluation-split partners (A12 item 1, post hoc; `a12_partner_ref.json`).** Gap =
mean over keys of the per-key difference of mean logits over the 5 partners; 10,000 key-bootstrap draws (seed
20261111, the same draws for every score set). Own-rule miss = share of morphs with logit < 0.

| Release | trained − KE (crop path) | KE − U | trained − U (registered row, biased) | trained − KE (whole file) | own-rule miss KP / KE / KX / KU (crop) |
|---|---|---|---|---|---|
| MADation ViT-B/16 | 0.43 [0.34, 0.54] | 1.29 [1.08, 1.51] | 1.72 | 0.44 [0.37, 0.52] | 0.001 / 0.014 / 0.019 / 0.064 |
| MADation ViT-L/14 | 0.95 [0.78, 1.12] | 2.56 [2.23, 2.90] | 3.50 | 0.45 [0.37, 0.55] | 0.002 / 0.032 / 0.045 / 0.128 |
| MADation FE ViT-B/16 | 3.87 [3.72, 4.01] | 0.56 [0.41, 0.71] | 4.43 | 4.14 [3.97, 4.32] | 0.003 / 0.082 / 0.074 / 0.077 |
| MADation FE ViT-L/14 | 3.76 [3.55, 3.96] | 1.42 [1.22, 1.61] | 5.17 | 3.46 [3.27, 3.67] | 0.003 / 0.080 / 0.080 / 0.114 |
| MixFaceNet-MAD | 13.36 [12.90, 13.82] | 2.80 [2.57, 3.03] | 16.16 | 4.57 [4.40, 4.74] | 0.000 / 0.184 / 0.148 / 0.240 |
| FS ViT-B/16 (descriptive) | 1.56 [1.35, 1.79] | 2.25 [2.02, 2.48] | 3.81 | – | 0.000 / 0.096 / 0.119 / 0.233 |
| FS ViT-L/14 (descriptive) | 6.90 [6.60, 7.20] | 1.68 [1.47, 1.88] | 8.58 | – | 0.022 / 0.430 / 0.492 / 0.558 |

Why trained − U is biased: U was matched only on cosine to the keys, inter-ocular distance and yaw (not sharpness,
colour, background, hair or gender), and U scores 0.9 to 1.8 logits below KE even on frozen heads that saw none of
the 15 partners (table below). KE is not exactly neutral either: on those heads trained − KE is −1.15 to −0.03, i.e.
the five training partners score slightly *below* the evaluation partners when untrained; the head DiD below is the
clean comparison. The adapted MADation releases are near their score ceiling (maximum logits 11.75 and 12.38; 26%
and 41% of trained-partner morphs within 0.1 of the maximum, review F7). Whole-file MixFaceNet-MAD is off its input
path (KP own-rule miss 0.25 there), so its crop row is the reading.

**Frozen heads on whole-image features (our frames, first-test data, arms fixed in advance; A12 item 1).**

| Head arm | trained the five? | trained − KE (5-seed mean) | per seed | KE − U | trained − U (registered) | own-rule miss KP / KE / KU |
|---|---|---|---|---|---|---|
| a (release files) | yes | 4.10 [3.91, 4.29] | 4.16, 4.16, 4.00, 4.13, 4.04 | 1.69 | 5.79 | 0.000 / 0.022 / 0.029 |
| a256 | yes | 4.03 [3.84, 4.23] | 4.09, 4.09, 3.93, 4.05, 4.00 | 1.81 | 5.84 | 0.000 / 0.021 / 0.029 |
| b (our tool, release pairs) | yes | 4.42 [4.24, 4.60] | 4.49, 4.53, 4.32, 4.45, 4.32 | 1.67 | 6.09 | 0.000 / 0.021 / 0.035 |
| K = 50 | no | −0.49 [−0.67, −0.32] | −0.52, −0.50, −0.46, −0.49, −0.49 | 1.83 | 1.34 | 0.003 / 0.003 / 0.007 |
| K = 500 | no | −0.52 [−0.69, −0.35] | −0.53, −0.46, −0.56, −0.57, −0.50 | 1.14 | 0.61 | 0.001 / 0.000 / 0.001 |
| b′ | no | −1.15 [−1.32, −0.97] | −1.21, −1.09, −1.16, −1.18, −1.10 | 1.25 | 0.10 | 0.003 / 0.001 / 0.001 |
| c′ | no | −0.85 [−1.02, −0.68] | −0.88, −0.86, −0.83, −0.81, −0.87 | 1.25 | 0.40 | 0.002 / 0.000 / 0.001 |
| c | no | −0.58 [−0.75, −0.41] | −0.64, −0.50, −0.59, −0.62, −0.55 | 0.93 | 0.35 | 0.001 / 0.000 / 0.000 |
| d | no | −0.33 [−0.50, −0.16] | −0.33, −0.26, −0.36, −0.39, −0.31 | 0.98 | 0.65 | 0.002 / 0.001 / 0.001 |
| d+ | no | −0.42 [−0.60, −0.23] | −0.41, −0.28, −0.51, −0.45, −0.44 | 1.33 | 0.92 | 0.001 / 0.001 / 0.001 |
| e | no | −0.10 [−0.25, 0.05] | −0.06, −0.05, 0.05, −0.13, −0.32 | 1.36 | 1.26 | 0.001 / 0.001 / 0.002 |
| f | no | −0.03 [−0.18, 0.12] | 0.00, −0.09, 0.06, −0.00, −0.13 | 1.36 | 1.33 | 0.001 / 0.002 / 0.002 |
| FE ViT-L/14 release header | SMDD-trained | 3.46 [3.27, 3.67] | – | 1.45 | 4.92 | 0.002 / 0.019 / 0.024 |

Difference-in-differences of trained − KE (key bootstrap): a − b′ 5.25 [5.14, 5.36]; a − c′ 4.95 [4.85, 5.06];
a − c 4.68 [4.54, 4.83]; a − K = 50 4.59 [4.49, 4.70]; b − b′ 5.57 [5.46, 5.67]; FE header − b′ 4.61 [4.47, 4.75]
(registered DiD against U: a − c′ 5.39 [5.27, 5.50]). On these features and this recipe, training on the five
partner images produces the trace; frozen linear heads only, partner images not identities.

**Registered rows (A1.1; `p2_full.json` "detectors", "whole_file_secondary"; gap against U, kept as registered, not
the size).** Interval from 10,000 key-bootstrap draws; two-way = keys x slots.

| Release | gap vs U [95%] | two-way [95%] | AUC KP vs KU [95%] | per-slot gaps (img054553, img282038, img496816, img337488, img099545) | sign-flip p | placebo p (trained ranks among 30) | responsive (AUC morphs vs key renders) | registered rule outcome (A1.1) |
|---|---|---|---|---|---|---|---|---|
| MADation ViT-B/16 | 1.72 [1.48, 1.99] | [0.42, 3.27] | 0.807 [0.795, 0.819] | 1.83, 0.41, 4.55, 1.94, −0.12 | 0.062 | 0.0004 (4, 3, 2, 6, 8) | 1.000 | "partner memorisation" |
| MADation ViT-L/14 | 3.50 [3.10, 3.93] | [1.40, 5.53] | 0.837 [0.828, 0.846] | 5.18, 2.46, 6.64, 3.26, −0.01 | 0.062 | 0.0044 (3, 2, 6, 14, 7) | 1.000 | "partner memorisation" |
| MADation FE ViT-B/16 | 4.43 [4.21, 4.65] | [3.38, 5.54] | 0.819 [0.806, 0.832] | 2.84, 3.31, 6.21, 5.17, 4.60 | 0.031 | < 1e-4 (5, 4, 2, 3, 1) | 0.998 | "partner memorisation" |
| MADation FE ViT-L/14 | 5.17 [4.93, 5.41] | [2.93, 7.74] | 0.764 [0.752, 0.776] | 3.46, 2.23, 9.98, 6.58, 3.60 | 0.031 | < 1e-4 (2, 8, 3, 4, 1) | 0.999 | "partner memorisation" |
| MixFaceNet-MAD | 16.16 [15.57, 16.76] | [13.33, 18.71] | 0.922 [0.912, 0.931] | 16.55, 19.33, 19.22, 11.24, 14.48 | 0.031 | < 1e-4 (5, 3, 4, 2, 1) | 0.999 | "partner memorisation" |

Whole-file secondary (registered, same rule): gap vs U 1.87 [1.66, 2.11], 1.63 [1.40, 1.86], 5.05 [4.82, 5.28],
4.92 [4.65, 5.19], 6.32 [6.03, 6.61]; placebo p 0.0008, 1.4e-5, 8.4e-5, 0.0006, 8.4e-5 (same order); every
release's rule outcome "partner memorisation" (FS pair included, descriptive). Bridge to the original tool (A3,
whole files): our-engine audit morphs minus SMDD's own morphs with the same partner, mean logit per partner:
adapted MADation −0.14 to +0.19 (both splits); FE ViT-B/16 +0.3 to +2.5; FE ViT-L/14 −0.5 to +2.2; MixFaceNet −0.4
to +1.0 (SMDD's training-split morphs are the releases' training images).

(Slot order in the table header is the order of `K.PARTNERS`.) Mean logits, crop path: key x trained partner / key x
matched unused / partner x partner / unused x unused / key renders: ViT-B/16 11.6 / 9.8 / 11.6 / 7.9 / −12.2;
ViT-L/14 12.2 / 8.7 / 12.3 / 0.6 / −12.9; FE ViT-B/16 9.7 / 5.3 / 11.5 / 5.6 / −10.2; FE ViT-L/14 12.1 / 7.0 /
14.1 / 7.0 / −12.6; MixFaceNet 22.4 / 6.2 / 39.2 / 2.3 / −17.9. Percentile of the five trained partner renders
among the 500 key renders (crop path): ViT-B/16 0.57, 0.92, 0.28, 0.03, 0.60; ViT-L/14 0.09, 0.13, 0.02, 0.01, 0.31;
FE ViT-B/16 1.00, 0.99, 0.98, 0.98, 0.83; FE ViT-L/14 1.00, 0.99, 0.99, 1.00, 0.99; MixFaceNet 1.00, 0.99, 0.99,
0.98, 0.94 (matched unused renders: 0.02 to 0.99, no pattern).

**Registered readings.** Lead's falsifier ("no partner memorisation if the paired gap interval includes 0 for every
detector"): **does not hold** (crop path and whole files). SMDD-T partner condition (A1.2): does not hold, so the
partner claim is not dropped. The size and wording of the claim are conclusion 2 above. The LoRA fits will be read
on the audit set (A12 item 10, H-new-5) when they finish.

## Part 3: rebuild arms on frozen features (our frames, first-test data, arms fixed in advance)

**Rebuild acceptance, Laplacian variance (A3, A4; `lapvar.json`, `lapvar_f.json`; registered; 2,000 morphs vs 2,000
genuine-class images per arm; AUC = P(morph has the lower variance)).** No rebuilt arm is accepted (bar: AUC ≤ 0.65).
The pooled AUC of e and f mixes two storage sizes and is not a reduction (withdrawn statement above).

| Arm | AUC at stored size | AUC at the loader's 224 px | median variance morph / genuine (stored) |
|---|---|---|---|
| a release (reference) | 0.993 | 0.988 | 209 / 854 |
| b | 0.999 | 0.998 | 161 / 859 |
| b′ | 0.998 | 0.995 | 177 / 856 |
| c | 0.997 | 0.993 | 188 / 851 |
| c′ | 0.998 | 0.995 | 180 / 843 |
| d (halves as genuine) | 0.936 | 0.949 | 189 / 532 |
| e (pooled over 2 storage sizes) | 0.856 | 0.716 (pooled; not a reduction) | 336 / 768 |
| f (pooled over 4 storage strata) | 0.843 | 0.724 (pooled; not a reduction) | 319 / 733 |
| K = 50 | 0.999 | 0.997 | 175 / 863 |
| K = 500 | 0.998 | 0.995 | 178 / 858 |

**Inside each storage stratum (A12 item 2, post hoc; `a12_sharp.json`; seed-401 compositions, 2,000 + 2,000 per arm;
± Hanley–McNeil SE).** Two-variable rule = 5-fold out-of-fold AUC of a logistic regression on stratum indicators and
log variance at 224 px (stratum alone: 0.49 to 0.50, the classes are balanced inside strata).

| Arm | stratum (morphs / genuine in the sample) | AUC stored | AUC at 224 px | morph against renders / against halves (224 px) |
|---|---|---|---|---|
| d | 256 px (2,000 / 2,000) | 0.935 ± 0.004 | 0.948 ± 0.004 | 0.989 / 0.906 |
| e | 256 px (991 / 1,038) | 0.936 ± 0.006 | 0.952 ± 0.005 | 0.991 / 0.914 |
| e | 80 px (1,009 / 962) | 0.908 ± 0.007 | 0.898 ± 0.007 | 0.923 / 0.871 |
| f | 256 px (661 / 686) | 0.933 ± 0.007 | 0.949 ± 0.006 | 0.992 / 0.910 |
| f | 256 px + JPEG (330 / 352) | 0.935 ± 0.010 | 0.956 ± 0.008 | 0.987 / 0.921 |
| f | 80 px (655 / 650) | 0.911 ± 0.008 | 0.901 ± 0.009 | 0.926 / 0.874 |
| f | 80 px + JPEG (354 / 312) | 0.894 ± 0.013 | 0.886 ± 0.013 | 0.911 / 0.863 |

Two-variable rule (stratum + log variance at 224 px): d 0.948, e 0.928, f 0.927 (with stratum x variance
interactions 0.948, 0.927, 0.926; at stored size 0.935, 0.922, 0.919). Arms e and f are no nearer acceptance than
arm d; the registered verdict ("not accepted") stands. A morph of (c) against its own two halves: AUC 0.881, median
variance ratio morph / mean of its halves 0.52. All rebuilt files are 256 x 256 (the 80-px copies are stored at 80
px by the unchanged a47 shrink call).

**Feature platform (A7):** all features from Athena job 3545820 (A100, torch 2.2.1). Equivalence with the DGX
features on all 14,120 FRLL evaluation frames: max |Δ feature| 1.0e-3, max |Δ FE-header logit| 0.097, AUC of the FE
header (all FRLL morphs vs genuine) 0.88252 on Athena vs 0.88253 on the DGX (Δ −1.1e-5) (`feat_equivalence.json`).
**Pool-cue check (A1.3):** a head cannot tell `os25k_bf_t` from `os25k_m_t` renders, out-of-fold AUC 0.507
(5,000 + 5,000; `pool_cue.json`).

**Smoke pass** (500 morph pairs + 834 genuine renders per arm, seed 401 only; `p3_smoke.json`): superseded by the
full run below; kept in the JSON.

**Full run, frozen CLIP ViT-L/14 heads, 5 seeds (401 to 405), N = 14,734 morphs + 25,000 genuine per arm
(`p3_full.json`, per seed `p3_full_seeds.csv`; our frames, first-test data, arms fixed in advance).** Value = mean of
the 5 seeds' metrics; [95%] = person bootstrap (B = 2,000) of that mean. EER in %. Seed spread is small (arm c
landmark-7 native EER per seed 3.25, 3.24, 3.24, 3.29, 3.23), but the training-pair bootstrap SD of landmark-7 EER is
0.26 to 0.83 points (`p3_full_boot_seeds.csv`), so steps of about 1 point are marginal (F10).

| Arm | landmark-7 EER native | landmark-7 E7 | landmark rise | diffusion-7 EER native | diffusion rise | GAN-3 EER | halves flagged, AR1 EER thr | halves flagged, camera thr | R2w OpenCV flagged (EER thr) | AUC halves vs R0 | FRLL neutral above smiling |
|---|---|---|---|---|---|---|---|---|---|---|---|
| a release | 7.34 [5.47, 9.26] | 9.92 | +2.59 [1.91, 3.28] | 20.70 | +11.32 [9.66, 13.41] | 15.82 | 0.083 [0.067, 0.101] | 0.076 | 0.078 | 0.604 | 0.70 [0.61, 0.78] |
| a256 (256 x 256 files only) | 7.53 | 10.29 | +2.76 | 21.69 | +11.15 | 16.60 | 0.087 | 0.079 | 0.078 | 0.602 | 0.70 |
| b our tool, release pairs (K = 5) | 7.61 [5.72, 9.73] | 10.76 | +3.15 | 20.15 | +14.56 | 16.99 | 0.094 | 0.082 | 0.080 | 0.621 | 0.63 |
| K = 50 | 4.79 [3.43, 6.46] | 8.51 | +3.72 | 9.71 | +16.45 | 7.52 | 0.069 | 0.063 | 0.070 | 0.648 | 0.67 |
| K = 500 | 4.51 [3.25, 5.72] | 7.79 | +3.29 | 8.80 | +14.67 | 7.07 | 0.058 | 0.065 | 0.047 | 0.656 | 0.56 |
| b′ K = 2,433 (cap 7) | 4.20 [2.98, 5.37] | 7.60 | +3.41 | 9.02 | +17.04 | 6.80 | 0.062 | 0.070 | 0.054 | 0.652 | 0.53 |
| c′ balanced random, genuine pool | 4.37 [3.08, 5.59] | 7.71 | +3.34 | 10.07 | +17.31 | 8.19 | 0.055 | 0.062 | 0.047 | 0.657 | 0.66 |
| c balanced look-alike | 3.25 [2.23, 4.24] | 6.97 | +3.72 | 7.18 | +21.42 | 8.40 | 0.072 [0.057, 0.089] | 0.072 | 0.072 | 0.673 | 0.77 [0.68, 0.84] |
| d c + halves as genuine | 7.44 [5.79, 9.11] | 9.29 | +1.85 | 14.39 | +7.20 | 8.61 | 0.026 [0.017, 0.036] | 0.088 | 0.025 | 0.572 | 0.59 |
| d+ (halves added, unequal count) | 6.85 | 8.70 | +1.86 | 15.22 | +6.82 | 8.18 | 0.022 | 0.092 | 0.026 | 0.580 | 0.63 |
| e d + history crossing | 9.38 [7.65, 11.04] | 10.24 | +0.86 [0.58, 1.37] | 13.69 | +3.47 [2.06, 4.85] | 11.38 | 0.023 | 0.071 | 0.028 | 0.546 | 0.53 |
| f e + JPEG 90 / 70 copies | 8.45 [6.84, 10.23] | 9.61 | +1.16 [0.77, 1.50] | 15.06 | +3.61 [2.47, 4.97] | 10.55 | 0.023 | 0.066 | 0.029 | 0.546 | 0.56 |
| FE ViT-L/14 release header (reference) | 8.37 | 8.97 | +0.60 | 19.51 | +3.33 | 12.73 | 0.076 | 0.073 | 0.075 | 0.541 | 0.34 |

The GAN-3 E7 rise is 0 for every arm because the E7 genuine copies of those cells equal the native photos. Every
better native EER must be read together with the fixed-threshold costs below. Arm c is the worst-behaved base under
history matching, so d / e / f against c look large; compare them with arm a as well.

Steps between arms (difference of 5-seed means, paired person bootstrap; `p3_full.json` "steps"):

| Step | what changes | landmark-7 EER native | landmark rise | diffusion-7 EER native | diffusion rise | halves flagged (AR1 EER thr) | neutral above smiling |
|---|---|---|---|---|---|---|---|
| a → b | tool (SMDD's files → our engine) | +0.27 [−0.29, +0.89] | +0.57 | −0.54 | +3.25 [1.78, 4.86] | +0.010 | −0.06 |
| b → K = 50 | five partners → 50 (random pool partners; count confounded with which partners, F9) | −2.82 [−4.18, −1.32] | +0.57 | −10.44 | +1.89 | −0.024 | +0.03 |
| b → K = 500 | five → 500 | −3.11 [−4.81, −1.63] | +0.14 | −11.36 | +0.11 | −0.036 | −0.08 |
| b → b′ | five → 2,433 | −3.42 [−5.19, −1.87] | +0.26 | −11.14 [−13.88, −8.11] | +2.47 | −0.031 | −0.10 |
| b′ → c′ | source pool + genuine identities become contributors | +0.18 [−0.36, +0.69] | −0.07 | +1.06 | +0.27 | −0.008 | +0.13 |
| c′ → c | random → look-alike pairs | −1.12 [−1.92, −0.38] | +0.38 | −2.89 | +4.11 [2.28, 6.26] | +0.018 | +0.11 |
| c → d | halves as genuine images | +4.19 [+2.95, +5.62] | −1.87 [−2.58, −1.24] | +7.21 | −14.22 [−17.32, −11.57] | −0.047 [−0.063, −0.032] | −0.18 |
| d → e | history crossing | +1.94 [+0.91, +2.91] | −0.99 [−1.39, −0.46] | −0.70 | −3.73 [−5.43, −1.99] | −0.003 | −0.06 |
| a → a256 | drop the 733 off-size files | +0.19 | +0.17 | +0.99 | −0.17 | +0.003 | 0.00 |

**Fixed-threshold paired table (A12 item 3, post hoc re-read of the existing scores; `a12_fixed.json`, per seed
`a12_fixed_seeds.csv`).** Flag = genuine-class image scored at or above the threshold; miss = morph below it; always
read together. "Camera threshold" = the 95th percentile of the head's logits on AR1 FRGC/colorFERET R0 (5% of those
camera photos flagged); "own rule" = logit ≥ 0. JPEG 50 − untouched is paired on the same 204 FRLL photos. 5-seed
means, person-bootstrap intervals.

Camera-photo threshold:

| Arm | halves flagged | R2w OpenCV / FaceMorpher flagged | untouched FRLL flagged | JPEG 50 − untouched | MorDIFF E7 pool flagged | miss FRLL landmark-4 | miss AR1 OpenCV R4 | miss MorDIFF |
|---|---|---|---|---|---|---|---|---|
| a release | 0.076 [0.060, 0.093] | 0.068 / 0.060 | 0.091 [0.050, 0.136] | 0.196 [0.143, 0.251] | 0.770 | 0.187 [0.139, 0.240] | 0.058 | 0.204 |
| a256 | 0.079 [0.063, 0.097] | 0.068 / 0.059 | 0.098 [0.055, 0.145] | 0.197 [0.142, 0.256] | 0.751 | 0.194 [0.144, 0.248] | 0.060 | 0.229 |
| b (K = 5, SMDD partners) | 0.082 [0.066, 0.101] | 0.070 / 0.058 | 0.117 [0.070, 0.170] | 0.206 [0.152, 0.262] | 0.751 | 0.178 [0.129, 0.235] | 0.069 | 0.150 |
| K = 50 | 0.063 [0.047, 0.080] | 0.064 / 0.057 | 0.025 [0.005, 0.049] | 0.217 [0.159, 0.276] | 0.654 | 0.181 [0.134, 0.233] | 0.060 | 0.125 |
| K = 500 | 0.065 [0.050, 0.083] | 0.062 / 0.054 | 0.055 [0.023, 0.089] | 0.238 [0.175, 0.303] | 0.884 | 0.133 [0.095, 0.172] | 0.036 | 0.026 |
| b′ (K = 2,433) | 0.070 [0.055, 0.087] | 0.056 / 0.054 | 0.046 [0.018, 0.078] | 0.224 [0.166, 0.280] | 0.873 | 0.104 [0.073, 0.138] | 0.045 | 0.035 |
| c′ | 0.062 [0.048, 0.079] | 0.053 / 0.050 | 0.053 [0.024, 0.086] | 0.216 [0.161, 0.273] | 0.815 | 0.126 [0.090, 0.164] | 0.037 | 0.069 |
| c look-alike | 0.072 [0.056, 0.089] | 0.073 / 0.056 | 0.026 [0.006, 0.054] | 0.121 [0.076, 0.175] | 0.837 | 0.091 [0.062, 0.124] | 0.053 | 0.067 |
| d halves | 0.088 [0.072, 0.106] | 0.077 / 0.062 | 0.116 [0.068, 0.171] | 0.072 [0.031, 0.115] | 0.652 | 0.211 [0.164, 0.259] | 0.011 | 0.104 |
| d+ | 0.092 [0.076, 0.110] | 0.080 / 0.064 | 0.120 [0.071, 0.176] | 0.117 [0.068, 0.168] | 0.666 | 0.193 [0.147, 0.241] | 0.012 | 0.126 |
| e history | 0.071 [0.057, 0.085] | 0.064 / 0.058 | 0.136 [0.087, 0.194] | 0.032 [−0.005, 0.072] | 0.637 | 0.235 [0.189, 0.280] | 0.014 | 0.078 |
| f JPEG | 0.066 [0.053, 0.080] | 0.063 / 0.061 | 0.132 [0.079, 0.191] | 0.068 [0.028, 0.110] | 0.718 | 0.220 [0.175, 0.266] | 0.015 | 0.059 |
| FE header (ref.) | 0.073 [0.055, 0.091] | 0.067 / 0.060 | 0.265 [0.196, 0.338] | 0.025 [−0.020, 0.069] | 0.716 | 0.069 [0.043, 0.102] | 0.060 | 0.045 |

Own rule (logit ≥ 0):

| Arm | halves flagged | R2w OpenCV / FaceMorpher flagged | untouched FRLL flagged | JPEG 50 − untouched | MorDIFF E7 pool flagged | miss FRLL landmark-4 | miss AR1 OpenCV R4 | miss MorDIFF |
|---|---|---|---|---|---|---|---|---|
| a release | 0.002 [0.000, 0.004] | 0.002 / 0.002 | 0.000 [0.000, 0.000] | 0.013 [0.000, 0.035] | 0.267 | 0.508 [0.441, 0.579] | 0.276 | 0.721 |
| a256 | 0.002 [0.000, 0.005] | 0.002 / 0.002 | 0.001 [0.000, 0.003] | 0.018 [0.001, 0.043] | 0.254 | 0.513 [0.446, 0.584] | 0.274 | 0.728 |
| b (K = 5, SMDD partners) | 0.005 [0.001, 0.011] | 0.005 / 0.004 | 0.000 [0.000, 0.000] | 0.019 [0.000, 0.044] | 0.215 | 0.524 [0.455, 0.597] | 0.321 | 0.738 |
| K = 50 | 0.041 [0.030, 0.055] | 0.035 / 0.038 | 0.020 [0.005, 0.040] | 0.138 [0.093, 0.188] | 0.552 | 0.236 [0.182, 0.294] | 0.088 | 0.207 |
| K = 500 | 0.018 [0.010, 0.027] | 0.019 / 0.019 | 0.012 [0.000, 0.027] | 0.068 [0.035, 0.104] | 0.651 | 0.250 [0.198, 0.302] | 0.099 | 0.129 |
| b′ (K = 2,433) | 0.023 [0.014, 0.033] | 0.024 / 0.026 | 0.014 [0.000, 0.031] | 0.089 [0.051, 0.129] | 0.653 | 0.208 [0.159, 0.257] | 0.108 | 0.145 |
| c′ | 0.031 [0.021, 0.044] | 0.029 / 0.031 | 0.033 [0.010, 0.063] | 0.100 [0.058, 0.146] | 0.636 | 0.182 [0.137, 0.227] | 0.067 | 0.141 |
| c look-alike | 0.166 [0.143, 0.193] | 0.163 / 0.124 | 0.134 [0.087, 0.185] | 0.223 [0.162, 0.283] | 0.953 | 0.031 [0.017, 0.049] | 0.019 | 0.012 |
| d halves | 0.023 [0.015, 0.033] | 0.023 / 0.016 | 0.035 [0.011, 0.067] | 0.027 [0.005, 0.057] | 0.397 | 0.332 [0.279, 0.383] | 0.024 | 0.291 |
| d+ | 0.024 [0.016, 0.034] | 0.029 / 0.024 | 0.029 [0.010, 0.053] | 0.050 [0.022, 0.084] | 0.413 | 0.306 [0.255, 0.357] | 0.021 | 0.318 |
| e history | 0.014 [0.008, 0.021] | 0.019 / 0.017 | 0.046 [0.020, 0.081] | 0.021 [−0.007, 0.052] | 0.424 | 0.361 [0.312, 0.410] | 0.030 | 0.222 |
| f JPEG | 0.010 [0.005, 0.016] | 0.014 / 0.012 | 0.027 [0.007, 0.054] | 0.040 [0.009, 0.077] | 0.426 | 0.369 [0.319, 0.422] | 0.042 | 0.231 |
| FE header (ref.) | 0.000 [0.000, 0.000] | 0.000 / 0.000 | 0.005 [0.000, 0.015] | −0.005 [−0.015, 0.000] | 0.172 | 0.457 [0.386, 0.530] | 0.429 | 0.580 |

Paired steps at the camera threshold (difference of 5-seed means, same person draws):

| Step | halves flagged | untouched FRLL flagged | JPEG 50 − untouched | MorDIFF E7 pool flagged | miss FRLL landmark-4 | miss AR1 OpenCV R4 |
|---|---|---|---|---|---|---|
| b → b′ | −0.012 [−0.027, +0.001] | −0.071 [−0.121, −0.024] | +0.018 [−0.050, +0.085] | +0.122 [+0.070, +0.181] | −0.075 [−0.117, −0.039] | −0.024 [−0.058, +0.005] |
| c′ → c | +0.009 [−0.003, +0.021] | −0.026 [−0.051, −0.005] | −0.095 [−0.145, −0.048] | +0.023 [−0.025, +0.070] | −0.036 [−0.054, −0.017] | +0.016 [−0.005, +0.042] |
| c → d | +0.016 [−0.003, +0.036] | +0.089 [+0.041, +0.147] | −0.049 [−0.101, +0.001] | −0.185 [−0.241, −0.134] | +0.120 [+0.092, +0.148] | −0.042 [−0.073, −0.017] |
| d → e | −0.017 [−0.030, −0.004] | +0.021 [−0.016, +0.057] | −0.039 [−0.079, −0.001] | −0.015 [−0.067, +0.036] | +0.024 [−0.008, +0.054] | +0.003 [−0.001, +0.012] |
| e → f | −0.005 [−0.013, +0.003] | −0.004 [−0.029, +0.023] | +0.035 [+0.006, +0.066] | +0.080 [+0.048, +0.119] | −0.015 [−0.027, −0.002] | +0.001 [−0.000, +0.004] |
| a → e | −0.005 [−0.025, +0.013] | +0.045 [+0.000, +0.093] | −0.164 [−0.224, −0.105] | −0.132 [−0.191, −0.075] | +0.048 [+0.001, +0.092] | −0.044 [−0.080, −0.015] |
| a → f | −0.010 [−0.029, +0.007] | +0.041 [−0.009, +0.093] | −0.128 [−0.194, −0.068] | −0.052 [−0.111, +0.006] | +0.033 [−0.007, +0.071] | −0.043 [−0.079, −0.014] |

JPEG 90 and 70 increments at the camera threshold are small for every arm (a +0.007 / +0.039; c +0.005 / +0.053;
d −0.003 / +0.023; e −0.003 / +0.025; f −0.008 / +0.027). 204 photos per JPEG level, about ±3 points.

**JPEG reads (A10, registered; FRLL genuine photos under JPEG, 204 each; miss = FRLL-Morphs landmark-4 pooled morphs
at the same threshold; 5-seed means).** "own" = logit ≥ 0; "dev" = the camera-photo threshold. Read the paired
increments above, not these levels: the levels carry the offset between photo pools.

| Arm | own: jpeg90 / 70 / 50 / native flagged | own: miss | dev: jpeg90 / 70 / 50 / native flagged | dev: miss |
|---|---|---|---|---|
| a | 0.005 / 0.001 / 0.013 / 0.000 | 0.508 | 0.098 / 0.130 / 0.287 / 0.091 | 0.187 |
| b | 0.004 / 0.004 / 0.019 / 0.000 | 0.524 | 0.125 / 0.164 / 0.323 / 0.117 | 0.178 |
| bp | 0.015 / 0.023 / 0.103 / 0.014 | 0.208 | 0.046 / 0.110 / 0.270 / 0.046 | 0.104 |
| cr | 0.028 / 0.042 / 0.133 / 0.033 | 0.182 | 0.049 / 0.102 / 0.269 / 0.053 | 0.126 |
| c | 0.123 / 0.242 / 0.357 / 0.134 | 0.031 | 0.031 / 0.079 / 0.147 / 0.026 | 0.091 |
| d | 0.033 / 0.048 / 0.063 / 0.035 | 0.332 | 0.113 / 0.138 / 0.187 / 0.116 | 0.211 |
| e | 0.045 / 0.058 / 0.067 / 0.046 | 0.361 | 0.133 / 0.162 / 0.169 / 0.136 | 0.235 |
| f | 0.025 / 0.050 / 0.068 / 0.027 | 0.369 | 0.125 / 0.160 / 0.200 / 0.132 | 0.220 |
| d50 | 0.018 / 0.027 / 0.158 / 0.020 | 0.236 | 0.023 / 0.046 / 0.241 / 0.025 | 0.181 |
| d500 | 0.015 / 0.019 / 0.079 / 0.012 | 0.250 | 0.056 / 0.114 / 0.293 / 0.055 | 0.133 |
| FE header (reference) | 0.005 / 0.005 / 0.000 / 0.005 | 0.457 | 0.250 / 0.260 / 0.289 / 0.265 | 0.069 |

**History-matched genuine pools (A11, registered; E7 copies; flag rate of the pool and miss rate of that cell's
morphs at the same threshold; the three most-flagged pools per arm; 5-seed means).** Validity condition: arm (a)
flags more than 10% of some pool (MorDIFF E7: 0.267 at its own rule, 0.770 at the camera-photo threshold), so the
storage comparison counts for the frozen heads.

| Arm | own rule: pool flagged (morph miss) | camera-photo 5% threshold: pool flagged (morph miss) |
|---|---|---|
| a | mordiff:mordiff 0.27 (0.72); dim:dim_a 0.02 (0.72); dim:greedy_dim 0.02 (0.82) | mordiff:mordiff 0.77 (0.20); dim:fast_dim_ode 0.35 (0.29); dim:greedy_dim 0.35 (0.28) |
| b | mordiff:mordiff 0.21 (0.74); dim:fast_dim 0.05 (0.91); mad22:FaceMorpher 0.04 (0.00) | mordiff:mordiff 0.75 (0.15); dim:fast_dim 0.46 (0.39); dim:fast_dim_ode 0.46 (0.25) |
| bp | mordiff:mordiff 0.65 (0.14); mad22:FaceMorpher 0.36 (0.00); dim:fast_dim_ode 0.36 (0.16) | mordiff:mordiff 0.87 (0.03); mad22:FaceMorpher 0.61 (0.00); dim:fast_dim 0.60 (0.15) |
| cr | mordiff:mordiff 0.64 (0.14); mad22:FaceMorpher 0.44 (0.00); dim:dim_a 0.43 (0.14) | mordiff:mordiff 0.81 (0.07); mad22:FaceMorpher 0.57 (0.00); dim:fast_dim 0.55 (0.20) |
| c | mordiff:mordiff 0.95 (0.01); mad22:FaceMorpher 0.91 (0.00); dim:greedy_dim 0.90 (0.01) | mordiff:mordiff 0.84 (0.07); mad22:FaceMorpher 0.73 (0.00); dim:dim_a 0.72 (0.06) |
| d | mordiff:mordiff 0.40 (0.29); mad22:FaceMorpher 0.12 (0.00); dim:fast_dim 0.12 (0.46) | mordiff:mordiff 0.65 (0.10); mad22:FaceMorpher 0.31 (0.00); dim:fast_dim 0.30 (0.23) |
| e | mordiff:mordiff 0.42 (0.22); mad22:FaceMorpher 0.10 (0.00); dim:greedy_dim_s 0.09 (0.08) | mordiff:mordiff 0.64 (0.08); dim:greedy_dim 0.25 (0.14); dim:fast_dim 0.25 (0.17) |
| f | mordiff:mordiff 0.43 (0.23); dim:dim_a 0.07 (0.38); dim:dim_c 0.07 (0.27) | mordiff:mordiff 0.72 (0.06); dim:dim_a 0.25 (0.13); mad22:FaceMorpher 0.25 (0.00) |
| FE header (reference) | mordiff:mordiff 0.17 (0.58); dim:dim_c 0.01 (0.68); dim:fast_dim_ode 0.01 (0.63) | mordiff:mordiff 0.72 (0.04); dim:fast_dim_ode 0.38 (0.11); dim:fast_dim 0.37 (0.16) |

Registered falsifiers (descriptive, because no rebuilt arm passed the Laplacian acceptance; each with its cost):
- SMDD-T partner part, EER condition: (c) − (b) = −4.36 [−6.27, −2.81] points; |diff| < 1 with interval including 0
  does **not** hold. Cost: at the own rule arm (c) flags 0.95 of the MorDIFF history-matched genuine pool (b 0.21).
- SMDD-T halves part (registered EER-threshold reading): (d) − (c) = +4.19 points (≤ 5: passes the EER rule);
  halves flag rate at the AR1 EER threshold 0.072 → 0.026; the halves arm does not fail the registered rule. At the
  camera-photo threshold the halves flag rate rises 0.072 → 0.088 and untouched FRLL photos flagged rise 0.026 →
  0.116; the AUC of halves against camera photos falls 0.673 → 0.572. The AR1 halves are made by the training
  engine, so they are in-distribution for arm d.
- Partner-count dose curve: **not flat** (K = 50 is 2.8 points below K = 5 on the landmark cells, interval excludes
  0). Count is confounded with which partners (SMDD's five against random pool renders); the five-random arm is
  A12 item 11.
- SMDD-X frozen-head analogue (not the registered ViT-B/16 LoRA test): diffusion-cell E7 rise 11.3 (a), 7.2 (d),
  3.5 (e); the released FE header on the same features +3.3, so arm (e) brings our recipe to the release header's
  level (F4).
- Arm (f) vs (e) (JPEG copies added): JPEG 50 − untouched at the camera threshold +0.068 vs +0.032 (e → f +0.035
  [+0.006, +0.066]); no reduction.

## A12 CPU items 5 to 9 (post hoc; run 11 Nov 21:30 to 21:55; our frames, first-test data, arms fixed in advance)

**Item 5, heads refitted with the release (FZ1) recipe (H-new-4; `heads_fz1.py` → `heads/../heads_fz1/`, reads
`p3_fz1.json`, `a12_fixed_fz1.json`, `a12_partner_ref_fz1.json`).** Same features, compositions and seeds; recipe of
the MADation FE header without the flip (no flipped features exist; registered deviation). 5-seed means.

| Arm | landmark-7 EER native (ours) | diffusion-7 EER native (ours) | diffusion rise (ours) | landmark rise (ours) | untouched FRLL flagged, camera thr (ours) | JPEG 50 − untouched, camera thr (ours) | trained − KE (ours) |
|---|---|---|---|---|---|---|---|
| a | 8.29 [6.06, 10.67] (7.34) | 17.36 (20.70) | +6.68 [5.09, 8.16] (+11.32) | +1.72 (+2.59) | 0.192 (0.091) | 0.185 (0.196) | 4.93 (4.10) |
| b | 9.04 (7.61) | 17.42 (20.15) | +10.05 (+14.56) | +2.40 (+3.15) | 0.201 (0.117) | 0.232 (0.206) | 5.60 (4.42) |
| b′ | 4.35 (4.20) | 9.44 (9.02) | +8.56 (+17.04) | +2.20 (+3.41) | 0.158 (0.046) | 0.368 (0.224) | −0.63 (−1.15) |
| c | 3.32 (3.25) | 8.09 (7.18) | +12.87 (+21.42) | +2.67 (+3.72) | 0.098 (0.026) | 0.296 (0.121) | −0.55 (−0.58) |
| d | 5.49 (7.44) | 13.15 (14.39) | +3.40 (+7.20) | +1.08 (+1.85) | 0.250 (0.116) | 0.298 (0.072) | −0.30 (−0.33) |
| e | 7.65 (9.38) | 11.48 (13.69) | +0.03 [−1.15, 1.12] (+3.47) | +0.14 (+0.86) | 0.183 (0.136) | 0.134 (0.032) | 0.27 (−0.10) |
| f | 7.68 (8.45) | 12.01 (15.06) | −0.16 (+3.61) | −0.03 (+1.16) | 0.158 (0.132) | 0.158 (0.068) | 0.35 (−0.03) |
| FE header (release) | 8.37 | 19.51 | +3.33 | +0.60 | 0.265 | 0.025 | 3.46 |

Prediction (review): arm (a) diffusion rise ≤ +5 and the a → e reduction < 3 points; falsified if the rise stays
≥ +8. Reading: the rise is +6.68 [5.09, 8.16], so neither supported nor falsified; the a → e reduction is 6.65
points (not < 3). The recipe changes the size (arm a +11.3 → +6.7, still twice the release header's +3.3) but not the
pattern: history crossing still removes the rise (e +0.03). With the release recipe the fixed-threshold costs are
larger: untouched FRLL photos flagged at the camera threshold 0.10 to 0.25 for every arm, and the JPEG-50 increment
of e and f is +0.13 / +0.16 (ours +0.03 / +0.07). Partner trace under the release recipe: trained − KE 4.9 to 5.6
with the five, −0.75 to +0.35 without; DiD a − b′ 5.56 [5.46, 5.66]. Steps (landmark-7 native): b → b′ −4.69
[−6.73, −2.58], c′ → c −0.99, c → d +2.17 [+1.42, +3.11], d → e +2.16 [+1.33, +2.88], e → f +0.03.

**Item 6, Part 3 steps with the alignment border held equal (H-new-3; `a12_border.py` → `a12_border.json`).**
Border = EV1's zero fraction of each aligned frame. Landmark genuine frames have none (median 0.000). Two landmark
cells have border-free morph frames (corrected MAD22 OpenCV 984 and Webmorph 500 morphs, 100% < 0.005); the five
others carry a border (medians 0.05 to 0.26; FRLL FaceMorpher 0.26, OpenCV 0.19). Matched pairs cannot be formed in
the bordered cells (no genuine frame with a border); there each cell's morphs are split at the cell's median border.

| Step (native landmark EER, points) | registered (7 cells) | border-free cells (2) | bordered cells (5) | bordered, low-border half | bordered, high-border half |
|---|---|---|---|---|---|
| b → b′ | −3.42 [−5.19, −1.87] | −2.77 [−4.94, −0.69] | −3.67 [−5.38, −2.17] | −3.16 | −4.02 |
| b → K = 50 | −2.82 | −2.18 [−4.02, −0.02] | −3.08 | −2.94 | −3.00 |
| b′ → c′ | +0.18 | −0.30 [−1.36, +0.62] | +0.37 | +0.28 | +0.56 |
| c′ → c | −1.12 | −0.14 [−1.36, +1.12] | −1.51 [−2.38, −0.79] | −2.00 | −1.38 |
| c → d | +4.19 [+2.95, +5.62] | −0.25 [−2.01, +1.33] | +5.97 [+4.63, +7.54] | +5.98 | +6.15 |
| d → e | +1.94 | +1.20 [−0.05, +2.38] | +2.23 [+1.06, +3.31] | +3.33 | +0.93 |

Prediction (review): with the border held equal, b → b′ shrinks by more than half; falsified if it stays within 1
point. Reading: **falsified** for b → b′ (−2.77 on the border-free cells against −3.42). Not predicted: the landmark
cost of halves (c → d +4.19) is absent on the border-free cells (−0.25 [−2.01, +1.33]) and +6.0 on the bordered
cells, and the look-alike gain c′ → c is −0.14 there against −1.51. Only two border-free cells, both corrected
MAD22, so cell family and border are confounded; descriptive.

**Item 7, partner-level variance of SMDD evaluation-split error rates (H-new-6; `a12_partner_var.py` →
`a12_partner_var.json`; T-A subsample, whole files, 500 morphs per partner vs 1,000 genuine).**

| Release | EER per evaluation partner (img005071, img042475, img141280, img226436, img279570) | spread | pooled EER | one-way interval (keys) | two-way interval (keys x partners) | width ratio |
|---|---|---|---|---|---|---|
| MADation ViT-B/16 | 0.40, 0.15, 0.40, 0.15, 0.15 | 0.25 | 0.20 | [0.06, 0.40] | [0.00, 0.49] | 1.44 |
| MADation ViT-L/14 | 0.15, 0.00, 0.00, 0.00, 0.00 | 0.15 | 0.02 | [0.00, 0.11] | [0.00, 0.16] | 1.45 |
| MADation FE ViT-B/16 | 6.80, 2.20, 1.60, 1.55, 0.60 | 6.20 | 3.42 | [2.78, 4.00] | [0.98, 5.60] | 3.81 |
| MADation FE ViT-L/14 | 3.60, 1.00, 0.55, 2.00, 0.40 | 3.20 | 2.09 | [1.54, 2.51] | [0.49, 3.19] | 2.79 |
| MixFaceNet-MAD | 4.00, 2.40, 1.80, 0.55, 1.00 | 3.45 | 2.20 | [1.69, 2.90] | [0.92, 3.49] | 2.13 |
| FS ViT-B/16 (descriptive) | 4.60, 0.95, 1.15, 0.95, 0.80 | 3.80 | 1.62 | [1.19, 2.08] | [0.63, 3.29] | 2.99 |
| FS ViT-L/14 (descriptive) | 25.2, 16.75, 16.8, 15.2, 16.0 | 10.0 | 18.11 | [16.61, 19.61] | [14.93, 22.11] | 2.39 |

Prediction (review): spread > 5 points and two-way ≥ 3 x one-way; falsified if the spread < 2 points. Reading by
release: supported for FE ViT-B/16 (6.2, 3.8x); falsified for the two adapted MADation releases (spread 0.25 and 0.15;
their evaluation EER is near 0, a floor); in between for FE ViT-L/14 and MixFaceNet-MAD (spread 3.2 and 3.5, ratio
2.8 and 2.1). For the three releases with EER above 2%, an interval over first contributors alone is 2 to 4 times
too narrow when the partners are the units that repeat.

**Item 8, file names against image content (F11; `a12_names.py` → `a12_names.json`; 100 seeded morphs per split,
buffalo_l ArcFace).** The named second contributor is the most similar of the split's five partners for 97 of 100
training and 98 of 100 evaluation morphs (chance 20); mean cosine to the named partner 0.33 / 0.30 against 0.05 /
0.02 for the other four. The named first contributor is more similar than all 20 random renders for 100 of 100 in
both splits (cosine 0.56 / 0.51 against 0.03 / 0.02). In the 5 mismatches the morph is dominated by its first
contributor (cosine 0.56 to 0.69) and the named partner is weak but present (0.02 to 0.31); consistent with SMDD's
random warp factor. The file names describe the image content; Part 1 (conclusion 1) holds at the content level.

**Item 9, head logit against sharpness (H-new-2; `a12_sharp_slope.py` → `a12_sharp_slope.json`; seed-401 heads,
2,000 training images per class, Spearman ρ of logit with log Laplacian variance at 224 px, 500 image-bootstrap
draws).** Our recipe, morph / genuine class: a −0.06 / −0.01; b −0.10 / −0.02; K = 50 +0.05 / −0.04; K = 500
−0.03 / −0.03; b′ −0.02 / −0.02; c′ −0.08 / −0.01; c −0.07 / −0.05; d −0.02 / −0.29; e +0.25 / −0.37; f +0.29 /
−0.37 (release recipe within 0.09 of these). Prediction: ρ more negative from b → K = 50 → b′; falsified if |Δρ| <
0.05 from b to b′. Reading: **falsified** in the genuine class (Δρ +0.0004) and the opposite direction in the morph
class (−0.10 → +0.05 → −0.02, Δρ +0.08). Partner diversity does not make the heads lean on softness inside a class;
halves and history copies do (genuine-class ρ −0.29 to −0.37 in d, e, f).

## First LoRA fits (A9; ViT-L/14 M3L recipe, arm a, seeds 401 and 402, Athena 3545823_0/1; `p3_lora_vitl.json`)

Our frames, first-test data, arms fixed in advance; 2 of the 25 ViT-L/14 fits (the others wait on Athena). Means of
2 seeds [person bootstrap]; frozen-head arm a in brackets: landmark-7 native EER 2.62 [1.91, 3.24] (7.34), landmark
rise −0.29 (+2.59); diffusion-7 native EER 31.2 [28.8, 33.3] (20.7), diffusion rise −0.76 [−1.85, +0.44] (+11.32);
GAN-3 EER 21.3 (15.8). History-matched pools flagged at the own rule: 0.00 for every pool (frozen 0.27 MorDIFF).
A11 validity (rule as written: more than 10% of some history-matched pool at either threshold): **met**, through the
camera branch only (MorDIFF E7 0.85, seeds 1.00 / 0.71); the camera branch is uninformative on this bounded head
(‖w‖ 4.22, logits −4.2 to +3.9; camera threshold 0.07 / 0.13 logit above the camera-photo median), and the own-rule
branch is not met (0.00 on every pool). Camera-threshold cells of these fits (untouched FRLL 0.31, JPEG-50 FRLL 0.83)
are floor-calibrated; descriptive only. This head does not detect MorDIFF at all (native EER 51 / 39%, own-rule miss
100%), so its absent MorDIFF rise is no robustness either. Train hours 3.50 per fit.

## ViT-B/16 LoRA fits on the rented machine (A13): first registered reading (8 fits: a, c, e, f x seeds 401, 402)

One machine type (RTX 6000 Ada, rented; A13), A11 recipe and reads (`p3_lora_vitb.json`, `a12_fixed_vitb.json`,
`a12_partner_ref_vitb.json`). Our frames, first-test data, arms fixed in advance. **Arms e and f (and c as the
look-alike base) on benchmark cells are development exposure** (author's ruling of 12 Nov; README §1a), not benchmark
results of a proposed method. 2-seed means [person bootstrap]; seeds in parentheses.

| Arm | landmark-7 EER native | landmark rise | diffusion-7 EER native | diffusion rise | GAN-3 EER | MorDIFF E7 pool flagged, own rule | most-flagged pool, own rule |
|---|---|---|---|---|---|---|---|
| a release files | 2.76 [2.07, 3.47] | +2.26 | 6.40 (7.52, 5.28) | +18.04 [16.31, 19.96] | 23.91 | 0.20 (0.03, 0.37) | 0.21 |
| c look-alike | 5.29 [4.13, 6.46] | +13.39 | 15.12 | +29.09 [26.75, 31.48] | 20.88 | 0.90 | 0.96 |
| e history crossing | 2.24 [1.47, 2.85] | −0.30 | 13.76 | −3.10 [−4.69, −1.36] | 25.03 | 0.00 | 0.00 |
| f e + JPEG 90 / 70 | 2.38 [1.72, 3.04] | +0.02 | 12.70 | −1.21 [−2.77, +0.35] | 18.79 | 0.00 | 0.00 |

A11 validity: met as registered. MorDIFF pool at the own rule 0.20 (seeds 0.03, 0.37; seed 401's largest pool is DiM
fast_dim 0.05, so 1 of 2 seeds). The camera branch is uninformative on this bounded head. Seed spread for arm a from
PN1's eight reference retrains of the same recipe on the released SMDD (`p3_lora_pn1ref.json`; their manifest has no
MorDIFF / DiM rows): landmark-7 native EER 2.37 to 6.86 (SM1 a 2.56, 2.95), landmark rise +1.5 to +7.4 (SM1 +1.6, +2.9),
largest history-pool flag at the own rule 0.00 to 0.70 (SM1 0.05, 0.37); SM1's two seeds sit inside that range.

MorDIFF alone (2 seeds; native EER / history-matched EER / own-rule miss of MorDIFF morphs): a 7.4, 8.3 / 19.6, 20.1 /
0.39, 0.12; c 3.0, 2.0 / 13.7, 15.7 / 0.00; e 33.8, 47.1 / 23.5, 32.4 / 0.95, 0.99; f 31.9, 40.3 / 23.5, 27.9 / 0.97,
0.98.

Camera-threshold cells of every LoRA fit are **floor-calibrated; descriptive only**, with no between-arm statement
(threshold − camera-photo median: a 0.28 / 0.98, c 2.23 / 5.96, e 0.068 / 0.055, f 0.100 / 0.091 logit; floor table
below): untouched FRLL photos flagged a 0.110, c 0.105, e 0.201, f 0.049; JPEG 50 − untouched a +0.245, c −0.056,
e +0.515, f +0.120; FRLL landmark-4 miss a 0.020, c 0.184, e 0.002, f 0.150. At the own rule untouched FRLL photos are
never flagged by a, e, f (c 0.145), and landmark-4 miss is 0.48 / 0.50 / 0.44 (c 0.14).

Reading (2 seeds, our frames): the standard ViT-B/16 recipe on the SMDD release files rises +18.0 EER points on the 7
diffusion cells (MorDIFF alone +12.0: 7.9 → 19.9) when genuine photos carry the morphs' storage history. Development
exposure, not a method result: history-crossed fits (e, f) lose MorDIFF detection (native EER 34 / 47% and 32 / 40%;
own-rule miss 95 to 99%); their negative rise reflects that loss. Diffusion-7 native EER doubles (6.4 → 13.8).
Camera-threshold reads of these fits are floor-calibrated (threshold 0.06 to 0.10 logit above the camera-photo median
for e and f) and are not compared between arms. Signs that repeat within each seed: a's diffusion rise (+17.3, +18.8),
the a − e gap (about 21 points in both seeds), the MorDIFF collapse of e and f (all four fits); GAN-3 and flag rates
carry no claim (between-seed SD about 0.24 for a's largest pool flag).

Audit set (A12 item 10, H-new-5 on ViT-B/16): logits of these fits sit at a narrow ceiling (arm a, trained-partner
morphs mean 3.50, max 3.53), so the gaps are compressed: trained − KE a 0.045 [0.038, 0.053] (seeds 0.056, 0.033),
c 0.001 [−0.001, 0.002], e 0.001, f 0.003; DiD a − c 0.044 [0.037, 0.052]. Own-rule miss with every partner kind
≤ 0.3%. By rank the trace is clear (`a12_rank_vitb.json`, recomputed here; A14 definition): within-key AUC trained over
KE 0.757 [0.745, 0.768] for arm a (seeds 0.727, 0.786; b s401 0.814) against 0.53 to 0.59 without the five (c 0.533,
e 0.562, f 0.586); DiD a − c 0.224 [0.210, 0.237], a − e 0.194 [0.180, 0.209]. Mean gaps are compressed by the head's
±3.8 bound. The registered H-new-5 concerns ViT-L/14 (job 3547052; read by the rank rule A14).

**Calibration floor of every LoRA fit (post hoc, zero GPU; `a12_floor.json`).** Head = Linear on normalised features;
camera threshold = 95th percentile of the fit's AR1 FRGC/colorFERET R0 logits. Cells: source median minus threshold /
share flagged at the threshold.

| Fit | head norm ‖w‖ | bias | logit range | camera thr | thr − R0 median | FRLL photos: median − thr / flagged | JPEG-50 photos | MorDIFF native genuine | MorDIFF E7 genuine |
|---|---|---|---|---|---|---|---|---|---|
| ViT-B:a_s401 | 3.803 | -0.095 | -3.76 to 3.53 | -3.45 | 0.279 | -0.15 / 0.21 | +0.03 / 0.55 | +0.30 / 0.88 | +0.92 / 1.00 |
| ViT-B:a_s402 | 3.764 | -0.088 | -3.74 to 3.49 | -2.71 | 0.985 | -0.72 / 0.01 | -0.50 / 0.16 | +0.07 / 0.55 | +1.71 / 0.95 |
| ViT-B:b_s401 | 3.799 | -0.095 | -3.77 to 3.54 | -3.46 | 0.276 | -0.14 / 0.20 | -0.01 / 0.48 | +0.20 / 0.93 | +0.62 / 1.00 |
| ViT-B:c_s401 | 3.824 | -0.082 | -3.75 to 3.46 | -1.47 | 2.226 | -1.33 / 0.15 | -1.31 / 0.07 | +3.20 / 0.89 | +4.42 / 0.99 |
| ViT-B:c_s402 | 3.779 | -0.08 | -3.73 to 3.48 | 2.28 | 5.959 | -4.23 / 0.06 | -4.95 / 0.03 | -4.00 / 0.00 | -0.60 / 0.33 |
| ViT-B:e_s401 | 3.869 | -0.077 | -3.69 to 3.39 | -3.56 | 0.068 | -0.04 / 0.17 | +0.01 / 0.55 | +0.23 / 0.99 | +0.14 / 0.98 |
| ViT-B:e_s402 | 3.862 | -0.034 | -3.68 to 3.22 | -3.52 | 0.055 | -0.04 / 0.23 | +0.07 / 0.88 | +0.16 / 0.99 | +0.09 / 0.94 |
| ViT-B:f_s401 | 3.881 | -0.082 | -3.69 to 3.37 | -3.52 | 0.100 | -0.08 / 0.04 | -0.05 / 0.10 | +0.15 / 0.96 | +0.06 / 0.82 |
| ViT-B:f_s402 | 3.864 | -0.029 | -3.66 to 3.18 | -3.47 | 0.091 | -0.10 / 0.05 | -0.04 / 0.24 | +0.10 / 0.89 | +0.05 / 0.81 |
| ViT-L:a_s401 | 4.22 | -0.098 | -4.17 to 3.90 | -4.05 | 0.071 | -0.01 / 0.48 | +0.28 / 0.99 | +0.16 / 0.99 | +0.20 / 1.00 |
| ViT-L:a_s402 | 4.23 | -0.099 | -4.18 to 3.92 | -4.01 | 0.129 | -0.10 / 0.14 | +0.04 / 0.66 | +0.03 / 0.62 | +0.05 / 0.71 |
| PN1 ref:a_s1 | – | – | -3.73 to 3.46 | -2.73 | 0.956 | -0.50 / 0.04 | – | – | – |
| PN1 ref:a_s2 | – | – | -3.80 to 3.44 | -3.30 | 0.466 | -0.36 / 0.06 | – | – | – |
| PN1 ref:a_s3 | – | – | -3.79 to 3.50 | -3.46 | 0.299 | -0.24 / 0.02 | – | – | – |
| PN1 ref:a_s4 | – | – | -3.73 to 3.40 | -1.20 | 2.476 | -1.26 / 0.14 | – | – | – |
| PN1 ref:a_s5 | – | – | -3.70 to 3.44 | -2.37 | 1.300 | -0.69 / 0.03 | – | – | – |
| PN1 ref:a_s6 | – | – | -3.72 to 3.49 | -2.96 | 0.725 | -0.42 / 0.15 | – | – | – |
| PN1 ref:a_s7 | – | – | -3.81 to 3.48 | -3.32 | 0.445 | -0.15 / 0.11 | – | – | – |
| PN1 ref:a_s8 | – | – | -3.76 to 3.42 | -3.49 | 0.241 | -0.10 / 0.14 | – | – | – |

H-new-B, ρ part (Spearman of the flag rate with threshold − source median over all fit x source cells): −0.675 (131
cells; −0.719 over 101 cells without the duplicated FRLL photo sources); prediction |ρ| ≥ 0.8: not met, but flag rates
at the camera threshold are largely set by where the threshold sits on the floor.

## ViT-B/16 LoRA, full registered set (A13: 12 fits, arms a, b, b′, c, e, f x seeds 401, 402; `p3_lora_vitb12.json`, `a12_rank_vitb12.json`, `a12_fixed_vitb12.json`)

One rented RTX 6000 Ada; all 12 tars sha256-verified (`/mnt/t7/smad_next/SM1/results_rented/`). Our frames, first-test
data, arms fixed in advance; 2-seed means (seeds in parentheses). **c, e, f on benchmark cells are development
exposure**; a, b, b′ are audit arms of SMDD's construction (no row recommends them as a training set). Camera-threshold
cells are floor-calibrated and not read here.

| Arm | landmark-7 EER native | landmark rise | diffusion-7 EER native | diffusion rise | MorDIFF native EER / rise / own-rule miss | MorDIFF E7 pool flagged, own rule | GAN-3 EER | partner trace, within-key AUC trained over KE |
|---|---|---|---|---|---|---|---|---|
| a release files | 2.76 (2.56, 2.95) | +2.26 | 6.40 | +18.04 (17.3, 18.8) | 7.9 / +12.0 / 0.26 | 0.20 (0.03, 0.37) | 23.9 | 0.757 [0.745, 0.768] |
| b our tool, SMDD's five | 2.59 (2.26, 2.93) | +2.99 | 5.88 | +22.41 (20.3, 24.5) | 4.1 / +14.0 / 0.37 | 0.15 (0.00, 0.29) | 28.0 | 0.817 [0.806, 0.827] |
| b′ 2,433 partners | 3.06 (2.34, 3.78) | +5.31 | 9.70 | +20.35 (16.9, 23.9) | 4.4 / +10.0 / 0.04 | 0.53 (0.41, 0.64) | 35.1 | 0.567 [0.554, 0.579] |
| c look-alike (exposure) | 5.29 | +13.39 | 15.12 | +29.09 | 2.5 / +12.2 / 0.00 | 0.90 | 20.9 | 0.533 |
| e history (exposure) | 2.24 | −0.30 | 13.76 | −3.10 | 40.5 / −12.5 / 0.97 | 0.00 | 25.0 | 0.562 |
| f e + JPEG (exposure) | 2.38 | +0.02 | 12.70 | −1.21 | 36.1 / −10.4 / 0.98 | 0.00 | 18.8 | 0.586 |

Steps (paired person bootstrap): a → b (our engine instead of SMDD's files): landmark −0.16 [−0.61, +0.04], diffusion
rise +4.4 [+3.3, +5.2], GAN-3 +4.1. b → b′ (SMDD's five → 2,433 partners), the partner-diversity question on the
standard recipe (A12 item 12): landmark-7 native +0.47 [+0.01, +1.23], landmark rise +2.3 [+1.6, +3.1], diffusion-7
native +3.8 [+3.0, +4.4], diffusion rise −2.1 [−2.9, −0.5], GAN-3 +7.1 [+4.7, +9.1], MorDIFF E7 pool flagged at the own
rule 0.15 → 0.53. Partner trace: rank DiD b − b′ 0.250 [0.238, 0.262], a − b′ 0.190 [0.178, 0.202].

Reading (audit; 2 seeds): on the standard ViT-B/16 recipe the five SMDD partners leave a clear rank trace (0.76 to
0.82; 0.53 to 0.59 without them). On the standard recipe (2 seeds per arm) no partner-diversity effect is detected:
b → b′ landmark +0.5 (seed SD of 8 reference retrains 1.7), GAN-3 +7.1 (seed SD 9.9), history-pool flags 0.15 → 0.53
(reference range 0.00–0.70); the registered intervals resample persons only and leave out seed variance. Diffusion-7
native +3.8 repeats in both seeds (b 5.8 / 5.9, b′ 10.3 / 9.0) but has no reference spread. The frozen-head gain (−3.4,
5 seeds) is not shown to carry over to fine-tuning. Every arm trained on renders reacts to storage history on the diffusion cells (+18 to
+29); the only fits without the rise (e, f) do not detect MorDIFF (development exposure).

## A15: saved ViT-B/16 a, e, f on development data only (registered d84a1c2; `a15_read.json`)

Run 12 Nov 15:35 to 15:59 on a second rented RTX 6000 Ada (lease `sm1dev`, `drive_v2.sh devfresh`; deviation from
the registered machine sm1b, noted in `prereg.md`; the first attempt on sm1b scored nothing, README). Scorer with the non-benchmark reproduction check (256 stored AR1 camera-photo rows per
fit, max diff 0.0 for all 6); 6 tars sha256-verified in `/mnt/t7/smad_next/SM1/results_rented/dev/`, machine logs
back before RELEASE. No benchmark cell scored. Host bootstrap (536 FRGC / colorFERET hosts), B = 10,000; 2-seed means
[interval] (seeds).

| Fit | AUC X20 over AR1 R0 (native) | AUC X20 over REC20 (history-matched) | softening increment R0, 112.7 px / 61.2 px (logit) | paired AUC softened over raw R0, 112.7 / 61.2 |
|---|---|---|---|---|
| a | 0.999 [0.997, 1.000] | 0.745 [0.727, 0.763] (0.708, 0.782) | +0.22 [0.18, 0.28] / +1.44 [1.23, 1.66] | 0.80 / 0.95 |
| e | 0.997 [0.995, 0.999] | **0.510 [0.485, 0.536]** (0.508, 0.512) | +0.020 [0.004, 0.042] / +0.091 [0.029, 0.172] | 0.49 / 0.44 |
| f | 0.993 [0.990, 0.996] | 0.562 [0.538, 0.588] (0.571, 0.553) | +0.042 [0.013, 0.081] / +0.140 [0.068, 0.230] | 0.52 / 0.52 |

- **H-new-A (render-path matching removes the mix signal): supported as registered.** e's history-matched AUC 0.510
  (≤ 0.65) and a drops 0.254 from native to history-matched (≥ 0.15; near-automatic, since the native contrast mixes
  resolution, crop and file format). REC20 controls the generator path, not storage history (no resize, no JPEG), so
  the ladder tests render-path matching and says nothing directly about MorDIFF. The native contrast is near 1 for
  every fit, and so is REC20 over R0 (a 0.992, e 0.999, f 0.995): every fit scores one-person reconstructions as
  morph-like (median logit +1.2 to +2.5 against −3.6 for camera photos), a check that each fit flags generator output
  and a deployment cost (diffusion-processed genuine photos would be flagged), not morph detection.
- **H-new-E (e penalises camera detail): falsified as registered, but negligible.** e's mean increment is above 0 with
  the interval above 0 at both strengths (+0.020, +0.091), but the median increment is about 0 (−0.003 / −0.009) and
  57% / 65% of hosts decrease: e is close to indifferent to softening, with a small positive tail. Arm a's increment
  is far larger (+0.22, +1.44; its R0 sits on the floor, descriptive).
- **H-new-B, AUC part.** Reader deviation: `a15_read.py` used an unpaired estimator (all 200 x 200 cross-host pairs):
  e − f −0.030 [−0.046, −0.015] (112.7 px) and −0.080 [−0.102, −0.060] (61.2 px), undecided. The registered per-host
  paired estimator (share of hosts whose softened copy scores above its own raw photo; `a17_read.json`): e 0.430 /
  0.355, f 0.518 / 0.490; e − f −0.088 [−0.125, −0.052] and **−0.135 [−0.175, −0.097]** at 61.2 px: **falsified under the
  registered rule.** Caveat: 40% / 29% of e's per-host increments are below 0.01 logit in size, so the sign statistic
  partly reads noise near zero.

**Post hoc (review F1; recomputed here, `a17_read.json`): the SAME20 rung.** X20 and SAME20 are both mixes; only the
second person differs, so X20 over SAME20 is the identity-controlled contrast.

| Contrast | a | e | f | a − e |
|---|---|---|---|---|
| X20 over REC20 | 0.745 | 0.510 | 0.562 | +0.235 [0.215, 0.256] |
| SAME20 over REC20 | 0.606 | 0.356 | 0.413 | +0.250 [0.231, 0.271] |
| X20 over SAME20 | 0.658 | 0.645 | 0.639 | +0.014 [−0.006, +0.033] |
| X20 over SAME20, Laplacian-stratified (A17) | 0.595 | 0.621 | 0.617 | −0.026 [−0.050, −0.001] |
| X20 over SAME20, θ-stratified (A17) | 0.568 | 0.583 | 0.587 | −0.015 [−0.054, +0.023] |

**A17 (H-n3, registered f6b06e2 before computing):** H-n3a supported (Laplacian-stratified a − e −0.026, within ±0.03);
H-n3b undecided (θ-stratified a 0.568 [0.523, 0.612], e 0.583 [0.538, 0.627], f 0.587 [0.540, 0.632]: e and f above
0.58 at the point, every interval includes 0.58).

Reading: on development data (one generator, 2 seeds), history crossing removes arm a's separation of mixed renders
from one-person reconstructions, for two-person (X) and one-person (SAME) mixes alike (a − e +0.235 and +0.250). It
does not change the identity-controlled contrast X vs SAME (a 0.658, e 0.645; a − e +0.014 [−0.006, +0.033]), which no
arm lifts above one sharpness statistic (face-box Laplacian, 0.695). Every fit still scores one-person reconstructions
as morph-like against camera photos (0.99+). What the remedy removes is a mixing/render-path signal, not shown
second-identity detection. Arm a's 0.745 is not face-box sharpness or file size (removing both from its score raises
its AUC; review F2): a reads mixing in the latent path. The cleanest statement in A15: a = e on X vs SAME.

## A18 parallel arm: frozen-feature probe on our own diffusion ladder (registered d2a0b49, 12 Nov 23:06; `a18_probe.json`)

Development data only. Logistic probe on frozen CLIP (clip_mad) and DINOv2 features, trained on X20 vs SAME20 of DG1
shards 0–5, scored on shards 6–7 (133 X20, 134 SAME20, 55 partner cycles); incremental read over the fixed floor
(θ, face-box Laplacian, PNG bytes, asymmetry, d), cross-fit on test partner-cycle folds, partner-cycle bootstrap.

| Features | probe AUC X20 over SAME20 | floor F | F + probe | ΔAUC over F | floor F_img (no θ) | ΔAUC over F_img | registered reading |
|---|---|---|---|---|---|---|---|
| CLIP (clip_mad) | 0.963 [0.941, 0.983] | 0.901 | 0.962 | **+0.061 [0.030, 0.092]** | 0.778 | +0.180 [0.127, 0.233] | falsified: information beyond the measured traces |
| DINOv2 | 0.963 [0.938, 0.986] | 0.901 | 0.970 | **+0.069 [0.038, 0.101]** | 0.778 | +0.180 [0.129, 0.231] | falsified |
| (unflagged rows) | 0.964 / 0.964 | 0.900 | 0.962 / 0.969 | +0.062 / +0.069 | 0.788 | +0.168 / +0.169 | falsified |

Reading (FRGC test hosts, one generator, one render platform): frozen foundation features carry X-vs-SAME information
beyond simple statistics and the noise-angle θ; unmeasured render traces are not excluded. Post hoc: over the
noise-map band floor, +0.001 (CLIP) / +0.003 (DINOv2) (review of 13 Nov).

## A16 (H-n1) and A18 (H-n2): registered readings (rented RTX 6000 Ada sm1dg, deviation D1; development data only)

Run 13 Nov 01:44 to 06:16 on lease sm1dg (A18 first, then A16; one GPU user at a time). All 3 A18 tars and all 6 A16
tars sha256-verified with the machine logs before RELEASE (06:16). A16 reproduction check: max diff 0.0 on 6 of 6.
No benchmark row scored.

**A18 (H-n2): the standard ViT-B/16 recipe trained on our own ladder (arm RS: X20 vs REC20 + SAME20, shards 0–5),
read on unseen shards 6–7 (`hn2_read.json`).** Training-row AUC 0.994, 0.996, 0.996 (about 1,330 epochs).

| Read (2-seed mean 401, 402) | all rows | without flagged rows |
|---|---|---|
| network AUC X20 over SAME20 | 0.989 [0.980, 0.997] | 0.989 |
| floor F (θ, Laplacian, PNG bytes, asymmetry, d), cross-fit | 0.901 | 0.900 |
| F + network logit, cross-fit | 0.978 | 0.977 |
| **ΔAUC over F (primary)** | **+0.077 [0.040, 0.114]** | +0.077 [0.040, 0.116] |
| ΔAUC over the image-statistics floor F_img (0.778) | +0.191 [0.137, 0.246] | +0.180 |
| 3-seed mean ΔAUC (stability) | +0.077 [0.041, 0.113] (seeds 0.081, 0.073, 0.079) | +0.079 |
| secondary: Laplacian- / θ-stratified X20 over SAME20 | 0.987 / 0.961 (s401); 0.982 / 0.972 (s402); 0.986 / 0.967 (s403) | |
| secondary: X20 over REC20 / SAME20 over REC20 | 1.000 / 0.88, 0.77, 0.88 | |

**Registered reading: falsified (signal beyond measured traces).** Outcome sentence: "With this generator and this
recipe (6,250 steps on 1,205 images, about 1,330 epochs, 2 seeds; FRGC, single render platform), the network adds
X-vs-SAME information beyond the measured traces (θ, sharpness, size, asymmetry); unmeasured render traces are not
excluded." Post hoc (review, shard 6 with saved noise maps, 133 rows): adding the band cosines and the low-pass cosine
of the two inverted noise maps to the floor raises it to 0.986 (0.992 when fit on shards 2–5) and the network's
increment to −0.006 [−0.018, +0.005]; the frozen probes' increments also vanish. So the network's X-vs-SAME signal is
not shown to exceed the similarity of the two noise maps, which is itself caused by input similarity; no
second-identity reading is shown. Training on SMDD and on this generator are not compared at equal data (arm R
dropped). **WITHDRAWN (13 Nov): "a two-person signal is learnable on this generator when the training contrast asks for
it, and the SMDD-trained recipes do not use it"** (review F1, F3). Supported version: the recipe trained on our ladder
separates two-person from same-person mixes of unseen persons at 0.99, beyond the registered floor (+0.077); post hoc,
nothing beyond the similarity of the two noise maps (floor 0.99); no second-identity reading shown; SMDD and this
generator not compared at equal data (arm R dropped).

**Post hoc addendum, recomputed by the owner (`a19_floor.json`; A19 note; shard 6, 66 X20 / 67 SAME20, 23 partner
cycles).** Cross-fit on shard-6 cycles: floor F 0.879, F + network ΔAUC +0.088 (reproduces the full-test effect);
F + band cosines + low-pass: floor 0.986, ΔAUC −0.006 [−0.018, +0.005] (3-seed −0.003); + semantic-code cosine: floor
0.985, ΔAUC −0.005 [−0.015, +0.007]. Extended floor fit on training shards, applied to shard 6, then combined with the
network logit (cross-fit on shard-6 cycles): shards 2–5 (535 rows) floor 0.992, ΔAUC −0.005 [−0.010, +0.000]; with the
shard 0–1 codes fetched from Athena (803 rows) floor 0.995, ΔAUC −0.004 [−0.010, +0.004] (3-seed −0.002). Adding shards
0–1 changes nothing material: the floor rises 0.992 → 0.995 and the increment stays at about zero.

**A16 (H-n1): saved SMDD-trained ViT-B/16 a, e, f on the DG1 rungs (`a16_read.json`).** 2-seed means, host bootstrap.

| AUC | a | e | f |
|---|---|---|---|
| FRESH1_20 over REC20 | 0.337 [0.319, 0.354] | 0.241 | 0.289 |
| NOISES20 over REC20 | 0.556 [0.539, 0.573] | 0.311 | 0.365 |
| NOISEX20 over NOISES20 | 0.572 [0.555, 0.589] | 0.595 | 0.585 |
| SEMX20 over SEMS20 | 0.598 [0.576, 0.620] | 0.548 | 0.557 |
| MIR20 over REC20 (descriptive) | 0.675 | 0.442 | 0.497 |

Registered reading (arm a): **undecided** (FRESH1 and NOISES over REC are not ≥ 0.70, nor both ≤ 0.55; SEMX over SEMS
0.60 is not ≥ 0.70). Not predicted: the fresh-noise renders score below the one-person reconstruction for every fit
(a 0.34, e 0.24, f 0.29), as do e's and f's noise-only renders (0.31, 0.36; a 0.56, seeds 0.50 / 0.61). The
reconstruction is the smoothest rung (median face-box Laplacian 87.5 against 103 and 128), consistent with the heads
reading smoothness as morph-like (partial explanation; A19 H-N4 below tests it). The host-bootstrap intervals ignore
seed variance (NOISES over REC seeds 0.50 / 0.61). The mix-type contrasts (NOISEX over NOISES, SEMX over SEMS) sit at
0.55–0.60 for every arm.

## A19 follow-ups (registered 71a08f6 before computing; development data only; CPU)

- **H-N4 (A16 smoothness; `a19_hn4.json`): falsified.** FRESH1_20 over REC20 stratified by face-box Laplacian quintiles,
  2-seed means: e 0.248 [0.226, 0.268] (raw 0.241), a 0.357 (raw 0.337), f 0.299 (raw 0.289). Holding sharpness equal
  barely moves the below-reconstruction ranking, so smoothness does not explain it.

## A12 items 11 and 13 (post hoc; Athena features 3546033; our frames, first-test data, arms fixed in advance)

**Item 11, five random pool partners (H-new-1; arm d5, 5 seeds; `p3_full.json`, `p3_fz1.json`).** Landmark-7 native
EER: d5 5.07 [3.52, 6.78] (seeds 4.84 to 5.21) against SMDD's five (b) 7.61, K = 50 4.79, b′ 4.19; b → d5 −2.54 [−4.21,
−0.88], d5 → K = 50 −0.29 [−1.31, +0.89]. Release recipe: d5 5.04, b → d5 −4.00 [−5.88, −2.00]. Diffusion-7 native 13.5
(b 20.2, K = 50 9.7); diffusion rise +11.0 (b +14.6); MorDIFF E7 pool flagged at the own rule 0.46 (b 0.21, K = 50
0.55). Partner trace of d5 on the audit set (its five are not audit partners) 0.16 [−0.02, 0.35]. Prediction: landmark-
7 ≥ 6.5%; falsified if ≤ 5.5%. Reading: **falsified** (5.07). One alternative draw of five, so the variance between
partner sets is not estimated; whatever improves native EER here also raises history-pool flags.

**Item 13, softened AR1 copies at 112.7 and 61.2 px target inter-eye distance (frozen heads; `a12_af0soft.json`).**
Flag rate of 200 softened camera photos (R0) at the head's camera threshold, against the same hosts unsoftened (raw
photos; the softened copies are aligned frames, so the increment mixes alignment and softening). Increment 112.7 /
61.2 px: a +0.11 / +0.18; b +0.09 / +0.20; d5 +0.17 / +0.23; K = 50 +0.05 / +0.13; b′ +0.06 / +0.17; c +0.11 / +0.28;
d +0.11 / +0.19; e +0.05 / +0.03; f +0.04 / +0.04; FE header +0.10 / +0.19 (release recipe: e +0.05 / +0.04, f +0.05 /
+0.04). Softened OpenCV R4 morphs missed at the same threshold: 0.01 to 0.04 for every arm. Frozen heads are unbounded,
so these increments are not floor reads. Development data (AR1 / AF0), not benchmark cells.

## A12 / A14 / A15 items still open

10 for ViT-L/14 (job 3547052, rank read A14). 12 (ViT-B/16 fits of b and b′): done (all 12 ViT-B/16 fits read above). A15: done (above).

## Checks

- Landmark pass reproduces the stored if106 points on SMDD genuine renders: max 0.014 px over 4 renders (smoke;
  `lm_check_pool_limit8.json`).
- Feature path (`feat_check.json`, `feat_check_fp32.json`): the timm QuickGELU tower with the cached OpenAI weights is
  identical to the FE ViT-L/14 release tower (max weight difference 0.0). The FE release header on our features vs
  the existing A12REL FE ViT-L/14 scores on 8 FRLL frames: max |Δ probability| 0.0062 with TF32 (0.0046 in fp32);
  **the registered tolerance 1e-3 is missed**. All 8 values agree to about 0.03 logit and in rank. TF32 vs fp32 on the
  DGX alone differ by up to 0.002, so the residual is read as platform numerics, not a pipeline difference; not
  verified further. TF32 kept as registered. This affects only the reference row.
- Shrink step for arm (e) (`shrink_verify.json`): `a47_data._one` (sha256 fcd48e1a…, prep_eval.py 374408ab…, call
  `prep_eval.degrade(img, "R", scale=0.3125)`, INTER_AREA 256 → 80, lossless PNG) reproduces the stored a47 copies of
  8 genuine renders byte for byte.
- Engine wrapper (DGX test of the WCSS task, `wcss/test_c/res`): wrapper morph = unchanged 78 command line, max
  difference 0 on 8 + 8 pairs; 0.5 hA + 0.5 hB vs morph at most 0.5 grey level (asserted <= 1 on every pair).
- A12 item 1 reader: the registered trained − U values are reproduced from the same score files (arm a 5.79,
  ViT-B/16 crop 1.72), and the reviewer's numbers (seed 401, 4,000 draws) agree with the 10,000-draw values.

## Run log

- 16:41 WCSS CPU task `SM1_cpu_c` staged; job 6301971 stale (WCSS unreachable since 16:54).
- 17:48 to 18:45 builds on the rented CPU machine leaseB (96 workers, nice 19); 21:15 `armd5` (A12 item 11) built
  there as an overlay task on pack b (95 s, 0 failures; leaseB = DGX references on 8 rows).
- Athena (A100 40 GB): 3544208 feature smoke, 3544789 LoRA smoke, 3545820 full features, 3545893 JPEG features,
  3545823_[0-19] + 3545894_[20-24] ViT-L/14 fits (tasks 0 and 1 running since about 19:55; the rest pending,
  "ReqNodeNotAvail", 23 nodes failed and 13 reserved at 21:05), 3545956 → 3545957_[0-9] ViT-B/16 fits (pending),
  3546033 A12 features (MODE a12), 3546034_[0-3] ViT-B/16 fits of b, b′.
- DGX: whole-file Part 2 pass 20:55 to 21:13 (1 process + 2 loader workers, OMP 2, nice 10); A12 items 1 to 3 single
  processes under the 2-process limit.

## Not verified / caveats

- Every rebuilt-arm number is descriptive: no arm passes the Laplacian acceptance (inside strata 0.89 to 0.96).
- T-A / T-B use the registered 7,810-image subsample and the whole-file path (A6, A8), not the releases' crops.
- Our engine differs from SMDD's dlib tool (fixed warp factor 0.5 vs random in [0, 1]); the audit and rebuilt
  morphs are ours. The bridge says our engine's morphs score like SMDD's own for the adapted releases (±0.2 logit).
- KE is a better reference than U but not neutral (on heads without the five, trained − KE is −1.15 to −0.03).
- The FE header reproduction of the A12REL scores missed 1e-3 (0.0062); platform numerics, not verified further.
- Origin of the `os25k_m_t` / `os25k_m_e` folders on disk is not recorded; the names agree with the content on
  100 morphs per split (A12 item 8), not on all 30,000.
- The expression check is a geometry substitute trained on FRLL photos (domain shift); the pixel probe did not run.
- LoRA fits: 2 of 25 ViT-L/14 (Athena) and all 12 ViT-B/16 (rented RTX 6000 Ada) are read; 2 seeds per arm cannot
  estimate flag rates; LoRA heads are bounded (±3.8 to ±4.2), so fixed-threshold cells are floor reads.
