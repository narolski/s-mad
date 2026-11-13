# Threshold transfer on unseen genuine sources (TT1): result (registered reading, not yet reviewed)

Status at the commit that adds this text: the 11 networks that passed the platform gate were scored on lease tt1c
(A100-SXM4 80 GB, torch 2.2.1). The registered reader was run. Owner's numbers, sent for independent post-result review.

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
| B | none; every family's upper bound ≤ 10% on both seeds | falsified: the own rule transfers on these sources |
| Sb | cfp_ff and agedb_30 | supported |
| Bv | none | falsified (printed arm) |
| C | 4 on seed 401, 0 on seed 402 | printed |

The R_cam own-rule share is 0 for every network except C_s401 (0.5%), so TT-H1 is informative for every network.

### TT-H2: do unseen photos sit above the training-source photos?

Supported for all 11 networks. AUC of each unseen source against R_cam is 0.987-1.000 in all 8 sources. No read is
floor-tied: R_cam sits about 0.15 logit above the head floor of about −3.83, and its share within 0.05 of the floor
is 0.

### TT-H3: is the border material?

Inconclusive for all 11 networks:
- The border alone moves the camera photos strongly: R3(e) is 0.85-0.99.
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
- R4(c)/(d) are printed under the M5 labels and decide nothing. For reference, covariates explain 0.03-0.95 of the
  between-family variance depending on the network.

### TT-H6: arms (descriptive; no arm, seed or threshold is chosen from TT1)

| Pair | ΔF̄ seed 401 [interval] | ΔF̄ seed 402 [interval] | Registered sentence |
|---|---|---|---|
| B − A | −0.033 [−0.041, −0.027] | −0.035 [−0.040, −0.032] | "B has lower genuine flag rates than A on seeds 401/402" |
| Sb − A | −0.013 | −0.005 | not distinguished |
| Sb − B | +0.021 [0.013, 0.029] | +0.031 [0.028, 0.033] | not distinguished |

- Sb − B is positive on both seeds with intervals above 0. Sb flags more unseen genuine photos than B, but the
  registered rule only prints a "lower" sentence.
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

## What cannot be claimed

- Any miss rate or morph detection.
- A benchmark or generalisation statement.
- A cause of any source effect. Source is confounded with JPEG, sensor and capture.
- A separate effect of enlargement across geometry groups.
- Any arm choice. TT-H6 is descriptive.

Pack intervals use pseudo-identities, inflated by sqrt(components / people). CFP-FF and AgeDB people may overlap with
CASIA-WebFace celebrities (not checked).

## Spend

Rented A100 time:
- tt1a 0.56 USD;
- tt1b about 0.6 USD;
- tt1c about 0.9 USD (01:03 to the 01:46 release).

DGX GPU about 25 min. WCSS: nothing queued (uploaded files kept).
