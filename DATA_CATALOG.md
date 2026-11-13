# Data catalogue (data building, DATA)

Owner: data-building owner (DATA), one of the five standing roles (OWNER_BRIEF.md). First version written 13 Nov 2026,
18:55-19:03 by the machine clock (`date`), read-only and CPU only. Nothing was hashed, copied, moved, built or deleted
for this catalogue. Sizes are `du --apparent-size` at 13 Nov about 19:00. Image counts are file counts
(`find -type f` on png/jpg/jpeg/ppm/bmp) or the count stated in the named README or manifest. Licence terms are copied
from a file on disk where one exists (marked "on disk"); otherwise they are the project's earlier notes or general
knowledge and are marked "not verified". This catalogue gives no image, no file name and no identifier of NIST MEDS.

Disk at 19:00: `/mnt/t7` 1.8 TB, 196 GB free (90%). Root disk `/` 916 GB, 22 GB free (98%).

## Status words

- **closed benchmark**: never used for training, selection or development scoring; read only in the registered sealed
  read. FRLL and everything built on FRLL photos, MAD22, MorDIFF, DiM, H1, FEI, CASIA-WebFace.
  Exception already ruled by the author (13 Nov about 18:36): the frozen candidate's single MAD22 read, which also
  scores the 204 FRLL photos.
- **sealed**: not opened, not listed, not catalogued beyond its name.
- **development only**: scoring and comparison during development; never training.
- **training source**: may enter training manifests (with the guards named in the row).
- **restricted terms**: usable under the stated terms; no image, file name or identifier leaves the machines.
- **do not use**: ruled out by the author.
- **in progress, owner X**: being built tonight by another owner; DATA enters it only.

## Flags used in the tables

- **NO-MAN**: no manifest (no file list with per-file hash) found.
- **NO-SUM**: no checksum file found (neither SHA256SUMS nor a per-file sha in a manifest nor an archive hash).
- **NO-BLD**: no builder script and commit recorded (raw downloads are marked "download" instead).
- **OFF-T7**: the only copy sits outside `/mnt/t7` (home disk, `/dev/shm`, `/tmp`, a cluster or a rented machine).

## 1. Sealed sets (names only; not opened, not listed)

| Name | Status | Note |
|---|---|---|
| VAL-X (val10 persons of FRGC and colorFERET) | sealed | A directory named `valx` exists under `/home/narolski/mambamorph-code/smadcvpr_data/` (home disk). Not opened. Its location outside `/mnt/t7` is recorded as a fact of the name only. The allowed `valx_a.csv` was not opened either. |
| FST | sealed | location not catalogued |
| A12SP | sealed | location not catalogued |

Persons of VAL-X are excluded from every product below through `prep_train.is_val` (record's rule) and the PN1 split
files; no row of this catalogue was checked against VAL-X content.

## 2. Raw datasets (`/mnt/t7/Datasety`)

Builder for every row of this section: download or copy from the distributor ("download"); no project builder.

| Dataset | Path | Size | Checksum record | Source, licence / terms | Images / persons | Status | Flags |
|---|---|---|---|---|---|---|---|
| FRGC 2.0 stills | `Datasety/FRGC-2.0/FRGC-2.0-dist/nd1/`, BEE `BEE_DIST/` | 69 GB | none found | FRGC licence agreement (in use since the record; text not re-read) | 39,328 JPEG, 568 subjects (asset inventory D) | training source (non-val10 subjects) | NO-SUM, NO-MAN |
| colorFERET | `Datasety/colorferet/dvd{1,2}/`; archive `Datasety/colorferet.tar` (8.0 GB) | 7.9 GB | none found | NIST colorFERET release agreement (in use; not re-read) | 11,338 images, 994 subjects | training source (non-val10 subjects) | NO-SUM, NO-MAN |
| colorFERET subset | `Datasety/downloads/feret_bonafide/` | 41 MB | none | copy of colorFERET frontals (origin not recorded) | 356 JPEG, 166 subjects | training source (as colorFERET) | NO-SUM, NO-MAN, NO-BLD |
| FRLL (London face set) | `Datasety/downloads/frll_base/{*.zip, extracted/}` | 546 MB | none found (zips only; `facelab_london.pdf` on disk) | figshare release; licence CC BY 4.0 (not verified here) | 1,225 extracted files; 102 persons x 2 frontal used | **closed benchmark** | NO-SUM |
| FRLL-Morphs | `Datasety/downloads/FRLL-Morphs/facelab_london/`; archives `FRLL-Morphs.tar`, `.tar.gz` | 221 MB | `FRLL-Morphs.MD5SUM.txt` (md5 of the .tar.gz only) | Sarkar et al.; README.txt on disk (terms not re-read) | 7,061 files (AMSL, FaceMorpher, OpenCV, StyleGAN, WebMorph) | **closed benchmark** | per-file NO-SUM |
| MAD22, corrected population | `/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted/` | 7.6 GB (folder) | `marco_owncloud_20261109T103840Z/SHA256SUMS`; committed list `mambamorph-code/experiments/dataaudit/.../verified_inventory.json` (408e50e) | dataset author's re-upload (ownCloud, 9 Nov); terms not verified | 4,687 (204 genuine, 4,483 morphs), 102 persons | **closed benchmark** (one registered read of the frozen candidate approved) | none |
| MAD22, old subset (must not be used) | `Datasety/downloads/MAD22/original_sorted/` (+ `original_sorted_backup_partial`, `incoming`) | 9.3 GB | none | as above | 4,254 | **do not use** (185 + 4,069 subset; asset inventory B) | NO-SUM |
| MorDIFF | `Datasety/downloads/MorDIFF/MorDIFF_crop/`; zip `MorDIFF_crop.zip` | 47 MB | none | CC BY-NC-SA 4.0 (asset inventory A.1, checked 11 Nov) | 1,000 files | **closed benchmark** | NO-SUM |
| DiM-FRLL-Morphs | `Datasety/downloads/DiM-FRLL-Morphs/morphs/{dim_a,dim_c,fast_dim,fast_dim_ode,greedy_dim,greedy_dim_s}` | 261 MB | none | CC BY-SA 4.0 (HF page; README.md on disk) | 2,999 | **closed benchmark** | NO-SUM |
| FEI | `Datasety/downloads/FEI/{originalimages_part1-4.zip, extracted/}` | 680 MB | none | FEI face database, research use (not verified) | 2,800 JPEG, 200 subjects | **closed benchmark** | NO-SUM |
| CASIA-WebFace (insightface RecordIO) | `Datasety/downloads/CASIA-Webface/train.{rec,idx,lst}` | 3.1 GB (folder) | none | research use (not verified) | about 501k crops, 10,572 identities | **closed benchmark** (H1 source); used by MS1 for embedding-only exclusion with the lead's approval | NO-SUM |
| Face-verification packs in the same folder | `Datasety/downloads/CASIA-Webface/{lfw,calfw,cfp_ff,agedb_30,cfp_fp,cplfw}.bin` | (in folder above) | none | LFW / CALFW / CFP / AgeDB terms (not verified) | lfw, calfw, agedb_30 12,000 slots each; cfp_ff 14,000 (TT1 README) | development only (TT1 unseen genuine; cplfw and cfp_fp never opened) | NO-SUM |
| SMDD | `Datasety/downloads/SMDD/SMDD_release_{train,evaluation}/` (+ zips), `os25k_m_{t,e}/`, landmark and ArcFace npz | 30 GB | none found | Damer et al.; CC BY-NC-SA 4.0 per its GitHub README (not re-read) | train 40,000; evaluation 78,206; os25k_m_t 25,000; os25k_m_e 25,000 | training source (released recipe; synthetic identities) | NO-SUM |
| FFHQ-1024 | `Datasety/downloads/FFHQ-1024/Part{1..7}/` | 90 GB | none | NVIDIA FFHQ; images CC BY 2.0 / BY-NC 2.0 / PD, dataset CC BY-NC-SA 4.0 (FFHQ-Morphs LICENSE on disk restates this) | 70,000, no identity labels | development only (see MS1 for the selected training subset) | NO-SUM, NO-MAN |
| FFHQ-Morphs | `Datasety/downloads/FFHQ_Morphs/FFHQ-Morphs/{diffae,landmark-combined,landmark-complete,stylegan-interp-W,stylegan-interp-W+}`, tarballs, `_docs/` | 24 GB | none (per-file metadata JSON inside `_docs`, not hashed) | Idiap; CC BY-NC-SA 4.0 (`_docs/FFHQ-Morphs/LICENSE.txt`, on disk) | 5 x 5,000 = 25,000 | **development only** (development comparison set; lead's ruling, GX1 amendment 1b) | NO-SUM |
| CelebA-HQ (HF mirror) | `Datasety/downloads/CelebA-HQ/CelebA-HQ-1024.zip` | 32 GB | `CelebA-HQ-1024.zip.sha256` (bda2d6f0...) and `SOURCE.txt` | third-party mirror Iceclear/CelebA-HQ1024; CelebA terms non-commercial research, no redistribution; mirror says apache-2.0, which is not the original licence (SOURCE.txt, on disk); **author to check; reminder set for 15 Nov** | 30,000 PNG, no identity file | **training source** (author, 13 Nov 09:10) | none |
| CelebAMask-HQ | `Datasety/downloads/CelebAMask-HQ/` | 0 (empty) | - | - | 0 | empty folder; the HQ-to-CelebA mapping needed by LA1 is not on disk | - |
| CelebA aligned (128 px, labelled) | `Datasety/datasets_processed/data-celeb-aligned/{images/, split.csv}` | 1.0 GB | none | CelebA, non-commercial research (not verified); processed copy of unknown origin (June 2026) | 202,084 JPEG, 10,177 identities (`split.csv`) | development only (MS1 calibration; LA1-0 candidate) | NO-SUM, NO-BLD |
| Chicago Face Database 3.0.1 | `Datasety/downloads/ChicagoFaceDatabase/cfd/` | 1.8 GB | none | CFD research licence (not verified) | 1,441 files; 827 persons (MS1 README) | **development only** (MS1 held-out evaluation source; never training, lead's ruling) | NO-SUM |
| KDEF and AKDEF | `Datasety/downloads/KDEF_and_AKDEF/` | 501 MB | none | KDEF terms (research; image publication restricted; not verified) | 5,112 files; KDEF 70 persons x 2 sessions; AKDEF are averaged faces, never genuine | **development only** (MS1 held-out, printed secondary) | NO-SUM |
| MUCT | `Datasety/downloads/MUCT/*.tar.gz` | 270 MB | `SHA256SUMS.txt` (on disk) | README.txt (on disk): do not reproduce images in public documents except subjects 000, 001, 002, 200, 201, 400, 401, 402 | 3,755 images, 276 subjects (LA1 plan) | development only, descriptive (dropped from LA1: eye distance below the filter) | none |
| NIST SD32 MEDS I-II | `Datasety/downloads/NIST_SD32_MEDS/` (archive, `unpacked/`) | 220 MB | `sd32-MEDS_I-II.tar.gz.sha256` (26c3c790..., matches NIST's reply) and `SOURCE.txt` | NIST terms (SOURCE.txt, on disk): research, development and education only; no further distribution; no attempt to defeat de-identification; delete on NIST request; acknowledge NIST. Author 13 Nov: may be kept on all project machines, rented machines and clusters; **no image, file name or identifier in any figure, repository or artifact** | 2,018 JPEG (MEDS-I 712 of 380 subjects; MEDS-II 1,306 of 518 subjects) | **restricted terms**; development only (TT1-M unseen genuine source) | none |
| Multi-PIE (third-party crops) | `Datasety/downloads/multipie/multipie.zip`, `probe/` | 4.3 GB | none | third-party crop release, not the official distribution; licence not verified | 129,480 crops of 128 px, 249 subjects | unusable (128 px; rejected A23, MS1) | NO-SUM |
| FLUXSynID | `Datasety/downloads/FLUXSynID/FLUXSynID.zip` | 11 GB | none | - | 89,361 files | **do not use** (ruled out by the author, 12 Nov) | - |
| Anti-spoofing frames | `Datasety/datasets_processed/{replay_attack,msu_mfsd,oulu_npu,casia_fasd}/` + `metadata.json` | 51 MB in all | none | Replay-Attack, MSU-MFSD, OULU-NPU, CASIA-FASD EULAs (not verified); processed frames of unknown origin (June 2026) | 1,200 / 280 / 4,950 / 600 frames (TT1 README) | development only (TT1 genuine frames) | NO-SUM, NO-BLD |
| Note | `datasets_processed/ml-research-face-morphing-detection-s-mad-d-mad.md` | 6 KB | - | - | - | text file, not opened | - |

## 3. Derived products on `/mnt/t7/smad_next` (this sprint)

Commit = last commit touching the builder (git log, 13 Nov about 19:00). Score files, feature caches, network tars and
job packs are not catalogued file by file; packs are named where they carry the only list of a training set.

| Product | Path | Size | Checksum record | Builder (commit) | Images / persons | Status | Flags |
|---|---|---|---|---|---|---|---|
| Landmark ladder (AR1): hosts, rungs R0, R2, R2w, R2wm, R2w4, R3, R3m, R4, NC, graded FaceMorpher, both engines (OpenCV, FaceMorpher) | `smad_next/AR1/{src,img,mirror,blank,crops}/`, `manifest.csv` (19,515 rows, 9c69d44f...), `pool.csv` | 25 GB | manifest sha 9c69d44f... and `pool.csv` 86101978...; the manifest has no per-file hash column | `src/AR1/{pool,build,variants,graded_fm,blank,manifest}.py` (5a19286, 0fa3277) | 536 hosts (FRGC 427, colorFERET 109), 536 per rung and engine | training source (training-host rows, PN1 split L) and development (test T / development D hosts); 8 val-reserved hosts flagged | per-file NO-SUM |
| Ladder, FRLL side | `smad_next/AR1/frll_src/`, `pool_frll.csv`, bridge lists, FRLL rows of `img/` | (in AR1) | `pool_frll.csv` c69a96df... | `src/AR1/frll_prep.py` (5a19286) | 102 persons; 102 per rung and engine; bridge 2,443 | **closed benchmark** (built on FRLL photos) | none |
| AF0 morph fields, halves, softened copies | `smad_next/AF0/{src,img,maps,lists}/`, `manifest.csv` (43becaca...) | 83 GB | manifest sha 43becaca...; no per-file hash column | `src/AF0/{pairs,af_morph,ghost,soften}.py` (45d3ea0) | 715 photos; 5,000 morphs; halves for 1,680 pairs; 481 training and 115 development persons kept (PN1) | training source / development by the PN1 split | per-file NO-SUM; `src/` frames were copied from `/dev/shm` arms (section 6) |
| Protocol network manifests A, B, Bn, C, Sp, eval (PN1) | `smad_next/PN1/manifests/` (+ `pn1_pack*.tar`, `pn1_pack_fs.tar` 96c31ae2...) | 29 GB (PN1 folder) | sha256 in `manifests_summary.json` and pack `.sha256` | `src/PN1/mkmanifests.py`, `mkmanifests2.py` (652236c) | A 1,526 unique; B 5,099; eval 23,640 rows (includes closed benchmark cells for the sealed read) | training source (train_*); eval rows mixed (development + closed) | none |
| PN1 softened and JPEG copies | `smad_next/PN1/img/soft/`, `img/jpeg/{jpeg90,jpeg70}/` | (in PN1) | `jpeg_build.csv` log | PN1 (652236c) | 452 + 2,549 | development / training (C) | none |
| MS1 FFHQ source (selected FFHQ persons, AF0-style and ladder morphs, hold-out) | `smad_next/MS1/ffhq/` | (in MS1, 43 GB) | `select_log.csv` (raw and frame sha), `SbM3_files.csv` (sha of every training image), `excluded_raw_sha256.csv` | `src/MS1/{ffhq_select,ffhq_build}.py`, `mkmanifest.py` (9f02906) | 3,263 training images; hold-out 300 persons (1,480 rows) | training source (training part); development only (hold-out) | none |
| MS1 CelebA-HQ prepared frames and person grouping | `smad_next/MS1/celebahq/{frames/, align_log_*.csv, emb_*.npz, persons.csv, ref_*.npz}` | (in MS1) | zip sha checked (`zip_sha_ok`); per-frame sha256 in `align_log_*.csv` (column frame_sha256) | `src/MS1/celebahq_prep.py`, `celebahq_persons.py` (255c047) | 22,806 aligned of 30,000; 9,898 kept images of 3,220 persons (1,814 with 2 or more) after overlap drops | training source (author 13 Nov); persons are embedding clusters, not labels | none |
| MS1 held-out CFD and KDEF frames | `smad_next/MS1/{cfd,kdef}/`, `ms1_heldout_pack.tar` (06b64608...) | (in MS1) | pack sha256 | `src/MS1/heldout_pool.py` (f748da4) | CFD 831 frames of 827 persons; KDEF 140 of 70 | development only | none |
| MS1 training manifests SbM3, SbM3S, SbV | `smad_next/MS1/manifests/`; summaries in `experiments/MS1_.../manifest_*_summary.json` | - | sha in summaries | `src/MS1/mkmanifest*.py` | see summaries | training source | none |
| TT1 unseen genuine (anti-spoofing frames, verification packs) raw and aligned | `smad_next/TT1/{raw,aligned}/`, `raw_manifest.csv` (a7aebe16...), `aligned_manifest.csv` (8b3c6fa9...) | 51 GB (TT1) | per-file sha in both manifests; gz copies in `experiments/TT1_.../` | `src/TT1/extract.py`, `align.py` (3912ae4) | 25,241 raw and 25,241 aligned | development only | none |
| TT1-M NIST MEDS frames | `smad_next/TT1/meds_src/`, `smad_next/TT1/meds/{aligned/, meds_manifest.csv, tt1m_meds.tar}` | (in TT1) | per-file sha in `meds_manifest.csv`; `tt1m_meds.tar.sha256` | `src/TT1/meds/build_meds_pack.py` (7e6e913) | 1,018 images of 446 persons; 865 aligned of 400 persons; 157 persons with 2 or more encounters (`meds_counts.json`) | **restricted terms**; development only | copy also staged on rented se1d (`/workspace/tt1m`) for scoring; the `/mnt/t7` copy is the master |
| TT1 border and geometry references | `smad_next/TT1/{border_ref,geo_ref}/` + csv | (in TT1) | not checked | TT1 | not counted | development only | to confirm |
| AG1 MIPGAN-I / MIPGAN-II renders, FERET and FRGC persons (R2, R2i, R3, R3m, R4, RT, BR, AG3) | `smad_next/AG1/data/` (pins `AG1_data_pins.sha256`), result tars `AG1/results/` | 11 GB | `AG1_data_pins.sha256`, tar sha | `src/AG1/build_inputs.py`, `ag1_gen.py` (5a19286) | 200 FERET/FRGC persons; rung counts in the AG1 README | training source / development by person split | none |
| AG1 MIPGAN renders of FRLL persons | `smad_next/AG1/data/` (FRLL shards) | (in AG1) | as above | as above | 102 persons | **closed benchmark** (FRLL persons) | none |
| DG1 DiffAE renders on the ladder pool (sets A, B, add-on) | `smad_next/DG1/{pool_in,pool_a256,gen}/`, `validity/` manifests | 3.7 GB | `pool_a256.sha256`; result tar sha in `athena_results/`, `rented_results/`; `manifest_full.csv` per set | `src/DG1/` (b4aedd9) | set A 914 (FRLL), set B 3,616 (ladder pool), add-on 1,218 + 1,130 | set A: **closed benchmark** (FRLL); set B and add-on: development | add-on face codes: Athena only (OFF-T7, by design); shard 7 codes lost 12 Nov (OWNER_BRIEF) |
| SE1 same-person self-morphs | `smad_next/SE1/img/selfm/`, `mirror/`, `manifests/` | 2.3 GB | per-image sha in `selfm_build.csv`; `se1_overlay.tar.sha256` | `src/SE1/` (19fed7b) | 644 | training source (SE arm) | none |
| AB1 ablation and border-crossed manifests (Sb variants, Sbx) | `smad_next/AB1/{manifests, x/, b2/}`, overlays with `.sha256` | 6.5 GB | overlay sha256 files; pins `pins_x.sha256` | `src/AB1/` | see AB1 prereg | training source / development | AB1 overlay v1 (4e3afaa1...) only on WCSS: smoke only, superseded |
| Border rows (3,582, copied unchanged from TT1 into `ab1x_eval.csv`) | inside `smad_next/AB1/x/` | - | `ab1x_eval.csv` 5257fb63... | `src/AB1/` (7e4a974) | 3,582 rows | development only | none |
| RZ1 overlay (512 input study) | `smad_next/RZ1/` | 9.8 GB | `rz1_overlay.tar.sha256`, `overlay_tree/rz1/RZ1SUMS` | `src/RZ1/` | see RZ1 prereg | training / development | none |
| SM1 SMDD-recipe rebuild data (crops, landmarks, halves hn2) | `smad_next/SM1/` | 39 GB | `hn2/*.sha256`; others not checked | `src/SM1/` | not counted | training source (released recipe) | partly unchecked |
| CB1 SMDD training crops pack | `smad_next/CB1/packs/smdd_train_cropped.tar` | (in CB1, 27 GB) | `.sha256` | `src/CB1/` | not counted | training source (baseline retrains) | none |
| AD1b DiffAE pool and generation | `smad_next/AD1b/` | 502 MB | `pool_selection.csv`; no SUMS file found | `src/AD1b/` | not counted | development | NO-SUM (to confirm) |
| FINAL MAD22 read pack | `smad_next/FINAL/FINAL_mad22_pack.tar` (+ test8), `tree_FINAL_mad22*/` | 25 GB | pack `.sha256`; `SHA256SUMS` in trees | FINAL owner; `src/FINAL` has no commit at 19:00 | MAD22 corrected cells | **closed benchmark** pack | NO-BLD (builder not committed at 19:00) |
| Legacy RAM-disk landmark twins R8 (copy) | `smad_next/volatile_backup_20261111/{r8_cv,r8_fm}/` (+ GAN protocol, own-generation canonical256, A138, MAD22 raw manifest copy) | 2.9 GB | `SHA256SUMS` written 13 Nov 19:05 by DATA (17,506 files, sha 77f37bf06f5fcf5e...); r8_cv and r8_fm (5,002 files) match `/dev/shm` byte for byte | record's `smadcvpr/build_arms.py` (mambamorph-code; commit not recorded here) | 2,500 per tool | training identities of old networks; development use only after a person check | none |
| R6 extra FRGC stills and r6/r8 logs (copy of `/dev/shm/smad_arms`) | `smad_next/volatile_backup_20261113/` | 1.6 GB | `SHA256SUMS` (8,454 files, sha 9f1a8eb24646de14...), computed on the source and checked on the copy | `cp -a` by DATA, 13 Nov 19:04 (lead's go) | 4,223 png + 4,223 tem; r6_feret is an empty directory at the source | as R6 in the record: training-split FRGC subjects | none |

## 3b. Products built by DATA (`/mnt/t7/smad_next/DATA/`, builders in `src/DATA/`)

| Product | Path | Size | Checksum record | Builder | Images / rows | Status | Flags |
|---|---|---|---|---|---|---|---|
| D1d one-photo FaceMorpher renders R2 = tool(H, H) of the MS1 FFHQ frames | `DATA/D1d/facemorpher/R2/<key>.png`, `manifest.csv` (1bfa13ec...), `SHA256SUMS`, `build_log.json`; 8-image test in `DATA/D1d/test8/` | 367 MB | `SHA256SUMS` (898 files, checked), input and output sha256 per row | `src/DATA/d1d_fm_r2.py`, unchanged `96_facemorpher_tool.py` (954e9c02..., same file as AR1) | 898 of 900 (af0 449, hold-out 299, ladder 150); 2 dropped, a known limit of the unchanged tool: it raises IndexError (landmark index 512 outside the 512-pixel frame) on FFHQ keys 69321 (part af0) and 08060 (part hold-out) | development (hold-out rows) and training-person rows; a control for FaceMorpher morphs, none of which exist yet on FFHQ | none |
| D1a paired-control coverage table | `DATA/D1a/coverage.csv`; copy `experiments/DATA_builds/D1a_coverage.csv` | small | file sha in the README | `src/DATA/d1a_coverage.py` | 37 rows | lists only | none |
| D2 MEDS cross-encounter genuine pairs | `DATA/D2/meds_cross_encounter_pairs.csv` (+ `.sha256`, `counts.json`); counts only in `experiments/DATA_builds/D2_counts.json` | small | list sha 2ac6112e... | `src/DATA/d2_meds_pairs.py` | 941 pairs, 157 persons, 560 images | **restricted terms**; development only; ids never in the repository | none |
| D5 border- and resolution-balanced genuine lists, version 3 | `DATA/D5/genuine_balanced_{bied,border}_{all,nomeds}.csv` (+ `.sha256`), `frames_measured.csv` (border of 13,024 MS1 FFHQ, CelebA-HQ, AR1 and AF0 frames), `frames_ied.csv` (their source eye distance, sha a8be02e4..., detection only with the unchanged 73_delin_align detector), `genuine_balanced_biedstrat_{all,nomeds}.csv` (cells balanced within each source), `cells.json`; cell table in `experiments/DATA_builds/D5_cells.json`. Version 1 files `genuine_balanced_{all,nomeds}.csv` kept, superseded | small | list sha: bied_all b45c6ed9..., bied_nomeds e18dac9a..., border_all 46d237d0..., border_nomeds 97b3f30c...; frames_measured 6090a0ba... | `src/DATA/d5_measure_border.py`, `src/DATA/d5_measure_ied.py`, `src/DATA/d5_balanced_genuine.py` | border x eye distance, all sources: 6 x 176 = 1,056 with MEDS, 6 x 19 = 114 without; stratified by source: 1,028 rows with MEDS, 878 without (per-source counts per cell in `D5_cells.json`); border only (all sources): 2 x 1,120 = 2,240 with MEDS, 2 x 879 = 1,758 without | development only (MEDS rows: restricted terms; role column carries the PN1 split role of AR1 / AF0 rows, val-reserved persons left out) | AR1 / AF0 rows include training persons of the protocol arms (role column); MS1 FFHQ fills only one stratified cell |

| Partner-overlap audit outputs | `DATA/overlap/{clean_eval_hosts.csv, test_hosts_clean_of_dev.csv}`; counts in `experiments/DATA_builds/partner_overlap_*.json`, report `PARTNER_OVERLAP_AUDIT.md` | small | file sha in the report's CLAIMS | `src/DATA/partner_overlap_audit.py` | 16 training lists x 4 evaluation sets | development lists (FRGC / colorFERET ids on /mnt/t7 only) | none |
| Battery person and source lists (D7) and GD overlap (D8) | `DATA/battery/persons_{dev,tt1,meds,gd}.csv` (MEDS ids on /mnt/t7 only); counts `experiments/DATA_builds/{battery_person_source.csv, gd_overlap.csv, battery_set_training_overlap.json}` | small | sha in `battery_persons_summary.json` | `src/DATA/battery_persons.py` | dev 5,006, tt1 16,477, meds 446, gd 4,247 persons | development | none |

| D12a FFHQ FaceMorpher two-person morphs FM(H, B), MS1 hold-out frames, no mutual pairs (use this set) | `DATA/D12a/facemorpher/R4/<H>__<B>.png`, `pairs.csv`, `manifest.csv` (each row also points to the host's D1d render FM(H, H) with its sha256), `SHA256SUMS`, `failures.csv` (empty), `build_log.json` | 121 MB | `SHA256SUMS` (299, checked); manifest sha 9df020e1... | `src/DATA/d12_ffhq_fm_pairs.py --no-mutual`, unchanged `96_facemorpher_tool.py` (954e9c02...) | 299 morphs of 299 hold-out persons (each host once, partner once); pairing by eye distance, no sex matching (no label) | development only; **FaceMorpher is a seen engine for the SbFM arm (AB1)** | none |
| D12 same, first build (mutual pairs allowed) | `DATA/D12/` | 121 MB | `SHA256SUMS` (299, checked); manifest sha bd72f579... | as above without `--no-mutual` | 299 files, 190 distinct images: the 109 mutual pairs give byte-identical FM(A, B) = FM(B, A) | **contains duplicates: do not use**; kept, not deleted | duplicates |

## 4. In progress tonight (entered only; owners keep them)

| Product | Owner | Where | State at 19:00 |
|---|---|---|---|
| GAN morphs in training (GX1): new MIPGAN-I and MIPGAN-II two-person morphs and one-person renders of 311 FERET / FRGC persons (202 training, 109 development) | AG1 owner (GX1) | inputs `smad_next/GX1/inputs/`, pack `GX1/wcss_pack/` (GX1SUMS); outputs will come from WCSS 6315653 (smoke), 6315654_[0-11], 6315655_[0-7] | in progress, owner AG1/GX1; pending on WCSS |
| Border rows / border-equalised form for the sealed MAD22 read | FINAL owner | `smad_next/FINAL/` | in progress, owner FINAL |
| Second-engine block (FaceMorpher ladder rows R4fm 124, R2wfm 156, R2w4fm 124 of training hosts; arm SbFM) | AB1 owner | `smad_next/AB1/fm/ab1fm_overlay.tar` (681525d8...), WCSS 6315597_[0-4] | in progress, owner AB1; uses existing AR1 FaceMorpher images (no new generation) |
| Look-alike pair search (LA1) | LA1 owner | `experiments/LA1_look-alike-pair-search/` | plan only; author decisions open |

## 5. Older products on `/mnt/t7/smad_heldout` (record before this sprint)

Builders are the record's scripts in `/home/narolski/mambamorph-code/smadcvpr/` (commits not re-checked tonight).

| Product | Path | Size | Checksum record | Images / persons | Status | Flags |
|---|---|---|---|---|---|---|
| Corrected MAD22 processed (canonical512, E7) | `mad22_canonical_E7_inputs_v3_20261109T113746Z/{native,e7}` | 1.8 GB | `PROCESSED_SHA256SUMS` (5,707) | 4,687 + 1,020 | **closed benchmark** | none |
| MAD22 production / technical runs (staged weights, partial CPU runs) | `mad22_canonical164_production_v1`, `mad22_production_*`, `mad22_technical149_*`, `mad22_cpu_continuation86_*` | about 72 GB | SUMS only for `cpu_failure6295412`, `cpu_partial6295571` | - | closed benchmark scaffolding; not data products | NO-SUM for the rest |
| H1 Poisson landmark morphs (MediaPipe-478 + Poisson, `h1_build.py`) on CASIA look-alike pairs | `h1_poisson/data/` | 498 MB | `data/SHA256SUMS` | 598 + 598 | **closed benchmark** | none |
| H2 IP-Adapter-FaceID renders | `h2_embmid/data/` | 15 GB | `data/SHA256SUMS` | 992 + 992 (CASIA persons) | closed (CASIA-derived) | none |
| H3 StyleGAN3 morphs and A37 re-decodes | `h3_sg3/data/`, `a37_sg3ctl/data/` | 7.8 GB, 14 GB | `SHA256SUMS` each | 423 + 423; 19,570 files | closed (CASIA-derived) | none |
| H4 / H4b MIPGAN-I-style on CASIA | `h4_mipgan1/data/`, `h4b_mipgan1/data/` | 1.2 GB, 759 MB | `SHA256SUMS` (+ `_v2`) | 326 + 326; 338 + 338 | closed (CASIA-derived) | none |
| Arc2Face renders | `arc2face/data/` | 6.0 GB | `data/SHA256SUMS` | 548 + 548 | closed (CASIA-derived) | none |
| FFHQ morphs of the record (`ffhqm`) | `ffhq_morphs/` | 5.9 GB | `SHA256SUMS` | not counted | development only (record's FFHQ test) | none |
| DiffAE on FRLL (A41 X3: reconstructions, self-morphs, cross morphs) and A43 stored sets | `a41_diffae/data/`, `a43/data/` | 528 MB, 584 MB | `SHA256SUMS` each | 204 / 102 / 100; A43 counts in asset inventory C | **closed benchmark** (FRLL persons) | none |
| A41g, A41g2, A42, A44, A46, A47 working sets | `a41g*/`, `a42/`, `a44/`, `a46*/`, `a47/` | 0.6-31 GB | SUMS present except `a46_rgb_only_20261108` | not counted | record's diagnostics; mostly FRLL-based (closed) | NO-SUM: `a46_rgb_only_20261108` |
| A45, A50 | `a45/`, `a50/` | 15 MB, 4.2 GB | none | - | record's baselines | NO-SUM |

## 6. Copies outside `/mnt/t7` (flagged)

| What | Where | Only copy? | Note |
|---|---|---|---|
| Record's training frames and morphs behind `smadcvpr_data/train/` (genuine FERET 2,400 and FRGC 1,686 frames; OpenCV, OpenCV-68, WebMorph and FaceMorpher morphs of FERET 5,000 and FRGC 1,449 each) | `/home/narolski/mambamorph-code/baselines/{webmorph/aligned, webmorph/morphs_opencv, webmorph/morphs, facemorpher_out}/` (about 33 GB, home disk at 98%) | **yes, as far as found** (no copy located on `/mnt/t7`; AF0 and AR1 hold byte copies of a subset only) | OFF-T7, NO-SUM. Training data of the record's networks. |
| Record's evaluation frames and manifests | `/home/narolski/mambamorph-code/smadcvpr_data/{eval,gtest,manifests}/` (12 GB) | not checked | OFF-T7 (closed benchmark frames: frllm, mad22 old subset, mordiff, dim, FEI gtest) |
| FRGC extra stills R6 (4,223 frames, 490 subjects) and its provenance csv | `/dev/shm/smad_arms/r6_frgc/` (1.7 GB, RAM) | no longer: verified copy in `smad_next/volatile_backup_20261113/` (13 Nov 19:04) | `/dev/shm` left untouched; `r6_feret` holds no file, so nothing was at risk there |
| R8 landmark twins | `/dev/shm/smad_arms/r8_{cv,fm}` | no: copy in `smad_next/volatile_backup_20261111/` | backup has no checksum |
| SMDD 106-point landmarks | `/dev/shm/smad_arms/smdd_bona_landmarks_if106.npz` | no: also `Datasety/downloads/SMDD/` (byte equality not checked) | - |
| Corrected MAD22 raw manifest | `/tmp/opencode/.../raw_manifest.json` | no: copy `smad_next/volatile_backup_20261111/mad22_fixed_raw_manifest.json` | - |
| DG1 add-on face codes and fresh draws | Athena `.../smad-next/results/DG1/` | yes, by design (about 265 MB per shard) | shard 7 codes lost on 12 Nov |
| SelfMAD release weights | WCSS `A12REL` | yes (asset inventory) | weights, not data |
| MIPGAN-II / StyleGAN2 training morphs of the record (3,000 PNG, A28) | not located | unknown | asset inventory C: "files not located" |
| TT1-M MEDS pack | rented se1d `/workspace/tt1m` | no (master on `/mnt/t7`) | to be removed with the machine under the NIST terms |

## 7. Open checks (DATA, CPU only, no image operation)

1. Done 13 Nov 19:04-19:06: R6 copied and verified (`volatile_backup_20261113`); SHA256SUMS for `volatile_backup_20261111`.
2. Measure border fraction and source eye distance for the MS1 FFHQ, CelebA-HQ and AR1 / AF0 genuine frames (from existing .tem and align logs, no image operation), so D5 can fill its border-free and high-resolution cells without MEDS.
3. Decide with the author whether the record's training frames on the home disk (about 33 GB) get a verified copy on
   `/mnt/t7` (196 GB free; the 50 GB floor holds).
4. Per-file hash lists for the AR1 and AF0 images (manifests carry none), AD1b, SM1 and TT1 border references.
5. Licence texts not read tonight: FRGC, colorFERET, FRLL, FEI, CFD, KDEF, SMDD, CASIA-WebFace, anti-spoofing sets.
