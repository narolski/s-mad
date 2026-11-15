Reviewer: results-reviewer (Opus), 13 Nov 2026, read-only. Post-result review of TT1-X Part 2 (MS1 Sb, SbM3, SbV rows; result.md at 25232fe). Report as returned, unedited; saved by the TT1 owner after the record keeper's ledger (486d089). Corrections were applied in b16dba4.

**Verdict: needs qualification (minor).** I found no blocker. The Part-2 text is accurate to 3 decimals and the reader follows the pinned source rules. Three gaps need fixing: (1) the SbM3-vs-Sb line does not say that MS1's registered verdict on the same statistic is "no claim"; (2) the R3(g) line has no mixed-TF32 label, and the FFHQ line names no pool or TF32 setting; (3) the rank reads, which qualify SbM3's lower flag rate, are left out. Nothing pre-empts or contradicts MS1's registered read.

**What I checked (read-only, no sealed or benchmark files opened)**
- **Reader.** `src/TT1/tt1_read_ms1.py` sha256 is `142c8c4f…`, matching the Part-2 pin (prereg_x_block.md:132). It was committed at b82163c (11:14) and has not changed since; the pin is at fdc41e2 (11:27). The output sha256 is `f5787f57848f…`, matching result.md:391.
- **Source rules match amendment M1 (prereg_x_block.md:110-115).**
  - In-pack, TF32 on: U, R_cam, R_ffhq, M_ffhq.
  - tt1ref, TF32 off: Rcb, Rgeo, Rfb.
  - R3(e), R3(f) and geo_flag use the tt1ref R_cam on both sides (tt1_read_ms1.py:94-101).
  - Each net is scored with the matching tar for its machine (MACHINE map, line 30).
  - The TF32 split is 0.0020-0.0222 with 0 flips on 15/15 nets ✓.
- **Restricted pools.** In all 15 nets the missing rows are Uall pools only (msu 5, lfw 1666, calfw 1111, cfp_ff 11, agedb_30 1359; 4,152 rows in total). U_p is complete ✓.
- **Labels.** The SbM3 FFHQ label is present in the JSON for R_ffhq, Rfb, M_ffhq, u, R3(b) and R3(d) ✓. The exclusion proof shows overlap by key and by sha256 = 0 and max cos 0.396 (MS1 exclusion_proof.json).
- **Recomputations.**
  - SbM3 s403 F̄ = mean of the 7 family flags = 0.00783, which matches r5.Fbar ✓.
  - F̄ differences SbM3 − Sb: −0.0063, −0.0388, −0.0045, −0.0089, −0.0149.
  - R3(g) on the 112-px group (lfw, calfw, cfp_ff, agedb_30): Sb 0.810-0.951, SbM3 0.832-0.954, SbV 0.828-0.968 ✓.
  - R_ffhq flags: Sb 0.0235-0.050, SbM3 0.0015-0.0075, SbV 0.0265-0.0435.
  - FS1 A100 Sb F̄ (PN1_Sb, tt1_read_fs.json): 0.0145, 0.0411, 0.0129, 0.0140, 0.0175. The largest gap to L40S Sb is 0.0008.

**Findings (most severe first)**
1. **Major (calibration against MS1).** result.md:410-411 prints "below Sb on 5 of 5 seeds" without saying how MS1 ruled. MS1 registered P1-T as "untestable at the own rule (floor)" with the sentence "inconclusive, no claim" (MS1 result.md:16, 40; ms1_read.json P1T). As written, the TT1 line reads like a positive result that MS1 explicitly declined to claim.
2. **Major (omitted qualifier).** The rank reads in tt1_read_fs_tables.md (last section) show SbM3 shifts the whole genuine distribution down without separating sources better:
   - F̄ at the −2 cut-off: SbM3 0.008-0.024 vs Sb 0.21-0.41.
   - R3(f) is lower for SbM3 on 5/5 seeds: g224 0.725-0.771 vs 0.757-0.868; g112 0.846-0.903 vs 0.901-0.953.
   - R3(c) cfp_ff: SbM3 0.493-0.791 vs Sb 0.634-0.857, lower on 4/5 seeds (mixed TF32).

   This matches MS1's P2 (offset AUC slightly lower for SbM3; inconclusive) and MS1's printed miss cost. Without it, the low flag rate reads as better source invariance.
3. **Minor (labels).**
   - The R3(g) bullet (line 415) should carry "mixed TF32 (U on, references off)".
   - The FFHQ bullet (line 412) should name R_ffhq (2,000 images, in-pack, TF32 on).
   - The table should say which columns are tt1ref TF32 off (Geo-112, CFP-border) and which are in-pack TF32 on (F̄, F_max).
   - "development persons excluded, other pipeline" (line 398) is unclear; see the rewrite below.
4. **Minor (wording and rounding).**
   - The difference range should read −0.0045 to −0.0388, not "−0.004 to −0.039".
   - SbM3's FFHQ range is 0.0015-0.0075.
   - "within 0.002" understates the agreement: the largest gap is 0.0008. The FS1 values should be printed to 4 decimals (0.015 and 0.018 are rounded from 0.0145 and 0.0175).
   - "Platform reference" is misleading. These are independently retrained networks (same manifest train_Sb and seed, different GPU), not the same networks scored on two platforms.
5. **Minor (traceability).** TT1's F̄ differs from MS1's registered F_T in the 4th decimal (Sb s404: 0.04142 vs 0.04146), because of pool and weighting differences. The text should say MS1's values are the registered ones. "(fdc41e2)" should give the sha256 `142c8c4f…` as well.

**Exact text corrections for "TT1-X Part 2" (result.md:388-418)**
- **Heading:** replace "not yet reviewed" with "reviewed (post-result, 13 Nov)".
- **Line 390:** "Reader `tt1_read_ms1.py` (sha256 `142c8c4f…`, pinned at fdc41e2), run once."
- **Line 398:** "For SbM3, every FFHQ read (R_ffhq, R_ffhq^border, M_ffhq, u, R3(b), R3(d)) is on a trained source. The TT1 FFHQ images and persons were excluded from SbM3's training by key, file and identity (MS1 exclusion proof), and SbM3's FFHQ training images were made by a different pipeline."
- **Line 399:** "U_all pools are cut to aligned frames (4,152 non-aligned rows absent); U_p (21,035) is complete."
- **Add after line 399:** "Column sources: F̄ and F_max are in-pack, TF32 on; the Geo-112 and CFP-border flags are tt1ref, TF32 off."
- **Lines 410-411:** "**SbM3 against Sb.** SbM3's F̄ is below L40S Sb's on 5 of 5 seeds (difference −0.0045 to −0.0388). MS1's registered read of this statistic (P1-T) is 'untestable at the own rule (floor)'; no claim. TT1 adds none. The rank reads do not show better source separation: SbM3's R3(f) is lower than Sb's on 5/5 seeds (g224 0.725-0.771 vs 0.757-0.868; g112 0.846-0.903 vs 0.901-0.953), and R3(c) on cfp_ff is 0.49-0.79 vs 0.63-0.86 (mixed TF32). F̄ at −2 is 0.008-0.024 vs 0.21-0.41: SbM3 moves the whole genuine distribution lower, consistent with MS1's P2 and its printed miss cost on FFHQ morphs."
- **Line 412:** "**FFHQ genuine flags (R_ffhq, 2,000 images, in-pack, TF32 on).** Sb 0.024-0.050; SbM3 0.0015-0.0075 (trained source); SbV 0.027-0.044."
- **Line 415:** "**R3(g), 112-px group (lfw, calfw, cfp_ff, agedb_30; mixed TF32).** Sb 0.81-0.95, SbM3 0.83-0.95, SbV 0.83-0.97."
- **Lines 416-418:** "**Retraining reference, not a comparison.** L40S MS1 Sb F̄ (0.0141, 0.0414, 0.0132, 0.0132, 0.0172) is within 0.0008 of FS1 A100 Sb at the same seeds (0.0145, 0.0411, 0.0129, 0.0140, 0.0175). Same manifest and seed, independently trained on different GPUs, with different TF32 settings for U. Printed only. MS1's registered F_T values (ms1_read.json) differ from these in the 4th decimal and are the registered ones."

Files: /home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/result.md, …/tt1_read_ms1.json, …/tt1_read_fs_tables.md, …/prereg_x_block.md, /home/narolski/smad-next/src/TT1/tt1_read_ms1.py, /home/narolski/smad-next/experiments/MS1_multi-source-training-set/result.md and ms1_read.json.
