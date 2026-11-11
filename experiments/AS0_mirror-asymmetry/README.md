# Mirror-asymmetry test (AS0): full record

Owner: hypothesis-owner agent for the mirror-asymmetry test (AS0), phase 1 (CPU only, existing images only).
Machine: DGX (GB10, ARM), CPU only, at most 2 processes at nice 10. Registration: `prereg.md` (this folder, written
before any statistic). Short verdict: `result.md` (when phase 1 numbers exist). This README follows
`/home/narolski/smad-next/DOCUMENTATION.md`; dated lines are added, history is not rewritten.

Terms. AUC = area under the ROC curve (0.5 = chance). IOD = inter-ocular distance (pupil landmarks 38 and 92 of the
106-point insightface layout). E_A, E_S = energy of the mirror-asymmetric part A = (x - mirror x)/2 and of the
mirror-symmetric part S = (x + mirror x)/2 inside a symmetric face mask, per octave band. L = ln(E_A / E_S).
Rungs of the landmark ladder (AR1): camera photo (R0), the person's other-session photo (S0), tool run on one photo
(R2), warp-only image toward the mean shape of the two photos (R2w), warp-only toward the own mirrored shape (R2wm),
mirror self-morph (R3m), same-person morph (R3), two-person morph (R4). E7 = the existing shrink-and-enlarge
storage-history copy. FR = face recognition.

## 1. Question and current answer

Question (lead, 11 Nov): averaging two different persons averages two independent asymmetry patterns, so a
two-person morph should have a lower ratio of asymmetric to symmetric energy than a same-person morph, and the ratio
should not move with softness or storage history. Is this a single-image signal for a second identity?

Status 11 Nov 2026, 21:00 CET: **closed** (after the independent review and amendment A14; CPU only; no detector
score opened; no image built). Short verdict in `result.md` (version 2). Registered verdict: **weak**. On the
landmark ladder (536 hosts, both engines) the two-person morph (R4) has a lower asymmetry ratio than the same-person
morph (R3): 0.611 [0.573, 0.651] over all bands B1-B5 (selection-free), 0.618 [0.580, 0.659] in the best of five
bands (B3); only B3 clears the kill mark of 0.60. The mirror self-blend control is algebra; the dose curve, the
informative control, shrinks at about 0.54-0.63 of the square-root-law rate. The ratio is history-stable, not
history-free (FaceMorpher storage history up to +0.10 SD with own landmarks, +0.20 with native landmarks in B3; with
the primary flip always toward the genuine side), and its level differs between photo pools (genuine FRGC against
genuine colorFERET 0.72 in B3, post hoc; follows capture sharpness, not pose or lighting) more than between morph
types: usable only within a pool on the same hosts. The geometry-matched warp-only reference (A14) gives geometry a
third of the key contrast (0.33 [0.23, 0.43] in B3) and a texture excess of +0.08 (two-person against R2w4 0.655
against same-person against R2w 0.576): the review's H-new-1 is falsified; detected-landmark typicality reads the
target shape (R4 against R2w4 0.528), H-new-2 not falsified. GAN latent morphs: no two-person reading (0.48-0.52);
diffusion: the 0.74 against the same-person mix is that mix being unusually asymmetric (against the reconstruction
0.60).

## 2. Timeline (11 Nov 2026, CET)

- 18:02-18:08 Read OWNER_BRIEF, DOCUMENTATION, ideas/ROUND3_BRIEF, AR1 README, PD1 GAN prereg, AD1b README and
  result, ID0 README, NOTEBOOK, EXPERIMENTS, 10_ASSET_INVENTORY. Inventory (no statistic): AR1 pool (536 hosts; every
  same-person pair R3 is cross-session by construction), AR1 rungs (536 each, graded FaceMorpher 6 x 300), the
  106-point layout (mean host shape printed; contour 0-32, brows 43-51 / 97-105, pupils 38 / 92, nose tip 86, mouth
  52-71), alignment eye coordinates of 73_delin_align and prep_eval (both (190, 210), (322, 210) in 512 frames),
  MAD22 canonical E7 records (FaceMorpher E7 scale about 0.30), AF0 softened AR1 copies (1,200), r8 same-person
  landmark morphs with session information (2,500 pairs x 2 engines), GAN32 SOURCES (capture names), A43 and AD1b
  folders (AD1b full run at x_T 32 of 80 at 17:35), expanded123 DiffAE blocks (102 complete; include non-frontal
  FERET captures).
- 18:10 `as0_lists.py` written and run: 24,624 items (graded-folder filter bug fixed: a JSON file in the folder was
  read as a level). 18:16 rerun with the second photos S0 added: 25,160 items, 0 missing paths, 4,228 need landmark
  detection. sha256 of `items.csv` in `lists_summary.json`.
- 18:11-18:13 `as0_landmarks.py`: 8-image tests per set (about 0.6 s per image on the CPU); the A43 stored crops
  gave no face in 8 of 8 (tight crops), fixed by one retry on an in-memory copy padded with black (8 of 8 found;
  detector input only). Full detection launched 18:13 (PID 2241441, log `/mnt/t7/smad_next/AS0/logs/landmarks.log`).
- 18:10-18:17 `prereg.md` written (before any statistic). 18:18 experiment-reviewer agent asked for an independent
  read of the registration.
- 18:19 `as0_measure.py` written. Nominal IOD: ar1_512 130.51 px (1,072 genuine shapes). The SMDD landmark file
  stores coordinates divided by the image size (first IOD read 0.249); fixed by scaling with 256 (IOD 63.7 px).
  8-image tests of L, Lsoft, R8, S (0.19 s per 512 image). `as0_check.py`: implementation checks (section 6).
- 18:21 measurement of L, Lsoft, R8, S launched (PID 2250330, log `/mnt/t7/smad_next/AS0/logs/measure_a.log`).
  8-image smoke outputs `meas/smoke_*` deleted unread. Prereg time stamps corrected to the file times (18:21:55 save;
  only three time strings changed).
- 18:22-18:30 `as0_analyse.py` (contrasts, bootstrap, verdict) and `as0_tables.py` written; README first version;
  volatile inputs byte-copied to `/mnt/t7/smad_next/AS0/inputs/` (r8_pairs.csv sha256 e7bca16c...,
  smdd_bona_landmarks_if106.npz f167eaf8...; `COPY_SHA256.txt`).
- about 18:35 reviewer: GO WITH FIXES (no rule violation); 8 findings (geometry can produce the contrast; timeline;
  history cut-off scale and re-aligned copies; low-band leakage; numerical floor; dose/share bias; database mix in the
  strata; canon512 IOD). 18:38-18:45 registered as amendments A1-A8 (prereg section "Review result and amendments").
- 18:40 base landmark detection stopped by me before the secondary X set (PID 2241441; parts for G, Fm, D, M, Ds,
  Fe complete) to give the primary history control priority.
- about 18:40 lead message (review of the identity-shrinkage triage (ID0)): five additions, registered 18:45 as A9-A13
  (calculated shapes are arithmetic; detected landmarks on the built ladder images with ID0's typicality score and
  the shape asymmetry; external prediction 0.58-0.70 with dose slope < 0.7; drop the 8 validation-reserved persons from
  fits and report with and without; all R3 cross-session). prereg sha256 after A13: ee1ae0de...
- 18:41 `as0_lists.py` extended (appended rows only; existing ids unchanged): copies with own detected landmarks
  (FmO, FeO, LsoftO, 2,628) and Lsoft natives detected (LsoftN, 600); 18:40 detected-landmark ladder sets LD1 (R0,
  S0, R3, R4; 3,216), LD2 (R2w, R3m, R2wm; 3,216), LD3 (graded; 1,800). items.csv now 36,620 rows, 15,688 to detect.
- 18:41 compute chains started (one process each, nice 10): `src/AS0/chain_b.sh` (PID 2272290: detect FmO and X,
  merge, nominal IOD, measure Fm, FmO, G, D, M, Ds, Fe, X, detect LsoftN, LsoftO, FeO, measure them, blank run) and
  `src/AS0/chain_a.sh` (PID 2272291: waits for PID 2250330, then detects LD1, LD2, LD3). `as0_geom.py` (midline
  geometry, A1) and `as0_typ.py` (A10) written; `as0_analyse.py` patched for A1-A8 and A12 (pre-amendment copy
  `/mnt/t7/smad_next/AS0/logs/as0_analyse_pre_amend.py.txt`).

- 18:50-19:04 machine load rose to about 140 (20 cores); my processes at nice 10 slowed from 0.19 to about 1.4 s per
  512 image and detection to about 0.9-1.5 s per image. Plans re-ordered three times (chain_b2/a2, chain_b3/a3,
  chain_b4) so that the registered primary cell comes first; each superseded chain was stopped by PID while waiting
  or between steps (the running measurement of Fm was stopped once at 19:03 after one 256-item chunk; that chunk is
  kept, duplicate ids are dropped at merge, keeping the first). Phase-1 cuts because of the load (no result was
  looked at): the expanded123 DiffAE blocks (X) are not measured (128 of 1,224 landmark detections done); diffae256
  nominal IOD therefore from the A43 photos only (63.91 px, 204); R8 is measured on the colorFERET pairs only
  (1,792 images; the A7 reading is within colorFERET); the blank sensitivity run uses a host subsample
  (sha1(host) mod 3 = 0) for R3 / R4; Fe uses the facemorpher and amsl copies; S0 moved from LD1 to LD2.
- 19:11 L measured (9,304 images). 19:12-19:18 permuted-label test run of `as0_analyse.py` (`--test-permute`, B = 50,
  outputs `/mnt/t7/smad_next/AS0/test_analysis/`; AUCs 0.47-0.52 as expected; code path checked). 19:22-19:29 first
  real analysis (L, Fm, FmO; log `analyse_1.log`): the first time any contrast was computed or opened.
- 19:35 slot-B plan five (`chain_b5.sh`): G, a second detection worker on LD1 from the end (`--reverse`), blank run,
  Ds, Lsoft own landmarks, Fe, secondary Fm copies; finished 20:14. Slot A (`chain_a3.sh`): LD1 19:52, Lsoft and S
  19:56, LD2 20:20. The detection and analysis processes were paused with SIGSTOP while an extra short process ran
  (19:12-19:18, 19:22-19:29, 19:53), so that at most two of my processes used CPU at a time.
- 19:35 geometry share: the registered log version (L_R2wm - L_R0) / (L_R3m - L_R0) is dominated by the near-zero
  mirror self-morph (0.01-0.05); an energy version (1 - r_R2wm/r_R0) / (1 - r_R3m/r_R0) was added as descriptive
  (after seeing the log version).
- 19:53 `as0_typ.py` on LD1 (A10): typicality R4 against R3 on detected shapes 0.653; 20:21 rerun with LD2.
- 20:28-20:31 the AD1b generator ended ("attempt 1 ok"); its 32 mirror mixes and reconstructions added as set Mf
  (64 detections, measurement, `analyse_3.log`, tables); no other number changed.
- 20:14-20:17 final analysis (`analyse_2.log`; first attempt crashed on the 80 px SMDD copies in bands beyond their
  Nyquist, an empty array in the bootstrap; fixed by returning "not measurable" below 10 pairs) and tables; 20:18
  blank run compared with the primary statistic on the same 187 hosts (`blank_vs_primary_same_hosts.json`).
- 18:52 nominal IOD (`iod_nominal.json`): ar1_512 130.51, canon512 131.25, shared512_photo 130.49, diffae256 63.91,
  a43_stored 63.68, smdd256 63.73 (smdd80 19.92), stylegan_raw1024 256.09 (all renders). (The "note" on ar1_512 in
  that file, "also used for canon512", is stale: since A8 canon512 uses its own value.)

- 20:33 report to the lead. About 20:50 the independent review (`experiments/reviews/REVIEW_AS0_20261111.md`, verdict
  "needs qualification") and the lead's five instructions arrived. 20:45 amendment A14 registered in prereg.md (sha256
  1a75d8bf...) before any R2w4 statistic; seen beforehand: one AR1 README line on R2w4 in other statistics (recorded
  in A14).
- 20:46 post hoc addendum (`as0_posthoc.py`, seconds, `posthoc_addendum.json`), labelled post hoc.
- 20:46-20:49 `chain_a14.sh` (one process, OMP 2, nice 10; machine load had fallen to about 9): R2w4 measured (set
  L4, 1,072) and its landmarks detected (set LD4, 1,072, no image without a face). 20:49 `as0_a14.py` -> `a14.csv`,
  `a14.json`.
- 20:50-21:00 `result.md` version 2 and this README corrected as the review and the lead asked; one statement of the
  review checked and qualified (the "always toward the genuine side" holds for the primary flip F0; with the
  landmark-midline flip and own landmarks the FaceMorpher shift is -0.08 in B3 and -0.14 in B4). Closed.

Amendments to the registration: A1-A14 (prereg.md), each registered before the numbers it governs.

## 3. Data

Item list `/mnt/t7/smad_next/AS0/items.csv` (25,160 rows; columns described in `src/AS0/as0_lists.py`), counts per
set and rung in `lists_summary.json` (this folder). Inputs are read in place, nothing is copied or written:

| Set | What | Path | n |
|---|---|---|---|
| L | landmark ladder (AR1) primary pool, FRGC + colorFERET | `/mnt/t7/smad_next/AR1/{src,img/frgcferet/{opencv,facemorpher}/{R2,R2w,R2wm,R3,R3m,R4},img/frgcferet/fm_graded/m000..m050,mirror/frgcferet}`, pool `/mnt/t7/smad_next/AR1/pool.csv` | 536 R0 + 536 S0 + 6 x 2 x 536 + 1,800 graded |
| Lsoft | AR1 R0 and R2w (200 hosts) through the existing shrink-and-enlarge path, strengths amsl112 / fm61 | `/mnt/t7/smad_next/AF0/img/soft/`, lists `/mnt/t7/smad_next/AF0/{lists/ar1soft_src.csv,soft_ar1soft_src.csv}` | 1,200 |
| R8 | record's landmark same-person morphs of two captures | images `/mnt/t7/smad_next/volatile_backup_20261111/r8_{cv,fm}/m*.png`, pairs `/dev/shm/smad_arms/r8_pairs.csv` (volatile; to be copied) | 2 x 2,500 |
| G | GAN latent blocks (PD1 set G) | `/mnt/t7/smad_next/PD1/gan/items.csv` (paths), anchors and raw1024 renders | 768 |
| D | A43 DiffAE-native 256 frames | `/mnt/t7/smad_heldout/a41_diffae/data/a41diffae/a256/png256`, `/mnt/t7/smad_heldout/a43/gen/{D20,C20,B20,B}/png256` | 910 |
| M | AD1b mirror mix and re-run reconstruction (smoke, 4 persons) | `/mnt/t7/smad_next/AD1b/smoke_gen/{PAF,D20r}/png256` | 8 |
| Ds | A43 stored crops and published MorDIFF | `/mnt/t7/smad_heldout/a43/data/a43/stored/{E,D20,C20,B20,A}` | 910 |
| Fm | corrected MAD22 canonical native genuine and E7 copies | `/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/{native/BonaFide,e7/{FaceMorpher,OpenCV,Webmorph}}` | 204 + 3 x 204 |
| Fe | FRLL-Morphs evaluation frames native and resmatch | `/home/narolski/mambamorph-code/smadcvpr_data/eval/frllm/frll_bona/*_{orig,resmatch_*}.png` | 204 + 4 x 204 |
| S | SMDD genuine renders and E7 (80 px) | PD1 items set S; landmarks `/dev/shm/smad_arms/smdd_bona_landmarks_if106.npz` (volatile) | 2,000 + 2,000 |
| X | expanded123 DiffAE blocks (secondary) | `/mnt/t7/smad_research/diffae-expanded123-v1/run/<block>/` | 1,224 |

Produced (all under `/mnt/t7/smad_next/AS0/`): `items.csv` (36,620 rows at the end; sha256 in `lists_summary.json`),
`lm/part_*.npz` (detected landmarks; merged `lm/landmarks.npz`, 11,860 images detected, 0 without a face),
`iod_nominal.json`, `meas/<set>[_filter]_<k>.npz` (per-image energies and covariates; merged `meas_all.npz`, 22,324
images), `meas_blank/` and `meas_blank_all.npz` (1,360 images), `geom.npz` (midline geometry), `check.json`,
`test_analysis/` (permuted-label code test), `inputs/` (byte copies of volatile inputs), logs in `logs/`
(`landmarks*.log`, `measure_*.log`, `chain_*.log`, `analyse_1.log`, `analyse_2.log`, `typ.log`,
`as0_analyse_pre_amend.py.txt` = the analysis script before the amendments).

Measured in phase 1: L 9,304 (+ L4 = R2w4 1,072 and its detected landmarks LD4 1,072, amendment A14); Lsoft 1,200 (+ LsoftN 600, LsoftO 1,200 with own landmarks); R8 colorFERET 1,792;
G 768; D 910; M 8; Ds 910; Fm 816 and FmO (FaceMorpher) 204; Fe native, amsl, facemorpher (612); S 4,000. Detected
landmarks on the built ladder images LD1 2,680 and LD2 3,752 (A10). Not measured: X (expanded123), R8 FRGC pairs, LD3
(graded), FeO, FmO OpenCV / Webmorph. Items without a face or with a mask under 1,000 pixels: none in the analysed
sets (`analysis.json`); 42 items had E_A floored (A5; mirror self-morphs).

## 4. Code (`/home/narolski/smad-next/src/AS0/`)

| Script | Job |
|---|---|
| `as0_common.py` | paths, sealed-name guard, `.tem` reader, mirrored shape, 106-point indices, face polygon |
| `as0_lists.py` | item list from existing files and metadata; FRGC session dates through AR1 `pool.frgc_meta` (imported unchanged) |
| `as0_landmarks.py` | insightface buffalo_l landmarks on the CPU (2 intra-op threads), padded retry, parts, `--merge` |
| `as0_measure.py` | `--iod` nominal IOD per frame; per-image band energies (7 bands, 4 channels, 2 flips), shape asymmetry, covariates; `--merge` |
| `as0_check.py` | implementation checks on synthetic arrays and mirror equivariance |
| `as0_geom.py` | midline offsets at eye, nose and mouth level per item (A1) |
| `as0_analyse.py` | contrasts, bootstrap, history shifts, dose curve, shares, confound reads, blank run, verdict; `--test-permute` |
| `as0_typ.py` | shape statistics on detected landmarks of the built ladder images: ID0 typicality (imported unchanged) and shape asymmetry (A10) |
| `as0_tables.py` | `tables.md` from the CSV / JSON outputs |
| `as0_lmcheck.py` | landmark-source check (written, not run; the detected-versus-calculated error is reported by `as0_typ.py`) |
| `as0_posthoc.py` | post hoc addendum after the review: pool offset with pose / lighting / softness partialled out, person-disjoint logistic ceiling, partner-similarity Spearman (F9), neutral against smiling (F8) |
| `as0_a14.py` | amendment A14: geometry-matched warp-only reference R2w4 (H-new-1) and detected typicality (H-new-2) |
| `chain_*.sh` | the compute chains (one process each, nice 10); `chain_a3.sh` and `chain_b5.sh` are the ones that finished the work |

Run order: `as0_lists.py` -> `as0_landmarks.py` (+ `--merge`) -> `as0_measure.py --iod` -> `as0_measure.py --sets ...`
-> `as0_measure.py --merge` -> `as0_analyse.py`. Environment: `/home/narolski/mambamorph-code/.venv-spark/bin/python`
(Python 3.12, numpy 1.26.4, scipy 1.17.1, OpenCV 4.11.0, insightface 1.0.1, onnxruntime 1.27.0 CPU only). Weights:
`~/.insightface/models/buffalo_l/{det_10g,2d106det}.onnx` (the pack of 73_delin_align / prep_eval). Seeds: bootstrap
[20261111, 61]; no other randomness (check script noise seed 1).

## 5. Results

Source files (this folder): `contrasts.csv` (every AUC), `history.csv`, `dose.csv`, `shares.csv`, `verdict.json`,
`analysis.json`, `tables.md` (rendered by `src/AS0/as0_tables.py`). First analysis run 19:22-19:29 (`as0_analyse.py
--B 2000`, log `/mnt/t7/smad_next/AS0/logs/analyse_1.log`) on L, Fm (natives and FaceMorpher copies), FmO
(FaceMorpher copies with own landmarks), D, M (sets measured at that time). The final run on all measured sets
overwrites these files; numbers of L below do not change (L is complete).

Primary cell, landmark ladder, both engines pooled, Y, flip F0 (AUC = P(L(R4) < L(R3)), 1,072 / 1,072 images, 536
persons, two-way person bootstrap B = 2,000):

| band | K1 R4 vs R3 | K1 without the 8 reserved persons | OpenCV / FaceMorpher | halves (person-disjoint) | history d, FaceMorpher E7, own landmarks (below cut-off) | d, native landmarks | R3m collapse |
|---|---|---|---|---|---|---|---|
| B1 | 0.563 [0.526, 0.603] | 0.567 | 0.573 / 0.553 | 0.582 / 0.592 | -0.018 [-0.052, +0.012] (yes) | -0.013 | yes (AUC 1.000) |
| B2 | 0.599 [0.561, 0.640] | 0.603 | 0.608 / 0.590 | 0.620 / 0.596 | +0.048 [+0.017, +0.081] (yes) | +0.106 | yes |
| B3 | 0.618 [0.580, 0.659] | 0.622 | 0.625 / 0.611 | 0.635 / 0.624 | +0.102 [+0.062, +0.151] (yes) | +0.204 | yes |
| B4 | 0.562 [0.522, 0.605] | 0.567 | 0.567 / 0.557 | 0.584 / 0.559 | +0.095 [+0.041, +0.154] (yes) | +0.124 | yes |
| B5 | 0.524 [0.483, 0.565] | 0.526 | 0.529 / 0.519 | 0.523 / 0.492 | +0.016 [-0.102, +0.135] (no) | +0.014 | yes |
| B1-B5 | 0.611 [0.573, 0.651] | 0.615 | 0.621 / 0.601 | 0.627 / 0.627 | -0.175 | -0.142 | - |

(Intervals corrected 21:00 to the final run, `analyse_3.log`; the first version of this table had the 19:22 run's
intervals, whose person draw did not include the R8 persons.) Only B3 is at or above 0.60 (B2 0.5991).

Verdict (registered rule): **weak**. External prediction of the ID0 review (A11): best band 0.618 with dose slope
0.535 in that band, inside the predicted zone (0.58-0.70, slope < 0.7); not falsified.

Other landmark-ladder contrasts (pooled, Y, F0; full table in `tables.md`): R4 against R2w 0.64 / 0.67 / 0.69 /
0.62 / 0.56 (B1..B5), broadband 0.719; R3 against R2w 0.58 / 0.58 / 0.58 / 0.56 / 0.53, broadband 0.619; R2w against
R0 0.51-0.53; R4 against R0 broadband 0.747; S0 against R0 0.47-0.51; R2 against R0 0.500; R2wm (shape symmetrised
only) against R0 0.56 / 0.66 / 0.71 / 0.73 / 0.74; R3m against R2w 1.000. Shape asymmetry calculated from source
landmark files (arithmetic, A9): R4 against R3 0.595 [0.553, 0.639], R4 against R0 0.633. Channels R, G, B and the
channel sum give the same K1 within 0.01; the landmark-midline flip F1 also (B3 0.611).

Confounds on K1 (B3 unless stated): residual after Laplacian variance 0.627, after pose and lighting 0.604, after
geometry ("beyond geometry": shape asymmetry, three midline offsets, mask size) 0.596, after all 0.608 (fits without
the reserved persons); covariates alone: |yaw| 0.571, calculated shape asymmetry 0.595, Laplacian variance 0.530,
lighting 0.502, midline offsets 0.53-0.55. Session-gap strata (all R3 cross-session by construction): <= 60 days
0.642, 61-365 days 0.621, > 365 days 0.563 (wide intervals); FRGC 0.634, colorFERET 0.581. |yaw| tertiles 0.590 /
0.635 / 0.588; pose-gap tertiles 0.622 / 0.639 / 0.619; lighting-gap tertiles 0.617 / 0.626 / 0.617.

Paired per-host ratios (pooled, median exp(L_rung - L_R2w)): R3 0.78 / 0.85 / 0.88 / 0.92 / 0.97 (B1..B5); R4 0.61 /
0.65 / 0.68 / 0.81 / 0.95 (predicted 0.5); person-specific share pi_L 0.55 / 0.70 / 0.75 / 0.84 / 0.95 and, from the
asymmetric energy alone, pi_A 0.49 / 0.58 / 0.60 / 0.51 / 0.28 (the symmetric energy of R3 also falls in B4-B5: E_S
ratio 0.82, 0.66, i.e. softening). Dose curve (300 hosts, graded FaceMorpher): slope 0.63 [0.54, 0.72] (B1), 0.60
[0.53, 0.68] (B2), 0.54 [0.47, 0.60] (B3), 0.27 (B4), 0.08 (B5), broadband 0.63; calculated shape asymmetry 0.84
(arithmetic). AUC of m = 0.5 against m = 0: 0.64 / 0.67 / 0.71 / 0.64 / 0.57.

Storage history (Y, F0; d in native-SD units, [shift / (mean L_R3 - mean L_R4)]): FaceMorpher E7 (204, scale 0.47,
B1-B4 below the cut-off), own landmarks: B1 -0.018 [-0.08], B2 +0.048 [+0.15], B3 +0.102 [+0.21], B4 +0.095 [+0.42],
B5 +0.016, broadband -0.175; with the native landmarks the shifts are larger in B2-B3 (+0.106, +0.204). OpenCV and
Webmorph E7 copies that differ from the native frame: 28 each, |d| <= 0.04.

Geometry-matched reference R2w4 (A14; `a14.csv`, `a14.json`; Y, F0, both engines pooled, 1,072 / 1,072; B1 / B2 / B3 /
B4 / B5 / B1-B5):
- R2w4 against R2w (shape change only): 0.513 / 0.526 / 0.540 [0.503, 0.576] / 0.534 / 0.521 / 0.526.
- R4 against R2w4 (second texture only): 0.629 / 0.649 / 0.655 [0.628, 0.685] / 0.587 / 0.534 / 0.701 [0.669, 0.736]
  (OpenCV 0.648, FaceMorpher 0.661 in B3); R3 against R2w (same-person analogue) 0.583 / 0.579 / 0.576 / 0.555 / 0.528
  / 0.619; texture excess in B3 +0.079.
- R2w4 against R3: 0.430 / 0.446 / 0.462 / 0.477 / 0.491 (the warp-only image toward the two-person shape keeps more
  asymmetry than the same-person morph).
- Paired median exp(L_R2w4 - L_R2w): 0.972 / 0.939 / 0.903 [0.878, 0.938] / 0.934 / 0.972; geometry share of the
  R3-to-R4 gap 0.17 [0.06, 0.30] / 0.30 [0.20, 0.40] / 0.33 [0.23, 0.43] / 0.51 [0.24, 0.74] / undefined (B5 gap near
  zero) / 0.24 [0.15, 0.32]; without the reserved persons B3 0.33 [0.22, 0.43].
- Readings: H-new-1 falsified (R4 against R2w4 0.655 >= 0.65; median ratio 0.903 < 0.95); H-new-2 not falsified
  (detected typicality R4 against R2w4 0.528 [0.505, 0.552], R2w4 against R3 0.626 [0.590, 0.662]; total typicality
  0.530 and 0.632; detected shape asymmetry 0.537 and 0.554).

Post hoc addendum (lead's request after the review, `posthoc_addendum.json`; not registered): genuine FRGC against
colorFERET photos (427 / 109), AUC = P(L_FRGC < L_FERET): raw 0.743 / 0.761 / 0.720 / 0.667 / 0.567, after |yaw|, yaw,
nose offset and lighting 0.780 / 0.790 / 0.739 / 0.682 / 0.569, after adding log Laplacian variance 0.539 / 0.532 /
0.520 / 0.537 / 0.506; mean L gap FRGC - colorFERET -0.79 / -0.68 / -0.42 / -0.26 / -0.09 nats. Person-disjoint
logistic ceiling (5 folds, out of fold): same-person against two-person: bands 0.632 [0.588, 0.674], + calculated
shape 0.635, + detected shape 0.634, detected shape alone 0.589; warp-only against two-person: bands 0.701 [0.660,
0.741], + shape 0.700. Partner similarity (F9): Spearman(cos_HB, L_R4 - L_R2w) -0.06 to -0.15 (B2-B3 -0.10 [-0.18,
-0.01] both engines). Neutral against smiling FRLL photos (F8): 0.505 / 0.507 / 0.488 / 0.543 / 0.464. Review F8's
released-detector values (0.60-0.75 on R4 against R3) are quoted from the review, not re-read.

Shape statistics on landmarks DETECTED on the built ladder images (A10, review hypothesis H-new-2; `as0_typ.py`,
19:53; `typ_detected.csv`, `typ_detected.json`; LD1 = R0, R3, R4, both engines; 2,680 detections, no image without a
face). Identity-shrinkage typicality score (ID0 `iss.py`, its landmark fit: 776 persons, k = 11, d = 10), AUC = P(score
R4 > score R3), the 8 reserved persons dropped: **detected 0.653 [0.616, 0.692]** (OpenCV 0.655, FaceMorpher 0.651;
with them 0.653) against **calculated from source landmark files 0.687 [0.651, 0.726]** (reproduces the ID0 number);
registered reading: supported (>= 0.65), by a margin of 0.003. Total typicality: detected 0.661, calculated 0.697. R4
against R0: detected 0.671, calculated 0.725; R3 against R0: 0.523 / 0.548. Shape asymmetry L_shape on detected shapes,
R4 against R3: 0.590 [0.551, 0.632] (calculated 0.595); R4 against R0 0.628 (0.634); R3 against R0 0.538 (0.541).
Detection error against the calculated target shape (mean point distance / IOD, median): photos 0.0082, R3 0.0084 /
0.0094, R4 0.0097 / 0.0121 (OpenCV / FaceMorpher). With LD2 (20:21): R4 against R2w 0.650, R4 against S0 0.679, S0
against R0 0.495; detected shape asymmetry of the mirror self-morph against R2w 0.964.

Final analysis (20:14-20:17, `analyse_2.log`; L numbers unchanged):

- Same-person landmark morphs with session information (record's r8 arms, colorFERET only, both engines pooled; Y, F0;
  B1 / B2 / B3 / B4 / B5): cross-session against same-session 0.587 / 0.574 / 0.616 / 0.573 / 0.541 (620 / 1,172);
  two-person morph (L R4, colorFERET hosts) against same-session same-person 0.608 / 0.619 / 0.692 [0.613, 0.767] /
  0.628 / 0.560; against cross-session 0.517 / 0.543 / 0.575 / 0.548 / 0.518; R8 cross-session against L R3 (both
  colorFERET) 0.538 / 0.514 / 0.506 / 0.481 / 0.500 (the two sets agree). Same-session pairs with the same expression
  code (fa + fa or fb + fb, 134 images): two-person against them 0.64 / 0.66 / 0.75 / 0.76 / 0.68 (small n). The rows
  that mix databases (pooled R4 against colorFERET R8) are descriptive only.
- GAN latent blocks (64 blocks; Y; F0 / F1 within 0.04): x3 against x2 0.504 / 0.505 / 0.515 / 0.511 / 0.479; x3
  against x1 0.616 / 0.616 / 0.659 / 0.682 / 0.654; x2 against x1 0.613 / 0.611 / 0.652 / 0.668 / 0.680; x1 against x0
  0.516 / 0.552 / 0.619 / 0.622 / 0.647; x3 against same-session x2 (62) 0.52-0.56, against cross-session x2 (66)
  0.44-0.49. Shape asymmetry (detected) x3 against x2 0.515.
- Diffusion autoencoder (A43, DiffAE-native 256): B20 against C20 0.646 / 0.709 / 0.741 [0.654, 0.821] / 0.685 /
  0.607 (broadband 0.722); B20 against D20 0.607 / 0.626 / 0.598 / 0.571 / 0.503; C20 against D20 0.461 / 0.431 /
  0.365 / 0.399 / 0.413 (the same-person mix is more asymmetric than the reconstruction); D20 against photo 0.512 /
  0.537 / 0.595 / 0.632 / 0.638; B (100 steps) against D20 0.597 / 0.595 / 0.505 / 0.449 / 0.356; mirror mix P_AF
  against D20r (4 persons) 1.000. Stored crops (F1): B20 against C20 0.636 / 0.701 / 0.718 / 0.680 / 0.588; published
  MorDIFF against photo 0.62-0.70. Lead's face-box statistic (mean |x - flip x|, rows 70-220, columns 64-192): persons
  001-004: photo 19.4, D20 17.7, C20 18.7, B20 12.0, P_AF 2.1; all persons (medians): photo 12.9, D20 11.8, C20 13.4,
  B20 10.9, B 12.5. AD1b full run (32 persons, added 20:31 after the generator ended, set Mf): mirror mix against its
  re-run reconstruction 1.000 in every band (32 / 32), face-box statistic 1.3 against 12.8.
- More storage history (Y, F0, d [shift / K1 effect]): Lsoft fm61 own landmarks R0 +0.015 / -0.014 / +0.034 / +0.044
  / +0.038; R2w OpenCV +0.038 / +0.039 / +0.129 / +0.130 / +0.051; R2w FaceMorpher +0.034 / +0.046 / +0.118 / +0.134 /
  +0.032; Lsoft amsl112 within -0.02 to +0.09; Fm OpenCV (96) and Webmorph (100) |d| <= 0.03; Fe amsl -0.003 / +0.038
  / +0.067 / +0.030 / +0.013, Fe facemorpher |d| <= 0.04; SMDD 80 px (1,859 pairs) +0.035 / +0.060 / +0.048 / -0.085
  / +1.66 (B3-B5 beyond the copy's Nyquist). Full table in `tables.md` and `history.csv`.
- Blank sensitivity run (outside the mask = mean face colour, 187 hosts, R3 / R4): K1 0.576 / 0.607 / 0.650 / 0.600 /
  0.566 against the primary statistic on the same hosts 0.586 / 0.606 / 0.642 / 0.583 / 0.537
  (`blank_vs_primary_same_hosts.json`).

## 6. Checks

`as0_check.py` -> `check.json` (11 Nov 18:20): a symmetric image has E_A / E_S below 1e-7 in every band; a symmetric
image about a shifted axis (x = 250) has E_A / E_S below 2e-4 under the shifted flip F1; the squared band weights sum
to 1 within 1e-7; flipping a photo and its shape changes the energies by at most 1.2% (mask rasterisation at the
boundary); an exactly symmetric shape gives shape asymmetry ln = -72.9 (numerical zero). White noise gives
E_A / E_S = 0.52, 0.80, 0.89, 0.97, 1.00 in B1..B5 (0 in B0): in low bands the mask is only a few wavelengths wide and
pixels near the axis correlate with their own mirror, so the no-structure baseline is below 1 there. This baseline is
the same for every image of a frame type.

Further checks: the permuted-label run gives AUCs 0.47-0.52 (no structure from the code); R2 (tool on one photo)
against R0 is 0.500-0.503 (OpenCV bit-identical); two genuine photos (S0 against R0) 0.47-0.51; the ID0 typicality
on shapes calculated from the source files reproduces ID0's 0.687 exactly; detected 106-point landmarks deviate from
the `.tem` landmarks of the same photos by a median 0.8% of the IOD (R0) and from the calculated morph shapes by 0.8 to
1.2%; the three colour channels and the landmark-midline flip give K1 within 0.01 of luminance; K1 on two
person-disjoint halves agrees within 0.03; blanking outside the mask changes K1 by at most 0.03 on the same hosts.

Not verified: the AF0 softened copies' re-alignment jitter (as0_lmcheck.py not run); the FRGC environment field is a
camera id, not tested.

## 7. Dead ends and failures

- `as0_lists.py` first run read `fm_graded/graded_log.json` as a mixing level (crash); fixed with a folder filter.
- A43 stored crops: no face found without padding (8 of 8); padded retry added.
- SMDD landmark file in normalised coordinates; first nominal IOD 0.249; fixed (x 256).
- Machine load about 140 from 18:50 to about 19:50: four re-plans of the compute chains (section 2); one Fm chunk
  measured twice (kept once at merge); X dropped; R8 FRGC dropped; blank run reduced.
- Final analysis first crashed (SMDD 80 px copies have no data in B4-B6: empty bootstrap); fixed.
- Blank run: the R3m / R2w rows were not blanked (reduced plan), so the K5 row of the blank table is empty (0 / 0).
- The registered geometry share in log units is degenerate (mirror self-morph near zero); energy version added.

## 8. Observations and ideas

- Every AR1 same-person morph (R3) is cross-session; the record's r8 same-person morphs provide same-session
  (colorFERET fa + fb, expression change) and cross-session pairs in the same frame.
- The expanded123 DiffAE blocks contain non-frontal colorFERET captures (rc, qr), useful as a pose stress test.
- In the diffusion autoencoder, mixing a neutral and a smiling photo of one person gives a MORE asymmetric face than
  either reconstruction (C20 against D20 0.37-0.46): the expression mix is not a clean same-person control for an
  asymmetry statistic; the 0.74 of B20 against C20 is mostly C20 being high.
- In the GAN family the ratio falls for any mix of two codes (same-person or two-person alike), as the paired
  differences experiment (PD1) found for CLIP features ("two codes were mixed").
- Symmetrising only the geometry (R2wm) removes a large part of the asymmetric energy in B3-B5 (AUC 0.71-0.74
  against R0): much of the per-band asymmetry of an aligned face photo is shape, which the landmark statistics already
  measure.
- The two-person landmark morph keeps 61-68% of the warp-only asymmetric-energy ratio in B1-B3 instead of 50%. The
  look-alike explanation first written here is disfavoured and withdrawn (21:00): partner similarity correlates with
  a slightly LARGER loss (Spearman -0.10 [-0.18, -0.01], review F9, recomputed post hoc). R2w having the H-S mean
  shape is answered by A14 (geometry is a third of the gap).
- Statements corrected after the review (21:00): "clean" with respect to storage history is replaced by
  "history-stable, not history-free"; the mirror self-blend positive control is algebra (built with the statistic's
  flip), the dose curve is the informative control; the 0.69 against same-session same-person morphs (colorFERET only,
  best band) and the pooled 0.84 (mixes databases) are not to be quoted; "B2 and B3 at or above 0.60" was wrong (only
  B3).

## 9. Open items and next steps

**Closed** (lead, 11 Nov 21:00). Remains for after the deadline (not before 14 Nov):
- the learned head on f(x) - f(flip x) of frozen features (the A14 texture excess +0.08 meets the review's rule for
  revisiting it);
- same-session same-person morphs on FRGC (session split on 80% of the pool).
Dropped: the expanded123 DiffAE blocks (X) and the R8 FRGC pairs. The diffusion expression-mix read (review H-new-3)
belongs to the frozen read of the new diffusion ladder (FZ2), not to this experiment.

## 10. Handover state (21:00 CET)

No AS0 process is running (last: `chain_a14.sh`, "done 20:49"; `as0_a14.py` and `as0_posthoc.py` ran in the
foreground). Nothing queued. Outputs on the T7 drive (`/mnt/t7/smad_next/AS0/`, 56 GB free at 20:46) and in this
folder. Compute: CPU only (DGX, nice 10, at most two processes, one in the last step); 0 GPU-hours; 0 USD.

## 11. Reproduce from scratch

```
P=/home/narolski/mambamorph-code/.venv-spark/bin/python; cd /home/narolski/smad-next/src/AS0
$P -I as0_lists.py
OMP_NUM_THREADS=2 nice -n 10 $P -I as0_landmarks.py --threads 2; $P -I as0_landmarks.py --merge
$P -I as0_measure.py --iod
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
nice -n 10 $P -I as0_measure.py --sets L,Lsoft,S
nice -n 10 $P -I as0_measure.py --sets R8 --db feret
nice -n 10 $P -I as0_landmarks.py --threads 2 --sets FmO,LsoftN,LsoftO,LD1,LD2; $P -I as0_landmarks.py --merge
nice -n 10 $P -I as0_measure.py --sets Fm --roles native,e7_FaceMorpher; $P -I as0_measure.py --sets FmO --roles e7_FaceMorpher
nice -n 10 $P -I as0_measure.py --sets D,M,G,Ds,LsoftN,LsoftO; $P -I as0_measure.py --sets Fe --roles native,e7_facemorpher,e7_amsl
nice -n 10 $P -I as0_measure.py --sets Fm --roles e7_OpenCV,e7_Webmorph
nice -n 10 $P -I as0_measure.py --blank --sets L --roles R3,R4 --subsample 3
nice -n 10 $P -I as0_measure.py --blank --sets Fm,FmO --roles native,e7_FaceMorpher
$P -I as0_measure.py --merge; $P -I as0_measure.py --merge --blank; $P -I as0_check.py; $P -I as0_geom.py
nice -n 10 $P -I as0_analyse.py --B 2000; $P -I as0_typ.py; $P -I as0_tables.py
# after the review: post hoc addendum, then A14 (list rows L4 / LD4 added by as0_lists.py)
$P -I as0_posthoc.py; $P -I as0_lists.py; ./chain_a14.sh; $P -I as0_a14.py
```

## Log of README updates

- 11 Nov 18:25 CET: first version.
- 11 Nov 18:47 CET: review, amendments A1-A13, chains.
- 11 Nov 19:40 CET: primary results (section 5), restructured chains.
- 11 Nov 20:30 CET: final phase-1 state: all families, R8, detected landmarks, blank run, next steps, handover.
- 11 Nov 21:00 CET: review corrections, post hoc addendum, A14, closed.
