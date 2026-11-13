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

## Amendment 2: three zero-GPU follow-ups (lead's go, 13 Nov 18:10; registered before computing)

Source: `REVIEW_BD1_20261113.md`. Blocks as before: FS1 Sb 403-407 decides; AB1 (H100, 408-412) and SE1 (A100,
408-411; 4 of 4) replicate. They are read separately, never pooled, and "replicates" means over fits and platforms.
Known before this commit:
- the BD1 test-host results and the reviewer's post hoc test-host numbers;
- facts without scores, printed by the mock: the median H-to-S session gap is FRGC 49 days and colorFERET 274 days;
  ρ(gap, cos_HS) is FRGC −0.32 and colorFERET −0.15;
- the 9-row feature code test (`d_feats_limit9.csv`), not looked at.

No development-host logit of S3, S4 or the blanked rows has been computed by this owner for these reads.

New features (`src/BD1/bd1b_feat.py`; statistics only, nothing is written as an image), inside the amendment-7b hull,
with d = S − counterpart per channel:
- D_dc: mean colour shift;
- D_ac: the difference with that mean removed;
- D_lin: the residual after a per-channel least-squares gain and offset;
- D_grad: finite-difference energy of d.

Reader: `src/BD1/bd1b_read.py`.

### Part 1, BD1b: face-recognition similarity and colour on the 100 development hosts (S3 and S4 of the same hosts)

- **H1, FR similarity.** Partial Spearman ρ(S3 logit, cos_HS | D, D_lin, D_dc): ranks, with the covariates removed by
  linear regression on ranks. cos_HS is the existing glintr100 cosine of the host's two photos (`AR1/pool.csv`).
  - **Supported** if ≤ −0.10 on ≥ 4 seeds; **falsified** if > −0.05 on ≥ 3 seeds; otherwise "weak".
  - Printed: the raw ρ.
  - With n = 100, the standard error of one ρ is about 0.10. This is stated.
- **H2, colour strata.** For D_dc and D_lin separately: Sb's AUC(S4 vs S3) within quintiles of the statistic,
  minus that statistic's own pure reference, on the same rows and the same functions. A seed is readable if the
  strata hold ≥ 50% of the rows.
  - **"Residual beyond this colour statistic"** if ≥ +0.10 on ≥ 4 seeds; **"accounted for"** if ≤ +0.03 on ≥ 4;
    otherwise "inconclusive".
- **H4, Sb adds to simple statistics.** A propensity is fitted on 7 statistics (D, D_Y, D_int, D_band, D_dc, D_lin,
  D_grad), with logistic regression cross-fitted in 5 host-grouped folds (`default_rng(20261152)`). Its out-of-fold
  AUC is compared with the same model plus Sb's logit.
  - **Supported** if the gain is ≥ +0.03 on ≥ 4 seeds; **falsified** if < +0.01 on ≥ 4; otherwise "weak".
  - These statistics use the counterpart image: oracle diagnostics, not competing detectors.
- **What each outcome means for a later arm matched on FR similarity:**
  - H1 supported and H2 "residual beyond colour": the same-person flags follow appearance and FR dissimilarity at
    equal blend energy and colour. Matching on FR similarity is the right control for such an arm. Its training
    pairs must overlap in FR similarity, which needs new look-alike morphs (see below).
  - H1 falsified, or H2 "accounted for by colour": the test-host FR reading does not generalise to new hosts, or
    colour carries it. An FR-matched arm would then be matching on a variable the network does not use; a
    colour-matched control is the priority (an author item).
  - H4 falsified: Sb adds nothing beyond simple difference statistics on this contrast, so any arm should be judged
    first against that propensity.

### Part 2: session gap (S3 rows of all 291 development and test hosts, per database)

- gap = |S_session − H_session| in days (FERET yymmdd, FRGC ISO dates, from `pool.csv`). The S3 test logits are known,
  but the gap has not been related to any score.
- Per seed and database: ρ(S3 logit, gap). Printed: the same partial on cos_HS. Sizes: FRGC 235, colorFERET 56.
  - **Supported** if ρ > 0.15 in both databases on ≥ 4 seeds; **falsified** if ρ ≤ 0.05 in both on ≥ 4; otherwise
    "inconclusive".
- **Meaning for an FR-matched arm:** if supported, the time between sessions (ageing, capture change) drives
  same-person flags beyond FR similarity, and an arm must also match on session gap. If falsified, session gap
  needs no matching.

### Part 3: blanked-row addendum (development hosts decide; test hosts printed and labelled "seen post hoc")

- Inside only: AUC(S4_bg vs S3_bg), background blanked to grey 128 outside the hull. Outside only:
  AUC(S4_face vs S3_face), face blanked. These are the existing blanked rows, scored in every block's tar.
  - **"Residual inside the hull"** if inside ≥ 0.65 on ≥ 4 seeds AND outside ≤ 0.55 on ≥ 4.
  - **"Outside contributes"** if outside ≥ 0.60 on ≥ 4. Otherwise "inconclusive".
- **Meaning for an FR-matched arm:** if inside, the arm's matching and its controls can be restricted to the face
  region (the outside warp history is not the cue). If outside contributes, the arm must also match the outside
  warp (R2w4 against R2w).

### Look-alike pairs in the existing pools (fact, embeddings only, no score; `AR1/pool_src_emb.npz`)

- Among the 536 ladder persons (FRGC 427, colorFERET 109), cross-person cosines between one person's H photo and
  another's S photo exceed 0.6 for **2 pairs** (FRGC; 0 in colorFERET). They exceed 0.4 for only 4 pairs, with a
  maximum of 0.686.
- The same-person range is 0.70-0.94 (5-95%). Look-alike two-person morphs overlapping it cannot be built from these
  pools. They need a much larger person pool (thousands of identities, for example a development face set searched
  by FR similarity) or generated look-alikes, and then new morphs (warping: an author item).

## Amendment 3: pre-run fixes for amendment 2 (`experiments/reviews/PRERUN_BD1_AMEND2_20261113.md`, GO WITH FIXES; registered before computing)

**Times corrected.** The amendment-2 commit is 7697fbf at 18:07:01. The BD1 read commit 83daa17 is at 17:57:18; the
"about 18:10" in result.md is wrong. The same-person cos_HS range (5-95%) is 0.77-0.93, not 0.70-0.94.

**Known before this commit, added.**
- Development-host flag rates on the blanked rows for AB1 Sb 408-412 (`AB1 review_recompute.json`; for example
  Sb_408: S3_bg 0.93, S4_bg 0.99, S3_face 0.01, S4_face 0.01).
- The reviewer's blanked AUCs quoted in BD1 result.md.
- The development S4-vs-S3 AUCs, printed in PR1 Z1b-3 and BD1 (`auc_dev`, `strat_auc_dev`).
- The test-host link between S3 logit and cos_HS (reviewer, post hoc). Since ρ(D_dc, D) is 0.86, the H2 development
  values are partly predictable.

**Part 3 relabelled.** It formalises values already seen (post hoc); it is not a test. New rule for the outside read:
if both face-blanked classes are flagged ≤ 5% on ≥ 4 seeds, the outside read is "non-diagnostic", and the verdict is
"inside-only signal; outside-only read non-diagnostic". Printed: flag rates and logit SDs of all four blanked kinds.
Meaning, reworded: "no outside-only signal", never "the outside is not the cue". The inside-only contrast still carries
S3's hull/geometry mismatch (pre-run F3).

**Part 2 (session gap), primary changed.**
- Primary: a database-stratified partial correlation over all 291 hosts: ranks within database of the S3 logit and of
  the gap, with ranked-within-database cos_HS, D and D_dc and a database indicator removed.
- Supported if > 0.15 on ≥ 4 seeds; falsified if ≤ 0.05 on ≥ 4.
- Printed: per-database raw and partial values with host-bootstrap 95% intervals (2,000 draws). colorFERET (n = 56)
  is descriptive only.
- Seeds share the same hosts, so "4 of 5 seeds" is close to one draw; this is stated.

**Part 1.**
- H1's partial adds a database indicator and prints a host-bootstrap 95% interval. Its "falsified" outcome is worded
  "not replicated at n = 100" unless the interval excludes the test-host value.
- H4 averages the gain over 20 fold splits (`default_rng(20261152 + j)`, j = 0-19) and prints its SD.

**Robustness.** A missing row counts the seed as not meeting (assert inside the try). D_dc > 0 and D_lin > 0 are
asserted.

**Action for a later arm matched on face-recognition (FR) similarity, by outcome (replaces the meaning sentences of
amendment 2).**

| H1 (FR partial) | H2 (colour strata) | Action |
|---|---|---|
| supported | residual beyond colour | FR similarity is a candidate control (it also tracks pose, illumination, age). An arm needs pairs overlapping in FR similarity, which means new look-alike morphs (author item). |
| supported | accounted for / inconclusive | Colour and FR similarity are not separated. A colour-matched rescore (author item) comes before any FR-matched arm. |
| falsified ("not replicated at n = 100") or weak | any | There is no basis for an FR-matched arm from this read. A larger development set, or the colour route, comes first. |

- H4: if falsified, any arm is judged first against the 7-statistic propensity.
- Session gap: if supported, an arm matches on session gap as well; if falsified or inconclusive, it needs no gap
  matching on this evidence.

## Amendment 4 (lead's go, 13 Nov; one line, registered before computing): descriptive read of the least-similar same-person splices

Printed only, no rule, per block (FS1, AB1, SE1; never pooled). Over the 291 dev+test S3 hosts, take the bottom and
top quintiles of cos_HS (pooled edges). Print per Sb seed: own-rule S3 flag rate in each quintile; AUC(S4 vs S3)
using only the S3 rows of that quintile (all 291 S4 rows); the median D, D_dc and D_lin of each quintile; the number of
hosts per database in each quintile. Code `src/BD1/bd1c_read.py`; post hoc (the test S3 logits and the cos_HS link
are known).
