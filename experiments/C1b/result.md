# C1b Is the expression imbalance used by detectors? Result

> **Correction, 11 Nov 2026 17:40 CET (owner, after the independent review `../reviews/REVIEW_C1b_20261111.md`
> and the follow-up study C1c).** The numbers below stand. Withdrawn: "only the expression differs" and
> "the expression cue is used" (row 15 USED): the smiling FRLL photos are also 1.43 times larger as files and
> have a 4.8 times noisier backdrop (102 of 102 persons), and the ViT-L/14 release's ordering fades with
> resolution and is weak in other photo pools. Also corrected: "CNN recipes do not show it" (the SelfMAD-style
> recipe M4 ranks the smiling photo higher in every untied pair) and "no CNN recipe network reaches 0.65"
> (M5 s2 es: 0.667). Corrected wording, reasons and the full list: `README.md`, section 7.

Owner run, 11 Nov 2026, DGX CPU only, zero GPU, no image re-encoded or written. Pre-registration
`prereg.md` (15:25 CET, before any score file was opened by this owner). Code `src/C1b/c1b_read.py`
(statistics a–c), `src/C1b/c1b_probe.py` (probe validation), `src/C1b/c1b_summarize.py` (tables, fixed
falsifiers). Outputs: `c1b_read.json`, `c1b_within_person.csv`, `c1b_cells.csv`, `c1b_probe.json`,
`c1b_summary.txt` (all tables, including those not copied here); bootstrap replicates
`/mnt/t7/smad_next/C1b/c1b_eer_bootstrap_reps.npz`. Smoke runs reproduced the reviewer preview
(ViT-L/14 release AMSL EER 17.65 all / 24.51 neutral-only; 101 of 102 persons).

**Deviations from the pre-registration.** (1) The statistic (b) bootstrap uses the first 2,000 rows of
the B = 10,000 person draw of statistic (a) (same seed 20261111) rather than a separate draw. (2) "Flip
beyond noise" in (c) is implemented as: the pair's EER-gap interval excludes 0 on one side with all genuine
photos and on the other side with neutral-only; the interval of the gap change is printed too. (3) The
FE ViT-B/16 release reads expression against the cue, a case the reading rule did not foresee; it is
reported as "undetermined, reversed". No other change.

**Post hoc rows.** Every release row and every early-stopped (es) recipe row was seen in aggregate by the
reviewer preview. H1 and H2 are decided on the last-checkpoint recipe files only, which no preview read.

**Scope.** 12 cells: FRLL-Morphs ×5 and DiM ×6 (imbalanced: 102 neutral + 102 smiling genuine against
neutral-only morphs) and MorDIFF (balanced). **The five corrected-MAD22 cells are left out**: no score on
the corrected MAD22 exists (canonical164 cancelled; WCSS job 6299123 still pending, start forecast
13 Nov). The `eval.csv` `mad22` rows (old 185 + 4,069 subset) were not read. MAD22c Webmorph, the 12th
imbalanced cell, is therefore untested. Note: C1 counts "11 of 17" imbalanced cells but lists DiM ×6 +
FRLL-Morphs ×5 + MAD22c Webmorph = **12 of 17** (balanced: MAD22c FaceMorpher, MIPGAN-I, MIPGAN-II,
OpenCV, MorDIFF = 5). The 11 imbalanced cells tested here are all of them except MAD22c Webmorph.

Detectors: 9 release score sets (MADation ViT-B/16, ViT-L/14, FE ×2, FS ×2; SelfMAD own preprocessing and
our pipeline; MixFaceNet-MAD on our frames) and 51 primary recipe networks × 2 checkpoints (es, last) =
111 score sets, from `mambamorph-code/smadcvpr_runs/A12_scored/` and
`experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz` (every file carries the `eval.csv`
sha 86d055d3…, asserted in the reader; the SelfMAD own file checked by hand, all 26,077 rows cropped).
`/mnt/t7/wcss_backups/smadcvpr/runs/A12BR/` holds weights only. Score orientation as stored (higher =
morph), no flipping: MixFaceNet-MAD on our frames (EER 75–98 on four FRLL-Morphs cells) and the M4 recipe
(mean EER 89) are reversed on these frames and are descriptive only.

## (a) Within-person neutral-above-smiling AUC

AUC_wp = share of the 102 FRLL persons whose neutral photo (03) gets a higher morph score than their
smiling photo (08); 0.5 = no expression reading, > 0.5 = neutral looks more morph-like. 95% person
bootstrap, B = 10,000. Frames: `frll_bona` (= `dim_bona`, byte-identical). Secondary: MorDIFF's own
genuine frames (`mordiff_bona`, a different crop).

| Detector (release, post hoc) | AUC_wp [95%] | persons | pooled AUC [95%] | on MorDIFF frames |
|---|---|---|---|---|
| MADation ViT-B/16 | 0.578 [0.480, 0.676] | 59/102 | 0.539 [0.501, 0.577] | 0.529 [0.431, 0.627] |
| **MADation ViT-L/14** | **0.990 [0.971, 1.000]** | 101/102 | 0.855 [0.814, 0.898] | 0.794 [0.716, 0.873] |
| MADation FE ViT-B/16 | **0.088 [0.039, 0.147]** (reversed) | 9/102 | 0.238 [0.193, 0.279] | 0.098 [0.049, 0.157] |
| MADation FE ViT-L/14 | 0.343 [0.255, 0.432] | 35/102 | 0.405 [0.362, 0.444] | 0.206 [0.127, 0.284] |
| MADation FS ViT-B/16 | 0.539 [0.441, 0.637] | 55/102 | 0.528 [0.490, 0.567] | 0.657 [0.568, 0.745] |
| MADation FS ViT-L/14 | 0.500 [0.402, 0.598] | 51/102 | 0.493 [0.437, 0.546] | 0.520 [0.422, 0.618] |
| SelfMAD, own preprocessing | 0.480 [0.382, 0.578] | 49/102 | 0.489 [0.446, 0.532] | 0.422 [0.324, 0.520] |
| SelfMAD, our pipeline (desc.) | 0.314 [0.225, 0.402] | 32/102 | 0.418 [0.379, 0.454] | 0.412 [0.314, 0.510] |
| MixFaceNet-MAD, our frames (desc.) | 0.471 [0.373, 0.569] | 48/102 | 0.479 [0.450, 0.509] | 0.529 [0.431, 0.627] |

| Recipe, checkpoint | n | AUC_wp per seed | mean | n ≥ 0.65 | on MorDIFF frames, per seed |
|---|---|---|---|---|---|
| **M3 last** (pre-registered) | 8 | 0.88 0.75 0.78 0.67 0.97 0.82 0.72 0.85 | **0.806** | 8 | 0.90 0.66 0.72 0.66 0.93 0.76 0.85 0.80 |
| **M3L last** (pre-registered) | 5 | 1.00 1.00 1.00 1.00 1.00 | **1.000** | 5 | 0.94 0.97 0.96 0.99 0.96 |
| M3 es (post hoc) | 8 | 0.98 0.99 0.84 0.99 0.94 0.95 0.89 0.95 | 0.942 | 8 | 0.28 0.27 0.22 0.31 0.15 0.34 0.20 0.24 |
| M3L es (post hoc) | 5 | 0.96 0.81 0.92 0.96 0.91 | 0.914 | 5 | 0.08 0.13 0.11 0.14 0.09 |
| M1 last / es | 5 | 0.45–0.54 / 0.44–0.63 | 0.494 / 0.500 | 0 / 0 | |
| M2 last / es | 5 | 0.48–0.63 / 0.43–0.63 | 0.560 / 0.537 | 0 / 0 | |
| M4 last / es | 5 | 0.34–0.46 / 0.00–0.34 | 0.414 / 0.199 | 0 / 0 | reversed (0.00–0.29) |
| M5 last / es | 8 | 0.25–0.61 / 0.28–0.67 | 0.440 / 0.491 | 0 / 1 | |
| M6 last / es | 5 | 0.48–0.65 / 0.48–0.58 | 0.567 / 0.525 | 0 / 0 | |
| M8 last / es | 5 | 0.44–0.62 / 0.43–0.63 | 0.561 / 0.551 | 0 / 0 | |
| M8O last / es | 5 | 0.43–0.61 / 0.45–0.58 | 0.541 / 0.520 | 0 / 0 | |

(M6 s2 last is 0.647, below 0.65.) Per-network intervals: `c1b_within_person.csv`.

## Fixed falsifiers

- **H1 (smile direction): not falsified.** 13 of 13 last-checkpoint MADation-recipe networks reach
  AUC_wp ≥ 0.65 (bar: 10). Lowest: M3 s4 0.667 [0.578, 0.755]; all 13 lower bounds are above 0.57; the
  five M3L networks score the neutral photo higher in 102 of 102 persons.
- **H2 (training length): falsified.** Mean AUC_wp of the 8 last-checkpoint M3 networks = 0.806
  (range 0.667–0.971; bar for falsification ≥ 0.70); 0 of 8 are at or below 0.60.
- Descriptive (post hoc): all 13 es checkpoints are also ≥ 0.81 on these frames. Among the releases only
  ViT-L/14 reads expression in the cue's direction (0.99); ViT-B/16 is at 0.58 [0.48, 0.68]; the FE
  variants read it in the **opposite** direction (FE ViT-B/16 0.09: smiling photos look more morph-like).
  No CNN recipe network and neither SelfMAD pipeline reaches 0.65.
- Unexplained (not tested): on MorDIFF's own genuine crop, every es checkpoint of M3 and M3L reverses
  (0.08–0.34) while the last checkpoints stay positive (0.66–0.99). The expression response of a given
  network can depend on framing; the per-cell error rates below use each cell's own frames.

## (b) Error rates with all, neutral-only and smiling-only genuine photos

EER change "neutral-only minus all" in points, 95% two-way person bootstrap (pigeonhole, B = 2,000,
paired on one draw). Positive = the benchmark EER is lowered by the smiling half of the genuine class.

| Release (post hoc) | amsl | facemorpher | opencv | stylegan | webmorph | dim_a | dim_c | fast_dim | fast_dim_ode | greedy_dim | greedy_dim_s | mean | LB > 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MADation ViT-B/16 | +0.4 [−1.2, +2.9] | +0.1 | +0.1 | +0.3 | +1.1 [−0.2, +3.0] | +0.1 | +0.4 | +0.5 | +0.5 | +0.9 | +1.8 [−0.8, +3.0] | +0.57 | 0/11 |
| **MADation ViT-L/14** | **+6.9 [+3.5, +10.3]** | +0.0 | +0.1 | **+13.3 [+9.3, +18.5]** | +1.9 [+0.1, +3.5] | +5.4 [+3.0, +10.4] | +5.4 [+1.9, +8.3] | +5.6 [+2.8, +10.5] | +6.4 [+2.0, +8.5] | +4.0 [+0.7, +6.0] | +1.1 [+0.1, +3.9] | **+4.55** | 9/11 |
| MADation FE ViT-B/16 | −8.4 [−12.5, −5.8] | −8.8 | −9.9 | −10.8 | −8.8 | −8.3 | −9.3 | −9.8 | −9.7 | −10.7 | −9.3 | −9.42 | 0/11 (UB < 0 in 11/11) |
| MADation FE ViT-L/14 | −1.0 | +0.0 | −0.4 | −0.6 | −2.0 | −1.0 | −1.3 | −1.1 | −1.0 | −0.2 | −1.1 | −0.88 | 0/11 |
| MADation FS ViT-B/16 | −0.2 | −1.0 | +0.0 | −1.4 | +0.3 | −1.0 | −0.3 | −1.2 | −0.4 | −0.9 | −2.4 | −0.78 | 0/11 |
| MADation FS ViT-L/14 | −0.9 | −0.1 | +0.2 | −0.3 | −0.5 | +0.0 | −0.3 | +0.0 | −0.9 | −0.2 | −0.9 | −0.37 | 0/11 |
| SelfMAD, own preprocessing | −2.0 [−3.5, −0.4] | −0.2 | +0.0 | −1.3 | −2.2 [−4.6, −0.4] | −1.9 | −1.0 | −2.1 | −2.3 | −1.7 | −1.0 | −1.43 | 0/11 |
| SelfMAD, our pipeline (desc.) | −3.0 | +0.0 | −0.3 | −3.4 | −3.3 | −3.7 | −1.1 | −3.4 | −2.3 | −3.0 | −1.0 | −2.22 | 0/11 |
| MixFaceNet-MAD, our frames (desc.) | −0.5 | +0.0 | +0.0 | −0.9 | −0.0 | +0.0 | −0.2 | −0.1 | −0.1 | −0.4 | −0.6 | −0.26 | 0/11 |

Intervals for every entry: `c1b_summary.txt` and `c1b_cells.csv`. EER all / neutral-only / smiling-only
for ViT-L/14 release: AMSL 17.7 / 24.5 / 7.9; FRLL-Morphs StyleGAN 52.4 / 65.7 / 34.3; DiM-A
22.0 / 27.4 / 10.8; Fast-DiM 22.6 / 28.2 / 11.8; FaceMorpher and OpenCV unchanged (1.0).

BPCER at APCER 5% (all → neutral-only), ViT-L/14 release: AMSL 31 → 51 (+20 [+14, +25]), StyleGAN 87 → 99,
DiM-A 43 → 71 (+27 [+19, +34]), DiM-C 35 → 58, Fast-DiM 43 → 71, Fast-DiM-ODE 29 → 49, Greedy-DiM 16 → 25,
Greedy-DiM-S 15 → 24, WebMorph 5 → 8; 0 → 0 on FaceMorpher and OpenCV. ViT-B/16 release: +0 to +3 points.
FE ViT-B/16 release: −9 to −19 points in every imbalanced cell. SelfMAD own preprocessing: 0 to −6.

Recipes, seed mean of the EER change over the 11 imbalanced cells (cells × networks with lower bound > 0):

| Recipe, ckpt | mean EER change | largest cells | LB > 0 | mean EER (all genuine) |
|---|---|---|---|---|
| **M3L last** | **+6.88** (per network +5.8 to +8.6) | StyleGAN +21.4, Fast-DiM +13.8, Greedy-DiM +11.1, Greedy-DiM-S +9.6 | 35/55 | 14.6 |
| M3L es | +1.74 | Greedy-DiM +5.0, Fast-DiM +3.7, AMSL +3.4 | 22/55 | 9.8 |
| **M3 last** | +1.02 (−0.7 to +3.2) | Greedy-DiM +6.6, StyleGAN +4.7; others −0.3 to +0.9 | 10/88 | 8.9 |
| M3 es | +2.43 | Greedy-DiM +5.7, StyleGAN +3.2, AMSL +2.9 | 49/88 | 8.4 |
| CNN recipes last (M1 M2 M4 M5 M6 M8 M8O, 38 networks) | +0.17 (−3.1 to +1.7) | M8 +1.1 | 2/418 | — |
| CNN recipes es (38) | −0.12 | | 5/418 | — |

Family summary (mean over the 11 imbalanced cells; EER points, BPCER@APCER5 points):

| Family | EER change | BPCER@5 change | AUC_wp |
|---|---|---|---|
| MADation ViT-L/14 release | +4.5 | +13.7 | 0.99 |
| MADation ViT-B/16 release | +0.6 | +1.6 | 0.58 |
| MADation FE / FS releases (4) | −2.9 (FE B/16 −9.4) | −5.3 | 0.09–0.54 |
| SelfMAD release (2 pipelines) | −1.8 | −2.9 | 0.31–0.48 |
| MixFaceNet-MAD release (desc.) | −0.3 | −0.4 | 0.47 |
| M3L last (5) / M3 last (8) | +6.9 / +1.0 | +21.8 / +2.7 | 1.00 / 0.81 |
| CNN recipes last (38) | +0.2 | −0.2 | 0.51 |

Across all 111 score sets, Spearman(AUC_wp, mean EER change) = 0.86. A high AUC_wp does not always move the
EER: M3 last reads expression (0.67–0.97) but its EER moves in only 10 of 88 network × cell combinations,
because on most cells its genuine scores sit well below the morph threshold region; the shift shows up
where the genuine and morph scores overlap (StyleGAN, Greedy-DiM).

MorDIFF (balanced cell, descriptive): ViT-L/14 release EER 28.9 / 31.4 / 26.3 (neutral-only − all
+2.5 [+0.2, +4.6]); in the 2 × 2 table its AUC is higher against smiling genuine photos for both neutral and
smiling morphs (0.834 vs 0.758 for neutral morphs; 0.845 vs 0.775 for smiling morphs), i.e. the expression
reading is a genuine-side effect, present even where morph expressions are balanced. Other releases: see
`c1b_summary.txt`.

## (c) Rank changes (27 rows: 9 releases + 18 recipe-checkpoint seed means), 11 imbalanced cells

| Cell | Kendall τ (all vs neutral-only) | rows that move | pairs that flip | release pairs flipped with both gap intervals excluding 0 |
|---|---|---|---|---|
| FRLL-Morphs amsl | 0.954 | 10 | 8 | ViT-L/14 release vs FE ViT-B/16 release |
| FRLL-Morphs facemorpher | 0.964 | 7 | 6 | none |
| FRLL-Morphs opencv | 0.976 | 10 | 4 | none |
| FRLL-Morphs stylegan | 0.833 | 15 | 29 | none |
| FRLL-Morphs webmorph | 0.949 | 12 | 9 | none |
| DiM-A | 0.930 | 15 | 12 | none |
| DiM-C | 0.937 | 7 | 11 | none |
| Fast-DiM | 0.901 | 16 | 17 | none |
| Fast-DiM-ODE | 0.914 | 18 | 15 | none |
| Greedy-DiM | 0.874 | 12 | 22 | none |
| Greedy-DiM-S | 0.943 | 13 | 10 | none |

Rank (1 = lowest EER) all → neutral-only for selected rows:

| Row | amsl | facem. | opencv | stylegan | webm. | dim_a | dim_c | fast | fast_ode | greedy | greedy_s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MADation ViT-B/16 release | 8→7 | 7→7 | 7→7 | 9→8 | 4→5 | 11→12 | 5→4 | 4→6 | 10→11 | 24→24 | 6→9 |
| MADation ViT-L/14 release | 9→11 | 4→4 | 5→6 | 27→27 | 5→6 | 12→13 | 9→13 | 10→13 | 6→9 | 3→4 | 10→10 |
| SelfMAD release, own prep. | 2→1 | 2→2 | 1→1 | 3→2 | 6→3 | 2→1 | 2→2 | 3→2 | 4→2 | 1→1 | 1→1 |
| M3 last (seed mean) | 3→3 | 6→6 | 6→5 | 13→18 | 2→2 | 1→2 | 1→1 | 1→1 | 2→1 | 14→20 | 2→2 |
| M3L last (seed mean) | 1→2 | 1→1 | 4→4 | 18→26 | 1→1 | 5→8 | 13→16 | 13→16 | 5→8 | 6→10 | 20→22 |

Release-pair order changes whose gap change has a 95% interval excluding 0 (the two single-condition gap
intervals do not both exclude 0, except the AMSL pair in the table):

- FRLL-Morphs WebMorph: MADation ViT-B/16 and ViT-L/14 releases are ahead of SelfMAD (own preprocessing)
  with all genuine photos (gaps −1.0, −0.9) and behind it with neutral-only (+2.3, +3.2); change CIs
  [+1.1, +6.4] and [+1.4, +7.2].
- AMSL, DiM-A, DiM-C, Fast-DiM, Fast-DiM-ODE: ViT-L/14 release moves from ahead of to behind the FE
  ViT-B/16 release (e.g. DiM-C gap −12.7 → +2.0, change CI [+9.6, +19.2]) and, in AMSL, DiM-C and
  Fast-DiM-ODE, behind FE ViT-L/14 as well.
- Among recipe rows, M3L last falls from rank 18 to 26 on FRLL-Morphs StyleGAN and by 2–4 places on
  all six DiM cells; M3 last falls 13 → 18 (StyleGAN) and 14 → 20 (Greedy-DiM).

Full flip lists: `c1b_read.json` → `ranks`.

## Probe validation (step 3)

The C1 probe unchanged (lower-face 22 × 36 grey thumbnail of the eye-aligned frame, logistic regression
fit on the 204 FRLL genuine frames; features imported from `src/C_cue_checks/c_checks.py`). Applied to
aligned morphs whose expression is in the file name (every pair is 03/03 or 08/08). Threshold p = 0.5;
Clopper–Pearson intervals; AUC interval by image bootstrap.

| Family (corrected MAD22 aligned frames; MorDIFF eval frames) | n (smiling) | accuracy [95%] | sensitivity | specificity | AUC |
|---|---|---|---|---|---|
| MAD22c FaceMorpher | 1000 (500) | 0.931 [0.913, 0.946] | 0.878 [0.846, 0.905] | 0.984 [0.969, 0.993] | 0.977 [0.969, 0.985] |
| MAD22c MIPGAN-I | 1000 (500) | **0.811 [0.785, 0.835]** | **0.642 [0.598, 0.684]** | 0.980 [0.964, 0.990] | 0.969 [0.959, 0.977] |
| MAD22c MIPGAN-II | 999 (499) | 0.886 [0.865, 0.905] | 0.820 [0.783, 0.852] | 0.952 [0.929, 0.969] | 0.961 [0.950, 0.970] |
| MAD22c OpenCV | 984 (495) | 0.978 [0.966, 0.986] | 0.974 [0.956, 0.986] | 0.982 [0.965, 0.992] | 0.997 [0.996, 0.999] |
| MAD22c Webmorph (all neutral) | 500 (0) | 0.978 [0.961, 0.989] | – | 0.978 [0.961, 0.989] | – |
| MorDIFF | 1000 (500) | 0.942 [0.926, 0.956] | 0.900 [0.870, 0.925] | 0.984 [0.969, 0.993] | 0.985 [0.977, 0.991] |

The probe ranks smiling above neutral morphs well everywhere (AUC 0.96–1.00) and rarely calls a neutral
morph smiling (specificity 0.95–0.98), but at p = 0.5 it misses a third of the smiling MIPGAN-I morphs
(GAN morphs soften the smile). Misclassification-corrected smiling share (Rogan–Gladen; references
pooled per type: landmark = MAD22c FaceMorpher + OpenCV + Webmorph, sensitivity 0.926, specificity
0.981; MIPGAN = I + II, 0.731 / 0.966; MorDIFF 0.900 / 0.984; bootstrap B = 10,000):

| Target family | flagged smile-like [95%] | reference | corrected smiling share [95%] | neutral-only (pre-registered: UB ≤ 10%) |
|---|---|---|---|---|
| FRLL-Morphs AMSL | 0.010 [0.006, 0.015] | landmark | 0.000 [0.000, 0.000] | supported |
| FRLL-Morphs FaceMorpher | 0.011 [0.006, 0.018] | landmark | 0.000 [0.000, 0.001] | supported |
| FRLL-Morphs OpenCV | 0.011 [0.006, 0.019] | landmark | 0.000 [0.000, 0.002] | supported |
| FRLL-Morphs WebMorph | 0.015 [0.009, 0.023] | landmark | 0.000 [0.000, 0.006] | supported |
| FRLL-Morphs StyleGAN | 0.069 [0.055, 0.084] | MIPGAN | 0.050 [0.025, 0.075] | supported |
| DiM ×6 (neutral by README) | 0.026–0.068 | MorDIFF | 0.011–0.059 (UB 0.032–0.087) | (control) |

The DiM families are neutral-only by their README, yet the correction leaves 1–6% "smiling" there: that
is the size of the correction's bias on generator morphs. The StyleGAN family's 5.0% sits in the same
range, so it is consistent with neutral-only, but a small smiling share in that family cannot be
excluded by the probe alone.

Documentary support for FRLL-Morphs (all checked in this session):

- `/mnt/t7/Datasety/downloads/FRLL-Morphs/facelab_london/preprocess.py`: the AMSL morphs it renames
  are named like `001_03_002_03_alpha0.5_combined_morph_q33.jpg` → `001_002.jpg` (both contributors
  `_03`, neutral). The rename keeps only the two person IDs, so the set as distributed cannot hold both a
  03 and an 08 morph of the same ordered pair (2,175 `PPP_QQQ` files on disk). Only one example name is
  given, so this shows the naming, not that every source file was `_03`.
- The dataset's `README.txt` and the paper (Sarkar, Korshunov, Colbois, Marcel, arXiv 2012.05344v1,
  "Vulnerability analysis of face morphing attacks from landmarks and generative adversarial networks",
  **web check done, pages 1–5 read**): "For FRLL dataset, we follow the protocols used in AMSL Face Morph
  Image dataset by Neubert et al. ... Using these protocols (essentially, which facial image pairs to
  morph), we generated morphs with the following morphing tools: OpenCV, FaceMorpher, WebMorph, and
  StyleGAN 2"; WebMorph "requires 189 landmarks that are available only in FRLL"; Fig. 2 shows neutral
  contributors and neutral morphs. The paper does not state the expression in words; it also notes that
  StyleGAN 2 "is equally easy to generate high-quality morphs for smiling expressions", without saying
  any were made.
- The FRLL distribution ships WebMorph landmark templates (`.tem`) for `neutral_front` only (102 of 102;
  0 of 102 for `smiling_front`, checked in `frll_base/extracted`); `preprocess.py` deletes `.tem` files
  from `raw/neutral` only.
- The FRLL-Morphs protocols (`protocols/*/for_models.lst`, `for_probes.lst`) use `raw/neutral/NNN_03`
  as enrolment references and `raw/smiling/NNN_08` as genuine probes; morphs are compared against the
  neutral references.
- The AMSL dataset's own description was not checked (web page not opened).

Reading: neutral-only status of the five FRLL-Morphs families is supported by the probe (pre-registered
rule met in 5 of 5) and by file names in the AMSL source, the per-pair uniqueness, the neutral-only
landmark templates and the paper's figure; no document states it in words.

## Cue-matrix reading (pre-registered rule) and proposed edit (not applied)

Rule: "uses expression" if AUC_wp ≥ 0.65 with lower bound > 0.5 and the neutral-only − all EER difference
has a lower bound > 0 in ≥ 6 of the 11 imbalanced cells; "not used" if AUC_wp folded around 0.5 is < 0.60
with upper bound < 0.65; otherwise undetermined.

| Detector | Reading |
|---|---|
| MADation ViT-L/14 release (post hoc) | **uses** (0.990; 9/11 cells) |
| M3L last (pre-registered) | **uses**, 5 of 5 seeds |
| M3L es (post hoc) | uses 1, undetermined 4 |
| M3 es (post hoc) | uses 5, undetermined 3 |
| M3 last (pre-registered) | undetermined 8 of 8 (expression read, EER moved in ≤ 2 cells per network) |
| MADation ViT-B/16 release | undetermined (0.578 [0.480, 0.676]; 0/11) |
| MADation FE ViT-B/16 release | undetermined by the rule; reads expression **against** the cue (0.088; EER *lower* with neutral-only by 9.4 points, upper bound < 0 in 11/11) |
| MADation FE ViT-L/14 release; SelfMAD our pipeline | undetermined (0.343; 0.314: mildly reversed) |
| MADation FS ViT-B/16, FS ViT-L/14; SelfMAD own preprocessing; MixFaceNet-MAD (desc.) | **not used** |
| CNN recipes (M1, M2, M4, M5, M6, M8, M8O), both checkpoints | not used or undetermined; no network "uses" |

Reading caveat (stated in the pre-registration): restricting the genuine class is a matched comparison
(same person, session, camera and file pipeline; only the expression differs), not an image
intervention. The cue-matrix definition of USED asks for an intervention; the lead decides whether this
matched comparison qualifies.

**Proposed edit to `08_CUE_MATRIX.md`, row 15** (split as C1 proposed; C1's own "In the files?" text kept,
with "11 of 17" corrected to "12 of 17"):

- **15a Expression, imbalanced cells (DiM ×6, FRLL-Morphs ×5, MAD22 Webmorph).** "Does a detector use
  it?" → "Yes for CLIP-based MADation networks (matched comparison: genuine class restricted to the
  neutral photo of each of the 102 persons, C1b). MADation ViT-L/14 release: neutral photo scored above
  the smiling one in 101 of 102 persons (AUC_wp 0.990); neutral-only genuine raises its EER by 4.5 points
  on average over 11 cells (AMSL 17.7 → 24.5; FRLL-Morphs StyleGAN 52.4 → 65.7; DiM-A 22.0 → 27.4), lower
  bound > 0 in 9 of 11 (post hoc). M3L recipe, last checkpoint: 5 of 5 seeds, AUC_wp 1.00, EER +6.9 on
  average (pre-registered H1, not falsified). M3 recipe reads expression (AUC_wp 0.67–0.97) with small EER
  effects (+1.0). MADation ViT-B/16 release: +0.6, no cell significant. Opposite direction: MADation FE
  ViT-B/16 release (AUC_wp 0.09; neutral-only lowers EER by 9.4). Not used: SelfMAD release (own
  preprocessing), MADation FS releases, CNN recipes. MAD22 Webmorph not tested (no corrected-MAD22
  scores)". Status **PRESENT, USE UNTESTED → USED (MADation ViT-L/14 release, M3L recipe; matched
  comparison)**, with "NOT USED (SelfMAD release, MADation FS releases, CNN recipes)" in the evidence
  column.
- **15b Expression, balanced cells (MAD22 FaceMorpher, MIPGAN-I, MIPGAN-II, OpenCV; MorDIFF).** Status
  **ABSENT** as C1 proposed; add "genuine-side expression reading still present (ViT-L/14 release on
  MorDIFF: AUC higher against smiling genuine photos for both morph expressions), but the cell is balanced
  so it cannot bias the benchmark number".
- Status summary: move 15a from UNKNOWN to USED, 15b to ABSENT.

## What could not be verified

- Corrected MAD22 (5 cells, including the imbalanced Webmorph cell): no scores exist; not tested.
- MixFaceNet-MAD release is scored only on our frames (its own MTCNN crop branch is suspended); its
  rankings are reversed on four cells, so its rows are descriptive.
- Whether the 03/08 difference is purely expression: same person, session, camera and file format, but
  small pose or lighting differences between the two photos cannot be separated here.
- Why the es checkpoints of M3/M3L reverse on MorDIFF's crop (0.08–0.34) but not on the FRLL eval frames:
  not examined.
- The es checkpoint rule and training length of the M3 networks were not read (the es metadata may hold
  validation scores, which are off limits); H2's "training length" is therefore only "es vs last".
- MADation release training epoch and whether its expression reading comes from pretraining or SMDD
  fine-tuning: not tested.
