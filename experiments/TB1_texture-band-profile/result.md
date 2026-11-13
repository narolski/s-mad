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
| hull (primary) | 0.783 | **0.758** [0.718, 0.795] (pure-D reference 0.524) | 0.707 (0.566) | 0.776 (0.509) | 0.787 (0.500) |
| hull eroded 16 px (printed) | 0.821 | 0.809 | 0.773 | 0.820 | 0.823 |

- **Registered verdict for the premise: "premise holds (≥ 0.70 within D)".** The table's reading also needs the S
  part (the single-image read), which waits for ADVERSARY.
- By database (printed): FRGC 0.864, **colorFERET 0.554** (n = 56).
- Joint D-tertile × G-half strata: 0.843, 0.823, 0.815, 0.788, 0.715, 0.609. The lowest is in the highest-D tertile
  with large G.
- **Stated limits.** The profile is computed on the half-difference, which needs the counterpart image: this is an
  oracle premise, not a detector. Equal D is one-dimensional. The colorFERET value is near chance, so the premise holds
  on FRGC hosts and not visibly on colorFERET hosts.
