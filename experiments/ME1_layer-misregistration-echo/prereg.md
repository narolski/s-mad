# Layer misregistration echo (ME1): registration (in force from the commit that adds amendment 1; draft at ddf75a7)

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

## Amendment 1 (13 Nov; pre-run check `experiments/reviews/PRERUN_ME1_20261113.md`, c23f7e0; lead's answers; registered before any value of the 291 hosts exists)

The fixes below replace the corresponding draft text. The code is `src/ME1/me1_measure.py` and `src/ME1/me1_read.py`,
re-pinned in `src/ME1/SHA256SUMS` and tested on 4 hosts and on fully randomised mock data. The 4-host test file
(`me1_feats_limit4.csv`) was not looked at. The earlier 6-host test file was deleted (my own temporary file).

- **O1 (lead's answer 1: the gate replaces the registered statistic).**
  - Null response r* = the 95th percentile of the responses of phaseCorrelate(H_w window, H_w window 48 px lower),
    both inside the eroded hull, computed per pair.
  - Statistic = median shift over windows with response > r* (at least 10 windows, otherwise not finite), together
    with the fraction of windows above r*.
  - The ungated median is printed only.
- **O2 (positive calibration).** The gated shift between R2w4 and R2w (one texture, two geometries) must have a
  Spearman ρ ≥ 0.5 with the mean landmark distance |mean(H, B) − mean(H, S)|. Otherwise the oracle is "invalid
  (estimator)" and the result is inconclusive.
- **O3 (base).** The binding gain is over [log E, log W, log median response]. The gain over [log E, log W] is printed.
  The point estimate and the bootstrap use the same fold seed (20261191). Rule: "no" if < +0.02; "yes" if ≥ +0.03 with
  a component lower bound > 0; otherwise "inconclusive"; inconclusive if > 1% of draws fail.
- **O4 (strata).** Binding within-W, within-E and within-D reads use quintiles computed inside each database, combined
  with weights n_pos × n_neg. A binding read with coverage < 0.50 gives "inconclusive (coverage)". A component-bootstrap
  interval is printed for the within-W AUC.
- **S1 (statistic).** The echo is the median over windows of the largest prominence. A prominence is a local maximum
  among its 8 neighbours, minus the median autocorrelation at the same radius, after dividing out the Hann window's own
  autocorrelation (code verbatim from the review). The old maximum is kept as `echo_raw` and printed only.
- **S2 (one layer against two).**
  - Checks S4 vs R2w4 and S3 vs R2w (same host, geometry and hull): if both are ≤ 0.55, the statistic does not see a
    second layer, and the part is closed.
  - The paired difference [echo(S4) − echo(R2w4)] against [echo(S3) − echo(R2w)] within D is binding beside the
    primary.
- **S3 (lead's answer 2: no separate adversary row).** The single-image part reads against the adversary's existing
  `dev_S4_vs_S3` and `test_S4_vs_S3` floors. The code refuses to run it until those floor files exist and prints them
  beside the shortcut gain. TB1's single-image band features (r_1..r_5) are added to the shortcut base.
- **S4 (rules).**
  - "Readable" needs within-D ≥ 0.65, the paired difference ≥ 0.65, and a component lower bound of the within-D AUC
    above 0.60.
  - The shortcut gain follows the oracle's gain rule.
  - Rows with a non-finite statistic are dropped pairwise and counted. Above 5% missing in any rung, its contrast is
    "not measured".
  - A control outside its band gives "invalid (control)". Each host has exactly one row per rung (asserted).
- **S5 (masks).** The binding warp control is R2w4 against R0 on the amendment-7b hull (R0_m7). The mH version is
  printed.
- **L1 (licence; replaces the pass sentence of the draft).** "A pass means that two-person blends show more
  between-landmark misregistration than same-person blends, at equal D. It does not separate this from FR
  dissimilarity or W (cos_HB ≤ 0.65 < 0.68 ≤ cos_HS). It holds for landmark morphs on one engine only, and it is not a
  detector. An oracle pass licenses nothing about one image."
- **M1 (notes).**
  - The FRGC source photos were JPEG, so source compression survives inside the PNG frames; per-database prints cover
    this.
  - The controls became two-sided (draft change from the ledger's one-sided ≤ 0.58).
  - The reconstruction error is −1 or 0 grey levels, from truncation. The review checked R4 against the mean of the
    halves within 0.5 levels on all 536 hosts.
- **Order.** The oracle part is read once now, after the full measurement. The single-image part waits for the
  adversary floors.

## Code fix after the oracle outcome (13 Nov; labelled as such) and a prediction logged before the single-image read

- **Code fix (after the oracle outcome, which is closed by the lead's ruling).** The shared cross-fitting helper is
  `src/TB1/tb1_amend2.py` `cf_scores`. TB1 amendment 2 was read with it, so it is left unchanged. Instead,
  `src/ME1/me1_read.py` uses its own copy, `cf_scores_safe`, which skips empty folds and counts them in the output
  (`empty_folds`). Re-pinned.
- **Logged prediction for the single-image part (held for the adversary's dev_S4_vs_S3 and test_S4_vs_S3 floors):** the
  "sees a second layer" check (S4 vs R2w4 and S3 vs R2w) fails, with both ≤ 0.55, because the layers share no
  window-level correlated structure.

## Operations note (13 Nov, after the adversary floors were pinned at 35f25a7 / pins_stage3; before this part is read)

The read prints the adversary's floors beside its own registered floor: the all-cue ADV floor, the non-F27/non-BLEND
floor and the floor's within-BD1-D-quintile values, through `check.exceeds` on the pinned files
(`src/PR1/adv_beside.py`). Contrasts: ri_S4_vs_S3, test_S4_vs_S3, dev_S4_vs_S3; for RI1 also ri_R4_vs_R3 and
ri_R4_vs_R0. Printed only. No registered rule changes.
