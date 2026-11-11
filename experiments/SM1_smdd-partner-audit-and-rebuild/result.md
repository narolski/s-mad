# SMDD five-partner audit and rebuild of the standard training set (SM1): result

Owner run, 11 Nov 2026. Pre-registration: `prereg.md` (with amendment A1 from the pre-run review, registered before
any score). Code: `src/SM1/`. Large outputs: `/mnt/t7/smad_next/SM1/`. Status: **in progress** (sections below are
filled as stages finish).

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
SMDD's documented design (see the paper quote below), not a finding.

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
quoted condition: the Part 2 audit morphs (keys and partners are `os25k_m_t` source renders), arms (b), (b′) and the
dose arms (release source data and pairing). Arms (c), (c′), (d) use the genuine renders only, which the sentence does
not name, but CC BY-NC-SA share-alike applies to any distribution. All rebuilt images stay internal (T7 and the WCSS
project space).

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
  (AR1) pairs; halves average within 0.5 grey level of the morph on every pair with halves (16,036 checked by
  assertion: 15,000 + 536 + 500 smoke).
- Cross-machine equality: leaseB (x86, OpenCV 4.11.0) outputs equal the DGX (ARM, OpenCV 4.11.0) outputs on every
  compared file (32 per task, plus the 2,000 smoke files of c and c′); our 536 AR1 morphs equal AR1's own OpenCV R4
  files (`ar1h_vs_ar1_r4.json`).

## T-A and T-B: tests with no new image (A3, A8; `tab_sub.json`)

Whole-file path (A6), registered subsample (A8: per split 500 morphs per partner, 1,000 genuine, 400 non-contributor
source renders, the 5 partner renders). Threshold t = EER threshold of the training split. Miss rate in %, interval
from 2,000 bootstrap draws over first contributors. The training morphs are these detectors' own training images.

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

pending (audit crops finishing; then the five releases on own crops and on whole files)

## Part 3: rebuild arms on frozen features

**Rebuild acceptance, Laplacian variance (A3, A4; `lapvar.json`; 2,000 morphs vs 2,000 genuine-class images per arm;
AUC = P(morph has the lower variance)).** No rebuilt arm is accepted (bar: AUC ≤ 0.65), so every reading of the
rebuilt arms below is labelled **"still separable by sharpness"** and is descriptive; falsifier readings involving
them are printed but not decisive.

| Arm | AUC at stored size | AUC at the loader's 224 px | median variance morph / genuine (stored) |
|---|---|---|---|
| a release (reference) | 0.993 | 0.988 | 209 / 854 |
| b | 0.999 | 0.998 | 161 / 859 |
| b′ | 0.998 | 0.995 | 177 / 856 |
| c | 0.997 | 0.993 | 188 / 851 |
| c′ | 0.998 | 0.995 | 180 / 843 |
| d (halves as genuine) | 0.936 | 0.949 | 189 / 532 |
| e (history crossing; acceptance at 224 px) | 0.856 | **0.716** | 336 / 768 |
| f (e + JPEG 90 / 70 copies; acceptance at 224 px) | 0.843 | **0.724** | 319 / 733 |
| K = 50 | 0.999 | 0.997 | 175 / 863 |
| K = 500 | 0.998 | 0.995 | 178 / 858 |

A (c) morph against its own two halves: AUC 0.881, median variance ratio morph / mean of its halves 0.52. All rebuilt
files are 256 x 256. What would be needed to pass: genuine-class images with the morphs' sharpness (the softening of
blending itself), i.e. more of the approved shrink-and-enlarge history or another approved softening on the genuine
side; (e) moves the AUC from 0.99 to 0.72 at the loader size; adding JPEG copies (f) leaves it at 0.72.

**Feature platform (A7):** all features from Athena job 3545820 (A100, torch 2.2.1). Equivalence with the DGX
features on all 14,120 FRLL evaluation frames: max |Δ feature| 1.0e-3, max |Δ FE-header logit| 0.097, AUC of the FE
header (all FRLL morphs vs genuine) 0.88252 on Athena vs 0.88253 on the DGX (Δ −1.1e-5) (`feat_equivalence.json`).
**Pool-cue check (A1.3):** a head cannot tell `os25k_bf_t` from `os25k_m_t` renders, out-of-fold AUC 0.507
(5,000 + 5,000; `pool_cue.json`).

**Smoke pass (500 morph pairs + 834 genuine renders per arm, seed 401 only; `p3_smoke.json`; person-bootstrap
B = 1,000).** EER in %, flag rates as shares. Not the registered result (that is the 5-seed full run below).

| Arm | landmark-7 EER native | E7 | rise | diffusion-7 EER native | rise | GAN-3 EER | halves flagged (AR1 EER thr) | R2w OpenCV flagged | R2w FaceMorpher flagged | AUC R4 vs R2w (OpenCV) | AUC halves vs R0 | neutral above smiling |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a release | 13.0 | 13.7 | +0.7 | 24.6 | +2.1 | 15.2 | 0.062 | 0.065 | 0.062 | 0.986 | 0.554 | 0.35 |
| b our tool, release pairs | 12.6 | 13.7 | +1.1 | 23.2 | +3.5 | 14.5 | 0.076 | 0.076 | 0.069 | 0.985 | 0.570 | 0.39 |
| b′ balanced unused partners | 7.6 | 8.5 | +0.9 | 13.7 | +3.5 | 7.0 | 0.069 | 0.050 | 0.045 | 0.993 | 0.593 | 0.42 |
| c′ balanced random, genuine pool | 7.7 | 8.8 | +1.1 | 16.2 | +1.6 | 8.0 | 0.066 | 0.049 | 0.052 | 0.993 | 0.575 | 0.47 |
| c balanced look-alike | 5.3 | 7.6 | +2.2 | 11.8 | +7.8 | 5.4 | 0.074 | 0.063 | 0.047 | 0.994 | 0.621 | 0.48 |
| d c + halves as genuine | 7.5 | 8.1 | +0.7 | 17.2 | +2.0 | 5.9 | 0.051 | 0.037 | 0.032 | 0.997 | 0.572 | 0.41 |

Smoke reading of the registered SMDD-T rules (descriptive at this size): (c) − (b) landmark-7 native EER −7.2
[−10.0, −4.9] points (the "partner claim dropped" condition does not hold); (d) − (c) +2.2 [+1.3, +3.0] points
(within the 5-point rule), halves flag rate 0.074 → 0.051 (not halved, so the halves arm "fails" the registered rule).

**Full run, frozen CLIP ViT-L/14 heads, 5 seeds (401 to 405), N = 14,734 morphs + 25,000 genuine per arm
(`p3_full.json`, per seed `p3_full_seeds.csv`).** Value = mean of the 5 seeds' metrics; [95%] = person bootstrap
(B = 2,000) of that mean. EER in %. Every rebuilt arm is "still separable by sharpness" (descriptive).

| Arm | landmark-7 EER native | landmark-7 E7 | landmark rise | diffusion-7 EER native | diffusion rise | GAN-3 EER | halves flagged, AR1 EER thr | halves flagged, R0-5% thr | R2w OpenCV flagged (EER thr) | AUC halves vs R0 | FRLL neutral above smiling |
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

Seed spread is small (e.g. landmark-7 native EER per seed, arm c: 3.25, 3.24, 3.24, 3.29, 3.23). The GAN-3 E7 rise is 0
for every arm because the E7 genuine copies of those cells equal the native photos (no shrink needed).

Steps between arms (difference of 5-seed means, paired person bootstrap; `p3_full.json` "steps"):

| Step | what changes | landmark-7 EER native | landmark rise | diffusion-7 EER native | diffusion rise | halves flagged (AR1 EER thr) | neutral above smiling |
|---|---|---|---|---|---|---|---|
| a → b | tool (SMDD's files → our engine) | +0.27 [−0.29, +0.89] | +0.57 | −0.54 | +3.25 [1.78, 4.86] | +0.010 | −0.06 |
| b → K = 50 | five partners → 50 | −2.82 [−4.18, −1.32] | +0.57 | −10.44 | +1.89 | −0.024 | +0.03 |
| b → K = 500 | five → 500 | −3.11 [−4.81, −1.63] | +0.14 | −11.36 | +0.11 | −0.036 | −0.08 |
| b → b′ | five → 2,433 | −3.42 [−5.19, −1.87] | +0.26 | −11.14 [−13.88, −8.11] | +2.47 | −0.031 | −0.10 |
| b′ → c′ | source pool + genuine identities become contributors | +0.18 [−0.36, +0.69] | −0.07 | +1.06 | +0.27 | −0.008 | +0.13 |
| c′ → c | random → look-alike pairs | −1.12 [−1.92, −0.38] | +0.38 | −2.89 | +4.11 [2.28, 6.26] | +0.018 | +0.11 |
| c → d | halves as genuine images | +4.19 [+2.95, +5.62] | −1.87 [−2.58, −1.24] | +7.21 | −14.22 [−17.32, −11.57] | −0.047 [−0.063, −0.032] | −0.18 |
| d → e | history crossing | +1.94 [+0.91, +2.91] | −0.99 [−1.39, −0.46] | −0.70 | −3.73 [−5.43, −1.99] | −0.003 | −0.06 |
| a → a256 | drop the 733 off-size files | +0.19 | +0.17 | +0.99 | −0.17 | +0.003 | 0.00 |


**JPEG reads (A10; FRLL genuine photos under JPEG, 204 each; miss = FRLL-Morphs landmark-4 pooled morphs at the same
threshold; 5-seed means).** "own" = the head's own rule (logit ≥ 0); "dev" = flags 5% of the AR1 camera photos.

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

**History-matched genuine pools (A11; E7 copies; flag rate of the pool and miss rate of that cell's morphs at the
same threshold; the three most-flagged pools per arm; 5-seed means).** Validity condition: arm (a) flags more than
10% of some pool (MorDIFF E7: 0.267 at its own rule, 0.770 at the camera-photo threshold), so the storage
comparison counts for the frozen heads.

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

Registered falsifiers (descriptive, because no rebuilt arm passed the Laplacian acceptance):
- SMDD-T partner part, EER condition: (c) − (b) = −4.36 [−6.27, −2.81] points; |diff| < 1 with interval including 0
  does **not** hold. (The second half of the condition, the releases' partner gap, is the Part 2 reading below.)
- SMDD-T halves part: (d) − (c) = +4.19 points (≤ 5: passes the EER rule); halves flag rate 0.072 → 0.026 (halved;
  (c) is above 5%, so the rule is informative): the halves arm **does not fail** the registered rule.
- Partner-count dose curve: **not flat** (K = 50 is already 2.8 points below K = 5 on the landmark cells, interval
  excludes 0).
- SMDD-X frozen-head analogue (not the registered ViT-B/16 LoRA test): diffusion-cell E7 rise 11.3 (a), 7.2 (d),
  3.5 (e); FRLL FaceMorpher / OpenCV E7 EER per arm in `p3_full.json`.
- Arm (f) vs (e) (JPEG copies added): landmark-7 native EER 8.45 vs 9.38; FRLL genuine jpeg50 flagged at the
  camera-photo threshold 0.200 vs 0.169 (no reduction); at the own rule 0.068 vs 0.067.

## Checks

- Landmark pass reproduces the stored if106 points on SMDD genuine renders: max 0.014 px over 4 renders (smoke;
  `lm_check_pool_limit8.json`).
- Feature path (`feat_check.json`, `feat_check_fp32.json`): the timm QuickGELU tower with the cached OpenAI weights is
  identical to the FE ViT-L/14 release tower (max weight difference 0.0). The FE release header on our features vs
  the existing A12REL FE ViT-L/14 scores on 8 FRLL frames: max |Δ probability| 0.0062 with TF32 (0.0046 in fp32);
  **the registered tolerance 1e-3 is missed**. All 8 values agree to about 0.03 logit and in rank. TF32 vs fp32 on the
  DGX alone differ by up to 0.002, so the residual is read as platform numerics (A12REL ran on a different machine and
  software stack), not a pipeline difference; not verified further. TF32 kept as registered.

- Shrink step for arm (e) (`shrink_verify.json`): `a47_data._one` (sha256 fcd48e1a…, prep_eval.py 374408ab…, call
  `prep_eval.degrade(img, "R", scale=0.3125)`, INTER_AREA 256 → 80, lossless PNG) reproduces the stored a47 copies of
  8 genuine renders byte for byte.
- Engine wrapper (DGX test of the WCSS task, `wcss/test_c/res`): wrapper morph = unchanged 78 command line, max
  difference 0 on 8 + 8 pairs; 0.5 hA + 0.5 hB vs morph at most 0.5 grey level (asserted <= 1 on every pair).

## Run log

- 16:41 WCSS CPU task `SM1_cpu_c` (arms c and c′, 30,000 morphs + 30,000 halves) staged; submitted by the lead as job
  6301971 (48 cores). It cannot succeed (pre-A5 lists, engine failures stop the build); WCSS unreachable since
  16:54. The author accepts SMDD's condition on derived morphs (lead, 17:00).
- 17:48 to 18:45 all builds on the rented CPU machine leaseB (96 workers, nice 19; 0 USD of our own).
- Athena jobs (account plgrestorearc-gpu-a100, A100 40 GB): 3544208 feature smoke (passed; about 0.05 GPU-h),
  3544789 LoRA smoke (passed; 148 s), 3545820 full feature pass (running from 19:09), 3545823_[0-19] LoRA fits
  (queued 19:09; estimate under 100 GPU-h).

## Not verified / caveats

- pending
