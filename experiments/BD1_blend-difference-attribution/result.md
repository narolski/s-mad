# Blend-difference attribution (BD1): result

Read once on 13 Nov 2026, about 18:10 CET. D for 873 splices was computed with `src/BD1/bd1_d.py`; the output is
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
