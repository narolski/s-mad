# FZ2 Frozen read of the new diffusion ladder: result

Status 12 Nov 2026, 03:30 CET: **done** (qualified after the independent review `experiments/reviews/REVIEW_FZ2_AR1A10_20261112.md`,
12 Nov). Registered readings (add-on, all 8 shards): H-new-1 not decided, H-new-2 not decided, H-new-3 falsified (SMDD
head and release head), H-new-4 falsified for pixel disagreement d. Post hoc: the X-vs-SAME direction marks same-person
mixes (sharper, correlated noise maps); two-person mixes sit with reconstructions along it. Paper sentence:
"render-path separability, one generator", not "frozen features read mixing".
Registration `prereg.md` (20:32, before any DG1 feature), full record `README.md`.

## Production set B: cross-platform reproducibility check (`read_prod.json`; per image `/mnt/t7/smad_next/FZ2/read_prod_items.csv`)

Production set B: the same 536 hosts and pairs re-rendered with the same deterministic sampler; its agreement with the
add-on is a cross-platform reproducibility check (Athena A100 vs RTX 3090), not an independent replication (review F1:
536 of 536 matched per rung; 470 of 536 Athena and 0 of 1,608 rented PNGs byte-identical; head, P_XS and Laplacian Spearman ≥ 0.9997 (`../DG1_diffusion-generation-athena/platform_reproducibility_fz2.json`); largest head-score
difference 0.055). Its numbers below equal the add-on's by construction.

536 hosts (FRGC 427, colorFERET 109), 20 steps; REC, MIR, SAME, X 536 each; two-person dose α 0.1–0.4, 100 hosts each.
Features on the DGX (deviation, `prereg.md`); probes out of fold with whole partner cycles held out; two-way person
bootstrap, B = 10,000. AUC: positive = first named.

**Frozen SMDD heads and the release head, no refit (H-new-3 contrasts; no FRESH rung in this run):**

| | head s401 | heads s402–s405 | released FE ViT-L/14 head |
|---|---|---|---|
| X20 vs SAME20 | 0.662 [0.622, 0.699] | 0.660–0.661 | 0.665 [0.625, 0.703] |
| best baseline for X20 vs SAME20 | thumb32 0.700 [0.656, 0.741] | | thumb32 0.700 |
| excess over the best baseline | −0.038 [−0.094, +0.019] | | −0.035 [−0.089, +0.023] |
| SAME20 vs REC20 | 0.378 [0.356, 0.401] | | 0.396 [0.374, 0.417] |
| X20 vs REC20 | 0.537 [0.496, 0.578] | | 0.561 [0.518, 0.604] |
| MIR20 vs REC20 | 0.702 [0.681, 0.723] | | 0.722 [0.702, 0.742] |

X20 vs SAME20 without flagged items 0.662 [0.619, 0.702]; FRGC 0.664, colorFERET 0.683. The five baselines for X20 vs
SAME20: PNG bytes 0.603 (X lower), Laplacian variance 0.695 (X lower), asymmetry 0.631 (X lower), thumb32 0.700,
surround-only thumbnail 0.669. (H-new-3's falsifier, applied here descriptively, would fire: the excess interval
includes 0.)

**Probes (clip_mad; dinov2 in brackets):**
- Shared direction D_SR (trained SAME20 vs REC20, 0.999 [0.998]): X20 vs REC20 0.987 [0.985], MIR20 vs REC20 0.994
  [0.980], and it ranks SAME20 above X20 (X20 vs SAME20 0.162 [0.183]).
- Probe X20 vs REC20 0.995 (excess over thumb32 +0.19); MIR20 vs REC20 1.000.
- **P_XS (trained X20 vs SAME20): 0.941 [0.923, 0.957] (0.953).** Stratified by input-pair disagreement d (pooled
  fifths): 0.933 [0.911, 0.952], Δ = +0.008 [+0.001, +0.017]; X against the top-fifth-d SAME images 0.912 [0.874, 0.945]
  (108 images). Within-stratum AUCs 0.97, 0.93, 0.94, 0.94, 0.88. Median d: X 29.1, SAME 22.5 grey levels. Spearman of
  the score with d: −0.03 inside X, +0.16 inside SAME. (H-new-4's falsifier, applied descriptively: Δ ≤ 0.05.)
- P_XS scores by rung (mean decision value): SAME −2.81, MIR −0.64, REC +2.21, X +2.17, two-person dose α 0.1 / 0.2 /
  0.3 / 0.4: +2.37 / +2.46 / +2.52 / +2.42 (dose vs SAME 0.96 at every α; dose vs REC 0.52–0.55). Dinov2 the same
  pattern. So in this run the P_XS direction separates the same-person mix from every other rung, including the
  reconstruction and the 10% two-person dose.

## Primary read (DG1 add-on, all 8 shards; registered readings) — `read_addon.json`

536 hosts; 9,544 images (shards 0–1 Athena, 2–7 rented RTX 3090; `platform` column in
`/mnt/t7/smad_next/FZ2/read_addon_items.csv`). DGX features (deviation in `prereg.md`); partner-cycle folds; two-way
person bootstrap, B = 10,000. clip_mad decides; dinov2 in brackets.

| Hypothesis | Registered numbers | Reading |
|---|---|---|
| H-new-1 | D_SR (SAME20 vs REC20, 0.998) applied to FRESH1_20 vs REC20: 0.664 [0.643, 0.686] (0.823); probe SAME20 vs FRESH1_20: 0.999 [0.997, 1.000] (0.999) | **not decided** (neither branch met); on clip_mad very close to the falsified branch (transfer misses 0.65 by 0.014, its upper bound meets 0.70, the probe condition is met), with dinov2 transfer at 0.82 |
| H-new-2 | probe NOISES20 vs REC20 0.997 [0.995, 0.999] (0.996); SEMS20 vs REC20 0.902 [0.886, 0.918] (0.972); along D_SR NOISES − SEMS +0.166 [+0.147, +0.184] (+0.136) | **not decided** (SEMS above 0.85; falsifier SEMS ≥ NOISES not met). The noise map carries more than the semantic code in clip_mad (+0.166 along D_SR), but semantic-only mixes are separable too (0.902; dinov2 0.972); specific to clip_mad |
| H-new-3 | head s401 X20 vs SAME20 0.662 [0.622, 0.700]; SAME20 vs FRESH1_20 0.572 [0.545, 0.598]; best baseline thumb32 0.700; excess −0.038 [−0.094, +0.020] | **falsified** (excess interval includes 0). Release head: 0.665, 0.583, excess −0.035 [−0.089, +0.023], **falsified**. The ordering is real (lower bound 0.622) but a 32×32 thumbnail matches it; the heads score SAME as more bona fide than REC (0.379; FZ1 on FRLL frames: 0.51) |
| H-new-4 | P_XS (X20 vs SAME20) A0 0.941 [0.923, 0.958] (0.953); stratified by d A_s 0.933 [0.912, 0.952]; Δ +0.008 [+0.001, +0.016]; A_hi 0.913 [0.875, 0.945] | **falsified for pixel-level input disagreement d** (Δ +0.008). Post hoc (review F2): the angle θ between the two inverted noise maps separates X from SAME by itself (0.916), and stratifying on it lowers P_XS to about 0.88; the direction may partly read noise-map similarity of the input pair (amendment 1 below) |

Sensitivity (unflagged / FRGC / colorFERET / Athena / rented). The platform rows repeat the database rows (review F4:
Athena = 109 colorFERET + 25 FRGC hosts, 38% flagged; rented = 402 FRGC hosts, 4% flagged; 1 of 88 partner cycles spans
both); within FRGC, P_XS is 0.938 on Athena (25 hosts) vs 0.951 rented.
- H-new-1 transfer FRESH1 vs REC: 0.670 / 0.668 / 0.702 / 0.669 / 0.675; probe SAME vs FRESH1 0.996–0.999 in every row.
- H-new-2 probes: NOISES vs REC 0.990–0.998; SEMS vs REC 0.891–0.908.
- H-new-3 head s401: 0.662 / 0.664 / 0.683 / 0.662 [0.578, 0.744] / 0.668 [0.622, 0.711]; release 0.667 / 0.681 / 0.682 /
  0.651 / 0.685.
- H-new-4 A0: 0.946 / 0.950 / 0.903 / 0.906 / 0.951.

Descriptive (clip_mad):
- Heads s401: FRESH1 vs REC 0.305, SAME vs REC 0.379, X vs REC 0.538, MIR vs REC 0.702; 100 steps X vs SAME 0.650, SAME vs
  FRESH1 0.529; NOISEX vs NOISES 0.606, SEMX vs SEMS 0.567. Five baselines for X20 vs SAME20: PNG 0.603, Laplacian 0.695,
  asymmetry 0.631, thumb32 0.700, surround 0.669.
- Excesses below are over the best of five baselines, none high-frequency (thumb32 is low-pass; review F5), so they do
  not mean "beyond simple statistics". Seed and writer are ruled out (FRESH1 vs FRESH2 0.518; one `save_image` for all
  rungs); what the probes read is which noise map was decoded.
- Trained probes: FRESH1 vs REC 0.976 (excess over thumb32 +0.05), FRESH1 vs FRESH2 0.518, X vs FRESH1 0.997, NOISES vs
  SEMS 0.979, SEMS vs REC 0.902 (excess +0.30), 100 steps SAME vs REC 0.999, FRESH1 vs REC 0.990, X vs SAME 0.952; D_SR at
  100 steps on FRESH1 vs REC 0.617 (dinov2 0.844).
- D_SR on other rungs: X vs REC 0.987, X vs SAME 0.157, MIR vs REC 0.994, NOISES vs REC 0.997, SEMS 0.831, NOISEX 0.967,
  SEMX 0.895, FRESH2 vs REC 0.659.
- Laplacian (face box) against REC: NOISES 0.728, SEMS 0.554, NOISEX 0.571, SEMX 0.566, SAME 0.745, X 0.582, FRESH1 0.612.
- P_XS mean score: SAME −2.81, same-person dose α 0.1 / 0.2 / 0.3 / 0.4: +1.25 / −0.37 / −1.72 / −2.42; two-person dose
  +2.35 / +2.34 / +2.28 / +2.13; X +2.17; REC +2.23; FRESH1 +3.25; MIR −0.63. DOSEX vs DOSES per α: 0.673, 0.835,
  0.912, 0.931. Spearman score vs α·d: −0.03 (two-person), −0.30 (same-person). Median d: X 29.1, SAME 22.5.
- Reading (review F3): along P_XS, two-person mixes and every two-person dose sit with the reconstruction; what separates
  X from SAME is a property of the same-person mix (face-box sharpness medians REC 87, X 96, SAME 128, reviewer's check).

## Amendment 1 (post hoc in substance; registered in commit dbc151d before computing; reviewed in `experiments/reviews/REVIEW_PN1_BATCH2_FZ2A12_AR1A11_20261112.md`, F6) — `amend1.json`

Zero GPU, existing features; partner-cycle folds, two-way person bootstrap B = 10,000. Code `src/FZ2/fz2_amend1.py`.
Order note (review F6): the registration commits (dbc151d, c258935) precede the result commits, but the gaps are about
60 s, so the order of computation cannot be proved from timestamps.

- **(i) H-A transfer: supported.** P_XS (clip_mad) on NOISEX vs NOISES 0.907 [0.884, 0.928] (dinov2 0.932); SEMX vs SEMS
  0.579 [0.538, 0.620] (0.553). Mean P_XS scores: NOISES −2.85 (like SAME −2.81), NOISEX +1.46, SEMS +2.09, SEMX +2.61, REC
  +2.23, X +2.17. So the same-person signature travels with the slerped noise map, not with the semantic code. D_SR: NOISEX
  vs NOISES 0.146, SEMX vs SEMS 0.608.
- θ alone, X vs SAME: 0.916 [0.895, 0.935] (median X 1.564, SAME 1.537 rad). P_XS stratified by θ fifths: 0.941 → 0.876
  [0.835, 0.913], Δ +0.065 [+0.038, +0.096] (4 usable strata; X/SAME counts 0/215, 17/197, 145/69, 186/28, 188/27). By
  Laplacian fifths: 0.929 [0.906, 0.949], Δ +0.013 [+0.006, +0.021]. Spearman of P_XS with θ: +0.50 inside SAME, 0.00
  inside X; with Laplacian −0.33 inside SAME, +0.01 inside X. θ vs Laplacian: −0.40 (SAME), −0.34 (NOISES), +0.09 (X,
  NOISEX), −0.10 (SEMS).
- **(ii) H-B: falsified** (residual-12 floor ≤ 0.85 on both): NOISES vs REC 0.810 [0.791, 0.829], FRESH1 vs REC 0.827
  [0.805, 0.849]. Floors (best of single / residual-12 / simple-10 / combined-22) and clip_mad probe excess over them:
  NOISES vs REC floor 0.857, excess +0.140 [+0.122, +0.158]; FRESH1 vs REC 0.827, +0.149; SAME vs REC 0.868, +0.13; X vs
  SAME 0.798, +0.143 [+0.112, +0.176]; SEMS vs REC 0.654, +0.248; X vs REC 0.749, +0.246; FRESH1 vs FRESH2 0.516, +0.001;
  100 steps: SAME vs REC 0.983, +0.016; FRESH1 vs REC 0.888, +0.101; X vs SAME 0.831, +0.121. dinov2 excesses alike. So the
  frozen features read the render path beyond these 22 residual and simple statistics. Head s401 on X vs SAME is below
  the floor (−0.137 [−0.185, −0.088]).
- **(iii) H-C on FZ1's A43 frames: supported** (registered ≤ 0.62): head s401 B20 vs C20 0.621 → 0.569 [0.455, 0.684]
  stratified by centre-256 Laplacian fifths (within-stratum 0.720, 0.463, 0.737, 0.516, 0.479; B20/C20 counts 50/11,
  47/13, 49/11, 38/22, 16/45; thin strata). "Supported" rests on the point estimate only: 0.569 [0.455, 0.684], and the
  interval includes the falsifier 0.65.
- **(iv) P_XS from DG1 on A43 frames** (other persons, 512 frames): B20 vs C20 0.878, B vs C 0.901, C20 vs D20 0.053, B20
  vs D20 0.304, B vs D 0.388 (dinov2 0.930, 0.926, 0.020, 0.241, 0.325). The DG1 direction transfers to FRLL and again
  marks the same-person mix (it scores reconstructions above both mixes).

## Amendment 2 (post hoc in substance; registered in commit c258935 before computing; reviewed in `experiments/reviews/REVIEW_PN1_BATCH2_FZ2A12_AR1A11_20261112.md`, F6) — `amend2.json`

Saved noise maps of add-on shards 2–6 (335 hosts; shards 0–1 codes on Athena, shard 7's lost). Code `src/FZ2/fz2_amend2.py`.

- Medians, same-person pair (a, b) vs other-person pair (a, p): θ 1.536 vs 1.564 rad; band cosines (lowest to highest)
  0.400 / 0.172 / 0.058 / 0.021 vs 0.167 / 0.029 / 0.006 / 0.005; 8×8 low-pass cosine 0.224 vs 0.056.
- Separation of X from SAME (two-way person bootstrap): θ 0.918 [0.894, 0.942] (0.916 on all 536); lowest-band cosine c0
  0.971 [0.957, 0.983]; band 2 0.985 [0.975, 0.994]; low-pass 0.985 [0.975, 0.993]; band 3 0.918; band 4 0.827.
- Within SAME, Spearman with face-box Laplacian L: c0 +0.095 [−0.016, +0.206]; band 2 +0.343 [+0.241, +0.437]; band 3
  +0.440 [+0.347, +0.525]; band 4 +0.414 [+0.318, +0.503]; low-pass +0.231 [+0.125, +0.331]; θ −0.424 [−0.513, −0.327].
  With P_XS: c0 −0.239, bands 2–4 −0.50 / −0.52 / −0.41, θ +0.486. Within X every correlation is within ±0.08 (intervals
  include 0).
- Joint model within SAME (ranks): R² of L on c0 0.009; adding θ raises it to 0.192, ΔR² +0.183 [+0.110, +0.267].
- **Registered reading: falsified as registered for the lowest-band version (c0, 0.3% of the noise power; ρ +0.095
  [−0.016, 0.206]). Post hoc: θ is the power-weighted mean of the band cosines, and shared structure in the mid and high
  bands tracks sharpness within SAME (ρ 0.34–0.44). Coherent-noise sharpening in general is not falsified (descriptive).**
  (Wording from the review, F6; the identity check is in amendment 3.)

## Amendment 3 (HN10 mediation; registered in commit 3c7fbbd before computing; post hoc in substance) — `amend3.json`

Same 335 hosts as amendment 2. Code `src/FZ2/fz2_amend3.py`.

- Identity check: cos(a, b) equals the power-weighted sum of the four band cosines (Pearson 1.000000, largest difference
  2.3e-15 over 335 hosts; the weights sum to 0.99987 because the outermost corner frequencies are not in a band). Band
  power shares (median): 0.30% / 4.3% / 18.8% / 76.6% (reviewer: 0.3 / 4 / 18 / 77% on 67 hosts).
- Within SAME: partial Spearman of θ with L given c1, c2, c3: +0.177 [+0.038, +0.322]; partial of c2 with L given θ: +0.139
  [+0.041, +0.243].
- **Registered reading, HN10: falsified** (θ keeps a partial correlation with sharpness beyond the band cosines, interval
  excludes 0; c2's partial correlation is below 0.20, upper bound above it). The mechanism is not resolved to a band.

**The diffusion mechanism line stops here** (lead, 12 Nov). The paper carries one sentence: render-path separability, one
generator.

## Compute

Athena: job 3545969 submitted 20:39, cancelled 21:31 before it started (0 GPU-hours). DGX GB10: production features
about 10 min (both backbones). Add-on features: DGX, all 8 shards, done 03:10.
