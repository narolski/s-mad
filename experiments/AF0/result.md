# Alpha-field probe on frozen features (AF0): result

Owner's page. Facts only; the lead draws conclusions. Status: first pass running (numbers below are filled in as
they arrive). Pre-registration: `experiments/AF0/prereg.md` (unchanged).

Terms used here. The landmark ladder (AR1) rungs, in words: R0 = the untouched aligned camera photo; R1 = the camera
photo with the benchmark's shrink-and-enlarge history (existing E7 frames, FRLL only); R2 = the landmark tool run on one
photo (host with itself); R2w = warp-only image (host warped to the mean shape of host and a second photo of the same
person, texture from the host only; added by the AR1 owner); R3 = same-person morph (two photos of the host); R3m =
mirror self-morph (host with its mirror image); R4 = two-person morph (host with another person); NC = the reverse
same-person morph (negative control). "Zero-field image" = an AF0 pair warped to the mean shape and blended with
a(x) = 0 everywhere, i.e. the host warped, no texture from the partner: it is the AF0 training analogue of R2w.

## Build verification

- Engine: `scripts/68_hires_morph.py` (sha256 71643aad…), loaded through `scripts/78_tool_morph.py` (sha256 b8a389f1…)
  exactly as 78 loads it; `src/AF0/af_morph.py` runs the unchanged `hm.morph` and records its own two float32 warped
  images and its triangles while it runs (wrapper around the module's `_warp_tri`), then blends
  `clip((1 - a) * W_A + a * W_B)` with the engine's own clip and uint8 cast. No warp, blur, resize or compression code
  was added.
- a(x) = 0.5 everywhere vs the unchanged engine, 8 pairs: maximum absolute pixel difference **0** on every pair
  (0 differing pixels), both against a fresh in-process `hm.morph` call and against the PNGs written by the
  `78_tool_morph.py` command line (`verify_u50.json`, `verify_u50_vs_78cli.json`). The zero field equals the engine's
  own warped host image exactly (8 of 8).
- Field definition outside the face hull: the engine triangulates the whole frame through 8 added frame vertices
  (4 corners, 4 edge midpoints) and blends every pixel at 0.5. Here those 8 vertices carry the mean of the field over
  the 106 landmark vertices, and triangles between the hull and the frame interpolate between hull values and that
  mean, so the field is continuous (no seams); for uniform fields it is the constant (0.5 reproduces the engine).
  Pixels left uncovered by the engine's triangles: 0 in every image built so far.

## Counts

- Persons (`pairs_summary.json`): the AR1 candidate set (record's 73_delin_align frames with 106-point `.tem`,
  imported unchanged from `src/AR1/pool.py`) minus the 536 AR1 hosts / partners: 663 persons with at least one
  neutral photo after AR1's pixel-duplicate rule (164 duplicates dropped): colorFERET 613 (train 490, val 123),
  FRGC 50 (train 40, val 10); 715 neutral photos. No overlap with AR1 persons, no train/validation person overlap, no
  FRLL person. FRGC is small because AR1 took 427 of the FRGC persons in the candidate set; the FRGC val10 persons
  (sealed VAL-X) were not used.
- Images: 5,000 alpha-field morphs, equal shares over the five field types and the two databases (train 4,000 =
  5 x 2 x 400; validation 1,000 = 5 x 2 x 100), plus the 715 unprocessed photos (train 569, validation 146) with an
  all-zero map. Same-database pairs only, partners from the same split.
- Build speed: 1,165 images per minute at 6 processes (wave 1, 792 images in 40.8 s); the remaining 4,200 were built
  at 57 per minute with 2 processes while the machine's load average was 80 to 146.

## First small pass (DINOv3 ViT-L/16 at 512, ridge head, wave-1 images)

Written at about 16:40 CET as soon as the numbers existed. Training: 600 alpha-field morphs (train persons, 120 per field
type) + 569 unprocessed photos, all 1,024 patches per image; ridge on standardised tokens, lambda by 3-fold CV over
training host persons. Validation: 200 morphs + 146 photos of the validation persons.

| Metric (fixed threshold) | Value [95% interval] | Against the threshold |
|---|---|---|
| F1: within-image Spearman, predicted vs true a, patches inside the face hull, gradient + bump images (80 images, 44 host persons) | 0.275 [0.235, 0.312] | below 0.4 (pass mark), above 0.2 (drop mark): neither |
| F1, all 1,024 patches | 0.221 [0.185, 0.255] | — |
| F2: landmark ladder (AR1), FaceMorpher, R2 vs R4, 536 hosts | 0.9992 [0.9968, 1.0000] | at least 0.85 with lower bound above 0.75: met |
| Same, R2w vs R4 (lead's main contrast) | 0.9966 [0.9908, 0.9991] | — |
| Same, OpenCV R2 vs R4 / R2w vs R4 | 0.9970 [0.9920, 0.9997] / 0.9948 [0.9875, 0.9988] | — |

Descriptive, same head (AUC, higher rung positive; AR1's pigeonhole person bootstrap):
FaceMorpher R3 vs R4 0.853 [0.820, 0.883], R2 vs R3 0.977, R3m vs R4 0.747 [0.709, 0.786];
OpenCV R3 vs R4 0.830 [0.795, 0.861], R3m vs R4 0.726 [0.687, 0.764]. FRLL pool (102 hosts): R2 vs R4 0.9996
(FaceMorpher), 0.9974 (OpenCV); R3 vs R4 0.948 / 0.932. NC vs R3 is exactly 0.5 because both tools return the same
image for tool(S, H) and tool(H, S). Mean image score (validation): photos 0.030, zero-field 0.073, u25 0.273,
u50 0.319, gradient 0.266, bump 0.244.
Genuine-photo shifts in R0 standard deviations (part of F3, descriptive at this stage): R0 -> R2 0.076
(FaceMorpher), 0.000 (OpenCV); R0 -> R2w 0.726 [0.674, 0.792] (FaceMorpher), 0.299 [0.274, 0.328] (OpenCV).
Source: `metrics_dinov3_512_first.json`; predictions `/mnt/t7/smad_next/AF0/heads/dinov3_512/first/`.

## Lead's additions, registered before any of their numbers existed (11 Nov, afternoon)

### Fact recorded by the lead
The landmark ladder's (AR1) R2 rung is pixel-identical to the source photo for OpenCV and within 1 grey level for
FaceMorpher, so R2 is effectively R0. Every F2 / F3 number is therefore also reported against R2w (warp-only), and
R2w vs R4 is the main "processed genuine image vs morph" contrast for landmark tools.

### Clean-negative test (CN0), registered by the lead
On mean-pooled frozen CLIP ViT-L/14 tokens (DINOv3 as a second line), a logistic head on R2 vs R4 of the landmark
ladder (AR1), trained on one tool and tested on the other, 5 folds by person. Read (a) the rate at which it flags the
untouched source photos of the test persons and the FRLL E7 genuine photos, at the threshold that flags 10% of the
test persons' R2; (b) the best single-cue AUC for R2 vs R4 among simple cues (the `cue_floor` statistics, which run
unchanged; plus PNG byte size). Fixed verdict: the image-level class definition fails if (a) exceeds 20% on either
genuine set or any single cue exceeds 0.80; it stands if both rates are at most 15% and no cue exceeds 0.65; otherwise
mixed. Repeated with R2w as the negative class; the same reads (a) for the dense head's mean prediction.

### Mirror distance (free rider), registered by the lead
Features of the left-right flipped image (lossless flip) for the landmark ladder images and the benchmark landmark
cells; score = raw distance between the image's tokens and the flipped image's tokens at mirrored token positions,
no training. AUC for R2 vs R4, R2w vs R4, R3 vs R4 per tool, and R0 vs R1 on FRLL (expected near 0.5). Falsifier
fixed by the lead: no value for landmark morphs if R2 vs R4 is below 0.60; not history-blind if FRLL R0 vs R1
exceeds 0.60.

### AF0 wave 2 (ghost-energy target), registered by the lead before its numbers existed
Why: the nominal mixing fraction a(x) is not identifiable where the two warped source images agree (smooth skin on
both); blending leaves no trace there at any a. What is physically in the image is the foreign layer a·(W_B − W_A).
Changes (everything else as in the prereg):
1. Target "ghost energy" per patch: g = 4·a·(1 − a) · (standard deviation over the patch of (W_A − W_B)), divided by
   the patch's own contrast (standard deviation of the output image in that patch plus a small constant), computed
   from the two warped images the engine already has (numpy only, no image written). Also a simpler variant
   D = a-weighted mean absolute difference |W_A − W_B| per patch. Both are exactly zero for any image made from one
   capture.
2. Negatives with all-zero maps: both warped halves W_A and W_B of every pair (same warp, frame and storage as the
   morph), the unprocessed photos, and the uniform-zero field images.
3. Image score: mean of the highest tenth of predicted patches inside the face hull, beside the plain mean.
4. Report per region: inner face (eyes, nose, mouth hull) and periphery (hair outline, ears, collar) separately.
5. Compare the three targets (alpha, ghost energy g, plain disagreement D) with the same heads and backbones on:
   within-image rank correlation; the landmark ladder contrasts (warp-only vs two-person morph, same-person vs
   two-person morph, mirror self-morph vs two-person morph, per tool, held-out tool); the graded mixing set; the shift
   of genuine photos from native to E7; the stress test F4; and the benchmark families FRLL-Morphs AMSL and WebMorph
   beside the released MADation ViT-L/14.
Fixed falsifier for wave 2: the ghost-energy head fails if warp-only vs two-person morph on FaceMorpher images is
below 0.75, or if the genuine native-to-E7 shift exceeds 0.3 standard deviations; it brings no gain if it is neither
at least 0.03 AUC better than the alpha head on same-person vs two-person morph nor lower in the E7 shift.

### AF0 wave 3: controls, registered by the lead before their numbers existed
Background (lead, from a vetting round of three hostile reviewers; `ideas/CONSOLIDATED_v2.md` sections 1 and 3): the
probe's pass marks can be met by softness alone. Measured by a reviewer: a two-person morph has 0.52 times the
Laplacian variance of its own two warped halves, and that one number separates morph from halves at AUC 0.76 at
512 px and 0.87 at 224 px; the contrast-normalised ghost target of wave 2 is highest on flat skin (0.97 against 0.73
on eyes and mouth); a mirror self-blend carries 40 to 76% of the two-person target value; the mean-absolute-difference
target is 74% smooth tone mismatch; stored halves have black bands where the source does not cover the frame, and
morphs show half-dark bands there.
Controls (all on cached features and saved predictions; CPU):
1. Sharpness floor: AUC of Laplacian variance alone (and of the best of the simple statistics already computed) for
   every reported contrast; every head's AUC printed as excess over that floor.
2. Target sanity for each target variant: median value on the flattest and the busiest quartile of in-hull patches,
   rank correlation with the patch's own contrast, and the same-person and mirror ratios. A fourth target that
   excludes flat regions (e.g. the disagreement of the two halves' local gradients, or the disagreement restricted to
   patches above the median contrast); a target is accepted only if flat is below busy and the contrast correlation
   is below 0.3 in absolute value.
3. Template baseline: correlation of each validation map with the mean training target map; map correlations after
   removing the template. Pair swap: predicted map against its own target minus against the target of another morph
   with the same host (lower bound above 0.10 required). Shuffled-map control: refit the per-patch head with target
   maps shuffled between positive images; if image-level AUC and the genuine native-to-history-matched shift are
   unchanged, the map is decoration.
4. Five-arm ablation, same backbone and images, one global mixing weight: (a) image-level label with camera photos as
   negatives; (b) image-level label with warped halves as negatives; (c) constant map inside the face hull with
   halves; (d) measured-disagreement map with halves; (e) measured-disagreement map with camera photos only. Read
   held-out-tool AUC, the history shift under mean and top-tenth pooling, and the F4 stress-test drop for each. Fixed
   reading: the map earns its place only if (d) beats (b) by at least 0.03 AUC or halves the history shift.
5. Border: blank the same out-of-coverage region in both classes before feature extraction (constant-colour blanking)
   for one rerun of the main contrast, and report the change.
6. Pooling audit from saved predictions: history shift under mean, top-tenth and median pooling; where the top-tenth
   patches lie on genuine photos.
7. FaceMorpher numbers are descriptive only (its morph pastes the face onto a double-exposed surround); the
   OpenCV-style engine decides; the approved Poisson set `/mnt/t7/smad_heldout/h1_poisson` (unseen CASIA persons,
   both classes same source and border) is added as an unseen-tool, unseen-source test for every head.
No blurred or resized negatives are built (sharpness-matched negatives need the author's yes).

### AF0 wave 4: softened examples, registered by the lead before its numbers existed
The author approved teaching the detector that softness is not blending ("Let's teach that softness is not blending,
yes"). Scope: the EXISTING shrink-and-enlarge path (the registered history-matching step that produced the E7
copies, as run on the SMDD renders for the earlier morph-free experiment, A47 part I-3, and the a37_restore path) may
be run UNCHANGED on training photos, warped halves and our own morphs. No other blur, resize or compression code;
prep_eval.py and prep_gtest.py are not edited; the exact function, parameters and code hash are recorded, and the
call is verified on 8 images to reproduce an existing registered copy bit for bit before use.
(1) Softened negatives: each unprocessed photo and each warped half passed through that path, target map all zero.
(2) Softened positives: each morph passed through the same path, target map unchanged; two or three of the
registered strengths if the path has them, otherwise the one registered strength.
(3) Refit the heads of the five-arm ablation (wave 3) with these added and report: held-out-tool AUC against warped
halves and against softened halves, the sharpness floor for each contrast, the native-to-history-matched shift of
FRLL genuine photos (FRLL stays evaluation only), the flag rate on softened genuine photos at the 5% threshold, and
the F4 stress test.
Fixed reading: softened training earns its place if the flag rate on history-matched FRLL genuine photos at the 5%
threshold falls to at most 10% while held-out-tool AUC against warped halves drops by no more than 0.05 and stays
above the sharpness floor by at least 0.05.

#### Wave 4 path verification (done before any softened image was built)
`src/AF0/soften.py verify` (`wave4_verify.json`): prep_eval.py at its pin 374408ab… imported unchanged.
(a) `prep_eval.degrade(img, "R", scale=0.3125)` on 8 SMDD renders reproduces the stored A47 I-3 copies (80 x 80)
bit for bit (maximum absolute difference 0 on 8 of 8). (b) The full E7 branch (native inter-eye distance from
`prep_eval.kps`, `degrade(img, "R", scale = family median / native)`, then `prep_eval.align`) on 8 FRLL raw photos
reproduces their registered `*_resmatch_{amsl,opencv}.png` eval frames bit for bit (maximum absolute difference 0,
0 differing pixels, 8 of 8; native inter-eye distances equal the registered ones). Strengths to be used: the
registered family medians of FRLL-Morphs AMSL (112.718 px) and corrected MAD22 FaceMorpher (61.211 px).

## Full design, interim (19:00 CET): CLIP ViT-L/14 at 224, thumbnail baseline, clean-negative test, target sanity

Training: 4,000 alpha-field morphs + 569 photos (training persons). Heads: ridge; MLP seeds 401-405 (each image
contributes 384 random patches per seed: deviation, RAM; CLIP-224 has 256 patches, so all of them); logistic baseline
(iii). Scores: mean prediction over patches inside the face hull (top-tenth pooling in `metrics_clip224_full.json`,
key score_top10). Floors (wave 3, control 1): Laplacian variance alone and the best of 27 simple statistics, same
images. Benchmark list: all genuine images, at most 600 morphs per cell (seed 401; deviation).

| Head | F1 rho [95%] (pass 0.4 / drop 0.2) | F2 FaceMorpher R2 vs R4 [95%] | OpenCV R2w vs R4 | FaceMorpher R3 vs R4 | OpenCV R3m vs R4 |
|---|---|---|---|---|---|
| ridge | 0.125 [0.093, 0.157] | 0.997 [0.993, 0.999] | 0.994 [0.987, 0.998] | 0.871 | 0.763 |
| MLP 401 / 402 / 403 / 404 / 405 | 0.266 / 0.276 / 0.260 / 0.275 / 0.283 (each CI about ±0.045) | 0.999 / 0.999 / 0.999 / 0.998 / 0.999 | 0.997-0.998 | 0.897-0.900 | 0.833-0.838 |
| logistic (iii) | — | 1.000 [0.999, 1.000] | 0.999 | 0.865 | 0.745 |
| thumbnail dense / image (32 px) | 0.129 [0.097, 0.157] | 0.495 / 0.503 | — | — | — |
| floor: Laplacian variance | — | 0.753 (R2 vs R4); 0.723 (R2w vs R4) | 0.774 | — | — |
| floor: best simple statistic | — | 0.905 (band power 0.125-0.25 cycles/px) | 0.886 | — | — |

F1 on CLIP-224: below 0.4 for every head and seed; ridge below 0.2. Template baseline (correlation of each true map with
the mean training map, MLP): 0.23; F1 after removing the template 0.24-0.26; pair swap (own minus same-host other
target) 0.27-0.29 for MLP (lower bounds 0.22-0.24), 0.10 [0.063, 0.134] for ridge.
F3 (shift of genuine scores in R0 standard deviations, MLP seeds; ridge in brackets): FRLL native -> E7 0.01-0.04
(ridge -0.01 to -0.02) for opencv, facemorpher, amsl, webmorph; corrected MAD22 native -> E7 (FaceMorpher) 0.16-0.20
(ridge 0.03); R0 -> R2 0.04 (FaceMorpher), 0.00 (OpenCV); R0 -> R2w 0.09-0.10 (FaceMorpher), -0.01 to 0.00 (OpenCV);
logistic: 0.00-0.01, 0.13, 0.09. All at most 0.3. Top-tenth pooling gives the same values within 0.02.
F4 (confounded training: mixed from FRGC, zero-field from colorFERET; crossed test: colorFERET u50 vs FRGC zero-field,
100 vs 100 images, FRGC side 10 persons): logistic baseline AUC 1.000 (unconfounded) -> 0.271 [0.130, 0.437]
(confounded), drop 0.73 (prediction: at least 0.20, met). Dense heads: ridge 0.999 -> 0.610 [0.432, 0.773], drop 0.39;
MLP drops 0.40-0.44 (confounded AUC 0.56-0.60). Prediction for the dense head: drop at most 0.05; registered
falsifier: a drop above 0.15 makes the central claim false. Measured drops 0.39-0.44 on CLIP-224.
F5, EER % (genuine native / E7), MLP seed range: FRLL AMSL 6.9-8.8 / 7.3-8.3, FaceMorpher 1.5-1.9 / 1.5-1.6, OpenCV
1.6-2.4 / 1.5-2.4, WebMorph 5.4-7.3 / 5.5-7.3; corrected MAD22 FaceMorpher 0.4-0.5 / 0.5, OpenCV 3.4-4.3 / 3.4-4.3,
Webmorph 5.4-6.4 / 5.5-6.8. Ridge is worse (FRLL AMSL 22.5 / 21.5). Released MADation ViT-L/14 on the same FRLL rows
(registered A12REL scores on our frames, no rescoring; `madation_vitl14_ref.json`): AMSL 18.2 / 15.6, FaceMorpher 1.0 /
1.0, OpenCV 1.5 / 1.5, WebMorph 5.9 / 5.3; its FRLL native -> E7 shift -0.07 to -0.10. Corrected MAD22 has no
MADation score. Full tables: `metrics_clip224_full.json`, `metrics_thumb_full.json`, `f4_clip224.json`.

Clean-negative test (CN0; `cn0.json`): image-level logistic on mean-pooled tokens, R2 vs R4, trained on one tool, tested
on the other, 5 folds by host: out-of-fold AUC 0.9998-1.0 (CLIP-224 and DINOv3). (a) At the threshold flagging 10% of
test-person R2: untouched source photos flagged 8.6-10.6% (CLIP-224), 3.5-10.3% (DINOv3); FRLL E7 genuine frames
(opencv + facemorpher) 3.2-5.4% (CLIP-224), 0.8-9.2% (DINOv3). Same reads with R2w as the negative: within those
ranges. (b) Best single simple statistic for R2 vs R4: band power 0.125-0.25 cycles/px, folded AUC 0.905 (FaceMorpher),
0.928 (OpenCV); R2w vs R4: 0.889 / 0.886. Fixed verdict: (b) exceeds 0.80, so "the image-level class definition fails"
for both lines. Dense CLIP-224 heads' mean prediction at the same thresholds: source photos 7.8-11.0%, FRLL E7
0.7-3.2%. The DINOv3 dense reads will be added when its scores are complete.

Target sanity (wave 3, control 2; `wave3_target_sanity.json`; 1,000 uniform-0.5 morphs; 32 x 32 patches in the hull):
| target | median flattest quartile | median busiest quartile | rank corr. with patch contrast | accepted (flat < busy and abs(corr) < 0.3) | same-person / two-person | mirror / two-person |
|---|---|---|---|---|---|---|
| g (registered, contrast-normalised) | 1.031 | 0.873 | -0.13 | no (higher on flat) | 0.72 | 0.76 |
| D (a-weighted mean abs. difference) | 11.66 | 12.89 | 0.10 | yes | 0.86 | 0.50 |
| G (gradient disagreement, flat-excluding) | 1.57 | 3.78 | 0.70 | no (contrast) | 0.89 | 0.90 |
| Dm (D above median contrast) | 0.00 | 12.89 | 0.82 | no (contrast) | 0.83 | 0.50 |
Ratios from 100 AR1 primary hosts on the OpenCV-style engine at a = 0.5 (medians). Arms (d)/(e) of wave 3 therefore use
D. (Lead's note, CONSOLIDATED_v3 section 3 point 3: the mirror self-blend is not a matched twin; trace contrasts only.)

## Full design, interim (19:30 CET): DINOv3 ViT-L/16 at 512

Same training images and heads as for CLIP-224 (MLP: 384 of 1,024 patches per image per seed). `metrics_dinov3_512_full.json`.

| Head | F1 rho [95%] (pass 0.4 / drop 0.2) | F2 FaceMorpher R2 vs R4 [95%] | FaceMorpher R2w vs R4 | OpenCV R2w vs R4 | FaceMorpher R3 vs R4 | OpenCV R3m vs R4 |
|---|---|---|---|---|---|---|
| ridge | 0.285 [0.254, 0.313] | 0.999 [0.997, 1.000] | 0.997 | 0.995 | 0.862 | 0.725 |
| MLP 401 | 0.514 [0.458, 0.562] | 1.000 [0.999, 1.000] | 0.999 | 0.999 | 0.879 | 0.770 |
| MLP 402 | 0.520 [0.466, 0.567] | 1.000 | 0.999 | 0.998 | 0.876 | 0.774 |
| MLP 403 | 0.514 [0.455, 0.565] | 1.000 | 0.999 | 0.998 | 0.876 | 0.770 |
| MLP 404 | 0.517 [0.465, 0.564] | 1.000 | 0.999 | 0.998 | 0.877 | 0.774 |
| MLP 405 | 0.513 [0.458, 0.562] | 1.000 | 0.999 | 0.998 | 0.879 | 0.781 |
| logistic (iii) | — | 1.000 [1.000, 1.000] | 1.000 | 1.000 | 0.858 | 0.751 |
Floors for the same contrasts: Laplacian variance 0.753 (FaceMorpher R2 vs R4), 0.723 / 0.774 (R2w vs R4,
FaceMorpher / OpenCV); best simple statistic 0.905 (band power 0.125-0.25 cycles/px).
F1 MLP: 5 of 5 seeds at or above the 0.4 pass mark (lower bounds 0.455-0.466); ridge between the marks. Template
baseline about 0.23 (as above); F1 after removing the template 0.49-0.50 (MLP), 0.25 (ridge); pair swap 0.48-0.50
(lower bounds 0.415-0.426) for MLP, 0.24 [0.21, 0.28] for ridge.
F3 (R0 standard deviations; MLP seed range, ridge, logistic): registered rungs: FRLL R0 -> R1 (native -> E7 frames)
opencv 0.08-0.09 (ridge 0.08, logistic 0.18), facemorpher -0.01-0.00, amsl and webmorph -0.00-0.01; R0 -> R2
0.10-0.11 FaceMorpher, 0.00 OpenCV: all at most 0.3. Lead's added rung R0 -> R2w: FaceMorpher 0.68-0.73 (ridge 0.65,
logistic 0.47), OpenCV 0.21-0.23 (ridge 0.22, logistic 0.40). Corrected MAD22 native -> E7 (FaceMorpher, outside the
registered F3): 0.42-0.46 (ridge 0.22, logistic 0.79).
F5, EER % native / E7 (MLP seed range): FRLL AMSL 8.4-10.3 / 8.8-10.3, FaceMorpher 0.5-1.5 / 0.5-1.0, OpenCV 0.5-0.6 /
0.5-0.6, WebMorph 9.4-10.8 / 9.3-10.9; corrected MAD22 FaceMorpher 1.5-3.0 / 3.0-4.4, OpenCV 1.5-2.6, Webmorph
6.3-7.9 / 5.9-7.7. Logistic: AMSL 13.7 / 15.7, WebMorph 3.0 / 3.5, OpenCV 0.5 / 0.9. Ridge: AMSL 14.1, WebMorph 14.1.
F4 on DINOv3: running.

## Mirror distance (lead's free rider), CLIP ViT-L/14 at 224, final (`mirror_clip224.json`)

Score = mean over in-hull patches of the L2 distance between the image's tokens and the flipped image's tokens.
"Mirrored token positions" was read two ways (both reported): content-aligned (token (i, j) against the flipped
image's token (i, n-1-j): the same content, mirrored; primary) and position-aligned (token (i, j) against the flipped
image's token (i, j): left half against mirrored right half, a symmetry measure). AUC with the higher rung positive;
folded = max(AUC, 1 - AUC); AR1's person bootstrap. Primary pool, 536 hosts.

| contrast | content-aligned AUC [95%] | position-aligned AUC (folded) |
|---|---|---|
| FaceMorpher R2 vs R4 | 0.715 [0.671, 0.759] | 0.428 (0.572) |
| FaceMorpher R2w vs R4 | 0.678 [0.633, 0.721] | 0.411 (0.589) |
| FaceMorpher R3 vs R4 | 0.580 [0.539, 0.624] | 0.447 (0.553) |
| OpenCV R2 vs R4 | 0.608 [0.564, 0.649] | 0.325 (0.676) |
| OpenCV R2w vs R4 | 0.598 [0.555, 0.639] | 0.338 (0.662) |
| OpenCV R3 vs R4 | 0.537 [0.498, 0.579] | 0.392 (0.608) |
| FRLL R0 vs R1 (native vs E7 frames), opencv / facemorpher / amsl / webmorph | 0.481 / 0.481 / 0.473 / 0.471 (folded 0.52-0.53) | 0.49 (folded 0.51-0.52) |
| corrected MAD22 R0 vs R1, FaceMorpher / OpenCV / Webmorph | 0.427 / 0.499 / 0.497 | 0.464 / 0.501 / 0.500 |
| benchmark morph vs native: FRLL opencv / facemorpher / amsl / webmorph | 0.723 / 0.798 / 0.546 / 0.653 | 0.379 / 0.406 / 0.299 / 0.348 |
| benchmark morph vs native: MAD22 FaceMorpher / OpenCV / Webmorph | 0.932 / 0.504 / 0.568 | 0.734 / 0.314 / 0.239 |
Falsifiers fixed by the lead: "no value for landmark morphs if R2 vs R4 is below 0.60": content-aligned FaceMorpher 0.715,
OpenCV 0.608 (lower bound 0.564). "Not history-blind if FRLL R0 vs R1 exceeds 0.60": 0.47-0.48 (folded 0.52-0.53).
Not run: DINOv3 and CLIP-336 flips (GPU time); no training anywhere in this block.

## AF0 wave 2 (ghost-energy target), interim: CLIP ViT-L/14 at 224 (`wave2_clip224.json`, `metrics_clip224_w2_*.json`)

Scale (deviation): wave-1 training pairs (600 morphs) + 569 photos + the 1,080 warped halves of those pairs (all-zero maps), ridge and MLP seed 401 only. Targets: alpha (prereg), g (registered ghost energy, scaled 1/8), D (disagreement, scaled 1/120), G (gradient disagreement, wave 3's flat-excluding attempt, scaled 1/40). F1 here = Spearman between predicted and true map of the head's own target on validation morphs (gradient and bump for alpha; every non-zero morph for g, D, G). Pooling: mean in hull, top tenth, inner face (hull of the eyebrow, eye, nose and mouth landmarks), periphery (outside the face hull). Floor for FaceMorpher R2w vs R4: Laplacian variance 0.723.

| target | head | pooling | F1 rho | pair swap | FM R2w vs R4 (floor) | CV R2w vs R4 | FM R3 vs R4 | CV R3 vs R4 | CV R3m vs R4 | FRLL E7 shift (max) | MAD22 FM E7 shift | R0->R2w FM / CV | EER AMSL / WebMorph | Poisson AUC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| alpha | ridge | mean | 0.068 | 0.070 | 0.997 (0.723) | 0.994 | 0.868 | 0.866 | 0.742 | -0.036 | -0.012 | 0.114 / -0.016 | 22.610 / 16.090 | 0.905 |
| alpha | ridge | top10 | 0.068 | 0.070 | 0.995 (0.723) | 0.992 | 0.855 | 0.852 | 0.724 | -0.046 | -0.028 | 0.127 / -0.007 | 25.500 / 16.580 | 0.894 |
| alpha | ridge | inner | 0.068 | 0.070 | 0.996 (0.723) | 0.994 | 0.868 | 0.863 | 0.737 | -0.026 | 0.015 | 0.128 / -0.012 | 21.120 / 15.680 | 0.908 |
| alpha | ridge | periph | 0.068 | 0.070 | 0.998 (0.723) | 0.996 | 0.860 | 0.856 | 0.713 | -0.021 | 0.005 | 0.081 / -0.036 | 19.060 / 7.340 | 0.901 |
| alpha | mlp_s401 | mean | 0.140 | 0.162 | 0.998 (0.723) | 0.997 | 0.884 | 0.880 | 0.772 | -0.014 | 0.039 | 0.088 / -0.009 | 14.190 / 9.410 | 0.909 |
| alpha | mlp_s401 | top10 | 0.140 | 0.162 | 0.996 (0.723) | 0.995 | 0.874 | 0.870 | 0.754 | -0.018 | 0.033 | 0.094 / -0.006 | 18.730 / 11.300 | 0.902 |
| alpha | mlp_s401 | inner | 0.140 | 0.162 | 0.998 (0.723) | 0.997 | 0.881 | 0.879 | 0.765 | -0.005 | 0.067 | 0.109 / -0.004 | 14.190 / 8.750 | 0.913 |
| alpha | mlp_s401 | periph | 0.140 | 0.162 | 1.000 (0.723) | 0.999 | 0.873 | 0.872 | 0.765 | -0.014 | 0.068 | 0.063 / -0.025 | 16.170 / 4.370 | 0.911 |
| g | ridge | mean | 0.107 | 0.051 | 0.995 (0.723) | 0.991 | 0.852 | 0.847 | 0.707 | -0.038 | -0.010 | 0.147 / -0.011 | 26.490 / 20.630 | 0.900 |
| g | ridge | top10 | 0.107 | 0.051 | 0.992 (0.723) | 0.987 | 0.836 | 0.829 | 0.680 | -0.048 | -0.021 | 0.159 / -0.004 | 28.470 / 21.120 | 0.899 |
| g | ridge | inner | 0.107 | 0.051 | 0.994 (0.723) | 0.989 | 0.848 | 0.842 | 0.696 | -0.024 | 0.022 | 0.155 / -0.010 | 25.990 / 22.520 | 0.890 |
| g | ridge | periph | 0.107 | 0.051 | 0.998 (0.723) | 0.997 | 0.855 | 0.851 | 0.708 | -0.022 | 0.020 | 0.090 / -0.032 | 17.660 / 5.860 | 0.901 |
| g | mlp_s401 | mean | 0.140 | 0.060 | 0.996 (0.723) | 0.993 | 0.866 | 0.859 | 0.740 | -0.014 | 0.024 | 0.109 / -0.010 | 20.050 / 13.200 | 0.899 |
| g | mlp_s401 | top10 | 0.140 | 0.060 | 0.993 (0.723) | 0.988 | 0.853 | 0.844 | 0.716 | -0.021 | 0.030 | 0.118 / 0.008 | 26.980 / 16.170 | 0.897 |
| g | mlp_s401 | inner | 0.140 | 0.060 | 0.996 (0.723) | 0.993 | 0.861 | 0.855 | 0.728 | 0.012 | 0.059 | 0.126 / -0.003 | 20.130 / 13.120 | 0.890 |
| g | mlp_s401 | periph | 0.140 | 0.060 | 1.000 (0.723) | 0.999 | 0.861 | 0.856 | 0.751 | -0.019 | 0.041 | 0.077 / -0.027 | 15.760 / 4.780 | 0.903 |
| D | ridge | mean | 0.025 | 0.035 | 0.992 (0.723) | 0.984 | 0.835 | 0.834 | 0.669 | -0.063 | -0.076 | 0.100 / -0.017 | 24.500 / 20.710 | 0.891 |
| D | ridge | top10 | 0.025 | 0.035 | 0.986 (0.723) | 0.976 | 0.816 | 0.812 | 0.648 | -0.084 | -0.095 | 0.117 / -0.010 | 27.890 / 24.590 | 0.891 |
| D | ridge | inner | 0.025 | 0.035 | 0.989 (0.723) | 0.980 | 0.834 | 0.830 | 0.661 | -0.052 | -0.047 | 0.105 / -0.013 | 24.500 / 21.040 | 0.882 |
| D | ridge | periph | 0.025 | 0.035 | 0.996 (0.723) | 0.993 | 0.833 | 0.826 | 0.668 | -0.038 | -0.019 | 0.083 / -0.033 | 18.070 / 7.340 | 0.901 |
| D | mlp_s401 | mean | 0.064 | 0.074 | 0.995 (0.723) | 0.992 | 0.859 | 0.858 | 0.733 | -0.018 | 0.003 | 0.085 / -0.007 | 21.040 / 15.180 | 0.903 |
| D | mlp_s401 | top10 | 0.064 | 0.074 | 0.988 (0.723) | 0.983 | 0.836 | 0.830 | 0.702 | -0.020 | 0.028 | 0.097 / -0.001 | 26.490 / 20.220 | 0.906 |
| D | mlp_s401 | inner | 0.064 | 0.074 | 0.994 (0.723) | 0.990 | 0.857 | 0.855 | 0.727 | 0.012 | 0.047 | 0.098 / 0.000 | 20.050 / 15.680 | 0.897 |
| D | mlp_s401 | periph | 0.064 | 0.074 | 0.999 (0.723) | 0.997 | 0.836 | 0.834 | 0.724 | -0.022 | 0.031 | 0.076 / -0.015 | 17.160 / 5.360 | 0.904 |
| G | ridge | mean | 0.306 | 0.040 | 0.993 (0.723) | 0.989 | 0.860 | 0.856 | 0.727 | -0.045 | -0.046 | 0.126 / -0.011 | 25.000 / 16.670 | 0.898 |
| G | ridge | top10 | 0.306 | 0.040 | 0.990 (0.723) | 0.986 | 0.852 | 0.847 | 0.718 | -0.039 | -0.006 | 0.143 / 0.010 | 28.470 / 21.450 | 0.899 |
| G | ridge | inner | 0.306 | 0.040 | 0.993 (0.723) | 0.989 | 0.859 | 0.854 | 0.724 | -0.028 | 0.000 | 0.134 / -0.007 | 24.500 / 17.160 | 0.892 |
| G | ridge | periph | 0.306 | 0.040 | 0.996 (0.723) | 0.994 | 0.857 | 0.852 | 0.701 | -0.027 | -0.019 | 0.092 / -0.030 | 19.140 / 6.850 | 0.893 |
| G | mlp_s401 | mean | 0.298 | 0.045 | 0.990 (0.723) | 0.986 | 0.859 | 0.854 | 0.736 | -0.015 | -0.008 | 0.078 / -0.008 | 27.890 / 19.060 | 0.873 |
| G | mlp_s401 | top10 | 0.298 | 0.045 | 0.981 (0.723) | 0.973 | 0.848 | 0.838 | 0.722 | 0.011 | 0.035 | 0.093 / 0.013 | 32.840 / 24.010 | 0.868 |
| G | mlp_s401 | inner | 0.298 | 0.045 | 0.990 (0.723) | 0.985 | 0.858 | 0.853 | 0.735 | 0.023 | 0.056 | 0.097 / 0.001 | 23.020 / 18.150 | 0.863 |
| G | mlp_s401 | periph | 0.298 | 0.045 | 0.997 (0.723) | 0.995 | 0.859 | 0.852 | 0.722 | -0.033 | -0.008 | 0.069 / -0.023 | 22.940 / 8.420 | 0.880 |

Registered wave-2 reading for the ghost-energy head g (both heads, mean and top-tenth pooling): fails? no (FaceMorpher warp-only vs two-person 0.992-0.996, at least 0.75; FRLL native -> E7 shift at most 0.05 in absolute value, at most 0.3). Gain? no (same-person vs two-person FaceMorpher 0.836-0.866 against alpha's 0.855-0.884, i.e. 0.02 lower, not 0.03 higher; E7 shift not lower than alpha's). Wave 2 on DINOv3: running.

## AF0 wave 3, control 1 on AF0's own validation images (`wave3_floor_valcmp.json`)

Uniform-0.5 validation morphs (200) against their own warped halves (400, all-zero maps): Laplacian variance alone
0.760 (the reviewer's measured 0.76 at 512 px reproduced), best simple statistic 0.823 (band power 0.063-0.125
cycles/px). CLIP-224 heads on the same images: full-design heads (never trained with halves) 0.9995-1.000; wave-2
heads trained with halves 0.989-0.9999 (floor on their image subset 0.748 / 0.812). Excess over the Laplacian floor
about 0.24, over the best simple statistic about 0.18. DINOv3: pending (halves scored by the running chain).
Landmark-ladder floors (same statistics, 536 hosts; in every metrics_*.json beside each AUC): FaceMorpher R2 vs R4
0.753 / best 0.905; R2w vs R4 0.723 / 0.889; OpenCV R2 vs R4 best 0.928; OpenCV R2w vs R4 0.774 / 0.886.

## Softened landmark-ladder copies for the protocol-network tests (PN1), lead's round-3 task (19:55 CET)

Built with `src/AF0/soften.py` (verified E7 branch, unchanged; prep_eval.py at pin 374408ab...; detector = prep_eval's
torch-on-GPU insightface wrapper, as in the verification), strengths = registered family medians 112.718 px (FRLL AMSL,
"amsl112") and 61.211 px (corrected MAD22 FaceMorpher, "fm61"). Sources (read only): AR1 OpenCV R4 and R3 of all 536
primary hosts and R3m of the 200 hosts of `ar1soft_src.csv`, from `/mnt/t7/smad_next/AR1/img/frgcferet/opencv/`.
- Images (2,544, all aligned by prep_eval.align): `/mnt/t7/smad_next/AF0/img/soft_ladder/{R4,R3,R3m}_{amsl112,fm61}/<host>.png`
  (hard links to `/mnt/t7/smad_next/AF0/img/soft/<strength>/ar1_<id>_<strength>.png`).
- Lead's list: `/mnt/t7/smad_next/AF0/lists/ar1soft_ladder.csv` (host, person, rung, strength, target_ied_px,
  source_path, output_path, sha256, aligned, native_ied, scale; 2,544 rows; file sha256 8483ccc1...).
- Extraction list (feat.py format): `/mnt/t7/smad_next/AF0/lists/ladsoft.csv` (sha256 c1f7e756...).
- CLIP ViT-L/14-224 patch tokens: `/mnt/t7/smad_next/AF0/feat/clip224/ladsoft.tokens.npy` (2,544 x 256 x 1,024 float16)
  + `ladsoft.ids.npy` (order = ladsoft.csv, checked).
- DINOv3 ViT-L/16-512 patch tokens: `/mnt/t7/smad_next/AF0/feat/dinov3_512/ladsoft.tokens.npy` (2,544 x 1,024 x 1,024;
  mean patch token = mean over axis 1) + `.ids.npy`; complete when `ladsoft.done` reads 2544.
- 27 simple statistics: `/mnt/t7/smad_next/AF0/cues/ladsoft.npz` (ids, cues, names).
- Unsoftened counterparts: `feat/{clip224,dinov3_512}/ar1.tokens.npy` (list `lists/ar1.csv`), `cues/ar1.npz`.
Build time: about 55 min with two processes (forward and reverse); both logs merged
(`soft_ladsoft_src.csv`, `soft_ladsoft_src_rev.csv`).
