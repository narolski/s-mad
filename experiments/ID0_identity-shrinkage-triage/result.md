# Identity-shrinkage triage: how average is a morph, and what is the ceiling [ID0] — result

First version 11 Nov 2026, 18:20 CET (kept as `result_v1_20261111_1820.md`). **Revised 11 Nov, about 19:15 CET,
after the independent review** (`experiments/reviews/REVIEW_ID0_20261111.md`, verdict "needs qualification")
and the four zero-GPU reruns of pre-registration amendment 1 (`prereg.md`, 18:45). Withdrawn statements are kept
below, marked **WITHDRAWN**, with the reason. Full record: `README.md`. AUC = area under the ROC curve,
second-named group positive; [a, b] = 95% two-way person bootstrap (a41_read.Draw, B = 2,000). ISS = the
pre-registered identity-subspace shrinkage score (higher = closer to the average face). Facts only.

## What the data say (corrected statements)

1. How close a face is to the average face does not work as a single-image morph detector in the form tested
   (five feature spaces, statistic fitted on 776 genuine persons): no space reaches 0.75 with every
   storage-history control in band (unchanged; follows from the registered rule).
2. **No arm is both powered and clean** (amendment 1a; power flag fixed before the rerun: ideal-midpoint AUC
   ≥ 0.65 with lower bound > 0.60). The face-recognition (glintr100) arm is clean on storage history but has no
   power on the landmark ladder: its registered ISS scores an ideal midpoint of the same ladder pairs *lower*
   than a photo (0.44–0.45), and its virtual head and mean-direction projection reach only 0.60–0.64 on ideal
   midpoints. CLIP, DINOv3 and the diffusion-autoencoder code are powered (ideal 0.82–0.92) but fail the
   MorDIFF-history control (0.582, 0.356, 0.000).
3. In face-recognition features an ideal two-person midpoint is only slightly more typical than a photo
   (virtual head 0.64, mean direction 0.61 on the ladder pairs); real landmark morphs reach 0.58–0.59 (head) and
   0.50–0.55 (mean direction); diffusion morphs are not distinguishable from reconstructions within wide
   intervals (head 0.524 [0.454, 0.594]). Typicality cannot explain near-zero benchmark errors. What a second
   identity leaves in an image is not measured here.
4. Computed from exact landmark files, the mean shape of two persons is more average than a real shape
   (0.725 [0.689, 0.758]); the mean of two sessions of one person hardly is (0.548 [0.536, 0.559]). This is a
   calculation on landmark files; whether it can be read from a morph image is untested (the detected-landmark
   arm belongs to the mirror-asymmetry test, AS0).
5. Shape ladder, correct reading: photo vs two-session same-person mean 0.548; photo vs own-mirror mean 0.572;
   same-person mean vs two-person mean 0.687 [0.650, 0.720]. All 536 AR1 host pairs are cross-session, so
   averaging of pose and session is bounded by the 0.548: most of the shape effect is specific to the second
   person.
6. In CLIP, DINOv3 and the diffusion autoencoder an ideal feature midpoint would stand out (0.82–0.92), but the
   features of a real morph are not that midpoint: realised share (AUC_real − 0.5)/(AUC_ideal − 0.5) on the AR1
   ladder −0.30 to −0.39 (CLIP), 0.07–0.09 (DINOv3), 0.44–0.49 (diffusion autoencoder); on MorDIFF D20 vs B20
   0.47 (CLIP), 0.35 (DINOv3), 0.58 (diffusion autoencoder, native frames).
7. The informative control for within-pipeline contrasts is the same-person rung, not only the storage-history
   copy. CLIP and DINOv3 fail it (same-person mix vs two-person morph 0.419 and 0.478; reconstruction vs
   same-person mix 0.756 and 0.627: they read "two codes mixed", not "two persons"). The diffusion-autoencoder
   code passes it: same-person mix vs two-person morph 0.747 [0.685, 0.807] on the diffusion ladder and 0.676
   [0.637, 0.715] on the landmark ladder, and it is clean on the landmark-family history copies (0.515, 0.514).
   What disqualifies it is that its absolute level follows frame and pool: MorDIFF history 0.000, stored crops
   0.462 against 0.688 on native frames, FRLL photo vs StyleGAN3 render 0.004.
8. How sure: one deterministic analysis with person bootstrap on our own diagnostic sets (520 hosts, 200
   diffusion morphs, 423 StyleGAN3 morphs); not a held-out benchmark. Not shown: that a second identity leaves
   little in an image, or that benchmark error rates come from process traces.

## Withdrawn

- **WITHDRAWN: the "ceiling" of 0.70 to 0.78** (the Λ-based table, and "the measured identity-only ceiling").
  Reason: it is not a bound. It used Λ = 2.68 (Ledoit-Wolf); the ridge variants in the same file give Λ
  3.70–4.81 (0.86–0.92 at c = 0); the in-domain head still rises with fit persons and with weaker
  regularisation (amendment 1b, table below); and it is a linear, first-moment number in one feature space.
  Replacement wording: "what a linear head reaches with 776 persons: 0.751 [0.735, 0.767] morph vs single
  photo, in domain".
- **WITHDRAWN: "the closed form matches the exact-shape arm within about 0.03".** Reason: it holds only with
  the pool-centred similarity added after the numbers were seen. With the registered estimator the closed form
  misses by 0.04 on the ladder (0.687 vs 0.725) and by 0.10–0.11 on benchmark pairs (0.634 vs 0.737; 0.650 vs
  0.757). The ten benchmark-pair rows are two results repeated (the families share pair lists).
- **WITHDRAWN: every sentence that reads the face-recognition ISS "at chance" numbers (0.494, 0.503, 0.554,
  0.545, flat dose) as evidence about morphs.** Reason: the statistic has no power there (ideal midpoints
  0.44–0.45; genuine-only virtual check 0.521).
- **WITHDRAWN: any sentence that calls the exact-shape result a signal read from images.** Reason: no morph
  image is read; the positive class is the mean of two source landmark files.
- **WITHDRAWN: "dose monotone" for the exact-shape arm as evidence** (Page p 4e-234). Reason: algebra; a
  quadratic score on a linear interpolation of shapes is monotone by construction. (The diffusion-autoencoder
  dose, p 9e-99, is measured on built FaceMorpher images; it stays as a measurement with the frame/pool caveat
  of point 7.)
- **WITHDRAWN: "physics part 1 does not fire" read as support.** It does not fire on the best of five arms, but
  the lower bound on MorDIFF (0.626) is below the 0.65 line and the arm that clears it fails its control.

## Registered results (numbers unchanged)

| Arm | native vs E7, MorDIFF family | AR1 OpenCV R2w vs R4 | MorDIFF D20 vs B20 | StyleGAN3 render vs morph |
|---|---|---|---|---|
| Landmark, exact shapes (calculation) | not applicable (no image) | 0.687 [0.650, 0.720] | — | — |
| glintr100 ISS (no power, see 2) | 0.506 [0.489, 0.524] | 0.503 [0.460, 0.548] | 0.554 [0.471, 0.640] | 0.545 [0.513, 0.578] |
| CLIP ViT-L/14 | 0.582 [0.543, 0.621] | 0.364 [0.323, 0.404] | 0.698 [0.616, 0.775] | 0.542 [0.511, 0.572] |
| DINOv3 ViT-L/16 (bf16) | 0.356 [0.300, 0.406] | 0.533 [0.486, 0.578] | 0.611 [0.522, 0.698] | 0.624 [0.598, 0.652] |
| DiffAE z_sem | 0.000 [0.000, 0.000] | 0.692 [0.657, 0.729] | 0.688 [0.626, 0.749] (native frames) | 0.597 [0.568, 0.627] |

The other primary-family history copies (opencv, facemorpher) are 0.502–0.531 in every arm; the stylegan copies
are identical to the native photos (cosine 1.000), so three families are informative. Two registered controls are
vacuous: NC vs R3 (practically identical embeddings) and OpenCV R2 (equals the host photo).
GEO-0 reads (glintr100): fidelity of the embedding to the normalised sum of its sources, median: landmark R4
0.856–0.876, twins 0.96–0.98, diffusion morphs 0.69–0.72, same-person mix 0.915. Mean-direction gain: AR1 OpenCV
R4 1.108 [1.057, 1.157] (prediction 1.27), R3 1.030 [1.017, 1.042] (prediction 1.03). Virtual head on real sets:
AR1 R3 vs R4 0.557 [0.514, 0.598], R2w vs R4 0.590 [0.546, 0.631], a43_D vs a43_B 0.522 [0.453, 0.593];
StyleGAN3 0.600 against contributor renders but 0.458 against spread-matched renders (reads latent typicality,
which a single render shares). GEO-0: neither Go nor Kill; identity idea 0's control clause fires (head under
MorDIFF history 0.415 [0.396, 0.427]). Contributor similarity in benchmark pairs (glintr100 cosine, median):
FRLL-Morphs 0.037, corrected MAD22 / MorDIFF / DiM 0.114–0.116, H3 0.162, AR1 0.234.

## Amendment 1 reruns (descriptive; files in this folder)

(a) Ideal against realised — `amend1_a.json`, `amend1_a.csv` (P = powered by the pre-fixed rule).

| Arm, read-out | Contrast | real | ideal | P | realised share |
|---|---|---|---|---|---|
| glintr100 ISS | AR1 OpenCV R4 vs H | 0.494 [0.451, 0.540] | 0.439 [0.398, 0.483] | no | — |
| glintr100 head | AR1 OpenCV R4 vs H | 0.593 [0.549, 0.633] | 0.642 [0.605, 0.678] | no | 0.65 |
| glintr100 mean dir. | AR1 OpenCV R4 vs H | 0.547 [0.506, 0.588] | 0.614 [0.576, 0.653] | no | 0.41 |
| glintr100 head | AR1 FaceMorpher R4 vs H | 0.578 [0.535, 0.619] | 0.642 [0.605, 0.678] | no | 0.55 |
| glintr100 head | A43 B20 vs E | 0.622 [0.548, 0.694] | 0.691 [0.619, 0.761] | yes | 0.64 [0.31, 0.97] |
| glintr100 head | A43 B20 vs D20 | 0.524 [0.454, 0.594] | 0.594 [0.523, 0.663] | no | 0.26 |
| glintr100 head | published MorDIFF vs rec | 0.489 [0.440, 0.537] | 0.679 [0.639, 0.719] | yes | −0.06 [−0.39, 0.19] |
| CLIP ISS | AR1 OpenCV R4 vs R2w | 0.364 [0.323, 0.404] | 0.845 [0.813, 0.876] | yes | −0.39 [−0.53, −0.27] |
| CLIP ISS | A43 B20 vs D20 | 0.698 [0.616, 0.775] | 0.918 [0.882, 0.951] | yes | 0.47 [0.28, 0.65] |
| DINOv3 ISS | AR1 OpenCV R4 vs R2w | 0.533 [0.486, 0.578] | 0.900 [0.874, 0.924] | yes | 0.08 [−0.03, 0.19] |
| DINOv3 ISS | A43 B20 vs D20 | 0.611 [0.522, 0.698] | 0.816 [0.758, 0.871] | yes | 0.35 [0.08, 0.57] |
| DiffAE ISS | AR1 OpenCV R4 vs R2w | 0.692 [0.657, 0.729] | 0.895 [0.870, 0.918] | yes | 0.49 [0.41, 0.56] |
| DiffAE ISS | AR1 OpenCV R3 vs R2w (same person) | 0.537 [0.518, 0.555] | 0.719 [0.701, 0.738] | yes | 0.17 [0.09, 0.24] |
| DiffAE ISS | native B20 vs D20 | 0.688 [0.626, 0.749] | 0.825 [0.774, 0.878] | yes | 0.58 [0.41, 0.73] |
| DiffAE ISS | stored B20 vs E | 0.324 [0.251, 0.399] | 0.685 [0.633, 0.738] | yes | −0.95 [−1.67, −0.48] |

H3 ideal midpoints come from the CASIA source crops while the negatives are renders, so the H3 ideal rows (in the
CSV) mix pools and are not read.

(b) Learning curve and regulariser table, glintr100 virtual head — `amend1_b.json`, `amend1_b.csv`.

| Head | C | training persons per fold | morph vs single | morph vs single + twin |
|---|---|---|---|---|
| logistic | 1.0 | 75 | 0.611 [0.595, 0.627] | 0.607 [0.583, 0.630] |
| logistic | 1.0 | 150 | 0.621 [0.606, 0.637] | 0.623 [0.602, 0.646] |
| logistic | 1.0 | 300 | 0.659 [0.642, 0.677] | 0.658 [0.625, 0.688] |
| logistic | 1.0 | all (about 620) | 0.751 [0.735, 0.767] | 0.744 [0.713, 0.770] |
| logistic | 0.001 | all (about 620) | 0.711 [0.696, 0.727] | 0.713 [0.694, 0.734] |
| logistic | 0.01 | all (about 620) | 0.726 [0.710, 0.743] | 0.724 [0.697, 0.748] |
| logistic | 0.1 | all (about 620) | 0.734 [0.718, 0.751] | 0.730 [0.700, 0.755] |
| logistic | 10.0 | all (about 620) | 0.762 [0.746, 0.778] | 0.752 [0.721, 0.779] |
| logistic | 100.0 | all (about 620) | 0.756 [0.740, 0.772] | 0.747 [0.721, 0.772] |
| mean-direction projection (no fit beyond the mean) | — | all (about 620) | 0.659 [0.642, 0.676] | 0.652 [0.626, 0.678] |

Pooled out-of-fold AUC over the 5 registered person folds; the full-size C = 1 row reproduces the registered
in-domain value (0.744). The one-hidden-layer network row and the real-contrast columns (each variant refitted on
all fit persons and applied to AR1 R3 vs R4, H vs R4, R2w vs R4, a43_D vs a43_B and the MorDIFF E7 control) are
still being computed at 19:25 (PID 2324274, nice 10, machine load about 150); they will be in `amend1_b.json`.
Rows above are parsed from its log into `amend1_b_partial.csv`.

(c) Review hypothesis H-new-1 — `amend1_c.json`. Per-host Spearman ρ of the ISS shift (R4 − R2w, AR1 OpenCV,
520 hosts) with the loss of fine detail (log Laplacian variance inside the face box, R2w minus R4; median loss
0.645): CLIP +0.161 [0.006, 0.313]; diffusion autoencoder +0.078 [−0.072, 0.220]; DINOv3 +0.020 [−0.132, 0.170].
Whole-frame Laplacian variance: CLIP +0.079 [−0.068, 0.234], diffusion autoencoder +0.211 [0.056, 0.351], DINOv3
−0.002. Read on the pre-fixed lines: CLIP |ρ| 0.161 is below 0.3 (prediction not met) and not below 0.1 (not
falsified); diffusion autoencoder 0.078 < 0.15 (as predicted).

(d) Storage-history rows, glintr100 read-outs — `amend1_d.json`, `amend1_d.csv`. Copy vs native AUC, share of
photos scored lower in the copy, median paired shift in SD of the native scores:

| Family | cos(native, copy) | ISS | virtual head | mean direction |
|---|---|---|---|---|
| opencv | 0.996 | 0.506 [0.500, 0.512] | 0.496 [0.489, 0.502]; lower 0.55; −0.01 SD | 0.504 |
| facemorpher | 0.996 | 0.509 [0.503, 0.516] | 0.497 [0.491, 0.502]; lower 0.58; −0.02 SD | 0.504 |
| stylegan | 1.000 | 0.500 | 0.500 (identical copies) | 0.500 |
| mordiff | 0.979 | 0.506 [0.489, 0.524] | **0.415 [0.396, 0.427]; lower 0.88 [0.83, 0.93]; −0.30 SD [−0.35, −0.26]** | 0.493 [0.480, 0.507] |
| dim_c | 0.991 | 0.512 | 0.480 [0.471, 0.487]; lower 0.66; −0.06 SD | 0.503 |
| greedy_dim | 0.991 | 0.513 | 0.482 [0.473, 0.488]; lower 0.67; −0.06 SD | 0.505 |
| greedy_dim_s | 0.991 | 0.511 | 0.482 [0.473, 0.488]; lower 0.66; −0.07 SD | 0.505 |
| amsl | 0.995 | 0.508 | 0.493 [0.486, 0.498]; lower 0.58; −0.02 SD | 0.505 |
| webmorph | 0.995 | 0.506 | 0.493 [0.486, 0.499]; lower 0.60; −0.03 SD | 0.505 |

The plain mean-direction projection stays at 0.493–0.505 under all nine histories; the fitted head moves under
every diffusion-size history.

## Not verified, gaps, process

Not verified: that Enc(Dec(lerp)) returns the generator's lerp code in its own precision path; that fp16 CLIP
equals a46's fp32 CLIP on identical files. Gaps: CLIP, DINOv3 and DiffAE ran on tier-1 sets only; no BPCER per
demographic group; released-detector shrink-law audit not run; detected landmarks on built images go to AS0.
Process: `prereg.md` (first part, sha 3ee8588b…) has file time 15:38:57 but was first committed in 5a19286 at
17:25:21 together with three arms' results, so there is no independent timestamp; no pre-run review was run.
8 AR1 hosts are validation-reserved persons; any experiment that fits on the AR1 ladder must drop them (ID0
does).
