Reviewer: results-reviewer (Opus), 13 Nov 2026, read-only. Post-result review of the TT1 MEDS post hoc follow-ups S1 and S2 (result.md at 7e6e913). Report as returned, unedited; saved by the TT1 owner after the record keeper's ledger (486d089). Corrections were applied in bf774cb.

**Verdict: needs qualification.** I checked the code (`/home/narolski/smad-next/src/TT1/meds/meds_strata.py`) against the registration (`prereg_meds_block.md` §7 at 104edc3). They match: the flag rule is logit > 0, the same as `tt1_read_meds.py`; the seeds are 20261126 and 20261127; there are 2,000 person-bootstrap draws; the bins are fixed; and the rule is |diff| ≤ 0.05 with an arm sentence when at least 4 of 5 seeds agree. The JSON hash matches (`b4c5da33…`). Every S1 count and S2 difference quoted in the text matches the JSON. The S1 reading is sound. The S2 arm sentences are fragile: the TT1 rate the sparse bins add to the reweighted figure is dominated by one or two flagged frames out of four casia_fasd frames. That makes the Sb verdict look less clean than it is, creates every Sp difference, and understates A. I did not open any MEDS image, sealed file or benchmark file.

**Findings (most severe first)**

1. **Major: the 2.0–2.5x bin is 4 casia_fasd frames from 4 persons, and its weight is 0.282.** Each flagged frame shifts the reweighted TT1 rate by 0.282 × 0.25 = 0.07, which is more than the 0.05 rule margin. The 2.5–3.0x bin (13 frames, weight 0.209) has a TT1 rate of 0 in every network except A_s404 (0.15). Shares from the per-bin rates in the JSON:
   - **Sb_s404 "differs" (−0.145):** −0.141 of it comes from the sparse bins (TT1 rate 0.5 there, i.e. 2 of 4 casia frames). Over the bins with at least 127 frames, the difference is −0.008.
   - **Sp (−0.070, −0.085, −0.057):** sparse-bin shares are −0.070, −0.105 and −0.086. Over the dense bins the differences are +0.002, +0.039 and +0.057.
   - **Sb on dense bins only:** all 5 seeds have |diff| ≤ 0.024.
   - **A on dense bins only:** +0.142, +0.332, +0.159, +0.483, +0.192. That is 5 of 5 "differs"; the registered numbers understate the excess.
   - **B on dense bins only:** +0.034, +0.285, +0.070, +0.143, +0.017, so still "mixed".

   The registered verdicts stand, but this sensitivity reading should be printed next to them and labelled as not registered.
2. **Moderate: the 240x240 Laplacian sign is cherry-picked.** "−0.22 / −0.24, the TT1 sign" uses s404 only. Across A seeds ρ is +0.12, −0.22, +0.05, −0.10, −0.12. Across B seeds it is +0.10, −0.24, +0.01, −0.06, −0.07. The sign is not consistent; with n = 110 and 54 persons this is noise-level.
3. **Minor: the "other sizes" ranges are wrong.** ρ with log Laplacian variance (other|all) runs +0.20 to +0.34, not +0.21 to +0.38; 0.38 and above appear only in the MEDS-I sub-stratum. ρ with enlargement is about 0 for A and B, but +0.13 to +0.21 for Sb and Sp.
4. **Minor: dropped frames are not reported, although §7 says they must be.** 23 TT1 primary frames are in no kept bin (21,035 primary, 21,012 used); no MEDS-240 image is dropped. The 4.0–6.0x bin (127 frames) is not mentioned.
5. **Minor: one interval is omitted.** B_s406 [0.017, 0.154] also excludes 0.
6. **Minor (bootstrap).** When a draw contains none of the 4 casia persons, the bin rate is set to 0 instead of the bin being left out (about e⁻⁴ ≈ 2% of draws). That pulls the TT1 draws slightly towards 0. With that few frames the intervals are also coarse, near-discrete steps. Say so; no rerun needed.
7. **Wording.** "So the MEDS-I excess is the size effect" should be "is explained by composition". The data support it: the 240 share is 51 of 126 MEDS-I primary images against 59 of 739 MEDS-II, and the within-240 rates are similar in every arm.

**Text corrections** (section "MEDS post hoc follow-ups S1, S2", `/home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/result.md`, lines 532–552)

- L533: "So the MEDS-I excess is the size effect." → "So the MEDS-I excess is explained by composition: 51 of 126 MEDS-I images are 240x240, against 59 of 739 in MEDS-II."
- L535: replace with "ρ(logit, log Laplacian variance) is −0.22 / −0.24 for A_s404 / B_s404, but its sign is not consistent across seeds (A: +0.12, −0.22, +0.05, −0.10, −0.12; B: +0.10, −0.24, +0.01, −0.06, −0.07); no sign is read."
- L536: "ρ with log enlargement is +0.51 / +0.29." → "ρ with log enlargement is positive in every A seed (+0.44 to +0.60) and every B seed (+0.09 to +0.37), and about 0 for Sb and Sp."
- L537: "ρ with enlargement is about 0, and ρ with log Laplacian variance is +0.21 to +0.38" → "ρ with enlargement is about 0 for A and B (+0.13 to +0.21 for Sb and Sp), and ρ with log Laplacian variance is +0.20 to +0.34"
- L541–543: replace with "TT1 has 1,377 frames at 1.6–2.0x (the anti-spoofing frames), 4 at 2.0–2.5x (all casia_fasd, 4 persons), 13 at 2.5–3.0x, about 9,700 each at 3.0–3.5x and 3.5–4.0x, and 127 at 4.0–6.0x; 23 TT1 frames at 1.2–1.6x are dropped (no MEDS-240 image there). MEDS-240 has 31 and 23 images in the two sparse bins (weights 0.28 and 0.21), so one flagged casia frame moves the reweighted TT1 rate by 0.07, more than the 0.05 margin."
- L545–546: append "B_s406 [0.017, 0.154] also excludes 0."
- After L549, add: "**Sensitivity (not registered):** dropping the two sparse bins, A differs on 5 of 5 seeds (+0.14 to +0.48), B stays mixed (+0.02 to +0.29), Sb is consistent on 5 of 5 (|diff| ≤ 0.024) and Sp is +0.00 to +0.06. The Sb_s404 '−0.145' and all the negative Sp differences come from 1–2 flagged casia frames in the 2.0–2.5x bin."
- L550: "For A, and partly B, the small MEDS mugshots are flagged more" → "For A on every seed, and for B on some seeds, the small MEDS mugshots are flagged more"

Recomputed from the JSON: the S1 counts for A, B, Sb and Sp; A_s404 20/51 and 23/59; S2 A_s406 0.309 − 0.079 = +0.230; and the dense-bin differences above.
