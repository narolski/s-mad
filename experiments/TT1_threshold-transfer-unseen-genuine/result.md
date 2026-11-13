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

# Fresh-seed block TT1-FS (seeds 403-407) and extension TT1-X Part 1 (Sp): registered reading; reviewed (REVIEW_TT1_FS_20261113.md, 59c08bb: needs qualification), corrections applied

Registration TT1-FS: `prereg_fs1_block.md`. It was registered at a2fef5c, with the pre-run amendment at ab81b35 and
the operational note at 451c419. Reader `tt1_read_fs.py` 87356fd7…, run once.

Files:
- `tt1_read_fs.json` (sha256 `434208c6…`) and the tables in `tt1_read_fs_tables.md`.
- Scores: `/mnt/t7/smad_next/TT1/results/TT1_A100_pn1fs_fs.tar`.

Platform:
- Lease pn1fs: A100-PCIE-40GB, GPU-5bd20020…, driver 610.57.04, torch 2.2.1, CUDA 12.1, cuDNN 8902, timm 1.0.27,
  numpy 1.26.4, Pillow 10.2.0.
- The job took the fit lock at 10:08:28 CET.
- **Gate: 15 of 15 networks byte-identical** on all 19,797 FS1 evaluation rows (TF32 on, batch 64, manifest order),
  max |Δ| 0 for every network.
- TF32 split on R_cam (this job's logits (PyTorch defaults: matmul TF32 off, cuDNN TF32 on) against the stored TF32-on ones): max |Δ| 0.001-0.042 logit,
  0 own-rule changes in any network.

The F4 limits apply: false alarms only, on low-resolution black-bordered frames, development sources only. No arm,
seed or threshold is chosen from TT1.

## Registered verdicts (an arm verdict needs at least 4 of 5 seeds agreeing)

| Hypothesis | A | B | Sb |
|---|---|---|---|
| TT-H1: does the own rule transfer? | **mixed** (3 of 5 'transfers'); the prediction (at least 4 failing families) held on 0 of 5 seeds; s404 fails 2 families, s405 fails 1 | **transfers on 5 of 5 seeds**: every family's upper bound ≤ 10%, largest bootstrap bound 3.3% (exact Clopper-Pearson bound for zero-event MSU-MFSD 5.5% on every seed) | **transfers on 4 of 5 seeds**, so the prediction (at least 2 failing families) is falsified on fresh seeds (it held on 0 of 5). This reverses the narrow 401/402 'supported'. s404 fails 1 family (cfp_ff, 13.4%) |
| TT-H2: unseen photos above the training-source photos? | supported 5 of 5 | supported 5 of 5 | supported 5 of 5 |
| TT-H3: is the border material? | inconclusive 5 of 5 | inconclusive 5 of 5 | inconclusive 5 of 5 |
| TT-H4: softer photos score higher at fixed size? | **mixed**: "not as predicted" 3 of 5 | **'falsified' by the registered rule, 4 of 5** (ρ ≥ 0 in at least 3 packs): B shows no 'softer scores higher' effect. This agrees with B's own prediction; \|ρ\| is also below A's on 4 of 5 seeds. Not evidence against B | **mixed**: \|ρ\| below A's on 3 of 5 seeds; the mixed count comes from A being flat on s405/s406; Sb's \|ρ\| ≤ 0.154 everywhere |
| TT-H5: source matters beyond geometry? | "source matters beyond geometry" 5 of 5 | same, 5 of 5 | same, 5 of 5 |

Per-seed numbers behind the verdicts:
- **TT-H1, A:** largest family upper bounds per seed are 3.4%, 19.2%, 10.4%, 2.0% and 7.9%.
- **TT-H1, B:** this matches its registered falsifier, "own rule transfers on these sources", now on five seeds.
- **TT-H1, Sb:** under the registered rule the arm verdict is "transfers". The registered prediction was failure in at
  least 2 families per seed; it held on 0 of 5 seeds.
- **TT-H2:** AUC of every unseen source against R_cam is 0.989-1.000 for every network.
- **TT-H4, A:** ρ(logit, log sharpness) in LFW is −0.28 to −0.54 on every seed. In AgeDB it is −0.29 to −0.40 on four
  seeds and 0.00 on s406. In CALFW and CFP it is −0.18 to +0.12.
- **TT-H4, B:** ρ is −0.13 to +0.22.

### TT-H6 (descriptive; the −0.03 bar equals the size of the 401/402 B − A effect)

| Pair | ΔF̄ per seed (403, 404, 405, 406, 407) | Mean ± SD over 5 seeds | Seeds negative | Registered sentence |
|---|---|---|---|---|
| B − A | −0.005, −0.041, −0.032, −0.003, −0.022 | −0.021 ± 0.016 | 5 / 5 | not distinguished |
| Sb − A | +0.008, −0.007, −0.021, +0.010, −0.005 | −0.003 ± 0.013 | 3 / 5 | not distinguished |
| Sb − B | +0.013, +0.034, +0.011, +0.014, +0.017 | +0.018 ± 0.009 | 0 / 5 | not distinguished |
| B − Sb | −0.013, −0.034, −0.011, −0.014, −0.017 | −0.018 ± 0.009 | 5 / 5 | "not distinguished" (bar −0.03 reached on 1 of 5 seeds) |

- B − A: every per-seed interval excludes 0, but only 2 of 5 seeds reach −0.03.
- Sb − B: every per-seed interval lies above 0.
- Across all seven seeds, B − A is negative on 7 of 7 and meets −0.03 on 4 of 7; Sb − B is positive on 7 of 7. The
  fresh-seed effect (−0.021) is about 60% of the 401/402 effect. The two blocks differ in training and scoring host
  (pn1a/pn1b plus tt1c, against pn1fs), so the shrinkage is not attributed.

Across-seed means (± SD):

| Arm | F̄ | F_max |
|---|---|---|
| A | 0.023 ± 0.019 | 0.078 ± 0.068 |
| B | 0.0024 ± 0.0028 | 0.0072 ± 0.0072 |
| Sb | 0.020 ± 0.012 | 0.064 ± 0.041 |

### Printed reads (no rule)

- **Geometry-112 flag share (camera photos after the 112 px path):**
  - A: 0.415, 0.504, 0.475, 0.185, 0.348;
  - B: 0.012, 0.002, 0.002, 0.000, 0.005;
  - Sb: 0.091, 0.065, 0.022, 0.029, 0.058.
  - At 224 px the share is 0-1.2% for every network.
- A's TT-H5 'source matters' verdict rests on the 224 px anti-spoofing group only, as in 401/402.
- **R3(g) at 112 px, all four packs:**
  - A: 0.23-0.50;
  - B: 0.93-0.997;
  - Sb: 0.81-0.95.
  - At 224 px every network is at 0.92-1.00.
- **FFHQ genuine own-rule flags:**
  - A: 0.065-0.108;
  - B: 0.025-0.108;
  - Sb: 0.024-0.051.
- On FFHQ genuine photos, B is not clearly below A (paired −0.05 to 0; equal on s404), and B exceeds 10% on 2 of 7
  seeds (s401, s404). B's low false-alarm rate is specific to the low-resolution bordered frames.
- **F̄ above −2 logit:**
  - A: 0.010-0.072;
  - B: 0.006-0.022;
  - Sb: 0.215-0.393.

## TT1-X Part 1: the Sp arm, seeds 403-405 (printed only; no rule)

Reader `tt1_read_x.py` (f358128, pinned before any Sp score was opened). Output `tt1_read_x_sp.json` (`986c2573…`).
Gate: 3 of 3 byte-identical.

| Network | F̄ | F_max | Family with F_max | FFHQ genuine flag | Geometry-112 flag | R3(g) at 112 px | F̄ above −2 |
|---|---|---|---|---|---|---|---|
| Sp_s403 | 0.033 | 0.109 | cfp_ff | 0.085 | 0.084 | 0.86-0.87 | 0.20 |
| Sp_s404 | 0.030 | 0.114 | cfp_ff | 0.154 | 0.041 | 0.92-0.93 | 0.12 |
| Sp_s405 | 0.023 | 0.060 | casia_fasd | 0.116 | 0.024 | 0.94-0.95 | 0.26 |

FS1 Sb at the same seeds, for reference: F̄ 0.015, 0.041, 0.013.

## What the paper may and may not say (review REVIEW_TT1_FS_20261113.md)

May say: "On about 21,000 genuine photos from eight development sources not seen in training (small faces enlarged
1.7-3.5x, with a black border), the protocol-trained network kept its fixed decision rule on all seven seeds: at most
4.9% of any family flagged, mean F̄ 0.6%. The plain network exceeded the rule on 4 of 7 seeds (up to 23.5%). Both remain
clearly displaced from the training camera photos, so a threshold calibrated on camera photos does not transfer." With
the note: the seven seeds come from two training blocks on different hosts (pn1a/pn1b plus tt1c; pn1fs).

May not say: that B is the better arm overall; that B transfers to sharp sources (FFHQ up to 17.8%); anything about
misses or detection; that the B − A size is fixed; that the plain network "fails to transfer" in general (it passes on
3 of 7 seeds); that splice positives (Sb) "cost" false alarms in general (Sb is higher on these frames but lowest on
FFHQ).

Sp (review F7): Sp F̄ 0.023-0.033 against Sb 0.013-0.041 at the same seeds, not separable; Sp flags more FFHQ genuine
photos (8.5-15.4%) and is the only arm with nonzero R_cam flags (0.2-0.7%).

## Post-result items Z1-Z4 (registered before computing at 62139a7; `zfs.json`, `src/TT1/zfs.py`; zero GPU; reviewed by results-reviewer (opus): sound, wording fixes applied)

- **Z1 (post hoc): flags against development misses, 15 fresh-seed networks.** Verdict: **"no B-against-A miss cost
  shown"**.
  - Spearman ρ(F̄, development miss) = −0.35 (permutation p = 0.10).
  - B − A development miss is −0.002, +0.001, +0.010, +0.003, +0.010 on seeds 403-407, all ≤ 0.02. The ladder R4 and
    AF0 u50 misses are 0-0.3% for every network; splice S4 is B − A −0.7 to +3.1 points.
  - Sb − B is −0.22 to −0.25: Sb misses far fewer splices, about 25% against about 97%.
  - Ladder R4 and AF0 u50 misses are at the floor (≤ 0.6%) for every network, and A and B both miss 92-99% of S4
    splices. So y can show a B-against-A cost only on splices, and both arms are near the ceiling there. The verdict
    is therefore weak evidence of no cost. The pooled ρ is between arms. Within each arm, Spearman(F̄, y) is +0.2 (A),
    +0.7 (B) and +0.8 (Sb) (post hoc, from zfs.json), so within an arm more false alarms go with more misses. The p
    value is a one-sided permutation p.
- **Z2 (descriptive): A's flags track its storage sensitivity.** Verdict: **"related"**.
  - Spearman(F̄, geometry-112 flag share) = 0.90 and Spearman(F̄, |ρ_LFW|) = 0.70, the latter exactly at the 0.7 cut.
    With n = 5, Spearman moves in steps of 0.1. 'Related' is the coded label for ≥ 0.7.
  - F̄ per seed: 0.007, 0.048, 0.034, 0.004, 0.023.
  - Geometry-112 flags per seed: 0.415, 0.504, 0.475, 0.185, 0.348.
  - Seeds 401/402, printed separately because they come from other hosts: F̄ 0.057 / 0.038 and geometry-112 flags
    0.460 / 0.566.
  - A_s401 has the highest F̄ of all seven seeds but a middling geometry-112 share.
  - Association only, five seeds.
- **Z3 (descriptive): Sb and CFP-sized borders.** Verdict: **"Sb above B on 5 of 5 seeds"**.
  - CFP-FF border-reference flag share, Sb against B: 0.118 / 0.014, 0.060 / 0.010, 0.067 / 0.007, 0.029 / 0.000,
    0.163 / 0.019.
  - Sb flags more training-source camera photos once a CFP-FF-shaped constant border is blanked in (Sb 0.029-0.163;
    B 0.000-0.019). On the same photos without the border, both flag 0.000 on all five seeds. The excess is not
    specific to CFP: Sb − B is +0.026 to +0.060 on MSU-MFSD and +0.026 to +0.048 on Oulu-NPU, and +0.00 to +0.03
    elsewhere. CFP-FF is the largest gap on 3 of 5 seeds. This is descriptive and Sb is splice-trained, so it does not
    show that Sb uses borders on unseen CFP-FF images.
  - R3(c) for CFP-FF (Sb − B) is mixed: −0.074 to +0.082.
- **Z4 (descriptive): B's FFHQ flags against its unseen-source flags.** Verdict: **"one seed-level instability
  consistent"**.
  - Over B's 7 seeds, Spearman(FFHQ genuine flag share, F̄) = 0.96.
  - FFHQ flags: 0.179, 0.064, 0.052, 0.108, 0.061, 0.038, 0.025.
  - F̄: 0.0238, 0.0022, 0.0016, 0.0073, 0.0020, 0.0003, 0.0010.
  - This is an association over 7 seeds from two hosts. Seeds 401/402 were trained on pn1a/pn1b and scored on tt1c;
    seed 401 is the extreme on both axes. On seeds 403-407 alone, ρ = 0.90.
