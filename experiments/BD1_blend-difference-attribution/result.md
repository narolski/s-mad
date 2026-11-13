# Blend-difference attribution (BD1): result

Read once on 13 Nov 2026 (read commit 83daa17, 17:57 CET). D for 873 splices was computed with `src/BD1/bd1_d.py`; the output is
`/mnt/t7/smad_next/BD1/d_values.csv`, sha256 `cf2ba3fa…`, and every splice equals its counterpart outside the hull
(asserted). The reader `src/BD1/bd1_read.py` (pins in `src/BD1/SHA256SUMS`, commit 9562302) wrote `bd1_read.json` and
`bd1_read_stdout.txt`. Registration: `prereg.md` (33bdee6) and amendment 1 (9562302), after the pre-run review
`experiments/reviews/PRERUN_BD1_20261113.md`. Development data only: 191 test hosts of our FRGC / colorFERET splice
ladder, OpenCV-style engine. Results review (Opus) `experiments/reviews/REVIEW_BD1_20261113.md`: accept with
corrections. D was recomputed for all 573 test rows (max |Δ| 0) and every AUC matched; the corrections are applied below.

## The measure

- Median D (0-255): two-person splice S4 12.85, same-person splice S3 10.22, seam-only S0 7.22.
- D alone separates S4 from S3 at 0.636 (direction-free).
- The pure-D reference is the stratified AUC of D itself, computed on the same rows with the same functions: 0.557
  over quintiles (coverage 1.00), 0.516 in the window version.
- ρ(D_S3, G) = −0.17, where G is the geometry gap between S3's inside and the hull.
- D by database is similar for FRGC and colorFERET hosts.

## Registered block (FS1, Sb seeds 403-407, A100)

| Seed | 403 | 404 | 405 | 406 | 407 |
|---|---|---|---|---|---|
| S4 vs S3, unstratified | 0.743 | 0.732 | 0.716 | 0.744 | 0.725 |
| S4 vs S3 within D quintiles (primary) | 0.729 | 0.716 | 0.697 | 0.724 | 0.713 |
| primary − pure-D reference | +0.172 | +0.159 | +0.140 | +0.167 | +0.156 |
| ρ(logit, D) within S3 | 0.316 | 0.372 | 0.359 | 0.389 | 0.406 |
| ρ(logit, D) within S0 (identity-free) | 0.042 | −0.021 | 0.008 | 0.034 | 0.008 |
| primary, 95% host-bootstrap interval | 0.680-0.769 | 0.669-0.763 | 0.647-0.741 | 0.678-0.769 | 0.665-0.755 |
| within D_int / D_band quintiles | 0.729 / 0.722 | 0.719 / 0.716 | 0.699 / 0.699 | 0.728 / 0.724 | 0.714 / 0.706 |

- ρ_P (D against the number of seeds that flag each S3 host) = 0.349. With D_int 0.339, D_band 0.393, D_Y 0.298;
  with G 0.082. 56 S3 hosts are flagged on all 5 seeds, 68 on at least 4.
- **Registered verdict: "fail: a residual beyond D (identity or content D misses)"**: primary − reference ≥ +0.12
  on 5 of 5 seeds. The pass branch is not met: the relative condition holds on 0 of 5 and ρ_P < 0.4. The within-S3
  co-condition (ρ ≥ 0.2) does hold on 5 of 5.
- A and B, printed: S4 vs S3 within D quintiles 0.513-0.560 (primary − reference −0.043 to +0.003); ρ within S3
  0.08-0.22.

## Replication blocks (read separately, never pooled; the same 382 test rows; AB1 and SE1 share seeds 408-411)

| Block | primary per seed | primary − reference | ρ within S3 | ρ_P | verdict |
|---|---|---|---|---|---|
| AB1 (H100, Sb 408-412) | 0.694, 0.709, 0.707, 0.712, 0.719 | +0.137 to +0.162 | 0.36-0.42 | 0.367 | fail (replicates) |
| SE1 (A100, Sb 408-411) | 0.696, 0.708, 0.710, 0.711 | +0.140 to +0.155 | 0.36-0.39 | 0.340 | fail (replicates, 4 of 4) |

"Replicates" means over fits and platforms, not over hosts.

## What the numbers say, within the registered wording

- **Registered:** at equal blend-difference magnitude D, Sb still ranks the two-person splice above the same-person
  splice: 0.70-0.73, against 0.56 for D alone.
  - The 95% host-bootstrap interval of the excess (reviewer, paired) is +0.07 to +0.26, so a pass is excluded. The
    +0.12 fail threshold is met on point estimates (primary intervals 0.65-0.77 in FS1, 0.65-0.76 in AB1 and SE1).
  - On the 74 hosts where the same-person splice has the larger D, Sb still ranks the two-person splice higher in
    57-65% of them. A detector that reads only D scores 0 there by construction.
- **Post hoc (reviewer), not registered:**
  - The separation lives inside the hull: face-blanked 0.48-0.50, background-blanked 0.66-0.75, from existing
    development scores of the blanked rows.
  - It survives stratification on mean colour shift, on colour-corrected difference energy and on a 7-statistic
    propensity (0.68-0.74). So colour or illumination shift between the two photos does not account for it. These
    statistics use the counterpart image; they are oracle diagnostics, not competing detectors.
  - Within same-person splices, Sb's logit rises as the face-recognition similarity of the host's two photos falls
    (existing glintr100 cosines in `AR1/pool.csv`; ρ −0.31 to −0.38 on 14 of 14 Sb networks; partial −0.17 to −0.25
    given D and the colour statistics). This is consistent with an identity-weighted appearance cue but does not
    show one. FR cosine also moves with pose, illumination and age.
- Sb's logits rise with D within same-person splices (ρ 0.32-0.42) but not within seam-only images S0 (ρ ≈ 0). S0 is
  a trained negative with logits at the floor (SD 0.1-0.5 against 2.5-2.7 for S3), and its D is warp disagreement
  with almost no colour shift. The S0 null therefore does not show that the response to D needs blended content.
- Sb was trained on exactly this contrast (430 S4 positives; 156 S3 and 156 S0 negatives). The residual on unseen
  hosts is generalisation within the construction (one engine), not across engines or sources. A and B, which saw
  no splices, show no residual (≤ +0.003); this is expected and is not a mechanism control.

## Not verified / limits

- One engine, one splice construction, the same 191 hosts in every block.
- D partly carries identity by construction (pre-run F2). The existing glintr100 cosines of the source photos
  (`pool.csv`) allow a registered identity-similarity read without new inference (proposed as BD1b, on development
  hosts).
- For the strategist's next step (a difference-matched splice arm): BD1 licenses only "a residual inside the hull at
  equal D". With the post hoc FR-similarity reading, it points the arm at appearance and FR similarity, not at D. The
  existing pool has no overlap in FR cosine (S4 0.14-0.35, S3 0.77-0.93), so matching on identity needs new
  look-alike morphs (an author item). A "dissimilar-session S3" selection (low cos_HS) can be built from existing
  files. The arm stays post-freeze and ablation-only.

## Amendments 2-3: development-host follow-ups (registered at 7697fbf and 23266fb; read once at about 18:25 CET)

Results review (Opus) `experiments/reviews/REVIEW_BD1_AMEND2_20261113.md`: accept with corrections. All values were recomputed and matched; the corrections are applied below.

Features: `/mnt/t7/smad_next/BD1/d_feats.csv`, sha256 `7391328e…`. Reader: `src/BD1/bd1b_read.py`. Output:
`bd1b_read.json` and `bd1b_read_stdout.txt`. Development data only. Development hosts: 100 (81 FRGC, 19 colorFERET).
Seeds share the same hosts, so "4 of 5 seeds" is close to one draw.

| Read | FS1 (Sb 403-407; decides) | AB1 (H100, 408-412) | SE1 (A100, 408-411) |
|---|---|---|---|
| H1: partial ρ(S3 logit, cos_HS ∣ D, D_lin, D_dc, database) | −0.183, −0.259, −0.149, −0.248, −0.259 → **supported** | −0.17 to −0.22 → supported | −0.16 to −0.22 → supported |
| H2: S4 vs S3 within D_dc quintiles, minus own reference (0.496) | +0.25 to +0.29 → **residual beyond this colour statistic** | +0.23 to +0.28 → same | +0.23 to +0.27 → same |
| H2: within D_lin quintiles, minus own reference (0.584) | +0.13 to +0.20 → **residual beyond this colour statistic** | +0.12 to +0.17 → same | +0.12 to +0.17 → same |
| H4: gain of Sb's logit over the 7-statistic propensity (0.741; SD over 20 splits 0.004-0.006) | +0.059 to +0.066 → **supported** | +0.034 to +0.089 → supported | +0.033 to +0.089 → supported |
| Session gap: stratified partial ρ (∣ cos_HS, D, D_dc, database), 291 hosts | −0.022 to +0.036 → **falsified** | −0.034 to +0.003 → falsified | −0.035 to +0.003 → falsified |
| Blanked rows (post hoc formalisation): inside / outside only | 0.651-0.761 / 0.482-0.518 → **inside-only signal; outside read non-diagnostic** | 0.713-0.760 / 0.483-0.495 → same | 0.713-0.762 / 0.483-0.495 → same |

- **H1 is supported by the registered rule** (point estimates −0.15 to −0.26 on 5 of 5 FS1 seeds).
  - Seeds share the hosts and rank them almost identically (ρ 0.87-0.95), so this is one sample of 100 hosts.
  - The seed-averaged partial is −0.23 (95% host interval −0.42 to −0.01; reviewer).
  - Per-seed intervals: FS1 403 [−0.39, +0.04], 404 [−0.45, −0.05], 405 [−0.37, +0.07], 406 [−0.44, −0.04],
    407 [−0.46, −0.03]. They include or reach 0 on most AB1 and SE1 seeds.
  - The direction and size reproduce the post hoc test-host value on new hosts.
  - The effect does not weaken when geometry and all difference statistics are added as covariates (−0.21 to −0.30;
    reviewer). Within S3, cos_HS correlates with D_ac at −0.57 and with D_lin at −0.51.
- Development S4 vs S3 for Sb, unstratified: 0.781-0.816 (known before). Within D_dc quintiles: 0.74-0.79. Within
  D_lin: 0.72-0.78.
  - The D_dc verdict follows almost entirely from the known development AUC, because D_dc has no within-stratum signal
    of its own.
  - The D_lin verdict (+0.12 to +0.20) is the informative colour control. Both are one-dimensional stratifications;
    the joint control is H4.
- H4: Sb's logit adds +0.06 AUC to a cross-fitted linear model of 7 oracle difference statistics, so Sb is not a
  linear read of these statistics. A non-linear model of them was not tested. Sb alone (0.78-0.82) exceeds that
  oracle (0.741).
- Session gap per database (descriptive): FRGC partial +0.004 to +0.067; colorFERET −0.10 to +0.04 (n = 56, wide
  intervals). The raw FRGC ρ is +0.10 to +0.16, as expected through cos_HS alone.
- Blanked rows:
  - Face-blanked rows (outside only) are flagged 0-5% in both classes, with logit SD 0.45-0.92. Inside-only rows are
    flagged 88-100% in both classes.
  - So the outside-only read is non-diagnostic ("no outside-only signal").
  - Correction: inside-only (background-blanked) rows are mostly flagged in both classes (S4 0.88-1.00, S3 0.62-1.00
    across blocks), so they do not separate at the own rule. Their ranking does (0.65-0.76): two-person logits sit at
    a ceiling (SD 0.2-0.4 in FS1) and part of the same-person rows fall below it.
  - These rows are out of distribution. This is a post hoc ranking observation, not evidence that a deployable cue
    lives inside the face. FS1 seed 405's 0.6506 is at the bar; the verdict holds on 4 of 5 either way.
  - The inside-only contrast still carries S3's hull/geometry mismatch.
- **Outcome-table action (amendment 3), H1 supported and H2 "residual beyond colour":** FR similarity of the host's
  two photos is a candidate control at equal blend energy and colour; it also tracks pose, illumination and age.
  - A later arm matched on FR similarity needs two-person and same-person pairs that overlap in FR similarity. The
    existing pools cannot supply them: 2 cross-person pairs above 0.6 among 536 persons, against a same-person range
    of 0.77-0.93. New look-alike morphs from a much larger person pool are an author item.
  - Session gap adds nothing beyond FR similarity. Without the cos_HS covariate the FS1 partial is +0.03 to +0.08
    (ρ(gap, cos_HS) −0.45 on the development hosts). An arm that matches on FR similarity needs no separate gap
    matching; an arm that does not match on it should not assume the gap is harmless.
- **What BD1 licenses:** BD1 supports no training arm before the freeze. It ranks a future FR-matched look-alike arm
  (an author item; new morphs from a much larger person pool needed) above a colour-matched rescore, which BD1's
  colour controls do not motivate. Before the freeze, at most a registered zero-GPU descriptive read of low-cos_HS
  same-person splices from the existing files.

## Amendment 4: least- against most-similar same-person splices (descriptive, post hoc; registered at 1cd0304; read once)

All 291 development and test S3 hosts were split into quintiles of cos_HS, with edges 0.834 and 0.903 (59 hosts
each). Output: `bd1c_read.json`, `bd1c_read_stdout.txt`.

| | Bottom quintile (least similar) | Top quintile (most similar) |
|---|---|---|
| Databases (FRGC / colorFERET) | 37 / 22 | 53 / 6 |
| Median D / D_dc / D_lin | 13.0 / 10.2 / 6.5 | 6.4 / 4.3 / 4.4 |
| Sb S3 flags, FS1 seeds 403-407 | 0.56-0.75 | 0.17-0.27 |
| AUC(S4 vs these S3), FS1 | 0.58-0.64 | 0.84-0.87 |
| Sb S3 flags, AB1 / SE1 | 0.64-0.73 / 0.68-0.71 | 0.22-0.31 / 0.25-0.31 |
| AUC(S4 vs these S3), AB1 / SE1 | 0.60-0.64 / 0.59-0.64 | 0.83-0.87 / 0.83-0.87 |

- Least-similar same-person splices are flagged 2.2 to 3.4 times as often as the most similar (per seed, all three
  blocks). They are ranked much closer to the two-person splices: AUC(S4 vs S3) 0.58-0.64, against 0.83-0.87.
- The bottom quintile also has about twice the median D and D_dc (13.0 / 10.2 against 6.4 / 4.3). It holds 22 of the
  56 colorFERET hosts, against 6 in the top quintile. So cos_HS, D and database are not separated here.
- The gap also appears within each database (reviewer, not registered). In FS1, bottom against top flag rates are
  0.49-0.70 against 0.17-0.28 within FRGC, and 0.68-0.82 against 0.17 within colorFERET. It cannot be attributed to
  cos_HS rather than to D, because the two move together.
- Descriptive only; decides nothing. Seeds share hosts, so the per-seed ranges are not independent replications.
  Review: `experiments/reviews/REVIEW_BD1_AMEND4_20261113.md` (accept with corrections, applied).
