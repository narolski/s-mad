# Same-person blends as negatives (SE1): result of the A100 block

Read once on 13 Nov 2026 at 17:05 CET with `src/SE1/se1_read.py` (fbf9b260…; the registered reader with the print-only and provenance changes recorded in prereg.md). Output: `se1_read.json`. Development data only. Reviewed by the results-reviewer (Opus), 13 Nov (`experiments/reviews/REVIEW_SE1_A100_20261113.md`); its corrections are applied below.

**Platform.** Rented A100 PCIe 40 GB, image pytorch 2.2.1 / CUDA 12.1 (deviations SE1-D1 and SE1-D2).
- Read seeds: 408, 409, 410 and 411 (4 seeds), so "met" means 4 of 4. Seed 412 was not run.
- Each seed's three networks (A, Sb, SE) were fitted on one lease. All 12 tars are verified in two copies.
- Final training losses: A 0.026–0.027; Sb 0.041–0.064; SE 0.038–0.111.

## Registered verdicts

| Rule | Verdict |
|---|---|
| 7.1 Target T: S3 ≤ 10%, R3 ≤ 10%, stored R3 ≤ 20%, OpenCV, development | **not met** (0 of 4 seeds); "reduced, not removed" also not met (0 of 4) |
| Held-out engine sentence (FaceMorpher S3 and R3 ≤ 20%) | not met (0 of 4) |
| 7.2 G1, two-person detection (seed means) | **met** (all five legs). The R4 OpenCV leg is met at the margin, 0.048 against 0.05: SE misses 2–7% of development R4 where Sb misses none |
| 7.3 G2, storage (C2P rule, A of the same seed as control) | **inconclusive, no claim for SE and for Sb alike**: fm61 4 of 4, amsl112 2 of 4, with the same seeds (409 and 411) failing; A's control met 4 of 4 at both sizes; H-new-1 falsified for both; no attribution. The reader prints "fails for Sb as well: no attribution" because it maps every non-pass to "fails". Under section 7.3 neither arm "fails": that needs ≤ 1 passing seed. The amsl112 misses come only from the \|Δm\| ≤ Δm(A)/3 leg (A's Δm 0.29 and 0.19). There, SE and Sb lie on the genuine side (Δm −0.12 and −0.07), with Δf ≤ +0.021 and the upper bound ≤ 0.041 on every seed |
| 7.4 G3, camera photos | **inconclusive**: absolute legs met (4 of 4); FFHQ relative leg met; MS1 native relative leg inconclusive |
| 7.5 Baseline (claim wording) | **met** (4 of 4): SE exceeds the 27-statistic baseline by ≥ 0.05 on R4 vs R3 and on S4 vs S3 (OpenCV). It governs no sentence because T was not met. Seed 410 clears the S4-vs-S3 margin by 0.0005 |
| Section 8 outcome | Target not met (0 of 4). "Reduced, not removed" not met (0 of 4): S3 failed the half rule on every seed, while R3 met it on 4 of 4 (64 ≤ 90, 52 ≤ 86, 50 ≤ 88, 54 ≤ 83). Ablation row; FINAL unchanged. The registered sentence for this row, "Same-person blends as negatives did not change the same-person flags at this dose", is **not used as written**: the registered printed read contradicts it. Wording deviation **approved by the lead on 13 Nov 2026 (17:25), after the read**; the verdict is unchanged (target not met; ablation row; FINAL unchanged). Used instead: "Same-person blends as negatives did not lower same-person splice flags (S3, SE − Sb −0.010 [−0.063, +0.040]); they lowered, but did not remove, full-frame same-person morph flags (R3 0.83–0.90 → 0.25–0.32; −0.593 [−0.678, −0.502]), also on the held-out engine (0.88–0.92 → 0.34–0.44). Four seeds, the same 100 development hosts, development data." |

## Numbers (own rule, logit > 0; development persons; 100 hosts per ladder cell; per seed 408 / 409 / 410 / 411)

### Same-person blends (flag rate)

| Cell | A | Sb | SE |
|---|---|---|---|
| S3 same-person splice, OpenCV | 0.05 / 0.04 / 0.05 / 0.07 | 0.38 / 0.37 / 0.41 / 0.36 | 0.36 / 0.34 / 0.37 / 0.41 |
| R3 same-person morph, OpenCV | 1.00 / 0.99 / 0.99 / 0.99 | 0.90 / 0.86 / 0.88 / 0.83 | 0.32 / 0.26 / 0.25 / 0.27 |
| R3 stored 61.2 px | 1.00 / 1.00 / 1.00 / 1.00 | 0.85 / 0.79 / 0.88 / 0.72 | 0.36 / 0.27 / 0.35 / 0.31 |
| R3 stored 112.7 px | 1.00 / 1.00 / 0.99 / 1.00 | 0.84 / 0.78 / 0.83 / 0.70 | 0.37 / 0.32 / 0.33 / 0.35 |
| S3, FaceMorpher (held-out engine) | 0.03 / 0.03 / 0.03 / 0.04 | 0.48 / 0.43 / 0.46 / 0.47 | 0.47 / 0.45 / 0.47 / 0.47 |
| R3, FaceMorpher | 0.99 / 0.98 / 0.99 / 0.99 | 0.92 / 0.88 / 0.90 / 0.88 | 0.44 / 0.38 / 0.34 / 0.44 |
| R3m mirror self-morph, OpenCV | 0.99 / 0.99 / 0.98 / 0.98 | 0.96 / 0.93 / 0.96 / 0.94 | 0.01 / 0.00 / 0.01 / 0.01 |
| R3m, FaceMorpher | 0.98 / 0.98 / 0.98 / 0.97 | 0.98 / 0.96 / 0.97 / 0.95 | 0.03 / 0.00 / 0.02 / 0.03 |
| AF0 development self-morphs (126) | 0.95 / 0.95 / 0.95 / 0.97 | 0.94 / 0.92 / 0.91 / 0.94 | 0.00 / 0.00 / 0.00 / 0.00 |
| S0 seam only, OpenCV | 0.00 / 0.00 / 0.01 / 0.01 | 0.00 (all) | 0.00 (all) |

Seed means of SE − Sb, with 95% host-bootstrap intervals:
- S3 (OpenCV): −0.010 [−0.063, +0.040].
- R3 (OpenCV): −0.593 [−0.678, −0.502].

SE's own-rule flags on its training rows: lad_S3 0.30 / 0.31 / 0.30 / 0.39; lad_R3 0.27 / 0.25 / 0.22 / 0.26; lad_R3m 0.00–0.006; af0_selfm 0.00–0.002; lad_S4 0.93–0.96; lad_R4 0.98–1.00.

### Two-person morphs

| Read | A | Sb | SE |
|---|---|---|---|
| FFHQ landmark_combined AUC | 0.770 / 0.749 / 0.772 / 0.773 | 0.895 / 0.891 / 0.904 / 0.886 | 0.909 / 0.910 / 0.911 / 0.911 |
| landmark_combined miss | 0.13 / 0.35 / 0.19 / 0.26 | 0.27 / 0.19 / 0.16 / 0.13 | 0.16 / 0.16 / 0.15 / 0.14 |
| R4 miss, OpenCV | 0.00 (all) | 0.00 (all) | 0.02 / 0.05 / 0.07 / 0.05 |
| R4 miss, FaceMorpher | 0.00 (all) | 0.00 (all) | 0.00 / 0.01 / 0.00 / 0.00 |
| S4 miss, OpenCV | 0.93 / 0.97 / 0.97 / 0.98 | 0.25 / 0.12 / 0.25 / 0.21 | 0.18 / 0.19 / 0.21 / 0.12 |
| AUC R4 vs R3, OpenCV | 0.821 / 0.846 / 0.845 / 0.853 | 0.901 / 0.912 / 0.910 / 0.880 | 0.917 / 0.926 / 0.912 / 0.911 |
| AUC R4 vs R3, FaceMorpher | 0.809 / 0.827 / 0.831 / 0.827 | 0.881 / 0.894 / 0.896 / 0.854 | 0.922 / 0.929 / 0.917 / 0.912 |
| AUC S4 vs S3, OpenCV | 0.559 / 0.598 / 0.593 / 0.587 | 0.782 / 0.804 / 0.756 / 0.792 | 0.805 / 0.829 / 0.785 / 0.824 |
| AUC S4 vs S3, FaceMorpher | 0.554 / 0.585 / 0.594 / 0.597 | 0.773 / 0.794 / 0.764 / 0.781 | 0.796 / 0.829 / 0.786 / 0.810 |

27-statistic baseline (trained on SE's ladder labels, `baseline27_se1.json`):
- R4 vs R3: OpenCV 0.798, FaceMorpher 0.747.
- S4 vs S3: OpenCV 0.734, FaceMorpher 0.640.
- landmark_combined: 0.783.

G1 seed-mean legs (SE − Sb, 95% bootstrap):

| Leg | Value | Bar |
|---|---|---|
| landmark_combined AUC | +0.016 [+0.006, +0.026] | ≥ −0.02 |
| landmark_combined miss | −0.037 [−0.053, −0.020] | ≤ +0.05 |
| R4 miss, OpenCV (SE mean) | 0.048 [0.018, 0.083] | ≤ 0.05 |
| R4 miss, FaceMorpher (SE mean) | 0.003 | ≤ 0.05 |
| S4 miss | −0.033 [−0.088, +0.018] | ≤ +0.05 |

### Storage (MS1 FFHQ hold-out; Δf = stored minus native flag share, Δm in genuine SD)

| Network | fm61 Δf | fm61 Δm | amsl112 Δf | amsl112 Δm |
|---|---|---|---|---|
| A | +0.351 / +0.265 / +0.381 / +0.275 | +1.10 / +1.13 / +1.25 / +0.96 | +0.152 / +0.066 / +0.107 / +0.062 | +0.40 / +0.29 / +0.31 / +0.19 |
| Sb | +0.027 / +0.003 / +0.048 / +0.007 | −0.05 / −0.17 / +0.02 / −0.09 | +0.010 / +0.003 / +0.024 / 0.000 | −0.05 / −0.12 / −0.03 / −0.07 |
| SE | +0.014 / +0.017 / +0.041 / +0.003 | −0.10 / −0.16 / +0.02 / −0.13 | 0.000 / −0.003 / +0.021 / 0.000 | −0.08 / −0.12 / −0.03 / −0.07 |

- Morph shift Δm_att for SE: −0.025 to +0.026 (fm61), −0.022 to +0.009 (amsl112).
- At amsl112, SE and Sb pass on seeds 408 and 410 and fail on 409 and 411. The failing seeds have |Δm| above one third of A's Δm (A: 0.29 and 0.19).

### Camera photos (flag rate)

| Pool | A | Sb | SE |
|---|---|---|---|
| Development R0 | 0.00 (all) | 0.00 (all) | 0.00 (all) |
| AF0 development photos | 0.008 / 0 / 0 / 0 | 0 (all) | 0 (all) |
| FFHQ ffhq_bona_orig | 0.182 / 0.086 / 0.123 / 0.115 | 0.045 / 0.075 / 0.102 / 0.187 | 0.087 / 0.110 / 0.103 / 0.164 |
| MS1 native | 0.137 / 0.070 / 0.107 / 0.087 | 0.043 / 0.073 / 0.087 / 0.143 | 0.103 / 0.093 / 0.107 / 0.133 |

Relative legs, seed means of SE − Sb (bar ≤ +0.02):
- FFHQ: +0.013 [+0.003, +0.023], met.
- MS1 native: +0.023 [−0.003, +0.050], inconclusive.

## Post hoc descriptive readings (not registered; results-reviewer, recomputed from the tars)

- **Operating point, not a better ranking.** Most of the R3 drop is a shift of the operating point within the ladder.
  - R4-vs-R3 AUC rises only from 0.880–0.912 to 0.911–0.926.
  - SE's R4 lower tail falls: 5th-percentile logit +3.21 (Sb) to +0.19 (SE).
  - At a threshold that gives Sb SE's R4 miss, Sb flags R3 at 0.38 / 0.34 / 0.30 / 0.28, close to SE's 0.32 / 0.26 / 0.25 / 0.27.
  - At a threshold matching the landmark_combined miss, Sb flags R3 at 0.82–0.94. So SE separates ladder same-person full-frame blends from FFHQ landmark morphs, but not better from ladder two-person morphs.
- **Residual flags are a property of the host.**
  - Development R3: 23 hosts are flagged on 4 of 4 seeds and 68 on 0 of 4.
  - Host order is stable: Spearman SE vs Sb 0.83; OpenCV vs FaceMorpher 0.97; R3 vs S3 0.67.
  - Training rows show the same pattern: 26 of 156 lad_R3 and 35 of 156 lad_S3 rows are flagged on all 4 seeds. Training flags (lad_S3 0.30–0.39, lad_R3 0.22–0.27) are close to development flags.
  - So this is a fit limit or a label conflict on a stable subset, not a failure to generalise.
- **Mirror route.**
  - R3-vs-R3m AUC: SE 0.76–0.80, Sb 0.33–0.36.
  - At the matched-R4 threshold, Sb still flags R3m at 0.45–0.65; SE flags 0.00–0.01.
  - 674 of the 830 new negatives are mirror-symmetric. The R3m and self-morph numbers are not evidence about identity.
- **G1 improved rather than failed.** The trade-off the strategist predicted was not tested, because the target was not reached. Do not read G1 as "identity learned at no cost".
- **Storage claim on fresh seeds.** Sb's amsl112 storage pass does not replicate on these fresh A100 seeds (2 of 4, rule shape as above). AB1's H100 read also gives Sb "inconclusive, no claim" for C2P. The paper must state this when describing the freeze basis.

## Printed only

- **Platform reproduction check** (precision and GPU together; FS1 Sb seed 403 rescored on the 6,339 gate rows), the same on all four leases:
  - 99th percentile |Δlogit| 0.0071, maximum 0.0177, own-rule agreement 1.000;
  - the C2P gate is passed: "reproduces FS1 scores (precision and GPU together)".
- **FS1 Sb (A100, seeds 403–407) beside the refit Sb:**
  - development S3: 0.31–0.41 (refit 0.36–0.41);
  - R3: 0.83–0.91 (refit 0.83–0.90);
  - R3m: 0.93–0.96 (refit 0.93–0.96).

## Not verified / limitations

- The H100 block (amendment SE1-A1, WCSS array 6312894) has not run yet. It is read separately, after AB1's read, by 14 Nov 18:00.
- The mirror self-morphs are left-right symmetric. SE flags 0–3% of development mirror self-morphs but 25–32% of non-mirror same-person morphs (disclosed before the read, prereg section 10).
- The first run of the reader stopped at load time (a KeyError on the training-score file) before computing anything. It was fixed and committed before the read (prereg note).
- Every number is development data. None is a benchmark result.

Files:
- `se1_read.json`;
- tars in `/mnt/t7/smad_next/SE1/results/`, with copies in `/home/narolski/se1_results_copy/`;
- platform-check tars in `/mnt/t7/smad_next/SE1/smoke_se1{a,b,c,d}/`.

## Notes after the read

- **Wording deviation (lead, 13 Nov 17:25):** the section 8 sentence above replaces the registered sentence "Same-person blends as negatives did not change the same-person flags at this dose". The registered sentence would be false for same-person full-frame morphs. Verdicts are unchanged.
- **Author's ruling (13 Nov 17:15):** cluster waits may go past the experiment-stage cut-off. The H100 block's read deadline (now 14 Nov 18:00) will be moved accordingly, by a dated amendment before any H100 SE tar exists, when the dispatcher asks.

- Time correction (`date`: Fri Nov 13 18:48 CET 2026; nothing else changes): the lead's message gave times written from memory, about 45 min ahead (NOTEBOOK, "13 Nov 2026, 18:46 machine clock (lead): CORRECTION OF TIMES"). The wording approval cited above as "17:25" came before this file's commit 1b8b120, git time 13 Nov 17:14:04. The author's cut-off ruling cited as "17:15" is about 17:11 by the machine clock (the lead's message said 17:15). No rule, verdict or deadline changes.
