# Competitor baselines on the corrected MAD22 and FRLL-Morphs (CB1): full record

Owner: CB1 owner (agent), for Paweł Narolski. Code `/home/narolski/smad-next/src/CB1/`. Large outputs
`/mnt/t7/smad_next/CB1/`. Registration `prereg.md`; verdicts `result.md`.

## 1. Question and current answer

Which competitor rows of the paper's comparison tables can we verify on the corrected MAD22 (204 genuine + 4,483
morphs) and on FRLL-Morphs, and how? Status 12 Nov 2026, 23:55 CET: inventory done (section 3 and `result.md`),
registration written, CNN re-score running on the DGX GPU, IDistill code obtained and planned, FD-MAD code located.
No CB1 score read yet.

## 2. Timeline

- 12 Nov 23:22 CET (`date`: Thu Nov 12 11:22:32 PM CET 2026). Started. Repository at 681f6a5 (sprint-plan-v2).
  Read OWNER_BRIEF.md, DOCUMENTATION.md, NOTEBOOK.md (12 Nov entries), 10_ASSET_INVENTORY.md A-B,
  01_EVIDENCE_DOSSIER.md (A12-BR, A45 rows), 16_PLAN_NIGHT_12_TO_13_NOV.md, RS1 result, AD5 README/result,
  `/mnt/t7/smad_heldout/mad22_canonical164_production_v1/`.
- 23:26. IDistill cloned into an empty folder `/mnt/t7/smad_next/CB1/thirdparty/idistill_clone`
  (`git ls-remote`: HEAD 0473bb43007bb0088e90d226b59a2208d7e45856; no LICENSE file in the tree).
- 23:28. WCSS listing (one connection under the lock, waited on another owner's upload): A45 run dirs exist
  (`$L/runs/A45/a12_inception_v3_official_r224_..._s{1..5}_ofc`, `a12_hrnet_w18_scratch_r256_..._s{1..5}_fhr`) with
  es.pt, last.pt, meta.json and stored `scores_eval_{es,last}.npz`; A12-BR run dirs on WCSS hold meta.json and stored
  `scores_eval_{es,last}.npz` (the local backup BK holds only es.pt / last.pt).
- 23:30. Image list built: `python3 -I src/CB1/build_manifest.py /mnt/t7/smad_next/CB1/manifests/cb1_cnn_images.csv`
  (19,171 rows, sha256 10686dec76b73ba63e151c77c3839d936572950ab72991173b1e429562031623).
  Network list `/mnt/t7/smad_next/CB1/manifests/cb1_nets_bk.tsv` (76 checkpoints: es.pt and last.pt of M1 x5, M2 x5,
  M4 x5, M5 x8, M6 x5, M8 x5, M8O x5; sha256 per file; es.pt hashes equal the A36 network list).
- 23:32. Smoke on 8 images, one network per architecture (strict state-dict load passed for all 7 architectures).
- 23:34. Full scoring started on the DGX GPU (PID 513985, log `/mnt/t7/smad_next/CB1/logs/score_cnn_bk.log`,
  output `/mnt/t7/smad_next/CB1/scores_cnn/`). Scores are not read before `prereg.md` is committed.
- 23:40. IDistill paper (arXiv 2306.03002) saved to `/mnt/t7/smad_next/CB1/literature/` and read: autoencoder latent
  128, 300 epochs, batch 32, lr 1e-4; classifier ResNet-18, product fusion (Eq. 3), lr 1e-4, batch 16; KD loss Eq. 6-8.
  Its Table I prints OrthoMAD FRLL AMSL 14.80, the manuscript table 9.50.
- 23:55. `prereg.md` written. Committed with README / result as fb0c5d5 (pushed 23:36 by the machine clock; my
  earlier stamps in this list ran about 20 minutes ahead of `date` and are corrected from here on).
- 23:39 (`date`). CNN scoring restarted in two passes (es.pt first, then last.pt) because one pass over 76 networks ran
  at 15 s per batch: `cb1_nets_bk_es.tsv`, `cb1_nets_bk_last.tsv`; PID 519094 (loop), logs
  `/mnt/t7/smad_next/CB1/logs/score_cnn_bk_{es,last}.log`.
- 23:43. WCSS fetch (one rsync under the lock) of 212 files into `/mnt/t7/smad_next/CB1/wcss_copy/`: meta.json, es.json,
  stored `scores_eval_{es,last}.npz` of the 38 A12-BR run dirs, and of the 10 A45 run dirs plus their es.pt / last.pt
  (1.8 GB). A45 code root (archs_a12.py d7617dd1, common.py b5d42a99, a45_fdmad.py aa41b5a1) copied from the A45 job root
  to `/mnt/t7/smad_next/CB1/code_a45_jobroot/` (files whose names contain fst / valx / A12SP and the plans folder
  excluded). A45 network list `/mnt/t7/smad_next/CB1/manifests/cb1_nets_a45.tsv`.
- 23:44-23:57. IDistill: patch (`src/CB1/idistill/idistill_cb1.patch`: data paths from environment variables, seed
  from IDS_SEED, last checkpoint saved beside the selected one), W&B / torchinfo stubs, runner for `python -I`, CSV
  builder, scorer, job script `cb1_idistill.sbatch`. Data pack `/mnt/t7/smad_next/CB1/packs/idistill_data.tar`
  (sha256 aa161436...; 39,400 files: 25,000 os25k_m_t contributors, raw FRLL photos and FRLL-Morphs morphs, raw corrected
  MAD22, aligned native and E7 frames of both benchmarks; counts in `idistill_stage_counts.txt`). First build had a shell
  bug (a loop variable reused inside a function) that put the MAD22 E7 folders in the wrong place; rebuilt. Code pack
  idistill_code.tar (sha256 69a3cc41...). Uploaded to WCSS `smad-next/packs/CB1/` with copies of AD5's
  ad5w_wheels39.tar (ac10259a...) and smdd_train_cropped.tar (3189e52a..., SMDD release crop script output: 24,730 bona
  fide, 14,995 morphs); all four hashes verified on WCSS.
- 23:52. FD-MAD global re-score started on the DGX CPU (PID 603857; `src/CB1/fdmad_cb1.py`, res 256 then 512, seeds
  1-3; logs `/mnt/t7/smad_next/CB1/logs/fdmad_r*_s*.log`). Seed 1 at 256 reproduces the stored A45 scores on the 13,464
  eval.csv rows of the list: max abs difference 1.3e-4, median 1.0e-5 (probability scale).
- 23:57. WCSS smoke job 6308827 submitted (`--gres=gpu:hopper:1,storage:local:150G --time=01:30:00 --export=ALL,STAGE=ae,SMOKE=1`;
  owner CB1; expected run 30-60 min after start). 23:59: PENDING (Priority 682); Slurm start estimates for other pending
  jobs of ours reach 13 Nov 14:00 and 15 Nov 01:00. Risk reported to the lead.
- 23:58. Pre-run review requested from the experiment-reviewer (IDistill plan, scorer, analysis).

- 00:00 (13 Nov). Pre-run review: GO WITH FIXES (F1-F11). Applied before any score is read: F1 (IDistill checkpoint
  selected on the SMDD validation split saved as `.valbest`; `.last` relabelled "stopping epoch set by test-set early
  stopping"), F2 (FRLL-Morphs contributor parser fixed; list v2 `cb1_cnn_images_v2.csv`, sha256 aa140e91..., ids and
  paths identical to v1; 10 FRLL-Morphs morph files name one person twice and are kept), F3 (IDistill morph score
  id1 x id2 in double precision), F4 (checkpoints and logs copied out of TMPDIR every 30 min; `--time` set from the
  smoke step rate), F5 (C1 row-wise and binding in `analyse_cnn.py`), F6-F10 registered. Amendment 1 in `prereg.md`;
  commit 114a40e. IDistill code pack v2 (sha256 ceaa1a9c...) uploaded; the pending smoke 6308827 reads it.
- 00:01. Coordinator: no rental tonight; keep 6308827 queued; prepare the rented variant (done:
  `src/CB1/idistill/rented/`, README_rented.md with cost and wall time, upload.sh and drive.sh with HOST PORT LEASE;
  keep rule built in; the job script takes CB1_L / CB1_PIP=online for it). Fallback wording if IDistill cannot finish by
  the retrain cut-off of 14 Nov 18:00: "IDistill: as reported, not verified; the authors' code selects its checkpoint on
  the FRLL-Morphs test sets".
- 00:04-00:06. FD-MAD fused branch: no landmarks exist for the SMDD morph frames or for any evaluation frame, so five
  facial points are extracted (`src/CB1/landmarks_5pt.py`: insightface buffalo_l SCRFD five points, CPU; det_size 320
  because at 640 the detector found a face in 1 of 40 evaluation frames and 7 of 40 SMDD frames, at 320 in all 80).
  List `/mnt/t7/smad_next/CB1/manifests/fdmad_landmark_paths.txt` (30,639 SMDD training rows of seeds 1-3 + 19,171 CB1
  rows); PID 617534, log `logs/landmarks_5pt.log`, about 27 images/s. Fused wrapper added to `fdmad_cb1.py`
  (`--branch fused`; points scaled to the loader side; training rows without a face left out of the local fit; list rows
  without a face keep the global score; both counted). Landmark detection is not image code (no pixel is written).
- 00:06. WCSS Slurm controller unreachable ("connect failure"); state of 6308827 unknown.

- 00:20-00:31. FD-MAD C1-F (`src/CB1/fdmad_gate.py`): global 256 seeds 1-3 reproduce the stored A45 scores row by row
  (max 1.3e-4 / 0 / 9e-7; 10 of 10 cells). Readings (`/mnt/t7/smad_next/CB1/analysis_fdmad/read_g256/`): inverted on our
  frames (FRLL mean 83.02, MAD22 mean 56.08), as A45 found; `10_ASSET_INVENTORY.md`'s "reproduced on both global-only
  means" is contradicted by `smadcvpr/results/A45/a45_read.md` (GATE FAIL).
- 00:27. First 23 networks (224 px, es.pt) scored. C1: M6, M8, M8O pass every seed; M5 fails the max criterion on seeds
  1, 2, 6 (platform). Amendment 2 registered and committed (9f171b8) before the readings were looked at.
- 00:30. `src/CB1/rs1_bpcer.py`: BPCER at APCER for the released detectors from RS1's score files through RS1's own
  analyse.py; EERs equal RS1's table (e.g. MADation ViT-B/16 AMSL 3.91); `cb1_released_rs1_bpcer.csv`.
- 00:40. Five facial points written for 49,810 frames (`/mnt/t7/smad_next/CB1/manifests/fdmad_landmarks_5pt.npz`, no
  frame without a face). Fused smoke passed; fused runs (256 then 512) via `src/CB1/run_fdmad_fused.sh` (PID 678580).
  A first chain was killed and restarted to put the fast 256 runs first; the FD-MAD global 512 runs take about 1.5 h
  per seed (training features 38 min).

- 01:05-01:41. es.pt pass finished (M2, M1, M4). C1: M1, M2 pass all seeds; M4 seed 3 fails (EER cells 7 of 10;
  saturated probabilities). Readings committed (9cc05b4; tables `tables_es_and_fdmad.md`).
- 01:41. last.pt pass started (38 networks; log `logs/score_cnn_bk_last.log`); the A45 arms follow (PID 610751 waits).
- 01:44. WCSS controller back: Slurm forecasts 15 Nov 01:00 for every pending job of ours incl. smoke 6308827
  (after the retrain cut-off). Coordinator informed; at 01:50 approved IDistill on the DGX GPU after the CNN work.
- 01:50-02:00. DGX variant prepared: extra packages (pandas 2.2.3, tensorboard 2.21, facenet-pytorch 2.5.2; pillow and
  numpy copies removed so the venv's are used) in `/mnt/t7/smad_next/CB1/site_idistill_dgx`; `run_code.py` reads
  CB1_EXTRA_SITE; job script mode CB1_PIP=dgx; local run root `/mnt/t7/smad_next/CB1/dgxrun/` (packs symlinked, hashes
  checked by the script). A first attempt with a `--system-site-packages` venv failed (a venv of a venv does not see
  the parent's packages) and was removed. Amendment 3 committed (1ad2566). Code pack v3 sha256 07794689....

- 02:20-03:35. last.pt pass: 224-px networks and M2, M1 scored; stopped by PID at 03:00 before M4 (descriptive arm,
  secondary checkpoint) to free the GPU; A45 arms scored 03:00-03:35 (code root `code_a45_jobroot`). FD-MAD global 512
  seeds 1-3 and fused 256 / 512 (seeds 1-2) read. C1: M5 last.pt fails on 6 of 8 seeds (withheld), M8O last seed 3
  fails; all A45 pass.
- 03:36-03:38. IDistill DGX smoke (`dgxrun/run_smoke.sh`, SMOKE=1): passed end to end (crop, 2 AE epochs, latents,
  classifier 6 epochs, scoring of best / valbest / last). 03:38: production (`dgxrun/run_prod.sh`, PID 906453): AE stage
  then classifier seed 401. Crops: 24,694 of 25,000 contributors; FRLL FaceMorpher 806 of 1,222 (the known script
  failure), OpenCV 1,212 of 1,221, all others complete. AE step rate 3.0 it/s at batch 32 (GPU 94%): 259 s per epoch,
  300 epochs about 21.5 h (end about 01:20 on 14 Nov); classifier estimated 2.5-7 h. Coordinator told at 03:50.
- 03:55. Readings committed (b554c85): `result.md`, `tables_all.md`, `cnn_{es,last,a45}_*.csv/json`, FD-MAD files.

- 03:55-04:30. Results review ("needs qualification"; F1-F8, H-new-1..3) applied: `src/CB1/review_addons.py` ->
  `review_addons/{a12style_vs_cb1.csv,all_seed_readings.csv,auc_native.csv,c2_summary.json}`; result.md rewritten
  (A12-style vs registered EER table; MixFaceNet release vs retrain decomposition; FD-MAD relabelled; paper labels without
  "our retrain does not reproduce"); amendment 4 (IDistill gate on written crops, worst case beside; FD-MAD wording;
  C1 deviation stated). OrthoMAD paper fetched (`/mnt/t7/smad_next/CB1/literature/orthomad.{pdf,txt}`): FRLL-AMSL EER
  14.80; the manuscript's 9.50 is a transcription error (OrthoMAD WebMorph BPCER@APCER20).
- 04:30. `src/CB1/analyse_idistill.py` written and tested on the smoke tar (runs end to end).

## 3. Data

See `prereg.md` section 2. Corrected MAD22 aligned frames and E7 pools:
`/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/{native,e7}`. FRLL-Morphs: eval.csv rows (old
aligner). Gate rows: old MAD22 subset rows of eval.csv. SMDD (IDistill, FD-MAD training):
`/mnt/t7/Datasety/downloads/SMDD/SMDD_release_train/{os25k_bf_t (25,000), m15k_t (15,000)}` and
`/mnt/t7/Datasety/downloads/SMDD/os25k_m_t` (25,000 contributor images; all 3,853 first and 5 second contributors of
the m15k_t file names are present).

## 4. Code

- `src/CB1/build_manifest.py`: the image list (file reads only).
- `src/CB1/score_cnn.py`: scoring of A12-BR / A45 networks with the pinned code root
  `/home/narolski/mambamorph-code-a36/smadcvpr` (git c5fc0c3; common.py b5d42a99, archs_a12.py bedfeb86).
  Command: `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n 10
  /home/narolski/mambamorph-code/.venv-spark/bin/python -I score_cnn.py --code /home/narolski/mambamorph-code-a36/smadcvpr
  --nets /mnt/t7/smad_next/CB1/manifests/cb1_nets_bk.tsv --images /mnt/t7/smad_next/CB1/manifests/cb1_cnn_images.csv
  --out /mnt/t7/smad_next/CB1/scores_cnn --workers 2`.

## 5. Results

Readings as they arrive are in `result.md`. Tables: `/mnt/t7/smad_next/CB1/analysis_cnn/<pass>/{per_network,per_arm,
c1_gate,c2_pipeline_shift}.csv`, `readings.json`, `c1_verdicts.json`; FD-MAD `/mnt/t7/smad_next/CB1/analysis_fdmad/`.

## 6. Checks

Registered: C1 scorer gate against stored A12-BR / A45 numbers, C2 pipeline shift on the 204 FRLL photos, C3 no old
subset row in results. Done so far: strict load of all architectures; checkpoint hashes.

## 7. Dead ends and failures

- The cancelled canonical164 plan (`/mnt/t7/smad_heldout/mad22_canonical164_production_v1/`): 164 plan JSONs (A36
  primaries M1-M8O 51, A49 P0-P3 40, A50 66, 7 releases) for 4,687 corrected native + 1,020 E7 frames, built to replay
  the historical GPU batch composition ("HISTORICAL_BATCH_CONTEXT_V1"), one H100 for 50,400 s; the 2.4 GB
  `production_pack.tar` holds only code, ledger and plans (weights and images were staged separately on WCSS). WCSS
  job 6298965 was CANCELLED by account61921 after 0 s (CONCLUSIONS.md l.493); the reason is not recorded. CB1 does not
  reuse that machinery: a plain scorer with the pinned model code and loader is used instead, and checked row by row
  against the stored scores (C1).

## 8. Observations and ideas

- IDistill's code selects its checkpoint by the mean EER on the five FRLL-Morphs test sets every 5 epochs
  (`train.py: run_extra_test`); its published FRLL numbers are therefore test-selected.
- The A12-BR "published recipe" arms are re-implementations in our pipeline (our 512 frames of SMDD, blur / resampling
  / JPEG augmentations removed, early stopping on VALX-A*), not the authors' pipelines (A12-BR README).

## 9. Open items and next steps

Copy A45 weights and stored scores from WCSS; run C1/C2; read; IDistill smoke and WCSS jobs; FD-MAD re-score.

## 10. Handover state

- DGX GPU: IDistill production, `/mnt/t7/smad_next/CB1/dgxrun/run_prod.sh` (PID 906453), logs
  `dgxrun/prod_STAGE_ae.log`, `dgxrun/prod_STAGE_cls_SEED_401.log`, live training log in
  `dgxrun/tmp_STAGE_ae/ids/out/ae_train.log`; checkpoints copied every 30 min to `dgxrun/results/CB1/idistill_ae_partial/`;
  result tars to `dgxrun/results/CB1/`. Expected end 14 Nov 04:00-08:30. If it dies during the AE: the authors' `--resume`
  from the copied `*_best.pt` (needs a resume patch of the job script; not prepared).
- DGX CPU: FD-MAD fused 512 seed 3 (`src/CB1/run_fdmad_fused.sh`, PID 678580).
- WCSS 6308827 (IDistill smoke, owner CB1, code pack v2): pending, Slurm forecast 15 Nov 01:00; kept queued on the
  coordinator's instruction (carries its whole workload; runs about 30-60 min if it starts).
- Not scored: M4 last.pt (descriptive). CNN scoring is complete otherwise.
- When IDistill finishes (`dgxrun/prod_STAGE_cls_SEED_401.log` ends with "EXIT 0"): read with
  `OMP_NUM_THREADS=2 nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/CB1/analyse_idistill.py
  /mnt/t7/smad_next/CB1/dgxrun/results/CB1/idistill_cls_s401.tar /mnt/t7/smad_next/CB1/analysis_idistill` -> gate JSON
  (binding: test-selected checkpoint, FRLL native, written crops, mean within 1.5 of 2.90) and readings CSV (three
  checkpoints, both benchmarks, native / aligned-native / E7 pools, BPCER at APCER, worst case for uncropped morphs).
  Copy `idistill_cls_s401.tar` and `idistill_ae.tar` hashes into this folder; the weights are inside those tars (keep).
  Unresolved review items for later: SelfMAD release on the corrected MAD22 (RS1 machinery, about 0.5 GPU-h after
  IDistill); H-new-1 (retrain logits vs frame high-frequency energy; needs the author's view on spectral statistics);
  H-new-2 (FD-MAD feature distances by resolution); H-new-3 (probability ties in A12 ledger EERs).

## 11. Reproduce from scratch

The commands in section 4, in order.
