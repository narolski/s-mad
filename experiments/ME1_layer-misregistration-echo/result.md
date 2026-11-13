# Layer misregistration echo (ME1): result

Development data only. Registration: `prereg.md` (draft ddf75a7) with amendment 1 (7008986), after the pre-run check
`experiments/reviews/PRERUN_ME1_20261113.md` (c23f7e0).

## Oracle part: not measured as registered (13 Nov, measurement finished 20:26 by the machine clock)

- Measurement `/mnt/t7/smad_next/ME1/me1_feats.csv` (sha256 `9cdd6b94…`, 291 hosts; every splice equals its
  counterpart outside the hull, asserted).
- The registered oracle statistic (amendment 1, O1) is the median shift over windows whose phase-correlation response
  exceeds the within-image null r*: the 95th percentile of responses between H_w windows 48 px apart. It requires at
  least 10 windows above r*. That condition fails for **267 of 291** two-person pairs and **264 of 291** same-person
  pairs. The calibration statistic (R2w4 against R2w, O2) is non-finite for **142 of 291** hosts. Each host has 255-318
  windows (median 318), so few cross-layer windows respond more strongly than the 95th percentile of the within-image
  null.
- The reader `src/ME1/me1_read.py --part oracle` then stopped with an error: a cross-fitting fold was empty because of
  the few finite rows. No contrast value was produced or seen.
- The only numbers looked at are missingness counts and window counts, which are properties of the estimator. Neither
  class-wise fractions nor shifts were looked at.
- **Outcome: the oracle part is "not measured"**: the gated statistic as registered is not finite for about 91% of
  hosts. The draft's ungated statistic was rejected by the pre-run check (O1). No verdict on the ME1 premise is drawn,
  and the single-image part stays on hold (it also waits for the adversary floors).
- A different gate (for example a lower null percentile, or a gate on the pair's own response distribution) would be a
  new design. It needs a new amendment and a pre-run check before any value is read. That decision is the lead's.

## Lead's ruling (13 Nov): oracle closed as "not measurable with this estimator"

The only reading allowed: window-level phase correlation finds no above-null correlated structure between the two
layers on about 91% of pairs. It fails even on the calibration (one person's texture at two geometries) for 142 of
291 hosts. This is a property of the estimator and gives no verdict on the mechanism. No new gate is designed after
seeing that the registered one fails.

## Single-image part (read once at 20:38 by the machine clock, after the adversary floors were pinned; results review pending)

Reader `src/ME1/me1_read.py --part single`. Output: `me1_single.json`, `me1_single_stdout.txt`.

- **Registered verdict: "not measured (R2w4, R2w, R0_61 > 5% missing)".** The echo ratio (hull prominence over ring
  prominence) is non-finite on more than 5% of rows for the warp-only rungs R2w4 and R2w and for the stored-small R0_61.
  The ring median prominence is 0 there, so the ratio is undefined.
  - As a result the "sees a second layer" check (S4 vs R2w4, S3 vs R2w), the paired difference and three binding
    controls are not computable.
  - The adversary floors could not be printed (non-finite echo rows).
- Printed values on the rows that are finite (registered rules give no verdict from them):
  - S4 vs S3 within D 0.596 (coverage 0.81; component interval [0.561, 0.633]), pure-D reference 0.524;
  - R0_61 vs R0 0.100, on the finite subset only; S0 vs R0 0.451;
  - shortcut gain −0.004 [−0.014, +0.007] ("no" by its rule); Sb increment +0.000 to +0.003 (all hosts);
  - FRGC within D 0.596; colorFERET not computable (coverage 0).
- **Logged prediction** ("sees a second layer" fails, both ≤ 0.55): not testable, because the check is not computable.
