# Texture band profile, two people against one (TB1): result

Development data only. 291 BD1 hosts (FRGC 235, colorFERET 56). Registration: `prereg.md` (d4ebfd9) and amendment 1
(6af821f), after the pre-run check `experiments/reviews/PRERUN_RI1_TB1_20261113.md`.

## Part 1: premise (read once, 13 Nov 19:37 by the machine clock; the S part waits for ADVERSARY's floor)

Features: `/mnt/t7/smad_next/TB1/tb1_feats.csv`, sha256 `a79980a3…`. Equality of each splice with its counterpart
outside the hull is asserted for all hosts. Reader: `src/TB1/tb1_read.py --part premise`. Output: `tb1_premise.json`,
`tb1_premise_stdout.txt`.

The premise asks whether the band profile of the luminance half-difference inside the hull tells two people apart from
two sessions of one person. Two-person: S4 − R2w4 = ½(B_w − H_w). Same-person: S3 − R2w = ½(S_w − H_w). The profile
is centred by its hull mean. The model is a cross-fitted logistic on the log profile over 5 octave bands, with 5 host
folds.

| | AUC | within D | within D_lin | within D_dc | within G |
|---|---|---|---|---|---|
| hull (primary) | 0.783 | **0.758** [0.718, 0.795] (pure-D reference 0.524) | 0.707 (0.566) | 0.776 (0.509) | 0.787, **withdrawn as a control** (see below) |
| hull eroded 16 px (printed) | 0.821 | 0.809 | 0.773 | 0.820 | 0.823, withdrawn |

- **Registered verdict for the premise: "premise holds (≥ 0.70 within D)".** The table's reading also needs the S
  part (the single-image read), which waits for ADVERSARY.
- By database (printed): FRGC 0.864, **colorFERET 0.554** (n = 56).
- Joint D-tertile × G-half strata: 0.843, 0.823, 0.815, 0.788, 0.715, 0.609. The lowest is in the highest-D tertile
  with large G.
- **Stated limits.** The profile is computed on the half-difference, which needs the counterpart image: this is an
  oracle premise, not a detector. Equal D is one-dimensional. The colorFERET value is near chance, so the premise holds
  on FRGC hosts and not visibly on colorFERET hosts.

## Post-result review of the premise (`experiments/reviews/REVIEW_TB1_PREMISE_20261113.md`, e7e57ed): needs qualification

The registered verdict "premise holds (≥ 0.70 within D)" stands. The physical sentence does not follow from it. Every
number in this section is **post hoc** (reviewer, from the registered feature file and the landmark files; scripts in
`experiments/reviews/scripts_tb1/`).

- **"Within G" is withdrawn as a control.** G is one value per host (the S4 and S3 rows carry the same G), so the G
  strata and the G halves of the joint strata control nothing.
- **Interval.** Folds and a bootstrap by connected components of the host-partner graph (110 components) give
  0.757 within D, with the component-bootstrap interval **[0.701, 0.801]**. This replaces [0.718, 0.795].
- **Energy (post hoc).**
  - The band-limited energy E over the same five bands separates the classes at 0.804, and 0.775 within D.
  - Within E quintiles the profile falls to 0.619.
  - The profile adds +0.033 over log E alone.
- **Finest band (post hoc).**
  - The B5 share alone gives 0.708 within D, and it carries FRGC.
  - colorFERET's fine-band shares are small in both classes.
  - The FRGC / colorFERET split looks like a source-detail (noise-floor) effect.
- **Geometry (post hoc).**
  - The landmark displacement W between the two source photos separates the classes at 0.869.
  - Within W quintiles the profile reads 0.707 (coverage 0.60). Joint D × W tertiles give 0.726.
- **Conclusion (reviewer's F6 wording, replacing any earlier reading):**

  "At equal BD1 D, the band-limited energy and the band profile of the luminance half-difference separate two-person
  from same-person pairs (0.76 within D; FRGC 0.86, colorFERET 0.55). Most of it is the share of the finest band, and
  at equal band-limited energy it falls to 0.62. It is not separated from the larger landmark displacement between two
  people (0.71 within W, coverage 0.60). An oracle reading on one engine. Not a texture trace of a second identity,
  and not a detector."

## Amendment 2 (post hoc; registered at cbbcdae with pre-run fixes 2b at 3f65cf9; read once at 19:51 machine clock)

Results review (Opus) `experiments/reviews/REVIEW_TB1_A2_20261113.md`: accept with corrections. Every number recomputed and matched; corrections applied below. Review numbers are post hoc.

Reader: `src/TB1/tb1_amend2.py`. Output: `tb1_amend2.json`, `tb1_amend2_stdout.txt`. 291 hosts. Folds and bootstrap
by connected components of the person graph: 110 components (the same count as the review; the 2b note expected it
to differ; the 2b F6 expectation was wrong, see the erratum in prereg.md).

- **Binding rule.** The profile's gain over [log E, log W] is **+0.010**: base 0.888, plus profile 0.898, 95%
  percentile interval over components [−0.006, +0.021], 0 of 2,000 draws failed. Five other fold seeds give
  +0.009 to +0.012. **Registered verdict: "falsified: the profile adds < +0.02 over band energy and geometry"**, by
  the registered point rule (+0.010 < +0.02). The interval excludes the supported bar (+0.03) but not +0.02.
- **H-new-1 survives:** its falsifier, a gain ≥ +0.03 with a lower bound > 0, did not occur. Band energy and geometry
  carry the all-hosts premise.
- **The databases behave in opposite ways.** On FRGC alone (descriptive, post hoc) the profile adds +0.018 (reviewer's
  component interval about [+0.003, +0.030]): small, probably above zero, below the +0.03 bar. On colorFERET it adds
  nothing (−0.016, n = 56). The base is near the ceiling (0.888; FRGC 0.921), so any gain is capped at about
  0.08-0.11.
- All-hosts within-strata AUCs mix databases: FRGC two-person rows are compared with colorFERET same-person rows in the
  same stratum. FRGC within E is 0.72 and within E × W 0.75. So "at equal band-limited energy it falls to 0.62" is
  partly a database-mix artefact.
- Gain over [log D, log E, log W]: +0.011 (base 0.888).
- Alone (direction-free): E 0.805, W 0.869, D 0.651. Profile 0.785.
- Profile within strata (descriptive): E 0.625 (coverage 0.80); W 0.709 (0.60); D 0.761; D × W 0.727 (0.69);
  E × W 0.593 (0.54).
- FRGC only (descriptive): gain over [log E, log W] +0.018; within E 0.715, within W 0.842, within E × W 0.750.
- **(a) Capture-day gap (descriptive):**
  - Same-day pairs: FRGC 3 and colorFERET 5 two-person, 0 same-person, so not computable and no session claim.
  - FRGC bins: 1-30 days 0.858 (43 / 92), 31-180 days 0.855 (92 / 94), > 180 days 0.855 (97 / 49).
  - colorFERET bins: 0.397 (6 / 13), 0.542 (6 / 8), 0.597 (39 / 35).
  - Same-day anecdote (n ≤ 8, no claim): FRGC 0.942 (n = 3), colorFERET 0.536 (n = 5).
- **(b) Matched W (descriptive):** 100 pairs matched within the caliper, 10 dropped, mean |Δ ln W| 0.024, medians 6.78
  / 6.78 px. AUC **0.672**, "not resolved". No verdict on H-new-2.
  - There were 110 eligible pairs, not about 40 as 2b expected.
  - The pooled 0.672 mixes FRGC (0.81) and colorFERET (0.48), and E is not matched (E alone gives 0.71 in the matched
    set).
  - On FRGC the profile still separates at matched W, which argues against a purely geometric reading (descriptive).
- **Day gap.** On FRGC the separation does not change with capture-day gap from 1 day to over 180 days. Same-day pairs
  cannot be tested (0 same-person).
- **Combined TB1 reading (premise, its review and amendment 2; all post hoc except the premise verdict).** "In an
  oracle half-difference reading on one morphing engine, two-person pairs differ from same-person pairs mainly through
  larger band-limited energy and larger landmark displacement. On FRGC the shape of the band profile adds a small
  further amount (about +0.02 AUC). On colorFERET there is no visible signal. This is not a texture trace of a second
  identity and not a detector." No arm may be justified by a profile-shape premise. Any arm must report per database.
- **Limit.** The earlier mock run may have written a W-only base value to an unviewed scratchpad file. Two matched-W
  medians from that mock were seen (amendment 2b F4).

## Single-image part S (read once at 20:36 by the machine clock, after the adversary floors were pinned; results review pending)

Reader `src/TB1/tb1_read.py --part s`. Output: `tb1_s.json`, `tb1_s_stdout.txt`. 291 hosts. The S4-vs-S3 fold models
score every row out of fold.

- S4 vs S3: AUC 0.654, **within D 0.657** (coverage 1.00).
  - Printed: within G 0.664 (G is per host, see the premise review), within seam-tone quintiles 0.654, guard-band
    version within D 0.625.
- **Controls** (scored by the S4-vs-S3 models; band [0.42, 0.58]; refit ceilings in brackets): R0_61 vs R0 0.565
  (0.657), R2w4 vs R2w 0.527 (0.527), S0 vs R2w4 0.472 (0.524). All in band. Printed: S0 vs R0 0.475, R2w4 vs R0 0.503.
- **Binding shortcut gain** of r over [27 statistics + splice shortcut features]: **+0.006**. Base 0.779 (27-statistic
  logistic alone 0.763), plus r 0.786. Best single statistic, cross-fitted: 0.657.
- **Sb increment** (gain of r over Sb's logit): 403 +0.025, 404 +0.023, 405 +0.026, 406 +0.013, 407 +0.019. That is
  ≥ +0.03 on 0 of 5 seeds. On test hosts alone: +0.013 to +0.025.
- **Per database (descriptive):** FRGC within D 0.684, gain +0.002, controls 0.575 / 0.519 / 0.485. colorFERET within
  D 0.583, gain +0.004, controls 0.526 / 0.558 / 0.428.
- **Adversary floors** (check.exceeds on pinned files; printed): the AUC is S4 vs S3 of the out-of-fold r score.

| Contrast | Arm AUC | All-cue ADV floor | Difference [95%] | Exceeds | Non-F27/non-BLEND floor | Floor within D (logreg) |
|---|---|---|---|---|---|---|
| ri_S4_vs_S3 | 0.654 | 0.773 | −0.118 [−0.151, −0.087] | no | 0.719 (difference −0.064, lower bound −0.100; no) | 0.757 (pure-D 0.572) |
| test_S4_vs_S3 | 0.647 | 0.754 | −0.107 [−0.155, −0.055] | no | 0.676 (lower bound −0.084; no) | 0.744 |
| dev_S4_vs_S3 | 0.670 | 0.820 | −0.150 [−0.211, −0.088] | no | 0.739 (lower bound −0.135; no) | 0.785 (coverage 0.60) |

- **Registered outcome table, applied mechanically.**
  - The controls are in band, P within D is 0.758 (≥ 0.70) and S within D is 0.657 (≥ 0.65).
  - Row 1 therefore applies: "a two-person texture trace exists and one image shows it; arm condition not met"
    (shortcut gain +0.006 < +0.03; Sb increment ≥ +0.03 on 0 of 5 seeds).
  - The row's wording rests on the premise sentence. The premise review and amendment 2 withdrew that sentence: the
    profile adds +0.010 over band energy and geometry, and the profile is not a texture trace of a second identity.
  - **Logged prediction** (binding gain fails): confirmed.
