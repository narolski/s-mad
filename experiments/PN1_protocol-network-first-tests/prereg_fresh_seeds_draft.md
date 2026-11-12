# DRAFT v3 (not registered, nothing run): protocol network, fresh seeds for A, B and Sb with scale-free marks

v3 follows the batch-2 review `experiments/reviews/REVIEW_PN1_BATCH2_FZ2A12_AR1A11_20261112.md` (commit 88f6016),
section 5. It is the recommended plan. The earlier A/B/C plan (v2) is kept below as the alternative. Both go through the
pre-run reviewer before anything runs. Both also wait for the author's budget. Amendment 14 (draft
`prereg_amendment14_draft.md`) is meant to be read before this batch is registered.

## 1. Arms, seeds and why Sb

- **Arms and fits:**
  - A, B and Sb at seeds 403, 404, 405, 406 and 407 (15 fits), plus the replicate fit of A seed 401 (1 fit).
  - C is optional, at seeds 403 to 405 only (3 fits), if the author's budget allows. It is printed only and is not part of any primary contrast.
- **Recipe and pack:**
  - Unchanged recipe, last checkpoint.
  - Pack 2 (`266ce5c3…`): manifests A and B byte-equal to pack 1, and train_Sb (`2cf3fda3…`).
  - run.sh `a208fcf8…`, the pack-2 version with the Sb arm. A pack-1 run.sh cannot run Sb.
- **Selecting Sb complies with amendment 10.** The selection uses development-ladder reads only (`tier1_sb/sb_read.json`):

| Development-ladder read | Sb (seed 401 / 402) | B (seed 401 / 402) |
|---|---|---|
| face-only S0 vs S4 AUC (= face-only R2w vs R4) | 0.925 / 0.938 | 0.836 / 0.862 |
| S0 vs S4 excess over the 3-statistic floor, bootstrap lower bound | +0.049 / +0.051 | −0.294 / −0.283 |

  Sb's MAD22, H1 and test-ladder numbers (first-test data) did not enter the choice.

## 2. Platform

- **Two leases of one type,** A100-SXM4 40 GB, with GPU UUIDs recorded in every tar. Each seed runs whole on one machine:
  - machine 1: seeds 403, 405 and 407 (A, B, Sb), 9 fits;
  - machine 2: seeds 404 and 406, plus the replicate A seed 401, 7 fits (+ C 403 to 405, 3 fits, if included).
- **Replacement:** same type only, disclosed; the unfinished seed restarts from its first arm. If no same-type machine is available, the batch stops and the lead decides.
- **Replicate fit:** compared with pn1a's A seed 401 cell by cell. HN9 reads it: machine-driven if FFHQ own-rule genuine flags land outside 22.5 ± 3%, seed-driven if inside. It is never pooled as a seed.

| | Fits | A100-hours (69 min per fit + scoring) | Cost (0.59 USD/h) | Wall time (two leases) |
|---|---|---|---|---|
| A, B, Sb × 5 seeds + replicate | 16 | about 19.7 h | about 11.6 USD | about 11 h (machine 1 longer: 9 fits) |
| plus C at 3 seeds | 19 | about 23.4 h | about 13.8 USD | about 11.5 h (machine 2 then 10 fits) |

Scoring per fit: the pack-2 evaluation (with the splice rows), the HN2 list, the landmark_combined list of amendment 14 and the τ_multi list of the alternative (printed only). Plan v2 (A, B, C at 3 seeds) cost about 7.5 USD and 12.5 h serial on one lease.

## 3. Primary contrasts (fixed), fresh seeds only

The seed rule for every contrast:

| Outcome | Seeds meeting the contrast | Reading |
|---|---|---|
| Replicated | ≥ 4 of 5 | contrast replicated |
| Not replicated | ≤ 1 of 5 | contrast not replicated |
| Middle | 2 or 3 of 5 | inconclusive, no claim |

Under no effect with p = 0.5 per seed, "≥ 4 of 5" has probability 0.19, and 5 of 5 has 0.031 (printed beside).

1. **H1 (labelled "re-read": first-test data, already read for seeds 401 and 402).** Each seed counts if Sb − B ≥ +0.05 H1 AUC and Sb − A ≥ 0.
2. **FFHQ landmark_combined against its history-matched genuine pool (amendment-14 list).** Same rule: Sb − B ≥ +0.05 AUC and Sb − A ≥ 0. Stated: seeds 401 and 402 will already have been read on this list under amendment 14.
3. **Scale-free storage mark on FFHQ.**
   - The read: the share of the 2,000 FFHQ persons whose logit rises from native to history-matched (amendment-13 list, paired by key).
   - An arm passes on a seed if that share is ≤ 0.65.
   - Positive control: A must fail (share > 0.65) on ≥ 4 of 5 seeds, otherwise the mark is "uninformative on these seeds".
   - Arms B and Sb pass the mark if they pass on ≥ 4 of 5 seeds.
   - Post hoc tier-1 values, which motivated this mark: A 0.78 / 0.72; B, Bn and C 0.30 to 0.44.

## 4. Printed only

- **Threshold transfer (step 1 of v2):** flags on unseen genuine sources at τ_0.5, τ_cam and, if the author admits calibration sources, τ_multi. All of these are printed only; the expectation is that every arm fails it.
- P-c′ of v2 on the test ladder.
- HN2 under the amendment-13 rule.
- HN7 for the fresh networks.
- MAD22 E7 EERs, labelled "first-test data, re-read".

## 5. Bootstrap and intervals

2,000 draws, `default_rng(20261118)`. Resampling units:
- H1 hosts, for H1;
- images within class, for FFHQ landmark_combined;
- FFHQ persons, for the paired share.

Per-seed intervals are printed. Arm statements use only the seed counts of section 3.

## 6. Not decided here

- The equality term (loss rule; fresh seeds are a parallel step, not that step).
- The head change and multi-source genuine training (author items).
- The budget (author).

## 7. Author questions

- Budget: 16 fits (about 11.6 USD) or 19 fits with C (about 13.8 USD).
- Questions 1 and 2 of the alternative (SMDD and FEI as calibration sources): these concern only the printed τ_multi read.

---

# ALTERNATIVE (draft v2, arms A, B, C), kept as written at git e75a9c3

This draft replaces v1 (git 1ab1256). It applies every fix F1 to F10 of the pre-run review
`experiments/reviews/PRERUN_PN1_FRESH_SEEDS_20261112.md` (commit 7d90384) and the lead's decisions. It is for the
author's budget decision and answers (section 11). No fit, no score, no image build has been run under it. HN2 is
registered separately as amendment 13 (git a1c6664), FFHQ only.

### ALT 1. Question and standing

1. Do the within-seed arm differences of the first eight fits replicate on fresh seeds (HN6, section 7)?
2. Does any arm pass a storage mark that is not read on the saturated floor of the training sources (P-c′, section 6)?
3. Do the genuine flags on unseen genuine sources (step 1, section 5) hold at fixed thresholds?

- Fresh seeds are a parallel step. They are not the equality term that the loss rule (prereg line 179) names as the
  registered next step. The equality term stays outside this draft.
- The C − A contrast (MAD22 Webmorph E7) was chosen on the MAD22 test images and is re-read on the same images: label
  "first-test data, re-read" (F10). The same holds for every MAD22 and H1 cell and for the 191-host test ladder.

### ALT 2. Networks and platform (F6, F9)

- Arms A, B and C, all three fixed in (B is no longer optional). Bn is not refitted.
- Recipe and packing:
  - Unchanged recipe, last checkpoint.
  - Pack 1 (`5c642790…`) manifests A, B, C, byte-equal.
  - run.sh as registered for these arms (`42b335b6…`, amendment 6). The pack-2 run.sh `a208fcf8…` differs only in its arm list and is not used.
- One physical lease of one A100-SXM4 40 GB (the pn1a type) runs every fit of this batch, one fit at a time.
  - Each result tar records `nvidia-smi --query-gpu=uuid,name`.
  - All arms of one seed always run on the one machine.
  - If the lease is lost, a replacement must be the same type, and the change is disclosed in the result. Seeds already finished stay, and the unfinished seed restarts from its first arm on the replacement. If no same-type machine is available, the batch stops and the lead decides; no other type is used.
- Replicate fit: A seed 401 refitted on the new machine (same pack and run.sh), to measure platform plus nondeterminism against seed variance (review Q3).
  - Read: per cell, the absolute difference to pn1a's A seed 401, printed beside the seed SD of the fresh seeds.
  - It is never pooled as a seed.
- Pooling seeds 401 and 402 with the fresh seeds mixes pn1a and pn1b. Only the fresh seeds count for every mark; 401 and 402 are printed beside them.

### Variants (the author picks one)

| Variant | Seeds | Fits | A100-hours | Cost (0.59 USD/h) | Serial wall time |
|---|---|---|---|---|---|
| V3 | 403, 404, 405 | 9 + 1 replicate = 10 | 10 × 69 min + scoring about 0.6 h ≈ 12.1 h | about 7.2 USD (+ smoke 0.3 USD) | about 12.5 h |
| V5 | 403 to 407 | 15 + 1 replicate = 16 | 16 × 69 min + scoring about 0.9 h ≈ 19.3 h | about 11.4 USD (+ smoke 0.3 USD) | about 20 h |

- Scoring per fit: pack-1 evaluation (as tier 1), plus the τ_multi list (section 4), plus FFHQ HN2 rows (amendment 13 list), about 5 min each.
- V3 started on 12 Nov morning ends about 13 Nov 01:00; V5 ends about 13 Nov 09:00.
- Guard cap: the lead's, at 1.2 × the cost column.

### ALT 3. Claim order (hierarchical, fixed)

1. **Step 1.** Genuine flags on unseen genuine sources at fixed thresholds (section 5). Only an arm that passes step 1 is read in step 2.
2. **Step 2.** Gating-attack miss at τ_all.
   - The arm is compared with A of the same seed by a paired bootstrap.
   - It is non-inferior if the upper 95% bound of (arm − A) on the mean gating miss is at most +3 points (as P-g).
   - If A itself fails step 1, the arm's step-2 numbers are printed against A but labelled "A outside step 1; descriptive, no claim".
3. **P-c′** (section 6) is read independently of steps 1 and 2.

Middle outcomes, anywhere: "inconclusive, no claim".

### ALT 4. Thresholds (F1, F3, F4, F8)

- **τ_0.5**: the own rule, logit > 0.
- **τ_cam** of PN1: printed only, because it sits on the training sources' saturated floor.
- **Calibration sources.** At most three: FFHQ bona fide, FEI bona fide and SMDD genuine renders. FEI and SMDD are used only if the author admits them (section 11). FRGC and colorFERET are training databases and are excluded.
- **Person split.** A person is on the development side if `int(sha256("PN1fresh|" + person_key)[:8], 16) % 2 == 0`.
  - FFHQ key: the image key, from 2,000 ffhq_bona orig.
  - FEI key: the subject number. Both expressions of a subject fall on one side.
  - SMDD: 2,000 renders drawn from the sorted `os25k_bf_t` file list with `numpy.random.default_rng(20261114).choice(25000, 2000, replace=False)`; the first 1,000 drawn form the development half and the rest the test half. The list sha256 is pinned at the registration commit.
- **Quantile rule (fixed).** Use an equal-weight empirical CDF: each source carries weight 1/k, spread evenly over its development images. τ is the smallest t with weighted share(score > t) ≤ 0.05. The max-of-per-source rule (prereg §5) is printed only.
- **Two thresholds.**
  - τ_all is fitted on all admitted development halves. It is used for step 2, for FRLL and H1 in step 1, and for P-c′ (ii).
  - τ_LOSO(s) is fitted on the development halves of every admitted source except s, and read on the test half of s.
- **Fallbacks.**
  - With two admitted sources, τ_LOSO(s) uses the one other source.
  - With FFHQ only (FEI and SMDD both refused), τ_all equals the FFHQ development half. Step 1 on FFHQ is then labelled "self-calibrated", and step 1 rests on FRLL and H1.
- **Scoring list.** One extra list `pn1_fresh_cal.csv` holds the calibration and test halves of every admitted source, built from existing aligned files only. Its sha256 and the sha256 of the scorer (`rescore.py`, `6f6eede7…` or its successor) are pinned at the registration commit. Every fresh network, and the eight tier-1 networks (printed only), are scored on it.
- **Reference row.** It is not read at τ_multi: its networks were trained on SMDD `os25k_bf_t` (F4).
- **Native history.** Every unseen-source flag rate is printed beside its native eye distance, format and frame size (`tier1/native_history.json`):

| Source | Native eye distance (median) | Native file and frame | Scale into the 512 frame |
|---|---|---|---|
| FRGC | 271 px | JPEG, 1704×2272 | 0.49× |
| colorFERET | 132 px | PPM (lossless), 512×768 | 1.0× |
| FRLL | 202 px | JPEG, 1350×1350 | 0.65× |
| FFHQ bona fide | 259 px | PNG, 1024×1024 | 0.51× |
| FFHQ landmark_complete morphs | 65 px | PNG, 256×256 | 2.0× |
| FEI | 90 px | JPEG, 640×480 | 1.47× |
| H1 | 37.7 px | PNG, 112×112 | 3.5× |
| SMDD | to be measured before registration | PNG, 256×256 | — |

### ALT 5. Step 1: unseen-source genuine mark (F3, F8)

- **Per network, all of the following must hold:**
  - at τ_LOSO(s), at most 10% flagged on the test half of each admitted calibration source s;
  - at τ_all, at most 10% flagged on FRLL native (204) and on H1 genuine (598);
  - at τ_0.5, at most 10% flagged on each of the same pools.
- Both thresholds are required, not either.
- **Per arm:** step 1 passes on at least 2 of 3 seeds (V3), or at least 4 of 5 (V5).
- Clopper-Pearson 95% intervals are printed.

### ALT 6. P-c′ (F2, F7): "written after tier 1; confirmatory on fresh seeds only"

P-c′ was written after the tier-1 results were seen. On tier 1, B, Bn and C meet parts (i) and (iii) and A fails them.

- **Scope.** P-c′ is read only on networks fitted after this registration. It uses the same 191-host test ladder, which was already read once for tier 1 with other networks (stated).
- **Parts** (every part on every fresh seed of the arm):
  - (i) Own rule: at most 10% of test-ladder R0_61 flagged, with a Clopper-Pearson upper bound of at most 15%. In practice this means at most 18 of 191 flagged.
  - (ii) At τ_all, at most 10% of R0_61 flagged.
  - (iii) Paired shift scale, both conditions:
    - the median paired shift R0 -> R0_61 is at most 0.05 × (median development R4 logit − median development R0 logit) of the same network;
    - the paired AUC is at most 0.65.
- **Paired AUC (defined).** Over the 191 test hosts, P(logit(R0_61 of host h) > logit(R0 of host h)), with ties counted half. This is the "share rising" of `tier1/followups.json`.
- **Positive control.** P-c′ is informative only if A fails it on at least 2 of 3 fresh seeds (V3), or at least 3 of 5 (V5). Otherwise P-c′ is reported as "uninformative on these seeds" and no arm passes it. The reference recipe's own-rule R0_61 flag spread is 5 to 50%, so a fresh A may pass (i).
- **P-a, P-b:** printed only (ceiling).

### ALT 7. HN6 (F6): direction and decision

- HN6 states that seed variance exceeds the tier-1 arm differences. It therefore predicts that the two contrasts below do not replicate.
- **Contrast 1:** C − A on MAD22 Webmorph E7 EER, at most −5 points per seed (first-test data, re-read).
- **Contrast 2:** B − A on H1 AUC, at most −0.03 per seed.

| Outcome | V3 | V5 | Reading |
|---|---|---|---|
| Replicated | 3 of 3 | 5 of 5 | HN6 falsified for that contrast |
| Middle | 2 of 3 | 3 to 4 of 5 | inconclusive, no claim |
| Not replicated | 0 to 1 of 3 | 0 to 2 of 5 | HN6 supported for that contrast |

Stated probabilities:
- Under no effect with a symmetric per-seed distribution, the probability of meeting a one-sided threshold on every seed is at most 0.125 for 3 of 3 (weak evidence) and at most 0.031 for 5 of 5.
- With a true C − A of −12 points and a per-seed SD of 6 to 9, V3 replicates with probability about 0.5 to 0.7. With winner's-curse shrinkage to −8, it falls to about 0.25 to 0.4.
- The H1 rule follows the review (B − A ≤ −0.03 on 3 of 3). The reference-recipe seed SD on H1 is 0.018.

### ALT 8. Bootstrap (F8)

- 2,000 draws, `default_rng(20261115)`.
- Resampling units: partner cycles for ladder hosts; images within cell for the MAD22 and H1 cells; persons within each calibration development half, with τ_all and τ_LOSO refitted in every draw.
- Step-2 and HN6 intervals are per seed. Arm-level statements use only the seed counts above.

### ALT 9. HN2

Registered and run separately (amendment 13, FFHQ only, the eight tier-1 networks). The fresh networks are also scored on the amendment-13 list. Their HN2 reads are printed under the same rule and labelled "fresh seeds, same rule".

### ALT 10. Not decided here

- The equality term (loss rule).
- Multi-source genuine training: not before HN2 is read, because it would use up FFHQ and FEI.
- Head changes (temperature or unbounded head): new code, an author item.

### ALT 11. Questions for the author (D)

1. **SMDD as genuine.** May the SMDD synthetic genuine renders (`os25k_bf_t`) be used as a genuine calibration source?
   - They come from an FFHQ-trained generator, so they are not independent of FFHQ.
   - They are the reference row's training set.
   - Are they aligned to the canonical frame (review Q5)?
2. **FEI as development pool.** Is FEI (inside `gtest.csv`) released for use as a development pool in this sprint? Its scores in `gtest` would then no longer be untouched.
3. **Seeds and budget.** 3 seeds (V3, about 7.5 USD, about 12.5 h) or 5 seeds (V5, about 11.7 USD, about 20 h), with the replicate fit included in both, on 12 Nov?
