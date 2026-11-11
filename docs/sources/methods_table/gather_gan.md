# GAN morphs: published S-MAD methods, native benchmark numbers vs the controlled tests

Gathered 2026-11-07 for the author's request: "Explain plainly how each competing method actually works against
'regular' morphs, GAN and Diffusion once shortcuts are not available. Prepare table with comparison." This file is
the **GAN column** only. The work was read-only and computed nothing new, except the arm means marked † (see "Sources
and status for each column" in section 3, and flag 2 in section 7).

**MADMamba is not in this table.** It is sealed and was not evaluated on H3. W3, E10 and FST results were not
opened or used, and nothing under fst*, manifests/valx.csv or A12SP was read. M7 (FD-MAD-G) was never run: the A12
plan left it off by default (`smadcvpr/plans/A12/plan.md` l.236, 658).

## 1. The answer in one paragraph

On the native GAN benchmarks (MAD22 MIPGAN-I / MIPGAN-II, FRLL StyleGAN, the G-test), the morphs are generator
output and the bona fide photos are camera photos. The low MIPGAN EERs there (0.1-18.4% for the CLIP rows and the
SelfMAD release) measure that difference. When the bona fide side is also generator output (H3: StyleGAN3 two-person
latent-average morphs against single-person renders of the same generator), **no published row scores the morphs
above the renders at AUC ≥ 0.65**. The range is 0.35-0.59. Four rows rank the single-person renders *higher* than the
morphs: the two MADation retrains, the official ViT-L/14 and the SelfMAD release (15 row-cells, 0.35-0.45). The
official ViT-B/16 is at 0.554. Matching the renders to the morphs' latent spread (X4)
brings every row to 0.42-0.52, and 11 of 12 primary rows have an upper bound below 0.5. On the second generator
(H4b, StyleGAN v1 MIPGAN-I-style morphs against single-identity renders), no row exceeds the 0.912 that file size
alone gives by more than noise. The highest, M3L at 0.923, is +0.010 over it with a Bonferroni lower bound of
−0.031. Threshold free, the rows that flag morphs against camera photos flag single-person renders against the
same photos about as strongly. Across 38 rows, Spearman between the two is 0.95. So what they detect is generator
output, not two identities. This is the C3 claim (grade "strong (narrow)", one generator per test, no causal
reading), and its allowed wording is in section 6. One caveat on how hard this test is: for latent-average morphs, a
spread-matched single-person render is almost the same kind of image by construction. So H3 and X4 have almost no
power against a two-identity component, and absence here is not proof that a detector is blind to identity (A39 P
review; A41 amendment G review F8).

## 2. The GAN sets and controls used

| Set / control | Morph class | Bona fide / reference class | What it removes | Cue-only floor (AUC) | Source |
|---|---|---|---|---|---|
| MAD22 MIPGAN-I / MIPGAN-II (native) | MIPGAN on StyleGAN, PNG 1024 px | FRLL camera photos, JPEG q≈98.5, 1350 px (MAD22 bona fide are byte copies of FRLL, n 185) | nothing | container, width, bits per pixel: one-feature O = 1.000 each | A41 `a41_files.json` DC-A cells MAD22/MIPGAN_I, _II; A36 README disclosures |
| FRLL StyleGAN (native) | StyleGAN latent-average, **JPEG q≈75**, 1024 px | FRLL camera JPEG q≈98.5, 1350 px | nothing (the E7 pool equals the native pool for this family: delta +0.00 in every row) | w, h, bpp, JPEG quality O = 1.000; container 0.500 | `a41_files.json` DC-A FRLL-Morphs/stylegan; RSX `rsx_read.md` |
| G-test (native, held out) | StyleGAN2 W+ (e4e) latent-average morphs of FEI pairs, scaled to the bona fide face size | FEI frontal neutral captures (n 385) | resolution (by construction) | not logged in the sources read | PROTOCOL l.122-126 |
| H4 (held out, generator vs camera) | MIPGAN-I-style (StyleGAN v1) at 112 px | CASIA camera source crops | nothing | bytes 0.983 (orig) / 0.990 (pp) | PROTOCOL A33 / A34; `a36_read_own.md` baselines |
| **H4b** (generator vs generator) | the same H4 morphs | the same StyleGAN v1's single-identity render of the host | camera vs generator | **bytes-only 0.912** (two-identity optimisation gives smoother files; not neutralised) | PROTOCOL A34 (l.8517-8545) |
| **H3** (generator vs generator) | StyleGAN3-T G((w+A + w+B)/2), 423 pairs, orig + pp | the same generator's G(w+C) | camera vs generator, native size (both 1024²) | bytes 0.526 / eye geometry 0.560 (orig), 0.488 / 0.578 (pp); combined covariate floor 0.607 (A30 a5) or 0.617 / 0.605 (A41 DC-B (c)) | PROTOCOL A35; `a36_read_own.md` baselines; A41 meta.json DC-B |
| **X4** (spread-matched H3) | the H3 morphs | renders decoded at m + (w_C − m)/√2 (the A37 a37spread pool) | latent-spread asymmetry | not logged per pool | A41 amendment G `a41g_x4.json/md` |
| A37 descriptive pools (releases only) | the H3 morphs | truncated renders (ψ 0.5 / 0.7), re-decodes, re-stored (box 256 → x2.07) renders | typicality / fine texture | trunc50 vs plain renders differ in image properties at 0.96 (A37 F1) | `a41g_x4.json` detail.<row>.networks[0] |
| Renders vs camera (H-new-83) | H3 single-person renders, scored as positives | FRLL / FFHQ native (same framing) / FEI photos | tests whether the row flags *any* generator output | - | A36 amendment 1 `a36_a1.md` (1) |
| Morph-side storage ladder (S10) | MIPGAN-I / II, FRLL StyleGAN re-stored as JPEG 90 / 70 / 50 or halved (resample50) | native bona fide | tests for a storage-format cue | - | A41 `a41_eval.json` H-new-142 |

## 3. Main comparison table (one row per published method)

Columns: **Native** = EER % (thresholded, lower is better), in the order MIPGAN-I / MIPGAN-II / FRLL StyleGAN /
G-test. **H3** = AUC (threshold free; 0.5 is chance; above 0.5 means morphs score above single-person renders),
orig full pairs. **X4** = AUC of the H3 morphs against the spread-matched renders, orig, with a pair-clustered 95% CI
(423 pairs, B 10,000). **H4b** = AUC; the bytes-only floor is 0.912. **Renders vs camera** = AUC of the H3 orig
renders against FRLL / FFHQ native / FEI photos, with the morphs-vs-FRLL control in brackets. Data: d0 = SMDD only
(d0b = SMDD bona fide only), unless marked.

| # | Method (what it is) | Networks | Native EER % MIPGAN-I / II / FRLL SG / G-test | H3 AUC orig [CI] | X4 AUC orig [95%] | H4b AUC (floor 0.912) | Renders vs camera FRLL / FFHQ / FEI (morphs vs FRLL) | Plain reading |
|---|---|---|---|---|---|---|---|---|
| M1 | Inception-MAD, Inception-v3 from scratch; **our re-implementation of the published recipe**, R × d0 | 5 seeds | 19.8 ± 7.5† / 26.5 ± 8.6† / 15.0 ± 3.1† / 37.5 ± 4.8 | 0.555 ± 0.007 [0.535, 0.576] | 0.441 [0.417, 0.465] | 0.672 | 0.969 / 0.977 / 0.644 (0.990) | Flags StyleGAN3 single-person renders against FRLL and FFHQ photos about as strongly as it flags morphs. With both classes from the generator it sits at the eye-geometry floor (0.560), and on spread-matched renders it ranks the renders higher. |
| M2 | MorphHRNet-style, HRNet-W48 from scratch; re-implemented recipe, R × d0 | 5 seeds | 43.0 ± 18.8† / 45.4 ± 20.0† / 39.3 ± 13.0† / 38.2 ± 4.3 | 0.591 ± 0.025 [0.572, 0.610] (the highest row; D vs floor +0.031, Bonferroni LB −0.003) | 0.469 [0.446, 0.491] | 0.678 | 0.440 / 0.886 / 0.587 (0.533) | Weak even on the native GAN sets. Against FRLL it barely separates renders or morphs from camera photos. Its small H3 edge is below the combined file-size + eye-geometry floor (0.607-0.617) and is gone on spread-matched renders. Single networks reach a within-pair θ of 0.66, so never write "no network". |
| M3 | MADation recipe, CLIP ViT-B/16 + LoRA; re-implemented recipe, R × d0 | 8 seeds | 7.0 ± 1.9 / 3.9 ± 1.6 / 11.3 ± 2.4 / 35.6 ± 6.5 | **0.448** ± 0.030 [0.426, 0.471] (reverse; 95% pair CI [0.420, 0.475]) | 0.458 [0.431, 0.486] | 0.847 | 0.951 / 0.956 / 0.967 (0.941) | A consistent generator-output detector on all three camera pools. With both sides from the generator it ranks single-person renders above two-person morphs. Its strong MIPGAN numbers are generator-vs-camera results. |
| M3L | MADation recipe, CLIP ViT-L/14 + LoRA; re-implemented recipe, R × d0 | 5 seeds | 0.8 / 0.1 / 5.9 / 37.6 ± 5.9 | **0.401** ± 0.040 [0.375, 0.428] (reverse) | 0.442 [0.411, 0.474] | 0.923 (+0.010 over the floor, Bonferroni LB −0.031: not above it) | 0.934 / 0.940 / 0.957 (0.834) | Same as M3 but stronger: near-perfect MIPGAN EER, the clearest reversal on H3, and on H4b only what file size gives. |
| M4 | SelfMAD-style, HRNet-W18 (ImageNet) + SAM + self-blended fakes; re-implemented recipe, R × d0b | 5 seeds | 34.5 ± 8.7† / 34.4 ± 8.7† / 46.1 ± 4.1† / 24.3 ± 4.2 | 0.551 ± 0.019 [0.531, 0.573] | 0.517 [0.493, 0.541] (the only primary row with an upper bound above 0.5) | 0.403 (scores renders above morphs) | 0.314 / 0.394 / 0.999 (0.354) | It does not even read "generator output" consistently: it scores FRLL and FFHQ photos above the renders and FEI photos below them. It is at chance on morph vs render. |
| M5 | PW-MAD, DenseNet-121 with pixel-wise supervision; re-implemented recipe, R × d0 | 8 seeds | 36.8 ± 6.5† / 37.4 ± 8.0† / 39.0 ± 5.7† / 56.0 ± 10.2 (inverted) | 0.564 ± 0.020 [0.544, 0.585] | 0.460 [0.436, 0.484] | 0.455 | 0.881 / 0.845 / 0.801 (0.908) | A moderate generator-output detector on StyleGAN3. It is inverted on the StyleGAN v1 held-out set (H4 orig 0.338: camera photos above MIPGAN-style morphs) and at chance on generator vs generator. |
| M6 | OrthoMAD, ResNet-18 from scratch; re-implemented recipe, R × d0 | 5 seeds | 37.0 ± 6.1† / 36.6 ± 6.2† / 35.5 ± 2.5† / 33.7 ± 3.8 | 0.574 ± 0.009 [0.555, 0.594] | 0.469 [0.445, 0.493] | 0.647 | 0.525 / 0.913 / 0.572 (0.621) | Its scores depend on which camera pool it is compared with. On morph vs render it is at the image-property floor, and the edge is gone on spread-matched renders. |
| M8 | MixFaceNet-MAD, MixFaceNet-S from scratch; re-implemented recipe, R × d0 | 5 seeds | 35.5 ± 13.0† / 34.9 ± 12.8† / 23.0 ± 7.3† / 37.3 ± 4.8 | 0.560 ± 0.014 [0.540, 0.578] | 0.448 [0.426, 0.470] | 0.623 | 0.763 / 0.963 / 0.662 (0.821) | Like M6: depends on the camera pool, and at chance once both classes come from the generator. |
| M8O | MixFaceNet-MAD, **official training code** retrained here, O × d0 | 5 seeds | 44.9 / 42.9 / 32.8 (no-TTA) / 36.8 ± 3.2 | 0.556 ± 0.027 [0.537, 0.574] | 0.453 [0.430, 0.475] | 0.630 | 0.697 / 0.954 / 0.629 (0.763) | Indistinguishable from M8 on GAN sets. Near chance on H3. |
| REL-MFN | **Official MixFaceNet-MAD release** (mixfacenet_SMDD.pth), on our 512 eye-aligned frames; descriptive | 1 | 47.0 / 43.2 / 28.4 / 39.5 | 0.581 [0.559, 0.603] (90%) | not scored | 0.695 | 0.588 / 0.875 / 0.651 (0.689) | Out of its input domain on our frames (S_MFN not within 5 points of the published numbers). Near chance on the GAN benchmarks and on H3. Adds no weight to C3 (near chance on VALX-A*, EER 46.4%). |
| REL-SM | **Official SelfMAD release** (HRNet-W18), its own preprocessing (dlib crop, cv2 resize) | 1 | **0.5 / 0.1** / 14.2 / not logged | **0.353** [0.331, 0.375] (the strongest reversal) | 0.447 [0.419, 0.474] | 0.405 | 1.000 / 0.952 / n.a. | It separates StyleGAN3 output from camera photos almost perfectly, yet ranks single-person renders well above two-person morphs. Its near-perfect MIPGAN EERs are generator PNG against camera JPEG. |
| REL-SM-p | The same release through our pipeline; descriptive | 1 | 1.1 / 1.0 / 27.9 / 61.5 (inverted) | 0.360 [0.337, 0.384] | 0.452 [0.423, 0.480] | 0.511 | 0.997 / 0.942 / 0.877 (0.995) | The same pattern as its own preprocessing, so the crop is not the cause. |
| REL-B16 | **Official MADation ViT-B/16 weights**, on our frames | 1 | 18.4 [13.4, 23.6] / 13.5 [9.4, 18.0] / 23.1 / **9.9** | 0.554 [0.530, 0.578] | **0.423** [0.395, 0.451] (the lowest row) | 0.716 | 0.947 / 0.980 / 0.964 (0.975) | The best G-test row of any published method, and a strong generator-output detector on all three pools. On morph vs render it is at chance on H3 and ranks the spread-matched renders higher. Its 9.9% G-test EER is a generator-vs-camera result. |
| REL-L14 | **Official MADation ViT-L/14 weights**, on our frames | 1 | 11.9 [8.0, 15.6] / 9.9 [7.0, 14.1] / 52.4 (inverted) / 69.5 (inverted) | **0.427** [0.404, 0.451] (reverse) | 0.445 [0.417, 0.472] | 0.902 (at the floor) | 0.904 / 0.808 / 0.924 (0.849) | It flags StyleGAN3 renders against camera photos, yet is inverted on FRLL StyleGAN and the G-test (StyleGAN2-type latent-average morphs). It reverses H3, and on H4b it gives only what file size gives. |
| REL-FE-B16 | Official MADation baseline FE (frozen CLIP ViT-B/16 + head); descriptive | 1 | 35.1 / 38.4 / 35.3 / 35.1 | 0.514 [0.491, 0.537] | 0.451 [0.425, 0.477] | 0.661 | 0.922 / 0.892 / 0.656 (0.932) | Frozen CLIP alone already reads generator output against FRLL and FFHQ. At chance on morph vs render. |
| REL-FE-L14 | Official FE ViT-L/14; descriptive | 1 | 8.5 / 10.3 / 19.2 / 29.1 | 0.505 [0.480, 0.530] | 0.475 [0.445, 0.505] | 0.804 | 0.887 / 0.903 / 0.861 (0.902) | The same: strong on MIPGAN against camera photos, at chance on generator vs generator. |
| REL-FS-B16 | Official FS (ViT-B/16 from scratch + head); descriptive | 1 | 17.8 / 17.9 / 17.1 / 46.4 | 0.511 [0.479, 0.542] | 0.466 [0.429, 0.503] | 0.546 | 0.877 / 0.509 / 0.569 (0.889) | Depends on the camera pool. At chance on generator vs generator. |
| REL-FS-L14 | Official FS ViT-L/14; descriptive | 1 | 32.5 / 31.4 / 44.6 / 67.4 (inverted) | 0.540 [0.514, 0.566] | 0.470 [0.440, 0.499] | 0.641 | 0.594 / 0.611 / 0.465 (0.637) | Weak everywhere. At chance on generator vs generator. |

Row grouping for the registered tests (A36 H-new-72, A41 C3 / F8 / H-new-146) has **12 primary rows**: M1, M2, M3,
M3L, M4, M5, M6, M8 and M8O (together 51 retrained networks), plus REL-SM, REL-B16 and REL-L14. REL-SM-p, the four
FE / FS rows and REL-MFN are descriptive.

### Sources and status for each column

- **Native, retrained rows:**
  - † marks the arm mean ± SD over seeds of the TTA family EERs at the VALX-A*-early-stopped checkpoint (R-es),
    E7 pool (equal to native for these families). It was computed for this table from the per-network values in
    `experiments/A12-BR_benchmark_recipes/raw/A12_3e_report.json` (`networks[].main.family_eer`, keys
    `MAD22/MIPGAN_I`, `MAD22/MIPGAN_II`, `FRLL-Morphs/stylegan`). No reader prints these arm means.
  - M3: means as logged in `smadcvpr/results/RSX/rsx_read.md`, "MADation published recipe R, SMDD (d0)", n 8; the
    SDs (1.9, 1.6, 2.4) are computed as †.
  - M3L: as logged in `a36_read_own.md` (B), "full" EERs (0.8, 0.1, 5.9).
  - M8O: no-TTA, from `a36_a2.md` "RSX, UA8c and MAD22"; the TTA values 45.8 / 43.7 / 33.6 are in `rsx_read.md`.
  - G-test: mean of the neutral and smiling family EERs, seed mean ± SD, from `smadcvpr/results/A12/a12_5_read_stage1.md`
    (i).
  - All of these are thresholded EERs, descriptive: A12.3e early unseal and A12.5, exploratory, never a W3 input. The
    benchmark sets are design-seen.
- **Native, releases:**
  - REL-SM and REL-SM-p: `rsx_read.md` (A32, H2 "GAN contrast", descriptive; single network, no CI). REL-SM-p's
    G-test is from `a12_5_read_stage1.md`. REL-SM's G-test is not logged.
  - REL-B16 / REL-L14 MIPGAN: A41 `a41_eval.json` DC-8, with person-clustered 95% CIs. The published values are
    33.37 / 22.21 and 20.32 / 9.06; status "not reproduced", except L14 MIPGAN-II, which is "reproduced". FRLL SG
    and the FE / FS values come from `a36_read_own.md` "RSX" and "sanity vs published" lines; G-test from
    `a36_read_own.md` "G-test".
  - REL-MFN: `a36_a2.md`.
  - All descriptive.
- **H3:**
  - Retrained rows: seed mean ± t95 with a [90% pair-bootstrap CI]; releases: [90% pair CI]. Both from
    `experiments/A36_published-detector-shortcuts/raw/results/a36_read_own.md` (C). Threshold free.
  - Registered: A36 H-new-72, verdict "neither" in both pools. Also A41 F8 / H-new-141 (supported, IUT p 0.0027),
    whose one-sided bounds are in section 4.
  - REL-MFN: `a36_a2.md`, descriptive (A36 amendment 2).
- **X4:** `smadcvpr/results/A41/a41g_x4.md`. Registered rule H-new-146 (A41 amendment G; the numbers were blind).
  Result: "no kill in any of the 12 primary rows". The five descriptive rows ran too.
- **H4b:** `a36_read_own.md` (C), with the floor 0.912 from the same file's baselines. Registered (the A36 H-new-72
  H4b route). REL-MFN from `a36_a2.md`.
- **Renders vs camera:**
  - From `a36_a1.md` (1), seed mean with [pair × person 90%] CIs in the file. Registered as A36 amendment 1 H-new-83
    (verdict "neither"; not blind). The FFHQ and FEI pools and the Spearman of 0.95 are descriptive and post hoc.
  - REL-SM: `experiments/A39_batch-before-window-close/README.md` R3 panel (90%), descriptive.
  - REL-MFN: `a36_a2.md`.

## 4. Supporting detail

### 4a. H3 bounds (A41 F8, `smadcvpr/results/A41/a41_h3.md`; registered, one-sided 95% pair UB, seed UB) and H3 pp, X4 pp, H4

| Row | H3 orig full (pair UB) | H3 orig potent (pair UB) | H3 pp full | X4 pp [95%] | H4 orig / pp (bytes floor 0.983 / 0.990) |
|---|---|---|---|---|---|
| M1 | 0.555 (0.576; seed UB 0.561) | 0.560 (0.589) | 0.498 | 0.445 [0.425, 0.464] | 0.794 / 0.824 |
| M2 | 0.591 (0.609; seed 0.610) | **0.592 (0.621)**, the largest component | 0.526 | 0.464 [0.446, 0.481] | 0.805 / 0.801 |
| M3 | 0.448 (0.470) | 0.471 (0.503) | 0.440 | 0.460 [0.433, 0.488] | 0.947 / 0.878 |
| M3L | 0.401 (0.428) | 0.419 (0.455) | 0.402 | 0.458 [0.427, 0.489] | 0.998 / 0.981 |
| M4 | 0.551 (0.572) | 0.574 (0.605) | 0.562 | 0.506 [0.489, 0.524] | 0.852 / 0.919 |
| M5 | 0.564 (0.585) | 0.572 (0.602) | 0.499 | 0.434 [0.415, 0.453] | **0.338 / 0.332** |
| M6 | 0.574 (0.595) | 0.569 (0.598) | 0.499 | 0.451 [0.432, 0.470] | 0.770 / 0.816 |
| M8 | 0.560 (0.579) | 0.560 (0.586) | 0.517 | 0.458 [0.439, 0.477] | 0.755 / 0.821 |
| M8O | 0.556 (0.575) | 0.560 (0.586) | 0.501 | 0.456 [0.438, 0.474] | 0.751 / 0.804 |
| REL-SM | 0.353 (0.375) | 0.374 (0.404) | 0.372 | 0.467 [0.441, 0.493] | 0.849 / 0.946 |
| REL-B16 | 0.554 (0.577) | 0.555 (0.587) | 0.495 | 0.420 [0.393, 0.445] | 0.911 / 0.906 |
| REL-L14 | 0.427 (0.451) | 0.446 (0.481) | 0.409 | 0.456 [0.430, 0.483] | 0.975 / 0.965 |
| REL-SM-p | 0.360 | - | 0.375 | 0.472 [0.445, 0.499] | 0.743 / 0.868 |
| REL-FE-B16 / FE-L14 | 0.514 / 0.505 | - | 0.511 / 0.504 | 0.451 / 0.477 | 0.705 / 0.762; 0.915 / 0.904 |
| REL-FS-B16 / FS-L14 | 0.511 / 0.540 | - | 0.497 / 0.509 | 0.495 / 0.455 | 0.669 / 0.690; 0.671 / 0.637 |
| REL-MFN | 0.581 | - | 0.537 [0.518, 0.556] | not scored | 0.828 / 0.837 |

- Potent pairs are those whose morph verifies both contributors: 203 of 423 (orig) and 212 of 423 (pp).
- Reverse separation (95% pair CI below 0.5) occurs in 15 cells of four rows: M3, M3L, REL-SM and REL-L14, at
  0.353-0.455 (`a41_h3.md`).
- H4 has no verdict cell and is descriptive; its values are from `a36_read_own.md` (C) and, for REL-MFN, `a36_a2.md`.
- Post hoc, descriptive (A36 amendment 1 (6)): our training protocol P lowers H3 orig AUC below the published
  recipe R in 14 of 14 method × data cells (−0.008 to −0.197).

### 4b. A37 control pools on the release lines (descriptive point estimates)

Source: `a41g_x4.json` `detail.<row>.networks[0]`. The registered rule treats trunc50, trunc70, redec and restore as
descriptive, and scored them for the releases only. No CI was printed. Each value is AUC(morphs vs that render
pool).

| Release | H3 orig | spread (X4) | trunc50 orig / pp | trunc70 orig | re-decode | re-stored (morphs vs renders, both box-256) |
|---|---|---|---|---|---|---|
| REL-SM (own) | 0.353 | 0.447 | 0.883 / 0.910 | 0.681 | 0.353 | 0.403 |
| REL-SM-p | 0.360 | 0.452 | 0.830 / 0.863 | 0.661 | 0.360 | 0.390 |
| REL-B16 | 0.554 | 0.423 | 0.715 / 0.746 | 0.591 | 0.554 | 0.568 |
| REL-L14 | 0.427 | 0.445 | 0.838 / 0.850 | 0.657 | 0.427 | 0.441 |
| FE-B16 / FE-L14 | 0.514 / 0.505 | 0.451 / 0.475 | 0.592 / 0.591 | 0.537 / 0.562 | = H3 | 0.519 / 0.516 |
| FS-B16 / FS-L14 | 0.511 / 0.540 | 0.466 / 0.470 | 0.566 / 0.344 | 0.519 / 0.448 | = H3 | 0.507 / 0.546 |

Reading:
- **Re-decode** equals H3 exactly, because the re-decodes are byte-identical to the H3 renders (423 of 423, A37).
  This is a pipeline sanity check.
- **Re-stored:** removing the fine texture from both classes leaves each release about where it was on H3.
- **Truncated renders** (more average) score *less* morph-like than the morphs for most releases. Truncated renders
  also differ in simple image properties at AUC 0.96 (A37 review F1), so this must **not** be read as "the networks
  read typicality".
- The same pools for our own 84 A30 networks are in A37: spread-matched AUC 42.8-49.2 in all 14 arms; truncation
  "overshoot" in 8 of 8 b / c arms; arm a still flags 96-99% of the re-stored renders. Those are our networks, not
  published methods, and MADMamba is not among them.

### 4c. Morph-side storage ladder (A41 S10 / H-new-142)

Registered secondary rule; reader labels stored as open. Source: `a41_eval.json` `H-new-142`. Each value is the
EER change in points [95%] when the *morphs* are re-stored. "Storage-format cue" requires the lower bound of the
JPEG-90 rise to be at least +10.

| Row | MIPGAN-I: jpeg90 / jpeg50 / resample50 | MIPGAN-II: jpeg90 / jpeg50 / resample50 | FRLL SG: jpeg90 / jpeg50 / resample50 | Label |
|---|---|---|---|---|
| REL-SM (own) | n.a. / +4.50 [2.02, 7.63] / −0.44 | n.a. / +3.29 / 0.00 | n.a. / +11.14 [6.68, 16.39] / **−9.90 [−15.62, −6.25]** | not evaluable (no jpeg90) |
| REL-SM-p | +0.60 / +3.89 / −1.04 | +0.17 / +2.68 / −0.60 | −0.58 / +15.68 / **−11.30 [−17.08, −7.11]** | no format cue / no format cue / graded |
| REL-B16 | +2.25 [−0.56, 5.53] / +4.93 / −9.26 | +3.89 [1.37, 7.14] / +8.82 / −5.81 | −2.39 / +15.68 / −7.34 | graded on all three |
| REL-L14 | +1.48 / −4.50 / −4.93 | +2.41 / −3.73 / −3.12 | 0.00 / −39.11 / −7.75 | graded / graded / no format cue |
| M3 (n 8) | +3.21 [1.71, 4.91] / +1.62 / −0.03 | +2.00 / +0.27 / −0.31 | +0.18 / +2.16 / +0.92 | graded / graded / no format cue |
| M3L (n 5) | +0.09 / +1.35 / +0.24 | +0.21 / +0.42 / 0.00 | −0.92 / +3.70 / +0.74 | no format cue on all three |

- No row reaches "storage-format cue". C4 therefore keeps the construction sentence only.
- Descriptive and not tested: halving the FRLL StyleGAN morphs makes the SelfMAD release detect them *better* (EER
  down 9.9-11.3 points). Its scores move with the morphs' resampling history too. This is consistent with C1's
  "processing history" reading, but nothing was tested here.

### 4d. Other checks that bear on the GAN column

- **Cue-matched benchmark subsets** (A36 H-new-74, descriptive; `a36_read_own.md` (B)): on MIPGAN-I (n 77 per
  class), MIPGAN-II (n 70) and FRLL StyleGAN (n 52), every row that enters is "cue-robust" when aligned-PNG size and
  eye geometry are matched. Examples: REL-SM MIPGAN-I 0.5 → 0.0; M3L 0.8 → 1.0. The rows that enter rank renders
  above morphs on H3, so their MIPGAN and StyleGAN EERs read as synthetic vs camera. The native file size still
  separates every matched subset, so "cue-robust" never means "no source shortcut".
- **X4's reverse direction is not explained by aligned file size** (A42 H-new-245, descriptive, post hoc;
  `experiments/A42_shortcut-followups-descriptive/README.md`): per-row ρ is −0.194 to 0.159. On the same 141 pairs
  the byte-matched AUC is 0.432-0.485 (pooled 0.460). These are not 10 replications.
- **The cross-source check depends on the camera pool** (A36 amendment 1):
  - Against FFHQ native photos with the renders' framing, 10 of 11 primary rows rank renders above photos at AUC
    0.81-0.98. Against FEI the count is 6, and against FRLL 7 (≥ 0.75).
  - Our-protocol rows separate renders from all three pools (median worst pool 0.94-0.95). The published recipes do
    not (0.61-0.65); only 2 of 14 R rows reach 0.92, both CLIP (post hoc).
- **Thresholded render flag rates are uninformative:** the SMDD rows' VALX-A* thresholds are near chance, so they
  flag 19-100% of FRLL photos (A36 H-new-76, post-result review). Cross-method tables should use AUC and name the
  camera pool.
- **REL-MFN loader check** (A39 S2): on its own SMDD training files, EER 0.45% (AUC 0.9997). The loader is right; the
  miss is our frames or the bona fide source, and the cause is not separated.

## 5. How each method works against GAN morphs once the camera / generator difference is gone

- **MADation family (M3, M3L recipes; the official ViT-B/16 and ViT-L/14; FE).** These rows are reliable detectors
  of generator output.
  - Threshold free, they separate StyleGAN3 single-person renders from FRLL, FFHQ and FEI photos at 0.81-0.98 (one
  exception: FE ViT-B/16 against FEI, 0.66). That explains their good native MIPGAN numbers (0.1-18%) and, for the
  official ViT-B/16, its 9.9% G-test.
  - When both classes come from the generator, they give the single-person render the same or a higher morph score:
  H3 0.40-0.45 for M3, M3L and REL-L14, 0.55 for REL-B16, and 0.42-0.48 on spread-matched renders.
  - On StyleGAN v1 (H4b) the ViT-L/14 rows reach 0.90-0.92 and M3 0.85, at or below the 0.912 that the morphs'
  smoother files give. REL-B16 reaches 0.72.
  - Frozen CLIP with a linear head (FE) shows the same render-vs-camera pattern against FRLL and FFHQ (0.92 / 0.89
  for ViT-B/16). So the pattern is largely present in the pretrained features (descriptive, one network each).
- **SelfMAD release (own preprocessing; also through our pipeline).**
  - It separates StyleGAN3 output from camera photos almost perfectly (1.000 against FRLL, 0.952 against FFHQ), and
  its native MIPGAN EERs are 0.5 / 0.1%.
  - It also ranks single-person renders furthest above two-person morphs of any row (H3 0.353). Its "morph" score
  rises for anything generated or resampled, not for two identities.
  - The same holds through our pipeline (0.360), so its face crop is not the cause.
  - It is at chance on spread-matched renders (0.447) and below the file-size floor on H4b (0.405).
- **From-scratch CNN recipes (Inception-MAD, MorphHRNet-style, PW-MAD, OrthoMAD, MixFaceNet-MAD R and official
  code) and SelfMAD-style.**
  - Retrained on SMDD alone, they are already weak or inverted on the native GAN sets (15-46% EER; PW-MAD inverted on
  the G-test and on H4).
  - They do not read generator output consistently: whether renders look more morph-like than photos depends on the
  camera pool (e.g. MorphHRNet-style 0.44 against FRLL, 0.89 against FFHQ).
  - On H3 they sit at 0.55-0.59, inside the file-size + eye-position covariate floors (0.56-0.62). On spread-matched
  renders they fall to 0.44-0.52, and on H4b they stay far below the file-size floor.
  - MorphHRNet-style's 0.592 (orig, potent pairs) is the best primary-row cell; single M2 networks reach a
  within-pair θ of 0.66.
  - The published recipes trained on *our* data (R × d1, descriptive, named post hoc) reach 0.608-0.628 on orig only.
  None of them is above the combined floor of 0.607 by its CI (A36 amendment 1 (6)).
- **Official MixFaceNet-MAD release.** On our frames it is out of its input domain and near chance on everything GAN
  (H3 0.581, MIPGAN 47 / 43%). Its loader is verified, so this says nothing about the method on its own crops.

## 6. Allowed wording (CONCLUSIONS.md "What we can claim about shortcuts", final after A41 G2) and what to drop

- **C3** (12 published rows, 51 networks; StyleGAN3; grade "strong (narrow)"). The paper may write:
  > "No primary row scores the morphs above single-person renders at AUC ≥ 0.65 (one-sided pair and seed bounds;
  > full / potent, orig / pp); 15 row-cells rank the renders higher (0.35–0.45); on spread-matched renders 0.42–0.52,
  > 11 of 12 with an upper bound below 0.5."

  It does **not** show: "does not separate", that the detectors are blind to identity, anything about other
  generators, or anything causal. Never write "no signal" or "no network". X4 sits near 0.5 by construction, so it is
  weak evidence. Report H3 and spread-matched H3 side by side.
- **C4** (MAD22 MIPGAN-I/II, FRLL StyleGAN, the G-test; "construction sentence"). The paper may write:
  > "These sets compare generator output (PNG) with camera photos (JPEG)."

  It does **not** show any storage-format cue (no row reads one), and it allows no causal sentence about GANs. See
  flag 1 below on "PNG" for FRLL StyleGAN.
- **B** (the ten FRLL-based diffusion and MAD22 cells, which include MIPGAN-I/II). The paper may write:
  > "Morph and bona fide files differ in documented construction attributes that alone separate the classes (O = 1.000
  > per decision cell)."

  It does not show that the detectors use those attributes.
- **Drop list items relevant here:**
  - "Published S-MAD detectors rely on shortcuts" (general) and "for every method".
  - "Does not separate", "no signal" and "no network" for C3.
  - "Resolution shortcut".
  - The MixFaceNet-MAD resolution sentence.
  - The probe as identity evidence.
  - Any cue-floor sentence from A41's frame cues: DC-B (a)/(b) are "leaky (not read)". The floors quoted above come
    from A36 baselines and A41 DC-A / DC-B (c), not from DC-B (a)/(b).
- **Printed beside every claim:** "MADMamba not evaluated on H3 (sealed)".

## 7. Flags for the author

1. **C4 wording vs the file headers.** A41 DC-A (`a41_files.json`) records the FRLL StyleGAN morphs as **JPEG**
   (median quality 74.7, 1024 px, container O 0.500), against JPEG q 98.5 bona fide at 1350 px. The A37 disclosures
   say the same ("JPEG quality 75 at 1024 px"). Only MAD22 MIPGAN-I/II are PNG against JPEG (container O 1.000). The
   G-test's containers are not in DC-A. As registered, C4's "(PNG) ... (JPEG)" does not hold literally for FRLL
   StyleGAN. Your Q4 sign-off can only weaken wording, for example "generator output (PNG, or JPEG q≈75 for FRLL
   StyleGAN) with camera photos (JPEG)". Not changed here.
2. **† arm means** for M1, M2, M4, M5, M6 and M8 on MIPGAN-I/II and FRLL StyleGAN were computed for this table from
   logged per-network values; no reader prints them. They agree with every logged arm value I could check (M3 7.0 /
   3.9 / 11.3; M3L 0.8 / 0.1 / 5.9; M8O TTA 45.8 / 43.7 / 33.6). Re-derive them with a registered reader before
   they go into the paper.
3. Four cells are missing:
   - X4 was not run for the official MixFaceNet-MAD release.
   - No G-test is logged for the SelfMAD release with its own preprocessing.
   - Truncation and re-stored pools exist for the release lines only, as point estimates with no CI.
   - H4 has no registered verdict.
4. **Mixed CI levels.** A36 intervals are 90% pair (or pair × person). A41 H3 bounds are one-sided 95% pair, and X4 is
   two-sided 95% pair. The DC-8 MIPGAN CIs are person-clustered 95%. Keep the level next to each number.
5. **Disclosure.** `smadcvpr/results/RSX/rsx_read.md`, opened for the SelfMAD / MADation / MixFaceNet rows, also
   contains league (L0-L2) and W3 rows. They were not used or reported. `CONCLUSIONS.md` was read only in its
   shortcut-claims and published-methods sections.

## 8. Files read (all relative to /home/narolski/mambamorph-code)

- `experiments/CONCLUSIONS.md` (sections "What we can claim about shortcuts" and "Published methods in our
  pipeline")
- A36: `experiments/A36_published-detector-shortcuts/README.md`, `raw/A36_networks.tsv`, `raw/A36_releases.tsv`,
  `raw/results/a36_read_own.md`, `a36_a1.md`, `a36_a2.md`
- A37: `experiments/A37_stylegan3-render-controls/README.md`
- A39: `experiments/A39_batch-before-window-close/README.md`
- A41: `experiments/A41_shortcut-proof-zero-gpu/README.md`, `meta.json`, and `smadcvpr/results/A41/` (`a41_h3.md`,
  `a41g_x4.md/.json`, `a41_eval.md/.json`, `a41_files.md/.json`, `a41_img.md`, `a41_decide_full_g2.md`)
- A42: `experiments/A42_shortcut-followups-descriptive/README.md`
- A12-BR: `experiments/A12-BR_benchmark_recipes/README.md`, `raw/A12_3e_report.md/.json`
- A12-4: `experiments/A12-4_benchmark-followups/README.md`, `smadcvpr/results/A12/a12_4_read_stage1.md`
- A12-5: `smadcvpr/results/A12/a12_5_read_stage1.md`
- A32: `experiments/A32-RSX_resolution-shortcut/README.md`, `smadcvpr/results/RSX/rsx_read.md` (published rows only)
- A38: `experiments/A38_twins-and-feature-probe/README.md`
- `smadcvpr/PROTOCOL.md` (G-test definition l.122-126; selection-seen note l.180; A33 H4, A34 H4b, A35 H3
  registrations)
- `smadcvpr/plans/A12/plan.md` (method list)
