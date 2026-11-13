# Blend-difference attribution (BD1): registration

Owner: PR1 owner agent (Opus), on the lead's request of 13 Nov 2026, 17:55. Source:
`experiments/reviews/STRATEGIST_EVENING_20261113.md`, section 3, experiment 1. Zero GPU. Development data only.
Registered at the git commit that adds this file, before any D value of the 582 splices is computed or seen. The only
D values computed before this commit are 8 rows of a code test (`/mnt/t7/smad_next/BD1/d_values_limit8.csv`), not
looked at.

## 1. Question and hypothesis

- **Hypothesis H-BD1 (blend energy, not identity):** the candidate network Sb reads the blend-difference energy D
  inside the face, not a second identity. Within narrow bands of D, Sb does not separate the two-person splice (S4)
  from the same-person splice (S3). The same-person splices Sb keeps flagging across seeds are those with high D.
- **Alternative (identity residual):** at equal D, Sb still ranks S4 above S3.
- What each outcome changes (strategist): a pass gives a mechanism sentence for SE1, the AB1 trade-off and SM1. A
  fail is the only lead toward real second-identity training (a difference-matched splice arm, after the freeze).

## 2. Data and the measure D

- **Splices (OpenCV-style engine only, the one Sb trained on):** S4 and S3 of the FS1 evaluation list
  (`/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv`, sha256 `f0f29f22…`). Test hosts (191 S4 + 191
  S3, the same 191 hosts) decide; development hosts (100 + 100) are printed.
- **How the files were built** (AR1 `src/AR1/splice.py`, amendment 7b, job7b; checked before registration). S4 =
  R2w4 (warp-only toward the two-person mean shape) with R4 pixels copied inside one hull. S3 = R2w (warp-only toward
  the same-person mean shape) with R3 pixels inside the same hull, made from mean(H, B) landmarks, the R4 geometry.
  The counterpart of S4 is therefore R2w4 and that of S3 is R2w. The strategist wrote "S − R2w4" for both, which is
  corrected here to each splice's own outside image. A check before registration found all 582 splices, their
  counterparts, R3/R4 sources and .tem files present (0 missing). Outside the hull, S4 equals R2w4 exactly; S3 equals
  R2w exactly with the amendment-7b hull.
- **D** (`src/BD1/bd1_d.py`): mean over hull pixels and the 3 channels of |S − counterpart| on the stored 512 px PNGs
  (0-255). The hull is rebuilt with AR1's `splice.hull`, imported unchanged. It is asserted that S equals its
  counterpart outside the hull, otherwise the run stops. Printed: D_Y (the same on luma) and the hull size. No new
  image operation: subtraction of existing images only.

## 3. Blocks (each read separately, never pooled)

| Block | Networks | Platform | Role |
|---|---|---|---|
| FS1 | Sb seeds 403-407 (A and B printed beside, no rule) | A100 PCIe (pn1fs), stored scores | **registered** |
| AB1 | Sb seeds 408-412 (`/mnt/t7/smad_next/AB1/results/AB1_Sb_s*.tar`) | H100 (WCSS) | replication |
| SE1 | Sb seeds 408-411 (`/mnt/t7/smad_next/SE1/results/SE1_Sb_s*.tar`) | A100 (rented) | replication |

- Scores come from each tar's `scores_eval.npz` after a sha256 check against its `.sha256`. Checked before
  registration (row ids only, no logits): the AB1 and SE1 Sb tars hold all 582 S3/S4 ids. Their evaluation manifests
  differ from FS1's (sha256 `93a5ba23…`, `6dcef964…`) because of overlays. The reader uses the FS1 ids and paths. A tar
  that is missing, off its pin or lacking a row counts as not meeting a condition (denominator kept).
- Known before registration: Sb's unstratified test S4-vs-S3 AUC on FS1, 0.716-0.744 (PR1 part 1), and its
  lapvar-stratified version 0.71-0.75. The AB1 and SE1 values of this contrast have not been looked at by this
  owner.

## 4. Reads and rule

Per Sb network, test hosts:
- **Primary statistic: D-stratified AUC(S4 vs S3).** Quintile edges of log D over the pooled 382 rows. AUC within
  each stratum. Mean weighted by n_pos × n_neg over strata with ≥ 10 rows of each class. Readable if those strata
  hold ≥ 50% of the 382 rows.
  - Fallback, fixed now, used only if a seed is not readable by quintiles: D-window matched AUC. All (S4 i, S3 j)
    pairs whose pooled D percentile ranks differ by ≤ 0.05. Readable if ≥ 1,000 pairs.
  - A seed readable by neither counts as not meeting any condition.
  - Interval: 2,000 host bootstrap draws (`default_rng(20261151)`), printed.
- **Persistence:** for the 191 test S3 hosts, k(h) = the number of the block's Sb seeds that flag h at the own rule
  (logit > 0). ρ_P = Spearman(D, k) over the 191 hosts, one value per block.
- **Rule per block** (n = 5 seeds; SE1 n = 4, where "4 of 5" reads "4 of 4"):
  - **PASS, "blend-difference energy explains":** primary ≤ 0.62 on ≥ 4 seeds AND ρ_P ≥ 0.4.
  - **FAIL, "identity residual":** primary ≥ 0.70 on ≥ 4 seeds.
  - Otherwise **"inconclusive"**. That includes primary ≤ 0.62 with ρ_P < 0.4.
  - The FS1 block decides. AB1 and SE1 are reported as "replicates" or "does not replicate" the FS1 verdict.
- **Printed:**
  - D alone as a classifier of S4 vs S3 (direction-free AUC);
  - unstratified AUC; per-seed ρ(logit, D) within S3 and within S4;
  - development-host versions;
  - the number of S3 hosts flagged on all (or all but one) seeds;
  - the same reads for A and B of the FS1 block (no rule);
  - D_Y and hull sizes.
- **Not claimed:** no identity claim from a pass or a fail beyond the sentence of the verdict. A pass does not show
  that D is the cause, only that D accounts for the ranking within this contrast. One engine (OpenCV-style). Splice
  hosts only.

## 5. Code, commands, review

- `src/BD1/bd1_d.py` (D), `src/BD1/bd1_read.py` (reader). Pins are in `src/BD1/SHA256SUMS`, committed with this file.
  The reader was tested on mock data only (random logits and random D over the true ids).
- Run once, after the pre-run review fixes:
  `OMP_NUM_THREADS=2 nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/BD1/bd1_d.py`
  then `... -I src/BD1/bd1_read.py --out experiments/BD1_blend-difference-attribution/bd1_read.json`.
- Pre-run review: experiment-reviewer (Opus) on this registration. Blockers and majors are fixed in a dated
  amendment before any computation.

## Amendment 1: pre-run review fixes (`experiments/reviews/PRERUN_BD1_20261113.md`, GO WITH FIXES; registered before any D of the full set or any S3/S4/S0 logit is computed)

Times corrected: the registration commit 33bdee6 is at 17:49:13 CET. The lead's message was stamped 17:55 by the lead
and arrived before that commit. The README's "18:00-18:20" should read about 17:35-17:50. The code tests wrote 8 and 9
rows of D (`d_values_limit8.csv`, `d_values_limit9.csv`); they were not looked at.
- **F1, pure-D reference and a relative rule.** A detector that reads only D keeps an AUC above 0.5 inside quintile
  strata. The reviewer's simulation gives 0.57-0.71 as the AUC of D alone rises from 0.76 to 0.96. So the rule is
  set against a reference: the same stratified (or window) AUC computed with D itself as the score, on the same rows
  and the same functions. The reference matches each seed's primary kind.
  - **PASS, renamed "no S4-vs-S3 signal beyond pixel-difference magnitude D":** primary − reference ≤ +0.05 on ≥ 4
    seeds, AND ρ(logit, D) within test S3 ≥ 0.2 on ≥ 4 seeds (Sb responds to D where no second person exists), AND
    ρ_P ≥ 0.4.
  - **FAIL, renamed "a residual beyond D (identity or content D misses)":** primary − reference ≥ +0.12 on ≥ 4 seeds.
  - Otherwise "inconclusive". Thresholds are fixed now, before any value is seen. SE1: 4 of 4.
- **F2, D partly carries identity.** For S4, D ≈ half the pixel difference between two persons. A pass therefore
  means only what its new name says, not "not identity". Identity-free controls are printed:
  - S0 rows (R2w4 outside, R2w inside the same hull, one photo, geometry only; 191 test, 100 development, scored in
    the same tars): D_S0 against R2w4, ρ(logit, D) within S0, and S0 flags;
  - ρ(logit, D) within S3, now a registered co-condition (above).
- **F3, the hull does not fit S3's geometry** (amendment-7b hull from mean(H, B); S3's inside follows mean(H, S)).
  Printed:
  - D_int, D on the hull eroded by 5 px (cv2.erode with an 11 × 11 ellipse; a mask operation, not an image
    operation);
  - D_band, the hull minus the interior;
  - for each: the stratified AUC, ρ within S3 and ρ_P;
  - G, the mean landmark distance between mean(H, S) and mean(H, B), with ρ(D_S3, G) and ρ(S3 logit, G);
  - D medians by host × partner database.
  - Answer to the review's question: Sb's 156 training S3 rows are the same amendment-7b builds (ids `sp2_S3_*`).
- **F4:** the mock no longer opens any tar.
- **F6:** D > 0 is asserted. ρ_P is None if k is constant. Hosts flagged on all seeds and on all but one are both
  printed. Bootstrap draws with quintile coverage < 0.5 are counted.
- **F7, wording:** all blocks use the same 382 test rows, and AB1 and SE1 share seeds 408-411. "Replicates" means over
  fits and platforms, not over hosts. A pass is worded "accounts for most of", never "explains".
- Not adopted now: an ArcFace identity-similarity covariate (a new model inference; needs the lead's approval).
