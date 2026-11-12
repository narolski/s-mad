# Threshold transfer on unseen genuine sources (TT1): full record

Standard: `DOCUMENTATION.md`. Short verdict: `result.md`. Registration: `prereg.md` (pool building; section 3 registers
the scoring text `prereg_scoring.md` at 01557ce; section 4 pins at ccd6319). Draft history: `prereg_scoring_draft.md`. Code: `/home/narolski/smad-next/src/TT1/`. Large outputs:
`/mnt/t7/smad_next/TT1/`.

## 1. Question and current answer

Do the candidate detectors (CLIP ViT-B/16 + LoRA networks of the protocol network first tests (PN1)) keep their
false-alarm rate on genuine photos from sources they never saw, and if not, is the excess explained by how much the
small source face is enlarged to the canonical frame and by its sharpness, or by the source itself? Which training arm
(plain A, protocol B, protocol plus spliced positives Sb, and the controls Bn, C, Bv) gives the lowest and most uniform
genuine false-alarm rates? This is a false-alarm test only: there are no morphs of these sources.
Status at the commit that adds this section: genuine pools built and aligned (25,241 photos from 8 sources, 7
families); scoring registered (TT1-S, 01557ce) after the pre-run review (GO WITH FIXES, 7c0ecb6); references built and pinned
(ccd6319); WCSS H100 run in preparation (see Handover).

## 2. Timeline

- `date` Thu Nov 12 10:52:17 PM CET 2026: start; read OWNER_BRIEF.md, DOCUMENTATION.md, NOTEBOOK.md (last entries),
  PN1 BENCHMARK_EXPOSURE.md, REVIEW_PN1_TIER1_20261112.md, PN1 prereg.md (amendments 12-15, FS1). HEAD dac4d99.
- `date` Thu Nov 12 10:54:00 PM CET 2026: folders created; author's approval ("Run the aligner, of course!", relayed by
  the lead) recorded in prereg.md section 0.
- Genuine/attack convention of the anti-spoofing sets verified (how: section 3).
- 22:55:13-22:55:19 (`date` before and after): `extract.py` run (after the 8-per-source test). 25,241 distinct photos.
- 22:55:46-22:55:52: `align.py --limit 8` test (64 images). Then the full run, log `/mnt/t7/smad_next/TT1/logs/align.log`,
  668 s, finished 23:07:10 (log mtime). Outputs 25,241 aligned PNGs.
- `summary.py` -> `pools_summary.md/json`. Test outputs (raw_test, aligned_test, *_test.csv) removed (own files).
- After commit 3912ae4 (`date` Thu Nov 12 11:10:42 PM CET 2026): interim report to the lead.
- `date` Thu Nov 12 11:11:52 PM CET 2026 to 11:12:09 PM: DGX command test of `src/PN1/rescore.py` (unchanged) on 8 FFHQ
  bona fide rows already scored by pn1a (A_s401): max |logit difference| 0.0015 (`/mnt/t7/smad_next/TT1/dgxtest/`). No
  TT1 image scored.
- QC found after alignment, from the manifest only: 54 aligned frames with implausible enlargement (wrong, tiny
  detections; one viewed, 35x), LFW 40, CALFW 9, CFP-FF 1, AgeDB 4; excluded from the draft's primary pool by a band
  rule ([1.2, 2.5] for 224 px frames, [2.5, 5.0] for 112 px).
- `src/TT1/strata.py` -> `strata_edges.json` (fixed sharpness, enlargement and border quintiles; manifests only).
- Scoring registration drafted: `prereg_scoring_draft.md` (f4fe159), sent to the lead.
- Lead's message (after f4fe159): border-matched reference approved; WCSS H100 allowed; gate needed for the H100; pack
  must be reusable for FS1. Pre-run review `experiments/reviews/PRERUN_TT1_SCORING_20261112.md` (7c0ecb6): GO WITH FIXES,
  majors M1-M7; lead rulings R1 (build the crop-geometry control with the approved shrink path), R2 (packs outside the
  CASIA-WebFace closure; overlap statement; never-read assert), R3 (TT-H6 descriptive), R4 (H100 with G-DGX gate +
  Kendall; DGX fallback), R5 (MS1 FFHQ disjointness).
- `date` Thu Nov 12 11:23:08 PM CET 2026: `geometry.py` -> `crop_geometry.json` (median non-black boxes of U_p frames).
- Commit 01557ce (`date` Thu Nov 12 11:25:26 PM CET 2026): registration TT1-S (`prereg_scoring.md`).
- 23:26:12-23:26:53: `build_geo_ref.py` (after an 8-image test, one frame viewed): 834 geo references, all aligned.
- 23:27:10-23:28:19: border references rebuilt with the edge-connected mask (M3); the first build (every-black-pixel
  mask, made 23:17:45-23:18:59, never scored) deleted.
- 23:28-23:30: list (34,411 rows), network tar, pack (`build_pack.py`); gate_check.py set to the registered tolerances
  and the pack rebuilt with it.
- 23:30:49-23:32:00: local DGX test of `tt1_job.sh` in test mode (8 gate rows x 12 networks): max |Δlogit| 0.00067.
  gate_check self-test on identical scores: pass.
- Commit ccd6319: pins section. 23:33-23:37 WCSS folder check (waited for the shared lock); upload of pack, networks
  and job files started 23:37 (`/mnt/t7/smad_next/TT1/logs/upload.log`).
- Reader `tt1_read.py` written; mock test started 23:37:45.

## 3. Data

Inputs (read only):
- Anti-spoofing sets, genuine frames only, 224x224 JPEG: `/mnt/t7/Datasety/datasets_processed/{replay_attack,msu_mfsd,
  oulu_npu,casia_fasd}/` with `metadata.json`. Genuine = metadata label "Bona fide". Verified: `extract.py` asserts that
  the metadata label agrees, on every row (genuine and spoof), with each set's documented file-name convention:
  Replay-Attack live videos under `real/` (200 of 1,200 rows); MSU-MFSD `real_client...` (70 of 280); OULU-NPU video name
  Phone_Session_User_File with File 1 = real access (990 of 4,950); CASIA-FASD videos 1, 2 and HR_1 genuine (150 of 600).
  Agreement 1,200/1,200, 280/280, 4,950/4,950, 600/600 (`extract_report.json`). The metadata was written by an earlier
  preprocessing step (June 2026); the original dataset documentation is not on this machine, so the convention is the
  publicly documented one, checked against the metadata, not against the original readme files. One OULU-NPU genuine
  frame is a byte-identical duplicate of another (990 frames, 989 kept). Spoof frames are not copied.
- Verification packs, 112x112 JPEG: `/mnt/t7/Datasety/downloads/CASIA-Webface/{lfw,calfw,cfp_ff,agedb_30}.bin`, loaded
  only with a restricted unpickler (numpy `_reconstruct`, `ndarray`, `dtype`; everything else refused), `python -I`.
  Not opened: `train.rec/.idx/.lst` (CASIA-WebFace, closed), `cplfw.bin`, `cfp_fp.bin`. Slots / pairs / distinct:
  lfw 12,000 / 6,000 / 7,701; calfw 12,000 / 6,000 / 6,098; cfp_ff 14,000 / 7,000 / 4,737; agedb_30 12,000 / 6,000 /
  5,296. No byte-identical image is shared between any two packs (also not LFW and CALFW).
- Persons: anti-spoofing sets use the file-name person id (CASIA-FASD: "<train|test>_<number>", numbers restart).
  Packs have no identity labels: pseudo-identity = connected component over "same" pairs, per family (LFW and CALFW in
  one graph, family `lfw_calfw`; since they share no byte-identical image, no component spans both packs, although
  CALFW was built from LFW people). Components fragment true identities: cfp_ff 1,586 components (CFP has 500 people),
  agedb_30 2,338 (AgeDB has 568), lfw 4,859, calfw 3,098. A bootstrap over components is therefore anti-conservative
  for these packs (stated in the scoring draft).
- Not checked (would need opening a closed set): person overlap of the celebrity packs (CFP, AgeDB, LFW) with
  CASIA-WebFace / H1 persons. CASIA-WebFace was designed identity-disjoint from LFW (its paper); for CFP and AgeDB no
  such statement. TT1 trains nothing, and these photos are not compared with H1.

Produced:
- `/mnt/t7/smad_next/TT1/raw/<source>/` 25,241 files, 152,389,212 bytes: encoded bytes copied verbatim (anti-spoofing:
  original file names; packs: `<pack>_<first slot index>.jpg`).
- `/mnt/t7/smad_next/TT1/raw_manifest.csv` sha256 `a7aebe163328d12652c512fcb169152e7c3c4c31f63833d91e1ae3d63dd12168`
  (columns: id, source, family, person, person_kind, orig_file, pack_index, origin_id, origin_set, raw_path, sha256,
  bytes, n_slots, width, height, format, pil_mode, lap_var, chroma_mean, greyscale). Repo copy gzip -n:
  `raw_manifest.csv.gz` sha256 `ec156007cfa9f849741bfd62307c71aebf2e09707ab6fffac3420af2e34627e8`.
- `/mnt/t7/smad_next/TT1/aligned/<source>/<id>.png` 25,241 files, 4,780,540,514 bytes (512x512 PNG from prep_eval.align;
  aligned=0 rows are prep_eval's plain resize, written as prep_eval does).
- `/mnt/t7/smad_next/TT1/aligned_manifest.csv` sha256 `8b3c6fa932ac24c13a086984468539ba841f2facc1ac883be34c89b1c6971bef`
  (id, source, family, person, detected, aligned, ied_src, enlarge, fail_reason, border_frac, aligned_path,
  aligned_sha256). Repo copy `aligned_manifest.csv.gz` sha256
  `7bb2c5c12a85d07be08080377617aa273c4fdfc1b73ec14f6d5667635b3e4372`.
- Copies: DGX `/mnt/t7` only (raw files are re-extractable bit for bit from the inputs; aligned PNGs are regenerable by
  `align.py`, same GPU path). Nothing on rented machines or clusters.

## 4. Code

Run order (all with `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n 10`,
Python `/home/narolski/mambamorph-code/.venv-spark/bin/python -I`: Python 3.12.3, numpy 1.26.4, OpenCV 4.11.0,
insightface 1.0.1, Pillow 12.2.0; detection on the GB10 GPU via `dmad.quads.gpuface` as prep_eval does):
1. `src/TT1/extract.py` (sha256 `6aeec05eb86f1c58a8bff354f0b04ad6548c296901a2b8645f19aebd119b8710`): pools, raw manifest,
   `extract_report.json`. `--limit 8` is the test mode.
2. `src/TT1/align.py` (`8014ff51c6a81cc8fcaa2bba8227fafa9477f9d89d676a9973a1c8096e2cdc03`): imports
   `/home/narolski/mambamorph-code/smadcvpr/prep_eval.py` (pin `374408ab3a886e6df25b563bc2344d190efe2ab7b3163efbb17c9b6ca9100628`,
   asserted) and calls `align(img)` unchanged on `cv2.imread(raw file)`; buffalo_l detection at det 512 with
   prep_eval's padded retry, frontal filter, 2-eye similarity to eyes (190,210)/(322,210) (132 px), 512x512 PNG.
   Writes `aligned_manifest.csv`, `align_run.json`.
3. `src/TT1/strata.py` (`97ac2c602ed381d6a52d03985531b67d27c36bc3ef18cc4accc279f91a691e3c`): `strata_edges.json`
   (`4aa95f038397bd45b4446e59b3c696b03e091d042c2bfd5ff99d423fe0fdb798`).
4. `src/TT1/summary.py` (`fae542cf6d2388adb27c30d2d47f716cd9ab8dfc53bec3c41c97f934a03cd094`): `pools_summary.{md,json}`.
Measurements: lap_var = variance of the Laplacian (CV_64F) of the greyscale raw image; greyscale = JPEG mode "L" or
mean channel difference < 1.0; enlarge = 132 / source IED; border_frac = share of exactly-black pixels in the 512 frame.
No new image operation (no resize, blur, rotation or re-encode written by TT1 code).

## 5. Results (pools only; no score)

From `pools_summary.md` (aligned-only columns: IED, enlargement, border):

| Source (family) | Photos kept | Persons / pseudo-ids | Aligned | Fail no face / frontal | Median enlargement (p10-p90) | Median sharpness, Laplacian var. (p10-p90) | Greyscale | Median border |
|---|---|---|---|---|---|---|---|---|
| Replay-Attack | 200 | 50 | 1.000 | 0 / 0 | 1.73 (1.66-1.81) | 21.6 (15.3-32.8) | 0.000 | 0.43 |
| MSU-MFSD | 70 | 35 | 0.929 | 1 / 4 | 1.73 (1.65-1.81) | 73.9 (20.6-321.7) | 0.000 | 0.43 |
| OULU-NPU | 989 | 55 | 1.000 | 0 / 0 | 1.71 (1.65-1.78) | 643.9 (308.1-1252.5) | 0.000 | 0.44 |
| CASIA-FASD | 150 | 50 | 1.000 | 0 / 0 | 1.72 (1.66-1.84) | 86.4 (37.3-301.5) | 0.000 | 0.43 |
| LFW (lfw_calfw) | 7,701 | 4,859 | 0.784 | 0 / 1,666 | 3.51 (3.35-3.75) | 198.5 (90.8-441.3) | 0.004 | 0.40 |
| CALFW (lfw_calfw) | 6,098 | 3,098 | 0.818 | 2 / 1,109 | 3.51 (3.36-3.72) | 537.9 (244.3-1085.3) | 0.075 | 0.40 |
| family lfw_calfw | 13,799 | 7,957 | 0.799 | 2 / 2,775 | 3.51 (3.35-3.73) | 309.3 (110.3-830.1) | 0.035 | 0.40 |
| CFP frontal (cfp_ff) | 4,737 | 1,586 | 0.998 | 1 / 10 | 3.47 (3.25-3.68) | 1408.1 (618.9-2906.2) | 0.016 | 0.53 |
| AgeDB-30 | 5,296 | 2,338 | 0.743 | 0 / 1,359 | 3.52 (3.37-3.70) | 837.7 (228.7-2310.7) | 0.275 | 0.40 |
| all | 25,241 | 12,071 | 0.836 | 4 / 4,148 | 3.49 (3.25-3.71) | 508.3 (130.4-1827.5) | 0.080 | 0.42 |

## 6. Checks

- prep_eval.py pin asserted at import; not edited. Test runs on 8 images per source before both full runs.
- Genuine/attack convention: 100% agreement of metadata labels with the documented file-name rule (section 3).
- Raw copies: sha256 of every encoded image recorded; bytes copied, not re-encoded.
- Not verified: original anti-spoofing dataset readme files (not on disk); true identities of pack images.

## 7. Dead ends and failures

- Alignment failures: 4,152 of 25,241 (16.4%): 4 no face, 4,148 frontal filter (prep_eval's rule: nose off the eye
  midline by more than 0.16 IED, or eyes not level within 0.12 IED). By source: LFW 1,666 (21.6%), AgeDB 1,359
  (25.7%), CALFW 1,111 (18.2%), CFP-FF 11, MSU-MFSD 5, others 0. The 112 px crops did not defeat the detector (4 no-face
  cases); the failures are pose and roll in the in-the-wild packs. The 5 MSU-MFSD failures are all android clients
  003-009; the frame of client 003 viewed by the owner is upside down (rotated 180 degrees); not rotated (no new image
  operation). Failed frames are kept as prep_eval's plain 512 resize, flagged aligned=0.
- Owner error (no data effect): background "wait until align.py ends" loops matched their own command line with
  `pgrep -f` and never ended; killed (own processes).

## 8. Observations and ideas

- Every aligned TT1 frame carries a large black border (median 40-53% of the 512 frame), because the 224 / 112 px source
  crops cover only part of the canonical frame after enlargement. Training-source photos (FRGC 1704x2272, colorFERET
  512x768) and FFHQ fill the frame. The border is therefore confounded with "unseen source" for all eight sources; EV1
  and AD4 found our aligner's border to be a usable cue. The scoring draft adds a border-matched reference (constant-
  colour blanking of the reference photos with TT1 border masks, an allowed operation) to separate the two.
- Natural experiments: at a fixed enlargement of about 1.7 the four anti-spoofing sets span a 30-fold sharpness range
  (Replay-Attack 21.6 to OULU-NPU 644); at a fixed 112 px / about 3.5x the packs span about seven-fold (LFW 198.5 to
  CFP-FF 1408). Enlargement differs between the two groups by about 2x, but so do capture conditions.
- AgeDB-30 is 27.5% greyscale; CALFW 7.5%.

## 9. Open items and next steps

- Independent pre-run review of `prereg_scoring_draft.md`; lead decides platform (rented A100 with byte-identity gate,
  or DGX with equivalence gate); then build the scoring pack and run.
- Later: the 16 fresh-seed networks (FS1) under the same registration once their tars are verified.

## 10. Handover state

No process running. Nothing queued. Test files: `/mnt/t7/smad_next/TT1/dgxtest/` (8-row gate test, symlink to the HN2
tree, small). Compute: DGX GB10 about 11 minutes of detection (shared GPU), 0 USD.

## 11. Reproduce from scratch

```
cd /mnt/t7/smad_next/TT1
E="env OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n 10"
P="/home/narolski/mambamorph-code/.venv-spark/bin/python -I"
$E $P /home/narolski/smad-next/src/TT1/extract.py --limit 8   # test
$E $P /home/narolski/smad-next/src/TT1/extract.py
$E $P /home/narolski/smad-next/src/TT1/align.py --limit 8     # test
$E $P /home/narolski/smad-next/src/TT1/align.py
$P /home/narolski/smad-next/src/TT1/summary.py
$P /home/narolski/smad-next/src/TT1/strata.py
cd /home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine && gzip -n -9 -f raw_manifest.csv aligned_manifest.csv
```
