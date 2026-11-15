# AD1 step 1 result: MorDIFF ladder from the A43 scores (post hoc re-read)

Owner run, 11 Nov 2026. **Post hoc, outcome partly known** (A43 aggregate table read before the
prereg). No image generated, no score recomputed: every number comes from existing per-image score
files. Code: `src/AD1/ad1_read.py`, `src/AD1/ad1_expr.py` (CPU, 50 s). Outputs:
`ad1_ladder.json`, `ad1_ladder.csv`, `ad1_expr_split.json`.

## Sources

- A43 scores: `/mnt/t7/smad_heldout/a43/a43_out/a43/<release>/<mode>/scores_a43.npz` (manifest
  `a43.csv` sha ce3a264a…, checked against every file).
- R1 (E7 MorDIFF pool, `mordiff`/`resmatch`, 204): registered eval scores
  `smadcvpr_runs/A12_scored/A12REL/<release>/scores_eval.npz` and, for SelfMAD own preprocessing,
  `experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz` (eval.csv sha 86d055d3…).
  Consistency check on the 204 shared R0 frames, A43 file vs eval file: max |Δscore| 0 (ViT-B/16),
  3e-12 (ViT-L/14), 4.2e-4 (SelfMAD own), 2.8e-4 (SelfMAD our pipeline).
- Reader check: my re-implementation of the `a41_read.py` pigeonhole person bootstrap (same seed as
  A43) reproduces A43's printed numbers exactly, e.g. ViT-B/16 R3m 0.480 [0.382, 0.578], R2m 0.706
  [0.625, 0.785], bridge 0.505 [0.473, 0.539]; SelfMAD own R2m 0.252.

## Ladder mapping

R0 = FRLL photo in the MorDIFF cell (204). R1 = its E7 copy (204). R2 = D20, DiffAE reconstruction of
one photo at the matched 20 steps (204). R3 = C20, DiffAE mix of the neutral and smiling photo of one
person (102). R4 = B20, our same-pair DiffAE morphs at 20 steps (200; 100 neutral pairs, 100 smiling
pairs). Benchmark R4 = the 200 sampled published MorDIFF morphs. Bridge = published vs B20.
Bootstrap: two-way person (pigeonhole), 102 persons, B = 10,000. Share = step d′ / d′(R0 vs published).

## Gates

- **G-a (reproduction): fails or unverifiable for every row, so every cell is "not reproduced,
  descriptive".** EER R0 vs the 200 sampled published morphs: ViT-B/16 5.4% vs 1.10% published
  (A41 on all 1,000 morphs: 4.9%); ViT-L/14 26.0% vs 19.3%; SelfMAD own preprocessing 2.0%, no
  published MorDIFF number in the record.
- **G-b (twin validity), from the A43 manifest glint cosines, before scores:** oracle AUC morph vs
  twin (lower min-cosine to the two source photos = morph) 1.000; B20 verifies against both
  contributors at FMR 1e-3 in 99.5%; C20 verifies against A in 100%. Passes. Negative control
  twin(A, A′) vs twin(A′, A) not available (one twin per person).
- **G-c (probe readability): not done** (needs features; outside this step).

## Results (AUC [95%], higher rung = positive)

| Step | ViT-B/16 release | ViT-L/14 release | SelfMAD own prep. | SelfMAD our pipeline (desc.) |
|---|---|---|---|---|
| Benchmark R0 vs published | 0.986 [0.970, 0.997] | 0.825 [0.746, 0.896] | 0.994 [0.983, 1.000] | 0.977 [0.954, 0.993] |
| Bridge published vs B20 | 0.505 [0.473, 0.539] | 0.486 [0.458, 0.509] | 0.481 [0.448, 0.513] | 0.478 [0.449, 0.499] |
| R0 → R1 (E7) | 0.894 [0.863, 0.924] | 0.645 [0.616, 0.681] | 0.997 [0.992, 1.000] | 0.985 [0.973, 0.995] |
| R1 → R2 | 0.917 [0.891, 0.942] | 0.743 [0.719, 0.772] | 0.426 [0.391, 0.459] | 0.414 [0.381, 0.443] |
| R0 → R2 | 0.992 [0.982, 0.999] | 0.877 [0.848, 0.907] | 0.996 [0.990, 1.000] | 0.982 [0.966, 0.994] |
| R2 → R3 | 0.266 [0.216, 0.315] | 0.444 [0.396, 0.492] | 0.678 [0.629, 0.727] | 0.683 [0.637, 0.730] |
| R3 → R4 | 0.706 [0.625, 0.785] | 0.541 [0.422, 0.652] | 0.252 [0.186, 0.323] | 0.290 [0.213, 0.371] |
| **Main R2 vs R4** | **0.480 [0.382, 0.578]** | **0.486 [0.384, 0.588]** | **0.403 [0.324, 0.487]** | 0.460 [0.372, 0.549] |
| R2 vs published | 0.487 [0.381, 0.594] | 0.471 [0.369, 0.573] | 0.379 [0.305, 0.457] | 0.436 [0.355, 0.518] |

Shares of the benchmark d′ (point [95%]):

| Share | ViT-B/16 | ViT-L/14 | SelfMAD own | SelfMAD pipe |
|---|---|---|---|---|
| R0 → R1 | 0.57 [0.49, 0.65] | 0.40 [0.29, 0.57] | 1.04 [1.00, 1.16] | 1.09 [1.00, 1.19] |
| R1 → R2 | 0.63 [0.55, 0.71] | 0.70 [0.52, 0.98] | −0.07 [−0.12, −0.04] | −0.11 [−0.16, −0.07] |
| **R0 → R2** | **1.10 [0.99, 1.23]** | **1.24 [0.94, 1.73]** | **1.04 [1.00, 1.13]** | 1.05 [0.97, 1.15] |
| R2 → R4 (main) | −0.02 [−0.15, 0.08] | −0.04 [−0.43, 0.19] | −0.10 [−0.20, −0.01] | −0.05 [−0.18, 0.06] |

d′ shares are not additive (unequal variances, saturated AUCs); they are printed per step as the plan asks.

Twins' (C20) rejection rate at the benchmark EER threshold (exact 95%): ViT-B/16 76/102 = 0.75
[0.65, 0.83]; ViT-L/14 78/102 = 0.76 [0.67, 0.84]; SelfMAD own 101/102 = 0.99 [0.95, 1.00]. At the
same threshold the reconstructions D20 are flagged at 99.5% / 82.4% / 98.5%, the E7 photos at
53.9% / 51.0% / 98.0%.

## Verdicts under the fixed rules (all cells descriptive by G-a; post hoc)

| Detector | Main (R2 vs R4) | Side R3 vs R4 | Side R2 vs R3 |
|---|---|---|---|
| MADation ViT-B/16 release | **reads the benchmark** (R0 → R2 share LB 0.99; main folded 0.52, UB 0.62) | mixed (0.71) | **twin artefact, cell invalid** (0.27, UB 0.32: reconstructions score above same-person mixes) |
| MADation ViT-L/14 release | **reads the benchmark** (share LB 0.94; folded UB 0.62) | mixed (0.54; folded UB 0.653 misses the 0.65 bar) | no identity reading (0.44, folded UB 0.60) |
| SelfMAD release, own preprocessing | **reads the benchmark** (share LB 1.00; the E7 step alone carries it) | **twin artefact, cell invalid** (0.25, UB 0.32; reproduces A43's 0.252) | mixed (0.68) |
| SelfMAD release, our pipeline (descriptive) | reads the benchmark | twin artefact, cell invalid (0.29) | mixed (0.68) |

FE / FS variants (descriptive, `ad1_ladder.json`): none separates the benchmark above 0.71; FS ViT-B/16
is reversed (0.25), so its shares are undefined.

## Expression confound (descriptive, `ad1_expr_split.json`)

R3 (C20) mixes a neutral and a smiling photo; R4 (B20) keeps one expression per pair; R2 (D20) has one
expression per image. Expression-matched main contrast (B20 vs D20 within neutral / within smiling):
ViT-B/16 0.444 [0.312, 0.580] / 0.510 [0.394, 0.625]; ViT-L/14 0.475 / 0.495; SelfMAD own 0.408 /
0.398. The main verdict does not depend on expression. R3 → R4 split by the morph's expression:
ViT-B/16 0.646 [0.536, 0.756] neutral vs 0.765 [0.674, 0.844] smiling; SelfMAD own 0.259 / 0.246.
The ViT-B/16 R3 → R4 value is therefore partly an expression effect; the SelfMAD twin artefact is not.
An expression-matched twin set (R2x) does not exist; the side-study cells stay confounded.

## MixFaceNet-MAD

Not added. The A46 RGB-only scorer (`smadcvpr/a46_rgb_score.py`) is bound to its own plan, manifest
`a46_rgb_only.csv` and data pins (`verify_data(..., require_complete=True)`) and requires the
registered H100; it cannot run unchanged on the A43 images. No per-image MixFaceNet scores of the A43
arms exist.

## Not verifiable / caveats

- Published MorDIFF EER of the SelfMAD release: not in the record (G-a "not in record").
- The 20-step match is relative to 20 vs 100 steps (A43 qualifier); R2 images are stored at the
  published files' small size (about 150 px wide), so R1 → R2 mixes rendering and that storage history.
- Arm E (photo through DiffAE's aligner and the A43 storage) already scores far above R0 for every
  detector (ViT-B/16 0.856, SelfMAD own 1.000): storage at the published size alone moves them.
- R1 frames come from a different scoring run than R0/R2 (same frames; consistency checked above).
- G-c and the twin negative control were not run. Scores are near-binary for SelfMAD, so AUCs near
  1.0 saturate the d′ (clipped at AUC 0.995).

## Correction, 11 Nov 2026 ~17:40 (independent review)

(1) The released MADation FE ViT-L/14 reads the mixing step: R2 vs R4 0.655 [0.580, 0.730] (20 steps),
0.852 (100 steps), with R0 → R2 only 0.561; "no released detector reads the morph step" is false.
(2) Rename the ViT-B/16 R2 vs R3 label to "non-monotone rung; same-person mix confounded by expression".
(3) Drop d′ shares from prose; quote AUCs and flag rates: E7 raises the share flagged at the EER threshold
from 5% to 54% (ViT-B/16), 26% to 51% (ViT-L/14), 2% to 98% (SelfMAD); at a 1%-photo threshold 13%, 12%,
88% (`ad1_flagrates.json`). Full record: `README.md`.
