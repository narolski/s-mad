# Own-crop re-score of the audit rows (RS1): pre-registration

Written 11 Nov 2026, 16:50 CET, before any score of this experiment exists. Owner: RS1 hypothesis owner.
Code `src/RS1/`, large outputs `/mnt/t7/smad_next/RS1/`.

Abbreviations. EER = equal error rate (%). AUC = area under the ROC curve (0.5 = chance). E7 (also called
"resmatch") = the existing control that gives a genuine photo the morphs' shrink-and-store history (registered rule:
scale = the family's median morph inter-eye distance / the photo's inter-eye distance). MTCNN = the face detector of
the MADation and MixFaceNet-MAD crop. FE = frozen-encoder MADation release (CLIP encoder frozen, head trained). LoRA =
the main MADation release (low-rank adapted encoder). "Stored-small photo" = A43 arm E, the FRLL photo cropped by
DiffAE's aligner and stored at the published MorDIFF size (about 145 px wide).

## What I knew before writing this page (disclosed; outcomes partly known)

- The A46 RGB-only descriptive table (`mambamorph-code/experiments/A46_diffusion-register-raw-files/RGB_ONLY_RESULTS_20261108.md`):
  native EERs on the same RGB MTCNN crops of the raw benchmark files for all seven MADation / MixFaceNet releases, and
  E7-vs-morph EER changes for MorDIFF, DiM-A and Greedy-DiM. From it, the reproduction labels of the native
  MADation and MixFaceNet cells below are predictable (so those labels are **post hoc**):
  ViT-B/16 AMSL 3.49 / FaceMorpher 0.86 / OpenCV 1.47 / StyleGAN 17.17 / WebMorph 1.88 / MorDIFF 0.99;
  ViT-L/14 8.87 / 0.90 / 1.96 / 38.72 / 4.42 / 28.81; FE ViT-B/16 MorDIFF 19.11; FE ViT-L/14 MorDIFF 22.03;
  MixFaceNet-MAD 17.15 / 2.98 / 4.42 / 10.79 / 14.15 / 8.91. Under the rule below this predicts "reproduced" for all
  except ViT-B/16 WebMorph (1.54 below the published value, outside 1.5), ViT-L/14 StyleGAN and ViT-L/14 MorDIFF.
  ViT-B/16 OpenCV sits at the edge (1.498 against a window of 1.5).
- Found while preparing this page (no score read): the A46 E7 pools (`e7area_*`, from `a41g/x7/a41g_x7/`) are the
  **SelfMAD dlib crops** of the raw E7 files (197 x 245 for a 428 x 428 raw E7 file), so A46's E7 numbers for MADation
  are a crop of a crop. RS1 crops the staged raw E7 files instead (`a41g/x7work/in/s*/e7area_<family>/`, hashes in
  `x7_inputs.csv`).
- AD1 result and its review (our-frame ladder numbers; SelfMAD own-crop-on-frames numbers), the C1b summary
  (expression split on our frames), and the SelfMAD raw-file FRLL figures quoted in the round-2 vetting text
  ("0.4 / 0.1 / 2.9 / 5.9 against 0.00 / 0.00 / 0.99 / 3.45"; Greedy-DiM 6.4 against 7.60). I have not opened the
  SelfMAD per-image files.
- No own-crop score exists for MADation or MixFaceNet on the A43 control images, the aligned E7 frames or the raw E7
  files (checked: A43 and A41 score MADation on our 512 frames only).

## Question (measurement, not a hypothesis test)

When each released detector receives the benchmark files through its own crop and preprocessing, which rows
reproduce the published EER, and for those rows: how much do the history-matched genuine photos, storage at the
published size, and the neutral / smiling split of the genuine class move the numbers; and where does each release
place the MorDIFF control images.

## Published reference values (EER %, fixed now)

| Detector | Cell | Published | Source | Check |
|---|---|---|---|---|
| MADation ViT-B/16 (LoRA) | MorDIFF | 1.10 | MADation (Caldeira et al., WACVW 2025), Table 1 and Table 2 | checked: arXiv 2501.03800v3 HTML, tables parsed from the page this session; CVF PDF not opened |
| MADation ViT-B/16 | FRLL AMSL / FaceMorpher / OpenCV / StyleGAN2 / WebMorph | 3.85 / 1.35 / 2.97 / 17.21 / 3.42 | MADation Table 3 | checked (same) |
| MADation ViT-L/14 (LoRA) | MorDIFF | 19.26 | MADation Table 1. Table 2 prints 20.40 in its MorDIFF row, with the OpenCV, WebMorph and MorDIFF labels permuted relative to Table 1; Table 1 is the reference, the label under 20.40 is printed beside | checked (same) |
| MADation ViT-L/14 | FRLL AMSL / FaceMorpher / OpenCV / StyleGAN2 / WebMorph | 7.26 / 0.74 / 0.99 / 24.96 / 4.07 | MADation Table 3 | checked (same) |
| MADation FE ViT-B/16 | MorDIFF | 17.86 | MADation Table 1 (FE row) | checked (same) |
| MADation FE ViT-L/14 | MorDIFF | 22.85 | MADation Table 1 (FE row) | checked (same) |
| MADation FE ViT-B/16, FE ViT-L/14 | FRLL families, DiM | none | not reported in MADation | checked (same) |
| MixFaceNet-MAD | MorDIFF | 8.50 | as quoted in MADation Table 2 (citing the SMDD and MorDIFF papers) | checked as quoted in MADation; the SMDD and MorDIFF papers were not opened |
| MixFaceNet-MAD | FRLL AMSL / FaceMorpher / OpenCV / StyleGAN2 / WebMorph | 15.18 / 3.87 / 4.39 / 8.99 / 12.35 | as quoted in MADation Table 3 (citing SMDD) | checked as quoted; SMDD paper not opened |
| SelfMAD (HRNet-W18 release) | FRLL AMSL / FaceMorpher / OpenCV / StyleGAN2 / WebMorph | 0.99 / 0.00 / 0.00 / 10.34 / 3.45 | SelfMAD (Ivanovska et al., FG 2025), Table II | checked: arXiv 2504.05504 HTML, parsed this session |
| SelfMAD | Greedy-DiM | 7.60 | SelfMAD Table II | checked (same) |
| SelfMAD | MorDIFF, other DiM families | none | not reported | checked (same) |
| any | DiM families other than Greedy-DiM | none | — | — |

"StyleGAN" in our folder names is FRLL-Morphs StyleGAN2. The published genuine populations (for example which FRLL
photos form the bona fide class) are not verified; we use the 204 FRLL front photos.

## Reproduction rule (fixed)

Window W = max(1.5, 0.25 x published). A row is **reproduced** if |native EER − published| <= W, on the point
estimate of the full cell (204 raw genuine photos against all raw morphs of the cell), EER as `analyze.eer`
(float64, no rounding). Otherwise: **"our pipeline, published number not reproduced"**. A cell without a published
value: **"no published number"**. Only reproduced rows carry audit claims; all others are printed with their label.
The label is the only verdict word used.

## Detectors and preprocessing

- MADation ViT-B/16 (sha ddb1455b), ViT-L/14 (bb452ded), FE ViT-L/14 (74dd7fbc), FE ViT-B/16 (6a4d93ba);
  MixFaceNet-MAD (3d507c8b; its own MTCNN-crop path runs unchanged locally in the landmark ladder (AR1)). Path: the
  A46 RGB-only acquisition (RGB MTCNN, box[0], SMDD-script 5% margin with clamping, `a46_corrective_crop.py` of the
  frozen A46 runtime) then the `a12_released` adapters (BGR, (x − 0.5) / 0.5, 224), flip TTA computed but the
  decision key is `score_noTTA` (as A46). Ranks and thresholds use `logit_noTTA` (strictly monotone in
  `score_noTTA`; avoids float32 saturation ties).
- Crops: the registered A46 RGB crops are reused for the raw files they cover (FRLL photos, five FRLL-Morphs
  families, MorDIFF, six DiM families; hashes checked against their SHA256SUMS). New crops with the landmark ladder's
  (AR1) `crop_rgb.py`, copied byte-identically into `src/RS1/` (batched MTCNN, AR1's disclosed deviation) for: raw
  E7 files, aligned frames, A43 stored images. Check: 32 raw files already covered by A46 are re-cropped with
  `crop_rgb.py`; box differences are printed.
- Scoring: the landmark ladder's (AR1) `score.py`, copied byte-identically; a wrapper adds the two FE weight files to
  its weight table (nothing else changes). Platform check: the A46 crops of the FRLL photos, MorDIFF and OpenCV are
  rescored and compared with the registered A46 RGB-only per-image files (`score_noTTA`, max |difference| printed).
- SelfMAD release (0ad8db6f), own preprocessing (dlib 81 landmarks, landmark box + margin, 384, softmax[:, 1]):
  **existing scores only, no rescoring**: A41 x7 (raw files: FRLL photos, five FRLL families, MorDIFF, DiM-A,
  Greedy-DiM, raw E7 for MorDIFF / DiM-A / Greedy-DiM; `logit_noTTA`), the resolution-shortcut file A32-RSX
  (`selfmad_own_eval.npz`: our aligned frames, native and E7, all families; probability only), A43 own (control
  images as our aligned frames). Probabilities from logits are sigmoid(logit) in float64; ties at the threshold are
  counted and printed for the probability-only file.

## Image sets and cells

Genuine class G = 204 raw FRLL front photos (102 persons; neutral `_03`, smiling `_08`).

- (a) FRLL-Morphs AMSL (2,175), FaceMorpher (1,222), OpenCV (1,221), WebMorph (1,221), StyleGAN2 (1,222), raw files.
  History-matched genuine: **no raw E7 file exists** for these families, so the row uses our aligned E7 frames
  (`eval/frllm/frll_bona/*_resmatch_<family>.png`) through the release's crop, labelled "aligned-frame E7".
  Reference row: our aligned native frames (`*_orig.png`) through the same crop ("aligned native").
- (b) MorDIFF (1,000 raw). History-matched: raw E7 files (A41 `e7area_mordiff`, 204). Cross-check of the
  aligned-frame substitute: aligned native and aligned E7 frames of `mordiff_bona`.
- (c) A43 control images as stored: A = 200 sampled published MorDIFF morphs; B / B20 = our same-pair morphs at 100 /
  20 decoding steps (200 each); C / C20 = same-person mixes, neutral + smiling of one person (102 each); D / D20 =
  one-photo reconstructions (204 each); E = stored-small photo (204).
- (d) DiM families (dim_a, dim_c, fast_dim, fast_dim_ode, greedy_dim, greedy_dim_s), raw. Raw E7 for DiM-A and
  Greedy-DiM; aligned-frame E7 for the other four (labelled).

Faces not found by a crop are excluded and counted per set; a set with more than 5% missing is flagged.

## Quantities, per detector and cell

1. Native EER [95% interval], published value, |difference|, window W, reproduction label.
2. History: EER with the history-matched genuine class (raw E7, or aligned-frame E7 labelled), the aligned-native
   EER, and the history effect: raw cells E7 − native; aligned cells aligned E7 − aligned native (also printed:
   aligned E7 − raw native). Paired intervals.
3. Flag rates at two thresholds set on the native raw genuine photos of that detector and cell, recomputed in every
   bootstrap replicate: t5 = the lowest native genuine score with at most 5% of the (weighted) native genuine photos
   strictly above it, flagged = score > t5; t_eer = the threshold `analyze.eer` selects on native genuine vs the
   cell's morphs, flagged = score >= t_eer. Rates printed for native, history-matched, aligned-native and
   stored-small genuine photos.
4. Genuine class split: native EER and history-matched EER with neutral-only (102) and smiling-only (102) genuine
   photos, morphs unchanged; history-matched flag rate at t5 per split.
5. MorDIFF ladder (A43 images through each release's crop), AUC with the higher rung positive: stored-small photo E vs
   raw photo; reconstruction vs stored-small photo (D20 vs E, D vs E); our morph vs reconstruction (B20 vs D20, B vs
   D); published vs our morph (A vs B20, A vs B). Descriptive: C20 vs D20, B20 vs C20, A vs E, A vs raw photo, and
   the flag rates of A, B20, B, C20, D20, D, E at the MorDIFF t5 and t_eer.

Bootstrap: two-way pigeonhole person bootstrap (`a41_read.Draw`, Owen 2007) over the 102 FRLL persons, B = 2,000,
seed 20261111, one draw shared by every detector and cell (paired). Genuine photo weight = its person's count; morph
= product of its two contributors' counts; one-person image (C, D, E) = the person's count. 95% percentile intervals.
AUC = `a36_read.wauc`, EER = `analyze.eer_weighted`.

No verdict words; numbers and the reproduction label only.

## Guards and known limits

- The aligned-frame E7 rows mix our alignment with the history; the aligned-native row shows the alignment part.
- Stored-small photo E went through DiffAE's aligner crop as well as storage; it is not storage alone.
- No image operation other than the release crop step (crop and lossless PNG storage of the crop, as AR1).
- SelfMAD rows from frames (A32-RSX, A43) are labelled "our aligned frames through SelfMAD's crop".

## Budget, stop rule, commands

DGX only, GPU shared: under 12 GB, one GPU process at a time, at most 4 CPU processes at `nice -n 10`. About one
GPU-hour. Every command is first run on 8 images. Commands: `src/RS1/manifest.py` -> `crop_rgb.py` (sharded) ->
`rs1_score.py` per detector -> `platform_check.py` -> `analyse.py`. Pre-run review: not run (lead to decide).

## Amendment 1 (11 Nov 2026, 17:30 CET; before any corrected-MAD22 score and before any RS1 score of a MADation or MixFaceNet release has been read)

Trigger: the lead's message of 17:20 (Athena available; widen the re-score) and the slow, out-of-memory-prone shared
DGX (two crop processes and one scoring process failed at CUDA start; crops run at about 0.4 images/s per process).
What I had read by then: no RS1 score of any MADation / MixFaceNet release. I had run the analysis code once on the
existing SelfMAD files (A41 x7, A32-RSX, A43 own) to test it (17:00); its raw-file EERs equal the A41 x7 table
exactly. I had also read the A46 RGB-only MAD22 numbers on the **old** 185 / 4,069 subset (all seven releases).

1. **Platform.** A second, complete run on Athena (A100, x86; shared environment torch 2.2.1 / CUDA 12.1, timm
   1.0.27, numpy 1.26.4, pillow 10.2.0; facenet-pytorch 2.6.0 from the same wheel as the DGX and
   opencv-python-headless 4.11.0.86 installed into `envs/RS1` inside a job). Same code (the frozen A46 runtime files
   and the byte-identical AR1 `crop_rgb.py` / `score.py`, run through a wrapper that only re-points paths), same
   images, A46 crops reused, all other crops redone there. Smoke job (8 images per stage) first, then one
   production job, at most 10 GPU-hours in total.
2. **Primary source.** Pre-registered cells: the DGX run, as registered, if it completes; otherwise the Athena run,
   and the row says so. The Athena run of the same cells is printed as a platform check (max |score_noTTA
   difference| per release; EER differences per cell). New cells (below): Athena.
3. **New cells.** (a) **Corrected MAD22** (the author's re-upload, 204 bona fide FRLL photos, FaceMorpher 1,000,
   MIPGAN-I 1,000, MIPGAN-II 999, OpenCV 984, Webmorph 500; raw files from
   `mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted/`, hash-checked against
   `verified_inventory.json`): native = raw bona fide vs raw morphs through each release's own crop. History-matched:
   **no raw E7 file exists**, so the existing canonical v3 E7 frames (`mad22_canonical_E7_inputs_v3_20261109T113746Z/e7/<family>/`,
   hash-checked against `PROCESSED_SHA256SUMS`) through the release crop, labelled "aligned-frame E7", with the
   aligned native bona fide frames (`native/BonaFide/`) as reference. Flag rates, neutral / smiling split and person
   bootstrap as for the other cells (the same 102 persons and the same draw). (b) **All released MADation variants**:
   add FS ViT-B/16 (a7cacd47) and FS ViT-L/14 (6071ec7b) on every cell.
4. **Published values added** (MADation, arXiv 2501.03800v3, Table 1 for the six MADation releases, Table 2 for
   MixFaceNet-MAD; parsed from the HTML this session, "checked"; CVF PDF not opened). MAD22 FaceMorpher / MIPGAN-I /
   MIPGAN-II / OpenCV / Webmorph: LoRA ViT-B/16 0.00 / 33.37 / 22.21 / 3.85 / 10.80; LoRA ViT-L/14 0.40 / 20.32 /
   9.06 / 2.23 / 20.40 (Table 2 permutes the ViT-L/14 OpenCV, WebMorph and MorDIFF labels; Table 1 is the
   reference); FE ViT-B/16 2.89 / 26.00 / 34.26 / 14.88 / 32.80; FE ViT-L/14 9.77 / 23.51 / 21.81 / 15.89 / 26.40;
   FS ViT-B/16 5.38 / 32.87 / 27.19 / 16.30 / 22.80; FS ViT-L/14 22.63 / 23.80 / 21.81 / 30.47 / 33.60;
   MixFaceNet-MAD 4.60 / 16.70 / 20.62 / 8.33 / 18.20. MorDIFF: FS ViT-B/16 28.14, FS ViT-L/14 40.92. FRLL: none for
   FE / FS. The reproduction rule is unchanged (W = max(1.5, 0.25 x published), point estimate).
   Caveat printed with every MAD22 row: the published numbers were computed on the SYN-MAD 2022 release as the
   authors held it; equivalence with the corrected copy (which retains five duplicate Webmorph groups and an
   inherited OpenCV bona-copy defect) is not verified.
5. **Not added:** SelfMAD on corrected MAD22 (no published MAD22 value, so no row could be reproduced; the brief
   says reuse, not rescore, SelfMAD scores).

## Amendment 2 (11 Nov 2026, 17:45 CET; from the independent review of the fixed-threshold re-read (EV1), `experiments/reviews/REVIEW_EV1_20261111.md`; before any full RS1 result is read)

State when written: one RS1 score file exists (MADation ViT-B/16 on the reused A46 crops); it has not been opened.
Athena: the lead reports that Slurm rejects our user's grant accounts; nothing is submitted until the lead says so
(the account to use is `plgrestorearc-gpu-a100`). The work runs on the DGX meanwhile.

The review withdrew the released ViT-L/14 false-alarm figures (saturated scores on our 512-pixel frames); RS1 now
carries them.

(a) **Extra genuine pools**, each through every MADation / MixFaceNet release's own crop and through SelfMAD's own
crop, existing files only (the files behind the EV1 rows; no new blur, resize, resampling or JPEG code):
- unprocessed FRLL photos (raw files; already in RS1);
- the existing JPEG quality 50 and 70 files and the existing 50% shrink-and-enlarge files of the FRLL photos
  (`eval/frllm/frll_bona/*_{jpeg50,jpeg70,resample50}.png`, our aligned frames, 204 each);
- the DiM and MorDIFF storage-history files (raw E7 files where they exist, aligned E7 frames otherwise; already in
  RS1);
- the stored-small pool (A43 arm E; already in RS1);
- the 2,000 FFHQ photos (`/mnt/t7/smad_heldout/ffhq_morphs/eval/ffhqm/ffhq_bona/*_orig.png`) paired with their
  history-matched versions at the 65-pixel inter-eye distance (`*_resmatch_diffae.png`, `*_resmatch_landmark_complete.png`;
  the StyleGAN-matched copies, inter-eye distance about 266, are left out);
- FEI neutral (198) and smiling (187) photos (`gtest/{neutral,smiling}/bona/*.png`, the gtest.csv frames).
SelfMAD scores that already exist are reused (A41 x7 raw files, A32-RSX frames incl. JPEG 50 / 70 and 50%
shrink-and-enlarge, A43 own frames); SelfMAD is newly scored (AR1's `score.py --mode own`, the release file
0ad8db6f fetched by the landmark ladder (AR1)) only where no score exists: the FFHQ pools, FEI, and the A43 stored
files themselves.
(b) **Rates at two kinds of threshold.** Every flag rate is printed (i) at the release's own decision rule
(probability of morph > 0.5; MADation / MixFaceNet `score_noTTA` > 0.5, SelfMAD softmax[:, 1] > 0.5), which needs no
threshold pool, and (ii) at named threshold pools, with the pool printed as a column: t5 and t_eer on the native
raw FRLL photos of the cell (as registered), and t5 on each of the other unprocessed pools (FFHQ orig, FEI all).
**Paired shifts in logits** (history-matched or processed copy minus its own unprocessed photo, per photo) with a
person bootstrap interval (FRLL, FEI: person; FFHQ: image, no identity labels), the median shift and the share of
photos whose logit rises.
(c) **SelfMAD genuine class, both definitions**: neutral-only genuine photos (which match its published FRLL
numbers per the EV1 review) and all photos; the reproduction label is printed for both, and audit claims for a
SelfMAD row need the label "reproduced" under the definition used.
(d) **Border check.** For each release's own crop, the fraction of black pixels (all three channels exactly 0) in
the crops of genuine images and of morph images, per cell (MTCNN crops: from the saved crop files; SelfMAD: from its
saved raw-file crops in `a41g_x7/`; SelfMAD crops of our frames are not saved and are not checked). Printed beside
each cell, with a sentence on whether the release's crop removes the border our aligner leaves.
(e) Acceptance rule unchanged: a row counts only where the published number is reproduced within 1.5 points or 25%.
For the new pools (no morph class of their own) the flag rates carry the label of the cell whose threshold they use;
at the 0.5 rule they carry the label of the detector's FRLL / MorDIFF cells, printed beside.

## Amendment 3 (11 Nov 2026, 19:15 CET; before any full RS1 result of a MADation or MixFaceNet release is read)

Trigger: the lead's rule of 18:25 (all rows that are compared with each other come from one platform) and two facts
found by the platform checks (no efficacy number read): (i) MTCNN boxes differ between the GB10 and the A100 (Athena
smoke job 3544220: 21 of 200 images by more than 1 px, at most 15.9 px; median 0.03 px), so crops made on different
machines are not interchangeable; (ii) the release crop step stores a JPEG input as JPEG (SMDD
`image_preprocess.py` line 43, `cv2.imwrite` with the input's name; A46 did the same), while AR1's `crop_rgb.py`
always stores PNG.

1. **Primary pipeline: everything on Athena, crop and score.** The raw files that A46 had cropped on the GB10 (FRLL
   photos, five FRLL-Morphs families, MorDIFF, six DiM families; 11,264 files) are shipped raw and re-cropped on
   Athena, so every MADation / MixFaceNet-MAD row is cropped and scored on one machine type.
2. **Crop storage as the release does it:** `src/RS1/crop_rgb_ext.py` = AR1 `crop_rgb.py` with one change, the crop
   is written in the source's format (JPEG input -> JPEG crop at OpenCV's default quality 95; PNG -> PNG).
3. **Checks, not primary:** the reused A46 crops (GB10) are also scored on Athena and printed as a crop-platform check
   (native EER per cell, both crop sets); the DGX scores of the A46 crops (MADation ViT-B/16, ViT-L/14) and the
   registered A46 scores (WCSS) are printed as scoring-platform checks. The Athena smoke equivalence (same A46 crops,
   Athena vs DGX): max |logit difference| 0.20 (ViT-B/16) and 0.07 (ViT-L/14); vs the registered WCSS scores up to
   1.6 and 3.0 on JPEG-stored crops.
4. **SelfMAD:** two separate runs, each on one platform: the existing files (WCSS: A41 x7 raw files, A32-RSX and A43
   frames) and the RS1 DGX run (raw FRLL photos, raw MorDIFF, raw E7 MorDIFF, A43 stored files, FEI, FFHQ). Rows are
   never compared across the two runs.
Everything else (rule, cells, pools, statistics) is unchanged.

## Amendment 4 (11 Nov 2026, 19:35 CET; lead's decision on crop storage; before any full RS1 result of a MADation or MixFaceNet release is read)

Replaces item 2 of amendment 3 and the use of the reused A46 crops. No table of this experiment is built from crops
that were re-encoded as JPEG by code written in this sprint (AR1 / RS1 `crop_rgb_ext.py`) or by the A46 acquisition.

1. **Primary "own preprocessing" rows (variant 1):** the authors' crop script, SMDD `image_preprocess.py` (sha256
   bcaecd2970cd8d95e37b005f793035f2d0222219bf99215edc1168519fe5ee2c, `/mnt/t7/thirdparty/smdd_9683229_20261107/`),
   run **unchanged** on Athena on every input image, including its two properties: BGR pixels passed to MTCNN (line
   24) and the unbounded slice of line 40 (a negative start index wraps or gives an empty crop), and its storage
   (line 43, `cv2.imwrite` under the input's name: a JPEG input gives a JPEG crop). Images for which the script writes
   no crop (no face, or an empty / failed write) are counted and listed per set; rows are reported with them excluded,
   and the count per cell is printed beside each row.
2. **Secondary rows (variant 2):** the corrected crop (RGB pixels to MTCNN, all four edges clamped; the A46
   corrective functions through AR1's `crop_rgb.py`, unchanged) stored losslessly as PNG.
3. Not result rows: the corrected crop with JPEG re-encode (`crop_rgb_ext.py`) and the reused A46 crops. The
   300-image JPEG-vs-PNG measurement (`jpeg_check.py`, `rs1_jpeg_storage_check.json`) is kept as a recorded effect
   size. The DGX ViT-B/16 and ViT-L/14 scores of the A46 crops stay as a scoring-platform check only.
4. Both variants are cropped and scored on Athena with all seven releases (one platform). The reproduction label and
   every audit number are given for variant 1; variant 2 is printed beside it. Crop files of both variants are kept
   (tar in the result) with a sha256 list, for the retrains experiment (AD5).

## Amendment 5 (11 Nov 2026, 21:45 CET; before any full RS1 result of a MADation or MixFaceNet release is read)

Athena forecasts the two production jobs for 13 Nov; with the author's approval the lead rents one GPU machine
(plain Docker, image pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime, one 48 GB card). **Every MADation and MixFaceNet-MAD
row of the experiment comes from this one machine** (both crop variants of amendment 4 and all scoring). Same code and
packs (hash-checked on the machine); packages pinned as on Athena (timm 1.0.27, numpy 1.26.4, pillow 10.2.0,
opencv-python-headless 4.11.0.86, tqdm 4.67.1, facenet-pytorch 2.6.0 from the pack's wheel; torch 2.2.1 from the
image), versions logged. Scripts: `src/RS1/rented/rs1_run.sh` (the Athena job body), `drive.sh` (upload, setup, smoke,
production, copy-back with sha256), `compare_smoke.py`. Gate before production: an 8-images-per-set run of both
variants on the machine compared with Athena smoke job 3545869 on the same inputs; pass = the same images dropped by
the unchanged script and every release's largest |logit difference| below 0.5 (the largest value is reported). After
the gate passes, Athena jobs 3545972 and 3545973 are cancelled. Crops stay on the machine; the small result tars come
back to `/mnt/t7/smad_next/RS1/results_rented/`.

## Amendment 6 (11 Nov 2026, 23:55 CET; lead's decision; before any production row)

The 8-image gate of amendment 5 failed on the replacement machine rs1b (RTX 3090): largest |logit difference| 10.84
against Athena smoke 3545869. Breakdown: same image dropped by the unchanged script on both machines; 47 (v1) and 85
(v2) of about 464 crops differ in their detector box; on byte-identical crops the JPEG files scored differently
because the image's conda Pillow links another libjpeg (fixed: PyPI Pillow 10.2.0 wheel force-installed); on
identical PNG crops ViT-B/16 differs by up to 0.19 logit on 13 images (GPU arithmetic). Decision: the comparison with
Athena is **descriptive** (reported as a finding on cross-machine differences of the crop and scoring steps); every
MADation / MixFaceNet-MAD row comes from the one rented machine and no row is compared across machines. The gate is
rerun after the Pillow fix and recorded; production proceeds (`RS1_GATE=descriptive`).
Added (lead, 23:55): the post-fix comparison (identical JPEG crops still differing, libjpeg versions on both sides,
residual on identical PNG crops) is reported as a finding (a released detector's score depends on the JPEG decoder
build, by up to several logits per image). If after the fix identical crops still differ by more than 0.5 logit on
more than 1% of images for any release, the lead is told before any production row is read. Driver run:
`/mnt/t7/smad_next/RS1/rented_drive_b2.log` (lead's flag `RS1_GATE_DESCRIPTIVE=1`).
Correction (23:58): the production driver run is `/mnt/t7/smad_next/RS1/rented_drive_c.log` (`RS1_GATE=descriptive`); the b2 run was stopped by the lead.
