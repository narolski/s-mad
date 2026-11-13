# Layer misregistration echo (ME1): registration DRAFT (pre-run check requested from the lead; not in force)

Owner: PR1/BD1/RI1/TB1 owner agent (Opus), on the lead's assignment of 13 Nov 2026. Source: mechanism ledger v2,
entry M13 (`experiments/IDEAS_mechanism-ledger/LEDGER.md`, 3e893a6). Development data only. Zero GPU (DGX CPU, nice 19,
at most 2 processes while the RI1 embeddings run). Nothing enters the frozen method.

**Lead's ruling (NOTEBOOK).** Phase correlation between images in memory, and echo or autocorrelation statistics, are
measurements. Nothing shifted or filtered is stored.

Computed before this draft:
- a 6-host code test of `me1_measure.py` (`me1_feats_limit6.csv`, not looked at);
- a mock run of the reader with every real quantity randomised (synthetic feature file; E, W, D, the shortcut
  features and the logits replaced by random numbers in memory before any statistic).

No ME1 value of the 291 hosts exists.

**Stated before any read:** a pass means "two shapes were superimposed", not "two people", until look-alike pairs
(LA1) exist. On this ladder FR similarity of two people and of two sessions of one person do not overlap.

## 1. Hypothesis

**H-ME1.** A piecewise-affine landmark warp brings the two layers into register only at the landmarks. A blend of two
photos therefore contains person-specific sub-landmark structure twice, offset by the residual warp field (an "echo"
at a few pixels). A warp-only image, a genuine photo and a one-photo render have one layer. The residual grows with the
shape difference between the two sources.

## 2. Rows and measures (`src/ME1/me1_measure.py`)

- **Rows.** The 291 BD1 hosts (FRGC 235, colorFERET 56), FS1 evaluation frames, OpenCV-style:
  - S4, S3, S0, R2w4, R2w, R4, R3 on the amendment-7b hull (mean(H, B));
  - R0 and R0_61 on H's own hull.
  All frames are PNG.
- **Oracle (needs the counterpart; not a detector).** The warped halves come from existing images by arithmetic, since
  a 50% OpenCV morph is the mean of its two warped halves:
  - two-person: H_w = R2w4, B_w = 2 S4 − R2w4;
  - same-person: H_w = R2w, S_w = 2 S3 − R2w (uint8 rounding gives errors of about one grey level).

  Phase correlation (cv2.phaseCorrelate, Hann window) runs in 24 × 24 windows on a 12 px grid, using windows fully
  inside the hull eroded by 12 px. Statistic: the median shift magnitude in px. The median peak response is printed.
- **Single image.**
  - Windows of 24 × 24 px (12 px grid) of the Sobel gradient magnitude, mean removed and Hann-windowed.
  - Autocorrelation by FFT. Echo = max over lags with 2 ≤ max(|dx|, |dy|) ≤ 8, excluding lags whose dx or dy is a
    non-zero multiple of 8 (the JPEG block period), of AC(lag) / AC(0).
  - Statistic: the median echo over hull windows (hull eroded by 4 px), divided by the median over windows fully inside
    an outer ring of at least the hull's area. The hull median alone is printed.
  - The ledger's restriction to eye and mouth windows is not applied; all hull windows are used (stated).

## 3. Covariates, folds, intervals (lessons of tonight's reviews)

- **Per-class stratifiers**, checked in code to vary per class:
  - W, the landmark displacement between the two source photos (H–B and H–S);
  - E, the band energy of the half-difference (TB1 `tb1_feats.csv` P4_Etot / P3_Etot);
  - D, BD1's D of the S4 and S3 rows.
- **Folds and bootstraps** by connected components of the person graph (110 components); 2,000 draws; failed draws
  counted, and more than 1% failed makes the verdict inconclusive.
- **Per-database prints** (FRGC, colorFERET) for every read.

## 4. Oracle read and rule

- AUC (two-person > same-person) of log median shift: overall, within W, within E, within D, per database. Component
  95% percentile interval.
- **Kill** (ledger): AUC ≤ 0.65 overall, or ≤ 0.55 within W quintiles.
- **Premise holds:** AUC ≥ 0.75 overall and ≥ 0.60 within W on FRGC.
- Otherwise "inconclusive".
- **Binding for any claim that the oracle adds beyond energy and geometry:** the cross-fitted gain of log shift over
  [log E, log W] (component folds). "No" if < +0.02; "yes" if ≥ +0.03 with a component lower bound > 0; otherwise
  "inconclusive".

## 5. Single-image read and rule

- **Primary:** S4 vs S3 within D quintiles (strata with ≥ 10 of each class), beside the pure-D reference. Printed:
  overall, within W, within E, R4 vs R3 within D.
- **Controls (two-sided, each within [0.42, 0.58]):** R0_61 vs R0 (storage), R2w4 vs R0 (warp), S0 vs R2w4 (seam, same
  base and hull), R2w4 vs R2w (warp magnitude). S0 vs R0 is printed.
- **Not controlled:** the border (no clean border-blanked set among these rows) and spectacles (no label on the
  ladder).
- **Kill:** S4 vs S3 within D ≤ 0.60, or any control outside [0.42, 0.58].
- **Readable:** ≥ 0.65 within D with every control in band. Otherwise "inconclusive".
- **Floor and gains:**
  - the 27-statistic best single statistic (cross-fitted by host halves);
  - the binding cross-fitted gain of the echo over [27 statistics + seam tone luma and R−G steps + log sharpness
    ratio], at ≥ +0.03;
  - Sb's increment (FS1 seeds 403-407): gain of the echo over Sb's logit, ≥ +0.03 on ≥ 4 of 5 seeds, also printed on
    the 191 test hosts alone.
- **ADVERSARY floor:** the read of this part waits if ADVERSARY announces it as pending.
- **Arm (ledger f):** only if the premise holds, the single image is readable, both gains are met, **and** the
  look-alike matched set (LA1) exists and passes. No arm is licensed before LA1, whatever these numbers are.

## 6. Cost and commands

- About 7 CPU minutes (measured 1.4 s per host). Reader: seconds plus the bootstrap.
- `OMP_NUM_THREADS=1 nice -n 19 .venv-spark/bin/python -I src/ME1/me1_measure.py`, then
  `... src/ME1/me1_read.py --part all --out experiments/ME1_layer-misregistration-echo/me1_read.json`, run once.
- Pins in `src/ME1/SHA256SUMS`.

## 7. Risks

- **Natural double structures** (eyelids, hair, spectacles) inflate the echo in every class.
- **Storage blur** hides echoes (the R0_61 control).
- **Expression difference** in same-person pairs is a real "two shapes" effect.
- **The oracle reconstruction** 2S − counterpart amplifies rounding noise.
- **The single-image statistic** is one choice among several (autocorrelation, not cepstrum); its window and lag set
  are fixed here.
