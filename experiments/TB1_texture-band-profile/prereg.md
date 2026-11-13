# Texture band profile, two people against one (TB1): registration

Owner: PR1/BD1 owner agent (Opus), on the lead's assignment of 13 Nov 2026. It is built from the IDEAS test draft
`experiments/IDEAS_mechanism-ledger/TEST_texture-band-profile.md` at commit c17ac7d (sha256 `e542490f…`; ledger
entry M2). Registered at the git commit that adds this file. Before that commit, the only computations were:
- a 6-host code test of `src/TB1/tb1_measure.py` (`tb1_feats_limit6.csv`, not looked at);
- mock runs of the reader on random features. These printed the cue-only S4-vs-S3 27-statistic floor on real cues.

Development data only. Nothing enters the frozen method.

**Lead's ruling (13 Nov, in substance).** "FFT band statistics computed in memory are measurements like the existing
hand-made statistics (AS0 precedent), not image operations. No filtered image is stored as data or fed to training."

## 1. Question and hypothesis

- **H-TB1.** At equal blend energy, the difference between two people's warped faces is distributed over spatial
  frequency differently from the difference between two sessions of one person, and a single image shows it.
- **If no,** texture or skin-statistics mechanisms for a second identity are closed at this resolution, and BD1's
  residual beyond D is something other than texture.

## 2. Rows and the half-differences (no image is built)

- **Hosts.** The 291 BD1 hosts (191 test, 100 development; FRGC 235, colorFERET 56), with the FS1 evaluation frames.
- **Deviation from the draft: no warped halves are rebuilt.** As built (AR1 amendment 7b), a splice equals its
  counterpart outside the hull and equals the 50% OpenCV-style morph inside. So S4 − R2w4 = 0.5 (B_w − H_w) inside the
  hull for the two-person case, and S3 − R2w = 0.5 (S_w − H_w) for the same-person case. The half-difference of the
  draft is therefore available from existing images. Equality outside the hull is asserted in the code.
- **Single-image rows:** S4, S3, S0, R2w4, all with the amendment-7b hull from mean(H, B); R0 and R0_61 (stored
  small), with the hull of H's own landmarks. Outer ring: 3 × 3 dilations of the hull until the ring is at least as
  large as the hull.

## 3. Measurement (`src/TB1/tb1_measure.py`, DGX CPU)

- Luminance Y. AS0's octave bands B1-B5 (`as0_measure.band_weights`, imported unchanged), at the ar1_512 nominal IOD
  of 130.51 px (AS0 `iod_nominal.json`). One FFT of the whole frame.
- **P (premise):** E_k = Σ over the hull of b_k(d)², p_k = E_k / Σ E (independent of total energy).
- **S (single image):** r_k = ln(mean over the hull of b_k(Y)² / the same over the ring). This cancels the storage
  history and noise level the two regions share.

## 4. Reads (`src/TB1/tb1_read.py`) and rule

- **P.** Cross-fitted logistic regression on ln p_1..p_5 (5 host folds, `default_rng(20261171)`; the S4 and S3 rows of
  a host share a fold), two-person against same-person half-differences.
  - Out-of-fold AUC overall, and within quintiles of D (primary), D_lin and G (strata with ≥ 10 of each class),
    each beside its pure reference (the statistic alone).
  - Host-bootstrap interval for the within-D AUC.
  - Printed: by database, and within joint D-tertile × G-half strata.
- **S.** The same cross-fitted logistic on r_1..r_5: S4 vs S3, within D quintiles.
  - Controls (same model): R0_61 vs R0, S0 vs R0, R2w4 vs R0, each of which must be ≤ 0.58.
- **Floor.** The best single 27-statistic cue on S4 vs S3, chosen on one host half and scored on the other. The
  ADVERSARY floor is added beside it when published; the read waits if it is announced as pending.
- **Increment.** Per Sb seed 403-407 (stored development scores): out-of-fold AUC of [Sb logit, r] against
  [Sb logit], S4 vs S3.

**Outcome table (fixed now; draft thresholds unchanged):**

| P within D | S within D | S controls | Reading | Next |
|---|---|---|---|---|
| ≥ 0.70 | ≥ 0.65 | all ≤ 0.58 | a two-person texture trace exists and one image shows it | if the increment is ≥ +0.03 on ≥ 4 of 5 seeds: an arm with same-person blends at matched D plus a band-profile target (post-freeze ablation) |
| ≥ 0.70 | < 0.65 | — | the trace exists but is too weak or masked in the composite | report as a measured fact; no arm |
| ≤ 0.62 | any | — | no texture-level second-identity trace beyond blend energy | close M2; BD1's residual is not texture |
| any | any | a control > 0.58 | storage, seam or warp reads as the trace | closed unless stratifiable |

Otherwise "inconclusive (no row of the outcome table)".

**Deviation from the draft: one read of all 291 hosts.** The draft read development hosts first and test hosts once.
Here every rule is fixed before any value, so there is nothing to tune in between. Development and test values are
printed separately.

## 5. Cost and commands

- About 2 minutes of DGX CPU.
- `OMP_NUM_THREADS=2 nice -n 10 .venv-spark/bin/python -I src/TB1/tb1_measure.py`, then
  `... src/TB1/tb1_read.py --out experiments/TB1_texture-band-profile/tb1_read.json`, run once.
- Pins in `src/TB1/SHA256SUMS`.

## 6. Risks (from the draft)

- The hull edge leaks into the low bands. AS0's band weights are reused, but its masking is not, because the masks
  differ.
- colorFERET sessions are further apart in time; the result is printed by database.
- "Equal D" is one-dimensional; joint D × G strata are printed.

## Amendment 1 (13 Nov, before any computation; pre-run check `PRERUN_RI1_TB1_20261113.md`, 3f9f136; lead's answers)

All fixes T1-T5 are in code and registered here before anything is computed (`src/TB1/tb1_measure.py`,
`src/TB1/tb1_read.py`, pins in `src/TB1/SHA256SUMS`; tested on 7 hosts and mock features).

The read is split by `--part`:
- **premise:** read after this amendment;
- **s** (S4 vs S3, its controls, floor, gain and increment): waits for ADVERSARY's floor commit (lead's hold).

The fixes:
- **T1.** Controls are scored by the S4-vs-S3 fold models (trained on the S4/S3 rows of the other folds) and scored
  out-of-fold by host. Each must lie in [0.42, 0.58]. Separately refitted control AUCs are printed as separability
  ceilings.
- **T2.**
  - **Binding controls:** R0_61 vs R0 (both on H's hull), R2w4 vs R2w (both on the amendment-7b hull; R2w is now
    measured on it), S0 vs R2w4 (same hull).
  - **Printed:** S0 vs R0, R2w4 vs R0, and S4 vs S3 within G quintiles.
- **T3.**
  - P: d is centred by its hull mean before the FFT. E_k is summed over the hull (primary) and over the hull eroded by
    16 px (printed; a mask operation only). P is also printed within D_dc quintiles.
  - S: r_k is also printed with a 16 px guard band either side of the hull edge. S4 vs S3 is also printed within
    quintiles of the seam tone step (|luma step|, `tone_splice.npz`).
- **T4 (binding, lead's answer 2).** The arm row also requires a cross-fitted gain of r of ≥ +0.03 on S4 vs S3, over a
  logistic of the 27 statistics plus the splice shortcut features (seam tone luma and R−G steps, log sharpness ratio).
  The cross-fitted 27-statistic logistic baseline is printed beside it.
- **T5.**
  - Row 3 now reads: "no band-profile difference of the luminance half-difference in AS0's five octave bands at equal
    D; other texture statistics are not tested". The old "BD1's residual is not texture" is withdrawn.
  - The controls row is applied first.
  - The Sb increment is printed on the 191 test hosts alone as well as on all 291 hosts.
- **D:** BD1's D, not D_ac.

## Logged before the single-image (S) part is read (13 Nov, from `REVIEW_TB1_PREMISE_20261113.md`, e7e57ed)

- **Reviewer's prediction for S:** in one image, the fine-band drop inside a 50% blend is mostly noise averaging, which
  an identity-free same-person blend has too. The binding gain of +0.03 over the splice shortcut features (including
  the inside/outside sharpness ratio) is the deciding row, and is expected to **fail**.
- **H-new-1** (the TB1 signal is the extra structured energy between two people diluting a fine-scale floor shared by
  both classes). Prediction: on FRGC, the profile within band-energy and W strata is ≤ 0.62. **Falsified** if the gain
  over [log E, log W] is ≥ +0.03 with a component-bootstrap lower bound above 0.
- **H-new-2** (TB1 measures face-shape mismatch, identity geometry, not skin texture). Prediction: same-person pairs at
  matched W score like two-person pairs (amendment 2 read (b); the clean test needs new warps, an author item).

## Amendment 2 (post hoc; labelled so; registered before reading, pre-run check requested from the lead)

Source: `REVIEW_TB1_PREMISE_20261113.md` (e7e57ed), lead's order of 13 Nov. The premise values and the reviewer's post
hoc numbers are known; every read below is post hoc. Code: `src/TB1/tb1_amend2.py` (pinned in `src/TB1/SHA256SUMS`),
tested on mock features only. Zero GPU. It reads the registered feature file, BD1's D, the AR1 pool and the .tem files.

- **E** = band-limited energy of the half-difference (P4_Etot / P3_Etot: B1-B5, hull). **W** = mean landmark
  displacement over the 106 points between the two source photos (H to B for two-person, H to S for same-person).
- **Folds and bootstrap** by connected components of the person graph (host-partner edges).
- **Reads:**
  - the profile (cross-fitted logistic on ln p_1..p_5) within E quintiles, within W quintiles, and within joint
    D × W tertile cells (cells with ≥ 10 of each class);
  - the gain of the profile over [log D, log E, log W] and over [log E, log W];
  - the component bootstrap of the second gain (2,000 draws, `default_rng(20261182)`).
- **Rule:**
  - **Falsified** ("the profile adds < +0.02 over band energy and geometry") if the gain over [log E, log W] is
    < +0.02.
  - **Supported** if ≥ +0.03 with a component-bootstrap lower bound > 0. Otherwise "inconclusive".
  - H-new-1 is falsified only in the supported case.
- **Descriptive (a): capture-day gap.** Gaps from the pool's session dates (host H_session; the partner photo B is the
  partner's S photo, S_session), so no sigset read is needed. Two-person rows are binned by host-partner day gap (0
  [same day], 1-30, 31-180, > 180) against same-person rows in the same bins, per database. AUC where both bins hold
  ≥ 5 rows.
- **Descriptive (b): matched W.** Same-person pairs with W at or above the two-person 10th percentile, matched 1:1 on W
  to two-person pairs (nearest, without replacement). AUC and n printed.
- **Not built:** the follow-up with new warps (same-person different-session halves from the NIST cross-encounter
  list, same-day two-person splices) is an author item.

## Amendment 2b: pre-run fixes for amendment 2 (`PRERUN_TB1_A2_20261113.md`, b7d611c; registered before the read)

- **F1, day gap.** Same-day pairs: n = 3 (FRGC) and 5 (colorFERET) two-person, and 0 same-person. The same-day
  comparison is therefore not computable; the counts are printed and no session claim is made. Bins with < 5 of either
  class print n only. Two-person same-day rows against all same-person rows of the database are printed as a labelled
  anecdote (n ≤ 8, no claim).
- **F2, matched W.** Pairs are matched 1:1, nearest on ln W, without replacement, with a caliper of 0.10 in ln W;
  unmatched pairs are dropped and counted. Printed: n matched, n dropped, mean |Δ ln W|, medians.
  - Descriptive only. With n ≈ 40 per side the AUC's SE is about 0.065, so the read can only say "consistent with
    H-new-2" (AUC ≤ 0.60) or "against H-new-2" (AUC ≥ 0.70); otherwise "not resolved".
  - No verdict on H-new-2 comes from (b).
- **F3, scope.** The rule is applied to all 291 hosts. FRGC-only values (the gain and the E, W and E × W strata) and
  joint E × W tertile cells (≥ 10 of each class) are printed as descriptive.
- **F4, mock run (answered truthfully).**
  - The mock used `/tmp/…/scratchpad/tb1_mockfeats2.csv`: synthetic features over the real 291 host ids and the real
    S4 / S3 row ids.
  - E was not real: P4_Etot and P3_Etot were set to 1, so log E was constant.
  - D (BD1 `d_values.csv`) and W (the .tem files) were real. The mock's E_alone, W_alone and D_alone AUCs and its
    [log E, log W] base AUC were written to the scratchpad JSON `tb1_a2_mock.json`. With E constant, that base was in
    effect a W-only fit on real W.
  - I did not open that JSON. The only printout I saw was the last four lines of stdout: the matched-W medians of the
    mock matching (W_two 6.52 px, W_same 6.50 px), which come from real W.
  - Since then, mock mode replaces E, D and W with random numbers.
  - The read is labelled accordingly: the W-only base value may have been computed in a file I did not view, and two
    matched-W medians were seen.
- **F5, bootstrap.** Failed bootstrap draws are counted and printed. If more than 1% of the 2,000 draws fail, the
  verdict is "inconclusive". The interval is a "95% percentile interval". The gain over five more fold seeds
  (20261183-20261187) is printed as a sensitivity check and binds nothing.
- **F6.** n_components differs from the review's 110, because partners outside the 291 hosts are graph nodes (shared B
  photos).
- **F7.** Within-strata AUCs are descriptive; coverage is printed; no rule uses them.

**Erratum to 2b F6 (13 Nov, after the read; results review `REVIEW_TB1_A2_20261113.md`).** F6 was wrong: counting the
partners outside the host set as nodes gives 110 components, the review's count. The JSON field `note_components`
(a hard-coded string in `tb1_amend2.py`) is superseded by this erratum. The registered output is not edited.

## Amendment 3 (13 Nov, before ADVERSARY's floor commit and before the S part is read; from the amendment-2 review)

The S part adds per-database prints, descriptive only: FRGC-only and colorFERET-only values of the S4-vs-S3 within-D
AUC, the binding-gain components (baseline, plus r, gain) and the three binding controls. The binding rule is
unchanged; it stays on all 291 hosts. Code: `src/TB1/tb1_read.py` (re-pinned).

## Operations note (13 Nov, after the adversary floors were pinned at 35f25a7 / pins_stage3; before this part is read)

The read prints the adversary's floors beside its own registered floor: the all-cue ADV floor, the non-F27/non-BLEND
floor and the floor's within-BD1-D-quintile values, through `check.exceeds` on the pinned files
(`src/PR1/adv_beside.py`). Contrasts: ri_S4_vs_S3, test_S4_vs_S3, dev_S4_vs_S3; for RI1 also ri_R4_vs_R3 and
ri_R4_vs_R0. Printed only. No registered rule changes.
