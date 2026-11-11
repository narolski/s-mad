# Own-crop re-score of the audit rows (RS1): result

Status: **partly finished** (11 Nov 2026, 20:25 CET). SelfMAD rows: done. MADation / MixFaceNet-MAD rows: Athena jobs
3545970 (variant 1) and 3545971 (variant 2) queued. Full record: `README.md`; registration: `prereg.md` (amendments
1 to 4). All numbers: EER in %, AUC 0 to 1, rates in %, 95% intervals from the two-way person bootstrap (102 FRLL
persons, B = 2,000; FEI subjects and FFHQ images have their own draws).

## Labels

A row is "reproduced" when its native EER is within max(1.5, 25%) of the published value (MADation arXiv 2501.03800v3
Tables 1 to 3; SelfMAD arXiv 2504.05504 Table II); otherwise "our pipeline, published number not reproduced"; "no
published number" where the paper has none. Only reproduced rows carry audit claims.

## SelfMAD release (HRNet-W18), its own dlib crop

Two runs, never compared with each other: (A) existing scores on WCSS (A41 x7 raw files; A32-RSX and A43 frames);
(B) RS1 scores on the DGX of raw, stored and dataset files (raw FRLL photos, raw MorDIFF, raw E7 MorDIFF, the A43
stored control images, FEI, FFHQ). Run B gives the same MorDIFF EER as run A (1.49; raw E7 45.20).

| Cell (run A) | Native EER [95%] | Published | Label (all photos) | Neutral-only EER | Label (neutral-only) |
|---|---|---|---|---|---|
| FRLL AMSL | 2.44 [0.94, 4.86] | 0.99 | reproduced | 0.97 | reproduced |
| FRLL FaceMorpher | 0.98 [0.07, 1.68] | 0.00 | reproduced | 0.21 | reproduced |
| FRLL OpenCV | 0.37 [0.00, 0.56] | 0.00 | reproduced | 0.08 | reproduced |
| FRLL WebMorph | 7.36 [4.93, 10.78] | 3.45 | not reproduced | 4.91 | reproduced |
| FRLL StyleGAN2 | 16.60 [12.26, 22.07] | 10.34 | not reproduced | 12.59 | reproduced |
| Greedy-DiM | 6.39 [3.26, 9.56] | 7.60 | reproduced | 3.07 | not reproduced |
| MorDIFF | 1.49 [0.00, 3.46] | none | no published number | 0.99 | no published number |
| DiM-A | 4.41 [1.86, 6.75] | none | no published number | 2.77 | no published number |

History-matched genuine photos (run A): raw E7 files raise the EER from 6.39 to 87.23 on Greedy-DiM (+80.8 [76.0,
85.5], reproduced row), from 1.49 to 45.20 on MorDIFF, from 4.41 to 69.50 on DiM-A. On the FRLL landmark cells only our
aligned E7 frames exist (labelled "aligned-frame E7"): aligned native -> aligned E7 AMSL 4.91 -> 49.02 (+44.1 [38.3,
48.9]), FaceMorpher 1.51 -> 8.34 (+6.8), OpenCV 0.49 -> 6.30 (+5.8), WebMorph 15.79 -> 71.00 (+55.2); for StyleGAN2
the E7 rule leaves the photo unchanged.

Release rule (probability of morph > 0.5), run B: raw FRLL photos 0.0% flagged, raw E7 MorDIFF photos 26.0 [18.1,
33.8], stored-small photos 56.9 [49.0, 65.2], MorDIFF morphs 26.5 [19.3, 34.8]; FEI frames 33.3 (neutral) and 40.1
(smiling); FFHQ photos 17.7 -> 48.1 with the DiffAE-matched history. Paired logit shifts (run B): raw E7 vs its photo
+5.06 [4.84, 5.27] (100% of photos rise), stored-small vs photo +6.04 [5.77, 6.30] (100%), FFHQ history copies +2.37
[2.26, 2.48] (89.5%).

MorDIFF ladder, run B (AUC, higher rung positive): stored-small photo vs photo 0.999 [0.998, 1.000]; reconstruction
D20 vs stored-small 0.465 [0.429, 0.499]; our morph B20 vs reconstruction D20 0.334 [0.260, 0.407]; published vs our
morph B20 0.463 [0.424, 0.493]. The MorDIFF row has no published number for SelfMAD.

## MADation and MixFaceNet-MAD releases

(pending: Athena jobs 3545970 and 3545971)

## Deviations and what could not be verified

- MADation / MixFaceNet primary rows use the SMDD crop script unchanged (amendment 4); variant 2 is the corrected
  crop stored as PNG. The reused A46 crops and the JPEG-re-encoding corrected crop are not result rows.
- Effect of the crop step's JPEG re-save, measured on 300 JPEG files (identical crop regions, JPEG q95 vs PNG):
  median |logit difference| 0.003 to 0.86 by release, up to 16 logits on single images, 1 to 7 images of 300 cross
  the 0.5 rule (`rs1_jpeg_storage_check.json`).
- Scoring platform matters at the level of single EER points: the same A46 crop files scored on the DGX and on WCSS
  give native EERs that differ by up to 1.5 points on PNG cells (near-tied saturated logits) and up to 0.4 points on
  JPEG cells (decoder). Athena vs DGX on identical files: max 0.20 logit.
- SelfMAD's FRLL numbers are reproduced only with neutral-only genuine photos for WebMorph and StyleGAN2, and only
  with all photos for Greedy-DiM.
- Published numbers come from the arXiv HTML versions; the CVF PDFs were not opened; the published genuine
  populations are not verified.
- Athena job IDs and GPU-hours (sacct elapsed, 1 GPU each): smoke 3544220 0:06:52 (0.11 h), cancelled smoke 3545836 0:02:37 (0.04 h), smoke 3545869 0:03:34 (0.06 h); cancelled production 3545884 never started (0 h);
  production 3545918 / 3545919 cancelled before start (0 h), resubmitted as 3545970 / 3545971 (pending).
