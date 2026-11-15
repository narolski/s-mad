# Post-read hypotheses on the MAD22 read (FINAL): registered for the record (MAD22-informed)

Written `date`: Fri Nov 13 09:31:43 PM CET 2026. This is after the sealed MAD22 read (0cfec2a), under the lead's decision (4).

**Label on every read below: "MAD22-informed, post-read, descriptive".**
- Existing score files only: the result tar `FINAL_mad22_final2.tar` (c5205a58…), the pinned release files and the
  pack frames.
- No new scoring of any network on any benchmark row.
- No method choice, arm, threshold or selection rule may follow from these reads.
- NOTEBOOK records 21:08 as the MAD22-informed cut-off.

**Source.** The four hypotheses come from the results review, `experiments/reviews/REVIEW_FINAL_MAD22_20261113.md`,
section 5.

## H-new-1 (expression): the smiling genuine photos (_08) drive our MAD22 errors

- **Read:** per seed and per family (OpenCV, Webmorph), history-matched form. Take the threshold at the seed's EER
  point, and compute BPCER on the _08 photos and on the _03 photos.
- **Supported:** the _08/_03 ratio ≥ 2 on ≥ 4 of 5 seeds in both families.
- **Falsified:** the ratio < 1.5 on ≥ 3 seeds.
- **Otherwise:** inconclusive.

## H-new-2: the border-equalised rise on FaceMorpher sits on the genuine side

- **Read:** per seed. Take S-form morph scores with BE-form genuine scores; compute the EER rise over S, and divide it
  by the full BE_S − S rise.
- **Supported:** the share is ≥ 70% on ≥ 4 of 5 seeds.
- **Falsified:** the share is < 40% on ≥ 3 seeds.
- **Otherwise:** inconclusive.
- **Seeds with no rise:** a seed whose BE_S − S rise is ≤ 0.5 points is "not read".

## H-new-3: Webmorph misses are low blend-energy morphs

- **Measure.** D = the mean absolute difference, inside the face hull, between each Webmorph morph's aligned frame and
  the mean of its two contributors' aligned FRLL frames. It is computed in memory and no image is written. The hull
  comes from the existing landmark files; if none exist for these frames, the read is "not read".
- **Read:** Spearman(logit, D) per seed, and the share of own-rule misses in the bottom two D quintiles.
- **Supported:** ρ ≥ 0.3 on ≥ 4 of 5 seeds, and ≥ 60% of misses in the bottom two quintiles.
- **Falsified:** ρ < 0.15 on ≥ 3 seeds.

## H-new-4: development AUC predicts the MAD22 rank over Sb seeds 401-407

- **Read:** Spearman between each seed's development landmark_combined AUC (registered FS1/tier-1 reads) and its
  MAD22 mean2 EER on the history-matched form. For 401/402 the tier-1 read gives OpenCV and Webmorph E7 EER
  (`sb_read.json`); for 403-407 the values come from `final_read.json`.
- **Supported:** ρ ≤ −0.7.
- **Falsified:** ρ ≥ 0.
- **Otherwise:** inconclusive.
- **Caveat:** n = 7 gives low power, and seeds 401/402 come from a different block (exposure).

**Status:** registered, not run. Each read is run only on the lead's word and reported with the label above.
