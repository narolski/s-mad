# AF0: alpha-field probe on frozen features

Written by the lead on 11 Nov 2026 before any data for it existed.

- **Hypothesis (plain words):** if the training target is a mixing-fraction map that varies inside
  each image, a head on frozen patch features learns to see texture superposition and cannot use any
  cue that is constant over an image. Its mean prediction then separates real landmark morphs from
  processed genuine photos, and does not move when the genuine photos' history changes.
- **Data.** Persons from FRGC and colorFERET that are not hosts, partners or references in
  `experiments/AR1/pool.csv`; no FRLL person. Split by person: 80% train, 20% validation.
  Per pair (A, B), both warped to the mean shape with the existing Delaunay engine
  (`scripts/68_hires_morph.py` as used by `78_tool_morph.py`), then blended per pixel as
  (1 − a(x))·A + a(x)·B with a(x) from: zero everywhere; uniform 0.25; uniform 0.5; linear gradient in
  a random direction; one or two smooth bumps on random landmarks. a(x) is defined on landmark
  vertices and interpolated inside triangles, so it has no seams. Also unprocessed aligned photos
  (target zero). About 4,000 training images to start. Stored as PNG in the aligned 512 frame.
  Verification of the modified blend: with a(x) = 0.5 everywhere the output equals the unchanged
  engine's output (maximum absolute pixel difference at most 1).
- **Model and recipe.** Frozen DINOv3 ViT-L/16 at 512 (32 × 32 patches), frozen CLIP ViT-L/14 at 336
  and 224. Per-patch target = mean of a(x) over the patch. Heads: (i) ridge regression per patch,
  (ii) two-layer MLP per patch, Huber loss, seeds 401 to 405. Image score = mean prediction over
  patches inside the face hull. Baseline (iii): logistic regression on mean-pooled tokens with
  image-level labels (uniform 0.5 versus zero), same images.
- **Primary metrics and falsifiers (fixed now).**
  - F1, learnable: on validation persons, rank correlation between predicted and true a over patches,
    computed within each image and averaged, at least 0.4. Below 0.2 on every backbone: the frozen
    features do not carry local superposition evidence at this size; one retry at higher input size or
    with LoRA, then drop.
  - F2, transfer to real morphs: AR1 ladder, tool not used for the fields (FaceMorpher), R2 versus R4
    AUC at least 0.85 with lower bound above 0.75. Below 0.65: drop as a detector.
  - F3, history does not matter: mean score shift of genuine photos from R0 to R1 (existing E7 frames)
    and R0 to R2, in units of the R0 standard deviation, at most 0.3 for the dense head. Reported
    beside the same number for the image-level baseline and the released MADation ViT-L/14.
  - F4, shortcut stress test: train (i)/(ii) and (iii) on a confounded set (every mixed image built from
    FRGC pairs, every zero image from colorFERET), test on the crossed set (mixed from colorFERET,
    zero from FRGC). Prediction: baseline AUC falls by at least 0.20 relative to its unconfounded
    training; dense head falls by at most 0.05. If the dense head falls by more than 0.15 the central
    claim is false.
  - F5, benchmark (descriptive tonight): FRLL-Morphs landmark families and corrected MAD22 landmark
    cells, genuine class native and E7; EER beside the released MADation ViT-L/14.
- **Guards.** Person-disjoint splits; no FRLL person in any fit; 32-pixel thumbnail baseline on the
  same task; prediction maps for 20 validation images saved as figures.
- **Stop rule and budget.** One evening on the DGX: CPU build with at most 6 processes, under 1
  GPU-hour of feature extraction.
- **Pre-run review:** lead's own design; results reviewer after the run.
- **Result:** pending.
