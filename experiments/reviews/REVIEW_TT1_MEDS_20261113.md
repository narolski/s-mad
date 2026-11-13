Reviewer: results-reviewer (Opus), 13 Nov 2026, read-only. Post-result review of the TT1 MEDS reading (TT1-M, result.md at 48af747). Report as returned, unedited; saved by the TT1 owner after the record keeper's ledger (486d089) found no review file. Corrections were applied in c4c2233.

## Verdict: needs qualification

I checked the registered mechanics and they are sound. The pins match: reader 0b5d86b1…, gate_check_m 1a62c58b…, remote 70028d9b…, drive 9006cc99…, manifest 3698bcb4…, meds_score.csv 9093d5d5…, output dd65adb3…. `mock` is false, 18 of 18 networks pass the gate with max|Δ| 0, and TT-M1 to TT-M3 were applied exactly as registered (tt1_read_meds.py:115-129).

I recomputed several numbers from tt1_read_meds.json and they match the text:
- A_s404 flag 0.0509, bootstrap [0.032, 0.072];
- B_s406 AUC against R_cam 0.999;
- Sb_s407 shift 0.52;
- B − A −0.019 ± 0.008;
- 240x240 range 0.000-0.391.

The printed reads are the problem. In my post hoc split of the raw npz scores, almost every flag comes from the 110 images that are 240x240. TT-M4's "sharper scores higher, opposite to A's packs in TT1" is a Simpson artefact and should be withdrawn. The headline verdicts stand.

## Findings (most severe first)

**F1 (major): MEDS flags are a small-native-size effect.** This is my post hoc read of the npz files plus the manifest, primary pool.
- The 110 primary images at 240x240 come from 54 persons. Their median source eye distance is 46 px, and they are enlarged 1.62-5.84x (median 2.84). The other 755 images have median eye distance 108 px and median enlargement 1.22.
- Flags on the other 755 images:
  - A_s403 0, A_s404 1, A_s406 1;
  - B_s404 0;
  - Sb_s403 1, Sb_s407 1.
- Flags inside the 240 group, same networks: 11, 43, 34, 25, 2, 0.
- MEDS-I images that are not 240x240 (n = 75) have 0 flags in every network I checked.
- So the "MEDS-I is flagged more" read is the size effect: 51 of the 126 primary MEDS-I images are 240x240, against 59 of 739 for MEDS-II.
- This matches TT1, where A is sensitive to small, enlarged faces (Geometry-112 flags 0.19-0.50). It is consistent with "enlarged low-resolution faces trigger false alarms". It does not show a separate MEDS source effect.
- A_s404 at 39% on the 240 group, from 54 persons, is the operationally relevant number.

**F2 (major): the TT-M4 sentence is wrong.**
- `lap_var` is computed on the full native frame (meds_build.py:87). Across MEDS's mixed sizes it measures size and background as much as sharpness: ρ(log lap, width) = −0.51 and ρ(log lap, log enlargement) = +0.40.
- Inside the 240 group, ρ(logit, log lap) is −0.10 to −0.24 for A_s404, A_s406 and B_s404. That is the same sign as TT1 (softer scores higher). ρ(logit, log enlargement) there is +0.29 to +0.53 for A and B.
- Inside the 755 other images, ρ with enlargement is about 0 (−0.10 to +0.21). ρ with lap stays at +0.17 to +0.28, which is unexplained and not interpretable as sharpness.

**F3 (moderate): "displaced" needs its size.**
- R_cam is a collapsed floor: median −3.65, p95 −3.61 (A_s404).
- AUC of 0.98-0.99 therefore comes from shifts of only 0.16-0.52 logit, which is 2.2-7.9% of u (`shift_in_u` 0.022-0.079).
- This is rank separation from a very tight reference, not a large displacement. Print `shift_in_u`.

**F4 (minor): factual fixes.**
- The 240x240 line says 156 images; that is the full manifest. The primary pool has 110 images of 54 persons.
- The TT-M2 range 0.977-0.999 includes Sp. The deciding arms span 0.979-0.999.
- Sb − B: 3 negative and 2 exactly 0.
- Missing TT-M3 detail:
  - B − A: interval excludes 0 on 5 of 5 seeds, −0.03 bar met on 1 of 5 (s406).
  - Sb − A: interval excludes 0 on 4 of 5 seeds, bar met on 2 of 5 (s404, s406).
- AUC against R_ffhq is below 0.5 on 16 of 18 networks; A_s406 is 0.616 and B_s406 is 0.562.
- The header still says "not yet reviewed".

**F5 (minor): JPEG and part remain confounded.**
- All 110 images in the 240 group are JPEG.
- Median bits per pixel is 0.80 against 0.91 for the rest. This is crude, from file size only; no image was opened.
- Compression cannot be separated from size here. Only 7 of the 54 persons in the 240 group also have larger images, so a within-person contrast is not feasible.

## Text corrections for "MEDS extension TT1-M"

- **Header:** "(NIST SD32 mugshots; registered reading; reviewed 13 Nov (results-reviewer): needs qualification, corrections applied)"
- **TT-M2 bullet:** "AUC against R_cam is 0.979-0.999 for the deciding arms (Sp 0.977-0.979). R_cam is a tight floor (p95 within 0.05 logit of its median), so the median shift is only 0.16-0.52 logit, 2-8% of u."
- **TT-M3 table note:** "B − A: interval excludes 0 on 5 of 5 seeds, −0.03 met on 1 of 5 seeds. Sb − A: interval excludes 0 on 4 of 5 seeds, met on 2 of 5. Sb − B: 3 negative, 2 equal."
- **Replace the TT-M4 bullet:** "TT-M4. Spearman of logit with log Laplacian variance is +0.37 to +0.50 and with log enlargement +0.21 to +0.46. Laplacian variance is computed on the full native frame, so across MEDS's mixed sizes it tracks image size (ρ with width −0.51). Post hoc review split by size: inside the 240x240 group, ρ with sharpness is −0.10 to −0.24 for A and B (the TT1 sign) and ρ with enlargement +0.29 to +0.53. Among the other images, ρ with enlargement is about 0. No sign reversal relative to TT1 is shown."
- **Replace the part and 240 bullets:** "240x240 images: 110 in the primary pool, 54 persons, enlarged 1.6-5.8x (median 2.8); 0.000-0.391 flagged (A 0.10-0.39, B 0.009-0.23, Sb 0-0.027). Post hoc review: nearly all flags fall in this group (for example A_s404 43 of 44, B_s404 25 of 25), with at most 1 flag per network among the other 755 images. The MEDS-I against MEDS-II difference (A 0.040-0.159 against 0.008-0.032) follows from this: 51 of 126 MEDS-I images are 240x240, and MEDS-I images above 240x240 have 0 flags. Size, JPEG coding and part cannot be separated."

## What may and may not be said

- **May say:** "On 865 frontal NIST MEDS mugshots of 400 persons, unseen in training, all 15 fresh-seed networks stayed within the fixed decision rule (bootstrap upper bound ≤ 7.2%). The false alarms that occur concentrate in small 240x240 mugshots whose faces are enlarged about 3x. There the plain network flags up to 39% of 54 persons and the protocol network up to 23%."
- **May not say:**
  - that MEDS-I or the source itself causes the flags;
  - that sharper photos score higher;
  - that MEDS is strongly displaced in magnitude;
  - that any arm is better;
  - anything about misses.

## Next steps

1. Zero GPU, now: register a post hoc stratified print, size group × part, for all 18 networks. It should give the flag share, a person-bootstrap interval and Spearman by stratum. This turns F1 into a recorded read.
2. Zero GPU: compare the MEDS 240-group flag rates with TT1 families at matched enlargement (1.6-3.5x). This tests "enlargement, not source".
3. Author item only (resampling): rescore the MEDS images above 240x240 after downsampling them to an eye distance of about 46 px. This is the causal test of size against source. No agent may write that code.
4. Later: morph pairs from the 157 persons with multiple encounters, for a miss read. Not before the paper.

Files:
- /home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/result.md (lines 429-492)
- /home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/tt1_read_meds.json
- /home/narolski/smad-next/src/TT1/meds/tt1_read_meds.py
- /home/narolski/smad-next/src/TT1/meds_build.py (line 87)
