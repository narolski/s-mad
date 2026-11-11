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

## Part 2: partner audit of released detectors

pending

## Part 3: rebuild arms on frozen features

pending

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
