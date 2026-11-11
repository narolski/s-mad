# Own-crop re-score of the audit rows (RS1): result

Status: **in progress** (11 Nov 2026, 18:05 CET). Numbers below are filled in as the DGX run finishes; the full record
is `README.md`, the registration `prereg.md` (with amendments 1 and 2).

## What was done

Each released detector received the benchmark files through its own crop and preprocessing: MADation ViT-B/16,
ViT-L/14, FE ViT-L/14, FE ViT-B/16 and MixFaceNet-MAD through the corrected RGB MTCNN crop of the SMDD script
(A46 RGB-only path) and their own input adapters; SelfMAD through its own dlib crop (existing scores; new scores only
for FEI, FFHQ and the A43 stored files). Rows are labelled "reproduced" when the native EER is within max(1.5, 25%)
of the published value (MADation arXiv 2501.03800v3 Tables 1 to 3; SelfMAD arXiv 2504.05504 Table II), otherwise
"our pipeline, published number not reproduced", or "no published number".

## Tables

(pending)

## Deviations and what could not be verified

- Crops of images A46 had not cropped were made with the landmark ladder's (AR1) batched `crop_rgb.py` and stored as
  PNG; the original SMDD script re-saves a JPEG input as JPEG. None of the DGX-cropped inputs is a JPEG file.
- Scores of JPEG-stored crops (FRLL-Morphs) depend on the JPEG decoder: DGX (Pillow 12.2.0) vs the registered A46
  scores (WCSS) differ by up to 0.78 in probability for 1,070 of 7,061 morph crops (`rs1_platform_check.json`).
- MADation ViT-B/16 logits on DiM cells are packed so tightly that the DiM EERs move by up to 1.5 points between two
  GPUs at score differences below 6e-5.
- Published numbers come from the arXiv HTML versions; the CVF PDFs were not opened. The published genuine
  populations are not verified.
- Athena (amendment 1: corrected MAD22 cells, FS releases) has not run: Slurm account association missing. Job IDs and
  GPU-hours: none.
