# NE1b: splice feature ceiling and rank-7 border erasers: result

Status: read once, 13 Nov 2026 (`date` Fri Nov 13 08:30:50 PM CET 2026 to 08:57:10 PM). Reviewed (post-result,
`experiments/reviews/REVIEW_NE1B_20261113.md`: needs qualification); corrections applied. Figures marked *post hoc*
come from the reviewer's recomputation (`posthoc_ne1b/`; replay of the registered stream reproduced the registered
flags exactly).

- Registration 22618b8 (pre-run check b8288e3, fixes 1-7; DATA audit 1b05940).
- Reader `ne1b.py` `9b78d588…`; output `ne1b_read.json` `4227f8eabe0c7fde…`.
- CPU only, saved NE1 features, development rows only. All five networks are platform-certified (NE1 gate).
- Storage is not read.

## Registered table

| Part | Reading | Count |
|---|---|---|
| A. Splice feature ceiling | **intermediate (probe above H0 but below the bottleneck bar)** | low ceiling on 3 of 5 seeds (needs 4); bottleneck 0; nonlinear-only 0. Knife-edge: 405 fails the plateau rule by 0.00004, 404 passes the interval rule by 0.0001 |
| B. Rank-7 border erasers | **criteria unreachable (inconclusive by design)** | the half-B ceiling eraser E7c is clean on only 3 of 5 seeds (405 and 406 fail at flag removal 0.662 and 0.667 against 0.70); E7 is clean on 2, LEACE on 0 |

## Part A readings (out-of-fold over 110 person components, 291 hosts; seeds 403 / 404 / 405 / 406 / 407)

- **AUCs.**
  - Frozen head H0, S4 against S3: 0.757 / 0.754 / 0.739 / 0.769 / 0.748.
  - Linear probe: 0.760 / 0.785 / 0.762 / 0.791 / 0.787.
  - Gain +0.003 to +0.039 (median +0.023). Component-bootstrap intervals [−0.016, 0.021], [0.011, 0.050],
    [0.005, 0.040], [0.004, 0.039], [0.018, 0.058]; the lower bound is above 0 on 4 of 5 seeds.
  - On the 80 clean test hosts the gain is +0.015 to +0.033.
- **Why "low ceiling" holds on only 3 seeds.**
  - Seed 407's upper bound is 0.058, above the 0.05 bar.
  - Seed 405 fails the plateau rule by 0.00004.
  - The learning curve is still rising: +0.001 to +0.022 from 100 hosts to all of them, and +0.027 to +0.070 from 25
    hosts to all.
  - C sat at the top of its grid (10) in all 25 folds, so the ceiling may be slightly understated.
- **Other probes.**
  - Small MLP: 0.725-0.776. At about 230 fit hosts this says nothing about nonlinear information.
  - Core-only probe: about the same as the linear probe.
  - Training-list probe lin_T: equal to H0 (±0.003).
  - Label-permutation null: at most 0.57.
  - Without the largest component (10 hosts): unchanged.
- **Plain reading.**
  - A linear probe fitted on held-out development persons separates S4 from S3 slightly better than the frozen head.
  - The best probe reaches 0.791, far below the 0.85 bar. No linear or small-MLP head tested reaches it, and
    extrapolating the learning curve, a larger refit set is unlikely to close the gap.
  - Simple morph cues alone separate these same rows at 0.773 [0.742, 0.805] (FLOORS stage 3, `ri_S4_vs_S3`). So this
    gain cannot be read as identity information.

## Part B readings (half-B persons, 1,435 pairs, 202 hosts)

- **H1's border response.** Pooled Δlogit 0.47-0.72; excess flags at the 99th-percentile camera cut 0.048-0.166.
- **E7 (rank-7 per-mask span).**
  - Logits: cancelled two-sidedly (removal 0.91-1.02), and per mask on 6-7 of 7 masks.
  - Ranks: two-sided (1.05-1.11).
  - Flags: two-sided only on seeds 403 and 407 (0.72, 0.72). Elsewhere 0.26-0.66, so E7 keeps 28-74% of the excess
    flags.
  - The residual sits mostly in CFP-FF and MSU-MFSD (0.04-0.15 excess).
- **E7c (fitted on the read rows, the ceiling).** Flags 0.66-0.87; even this in-sample eraser keeps 13-34% of the
  excess flags. Two-sided on 3 of 5 seeds, so by the registered order the criteria are unreachable.
- **Why, post hoc.** The residual flags are a dispersion effect.
  - After E7c the mean logit shift per mask is 0, yet bordered copies keep 2.5-4.7× the photos' logit spread on CFP-FF
    and MSU-MFSD (H1: 6-18×). The paired Δlogit SD is 0.73-1.05.
  - Any first-moment eraser leaves copies whose tails cross the 99th-percentile cut. "Criteria unreachable" is
    therefore a property of mean-based erasers, not only a design accident.
- **LEACE (Ledoit-Wolf).**
  - It removes the half-B class-mean spread by 88-90% (0.39-0.60 → 0.05-0.06), but transfers worse to flags: removal
    0.22-0.48, never two-sided. Its condition number is 1.0e4-2.8e4.
  - No bug (*post hoc*): the half-A spread after erasure is 1e-15 and the rank is 7. The oblique projector (largest
    singular value of I − M 13-22, against 1 for E7) amplifies the 5-11% of the half-B mean differences that lie off
    the half-A span.
  - LEACE also guarantees first moments only, so it cannot fix tail flags either.
- **Nulls.** Isotropic rank-7 nulls pass two-sided on 0 of 20 on every seed; head-matched on 0; covariance on 0-2.
- **The registered in-domain cost check was saturated, and this was foreseeable.**
  - Shortcut cues alone separate R4 from R0 at 1.000 (FLOORS stage 3), and every head here has R4 recall 1.000 and
    R4-vs-R0 AUC 1.000 on the 198 half-B test-host R4 rows.
  - So the check cannot detect a cost. The pre-run check proposed the same contrast, so the flaw is shared.
- **Cross-domain cost (printed only).**
  - On FFHQ landmark_combined, refitting after E7 loses 0.269 / 0.060 / 0.188 / −0.011 / 0.141 recall at the
    99th-percentile camera cut. The AUC loss is 0.075 / 0.001 / 0.081 / 0.021 / 0.021.
  - *Post hoc* (not registered): 20 head-matched random rank-7 subspaces, which remove the same share of ŵ (the E7 span
    holds 0.68-0.90 of ŵ), lose at most 0.054. E7 exceeds the largest of them on 4 of 5 seeds (all but 406).
  - So the loss is specific to the border span, not to removing the head direction.
  - landmark_combined differs from its genuine photos in surround history (surround-only floor 0.942), so this span may
    carry a surround shortcut as well as morph evidence. NE1b does not decide which.
  - LEACE costs little (−0.05 to +0.03).

## What this does and does not show

- **Shows.**
  - A rank-7 eraser cancels the frozen heads' mean border response, per mask, but not their border false alarms.
    Bordered copies still have 2.5-4.7× wider scores (*post hoc*).
  - Removing the border span costs recall on FFHQ landmark_combined. Random subspaces with the same overlap with the
    head do not (*post hoc*).
- **Does not show.**
  - That a training-time debiasing arm would help. The reading is "criteria unreachable", and the in-domain cost check
    was saturated.
  - A cost to morph detection. NE1b shows that the border span and the heads' landmark_combined response overlap.
  - That the splice gain is identity information: it sits inside the simple-cue floor.
- **Wording for the paper.** Do not say "border and detection share features" until an unsaturated in-domain cost check
  and a surround-balanced landmark_combined read are done.
- **Licenses.** No debiasing arm and no splice-head arm is licensed by NE1b. Any such arm would be post-freeze only.
- **How sure.** Development data, 5 seeds, both readings on a knife-edge (one seed; a margin ≤ 0.04 on a ratio).

## Reviewer's next steps (CPU only; each needs its own registration)

1. An amendment replacing the in-domain cost with R4 vs R3 and S4 vs S3 AUC and recall at the 99th-percentile cut, and
   registering the head-matched-null FFHQ cost as a printed quantity.
2. H-new-2 (waiting) with that cost check.
3. H-new-5 (a second-moment border eraser) together with H-new-4 (storage as spread).
4. H-new-6: the E7 cost on the surround-balanced `lcomb_bal`.
5. H-new-7: the splice probe within blend-softness D quintiles, with C ∈ {100, 1000} printed.

## Closing (lead's ruling, 13 Nov 2026: the erasure line stops here for the sprint)

**Established (NE1 and NE1b, development data, frozen Sb seeds 403-407).**
- **The border cue is linearly decodable** from the penultimate features (probe AUC 0.991-0.996).
- **Mean-based erasers cancel the mean border response but not the false alarms.**
  - Rank-1 (NE1), rank-7 (E7) and LEACE erasers cancel the mean border response in logits, per mask for E7.
  - They leave 28-74% of the excess flags at the 1% camera cut (E7), because bordered copies keep 2.5-4.7× the
    photos' score spread (post hoc).
- **The splice probe barely beats the frozen head.** A probe fitted on held-out development persons gains +0.003 to
  +0.039 AUC over the frozen head (0.76-0.79). That is inside the simple-morph-cue floor of 0.773 and far below the
  0.85 bottleneck bar.
- **Storage was untestable in the registered unit** (NE1: the camera-pool rank saturates for FFHQ photos). Sb's storage
  reaction rests on MS1 and FS1.

**Not established.**
- No cost to morph detection was shown. The registered in-domain cost check was saturated (R4 recall 1.000). The
  FFHQ landmark_combined cost is specific to the border span, but that set has a surround shortcut.
- **"Border and detection share features" may not be written.**
- No debiasing arm and no splice-head arm is licensed.

**Not run, available after the deadline (CPU only, on the saved features).**
1. An amendment replacing the in-domain cost with R4 vs R3 and S4 vs S3.
2. H-new-2 (an eraser orthogonal to the head) with that cost check.
3. H-new-5 (a second-moment border eraser) together with H-new-4 (storage as spread).
4. H-new-6 (the E7 cost on the surround-balanced lcomb_bal).
5. H-new-7 (the splice probe within blend-softness D quintiles).

The direct test of the border reaction is the border-crossed training arm (Sbx, queued on WCSS). The second-identity
question goes through the pipeline-matched ladder reads and the look-alike set.

**Saved features, kept for reuse.**
- `/mnt/t7/smad_next/NE1/results/NE1_feats.tar` (`18d13b10…`) and its unpacked copy in `results/unpacked/`.
- The Athena copy in `results/NE1`.
- Manifests in `/mnt/t7/smad_next/NE1/`.
