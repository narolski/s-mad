# Blend-difference attribution (BD1): result

Read once on 13 Nov 2026, about 18:10 CET. D for 873 splices was computed with `src/BD1/bd1_d.py`; the output is
`/mnt/t7/smad_next/BD1/d_values.csv`, sha256 `cf2ba3fa…`, and every splice equals its counterpart outside the hull
(asserted). The reader `src/BD1/bd1_read.py` (pins in `src/BD1/SHA256SUMS`, commit 9562302) wrote `bd1_read.json` and
`bd1_read_stdout.txt`. Registration: `prereg.md` (33bdee6) and amendment 1 (9562302), after the pre-run review
`experiments/reviews/PRERUN_BD1_20261113.md`. Development data only: 191 test hosts of our FRGC / colorFERET splice
ladder, OpenCV-style engine. Owner's reading; results review pending.

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

- At equal blend-difference energy D, Sb still ranks the two-person splice above the same-person splice (0.70-0.73
  against 0.56 for a detector that reads D alone). The unstratified 0.72-0.74 falls by only 0.01-0.02 under
  stratification. This holds in three blocks and on interior-only and band-only D.
- Sb's logits do rise with D within same-person splices (ρ 0.32-0.42), but not within seam-only images S0 (ρ about 0).
  The response to D needs blended face content, not geometry alone.
- The residual is "identity or content D misses". This read does not show that it is identity. D is one pixel-level
  magnitude, and texture, colour or capture differences between the two photos are not separated from identity.
- A and B show no residual (≤ +0.003).

## Not verified / limits

- One engine, one splice construction, the same 191 hosts in every block.
- D partly carries identity by construction (pre-run F2). A finer identity-free contrast would need, for example, an
  ArcFace similarity covariate, which would require the lead's approval.
- Strategist's consequence of a fail: "the only lead toward real second-identity training (a difference-matched splice
  arm, post-freeze)". This is not run here.
