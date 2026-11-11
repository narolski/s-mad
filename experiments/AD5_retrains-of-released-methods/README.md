# Retrains of released methods with the authors' code (AD5): full record

Owner: AD5 hypothesis owner (agent). Code `/home/narolski/smad-next/src/AD5/`. Large outputs `/mnt/t7/smad_next/AD5/`.
Registration: `prereg.md` (this folder). Verdict file: `result.md` (this folder, when results exist).

## 1. Question and current answer

Every audit statement about a published morphing attack detector (MAD) currently rests on one released checkpoint per
method. Question: if each method is retrained with its authors' own code and training set (SMDD, the synthetic
morphing development set), seeds 401 to 405, last checkpoint, do the retrains behave like the released checkpoint on
the readings the own-crop re-score of the audit rows (RS1) takes (history-matched genuine photos, flag rates under
benign processing, the smiling half of the FRLL genuine class, the MorDIFF control images)?

Status 11 Nov 2026, 17:40 CET: inventory done (section 3/4), pre-registration being written. Athena (Cyfronet A100
cluster) does not accept jobs yet (no Slurm association for the grant accounts; lead's message 17:30); nothing has
been submitted. No retrain exists. No score of this experiment exists.

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

## 3. Data

Training set of all three methods: SMDD training split, local copy `/mnt/t7/Datasety/downloads/SMDD/SMDD_release_train/`
(from `SMDD_release_train.zip`, 4,561,053,773 bytes): `os25k_bf_t/` 25,000 genuine renders (256 x 256 PNG),
`m15k_t/` 15,000 morphs (256 x 256 PNG), `train.csv` (40,000 rows: 25,000 `bonafide`, 15,000 `attack`).
- MADation trained on `smdd_train_cropped.csv` with **39,730** rows (release training logs: "Trainset lenght: 39730"),
  i.e. 270 of the 40,000 images were lost by the crop step. The crop script is not in the MADation repository; the
  SMDD repository's `image_preprocess.py` (MTCNN, first box, 5% margin, BGR pixels passed to MTCNN, unclipped
  indices; sha256 bcaecd29...) is the same group's crop and is assumed. Whether it yields exactly 39,730 survivors is
  a check to run (section 6).
- SelfMAD trains on the 25,000 genuine renders only, plus dlib 81-point landmarks and face-parsing label maps that
  its own preprocessing scripts produce (not yet built).
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
Our scripts: none yet.

## 5. Results

none yet.

## 6. Checks

Done: commits pinned against upstream (`git ls-remote`, 11 Nov 17:25); training-log hashes equal those recorded by the
A36 conversion. For ViT-B/16 the A36 conversion found the HF `timm/vit_base_patch16_clip_224.openai` file's visual
tensors equal to the authors' frozen-encoder checkpoint (max abs difference 0).
Not verified: which crop produced `smdd_train_cropped.csv`; the epoch and run selection of the MADation release beyond
what the log shows; how the SelfMAD and MixFaceNet-MAD releases were selected.

## 7. Dead ends and failures

none yet.

## 8. Observations and ideas

- The MADation ViT-L/14 release log (epoch 39) prints FRLL AMSL EER 12.08, StyleGAN 27.98, WebMorph 2.61 on the
  authors' own frames, while the paper's Table 3 prints 7.26 / 24.96 / 4.07; FaceMorpher (0.74) and OpenCV (0.99)
  agree, MorDIFF 19.26 agrees with Table 1. Possibly different FRLL frames or a later evaluation; not followed up.

## 9. Open items and next steps

1. Pre-registration (`prereg.md`). 2. Patch list, packs and environment scripts; 8-image check on the DGX.
3. Uploads to Athena (allowed; submission waits for the lead). 4. Smoke jobs, then production arrays.

## 10. Handover state

No process running, no job submitted. Compute spent: 0 GPU-hours.

## 11. Reproduce from scratch

Not yet.
