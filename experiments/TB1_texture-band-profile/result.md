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
