# Retrains of released methods with the authors' code (AD5): full record

Owner: AD5 hypothesis owner (agent). Code `/home/narolski/smad-next/src/AD5/`. Large outputs `/mnt/t7/smad_next/AD5/`.
Registration: `prereg.md` (this folder). Verdict file: `result.md` (this folder, when results exist).

## 1. Question and current answer

Every audit statement about a published morphing attack detector (MAD) currently rests on one released checkpoint per
method. Question: if each method is retrained with its authors' own code and training set (SMDD, the synthetic
morphing development set), seeds 401 to 405, last checkpoint, do the retrains behave like the released checkpoint on
the readings the own-crop re-score of the audit rows (RS1) takes (history-matched genuine photos, flag rates under
benign processing, the smiling half of the FRLL genuine class, the MorDIFF control images)?

Status 11 Nov 2026, 18:55 CET: `prereg.md` written (18:10). All 8-image checks passed on the DGX (SMDD crop,
MADation ViT-B/16 and ViT-L/14 training, MixFaceNet-MAD training, SelfMAD landmarks, face labels and training,
conversion and scoring wrappers). Packs uploaded to Athena. Smoke jobs running on Athena (A100): smoke A 3544216
(environment + SMDD crop), then smoke B 3544217 (MADation L/B + MixFaceNet-MAD speed), SelfMAD smoke 3544218.
No retrain and no score exist yet.

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

1. Smoke A / B / SelfMAD smoke results -> timing to the lead (3 lines), GPU-hour estimates in this README.
2. Production arrays: MADation L and B (8 GPUs per seed), MixFaceNet-MAD X, SelfMAD S; then F if budget allows.
3. Scoring: `ad5_score_rel.sbatch` per finished arm (Athena; needs RS1's pack in packs/RS1), SelfMAD on the DGX.
4. `ad5_analyse.py`, result.md, report.

## 10. Handover state

DGX: no AD5 process running. Athena jobs (logs in
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
| 3545960 | scoring smoke, second try | 1 x 1:00 | submitted 20:50 | read log |
Compute spent so far: 1.82 GPU-hours (3544190 0.065, 3544216 0.20, 3544217 0.2, 3544218 0.59, 3545815_401 0.19,
3545882 0.57; plus running jobs). Allowance: 300 A100-hours for AD5 (lead, 20:17); planned about 272. Planned
production: about 111 GPU-hours (L 62, B 16, X 33), then SelfMAD.
Logs on Athena: `/net/pr2/projects/plgrid/plggrestoration/smad-next/logs/AD5-madation-ad5-madL-<job>_<seed>.out`,
`AD5-madation-ad5-madB-...`, `AD5-mixfacenet-<job>_<seed>.out`.
DGX: `src/AD5/score/run_selfmad_dgx.sh selfmad_hrnet_w18` is scoring the SelfMAD release through the AD5 path
(log `/mnt/t7/smad_next/AD5/scores_selfmad_release.log`, output `/mnt/t7/smad_next/AD5/scores_selfmad/`); rerun is
safe (finished networks are skipped).

## 11. Reproduce from scratch

Not yet.
