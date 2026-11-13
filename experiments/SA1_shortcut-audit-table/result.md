# Shortcut audit table (SA1): result, version 2 (13 Nov 2026, reviewed; before today's readings)

Status 13 Nov 2026, 08:49 CET (machine clock; earlier "09:30" and "10:10" stamps in these files were estimates and wrong). Update 08:58: G9 and G11 added. Update about 09:45: PR1 part 1 (five fresh seeds for rows 6-9, 17, 19; new row 20) and C2P (rows 1, 2) entered from their reviewed results. Update about 09:15: row 15 carries the A23 within-key AUCs of the released networks (logit gaps moved to detail). Update about 09:05: row 15b (retrained ViT-L/14 partner trace, SM1 A14) and AD4 cluster-stack wording. Version 2 applies the independent review (results-reviewer, Opus, 13 Nov; 20 corrections, summarised in `README.md` section 2). Compiled from registered, committed results only. **Nothing was scored, computed
on images or run for this page.** No file whose name contains `fst`, `valx` or `A12SP` was opened. Numbers that come
from the 12 Nov benchmark exposure of candidate networks (FRLL, MAD22, H1 reads of the protocol networks;
`experiments/PN1_protocol-network-first-tests/BENCHMARK_EXPOSURE.md`) are **not** used: those cells say
"not measured (exposure only)". Audits of released detectors on benchmark files are allowed and are used, labelled
"benchmark audit". Where a reviewer's wording exists, it is used instead of the owner's.

This is the state before today's readings: the ablation without matched negatives (Sp, 1 of 3 fits landed,
not read), the three-source training set (SbM3, MS1, reading today) and the registered storage test on unseen FFHQ
persons (contrast 2-prime, C2P, scoring today) and the fresh-seed block of the unseen-genuine test (TT1-FS, end about 13:30). Those cells are "not measured (pending today)" and will be filled
when the lead says the readings are in.

## Words used in this table

- **Columns (training arms, all CLIP ViT-B/16 with LoRA, MADation recipe, from the protocol network first tests, PN1).**
  **A** plain training (camera photos against two-person morphs). **B** protocol negatives (A plus warp-only images,
  the morph's own warped halves and 61 px stored copies, as negatives). **Sb** protocol negatives plus face-spliced
  morphs as attacks with seam-only (S0) and same-person-splice (S3) negatives. **Sp** Sb without the S0 and S3
  negatives (ablation). **SbM3** Sb plus FFHQ photos, morphs and controls (three sources; MS1). Where a control arm
  answers the row, it is named in the cell: **Bn** = B cut to A's number of unique images; **Bv** = B at Sb's row
  volume; **C** = B plus JPEG-crossed copies.
- **Released detectors** (released weights, our scoring): MADation ViT-B/16, MADation ViT-L/14, MixFaceNet-MAD,
  SelfMAD.
- **Rungs (landmark ladder, AR1).** R0 camera photo; R0_61 the same photo shrunk to 61.2 px between the eyes and
  enlarged back ("stored small"); R2w warp-only image (one person, no blend); R2w4 warp-only image with the two-person
  geometry; R3 same-person morph (two photos of one person blended); R4 two-person morph; S4 face-spliced morph (R4
  inside the face hull, R2w4 outside); S3 same-person splice; S0 seam-only negative (R2w face pasted on R2w4, no
  second person and no blend).
- **Own rule** = logit above 0 (the network's own decision). **τ_cam** = threshold flagging 5% of training-source
  camera photos (saturated band for these networks; not used as evidence here).
- **Data.** "Development" = our own ladder (FRGC, colorFERET hosts), AF0 images, FFHQ (development set by the lead's
  designation of 12 Nov) and the TT1 unseen-genuine sources (LFW/CALFW, CFP-FF, AgeDB, anti-spoofing live frames).
  "Benchmark audit" = released detectors on FRLL, FRLL-Morphs, corrected MAD22, MorDIFF or DiM.
- **Status.** "reviewed" = the number or sentence is in an independent review file in `experiments/reviews/`;
  "unreviewed" = only in an owner's or lead's file; "two seeds only" = seeds 401/402, each seed on its own machine
  (seed confounded with machine); "not measured"; "not measured (exposure only)"; "not measured (pending today)";
  "n/a" = the row does not apply. A cell can carry two status words (for example "reviewed; two seeds only").
- **Paired control.** Every row compares the same images with and without the suspected cue, except row 4 (unseen
  camera source), where the source cannot be switched on the same image; that row is a source comparison.

## The matrix (headline per cell; details, intervals, files and lines in the register below)

| # | Shortcut (paired control) | A plain | B protocol | Sb protocol + splice | Sp | SbM3 | MADation ViT-B/16 | MADation ViT-L/14 | MixFaceNet-MAD | SelfMAD |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Storage history of genuine photos (shrink and re-store) | **used**: own-rule flags on FFHQ +14.7 to +21.8 pts (5 seeds); C2P not read (every plain network failed the platform gate; re-scoring C2P-R pending) | **reduced, not removed**: +2.5 to +5.5 pts (5 seeds), at a near-trained size; C2P not read (1 seed passed the gate) | **reduced, not removed**: +0.5 to +2.7 pts (5 seeds); C2P (4 gate-passed seeds): +1.0 to +3.8 pts at 61.2 px, −0.3 to +3.4 at the untrained 112.7 px, not compared with the plain recipe (registered contrast uninformative) | pending today | pending today | **used**: EER +12.2 to +19.0 pts | not shown (saturated; small effects not excluded): −1.0 to +2.0 pts; MAD22 FaceMorpher 17.6 vs 3.4% flagged | **used**: EER +18.5 to +21.1 pts | **used**: 0% → 44.6–97.1% flagged |
| 2 | Storage history of morphs (stored-small morph missed) | not available: C2P gate failed all 5 plain networks (C2P-R pending) | not read: 1 seed passed the C2P gate (C2P-R pending) | **evasion falsified** on 4 of 4 read seeds (C2P H-new-1) | not measured | not measured | not measured | not measured | not measured | not measured |
| 3 | JPEG history | not measured (exposure only) | not measured (exposure only) | not measured (exposure only) | not measured | not measured | graded reaction (older ledger) | 0.13 logit shift, no own-rule change (saturated) | 4.9% flagged at JPEG 50 (older ledger) | not evaluable (own crop) |
| 4 | Unseen camera source (source comparison, not paired) | own rule fails on 2 of 7 families (2 seeds; fresh seeds pending today, TT1-FS) | own rule holds (≤ 4.9%), but FFHQ 17.8 / 6.4% (2 seeds; TT1-FS pending) | own rule fails narrowly on 2 of 7 families (2 seeds; TT1-FS pending) | not measured | pending today (its purpose) | 0.1–2.6% FFHQ at own rule | not measured (earlier figure withdrawn) | source-dependent flags (older ledger) | 25–47% of ladder photos at its FRLL threshold |
| 5 | Image border / frame (black border alone) | inconclusive (TT-H3): +0.04 to +0.10 logit; CFP-sized borders +0.21 to +0.38; FFHQ mixed in sign (2 seeds; TT1-FS pending) | inconclusive (TT-H3), same range (2 seeds; TT1-FS pending) | inconclusive (TT-H3), same range; FFHQ flags 7.0 → 13.4% (2 seeds; TT1-FS pending) | not measured | not measured | frame alone +0.42 logit | not measured | not measured | frame alone +0.72 logit |
| 6 | Warp only, no second person (R2w) | **not flagged** (5 seeds) | not flagged (5 seeds; trained negative) | not flagged (5 seeds; trained negative) | not measured | not measured | small (warp share 0.01–0.07; registered "reads morphing"): R0→R2w 0.51–0.57 | not used: 0.43–0.46 | small (share 0.05–0.15): 0.53–0.59 | **reacts**: R0→R2w 0.65–0.71 |
| 7 | Same-person morph (R3) | **flagged like a morph**: 94.8–99.5% (5 seeds) | **flagged like a morph**: 90.6–95.3% (5 seeds) | **flagged like a morph**: 83.2–88.5% (5 seeds) | not measured | not measured | **flagged like morphs**: R2w→R3 0.948 | **flagged**: 0.90–0.93 | **flagged**: 0.81–0.84 | **flagged**: 0.92–0.96 |
| 8 | Same-person face splice (S3) | not flagged: 2.1–5.8% (5 seeds), but misses splices | not flagged: 0.5–3.7% (5 seeds), but misses splices | **inconclusive**: 37.2–48.2% flagged (5 seeds), a trained negative type | pending today | not measured | S3 ≈ S4 (0.473, OpenCV) | S3 ≈ S4 (0.519) | S3 ≈ S4 (0.511) | S3 vs S4 0.579 |
| 9 | Blending seam (S0 seam-only negative) | inconclusive: S0 flagged 0–0.5%, weak S4 detection (5 seeds) | inconclusive: S0 flagged 0%, 91–98% of S4 missed (5 seeds) | **seam-only not flagged** (5 seeds; trained negative) | pending today (its purpose) | not measured | seam alone not used (R2w4 vs S0 0.46–0.54) | not used (same) | not used (same) | not used (same); reads face blend 0.889 |
| 10 | Alignment or crop path | small at 224 px crop geometry (2 seeds; TT1-FS pending) | small (2 seeds) | small (2 seeds) | not measured | not measured | **crop-path dependent** | crop-path dependent | crop-path dependent | not measured |
| 11 | Data volume | n/a (reference) | not volume: Bn ≈ B (2 seeds) | not volume: Bv ≈ B (2 seeds) | n/a | pending today (SbV arm) | n/a | n/a | n/a | n/a |
| 12 | Surround blend (whole-frame tools; a real blend, not an artefact) | relies on it | relies on it | reduced in degree, not removed | not measured | not measured | relies on it | relies on it | relies on it | reads the face too |
| 13 | Diffusion render path (one-photo reconstruction) | not measured | not measured | not measured | not measured | not measured | **used**: morph vs reconstruction 0.48 | **used**: 0.49 | not measured | **used**: 0.40 |
| 14 | GAN one-person render (MIPGAN) | not measured | not measured | not measured | not measured | not measured | **mostly second photo**: same-person flagged 95.5% | 87.0% | not measured | 100% |
| 15 | Training-partner trace (SMDD five partners) | mild structure (one person in ≤ 2.9% of morphs; use untested) | same (≤ 2.9%) | same (≤ 2.6%) | same (≤ 2.6%) | same (≤ 1.6%) | within-key AUC 0.716 (crop) / 0.702 (whole) | within-key AUC 0.768 (crop) / 0.835 (whole) | within-key AUC 0.909 (crop) / 0.808 (whole) | n/a (not SMDD) |
| 16 | Expression / capture detail of the FRLL smiling half | not measured (exposure only) | not measured (exposure only) | not measured (exposure only) | not measured (exposure only) | not measured | change < 1.5 pts | **+4.5 pts** with neutral-only genuine | not measured | change < 1.5 pts |
| 17 | Softness / detail loss | reads missing high frequency (TT1 H-new-1, unreviewed) | mostly softness on R2w vs R4 (2 seeds) | "not softness alone" at the ceiling (decides nothing); S4 vs S3 within lapvar strata 0.71–0.75 (5 seeds) | not measured | not measured | mixed (AR1 softened copies) | more than detail loss (not separated from ghosting) | **detail loss explains** at 61 px | more than detail loss |
| 18 | Processing cue in the surround of the development set (FFHQ landmark_combined) | below floor | below floor | level with floor; R2 fails on noise_std_border (5 seeds) | pending today (printed R1–R6) | not measured | n/a | n/a | n/a | n/a |
| 19 | Operating point / bounded output scale | no usable operating point at τ5 (0 of 5); τ_cam saturated | no usable operating point at τ5 (0 of 5) | τ5 usable within the calibration sources (4 of 5), but flags 32–43% of dev S3; τ_dev degenerate | not measured | not measured | own 0.5 rule catches 4% of AMSL | saturated genuine scores | not measured | own rule usable (0% unprocessed) |
| 20 | Morph engine of the training morphs (OpenCV-style trained, FaceMorpher held out) | "no engine gap" at the ceiling (decides nothing; 5 seeds) | same | same | not measured | not measured | n/a | n/a | n/a | n/a |

Columns pending (not yet in the matrix): SE1 (same-person blend arm), BB2 (second backbone), AB1 (protocol ablation and replication, seeds 408–412, leave-one-component-out arms that say which component removes which shortcut).

Routing of the fill experiments (lead, 13 Nov): ranks 2, 5, 6, 7, 8 to the owner of registered reads of the existing fresh-seed networks (PR1); rank 4 to the TT1 owner; rank 10 to the CB1 owner; rank 3 (JPEG pack) waits for the author; ranks 9 and 11 done here (G9, G11).

Bold words mark a cue that moved the column in the direction the shortcut predicts.

## Cell register

Path shorthand: **PN1/** = `experiments/PN1_protocol-network-first-tests/`; **TT1/** =
`experiments/TT1_threshold-transfer-unseen-genuine/`; **rev/** = `experiments/reviews/`; **CM** = `08_CUE_MATRIX.md`;
**NB** = `NOTEBOOK.md`. Line numbers refer to the files at git `aead489`.

### Row 1. Storage history of genuine photos (same photos native against shrunk and enlarged back)

| Cell | Number [interval] | Seeds | Data | Source (file:line) | Review | Status |
|---|---|---|---|---|---|---|
| 1-A | FFHQ genuine, own rule: 6.4–10.7% native → 21.1–30.7% history-matched (+14.7 to +21.8 points; 294 to 436 discordant persons, all one direction, McNemar p < 1e-88); paired share rising 0.576 ± 0.044 [0.527, 0.626]; mean shift +0.70 ± 0.07 genuine SD; flag ratio 2.8–3.5. Earlier seeds: test ladder R0_61 flagged 20.4 / 31.9% at own rule; FFHQ share rising 0.78 / 0.72; TT1 112 px camera photos 46.0 / 56.6% (paired shift +2.85 / +5.37 logit) | 403–407 (5); 401/402 for the earlier reads | development (FFHQ 2,000 persons; test ladder 191 hosts; TT1 417 camera photos) | rev/REVIEW_PN1_FS1_20261113.md:36-41, :45-51; PN1/result.md:296, :68, :169-182; TT1/result.md:96-98 | REVIEW_PN1_FS1, REVIEW_PN1_TIER1 (:29, :74), REVIEW_PN1_BATCH2 (F2, :37-45), REVIEW_TT1 (F2, :24-38) | reviewed (post hoc, descriptive: the registered contrast 2 was "uninformative" because A's positive control failed) |
| 1-B | At a near-trained size (FFHQ history copies about 64.6 px against the trained 61.2 px; "the evidential weight is carried by amsl112", PN1/prereg.md:791-793; unseen-size test C2P pending). FFHQ own-rule flag increase +2.5 to +5.5 points; share rising 0.243 ± 0.060 [0.180, 0.326]; mean shift +0.07 ± 0.04 SD; flag ratio 1.5–2.0; A above B on all three storage reads at every seed (Mann–Whitney p = 0.0079). Earlier seeds: test ladder 1.6 / 1.0%; FFHQ share 0.443 / 0.372; TT1 112 px 1.0 / 0.2% | 403–407; 401/402 | development | rev/REVIEW_PN1_FS1_20261113.md:45-55; PN1/result.md:63-68, :172, :176; TT1/result.md:96-97 | as 1-A | reviewed (post hoc; registered contrast 2 "uninformative") |
| 1-Sb | At a near-trained size (as 1-B). FFHQ own-rule flag increase +0.5 to +2.7 points; share rising 0.140 ± 0.034 [0.084, 0.175]; mean shift −0.09 ± 0.06 SD (reversed bulk shift); flags still rise, McNemar p ≤ 0.0012 on 4 of 5 seeds (403: p = 0.078). TT1 112 px camera photos 7.7 / 3.4% (401/402) | 403–407; 401/402 | development | rev/REVIEW_PN1_FS1_20261113.md:45-57; TT1/result.md:96-97 | REVIEW_PN1_FS1, REVIEW_TT1 | reviewed (post hoc; registered contrast 2 "uninformative") |
| 1-Sb (C2P) | Review Q4, can be said: "On 300 FFHQ persons no network was trained on, the four protocol-plus-splice networks that passed the platform gate (seeds 403, 405, 406, 407) raised their own-rule flag rate on stored genuine photos by +1.0 to +3.8 points at the trained size (61.2 px) and by −0.3 to +3.4 points at an untrained size (112.7 px). Their mean genuine logit moved toward genuine (−0.02 to −0.24 genuine SD). ... No plain network passed the gate, so these reactions are not compared with the plain recipe, and the registered storage contrast is uninformative." Sb 406 is the largest (native flags 6.0%; upper 95% bounds 6.5 and 5.9 points). Cannot be said: "reduced relative to the plain recipe" or "at most one third of it"; "removed", "absent" or "shortcut-free"; anything about B (one seed) or A. C2P-R (re-scoring on the training platform) awaits the author | 403, 405, 406, 407 | development | PN1/c2p_result.md:70-87; rev/REVIEW_PN1_C2P_20261113.md:112-127 | REVIEW_PN1_C2P_20261113 | reviewed |
| 1-Sp | — (registered printed read "storage share"; Sp s403 tar landed 13 Nov, not read) | 403–405 | development | PN1/prereg.md:746-761 | — | not measured (pending today) |
| 1-SbM3 | — (MS1 hold-out has fm61 and amsl112 stored copies of 300 unseen FFHQ persons) | 403–407 | development | experiments/MS1_multi-source-training-set/README.md:123-126 | — | not measured (pending today) |
| 1-ViTB | EER rise with the morphs' shrink-and-store history on the genuine photos: +12.8 to +19.0 points on AMSL, WebMorph and MAD22 FaceMorpher (our aligned frames in both arms), +12.2 [8.3, 16.3] on MorDIFF (raw files, corrected crop); at the threshold flagging 5% of unprocessed photos: 38–56% of history-matched photos against 10% of the same aligned photos without history; 68% on MorDIFF. On 2,000 FFHQ photos the 63–65 px history raises 99% of scores by 0.36 logit | one released network | benchmark audit (FFHQ part: development) | rev/REVIEW_RS1_20261112.md:79; rev/REVIEW_EV1_20261111.md:13-16 | REVIEW_RS1, REVIEW_EV1 | reviewed |
| 1-ViTL | −1.0 to +2.0 points on reproduced cells; MAD22 FaceMorpher +2.0 [0.6, 4.6], 17.6% flagged against 3.4% for aligned native. "Its genuine scores are saturated, so small effects cannot be excluded" | one network | benchmark audit | rev/REVIEW_RS1_20261112.md:81, :67-70 | REVIEW_RS1 | reviewed |
| 1-MFN | +19.6 (AMSL), +18.5 (WebMorph), +21.1 [17.2, 25.0] (MorDIFF, corrected crop) | one network | benchmark audit | rev/REVIEW_RS1_20261112.md:80, :48 | REVIEW_RS1 | reviewed |
| 1-SelfMAD | Own 0.5 rule: 0% of unprocessed genuine photos, 44.6% after a 50% shrink-and-enlarge, 55–79% with the DiM and MorDIFF histories, 97.1% stored small; history-matched photos flagged more often than the morphs in six families (MorDIFF 79 against 58%). Greedy-DiM raw E7 +80.8 points (own crop, raw files; holds only with all photos as genuine) | one network | benchmark audit (SelfMAD crop on our aligned frames; Greedy-DiM row on raw files) | rev/REVIEW_EV1_20261111.md:7-12; rev/REVIEW_RS1_20261112.md:74-75 | REVIEW_EV1, REVIEW_RS1 | reviewed |

### Row 2. Storage history of morphs (two-person morph native against its 61 px stored copy; "storage evasion")

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 2-A | "not available": the C2P gate (L40S, TF32 off) failed for all five A networks on the max condition (max abs Δlogit 0.119–0.249 > 0.10). The tier-1 read (R4_61 miss 0 of 191, seeds 401/402) is at the floor and not evaluable. A registered re-scoring on the training platform (C2P-R) awaits the author | 403–407 | development (MS1 FFHQ hold-out) | PN1/c2p_result.md:34-39; experiments/PR1_protocol-reads-existing-networks/result.md:131-132 | REVIEW_PN1_C2P_20261113 | not measured (pending: C2P-R) |
| 2-B | Not read: only seed 405 passed the C2P gate (C2P.2). Seeds 401/402: 61.2 px morph copies are B's training attacks and ladder misses are at the floor, so the tier-1 "P-f pass" is not evidence against evasion | 403–407 | development | PN1/c2p_result.md:37-39; rev/REVIEW_PN1_TIER1_20261112.md:70 | REVIEW_PN1_C2P_20261113 | not measured (pending: C2P-R) |
| 2-Sb | H-new-1 "falsified" on 4 of 4 read seeds (seed 404 not read, gate): "Stored morphs did not become easier to miss (morph shift +0.06 to +0.11 SD at 61.2 px and −0.02 to +0.04 SD at 112.7 px; storage evasion falsified on 4 of 4 read seeds). Development data only." | 403, 405, 406, 407 | development (300 unseen FFHQ persons) | PN1/c2p_result.md:37-39; rev/REVIEW_PN1_C2P_20261113.md:116 | REVIEW_PN1_C2P_20261113 | reviewed |
| 2-Sp, 2-SbM3, 2-released | — | — | — | — | — | not measured |

### Row 3. JPEG history (same photo native against JPEG re-saved)

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 3-A, 3-B, 3-Sb | The only JPEG pools read for PN1 networks are FRLL genuine jpeg90/70/50 (benchmark, read 12 Nov for seeds 401/402). No development JPEG pool exists | — | — | PN1/BENCHMARK_EXPOSURE.md:23; PN1/prereg.md:140, :263-268 | — | not measured (exposure only) |
| 3-Sp, 3-SbM3 | — | — | — | — | — | not measured |
| 3-ViTB | Morph-side storage ladder (morphs re-saved as JPEG) on GAN cells: "graded"; JPEG 50 rise +4.93, +8.82, +15.68 EER points (A41 H-new-142, earlier programme) | one network | benchmark audit | CM:73 (from `mambamorph-code` A41 meta.json) | not in a sprint review file | unreviewed |
| 3-ViTL | "JPEG quality 50 shifts every photo by 0.13 logits, which moves 42 photos across the development threshold and none across the release's own rule" (FRLL, our frames); scores saturated on our frames | one network | benchmark audit | rev/REVIEW_EV1_20261111.md:17-22 | REVIEW_EV1 | reviewed |
| 3-MFN | Flags 4.9% of genuine photos after JPEG 50 (A36, earlier programme, descriptive) | one network | benchmark audit | CM:74 | not in a sprint review file | unreviewed |
| 3-SelfMAD | Morph-side ladder: "no format cue" in our pipeline (MIPGAN-I/II); own-crop row not evaluable (A41) | one network | benchmark audit | CM:73 | not in a sprint review file | unreviewed |
| 3-note | Crop stored as JPEG 95 against PNG (300 images, same crop): mean shift morphs / photos ViT-B/16 +0.14 / +0.02, ViT-L/14 +0.40 / 0.00, MixFaceNet −0.14 / 0.00 logits; single images up to 16 logits (RS1 owner's check) | — | benchmark audit | NB:163; experiments/RS1_own-crop-rescore/rs1_jpeg_storage_check.json | not reviewed | unreviewed |

### Row 4. Unseen camera source (genuine photos of sources never seen in training; source comparison, not a paired control)

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 4-A | Fresh seeds of the TT1 read: TT1-FS registered (a2fef5c, ab81b35) and queued on pn1fs, expected end about 13:30, pending. Own rule fails (lower bound above 5%) on LFW/CALFW and AgeDB on both seeds; LFW 23.5% [22.2, 24.8] / 18.7%; mean family flag share F̄ 0.057 / 0.038; FFHQ genuine 22.5 / 9.9%. Fresh seeds: FFHQ genuine 6.4–10.7% | 401/402; FFHQ also 403–407 | development (TT1, about 21,000 photos, 8 sources; FFHQ) | TT1/result.md:44-50, :126-127, :144-145; rev/REVIEW_PN1_FS1_20261113.md:38 | REVIEW_TT1, REVIEW_PN1_FS1 | reviewed; two seeds only (TT1) |
| 4-B | "On both seeds every family's own-rule share has upper bound ≤ 10% (points 0.0–4.9%; also ≤ 8.3% by Clopper-Pearson). False alarms only, on black-bordered 1.7–3.5x frames; the same networks flag 17.8% / 6.4% of FFHQ genuine photos." τ_cam does not transfer (99–100% flagged). Fresh seeds: FFHQ 2.5–10.7% at own rule | 401/402; FFHQ 403–407 | development | TT1/result.md:47, :54-57, :146-147; PN1/tier_fs/fs.json (`seeds.*.B.flags_own.ffhq_bona_orig`) | REVIEW_TT1 (F4); fresh-seed FFHQ values printed by the registered reader, not discussed in the review | reviewed; two seeds only (TT1); fresh FFHQ unreviewed |
| 4-Sb | "Supported narrowly (AgeDB lower bounds 0.051 / 0.053 against 0.05)": fails CFP-FF (11.2 / 10.0%) and AgeDB (6.6 / 6.9%); F̄ 0.045 / 0.033; FFHQ 5.9 / 7.0%. Sb − B +0.021 [0.013, 0.029] / +0.031 [0.028, 0.033] (Sb flags more than B). Fresh seeds FFHQ 2.4–5.1% | 401/402; FFHQ 403–407 | development | TT1/result.md:48, :104-120, :148-149; PN1/tier_fs/fs.json | REVIEW_TT1 (F5, F7) | reviewed; two seeds only (TT1); fresh FFHQ unreviewed |
| 4-Sp | — (Sp's printed reads are S3 flags, landmark_combined, R1–R6 and storage share only, PN1/prereg.md:753-754; TT1-FS covers only the 15 FS1 networks) | — | — | — | — | not measured |
| 4-SbM3 | — (MS1 is built for this read: P1-T on the TT1 sources, CFD and KDEF held out) | 403–407 | development | experiments/MS1_multi-source-training-set/README.md:45-56 | — | not measured (pending today) |
| 4-ViTB | 0.1–2.6% of 2,000 FFHQ photos flagged at the 0.5 rule; 4–11% of FRLL | one network | development (FFHQ) and benchmark audit (FRLL) | rev/REVIEW_EV1_20261111.md:13-16 | REVIEW_EV1 | reviewed |
| 4-ViTL | Earlier "22% FFHQ" withdrawn (saturated scores on our frames); no replacement in the reviewed record | — | — | rev/REVIEW_EV1_20261111.md:17-22 | REVIEW_EV1 | not measured |
| 4-MFN | At one threshold flags 73.0% of FRLL, 55.3% of FEI, 14.3% of FFHQ photos (A36, descriptive) | one network | benchmark audit and development | CM:84 | not in a sprint review file | unreviewed |
| 4-SelfMAD | Flags 25–47% of genuine ladder photos (FRGC, colorFERET R0) at its FRLL threshold: "a calibration shift, not an operating point" | one network | development (ladder) | rev/REVIEW_AR1_20261111.md:83 | REVIEW_AR1 | reviewed |

### Row 5. Image border or frame (same photo with and without the black border of our aligner)

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 5-A, 5-B, 5-Sb | Fresh seeds: TT1-FS pending today. Registered TT-H3: inconclusive for all 11 networks. "The border alone shifts camera photos by +0.04 to +0.10 logit (paired median; CFP-sized borders +0.21 to +0.38), about 10–20% of the unseen excess except CFP-FF." On FFHQ mixed in sign: B_s401 flags 17.8 → 13.0%, Sb_s402 7.0 → 13.4% (border-matched). Range over all networks; not split by arm in the reviewed text | 401/402 | development (TT1 camera photos, FFHQ) | TT1/result.md:66-74; rev/REVIEW_TT1_20261113.md:40-50 | REVIEW_TT1 (F3) | reviewed; two seeds only |
| 5-Sp, 5-SbM3 | — (the TT1 fresh-seed block, `TT1/prereg_fs1_block.md`, registers the same border reference for fresh networks) | — | — | — | — | not measured |
| 5-ViTB | MorDIFF tight frame alone at full resolution: +0.42 logit; with the border held equal, the 65 px history alone +1.35 [1.14, 1.55] | one network | benchmark audit (FRLL photos) | experiments/EV1_fixed-threshold-reread/result.md:93-97 | EV1 amendment 2; the lead records that every number matched the reviewer's recomputation (NB:141), but no review file covers it | unreviewed |
| 5-ViTL, 5-MFN | — (EV1 amendment 2 gives no frame-alone number for these releases) | — | — | — | — | not measured |
| 5-SelfMAD | Frame alone +0.72 logit; history alone with the border equal +4.64 [4.37, 4.82] | one network | benchmark audit | experiments/EV1_fixed-threshold-reread/result.md:93-97 | as 5-ViTB | unreviewed |

### Row 6. Warp only, no second person (R2w against R0; and R2w against R4)

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 6-A | Five fresh seeds (PR1 Z4, test ladder, own rule, OpenCV): R2w flagged 0%; R4 vs R2w 1.000 → "not flagged" (R2w is not in A's training). Seeds 401/402 the same. Caveat (tier-1 review Q4): "Mostly softness": networks trained only to flag shrink-and-enlarge copies reach R4 vs R2w 0.84–0.86 and one band-power statistic 0.888 | 403–407 (and 401/402) | development (test ladder) | experiments/PR1_protocol-reads-existing-networks/result.md:92-94; rev/REVIEW_PN1_TIER1_20261112.md:25, :102 | REVIEW_PR1_PART1_20261113, REVIEW_PN1_TIER1 | reviewed |
| 6-B | R2w flagged 0%; R4 vs R2w 1.000 → "not flagged" (trained negative, in distribution) | 403–407 | development | experiments/PR1_protocol-reads-existing-networks/result.md:94 | REVIEW_PR1_PART1_20261113 | reviewed |
| 6-Sb | R2w flagged 0–0.5%; R4 vs R2w 1.000 → "not flagged" (trained negative); face-blanked test 0.987–1.000 | 403–407 | development | experiments/PR1_protocol-reads-existing-networks/result.md:94; PN1/tier_fs/fs.json | REVIEW_PR1_PART1_20261113 | reviewed |
| 6-Sp, 6-SbM3 | — | — | — | — | — | not measured |
| 6-ViTB | Small: warp share 0.07 / 0.01, interval excludes 0.5 on OpenCV; registered "reads morphing". R0 → R2w 0.566 [0.55, 0.58] (OpenCV) / 0.511 (FaceMorpher); R2w vs R4 0.986 / 0.984 | one network | development (536 FRGC/colorFERET hosts, our frames) | experiments/AR1/result.md:106-107 | REVIEW_AR1 (:7, :100) | reviewed |
| 6-ViTL | R0 → R2w 0.427 / 0.463; R2w vs R4 0.992 / 0.994 | one network | development | experiments/AR1/result.md:108-109 | REVIEW_AR1 | reviewed |
| 6-MFN | Small: warp share 0.15 / 0.05. R0 → R2w 0.587 [0.58, 0.60] / 0.528; R2w vs R4 0.890 / 0.901 | one network | development | experiments/AR1/result.md:110-111 | REVIEW_AR1 | reviewed |
| 6-SelfMAD | R0 → R2w 0.710 [0.69, 0.73] / 0.650 (share of the full step 0.25 / 0.16; registered verdict "mixed" on OpenCV); R2w vs R4 0.966 / 0.984 | one network | development | experiments/AR1/result.md:104-105; rev/REVIEW_AR1_20261111.md:19 | REVIEW_AR1 | reviewed |

### Row 7. Same-person morph (R3: two photos of one person blended)

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 7-A | Five fresh seeds (PR1 Z4): R3 flagged 94.8–99.5%, R4 vs R3 0.72–0.75; mirror self-morph R3m 97.9–99.5%, R4 vs R3m 0.77–0.79 → "flagged like a morph". Seeds 401/402: 91–99% (tier-1 review) | 403–407 | development (test ladder) | experiments/PR1_protocol-reads-existing-networks/result.md:95-96; rev/REVIEW_PN1_TIER1_20261112.md:101 | REVIEW_PR1_PART1_20261113 | reviewed |
| 7-B | R3 90.6–95.3%, R4 vs R3 0.75–0.79; R3m 94.8–97.4% → "flagged like a morph" | 403–407 | development | experiments/PR1_protocol-reads-existing-networks/result.md:95-96 | REVIEW_PR1_PART1_20261113 | reviewed |
| 7-Sb | R3 83.2–88.5%, R4 vs R3 0.80–0.85; R3m 95.8–96.9% → "flagged like a morph". Engine contrast on R4 vs R3 (Z3b, amendment 3): "inconclusive" | 403–407 | development | experiments/PR1_protocol-reads-existing-networks/result.md:95-96, :120-122 | REVIEW_PR1_PART1_20261113 (Z4); Z3b unreviewed | reviewed |
| 7-Sp, 7-SbM3 | — | — | — | — | — | not measured |
| 7-released | "A same-person morph is flagged almost as readily (0.81 to 0.96). Swapping in a second, dissimilar person adds 0.60 to 0.75, an upper bound." R2w → R3 / R3 → R4: ViT-B/16 0.948 / 0.695 (OpenCV); ViT-L/14 0.896 / 0.749; MixFaceNet 0.813 / 0.619; SelfMAD 0.922 / 0.689 (FaceMorpher: 0.948/0.672, 0.926/0.737, 0.841/0.598, 0.959/0.663) | one network each | development | experiments/AR1/result.md:102-111; rev/REVIEW_AR1_20261111.md:101 | REVIEW_AR1 | reviewed |
| 7-note | Class status: same-person morphs are "single-subject" images under the lead's working rule (PN1/prereg.md:26-30); whether flagging them is an error awaits the author's class ruling (`14_CLASS_DEFINITIONS.md`) | — | — | — | — | — |

### Row 8. Same-person face splice (S3: R3 inside the face hull, R2w outside)

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 8-A, 8-B | Test ladder S3 flagged: A 2.1–5.8%, B 0.5–3.7% → "not flagged". But A and B miss most face splices (development S4 missed 91–98% for B; 93–97% for A, B, C, Bv in TT1 H-new-4), so a low S3 rate is not evidence of avoiding the cue | 403–407 | development | experiments/PR1_protocol-reads-existing-networks/result.md:97-98; rev/REVIEW_PN1_FS1_20261113.md:85; TT1/result.md:179-185 | REVIEW_PR1_PART1_20261113, REVIEW_PN1_FS1 | reviewed |
| 8-Sb | Test ladder S3 flagged 37.2–48.2%, S4 vs S3 0.72–0.74 → "inconclusive" (trained negative); development S3 31–41%. Sb's own training S3 rows are flagged nearly as often (26–37%): a training-level problem; the flagged training rows are largely the same on every seed (Z1b-1, unreviewed) | 403–407 | development | experiments/PR1_protocol-reads-existing-networks/result.md:28-46, :97, :112-115; rev/REVIEW_PN1_FS1_20261113.md:84-87 | REVIEW_PR1_PART1_20261113 (finding 2), REVIEW_PN1_FS1; Z1b unreviewed | reviewed |
| 8-Sp | — (registered printed read "development S3 own-rule flags") | 403–405 | development | PN1/prereg.md:751-755 | — | not measured (pending today) |
| 8-SbM3 | — (FFHQ supplies no S3; the FRGC/colorFERET S3 rows equal Sb's) | — | — | experiments/MS1_multi-source-training-set/README.md:124-125 | — | not measured |
| 8-released | S3 vs S4 (second identity inside the face only), OpenCV only (FaceMorpher splice reads are "not used for conclusions", AR1/result.md:279-280): SelfMAD 0.579, ViT-B/16 0.473, ViT-L/14 0.519, MixFaceNet 0.511. S3 flag rates not measured | one network each | development | experiments/AR1/result.md:282-301 | values not restated in REVIEW_SPLICE | unreviewed |

### Row 9. Blending seam (S0: seam-only negative without a second person or a blend)

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 9-A | S0 flagged 0–0.5%; S4 vs S0 0.75–0.83 → "inconclusive" (0–0.5% seam-only flags; weak S4 detection) | 403–407 | development (test ladder) | experiments/PR1_protocol-reads-existing-networks/result.md:98 | REVIEW_PR1_PART1_20261113 | reviewed |
| 9-B | S0 flagged 0%; S4 vs S0 0.68–0.78 → "inconclusive" (the verdict comes from weak S4 detection: 91–98% of S4 missed). Seeds 401/402: S0 vs S4 0.682 / 0.725; development S0 0 of 100 | 403–407 (and 401/402) | development | experiments/PR1_protocol-reads-existing-networks/result.md:98; rev/REVIEW_PN1_BATCH2_FZ2A12_AR1A11_20261112.md:28 | REVIEW_PR1_PART1_20261113, REVIEW_PN1_BATCH2 | reviewed |
| 9-Sb | Five fresh seeds: S0 flagged 0–0.5% (development 0 of 100 on all five; test 1 of 191 once), S4 vs S0 0.985–0.994 → "seam-only not flagged" (trained negative; experiments/PR1_protocol-reads-existing-networks/result.md:18, :98). Seeds 401/402: S0 is a training negative. S0 vs S4 (test) 0.983 / 0.989; excess over the 3-statistic floor (seam tone, sharpness ratio, band5) +0.125 / +0.131 (lower bounds +0.08 / +0.09); development S0 placed 0 of 100 on both seeds (rev/PRERUN_PN1_SP_20261112.md:10; PN1/prereg_remedies_v2_draft.md:50). The OpenCV seam "is equal in size but not in kind" (a colour step separates S4 from S0 at about 0.71) | 401/402 | development | rev/REVIEW_PN1_BATCH2_FZ2A12_AR1A11_20261112.md:28-29; rev/PRERUN_PN1_SP_20261112.md:10; rev/REVIEW_SPLICE_20261111.md:19, :99 | REVIEW_PN1_BATCH2, REVIEW_SPLICE | reviewed |
| 9-Sp | — (registered prediction 1: Sp places at least max(2·Sb, Sb + 0.10) of the 100 development S0 images) | 403–405 | development | PN1/prereg.md:746-755 | — | not measured (pending today) |
| 9-SbM3 | — | — | — | — | — | not measured |
| 9-released | Seam alone: "No release flags it: R2w4 vs S0 is 0.46 to 0.54." Face blend: "Only SelfMAD reads a face-confined blend beyond simple cues (0.889 seam-matched), possibly as a blend boundary. The MADation CLIP releases read mainly surround ghosting; MixFaceNet-MAD mainly detail loss." Swap-splice: "No released detector is shown to read more than one simple statistic, interior sharpness, on spliced morph vs swap-splice: inside-hull Laplacian variance alone gives 0.926 against SelfMAD's 0.888." Post hoc AR1 amendment 9: excess of S0 vs S4 over the 3-statistic floor (0.861): SelfMAD +0.021 [−0.013, 0.057], ViT-B/16 −0.185, ViT-L/14 −0.138, MixFaceNet −0.231 | one network each | development | rev/REVIEW_SPLICE_20261111.md:21, :100; rev/REVIEW_FZ2_AR1A10_20261112.md:78; experiments/AR1/result.md:306-317 | REVIEW_SPLICE, REVIEW_FZ2_AR1A10; amendment 9 unreviewed | reviewed (seam alone, swap-splice); amendment 9 unreviewed |

### Row 10. Alignment or crop path (same images through two crop or scoring paths)

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 10-A, 10-B, 10-Sb | Camera photos through the unseen sources' crop geometry at 224 px (1.7x enlargement, black border): "every arm shifts by only +0.03 to +0.07, with 0–1% flagged". At 112 px (3.5x) A flags 46.0 / 56.6%, B 1.0 / 0.2%, Sb 7.7 / 3.4% (geometry and storage together; counted in row 1). Scoring platform: GB10 / torch 2.12 not equivalent to A100 (best 0.088 logit, TT1 H-new-5); A100 SXM4-40/80 and PCIe-40 byte-identical (PN1 amendment-14 gate) | 401/402 | development | rev/REVIEW_TT1_20261113.md:24-38; TT1/result.md:186-189; PN1/result.md:204-207 | REVIEW_TT1 (F2); platform reads unreviewed | reviewed (geometry); two seeds only |
| 10-Sp, 10-SbM3 | — | — | — | — | — | not measured |
| 10-released | The authors' crop script "fails on 95% of MorDIFF morphs (strips, median 4 px) ... and returns nothing for 34% of FRLL FaceMorpher morphs"; scores depend on the JPEG decoder build (up to 5.9 logits) and face-detector boxes differ between GPUs for about 1 image in 10; labels flip with crop variant (ViT-B/16 AMSL 3.92 variant 1 against 6.38 variant 2). Own crop on raw files against our aligned frames as the genuine class: ViT-B/16 AMSL EER 3.91 → 5.45, MixFaceNet five-family mean FRLL 9.19 → 12.54 (crop v1; includes the FaceMorpher cell where the release crop fails), MAD22 13.66 → 17.09. SelfMAD: no crop-path comparison in the cited sources (10-SelfMAD not measured) | one network each | benchmark audit | rev/REVIEW_RS1_20261112.md:9-26, :55-59, :83-84; NB:202; experiments/CB1_competitor-baselines-corrected-mad22/cb1_released_rs1_bpcer.csv:2-3; CB1 result.md:106-108 | REVIEW_RS1; CB1 numbers: a results review was applied (CB1 README:118) but no review file is in `experiments/reviews/` | reviewed (RS1); CB1 part unreviewed |

### Row 11. Data volume (same arm at another number of unique images or rows)

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 11-A | Reference. A trains on 1,992 unique items against 7,762 for B and 8,386 for Sb at equal steps | — | — | rev/REVIEW_PN1_FS1_20261113.md:109 | REVIEW_PN1_FS1 | n/a |
| 11-B | Bn (protocol cut to A's unique count) equals B on storage: test ladder R0_61 own-rule 3.1 / 0.5% (B 1.6 / 1.0%); FFHQ share rising 0.414 / 0.340 (B 0.443 / 0.372); TT1 F̄ Bn_s402 0.001 (B 0.002) | 401/402 | development | PN1/result.md:68, :172-177; TT1/result.md:128-136 | REVIEW_PN1_TIER1, REVIEW_PN1_BATCH2 (F2) | reviewed; two seeds only |
| 11-Sb | Bv (B at Sb's row volume) equals B: face-only R4 vs R2w 0.838 / 0.861 (B 0.840 / 0.865; Sb 0.938 / 0.957), "so the change is not row volume"; unseen-source flags Bv − B between −0.003 and 0 at every cut-off | 401/402 | development | rev/REVIEW_PN1_BATCH2_FZ2A12_AR1A11_20261112.md:24-35; rev/REVIEW_TT1_20261113.md:66-81 | REVIEW_PN1_BATCH2 (F1), REVIEW_TT1 (F7) | reviewed; two seeds only |
| 11-Sp | Sp repeats each image about 8% more than Sb (disclosed) | — | — | PN1/prereg_remedies_v2_draft.md:47 | — | n/a |
| 11-SbM3 | — (SbV: Sb rows repeated to SbM3's 13,414 rows, the volume control) | 403–407 | development | experiments/MS1_multi-source-training-set/README.md:45-50 | — | not measured (pending today) |
| 11-released | — | — | — | — | — | n/a |

### Row 12. Surround blend (whole-frame morph tools blend hair, ears and background)

The reviewers rule this a real blend of full-frame morphs, not an artefact ("a surround read on R4 is a real signal,
not a shortcut", rev/REVIEW_PN1_BATCH2_FZ2A12_AR1A11_20261112.md:34). It is listed because it governs face-spliced
attacks.

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 12-A | Face-blanked R2w vs R4 0.990–1.000 (fresh seeds); scale-free AUC loss from whole-frame to face-only-splice morphs (FFHQ landmark_complete → landmark_combined) 0.157 / 0.225 (401/402); fresh seeds 0.22–0.30 (registered printed read `printed_R1_R6.*.R6.auc_loss` in PN1/tier_fs/fs.json) | 401/402 (loss); 403–407 (blanked) | development | PN1/result.md:264-266 (owner's post hoc read requested by the A14 review); PN1/tier_fs/fs.json | — | unreviewed |
| 12-B | "Scale-free, Sb loses 0.09 to 0.11 AUC from complete to combined, B, Bn, C and Bv 0.24 to 0.28"; every network ranks the whole-frame morph above the face-only splice of the same pair for 95 to 99% of pairs. Fresh seeds: B loss 0.28–0.35 (fs.json printed read, unreviewed) | 401/402; 403–407 | development | PN1/result.md:230-236; PN1/tier_fs/fs.json | REVIEW_PN1_A14_DEVREAD (401/402) | reviewed (401/402); fresh seeds unreviewed |
| 12-Sb | Loss 0.09–0.11 (401/402); "Surround reliance is reduced in degree, not removed"; fresh-seed risk list: "Surround reliance remains (R6 AUC loss from complete to combined 0.11–0.18)" | 401/402; 403–407 | development | PN1/result.md:233-236; rev/REVIEW_PN1_FS1_20261113.md:182 | REVIEW_PN1_A14_DEVREAD, REVIEW_PN1_FS1 | reviewed |
| 12-released | "0.76 to 0.92 with the face blanked" (reviewed wording); spliced (face-only blend) R2w4 vs S4, OpenCV: ViT-B/16 0.66, ViT-L/14 0.71, MixFaceNet 0.60, SelfMAD 0.91 | one network each | development | experiments/AR1/result.md:36-43; rev/REVIEW_AR1_20261111.md:102 | REVIEW_AR1, REVIEW_SPLICE | reviewed |

### Row 13. Diffusion render path (morph against a one-photo reconstruction rendered and stored identically)

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 13-A, B, Sb, Sp, SbM3 | — (only tier-0 frozen heads were read on diffusion images) | — | — | — | — | not measured |
| 13-ViTB, ViTL, SelfMAD | "Same-pair DiffAE morphs are not ranked above one-photo reconstructions rendered and stored identically: 0.480 (MADation ViT-B/16), 0.486 (ViT-L/14), 0.403 (SelfMAD); upper bounds at most 0.59." ViT-B/16 (corrected crop) flags 100% of reconstructions at the 5% threshold; morph vs reconstruction 0.664 [0.562, 0.754] | one network each | benchmark audit (MorDIFF on FRLL photos) | rev/REVIEW_AD1_AG5_C_20261111.md:17ff (evidence level :12: post hoc, one genuine pool, released weights scored once); rev/REVIEW_RS1_20261112.md:32-37 | REVIEW_AD1_AG5_C, REVIEW_RS1 | reviewed |
| 13-MFN | — | — | — | — | — | not measured |

### Row 14. GAN one-person render (MIPGAN output of one photo, or of two photos of one person)

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 14-A, B, Sb, Sp, SbM3 | — | — | — | — | — | not measured |
| 14-ViTB, ViTL, SelfMAD | "Most of the separation is already present between one photo and two photos of the same person": R2 > R3 0.794 / 0.812 / 0.716 (ViT-B/16 / ViT-L/14 / SelfMAD own crop), R3 > R4 0.661 / 0.720 / 0.653; same-person MIPGAN morphs flagged 0.955 / 0.870 / 1.000 at the corrected-MAD22 threshold, two-person 0.985 / 0.990 / 1.000 | one network each | development pool (threshold from a benchmark cell) | rev/REVIEW_AG1_20261112.md:24-30 | REVIEW_AG1 | reviewed |
| 14-MFN | — | — | — | — | — | not measured |

### Row 15. Training-partner trace (SMDD's 15,000 training morphs share five second contributors)

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 15-A, B, Sb, Sp, SbM3 | Manifest audit G9 (registered, `prereg.md`; `g9_partners.json`, `src/SA1/g9_partners.py`): registered reading "partner structure present" (rule: no contributor in more than 1% of unique morphs). Largest share of unique training morphs that contain one person: A, B, C 2.9% (25 of 852), Bn 3.1% (21 of 674), Sb, Sp, SbV 2.6% (25 of 976), SbM3 1.6% (25 of 1,526); 388 distinct second contributors (SbM3 799); the most repeated persons are AF0 FRGC persons in af0_u50 morphs. For scale, SMDD: 5 second contributors for 15,000 morphs. Whether any arm uses this structure is not tested | — | development (manifests only) | g9_partners.json | — | unreviewed (manifest audit; use not tested) |
| 15-ViTB | Released network, within-key AUC (per key, its 5 trained-partner morphs over its 5 SMDD evaluation-partner morphs, mean over 500 keys): 0.716 [0.702, 0.729] on its own crop path (whole file 0.702 [0.688, 0.716]); one network, key bootstrap B = 10,000 only; audit set, not a benchmark; no TTA. Without SMDD's five partners (retrained ViT-B/16 arms c, b′, e, f): 0.53–0.59. Secondary detail: logit gap 0.43 (crop; scale-dependent, not comparable across networks, never used to rank paths or networks). Benchmarks contain no training partner, so the trace has no direct effect on them (REVIEW_SM1:106) | one network | development (SMDD audit set) | experiments/SM1_smdd-partner-audit-and-rebuild/result.md:675-699 (A23, registered 80ba899); rev/REVIEW_SM1_20261111.md:27 | REVIEW_SM1_A23_20261113, REVIEW_SM1 | reviewed |
| 15-ViTL | "released network, within-key AUC 0.768 [0.754, 0.780] on its own crop path (whole file 0.835 [0.825, 0.845]); one network, key bootstrap only; audit set, not a benchmark; no TTA". Like-for-like input path (whole image): released 0.835 against retrained 0.756 (row 15b); neither interval includes seed variance, so no difference between released and retrained is claimed. Secondary detail: logit gap 0.95 [0.78, 1.12] crop, 0.45 [0.37, 0.55] whole file; the gap and the AUC rank the two paths in opposite orders, so the gap must not rank paths or networks | one network | development (SMDD audit set) | experiments/SM1_smdd-partner-audit-and-rebuild/result.md:675-699 (A23, registered 80ba899); SM1/result.md:215 | REVIEW_SM1_A23_20261113 (F3), REVIEW_SM1 | reviewed |
| 15-MFN | Released network, within-key AUC 0.909 [0.901, 0.917] crop path (whole file 0.808 [0.799, 0.816]); one network, key bootstrap only; audit set; no TTA. Different architecture and resolution: comparison with the CLIP releases descriptive. Secondary detail: logit gap 13.36, which mostly reflects its score spread | one network | development (SMDD audit set) | experiments/SM1_smdd-partner-audit-and-rebuild/result.md:675-699 (A23, registered 80ba899) | REVIEW_SM1_A23_20261113 (F4), REVIEW_SM1 | reviewed |
| 15-SelfMAD | SelfMAD is not trained on SMDD | — | — | — | — | n/a |

**Row 15b, retrained networks, kept apart from the released networks (a retrained AUC is compared with a released one only on the same input path, whole image, and no difference is claimed; logit gaps are never set beside AUCs).**

| Network | Retrained, 2 seeds, within-key AUC | Released network, same metric |
|---|---|---|
| MADation-recipe ViT-L/14 (LoRA) retrained on the SMDD release files (SM1 arm a, A14) | "within-key AUC, morphs with SMDD's five training partners over morphs with SMDD evaluation partners (same first contributor, 500 keys), 0.756 [0.746, 0.765], 2 seeds (401: 0.755; 402: 0.756), key bootstrap B = 10,000 (seed variance not included); whole image, no TTA; audit set, not a benchmark." Source: experiments/SM1_smdd-partner-audit-and-rebuild/result.md:654-674 (registration b4cb17b; review applied in 49dbf12; review rev/REVIEW_SM1_A14_VITL_20261113.md) | released ViT-L/14 on the same whole-image path: 0.835 (15-ViTL); no difference claimed |
| MADation-recipe ViT-B/16 (LoRA) retrained on SMDD (SM1 A13, arm a) | 0.7566 (arm b 0.8168, arm b′ 0.5667), rev/REVIEW_SM1_12FITS_A15_20261112.md:17 | see 15-ViTB (a different network) |

### Row 16. Expression and capture detail of the FRLL smiling half (genuine class with and without the smiling photos)

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 16-A, B, Sb, Sp | Only FRLL neutral-only reads exist (benchmark, 12 Nov exposure). G11 (registered): a paired pool exists in held-out development sources: CFD 158 persons with neutral and happy images (all in the main CFD subset; MS1 holds their neutral images aligned), KDEF 70 persons with front neutral and happy images of the same session (`g11_expression_pool.json`). Not scored | — | — | PN1/tier1/*.json (`FRLL_bona_native_neutral`); PN1/BENCHMARK_EXPOSURE.md:23 | — | not measured (exposure only) |
| 16-SbM3 | — | — | — | — | — | not measured |
| 16-ViTL | Neutral-only genuine class raises the error by 4.5 points on average over 11 cells (95% interval 3.4 to 5.8; AMSL 17.7 to 24.5); for this release the cause is mainly capture detail of the smiling files, not expression (C1c) | one network | benchmark audit | rev/REVIEW_C1b_20261111.md:10-12; CM:16-17 | REVIEW_C1b (+4.5); the C1c capture-detail attribution is not in a review file | reviewed (C1b); C1c attribution unreviewed |
| 16-ViTB, 16-SelfMAD | "The fine-tuned ViT-B/16 release and SelfMAD change by under 1.5" | one network each | benchmark audit | rev/REVIEW_C1b_20261111.md:12-13 | REVIEW_C1b | reviewed |
| 16-MFN | — | — | — | — | — | not measured |

### Row 17. Softness / detail loss (softened or detail-matched control)

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 17-A | Consistent with reading missing high frequency: geometry-matched 112 px camera photos (face-box Laplacian variance 7.3) score 2.26 / 4.91 logits above pack photos (10.7); OLS slope of logit on log variance −0.88 (measurement only, not causal) | 401/402 | development | TT1/result.md:173-178 | — (post-result amendment) | unreviewed; two seeds only |
| 17-B | "Mostly softness. AD4's morph-free networks, which never saw a blend, reach R4 vs R2w 0.84 to 0.86 on the ladder. One band-power statistic gives 0.888." [AD4 wording since 13 Nov: "trained only to flag shrink-and-enlarge copies" replaces "never saw a morph" alone, experiments/AD4/result.md:132] (said of all 8 tier-1 fits) | 401/402 | development | rev/REVIEW_PN1_TIER1_20261112.md:102 | REVIEW_PN1_TIER1 | reviewed; two seeds only |
| 17-A, 17-B, 17-Sb (PR1 Z6) | "not softness alone" for A, B, Sb (5 of 5), read at the ceiling: it rests on one statistic (lapvar_face), the strata cover 60% of rows, and R2w is a trained negative of B and Sb. Informative part: Sb's S4 vs S3 within lapvar strata 0.71–0.75 on all five seeds (lapvar alone 0.50) | 403–407 | development | experiments/PR1_protocol-reads-existing-networks/result.md:100-108 | REVIEW_PR1_PART1_20261113 (finding 4) | reviewed (A and B keep their earlier entries as the matrix headline) |
| 17-Sp, SbM3 | — | — | — | — | — | not measured |
| 17-released | Softened warp-only against native two-person morph: MixFaceNet 0.58 / 0.78 ("detail loss explains" at 61 px); ViT-B/16 0.79 / 0.96 ("mixed"); SelfMAD 0.98 / 0.90 and ViT-L/14 0.97 / 0.99 ("more than detail loss"); ViT-L/14's "more than detail loss" "is not separated from ghosting" | one network each | development | experiments/AR1/result.md:30-35; rev/REVIEW_SPLICE_20261111.md:30, :100 | REVIEW_SPLICE | reviewed |
| 17-note | Networks trained only to flag shrink-and-enlarge copies of synthetic faces (AD4) reach 0.0% EER on MorDIFF native in all five seeds [0.0, 0.0] (references 37.3 to 60.8%): low error there is not by itself evidence of morph detection. Matching resolution history does not remove the cue on MorDIFF (2.4%) | 5 seeds | benchmark audit | experiments/AD4/result.md:43, :54 (cluster-stack readings, review corrections applied in ad792a0); rev/REVIEW_AD4_VITB_20261111.md | REVIEW_AD4_VITB and the AD4 cluster-stack review (applied ad792a0) | — |

### Row 18. Processing cue in the surround of the development set (FFHQ landmark_combined)

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 18-A, 18-B | Below the best single statistic (noise_std_face 0.886) and below the 27-statistic ladder baseline (0.814) on every seed; noise_std_border alone separates the set at 0.786 | 403–407 | development | PN1/result.md:227; rev/REVIEW_PN1_FS1_20261113.md:68 | REVIEW_PN1_FS1 | reviewed |
| 18-Sb | Sb 0.860 ± 0.030; gaps to the best single statistic −0.071 to −0.001; "The gain is not separated from simple statistics": Sb's within-class correlation with noise_std_border on genuine images 0.18–0.22, above 0.2 on three seeds; Sb − B within noise_std_border deciles +0.12 to +0.22 (post hoc) | 403–407 | development | PN1/result.md:294; rev/REVIEW_PN1_FS1_20261113.md:59-76 | REVIEW_PN1_FS1 | reviewed |
| 18-Sp | — (printed R1–R6) | 403–405 | development | PN1/prereg.md:753-754 | — | not measured (pending today) |
| 18-SbM3 | — | — | — | — | — | not measured |
| 18-released | The set is a development set for candidate networks only | — | — | — | — | n/a |

### Row 19. Operating point / bounded output scale

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 19-A, 19-B | Head linear on normalised features, logits bounded near ±3.87; camera photos at −3.67 (SD 0.02–0.19), τ_cam 0.03–0.10 logit above them; every τ_cam mark reads a saturated band | 401/402 | development | PN1/result.md:85-89; rev/REVIEW_PN1_TIER1_20261112.md:39-48 | REVIEW_PN1_TIER1 | reviewed; two seeds only |
| 19-Sb | At 5% false alarms on R0 + AF0 (FINAL's τ_dev), every arm and seed flags 96–98% of FFHQ genuine photos (threshold about −3.6 for A and B, −3.4 for Sb) | 403–407 | development | rev/REVIEW_PN1_FS1_20261113.md:111-114 | REVIEW_PN1_FS1 (F10) | reviewed |
| 19-A, B, Sb (PR1 Z2a, τ5) | τ5 = smallest cut-off with ≤ 5% flags in each calibration source (FRGC/colorFERET dev photos, FFHQ calibration half); "within the calibration sources". A: "no usable operating point" (0 of 5; fails through history-matched FFHQ copies, 19–22% flagged); B: "no usable operating point" (0 of 5; landmark_combined missed 62–70%); Sb: "usable operating point" (4 of 5; seed 403 misses 0.39), but G_max excludes one-person images and Sb flags 32–43% of dev S3 at τ5. Unseen-source version (Z2b-τ5) waits for TT1-FS | 403–407 | development | experiments/PR1_protocol-reads-existing-networks/result.md:48-63 | REVIEW_PR1_PART1_20261113 (finding 5) | reviewed |
| 19-Sp, 19-SbM3 | — | — | — | — | — | not measured |
| 19-ViTB | "The same rule catches only 4.0% of AMSL, 0.8% of StyleGAN2 and 21% of WebMorph morphs, so the release rule is not a meaningful operating point for this release" | one network | benchmark audit | rev/REVIEW_RS1_20261112.md:49 | REVIEW_RS1 | reviewed |
| 19-ViTL | Genuine logits saturated (median −12.80, SD 0.056, own crop); all genuine logits within 0.3 logit on our frames | one network | benchmark audit | rev/REVIEW_RS1_20261112.md:68; rev/REVIEW_EV1_20261111.md:17-19 | REVIEW_RS1, REVIEW_EV1 | reviewed |
| 19-MFN | — | — | — | — | — | not measured |
| 19-SelfMAD | Own 0.5 rule needs no threshold pool: 0% of unprocessed genuine photos flagged | one network | benchmark audit | rev/REVIEW_EV1_20261111.md:7-12 | REVIEW_EV1 | reviewed |

### Row 20. Morph engine of the training morphs (OpenCV-style in training; FaceMorpher never trained)

| Cell | Number [interval] | Seeds | Data | Source | Review | Status |
|---|---|---|---|---|---|---|
| 20-A, 20-B, 20-Sb | Every ladder R4, S0, S3, S4 training row is OpenCV-style. AUC(R4 vs R2w) and (R4 vs R0) 1.0000 for both engines, every arm and seed; misses 0–0.5%. Registered "no engine gap", read at the ceiling: "It gives no evidence that our training engine transfers beyond whole-frame ladder morphs". Engine contrast on the non-saturated R4 vs R3 axis (Z3b, amendment 3, unreviewed): "inconclusive" (Sb Δ3 +0.006 to +0.029) | 403–407 | development | experiments/PR1_protocol-reads-existing-networks/result.md:76-88, :120-122 | REVIEW_PR1_PART1_20261113 (finding 1); Z3b unreviewed | reviewed |
| 20-Sp, 20-SbM3 | — | — | — | — | — | not measured |
| 20-released | Released detectors are not trained on our engines | — | — | — | — | n/a |

## Counts (version 2, updated 13 Nov 09:50 with PR1 part 1 and C2P)

Counted over the 180 cells of the matrix (20 rows × 9 columns); a register line that covers several columns counts
once per column. Row 15b (retrained networks) is outside the matrix. See `cells.csv` (written by `src/SA1/cells.py`).

| Status | Our arms (A, B, Sb, Sp, SbM3; 100 cells) | Released detectors (80 cells) | All 180 |
|---|---|---|---|
| reviewed | 40 (12 of them two seeds only) | 45 | 85 |
| unreviewed | 7 (1 two seeds only) | 10 | 17 |
| not measured | 35 | 12 | 47 |
| not measured (exposure only) | 7 | 0 | 7 |
| not measured (pending: today's readings, or C2P-R for 2-A and 2-B) | 9 | 0 | 9 |
| n/a | 2 | 13 | 15 |

Empty cells in total: 63 (47 + 7 + 9). For our arms, 51 of 100 cells are empty: Sp and SbM3 in every row they apply
to (39 cells); A, B and Sb in rows 3 (JPEG, exposure only), 13 (diffusion render path), 14 (GAN one-person render) and
16 (smiling half, exposure only); A and B in row 2 (storage evasion, C2P-R pending). Of the 47 filled cells for our
arms, 13 rest on seeds 401/402 only.

## What the filled cells support today (reviewers' wording)

1. **Storage history, our arms (development data, five fresh seeds, post hoc).** "The protocol cuts the storage
   reaction at the networks' own decision rule by about an order of magnitude. It does not remove it."
   (rev/REVIEW_PN1_FS1_20261113.md:20). "The plain recipe's storage reaction is present on every fresh seed but sits
   in the upper tail (own-rule flags rise from 6–11% to 21–31%). Protocol negatives reduce the rise to +2.5 to +5.5
   points (B) and +0.5 to +2.7 points (Sb), and reverse the bulk shift. The reaction is reduced, not removed."
   (PN1/result.md:296). The registered contrast for this read was uninformative (its positive control failed), so
   this is a descriptive statement. The registered replacement (contrast 2-prime) is "uninformative": the platform
   gate removed every plain network. For Sb the review allows (REVIEW_PN1_C2P Q4): "On 300 FFHQ persons no network was
   trained on, the four protocol-plus-splice networks that passed the platform gate (seeds 403, 405, 406, 407) raised
   their own-rule flag rate on stored genuine photos by +1.0 to +3.8 points at the trained size (61.2 px) and by −0.3
   to +3.4 points at an untrained size (112.7 px). Their mean genuine logit moved toward genuine (−0.02 to −0.24
   genuine SD). Stored morphs did not become easier to miss (...; storage evasion falsified on 4 of 4 read seeds).
   Development data only. No plain network passed the gate, so these reactions are not compared with the plain
   recipe, and the registered storage contrast is uninformative." A registered re-scoring on the training platform
   (C2P-R) awaits the author.
6. **One-person images, five fresh seeds (PR1 Z4, test ladder).** Warp-only images are not flagged by A, B or Sb;
   same-person morphs and mirror self-morphs are "flagged like a morph" by all three (83.2–99.5%); seam-only images
   are not flagged by Sb (a trained negative). Engine and softness reads are at the ceiling and decide nothing
   (REVIEW_PR1_PART1 findings 1 and 4).
2. **Storage history, unseen source (seeds 401/402).** "On 2,000 FFHQ persons (unseen source), shrinking to the
   morphs' 65 px eye distance and enlarging back raises the plain network's logit for 72–78% of persons (AUC
   0.67–0.68). It raises B, Bn and C for 30–44% (AUC 0.48–0.51). ... A small upper tail remains: own-rule flags rise by 5 to 8 points." (REVIEW_PN1_BATCH2 F2). The share statistic was later judged the wrong instrument for the plain arm's tail reaction (REVIEW_PN1_FS1:18). The volume control Bn
   behaves like B, so this is not data volume.
3. **Unseen genuine sources (false alarms only).** "On about 21,000 genuine photos from eight development sources
   unseen in training (small faces enlarged 1.7–3.5x, with a black border), the protocol-trained network kept its
   fixed decision rule: at most 4.9% of any family flagged, on two seeds, against up to 23.5% for the plain network.
   These photos are still clearly displaced from the training camera photos in score, so a threshold calibrated on
   camera photos does not transfer (99–100% flagged)." (REVIEW_TT1, Q6).
4. **Face splice, Sb.** "Sb's face-splice gain is real across seeds, but it is level with simple statistics, not
   beyond them." (REVIEW_PN1_FS1:21). "Spliced positives repair what protocol negatives cost, and add a margin on
   face-splice morphs." "Against the plain arm the gain is small: Sb − A = +0.019 on the test ladder, −0.010 on the development ladder." (REVIEW_PN1_FS1 F5, :79-82). The development set (FFHQ landmark_combined) carries a processing cue in the surround (noise_std_border 0.786, PN1/result.md:227).
5. **Released detectors.** Storage history moves MADation ViT-B/16, MixFaceNet-MAD and SelfMAD strongly (rows 1-ViTB,
   1-MFN, 1-SelfMAD, reviewed); ViT-L/14 changes by −1.0 to +2.0 points with saturated genuine scores ("small effects
   cannot be excluded"). On landmark morphs built without benchmark cues, "released detectors separate a two-person
   morph from a warp-only photo with the same geometry (0.89 to 0.99) ... This shows they detect blending traces, not
   that the cues play no role on the benchmark." (REVIEW_AR1). "Neither a second identity nor face-only blending is shown to be what they read" (REVIEW_AR1:103). Three adapted
   releases do not rank diffusion morphs above one-photo reconstructions (0.40–0.49, REVIEW_AD1_AG5_C; post hoc, one
   genuine pool, released weights scored once).

## What cannot be claimed today

- That the training protocol is "shortcut-free", or that it "removes" any named shortcut. Reviewed wording for the
  best-measured row is "reduced, not removed" (rev/REVIEW_PN1_FS1_20261113.md:22: no sentence may say "removes the
  storage reaction", "reads the face splice" or "beyond simple statistics").
- Anything about JPEG history for our arms: every such cell is "not measured (exposure only)".
- That the border is not used: TT-H3 is "inconclusive"; the effect is small on camera photos but mixed in sign on
  FFHQ, and only two seeds exist.
- That the protocol stops same-person morphs or same-person splices from being flagged: on five fresh seeds A, B and Sb
  place 83.2–99.5% of R3 above the rule, and Sb flags 37.2–48.2% of test S3 ("inconclusive"), a type it was trained to
  reject. The claim must be "detects in-face blending", never identity (REVIEW_PR1_PART1, risks). Whether flagging R3 is an error waits for
  the author's class ruling.
- That Sb is better than B on unseen genuine sources (Sb flags more: +0.021 / +0.031), or that any threshold transfers
  in general, to sharp sources or with calibration.
- Any benchmark or generalisation statement for A, B, Sb, Sp or SbM3 (sealed until the freeze; FRLL, MAD22 and H1
  reads of PN1 networks are compromised by the 12 Nov exposure).
- That the arms read a second identity: R4 vs R3 is 0.72–0.85 for every arm on five fresh seeds, and AD4's morph-free networks reach R4
  vs R2w 0.84–0.86 ("mostly softness").
- Storage evasion for A or B: not read (C2P gate); it is falsified only for Sb on 4 of 4 read seeds.
- From contrast 2-prime (REVIEW_PN1_C2P Q4): "reduced relative to the plain recipe" or "at most one third of it";
  "removed", "absent" or "shortcut-free"; anything about B (one seed) or A; anything about H-new-2; any generalisation
  beyond development data. "Small absolute reactions are not evidence of reduction, because the plain networks may not
  react at 112.7 px either."
- That our training engine transfers to other morph tools: the engine read is at the ceiling (REVIEW_PR1_PART1 F1).
- That Sb's τ5 operating point holds beyond its calibration sources (Z2b-τ5 waits for TT1-FS), or that it is usable
  for one-person images (32–43% of development S3 flagged at τ5).
- Any BPCER at τ_dev: the decision pool is degenerate (96–98% of FFHQ genuine flagged; REVIEW_PN1_FS1 F10).
- That A or B detect face-spliced morphs: development S4 miss 93–97% (TT1/result.md:183).
- For the unseen sources (REVIEW_TT1 Q6): anything about detection or misses on these sources; the cause of the source
  shift; that B is the better arm overall.
- Any arm sentence on seeds 401/402 beyond a lead: seed = machine; "every arm sentence is a two-seed lead" (REVIEW_TT1 F6).
- That Sb exceeds simple statistics, or that its development gain is free of processing cues (row 18).
- That the threshold is meaningful for our networks: logits are bounded near ±3.87 and camera photos sit on the floor
  (row 19).
- That the Sb recipe was chosen blind: it was selected after H1 and MAD22 had been read on seeds 401/402; the fresh
  seeds remove seed picking, not recipe selection (REVIEW_PN1_FS1 F7).

## Empty cells and the cheapest experiment to fill each (ranked by how much they matter for "the protocol removes these named shortcuts")

All on development data. Scoring on an A100 (the DGX GB10 is not a valid scoring platform for comparison with the
A100 scores, TT1 H-new-5), except C2P, which is registered on an L40S (PN1/prereg.md:817): compare only within C2P. Checkpoints: seeds 401/402 of A, B, Bn, C, Sb, Bv in
`/mnt/t7/smad_next/PN1/results_rented/PN1_*_s40[12].tar`; fresh seeds 403–407 of A, B, Sb in
`/mnt/t7/smad_next/PN1/results_fs/` (also uploaded to the MS1 lease ms1m1b for C2P); Sp in `results_fs/` as it lands;
SbM3 and SbV tars on the MS1 leases and their local copies. Each tar carries `last_trainable.pt` (LoRA and head) and
the per-image scores of the registered evaluation list. Nothing below was run.

| Rank | Empty cells | Experiment (registered style) | Pack and checkpoints | Cost | Why it matters |
|---|---|---|---|---|---|
| 1 | 1-Sp, 1-SbM3, 2-Sb, 4-SbM3, 8-Sp, 9-Sp, 11-SbM3, 18-Sp; fresh-seed parts of 4, 5, 10 (TT1-FS) | Today's registered reads: TT1-FS (registered a2fef5c, ab81b35; queued on pn1fs, end about 13:30); Sp reader `src/PN1/sp_read.py` (registered); MS1 reader `ms1_read.py`; contrast 2-prime (C2P) storage test and H-new-1 storage evasion on the MS1 FFHQ hold-out | already scored or scoring | 0 new GPU (C2P under 1 GPU-hour, already registered) | The registered storage test and the seam ablation are the central cells of the claim |
| 2 | 7-Sb, 7-Sp, 9-A, 6-Sb full R2w placement, and fresh-seed versions of 6-A, 7-A, 7-B | Zero-GPU read of R3, R3m, R2w, S0 and S4 rows already in the FS1, Sp and MS1 score files (development ladder and test ladder rows of the FS1 evaluation list). Must be registered before reading, since these rows have not been printed | existing tars | 0 GPU, about 1 CPU-hour | Gives five seeds instead of two for warp-only and same-person rows, and the missing Sb same-person row |
| 3 | 3-A, 3-B, 3-Sb, 3-Sp, 3-SbM3 | JPEG history on development genuine photos: the registered JPEG branch (`degrade(img, "jpeg90/70/50")`, imported unchanged, as in PN1 amendment 1) applied to the 191 test-ladder R0 photos and the 300 MS1 FFHQ hold-out photos, paired native against JPEG, own-rule flag change and paired shift; scored by the 15 fresh-seed checkpoints plus Sp and SbM3 | new pack of about 1,500 PNG files; checkpoints above | about 0.5 A100-hour (about 0.5 USD rented) once the pack exists | The whole JPEG row is empty for our arms; it is a named benchmark cue (cue matrix rows 4a, 4b). Re-encoding evaluation images as JPEG is an author item: the author builds the JPEG pack; agents only score it |
| 4 | 4-Sp, 5-Sp, 5-SbM3, 10-Sp, 10-SbM3 | TT1-FS (`TT1/prereg_fs1_block.md`) is registered and queued for the 15 fresh networks, 0 new GPU; extending it to Sp and SbM3 needs a new registration | existing TT1 pack and border references | about 0.3 A100-hour for the extension | Moves rows 4 and 5 from two seeds to five; border is a named cue of our own aligner |
| 5 | 2-A, 2-B fresh seeds; 2-SbM3 | Storage evasion of morphs on the MS1 hold-out stored u50 morphs (as C2P H-new-1) for A, B and SbM3 | in C2P and MS1 score files | 0 GPU once C2P and MS1 are read | Completes the "evasion" row, which the FS1 review calls "the key threat to any shortcut-free claim" |
| 6 | 13-A, 13-B, 13-Sb, 13-Sp, 13-SbM3 | Diffusion render path: score the DG1 diffusion ladder (reconstruction, same-person mix, two-person mix; FRGC/colorFERET hosts, restricted to PN1 test hosts so that no training host enters) with the 15 fresh-seed checkpoints; read morph vs reconstruction AUC and reconstruction flags | DG1 sets on the DGX (`experiments/DG1_diffusion-generation-athena/`), host filter by `PN1/split/ladder_split.csv` | about 0.3 A100-hour | The released detectors fail this row; showing our arms on it is needed before any diffusion claim |
| 7 | 14-A, 14-B, 14-Sb | GAN one-person render: score the AG1 MIPGAN controls (one photo, same-person, two-person) on hosts outside PN1 training | AG1 images on Athena (11 rented originals lost; Athena copies verified per `experiments/AG1/athena_backup_verify.txt`) | about 0.3 A100-hour plus transfer | Same reason for the GAN family |
| 8 | 17-Sb, 17-Sp, 17-SbM3 | Softness: the TT1 H-new-1 Laplacian-variance read for Sb and for the fresh seeds, from existing scores (registered first) | existing scores | 0 GPU | Separates softness from blend reading for our arms |
| 9 (done, G9) | 15-A, 15-B, 15-Sb | Partner audit of our own training manifests (how many morphs share a second contributor), then the SM1 trained-against-unused partner contrast if any partner repeats | manifests only | 0 GPU (CPU minutes) | Probably empty by construction (one partner per host); cheap to confirm |
| 10 | 5-ViTL, 5-MFN, 13-MFN, 14-MFN, 16-MFN, 4-ViTL, 10-SelfMAD, 19-MFN | Released-detector audits with the RS1 machinery: border-matched pairing (EV1 amendment 2 style) for ViT-L/14 and MixFaceNet; MixFaceNet on the AD1 and AG1 ladders; MixFaceNet neutral-only column | RS1 crops and scorer on an A100 | about 0.5–1 A100-hour | Completes the comparison columns; does not bear on the protocol claim |
| 11 (pool check done, G11: CFD 158 + KDEF 70 persons) | 16-A, 16-B, 16-Sb | Expression on development data, paired neutral against happy on CFD and KDEF (held-out MS1 sources; needs alignment of the happy images with the unchanged aligner, a registration and the lead's approval): neutral against smiling genuine photos of the same persons where a development pool has both (to be checked; FRGC sessions), paired by person | to be built | unknown; first a zero-GPU check that such a pool exists | Expression is a benchmark cue only for FRLL; low priority for the protocol claim |
</content>
</invoke>
