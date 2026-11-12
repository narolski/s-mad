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

## Compute

Athena: job 3545969 submitted 20:39, cancelled 21:31 before it started (0 GPU-hours). DGX GB10: production features
about 10 min (both backbones). Add-on features: DGX, all 8 shards, done 03:10.
