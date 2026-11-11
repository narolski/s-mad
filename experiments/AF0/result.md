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

Written at 16:45 CET as soon as the numbers existed. Training: 600 alpha-field morphs (train persons, 120 per field
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
