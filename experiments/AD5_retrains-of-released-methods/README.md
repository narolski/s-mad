# Retrains of released methods with the authors' code (AD5): full record

Owner: AD5 hypothesis owner (agent). Code `/home/narolski/smad-next/src/AD5/`. Large outputs `/mnt/t7/smad_next/AD5/`.
Registration: `prereg.md` (this folder). Verdict file: `result.md` (this folder, when results exist).

## 1. Question and current answer

Every audit statement about a published morphing attack detector (MAD) currently rests on one released checkpoint per
method. Question: if each method is retrained with its authors' own code and training set (SMDD, the synthetic
morphing development set), seeds 401 to 405, last checkpoint, do the retrains behave like the released checkpoint on
the readings the own-crop re-score of the audit rows (RS1) takes (history-matched genuine photos, flag rates under
benign processing, the smiling half of the FRLL genuine class, the MorDIFF control images)?

Status 11 Nov 2026, 22:40 CET: registration with amendments 1-3 in `prereg.md`. All smoke jobs passed (SMDD crop,
MADation ViT-L/14 and ViT-B/16 DDP, MixFaceNet-MAD, SelfMAD, scoring). Production arrays submitted and pending
(Athena has 12 usable nodes tonight): MADation ViT-L/14 3545813, ViT-B/16 3545814 (8 GPUs per seed), MixFaceNet-MAD
3545870, SelfMAD 3545933 + 3545936 (1 GPU per seed; about 30 h each). The SelfMAD release has been scored through
the AD5 path on the DGX (not read). No retrain and no retrain score exist yet.

## 2. Timeline

- 11 Nov 17:00-17:40 CET. Read OWNER_BRIEF.md, ATHENA.md, ideas/CONSOLIDATED_v2.md, the review of AD1/AG5/C,
  10_ASSET_INVENTORY.md section A, the own-crop re-score (RS1) pre-registration and amendment 1, C_cue_checks/result.md.
- 11 Nov 17:10. Inventory of the authors' code (section 4). Found the MADation release training logs (authors' own
  `training.log` files from their Google Drive release) in a volatile scratchpad and copied them to
  `/mnt/t7/smad_next/AD5/release_logs/` (hashes in `TRAINING_LOG_SHA256SUMS`; they match the hashes recorded in the
  A36 conversion `convert.json`). Copied the SMDD repository mirror (commit 9683229, contains the MixFaceNet-MAD
  training script `main.py`) from the scratchpad to `/mnt/t7/smad_next/AD5/thirdparty/smdd_repo_9683229/`.
- 11 Nov 17:25. `git ls-remote` of the three upstream repositories: MADation HEAD = 0542cf86 (= local mirror), SMDD
  HEAD = 9683229c (= mirror), SelfMAD HEAD = 09ed0819 (local mirror 673d0640; the two newer commits change only
  LICENSE and README). Cloned SelfMAD 09ed081 into its own empty directory
  `/mnt/t7/smad_next/AD5/thirdparty/selfmad_09ed081/repo`.
- 11 Nov 17:30. Lead: Athena refuses both accounts; do not submit or probe; job files use account
  `plgrestorearc-gpu-a100`. Documentation standard (DOCUMENTATION.md) adopted; this README started.
- 11 Nov 17:31. One ssh command to Athena (lock held): project folder exists (13 GB used, 2.0 TB free on /net/pr2);
  only module `Python/3.10.4`; CUDA modules 10.0 to 12.0. No job of ours has ever run there, so compute-node internet
  access is unknown: every package travels as a local wheel house, every model file in the code pack.
- 11 Nov 17:32-17:50. Wheel houses (x86_64, cp310) downloaded on the DGX with `pip download --platform ...` into
  `/mnt/t7/smad_next/AD5/wheels/{madation,selfmad}` from `src/AD5/env/{madation,selfmad}_requirements.txt`; three
  packages exist only as sdists (easydict 1.10, openai-clip 1.0.1, efficientnet-pytorch 0.7.1; in `*_sdist/`, read:
  plain setuptools setup.py files). Offline resolution check (`pip download --no-index --find-links`) passes for both.
- 11 Nov 17:45. CLIP initialisation check (`src/AD5/checks/clip_init_equivalence.py`): building CLIP from the HF
  OpenAI-format file and casting as the authors do gives tensors identical to the authors' frozen-encoder release
  checkpoint (ViT-B/16 302 of 302 tensors, ViT-L/14 446 of 446, max abs difference 0). Hence patch 2 (no TorchScript
  download). Outputs `/mnt/t7/smad_next/AD5/checks/clip_init_equivalence_{vitb16,vitl14}.json`.
- 11 Nov 17:45-18:00. Patched copies made from `git archive <commit>` in `/mnt/t7/smad_next/AD5/build/{madation,smdd,
  selfmad}_src` (pristine copies `*_orig`); diffs saved as `src/AD5/{madation,mixfacenet,selfmad}_ad5.patch`.
- 11 Nov 17:51. 8-image check, SMDD crop: the unchanged `image_preprocess.py` on 4 genuine + 4 morph SMDD images
  (DGX GPU, facenet-pytorch 2.5.2): 8 of 8 crops written (148-164 x 189-212 px). `checks/crop8/`.
- 11 Nov 18:00. 8-image check, SelfMAD landmarks: unchanged `preprocessing/dlib_lm.py` on 8 renders: 8 files of
  shape (1, 81, 2) int64, as the authors' loader comment says for SMDD. `checks/selfmad8/`.
- 11 Nov 18:03. Started the full landmark build (`src/AD5/selfmad_landmarks.sh`, 4 shards, nice 10), log
  `/mnt/t7/smad_next/AD5/data/selfmad_landmarks.log`; about 2 images/s per shard on the loaded DGX (load average 93).
- 11 Nov 18:01-18:11. 8-image check, MADation ViT-B/16 (world size 1, batch 4): first run failed (openai-clip needs
  `pkg_resources.packaging`; fixed by setuptools 69.5.1), second ran 2 epochs but saved nothing (the authors' saver
  needs epoch index > 1; run with 3 epochs), third failed with CUDA out of memory at start (shared GPU); retry loop
  `src/AD5/checks/dgx_madation8.sh` running. 8-image check, MixFaceNet-MAD (patched main.py, 2 epochs, batch 4):
  passed; the saved state dict has the same 415 keys and shapes as the release file.
- 11 Nov 18:10. `prereg.md` written.
- 11 Nov 18:15. Job scripts written (`src/AD5/athena/`), pack builder started (`src/AD5/build_packs.sh`, log
  `/mnt/t7/smad_next/AD5/build_packs.log`).
- 11 Nov 18:13 / 18:18. 8-image MADation checks passed on the DGX (`checks/dgx_madation8.sh B` and `L`): epoch-3
  checkpoints written (`checks/madation8/out_{B,L}/...`). The ViT-B/16 checkpoint converts with the release converter
  (`a36_madation.py convert`, 155 tensors as the release, CPU equivalence logit max abs 8.5e-8;
  `checks/madation8/convert_B/`).
- 11 Nov 18:20. Landmark build finished: 24,982 of 25,000 renders have landmarks; 18 without a face
  (`data/selfmad/no_face.txt`; the authors' loader skips them). Packed as `packs/selfmad_landmarks.tar`
  (sha256 a43776b6...).
- 11 Nov 18:18-18:24. Upload 1 to Athena (`rsync` under the lock): code/, wheels_madation.tar (90dceaf3...),
  wheels_selfmad.tar (8565c291...), smdd_train_raw.tar (269b7262...): 12.8 GB in 6 min (35 MB/s).
- 11 Nov 18:25. Scoring wrapper `src/AD5/score/ad5_score_athena.py` (registers a retrain as a copy of its release's
  spec, then RS1's byte-identical score.py). Check on the DGX (`checks/dgx_wrapper_check.sh`): the release scored
  through the wrapper and through RS1's `rs1_score.py` on 8 A46 crops: score, score_noTTA, logit_noTTA and features
  identical (max abs difference 0). First wrapper version imported the A46 tree's own `score.py` (sys.path order):
  fixed by importing RS1's score.py first and asserting its path.
- 11 Nov 18:25. Lead: Athena accepts jobs (account `plgrestorearc-gpu-a100`).
- 11 Nov 18:27. Upload 2: code/ (rebuilt) and `selfmad_landmarks.tar`; 18:29 upload of `wheels_score.tar`
  (70a966d4...). Submitted smoke A = job **3544190** (1 GPU) and smoke B = job **3544192** (2 GPUs, after A).
- 11 Nov 18:29-18:33. Job 3544190 on t0016 (A100-SXM4-40GB, driver 595.91.07): the MADation environment
  `envs/AD5/madation` built from the wheels in about 3 min (pip freeze in the job log; `AD5_ENV_OK` written), then the
  job FAILED at 3:53 while extracting the SMDD pack: "No space left on device" (`-C localfs` gives only 4.0 GB, see
  ATHENA.md). Cost 0.065 GPU-hours. Job 3544192 never started (dependency) and was cancelled (scancel).
- 11 Nov 18:34. 8-image check, SelfMAD training (`checks/dgx_selfmad8.sh`): the patched `train__.py -v last` ran
  1 epoch (2 steps) on the 8 renders after face labels were made by the unchanged `face_labels.py` (it does not create
  its output directory; the job script now does); `epoch_1.tar` has keys epoch / model / optimizer and its model
  state dict has the release's 1,956 keys and shapes.
- 11 Nov 18:36. Lead's two Athena facts recorded: (1) work in the RAM disk `$MEMFS` (`-C memfs`, counts toward
  `--mem`, at most 120G per GPU); every AD5 job file now uses it (`ad5_common.sh` sets SCRATCH_LOCAL=$MEMFS);
  (2) two locks: `/tmp/smadnext-athena-cmd.lock` (`-w 300`) for short commands, `/tmp/smadnext-athena.lock`
  (`-w 1800`) for transfers; a flock timeout returns 1 silently (seen once at 18:32: an empty ssh result, rc 1).
  Smoke A resubmitted after the fix (job number below).
- 11 Nov 18:41-18:47. Script sync waited about 6 min for the transfer lock (other owners' uploads). Submitted smoke A =
  job **3544216**, smoke B = job **3544217** (`--dependency=afterok:3544216`), SelfMAD smoke = job **3544218**.
  3544216 started 18:49.
- 11 Nov 18:48-19:00. Smoke A (job 3544216, t0015, A100-SXM4-40GB; 12:13 elapsed = 0.20 GPU-hours) PASSED: env
  reused (torch 2.0.1+cu117, cuDNN 8500, cv2 4.5.5); the unchanged SMDD crop script on cuda:0 took 623 s for 40,000
  images (peak GPU memory 675 MiB); **39,723 of 40,000 images kept** (24,729 genuine, 14,994 morphs; 277 lost: 271
  genuine and 6 morphs, "Images with no Face" in the authors' wording, which also counts empty slices); the MADation
  release log reports 39,730 training images (difference 7, 0.02%). Crop pack `packs/AD5/smdd_train_cropped.tar`
  (2.38 GB, sha256 3189e52a...), report `results/AD5/crop_report.json` (lost list).
- 11 Nov 19:01-19:07. Smoke B (job 3544217, t0013, 2 x A100-SXM4-40GB; about 6 min = 0.2 GPU-hours) PASSED. The
  patched MADation code under `torch.distributed.launch` with 2 processes, authors' flags, batch 32 per GPU, on every
  12th image (3,311) for 3 epochs (155 steps), checkpoint `3_backbone.pth` written:
  ViT-L/14 73.9 samples/s on 2 GPUs (37 per GPU, 0.87 s per step), peak 16,529 MiB, GPU utilisation 100%;
  ViT-B/16 318 samples/s on 2 GPUs (159 per GPU), peak 5,863 MiB. MixFaceNet-MAD (patched main.py, 1 epoch of the
  subset, 207 steps of 16): 10.6 it/s, peak 5,485 MiB. For comparison, the authors' logs show 860 (ViT-L/14) and
  2,340 (ViT-B/16) samples/s on 8 GPUs of unknown type, i.e. 107 and 292 per GPU.
  Estimates (39,723 images, 40 epochs, 8 GPUs at the measured per-GPU speed, plus about 5 min start):
  L 1.5 h wall = about 12.5 GPU-h per seed; B 21 min wall = about 3.2 GPU-h per seed; X (1 GPU, 2,483 steps x 100
  epochs at 10.6 it/s) 6.5 h = 6.5 GPU-h per seed. Five seeds each: L 62, B 16, X 33 GPU-hours.
- 11 Nov 19:08. Timing sent to the lead. Production submitted (`ad5_madation_train.sbatch`, `ad5_mixfacenet_train.sbatch`):
  **3545813** = MADation L, `ARM=L`, `--time=02:45:00`, array 401-405, 8 GPUs per task;
  **3545814** = MADation B, `ARM=B`, `--time=01:00:00`, array 401-405, 8 GPUs per task;
  **3545815** = MixFaceNet-MAD X, `--time=09:00:00`, array 401-405, 1 GPU per task. Lead told.
- 11 Nov 19:20. Independent pre-run review (`experiments/reviews/PRERUN_AD5_20261111.md`): GO WITH FIXES; MADation
  arrays stay; MixFaceNet-MAD array to be cancelled and resubmitted with per-epoch weights; SelfMAD held until weights
  every 5 epochs, a training-set size assertion and a time limit from the smoke; changed code only in new folders;
  analysis amendments before any score (gate as per-seed per-cell label, all-five headline, second window around the
  release through our path, primary cells by rule, JPEG 50 and 0.5-rule readings, loss overlay, scoring job updated to
  RS1 amendments). Budget for AD5 raised by the lead to 250 GPU-hours (per experiment).
- 11 Nov 19:24. Cancelled MixFaceNet-MAD array 3545815 (task 401 had run 11:38 = 0.19 GPU-hours; 402-405 never ran).
- 11 Nov 19:25-19:32. Patch v2 (`src/AD5/mixfacenet_ad5.patch`, `selfmad_ad5.patch`): MixFaceNet-MAD saves the state
  dict after every epoch to `AD5_EPOCH_DIR` (job: `results/AD5/mixfacenet_X_s<seed>_epochs/`, persistent, about 11 MB
  each); SelfMAD saves `{"model", "epoch"}` every 5 epochs to `AD5_EPOCH_DIR` and asserts `len(train_dataset) ==
  AD5_EXPECT_N` (24,982 in production). `torch.save` draws no random numbers. Epoch 100 stays the registered reading;
  other epochs are descriptive. DGX 8-image checks: MixFaceNet-MAD 2 epochs -> `epoch_001.pth`, `epoch_002.pth`,
  epoch_002 equal tensor by tensor to the final file (`checks/mixfacenet8v2/`); SelfMAD v2 check (`checks/selfmad8/
  epochs_v2`, assertion with a wrong count) running.
  Job files: every AD5 job now sources `packs/AD5/code_v2/` (or `code_v3/` for SelfMAD), `PYTHONDONTWRITEBYTECODE=1`,
  `keep_log` copies the training log of a failed run to `logs/AD5_keep/<job>_<task>/`; the MADation job file no longer
  exits before printing the log tail when `training.log` is missing (only for reruns: the pending arrays 3545813/14
  use the batch script stored at submission).
- 11 Nov 19:30. Frozen code trees on Athena (never modified while tasks read them):
  `packs/AD5/code/` = what smoke A/B and the MADation arrays 3545813/3545814 read. Its hash list (local mirror,
  103 files) is `/mnt/t7/smad_next/AD5/packs/code_tree_SHA256SUMS_20261111T1930.txt` (sha256 0fce8cb9...); an
  `rsync -n -c` comparison with the Athena tree shows no content difference; Athena additionally holds `__pycache__`
  files written by the smoke jobs and `hf_cache/version.txt` (`packs/code_tree_athena_compare_20261111T1930.txt`).
  Why the reviewer saw a mismatch: `packs/code/CODE_SHA256SUMS` was written by `build_packs.sh` at 18:27; afterwards
  the job files were edited (memfs switch 18:36, score job 19:14) and only `src/AD5/` was re-synced into `packs/code/`
  (locally and to Athena, 18:41 and 19:15) without regenerating that list, so the list was stale for 10 files under
  `src/AD5/`; the batch script of the MADation arrays was stored by Slurm at submission (19:08) from the 18:41 version.
  `packs/AD5/code_v2/` (CODE_SHA256SUMS sha256 9b51b7f6...; uploaded with `--link-dest=code`, checksum comparison
  clean) = patch v2 + job files v2; read by MixFaceNet-MAD array 3545870. `packs/AD5/code_v3/` (CODE_SHA256SUMS
  3edea017...) = code_v2 + SelfMAD job files pointing to code_v3 + `efficientnet-pytorch==0.7.1` in
  `selfmad_requirements.txt`; read by SelfMAD jobs.
- 11 Nov 19:33. Resubmitted MixFaceNet-MAD from code_v2: **3545870** (array 401-405, 1 GPU, `--time=12:00:00`).
- 11 Nov 19:29. SelfMAD smoke 3544218 FAILED after 35:28 (0.59 GPU-hours): face labels done (25,000 files in
  1,641 s; `packs/AD5/selfmad_labels.tar.gz`, 199,736,221 bytes, sha256 22dc283d...), then `train__.py` failed with
  `No module named 'efficientnet_pytorch'`: the rewritten `selfmad_requirements.txt` (17:55) had dropped the sdist
  line (the DGX check passed because the DGX environment has the package). Fixed in code_v3; the smoke rebuilds the
  environment once and skips the labels (tar exists). Resubmitted: **3545882**.
- 11 Nov 19:45-20:05. Before any retrain score: prereg amendment 1 (gate as per-seed per-cell labels with the
  all-five-seeds headline and two secondary lines, a second window around the release's own number; primary cells by
  a fixed rule; JPEG-50, 50%-resample and 0.5-rule readings with miss rates; loss fidelity check; checkpoints kept;
  scoring on RS1 crop files by hash) and amendment 2 (the author-approved, labelled SelfMAD oracle-epoch row; crop
  storage ruling). `ad5_analyse.py` rewritten to amendment 1; `ad5_loss.py` written and run on the authors' logs only
  (complete runs: ViT-B/16 3, last-epoch mean losses 0.0037 / 0.0041 / 0.0039; ViT-L/14 2, 0.0067 / 0.0028; the
  amendment text was corrected: the ViT-L/14 log's run 2 stops at epoch 35). Scoring job rewritten (v2) to reuse RS1's
  result tar (crops/v1 + crops/v2 + crops_sha256.txt), score both crop variants, verify the crop hashes; it will live
  in `packs/AD5/code_v4/`; `facenet-pytorch==2.6.0` added to `score_requirements.txt` (offline resolution passes).
- 11 Nov 19:41 (lead). Athena has 12 working nodes tonight; the 8-GPU tasks may wait; do not reshape them.
- 11 Nov 19:48 (lead, author's approval). Waiting jobs moved in place to account `plgmultivision-gpu-a100` (more
  scheduling priority tonight): MADation 3545813, 3545814 and MixFaceNet-MAD 3545870. Every new AD5 job is submitted
  with `-A plgmultivision-gpu-a100` on the sbatch command line (the job files still say plgrestorearc). Accounts per job:
  3544190, 3544192, 3544216, 3544217, 3544218, 3545815, 3545882: plgrestorearc-gpu-a100; 3545813, 3545814, 3545870:
  submitted under plgrestorearc, moved to plgmultivision before starting.
- 11 Nov 19:38. DGX scoring of the SelfMAD release (one run over 23,145 images) was killed by the DGX ("Killed",
  BrokenPipe in the dlib workers; memory pressure from other jobs). `score/run_selfmad_dgx.sh` rewritten to score in
  parts of 2,500 images (`/mnt/t7/smad_next/AD5/scores_selfmad/parts/`), each retried up to 6 times, then merged;
  restarted 20:02 (4 dlib workers, nice 10), log `/mnt/t7/smad_next/AD5/scores_selfmad_release.log`. No score opened.
- 11 Nov 20:03. SelfMAD smoke 3545882: the environment rebuild on the project file system is slow (torch and CUDA
  wheels installed between 19:39 and 20:01).
- 11 Nov 19:38-20:12. SelfMAD smoke 3545882 (t0013, account plgrestorearc; 34:03 = 0.57 GPU-hours) PASSED:
  environment rebuilt with efficientnet-pytorch (about 23 min on the project file system), labels reused, 1 epoch of
  the 1,600-render subset (99 steps of 16 + 16): about 1.45 it/s (0.69 s per step), GPU utilisation 92-100% in 12 of
  16 samples (GPU-bound, so more loader workers would not help), peak 14,957 MiB; `epoch_1.tar` has the authors'
  keys and the release's 1,956 tensors. Estimate: 24,982 / 16 = 1,561 steps per epoch, 100 epochs = about 30 h =
  30 GPU-hours per seed.
- 11 Nov 20:14. Submitted SelfMAD array **3545933** (code_v3 `ad5_selfmad_train.sbatch`, `-A plgmultivision-gpu-a100`,
  `--time=46:00:00`, `--array=401-404`): four seeds keep the total within the 250 GPU-hour budget (L 64 + B 17 + X 34
  + S 120 + spent about 2 + scoring about 5 = about 242). Seed 405 (about 30 GPU-hours more) asked of the lead.
- 11 Nov 20:17 (lead). Seed 405 approved, allowance 300 A100-hours, exclude node t0010, end of stage 14 Nov (a seed
  not at epoch 100 by 14 Nov 18:00 is "incomplete"). 20:19: submitted **3545936** (SelfMAD seed 405, code_v3,
  `-A plgmultivision-gpu-a100 --time=46:00:00 --exclude=t0010`); `scontrol update JobId=3545933 ExcNodeList=t0010`
  for the pending seeds 401-404 (checked: ExcNodeList=t0010). Prereg amendment 3 registered (20:20).
- 11 Nov 20:25-20:35. `packs/AD5/code_v4/` (CODE_SHA256SUMS sha256 db6077a5...; = code_v3 + scoring job v2,
  `score_requirements.txt` with facenet-pytorch, analysis scripts); uploaded with `--link-dest=code_v3`, checksum
  comparison clean. Scoring smoke **3545948** (`ad5_score_rel.sbatch`, `-A plgmultivision-gpu-a100 --time=01:00:00`,
  RS1's smoke result tar `rs1a_smoke_3545869.tar`, releases ViT-B/16, ViT-L/14, MixFaceNet-MAD only, 8 images per
  set): tests the scoring environment, the crop-hash check and the wrapper on Athena while training waits.
  DGX SelfMAD release scoring in parts: 4 of 10 parts done by 20:25 (about 5 min per part).
- 11 Nov 20:45. SelfMAD oracle-epoch tool `src/AD5/score/selfmad_oracle.py` (amendment 2): `cache` computes the
  SelfMAD own preprocessing (rsx_selfmad_own._prep, unchanged) once for the 7,265 FRLL-cell images and stores the exact
  uint8 arrays (`/mnt/t7/smad_next/AD5/oracle_cache/x_u8.npy`, started 20:44, 3 dlib workers, log `cache.log`);
  `score` scores one saved epoch on the cache with score.py's network builder (the per-epoch `{"model", "epoch"}` files
  load directly through a12_released's state_keys); `pick` takes the lowest mean FRLL-Morphs EER. Registered check
  before use: cached path equals `score.py --mode own` on the same images for one network.
- 11 Nov 20:40. `src/AD5/fetch_results.sh [PATTERN]`: copy-back of result tars under the transfer lock with sha256
  checks into `/mnt/t7/smad_next/AD5/results/`.
- 11 Nov 20:27. Scoring smoke 3545948 FAILED after 47 s (0.01 GPU-h): `build_env` insisted on setuptools / wheel,
  which the scoring wheel house does not hold (it needs no sdist). `ad5_common.sh` now only tries that step; code_v4
  updated in place (no task reads it; CODE_SHA256SUMS sha256 dc11b680...); resubmitted as **3545960**.
- 11 Nov 20:40-21:05. Disk: /mnt/t7 reached 100% at about 20:40 (lead; new rule in OWNER_BRIEF.md: keep 50 GB
  free, check `df` before writes over 1 GB, per-epoch weights and packs stay on Athena, only scores and small tables
  come back). My oracle cache (3.2 GB, written 20:44) completed. I removed my own 8-image check checkpoints (2.9 GB;
  hashes in `checks/large_check_files_deleted_20261111T2100.sha256`); T7 57 GB free at 21:00. Sent the lead a list
  of deletion candidates (pack tars and wheel folders with verified Athena copies; packs/code); kept release_raw/
  (the only non-volatile copy of the authors' raw MADation files) and oracle_cache/.
- 11 Nov 20:55. SelfMAD release scored through the AD5 path on the DGX: 23,145 images in 10 parts, merged
  (`/mnt/t7/smad_next/AD5/scores_selfmad/scores_own_selfmad_hrnet_w18__ad5.npz`; no number read). Oracle-cache check:
  the release scored on the cache vs score.py --mode own on the same 7,265 FRLL images: max |logit difference|
  8.9e-4, mean 5e-7, 11 images above 1e-4, crop flags equal (`oracle_scores/check_cached_vs_scorepy.json`); the cache
  has 0 images without a face. Because per-epoch weights stay on Athena, the oracle `score` step will run there (the
  cache, 3.2 GB, to be uploaded).
- 11 Nov 20:31-21:05. Scoring smoke 3545960 (t0015): environment built on the project file system (about 20 min),
  RS1 smoke crops verified by hash (927 files), lists of 303 / 304 crops; but the first scoring call (ViT-B/16 release,
  303 crops) took 750 s, so the job could not finish in its hour; cancelled at 34:40 (0.58 GPU-hours). Probable cause:
  Python importing thousands of files from the shared file system (slow tonight; the same environment build took
  20 min). Fix: short jobs build their environment in the RAM disk from the local wheels (`build_env_local`); the
  score job prints per-call times and the scorer's own img/s line, and keeps its logs on SIGTERM. code_v4 updated in
  place (no task reads it; CODE_SHA256SUMS b6fd552d...). Resubmitted as **3546004**.
- 11 Nov 21:15-21:30. Uploaded for the oracle diagnostic: `packs/AD5/selfmad_oracle_cache.tar` (sha256 f12bc071...,
  3.2 GB; `rsync -n -c` shows no difference) and `packs/AD5/selfmad_release.safetensors` (0ad8db6f...); local tar
  copies deleted (no second local copies; the cache stays in `oracle_cache/`, the release file in AR1's folder). The
  local tar was written with 60 GB free (rule: at least 50 GB). Scripts: `score/selfmad_oracle_athena.py` and
  `athena/ad5_selfmad_oracle.sbatch` (to be placed in a code_v5 tree when the SelfMAD epochs exist).
- 11 Nov 21:20. Queue: MADation tasks have the highest priority of the pending sprint jobs (6396) but wait for free
  nodes (23 nodes failed, 13 reserved, 11 mixed, 1 allocated); MixFaceNet-MAD and SelfMAD wait for nodes too.
- 11 Nov 21:24-21:26. Scoring smoke 3546004 (t0010; 2:15 = 0.04 GPU-hours) PASSED: environment built in the RAM
  disk in 52 s; RS1 smoke crops verified (927 files); releases ViT-B/16, ViT-L/14, MixFaceNet-MAD scored on both crop
  variants (303 / 304 crops) in 4-15 s per call (24-109 img/s); result `results/AD5/scores_smoke_rel8b.tar`
  (0d22533b...; smoke only, not used). The 750 s of 3545960 were therefore start-up from the shared file system.
  Note: the pending production tasks import from shared environments (envs/AD5/madation, envs/AD5/selfmad); their
  start-up may cost minutes on a slow evening; they are not changed (MADation arrays frozen by the lead's ruling).
- 11 Nov 21:58. Persistent job poller `src/AD5/athena/poll_jobs.sh` (command lock, every 170 s) writes state changes to
  `/mnt/t7/smad_next/AD5/state/jobs.log` (PID in `state/poller.pid`). 22:40: all AD5 production tasks still pending
  ("ReqNodeNotAvail": 23 nodes failed, 13 reserved, 12 partly used; 8-GPU tasks need a whole node).
- 12 Nov 00:15. Athena: all 12 usable nodes fully allocated (95 of 96 GPUs in use; 13 nodes reserved and idle, 23
  failed). AD5 tasks wait at the top of our pending list ("ReqNodeNotAvail" = waiting for resources). 00:50: still
  pending; nothing resubmitted or reshaped (lead's instruction).
- 12 Nov 02:35-02:45. Athena: 5 GPUs free (t0014: 2, t0018: 3) but no AD5 task starts. `scontrol show job` for
  3545813 / 3545870 / 3545933: Reason=ReqNodeNotAvail, UnavailableNodes t[0001-0031,0034-0036,0038-0047] (every
  usable node). `sbatch --test-only` (no job created): a 1-GPU, 8-CPU, 32G, memfs job with limit 1 h, 6 h, 12 h or
  46 h "to start at 2026-12-20T23:47" on t0018 (plgmultivision; 2026-12-22T05:32 with plgrestorearc, memfs or
  localfs; the same without a constraint); an 8-GPU job 2026-12-21T06:46 on t0014. Looks like a cluster-wide
  reservation or maintenance not visible to users (`scontrol show res`: none). Lead told at 02:40; nothing changed.
- 12 Nov 02:50 (lead). Fair share exhausted (0.045 / 0.020), only 12 of 48 nodes work, Slurm forecasts 20-22 Dec for
  new jobs: jobs stay queued (no resubmission, no account change, no cancel); poll at most hourly (poller now 3600 s);
  rented machines are the author's decision. Zero-GPU work meanwhile:
  - `ad5_analyse.py`: variant-1 rows of MorDIFF, the A43 arms and FRLL FaceMorpher are excluded (RS1 README: the
    authors' crop script fails there; variant 2 is used), set `V1_INVALID`.
  - Dry run on the DGX (`checks/dgx_score_dryrun.sh`): RS1 smoke crops 3545869 (463 / 464 crops, both variants),
    wrapper scoring of a stand-in retrain (the MixFaceNet-MAD 8-image check network as `mixfacenet_X_s401`) and two
    releases, then `ad5_analyse.py --B 50`: ran end to end (60 gate rows, 321 reading rows, 214 verdict rows);
    analysis outputs deleted unread.
  - Loss overlay `ad5_loss.py` ready (tested on the authors' logs).
  - Cost table sent to the lead (section 9).
- 12 Nov 23:00 (lead). WCSS reachable again; the author asked the lead to execute without waiting. Retrains move
  to WCSS (H100) in the order ViT-B/16, MixFaceNet-MAD, ViT-L/14, SelfMAD if GPUs remain; at most 6 sprint GPUs at
  once; no placeholder jobs (OWNER_BRIEF 92799d8). Athena tasks stay queued until a WCSS copy is verified.
- 12 Nov 23:05. WCSS probe (one connection under `/tmp/opencode/wcss-client.lock`): login works; system Python 3.9.25;
  partitions lem-gpu-short (3 days) and lem-gpu-normal (7 days); our queue holds only the held array 6294928_[4-14].
  The login banner says the home directory was archived (old home in `/lustre/archived-users/narolski/`); Lustre
  project folder used instead: `/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/{packs,results,logs}`.
- 12 Nov 23:10-23:30. Prereg amendment 4 (WCSS, H100, Python 3.9, global batch 256 on 1 GPU (B) or 2 x 128 (L)).
  Job script `src/AD5/wcss/ad5w_train.sbatch` (one seed per array task; code, cp39 wheels and the crop pack untarred
  in $TMPDIR; venv built there; one result tar back; `--extra=FORCE_RM_TMPDIR`; logs of failed runs to
  `logs/keep/<task>/`). Packs: `/mnt/t7/smad_next/AD5/wcss/ad5w_code.tar` (sha256 d263083c...; = the local code_v2
  tree with current `src/AD5`, without hf_cache and SelfMAD; the local `packs/code_v2/src/AD5` was refreshed for this,
  so it no longer mirrors Athena's code_v2, whose hash list remains `packs/code_v2/CODE_SHA256SUMS`), the crop pack
  fetched from Athena (`smdd_train_cropped.tar`, 3189e52a..., sha256 OK), cp39 wheel house being downloaded
  (`wcss/wheels39/`, slow network about 1 MB/s).
- 12 Nov 23:35-23:55. cp39 wheel house downloaded (56 files, offline resolution passes), packed
  `wcss/ad5w_wheels39.tar` (sha256 ac10259a...); uploaded with the code and crop packs to
  `/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/packs/` (2.5 min); `sha256sum -c` OK on WCSS. The WCSS Slurm
  controller did not answer from 23:40 to about 00:00 ("Unable to contact slurm controller"); retried every 5 min.
- 13 Nov 00:00. Submitted smokes (owner AD5; each 1 H100, limit 45 min; expected start within minutes, end about
  00:30): **6308828** = ViT-B/16, `SMOKE=1` (every 12th image, 3 epochs, batch 256 on 1 GPU); **6308829** =
  MixFaceNet-MAD, `SMOKE=1 EPOCHS=1`. Logs `/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/logs/ad5w-<name>-<job>_401.out`.
- 13 Nov 00:25 (lead). Smokes 6308828 / 6308829 pending at priority 682 (head of the queue about 10,800; 139 waiting
  jobs); both WCSS controllers down at 00:16. I stopped my 4-minute watcher; the lead's single watcher tells me when
  the controller is back; production will be submitted behind the smokes with `--dependency=afterok`.
- 13 Nov 00:30. Rented variant of the ViT-B/16 retrain prepared (`src/AD5/rented/`): `upload.sh HOST PORT LEASE`
  (same three packs + job script, hashes checked on the machine), `start.sh HOST PORT LEASE` (detached
  `remote_run.sh`: Python 3.9 from the image or a conda env, then the WCSS job script run unchanged as a plain script,
  one seed per GPU at a time, batch 256 on 1 GPU, `ARM=B`), `fetch.sh HOST PORT LEASE` (results and logs to
  `/mnt/t7/smad_next/AD5/results/rented/`, sha256 checked; writes `RELEASE` for the lead's guard when 5 of 5 verify).
  The job script now takes `AD5_L` / `AD5_PYTHON` and counts GPUs with torch (respects CUDA_VISIBLE_DEVICES).
  Not run. Cost and wall time (A100 80 GB, the measured 159 images/s per A100 at the authors' per-GPU load; 40 epochs
  x 39,723 images = 1.59 M samples): 2.8 h per seed + about 15 min set-up; 1 card: 14.5 h, 5 cards: 3.1 h, 2 cards:
  8.7 h; about 15 GPU-hours in every layout, so 15-23 USD at 1.0-1.5 USD per card-hour. Risk: the authors' loader
  reads images in the main process (num_workers 0); if it cannot feed 256-image steps at that rate the run is slower.
- 13 Nov 00:50. WCSS controller up (lead, 00:47). One check and submission (owner AD5; job script as in the repo,
  uploaded again; real workloads, chained, so nothing idles): **6308948** = MADation ViT-B/16, array 401-405%3,
  1 H100 each, 6 h limit, `afterok:6308828`; **6308949** = MixFaceNet-MAD, 401-405%2, 1 H100, 12 h, `afterok:6308829`;
  **6308950** = MADation ViT-L/14, 401-405%2, 2 H100 at batch 128 each, 200G, 12 h, `afterok:6308948` (so at most
  3 + 2 GPUs, then 2 + 4: never more than 6). Slurm forecast for the smokes: start 15 Nov 01:00 (after the stage
  ends); production starts after them. Not polled further. The realistic route for the final read is the rented
  ViT-B/16 variant (author's budget decision at 09:00).
- 13 Nov 07:46-07:52 (Athena). All five SelfMAD tasks (3545933_401-404, 3545936_405) FAILED 1-4 min after start:
  `train__.py` line 96 `os.mkdir(save_path)` -> FileNotFoundError, because its parent `-s $S/run` did not exist (the
  smoke used `-s $S/out`, which the job creates). Quota is not the cause (`hpc-fs`: group store 7.94 of 9.77 TiB).
  Logs: `logs/AD5-selfmad-3545933_<seed>.out`, `logs/AD5_keep/3548411_401` etc. Cost: about 0.2 GPU-hours.
  Fix in `athena/ad5_selfmad_train.sbatch` (now in `packs/AD5/code_v5/`, CODE_SHA256SUMS sha256 d406f4ff...):
  `mkdir -p $S/run`; plus `TEST=1` = the real code path on the first 160 renders for 5 epochs (passes the failing
  line, the epoch-5 save, the final save and the tar). Test job **3548459** submitted 08:15.
  Same cause elsewhere? No: MixFaceNet-MAD writes into `$S/out` (created) and its epochs folder is made with
  `makedirs`; MADation's logger creates its output path with `os.makedirs` (smoke B used a fresh path); the WCSS
  script likewise.
- 13 Nov 08:10. MixFaceNet-MAD seed 401 (3545870_401, running since 07:52:49 on Athena): epoch files at 07:59:41,
  08:03:41, 08:07:42, i.e. 240 s per epoch, so epoch 100 at about 14:35 and the result tar about 14:40 on 13 Nov.
- 13 Nov 08:35. Prereg amendment 5 (author's ruling 08:30): no cut-off; retrain rows arriving after 14 Nov 18:00
  are late additions read exactly as registered; SelfMAD to be resubmitted after its test job passes.
- 13 Nov 08:45-09:00. WCSS smokes 6308828 / 6308829 FAILED at 03:11 after 29 s (r18-11, H100 95,830 MiB, driver
  595.112.07): `pip install` could not find `importlib-metadata>=4.4; python_version < "3.10"` (needed by Markdown,
  a tensorboard dependency). My offline resolution check ran under the DGX's Python 3.12, so it never evaluated that
  marker. A scan of every wheel's METADATA for Python-version markers finds no other gap. Fix:
  `importlib-metadata==8.4.0` and `zipp==3.20.0` (the authors' pins) added to `env/madation_requirements.txt` and to
  the wheel house; new `ad5w_wheels39.tar` (sha256 d9329afc...) and `ad5w_code.tar` (508c41ae...) uploaded and
  hash-checked on Lustre. The arrays chained behind the smokes (6308948, 6308949, 6308950) can never start; cancelling
  them and submitting two new smokes failed at 09:00 because the controller did not answer; to be retried.
- 11 Nov 18:40. SelfMAD scoring path checked on the DGX: `score/convert_selfmad.py` (epoch tar -> the release's
  safetensors layout; 1,956 tensors, keys and shapes equal to the release) and `score/ad5_score_dgx.py` (RS1's
  score.py `--mode own`) scored 8 raw images (4 FRLL photos, 4 MorDIFF morphs) with the 8-image checkpoint.
- 11 Nov 18:50. Analysis script `src/AD5/ad5_analyse.py` written (imports `src/RS1/analyse.py` unchanged; gate,
  readings, agreement rule and verdicts as prereg.md); not run (no scores).

## 3. Data

Training set of all three methods: SMDD training split, local copy `/mnt/t7/Datasety/downloads/SMDD/SMDD_release_train/`
(from `SMDD_release_train.zip`, 4,561,053,773 bytes): `os25k_bf_t/` 25,000 genuine renders (256 x 256 PNG),
`m15k_t/` 15,000 morphs (256 x 256 PNG), `train.csv` (40,000 rows: 25,000 `bonafide`, 15,000 `attack`).
- MADation trained on `smdd_train_cropped.csv` with **39,730** rows (release training logs: "Trainset lenght: 39730"),
  i.e. 270 of the 40,000 images were lost by the crop step. The crop script is not in the MADation repository; the
  SMDD repository's `image_preprocess.py` (MTCNN, first box, 5% margin, BGR pixels passed to MTCNN, unclipped
  indices; sha256 bcaecd29...) is the same group's crop and is assumed. Whether it yields exactly 39,730 survivors is
  a check: our run of that script (A100, facenet-pytorch 2.5.2, torch 2.0.1) keeps 39,723 (section 2, 19:00).
- SelfMAD trains on the 25,000 genuine renders only, plus dlib 81-point landmarks and face-parsing label maps that
  its own preprocessing scripts produce. Landmarks: `/mnt/t7/smad_next/AD5/data/selfmad/SMDD_landmarks/os25k_bf_t/`
  (24,982 files; 18 renders without a face listed in `no_face.txt`; per-file hashes `landmarks_SHA256SUMS`, sha256 of
  that list d83319a6...), packed as `packs/selfmad_landmarks.tar` (a43776b6...). Face labels: built on Athena by the
  SelfMAD smoke job -> `packs/AD5/selfmad_labels.tar.gz` (Athena only, then copied back).
- MixFaceNet-MAD trains on the cropped SMDD training split (same crop script, SMDD README).
- Test images: those of the own-crop re-score (RS1), its manifest `/mnt/t7/smad_next/RS1/manifest.csv` and its Athena
  pack (`/mnt/t7/smad_next/RS1/athena/`); not copied here.

## 4. Code

Authors' code, pinned:
| Method | Repository | Commit used | Local copy | Licence |
|---|---|---|---|---|
| MADation (CLIP ViT-B/16 and ViT-L/14, LoRA) | github.com/gurayozgur/MADation | 0542cf8611401e640241e20deffd0b1a455f22c3 (upstream HEAD 11 Nov) | `/home/narolski/mambamorph-code/baselines/MADation` (clean) | CC BY-NC-SA 4.0 |
| SelfMAD (HRNet-W18) | github.com/LeonTodorov/SelfMAD | 09ed0819a1bc46248db8ed8ef86f523d249a9584 (code identical to 673d0640) | `/mnt/t7/smad_next/AD5/thirdparty/selfmad_09ed081/repo`; older mirror `/home/narolski/mambamorph-code/baselines/SelfMAD` | Apache-2.0 (LICENSE added 17 Jul 2026) |
| MixFaceNet-MAD | github.com/naserdamer/SMDD-Synthetic-Face-Morphing-Attack-Detection-Development-dataset | 9683229c7037f6e799e91ea913604a62ccefa47b | `/mnt/t7/smad_next/AD5/thirdparty/smdd_repo_9683229` | CC BY-NC-SA 4.0 |

Authors' training configuration as found (no change made yet):
- MADation `train.sh`: 8 GPUs (`torch.distributed.launch --nproc_per_node=8`), batch 32 per GPU, `MAD_training`,
  lr_model 1e-5, lr_header 1e-4, LoRA r 2 on q and v; ViT-B/16 alpha 4, dropout 0.4; ViT-L/14 alpha 8, dropout 0.2;
  40 epochs (default), AdamW wd 0.05, CosineAnnealingWarmRestarts with eta_min = base lr (so the LR is constant),
  grad clip 5, seed 777 hard-coded in `config.py`. Saves only `40_backbone.pth` / `40_header.pth` (save_every 40);
  evaluates the test lists only at epoch index 39 (logging; no selection in the code). Loader: `cv2.imread` (BGR),
  PIL Resize 224 (bilinear), random flip, Normalize(0.5, 0.5); labels bonafide = 1. The release logs confirm 8 GPUs,
  39,730 images, 6,207 steps, and that the released file is epoch 40 of the fourth run in the log (runs 2 and 3 also
  ran 40 epochs without evaluation; run 1 was a 2-epoch debug run; all four have identical configs). Speed in the
  log: ViT-L/14 about 860 images/s on 8 GPUs (31 min per run), ViT-B/16 about 2,340 images/s (12 min).
- SelfMAD `configs/train_config.json`: hrnet_w18 (timm ImageNet weights), batch 32 (16 genuine + 16 self-blended or
  self-morphed), 100 epochs, lr 5e-4, SAM over SGD momentum 0.9, linear LR decay from epoch 75, input 384,
  `saving_strategy: testset_best` = keep the epoch with the lowest mean EER over the FRGC, FERET and FRLL morph test
  sets (forbidden here); alternative `original` = FF++ validation AUC (needs FaceForensics++). Seed 5 hard-coded.
- MixFaceNet-MAD `main.py`: MixFaceNet-S from scratch, Adam lr 1e-4, wd 1e-6, batch 16, up to 100 epochs, class-weighted
  cross-entropy, early stopping with patience 20 on the EER of `--test_csv_path` (selection on test data; forbidden
  here). `torch.cuda.manual_seed(0)`.
Our scripts (`/home/narolski/smad-next/src/AD5/`), in run order:
- `env/madation_requirements.txt`, `env/selfmad_requirements.txt`: pinned environments (deviations in the header).
- `checks/clip_init_equivalence.py MODEL_PY HF_BIN FE_BACKBONE OUT_JSON`: CLIP initialisation equality check.
- `checks/run_with_site.py DIRS SCRIPT args`: runs a third-party script under `python3 -I` with extra sys.path entries.
- `checks/dgx_madation8.sh B|L`: the 8-image MADation check on the DGX (retries on out of memory).
- `make_train_csv.py`: training list of the cropped SMDD split in train.csv order (prefix placeholder `CROP_ROOT`).
- `selfmad_landmarks.sh`: SelfMAD landmarks on the DGX (authors' dlib_lm.py, 4 shards).
- `build_packs.sh`: assembles `/mnt/t7/smad_next/AD5/packs/` (code/, wheels_madation.tar, wheels_selfmad.tar,
  smdd_train_raw.tar, each tar with .sha256).
- `athena/ad5_common.sh`: shared job functions (hash-checked untar, offline env build, GPU memory monitor).
- `athena/ad5_smokeA_env_crop.sbatch` (1 GPU, 30 min): env build + SMDD crop -> `packs/AD5/smdd_train_cropped.tar`.
- `athena/ad5_smokeB_train.sbatch` (2 GPUs, 15 min): DDP smoke of MADation L and B, MixFaceNet-MAD 1 epoch.
- `athena/ad5_madation_train.sbatch` (8 GPUs, array 401-405, `ARM=L|B|F`): production.
- `athena/ad5_mixfacenet_train.sbatch` (1 GPU, array 401-405): production.
- `athena/ad5_selfmad_smoke.sbatch` (1 GPU, 55 min): SelfMAD env, face labels -> `selfmad_labels.tar.gz`, 1-epoch smoke.
- `athena/ad5_selfmad_train.sbatch` (1 GPU, array 401-405): production.
- `score/ad5_score_athena.py`: scores one retrain through RS1's release path (wrapper around RS1's score.py).
- `athena/ad5_score_rel.sbatch` (1 GPU): RS1 crops (made once, kept as `results/AD5/rs1_crops.tar`), conversion of
  MADation retrains, scoring of retrains and releases -> `results/AD5/scores_<TAG>.tar`.
- `env/score_requirements.txt`: the RS1 Athena environment as wheels (torch 2.2.1, timm 1.0.27, ...).
- `score/convert_selfmad.py EPOCH_TAR OUT.safetensors RELEASE`: SelfMAD retrain -> release storage format.
- `score/ad5_score_dgx.py --name N --weights F -- <score.py args>`: DGX scoring through RS1's score.py (SelfMAD own).
- `checks/dgx_selfmad8.sh`, `checks/dgx_wrapper_check.sh`: the 8-image SelfMAD check and the wrapper equality check.
- `ad5_analyse.py --scores DIR`: amendment-1 gate labels, readings, verdicts (all seeds; reproduced subset; matches-
  release subset), k-of-5 sentences, levels (EER, 0.5-rule flag and miss rates) -> `ad5_*.csv`, `ad5_results.json`.
- `ad5_loss.py --arm L|B --release-log ... --retrain NAME=training.log ... --out CSV`: loss fidelity check.
- `score/run_selfmad_dgx.sh [NAMES]`: SelfMAD release and retrains scored on the DGX (RS1 score.py own mode).
Patches: `madation_ad5.patch`, `mixfacenet_ad5.patch` (the SMDD main.py has CRLF line ends; the patch keeps them),
`selfmad_ad5.patch`. Model files: OpenAI-format CLIP from HF `timm/vit_base_patch16_clip_224.openai` (sha256
53b40183...) and `timm/vit_large_patch14_clip_224.openai` (eb70c15b...); HRNet-W18 ImageNet weights HF
`timm/hrnet_w18.ms_aug_in1k` rev 7e2c5583 (f9e3c451...); face parser HF `jonathandinu/face-parsing` rev 758b82e1
(model.safetensors c2bec795...); dlib 81-point predictor `/mnt/t7/thirdparty/dlib81_wcss_20261107/`; MTCNN weights
inside facenet-pytorch 2.5.2 (identical files to 2.6.0; plain tensor state dicts, checked with weights_only=True).

## 5. Results

none yet.

## 6. Checks

Done: commits pinned against upstream (`git ls-remote`, 11 Nov 17:25); training-log hashes equal those recorded by the
A36 conversion. For ViT-B/16 the A36 conversion found the HF `timm/vit_base_patch16_clip_224.openai` file's visual
tensors equal to the authors' frozen-encoder checkpoint (max abs difference 0).
Not verified: which crop produced `smdd_train_cropped.csv`; the epoch and run selection of the MADation release beyond
what the log shows; how the SelfMAD and MixFaceNet-MAD releases were selected.

## 7. Dead ends and failures

- `pip download --only-binary` fails for easydict 1.10, openai-clip 1.0.1 and efficientnet-pytorch 0.7.1 (sdist
  only): downloaded as sdists and built inside the job with `--no-build-isolation`.
- `pip download --platform` skips dependencies with environment markers (torch 2.3.1's CUDA 12 packages and triton
  were missing, 921 MB instead of 2.8 GB): all of them are now pinned explicitly in `selfmad_requirements.txt`.
  Unpinned indirect dependencies first resolved to 2026 versions (pillow 12.3, pydantic 2.14); now pinned to mid-2024.
- openai-clip 1.0.1 imports `from pkg_resources import packaging`; setuptools >= 70 removed it (DGX check failed with
  ImportError). Pinned setuptools 69.5.1 (checked: its pkg_resources binds `packaging`).
- MADation saver writes only when `epoch > 1 and (epoch+1) % save_every == 0`: a 2-epoch check saves nothing. Smoke
  runs use 3 epochs.
- The SMDD main.py has CRLF line ends; a first patch rewrote every line (LF). Regenerated with CRLF kept (46 lines).
- DGX GPU out of memory at `torch.cuda.set_device` (other jobs fill the unified memory): retried in a loop.

## 8. Observations and ideas

- The MADation ViT-L/14 release log (epoch 39) prints FRLL AMSL EER 12.08, StyleGAN 27.98, WebMorph 2.61 on the
  authors' own frames, while the paper's Table 3 prints 7.26 / 24.96 / 4.07; FaceMorpher (0.74) and OpenCV (0.99)
  agree, MorDIFF 19.26 agrees with Table 1. Possibly different FRLL frames or a later evaluation; not followed up.

## 9. Open items and next steps

Cost table (12 Nov 03:00; A100 40 GB measured; same effective batch and schedule as the authors):
| Arm | GPU-h per seed | x5 | One 40 GB card? | One 80 GB card? |
|---|---|---|---|---|
| MADation ViT-L/14 | 12.5 | 64 | no (global batch 256 needs about 130 GB; 4 x 40 GB at 64 per card fits) | no (2 x 80 GB at 128 per card) |
| MADation ViT-B/16 | 3.2 | 17 | no (about 47 GB at 256; 2 x 40 GB at 128 fits) | yes, 1 process at batch 256 |
| MixFaceNet-MAD | 6.5 | 34 | yes (5.5 GB) | yes |
| SelfMAD | 30 | 150 | yes (15 GB) | yes |
| MADation FE ViT-L/14 (optional) | about 4 | 20 | as ViT-L/14 (no gradients through the encoder, less) | as ViT-L/14 |
Per-card batches other than 32 change only how the 256 images of a step are split across processes (no batch norm in
CLIP); a single-card run without accumulation is the authors' setup only where the whole step fits.

1. Smoke A / B / SelfMAD smoke results -> timing to the lead (3 lines), GPU-hour estimates in this README.
2. Production arrays: MADation L and B (8 GPUs per seed), MixFaceNet-MAD X, SelfMAD S; then F if budget allows.
3. Scoring: `ad5_score_rel.sbatch` per finished arm (Athena; needs RS1's pack in packs/RS1), SelfMAD on the DGX.
4. `ad5_analyse.py`, result.md, report.

## 10. Handover state

12 Nov 03:05 handover: the owner agent hands back while all production tasks are queued (Athena forecasts
20-22 Dec for new starts). DGX process left running: the hourly poller `src/AD5/athena/poll_jobs.sh` (PID in
`/mnt/t7/smad_next/AD5/state/poller.pid`, log `state/jobs.log`; kill it or leave it). When tasks finish: run
`src/AD5/fetch_results.sh 'scores_*'` only for score tars (weights stay on Athena), score MADation / MixFaceNet-MAD
with `athena/ad5_score_rel.sbatch` (RS1 production tars rs1a_prod_v1_3545918.tar / rs1a_prod_v2_3545919.tar, ITEMS =
finished result names), SelfMAD with `score/run_selfmad_dgx.sh` (needs the five `selfmad_S_s<seed>.tar` copied back;
or adapt to Athena), oracle with `athena/ad5_selfmad_oracle.sbatch` (place it in a code_v5 tree), then
`ad5_analyse.py --scores <dir>` and `ad5_loss.py`, and write result.md. Rule from amendment 3: unfinished seeds by
14 Nov 18:00 are "incomplete".
DGX: no other AD5 process running. Athena jobs (logs in
`/net/pr2/projects/plgrid/plggrestoration/smad-next/logs/AD5-<name>-<jobid>.out`):
| Job | What | GPUs x limit | State | If it fails |
|---|---|---|---|---|
| 3544190 | smoke A, first try | 1 x 30 min | FAILED 3:53 (localfs full), 0.065 GPU-h | fixed (memfs), resubmitted |
| 3544192 | smoke B, first try | 2 x 15 min | cancelled before start, 0 GPU-h | resubmitted |
| 3544216 | smoke A: env (exists) + SMDD crop -> packs/AD5/smdd_train_cropped.tar | 1 x 30 min | COMPLETED 12:13, 0.20 GPU-h | done |
| 3544217 | smoke B: MADation L/B DDP 2 GPUs, MixFaceNet-MAD 1 epoch | 2 x 15 min | COMPLETED about 6 min, 0.2 GPU-h | done |
| 3545813_[401-405] | MADation ViT-L/14 retrains -> results/AD5/madation_L_s<seed>.tar | 8 x 2:45 each | submitted 19:08 | resubmit the failed task ids with `--array=<ids> --export=ALL,ARM=L`; finished seeds are skipped |
| 3545814_[401-405] | MADation ViT-B/16 retrains -> results/AD5/madation_B_s<seed>.tar | 8 x 1:00 each | submitted 19:08 | as above with ARM=B |
| 3545815_[401-405] | MixFaceNet-MAD retrains, first submission | 1 x 9:00 | CANCELLED 19:24 (review finding 2); 401 ran 11:38 = 0.19 GPU-h | replaced by 3545870 |
| 3545870_[401-405] | MixFaceNet-MAD retrains v2 (code_v2, per-epoch weights) -> results/AD5/mixfacenet_X_s<seed>.tar + _epochs/ | 1 x 12:00 each | submitted 19:33 | resubmit failed ids from code_v2; log kept in logs/AD5_keep |
| 3544218 | SelfMAD: env, face labels -> packs/AD5/selfmad_labels.tar.gz, 1-epoch smoke | 1 x 55 min | FAILED 35:28 (missing package after the labels), 0.59 GPU-h | fixed, resubmitted as 3545882 |
| 3545882 | SelfMAD smoke v3 (env rebuild, labels reused, 1-epoch smoke) | 1 x 55 min | COMPLETED 34:03, 0.57 GPU-h | done |
| 3545933_[401-404] | SelfMAD retrains (code_v3; account plgmultivision; t0010 excluded) -> results/AD5/selfmad_S_s<seed>.tar + _epochs/ | 1 x 46:00 each | submitted 20:14 | resubmit failed ids from code_v3 with -A plgmultivision-gpu-a100 --exclude=t0010 |
| 3545936 (task 405) | SelfMAD retrain seed 405 (same) | 1 x 46:00 | submitted 20:19 | as above |
| 3545948 | scoring smoke (code_v4, releases only, RS1 smoke crops, 8 per set) | 1 x 1:00 | FAILED 0:47 (no setuptools in the wheel house), 0.01 GPU-h | fixed, resubmitted |
| 3545960 | scoring smoke, second try | 1 x 1:00 | CANCELLED 34:40 (first call 750 s), 0.58 GPU-h | fixed (env in RAM disk) |
| 3546004 | scoring smoke, third try | 1 x 1:00 | COMPLETED 2:15, 0.04 GPU-h | done |
Compute spent so far: 2.4 GPU-hours (3544190 0.065, 3544216 0.20, 3544217 0.2, 3544218 0.59, 3545815_401 0.19,
3545882 0.57, 3545948 0.01, 3545960 0.58; plus running jobs). Allowance: 300 A100-hours for AD5 (lead, 20:17); planned about 272. Planned
production: about 111 GPU-hours (L 62, B 16, X 33), then SelfMAD.
Logs on Athena: `/net/pr2/projects/plgrid/plggrestoration/smad-next/logs/AD5-madation-ad5-madL-<job>_<seed>.out`,
`AD5-madation-ad5-madB-...`, `AD5-mixfacenet-<job>_<seed>.out`.
DGX: `src/AD5/score/run_selfmad_dgx.sh selfmad_hrnet_w18` is scoring the SelfMAD release through the AD5 path
(log `/mnt/t7/smad_next/AD5/scores_selfmad_release.log`, output `/mnt/t7/smad_next/AD5/scores_selfmad/`); rerun is
safe (finished networks are skipped).

## 11. Reproduce from scratch

Not yet.
