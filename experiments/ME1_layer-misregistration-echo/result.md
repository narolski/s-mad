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

### Erratum and results review of the single-image part (`experiments/reviews/REVIEW_TB1S_ME1_RI1_20261113.md`, ACCEPT WITH EDITS; added `date`: Fri Nov 13 21:44 CET)
Registered (code) verdict: "not measured (R2w4, R2w, R0_61 > 5% missing)".

Erratum to the explanation above: it is the hull median prominence that is exactly 0 on 287 of 291 warp-only R2w4 and R2w rows, not the ring.
- The ratio is therefore 0, a finite value; the reader's log turned it into −inf.
- Truly missing rows: 1.4% (R2w4, R2w) and 5.5% (R0_61).

Read as the registration's text says (post hoc), the verdict is "invalid (control)": R2w4 vs R0_m7 0.002 and S0 vs R2w4 0.991. The statistic records resampling history (zero after one warp or one downscale), not a second layer. S4 vs S3 within D 0.596 [0.561, 0.633] is printed only and is not a kill. Lead's ruling on which verdict string the record carries: [pending].

What the paper may say: "An autocorrelation echo statistic was dominated by resampling history and gave no usable reading."

## Closing (lead's ruling, 13 Nov 2026: ME1 is closed for the sprint)

**Verdict of record for the single-image part: "invalid (control)".** This is the verdict the registered text gives (R2w4 vs R0 on the 7b hull 0.002; S0 vs R2w4 0.991). The reviewer derived it from the numbers already computed; there was no second read.
- The code's printed string, "not measured (R2w4, R2w, R0_61 > 5% missing)", stays in `me1_single.json` as printed.
- That string comes from a reader fault: a log of a zero hull median made 287 of 291 warp-only rows non-finite. Truly missing rows are 1.4% (R2w4, R2w) and 5.5% (R0_61). The reader is not re-run.

**Established.**
- The oracle is not measurable with the registered estimator: the gated statistic is non-finite for most pairs.
- The single-image part is invalid by its controls. The echo statistic records resampling history (zero after one warp or one downscale), not a second layer.

**May not be written.** Neither string licenses anything: no kill, no arm and no mechanism claim. S4 vs S3 within D (0.596) is printed only.

**Not run, available after the deadline.** A finite-safe echo estimator (no log of a zero median) that is insensitive to resampling history, registered fresh.

**Saved features, kept for reuse.** `/mnt/t7/smad_next/ME1/me1_feats.csv` (`9cdd6b94…`).
