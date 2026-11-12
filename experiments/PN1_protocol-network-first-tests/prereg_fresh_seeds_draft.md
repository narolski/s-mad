# DRAFT (not registered, nothing run): protocol network, fresh seeds 403 to 405 with the replacement storage mark P-c′

Draft written 12 Nov 2026 (`date`: see the git commit of this file) after the tier-1 review
(`experiments/reviews/REVIEW_PN1_TIER1_20261112.md`). For the lead's pre-run reviewer. No fit, no score, no image build.

## 1. Question

Do the within-seed patterns of the first eight fits replicate on fresh seeds (HN6): C − A history-matched Webmorph EER
at most −5 points, and B − A H1 AUC below 0, and does any arm pass a storage mark that is not read on the saturated
floor of the training sources?

## 2. Networks

- Arms A and C (and B if the budget allows), unchanged pack 1 (`5c642790…`), unchanged run.sh and recipe, seeds 403,
  404, 405, all on ONE rented A100 type (A100-SXM4 40 GB, as pn1a), one fit at a time. Last checkpoint.
- Cost: 6 fits about 6.6 A100-hours (9 fits with B about 10).

## 3. Claim order (hierarchical, fixed now)

1. First: genuine flags on unseen genuine sources at the fixed thresholds (section 4). Only a network that holds them
   is read further.
2. Then: miss on the gating attack cells at the same threshold. A miss is never read for a network that failed step 1.

## 4. Thresholds

- τ_0.5: own rule.
- τ_multi: 5% false alarms on a pooled development genuine set with equal weight per source, at least 3 sources, none a
  training database (FRGC and colorFERET are training databases and are excluded). Sources that exist aligned today,
  without building anything:
  - FFHQ: 2,000 genuine photos (`/mnt/t7/smad_heldout/ffhq_morphs/manifests/ffhqm.csv`, family ffhq_bona, orig) and
    five history-matched pools of 2,000 each;
  - FEI: 385 genuine photos (`smadcvpr_data/manifests/gtest.csv`, fei_bona_neutral 198, fei_bona_smiling 187);
  - SMDD genuine renders (25,000, `smadcvpr_data/train/smdd/os25k_bf_t`; synthetic, 256 px).
  Proposal: development half = persons with an even seeded hash in FFHQ and FEI, and 1,000 seeded SMDD renders; the
  other halves are test pools of unseen sources, together with FRLL (204) and CASIA/H1 genuine (598), which are never
  used for a threshold.
- τ_cam of PN1 is printed only (it sits on the training sources' saturation floor).

## 5. Marks (both seeds of a pair, here all three seeds)

- P-c′ (review Q2), every part on every seed:
  (i) own rule: at most 10% of test-ladder R0_61 flagged, with Clopper-Pearson upper bound at most 15%;
  (ii) τ_multi: at most 10% of R0_61 flagged;
  (iii) paired shift scale: median paired shift R0 -> R0_61 at most 0.05 x (median development R4 logit − median
  development R0 logit), and paired AUC(R0_61 vs R0) at most 0.65.
- Unseen-source genuine mark (step 1 of the claim): at τ_multi at most 10% flagged on each test half of FFHQ and FEI,
  on FRLL and on CASIA/H1 genuine; at the own rule likewise.
- Only after that: gating-family miss at τ_multi (test R4 OpenCV-style, MAD22 OpenCV, MAD22 Webmorph, H1), arm against
  A of the same seed, paired bootstrap (as P-g).
- HN6 reads: C − A MAD22 Webmorph E7 EER per seed; B − A H1 AUC per seed. Prediction: −5 points or less in 3 of 3; below
  0 in at least 2 of 3.
- The first eight fits and the present test ladder cannot be used to pass P-c′; P-a and P-b are printed only (ceiling).

## 6. HN2 (genuine-source shortcut)

FFHQ and FEI frames already exist aligned (EV1 used their scores), so HN2 needs no new alignment: score them (about
0.2 A100-hours for the eight existing fits, on the rented machine type of each seed). Note for the author: FFHQ files are
256 px natively (loader enlarges to 224 only; no change); if a further unused database (for example CASIA beyond H1, or
Multi-PIE) were wanted, its alignment would be a new build: author item, not done.

## 7. Not decided here

The equality term (loss rule) is outside this draft. Budget, platform and whether B is included: the lead.
