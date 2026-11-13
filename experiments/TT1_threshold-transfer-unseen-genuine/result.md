# Threshold transfer on unseen genuine sources (TT1): result (registered reading; reviewed 13 Nov, corrections applied)

Status: the 11 networks that passed the platform gate were scored on lease tt1c (A100-SXM4 80 GB, torch 2.2.1); the
registered reader was run (cf963d1). Independent review `experiments/reviews/REVIEW_TT1_20261113.md` (21ed1d1): numbers
reproduce exactly, conclusions need qualification; its text corrections are applied below. Post hoc numbers requested
by the review (F1-F8) are in `posthoc_review.json` (`src/TT1/posthoc_review.py`), labelled post hoc.

Registration and deviations:
- TT1-S `prereg_scoring.md` (01557ce); pins at ccd6319 and 4f1ce82.
- TT1-D1 (8bf5e12), TT1-D2 (4454f3f), TT1-D3 (38999cc). TT1-D3 was written after seeing the tt1b gate.
- Reader re-pin 52e64f6.

Files:
- `tt1_read.json` (sha256 `9ac3a0b8…`), tables in `tt1_read_tables.md` (`2cf5899e…`).
- Gates: `gate_a100_tt1c.json`; earlier failed gates `gate_dgx_run2.json`, `gate_a100.json`, `gate_a100_tt1b.json`.
- Scores: `/mnt/t7/smad_next/TT1/results/TT1_A100_tt1c_full.tar`.
- Pool counts: `pools_summary.md`.

This is a false-alarm test only: there are no morphs of these sources, and none of these sources is a benchmark.
"Flag" means logit > 0, the network's own rule.

## Platform gate

| Lease or machine | Gate result |
|---|---|
| DGX (GB10, torch 2.12) | failed, all 12 networks |
| tt1a | failed: FFHQ rows differed at the last bit, from batch composition |
| tt1b | failed in Bn_s401 only |
| tt1c | passed for the 11 non-excluded networks |

Detail for tt1c:
- FFHQ rows are byte-identical in all 12 networks (0 of 3,000 rows differ).
- Camera photos: 0 decision changes, Kendall 0.996-0.998.
- Bn_s401 repeats its tt1b miss exactly (one camera row, |Δ| 0.035). It is excluded under TT1-D3, and every read
  that needs it is "not available (failed platform gate)". Bn_s402 is printed alone ("one seed").
- tt1c reproduced tt1b's gate numbers to every printed digit.

## Registered verdicts (seeds 401/402, two machines)

### TT-H1: does the own rule transfer to unseen sources?

A family "fails" if the lower bound of its person-bootstrap interval is above 5%.

| Arm | Families failing (both seeds) | Registered verdict |
|---|---|---|
| A | lfw_calfw and agedb_30 on both seeds; prediction was ≥ 4 of 7 | not supported as predicted |
| B | none | falsified: on both seeds every family's own-rule share has upper bound ≤ 10% (points 0.0-4.9%; also ≤ 8.3% by Clopper-Pearson). False alarms only, on black-bordered 1.7-3.5x frames; the same networks flag 17.8% / 6.4% of FFHQ genuine photos |
| Sb | cfp_ff and agedb_30 | supported narrowly (AgeDB lower bounds 0.051 / 0.053 against 0.05) |
| Bv | none | falsified (printed arm) |
| C | 4 on seed 401, 0 on seed 402 | printed |

The R_cam own-rule share is 0 for every network except C_s401 (0.5%), so TT-H1 is informative for every network.

Limits of B's verdict (review F4): it does not show that scores are unchanged (ranks shift completely; TT-H2), that
τ_cam transfers (99-100% flagged), that attacks from these sources are caught (no morphs), or that the rule transfers
to sharp sources (B_s401 flags 17.8% of FFHQ genuine photos, which would fail TT-H1's own 10% bar). A possible trade
against misses is invisible to TT1 (tested on development attack pools in H-new-4).

### TT-H2: do unseen photos sit above the training-source photos?

Supported for all 11 networks. AUC of each unseen source against R_cam is 0.987-1.000 in all 8 sources. No read is
floor-tied: R_cam sits about 0.15 logit above the head floor of about −3.83, and its share within 0.05 of the floor
is 0. R_cam spans 0.05-0.15 logit (5th-95th percentile); unseen medians sit 0.3-0.8 logit (A, B) and 1.0-1.7 (Sb)
above it, about 3 logits below the rule for B. The AUC measures displacement, not closeness to the threshold.

### TT-H3: is the border material?

Inconclusive for all 11 networks:
- The border alone shifts camera photos by +0.04 to +0.10 logit (paired median; CFP-sized borders +0.21 to +0.38),
  about 10-20% of the unseen excess except CFP-FF. R3(e) is high because R_cam is tight. On FFHQ the shift is mixed
  in sign.
- Matching the border lowers the unseen-vs-camera AUC by 0.004-0.41. The largest drop is CFP-FF (0.12-0.41); the
  smallest are CASIA-FASD and the packs other than CFP (0.01-0.05).
- The FFHQ border read R3(d) is 0.49-0.62, below the 0.65 required.

### TT-H4: do softer photos score higher at fixed size?

- A: not supported as predicted. ρ ≤ −0.15 in 2 of 4 packs on both seeds: LFW −0.41/−0.45, AgeDB −0.34/−0.37;
  CALFW and CFP −0.09 to −0.15.
- B and Sb: supported (|ρ| below A's in ≥ 3 of 4 packs on both seeds).

### TT-H5: does the source matter beyond crop geometry, enlargement and border?

The registered verdict is "source matters beyond geometry" for A, B, Sb (and the printed arms C, Bv). The geometry
reference is not weak: R3(f) is 0.81-0.97 at the 224 px geometry and 0.88-1.00 at 112 px.

What the verdict rests on, stated plainly:
- In the 224 px group (the four anti-spoofing sets), every network places the unseen frames above the
  geometry-matched camera photos (R3(g) 0.91-1.00).
- In the 112 px group (the four packs) the arms differ:
  - B, C and Bv: 0.95-0.98.
  - Sb: 0.87-0.92.
  - A: 0.16-0.41. Arm A scores the 112 px geometry-matched camera photos ABOVE the real 112 px pack photos.
- So for arm A at 112 px, crop geometry plus shrink-and-enlarge history accounts for more than the whole pack
  excess.
- Own-rule flags on camera photos after the 112 px path: A 46.0% / 56.6% (paired shift +2.85 / +5.37 logit); B, Bv,
  C, Bn 0.2-1.9%; Sb 7.7% / 3.4%. At 224 px: 0-1% for every arm. A's 'source matters' verdict rests on the four
  anti-spoofing sets only. (Post hoc, descriptive; recomputed by the owner, `posthoc_review.json`.)
- R4(c)/(d) are printed under the M5 labels and decide nothing. The variance share is unstable across seeds (B 0.03
  vs 0.69) and is not interpreted.

### TT-H6: arms (descriptive; no arm, seed or threshold is chosen from TT1)

| Pair | ΔF̄ seed 401 [interval] | ΔF̄ seed 402 [interval] | Registered sentence |
|---|---|---|---|
| B − A | −0.033 [−0.041, −0.027] | −0.035 [−0.040, −0.032] | "B has lower genuine flag rates than A on seeds 401/402" |
| Sb − A | −0.013 | −0.005 | not distinguished |
| Sb − B | +0.021 [0.013, 0.029] | +0.031 [0.028, 0.033] | not distinguished |

- Sb − B is positive on both seeds with intervals above 0. Sb flags more unseen genuine photos than B, but the
  registered rule only prints a "lower" sentence.
- Post hoc, descriptive: Sb − B rises to +0.055 / +0.082 above −1; Bv − B ≈ 0 at every cut-off.

  | Cut-off (logit) | Sb − B, s401 / s402 | Bv − B, s401 / s402 |
  |---|---|---|
  | 0 | +0.021 / +0.031 | −0.002 / −0.000 |
  | −0.5 | +0.030 / +0.047 | −0.001 / −0.000 |
  | −1 | +0.055 / +0.082 | −0.001 / −0.000 |
  | −2 | +0.325 / +0.341 | −0.003 / −0.000 |
- The intervals capture image sampling only, not training variance.

Per-network summary (F̄ = mean of the 7 family flag shares, F_max = largest family flag share):

| Network | F̄ | F_max |
|---|---|---|
| A_s401 | 0.057 | 0.151 |
| A_s402 | 0.038 | 0.122 |
| B_s401 | 0.024 | 0.034 |
| B_s402 | 0.002 | 0.009 |
| Sb_s401 | 0.045 | 0.112 |
| Sb_s402 | 0.033 | 0.100 |
| C_s401 | 0.117 | 0.180 |
| C_s402 | 0.019 | 0.063 |
| Bv_s401 | 0.022 | 0.033 |
| Bv_s402 | 0.002 | 0.009 |
| Bn_s402 (one seed) | 0.001 | 0.003 |

## Numbers anyone might quote

Own-rule flag shares, primary pool, person-bootstrap 95% interval (inflated for packs):

| Network | LFW | AgeDB | CFP-FF | OULU-NPU | FFHQ genuine (R_ffhq) |
|---|---|---|---|---|---|
| A_s401 | 23.5% [22.2, 24.8] | 9.9% | 4.0% | 0.1% | 22.5% |
| A_s402 | 18.7% | 8.3% | 4.3% | 0.0% | 9.9% |
| B_s401 | 4.9% | 3.2% | 3.0% | 1.1% | 17.8% |
| B_s402 | 0.2% | 0.4% | 0.9% | 0.0% | 6.4% |
| Sb_s401 | 1.4% | 6.6% | 11.2% | 7.7% | 5.9% |
| Sb_s402 | 2.9% | 6.9% | 10.0% | 2.0% | 7.0% |

- Camera photos (R_cam): 0% flagged for every network except C_s401 (0.5%).
- At τ_cam (the camera-photo threshold; label "saturated band"), 99-100% of every unseen source and 95-99% of FFHQ
  genuine photos are flagged, against 2.2-5.5% of R_cam.

## Seed spread

- B_s401 against B_s402: F̄ 0.024 against 0.002.
- C_s401 against C_s402: F̄ 0.117 against 0.019.
- The seed-to-seed spread of the same arm is as large as most arm differences.
- Seed = machine (seed 401 on pn1a, seed 402 on pn1b). Every arm sentence is a two-seed lead.

## Post-result amendments H-new-1, 2, 4, 5 (registered before computing: 5954c12, a714c17; `hnew.json`, `diag_kernels.json`)

All are post hoc to the TT1 reading; development data only.

- **H-new-2, onset of A's storage cue: FALSIFIED.** On the development ladder R0 and AF0 development photos (226 pairs),
  the stored 61.2 px copies (2.16x enlargement) shift A by a paired median +0.09 / +0.26 logit (B: 0.00 / −0.00), with
  12% / 19% of A's copies flagged (B 0.9% / 0.5%). The registered rule (A's 61 px shift > B's + 0.1 on both seeds)
  fails on seed 401. At 112.7 px (1.17x) every arm shifts by ≤ 0.01.
  - Together with TT1's geometry reference (3.5x: A +2.85 / +5.37, 46-57% flagged), A's large shift appears only
    beyond 2.16x on these data, or needs the crop geometry as well. The onset is not located.
  - The PN1 tier-1 test-ladder figure (+1.73 / +2.64) was a mean raw shift on other hosts.
- **H-new-1, missing high frequency: not falsified.**
  - Median face-box Laplacian variance: geometry-matched 112 px camera photos 7.3, pack photos 10.7. The geometry
    references are softer.
  - A scores them 2.26 / 4.91 logits above the packs.
  - Pooled OLS slope of A's logit on log face-box variance: −0.88 / −0.88.
  - Consistent with A reading missing high frequency. Measurement only; not causal.
- **H-new-4, trade between genuine flags and misses: "supported" by the registered rule, but driven by one arm.**
  Spearman ρ(F̄, development miss) = −0.63 over 10 networks (permutation p = 0.027). Development attack pools: ladder
  R4 582, AF0 u50 180, splice S4 291.
  - The ladder R4 and AF0 u50 misses are at the floor (0-0.6%) for every network. The miss mean is driven by the
    splice pool: Sb misses 25-26% of splices against 93-97% for A, B, C, Bv.
  - So the negative ρ is "Sb flags more genuine photos and misses fewer splices". It is not a B-against-A trade:
    B's development misses equal A's within 1 point (0.322-0.324 against 0.312-0.315).
- **H-new-5, GB10 kernels: FALSIFIED.** None of six settings brings the DGX within 1e-3 of the A100 on the five
  diagnostic rows (best 0.088): TF32 off/on and math-only attention, alone and combined. The DGX (GB10 / torch 2.12)
  cannot be a scoring fallback for comparisons with A100 scores. The source of the difference is not located; other
  network ops or library versions remain.

## Review findings and where they are applied

F1 AUC meaning (TT-H2 text); F2 storage result (TT-H5 text, post hoc); F3 border wording (TT-H3 text); F4 limits of
B (TT-H1 text); F5 Sb narrow (TT-H1 table); F6 seed = machine (Seed spread); F7 Sb − B cut-offs (TT-H6, post hoc); F8
reader correction (section below); F9 TT1-D3 accepted (gate section); F10 platform pins
(`PLATFORM_PINS_FOR_FINAL_READ.md`). What the paper may say (review Q6): "On about 21,000 genuine photos from eight
development sources unseen in training (small faces enlarged 1.7-3.5x, with a black border), the protocol-trained
network kept its fixed decision rule: at most 4.9% of any family flagged, on two seeds, against up to 23.5% for the
plain network. These photos are still clearly displaced from the training camera photos in score, so a threshold
calibrated on camera photos does not transfer (99-100% flagged)."

## What cannot be claimed

- Any miss rate or morph detection.
- A benchmark or generalisation statement.
- A cause of any source effect. Source is confounded with JPEG, sensor and capture.
- A separate effect of enlargement across geometry groups.
- Any arm choice. TT-H6 is descriptive. B is not shown to be the better arm overall.
- That the threshold transfers in general or to sharp sources; calibration.

Pack intervals use pseudo-identities, inflated by sqrt(components / people).

## Reader correction (review F8; labelled as a correction, verdicts unchanged)

The registered reader did not clip inflated lower bounds at 0 (AgeDB −0.001 for Bn_s402 and Bv_s402) and gives
zero-width bootstrap intervals for zero-event families. Correction: lower bounds are clipped at 0, and the exact
Clopper-Pearson interval is printed beside every zero-event family (`posthoc_review.json`, family_flag_corrected).
Re-check: TT-H1 failing-family lists and the "all upper ≤ 10%" test are identical after the clip for A, B, Sb, C, Bv
on both seeds (TT-H1_recheck_after_clip: unchanged = true for all). Largest Clopper-Pearson upper bound over families:
B 8.3% / 5.5%, Bv 8.3% / 5.5%, A 15.8% / 12.8%, Sb 12.2% / 10.9%, C 25.1% / 7.1%. CFP-FF and AgeDB people may overlap with
CASIA-WebFace celebrities (not checked).

## Spend

Rented A100 time:
- tt1a 0.56 USD;
- tt1b about 0.6 USD;
- tt1c about 0.9 USD (01:03 to the 01:46 release).

DGX GPU about 25 min. WCSS: nothing queued (uploaded files kept).
