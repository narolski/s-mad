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
- `ad5_analyse.py --scores DIR`: reproduction gate, readings, verdicts -> `ad5_{gate,readings,verdicts}.csv`.
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
| 3545815_[401-405] | MixFaceNet-MAD retrains -> results/AD5/mixfacenet_X_s<seed>.tar | 1 x 9:00 each | submitted 19:08 | resubmit failed ids |
| 3544218 | SelfMAD: env, face labels -> packs/AD5/selfmad_labels.tar.gz, 1-epoch smoke | 1 x 55 min | pending | resubmit; it skips the labels if the tar exists |
Compute spent so far: 0.47 GPU-hours (3544190 0.065, 3544216 0.20, 3544217 0.2; plus running jobs). Planned
production: about 111 GPU-hours (L 62, B 16, X 33), then SelfMAD.
Logs on Athena: `/net/pr2/projects/plgrid/plggrestoration/smad-next/logs/AD5-madation-ad5-madL-<job>_<seed>.out`,
`AD5-madation-ad5-madB-...`, `AD5-mixfacenet-<job>_<seed>.out`.
DGX: `src/AD5/score/run_selfmad_dgx.sh selfmad_hrnet_w18` is scoring the SelfMAD release through the AD5 path
(log `/mnt/t7/smad_next/AD5/scores_selfmad_release.log`, output `/mnt/t7/smad_next/AD5/scores_selfmad/`); rerun is
safe (finished networks are skipped).

## 11. Reproduce from scratch

Not yet.
