# Protocol network, first tests (PN1): result (short page)

Status 12 Nov 03:00 CET: tier 1 read as registered on rented A100s (amendment 7); Athena jobs cancelled or discarded.
Full record: `README.md`. Registration: `prereg.md` (amendments 1 to 12, pack pins). No conclusion is drawn here; the
lead draws conclusions. Review of tier 1: `experiments/reviews/REVIEW_PN1_TIER1_20261112.md` (corrections applied).

## Tier 0 (frozen heads; tier 0 decides nothing in favour, prereg section 7)

Test ladder 191 hosts (OpenCV-style engine), seed 401, arms photos-against-morphs (A0) / protocol (B0) / equal-size
protocol (Bn0). Intervals over partner cycles. τ_cam = 5% false alarms on development camera photos.

| Read | CLIP A0 | CLIP B0 | CLIP Bn0 | DINOv3 A0 | DINOv3 B0 | DINOv3 Bn0 |
|---|---|---|---|---|---|---|
| R2w vs R4 (excess over best of 39 statistics, 0.888) | 1.000 (+0.11) | 0.998 (+0.11) | 0.999 (+0.11) | 0.999 (+0.11) | 0.999 (+0.11) | 0.999 (+0.11) |
| R0_61 vs R4 | 0.999 | 0.998 | 0.999 | 0.999 | 0.999 | 0.998 |
| shift R0 -> R0_61 (SD) | +0.30 | +0.17 | +0.14 | +0.75 | +0.43 | +0.40 |
| shift R0 -> R0_112 (SD) | +0.15 | +0.08 | +0.04 | +0.45 | +0.24 | +0.18 |
| τ_cam: R0_61 flagged | 20.4% | 8.4% | 5.2% | 23.6% | 10.5% | 10.5% |
| τ_cam: FRLL jpeg50 flagged | 3.9% | 2.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| τ_cam: gating-family mean miss | 16.0% | 16.4% | 22.8% | 37.6% | 37.1% | 40.1% |
| own rule: gating-family mean miss | 48.5% | 46.6% | 49.7% | 61.9% | 61.1% | 60.9% |
| H1 AUC | 0.877 | 0.888 | 0.879 | 0.850 | 0.842 | 0.839 |
| MAD22 E7 EER OpenCV / Webmorph | 4.9 / 6.2% | 4.4 / 4.9% | 3.9 / 6.8% | 5.4 / 12.8% | 5.2 / 11.4% | 4.9 / 10.8% |
| P-c / P-c2 | fail / fail | pass / pass | pass / pass | fail / fail | fail / pass | fail / pass |
| K0; 2 x 2 control | no; pass | no; pass | no; pass | no; pass | no; pass | no; pass |

Seed spread (CLIP): A0 seeds 402 to 404 chose a stronger regularisation (C = 0.1) and flag 7.3% of R0_61 at τ_cam.

Certificate (nuisance-only; `cert/`): manifest A 1.00 (engine), B 0.84, Bn 0.83, C 0.84. Matched-subsample test: no
kill rule met (48.5% kept; nuisance AUC 0.47; R0 -> R0_61 flag change +4.7 points matched, +8.9 random, +4.7 full).

## Provisional tier-0 version (kept, superseded)

The first tier-0 tables (CLIP heads A0 and B0, computed 19:35 to 19:53, read by the owner and reported to the lead at
about 19:53) were made with class balance over the whole manifest. The independent pre-run review (manifest counts
only, no score opened) showed that this balance made "stored at 61.2 px" a cue for "morph" in B0 and left a database
cue in A0. Those tables are kept under `tier0_v1_provisional/`, `tier0_v1_provisional_tables.md` and
`tier0_v1_provisional_key.csv` and are superseded. They are not results of PN1.

## Spliced reads (amendments 8 to 11), wording as corrected by the splice review

- "Spliced morphs (blend only inside the face): with OpenCV the seam is equal in size but not in kind. A spliced morph
  carries a colour step that one simple number separates from the negative at about 0.71. With FaceMorpher the
  negative has almost no seam, and those reads are not seam-matched."
- "Spliced positives move frozen heads partly toward the face (face-blanked 0.99 to 0.76 / 0.88 for spliced-only). No
  full-frame head reads more inside the face than one band-power statistic (0.906, chosen on test, optimistic). Spliced
  heads do not improve on real face-spliced morphs (H1)." Post hoc: heads trained on face-only copies do exceed band5
  on face-only test copies (CLIP 0.950, DINOv3 0.992) but transfer to nothing else (MAD22 E7 EER 33-36%, H1 0.53-0.56).
- "The bracketing share is saturated (1.000) and does not discriminate between heads."
- "Protocol plus spliced on DINOv3, corrected MAD22 2.0 / 3.0%: best of 8 heads on first-test data. The head still reads
  the surround. A lead to re-test, not a method result. Seeds vary only the inner folds." Post hoc training-person
  resampling: OpenCV E7 EER 1.0 to 8.8% (median 2.75%).

## Tier 1 (eight ViT-B/16 LoRA fits, rented A100s, amendment 7; read as registered, 12 Nov 03:00)

Platform: pn1a (A100-SXM4 40 GB) seed 401, pn1b (A100-SXM4 80 GB) seed 402; host Python, pinned packages, pack
`5c642790…`; scores = logit without flip. Test ladder 191 hosts (OpenCV-style). τ_cam = 5% on development camera photos.

| Read | A 401 | B 401 | Bn 401 | C 401 | A 402 | B 402 | Bn 402 | C 402 |
|---|---|---|---|---|---|---|---|---|
| R2w vs R4 / R2w4 vs R4 (excess +0.112 [0.076, ...] over 0.888) | 1.000 / 1.000 | 1.000 / 1.000 | 1.000 / 1.000 | 1.000 / 1.000 | 1.000 / 1.000 | 1.000 / 1.000 | 1.000 / 1.000 | 1.000 / 1.000 |
| R0_61 vs R4 / R2w_61 vs R4 | 0.999 / 0.998 | 1.000 / 1.000 | 1.000 / 1.000 | 1.000 / 1.000 | 0.999 / 0.997 | 1.000 / 1.000 | 1.000 / 1.000 | 1.000 / 1.000 |
| mean logit shift R0 -> R0_61 (SD of R0 logits) | +1.73 (0.027) | +0.15 (0.039) | +0.22 (0.060) | +0.19 (0.187) | +2.64 (0.024) | +0.13 (0.019) | +0.16 (0.028) | +0.11 (0.026) |
| shift in SD units (P-c reads this) | 63.4 | 3.9 | 3.7 | 1.0 | 108.2 | 6.7 | 5.5 | 4.2 |
| H1 AUC | 0.847 | 0.781 | 0.747 | 0.838 | 0.827 | 0.680 | 0.661 | 0.816 |
| MAD22 E7 EER OpenCV / Webmorph (%) | 3.4 / 18.4 | 1.8 / 13.7 | 2.1 / 11.8 | 0.5 / 7.8 | 5.0 / 20.6 | 4.4 / 19.0 | 3.6 / 18.2 | 0.9 / 7.0 |
| R4 vs R3 | 0.731 | 0.767 | 0.770 | 0.772 | 0.756 | 0.761 | 0.765 | 0.773 |
| τ_0.5 flag T_R0_61 / T_R0_112 | 20.4 / 2.1% | 1.6 / 1.0% | 3.1 / 1.0% | 2.1 / 1.0% | 31.9 / 3.7% | 1.0 / 0.0% | 0.5 / 0.0% | 1.0 / 0.0% |
| τ_0.5 flag FRLL jpeg50 / H1 genuine | 0 / 22.2% | 0 / 8.2% | 0 / 7.9% | 0 / 25.6% | 0 / 15.6% | 0 / 0.3% | 0 / 0.3% | 0 / 3.7% |
| τ_0.5 gating-family mean miss | 30.3% | 28.8% | 31.1% | 14.2% | 34.7% | 38.9% | 38.3% | 22.0% |
| τ_cam flag T_R0 / T_R0_61 / T_R0_112 | 1.0 / 75.9 / 16.8% | 1.0 / 7.9 / 4.2% | 3.7 / 10.5 / 6.3% | 2.1 / 11.5 / 5.8% | 6.3 / 93.2 / 33.0% | 2.6 / 13.6 / 7.3% | 3.7 / 17.8 / 8.4% | 0.5 / 11.5 / 5.2% |
| τ_cam flag FRLL native / jpeg70 / jpeg50 | 51 / 57 / 79% | 77 / 83 / 91% | 95 / 96 / 99% | 30 / 21 / 32% | 66 / 84 / 99% | 67 / 78 / 99% | 70 / 87 / 98% | 38 / 31 / 47% |
| τ_cam flag H1 genuine | 100% | 100% | 100% | 99.5% | 100% | 100% | 100% | 100% |
| τ_cam miss ladder R4 / MAD22 OpenCV / Webmorph / H1 | 0 / 0.2 / 5.0 / 0% | 0 / 0 / 2.2 / 0% | 0 / 0 / 0.2 / 0% | 0 / 0 / 4.2 / 0% | 0 / 0.2 / 2.8 / 0% | 0 / 0.3 / 4.0 / 0% | 0 / 0.1 / 3.4 / 0% | 0 / 0 / 3.0 / 0% |

Marks (section 7, amendments 1 and 4), every B, Bn and C network: P-a pass, P-b pass, P-e pass, P-f pass; P-c fail,
P-c2 fail (unseen kernels and other E7 strengths fail: FRLL and MAD22 genuine pools flagged above 10% at τ_cam), P-d
fail (H1 below 0.85); kill rules not met. P-g (gating miss at τ_cam, X minus A, paired bootstrap refitting τ_cam):
B 401 -0.8 points [-4.1, +8.5], B 402 +0.3 [-1.6, +16.4], Bn -1.3 [-4.4, +14.2] / +0.1 [-1.6, +24.9], C -0.3 [-3.1,
+5.3] / -0.0 [-2.3, +1.6]; non-inferior (upper bound at most +3) only C 402. A violation: yes on both seeds (storage and
JPEG 50). JPEG mark for C: FRLL jpeg50 flagged 32% / 47% at τ_cam (not at most 10%).
Registered reading: B, Bn and C do not pass (P-c, P-c2, P-d fail on both seeds); no kill rule met; loss rule (§7)
applies (pass P-a and P-b, fail P-c → equality term, outside PN1). A violation on both seeds, robust at the own rule
(20.4 / 31.9% of 61 px copies). No "removes" sentence.
Scale caveat: the head is linear on normalised features (‖w‖ 3.84 to 3.86, bias about 0.01), so logits are bounded at
about ±3.87. Camera photos sit at −3.67 with SD 0.02 to 0.19, and τ_cam lies 0.03 to 0.10 logits above them. P-c's SD
unit and every τ_cam mark (P-c, P-c2, JPEG, P-g) read this saturated band. At τ_cam the gating-family miss is 0.05 to
1.3% for every fit, bought by flagging 30 to 95% of FRLL and 99.5 to 100% of H1 genuine photos, so P-g carries no
information. MAD22 genuine = the same 204 FRLL photos. P-a and P-b are at ceiling (identical excess in all 8 fits).
Training-row minus held-out logit gaps per kind: within ±0.2 logits (up to 7 floor-SDs: lad_R2w −0.17 C401, −0.14
Bn401).

Reference row "standard recipe on released SMDD" (eight A12-BR ViT-B/16 retrains, same scorer, rented pn1a): seven of
eight flag more than 10% of some history-matched genuine pool at the own rule, all eight at τ_cam (largest pool flag
43 to 74%); JPEG pools 0 to 6.4% at τ_cam; gating-family mean miss 13 to 56% at the own rule, 8 to 22% at τ_cam.
Athena reference result 3545977 discarded (amendment 6).

## Tier-1 follow-ups (POST HOC, descriptive; README section 5.3)

Head norm 3.84 to 3.86 (logits bounded at about ±3.87); test photos sit 0.15 to 0.19 logits above the floor. Share of
hosts whose logit rises photo -> 61 px copy: A 0.98 / 0.99, B 0.66 / 0.61, Bn 0.50 / 0.56, C 0.69 / 0.53. The
corrected-MAD22 raw files are JPEG in every class; C − A score difference vs blockiness: |ρ| ≤ 0.013.

## Compute

- DGX GB10 (shared), one process: about 37 minutes of GPU wall time (allowance 30 minutes).
- Rented A100s (lead's leases, amendment 7): pn1a A100-SXM4 40 GB at 0.59 USD/h, pn1b A100-SXM4 80 GB at 1.06 USD/h;
  at 03:05: pn1a 5.8 h / 3.44 USD, pn1b 5.8 h / 6.19 USD (guard estimates in the lease folders' LIVE.json); final
  figures when RELEASE is written. Fit times 69 min (pn1a), 82 to 85 min (pn1b).
- Athena (account plgmultivision-gpu-a100, A100-SXM4-40GB, container image `fedeff10…`):

| Job | Purpose | State | Elapsed | GPU-hours |
|---|---|---|---|---|
| 3545947 | smoke 1 (arm Bn) + DINOv3 extraction | FAILED (path bug in the smoke job file; DINOv3 part done) | 0:04:14 | 0.07 |
| 3545968 | smoke 2 (arm Bn, 200 steps, 64 rows) | COMPLETED, rc 0, 1.24 it/s, peak 30,833 MiB | 0:05:21 | 0.09 |
| 3545976_[0-7] | eight fits (limit 2 h 15 min) | cancelled 21:46 before start (amendment 6) | 0 | 0 |
| 3545977 | reference row (amendment 5) | completed 7 min 46 s; result discarded (amendment 6) | 0:07:46 | 0.13 |

## Spliced LoRA arm and volume control (amendment 10, with B rescored under amendment 12), registered reading

Tars verified, RELEASE written by the pull loops: pn1a 04:18:58 (9 of 9), pn1b 05:04:26 (8 of 8) (pull-log times).
Reader `src/PN1/sb_read.py` -> `tier1_sb/sb_read.json`.

| seed | arm | (i) face-blanked R2w vs R4 AUC, dev / test (B: 1.000 / 0.999-1.000) | (ii) S0 vs S4 excess lower bound, dev | (iii) P-c, P-c2, kernels | (iv) P-g vs B, diff [lo, hi] | (v) H1 AUC (B) | MAD22 E7 EER OpenCV / Webmorph |
|---|---|---|---|---|---|---|---|
| 401 | Sb | 0.991 / 0.995: fails | +0.049: passes | fail, fail, fail | +0.6 [−12.5, +1.9] pts: passes | 0.909 (0.781): passes | 1.9 / 8.2 (B 1.8 / 13.7) |
| 401 | Bv | 1.000 / 0.999: fails | −0.283: fails | fail, fail, fail | −0.3 [−1.4, +0.4]: passes | 0.777: passes | 1.7 / 13.4 |
| 402 | Sb | 0.999 / 0.999: fails | +0.051: passes | fail, pass, fail | −0.5 [−16.1, +0.7]: passes | 0.913 (0.680): passes | 2.9 / 16.4 (B 4.4 / 19.0) |
| 402 | Bv | 1.000 / 1.000: fails | −0.287: fails | fail, fail, fail | 0.0 [−0.5, +0.8]: passes | 0.671: passes | 3.9 / 17.6 |

Registered reading: killed by the amendment-10 rule; (i) fails on both seeds (face-blanked 0.991 / 0.999 vs B 1.000).
Read (i) asks whether surround reliance falls; it did not, and on OpenCV full-frame morphs the surround carries a real
blend. It does not show that Sb ignores the face. Post hoc: face-only R4 vs R2w rose from 0.840 / 0.865 (B) to 0.938 /
0.957 (Sb); Bv equals B (0.838 / 0.861), so the change is not row volume.

H1 (post hoc wording, review F4): Sb raises H1 AUC over B by 0.13 / 0.23 and over A by 0.06 / 0.09; paired
host-matched ranking equals A's (0.95). First-test data; a lead for a fresh registration, not a result.

## HN2 on FFHQ (amendment 13, git a1c6664), registered reading

Reader `src/PN1/hn2_read.py` -> `tier1/hn2.json`. Scored on the seed's own machine: seed 401 on GPU-268644bb
(A100-SXM4-40GB, pn1a), seed 402 on GPU-eb4176c8 (A100-SXM4-80GB, pn1b).

| network | (a) FFHQ genuine flagged at own rule [95% CI] | (b) AUC lc morphs vs FFHQ genuine [95% CI] | verdict | printed: flagged at τ_cam; AUC vs history-matched genuine; history-matched flagged at own rule |
|---|---|---|---|---|
| A 401 | 22.5% [20.6, 24.3] | 0.988 [0.984, 0.991] | calibration shift | 94.8%; 0.935; 54.7% |
| B 401 | 17.8% | 0.998 | calibration shift | 95.3%; 0.994; 26.3% |
| Bn 401 | 22.4% | 0.997 | calibration shift | 97.7%; 0.993; 29.3% |
| C 401 | 17.7% | 0.999 | calibration shift | 96.5%; 0.997; 23.5% |
| A 402 | 9.9% | 0.997 | calibration shift | 95.5%; 0.971; 34.1% |
| B 402 | 6.4% | 0.998 | calibration shift | 95.9%; 0.995; 11.8% |
| Bn 402 | 5.4% | 0.998 | calibration shift | 96.8%; 0.995; 10.2% |
| C 402 | 3.5% | 1.000 | calibration shift | 95.7%; 0.999; 7.4% |

Registered reading (rule of amendment 13): every network returns the registered verdict "calibration shift (not a
shortcut)", both seeds agreeing. Label (review F3): not a source-identity shortcut for ranking: within FFHQ the
networks rank whole-frame landmark morphs above disjoint genuine persons (AUC ≥ 0.988; against history-matched genuine
0.993–0.999 for B, Bn, C; 0.935 / 0.971 for A). The decision threshold does not transfer: 3.5–22.5% flagged at the
own rule, 95–98% at τ_cam. No simple-statistic floor on FFHQ, so "reads the blend" is not shown.

## Post hoc tables (batch-2 review F2, F4; recomputed in `src/PN1/posthoc_b2.py` -> `tier1/posthoc_b2.json`)

POST HOC, descriptive. 95% intervals from 2,000 bootstraps (rng 20261116) over persons (FFHQ) or hosts (H1); they do not
cover training variance.

FFHQ, the same 2,000 persons, history-matched (shrunk to the morphs' 65 px eye distance and enlarged back) against
native, paired by key:

| network | AUC history-matched vs native [CI] | share whose logit rises [CI] | mean shift, logits [CI] | median shift | own-rule flags native -> history-matched |
|---|---|---|---|---|---|
| A 401 | 0.683 [0.672, 0.693] | 0.778 [0.760, 0.796] | +2.03 [1.92, 2.13] | +0.743 | 22.5 -> 54.7% |
| B 401 | 0.513 [0.508, 0.519] | 0.443 [0.421, 0.465] | +0.39 [0.34, 0.44] | −0.026 | 17.8 -> 26.3% |
| Bn 401 | 0.494 [0.487, 0.500] | 0.414 [0.392, 0.436] | +0.34 [0.29, 0.40] | −0.035 | 22.4 -> 29.3% |
| C 401 | 0.496 [0.490, 0.501] | 0.357 [0.337, 0.378] | +0.23 [0.19, 0.27] | −0.051 | 17.7 -> 23.5% |
| A 402 | 0.665 [0.654, 0.675] | 0.721 [0.701, 0.740] | +1.61 [1.51, 1.71] | +0.232 | 9.9 -> 34.1% |
| B 402 | 0.487 [0.480, 0.494] | 0.372 [0.350, 0.394] | +0.27 [0.23, 0.31] | −0.030 | 6.4 -> 11.8% |
| Bn 402 | 0.482 [0.475, 0.489] | 0.340 [0.320, 0.361] | +0.20 [0.16, 0.24] | −0.041 | 5.4 -> 10.2% |
| C 402 | 0.476 [0.470, 0.482] | 0.302 [0.282, 0.322] | +0.17 [0.13, 0.21] | −0.040 | 3.5 -> 7.4% |

Reading (post hoc): on 2,000 FFHQ persons (unseen source), the history change raises the plain network's logit for
72–78% of persons (AUC 0.67–0.68) and B, Bn, C for 30–44% (AUC 0.48–0.51): the tier-1 scale-free storage reading
replicates on a second source. A small upper tail remains (own-rule flags rise by 4 to 9 points for B, Bn, C).

H1, each Poisson morph against its own host's genuine photo (same 112 px history), 598 pairs:

| network | share of morphs above own host [CI] (401) | genuine flagged / morphs missed, own rule (401) | share [CI] (402) | genuine flagged / morphs missed (402) |
|---|---|---|---|---|
| A | 0.955 [0.938, 0.972] | 22.2 / 23.9% | 0.958 [0.941, 0.973] | 15.6 / 36.6% |
| B | 0.905 [0.881, 0.928] | 8.2 / 49.7% | 0.696 [0.657, 0.732] | 0.3 / 80.3% |
| Bn | 0.848 [0.818, 0.875] | 7.9 / 56.7% | 0.639 [0.599, 0.679] | 0.3 / 85.8% |
| C | 0.953 [0.936, 0.970] | 25.6 / 23.2% | 0.905 [0.881, 0.926] | 3.7 / 53.7% |
| Sb | 0.950 [0.931, 0.967] | 7.0 / 26.1% | 0.948 [0.931, 0.965] | 9.7 / 21.6% |
| Bv | 0.903 [0.878, 0.926] | 7.7 / 50.8% | 0.669 [0.632, 0.706] | 0.3 / 82.4% |

## Rented compute, final (guard estimates at RELEASE)

pn1a: 7.13 h, about 4.22 USD (cap 6). pn1b: 7.9 h, about 8.39 USD (cap 11). The lead stops the instances.

## Amendment 14, development read on FFHQ (registered a1dc46e; deviations de30e7f, bcf2164, 12e55c6), registered reading

Tar `PN1_A14.tar` verified 10:24:56 (rc 0). Scored on the FS1 host, GPU-5bd20020 (A100-PCIE-40GB), before the fit
queue. Reader `src/PN1/a14_read.py` (`0f259c8d…`) -> `tier1_a14/a14.json`. No benchmark row read.

**Gate:** equivalent. The rescored A_s401 and B_s402 HN2 files are byte-identical to the pn1a (A100-SXM4-40GB) and
pn1b (A100-SXM4-80GB) files: max |Δ logit| 0.0, ΔAUC 0.0. HN7 and HN2b keep their verdicts.

**HN8, landmark_combined orig morphs vs history-matched genuine (AUC [95% CI]; own-rule morph miss / genuine flagged):**

| network | 401 | 402 |
|---|---|---|
| A | 0.778 [0.760, 0.795]; 11.2 / 54.4% | 0.746 [0.727, 0.765]; 29.3 / 33.8% |
| B | 0.754 [0.733, 0.772]; 31.1 / 26.1% | 0.716 [0.694, 0.736]; 54.9 / 11.8% |
| Bn | 0.748; 31.8 / 29.7% | 0.724; 57.0 / 10.3% |
| C | 0.752; 32.4 / 23.5% | 0.751; 54.0 / 7.7% |
| Sb | 0.887 [0.873, 0.902]; 24.2 / 6.7% | 0.909 [0.897, 0.922]; 18.5 / 9.6% |
| Bv | 0.752; 31.9 / 25.8% | 0.711; 59.1 / 10.2% |

- Registered reading: **supported**.
  - Both seeds are testable (B 0.754 / 0.716 < 0.95).
  - Sb − B: +0.133 / +0.194 (≥ 0.05). Sb − A: +0.109 / +0.163 (≥ 0).
- Floor: the best simple statistic is noise_std_face at 0.886. Sb's lower bound over the floor maximum, re-taken per draw, is −0.017 (401) and +0.006 (402).
  - It is not above 0 on both seeds, so **"reads the face splice" is not stated**.
  - Every other network sits 0.13 to 0.20 below the floor.
- The aligned==1 subset gives the same AUCs to the third decimal.
- Disclosure (registered): A's reading of this pool is partly history-driven.

**Paired landmark_complete minus landmark_combined logit, same pair key (1,000 pairs; printed; complete scores of A, B, Bn, C from pn1a / pn1b):**
- mean shift 401 / 402: A +0.88 / +2.18; B +2.39 / +3.94; Bn +2.35 / +4.03; C +2.43 / +3.84; Sb +1.62 / +1.41; Bv +2.44 / +4.12.
- The share scored higher on the complete morph is 0.70 to 0.99 for every network.
- Every network scores the whole-frame morph above the face-only splice of the same pair. Sb loses the least on seed 402, and A the least on seed 401.

**HN7 (associational, between arms), face-only R4 vs R2w on the test ladder against landmark_combined AUC, 12 networks:**
- Spearman: ρ = 0.35 [0.24, 0.70]; arm level (n = 6) 0.66 [0.31, 0.94]; without Sb −0.12 (n = 10), 0.40 at arm level (n = 5).
- Registered reading: **inconclusive, no claim** (between 0.2 and 0.6).
- The blind prediction holds: A's face-only AUC is above B's on both seeds (0.941 / 0.932 against 0.840 / 0.865). But A's landmark_combined AUC is only 0.778 / 0.746, so face-only sensitivity on our ladder does not rank-predict the combined read without Sb.

**HN2b** (amendment-13 rule): Sb 401 / 402 and Bv 401 / 402 all read "calibration shift (not a shortcut)" (added under amendment 14).
- Own-rule FFHQ genuine flags: Sb 5.9 / 7.0%, Bv 17.6 / 5.8%.
- Within-source AUC: 0.995 to 0.998.

Development data only (FFHQ by designation, our own ladder). Seeds 401/402 are confounded with machine. The FS1
contrasts were frozen (ac585b7) before this read.
